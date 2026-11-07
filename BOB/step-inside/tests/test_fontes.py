"""Tests for the Step Inside Phase 1 source tools (standard library unittest; synthetic fixture, no client data).

    python -m unittest discover -s step-inside/tests -v        (from BOB/)
"""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "ferramentas" / "fontes"))

import esquema  # noqa: E402
import matriz  # noqa: E402
import proveniencia  # noqa: E402
import relatorio  # noqa: E402
from comum import CONFIRMED, INFERRED, MISSING, REVIEW, campos  # noqa: E402

FIX = AQUI / "fixtures" / "casa_simples"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for f in FIX.iterdir():
            shutil.copy(f, self.tmp / f.name)
        self.cfg = json.loads((self.tmp / "config.json").read_text(encoding="utf-8"))
        self.planta = json.loads((self.tmp / "planta_paredes.json").read_text(encoding="utf-8"))
        self.decl = json.loads((self.tmp / "declaracoes.json").read_text(encoding="utf-8"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def gerar(self, decl=None):
        (self.tmp / "config.json").write_text(json.dumps(self.cfg), encoding="utf-8")
        (self.tmp / "planta_paredes.json").write_text(json.dumps(self.planta), encoding="utf-8")
        return proveniencia.construir(self.tmp / "config.json", decl)

    @staticmethod
    def campo(doc, caminho):
        return dict(campos(doc))[caminho]


class TestProveniencia(Base):
    def test_sem_declaracoes_escala_deduzida(self):
        doc = self.gerar()
        self.assertEqual(esquema.validar(doc), [])
        self.assertEqual(self.campo(doc, "escala")["estado"], INFERRED)
        self.assertEqual(self.campo(doc, "paredes.P01.inicio")["estado"], INFERRED)  # inherits the scale
        porta = self.campo(doc, "paredes.P01.aberturas.1.altura")
        self.assertEqual((porta["estado"], porta["metodo"]), (REVIEW, "valor_omissao"))  # not in any drawing
        janela = self.campo(doc, "paredes.P01.aberturas.0.peitoril")
        self.assertEqual(janela["estado"], REVIEW)  # the config note says "a confirmar"
        interior = self.campo(doc, "paredes.P05.aberturas.0.altura")
        self.assertEqual((interior["estado"], interior["metodo"], interior["valor"]), (CONFIRMED, "norma_empresa", 2.03))
        self.assertEqual(self.campo(doc, "terreno.crs")["estado"], MISSING)
        self.assertIsNone(self.campo(doc, "referencial.norte")["valor"])
        self.assertEqual(relatorio.avaliar(doc)[0], REVIEW)

    def test_escala_declarada_confirma_a_geometria(self):
        doc = self.gerar(self.decl)
        self.assertEqual(self.campo(doc, "escala")["estado"], CONFIRMED)
        self.assertEqual(self.campo(doc, "paredes.P03.espessura")["estado"], CONFIRMED)
        self.assertEqual(self.campo(doc, "dimensoes.area_base_fundacao")["valor"], 80.0)

    def test_vao_fora_da_parede_falha(self):
        self.planta["paredes"][0]["aberturas"].append({"s0": 9.5, "s1": 10.6, "tipo": "janela"})
        doc = self.gerar(self.decl)
        self.assertTrue(any(c["gravidade"] == "FAIL" for c in doc["conflitos"]))
        self.assertEqual(relatorio.avaliar(doc)[0], "FAIL")

    def test_vaos_sobrepostos_falham(self):
        self.planta["paredes"][2]["aberturas"].append({"s0": 5.0, "s1": 6.0, "tipo": "janela"})
        doc = self.gerar(self.decl)
        self.assertEqual(relatorio.avaliar(doc)[0], "FAIL")

    def test_peitoril_acima_do_topo_falha(self):
        self.cfg["aberturas"]["janela"] = {"peitoril": 2.0, "topo": 1.5}
        self.assertEqual(relatorio.avaliar(self.gerar(self.decl))[0], "FAIL")

    def test_dimensoes_da_config_contra_a_planta(self):
        self.cfg["casa"]["comprimento"] = 10.5
        doc = self.gerar(self.decl)
        c = self.campo(doc, "dimensoes.comprimento")
        self.assertEqual(c["conflitos"][0]["valor"], 10.0)
        self.assertIn("dimensoes.comprimento", [x["campo"] for x in doc["conflitos"] if x["estado"] == "aberto"])

    def test_declaracao_com_outro_valor_abre_conflito(self):
        d = copy.deepcopy(self.decl)
        d["campos"]["niveis.pe_direito"] = {"estado": CONFIRMED, "metodo": "utilizador", "valor": 2.6}
        doc = self.gerar(d)
        self.assertTrue(any(c["campo"] == "niveis.pe_direito" and c["gravidade"] == REVIEW for c in doc["conflitos"]))

    def test_declaracao_sem_campo_avisa(self):
        d = copy.deepcopy(self.decl)
        d["campos"]["niveis.nao_existe"] = {"estado": CONFIRMED, "metodo": "utilizador"}
        doc = self.gerar(d)
        self.assertTrue(any(c["campo"] == "niveis.nao_existe" and c["gravidade"] == "WARNING" for c in doc["conflitos"]))

    def test_declaracao_preenche_um_campo_em_falta(self):
        d = copy.deepcopy(self.decl)
        d["campos"]["terreno.fonte"] = {"estado": CONFIRMED, "metodo": "texto", "valor": "levantamento.dwg"}
        c = self.campo(self.gerar(d), "terreno.fonte")
        self.assertEqual((c["estado"], c["valor"]), (CONFIRMED, "levantamento.dwg"))

    def test_modulos_reais_prevalecem(self):
        self.cfg["modulos_reais"] = {"ficheiro": "modulos.json"}
        doc = self.gerar(self.decl)
        jan = self.campo(doc, "paredes.P01.aberturas.0.peitoril")
        self.assertEqual((jan["valor"], jan["estado"], jan["metodo"]), (0.9, CONFIRMED, "desenho_empresa"))
        self.assertEqual(jan["conflitos"][0]["valor"], 1.0)
        self.assertEqual(jan["conflitos"][0]["estado"], "resolvido")
        porta = self.campo(doc, "paredes.P01.aberturas.1.largura")
        self.assertEqual(porta["valor"], 0.95)
        # M2's window is not in the plan; P03's window is not in the modules
        abertos = {c["campo"]: c["gravidade"] for c in doc["conflitos"] if c["estado"] == "aberto"}
        self.assertEqual(abertos.get("modulos_reais.M2"), "WARNING")
        self.assertEqual(abertos.get("paredes.P03.aberturas.0.tipo"), REVIEW)

    def test_tudo_confirmado_passa(self):
        d = copy.deepcopy(self.decl)
        d["campos"]["*"] = {"estado": CONFIRMED, "metodo": "utilizador"}
        doc = self.gerar(d)
        self.assertEqual(esquema.validar(doc), [])
        self.assertEqual(relatorio.avaliar(doc)[0], "PASS")
        md, res = relatorio.markdown(doc)
        self.assertIn("Resultado: PASS", md)


class TestProjetosDeTeste(unittest.TestCase):
    """The two Phase 1 test projects, from the model data in the repo (the drawings themselves stay on the PC)."""
    BOB = AQUI.parents[1]
    PT = AQUI.parent / "projetos-teste"

    def construir(self, config, pasta):
        p = self.PT / pasta
        return proveniencia.construir(self.BOB / config, json.loads((p / "declaracoes.json").read_text(encoding="utf-8")),
                                      json.loads((p / "catalogo.json").read_text(encoding="utf-8")))

    def test_torres_vedras(self):
        doc = self.construir("Construção Torres Vedras/modelos/casa/config.json", "torres-vedras")
        self.assertEqual(esquema.validar(doc), [])
        self.assertEqual(doc["projeto"]["entrada"], "planta_arquitetura")
        vaos = [a for p in doc["paredes"] for a in p["aberturas"]]
        self.assertEqual(len(vaos), 19)
        self.assertTrue(all(a["altura"]["metodo"] == "desenho_empresa" for a in vaos))  # all matched in D2503
        self.assertNotEqual(relatorio.avaliar(doc)[0], "FAIL")

    def test_sobral_tipo1(self):
        doc = self.construir("Construção Sobral/modelos/tipo1/config.json", "sobral-tipo1")
        self.assertEqual(esquema.validar(doc), [])
        self.assertEqual(doc["projeto"]["entrada"], "desenhos_engenheiro")
        self.assertEqual(self.campo(doc, "escala")["estado"], CONFIRMED)  # 1:50 written on the sheets
        ids = {p["id"] for p in doc["paredes"]}
        self.assertNotIn("PI2.09", ids)  # removed on purpose (duct)
        self.assertIn("PD1.01", ids)  # added from the architecture
        vao = [a for p in doc["paredes"] if p["id"] == "PE1.04" for a in p["aberturas"]][0]
        self.assertEqual(vao["altura"]["estado"], INFERRED)  # sizes are not drawn by the engineer
        self.assertNotEqual(relatorio.avaliar(doc)[0], "FAIL")

    campo = staticmethod(Base.campo)


def _desenhos(obra, ficheiro):
    """Folder holding a project's drawing (they stay on the PC, never in Git), or None to skip the test.
    STEP_INSIDE_DESENHOS may point at the folder that contains "Construção <obra>/desenhos/"."""
    import os
    bases = [Path(os.environ["STEP_INSIDE_DESENHOS"])] if os.environ.get("STEP_INSIDE_DESENHOS") else []
    bases += [AQUI.parents[1], AQUI.parents[3].parent]  # BOB/ itself, or the old BOB folder next to _trabalho/
    for b in bases:
        d = b / f"Construção {obra}" / "desenhos"
        if (d / ficheiro).exists():
            return d
    return None


class TestRegressaoLeitores(unittest.TestCase):
    """The existing readers must still give the stored plan / panels (spec §3.2: regression tests with reference
    projects). Runs only where the drawings are (skipped elsewhere)."""
    BOB = AQUI.parents[1]

    def test_planta_torres_vedras(self):
        from ferramentas.dwfx.leitor import Dwfx
        from ferramentas.modelo.planta_arquitetura import ler_planta
        guardada = json.loads((self.BOB / "Construção Torres Vedras/modelos/casa/planta_paredes.json").read_text(encoding="utf-8"))
        o = guardada["origem_desenho"]
        pasta = _desenhos("Torres Vedras", o["dwfx"])
        if not pasta:
            self.skipTest("desenhos de Torres Vedras não estão neste PC")
        nova = ler_planta(Dwfx(pasta / o["dwfx"]).paths(o["folha"]), o["regiao"], o["escala"],
                          origem={"dwfx": o["dwfx"], "folha": o["folha"]})
        self.assertEqual(nova["paredes"], guardada["paredes"])
        self.assertEqual(nova["contorno"], guardada["contorno"])

    def test_paineis_sobral_tipo1(self):
        from ferramentas.dwfx.leitor import Dwfx
        from ferramentas.dwfx.pecas import build_members
        from ferramentas.modelo.extrair_casa import elevations, place_panels
        cp = self.BOB / "Construção Sobral/modelos/tipo1/config.json"
        cfg = json.loads(cp.read_text(encoding="utf-8"))
        nome = Path(cfg["dwfx"]).name
        pasta = _desenhos("Sobral", nome)
        if not pasta:
            self.skipTest("desenhos do Sobral não estão neste PC")
        G = json.loads((cp.parent / cfg["saida"]["geometria"]).read_text(encoding="utf-8"))
        dw, S, fw = Dwfx(pasta / nome), cfg.get("escala", 50) / 1000, cfg["folhas"]["paredes"]
        mw, gw = build_members(dw.paths(fw)), dw.glyphs(fw)
        paineis = place_panels(mw, gw, elevations(mw, gw, cfg, S), cfg, S)
        chave = ("nome", "piso", "origem", "sentido", "espessura", "encaixe")
        resumo = lambda ps: sorted(([p[k] for k in chave] for p in ps), key=lambda x: (x[0], x[1]))  # noqa: E731
        self.assertEqual(resumo(paineis), resumo(G["paineis"]))


class TestRelatorio(unittest.TestCase):
    def test_padrao_com_ids_com_pontos(self):
        self.assertEqual(relatorio._padrao("paredes.PE1.12.aberturas.3.altura"), "paredes.*.aberturas.*.altura")
        self.assertEqual(relatorio._padrao("paredes.P03.espessura"), "paredes.*.espessura")
        self.assertEqual(relatorio._padrao("niveis.pe_direito"), "niveis.pe_direito")


class TestEsquema(Base):
    def test_missing_com_valor_e_erro(self):
        doc = self.gerar(self.decl)
        doc["terreno"]["crs"]["valor"] = "EPSG:3763"
        self.assertTrue(any("MISSING com valor" in e for e in esquema.validar(doc)))

    def test_estado_desconhecido_e_erro(self):
        doc = self.gerar(self.decl)
        doc["escala"]["estado"] = "TALVEZ"
        self.assertTrue(esquema.validar(doc))


class TestMatriz(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ficheiro(self, nome, dados=b""):
        p = self.tmp / nome
        p.write_bytes(dados)
        return p

    def test_categorias(self):
        dwg = matriz.classificar(self.ficheiro("a.dwg", b"AC1032" + b"\0" * 20))
        self.assertEqual((dwg["categoria"], dwg["versao"]), (matriz.CONVERT, "AutoCAD 2018 ou mais recente"))
        self.assertEqual(matriz.classificar(self.ficheiro("m.skp"))["categoria"], matriz.REFERENCE)
        self.assertEqual(matriz.classificar(self.ficheiro("f.jpg"))["categoria"], matriz.REFERENCE)
        self.assertEqual(matriz.classificar(self.ficheiro("t.las"))["categoria"], matriz.UNSUPPORTED)
        self.assertEqual(matriz.classificar(self.ficheiro("x.abc"))["categoria"], matriz.UNSUPPORTED)
        self.assertEqual(matriz.classificar(self.ficheiro("d.dwfx", b"nao e zip"))["categoria"], matriz.UNSUPPORTED)

    def test_pdf_sem_tracos_nao_e_direct(self):
        pdf = (b"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
               b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
               b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] >> endobj\ntrailer << /Root 1 0 R >>\n")
        self.assertEqual(matriz.classificar(self.ficheiro("s.pdf", pdf))["categoria"], matriz.REFERENCE)


if __name__ == "__main__":
    unittest.main()
