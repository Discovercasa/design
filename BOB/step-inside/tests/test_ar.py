"""Step Inside Phase 7 tests: the AR budget rules and what is left out of the phone model.

    python -m unittest discover -s step-inside/tests        (from BOB/)
"""
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "ferramentas" / "ar"))
import ar  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
