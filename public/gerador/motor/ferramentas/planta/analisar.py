"""Floor-plan analysis of ANY architecture drawing: walls, openings, outside, rooms. Pure Python (runs in the browser).

    python ferramentas/planta/analisar.py "<drawing>.dwfx|.pdf" [--folha N] [--regiao X0 Y0 X1 Y1] [--escala 100]
           [--saida plan.json] [--png check.png]

User 2026-11-11: «cada projeto pode ter cores diferentes ou então simplesmente não usar o vermelho, tens de conseguir
ler qualquer documento e construir qualquer casa» and «leitura de qualquer tipo de parede e conseguires analisar
qualquer tipo de planta». So nothing here depends on a colour or a layer convention: a wall is recognised by its SHAPE.

1. The region of the sheet is drawn into a binary image at 2 cm per pixel (every stroke and every small fill; texture
   strokes shorter than 6 cm — floor stipple — are left out; thick strokes are drawn with their width).
2. Wall mask: what stays solid after closing the image (hatching, insulation crosses and poché merge) and opening it
   (thin lines — furniture, door swings, dimensions, text — go away), plus the empty cores of walls drawn as two lines
   only (thin, long, empty bands bounded by two lines; stacked bands — stairs, decking, hatching — are rejected),
   minus solid blobs too thick to be a wall (hatched floors).
3. Wall faces: the drawing's own straight lines (any angle) that have the wall mask on one side and free space on the
   other; a wall = two facing faces 5–50 cm apart with the mask between. Collinear pieces of the same thickness are
   joined across junctions; a gap of 0,40–3,60 m between them is an opening: a DOOR when a swing (an arc centred on a
   jamb, or the leaf) is drawn beside it, a WINDOW when glazing lines (or a thinner band) run inside the wall, else a
   passage.
4. With the openings bridged, the outside is flooded from the border: walls with outside on one side are exterior,
   the enclosed free regions of at least 1 m² are the rooms.
5. Scale: when not given, the plausible ones for the region's size are tried (1:20 … 1:500) and the one giving the
   most coherent house wins (closed outline, rooms, wall thicknesses, doors).

Output: {"escala", "regiao", "paredes" (any angle: p0, p1 in metres, y up, origin at the bottom-left of the walls),
"divisoes", "contorno", "nota"} and, when every wall follows two perpendicular directions, "eixos": the same plan
turned to them in the format of modelo/planta_arquitetura.py (eixo x|y, s0, s1, c, espessura, exterior,
lado_exterior, aberturas), which the configurator chain (documentos/de_desenhos.py) builds the house from.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.planta.mascara import Mascara, profundidade  # noqa: E402

RES = 0.02                 # m per pixel
ESP = (0.05, 0.50)         # m: wall thickness
VAO = (0.40, 3.60)         # m: opening width
COMP_TEXTURA = 0.06        # m: shorter subpaths are texture (stipple), not drawing
FECHO, ABERTURA = 2, 2     # px: closing joins hatching up to ~8 cm, opening drops lines thinner than ~10 cm
FACE_MIN = 0.20            # m: shortest face run
ANG_TOL = math.radians(1.0)
ESCALAS = (20, 50, 75, 100, 150, 200, 250, 500)


# ============================================================================ 1. the drawing as primitives
def _comprimento(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def _area(pts):
    a = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        a += x0 * y1 - x1 * y0
    return abs(a) / 2


def primitivas(paths, regiao, escala):
    """Strokes and fills of the region in metres, image frame (x right, y down, origin at the region's corner).
    Returns (tracos [(pts, largura_m, cor)], preenchimentos [(pts, cor)])."""
    x0, y0, x1, y1 = regiao
    k = escala / 1000.0
    tracos, cheios = [], []
    for p in paths:
        for sp, cl in p["subs"]:
            if len(sp) < 2 or not any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in sp):
                continue
            pts = [((x - x0) * k, (y - y0) * k) for x, y in sp]
            if cl and pts[0] != pts[-1]:
                pts.append(pts[0])
            if p.get("fill") and len(pts) >= 4:
                cheios.append((pts, p["fill"]))
            if p.get("stroke"):
                tracos.append((pts, (p.get("sw") or 0) * k, p["stroke"]))
    return tracos, cheios


# ============================================================================ 2. the image and the wall mask
def imagem(tracos, cheios, largura_m, altura_m):
    """The drawing as ink (Mascara) at RES. Small or thin fills are solid; big fills (floors, terrain) only outlined.
    The solid fills are also kept apart (m.preenchido): poché is the strongest sign of a wall."""
    w, h = int(largura_m / RES) + 1, int(altura_m / RES) + 1
    m = Mascara(w, h)
    pre = Mascara(w, h)
    for pts, cor in cheios:
        a = _area(pts)
        per = _comprimento(pts) or 1e-9
        if a <= 1.0 or 2 * a / per <= ESP[1]:     # poché pieces, hatch fills, a wall drawn as one filled outline
            pre.poligono([(x / RES, y / RES) for x, y in pts])
    m.r = list(pre.r)
    m.preenchido = pre
    for pts, larg, cor in tracos:
        if _comprimento(pts) < COMP_TEXTURA:
            continue
        if larg >= 2 * RES:                       # a heavy stroke: drawn with its width (walls drawn as one thick line)
            for a, b in zip(pts, pts[1:]):
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                if L < 1e-9:
                    continue
                nx, ny = -(b[1] - a[1]) / L * larg / 2, (b[0] - a[0]) / L * larg / 2
                m.poligono([((a[0] + nx) / RES, (a[1] + ny) / RES), ((b[0] + nx) / RES, (b[1] + ny) / RES),
                            ((b[0] - nx) / RES, (b[1] - ny) / RES), ((a[0] - nx) / RES, (a[1] - ny) / RES)])
        for a, b in zip(pts, pts[1:]):
            m.segmento(a[0] / RES, a[1] / RES, b[0] / RES, b[1] / RES)
    return m


def _dilatar_esparso(linhas, n, w):
    cheia = (1 << w) - 1
    cur = dict(linhas)
    for _ in range(n):
        hh = {y: (b | (b << 1) | (b >> 1)) & cheia for y, b in cur.items()}
        novo = {}
        for y, b in hh.items():
            for yy in (y - 1, y, y + 1):
                if yy >= 0:
                    novo[yy] = novo.get(yy, 0) | b
        cur = novo
    return cur


def nucleos_de_parede(tinta, fora_px):
    """Empty cores of walls drawn as two lines only: thin (5–45 cm), long (>= 3 x thickness, >= 0,5 m) free regions,
    not stacked between other such bands (stairs, decking, hatching are). Returns {row: bits}."""
    livre = tinta.inverso()
    # only the thin parts of the free space: a wall core open at one end (a passage without jambs) would otherwise run
    # into the room and stop looking like a band
    largo = livre.abrir(int(0.25 / RES))
    fino = livre.menos(largo.dilatar(1))
    cands = []
    for c in fino.componentes(area_min=int(0.04 / RES / RES)):
        x0, y0, x1, y1 = c["caixa"]
        if (x0 <= 0 or y0 <= 0 or x1 >= tinta.w - 1 or y1 >= tinta.h - 1) or c["area"] * RES * RES > 12:
            continue
        d = profundidade(c["linhas"])
        esp = (2 * d + 1) * RES
        comp = c["area"] * RES * RES / max(esp, RES)
        if ESP[0] <= esp <= 0.45 and comp >= max(0.5, 3 * esp):
            c["esp"] = esp
            cands.append(c)
    out = {}
    for c in cands:
        # bands of about the same width around it: a pattern (stairs, decking, hatching), not a wall. A wall's core
        # beside decking has bands on one side only, and of another width.
        iguais = {}
        for o in cands:
            if o is not c and abs(o["esp"] - c["esp"]) <= 0.35 * c["esp"]:
                for y, b in o["linhas"].items():
                    iguais[y] = iguais.get(y, 0) | b
        perto = _dilatar_esparso(c["linhas"], 1, tinta.w)
        anel = _dilatar_esparso(c["linhas"], 4, tinta.w)
        n_anel = n_banda = 0
        for y, b in anel.items():
            r = b & ~perto.get(y, 0)
            n_anel += r.bit_count()
            n_banda += (r & iguais.get(y, 0)).bit_count()
        if n_anel and n_banda / n_anel > 0.3:
            continue
        for y, b in _dilatar_esparso(c["linhas"], 1, tinta.w).items():
            if y < tinta.h:
                out[y] = out.get(y, 0) | b
    return out


def mascara_paredes(tinta):
    """The wall mask (see the module docstring)."""
    solido = tinta.fechar(FECHO).abrir(ABERTURA)
    nuc = nucleos_de_parede(tinta, None)
    r = list(solido.r)
    for y, b in nuc.items():
        if y < len(r):
            r[y] |= b & solido.cheia
    S = Mascara(tinta.w, tinta.h, r)
    raio = int(0.30 / RES) + 1                    # a 60 cm square fits: a hatched floor or decking, not a wall
    grosso = S.abrir(raio)
    if not grosso.vazia():
        S = S.menos(grosso.dilatar(1))
    pre = getattr(tinta, "preenchido", None)
    if pre is not None:                           # poché stays a wall even beside a merged hatching
        poche = pre.abrir(1)
        poche = poche.menos(poche.abrir(raio))
        S = S.ou(poche)
    return S


# ============================================================================ 3. wall faces and walls
def _segmentos(tracos, cheios):
    """Straight pieces of the drawing (strokes and fill edges), in metres, image frame: [(x0, y0, x1, y1)]."""
    out = []
    for pts, _l, _c in tracos:
        out += [(a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:])]
    for pts, _c in cheios:
        out += [(a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:])]
    return [s for s in out if math.hypot(s[2] - s[0], s[3] - s[1]) >= 0.02]


def linhas_retas(segs, cx, cy):
    """Collinear segments merged into lines: [(theta, c, [(s0, s1)])], theta in [0, pi), c = offset along the normal
    (-sin, cos) from (cx, cy), s along (cos, sin)."""
    itens = []
    for x0, y0, x1, y1 in segs:
        th = math.atan2(y1 - y0, x1 - x0) % math.pi
        u, n = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))
        a, b = (x0 - cx, y0 - cy), (x1 - cx, y1 - cy)
        c = (a[0] * n[0] + a[1] * n[1] + b[0] * n[0] + b[1] * n[1]) / 2
        sa, sb = a[0] * u[0] + a[1] * u[1], b[0] * u[0] + b[1] * u[1]
        itens.append((th, c, min(sa, sb), max(sa, sb)))
    # angles near pi wrap to 0
    itens = [(th - math.pi, -c, -s1, -s0) if th > math.pi - ANG_TOL / 2 else (th, c, s0, s1) for th, c, s0, s1 in itens]
    itens.sort()
    grupos, g = [], []
    for it in itens:
        if g and it[0] - g[-1][0] > ANG_TOL / 2:
            grupos.append(g)
            g = []
        g.append(it)
    if g:
        grupos.append(g)
    out = []
    for g in grupos:
        th = sum(i[0] * (i[3] - i[2]) for i in g) / max(1e-9, sum(i[3] - i[2] for i in g))
        u, n = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))
        # re-project on the common angle
        proj = []
        for th0, c0, s0, s1 in g:
            u0, n0 = (math.cos(th0), math.sin(th0)), (-math.sin(th0), math.cos(th0))
            pa = (c0 * n0[0] + s0 * u0[0], c0 * n0[1] + s0 * u0[1])
            pb = (c0 * n0[0] + s1 * u0[0], c0 * n0[1] + s1 * u0[1])
            c = ((pa[0] + pb[0]) * n[0] + (pa[1] + pb[1]) * n[1]) / 2
            sa, sb = pa[0] * u[0] + pa[1] * u[1], pb[0] * u[0] + pb[1] * u[1]
            proj.append((c, min(sa, sb), max(sa, sb)))
        proj.sort()
        bloco = []
        for c, s0, s1 in proj + [(1e18, 0, 0)]:
            if bloco and c - bloco[-1][0] > 0.01:
                cm = sum(b[0] * (b[2] - b[1]) for b in bloco) / max(1e-9, sum(b[2] - b[1] for b in bloco))
                iv = []
                for _c, a, b in sorted(bloco, key=lambda t: t[1]):
                    if iv and a <= iv[-1][1] + 0.02:
                        iv[-1][1] = max(iv[-1][1], b)
                    else:
                        iv.append([a, b])
                iv = [(a, b) for a, b in iv if b - a >= 0.05]
                if iv:
                    out.append((th, cm, iv))
                bloco = []
            bloco.append((c, s0, s1))
    return out


class Plano:
    """Image-frame geometry helpers around the region centre (cx, cy) for one wall mask."""

    def __init__(self, S, cx, cy):
        self.S, self.cx, self.cy = S, cx, cy

    def ponto(self, th, c, s):
        u, n = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))
        return (self.cx + c * n[0] + s * u[0], self.cy + c * n[1] + s * u[1])

    def em(self, x, y, M=None):
        M = M or self.S
        return bool(M.bit(int(x / RES), int(y / RES)))

    def cheio(self, th, c, esp, a, b, minimo=0.9):
        """The wall mask fills the strip [a, b] across the wall's whole thickness (centre and +-35 %): a junction
        where another wall crosses, not an opening (a window's glazing band is thinner than the wall)."""
        for dc in (0.0, -0.35 * esp, 0.35 * esp):
            n = n_ok = 0
            s = a
            while s <= b:
                x, y = self.ponto(th, c + dc, s)
                n += 1
                n_ok += self.em(x, y)
                s += RES
            if not n or n_ok / n < minimo:
                return False
        return True


def faces(P, linhas):
    """Runs of the lines that have the wall mask on exactly one side: [(theta, c, s0, s1, lado)], lado +1 when the
    wall lies on the +normal side."""
    out = []
    d = 2.5 * RES
    passo = RES
    for th, c, ivs in linhas:
        n = (-math.sin(th), math.cos(th))
        for a, b in ivs:
            if b - a < FACE_MIN:
                continue
            k = int((b - a) / passo)
            run, ini = None, a
            marcas = []
            for i in range(k + 1):
                s = a + i * passo
                x, y = P.ponto(th, c, s)
                mais = P.em(x + n[0] * d, y + n[1] * d)
                menos = P.em(x - n[0] * d, y - n[1] * d)
                marcas.append(1 if mais and not menos else (-1 if menos and not mais else 0))
            # runs, bridging one-sample breaks
            i = 0
            while i < len(marcas):
                v = marcas[i]
                if v == 0:
                    i += 1
                    continue
                j = i
                while j + 1 < len(marcas) and (marcas[j + 1] == v or (j + 2 < len(marcas) and marcas[j + 2] == v)):
                    j += 1
                s0, s1 = a + i * passo, a + j * passo
                if s1 - s0 >= FACE_MIN:
                    out.append((th, c, s0, s1, v))
                i = j + 1
    return out


def faces_exteriores(fs, junto=0.06):
    """Of parallel faces on the same side less than 6 cm apart (finish, render, ETICS lines of one wall surface) only
    the outermost stays, over the length they share."""
    out = []
    for f in fs:
        th, c, s0, s1, lado = f
        livre = [(s0, s1)]
        for g in fs:
            if g is f or g[4] != lado or abs(g[0] - th) > ANG_TOL:
                continue
            # g is further out when it lies on the side away from the wall (wall on +n: smaller c is further out)
            fora = (g[1] < c) if lado == 1 else (g[1] > c)
            if not fora or abs(g[1] - c) > junto:
                continue
            novos = []
            for a, b in livre:
                lo, hi = max(a, g[2]), min(b, g[3])
                if hi - lo <= 0:
                    novos.append((a, b))
                    continue
                if lo - a >= FACE_MIN:
                    novos.append((a, lo))
                if b - hi >= FACE_MIN:
                    novos.append((hi, b))
            livre = novos
        out += [(th, c, a, b, lado) for a, b in livre]
    return out


def paredes_de_faces(P, fs):
    """Pairs of facing faces with the mask between: wall pieces [(theta, c_mid, s0, s1, esp)]."""
    fs = faces_exteriores(fs)
    pecas = []
    por_ang = {}
    for f in fs:
        por_ang.setdefault(round(f[0] / ANG_TOL), []).append(f)

    def vizinhos(th):
        k = round(th / ANG_TOL)
        out = []
        for kk in (k - 1, k, k + 1):
            out += por_ang.get(kk, [])
        return out

    for th, c, s0, s1, lado in fs:
        if lado != 1:
            continue
        parceiros = sorted((g for g in vizinhos(th) if g[4] == -1 and abs(g[0] - th) <= ANG_TOL
                            and ESP[0] <= g[1] - c <= ESP[1] and min(s1, g[3]) - max(s0, g[2]) >= FACE_MIN),
                           key=lambda g: g[1] - c)
        livre = [(s0, s1)]
        for g in parceiros:
            t = g[1] - c
            novos = []
            for a, b in livre:
                lo, hi = max(a, g[2]), min(b, g[3])
                if hi - lo < FACE_MIN:
                    novos.append((a, b))
                    continue
                # the mask must fill the middle
                n_ok = n = 0
                s = lo
                while s <= hi:
                    x, y = P.ponto(th, c + t / 2, s)
                    n += 1
                    n_ok += P.em(x, y)
                    s += 2 * RES
                if n and n_ok / n >= 0.8:
                    pecas.append((th, c + t / 2, lo, hi, t))
                    if lo - a >= FACE_MIN:
                        novos.append((a, lo))
                    if b - hi >= FACE_MIN:
                        novos.append((hi, b))
                else:
                    novos.append((a, b))
            livre = novos
            if not livre:
                break
    return pecas


def juntar(P, pecas):
    """Collinear pieces of the same thickness joined (across junctions the mask fills); gaps kept for openings.
    Returns walls [{"th", "c", "esp", "trocos": [(s0, s1)]}] sorted by length."""
    pecas = sorted(pecas, key=lambda p: (round(p[0] / ANG_TOL), p[1]))
    grupos = []
    for p in pecas:
        for g in grupos:
            if abs(g["th"] - p[0]) <= ANG_TOL and abs(g["c"] - p[1]) <= 0.025 and abs(g["esp"] - p[4]) <= 0.03:
                g["pp"].append(p)
                break
        else:
            grupos.append({"th": p[0], "c": p[1], "esp": p[4], "pp": [p]})
    out = []
    for g in grupos:
        tot = sum(p[3] - p[2] for p in g["pp"])
        g["c"] = sum(p[1] * (p[3] - p[2]) for p in g["pp"]) / tot
        g["esp"] = sum(p[4] * (p[3] - p[2]) for p in g["pp"]) / tot
        iv = sorted((p[2], p[3]) for p in g["pp"])
        trocos = []
        for a, b in iv:
            if trocos and a <= trocos[-1][1] + 0.02:
                trocos[-1] = (trocos[-1][0], max(trocos[-1][1], b))
                continue
            if trocos and P.cheio(g["th"], g["c"], g["esp"], trocos[-1][1], a):
                # a gap the mask fills across the whole thickness: a junction where another wall crosses
                trocos[-1] = (trocos[-1][0], max(trocos[-1][1], b))
                continue
            trocos.append((a, b))
        out.append({"th": g["th"], "c": g["c"], "esp": g["esp"], "trocos": trocos})
    return _mesma_faixa(out)


def _mesma_faixa(ws):
    """Readings of one physical wall in the same band (a sill, a lining or a frame line moved a face) become one: the
    longest keeps its line and thickness and takes the others' length. A much thinner reading inside the band is
    glazing or a lining, not a wall of its own."""
    ws = sorted(ws, key=lambda w: -sum(b - a for a, b in w["trocos"]))
    aceites = []
    for w in ws:
        for A_ in aceites:
            if abs(w["th"] - A_["th"]) > ANG_TOL:
                continue
            sobre = (w["esp"] + A_["esp"]) / 2 - abs(w["c"] - A_["c"])
            if sobre < 0.02:
                continue
            ini, fim = A_["trocos"][0][0], A_["trocos"][-1][1]      # A's whole extent: a reading in its gap counts
            perto = any(min(b, fim) - max(a, ini) > -0.05 for a, b in w["trocos"])
            if not perto:
                continue
            if w["esp"] >= 0.6 * A_["esp"]:
                iv = sorted(A_["trocos"] + w["trocos"])
                novo = []
                for a, b in iv:
                    if novo and a <= novo[-1][1] + 0.02:
                        novo[-1] = (novo[-1][0], max(novo[-1][1], b))
                    else:
                        novo.append((a, b))
                A_["trocos"] = novo
            break
        else:
            aceites.append(w)
    return aceites


# ============================================================================ 4. openings
class Pontos:
    """Every stroke of the drawing as points (dashes included, long lines every 5 cm) in a 0,25 m grid."""

    def __init__(self, tracos, passo=0.05):
        self.g = {}
        for pts, _l, _c in tracos:
            for a, b in zip(pts, pts[1:]):
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                n = max(1, int(L / passo))
                for i in range(n + 1):
                    x, y = a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n
                    self.g.setdefault((int(x // 0.25), int(y // 0.25)), []).append((x, y))

    def perto(self, x, y, r):
        out = []
        for i in range(int((x - r) // 0.25), int((x + r) // 0.25) + 1):
            for j in range(int((y - r) // 0.25), int((y + r) // 0.25) + 1):
                out += self.g.get((i, j), [])
        return out


def _arco_em(pontos, jx, jy, r):
    """A swing of radius r drawn around (jx, jy): points on the circle (solid or dashed) spanning at least 40 degrees,
    clearly more than on the circles 12 cm inside and outside (floor stipple and hatching are everywhere)."""
    hw = max(0.025, 0.04 * r)
    anel, dentro, fora_, angs = 0, 0, 0, []
    for x, y in pontos.perto(jx, jy, r + 0.2):
        d = math.hypot(x - jx, y - jy)
        if abs(d - r) <= hw:
            anel += 1
            angs.append(math.atan2(y - jy, x - jx))
        elif abs(d - (r - 0.12)) <= hw:
            dentro += 1
        elif abs(d - (r + 0.12)) <= hw:
            fora_ += 1
    if anel < 6 or anel < 3 * (max(dentro, fora_) + 1):
        return False
    angs.sort()
    # the largest empty angular gap; the swing covers the rest
    vaz = max([b - a for a, b in zip(angs, angs[1:])] + [angs[0] + 2 * math.pi - angs[-1]])
    return 2 * math.pi - vaz >= math.radians(40)


def _e_porta(P, pontos, folhas, th, c, esp, a, b):
    """A swing beside the opening [a, b] of a wall: an arc (solid or dashed) centred on one of the four jamb corners
    with the opening's width as radius (or half of it: double doors), or a straight leaf of that length leaving a jamb."""
    larg = b - a
    jambas = [P.ponto(th, c + sg * esp / 2, s) for s in (a, b) for sg in (-1, 1)]
    raios = ([larg] if larg <= 1.30 else []) + ([larg / 2] if 1.0 <= larg <= 2.0 else [])   # one leaf, or two
    for jx, jy in jambas:
        for r in raios:
            if _arco_em(pontos, jx, jy, r):
                return True
    for x0, y0, x1, y1 in folhas:
        L = math.hypot(x1 - x0, y1 - y0)
        if larg > 1.30 or not (0.6 * larg <= L <= 1.25 * larg):
            continue
        for jx, jy in jambas:
            if min(math.hypot(x0 - jx, y0 - jy), math.hypot(x1 - jx, y1 - jy)) <= 0.08:
                ang = abs(math.atan2(y1 - y0, x1 - x0) % math.pi - th % math.pi)
                ang = min(ang, math.pi - ang)
                if ang >= math.radians(20):
                    return True
    return False


def _e_janela(P, linhas, pecas_finas, th, c, esp, a, b):
    """Glazing inside the opening: a thinner wall piece, or at least two lines parallel to the wall within its
    thickness covering most of the opening."""
    larg = b - a
    cob = 0.0
    for t2, c2, s0, s1, e2 in pecas_finas:
        if abs(t2 - th) <= ANG_TOL and abs(c2 - c) <= esp / 2 and e2 < 0.75 * esp:
            cob += max(0.0, min(b, s1) - max(a, s0))
    if cob >= 0.5 * larg:
        return True
    n = 0
    for t2, c2, ivs in linhas:
        if abs(t2 - th) > ANG_TOL or abs(c2 - c) > esp / 2 + 0.01:
            continue
        if sum(max(0.0, min(b, s1) - max(a, s0)) for s0, s1 in ivs) >= 0.7 * larg:
            n += 1
    return n >= 2


def _vaos_por_textura(P, w, segs, pontos, folhas):
    """Openings inside a wall the mask shows as solid: where a wall drawn WITH texture (hatching, insulation crosses,
    studs, poché triangles: lines across the wall) has 0,40–3,60 m with only lines along it (frames, glazing).
    Nothing is said for walls drawn without texture (two faces only)."""
    th, c, esp = w["th"], w["c"], w["esp"]
    u, n = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))
    lim = esp / 2 - 0.02
    if lim <= 0.01:
        return []
    marcas = []
    for x0, y0, x1, y1 in segs:
        a = (x0 - P.cx, y0 - P.cy)
        b = (x1 - P.cx, y1 - P.cy)
        sa, sb = a[0] * u[0] + a[1] * u[1], b[0] * u[0] + b[1] * u[1]
        ca, cb = a[0] * n[0] + a[1] * n[1] - c, b[0] * n[0] + b[1] * n[1] - c
        if max(sa, sb) < w["s0"] or min(sa, sb) > w["s1"] or max(ca, cb) < -lim or min(ca, cb) > lim:
            continue
        ds, dc = sb - sa, cb - ca
        ang = math.degrees(math.atan2(abs(dc), abs(ds)))
        if not (20 <= ang <= 70):      # hatching, insulation crosses, poché triangles are diagonal; frames are square
            continue
        # the part inside the band
        t0, t1 = 0.0, 1.0
        if abs(dc) > 1e-12:
            ta, tb = (-lim - ca) / dc, (lim - ca) / dc
            t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
        if t1 <= t0:
            continue
        marcas.append((min(sa + ds * t0, sa + ds * t1), max(sa + ds * t0, sa + ds * t1)))
    if not marcas:
        return []
    # 5 cm bins crossed by at least two diagonal marks: texture (a lone diagonal of a frame detail is not)
    b0 = w["s0"]
    nb = int((w["s1"] - b0) / 0.05) + 1
    conta = [0] * nb
    for a, b in marcas:
        for i in range(max(0, int((a - b0) / 0.05)), min(nb, int((b - b0) / 0.05) + 1)):
            conta[i] += 1
    cobertas = []
    for i, n_ in enumerate(conta):
        if n_ < 2:
            continue
        a, b = b0 + i * 0.05, b0 + (i + 1) * 0.05
        if cobertas and a <= cobertas[-1][1] + 0.08:     # hatching lines are a few cm apart
            cobertas[-1][1] = b
        else:
            cobertas.append([a, b])
    tot = sum(min(b, w["s1"]) - max(a, w["s0"]) for a, b in cobertas)
    if tot < 0.5 * (w["s1"] - w["s0"]):
        return []
    out = []
    for (a0, a1), (b0, b1) in zip(cobertas, cobertas[1:]):
        if VAO[0] <= b0 - a1 <= VAO[1] and a1 >= w["s0"] and b0 <= w["s1"]:
            out.append({"s0": a1, "s1": b0, "tipo": "janela"})   # solid in the mask: frames and glazing
    return out


def vaos(P, paredes, linhas, tracos, pecas, cheios=()):
    """Openings between the pieces of each wall, and inside walls drawn with texture (see _vaos_por_textura)."""
    arcos = Pontos(tracos)
    folhas = [s for s in _segmentos(tracos, []) if math.hypot(s[2] - s[0], s[3] - s[1]) >= VAO[0] * 0.6]
    for w in paredes:
        tr = []
        for a, b in sorted(w["trocos"]):
            if tr and a <= tr[-1][1] + 0.02:
                tr[-1] = (tr[-1][0], max(tr[-1][1], b))
            else:
                tr.append((a, b))
        w["aberturas"] = []
        juntos = [list(tr[0])]
        for (a0, a1), (b0, b1) in zip(tr, tr[1:]):
            g = b0 - a1
            # the same wall measured with another thickness there (an extra lining line on one side): not an opening
            mesma = sum(max(0.0, min(b0, p[3]) - max(a1, p[2])) for p in pecas
                        if abs(p[0] - w["th"]) <= ANG_TOL and abs(p[1] - w["c"]) <= w["esp"] / 2 and p[4] >= 0.6 * w["esp"])
            if g < VAO[0] or mesma >= 0.7 * g:      # a short break, or the same wall read with another thickness
                juntos[-1][1] = max(juntos[-1][1], b1)
            elif VAO[0] <= g <= VAO[1]:
                jan = _e_janela(P, linhas, pecas, w["th"], w["c"], w["esp"], a1, b0)
                porta = not jan and _e_porta(P, arcos, folhas, w["th"], w["c"], w["esp"], a1, b0)
                w["aberturas"].append({"s0": a1, "s1": b0, "tipo": "janela" if jan else "porta" if porta else "vao"})
                juntos[-1][1] = b1
            else:
                juntos.append([b0, b1])
        # a wall cut in separate parts (gaps too big): each part a wall of its own
        w["trocos"] = [tuple(j) for j in juntos]
    segs = _segmentos(tracos, cheios)
    out = []
    for w in paredes:
        for a, b in w["trocos"]:
            ab = [o for o in w["aberturas"] if a - 1e-6 <= o["s0"] and o["s1"] <= b + 1e-6]
            nw = {"th": w["th"], "c": w["c"], "esp": w["esp"], "s0": a, "s1": b, "aberturas": ab}
            for o in _vaos_por_textura(P, nw, segs, arcos, folhas):
                if not any(min(o["s1"], x["s1"]) - max(o["s0"], x["s0"]) > 0 for x in ab):
                    ab.append(o)
            ab.sort(key=lambda o: o["s0"])
            out.append(nw)
    return out


# ============================================================================ 5. outside, exterior walls, rooms
def _poligono_parede(P, w, s0, s1, mais=0.0):
    u, n = (math.cos(w["th"]), math.sin(w["th"])), (-math.sin(w["th"]), math.cos(w["th"]))
    e = w["esp"] / 2 + mais
    pts = []
    for s, sg in ((s0, -1), (s1, -1), (s1, 1), (s0, 1)):
        x, y = P.ponto(w["th"], w["c"] + sg * e, s)
        pts.append((x / RES, y / RES))
    return pts


def fora_e_divisoes(P, paredes):
    """Bridge the openings, flood the outside from the border; exterior side of each wall; rooms >= 1 m²."""
    C = P.S.copia()
    for w in paredes:
        C.poligono(_poligono_parede(P, w, w["s0"], w["s1"], 0.5 * RES))
    livre = C.inverso()
    # the outside is flooded on the walls CLOSED by 1 m: an opening not recognised (an entrance, a glazed wall) does not
    # let it run into the house; the rooms are then taken on the walls as drawn
    R = int(1.0 / RES)
    m = R + 2                    # an empty margin, or the closing's erosion would eat the walls near the border
    largo = Mascara(C.w + 2 * m, C.h + 2 * m, [0] * m + [b << m for b in C.r] + [0] * m)
    fechado = largo.fechar(R).inverso()
    fora_l = fechado.preencher({0: fechado.r[0]})
    fora = Mascara(C.w, C.h, [(fora_l.get(y + m, 0) >> m) & C.cheia for y in range(C.h)])
    for w in paredes:
        votos = {1: 0, -1: 0}
        n = 0
        s = w["s0"] + 0.1
        while s <= w["s1"] - 0.1:
            if not any(o["s0"] - 0.05 <= s <= o["s1"] + 0.05 for o in w["aberturas"]):
                n += 1
                for sg in (1, -1):
                    x, y = P.ponto(w["th"], w["c"] + sg * (w["esp"] / 2 + 4 * RES), s)
                    votos[sg] += P.em(x, y, fora)
            s += 0.1
        lado = 0
        if n:
            for sg in (1, -1):
                if votos[sg] >= 0.5 * n and votos[-sg] < 0.5 * n:
                    lado = sg
        w["lado_exterior"] = lado
        w["exterior"] = bool(lado)
    dentro = livre.menos(fora)
    divisoes = []
    salas = Mascara(C.w, C.h)
    for c in dentro.componentes(area_min=int(1.0 / RES / RES)):
        # a room has a wall between it and the outside; a small pocket the 1 m closing cut off touches the outside
        # directly (a big room behind an opening not recognised does too, and stays)
        if c["area"] * RES * RES < 3.0 and any(_dilatar_esparso({y: b}, 1, C.w).get(yy, 0) & fora.r[yy]
               for y, b in c["linhas"].items() for yy in (y - 1, y, y + 1) if 0 <= yy < C.h):
            continue
        if c["area"] * RES * RES <= 150:
            for y, b in c["linhas"].items():
                salas.r[y] |= b
        sx = sy = 0
        for y, b in c["linhas"].items():
            n = b.bit_count()
            sy += y * n
            bb, x = b, 0
            while bb:
                low = bb & -bb
                sx += low.bit_length() - 1
                bb ^= low
        divisoes.append({"area": round(c["area"] * RES * RES, 2),
                         "centro": [round(sx / c["area"] * RES, 3), round(sy / c["area"] * RES, 3)]})
    P.salas = salas
    return fora, sorted(divisoes, key=lambda d: -d["area"])


def junto_a_divisoes(P, paredes):
    """The walls with a room (<= 150 m²) on at least one side: the house, without the site's walls and fences."""
    out = []
    for w in paredes:
        n = n_ok = 0
        s = w["s0"] + 0.05
        while s <= w["s1"] - 0.05:
            n += 1
            for sg in (1, -1):
                x, y = P.ponto(w["th"], w["c"] + sg * (w["esp"] / 2 + 4 * RES), s)
                if P.em(x, y, P.salas):
                    n_ok += 1
                    break
            s += 0.1
        if n and n_ok / n >= 0.3:
            out.append(w)
    return out


# ============================================================================ 6. one region at one scale
def analisar(paths, regiao, escala):
    """The plan of one sheet region at one scale (1:escala), or None. See the module docstring for the output."""
    tracos, cheios = primitivas(paths, regiao, escala)
    if not tracos and not cheios:
        return None
    k = escala / 1000.0
    L, H = (regiao[2] - regiao[0]) * k, (regiao[3] - regiao[1]) * k
    if max(L, H) / RES > 4000:
        return None
    tinta = imagem(tracos, cheios, L, H)
    S = mascara_paredes(tinta)
    cx, cy = L / 2, H / 2
    P = Plano(S, cx, cy)
    linhas = linhas_retas(_segmentos(tracos, cheios), cx, cy)
    fs = faces(P, linhas)
    pecas = paredes_de_faces(P, fs)
    if not pecas:
        return None
    ps = vaos(P, juntar(P, pecas), linhas, tracos, pecas, cheios)
    ps = _rede_principal(P, estender(P, ps))
    if len(ps) < 3:
        return None
    fora, divisoes = fora_e_divisoes(P, ps)
    casa = junto_a_divisoes(P, ps)
    if 3 <= len(casa) < len(ps):          # walls of the site (fences, retaining walls, decking) left out
        ps = casa
        fora, divisoes = fora_e_divisoes(P, ps)
    return _documento(P, ps, divisoes, regiao, escala, L, H)


def estender(P, ps):
    """Each wall's ends carried on along its centre line while the wall mask goes on (up to 0,6 m): the faces stop
    short of corners and junctions, where the mask is wider; this makes the walls meet."""
    for w in ps:
        for fim, sg in (("s0", -1), ("s1", 1)):
            s = w[fim]
            andou = 0.0
            while andou < 0.6:
                if not P.cheio(w["th"], w["c"], w["esp"], s + sg * RES, s + sg * RES, 1.0):
                    break
                s += sg * RES
                andou += RES
            w[fim] = s
    return ps


def _rede_principal(P, ps):
    """Keep the walls that belong to the house: those on the wall-mask region(s) carrying most wall length, plus the
    walls joined to them by an opening (a wall between two doors). Furniture, text and symbols on their own go."""
    if not ps:
        return ps
    comp = P.S.componentes(area_min=4)
    rotulo = {}
    for i, c in enumerate(comp):
        for y, b in c["linhas"].items():
            rotulo.setdefault(y, []).append((b, i))

    def onde(x, y):
        px, py = int(x / RES), int(y / RES)
        for b, i in rotulo.get(py, []):
            if (b >> px) & 1:
                return i
        return None
    soma, de = {}, []
    for w in ps:
        ids = set()
        s = w["s0"]
        while s <= w["s1"]:
            i = onde(*P.ponto(w["th"], w["c"], s))
            if i is not None:
                ids.add(i)
            s += 0.1
        de.append(ids)
        for i in ids:
            soma[i] = soma.get(i, 0.0) + (w["s1"] - w["s0"])
    if not soma:
        return []
    top = max(soma.values())
    bons = {i for i, v in soma.items() if v >= 0.25 * top}
    out = [w for w, ids in zip(ps, de) if ids & bons]
    return [w for w in out if w["s1"] - w["s0"] >= 0.3 or w["aberturas"]]


def _documento(P, ps, divisoes, regiao, escala, L, H):
    """Walls in metres, y UP, origin at the bottom-left corner of the walls' box."""
    pts = []
    for w in ps:
        for s in (w["s0"], w["s1"]):
            for sg in (-1, 1):
                pts.append(P.ponto(w["th"], w["c"] + sg * w["esp"] / 2, s))
    ox, oy_baixo = min(p[0] for p in pts), max(p[1] for p in pts)   # image y down: the bottom is the max y

    def m(p):
        return [round(p[0] - ox, 3), round(oy_baixo - p[1], 3)]
    paredes = []
    for i, w in enumerate(sorted(ps, key=lambda w: -(w["s1"] - w["s0"])), 1):
        p0, p1 = P.ponto(w["th"], w["c"], w["s0"]), P.ponto(w["th"], w["c"], w["s1"])
        # image y down -> y up flips the sides: +normal (image) is -normal (y up) for the same p0 -> p1
        paredes.append({"id": f"P{i:02d}", "p0": m(p0), "p1": m(p1), "espessura": round(w["esp"], 3),
                        "exterior": w["exterior"], "lado_exterior": -w["lado_exterior"],
                        "aberturas": [{"t0": round(o["s0"] - w["s0"], 3), "t1": round(o["s1"] - w["s0"], 3), "tipo": o["tipo"]}
                                      for o in w["aberturas"]]})
    for d in divisoes:
        d["centro"] = m(d["centro"])
    Lw = max(p[0] for p in pts) - ox
    Dw = oy_baixo - min(p[1] for p in pts)
    doc = {"escala": escala, "regiao": [round(v, 1) for v in regiao], "paredes": paredes, "divisoes": divisoes,
           "contorno": [0.0, round(Lw, 3), 0.0, round(Dw, 3)]}
    doc["nota"] = round(nota(doc), 1)
    eix = em_eixos(doc)
    if eix:
        doc["eixos"] = eix
    return doc


# ============================================================================ 7. how plausible, and the axis format
def nota(doc):
    """How plausible as a house plan (0 = not a house)."""
    ps, dv = doc["paredes"], doc["divisoes"]
    ext = [p for p in ps if p["exterior"]]
    L, D = doc["contorno"][1], doc["contorno"][3]
    area = sum(d["area"] for d in dv)
    if len(ext) < 3 or not dv or not (3.0 <= max(L, D) <= 60.0) or min(L, D) < 2.0 or area < 8.0:
        return 0.0
    if area > 1.05 * L * D:
        return 0.0
    esp_ext = sum(0.12 <= p["espessura"] <= 0.50 for p in ext) / len(ext)
    larguras = [o["t1"] - o["t0"] for p in ps for o in p["aberturas"]]
    portas = [l_ for p in ps for o in p["aberturas"] if o["tipo"] == "porta" for l_ in [o["t1"] - o["t0"]]]
    preench = area / (L * D)      # rooms fill the box (not a frame or a title block)
    base = len(ps) * 0.5 + 2 * len(dv) + 3 * len(portas) + len(larguras) + 10 * preench
    # plausibility of the scale: outside walls 12–50 cm, doors 0,6–1,3 m, openings 0,4–3,6 m, rooms 1,5–80 m², a house
    # 6–35 m long
    f = 0.2 + 0.8 * esp_ext
    if portas:
        f *= 0.5 + 0.5 * sum(0.6 <= l_ <= 1.3 for l_ in portas) / len(portas)
    if larguras:
        f *= 0.6 + 0.4 * sum(0.5 <= l_ <= 3.0 for l_ in larguras) / len(larguras)
    f *= 0.4 + 0.6 * sum(1.5 <= d["area"] <= 80 for d in dv) / len(dv)
    if not (6.0 <= max(L, D) <= 35.0):
        f *= 0.4
    if not (40.0 <= L * D <= 500.0):      # a house's footprint box
        f *= 0.5
    return base * f


def em_eixos(doc, tol=math.radians(1.5)):
    """The plan turned to its two perpendicular wall directions, in planta_arquitetura.py's format, or None when a
    wall follows another direction (oblique walls: the configurator chain does not build them yet)."""
    ps = doc["paredes"]
    angs = []
    for p in ps:
        (x0, y0), (x1, y1) = p["p0"], p["p1"]
        angs.append((math.atan2(y1 - y0, x1 - x0) % (math.pi / 2), math.hypot(x1 - x0, y1 - y0)))
    # dominant direction (mod 90): length-weighted circular mean on 4*angle
    sx = sum(L * math.cos(4 * a) for a, L in angs)
    sy = sum(L * math.sin(4 * a) for a, L in angs)
    a0 = (math.atan2(sy, sx) / 4) % (math.pi / 2)
    if a0 > math.pi / 4:          # turn by the smaller angle (89,9° is -0,1°: the plan keeps its orientation)
        a0 -= math.pi / 2
    for a, L in angs:
        d = abs(a - a0) % (math.pi / 2)
        if min(d, math.pi / 2 - d) > tol:
            return None
    ca, sa = math.cos(-a0), math.sin(-a0)

    def rod(p):
        return (p[0] * ca - p[1] * sa, p[0] * sa + p[1] * ca)
    paredes = []
    for p in ps:
        a, b = rod(p["p0"]), rod(p["p1"])
        horiz = abs(b[1] - a[1]) < abs(b[0] - a[0])
        ax = 0 if horiz else 1
        s0, s1 = a[ax], b[ax]
        c = (a[1 - ax] + b[1 - ax]) / 2
        sentido = 1 if s1 >= s0 else -1
        # lado_exterior is relative to p0->p1's left normal (y up); in the axis format it is +1 when outside is at +c
        if horiz:
            lado = p["lado_exterior"] * sentido
        else:
            lado = -p["lado_exterior"] * sentido
        ab = []
        for o in p["aberturas"]:
            t0, t1 = (s0 + o["t0"] * sentido, s0 + o["t1"] * sentido)
            ab.append({"s0": min(t0, t1), "s1": max(t0, t1), "tipo": "janela" if o["tipo"] == "janela" else "porta"})
        paredes.append({"eixo": "x" if horiz else "y", "s0": min(s0, s1), "s1": max(s0, s1), "c": c,
                        "espessura": p["espessura"], "exterior": p["exterior"], "lado_exterior": lado,
                        "aberturas": sorted(ab, key=lambda o: o["s0"])})
    xs, ys = [], []
    for w in paredes:
        lo, hi = (w["c"] - w["espessura"] / 2, w["c"] + w["espessura"] / 2)
        if w["eixo"] == "x":
            xs += [w["s0"], w["s1"]]
            ys += [lo, hi]
        else:
            ys += [w["s0"], w["s1"]]
            xs += [lo, hi]
    ox, oy = min(xs), min(ys)
    for w in paredes:   # interior walls stop at the inner face of the exterior wall they run into
        if w["exterior"]:
            continue
        for e in paredes:
            if not e["exterior"] or e["eixo"] == w["eixo"]:
                continue
            e0, e1 = e["c"] - e["espessura"] / 2, e["c"] + e["espessura"] / 2
            if not (e["s0"] - 0.01 <= w["c"] <= e["s1"] + 0.01):
                continue
            if e0 - 0.01 < w["s1"] < e1 + 0.05 and w["s0"] < e0:
                w["s1"] = e0
            if e0 - 0.05 < w["s0"] < e1 + 0.01 and w["s1"] > e1:
                w["s0"] = e1
    out = []
    for i, w in enumerate(sorted(paredes, key=lambda w: (w["eixo"], round(w["c"], 2), w["s0"])), 1):
        dc, ds = (oy, ox) if w["eixo"] == "x" else (ox, oy)
        out.append({"id": f"P{i:02d}", "eixo": w["eixo"], "s0": round(w["s0"] - ds, 3), "s1": round(w["s1"] - ds, 3),
                    "c": round(w["c"] - dc, 3), "espessura": round(w["espessura"], 3), "exterior": w["exterior"],
                    "lado_exterior": w["lado_exterior"],
                    "aberturas": [{"s0": round(o["s0"] - ds, 3), "s1": round(o["s1"] - ds, 3), "tipo": o["tipo"]}
                                  for o in w["aberturas"]]})
    return {"rotacao_graus": round(math.degrees(a0), 2), "contorno": [0.0, round(max(xs) - ox, 3), 0.0, round(max(ys) - oy, 3)],
            "paredes": out}


# ============================================================================ 8. where the plans are, and their scale
def regioes(paths, passo_mm=0.25):
    """Where the drawings with walls are on a sheet: [(x0, y0, x1, y1)] in sheet mm, the biggest first. The whole sheet
    is drawn at 0,25 mm per pixel; what stays solid after closing and opening by one pixel (poché, hatched or heavy
    walls; thin lines, dimensions and text go) is grouped when less than 5 mm apart, and each group with enough solid
    is a view to analyse. Frames and title blocks give little solid; the scoring rejects what is not a house."""
    xs = [x for p in paths for sp, _ in p["subs"] for x, _y in sp]
    ys = [y for p in paths for sp, _ in p["subs"] for _x, y in sp]
    if not xs:
        return []
    X0, Y0, X1, Y1 = min(xs), min(ys), max(xs), max(ys)
    W, H = X1 - X0, Y1 - Y0
    w, h = int(W / passo_mm) + 2, int(H / passo_mm) + 2
    if w * h > 16_000_000:
        passo_mm = math.sqrt(W * H / 16_000_000)
        w, h = int(W / passo_mm) + 2, int(H / passo_mm) + 2
    m = Mascara(w, h)
    for p in paths:
        for sp, _cl in p["subs"]:
            pts = [((x - X0) / passo_mm, (y - Y0) / passo_mm) for x, y in sp]
            if p.get("fill") and len(pts) >= 3 and _area(sp) <= 400:
                m.poligono(pts)
            if p.get("stroke"):
                for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                    if abs(bx - ax) * passo_mm > 0.4 * W or abs(by - ay) * passo_mm > 0.4 * H:
                        continue
                    m.segmento(ax, ay, bx, by)
    solido = m.fechar(1).abrir(1)
    grupos = solido.dilatar(int(2.5 / passo_mm))
    out = []
    for c in grupos.componentes(area_min=int((10 / passo_mm) ** 2)):
        x0, y0, x1, y1 = c["caixa"]
        bw, bh = (x1 - x0) * passo_mm, (y1 - y0) * passo_mm
        if bw < 15 or bh < 15 or (bw > 0.9 * W and bh > 0.9 * H):
            continue
        so = {y: solido.r[y] & b for y, b in c["linhas"].items() if solido.r[y] & b}
        n_sol = sum(b.bit_count() for b in so.values())
        if n_sol * passo_mm * passo_mm < 30:          # less than 30 mm² of solid: not a drawing with walls
            continue
        # typical thickness of its solid bands (sheet mm), weighted by their area: the scale follows from it
        partes = sorted(Mascara(w, h, [so.get(y, 0) for y in range(h)]).componentes(area_min=8), key=lambda k: -k["area"])[:25]
        esp = []
        for k in partes:
            e_px = 2 * profundidade(k["linhas"]) + 1
            if k["area"] < 6 * e_px * e_px:            # not band-like: a merged hatching or a blob, not a wall
                continue
            esp += [e_px * passo_mm] * max(1, k["area"] // 50)
        esp.sort()
        out.append((X0 + x0 * passo_mm - 3, Y0 + y0 * passo_mm - 3, X0 + x1 * passo_mm + 3, Y0 + y1 * passo_mm + 3, n_sol,
                    esp[len(esp) // 2] if esp else None))
    out.sort(key=lambda r: -r[4])
    return [(r[0], r[1], r[2], r[3], r[5]) for r in out]


def raio_portas_mm(paths, regiao):
    """Median radius (sheet mm) of the quarter-circle arcs of a region: door swings (a leaf ≈ 0,85 m), or None."""
    x0, y0, x1, y1 = regiao
    rs = []
    for p in paths:
        if not p.get("stroke"):
            continue
        for sp, _cl in p["subs"]:
            if len(sp) < 5 or not all(x0 <= x <= x1 and y0 <= y <= y1 for x, y in (sp[0], sp[-1])):
                continue
            (ax, ay), (bx, by), (cx_, cy_) = sp[0], sp[len(sp) // 2], sp[-1]
            d = 2 * (ax * (by - cy_) + bx * (cy_ - ay) + cx_ * (ay - by))
            if abs(d) < 1e-9:
                continue
            ux = ((ax * ax + ay * ay) * (by - cy_) + (bx * bx + by * by) * (cy_ - ay) + (cx_ * cx_ + cy_ * cy_) * (ay - by)) / d
            uy = ((ax * ax + ay * ay) * (cx_ - bx) + (bx * bx + by * by) * (ax - cx_) + (cx_ * cx_ + cy_ * cy_) * (bx - ax)) / d
            r = math.hypot(ax - ux, ay - uy)
            if r < 0.5 or any(abs(math.hypot(x - ux, y - uy) - r) > 0.03 * r for x, y in sp):
                continue
            varre = abs(math.atan2((ax - ux) * (cy_ - uy) - (ay - uy) * (cx_ - ux), (ax - ux) * (cx_ - ux) + (ay - uy) * (cy_ - uy)))
            if math.radians(70) <= varre <= math.radians(100):
                rs.append(r)
    if len(rs) < 2:
        return None
    rs.sort()
    return rs[len(rs) // 2]


def escala_alvo(paths, regiao, esp_mm=None):
    """The scale the region suggests: door leaves ≈ 0,85 m, else walls ≈ 0,25 m thick."""
    pelas_paredes = 250.0 / esp_mm if esp_mm else None
    r = raio_portas_mm(paths, regiao)
    pelas_portas = 850.0 / r if r else None
    # door leaves vary far less than walls (0,7–0,9 m against 0,10–0,45 m): they decide when they agree with the walls
    # (arcs are also drawn by fixtures — a toilet seat, a shower — hence the check)
    if pelas_portas and (not pelas_paredes or 0.4 <= pelas_portas / pelas_paredes <= 2.5):
        return pelas_portas
    return pelas_paredes


def escalas_plausiveis(regiao, esp_mm=None, alvo=None):
    """Scales that make the region 4–45 m long on its longer side; when the typical thickness of its solid bands is
    known, only the three standard scales nearest to the one that makes them ≈ 0,25 m thick (a usual wall)."""
    lado = max(regiao[2] - regiao[0], regiao[3] - regiao[1])
    ok = [e for e in ESCALAS if 4.0 <= lado * e / 1000 <= 45.0]
    alvo = alvo or (250.0 / esp_mm if esp_mm else None)
    if alvo:
        ok = sorted(ok, key=lambda e: abs(math.log(e / alvo)))[:3]
    return ok


def melhor(paths, regiao, escalas=None, esp_mm=None):
    """The best reading of a region over the plausible scales (or the given ones), or None. Each scale's score is
    weighed by how close it is to the scale the walls and the door swings suggest."""
    alvo = escala_alvo(paths, regiao, esp_mm)
    top, top_v = None, 0.0
    for e in escalas or escalas_plausiveis(regiao, esp_mm, alvo):
        try:
            d = analisar(paths, regiao, e)
        except (ValueError, ZeroDivisionError, IndexError):
            continue
        if not d or d["nota"] <= 0:
            continue
        v = d["nota"] * (math.exp(-2 * abs(math.log(e / alvo))) if alvo else 1.0)
        d["escala_sugerida"] = round(alvo) if alvo else None
        if v > top_v:
            top, top_v = d, v
    return top


def plantas(paths):
    """Every floor plan found on a sheet, best first."""
    out = []
    for r in regioes(paths)[:10]:
        d = melhor(paths, r[:4], esp_mm=r[4])
        if d:
            out.append(d)
    return sorted(out, key=lambda d: -d["nota"])


def main():
    import argparse
    import json
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from ferramentas.dwfx.leitor import Dwfx
    from ferramentas.dwfx.leitor_pdf import Pdf
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("desenho")
    ap.add_argument("--folha", type=int)
    ap.add_argument("--regiao", type=float, nargs=4)
    ap.add_argument("--escala", type=float)
    ap.add_argument("--saida")
    a = ap.parse_args()
    d = Pdf(a.desenho) if a.desenho.lower().endswith(".pdf") else Dwfx(a.desenho)
    folhas = [a.folha] if a.folha else range(1, len(d.pages) + 1)
    res = []
    for f in folhas:
        paths = d.paths(f, curvas=True)
        if a.regiao:
            doc = analisar(paths, a.regiao, a.escala) if a.escala else melhor(paths, a.regiao)
            docs = [doc] if doc else []
        else:
            docs = plantas(paths)
        for doc in docs:
            doc["folha"] = f
            res.append(doc)
            ab = sum(len(p["aberturas"]) for p in doc["paredes"])
            print(f"folha {f}  regiao {doc['regiao']}  1:{doc['escala']}  {doc['contorno'][1]:.2f} x {doc['contorno'][3]:.2f} m  "
                  f"{len(doc['paredes'])} paredes ({sum(p['exterior'] for p in doc['paredes'])} ext)  {ab} vãos  "
                  f"{len(doc['divisoes'])} divisões  nota {doc['nota']}{'  eixos' if doc.get('eixos') else ''}")
    if a.saida:
        Path(a.saida).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
