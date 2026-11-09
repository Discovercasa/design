"""Place a house on its site plan by fitting the model's walls to the walls drawn on the plan (Step Inside Phase 2).

When the site plan is in real coordinates (a DXF/DWG of the survey with the proposal drawn in it), the walls'
hatches (poché) give the house exactly: find the rotation and offset that put the most hatch points on the model's
walls (fontes.json: axis, start, end, thickness). Standard library only.

    ajustar(pontos, paredes) -> {"rotacao_graus", "origem" (world position of the model's (0, 0)), "inliers", "n",
                                 "mediana_m", "p90_m", "segundo_inliers"}
"""
import math

TOL = 0.12  # m: a hatch point on a wall


def retangulos(paredes):
    out = []
    for p in paredes:
        a0, a1 = sorted([p["inicio"], p["fim"]])
        e = (p.get("espessura") or 0.16) / 2
        pos = p["posicao"]
        out.append((a0, pos - e, a1, pos + e) if p["eixo"] == "x" else (pos - e, a0, pos + e, a1))
    return out


def _dist(x, y, rects):
    best = 1e9
    for x0, y0, x1, y1 in rects:
        dx = x0 - x if x < x0 else (x - x1 if x > x1 else 0.0)
        dy = y0 - y if y < y0 else (y - y1 if y > y1 else 0.0)
        d = math.hypot(dx, dy)
        if d < best:
            best = d
            if d == 0.0:
                break
    return best


def _dist_face(x, y, rects):
    """Distance to the nearest wall FACE (hatch vertices sit on the faces of the walls' poché)."""
    best = 1e9
    for x0, y0, x1, y1 in rects:
        if x0 <= x <= x1 and y0 <= y <= y1:
            d = min(x - x0, x1 - x, y - y0, y1 - y)
        else:
            dx = x0 - x if x < x0 else (x - x1 if x > x1 else 0.0)
            dy = y0 - y if y < y0 else (y - y1 if y > y1 else 0.0)
            d = math.hypot(dx, dy)
        if d < best:
            best = d
    return best


def _eixo_principal(pts, robusto=False):
    """Angle (degrees, 0-180) of the minimum-area rectangle around the points (0.1° steps) and the centre used.
    robusto: ignore points far from the rest (other hatches nearby)."""
    if robusto:
        xs = sorted(p[0] for p in pts)
        ys = sorted(p[1] for p in pts)
        cx, cy = xs[len(xs) // 2], ys[len(ys) // 2]
        ds = sorted(math.hypot(p[0] - cx, p[1] - cy) for p in pts)
        lim = 2.5 * ds[len(ds) // 2]
        pts = [p for p in pts if math.hypot(p[0] - cx, p[1] - cy) <= lim] or pts
    mx = sum(p[0] for p in pts) / len(pts)
    my = sum(p[1] for p in pts) / len(pts)
    best = None
    for a10 in range(0, 1800):
        a = math.radians(a10 / 10)
        c, s = math.cos(a), math.sin(a)
        rx = [(p[0] - mx) * c + (p[1] - my) * s for p in pts]
        ry = [-(p[0] - mx) * s + (p[1] - my) * c for p in pts]
        A = (max(rx) - min(rx)) * (max(ry) - min(ry))
        if best is None or A < best[0]:
            best = (A, a10 / 10)
    return best[1], mx, my


def ajustar(pontos, paredes):
    rects = retangulos(paredes)
    L = max(r[2] for r in rects) - min(r[0] for r in rects)
    D = max(r[3] for r in rects) - min(r[1] for r in rects)
    candidatos = []
    a1, mx, my = _eixo_principal(pontos)  # all points, and without the far ones: two starting angles
    a2, _x, _y = _eixo_principal(pontos, robusto=True)
    for k in [(a, k) for a in sorted({a1, a2}) for k in range(4)]:
        th = math.radians(k[0] + 90 * k[1])
        c, s = math.cos(th), math.sin(th)
        loc = [((p[0] - mx) * c + (p[1] - my) * s, -(p[0] - mx) * s + (p[1] - my) * c) for p in pontos]
        bx0, by0 = min(q[0] for q in loc), min(q[1] for q in loc)
        bx1, by1 = max(q[0] for q in loc), max(q[1] for q in loc)

        def contar(ox, oy):
            return sum(1 for q in loc if _dist(q[0] - ox, q[1] - oy, rects) < TOL)
        melhor = None
        passo = 0.25  # coarse search over every offset that keeps the house inside the drawn extent (+1 m)
        nx = int(max(0.0, (bx1 - bx0) - L + 2.0) / passo) + 1
        ny = int(max(0.0, (by1 - by0) - D + 2.0) / passo) + 1
        for i in range(nx):
            for j in range(ny):
                ox, oy = bx0 - 1.0 + passo * i, by0 - 1.0 + passo * j
                n = contar(ox, oy)
                if melhor is None or n > melhor[0]:
                    melhor = (n, ox, oy)
        for passo, raio in ((0.05, 0.3), (0.01, 0.06)):  # refine around the best
            n0, ox0, oy0 = melhor
            r = int(raio / passo)
            for i in range(-r, r + 1):
                for j in range(-r, r + 1):
                    n = contar(ox0 + passo * i, oy0 + passo * j)
                    if n > melhor[0]:
                        melhor = (n, ox0 + passo * i, oy0 + passo * j)
        candidatos.append((melhor[0], th, melhor[1], melhor[2], loc))
    candidatos.sort(key=lambda c: -c[0])
    n, th, ox, oy, loc = candidatos[0]
    # the best count with a clearly different orientation (> 45°): how unambiguous the fit is
    outra = next((c[0] for c in candidatos[1:] if abs((math.degrees(c[1] - th) + 180) % 360 - 180) > 45), 0)
    # refine the angle around the best orientation (the rectangle's angle is only a start)
    for passo_a, raio_a, passo_t, raio_t in ((0.25, 2.0, 0.05, 0.2), (0.05, 0.25, 0.01, 0.05)):
        melhor = (n, th, ox, oy, loc)
        for ia in range(-int(raio_a / passo_a), int(raio_a / passo_a) + 1):
            th2 = th + math.radians(passo_a * ia)
            c2, s2 = math.cos(th2), math.sin(th2)
            loc2 = [((p[0] - mx) * c2 + (p[1] - my) * s2, -(p[0] - mx) * s2 + (p[1] - my) * c2) for p in pontos]
            r_t = int(raio_t / passo_t)
            for i in range(-r_t, r_t + 1):
                for j in range(-r_t, r_t + 1):
                    ox2, oy2 = ox + passo_t * i, oy + passo_t * j
                    n2 = sum(1 for q in loc2 if _dist(q[0] - ox2, q[1] - oy2, rects) < TOL)
                    if n2 > melhor[0]:
                        melhor = (n2, th2, ox2, oy2, loc2)
        n, th, ox, oy, loc = melhor
    # last: among the positions with the same count, the one that puts the inliers on the wall faces
    inl = [p for p, q in zip(pontos, loc) if _dist(q[0] - ox, q[1] - oy, rects) < TOL]

    def custo(th_, ox_, oy_):
        c_, s_ = math.cos(th_), math.sin(th_)
        return sum(_dist_face((p[0] - mx) * c_ + (p[1] - my) * s_ - ox_, -(p[0] - mx) * s_ + (p[1] - my) * c_ - oy_, rects)
                   for p in inl) / len(inl)
    atual = custo(th, ox, oy)
    passo_t, passo_a = 0.04, math.radians(0.04)
    while passo_t > 0.002:
        melhorou = False
        for dth, dx, dy in ((passo_a, 0, 0), (-passo_a, 0, 0), (0, passo_t, 0), (0, -passo_t, 0), (0, 0, passo_t), (0, 0, -passo_t)):
            c_ = custo(th + dth, ox + dx, oy + dy)
            if c_ < atual - 1e-9:
                atual, th, ox, oy, melhorou = c_, th + dth, ox + dx, oy + dy, True
        if not melhorou:
            passo_t, passo_a = passo_t / 2, passo_a / 2
    c, s = math.cos(th), math.sin(th)
    loc = [((p[0] - mx) * c + (p[1] - my) * s, -(p[0] - mx) * s + (p[1] - my) * c) for p in pontos]
    ds = sorted(_dist_face(q[0] - ox, q[1] - oy, rects) for q in loc
                if -0.3 <= q[0] - ox <= L + 0.3 and -0.3 <= q[1] - oy <= D + 0.3)
    c, s = math.cos(th), math.sin(th)
    # model -> world: w = R(th) (m + o) + centroid
    origem = (c * ox - s * oy + mx, s * ox + c * oy + my)
    return {"rotacao_graus": round(math.degrees(th) % 360, 3), "origem": origem, "inliers": n, "n": len(pontos),
            "dist_media_faces_m": round(atual, 4),
            "pontos_na_casa": len(ds), "mediana_m": round(ds[len(ds) // 2], 3) if ds else None,
            "p90_m": round(ds[int(len(ds) * 0.9)], 3) if ds else None, "segundo_inliers": outra}


def mundo(res, x, y):
    th = math.radians(res["rotacao_graus"])
    return (math.cos(th) * x - math.sin(th) * y + res["origem"][0], math.sin(th) * x + math.cos(th) * y + res["origem"][1])
