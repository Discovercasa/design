"""House shapes of the configurator: the foundation base from a shape and its m² (user 2026-10-20: "o cliente a
escolher primeira a shape da casa e só depois o metros quadrados"). Pure Python.

Every shape is an outline with right angles only (the method and the builder know walls along X / Y only), given
counter-clockwise from its lower-left corner, metres, X to the right (east), Y up (north). The default proportions
are ours; the client then moves each side (configurator spec §2, step 2).
"""
import math

PASSO = 0.05  # sides rounded to 5 cm


def _r(v):
    return round(round(v / PASSO) * PASSO, 3)


def area(contorno):
    """Area of an outline (shoelace), m²; positive when counter-clockwise."""
    n = len(contorno)
    return sum(contorno[i][0] * contorno[(i + 1) % n][1] - contorno[(i + 1) % n][0] * contorno[i][1] for i in range(n)) / 2


# shape: (outline for a unit size a, parameter names) — a = the house depth
FORMAS = {
    "retangular": "Retangular",
    "L": "Formato em L",
    "T": "Formato em T",
    "U": "Formato em U",
}


def contorno(forma, area_m2, proporcoes=None):
    """The outline of a shape with the given area. proporcoes (optional, fractions of the depth a): retangular
    {"comprimento"}; L {"comprimento", "recorte_x", "recorte_y"} (the corner cut out at the south-east, as the wing
    of Torres Vedras); T {"comprimento", "haste_x", "haste_y"} (the bar to the north, the stem to the south); U
    {"comprimento", "patio_x", "patio_y"} (the courtyard open to the north)."""
    p = dict(proporcoes or {})

    def forma_unitaria(a):
        C = p.get("comprimento", 1.6) * a
        if forma == "retangular":
            return [(0, 0), (C, 0), (C, a), (0, a)]
        if forma == "L":
            rx, ry = p.get("recorte_x", 0.4) * C, p.get("recorte_y", 0.35) * a
            return [(0, 0), (C - rx, 0), (C - rx, ry), (C, ry), (C, a), (0, a)]
        if forma == "T":
            hx, hy = p.get("haste_x", 0.4) * C, p.get("haste_y", 0.45) * a
            x0 = (C - hx) / 2
            return [(x0, 0), (x0 + hx, 0), (x0 + hx, hy), (C, hy), (C, a), (0, a), (0, hy), (x0, hy)]
        if forma == "U":
            px, py = p.get("patio_x", 0.4) * C, p.get("patio_y", 0.45) * a
            x0 = (C - px) / 2
            return [(0, 0), (C, 0), (C, a), (x0 + px, a), (x0 + px, a - py), (x0, a - py), (x0, a), (0, a)]
        raise ValueError(f"forma desconhecida: {forma} (há {', '.join(FORMAS)})")

    a = math.sqrt(area_m2 / area(forma_unitaria(1.0)))
    pts = [(_r(x), _r(y)) for x, y in forma_unitaria(a)]
    xmin = min(x for x, _ in pts)
    return [[round(x - xmin, 3), y] for x, y in pts]
