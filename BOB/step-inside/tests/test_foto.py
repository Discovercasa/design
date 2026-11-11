"""Photo -> texture (Step Inside Phase 3, task 156): the maps the visit model reads and the builder's mapping entry."""
import json
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

BOB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BOB / "step-inside" / "ferramentas" / "materiais"))
import foto  # noqa: E402

encontrar_blender = foto.comum.encontrar_blender


def png(caminho, w, h):
    """Vertical boards: brown stripes with dark joints every 40 px."""
    linhas = b""
    for _y in range(h):
        linha = bytearray([0])
        for x in range(w):
            junta = x % 40 < 3
            linha += bytes((40, 25, 15) if junta else (160 + (x * 7) % 30, 100, 60))
        linhas += bytes(linha)
    def bloco(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    caminho.write_bytes(b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                        + bloco(b"IDAT", zlib.compress(linhas)) + bloco(b"IEND", b""))


@unittest.skipUnless(encontrar_blender(), "precisa do Blender")
class TestFoto(unittest.TestCase):
    def test_foto_vira_textura_do_produto(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            png(t / "forro.png", 480, 320)
            mp = t / "discovercasa.json"
            shutil.copy(BOB / "step-inside" / "materiais" / "mapeamentos" / "discovercasa.json", mp)
            foto.main([str(t / "forro.png"), "--produto", "Douglas marron", "--largura-m", "1.2", "--altura-m", "0.8",
                       "--mapeamento", str(mp), "--saida", str(t / "saida"), "--lado-max", "256"])
            for m in ("Color", "NormalGL", "Roughness"):
                self.assertTrue((t / "saida" / f"douglas-marron_{m}.jpg").exists(), m)
            e = json.loads(mp.read_text(encoding="utf-8"))["materiais"]["Douglas marron"]
            self.assertEqual(e["textura"]["tile_m"], [1.2, 0.8])
            self.assertEqual(e["textura"]["uso"], "cor")
            self.assertTrue(e["textura"]["fonte"]["licenca"].startswith("fotografia própria"))
            self.assertEqual(e["textura"]["rotacao_uv"], 90)   # kept from the catalogue (the boards stand up)
            self.assertEqual(e["mat"], "MAT_WOOD_CLADDING__DOUGLAS_BROWN")   # the common ID does not change

    def test_produto_desconhecido(self):
        with self.assertRaises(SystemExit):
            foto.main(["x.png", "--produto", "Não existe", "--largura-m", "1"])


if __name__ == "__main__":
    unittest.main()
