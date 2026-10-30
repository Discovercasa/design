"""Walls and openings from an architecture floor plan (DWFx). Pure Python.

    python ferramentas/modelo/planta_arquitetura.py "<plan>.dwfx" --folha 1 --regiao X0 Y0 X1 Y1 --escala 200
        [--cor "#FF0000"] [--saida walls.json] [--svg plan.svg]

Architecture plans for licensing draw the walls to build as two parallel face lines (Portuguese convention:
red = to build). A wall = two parallel face lines 0.08-0.40 m apart that overlap; where one face is interrupted
by a wall meeting it (T-junction) the other face carries on; an OPENING = both faces interrupted between two
jamb lines that cross the wall. Windows are recognised by glazing lines (blue) inside the opening, doors by
the swing (magenta) beside it.
Output (metres, model axes: X to the right of the sheet, Y up the sheet, origin = bottom-left corner of the
walls' bounding box): {"paredes": [{id, eixo "x"|"y", s0, s1, c (centre line), espessura, exterior,
aberturas: [{s0, s1, tipo}]}], "contorno": [x0, x1, y0, y1], ...}.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.dwfx.leitor import Dwfx  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOL = 0.006          # m: points on the same face line
ESP = (0.08, 0.40)   # m: wall thickness range
VAO_MAX = 3.6        # m: widest opening (wider ones: set by hand in the config)


def segmentos(paths, regiao, cor, k):
    """Axis-parallel stroke segments of colour `cor` inside the region, in metres (y up)."""
    x0, y0, x1, y1 = regiao
    out = []
    for p in paths:
        if (p.get("stroke") or "").upper() != cor.upper():
            continue
        for sp, _cl in p["subs"]:
            for (ax, ay), (bx, by) in zip(sp, sp[1:]):
                if not all(x0 <= x <= x1 and y0 <= y <= y1 for x, y in ((ax, ay), (bx, by))):
                    continue
                a, b = (ax * k, -ay * k), (bx * k, -by * k)
                if abs(a[1] - b[1]) < TOL and abs(a[0] - b[0]) > TOL:
                    out.append(("h", (a[1] + b[1]) / 2, min(a[0], b[0]), max(a[0], b[0])))
                elif abs(a[0] - b[0]) < TOL and abs(a[1] - b[1]) > TOL:
                    out.append(("v", (a[0] + b[0]) / 2, min(a[1], b[1]), max(a[1], b[1])))
    return out


def unir(iv, gap=TOL):
    iv = sorted(iv)
    out = []
    for a, b in iv:
        if out and a <= out[-1][1] + gap:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def linhas(segs, o):
    """Face lines of orientation o: {coordinate: merged intervals}."""
    por = {}
    for oo, c, a, b in segs:
        if oo != o:
            continue
        chave = next((cc for cc in por if abs(cc - c) < TOL), c)
        por.setdefault(chave, []).append((a, b))
    return {c: unir(iv) for c, iv in por.items()}


def cobre(iv, a, b, tol=0.01):
    return any(x <= a + tol and y >= b - tol for x, y in iv)


def intersecao(A, B):
    out = []
    for a0, a1 in A:
        for b0, b1 in B:
            lo, hi = max(a0, b0), min(a1, b1)
            if hi - lo > 0.05:
                out.append([lo, hi])
    return out


def percorrer(o, ca, cb, A, B, jamba, jambas, passo=0.01):
    """Walk along a pair of face lines in 1 cm steps: 2 = both faces drawn (solid wall), 1 = one face only
    (T-junction, or a window whose frame is drawn on one face), 0 = none; runs are also split at the jamb
    lines that cross the wall. A run of 0/1 between two jambs is an OPENING; a short run of 1 is a junction or
    a corner piece; anything else ends the wall. Walks both ways from every solid run."""
    lo = min(a for a, _b in A + B)
    hi = max(b for _a, b in A + B)
    n = int(round((hi - lo) / passo))
    cortes = {int(round((j - lo) / passo)) for j in jambas if lo < j < hi}
    runs = []
    for i in range(n):
        s = lo + (i + 0.5) * passo
        e = any(a <= s <= b for a, b in A) + any(a <= s <= b for a, b in B)
        if runs and runs[-1][0] == e and i not in cortes:
            runs[-1][2] = lo + (i + 1) * passo
        else:
            runs.append([e, lo + i * passo, lo + (i + 1) * passo])

    def segue_parede(j, d):
        """After an opening (run j) the wall must go on: a solid run, or a corner piece ending the pair."""
        j += d
        while 0 <= j < len(runs):
            e, a, b = runs[j]
            if e == 2:
                return True
            if e == 1 and b - a <= 0.5:  # pier between two openings, or the corner piece at the end
                if not (0 <= j + d < len(runs)):
                    return True
                j += d
                continue
            if 0.3 <= b - a <= VAO_MAX and jamba(a) and jamba(b):  # the next opening of a row
                j += d
                continue
            return False
        return False

    def passo_ok(j, d):
        e, a, b = runs[j]
        if e == 2:
            return "parede"
        if 0.3 <= b - a <= VAO_MAX and jamba(a) and jamba(b) and segue_parede(j, d):
            return "vao"
        if e == 1 and b - a <= 0.5:
            return "parede"
        return None

    out, vistos = [], set()
    for i, r in enumerate(runs):
        if r[0] != 2 or i in vistos:
            continue
        s0, s1, abert = r[1], r[2], []
        j = i + 1
        while j < len(runs):
            k = passo_ok(j, 1)
            if not k:
                break
            if k == "vao":
                abert.append((runs[j][1], runs[j][2]))
            vistos.add(j)
            s1 = runs[j][2]
            j += 1
        j = i - 1
        while j >= 0:
            k = passo_ok(j, -1)
            if not k:
                break
            if k == "vao":
                abert.append((runs[j][1], runs[j][2]))
            s0 = runs[j][1]
            j -= 1
        abert.sort()
        while abert and abs(abert[-1][1] - s1) < 1e-6:  # never end on an opening
            s1 = abert.pop()[0]
        while abert and abs(abert[0][0] - s0) < 1e-6:
            s0 = abert.pop(0)[1]
        if s1 - s0 >= 0.15:
            out.append({"eixo": "x" if o == "h" else "y", "s0": s0, "s1": s1, "c0": ca, "c1": cb,
                        "aberturas": [{"s0": a, "s1": b} for a, b in abert]})
    return out


def paredes(segs):
    """Walls from pairs of parallel face lines. Returns list of dict (eixo, s0, s1, c0, c1, aberturas)."""
    cand = []
    for o, perp in (("h", "v"), ("v", "h")):
        L = linhas(segs, o)
        P = linhas(segs, perp)  # jamb candidates
        cs = sorted(L)
        for i, ca in enumerate(cs):
            for cb in cs[i + 1:]:
                t = cb - ca
                if not (ESP[0] <= t <= ESP[1]):
                    continue
                ov = intersecao(L[ca], L[cb])
                if sum(b - a for a, b in ov) < 0.2:
                    continue

                def jamba(s, ca=ca, cb=cb):
                    return any(abs(c - s) < 0.02 and cobre(iv, ca, cb, 0.02) for c, iv in P.items())

                jambas = [c for c, iv in P.items() if cobre(iv, ca, cb, 0.02)]
                cand += percorrer(o, ca, cb, L[ca], L[cb], jamba, jambas)
    # thinnest first; a candidate mostly inside an accepted wall is a false pairing of faces
    cand.sort(key=lambda w: w["c1"] - w["c0"])
    res = []

    def caixa(w):
        return (w["s0"], w["s1"], w["c0"], w["c1"]) if w["eixo"] == "x" else (w["c0"], w["c1"], w["s0"], w["s1"])

    for w in cand:
        x0, x1, y0, y1 = caixa(w)
        area = (x1 - x0) * (y1 - y0)
        sob = 0.0
        for r in res:
            a0, a1, b0, b1 = caixa(r)
            sob += max(0.0, min(x1, a1) - max(x0, a0)) * max(0.0, min(y1, b1) - max(y0, b0))
        if sob < 0.3 * area:
            res.append(w)
    return res


def classificar(ws, paths, regiao, k):
    """Door when a swing (magenta) lies beside the opening, otherwise window / glazed opening."""
    folha = segmentos_livres(paths, regiao, "#FF00FF", k)
    for w in ws:
        for op in w["aberturas"]:
            larg = op["s1"] - op["s0"]
            if w["eixo"] == "x":
                bx = (op["s0"] - 0.05, op["s1"] + 0.05, w["c0"] - larg - 0.1, w["c1"] + larg + 0.1)
            else:
                bx = (w["c0"] - larg - 0.1, w["c1"] + larg + 0.1, op["s0"] - 0.05, op["s1"] + 0.05)
            n = sum(1 for x, y in folha if bx[0] <= x <= bx[1] and bx[2] <= y <= bx[3])
            op["tipo"] = "porta" if n >= 3 else "janela"


def segmentos_livres(paths, regiao, cor, k):
    """All points of the paths of colour `cor` (stroke) inside the region, in metres (y up)."""
    x0, y0, x1, y1 = regiao
    pts = []
    for p in paths:
        if (p.get("stroke") or "").upper() != cor.upper():
            continue
        for sp, _cl in p["subs"]:
            pts += [(x * k, -y * k) for x, y in sp if x0 <= x <= x1 and y0 <= y <= y1]
    return pts


def ler_planta(paths, regiao, escala, cor="#FF0000", origem=None):
    """The walls document (see the module docstring) from one sheet's paths; None when no wall is found."""
    k = escala / 1000.0
    segs = segmentos(paths, regiao, cor, k)
    ws = paredes(segs)
    if not ws:
        return None
    classificar(ws, paths, regiao, k)
    xs = [v for w in ws for v in ((w["s0"], w["s1"]) if w["eixo"] == "x" else (w["c0"], w["c1"]))]
    ys = [v for w in ws for v in ((w["c0"], w["c1"]) if w["eixo"] == "x" else (w["s0"], w["s1"]))]
    ox, oy = min(xs), min(ys)
    L, D = max(xs) - ox, max(ys) - oy
    def rect(w):
        return (w["s0"], w["s1"], w["c0"], w["c1"]) if w["eixo"] == "x" else (w["c0"], w["c1"], w["s0"], w["s1"])

    def lado_fora(w):
        """+1 / -1 when the face on that side looks outside (a ray across it meets no other wall), else 0."""
        for sg in (-1, 1):
            livres = 0
            for f in (0.2, 0.35, 0.5, 0.65, 0.8):
                sm = w["s0"] + f * (w["s1"] - w["s0"])
                if any(o["s0"] <= sm <= o["s1"] for o in w["aberturas"]):
                    continue
                cf = (w["c1"] + 0.03) if sg > 0 else (w["c0"] - 0.03)
                bate = False
                for r in ws:
                    if r is w:
                        continue
                    x0, x1, y0, y1 = rect(r)
                    if w["eixo"] == "x":  # ray along y from (sm, cf)
                        bate |= x0 <= sm <= x1 and ((y1 >= cf) if sg > 0 else (y0 <= cf)) and                             ((y0 >= cf - 0.01) if sg > 0 else (y1 <= cf + 0.01))
                    else:
                        bate |= y0 <= sm <= y1 and ((x1 >= cf) if sg > 0 else (x0 <= cf)) and                             ((x0 >= cf - 0.01) if sg > 0 else (x1 <= cf + 0.01))
                livres += not bate
            if livres >= 2:
                return sg
        return 0

    for w in ws:
        w["fora"] = lado_fora(w)
    exteriores = [w for w in ws if w["fora"]]
    for w in ws:  # interior walls stop at the inner face of the exterior wall they run into
        if w in exteriores:
            continue
        for e in exteriores:
            if e["eixo"] == w["eixo"] or not (e["s0"] - 0.01 <= w["c0"] and w["c1"] <= e["s1"] + 0.01):
                continue
            if e["c0"] < w["s1"] < e["c1"] + 0.01 and w["s0"] < e["c0"]:
                w["s1"] = e["c0"]
            if e["c0"] - 0.01 < w["s0"] < e["c1"] and w["s1"] > e["c1"]:
                w["s0"] = e["c1"]
    out = []
    for i, w in enumerate(sorted(ws, key=lambda w: (w["eixo"], round(w["c0"], 2), w["s0"])), 1):
        dc, ds = (oy, ox) if w["eixo"] == "x" else (ox, oy)
        c0, c1 = w["c0"] - dc, w["c1"] - dc
        ext = bool(w["fora"])
        out.append({"id": f"P{i:02d}", "eixo": w["eixo"], "s0": round(w["s0"] - ds, 3), "s1": round(w["s1"] - ds, 3),
                    "c": round((c0 + c1) / 2, 3), "espessura": round(c1 - c0, 3), "exterior": ext,
                    "lado_exterior": w["fora"],
                    "aberturas": [{"s0": round(o["s0"] - ds, 3), "s1": round(o["s1"] - ds, 3), "tipo": o["tipo"]}
                                  for o in w["aberturas"]]})
    return {"origem_desenho": dict(origem or {}, regiao=list(regiao), escala=escala, origem_m=[round(ox, 3), round(oy, 3)]),
            "contorno": [0.0, round(L, 3), 0.0, round(D, 3)], "paredes": out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dwfx")
    ap.add_argument("--folha", type=int, default=1)
    ap.add_argument("--regiao", type=float, nargs=4, required=True, help="sheet mm X0 Y0 X1 Y1")
    ap.add_argument("--escala", type=float, required=True, help="1:N")
    ap.add_argument("--cor", default="#FF0000")
    ap.add_argument("--saida")
    ap.add_argument("--svg")
    a = ap.parse_args()
    doc = ler_planta(Dwfx(a.dwfx).paths(a.folha), a.regiao, a.escala, a.cor,
                     {"dwfx": Path(a.dwfx).name, "folha": a.folha})
    if doc is None:
        raise SystemExit("nenhuma parede encontrada na região")
    out = doc["paredes"]
    L, D = doc["contorno"][1], doc["contorno"][3]
    for w in out:
        ab = ", ".join(f"{o['tipo']} {o['s1'] - o['s0']:.2f}@{o['s0']:.2f}" for o in w["aberturas"])
        print(f"{w['id']} {w['eixo']} c={w['c']:.3f} t={w['espessura']:.3f} {w['s0']:.3f}-{w['s1']:.3f}"
              f"{' ext' if w['exterior'] else ''}  {ab}")
    print(f"{len(out)} paredes, contorno {L:.3f} x {D:.3f} m")
    if a.saida:
        Path(a.saida).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.svg:
        s = 50.0
        H = D * s + 40
        el = []
        for w in out:
            if w["eixo"] == "x":
                x, y, ww, hh = w["s0"], w["c"] - w["espessura"] / 2, w["s1"] - w["s0"], w["espessura"]
            else:
                x, y, ww, hh = w["c"] - w["espessura"] / 2, w["s0"], w["espessura"], w["s1"] - w["s0"]
            cor = "#c0392b" if w["exterior"] else "#e67e22"
            el.append(f'<rect x="{20 + x * s:.1f}" y="{H - 20 - (y + hh) * s:.1f}" width="{ww * s:.1f}" '
                      f'height="{hh * s:.1f}" fill="{cor}" opacity="0.85"/>')
            for o in w["aberturas"]:
                cor_o = "#2e86de" if o["tipo"] == "janela" else "#27ae60"
                if w["eixo"] == "x":
                    r = (o["s0"], y, o["s1"] - o["s0"], hh)
                else:
                    r = (x, o["s0"], ww, o["s1"] - o["s0"])
                el.append(f'<rect x="{20 + r[0] * s:.1f}" y="{H - 20 - (r[1] + r[3]) * s:.1f}" width="{r[2] * s:.1f}" '
                          f'height="{r[3] * s:.1f}" fill="{cor_o}"/>')
            cx = (w["s0"] + w["s1"]) / 2 if w["eixo"] == "x" else w["c"]
            cy = w["c"] if w["eixo"] == "x" else (w["s0"] + w["s1"]) / 2
            el.append(f'<text x="{20 + cx * s:.1f}" y="{H - 20 - cy * s - 4:.1f}" font-size="11" '
                      f'font-family="sans-serif" text-anchor="middle">{w["id"]}</text>')
        Path(a.svg).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{L * s + 40:.0f}" height="{H:.0f}" '
                               f'style="background:#fff">{"".join(el)}</svg>', encoding="utf-8")


if __name__ == "__main__":
    main()
