"""Closing the joints between the pieces of one finish layer (pure Python, used inside Blender by blender_visita.py).

The production model draws every piece of a layer with its joint (`junta` in sistema_construtivo.json: Tremolo 6 mm,
Pladur 2 mm, OSB 3 mm) so production can count the pieces. On site those joints are closed: the Tremolo is tongue
and groove, the plasterboard joints are taped and filled. In the visit model the layers behind are hidden, so each
joint becomes a slit into the wall (user 2026-11-09: «continua com gaps entre as madeiras do revestimento
exterior»). Each piece grows half the joint towards a neighbour in the same plane; pieces with no neighbour (façade
ends, openings) keep their edge.
"""

JUNTA_MAX = 0.012   # wider gaps are not joints (battens 35 cm apart, an opening, a corner)
TOL = 0.0005        # touching pieces: nothing to close
SOBREPOSICAO_MIN = 0.01  # neighbours share the joint over at least 1 cm (pieces meeting only at a corner do not)


def placas(caixas, espessura_max=0.06, comprido_min=0.1):
    """The pieces that are plates (boards, sheets): at most espessura_max thick, at least comprido_min long.
    caixas: [(lo, hi)] 3-tuples. Returns {i: thickness axis}.

    A board ripped narrow (a 39 mm strip of a 22 mm board beside an opening) is thin along two axes; its thickness
    axis is then the one of the nearest piece that is thin along one axis only."""
    cand, ext = {}, {}
    for i, (lo, hi) in enumerate(caixas):
        e = [hi[k] - lo[k] for k in range(3)]
        c = [k for k in range(3) if e[k] <= espessura_max]
        if c and max(e) >= comprido_min:
            cand[i], ext[i] = c, e
    certos = {i: c[0] for i, c in cand.items() if len(c) == 1}

    def centro(i):
        lo, hi = caixas[i]
        return [(lo[k] + hi[k]) / 2 for k in range(3)]

    out = dict(certos)
    for i, c in cand.items():
        if len(c) == 1:
            continue
        ci = centro(i)
        perto = [(sum((a - b) ** 2 for a, b in zip(ci, centro(j))), certos[j]) for j in certos if certos[j] in c]
        out[i] = min(perto)[1] if perto else min(c, key=lambda k: ext[i][k])
    return out


def extensoes(caixas, junta_max=JUNTA_MAX, tol=TOL):
    """How much each piece grows on each side to close the joints with its neighbours.

    Neighbours: plates with the same thin axis and the same plane (same faces within 1 mm), a gap along one in-plane
    axis between tol and junta_max, side by side over at least SOBREPOSICAO_MIN along the other in-plane axis.
    Returns ({i: {(axis, +1 | -1): distance}}, number of joints closed)."""
    finas = placas(caixas)
    grupos = {}
    for i, t in finas.items():
        lo, hi = caixas[i]
        grupos.setdefault((t, round(lo[t], 3), round(hi[t], 3)), []).append(i)
    ext, n = {}, 0
    for (t, _a, _b), idx in grupos.items():
        for a in (k for k in range(3) if k != t):
            b = 3 - t - a
            ordem = sorted(idx, key=lambda i: caixas[i][0][a])
            for p, i in enumerate(ordem):
                lo_i, hi_i = caixas[i]
                for j in ordem[p + 1:]:
                    lo_j, hi_j = caixas[j]
                    if lo_j[a] > hi_i[a] + junta_max:
                        break
                    g = lo_j[a] - hi_i[a]
                    if not tol < g <= junta_max:
                        continue
                    sob = min(hi_i[b], hi_j[b]) - max(lo_i[b], lo_j[b])
                    if sob < SOBREPOSICAO_MIN:  # side by side over a real length (staggered sheets: half a sheet)
                        continue
                    di = ext.setdefault(i, {})
                    dj = ext.setdefault(j, {})
                    di[(a, 1)] = max(di.get((a, 1), 0.0), g / 2)
                    dj[(a, -1)] = max(dj.get((a, -1), 0.0), g / 2)
                    n += 1
    return ext, n
