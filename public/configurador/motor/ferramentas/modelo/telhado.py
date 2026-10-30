"""Exposed roofs of a plan house (cobertura à vista, sandwich panel): the roof surface, its faces and its lines.
Pure Python (standard library) — the builder uses it, and the configurator runs the same code in the browser.

    python ferramentas/modelo/telhado.py "<house>.json" [--svg out.svg]      (a configured house: prints the faces)

The method (conhecimento/metodo-construtivo.md §7; user 2026-10-21): always sandwich panel; a rectangle gets 2 águas
with empenas as the rule ("por regra geral definir o de 2 águas"), 4 águas as an option; L / T / U houses "várias
águas"; one slope for the whole roof (at least 15 % — "A inclinação mínima da cobertura à vista é 15 %"), eaves
overhang 0,25 by default. Our reading
for L / T / U (to confirm): the main body (the biggest rectangle of the outline) and the wings around it, each with
its own roof (2 águas with empenas, or hipped) at the one slope and eaves height; each wing runs into the body it
meets up to that body's ridge, so its end hides under it and the two meet in larós (valleys). "misto" (várias águas
with empenas — user 2026-10-27 "Quero também com duas águas e depois várias águas"; our reading, to confirm): the
main body hipped, the wings' ends in empenas. The roof surface is the
upper envelope of those roofs; its faces are convex plan polygons, each on one plane z = z0 + gx x + gy y (the top of
the purlins = the underside of the panels), z = 0 on the eaves line (the walls' outer faces) — the caller adds the
height.

Coordinates: metres, X east, Y north, the outline counter-clockwise, right angles only (as para_construtor.py).
"""
import argparse
import json
import math
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
EPS = 1e-9


# ============================================================================ the outline in rectangles
def _dentro(cont, x, y):
    ins = False
    n = len(cont)
    for i in range(n):
        (xi, yi), (xj, yj) = cont[i], cont[i - 1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            ins = not ins
    return ins


def decompor(cont):
    """The main body (the biggest rectangle inside the outline) and the wings: [{"x0", "x1", "y0", "y1", "pai" (index
    of the rectangle it meets, None for the main body), "lado" (its side on the parent: "O"/"E"/"S"/"N")}]."""
    xs, ys = sorted({p[0] for p in cont}), sorted({p[1] for p in cont})
    nx, ny = len(xs) - 1, len(ys) - 1
    cel = [[_dentro(cont, (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2) for j in range(ny)] for i in range(nx)]
    cheio = lambda i0, i1, j0, j1: all(cel[i][j] for i in range(i0, i1) for j in range(j0, j1))  # noqa: E731
    cands = [(i0, i1, j0, j1) for i0 in range(nx) for i1 in range(i0 + 1, nx + 1)
             for j0 in range(ny) for j1 in range(j0 + 1, ny + 1) if cheio(i0, i1, j0, j1)]
    area = lambda r: (xs[r[1]] - xs[r[0]]) * (ys[r[3]] - ys[r[2]])  # noqa: E731
    menor = lambda r: min(xs[r[1]] - xs[r[0]], ys[r[3]] - ys[r[2]])  # noqa: E731
    usados = [[False] * ny for _ in range(nx)]
    rets = []

    def tomar(r, pai, lado):
        for i in range(r[0], r[1]):
            for j in range(r[2], r[3]):
                usados[i][j] = True
        rets.append({"x0": xs[r[0]], "x1": xs[r[1]], "y0": ys[r[2]], "y1": ys[r[3]], "pai": pai, "lado": lado, "_r": r})

    tomar(max(cands, key=lambda r: (round(area(r), 6), round(menor(r), 6))), None, None)
    while True:  # the biggest free rectangle touching one already placed, until the outline is covered
        livres = [r for r in cands if all(not usados[i][j] for i in range(r[0], r[1]) for j in range(r[2], r[3]))]
        melhor = None
        for r in sorted(livres, key=lambda r: -area(r)):
            for k, q in enumerate(rets):
                a, b = q["_r"], r
                lado = None
                if b[1] == a[0] and min(a[3], b[3]) > max(a[2], b[2]):
                    lado = "O"
                elif b[0] == a[1] and min(a[3], b[3]) > max(a[2], b[2]):
                    lado = "E"
                elif b[3] == a[2] and min(a[1], b[1]) > max(a[0], b[0]):
                    lado = "S"
                elif b[2] == a[3] and min(a[1], b[1]) > max(a[0], b[0]):
                    lado = "N"
                if lado:
                    melhor = (r, k, lado)
                    break
            if melhor:
                break
        if not melhor:
            break
        tomar(*melhor)
    if any(cel[i][j] and not usados[i][j] for i in range(nx) for j in range(ny)):
        raise ValueError("forma não suportada pela cobertura à vista")
    for r in rets:
        del r["_r"]
    return rets


# ============================================================================ the roofs of the rectangles
def telhados(cont, tipo, beirado=0.25, empena=0.12):
    """Each rectangle's roof: {"x0".."y1" (its footprint: a wing with the part run into its parent), "eixo" ("x"/"y":
    the ridge), "planos": [(a, b, c, nome)] with z = t·(a x + b y + c) (t = tan of the slope), "dominios" (convex
    boxes where the roof is: its own part with the overhangs on its outline sides, the part inside the parent without
    any), "lados" {side: "beirado" | "empena" | "rincao" | "dentro"}, "zonas" (boxes where its ceiling beams are, down
    its slopes: its own part, plus where it crosses its parent — that part taken off the parent's)}."""
    rets = decompor(cont)
    m = rets[0]
    W, D = m["x1"] - m["x0"], m["y1"] - m["y0"]
    eixo0 = "x" if W >= D else "y"
    # a squarish main body with gables: its ridge along the edges the wings meet, so they join in larós, not against
    # a gable. Hipped (4 águas) the surface is the same either way and the ridge only sets the beams: they stay across
    # the short side (an L 9 x 8 got 9 m glulams and a header where the wing opens instead of 22x7,5 over 8 m)
    if tipo == "duas_aguas" and max(W, D) / min(W, D) < 1.6:
        horiz = sum(min(r["x1"], m["x1"]) - max(r["x0"], m["x0"]) for r in rets[1:] if r["pai"] == 0 and r["lado"] in ("S", "N"))
        vert = sum(min(r["y1"], m["y1"]) - max(r["y0"], m["y0"]) for r in rets[1:] if r["pai"] == 0 and r["lado"] in ("O", "E"))
        if abs(horiz - vert) > EPS:  # its slopes in larós (an L's usual roof), not its gable
            eixo0 = "x" if horiz > vert else "y"
    def tipo_de(k):  # each rectangle's own roof: "misto" hips the main body only
        return "quatro_aguas" if tipo == "quatro_aguas" or (tipo == "misto" and k == 0) else "duas_aguas"
    ov_de = {"beirado": beirado, "rincao": beirado, "empena": empena, "dentro": 0.0}
    out = []

    def menos_caixa(zs, c):
        """Boxes minus a box (the parts left, split in two where it crosses the middle)."""
        res = []
        for z in zs:
            if min(z[1], c[1]) - max(z[0], c[0]) <= EPS or min(z[3], c[3]) - max(z[2], c[2]) <= EPS:
                res.append(z)
                continue
            for q in ([z[0], c[0], z[2], z[3]], [c[1], z[1], z[2], z[3]],
                      [max(z[0], c[0]), min(z[1], c[1]), z[2], c[2]], [max(z[0], c[0]), min(z[1], c[1]), c[3], z[3]]):
                if q[1] - q[0] > EPS and q[3] - q[2] > EPS:
                    res.append(q)
        return res

    def parar_no_cume(p, wx0, wx1, wy0, wy1):
        """A wing wider than its parent crosses it: where the parent ENDS inside the wing's span, the parent's roof
        runs into the wing as a wing into a body — up to the wing's ridge, without overhangs. Left as it was it went
        on under the wing to its own gable or hip, and stood out of the wing's slope by the wing's eaves (a "mini
        telhado" on the U's corner, user 2026-10-22); covered over its whole length it has no roof of its own."""
        px0, px1, py0, py1 = p["proprio"]
        if p["eixo"] == "x":
            fins = [s for s, ok in (("O", wx0 <= px0 + EPS), ("E", wx1 >= px1 - EPS)) if ok]
            cume = (wx0 + wx1) / 2
        else:
            fins = [s for s, ok in (("S", wy0 <= py0 + EPS), ("N", wy1 >= py1 - EPS)) if ok]
            cume = (wy0 + wy1) / 2
        if not fins:
            return  # the wing crosses the middle of the parent: they meet in larós on both sides (a T)
        p["planos"] = [pl for pl in p["planos"] if pl[3] not in fins]
        for s in fins:
            p["lados"][s] = "dentro"
        if len(fins) == 2:
            p["dominios"] = []
            return
        box = list(p["dominios"][0])
        s = fins[0]
        if s == "O":
            box[0], ext = wx1, [cume, wx1, py0, py1]
        elif s == "E":
            box[1], ext = wx0, [wx0, cume, py0, py1]
        elif s == "S":
            box[2], ext = wy1, [px0, px1, cume, wy1]
        else:
            box[3], ext = wy0, [px0, px1, wy0, cume]
        p["dominios"] = ([box] if box[1] - box[0] > EPS and box[3] - box[2] > EPS else []) + [ext] + p["dominios"][1:]

    for k, r in enumerate(rets):
        x0, x1, y0, y1 = r["x0"], r["x1"], r["y0"], r["y1"]
        eixo = eixo0 if r["pai"] is None else ("y" if r["lado"] in ("S", "N") else "x")  # a wing's ridge runs to its body
        fim_tipo = "rincao" if tipo_de(k) == "quatro_aguas" else "empena"
        lados = {s: (fim_tipo if (s in ("O", "E")) == (eixo == "x") else "beirado") for s in ("O", "E", "S", "N")}
        F = [x0, x1, y0, y1]          # the whole footprint
        zonas = [[x0, x1, y0, y1]]    # where its ceiling beams are (its own part; a crossing of its parent too)
        proprio = dict(lados)         # the sides of its own part
        ext = None                    # the part inside the parent: (box, the far side reached or None)
        if r["pai"] is not None:
            p = out[r["pai"]]
            lado_meu = {"O": "E", "E": "O", "S": "N", "N": "S"}[r["lado"]]  # the wing's side on the parent
            proprio[lado_meu] = "dentro"
            larg = (x1 - x0) if eixo == "y" else (y1 - y0)
            par = (p["eixo"] == "x") == (r["lado"] in ("S", "N"))  # the parent's ridge along the shared edge
            idx = {"S": 3, "N": 2, "O": 1, "E": 0}[r["lado"]]   # which coordinate of F moves into the parent
            sinal = 1 if r["lado"] in ("S", "O") else -1
            longe = None
            if par:
                meio = (p["y0"] + p["y1"]) / 2 if p["eixo"] == "x" else (p["x0"] + p["x1"]) / 2
                prof = (p["y1"] - p["y0"]) if p["eixo"] == "x" else (p["x1"] - p["x0"])
                if larg <= prof + EPS:
                    F[idx] = meio                      # to the parent's ridge: hidden under it
                else:                                  # wider than the body: across it, its far side on the outline
                    F[idx] = {3: p["y1"], 2: p["y0"], 1: p["x1"], 0: p["x0"]}[idx]
                    longe = {3: "N", 2: "S", 1: "E", 0: "O"}[idx]
                    parar_no_cume(p, x0, x1, y0, y1)
                    # its roof stands over the body there: the ceiling beams below run down its slopes ("sempre
                    # inseridos no sentido da cobertura"), not the body's — they had stayed the body's, parallel to
                    # the wing's purlins, and those got no prumos (3 m bare on the user's U, 2026-10-28)
                    pp_ = p["proprio"]
                    cruz = [max(x0, pp_[0]), min(x1, pp_[1]), max(y0, pp_[2]), min(y1, pp_[3])]
                    cruz[idx] = pp_[idx]                              # the parent's far side
                    cruz[idx ^ 1] = {2: y0, 3: y1, 0: x0, 1: x1}[idx]  # to the wing's own part
                    p["zonas"] = menos_caixa(p["zonas"], cruz)
                    zonas.append(cruz)
                    # nor does the body's eave run on in front of the wing's gable on that far side (a T's stem across
                    # its bar: a strip of the bar's overhang had stood out there, on nothing — ours, 2026-10-28)
                    faixa = {"N": [x0, x1, pp_[3], pp_[3] + 5], "S": [x0, x1, pp_[2] - 5, pp_[2]],
                             "E": [pp_[1], pp_[1] + 5, y0, y1], "O": [pp_[0] - 5, pp_[0], y0, y1]}[longe]
                    p["dominios"] = menos_caixa(p["dominios"], faixa)
            elif p["tipo"] == "quatro_aguas":          # at the end of a hipped body: in by its half width
                F[idx] += sinal * larg / 2
            # (at a gable end it stops: it abuts the gable — "encosto")
            lados[lado_meu] = fim_tipo if longe else "dentro"
            caixa = [min(F[0], x0) if idx == 0 else x0, max(F[1], x1) if idx == 1 else x1,
                     min(F[2], y0) if idx == 2 else y0, max(F[3], y1) if idx == 3 else y1]
            ext_box = {0: [F[0], x0, y0, y1], 1: [x1, F[1], y0, y1], 2: [x0, x1, F[2], y0], 3: [x0, x1, y1, F[3]]}[idx]
            F = caixa
            if ext_box[1] - ext_box[0] > EPS and ext_box[3] - ext_box[2] > EPS:
                ext = (ext_box, longe, p["proprio"])
        # the planes (z/t = the distance from the eaves line): the eaves are its own long sides
        if eixo == "x":
            planos = [(0.0, 1.0, -y0, "S"), (0.0, -1.0, y1, "N")]
        else:
            planos = [(1.0, 0.0, -x0, "O"), (-1.0, 0.0, x1, "E")]
        for s, (a, b, c) in (("O", (1.0, 0.0, -F[0])), ("E", (-1.0, 0.0, F[1])), ("S", (0.0, 1.0, -F[2])), ("N", (0.0, -1.0, F[3]))):
            if lados[s] == "rincao":
                planos.append((a, b, c, s))
        dom = [[x0 - ov_de[proprio["O"]], x1 + ov_de[proprio["E"]], y0 - ov_de[proprio["S"]], y1 + ov_de[proprio["N"]]]]
        if ext:
            bx, longe, pp = ext
            bx = list(bx)
            if longe:  # its far side on the outline gets its overhang
                i = {"O": 0, "E": 1, "S": 2, "N": 3}[longe]
                bx[i] += (-1 if i in (0, 2) else 1) * ov_de[lados[longe]]
                # and a side of it where the parent ended (that side of the crossing is on the outline too)
                for i, s, v_meu, v_pai in ((0, "O", x0, pp[0]), (1, "E", x1, pp[1]), (2, "S", y0, pp[2]), (3, "N", y1, pp[3])):
                    if s not in (longe, lado_meu) and abs(v_meu - v_pai) < EPS:
                        bx[i] += (-1 if i in (0, 2) else 1) * ov_de[lados[s]]
            dom.append(bx)
        out.append({"x0": F[0], "x1": F[1], "y0": F[2], "y1": F[3], "eixo": eixo, "planos": planos, "lados": lados,
                    "dominios": dom, "tipo": tipo_de(k), "pai": r["pai"], "lado_pai": r["lado"],
                    "proprio": [x0, x1, y0, y1], "zonas": zonas})
    for r in out:  # two boxes of one roof side by side along a whole edge: one zone (its beams across both)
        zs = [list(z) for z in r["zonas"]]
        junta = True
        while junta:
            junta = False
            for i in range(len(zs)):
                for j in range(i + 1, len(zs)):
                    a, b = zs[i], zs[j]
                    if abs(a[0] - b[0]) < EPS and abs(a[1] - b[1]) < EPS and (abs(a[3] - b[2]) < EPS or abs(b[3] - a[2]) < EPS):
                        zs[i] = [a[0], a[1], min(a[2], b[2]), max(a[3], b[3])]
                    elif abs(a[2] - b[2]) < EPS and abs(a[3] - b[3]) < EPS and (abs(a[1] - b[0]) < EPS or abs(b[1] - a[0]) < EPS):
                        zs[i] = [min(a[0], b[0]), max(a[1], b[1]), a[2], a[3]]
                    else:
                        continue
                    del zs[j]
                    junta = True
                    break
                if junta:
                    break
        r["zonas"] = zs
    return out


# ============================================================================ convex polygon clipping
def _cortar(poly, a, b, c):
    """The part of the convex polygon where a x + b y + c >= 0."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = a * p[0] + b * p[1] + c, a * q[0] + b * q[1] + c
        if fp >= -EPS:
            out.append(p)
        # a point within EPS of the line is on it (kept above): an edge crosses only from one side to the other —
        # an end just inside the tolerance made fp - fq ~ 0 and a point millions of metres away (a roof "to the sky")
        if (fp > EPS and fq < -EPS) or (fp < -EPS and fq > EPS):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return _limpar(out)


def _limpar(poly):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) > 1e-7 or abs(p[1] - out[-1][1]) > 1e-7:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-7 and abs(out[0][1] - out[-1][1]) < 1e-7:
        out.pop()
    return out if len(out) >= 3 and abs(_area(out)) > 1e-7 else []


def _area(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly))) / 2


def _subtrair(pecas, semiplanos):
    """Convex pieces minus the convex region given by its half-planes (a x + b y + c >= 0 each)."""
    out = []
    for poly in pecas:
        resto = poly
        for k, (a, b, c) in enumerate(semiplanos):
            fora = _cortar(resto, -a, -b, -c)  # the part outside this half-plane is outside the region
            if fora:
                out.append(fora)
            resto = _cortar(resto, a, b, c)
            if not resto:
                break
    return out


def _ret(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ============================================================================ the roof surface
def telhado(cont, tipo="duas_aguas", inclinacao_graus=math.degrees(math.atan(0.15)), beirado=0.25, empena=0.12):
    """The exposed roof of the outline: {"faces": [{"pts", "plano": (a, b, c), "z0", "gx", "gy", "subida", "ret",
    "nome"}], "retangulos", "t" (tan of the slope), "linhas": [{"tipo": "cumeeira" | "rincao" | "laro" | "beirado" |
    "empena" | "encosto", "p0", "p1"}], "z_max"} — z = 0 on the eaves line."""
    t = math.tan(math.radians(inclinacao_graus))
    rs = telhados(cont, tipo, beirado, empena)
    faces = []
    for k, r in enumerate(rs):
        for i, (a, b, c, nome) in enumerate(r["planos"]):
            pecas = [_ret(*d) for d in r["dominios"]]
            for j, (a2, b2, c2, _) in enumerate(r["planos"]):  # where this plane is the lowest of its roof
                if j != i:
                    pecas = [q for p in pecas for q in [_cortar(p, a2 - a, b2 - b, c2 - c)] if q]
            for k2, r2 in enumerate(rs):  # minus where another roof stands higher (an earlier one wins a tie)
                if k2 == k or not pecas:
                    continue
                tol = 1e-9 if k2 < k else -1e-9
                for X0b, X1b, Y0b, Y1b in r2["dominios"]:
                    hs = [(1.0, 0.0, -X0b), (-1.0, 0.0, X1b), (0.0, 1.0, -Y0b), (0.0, -1.0, Y1b)]
                    # a plane of the other roof identical to this one (a wing flush with the main body's eave): the
                    # earlier roof keeps the overlap — a constant half-plane (the tolerance alone is within the
                    # clipping EPS: both kept it, a duplicate piece and no eave line under it)
                    hs += [(0.0, 0.0, 1.0 if k2 < k else -1.0) if max(abs(a2 - a), abs(b2 - b), abs(c2 - c)) < 1e-9
                           else (a2 - a, b2 - b, c2 - c + tol) for a2, b2, c2, _ in r2["planos"]]
                    pecas = _subtrair(pecas, hs)
            for p in pecas:
                n = math.hypot(a, b)
                faces.append({"pts": [[round(x, 4), round(y, 4)] for x, y in p], "plano": (a, b, c),
                              "z0": round(t * c, 6), "gx": round(t * a, 6), "gy": round(t * b, 6),
                              "subida": [a / n, b / n], "ret": k, "nome": nome, "area_planta": round(_area(p), 4)})
    linhas = _linhas(faces)
    z_max = max((f["z0"] + f["gx"] * x + f["gy"] * y for f in faces for x, y in f["pts"]), default=0.0)
    return {"faces": faces, "retangulos": rs, "t": t, "linhas": linhas, "z_max": round(z_max, 4),
            "tipo": tipo, "inclinacao_graus": inclinacao_graus, "beirado": beirado, "empena": empena}


def _linhas(faces):
    """The lines of the roof from the faces' edges: an edge shared by two faces on different planes is a ridge or hip
    (both faces go down from it) or a valley (both go up); an edge on one face only is an eave (the face goes up from
    it, level), a verge (inclined) or an abutment."""
    arestas = []
    for k, f in enumerate(faces):
        p = f["pts"]
        for i in range(len(p)):
            arestas.append((k, tuple(p[i]), tuple(p[(i + 1) % len(p)])))
    z = lambda f, q: f["z0"] + f["gx"] * q[0] + f["gy"] * q[1]  # noqa: E731
    out = []
    for k, a, b in arestas:
        f = faces[k]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L < 1e-4:
            continue
        ux, uy = dx / L, dy / L
        # the other faces with an edge along this one (collinear, overlapping), on a different plane
        partes = [(0.0, L, None)]
        for k2, a2, b2 in arestas:
            if k2 == k:
                continue
            g = faces[k2]
            # collinear?
            c1 = (a2[0] - a[0]) * -uy + (a2[1] - a[1]) * ux
            c2 = (b2[0] - a[0]) * -uy + (b2[1] - a[1]) * ux
            if abs(c1) > 1e-4 or abs(c2) > 1e-4:
                continue
            s1 = (a2[0] - a[0]) * ux + (a2[1] - a[1]) * uy
            s2 = (b2[0] - a[0]) * ux + (b2[1] - a[1]) * uy
            lo, hi = max(0.0, min(s1, s2)), min(L, max(s1, s2))
            if hi - lo < 1e-4:
                continue
            novas = []
            for p0, p1, viz in partes:
                if viz is not None or hi <= p0 or lo >= p1:
                    novas.append((p0, p1, viz))
                    continue
                if lo > p0:
                    novas.append((p0, lo, None))
                novas.append((max(p0, lo), min(p1, hi), k2))
                if hi < p1:
                    novas.append((hi, p1, None))
            partes = novas
        dentro = (-uy, ux)  # the face lies to the left of its counter-clockwise edges
        sobe = f["subida"][0] * dentro[0] + f["subida"][1] * dentro[1]
        for p0, p1, viz in partes:
            if p1 - p0 < 1e-4:
                continue  # a zero-length piece between two neighbours
            q0 = (a[0] + ux * p0, a[1] + uy * p0)
            q1 = (a[0] + ux * p1, a[1] + uy * p1)
            if viz is not None:
                if viz < k:
                    continue  # once per pair
                g = faces[viz]
                if tuple(g["plano"]) == tuple(f["plano"]):
                    continue  # two pieces of one face
                sobe_g = -(g["subida"][0] * dentro[0] + g["subida"][1] * dentro[1])  # g lies on the other side
                if sobe < 0 and sobe_g < 0:
                    nivel = abs(z(f, q0) - z(f, q1)) < 1e-4
                    tipo = "cumeeira" if nivel else "rincao"
                elif sobe > 0 and sobe_g > 0:
                    tipo = "laro"
                else:
                    tipo = "encosto"
            else:
                nivel = abs(z(f, q0) - z(f, q1)) < 1e-4
                tipo = "beirado" if nivel and sobe > 0 else ("empena" if not nivel else "encosto")
            out.append({"tipo": tipo, "p0": [round(q0[0], 4), round(q0[1], 4), round(z(f, q0), 4)],
                        "p1": [round(q1[0], 4), round(q1[1], 4), round(z(f, q1), 4)], "face": k})
    return out


def svg(cont, T, caminho):
    """A plan of the roof: faces, lines and the outline."""
    xs = [p[0] for f in T["faces"] for p in f["pts"]] + [p[0] for p in cont]
    ys = [p[1] for f in T["faces"] for p in f["pts"]] + [p[1] for p in cont]
    x0, x1, y0, y1 = min(xs) - 0.5, max(xs) + 0.5, min(ys) - 0.5, max(ys) + 0.5
    k = 800 / max(x1 - x0, y1 - y0)
    P = lambda x, y: f"{(x - x0) * k:.1f},{(y1 - y) * k:.1f}"  # noqa: E731
    cores = {"S": "#c9ced4", "N": "#9aa2aa", "O": "#b4bbc2", "E": "#aab1b8"}
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{(x1 - x0) * k:.0f}" height="{(y1 - y0) * k:.0f}">']
    for f in T["faces"]:
        s.append(f'<polygon points="{" ".join(P(*p) for p in f["pts"])}" fill="{cores.get(f["nome"], "#ccc")}" stroke="#fff" stroke-width="0.5"/>')
    s.append(f'<polygon points="{" ".join(P(*p) for p in cont)}" fill="none" stroke="#6e4b31" stroke-width="3" stroke-dasharray="6 4"/>')
    cor_l = {"cumeeira": "#d0453a", "rincao": "#e2a43a", "laro": "#2e86de", "beirado": "#1d1f21", "empena": "#27ae60", "encosto": "#8e44ad"}
    for l in T["linhas"]:
        s.append(f'<line x1="{P(*l["p0"][:2]).split(",")[0]}" y1="{P(*l["p0"][:2]).split(",")[1]}" '
                 f'x2="{P(*l["p1"][:2]).split(",")[0]}" y2="{P(*l["p1"][:2]).split(",")[1]}" stroke="{cor_l[l["tipo"]]}" stroke-width="3"/>')
    s.append("</svg>")
    Path(caminho).write_text("\n".join(s), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("casa")
    ap.add_argument("--tipo", default=None)
    ap.add_argument("--svg")
    a = ap.parse_args()
    casa = json.load(open(a.casa, encoding="utf-8"))
    cob = casa.get("cobertura", {})
    tipo = a.tipo or (cob.get("tipo") if cob.get("tipo") in ("duas_aguas", "quatro_aguas", "misto") else "duas_aguas")
    graus = cob["inclinacao_graus"] if "inclinacao_graus" in cob else math.degrees(math.atan(cob.get("inclinacao_pct", 15.0) / 100))
    T = telhado(casa["base"]["contorno"], tipo, graus, cob.get("beirado", 0.25))
    for k, r in enumerate(T["retangulos"]):
        print(f"retângulo {k}: x {r['x0']:.2f}-{r['x1']:.2f} y {r['y0']:.2f}-{r['y1']:.2f} cumeeira em {r['eixo']}"
              f" pai {r['pai']} {r['lados']}")
    area = sum(f["area_planta"] for f in T["faces"])
    print(f"{len(T['faces'])} faces, {area:.2f} m² em planta, {area / math.cos(math.atan(T['t'])):.2f} m² de painel; "
          f"topo {T['z_max']:.2f} acima do beirado")
    from collections import Counter
    tot = Counter()
    for l in T["linhas"]:
        tot[l["tipo"]] += math.dist(l["p0"], l["p1"])
    print("linhas:", ", ".join(f"{k} {v:.2f} m" for k, v in sorted(tot.items())))
    if a.svg:
        svg(casa["base"]["contorno"], T, a.svg)
        print("SVG", a.svg)


if __name__ == "__main__":
    main()
