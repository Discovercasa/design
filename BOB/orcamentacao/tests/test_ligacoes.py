"""Orçamentação tests: stable product codes on every Listagem line, and every code linked (or explained) in
orcamentacao/ligacoes.json.

    python -m unittest discover -s orcamentacao/tests        (from BOB/)
"""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BOB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BOB))
from ferramentas.documentos.codigos import PRODUTOS, codigo  # noqa: E402

LIG = json.loads((BOB / "orcamentacao" / "ligacoes.json").read_text(encoding="utf-8"))["ligacoes"]
BASES = {"area", "comprimento", "volume", "pecas", "compra"}


def ler_csv(caminho):
    with open(caminho, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


class TestLigacoes(unittest.TestCase):
    def test_um_registo_por_codigo(self):
        self.assertEqual(set(LIG), set(PRODUTOS))
        for k, v in LIG.items():
            self.assertEqual(v["produto"], PRODUTOS[k], k)

    def test_registos_completos(self):
        for k, v in LIG.items():
            if v.get("resumo"):
                continue
            self.assertIn("hub", v, k)
            self.assertTrue(v.get("nota"), f"{k}: a note says why or how")
            self.assertIn(v["estado"], ("INFERRED", "CONFIRMED"), k)
            if v["hub"]:
                self.assertRegex(v["hub"], r"^[0-9a-f-]{36}$", k)
                self.assertIn(v["unidade"], ("m2", "ml", "m3", "un"), k)
                self.assertIn(v["quantidade"]["base"], BASES, k)

    def test_sem_nomes_nem_precos_do_hub(self):
        # the repo is public: only ids of the Hub list, never its names, suppliers or prices
        for k, v in LIG.items():
            self.assertFalse({"preco", "fornecedor", "material", "nome"} & set(v), k)


class TestCodigos(unittest.TestCase):
    def test_madeira(self):
        self.assertEqual(codigo("1", "Paredes exteriores (módulos)", "Madeira 11x3,5"), "MAD-CASQ")
        self.assertEqual(codigo("1", "Madres", "Madeira 22x7,5"), "MAD-CASQ-22")
        self.assertEqual(codigo("1", "Lameladas 200x100", "Madeira 20x10"), "MAD-LAM")
        self.assertEqual(codigo("8m", "Pérgola", "Madeira 16x16"), "MAD-LAM-AUT")
        self.assertEqual(codigo("8m", "Pérgola", "Madeira 7x3"), "MAD-AUT")
        self.assertEqual(codigo("1", "1.9", "Madeira OSB 22"), "OSB-22")

    def test_camadas(self):
        self.assertEqual(codigo("2", "Forro Tremolo 22x135 (A)", ""), "FORRO-TREMOLO")
        self.assertEqual(codigo("3", "Lã mineral Volcalis Comfort", ""), "LA-80")
        self.assertEqual(codigo("5", "Lã mineral Volcalis 100 mm (teto)", ""), "LA-100")
        self.assertEqual(codigo("7", "Vidros", ""), "RESUMO")
        self.assertEqual(codigo("7i", "Janela de correr", ""), "CAIXILHARIA")
        self.assertEqual(codigo("6", "Caleira de laró", ""), "CALEIRA-LARO")
        self.assertEqual(codigo("6", "Produto que não existe", ""), "")

    def test_torres_vedras_tudo_com_codigo(self):
        linhas = ler_csv(BOB / "Construção Torres Vedras" / "documentos" / "D2503_Listagem_Material.csv")
        self.assertGreater(len(linhas), 40)
        sem = [l["descricao"] for l in linhas if not l["codigo"]]
        self.assertEqual(sem, [])
        self.assertTrue(all(l["codigo"] in LIG for l in linhas))

    def test_casa_configurada_so_a_opcao_escolhida(self):
        """A configured house with an exposed roof (L / T / U) and the capoto facade (B): every line has a code and the
        two facades not chosen (A, C) are not in the purchase list (they listed all three until 2026-11-11)."""
        casa = json.loads((BOB / "configurador" / "exemplos" / "casa_exemplo_L.json").read_text(encoding="utf-8"))
        casa["cobertura"] = {"tipo": "misto", "inclinacao_pct": 15, "beirado": 0.25}
        casa.setdefault("acabamentos", {})["exterior"] = "B"
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "casa.json"
            f.write_text(json.dumps(casa, ensure_ascii=False), encoding="utf-8")
            r = subprocess.run([sys.executable, str(BOB / "ferramentas" / "configurador" / "para_construtor.py"), str(f),
                                "--saida", str(Path(t) / "m"), "--documentos"], capture_output=True, text=True, encoding="utf-8",
                               errors="replace", cwd=BOB)
            self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1500:])
            linhas = ler_csv(next((Path(t) / "m").rglob("*_Listagem_Material.csv")))
        self.assertEqual([l["descricao"] for l in linhas if not l["codigo"]], [])
        ext = [l["descricao"] for l in linhas if l["capitulo"].startswith("Paredes - camadas exteriores")]
        self.assertTrue(any(d.endswith("(B)") for d in ext), ext)
        self.assertFalse(any(d.endswith(("(A)", "(C)")) for d in ext), ext)
        self.assertIn("PAINEL-TELHA-40", {l["codigo"] for l in linhas})


if __name__ == "__main__":
    unittest.main()
