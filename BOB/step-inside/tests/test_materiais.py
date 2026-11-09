"""Step Inside Phase 3 tests: the common material catalogue and the per-builder mappings.

    python -m unittest discover -s step-inside/tests        (from BOB/)
"""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas" / "materiais"))
import materiais  # noqa: E402


class TestCatalogo(unittest.TestCase):
    def setUp(self):
        self.cat, self.mp = materiais.ler("discovercasa")

    def test_catalogo_e_mapeamento_validos(self):
        self.assertEqual(materiais.validar(self.cat, self.mp), [])

    def test_ids_estaveis_e_independentes_do_construtor(self):
        for m in self.cat["materiais"]:
            self.assertRegex(m["id"], r"^MAT_[A-Z0-9_]+$")
            self.assertNotIn("DISCOVERCASA", m["id"])  # the catalogue serves any builder

    def test_variante_por_cima_do_mestre(self):
        t = materiais.resolver(self.cat, self.mp)
        e = t["Alumínio RAL 7016"]
        self.assertEqual((e["id"], e["mestre"], e["variante"]), ("MAT_FRAME_ALUMINIUM__RAL7016", "MAT_FRAME_ALUMINIUM", "RAL7016"))
        self.assertEqual(e["pbr"]["base_color"], "#383E42")
        self.assertEqual(e["pbr"]["metallic"], 0.5)  # from the variant
        self.assertEqual(t["MAT_GLASS_CLEAR"]["id"], "MAT_GLASS_CLEAR")  # catalogue ids map to themselves

    def test_provisorio_ate_lista_oficial(self):
        t = materiais.resolver(self.cat, self.mp)
        self.assertEqual({t[k]["estado"] for k in self.mp["materiais"]}, {"INFERRED"})

    def test_erros_detetados(self):
        cat = copy.deepcopy(self.cat)
        cat["materiais"].append(dict(cat["materiais"][0]))  # repeated id
        cat["materiais"].append({"id": "mat_bad", "categoria": "xpto", "nome": {}, "pbr": {"base_color": "red"}})
        mp = copy.deepcopy(self.mp)
        mp["materiais"]["Produto X"] = {"mat": "MAT_DOES_NOT_EXIST"}
        mp["materiais"]["Produto Y"] = {"mat": "MAT_FRAME_ALUMINIUM__PINK"}
        erros = " | ".join(materiais.validar(cat, mp))
        for frag in ("id repetido", "id inválido", "categoria", "#RRGGBB", "não existe no catálogo", "variante não existe"):
            self.assertIn(frag, erros)


if __name__ == "__main__":
    unittest.main()
