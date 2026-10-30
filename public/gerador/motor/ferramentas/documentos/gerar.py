"""Production documents of a DiscoverCasa house, in the company's D2503 standard, generated from the model:

    python ferramentas/documentos/gerar.py "<project>/modelos/casa/config.json" [--saida DIR] [--sem-reconstruir]

Rebuilds the model data (casa_planta.py + camadas.py, no Blender) and writes to <project>/documentos/:
  <obra>_Modulos.pdf            plan of the modules, elevations of every module (members by section: black
                                11x3,5 / 7,5x3,5, red 11x7,5 / 7,5x11; openings), dimensions and quantities table,
                                cut list ("Comprimento das vigas")
  <obra>_Cobertura.pdf          hidden roof: lameladas and amarração, madres / prumos / caleiras with their falls and
                                outlets, sandwich panels, typical sections through the lameladas; exposed roof: slopes
                                and their lines, ceiling beams / glulams / headers, purlins / hips / valleys / prumos,
                                panels and flashings, sections across the ridges
  <obra>_Listagem_Material.pdf  material list by chapter (structure, walls, insulation, floors, ceilings, roof,
  <obra>_Listagem_Material.csv  windows and doors, pergola), purchase units, cut list
Config "documentos" (optional): obra (code, e.g. D2503), projeto, local, revisoes [[rev, data, texto]].
"""
import argparse
import csv
import datetime
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.documentos.dados import (Casa, caixa_planta, comprimento_membro, contorno_planta, corte,  # noqa: E402
                                          corte_x)
from ferramentas.documentos.folha import (A4, AZUL, CASTANHO, CINZA, CINZA_CLARO, CORES_TIPO, ESCURO_DC, MAGENTA,  # noqa: E402
                                          PRETO, VERDE, VERMELHO, Tabela, Vista, cota_h, cota_v, escala_para, fmt,
                                          folha, logo, seccao)
from ferramentas.documentos.pdf import PDF, hexcor, largura  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AZUL_CLARO = hexcor("#CFE3F5")
SVG = None  # folder for SVG previews of every sheet (--svg)
VERMELHO_CLARO = hexcor("#FBD3D3")


def clarear(cor, f=0.7):
    return tuple(c + (1 - c) * f for c in cor)


def ordem_secoes(s):
    try:
        a, b = s.lower().split("x")
        return (-float(a), -float(b))
    except ValueError:
        return (0, 0)


class Documento:
    """Sheets drawn in two passes (the total count goes in every title block)."""

    def __init__(self, info, titulo_pdf):
        self.info, self.pdf, self.folhas = info, PDF(titulo=titulo_pdf), []

    def add(self, titulo, escala, legenda, desenho, notas=()):
        self.folhas.append((titulo, escala, legenda, desenho, notas))

    def gravar(self, caminho):
        n = len(self.folhas)
        for i, (titulo, escala, legenda, desenho, notas) in enumerate(self.folhas, 1):
            pg = folha(self.pdf, self.info, titulo, i, n, escala, legenda, notas)
            desenho(pg)
        self.pdf.gravar(caminho)
        if SVG:
            self.pdf.gravar_svg(SVG, Path(caminho).stem)
        return n


# ============================================================================ MÓDULOS
def membro_cor(mb):
    us, vs = [q[0] for q in mb["poly"]], [q[1] for q in mb["poly"]]
    fino = min(max(us) - min(us), max(vs) - min(vs))
    if mb["section"].startswith("220"):
        return hexcor("#E07B00"), clarear(hexcor("#E07B00"), 0.75)
    return (PRETO, None) if fino < 0.05 else (VERMELHO, VERMELHO_CLARO)


def planta_modulos(casa):
    xs = [v for m in casa.modulos for v in m.pegada()[:2]]
    ys = [v for m in casa.modulos for v in m.pegada()[2:]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    e = escala_para(x1 - x0, y1 - y0, 280, 205)
    k = 1000 / e
    px0 = 10 + (340 - (x1 - x0) * k) / 2
    py0 = 12 + (275 - (y1 - y0) * k) / 2
    V = Vista(px0, py0, e, x0, y0)

    def desenho(pg):
        for m in sorted(casa.modulos, key=lambda m: m.exterior):
            a, b, c, d = m.pegada()
            (pa, pc), (pb, pd) = V.p(a, c), V.p(b, d)
            cor = PRETO if m.exterior else VERDE
            pg.ret(pa, pc, pb - pa, pd - pc, esp=0.3 if m.exterior else 0.22, cor=cor,
                   preench=(0.9, 0.9, 0.9) if m.exterior else (0.94, 0.97, 0.94))
            cx, cy = (pa + pb) / 2, (pc + pd) / 2
            ang = 90 if m.eixo == "y" else 0
            off = (-1.6 if m.exterior else -1.4) if ang == 0 else 0
            lado = 3.2 if m.exterior else 2.4
            if m.eixo == "x":
                ty = cy + (lado if (m.fora > 0) else -lado - 1.6) if m.exterior else cy + 1.6
                pg.texto(cx, ty, m.rotulo, 2.0 if m.exterior else 1.7, AZUL if m.exterior else VERDE, negrito=m.exterior, alinh="c")
            else:
                tx = cx + (-lado if (m.fora > 0) else lado + 1.6) if m.exterior else cx - 1.6
                pg.texto(tx, cy, m.rotulo, 2.0 if m.exterior else 1.7, AZUL if m.exterior else VERDE, negrito=m.exterior,
                         alinh="c", ang=90)
            del off
        # module lengths along every exterior wall, outside it
        for pid, mods in casa.paredes(True).items():
            m0 = mods[0]
            if m0.eixo == "x":
                a, b, c, d = m0.pegada()
                yf = d if m0.fora > 0 else c
                pts = [V.p(m.pegada()[0], yf)[0] for m in mods] + [V.p(mods[-1].pegada()[1], yf)[0]]
                yo = V.p(0, yf)[1]
                cota_h(pg, pts, yo + (1 if m0.fora > 0 else -1) * 7.0, yo + (1 if m0.fora > 0 else -1) * 9.0,
                       [fmt(m.W) for m in mods], 1.8)
            else:
                a, b, c, d = m0.pegada()
                xf = a if m0.fora > 0 else b
                pts = [V.p(xf, m.pegada()[2])[1] for m in mods] + [V.p(xf, mods[-1].pegada()[3])[1]]
                xo = V.p(xf, 0)[0]
                cota_v(pg, pts, xo + (-1 if m0.fora > 0 else 1) * 7.0, xo + (-1 if m0.fora > 0 else 1) * 9.0,
                       [fmt(m.W) for m in mods], 1.8)
        # overall
        if casa.contorno:
            cx_ = sorted({round(p[0], 3) for p in casa.contorno})
            cy_ = sorted({round(p[1], 3) for p in casa.contorno})
            ytop = V.p(0, max(cy_))[1]
            cota_h(pg, [V.p(x, 0)[0] for x in cx_], ytop + 16, ytop + 18, [fmt(b - a) for a, b in zip(cx_, cx_[1:])], 2.2)
            cota_h(pg, [V.p(cx_[0], 0)[0], V.p(cx_[-1], 0)[0]], ytop + 22, ytop + 24, [fmt(cx_[-1] - cx_[0])], 2.4)
            xl = V.p(min(cx_), 0)[0]
            cota_v(pg, [V.p(0, y)[1] for y in cy_], xl - 16, xl - 18, [fmt(b - a) for a, b in zip(cy_, cy_[1:])], 2.2)
            cota_v(pg, [V.p(0, cy_[0])[1], V.p(0, cy_[-1])[1]], xl - 22, xl - 24, [fmt(cy_[-1] - cy_[0])], 2.4)
        pg.texto(V.p(x0, 0)[0], 14, "PLANTA DOS MÓDULOS (exteriores a negro, interiores a verde)", 2.6, PRETO, negrito=True)
    return e, desenho


def layout_alcados(casa, exterior):
    paredes = casa.paredes(exterior)
    ordem = {"Norte": 0, "Poente": 1, "Sul": 2, "Nascente": 3, "": 4}
    ids = sorted(paredes, key=lambda p: (ordem[paredes[p][0].orientacao()], p))
    larg = {}
    for p in ids:
        ms = paredes[p]
        s = [m.o[0] if m.eixo == "x" else m.o[1] for m in ms]
        larg[p] = (min(s), max(si + m.W for si, m in zip(s, ms)))
    Lmax = max(b - a for a, b in larg.values())
    Hmax = max(m.H for ms in paredes.values() for m in ms)
    e = 50
    for cand in (50, 60, 75, 100):
        e = cand
        if Lmax * 1000 / cand <= 330:
            break
    k = 1000 / e
    alt_linha = Hmax * k + 30
    linhas, cur, w = [], [], 0.0
    for p in ids:
        wp = (larg[p][1] - larg[p][0]) * k + 16
        if cur and w + wp > 335:
            linhas.append(cur)
            cur, w = [], 0.0
        cur.append(p)
        w += wp
    if cur:
        linhas.append(cur)
    por_folha = max(1, int(262 // alt_linha))
    folhas = [linhas[i:i + por_folha] for i in range(0, len(linhas), por_folha)]
    return paredes, larg, e, k, alt_linha, folhas


def desenhar_parede(pg, mods, s_min, s_max, x_esq, y_base, k, mirror, exterior, caixa=True):
    def px(s):
        return x_esq + ((s_max - s) if mirror else (s - s_min)) * k

    H = max(m.H for m in mods)
    for m in mods:
        s0 = m.o[0] if m.eixo == "x" else m.o[1]
        a, b = sorted((px(s0), px(s0 + m.W)))
        if caixa:  # the module's outline (not round a gable triangle)
            pg.ret(a, y_base, b - a, m.H * k, esp=0.15, cor=CINZA)
        for mb in m.membros:
            cor, fill = membro_cor(mb)
            pts = [(px(s0 + u), y_base + v * k) for u, v in mb["poly"]]
            pg.poli(pts, True, esp=0.12 if fill is None else 0.18, cor=cor, preench=fill)
        for u0, u1, v0, v1 in m.entalhes:  # lamelada notch, cut on site
            pa, pb = sorted((px(s0 + u0), px(s0 + u1)))
            pg.ret(pa - 0.3, y_base + v0 * k, pb - pa + 0.6, (v1 - v0) * k, esp=0.15, cor=AZUL, tracejado=(0.6, 0.4))
        for ab in m.aberturas:
            u0, u1, v0, v1 = ab[:4]
            pa, pb = sorted((px(s0 + u0), px(s0 + u1)))
            qa, qb = y_base + v0 * k, y_base + v1 * k
            pg.ret(pa, qa, pb - pa, qb - qa, esp=0.12, cor=CINZA, tracejado=(1.0, 0.8))
            pg.linha(pa, qa, pb, qb, 0.08, CINZA_CLARO)
            pg.linha(pa, qb, pb, qa, 0.08, CINZA_CLARO)
            pg.texto((pa + pb) / 2, (qa + qb) / 2 - 0.8, f"{fmt(u1 - u0)}x{fmt(v1 - v0)}", 1.7, ESCURO_DC, alinh="c")
            if v0 > 0.05:
                pg.texto((pa + pb) / 2, qa + 0.8, f"peitoril {fmt(v0)}", 1.4, CINZA, alinh="c")
        pg.texto((a + b) / 2, y_base + m.H * k + 7.6, m.rotulo, 2.0, AZUL if exterior else VERDE, negrito=True, alinh="c")
    ordem = sorted(mods, key=lambda m: px(m.o[0] if m.eixo == "x" else m.o[1]))
    xs = []
    for m in ordem:
        s0 = m.o[0] if m.eixo == "x" else m.o[1]
        xs += sorted((px(s0), px(s0 + m.W)))
    xs0, xs = sorted(xs), []
    for v in xs0:  # module joints closer than 0,3 mm are one point
        if not xs or v - xs[-1] > 0.3:
            xs.append(v)
    cota_h(pg, xs, y_base + H * k + 1.0, y_base + H * k + 3.5, [fmt(abs(b - a) / k) for a, b in zip(xs, xs[1:])], 1.7)
    cota_v(pg, [y_base, y_base + H * k], xs[0] - 1.0, xs[0] - 3.5, [fmt(H)], 1.8)


def doc_modulos(casa, info, caminho):
    D = Documento(info, f"{info['obra']} - Módulos")
    leg_planta = [("ret", PRETO, "Módulos exteriores (Mn a azul)"), ("ret", VERDE, "Módulos interiores (Mn a verde)"),
                  ("cota", VERMELHO, "Comprimento dos módulos / dimensões da fundação e módulos")]
    e, des = planta_modulos(casa)
    D.add("Módulos - Planta", e, leg_planta, des,
          [f"{sum(1 for m in casa.modulos if m.exterior)} módulos exteriores, "
           f"{sum(1 for m in casa.modulos if not m.exterior)} interiores.",
           "Gerado a partir do modelo (método DiscoverCasa)."])
    leg_alc = [("linha", PRETO, "Madeira 11x3,5 / 7,5x3,5"), ("ret", VERMELHO, "Madeira 11x7,5 / 7,5x11 (cantos, ombreiras, padieiras, peitoris)"),
               ("ret", hexcor("#E07B00"), "Madeira 22x7,5"), ("linha", CINZA, "Vão em bruto (L x A)"),
               ("cota", VERMELHO, "Dimensões dos módulos")]
    for exterior in (True, False):
        if not casa.paredes(exterior):
            continue  # a house without interior walls (open plan)
        paredes, larg, e, k, alt_linha, folhas = layout_alcados(casa, exterior)
        for nf, linhas in enumerate(folhas, 1):
            def des(pg, linhas=linhas, paredes=paredes, larg=larg, k=k, alt_linha=alt_linha, exterior=exterior):
                y = 287 - alt_linha + 14
                for linha in linhas:
                    x = 18.0
                    for pid in linha:
                        mods = paredes[pid]
                        s_min, s_max = larg[pid]
                        m0 = mods[0]
                        mirror = exterior and m0.fora > 0
                        desenhar_parede(pg, mods, s_min, s_max, x, y, k, mirror, exterior)
                        rot = f"Parede {pid}" + (f" - {m0.orientacao()} (vista do exterior)" if exterior else " (interior)")
                        pg.texto(x, y - 5.0, rot, 2.2, PRETO, negrito=True)
                        x += (s_max - s_min) * k + 16
                    y -= alt_linha
            tit = f"Módulos {'exteriores' if exterior else 'interiores'} - Alçados" + (f" ({nf}/{len(folhas)})" if len(folhas) > 1 else "")
            D.add(tit, e, leg_alc, des)
        if exterior and casa.empenas:  # the gable triangles of an exposed roof, on the edge beams over the walls
            e_emp = next((c for c in (50, 60, 75, 100) if max(m.W for m in casa.empenas) * 1000 / c <= 330), 100)
            k_e = 1000 / e_emp
            alt_e = max(m.H for m in casa.empenas) * k_e + 30
            filas, cur, w = [], [], 0.0
            for m in casa.empenas:
                wp = m.W * k_e + 16
                if cur and w + wp > 335:
                    filas.append(cur)
                    cur, w = [], 0.0
                cur.append(m)
                w += wp
            if cur:
                filas.append(cur)
            por_f = max(1, int(262 // alt_e))
            grupos = [filas[i:i + por_f] for i in range(0, len(filas), por_f)]
            for nf, fs in enumerate(grupos, 1):
                def des_e(pg, fs=fs):
                    y = 287 - alt_e + 14
                    for fila in fs:
                        x = 18.0
                        for m in fila:
                            s0 = m.o[0] if m.eixo == "x" else m.o[1]
                            desenhar_parede(pg, [m], s0, s0 + m.W, x, y, k_e, m.fora > 0, True, caixa=False)
                            pg.texto(x, y - 5.0, f"Empena {m.parede} - {m.orientacao()} (vista do exterior)", 2.2, PRETO, negrito=True)
                            x += m.W * k_e + 16
                        y -= alt_e
                D.add("Empenas - Alçados" + (f" ({nf}/{len(grupos)})" if len(grupos) > 1 else ""), e_emp, leg_alc, des_e,
                      ["Triângulos da empena sobre a viga de bordo (cobertura à vista): fabricados como os módulos; "
                       "a travessa superior segue a inclinação da cobertura (comprimento real na lista de corte)."])
    # tables
    linhas_q = []
    for exterior in (True, False):
        linhas_q.append("# Módulos exteriores" if exterior else "# Módulos interiores")
        ms = sorted([m for m in casa.modulos if m.exterior == exterior], key=lambda m: int("".join(c for c in m.rotulo if c.isdigit()) or 0))
        for m in ms:
            vaos = ", ".join(f"{fmt(a[1] - a[0])}x{fmt(a[3] - a[2])}" for a in m.aberturas)
            linhas_q.append([m.rotulo + (" *" if m.em_obra else ""), m.parede, fmt(m.W, 3), fmt(m.H, 3), fmt(m.t, 2),
                             str(len(m.membros)), vaos])
        linhas_q.append([f"Total {len(ms)}", "", fmt(sum(m.W for m in ms), 2), "", "", str(sum(len(m.membros) for m in ms)), ""])
    if casa.empenas:
        linhas_q.append("# Empenas (cobertura à vista)")
        for m in casa.empenas:
            linhas_q.append([m.parede, m.orientacao(), fmt(m.W, 3), fmt(m.H, 3), fmt(m.t, 2), str(len(m.membros)), ""])
        linhas_q.append([f"Total {len(casa.empenas)}", "", fmt(sum(m.W for m in casa.empenas), 2), "", "",
                         str(sum(len(m.membros) for m in casa.empenas)), ""])
    if any(m.em_obra for m in casa.modulos):
        linhas_q.append(["*", "", "", "", "", "", "Painel a executar em obra"])
    tq = Tabela("QUADRO DE DIMENSÕES E QUANTIDADES", [("Módulo", 14, "e"), ("Parede", 13, "e"), ("Comp. (m)", 17, "d"),
                                                       ("Alt. (m)", 15, "d"), ("Esp. (m)", 15, "d"), ("Peças", 12, "d"),
                                                       ("Vãos em bruto (L x A)", 44, "e")], linhas_q, 1.8, 3.2)
    corte = casa.lista_corte(True)
    linhas_c = []
    for sec in sorted(corte, key=ordem_secoes):
        linhas_c.append(f"# Madeira {seccao(sec)}")
        n = tot = 0
        for cm, q in sorted(corte[sec].items(), reverse=True):
            linhas_c.append([seccao(sec), fmt(cm / 100), str(q), fmt(q * cm / 100, 2)])
            n += q
            tot += q * cm / 100
        a, b = (float(v) / 1000 for v in sec.lower().split("x"))
        linhas_c.append([f"Total {seccao(sec)}", "", str(n), f"{fmt(tot, 1)} m / {fmt(tot * a * b, 3)} m³"])
    tc = Tabela("COMPRIMENTO DAS VIGAS (lista de corte dos módulos)", [("Secção", 18, "e"), ("Comp. (m)", 18, "d"),
                                                                       ("Quant.", 14, "d"), ("Total", 32, "d")], linhas_c, 1.8, 3.2)
    blocos = [(tq, 0), (tc, 0)]

    def des_tabelas(pg, estado):
        x = 14.0
        for idx in range(len(blocos)):
            t, ini = blocos[idx]
            while ini < len(t.linhas) and x + t.largura() <= 352:
                ini = t.desenhar(pg, x, 282, 14, ini)
                x += t.largura() + 8
            blocos[idx] = (t, ini)
        del estado

    # how many sheets the tables need
    n_folhas = 1
    while True:
        prova = [(t, 0) for t, _ in blocos]
        ok = _simular(prova, n_folhas)
        if ok or n_folhas > 6:
            break
        n_folhas += 1
    for i in range(n_folhas):
        D.add("Módulos - Quadro de dimensões e quantidades / comprimento das vigas" + (f" ({i + 1}/{n_folhas})" if n_folhas > 1 else ""),
              None, [], lambda pg, i=i: des_tabelas(pg, i))
    return D.gravar(caminho)


def _simular(blocos, n_folhas):
    """True if the tables fit in n_folhas sheets (same flow as des_tabelas)."""
    for _ in range(n_folhas):
        x = 14.0
        for idx in range(len(blocos)):
            t, ini = blocos[idx]
            while ini < len(t.linhas) and x + t.largura() <= 352:
                y = 282 - 5.0 - t.alt - 0.6
                while ini < len(t.linhas) and y > 14:
                    y -= t.alt + (0.8 if isinstance(t.linhas[ini], str) else 0)
                    ini += 1
                x += t.largura() + 8
            blocos[idx] = (t, ini)
    return all(ini >= len(t.linhas) for t, ini in blocos)


# ============================================================================ COBERTURA
def tipos_lameladas(casa):
    lams = [e for e in casa.extra if e["colecao"] == "1.7"]
    comps = sorted({round(e["props"]["comprimento_m"], 2) for e in lams})
    letra = {c: chr(65 + i) for i, c in enumerate(comps)}
    return lams, comps, letra


def vista_planta(casa, larg_mm=290, alt_mm=225):
    xs = [p[0] for p in casa.contorno] or [v for m in casa.modulos for v in m.pegada()[:2]]
    ys = [p[1] for p in casa.contorno] or [v for m in casa.modulos for v in m.pegada()[2:]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    e = escala_para(x1 - x0, y1 - y0, larg_mm, alt_mm)
    k = 1000 / e
    px0 = 14 + (300 - (x1 - x0) * k) / 2
    py0 = 22 + (215 - (y1 - y0) * k) / 2
    return Vista(px0, py0, e, x0, y0), e, (x0, x1, y0, y1)


def fundo_planta(pg, casa, V, cor=CINZA_CLARO):
    for m in casa.modulos:
        a, b, c, d = m.pegada()
        (pa, pc), (pb, pd) = V.p(a, c), V.p(b, d)
        pg.ret(pa, pc, pb - pa, pd - pc, esp=0.12, cor=cor, preench=(0.97, 0.95, 0.92) if m.exterior else None)
    if casa.contorno:
        pg.poli([V.p(*p) for p in casa.contorno], True, esp=0.25, cor=CASTANHO)


def ret_planta(pg, V, pc, **kw):
    a, b, c, d, _z0, _z1 = caixa_planta(pc)
    (pa, pc_), (pb, pd) = V.p(a, c), V.p(b, d)
    pts = [(pa, pc_), (pb, pc_), (pb, pd), (pa, pd)]
    pg.poli(pts, True, **kw)
    return pts


def doc_cobertura(casa, info, caminho):
    D = Documento(info, f"{info['obra']} - Cobertura")
    V, e, (x0, x1, y0, y1) = vista_planta(casa)
    lams, comps, letra = tipos_lameladas(casa)
    sec_l = lams[0]["props"]["seccao"] if lams else ""
    a_l, b_l = ((float(v) for v in sec_l.lower().split("x")) if sec_l else (0, 0))
    cores = {c: CORES_TIPO[i % len(CORES_TIPO)] for i, c in enumerate(comps)}
    telh = casa.G["cobertura"].get("telhados", [])
    t_ext = max((m.t for m in casa.modulos if m.exterior), default=0.11)

    # ---------------------------------------------------------------- sheet 1: lameladas and amarração
    def des1(pg):
        fundo_planta(pg, casa, V)
        for p in casa.extra:
            if p["colecao"] == "1.6":
                for pc in p["pecas"]:
                    ret_planta(pg, V, pc, esp=0.25, cor=MAGENTA)
        eixos = []
        for l in lams:
            c = round(l["props"]["comprimento_m"], 2)
            pts = ret_planta(pg, V, l["pecas"][0], esp=0.3, cor=cores[c], preench=None)
            pg.tracejar(pts, 0.9, 60, 0.1, cores[c])
            a, b, *_ = caixa_planta(l["pecas"][0])
            eixos.append(((a + b) / 2, a, b))
        eixos.sort()
        for t in telh:  # ridge
            yc = t["y_cume"]
            pg.linha(V.p(x0, yc)[0], V.p(0, yc)[1], V.p(x1, yc)[0], V.p(0, yc)[1], 0.15, CINZA, (3, 1.5))
        if telh:
            yc = telh[0]["y_cume"]
            pg.texto(V.p(x1, 0)[0] + 3, V.p(0, yc)[1] - 0.8, "Linha de cumeeira", 2.0, CINZA)
        if eixos:
            ytop = V.p(0, y1)[1]
            xa, xb = x0 + t_ext / 2, x1 - t_ext / 2
            ax = [xa] + [c for c, _, _ in eixos] + [xb]
            cota_h(pg, [V.p(x, 0)[0] for x in ax], ytop + 2, ytop + 11, [fmt(b - a) for a, b in zip(ax, ax[1:])], 1.9)
            livres = [x0 + t_ext] + [v for _c, a, b in eixos for v in (a, b)] + [x1 - t_ext]
            vals = []
            for i in range(0, len(livres) - 1, 2):
                vals += [fmt(livres[i + 1] - livres[i]), ""]
            cota_h(pg, [V.p(x, 0)[0] for x in livres], ytop + 2, ytop + 5, vals[:len(livres) - 1], 1.7)
            cota_h(pg, [V.p(x0, 0)[0], V.p(x1, 0)[0]], ytop + 2, ytop + 18, [fmt(x1 - x0)], 2.4)
            pg.texto(V.p(x1, 0)[0] + 3, ytop + 18, "Dimensão da fundação e módulos", 1.8, VERMELHO)
            pg.texto(V.p(x1, 0)[0] + 3, ytop + 11, "Dimensões ao eixo", 1.8, VERMELHO)
            pg.texto(V.p(x1, 0)[0] + 3, ytop + 5, "Dimensões de espaçamento", 1.8, VERMELHO)
        # list
        y = 16.0
        for c in comps:
            n = sum(1 for l in lams if round(l["props"]["comprimento_m"], 2) == c)
            pg.ret(18, y - 0.4, 8, 2.4, esp=0.3, cor=cores[c])
            pg.texto(29, y, f"Lameladas {letra[c]} ({seccao(sec_l)}x{fmt(c * 100, 0)}): {n} un. x {fmt(c)} m", 2.2, cores[c], negrito=True)
            y += 4.2
        tot = sum(l["props"]["comprimento_m"] for l in lams)
        pg.texto(150, 16, f"Total: {len(lams)} lameladas, {fmt(tot, 1)} m, {fmt(tot * a_l * b_l / 1e6, 2)} m³", 2.2, PRETO)
    leg1 = [("linha", CASTANHO, "Dimensão da fundação e módulos"), ("ret", (0.85, 0.8, 0.7), "Módulos"),
            ("linha", MAGENTA, "Amarrações (11x7,5)")] + \
           [("trac", cores[c], f"Lameladas {letra[c]} ({seccao(sec_l)}x{fmt(c * 100, 0)})") for c in comps] + \
           [("linha", CINZA, "Linha de cumeeira"), ("cota", VERMELHO, "Dimensões")]
    D.add("Cobertura - Lameladas horizontais e amarração", e, leg1, des1)

    # ---------------------------------------------------------------- sheet 2: madres, prumos, caleiras
    madres = [p for p in casa.extra if p["colecao"] == "1.9" and p["props"]["tipo"].startswith("Madre")]
    prumos = [p for p in casa.extra if p["colecao"] == "1.9" and p["props"]["tipo"] == "Prumo"]
    calcos = [p for p in casa.extra if p["colecao"] == "1.9" and p["props"]["tipo"].startswith("Calço")]

    def des2(pg):
        fundo_planta(pg, casa, V)
        for l in lams:
            ret_planta(pg, V, l["pecas"][0], esp=0.1, cor=clarear(cores[round(l["props"]["comprimento_m"], 2)], 0.5))
        for t in telh:
            if "canal" not in t or "caleira_de" in t:
                continue  # (strips side by side on one wall share the first one's gutter)
            ya, yb = t["canal"]
            xa_t, xb_t = t.get("caleira_x", (t["x0"], t["x1"]))
            (pa, qa), (pb, qb) = V.p(xa_t, ya), V.p(xb_t, yb)
            pg.ret(pa, qa, pb - pa, qb - qa, esp=0.15, cor=AZUL, preench=AZUL_CLARO)
            fd = t.get("fundo") or []
            if fd:
                zmin = min(z for _x, z in fd)
                ym = V.p(0, (ya + yb) / 2)[1]
                for (xa, za), (xb, zb) in zip(fd, fd[1:]):
                    pxa, pxb = V.p(xa, 0)[0], V.p(xb, 0)[0]
                    if abs(za - zb) > 0.002:  # arrow to the low end
                        hi, lo = (pxa, pxb) if za > zb else (pxb, pxa)
                        pg.linha(hi, ym, lo, ym, 0.25, AZUL)
                        d = 1 if lo > hi else -1
                        pg.poli([(lo, ym), (lo - d * 2.0, ym + 0.9), (lo - d * 2.0, ym - 0.9)], True, esp=0.1, cor=AZUL, preench=AZUL)
                for xp, zp in fd:
                    pg.texto(V.p(xp, 0)[0], ym + (2.2 if t["lado"] == "N" else -3.6), fmt(zp - zmin), 1.8, AZUL, alinh="c")
            for xs_ in t.get("saidas", []):
                cx, cy = V.p(xs_, (ya + yb) / 2)
                pg.poli([(cx + 1.4 * math.cos(a / 8 * math.pi), cy + 1.4 * math.sin(a / 8 * math.pi)) for a in range(16)],
                        True, esp=0.3, cor=AZUL, preench=(1, 1, 1))
        for p in calcos:
            for pc in p["pecas"]:
                pts = ret_planta(pg, V, pc, esp=0.1, cor=CINZA)
                pg.tracejar(pts, 0.6, 45, 0.06, CINZA)
        linhas_m = defaultdict(list)
        for p in madres:
            for pc in p["pecas"]:
                ret_planta(pg, V, pc, esp=0.2, cor=MAGENTA, preench=clarear(MAGENTA, 0.75))
                a, b, c, d, _z0, _z1 = caixa_planta(pc)
                linhas_m[round((c + d) / 2, 2)].append((a, b, p["props"]["seccao"], p["props"]["tipo"]))
        for p in prumos:
            for pc in p["pecas"]:
                ret_planta(pg, V, pc, esp=0.1, cor=MAGENTA, preench=MAGENTA)
        # labels per madre line: section and the prumo heights
        y_ult = -1e9
        for y in sorted(linhas_m):
            if V.p(0, y)[1] - y_ult < 3.0:  # ridge pair: one label
                continue
            y_ult = V.p(0, y)[1]
            segs = linhas_m[y]
            secs = sorted({s for *_r, s, _t in segs})
            hs = sorted({round(p["props"]["comprimento_m"], 2) for p in prumos
                         if abs((caixa_planta(p["pecas"][0])[2] + caixa_planta(p["pecas"][0])[3]) / 2 - y) < 0.08})
            tipo = segs[0][3]
            txt = f"{'Cumeeira' if 'cumeeira' in tipo else 'Madre'} {'/'.join(seccao(s) for s in secs)}"
            txt += f" - prumos {', '.join(fmt(h) for h in hs)}" if hs else " - sobre as lameladas"
            pg.texto(V.p(x1, 0)[0] + 3, V.p(0, y)[1] - 0.7, txt, 1.6, MAGENTA)
        ys_m = sorted(linhas_m)
        if ys_m:
            xl = V.p(x0, 0)[0]
            ys = [y0] + ys_m + [y1]
            cota_v(pg, [V.p(0, y)[1] for y in ys], xl - 2, xl - 8, [fmt(b - a) for a, b in zip(ys, ys[1:])], 1.7)
        tot = defaultdict(lambda: [0, 0.0])
        for p in madres + prumos + calcos:
            k_ = (p["props"]["tipo"], p["props"]["seccao"])
            tot[k_][0] += 1
            tot[k_][1] += p["props"]["comprimento_m"]
        y = 16.0
        for (tp, sec), (n, L) in sorted(tot.items()):
            pg.texto(18, y, f"{tp} {seccao(sec)}: {n} peças, {fmt(L, 1)} m", 2.0, MAGENTA)
            y += 3.4
    leg2 = [("ret", (0.85, 0.8, 0.7), "Módulos"), ("ret", MAGENTA, "Madres (11x7,5) e cumeeiras"),
            ("ret", MAGENTA, "Prumos verticais (altura indicada à direita)"), ("trac", CINZA, "Calços da caleira"),
            ("ret", AZUL, "Caleira oculta: pendente (seta para a saída), cotas do fundo, saídas (círculo)"),
            ("cota", VERMELHO, "Dimensões ao eixo das madres")]
    D.add("Cobertura - Madres (pendentes), prumos e caleiras", e, leg2, des2)

    # ---------------------------------------------------------------- sheet 3: sandwich panels
    paineis = [o for o in casa.objetos if o["colecao"] == "6.2"]
    cumes = [o for o in casa.objetos if o["props"].get("camada") == "Cumeeira"]
    comp_p = sorted({round(o["props"].get("comprimento_m", 0), 2) for o in paineis})
    cor_p = {c: CORES_TIPO[i % len(CORES_TIPO)] for i, c in enumerate(comp_p)}

    def des3(pg):
        fundo_planta(pg, casa, V)
        for o in paineis:
            c = round(o["props"].get("comprimento_m", 0), 2)
            pts = ret_planta(pg, V, o["pecas"][0], esp=0.2, cor=cor_p[c], preench=clarear(cor_p[c], 0.82))
            xs_, ys_ = [p[0] for p in pts], [p[1] for p in pts]
            if max(xs_) - min(xs_) > 3:
                pg.texto((min(xs_) + max(xs_)) / 2, (min(ys_) + max(ys_)) / 2, fmt(c), 1.7, cor_p[c], alinh="c", ang=90)
        for o in cumes:
            for pc in o["pecas"]:
                ret_planta(pg, V, pc, esp=0.4, cor=ESCURO_DC)
        y = 16.0
        tot_a = 0.0
        for c in comp_p:
            sel = [o for o in paineis if round(o["props"].get("comprimento_m", 0), 2) == c]
            a = sum(o["props"].get("area_m2", 0) for o in sel)
            tot_a += a
            pg.ret(18, y - 0.4, 8, 2.4, esp=0.3, cor=cor_p[c], preench=clarear(cor_p[c], 0.82))
            pg.texto(29, y, f"Painel {fmt(c)} m: {len(sel)} un. ({fmt(a, 1)} m²)", 2.2, cor_p[c], negrito=True)
            y += 4.2
        pg.texto(150, 16, f"Total: {len(paineis)} painéis, {fmt(tot_a, 1)} m²; cumeeira {fmt(sum(o['props'].get('comprimento_m', 0) for o in cumes), 1)} m",
                 2.2, PRETO)
        if any("grelha_x" in t for t in telh):
            pg.texto(150, 20.2, "Colocação a partir de nascente (faixa de acerto a poente).", 2.0, ESCURO_DC)
    pn = casa.S["cobertura"].get("painel_oculto", {})
    leg3 = [("ret", CORES_TIPO[i % len(CORES_TIPO)], f"Painel {fmt(c)} m") for i, c in enumerate(comp_p)] + \
           [("linha", ESCURO_DC, "Cumeeira")]
    D.add(f"Cobertura - Painéis ({pn.get('nome', 'painel sandwich')})", e, leg3, des3,
          [f"Largura útil {fmt(pn.get('largura', 1.0))} m; pendente {fmt(casa.G['cobertura'].get('pendente_pct', 0), 1)} %."])

    # ---------------------------------------------------------------- sheet 4: typical sections
    cortes = []
    for c in comps:
        sel = sorted((caixa_planta(l["pecas"][0]) for l in lams if round(l["props"]["comprimento_m"], 2) == c), key=lambda b: b[0])
        bmid = sel[len(sel) // 2]
        cortes.append((c, (bmid[0] + bmid[1]) / 2))
    cortes = cortes[:2]

    def pecas_corte(xs):
        res = []
        for m in casa.modulos:
            a, b, *_ = m.pegada()
            if a - 1e-6 <= xs <= b + 1e-6:
                for pc in m.prismas():
                    res.append(("mod", pc["seccao"], pc))
        for p in casa.extra:
            if p["colecao"] in ("1.6", "1.7", "1.8", "1.9"):
                for pc in p["pecas"]:
                    res.append((p["colecao"], p["props"].get("tipo", ""), pc))
        for o in casa.objetos:
            g = o["colecao"]
            if g.split(".")[0] in ("2", "3", "5", "6"):
                for pc in o["pecas"]:
                    res.append(("c" + g, o["props"].get("camada", ""), pc))
        return res

    nv = casa.G["niveis"]
    pe = casa.cfg.get("niveis", {}).get("pe_direito")

    def des4(pg):
        alt = 128.0
        for i, (c, xs) in enumerate(cortes):
            yb = 287 - alt * (i + 1) + 30
            Vs = Vista(40, yb, 50, y0, 0.0)
            for kind, tp, pc in pecas_corte(xs):
                poly = corte_x(pc, xs)
                if not poly or len(poly) < 2:
                    continue
                pts = [Vs.p(y, z) for y, z in poly]
                if kind == "mod":
                    pg.poli(pts, True, esp=0.12, cor=CASTANHO, preench=(0.96, 0.92, 0.86))
                elif kind == "1.7":
                    pg.poli(pts, True, esp=0.25, cor=cores[c])
                    pg.tracejar(pts, 0.7, 60, 0.08, cores[c])
                elif kind in ("1.6", "1.9", "1.8"):
                    pg.poli(pts, True, esp=0.2, cor=MAGENTA)
                    pg.tracejar(pts, 0.6, 45, 0.06, MAGENTA)
                elif kind.startswith("c6.3"):
                    pg.poli(pts, True, esp=0.25, cor=AZUL if "aleira" in tp else ESCURO_DC, preench=AZUL if "aleira" in tp else ESCURO_DC)
                elif kind.startswith("c6.2"):
                    pg.poli(pts, True, esp=0.1, cor=CINZA, preench=(0.88, 0.88, 0.9))
                else:
                    pg.poli(pts, True, esp=0.06, cor=CINZA, preench=(0.95, 0.95, 0.95))
            # levels
            xr = Vs.p(y1, 0)[0] + 10
            niveis = [(0.0, "0,00")]
            if pe:
                niveis.append((pe, f"{fmt(pe)} teto"))
            for kz, lbl in (("topo_forro_piso0", "amarração"), ("teto_piso0", "lameladas"), ("topo_vigas_teto", "topo lameladas"),
                            ("platibanda", "platibanda")):
                if nv.get(kz) is not None:
                    niveis.append((nv[kz], f"{fmt(nv[kz], 3)} {lbl}"))
            y_txt = -1e9
            for z, lbl in sorted(niveis):
                yy = Vs.p(0, z)[1]
                pg.linha(xr - 3, yy, xr + 1, yy, 0.15, VERMELHO)
                pg.poli([(xr - 1, yy), (xr - 1.8, yy + 1.2), (xr - 0.2, yy + 1.2)], True, esp=0.1, cor=VERMELHO, preench=VERMELHO)
                yt = max(yy - 0.7, y_txt + 2.4)  # close levels: the labels step up
                if yt > yy - 0.7 + 0.1:
                    pg.linha(xr + 1, yy, xr + 1.8, yt + 0.6, 0.08, VERMELHO)
                pg.texto(xr + 2, yt, lbl, 1.7, VERMELHO)
                y_txt = yt
            # madre heights over the lamelada
            for p in prumos:
                a, b, cc, d, z0, z1 = caixa_planta(p["pecas"][0])
                if a - 0.01 <= xs <= b + 0.01:
                    xp, yp = Vs.p((cc + d) / 2, z1)
                    pg.texto(xp, yp + 3.5, fmt(z1 - z0), 1.6, VERMELHO, alinh="c", ang=90)
            pg.texto(40, yb - 12, f"SECÇÃO TIPO PARA AS LAMELADAS {letra[c]} DE {fmt(c)} m  (x = {fmt(xs)})", 2.4, PRETO, negrito=True)
    leg4 = [("ret", CASTANHO, "Módulos"), ("trac", MAGENTA, "Amarrações, madres, prumos e calços (11x7,5)")] + \
           [("trac", cores[c], f"Lameladas {letra[c]}") for c, _ in cortes] + \
           [("ret", CINZA, "Painel sandwich / camadas"), ("ret", AZUL, "Caleira oculta"), ("ret", ESCURO_DC, "Chapéu"),
            ("linha", VERMELHO, "Cotas de nível (m)")]
    D.add("Cobertura - Secções tipo pelas lameladas", 50, leg4, des4,
          ["Alturas dos prumos (vermelho, vertical) acima das lameladas."])
    return D.gravar(caminho)


# ============================================================================ COBERTURA À VISTA
LINHAS_AV = {"cumeeira": (ESCURO_DC, 0.6, None, "Cumeeira"), "rincao": (VERMELHO, 0.45, None, "Rincão"),
             "laro": (AZUL, 0.45, None, "Laró"), "beirado": (CASTANHO, 0.3, None, "Beirado (caleira exterior)"),
             "empena": (CINZA, 0.3, (2.0, 1.0), "Empena (remate lateral)"),
             "encosto": (MAGENTA, 0.45, (1.2, 0.8), "Encosto (empena sobre a cobertura mais baixa)")}
NOME_VERTENTE = {"N": "norte", "S": "sul", "E": "nascente", "O": "poente"}


def vista_avista(casa, pts, larg_mm=290, alt_mm=200):
    """Plan view of an exposed roof (the slopes with their overhangs and the structure) in the drawing area, with
    room for the dimension chains round it and the lists under it."""
    pts = list(pts) + list(casa.contorno)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    e = escala_para(x1 - x0, y1 - y0, larg_mm, alt_mm)
    k = 1000 / e
    return Vista(34 + (296 - (x1 - x0) * k) / 2, 50 + (205 - (y1 - y0) * k) / 2, e, x0, y0), e, (x0, x1, y0, y1)


def _centro(pts):
    """Area centroid of a plan polygon."""
    pts = [tuple(p) for p in pts]
    a = cx = cy = 0.0
    for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
        c = xa * yb - xb * ya
        a += c
        cx += (xa + xb) * c
        cy += (ya + yb) * c
    if abs(a) < 1e-9:
        return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    return cx / (3 * a), cy / (3 * a)


def _corda(pts, u, a_val):
    """The parts inside the plan polygon pts of the line {-u_y x + u_x y = a_val} (u: its unit direction)."""
    ux, uy = u
    ts = []
    pts = [tuple(p) for p in pts]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
        da, db = -uy * xa + ux * ya - a_val, -uy * xb + ux * yb - a_val
        if (da < 0) != (db < 0) and abs(da - db) > 1e-12:
            k = da / (da - db)
            ts.append(ux * (xa + k * (xb - xa)) + uy * (ya + k * (yb - ya)))
    ts.sort()
    bx, by = -uy * a_val, ux * a_val
    return [((bx + ux * ta, by + uy * ta), (bx + ux * tb, by + uy * tb)) for ta, tb in zip(ts[::2], ts[1::2])]


def _unir_linhas(linhas):
    """The roof's lines joined where a run is split between face pieces: [(tipo, p0, p1)] (3D points)."""
    res = [[ln["tipo"], list(ln["p0"]), list(ln["p1"])] for ln in linhas]

    def juntar():
        for i, r in enumerate(res):
            a, b = r[1], r[2]
            L = math.dist(a[:2], b[:2])
            if L < 1e-6:
                continue
            for j in range(i + 1, len(res)):
                q = res[j]
                if q[0] != r[0] or max(abs((p[0] - a[0]) * (b[1] - a[1]) - (p[1] - a[1]) * (b[0] - a[0])) / L
                                       for p in q[1:]) > 1e-3:
                    continue  # another kind, or not on the same line
                for fim_r, fim_q, novo in ((b, q[1], (a, q[2])), (b, q[2], (a, q[1])), (a, q[2], (q[1], b)), (a, q[1], (q[2], b))):
                    if math.dist(fim_r[:2], fim_q[:2]) < 2e-3:  # end to end: one longer run
                        r[1], r[2] = novo
                        del res[j]
                        return True
        return False

    while juntar():
        pass
    return [tuple(r) for r in res]


def _seta(pg, V, c, u, comp=0.9, cor=ESCURO_DC, txt=""):
    """A slope arrow at the plan point c pointing down the slope (u: the uphill unit vector)."""
    (xa, ya), (xb, yb) = V.p(c[0] + u[0] * comp / 2, c[1] + u[1] * comp / 2), V.p(c[0] - u[0] * comp / 2, c[1] - u[1] * comp / 2)
    pg.linha(xa, ya, xb, yb, 0.25, cor)
    L = math.hypot(xb - xa, yb - ya) or 1.0
    dx, dy = (xb - xa) / L, (yb - ya) / L
    pg.poli([(xb, yb), (xb - dx * 2.0 - dy * 0.9, yb - dy * 2.0 + dx * 0.9), (xb - dx * 2.0 + dy * 0.9, yb - dy * 2.0 - dx * 0.9)],
            True, esp=0.1, cor=cor, preench=cor)
    if txt:
        pg.texto((xa + xb) / 2 + dy * 2.2, (ya + yb) / 2 - dx * 2.2 - 0.7, txt, 1.8, cor, alinh="c")


def _rotulo(pg, x, y, txt, tam, cor, ang=0.0):
    """Text on a white box (over the drawing), centred on (x, y)."""
    w = largura(txt, tam)
    if abs(ang) < 1:
        pg.ret(x - w / 2 - 0.6, y - 0.6 * tam, w + 1.2, 1.25 * tam, esp=0.05, cor=(1, 1, 1), preench=(1, 1, 1))
    pg.texto(x, y - 0.35 * tam, txt, tam, cor, alinh="c", ang=ang)


def lista_rodape(pg, itens, n_lin=5, col=84.0):
    """Lines (text, colour[, bold]) in up to four columns in the band under the drawing."""
    for i, it in enumerate(itens[:4 * n_lin]):
        c, l = divmod(i, n_lin)
        pg.texto(16 + c * col, 33 - l * 4.4, it[0], 1.9, it[1], negrito=len(it) > 2 and it[2])


def doc_cobertura_avista(casa, info, caminho):
    """The exposed sandwich-panel roof (casa_planta "a_vista": 2 águas the rule, 4 águas an option, várias águas on
    L / T / U — user 2026-10-21) in five sheets: the slopes and their lines, the ceiling beams / glulams / headers,
    the purlins / hips / valleys / prumos, the panels and flashings, sections across the ridges."""
    C = casa.G["cobertura"]
    D = Documento(info, f"{info['obra']} - Cobertura")
    faces = C["faces"]
    linhas = _unir_linhas(C["linhas"])
    # one slope = one plane (two rectangles on one plane are one slope, named after the first: R1 N …), as the
    # purlins and the panels of the model (telhado_estrutura, camadas)
    por_plano = defaultdict(list)
    for f in faces:
        por_plano[tuple(round(v, 6) for v in f["plano"])].append(f)
    aguas = {(min(f["ret"] for f in fs), fs[0]["nome"]): fs for fs in por_plano.values()}

    def faces_agua(k_r, nome_a):
        return next((fs for fs in por_plano.values() if any(f["ret"] == k_r and f["nome"] == nome_a for f in fs)), [])
    V, e, (x0, x1, y0, y1) = vista_avista(casa, [tuple(p) for f in faces for p in f["pts"]])
    pct = C.get("pendente_pct", 0.0)
    graus = math.degrees(math.atan(pct / 100))
    vertentes = sorted({f["nome"] for f in faces})
    cor_v = {n: clarear(CORES_TIPO[i % len(CORES_TIPO)], 0.84) for i, n in enumerate(vertentes)}
    cxs, cys = [p[0] for p in casa.contorno], [p[1] for p in casa.contorno]
    sx0, sx1, sy0, sy1 = min(cxs), max(cxs), min(cys), max(cys)
    nota_inc = f"Inclinação {fmt(pct, 1)} % ({fmt(graus, 1)}°), painel sandwich (mínimo 15 % à vista)."

    def modulos_traco(pg, cor=CINZA_CLARO, preench=None):
        for m in casa.modulos:
            a, b, c, d = m.pegada()
            (pa, pc), (pb, pd) = V.p(a, c), V.p(b, d)
            pg.ret(pa, pc, pb - pa, pd - pc, esp=0.1, cor=cor, preench=preench if m.exterior else None)
        if casa.contorno:
            pg.poli([V.p(*p) for p in casa.contorno], True, esp=0.25, cor=CASTANHO, tracejado=(1.5, 0.8))

    def cotas_gerais(pg):
        """The roof (with its overhangs) and the structure, bottom and left."""
        yb, xl = V.p(0, y0)[1], V.p(x0, 0)[0]
        xs = sorted({round(v, 4) for v in (x0, sx0, sx1, x1)})
        cota_h(pg, [V.p(x, 0)[0] for x in xs], yb - 1.5, yb - 6, [fmt(b - a) for a, b in zip(xs, xs[1:])], 1.8)
        cota_h(pg, [V.p(x0, 0)[0], V.p(x1, 0)[0]], yb - 1.5, yb - 12, [fmt(x1 - x0)], 2.2)
        ys = sorted({round(v, 4) for v in (y0, sy0, sy1, y1)})
        cota_v(pg, [V.p(0, y)[1] for y in ys], xl - 1.5, xl - 6, [fmt(b - a) for a, b in zip(ys, ys[1:])], 1.8)
        cota_v(pg, [V.p(0, y0)[1], V.p(0, y1)[1]], xl - 1.5, xl - 12, [fmt(y1 - y0)], 2.2)

    # ---------------------------------------------------------------- sheet 1: slopes and lines
    def des1(pg):
        for f in faces:
            pg.poli([V.p(*p) for p in f["pts"]], True, esp=0.05, cor=cor_v[f["nome"]], preench=cor_v[f["nome"]])
        modulos_traco(pg)
        tot = defaultdict(float)
        for tipo, p0, p1 in linhas:
            cor, esp, tr, _n = LINHAS_AV[tipo]
            (xa, ya), (xb, yb) = V.p(p0[0], p0[1]), V.p(p1[0], p1[1])
            pg.linha(xa, ya, xb, yb, esp, cor, tr)
            L = math.hypot(math.dist(p0[:2], p1[:2]), p1[2] - p0[2])
            tot[tipo] += L
            if tipo in ("cumeeira", "rincao", "laro", "encosto") and L > 0.8:
                ang = math.degrees(math.atan2(yb - ya, xb - xa))
                ang = ang - 180 if ang > 90 else (ang + 180 if ang < -90 else ang)
                txt = fmt(L)
                if tipo == "cumeeira":
                    txt = f"Cumeeira {fmt(L)} (+{fmt(p0[2], 2)})"
                nx_, ny_ = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
                pg.texto((xa + xb) / 2 + nx_ * 1.6, (ya + yb) / 2 + ny_ * 1.6 - 0.3, txt, 1.7, cor, alinh="c", ang=ang)
        for f in faces:
            if f.get("area_planta", 0) < 2.0:
                continue
            _seta(pg, V, _centro(f["pts"]), f["subida"], 1.2, ESCURO_DC, f"{fmt(pct, 0)} %")
        cotas_gerais(pg)
        itens = [(nota_inc, PRETO, True),
                 (f"Beirado {fmt(C.get('beirado', 0.25))} m; empena {fmt(C.get('empena', 0.12))} m (além da face da estrutura)", ESCURO_DC),
                 (f"Cota do beirado (topo das madres na linha da parede) +{fmt(C.get('z_beirado', 0), 3)}", ESCURO_DC),
                 (f"Cota da cumeeira +{fmt(C.get('cumeeira_z', 0), 3)}", ESCURO_DC)]
        n_lin = {t: sum(1 for l in linhas if l[0] == t) for t in tot}
        for t in ("cumeeira", "rincao", "laro", "encosto", "beirado", "empena"):
            if tot.get(t):
                itens.append((f"{LINHAS_AV[t][3].split(' (')[0]}: {n_lin[t]} troço{'s' if n_lin[t] > 1 else ''}, "
                              f"{fmt(tot[t], 1)} m (comprimento real)", LINHAS_AV[t][0]))
        area_p = sum(f.get("area_planta", 0) for f in faces)
        itens.append((f"Área da cobertura: {fmt(area_p, 1)} m² em planta, {fmt(area_p / math.cos(math.radians(graus)), 1)} m² inclinada",
                      PRETO))
        lista_rodape(pg, itens)
    leg1 = [("ret", CORES_TIPO[i % len(CORES_TIPO)], f"Vertente {NOME_VERTENTE.get(n, n)} (desce para {NOME_VERTENTE.get(n, n)})")
            for i, n in enumerate(vertentes)] + \
           [("linha", LINHAS_AV[t][0], LINHAS_AV[t][3]) for t in ("cumeeira", "rincao", "laro", "encosto", "beirado", "empena")
            if any(l[0] == t for l in linhas)] + \
           [("linha", CASTANHO, "Face exterior da estrutura (módulos)"), ("linha", ESCURO_DC, "Seta: desce a vertente"),
            ("cota", VERMELHO, "Dimensões (m)")]
    D.add("Cobertura - Águas, cumeeiras, rincões e larós", e, leg1, des1,
          ["Comprimentos de rincões e larós em verdadeira grandeza (inclinados); cotas a partir do 0,00 (pavimento acabado)."])

    # ---------------------------------------------------------------- sheet 2: ceiling beams, glulams, headers
    p17 = [p for p in casa.extra if p["colecao"] == "1.7"]
    p16 = [p for p in casa.extra if p["colecao"] == "1.6"]
    correntes = [p for p in p17 if p["props"]["tipo"] in ("Viga de apoio ao teto", "Lamelada")]
    comps = sorted({round(p["props"]["comprimento_m"], 2) for p in correntes})
    letra = {c: chr(65 + i) if i < 26 else f"A{i - 25}" for i, c in enumerate(comps)}
    cor_c = {c: CORES_TIPO[i % len(CORES_TIPO)] for i, c in enumerate(comps)}

    def des2(pg):
        for _t, p0, p1 in linhas:  # the roof's outline and lines, faint
            pg.linha(*V.p(p0[0], p0[1]), *V.p(p1[0], p1[1]), 0.12, CINZA_CLARO)
        modulos_traco(pg, CINZA_CLARO, (0.97, 0.95, 0.92))
        for p in p16:
            for pc in p["pecas"]:
                ret_planta(pg, V, pc, esp=0.2, cor=MAGENTA)
        zonas = defaultdict(list)
        for p in p17:
            tp = p["props"]["tipo"]
            for pc in p["pecas"]:
                if tp in ("Viga de apoio ao teto", "Lamelada"):
                    c = round(p["props"]["comprimento_m"], 2)
                    pts = ret_planta(pg, V, pc, esp=0.25, cor=cor_c[c], preench=clarear(cor_c[c], 0.7))
                    if tp == "Lamelada":
                        pg.tracejar(pts, 0.9, 60, 0.1, cor_c[c])
                    a, b, cc, d, *_ = caixa_planta(pc)
                    vert = (d - cc) > (b - a)
                    pg.texto(*V.p((a + b) / 2, (cc + d) / 2), letra[c], 1.5, cor_c[c], alinh="c", ang=90 if vert else 0)
                    zonas[p["nome"].split()[-1].split(".")[0]].append((p, (a, b, cc, d)))
                elif tp.startswith("Viga de bordadura"):
                    pts = ret_planta(pg, V, pc, esp=0.35, cor=hexcor("#E07B00"), preench=clarear(hexcor("#E07B00"), 0.6))
                    pg.tracejar(pts, 0.7, 60, 0.1, hexcor("#E07B00"))
                else:  # edge beams on the walls
                    ret_planta(pg, V, pc, esp=0.2, cor=CASTANHO, preench=clarear(CASTANHO, 0.6))
        for z, sel in sorted(zonas.items()):
            vert = (sel[0][1][3] - sel[0][1][2]) > (sel[0][1][1] - sel[0][1][0])
            pos = sorted(((a + b) / 2 if vert else (c + d) / 2) for _p, (a, b, c, d) in sel)
            passo = max((q - p for p, q in zip(pos, pos[1:])), default=0.0)
            xs_ = [v for _p, bb in sel for v in bb[:2]]
            ys_ = [v for _p, bb in sel for v in bb[2:]]
            sec = sel[0][0]["props"]["seccao"]
            vao = sel[0][0]["props"].get("vao_m", 0.0)
            _rotulo(pg, *V.p((min(xs_) + max(xs_)) / 2, (min(ys_) + max(ys_)) / 2),
                    f"{z}: {len(sel)} x {seccao(sec)} a {fmt(passo)} (vão {fmt(vao)})", 1.8, PRETO)
        cotas_gerais(pg)
        itens = []
        for c in comps:
            sel = [p for p in correntes if round(p["props"]["comprimento_m"], 2) == c]
            itens.append((f"{letra[c]}: {len(sel)} x {sel[0]['props']['tipo'].lower()} {seccao(sel[0]['props']['seccao'])} x {fmt(c)} m",
                          cor_c[c], True))
        outros = defaultdict(lambda: [0, 0.0])
        for p in p17 + p16:
            tp = p["props"]["tipo"]
            if tp in ("Viga de apoio ao teto", "Lamelada"):
                continue
            k_ = (tp.split(" (")[0], p["props"]["seccao"])
            outros[k_][0] += 1
            outros[k_][1] += p["props"]["comprimento_m"]
        for (tp, sec), (n, L) in sorted(outros.items()):
            itens.append((f"{tp} {seccao(sec)}: {n} peça{'s' if n != 1 else ''}, {fmt(L, 1)} m", ESCURO_DC))
        lista_rodape(pg, itens)
    leg2 = [("ret", cor_c[c], f"{letra[c]}: vigas de {fmt(c)} m") for c in comps[:8]] + \
           [("trac", hexcor("#E07B00"), "Viga de bordadura (lamelada): apoio das vigas onde a ala abre / sob a empena"),
            ("ret", CASTANHO, "Viga de bordo sobre a parede (empena / testeira)"), ("linha", MAGENTA, "Afinação e amarração"),
            ("ret", (0.85, 0.8, 0.7), "Módulos"), ("cota", VERMELHO, "Dimensões (m)")]
    D.add("Cobertura - Vigas de apoio ao teto, lameladas e vigas de bordo", e, leg2, des2,
          ["Z1, Z2, ...: zonas da cobertura (corpo principal e alas); vigas a descer a vertente, apoiadas nas paredes.",
           "22x7,5 até 8 m de vão livre; acima, lameladas (método DiscoverCasa §6)."])

    # ---------------------------------------------------------------- sheet 3: purlins, hips, valleys, prumos
    p19 = [p for p in casa.extra if p["colecao"] == "1.9"]
    madres = [p for p in p19 if p["props"]["tipo"] == "Viga de apoio à cobertura"]
    vincos = [p for p in p19 if p["props"]["tipo"].startswith(("Rincão", "Laró"))]
    prumos = [p for p in p19 if p["props"]["tipo"] == "Prumo"]
    calcos = [p for p in p19 if p["props"]["tipo"] == "Calço"]
    subida = {(f["ret"], f["nome"]): f["subida"] for f in faces}

    def des3(pg):
        for f in faces:
            pg.poli([V.p(*p) for p in f["pts"]], True, esp=0.05, cor=clarear(cor_v[f["nome"]], 0.5),
                    preench=clarear(cor_v[f["nome"]], 0.5))
        modulos_traco(pg)
        for p in p17:
            for pc in p["pecas"]:
                ret_planta(pg, V, pc, esp=0.08, cor=CINZA)
        por_agua = defaultdict(set)
        for p in madres:
            for pc in p["pecas"]:
                pg.poli([V.p(*q) for q in contorno_planta(pc)], True, esp=0.15, cor=MAGENTA, preench=clarear(MAGENTA, 0.6))
            nm = p["nome"].split()
            agua, linha_ = nm[-2], nm[-1].split(".")[0]
            por_agua[agua].add(linha_)
        for p in vincos:
            cor = VERMELHO if p["props"]["tipo"].startswith("Rincão") else AZUL
            for pc in p["pecas"]:
                pg.poli([V.p(*q) for q in contorno_planta(pc)], True, esp=0.25, cor=cor, preench=clarear(cor, 0.5))
        for p in prumos:
            for pc in p["pecas"]:
                ret_planta(pg, V, pc, esp=0.1, cor=ESCURO_DC, preench=ESCURO_DC)
        for p in calcos:
            for pc in p["pecas"]:
                ret_planta(pg, V, pc, esp=0.1, cor=CINZA, preench=CINZA)
        # one label per slope: its purlin lines and their spacing up the slope
        for agua, lns in sorted(por_agua.items()):
            k_r, nome_a = int(agua[1:-1]) - 1, agua[-1]
            fs = faces_agua(k_r, nome_a)
            if not fs:
                continue
            u = subida[(k_r, nome_a)]
            ds = sorted({round(sum(u[0] * q[0] + u[1] * q[1] for q in contorno_planta(pc)) / len(contorno_planta(pc)), 2)
                         for p in madres if p["nome"].split()[-2] == agua for pc in p["pecas"]})
            passo = max((b - a for a, b in zip(ds, ds[1:]) if b - a > 0.05), default=0.0)
            maior = max(fs, key=lambda f: f.get("area_planta", 0))
            cx, cy = _centro(maior["pts"])
            _rotulo(pg, *V.p(cx, cy), f"{agua}: {len(lns)} madres{f' a {fmt(passo)}' if passo else ''}", 1.7, PRETO)
        cotas_gerais(pg)
        tot = defaultdict(lambda: [0, 0.0])
        for p in madres + vincos + prumos + calcos:
            k_ = (p["props"]["tipo"].split(" (")[0], p["props"]["seccao"])
            tot[k_][0] += 1
            tot[k_][1] += p["props"]["comprimento_m"]
        itens = [(f"{tp} {seccao(sec)}: {n} peça{'s' if n != 1 else ''}, {fmt(L, 1)} m", MAGENTA if tp.startswith("Viga") else ESCURO_DC)
                 for (tp, sec), (n, L) in sorted(tot.items())]
        if prumos:
            hs = [p["props"]["comprimento_m"] for p in prumos]
            itens.append((f"Prumos de {fmt(min(hs))} a {fmt(max(hs))} m (sobre as vigas de apoio ao teto)", ESCURO_DC))
        peca_max = max((p["props"]["comprimento_m"] for p in madres), default=0)
        itens.append((f"Madres em peças até {fmt(peca_max)} m, emendadas sobre as vigas", ESCURO_DC))
        lista_rodape(pg, itens)
    leg3 = [("ret", MAGENTA, "Vigas de apoio à cobertura (madres 11x7,5 deitadas, na inclinação)"),
            ("ret", VERMELHO, "Rincão (11x7,5 ao alto)"), ("ret", AZUL, "Laró (11x7,5 ao alto)"),
            ("ret", ESCURO_DC, "Prumos"), ("ret", CINZA, "Calços (apoio < 3 cm)"),
            ("linha", CINZA, "Vigas de apoio ao teto (folha 2)"), ("linha", CASTANHO, "Face exterior da estrutura"),
            ("cota", VERMELHO, "Dimensões (m)")]
    D.add("Cobertura - Vigas de apoio à cobertura, rincões, larós e prumos", e, leg3, des3,
          ["R1 N = retângulo 1 da cobertura, vertente que desce para norte (folha 1).", nota_inc])

    # ---------------------------------------------------------------- sheet 4: panels and flashings
    paineis = [o for o in casa.objetos if o["colecao"] == "6.2"]
    remates = [o for o in casa.objetos if o["colecao"] == "6.3"]
    pn = casa.S["cobertura"].get("painel", {})
    lg = pn.get("largura", 1.0)

    def des4(pg):
        for f in faces:
            pg.poli([V.p(*p) for p in f["pts"]], True, esp=0.05, cor=cor_v[f["nome"]], preench=cor_v[f["nome"]])
        modulos_traco(pg, CINZA_CLARO)
        for (k_r, nome_a), fs in sorted(aguas.items()):
            ex, ey = fs[0]["subida"]
            acr = [(-ey * x + ex * y) for f in fs for x, y in f["pts"]]
            a0, a1 = min(acr), max(acr)
            n_p = max(1, math.ceil((a1 - a0) / lg - 1e-6))
            for i in range(1, n_p):
                for f in fs:
                    for q0, q1 in _corda(f["pts"], (ex, ey), a0 + i * lg):
                        (xa, ya), (xb, yb) = V.p(*q0), V.p(*q1)
                        pg.linha(xa, ya, xb, yb, 0.1, ESCURO_DC)
        for tipo, p0, p1 in linhas:
            cor, esp, tr, _n = LINHAS_AV[tipo]
            if tipo == "beirado":
                cor, esp = AZUL, 0.6
            (xa, ya), (xb, yb) = V.p(p0[0], p0[1]), V.p(p1[0], p1[1])
            pg.linha(xa, ya, xb, yb, esp, cor, tr)
        for o in remates:
            if o["props"].get("camada") != "Tubo de queda":
                continue
            a, b, c, d, *_ = caixa_planta(o["pecas"][0])
            cx, cy = V.p((a + b) / 2, (c + d) / 2)
            pg.poli([(cx + 1.3 * math.cos(t / 8 * math.pi), cy + 1.3 * math.sin(t / 8 * math.pi)) for t in range(16)],
                    True, esp=0.3, cor=AZUL, preench=(1, 1, 1))
        for o in paineis:
            nome_a = o["props"].get("vertente")
            k_r = int(o["nome"].split()[-1][1:-1]) - 1
            fs = aguas.get((k_r, nome_a)) or []
            if not fs:
                continue
            maior = max(fs, key=lambda f: f.get("area_planta", 0))
            _rotulo(pg, *V.p(*_centro(maior["pts"])), f"R{k_r + 1}{nome_a}: {o['props'].get('pecas')} x {fmt(o['props'].get('comprimento_m', 0))}",
                    1.8, PRETO)
        cotas_gerais(pg)
        itens = []
        tot_a, tot_n = 0.0, 0
        for o in paineis:
            itens.append((f"{o['nome'].split()[-1]}: {o['props'].get('pecas')} painéis x {fmt(o['props'].get('comprimento_m', 0))} m "
                          f"({fmt(o['props'].get('area_m2', 0), 1)} m²)", ESCURO_DC))
            tot_a += o["props"].get("area_m2", 0)
            tot_n += o["props"].get("pecas", 0)
        itens.insert(0, (f"Painéis: {tot_n} un., {fmt(tot_a, 1)} m² (largura útil {fmt(lg)} m)", PRETO, True))
        rem = defaultdict(lambda: [0, 0.0])
        for o in remates:
            rem[o["props"].get("camada", "")][0] += 1
            rem[o["props"].get("camada", "")][1] += o["props"].get("comprimento_m", 0)
        for nm, (n, L) in sorted(rem.items()):
            itens.append((f"{nm}: {fmt(L, 1)} m" if nm != "Tubo de queda" else f"Tubos de queda: {n} un., {fmt(L, 1)} m", AZUL
                          if "aleira" in nm or "Tubo" in nm else ESCURO_DC))
        lista_rodape(pg, itens)
    leg4 = [("ret", CORES_TIPO[i % len(CORES_TIPO)], f"Vertente {NOME_VERTENTE.get(n, n)}") for i, n in enumerate(vertentes)] + \
           [("linha", ESCURO_DC, f"Juntas dos painéis (largura útil {fmt(lg)} m, a descer a vertente)"),
            ("linha", AZUL, "Caleira exterior (beirado) e caleira de laró"), ("linha", ESCURO_DC, "Cumeeira / remate de rincão"),
            ("linha", CINZA, "Remate lateral (empena)"), ("linha", MAGENTA, "Remate de encosto"),
            ("texto", AZUL, "Círculo: tubo de queda (2 por caleira, a 0,30 das pontas)")]
    D.add(f"Cobertura - Painéis ({pn.get('nome', 'painel sandwich')}) e remates", e, leg4, des4,
          ["R1 N: 12 x 5,40 = número de painéis x comprimento do maior; os painéis cortam-se em obra nos rincões e larós.",
           nota_inc])

    # ---------------------------------------------------------------- sheet 5: sections across the ridges
    cortes = []
    for k_r, r in enumerate(C["retangulos"][:2]):
        eixo_c = "x" if r["eixo"] == "x" else "y"  # the ridge along x: the section is a plane x = const
        px0, px1, py0, py1 = r["proprio"]
        meio = (px0 + px1) / 2 if eixo_c == "x" else (py0 + py1) / 2
        z_ = f"Z{k_r + 1}."
        cand = []
        for p in p17:
            if p["props"]["tipo"] in ("Viga de apoio ao teto", "Lamelada") and f" {z_}" in f" {p['nome'].split()[-1]}":
                a, b, c, d, *_ = caixa_planta(p["pecas"][0])
                cand.append((abs(((a + b) / 2 if eixo_c == "x" else (c + d) / 2) - meio), (a + b) / 2 if eixo_c == "x" else (c + d) / 2,
                             p["nome"]))
        if cand:
            _d, s, nome_v = min(cand)
            cortes.append((k_r, eixo_c, s, nome_v))
    nv = casa.G["niveis"]
    pe = casa.cfg.get("niveis", {}).get("pe_direito")
    janelas = []  # each section's window across (w0, w1) and one scale for all
    for k_r, eixo_c, s, nome_v in cortes:
        r = C["retangulos"][k_r]
        w0, w1 = (r["y0"], r["y1"]) if eixo_c == "x" else (r["x0"], r["x1"])
        janelas.append((w0 - C.get("beirado", 0.25) - 0.4, w1 + C.get("beirado", 0.25) + 0.4))
    es = max((escala_para(w1 - w0, 5.0, 280, 110, (50, 75, 100)) for w0, w1 in janelas), default=50)

    def recortar(poly, lo, hi):
        """A section polygon (across, z) clipped to lo <= across <= hi."""
        for lim, sg in ((lo, 1), (hi, -1)):
            out_ = []
            for i, p in enumerate(poly):
                q = poly[(i + 1) % len(poly)]
                dp, dq = sg * (p[0] - lim), sg * (q[0] - lim)
                if dp >= 0:
                    out_.append(p)
                if (dp >= 0) != (dq >= 0):
                    k = dp / (dp - dq)
                    out_.append((p[0] + k * (q[0] - p[0]), p[1] + k * (q[1] - p[1])))
            poly = out_
            if len(poly) < 2:
                return []
        return poly

    def pecas_corte(s, eixo_c):
        res = []
        for m in casa.modulos:
            a, b, c, d = m.pegada()
            lo, hi = (a, b) if eixo_c == "x" else (c, d)
            if lo - 1e-6 <= s <= hi + 1e-6:
                for pc in m.prismas():
                    res.append(("mod", pc["seccao"], pc))
        for p in casa.extra:
            if p["colecao"] in ("1.6", "1.7", "1.8", "1.9"):
                for pc in p["pecas"]:
                    res.append((p["colecao"], p["props"].get("tipo", ""), pc))
        for o in casa.objetos:
            g = o["colecao"]
            if g.split(".")[0] in ("2", "3", "4", "5", "6"):
                for pc in o["pecas"]:
                    res.append(("c" + g, o["props"].get("camada", ""), pc))
        return res

    def des5(pg):
        alt = 128.0
        for i, (k_r, eixo_c, s, nome_v) in enumerate(cortes):
            w0, w1 = janelas[i]
            yb = 287 - alt * (i + 1) + 30
            Vs = Vista(40 + (290 - (w1 - w0) * 1000 / es) / 2, yb, es, w0, 0.0)
            for kind, tp, pc in pecas_corte(s, eixo_c):
                poly = corte(pc, s, eixo_c)
                if not poly or len(poly) < 2:
                    continue
                poly = recortar(poly, w0, w1) if len(poly) > 2 else poly
                if len(poly) < 2 or any(q[0] < w0 - 1e-6 or q[0] > w1 + 1e-6 for q in poly):
                    continue
                pts = [Vs.p(a, z) for a, z in poly]
                if kind == "mod":
                    pg.poli(pts, True, esp=0.12, cor=CASTANHO, preench=(0.96, 0.92, 0.86))
                elif kind == "1.7":
                    cor = hexcor("#E07B00") if tp.startswith("Viga de bordadura") else AZUL
                    pg.poli(pts, True, esp=0.25, cor=cor, preench=clarear(cor, 0.75))
                elif kind in ("1.6", "1.9", "1.8"):
                    pg.poli(pts, True, esp=0.2, cor=MAGENTA)
                    pg.tracejar(pts, 0.6, 45, 0.06, MAGENTA)
                elif kind.startswith("c6.3"):
                    pg.poli(pts, True, esp=0.25, cor=AZUL if "aleira" in tp or "Tubo" in tp else ESCURO_DC,
                            preench=AZUL if "aleira" in tp or "Tubo" in tp else ESCURO_DC)
                elif kind.startswith("c6.2"):
                    pg.poli(pts, True, esp=0.1, cor=CINZA, preench=(0.88, 0.88, 0.9))
                else:
                    pg.poli(pts, True, esp=0.06, cor=CINZA, preench=(0.95, 0.95, 0.95))
            # levels
            xr = Vs.p(w1, 0)[0] + 6
            niveis = [(0.0, "0,00")]
            if pe:
                niveis.append((pe, f"{fmt(pe)} teto"))
            for kz, lbl in (("teto_piso0", "vigas de apoio ao teto"), ("topo_vigas_teto", "topo das vigas")):
                if nv.get(kz) is not None:
                    niveis.append((nv[kz], f"{fmt(nv[kz], 3)} {lbl}"))
            niveis.append((C["z_beirado"], f"{fmt(C['z_beirado'], 3)} beirado (madres)"))
            z_c = max((f["z0"] + f["gx"] * x + f["gy"] * y for f in faces if f["ret"] == k_r for x, y in f["pts"]),
                      default=C["cumeeira_z"])  # this roof's own ridge (a wing's is lower)
            niveis.append((z_c, f"{fmt(z_c, 3)} cumeeira (madres)"))
            y_txt = -1e9
            for z, lbl in sorted(niveis):
                yy = Vs.p(0, z)[1]
                pg.linha(xr - 3, yy, xr + 1, yy, 0.15, VERMELHO)
                pg.poli([(xr - 1, yy), (xr - 1.8, yy + 1.2), (xr - 0.2, yy + 1.2)], True, esp=0.1, cor=VERMELHO, preench=VERMELHO)
                yt = max(yy - 0.7, y_txt + 2.4)
                if yt > yy - 0.7 + 0.1:
                    pg.linha(xr + 1, yy, xr + 1.8, yt + 0.6, 0.08, VERMELHO)
                pg.texto(xr + 2, yt, lbl, 1.7, VERMELHO)
                y_txt = yt
            for p in prumos:
                a, b, cc, d, z0, z1 = caixa_planta(p["pecas"][0])
                lo, hi, mid = (a, b, (cc + d) / 2) if eixo_c == "x" else (cc, d, (a + b) / 2)
                if lo - 0.01 <= s <= hi + 0.01:
                    xp, yp = Vs.p(mid, z1)
                    pg.texto(xp, yp + 3.5, fmt(z1 - z0), 1.5, VERMELHO, alinh="c", ang=90)
            plano = "x" if eixo_c == "x" else "y"
            pg.texto(40, yb - 12, f"SECÇÃO R{k_r + 1} PERPENDICULAR À CUMEEIRA, PELA {nome_v.upper()} ({plano} = {fmt(s)})",
                     2.4, PRETO, negrito=True)
    leg5 = [("ret", CASTANHO, "Módulos"), ("ret", AZUL, "Vigas de apoio ao teto / lameladas"),
            ("ret", hexcor("#E07B00"), "Viga de bordadura (lamelada)"),
            ("trac", MAGENTA, "Afinação, amarração, madres, rincões, larós, prumos"),
            ("ret", CINZA, "Painel sandwich / camadas"), ("ret", AZUL, "Caleira, tubo de queda"), ("ret", ESCURO_DC, "Remates"),
            ("linha", VERMELHO, "Cotas de nível (m)")]
    if cortes:
        D.add("Cobertura - Secções perpendiculares à cumeeira", es, leg5, des5,
              ["Alturas dos prumos (vermelho, vertical) acima das vigas de apoio ao teto.", nota_inc])
    return D.gravar(caminho)


# ============================================================================ LISTAGEM DE MATERIAL
CAPITULOS = {"1": "Estrutura de madeira", "2": "Paredes - camadas exteriores", "3": "Paredes - isolamento e camadas interiores",
             "4": "Pavimentos", "5": "Tetos", "6": "Cobertura", "7": "Caixilharia e remates", "8": "Pérgola - cobertura"}


def linhas_material(casa):
    """[(chapter, description, product, pieces, length, area, volume, purchase qty, purchase unit)]"""
    out = []
    madeira = defaultdict(lambda: [0, 0.0, 0.0])
    for g, sec, L, vol, _tp in casa.pecas_madeira():
        t = madeira[(g, sec)]
        t[0] += 1
        t[1] += L
        t[2] += vol
    for (g, sec), (n, L, vol) in sorted(madeira.items(), key=lambda kv: (kv[0][0], ordem_secoes(kv[0][1]))):
        cap = "8" if "érgola" in g else "1"
        out.append((cap if cap == "1" else "8m", g, f"Madeira {seccao(sec)}", n, L, 0.0, vol, "", ""))
    ferr = defaultdict(int)
    for g, tp, prod, n in casa.ferragens():
        ferr[(g, tp, prod)] += n
    for (g, tp, prod), n in sorted(ferr.items()):
        out.append(("8" if "érgola" in g else "1", tp, prod, n, 0.0, 0.0, 0.0, n, "un"))
    for (col, cam), t in sorted(casa.camadas_totais().items(), key=lambda kv: [int(x) if x.isdigit() else 0 for x in kv[0][0].split(".")]):
        cap = col.split(".")[0]
        if cap == "9":
            continue
        desc = cam if cam not in ("Caixilharia",) else t["colecao"].split(" ", 1)[-1]
        out.append((cap, desc, t["produto"], t["n"], t["comp"], t["area"], t["vol"], t["compra"], t["un"] if t["compra"] != "" else ""))
    return out


def doc_listagem(casa, info, caminho_pdf, caminho_csv):
    linhas = linhas_material(casa)
    itens = (casa.S.get("caixilharia") or {}).get("itens", [])
    # CSV (for budgeting)
    with open(caminho_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["capitulo", "descricao", "produto", "pecas", "comprimento_m", "area_m2", "volume_m3", "quantidade_compra", "unidade_compra"])
        for cap, d, p, n, L, A, Vv, q, u in linhas:
            w.writerow([CAPITULOS.get(cap[0], cap) + (" (madeira)" if cap == "8m" else ""), d, p, n, round(L, 2) or "", round(A, 2) or "",
                        round(Vv, 3) or "", q, u])
        for it in itens:
            w.writerow([CAPITULOS["7"] + " (itens)", f"{it.get('modulo') or it.get('parede', '')} {it.get('divisao', '')} - {it.get('descricao_curta', '')}", it.get("descricao", ""),
                        1, "", round(it["largura"] * it["altura"], 3), "", 1, f"{fmt(it['largura'])}x{fmt(it['altura'])}"
                        + (" + estore" if it.get("estore") else "")])
    # PDF (A4 portrait)
    pdf = PDF(titulo=f"{info['obra']} - Listagem de material")
    cols = [("Descrição", 46, "e"), ("Produto / secção", 56, "e"), ("Peças", 12, "d"), ("Comp. m", 15, "d"),
            ("Área m²", 15, "d"), ("Vol. m³", 14, "d"), ("Compra", 32, "d")]
    tab = []
    for cap in ("1", "2", "3", "4", "5", "6", "7", "8"):
        sel = [l for l in linhas if l[0] == cap or (cap == "8" and l[0] == "8m")]
        if cap == "7" and itens:
            tab.append(f"# 7 {CAPITULOS['7']}")
            for it in itens:
                tab.append([f"{it.get('modulo') or it.get('parede', '')} {it.get('divisao', '')}", it.get("descricao_curta", ""), "1", "",
                            fmt(it["largura"] * it["altura"], 2), "", f"{fmt(it['largura'])}x{fmt(it['altura'])}" + (" + estore" if it.get("estore") else "")])
            tab.append(["Total caixilharia", "", str(len(itens)), "", fmt(sum(i["largura"] * i["altura"] for i in itens), 2), "", ""])
            sel = [l for l in sel if not l[1].startswith(("Aros", "Vidros", "Estores", "Portas"))]
            if not sel:
                continue
        elif not sel:
            continue
        else:
            tab.append(f"# {cap} {CAPITULOS[cap]}")
        for _c, d, p, n, L, A, Vv, q, u in sel:
            tab.append([d, p, str(n) if n else "", fmt(L, 1) if L else "", fmt(A, 1) if A else "", fmt(Vv, 3) if Vv else "",
                        f"{q} {u}" if q != "" else ""])
        if cap in ("1",):
            sel = [l for l in sel if l[2].startswith("Madeira")]  # not the hardware
            tab.append(["Total madeira", "", str(sum(l[3] for l in sel)), fmt(sum(l[4] for l in sel), 1), "",
                        fmt(sum(l[6] for l in sel), 2), ""])
    corte = casa.lista_corte(False)
    tab.append("# Anexo - lista de corte da madeira (módulos, amarração, lameladas, madres, prumos, calços, pérgola)")
    for sec in sorted(corte, key=ordem_secoes):
        for cm, q in sorted(corte[sec].items(), reverse=True):
            tab.append([f"Madeira {seccao(sec)}", f"{fmt(cm / 100)} m", str(q), fmt(q * cm / 100, 1), "", "", ""])
    t = Tabela("", cols, tab, 1.8, 3.3)
    paginas = []
    ini = 0
    while ini < len(t.linhas):
        paginas.append(ini)
        y = 262 - 5.0 - t.alt - 0.6
        while ini < len(t.linhas) and y > 18:
            y -= t.alt + (0.8 if isinstance(t.linhas[ini], str) else 0)
            ini += 1
    total = len(paginas)
    for n, ini in enumerate(paginas, 1):
        pg = pdf.pagina(*A4)
        logo(pg, 10, 284, 4.6)
        pg.texto(200, 286, f"Obra {info['obra']}", 2.6, PRETO, negrito=True, alinh="d")
        pg.texto(200, 281.5, info.get("projeto", ""), 2.0, ESCURO_DC, alinh="d")
        pg.texto(10, 274, "LISTAGEM DE MATERIAL", 3.6, PRETO, negrito=True)
        pg.texto(200, 274, info.get("data", ""), 2.0, ESCURO_DC, alinh="d")
        pg.linha(10, 271, 200, 271, 0.3, PRETO)
        t.desenhar(pg, 10, 266, 18, ini)
        pg.linha(10, 12, 200, 12, 0.15, CINZA)
        pg.texto(10, 8, "Quantidades do modelo (líquidas, peças como cortadas; montantes inteiros); compra = quantidade x "
                 "(1 + desperdício) / unidade. Não inclui consumíveis, fundação, portas interiores nem instalações.", 1.5, CINZA)
        pg.texto(200, 8, f"Página {n}/{total}", 1.8, ESCURO_DC, alinh="d")
    pdf.gravar(caminho_pdf)
    if SVG:
        pdf.gravar_svg(SVG, Path(caminho_pdf).stem)
    return total, linhas


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--saida")
    ap.add_argument("--sem-reconstruir", action="store_true")
    ap.add_argument("--svg", action="store_true", help="also SVG previews of every sheet in the work folder")
    a = ap.parse_args()
    global SVG
    casa = Casa(a.config, reconstruir=not a.sem_reconstruir)
    if a.svg:
        SVG = casa.trab / "svg"
    doc = casa.cfg.get("documentos", {})
    projeto_dir = casa.base.parents[1] if casa.base.parent.name == "modelos" else casa.base
    saida = Path(a.saida) if a.saida else projeto_dir / "documentos"
    saida.mkdir(parents=True, exist_ok=True)
    hoje = datetime.date.today()
    info = {"obra": casa.obra, "projeto": doc.get("projeto", casa.cfg.get("nome", "")), "local": doc.get("local", ""),
            "data": hoje.strftime("%d/%m/%Y"),
            "revisoes": doc.get("revisoes") or [["A", hoje.strftime("%y/%m/%d"), "Gerado a partir do modelo (BOB)"]],
            "origem": "Gerado pelo BOB a partir do modelo"}
    pre = casa.obra.replace(" ", "_")
    n1 = doc_modulos(casa, info, saida / f"{pre}_Modulos.pdf")
    doc_cob = doc_cobertura_avista if casa.G["cobertura"].get("tipo") == "a_vista" else doc_cobertura
    n2 = doc_cob(casa, info, saida / f"{pre}_Cobertura.pdf")
    n3, linhas = doc_listagem(casa, info, saida / f"{pre}_Listagem_Material.pdf", saida / f"{pre}_Listagem_Material.csv")
    mad = [l for l in linhas if l[0] == "1"]
    print(f"DOCS_OK {saida}")
    print(f"  {pre}_Modulos.pdf: {n1} folhas; {pre}_Cobertura.pdf: {n2} folhas; {pre}_Listagem_Material.pdf: {n3} páginas")
    print(f"  madeira da estrutura: {sum(l[3] for l in mad)} peças, {sum(l[4] for l in mad):.1f} m, {sum(l[6] for l in mad):.2f} m3")


if __name__ == "__main__":
    main()
