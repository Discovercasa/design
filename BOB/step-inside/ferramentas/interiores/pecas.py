"""Parametric interior pieces (runs inside Blender): simple boxes with the catalogue's sizes and colours.

Each generator builds one mesh in the object's own frame: origin at the centre of the footprint on the floor, width
along x, depth along y with the FRONT towards -y, height up z (interiores/catalogo.json). `mat(hex, rugosidade,
alfa, metal)` returns the material index to use. Few faces on purpose: these pieces also go to the phone (AR budget).
"""
import math

import bmesh


def _caixa(bm, x0, y0, z0, x1, y1, z1, mi):
    vs = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                    (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f]).material_index = mi


def _elipse(bm, cx, cy, rx, ry, z0, z1, mi, n=20):
    em = bmesh.ops.create_circle(bm, cap_ends=True, segments=n, radius=1.0)["verts"]
    for v in em:
        v.co.x, v.co.y, v.co.z = cx + v.co.x * rx, cy + v.co.y * ry, z0
    faces = list({f for v in em for f in v.link_faces})
    for f in faces:
        f.material_index = mi
    ext = bmesh.ops.extrude_face_region(bm, geom=faces)
    novos = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    for v in novos:
        v.co.z = z1
    for f in {f for v in novos for f in v.link_faces}:
        f.material_index = mi


def _frentes(bm, x0, x1, y, z0, z1, mi, mp, n=None, puxador="h", folga=0.003):
    """Doors / drawer fronts across x0..x1 on the plane y (the front), each with its handle."""
    n = n or max(1, round((x1 - x0) / 0.6))
    w = (x1 - x0) / n
    for i in range(n):
        a, b = x0 + i * w + folga, x0 + (i + 1) * w - folga
        _caixa(bm, a, y - 0.02, z0 + folga, b, y, z1 - folga, mi)
        if mp is None:
            continue
        if puxador == "h":
            _caixa(bm, a + 0.06, y - 0.035, z1 - 0.07, b - 0.06, y - 0.02, z1 - 0.055, mp)
        else:  # vertical, on the side away from the next door
            xh = b - 0.05 if i % 2 == 0 else a + 0.04
            _caixa(bm, xh, y - 0.035, z0 + (z1 - z0) * 0.42, xh + 0.012, y - 0.02, z0 + (z1 - z0) * 0.62, mp)


def cozinha(bm, W, D, H, c, mat, p):
    fr, bc, px, el = mat(c["frentes"], 0.5), mat(c["bancada"], 0.35), mat(c["puxador"], 0.4, metal=0.6), mat(c["eletro"], 0.25, metal=0.8)
    x0, x1, yf, yb = -W / 2, W / 2, -D / 2, D / 2
    _caixa(bm, x0, yf + 0.06, 0, x1, yb, 0.1, mat("#2B2B2B", 0.6))                 # plinth
    _caixa(bm, x0, yf + 0.02, 0.1, x1, yb, 0.86, fr)                              # base units
    _frentes(bm, x0, x1, yf + 0.02, 0.1, 0.86, fr, px)
    _caixa(bm, x0, yf, 0.86, x1, yb, 0.9, bc)                                     # worktop
    if p.get("pia") is not None:                                                  # sink + tap
        a = x0 + p["pia"]
        _caixa(bm, a + 0.08, yf + 0.08, 0.9, a + 0.52, yb - 0.12, 0.903, el)
        _caixa(bm, a + 0.28, yb - 0.1, 0.9, a + 0.32, yb - 0.06, 1.15, el)
        _caixa(bm, a + 0.28, yb - 0.3, 1.11, a + 0.32, yb - 0.06, 1.15, el)
    if p.get("placa") is not None:                                                # hob
        a = x0 + p["placa"]
        _caixa(bm, a + 0.03, yf + 0.06, 0.9, a + 0.57, yb - 0.06, 0.905, mat("#111214", 0.15))
    for a, b in p.get("altos", [[0.0, W]]):                                       # wall units
        _caixa(bm, x0 + a, yb - 0.35, 1.45, x0 + b, yb, H, fr)
        _frentes(bm, x0 + a, x0 + b, yb - 0.35, 1.45, H, fr, px, puxador="v")
        if p.get("placa") is not None and a <= p["placa"] and p["placa"] + 0.6 <= b:   # hood in the unit above the hob
            _caixa(bm, x0 + p["placa"] + 0.03, yb - 0.38, 1.43, x0 + p["placa"] + 0.57, yb - 0.05, 1.45, el)


def ilha(bm, W, D, H, c, mat, p):
    fr, bc = mat(c["frentes"], 0.5), mat(c["bancada"], 0.35)
    px = mat(c.get("puxador", "#2B2B2B"), 0.4, metal=0.6)
    sobra = p.get("balanco", 0.25)                                                # overhang for stools at the back
    _caixa(bm, -W / 2 + 0.05, -D / 2 + 0.06, 0, W / 2 - 0.05, D / 2 - sobra, 0.1, mat("#2B2B2B", 0.6))
    _caixa(bm, -W / 2, -D / 2 + 0.02, 0.1, W / 2, D / 2 - sobra, H - 0.04, fr)
    _frentes(bm, -W / 2, W / 2, -D / 2 + 0.02, 0.1, H - 0.04, fr, px)
    _caixa(bm, -W / 2, -D / 2, H - 0.04, W / 2, D / 2, H, bc)


def coluna(bm, W, D, H, c, mat, p):
    fr, px = mat(c["frentes"], 0.5), mat(c["puxador"], 0.4, metal=0.6)
    _caixa(bm, -W / 2, -D / 2 + 0.02, 0, W / 2, D / 2, H, fr)
    _frentes(bm, -W / 2, W / 2, -D / 2 + 0.02, 0.1, 1.4, fr, px, n=1, puxador="v")
    _frentes(bm, -W / 2, W / 2, -D / 2 + 0.02, 1.4, H, fr, px, n=1, puxador="v")


def mesa(bm, W, D, H, c, mat, p):
    t, ps = mat(c["tampo"], 0.45), mat(c["pes"], 0.4, metal=0.5)
    _caixa(bm, -W / 2, -D / 2, H - 0.03, W / 2, D / 2, H, t)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (W / 2 - 0.08), sy * (D / 2 - 0.08)
            _caixa(bm, x - 0.025, y - 0.025, 0, x + 0.025, y + 0.025, H - 0.03, ps)


def cama(bm, W, D, H, c, mat, p):
    e, co, ed, al = mat(c["estrutura"], 0.5), mat(c["colchao"], 0.8), mat(c["edredao"], 0.85), mat(c["almofada"], 0.8)
    yb = D / 2
    _caixa(bm, -W / 2, -D / 2, 0, W / 2, yb - 0.06, 0.3, e)                       # base
    _caixa(bm, -W / 2, yb - 0.06, 0, W / 2, yb, H, e)                             # headboard
    _caixa(bm, -W / 2 + 0.05, -D / 2 + 0.04, 0.3, W / 2 - 0.05, yb - 0.08, 0.52, co)   # mattress
    _caixa(bm, -W / 2 + 0.02, -D / 2 + 0.02, 0.3, W / 2 - 0.02, yb - 0.62, 0.56, ed)   # duvet over the lower part
    n = 2 if W > 1.3 else 1
    w = (W - 0.16) / n
    for i in range(n):
        a = -W / 2 + 0.08 + i * w
        _caixa(bm, a + 0.02, yb - 0.55, 0.52, a + w - 0.02, yb - 0.12, 0.66, al)


def roupeiro(bm, W, D, H, c, mat, p):
    fr, px = mat(c["frentes"], 0.5), mat(c["puxador"], 0.4, metal=0.6)
    _caixa(bm, -W / 2, -D / 2 + 0.02, 0, W / 2, D / 2, H, fr)
    _frentes(bm, -W / 2, W / 2, -D / 2 + 0.02, 0.06, H, fr, px, n=max(2, round(W / 0.6)), puxador="v")


def sanita(bm, W, D, H, c, mat, p):
    lo = mat(c["loica"], 0.15)
    _caixa(bm, -W / 2 + 0.02, D / 2 - 0.2, H - 0.2, W / 2 - 0.02, D / 2, H, lo)    # against the wall
    _elipse(bm, 0, -0.04, W / 2, D / 2 - 0.04, H - 0.17, H, lo)                     # bowl
    _elipse(bm, 0, -0.04, W / 2 - 0.01, D / 2 - 0.05, H, H + 0.02, mat("#FFFFFF", 0.3))   # seat
    _caixa(bm, -0.11, D / 2 - 0.005, 0.95, 0.11, D / 2, 1.1, mat("#DADCDD", 0.3, metal=0.5))  # flush plate


def lavatorio(bm, W, D, H, c, mat, p):
    # the mirror as a light glossy grey, not a metal: without a reflection probe a metal mirror renders dark blue
    fr, lo, es = mat(c["frentes"], 0.5), mat(c["loica"], 0.15), mat(c["espelho"], 0.06)
    _caixa(bm, -W / 2, -D / 2 + 0.02, 0.35, W / 2, D / 2, 0.82, fr)                # wall-hung unit
    _frentes(bm, -W / 2, W / 2, -D / 2 + 0.02, 0.35, 0.82, fr, None, n=1)
    _caixa(bm, -W / 2, -D / 2, 0.82, W / 2, D / 2, 0.86, lo)                       # basin top
    _caixa(bm, -0.2, -D / 2 + 0.07, 0.858, 0.2, D / 2 - 0.12, 0.861, mat("#E4E6E6", 0.1))
    m = mat("#C9CCCE", 0.2, metal=0.9)
    _caixa(bm, -0.015, D / 2 - 0.1, 0.86, 0.015, D / 2 - 0.07, 1.02, m)            # tap
    _caixa(bm, -0.015, D / 2 - 0.22, 0.99, 0.015, D / 2 - 0.07, 1.02, m)
    _caixa(bm, -W / 2, D / 2 - 0.015, 1.0, W / 2, D / 2, H, es)                     # mirror


def duche(bm, W, D, H, c, mat, p):
    b, v, m = mat(c["base"], 0.35), mat(c["vidro"], 0.05, alfa=0.22), mat(c["metal"], 0.25, metal=0.9)
    _caixa(bm, -W / 2, -D / 2, 0, W / 2, D / 2, 0.04, b)                           # tray
    g = W * p.get("vidro", 0.55)                                                   # fixed glass on the front
    _caixa(bm, W / 2 - g, -D / 2 + 0.02, 0.04, W / 2, -D / 2 + 0.028, H, v)
    _caixa(bm, W / 2 - g, -D / 2 + 0.015, H - 0.03, W / 2, -D / 2 + 0.033, H, m)
    _caixa(bm, W / 2 - g - 0.01, -D / 2 + 0.015, 0.04, W / 2 - g, -D / 2 + 0.033, H, m)
    _caixa(bm, -0.015, D / 2 - 0.03, 0.95, 0.015, D / 2, H, m)                     # column + head
    _caixa(bm, -0.13, D / 2 - 0.3, H - 0.01, 0.13, D / 2 - 0.04, H, m)


def tv(bm, W, D, H, c, mat, p):
    mo, ec = mat(c["moldura"], 0.4), mat(c["ecra"], 0.08)
    _caixa(bm, -0.25, -D / 2, 0, 0.25, D / 2, 0.015, mo)                           # foot
    _caixa(bm, -0.04, 0.0, 0.015, 0.04, 0.03, 0.07, mo)
    _caixa(bm, -W / 2, -0.015, 0.07, W / 2, 0.03, H, mo)                            # screen
    _caixa(bm, -W / 2 + 0.008, -0.016, 0.078, W / 2 - 0.008, -0.015, H - 0.008, ec)


GERADORES = {"cozinha": cozinha, "ilha": ilha, "coluna": coluna, "mesa": mesa, "cama": cama, "roupeiro": roupeiro,
             "sanita": sanita, "lavatorio": lavatorio, "duche": duche, "tv": tv}


def angulo(frente):
    """Rotation about z (radians) that turns a front facing -y (S) to `frente` (S, E, N, W or degrees, 0 = S)."""
    if isinstance(frente, str):
        return math.radians({"S": 0, "E": 90, "N": 180, "W": 270}[frente.upper()])
    return math.radians(float(frente))
