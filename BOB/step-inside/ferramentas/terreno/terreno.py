"""Step Inside Phase 2 — terrain from a project's survey (hub tasks 59, 60, 61).

    python step-inside/ferramentas/terreno/terreno.py step-inside/projetos-teste/<obra>/terreno.json [--blender EXE]

The declaration (terreno.json, committed, no coordinates) lists each surface's sources and reading rules and the
facts a person stated (CRS, datum, survey date...) with their source. This command:
  1. reads every source (leitores.py), georeferences DWFx sheets from their coordinate grid (georef.py);
  2. moves everything to a local site origin (Blender keeps 32-bit floats) and builds the surfaces in Blender
     (blender_tin.py): TIN of points + contours, cross-validation, points vs contours, spikes;
  3. fills the terrain fields of the Phase 1 contract (crs, datum_vertical, units, lot limit, survey date,
     precision, control points) with estado / método / fonte;
  4. writes the report with PASS / WARNING / NEEDS_HUMAN_REVIEW / FAIL.

Outputs. Committed (step-inside/projetos-teste/<obra>/): terreno_resumo.json and terreno_relatorio.md — numbers
and states only. Local only (_trabalho/step-inside/<obra>/terreno/, git-ignored): the points in real coordinates,
the site origin and terreno.blend — a georeferenced survey locates a client's land, so it never goes to the public
repo (same rule as the drawings).
Exit code: 0 PASS / WARNING, 2 NEEDS_HUMAN_REVIEW, 1 FAIL.
"""
import argparse
import json
import math
import os
import statistics as st
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "fontes"))
import comum  # noqa: E402  (Phase 1 helpers; puts BOB/ on sys.path)
import georef  # noqa: E402
import leitores  # noqa: E402
from comum import CONFIRMED, INFERRED, MISSING, REVIEW, campo, em_falta, fonte  # noqa: E402

BOB = comum.BOB
CAMPOS_TERRENO = ("fonte", "crs", "datum_vertical", "unidade_horizontal", "unidade_vertical", "limite_lote",
                  "data_levantamento", "precisao", "pontos_controlo")


def pasta_desenhos(obra, ficheiro):
    """Drawings stay on the PC (never in Git). STEP_INSIDE_DESENHOS may point at the folder holding
    'Construção <obra>/desenhos/'; else BOB/ itself or the old BOB folder next to _trabalho/."""
    bases = [Path(os.environ["STEP_INSIDE_DESENHOS"])] if os.environ.get("STEP_INSIDE_DESENHOS") else []
    bases += [BOB, BOB.parents[2]]
    for b in bases:
        d = b / f"Construção {obra}" / "desenhos"
        if (d / ficheiro).exists():
            return d / ficheiro
    return None


def ler_fonte(decl, f):
    caminho = pasta_desenhos(decl["obra_pasta"], f["ficheiro"])
    if not caminho:
        raise SystemExit(f"não encontrei {f['ficheiro']} em 'Construção {decl['obra_pasta']}/desenhos/' "
                         "(os desenhos ficam só no PC; STEP_INSIDE_DESENHOS pode indicar a pasta)")
    if caminho.suffix.lower() == ".dwfx":
        return leitores.ler_dwfx(caminho, f["folha"], f)
    kw = {k: f[k] for k in ("colunas", "camadas", "passo") if k in f}
    lev = leitores.ler(caminho, **kw)
    # 2D lines: contours only on the layers declared as such (walls, roads, buildings are 2D lines too)
    cc = f.get("curvas_camadas", {})
    lims = set(f.get("limite_camadas", []))
    linhas = []
    for l in lev["linhas"]:
        if l["tipo"] != "linha2d":
            linhas.append(l)
        elif l["camada"] in cc:
            l["papel"] = cc[l["camada"]]
            linhas.append(l)
        elif l["camada"] in lims and len(l["pts"]) >= 4 and l["pts"][0][:2] == l["pts"][-1][:2]:
            lev["limites"].append([q[:2] for q in l["pts"][:-1]])
    lev["linhas"] = linhas
    if f.get("escolher_copia") and len(lev["limites"]) > 1:
        escolher_copia(lev, f.get("margem_m", 15.0))
    lev["contagens"]["curvas_2d_usadas"] = sum(1 for l in lev["linhas"] if l["tipo"] == "linha2d")
    if f.get("rotulos_como_pontos"):  # heights written as text at the point (declared after looking at the file)
        lev["pontos"] += [list(r) for r in lev["rotulos"]]
        lev["contagens"]["pontos_de_rotulos"] = len(lev["rotulos"])
    return lev


def _dist_poligono(x, y, poly):
    """0 inside, else the distance to the polygon's edges."""
    dentro = False
    best = 1e18
    for i in range(len(poly)):
        (x0, y0), (x1, y1) = poly[i][:2], poly[(i + 1) % len(poly)][:2]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            dentro = not dentro
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1e-12
        t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
        best = min(best, math.hypot(x0 + t * dx - x, y0 + t * dy - y))
    return 0.0 if dentro else best


def coincide_gnss(p, gnss):
    return any(abs(p[0] - g[0]) < 0.01 and abs(p[1] - g[1]) < 0.01 and abs(p[2] - g[2]) < 0.01 for g in gnss)


def escolher_copia(lev, margem):
    """Some CAD files hold several copies of the survey in model space (one per sheet), shifted from one another;
    only one sits at the real coordinates. That copy is the one whose lot boundary has the GNSS points written as
    text (E=, N=, h=) around it, matching the drawn 3D points. Keep it and what lies within `margem` of its boundary."""
    gnss = lev.get("gnss", [])
    pontos = lev["pontos"]

    def coincide(g):
        return any(abs(p[0] - g[0]) < 0.01 and abs(p[1] - g[1]) < 0.01 and abs(p[2] - g[2]) < 0.01 for p in pontos)
    reais = [g for g in gnss if coincide(g)]
    if not reais:
        lev["avisos"].append(f"{len(lev['limites'])} limites do lote e nenhum ponto GNSS escrito que coincida: "
                             "não sei que cópia está nas coordenadas reais (ver o desenho)")
        return
    contagem = [sum(1 for g in reais if _dist_poligono(g[0], g[1], L) <= margem) for L in lev["limites"]]
    k = max(range(len(contagem)), key=lambda i: contagem[i])
    L = lev["limites"][k]
    n0 = len(pontos)
    # points within the margin, plus the GNSS points (certainly of the real copy) a little further out
    lev["pontos"] = [p for p in pontos if _dist_poligono(p[0], p[1], L) <= margem or
                     (_dist_poligono(p[0], p[1], L) <= 3 * margem and coincide_gnss(p, reais))]
    novas = []
    for l in lev["linhas"]:  # cut lines where they leave the kept zone
        troco = []
        for q in l["pts"]:
            if _dist_poligono(q[0], q[1], L) <= margem:
                troco.append(q)
            else:
                if len(troco) >= 2:
                    novas.append(dict(l, pts=troco))
                troco = []
        if len(troco) >= 2:
            novas.append(dict(l, pts=troco))
    lev["linhas"] = novas
    lev["limites"] = [L]
    lev["contagens"]["copias_do_levantamento"] = len(contagem)
    lev["contagens"]["gnss_escritos"] = len(gnss)
    lev["contagens"]["gnss_que_coincidem"] = len(reais)
    lev["contagens"]["gnss_junto_da_copia_usada"] = contagem[k]
    lev["contagens"]["pontos_na_copia_usada"] = len(lev["pontos"])
    lev["avisos"].append(f"o ficheiro tem {len(contagem)} cópias do levantamento; usada a que tem à volta os pontos GNSS "
                         f"escritos que coincidem com os pontos 3D ({contagem[k]} de {len(reais)}), com {margem:g} m à "
                         f"volta do limite ({len(lev['pontos'])} de {n0} pontos)")


def area_poligono(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                   for i in range(len(pts)))) / 2


def declarado(decl, chave):
    """A fact a person stated in terreno.json ({"valor", "estado", "metodo", "fonte", "nota"}), or None."""
    d = decl.get("metadados", {}).get(chave)
    if not d:
        return None
    return campo(d.get("valor"), d["estado"], d.get("metodo", "utilizador"), unidade=d.get("unidade", ""),
                 tipo="terreno", fonte=d.get("fonte"), nota=d.get("nota", ""))


def metadados(decl, levs, sup_stats):
    """The terrain fields of the Phase 1 contract (schema 'terreno'), each with its provenance."""
    f0 = decl["superficies"][0]["fontes"][0]
    lev0 = levs[0][0]
    src = fonte(f0["ficheiro"], f0.get("folha"), f0.get("local", ""))
    out = {}
    out["fonte"] = declarado(decl, "fonte") or campo(
        f"{lev0['formato']}: {f0['ficheiro']}" + (f", folha {f0['folha']}" if f0.get("folha") else ""),
        CONFIRMED, "texto", tipo="terreno", fonte=src)
    g = lev0.get("georef")
    xs = [p[0] for lev, _ in levs for p in lev["pontos"]]
    ys = [p[1] for lev, _ in levs for p in lev["pontos"]]
    texto_crs, plaus = georef.sistema_provavel(xs, ys)
    if lev0.get("crs", {}).get("epsg"):
        auto = campo(f"EPSG:{lev0['crs']['epsg']}", CONFIRMED, "texto", tipo="referencial", fonte=src,
                     nota="declarado no próprio ficheiro")
    elif g and plaus:
        auto = campo("PT-TM06/ETRS89 (EPSG:3763), provável", INFERRED, "inferencia", tipo="referencial", fonte=src,
                     nota=f"quadrícula M/P lida na folha ({g['n_cruzes']} cruzes, resíduo {_n(g['residuo_max_m'], 3)} m, "
                          f"escala 1:{round(g['escala_x'])}); {texto_crs}. O desenho não escreve o sistema.")
    elif g:
        auto = campo(None, MISSING, "nenhum", tipo="referencial", nota=texto_crs)
    else:
        auto = em_falta("referencial", "sem coordenadas no ficheiro: terreno em coordenadas locais (aproximado)")
    out["crs"] = declarado(decl, "crs") or auto
    zs = [p[2] for lev, _ in levs for p in lev["pontos"]]
    out["datum_vertical"] = declarado(decl, "datum_vertical") or (
        campo("altitudes ortométricas (Marégrafo de Cascais), provável", INFERRED, "inferencia", tipo="terreno",
              nota=f"cotas entre {_n(min(zs))} e {_n(max(zs))} m, coerentes com altitudes em Portugal continental; "
                   "o desenho não escreve o datum") if plaus and zs else em_falta("terreno", "o ficheiro não diz o datum"))
    uh = lev0.get("unidade")
    if g:
        out["unidade_horizontal"] = campo("m", CONFIRMED, "texto", unidade="m", tipo="terreno", fonte=src,
                                          nota="rótulos da quadrícula em metros ('…mM', '…mP') e escala verificada")
    elif uh:
        out["unidade_horizontal"] = campo(uh, CONFIRMED, "texto", unidade=uh, tipo="terreno", fonte=src)
    else:
        out["unidade_horizontal"] = declarado(decl, "unidade_horizontal") or em_falta("terreno", "o ficheiro não diz a unidade")
    out["unidade_vertical"] = declarado(decl, "unidade_vertical") or (
        campo("m", INFERRED, "inferencia", unidade="m", tipo="terreno", fonte=src,
              nota="cotas com 2 casas decimais e a gama de altitudes da região") if zs else em_falta("terreno"))
    lims = [l for lev, _ in levs for l in lev["limites"]]
    if lims:
        L = max(lims, key=area_poligono)
        per = sum(math.dist(L[i], L[(i + 1) % len(L)]) for i in range(len(L)))
        out["limite_lote"] = campo({"area_m2": round(area_poligono(L)), "perimetro_m": round(per),
                                    "vertices": len(L), "coordenadas": "só no PC (terreno_local.json)"},
                                   INFERRED, "geometria", tipo="terreno", fonte=src,
                                   nota="linha tracejada «LIMITE DO TERRENO» reconstruída a partir dos traços")
    else:
        out["limite_lote"] = declarado(decl, "limite_lote") or em_falta("terreno", "sem limite do lote no ficheiro")
    out["data_levantamento"] = declarado(decl, "data_levantamento") or em_falta(
        "terreno", "o desenho não diz a data do levantamento (a data da folha é a do desenho de arquitetura)")
    out["precisao"] = declarado(decl, "precisao") or em_falta(
        "terreno", "precisão não declarada pelo topógrafo; ver a coerência medida no relatório")
    ctrl = [c for lev, _ in levs for c in (lev.get("georef") or {}).get("controlos", [])]
    out["pontos_controlo"] = declarado(decl, "pontos_controlo") or em_falta(
        "terreno", "o desenho não mostra marcos nem estações do levantamento com coordenadas e cota")
    return out, ctrl


def avaliar(meta, stats, decl):
    """(gate, reasons). FAIL: unusable. NEEDS_HUMAN_REVIEW: something a person must look at. WARNING: usable as an
    approximate terrain (spec §19.4: missing CRS/datum -> marked approximate)."""
    falhas, rever, avisos = [], [], []
    for s in stats:
        if s.get("erro"):
            falhas.append(f"{s['id']}: {s['erro']}")
            continue
        cv = s.get("validacao_cruzada", {})
        if cv.get("rmse", 0) > decl.get("limites", {}).get("rmse_max_m", 3.0):
            falhas.append(f"{s['id']}: os pontos não concordam entre si (RMSE {cv['rmse']} m)")
        if s.get("pontos_afastados"):
            rever.append(f"{s['id']}: {len(s['pontos_afastados'])} pontos discordam dos vizinhos e das curvas "
                         "(afastados da superfície até alguém ver o desenho)")
        if s.get("duplicados_com_cotas_diferentes"):
            rever.append(f"{s['id']}: {len(s['duplicados_com_cotas_diferentes'])} pontos repetidos com cotas diferentes")
        if s.get("curvas", {}).get("rotulos_em_conflito"):
            rever.append(f"{s['id']}: rótulos de curvas em conflito")
        if s.get("malha", {}).get("faces_para_baixo"):
            falhas.append(f"{s['id']}: faces do terreno viradas para baixo")
        if s.get("pontos_a_rever"):
            avisos.append(f"{s['id']}: {len(s['pontos_a_rever'])} pontos discordam de uma das verificações (mantidos)")
    for k in ("unidade_horizontal", "unidade_vertical"):
        if meta[k]["estado"] == MISSING:
            falhas.append(f"{k} desconhecida")
    for k in ("crs", "datum_vertical"):
        if meta[k]["estado"] != CONFIRMED:
            avisos.append(f"{k}: {meta[k]['estado']} — terreno aproximado (posição relativa medida; georreferência por "
                          "confirmar com o topógrafo)")
    for k in ("data_levantamento", "precisao", "pontos_controlo"):
        if meta[k]["estado"] == MISSING:
            avisos.append(f"{k}: em falta")
    if any(meta[k]["estado"] == REVIEW for k in meta):
        rever.append("há metadados a rever")
    if falhas:
        return "FAIL", falhas + rever + avisos
    if rever:
        return "NEEDS_HUMAN_REVIEW", rever + avisos
    if avisos:
        return "WARNING", avisos
    return "PASS", []


def main():
    comum.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("declaracao")
    ap.add_argument("--blender")
    a = ap.parse_args()
    dpath = Path(a.declaracao).resolve()
    decl = comum.ler_json(dpath)
    obra = decl["obra"]
    local = BOB / "_trabalho" / "step-inside" / obra / "terreno"
    local.mkdir(parents=True, exist_ok=True)

    # 1. read
    sups = []
    for S in decl["superficies"]:
        levs = [(ler_fonte(decl, f), f) for f in S["fontes"]]
        sups.append((S, levs))
    todos = [p for _S, levs in sups for lev, _ in levs for p in lev["pontos"]]
    if not todos:
        raise SystemExit("nenhum ponto lido")
    # 2. local origin (10 m grid) — kept only on this PC
    ox = round(st.fmean(p[0] for p in todos), -1)
    oy = round(st.fmean(p[1] for p in todos), -1)
    run = {"blend": str(local / "terreno.blend"), "saida": str(local / "tin.json"), "superficies": []}
    pontos_folha = {}
    for S, levs in sups:
        pts, curvas, rot, lim, pf = [], [], [], None, []
        for lev, _f in levs:
            pts += [[p[0] - ox, p[1] - oy, p[2]] for p in lev["pontos"]]
            pf += lev.get("pontos_folha", [None] * len(lev["pontos"]))
            for l in lev["linhas"]:
                if l["tipo"] == "linha2d":
                    curvas.append({"pts": [[q[0] - ox, q[1] - oy] for q in l["pts"]], "papel": l.get("papel", "curva")})
            rot += [[r[0] - ox, r[1] - oy, r[2]] for r in lev["rotulos"] if _f.get("rotulos_curvas")]
            if lev["limites"] and lim is None:
                lim = [[q[0] - ox, q[1] - oy] for q in max(lev["limites"], key=area_poligono)]
        pontos_folha[S["id"]] = pf
        sup = {"id": S["id"], "nome": S["nome"], "pontos": pts, "curvas": curvas, "rotulos_curvas": rot,
               "limite": lim, "excluir": S.get("excluir_pontos", []), "equidistancia": S.get("equidistancia", {})}
        # 3D breaklines / contours with heights from DXF or LandXML: their vertices are survey points
        for lev, _f in levs:
            for l in lev["linhas"]:
                if l["tipo"] in ("curva", "quebra"):
                    sup["pontos"] += [[q[0] - ox, q[1] - oy, q[2]] for q in l["pts"] if q[2] is not None]
                    pf += [None] * sum(1 for q in l["pts"] if q[2] is not None)
        run["superficies"].append(sup)
    comum.escrever_json(local / "terreno_local.json", {
        "_doc": "LOCAL ONLY (git-ignored): site origin and survey data in real coordinates.",
        "origem": {"x": ox, "y": oy, "crs": "como o levantamento"},
        "superficies": [{"id": S["id"], "pontos_abs": [p for lev, _ in levs for p in lev["pontos"]],
                         "limites_abs": [l for lev, _ in levs for l in lev["limites"]],
                         "georef": [lev.get("georef") for lev, _ in levs]} for S, levs in sups]})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump(run, fh)
        run_path = fh.name
    from ferramentas.comum import correr_blender
    code, out = correr_blender(AQUI / "blender_tin.py", [run_path], factory=True, blender=a.blender)
    Path(run_path).unlink(missing_ok=True)
    if code or "TIN_OK" not in out:
        print(out[-3000:])
        raise SystemExit("Blender (blender_tin.py) falhou")
    stats = json.loads((local / "tin.json").read_text(encoding="utf-8"))["superficies"]
    for s in stats:  # where a person should look: the sheet position and text of each flagged point
        pf = pontos_folha.get(s["id"], [])
        for chave in ("pontos_afastados", "pontos_a_rever", "picos_confirmados_pelas_curvas"):
            for item in s.get(chave, []):
                loc = pf[item["indice"]] if item["indice"] < len(pf) else None
                if loc:
                    item["folha_mm"] = loc[:2]
                    item["texto"] = loc[2]

    meta, controlos = metadados(decl, sups[0][1], stats)
    gate, motivos = avaliar(meta, stats, decl)
    leitura = []
    for S, levs in sups:
        for lev, f in levs:
            leitura.append({"superficie": S["id"], "ficheiro": lev["ficheiro"], "formato": lev["formato"],
                            "folha": f.get("folha"), "contagens": lev["contagens"], "avisos": lev["avisos"],
                            "georef": {k: v for k, v in (lev.get("georef") or {}).items() if k in (
                                "residuo_max_m", "escala_x", "escala_y", "rotacao_graus", "n_cruzes")} or None})
    resumo = {"obra": obra, "resultado": gate, "motivos": motivos, "terreno": meta, "leitura": leitura,
              "controlo_xy_implantacao": [{"folha_mm": c["folha_mm"], "erro_m": c["erro_m"]} for c in controlos],
              "superficies": stats,
              "origem_local": "guardada só no PC (_trabalho/step-inside/<obra>/terreno/terreno_local.json)"}
    saida = dpath.parent
    comum.escrever_json(saida / "terreno_resumo.json", resumo)
    (saida / "terreno_relatorio.md").write_text(relatorio_md(resumo, decl), encoding="utf-8")
    print(f"{gate}: " + "; ".join(motivos[:4]))
    print(f"relatório: {saida / 'terreno_relatorio.md'}")
    print(f"modelo local: {local / 'terreno.blend'}")
    sys.exit({"PASS": 0, "WARNING": 0, "NEEDS_HUMAN_REVIEW": 2, "FAIL": 1}[gate])


def _n(v, casas=2):
    return "—" if v is None else (f"{v:.{casas}f}".replace(".", ",") if isinstance(v, float) else str(v))


def relatorio_md(r, decl):
    L = [f"# Terreno · {decl.get('nome', r['obra'])}", "",
         f"**Resultado: {r['resultado']}**", ""]
    L += [f"- {m}" for m in r["motivos"]] + [""]
    L += ["Gerado por `step-inside/ferramentas/terreno/terreno.py` a partir de `terreno.json`. Só números e estados: "
          "as coordenadas reais e a origem local ficam só no PC (o levantamento localiza o terreno do cliente).", ""]
    L += ["## Campos do terreno (contrato da Fase 1)", "", "| Campo | Valor | Estado | Método | Nota |", "|---|---|---|---|---|"]
    for k in CAMPOS_TERRENO:
        c = r["terreno"][k]
        v = c["valor"]
        if isinstance(v, dict):
            v = ", ".join(f"{a} {_n(b, 0)}" for a, b in v.items())
        L.append(f"| {k} | {_n(v)} | {c['estado']} | {c['metodo']} | {c.get('nota', '')} |")
    L += ["", "## Leitura das fontes", ""]
    for l in r["leitura"]:
        g = l["georef"]
        L.append(f"- **{l['ficheiro']}**" + (f", folha {l['folha']}" if l["folha"] else "") + f" ({l['formato']}): "
                 + ", ".join(f"{k} {v}" for k, v in l["contagens"].items()))
        if g:
            L.append(f"  - georreferência pela quadrícula: {g['n_cruzes']} cruzes, resíduo máximo {_n(g['residuo_max_m'], 3)} m, "
                     f"escala 1:{_n(g['escala_x'], 1)} × 1:{_n(g['escala_y'], 1)}, rotação {_n(g['rotacao_graus'], 3)}°")
        for av in l["avisos"]:
            L.append(f"  - aviso: {av}")
    if r["controlo_xy_implantacao"]:
        e = [c["erro_m"] for c in r["controlo_xy_implantacao"]]
        L.append(f"- pontos com coordenadas escritas na folha (controlo da leitura): {len(e)}, erro máximo {_n(max(e), 3)} m")
    for s in r["superficies"]:
        L += ["", f"## Superfície «{s['nome']}»", ""]
        if s.get("erro"):
            L.append(f"Erro: {s['erro']}")
            continue
        m, cv, cu = s["malha"], s["validacao_cruzada"], s.get("curvas", {})
        L += [f"- {s['pontos']} pontos cotados ({s.get('excluidos_por_decisao', 0)} excluídos por decisão), "
              f"{cu.get('linhas', 0)} curvas de nível 2D: {cu.get('com_cota_por_rotulo', 0)} com cota pelo rótulo, "
              f"{cu.get('com_cota_pelo_tin', 0)} pelo terreno dos pontos, {cu.get('retiradas_por_incoerencia', 0)} retiradas "
              f"por incoerência, {cu.get('com_cota_final', 0)} usadas.",
              f"- Equidistância: curvas mestras {_n(cu.get('equidistancia_mestras'))} m (rótulos), curvas "
              f"{_n(cu.get('equidistancia'))} m (razão de comprimentos {_n(cu.get('razao_comprimentos_intermedias_mestras'))}).",
              f"- Malha: {m['vertices']} vértices, {m['triangulos']} triângulos, {_n(m['area_planta_m2'], 0)} m² em planta, "
              f"{_n(m['extensao_m'][0], 0)} × {_n(m['extensao_m'][1], 0)} m, cotas {_n(m['z_min'])} a {_n(m['z_max'])} m, "
              f"inclinação mediana {_n(m['inclinacao_graus_p50'], 1)}° (p95 {_n(m['inclinacao_graus_p95'], 1)}°). "
              f"Faces viradas para baixo: {m['faces_para_baixo']}.",
              "", "| Verificação | n | média | mediana |abs| | p95 |abs| | máx |abs| |", "|---|---|---|---|---|---|"]
        for nome, k in (("Cada ponto previsto pelos vizinhos (validação cruzada, 5 grupos)", "validacao_cruzada"),
                        ("Pontos contra as curvas de nível (duas fontes independentes)", "curvas_vs_pontos")):
            e = s.get(k) or {}
            if e:
                L.append(f"| {nome} | {e['n']} | {_n(e['media'])} | {_n(e['p50'])} | {_n(e['p95'])} | {_n(e['max'])} |")
        for chave, titulo in (("pontos_afastados", "Pontos afastados (discordam dos vizinhos e das curvas: ver o desenho)"),
                              ("pontos_a_rever", "Pontos mantidos que discordam de uma verificação"),
                              ("picos_confirmados_pelas_curvas", "Picos confirmados pelas curvas (terreno real)")):
            if s.get(chave):
                L += ["", f"**{titulo}:**", "", "| Texto | Folha (mm) | Cota | Vizinhos dão | Diferença das curvas | Declive |", "|---|---|---|---|---|---|"]
                for it in s[chave]:
                    L.append(f"| {it.get('texto', it['indice'])} | {it.get('folha_mm', '—')} | {_n(it['z'])} | "
                             f"{_n(it.get('previsto_vizinhos'))} | {_n(it.get('dif_curvas'))} | {_n(it.get('declive_pct'))} % |")
    L += ["", "## Como ler", "",
          "- **PASS**: medido e georreferenciado com o sistema confirmado. **WARNING**: utilizável como terreno "
          "aproximado (falta confirmar o sistema, o datum, a data ou os pontos de controlo). **NEEDS_HUMAN_REVIEW**: "
          "há pontos ou rótulos que uma pessoa tem de ver no desenho. **FAIL**: não serve.",
          "- Uma imagem, foto ou PDF sem escala nunca dá um terreno medido (especificação §19.4).", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
