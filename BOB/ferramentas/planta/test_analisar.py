"""Plan analysis on synthetic drawings with a known answer (no files): any colour, any wall style, any angle.

    python -m unittest ferramentas/planta/test_analisar.py      (from BOB/)

A 10 x 8 m house (outside walls 0,30, one inside wall 0,12 with a door, a window in the south wall), drawn at 1:100
on the sheet in several styles: poché, diagonal hatching, two lines only, black and grey only (no red anywhere),
with furniture, a dimension chain, text-like marks and floor stipple around; and the same house turned 30 degrees.
"""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.planta import analisar as A  # noqa: E402

ESC = 100            # 1:100 -> 1 m = 10 sheet mm
OX, OY = 50.0, 150.0  # sheet mm of the house's SW outer corner (sheet y down)


def _sheet(x, y, rot=0.0):
    """Model metres (y up, origin the house's SW outer corner) -> sheet mm (y down), turned by rot degrees."""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    xr, yr = x * c - y * s, x * s + y * c
    return (OX + xr * 1000 / ESC, OY - yr * 1000 / ESC)


def _faixa(x0, y0, x1, y1, esp, lado=0):
    """The rectangle of a wall from (x0,y0) to (x1,y1) (axis-aligned) of thickness esp."""
    if y0 == y1:
        return [(x0, y0 - esp / 2), (x1, y0 - esp / 2), (x1, y0 + esp / 2), (x0, y0 + esp / 2)]
    return [(x0 - esp / 2, y0), (x0 + esp / 2, y0), (x0 + esp / 2, y1), (x0 - esp / 2, y1)]


def casa(estilo="poche", rot=0.0, cor="#000000"):
    """Paths of the test house. Walls as centre lines with openings cut: [(x0, y0, x1, y1, esp)]."""
    E, I = 0.30, 0.12
    h = E / 2
    paredes = [
        (0, h, 4.0, h, E), (5.2, h, 10, h, E),            # south: window 4,0–5,2 m
        (0, 8 - h, 10, 8 - h, E),                         # north
        (h, h, h, 8 - h, E), (10 - h, h, 10 - h, 8 - h, E),  # west, east
        (6.0, E, 6.0, 3.0, I), (6.0, 3.9, 6.0, 8 - E, I),     # inside, door 3,0–3,9 m
    ]
    P = []

    def linha(pts, cor_=cor, sw=0.25):
        P.append({"fill": None, "stroke": cor_, "sw": sw, "subs": [([_sheet(x, y, rot) for x, y in pts], False)]})

    def cheio(pts, cor_="#808080"):
        P.append({"fill": cor_, "stroke": None, "sw": 0, "subs": [([_sheet(x, y, rot) for x, y in pts] + [_sheet(*pts[0], rot)], True)]})

    for x0, y0, x1, y1, esp in paredes:
        q = _faixa(x0, y0, x1, y1, esp)
        if y0 == y1:   # faces
            linha([(x0, y0 - esp / 2), (x1, y0 - esp / 2)])
            linha([(x0, y0 + esp / 2), (x1, y0 + esp / 2)])
        else:
            linha([(x0 - esp / 2, y0), (x0 - esp / 2, y1)])
            linha([(x0 + esp / 2, y0), (x0 + esp / 2, y1)])
        if estilo == "poche":
            cheio(q)
        elif estilo == "tracejado":   # 45 degree hatching every 4 cm across the band
            L = max(abs(x1 - x0), abs(y1 - y0))
            k = 0.0
            while k < L:            # clipped to the wall piece, up to its ends (as drawn: the hatching fills the wall)
                f = min(1.0, (L - k) / esp)
                if y0 == y1:
                    linha([(x0 + k, y0 - esp / 2), (x0 + k + esp * f, y0 - esp / 2 + esp * f)], "#909090", 0.0)
                else:
                    linha([(x0 - esp / 2, y0 + k), (x0 - esp / 2 + esp * f, y0 + k + esp * f)], "#909090", 0.0)
                k += 0.04
    # jambs
    for x in (4.0, 5.2):
        linha([(x, 0), (x, E)])
    for y in (3.0, 3.9):
        linha([(6.0 - I / 2, y), (6.0 + I / 2, y)])
    # window: two glazing lines inside the south wall
    for yy in (0.13, 0.17):
        linha([(4.0, yy), (5.2, yy)], "#606060", 0.1)
    # door: leaf and swing (quarter circle centred on the jamb)
    linha([(6.0 + I / 2, 3.0), (6.0 + I / 2 + 0.9, 3.0)])
    linha([(6.0 + I / 2 + 0.9 * math.cos(math.radians(a)), 3.0 + 0.9 * math.sin(math.radians(a))) for a in range(0, 91, 5)],
          "#606060", 0.1)
    # the entrance door's swing (east wall, 4,0–4,9 m; the wall itself is drawn closed: a second arc for the scale)
    linha([(10 - E + 0.9 * math.cos(math.radians(a)) * -1, 4.0 + 0.9 * math.sin(math.radians(a))) for a in range(0, 91, 5)],
          "#606060", 0.1)
    # distractors: furniture (a bed, a table), a dimension chain under the house, text-like marks, floor stipple
    linha([(1.0, 1.0), (2.6, 1.0), (2.6, 3.0), (1.0, 3.0), (1.0, 1.0)])
    linha([(7.0, 5.0), (8.6, 5.0), (8.6, 5.9), (7.0, 5.9), (7.0, 5.0)])
    linha([(0, -0.8), (10, -0.8)])
    for x in (0, 4.0, 5.2, 10):
        linha([(x, -0.9), (x, -0.5)])
    for k in range(6):
        linha([(2.0 + 0.1 * k, 6.0), (2.05 + 0.1 * k, 6.1), (2.1 + 0.1 * k, 6.0)])
    for i in range(40):
        for j in range(30):
            x, y = 0.4 + i * 0.23, 0.4 + j * 0.24
            if x < 9.6 and y < 7.6:
                linha([(x, y), (x + 0.02, y)], "#A0A0A0", 0.0)
    return P


REGIAO = (OX - 15, OY - 95, OX + 115, OY + 15)


class TestAnalisar(unittest.TestCase):
    def verifica(self, doc, nome):
        self.assertIsNotNone(doc, nome)
        ps = doc["paredes"]
        ext = [p for p in ps if p["exterior"]]
        cont = (doc.get("eixos") or doc)["contorno"]    # in the house's own axes (a turned house's box is bigger)
        L, D = cont[1], cont[3]
        self.assertAlmostEqual(max(L, D), 10.0, delta=0.1, msg=f"{nome}: {L} x {D}")
        self.assertAlmostEqual(min(L, D), 8.0, delta=0.1, msg=f"{nome}: {L} x {D}")
        self.assertGreaterEqual(len(ext), 4, nome)
        for p in ext:
            self.assertAlmostEqual(p["espessura"], 0.30, delta=0.04, msg=nome)
        dentro = [p for p in ps if not p["exterior"]]
        self.assertTrue(any(abs(p["espessura"] - 0.12) <= 0.03 for p in dentro), f"{nome}: inside wall")
        tipos = sorted((o["tipo"], round(o["t1"] - o["t0"], 2)) for p in ps for o in p["aberturas"])
        # windows in hatched walls are measured where the hatching stops: ±0,2 m for now
        tol = 0.25 if nome == "tracejado" else 0.06
        self.assertTrue(any(t_ == "janela" and abs(l_ - 1.2) <= tol for t_, l_ in tipos), f"{nome}: {tipos}")
        self.assertTrue(any(t_ == "porta" and abs(l_ - 0.9) <= 0.06 for t_, l_ in tipos), f"{nome}: {tipos}")
        areas = sorted(d["area"] for d in doc["divisoes"])
        self.assertEqual(len(areas), 2, f"{nome}: {areas}")
        self.assertAlmostEqual(sum(areas), (10 - 0.6) * (8 - 0.6) - 0.12 * (8 - 0.6), delta=2.5, msg=nome)

    def test_estilos_de_parede(self):
        for estilo in ("poche", "tracejado", "duas_linhas"):
            with self.subTest(estilo=estilo):
                self.verifica(A.analisar(casa(estilo), REGIAO, ESC), estilo)

    def test_sem_vermelho_cinzento(self):
        self.verifica(A.analisar(casa("poche", cor="#7F7F7F"), REGIAO, ESC), "cinzento")

    def test_rodada_30_graus(self):
        reg = (OX - 60, OY - 120, OX + 110, OY + 15)
        doc = A.analisar(casa("poche", rot=30), reg, ESC)
        self.verifica(doc, "rodada")
        self.assertIsNotNone(doc.get("eixos"))
        self.assertAlmostEqual(doc["eixos"]["rotacao_graus"] % 90, 30, delta=1)

    def test_escala_deduzida(self):
        doc = A.melhor(casa("poche"), REGIAO, esp_mm=3.0)
        self.assertIsNotNone(doc)
        self.assertEqual(doc["escala"], ESC)

    def test_formato_em_eixos(self):
        e = A.analisar(casa("poche"), REGIAO, ESC)["eixos"]
        self.assertEqual({p["eixo"] for p in e["paredes"]}, {"x", "y"})
        ext = [p for p in e["paredes"] if p["exterior"]]
        self.assertTrue(all(p["lado_exterior"] in (1, -1) for p in ext))
        # the south wall: outside below it (-c side)
        sul = min((p for p in ext if p["eixo"] == "x"), key=lambda p: p["c"])
        self.assertEqual(sul["lado_exterior"], -1)


if __name__ == "__main__":
    unittest.main()
