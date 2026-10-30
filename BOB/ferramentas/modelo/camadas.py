"""DiscoverCasa build-up layers ("camadas") of a timber-frame house model. Pure Python.

    python ferramentas/modelo/camadas.py "<project>/modelos/<type>/config.json" [--saida FILE]

Inputs: the geometry JSON written by extrair_casa.py, the company standard
`sistema_construtivo.json` (this folder) and the project overrides in config.json -> "camadas".
Output (default `_trabalho/modelos/<model folder>/camadas.json`): collections, materials and objects
whose pieces are prisms in world coordinates; blender/build_casa.py turns them into meshes.

What is generated (sequence of the DiscoverCasa build, see conhecimento/sistema-construtivo.md):
  2   exterior of the exterior walls: OSB 9 -> Traspir 95 -> finish option A (battens + Tremolo boards),
      B (ETICS: XPS + render) or C (battens + cork boards); all options are built, one is visible;
  3   inside: mineral wool in the stud cavities (per wall module) -> OSB 15 -> Pladur (per room);
  4   floors: ground floor XPS + screed + finish, upper floor finish on the structural OSB;
  5   ceilings: T-47 profiles + Pladur (flat under the joists, sloped under the rafters);
  6   roof covering: purlins, tile-effect sandwich panels, ridge cap, verge trims, gutters, downpipes.

Geometry rules: rooms and facades come from the plan footprints of the wall modules (coordinate grid).
Openings come from the stud layout (paineis.py). Corners are butt joints: faces running E-W run
through, faces running N-S stop against them. Door/window sizes are inferred (not in the drawings).
"""
import argparse
import bisect
import copy
import json
import math
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.comum import pasta_trabalho  # noqa: E402
from ferramentas.modelo.geometria2d import (area, clean, clip_box, clip_semiplano, dividir_grelha,  # noqa: E402
                                            encolher, subtrair_retangulos)
from ferramentas.modelo.paineis import Painel  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent


def fundir(base, extra):
    """Deep merge (extra wins; lists are replaced; null removes the key, e.g. a finish option)."""
    out = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        if v is None:
            out.pop(k, None)
            continue
        out[k] = fundir(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


def R(v):
    return round(v, 5)


def prisma(base, ext):
    return {"b": [[R(c) for c in p] for p in base], "e": [R(c) for c in ext]}


def caixa(x0, x1, y0, y1, z0, z1):
    return prisma([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], (0, 0, z1 - z0))


# ============================================================================ house and roof
class Casa:
    def __init__(self, G):
        self.G = G
        self.L, self.D = G["casa"]["comprimento"], G["casa"]["profundidade"]
        self.nv = G["niveis"]
        C = G["cobertura"]
        self.yr, self.zr = C["cumeeira_y"], C["cumeeira_z"]  # zr = top of the rafters on the ridge line
        th = math.radians(C["inclinacao"])
        self.tn, self.ct, self.st = math.tan(th), math.cos(th), math.sin(th)
        self.dz = C["altura_viga"] / self.ct  # vertical depth of the rafters
        self.apoio = C["apoio_z"]
        # "discovercasa": flat ceiling at the tie beam on the upper floor, purlins on posts (estrutura_dc.py)
        self.sistema = C.get("sistema", "vigas")
        self.z_cob_dc = C.get("plano_z_cume")
        # underside of the structure above each flat ceiling (single-storey houses: the ceiling beams)
        self.teto = {0: self.nv.get("teto_piso0", self.nv["topo_paredes_piso0"])}
        if self.sistema == "discovercasa" and "teto_piso1" in self.nv:
            self.teto[1] = self.nv["teto_piso1"]
        centro = (self.L / 2, self.D / 2)
        self.paineis = [Painel(p, G["alcados"][p["alcado"]], centro) for p in G["paineis"]]
        self.pisos = sorted({P.piso for P in self.paineis if P.piso in (0, 1)})  # storeys with rooms
        self.platibanda = C.get("tipo") == "platibanda"
        # an exposed roof of several slopes (casa_planta.py + telhado.py): its faces, z on the top of the purlins
        self.faces = C.get("faces") if C.get("tipo") == "a_vista" else None

    def z_faces(self, x, y):
        """The exposed roof's underside (top of the purlins) above a plan point, or None outside it."""
        zs = []
        for f in self.faces or []:
            p, n = f["pts"], len(f["pts"])
            if all((p[(i + 1) % n][0] - p[i][0]) * (y - p[i][1]) - (p[(i + 1) % n][1] - p[i][1]) * (x - p[i][0]) >= -1e-6
                   for i in range(n)):
                zs.append(f["z0"] + f["gx"] * x + f["gy"] * y)
        return max(zs) if zs else None

    def z_cob_cume(self, S):
        """Underside of the roof panels on the ridge line."""
        if self.sistema == "discovercasa":
            return self.z_cob_dc
        va = S["cobertura"].get("vigas_apoio")
        return self.zr + (va["altura"] / self.ct if va else 0.0)

    def z_rt(self, y):
        """Top plane of the rafters."""
        return self.zr - self.tn * abs(y - self.yr)

    def z_rb(self, y):
        """Underside plane of the rafters (sloped ceiling)."""
        return self.z_rt(y) - self.dz


def sob_faces(rect, face, casa, w=0.0):
    """A façade layer under an exposed roof of several slopes: the rectangle (s, z) cut by the roof's profile along the
    layer's plane, in vertical strips between the profile's corners (each strip convex)."""
    s0, s1 = min(p[0] for p in rect), max(p[0] for p in rect)
    z0 = min(p[1] for p in rect)
    fixo = face["c"] + face["n"] * w
    xy = (lambda s: (s, fixo)) if face["o"] == "y" else (lambda s: (fixo, s))
    cortes = {s0, s1}
    for f in casa.faces:  # where the line crosses an edge of a roof face
        p, n = f["pts"], len(f["pts"])
        for i in range(n):
            (xa, ya), (xb, yb) = p[i], p[(i + 1) % n]
            a, b = ((ya, yb), (xa, xb)) if face["o"] == "y" else ((xa, xb), (ya, yb))  # across, along
            if (a[0] - fixo) * (a[1] - fixo) < 0:
                s = b[0] + (b[1] - b[0]) * (fixo - a[0]) / (a[1] - a[0])
                if s0 < s < s1:
                    cortes.add(s)
    cortes = sorted(cortes)
    out = []
    for sa, sb in zip(cortes, cortes[1:]):
        if sb - sa < 1e-4:
            continue
        m = (sa + sb) / 2
        fs = [f for f in casa.faces if all(
            (f["pts"][(i + 1) % len(f["pts"])][0] - f["pts"][i][0]) * (xy(m)[1] - f["pts"][i][1]) -
            (f["pts"][(i + 1) % len(f["pts"])][1] - f["pts"][i][1]) * (xy(m)[0] - f["pts"][i][0]) >= -1e-6
            for i in range(len(f["pts"])))]
        if not fs:
            continue
        zf = lambda f, s: f["z0"] + f["gx"] * xy(s)[0] + f["gy"] * xy(s)[1]  # noqa: E731
        f = max(fs, key=lambda f: zf(f, m))
        za, zb = zf(f, sa), zf(f, sb)
        if max(za, zb) <= z0 + 1e-4:
            continue
        out.append([(sa, z0), (sb, z0), (sb, zb), (sa, za)])
    return out


def entre_telhados(s0, s1, face, casa, w, folga_baixo):
    """The cladding of a gable standing over a lower roof ("encosto", telhado_estrutura.py): from the lower roof's
    covering (+ folga_baixo) up to the upper roof's underside, along the layer's plane, in convex strips."""
    C = casa.G["cobertura"]
    rets, t, ze = C["retangulos"], C["t"], C["z_beirado"]
    rb, rc = face["encosto"]["ret_baixo"], face["encosto"]["ret_cima"]
    fixo = face["c"] + face["n"] * w
    xy = (lambda s: (s, fixo)) if face["o"] == "y" else (lambda s: (fixo, s))
    # each roof's own surface (the lowest of its planes), also where the other roof hides it: z = ze + t (a x + b y + c)
    zr = lambda r, s: ze + t * min(a * xy(s)[0] + b * xy(s)[1] + c for a, b, c, *_ in rets[r]["planos"])  # noqa: E731
    cortes = {s0, s1}
    for r in (rb, rc):  # where the profile of a roof breaks along the line (two of its planes cross)
        if r is None:
            continue
        ps = rets[r]["planos"]
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                (a1, b1, c1, *_), (a2, b2, c2, *_) = ps[i], ps[j]
                # along the line: plane value = A s + B; equal where (A1 - A2) s = B2 - B1
                A1, B1 = (a1, b1 * fixo + c1) if face["o"] == "y" else (b1, a1 * fixo + c1)
                A2, B2 = (a2, b2 * fixo + c2) if face["o"] == "y" else (b2, a2 * fixo + c2)
                if abs(A1 - A2) > 1e-9:
                    s = (B2 - B1) / (A1 - A2)
                    if s0 < s < s1:
                        cortes.add(s)
    out = []
    cortes = sorted(cortes)
    for sa, sb in zip(cortes, cortes[1:]):
        if sb - sa < 1e-4:
            continue
        za_u, zb_u = zr(rc, sa), zr(rc, sb)
        if rb is not None:
            za_l, zb_l = zr(rb, sa) + folga_baixo, zr(rb, sb) + folga_baixo
        else:
            za_l = zb_l = ze
        if max(za_u - za_l, zb_u - zb_l) <= 1e-3:
            continue
        da, db = za_u - za_l, zb_u - zb_l
        if da < 0 or db < 0:  # the two profiles cross inside the strip: keep the part where the upper roof is higher
            m = sa + (sb - sa) * da / (da - db)
            zm = za_l + (zb_l - za_l) * (m - sa) / (sb - sa)
            if da < 0:
                sa, za_l, za_u = m, zm, zm
            else:
                sb, zb_l, zb_u = m, zm, zm
        out.append([(sa, za_l), (sb, zb_l), (sb, zb_u), (sa, za_u)])
    return out


def clip_telhado(poly, face, z_cume, casa, w=0.0):
    """Keep the part of a face polygon (s, z) below the roof-parallel plane z = z_cume - tan * |y - y_ridge|."""
    if face["o"] == "y":  # face along x: y is fixed
        y = face["c"] + face["n"] * w
        return [clip_box(poly, v1=z_cume - casa.tn * abs(y - casa.yr))]
    out = []
    for part, lado in ((clip_box(poly, None, casa.yr), -1), (clip_box(poly, casa.yr, None), 1)):
        if len(part) < 3:
            continue
        # south of the ridge z <= z_cume - tn (yr - s); north z <= z_cume - tn (s - yr)
        q = clip_semiplano(part, -casa.tn * -lado, 1.0, z_cume + casa.tn * casa.yr * lado)
        if len(q) >= 3 and area(q) > 1e-6:
            out.append(q)
    return out


# ============================================================================ plan grid (rooms, facades)
class Grelha:
    """Coordinate grid built from wall footprints: covered cells = walls, free cells = rooms / outside."""

    def __init__(self, rects, limites, tol=0.012):
        X0, X1, Y0, Y1 = limites
        self.xs, mx = self._snap([X0, X1] + [v for r in rects for v in r[:2]], tol)
        self.ys, my = self._snap([Y0, Y1] + [v for r in rects for v in r[2:]], tol)
        self.rects = [(mx(r[0]), mx(r[1]), my(r[2]), my(r[3])) for r in rects]
        self.nx, self.ny = len(self.xs) - 1, len(self.ys) - 1
        self.cheio = [[False] * self.ny for _ in range(self.nx)]
        for i in range(self.nx):
            cx = (self.xs[i] + self.xs[i + 1]) / 2
            for j in range(self.ny):
                cy = (self.ys[j] + self.ys[j + 1]) / 2
                self.cheio[i][j] = any(r[0] < cx < r[1] and r[2] < cy < r[3] for r in self.rects)

    @staticmethod
    def _snap(vals, tol):
        clusters = []
        for v in sorted(vals):
            if clusters and v - clusters[-1][-1] <= tol:
                clusters[-1].append(v)
            else:
                clusters.append([v])
        reps, mapa = [], {}
        for c in clusters:
            cnt = {}
            for v in c:
                cnt[round(v, 4)] = cnt.get(round(v, 4), 0) + 1
            media = sum(c) / len(c)
            rep = max(cnt.items(), key=lambda kv: (kv[1], -abs(kv[0] - media)))[0]
            reps.append(rep)
            for v in c:
                mapa[round(v, 7)] = rep
        return reps, (lambda v: mapa[round(v, 7)])

    def celula(self, x, y):
        return bisect.bisect_right(self.xs, x) - 1, bisect.bisect_right(self.ys, y) - 1

    def livre(self, i, j):
        return 0 <= i < self.nx and 0 <= j < self.ny and not self.cheio[i][j]

    def componentes(self):
        visto, comps = set(), []
        for i in range(self.nx):
            for j in range(self.ny):
                if self.cheio[i][j] or (i, j) in visto:
                    continue
                comp, fila = [], deque([(i, j)])
                visto.add((i, j))
                while fila:
                    a, b = fila.popleft()
                    comp.append((a, b))
                    for c, d in ((a - 1, b), (a + 1, b), (a, b - 1), (a, b + 1)):
                        if self.livre(c, d) and (c, d) not in visto:
                            visto.add((c, d))
                            fila.append((c, d))
                comps.append(comp)
        return comps

    def area(self, comp):
        return sum((self.xs[i + 1] - self.xs[i]) * (self.ys[j + 1] - self.ys[j]) for i, j in comp)

    def centro(self, comp):
        a = self.area(comp)
        cx = sum((self.xs[i + 1] - self.xs[i]) * (self.ys[j + 1] - self.ys[j]) * (self.xs[i] + self.xs[i + 1]) / 2
                 for i, j in comp) / a
        cy = sum((self.xs[i + 1] - self.xs[i]) * (self.ys[j + 1] - self.ys[j]) * (self.ys[j] + self.ys[j + 1]) / 2
                 for i, j in comp) / a
        return cx, cy

    def faces(self, comp):
        """Boundary faces between the free region `comp` and walls.

        Face: o = "y" (lies on the line y = c, runs along x) or "x"; n = +1/-1 side of the free region;
        s0/s1 = extent along the face; ka/kb = corner at start/end (+1 inside corner, -1 wall end).
        """
        runs = {}
        for i, j in comp:
            if i > 0 and self.cheio[i - 1][j]:
                runs.setdefault(("x", i, 1), []).append(j)
            if i < self.nx - 1 and self.cheio[i + 1][j]:
                runs.setdefault(("x", i + 1, -1), []).append(j)
            if j > 0 and self.cheio[i][j - 1]:
                runs.setdefault(("y", j, 1), []).append(i)
            if j < self.ny - 1 and self.cheio[i][j + 1]:
                runs.setdefault(("y", j + 1, -1), []).append(i)
        out = []
        for (o, k, n), idx in sorted(runs.items()):
            idx.sort()
            ini = ant = idx[0]
            for v in idx[1:] + [None]:
                if v is not None and v == ant + 1:
                    ant = v
                    continue
                out.append(self._face(o, k, n, ini, ant + 1))
                if v is not None:
                    ini = ant = v
        return out

    def _face(self, o, k, n, a, b):
        r = k if n > 0 else k - 1  # row / column of the free side
        if o == "y":
            c, s0, s1 = self.ys[k], self.xs[a], self.xs[b]
            ka = -1 if self.livre(a - 1, r) else 1
            kb = -1 if self.livre(b, r) else 1
        else:
            c, s0, s1 = self.xs[k], self.ys[a], self.ys[b]
            ka = -1 if self.livre(r, a - 1) else 1
            kb = -1 if self.livre(r, b) else 1
        return {"o": o, "c": c, "n": n, "s0": s0, "s1": s1, "ka": ka, "kb": kb}

    def retangulos(self, comp, recuo=0.0):
        """Plan rectangles of a free region, inset by `recuo` from the walls."""
        rs = []
        for i, j in comp:
            x0 = self.xs[i] + (recuo if i > 0 and self.cheio[i - 1][j] else 0)
            x1 = self.xs[i + 1] - (recuo if i < self.nx - 1 and self.cheio[i + 1][j] else 0)
            y0 = self.ys[j] + (recuo if j > 0 and self.cheio[i][j - 1] else 0)
            y1 = self.ys[j + 1] - (recuo if j < self.ny - 1 and self.cheio[i][j + 1] else 0)
            if x1 - x0 > 1e-4 and y1 - y0 > 1e-4:
                rs.append([x0, x1, y0, y1])
        return fundir_retangulos(rs)


def fundir_retangulos(rs, eps=1e-6):
    rs = [list(r) for r in rs]
    mudou = True
    while mudou:
        mudou = False
        for eixo in (0, 1):
            a, b = (0, 1) if eixo == 0 else (2, 3)   # merge along this axis
            c, d = (2, 3) if eixo == 0 else (0, 1)   # the other extents must match
            rs.sort(key=lambda r: (round(r[c], 6), round(r[d], 6), r[a]))
            out = []
            for r in rs:
                if out and abs(out[-1][c] - r[c]) < eps and abs(out[-1][d] - r[d]) < eps and abs(out[-1][b] - r[a]) < eps:
                    out[-1][b] = r[b]
                    mudou = True
                else:
                    out.append(r)
            rs = out
    return rs


def menos_retangulo(r, b):
    x0, x1, y0, y1 = r
    bx0, bx1, by0, by1 = b
    if bx0 >= x1 or bx1 <= x0 or by0 >= y1 or by1 <= y0:
        return [r]
    out = []
    if bx0 > x0:
        out.append([x0, bx0, y0, y1])
    if bx1 < x1:
        out.append([bx1, x1, y0, y1])
    cx0, cx1 = max(x0, bx0), min(x1, bx1)
    if by0 > y0:
        out.append([cx0, cx1, y0, by0])
    if by1 < y1:
        out.append([cx0, cx1, by1, y1])
    return out


# ============================================================================ faces helpers
def extensao(face, w0, w1):
    """Face extent for a layer between offsets w0..w1 (butt joints: faces along x run through)."""
    prio = face["o"] == "y"

    def sel(k):
        return w0 if (k > 0) == prio else w1

    return face["s0"] + face["ka"] * sel(face["ka"]), face["s1"] - face["kb"] * sel(face["kb"])


def ponto(face, s, z, w):
    if face["o"] == "y":
        return (s, face["c"] + face["n"] * w, z)
    return (face["c"] + face["n"] * w, s, z)


def prisma_face(face, poly, w0, w1):
    d = face["n"] * (w1 - w0)
    return prisma([ponto(face, s, z, w0) for s, z in poly], (0, d, 0) if face["o"] == "y" else (d, 0, 0))


def paineis_da_face(face, paineis, tol=0.02, aparar=True):
    """Wall modules behind a face -> [(panel, s_lo, s_hi)] sorted along the face (overlaps trimmed
    unless `aparar` is False: facades hold the modules of both floors)."""
    out = []
    for P in paineis:
        x0, x1, y0, y1 = P.pegada()
        if face["o"] == "y":
            borda, lo, hi = (y1 if face["n"] > 0 else y0), max(face["s0"], x0), min(face["s1"], x1)
        else:
            borda, lo, hi = (x1 if face["n"] > 0 else x0), max(face["s0"], y0), min(face["s1"], y1)
        if abs(borda - face["c"]) <= tol and hi - lo > 0.01:
            out.append([P, lo, hi])
    out.sort(key=lambda t: t[1])
    for a, b in zip(out, out[1:]) if aparar else ():
        if b[1] < a[2]:
            b[1] = a[2]
    return [t for t in out if t[2] - t[1] > 0.005]


def aberturas_face(pf):
    rects = []
    for P, lo, hi in pf:
        for u0, u1, v0, v1, _k in P.aberturas:
            a, b = sorted((P.s_de_u(u0), P.s_de_u(u1)))
            a, b = max(a, lo), min(b, hi)
            if b - a > 0.05:
                rects.append((a, b, P.oz + v0, P.oz + v1))
    return rects


def contorno_face(P):
    """Panel frame outline mapped to face coordinates (s, z)."""
    return clean([(P.s_de_u(u), P.oz + v) for u, v in P.contorno])


def estender(poly, lo, hi):
    """Stretch a convex outline horizontally so it reaches lo..hi (butt-joint extensions at wall ends)."""
    smin = min(p[0] for p in poly)
    smax = max(p[0] for p in poly)
    return [(min(lo, s) if abs(s - smin) < 1e-6 else max(hi, s) if abs(s - smax) < 1e-6 else s, z) for s, z in poly]


# ============================================================================ output container
class Saida:
    def __init__(self):
        self.colecoes, self.objetos, self.etiquetas = [], [], []

    def colecao(self, cid, nome, visivel=True):
        self.colecoes.append({"id": cid, "nome": f"{cid} {nome}", "visivel": visivel})

    def objeto(self, nome, cid, material, pecas, props=None, pai=None):
        if pecas:
            self.objetos.append({"nome": nome, "colecao": cid, "material": material, "pecas": pecas,
                                 "props": props or {}, "pai": pai})


def props_camada(cam, **kw):
    p = {"camada": cam.get("nome", ""), "produto": cam.get("produto", "")}
    for k in ("unidade", "area_unidade_m2", "comprimento_unidade_m", "desperdicio"):
        if k in cam:
            p[k] = cam[k]
    if "placa" in cam and "area_unidade_m2" not in cam:
        p["unidade"] = f"placa {round(cam['placa'][0] * 1000)}x{round(cam['placa'][1] * 1000)}"
        p["area_unidade_m2"] = round(cam["placa"][0] * cam["placa"][1], 4)
    p.update({k: (round(v, 3) if isinstance(v, float) else v) for k, v in kw.items()})
    return p


# ============================================================================ layout of one layer on a face
def dispor(cam, face, regioes, aberturas, w0, w1, s0, z0, cortes=()):
    """Pieces of one layer on one face. Returns (pieces, totals dict). `cortes`: (s0, s1, z0, z1) zones the
    battens stop at without framing them (downpipes in the cavity)."""
    tipo = cam.get("tipo", "continuo")
    pecas, tot = [], {"area": 0.0, "comp": 0.0, "n": 0}
    junta = cam.get("junta", 0.0)
    if tipo in ("placas", "continuo"):
        for reg in regioes:
            for pc in subtrair_retangulos(reg, aberturas):
                cells = dividir_grelha(pc, *(cam["placa"] if tipo == "placas" else (None, None)), u0=s0, v0=z0,
                                       desfasado=cam.get("desfasado", False))
                for c in cells:
                    tot["area"] += area(c)
                    tot["n"] += 1
                    pecas.append(prisma_face(face, encolher(c, junta / 2), w0, w1))
        return pecas, tot
    if tipo == "ripas":
        lg, esp = cam["largura"], cam["espacamento"]
        cv = cam.get("contorno_vaos")  # battens framing every opening (user 2026-10-16)
        if cam["direcao"] == "vertical":
            smin = min(p[0] for r in regioes for p in r)
            smax = max(p[0] for r in regioes for p in r)
            jambas = [x for a, b, _z0, _z1 in aberturas for x in (a - lg, b)]
            pos, s = [], smin
            while s < smax - lg + 1e-9:
                pos.append(s)
                s += esp
            pos.append(smax - lg)
            pos = [p for p in pos if all(abs(p - j) > 0.1 for j in jambas) or p in (smin, smax - lg)] + jambas
            unicos = []
            for p in sorted(pos):
                if not unicos or p - unicos[-1] > 0.005:
                    unicos.append(p)
            faixas = [(p, p + lg, None) for p in unicos]
        else:
            zmin = min(p[1] for r in regioes for p in r)
            zmax = max(p[1] for r in regioes for p in r)
            faixas, z = [], zmin
            while z < zmax - lg + 1e-9:
                faixas.append((None, None, z))
                z += esp
        # outer box of the battens round each opening (jambs, head, sill if any): a course that would touch it
        # stops at the jambs over its whole height (no slivers)
        molduras = []
        for a, b, za, zb in aberturas:
            chao = za <= z0 + 0.05
            if cv:
                aa, bb = (a - lg, b + lg) if cv.get("ombreiras", True) else (a, b)
                molduras.append((aa, bb, za - (lg if cv.get("peitoril") and not chao else 0.0),
                                 zb + (lg if cv.get("padieira", True) else 0.0)))
            else:
                molduras.append((a, b, za - 0.08, zb + 0.08))
        # a vertical batten at both ends of the face (the corners of the house, on both faces; user 2026-10-16)
        cantos_v = []
        if cv and cv.get("cantos") and cam["direcao"] == "horizontal":
            for reg in regioes:
                smin_, smax_ = min(p[0] for p in reg), max(p[0] for p in reg)
                cantos_v += [(smin_, smin_ + lg), (smax_ - lg, smax_)]
        for fa, fb, z in faixas:
            if z is None:
                zonas = list(aberturas) + list(cortes)
            else:
                zonas = [(aa, bb, z - 1.0, z + lg + 1.0) for aa, bb, za_, zb_ in list(molduras) + list(cortes)
                         if z < zb_ + 0.02 and z + lg > za_ - 0.02] + [(a_, b_, z - 1.0, z + lg + 1.0) for a_, b_ in cantos_v]
            for reg in regioes:
                band = clip_box(reg, fa, fb) if z is None else clip_box(reg, v0=z, v1=z + lg)
                if len(band) < 3:
                    continue
                for pc in subtrair_retangulos(band, zonas):
                    ext = (max(p[1] for p in pc) - min(p[1] for p in pc)) if z is None else \
                        (max(p[0] for p in pc) - min(p[0] for p in pc))
                    if ext < 0.05:
                        continue
                    tot["comp"] += ext
                    tot["n"] += 1
                    pecas.append(prisma_face(face, pc, w0, w1))
        for a_, b_ in cantos_v:
            for reg in regioes:
                pc = clip_box(reg, a_, b_)
                if len(pc) >= 3 and area(pc) > 1e-5:
                    tot["comp"] += max(q[1] for q in pc) - min(q[1] for q in pc)
                    tot["n"] += 1
                    pecas.append(prisma_face(face, pc, w0, w1))
        if cam["direcao"] == "horizontal":
            for a, b, za, zb in aberturas:
                chao = za <= z0 + 0.05
                if cv:  # two jambs and the head (and the sill when set): the battens go round the opening
                    aa, bb = (a - lg, b + lg) if cv.get("ombreiras", True) else (a, b)
                    pv = [(aa, bb, zb, zb + lg)] if cv.get("padieira", True) else []
                    if cv.get("peitoril") and not chao:
                        pv.append((aa, bb, za - lg, za))
                    if cv.get("ombreiras", True):
                        pv += [(a - lg, a, za, zb), (b, b + lg, za, zb)]
                else:  # heads and sills
                    pv = [(a, b, zb, zb + lg)] + ([(a, b, za - lg, za)] if not chao else [])
                for s0_, s1_, v0_, v1_ in pv:
                    for reg in regioes:
                        pc = clip_box(reg, s0_, s1_, v0_, v1_)
                        if len(pc) >= 3 and area(pc) > 1e-5:
                            tot["comp"] += max(s1_ - s0_, v1_ - v0_)
                            tot["n"] += 1
                            pecas.append(prisma_face(face, pc, w0, w1))
        return pecas, tot
    if tipo == "tabuas":
        lg, cmax = cam["largura"], cam.get("comprimento_max", 4.0)
        smin = min(p[0] for r in regioes for p in r)
        smax = max(p[0] for r in regioes for p in r)
        s = smin
        while s < smax - 0.01:
            for reg in regioes:
                band = clip_box(reg, s, min(s + lg - junta, smax))
                if len(band) < 3:
                    continue
                for pc in subtrair_retangulos(band, aberturas):
                    for c in dividir_grelha(pc, None, cmax, v0=z0):
                        comp = max(p[1] for p in c) - min(p[1] for p in c)
                        if comp < 0.03:
                            continue
                        tot["area"] += area(c) * lg / (lg - junta)
                        tot["comp"] += comp
                        tot["n"] += 1
                        pecas.append(prisma_face(face, c, w0, w1))
            s += lg
        return pecas, tot
    raise ValueError(f"unknown layer type {tipo}")


# ============================================================================ generators
def nome_fachada(face, casa):
    if face["o"] == "y":
        return "Sul" if face["n"] < 0 else "Norte"
    return "Oeste" if face["n"] < 0 else "Este"


def degraus(f, s0, s1, z_base):
    """Facade outline of a parapet house: along the face, the top of the highest module behind each stretch."""
    pf = [(lo, hi, P.oz + P.hf) for P, lo, hi in f["pf"]]
    cortes = sorted({s0, s1} | {v for lo, hi, _t in pf for v in (lo, hi) if s0 < v < s1})
    topo = []
    for a, b in zip(cortes, cortes[1:]):
        m = (a + b) / 2
        t = [z for lo, hi, z in pf if lo - 1e-6 <= m <= hi + 1e-6]
        if not t:  # end extensions beyond the modules (outside corners): the highest of the nearest modules
            dist = [min(abs(m - lo), abs(m - hi)) for lo, hi, _z in pf]
            t = [z for (_lo, _hi, z), d in zip(pf, dist) if d <= min(dist) + 1e-6]
        z = max(t)
        if topo and abs(topo[-1][2] - z) < 1e-6:
            topo[-1][1] = b
        else:
            topo.append([a, b, z])
    poly = [(s0, z_base), (s1, z_base)]
    for a, b, z in reversed(topo):
        poly += [(b, z), (a, z)]
    return clean(poly)


def exterior(casa, S, out, resumo):
    E = S["exterior"]
    cob = S["cobertura"]
    z_base = E.get("cota_base", 0.0)
    z_cob = casa.z_cob_cume(S)
    pe = [P for P in casa.paineis if P.tipo == "PE"]
    L, D = casa.L, casa.D
    grid = Grelha([P.pegada() for P in pe], (-1.0, L + 1.0, -1.0, D + 1.0))
    comp = next(c for c in grid.componentes() if (0, 0) in c)
    faces = grid.faces(comp)
    usados = {}
    for f in faces:
        nm = nome_fachada(f, casa)
        usados[nm] = usados.get(nm, 0) + 1
        f["nome"] = nm if usados[nm] == 1 else f"{nm} {usados[nm]}"
        f["pf"] = paineis_da_face(f, pe, aparar=False)
        f["aberturas"] = aberturas_face(f["pf"])
    for k, e in enumerate((casa.G["cobertura"].get("encostos") or []) if casa.faces else [], 1):
        # a gable over a lower roof: clad like the façade, above that roof (telhado_estrutura.py "encostos")
        faces.append({"o": e["o"], "c": e["c"], "n": e["n"], "s0": e["s0"], "s1": e["s1"], "ka": 0, "kb": 0,
                      "nome": f"Encosto {k}", "pf": [], "aberturas": [], "encosto": e})
    casa.fachadas = faces
    pn_ = cob["painel"]
    folga_enc = (pn_["nucleo"] + pn_.get("relevo", 0.0)) / max(casa.ct, 1e-6) + 0.01
    tubos = tubos_queda(casa, S) if casa.platibanda else []

    out.colecao("2", "Paredes | camadas exteriores")
    pilha = [("2.1", E["osb"]), ("2.2", E["membrana"])]
    w_comum = E["osb"]["espessura"] + E["membrana"]["espessura"]
    for cid, cam in pilha:
        out.colecao(cid, cam["nome"])
    visivel = E.get("opcao_visivel", "A")
    for k, (letra, op) in enumerate(sorted(E["opcoes"].items()), 3):
        cid = f"2.{k}"
        out.colecao(cid, f"Opção {letra} | {op['nome']}", visivel=(letra == visivel))
        w = w_comum
        for m, cam in enumerate(op["camadas"], 1):
            sub = f"{cid}.{m}"
            cam = dict(cam, _w0=w, nome=f"{cam['nome']} ({letra})")  # object names must be unique
            out.colecao(sub, cam["nome"])
            pilha.append((sub, cam))
            w += cam["espessura"]
    w = 0.0
    for cid, cam in pilha:
        w0 = cam.get("_w0", w)
        w1 = w0 + cam["espessura"]
        if "_w0" not in cam:
            w = w1
        tot_c = {"area": 0.0, "comp": 0.0, "n": 0}
        for f in faces:
            s0, s1 = extensao(f, w0, w1)
            if casa.platibanda:  # up to the top of the walls behind (parapet, or the roof edge on the gutter sides)
                regioes = [degraus(f, s0, s1, z_base)]
            elif casa.faces and f.get("encosto"):  # a gable over a lower roof: between the two roofs, on past its
                s0, s1 = s0 - w1, s1 + w1          # ends by the layer's depth (to meet the façade beside it)
                regioes = entre_telhados(s0, s1, f, casa, w1, folga_enc)
            elif casa.faces:  # under the exposed roof's slopes (gables included)
                regioes = sob_faces([(s0, z_base), (s1, z_base), (s1, z_cob + 5), (s0, z_cob + 5)], f, casa, w1)
            else:
                rect = [(s0, z_base), (s1, z_base), (s1, z_cob + 5), (s0, z_cob + 5)]
                regioes = clip_telhado(rect, f, z_cob, casa, w1)
            cortes = [(tq["x"][0] - 0.01, tq["x"][1] + 0.01, tq["z"][0] - 0.01, tq["z"][1]) for tq in tubos
                      if f["o"] == "y" and abs(f["c"] - tq["y_fora"]) < 0.01 and f["n"] == tq["n"]] \
                if cam.get("tipo") == "ripas" else []
            vaos = f["aberturas"]
            for pf in (casa.G.get("pergola") or {}).get("faces", []):  # the boards stop round the pergola's
                # ledgers and beam ends
                if cam.get("tipo") == "tabuas" and f["o"] == "y" and abs(f["c"] - pf["y_fora"]) < 0.01 and f["n"] == pf["n"]:
                    vaos = list(vaos) + [tuple(c) for c in pf["cortes"]]
            pecas, tot = dispor(cam, f, regioes, vaos, w0, w1, s0, z_base, cortes)
            for k2 in tot_c:
                tot_c[k2] += tot[k2]
            out.objeto(f"{cam['nome']} | Fachada {f['nome']}", cid, cam["material"], pecas,
                       props_camada(cam, area_m2=tot["area"], comprimento_m=tot["comp"], pecas=tot["n"],
                                    fachada=f["nome"], espessura_m=cam["espessura"]))
        resumo.append((cid, cam["nome"], tot_c))


def isolamento(casa, S, out, resumo):
    la = S["interior"]["la_mineral"]
    out.colecao("3", "Paredes | camadas interiores")
    out.colecao("3.1", la["nome"])
    e = la["espessura"]
    fachada = {id(P) for f in casa.fachadas for P, _a, _b in f["pf"]}
    tot = {"area": 0.0, "comp": 0.0, "n": 0}
    sotao_frio = bool(S.get("tetos", {}).get("la"))  # wool on the top ceiling: the attic is outside
    for P in casa.paineis:
        ext = id(P) in fachada
        if P.fantasma:  # parapet part of a full-height module: its wool is in the module
            continue
        if not ext and not la.get("paredes_interiores", True):
            continue
        if sotao_frio and P.piso == 2 and not casa.platibanda:  # gable triangles of a cold attic: no wool
            continue
        ee = min(e if ext else la.get("espessura_interior", e), P.t)
        wa = (-P.t / 2 if P.fora < 0 else P.t / 2 - ee) if ext else -ee / 2
        pecas, a = [], 0.0
        for q in P.cavidades():
            a += area(q)
            pecas.append(prisma([P.mundo(u, v, wa) for u, v in q], (-P.uy * ee, P.ux * ee, 0.0)))
        tot["area"] += a
        tot["n"] += len(pecas)
        out.objeto(f"Lã mineral | {P.nome}", "3.1", la["material"], pecas,
                   props_camada(la, area_m2=a, volume_m3=a * ee, pecas=len(pecas), painel=P.nome,
                                espessura_m=ee), pai=P.nome)
    resumo.append(("3.1", la["nome"], tot))


def fechos(rects, porta_max=1.0, vazio_max=0.38, excluir=()):
    """Virtual wall pieces used only to split rooms: doorways (gap <= porta_max between a wall end and the
    next wall on its line) and narrow voids (gap < vazio_max between parallel walls, e.g. ducts).
    Heuristic (the structural drawings have no doors): pieces overlapping `excluir` (stair void) are dropped.
    They carry no panel, so no lining is generated on them."""
    out = []
    for i, (x0, x1, y0, y1) in enumerate(rects):
        ew = x1 - x0 >= y1 - y0
        for sent in (-1, 1):
            if ew:
                cand = [(r[0] - x1) if sent > 0 else (x0 - r[1]) for k, r in enumerate(rects) if k != i
                        and r[2] < y1 - 0.01 and r[3] > y0 + 0.01 and ((r[0] >= x1 - 0.01) if sent > 0 else (r[1] <= x0 + 0.01))]
            else:
                cand = [(r[2] - y1) if sent > 0 else (y0 - r[3]) for k, r in enumerate(rects) if k != i
                        and r[0] < x1 - 0.01 and r[1] > x0 + 0.01 and ((r[2] >= y1 - 0.01) if sent > 0 else (r[3] <= y0 + 0.01))]
            g = min(cand, default=None)
            if g is not None and 0.05 < g <= porta_max:
                if ew:
                    out.append((x1, x1 + g, y0, y1) if sent > 0 else (x0 - g, x0, y0, y1))
                else:
                    out.append((x0, x1, y1, y1 + g) if sent > 0 else (x0, x1, y0 - g, y0))
        for k, r in enumerate(rects[i + 1:], i + 1):
            if ew == (r[1] - r[0] >= r[3] - r[2]):
                if ew:
                    ov0, ov1 = max(x0, r[0]), min(x1, r[1])
                    lo, hi = (y1, r[2]) if r[2] >= y1 else (r[3], y0)
                    if ov1 - ov0 >= 0.1 and 0.01 < hi - lo < vazio_max:
                        out.append((ov0, ov1, lo, hi))
                else:
                    ov0, ov1 = max(y0, r[2]), min(y1, r[3])
                    lo, hi = (x1, r[0]) if r[0] >= x1 else (r[1], x0)
                    if ov1 - ov0 >= 0.1 and 0.01 < hi - lo < vazio_max:
                        out.append((lo, hi, ov0, ov1))
    return [r for r in out if not any(r[0] < e[1] and r[1] > e[0] and r[2] < e[3] and r[3] > e[2] for e in excluir)]


def fechos_salas(rects, limites, cfg, excluir=()):
    """Virtual closures that split the free space into rooms (`fechos`), without the doorways that would cut off
    a tiny space. Returns (closures, grid). Also used by estrutura_dc.py to find the doorways between modules."""
    virt = fechos(rects, cfg.get("porta_max", 1.0), cfg.get("vazio_max", 0.38), excluir)
    grid = Grelha(rects + virt, limites)
    # a virtual doorway that cuts off a tiny space (< area_espaco) was not a door: drop the one towards the
    # smallest neighbouring space (usually the corridor) and recompute
    minimo = cfg.get("area_espaco", 0.5)
    comps = grid.componentes()
    dono = {cell: k for k, c in enumerate(comps) for cell in c}
    retirar = []
    for k, c in enumerate(comps):
        if grid.area(c) >= minimo:
            continue
        x0, x1 = grid.xs[min(i for i, _j in c)], grid.xs[max(i for i, _j in c) + 1]
        y0, y1 = grid.ys[min(j for _i, j in c)], grid.ys[max(j for _i, j in c) + 1]
        opcoes = []
        for v in virt:
            if not (v[0] <= x1 + 0.02 and v[1] >= x0 - 0.02 and v[2] <= y1 + 0.02 and v[3] >= y0 - 0.02):
                continue
            xm, ym = (v[0] + v[1]) / 2, (v[2] + v[3]) / 2
            lados = ((xm, v[2] - 0.02), (xm, v[3] + 0.02)) if v[1] - v[0] >= v[3] - v[2] else                 ((v[0] - 0.02, ym), (v[1] + 0.02, ym))
            for q in lados:
                viz = dono.get(grid.celula(*q))
                if viz is not None and viz != k:
                    opcoes.append((grid.area(comps[viz]), v))
        if opcoes:
            retirar.append(min(opcoes)[1])
    if retirar:
        virt = [v for v in virt if v not in retirar]
        grid = Grelha(rects + virt, limites)
    return virt, grid


def portas_virtuais(virt, porta_max=1.05, espessura_max=0.12, vao_min=0.5):
    """Doorway pieces among the virtual closures (thin and door-wide; ducts excluded), duplicates merged."""
    out = []
    for v in virt:
        w, h = v[1] - v[0], v[3] - v[2]
        if min(w, h) > espessura_max or not vao_min <= max(w, h) <= porta_max + 0.01:
            continue
        if any(v[0] < o[1] - 0.01 and v[1] > o[0] + 0.01 and v[2] < o[3] - 0.01 and v[3] > o[2] + 0.01 for o in out):
            continue
        out.append(v)
    return out


def salas(casa, piso, S):
    cfg = S.get("divisoes", {})
    pan = [P for P in casa.paineis if P.piso == piso]
    rects = [P.pegada() for P in pan]
    ab = casa.G["pavimento"].get("abertura_escada")
    abertas = [a["rect"] for a in cfg.get("passagens_abertas", []) if a["piso"] == piso]  # open passages
    virt, grid = fechos_salas(rects, (0.0, casa.L, 0.0, casa.D), cfg, ([ab] if ab and piso == 1 else []) + abertas)
    # a free space touching the bounding box is outside (e.g. the notch of an L-shaped house)
    comps = [c for c in grid.componentes() if grid.area(c) >= cfg.get("area_min", 0.1)
             and not any(i in (0, grid.nx - 1) or j in (0, grid.ny - 1) for i, j in c)]
    comps.sort(key=lambda c: (round(grid.centro(c)[1] * 2) / 2, grid.centro(c)[0]))
    return grid, pan, [(f"P{piso}.{k:02d}", c) for k, c in enumerate(comps, 1)]


def interior(casa, S, out, resumo):
    I, T = S["interior"], S["tetos"]
    osb, acab = I["osb"], I["acabamento"]
    teto_plano = T["suspensao"]["folga"] + T["perfis"]["altura"] + T["acabamento"]["espessura"]
    teto = T["perfis"]["altura"] + T["acabamento"]["espessura"]  # sloped ceiling under rafters
    fin0 = S["pavimentos"]["piso0"]["acabado_z"]
    fin_e = S["pavimentos"]["acabamento"]["espessura"]
    out.colecao("3.2", osb["nome"])
    out.colecao("3.3", acab["nome"])
    camadas = [("3.2", osb, 0.0, osb["espessura"]), ("3.3", acab, osb["espessura"], osb["espessura"] + acab["espessura"])]
    totais = {cid: {"area": 0.0, "comp": 0.0, "n": 0} for cid, *_ in camadas}
    # the client's finish on a face of an interior wall (configurator: wood, tiles) instead of the Pladur
    alt = {k: v for k, v in (I.get("acabamento_opcoes") or {}).items() if isinstance(v, dict)}
    cid_alt = {k: f"3.{4 + i}" for i, k in enumerate(sorted(alt))}
    usados_alt = {}

    def camadas_alt(k, w0):
        """The layers of a chosen finish, each with its depth off the frame (a list: battens, counter-battens, boards)."""
        out_, w = [], w0
        for cam in alt[k].get("camadas") or [alt[k]]:
            out_.append((cam, w, w + cam["espessura"]))
            w += cam["espessura"]
        return out_

    def cam_da_face(P, f):
        if not P.acabamentos:
            return None
        lado = ("norte" if f["n"] > 0 else "sul") if f["o"] == "y" else ("nascente" if f["n"] > 0 else "poente")
        k = P.acabamentos.get(lado)
        return k if k in alt else None

    casa.salas = {}
    for piso in casa.pisos:
        grid, pan, lista = salas(casa, piso, S)
        casa.salas[piso] = (grid, lista)
        z_bot = fin0 - fin_e if piso == 0 else casa.nv["piso1_interior"]
        for nome, comp in lista:
            faces = grid.faces(comp)
            for f in faces:
                f["pf"] = paineis_da_face(f, pan)
                f["aberturas"] = aberturas_face(f["pf"])
            for cid, cam0, w0, w1_0 in camadas:
                pecas, tot = [], {"area": 0.0, "comp": 0.0, "n": 0}
                pecas_alt = {}  # (finish id, its layer) -> (pieces, totals)

                def assentar(f, P, idx, pf, lo, hi, cam, wa, wb):
                    """One layer of the lining on the part of face f along panel P (wa..wb off the frame)."""
                    s0, s1 = extensao(f, wa, wb)
                    lo2 = s0 if idx == 0 and lo <= f["s0"] + 0.02 else max(lo, s0)
                    hi2 = s1 if idx == len(pf) - 1 and hi >= f["s1"] - 0.02 else min(hi, s1)
                    if hi2 - lo2 < 0.005:
                        return None, None
                    reg = clip_box(estender(contorno_face(P), lo2, hi2), lo2, hi2, z_bot, None)
                    if len(reg) < 3:
                        return None, None
                    if piso in casa.teto:
                        topo = (min(casa.teto[piso], casa.nv.get(f"topo_forro_piso{piso}", 9e9)) if cid != "3.3"
                                else casa.teto[piso] - teto_plano)
                        zt = max(z for _s, z in reg)
                        if topo > zt + 1e-4 and zt >= casa.teto[piso] - 0.15:
                            # the module stops under the levelling / tie beam: the lining goes on up to the
                            # false ceiling (Pladur) or to the beams (OSB, which also covers the beam)
                            reg = [(s_, topo if z > zt - 1e-4 else z) for s_, z in reg]
                        regioes = [clip_box(reg, v1=topo)]
                    else:
                        off = casa.dz + (teto / casa.ct if cid == "3.3" else 0.0)
                        regioes = clip_telhado(reg, f, casa.zr - off, casa, (wa + wb) / 2)
                    regioes = [r for r in regioes if len(r) >= 3 and area(r) > 1e-5]
                    return dispor(cam, f, regioes, f["aberturas"], wa, wb, s0, z_bot)

                for f in faces:
                    pf = f["pf"]
                    for idx, (P, lo, hi) in enumerate(pf):
                        k_alt = cam_da_face(P, f) if cid == "3.3" else None
                        if not k_alt:
                            p2, t2 = assentar(f, P, idx, pf, lo, hi, cam0, w0, w1_0)
                            if p2 is not None:
                                pecas += p2
                                for k in tot:
                                    tot[k] += t2[k]
                            continue
                        for jj, (cam, wa, wb) in enumerate(camadas_alt(k_alt, w0)):
                            p2, t2 = assentar(f, P, idx, pf, lo, hi, cam, wa, wb)
                            if p2 is None:
                                continue
                            pa, ta = pecas_alt.setdefault((k_alt, jj), ([], {"area": 0.0, "comp": 0.0, "n": 0}))
                            pa += p2
                            for k in ta:
                                ta[k] += t2[k]
                for k in tot:
                    totais[cid][k] += tot[k]
                out.objeto(f"{cam0['nome']} | {nome}", cid, cam0["material"], pecas,
                           props_camada(cam0, area_m2=tot["area"], pecas=tot["n"], divisao=nome, piso=piso,
                                        espessura_m=cam0["espessura"]))
                for (k_alt, jj), (pa, ta) in sorted(pecas_alt.items()):
                    ca = camadas_alt(k_alt, w0)[jj][0]
                    varias = len(camadas_alt(k_alt, w0)) > 1
                    c_id = f"{cid_alt[k_alt]}.{jj + 1}" if varias else cid_alt[k_alt]
                    if (k_alt, jj) not in usados_alt:
                        if varias and not any(k == k_alt for k, _ in usados_alt):
                            out.colecao(cid_alt[k_alt], alt[k_alt]["nome"])
                        out.colecao(c_id, ca["nome"])
                        usados_alt[(k_alt, jj)] = {"area": 0.0, "comp": 0.0, "n": 0}
                    for k in ta:
                        usados_alt[(k_alt, jj)][k] += ta[k]
                    out.objeto(f"{ca['nome']} | {nome}", c_id, ca["material"], pa,
                               props_camada(ca, area_m2=ta["area"], comprimento_m=ta["comp"], pecas=ta["n"], divisao=nome,
                                            piso=piso, espessura_m=ca["espessura"]))
    for cid, cam, *_ in camadas:
        resumo.append((cid, cam["nome"], totais[cid]))
    for (k_alt, jj), t in sorted(usados_alt.items()):
        varias = len(camadas_alt(k_alt, 0.0)) > 1
        resumo.append((f"{cid_alt[k_alt]}.{jj + 1}" if varias else cid_alt[k_alt], camadas_alt(k_alt, 0.0)[jj][0]["nome"], t))


def pavimentos(casa, S, out, resumo):
    P = S["pavimentos"]
    I = S["interior"]
    rev = I["osb"]["espessura"] + I["acabamento"]["espessura"]
    fin = P["acabamento"]
    fin0 = P["piso0"]["acabado_z"]
    ab = casa.G["pavimento"].get("abertura_escada")
    out.colecao("4", "Pavimentos")
    ids = {}
    k = 1
    for cam in P["piso0"]["camadas"]:
        ids[cam["id"]] = f"4.{k}"
        out.colecao(f"4.{k}", f"Piso 0 | {cam['nome']}")
        k += 1
    ids["deck"] = f"4.{k}"  # structural OSB of the upper floor: created by build_casa.py
    k += 1
    # the finish of each room: the client's choice for that room (a point inside it — configurator, user 2026-10-22:
    # "a pessoa pode aplicar pavimento que desejar na divisão que desejar"), else the house's
    divs = P.get("divisoes") or []
    col_acab = {}  # finish name -> its collection
    fin_casa = fin

    def acab_de(grid, comp):
        rs_ = grid.retangulos(comp, 0.0)
        for d in reversed(divs):  # the last choice wins
            x, y = d["ponto"]
            if any(r[0] - 1e-6 <= x <= r[1] + 1e-6 and r[2] - 1e-6 <= y <= r[3] + 1e-6 for r in rs_):
                return d["acabamento"]
        return fin_casa

    def colecao_acab(f):
        nonlocal k
        if f["nome"] not in col_acab:
            col_acab[f["nome"]] = f"4.{k}"
            out.colecao(f"4.{k}", f"Revestimento de piso | {f['nome']}")
            k += 1
        return col_acab[f["nome"]]

    colecao_acab(fin)
    tot = {}
    for piso in casa.pisos:
        grid, lista = casa.salas[piso]
        for nome, comp in lista:
            area_util = 0.0
            fin = acab_de(grid, comp)
            ids["acab"] = colecao_acab(fin)
            if piso == 0:
                z = 0.0
                for cam in P["piso0"]["camadas"]:
                    e = (fin0 - fin["espessura"] - z) if cam["espessura"] == "resto" else cam["espessura"]
                    rs = grid.retangulos(comp, 0.0)
                    a = sum((r[1] - r[0]) * (r[3] - r[2]) for r in rs)
                    pecas = [prisma([(r[0], r[2], z), (r[1], r[2], z), (r[1], r[3], z), (r[0], r[3], z)], (0, 0, e))
                             for r in rs]
                    out.objeto(f"{cam['nome']} | {nome}", ids[cam["id"]], cam["material"], pecas,
                               props_camada(cam, area_m2=a, volume_m3=a * e, divisao=nome, piso=0, espessura_m=e))
                    t = tot.setdefault(ids[cam["id"]], [cam["nome"], {"area": 0.0, "comp": 0.0, "n": 0}])[1]
                    t["area"] += a
                    t["n"] += len(pecas)
                    z += e
                z_fin = z
            else:
                z_fin = casa.nv["piso1_interior"]
            rs = grid.retangulos(comp, rev)
            if piso == 1 and ab:
                rs = [q for r in rs for q in menos_retangulo(r, ab)]
            e = fin["espessura"]
            area_util = sum((r[1] - r[0]) * (r[3] - r[2]) for r in rs)
            pecas = [prisma([(r[0], r[2], z_fin), (r[1], r[2], z_fin), (r[1], r[3], z_fin), (r[0], r[3], z_fin)], (0, 0, e))
                     for r in rs if (r[1] - r[0]) > 0.01 and (r[3] - r[2]) > 0.01]
            out.objeto(f"{fin['nome']} | {nome}", ids["acab"], fin["material"], pecas,
                       props_camada(fin, area_m2=area_util, divisao=nome, piso=piso, espessura_m=e))
            t = tot.setdefault(ids["acab"], [fin["nome"], {"area": 0.0, "comp": 0.0, "n": 0}])[1]
            t["area"] += area_util
            t["n"] += len(pecas)
            r0 = max(grid.retangulos(comp), key=lambda r: (r[1] - r[0]) * (r[3] - r[2]))  # label inside the room
            cx, cy = (r0[0] + r0[1]) / 2, (r0[2] + r0[3]) / 2
            out.etiquetas.append({"texto": f"{nome}  {area_util:.1f} m²", "pos": [R(cx), R(cy), R(z_fin + e + 0.01)]})
            casa.area_util = getattr(casa, "area_util", {})
            casa.area_util[nome] = area_util
    for cid, (nome, t) in sorted(tot.items()):
        resumo.append((cid, nome, t))
    return ids["deck"]


def tetos(casa, S, out, resumo):
    """Ceilings. Flat (DiscoverCasa, user 2026-09-30 / 2026-10-09): réguas de suspensão screwed upright to the
    side of every beam or joist hold the steel ceiling profiles (perfis), which rest on a 30x30 perimeter
    angle (cantoneira, 3 m bars) screwed to the walls of each room; Pladur below; wool on top under the attic
    (la) and between the floor joists (la_pavimento).
    Sloped (roof on rafters, drawings' system): profiles + Pladur under the rafters."""
    T = S["tetos"]
    ca, pf, cn, ac = T["suspensao"], T["perfis"], T["cantoneira"], T["acabamento"]
    la, lp = T.get("la"), T.get("la_pavimento")  # wool on the top ceiling / between the floor joists
    osb = S["interior"]["osb"]["espessura"]
    ab = casa.G["pavimento"].get("abertura_escada")
    out.colecao("5", "Tetos")
    camadas = (("5.1", ca), ("5.2", pf), ("5.3", cn), ("5.4", ac)) + ((("5.5", la),) if la else ()) +         ((("5.6", lp),) if lp else ())
    las = [(cid, cam) for cid, cam in camadas if cid in ("5.5", "5.6")]
    for cid, cam in camadas:
        out.colecao(cid, cam["nome"])
    lg, hp, esp = pf["largura"], pf["altura"], pf["espacamento"]
    ct, st = casa.ct, casa.st
    tot = {cid: {"area": 0.0, "comp": 0.0, "n": 0} for cid, _c in camadas}
    # beams / joists above each flat ceiling: (centre x, width)
    faixas = {0: [(b[2], b[3]) for b in casa.G["pavimento"].get("vigas_principais", [])], 1: []}  # E-W main beams
    vigas = {0: sorted({(round((f["x0"] + f["x1"]) / 2, 4), round(f["x1"] - f["x0"], 4)) for f in casa.G["pavimento"]["pecas"]
                        if f["y1"] - f["y0"] > max(1.0, f["x1"] - f["x0"])}),
             1: [(x, casa.G["cobertura"].get("vigas_teto_largura", 0.075)) for x in casa.G["cobertura"].get("vigas_teto_x", [])]}
    for piso in casa.pisos:
        grid, lista = casa.salas[piso]
        plano = piso in casa.teto
        pan = [P for P in casa.paineis if P.piso == piso]
        if plano:
            zb = casa.teto[piso]                  # underside of the joists / ceiling beams
            z_ca = zb - ca["folga"]               # top of the profiles, hung from the beams by the réguas
            z_pf = z_ca - hp
            z_pl = z_pf - ac["espessura"]
        for nome, comp in lista:
            rs = grid.retangulos(comp, osb)
            if piso == 0 and ab:
                rs = [q for r in rs for q in menos_retangulo(r, ab)]
            pc = {cid: [] for cid in tot}
            q = {cid: {"area": 0.0, "comp": 0.0} for cid in tot}
            for x0, x1, y0, y1 in rs:
                # thin strips (where wall faces of different rooms do not line up) still get Pladur and wool,
                # only no profiles: skipping them left slots in the ceiling (Torres Vedras sala, 2026-10-15)
                fino = x1 - x0 < 0.05 or y1 - y0 < 0.05
                if x1 - x0 < 0.003 or y1 - y0 < 0.003 or (fino and not plano):
                    continue
                if plano:
                    yps = []
                    k = math.ceil((y0 + 0.05 - esp / 2) / esp)
                    while not fino and esp / 2 + k * esp < y1 - 0.05:
                        yc = esp / 2 + k * esp
                        pc["5.2"].append(caixa(x0, x1, yc - lg / 2, yc + lg / 2, z_pf, z_ca))
                        q["5.2"]["comp"] += x1 - x0
                        yps.append(yc)
                        k += 1
                    dentro = [(xv, wv) for xv, wv in vigas[piso] if x0 + 0.02 < xv < x1 - 0.02]  # no profiles -> no réguas
                    for xv, wv in dentro:  # one régua per profile on every beam, on the beam's side face
                        xs = xv + wv / 2
                        for yc in yps:
                            pc["5.1"].append(caixa(xs, xs + ca["espessura"], yc - ca["largura"] / 2, yc + ca["largura"] / 2,
                                                   z_pf, zb + ca["fixacao"]))
                            q["5.1"]["comp"] += zb + ca["fixacao"] - z_pf
                    for cid_l, cam_l in las:  # wool laid on the ceiling, between the beams / joists
                        if piso not in cam_l.get("pisos", []):
                            continue
                        ys, ya = [], y0
                        for f0, f1 in sorted(faixas[piso]):  # no wool under a main beam
                            if f1 > y0 and f0 < y1:
                                ys.append((ya, max(ya, f0)))
                                ya = max(ya, f1)
                        ys = [(a, b) for a, b in ys + [(ya, y1)] if b - a > 0.02]
                        xa = x0
                        for xv, wv in dentro + [(x1 + 1.0, 0.0)]:
                            xb = min(xv - wv / 2, x1)
                            for ya_, yb_ in (ys if xb - xa > 0.02 else []):
                                pc[cid_l].append(caixa(xa, xb, ya_, yb_, z_ca, z_ca + cam_l["espessura"]))
                                q[cid_l]["area"] += (xb - xa) * (yb_ - ya_)
                            xa = xv + wv / 2
                    for c in dividir_grelha([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ac["placa"][0], ac["placa"][1]):
                        q["5.4"]["area"] += area(c)
                        c = encolher(c, ac["junta"] / 2)
                        pc["5.4"].append(prisma([(u, v, z_pl) for u, v in c], (0, 0, ac["espessura"])))
                    continue
                # sloped ceiling under the rafters, split at the ridge
                for ya, yb, lado in ((y0, min(y1, casa.yr), -1), (max(y0, casa.yr), y1, 1)):
                    if yb - ya < 0.05:
                        continue
                    t = (-lado * ct, st)          # up the slope, in (y, z)
                    nd = (-lado * st, -ct)        # unit normal pointing below the rafters
                    s_max = max(abs(ya - casa.yr), abs(yb - casa.yr)) / ct
                    s = esp / 2
                    while s < s_max:
                        yc = casa.yr + lado * s * ct
                        if ya + 0.03 <= yc <= yb - 0.03:
                            zc = casa.z_rb(yc)
                            sec = [(yc - t[0] * lg / 2, zc - t[1] * lg / 2), (yc + t[0] * lg / 2, zc + t[1] * lg / 2)]
                            sec += [(p[0] + nd[0] * hp, p[1] + nd[1] * hp) for p in reversed(sec)]
                            pc["5.2"].append(prisma([(x0, y, z) for y, z in sec], (x1 - x0, 0, 0)))
                            q["5.2"]["comp"] += x1 - x0
                        s += esp
                    off = hp / ct
                    for c in dividir_grelha([(x0, ya), (x1, ya), (x1, yb), (x0, yb)], ac["placa"][0], ac["placa"][1] * ct,
                                            v0=casa.yr):
                        q["5.4"]["area"] += area(c) / ct
                        c = encolher(c, ac["junta"] / 2)
                        pc["5.4"].append(prisma([(u, v, casa.z_rb(v) - off) for u, v in c],
                                                (0, nd[0] * ac["espessura"], nd[1] * ac["espessura"])))
            if plano:  # perimeter angle on the real walls of the room (not on virtual doorways)
                for f in grid.faces(comp):
                    if not paineis_da_face(f, pan):
                        continue
                    s0, s1 = extensao(f, osb, osb + cn["aba"])
                    e = cn["espessura"]
                    pc["5.3"].append(prisma_face(f, [(s0, z_pf), (s1, z_pf), (s1, z_pf + cn["aba"]), (s0, z_pf + cn["aba"])],
                                                 osb, osb + e))
                    pc["5.3"].append(prisma_face(f, [(s0, z_pf - e), (s1, z_pf - e), (s1, z_pf), (s0, z_pf)],
                                                 osb, osb + cn["aba"]))
                    q["5.3"]["comp"] += s1 - s0
            for cid, cam in camadas:
                if cid in ("5.4", "5.5", "5.6"):
                    kw = {"area_m2": q[cid]["area"], "espessura_m": cam["espessura"]}
                    if cid != "5.4":
                        kw["volume_m3"] = q[cid]["area"] * cam["espessura"]
                else:
                    kw = {"comprimento_m": q[cid]["comp"]}
                n_pecas = len(pc[cid]) // (2 if cid == "5.3" else 1)
                out.objeto(f"{cam['nome']} | {nome}", cid, cam["material"], pc[cid],
                           props_camada(cam, pecas=n_pecas, divisao=nome, piso=piso, **kw))
                tot[cid]["area"] += q[cid]["area"]
                tot[cid]["comp"] += q[cid]["comp"]
                tot[cid]["n"] += n_pecas
    for cid, cam in camadas:
        resumo.append((cid, cam["nome"], tot[cid]))


def cobertura(casa, S, out, resumo):
    C = S["cobertura"]
    va, pn = (None if casa.sistema == "discovercasa" else C.get("vigas_apoio")), C["painel"]
    L, D, yr = casa.L, casa.D, casa.yr
    ct, st, tn = casa.ct, casa.st, casa.tn
    be, em = C["beirado"], C["empena"]
    xa, xb = -em, L + em
    out.colecao("6", "Cobertura | revestimento")
    hv = va["altura"] if va else 0.0
    if va:
        out.colecao("6.1", va["nome"])
    out.colecao("6.2", f"{pn['nome']} ({pn['material'].replace('Painel sandwich ', '')})")
    out.colecao("6.3", "Cumeeira, remates, caleiras e tubos de queda")
    fr = {f["lado"]: f for f in casa.G["cobertura"].get("frechais", [])}

    z_cume = casa.z_cob_cume(S)

    def zu(y):  # underside of the sandwich panels
        return z_cume - tn * abs(y - yr)

    tv = {"area": 0.0, "comp": 0.0, "n": 0}
    tpn = {"area": 0.0, "comp": 0.0, "n": 0}
    for lado, sg in (("S", -1), ("N", 1)):
        t = (-sg * ct, st)          # up the slope (y, z)
        m = (sg * st, ct)           # unit normal pointing up / out of the roof
        if va:  # purlins between the rafter end (on the eave plate) and the ridge
            y_fim = yr + sg * (casa.zr - casa.apoio[lado]) / tn
            s_fim = abs(y_fim - yr) / ct
            c_top, c_bot = 0.05 + va["largura"] / 2, s_fim - va["largura"] / 2
            n = max(1, math.ceil((c_bot - c_top) / va["espacamento_max"]))
            for k in range(n + 1):
                sc = c_top + (c_bot - c_top) * k / n
                yc = yr + sg * sc * ct
                base = (yc - t[0] * va["largura"] / 2, casa.z_rt(yc) - t[1] * va["largura"] / 2)
                sec = [base, (base[0] + t[0] * va["largura"], base[1] + t[1] * va["largura"])]
                sec += [(p[0] + m[0] * hv, p[1] + m[1] * hv) for p in reversed(sec)]
                out.objeto(f"Viga apoio cobertura {lado} {k + 1:02d}", "6.1", va["material"],
                           [prisma([(xa, y, z) for y, z in sec], (xb - xa, 0, 0))],
                           {"seccao": f"{round(va['largura'] * 1000)}x{round(hv * 1000)}", "tipo": "Viga de apoio à cobertura",
                            "vertente": lado, "comprimento_m": round(xb - xa, 3),
                            "volume_m3": round((xb - xa) * va["largura"] * hv, 5), "produto": va["produto"]})
                tv["comp"] += xb - xa
                tv["n"] += 1
        # sandwich panels: tile steps every `passo` along the slope, proud edge facing the eave
        y_e = (0.0 if sg < 0 else D) + sg * be
        A = (abs(yr - y_e) - 0.01) / ct
        hi, lo = pn["nucleo"] + pn["relevo"], pn["nucleo"]
        topo = [(0.0, hi)]
        a = pn["passo"]
        while a < A - 1e-6:
            topo += [(a, lo), (a, hi)]
            a += pn["passo"]
        a_ult = a - pn["passo"]
        topo.append((A, hi - (hi - lo) * (A - a_ult) / pn["passo"]))
        sec_as = [(0.0, 0.0), (A, 0.0)] + list(reversed(topo))
        p0 = (y_e, zu(y_e))
        sec = [(p0[0] + a_ * t[0] + p_ * m[0], p0[1] + a_ * t[1] + p_ * m[1]) for a_, p_ in sec_as]
        x, k = xa, 0
        while x < xb - 0.01:
            w = min(pn["largura"], xb - x)
            k += 1
            out.objeto(f"Painel sandwich {lado} {k:02d}", "6.2", pn["material"],
                       [prisma([(x + 0.001, y, z) for y, z in sec], (w - 0.002, 0, 0))],
                       props_camada(pn, area_m2=w * A, comprimento_m=A, pecas=1, vertente=lado,
                                    largura_m=w))
            tpn["area"] += w * A
            tpn["comp"] += A
            tpn["n"] += 1
            x += w
        # verge trims (both gables) and gutter + downpipes on this eave
        rm = C["remates"]["material"]
        q0, q1 = (p0[0] - m[0] * 0.03, p0[1] - m[1] * 0.03), (p0[0] + A * t[0] - m[0] * 0.03, p0[1] + A * t[1] - m[1] * 0.03)
        faixa = [q0, q1, (q1[0] + m[0] * (hi + 0.05), q1[1] + m[1] * (hi + 0.05)),
                 (q0[0] + m[0] * (hi + 0.05), q0[1] + m[1] * (hi + 0.05))]
        for xx, nm in ((xa - 0.004, "Oeste"), (xb, "Este")):
            out.objeto(f"Remate lateral {nm} {lado}", "6.3", rm, [prisma([(xx, y, z) for y, z in faixa], (0.004, 0, 0))],
                       {"camada": "Remate lateral", "comprimento_m": round(A, 3)})
        cl = C["caleira"]
        yo, yi = y_e + sg * cl["largura"] / 2, y_e - sg * cl["largura"] / 2
        zt = zu(y_e) - 0.02
        zb = zt - cl["altura"]
        e = 0.004
        ylo, yhi = min(yo, yi), max(yo, yi)
        partes = [(ylo, yhi, zb, zb + e), (ylo, ylo + e, zb, zt), (yhi - e, yhi, zb, zt)]
        out.objeto(f"Caleira {lado}", "6.3", cl["material"],
                   [prisma([(xa, a0, c0), (xa, a1, c0), (xa, a1, c1), (xa, a0, c1)], (xb - xa, 0, 0))
                    for a0, a1, c0, c1 in partes], {"camada": "Caleira exterior", "comprimento_m": round(xb - xa, 3)})
        tb = cl["tubo"]
        yt = y_e + sg * 0.01 - (tb if sg > 0 else 0)
        for xx, nm in ((0.30, "Oeste"), (L - 0.30 - tb, "Este")):
            out.objeto(f"Tubo de queda {lado} {nm}", "6.3", cl["material"],
                       [prisma([(xx, yt, 0.0), (xx + tb, yt, 0.0), (xx + tb, yt + tb, 0.0), (xx, yt + tb, 0.0)],
                               (0, 0, zb + 0.01))], {"camada": "Tubo de queda", "comprimento_m": round(zb, 3)})
    # ridge cap
    zq = zu(yr) + (pn["nucleo"] + pn["relevo"] + 0.005) / ct
    pecas = []
    for sg in (-1, 1):
        d = (sg * ct, -st)            # down the slope
        mm = (st * sg, ct)            # up / out of the roof
        q = (yr, zq)
        e_ = (yr + d[0] * 0.2, zq + d[1] * 0.2)
        sec = [q, e_, (e_[0] + mm[0] * 0.005, e_[1] + mm[1] * 0.005), (q[0] + mm[0] * 0.005, q[1] + mm[1] * 0.005)]
        pecas.append(prisma([(xa, y, z) for y, z in sec], (xb - xa, 0, 0)))
    out.objeto("Cumeeira", "6.3", C["remates"]["material"], pecas, {"camada": "Cumeeira", "comprimento_m": round(xb - xa, 3)})
    if va:
        resumo.append(("6.1", va["nome"], tv))
    resumo.append(("6.2", pn["nome"], tpn))
    return fr


def cobertura_faces(casa, S, out, resumo):
    """An exposed sandwich-panel roof of several slopes (casa_planta.py "a_vista", user 2026-10-21: always sandwich
    panel; 2 águas the rule, 4 águas an option, várias águas on L / T / U): the panels on every face, the ridge and
    hip caps, the valley gutters (caleira de laró), the verge trims, the abutment flashings, the exterior gutters on
    every eave and their downpipes down the façade to just above the base (rulebook v7.1 §7 E7–E10; sizes assumed)."""
    C = S["cobertura"]
    pn, rm, cl = C["painel"], C["remates"]["material"], C["caleira"]
    G = casa.G["cobertura"]
    th = math.radians(G["inclinacao"])
    ct = math.cos(th)
    esp = pn["nucleo"] + pn.get("relevo", 0.0)
    out.colecao("6", "Cobertura | revestimento")
    out.colecao("6.2", f"{pn['nome']} ({pn['material'].replace('Painel sandwich ', '')})")
    out.colecao("6.3", "Cumeeira, rincões, larós, remates, caleiras e tubos de queda")
    tpn = {"area": 0.0, "comp": 0.0, "n": 0}
    # the panels of each slope (one plane: its pieces together, also those of two rectangles on one plane — a wing
    # flush with the main body's eave, rulebook L49) run down the slope, pn["largura"] wide: their count across the
    # slope and the longest run (the order: count x length, cut on site at rincões / larós)
    aguas = {}
    for f in casa.faces:
        aguas.setdefault(tuple(round(v, 6) for v in f["plano"]), []).append(f)
    aguas = {(min(f.get("ret") or 0 for f in fs), fs[0]["nome"]): fs for fs in aguas.values()}
    lg = pn.get("largura", 1.0)
    for (ret, nome_a), fs in sorted(aguas.items(), key=lambda kv: (kv[0][0] or 0, kv[0][1])):
        ex, ey = fs[0]["subida"]
        across = [(-ey * x + ex * y) for f in fs for x, y in f["pts"]]
        along = [(ex * x + ey * y) for f in fs for x, y in f["pts"]]
        n_p = max(1, math.ceil((max(across) - min(across)) / lg - 1e-6))
        comp_max = (max(along) - min(along)) / ct
        a_agua = sum(area(f["pts"]) for f in fs) / ct
        pecas = [prisma([[R(c) for c in q] for q in [(x, y, f["z0"] + f["gx"] * x + f["gy"] * y + 0.001) for x, y in f["pts"]]],
                        (0, 0, R(esp / ct))) for f in fs]
        out.objeto(f"Painel sandwich R{(ret or 0) + 1}{nome_a}", "6.2", pn["material"], pecas,
                   props_camada(pn, area_m2=round(a_agua, 3), pecas=n_p, vertente=nome_a, comprimento_m=round(comp_max, 3),
                                paineis=f"{n_p} x {comp_max:.2f} m (largura útil {lg:.2f})"))
        tpn["area"] += a_agua
        tpn["comp"] += n_p * comp_max
        tpn["n"] += n_p
    tots = {}
    z_top = esp / ct + 0.002
    tubos = []
    for k, ln in enumerate(G["linhas"], 1):
        (x0, y0, z0), (x1, y1, z1) = ln["p0"], ln["p1"]
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 0.05:
            continue
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -uy, ux
        comp = math.hypot(L, z1 - z0)
        tipo = ln["tipo"]

        def faixa(meia, dz0, dz1, desloc=0.0):
            c0 = (x0 + nx * desloc, y0 + ny * desloc)
            q = [(c0[0] - nx * meia, c0[1] - ny * meia, z0 + dz0), (c0[0] + nx * meia, c0[1] + ny * meia, z0 + dz0),
                 (c0[0] + nx * meia, c0[1] + ny * meia, z0 + dz1), (c0[0] - nx * meia, c0[1] - ny * meia, z0 + dz1)]
            return prisma([[R(c) for c in p] for p in q], (R(x1 - x0), R(y1 - y0), R(z1 - z0)))

        def dobrada(meia):
            """A cap over a ridge / hip: a flange down each slope, on the panels (a flat strip had stood clear of
            them — user 2026-10-28: "elas estão 'coladas' à cobertura")."""
            pcs = []
            xm, ym, zm = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
            for sgn in (-1, 1):
                zo = casa.z_faces(xm + nx * sgn * meia, ym + ny * sgn * meia)
                if zo is None:
                    continue
                dz = zo - zm  # the slope's fall from the line to the flange's edge (the same all along the line)
                q = [(x0, y0, z0 + z_top), (x0 + nx * sgn * meia, y0 + ny * sgn * meia, z0 + dz + z_top),
                     (x0 + nx * sgn * meia, y0 + ny * sgn * meia, z0 + dz + z_top + 0.004), (x0, y0, z0 + z_top + 0.004)]
                pcs.append(prisma([[R(c) for c in p] for p in q], (R(x1 - x0), R(y1 - y0), R(z1 - z0))))
            return pcs

        if tipo in ("cumeeira", "rincao"):
            nome, pc = ("Cumeeira" if tipo == "cumeeira" else "Remate de rincão"), dobrada(0.20)
        elif tipo == "laro":
            nome, pc = "Caleira de laró", [faixa(0.25, -0.004, 0.0)]
        elif tipo == "empena":
            nome, pc = "Remate lateral", [faixa(0.003, -0.06, z_top + 0.01)]
        elif tipo == "encosto":  # on the lower roof's slope (its flange) and up the gable's cladding (its leg)
            pc = [f for f in dobrada(0.10) if f["b"][1][2] < f["b"][0][2] + 1e-6][:1]
            nome, pc = "Remate de encosto", pc + [faixa(0.003, z_top, z_top + 0.10)] if pc else [faixa(0.10, z_top, z_top + 0.005)]
        else:  # beirado: the exterior gutter under the panels' edge, out from the eave line
            nome = "Caleira"
            d = 1.0  # the outside is to the right of the face's counter-clockwise edge
            e, w_, h_ = 0.004, cl["largura"], cl["altura"]
            zt = z0 - 0.02
            pc = []
            for a0, a1, c0, c1 in ((0.0, w_, zt - h_, zt - h_ + e), (0.0, e, zt - h_, zt), (w_ - e, w_, zt - h_, zt)):
                q = [(x0 - nx * d * a0 - nx * 0.0, y0 - ny * d * a0, c0), (x0 - nx * d * a1, y0 - ny * d * a1, c0),
                     (x0 - nx * d * a1, y0 - ny * d * a1, c1), (x0 - nx * d * a0, y0 - ny * d * a0, c1)]
                q = [(px + nx * w_ / 2, py + ny * w_ / 2, pz) for px, py, pz in q]  # centred under the panels' edge
                pc.append(prisma([[R(c) for c in p] for p in q], (R(x1 - x0), R(y1 - y0), 0)))
            tubos.append(((x0, y0), (x1, y1), zt - h_, (nx, ny)))
        out.objeto(f"{nome} {k:02d}", "6.3", cl["material"] if nome == "Caleira" else rm, pc,
                   {"camada": nome, "comprimento_m": round(comp, 3)})
        tots[nome] = tots.get(nome, 0.0) + comp
    # downpipes: two per gutter run (rulebook E8), at its ends, down to 5 cm above the base, against the cladding
    # (the swan-neck from the gutter back to the façade drawn as a short level piece — assumed)
    tb = cl["tubo"]
    base_z = cl.get("folga_base", 0.05)
    # join the eave pieces of one straight gutter, in whatever order they come (one run, two downpipes — a run split
    # in three gave six on the 4-água L)
    corridas = [{"a": pa, "b": pb, "z": zb, "n": n_} for (pa, pb, zb, n_) in tubos]
    junta = True
    while junta:
        junta = False
        for i, c in enumerate(corridas):
            for d in corridas[i + 1:]:
                if abs(c["n"][0] - d["n"][0]) > 1e-6 or abs(c["n"][1] - d["n"][1]) > 1e-6 or abs(c["z"] - d["z"]) > 1e-3:
                    continue
                if math.dist(c["b"], d["a"]) < 0.02:
                    c["b"] = d["b"]
                elif math.dist(d["b"], c["a"]) < 0.02:
                    c["a"] = d["a"]
                else:
                    continue
                corridas.remove(d)
                junta = True
                break
            if junta:
                break
    n_tubos = 0
    be = casa.G["cobertura"].get("beirado", C["beirado"])
    for c in corridas:
        L = math.dist(c["a"], c["b"])
        if L < 1.0:
            continue
        ux, uy = (c["b"][0] - c["a"][0]) / L, (c["b"][1] - c["a"][1]) / L
        nx, ny = c["n"]
        for t in (0.30, L - 0.30 - tb):  # 0,30 from the run's ends (rulebook E8)
            px, py = c["a"][0] + ux * t, c["a"][1] + uy * t
            fx, fy = px + nx * (be - 0.10), py + ny * (be - 0.10)  # back against the cladding
            q = [(fx, fy, base_z), (fx + ux * tb, fy + uy * tb, base_z), (fx + ux * tb - nx * tb, fy + uy * tb - ny * tb, base_z),
                 (fx - nx * tb, fy - ny * tb, base_z)]
            n_tubos += 1
            # joined to its gutter: from the outlet in the gutter's bottom, down and back to the pipe's top (the
            # user 2026-10-28: "os tubos de queda não estão conectados as caleiras")
            h = tb / 2

            def quadrado(X, Y, Z):
                return [(X - ux * h - nx * h, Y - uy * h - ny * h, Z), (X + ux * h - nx * h, Y + uy * h - ny * h, Z),
                        (X + ux * h + nx * h, Y + uy * h + ny * h, Z), (X - ux * h + nx * h, Y - uy * h + ny * h, Z)]
            ligacao = {"b": [[R(v) for v in p] for p in quadrado(px + ux * h, py + uy * h, c["z"] + 0.002)],
                       "t": [[R(v) for v in p] for p in quadrado(fx + ux * h - nx * h, fy + uy * h - ny * h, c["z"] - 0.10)]}
            out.objeto(f"Tubo de queda {n_tubos:02d}", "6.3", cl["material"],
                       [prisma([[R(v) for v in p] for p in q], (0, 0, R(c["z"] - 0.10 - base_z))), ligacao],
                       {"camada": "Tubo de queda", "comprimento_m": round(c["z"] - 0.10 - base_z + 0.25, 3)})
            tots["Tubo de queda"] = tots.get("Tubo de queda", 0.0) + c["z"] - 0.10 - base_z + 0.25
    resumo.append(("6.2", pn["nome"], tpn))
    for nome, comp in sorted(tots.items()):
        resumo.append(("6.3", nome, {"area": 0.0, "comp": comp, "n": 0}))
    return {}


def cobertura_platibanda(casa, S, out, resumo):
    """Roof hidden behind the walls (geometry "cobertura.tipo" = "platibanda", casa_planta.py): the house has the
    same height on every side (user 2026-10-16); 5-rib sandwich panels on the purlins of every slope
    ("telhados"), ending in a caleira oculta inside the parapet at the low edge (aluminium lining up to the
    chapéu, end caps); two downpipes per gutter inside the exterior cladding, hidden by the Tremolo, clear of the
    openings, ending above the foundation base; a ridge cap where two slopes meet; a chapéu wrapping every
    parapet (chapeus); the parapets' roof side clad like a facade (platibanda_interior)."""
    C = S["cobertura"]
    po, cl = C["painel_oculto"], C["caleira_oculta"]
    Gc = casa.G["cobertura"]
    out.colecao("6", "Cobertura | revestimento")
    out.colecao("6.2", po["nome"])
    out.colecao("6.3", "Caleiras, chapéus, remates e tubos de queda")
    tpn = {"area": 0.0, "comp": 0.0, "n": 0}
    e = po["espessura"]
    tubos = tubos_queda(casa, S)
    for t_idx, t in enumerate(Gc["telhados"]):
        x0, x1, yb, yc, zc, tn = t["x0"], t["x1"], t["y_baixo"], t["y_cume"], t["z_cume"], t["inclinacao"]
        run = abs(yc - yb)
        ct = 1 / math.sqrt(1 + tn * tn)
        comp = run / ct

        def z(y):
            return zc - tn * abs(y - yc)

        sec = [(yc, z(yc)), (yb, z(yb)), (yb, z(yb) + e / ct), (yc, z(yc) + e / ct)]
        lg = po["largura"]
        if "grelha_x" in t:  # columns of full panels from the anchor (D2503: laid from the east end, the cut strip
            # at the west end; a column across two slopes is one panel cut in an L)
            ax = t["grelha_x"]
            cols = []
            j = 0
            while ax - j * lg > x0 + 0.01:
                a_, b_ = max(x0, ax - (j + 1) * lg), min(x1, ax - j * lg)
                if b_ - a_ > 0.01:
                    cols.append((a_, b_))
                j += 1
            cols.sort()
        else:
            cols, x = [], x0
            while x < x1 - 0.01:
                cols.append((x, min(x + lg, x1)))
                x += lg
        for k, (x, xb) in enumerate(cols, 1):
            w = xb - x
            out.objeto(f"Painel 5 ondas {t['lado']} x{x:.2f}", "6.2", po["material"],
                       [prisma([(x + 0.001, y, zz) for y, zz in sec], (w - 0.002, 0, 0))],
                       props_camada(po, area_m2=w * comp, comprimento_m=comp, pecas=1, vertente=t["lado"], largura_m=w))
            tpn["area"] += w * comp
            tpn["comp"] += comp
            tpn["n"] += 1
        if "y_fora" not in t:
            continue
        # hidden gutter (caleira oculta) inside the parapet: aluminium lining of the channel (bottom, parapet face up
        # to the rufo, upright face); downpipes inside the exterior cladding, hidden by the Tremolo (user 2026-10-16)
        sg = 1 if t["lado"] == "N" else -1
        ya_c, yb_c = t["canal"]
        zb_c, zt_c = t["z_canal"]
        y_par = t["y_parede"]
        y_up_face = ya_c if y_par == yb_c else yb_c        # channel edge on the roof side (face of the upright)
        zp = casa.nv.get("platibanda")
        if "fundo" in t:  # D2503: bottom on packing falling to the outlets, parapet side up to the top (under the
            # chapéu), madre side up the gutter madre + a 0,10 flange over it (under the panels), end caps
            fd = t["fundo"]
            y_md = t.get("y_caleira", y_up_face)
            zm = t["z_madre"]
            aba = cl.get("aba", 0.10)
            pecas_c = []
            for (xa, za), (xb, zb) in zip(fd, fd[1:]):
                pecas_c.append(prisma([(xa, ya_c, za), (xb, ya_c, zb), (xb, ya_c, zb + 0.002), (xa, ya_c, za + 0.002)],
                                      (0, yb_c - ya_c, 0)))
            def z_fundo(x):
                for (xa, za), (xb, zb) in zip(fd, fd[1:]):
                    if xa - 1e-9 <= x <= xb + 1e-9:
                        return za + (zb - za) * (x - xa) / ((xb - xa) or 1.0)
                return fd[0][1] if x < fd[0][0] else fd[-1][1]

            # the outlets: a hole in the lining where each downpipe's stub goes through the parapet (user
            # 2026-10-20: "um erro que esta presente é nas caleiras nao existem os buracos par agua escoar para os tubos de queda")
            furos = sorted((max(tq["x"][0], fd[0][0]), min(tq["x"][1], fd[-1][0]), tq["furo_z"][1])
                           for tq in tubos if tq.get("telhado") == t_idx)
            for y_l, z_top in ((y_par, zp), (y_md, zm)):
                d_ = -sg * 0.002 if y_l == y_par else sg * 0.002
                if y_l != y_par or not furos:
                    poly = [(x, y_l, z_) for x, z_ in fd] + [(fd[-1][0], y_l, z_top), (fd[0][0], y_l, z_top)]
                    pecas_c.append(prisma(poly, (0, d_, 0)))
                    continue
                cortes_x = [fd[0][0]] + [v for a_, b_, _z in furos for v in (a_, b_)] + [fd[-1][0]]
                for a_, b_ in zip(cortes_x[0::2], cortes_x[1::2]):  # the plate between the holes
                    if b_ - a_ < 0.002:
                        continue
                    base = [(a_, z_fundo(a_))] + [(x, z_) for x, z_ in fd if a_ < x < b_] + [(b_, z_fundo(b_))]
                    poly = [(x, y_l, z_) for x, z_ in base] + [(b_, y_l, z_top), (a_, y_l, z_top)]
                    pecas_c.append(prisma(poly, (0, d_, 0)))
                for a_, b_, zh in furos:  # over each hole
                    pecas_c.append(prisma([(a_, y_l, zh), (b_, y_l, zh), (b_, y_l, z_top), (a_, y_l, z_top)], (0, d_, 0)))
            pecas_c.append(caixa(x0, x1, min(y_md, y_md - sg * aba), max(y_md, y_md - sg * aba), zm, zm + 0.002))
            for (xe, ze), fim, dx in ((fd[0], t.get("fins_caleira", ["parede"] * 2)[0], 0.002),
                                      (fd[-1], t.get("fins_caleira", ["parede"] * 2)[1], -0.002)):
                xa_c, xb_c = min(xe, xe + dx), max(xe, xe + dx)
                if fim == "parede":  # up to the panel ends; above them it lines the parapet only between the
                    # wall and the panel ends (the parapet's cladding covers the rest, platibanda_interior)
                    pecas_c.append(caixa(xa_c, xb_c, ya_c, yb_c, ze, t["z_borda"]))
                    yp0, yp1 = sorted((y_par, t["y_baixo"]))
                    pecas_c.append(caixa(xa_c, xb_c, yp0, yp1, t["z_borda"], zp))
                else:
                    pecas_c.append(caixa(xa_c, xb_c, ya_c, yb_c, ze, t["z_borda"]))
                if fim == "livre":
                    esp_f = sum(c["espessura"] for c in camadas_platibanda(S)) + 0.002
                    z_rf = t["z_cume"] - t["inclinacao"] * abs(y_par - t["y_cume"]) + e
                    xa_, xb_ = (xe - esp_f, xe) if dx > 0 else (xe, xe + esp_f)
                    pecas_c.append(caixa(xa_, xb_, min(y_par, y_par - sg * 0.002), max(y_par, y_par - sg * 0.002), z_rf, zp))
            out.objeto(f"Caleira oculta {t['lado']} {x0:.1f}", "6.3", "Caleira", pecas_c,
                       {"camada": cl["nome"], "produto": cl["produto"], "comprimento_m": round(x1 - x0, 3),
                        "queda_m": round(max(z_ for _x, z_ in fd) - min(z_ for _x, z_ in fd), 3)})
            continue
        lam = [caixa(x0, x1, ya_c, yb_c, zb_c, zb_c + 0.002),
               caixa(x0, x1, min(y_par, y_par - sg * 0.002), max(y_par, y_par - sg * 0.002), zb_c, zp - 0.02),
               caixa(x0, x1, min(y_up_face, y_up_face + sg * 0.002), max(y_up_face, y_up_face + sg * 0.002), zb_c, zt_c),
               # end caps against the side parapets (up to the panel top)
               caixa(x0, x0 + 0.002, ya_c, yb_c, zb_c, t["z_borda"]),
               caixa(x1 - 0.002, x1, ya_c, yb_c, zb_c, t["z_borda"])]
        out.objeto(f"Caleira oculta {t['lado']} {x0:.1f}", "6.3", "Caleira", lam,
                   {"camada": cl["nome"], "produto": cl["produto"], "comprimento_m": round(x1 - x0, 3)})
    # downpipes inside the exterior cladding, hidden by the Tremolo (user 2026-10-16), ending a little above the
    # foundation base so the water can leave the pipe (user 2026-10-16: "tem de estar ligeiramente acima")
    for tq in tubos:
        out.objeto(tq["nome"], "6.3", "Caleira", tq["pecas"],
                   {"camada": "Tubo de queda (no revestimento)", "comprimento_m": round(tq["z"][1] - tq["z"][0], 3),
                    "produto": "Tubo de queda dentro do revestimento exterior, escondido pelo Tremolo (secção a confirmar)"})
    esp_int = sum(c["espessura"] for c in camadas_platibanda(S))
    # a ridge cap where two slopes meet (a slope whose high side stands against a parapet has none), between the
    # parapets' roof-side cladding
    cumes = {}
    for t in Gc["telhados"]:
        cumes.setdefault(round(t["y_cume"], 3), []).append(t)
    for yc, ts in cumes.items():
        ns, ss = [t for t in ts if t["lado"] == "N"], [t for t in ts if t["lado"] == "S"]
        if not ns or not ss:
            continue
        x0 = max(min(t["x0"] for t in ns), min(t["x0"] for t in ss)) + esp_int
        x1 = min(max(t["x1"] for t in ns), max(t["x1"] for t in ss)) - esp_int
        if x1 - x0 < 0.1:
            continue
        zq = ts[0]["z_cume"] + e + 0.002
        cai = ts[0]["inclinacao"] * 0.15  # folded down both slopes, on the panels (no gap under its edges)
        out.objeto(f"Cumeeira {yc:.2f}", "6.3", C["remates"]["material"],
                   [prisma([(x0, yc, zq), (x0, y_, zq - cai), (x0, y_, zq - cai + 0.004), (x0, yc, zq + 0.004)], (x1 - x0, 0, 0))
                    for y_ in (yc - 0.15, yc + 0.15)],
                   {"camada": "Cumeeira", "comprimento_m": round(x1 - x0, 3)})
    # one slope: its high end against the parapet — a top flashing over the panels' end and up the parapet's
    # cladding (no ridge cap; ours, as the abutment flashings of the exposed roof)
    for t in Gc["telhados"]:
        if not t.get("uma_agua"):
            continue
        sg = 1 if t["lado"] == "N" else -1  # down the slope
        y_f = t["y_cume"] + sg * esp_int          # face of the parapet's roof-side cladding
        zt_ = t["z_cume"] - t["inclinacao"] * esp_int + e / math.cos(math.atan(t["inclinacao"]))
        y_a, y_b = sorted((y_f, y_f + sg * 0.12))
        # its leg stops under the chapéu's inner leg (the parapet stands only ~5 cm over the plane's top there)
        zp_ = casa.nv.get("platibanda") or (zt_ + 0.12)
        alto = max(0.02, min(0.10, zp_ - C["chapeu"].get("descida", 0.02) - 0.002 - zt_))
        out.objeto(f"Remate de topo {t['x0']:.1f}", "6.3", C["remates"]["material"],
                   [caixa(t["x0"] + esp_int, t["x1"] - esp_int, y_a, y_b, zt_, zt_ + 0.002),
                    caixa(t["x0"] + esp_int, t["x1"] - esp_int, min(y_f, y_f + sg * 0.002), max(y_f, y_f + sg * 0.002),
                          zt_, zt_ + alto)],
                   {"camada": "Remate de topo", "comprimento_m": round(t["x1"] - t["x0"] - 2 * esp_int, 3)})
    chapeus(casa, S, out, resumo)
    resumo.append(("6.2", po["nome"], tpn))
    platibanda_interior(casa, S, out, resumo)
    return {}


def tubos_queda(casa, S):
    """Downpipes of the hidden gutters: two per gutter, in the batten cavity of the facade below it (outer face of
    the frame + OSB + membrane, behind the Tremolo), 0,45 from the gutter ends and >= 0,15 clear of the openings,
    from a little above the foundation base (tubo.folga_base) up to the outlet through the parapet."""
    ext = S["exterior"]
    op = ext["opcoes"][ext.get("opcao_visivel", "A")]
    cl = S["cobertura"]["caleira_oculta"]
    prof_cav = 0.0  # depth of the batten cavity behind the cladding (where the downpipes run)
    for c in op["camadas"]:
        if c.get("tipo") != "ripas":
            break
        prof_cav += c["espessura"]
    tb = cl.get("tubo", {}).get("largura", 0.08)
    z0 = ext.get("cota_base", 0.0) + cl.get("tubo", {}).get("folga_base", 0.05)
    res = []
    for it, t in enumerate(casa.G["cobertura"].get("telhados", [])):
        if "y_fora" not in t:
            continue
        sg = 1 if t["lado"] == "N" else -1
        zb_c = t["z_canal"][0]
        y_par = t["y_parede"]
        y_cav0 = t["y_fora"] + sg * (ext["osb"]["espessura"] + ext["membrana"]["espessura"])
        y_cav1 = y_cav0 + sg * max(prof_cav - 0.002, 0.02)
        pa, pb = t["parede_s"]
        x0, x1 = t["x0"], t["x1"]
        vaos = t.get("aberturas_parede", [])
        if "saidas" in t:  # outlets fixed by the gutter (its low points), the pipe inside the gutter's length
            locais = [(str(i), min(max(xs, x0 + 0.02), x1 - tb - 0.02), 0.0) for i, xs in enumerate(t["saidas"], 1)]
        else:
            locais = (("1", max(pa, x0) + 0.45, 0.05), ("2", min(pb, x1) - 0.45 - tb, -0.05))
        for nm, xx, passo in locais:
            n_ = 0
            while passo and any(v0 - 0.15 < xx + tb and xx < v1 + 0.15 for v0, v1 in vaos) and n_ < 400:
                xx += passo
                n_ += 1
            ys_ = sorted((y_cav0, y_cav1))
            yo = sorted((y_par, y_cav1))
            z1 = zb_c + 0.06
            e_ = 0.003  # the outlet stub through the parapet is hollow: the hole in the gutter shows into it
            res.append({"nome": f"Tubo de queda {t['lado']} {x0:.1f} {nm}", "y_fora": t["y_fora"], "n": sg,
                        "x": (xx, xx + tb), "z": (z0, z1), "telhado": it, "furo_z": (zb_c, z1),
                        "pecas": [caixa(xx, xx + tb, ys_[0], ys_[1], z0, z1),
                                  caixa(xx, xx + tb, yo[0], yo[1], zb_c - 0.01, zb_c - 0.01 + e_),
                                  caixa(xx, xx + tb, yo[0], yo[1], z1 - e_, z1),
                                  caixa(xx, xx + e_, yo[0], yo[1], zb_c - 0.01, z1),
                                  caixa(xx + tb - e_, xx + tb, yo[0], yo[1], zb_c - 0.01, z1)]})
    return res


def face_caleira(casa, d, fim):
    """For a free end (fim 0 = start, 1 = end) of a parapet module: the line of a gutter wall's inner face lying
    just beyond it (<= 0,10), across the same span — the end then runs on to it. None if there is none."""
    s_ = d["s"][fim]
    sg = -1 if fim == 0 else 1
    um = (d["f_out"] + d["f_in"]) / 2
    best = None
    for t in casa.G["cobertura"]["telhados"]:
        if "y_parede" not in t or d["eixo"] != "y":
            continue
        gap = sg * (t["y_parede"] - s_)
        if 0.0 < gap <= 0.10 and t["x0"] - 0.15 <= um <= t["x1"] + 0.15:
            if best is None or gap < abs(best - s_):
                best = t["y_parede"]
    return best


def platibandas(casa, S):
    """Parapet modules of a hidden roof with their sides: footprint, outer and inner (roof side) frame faces,
    direction from the frame to the roof, and what each end is: "canto" (outer corner of the frame outline),
    "livre" (free end standing over the roof, e.g. a parapet ending at the re-entrant corner of an L) or "junta"."""
    tipo = {p["nome"]: p.get("platibanda") for p in casa.G["paineis"]}
    plats = [P for P in casa.paineis if P.piso == 2 and tipo.get(P.nome) in ("alta", "calha")]
    tels = casa.G["cobertura"]["telhados"]
    cont = [tuple(v) for v in casa.G.get("contorno_estrutura") or []]
    # only the outer (convex) corners of the outline: at a re-entrant corner the walls do not turn outwards
    area2 = sum(cont[i][0] * cont[(i + 1) % len(cont)][1] - cont[(i + 1) % len(cont)][0] * cont[i][1]
                for i in range(len(cont)))
    cantos = []
    for i, v in enumerate(cont):
        a_, b_ = cont[i - 1], cont[(i + 1) % len(cont)]
        cr = (v[0] - a_[0]) * (b_[1] - v[1]) - (v[1] - a_[1]) * (b_[0] - v[0])
        if cr * area2 > 0:
            cantos.append(v)
    pegs = [Q.pegada() for Q in plats]
    pi_ = S["cobertura"]["platibanda_interior"]
    esp_forro = sum(c["espessura"] for c in camadas_platibanda(S))

    def em_painel(x, y):
        return any(a - 0.005 <= x <= b + 0.005 and c - 0.005 <= y <= d + 0.005 for a, b, c, d in pegs)

    def sobre_telhado(x, y):
        return any(t["x0"] - 0.01 <= x <= t["x1"] + 0.01 and
                   min(t.get("y_parede", t["y_baixo"]), t["y_cume"]) - 0.01 <= y <=
                   max(t.get("y_parede", t["y_baixo"]), t["y_cume"]) + 0.01 for t in tels)

    res = []
    for P, (x0, x1, y0, y1) in zip(plats, pegs):
        if abs(P.ux) > 0.5:  # along x: outside is +y when fora > 0
            ax, sp, um = "x", (x0, x1), (y0 + y1) / 2
            f_out, f_in, n_in = (y1, y0, -1) if P.fora > 0 else (y0, y1, 1)
        else:  # along y: outside is -x when fora > 0
            ax, sp, um = "y", (y0, y1), (x0 + x1) / 2
            f_out, f_in, n_in = (x0, x1, 1) if P.fora > 0 else (x1, x0, -1)
        fins = []
        for s_, d in ((sp[0], -1), (sp[1], 1)):
            pt = (s_ + d * 0.05, um) if ax == "x" else (um, s_ + d * 0.05)
            cn = (s_, f_out) if ax == "x" else (f_out, s_)
            if any(abs(cx - cn[0]) < 0.01 and abs(cy - cn[1]) < 0.01 for cx, cy in cantos):
                fins.append("canto")
            elif not em_painel(*pt) and sobre_telhado(*pt):
                fins.append("livre")
            else:
                fins.append("junta")
        # roof side: clad (OSB 15 ... Tremolo), or lined by the gutter on the gutter walls (D2503)
        forrada = tipo.get(P.nome) == "alta" or pi_.get("paredes_com_caleira", True)
        res.append({"P": P, "eixo": ax, "s": sp, "f_out": f_out, "f_in": f_in, "n_in": n_in, "fins": fins,
                    "zp": P.oz + P.hf, "forrada": forrada,
                    "esp_int": esp_forro if forrada else S["cobertura"]["caleira_oculta"].get("espessura_forro", 0.002)})
    return res


def chapeus(casa, S, out, resumo):
    """Chapéus on the parapets (user 2026-10-16: "Os Rufos da platibanda na realidade nós chamamos de Chapéus e eles
    envolvem a parede ou seja cobrem toda a largura e ficam junto da parede do lado de dentro e de foram cerca de 3
    cm para baixo"): a folded sheet over the whole width (frame + facade cladding + roof-side cladding), flat or
    with the fall `chapeu.queda` (TV: flat, D2503), with a leg down each face, tight to the cladding. Every top is
    covered once (user 2026-10-20: they "não podem deixar o topo destapado" and "não dão overlap uns aos outros"):
    at an end where a wall stands across, whichever frame runs through, the chapéu runs on to that wall's far edge
    (ate_parede); the X chapéus cover the corners and fold down their ends, the Y chapéus stop against them. The
    tops are checked for overlaps at the end (warning)."""
    C = S["cobertura"]
    ch = C["chapeu"]
    ext = S["exterior"]
    op = ext["opcoes"][ext.get("opcao_visivel", "A")]
    esp_ext = ext["osb"]["espessura"] + ext["membrana"]["espessura"] + sum(c["espessura"] for c in op["camadas"])
    esp_int = sum(c["espessura"] for c in camadas_platibanda(S))
    tl, desc, queda = ch.get("espessura", 0.002), ch.get("descida", 0.03), ch.get("queda", 0.02)
    info = platibandas(casa, S)

    def peca(ax, s0, s1, sec):
        """Prism along the wall axis from s0 to s1 of a section [(u, z)] across it."""
        if ax == "x":
            return prisma([(s0, u, z) for u, z in sec], (s1 - s0, 0, 0))
        return prisma([(u, s0, z) for u, z in sec], (0, s1 - s0, 0))

    def placa(u0, u1, z0, z1):
        return [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]

    feitos = []  # X chapéus: (span along x, span across in y), to stop the Y chapéus against
    topos_ch = []  # every chapéu's top: (name, axis, along a..b, across lo..hi), checked for overlaps

    def banda(d):  # across the wall: outer edge of the chapéu .. inner edge
        u_o_ = d["f_out"] - d["n_in"] * (esp_ext + tl)
        u_i_ = d["f_in"] + d["n_in"] * (d["esp_int"] + tl)
        return min(u_o_, u_i_), max(u_o_, u_i_)

    bandas = [banda(r) for r in info]

    def ate_parede(d, fim):
        """End `fim` of d's chapéu: when a wall across stands at that end (whichever frame runs through at the
        corner), the chapéu runs on to that wall's far edge, so the corner top is covered once (user 2026-10-19:
        the chapéus "não podem deixar o topo destapado" and "não dão overlap uns aos outros"). Returns (end, near
        edge of that wall, whether that wall runs on past d on d's outer side) or None."""
        s_, sg = d["s"][fim], (-1 if fim == 0 else 1)
        lo, hi = banda(d)
        res = None
        for r, (rl, rh) in zip(info, bandas):
            if r["eixo"] == d["eixo"] or not (rl - 0.01 <= s_ <= rh + 0.01):
                continue
            ra, rb = r["s"]
            if min(rb, hi) - max(ra, lo) < -0.05:  # that wall does not reach this one
                continue
            e = rl if sg < 0 else rh
            if sg * (e - s_) > 0.001 and (res is None or sg * (e - res[0]) > 0):
                fora_r = (ra < lo - 0.05) if d["n_in"] > 0 else (rb > hi + 0.05)
                res = (e, rh if sg < 0 else rl, fora_r)
        return res
    tot = {"area": 0.0, "comp": 0.0, "n": 0}
    for d in sorted(info, key=lambda d: d["eixo"] != "x"):  # X walls first
        P, ax, (s0, s1), zp = d["P"], d["eixo"], d["s"], d["zp"]
        so = -d["n_in"]                                     # direction to the outside
        u_cf_o = d["f_out"] + so * esp_ext                  # outer cladding face
        u_cf_i = d["f_in"] + d["n_in"] * d["esp_int"]       # roof-side face (cladding, or the gutter lining)
        u_o, u_i = u_cf_o + so * tl, u_cf_i + d["n_in"] * tl

        def z_sup(u, u_o=u_o, u_i=u_i, zp=zp):  # underside of the top: higher on the outside
            return zp + queda * (u - u_i) / (u_o - u_i)

        ext_ = {"canto": esp_ext + tl, "livre": esp_int + tl, "junta": 0.0}
        fim_p = [ate_parede(d, 0), ate_parede(d, 1)]
        if ax == "x":
            a, b = s0 - ext_[d["fins"][0]], s1 + ext_[d["fins"][1]]
            if fim_p[0]:
                a = min(a, fim_p[0][0])
            if fim_p[1]:
                b = max(b, fim_p[1][0])
        else:  # stop against the X chapéus that cover the corners; a free end short of a gutter wall runs on to it
            a = fim_p[0][0] if fim_p[0] else s0
            b = fim_p[1][0] if fim_p[1] else s1
            for fim in (0, 1):
                fc_ = face_caleira(casa, d, fim) if d["fins"][fim] == "livre" and not fim_p[fim] else None
                if fc_ is not None:
                    if fim == 0:
                        a = fc_ - 2 * tl
                    else:
                        b = fc_ + 2 * tl
            um = (d["f_out"] + d["f_in"]) / 2
            for (xa, xb), (ua, ub) in feitos:
                if xa - 0.001 <= um <= xb + 0.001:
                    if ua - 0.01 <= a <= ub + 0.01:
                        a = max(a, ub)
                    if ua - 0.01 <= b <= ub + 0.01:
                        b = min(b, ua)
        if b - a < 0.02:
            continue
        # outer leg over the whole length: past a re-entrant corner it closes the step down to the chapéu of the
        # wall below it
        oa, ob = a, b
        if ax == "x":  # at a re-entrant corner the outer leg stops where the wall across begins
            if fim_p[0] and fim_p[0][2]:
                oa = max(oa, fim_p[0][1])
            if fim_p[1] and fim_p[1][2]:
                ob = min(ob, fim_p[1][1])
        # inner leg: between the roof-side cladding of the walls across it
        ia, ib = a, b
        for r in info:
            if r["eixo"] == ax:
                continue
            ra, rb = r["s"]
            if not (ra - 0.01 <= d["f_in"] <= rb + 0.01):
                continue
            if not ((rb > d["f_in"] + 0.05) if d["n_in"] > 0 else (ra < d["f_in"] - 0.05)):
                continue  # that wall is not on the roof side of this one
            c_r = r["f_in"] + r["n_in"] * (r["esp_int"] + tl)
            if a - 0.01 <= c_r <= b + 0.01:
                if r["n_in"] > 0:
                    ia = max(ia, c_r)
                else:
                    ib = min(ib, c_r)
        lo, hi = sorted((u_o, u_i))
        pecas = [peca(ax, a, b, [(u_o, z_sup(u_o)), (u_i, z_sup(u_i)), (u_i, z_sup(u_i) + tl), (u_o, z_sup(u_o) + tl)])]
        if ob - oa > 0.01:
            pecas.append(peca(ax, oa, ob, placa(min(u_cf_o, u_o), max(u_cf_o, u_o), zp - desc, z_sup(u_o) + tl)))
        if ib - ia > 0.01:
            pecas.append(peca(ax, ia, ib, placa(min(u_cf_i, u_i), max(u_cf_i, u_i), zp - desc, z_sup(u_i) + tl)))
        for k, (sx, fim) in enumerate(((a, d["fins"][0]), (b, d["fins"][1]))):
            if ax == "x" and (fim in ("canto", "livre") or fim_p[k]):  # the end folds down over the corner
                e0, e1 = (sx, sx + tl) if k == 0 else (sx - tl, sx)
                pecas.append(peca(ax, e0, e1, [(u_o, zp - desc), (u_i, zp - desc), (u_i, z_sup(u_i) + tl),
                                               (u_o, z_sup(u_o) + tl)]))
        if ax == "x":
            feitos.append(((a, b), (lo, hi)))
        larg = hi - lo
        des = larg + 2 * desc + queda
        topos_ch.append((P.nome, ax, a, b, lo, hi))
        out.objeto(f"{ch['nome']} | {P.nome}", "6.3", ch["material"], pecas,
                   {"camada": ch["nome"], "produto": ch["produto"], "comprimento_m": round(b - a, 3),
                    "largura_m": round(larg, 3), "desenvolvimento_m": round(des, 3)})
        tot["comp"] += b - a
        tot["area"] += (b - a) * des
        tot["n"] += 1
    for i, (na, axa, a1, b1, l1, h1) in enumerate(topos_ch):  # no two chapéus on the same top
        ra = (a1, b1, l1, h1) if axa == "x" else (l1, h1, a1, b1)
        for nb, axb, a2, b2, l2, h2 in topos_ch[i + 1:]:
            rb = (a2, b2, l2, h2) if axb == "x" else (l2, h2, a2, b2)
            if min(ra[1], rb[1]) - max(ra[0], rb[0]) > 0.002 and min(ra[3], rb[3]) - max(ra[2], rb[2]) > 0.002:
                print(f"aviso: chapéus sobrepostos: {na} / {nb}")
    resumo.append(("6.3", ch["nome"], tot))


def camadas_platibanda(S):
    """The parapets' roof side: OSB 15 and Traspir on the frame, then the facade's own cladding (user 2026-10-28: "o
    capoto tem que ficar na casa toda a cobertura não tem um revestimento ou isolamento diferente"; was the Tremolo
    build-up of Torres Vedras for every house — user 2026-10-15, said on TV)."""
    pi_ = S["cobertura"]["platibanda_interior"]
    ext = S["exterior"]
    op = ext["opcoes"].get(ext.get("opcao_visivel", "A"))
    base = [c for c in pi_["camadas"] if c.get("id") in ("osb", "membrana")]
    return base + (op["camadas"] if op else [c for c in pi_["camadas"] if c.get("id") not in ("osb", "membrana")])


def platibanda_interior(casa, S, out, resumo):
    """Roof side of the parapets, from the roof panels up to the chapéu: wool in the frame, OSB 15, Traspir, then the
    house's own facade cladding (camadas_platibanda; user 2026-10-28 "o capoto tem que ficar na casa toda"; the
    ripado + Tremolo of 2026-10-15 is Torres Vedras', a Tremolo house). A parapet ending over the roof (free
    end, e.g. at the re-entrant corner of an L) is clad round its end too (user 2026-10-16: structure seen there)."""
    pi_ = S["cobertura"]["platibanda_interior"]
    tels = casa.G["cobertura"]["telhados"]
    e = S["cobertura"]["painel_oculto"]["espessura"]
    camadas = camadas_platibanda(S)
    esp_int = sum(c["espessura"] for c in camadas)

    def z_telhado(x, y):
        for t in tels:
            ya_, yb_ = min(t.get("y_parede", t["y_baixo"]), t["y_cume"]), max(t.get("y_parede", t["y_baixo"]), t["y_cume"])
            if t["x0"] - 0.2 <= x <= t["x1"] + 0.2 and ya_ - 0.5 <= y <= yb_ + 0.5:
                if "z_borda" in t and min(abs(y - t["y_baixo"]), abs(y - t.get("y_parede", t["y_baixo"]))) < 0.45 \
                        and abs(y - t["y_cume"]) > abs(t["y_baixo"] - t["y_cume"]):
                    return t["z_borda"]  # over the gutter: the cladding starts at the panel ends
                return t["z_cume"] - t["inclinacao"] * abs(y - t["y_cume"]) + e
        return None

    for k, cam in enumerate(camadas, 1):
        out.colecao(f"6.4.{k}", f"Platibanda (face da cobertura) | {cam['nome']}")
    out.colecao("6.4", "Platibanda | face da cobertura")
    tot = {k: {"area": 0.0, "comp": 0.0, "n": 0} for k in range(1, len(camadas) + 1)}
    faces, topos = [], []
    for d in platibandas(casa, S):
        P = d["P"]
        x0, x1, y0, y1 = P.pegada()
        u0, u1 = sorted((d["f_out"], d["f_in"]))
        if not d["forrada"]:  # lined by the gutter (D2503): only a free end standing over the roof is clad
            for s_, n_, fim in ((d["s"][0], -1, d["fins"][0]), (d["s"][1], 1, d["fins"][1])):
                if fim == "livre":
                    topos.append({"o": "x" if d["eixo"] == "x" else "y", "c": s_, "n": n_, "s0": u0, "s1": u1,
                                  "zp": d["zp"], "nome": P.nome, "forrada": False})
            continue
        # only along the roof: past its edge the parapet runs over the gutter wall (chapéu and facade cover it)
        if d["eixo"] == "x":
            face = {"o": "y", "c": d["f_in"], "n": d["n_in"], "s0": x0, "s1": x1}
            lim = [(t["x0"], t["x1"]) for t in tels
                   if min(t.get("y_parede", t["y_baixo"]), t["y_cume"]) - 0.3 <= face["c"] <=
                   max(t.get("y_parede", t["y_baixo"]), t["y_cume"]) + 0.3]
        else:
            face = {"o": "x", "c": d["f_in"], "n": d["n_in"], "s0": y0, "s1": y1}
            # the cladding runs to the end of the sandwich panels over the gutter (user 2026-10-19: "o forro é suposto
            # ir até ao final do painel sanduíche"); past them the gutter's end cap lines the parapet
            def y_fim(t):
                return t["y_baixo"] if "y_caleira" in t else t.get("y_parede", t["y_baixo"])
            lim = [(min(y_fim(t), t["y_cume"]), max(y_fim(t), t["y_cume"]))
                   for t in tels if t["x0"] - 0.3 <= face["c"] <= t["x1"] + 0.3]
        if not lim:
            continue
        a_, b_ = max(face["s0"], min(v[0] for v in lim)), min(face["s1"], max(v[1] for v in lim))
        # a free end: the cladding runs on over the end of the wall, and the end face is clad
        (sa, sb), o_fim = d["s"], ("x" if d["eixo"] == "x" else "y")
        u0, u1 = sorted((d["f_out"], d["f_in"]))
        ext_ = [None, None]  # per-layer extension at an outer corner: "w1" runs over the corner, "w0" stops
        for fim, s_ in ((0, sa), (1, sb)):
            if d["fins"][fim] != "livre" or abs((a_, b_)[fim] - s_) > 0.01:
                continue
            fc_ = face_caleira(casa, d, fim)
            if fc_ is not None:  # up to the lined face of the gutter wall, flush (the lining closes the corner)
                if fim == 0:
                    a_ = fc_
                else:
                    b_ = fc_
                continue
            ext_[fim] = "w1"
            topos.append({"o": o_fim, "c": s_, "n": -1 if fim == 0 else 1, "s0": u0, "s1": u1, "zp": d["zp"],
                          "nome": P.nome})
        if b_ - a_ < 0.05:
            continue
        face["s0"], face["s1"] = a_, b_
        faces.append({"face": face, "zp": d["zp"], "nome": P.nome, "oz": P.oz, "ext": ext_})
    for tp in topos:  # an end face continues the cladding of the wall it stands on, when there is one in line
        for f in faces:
            g = f["face"]
            if g["o"] == tp["o"] and abs(g["c"] - tp["c"]) < 0.01 and g["n"] == tp["n"]:
                if abs(g["s1"] - tp["s0"]) < 0.02:
                    g["s1"] = tp["s1"]
                    f["ext"][1] = "w0" if tp.get("forrada", True) else None
                    break
                if abs(g["s0"] - tp["s1"]) < 0.02:
                    g["s0"] = tp["s0"]
                    f["ext"][0] = "w0" if tp.get("forrada", True) else None
                    break
        else:
            faces.append({"face": {k: tp[k] for k in ("o", "c", "n", "s0", "s1")}, "zp": tp["zp"],
                          "nome": tp["nome"] + " (topo)", "oz": tp["zp"] - 1.0, "ext": [None, None]})

    def contorno(fd, a_, b_):
        face = fd["face"]
        if face["o"] == "y":
            pts = [a_, b_]
            zs = [z_telhado(x, face["c"] + face["n"] * 0.05) for x in pts]
        else:
            pts = sorted({a_, b_} | {t["y_cume"] for t in tels if a_ < t["y_cume"] < b_})
            zs = [z_telhado(face["c"] + face["n"] * 0.3, y) for y in pts]
        base = [(s_, z if z is not None else fd["oz"]) for s_, z in zip(pts, zs)]
        return base, clean(base + [(pts[-1], fd["zp"]), (pts[0], fd["zp"])])

    for fd in faces:
        face, zp = fd["face"], fd["zp"]
        base, _poly = contorno(fd, face["s0"], face["s1"])
        if all(zp - z < 0.03 for _s, z in base):
            continue
        w = 0.0
        for k, cam in enumerate(camadas, 1):
            w1 = w + cam["espessura"]
            e0, e1 = ({"w0": w, "w1": w1}.get(x, 0.0) for x in fd["ext"])
            base, poly = contorno(fd, face["s0"] - e0, face["s1"] + e1)
            pecas, t2 = dispor(cam, face, [poly], [], w, w1, face["s0"] - e0, min(z for _s, z in base))
            out.objeto(f"{cam['nome']} | platibanda {fd['nome']}", f"6.4.{k}", cam["material"], pecas,
                       props_camada(cam, area_m2=t2["area"], comprimento_m=t2["comp"], pecas=t2["n"],
                                    espessura_m=cam["espessura"]))
            for q in tot[k]:
                tot[k][q] += t2[q]
            w = w1
    for k, cam in enumerate(camadas, 1):
        resumo.append((f"6.4.{k}", cam["nome"] + " (platibanda)", tot[k]))


def caixilharia(casa, S, out, resumo):
    """Windows, doors and the garage door in the rough openings of the exterior modules (TV: the user's table
    "PROJETO APROVADO", 2026-10-19). Each item names the module (D2503) it sits in; the element (maker's size)
    is centred in the rough opening, at the outer side of the module, and an exterior roller-shutter box
    (estore) fills the rough opening above it. Every opening gets remates round the frame so the wall layers are not
    exposed (user 2026-10-20): outside a folded aluminium lining of the reveal, from the frame to the cladding face,
    with a return over the clearance and a flange on the cladding, and a sill with a drip under the windows; inside
    a lining of the reveal to the interior finish."""
    C = S.get("caixilharia")
    if not C or not C.get("itens"):
        return
    aro, fo, vd, fg = C["aro"], C["folha"], C["vidro"], C.get("folga", 0.01)
    out.colecao("7", "Caixilharia")
    out.colecao("7.1", "Aros e folhas (alumínio)")
    out.colecao("7.2", "Vidros")
    out.colecao("7.3", "Estores exteriores")
    out.colecao("7.4", "Portas e portão")
    out.colecao("7.5", "Remates exteriores dos vãos")
    out.colecao("7.6", "Remates interiores dos vãos")
    tot = {"area": 0.0, "comp": 0.0, "n": 0}
    tot_r = {"area": 0.0, "comp": 0.0, "n": 0}
    ex_ = S["exterior"]
    op_ = ex_["opcoes"][ex_.get("opcao_visivel", "A")]
    esp_ext = ex_["osb"]["espessura"] + ex_["membrana"]["espessura"] + sum(c["espessura"] for c in op_["camadas"])
    esp_int = S["interior"]["osb"]["espessura"] + S["interior"]["acabamento"]["espessura"]
    rm = C.get("remates", {})
    tr, ab_r, pin = rm.get("espessura", 0.002), rm.get("aba", 0.03), rm.get("pingadeira", 0.03)
    ti_r = rm.get("espessura_interior", 0.013)
    pe = [P for P in casa.paineis if P.tipo == "PE" and P.piso == 0 and P.aberturas]

    def bloco(P, u0, u1, v0, v1, w0, w1):
        a, b = sorted((w0, w1))
        base = [P.mundo(u0, v0, a), P.mundo(u1, v0, a), P.mundo(u1, v1, a), P.mundo(u0, v1, a)]
        return prisma(base, (-P.uy * (b - a), P.ux * (b - a), 0.0))

    def no_sitio(it):
        """(module, opening) of an item given by wall and position — the configurator's houses, whose modules the
        divider names (the company drawings' items name their module instead)."""
        for Q in pe:
            if Q.nome.split()[1].split(".")[0] != it["parede"]:
                continue
            u = it["s"] - (Q.ox if abs(Q.ux) > 0.5 else Q.oy)
            for a in Q.aberturas:
                if a[0] - 0.01 <= u <= a[1] + 0.01:
                    return Q, a
        return None, None

    for it in C["itens"]:
        if "modulo" in it:
            P = next((Q for Q in pe if Q.nome.endswith(f"({it['modulo']})")), None)
        else:
            P, ab = no_sitio(it)
        rotulo = it.get("modulo") or f"{it.get('parede')} em {it.get('s', 0):.2f}"
        if P is None:
            print(f"aviso: caixilharia {rotulo}: módulo sem vão")
            continue
        if "modulo" in it:
            ab = min(P.aberturas, key=lambda a: abs((a[1] - a[0]) - it["largura"]))
        u0, u1, v0, v1 = ab[0], ab[1], ab[2], ab[3]
        W, H = u1 - u0, v1 - v0
        porta = it["tipo"] in ("porta", "seccionado")
        we = min(it["largura"], W - 2 * fg)
        caixa_h = max(0.0, H - fg - it["altura"]) if it.get("estore") else 0.0
        he = min(it["altura"], H - (fg if porta else 2 * fg) - caixa_h)
        if we < it["largura"] - 2 * fg - 0.01 or he < it["altura"] - 2 * fg - 0.01:  # beyond the fitting clearance (+ drawing precision)
            print(f"aviso: caixilharia {rotulo}: {it['largura']:.2f} x {it['altura']:.2f} não cabe no vão "
                  f"{W:.2f} x {H:.2f} -> modelado {we:.2f} x {he:.2f}")
        ua, ub = u0 + (W - we) / 2, u0 + (W + we) / 2
        va = v0 + (0.0 if porta else fg)
        vb = va + he
        s_ = 1.0 if P.fora > 0 else -1.0     # w of the outside face
        w_out = s_ * P.t / 2
        w_in = w_out - s_ * aro["profundidade"]
        wm = (w_out + w_in) / 2
        al, vi, es, pt = [], [], [], []
        f = aro["face"]
        al += [bloco(P, ua, ua + f, va, vb, w_out, w_in), bloco(P, ub - f, ub, va, vb, w_out, w_in),
               bloco(P, ua, ub, vb - f, vb, w_out, w_in)]
        if not porta:
            al.append(bloco(P, ua, ub, va, va + f, w_out, w_in))
        ia, ib, ja, jb = ua + f, ub - f, (va if porta else va + f), vb - f
        tipo = it["tipo"]
        if tipo == "fixo":
            vi.append(bloco(P, ia, ib, ja, jb, wm - vd / 2, wm + vd / 2))
        elif tipo == "basculante":
            al += [bloco(P, ia, ia + fo, ja, jb, wm - 0.02, wm + 0.02), bloco(P, ib - fo, ib, ja, jb, wm - 0.02, wm + 0.02),
                   bloco(P, ia, ib, ja, ja + fo, wm - 0.02, wm + 0.02), bloco(P, ia, ib, jb - fo, jb, wm - 0.02, wm + 0.02)]
            vi.append(bloco(P, ia + fo, ib - fo, ja + fo, jb - fo, wm - vd / 2, wm + vd / 2))
        elif tipo == "correr":  # two leaves on two tracks, overlapping in the middle
            meio = (ia + ib) / 2
            for k, (fa, fb) in enumerate(((ia, meio + fo / 2), (meio - fo / 2, ib))):
                wc = wm + s_ * (0.017 if k == 0 else -0.017)
                al += [bloco(P, fa, fa + fo, ja, jb, wc - 0.015, wc + 0.015), bloco(P, fb - fo, fb, ja, jb, wc - 0.015, wc + 0.015),
                       bloco(P, fa, fb, ja, ja + fo, wc - 0.015, wc + 0.015), bloco(P, fa, fb, jb - fo, jb, wc - 0.015, wc + 0.015)]
                vi.append(bloco(P, fa + fo, fb - fo, ja + fo, jb - fo, wc - vd / 2, wc + vd / 2))
        elif tipo == "porta":  # painel liso
            pt.append(bloco(P, ia, ib, ja, jb, wm - 0.025, wm + 0.025))
        elif tipo == "seccionado":  # garage door: horizontal sections
            n = it.get("seccoes", 5)
            hs = (jb - ja) / n
            for k in range(n):
                pt.append(bloco(P, ia, ib, ja + k * hs + 0.003, ja + (k + 1) * hs - 0.003, wm - 0.02, wm + 0.02))
        if caixa_h > 0.02:  # roller-shutter box over the element, guides at its sides
            es.append(bloco(P, u0 + fg, u1 - fg, vb + 0.002, v1 - fg, w_out, w_out - s_ * C["estore"]["profundidade"]))
            g = C["estore"]["guia"]
            es += [bloco(P, ua - g, ua, va, vb, w_out, w_out - s_ * 0.04), bloco(P, ub, ub + g, va, vb, w_out, w_out - s_ * 0.04)]
        # remates (outside: reveal lining, return over the clearance, flange on the cladding; sill with a drip)
        w_cl = w_out + s_ * esp_ext
        w_if = -s_ * (P.t / 2 + esp_int)
        topo_el = (v1 - fg) if caixa_h > 0.02 else vb
        re_, ri_ = [], []
        re_ += [bloco(P, u0, u0 + tr, v0, v1, w_out, w_cl), bloco(P, u1 - tr, u1, v0, v1, w_out, w_cl),
                bloco(P, u0, u1, v1 - tr, v1, w_out, w_cl),
                bloco(P, u0, ua + 0.01, v0, v1, w_out, w_out + s_ * tr), bloco(P, ub - 0.01, u1, v0, v1, w_out, w_out + s_ * tr),
                bloco(P, u0, u1, topo_el - 0.01, v1, w_out, w_out + s_ * tr),
                bloco(P, u0 - ab_r, u0 + tr, v0, v1 + ab_r, w_cl, w_cl + s_ * tr),
                bloco(P, u1 - tr, u1 + ab_r, v0, v1 + ab_r, w_cl, w_cl + s_ * tr),
                bloco(P, u0 - ab_r, u1 + ab_r, v1 - tr, v1 + ab_r, w_cl, w_cl + s_ * tr)]
        no_chao = v0 <= 0.05  # openings down to the floor: no sill
        if not porta and not no_chao:  # sill (peitoril) over the bottom of the reveal, projecting with a drip
            re_ += [bloco(P, u0 - ab_r, u1 + ab_r, v0 - tr, v0, w_out, w_cl + s_ * pin),
                    bloco(P, u0, u1, v0, va + 0.01, w_out, w_out + s_ * tr)]
        w_i0 = w_in if caixa_h <= 0.02 else w_out - s_ * C["estore"]["profundidade"]
        ri_ += [bloco(P, u0, u0 + ti_r, v0, v1, w_in, w_if), bloco(P, u1 - ti_r, u1, v0, v1, w_in, w_if),
                bloco(P, u0, u1, v1 - ti_r, v1, w_i0, w_if)]
        if not porta and not no_chao:
            ri_.append(bloco(P, u0, u1, v0, v0 + ti_r, w_in, w_if))
        per = 2 * H + W + (0.0 if (porta or no_chao) else W)
        tot_r["comp"] += per
        tot_r["n"] += 1
        nome = f"{rotulo} {it['divisao']} — {it['descricao_curta']} {it['largura']:.2f} x {it['altura']:.2f}".replace(".", ",")
        props = {"camada": "Caixilharia", "divisao": it["divisao"], "produto": it["descricao"], "largura_m": it["largura"],
                 "altura_m": it["altura"], "area_m2": round(it["largura"] * it["altura"], 3), "modulo": rotulo,
                 "vao_bruto_m": f"{W:.2f} x {H:.2f}", "estore_exterior": bool(it.get("estore")),
                 "vidro": it.get("vidro", ""), "observacoes": it.get("observacoes", "")}
        for cid, mat, pecas, suf in (("7.1", C["material"], al, "aro e folhas"), ("7.2", C["vidros"].get(it.get("vidro", "transparente"), "Vidro"), vi, "vidro"),
                                     ("7.3", C["material"], es, "estore"), ("7.4", C["material_portas"] if tipo == "seccionado" else C["material"], pt, "painel")):
            if pecas:
                out.objeto(f"{nome} | {suf}", cid, mat, pecas, props)
        out.objeto(f"{nome} | remates exteriores", "7.5", rm.get("material", "Remate RAL 7016"), re_,
                   {"camada": "Remates exteriores dos vãos", "produto": rm.get("produto", ""), "comprimento_m": round(per, 3),
                    "modulo": rotulo})
        out.objeto(f"{nome} | remates interiores", "7.6", rm.get("material_interior", "Pladur N"), ri_,
                   {"camada": "Remates interiores dos vãos", "produto": rm.get("produto_interior", ""),
                    "comprimento_m": round(per, 3), "modulo": rotulo})
        tot["area"] += it["largura"] * it["altura"]
        tot["n"] += 1
    resumo.append(("7", "Caixilharia (vãos da tabela)", tot))
    resumo.append(("7.5", "Remates dos vãos (exteriores e interiores)", tot_r))


def pergola_cobertura(casa, S, out, resumo):
    """Covering of the pergola (geometry "pergola", casa_planta.py): tiles on the slats, falling to the front,
    up to the finished faces of the house; an exposed gutter along the whole front and downpipes down the posts
    (TV, user 2026-10-19 with the photo of the finished house: "a pérgola vai até ao comprimento total da casa e
    leva telha e uma caleira à vista em todo o comprimento")."""
    pg = casa.G.get("pergola")
    if not pg or not pg.get("telha"):
        return
    te, ca = pg["telha"], pg.get("caleira") or {}
    s_, y_fr, incl = pg["s"], pg["y_frente"], pg["inclinacao"]
    x0, x1 = pg["x0"], pg["x1"]
    acab = [tuple(p) for p in pg["contorno_acabado"]]

    def y_de(u):
        return y_fr + s_ * u

    def z_de(u):  # underside of the tiles (top of the slats)
        return pg["z_ripas_u0"] + incl * u

    def dentro_x(y):  # x intervals of the house at y (scanline of the finished outline)
        xs = sorted(p[0] for p, q in zip(acab, acab[1:] + acab[:1])
                    if abs(p[0] - q[0]) < 1e-9 and min(p[1], q[1]) <= y < max(p[1], q[1]))
        return list(zip(xs[0::2], xs[1::2]))

    def livres(ocup):
        res = [(x0, x1)]
        for o0, o1 in ocup:
            res = [r for r0, r1 in res for r in ((r0, min(r1, o0)), (max(r0, o1), r1)) if r[1] - r[0] > 0.02]
        return res

    out.colecao("8", "Pérgola | cobertura")
    out.colecao("8.1", "Telha da pérgola")
    out.colecao("8.2", "Caleira à vista e tubos de queda")
    # tiles: courses along the slope, broken at the facade lines so each stops at the facade
    e, bei, fia = te.get("espessura", 0.05), te.get("beiral", 0.10), te.get("fiada", 0.40)
    us = {round(-bei, 4), round(pg["u_max"], 4)}
    u = -bei
    while u < pg["u_max"]:
        us.add(round(u, 4))
        u += fia
    for f in pg.get("faces", []):
        us.add(round(s_ * (f["y_fora"] - y_fr), 4))
    us = sorted(v for v in us if -bei - 1e-6 <= v <= pg["u_max"] + 1e-6)
    pecas, area = [], 0.0
    ct = math.sqrt(1 + incl * incl)
    for ua, ub in zip(us, us[1:]):
        if ub - ua < 0.01:
            continue
        ya, yb = sorted((y_de(ua), y_de(ub)))
        for xa, xb in livres(dentro_x(ya + 1e-4) + dentro_x(yb - 1e-4)):
            base = [(xa, y_de(ua), z_de(ua)), (xa, y_de(ub), z_de(ub)), (xa, y_de(ub), z_de(ub) + e),
                    (xa, y_de(ua), z_de(ua) + e + 0.015)]  # thicker at the lower edge: the tile course
            pecas.append(prisma(base, (xb - xa, 0.0, 0.0)))
            area += (xb - xa) * (ub - ua) * ct
    out.objeto("Telha | pérgola", "8.1", te.get("material", "Telha"), pecas,
               {"camada": "Telha da pérgola", "produto": te.get("produto", ""), "area_m2": round(area, 3),
                "inclinacao_pct": round(incl * 100, 1)})
    resumo.append(("8.1", "Telha da pérgola", {"area": area, "comp": 0.0, "n": len(pecas)}))
    if not ca:
        return
    # exposed gutter under the front edge of the tiles, along the whole front
    lg, al, tl = ca.get("largura", 0.12), ca.get("altura", 0.10), ca.get("espessura", 0.002)
    zt = z_de(-bei) - 0.01
    zb_ = zt - al
    ua, ub = -bei - lg, -bei + 0.02
    ya, yb = sorted((y_de(ua), y_de(ub)))
    yo = sorted((y_de(ua), y_de(ua + tl)))
    yi = sorted((y_de(ub - tl), y_de(ub)))
    pc = [caixa(x0, x1, ya, yb, zb_, zb_ + tl), caixa(x0, x1, yo[0], yo[1], zb_, zt), caixa(x0, x1, yi[0], yi[1], zb_, zt),
          caixa(x0, x0 + tl, ya, yb, zb_, zt), caixa(x1 - tl, x1, ya, yb, zb_, zt)]
    mat = ca.get("material", "Remate RAL 7016")
    out.objeto("Caleira à vista | pérgola", "8.2", mat, pc,
               {"camada": "Caleira à vista da pérgola", "produto": ca.get("produto", ""), "comprimento_m": round(x1 - x0, 3)})
    # downpipes from the gutter down the chosen posts
    tb = ca.get("tubo", {}).get("largura", 0.08)
    comp_t = 0.0
    for k in ca.get("tubos_queda_pilares", []):
        xc, _yc = pg["pilares"][k - 1]
        uc = -bei - lg / 2
        yt = sorted((y_de(uc - tb / 2), y_de(uc + tb / 2)))
        z0 = ca.get("tubo", {}).get("folga_base", 0.05)
        out.objeto(f"Tubo de queda | pérgola pilar {k}", "8.2", mat,
                   [caixa(xc - tb / 2, xc + tb / 2, yt[0], yt[1], z0, zb_)],
                   {"camada": "Tubo de queda da pérgola", "comprimento_m": round(zb_ - z0, 3)})
        comp_t += zb_ - z0
    resumo.append(("8.2", "Caleira à vista e tubos de queda", {"area": 0.0, "comp": (x1 - x0) + comp_t, "n": 1}))


# ============================================================================ main
def teto_sob_anel(S, cfg):
    """A hidden roof (the exterior modules run to the parapet top, the amarração as a ring on their inner face): the false
    ceiling hangs from the ceiling beams below that ring (as Torres Vedras, 0,1185; user 2026-10-21: "os tetos falsos
    ficam presos as vigas de 22x7,5 através dos perfis de teto e das calhas de suspensão"), unless the project sets its
    own suspension. The same S for casa_planta.py and camadas.py, so the heights agree."""
    if (cfg.get("cobertura") or {}).get("tipo") != "platibanda" or not S["estrutura"].get("platibanda_modulos_inteiros", True):
        return S
    if "folga" in ((((cfg.get("camadas") or {}).get("tetos") or {}).get("suspensao")) or {}):
        return S
    sus = S["tetos"]["suspensao"]
    sus["folga"] = max(sus["folga"], round(S["estrutura"]["lameladas"]["amarracao"]["altura"] + 0.0085, 4))
    return S


def gerar(cfg_path, geometria=None):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    base = Path(cfg_path).resolve().parent
    G = json.load(open(geometria or base / cfg["saida"]["geometria"], encoding="utf-8"))
    S = teto_sob_anel(fundir(json.load(open(AQUI / "sistema_construtivo.json", encoding="utf-8")), cfg.get("camadas") or {}), cfg)
    casa = Casa(G)
    out, resumo = Saida(), []
    exterior(casa, S, out, resumo)
    caixilharia(casa, S, out, resumo)
    pergola_cobertura(casa, S, out, resumo)
    isolamento(casa, S, out, resumo)
    interior(casa, S, out, resumo)
    deck = pavimentos(casa, S, out, resumo)
    tetos(casa, S, out, resumo)
    (cobertura_platibanda if casa.platibanda else cobertura_faces if casa.faces else cobertura)(casa, S, out, resumo)
    doc = {"nome": cfg["nome"], "materiais": S["materiais"], "colecoes": out.colecoes, "objetos": out.objetos,
           "etiquetas": out.etiquetas, "colecao_osb_pavimento": deck,
           "z_cobertura_cume": R(casa.z_cob_cume(S)), "sistema": casa.sistema,
           "opcao_visivel": S["exterior"].get("opcao_visivel", "A"),
           "opcoes": {k: v["nome"] for k, v in S["exterior"]["opcoes"].items()},
           "divisoes": {k: round(v, 2) for k, v in getattr(casa, "area_util", {}).items()},
           "aberturas": {P.nome: [[round(x, 3) for x in a[:4]] + [a[4]] for a in P.aberturas]
                         for P in casa.paineis if P.aberturas}}
    return doc, resumo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--saida")
    ap.add_argument("--geometria", help="geometry JSON to use (default: config saida.geometria)")
    a = ap.parse_args()
    cfg_path = Path(a.config).resolve()
    doc, resumo = gerar(cfg_path, a.geometria)
    saida = Path(a.saida) if a.saida else pasta_trabalho("modelos", cfg_path.parent.name) / "camadas.json"
    saida.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    npecas = sum(len(o["pecas"]) for o in doc["objetos"])
    print(f"camadas: {len(doc['objetos'])} objects, {npecas} pieces, {len(doc['divisoes'])} rooms -> {saida}")
    for cid, nome, t in resumo:
        extra = (f"{t['area']:.1f} m2" if t["area"] else "") + (f"  {t['comp']:.1f} m" if t["comp"] else "")
        print(f"  {cid:6s} {nome:38s} {t['n']:5d} pcs  {extra}")
    print("  rooms: " + ", ".join(f"{k} {v} m2" for k, v in doc["divisoes"].items()))


if __name__ == "__main__":
    main()
