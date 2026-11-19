"""Listagem de material of a house from its MODULE SHEETS (PDF, as the company made them) — for houses the builder
(casa_planta.py, one storey from a plan) cannot rebuild: two timber storeys, real modules drawn in AutoCAD.

    python ferramentas/documentos/listagem_modulos.py "<project>/modelos/listagem/config.json" [--saida DIR]

What comes from where:
- the wall modules, piece by piece (cut list, sections, lengths), their openings and wall areas: the module sheets,
  read by ferramentas/documentos/modulos_pdf.py — exactly as drawn;
- everything the sheets do not draw (top of the walls, the floor between storeys, ceilings, the roof, the layers on
  the walls, floors): the DiscoverCasa method (conhecimento/metodo/) with the products, purchase units and waste of
  ferramentas/modelo/sistema_construtivo.json, on the plan measures in the config (read from the same sheets' plans);
  every rule used is written next to its line in `regras` of the output JSON, and every assumption in `avisos`;
- the document: gerar.doc_listagem (the same PDF + CSV as every house, with the product codes of codigos.py).
Config: "documentos" {obra, projeto}; "folhas" [{pdf, tipo exterior|interior, piso 0|1}]; "pisos" {"0"|"1": {pe_direito,
contorno [[x, y]...] (outer faces of the modules, m), recortes ...}}; "pavimento_entre_pisos", "coberturas",
"caixilharia", "faixa_piso" — see Construção Ribamar/modelos/listagem/config.json (written 2026-11-19).
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.comum import pasta_trabalho  # noqa: E402
from ferramentas.documentos import gerar  # noqa: E402
from ferramentas.documentos.modulos_pdf import ler_folha  # noqa: E402
from ferramentas.modelo.camadas import fundir  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
MODELO = Path(__file__).resolve().parents[1] / "modelo"
SECOES = {"110x35": (0.11, 0.035), "75x35": (0.075, 0.035), "110x75": (0.11, 0.075), "220x75": (0.22, 0.075),
          "200x100": (0.2, 0.1)}


def area_poligono(pts):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2


def perimetro(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:] + pts[:1]))


class CasaModulos:
    """What gerar.doc_listagem needs from a house (pecas_madeira, ferragens, camadas_totais, lista_corte, S, G)."""

    def __init__(self, cfg_path):
        self.cfg_path = Path(cfg_path).resolve()
        self.cfg = json.load(open(self.cfg_path, encoding="utf-8"))
        self.base = self.cfg_path.parent
        doc = self.cfg.get("documentos", {})
        self.obra = doc.get("obra") or self.cfg.get("nome", "Obra")
        self.S = fundir(json.load(open(MODELO / "sistema_construtivo.json", encoding="utf-8")), self.cfg.get("camadas") or {})
        self.avisos, self.regras = [], []
        self.pecas = []      # (group, section, length, volume, kind)
        self.extras = []     # (group, section, length, count) for the cut list
        self.camadas = {}    # (collection id, layer) -> totals
        self.folhas = []
        for f in self.cfg["folhas"]:
            r = ler_folha(str((self.base / f["pdf"]).resolve()), f["tipo"])
            r["piso"] = f["piso"]
            self.folhas.append(r)
            self.avisos += [f"{r['folha']}: {w}" for w in r["avisos"]]
        self.itens = []
        self.G = {"cobertura": {}, "niveis": {}, "areas_obra": []}
        self._modulos()
        self._estrutura()
        self._paredes()
        self._pisos_tetos()
        self._coberturas()
        self._caixilharia()
        self._dados()
        self.S = dict(self.S, caixilharia=dict(self.S.get("caixilharia") or {}, itens=self.itens))

    # ------------------------------------------------------------------ helpers
    def piso_nome(self, p):
        return (self.cfg.get("nomes_pisos") or {}).get(str(p), f"piso {p}")

    def madeira(self, grupo, sec, comp, n=1, tipo=""):
        a, b = SECOES[sec]
        for _ in range(int(n)):
            self.pecas.append((grupo, sec, comp, comp * a * b, tipo))
        self.extras.append((sec, comp, int(n)))

    def camada(self, col, nome, area=0.0, comp=0.0, n=0, vol=0.0, produto="", unidade="", au=0.0, cu=0.0, desp=0.0, colecao=""):
        t = self.camadas.setdefault((col, nome), {"colecao": colecao or col, "camada": nome, "n": 0, "comp": 0.0, "area": 0.0,
                                                  "vol": 0.0, "un": unidade, "au": au, "cu": cu, "desp": desp, "produto": produto})
        t["n"] += n
        t["comp"] += comp
        t["area"] += area
        t["vol"] += vol

    def camada_padrao(self, col, c, area=0.0, comp=0.0, n=0, nome=None, vol=0.0):
        """A layer with the standard's product and purchase unit (plates: one plate's area; rolls: area_unidade_m2)."""
        au = c.get("area_unidade_m2") or (c["placa"][0] * c["placa"][1] if c.get("placa") else 0.0)
        un = c.get("unidade") or (f"placa {round(c['placa'][0] * 1000)}x{round(c['placa'][1] * 1000)}" if c.get("placa") else "")
        self.camada(col, nome or c["nome"], area=area, comp=comp, n=n, vol=vol, produto=c.get("produto", ""), unidade=un,
                    au=au, cu=c.get("comprimento_unidade_m", 0.0), desp=c.get("desperdicio", 0.0))

    # ------------------------------------------------------------------ 1. the modules, piece by piece
    def _modulos(self):
        for f in self.folhas:
            g = f"Paredes {'exteriores' if f['tipo'] == 'exterior' else 'interiores'} {self.piso_nome(f['piso'])} (módulos)"
            for m in f["modulos"]:
                for mb in m["membros"]:
                    a, b = SECOES[mb["seccao"]]
                    self.pecas.append((g, mb["seccao"], mb["comprimento"], mb["comprimento"] * a * b, mb["tipo"]))
        self.regras.append("Módulos: todas as peças das folhas de módulos, como desenhadas (modulos_pdf.py); preto 11x3,5 "
                           "(exterior) / 7,5x3,5 (interior), vermelho 11x7,5, laranja 22x7,5.")

    def mods(self, piso=None, tipo=None):
        return [m for f in self.folhas for m in f["modulos"]
                if (piso is None or f["piso"] == piso) and (tipo is None or f["tipo"] == tipo)]

    def comp_paredes(self, piso, tipo):
        return sum(m["comprimento"] for m in self.mods(piso, tipo))

    # ------------------------------------------------------------------ 1. structure the sheets do not draw
    def _estrutura(self):
        E = self.S["estrutura"]
        cfg = self.cfg
        pv = cfg.get("pavimento_entre_pisos")
        # amarração rings (method §4)
        for an in cfg.get("amarracoes", []):
            for L in an["trocos"]:
                self.madeira(an["grupo"], "110x75", L, tipo="Amarração")
            self.regras.append(f"{an['grupo']}: {sum(an['trocos']):.2f} m — {an['regra']}")
        if pv:  # floor between storeys (method §5): joists 220x75 at <= 0,615 wall to wall, barrotes 110x75 flat at 0,60
            vg, br = E["pavimento"]["vigas"], E["pavimento"]["barrotes"]
            vao, larg = pv["vao"], pv["largura"]
            n = math.ceil(larg / vg["espacamento"]) + 1
            self.madeira("Pavimento entre pisos - vigas", vg["seccao"], vao, n, "Viga do pavimento")
            nb = math.ceil(vao / br["espacamento"]) + 1
            self.madeira("Pavimento entre pisos - barrotes", br["seccao"], larg, nb, "Barrote")
            self.regras.append(f"Pavimento entre pisos: {n} vigas 22x7,5 de {vao:.2f} m a {larg / (n - 1):.3f} (≤ 0,615) + "
                               f"{nb} barrotes 11x7,5 deitados de {larg:.2f} m a ≤ 0,60 (método §5).")
        for cb in cfg.get("coberturas", []):  # hidden roofs (method §4, §7): ceiling beams 220x75 at <= 1 m, madres on prumos
            vt, md = E["vigas_teto"], E["madres"]
            n = math.ceil(cb["comprimento_vigas_ao_longo"] / vt["espacamento"]) + 1
            self.madeira(f"{cb['nome']} - vigas de apoio ao teto", vt["seccao"], cb["vao_vigas"], n, "Viga de apoio ao teto")
            pend = cb["pendente_pct"] / 100
            linhas, prumos = 0, []
            for agua in cb["aguas"]:  # each slope: lines from the gutter to the top at <= 1,265
                L = agua["comprimento"]
                k = math.ceil(L / md["espacamento_max"])
                xs = [L * i / k for i in range(k + 1)]
                linhas += len(xs)
                for x in xs[1:]:  # the gutter line sits on the beams (no prumo)
                    prumos += [x * pend] * n
            self.madeira(f"{cb['nome']} - madres", md["seccao"], cb["comprimento_madres"], linhas, "Madre")
            if prumos:
                hm = sum(prumos) / len(prumos)
                self.madeira(f"{cb['nome']} - prumos", "110x75", round(hm, 3), len(prumos), "Prumo")
            self.regras.append(f"{cb['nome']}: {n} vigas de apoio ao teto 22x7,5 de {cb['vao_vigas']:.2f} m a ≤ 1,0; {linhas} "
                               f"linhas de madres 11x7,5 de {cb['comprimento_madres']:.2f} m (≤ 1,265 entre si; a da caleira "
                               f"sobre as vigas); {len(prumos)} prumos 11x7,5 (média {hm if prumos else 0:.2f} m) para "
                               f"{cb['pendente_pct']} % (método §7).")

    # ------------------------------------------------------------------ 2./3. wall layers
    def _paredes(self):
        ex, it = self.S["exterior"], self.S["interior"]
        op = ex["opcoes"][self.cfg.get("acabamento_exterior", "A")]
        letra = self.cfg.get("acabamento_exterior", "A")
        fx = self.cfg.get("faixa_piso", {})
        area_ext = 0.0
        vaos_perim = 0.0
        duas = self.cfg.get("faces_exteriores", {})  # modules with the outside on both faces (loggia returns, porch)
        for m in self.mods(tipo="exterior"):
            area_ext += (m["area_bruta"] - m["area_vaos"]) * (1 + duas.get(m["nome"], 0.0))
            for o in m["aberturas"]:
                vaos_perim += 2 * o["altura"] + o["largura"] * (1 if o["tipo"] == "porta" else 2)
        if fx:
            area_ext += fx["comprimento"] * fx["altura"]
            self.regras.append(f"Fachada: + faixa do pavimento entre pisos {fx['comprimento']:.2f} x {fx['altura']:.2f} m "
                               f"(o revestimento cobre a zona das vigas entre o topo dos módulos do piso 0 e a base dos do piso 1).")
        self.camada_padrao("2.1", ex["osb"], area=area_ext)
        self.camada_padrao("2.2", ex["membrana"], area=area_ext)
        for c in op["camadas"]:
            nome = f"{c['nome']} ({letra})"
            if c.get("tipo") == "ripas":
                comp = area_ext / c["espacamento"] + (vaos_perim if c["id"] == "ripado" else 0.0)
                self.camada("2.3", nome, comp=comp, produto=c.get("produto", ""))
            elif c.get("tipo") == "tabuas":
                comp = area_ext / (c["largura"] + c.get("junta", 0.0))
                self.camada("2.3", nome, area=area_ext, comp=comp, n=math.ceil(comp / c.get("comprimento_max", 4.0)),
                            produto=c.get("produto", ""), unidade=c.get("unidade", ""), cu=c.get("comprimento_unidade_m", 0.0),
                            desp=c.get("desperdicio", 0.0))
            else:
                self.camada_padrao("2.3", c, area=area_ext, nome=nome)
        self.regras.append(f"Fachada ({op['nome']}): área líquida dos módulos exteriores (altura de cada módulo, sem vãos) = "
                           f"{area_ext:.1f} m²; ripas a 0,35 + contorno dos vãos ({vaos_perim:.1f} m); tábuas pela largura + junta.")
        # inside: exterior walls lined up to the ceiling (pé direito), interior walls both faces; wool between the studs
        la, osb, pl = it["la_mineral"], it["osb"], it["acabamento"]
        a_ext_in, a_int, vol_la, a_la = 0.0, 0.0, 0.0, 0.0
        for piso, dados in self.cfg["pisos"].items():
            pd = dados["pe_direito"]
            for m in self.mods(int(piso), "exterior"):
                h = min(m["altura"], pd)
                vaos = sum(o["largura"] * min(o["altura"], h - o.get("peitoril", 0)) for o in m["aberturas"])
                a = m["comprimento"] * h - vaos
                a_ext_in += a * (1 - duas.get(m["nome"], 0.0))
                a_la += a * (1 - 0.035 / 0.435)
                vol_la += a * (1 - 0.035 / 0.435) * la["espessura"]
            for m in self.mods(int(piso), "interior"):
                h = min(m["altura"], pd)
                vaos = sum(o["largura"] * min(o["altura"], h) for o in m["aberturas"])
                a = m["comprimento"] * h - vaos
                a_int += 2 * a
                a_la += a * (1 - 0.035 / 0.435)
                vol_la += a * (1 - 0.035 / 0.435) * la.get("espessura_interior", la["espessura"])
        self.camada("3.1", la["nome"], area=a_la, vol=vol_la, produto=la.get("produto", ""))
        self.camada_padrao("3.2", osb, area=a_ext_in + a_int)
        self.camada_padrao("3.3", pl, area=a_ext_in + a_int)
        self.regras.append(f"Interior: face interior das paredes exteriores até ao pé direito ({a_ext_in:.1f} m²) + as duas faces "
                           f"das interiores ({a_int:.1f} m²): OSB 15 + Pladur 13; lã entre montantes (80 exterior / 60 interior, "
                           f"menos a largura dos montantes 3,5 / 43,5).")

    # ------------------------------------------------------------------ 4./5. floors and ceilings
    def _pisos_tetos(self):
        T, P = self.S["tetos"], self.S["pavimentos"]
        pv = self.cfg.get("pavimento_entre_pisos")
        for piso, d in self.cfg["pisos"].items():
            a = d["area_interior"]
            self.camada("4.1", P["acabamento"]["nome"], area=a, produto=P["acabamento"].get("produto", ""),
                        desp=P["acabamento"].get("desperdicio", 0.0))
            # ceiling (method §6): réguas one per perfil at each beam / joist, perfis at 0,40, cantoneira round the rooms
            ac, esp = d["area_teto"], d["espacamento_apoios_teto"]
            self.camada("5.1", T["suspensao"]["nome"], comp=round(ac / (T["perfis"]["espacamento"] * esp)) * 0.235,
                        n=round(ac / (T["perfis"]["espacamento"] * esp)), produto=T["suspensao"].get("produto", ""))
            self.camada("5.2", T["perfis"]["nome"], comp=ac / T["perfis"]["espacamento"], produto=T["perfis"].get("produto", ""))
            c = T["cantoneira"]
            self.camada("5.3", c["nome"], comp=d["perimetro_tetos"], produto=c.get("produto", ""), unidade=c.get("unidade", ""),
                        cu=c.get("comprimento_unidade_m", 0.0))
            self.camada_padrao("5.4", T["acabamento"], area=ac)
        topo = sum(d.get("area_teto_cobertura", 0.0) for d in self.cfg["pisos"].values())
        if topo:
            self.camada("5.5", T["la"]["nome"], area=topo, vol=topo * T["la"]["espessura"], produto=T["la"].get("produto", ""))
        if pv:
            self.camada("5.6", T["la_pavimento"]["nome"], area=pv["area_osb"], vol=pv["area_osb"] * T["la_pavimento"]["espessura"],
                        produto=T["la_pavimento"].get("produto", ""))
            self.camada("4.2", "OSB 22 mm (pavimento entre pisos)", area=pv["area_osb"], produto="OSB3 22 mm 2500x1250 sobre os barrotes",
                        unidade="placa 1250x2500", au=1.25 * 2.5, desp=0.1)
        self.regras.append("Pavimentos e tetos: áreas interiores da planta dos módulos (config); vinílico em todo o interior; "
                           "teto falso em todo o interior (réguas 0,235 m, perfis a 0,40, cantoneira, Pladur 13); lã 100 sobre o "
                           "teto sob as coberturas e entre as vigas do pavimento entre pisos; OSB 22 sobre os barrotes.")

    # ------------------------------------------------------------------ 6. roofs
    def _coberturas(self):
        C = self.S["cobertura"]
        pn, cal, ch = C["painel_oculto"], C["caleira_oculta"], C["chapeu"]
        for cb in self.cfg.get("coberturas", []):
            k = math.sqrt(1 + (cb["pendente_pct"] / 100) ** 2)
            area, npn, comp = 0.0, 0, 0.0
            for agua in cb["aguas"]:
                n = math.ceil(agua["largura"] / pn["largura"])
                area += agua["largura"] * agua["comprimento"] * k
                npn += n
                comp += n * agua["comprimento"] * k
            self.camada("6.1", pn["nome"], area=area, comp=comp, n=npn, produto=pn.get("produto", ""))
            for g in cb.get("caleiras", []):
                self.camada("6.2", cal["nome"], comp=g, n=1, produto=cal.get("produto", ""))
            if cb.get("tubos"):
                self.camada("6.3", "Saída da caleira oculta (bocal)", n=cb["tubos"], produto="Bocal 100 x 50 no fundo da caleira oculta")
                self.camada("6.4", "Tubo de queda (no revestimento)", comp=cb["tubos"] * cb["altura_tubos"], n=cb["tubos"],
                            produto="Tubo de queda 100 x 50 dentro do revestimento exterior, escondido pelo Tremolo")
            if cb.get("cumeeira"):
                self.camada("6.5", "Cumeeira", comp=cb["cumeeira"])
            if cb.get("chapeu"):
                self.camada("6.6", ch["nome"], comp=cb["chapeu"], produto=ch.get("produto", ""))
            if cb.get("remate_topo"):
                self.camada("6.7", "Remate de topo", comp=cb["remate_topo"],
                            produto="Placa impermeável dobrada + remate em metal na cor do painel (detalhe do utilizador)")
            self.regras.append(f"{cb['nome']}: painel 5 ondas 80 mm, {npn} painéis, {area:.1f} m² ({cb['pendente_pct']} %); "
                               f"caleiras {sum(cb.get('caleiras', [])):.2f} m; {cb.get('tubos', 0)} tubos 100x50 (dois por caleira, "
                               f"um numa ≤ 4 m — método §7). {cb.get('nota', '')}")

    # ------------------------------------------------------------------ 7. windows and doors (from the modules)
    def _caixilharia(self):
        cx = self.cfg.get("caixilharia", {})
        prod_j = cx.get("produto", "Caixilharia em alumínio")
        perim = 0.0
        for f in self.folhas:
            if f["tipo"] != "exterior":
                continue
            for m in f["modulos"]:
                for o in m["aberturas"]:
                    larga = o["largura"] >= 2.0
                    tipo = "Vão envidraçado até ao chão" if o["tipo"] == "porta" and larga else (
                        "Porta" if o["tipo"] == "porta" else "Janela")
                    self.itens.append({"modulo": m["nome"], "divisao": self.piso_nome(f["piso"]), "descricao_curta": tipo + " (vão em tosco)",
                                       "descricao": prod_j, "largura": o["largura"], "altura": o["altura"], "estore": False})
                    perim += 2 * o["altura"] + o["largura"] * (1 if o["tipo"] == "porta" else 2)
        self.camada("7.1", "Remates exteriores dos vãos", comp=perim, n=len(self.itens),
                    produto="Remate de vão em alumínio quinado RAL 7016 (assumido)")
        self.camada("7.2", "Remates interiores dos vãos", comp=perim, n=len(self.itens), produto="Forro interior do vão em Pladur (assumido)")

    def _dados(self):
        for cod, desc, a in self.cfg.get("dados_obra", []):
            self.G["areas_obra"].append((cod, desc, a))

    # ------------------------------------------------------------------ the interface of dados.Casa
    def pecas_madeira(self):
        return self.pecas

    def ferragens(self):
        return []

    def camadas_totais(self):
        for t in self.camadas.values():
            q = ""
            if t["au"]:
                q = math.ceil(t["area"] * (1 + t["desp"]) / t["au"])
            elif t["cu"]:
                q = math.ceil(t["comp"] * (1 + t["desp"]) / t["cu"])
            t["compra"] = q
        return self.camadas

    def lista_corte(self, so_modulos=True):
        res = defaultdict(lambda: defaultdict(int))
        for f in self.folhas:
            for m in f["modulos"]:
                for mb in m["membros"]:
                    res[mb["seccao"]][round(mb["comprimento"] * 100)] += 1
        if not so_modulos:
            for sec, comp, n in self.extras:
                res[sec][round(comp * 100)] += n
        return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--saida")
    a = ap.parse_args()
    import datetime
    casa = CasaModulos(a.config)
    saida = Path(a.saida) if a.saida else pasta_trabalho("documentos", casa.obra.replace(" ", "_"))
    saida.mkdir(parents=True, exist_ok=True)
    doc = casa.cfg.get("documentos", {})
    hoje = datetime.date.today()
    info = {"obra": casa.obra, "projeto": doc.get("projeto", casa.cfg.get("nome", "")), "data": hoje.strftime("%d/%m/%Y")}
    pre = casa.obra.replace(" ", "_")
    n, linhas = gerar.doc_listagem(casa, info, saida / f"{pre}_Listagem_Material.pdf", saida / f"{pre}_Listagem_Material.csv")
    mad = [l for l in linhas if l[0] == "1"]
    res = {"obra": casa.obra, "folhas": [{k: f[k] for k in ("folha", "tipo", "piso", "escala_mm_m")} | {"modulos": len(f["modulos"])}
                                         for f in casa.folhas],
           "modulos": {f"{f['folha']}": [{k: m[k] for k in ("nome", "comprimento", "comprimento_cota", "altura", "aberturas")}
                                         for m in f["modulos"]] for f in casa.folhas},
           "regras": casa.regras, "avisos": casa.avisos}
    (saida / f"{pre}_Listagem_resumo.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"LISTAGEM_OK {saida}: {n} páginas; madeira {sum(l[3] for l in mad)} peças, {sum(l[4] for l in mad):.1f} m, "
          f"{sum(l[6] for l in mad):.2f} m3")
    for r in casa.regras:
        print("  regra:", r)
    for w in casa.avisos:
        print("  aviso:", w)


if __name__ == "__main__":
    main()
