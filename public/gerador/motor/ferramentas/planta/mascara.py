"""A binary image held as one Python int per row (bit x = column x). Pure Python, fast enough in the browser too.

Morphology works on whole rows at once (shifts and AND / OR of big ints), flood fill with the "occluded fill" of
chess bitboards (log2(width) shifts per row), so a plan of a few hundred thousand pixels is handled in seconds.
Coordinates: column x to the right, row y down (as the sheet).
"""


class Mascara:
    def __init__(self, w, h, linhas=None):
        self.w, self.h = int(w), int(h)
        self.cheia = (1 << self.w) - 1
        self.r = list(linhas) if linhas is not None else [0] * self.h

    # ------------------------------------------------------------------ drawing
    def copia(self):
        return Mascara(self.w, self.h, self.r)

    def ponto(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.r[y] |= 1 << x

    def segmento(self, x0, y0, x1, y1):
        """A 1-pixel line (Bresenham) between two points in pixels (floats rounded)."""
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        if dy == 0:   # horizontal: one OR
            if 0 <= y0 < self.h:
                a, b = max(0, min(x0, x1)), min(self.w - 1, max(x0, x1))
                if a <= b:
                    self.r[y0] |= ((1 << (b - a + 1)) - 1) << a
            return
        err = dx + dy
        w, h, r = self.w, self.h, self.r
        while True:
            if 0 <= x0 < w and 0 <= y0 < h:
                r[y0] |= 1 << x0
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def poligono(self, pts):
        """Fill a polygon (even-odd, pixel centres) given in pixels."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0, y1 = max(0, int(min(ys))), min(self.h - 1, int(max(ys)) + 1)
        n = len(pts)
        for y in range(y0, y1 + 1):
            yc = y + 0.5
            xs = []
            for i in range(n):
                (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
                if (ay <= yc < by) or (by <= yc < ay):
                    xs.append(ax + (yc - ay) * (bx - ax) / (by - ay))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                xa, xb = max(0, int(round(a))), min(self.w - 1, int(round(b)) - 1)
                if xa <= xb:
                    self.r[y] |= ((1 << (xb - xa + 1)) - 1) << xa

    # ------------------------------------------------------------------ set operations
    def ou(self, o):
        return Mascara(self.w, self.h, [a | b for a, b in zip(self.r, o.r)])

    def e(self, o):
        return Mascara(self.w, self.h, [a & b for a, b in zip(self.r, o.r)])

    def menos(self, o):
        return Mascara(self.w, self.h, [a & ~b for a, b in zip(self.r, o.r)])

    def inverso(self):
        c = self.cheia
        return Mascara(self.w, self.h, [c & ~a for a in self.r])

    def contar(self):
        return sum(a.bit_count() for a in self.r)

    def vazia(self):
        return not any(self.r)

    def bit(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and (self.r[y] >> x) & 1

    # ------------------------------------------------------------------ morphology (square 3x3 element, n times)
    def dilatar(self, n=1):
        r, c = self.r, self.cheia
        for _ in range(n):
            h_ = [(a | (a << 1) | (a >> 1)) & c for a in r]
            r = [h_[y] | (h_[y - 1] if y else 0) | (h_[y + 1] if y + 1 < self.h else 0) for y in range(self.h)]
        return Mascara(self.w, self.h, r)

    def erodir(self, n=1):
        r, c = self.r, self.cheia
        for _ in range(n):
            h_ = [a & (a << 1) & (a >> 1) & c for a in r]   # outside the image counts as empty
            r = [h_[y] & (h_[y - 1] if y else 0) & (h_[y + 1] if y + 1 < self.h else 0) for y in range(self.h)]
        return Mascara(self.w, self.h, r)

    def fechar(self, n=1):
        return self.dilatar(n).erodir(n)

    def abrir(self, n=1):
        return self.erodir(n).dilatar(n)

    # ------------------------------------------------------------------ flood fill and components (4-connected)
    def _horizontal(self, g, m):
        """All bits of row mask m reachable from g along the row (g within m)."""
        pro, a = m, g
        s = 1
        while s < self.w:
            a |= pro & (a << s)
            pro &= pro << s
            s <<= 1
        pro, b = m, a
        s = 1
        while s < self.w:
            b |= pro & (b >> s)
            pro &= pro >> s
            s <<= 1
        return b & m

    def preencher(self, sementes):
        """Flood fill inside this mask from {row: bits}; returns {row: bits} of the region(s) reached."""
        r = self.r
        cur = {}
        fila = []
        for y, b in sementes.items():
            b &= r[y]
            if b:
                cur[y] = b
                fila.append(y)
        while fila:
            y = fila.pop()
            b = self._horizontal(cur[y], r[y])
            cur[y] = b
            for yy in (y - 1, y + 1):
                if 0 <= yy < self.h:
                    novo = b & r[yy] & ~cur.get(yy, 0)
                    if novo:
                        cur[yy] = cur.get(yy, 0) | novo
                        fila.append(yy)
        return cur

    def componentes(self, area_min=1):
        """Connected regions (4-connected): [{"linhas": {row: bits}, "area", "caixa": (x0, y0, x1, y1)}]."""
        resto = list(self.r)
        tmp = Mascara(self.w, self.h, resto)
        out = []
        for y in range(self.h):
            while resto[y]:
                semente = resto[y] & -resto[y]
                comp = tmp.preencher({y: semente})
                area = 0
                x0, x1 = self.w, -1
                for yy, b in comp.items():
                    resto[yy] &= ~b
                    area += b.bit_count()
                    x0 = min(x0, (b & -b).bit_length() - 1)
                    x1 = max(x1, b.bit_length() - 1)
                if area >= area_min:
                    out.append({"linhas": comp, "area": area, "caixa": (x0, min(comp), x1, max(comp))})
        return out


def de_linhas(w, h, linhas):
    """A mask from a component's {row: bits}."""
    r = [0] * h
    for y, b in linhas.items():
        r[y] = b
    return Mascara(w, h, r)


def profundidade(linhas):
    """How many 4-neighbour erosions a region survives (≈ half its thickness in pixels): its 'depth'."""
    cur = dict(linhas)
    n = 0
    while cur:
        novo = {}
        for y, b in cur.items():
            e = b & (b << 1) & (b >> 1) & cur.get(y - 1, 0) & cur.get(y + 1, 0)
            if e:
                novo[y] = e
        cur = novo
        n += 1
    return n
