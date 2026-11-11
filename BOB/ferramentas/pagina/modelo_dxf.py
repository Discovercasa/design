"""The 3D volumes of a house for the client page, from its architecture DXF (a DWG converted on the PC). Pure Python.

    python ferramentas/pagina/modelo_dxf.py "_trabalho/<obra>/config.json"

The config stays in _trabalho/ (git-ignored): it holds the drawing's site coordinates. It says what the drawing does
not say by itself (the confirmation step of the Builder app): which layers hold the walls, glazing and furniture; for
each storey the window of the drawing where its plan is, the shift that puts that copy on the real site (copies of the
site plan are often drawn side by side), its floor level and the level above, the rooms' areas; optionally
"contorno_de" (a basement taking the outline of the storey above); the roof; the terrain faces (3DFACE, the survey's
MDT). From that:
  - walls: ferramentas/planta/analisar.py on the storey's wall layers (any angle);
  - outline of the storey: the plan's lines closed by 10 cm and flooded from outside (door leaves and glazing lines
    close it; long loose lines away from the walls, such as an overhang's projection or a deck's edge, do not), the
    contour traced and simplified;
  - facade: each span of the outline is a wall (a band >= 14 cm drawn just inside it), a window frame or open
    (glazing drawn as one line); the page builds walls and glass there where the plan's walls do not already run;
  - slabs on the outlines; roof slabs on the roof plan's outline at its levels;
  - furniture: the closed shapes of the furniture layer, low blocks;
  - terrain: the MDT faces within a radius of the house.
Output (local metres, origin at the centre of the house, x east, y north, z up from the reference floor level): JSON for
gerar_pagina.py. Never written to Git: it is the client's house (it stays in _trabalho/).
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.dxf.leitor_dxf import Dxf, para_folha  # noqa: E402
from ferramentas.planta import analisar as A  # noqa: E402
from ferramentas.planta.mascara import Mascara  # noqa: E402


# ---------------------------------------------------------------------------- contour of a mask
def contorno(M):
    """Outer boundary of the biggest region of a mask (Moore tracing), in pixel corners: [(x, y)]."""
    comp = max(M.componentes(area_min=10), key=lambda c: c["area"], default=None)
    if not comp:
        return []
    ys = sorted(comp["linhas"])
    y0 = ys[0]
    b = comp["linhas"][y0]
    x0 = (b & -b).bit_length() - 1

    def dentro(x, y):
        return y in comp["linhas"] and x >= 0 and (comp["linhas"][y] >> x) & 1
    # walk the boundary edges with the region on the left (pixel edges), starting at the top-left pixel's top edge
    pts = []
    x, y, d = x0, y0, 0   # d: 0 right, 1 down, 2 left, 3 up (edges between pixel corners)
    inicio = (x, y, d)
    passos = 0
    while True:
        pts.append((x, y))
        # the pixel ahead-left and ahead-right of the current edge direction
        if d == 0:
            al, ar = dentro(x, y - 1), dentro(x, y)
        elif d == 1:
            al, ar = dentro(x, y), dentro(x - 1, y)
        elif d == 2:
            al, ar = dentro(x - 1, y), dentro(x - 1, y - 1)
        else:
            al, ar = dentro(x - 1, y - 1), dentro(x, y - 1)
        if al:
            d = (d - 1) % 4
        elif not ar:
            d = (d + 1) % 4
        dx, dy = ((1, 0), (0, 1), (-1, 0), (0, -1))[d]
        if al or ar:
            x, y = x + dx, y + dy
        passos += 1
        if (x, y, d) == inicio or passos > 4 * M.w * M.h:
            break
    return pts


def simplificar(pts, tol):
    """Douglas-Peucker on a closed polyline."""
    if len(pts) < 4:
        return pts

    def dp(seg):
        if len(seg) < 3:
            return seg
        (ax, ay), (bx, by) = seg[0], seg[-1]
        L = math.hypot(bx - ax, by - ay) or 1e-9
        dmax, k = 0.0, 0
        for i in range(1, len(seg) - 1):
            x, y = seg[i]
            dd = abs((bx - ax) * (ay - y) - (ax - x) * (by - ay)) / L
            if dd > dmax:
                dmax, k = dd, i
        if dmax <= tol:
            return [seg[0], seg[-1]]
        return dp(seg[:k + 1])[:-1] + dp(seg[k:])
    i_far = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
    a = dp(pts[:i_far + 1])
    b = dp(pts[i_far:] + [pts[0]])
    return a[:-1] + b[:-1]


def _sem_linhas_soltas(tracos, S, longo):
    """The strokes cut wherever a straight run longer than `longo` (m) lies away from the wall mask S."""
    def na_parede(a, b):
        return any(S.bit(int((a[0] + (b[0] - a[0]) * t) / A.RES), int((a[1] + (b[1] - a[1]) * t) / A.RES))
                   for t in (0.25, 0.5, 0.75))
    out = []
    for pts, larg, cor in tracos:
        cur = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            if math.hypot(b[0] - a[0], b[1] - a[1]) > longo and not na_parede(a, b):
                if len(cur) > 1:
                    out.append((cur, larg, cor))
                cur = [b]
            else:
                cur.append(b)
        if len(cur) > 1:
            out.append((cur, larg, cor))
    return out


# ---------------------------------------------------------------------------- one storey
def piso(d, cfg, p):
    X0, Y0, X1, Y1 = p["janela"]
    dx, dy = p.get("desloca", [0.0, 0.0])
    camadas = cfg["camadas"]["paredes"] + cfg["camadas"].get("vidros", [])
    ps = [q for q in d.paths(camadas=camadas) if any(X0 <= x <= X1 and Y0 <= y <= Y1 for sp, _ in q["subs"] for x, y in sp)]
    folha = para_folha(ps, 100, origem=(X0, Y1))
    reg = (0.0, 0.0, (X1 - X0) * 10, (Y1 - Y0) * 10)
    tracos, cheios = A.primitivas(folha, reg, 100)
    L, H = reg[2] / 10, reg[3] / 10
    tinta = A.imagem(tracos, cheios, L, H)
    S = A.mascara_paredes(tinta)
    P = A.Plano(S, L / 2, H / 2)
    linhas = A.linhas_retas(A._segmentos(tracos, cheios), L / 2, H / 2)
    pecas = A.paredes_de_faces(P, A.faces(P, linhas))
    rede = A._rede_principal(P, A.estender(P, A.vaos(P, A.juntar(P, pecas), linhas, tracos, pecas, cheios))) if pecas else []

    def real(x, y):    # image metres (y down from the window's top) -> real site coordinates
        return (X0 + x + dx, Y1 - y + dy)
    paredes = []
    for w in rede:
        a, b = P.ponto(w["th"], w["c"], w["s0"]), P.ponto(w["th"], w["c"], w["s1"])
        paredes.append({"p0": real(*a), "p1": real(*b), "esp": w["esp"],
                        "aberturas": [{"t0": o["s0"] - w["s0"], "t1": o["s1"] - w["s0"], "tipo": o["tipo"]} for o in w["aberturas"]]})
    # outline: everything drawn, closed by 10 cm, flooded from the border; long loose lines away from the walls
    # (overhang/projection lines, a deck's edge) do not close it
    fecho = int(p.get("fecho_m", 0.12) / A.RES)
    m = fecho + 2
    base = A.imagem(_sem_linhas_soltas(tracos, S, p.get("linha_solta_m", 2.5)), cheios, L, H).ou(S)
    larga = Mascara(tinta.w + 2 * m, tinta.h + 2 * m, [0] * m + [b << m for b in base.r] + [0] * m)
    fechada = larga.fechar(fecho)
    fora = fechada.inverso().preencher({0: fechada.inverso().r[0]})
    casa = Mascara(larga.w, larga.h, [larga.cheia & ~fora.get(y, 0) for y in range(larga.h)])
    cont = simplificar(contorno(casa), p.get("simplifica_m", 0.06) / A.RES)
    outline = [real((x - m) * A.RES, (y - m) * A.RES) for x, y in cont]
    fachada = [{"p0": real((a[0] - m) * A.RES, (a[1] - m) * A.RES), "p1": real((b[0] - m) * A.RES, (b[1] - m) * A.RES),
                "tipo": t, "esp": e} for a, b, t, e in _fachada(cont, casa, S, m)]
    return {"paredes": paredes, "contorno": outline, "fachada": fachada}


def _fachada(cont, casa, S, m, passo=0.1, parede_min=0.14):
    """What closes the outline, span by span: 'parede' (a wall band at least parede_min thick just inside the
    outline), 'vidro' (a thinner band: a window frame drawn in the wall line) or 'aberto' (nothing drawn: a
    glazed facade drawn as a single line, a gap). Walls come back on their centre line (moved in by half their
    thickness, lengthened by half at each end so corners meet); glass 5 cm inside the outline. Pixel coords."""
    out = []
    n = len(cont)
    for i in range(n):
        a, b = cont[i], cont[(i + 1) % n]
        Lp = math.hypot(b[0] - a[0], b[1] - a[1])
        if Lp * A.RES < 0.2:
            continue
        ux, uy = (b[0] - a[0]) / Lp, (b[1] - a[1]) / Lp
        nx, ny = -uy, ux
        k = 0.3 / A.RES
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if not casa.bit(int(mx + nx * k), int(my + ny * k)):
            nx, ny = -nx, -ny
        N = max(1, int(Lp * A.RES / passo))
        am = []
        for j in range(N):
            t = (j + 0.5) / N
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            ini = fim = None
            for s in range(int(0.7 / A.RES)):
                if S.bit(int(x + nx * s - m), int(y + ny * s - m)):
                    if ini is None:
                        ini = s
                    fim = s
                elif ini is not None or s * A.RES > 0.15:
                    break
            esp = (fim - ini + 1) * A.RES if ini is not None else 0.0
            am.append(["parede" if esp >= parede_min else "vidro" if esp > 0 else "aberto", esp, t])
        # runs of one kind; a run under 30 cm takes its neighbour's kind
        corr = []
        for tipo, esp, t in am:
            if corr and corr[-1][0] == tipo:
                corr[-1][2].append(esp)
                corr[-1][1] = t
            else:
                corr.append([tipo, t, [esp], (t - 0.5 / N)])
        curto = 0.3 / (Lp * A.RES)
        for _ in range(2):
            for j, c in enumerate(corr):
                if c[1] + 0.5 / N - c[3] < curto and len(corr) > 1:
                    viz = corr[j - 1] if j else corr[j + 1]
                    c[0] = viz[0]
            fund = []
            for c in corr:
                if fund and fund[-1][0] == c[0]:
                    fund[-1][1] = c[1]
                    fund[-1][2] += c[2]
                else:
                    fund.append(c)
            corr = fund
        for tipo, t1, esps, t0 in corr:
            t1 += 0.5 / N
            p0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
            p1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            if tipo == "parede":
                pos = sorted(e for e in esps if e > 0) or [0.2]
                esp = pos[len(pos) // 2]
                d, ext = esp / 2 / A.RES, esp / 2 / A.RES
                p0 = (p0[0] + nx * d - ux * ext, p0[1] + ny * d - uy * ext)
                p1 = (p1[0] + nx * d + ux * ext, p1[1] + ny * d + uy * ext)
            else:
                esp, d = 0.0, 0.05 / A.RES
                p0 = (p0[0] + nx * d, p0[1] + ny * d)
                p1 = (p1[0] + nx * d, p1[1] + ny * d)
            out.append((p0, p1, tipo, round(esp, 3)))
    return out


def faces_terreno(d, cfg, centro, raio):
    cx, cy = centro
    out = []
    for f in d.faces3d(cfg["camadas"].get("terreno")):
        mx = sum(p[0] for p in f) / len(f)
        my = sum(p[1] for p in f) / len(f)
        if math.hypot(mx - cx, my - cy) <= raio:
            out.append(f)
    return out


def mobilia(d, cfg, p):
    X0, Y0, X1, Y1 = p["janela"]
    dx, dy = p.get("desloca", [0.0, 0.0])
    out = []
    for q in d.paths(camadas=cfg["camadas"].get("mobilia", [])):
        for sp, fechado in q["subs"]:
            if len(sp) < 4 or not all(X0 <= x <= X1 and Y0 <= y <= Y1 for x, y in sp):
                continue
            a = 0.0
            for (x0, y0), (x1, y1) in zip(sp, sp[1:] + sp[:1]):
                a += x0 * y1 - x1 * y0
            a = abs(a) / 2
            if not (0.08 <= a <= 6.0):
                continue
            xs, ys = [x for x, _ in sp], [y for _, y in sp]
            if math.hypot(sp[0][0] - sp[-1][0], sp[0][1] - sp[-1][1]) > 0.05 and not fechado:
                continue
            out.append({"poli": [(x + dx, y + dy) for x, y in sp], "area": a,
                        "caixa": (min(xs) + dx, min(ys) + dy, max(xs) + dx, max(ys) + dy)})
    return out


def construir(cfg):
    d = Dxf(cfg["dxf"])
    pisos = []
    for p in cfg["pisos"]:
        g = piso(d, cfg, p)
        g.update({"id": p["id"], "nome": p["nome"], "cota": p["cota"], "cota_acima": p["cota_acima"],
                  "divisoes": p.get("divisoes", []), "laje_m": p.get("laje_m", 0.30)})
        if p.get("mobilia", True):
            g["mobilia"] = mobilia(d, cfg, p)
        pisos.append(g)
        print(f"  {p['nome']}: {len(g['paredes'])} paredes, contorno {len(g['contorno'])} pontos, "
              f"{len(g.get('mobilia', []))} peças de mobília")
    # a storey that reuses another one's outline (a basement mostly under the house, open towards its ramp)
    por_id = {g["id"]: g for g in pisos}
    for p, g in zip(cfg["pisos"], pisos):
        if p.get("contorno_de") in por_id:
            g["contorno"] = por_id[p["contorno_de"]]["contorno"]
            g["fachada"] = []      # its own walls only: the borrowed outline says nothing about what closes it
    cob = []
    for c in cfg.get("coberturas", []):
        g = piso(d, cfg, c)
        cob.append({"contorno": g["contorno"], "cota": c["cota"], "espessura": c.get("espessura", 0.35), "nome": c.get("nome", "")})
    # local frame: centre of the reference storey's outline; z from the reference level
    ref = next(p for p in pisos if p["id"] == cfg["referencia"])
    cx = sum(x for x, _ in ref["contorno"]) / len(ref["contorno"])
    cy = sum(y for _, y in ref["contorno"]) / len(ref["contorno"])
    z0 = ref["cota"]

    def loc(pt):
        return [round(pt[0] - cx, 3), round(pt[1] - cy, 3)]
    out = {"nome": cfg["nome"], "referencia": cfg["referencia"], "cota_ref": z0, "pisos": [], "coberturas": [], "terreno": []}
    for g in pisos:
        out["pisos"].append({
            "id": g["id"], "nome": g["nome"], "z": round(g["cota"] - z0, 3), "z_acima": round(g["cota_acima"] - z0, 3),
            "cota": g["cota"], "laje": g["laje_m"], "divisoes": g["divisoes"], "contorno": [loc(p) for p in g["contorno"]],
            "paredes": [{"p0": loc(w["p0"]), "p1": loc(w["p1"]), "esp": round(w["esp"], 3),
                         "aberturas": [{"t0": round(o["t0"], 3), "t1": round(o["t1"], 3), "tipo": o["tipo"]} for o in w["aberturas"]]}
                        for w in g["paredes"]],
            "fachada": [{"p0": loc(f["p0"]), "p1": loc(f["p1"]), "tipo": f["tipo"], "esp": f["esp"]} for f in g.get("fachada", [])],
            "mobilia": [{"poli": [loc(p) for p in m_["poli"]]} for m_ in g.get("mobilia", [])]})
    for c in cob:
        out["coberturas"].append({"nome": c["nome"], "z": round(c["cota"] - z0, 3), "espessura": c["espessura"],
                                  "contorno": [loc(p) for p in c["contorno"]]})
    t = cfg.get("terreno")
    if t:
        for f in faces_terreno(d, cfg, (cx, cy), t.get("raio_m", 35)):
            out["terreno"].append([[round(p[0] - cx, 2), round(p[1] - cy, 2), round(p[2] - z0, 2)] for p in f])
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cfg_path = Path(sys.argv[1])
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["dxf"] = str((cfg_path.parent / cfg["dxf"]).resolve()) if not Path(cfg["dxf"]).is_absolute() else cfg["dxf"]
    m = construir(cfg)
    saida = Path(cfg.get("saida") or (cfg_path.parent / "modelo.json"))
    if not saida.is_absolute():
        saida = (cfg_path.parent / saida).resolve()
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    print(f"modelo: {saida} ({len(m['pisos'])} pisos, {len(m['coberturas'])} coberturas, {len(m['terreno'])} faces de terreno)")


if __name__ == "__main__":
    main()
