"""Step Inside Phase 3 tests: re-import comparison rules and the export manifest schema.

    python -m unittest discover -s step-inside/tests        (from BOB/)
"""
import copy
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "ferramentas" / "fontes"))
sys.path.insert(0, str(AQUI.parent / "ferramentas" / "exportar"))
import comum  # noqa: E402
import esquema  # noqa: E402
import exportar  # noqa: E402

REF = {"objetos": 10, "triangulos": 1000, "caixa_min": [0, 0, 0], "caixa_max": [10, 6, 7], "dimensoes": [10, 6, 7],
       "materiais": ["MAT_WALL_RENDER__WHITE", "MAT_GLASS_CLEAR", "Etiqueta"], "imagens": 4}


def reimp(**mod):
    r = copy.deepcopy(REF)
    r.update({"imagens_em_falta": [], "imagem": {"diferenca_media": 0.0, "pixeis_diferentes": 0.0,
                                                 "silhueta_diferente": 0.0, "cobertura": 0.3}})
    r.update(mod)
    return r


class TestComparar(unittest.TestCase):
    def test_igual_passa(self):
        self.assertEqual(exportar.comparar(REF, reimp(), "glb"), ([], []))

    def test_geometria_perdida(self):
        self.assertTrue(exportar.comparar(REF, reimp(triangulos=900), "fbx")[0])

    def test_eixos_trocados(self):  # Y up read as Z up: the box turns
        f, _ = exportar.comparar(REF, reimp(caixa_max=[10, 7, 6], dimensoes=[10, 7, 6]), "usdz")
        self.assertIn("eixos", f[0])

    def test_escala_errada(self):  # centimetres read as metres
        self.assertTrue(exportar.comparar(REF, reimp(caixa_max=[1000, 600, 700]), "fbx")[0])

    def test_material_id_perdido(self):
        f, _ = exportar.comparar(REF, reimp(materiais=["MAT_WALL_RENDER__WHITE"]), "glb")
        self.assertIn("MAT_GLASS_CLEAR", f[0])  # labels and other non-catalogue names do not count

    def test_textura_em_falta(self):
        self.assertTrue(exportar.comparar(REF, reimp(imagens_em_falta=["X_Color.jpg"]), "fbx")[0])
        self.assertTrue(exportar.comparar(REF, reimp(imagens=0), "fbx")[0])

    def test_imagem(self):
        self.assertTrue(exportar.comparar(REF, reimp(imagem={"pixeis_diferentes": 0.0, "silhueta_diferente": 0.05}), "glb")[0])
        f, a = exportar.comparar(REF, reimp(imagem={"pixeis_diferentes": 0.2, "silhueta_diferente": 0.0}), "glb")
        self.assertEqual((f, len(a)), ([], 1))

    def test_nao_reabre(self):
        self.assertIn("não reabre", exportar.comparar(REF, {"erro": "boom"}, "usdz")[0][0])


class TestManifest(unittest.TestCase):
    M = {"project_id": "x", "version_id": "x-abc-202611090000", "source_blend_hash": "sha256:00", "export_timestamp": "t",
         "blender_version": "4.4.3", "unreal_target_version": "5.8", "unit_system": "m", "coordinate_system": {},
         "origin_transform": {}, "assets": [{"path": "x.glb", "type": "glb", "size_bytes": 1, "sha256": "00",
                                             "material_ids": ["MAT_GLASS_CLEAR"], "version": "abc", "purpose": "AR"}],
         "warnings": [], "validation_status": "PASS", "terrain_source": None}

    def esq(self):
        return comum.ler_json(exportar.ESQUEMA_MANIFEST)

    def test_valido(self):
        self.assertEqual(esquema.validar(self.M, self.esq()), [])

    def test_campos_da_especificacao(self):  # spec §4.3: every field is required
        for k in ("source_blend_hash", "assets", "validation_status", "terrain_source"):
            m = copy.deepcopy(self.M)
            del m[k]
            self.assertTrue(esquema.validar(m, self.esq()), k)

    def test_estado_e_tipo_validos(self):
        m = copy.deepcopy(self.M)
        m["validation_status"] = "OK"
        m["assets"][0]["type"] = "obj"
        self.assertEqual(len(esquema.validar(m, self.esq())), 2)


if __name__ == "__main__":
    unittest.main()
