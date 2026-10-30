"""DiscoverCasa structural skeleton for a house extracted from the engineer's drawings. Pure Python.

    python ferramentas/modelo/estrutura_dc.py "<project>/modelos/<type>/config.json" [--saida FILE]

Keeps the house as drawn in plan (outer faces, wall centre lines of interior walls, module joints,
openings, floor levels) and rebuilds the structure the DiscoverCasa way
(conhecimento/sistema-construtivo.md §2, §5, §6; standard in sistema_construtivo.json "estrutura"):
  - walls: exterior 110 deep (studs 110x35), interior 75 deep (studs 75x35), 40 cm clear between studs,
    single 35 plates, no noggings; 110x75 at the house corners and around openings (jambs, header,
    sill); 220x75 lintel over openings from 2.8 m (verga_grande.vao_min); doors without bottom plate; every module has its own
    end studs; doorways that the drawings leave as a gap between modules get a short wall above the door
    (bandeira) and 110x75 jambs on the module ends beside them;
  - floor between storeys: joists 220x75 on edge at 1 m on the ground-floor walls, battens 110x75 laid flat
    across them at 0.60 m centres, OSB 22 deck; the upper walls stand on the deck and everything above rises
    by the extra depth (the upper clear height stays as drawn);
  - upper floor: flat ceiling at the tie beam — afinação 110x35 + amarração 110x75 on the exterior
    walls, afinação 110x75 upright on interior walls, vigas de apoio ao teto 220x75 across the house;
  - roof: prumos (posts) on the ceiling beams carry the vigas de apoio à cobertura 110x75 (purlins)
    that give the slope; gable ends are framed triangles on the tie beam.
Output: a geometry JSON of the same shape as extrair_casa.py's plus "estrutura_extra" (world pieces).
"""
import argparse
import copy
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.comum import pasta_trabalho  # noqa: E402
from ferramentas.modelo.camadas import R, fechos_salas, fundir, portas_virtuais, prisma  # noqa: E402
from ferramentas.modelo.paineis import Painel  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent


def ret(u0, u1, v0, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def membro(tipo, seccao, poly):
    return {"section": seccao, "tipo": tipo, "poly": [[round(u, 5), round(v, 5)] for u, v in poly]}


# ============================================================================ wall modules
def emoldurar(f0, f1, H, aberturas, cls, E, canto0, canto1, ombreira0=False, ombreira1=False):
    """Members of one rectangular module (elevation u from f0 to f1, v from 0 to H). canto: the end is a house
    corner; ombreira: the end is the jamb of a doorway next to the module (both 110x75)."""
    pl, livre = E["placa"], E["vao_livre"]
    w, wr, hp, hs = cls["montante"], cls["reforco"], cls["padieira"], cls["peitoril"]
    sm, sr = cls["seccao_montante"], cls["seccao_reforco"]
    vg = E["verga_grande"]
    top = H - pl
    ms = []
    # plates: the bottom plate stops at door openings
    x = f0
    for u0, u1, v0, _v1, _k in sorted(aberturas):
        if v0 <= 1e-6:
            if u0 - x > 0.01:
                ms.append(membro("Travessa inferior", sm, ret(x, u0, 0, pl)))
            x = max(x, u1)
    if f1 - x > 0.01:
        ms.append(membro("Travessa inferior", sm, ret(x, f1, 0, pl)))
    ms.append(membro("Travessa superior", sm, ret(f0, f1, top, H)))
    # vertical reinforcements: jambs of every opening, ends (110x75 at house corners)
    grandes = [a for a in aberturas if a[1] - a[0] >= vg["vao_min"]]
    blocos = []
    for u0, u1, *_ in aberturas:
        blocos += [[u0 - wr, u0, "Ombreira", sr], [u1, u1 + wr, "Ombreira", sr]]
    def fim(canto, ombreira):
        if canto:
            return "Montante de canto", wr, sr
        return ("Ombreira", wr, sr) if ombreira else ("Montante", w, sm)

    t0, l0, s0 = fim(canto0, ombreira0)
    t1, l1, s1 = fim(canto1, ombreira1)
    fim0 = [f0, f0 + l0, t0, s0]
    fim1 = [f1 - l1, f1, t1, s1]
    for b in blocos:  # a jamb next to a module end replaces the end stud
        if fim0 and b[0] < fim0[1] + 0.035:
            b[0], fim0 = f0, None
        if fim1 and b[1] > fim1[0] - 0.035:
            b[1], fim1 = f1, None
    blocos += [b for b in (fim0, fim1) if b]
    blocos.sort()
    unidos = []
    for b in blocos:  # overlapping reinforcements become one member
        if unidos and b[0] < unidos[-1][1] + 0.005:
            unidos[-1][1] = max(unidos[-1][1], b[1])
            if unidos[-1][2] == "Montante" or b[2] == "Ombreira":
                unidos[-1][2:] = b[2:]
        else:
            unidos.append(list(b))
    for a, b, tipo, sec in unidos:
        vtop = top
        for g in grandes:  # posts of a big opening stop under the 220 lintel
            if a < g[1] + wr + 0.01 and b > g[0] - wr - 0.01:
                vtop = top - vg["altura"]
        ms.append(membro(tipo, sec, ret(max(a, f0), min(b, f1), pl, vtop)))
    # headers, sills
    for u0, u1, v0, v1, _k in aberturas:
        if u1 - u0 >= vg["vao_min"]:
            ms.append(membro("Verga", vg["seccao"], ret(u0 - wr, u1 + wr, top - vg["altura"], top)))
        else:
            ms.append(membro("Padieira", sr, ret(u0, u1, v1, v1 + hp)))
        if v0 > 1e-6:
            ms.append(membro("Peitoril", sr, ret(u0, u1, v0 - hs, v0)))
    # regular studs at 40 cm clear from the start end; cripples inside openings
    x = f0 + (unidos[0][1] - f0 if unidos and unidos[0][0] <= f0 + 1e-6 else w) + livre
    limite = f1 - (f1 - unidos[-1][0] if unidos and unidos[-1][1] >= f1 - 1e-6 else w)
    while x + w <= limite - 0.03:
        a, b = x, x + w
        x += livre + w
        if any(a < ub + 0.05 and b > ua - 0.05 for ua, ub, *_ in unidos):
            continue
        dentro = [op for op in aberturas if a >= op[0] - 1e-6 and b <= op[1] + 1e-6]
        if dentro:
            u0, u1, v0, v1, _k = dentro[0]
            cima = (top - vg["altura"]) if u1 - u0 >= vg["vao_min"] else v1 + hp
            if top - cima > 0.03:
                ms.append(membro("Montante curto", sm, ret(a, b, cima, top)))
            if v0 > 1e-6 and v0 - hs - pl > 0.03:
                ms.append(membro("Montante curto", sm, ret(a, b, pl, v0 - hs)))
            continue
        ms.append(membro("Montante", sm, ret(a, b, pl, top)))
    return ms


def emoldurar_bandeira(W, H, cls, E):
    """Short wall above a doorway left open between two modules: header (padieira) between the jambs of the
    modules beside it, short studs at 40 cm clear, top plate."""
    pl, livre, w = E["placa"], E["vao_livre"], cls["montante"]
    hp, sm, sr = cls["padieira"], cls["seccao_montante"], cls["seccao_reforco"]
    top = H - pl
    ms = [membro("Padieira", sr, ret(0, W, 0, hp)), membro("Travessa superior", sm, ret(0, W, top, H))]
    x = livre
    while x + w <= W - 0.03 and top - hp > 0.03:
        ms.append(membro("Montante curto", sm, ret(x, x + w, hp, top)))
        x += livre + w
    return ms


def emoldurar_empena(f0, f1, vt, u_cume, cls, E, ct):
    """Gable triangle on the tie beam: bottom plate, sloped top plates under the purlins, studs."""
    pl, livre, w, wr = E["placa"], E["vao_livre"], cls["montante"], cls["reforco"]
    sm, sr = cls["seccao_montante"], cls["seccao_reforco"]
    dp = pl / ct

    def poste(a, b, tipo, sec):
        pts = [(a, pl), (b, pl), (b, vt(b) - dp)]
        if a < u_cume < b:
            pts.append((u_cume, vt(u_cume) - dp))
        pts.append((a, vt(a) - dp))
        return membro(tipo, sec, pts)

    ms = [membro("Travessa inferior", sm, ret(f0, f1, 0, pl))]
    for a, b in ((f0, u_cume), (u_cume, f1)):
        ms.append(membro("Travessa superior inclinada", sm, [(a, vt(a) - dp), (b, vt(b) - dp), (b, vt(b)), (a, vt(a))]))
    ms += [poste(f0, f0 + wr, "Montante de canto", sr), poste(f1 - wr, f1, "Montante de canto", sr)]
    x = f0 + wr + livre
    while x + w <= f1 - wr - 0.03:
        if vt(x) - dp - pl > 0.05 and vt(x + w) - dp - pl > 0.05:
            ms.append(poste(x, x + w, "Montante", sm))
        x += livre + w
    if all(abs(u_cume - (m["poly"][0][0] + m["poly"][1][0]) / 2) > 0.2 for m in ms[3:]):
        ms.append(poste(u_cume - w / 2, u_cume + w / 2, "Montante", sm))  # stud under the ridge
    return ms


# ============================================================================ house
def converter(G, S, E):
    L, D = G["casa"]["comprimento"], G["casa"]["profundidade"]
    orig = [Painel(p, G["alcados"][p["alcado"]], (L / 2, D / 2)) for p in G["paineis"]]
    pdict = {id(P): p for P, p in zip(orig, G["paineis"])}
    remover = set(E.get("remover_paineis", []))  # modules dropped on purpose (e.g. Sobral duct PI2.09/PI2.10)
    orig = [P for P in orig if P.nome not in remover]
    ext_c, int_c = E["exterior"], E["interior"]
    te, ti = ext_c["espessura"], int_c["espessura"]
    pl = E["placa"]

    def na_fachada(P):
        x0, x1, y0, y1 = P.pegada()
        return x0 < 0.02 or x1 > L - 0.02 or y0 < 0.02 or y1 > D - 0.02

    novo = {}
    for P in orig:
        ext = na_fachada(P)
        t = te if ext else ti
        wc = P.fora * (P.t - t) / 2 if ext else 0.0  # exterior walls keep their outer face (centre moves out)
        novo[id(P)] = {"ext": ext, "t": t, "ox": P.ox - wc * P.uy, "oy": P.oy + wc * P.ux, "f0": P.f0, "f1": P.f1}

    def pegada(P, n):
        pts = [(n["ox"] + u * P.ux - w * P.uy, n["oy"] + u * P.uy + w * P.ux)
               for u in (n["f0"], n["f1"]) for w in (-n["t"] / 2, n["t"] / 2)]
        return (min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts))

    # interior walls standing against the inside of an exterior wall (e.g. the duct walls PI2.09/10 of Sobral)
    # follow its new inner face, so no slot opens between them
    encostadas = []
    for P in orig:
        n = novo[id(P)]
        if n["ext"]:
            continue
        a = P.pegada()
        k = 0 if abs(P.ux) < 0.5 else 2  # footprint index of the axis across the walls
        for Q in orig:
            nq = novo[id(Q)]
            if not nq["ext"] or Q.piso != P.piso or abs(P.ux * Q.ux + P.uy * Q.uy) < 0.9:
                continue
            b = Q.pegada()
            ao, bo = (a[2 - k], a[3 - k]), (b[2 - k], b[3 - k])  # extents along the walls
            if min(ao[1], bo[1]) - max(ao[0], bo[0]) < 0.05:
                continue
            baixo, cima = abs(a[k] - b[k + 1]) < 0.02, abs(a[k + 1] - b[k]) < 0.02
            if not (baixo or cima):
                continue
            an, bn = pegada(P, n), pegada(Q, nq)
            d = (bn[k + 1] - an[k]) if baixo else (bn[k] - an[k + 1])
            n["ox" if k == 0 else "oy"] += d
            encostadas.append((P.nome, Q.nome, round(d, 4)))
            # a wall forming a duct with it (narrow void on the other side) moves too: the duct keeps its size
            vmax = S.get("divisoes", {}).get("vazio_max", 0.38)
            for Pd in orig:
                if Pd is P or Pd.piso != P.piso or novo[id(Pd)]["ext"] or abs(P.ux * Pd.ux + P.uy * Pd.uy) < 0.9:
                    continue
                c = Pd.pegada()
                if min(a[3 - k], c[3 - k]) - max(a[2 - k], c[2 - k]) < 0.05:
                    continue
                vao = (c[k] - a[k + 1]) if baixo else (a[k] - c[k + 1])
                if 0.01 < vao < vmax:
                    novo[id(Pd)]["ox" if k == 0 else "oy"] += d
                    encostadas.append((Pd.nome, P.nome, round(d, 4)))
            break

    # wall ends that touched a perpendicular wall follow that wall's new face
    for P in orig:
        n = novo[id(P)]
        for fim in ("f0", "f1"):
            u = getattr(P, fim)
            xo, yo = P.ox + u * P.ux, P.oy + u * P.uy
            corpo = 1 if fim == "f0" else -1
            for Q in orig:
                if Q is P or Q.piso != P.piso or abs(P.ux * Q.ux + P.uy * Q.uy) > 0.5:
                    continue
                x0, x1, y0, y1 = Q.pegada()
                if not (x0 - 0.03 <= xo <= x1 + 0.03 and y0 - 0.03 <= yo <= y1 + 0.03):
                    continue
                qx0, qx1, qy0, qy1 = pegada(Q, novo[id(Q)])
                if abs(P.ux) > 0.5:
                    n[fim] = ((qx1 if corpo * P.ux > 0 else qx0) - n["ox"]) / P.ux
                else:
                    n[fim] = ((qy1 if corpo * P.uy > 0 else qy0) - n["oy"]) / P.uy
                break

    # floor between storeys (DiscoverCasa): joists on the ground-floor walls, flat battens, OSB deck; every
    # upper wall stands on the deck and the extra depth raises everything above (user 2026-10-09)
    nv = G["niveis"]
    Pv = E.get("pavimento")
    if Pv:
        z_vj = nv["topo_paredes_piso0"] + Pv["vigas"]["altura"]
        z_ba = z_vj + Pv["barrotes"]["altura"]
        z_p1 = z_ba + Pv["osb"]
    else:
        z_p1 = nv["piso1_interior"]
    subida = z_p1 - nv["piso1_interior"]

    # doorways left open between modules: the modules beside them get 110x75 jambs, a bandeira closes the top
    fin_e = S["pavimentos"]["acabamento"]["espessura"]
    fin = {0: S["pavimentos"]["piso0"]["acabado_z"], 1: z_p1 + fin_e}
    div = S.get("divisoes", {})

    def faixa(w):  # (along x?, s0, s1, centre line) of a wall or doorway given by its two end points
        (xa, ya), (xb, yb) = w["de"], w["ate"]
        if abs(xb - xa) >= abs(yb - ya):
            return True, min(xa, xb), max(xa, xb), (ya + yb) / 2
        return False, min(ya, yb), max(ya, yb), (xa + xb) / 2

    def retangulo(ew, s0, s1, c, t):
        return (s0, s1, c - t / 2, c + t / 2) if ew else (c - t / 2, c + t / 2, s0, s1)

    # partitions of the architecture that the structural drawings do not have (config estrutura.paredes_extra)
    novas = []
    for w in E.get("paredes_extra", []):
        ew, s0, s1, c = faixa(w)
        novas.append({"nome": w["nome"], "piso": w["piso"], "ew": ew, "s0": s0, "s1": s1, "c": c,
                      "t": w.get("espessura", ti), "portas": w.get("portas", [])})
    portas, jamba = [], {}

    def registar(piso, pp, v):
        ew = v[1] - v[0] >= v[3] - v[2]
        s0, s1 = (v[0], v[1]) if ew else (v[2], v[3])
        c = (v[2] + v[3]) / 2 if ew else (v[0] + v[1]) / 2
        lados = []
        for P in pp:
            n = novo[id(P)]
            if (abs(P.ux) > 0.5) != ew:
                continue
            for f in ("f0", "f1"):
                x, y = n["ox"] + n[f] * P.ux, n["oy"] + n[f] * P.uy
                s, cc = (x, y) if ew else (y, x)
                if abs(cc - c) < 0.06 and min(abs(s - s0), abs(s - s1)) < 0.02:
                    jamba.setdefault(id(P), set()).add(f)
                    lados.append(P)
        portas.append({"piso": piso, "ew": ew, "s0": s0, "s1": s1, "c": c, "t": min(v[1] - v[0], v[3] - v[2]),
                       "lados": lados})

    for piso in (0, 1):
        pp = [P for P in orig if P.piso == piso]
        ab = G["pavimento"].get("abertura_escada") if piso == 1 else None
        abertas = [a["rect"] for a in div.get("passagens_abertas", []) if a["piso"] == piso]  # stay open
        rects = [pegada(P, novo[id(P)]) for P in pp] + [retangulo(n["ew"], n["s0"], n["s1"], n["c"], n["t"])
                                                          for n in novas if n["piso"] == piso]
        virt, _g = fechos_salas(rects, (0.0, L, 0.0, D), div, ([ab] if ab else []) + abertas)
        for v in portas_virtuais(virt, div.get("porta_max", 1.05)):
            registar(piso, pp, v)
        for w in E.get("portas_extra", []):  # wider doorways given in the config (e.g. a sliding door)
            if w["piso"] == piso:
                ew, s0, s1, c = faixa(w)
                registar(piso, pp, retangulo(ew, s0, s1, c, w.get("espessura", ti)))

    # upper floor: every module ends level with the eave walls (flat ceiling at the tie beam); the deeper floor
    # lifts them by `subida`, so the upper clear height stays as drawn
    z_mod = E.get("topo_modulos_piso1") or subida + max(P.oz + P.hf for P in orig if P.piso == 1 and P.tipo == "PE"
                                                         and abs(P.ux) > 0.5 and na_fachada(P))
    alcados, paineis = {}, []
    corners = [(0, 0), (L, 0), (0, D), (L, D)]
    for P in orig:
        n = novo[id(P)]
        cls = ext_c if n["ext"] else int_c
        oz = z_p1 if P.piso == 1 else P.oz
        dv = P.oz - nv["piso1_interior"] if P.piso == 1 else 0.0  # openings keep their height above the floor
        H = (z_mod - oz) if P.piso == 1 else P.hf
        vg = E["verga_grande"]
        abs_ = []
        lista = P.aberturas
        alt = E.get("aberturas_alterar", {}).get(P.nome)  # openings corrected from the architecture (absolute Z)
        if alt:
            lista = [(u0, u1, alt["z"][0] - P.oz, alt["z"][1] - P.oz, alt.get("tipo", k)) for u0, u1, _a, _b, k in lista]
        for u0, u1, v0, v1, k in ((u0, u1, v0 + dv, v1 + dv, k) for u0, u1, v0, v1, k in lista):
            topo = H - pl - (vg["altura"] if u1 - u0 >= vg["vao_min"] else cls["padieira"])
            v0n = 0.0 if k == "porta" else max(v0, pl + cls["peitoril"] + 0.05)
            v1n = min(v1, topo)
            if v1n - v0n > 0.3:
                abs_.append([round(u0, 4), round(u1, 4), round(v0n, 4), round(v1n, 4), k])

        def canto(u):
            x, y = n["ox"] + u * P.ux, n["oy"] + u * P.uy
            return n["ext"] and any(math.hypot(x - cx, y - cy) < n["t"] + 0.05 for cx, cy in corners)

        jb = jamba.get(id(P), set())
        ms = emoldurar(n["f0"], n["f1"], H, abs_, cls, E, canto(n["f0"]), canto(n["f1"]), "f0" in jb, "f1" in jb)
        chave = f"{P.nome}__dc"
        alcados[chave] = {"W": n["f1"] - n["f0"], "H": H, "members": ms, "frame_u0": n["f0"], "frame_u1": n["f1"],
                          "section": cls["seccao_montante"], "aberturas": abs_, "sistema": "discovercasa",
                          "studs": sorted((m["poly"][0][0] + m["poly"][1][0]) / 2 for m in ms if m["tipo"] == "Montante")}
        p2 = copy.deepcopy(pdict[id(P)])
        p2.update({"alcado": chave, "espessura": n["t"], "origem": [round(n["ox"], 4), round(n["oy"], 4), round(oz, 4)],
                   "exterior": n["ext"]})
        paineis.append(p2)

    pi = E["porta_interior"]
    for n in novas:  # extra partitions: interior modules from floor to the module top, doors from the config
        piso = n["piso"]
        oz = 0.0 if piso == 0 else z_p1
        topo = G["niveis"]["topo_paredes_piso0"] if piso == 0 else z_mod
        H, W = topo - oz, n["s1"] - n["s0"]
        cabeca = fin[piso] + pi["altura"] - oz
        abs_ = [[round(a, 4), round(b, 4), 0.0, round(cabeca, 4), "porta"] for a, b in n["portas"]]
        ms = emoldurar(0.0, W, H, abs_, int_c, E, False, False)
        chave = f"{n['nome']}__dc"
        alcados[chave] = {"W": W, "H": H, "members": ms, "frame_u0": 0.0, "frame_u1": W,
                          "section": int_c["seccao_montante"], "aberturas": abs_, "sistema": "discovercasa",
                          "studs": sorted((m["poly"][0][0] + m["poly"][1][0]) / 2 for m in ms if m["tipo"] == "Montante")}
        org = [n["s0"], n["c"]] if n["ew"] else [n["c"], n["s0"]]
        paineis.append({"nome": n["nome"], "alcado": chave, "piso": piso, "tipo": "PI",
                        "origem": [round(org[0], 4), round(org[1], 4), oz],
                        "sentido": [1.0, 0.0] if n["ew"] else [0.0, 1.0], "espessura": n["t"],
                        "encaixe": "-", "extra": 0, "exterior": False})
    bandeiras = []
    for k, pt in enumerate(portas, 1):
        topo = z_mod if pt["piso"] == 1 else min([P.oz + P.hf for P in pt["lados"]] or [G["niveis"]["topo_paredes_piso0"]])
        z0_ = fin[pt["piso"]] + pi["altura"]
        H = topo - z0_
        if H < 0.15:
            continue
        nomes = "/".join(sorted({P.nome for P in pt["lados"]})) or f"{k:02d}"
        nome = f"Bandeira {nomes}"
        W = pt["s1"] - pt["s0"]
        ms = emoldurar_bandeira(W, H, int_c, E)
        chave = f"{nome}__dc"
        alcados[chave] = {"W": W, "H": H, "members": ms, "frame_u0": 0.0, "frame_u1": W,
                          "section": int_c["seccao_montante"], "aberturas": [], "sistema": "discovercasa", "studs": []}
        org = [pt["s0"], pt["c"]] if pt["ew"] else [pt["c"], pt["s0"]]
        paineis.append({"nome": nome, "alcado": chave, "piso": pt["piso"], "tipo": "PI",
                        "origem": [round(org[0], 4), round(org[1], 4), round(z0_, 4)],
                        "sentido": [1.0, 0.0] if pt["ew"] else [0.0, 1.0], "espessura": round(pt["t"], 4),
                        "encaixe": "-", "extra": 0, "exterior": False})
        bandeiras.append((nome, round(W, 3), round(z0_, 3), round(H, 3)))

    def pegada_p2(p2):
        e = alcados[p2["alcado"]]
        (ox, oy, _z), (ux, uy), t = p2["origem"], p2["sentido"], p2["espessura"]
        pts = [(ox + u * ux - w_ * uy, oy + u * uy + w_ * ux) for u in (e["frame_u0"], e["frame_u1"]) for w_ in (-t / 2, t / 2)]
        return (min(q[0] for q in pts), max(q[0] for q in pts), min(q[1] for q in pts), max(q[1] for q in pts))

    # ------------------------------------------------------------------ roof: flat ceiling + posts + purlins
    C = G["cobertura"]
    Sc = S["cobertura"]
    va = Sc["vigas_apoio"]
    wv, hv = va["largura"], va["altura"]
    yr = C["cumeeira_y"]
    th = math.radians(C["inclinacao"])
    z_teto = z_mod + max(E["afinacao_exterior"]["altura"] + E["amarracao"]["altura"], E["afinacao_interior"]["altura"])
    vt_ = E["vigas_teto"]
    z_vig = z_teto + vt_["altura"]
    manter = E.get("cobertura_manter", "inclinacao")
    z_cume_desenho = C["cumeeira_z"] + hv / math.cos(th)  # panel underside on the ridge in the drawings
    for _ in range(5):  # the eave purlin sits on the ceiling beams right over the wall
        ct, st, tn = math.cos(th), math.sin(th), math.tan(th)
        y_t0, z_t0 = -hv * st, z_vig + hv * ct  # top outer corner of the south eave purlin
        if manter == "inclinacao":
            z0 = z_t0 + tn * (yr - y_t0)
            break
        z0 = z_cume_desenho
        th = math.atan((z0 - z_t0) / (yr - y_t0))
    ct, st, tn = math.cos(th), math.sin(th), math.tan(th)

    def plano(y):  # underside of the roof panels = top of the purlins
        return z0 - tn * abs(y - yr)

    extra = []

    def peca(nome, col, sec, tipo, pecas, comp, vol):
        extra.append({"nome": nome, "colecao": col, "material": f"Madeira {sec}", "pecas": pecas,
                      "props": {"seccao": sec, "tipo": tipo, "comprimento_m": round(comp, 3), "volume_m3": round(vol, 5)}})

    def caixa(x0, x1, y0, y1, z0_, z1_):
        return prisma([(x0, y0, z0_), (x1, y0, z0_), (x1, y1, z0_), (x0, y1, z0_)], (0, 0, z1_ - z0_))

    pav = copy.deepcopy(G["pavimento"])
    if Pv:
        # joists 220x75 on edge N-S like the ceiling beams (outer ones at the E/W faces, trimmers beside the stair
        # opening, a header closing the cut joists); battens 110x75 flat E-W on top at 0.60 m centres (user
        # 2026-10-13: "medidos em eixo"); the OSB deck is built by build_casa.py (niveis)
        vj, ba = Pv["vigas"], Pv["barrotes"]
        wj, wb = vj["largura"], ba["largura"]
        z_w = nv["topo_paredes_piso0"]
        ab = pav.get("abertura_escada")
        xa, xb = wj / 2, L - wj / 2
        nj = max(1, math.ceil((xb - xa) / vj["espacamento"] - 1e-9))
        xs = [xa + (xb - xa) * i / nj for i in range(nj + 1)]
        trim = [ab[0] - wj / 2, ab[1] + wj / 2] if ab else []
        xs = sorted([x for x in xs if all(abs(x - t) > 0.15 for t in trim)] + trim)
        # main beams of the drawn floor (E-W, inside the house, not the stair trimmer) only if
        # `pavimento.vigas_principais`: two 220x75 side by side, flush with the joists, which are cut and hang on
        # them (e.g. Sobral: the beam over the 2.8 m living-room gap at y 3.45). DiscoverCasa default: none
        bandas = []
        for f in sorted(G["pavimento"]["pecas"] if Pv.get("vigas_principais") else [], key=lambda f: (f["y0"], f["x0"])):
            if f["x1"] - f["x0"] < 2.0 or f["y0"] < 0.3 or f["y1"] > D - 0.3:
                continue
            if ab and abs(f["y1"] - ab[2]) < 0.15 and f["x0"] < ab[1] and f["x1"] > ab[0]:
                continue
            b = bandas[-1] if bandas else None
            if b and abs(f["y0"] - b[3]) < 0.005 and min(f["x1"], b[1]) - max(f["x0"], b[0]) > 1.0:
                b[3] = f["y1"]
            else:
                bandas.append([f["x0"], f["x1"], f["y0"], f["y1"]])
        principais = []
        for bx0, bx1, by0, by1 in bandas:
            yc = (by0 + by1) / 2
            x0 = wj if bx0 < wj + 0.1 else bx0  # runs between the edge joists
            x1 = L - wj if bx1 > L - wj - 0.1 else bx1
            principais.append((x0, x1, yc - wj, yc + wj))
        tramos = []
        for x in xs:
            cortes = [(y0, y1) for x0, x1, y0, y1 in principais if x0 < x < x1]
            if ab and ab[0] < x < ab[1]:  # cut by the stair opening: carried by the header
                cortes.append((ab[2] - wj, ab[3] + wj))
            segs, y = [], 0.0
            for c0, c1 in sorted(cortes):
                segs.append((y, c0))
                y = max(y, c1)
            segs.append((y, D))
            tramos += [(x, y0, y1) for y0, y1 in segs if y1 - y0 >= 0.3]
        pav["pecas"] = []
        for k, (x, y0, y1) in enumerate(tramos, 1):
            peca(f"Viga de pavimento {k:02d}", "1.3", vj["seccao"], "Viga de pavimento",
                 [caixa(x - wj / 2, x + wj / 2, y0, y1, z_w, z_vj)], y1 - y0, (y1 - y0) * wj * vj["altura"])
            pav["pecas"].append({"x0": round(x - wj / 2, 4), "x1": round(x + wj / 2, 4), "y0": round(y0, 4),
                                 "y1": round(y1, 4)})
        for k, (x0, x1, y0, y1) in enumerate(principais, 1):
            for lado, (ya, yb) in (("a", (y0, y0 + wj)), ("b", (y1 - wj, y1))):
                peca(f"Viga principal do pavimento {k:02d}{lado}", "1.3", vj["seccao"], "Viga principal do pavimento",
                     [caixa(x0, x1, ya, yb, z_w, z_vj)], x1 - x0, (x1 - x0) * wj * vj["altura"])
        if ab:
            lados = [(ab[2] - wj, ab[2])]
            if D - ab[3] >= wj:  # opening short of the wall: header on its edge, or on the wall when the stubs drop
                lados.append((ab[3], ab[3] + wj) if D - ab[3] - wj >= 0.3 else (D - wj, D))
            for k, (y0, y1) in enumerate(lados, 1):
                peca(f"Viga de remate da escada {k:02d}", "1.3", vj["seccao"], "Viga de remate da escada",
                     [caixa(ab[0], ab[1], y0, y1, z_w, z_vj)], ab[1] - ab[0], (ab[1] - ab[0]) * wj * vj["altura"])
        nb = max(1, math.ceil((D - wb) / ba["espacamento"] - 1e-9))
        k = 0
        for i in range(nb + 1):
            y = wb / 2 + (D - wb) * i / nb
            cortado = ab and y + wb / 2 > ab[2] + 0.01 and y - wb / 2 < ab[3] - 0.01
            for x0, x1 in ([(0.0, ab[0]), (ab[1], L)] if cortado else [(0.0, L)]):
                if x1 - x0 < 0.2:
                    continue
                k += 1
                peca(f"Barrote de pavimento {k:02d}", "1.3", ba["seccao"], "Barrote de pavimento (deitado)",
                     [caixa(x0, x1, y - wb / 2, y + wb / 2, z_vj, z_ba)], x1 - x0, (x1 - x0) * wb * ba["altura"])
        pav.update({"sistema": "discovercasa", "deck_margem": 0.0, "n_vigas": len(tramos), "n_barrotes": k,
                    "vigas_principais": [[round(v, 4) for v in p] for p in principais]})

    af_e, am, af_i = E["afinacao_exterior"], E["amarracao"], E["afinacao_interior"]
    lados = {"S": (0, L, 0, te), "N": (0, L, D - te, D), "O": (0, te, te, D - te), "E": (L - te, L, te, D - te)}
    for lado, (x0, x1, y0, y1) in lados.items():
        comp = max(x1 - x0, y1 - y0)
        peca(f"Viga de afinação exterior {lado}", "1.6", af_e["seccao"], "Viga de afinação exterior",
             [caixa(x0, x1, y0, y1, z_mod, z_mod + af_e["altura"])], comp, comp * te * af_e["altura"])
        za = z_mod + af_e["altura"]
        peca(f"Viga de amarração {lado}", "1.6", am["seccao"], "Viga de amarração",
             [caixa(x0, x1, y0, y1, za, za + am["altura"])], comp, comp * te * am["altura"])
    for p2 in paineis:
        if p2["piso"] != 1 or p2["exterior"]:
            continue
        x0, x1, y0, y1 = pegada_p2(p2)
        comp = max(x1 - x0, y1 - y0)
        peca(f"Viga de afinação | {p2['nome']}", "1.6", af_i["seccao"], "Viga de afinação interior",
             [caixa(x0, x1, y0, y1, z_mod, z_mod + af_i["altura"])], comp, comp * ti * af_i["altura"])
    # ceiling beams across the house (perpendicular to the ridge), on the eave walls' tie beams
    xa, xb = te + vt_["largura"] / 2, L - te - vt_["largura"] / 2
    nv = max(1, math.ceil((xb - xa) / vt_["espacamento"] - 1e-9))
    vigas_x = [xa + (xb - xa) * i / nv for i in range(nv + 1)]
    for i, xv in enumerate(vigas_x, 1):
        peca(f"Viga de apoio ao teto {i:02d}", "1.7", vt_["seccao"], "Viga de apoio ao teto",
             [caixa(xv - vt_["largura"] / 2, xv + vt_["largura"] / 2, 0, D, z_teto, z_vig)], D,
             D * vt_["largura"] * vt_["altura"])
    # purlins (eave one resting on the ceiling beams over the wall, ridge one near the ridge) and posts
    emp = Sc["empena"]
    xe0, xe1 = -emp, L + emp
    pr = E["prumos"]
    n_prumos = 0
    madres = []
    for lado, sg in (("S", -1), ("N", 1)):
        t = (-sg * ct, st)
        m = (sg * st, ct)
        y_out = 0.0 if sg < 0 else D
        y_t_ext = y_out + sg * hv * st          # top outer corner of the eave purlin
        a_ext = abs(yr - y_t_ext) / ct          # slope distance of that corner from the ridge
        a_int = 0.05                            # inner top corner of the ridge purlin
        # top outer corners along the slope (distance from the ridge, measured on the top plane)
        c_top, c_bot = a_int + wv, a_ext
        nm = max(1, math.ceil((c_bot - c_top) / va["espacamento_max"] - 1e-9))
        for k in range(nm + 1):
            a_o = c_top + (c_bot - c_top) * k / nm   # outer (eave-side) top corner
            T0 = (yr + sg * a_o * ct, z0 - a_o * st)
            T1 = (T0[0] + t[0] * wv, T0[1] + t[1] * wv)
            B0 = (T0[0] - m[0] * hv, T0[1] - m[1] * hv)
            B1 = (T1[0] - m[0] * hv, T1[1] - m[1] * hv)
            sec = [B0, B1, T1, T0]
            nome = f"Viga de apoio à cobertura {lado} {k + 1:02d}"
            comp = xe1 - xe0
            peca(nome, "1.9", va.get("seccao", "110x75"), "Viga de apoio à cobertura",
                 [prisma([(xe0, y, z) for y, z in sec], (comp, 0, 0))], comp, comp * wv * hv)
            madres.append((lado, B0, B1))
            if min(B0[1], B1[1]) - z_vig < 0.03:
                continue  # rests directly on the ceiling beams
            yc = (B0[0] + B1[0]) / 2
            ya, yb = yc - pr["largura_y"] / 2, yc + pr["largura_y"] / 2

            def z_sob(y, B0=B0, B1=B1):  # underside of the purlin (sloped line through B0, B1)
                return B0[1] + (B1[1] - B0[1]) * (y - B0[0]) / (B1[0] - B0[0])

            for xv in vigas_x:
                xa_, xb_ = xv - pr["largura_x"] / 2, xv + pr["largura_x"] / 2
                base = [(xa_, ya, z_vig), (xb_, ya, z_vig), (xb_, yb, z_vig), (xa_, yb, z_vig)]
                topo = [(x, y, z_sob(y)) for x, y, _z in base]
                n_prumos += 1
                h = z_sob(yc) - z_vig
                peca(f"Prumo {lado} {k + 1:02d}.{vigas_x.index(xv) + 1:02d}", "1.9", pr["seccao"], "Prumo",
                     [{"b": [[R(c) for c in q] for q in base], "t": [[R(c) for c in q] for q in topo]}], h,
                     h * pr["largura_x"] * pr["largura_y"])
    # gable triangles on the tie beams of the end walls (under the purlins)
    dvh = hv / ct

    def vt_topo(y):
        return plano(y) - dvh - z_teto

    for nome, x_c in (("EMP.O", te / 2), ("EMP.E", L - te / 2)):
        chave = f"{nome}__dc"
        ms = emoldurar_empena(te, D - te, vt_topo, yr, ext_c, E, ct)
        alcados[chave] = {"W": D - 2 * te, "H": vt_topo(yr), "members": ms, "frame_u0": te, "frame_u1": D - te,
                          "section": ext_c["seccao_montante"], "aberturas": [], "sistema": "discovercasa", "studs": []}
        paineis.append({"nome": nome, "alcado": chave, "piso": 2, "tipo": "PE", "origem": [x_c, 0.0, round(z_teto, 4)],
                        "sentido": [0.0, 1.0], "espessura": te, "encaixe": "-", "extra": 0, "exterior": True})

    G2 = copy.deepcopy(G)
    G2["casa"].update({"espessura_exterior": te, "espessura_interior": ti})
    G2["niveis"].update({"topo_modulos_piso1": round(z_mod, 4), "teto_piso1": round(z_teto, 4),
                         "topo_vigas_teto": round(z_vig, 4)})
    if Pv:  # topo_vigas_pavimento = top of the floor structure (battens), under the OSB deck
        G2["niveis"].update({"piso1_exterior": round(z_p1, 4), "piso1_interior": round(z_p1, 4),
                             "topo_vigas_pavimento": round(z_ba, 4), "osb_pavimento": Pv["osb"],
                             "subida_pavimento": round(subida, 4)})
    G2["pavimento"] = pav
    G2["alcados"], G2["paineis"] = alcados, paineis
    G2["cobertura"].update({"sistema": "discovercasa", "inclinacao": round(math.degrees(th), 3),
                            "plano_z_cume": round(z0, 4), "vigas_teto_x": [round(x, 4) for x in vigas_x],
                            "vigas_teto_largura": vt_["largura"], "manter": manter})
    G2["cobertura_planta"] = []
    G2["estrutura_extra"] = extra
    G2["notas_modelo"] = G.get("notas_modelo", []) + [
        "Estrutura DiscoverCasa (sistema_construtivo.json 'estrutura'): mesmas dimensões e vãos dos desenhos, "
        "montantes 110x35 (exterior) / 75x35 (interior) a 40 cm livres, 110x75 nos cantos e vãos.",
        "Piso 1 com teto falso plano à altura da viga de amarração; cobertura em prumos + vigas de apoio à "
        "cobertura 110x75 sobre as vigas de apoio ao teto 220x75; empenas em triângulo sobre a amarração.",
        "Portas que os desenhos deixam como intervalo entre módulos: bandeira por cima da porta (altura "
        f"{pi['altura']:.2f} m acima do pavimento acabado) e ombreiras 110x75 nos módulos ao lado."]
    if Pv:
        G2["notas_modelo"].append(
            f"Pavimento entre pisos DiscoverCasa: vigas {Pv['vigas']['seccao']} a {Pv['vigas']['espacamento']:.2f} m, "
            f"barrotes {Pv['barrotes']['seccao']} deitados a {Pv['barrotes']['espacamento']:.2f} m entre eixos, "
            f"OSB {round(Pv['osb'] * 1000)} mm; o piso 1 sobe {subida * 100:.1f} cm em relação aos desenhos.")
    resumo = {"paineis": len(paineis), "pecas_paredes": sum(len(a["members"]) for a in alcados.values()),
              "pavimento": {k: pav[k] for k in ("n_vigas", "n_barrotes", "vigas_principais") if k in pav},
              "piso1": round(z_p1, 3), "subida": round(subida, 3),
              "vigas_teto": len(vigas_x), "madres": len(madres), "prumos": n_prumos,
              "z_modulos": round(z_mod, 3), "z_teto": round(z_teto, 3), "z_vigas": round(z_vig, 3),
              "cumeeira_painel": round(z0, 3), "cumeeira_desenho": round(z_cume_desenho, 3),
              "inclinacao": round(math.degrees(th), 2), "bandeiras": bandeiras, "encostadas": encostadas,
              "paredes_extra": [n["nome"] for n in novas], "removidos": sorted(remover)}
    return G2, resumo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--saida")
    a = ap.parse_args()
    cfg_path = Path(a.config).resolve()
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    G = json.load(open(cfg_path.parent / cfg["saida"]["geometria"], encoding="utf-8"))
    S = fundir(json.load(open(AQUI / "sistema_construtivo.json", encoding="utf-8")), cfg.get("camadas") or {})
    E = fundir(S["estrutura"], {k: v for k, v in (cfg.get("estrutura") or {}).items() if k != "sistema"})
    G2, resumo = converter(G, S, E)
    saida = Path(a.saida) if a.saida else pasta_trabalho("modelos", cfg_path.parent.name) / "geometria_dc.json"
    saida.write_text(json.dumps(G2, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("estrutura DiscoverCasa:", json.dumps(resumo, ensure_ascii=False), "->", saida)


if __name__ == "__main__":
    main()
