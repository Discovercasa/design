"""Interiors (hub task 167): the common catalogue and every project's layout, without Blender.

The footprint of each piece (catalogue size, turned to where its front faces) must sit inside its room, and the
pieces that stand on the floor must not overlap (chairs tucked under a table excepted), so a layout error shows up
before the Blender run.
"""
import json
import math
import unittest
from pathlib import Path

BOB = Path(__file__).resolve().parents[2]
CATALOGO = BOB / "interiores" / "catalogo.json"
PROJETOS = BOB / "step-inside" / "projetos-teste"
JUNTOS = {("OBJ_DINING_TABLE", "OBJ_DINING_CHAIR"), ("OBJ_TV_UNIT", "OBJ_TV"), ("OBJ_COFFEE_TABLE", "OBJ_PLANT_SMALL")}


def angulo(frente):
    if isinstance(frente, str):
        return math.radians({"S": 0, "E": 90, "N": 180, "W": 270}[frente.upper()])
    return math.radians(float(frente))


def pegada(p, o):
    """Corners of the footprint in the house frame."""
    w, d = (p.get("medidas") or o["medidas_m"])[:2]
    a = angulo(p.get("frente", "S"))
    c, s = math.cos(a), math.sin(a)
    x, y = p["xy"]
    return [(x + c * u - s * v, y + s * u + c * v) for u in (-w / 2, w / 2) for v in (-d / 2, d / 2)]


def _separados(A, B):
    """Separating axis test for two convex quads (corners in any order: use their edges from the convex hull)."""
    def casco(P):
        P = sorted(P)
        def cr(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        lo, hi = [], []
        for q in P:
            while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0:
                lo.pop()
            lo.append(q)
        for q in reversed(P):
            while len(hi) >= 2 and cr(hi[-2], hi[-1], q) <= 0:
                hi.pop()
            hi.append(q)
        return lo[:-1] + hi[:-1]
    A, B = casco(A), casco(B)
    for P in (A, B):
        for i in range(len(P)):
            ex, ey = P[(i + 1) % len(P)][0] - P[i][0], P[(i + 1) % len(P)][1] - P[i][1]
            n = (-ey, ex)
            pa = [n[0] * q[0] + n[1] * q[1] for q in A]
            pb = [n[0] * q[0] + n[1] * q[1] for q in B]
            folga = 0.01 * math.hypot(*n)
            if max(pa) <= min(pb) + folga or max(pb) <= min(pa) + folga:
                return True
    return False


class TestInteriores(unittest.TestCase):
    def setUp(self):
        self.cat = json.loads(CATALOGO.read_text(encoding="utf-8"))
        self.obj = {o["id"]: o for o in self.cat["objetos"]}
        self.disp = sorted(PROJETOS.glob("*/interiores.json"))

    def test_catalogo(self):
        ids = [o["id"] for o in self.cat["objetos"]]
        self.assertEqual(len(ids), len(set(ids)), "ids repetidos no catálogo")
        for o in self.cat["objetos"]:
            self.assertIn(o["divisao"], self.cat["divisoes"], o["id"])
            self.assertEqual(len(o["medidas_m"]), 3, o["id"])
            self.assertTrue(all(v > 0 for v in o["medidas_m"]), o["id"])
            self.assertGreater(o.get("ar_tris", 0), 0, o["id"])
            t = o["origem"]["tipo"]
            self.assertIn(t, ("polyhaven", "parametrico"), o["id"])
            if t == "polyhaven":
                self.assertTrue(o["origem"].get("asset"), o["id"])
            else:
                self.assertIn(o["origem"]["gerador"], ("cozinha", "ilha", "coluna", "mesa", "cama", "roupeiro", "sanita",
                                                       "lavatorio", "duche", "tv"), o["id"])

    def test_ha_uma_disposicao(self):
        self.assertTrue(self.disp, "nenhum projetos-teste/*/interiores.json")

    def test_pecas_dentro_das_divisoes_e_sem_choques(self):
        for f in self.disp:
            d = json.loads(f.read_text(encoding="utf-8"))
            with self.subTest(obra=d["obra"]):
                ids = [p["id"] for p in d["pecas"]]
                self.assertEqual(len(ids), len(set(ids)))
                chao = []
                for p in d["pecas"]:
                    self.assertIn(p["obj"], self.obj, p["id"])
                    self.assertIn(p["divisao"], d["divisoes"], p["id"])
                    x0, y0, x1, y1 = d["divisoes"][p["divisao"]]["caixa"]
                    for x, y in pegada(p, self.obj[p["obj"]]):
                        self.assertTrue(x0 - 0.02 <= x <= x1 + 0.02 and y0 - 0.02 <= y <= y1 + 0.02,
                                        f"{p['id']} sai da divisão {p['divisao']} ({x:.2f}, {y:.2f})")
                    if not p.get("teto") and not p.get("z"):
                        chao.append(p)
                for i, a in enumerate(chao):
                    for b in chao[i + 1:]:
                        par = (self.obj[a["obj"]]["id"], self.obj[b["obj"]]["id"])
                        if par in JUNTOS or par[::-1] in JUNTOS:
                            continue
                        self.assertTrue(_separados(pegada(a, self.obj[a["obj"]]), pegada(b, self.obj[b["obj"]])),
                                        f"{a['id']} e {b['id']} sobrepõem-se")

    def test_vistas(self):
        for f in self.disp:
            d = json.loads(f.read_text(encoding="utf-8"))
            for v in d.get("vistas", []):
                self.assertEqual(len(v["de"]), 3, v["id"])
                self.assertEqual(len(v["para"]), 3, v["id"])


if __name__ == "__main__":
    unittest.main()
