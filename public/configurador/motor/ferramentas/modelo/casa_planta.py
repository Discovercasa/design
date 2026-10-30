"""Builder: DiscoverCasa house from the walls of an ARCHITECTURE plan (single storey). Pure Python.

    python ferramentas/modelo/casa_planta.py "<project>/modelos/<type>/config.json" [--saida FILE]

Input: the walls and openings extracted by planta_arquitetura.py (config "planta") + the config. Output: a
geometry JSON of the same shape as estrutura_dc.py's (modules with their members, world pieces in
"estrutura_extra"), so camadas.py, build_casa.py, validar.py and quantidades.py work unchanged.

DiscoverCasa method (conhecimento/sistema-construtivo.md; standard in sistema_construtivo.json "estrutura"):
  - exterior walls: 110 frame placed so that frame + OSB 15 + Pladur end on the architect's inner face
    (rooms keep their size); interior walls: 75 frame on the architect's centre line;
  - walls along X run through the corners, walls along Y stop against them; interior walls stop at the
    frame face of the wall they meet;
  - every wall divided into modules by divisor_modulos.py — the company's way read from D2503 Módulos: whole bays of
    the 40 cm grid, each opening inside one module, a pier between close openings, no joint where another wall
    meets, factory modules normally <= 3 m (user 2026-10-19), longer ones built on site; config `modulos.divisor`:
    false restores the old split (<= `modulos.comprimento_max` from one end); `modulos_reais` uses the company's own
    modules instead;
  - module height from the clear height: floor finish + clear height + ceiling (suspension, perfis,
    Pladur) = underside of the ceiling beams; afinação + amarração (exterior) / afinação 110x75 (interior)
    on top; vigas de apoio ao teto 220x75 down the slope at <= 1 m; prumos + vigas de apoio à cobertura
    110x75 give the slope; the roof is hidden by a framed parapet (platibanda) on the exterior walls;
  - interior doors: rough opening `estrutura.porta_interior` (0,87 x 2,03) centred on the architect's door.
As built at Torres Vedras (DiscoverCasa roof drawing D2503, Construção Torres Vedras/docs/cobertura-D2503.md),
selected in the config: `paredes.exterior = "face_exterior"` puts the modules' outer face on the architect's
outer face (the foundation line); `cobertura.estrutura = "lameladas"`: amarração 11x7.5 on the inner face,
glulam beams 20x10 between the modules' inner faces on the ring (never through them), modules framed to the amarração with their studs
running on into the parapet, madres 11x7.5 on prumos (ridge pair; the longest slope's gutter madre on the
lameladas), hidden gutters on packing falling to outlets at their ends (`cobertura.caleiras`).
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.comum import pasta_trabalho  # noqa: E402
from ferramentas.modelo.camadas import R, fundir, prisma, teto_sob_anel  # noqa: E402
from ferramentas.modelo.divisor_modulos import dividir, juntas as juntas_divisor, parametros as parametros_divisor  # noqa: E402
from ferramentas.modelo.estrutura_dc import emoldurar, membro, ret  # noqa: E402
from ferramentas.modelo import telhado as telhado_avista, telhado_estrutura  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent


def rect(w, c0=None, c1=None):
    """Plan rectangle (x0, x1, y0, y1) of a wall given its across-the-wall interval."""
    c0 = w["c"] - w["espessura"] / 2 if c0 is None else c0
    c1 = w["c"] + w["espessura"] / 2 if c1 is None else c1
    return (w["s0"], w["s1"], c0, c1) if w["eixo"] == "x" else (c0, c1, w["s0"], w["s1"])


def dentro(px, py, r, tol=0.03):
    return r[0] - tol <= px <= r[1] + tol and r[2] - tol <= py <= r[3] + tol


def juntas(a, b, aberturas, lmax, folga=0.10):
    """Module joints along [a, b]: modules <= lmax, never within `folga` of an opening; a short last module
    is avoided by sharing the last two equally."""
    def livre(s):
        return all(not (o0 - folga < s < o1 + folga) for o0, o1 in aberturas)

    pts, s = [a], a
    while b - s > lmax + 1e-6:
        j = s + lmax
        while not livre(j) and j > s + 0.6:
            j -= 0.01
        if not livre(j):  # opening wider than a module: the joint goes after it
            j = s + lmax
            while not livre(j) and j < b:
                j += 0.01
        pts.append(round(j, 4))
        s = j
    pts.append(b)
    if len(pts) >= 3 and pts[-1] - pts[-2] < 0.6:
        m = (pts[-3] + pts[-1]) / 2
        if livre(m):
            pts[-2] = round(m, 4)
    return pts


def desloca(poly, d):
    """Orthogonal outline offset outward by d (the frame outline -> the finished faces)."""
    n = len(poly)
    area2 = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sg = 1 if area2 > 0 else -1

    def nrm(p, q):  # outward normal of the edge p -> q
        dx, dy = q[0] - p[0], q[1] - p[1]
        lg = math.hypot(dx, dy) or 1.0
        return sg * dy / lg, -sg * dx / lg

    out = []
    for i in range(n):
        n1, n2 = nrm(poly[i - 1], poly[i]), nrm(poly[i], poly[(i + 1) % n])
        if abs(n1[0] * n2[0] + n1[1] * n2[1]) > 0.5:  # collinear vertex
            n2 = (0.0, 0.0)
        out.append((poly[i][0] + d * (n1[0] + n2[0]), poly[i][1] + d * (n1[1] + n2[1])))
    return out


def dentro_x(poly, y):
    """x intervals of an orthogonal outline at height y (scanline)."""
    xs = sorted(p[0] for p, q in zip(poly, poly[1:] + poly[:1])
                if abs(p[0] - q[0]) < 1e-9 and min(p[1], q[1]) <= y < max(p[1], q[1]))
    return list(zip(xs[0::2], xs[1::2]))


def livres(a, b, ocupados, minimo=0.05):
    """Parts of [a, b] outside the intervals `ocupados`."""
    res = [(a, b)]
    for o0, o1 in ocupados:
        novo = []
        for r0, r1 in res:
            if o1 <= r0 or o0 >= r1:
                novo.append((r0, r1))
                continue
            if o0 > r0:
                novo.append((r0, o0))
            if o1 < r1:
                novo.append((o1, r1))
        res = novo
    return [(r0, r1) for r0, r1 in res if r1 - r0 >= minimo]

def contorno_estrutura(cont, exts):
    """Orthogonal outline (architect's outer faces) -> outline of the exterior frames' outer faces."""
    n = len(cont)
    lados = []
    for i in range(n):
        (xa, ya), (xb, yb) = cont[i], cont[(i + 1) % n]
        hor = abs(ya - yb) < 1e-6
        c, s0, s1 = (ya, min(xa, xb), max(xa, xb)) if hor else (xa, min(ya, yb), max(ya, yb))
        novo = c
        for w in exts:
            if (w["eixo"] == "x") != hor:
                continue
            face_arq = w["c"] + w["lado_exterior"] * w["espessura"] / 2
            if abs(face_arq - c) < 0.03 and min(w["s1"], s1) - max(w["s0"], s0) > 0.1:
                novo = w["f1"] if w["lado_exterior"] > 0 else w["f0"]
                break
        lados.append((hor, novo))
    out = []
    for i in range(n):  # vertex i joins side i-1 and side i (one horizontal, one vertical)
        h1, c1 = lados[i - 1]
        h2, c2 = lados[i]
        x = c2 if not h2 else c1
        y = c2 if h2 else c1
        out.append([round(x, 4), round(y, 4)])
    return out


def niveis_teto(cfg, S, E):
    """(finished floor, ceiling build-up, underside of the ceiling beams, top of the ceiling beams, eaves line of an
    exposed roof = top of the eave purlin lying on the beams) — the heights the roof starts from."""
    T = S["tetos"]
    teto_plano = T["suspensao"]["folga"] + T["perfis"]["altura"] + T["acabamento"]["espessura"]
    fin = S["pavimentos"]["piso0"]["acabado_z"]
    nv = cfg["niveis"]
    z_teto = nv.get("teto_estrutura") or (fin + nv["pe_direito"] + teto_plano)
    lam = E["lameladas"] if cfg["cobertura"].get("estrutura") == "lameladas" else None
    z_vig = z_teto + (lam["altura"] if lam else E["vigas_teto"]["altura"])
    return fin, teto_plano, z_teto, z_vig, z_vig + S["cobertura"]["vigas_apoio"]["altura"]


def cobertura_avista(T, z_e, z_vig, hv, vt, pn_esp, Cc, encostos=()):
    """G["cobertura"] of an exposed roof: the faces and lines of telhado.py at their real heights (z = the top of the
    purlins = the underside of the panels), the gables standing over a lower roof ("encostos": clad above it), plus
    the single-ridge keys the older readers expect."""
    faces = [{**f, "z0": round(f["z0"] + z_e, 5), "plano": list(f["plano"])} for f in T["faces"]]
    linhas = [{**l, "p0": [l["p0"][0], l["p0"][1], round(l["p0"][2] + z_e, 4)],
               "p1": [l["p1"][0], l["p1"][1], round(l["p1"][2] + z_e, 4)]} for l in T["linhas"]]
    z_cume = round(z_e + T["z_max"], 4)
    m = T["retangulos"][0]
    return {"sistema": "discovercasa", "tipo": "a_vista", "forma": Cc.get("forma", "duas_aguas"),
            "inclinacao": round(T["inclinacao_graus"], 3), "faces": faces, "linhas": linhas, "z_beirado": round(z_e, 4),
            "retangulos": [{**r, "planos": [list(p) for p in r["planos"]]} for r in T["retangulos"]],
            "t": round(T["t"], 6),
            "beirado": T["beirado"], "empena": T["empena"], "encostos": list(encostos),
            "cumeeira_y": round((m["y0"] + m["y1"]) / 2, 4), "cumeeira_z": z_cume, "plano_z_cume": z_cume,
            "altura_viga": hv, "apoio_z": {"N": z_vig, "S": z_vig}, "vigas_teto_x": [], "vigas_teto_largura": vt["largura"],
            "telhados": [], "pendente_pct": round(T["t"] * 100, 2), "painel_espessura": pn_esp}


def construir(cfg, S, E, planta):
    L, D = planta["contorno"][1], planta["contorno"][3]
    ws = planta["paredes"]
    ext_c, int_c = E["exterior"], E["interior"]
    te, ti, pl = ext_c["espessura"], int_c["espessura"], E["placa"]
    I, T = S["interior"], S["tetos"]
    forro = I["osb"]["espessura"] + I["acabamento"]["espessura"]
    teto_plano = T["suspensao"]["folga"] + T["perfis"]["altura"] + T["acabamento"]["espessura"]
    fin = S["pavimentos"]["piso0"]["acabado_z"]
    nv = cfg["niveis"]
    # glulam roof beams (lameladas) as at Torres Vedras (D2503), else the standard ceiling beams 220x75
    lam = E["lameladas"] if cfg["cobertura"].get("estrutura") == "lameladas" else None
    z_teto = nv.get("teto_estrutura") or (fin + nv["pe_direito"] + teto_plano)  # underside of the ceiling beams
    topo_ext = E["afinacao_exterior"]["altura"] + E["amarracao"]["altura"]
    topo_int = E["afinacao_interior"]["altura"]
    H_ext, H_int = z_teto - topo_ext, z_teto - topo_int
    if cfg.get("_modulos"):  # interior module height from the module drawings (TV D2503: 2,53)
        H_int = max([m["altura"] for m in cfg["_modulos"] if m["tipo"] == "interior"] or [H_int])
    vt = E["vigas_teto"]
    z_vig = z_teto + (lam["altura"] if lam else vt["altura"])
    dH_int = 0.0
    # a hidden roof: the exterior modules in one piece to the parapet top, the amarração as a ring on their inner face,
    # the ceiling beams on it inside, against the modules (never through them — user 2026-10-21) (D2503 with lameladas; user 2026-10-21 for every hidden roof, 22x7,5
    # beams too: "sim exatamente os módulos vao inteiros ate ao topo da platibanda")
    anel = bool(lam) or (cfg["cobertura"].get("tipo") == "platibanda" and E.get("platibanda_modulos_inteiros", True))
    if anel:  # the exterior modules run on past the ceiling beams (pockets) into the parapet: one piece
        H_ext = z_vig
        wl, ama = (lam or vt)["largura"], E["lameladas"]["amarracao"]
        if (cfg.get("modulos_reais") or {}).get("interior_a_medida_da_amarracao"):
            # user 2026-10-19: "Nós fazemos os módulos de forma a ficarem à medida certa das vigas amarração" — the
            # interior module + its amarração 11x7,5 reach the lameladas exactly (no packing), the amarração at the
            # level of the exterior ring
            dH_int = (z_teto - ama["altura"]) - H_int
            H_int = z_teto - ama["altura"]
    pi = E["porta_interior"]
    A = cfg.get("aberturas", {})

    # ------------------------------------------------------------------ frame line of every wall
    ref_ext = (cfg.get("paredes") or {}).get("exterior", "face_interior")
    for w in ws:
        if w["exterior"] and ref_ext == "face_exterior":
            # the module's outer face on the architect's outer face = the foundation line (D2503: "Dimensão
            # da fundação e módulos"); the cladding lies outside it
            sg = w["lado_exterior"]
            f_out = w["c"] + sg * w["espessura"] / 2
            w["f0"], w["f1"] = sorted((f_out, f_out - sg * te))
            w["t"] = te
        elif w["exterior"]:
            sg = w["lado_exterior"]
            dentro_ = w["c"] - sg * w["espessura"] / 2          # architect's inner face
            f_in = dentro_ + sg * forro
            w["f0"], w["f1"] = sorted((f_in, f_in + sg * te))
            w["t"] = te
        else:
            w["f0"], w["f1"] = w["c"] - ti / 2, w["c"] + ti / 2
            w["t"] = ti
        w["fc"] = (w["f0"] + w["f1"]) / 2
        w["a"], w["b"] = w["s0"], w["s1"]

    # ------------------------------------------------------------------ the company's real modules (optional)
    # Each module of the module drawings goes to the wall on its line; the wall's frame, ends and modules are
    # then the drawing's (no placement, corner or joint rules of the builder): "como foram feitos".
    reais = cfg.get("_modulos")
    if reais:
        for w in ws:
            w["mods"] = []
        for m in reais:
            x0, x1, y0, y1 = m["pegada"]
            a_, b_, c0_, c1_ = (x0, x1, y0, y1) if m["eixo"] == "x" else (y0, y1, x0, x1)
            best = None
            for w in ws:
                if w["eixo"] != m["eixo"] or w["exterior"] != (m["tipo"] == "exterior"):
                    continue
                ov = min(b_, w["s1"] + 0.3) - max(a_, w["s0"] - 0.3)
                d = abs((c0_ + c1_) / 2 - w["c"])
                if ov > 0.05 and d < 0.25 and (best is None or d < best[0]):
                    best = (d, w)
            if best is None:
                print(f"aviso: módulo {m['id']} sem parede da planta na sua linha")
                continue
            best[1]["mods"].append(m)
        for w in ws:
            if not w["mods"]:
                continue
            k_ = 0 if w["eixo"] == "x" else 2
            w["mods"].sort(key=lambda m: m["pegada"][k_])
            f0_, f1_ = (w["mods"][0]["pegada"][2:4] if w["eixo"] == "x" else w["mods"][0]["pegada"][0:2])
            w["f0"], w["f1"], w["fc"], w["t"] = f0_, f1_, (f0_ + f1_) / 2, round(f1_ - f0_, 4)
            w["a"], w["b"] = w["mods"][0]["pegada"][k_], w["mods"][-1]["pegada"][k_ + 1]
            w["aberturas"] = [{"s0": round(m["pegada"][k_] + o["u"][0], 4), "s1": round(m["pegada"][k_] + o["u"][1], 4),
                               "tipo": o["tipo"]} for m in w["mods"] for o in m["aberturas"]]

    def frame_rect(w):
        return rect({"eixo": w["eixo"], "s0": w["a"], "s1": w["b"], "c": w["fc"], "espessura": w["t"]})

    # ------------------------------------------------------------------ wall ends
    def rect_atual(q):
        return rect({"eixo": q["eixo"], "s0": q["a"], "s1": q["b"], "c": q["c"], "espessura": q["espessura"]})

    # two interior walls meeting end to end (a room's corner — user 2026-10-22: "o fim de uma das paredes pelo menos
    # deve fazer 90º perfeitamente"): as at the outside corners, the X wall runs through to the Y wall's far face and
    # the Y wall stops against it (each stopping at the other's face left the corner's square empty)
    cantos_int = {}
    ints = [w for w in ws if not w["exterior"] and not w.get("mods")]
    for w in ints:
        for fim, s_fim in (("a", w["s0"]), ("b", w["s1"])):
            px, py = (s_fim, w["c"]) if w["eixo"] == "x" else (w["c"], s_fim)
            corpo = 1 if fim == "a" else -1
            for q in ints:
                if q is w or q["eixo"] == w["eixo"]:
                    continue
                for s_q in (q["s0"], q["s1"]):
                    qx, qy = (s_q, q["c"]) if q["eixo"] == "x" else (q["c"], s_q)
                    if abs(qx - px) < 0.03 and abs(qy - py) < 0.03:
                        cantos_int[(id(w), fim)] = q["c"] + (-corpo if w["eixo"] == "x" else corpo) * q["t"] / 2

    ordem = [w for w in ws if w["exterior"] and w["eixo"] == "x"] + \
        [w for w in ws if w["exterior"] and w["eixo"] == "y"] + [w for w in ws if not w["exterior"]]
    for w in ordem:
        if w.get("mods"):
            continue  # ends as in the module drawings
        for fim in ("a", "b"):
            if (id(w), fim) in cantos_int:
                w[fim] = cantos_int[(id(w), fim)]
                continue
            s_fim = w["s0"] if fim == "a" else w["s1"]
            px, py = (s_fim, w["c"]) if w["eixo"] == "x" else (w["c"], s_fim)
            corpo = 1 if fim == "a" else -1  # direction from the end into the wall
            atravessa = w["exterior"] and w["eixo"] == "x"  # X exterior walls run through the corners
            novo = None
            for q in ws:
                if q is w or q["eixo"] == w["eixo"] or (w["exterior"] and not q["exterior"]):
                    continue  # an exterior wall ends on exterior walls only (not on an interior wall at its corner)
                # the architect leaves the square of a re-entrant corner out of both walls: look further
                tol = 0.3 if (w["exterior"] and q["exterior"]) else 0.03
                if not dentro(px, py, rect_atual(q), tol):
                    continue
                f_perto, f_longe = (q["f1"], q["f0"]) if corpo > 0 else (q["f0"], q["f1"])
                if atravessa and q["exterior"]:
                    cand = f_longe
                    novo = cand if novo is None else (min(novo, cand) if corpo > 0 else max(novo, cand))
                else:
                    cand = f_perto
                    novo = cand if novo is None else (max(novo, cand) if corpo > 0 else min(novo, cand))
            if novo is not None:
                w[fim] = novo

    # ------------------------------------------------------------------ lameladas: positions
    # D2503: wall to wall (outer faces of the walls they cross), the length between the end walls' axes in
    # equal bays <= espacamento_max (Torres Vedras: 17,39 in 19 bays of 0,915); the zones of the config say
    # which walls each one bears on
    exts = [w for w in ws if w["exterior"]]

    def face_interior(lado, x0, x1, y0, y1):
        """Inner frame face of the exterior wall along one side of the rectangle (None if no wall there)."""
        best = None
        for w in exts:
            if lado in ("S", "N") and w["eixo"] == "x":
                if abs(w["c"] - (y0 if lado == "S" else y1)) < 0.3 and min(w["b"], x1) - max(w["a"], x0) > 0.3:
                    f = w["f1"] if lado == "S" else w["f0"]
                    best = f if best is None else (max(best, f) if lado == "S" else min(best, f))
            if lado in ("O", "E") and w["eixo"] == "y":
                if abs(w["c"] - (x0 if lado == "O" else x1)) < 0.3 and min(w["b"], y1) - max(w["a"], y0) > 0.3:
                    f = w["f1"] if lado == "O" else w["f0"]
                    best = f if best is None else (max(best, f) if lado == "O" else min(best, f))
        return best

    def face_dentro(w):
        """Inner frame face of an exterior wall."""
        return w["f1"] if w["lado_exterior"] < 0 else w["f0"]

    def apoio_vigas(ys_, y_lado, baixo):
        """Where the ceiling beams end on the wall at the line y_lado: on a hidden roof at the modules' inner face, on
        the amarração ring, never through the module (user 2026-10-21: "essas vigas ficam por dentro e encostadas as
        da estrutura não atravessam … quanto muito é feito o entalhe nas vigas de 22x7,5 de forma a ficarem do
        comprimento perfeito para encaixar de um lado e do outro"); else over the wall to its outer face."""
        ws_ = [w for w in ys_ if abs(w["c"] - y_lado) < 0.3]
        if anel:
            fs = [face_dentro(w) for w in ws_]
            return (max(fs) if baixo else min(fs)) if fs else y_lado
        fs = [w["f0"] if baixo else w["f1"] for w in ws_]
        return (min(fs) if baixo else max(fs)) if fs else y_lado

    def vigas_220():
        """Ceiling beams 220x75 at <= 1 m in the config's zones (beam centres from wall face to wall face), from the
        wall they bear on at one end to the one at the other (apoio_vigas): [(zone, i, x, y0, y1)]."""
        out = []
        for k_z, (zx0, zx1, zy0, zy1) in enumerate(cfg["cobertura"]["vigas_teto"], 1):
            fx0 = face_interior("O", zx0, zx1, zy0, zy1)
            fx1 = face_interior("E", zx0, zx1, zy0, zy1)
            x_a = (fx0 if fx0 is not None else zx0) + vt["largura"] / 2
            x_b = (fx1 if fx1 is not None else zx1) - vt["largura"] / 2
            ys = [w for w in exts if w["eixo"] == "x" and min(w["b"], zx1) - max(w["a"], zx0) > 0.3]
            ya, yb = apoio_vigas(ys, zy0, True), apoio_vigas(ys, zy1, False)
            nvg = max(1, math.ceil((x_b - x_a) / vt["espacamento"] - 1e-9))
            out += [(k_z, i, x_a + (x_b - x_a) * i / nvg, ya, yb) for i in range(nvg + 1)]
        return out

    # the ceiling beams of a hidden roof: they end at the modules' inner face (apoio_vigas), so the exterior modules keep
    # whole studs — the pockets of continuar() only arise for beams that would run through a wall
    lams = []
    if anel and not lam:
        lams = [(round(xv, 4), ya, yb) for _, _, xv, ya, yb in vigas_220()]
    if lam:
        eY = [w for w in exts if w["eixo"] == "y"]
        xL, xR = min(w["fc"] for w in eY), max(w["fc"] for w in eY)
        nb = max(1, math.ceil((xR - xL) / lam["espacamento_max"] - 1e-9))
        for i in range(1, nb):
            xv = round(xL + (xR - xL) * i / nb, 4)
            zona = next((z for z in cfg["cobertura"]["vigas_teto"] if z[0] - 1e-6 <= xv <= z[1] + 1e-6), None)
            if zona is None:
                continue
            ys_ = [w for w in exts if w["eixo"] == "x" and w["a"] - 0.01 <= xv <= w["b"] + 0.01]
            lams.append((xv, apoio_vigas(ys_, zona[2], True), apoio_vigas(ys_, zona[3], False)))
    continuos, juntas_w = {}, {}

    def continuar(ms, W, H, Hf, m0, w, k):
        """Exterior module of a glulam roof: no top plate, the studs run on to the module top (they go on in the
        parapet module above), pockets where a beam would cross the wall (none on a hidden roof since 2026-10-21: the beams end at the inner face)."""
        res, vert = [], []
        for m in ms:
            if m["tipo"] == "Travessa superior":
                continue
            us, vs = [q[0] for q in m["poly"]], [q[1] for q in m["poly"]]
            u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
            if v1 >= Hf - pl - 0.002 and v1 - v0 > u1 - u0:
                m = membro(m["tipo"], m["section"], ret(u0, u1, v0, H))
                v1 = H
                vert.append((u0, u1, m["tipo"], m["section"]))
            res.append(m)
        continuos[(w["id"], k)] = vert
        if w["eixo"] != "x":
            return res
        bolsas = [(xv - wl / 2 - m0, xv + wl / 2 - m0) for xv, ya, yb in lams
                  if ya - 0.01 <= w["f0"] and w["f1"] <= yb + 0.01 and -wl / 2 < xv - m0 < W + wl / 2]
        out_ = []
        for m in res:
            us, vs = [q[0] for q in m["poly"]], [q[1] for q in m["poly"]]
            u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
            if not (any(b0 < u1 - 1e-6 and u0 + 1e-6 < b1 for b0, b1 in bolsas) and v1 > z_teto + 1e-6):
                out_.append(m)
            elif v0 < z_teto - 0.01:
                out_.append(membro(m["tipo"], m["section"], ret(u0, u1, v0, z_teto)))
        return out_

    # ------------------------------------------------------------------ openings (elevation of each wall)
    def aberturas_de(w):
        out = []
        extras = {o["i"]: o for o in A.get("por_parede", {}).get(w["id"], [])}
        for i, o in enumerate(w["aberturas"]):
            tipo = extras.get(i, {}).get("tipo", o["tipo"])
            s0, s1 = o["s0"], o["s1"]
            if not w["exterior"] and tipo == "porta":
                m = (s0 + s1) / 2
                s0, s1 = m - pi["largura"] / 2, m + pi["largura"] / 2
                z0, z1 = 0.0, fin + pi["altura"]
            elif tipo == "porta":
                z0, z1 = 0.0, fin + A.get("porta_exterior", {}).get("altura", 2.20)
            else:
                jn = A.get("janela", {"peitoril": 1.0, "topo": 1.75})
                z0, z1 = fin + jn["peitoril"], fin + jn["topo"]
            if i in extras and "z" in extras[i]:
                z0, z1 = fin + extras[i]["z"][0], fin + extras[i]["z"][1]
            # last: the drawing's own kind (a door has a swing; a sliding window to the floor stays "janela")
            out.append([s0, s1, z0, z1, "porta" if z0 <= fin + 1e-6 else "janela", o["tipo"]])  # at the floor = a door
        return out

    # ------------------------------------------------------------------ modules
    lmax = cfg.get("modulos", {}).get("comprimento_max", 3.0)
    vg = E["verga_grande"]
    alcados, paineis = {}, []
    cantos = set()
    for w in ws:  # exterior corners: ends of exterior walls
        if w["exterior"]:
            cantos.add((w["id"], "a"))
            cantos.add((w["id"], "b"))
    reais_plat = {}
    usar_divisor = cfg.get("modulos", {}).get("divisor", True)
    P_div = {True: parametros_divisor(E, True), False: parametros_divisor(E, False)}
    if "comprimento_max" in cfg.get("modulos", {}):  # the project's factory limit (perguntas-por-obra Q6)
        for p_ in P_div.values():
            p_["max"] = cfg["modulos"]["comprimento_max"]
            p_["preferido"] = min(p_["preferido"], p_["max"])

    def juncoes_de(w):
        """Walls meeting w (an end on one of its faces), away from its ends: [[centre, thickness]]."""
        out = []
        for q in ws:
            if q is w or q["eixo"] == w["eixo"] or not (w["a"] + 0.15 < q["fc"] < w["b"] - 0.15):
                continue
            if any(abs(s - f) < 0.03 for s in (q["a"], q["b"]) for f in (w["f0"], w["f1"])):
                out.append([round(q["fc"], 4), round(q["t"], 4)])
        return out

    em_obra = {}
    avisos_div, movidas = [], []
    for w in ws:
        cls = ext_c if w["exterior"] else int_c
        if w.get("mods"):  # the real modules, members as drawn
            k_ = 0 if w["eixo"] == "x" else 2
            for k, m in enumerate(w["mods"], 1):
                m0, W, Hm = m["pegada"][k_], m["comprimento"], m["altura"]
                fx = W / m.get("comprimento_alcado", W) if abs(m.get("comprimento_alcado", W) - W) > 0.005 else 1.0
                ms = [membro(x["tipo"], x["seccao"], ret(max(0.0, x["u"][0] * fx), min(W, x["u"][1] * fx),
                                                          max(0.0, x["v"][0]), min(Hm, x["v"][1])))
                      for x in m["membros"]]  # (clamped: the drawing's rounding)
                if not w["exterior"] and abs(dH_int) > 0.001:  # made to the amarração: top plate up, studs longer
                    lim_t = Hm - 0.036
                    ms2 = []
                    for mm in ms:
                        us, vs = [q[0] for q in mm["poly"]], [q[1] for q in mm["poly"]]
                        v0, v1 = min(vs), max(vs)
                        if v0 >= lim_t:
                            v0, v1 = v0 + dH_int, v1 + dH_int
                        elif v1 >= lim_t - 0.002:
                            v1 += dH_int
                        ms2.append(membro(mm["tipo"], mm["section"], ret(min(us), max(us), v0, v1)))
                    ms, Hm = ms2, Hm + dH_int
                loc = [[round(o["u"][0] * fx, 4), round(o["u"][1] * fx, 4), o["v"][0], o["v"][1], o["tipo"]]
                       for o in m["aberturas"]]
                ms_fab, bolsas = list(ms), []  # as made in the factory (whole studs; the notch is cut on site)
                if anel and w["exterior"] and w["eixo"] == "x":  # pockets where a beam would cross the wall (none since the beams end inside)
                    bolsas = [(xv - wl / 2 - m0, xv + wl / 2 - m0) for xv, ya, yb in lams
                              if ya - 0.01 <= w["f0"] and w["f1"] <= yb + 0.01 and -wl / 2 < xv - m0 < W + wl / 2]
                    novo = []
                    for mm in ms:
                        us, vs = [q[0] for q in mm["poly"]], [q[1] for q in mm["poly"]]
                        u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
                        if any(b0 < u1 - 1e-6 and u0 + 1e-6 < b1 for b0, b1 in bolsas) and v0 < z_vig and v1 > z_teto:
                            if v0 < z_teto - 0.01:
                                novo.append(membro(mm["tipo"], mm["section"], ret(u0, u1, v0, z_teto)))
                            if v1 > z_vig + 0.01:
                                novo.append(membro(mm["tipo"], mm["section"], ret(u0, u1, z_vig, v1)))
                        else:
                            novo.append(mm)
                    ms = novo
                if w["exterior"] and anel:  # the parapet part, for the layers only (structure is in this module)
                    reais_plat[(w["id"], k)] = (m0, W, [membro(mm["tipo"], mm["section"],
                                                               ret(min(q[0] for q in mm["poly"]), max(q[0] for q in mm["poly"]),
                                                                   max(min(q[1] for q in mm["poly"]), z_vig) - z_vig,
                                                                   max(q[1] for q in mm["poly"]) - z_vig))
                                                        for mm in ms if max(q[1] for q in mm["poly"]) > z_vig + 0.01])
                nome = f"{'PE' if w['exterior'] else 'PI'} {w['id']}.{k} ({m['nome']})"
                chave = f"{nome}__dc"
                alcados[chave] = {"W": W, "H": Hm, "members": ms, "frame_u0": 0.0, "frame_u1": W,
                                  "section": cls["seccao_montante"], "aberturas": loc, "sistema": "discovercasa",
                                  "modulo": m["nome"], "membros_fabrico": ms_fab,
                                  **({"em_obra": True} if W > P_div[w["exterior"]]["max"] + 1e-6 else {}),
                                  "entalhes": [[round(max(0.0, b0), 4), round(min(W, b1), 4), round(z_teto, 4), round(z_vig, 4)]
                                               for b0, b1 in bolsas],
                                  "studs": sorted((mm["poly"][0][0] + mm["poly"][1][0]) / 2 for mm in ms if mm["tipo"] == "Montante")}
                org = [m0, w["fc"]] if w["eixo"] == "x" else [w["fc"], m0]
                p_ = {"nome": nome, "alcado": chave, "piso": 0, "tipo": "PE" if w["exterior"] else "PI",
                      "origem": [round(org[0], 4), round(org[1], 4), 0.0], "sentido": [1.0, 0.0] if w["eixo"] == "x" else [0.0, 1.0],
                      "espessura": w["t"], "encaixe": "-", "extra": 0, "exterior": w["exterior"], "modulo": m["nome"]}
                if w["exterior"]:
                    p_["fora"] = float(w["lado_exterior"] if w["eixo"] == "x" else -w["lado_exterior"])
                paineis.append(p_)
            continue
        H = H_ext if w["exterior"] else H_int
        # glulam roof: the module is framed (lintels, top) up to the amarração, its studs then run on past the
        # lameladas into the parapet module
        Hf = z_teto if (anel and w["exterior"]) else H
        abert = sorted(aberturas_de(w))
        if usar_divisor:
            res = dividir({"id": w["id"], "exterior": w["exterior"], "a": w["a"], "b": w["b"],
                           "fim_a": "canto" if (w["id"], "a") in cantos else "parede",
                           "fim_b": "canto" if (w["id"], "b") in cantos else "parede",
                           "aberturas": [[o[0], o[1], o[5]] for o in abert], "juncoes": juncoes_de(w)}, P_div[w["exterior"]])
            for o, (s0, s1) in zip(abert, res["aberturas"]):  # openings the divider had to move (pier, wall end)
                if abs(o[0] - s0) > 1e-4 or abs(o[1] - s1) > 1e-4:  # the configurator shows them moved
                    movidas.append({"parede": w["id"], "de": [round(o[0], 4), round(o[1], 4)], "para": [round(s0, 4), round(s1, 4)]})
                o[0], o[1] = s0, s1
            for aviso in res["avisos"]:
                print("divisor:", aviso)
                avisos_div.append(aviso)  # the configurator tells the client (an opening moved)
            pts = juntas_divisor(res)
            em_obra[w["id"]] = [m["obra"] for m in res["modulos"]]
        else:
            pts = juntas(w["a"], w["b"], [(o[0], o[1]) for o in abert], lmax)
        juntas_w[w["id"]] = pts
        for k, (m0, m1) in enumerate(zip(pts, pts[1:]), 1):
            W = m1 - m0
            loc = []
            for s0, s1, z0, z1, kind, _ in abert:
                if s0 >= m0 - 1e-6 and s1 <= m1 + 1e-6:
                    topo = Hf - pl - (vg["altura"] if s1 - s0 >= vg["vao_min"] else cls["padieira"])
                    v0 = 0.0 if kind == "porta" else max(z0, pl + cls["peitoril"] + 0.05)
                    loc.append([round(s0 - m0, 4), round(s1 - m0, 4), round(v0, 4), round(min(z1, topo), 4), kind])
            c0 = k == 1 and (w["id"], "a") in cantos
            c1 = k == len(pts) - 1 and (w["id"], "b") in cantos
            ms = emoldurar(0.0, W, Hf, loc, cls, E, c0, c1)
            if anel and w["exterior"]:
                ms = continuar(ms, W, H, Hf, m0, w, k)
            nome = f"{'PE' if w['exterior'] else 'PI'} {w['id']}.{k}"
            chave = f"{nome}__dc"
            alcados[chave] = {"W": W, "H": H, "members": ms, "frame_u0": 0.0, "frame_u1": W,
                              "section": cls["seccao_montante"], "aberturas": loc, "sistema": "discovercasa",
                              "studs": sorted((m["poly"][0][0] + m["poly"][1][0]) / 2 for m in ms if m["tipo"] == "Montante")}
            if (em_obra.get(w["id"]) or [False] * k)[k - 1]:
                alcados[chave]["em_obra"] = True  # longer than a factory module: "* Painel a executar em obra" (D2503)
            org = [m0, w["fc"]] if w["eixo"] == "x" else [w["fc"], m0]
            p = {"nome": nome, "alcado": chave, "piso": 0, "tipo": "PE" if w["exterior"] else "PI",
                 "origem": [round(org[0], 4), round(org[1], 4), 0.0], "sentido": [1.0, 0.0] if w["eixo"] == "x" else [0.0, 1.0],
                 "espessura": w["t"], "encaixe": "-", "extra": 0, "exterior": w["exterior"]}
            if w["exterior"]:  # outer side in panel terms: w = +1 is the left of +u (+y for X walls, -x for Y walls)
                p["fora"] = float(w["lado_exterior"] if w["eixo"] == "x" else -w["lado_exterior"])
            if w.get("faces"):  # the client's finish on each face (norte / sul, nascente / poente; an outside wall: its
                # inner face — user 2026-10-22): camadas.interior
                p["acabamentos"] = w["faces"]
            paineis.append(p)

    extra = []

    def peca(nome, col, sec, tipo, pecas, comp, vol, **props):
        extra.append({"nome": nome, "colecao": col, "material": f"Madeira {sec}", "pecas": pecas,
                      "props": {"seccao": sec, "tipo": tipo, "comprimento_m": round(comp, 3), "volume_m3": round(vol, 5), **props}})

    def caixa(x0, x1, y0, y1, z0_, z1_):
        return prisma([(x0, y0, z0_), (x1, y0, z0_), (x1, y1, z0_), (x0, y1, z0_)], (0, 0, z1_ - z0_))

    # ------------------------------------------------------------------ afinação / amarração
    af_e, am, af_i = E["afinacao_exterior"], E["amarracao"], E["afinacao_interior"]
    for w in ws:
        x0, x1, y0, y1 = frame_rect(w)
        comp = w["b"] - w["a"]
        if w["exterior"] and anel:
            # D2503: amarração 11x7.5 all round on the inner face of the modules, under the lameladas
            n_in = -w["lado_exterior"]
            f_in = w["f1"] if n_in > 0 else w["f0"]
            c0_, c1_ = sorted((f_in, f_in + n_in * ama["largura"]))
            segs = [(w["a"], w["b"])]
            for q in exts:
                if q is w or q["eixo"] == w["eixo"]:
                    continue
                qr = frame_rect(q)
                qa, qb = (qr[0], qr[1]) if w["eixo"] == "x" else (qr[2], qr[3])
                qc0, qc1 = (qr[2], qr[3]) if w["eixo"] == "x" else (qr[0], qr[1])
                if qc0 < c1_ - 1e-6 and c0_ + 1e-6 < qc1:
                    segs = [sg_ for a_, b_ in segs for sg_ in ((a_, min(b_, qa)), (max(a_, qb), b_)) if sg_[1] - sg_[0] > 0.01]
            for k_, (a_, b_) in enumerate(segs, 1):
                r_ = (a_, b_, c0_, c1_) if w["eixo"] == "x" else (c0_, c1_, a_, b_)
                peca(f"Amarração | {w['id']}" + (f".{k_}" if len(segs) > 1 else ""), "1.6", ama["seccao"],
                     "Viga de amarração (face interior)", [caixa(*r_, z_teto - ama["altura"], z_teto)], b_ - a_,
                     (b_ - a_) * ama["largura"] * ama["altura"])
        elif w["exterior"]:
            peca(f"Viga de afinação exterior | {w['id']}", "1.6", af_e["seccao"], "Viga de afinação exterior",
                 [caixa(x0, x1, y0, y1, H_ext, H_ext + af_e["altura"])], comp, comp * te * af_e["altura"])
            za = H_ext + af_e["altura"]
            peca(f"Viga de amarração | {w['id']}", "1.6", am["seccao"], "Viga de amarração",
                 [caixa(x0, x1, y0, y1, za, za + am["altura"])], comp, comp * te * am["altura"])
        else:
            # with lameladas the interior walls carry them too (user 2026-10-19: "por norma as vigas de apoio ao teto
            # apoiam-se nas paredes dos módulos interiores também"): the afinação reaches their underside
            topo_af = z_teto if lam else H_int + af_i["altura"]
            if lam and abs(topo_af - H_int - ama["altura"]) < 0.002:  # the module made to the amarração
                peca(f"Viga de amarração interior | {w['id']}", "1.6", ama.get("seccao", af_i["seccao"]),
                     "Viga de amarração (topo do módulo interior)",
                     [caixa(x0, x1, y0, y1, H_int, topo_af)], comp, comp * ti * (topo_af - H_int))
            else:
                peca(f"Viga de afinação | {w['id']}", "1.6", af_i["seccao"], "Viga de afinação interior",
                     [caixa(x0, x1, y0, y1, H_int, topo_af)], comp, comp * ti * (topo_af - H_int))

    # ------------------------------------------------------------------ roof: ceiling beams, posts, purlins
    # Ceiling beams 220x75 down the slope (along y), at <= 1 m, in the zones of the config (they bear on the
    # exterior walls at both ends); slopes ("aguas") from one ridge line along x, each down to its side, with
    # purlins 110x75 parallel to the ridge on posts standing on the beams.
    Cc = cfg["cobertura"]
    va = S["cobertura"]["vigas_apoio"]
    pr = E["prumos"]
    wv, hv = va["largura"], va["altura"]
    pn_esp = Cc.get("painel_espessura", 0.08)
    tan = Cc.get("inclinacao_pct", 5.0) / 100.0
    # a hidden roof in ONE slope (para_construtor, user 2026-10-28 "nós tentamos sempre só fazer uma água"): the slopes
    # ("aguas") all on the low side, each strip up to its own high wall ("y_topo"), no ridge
    uma_agua = bool(Cc.get("uma_agua"))

    def uniao(ivs):
        res = []
        for a, b in sorted(ivs):
            if res and a <= res[-1][1] + 0.01:
                res[-1][1] = max(res[-1][1], b)
            else:
                res.append([a, b])
        return res

    def dentro_da_casa(y, ags_):
        """A roof line at y (madre, purlin) runs, over the slopes that reach it, from the inner face of one exterior wall
        across it to the next — continuous where two slopes meet with no wall between them (the user's circled gap of
        2026-10-21: the slope of the main block stopped at the re-entrant wall's face above that wall)."""
        fs = sorted((face_dentro(w), w["lado_exterior"]) for w in exts
                    if w["eixo"] == "y" and w["a"] - 0.01 <= y <= w["b"] + 0.01)
        casa_ = []
        ini = None
        for x, lado_ in fs:
            if lado_ < 0:  # a wall with the outside to the west: the house starts at its inner face
                ini = x
            elif ini is not None:
                casa_.append((ini, x))
                ini = None
        bruto = uniao([tuple(a["x_bruto"]) for a in ags_])
        res = [(max(a0, b0), min(a1, b1)) for a0, a1 in casa_ for b0, b1 in bruto if min(a1, b1) - max(a0, b0) > 0.05]
        return uniao(res) if res else uniao([(a["x0"], a["x1"]) for a in ags_])


    def fechar_aguas(aguas):
        """Two strips side by side on one slope: where one stopped at a re-entrant wall's inner face and the other,
        open at that boundary, began at the boundary itself, a strip of the frame's width had no panel over it (the
        user's screenshots, 2026-10-28: "a cobertura nao está a cobrir a casa toda esta com gaps") — the open one
        runs on to that face (its panels end against the corner's other wall)."""
        for a in aguas:
            for b in aguas:
                if a is b or a["lado"] != b["lado"]:
                    continue
                if abs(a["x_bruto"][1] - b["x_bruto"][0]) < 1e-6:  # a west of b
                    if a["x1"] < a["x_bruto"][1] - 0.01 and abs(b["x0"] - b["x_bruto"][0]) < 1e-6:
                        b["x0"] = a["x1"]
                    elif b["x0"] > b["x_bruto"][0] + 0.01 and abs(a["x1"] - a["x_bruto"][1]) < 1e-6:
                        a["x1"] = b["x0"]
        return aguas

    avista = Cc.get("tipo") == "a_vista"
    T_av = None
    if avista:
        # An exposed sandwich-panel roof (cobertura à vista, user 2026-10-21: 2 águas the rule, 4 águas an option,
        # "várias águas" on L / T / U): the roof surface from the outline (telhado.py), its timber from
        # telhado_estrutura.py — the eave purlin right on the ceiling beams over the wall line
        T_av = telhado_avista.telhado(cfg["fundacao"]["contorno"], Cc.get("forma", "duas_aguas"),
                                      Cc.get("inclinacao_graus", math.degrees(math.atan(Cc.get("inclinacao_pct", 15.0) / 100))),
                                      Cc.get("beirado", S["cobertura"]["beirado"]),
                                      Cc.get("empena", S["cobertura"]["empena"]))
        z_e = z_vig + hv
        res_av = telhado_estrutura.construir(T_av, {
            "z_e": z_e, "z_teto": z_teto, "z_vig": z_vig, "vt": vt, "lam": E["lameladas"], "va": va, "pr": pr,
            "exts": exts, "peca": peca, "caixa": caixa, "prisma": prisma, "te": te, "ext_c": ext_c, "E": E,
            "alcados": alcados, "paineis": paineis})
        vigas_pav, n_prumos, n_madres = res_av["vigas_pav"], res_av["n_prumos"], res_av["n_madres"]
        telhados, aguas = [], []
        z_topo_max = z_e + T_av["z_max"] + pn_esp
    elif lam:
        # Roof on glulam beams (lameladas), as built at Torres Vedras (drawing D2503, docs/cobertura-D2503.md):
        # lameladas wall to wall on the amarração; madres 11x7.5 standing, along the house, on prumos on every
        # lamelada; a pair of ridge madres; from each gutter the madres step up the slope at <= espacamento_max;
        # the longest slope's gutter madre sits on the lameladas (lowest possible ridge), the shorter slopes'
        # gutter madres stand on packing (calços); hidden gutters on packing with a fall to the outlets.
        md = E["madres"]
        wm, hm = md["largura"], md["altura"]
        dc, passo = md.get("cumeeira_entre_eixos", 0.10), md["espacamento_max"]
        cl = S["cobertura"]["caleira_oculta"]
        w_can = cl["largura"]
        vigas_pav, vigas, n_prumos, n_madres = [], [], 0, 0
        for i, (xv, ya, yb) in enumerate(lams, 1):
            peca(f"Lamelada {i:02d}", "1.7", lam["seccao"], "Lamelada",
                 [caixa(xv - wl / 2, xv + wl / 2, ya, yb, z_teto, z_vig)], yb - ya, (yb - ya) * wl * lam["altura"])
            vigas_pav.append({"x0": round(xv - wl / 2, 4), "x1": round(xv + wl / 2, 4), "y0": round(ya, 4), "y1": round(yb, 4)})
            vigas.append((xv, ya, yb))
        yr = Cc["cumeeira_y"]
        aguas = []
        for ag in Cc["aguas"]:
            x0, x1 = ag["x"]
            y_out = ag["y_fim"]
            y_alto = ag.get("y_topo", yr)  # one slope: each strip up to its own high wall
            ylo_, yhi_ = min(y_alto, y_out), max(y_alto, y_out)
            fx0 = face_interior("O", x0, x1, ylo_, yhi_)
            fx1 = face_interior("E", x0, x1, ylo_, yhi_)
            f_lo = face_interior(ag["lado"], x0, x1, ylo_, yhi_)
            a_ = {"x0": fx0 if fx0 is not None else x0, "x1": fx1 if fx1 is not None else x1,
                  "lado": ag["lado"], "y_lo": f_lo if f_lo is not None else y_out, "x_bruto": (x0, x1)}
            if uma_agua:
                f_hi = face_interior("S" if ag["lado"] == "N" else "N", x0, x1, ylo_, yhi_)
                a_["y_hi"] = f_hi if f_hi is not None else y_alto
            aguas.append(a_)
        fechar_aguas(aguas)
        for ag in aguas:
            sg = 1 if ag["lado"] == "N" else -1
            ag["y_gf"] = ag["y_lo"] - sg * w_can               # gutter-side face of the gutter madre
            ag["g"] = ag["y_gf"] - sg * wm / 2                  # axis of the gutter madre
            ag["y_pe"] = ag["y_gf"] + sg * md.get("beiral", 0.10)  # panel end, into the gutter
            # the ridge madre on this side; one slope: the top madre against its own high wall
            ag["yrm"] = ag["y_hi"] + sg * wm / 2 if uma_agua else yr + sg * dc / 2
            ag["run"] = abs(ag["yrm"] - ag["g"])
        subida = 0
        if uma_agua:  # one plane, its top the highest strip's top madre
            yr = (min if aguas[0]["lado"] == "N" else max)(a["yrm"] for a in aguas)
            subida = 1 if aguas[0]["lado"] == "S" else -1
        z_cume = z_vig + hm + tan * max(abs(yr - ag["g"]) if uma_agua else ag["run"] for ag in aguas)  # top madres

        def topo_madre(y):
            if uma_agua:
                return z_cume + tan * subida * (y - yr)
            return z_cume - tan * max(0.0, abs(y - yr) - dc / 2)

        linhas = []
        for lado, sgn in (("N", 1), ("S", -1)):
            ags = sorted([a for a in aguas if a["lado"] == lado], key=lambda a: a["run"])
            if not ags:
                continue
            ys_l = []
            if uma_agua:  # one gutter line (the straight low side): equal bays from it up to the plane's top madre
                g0 = ags[0]["g"]
                nb = max(1, math.ceil(abs(yr - g0) / passo - 1e-9))
                ys_l = [g0 - sgn * abs(yr - g0) * j / nb for j in range(nb)]
            for ag in ([] if uma_agua else ags):
                if not ys_l:  # the shortest slope: from its gutter madre up to the ridge at <= passo
                    y = ag["g"]
                    while sgn * (y - ag["yrm"]) > 0.3:
                        ys_l.append(y)
                        y -= sgn * passo
                else:  # a longer slope shares those lines and divides the rest down to its gutter equally
                    fim_ = max(ys_l) if sgn > 0 else min(ys_l)
                    span = sgn * (ag["g"] - fim_)
                    if span > 0.05:
                        nb = math.ceil(span / passo - 1e-9)
                        ys_l += [ag["g"] - sgn * span * j / nb for j in range(nb)]
            for y in ys_l:
                ags_y = [a for a in ags if sgn * (a["g"] - y) >= -0.01 and
                         sgn * (y - a["yrm"]) >= (wm + 0.04 if uma_agua else -0.01)]
                linhas.append((round(y, 4), dentro_da_casa(y, ags_y), "Madre"))
            if uma_agua:  # a top madre against each strip's high wall, on the slope (no ridge pair)
                for y_t in sorted({round(a["yrm"], 4) for a in ags}):
                    linhas.append((y_t, dentro_da_casa(y_t, [a for a in ags if abs(a["yrm"] - y_t) < 1e-3]), "Madre"))
                continue
            y_cm = yr + sgn * dc / 2
            linhas.append((round(y_cm, 4), dentro_da_casa(y_cm, ags), "Madre de cumeeira"))
        xs_lam = sorted(v[0] for v in vigas)
        cm_ = md.get("cumeeira_vao_longo")  # D2503: ridge madres 22x7.5 over the 11 m lameladas
        # where the ridge changes section (a long lamelada next to a short one): a joint on that last long lamelada, so
        # both ridge madres change at the same place and the 22x7,5 covers every long lamelada
        longa = {round(xv, 4): (yb - ya) > cm_["lamelada_min"] for xv, ya, yb in vigas} if cm_ else {}
        troca = [xs_lam[i] for i in range(len(xs_lam) - 1)
                 if longa.get(round(xs_lam[i], 4)) != longa.get(round(xs_lam[i + 1], 4))]
        troca += [xs_lam[i + 1] for i in range(len(xs_lam) - 1)
                  if not longa.get(round(xs_lam[i], 4)) and longa.get(round(xs_lam[i + 1], 4))]
        altas = []  # taller ridge madres (the prumos under them are shorter)
        for y, ivs, tipo_m in linhas:
            zt = topo_madre(y)
            h = zt - hm - z_vig
            k = 0
            for x0_, x1_ in ivs:
                s = x0_
                while x1_ - s > 0.01:  # pieces jointed on lameladas (D2503: 3,60 / 3,66 / 2,75 / 2,90)
                    if x1_ - s <= md["peca_max"]:
                        e_ = x1_
                    else:
                        cand = [x for x in xs_lam if s + 0.3 < x <= s + md["peca_max"]]
                        e_ = max(cand) if cand else s + md["peca_max"]
                    if tipo_m == "Madre de cumeeira":
                        e_ = min([e_] + [x for x in troca if s + 0.3 < x < e_ - 0.01])
                    k += 1
                    sec_m, hm_ = md["seccao"], hm
                    if tipo_m == "Madre de cumeeira" and cm_:
                        sob = [yb - ya for xv, ya, yb in vigas if s - 0.01 <= xv <= e_ + 0.01]
                        if sob and min(sob) > cm_["lamelada_min"]:
                            sec_m, hm_ = cm_["seccao"], cm_["altura"]
                    peca(f"{tipo_m} y{y:.2f} {k}", "1.9", sec_m, tipo_m,
                         [caixa(s, e_, y - wm / 2, y + wm / 2, zt - hm_, zt)], e_ - s, (e_ - s) * wm * hm_)
                    if hm_ != hm:
                        altas.append((s, e_, y, hm_))
                    n_madres += 1
                    s = e_
                for xv, ya, yb in vigas:  # prumos on the lameladas (gutter madres: on the gutter packing)
                    if not (x0_ - 0.01 <= xv <= x1_ + 0.01 and ya <= y <= yb) or h < 0.01:
                        continue
                    if any(abs(a["g"] - y) < 0.01 and a["x0"] - 0.01 <= xv <= a["x1"] + 0.01 for a in aguas):
                        continue
                    hp_ = h - max([hh - hm for s_a, e_a, y_a, hh in altas if abs(y_a - y) < 1e-6 and s_a - 0.01 <= xv <= e_a + 0.01] or [0.0])
                    if hp_ < 0.01:
                        continue
                    n_prumos += 1
                    peca(f"Prumo y{y:.2f} x{xv:.2f}", "1.9", pr["seccao"], "Prumo",
                         [caixa(xv - pr["largura_x"] / 2, xv + pr["largura_x"] / 2, y - pr["largura_y"] / 2,
                                y + pr["largura_y"] / 2, z_vig, z_vig + hp_)], hp_, hp_ * pr["largura_x"] * pr["largura_y"])
        # hidden gutters: on packing on the lameladas, falling to the outlets at the gutter ends (D2503 "Pendente
        # da caleira": ~2 %, never closer than folga_min to the top of the gutter madre)
        gcfg = Cc.get("caleiras", {})
        tb = cl.get("tubo", {}).get("largura", 0.08)
        x_grelha = max(a["x1"] for a in aguas)
        telhados = []
        for k_t, ag in enumerate(aguas, 1):
            sg = 1 if ag["lado"] == "N" else -1
            x0_, x1_ = ag["x0"], ag["x1"]
            zt_g = topo_madre(ag["g"])
            h_madre = zt_g - hm - z_vig
            parede = next((w for w in exts if w["eixo"] == "x" and abs((w["f0"] if sg > 0 else w["f1"]) - ag["y_lo"]) < 0.01
                           and min(w["b"], x1_) - max(w["a"], x0_) > 0.3), None)
            gc = gcfg.get(parede["id"], {}) if parede else {}
            vaos = [(o["s0"], o["s1"]) for o in parede["aberturas"]] if parede else []
            xs_out = []
            for sd in gc.get("saidas", ["inicio", "fim"]):
                xo, dx = (x0_ - tb / 2, 0.05) if sd == "inicio" else (x1_ - tb / 2, -0.05)
                n_ = 0
                while any(v0 - 0.10 < xo + tb and xo < v1 + 0.10 for v0, v1 in vaos) and n_ < 400:
                    xo += dx
                    n_ += 1
                xs_out.append(round(xo, 4))
            centros = [xo + tb / 2 for xo in xs_out]

            def dist(x, centros=centros):
                return min(abs(x - c) for c in centros) if centros else 0.0

            pts = sorted({x0_, x1_} | {min(max(c, x0_), x1_) for c in centros} |
                         {(a + b) / 2 for a, b in zip(sorted(centros), sorted(centros)[1:])})
            dmax = max(dist(x) for x in pts) or 1.0
            h_max = gc.get("queda")
            if h_max is None:
                h_max = min(cl.get("queda_pct", 2.0) / 100.0 * dmax, (zt_g - z_vig) - cl.get("folga_min", 0.04))
            q = max(0.0, h_max) / dmax
            fundo = [[round(x, 4), round(z_vig + q * dist(x), 4)] for x in pts]
            for xv, ya, yb in vigas:  # packing on every lamelada: under the gutter (the fall) and under the madre
                if not (x0_ - 0.01 <= xv <= x1_ + 0.01 and ya <= min(ag["y_lo"], ag["y_gf"]) and max(ag["y_lo"], ag["y_gf"]) <= yb):
                    continue
                for nome_c, (c0_, c1_), hh in (("caleira", (ag["y_lo"], ag["y_gf"]), q * dist(xv)),
                                               ("madre", (ag["y_gf"], ag["y_gf"] - sg * md.get("calco_madre", 0.19)), h_madre)):
                    if hh < 0.005:
                        continue
                    c0_, c1_ = sorted((c0_, c1_))
                    peca(f"Calço da caleira A{k_t} x{xv:.2f} ({nome_c})", "1.9", pr["seccao"], "Calço da caleira",
                         [caixa(xv - wl / 2, xv + wl / 2, c0_, c1_, z_vig, z_vig + hh)], c1_ - c0_, (c1_ - c0_) * wl * hh)
            z_borda = topo_madre(ag["y_pe"]) + pn_esp
            fins = []
            for x_e in (x0_, x1_):  # gutter end against a parapet (lined up to its top) or open to a lower roof
                contra = any(w["eixo"] == "y" and min(abs(w["f0"] - x_e), abs(w["f1"] - x_e)) < 0.01 and
                             w["a"] - 0.01 <= min(ag["y_lo"], ag["y_gf"]) and max(ag["y_lo"], ag["y_gf"]) <= w["b"] + 0.01
                             for w in exts)
                fins.append("parede" if contra else "livre")
            y_c = ag["y_hi"] if uma_agua else yr  # one slope: the panels end against the high wall
            telhados.append({"x0": round(x0_, 4), "x1": round(x1_, 4), "lado": ag["lado"],
                             "y_baixo": round(ag["y_pe"], 4), "y_cume": round(y_c, 4),
                             "z_cume": round(topo_madre(y_c) if uma_agua else z_cume + tan * dc / 2, 4),
                             **({"uma_agua": True} if uma_agua else {}),
                             "inclinacao": tan, "y_parede": round(ag["y_lo"], 4), "y_caleira": round(ag["y_gf"], 4),
                             "canal": [round(min(ag["y_lo"], ag["y_gf"]), 4), round(max(ag["y_lo"], ag["y_gf"]), 4)],
                             "z_canal": [round(min(z for _x, z in fundo), 4), round(zt_g, 4)], "fundo": fundo,
                             "z_madre": round(zt_g, 4), "saidas": xs_out, "fins_caleira": fins,
                             "z_borda": round(z_borda, 4), "grelha_x": round(x_grelha, 4)})
        z_topo_max = z_cume + pn_esp
    else:
        vigas_pav, vigas, n_prumos, n_madres = [], [], 0, 0
        for k_z, i, xv, ya, yb in vigas_220():  # from the wall they bear on to the other (apoio_vigas)
            peca(f"Viga de apoio ao teto Z{k_z}.{i + 1:02d}", "1.7", vt["seccao"], "Viga de apoio ao teto",
                 [caixa(xv - vt["largura"] / 2, xv + vt["largura"] / 2, ya, yb, z_teto, z_vig)], yb - ya,
                 (yb - ya) * vt["largura"] * vt["altura"])
            vigas_pav.append({"x0": round(xv - vt["largura"] / 2, 4), "x1": round(xv + vt["largura"] / 2, 4),
                              "y0": round(ya, 4), "y1": round(yb, 4)})
            vigas.append((xv, ya, yb))

        yr = Cc["cumeeira_y"]
        if isinstance(yr, str):  # ridge against an exterior wall (the high side of a slope): the ridge purlin
            w_r = next(w for w in exts if w["id"] == yr)  # stands against the wall's inner frame face
            yr = round(w_r["f1"] + wv / 2 if w_r["lado_exterior"] < 0 else w_r["f0"] - wv / 2, 4)
        aguas = []
        for ag in Cc["aguas"]:
            x0, x1 = ag["x"]
            y_out = ag["y_fim"]  # architect's outer face of the low side
            y_alto = ag.get("y_topo", yr)  # one slope: each strip up to its own high wall
            ylo_, yhi_ = min(y_alto, y_out), max(y_alto, y_out)
            fx0 = face_interior("O", x0, x1, ylo_, yhi_)
            fx1 = face_interior("E", x0, x1, ylo_, yhi_)
            f_lo = face_interior(ag["lado"], x0, x1, ylo_, yhi_)
            a_ = {"x0": fx0 if fx0 is not None else x0, "x1": fx1 if fx1 is not None else x1,
                  "lado": ag["lado"], "y_lo": f_lo if f_lo is not None else y_out, "x_bruto": (x0, x1)}
            if uma_agua:  # its top purlin against the inner face of its high wall
                sg_ = 1 if ag["lado"] == "N" else -1
                f_hi = face_interior("S" if ag["lado"] == "N" else "N", x0, x1, ylo_, yhi_)
                a_["y_hi"] = f_hi if f_hi is not None else y_alto
                a_["y_top"] = a_["y_hi"] + sg_ * wv / 2
            aguas.append(a_)
        fechar_aguas(aguas)
        if uma_agua:  # the plane's top: the highest strip's top purlin
            yr = (min if aguas[0]["lado"] == "N" else max)(a["y_top"] for a in aguas)
        # Hidden gutter (caleira oculta) along the low side of every slope, inside the parapet (user 2026-10-16:
        # "fica por dentro e ao nível da parte de baixo dos rufus"): a 110x75 laid flat on the ceiling beams, OSB 22,
        # a 110x75 upright on the roof side (company standard: 2 x 110x75 + OSB 22, channel 30 cm), lined with
        # aluminium; the panels end 5 cm into the channel. The ridge height follows from the longest slope, whose
        # panels must clear the upright.
        cl = S["cobertura"]["caleira_oculta"]
        w_can = cl["largura"]                        # channel width, parapet face to the upright
        t_up = am["altura"]                          # upright 110x75 on edge: 75 thick ...
        h_up = cl.get("altura", 0.11)                # ... 110 high (channel depth on the longest slope)
        z_osb = z_vig + am["altura"] + 0.022         # channel bottom: flat 110x75 + OSB 22 on the beams
        for ag in aguas:
            sg_ = 1 if ag["lado"] == "N" else -1
            ag["y_gi"] = ag["y_lo"] - sg_ * w_can              # roof-side edge of the channel (face of the upright)
            ag["y_up"] = ag["y_gi"] - sg_ * t_up               # roof-side face of the upright
            ag["y_pe"] = ag["y_gi"] + sg_ * 0.05               # end of the panels, 5 cm into the channel
        run_max = max(abs(a_["y_up"] - yr) for a_ in aguas)
        z_cume = z_osb + h_up + 0.005 + tan * run_max          # top of the purlins on the ridge line

        def plano(y):
            if uma_agua:  # one plane rising to the high side
                return z_cume + tan * (y - yr) * (1 if aguas[0]["lado"] == "S" else -1)
            return min(z_cume, z_cume - tan * (abs(y - yr) - 0.0))

        # purlins: per side, lines shared by its slopes (the shortest slope from the purlin against its gutter upright up
        # to the ridge at <= espacamento_max, a longer slope dividing the rest down to its own upright), each line from
        # the inner face of one exterior wall across it to the next (as the madres on lameladas — the user's broken roof
        # lines of 2026-10-21, L47); the ridge purlin once, over every slope
        esp = va["espacamento_max"]
        linhas_c = []
        for lado, sg in (("N", 1), ("S", -1)):
            ags = sorted([a for a in aguas if a["lado"] == lado], key=lambda a: abs(a["y_up"] - yr))
            ys_l = []
            for ag in ags:
                run = abs(ag["y_up"] - yr)
                y_1 = ag["y_up"] - sg * wv / 2  # the purlin against the gutter upright
                if not ys_l:
                    nm = max(1, math.ceil((run - wv) / esp - 1e-9))
                    ys_l += [ag["y_up"] - sg * (wv / 2 + (run - wv) * k / nm) for k in range(nm)]
                else:
                    fim_ = max(ys_l) if sg > 0 else min(ys_l)
                    span = sg * (y_1 - fim_)
                    if span > 0.05:
                        nb = math.ceil(span / esp - 1e-9)
                        ys_l += [y_1 - sg * span * j / nb for j in range(nb)]
            for yc in ys_l:
                ags_y = [a for a in ags if sg * ((a["y_up"] - sg * wv / 2) - yc) >= -0.01 and  # (one slope: below its top
                         (not uma_agua or sg * (yc - a["y_top"]) >= wv + 0.04)]           # purlin, clear of it)
                linhas_c.append((yc, dentro_da_casa(yc, ags_y), False))
        if uma_agua:  # one slope: a top purlin against each strip's high wall, on the slope (no ridge)
            for y_t in sorted({round(a["y_top"], 4) for a in aguas}):
                linhas_c.append((y_t, dentro_da_casa(y_t, [a for a in aguas if abs(a["y_top"] - y_t) < 1e-3]), False))
        else:
            linhas_c.append((yr, dentro_da_casa(yr, aguas), True))
        for k_l, (yc, ivs, cume) in enumerate(linhas_c, 1):
            y0_, y1_ = yc - wv / 2, yc + wv / 2
            if cume:
                sec = [(y0_, z_cume - hv), (y1_, z_cume - hv), (y1_, z_cume), (y0_, z_cume)]
            else:
                sec = [(y0_, plano(y0_) - hv), (y1_, plano(y1_) - hv), (y1_, plano(y1_)), (y0_, plano(y0_))]
            z_sob = min(sec[0][1], sec[1][1])
            for k_i, (x0_, x1_) in enumerate(ivs, 1):
                comp = x1_ - x0_
                peca(f"Viga de apoio à cobertura L{k_l:02d}" + (f".{k_i}" if len(ivs) > 1 else ""), "1.9",
                     va.get("seccao", "110x75"), "Viga de apoio à cobertura",
                     [prisma([(x0_, y, z) for y, z in sec], (comp, 0, 0))], comp, comp * wv * hv)
                n_madres += 1
                if z_sob - z_vig < 0.03:
                    continue  # rests on the beams
                for xv, ya, yb in vigas:
                    if not (x0_ <= xv <= x1_ and ya <= yc <= yb):
                        continue
                    xa_, xb_ = xv - pr["largura_x"] / 2, xv + pr["largura_x"] / 2
                    ya_, yb_ = yc - pr["largura_y"] / 2, yc + pr["largura_y"] / 2
                    base = [(xa_, ya_, z_vig), (xb_, ya_, z_vig), (xb_, yb_, z_vig), (xa_, yb_, z_vig)]
                    topo = [(x, y, (z_cume if cume else plano(y)) - hv) for x, y, _z in base]
                    h = (z_cume if cume else plano(yc)) - hv - z_vig
                    n_prumos += 1
                    peca(f"Prumo L{k_l:02d} x{xv:.2f}", "1.9", pr["seccao"], "Prumo",
                         [{"b": [[R(c) for c in q] for q in base], "t": [[R(c) for c in q] for q in topo]}], h,
                         h * pr["largura_x"] * pr["largura_y"])
        telhados = []
        for k_t, ag in enumerate(aguas, 1):
            sg = 1 if ag["lado"] == "N" else -1
            comp = ag["x1"] - ag["x0"]
            # the gutter box along the low wall: flat 110x75 under the upright, OSB 22 from the parapet to the upright,
            # upright 110x75 up to just under the panels. A shorter slope ends higher: its gutter keeps the standard
            # depth and is raised, the flat 110x75 standing on prumos on the ceiling beams (version 4, assumed)
            y_lo, y_gi, y_up = ag["y_lo"], ag["y_gi"], ag["y_up"]
            z_osb_a = max(z_osb, plano(y_up) - 0.005 - h_up)
            h_lado = plano(y_up) - 0.005 - z_osb_a
            z_base = z_osb_a - 0.022 - am["altura"]
            ys_base = sorted((y_up, y_up + sg * 0.11))
            partes = [("base 110x75 deitada", am["seccao"], ys_base, z_base, z_base + am["altura"]),
                      ("OSB 22", "OSB 22", sorted((y_lo, y_up)), z_osb_a - 0.022, z_osb_a),
                      ("110x75 ao alto", am["seccao"], sorted((y_gi, y_up)), z_osb_a, z_osb_a + h_lado)]
            for nome_p, sec_p, (ya, yb), za, zb in partes:
                peca(f"Caleira oculta A{k_t} | {nome_p}", "1.9", sec_p, f"Caleira oculta ({nome_p})",
                     [caixa(ag["x0"], ag["x1"], ya, yb, za, zb)], comp, comp * (yb - ya) * (zb - za))
            if z_base - z_vig > 0.01:
                yc_b = sum(ys_base) / 2
                for xv, ya, yb in vigas:
                    if not (ag["x0"] <= xv <= ag["x1"] and ya <= yc_b <= yb):
                        continue
                    h = z_base - z_vig
                    n_prumos += 1
                    peca(f"Prumo da caleira A{k_t} x{xv:.2f}", "1.9", pr["seccao"], "Prumo",
                         [caixa(xv - pr["largura_x"] / 2, xv + pr["largura_x"] / 2, ys_base[0], ys_base[1], z_vig, z_base)],
                         h, h * pr["largura_x"] * pr["largura_y"])
            y_c = ag["y_hi"] if uma_agua else yr  # one slope: the panels end against the high wall
            telhados.append({"x0": round(ag["x0"], 4), "x1": round(ag["x1"], 4), "lado": ag["lado"],
                             "y_baixo": round(ag["y_pe"], 4), "y_cume": round(y_c, 4),
                             "z_cume": round(plano(y_c) if uma_agua else z_cume, 4), "inclinacao": tan,
                             **({"uma_agua": True} if uma_agua else {}),
                             "y_parede": round(y_lo, 4), "canal": [round(min(y_lo, y_gi), 4), round(max(y_lo, y_gi), 4)],
                             "z_canal": [round(z_osb_a, 4), round(z_osb_a + h_lado, 4)],
                             "z_borda": round(plano(ag["y_pe"]) + pn_esp, 4)})
        z_topo_max = z_cume + pn_esp

    # ------------------------------------------------------------------ parapet (platibanda)
    # All exterior walls rise to the same height (user 2026-10-16: "a casa é suposto ter a mesma altura em todos
    # os lados"), 5 cm above the panels at the ridge; X walls run through the corners. The walls with the gutter
    # behind them ("calha") carry the downpipes in their cladding; every parapet is clad on the roof side too.
    folga = cfg.get("platibanda", {}).get("folga", 0.05)
    z_plat = None if avista else (cfg.get("platibanda", {}).get("topo") or round(z_topo_max + folga, 3))
    calhas = {}
    for t, ag in zip(telhados, aguas):
        for w in exts:
            if w["eixo"] != "x" or min(w["b"], ag["x1"]) - max(w["a"], ag["x0"]) < 0.3:
                continue
            f_in = w["f0"] if ag["lado"] == "N" else w["f1"]
            if abs(f_in - ag["y_lo"]) < 0.01:
                calhas[w["id"]] = t
                t.update({"parede": w["id"], "y_fora": round(w["f1"] if ag["lado"] == "N" else w["f0"], 4),
                          "parede_s": [round(w["a"], 4), round(w["b"], 4)],
                          "aberturas_parede": [[round(o["s0"], 3), round(o["s1"], 3)] for o in w["aberturas"]]})
    for w in exts:
        w["pa"], w["pb"] = w["a"], w["b"]
    n_plat = 0
    for w in ([] if avista else exts):  # an exposed roof has no parapet
        baixa = False  # (version 2 had low walls on the gutter sides; superseded 2026-10-16)
        z0p = z_vig if (w["eixo"] == "x" or anel) else z_teto  # on the beam ends on walls across the beams, else on the tie beam
        topo = z_plat
        Hp = topo - z0p
        if w.get("mods"):
            pts = [w["mods"][0]["pegada"][0 if w["eixo"] == "x" else 2]] + \
                [m["pegada"][1 if w["eixo"] == "x" else 3] for m in w["mods"]]
        else:
            pts = juntas_w[w["id"]] if anel else juntas(w["pa"], w["pb"], [], lmax)
        for k, (m0, m1) in enumerate(zip(pts, pts[1:]), 1):
            W = m1 - m0
            fantasma = (w["id"], k) in reais_plat
            if fantasma:  # the real module runs to the top: this parapet panel only carries the layers
                ms = reais_plat[(w["id"], k)][2]
            elif anel and continuos.get((w["id"], k)):  # the studs of the module below run on to the top plate
                ms = [membro(t_, sec_, ret(u0, u1, 0, Hp - pl)) for u0, u1, t_, sec_ in continuos[(w["id"], k)]]
                ms.append(membro("Travessa superior", ext_c["seccao_montante"], ret(0, W, Hp - pl, Hp)))
            elif baixa:  # cap on the beam ends up to the roof edge: 110x75 pieces, a 110x35 to finish
                ms, zz = [], 0.0
                while Hp - zz > 0.005:
                    h = min(am["altura"], Hp - zz)
                    ms.append(membro("Viga de remate", am["seccao"] if h > 0.04 else af_e["seccao"], ret(0, W, zz, zz + h)))
                    zz += h
            else:
                ms = [membro("Travessa inferior", ext_c["seccao_montante"], ret(0, W, 0, pl)),
                      membro("Travessa superior", ext_c["seccao_montante"], ret(0, W, Hp - pl, Hp))]
                c0, c1 = k == 1, k == len(pts) - 1
                ms.append(membro("Montante de canto" if c0 else "Montante", ext_c["seccao_reforco"] if c0 else ext_c["seccao_montante"],
                                 ret(0, ext_c["reforco"] if c0 else ext_c["montante"], pl, Hp - pl)))
                ms.append(membro("Montante de canto" if c1 else "Montante", ext_c["seccao_reforco"] if c1 else ext_c["seccao_montante"],
                                 ret(W - (ext_c["reforco"] if c1 else ext_c["montante"]), W, pl, Hp - pl)))
                x = (ext_c["reforco"] if c0 else ext_c["montante"]) + E["vao_livre"]
                while x + ext_c["montante"] <= W - ext_c["montante"] - 0.03:
                    ms.append(membro("Montante", ext_c["seccao_montante"], ret(x, x + ext_c["montante"], pl, Hp - pl)))
                    x += E["vao_livre"] + ext_c["montante"]
            nome = f"PLAT {w['id']}.{k}"
            chave = f"{nome}__dc"
            alcados[chave] = {"W": W, "H": Hp, "members": ms, "frame_u0": 0.0, "frame_u1": W,
                              "section": ext_c["seccao_montante"], "aberturas": [], "sistema": "discovercasa", "studs": []}
            org = [m0, w["fc"]] if w["eixo"] == "x" else [w["fc"], m0]
            paineis.append({"nome": nome, "alcado": chave, "piso": 2, "tipo": "PE",
                            "origem": [round(org[0], 4), round(org[1], 4), round(z0p, 4)],
                            "sentido": [1.0, 0.0] if w["eixo"] == "x" else [0.0, 1.0], "espessura": te,
                            "encaixe": "-", "extra": 0, "exterior": True, "platibanda": "calha" if w["id"] in calhas else "alta",
                            **({"fantasma": True} if fantasma else {}),
                            "fora": float(w["lado_exterior"] if w["eixo"] == "x" else -w["lado_exterior"])})
            n_plat += 1

    # ------------------------------------------------------------------ pergola (outside the house)
    # Timber pergola along the facades (TV, user 2026-10-19 and the photo of the finished house: the whole length
    # of the house, tiled, with an exposed gutter along the front; glulam with autoclave treatment). Posts under
    # the front beam; beams falling to the front, resting on the front beam and on a ledger screwed to each facade
    # over the battens (the Tremolo is cut round the ledger and the beam ends); slats across on the beams. The
    # tiles, the gutter and its downpipes are made by camadas.py (pergola_cobertura) from G["pergola"].
    pg = cfg.get("pergola")
    n_pg = 0
    pg_info = None
    cont = cfg.get("fundacao", {}).get("contorno")
    if pg and cont:
        ex_ = S["exterior"]
        op = ex_["opcoes"][ex_["opcao_visivel"]]
        esp_rev = ex_["osb"]["espessura"] + ex_["membrana"]["espessura"] + sum(c["espessura"] for c in op["camadas"])
        esp_rip = ex_["osb"]["espessura"] + ex_["membrana"]["espessura"] + \
            sum(c["espessura"] for c in op["camadas"] if c.get("tipo") == "ripas")
        acab = desloca(contorno_estrutura(cont, exts), esp_rev)  # finished faces of the house
        y_fr = pg["y_frente"]
        cy = sum(p[1] for p in acab) / len(acab)
        s_ = 1.0 if cy > y_fr else -1.0           # from the front towards the house
        px0 = min(p[0] for p in acab) if pg.get("x0", "casa") == "casa" else pg["x0"]
        px1 = max(p[0] for p in acab) if pg.get("x1", "casa") == "casa" else pg["x1"]
        # facades facing the pergola: (x0, x1, y of the finished face)
        fach = []
        for p, q in zip(acab, acab[1:] + acab[:1]):
            if abs(p[1] - q[1]) < 1e-9 and min(max(p[0], q[0]), px1) - max(min(p[0], q[0]), px0) > 0.1:
                ym = p[1] - s_ * 0.01
                if not any(a_ <= (p[0] + q[0]) / 2 <= b_ for a_, b_ in dentro_x(acab, ym)):  # the front side is outside
                    fach.append((max(min(p[0], q[0]), px0), min(max(p[0], q[0]), px1), p[1]))

        def u_de(y):
            return s_ * (y - y_fr)

        def facade(x):  # the facade a beam at x runs to (nearest the front)
            cands = [f for f in fach if f[0] - 1e-6 <= x <= f[1] + 1e-6]
            return min(cands, key=lambda f: u_de(f[2])) if cands else None

        pil, vf, ve, vg, rp = pg["pilar"], pg["viga_frontal"], pg["viga_encosto"], pg["vigas"], pg["ripas"]
        prod = {"produto": pg["produto"]} if pg.get("produto") else {}
        incl = pg.get("inclinacao", 0.0)        # the beams fall to the front
        z_v = pg["z_vigas"]                     # top of the front beam = underside of the beams at the front
        z_f = z_v - vf["altura"]
        dt = esp_rev - esp_rip                  # Tremolo: from the battens to the finished face

        def zb(u):  # underside of the beams
            return z_v + incl * u

        def inclinada(x0, x1, u0, u1, dz0, dz1):  # piece following the slope, between u0 and u1, dz above zb
            y0, y1 = y_fr + s_ * u0, y_fr + s_ * u1
            base = [(x0, y0, zb(u0) + dz0), (x0, y1, zb(u1) + dz0), (x0, y1, zb(u1) + dz1), (x0, y0, zb(u0) + dz1)]
            return prisma(base, (x1 - x0, 0.0, 0.0))

        def lim(x, h):
            return min(max(x, px0 + h), px1 - h)

        yf0, yf1 = sorted((y_fr, y_fr + s_ * vf["largura"]))
        pilares = []
        for k, xp in enumerate(pg["pilares_x"], 1):
            xc = lim(xp, pil["largura"] / 2)
            yc = (yf0 + yf1) / 2
            pilares.append([round(xc, 4), round(yc, 4)])
            peca(f"Pérgola | pilar {k}", "1.10", pil["seccao"], "Pilar da pérgola",
                 [caixa(xc - pil["largura"] / 2, xc + pil["largura"] / 2, yc - pil["largura"] / 2, yc + pil["largura"] / 2,
                        pg.get("z_base", 0.0), z_f)], z_f, pil["largura"] ** 2 * z_f, **prod)
        peca("Pérgola | viga frontal", "1.10", vf["seccao"], "Viga frontal da pérgola",
             [caixa(px0, px1, yf0, yf1, z_f, z_v)], px1 - px0, (px1 - px0) * vf["largura"] * vf["altura"], **prod)
        h_e = ve.get("altura", vg["altura"])
        faces_tq = {}
        for k, (fa, fb, yf) in enumerate(fach, 1):  # one ledger per facade, over its battens
            u_bat = u_de(yf) + dt
            ztop = zb(u_bat - ve["espessura"])
            ya_, yb_ = sorted((y_fr + s_ * u_bat, y_fr + s_ * (u_bat - ve["espessura"])))
            peca(f"Pérgola | viga de encosto {k}", "1.10", ve["seccao"],
                 "Viga de encosto da pérgola (aparafusada à fachada, sobre o ripado)",
                 [caixa(fa, fb, ya_, yb_, ztop - h_e, ztop)], fb - fa, (fb - fa) * ve["espessura"] * h_e, **prod)
            y_fora = round(yf + s_ * esp_rev, 4)
            faces_tq[y_fora] = {"y_fora": y_fora, "n": -s_, "cortes": [[fa - 0.005, fb + 0.005, ztop - h_e - 0.005, ztop]]}
        # beams: the plan's spacing over the whole length, one at each end
        if pg.get("vigas_x"):
            xs = list(pg["vigas_x"])
        else:
            o, e = pg["vigas_origem"], pg["vigas_espacamento"]
            a_, b_ = px0 + vg["largura"] / 2, px1 - vg["largura"] / 2
            xs = [o + e * k for k in range(-int((o - a_) / e) - 1, int((b_ - o) / e) + 2) if a_ <= o + e * k <= b_]
            if xs[0] - a_ > 0.3:
                xs.insert(0, a_)
            if b_ - xs[-1] > 0.3:
                xs.append(b_)
        n_v = 0
        for xv in xs:
            f = facade(xv)
            if f is None:
                continue
            xc = lim(xv, vg["largura"] / 2)
            if f[1] < px1 - 0.01:  # a wall stands at this facade's end (re-entrant corner): keep clear of it
                xc = min(xc, f[1] - vg["largura"] / 2)
            if f[0] > px0 + 0.01:
                xc = max(xc, f[0] + vg["largura"] / 2)
            u_bat = u_de(f[2]) + dt
            n_v += 1
            peca(f"Pérgola | viga {n_v}", "1.10", vg["seccao"], "Viga da pérgola",
                 [inclinada(xc - vg["largura"] / 2, xc + vg["largura"] / 2, 0.0, u_bat, 0.0, vg["altura"])],
                 u_bat * math.sqrt(1 + incl * incl), u_bat * vg["largura"] * vg["altura"], **prod)
            faces_tq[round(f[2] + s_ * esp_rev, 4)]["cortes"].append(
                [xc - vg["largura"] / 2 - 0.005, xc + vg["largura"] / 2 + 0.005, zb(u_bat), zb(u_bat) + vg["altura"] + 0.005])
        # slats across the beams, up to the finished faces
        u_max = max(u_de(f[2]) for f in fach)
        pecas_r, comp_r, u = [], 0.0, 0.0
        while u + rp["largura"] <= u_max + 0.001:
            ya_, yb_ = sorted((y_fr + s_ * u, y_fr + s_ * (u + rp["largura"])))
            ocup = dentro_x(acab, ya_ + 1e-4) + dentro_x(acab, yb_ - 1e-4)
            for x0_, x1_ in livres(px0, px1, ocup):
                pecas_r.append(inclinada(x0_, x1_, u, u + rp["largura"], vg["altura"], vg["altura"] + rp["espessura"]))
                comp_r += x1_ - x0_
            u += rp["espacamento"]
        peca("Pérgola | ripado", "1.10", rp["seccao"], "Ripado da pérgola", pecas_r, comp_r,
             comp_r * rp["largura"] * rp["espessura"], n_ripas=len(pecas_r), **prod)
        n_pg = len(pilares) + n_v + 1 + len(fach) + len(pecas_r)
        pg_info = {"faces": list(faces_tq.values()), "x0": round(px0, 4), "x1": round(px1, 4), "y_frente": y_fr, "s": s_,
                   "inclinacao": incl, "z_ripas_u0": round(zb(0.0) + vg["altura"] + rp["espessura"], 4),
                   "u_max": round(u_max, 4), "contorno_acabado": [[round(x, 4), round(y, 4)] for x, y in acab],
                   "pilares": pilares, "pilar_largura": pil["largura"],
                   "telha": pg.get("telha"), "caleira": pg.get("caleira")}

    # ------------------------------------------------------------------ geometry
    G = {"nome": cfg["nome"], "descricao": cfg.get("descricao", ""),
         "origem_desenhos": planta.get("origem_desenho", {}).get("dwfx", ""),
         "casa": {"comprimento": L, "profundidade": D, "espessura_exterior": te, "espessura_interior": ti},
         "niveis": {"piso0": 0.0, "topo_paredes_piso0": round(H_ext, 4), "teto_piso0": round(z_teto, 4),
                    "topo_vigas_teto": round(z_vig, 4), "platibanda": z_plat,
                    **({"topo_forro_piso0": round(z_teto - ama["altura"], 4)} if anel else {})},
         "cobertura": cobertura_avista(T_av, z_e, z_vig, hv, vt, pn_esp, Cc, res_av.get("encostos", [])) if avista else
                      {"sistema": "discovercasa", "tipo": "platibanda", "inclinacao": 0.0, "cumeeira_y": D / 2,
                       "cumeeira_z": z_plat, "plano_z_cume": z_plat, "altura_viga": hv, "apoio_z": {"N": z_vig, "S": z_vig},
                       "vigas_teto_x": [], "vigas_teto_largura": vt["largura"], "telhados": telhados,
                       "pendente_pct": tan * 100, "painel_espessura": pn_esp},
         "pavimento": {"pecas": vigas_pav, "abertura_escada": None, "sistema": "discovercasa", "sem_piso": True},
         "alcados": alcados, "paineis": paineis, "cobertura_planta": [], "estrutura_extra": extra,
         "notas_modelo": [
             "Casa gerada a partir da planta de arquitetura (ferramentas/modelo/casa_planta.py) com o método "
             "DiscoverCasa: módulos <= %.1f m, paredes exteriores 110 / interiores 75, pé-direito %.2f m, teto plano "
             "sob as vigas de apoio ao teto, %s." % (lmax, nv["pe_direito"], (
                 f"cobertura à vista em painel sandwich ("
                 f"{ {'quatro_aguas': 'quatro águas', 'misto': 'várias águas, com empenas'}.get(Cc.get('forma'), 'duas águas')}"
                 f", {100 * T_av['t']:.0f} %)" if avista else "cobertura escondida por platibanda"))]}
    if avista:
        G["colecoes_estrutura"] = {"1.6": "1.6 Afinação e amarração", "1.7": "1.7 Vigas de apoio ao teto, de bordo e de bordadura",
                                   "1.8": "1.8 Empenas (triângulos sobre a viga de bordo)",
                                   "1.9": "1.9 Vigas de apoio à cobertura, rincões, larós e prumos"}
    if lam:
        G["colecoes_estrutura"] = {"1.6": "1.6 Amarração 11x7,5 (face interior) e afinação",
                                   "1.7": f"1.7 Lameladas {lam['seccao']}",
                                   "1.8": "1.8 Platibanda (continuação dos módulos)",
                                   "1.9": "1.9 Madres (11x7,5; cumeeira 22x7,5 sobre a ala), prumos e calços da caleira"}
    if pg:
        G.setdefault("colecoes_estrutura", {})["1.10"] = pg.get("colecao", "1.10 Pérgola")
        G["pergola"] = pg_info
    if cfg.get("fundacao"):
        G["fundacao"] = cfg["fundacao"]
    if avisos_div:
        G["avisos_divisor"] = avisos_div
    if movidas:
        G["aberturas_movidas"] = movidas
    cont = cfg.get("fundacao", {}).get("contorno")
    if cont:  # outer outline of the exterior frames (the architect's outline moved to the frame faces)
        G["contorno_estrutura"] = contorno_estrutura(cont, exts)
    resumo = {"modulos": sum(1 for p in paineis if p["piso"] == 0), "platibanda": n_plat,
              "pecas_paredes": sum(len(a["members"]) for a in alcados.values()), "vigas_teto": len(vigas_pav),
              "madres": n_madres, "prumos": n_prumos, "H_modulos_ext": round(H_ext, 3), "H_modulos_int": round(H_int, 3),
              "z_teto": round(z_teto, 3), "z_vigas": round(z_vig, 3), "topo_cobertura": round(z_topo_max, 3),
              "topo_platibanda": z_plat, **({"pergola_pecas": n_pg} if pg else {})}
    return G, resumo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--saida")
    a = ap.parse_args()
    cfg_path = Path(a.config).resolve()
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    planta = json.load(open(cfg_path.parent / cfg["planta"], encoding="utf-8"))
    if cfg.get("modulos_reais"):  # the company's module drawings, read by modulos_dc.py
        cfg["_modulos"] = json.load(open(cfg_path.parent / cfg["modulos_reais"]["ficheiro"], encoding="utf-8"))["modulos"]
    S = teto_sob_anel(fundir(json.load(open(AQUI / "sistema_construtivo.json", encoding="utf-8")), cfg.get("camadas") or {}), cfg)
    E = fundir(S["estrutura"], {k: v for k, v in (cfg.get("estrutura") or {}).items() if k != "sistema"})
    G, resumo = construir(cfg, S, E, planta)
    saida = Path(a.saida) if a.saida else pasta_trabalho("modelos", cfg_path.parent.name) / "geometria_dc.json"
    saida.write_text(json.dumps(G, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("casa (planta):", json.dumps(resumo, ensure_ascii=False), "->", saida)


if __name__ == "__main__":
    main()
