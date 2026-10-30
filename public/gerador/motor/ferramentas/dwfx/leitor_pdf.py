"""Vector PDF drawings (AutoCAD plots) read like the DWFx ones. Pure Python (standard library), runs in the browser too.

    from ferramentas.dwfx.leitor_pdf import Pdf
    d = Pdf("plan.pdf"); d.info(); d.paths(1)

Same output as leitor.Dwfx.paths(): [{"fill", "stroke" ("#RRGGBB"), "sw" (mm), "subs": [([(x, y) mm], closed)]}] in
sheet millimetres with y DOWN from the top-left corner (as XPS / DWFx), so planta_arquitetura.py reads both alike.
What it understands: the page tree, FlateDecode content streams, q / Q / cm, colours (RGB, grey, CMYK, ICC-based and
indexed), paths (m l c v y h re) and their painting (S s f F f* B B* b b* n), Form XObjects (Do), page rotation.
Text and images are skipped. A scanned drawing (a picture) has no lines to read: it gives no paths.
"""
import math
import re
import zlib

MM = 25.4 / 72.0  # one PDF point in millimetres
_OBJ = re.compile(rb"(\d+)\s+(\d+)\s+obj\b")
_DELIM = b"()<>[]{}/%"
_ESPACO = b" \t\r\n\f\x00"


class Ref:
    __slots__ = ("n",)

    def __init__(self, n):
        self.n = n


class Nome(str):
    pass


class Op(str):
    pass


class Stream:
    def __init__(self, dic, raw):
        self.dic, self.raw = dic, raw


# ============================================================================ lexer / parser
def _tokens(b, i=0, fim=None):
    """PDF tokens from position i: numbers, Nome, bytes (strings), Op (keywords), '[', ']', '<<', '>>'."""
    n = len(b) if fim is None else fim
    while i < n:
        c = b[i:i + 1]
        if c in (b" ", b"\t", b"\r", b"\n", b"\f", b"\x00"):
            i += 1
        elif c == b"%":
            while i < n and b[i:i + 1] not in (b"\r", b"\n"):
                i += 1
        elif c == b"/":
            j = i + 1
            while j < n and b[j:j + 1] not in _ESPACO and b[j:j + 1] not in _DELIM:
                j += 1
            nome = re.sub(rb"#([0-9A-Fa-f]{2})", lambda m: bytes([int(m.group(1), 16)]), b[i + 1:j])
            yield Nome(nome.decode("latin-1")), j
            i = j
        elif c == b"(":
            nivel, j = 1, i + 1
            while j < n and nivel:
                ch = b[j:j + 1]
                if ch == b"\\":
                    j += 2
                    continue
                nivel += (ch == b"(") - (ch == b")")
                j += 1
            yield b[i + 1:j - 1], j
            i = j
        elif c == b"<":
            if b[i + 1:i + 2] == b"<":
                yield "<<", i + 2
                i += 2
            else:
                j = b.find(b">", i)
                j = n if j < 0 else j
                yield bytes.fromhex(re.sub(rb"[^0-9A-Fa-f]", b"", b[i + 1:j]).decode().ljust(2, "0")), j + 1
                i = j + 1
        elif c == b">" and b[i + 1:i + 2] == b">":
            yield ">>", i + 2
            i += 2
        elif c in (b"[", b"]", b"{", b"}"):
            yield c.decode(), i + 1
            i += 1
        else:
            j = i
            while j < n and b[j:j + 1] not in _ESPACO and b[j:j + 1] not in _DELIM:
                j += 1
            if j == i:
                i += 1
                continue
            t = b[i:j]
            try:
                yield (float(t) if (b"." in t or b"e" in t.lower()) else int(t)), j
            except ValueError:
                yield Op(t.decode("latin-1")), j
            i = j


class _Leitor:
    """Tokens with look-ahead; folds 'n g R' into Ref."""

    def __init__(self, b, i=0, fim=None):
        self.it = _tokens(b, i, fim)
        self.buf = []

    def _puxar(self, k):
        while len(self.buf) < k:
            try:
                self.buf.append(next(self.it))
            except StopIteration:
                return False
        return True

    def proximo(self):
        if not self._puxar(1):
            raise StopIteration
        t, fim = self.buf[0]
        if isinstance(t, int) and self._puxar(3) and isinstance(self.buf[1][0], int) and self.buf[2][0] == Op("R"):
            fim = self.buf[2][1]
            del self.buf[:3]
            return Ref(t), fim
        del self.buf[0]
        return t, fim

    def valor(self, t=None):
        """One object; t = its first token when already taken."""
        if t is None:
            t, _ = self.proximo()
        if t == "<<":
            d = {}
            while True:
                k, _ = self.proximo()
                if k == ">>":
                    return d
                d[k] = self.valor()
        if t == "[":
            arr = []
            while True:
                v, _ = self.proximo()
                if v == "]":
                    return arr
                arr.append(self.valor(v))
        return t


def _valor(it, primeiro):
    """For the content streams: arrays / dictionaries of operands (no references there)."""
    t = primeiro
    if t == "<<":
        d = {}
        while True:
            k, _ = next(it)
            if k == ">>":
                return d
            v, _ = next(it)
            d[k] = _valor(it, v)
    if t == "[":
        arr = []
        while True:
            v, _ = next(it)
            if v == "]":
                return arr
            arr.append(_valor(it, v))
    return t


def _objeto(b, pos):
    """The object after 'n g obj': (value, start of its stream data or None)."""
    L = _Leitor(b, pos)
    try:
        v = L.valor()
        t, fim = L.proximo()
    except StopIteration:
        return None, None
    if t == Op("stream"):
        return v, fim + (2 if b[fim:fim + 2] == b"\r\n" else 1)
    return v, None


# ============================================================================ document
class Pdf:
    def __init__(self, path):
        self.path = str(path)
        self.b = open(self.path, "rb").read() if not isinstance(path, (bytes, bytearray)) else bytes(path)
        self.pos = {}
        for m in _OBJ.finditer(self.b):
            self.pos[int(m.group(1))] = m.end()  # the last definition wins (incremental updates)
        self._cache = {}
        self._objstm()
        self.pages = self._paginas()

    # ---------------------------------------------------------------- objects
    def obj(self, x):
        """Resolve a Ref (or return x)."""
        while isinstance(x, Ref):
            n = x.n
            if n not in self._cache:
                if n not in self.pos:
                    self._cache[n] = None
                elif isinstance(self.pos[n], tuple):  # inside an object stream
                    self._cache[n] = self.pos[n][1]
                else:
                    v, ini = _objeto(self.b, self.pos[n])
                    if ini is not None and isinstance(v, dict):
                        comp = self.obj(v.get("Length"))
                        fim = ini + comp if isinstance(comp, int) and self.b[ini + comp:ini + comp + 30].lstrip().startswith(b"endstream") \
                            else self.b.find(b"endstream", ini)
                        v = Stream(v, self.b[ini:fim])
                    self._cache[n] = v
            x = self._cache[n]
        return x

    def dados(self, s):
        """A stream's decoded bytes (FlateDecode; other filters unsupported → empty)."""
        f = self.obj(s.dic.get("Filter"))
        fs = [self.obj(x) for x in (f if isinstance(f, list) else [f] if f else [])]
        d = s.raw
        for nome in fs:
            if nome in ("FlateDecode", "Fl"):
                try:
                    d = zlib.decompress(d)
                except zlib.error:
                    d = zlib.decompressobj().decompress(d)
            else:
                return b""
        return d

    def _objstm(self):
        """PDF 1.5 object streams: their objects become resolvable too."""
        for n in list(self.pos):
            if isinstance(self.pos[n], tuple):
                continue
            if b"/ObjStm" not in self.b[self.pos[n]:self.pos[n] + 200]:
                continue
            s = self.obj(Ref(n))
            if not isinstance(s, Stream) or s.dic.get("Type") != "ObjStm":
                continue
            d = self.dados(s)
            primeiro = s.dic.get("First", 0)
            cab = [t for t, _ in _tokens(d, 0, primeiro)]
            for k in range(0, len(cab) - 1, 2):
                num, off = cab[k], cab[k + 1]
                if num in self.pos and not isinstance(self.pos[num], tuple):
                    continue
                self.pos[num] = (None, _Leitor(d, primeiro + off).valor())

    def _paginas(self):
        raiz = None
        for m in re.finditer(rb"/Root\s+(\d+)\s+\d+\s+R", self.b):
            raiz = int(m.group(1))
        cat = self.obj(Ref(raiz)) if raiz is not None else None
        if not isinstance(cat, dict):
            cat = next((self.obj(Ref(n)) for n in self.pos if isinstance(self.obj(Ref(n)), dict)
                        and self.obj(Ref(n)).get("Type") == "Catalog"), None)
        out = []

        def andar(no, herdado):
            no = self.obj(no)
            if not isinstance(no, dict):
                return
            h = dict(herdado)
            for k in ("MediaBox", "CropBox", "Rotate", "Resources"):
                if k in no:
                    h[k] = self.obj(no[k])
            if no.get("Type") == "Pages" or "Kids" in no:
                for k in self.obj(no.get("Kids")) or []:
                    andar(k, h)
            else:
                out.append((no, h))

        if cat:
            andar(cat.get("Pages"), {})
        return out

    # ---------------------------------------------------------------- pages
    def info(self):
        out = []
        for k, (pg, h) in enumerate(self.pages, 1):
            x0, y0, x1, y1 = [float(self.obj(v)) for v in h.get("MediaBox", [0, 0, 595, 842])]
            rot = int(h.get("Rotate", 0) or 0) % 360
            w, hh = (x1 - x0) * MM, (y1 - y0) * MM
            out.append({"folha": k, "nome": f"Página {k}", "papel_mm": [round(hh if rot in (90, 270) else w, 1),
                                                                         round(w if rot in (90, 270) else hh, 1)]})
        return out

    def paths(self, folha):
        pg, h = self.pages[folha - 1]
        x0, y0, x1, y1 = [float(self.obj(v)) for v in h.get("MediaBox", [0, 0, 595, 842])]
        rot = int(h.get("Rotate", 0) or 0) % 360
        W, H = x1 - x0, y1 - y0
        # user space (points, y up) -> sheet mm, y down, rotation applied as the viewer shows it
        if rot == 90:
            base = (0, MM, MM, 0, -y0 * MM, -x0 * MM)
        elif rot == 180:
            base = (-MM, 0, 0, MM, (x1) * MM, -y0 * MM)
        elif rot == 270:
            base = (0, -MM, -MM, 0, y1 * MM, x1 * MM)
        else:
            base = (MM, 0, 0, -MM, -x0 * MM, y1 * MM)
        del W, H
        cont = self.obj(pg.get("Contents"))
        partes = cont if isinstance(cont, list) else [cont] if cont else []
        dados = b"\n".join(self.dados(self.obj(p)) for p in partes if isinstance(self.obj(p), Stream))
        out = []
        self._correr(dados, self.obj(h.get("Resources")) or {}, base, out, 0)
        return out

    def glyphs(self, folha):
        return []  # text is not read (AutoCAD plots draw it with embedded fonts; the scale is deduced instead)

    # ---------------------------------------------------------------- content
    def _cor(self, cs, vals):
        cs = self.obj(cs)
        nome = cs[0] if isinstance(cs, list) else cs
        try:
            if nome in ("DeviceRGB", "CalRGB", "RGB") or (nome == "ICCBased" and len(vals) == 3):
                r, g, b = vals[:3]
            elif nome in ("DeviceGray", "CalGray", "G") or (nome == "ICCBased" and len(vals) == 1):
                r = g = b = vals[0]
            elif nome in ("DeviceCMYK", "CMYK") or (nome == "ICCBased" and len(vals) == 4):
                c, m, y, k = vals[:4]
                r, g, b = (1 - c) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k)
            elif nome == "Indexed" and isinstance(cs, list):
                base, hival, tab = self.obj(cs[1]), cs[2], self.obj(cs[3])
                tab = self.dados(tab) if isinstance(tab, Stream) else tab
                nb = 3 if self.obj(base) in ("DeviceRGB", "CalRGB") else 1 if self.obj(base) in ("DeviceGray",) else 4
                i = int(vals[0]) * nb
                comp = [v / 255 for v in tab[i:i + nb]]
                return self._cor(base, comp)
            else:
                return None
        except (TypeError, ValueError, IndexError):
            return None
        return "#%02X%02X%02X" % tuple(max(0, min(255, round(v * 255))) for v in (r, g, b))

    def _correr(self, dados, recursos, ctm, out, nivel):
        if nivel > 8:
            return
        estado = {"ctm": ctm, "s": "#000000", "f": "#000000", "cs_s": "DeviceGray", "cs_f": "DeviceGray", "w": 1.0}
        pilha = []
        subs, atual = [], None
        args = []
        xobj = self.obj(recursos.get("XObject")) or {}
        cspaces = self.obj(recursos.get("ColorSpace")) or {}

        def pt(x, y):
            a, b, c, d, e, f = estado["ctm"]
            return (a * x + c * y + e, b * x + d * y + f)

        def fechar_atual():
            nonlocal atual
            if atual and len(atual[0]) > 1:
                subs.append(atual)
            atual = None

        def pintar(traco, preenche):
            nonlocal subs
            fechar_atual()
            if subs and (traco or preenche):
                a, b = estado["ctm"][0], estado["ctm"][1]
                out.append({"fill": estado["f"] if preenche else None, "stroke": estado["s"] if traco else None,
                            "sw": estado["w"] * math.hypot(a, b), "subs": [(s[0], s[1]) for s in subs]})
            subs = []

        def cs_de(n):
            return cspaces.get(n, n) if isinstance(cspaces, dict) else n

        it = _tokens(dados)
        for t, _ in it:
            if not isinstance(t, Op):
                if t == "[" or t == "<<":
                    args.append(_valor(it, t))
                else:
                    args.append(t)
                continue
            try:
                if t == "m":
                    fechar_atual()
                    atual = [[pt(*args[-2:])], False]
                elif t == "l" and atual:
                    atual[0].append(pt(*args[-2:]))
                elif t in ("c", "v", "y") and atual:
                    atual[0].append(pt(*args[-2:]))
                elif t == "h" and atual:
                    atual[0].append(atual[0][0])
                    atual[1] = True
                elif t == "re":
                    fechar_atual()
                    x, y, w, hh = args[-4:]
                    subs.append(([pt(x, y), pt(x + w, y), pt(x + w, y + hh), pt(x, y + hh), pt(x, y)], True))
                elif t in ("S", "s"):
                    if t == "s" and atual:
                        atual[0].append(atual[0][0])
                    pintar(True, False)
                elif t in ("f", "F", "f*"):
                    pintar(False, True)
                elif t in ("B", "B*", "b", "b*"):
                    if t.startswith("b") and atual:
                        atual[0].append(atual[0][0])
                    pintar(True, True)
                elif t == "n":
                    fechar_atual()
                    subs = []
                elif t == "q":
                    pilha.append(dict(estado))
                elif t == "Q" and pilha:
                    estado = pilha.pop()
                elif t == "cm":
                    a2, b2, c2, d2, e2, f2 = args[-6:]
                    a, b, c, d, e, f = estado["ctm"]
                    estado["ctm"] = (a2 * a + b2 * c, a2 * b + b2 * d, c2 * a + d2 * c, c2 * b + d2 * d,
                                     e2 * a + f2 * c + e, e2 * b + f2 * d + f)
                elif t == "w":
                    estado["w"] = float(args[-1])
                elif t == "RG":
                    estado["s"], estado["cs_s"] = self._cor("DeviceRGB", args[-3:]), "DeviceRGB"
                elif t == "rg":
                    estado["f"], estado["cs_f"] = self._cor("DeviceRGB", args[-3:]), "DeviceRGB"
                elif t == "G":
                    estado["s"], estado["cs_s"] = self._cor("DeviceGray", args[-1:]), "DeviceGray"
                elif t == "g":
                    estado["f"], estado["cs_f"] = self._cor("DeviceGray", args[-1:]), "DeviceGray"
                elif t == "K":
                    estado["s"], estado["cs_s"] = self._cor("DeviceCMYK", args[-4:]), "DeviceCMYK"
                elif t == "k":
                    estado["f"], estado["cs_f"] = self._cor("DeviceCMYK", args[-4:]), "DeviceCMYK"
                elif t == "CS":
                    estado["cs_s"] = cs_de(args[-1])
                elif t == "cs":
                    estado["cs_f"] = cs_de(args[-1])
                elif t in ("SC", "SCN"):
                    nums = [a for a in args if isinstance(a, (int, float))]
                    estado["s"] = self._cor(estado["cs_s"], nums) or estado["s"]
                elif t in ("sc", "scn"):
                    nums = [a for a in args if isinstance(a, (int, float))]
                    estado["f"] = self._cor(estado["cs_f"], nums) or estado["f"]
                elif t == "Do":
                    x = self.obj(xobj.get(args[-1])) if isinstance(xobj, dict) else None
                    if isinstance(x, Stream) and x.dic.get("Subtype") == "Form":
                        mat = [float(self.obj(v)) for v in (self.obj(x.dic.get("Matrix")) or [1, 0, 0, 1, 0, 0])]
                        a2, b2, c2, d2, e2, f2 = mat
                        a, b, c, d, e, f = estado["ctm"]
                        m = (a2 * a + b2 * c, a2 * b + b2 * d, c2 * a + d2 * c, c2 * b + d2 * d,
                             e2 * a + f2 * c + e, e2 * b + f2 * d + f)
                        rec = self.obj(x.dic.get("Resources")) or recursos
                        self._correr(self.dados(x), rec, m, out, nivel + 1)
                elif t == "BI":  # inline image: skip to EI
                    for t2, _ in it:
                        if t2 == Op("EI"):
                            break
            except (TypeError, ValueError, IndexError):
                pass
            args = []
