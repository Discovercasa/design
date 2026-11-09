"""Pure helpers of the AR table model (Step Inside Phase 7, hub task 157; no bpy, unit-tested in test_ar.py).

The survey terrain ends in an irregular outline (the edge of the surveyed TIN) and the old crop deleted the triangles
beyond `raio`, so the table model's edge was saw-toothed (task 157: «borda da maquete mais limpa»). Now the table model
is a rectangular block, like an architect's model:
  retangulo  the largest rectangle around the house, at most `raio` beyond it on each side, whose ground the terrain
             covers completely (so the cut has no notches)
  saia       the vertical faces that close the cut terrain down to a flat bottom
"""
import math


def _dentro(px, py, a, b, c, eps=1e-9):
    d1 = (px - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (py - b[1])
    d2 = (px - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (py - c[1])
    d3 = (px - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (py - a[1])
    neg = d1 < -eps or d2 < -eps or d3 < -eps
    pos = d1 > eps or d2 > eps or d3 > eps
    return not (neg and pos)


def nos_cobertos(tris, x0, y0, nx, ny, passo):
    """Grid nodes (i, j), 0 <= i <= nx, 0 <= j <= ny, at (x0 + i·passo, y0 + j·passo), that lie in at least one of the
    plan triangles `tris` ([(x, y)] × 3). Vertical (zero-area) triangles cover nothing."""
    cob = set()
    for a, b, c in tris:
        if abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) < 1e-9:
            continue
        xs, ys = (a[0], b[0], c[0]), (a[1], b[1], c[1])
        i0 = max(0, math.ceil((min(xs) - x0) / passo - 1e-9))
        i1 = min(nx, math.floor((max(xs) - x0) / passo + 1e-9))
        j0 = max(0, math.ceil((min(ys) - y0) / passo - 1e-9))
        j1 = min(ny, math.floor((max(ys) - y0) / passo + 1e-9))
        for i in range(i0, i1 + 1):
            px = x0 + i * passo
            for j in range(j0, j1 + 1):
                if (i, j) not in cob and _dentro(px, y0 + j * passo, a, b, c):
                    cob.add((i, j))
    return cob


def retangulo(tris, casa, raio, passo=0.5, minimo=1.0):
    """The table model's ground: the largest rectangle (x0, y0, x1, y1) that holds the house footprint `casa`
    (x0, y0, x1, y1), reaches at most `raio` beyond it on each side (in steps of `passo`) and whose ground the terrain
    triangles `tris` cover completely. Checked on a grid of `passo`: a cell counts when its four corners are on the
    terrain; cells under the house may be a hole in the terrain. Equal areas: the most even margins. None when the terrain
    does not reach `minimo` beyond the house on every side."""
    K = int(raio / passo + 1e-9)
    m0 = min(K, math.ceil(minimo / passo - 1e-9))
    nW = max(1, math.ceil((casa[2] - casa[0]) / passo - 1e-9))
    nH = max(1, math.ceil((casa[3] - casa[1]) / passo - 1e-9))
    X0, Y0 = casa[0] - K * passo, casa[1] - K * passo
    nx, ny = 2 * K + nW, 2 * K + nH
    cob = nos_cobertos(tris, X0, Y0, nx, ny, passo)

    def boa(i, j):
        if K <= i < K + nW and K <= j < K + nH:
            return True
        return (i, j) in cob and (i + 1, j) in cob and (i, j + 1) in cob and (i + 1, j + 1) in cob

    mas = []  # per row, running count of bad cells (row prefix sums)
    for j in range(ny):
        s, linha = 0, [0]
        for i in range(nx):
            s += 0 if boa(i, j) else 1
            linha.append(s)
        mas.append(linha)
    melhor = None
    for esq in range(m0, K + 1):
        for dir_ in range(m0, K + 1):
            i0, i1 = K - esq, K + nW + dir_

            def ok(j):
                return mas[j][i1] - mas[j][i0] == 0

            if not all(ok(j) for j in range(K, K + nH)):
                continue
            baixo = 0
            while baixo < K and ok(K - baixo - 1):
                baixo += 1
            cima = 0
            while cima < K and ok(K + nH + cima):
                cima += 1
            if min(baixo, cima) < m0:
                continue
            chave = ((nW + esq + dir_) * (nH + baixo + cima), min(esq, dir_, baixo, cima))
            if melhor is None or chave > melhor[0]:
                melhor = (chave, (esq, dir_, baixo, cima))
    if melhor is None:
        return None
    esq, dir_, baixo, cima = melhor[1]
    return (casa[0] - esq * passo, casa[1] - baixo * passo, casa[2] + dir_ * passo, casa[3] + cima * passo)


def saia(arestas, ret, z_base, tol=1e-3):
    """Vertical faces closing the cut terrain: for each boundary edge (p, q) of the terrain that lies on a side of the
    rectangle `ret`, the quad from it down to `z_base`, wound so its normal points out of the block. Plus the flat
    bottom (normal down). Points are (x, y, z)."""
    x0, y0, x1, y1 = ret
    lados = ((0, x0, -1), (0, x1, 1), (1, y0, -1), (1, y1, 1))  # (axis, value, outward sign)
    quads = []
    for p, q in arestas:
        for ax, val, s in lados:
            if abs(p[ax] - val) < tol and abs(q[ax] - val) < tol:
                pb, qb = (p[0], p[1], z_base), (q[0], q[1], z_base)
                e1 = [q[i] - p[i] for i in range(3)]
                e2 = [qb[i] - p[i] for i in range(3)]
                n = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
                quad = [tuple(p), tuple(q), qb, pb]
                if n[ax] * s < 0:
                    quad.reverse()
                quads.append(quad)
                break
    fundo = [(x0, y0, z_base), (x0, y1, z_base), (x1, y1, z_base), (x1, y0, z_base)]
    return quads, fundo
