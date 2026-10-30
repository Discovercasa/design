"""The timber of an exposed roof on a plan house (casa_planta.py): ceiling beams, headers, edge beams, purlins, prumos,
hip and valley members and the empenas, from the roof surface of telhado.py. Pure Python.

The DiscoverCasa method (conhecimento/metodo-construtivo.md §6, §7 "Exposed roof — the build, in order", E1–E11; v7.1):
  - ceiling beams 22x7,5 at <= 1 m (glulam 20x10 at <= 0,92 past 8 m), always down the slope ("sempre inseridos no
    sentido da cobertura"), eave wall to eave wall, over the walls to their outer faces — in an L / T / U they turn
    with each wing (ours, to confirm), and under a wing wider than its body's depth, where its roof crosses the body,
    they run down the WING's slopes (telhado.py "zonas"; 2026-10-28); where one wing opens into another a glulam
    header carries the beam ends, between the edge beams (the hangers nailed to it — user 2026-10-28 "Prendem-se as
    vigas laranja"); a beam right under the top purlin of a slope whose purlins run with the beams (ours);
  - an edge beam 22x7,5 on every wall that runs along the beams (gable and hip-end walls): the empena stands on it
    (Sobral: "gable triangle on the tie beam"), the hip-end eave purlin rests on it;
  - purlins 110x75 flat, parallel to each slope's eaves, <= 1,2 apart in equal bays, the eave purlin on the beams
    right over the wall, the top one up to the ridge (meeting the other slope's: the pair is the ridge — user
    2026-10-29), each line one piece across the slope and on over the verge
    overhang; where a slope's purlins run along the ceiling beams (a hip end, a wing's end over its body, a body's
    slope where a wider wing crosses it) they lie on the beam lines, jointed over a prumo; every purlin stops against
    the side of a hip / valley member (fixed to it — ours);
  - a prumo 110x75 on every ceiling beam under every purlin (none where the purlin rests on the beam), one per place,
    its 75 across the beam and its top cut to the member's underside (user 2026-10-29);
  - hips and valleys (rincões, larós): a 110x75 on edge under the line, on prumos on the beams it crosses (ours), each
    stopping at the bisector where it meets another, its foot over the house cut to sit on the beams, free over the
    overhang (they had run into the purlins, each other and the edge beams — the user's screenshots, 2026-10-28;
    checked by ferramentas/configurador/auditar_cobertura.py);
  - empenas: estrutura_dc.emoldurar_empena (bottom plate, sloped top plates under the purlins, corner posts, studs at
    40 cm clear, a stud under the ridge).
"""
import math

from ferramentas.modelo.estrutura_dc import emoldurar_empena, membro


def _z(f, x, y):
    return f["z0"] + f["gx"] * x + f["gy"] * y


def _dentro_poly(poly, x, y, tol=1e-6):
    """Inside (or on) a convex counter-clockwise polygon."""
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1) < -tol:
            return False
    return True


def z_telhado(T, x, y):
    """The roof surface (top of the purlins) above a plan point, or None outside the roof."""
    zs = [_z(f, x, y) for f in T["faces"] if _dentro_poly(f["pts"], x, y)]
    return max(zs) if zs else None


def _segmento_poly(poly, p0, u, L):
    """The part [t0, t1] of the segment p0 + t u (0 <= t <= L) inside a convex polygon, or None."""
    t0, t1 = 0.0, L
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        # inside: ex (y - y1) - ey (x - x1) >= 0 ; along the segment: f(t) = f0 + t df
        f0 = ex * (p0[1] - y1) - ey * (p0[0] - x1)
        df = ex * u[1] - ey * u[0]
        if abs(df) < 1e-12:
            if f0 < -1e-9:
                return None
            continue
        t = -f0 / df
        if df > 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
    return (t0, t1) if t1 - t0 > 1e-4 else None


def _unir(ivs, tol=0.01):
    out = []
    for a, b in sorted(ivs):
        if out and a <= out[-1][1] + tol:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def _cortar(poly, a, b, c):
    """The part of a convex plan polygon where a x + b y + c >= 0."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = a * p[0] + b * p[1] + c, a * q[0] + b * q[1] + c
        if fp >= 0:
            out.append(p)
        if (fp > 0 > fq) or (fp < 0 < fq):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out if len(out) >= 3 else []


def _folga_topo(T, a, b, c, dm):
    """How far a slope's top purlin stays off its top line (plane a x + b y + c = d, top at d = dm): at a ridge it runs
    up to it and meets the other slope's top purlin there — the pair is the ridge (user 2026-10-29: "junto as cumeeiras
    as vigas não encaixam nas cumeeiras estão simplesmente retas e próximas das cumeeiras o que não é suposto"; they had
    stood 0,05 off it, a 0,10 gap between them; 1 mm kept so each stays on its own slope); off any other top 0,05."""
    return 0.001 if any(ln["tipo"] == "cumeeira" and all(abs(a * q[0] + b * q[1] + c - dm) < 2e-3 for q in (ln["p0"], ln["p1"]))
                        for ln in T["linhas"]) else 0.05


def _caixa_na_faixa(bx, fx):
    """A plan box (x0, x1, y0, y1) overlapping a hip / valley member (start, along, across, length, half width)."""
    (px, py), (mx, my), (nx, ny), L, hw = fx
    poly = [(bx[0], bx[2]), (bx[1], bx[2]), (bx[1], bx[3]), (bx[0], bx[3])]
    for a, b, c in ((nx, ny, hw - nx * px - ny * py), (-nx, -ny, hw + nx * px + ny * py),
                    (mx, my, -(mx * px + my * py)), (-mx, -my, L + mx * px + my * py)):
        poly = _cortar(poly, a, b, c - 0.002)
        if not poly:
            return False
    return True


def construir(T, ctx):
    """The pieces of the exposed roof. ctx: {"z_e" (top of the eave purlin over the wall line, the roof's z = 0),
    "z_teto", "z_vig", "vt" (ceiling beams JSON), "lam" (glulam JSON), "va" (purlins JSON), "pr" (prumos JSON),
    "exts" (exterior walls of casa_planta), "peca", "caixa", "prisma", "te", "ext_c", "E", "alcados", "paineis"} →
    {"vigas_pav", "n_madres", "n_prumos", "n_empenas", "vigas" [(eixo, p, s0, s1, z_topo)]}."""
    peca, caixa, prisma = ctx["peca"], ctx["caixa"], ctx["prisma"]
    vt, lam, va, pr = ctx["vt"], ctx["lam"], ctx["va"], ctx["pr"]
    z_teto, z_vig, z_e = ctx["z_teto"], ctx["z_vig"], ctx["z_e"]
    exts, te = ctx["exts"], ctx["te"]
    wv, hv = va["largura"], va["altura"]
    esp_p = va["espacamento_max"]
    out = {"vigas_pav": [], "n_madres": 0, "n_prumos": 0, "n_empenas": 0, "vigas": []}
    abs_f = []  # faces with absolute heights
    for f in T["faces"]:
        abs_f.append({**f, "z0": f["z0"] + z_e})
    TA = {**T, "faces": abs_f}

    def parede_em(eixo_parede, coord, s0, s1):
        """Exterior walls along `eixo_parede` ("x": along X) whose outer face is on the line `coord`, covering
        [s0, s1]: the covered intervals."""
        ivs = []
        for w in exts:
            if w["eixo"] != eixo_parede:
                continue
            fora = w["f1"] if w["lado_exterior"] > 0 else w["f0"]
            if abs(fora - coord) > 0.02:
                continue
            a, b = max(w["a"], s0), min(w["b"], s1)
            if b - a > 0.01:
                ivs.append((a, b))
        return _unir(ivs)

    planos_t = {}  # the roof's slopes, each rectangle's part of a plane apart (its own top): (plane, ret) -> faces
    for f in T["faces"]:
        planos_t.setdefault((tuple(f["plano"]), f["ret"]), []).append(f)

    # ------------------------------------------------------------------ ceiling beams per zone (each rectangle's own part)
    vigas = []  # (eixo of the beam, position across, s0, s1 along, z of its top, width, kind)
    zonas = []  # (box, eixo of its beams): where each set of beams is — a wing over its parent takes that part
    for k, r, zb, n_z in [(k, r, zb, f"{k + 1}" + ("abcdefgh"[j - 1] if j else ""))
                          for k, r in enumerate(T["retangulos"]) for j, zb in enumerate(r.get("zonas") or [r["proprio"]])]:
        x0, x1, y0, y1 = zb
        ao_longo = "y" if r["eixo"] == "x" else "x"  # down the slope: across the ridge
        zonas.append(((x0, x1, y0, y1), ao_longo))
        if ao_longo == "y":
            p0_, p1_, s0_, s1_ = x0, x1, y0, y1  # positions along x, beams from y0 to y1
        else:
            p0_, p1_, s0_, s1_ = y0, y1, x0, x1
        vao = s1_ - s0_
        # the beam ends: on the wall at each end (over it to its outer face), or on a header where the side is open
        ends = []
        for s_lado in (s0_, s1_):
            eixo_lado = "x" if ao_longo == "y" else "y"
            cob = parede_em(eixo_lado, s_lado, p0_, p1_)
            ends.append(cob)
        # the free span (rulebook §6: 22x7,5 up to 8 m of FREE span, glulam beyond): between the walls' inner faces
        livre_v = vao - (te if ends[0] else 0.10) - (te if ends[1] else 0.10)
        sec = lam if (lam and livre_v > 8.0 + 1e-6) else vt
        larg, alt = sec["largura"], sec["altura"]
        passo = sec.get("espacamento_max", sec.get("espacamento", 1.0))
        cabecas = []  # headers: (side coordinate, interval along the side, inwards sign)
        for s_lado, cob, sg in ((s0_, ends[0], 1), (s1_, ends[1], -1)):
            livre, cur = [], p0_
            for a, b in cob:
                if a - cur > 0.3:
                    livre.append((cur, a))
                cur = max(cur, b)
            if p1_ - cur > 0.3:
                livre.append((cur, p1_))
            for a, b in livre:
                cabecas.append((s_lado, a, b, sg))
        # beam positions: between the side walls' inner faces (or the zone edge where the side is open)
        lado_p0 = parede_em(ao_longo, p0_, s0_, s1_)
        lado_p1 = parede_em(ao_longo, p1_, s0_, s1_)
        pa = p0_ + (te if lado_p0 else 0.0) + larg / 2
        pb = p1_ - (te if lado_p1 else 0.0) - larg / 2
        # a beam right under the top purlin of a slope whose purlins run with these beams (a wing's end over its
        # body, the body's slope where a wider wing crosses it): on the beam lines alone its top had up to a bay bare
        # under the ridge, the valley's top end in the air — ours; the bays between stay equal and <= the spacing
        fixos = []
        for ((a_p, b_p, c_p), _r), fs_p in planos_t.items():
            sub_x = abs(a_p) > 0.5
            if ("y" if sub_x else "x") != ao_longo:
                continue
            d_m = max(a_p * x + b_p * y + c_p for f in fs_p for x, y in f["pts"])
            d_t = d_m - _folga_topo(T, a_p, b_p, c_p, d_m) - wv / 2
            pos = (d_t - c_p) / a_p if sub_x else (d_t - c_p) / b_p
            # (the two top purlins meeting at a ridge get a beam each, side by side — 1 cm apart under a glulam zone)
            if not pa + larg + 0.02 < pos < pb - larg - 0.02 or any(abs(pos - q) < larg + 0.005 for q in fixos):
                continue
            q0 = (pos, s0_) if ao_longo == "y" else (s0_, pos)
            dirv = (0.0, 1.0) if ao_longo == "y" else (1.0, 0.0)
            if sum(b_s - a_s for a_s, b_s in _unir([s for f in fs_p for s in [_segmento_poly(f["pts"], q0, dirv, s1_ - s0_)]
                                                     if s])) >= 0.6:
                fixos.append(pos)
        # and a beam under the top of every rincão / laró over the zone (their prumo at the apex: the top had hung
        # ≈ 0,9 past the last beam it crossed — ours)
        for ln in T["linhas"]:
            if ln["tipo"] not in ("rincao", "laro"):
                continue
            px, py, _zq = max((ln["p0"], ln["p1"]), key=lambda q: q[2])
            if not (x0 - 1e-6 <= px <= x1 + 1e-6 and y0 - 1e-6 <= py <= y1 + 1e-6):
                continue
            pos = px if ao_longo == "y" else py
            if pa + larg + 0.02 < pos < pb - larg - 0.02 and all(abs(pos - q) >= larg + 0.02 for q in fixos):
                fixos.append(pos)
        ps = []
        anc = [pa] + sorted(fixos) + [pb]
        for a_, b_ in zip(anc, anc[1:]):
            n_ = max(1, math.ceil((b_ - a_) / passo - 1e-9))
            ps += [a_ + (b_ - a_) * i / n_ for i in range(n_)]
        ps.append(pb)
        hl = lam["largura"] if lam else 0.10
        for i, p in enumerate(ps):
            a_, b_ = s0_, s1_
            for s_lado, a, b, sg in cabecas:  # a header across this beam's end: the beam ends at its face
                if a - larg / 2 - 0.005 <= p <= b + larg / 2 + 0.005:  # (any of its width: one at the corner had run into it)
                    if sg > 0:
                        a_ = max(a_, s_lado + hl)
                    else:
                        b_ = min(b_, s_lado - hl)
            zt = z_teto + alt
            nome = f"Viga de apoio ao teto Z{n_z}.{i + 1:02d}" if sec is vt else f"Lamelada Z{n_z}.{i + 1:02d}"
            if ao_longo == "y":
                pc = [caixa(p - larg / 2, p + larg / 2, a_, b_, z_teto, zt)]
                out["vigas_pav"].append({"x0": round(p - larg / 2, 4), "x1": round(p + larg / 2, 4), "y0": round(a_, 4), "y1": round(b_, 4)})
            else:
                pc = [caixa(a_, b_, p - larg / 2, p + larg / 2, z_teto, zt)]
                out["vigas_pav"].append({"x0": round(a_, 4), "x1": round(b_, 4), "y0": round(p - larg / 2, 4), "y1": round(p + larg / 2, 4)})
            peca(nome, "1.7", sec["seccao"], "Viga de apoio ao teto" if sec is vt else "Lamelada", pc, b_ - a_,
                 (b_ - a_) * larg * alt, vao_m=round(vao, 3))
            vigas.append((ao_longo, p, a_, b_, zt, larg, "viga"))
        for s_lado, a, b, sg in cabecas:  # glulam header (ours: the open side of a wing has no wall to bear on)
            # from wall to wall, between the edge beams on them (it had run over the edge beam at the corner)
            a, b = max(a, pa - larg / 2), min(b, pb + larg / 2)
            if b - a < 0.3:
                continue
            h_sec = lam or {"seccao": "200x100", "largura": 0.10, "altura": 0.20}
            c0, c1 = sorted((s_lado, s_lado + sg * h_sec["largura"]))
            if ao_longo == "y":
                pc = [caixa(a, b, c0, c1, z_teto, z_teto + h_sec["altura"])]
            else:
                pc = [caixa(c0, c1, a, b, z_teto, z_teto + h_sec["altura"])]
            peca(f"Viga de bordadura Z{n_z} ({a:.2f}-{b:.2f})", "1.7", h_sec["seccao"], "Viga de bordadura (lamelada)",
                 pc, b - a, (b - a) * h_sec["largura"] * h_sec["altura"], assumido="apoio das vigas onde a ala abre (nosso)")
        # edge beams on the walls along the beams (gable / hip-end walls): the empena or the eave purlin on them
        for p_lado, cob in ((p0_, lado_p0), (p1_, lado_p1)):
            sg = 1 if p_lado == p0_ else -1
            for a, b in cob:
                cm = p_lado + sg * te / 2  # a 22x7,5 on the middle of the wall's frame (as its section says)
                c0, c1 = cm - vt["largura"] / 2, cm + vt["largura"] / 2
                if ao_longo == "y":
                    pc = [caixa(c0, c1, a, b, z_teto, z_vig)]
                    out["vigas_pav"].append({"x0": round(c0, 4), "x1": round(c1, 4), "y0": round(a, 4), "y1": round(b, 4)})
                else:
                    pc = [caixa(a, b, c0, c1, z_teto, z_vig)]
                    out["vigas_pav"].append({"x0": round(a, 4), "x1": round(b, 4), "y0": round(c0, 4), "y1": round(c1, 4)})
                peca(f"Viga de bordo Z{n_z} ({a:.2f}-{b:.2f})", "1.7", vt["seccao"], "Viga de bordo (sobre a parede)", pc,
                     b - a, (b - a) * vt["largura"] * vt["altura"])
                vigas.append((ao_longo, cm, a, b, z_vig, vt["largura"], "borda"))
    out["vigas"] = vigas

    # every prumo / calço placed (plan box, z range): one place, one prumo — a purlin's and a hip's on the same beam
    # crossing had stood one inside the other (the user's screenshots, 2026-10-28)
    postos = []

    def prumo(x, y, z_base, topo, nome, eixo_viga, membro=False):
        """A prumo on the beam running along `eixo_viga` at (x, y): its 75 across the beam (the beam's width), its 110
        along it — turned with the beam (JSON prumos: largura_x = across, largura_y = along). Its top cut to the
        underside of the member it carries, topo(x, y) (user 2026-10-29: the prumos where the L forms had "uma viga
        pousada a metade da sua largura e a viga nem encaixa totalmente nessa peça vertical" — they kept one
        orientation in every wing and a flat top under a sloping member)."""
        lx, ly = (pr["largura_x"], pr["largura_y"]) if eixo_viga == "y" else (pr["largura_y"], pr["largura_x"])
        bx = (x - lx / 2, x + lx / 2, y - ly / 2, y + ly / 2)
        cantos = [(bx[0], bx[2]), (bx[1], bx[2]), (bx[1], bx[3]), (bx[0], bx[3])]
        zs = [topo(cx, cy) for cx, cy in cantos]
        h = min(zs) - z_base
        if h < 0.003:
            return  # the member rests on the beam
        if any(min(bx[1], q[1]) - max(bx[0], q[0]) > 0.005 and min(bx[3], q[3]) - max(bx[2], q[2]) > 0.005
               for q in postos):
            return  # another member's prumo stands there already
        if not membro and any(_caixa_na_faixa(bx, fx) for fx in faixas_m):
            return  # under a hip / valley member: its own prumos carry it (a purlin ends against its side there)
        postos.append(bx)
        pc = [{"b": [[round(cx, 4), round(cy, 4), round(z_base, 4)] for cx, cy in cantos],
               "t": [[round(cx, 4), round(cy, 4), round(z_, 4)] for (cx, cy), z_ in zip(cantos, zs)]}]
        h_m = sum(zs) / 4 - z_base
        if h < 0.03:  # too short for a prumo (a glulam zone sits 2 cm under the 22x7,5 level): a packing piece
            peca(nome.replace("Prumo", "Calço"), "1.9", pr["seccao"], "Calço", pc, h_m, h_m * lx * ly)
            return
        out["n_prumos"] += 1
        peca(nome, "1.9", pr["seccao"], "Prumo", pc, h_m, h_m * lx * ly)

    # ------------------------------------------------------------------ hips and valleys: a 110x75 on edge under the line
    # (before the purlins: these stop against its sides, and its prumos come first where both cross a beam)
    w2 = 0.0375  # half its 75
    linhas_m = [ln for ln in T["linhas"] if ln["tipo"] in ("rincao", "laro")
                and math.hypot(ln["p1"][0] - ln["p0"][0], ln["p1"][1] - ln["p0"][1]) >= 0.2]
    casa_rs = [r["proprio"] for r in T["retangulos"]]

    def sobre_casa(x, y):  # over the walls and the rooms (the ceiling beams reach the walls' outer faces)
        return any(r0 - 1e-6 <= x <= r1 + 1e-6 and s0 - 1e-6 <= y <= s1 + 1e-6 for r0, r1, s0, s1 in casa_rs)

    faixas_m = []  # each member in plan: (start, unit along, unit across, length, half width) — the purlins keep out
    sob_m, prumos_m = [], []  # each member's band with its underside; the prumos under the members
    k_h = 0
    for ln in linhas_m:
        (x0, y0, z0r), (x1, y1, z1r) = ln["p0"], ln["p1"]
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -uy, ux
        # where it meets another hip / valley each stops at the bisector (they had run into each other at the apex):
        # each side (across -w2, +w2) cut on its own — against one member met there a mitre, the two faces on the
        # bisector (user 2026-10-29: "existem ainda gaps entre as vigas"; they had stopped square, a V open between)
        cortes, mitras = [], []
        for (px, py), sg in (((x0, y0), 1), ((x1, y1), -1)):
            lados_c = [None, None]
            for o in linhas_m:
                if o is ln:
                    continue
                for q, r_ in ((o["p0"], o["p1"]), (o["p1"], o["p0"])):
                    if math.hypot(q[0] - px, q[1] - py) < 1e-3:
                        Lo = math.hypot(r_[0] - q[0], r_[1] - q[1])
                        phi = math.acos(max(-1.0, min(1.0, (sg * ux * (r_[0] - q[0]) + sg * uy * (r_[1] - q[1])) / Lo)))
                        if phi < math.radians(179):
                            k_ = w2 / math.tan(phi / 2)
                            do_lado = 1 if (r_[0] - q[0]) * nx + (r_[1] - q[1]) * ny > 0 else 0  # the side it is on
                            for i_ in (0, 1):
                                v_ = k_ if i_ == do_lado else -k_
                                lados_c[i_] = v_ if lados_c[i_] is None else max(lados_c[i_], v_)
            lados_c = [v_ + 0.002 if v_ is not None else 0.0 for v_ in lados_c]
            mitras.append(lados_c)
            cortes.append(max(lados_c))
        ta, tb = cortes[0], L - cortes[1]
        mitra_a, mitra_b = mitras[0], [L - v_ for v_ in mitras[1]]
        if tb - ta < 0.2:
            continue
        k_h += 1
        t_lo, t_hi = min(mitra_a), max(mitra_b)  # where it is (trimmed; the mitres' points included)
        faixas_m.append(((x0 + ux * t_lo, y0 + uy * t_lo), (ux, uy), (nx, ny), t_hi - t_lo, w2))
        # a hip is a convex crease: the slopes fall away on both sides, so the member drops until its top edges are
        # under them; in a valley they rise from it
        baixa = T["t"] * w2 * math.sqrt(2) + 0.002 if ln["tipo"] == "rincao" else 0.0

        def z_top(tt, x0=x0, z0r=z0r, z1r=z1r, L=L, baixa=baixa):
            return z_e + z0r + (z1r - z0r) * tt / L - baixa

        def pt(tt, x0=x0, y0=y0, ux=ux, uy=uy):
            return (x0 + ux * tt, y0 + uy * tt)

        def sobre(tt, nx=nx, ny=ny):  # any of its width over the house
            (px, py) = pt(tt)
            return any(sobre_casa(px + nx * o, py + ny * o) for o in (-w2, 0.0, w2))
        # over the house its foot sits on the ceiling beams (cut to them, the depth left as it falls to the eave —
        # it had gone 3-4 cm into the edge beam and the beams at every eave corner); over the overhang it hangs free
        quebras = {ta, tb}
        dz = (z1r - z0r) / L
        if abs(dz) > 1e-9:
            tv = (z_vig + 0.11 + baixa - z_e - z0r) / dz
            if ta < tv < tb:
                quebras.add(tv)
        n_s = max(2, int((tb - ta) / 0.01))
        dentro_ant = sobre(ta)
        for i in range(1, n_s + 1):
            tt = ta + (tb - ta) * i / n_s
            d_ = sobre(tt)
            if d_ != dentro_ant:
                quebras.add(tt - (tb - ta) / n_s / 2)
                dentro_ant = d_
        qs = sorted(quebras)
        nome = "Rincão" if ln["tipo"] == "rincao" else "Laró"
        pecas_m = []
        comp_m = 0.0
        for s_, e_ in zip(qs, qs[1:]):
            if e_ - s_ < 0.005:
                continue
            assenta = sobre((s_ + e_) / 2) and z_top((s_ + e_) / 2) - 0.11 < z_vig - 1e-4
            if assenta and max(z_top(s_), z_top(e_)) < z_vig + 0.01:
                continue  # no depth left above the beams

            def sec(tt, assenta=assenta, tts=None):  # tts: each side's own t (a mitred end)
                out_ = []
                for i_, (sgn, cima) in enumerate(((-1, False), (1, False), (1, True), (-1, True))):
                    t_ = tts[0 if sgn < 0 else 1] if tts else tt
                    (px, py), zt_ = pt(t_), z_top(t_)
                    zb_ = max(z_vig, zt_ - 0.11) if assenta else zt_ - 0.11
                    out_.append([round(px + sgn * nx * w2, 4), round(py + sgn * ny * w2, 4), round(zt_ if cima else zb_, 4)])
                return out_
            pecas_m.append({"b": sec(s_, tts=mitra_a if abs(s_ - ta) < 1e-9 else None),
                            "t": sec(e_, tts=mitra_b if abs(e_ - tb) < 1e-9 else None)})
            comp_m += math.hypot(e_ - s_, z_top(e_) - z_top(s_))
        if not pecas_m:
            continue
        peca(f"{nome} {k_h:02d}", "1.9", "110x75", f"{nome} (110x75 ao alto, nosso)", pecas_m, comp_m, comp_m * 0.075 * 0.11)
        out["n_madres"] += 1
        # prumos where it crosses the beams (placed once every member is known: at an apex another one passes over)

        def sob_membro(cx, cy, x0=x0, y0=y0, ux=ux, uy=uy, ta=t_lo, tb=t_hi, z_top=z_top):
            return z_top(min(max((cx - x0) * ux + (cy - y0) * uy, ta), tb)) - 0.11
        sob_m.append((faixas_m[-1], sob_membro))
        for (eixo_v, p, s0, s1, zt, larg, _k) in vigas:
            if eixo_v == "y":
                if abs(ux) < 1e-9:
                    continue
                tt = (p - x0) / ux
                y = y0 + uy * tt
                if ta - 0.08 <= tt <= tb + 0.08 and s0 <= y <= s1:  # (a beam just past its end: under the apex)
                    prumos_m.append((p, y, zt, sob_membro, f"Prumo {nome} {k_h:02d} x{p:.2f}", "y"))
            else:
                if abs(uy) < 1e-9:
                    continue
                tt = (p - y0) / uy
                x = x0 + ux * tt
                if ta - 0.08 <= tt <= tb + 0.08 and s0 <= x <= s1:
                    prumos_m.append((x, p, zt, sob_membro, f"Prumo {nome} {k_h:02d} y{p:.2f}", "x"))
    # their tops cut to the underside of the member above, as it rises along its line — or of another member passing
    # lower over a corner of the prumo (at an apex where two meet)
    for x, y, zt, sob_proprio, nm, eixo in prumos_m:

        def topo_m(cx, cy, sob_proprio=sob_proprio):
            zs = [sob_proprio(cx, cy)]
            for ((px, py), (mx, my), (nx_, ny_), Lm, hw), sob_o in sob_m:
                t_, s_ = (cx - px) * mx + (cy - py) * my, (cx - px) * nx_ + (cy - py) * ny_
                if -0.002 <= t_ <= Lm + 0.002 and abs(s_) <= hw + 0.002:
                    zs.append(sob_o(cx, cy))
            return min(zs)
        prumo(x, y, zt, topo_m, nm, eixo, membro=True)

    # ------------------------------------------------------------------ purlins, slope by slope
    # one slope = one plane: one set of purlin lines, at one spacing, across all its pieces (rulebook X8); where the
    # beams below run WITH the purlins (a hip end; a wing's slope over its body's beams) the purlins of that part lie
    # on the beam lines instead, on prumos along the beam (rulebook §6 b) — they had crossed no beam there and got no
    # prumo (the user's U, 2026-10-28: "parecem haver vigas em falta"); every purlin stops against the side of a hip
    # or valley member ("umas vigas passam em cima das outras")
    planos = {}
    for f in abs_f:
        planos.setdefault(tuple(round(v, 6) for v in f["plano"]), []).append(f)

    def fora_das_faixas(q0, uu, t0, t1, membros=False):
        """The parts of [t0, t1] of a purlin (axis q0 + t uu, wv wide) clear of the hip / valley members — with
        membros, (t0, t1, m0, m1): the member each end stops against (its index in faixas_m), or None."""
        ivs = [(t0, t1, None, None)]
        nu = (-uu[1], uu[0])
        for i_m, ((px, py), (mx, my), (nx_, ny_), Lm, hw) in enumerate(faixas_m):
            hw += 0.002
            band = [(q0[0] + uu[0] * t_ + nu[0] * s_, q0[1] + uu[1] * t_ + nu[1] * s_)
                    for t_, s_ in ((t0, -wv / 2), (t1, -wv / 2), (t1, wv / 2), (t0, wv / 2))]
            for a_, b_, c_ in ((nx_, ny_, hw - nx_ * px - ny_ * py), (-nx_, -ny_, hw + nx_ * px + ny_ * py),
                               (mx, my, -(mx * px + my * py)), (-mx, -my, Lm + mx * px + my * py)):
                band = _cortar(band, a_, b_, c_)
                if not band:
                    break
            if not band:
                continue
            ts = [(vx - q0[0]) * uu[0] + (vy - q0[1]) * uu[1] for vx, vy in band]
            lo, hi = min(ts), max(ts)
            ivs = [iv for a_, b_, ma, mb in ivs for iv in ((a_, min(b_, lo), ma, i_m if lo < b_ else mb),
                                                            (max(a_, hi), b_, i_m if hi > a_ else ma, mb)) if iv[1] - iv[0] > 1e-4]
        return ivs if membros else [iv[:2] for iv in ivs]

    def ponta_obliqua(i_m, q0, uu, t_fim, t_dentro):
        """A purlin's end against the side of hip / valley member i_m, cut on the skew (user 2026-10-29: "no máximo
        podemos cortar a vigas com a diagonal necessária para encaixar as vigas umas na outras" — square ends had left
        a triangle open at every hip): the t of each long edge (across -wv/2, +wv/2) on that side, 2 mm off it."""
        (px, py), (mx, my), (nx_, ny_), Lm, hw = faixas_m[i_m]
        den = uu[0] * nx_ + uu[1] * ny_
        if abs(den) < 0.05:
            return (t_fim, t_fim)
        nu = (-uu[1], uu[0])
        lado = 1 if ((q0[0] + uu[0] * t_dentro - px) * nx_ + (q0[1] + uu[1] * t_dentro - py) * ny_) > 0 else -1
        res = []
        for off in (-wv / 2, wv / 2):
            dq = (q0[0] + nu[0] * off - px) * nx_ + (q0[1] + nu[1] * off - py) * ny_
            te_ = (lado * (hw + 0.002) - dq) / den
            # never short of the square cut, never more than 0,6 past it; only where the member is (an edge running
            # on past its end, at an apex, met the next member) and clear of every other member
            te_ = min(max(te_, t_fim), t_fim + 0.6) if t_fim > t_dentro else max(min(te_, t_fim), t_fim - 0.6)
            ex, ey = q0[0] + uu[0] * te_ + nu[0] * off, q0[1] + uu[1] * te_ + nu[1] * off
            ao_longo = (ex - px) * mx + (ey - py) * my
            if not -0.005 <= ao_longo <= Lm + 0.005 or not aresta_livre(q0, uu, off, t_fim, te_, i_m):
                return (t_fim, t_fim)  # square, as before (one edge skewed, the other not, cut into the member's end)
            res.append(te_)
        return tuple(res)

    def aresta_livre(q0, uu, off, t_a, t_b, excluir):
        """A purlin's long edge (across off) from t_a to t_b touches no hip / valley member but `excluir`."""
        t_a, t_b = sorted((t_a, t_b))
        if t_b - t_a < 1e-4:
            return True
        nu = (-uu[1], uu[0])
        for i_m, ((px, py), (mx, my), (nx_, ny_), Lm, hw) in enumerate(faixas_m):
            if i_m == excluir:
                continue
            band = [(q0[0] + uu[0] * t_ + nu[0] * (off + s_), q0[1] + uu[1] * t_ + nu[1] * (off + s_))
                    for t_, s_ in ((t_a, -0.002), (t_b, -0.002), (t_b, 0.002), (t_a, 0.002))]
            for a_, b_, c_ in ((nx_, ny_, hw + 0.002 - nx_ * px - ny_ * py), (-nx_, -ny_, hw + 0.002 + nx_ * px + ny_ * py),
                               (mx, my, -(mx * px + my * py)), (-mx, -my, Lm + mx * px + my * py)):
                band = _cortar(band, a_, b_, c_)
                if not band:
                    break
            if band:
                return False
        return True

    k_l = 0
    for fs in sorted(planos.values(), key=lambda fs: (min(f["ret"] for f in fs), fs[0]["nome"])):
        k_r, nome_p = min(f["ret"] for f in fs), fs[0]["nome"]
        a, b, c = fs[0]["plano"]  # eave distance d = a x + b y + c (unit normal, uphill)
        t = T["t"]
        d_max = max(a * x + b * y + c for f in fs for x, y in f["pts"])
        if d_max < 0.3:
            continue
        subida_eixo = "x" if abs(a) > 0.5 else "y"
        u = (-b, a)  # along the eaves
        eixo_u = "y" if subida_eixo == "x" else "x"

        def no_telhado(p0_, dirv, L_, so=None):
            """The parts of a segment over this slope (or over the faces `so` only), where BOTH long edges of the
            purlin stay on it (at a hip the other slope is lower: a purlin cut on its axis would stick out there)."""
            listas = []
            for off in (-wv / 2, 0.0, wv / 2 - 0.004):  # (the top one may stand on the ridge line: 4 mm in)
                q = (p0_[0] + a * off, p0_[1] + b * off)
                listas.append(_unir([seg for f in (so or fs) for seg in [_segmento_poly(f["pts"], q, dirv, L_)] if seg], 0.02))
            res = listas[0]
            for outra in listas[1:]:
                res = [(max(x0, y0), min(x1, y1)) for x0, x1 in res for y0, y1 in outra if min(x1, y1) - max(x0, y0) > 1e-4]
            return res

        # the parts of the slope over beams that run with its purlins
        paralelas = [z for z, ao in zonas if ao == eixo_u]
        linhas = []
        # one set of lines across the plane, equal bays <= esp_p up to its top (aligned over two rectangles on one
        # plane — X8); a lower rectangle's part of it (a wing's slope, its ridge lower) also gets a purlin under its
        # own ridge, over that part only, unless a line of the set is already there. At a ridge the top purlin runs up
        # to the ridge line and meets the other slope's there (_folga_topo)
        d_e, d_t = wv / 2, max(wv / 2, d_max - _folga_topo(T, a, b, c, d_max) - wv / 2)
        nb = max(1, math.ceil((d_t - d_e) / esp_p - 1e-9)) if d_t - d_e > 0.05 else 0
        ds = [(d_e + (d_t - d_e) * i / nb, None) for i in range(nb + 1)] if nb else [(d_e, None)]
        topo_r = {}
        for f in fs:
            topo_r[f["ret"]] = max(topo_r.get(f["ret"], 0.0), max(a * x + b * y + c for x, y in f["pts"]))
        for k2, dm in sorted(topo_r.items()):
            d_k = dm - _folga_topo(T, a, b, c, dm) - wv / 2
            if dm < d_max - 0.05 and d_k > d_e + 0.05 and all(abs(d_k - d) > 0.05 for d, _so in ds):
                ds.append((d_k, [f for f in fs if f["ret"] == k2]))
        for d, so in ds:
            # the line a x + b y + c = d: a point on it, then clip it to the slope's pieces, off the parallel zones
            p_ref = (a * (d - c), b * (d - c))
            ini = (p_ref[0] - u[0] * 1000, p_ref[1] - u[1] * 1000)
            pos = p_ref[1] if eixo_u == "x" else p_ref[0]  # the line's place across
            for t0, t1 in no_telhado(ini, u, 2000, so):
                segs = [(t0, t1)]
                for zx0, zx1, zy0, zy1 in paralelas:
                    lo_c, hi_c = (zy0, zy1) if eixo_u == "x" else (zx0, zx1)
                    if not lo_c + 1e-6 < pos < hi_c - 1e-6:
                        continue
                    lo_a, hi_a = (zx0, zx1) if eixo_u == "x" else (zy0, zy1)
                    # along the line: t = (coordinate - ini) / u (u is +-1 on its axis)
                    k_ax = 0 if eixo_u == "x" else 1
                    t_lo, t_hi = sorted(((lo_a - ini[k_ax]) / u[k_ax], (hi_a - ini[k_ax]) / u[k_ax]))
                    segs = [s for a_, b_ in segs for s in ((a_, min(b_, t_lo)), (max(a_, t_hi), b_)) if s[1] - s[0] > 1e-4]
                for s0, s1 in segs:
                    for s0_, s1_, m0_, m1_ in fora_das_faixas(ini, u, s0, s1, True):
                        linhas.append((d, (ini[0] + u[0] * s0_, ini[1] + u[1] * s0_), s1_ - s0_, None, None, None, m0_, m1_))
        # on the beam lines of those parts (the eave purlin over a wall on its edge beam), above the eave purlin; a
        # beam next to the edge beam carries none (two purlins 12 cm apart had stood one into the other)
        tomadas = []  # (d, s0, s1) of the beam lines used
        for (eixo_v, p, s0, s1, zt, larg, _k) in sorted(vigas, key=lambda v: v[6] != "borda"):
            if eixo_v != eixo_u:
                continue
            d = (a * p + c) if subida_eixo == "x" else (b * p + c)
            if d < wv / 2 - 1e-6 or d > d_max - 0.05:
                continue
            if any(abs(d - d2) < wv + 0.04 and min(s1, b2) - max(s0, a2) > 0.05 for d2, a2, b2 in tomadas):
                continue
            tomadas.append((d, s0, s1))
            pt0 = (p, s0) if eixo_u == "y" else (s0, p)
            uu = (0.0, 1.0) if eixo_u == "y" else (1.0, 0.0)
            for t0, t1 in no_telhado(pt0, uu, s1 - s0):
                for t0_, t1_, m0_, m1_ in fora_das_faixas(pt0, uu, t0, t1, True):
                    linhas.append((d, (pt0[0] + uu[0] * t0_, pt0[1] + uu[1] * t0_), t1_ - t0_, uu, zt, (s0, s1), m0_, m1_))
        for d, q0, comp, uu_v, zt_v, viga_s, m_ini, m_fim in linhas:
            uu = uu_v or u
            if comp < 0.2:
                continue
            def junto_membro(t_, r=0.15, q0=q0, uu=uu):  # an end at a hip / valley member (fixed to its side)
                px_, py_ = q0[0] + uu[0] * t_, q0[1] + uu[1] * t_
                return any(-r <= (px_ - fx[0][0]) * fx[1][0] + (py_ - fx[0][1]) * fx[1][1] <= fx[3] + r and
                           abs((px_ - fx[0][0]) * fx[2][0] + (py_ - fx[0][1]) * fx[2][1]) <= fx[4] + r for fx in faixas_m)
            if uu_v is None:  # a free end just short of a beam (a lower wing's slope stopping at the higher body's gable,
                # its first beam under the gable): the purlin runs on over that beam to its prumo — it had hung 0,86
                # free (a garage attached to a rectangle, 2026-10-29); an end at a hip / valley member stays there
                ini_livre, fim_livre = not junto_membro(0.0), not junto_membro(comp)
                for (eixo_v, p, s0b, s1b, zt, larg, kind) in vigas:
                    if kind == "borda" or (eixo_v == "y") == (abs(uu[1]) > 0.5):
                        continue
                    k_ax = 0 if eixo_v == "y" else 1  # the coordinate along the purlin
                    if abs(uu[k_ax]) < 1e-9:
                        continue
                    tt = (p - q0[k_ax]) / uu[k_ax]
                    if not s0b - 0.01 <= q0[1 - k_ax] + uu[1 - k_ax] * tt <= s1b + 0.01:
                        continue
                    if ini_livre and -(0.13 + larg / 2) <= tt < -0.01:
                        ext = -tt + larg / 2 - 0.006
                        if fora_das_faixas(q0, uu, -ext, 0.0) == [(-ext, 0.0)]:
                            q0, comp = (q0[0] - uu[0] * ext, q0[1] - uu[1] * ext), comp + ext
                    elif fim_livre and comp + 0.01 < tt <= comp + 0.13 + larg / 2:
                        ext = tt - comp + larg / 2 - 0.006
                        if fora_das_faixas(q0, uu, comp, comp + ext) == [(comp, comp + ext)]:
                            comp += ext
            k_l += 1
            # the purlin's section across the slope: flat, tilted with it (top = the roof plane)
            n_up = (a, b)
            zc = z_e + t * d
            dz = t * wv / 2
            # where it crosses the ceiling beams below (its prumos): the joints of a long line go there
            cruza = []
            if uu_v is None:
                for (eixo_v, p, s0, s1, zt, larg, kind) in vigas:
                    if (eixo_v == "y") == (abs(uu[1]) > 0.5) or kind == "borda":
                        continue
                    if eixo_v == "y" and abs(uu[0]) > 1e-9:
                        tt = (p - q0[0]) / uu[0]
                        ok = s0 - 0.01 <= q0[1] + uu[1] * tt <= s1 + 0.01
                    elif eixo_v == "x" and abs(uu[1]) > 1e-9:
                        tt = (p - q0[1]) / uu[1]
                        ok = s0 - 0.01 <= q0[0] + uu[0] * tt <= s1 + 0.01
                    else:
                        continue
                    if ok and 0.05 < tt < comp - 0.05:
                        cruza.append(tt)
            else:  # on a beam line: the joints over its prumos (they had fallen between two, each end in the air)
                n_p = max(1, math.ceil(comp / 1.0 - 1e-9))
                cruza = [comp * i / n_p for i in range(1, n_p)]
            # pieces of stock length, jointed over a beam (as the madres of Torres Vedras, D2503: <= 3,67 — ours here)
            peca_max = ctx["E"]["madres"].get("peca_max", 3.67)
            cortes_, ini = [0.0], 0.0
            while comp - ini > peca_max + 1e-6:
                cand = [c for c in cruza if ini + 1.0 <= c <= ini + peca_max + 1e-6]
                ini = max(cand) if cand else ini + peca_max
                cortes_.append(ini)
            cortes_.append(comp)
            # its ends against a hip / valley member cut on the skew: each long edge to the member's side
            nu_ = (-uu[1], uu[0])
            sg_n = 1 if nu_[0] * n_up[0] + nu_[1] * n_up[1] > 0 else -1  # n_up = nu_ * sg_n
            ob0 = ponta_obliqua(m_ini, q0, uu, 0.0, min(0.05, comp / 2)) if m_ini is not None else (0.0, 0.0)
            ob1 = ponta_obliqua(m_fim, q0, uu, comp, max(comp - 0.05, comp / 2)) if m_fim is not None else (comp, comp)
            for j, (ta, tb) in enumerate(zip(cortes_, cortes_[1:]), 1):
                # the top face on the slope's plane (the edges at -wv/2 / +wv/2 across, n_up uphill), the sides plumb
                ts_ = {}
                for k_o, off in enumerate((-wv / 2, wv / 2)):
                    k_ob = k_o if sg_n > 0 else 1 - k_o  # ponta_obliqua orders its edges along nu_
                    ts_[off] = (ob0[k_ob] if ta == 0.0 else ta, ob1[k_ob] if tb == comp else tb)
                cantos = []
                for off, ti in ((-wv / 2, 0), (-wv / 2, 1), (wv / 2, 1), (wv / 2, 0)):
                    tt_ = ts_[off][ti]
                    cantos.append((q0[0] + uu[0] * tt_ + n_up[0] * off, q0[1] + uu[1] * tt_ + n_up[1] * off,
                                   zc + t * off))
                lp = tb - ta
                peca(f"Viga de apoio à cobertura R{k_r + 1}{nome_p} L{k_l:02d}" + (f".{j}" if len(cortes_) > 2 else ""), "1.9",
                     va.get("seccao", "110x75"), "Viga de apoio à cobertura",
                     [prisma([[round(v, 4) for v in q] for q in cantos], (0, 0, -hv))], lp, lp * wv * hv)
                out["n_madres"] += 1
            # prumos: where the purlin crosses a ceiling beam (or along its beam line, every <= 1 m), their tops cut to
            # its underside (the slope's plane, hv down)

            def sob_madre(cx, cy, a=a, b=b, c=c):
                return z_e + t * (a * cx + b * cy + c) - hv
            if uu_v is not None:
                # prumos on the beam line at <= 1 m (rulebook §6 b), each whole on the beam (a purlin running on past the
                # beam's end — to a hip / valley, over a header — had its last prumo half off it)
                k_ax = 0 if abs(uu[0]) > 0.5 else 1
                s_a = q0[k_ax]
                s_b = q0[k_ax] + uu[k_ax] * comp
                lo_b, hi_b = sorted((s_a, s_b))
                lo_b = max(lo_b, viga_s[0] + pr["largura_y"] / 2)
                hi_b = min(hi_b, viga_s[1] - pr["largura_y"] / 2)
                if hi_b - lo_b > -1e-6:
                    n_p = max(1, math.ceil((hi_b - lo_b) / 1.0 - 1e-9))
                    for i in range(n_p + 1):
                        sv = lo_b + (hi_b - lo_b) * i / n_p
                        x, y = (sv, q0[1]) if k_ax == 0 else (q0[0], sv)
                        prumo(x, y, zt_v, sob_madre, f"Prumo L{k_l:02d} {i + 1:02d}", "x" if k_ax == 0 else "y")
                continue
            for (eixo_v, p, s0, s1, zt, larg, kind) in vigas:
                if (eixo_v == "y") == (abs(uu[1]) > 0.5):
                    continue  # parallel to the purlin
                if kind == "borda":
                    continue  # over a gable wall: the empena carries it
                if eixo_v == "y":  # beam along y at x = p
                    if abs(uu[0]) < 1e-9:
                        continue
                    tt = (p - q0[0]) / uu[0]
                    y = q0[1] + uu[1] * tt
                    if -0.01 <= tt <= comp + 0.01 and s0 - 0.01 <= y <= s1 + 0.01:
                        prumo(p, y, zt, sob_madre, f"Prumo L{k_l:02d} x{p:.2f}", "y")
                else:
                    if abs(uu[1]) < 1e-9:
                        continue
                    tt = (p - q0[1]) / uu[1]
                    x = q0[0] + uu[0] * tt
                    if -0.01 <= tt <= comp + 0.01 and s0 - 0.01 <= x <= s1 + 0.01:
                        prumo(x, p, zt, sob_madre, f"Prumo L{k_l:02d} y{p:.2f}", "x")

    # ------------------------------------------------------------------ empenas: the gable triangles on the edge beams
    E, ext_c = ctx["E"], ctx["ext_c"]
    ct = math.cos(math.atan(T["t"]))
    for k, r in enumerate(T["retangulos"]):
        for lado, est in r["lados"].items():
            if est != "empena":
                continue
            x0, x1, y0, y1 = r["x0"], r["x1"], r["y0"], r["y1"]
            if lado in ("O", "E"):  # a gable wall along y
                coord = x0 if lado == "O" else x1
                s0, s1 = y0, y1
                eixo_parede = "y"
            else:
                coord = y0 if lado == "S" else y1
                s0, s1 = x0, x1
                eixo_parede = "x"
            n_out = -1 if lado in ("O", "S") else 1  # the gable's outside
            cob = parede_em(eixo_parede, coord, s0, s1)
            if not cob:
                continue  # no wall on this gable line at all
            fc = coord - n_out * te / 2  # the middle of the frame
            a_, b_ = s0, s1
            if b_ - a_ < 0.5:
                continue
            # where the gable line has no wall below (a lower wing's roof abuts it — "encosto"): a header from wall to
            # wall carries the empena there, and the cladding goes on above the lower roof (camadas.py) — ours
            livres_, cur = [], s0
            for a2, b2 in cob:
                if a2 - cur > 0.3:
                    livres_.append((cur, a2))
                cur = max(cur, b2)
            if s1 - cur > 0.3:
                livres_.append((cur, s1))
            for a2, b2 in livres_:  # the standard glulam (JSON lameladas 200x100), its top at the edge beams' level
                h_l = lam or {"seccao": "200x100", "largura": 0.10, "altura": 0.20}
                c0, c1 = fc - h_l["largura"] / 2, fc + h_l["largura"] / 2
                zb_ = z_vig - h_l["altura"]
                pc = [caixa(a2, b2, c0, c1, zb_, z_vig)] if eixo_parede == "x" else [caixa(c0, c1, a2, b2, zb_, z_vig)]
                peca(f"Viga de bordadura da empena R{k + 1}{lado} ({a2:.2f}-{b2:.2f})", "1.7", h_l["seccao"],
                     "Viga de bordadura (lamelada, sob a empena)", pc, b2 - a2, (b2 - a2) * h_l["largura"] * h_l["altura"],
                     assumido="empena sobre a cobertura mais baixa de uma ala; secção por dimensionar (nosso)")
                sm = (a2 + b2) / 2
                q_out = (sm, coord + n_out * 0.3) if eixo_parede == "x" else (coord + n_out * 0.3, sm)
                baixo = next((j for j, r2 in enumerate(T["retangulos"]) if j != k and
                              r2["proprio"][0] - 1e-6 <= q_out[0] <= r2["proprio"][1] + 1e-6 and
                              r2["proprio"][2] - 1e-6 <= q_out[1] <= r2["proprio"][3] + 1e-6), None)
                out.setdefault("encostos", []).append({"o": "y" if eixo_parede == "x" else "x", "c": round(coord, 4),
                                                       "n": n_out, "s0": round(a2, 4), "s1": round(b2, 4),
                                                       "ret_cima": k, "ret_baixo": baixo})

            def ponto(s):
                return (s, fc) if eixo_parede == "x" else (fc, s)

            def vt(u, a_=a_):
                x, y = ponto(a_ + u)
                z = z_telhado(TA, x, y)
                return (z if z is not None else z_e) - hv - z_vig

            W = b_ - a_
            u_cume = max((i * W / 200 for i in range(201)), key=lambda u: vt(u))
            if vt(u_cume) < 0.15:
                continue
            # its ends: clear of the eave purlin and of a hip / valley member crossing the gable at its foot (its plates had
            # run through them and dipped into the edge beam — user 2026-10-29 "vigas a sobreporem-se umas as outras nos
            # cantos do triângulo da empena"); framed only where a plate and a top plate fit under the purlins, a wedge
            # packing on the edge beam between (ours); the panel keeps its whole width (the cladding runs on to the corner)
            def ocupado(u):
                for off in (-te / 2, 0.0, te / 2):
                    x, y = ponto(a_ + u)
                    x, y = (x, y + off) if eixo_parede == "x" else (x + off, y)
                    fs_p = [f for f in abs_f if _dentro_poly(f["pts"], x, y, 1e-6)]
                    if fs_p:
                        f = max(fs_p, key=lambda g: _z(g, x, y))
                        if f["plano"][0] * x + f["plano"][1] * y + f["plano"][2] < wv + 0.002:
                            return True  # over the eave purlin's band
                    for (px, py), (mx, my), (nx_, ny_), Lm, hw in faixas_m:
                        t_, s_ = (x - px) * mx + (y - py) * my, (x - px) * nx_ + (y - py) * ny_
                        if -0.002 <= t_ <= Lm + 0.002 and abs(s_) <= hw + 0.002:
                            return True
                return False
            minimo = E["placa"] + E["placa"] / ct + 0.005
            fins = []
            for u_, sg in ((0.0, 1), (W, -1)):
                while 0.0 <= u_ <= W and abs(u_ - u_cume) > 0.01 and ocupado(u_):
                    u_ += sg * 0.005
                livre = u_
                while 0.0 <= u_ <= W and abs(u_ - u_cume) > 0.01 and vt(u_) < minimo:
                    u_ += sg * 0.005
                fins.append((livre, u_))
            (la, fa), (lb, fb) = fins
            if fb - fa < 0.3:
                continue
            ms = emoldurar_empena(fa, fb, vt, u_cume, ext_c, E, ct)
            for u0_, u1_ in ((la, fa), (fb, lb)):
                if abs(u1_ - u0_) > 0.01:
                    ms.append(membro("Calço da empena", ext_c["seccao_montante"],
                                     [(u0_, 0.0), (u1_, 0.0), (u1_, max(vt(u1_), 0.001)), (u0_, max(vt(u0_), 0.001))]))
            nome = f"EMP R{k + 1}{lado}"
            chave = f"{nome}__dc"
            ctx["alcados"][chave] = {"W": W, "H": round(vt(u_cume), 4), "members": ms, "frame_u0": round(la, 4),
                                     "frame_u1": round(lb, 4), "section": ext_c["seccao_montante"], "aberturas": [],
                                     "sistema": "discovercasa", "studs": []}
            org = [a_, fc] if eixo_parede == "x" else [fc, a_]
            ctx["paineis"].append({"nome": nome, "alcado": chave, "piso": 2, "tipo": "PE", "empena": True,
                                   "origem": [round(org[0], 4), round(org[1], 4), round(z_vig, 4)],
                                   "sentido": [1.0, 0.0] if eixo_parede == "x" else [0.0, 1.0], "espessura": te,
                                   "encaixe": "-", "extra": 0, "exterior": True,
                                   "fora": float(n_out if eixo_parede == "x" else -n_out)})
            out["n_empenas"] += 1
    return out
