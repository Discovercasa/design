"""Step Inside Phase 7 tests: the AR budget rules and what is left out of the phone model.

    python -m unittest discover -s step-inside/tests        (from BOB/)
"""
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "ferramentas" / "ar"))
import ar  # noqa: E402
import maquete  # noqa: E402


def var(**mod):
    v = {"variante": "casa", "triangulos": 20000, "textura_maior": 1024, "dimensoes": [10.0, 6.0, 7.0], "z_min": -0.2}
    v.update(mod)
    return v


FICH = {"glb": {"bytes": 2_500_000}, "usdz": {"bytes": 2_000_000}}


def reimp(t=20000, dims=(10.0, 6.0, 7.0)):
    return {f: {"triangulos": t, "dimensoes": list(dims), "imagens_em_falta": []} for f in ("glb", "usdz")}


class TestOrcamento(unittest.TestCase):
    def test_dentro_do_orcamento(self):
        self.assertEqual(ar.avaliar(var(), FICH, reimp()), ([], []))

    def test_triangulos(self):
        self.assertEqual(len(ar.avaliar(var(triangulos=70000), FICH, reimp(70000))[1]), 1)   # above the ideal: warning
        self.assertTrue(ar.avaliar(var(triangulos=150000), FICH, reimp(150000))[0])         # above the maximum: fail

    def test_tamanho(self):
        grande = {"glb": {"bytes": 14_000_000}, "usdz": {"bytes": 30_000_000}}
        f, a = ar.avaliar(var(), grande, reimp())
        self.assertEqual((len(f), len(a)), (1, 1))

    def test_textura_acima_de_2048(self):
        self.assertTrue(ar.avaliar(var(textura_maior=4096), FICH, reimp())[0])

    def test_casa_a_flutuar(self):  # the phone sets the lowest point on the ground
        self.assertIn("flutuar", ar.avaliar(var(z_min=-1.0), FICH, reimp())[0][0])
        self.assertEqual(ar.avaliar(var(variante="maquete", z_min=-3.0), FICH, reimp())[0], [])
        # one storey at 1:1 (houses of two or more storeys, 2026-11-09): the same rule, by its base variant
        self.assertIn("flutuar", ar.avaliar(var(variante="casa_piso1", base="casa", piso=1, z_min=-3.2), FICH, reimp())[0][0])
        self.assertEqual(ar.avaliar(var(variante="casa_piso1", base="casa", piso=1), FICH, reimp())[0], [])
        self.assertEqual(ar.avaliar(var(variante="maquete_piso1", base="maquete", piso=1, z_min=-3.0), FICH, reimp())[0], [])

    def test_reabrir_com_escala_errada(self):
        self.assertTrue(ar.avaliar(var(), FICH, reimp(dims=(10.0, 7.0, 6.0)))[0])


class TestOcultos(unittest.TestCase):
    def test_camadas_escondidas_fora_do_ar(self):
        oc = set(ar.ocultos("discovercasa"))
        for m in ("MAT_BOARD_OSB", "MAT_INSULATION_MINERAL_WOOL", "MAT_TIMBER_STRUCTURE"):
            self.assertIn(m, oc)
        self.assertNotIn("MAT_TIMBER_STRUCTURE__GLULAM", oc)  # the pergola's timber is seen
        # behind the cladding (without it the AR showed the interior through small gaps between cladding pieces,
        # user 2026-11-09: "pequenos gaps no tremolo") and on parapet tops
        self.assertNotIn("MAT_MEMBRANE_BREATHER", oc)
        self.assertNotIn("MAT_MEMBRANE_BREATHER__DARK", oc)
        self.assertNotIn("MAT_WALL_RENDER__WHITE", oc)


def ret_tris(x0, y0, x1, y1):
    """A plan rectangle of terrain as two triangles."""
    return [((x0, y0), (x1, y0), (x1, y1)), ((x0, y0), (x1, y1), (x0, y1))]


CASA = (-5.0, -4.0, 5.0, 4.0)


class TestMaquete(unittest.TestCase):
    """The table model's clean edge (task 157): the largest covered rectangle around the house, cut straight."""

    def test_terreno_largo_corta_no_raio(self):
        self.assertEqual(maquete.retangulo(ret_tris(-40, -40, 40, 40), CASA, 20), (-25.0, -24.0, 25.0, 24.0))

    def test_levantamento_curto_de_um_lado(self):
        # the survey stops 8 m left of the house: the block stops there, the other sides keep the full radius
        self.assertEqual(maquete.retangulo(ret_tris(-13, -40, 40, 40), CASA, 20), (-13.0, -24.0, 25.0, 24.0))

    def test_buraco_debaixo_da_casa(self):
        # the terrain may be a hole under the house (the house stands in it)
        tris = ret_tris(-30, -30, 30, -4) + ret_tris(-30, 4, 30, 30) + ret_tris(-30, -4, -5, 4) + ret_tris(5, -4, 30, 4)
        self.assertEqual(maquete.retangulo(tris, CASA, 10), (-15.0, -14.0, 15.0, 14.0))

    def test_canto_em_falta(self):
        # an L-shaped survey (no ground beyond x 12 for y > 6): no notch, the larger of the two clean rectangles
        tris = ret_tris(-30, -30, 30, 6) + ret_tris(-30, 6, 12, 30)
        x0, y0, x1, y1 = maquete.retangulo(tris, CASA, 20)
        area = (x1 - x0) * (y1 - y0)
        self.assertTrue(x1 <= 12 or y1 <= 6)
        self.assertEqual(area, max(37 * 48, 50 * 30))  # (-25..12) × (-24..24) vs (-25..25) × (-24..6)

    def test_sem_terreno_junto_da_casa(self):
        self.assertIsNone(maquete.retangulo(ret_tris(10, 10, 40, 40), CASA, 20))

    def test_saia_fecha_os_lados_para_fora(self):
        ret = (-10.0, -8.0, 10.0, 8.0)
        arestas = [((-10.0, -2.0, 1.0), (-10.0, 3.0, 1.2)),   # on the left side
                   ((2.0, 8.0, 0.5), (6.0, 8.0, 0.4)),        # on the far side
                   ((1.0, 1.0, 0.0), (2.0, 2.0, 0.0))]        # inside (the hole around the house): no face
        quads, fundo = maquete.saia(arestas, ret, -1.5)
        self.assertEqual(len(quads), 2)

        def normal(q):
            a, b, c = q[0], q[1], q[2]
            e1, e2 = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
            return (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
        self.assertLess(normal(quads[0])[0], 0)     # left side faces -x
        self.assertGreater(normal(quads[1])[1], 0)  # far side faces +y
        self.assertTrue(all(p[2] == -1.5 for q in quads for p in q[2:]) or all(p[2] == -1.5 for q in quads for p in q[:2]))
        self.assertLess(normal(fundo)[2], 0)        # the bottom faces down


if __name__ == "__main__":
    unittest.main()
