"""Step Inside: closing the joints between the pieces of a finish layer (visit model, user 2026-11-09).

    python -m unittest discover -s step-inside/tests        (from BOB/)
"""
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "ferramentas" / "visita"))
import juntas as J  # noqa: E402


def tabua(s0, s1, z0=0.0, z1=2.5, y0=0.0, e=0.022):
    """A vertical board on a façade facing -y: along x from s0 to s1, thickness along y."""
    return ((s0, y0, z0), (s1, y0 + e, z1))


class TestJuntas(unittest.TestCase):
    def test_tremolo_boards_6_mm_apart_close_by_half_each(self):
        # boards 135 mm on centre, 129 mm wide: the production model's 6 mm joint
        caixas = [tabua(i * 0.135, i * 0.135 + 0.129) for i in range(4)]
        ext, n = J.extensoes(caixas)
        self.assertEqual(n, 3)
        self.assertAlmostEqual(ext[0][(0, 1)], 0.003, places=6)
        self.assertAlmostEqual(ext[1][(0, -1)], 0.003, places=6)
        self.assertNotIn((0, -1), ext[0])  # the façade end keeps its edge
        self.assertNotIn((0, 1), ext[3])

    def test_plasterboard_grid_closes_both_ways(self):
        # 2 x 2 sheets of 1,2 x 2,6 with 2 mm joints, on a wall facing x
        caixas = [((0.0, s, z), (0.0125, s + 1.198, z + 2.598)) for s in (0.0, 1.2) for z in (0.0, 2.6)]
        ext, n = J.extensoes(caixas)
        self.assertEqual(n, 4)
        self.assertAlmostEqual(ext[0][(1, 1)], 0.001, places=6)
        self.assertAlmostEqual(ext[0][(2, 1)], 0.001, places=6)

    def test_not_joints(self):
        # an opening (1 m), battens 35 cm apart, touching pieces, pieces in another plane, a piece beside another
        # only at its corner: nothing to close
        casos = [
            [tabua(0.0, 0.5), tabua(1.5, 2.0)],
            [((0.0, 0.0, 0.0), (5.0, 0.035, 0.0375)), ((0.0, 0.0, 0.35), (5.0, 0.035, 0.3875))],
            [tabua(0.0, 0.129), tabua(0.129, 0.258)],
            [tabua(0.0, 0.129), tabua(0.135, 0.264, y0=0.05)],
            [tabua(0.0, 0.129, 0.0, 1.0), tabua(0.135, 0.264, 1.0, 2.0)],
        ]
        for caixas in casos:
            self.assertEqual(J.extensoes(caixas)[1], 0, caixas)

    def test_staggered_rows_half_a_sheet(self):
        # XPS rows staggered by half a board (1,25 m boards, 1,5 mm joints): each board meets two above it
        baixo = [((0.0, s, 0.0), (0.06, s + 1.2485, 0.5985)) for s in (0.0, 1.25)]
        cima = [((0.0, s, 0.6), (0.06, s + 1.2485, 1.1985)) for s in (-0.625, 0.625, 1.875)]
        ext, n = J.extensoes(baixo + cima)
        self.assertEqual(n, 1 + 2 + 4)  # one joint below, two above, four between the rows
        self.assertAlmostEqual(ext[0][(2, 1)], 0.00075, places=6)

    def test_only_plates(self):
        # a stud (thick) or a beam is not a plate
        self.assertEqual(J.placas([((0, 0, 0), (0.075, 0.15, 2.5))]), {})
        self.assertEqual(J.placas([tabua(0, 0.129)]), {0: 1})

    def test_narrow_strip_closes_with_its_neighbour(self):
        # Torres Vedras, south façade: a board split into 93 mm + 39 mm, then a 6 mm joint to the next board. The
        # 39 mm strip is thin along x and y: its thickness axis is its neighbours' (y)
        caixas = [tabua(11.9316, 12.022), tabua(12.022, 12.0606), tabua(12.0666, 12.1956)]
        self.assertEqual(J.placas(caixas)[1], 1)
        ext, n = J.extensoes(caixas)
        self.assertEqual(n, 1)
        self.assertAlmostEqual(ext[1][(0, 1)], 0.003, places=6)
        self.assertAlmostEqual(ext[2][(0, -1)], 0.003, places=6)


if __name__ == "__main__":
    unittest.main()
