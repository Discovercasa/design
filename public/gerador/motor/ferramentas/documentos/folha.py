"""Sheet layout of the DiscoverCasa production documents (as the company's D2503 sheets): A3 landscape with the
title block on the right (legend, revisions, project, sheet title, obra, scale, logo), dimension chains in red,
tables. Paper units mm, origin bottom-left."""
from ferramentas.documentos.pdf import hexcor, largura

VERMELHO = hexcor("#E0161B")      # dimensions (D2503)
AZUL = hexcor("#3446A0")          # module labels, lameladas A
VERDE = hexcor("#2E9B3A")         # interior modules, lameladas B
MAGENTA = hexcor("#E5007E")       # amarrações, madres
CASTANHO = hexcor("#8A5A2B")      # modules (frames)
CINZA = hexcor("#9A9A9A")
CINZA_CLARO = hexcor("#D9D9D9")
PRETO = (0, 0, 0)
AMARELO_DC = hexcor("#F2B705")    # DISCOVER (logo)
ESCURO_DC = hexcor("#3C3C3B")     # CASA (logo)
CORES_TIPO = [AZUL, VERDE, hexcor("#E07B00"), hexcor("#7A3DB8")]

A3 = (420.0, 297.0)
A4 = (210.0, 297.0)
CONTEUDO = (10.0, 10.0, 350.0, 287.0)  # x0, y0, x1, y1 of the drawing area on A3


def fmt(v, casas=2):
    """0.915 -> '0,92'; 17.5 -> '17,5' (as the company's drawings)."""
    s = f"{v:.{casas}f}".rstrip("0").rstrip(".")
    return (s if s not in ("", "-0") else "0").replace(".", ",")


def seccao(sec):
    """'110x35' -> '11x3,5' (cm, as in the company's tables)."""
    try:
        a, b = sec.lower().split("x")
        return f"{fmt(float(a) / 10, 1)}x{fmt(float(b) / 10, 1)}"
    except ValueError:
        return sec


class Vista:
    """World metres -> paper mm at 1:escala, with (wx0, wy0) at paper (px0, py0)."""

    def __init__(self, px0, py0, escala, wx0=0.0, wy0=0.0, espelho=False):
        self.px0, self.py0, self.k, self.wx0, self.wy0, self.espelho = px0, py0, 1000.0 / escala, wx0, wy0, espelho
        self.escala = escala

    def p(self, x, y):
        dx = (x - self.wx0) * self.k
        return (self.px0 - dx if self.espelho else self.px0 + dx), self.py0 + (y - self.wy0) * self.k

    def d(self, v):
        return v * self.k


def escala_para(largura_m, altura_m, larg_mm, alt_mm, escalas=(20, 25, 50, 75, 100, 125, 150, 200)):
    for e in escalas:
        if largura_m * 1000 / e <= larg_mm and altura_m * 1000 / e <= alt_mm:
            return e
    return escalas[-1]


def cota_h(pg, xs, y_obj, y_linha, valores=None, tam=2.0, cor=VERMELHO, ext=True):
    """Horizontal dimension chain through paper xs at height y_linha (extension lines from y_obj)."""
    xs = list(xs)
    if len(xs) < 2:
        return
    pg.linha(xs[0], y_linha, xs[-1], y_linha, 0.13, cor)
    for i, x in enumerate(xs):
        if ext:
            pg.linha(x, y_obj, x, y_linha + (1.2 if y_linha > y_obj else -1.2), 0.1, cor)
        pg.linha(x - 0.8, y_linha - 0.8, x + 0.8, y_linha + 0.8, 0.25, cor)
    for i, (a, b) in enumerate(zip(xs, xs[1:])):
        txt = valores[i] if valores else ""
        if txt:
            w = largura(txt, tam)
            if w < abs(b - a) - 0.6:
                pg.texto((a + b) / 2, y_linha + 0.8, txt, tam, cor, alinh="c")
            else:  # no room: above, staggered
                pg.texto((a + b) / 2, y_linha + 0.8 + (tam + 0.6) * (i % 2), txt, tam * 0.85, cor, alinh="c")


def cota_v(pg, ys, x_obj, x_linha, valores=None, tam=2.0, cor=VERMELHO, ext=True):
    ys = list(ys)
    if len(ys) < 2:
        return
    pg.linha(x_linha, ys[0], x_linha, ys[-1], 0.13, cor)
    for y in ys:
        if ext:
            pg.linha(x_obj, y, x_linha + (1.2 if x_linha > x_obj else -1.2), y, 0.1, cor)
        pg.linha(x_linha - 0.8, y - 0.8, x_linha + 0.8, y + 0.8, 0.25, cor)
    for i, (a, b) in enumerate(zip(ys, ys[1:])):
        txt = valores[i] if valores else ""
        if txt:
            w = largura(txt, tam)
            off = -0.8 if w < abs(b - a) - 0.6 else -0.8 - (tam + 0.6) * (i % 2)
            pg.texto(x_linha + off, (a + b) / 2, txt, tam if off == -0.8 else tam * 0.85, cor, alinh="c", ang=90)


def logo(pg, x, y, tam=5.5):
    """DISCOVERCASA (DISCOVER in the company yellow, CASA dark), letter-spaced, starting at x."""
    for palavra, cor in (("DISCOVER", AMARELO_DC), ("CASA", ESCURO_DC)):
        for c in palavra:
            pg.texto(x, y, c, tam, cor, negrito=True)
            x += largura(c, tam, True) + tam * 0.12
    return x


def folha(pdf, info, titulo, n, total, escala=None, legenda=(), notas=()):
    """A3 sheet with the frame and the right-hand title block. info: obra, projeto, local, data, revisoes.
    legenda: (kind, colour, text) with kind 'linha' / 'ret' / 'trac' / 'texto'. Returns the page."""
    pg = pdf.pagina(*A3)
    pg.ret(5, 5, 410, 287, esp=0.25, cor=PRETO)
    x0, x1 = 356.0, 410.0
    pg.linha(x0, 5, x0, 292, 0.25, PRETO)
    # legend (top)
    y = 284.0
    if legenda:
        pg.texto(x0 + 2, y, "LEGENDA", 2.2, PRETO, negrito=True)
        y -= 5.0
        for tipo, cor, txt in legenda:
            if tipo == "linha":
                pg.linha(x0 + 2, y + 0.8, x0 + 9, y + 0.8, 0.35, cor)
            elif tipo == "trac":
                pg.ret(x0 + 2, y - 0.2, 7, 2.2, esp=0.2, cor=cor)
                pg.tracejar([(x0 + 2, y - 0.2), (x0 + 9, y - 0.2), (x0 + 9, y + 2.0), (x0 + 2, y + 2.0)], 0.8, 45, 0.1, cor)
            elif tipo == "ret":
                pg.ret(x0 + 2, y - 0.2, 7, 2.2, esp=0.2, cor=cor, preench=tuple(min(1, c * 0.25 + 0.75) for c in cor))
            elif tipo == "cota":
                pg.linha(x0 + 2, y + 0.8, x0 + 9, y + 0.8, 0.13, cor)
                for xx in (x0 + 2, x0 + 9):
                    pg.linha(xx - 0.6, y + 0.2, xx + 0.6, y + 1.4, 0.25, cor)
            for k, parte in enumerate(_quebrar(txt, 2.0, x1 - x0 - 14)):
                pg.texto(x0 + 11, y - k * 2.8, parte, 2.0, cor if tipo != "linha" or cor != CINZA_CLARO else CINZA)
            y -= 2.8 * len(_quebrar(txt, 2.0, x1 - x0 - 14)) + 1.6
    if notas:
        y -= 3.0
        pg.texto(x0 + 2, y, "NOTAS", 2.2, PRETO, negrito=True)
        y -= 4.2
        for nota in notas:
            for parte in _quebrar(nota, 1.8, x1 - x0 - 4):
                pg.texto(x0 + 2, y, parte, 1.8, ESCURO_DC)
                y -= 2.5
            y -= 0.8
    # revisions
    yb = 118.0
    pg.linha(x0, yb, x1, yb, 0.2, PRETO)
    pg.texto(x0 + 2, yb - 4, "REVISÕES", 2.0, PRETO, negrito=True)
    yy = yb - 8
    for rev, data, txt in (info.get("revisoes") or [])[-4:]:
        pg.texto(x0 + 2, yy, rev, 1.8)
        pg.texto(x0 + 6, yy, data, 1.8)
        for parte in _quebrar(txt, 1.8, x1 - x0 - 24)[:2]:
            pg.texto(x0 + 20, yy, parte, 1.8)
            yy -= 2.5
        yy -= 0.8
    # project and sheet
    yp = 80.0
    pg.linha(x0, yp, x1, yp, 0.2, PRETO)
    pg.texto(x0 + 2, yp - 5, info.get("projeto", ""), 2.8, PRETO, negrito=True)
    for k, parte in enumerate(_quebrar(info.get("local", ""), 1.9, x1 - x0 - 4)[:2]):
        pg.texto(x0 + 2, yp - 9 - k * 2.6, parte, 1.9, ESCURO_DC)
    pg.linha(x0, yp - 16, x1, yp - 16, 0.15, CINZA)
    for k, parte in enumerate(_quebrar(titulo, 2.6, x1 - x0 - 4)[:3]):
        pg.texto(x0 + 2, yp - 21 - k * 3.4, parte, 2.6, PRETO, negrito=True)
    pg.linha(x0, yp - 32, x1, yp - 32, 0.15, CINZA)
    pg.texto(x0 + 2, yp - 37, "Obra", 1.9, ESCURO_DC)
    pg.texto(x0 + 14, yp - 37, info.get("obra", ""), 2.4, PRETO, negrito=True)
    pg.texto(x1 - 2, yp - 37, f"Folha {n}/{total}", 1.9, ESCURO_DC, alinh="d")
    pg.texto(x0 + 2, yp - 42, "Escala", 1.9, ESCURO_DC)
    pg.texto(x0 + 14, yp - 42, f"1:{escala}" if escala else "Sem escala", 2.2, PRETO)
    pg.texto(x1 - 2, yp - 42, info.get("data", ""), 1.9, ESCURO_DC, alinh="d")
    pg.texto(x0 + 2, yp - 47, info.get("origem", ""), 1.5, CINZA)
    # logo
    pg.linha(x0, 22, x1, 22, 0.2, PRETO)
    xl = logo(pg, x0 + 3, 13, 5.2)
    pg.texto(x0 + 3, 8.5, "discovercasa.pt", 1.8, ESCURO_DC)
    del xl
    return pg


def _quebrar(txt, tam, larg):
    palavras, linhas, cur = str(txt).split(), [], ""
    for p in palavras:
        t = (cur + " " + p).strip()
        if largura(t, tam) <= larg or not cur:
            cur = t
        else:
            linhas.append(cur)
            cur = p
    if cur:
        linhas.append(cur)
    return linhas or [""]


class Tabela:
    """Table flowing in columns over the sheets: colunas = [(title, width mm, align)], linhas of strings;
    rows starting with '#' are section headings."""

    def __init__(self, titulo, colunas, linhas, tam=2.0, alt=3.6):
        self.titulo, self.colunas, self.linhas, self.tam, self.alt = titulo, colunas, linhas, tam, alt

    def largura(self):
        return sum(c[1] for c in self.colunas)

    def desenhar(self, pg, x, y_topo, y_min, inicio=0):
        """Draws from row `inicio` down to y_min; returns the next row index (len when done)."""
        pg.texto(x, y_topo, self.titulo, 2.4, PRETO, negrito=True)
        y = y_topo - 5.0
        cx = x
        for t, w, _a in self.colunas:
            pg.texto(cx + 0.8, y, t, self.tam, PRETO, negrito=True)
            cx += w
        pg.linha(x, y - 1.2, x + self.largura(), y - 1.2, 0.25, PRETO)
        y -= self.alt + 0.6
        i = inicio
        while i < len(self.linhas) and y > y_min:
            ln = self.linhas[i]
            if isinstance(ln, str):  # heading
                y -= 0.8
                pg.texto(x + 0.8, y, ln.lstrip("#").strip(), self.tam, ESCURO_DC, negrito=True)
                y -= self.alt
                i += 1
                continue
            cx = x
            negrito = bool(ln and str(ln[0]).startswith("Total"))
            for (t, w, a), v in zip(self.colunas, ln):
                v = str(v)
                while v and largura(v, self.tam, negrito) > w - 1.4:
                    v = v[:-1]
                if a == "d":
                    pg.texto(cx + w - 0.8, y, v, self.tam, PRETO, negrito=negrito, alinh="d")
                elif a == "c":
                    pg.texto(cx + w / 2, y, v, self.tam, PRETO, negrito=negrito, alinh="c")
                else:
                    pg.texto(cx + 0.8, y, v, self.tam, PRETO, negrito=negrito)
                cx += w
            pg.linha(x, y - 1.1, x + self.largura(), y - 1.1, 0.08, CINZA_CLARO)
            y -= self.alt
            i += 1
        return i
