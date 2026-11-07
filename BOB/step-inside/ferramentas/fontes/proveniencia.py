"""Build the provenance layer of a house (spec §13 Fase 1, hub task 54): fontes.json, valid against
step-inside/schema/fontes_projeto.schema.json.

It reads what the builder already uses and changes none of it:
  - config.json + its planta_paredes.json (walls and openings read from the architecture plan);
  - modulos_reais (DiscoverCasa's own module drawings, e.g. D2503), when the config has them: the openings as built;
  - declaracoes.json (optional, kept by hand): the source of the values that came from people or other sheets,
    e.g. "pé direito 2,50 — D2503 secções, confirmado pelo utilizador". Keys are field paths; "*" matches any part.

Each field gets estado CONFIRMED / INFERRED / MISSING / NEEDS_HUMAN_REVIEW. Without a declaration:
  - geometry read from the plan takes the state of the scale (deduced scale -> INFERRED);
  - values written in the config without a known source -> INFERRED, or NEEDS_HUMAN_REVIEW when its note says
    "a confirmar";
  - the builder's built-in defaults (not in any drawing) -> NEEDS_HUMAN_REVIEW;
  - what nobody gave (north, CRS, terrain...) -> MISSING. Nothing is invented (spec rule 9).

    python step-inside/ferramentas/fontes/proveniencia.py <config.json> [--declaracoes d.json]
        [--catalogo catalogo.json] --saida fontes.json
"""
import argparse
import copy
import fnmatch
import math
from pathlib import Path

from comum import (BOB, CONFIRMED, INFERRED, MISSING, REVIEW, VERSAO_ESQUEMA, campo, campos, em_falta,
                   escrever_json, fonte, ler_json, mais_fraco, utf8_stdout)
from esquema import validar
from matriz import FORMATOS, UNSUPPORTED

NORMA = ler_json(BOB / "ferramentas" / "modelo" / "sistema_construtivo.json")

# the builder's built-in values when the config says nothing (ferramentas/modelo/casa_planta.py)
OMISSAO_PORTA_EXTERIOR = 2.20
OMISSAO_JANELA = {"peitoril": 1.0, "topo": 1.75}
OMISSAO_PORTA_INTERIOR = (0.87, 2.03)   # DiscoverCasa rough opening: company method, not a guess
TOL = 0.02                                # m: differences below this are not conflicts
RESOLUCAO_MODULOS = "Prevalece o desenho de módulos (como construído)."


def _r(x, n=3):
    return None if x is None else round(float(x), n)


def _nota_doc(*docs):
    return " ".join(d for d in docs if d).strip()


def _estado_config(nota):
    return REVIEW if "a confirmar" in (nota or "").lower() else INFERRED


class Construtor:
    def __init__(self, config_path, declaracoes=None, catalogo=None):
        self.cp = Path(config_path)
        self.cfg = ler_json(self.cp)
        self.dir = self.cp.parent
        self.planta = ler_json(self.dir / self.cfg["planta"]) if self.cfg.get("planta") else None
        self.decl = declaracoes or {}
        self.catalogo = catalogo or {}
        self.conflitos = []
        self.cfg_nome = self.cp.name

    # ------------------------------------------------------------------ helpers
    def fonte_config(self, local):
        return fonte(f"{self.cfg_nome} (configuração do modelo)", None, local)

    def fonte_planta(self):
        o = (self.planta or {}).get("origem_desenho", {})
        r = o.get("regiao") or []
        local = f"planta, região {r[0]:g}–{r[2]:g} × {r[1]:g}–{r[3]:g} mm da folha" if len(r) == 4 else "planta"
        return fonte(o.get("dwfx", "?"), o.get("folha"), local)

    def conflito(self, campo_path, gravidade, nota, resolucao=""):
        self.conflitos.append({"campo": campo_path, "gravidade": gravidade, "nota": nota,
                               "estado": "resolvido" if resolucao else "aberto", "resolucao": resolucao})

    # ------------------------------------------------------------------ sections
    def escala(self):
        o = (self.planta or {}).get("origem_desenho")
        if not o:
            return em_falta("escala", "sem planta lida")
        return campo(f"1:{o['escala']:g}", INFERRED, "inferencia", tipo="escala", fonte=self.fonte_planta(),
                     nota="Escala dada ao leitor da planta (deduzida das cotas ou do rótulo).")

    def referencial(self):
        return {
            "unidade": "m",
            "origem": campo("canto inferior esquerdo das paredes; X para a direita da folha, Y para cima, Z a "
                            "partir do topo da laje", CONFIRMED, "calculo", tipo="referencial",
                            fonte=self.fonte_planta() if self.planta else None,
                            nota="Convenção do leitor da planta (planta_arquitetura.py)."),
            "norte": em_falta("referencial", "Direção do norte em relação ao eixo Y: não está lida dos desenhos."),
            "crs": em_falta("referencial", "Sem georreferência: o modelo está em coordenadas locais."),
            "cota_referencia": em_falta("cota", "Cota absoluta (altitude) do Z = 0 do modelo.", "m"),
        }

    def dimensoes(self, est_geo):
        out = {}
        casa = self.cfg.get("casa", {})
        cont = (self.planta or {}).get("contorno")
        bbox = None
        if cont and len(cont) == 4:
            bbox = (cont[1] - cont[0], cont[3] - cont[2])
        for i, k in enumerate(("comprimento", "profundidade")):
            if k in casa:
                c = campo(_r(casa[k]), INFERRED, "inferencia", unidade="m", tipo="dimensao",
                          fonte=self.fonte_config(f"casa.{k}"), nota="Valor da configuração.")
            elif bbox:
                c = campo(_r(bbox[i]), est_geo, "calculo", unidade="m", tipo="dimensao", fonte=self.fonte_planta(),
                          nota="Caixa envolvente das paredes lidas.")
            else:
                c = em_falta("dimensao", unidade="m")
            if bbox and k in casa and abs(casa[k] - bbox[i]) > TOL:
                c["conflitos"].append({"valor": _r(bbox[i]), "fonte": self.fonte_planta(), "estado": "aberto",
                                       "nota": "Caixa envolvente das paredes da planta."})
                self.conflito(f"dimensoes.{k}", REVIEW,
                              f"Configuração {casa[k]} m e planta {bbox[i]:.3f} m.")
            out[k] = c
        fund = self.cfg.get("fundacao", {}).get("contorno")
        if fund:
            a = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(fund, fund[1:] + fund[:1]))) / 2
            out["area_implantacao"] = campo(_r(a, 2), mais_fraco(est_geo, INFERRED), "calculo", unidade="m2",
                                            tipo="dimensao", fonte=self.fonte_config("fundacao.contorno"),
                                            nota="Área do contorno da base de fundação.")
        return out

    def niveis(self):
        nv = self.cfg.get("niveis", {})
        doc = nv.get("_doc", "")
        out = {}
        for k, v in nv.items():
            if k.startswith("_") or not isinstance(v, (int, float)):
                continue
            out[k] = campo(_r(v), _estado_config(doc), "inferencia", unidade="m", tipo="nivel",
                           fonte=self.fonte_config(f"niveis.{k}"), nota=doc)
        if "pe_direito" not in out:
            out["pe_direito"] = em_falta("nivel", "Pé direito não indicado.", "m")
        plat = self.cfg.get("platibanda", {})
        if isinstance(plat.get("topo"), (int, float)):
            out["topo_platibanda"] = campo(_r(plat["topo"]), _estado_config(plat.get("_doc")), "inferencia",
                                           unidade="m", tipo="nivel", fonte=self.fonte_config("platibanda.topo"),
                                           nota=plat.get("_doc", ""))
        return out

    def _alturas(self, tipo, exterior):
        """(peitoril, altura) campos for an opening from the config defaults."""
        A = self.cfg.get("aberturas", {})
        doc = A.get("_doc", "")
        if tipo == "porta" and not exterior:
            pi = self.cfg.get("estrutura", {}).get("porta_interior") or \
                NORMA.get("estrutura", {}).get("porta_interior") or {}
            w, h = pi.get("largura", OMISSAO_PORTA_INTERIOR[0]), pi.get("altura", OMISSAO_PORTA_INTERIOR[1])
            f = fonte("norma da empresa (sistema_construtivo.json, estrutura.porta_interior)")
            return (campo(0.0, CONFIRMED, "norma_empresa", unidade="m", tipo="cota", fonte=f),
                    campo(_r(h), CONFIRMED, "norma_empresa", unidade="m", tipo="cota", fonte=f,
                          nota=f"Vão DiscoverCasa {w:g} × {h:g} centrado na porta do arquiteto."))
        if tipo == "porta":
            pe = campo(0.0, CONFIRMED, "calculo", unidade="m", tipo="cota", nota="Porta: vão desde o pavimento.")
            if "porta_exterior" in A and "altura" in A["porta_exterior"]:
                return pe, campo(_r(A["porta_exterior"]["altura"]), _estado_config(doc), "inferencia", unidade="m",
                                 tipo="cota", fonte=self.fonte_config("aberturas.porta_exterior.altura"), nota=doc)
            return pe, campo(OMISSAO_PORTA_EXTERIOR, REVIEW, "valor_omissao", unidade="m", tipo="cota",
                             nota="Valor por omissão do motor: a altura não está nos desenhos lidos.")
        if "janela" in A:
            jn = A["janela"]
            return tuple(campo(_r(jn[k]), _estado_config(doc), "inferencia", unidade="m", tipo="cota",
                               fonte=self.fonte_config(f"aberturas.janela.{k}"), nota=doc) for k in ("peitoril", "topo"))
        return tuple(campo(OMISSAO_JANELA[k], REVIEW, "valor_omissao", unidade="m", tipo="cota",
                           nota="Valor por omissão do motor: não está nos desenhos lidos.") for k in ("peitoril", "topo"))

    def paredes(self, est_geo):
        if not self.planta:
            return []
        fp = self.fonte_planta()
        por_parede = self.cfg.get("aberturas", {}).get("por_parede", {})
        out = []
        for w in self.planta["paredes"]:
            g = dict(estado=est_geo, metodo="geometria", unidade="m", fonte=fp)
            p = {"id": w["id"], "exterior": bool(w.get("exterior")), "eixo": w["eixo"],
                 "inicio": campo(_r(w["s0"]), tipo="geometria", **g), "fim": campo(_r(w["s1"]), tipo="geometria", **g),
                 "posicao": campo(_r(w["c"]), tipo="geometria", **g),
                 "espessura": campo(_r(w["espessura"]), tipo="dimensao", **g), "aberturas": []}
            for i, a in enumerate(w.get("aberturas", [])):
                tipo = campo(a["tipo"], est_geo, "geometria", tipo="classificacao", fonte=fp,
                             nota="Pela convenção de cores da planta (azul = vidro, magenta = porta).")
                sob = next((o for o in por_parede.get(w["id"], []) if o.get("i") == i), None)
                if sob and sob.get("tipo") and sob["tipo"] != a["tipo"]:
                    tipo = campo(sob["tipo"], INFERRED, "inferencia", tipo="classificacao",
                                 fonte=self.fonte_config(f"aberturas.por_parede.{w['id']}"), nota=sob.get("_doc", ""),
                                 conflitos=[{"valor": a["tipo"], "fonte": fp, "estado": "resolvido",
                                             "nota": "A planta desenha-o de outro tipo.",
                                             "resolucao": "Prevalece a configuração (lida dos alçados)."}])
                peit, alt = self._alturas(tipo["valor"], p["exterior"])
                ab = {"id": str(i), "tipo": tipo,
                      "inicio": campo(_r(a["s0"]), tipo="geometria", **g), "fim": campo(_r(a["s1"]), tipo="geometria", **g),
                      "largura": campo(_r(a["s1"] - a["s0"]), est_geo, "calculo", unidade="m", tipo="dimensao", fonte=fp),
                      "peitoril": peit, "altura": alt}
                if a["s0"] < w["s0"] - TOL or a["s1"] > w["s1"] + TOL:
                    self.conflito(f"paredes.{w['id']}.aberturas.{i}", "FAIL", "O vão sai fora da parede.")
                if peit["valor"] is not None and alt["valor"] is not None and peit["valor"] >= alt["valor"]:
                    self.conflito(f"paredes.{w['id']}.aberturas.{i}", "FAIL", "Peitoril acima do topo do vão.")
                p["aberturas"].append(ab)
            iv = sorted((a["s0"], a["s1"]) for a in w.get("aberturas", []))
            for (a0, a1), (b0, b1) in zip(iv, iv[1:]):
                if b0 < a1 - TOL:
                    self.conflito(f"paredes.{w['id']}.aberturas", "FAIL", f"Vãos sobrepostos ({a0:.2f}–{a1:.2f} e {b0:.2f}–{b1:.2f}).")
            out.append(p)
        return out

    def comparar_modulos_reais(self, paredes):
        """Openings as built (DiscoverCasa module drawings) against the plan + config: the built one wins."""
        mr = self.cfg.get("modulos_reais")
        if not mr or not mr.get("ficheiro"):
            return
        dados = ler_json(self.dir / mr["ficheiro"])
        fmr = lambda m: fonte(dados.get("origem", mr["ficheiro"]), None, f"módulo {m['nome']}")  # noqa: E731
        reais = []  # (module, eixo, linha, a0, a1, v0, v1, tipo)
        for m in dados.get("modulos", []):
            x0, x1, y0, y1 = m["pegada"]
            linha, base = ((y0 + y1) / 2, x0) if m["eixo"] == "x" else ((x0 + x1) / 2, y0)
            for a in m.get("aberturas", []):
                reais.append([m, m["eixo"], linha, base + a["u"][0], base + a["u"][1], a["v"][0], a["v"][1], a["tipo"], False])
        for p in paredes:
            meia = p["espessura"]["valor"] / 2 + 0.15
            for ab in p["aberturas"]:
                s0, s1 = ab["inicio"]["valor"], ab["fim"]["valor"]
                melhor, sob = None, 0.0
                for r in reais:
                    if r[1] != p["eixo"] or abs(r[2] - p["posicao"]["valor"]) > meia:
                        continue
                    o = min(s1, r[4]) - max(s0, r[3])
                    if o > sob:
                        melhor, sob = r, o
                if not melhor or sob < 0.5 * min(s1 - s0, melhor[4] - melhor[3]):
                    ab["tipo"]["conflitos"].append({"valor": None, "fonte": fonte(dados.get("origem", "")),
                                                   "estado": "aberto", "nota": "Sem vão correspondente nos módulos como construídos."})
                    self.conflito(f"paredes.{p['id']}.aberturas.{ab['id']}.tipo", REVIEW,
                                  f"Vão {ab['tipo']['valor']} da planta ({s0:.2f}–{s1:.2f}) sem correspondência "
                                  "nos módulos como construídos.")
                    continue
                melhor[8] = True
                m, f = melhor[0], fmr(melhor[0])
                pares = (("largura", melhor[4] - melhor[3]), ("peitoril", melhor[5]), ("altura", melhor[6]),
                         ("tipo", melhor[7]))
                for k, real in pares:
                    c = ab[k]
                    antigo = c["valor"]
                    difere = (antigo != real) if k == "tipo" else (antigo is None or abs(antigo - real) > TOL)
                    herdados = [dict(cf, resolucao=RESOLUCAO_MODULOS) if cf.get("estado") == "resolvido" else cf
                                for cf in c["conflitos"]]
                    novo = campo(real if k == "tipo" else _r(real), CONFIRMED, "desenho_empresa", unidade=c["unidade"],
                                 tipo=c["tipo"], fonte=f, nota="Como construído (desenho de módulos da DiscoverCasa).",
                                 conflitos=herdados)
                    if difere and antigo is not None:
                        novo["conflitos"].append({"valor": antigo, "fonte": c["fonte"], "estado": "resolvido",
                                                  "nota": f"Planta/configuração: {antigo}.",
                                                  "resolucao": RESOLUCAO_MODULOS})
                    ab[k] = novo
        for r in reais:
            if not r[8]:
                self.conflito(f"modulos_reais.{r[0]['nome']}", "WARNING",
                              f"Vão {r[7]} no módulo {r[0]['nome']} sem vão correspondente na planta.")

    def lajes(self, est_geo):
        f = self.cfg.get("fundacao", {})
        if not f:
            return []
        nota = f.get("nota", "")
        return [{"id": "fundacao", "funcao": "base de fundação",
                 "contorno": campo(f.get("contorno"), mais_fraco(est_geo, INFERRED), "inferencia", unidade="m",
                                   tipo="geometria", fonte=self.fonte_config("fundacao.contorno"), nota=nota),
                 "espessura": campo(_r(f["espessura_laje"]), INFERRED, "inferencia", unidade="m", tipo="dimensao",
                                    fonte=self.fonte_config("fundacao.espessura_laje"), nota=nota)
                 if "espessura_laje" in f else em_falta("dimensao", unidade="m")}]

    def cobertura(self):
        cob = self.cfg.get("cobertura", {})
        doc = cob.get("_doc", "")
        out = {}
        for k, v in cob.items():
            if k.startswith("_") or isinstance(v, (dict, list)):
                continue
            out[k] = campo(_r(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v,
                           _estado_config(doc), "inferencia",
                           unidade={"inclinacao_pct": "%"}.get(k, "m" if isinstance(v, (int, float)) else ""),
                           tipo="dimensao" if isinstance(v, (int, float)) else "classificacao",
                           fonte=self.fonte_config(f"cobertura.{k}"), nota=doc)
        return out

    def materiais(self):
        out = []
        for el, v in self.cfg.get("camadas", {}).items():
            if el.startswith("_") or not isinstance(v, dict) or "opcao_visivel" not in v:
                continue
            op = v["opcao_visivel"]
            dados = (v.get("opcoes") or {}).get(op) or {}
            nota = dados.get("_doc", "") if isinstance(dados, dict) else ""
            camadas = [c.get("material") or c.get("nome") for c in dados.get("camadas", [])] if isinstance(dados, dict) else []
            out.append({"elemento": el, "camadas": [c for c in camadas if c],
                        "opcao": campo(op, INFERRED, "inferencia", tipo="material",
                                       fonte=self.fonte_config(f"camadas.{el}.opcao_visivel"), nota=nota)})
        return out

    def terreno(self):
        n = "Fase 2: ler o levantamento topográfico."
        return {"fonte": em_falta("terreno", "Nenhum levantamento indicado."),
                "crs": em_falta("terreno", n), "datum_vertical": em_falta("terreno", n),
                "unidade_horizontal": em_falta("terreno", n), "unidade_vertical": em_falta("terreno", n),
                "limite_lote": em_falta("terreno", n), "data_levantamento": em_falta("terreno", n),
                "precisao": em_falta("terreno", n), "pontos_controlo": em_falta("terreno", n)}

    # ------------------------------------------------------------------ declarations
    def aplicar_declaracoes(self, doc, regras):
        """Apply the hand-kept declarations whose pattern matches a field path; return the patterns used."""
        usados = set()
        for caminho, c in list(campos(doc)):
            for padrao, d in regras.items():
                if fnmatch.fnmatchcase(caminho, padrao):
                    usados.add(padrao)
                    if "valor" in d and d["valor"] is not None and c["valor"] is not None and \
                            not _iguais(d["valor"], c["valor"]):
                        self.conflito(caminho, REVIEW, f"Declarado {d['valor']} e no modelo {c['valor']}.")
                    for k in ("estado", "metodo", "fonte", "nota", "unidade"):
                        if k in d:
                            c[k] = copy.deepcopy(d[k])
                    if "valor" in d and c["valor"] is None:
                        c["valor"] = d["valor"]
                    for cf in d.get("conflitos", []):
                        c["conflitos"].append(copy.deepcopy(cf))
                    if c["estado"] == MISSING:
                        c["valor"] = None
        return usados

    # ------------------------------------------------------------------ all
    def construir(self):
        esc = self.escala()
        doc = {"versao_schema": VERSAO_ESQUEMA,
               "projeto": {"id": self.decl.get("projeto", {}).get("id", self.cp.parent.name),
                           "nome": self.decl.get("projeto", {}).get("nome", self.cfg.get("nome", "")),
                           "entrada": "planta_arquitetura" if self.planta else "configurador",
                           "config": self.cfg_nome, "planta": self.cfg.get("planta", ""),
                           "gerado_por": "step-inside/ferramentas/fontes/proveniencia.py"},
               "documentos": [], "referencial": self.referencial(), "escala": esc}
        # the scale first: the plan geometry inherits its state
        regras = self.decl.get("campos", {})
        usados = self.aplicar_declaracoes({"escala": esc}, {k: v for k, v in regras.items() if k == "escala"})
        est_geo = esc["estado"] if esc["estado"] in (CONFIRMED, INFERRED) else REVIEW
        paredes = self.paredes(est_geo)
        self.comparar_modulos_reais(paredes)
        doc.update(dimensoes=self.dimensoes(est_geo), niveis=self.niveis(), paredes=paredes,
                   lajes=self.lajes(est_geo), cobertura=self.cobertura(), materiais=self.materiais(),
                   terreno=self.terreno())
        usados |= self.aplicar_declaracoes({k: v for k, v in doc.items() if k != "escala"},
                                           {k: v for k, v in regras.items() if k != "escala"})
        for padrao in regras:
            if padrao not in usados:
                self.conflito(padrao, "WARNING", "Declaração sem campo correspondente (caminho errado?).")
        doc["documentos"] = self.documentos()
        for caminho, c in campos(doc):
            for cf in c["conflitos"]:
                if cf.get("estado") == "aberto" and not any(g["campo"] == caminho for g in self.conflitos):
                    self.conflito(caminho, REVIEW, cf.get("nota", "Conflito entre fontes."))
        doc["conflitos"] = self.conflitos
        doc["resumo"] = resumo(doc)
        return doc

    def documentos(self):
        out = []
        cat = {d["ficheiro"]: d for d in self.catalogo.get("documentos", [])}
        usados = {}
        if self.planta:
            usados.setdefault(self.planta["origem_desenho"].get("dwfx", ""), []).append("planta (paredes e vãos)")
        mr = self.cfg.get("modulos_reais")
        if mr and mr.get("ficheiro"):
            try:
                usados.setdefault(ler_json(self.dir / mr["ficheiro"]).get("origem", ""), []).append(
                    "vãos e módulos como construídos")
            except FileNotFoundError:
                pass
        for d in self.decl.get("documentos", []):
            usados.setdefault(d["ficheiro"], []).extend(d.get("usado_para", []))
        nomes = list(dict.fromkeys(list(usados) + list(cat)))
        for n in nomes:
            if not n:
                continue
            c = cat.get(n, {})
            ext = Path(n).suffix.lower()
            categoria = c.get("categoria") or FORMATOS.get(ext, (UNSUPPORTED,))[0]
            out.append({"ficheiro": n, "formato": c.get("formato", ext.lstrip(".").upper()), "categoria": categoria,
                        "usado_para": usados.get(n, []), "nota": c.get("nota", "")})
        return out


def _iguais(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, abs_tol=TOL)
    return a == b


def resumo(doc):
    r = {k: 0 for k in (CONFIRMED, INFERRED, MISSING, REVIEW)}
    for _, c in campos(doc):
        r[c["estado"]] += 1
    r["conflitos_abertos"] = sum(1 for c in doc["conflitos"] if c["estado"] == "aberto")
    r["conflitos_resolvidos"] = sum(1 for c in doc["conflitos"] if c["estado"] == "resolvido") + \
        sum(1 for _, c in campos(doc) for cf in c["conflitos"] if cf.get("estado") == "resolvido")
    return r


def construir(config, declaracoes=None, catalogo=None):
    return Construtor(config, declaracoes, catalogo).construir()


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--declaracoes")
    ap.add_argument("--catalogo")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    doc = construir(a.config, ler_json(a.declaracoes) if a.declaracoes else None,
                    ler_json(a.catalogo) if a.catalogo else None)
    erros = validar(doc)
    escrever_json(a.saida, doc)
    print(f"{a.saida}: {doc['resumo']}")
    if erros:
        print("Schema: " + "; ".join(erros[:10]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
