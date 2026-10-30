"""Production documents straight from an architecture drawing (DWFx). Pure Python, runs in the browser too (Pyodide).

    python ferramentas/documentos/de_desenhos.py "<plan>.dwfx" [--candidato N] [--escolhas escolhas.json] --saida DIR

1. candidatos(): finds the floor plans on every sheet by themselves — the walls to build are red strokes (licensing
   convention, planta_arquitetura.py); each cluster of red lines is tried at 1:50 / 1:100 / 1:200 and the scale that
   gives plausible walls (0,08-0,40 m thick, a house 4-40 m long, closed outside walls) wins. The sheets of these
   drawings carry their texts as lines, so the scale is not read from the title block: it is deduced.
2. planta_para_casa(): the walls found -> a configured house (the configurator's format, para_construtor.py): the
   outline of the outside faces, its sides in 3 m walls, the openings with the DiscoverCasa defaults (heights of
   conhecimento/perguntas-por-obra.md), the interior walls with their doors.
3. gerar(): the same chain as a configured house — para_construtor.converter -> casa_planta.py -> camadas.py ->
   gerar.py: Módulos, Cobertura, Listagem de material (PDF + CSV). How it is built is always the DiscoverCasa method;
   what the drawing does not say comes from the choices (roof, clear height, exterior finish) or their defaults.
"""
import argparse
import io
import json
import runpy
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.configurador.para_construtor import converter  # noqa: E402
from ferramentas.dwfx.leitor import Dwfx  # noqa: E402
from ferramentas.modelo.planta_arquitetura import ler_planta  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
VERMELHO = "#FF0000"
ESCALAS = (50, 100, 200)
JUNTAR_MM = 6.0      # red lines closer than this on the sheet belong to the same drawing
MIN_SEGMENTOS = 16   # fewer red lines than this: not a floor plan
# what the plan does not say (DiscoverCasa defaults, perguntas-por-obra.md: windows 1,20 high at 1,00, doors 2,20)
ESCOLHAS = {"cobertura": "escondida", "pe_direito": 2.5, "exterior": "A", "obra": "", "projeto": "", "local": ""}
JANELA_ALTURA, JANELA_PEITORIL, PORTA_ALTURA = 1.2, 1.0, 2.2
PORTA_LARGA = 1.6    # an opening at least this wide drawn as a door: a sliding glass door to the floor


# ============================================================================ 1. find the floor plans
def _segmentos_folha(paths):
    """Red axis-parallel strokes of a sheet: [(x0, y0, x1, y1)] in sheet mm."""
    out = []
    for p in paths:
        if (p.get("stroke") or "").upper() != VERMELHO:
            continue
        for sp, _cl in p["subs"]:
            for (ax, ay), (bx, by) in zip(sp, sp[1:]):
                if abs(ax - bx) < 0.05 or abs(ay - by) < 0.05:
                    out.append((min(ax, bx), min(ay, by), max(ax, bx), max(ay, by)))
    return out


def _grupos(segs):
    """Clusters of red strokes (boxes closer than JUNTAR_MM), biggest first: [(x0, y0, x1, y1, n)]."""
    caixas = [[s[0], s[1], s[2], s[3], 1] for s in segs]
    junta = True
    while junta:
        junta = False
        caixas.sort()
        res = []
        for c in caixas:
            for r in res:
                if c[0] <= r[2] + JUNTAR_MM and r[0] <= c[2] + JUNTAR_MM and c[1] <= r[3] + JUNTAR_MM and r[1] <= c[3] + JUNTAR_MM:
                    r[0], r[1], r[2], r[3], r[4] = min(r[0], c[0]), min(r[1], c[1]), max(r[2], c[2]), max(r[3], c[3]), r[4] + c[4]
                    junta = True
                    break
            else:
                res.append(c)
        caixas = res
    return sorted((tuple(c) for c in caixas if c[4] >= MIN_SEGMENTOS), key=lambda c: -c[4])


def _nota(doc):
    """How plausible a walls document is as a house plan (higher is better; 0 = not a house)."""
    if not doc:
        return 0.0
    ps = doc["paredes"]
    ext = [p for p in ps if p["exterior"]]
    L, D = doc["contorno"][1], doc["contorno"][3]
    if len(ext) < 4 or not (4.0 <= max(L, D) <= 40.0) or min(L, D) < 3.0:
        return 0.0
    tipicas = sum(0.18 <= p["espessura"] <= 0.40 for p in ext) / len(ext)  # outside walls of a licensing plan
    return len(ps) * (0.3 + tipicas) + sum(len(p["aberturas"]) for p in ps)


def candidatos(caminho):
    """The floor plans found in the drawing, best first: [{folha, nome, regiao, escala, nota, planta}]."""
    d = Dwfx(caminho)
    info = {i["folha"]: i for i in d.info()}
    out = []
    for folha in range(1, len(d.pages) + 1):
        paths = d.paths(folha)
        for x0, y0, x1, y1, _n in _grupos(_segmentos_folha(paths)):
            regiao = (x0 - 1, y0 - 1, x1 + 1, y1 + 1)
            melhor = None
            for esc in ESCALAS:
                try:
                    doc = ler_planta(paths, regiao, esc, VERMELHO, {"dwfx": Path(caminho).name, "folha": folha})
                except (ValueError, ZeroDivisionError, KeyError, IndexError):
                    continue
                n = _nota(doc)
                if n and (melhor is None or n > melhor["nota"]):
                    melhor = {"folha": folha, "nome": info.get(folha, {}).get("nome", ""), "regiao": [round(v, 1) for v in regiao],
                              "escala": esc, "nota": round(n, 1), "planta": doc}
            if melhor:
                out.append(melhor)
    return sorted(out, key=lambda c: -c["nota"])


def svg_planta(doc, largura=520):
    """A small SVG of the walls found (outside red, inside orange, windows blue, doors green) for the check."""
    L, D = doc["contorno"][1], doc["contorno"][3]
    s = (largura - 20) / max(L, D, 1)
    W, H = L * s + 20, D * s + 20
    el = []
    for w in doc["paredes"]:
        t = w["espessura"]
        r = (w["s0"], w["c"] - t / 2, w["s1"] - w["s0"], t) if w["eixo"] == "x" else (w["c"] - t / 2, w["s0"], t, w["s1"] - w["s0"])
        el.append(_ret(r, s, H, "#c0392b" if w["exterior"] else "#e67e22"))
        for o in w["aberturas"]:
            ro = (o["s0"], r[1], o["s1"] - o["s0"], r[3]) if w["eixo"] == "x" else (r[0], o["s0"], r[2], o["s1"] - o["s0"])
            el.append(_ret(ro, s, H, "#2e86de" if o["tipo"] == "janela" else "#27ae60"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">'
            + "".join(el) + "</svg>")


def _ret(r, s, H, cor):
    return (f'<rect x="{10 + r[0] * s:.1f}" y="{H - 10 - (r[1] + r[3]) * s:.1f}" width="{max(r[2] * s, 1):.1f}" '
            f'height="{max(r[3] * s, 1):.1f}" fill="{cor}"/>')


# ============================================================================ 2. walls -> configured house
def _face_fora(w):
    """(axis, line) of an outside wall's outer face."""
    return w["c"] + w["lado_exterior"] * w["espessura"] / 2


def contorno_exterior(paredes):
    """The outline of the outside faces, counter-clockwise, right angles: the union of the grid cells that lie inside
    the outside faces (a ray from the cell's centre crosses them an odd number of times), traced around."""
    ext = [w for w in paredes if w["exterior"] and w["lado_exterior"]]
    hs = [(_face_fora(w), w["s0"] - w["espessura"], w["s1"] + w["espessura"]) for w in ext if w["eixo"] == "x"]
    vs = [(_face_fora(w), w["s0"] - w["espessura"], w["s1"] + w["espessura"]) for w in ext if w["eixo"] == "y"]
    xs = sorted({round(v[0], 3) for v in vs})
    ys = sorted({round(h[0], 3) for h in hs})
    if len(xs) < 2 or len(ys) < 2:
        raise ValueError("não encontrei as faces exteriores da casa")

    def dentro(x, y):
        return sum(1 for c, a, b in vs if c > x and a <= y <= b) % 2 == 1 and \
            sum(1 for c, a, b in hs if c > y and a <= x <= b) % 2 == 1

    cel = {(i, j) for i in range(len(xs) - 1) for j in range(len(ys) - 1)
           if dentro((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2)}
    if not cel:
        raise ValueError("não consegui fechar o contorno da casa")
    # boundary edges with the inside on the left (counter-clockwise), then chained
    arestas = {}
    for i, j in cel:
        for (a, b), viz in ((((i, j), (i + 1, j)), (i, j - 1)), (((i + 1, j), (i + 1, j + 1)), (i + 1, j)),
                            (((i + 1, j + 1), (i, j + 1)), (i, j + 1)), (((i, j + 1), (i, j)), (i - 1, j))):
            if viz not in cel:
                arestas[a] = b
    ini = min(arestas)
    pts, p = [ini], arestas[ini]
    while p != ini:
        pts.append(p)
        p = arestas[p]
        if len(pts) > 4 * len(arestas):
            raise ValueError("contorno da casa com mais de um corpo")
    # drop collinear points
    res = []
    for k, q in enumerate(pts):
        a, c = pts[k - 1], pts[(k + 1) % len(pts)]
        if not ((a[0] == q[0] == c[0]) or (a[1] == q[1] == c[1])):
            res.append([xs[q[0]], ys[q[1]]])
    return res


def planta_para_casa(doc, escolhas=None):
    """The walls document -> a configured house ("discovercasa-configurador/1")."""
    E = dict(ESCOLHAS, **(escolhas or {}))
    cont = contorno_exterior(doc["paredes"])
    ox, oy = min(p[0] for p in cont), min(p[1] for p in cont)
    cont = [[round(x - ox, 3), round(y - oy, 3)] for x, y in cont]
    n = len(cont)
    lados = []
    for i in range(n):
        (x0, y0), (x1, y1) = cont[i], cont[(i + 1) % n]
        eixo = "x" if abs(y1 - y0) < 1e-6 else "y"
        lados.append({"i": i, "eixo": eixo, "c": y0 if eixo == "x" else x0, "a": x0 if eixo == "x" else y0,
                      "b": x1 if eixo == "x" else y1})
    paredes_ext = []
    for l in lados:
        comp = abs(l["b"] - l["a"])
        s = 0.0
        while comp - s > 1e-6:
            paredes_ext.append({"lado": l["i"], "s0": round(s, 3), "s1": round(min(s + 3.0, comp), 3)})
            s += 3.0
    vaos, avisos = [], []
    for w in doc["paredes"]:
        if not w["exterior"] or not w["lado_exterior"]:
            continue
        linha = _face_fora(w) - (oy if w["eixo"] == "x" else ox)
        d0 = ox if w["eixo"] == "x" else oy
        for o in w["aberturas"]:
            m = (o["s0"] + o["s1"]) / 2 - d0
            lado = next((l for l in lados if l["eixo"] == w["eixo"] and abs(l["c"] - linha) < 0.05
                         and min(l["a"], l["b"]) - 1e-3 <= m <= max(l["a"], l["b"]) + 1e-3), None)
            if lado is None:
                avisos.append(f"vão de {o['s1'] - o['s0']:.2f} m na parede {w['id']} fora do contorno: ignorado")
                continue
            larg = round(o["s1"] - o["s0"], 3)
            centro = round(abs(m - lado["a"]), 3)
            if o["tipo"] == "porta":
                tipo = "janela_correr" if larg >= PORTA_LARGA else "porta"
                vaos.append({"lado": lado["i"], "tipo": tipo, "centro": centro, "largura": larg, "altura": PORTA_ALTURA,
                             **({"estore": True} if tipo != "porta" else {})})
            else:
                vaos.append({"lado": lado["i"], "tipo": "janela", "centro": centro, "largura": larg,
                             "altura": JANELA_ALTURA, "peitoril": JANELA_PEITORIL, "estore": True})
    interiores = []
    for w in doc["paredes"]:
        if w["exterior"]:
            continue
        if w["eixo"] == "x":
            de, ate = [w["s0"] - ox, w["c"] - oy], [w["s1"] - ox, w["c"] - oy]
        else:
            de, ate = [w["c"] - ox, w["s0"] - oy], [w["c"] - ox, w["s1"] - oy]
        portas = [{"centro": round((o["s0"] + o["s1"]) / 2 - w["s0"], 3)} for o in w["aberturas"] if o["tipo"] == "porta"]
        interiores.append({"de": [round(v, 3) for v in de], "ate": [round(v, 3) for v in ate], **({"portas": portas} if portas else {})})
    cob = {"tipo": "escondida"} if E["cobertura"] == "escondida" else {"tipo": E["cobertura"]}
    casa = {"formato": "discovercasa-configurador/1", "nome": E.get("projeto") or "Casa a partir da planta",
            "obra": E.get("obra") or "OBRA", "base": {"forma": "planta", "contorno": cont},
            "paredes_exteriores": paredes_ext, "vaos": vaos, "paredes_interiores": interiores, "cobertura": cob,
            "acabamentos": {"exterior": E["exterior"], "contra_ripado": True}, "pe_direito": float(E["pe_direito"])}
    return casa, avisos


# ============================================================================ 3. the documents
def _correr_aqui(cmd, capture_output=False, text=False, **_kw):
    """subprocess.run for the repo's own scripts, run in this interpreter (the browser has no processes)."""
    script, args = cmd[1], [str(a) for a in cmd[2:]]
    antigo, sys.argv = sys.argv, [script] + args
    buf, codigo = io.StringIO(), 0
    try:
        with redirect_stdout(buf):
            runpy.run_path(script, run_name="__main__")
    except SystemExit as e:
        codigo = e.code if isinstance(e.code, int) else (1 if e.code else 0)
        if e.code and not isinstance(e.code, int):
            buf.write(str(e.code))
    finally:
        sys.argv = antigo
    return subprocess.CompletedProcess(cmd, codigo, buf.getvalue() if capture_output else None, "")


def gerar(casa, saida, escolhas=None):
    """Writes planta_paredes.json, config.json and the documents (documentos/) to `saida`; returns (files, notes)."""
    E = dict(ESCOLHAS, **(escolhas or {}))
    S = json.load(open(RAIZ / "ferramentas" / "modelo" / "sistema_construtivo.json", encoding="utf-8"))
    planta, cfg, notas = converter(casa, S)
    cfg["documentos"] = {"obra": E.get("obra") or casa.get("obra") or "OBRA", "projeto": E.get("projeto") or casa["nome"],
                         "local": E.get("local", "")}
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "planta_paredes.json").write_text(json.dumps(planta, ensure_ascii=False), encoding="utf-8")
    (saida / "config.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    real = subprocess.run
    subprocess.run = _correr_aqui if sys.platform == "emscripten" else real
    try:
        r = subprocess.run([sys.executable, str(RAIZ / "ferramentas" / "documentos" / "gerar.py"), str(saida / "config.json"),
                            "--saida", str(saida / "documentos")], capture_output=True, text=True)
    finally:
        subprocess.run = real
    if r.returncode:
        raise RuntimeError(f"gerar.py falhou: {(r.stdout or '')[-1500:]}")
    return sorted(str(p) for p in (saida / "documentos").iterdir()), notas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("dwfx")
    ap.add_argument("--candidato", type=int, default=0, help="which plan found (0 = the best)")
    ap.add_argument("--escolhas", help="JSON with cobertura, pe_direito, exterior, obra, projeto, local")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    cs = candidatos(a.dwfx)
    if not cs:
        raise SystemExit("nenhuma planta encontrada (paredes a vermelho)")
    for k, c in enumerate(cs):
        ps = c["planta"]["paredes"]
        print(f"[{k}] folha {c['folha']} {c['nome']}  1:{c['escala']}  {c['planta']['contorno'][1]:.2f} x "
              f"{c['planta']['contorno'][3]:.2f} m  {len(ps)} paredes  nota {c['nota']}")
    esc = json.load(open(a.escolhas, encoding="utf-8")) if a.escolhas else {}
    casa, avisos = planta_para_casa(cs[a.candidato]["planta"], esc)
    Path(a.saida).mkdir(parents=True, exist_ok=True)
    (Path(a.saida) / "casa.json").write_text(json.dumps(casa, ensure_ascii=False, indent=1), encoding="utf-8")
    for t in avisos:
        print("  aviso:", t)
    fich, notas = gerar(casa, a.saida, esc)
    for t in notas:
        print("  nota:", t)
    for f in fich:
        print(" ", f)


if __name__ == "__main__":
    main()
