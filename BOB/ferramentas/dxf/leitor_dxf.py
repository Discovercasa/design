"""DXF drawings (AutoCAD, or a DWG converted with the ODA File Converter on the company PC). Pure Python.

    from ferramentas.dxf.leitor_dxf import Dxf
    d = Dxf("drawing.dxf")
    d.camadas()                    # {layer: entity count}
    d.paths(camadas=None)          # every stroke / fill, model space, block inserts expanded (metres, y UP)
    d.textos()                     # [{"x", "y", "h", "texto", "camada"}] (TEXT, MTEXT, ATTRIB; MTEXT codes stripped)
    d.faces3d()                    # [[(x, y, z) x 3 or 4]] — 3DFACE (a terrain model, MDT)

The paths have the shape of the DWFx / PDF readers ({"fill", "stroke", "sw", "subs": [(pts, closed)], "camada"}) but in
DRAWING UNITS with y up (a DXF has real coordinates, usually metres); `para_folha(paths, escala)` turns them into
"sheet millimetres" (y down) at a chosen scale, so ferramentas/planta/analisar.py reads them like a plotted sheet.
Read: LINE, LWPOLYLINE (bulges as arcs), POLYLINE/VERTEX, ARC, CIRCLE, ELLIPSE (approximated), SPLINE (control
points), SOLID, HATCH (boundary loops: polylines and line/arc edges), INSERT (blocks, nested, scaled and rotated),
3DFACE, TEXT, MTEXT, ATTRIB. Colours: the ACI index (and true colour, code 420) of the entity or its layer.
"""
import math
import re

ACI = {1: "#FF0000", 2: "#FFFF00", 3: "#00FF00", 4: "#00FFFF", 5: "#0000FF", 6: "#FF00FF", 7: "#000000", 8: "#808080",
       9: "#C0C0C0", 250: "#333333", 251: "#505050", 252: "#696969", 253: "#828282", 254: "#BEBEBE", 255: "#FFFFFF"}


def _cor(aci, rgb=None):
    if rgb is not None:
        return "#%06X" % (int(rgb) & 0xFFFFFF)
    try:
        aci = abs(int(aci))
    except (TypeError, ValueError):
        return "#000000"
    return ACI.get(aci, "#7F7F7F")


def _arco(cx, cy, r, a0, a1, passo=math.radians(6)):
    """Points of an arc (angles in radians, counter-clockwise from a0 to a1)."""
    while a1 < a0:
        a1 += 2 * math.pi
    n = max(2, int((a1 - a0) / passo) + 1)
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def _bulge(p0, p1, b):
    """Points from p0 to p1 along a polyline bulge (tan of a quarter of the arc's angle), p0 excluded."""
    if abs(b) < 1e-9:
        return [p1]
    (x0, y0), (x1, y1) = p0, p1
    c = math.hypot(x1 - x0, y1 - y0)
    if c < 1e-12:
        return [p1]
    ang = 4 * math.atan(b)
    r = c / (2 * math.sin(ang / 2))
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    d = r * math.cos(ang / 2)
    nx, ny = -(y1 - y0) / c, (x1 - x0) / c
    cx, cy = mx + nx * d, my + ny * d
    a0 = math.atan2(y0 - cy, x0 - cx)
    a1 = a0 + ang
    n = max(2, int(abs(ang) / math.radians(6)) + 1)
    pts = [(cx + abs(r) * math.cos(a0 + (a1 - a0) * i / n), cy + abs(r) * math.sin(a0 + (a1 - a0) * i / n)) for i in range(1, n + 1)]
    pts[-1] = p1
    return pts


def _mtexto(t):
    """MTEXT without its formatting codes."""
    t = re.sub(r"\\[Pp]", " ", t)
    t = re.sub(r"\\[A-Za-z][^;\\{}]*;", "", t)
    t = re.sub(r"\\[A-Za-z]", "", t)
    return t.replace("{", "").replace("}", "").replace("%%c", "Ø").replace("%%d", "°").replace("%%p", "±").strip()


class Dxf:
    def __init__(self, caminho):
        txt = open(caminho, encoding="utf-8", errors="replace").read()
        if "AC1009" in txt[:2000] or "ANSI_" in txt[:3000]:
            pass
        linhas = txt.splitlines()
        self.pares = [(linhas[i].strip(), linhas[i + 1].rstrip("\r")) for i in range(0, len(linhas) - 1, 2)]
        self.cor_camada = {}
        self.blocos = {}
        self.entidades = []
        self._ler()

    # ------------------------------------------------------------------ parsing
    def _ler(self):
        sec = None
        tabela = None
        cur = None
        bloco = None
        lista = None

        def fechar():
            nonlocal cur
            if cur is not None and lista is not None:
                lista.append(cur)
            cur = None
        for c, v in self.pares:
            if c == "0" and v == "SECTION":
                fechar()
                sec = "?"
                continue
            if sec == "?" and c == "2":
                sec = v
                lista = self.entidades if sec == "ENTITIES" else None
                continue
            if c == "0" and v == "ENDSEC":
                fechar()
                sec = None
                continue
            if sec == "TABLES":
                if c == "0":
                    if cur and cur.get("t") == "LAYER":
                        self.cor_camada[cur.get("2", "")] = (cur.get("62"), cur.get("420"))
                    cur = {"t": v}
                elif cur is not None and c in ("2", "62", "420"):
                    cur[c] = v
                continue
            if sec == "BLOCKS":
                if c == "0":
                    fechar()
                    if v == "BLOCK":
                        bloco = {"nome": None, "base": [0.0, 0.0], "ents": []}
                        cur = None
                        lista = None
                        tabela = "cab"
                        continue
                    if v == "ENDBLK":
                        if bloco and bloco["nome"]:
                            self.blocos[bloco["nome"]] = bloco
                        bloco = None
                        lista = None
                        tabela = None
                        continue
                    tabela = None
                    if bloco is not None:
                        lista = bloco["ents"]
                        cur = {"tipo": v, "g": []}
                    continue
                if tabela == "cab" and bloco is not None:
                    if c == "2" and bloco["nome"] is None:
                        bloco["nome"] = v
                    elif c == "10":
                        bloco["base"][0] = float(v)
                    elif c == "20":
                        bloco["base"][1] = float(v)
                    continue
                if cur is not None:
                    cur["g"].append((c, v))
                continue
            if sec == "ENTITIES":
                if c == "0":
                    fechar()
                    cur = {"tipo": v, "g": []}
                    continue
                if cur is not None:
                    cur["g"].append((c, v))

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _um(e, c, d=None):
        for k, v in e["g"]:
            if k == c:
                return v
        return d

    @staticmethod
    def _todos(e, c):
        return [v for k, v in e["g"] if k == c]

    def _cor_de(self, e, camada):
        aci, rgb = self._um(e, "62"), self._um(e, "420")
        if rgb is None and (aci is None or aci in ("256", "0")):
            aci, rgb = self.cor_camada.get(camada, ("7", None))
        return _cor(aci, rgb)

    def camadas(self):
        out = {}
        for e in self.entidades:
            k = self._um(e, "8", "0")
            out[k] = out.get(k, 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    # ------------------------------------------------------------------ geometry of one entity (local coordinates)
    def _geometria(self, e):
        """[(pts, closed, fill)] of an entity, in its own (block) coordinates."""
        t = e["tipo"]
        f = lambda c, d=0.0: float(self._um(e, c, d))  # noqa: E731
        if t == "LINE":
            return [([(f("10"), f("20")), (f("11"), f("21"))], False, False)]
        if t == "LWPOLYLINE":
            pts, bul = [], []
            x = None
            for k, v in e["g"]:
                if k == "10":
                    x = float(v)
                elif k == "20" and x is not None:
                    pts.append((x, float(v)))
                    bul.append(0.0)
                    x = None
                elif k == "42" and bul:
                    bul[-1] = float(v)
            fechado = int(self._um(e, "70", "0") or 0) & 1 == 1
            return [(self._com_bulges(pts, bul, fechado), fechado, False)] if len(pts) >= 2 else []
        if t == "CIRCLE":
            return [(_arco(f("10"), f("20"), f("40"), 0, 2 * math.pi), True, False)]
        if t == "ARC":
            return [(_arco(f("10"), f("20"), f("40"), math.radians(f("50")), math.radians(f("51"))), False, False)]
        if t == "ELLIPSE":
            cx, cy, mx, my, rr = f("10"), f("20"), f("11"), f("21"), f("40", 1.0)
            a0, a1 = f("41", 0.0), f("42", 2 * math.pi)
            ma = math.hypot(mx, my)
            ang = math.atan2(my, mx)
            pts = []
            n = 36
            if a1 < a0:
                a1 += 2 * math.pi
            for i in range(n + 1):
                u = a0 + (a1 - a0) * i / n
                px, py = ma * math.cos(u), ma * rr * math.sin(u)
                pts.append((cx + px * math.cos(ang) - py * math.sin(ang), cy + px * math.sin(ang) + py * math.cos(ang)))
            return [(pts, abs(a1 - a0 - 2 * math.pi) < 1e-6, False)]
        if t == "SPLINE":
            xs, ys = [float(v) for v in self._todos(e, "10")], [float(v) for v in self._todos(e, "20")]
            pts = list(zip(xs, ys))
            return [(pts, False, False)] if len(pts) >= 2 else []
        if t in ("SOLID", "TRACE"):
            p = [(f("10"), f("20")), (f("11"), f("21")), (f("13"), f("23")), (f("12"), f("22"))]
            return [(p + [p[0]], True, True)]
        if t == "HATCH":
            return [(pts, True, True) for pts in self._laços(e)]
        return []

    @staticmethod
    def _com_bulges(pts, bul, fechado):
        out = [pts[0]]
        n = len(pts)
        for i in range(n if fechado else n - 1):
            a, b = pts[i], pts[(i + 1) % n]
            out += _bulge(a, b, bul[i])
        return out

    def _laços(self, e):
        """The boundary loops of a HATCH."""
        g = e["g"]
        lacos = []
        i = 0
        while i < len(g):
            if g[i][0] == "92":   # boundary path type flag
                tipo = int(g[i][1])
                i += 1
                if tipo & 2:      # polyline
                    tem_bulge = nv = 0
                    fech = 0
                    pts, bul = [], []
                    while i < len(g) and g[i][0] in ("72", "73", "93"):
                        if g[i][0] == "72":
                            tem_bulge = int(g[i][1])
                        elif g[i][0] == "73":
                            fech = int(g[i][1])
                        else:
                            nv = int(g[i][1])
                        i += 1
                    while i < len(g) and len(pts) < nv:
                        if g[i][0] == "10":
                            x = float(g[i][1])
                            y = float(g[i + 1][1]) if i + 1 < len(g) and g[i + 1][0] == "20" else 0.0
                            pts.append((x, y))
                            bul.append(0.0)
                            i += 2
                            if tem_bulge and i < len(g) and g[i][0] == "42":
                                bul[-1] = float(g[i][1])
                                i += 1
                        else:
                            i += 1
                    if len(pts) >= 3:
                        lacos.append(self._com_bulges(pts, bul, True))
                else:              # edges
                    ne = 0
                    if i < len(g) and g[i][0] == "93":
                        ne = int(g[i][1])
                        i += 1
                    pts = []
                    for _ in range(ne):
                        if i >= len(g) or g[i][0] != "72":
                            break
                        et = int(g[i][1])
                        i += 1
                        vals = {}
                        while i < len(g) and g[i][0] not in ("72", "97", "92", "75"):
                            vals.setdefault(g[i][0], []).append(g[i][1])
                            i += 1
                        try:
                            if et == 1:
                                p0 = (float(vals["10"][0]), float(vals["20"][0]))
                                p1 = (float(vals["11"][0]), float(vals["21"][0]))
                                if not pts:
                                    pts.append(p0)
                                pts.append(p1)
                            elif et == 2:
                                cx, cy, r = float(vals["10"][0]), float(vals["20"][0]), float(vals["40"][0])
                                a0, a1 = math.radians(float(vals["50"][0])), math.radians(float(vals["51"][0]))
                                ccw = int(vals.get("73", ["1"])[0])
                                arc = _arco(cx, cy, r, a0, a1) if ccw else list(reversed(_arco(cx, cy, r, -a1, -a0)))
                                if not ccw:
                                    arc = [(x, 2 * cy - y) for x, y in arc]
                                pts += arc
                        except (KeyError, IndexError, ValueError):
                            pass
                    if len(pts) >= 3:
                        lacos.append(pts)
                continue
            i += 1
        return lacos

    # ------------------------------------------------------------------ public views
    def paths(self, camadas=None, sem_camadas=()):
        """Model space strokes and fills (inserts expanded), drawing units, y up: [{fill, stroke, sw, subs, camada}]."""
        out = []
        filtro = set(camadas) if camadas else None
        sem = set(sem_camadas)

        def andar(ents, M, camada_pai, nivel):
            for e in ents:
                cam = self._um(e, "8", "0")
                if cam == "0" and camada_pai:
                    cam = camada_pai
                if e["tipo"] == "INSERT":
                    b = self.blocos.get(self._um(e, "2", ""))
                    if not b or nivel > 6:
                        continue
                    sx, sy = float(self._um(e, "41", 1.0)), float(self._um(e, "42", 1.0))
                    r = math.radians(float(self._um(e, "50", 0.0)))
                    tx, ty = float(self._um(e, "10", 0.0)), float(self._um(e, "20", 0.0))
                    bx, by = b["base"]
                    c, s = math.cos(r), math.sin(r)
                    # local -> parent: translate(-base), scale, rotate, translate(insert)
                    L = (sx * c, sx * s, -sy * s, sy * c, tx - (bx * sx * c - by * sy * s), ty - (bx * sx * s + by * sy * c))
                    andar(b["ents"], _mul(L, M), cam, nivel + 1)
                    continue
                if (filtro and cam not in filtro) or cam in sem:
                    continue
                cor = self._cor_de(e, cam)
                for pts, fechado, cheio in self._geometria(e):
                    pts = [_ap(M, x, y) for x, y in pts]
                    out.append({"fill": cor if cheio else None, "stroke": None if cheio else cor, "sw": 0.0,
                                "subs": [(pts, fechado)], "camada": cam, "tipo": e["tipo"]})
        andar(self.entidades, (1, 0, 0, 1, 0, 0), None, 0)
        return out

    def textos(self):
        out = []
        for e in self.entidades:
            if e["tipo"] not in ("TEXT", "MTEXT", "ATTRIB"):
                continue
            t = "".join(self._todos(e, "3")) + "".join(self._todos(e, "1"))
            if e["tipo"] == "MTEXT":
                t = _mtexto(t)
            out.append({"x": float(self._um(e, "10", 0)), "y": float(self._um(e, "20", 0)),
                        "h": float(self._um(e, "40", 0) or 0), "texto": t.strip(), "camada": self._um(e, "8", "0")})
        return out

    def faces3d(self, camadas=None):
        out = []
        for e in self.entidades:
            if e["tipo"] != "3DFACE" or (camadas and self._um(e, "8", "0") not in camadas):
                continue
            p = [tuple(float(self._um(e, f"{a}{k}", 0)) for a in "123") for k in "0123"]
            if p[3] == p[2]:
                p = p[:3]
            out.append(p)
        return out


def _mul(A, B):
    """Affine (a, b, c, d, e, f): x' = a x + c y + e, y' = b x + d y + f. Returns B after A."""
    a1, b1, c1, d1, e1, f1 = A
    a2, b2, c2, d2, e2, f2 = B
    return (a1 * a2 + b1 * c2, a1 * b2 + b1 * d2, c1 * a2 + d1 * c2, c1 * b2 + d1 * d2,
            e1 * a2 + f1 * c2 + e2, e1 * b2 + f1 * d2 + f2)


def _ap(M, x, y):
    a, b, c, d, e, f = M
    return (a * x + c * y + e, b * x + d * y + f)


def para_folha(paths, escala, origem=(0.0, 0.0), unidade_m=1.0):
    """Drawing units (y up) -> 'sheet millimetres' (y down) at 1:escala, from `origem` (drawing units): what
    ferramentas/planta/analisar.py reads. unidade_m: metres per drawing unit (1 for metres, 0.001 for millimetres)."""
    k = unidade_m * 1000.0 / escala
    ox, oy = origem
    out = []
    for p in paths:
        q = dict(p)
        q["subs"] = [([((x - ox) * k, -(y - oy) * k) for x, y in pts], cl) for pts, cl in p["subs"]]
        out.append(q)
    return out
