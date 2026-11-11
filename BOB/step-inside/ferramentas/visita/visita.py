"""Step Inside Phase 2 — the visit model of a house on its site (hub tasks 57, 58, 61).

    python step-inside/ferramentas/visita/visita.py step-inside/projetos-teste/<obra>/visita.json [--blender EXE]

Reuses what exists: the production model built by ferramentas/modelo/construir_casa.py (its .blend is opened, not
rebuilt), the timber clash check ferramentas/modelo/verificar.py, the Phase 1 sources (fontes.json) and the terrain
of terreno/terreno.py. blender_visita.py makes the visit file: semantic collections and stable ids, the house placed
on the site, the terrain (with a platform when declared) and the checks. This command adds the placement (read from
the drawings, each value with estado / método / fonte) and writes the report.

Outputs. Committed (step-inside/projetos-teste/<obra>/): visita_resumo.json, visita_relatorio.md (numbers and states).
Local only (_trabalho/step-inside/<obra>/visita/): visita.blend, visita.glb, preview.png (real site position).
Exit code: 0 PASS / WARNING, 2 NEEDS_HUMAN_REVIEW, 1 FAIL.
"""
import argparse
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "fontes"))
sys.path.insert(0, str(AQUI.parent / "terreno"))
import comum  # noqa: E402
import georef  # noqa: E402
from comum import CONFIRMED, INFERRED, MISSING, REVIEW, campo, em_falta, fonte  # noqa: E402
from terreno import pasta_desenhos  # noqa: E402

BOB = comum.BOB
NUM = re.compile(r"[<>\s]*(-?\d+[.,]\d+)[<>\s]*$")


def _f(s):
    return float(s.replace(",", "."))


def ler_folha(obra_pasta, ficheiro, folha):
    from ferramentas.dwfx.leitor import Dwfx, linhas
    p = pasta_desenhos(obra_pasta, ficheiro)
    if not p:
        raise SystemExit(f"não encontrei {ficheiro} (os desenhos ficam só no PC)")
    d = Dwfx(p)
    return linhas(d.glyphs(folha)), d.paths(folha)


def rotulo_perto(tx, perto, padrao, raio=3.0):
    cand = [(math.dist((l["x"], l["y"]), perto), l) for l in tx if padrao.match(l["text"].strip())]
    cand = [c for c in cand if c[0] <= raio]
    return min(cand, key=lambda c: c[0])[1] if cand else None


def poligono_que_contem(paths, ponto, estilo):
    melhor = None
    for p in paths:
        if (p["stroke"] or "").upper() != estilo["stroke"].upper() or abs(p["sw"] - estilo.get("sw", p["sw"])) > 0.015:
            continue
        for s, _cl in p["subs"]:
            if len(s) < 4:
                continue
            c = False
            for i in range(len(s)):
                x0, y0 = s[i]
                x1, y1 = s[(i + 1) % len(s)]
                if (y0 > ponto[1]) != (y1 > ponto[1]) and ponto[0] < x0 + (ponto[1] - y0) * (x1 - x0) / (y1 - y0):
                    c = not c
            if c:
                a = abs(sum(s[i][0] * s[(i + 1) % len(s)][1] - s[(i + 1) % len(s)][0] * s[i][1] for i in range(len(s)))) / 2
                if melhor is None or a < melhor[0]:
                    melhor = (a, s)
    return melhor[1] if melhor else None


def declarado(d, tipo=""):
    return campo(d.get("valor"), d["estado"], d.get("metodo", "utilizador"), unidade=d.get("unidade", ""), tipo=tipo,
                 fonte=d.get("fonte"), nota=d.get("nota", ""))


def tramas_dxf(caminho, camada, tipo, centro, raio, area_max):
    """Vertices of the hatches (e.g. the walls' poché) of one layer around a point, in the file's coordinates."""
    sys.path.insert(0, str(AQUI.parent / "terreno"))
    import leitores
    texto = Path(caminho).read_bytes().decode("utf-8", errors="replace")
    ents, _h = leitores._entidades(leitores._pares_dxf(texto))
    pts = []
    for tp, cs in ents:
        if tp != "HATCH" or leitores._g(cs, 8) != camada or (tipo and leitores._g(cs, 2) != tipo):
            continue
        xs = [float(v) for c, v in cs if c == 10][1:]  # the first 10/20 is the hatch's elevation point
        ys = [float(v) for c, v in cs if c == 20][1:]
        q = [(x, y) for x, y in zip(xs, ys) if math.hypot(x - centro[0], y - centro[1]) < raio]
        if len(q) < 4:
            continue
        a = abs(sum(q[i][0] * q[(i + 1) % len(q)][1] - q[(i + 1) % len(q)][0] * q[i][1] for i in range(len(q)))) / 2
        if a < area_max:
            pts += q
    return pts


def implantacao_ajuste(decl, fontes_doc, terreno_local):
    """The house drawn in real coordinates in a DXF (proposal over the survey): fit the model's walls to the walls'
    hatches. Returns (campos, local)."""
    import ajuste
    I = decl["implantacao"]
    campos, local = {}, {}
    f = pasta_desenhos(decl["obra_pasta"], I["ficheiro"])
    lim = terreno_local["superficies"][0]["limites_abs"]
    if not f or not lim:
        campos["posicao"] = campo(None, REVIEW, "geometria", nota="sem o DXF ou sem o limite do lote do terreno")
        return campos, local
    L0 = lim[0]
    centro = (sum(q[0] for q in L0) / len(L0), sum(q[1] for q in L0) / len(L0))
    pts = tramas_dxf(f, I["camada"], I.get("tipo_trama", "SOLID"), centro, I.get("raio_m", 40.0), I.get("area_max_m2", 60.0))
    paredes = [{"eixo": p["eixo"], "inicio": p["inicio"]["valor"], "fim": p["fim"]["valor"], "posicao": p["posicao"]["valor"],
                "espessura": p["espessura"]["valor"]} for p in fontes_doc["paredes"] if p.get("piso", 0) == 0]
    if len(pts) < 20:
        campos["posicao"] = campo(None, REVIEW, "geometria", nota=f"só {len(pts)} pontos de trama na camada {I['camada']}")
        return campos, local
    r = ajuste.ajustar(pts, paredes)
    src = fonte(I["ficheiro"], None, f"tramas das paredes, camada {I['camada']}")
    bom = r["inliers"] >= 0.8 * r["n"] and r["mediana_m"] is not None and r["mediana_m"] <= 0.05 and r["inliers"] > 1.5 * r["segundo_inliers"]
    est = CONFIRMED if bom else REVIEW
    nota = (f"paredes do modelo ajustadas às tramas das paredes da planta: {r['inliers']} de {r['n']} pontos sobre as "
            f"paredes (mediana {r['mediana_m']:.3f} m, p90 {r['p90_m']:.3f} m); a segunda orientação só tem "
            f"{r['segundo_inliers']}").replace(".", ",")
    campos["posicao"] = campo("só no PC", est, "geometria", tipo="referencial", fonte=src, nota=nota)
    campos["rotacao_graus"] = campo(r["rotacao_graus"], est, "geometria", unidade="°", tipo="geometria", fonte=src,
                                    nota="eixo X do modelo medido a partir do eixo das abcissas do sistema de coordenadas")
    o = comum.ler_json(BOB / "_trabalho" / "step-inside" / decl["obra"] / "terreno" / "terreno_local.json")["origem"]
    local["origem_xy"] = [r["origem"][0] - o["x"], r["origem"][1] - o["y"]]
    local["rotacao_graus"] = r["rotacao_graus"]
    if I.get("cota_pavimento"):
        campos["cota_pavimento"] = declarado(I["cota_pavimento"], "nivel")
        local["cota_pavimento"] = I["cota_pavimento"]["valor"]
    return campos, local


def implantacao(decl, origem):
    """Placement fields (committed: states and relative numbers) + the local values for Blender."""
    I = decl["implantacao"]
    campos, local = {}, {}
    ref = I["coordenadas"]
    tx, paths = ler_folha(decl["obra_pasta"], ref["ficheiro"], ref["folha"])
    src = fonte(ref["ficheiro"], ref["folha"], f"rótulos perto de {ref['perto_mm']} mm (folha)")
    m = rotulo_perto(tx, ref["perto_mm"], georef.ROTULO_M)
    p = rotulo_perto(tx, ref["perto_mm"], georef.ROTULO_P)
    g = georef.grelha_dwfx(tx, paths)
    if m and p:
        M = _f(georef.ROTULO_M.match(m["text"]).group(1))
        P = _f(georef.ROTULO_P.match(p["text"]).group(1))
        nota = f"canto {I['canto']} do contorno da casa {I.get('lote', '')}: coordenadas escritas no desenho"
        if g:  # the written coordinates vs the sheet's grid at the corner mark
            X, Y = georef.aplicar(g["coef"], (m["x"], m["y"]))
            nota += f"; confere com a quadrícula da folha a {math.hypot(X - M, Y - P):.2f} m (posição do rótulo)".replace(".", ",")
        campos["canto"] = campo("só no PC", CONFIRMED, "texto", tipo="referencial", fonte=src, nota=nota)
        local["alvo_abs"] = [M, P]
        if origem:
            local["alvo_xy"] = [M - origem[0], P - origem[1]]
    else:
        campos["canto"] = campo(None, REVIEW, "texto", tipo="referencial", fonte=src,
                                nota="não encontrei os dois rótulos de coordenadas (…mM e …mP) perto do ponto indicado")
    c = I.get("cota")
    if c:
        l = rotulo_perto(ler_folha(decl["obra_pasta"], c["ficheiro"], c["folha"])[0] if (c["ficheiro"], c["folha"]) !=
                         (ref["ficheiro"], ref["folha"]) else tx, c["perto_mm"], NUM)
        if l:
            v = _f(NUM.match(l["text"].strip()).group(1))
            campos["cota_pavimento"] = campo(v, INFERRED, "texto", unidade="m", tipo="nivel",
                                             fonte=fonte(c["ficheiro"], c["folha"], f"rótulo '{l['text'].strip()}'"),
                                             nota=c.get("nota", "cota com seta dentro do contorno da casa, lida como a do "
                                                                "pavimento acabado do rés do chão"))
        else:
            campos["cota_pavimento"] = campo(None, REVIEW, "texto", tipo="nivel", nota="rótulo da cota não encontrado")
    else:
        campos["cota_pavimento"] = em_falta("nivel", "sem cota de implantação")
    for k in ("rotacao_graus", "pavimento_acima_laje", "contorno_desenho_m"):
        if k in I:
            campos[k] = declarado(I[k], "geometria" if k != "pavimento_acima_laje" else "nivel")
    if campos.get("cota_pavimento", {}).get("valor") is not None and "pavimento_acima_laje" in campos:
        local["z_laje"] = campos["cota_pavimento"]["valor"] - campos["pavimento_acima_laje"]["valor"]
    local["canto"] = I["canto"]
    local["rotacao_graus"] = (campos.get("rotacao_graus") or {}).get("valor") or 0.0
    return campos, local, g


def plataforma(decl, origem, z_laje, campos):
    PL = decl.get("plataforma")
    if PL and PL.get("tipo") == "contorno_casa":  # flat ground around the house at a drawn exterior level
        c = PL["cota"]
        campos["plataforma"] = campo({"margem_m": PL.get("margem_m", 1.0), "cota": c["valor"]}, INFERRED, "geometria",
                                     tipo="terreno", fonte=c.get("fonte"),
                                     nota=PL.get("nota", "terreno plano à volta da casa (modelação aproximada)"))
        return {"contorno_casa": True, "margem_m": PL.get("margem_m", 1.0), "z": c["valor"], "nota": PL.get("nota", "")}
    if not PL or origem is None or z_laje is None:
        return None
    tx, paths = ler_folha(decl["obra_pasta"], PL["ficheiro"], PL["folha"])
    g = georef.grelha_dwfx(tx, paths)
    poly = poligono_que_contem(paths, PL["contem_mm"], PL["estilo"])
    if not poly or not g:
        campos["plataforma"] = campo(None, REVIEW, "geometria", nota="contorno da plataforma não encontrado")
        return None
    pts = [georef.aplicar(g["coef"], q) for q in poly]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    # default 2 cm under the slab top: level with it, the ground coincided with the slab where it runs past the walls
    # and the two flickered (Sobral, team note on the AR test, 2026-11-10)
    z = z_laje + PL.get("acima_da_laje", -0.02)
    area = abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2
    campos["plataforma"] = campo({"area_m2": round(area, 1), "vertices": len(pts), "cota": ("laje %+.2f m" % PL.get("acima_da_laje", -0.02)).replace(".", ",")},
                                 INFERRED, "geometria", tipo="terreno",
                                 fonte=fonte(PL["ficheiro"], PL["folha"], "contorno que contém a casa"),
                                 nota=PL.get("nota", "modelação simplificada: terreno plano dentro do contorno"))
    return {"contorno": [[x - origem[0], y - origem[1]] for x, y in pts], "z": z, "nota": PL.get("nota", "")}


def choques_madeira(cfg_path):
    """Timber clashes with the existing checker (ferramentas/modelo/verificar.py)."""
    from ferramentas.modelo.verificar import verificar
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    try:
        if cfg.get("planta"):
            from ferramentas.modelo.camadas import fundir, teto_sob_anel
            from ferramentas.modelo.casa_planta import construir
            planta = json.loads((cfg_path.parent / cfg["planta"]).read_text(encoding="utf-8"))
            S0 = json.loads((BOB / "ferramentas/modelo/sistema_construtivo.json").read_text(encoding="utf-8"))
            S = teto_sob_anel(fundir(S0, cfg.get("camadas") or {}), cfg)
            E = fundir(S["estrutura"], {k: v for k, v in (cfg.get("estrutura") or {}).items() if k != "sistema"})
            G, _ = construir(cfg, S, E, planta)
        elif (cfg.get("estrutura") or {}).get("sistema") == "discovercasa":
            with tempfile.TemporaryDirectory() as td:
                out = Path(td) / "geometria_dc.json"
                subprocess.run([sys.executable, str(BOB / "ferramentas/modelo/estrutura_dc.py"), str(cfg_path),
                                "--saida", str(out)], check=True, capture_output=True)
                G = json.loads(out.read_text(encoding="utf-8"))
        else:
            G = json.loads((cfg_path.parent / cfg["saida"]["geometria"]).read_text(encoding="utf-8"))
        r = verificar(G)
    except Exception as e:  # noqa: BLE001 - reported, not fatal
        return {"erro": f"{type(e).__name__}: {e}"}
    from collections import Counter
    pares = Counter(" x ".join(sorted((c["a"].split(" ")[0], c["b"].split(" ")[0]))) for c in r["choques"])
    return {"pecas": r["pecas"], "choques": len(r["choques"]), "fora": len(r["fora"]),
            "por_tipo": dict(pares.most_common(8)), "maior_cm": r["choques"][0]["cm"] if r["choques"] else 0}


def aberturas(fontes_doc):
    niv = fontes_doc.get("niveis", {})
    z1 = (niv.get("piso1_interior") or niv.get("piso1_exterior") or {}).get("valor")
    out = []
    for p in fontes_doc["paredes"]:
        for a in p["aberturas"]:
            zp = 0.0 if p.get("piso", 0) == 0 else z1
            if zp is None or a["inicio"]["valor"] is None:
                continue
            out.append({"parede": p["id"], "id": a["id"], "tipo": a["tipo"]["valor"], "eixo": p["eixo"],
                        "posicao": p["posicao"]["valor"], "inicio": a["inicio"]["valor"], "fim": a["fim"]["valor"],
                        "espessura": 0.16 if p["espessura"]["valor"] is None else p["espessura"]["valor"], "z_piso": zp})
    return out


def alturas_paredes(cfg_path, cfg):
    """Wall heights from the engineer's elevations (geometry JSON 'alcados'), when the house has them."""
    g = cfg.get("saida", {}).get("geometria")
    try:
        G = json.loads((cfg_path.parent / g).read_text(encoding="utf-8")) if g else {}
    except (OSError, ValueError):
        return {}
    al = G.get("alcados") or {}
    return {p["nome"]: al[p["alcado"]]["H"] for p in G.get("paineis", []) if p.get("alcado") in al and "H" in al[p["alcado"]]}


def paredes_cheias(fontes_doc, alturas=None):
    """For the negative control: the middle of the longest stretch of each wall without openings (> 0.6 m).
    alturas: wall heights (m) where known — a low wall is only tested below its head."""
    niv = fontes_doc.get("niveis", {})
    z1 = (niv.get("piso1_interior") or niv.get("piso1_exterior") or {}).get("valor")
    out = []
    for p in fontes_doc["paredes"]:
        a0, a1 = sorted([p["inicio"]["valor"], p["fim"]["valor"]])
        zp = 0.0 if p.get("piso", 0) == 0 else z1
        if zp is None:
            continue
        cortes = sorted((min(a["inicio"]["valor"], a["fim"]["valor"]), max(a["inicio"]["valor"], a["fim"]["valor"]))
                        for a in p["aberturas"] if a["inicio"]["valor"] is not None)
        livres, x = [], a0 + 0.2  # keep away from the corners (crossing walls)
        for i, j in cortes:
            livres.append((x, i - 0.15))
            x = max(x, j + 0.15)
        livres.append((x, a1 - 0.2))
        seg = max(livres, key=lambda t: t[1] - t[0])
        if seg[1] - seg[0] >= 0.6:
            out.append({"parede": p["id"], "eixo": p["eixo"], "posicao": p["posicao"]["valor"], "inicio": seg[0],
                        "fim": seg[1], "espessura": p["espessura"]["valor"] or 0.16, "z_piso": zp,
                        "altura_max": (alturas or {}).get(p["id"])})
    return out


def avaliar(r, campos, terreno_gate):
    falhas, rever, avisos = [], [], []
    dm, df = r["modelo"].get("dimensoes_modelo", {}), r["dimensoes_fontes"]
    est = dm.get("estrutura_planta_m")
    if est and df.get("comprimento") and df.get("profundidade"):
        dif = max(abs(est[0] - df["comprimento"]["valor"]), abs(est[1] - df["profundidade"]["valor"]))
        r["dif_dimensoes_estrutura_m"] = round(dif, 3)
        if dif > 0.02 and CONFIRMED in (df["comprimento"]["estado"], df["profundidade"]["estado"]):
            falhas.append(f"planta da estrutura {est} m ≠ fontes {df['comprimento']['valor']} × {df['profundidade']['valor']} m")
    cd = campos.get("contorno_desenho_m")
    ac = dm.get("acabamento_planta_m")
    if cd and ac and cd["valor"]:
        dif = max(abs(ac[0] - cd["valor"][0]), abs(ac[1] - cd["valor"][1]))
        r["dif_contorno_implantacao_m"] = round(dif, 3)
        if dif > 0.05:
            avisos.append(f"contorno acabado do modelo {ac} m difere do contorno da implantação {cd['valor']} m em "
                          f"{dif:.2f} m")
    ms = r["modelo"].get("malhas", {})
    if ms.get("n_invertidas"):
        falhas.append(f"{ms['n_invertidas']} objetos com as normais para dentro")
    if ms.get("n_abertas"):
        avisos.append(f"{ms['n_abertas']} objetos com malha aberta")
    if ms.get("n_duplicados"):
        avisos.append(f"{ms['n_duplicados']} objetos repetidos no mesmo sítio")
    sc = r["modelo"].get("chao_vaos", {}).get("sem_chao", [])
    if sc:
        avisos.append(f"{len(sc)} portas sem chão no vão: " + ", ".join(x["abertura"] for x in sc[:8]))
    jr = r["modelo"].get("juntas", {}).get("restantes")
    if jr:
        avisos.append(f"{jr} juntas por fechar entre peças dos acabamentos")
    fech = r["modelo"].get("aberturas", {}).get("fechadas", [])
    if fech:
        rever.append(f"{len(fech)} aberturas das fontes estão fechadas no modelo: "
                     + ", ".join(f"{v['parede']}#{v['abertura']}" for v in fech[:8]))
    mt = r["modelo"].get("materiais")
    if mt:
        vis = [x for x in mt["sem_mapa"] if x["categoria"] not in ("STRUCT_TIMBER", "ARCH_OPTIONS", "ARCH_LABELS")]
        if vis:
            rever.append("materiais sem correspondência no catálogo: " + ", ".join(f"{x['material']} ({x['categoria']})"
                                                                              for x in vis[:6]))
        if mt.get("texturas_em_falta"):
            avisos.append("texturas do catálogo em falta neste PC: " + ", ".join(mt["texturas_em_falta"]) +
                          " (descarregar para _trabalho/step-inside/texturas/)")
        if mt["estados"].get("INFERRED"):
            avisos.append(f"materiais provisórios: {mt['estados']['INFERRED']} peças com um material por confirmar (ainda não está na "
                          f"lista oficial de materiais, ou não é o mesmo produto); {mt['estados'].get('CONFIRMED', 0)} peças confirmadas")
    ab = r["modelo"].get("aberturas", {})
    if ab.get("controlo_abertas_por_engano"):
        rever.append(f"o teste das aberturas falhou o controlo: paredes cheias vistas como abertas "
                     f"({', '.join(ab['controlo_abertas_por_engano'][:6])}) — ver o modelo")
    ch = r.get("choques_madeira", {})
    if ch.get("erro"):
        avisos.append(f"verificação de choques da madeira não correu ({ch['erro']})")
    elif ch.get("choques"):
        avisos.append(f"{ch['choques']} choques entre peças de madeira > 8 mm no modelo de produção (verificar.py)")
    for k, c in campos.items():
        if c["estado"] == REVIEW:
            rever.append(f"implantação: {k} a rever ({c.get('nota', '')})")
        elif c["estado"] in (INFERRED, MISSING) and k != "canto":
            avisos.append(f"implantação: {k} {c['estado']}")
    ce = r["modelo"].get("casa_terreno_existente")
    if ce and ce.get("amostras") and r["modelo"].get("plataforma"):
        avisos.append(f"terreno existente entre {ce['terreno_menos_laje_min_m']:.2f} e {ce['terreno_menos_laje_max_m']:.2f} m "
                      "da laje sob a casa: a plataforma (modelação simplificada) corrige-o no modelo".replace(".", ","))
    if r["modelo"].get("chao_provisorio"):
        avisos.append("chão provisório plano: não é terreno (falta o levantamento)")
    ct = r["modelo"].get("casa_terreno")
    if ct and ct.get("amostras"):
        if ct["fracao_terreno_acima_do_pavimento"] > 0.02:
            avisos.append(f"o terreno fica acima do pavimento em {round(100 * ct['fracao_terreno_acima_do_pavimento'])} % "
                          f"da casa (até {ct['terreno_menos_laje_max_m']:.2f} m acima da laje): falta a modelação do terreno")
        if ct["terreno_menos_laje_min_m"] < -1.0:
            avisos.append(f"a laje fica até {-ct['terreno_menos_laje_min_m']:.2f} m acima do terreno: falta aterro / fundação")
    elif r.get("terreno") is None and not r["modelo"].get("chao_provisorio"):
        avisos.append("sem terreno (levantamento em falta)")
    if terreno_gate in ("WARNING", "NEEDS_HUMAN_REVIEW"):
        avisos.append(f"terreno: {terreno_gate}")
    if falhas:
        return "FAIL", falhas + rever + avisos
    if rever:
        return "NEEDS_HUMAN_REVIEW", rever + avisos
    if avisos:
        return "WARNING", avisos
    return "PASS", []


def _n(v, casas=2):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{casas}f}".replace(".", ",")
    if isinstance(v, (list, tuple)):
        return " × ".join(_n(x, casas) for x in v)
    return str(v)


def relatorio_md(r, decl):
    m = r["modelo"]
    L = [f"# Modelo de visita · {decl.get('nome', r['obra'])}", "", f"**Resultado: {r['resultado']}**", ""]
    L += [f"- {x}" for x in r["motivos"]] + [""]
    L += ["Gerado por `step-inside/ferramentas/visita/visita.py` a partir de `visita.json`. O modelo de visita fica só "
          "no PC (`_trabalho/step-inside/<obra>/visita/`): tem a posição real da casa.", "",
          "## O que se reutilizou", "",
          f"- Modelo de produção: `{r['casa_blend']}` (gerado por `ferramentas/modelo/construir_casa.py`, aberto sem o mudar).",
          "- Fontes da Fase 1: `fontes.json` (dimensões, paredes e aberturas com a origem de cada valor).",
          "- Choques da madeira: `ferramentas/modelo/verificar.py`.", "",
          "## Coleções semânticas", "", "| Coleção | Objetos | Na visita |", "|---|---|---|"]
    for k, n in sorted(m.get("objetos_por_categoria", {}).items()):
        L.append(f"| {k} | {n} | {'não (fica no ficheiro)' if k in ('STRUCT_TIMBER', 'ARCH_OPTIONS', 'ARCH_LABELS') else 'sim'} |")
    L += ["", "Cada objeto tem `si_id` = `<coleção>/<nome do objeto>` (os nomes vêm dos desenhos e não mudam), "
          "`si_categoria`, `si_colecao_producao` e `si_material`.", "", "## Implantação", "",
          "| Campo | Valor | Estado | Método | Nota |", "|---|---|---|---|---|"]
    for k, c in r["implantacao"].items():
        v = c["valor"]
        if isinstance(v, dict):
            v = ", ".join(f"{a} {_n(b, 2)}" for a, b in v.items())
        L.append(f"| {k} | {_n(v)} | {c['estado']} | {c['metodo']} | {c.get('nota', '')} |")
    dm = m.get("dimensoes_modelo", {})
    df = r["dimensoes_fontes"]
    L += ["", "## Verificações", "",
          f"- **Dimensões:** estrutura do modelo {_n(dm.get('estrutura_planta_m'), 3)} m; fontes "
          f"{_n((df.get('comprimento') or {}).get('valor'), 3)} × {_n((df.get('profundidade') or {}).get('valor'), 3)} m "
          f"(diferença {_n(r.get('dif_dimensoes_estrutura_m'), 3)} m). Contorno acabado {_n(dm.get('acabamento_planta_m'), 3)} m"
          + (f"; contorno da implantação {_n(r['implantacao']['contorno_desenho_m']['valor'], 3)} m (diferença "
             f"{_n(r.get('dif_contorno_implantacao_m'), 3)} m)." if "contorno_desenho_m" in r["implantacao"] else "."),
          f"- **Malhas:** {m['malhas']['verificadas']} objetos visíveis; abertas {m['malhas']['n_abertas']}, normais para "
          f"dentro {m['malhas']['n_invertidas']}, repetidos {m['malhas']['n_duplicados']}.",
          f"- **Aberturas:** {m['aberturas']['verificadas']} das fontes procuradas no modelo (raios horizontais através da "
          f"parede, de 0,3 a 2,0 m acima do piso); fechadas: {len(m['aberturas']['fechadas'])}. Controlo: "
          f"{m['aberturas'].get('controlo_paredes_cheias', 0)} troços de parede cheia, vistos como abertos: "
          f"{len(m['aberturas'].get('controlo_abertas_por_engano', []))}."]
    jt = m.get("juntas")
    if jt:
        L.append("- **Juntas dos acabamentos** (o modelo de produção desenha cada tábua e placa com a sua junta; em obra "
                 "ficam fechadas): fechadas " + (", ".join(f"{k} {v}" for k, v in sorted(jt["fechadas"].items())) or "nenhuma")
                 + f"; por fechar {jt['restantes']}.")
    cg = m.get("caixilharia_gerada")
    if cg and cg["vaos"]:
        L.append(f"- **Caixilharia padrão nos vãos exteriores sem caixilho** (INFERRED: alumínio RAL 7016 e vidro duplo, "
                 f"pergunta 12 por obra; o tipo de cada vão vem da tabela de vãos do projeto): {cg['vaos']} vãos.")
    cv = m.get("chao_vaos")
    if cv:
        L.append(f"- **Chão nos vãos das portas:** {cv['portas']} portas; chão acrescentado em {cv['criados']} peças, "
                 f"{cv['ja_com_chao']} já tinham chão ou soleira; sem chão (raio a descer do meio do vão): "
                 f"{len(cv['sem_chao'])}.")
    ch = r.get("choques_madeira", {})
    L.append(f"- **Choques da madeira** (verificar.py, > 8 mm): " + (ch.get("erro") or
             f"{ch.get('choques')} em {ch.get('pecas')} peças" + (f" — {', '.join(f'{k}: {v}' for k, v in ch['por_tipo'].items())}"
                                                                 if ch.get("por_tipo") else "") + "."))
    ce = m.get("casa_terreno_existente")
    if ce and ce.get("amostras"):
        L.append(f"- **Terreno existente sob a casa** (antes da plataforma): entre {_n(ce['terreno_menos_laje_min_m'])} e "
                 f"{_n(ce['terreno_menos_laje_max_m'])} m da laje; acima do pavimento em "
                 f"{round(100 * ce['fracao_terreno_acima_do_pavimento'])} % da área.")
    if m.get("chao_provisorio"):
        L.append(f"- **Chão provisório:** plano de {_n(m['chao_provisorio']['tamanho_m'], 0)} m à cota "
                 f"{_n(m['chao_provisorio']['z'])} do modelo. Não é terreno: falta o levantamento.")
    ct = m.get("casa_terreno")
    if ct and ct.get("amostras"):
        L.append(f"- **Casa e terreno** ({ct['amostras']} pontos sob a casa): terreno entre {_n(ct['terreno_menos_laje_min_m'])} e "
                 f"{_n(ct['terreno_menos_laje_max_m'])} m da laje; acima do pavimento em "
                 f"{round(100 * ct['fracao_terreno_acima_do_pavimento'])} % da área.")
    if m.get("plataforma"):
        L.append(f"- **Plataforma:** terreno plano dentro do contorno da plataforma ({m['plataforma']['vertices_rebaixados_ou_subidos']} "
                 "vértices do terreno ajustados).")
    mt = m.get("materiais")
    if mt:
        L += ["", "## Materiais (catálogo comum `MAT_*`)", "",
              f"Os materiais de produção foram trocados pelos do catálogo comum (`step-inside/materiais/catalogo.json`, "
              f"mapeamento `mapeamentos/{r.get('construtor', 'discovercasa')}.json`). Estados dos mapeamentos usados: "
              + ", ".join(f"{k} {v}" for k, v in sorted(mt["estados"].items())) + ".", "",
              "| ID | Objetos |", "|---|---|"]
        com_tex = set(mt.get("com_textura", []))
        L[-1] = "|---|---|---|"
        L[-2] = "| ID | Objetos | Textura |"
        L += [f"| `{k}` | {v} | {'sim' if k in com_tex else '—'} |" for k, v in mt["usados"].items()]
        if mt["sem_mapa"]:
            L += ["", "**Sem correspondência:** " + ", ".join(f"{x['material']} ({x['categoria']}, {x['objetos']})"
                                                             for x in mt["sem_mapa"])]
    L += ["", "## Ficheiros (só no PC)", "", "- `visita.blend` (coleções VISITA > SITE / HOUSE), `visita.glb` (o que está visível), "
          "`preview.png`.", ""]
    return "\n".join(L)


def main():
    comum.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("declaracao")
    ap.add_argument("--blender")
    a = ap.parse_args()
    dpath = Path(a.declaracao).resolve()
    decl = comum.ler_json(dpath)
    obra = decl["obra"]
    local = BOB / "_trabalho" / "step-inside" / obra / "visita"
    local.mkdir(parents=True, exist_ok=True)
    cfg_path = BOB / decl["casa"]["config"]
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    casa_blend = cfg_path.parent / cfg["saida"]["blend"]
    fontes_doc = comum.ler_json(BOB / decl["fontes"])

    origem, terreno_blend, terreno_gate = None, None, None
    T = decl.get("terreno")
    if T:
        tl = BOB / "_trabalho" / "step-inside" / obra / "terreno"
        if not (tl / "terreno_local.json").exists():
            raise SystemExit("primeiro o terreno: python step-inside/ferramentas/terreno/terreno.py " + T["declaracao"])
        o = comum.ler_json(tl / "terreno_local.json")["origem"]
        origem = (o["x"], o["y"])
        terreno_blend = tl / "terreno.blend"
        terreno_gate = comum.ler_json(BOB / Path(T["declaracao"]).parent / "terreno_resumo.json")["resultado"]
    campos, coloc, z_laje = {}, None, None
    if decl.get("implantacao") and decl["implantacao"].get("metodo") == "ajuste_tramas_dxf":
        tl = comum.ler_json(BOB / "_trabalho" / "step-inside" / obra / "terreno" / "terreno_local.json")
        campos, loc = implantacao_ajuste(decl, fontes_doc, tl)
        if loc.get("origem_xy") and loc.get("cota_pavimento") is not None:
            coloc = {"origem_xy": loc["origem_xy"], "rotacao_graus": loc["rotacao_graus"],
                     "cota_pavimento": loc["cota_pavimento"]}
    elif decl.get("implantacao"):
        campos, loc, _g = implantacao(decl, origem)
        z_laje = loc.get("z_laje")
        if loc.get("alvo_xy") and z_laje is not None:
            coloc = {"alvo_xy": loc["alvo_xy"], "canto": loc["canto"], "rotacao_graus": loc["rotacao_graus"], "z_laje": z_laje}
    pl = plataforma(decl, origem, z_laje, campos)
    sys.path.insert(0, str(AQUI.parent / "materiais"))
    import materiais
    cat, mp = materiais.ler(decl.get("construtor", "discovercasa"))
    erros_mat = materiais.validar(cat, mp)
    if erros_mat:
        raise SystemExit("catálogo de materiais inválido: " + "; ".join(erros_mat[:5]))
    tabela_mat = materiais.resolver(cat, mp)
    run = {"casa_blend": str(casa_blend), "terreno_blend": str(terreno_blend) if terreno_blend else "",
           "superficie": (T or {}).get("superficie", "existente"), "colocacao": coloc, "plataforma": pl,
           "pavimento_acima_laje": (campos.get("pavimento_acima_laje") or {}).get("valor", 0.16),
           "chao_provisorio": decl.get("chao_provisorio"), "materiais": tabela_mat, "bob_dir": str(BOB),
           "estrutura_a_vista": mp.get("estrutura_a_vista", []), "material_terreno": decl.get("material_terreno"),
           "texturas": decl.get("texturas", True),
           "aberturas": aberturas(fontes_doc), "paredes_cheias": paredes_cheias(fontes_doc, alturas_paredes(cfg_path, cfg)), "blend": str(local / "visita.blend"), "glb": str(local / "visita.glb"),
           "preview": str(local / "preview.png"), "saida": str(local / "visita_modelo.json")}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump(run, fh)
        run_path = fh.name
    from ferramentas.comum import correr_blender
    code, out = correr_blender(AQUI / "blender_visita.py", [run_path], blend=casa_blend, blender=a.blender)
    Path(run_path).unlink(missing_ok=True)
    if code or "VISITA_OK" not in out:
        print(out[-3000:])
        raise SystemExit("Blender (blender_visita.py) falhou")
    modelo = comum.ler_json(local / "visita_modelo.json")
    if modelo.get("colocacao", {}).get("pavimento_rc_modelo_m") is not None and "pavimento_acima_laje" not in campos:
        campos["pavimento_acima_laje"] = campo(modelo["colocacao"]["pavimento_rc_modelo_m"], CONFIRMED, "calculo", unidade="m",
                                               tipo="nivel", nota="medido no modelo: topo do pavimento acabado do rés do chão "
                                                                  "sobre o topo da laje")
    r = {"obra": obra, "construtor": decl.get("construtor", "discovercasa"), "casa_blend": str(casa_blend.relative_to(BOB)).replace("\\", "/"), "modelo": modelo,
         "implantacao": campos, "dimensoes_fontes": {k: fontes_doc["dimensoes"].get(k) for k in ("comprimento", "profundidade")},
         "choques_madeira": choques_madeira(cfg_path), "terreno": terreno_gate}
    gate, motivos = avaliar(r, campos, terreno_gate)
    r["resultado"], r["motivos"] = gate, motivos
    if "colocacao" in modelo:  # relative numbers only
        modelo["colocacao"] = {k: v for k, v in modelo["colocacao"].items() if k != "alvo_xy"}
    comum.escrever_json(dpath.parent / "visita_resumo.json", r)
    (dpath.parent / "visita_relatorio.md").write_text(relatorio_md(r, decl), encoding="utf-8")
    print(f"{gate}: " + "; ".join(motivos[:5]))
    print(f"relatório: {dpath.parent / 'visita_relatorio.md'}")
    print(f"modelo local: {local / 'visita.blend'}  pré-visualização: {local / 'preview.png'}")
    sys.exit({"PASS": 0, "WARNING": 0, "NEEDS_HUMAN_REVIEW": 2, "FAIL": 1}[gate])


if __name__ == "__main__":
    main()
