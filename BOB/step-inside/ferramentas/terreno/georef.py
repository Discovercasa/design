"""Georeferencing of a drawing sheet and plausibility checks of coordinates (Step Inside Phase 2, hub task 60).

A Portuguese survey sheet usually carries a coordinate grid: small crosses every 100 mm with the labels
"-10050mM" (M = meridiana, the X / easting) and "-20050mP" (P = perpendicular, the Y / northing).
grelha_dwfx() finds those crosses and labels and fits sheet millimetres -> (M, P) metres by least squares.
The residuals and the scale it gives are reported: they are the check that the grid was read right.

Nothing here says WHICH coordinate system the grid is in: M/P is the Portuguese notation used by both
PT-TM06/ETRS89 (EPSG:3763) and the older Hayford-Gauss systems (Datum 73, Datum Lisboa). sistema_provavel()
only says what the numbers are compatible with; the survey's CRS stays to be confirmed (INFERRED at best).
"""
import math
import re

ROTULO_M = re.compile(r"^\s*(-?\d+(?:[.,]\d+)?)\s*m\s*M\s*$")
ROTULO_P = re.compile(r"^\s*(-?\d+(?:[.,]\d+)?)\s*m\s*P\s*$")


def _num(s):
    return float(s.replace(",", "."))


def cruzes(paths, braco=(3.0, 8.0), tol=0.05):
    """Grid crosses: a horizontal and a vertical stroke of the same length range crossing at their middles.
    Returns [(x, y)] in sheet mm."""
    hs, vs = [], []
    for p in paths:
        for pts, _cl in p["subs"]:
            if len(pts) != 2:
                continue
            (x0, y0), (x1, y1) = pts
            if abs(y0 - y1) < 0.01 and braco[0] < abs(x1 - x0) < braco[1]:
                hs.append(((x0 + x1) / 2, y0))
            elif abs(x0 - x1) < 0.01 and braco[0] < abs(y1 - y0) < braco[1]:
                vs.append((x0, (y0 + y1) / 2))
    out = []
    for hx, hy in hs:
        for vx, vy in vs:
            if abs(hx - vx) < tol and abs(hy - vy) < tol:
                out.append((round(hx, 3), round(hy, 3)))
    return sorted(set(out))


def ajustar_afim(pares):
    """Least-squares affine map from sheet (x, y) to world (X, Y).
    pares: [((x, y), (X, Y))], at least 3 not collinear. Returns (coef, residuals) where
    X = a*x + b*y + c and Y = d*x + e*y + f, coef = (a, b, c, d, e, f)."""
    if len(pares) < 3:
        raise ValueError("são precisos pelo menos 3 pontos para georreferenciar")
    # normal equations of [x y 1] for each output separately (3x3, solved by Cramer's rule)
    sxx = sum(x * x for (x, _y), _ in pares)
    sxy = sum(x * y for (x, y), _ in pares)
    syy = sum(y * y for (_x, y), _ in pares)
    sx = sum(x for (x, _y), _ in pares)
    sy = sum(y for (_x, y), _ in pares)
    n = len(pares)
    M = [[sxx, sxy, sx], [sxy, syy, sy], [sx, sy, n]]

    def det3(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

    D = det3(M)
    if abs(D) < 1e-9:
        raise ValueError("pontos de georreferência alinhados: não definem um plano")
    coef = []
    for k in (0, 1):
        r = [sum(x * w[k] for (x, _y), w in pares), sum(y * w[k] for (_x, y), w in pares), sum(w[k] for _p, w in pares)]
        sol = []
        for col in range(3):
            Mc = [row[:] for row in M]
            for i in range(3):
                Mc[i][col] = r[i]
            sol.append(det3(Mc) / D)
        coef += sol
    res = [math.hypot(aplicar(coef, p)[0] - w[0], aplicar(coef, p)[1] - w[1]) for p, w in pares]
    return tuple(coef), res


def aplicar(coef, p):
    a, b, c, d, e, f = coef
    x, y = p
    return (a * x + b * y + c, d * x + e * y + f)


def escala_rotacao(coef):
    """(metres per sheet mm along x, along y, rotation of north in degrees from sheet-up, mirrored?)."""
    a, b, _c, d, e, _f = coef
    sx = math.hypot(a, d)
    sy = math.hypot(b, e)
    rot = math.degrees(math.atan2(-b, -e))  # sheet y points down; world north = -sheet y when unrotated
    espelho = (a * e - b * d) > 0  # sheet axes are left-handed (y down): a right map to world has det < 0
    return sx, sy, rot, espelho


def grelha_dwfx(linhas_texto, paths, raio=4.0):
    """Georeference one sheet from its coordinate grid.
    linhas_texto: ferramentas.dwfx.leitor.linhas(glyphs); paths: Dwfx.paths(folha).
    Returns None when there is no usable grid, else a dict:
      coef, residuo_max_m, escala (1:N), rotacao_graus, n_cruzes, pares, rotulos (implantation labels not on crosses)."""
    ms = [(l["x"], l["y"], _num(m.group(1))) for l in linhas_texto if (m := ROTULO_M.match(l["text"]))]
    ps = [(l["x"], l["y"], _num(m.group(1))) for l in linhas_texto if (m := ROTULO_P.match(l["text"]))]
    if not ms or not ps:
        return None
    pares = []
    for cx, cy in cruzes(paths):
        m = min(ms, key=lambda t: math.hypot(t[0] - cx, t[1] - cy))
        p = min(ps, key=lambda t: math.hypot(t[0] - cx, t[1] - cy))
        if math.hypot(m[0] - cx, m[1] - cy) <= raio and math.hypot(p[0] - cx, p[1] - cy) <= raio:
            pares.append(((cx, cy), (m[2], p[2])))
    if len(pares) < 3:
        return None
    coef, res = ajustar_afim(pares)
    sx, sy, rot, espelho = escala_rotacao(coef)
    return {"coef": list(coef), "residuo_max_m": round(max(res), 4), "escala_x": round(sx * 1000, 2),
            "escala_y": round(sy * 1000, 2), "rotacao_graus": round(rot, 3), "espelhado": espelho,
            "n_cruzes": len(pares), "pares": [[list(s), list(w)] for s, w in pares]}


def pontos_coordenados(linhas_texto, raio=1.5):
    """Points labelled with their own coordinates (implantation corners: '-10035,3mM' next to '-20117,1mP',
    small text). Returns [((x, y) sheet mm of the label pair, (M, P))]. Used as independent checks."""
    ms = [(l["x"], l["y"], _num(m.group(1)), l["h"]) for l in linhas_texto if (m := ROTULO_M.match(l["text"]))]
    ps = [(l["x"], l["y"], _num(m.group(1)), l["h"]) for l in linhas_texto if (m := ROTULO_P.match(l["text"]))]
    out = []
    for mx, my, mv, mh in ms:
        if mv % 50 == 0 and mh > 2:  # grid labels (round values, big text) are not implantation points
            continue
        cand = [p for p in ps if math.hypot(p[0] - mx, p[1] - my) <= raio]
        if cand:
            p = min(cand, key=lambda t: math.hypot(t[0] - mx, t[1] - my))
            out.append(((mx, my), (mv, p[2])))
    return out


# ------------------------------------------------------------------ coordinate systems
# Mainland Portugal in PT-TM06/ETRS89 (EPSG:3763) and in the Hayford-Gauss systems (central point near
# Melriça): eastings about -120 km..+170 km, northings about -300 km..+280 km. The two families overlap,
# so a coordinate alone cannot tell them apart (they differ by roughly 100-200 m).
LIMITES_PT = {"M": (-125000.0, 175000.0), "P": (-310000.0, 290000.0)}


def sistema_provavel(xs, ys):
    """What the coordinates are compatible with. Returns (texto, compativel_pt: bool)."""
    if not xs:
        return "sem coordenadas", False
    if all(abs(x) < 5000 for x in xs) and all(abs(y) < 5000 for y in ys):  # also the PT-TM06 central point: rare
        return "coordenadas locais (sem georreferência)", False
    dentro = all(LIMITES_PT["M"][0] <= x <= LIMITES_PT["M"][1] for x in xs) and \
        all(LIMITES_PT["P"][0] <= y <= LIMITES_PT["P"][1] for y in ys)
    if dentro:
        return ("compatível com Portugal continental em PT-TM06/ETRS89 (EPSG:3763) ou num sistema Hayford-Gauss "
                "antigo (Datum 73 / Datum Lisboa): confirmar com o topógrafo"), True
    return "fora de Portugal continental nos sistemas portugueses: confirmar o CRS", False
