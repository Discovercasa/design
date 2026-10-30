"""Reader of DiscoverCasa's own module drawings ("Módulos Exteriores" / "Módulos Interiores" sheets, e.g. Torres
Vedras D2503). Pure Python.

    python ferramentas/modelo/modulos_dc.py "<file>.dwfx" --planta "<model>/planta_paredes.json" --saida modulos.json

Sheet layout (DiscoverCasa standard, AutoCAD, "Sem Escala" but one scale for the whole sheet): the plan in the
middle with every module drawn in section (a black rectangle: module length x wall thickness, 0,11 exterior /
0,075 interior) and labelled "M<n>" (blue); each module's elevation drawn beside the plan, aligned with it (the
same x for walls along X, the same y for walls along Y) and labelled again. In the elevations black outlines
are the 11x3.5 / 7.5x3.5 members (studs, plates, cripples, the "escadas" of noggings where another wall
meets), red hatched outlines the 11x7.5 / 7.5x11 members (corner studs, jambs, lintels, sills). Regular stud
spacing 40 cm clear, not dimensioned ("CONSIDERAÇÕES GERAIS"); irregular spacings dimensioned.

Output (world metres, plan axes of planta_paredes.json): every module with its footprint, height, the members in
its own elevation (u along the wall in +x / +y, v up from the module base) and the openings found from the red
members (jambs + lintel, + sill for windows).
"""
import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.dwfx.leitor import Dwfx  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PRETO, VERMELHO = "#000000", "#ED1F24"


def retangulos(d, folha):
    """Axis-aligned rectangles of the member colours: (cor, x0, x1, y0, y1) in sheet mm."""
    out = set()
    for p in d.paths(folha):
        if p["stroke"] not in (PRETO, VERMELHO):
            continue
        for sp, _cl in p["subs"]:
            if len(sp) not in (4, 5):
                continue
            xs = sorted({round(x, 3) for x, _y in sp})
            ys = sorted({round(y, 3) for _x, y in sp})
            if len(xs) == 2 and len(ys) == 2:
                out.add(("R" if p["stroke"] == VERMELHO else "P", xs[0], xs[1], ys[0], ys[1]))
    return sorted(out)


def rotulos(d, folha):
    """Module labels "M<n>" (the font may split "M1" and "5"): {nome: [(x, y, angle)]}."""
    gl = d.glyphs(folha)
    res = defaultdict(list)
    for x, y, ang, h, s in gl:
        if 1.9 <= h <= 3.0 and re.fullmatch(r"M\d{1,2}", s.strip()):
            res[s.strip()].append((x, y, ang))
    return res


def extrair_folha(d, folha, H, t, tipo):
    """Modules of one sheet in sheet coordinates. H: module height (m); t: wall thickness (m)."""
    rs = retangulos(d, folha)
    labs = rotulos(d, folha)
    # scale: the plates (0,035 thick) and the footprints (t thick): take the footprints, then the stud width
    fps = []
    for c, x0, x1, y0, y1 in rs:
        if c != "P":
            continue
        w, h = x1 - x0, y1 - y0
        fps.append((min(w, h), (c, x0, x1, y0, y1)))
    # the sheet scale from the most common thin dimension of black members (0,035 m) and the thickness t
    finos = sorted(round(a, 2) for a, _r in fps if a < 3.0)
    moda = max(set(finos), key=finos.count)
    s = moda / 0.035
    tol = 0.25 * s * 0.035
    # refine: pairs of plates of the same module (same extent) are H apart, outer to outer
    pl = [r for a, r in fps if abs(a - 0.035 * s) < tol]
    seps = []
    for i, (_c, a0, a1, b0, b1) in enumerate(pl):
        for _c2, c0, c1, d0, d1 in pl[i + 1:]:
            if a1 - a0 > b1 - b0 and abs(a0 - c0) < 0.5 and abs(a1 - c1) < 0.5:
                sep = max(b1, d1) - min(b0, d0)
            elif a1 - a0 < b1 - b0 and abs(b0 - d0) < 0.5 and abs(b1 - d1) < 0.5:
                sep = max(a1, c1) - min(a0, c0)
            else:
                continue
            if abs(sep - H * s) < 0.03 * H * s:
                seps.append(sep)
    if seps:  # the most common separation (other plate pairs line up by chance)
        rr = [round(x, 2) for x in seps]
        s = max(set(rr), key=rr.count) / H
        tol = 0.25 * s * 0.035
    pegadas = [r for a, r in fps if abs(a - t * s) < tol and max(r[2] - r[1], r[4] - r[3]) > 0.2 * s]
    mods = []
    for r in pegadas:
        _c, x0, x1, y0, y1 = r
        eixo = "x" if x1 - x0 > y1 - y0 else "y"
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        # nearest label (plan label beside the module)
        best = None
        for nome, pos in labs.items():
            for lx, ly, _a in pos:
                if eixo == "x" and x0 - 1 <= lx <= x1 + 1:
                    dd = abs(ly - cy)
                elif eixo == "y" and y0 - 1 <= ly <= y1 + 1:
                    dd = abs(lx - cx)
                else:
                    continue
                if dd < 0.9 * s and (best is None or dd < best[0]):
                    best = (dd, nome)
        if best is None:
            continue
        mods.append({"nome": best[1], "eixo": eixo, "pegada": [x0, x1, y0, y1]})
    # elevations: plates of (about) the module length starting where the footprint starts; the elevation frame is
    # the side of a plate with the members in it (the drawing's elevation may differ a little from the plan)
    def dentro(r, ext, fr, eixo):
        _c, a0, a1, b0, b1 = r
        if eixo == "x":
            return ext[0] - 0.01 * s <= a0 and a1 <= ext[1] + 0.01 * s and fr[0] - 0.01 * s <= b0 and b1 <= fr[1] + 0.01 * s
        return ext[0] - 0.01 * s <= b0 and b1 <= ext[1] + 0.01 * s and fr[0] - 0.01 * s <= a0 and a1 <= fr[1] + 0.01 * s

    for m in mods:
        x0, x1, y0, y1 = m["pegada"]
        L = (x1 - x0) if m["eixo"] == "x" else (y1 - y0)
        cand = None
        for r in rs:
            c, a0, a1, b0, b1 = r
            if c != "P":
                continue
            if m["eixo"] == "x":
                if not (abs(b1 - b0 - 0.035 * s) < tol and abs(a0 - x0) < 0.02 * s and abs((a1 - a0) - L) < 0.06 * L):
                    continue
                ext, (p0, p1) = (a0, a1), (b0, b1)
            else:  # the south end (world) is the larger sheet y
                if not (abs(a1 - a0 - 0.035 * s) < tol and abs(b1 - y1) < 0.02 * s and abs((b1 - b0) - L) < 0.06 * L):
                    continue
                ext, (p0, p1) = (b0, b1), (a0, a1)
            for fr in ((p0, p0 + H * s), (p1 - H * s, p1)):
                if fr[0] - 0.01 * s < ((y0 + y1) / 2 if m["eixo"] == "x" else (x0 + x1) / 2) < fr[1] + 0.01 * s:
                    continue  # that side holds the plan, not the elevation
                # count elevation members only (long pieces; the plan shows studs as small squares)
                n = sum(1 for q in rs if dentro(q, ext, fr, m["eixo"]) and max(q[2] - q[1], q[4] - q[3]) > 0.2 * s)
                if n > 2 and (cand is None or n > cand[0]):
                    cand = (n, ext, fr)
        if cand is None:
            m["erro"] = "sem alçado"
            continue
        _n, ext, (e0, e1) = cand
        m["alcado"] = [e0, e1]
        m["comprimento"] = round(L / s, 4)
        m["comprimento_alcado"] = round((ext[1] - ext[0]) / s, 4)
        membros = []
        for r in rs:
            if not dentro(r, ext, (e0, e1), m["eixo"]):
                continue
            c, a0, a1, b0, b1 = r
            if m["eixo"] == "x":
                u0, u1, w0, w1 = (a0 - ext[0]) / s, (a1 - ext[0]) / s, (b0 - e0) / s, (b1 - e0) / s
            else:  # along y: +y world = up the sheet, u from the south end
                u0, u1, w0, w1 = (ext[1] - b1) / s, (ext[1] - b0) / s, (a0 - e0) / s, (a1 - e0) / s
            membros.append([c, round(u0, 4), round(u1, 4), round(w0, 4), round(w1, 4)])
        m["_membros_w"] = membros
    # which side of each elevation is the base: the plate line cut by doors, else the window sills (a window
    # sits nearer the base); modules in one strip share the side
    for m in mods:
        if "alcado" not in m:
            continue
        ms = m["_membros_w"]
        Hm = H
        # plates on each edge: the base plate is cut at doors (less plate length) — strong evidence
        L0 = sum(r[2] - r[1] for r in ms if r[0] == "P" and r[3] < 0.06 and r[4] < 0.1 and r[2] - r[1] > r[4] - r[3])
        L1 = sum(r[2] - r[1] for r in ms if r[0] == "P" and r[4] > Hm - 0.06 and r[3] > Hm - 0.1 and r[2] - r[1] > r[4] - r[3])
        voto = 0
        if abs(L0 - L1) > 0.2:
            voto = 3 if L0 < L1 else -3
        else:
            hor = [r for r in ms if r[0] == "R" and r[2] - r[1] > r[4] - r[3]]
            if len(hor) >= 2:
                mid = sum((r[3] + r[4]) / 2 for r in hor) / len(hor)
                voto = 1 if mid < Hm / 2 else -1
        m["_voto"] = voto
    faixas = defaultdict(list)
    for m in mods:
        if "alcado" in m:
            faixas[(m["eixo"], round((m["alcado"][0] + m["alcado"][1]) / 2, 0))].append(m)
    for _k, grupo in faixas.items():
        v = sum(m["_voto"] for m in grupo)
        for m in grupo:
            base0 = v >= 0 if m["eixo"] == "y" else v > 0
            if m["eixo"] == "x" and v == 0:
                base0 = False  # upright elevations: the base at the bottom of the sheet (larger y = w max)
            m["membros"] = [[c, u0, u1, round(w0, 4), round(w1, 4)] if base0 else
                            [c, u0, u1, round(Hm - w1, 4), round(Hm - w0, 4)]
                            for c, u0, u1, w0, w1 in m["_membros_w"]]
            m.pop("_membros_w")
            m.pop("_voto")
    return mods, s


def classificar(m, H, tipo, t):
    """Member types and sections; openings from the red members (jambs, lintel, sill)."""
    sec_p = "110x35" if tipo == "exterior" else "75x35"
    sec_r = "110x75" if tipo == "exterior" else "110x75"
    out = []
    for c, u0, u1, v0, v1 in m["membros"]:
        horiz = u1 - u0 > v1 - v0
        if c == "P":
            if horiz and (v0 < 0.01 or v1 > H - 0.01):
                k = "Travessa inferior" if v0 < 0.01 else "Travessa superior"
            elif horiz:
                k = "Travessa (escada)"
            elif v1 - v0 > H - 0.1:
                k = "Montante"
            else:
                k = "Montante curto"
            out.append({"tipo": k, "seccao": sec_p, "u": [u0, u1], "v": [v0, v1]})
        else:
            if horiz:
                k = "Padieira / peitoril"
            elif u0 < 0.01 or u1 > m["comprimento"] - 0.01:
                k = "Montante de canto"
            else:
                k = "Ombreira"
            out.append({"tipo": k, "seccao": sec_r, "u": [u0, u1], "v": [v0, v1]})
    # openings: between two red uprights, under a red horizontal, above a red horizontal (window) or the base
    reds_v = sorted([x for x in out if x["seccao"] == sec_r and x["tipo"] != "Padieira / peitoril"], key=lambda x: x["u"][0])
    reds_h = [x for x in out if x["tipo"] == "Padieira / peitoril"]
    aberturas = []
    for a, b in zip(reds_v, reds_v[1:]):
        uL, uR = a["u"][1], b["u"][0]
        if uR - uL < 0.3:
            continue
        hs = sorted([h for h in reds_h if h["u"][0] <= uL + 0.02 and h["u"][1] >= uR - 0.02], key=lambda h: h["v"][0])
        if not hs:
            continue
        top = hs[-1]
        sills = [h for h in hs if h is not top]
        base_cortada = not any(x["tipo"] == "Travessa inferior" and x["u"][0] < (uL + uR) / 2 < x["u"][1] for x in out)
        if sills:
            v0, kind = sills[-1]["v"][1], "janela"
        elif base_cortada:
            v0, kind = 0.0, "porta"
        else:
            continue
        v1 = top["v"][0]
        aberturas.append({"u": [round(uL, 4), round(uR, 4)], "v": [round(v0, 4), round(v1, 4)], "tipo": kind})
        for h in hs:
            h["tipo"] = "Padieira" if h is top else "Peitoril"
    for x in out:
        if x["tipo"] == "Padieira / peitoril":
            x["tipo"] = "Travessa 11x7,5"
    return out, aberturas


def mundo(mods, s, t, planta, tipo):
    """Sheet -> world: fit the translation that puts the footprints on the walls of planta_paredes.json (the
    exterior ones on the outer outline, the interior ones on the centre lines)."""
    ws = [w for w in planta["paredes"] if w["exterior"] == (tipo == "exterior")]
    # candidate offsets from every footprint / wall pair along each axis; keep the most voted
    votos_x, votos_y = defaultdict(int), defaultdict(int)
    for m in mods:
        x0, x1, y0, y1 = m["pegada"]
        for w in ws:
            if w["eixo"] != m["eixo"]:
                continue
            if tipo == "exterior":
                c_out = w["c"] + w["lado_exterior"] * w["espessura"] / 2
                c_in = c_out - w["lado_exterior"] * t
                lo, hi = sorted((c_out, c_in))
            else:
                lo, hi = w["c"] - t / 2, w["c"] + t / 2
            if m["eixo"] == "x":
                votos_y[round(lo + y1 / s, 2)] += 1   # world y = oy - sheet y / s
            else:
                votos_x[round(lo - x0 / s, 2)] += 1   # world x = ox + sheet x / s
    ox = max(votos_x, key=votos_x.get) if votos_x else 0.0
    oy = max(votos_y, key=votos_y.get) if votos_y else 0.0
    for m in mods:
        x0, x1, y0, y1 = m["pegada"]
        m["mundo"] = [round(ox + x0 / s, 4), round(ox + x1 / s, 4), round(oy - y1 / s, 4), round(oy - y0 / s, 4)]
    return ox, oy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dwfx")
    ap.add_argument("--planta", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--folha_ext", type=int, default=2)
    ap.add_argument("--folha_int", type=int, default=1)
    ap.add_argument("--H_ext", type=float, default=3.50)
    ap.add_argument("--H_int", type=float, default=2.53)
    a = ap.parse_args()
    d = Dwfx(a.dwfx)
    planta = json.load(open(a.planta, encoding="utf-8"))
    res = {"origem": Path(a.dwfx).name, "modulos": []}
    for folha, tipo, H, t in ((a.folha_ext, "exterior", a.H_ext, 0.11), (a.folha_int, "interior", a.H_int, 0.075)):
        mods, s = extrair_folha(d, folha, H, t, tipo)
        ox, oy = mundo(mods, s, t, planta, tipo)
        print(f"folha {folha} ({tipo}): {len(mods)} módulos, escala {s:.3f} mm/m, origem ({ox:.3f}, {oy:.3f})")
        for m in sorted(mods, key=lambda m: int(m["nome"][1:])):
            if "membros" not in m:
                print("  ", m["nome"], m.get("erro"))
                continue
            membros, ab = classificar(m, H, tipo, t)
            res["modulos"].append({"nome": m["nome"], "id": f"{'E' if tipo == 'exterior' else 'I'}-{m['nome']}",
                                   "tipo": tipo, "eixo": m["eixo"], "pegada": m["mundo"], "altura": H,
                                   "espessura": t, "comprimento": m["comprimento"], "membros": membros,
                                   "aberturas": ab})
            print(f"   {m['nome']:4s} {m['eixo']} L {m['comprimento']:.3f}  x {m['mundo'][0]:.3f}-{m['mundo'][1]:.3f}"
                  f"  y {m['mundo'][2]:.3f}-{m['mundo'][3]:.3f}  peças {len(membros):3d}  vãos "
                  + ", ".join(f"{o['tipo']} {o['u'][1] - o['u'][0]:.2f}x{o['v'][1] - o['v'][0]:.2f}@{o['v'][0]:.2f}" for o in ab))
    Path(a.saida).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("->", a.saida)


if __name__ == "__main__":
    main()
