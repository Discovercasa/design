"""DiscoverCasa module sheets plotted to PDF ("modulos piso 1 ext.pdf" ...): every module as it was made — its members
(the cut list), openings and wall area. Pure Python (standard library).

    python ferramentas/documentos/modulos_pdf.py "<sheet>.pdf" --tipo exterior|interior [--saida modulos.json]

The company's module sheet (one storey, exterior or interior modules; the same layout as D2503, read for DWFx by
ferramentas/modelo/modulos_dc.py): the plan with every module in section (footprint t thick: 0,11 exterior / 0,075
interior) and labelled "M001"; each module's elevation drawn beside the plan, the modules of one wall side by side,
with its label and its length dimensioned. Members by colour (no legend; conhecimento/sistema-construtivo.md §2,
"Module framing"): black = studs and plates (110x35 exterior / 75x35 interior), red #ED1F24 hatched = 110x75 (corner
posts, jambs, headers, sills; turned in a 75 interior wall), orange = 220x75 (lintels of wide openings).

How it reads (no scale on the sheet, "sem escala", and not the same on every sheet):
1. scale = the median of (dimension line length / its number) over the sheet's dimensions (ticks at 45°);
2. elevation members = the coloured rectangles that are not plan items (footprints, studs or posts seen in section);
   touching members are grouped: one group = the elevation of one wall (one or more modules);
3. a group's direction from its labels (text along it) or its plates; the modules from its plates (each module has
   its own top and bottom plates, so a plate's ends are module joints; a door cuts the bottom plate, so the edge
   with fewer breaks is used); labels give the names, the numbers check the lengths;
4. openings: between two red posts, under a red / orange header; a window has a second red piece (the sill), a
   door has no bottom plate there (that edge is the floor).
Output: {"folha", "tipo", "escala_mm_m", "modulos": [{"nome", "comprimento", "altura", "membros": [{"seccao",
"comprimento", "tipo"}], "aberturas": [{"tipo", "largura", "altura", "peitoril"}], "area_bruta", "area_vaos"}],
"avisos": [...]}. Written 2026-11-19 for Ribamar (the user's module sheets in the hub, generator «Documentos
adicionais»).
"""
import argparse
import json
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.dwfx.leitor_pdf import Pdf  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PRETO, VERMELHO, LARANJA = "#000000", "#ED1F24", ("#F4791A", "#F26722")
COTAS = ("#000000", "#939598", "#989898", "#333333")
ROTULO = re.compile(r"M\d{2,3}(?: ?[A-Z])?")
NUMERO = re.compile(r"\d+(?:,\d+)?")
ESPESSURA = {"exterior": 0.11, "interior": 0.075}
SECCAO = {("P", "exterior"): "110x35", ("P", "interior"): "75x35", ("R", "exterior"): "110x75",
          ("R", "interior"): "110x75", ("L", "exterior"): "220x75", ("L", "interior"): "220x75"}
LARGURA = {"P": 0.035, "R": 0.075, "L": 0.22}   # the member's width as drawn in the elevation (m)


# ============================================================================ sheet primitives
def retangulos(d, folha=1):
    """Axis-aligned closed rectangles of the member colours: {(c, x0, x1, y0, y1)} sheet mm (c: P black, R red, L orange)."""
    out = set()
    for p in d.paths(folha):
        st = p.get("stroke")
        c = "P" if st == PRETO else "R" if st == VERMELHO else "L" if st in LARANJA else None
        if not c:
            continue
        for sp, _cl in p["subs"]:
            q = []
            for pt in sp:
                if not q or abs(pt[0] - q[-1][0]) + abs(pt[1] - q[-1][1]) > 1e-4:
                    q.append(pt)
            if len(q) > 1 and abs(q[0][0] - q[-1][0]) + abs(q[0][1] - q[-1][1]) < 1e-4:
                q.pop()
            if len(q) != 4:
                continue
            xs = sorted({round(x, 3) for x, _y in q})
            ys = sorted({round(y, 3) for _x, y in q})
            if len(xs) == 2 and len(ys) == 2 and min(xs[1] - xs[0], ys[1] - ys[0]) < 6.0:
                out.add((c, xs[0], xs[1], ys[0], ys[1]))
    return out


def escala(d, textos, folha=1):
    """mm of sheet per metre: the median of dimension line / number. ([] when the sheet has no readable dimension.)"""
    ticks = []
    for p in d.paths(folha):
        if p.get("stroke") not in COTAS:
            continue
        for sp, _cl in p["subs"]:
            if len(sp) != 2:
                continue
            (ax, ay), (bx, by) = sp
            L = math.hypot(bx - ax, by - ay)
            if 0.6 < L < 1.8 and abs(abs(bx - ax) - abs(by - ay)) < 0.15:
                ticks.append(((ax + bx) / 2, (ay + by) / 2))
    linhas_h, linhas_v = defaultdict(list), defaultdict(list)
    for x, y in ticks:
        linhas_h[round(y, 1)].append(x)
        linhas_v[round(x, 1)].append(y)
    razoes = []
    for s, x, y, _h, ang in textos:
        if not NUMERO.fullmatch(s.strip()):
            continue
        v = float(s.replace(",", "."))
        if not 0.3 <= v <= 30:
            continue
        horiz = abs(ang) in (0, 180)
        melhor = None
        for k, lst in (linhas_h if horiz else linhas_v).items():
            dist = abs(k - (y if horiz else x))
            if dist > 3.5:
                continue
            pos = sorted(lst)
            alvo = x if horiz else y
            for a, b in zip(pos, pos[1:]):
                if a - 1 <= alvo <= b + 1 and b - a > 0.5 and (melhor is None or dist < melhor[0]):
                    melhor = (dist, (b - a) / v)
        if melhor:
            razoes.append(melhor[1])
    return (statistics.median(razoes) if razoes else None), razoes, ticks


# ============================================================================ elevations
def membros_alcado(rects, s, tipo):
    """The elevation members (plan footprints and members seen in section left out)."""
    t = ESPESSURA[tipo]
    out = []
    for c, x0, x1, y0, y1 in rects:
        fino, longo = min(x1 - x0, y1 - y0), max(x1 - x0, y1 - y0)
        w = LARGURA[c] * s
        if abs(fino - w) > 0.3 * w:
            continue
        if c == "P" and longo <= 1.2 * 0.11 * s:
            continue  # a stud in plan (0,035 x t) or a scrap
        if c == "R" and longo <= 1.2 * 0.11 * s:
            continue  # a 110x75 post in plan
        out.append((c, x0, x1, y0, y1))
    return out


def grupos(ms, folga=0.06):
    n = len(ms)
    pai = list(range(n))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    ordem = sorted(range(n), key=lambda i: ms[i][1])
    for k, i in enumerate(ordem):
        a = ms[i]
        for j in ordem[k + 1:]:
            b = ms[j]
            if b[1] > a[2] + folga:
                break
            if a[3] - folga <= b[4] and b[3] - folga <= a[4]:
                pai[raiz(i)] = raiz(j)
    g = defaultdict(list)
    for i in range(n):
        g[raiz(i)].append(ms[i])
    return [v for v in g.values() if len(v) >= 3]


def _uv(m, eixo, caixa):
    """Member in the group's own frame (sheet mm): u along the wall, v across (from the group's min)."""
    c, x0, x1, y0, y1 = m
    if eixo == "x":
        return c, x0 - caixa[0], x1 - caixa[0], y0 - caixa[2], y1 - caixa[2]
    return c, y0 - caixa[2], y1 - caixa[2], x0 - caixa[0], x1 - caixa[0]


def _dist_caixa(x, y, c):
    x0, x1, y0, y1 = c
    return math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1))


def _intervalos(ivs, tol):
    out = []
    for a, b in sorted(ivs):
        if out and a <= out[-1][1] + tol:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def ler_folha(caminho, tipo, folha=1):
    d = Pdf(caminho)
    textos = d.textos(folha)
    s, razoes, ticks = escala(d, textos, folha)
    avisos = []
    if not s:
        raise SystemExit(f"{caminho}: sem cotas legíveis para a escala")
    if razoes and (max(razoes) - min(razoes)) / s > 0.03:
        avisos.append(f"escala: cotas entre {min(razoes):.3f} e {max(razoes):.3f} mm/m (mediana {s:.3f})")
    rects = retangulos(d, folha)
    ms = membros_alcado(rects, s, tipo)
    rotulos = []
    pegadas = [r for r in rects if r[0] == "P" and abs(min(r[2] - r[1], r[4] - r[3]) - ESPESSURA[tipo] * s) < 0.2 * ESPESSURA[tipo] * s
               and max(r[2] - r[1], r[4] - r[3]) > 0.25 * s]
    for st, x, y, h, ang in textos:
        if not ROTULO.fullmatch(st.strip()):
            continue
        ext = len(st.strip()) * h * 0.62  # the run's length (text along its angle; y down on the sheet)
        cx, cy = x + ext / 2 * math.cos(math.radians(ang)), y - ext / 2 * math.sin(math.radians(ang))
        if any(_dist_caixa(cx, cy, r[1:]) < 6.0 for r in pegadas):
            continue  # a label of the plan
        rotulos.append((st.strip(), cx, cy, h, ang))
    numeros = [(float(st.replace(",", ".")), x, y, h, ang) for st, x, y, h, ang in textos if NUMERO.fullmatch(st.strip())]
    tol = 0.012 * s  # 1,2 cm
    modulos = []
    gs = grupos(ms)
    caixas = [(min(m[1] for m in g), max(m[2] for m in g), min(m[3] for m in g), max(m[4] for m in g)) for g in gs]
    # each label belongs to the elevation whose dimension line it stands by (the labels sit beyond the module's
    # length dimension, sometimes nearer the next elevation than their own), else to the nearest elevation
    def linhas_cota(c):
        X0, X1, Y0, Y1 = c
        out = []
        for eixo in ("x", "y"):
            lo, hi = (X0, X1) if eixo == "x" else (Y0, Y1)
            b0, b1 = (Y0, Y1) if eixo == "x" else (X0, X1)
            por = defaultdict(list)
            for tx, ty in ticks:
                u, w = (tx, ty) if eixo == "x" else (ty, tx)
                if lo - 2 <= u <= hi + 2 and (b0 - 12 <= w < b0 - 0.3 or b1 + 0.3 < w <= b1 + 12):
                    por[round(w, 1)].append(u)
            for w, us in por.items():
                if len(us) >= 2 and max(us) - min(us) > 0.3 * (hi - lo):
                    out.append((eixo, w, lo, hi))
        return out

    cotas_g = [linhas_cota(c) for c in caixas]
    dono = defaultdict(list)
    for r in rotulos:
        custos = []
        for k, c in enumerate(caixas):
            dc = _dist_caixa(r[1], r[2], c)
            if dc > 22:
                continue
            custo = dc + 5
            for eixo, w, lo, hi in cotas_g[k]:
                u, rw = (r[1], r[2]) if eixo == "x" else (r[2], r[1])
                if lo - 3 <= u <= hi + 3:
                    custo = min(custo, abs(rw - w))
            custos.append((custo, k))
        if custos:
            dono[min(custos)[1]].append(r)
    for kg, g in enumerate(gs):
        X0, X1, Y0, Y1 = caixa = caixas[kg]
        # direction: the labels beside the group (their text runs along the wall), else the plates
        perto = dono[kg]
        votos = defaultdict(int)
        for r in perto:
            votos["x" if abs(r[4]) in (0, 180) else "y"] += 1
        if votos:
            eixo = max(votos, key=votos.get)
        else:
            eixo = "x" if X1 - X0 >= Y1 - Y0 else "y"
        uv = [_uv(m, eixo, caixa) for m in g]
        Lg = (X1 - X0) if eixo == "x" else (Y1 - Y0)
        Hg = (Y1 - Y0) if eixo == "x" else (X1 - X0)
        horiz = [m for m in uv if m[2] - m[1] > m[4] - m[3]]
        # plates: black horizontals touching the group's edges (v = 0 / v = max of the module: modules may differ in
        # height, so an edge plate is one with nothing beyond it at its u range)
        def borda(m, lado):
            c, u0, u1, v0, v1 = m
            for o in uv:
                if o is m or o[2] <= u0 + tol or o[1] >= u1 - tol:
                    continue
                if (lado == 0 and o[3] < v0 - 0.1) or (lado == 1 and o[4] > v1 + 0.1):
                    return False
            return True
        placas = {0: [m for m in horiz if m[0] == "P" and borda(m, 0)], 1: [m for m in horiz if m[0] == "P" and borda(m, 1)]}
        # the edge with fewer breaks gives the joints (a door cuts the bottom plate)
        pontas = {}
        for lado, lst in placas.items():
            pontas[lado] = sorted({round(m[1], 2) for m in lst} | {round(m[2], 2) for m in lst})
        cobre = {lado: sum(m[2] - m[1] for m in lst) for lado, lst in placas.items()}
        topo = max((0, 1), key=lambda k: (cobre[k] > 0.97 * Lg, -len(pontas[k]), cobre[k]))
        juntas = [0.0]
        verticais = [m for m in uv if m[4] - m[3] > m[2] - m[1]]
        pl = sorted(placas[topo], key=lambda m: m[1])
        # consecutive plates meet at a joint; where the drawing overlaps them (a plate drawn too long over the next
        # module's end post), the joint is where the next module's plate and end member start
        for p_, q_ in zip(pl, pl[1:]):
            if q_[1] >= p_[2] - tol:
                j = q_[1]
            else:
                j = q_[1] if any(abs(m[1] - q_[1]) < tol for m in verticais) else p_[2]
                # a jamb in the overlap goes with the header or sill it carries
                cab = [m for m in uv if m[0] in ("R", "L") and m[2] - m[1] > m[4] - m[3]]
                for v_ in verticais:
                    if v_[0] == "R" and q_[1] - tol <= v_[1] and v_[2] <= p_[2] + tol:
                        if any(abs(h[1] - v_[2]) < tol for h in cab):
                            j = v_[1]
                        elif any(abs(h[2] - v_[1]) < tol for h in cab):
                            j = v_[2]
            if all(abs(j - k) > 0.15 * s for k in juntas) and abs(j - Lg) > 0.15 * s:
                juntas.append(j)
        if pl and pl[0][1] > 0.15 * s:
            juntas.append(pl[0][1])
        if pl and Lg - pl[-1][2] > 0.15 * s:
            juntas.append(pl[-1][2])
        if all(abs(Lg - j) > 0.15 * s for j in juntas):
            juntas.append(Lg)
        juntas.sort()
        if cobre[topo] < 0.97 * Lg:
            avisos.append(f"grupo em ({X0:.0f}, {Y0:.0f}) mm: placa {'superior' if topo else 'inferior'} cobre só "
                          f"{cobre[topo] / s:.2f} de {Lg / s:.2f} m (juntas incertas)")
        chao = 1 - topo  # the floor: the edge whose plate is cut by doors (if neither is cut, a guess)
        for a, b in zip(juntas, juntas[1:]):
            mm_ = [m for m in uv if m[1] >= a - tol and m[2] <= b + tol]
            if not mm_:
                continue
            v_lo, v_hi = min(m[3] for m in mm_), max(m[4] for m in mm_)
            L, H = (b - a) / s, (v_hi - v_lo) / s
            # name: the label beside this stretch (outside the band), the number next to it
            uc = (a + b) / 2
            nome, comp_rot = None, None
            cand = []
            for r in perto:
                ru = (r[1] - X0) if eixo == "x" else (r[2] - Y0)
                cand.append((0 if a - 1 <= ru <= b + 1 else 1, abs(ru - uc), r[0]))
            if cand:
                nome = min(cand)[2]
            for v, x, y, h, ang in numeros:
                ru = (x - X0) if eixo == "x" else (y - Y0)
                rv = (y - Y0) if eixo == "x" else (x - X0)
                horiz_txt = abs(ang) in (0, 180)
                if (eixo == "x") != horiz_txt or not (a - 3 <= ru <= b + 3):
                    continue
                if -12 <= rv <= 0 or Hg <= rv <= Hg + 12:
                    if abs(v - L) < 0.06 and (comp_rot is None or abs(v - L) < abs(comp_rot - L)):
                        comp_rot = v
            membros = []
            for c, u0, u1, v0, v1 in mm_:
                lu, lv = (u1 - u0) / s, (v1 - v0) / s
                along = lu > lv
                comp = max(lu, lv)
                if c == "P":
                    k = "Travessa" if along else "Montante"
                elif c == "L":
                    k = "Verga 22x7,5"
                else:
                    k = "Padieira / peitoril" if along else "Prumo 11x7,5"
                membros.append({"cor": c, "seccao": SECCAO[(c, tipo)], "comprimento": round(comp, 4), "tipo": k,
                                "u": [round((u0 - a) / s, 4), round((u1 - a) / s, 4)],
                                "v": [round((v0 - v_lo) / s, 4), round((v1 - v_lo) / s, 4)]})
            aberturas = vaos(membros, L, H, chao_alto=chao_do_modulo(membros, H, chao == 1))
            area_vaos = sum(o["largura"] * o["altura"] for o in aberturas)
            modulos.append({"nome": nome, "eixo": eixo, "comprimento": round(L, 3), "comprimento_cota": comp_rot,
                            "altura": round(H, 3), "membros": membros, "aberturas": aberturas,
                            "area_bruta": round(L * H, 3), "area_vaos": round(area_vaos, 3),
                            "folha_mm": [round(X0 + a if eixo == "x" else X0, 1), round(Y0 if eixo == "x" else Y0 + a, 1)],
                            "_grupo": kg})
    juntos = []
    for m in modulos:
        p = juntos[-1] if juntos else None
        if p and m["nome"] and p["nome"] == m["nome"] and p.get("_grupo") == m.get("_grupo") and m["eixo"] == p["eixo"]:
            off = p["comprimento"]
            for mb in m["membros"]:
                mb["u"] = [round(mb["u"][0] + off, 4), round(mb["u"][1] + off, 4)]
            p["membros"] += m["membros"]
            p["aberturas"] += m["aberturas"]
            p["comprimento"] = round(p["comprimento"] + m["comprimento"], 3)
            p["altura"] = max(p["altura"], m["altura"])
            p["area_bruta"] = round(p["area_bruta"] + m["area_bruta"], 3)
            p["area_vaos"] = round(p["area_vaos"] + m["area_vaos"], 3)
            p["partes"] = p.get("partes", 1) + 1
            continue
        juntos.append(m)
    modulos = juntos
    for m in modulos:
        m.pop("_grupo", None)
    nomes = defaultdict(int)
    for m in modulos:
        nomes[m["nome"]] += 1
    for n_, k in nomes.items():
        if n_ is None or k > 1:
            avisos.append(f"módulo {n_ or 'sem nome'} lido {k} vez(es): ver o desenho")
    todos = sorted({r[0] for r in rotulos})
    for n_ in todos:
        if n_ not in nomes:
            avisos.append(f"rótulo {n_} sem alçado encontrado")
    modulos.sort(key=lambda m: (m["nome"] or "~"))
    return {"folha": Path(caminho).name, "tipo": tipo, "escala_mm_m": round(s, 3), "modulos": modulos, "avisos": avisos}


def chao_do_modulo(membros, H, palpite):
    """Is the floor the module's high edge (v = H)? A lintel or header against one edge is the top; else a bottom
    plate shorter than the top one (cut at a door) is the floor; else the group's guess."""
    for m in membros:
        if m["cor"] in ("L", "R") and m["tipo"] != "Prumo 11x7,5":
            if m["v"][1] > H - 0.05:
                return False
            if m["v"][0] < 0.05:
                return True
    lo = sum(m["comprimento"] for m in membros if m["cor"] == "P" and m["tipo"] == "Travessa" and m["v"][0] < 0.02)
    hi = sum(m["comprimento"] for m in membros if m["cor"] == "P" and m["tipo"] == "Travessa" and m["v"][1] > H - 0.02)
    if abs(lo - hi) > 0.2:
        return hi < lo
    return palpite


def vaos(membros, L, H, chao_alto=False):
    """Openings of one module: between two red posts under a red / orange header; a second red piece across = the
    sill (window), none and the bottom plate cut = a door. v from the floor (chao_alto: the floor is the high edge)."""
    def vv(m):  # v from the floor
        v0, v1 = m["v"]
        return (H - v1, H - v0) if chao_alto else (v0, v1)

    postes = sorted([m for m in membros if m["cor"] == "R" and m["tipo"] == "Prumo 11x7,5" and m["comprimento"] > 0.5],
                    key=lambda m: m["u"][0])
    trav = [m for m in membros if m["cor"] in ("R", "L") and m["tipo"] != "Prumo 11x7,5"]
    placas_chao = [m for m in membros if m["cor"] == "P" and m["tipo"] == "Travessa" and vv(m)[0] < 0.02]
    out = []
    for p, q in zip(postes, postes[1:]):
        uL, uR = p["u"][1], q["u"][0]
        if uR - uL < 0.3:
            continue
        hs = sorted([h for h in trav if h["u"][0] <= uL + 0.03 and h["u"][1] >= uR - 0.03], key=lambda h: vv(h)[0])
        if not hs:
            continue
        mid = (uL + uR) / 2
        sem_placa = not any(m["u"][0] < mid < m["u"][1] for m in placas_chao)
        if sem_placa:  # door: from the floor up to the lowest header
            topo = hs[0]
            out.append({"tipo": "porta", "largura": round(uR - uL, 3), "altura": round(vv(topo)[0], 3), "peitoril": 0.0})
        elif len(hs) >= 2:
            sill, topo = hs[0], hs[1]
            out.append({"tipo": "janela", "largura": round(uR - uL, 3), "altura": round(vv(topo)[0] - vv(sill)[1], 3),
                        "peitoril": round(vv(sill)[1], 3)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--tipo", choices=("exterior", "interior"), required=True)
    ap.add_argument("--saida")
    a = ap.parse_args()
    r = ler_folha(a.pdf, a.tipo)
    print(f"{r['folha']} ({r['tipo']}): escala {r['escala_mm_m']} mm/m, {len(r['modulos'])} módulos")
    tot = defaultdict(lambda: [0, 0.0])
    for m in r["modulos"]:
        ck = "" if m["comprimento_cota"] is None else (" ok" if abs(m["comprimento_cota"] - m["comprimento"]) < 0.02 else f" cota {m['comprimento_cota']}")
        print(f"  {m['nome'] or '?':7s} {m['eixo']} L {m['comprimento']:.2f}{ck:10s} H {m['altura']:.2f}  peças {len(m['membros']):3d}  "
              + ", ".join(f"{o['tipo']} {o['largura']:.2f}x{o['altura']:.2f}" + (f"@{o['peitoril']:.2f}" if o['tipo'] == 'janela' else '')
                          for o in m["aberturas"]))
        for mb in m["membros"]:
            tot[mb["seccao"]][0] += 1
            tot[mb["seccao"]][1] += mb["comprimento"]
    for sec, (n, L) in sorted(tot.items()):
        print(f"  {sec}: {n} peças, {L:.1f} m")
    for w in r["avisos"]:
        print("  AVISO", w)
    if a.saida:
        Path(a.saida).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print("->", a.saida)


if __name__ == "__main__":
    main()
