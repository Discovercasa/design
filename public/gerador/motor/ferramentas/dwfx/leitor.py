"""DWFx reader (Autodesk DWFx = XPS/OPC zip). Standard library only.

Coordinates returned are SHEET millimetres, origin top-left, y pointing down.
Multiply by the drawing scale (e.g. 1:50 -> x 0.05) to get metres.
"""
import html
import math
import re
import zipfile
import xml.etree.ElementTree as ET

NS = "{http://schemas.microsoft.com/xps/2005/06}"
PX2MM = 25.4 / 96.0
_TOK = re.compile(r"[FMLHVCQSAZmlhvcqsaz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _matrix(s):
    if not s or s.startswith("{"):
        return (1, 0, 0, 1, 0, 0)
    return tuple(float(t) for t in s.replace(" ", "").split(","))


def _mul(a, b):
    a11, a12, a21, a22, ax, ay = a
    b11, b12, b21, b22, bx, by = b
    return (a11 * b11 + a12 * b21, a11 * b12 + a12 * b22, a21 * b11 + a22 * b21,
            a21 * b12 + a22 * b22, ax * b11 + ay * b21 + bx, ax * b12 + ay * b22 + by)


def _apply(m, x, y):
    return (x * m[0] + y * m[2] + m[4], x * m[1] + y * m[3] + m[5])


def _parse_data(d):
    """XPS abbreviated path geometry -> list of (points, closed). Curves reduced to end points."""
    toks = _TOK.findall(d)
    i, subs, cur = 0, [], []
    x = y = sx = sy = 0.0
    cmd = None

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Ff":
                i += 1
                continue
            if cmd in "Zz":
                if cur:
                    subs.append((cur, True))
                    cur = []
                x, y = sx, sy
                continue
        if cmd in ("M", "m"):
            nx, ny = num(), num()
            if cmd == "m":
                nx += x; ny += y
            if cur:
                subs.append((cur, False))
            cur = [(nx, ny)]
            x, y, sx, sy = nx, ny, nx, ny
            cmd = "L" if cmd == "M" else "l"
        elif cmd in ("L", "l"):
            nx, ny = num(), num()
            if cmd == "l":
                nx += x; ny += y
            cur.append((nx, ny)); x, y = nx, ny
        elif cmd in ("H", "h"):
            nx = num() + (x if cmd == "h" else 0)
            cur.append((nx, y)); x = nx
        elif cmd in ("V", "v"):
            ny = num() + (y if cmd == "v" else 0)
            cur.append((x, ny)); y = ny
        elif cmd in ("C", "c"):
            v = [num() for _ in range(6)]
            nx, ny = v[4] + (x if cmd == "c" else 0), v[5] + (y if cmd == "c" else 0)
            cur.append((nx, ny)); x, y = nx, ny
        elif cmd in ("Q", "q", "S", "s"):
            v = [num() for _ in range(4)]
            nx, ny = v[2] + (x if cmd in "qs" else 0), v[3] + (y if cmd in "qs" else 0)
            cur.append((nx, ny)); x, y = nx, ny
        elif cmd in ("A", "a"):
            v = [num() for _ in range(7)]
            nx, ny = v[5] + (x if cmd == "a" else 0), v[6] + (y if cmd == "a" else 0)
            cur.append((nx, ny)); x, y = nx, ny
        else:
            i += 1
    if cur:
        subs.append((cur, False))
    return subs


class Dwfx:
    """One DWFx file. Sheets are numbered from 1 (as printed on the drawings, e.g. 1/2, 2/2)."""

    def __init__(self, path):
        self.path = str(path)
        self.zip = zipfile.ZipFile(self.path)
        self.names = self.zip.namelist()
        fdoc = [n for n in self.names if n.endswith("FixedDocument.fdoc")][0]
        self.pages = re.findall(r'PageContent Source="/([^"]+)"', self.zip.read(fdoc).decode("utf-8"))
        self._roots = {}

    # ------------------------------------------------------------------ metadata
    def info(self):
        out = []
        dsd = [n for n in self.names if n.endswith(".dsd")]
        dsd_txt = self.zip.read(dsd[0]).decode("utf-8", "replace") if dsd else ""
        for k, p in enumerate(self.pages, 1):
            desc = p.rsplit("/", 1)[0] + "/descriptor.xml"
            d = {"folha": k, "parte": p}
            if desc in self.names:
                t = self.zip.read(desc).decode("utf-8", "replace")
                m = re.search(r'<ePlot:Page [^>]*name="([^"]*)"', t)
                d["nome"] = html.unescape(m.group(1)) if m else ""
                m = re.search(r'<ePlot:Paper units="(\w+)" width="([\d.]+)" height="([\d.]+)"', t)
                if m:
                    d["papel_mm"] = [round(float(m.group(2)), 1), round(float(m.group(3)), 1)]
                for key, prop in (("dwg", "File Name"), ("programa", "Creator")):
                    m = re.search(r'name="%s" value="([^"]*)"' % prop, t)
                    if m:
                        d[key] = html.unescape(m.group(1))
                m = re.findall(r'name="Modification Time" value="([^"]*)"', t)
                if m:
                    d["modificado"] = m[0]
            out.append(d)
        m = re.search(r"Setup=(.*)", dsd_txt)
        if m and out:
            out[0]["setup"] = m.group(1).strip()
        return out

    # ------------------------------------------------------------------ parsing
    def root(self, folha):
        if folha not in self._roots:
            self._roots[folha] = ET.fromstring(self.zip.read(self.pages[folha - 1]))
        return self._roots[folha]

    def _walk(self, el, m, paths, glyphs):
        rt = el.get("RenderTransform")
        if rt:
            m = _mul(_matrix(rt), m)
        tag = el.tag.replace(NS, "")
        if tag == "Path" and paths is not None:
            d = el.get("Data")
            if d and not d.startswith("{"):
                subs = [([tuple(v * PX2MM for v in _apply(m, px, py)) for px, py in sp], cl)
                        for sp, cl in _parse_data(d)]
                paths.append({"fill": el.get("Fill"), "stroke": el.get("Stroke"),
                              "sw": float(el.get("StrokeThickness", 0) or 0) * math.hypot(m[0], m[1]) * PX2MM,
                              "subs": subs})
        elif tag == "Glyphs" and glyphs is not None:
            x, y = _apply(m, float(el.get("OriginX", 0)), float(el.get("OriginY", 0)))
            ang = round(math.degrees(math.atan2(-m[1], m[0])))
            h = float(el.get("FontRenderingEmSize", 0)) * math.hypot(m[0], m[1]) * PX2MM
            glyphs.append((x * PX2MM, y * PX2MM, ang, h, el.get("UnicodeString") or ""))
        for ch in el:
            self._walk(ch, m, paths, glyphs)

    def paths(self, folha):
        out = []
        self._walk(self.root(folha), (1, 0, 0, 1, 0, 0), out, None)
        return out

    def glyphs(self, folha):
        out = []
        self._walk(self.root(folha), (1, 0, 0, 1, 0, 0), None, out)
        return out


def linhas(glyphs):
    """Merge glyph runs on the same baseline into readable lines: list of dict(x, y, ang, h, text)."""
    rows = sorted(glyphs, key=lambda g: (g[2], round(g[1] * 2) / 2 if g[2] == 0 else round(g[0] * 2) / 2,
                                         g[0] if g[2] == 0 else -g[1]))
    out = []
    for x, y, a, h, t in rows:
        if out and out[-1]["ang"] == a == 0 and abs(out[-1]["y"] - y) < 0.6 and \
                0 <= x - out[-1]["xend"] < max(2.5, h * 1.2):
            out[-1]["text"] += t
            out[-1]["xend"] = x + len(t) * h * 0.55
            continue
        out.append({"x": x, "y": y, "ang": a, "h": h, "text": t, "xend": x + len(t) * h * 0.55})
    return sorted(out, key=lambda l: (l["y"], l["x"]))
