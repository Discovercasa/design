"""Rebuild timber members from the drawings' filled triangles, and group them into views.

AutoCAD exports every filled rectangle as two triangles sharing the diagonal. Two triangles are
merged back when they share their LONGEST edge (so adjacent studs are never fused).
Colours used in DiscoverCasa structural drawings (layers "Perfil 160x80 / 100x80"):
    #FFBF7F 160x80 in view   #DD6E00 160x80 cut
    #BFFF7F 100x80 in view   #A5DD6E 100x80 cut
"""
import math
from collections import defaultdict

TIMBER = {
    "#FFBF7F": ("160x80", "vista"),
    "#DD6E00": ("160x80", "corte"),
    "#BFFF7F": ("100x80", "vista"),
    "#A5DD6E": ("100x80", "corte"),
}


def _key(p, q=0.004):
    return (round(p[0] / q), round(p[1] / q))


def convex_hull(pts):
    pts = sorted(set(pts))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 1e-9:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 1e-9:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def build_members(paths, colours=TIMBER):
    """paths: output of Dwfx.paths(). Returns members: dict(section, kind, colour, poly, bbox) in sheet mm."""
    tris, polys = [], []
    for p in paths:
        col = p["fill"]
        if col not in colours:
            continue
        for sub, _closed in p["subs"]:
            pts = [tuple(v) for v in sub]
            if len(pts) > 1 and math.dist(pts[0], pts[-1]) < 1e-6:
                pts = pts[:-1]
            if len(pts) == 3:
                tris.append((col, pts))
            elif len(pts) >= 4:
                polys.append((col, pts))
    diag = defaultdict(list)
    for i, (col, t) in enumerate(tris):
        a, b = max(((t[k], t[(k + 1) % 3]) for k in range(3)), key=lambda e: math.dist(*e))
        diag[(col, tuple(sorted([_key(a), _key(b)])))].append(i)
    used, merged = set(), []
    for ids in diag.values():
        ids = [i for i in ids if i not in used]
        while len(ids) >= 2:
            i, j = ids.pop(), ids.pop()
            used.update((i, j))
            merged.append((tris[i][0], convex_hull(tris[i][1] + tris[j][1])))
    merged += [(col, convex_hull(t)) for i, (col, t) in enumerate(tris) if i not in used]
    merged += [(col, convex_hull(pts)) for col, pts in polys]
    out = []
    for col, poly in merged:
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        sec, kind = colours[col]
        out.append({"section": sec, "kind": kind, "colour": col, "poly": poly,
                    "bbox": (min(xs), min(ys), max(xs), max(ys))})
    return out


def in_region(members, region):
    x0, y0, x1, y1 = region
    return [m for m in members if x0 <= m["bbox"][0] and m["bbox"][2] <= x1 and y0 <= m["bbox"][1] and m["bbox"][3] <= y1]


def cluster(members, gap=0.35):
    """Group members whose bounding boxes touch (within `gap` sheet-mm). Returns list of dict(members, bbox)."""
    n = len(members)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    bb = [m["bbox"] for m in members]
    order = sorted(range(n), key=lambda i: bb[i][0])
    for ii, i in enumerate(order):
        x0, y0, x1, y1 = bb[i]
        for j in order[ii + 1:]:
            if bb[j][0] > x1 + gap:
                break
            u0, v0, u1, v1 = bb[j]
            if u0 <= x1 + gap and u1 >= x0 - gap and v0 <= y1 + gap and v1 >= y0 - gap:
                ra, rb = find(i), find(j)
                if ra != rb:
                    parent[ra] = rb
    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(members[i])
    res = []
    for g in groups.values():
        res.append({"members": g, "bbox": (min(m["bbox"][0] for m in g), min(m["bbox"][1] for m in g),
                                            max(m["bbox"][2] for m in g), max(m["bbox"][3] for m in g))})
    return res
