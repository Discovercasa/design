"""Step Inside Phase 2 tests: terrain readers, georeferencing, the TIN in Blender, the visit model's checks.

    python -m unittest discover -s step-inside/tests        (from BOB/)

Synthetic inputs are written to a temporary folder (no client data). The Blender tests are skipped when Blender is not
installed; the tests on the real Sobral survey are skipped where the drawings are not (they stay on the PC).
"""
import json
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FERR = AQUI.parent / "ferramentas"
sys.path.insert(0, str(FERR / "fontes"))
sys.path.insert(0, str(FERR / "terreno"))
sys.path.insert(0, str(FERR / "visita"))
import comum  # noqa: E402
import georef  # noqa: E402
import leitores  # noqa: E402
import terreno  # noqa: E402
import visita  # noqa: E402
from comum import CONFIRMED, INFERRED, MISSING, campo, em_falta  # noqa: E402

DXF = """0
SECTION
2
HEADER
9
$INSUNITS
70
6
0
ENDSEC
0
SECTION
2
ENTITIES
0
POINT
8
PONTOS
10
10.0
20
20.0
30
101.25
0
LWPOLYLINE
8
CURVAS
90
3
70
0
38
100.5
10
0.0
20
0.0
10
5.0
20
0.0
10
10.0
20
1.0
0
LWPOLYLINE
8
MUROS
90
2
70
0
10
0.0
20
5.0
10
3.0
20
5.0
0
POLYLINE
8
QUEBRAS
66
1
70
8
0
VERTEX
8
QUEBRAS
10
0.0
20
0.0
30
100.0
0
VERTEX
8
QUEBRAS
10
4.0
20
3.0
30
101.0
0
SEQEND
0
TEXT
8
COTAS
10
2.0
20
2.0
30
0.0
1
100.75
0
3DFACE
8
TIN
10
0.0
20
0.0
30
1.0
11
1.0
21
0.0
31
1.0
12
0.0
22
1.0
32
2.0
13
0.0
23
1.0
33
2.0
0
ENDSEC
0
EOF
"""

LANDXML = """<?xml version="1.0"?>
<LandXML xmlns="http://www.landxml.org/schema/LandXML-1.2" version="1.2">
 <Units><Metric linearUnit="meter" areaUnit="squareMeter" volumeUnit="cubicMeter"/></Units>
 <CoordinateSystem epsgCode="3763" verticalDatum="Cascais"/>
 <CgPoints><CgPoint name="E1">-20100.0 -10000.0 210.5</CgPoint></CgPoints>
 <Surfaces><Surface name="EG"><Definition surfType="TIN">
  <Pnts><P id="1">0 0 100</P><P id="2">0 10 101</P><P id="3">10 0 102</P></Pnts>
  <Faces><F>1 2 3</F></Faces>
 </Definition></Surface></Surfaces>
</LandXML>
"""

ASC = """ncols 3
nrows 2
xllcorner 100
yllcorner 200
cellsize 2
NODATA_value -9999
1 2 3
4 -9999 6
"""


class TestLeitores(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.d = Path(self.td.name)

    def tearDown(self):
        self.td.cleanup()

    def escrever(self, nome, texto):
        p = self.d / nome
        p.write_text(texto, encoding="utf-8")
        return p

    def test_csv_com_cabecalho_e_virgula_decimal(self):
        p = self.escrever("pontos.csv", "id;M;P;Cota\n1;-10000,10;-20100,20;210,55\n2;-9990,00;-20105,00;211,00\n")
        lev = leitores.ler(p)
        self.assertEqual(lev["pontos"], [[-10000.10, -20100.20, 210.55], [-9990.0, -20105.0, 211.0]])

    def test_xyz_sem_cabecalho(self):
        lev = leitores.ler(self.escrever("p.xyz", "1.0 2.0 3.0\n4 5 6\n"))
        self.assertEqual(len(lev["pontos"]), 2)
        self.assertIsNone(lev["unidade"])  # a bare XYZ does not say its unit

    def test_xyz_quatro_colunas_assume_id(self):
        lev = leitores.ler(self.escrever("p.txt", "7 1.0 2.0 3.0\n8 4 5 6\n"))
        self.assertEqual(lev["pontos"][0], [1.0, 2.0, 3.0])
        self.assertTrue(any("id x y z" in a for a in lev["avisos"]))

    def test_landxml_ordem_norte_este(self):
        lev = leitores.ler(self.escrever("s.xml", LANDXML))
        self.assertEqual(lev["unidade"], "m")
        self.assertEqual(lev["crs"]["epsg"], "3763")
        self.assertEqual(lev["pontos"][0], [-10000.0, -20100.0, 210.5])  # x = easting, y = northing
        self.assertEqual(lev["pontos"][2], [10.0, 0.0, 101.0])           # P "0 10 101": N=0, E=10
        self.assertEqual(lev["faces"], [[1, 2, 3]])

    def test_dxf_so_dados_3d_dao_cotas(self):
        lev = leitores.ler(self.escrever("t.dxf", DXF))
        self.assertEqual(lev["unidade"], "m")
        self.assertIn([10.0, 20.0, 101.25], lev["pontos"])
        tipos = sorted(l["tipo"] for l in lev["linhas"])
        self.assertEqual(tipos, ["curva", "linha2d", "quebra"])
        curva = [l for l in lev["linhas"] if l["tipo"] == "curva"][0]
        self.assertEqual(curva["z"], 100.5)
        plana = [l for l in lev["linhas"] if l["tipo"] == "linha2d"][0]
        self.assertTrue(all(q[2] is None for q in plana["pts"]))  # spec §19.4: a 2D line is never a height
        self.assertEqual(lev["rotulos"], [[2.0, 2.0, 100.75]])        # text heights only when declared
        self.assertEqual(len(lev["faces"]), 1)                       # 3DFACE with 3rd = 4th vertex: a triangle

    def test_dxf_filtro_de_camadas(self):
        lev = leitores.ler(self.escrever("t.dxf", DXF), camadas=["PONTOS"])
        self.assertEqual(len(lev["pontos"]), 1)
        self.assertEqual(lev["linhas"], [])

    def test_dxf_binario_recusado(self):
        p = self.d / "b.dxf"
        p.write_bytes(b"AutoCAD Binary DXF\r\n\x1a\x00")
        with self.assertRaises(ValueError):
            leitores.ler(p)

    def test_asc(self):
        lev = leitores.ler(self.escrever("d.asc", ASC))
        self.assertEqual(len(lev["pontos"]), 5)  # one NODATA cell
        self.assertIn([101.0, 203.0, 1.0], lev["pontos"])  # top-left cell centre
        self.assertIn([105.0, 201.0, 6.0], lev["pontos"])

    def test_formato_desconhecido(self):
        with self.assertRaises(ValueError):
            leitores.ler(self.escrever("x.tif", "x"))


def _cruz(x, y, braco=2.5):
    return [{"stroke": "#000000", "fill": None, "sw": 0.0, "subs": [([(x - braco, y), (x + braco, y)], False)]},
            {"stroke": "#000000", "fill": None, "sw": 0.0, "subs": [([(x, y - braco), (x, y + braco)], False)]}]


class TestGeoref(unittest.TestCase):
    def grelha(self, rot=0.0):
        """Crosses every 100 mm at 1:500 (50 m), labels next to them, optionally rotated sheet."""
        paths, tx = [], []
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for i in range(3):
            for j in range(3):
                x, y = 100 + 100 * i, 100 + 100 * j
                xr, yr = 300 + (x - 300) * c - (y - 300) * s, 300 + (x - 300) * s + (y - 300) * c
                paths += _cruz(xr, yr)
                M, P = -10050 + 50 * i, -20050 - 50 * j
                tx.append({"x": xr - 1.0, "y": yr - 1.0, "ang": 90, "h": 2.8, "text": f"{M}mM"})
                tx.append({"x": xr + 1.0, "y": yr - 1.0, "ang": 0, "h": 2.8, "text": f"{P}mP"})
        return tx, paths

    def test_grelha_1_500(self):
        g = georef.grelha_dwfx(*self.grelha())
        self.assertEqual(g["n_cruzes"], 9)
        self.assertAlmostEqual(g["escala_x"], 500.0, places=1)
        self.assertAlmostEqual(g["escala_y"], 500.0, places=1)
        self.assertLess(g["residuo_max_m"], 0.001)
        self.assertFalse(g["espelhado"])
        X, Y = georef.aplicar(g["coef"], (150, 150))  # halfway between crosses
        self.assertAlmostEqual(X, -10025, places=3)
        self.assertAlmostEqual(Y, -20075, places=3)

    def test_grelha_rodada(self):
        g = georef.grelha_dwfx(*self.grelha(rot=10))
        self.assertAlmostEqual(g["escala_x"], 500.0, places=1)
        self.assertLess(g["residuo_max_m"], 0.001)

    def test_sem_grelha(self):
        self.assertIsNone(georef.grelha_dwfx([], []))

    def test_alinhados_recusados(self):
        with self.assertRaises(ValueError):
            georef.ajustar_afim([((0, 0), (0, 0)), ((1, 0), (1, 0)), ((2, 0), (2, 0))])

    def test_sistema_provavel(self):
        self.assertTrue(georef.sistema_provavel([-10000.0], [-20100.0])[1])
        self.assertFalse(georef.sistema_provavel([12.0], [30.0])[1])
        self.assertIn("locais", georef.sistema_provavel([12.0], [30.0])[0])

    def test_pontos_coordenados(self):
        tx = [{"x": 10.0, "y": 10.0, "ang": 90, "h": 0.7, "text": "-10035,3mM"},
              {"x": 10.5, "y": 10.1, "ang": 0, "h": 0.7, "text": "-20117,1mP"},
              {"x": 50.0, "y": 50.0, "ang": 90, "h": 2.8, "text": "-10050mM"}]
        self.assertEqual(georef.pontos_coordenados(tx), [((10.0, 10.0), (-10035.3, -20117.1))])


class TestTracejado(unittest.TestCase):
    def test_quadrado_tracejado_fecha(self):
        """A 100 mm square drawn as 2 mm filled dashes with 1 mm gaps (and gaps at the corners) closes."""
        paths = []
        cantos = [(0, 0), (100, 0), (100, 100), (0, 100)]
        for k in range(4):
            (x0, y0), (x1, y1) = cantos[k], cantos[(k + 1) % 4]
            L = math.dist((x0, y0), (x1, y1))
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            t = 2.0  # corner gap
            while t + 2 < L - 2:
                a = (x0 + ux * t, y0 + uy * t)
                b = (x0 + ux * (t + 2), y0 + uy * (t + 2))
                nx, ny = -uy * 0.2, ux * 0.2
                q = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
                paths.append({"stroke": None, "fill": "#000000", "sw": 0.0, "subs": [(q, True)]})
                t += 3
        cad = leitores.tracejado(paths, {"fill": "#000000"})
        self.assertEqual(len(cad), 1)
        self.assertEqual(cad[0][0], cad[0][-1])
        per = sum(math.dist(cad[0][i], cad[0][i + 1]) for i in range(len(cad[0]) - 1))
        self.assertAlmostEqual(per, 400 - 4 * (4 - 2 * math.sqrt(2)), delta=1.5)  # corners cut across their gaps


class TestAvaliacaoTerreno(unittest.TestCase):
    def meta(self, **mud):
        m = {k: em_falta("terreno") for k in terreno.CAMPOS_TERRENO}
        m["unidade_horizontal"] = campo("m", CONFIRMED, "texto")
        m["unidade_vertical"] = campo("m", CONFIRMED, "texto")
        m["crs"] = campo("EPSG:3763", CONFIRMED, "texto")
        m["datum_vertical"] = campo("Cascais", CONFIRMED, "texto")
        for k in ("data_levantamento", "precisao", "pontos_controlo", "fonte", "limite_lote"):
            m[k] = campo("x", CONFIRMED, "utilizador")
        m.update(mud)
        return m

    def sup(self, **mud):
        s = {"id": "t", "validacao_cruzada": {"rmse": 0.2}, "malha": {"faces_para_baixo": 0}, "curvas": {}}
        s.update(mud)
        return s

    def test_pass(self):
        self.assertEqual(terreno.avaliar(self.meta(), [self.sup()], {})[0], "PASS")

    def test_crs_inferido_e_aproximado(self):
        g, mot = terreno.avaliar(self.meta(crs=campo("PT-TM06?", INFERRED, "inferencia")), [self.sup()], {})
        self.assertEqual(g, "WARNING")
        self.assertTrue(any("aproximado" in m for m in mot))

    def test_pontos_afastados_pedem_revisao(self):
        g, _ = terreno.avaliar(self.meta(), [self.sup(pontos_afastados=[{"indice": 3}])], {})
        self.assertEqual(g, "NEEDS_HUMAN_REVIEW")

    def test_unidade_desconhecida_falha(self):
        g, _ = terreno.avaliar(self.meta(unidade_horizontal=em_falta("terreno")), [self.sup()], {})
        self.assertEqual(g, "FAIL")

    def test_pontos_incoerentes_falham(self):
        g, _ = terreno.avaliar(self.meta(), [self.sup(validacao_cruzada={"rmse": 9.0})], {})
        self.assertEqual(g, "FAIL")


class TestVisita(unittest.TestCase):
    FONTES = {"niveis": {"piso1_interior": {"valor": 3.0, "estado": CONFIRMED}},
              "paredes": [{"id": "PE1", "piso": 0, "eixo": "x", "inicio": {"valor": 0.0}, "fim": {"valor": 6.0},
                           "posicao": {"valor": 0.0}, "espessura": {"valor": 0.16},
                           "aberturas": [{"id": "0", "tipo": {"valor": "porta"}, "inicio": {"valor": 1.0},
                                          "fim": {"valor": 2.0}}]},
                          {"id": "PI2", "piso": 1, "eixo": "y", "inicio": {"valor": 0.0}, "fim": {"valor": 0.7},
                           "posicao": {"valor": 3.0}, "espessura": {"valor": 0.1}, "aberturas": []}]}

    def test_aberturas_com_cota_do_piso(self):
        a = visita.aberturas(self.FONTES)
        self.assertEqual(len(a), 1)
        self.assertEqual((a[0]["inicio"], a[0]["fim"], a[0]["z_piso"]), (1.0, 2.0, 0.0))

    def test_paredes_cheias_longe_dos_vaos_e_cantos(self):
        c = visita.paredes_cheias(self.FONTES, {"PE1": 2.4})
        self.assertEqual([x["parede"] for x in c], ["PE1"])  # PI2: 0.7 m minus the corners is too short
        self.assertEqual((round(c[0]["inicio"], 2), round(c[0]["fim"], 2)), (2.15, 5.8))
        self.assertEqual(c[0]["altura_max"], 2.4)

    def r(self, **mod):
        m = {"dimensoes_modelo": {"estrutura_planta_m": [9.86, 6.11]}, "malhas": {}, "aberturas": {"fechadas": []}}
        m.update(mod)
        return {"modelo": m, "dimensoes_fontes": {"comprimento": campo(9.86, CONFIRMED, "geometria"),
                                                   "profundidade": campo(6.11, CONFIRMED, "geometria")},
                "choques_madeira": {"choques": 0}, "terreno": "PASS"}

    def test_pass(self):
        self.assertEqual(visita.avaliar(self.r(), {}, "PASS")[0], "PASS")

    def test_dimensoes_erradas_falham(self):
        r = self.r(dimensoes_modelo={"estrutura_planta_m": [9.90, 6.11]})
        self.assertEqual(visita.avaliar(r, {}, "PASS")[0], "FAIL")

    def test_vao_fechado_pede_revisao(self):
        r = self.r(aberturas={"fechadas": [{"parede": "PE1", "abertura": "0"}]})
        self.assertEqual(visita.avaliar(r, {}, "PASS")[0], "NEEDS_HUMAN_REVIEW")

    def test_controlo_do_teste_dos_vaos(self):
        r = self.r(aberturas={"fechadas": [], "controlo_abertas_por_engano": ["PI2"]})
        self.assertEqual(visita.avaliar(r, {}, "PASS")[0], "NEEDS_HUMAN_REVIEW")

    def test_normais_invertidas_falham(self):
        self.assertEqual(visita.avaliar(self.r(malhas={"n_invertidas": 2}), {}, "PASS")[0], "FAIL")


def _blender():
    sys.path.insert(0, str(AQUI.parents[1]))
    from ferramentas.comum import encontrar_blender
    return encontrar_blender()


@unittest.skipUnless(_blender(), "Blender não está instalado")
class TestTinBlender(unittest.TestCase):
    """The TIN on a known surface: z = 100 + 0.08 x + 0.03 y (a plane: every check must be ~0)."""

    @classmethod
    def setUpClass(cls):
        from ferramentas.comum import correr_blender
        cls.td = tempfile.TemporaryDirectory()
        d = Path(cls.td.name)

        def z(x, y):
            return 100 + 0.08 * x + 0.03 * y
        pts = [[x, y, round(z(x, y), 3)] for x in range(0, 101, 10) for y in range(0, 81, 10)]
        pts.append([55.0, 45.0, z(55, 45) + 6.0])  # a spike (misread label)
        curvas, rotulos = [], []
        for zc in [100.5 + 0.5 * k for k in range(19)]:  # contours every 0.5 m, index every 2.5 m
            linha = []
            for y in range(0, 81, 4):
                x = (zc - 100 - 0.03 * y) / 0.08
                if 0 <= x <= 100:
                    linha.append([x, float(y)])
            if len(linha) >= 2:
                mestra = abs(zc / 2.5 - round(zc / 2.5)) < 1e-9
                curvas.append({"pts": linha, "papel": "mestra" if mestra else "intermedia"})
                if mestra:
                    rotulos.append(linha[len(linha) // 2] + [zc])
        run = {"blend": str(d / "t.blend"), "saida": str(d / "t.json"),
               "superficies": [{"id": "teste", "nome": "plano", "pontos": pts, "curvas": curvas,
                                "rotulos_curvas": rotulos, "limite": [[0, 0], [100, 0], [100, 80], [0, 80]]}]}
        (d / "run.json").write_text(json.dumps(run), encoding="utf-8")
        cls.code, cls.out = correr_blender(FERR / "terreno" / "blender_tin.py", [d / "run.json"], factory=True)
        cls.R = json.loads((d / "t.json").read_text(encoding="utf-8"))["superficies"][0] if cls.code == 0 else None

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_correu(self):
        self.assertEqual(self.code, 0, self.out[-2000:])
        self.assertIn("TIN_OK", self.out)

    def test_equidistancias(self):
        c = self.R["curvas"]
        self.assertEqual(c["equidistancia_mestras"], 2.5)
        self.assertEqual(c["equidistancia"], 0.5)
        self.assertGreater(c["com_cota_final"], 0.8 * c["linhas"])

    def test_pico_afastado(self):
        self.assertEqual([p["indice"] for p in self.R["pontos_afastados"]], [len(range(0, 101, 10)) * len(range(0, 81, 10))])

    def test_curvas_concordam_com_pontos(self):
        self.assertLess(self.R["curvas_vs_pontos"]["p50"], 0.05)

    def test_malha_virada_para_cima(self):
        self.assertEqual(self.R["malha"]["faces_para_baixo"], 0)
        self.assertAlmostEqual(self.R["malha"]["inclinacao_graus_p50"], math.degrees(math.atan(math.hypot(0.08, 0.03))), delta=0.5)


class TestLevantamentoSobral(unittest.TestCase):
    """The real survey sheet of the Sobral architecture set (skipped where the drawings are not)."""

    def test_folha_2(self):
        p = terreno.pasta_desenhos("Sobral", "SMA_012_arquitectura_pecas_desenhadas.dwfx")
        if not p:
            self.skipTest("desenhos do Sobral não estão neste PC")
        decl = comum.ler_json(AQUI.parent / "projetos-teste" / "sobral-tipo1" / "terreno.json")
        f = decl["superficies"][0]["fontes"][0]
        lev = leitores.ler_dwfx(p, f["folha"], f)
        self.assertEqual(lev["contagens"]["pontos_cotados"], 450)
        self.assertAlmostEqual(lev["georef"]["escala_x"], 500, delta=0.5)
        self.assertLess(lev["georef"]["residuo_max_m"], 0.01)
        self.assertEqual(len(lev["limites"]), 1)
        self.assertEqual(lev["limites"][0][0], lev["limites"][0][-1])  # the lot boundary closes
        self.assertEqual(sorted({r[2] for r in lev["rotulos"]})[:2], [202.5, 205.0])


if __name__ == "__main__":
    unittest.main()


def _dxf(entidades):
    """A minimal ASCII DXF from [(type, [(code, value)])]."""
    linhas = ["0", "SECTION", "2", "ENTITIES"]
    for tipo, cs in entidades:
        linhas += ["0", tipo]
        for c, v in cs:
            linhas += [str(c), str(v)]
    return "\n".join(linhas + ["0", "ENDSEC", "0", "EOF"]) + "\n"


class TestDxfLevantamento(unittest.TestCase):
    """What the real survey DXF of Torres Vedras taught (2026-11-08): contours as 3D polylines with z = 0, the CRS in a
    legend text, GNSS labels E= / N= / h=, several copies of the survey in model space."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.d = Path(self.td.name)

    def tearDown(self):
        self.td.cleanup()

    def ler(self, ents, **kw):
        p = self.d / "s.dxf"
        p.write_text(_dxf(ents), encoding="utf-8")
        return leitores.ler(p, **kw)

    def test_polilinha_3d_com_cotas_zero_e_2d(self):
        ents = [("POLYLINE", [(8, "CV"), (66, 1), (70, 8)]),
                ("VERTEX", [(8, "CV"), (10, 0), (20, 0), (30, 0)]), ("VERTEX", [(8, "CV"), (10, 5), (20, 0), (30, 0)]),
                ("SEQEND", [(8, "CV")])]
        lev = self.ler(ents)
        self.assertEqual([l["tipo"] for l in lev["linhas"]], ["linha2d"])
        self.assertEqual(lev["pontos"], [])

    def test_crs_escrito_e_rotulos_gnss(self):
        ents = [("TEXT", [(8, "LEG"), (10, 0), (20, 0), (1, "COORDENADAS ETRS89/PT-TM06 (Projec: tmerc - EPSG:3763)")]),
                ("TEXT", [(8, "GPS"), (10, 1), (20, 1), (1, "E=-10000.123m.")]),
                ("TEXT", [(8, "GPS"), (10, 1), (20, 1), (1, "N=-20000.456m.")]),
                ("TEXT", [(8, "GPS"), (10, 1), (20, 1), (1, "h=100.25m.")])]
        lev = self.ler(ents)
        self.assertEqual(lev["crs"]["epsg"], "3763")
        self.assertEqual(lev["gnss"], [[-10000.123, -20000.456, 100.25]])

    def test_escolher_copia_pelos_pontos_gnss(self):
        quadrado = [[0, 0], [20, 0], [20, 20], [0, 20]]
        copia = [[x + 100, y + 100] for x, y in quadrado]
        lev = {"pontos": [[5, 5, 10.0], [15, 15, 11.0], [105, 105, 10.0], [115, 115, 11.0], [40, 40, 12.0]],
               "linhas": [{"tipo": "linha2d", "pts": [[1, 1, None], [9, 9, None], [60, 60, None]], "camada": "CV"}],
               "limites": [copia, quadrado], "gnss": [[5, 5, 10.0], [15, 15, 11.0]], "avisos": [], "contagens": {}}
        terreno.escolher_copia(lev, 15.0)
        self.assertEqual(lev["limites"], [quadrado])
        self.assertEqual(sorted(p[2] for p in lev["pontos"]), [10.0, 11.0])  # (40, 40) is 28 m away: dropped
        self.assertEqual(lev["linhas"][0]["pts"], [[1, 1, None], [9, 9, None]])  # cut where it leaves the zone
        self.assertEqual(lev["contagens"]["copias_do_levantamento"], 2)

    def test_sem_gnss_avisa(self):
        lev = {"pontos": [], "linhas": [], "limites": [[[0, 0], [1, 0], [1, 1]], [[5, 5], [6, 5], [6, 6]]],
               "gnss": [], "avisos": [], "contagens": {}}
        terreno.escolher_copia(lev, 15.0)
        self.assertEqual(len(lev["limites"]), 2)
        self.assertTrue(lev["avisos"])


class TestAjustePlanta(unittest.TestCase):
    """The model's walls fitted to the walls' hatches of a site plan: a 10 × 6 m box with a middle wall, turned 30°."""

    def test_recupera_rotacao_e_origem(self):
        import ajuste
        paredes = [{"eixo": "x", "inicio": 0, "fim": 10, "posicao": 0.08, "espessura": 0.16},
                   {"eixo": "x", "inicio": 0, "fim": 10, "posicao": 5.92, "espessura": 0.16},
                   {"eixo": "y", "inicio": 0, "fim": 6, "posicao": 0.08, "espessura": 0.16},
                   {"eixo": "y", "inicio": 0, "fim": 6, "posicao": 9.92, "espessura": 0.16},
                   {"eixo": "y", "inicio": 0, "fim": 6, "posicao": 4.0, "espessura": 0.1}]
        loc = []
        for k in range(0, 101, 4):  # hatch vertices sit on the wall faces (model coordinates)
            loc += [(k / 10, 0.0), (k / 10, 0.16), (k / 10, 5.84), (k / 10, 6.0)]
        for k in range(2, 59, 4):
            loc += [(0.0, k / 10), (0.16, k / 10), (9.84, k / 10), (10.0, k / 10), (3.95, k / 10), (4.05, k / 10)]
        th = math.radians(30)
        T = (-11000.0, -21000.0)
        pts = [(math.cos(th) * x - math.sin(th) * y + T[0], math.sin(th) * x + math.cos(th) * y + T[1]) for x, y in loc]
        pts += [(T[0] + 30, T[1] + 30), (T[0] - 12, T[1] + 4)]  # other hatches nearby
        r = ajuste.ajustar(pts, paredes)
        self.assertAlmostEqual(r["rotacao_graus"], 30.0, delta=0.15)
        self.assertLess(math.dist(r["origem"], T), 0.02)
        self.assertGreaterEqual(r["inliers"], len(loc) - 2)
        x, y = ajuste.mundo(r, 10, 6)  # the far corner lands where it should
        self.assertLess(math.dist((x, y), (math.cos(th) * 10 - math.sin(th) * 6 + T[0], math.sin(th) * 10 + math.cos(th) * 6 + T[1])), 0.06)
