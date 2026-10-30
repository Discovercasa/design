"""2D geometry helpers shared by the model tools. Pure Python (also imported inside Blender).

Polygons are lists of (x, y) tuples. Convex polygons are enough for everything the tools build
(timber members, sheets, boards, lining strips).
"""
import math


def area2(p):
    return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))


def area(p):
    return abs(area2(p)) / 2 if len(p) >= 3 else 0.0


def clean(poly, tol=0.001):
    """Drop repeated points, close duplicates and orient counter-clockwise."""
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) > tol or abs(p[1] - out[-1][1]) > tol:
            out.append((p[0], p[1]))
    if len(out) > 2 and abs(out[0][0] - out[-1][0]) <= tol and abs(out[0][1] - out[-1][1]) <= tol:
        out.pop()
    if len(out) >= 3 and area2(out) < 0:
        out.reverse()
    return out


def clip(poly, axis, val, keep_greater):
    """Clip a convex polygon by the axis-aligned half-plane p[axis] >= val (or <= val)."""
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ina = a[axis] >= val if keep_greater else a[axis] <= val
        inb = b[axis] >= val if keep_greater else b[axis] <= val
        if ina:
            out.append(a)
        if ina != inb:
            t = (val - a[axis]) / (b[axis] - a[axis])
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out


def clip_box(poly, u0=None, u1=None, v0=None, v1=None):
    for axis, val, kg in ((0, u0, True), (0, u1, False), (1, v0, True), (1, v1, False)):
        if val is not None and len(poly) >= 3:
            poly = clip(poly, axis, val, kg)
    return poly


def clip_semiplano(poly, a, b, c):
    """Keep the part of a convex polygon where a*x + b*y <= c."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fp <= 1e-12:
            out.append(p)
        if (fp < -1e-12 < fq) or (fq < -1e-12 < fp):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def hull(pts):
    pts = sorted(set((round(x, 5), round(y, 5)) for x, y in pts))
    if len(pts) <= 2:
        return pts

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 1e-12:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cr(hi[-2], hi[-1], p) <= 1e-12:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def analyse(poly):
    """Bounding box, slope and perpendicular thickness of a member polygon (elevation u, v)."""
    us = [p[0] for p in poly]
    vs = [p[1] for p in poly]
    longest, sloped = 0.0, False
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ln = math.dist(a, b)
        longest = max(longest, ln)
        if ln > 0.15 and 3 < abs(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))) % 90 < 87:
            sloped = True
    return {"du": max(us) - min(us), "dv": max(vs) - min(vs), "umin": min(us), "umax": max(us),
            "vmin": min(vs), "vmax": max(vs), "sloped": sloped, "longest": longest,
            "tperp": area(poly) / longest if longest else 0}


def corte_vertical(poly, u):
    """(vmin, vmax) of a convex polygon on the vertical line x = u, or None."""
    vs = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        if (a[0] - u) * (b[0] - u) <= 0 and a[0] != b[0]:
            t = (u - a[0]) / (b[0] - a[0])
            vs.append(a[1] + t * (b[1] - a[1]))
        elif a[0] == u:
            vs.append(a[1])
    return (min(vs), max(vs)) if vs else None


def subtrair_retangulos(poly, rects, eps=1e-6):
    """Convex polygon minus axis-aligned rectangles (u0, u1, v0, v1) -> list of convex polygons.

    Vertical strip decomposition at the rectangle edges, then horizontal bands are removed per strip.
    """
    if len(poly) < 3:
        return []
    umin = min(p[0] for p in poly)
    umax = max(p[0] for p in poly)
    cuts = sorted({umin, umax} | {x for r in rects for x in r[:2] if umin + eps < x < umax - eps})
    out = []
    for a, b in zip(cuts, cuts[1:]):
        if b - a < eps:
            continue
        strip = clip_box(poly, a, b)
        if len(strip) < 3:
            continue
        mid = (a + b) / 2
        bands = sorted((r[2], r[3]) for r in rects if r[0] <= mid <= r[1])
        pieces = [strip]
        for z0, z1 in bands:
            nxt = []
            for pc in pieces:
                lo = clip_box(pc, v1=z0)
                hi = clip_box(pc, v0=z1)
                nxt += [q for q in (lo, hi) if len(q) >= 3 and area(q) > eps]
            pieces = nxt
        out += pieces
    return out


def dividir_grelha(poly, du=None, dv=None, u0=0.0, v0=0.0, desfasado=False):
    """Split a convex polygon by a sheet grid (columns du from u0, rows dv from v0).

    With `desfasado` (running bond) every other row is shifted by du / 2.
    """
    if len(poly) < 3:
        return []
    rows = [poly]
    row_idx = [0]
    if dv:
        vmin = min(p[1] for p in poly)
        vmax = max(p[1] for p in poly)
        k0 = math.floor((vmin - v0) / dv + 1e-9)
        rows, row_idx = [], []
        k = k0
        while v0 + k * dv < vmax - 1e-9:
            r = clip_box(poly, v0=v0 + k * dv, v1=v0 + (k + 1) * dv)
            if len(r) >= 3 and area(r) > 1e-8:
                rows.append(r)
                row_idx.append(k)
            k += 1
    out = []
    for r, k in zip(rows, row_idx):
        if not du:
            out.append(r)
            continue
        off = u0 + (du / 2 if desfasado and k % 2 else 0.0)
        umin = min(p[0] for p in r)
        umax = max(p[0] for p in r)
        j = math.floor((umin - off) / du + 1e-9)
        while off + j * du < umax - 1e-9:
            c = clip_box(r, off + j * du, off + (j + 1) * du)
            if len(c) >= 3 and area(c) > 1e-8:
                out.append(c)
            j += 1
    return out


def encolher(poly, d):
    """Shrink a convex polygon by d towards its centroid along x and y (visual joints between sheets)."""
    if d <= 0 or len(poly) < 3:
        return poly
    us = [p[0] for p in poly]
    vs = [p[1] for p in poly]
    if max(us) - min(us) <= 2 * d or max(vs) - min(vs) <= 2 * d:
        return poly
    return clip_box(poly, min(us) + d, max(us) - d, min(vs) + d, max(vs) - d)
