"""The timber of a configured house's exposed roof, checked as built by the engine (telhado.py, telhado_estrutura.py
via casa_planta.py): members through one another (one convex piece inside another by more than 8 mm), purlins / hips /
valleys bearing on nothing for more than 1,30 (1,45 for a hip or valley, which crosses the beams at 45°; 0,75 at a free
end, a hip / valley tail over the overhang the eave's diagonal + 0,12 — an end fixed to the side of a hip or valley
bears on it), prumos standing on no beam or past its edge, the empenas' members against the roof timber (2026-10-29),
and slope areas where a panel spans more than 1,30 between purlins or ends more than 0,25 short of the ridge / 0,70 past
the eave purlin.
Written after the user's screenshots of 2026-10-28 ("parecem haver vigas em falta e nas junções umas vigas passam em
cima das outras").

    python ferramentas/configurador/auditar_cobertura.py <casa.json> [--tipo misto] [--pct 40] [--beirado 0.4] [-v]
    python ferramentas/configurador/auditar_cobertura.py --formas [duas_aguas misto]   (L / T / U / rectangle / with a
    garage sweep)
"""
import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.configurador.para_construtor import converter  # noqa: E402
from ferramentas.modelo.casa_planta import construir  # noqa: E402
from ferramentas.modelo.camadas import fundir, teto_sob_anel  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
S0 = json.load(open(RAIZ / "ferramentas/modelo/sistema_construtivo.json", encoding="utf-8"))
TELHADO = ("Viga de apoio à cobertura", "Prumo", "Calço", "Rincão", "Laró", "Viga de apoio ao teto", "Lamelada",
           "Viga de bordadura", "Viga de bordo")


def vertices(pc):
    b = pc["b"]
    t = pc.get("t") or [[x + pc["e"][0], y + pc["e"][1], z + pc["e"][2]] for x, y, z in b]
    return b, t


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    L = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)
    return (a[0] / L, a[1] / L, a[2] / L) if L > 1e-9 else None


def solido(pc):
    b, t = vertices(pc)
    n = len(b)
    V = [tuple(p) for p in b] + [tuple(p) for p in t]
    faces, arestas = [], []
    for i in range(n):
        j = (i + 1) % n
        faces.append(cross(sub(b[j], b[i]), sub(t[i], b[i])))
        arestas += [sub(b[j], b[i]), sub(t[j], t[i]), sub(t[i], b[i])]
    faces.append(cross(sub(b[1], b[0]), sub(b[2], b[0])))
    faces.append(cross(sub(t[1], t[0]), sub(t[2], t[0])))
    F = [f for f in (norm(f) for f in faces) if f]
    A = [a for a in (norm(a) for a in arestas) if a]
    lo = [min(v[k] for v in V) for k in range(3)]
    hi = [max(v[k] for v in V) for k in range(3)]
    return {"V": V, "F": F, "A": A, "lo": lo, "hi": hi}


def penetracao(s1, s2):
    """Separating-axis test: the smallest overlap over the candidate axes (<= 0: apart or touching)."""
    eixos = s1["F"] + s2["F"]
    for a in s1["A"]:
        for b in s2["A"]:
            c = norm(cross(a, b))
            if c:
                eixos.append(c)
    m = float("inf")
    for ax in eixos:
        p1 = [v[0] * ax[0] + v[1] * ax[1] + v[2] * ax[2] for v in s1["V"]]
        p2 = [v[0] * ax[0] + v[1] * ax[1] + v[2] * ax[2] for v in s2["V"]]
        ov = min(max(p1), max(p2)) - max(min(p1), min(p2))
        if ov < m:
            m = ov
            if m <= 0:
                return m
    return m


def tipo_de(o):
    t = o["props"].get("tipo", "")
    for k in TELHADO:
        if t.startswith(k):
            return k
    return None


def main():
    if "--formas" in sys.argv:
        return formas([t for t in sys.argv[1:] if t != "--formas"] or ["duas_aguas", "misto"])
    ap = argparse.ArgumentParser()
    ap.add_argument("casa")
    ap.add_argument("--tipo")
    ap.add_argument("--pct", type=float)
    ap.add_argument("--beirado", type=float)
    ap.add_argument("--tol", type=float, default=0.008)
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    casa = json.load(open(a.casa, encoding="utf-8"))
    auditar(casa, a)


def auditar(casa, a):
    cob = casa.setdefault("cobertura", {})
    if a.tipo:
        cob["tipo"] = a.tipo
    if a.pct:
        cob["inclinacao_pct"] = a.pct
    if a.beirado:
        cob["beirado"] = a.beirado
    planta, cfg, notas = converter(casa, S0)
    S = teto_sob_anel(fundir(json.loads(json.dumps(S0)), cfg.get("camadas") or {}), cfg)
    E = fundir(S["estrutura"], {k: v for k, v in (cfg.get("estrutura") or {}).items() if k != "sistema"})
    G, resumo = construir(cfg, S, E, planta)
    pecas = []
    for o in G["estrutura_extra"]:
        k = tipo_de(o)
        if not k:
            continue
        for pc in o["pecas"]:
            s = solido(pc)
            s.update({"nome": o["nome"], "tipo": k})
            pecas.append(s)
    print(f"{cob.get('tipo')}: {len(pecas)} roof pieces; types {dict(Counter(p['tipo'] for p in pecas))}")
    # ------------------------------------------------------------ clashes (the empenas' members too: the eave purlin and
    # a valley's foot had run through the gable's plates — user 2026-10-29 "vigas a sobreporem-se umas as outras nos
    # cantos do triângulo da empena")
    choques = []
    todas = sorted(pecas + empenas_solidos(G), key=lambda s: s["lo"][0])
    for i, s1 in enumerate(todas):
        for s2 in todas[i + 1:]:
            if s2["lo"][0] > s1["hi"][0] - a.tol:
                break
            if s1["tipo"] == s2["tipo"] == "Empena" and s1["nome"] == s2["nome"]:
                continue  # the members of one gable frame touch by design
            if any(s1["lo"][k] > s2["hi"][k] - a.tol or s2["lo"][k] > s1["hi"][k] - a.tol for k in (1, 2)):
                continue
            p = penetracao(s1, s2)
            if p > a.tol:
                choques.append((p, s1, s2))
    por_par = defaultdict(list)
    for p, s1, s2 in choques:
        par = tuple(sorted((s1["tipo"], s2["tipo"])))
        por_par[par].append((p, s1, s2))
    print(f"clashes > {a.tol * 1000:.0f} mm: {len(choques)}")
    for par, lst in sorted(por_par.items(), key=lambda kv: -len(kv[1])):
        lst.sort(key=lambda t: -t[0])
        print(f"  {par[0]} x {par[1]}: {len(lst)} (worst {lst[0][0] * 100:.1f} cm)")
        for p, s1, s2 in lst[: (12 if a.v else 3)]:
            c = [(s1["lo"][k] + s1["hi"][k]) / 2 for k in range(3)]
            print(f"     {p * 100:5.1f} cm  {s1['nome']}  <>  {s2['nome']}  near ({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f})")
    prumos_na_viga(pecas, a.v)
    apoio_suporte(G, pecas, a.v)
    if a.v:
        print("notas:", "; ".join(notas))


def prumos_na_viga(pecas, verbose):
    """Every prumo / calço stands within the width of the beam under it (they had kept one orientation in every wing,
    half off a beam running the other way — user 2026-10-29 "apenas tem uma viga pousada a metade da sua largura")."""
    vigas = [s for s in pecas if s["tipo"] in ("Viga de apoio ao teto", "Lamelada", "Viga de bordadura", "Viga de bordo")]
    maus = []
    for s in pecas:
        if s["tipo"] not in ("Prumo", "Calço"):
            continue
        zb = s["lo"][2]
        sob = [v for v in vigas if abs(v["hi"][2] - zb) < 0.01 and
               v["lo"][0] - 0.003 <= (s["lo"][0] + s["hi"][0]) / 2 <= v["hi"][0] + 0.003 and
               v["lo"][1] - 0.003 <= (s["lo"][1] + s["hi"][1]) / 2 <= v["hi"][1] + 0.003]
        if sob and not any(v["lo"][0] - 0.003 <= s["lo"][0] and s["hi"][0] <= v["hi"][0] + 0.003 and
                           v["lo"][1] - 0.003 <= s["lo"][1] and s["hi"][1] <= v["hi"][1] + 0.003 for v in sob):
            maus.append(s)
    print(f"prumos over the edge of their beam: {len(maus)}")
    for s in maus[: (12 if verbose else 3)]:
        print(f"     {s['nome']} x {s['lo'][0]:.3f}-{s['hi'][0]:.3f} y {s['lo'][1]:.3f}-{s['hi'][1]:.3f}")


def semiespacos(s):
    V = s["V"]
    c = [sum(v[k] for v in V) / len(V) for k in range(3)]
    n4 = len(V) // 2
    b, t = V[:n4], V[n4:]
    hs = []
    quads = [(b[i], b[(i + 1) % n4], t[(i + 1) % n4], t[i]) for i in range(n4)] + [tuple(b), tuple(t)]
    for q in quads:
        nrm = norm(cross(sub(q[1], q[0]), sub(q[2], q[0])))
        if not nrm:
            nrm = norm(cross(sub(q[2], q[0]), sub(q[3], q[0])))
        if not nrm:
            continue
        d = sum(nrm[k] * q[0][k] for k in range(3))
        if sum(nrm[k] * c[k] for k in range(3)) > d:
            nrm, d = (-nrm[0], -nrm[1], -nrm[2]), -d
        hs.append((nrm, d))
    s["H"] = hs


def dentro_s(s, p, tol=0.01):
    if any(p[k] < s["lo"][k] - tol or p[k] > s["hi"][k] + tol for k in range(3)):
        return False
    return all(n[0] * p[0] + n[1] * p[1] + n[2] * p[2] - d <= tol for n, d in s["H"])


def empenas_solidos(G):
    out = []
    for p in G["paineis"]:
        if not p.get("empena"):
            continue
        a = G["alcados"][p["alcado"]]
        ox, oy, oz = p["origem"]
        ux, uy = p["sentido"]
        t = p["espessura"]

        def mundo(u, v, w):
            return [ox + u * ux - w * uy, oy + u * uy + w * ux, oz + v]
        for m in a["members"]:
            b = [mundo(u, v, -t / 2) for u, v in m["poly"]]
            tt = [mundo(u, v, t / 2) for u, v in m["poly"]]
            s = solido({"b": b, "t": tt})
            s.update({"nome": p["nome"], "tipo": "Empena"})
            out.append(s)
    return out


def apoio_suporte(G, pecas, verbose):
    """Every purlin / hip / valley must bear on something every <= 1,25 m; every prumo on a beam."""
    emp = empenas_solidos(G)
    cauda = G["cobertura"].get("beirado", 0.25) * 2 ** 0.5 + 0.12  # a rincão / laró tail over the overhang
    todos = pecas + emp
    for s in todos:
        semiespacos(s)
    sup_tipos = ("Prumo", "Calço", "Viga de apoio ao teto", "Lamelada", "Viga de bordadura", "Viga de bordo", "Rincão",
                 "Laró", "Empena", "Viga de apoio à cobertura")
    falhas = defaultdict(list)
    for s in pecas:
        if s["tipo"] not in ("Viga de apoio à cobertura", "Rincão", "Laró", "Prumo", "Calço"):
            continue
        V = s["V"]
        n4 = len(V) // 2
        b, t = V[:n4], V[n4:]
        if s["tipo"] in ("Prumo", "Calço"):
            p = [sum(v[k] for v in b) / n4 for k in range(3)]
            p[2] = min(v[2] for v in b) - 0.012
            if not any(o is not s and o["tipo"] in ("Viga de apoio ao teto", "Lamelada", "Viga de bordadura", "Viga de bordo",
                                                     "Viga de apoio à cobertura")
                       and dentro_s(o, p, 0.006) for o in todos):
                falhas["prumo sem viga por baixo"].append((s["nome"], p))
            continue
        # the long axis: from the base to the top face (centre to centre: a mitred end's corners stand at different
        # places along it); the bottom line = the lowest edge of the base
        e = sub([sum(v[k] for v in t) / n4 for k in range(3)], [sum(v[k] for v in b) / n4 for k in range(3)])
        L = math.sqrt(sum(c * c for c in e))
        zmin = min(v[2] for v in b)
        lows = sorted(b, key=lambda v: v[2])[:2]
        p0 = [(lows[0][k] + lows[1][k]) / 2 for k in range(3)]
        n_s = max(2, int(L / 0.05))
        ok = []
        for i in range(n_s + 1):
            f = i / n_s
            p = [p0[k] + e[k] * f for k in range(3)]
            q = [p[0], p[1], p[2] - 0.015]
            ok.append(any(o is not s and o["tipo"] in sup_tipos and dentro_s(o, q, 0.008) for o in todos))
        # also the ends butting a hip / valley / another purlin side (lateral support)
        runs, cur = [], None
        for i, v in enumerate(ok):
            if not v and cur is None:
                cur = i
            if v and cur is not None:
                runs.append((cur, i - 1))
                cur = None
        if cur is not None:
            runs.append((cur, n_s))
        # an end butting a hip / valley member (fixed to its side) bears on it
        topo = max(v[2] for v in b)
        ue = [c / L for c in e]

        def encosta(f):
            q = [p0[k] + e[k] * f + ue[k] * (0.07 if f > 0.5 else -0.07) for k in range(3)]
            q[2] = (zmin + topo) / 2 + e[2] * f
            return any(o is not s and o["tipo"] in ("Rincão", "Laró") and dentro_s(o, q, 0.012) for o in todos)
        for a_, b_ in runs:
            comp = (b_ - a_ + 1) * L / n_s
            ponta = (a_ == 0 and not encosta(0.0)) or (b_ == n_s and not encosta(1.0))
            diag = s["tipo"] in ("Rincão", "Laró")  # crosses the beams at 45°; its tail runs the eave's diagonal
            lim = (max(0.75, cauda) if diag else 0.75) if ponta else (1.45 if diag else 1.30)
            if comp > lim:
                f = (a_ + b_) / 2 / n_s
                c = [p0[k] + e[k] * f for k in range(3)]
                falhas[f"{s['tipo']}: {'consola' if ponta else 'vão'} sem apoio > {lim:.2f}"].append(
                    (f"{s['nome']} {comp:.2f} m", c))
    print("supports:")
    if not falhas:
        print("  all members bear every <= 1,30 (ends <= 0,75), every prumo on a beam")
    for k, lst in falhas.items():
        print(f"  {k}: {len(lst)}")
        for nome, c in lst[: (15 if verbose else 4)]:
            print(f"     {nome}  at ({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f})")
    cobertura_coberta(G, pecas)


def raio_poly(poly, p, d):
    """Distance along the ray p + s d (s >= 0) to the first point inside the convex polygon, or None."""
    t0, t1 = 0.0, 1e9
    n = len(poly)
    area2 = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sg = 1 if area2 > 0 else -1
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        f0 = sg * (ex * (p[1] - y1) - ey * (p[0] - x1))
        df = sg * (ex * d[1] - ey * d[0])
        if abs(df) < 1e-12:
            if f0 < 0:
                return None
            continue
        s = -f0 / df
        if df > 0:
            t0 = max(t0, s)
        else:
            t1 = min(t1, s)
    return t0 if t1 >= t0 else None


def saida(poly, p, d):
    """From a point inside a convex polygon, the distance along d to its boundary."""
    best = 1e9
    n = len(poly)
    area2 = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sg = 1 if area2 > 0 else -1
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        f0 = sg * (ex * (p[1] - y1) - ey * (p[0] - x1))
        df = sg * (ex * d[1] - ey * d[0])
        if df < -1e-12:
            best = min(best, -f0 / df)
    return best


def dentro_p(poly, x, y, tol=1e-6):
    n = len(poly)
    area2 = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sg = 1 if area2 > 0 else -1
    return all(sg * ((poly[(i + 1) % n][0] - poly[i][0]) * (y - poly[i][1]) - (poly[(i + 1) % n][1] - poly[i][1]) * (x - poly[i][0])) >= -tol
               for i in range(n))


def saida_plano(polys, p, d):
    """From a point on a slope (its convex pieces), the distance along d to the slope's edge."""
    s = 0.0
    for _ in range(50):
        q = (p[0] + d[0] * s, p[1] + d[1] * s)
        cur = next((pl for pl in polys if dentro_p(pl, q[0], q[1], 1e-4)), None)
        if cur is None:
            return s
        s += saida(cur, q, d) + 0.005
    return s


def hull(pts):
    pts = sorted(set((round(x, 5), round(y, 5)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def cobertura_coberta(G, pecas):
    """Every point of every slope: the panel spans <= 1,25 (along the slope) between the supports below it."""
    C = G["cobertura"]
    faces = C.get("faces") or []
    if not faces:
        return
    t = math.tan(math.radians(C["inclinacao"]))
    ct = math.cos(math.atan(t))
    sup = [hull([(v[0], v[1]) for v in s["V"]]) for s in pecas if s["tipo"] in ("Viga de apoio à cobertura", "Rincão", "Laró")]
    maus = []
    for f in faces:
        ex, ey = f["subida"]
        xs = [p[0] for p in f["pts"]]
        ys = [p[1] for p in f["pts"]]
        passo = 0.2
        x = min(xs) + passo / 2
        while x < max(xs):
            y = min(ys) + passo / 2
            while y < max(ys):
                pts = f["pts"]
                n = len(pts)
                dentro = all((pts[(i + 1) % n][0] - pts[i][0]) * (y - pts[i][1]) - (pts[(i + 1) % n][1] - pts[i][1]) * (x - pts[i][0]) >= 1e-6
                             for i in range(n))
                if dentro:
                    # a purlin within 0,12 along the eaves counts (a 10 cm strip over a header is no gap for a 1 m panel)
                    up, dn = [], []
                    for off in (-0.12, 0.0, 0.12):
                        q = (x - ey * off, y + ex * off)
                        up += [r for r in (raio_poly(s, q, (ex, ey)) for s in sup) if r is not None]
                        dn += [r for r in (raio_poly(s, q, (-ex, -ey)) for s in sup) if r is not None]
                    mesmo = [g["pts"] for g in faces if tuple(g["plano"]) == tuple(f["plano"])]
                    su, sd = saida_plano(mesmo, (x, y), (ex, ey)), saida_plano(mesmo, (x, y), (-ex, -ey))
                    du = min(up) if up and min(up) <= su + 0.05 else None
                    dd = min(dn) if dn and min(dn) <= sd + 0.05 else None
                    if du is not None and dd is not None:
                        if (du + dd) / ct > 1.30:
                            maus.append((f["ret"], f["nome"], x, y, (du + dd) / ct))
                    else:  # the ridge above (<= 0,25 to it) or the eaves below (the overhang, <= 0,70)
                        if (du is None and su > 0.25) or (dd is None and sd > 0.70):
                            maus.append((f["ret"], f["nome"], x, y, None))
                y += passo
            x += passo
    print(f"slope coverage: {len(maus)} sample points (0,2 grid) with a panel span > 1,30 or no purlin on one side")
    grupos = defaultdict(list)
    for r, nm, x, y, v in maus:
        grupos[(r, nm, v is None)].append((x, y, v))
    for (r, nm, lado), lst in sorted(grupos.items()):
        xs = [p[0] for p in lst]
        ys = [p[1] for p in lst]
        print(f"   R{r + 1}{nm} {'no purlin above or below' if lado else 'span > 1,30'}: {len(lst)} pts in x {min(xs):.1f}-{max(xs):.1f}, y {min(ys):.1f}-{max(ys):.1f}")


def formas(tipos):
    """The shapes the configurator offers (its default proportions, a few sizes and slopes), one line each."""
    import io
    from contextlib import redirect_stdout
    from types import SimpleNamespace
    from ferramentas.configurador.formas import contorno
    casos = [("R 12x8", [[0, 0], [12, 0], [12, 8], [0, 8]], 15, 0.25),
             ("L 120", contorno("L", 120), 15, 0.25),
             ("L 12x8+5x6", [[0, -6], [5, -6], [5, 0], [12, 0], [12, 8], [0, 8]], 15, 0.25),
             ("L 140 40%", contorno("L", 140), 40, 0.4),
             ("T 150", contorno("T", 150), 15, 0.25),
             ("U 175", contorno("U", 175.5), 15, 0.25),
             ("U 25x10 patio 11x5", [[0, 0], [25, 0], [25, 10], [18, 10], [18, 5], [7, 5], [7, 10], [0, 10]], 15, 0.25),
             ("U 25x10 patio 5x7 40%", [[0, 0], [25, 0], [25, 10], [15, 10], [15, 3], [10, 3], [10, 10], [0, 10]], 40, 0.4),
             # a garage attached to a rectangle (step 7, 2026-10-29): flush with a corner (an L with a shallow wing) and
             # mid side (a T)
             ("R + garagem (L)", [[0, 0], [19.85, 0], [19.85, 3.7], [13.85, 3.7], [13.85, 8.65], [0, 8.65]], 15, 0.25),
             ("R + garagem (T)", [[0, 0], [13.85, 0], [13.85, 8.65], [8.8, 8.65], [8.8, 14.65], [5.1, 14.65], [5.1, 8.65], [0, 8.65]], 15, 0.25)]
    for nome, cont, pct, beir in casos:
        for tipo in tipos:
            casa = {"formato": "discovercasa-configurador/1", "nome": nome, "obra": "CFG", "base": {"contorno": cont},
                    "cobertura": {"tipo": tipo, "inclinacao_pct": pct, "beirado": beir}, "pe_direito": 2.5}
            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    auditar(casa, SimpleNamespace(tipo=None, pct=None, beirado=None, tol=0.008, v=False))
            except Exception as e:  # noqa: BLE001
                print(f"{nome:24s} {tipo:12s} ERRO {type(e).__name__}: {e}")
                continue
            ls = buf.getvalue().splitlines()
            ch = next((ln for ln in ls if ln.startswith("clashes")), ":?").split(":")[-1].strip()
            sup = [ln.strip() for ln in ls if "sem apoio" in ln or "sem viga" in ln]
            pv = next((ln for ln in ls if ln.startswith("prumos over")), ": ?").split(":")[-1].strip()
            if pv != "0":
                sup.append(f"{pv} prumos off their beam")
            cov = next((ln for ln in ls if ln.startswith("slope coverage")), ": ? ").split(":")[1].split("sample")[0].strip()
            print(f"{nome:24s} {tipo:12s} {ch} clashes | {'; '.join(sup) or 'supports ok'} | {cov} slope points bare")


if __name__ == "__main__":
    main()
