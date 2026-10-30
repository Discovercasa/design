"""Minimal vector PDF writer (pure Python, standard library only).

Pages in millimetres with the origin at the bottom-left (y up, like a plan). Lines, polylines, polygons
(stroke / fill / hatch), rectangles, text in Helvetica / Helvetica-Bold (WinAnsi: Portuguese accents work),
rotated text, dashed lines and clipping. Used by gerar.py for the production documents.
"""
import zlib

MM = 72 / 25.4  # points per millimetre

# Helvetica advance widths (1/1000 em), characters 32..126
_HV = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556, 556, 556,
       556, 556, 556, 556, 278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667,
       556, 833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556,
       556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556, 500, 722,
       500, 500, 500, 334, 260, 334, 584]
_HB = [278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556, 556, 556,
       556, 556, 556, 556, 333, 333, 584, 584, 584, 611, 975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722,
       611, 833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333, 278, 333, 584, 556, 333, 556,
       611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611, 611, 611, 389, 556, 333, 611, 556, 778,
       556, 556, 500, 389, 280, 389, 584]
_TROCA = {"≈": "~", "→": "->", "←": "<-", "≤": "<=", "≥": ">=", "−": "-", "’": "'", "‘": "'", "“": '"', "”": '"',
          "…": "...", "Δ": "D", "≠": "!="}
_BASE = str.maketrans("áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ",
                      "aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCN")


def _limpo(s):
    s = "".join(_TROCA.get(c, c) for c in str(s))
    return s.encode("cp1252", errors="replace").decode("cp1252")


def largura(texto, tam, negrito=False):
    """Width in mm of `texto` at font size `tam` (mm)."""
    tab = _HB if negrito else _HV
    tot = 0
    for c in _limpo(texto):
        b = c.translate(_BASE)
        o = ord(b)
        if 32 <= o <= 126:
            tot += tab[o - 32]
        elif c in "×±÷":
            tot += 584
        elif c in "ºª²³":
            tot += 350
        else:
            tot += 556
    return tot / 1000 * tam


def _esc(s):
    b = _limpo(s).encode("cp1252", errors="replace")
    out = []
    for x in b:
        ch = chr(x)
        if ch in "()\\":
            out.append("\\" + ch)
        elif x < 32 or x > 126:
            out.append("\\%03o" % x)
        else:
            out.append(ch)
    return "".join(out)


def _n(v):
    return ("%.3f" % v).rstrip("0").rstrip(".") or "0"


def hexcor(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


class Pagina:
    def __init__(self, w, h):
        self.w, self.h, self.ops, self.cmds = w, h, [], []  # cmds: the same drawing for the SVG preview

    # ------------------------------------------------------------------ state
    def _estilo(self, esp, cor, tracejado, preench=None):
        o = ["%s w" % _n(esp * MM)]
        if cor is not None:
            o.append("%s %s %s RG" % tuple(_n(c) for c in cor))
        if preench is not None:
            o.append("%s %s %s rg" % tuple(_n(c) for c in preench))
        o.append(("[%s] 0 d" % " ".join(_n(d * MM) for d in tracejado)) if tracejado else "[] 0 d")
        return " ".join(o)

    def _cam(self, pts, fechar):
        s = ["%s %s m" % (_n(pts[0][0] * MM), _n(pts[0][1] * MM))]
        s += ["%s %s l" % (_n(x * MM), _n(y * MM)) for x, y in pts[1:]]
        if fechar:
            s.append("h")
        return " ".join(s)

    # ------------------------------------------------------------------ drawing
    def linha(self, x1, y1, x2, y2, esp=0.18, cor=(0, 0, 0), tracejado=None):
        self.cmds.append(("poli", [(x1, y1), (x2, y2)], False, esp, cor, None, tracejado))
        self.ops.append("q %s 1 J %s Q" % (self._estilo(esp, cor, tracejado), self._cam([(x1, y1), (x2, y2)], False) + " S"))

    def poli(self, pts, fechar=True, esp=0.18, cor=(0, 0, 0), preench=None, tracejado=None):
        if len(pts) < 2:
            return
        self.cmds.append(("poli", list(pts), fechar, esp, cor, preench, tracejado))
        op = "B" if (preench is not None and cor is not None) else ("f" if preench is not None else "S")
        if not fechar and op != "S":
            op = "S"
        self.ops.append("q 1 j %s %s %s Q" % (self._estilo(esp, cor, tracejado, preench), self._cam(pts, fechar), op))

    def ret(self, x, y, w, h, **kw):
        self.poli([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True, **kw)

    def tracejar(self, pts, passo=1.2, ang=45, esp=0.1, cor=(0, 0, 0)):
        """Hatch the polygon `pts` with parallel lines (clip)."""
        if len(pts) < 3:
            return
        import math
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        r = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2 + passo
        a = math.radians(ang)
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        self.cmds.append(("trac", list(pts), passo, ang, esp, cor))
        linhas = []
        k = -r
        while k <= r:
            px, py = cx + nx * k, cy + ny * k
            linhas.append(self._cam([(px - dx * r, py - dy * r), (px + dx * r, py + dy * r)], False) + " S")
            k += passo
        self.ops.append("q %s W n %s %s Q" % (self._cam(pts, True), self._estilo(esp, cor, None), " ".join(linhas)))

    def texto(self, x, y, s, tam=2.5, cor=(0, 0, 0), negrito=False, alinh="e", ang=0.0):
        """Text with its baseline at (x, y); alinh e (left) / c (centre) / d (right); ang in degrees."""
        import math
        s = str(s)
        if not s:
            return
        self.cmds.append(("texto", x, y, s, tam, cor, negrito, alinh, ang))
        w = largura(s, tam, negrito)
        dxs = {"e": 0.0, "c": -w / 2, "d": -w}[alinh]
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        x0, y0 = x + dxs * ca, y + dxs * sa
        self.ops.append("q %s %s %s rg BT /%s %s Tf %s %s %s %s %s %s Tm (%s) Tj ET Q" % (
            _n(cor[0]), _n(cor[1]), _n(cor[2]), "F2" if negrito else "F1", _n(tam * MM),
            _n(ca), _n(sa), _n(-sa), _n(ca), _n(x0 * MM), _n(y0 * MM), _esc(s)))

    def svg(self, escala=4.0):
        """The page as SVG (preview), `escala` px per mm."""
        import math
        from xml.sax.saxutils import escape
        H = self.h

        def c(cor):
            return "none" if cor is None else "#%02x%02x%02x" % tuple(int(round(v * 255)) for v in cor)

        def pt(x, y):
            return "%s,%s" % (_n(x), _n(H - y))

        out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %s %s">'
               % (self.w * escala, self.h * escala, _n(self.w), _n(self.h)), '<rect width="100%" height="100%" fill="#fff"/>']
        nclip = 0
        for cmd in self.cmds:
            if cmd[0] == "poli":
                _k, pts, fechar, esp, cor, preench, trac = cmd
                tag = "polygon" if fechar else "polyline"
                da = (' stroke-dasharray="%s"' % " ".join(_n(d) for d in trac)) if trac else ""
                out.append('<%s points="%s" fill="%s" stroke="%s" stroke-width="%s"%s/>' % (
                    tag, " ".join(pt(*p) for p in pts), c(preench) if fechar else "none", c(cor), _n(esp), da))
            elif cmd[0] == "trac":
                _k, pts, passo, ang, esp, cor = cmd
                nclip += 1
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
                r = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2 + passo
                a = math.radians(ang)
                dx, dy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
                ls = []
                k = -r
                while k <= r:
                    px, py = cx + nx * k, cy + ny * k
                    ls.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (_n(px - dx * r), _n(H - (py - dy * r)), _n(px + dx * r), _n(H - (py + dy * r))))
                    k += passo
                out.append('<clipPath id="c%d"><polygon points="%s"/></clipPath><g clip-path="url(#c%d)" stroke="%s" stroke-width="%s">%s</g>'
                           % (nclip, " ".join(pt(*p) for p in pts), nclip, c(cor), _n(esp), "".join(ls)))
            else:
                _k, x, y, s, tam, cor, neg, alinh, ang = cmd
                anc = {"e": "start", "c": "middle", "d": "end"}[alinh]
                out.append('<text x="%s" y="%s" font-family="Helvetica, Arial, sans-serif" font-size="%s"%s fill="%s" text-anchor="%s"%s>%s</text>' % (
                    _n(x), _n(H - y), _n(tam * 1.0), ' font-weight="bold"' if neg else "", c(cor), anc,
                    (' transform="rotate(%s %s %s)"' % (_n(-ang), _n(x), _n(H - y))) if ang else "", escape(s)))
        out.append("</svg>")
        return "\n".join(out)

    def conteudo(self):
        return "\n".join(self.ops).encode("latin-1")


class PDF:
    def __init__(self, titulo="", autor="DiscoverCasa"):
        self.paginas, self.titulo, self.autor = [], titulo, autor

    def pagina(self, w=420.0, h=297.0):
        p = Pagina(w, h)
        self.paginas.append(p)
        return p

    def gravar_svg(self, pasta, prefixo, escala=4.0):
        """Every page as an SVG preview: <pasta>/<prefixo>_<n>.svg."""
        from pathlib import Path
        Path(pasta).mkdir(parents=True, exist_ok=True)
        for i, p in enumerate(self.paginas, 1):
            (Path(pasta) / f"{prefixo}_{i}.svg").write_text(p.svg(escala), encoding="utf-8")

    def gravar(self, caminho):
        objs = []

        def novo(corpo):
            objs.append(corpo)
            return len(objs)

        f1 = novo(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        f2 = novo(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        raiz_pags = novo(None)  # filled below
        kids = []
        for p in self.paginas:
            dados = zlib.compress(p.conteudo())
            c = novo(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(dados) + dados + b"\nendstream")
            pg = novo(("<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %s %s] /Resources << /Font << /F1 %d 0 R /F2 %d 0 R >> >> "
                       "/Contents %d 0 R >>" % (raiz_pags, _n(p.w * MM), _n(p.h * MM), f1, f2, c)).encode("latin-1"))
            kids.append(pg)
        objs[raiz_pags - 1] = ("<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join("%d 0 R" % k for k in kids), len(kids))).encode()
        info = novo(("<< /Title (%s) /Author (%s) /Producer (BOB - DiscoverCasa) >>" % (_esc(self.titulo), _esc(self.autor))).encode("latin-1"))
        cat = novo(("<< /Type /Catalog /Pages %d 0 R >>" % raiz_pags).encode())
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offs = []
        for i, corpo in enumerate(objs, 1):
            offs.append(len(out))
            out += b"%d 0 obj\n" % i + corpo + b"\nendobj\n"
        xref = len(out)
        out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
        for o in offs:
            out += b"%010d 00000 n \n" % o
        out += b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, cat, info, xref)
        with open(caminho, "wb") as fh:
            fh.write(bytes(out))
