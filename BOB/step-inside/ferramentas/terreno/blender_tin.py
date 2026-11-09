"""Runs INSIDE Blender (>= 4.4): terrain surfaces (TIN) from survey points and contours, with the checks.

    blender --background --factory-startup --python blender_tin.py -- run.json

run.json = {"blend": out .blend, "saida": out stats .json, "folds": 5, "superficies": [{
    "id", "nome", "pontos": [[x, y, z]] (local metres), "curvas": [[[x, y], ...]] (2D lines, heights unknown),
    "rotulos_curvas": [[x, y, z]] (contour value labels, optional), "limite": [[x, y], ...] (optional),
    "faces": [[i, j, k]] (optional: the file's own triangles, e.g. LandXML), "intervalos": [0.25, 0.5, 1, 2, 2.5, 5]}]}

For each surface:
  1. Delaunay triangulation of the points (mathutils.geometry.delaunay_2d_cdt).
  2. Cross-validation: k folds; each fold's points are predicted from a TIN of the others (how well the points
     agree with each other; spikes = labels misread or not ground heights).
  3. Contours: the TIN is sampled along every 2D contour; the contour interval is the largest candidate that most
     lines round to; each line gets the rounded height when it is unambiguous. The contour value labels, when given,
     check that assignment independently.
  4. Final surface: points + contours as constrained edges, border slivers trimmed. Faces must all point up.
Coordinates are local (the caller subtracts the site origin): Blender stores 32-bit floats.
"""
import json
import math
import statistics as st
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt

run = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
FOLDS = run.get("folds", 5)


def cdt(pts2, arestas=()):
    """Delaunay (constrained by arestas) -> (verts2d, faces, orig index of each output vert or None)."""
    vs, _es, fs, orig, _oe, _of = delaunay_2d_cdt([Vector(p) for p in pts2], list(arestas), [], 0, 1e-6, True)
    o = [ov[0] if ov else None for ov in orig]
    return vs, fs, o


def malha_bvh(vs, fs, zs):
    v3 = [(v.x, v.y, z) for v, z in zip(vs, zs)]
    return BVHTree.FromPolygons(v3, fs, all_triangles=True), v3


def amostrar(bvh, x, y):
    hit = bvh.ray_cast(Vector((x, y, 1e5)), Vector((0, 0, -1)))
    return hit[0].z if hit[0] is not None else None


def declive(bvh, x, y):
    """tan of the slope of the surface at (x, y), or 0."""
    hit = bvh.ray_cast(Vector((x, y, 1e5)), Vector((0, 0, -1)))
    if hit[1] is None or abs(hit[1].z) < 1e-6:
        return 0.0
    n = hit[1]
    return math.hypot(n.x, n.y) / abs(n.z)


def estat(erros):
    if not erros:
        return {}
    a = [abs(e) for e in erros]
    a.sort()
    return {"n": len(erros), "media": round(st.fmean(erros), 3), "media_abs": round(st.fmean(a), 3),
            "rmse": round(math.sqrt(st.fmean(e * e for e in erros)), 3), "p50": round(a[len(a) // 2], 3),
            "p95": round(a[min(len(a) - 1, int(len(a) * 0.95))], 3), "max": round(a[-1], 3)}


def unicos(pontos):
    """Drop repeated XY (1 mm); report those whose heights disagree. Returns (points, duplicates, original index)."""
    vistos, out, dup, orig = {}, [], [], []
    for i, (x, y, z) in enumerate(pontos):
        k = (round(x, 3), round(y, 3))
        if k in vistos:
            j = vistos[k]
            if abs(out[j][2] - z) > 0.005:
                dup.append({"indices": [orig[j], i], "z": [out[j][2], z]})
            continue
        vistos[k] = len(out)
        out.append([x, y, z])
        orig.append(i)
    return out, dup, orig


def validacao_cruzada(P):
    erros, piores = [], []
    for f in range(FOLDS):
        treino = [p for i, p in enumerate(P) if i % FOLDS != f]
        teste = [(i, p) for i, p in enumerate(P) if i % FOLDS == f]
        vs, fs, o = cdt([(p[0], p[1]) for p in treino])
        bvh, _ = malha_bvh(vs, fs, [treino[k][2] if k is not None else 0.0 for k in o])
        for i, p in teste:
            z = amostrar(bvh, p[0], p[1])
            if z is not None:  # outside the others' hull: not predictable
                erros.append(z - p[2])
                piores.append((abs(z - p[2]), i, round(z, 2)))
    piores.sort(reverse=True)
    return erros, piores


def dist_linha(x, y, c):
    best = 1e18
    for (x0, y0), (x1, y1) in zip(c, c[1:]):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
        best = min(best, math.hypot(x0 + t * dx - x, y0 + t * dy - y))
    return best


def tin_com_curvas(P, curvas, cotas):
    pts2 = [(p[0], p[1]) for p in P]
    zs = [p[2] for p in P]
    arestas = []
    for c, z in zip(curvas, cotas):
        if z is None:
            continue
        k0 = len(pts2)
        pts2 += [tuple(q) for q in c["pts"]]
        zs += [z] * len(c["pts"])
        arestas += [(k0 + i, k0 + i + 1) for i in range(len(c["pts"]) - 1)]
    return pts2, zs, arestas


def curvas_cotas(P, curvas, rotulos, eq):
    """Heights of 2D contour lines (spec §19.4: a 2D line is never taken as a height by itself):
    1. a contour value label sitting on a line (≤ 1 m) gives that line its height;
    2. the TIN of the points + those lines is sampled along the others and rounded to the contour interval
       (index contours to the index interval); kept only when the rounding is unambiguous.
    eq: {"mestras": index interval, "curvas": contour interval} (each detected when not given)."""
    n = len(curvas)
    cotas, como = [None] * n, [None] * n
    votos = [[] for _ in range(n)]
    caixas = [(min(q[0] for q in c["pts"]), min(q[1] for q in c["pts"]), max(q[0] for q in c["pts"]),
               max(q[1] for q in c["pts"])) for c in curvas]
    for x, y, v in rotulos:
        melhor, md = None, 1.0
        for k, c in enumerate(curvas):
            b = caixas[k]
            if b[0] - md <= x <= b[2] + md and b[1] - md <= y <= b[3] + md:
                d = dist_linha(x, y, c["pts"])
                if d < md:
                    melhor, md = k, d
        if melhor is not None:
            votos[melhor].append(v)
    conflitos = 0
    for k, vs in enumerate(votos):
        if vs and max(vs) - min(vs) < 1e-6:
            cotas[k], como[k] = vs[0], "rotulo"
        elif vs:
            conflitos += 1
    # intervals: index contours from the labels' steps; contours from the length ratio of the two kinds of line
    D = eq.get("mestras")
    if not D and rotulos:
        u = sorted({round(r[2], 3) for r in rotulos})
        passos = [round(b - a, 3) for a, b in zip(u, u[1:]) if b - a > 1e-6]
        D = min(passos) if passos else None
    iv = eq.get("curvas")
    razao = None
    if not iv and D:
        lm = sum(dist_linha_total(c["pts"]) for c in curvas if c.get("papel") == "mestra")
        li = sum(dist_linha_total(c["pts"]) for c in curvas if c.get("papel") == "intermedia")
        if lm and li:
            razao = li / lm
            iv = D / (round(razao) + 1)
    def passagem(papeis, passo_de, tol):
        """One pass: TIN of the points + every line with a height so far, then round the others."""
        pts2, zs, arestas = tin_com_curvas(P, curvas, cotas)
        vs, fs, o = cdt(pts2, arestas)
        bvh, _ = malha_bvh(vs, fs, [zs[k] if k is not None else 0.0 for k in o])
        novas, desv = 0, []
        for k, c in enumerate(curvas):
            if cotas[k] is not None or c.get("papel", "curva") not in papeis:
                continue
            amostras = [z for x, y in c["pts"] if (z := amostrar(bvh, x, y)) is not None]
            passo = passo_de(c)
            if len(amostras) < 2 or not passo:
                continue
            m = st.median(amostras)
            desv.append(st.median(abs(z - m) for z in amostras))
            zr = round(m / passo) * passo
            if c.get("papel") == "intermedia" and D and abs(zr / D - round(zr / D)) < 1e-6:
                continue  # an ordinary contour cannot sit on an index level
            if abs(m - zr) < passo * tol:
                cotas[k], como[k] = round(zr, 3), "tin"
                novas += 1
        return novas, desv

    # index contours first (big interval: robust), then the ordinary ones between them, a few passes
    passagem({"mestra"}, lambda c: D, 0.35)
    desvios = []
    for _ in range(4):
        novas, desvios = passagem({"intermedia", "curva"}, lambda c: iv if c.get("papel") != "mestra" else D, 0.2)
        if not novas:
            break
    return cotas, como, {"linhas": n, "com_cota_por_rotulo": como.count("rotulo"), "com_cota_pelo_tin": como.count("tin"),
                   "sem_cota": cotas.count(None), "rotulos_em_conflito": conflitos,
                   "equidistancia_mestras": D, "equidistancia": iv,
                   "razao_comprimentos_intermedias_mestras": round(razao, 2) if razao else None,
                   "desvio_ao_longo_da_curva_p50": round(st.median(desvios), 3) if desvios else None}


def dist_linha_total(c):
    return sum(math.dist(a, b) for a, b in zip(c, c[1:]))


def aparar(vs, fs, fator=4.0):
    """Remove border triangles with a very long edge (Delaunay's convex-hull slivers), repeatedly."""
    fs = [tuple(f) for f in fs]
    comp = sorted(max((vs[f[0]] - vs[f[1]]).length, (vs[f[1]] - vs[f[2]]).length, (vs[f[2]] - vs[f[0]]).length) for f in fs)
    lim = comp[len(comp) // 2] * fator if comp else 0
    removidos = 0
    while True:
        arestas = {}
        for k, f in enumerate(fs):
            for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
                arestas.setdefault((min(a, b), max(a, b)), []).append(k)
        fora = set()
        for (a, b), ks in arestas.items():
            if len(ks) == 1 and (vs[a] - vs[b]).length > lim:
                fora.add(ks[0])
        if not fora:
            break
        removidos += len(fora)
        fs = [f for k, f in enumerate(fs) if k not in fora]
    return fs, removidos, lim


for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
col = bpy.data.collections.new("SITE_TERRAIN")
bpy.context.scene.collection.children.link(col)
mat = bpy.data.materials.new("MAT_SITE_TERRAIN")
mat.diffuse_color = (0.45, 0.52, 0.32, 1.0)
saida = {"superficies": []}

for S in run["superficies"]:
    R = {"id": S["id"], "nome": S["nome"]}
    excluir = set(S.get("excluir", []))  # human decisions (indices into S["pontos"])
    P0 = [p for i, p in enumerate(S["pontos"]) if i not in excluir]
    orig0 = [i for i in range(len(S["pontos"])) if i not in excluir]
    P, dup, orig1 = unicos(P0)
    ORIG = [orig0[k] for k in orig1]  # P[i] is S["pontos"][ORIG[i]]
    R["pontos"] = len(P)
    R["excluidos_por_decisao"] = len(excluir)
    R["duplicados_com_cotas_diferentes"] = dup
    if len(P) < 3:
        R["erro"] = "menos de 3 pontos"
        saida["superficies"].append(R)
        continue
    erros, piores = validacao_cruzada(P)
    R["validacao_cruzada"] = estat(erros)
    s = R["validacao_cruzada"]
    # spikes: far from what the neighbours predict (robust scale from the median absolute error)
    lim_pico = max(1.0, 6 * 1.4826 * s.get("p50", 0))
    R["limite_pico_m"] = round(lim_pico, 2)
    picos = {i: (e, zp) for e, i, zp in piores if e > lim_pico}

    vs, fs, o = cdt([(p[0], p[1]) for p in P])
    zs = [P[k][2] if k is not None else 0.0 for k in o]
    bvh, _ = malha_bvh(vs, fs, zs)
    curvas = [c for c in S.get("curvas", []) if len(c["pts"]) >= 2]
    cotas, como, cstat = curvas_cotas(P, curvas, S.get("rotulos_curvas", []), S.get("equidistancia", {}))
    R["curvas"] = cstat

    # leave-one-out of the contours: each contour against the TIN of the points + all the OTHER contours.
    # Off by more than half an interval = its height disagrees with its neighbours: not used.
    iv_c = cstat.get("equidistancia")
    retiradas = 0
    if iv_c:
        for k, c in enumerate(curvas):
            if cotas[k] is None or como[k] == "rotulo":
                continue
            outras = list(cotas)
            outras[k] = None
            pts2, zfin, arestas = tin_com_curvas(P, curvas, outras)
            vs_, fs_, o_ = cdt(pts2, arestas)
            b_, _ = malha_bvh(vs_, fs_, [zfin[q] if q is not None else 0.0 for q in o_])
            am = [z for x, y in c["pts"] if (z := amostrar(b_, x, y)) is not None]
            if am and abs(st.median(am) - cotas[k]) > iv_c / 2:
                cotas[k] = None
                retiradas += 1
    R["curvas"]["retiradas_por_incoerencia"] = retiradas
    R["curvas"]["com_cota_final"] = sum(1 for z in cotas if z is not None)

    # points against the contours (two independent drawings of the same ground): each point vs a TIN of the
    # contours alone. A point far from BOTH its neighbours and the contours is set aside for a human to check;
    # a spike the contours confirm is real ground (a bank, a wall foot) and stays.
    dif_curvas, tans = {}, {}
    if any(z is not None for z in cotas):
        pc2, zc, ac = tin_com_curvas([], curvas, cotas)
        vs2, fs2, o2 = cdt(pc2, ac)
        b2, _ = malha_bvh(vs2, fs2, [zc[k] if k is not None else 0.0 for k in o2])
        tans = {}
        for i, p in enumerate(P):
            z = amostrar(b2, p[0], p[1])
            if z is not None:
                dif_curvas[i] = z - p[2]
                tans[i] = declive(b2, p[0], p[1])
        R["curvas_vs_pontos"] = estat(list(dif_curvas.values()))
        cv = R["curvas_vs_pontos"]
        lim_curvas = max(1.0, 6 * 1.4826 * cv.get("p50", 0))
    else:
        lim_curvas = None
    R["limite_desacordo_curvas_m"] = round(lim_curvas, 2) if lim_curvas else None
    # on a slope, the uncertainty of WHERE the point is (label placement, scale) becomes height: allow for it
    INC_XY = S.get("incerteza_xy_m", 1.0)
    R["incerteza_xy_m"] = INC_XY

    def fora_curvas(i):
        d = dif_curvas.get(i)
        return d is not None and lim_curvas and abs(d) > lim_curvas + tans.get(i, 0.0) * INC_XY
    afastar, rever, confirmados = [], [], []
    for i in sorted(set(picos) | {i for i in dif_curvas if fora_curvas(i)}):
        e_viz = picos.get(i, (None, None))
        d_c = dif_curvas.get(i)
        item = {"indice": ORIG[i], "z": P[i][2], "erro_vizinhos": round(e_viz[0], 2) if e_viz[0] else None,
                "previsto_vizinhos": e_viz[1], "dif_curvas": round(d_c, 2) if d_c is not None else None,
                "declive_pct": round(100 * tans.get(i, 0.0)) if dif_curvas else None}
        mau_viz = i in picos
        mau_curvas = fora_curvas(i)
        if mau_viz and mau_curvas:
            afastar.append(item)
        elif mau_viz and d_c is not None:
            confirmados.append(item)
        else:
            rever.append(item)
    R["pontos_afastados"] = afastar      # not used in the surface (NEEDS_HUMAN_REVIEW)
    R["pontos_a_rever"] = rever          # used, but disagree with one of the two checks
    R["picos_confirmados_pelas_curvas"] = confirmados
    fora = {i for i in range(len(P)) if ORIG[i] in {a["indice"] for a in afastar}}
    P = [p for i, p in enumerate(P) if i not in fora]

    # final surface: points + contours with a height as constrained edges
    pts2, zfin, arestas = tin_com_curvas(P, curvas, cotas)
    vs, fs, o = cdt(pts2, arestas)
    zv = []
    sem_origem = 0
    for k in o:
        if k is None:  # a new vertex where two constraints cross (contours should not cross)
            sem_origem += 1
            zv.append(None)
        else:
            zv.append(zfin[k])
    if sem_origem:  # give crossing points the height of the points TIN
        zv = [z if z is not None else (amostrar(bvh, vs[i].x, vs[i].y) or 0.0) for i, z in enumerate(zv)]
    R["cruzamentos_de_curvas"] = sem_origem
    fs, removidos, lim = aparar(vs, fs)
    R["triangulos_aparados"] = removidos
    R["aresta_max_borda_m"] = round(lim, 2)

    bm = bmesh.new()
    bv = [bm.verts.new((v.x, v.y, z)) for v, z in zip(vs, zv)]
    for f in fs:
        try:
            bm.faces.new([bv[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    for f in bm.faces:  # a terrain faces up
        if f.normal.z < 0:
            f.normal_flip()
    bm.normal_update()
    para_baixo = sum(1 for f in bm.faces if f.normal.z < -1e-6)
    verticais = sum(1 for f in bm.faces if abs(f.normal.z) < 0.05)
    inclin = sorted(math.degrees(math.acos(min(1.0, f.normal.z))) for f in bm.faces if f.calc_area() > 0)
    area = sum(f.calc_area() for f in bm.faces)
    area_plana = sum(f.calc_area() * max(0.0, f.normal.z) for f in bm.faces)
    me = bpy.data.meshes.new(f"SITE_TERRAIN_{S['id'].upper()}")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(f"SITE_TERRAIN_{S['id'].upper()}", me)
    ob["si_id"] = f"SITE_TERRAIN_{S['id'].upper()}"
    ob["si_categoria"] = "SITE_TERRAIN"
    ob["si_nome"] = S["nome"]
    col.objects.link(ob)
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zz = [v.co.z for v in me.vertices]
    R["malha"] = {"vertices": len(me.vertices), "triangulos": len(me.polygons), "area_planta_m2": round(area_plana, 1),
                  "area_m2": round(area, 1), "extensao_m": [round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1)],
                  "z_min": round(min(zz), 2), "z_max": round(max(zz), 2), "faces_para_baixo": para_baixo,
                  "faces_verticais": verticais,
                  "inclinacao_graus_p50": round(inclin[len(inclin) // 2], 1) if inclin else None,
                  "inclinacao_graus_p95": round(inclin[int(len(inclin) * 0.95)], 1) if inclin else None,
                  "inclinacao_graus_max": round(inclin[-1], 1) if inclin else None}
    if S.get("limite"):
        cu = bpy.data.curves.new(f"SITE_LIMIT_{S['id'].upper()}", "CURVE")
        cu.dimensions = "3D"
        sp = cu.splines.new("POLY")
        lim_pts = S["limite"]
        sp.points.add(len(lim_pts) - 1)
        for k, (x, y) in enumerate(lim_pts):
            z = amostrar(bvh, x, y)
            sp.points[k].co = (x, y, (z if z is not None else st.fmean(zz)) + 0.05, 1)
        lo = bpy.data.objects.new(f"SITE_LIMIT_{S['id'].upper()}", cu)
        lo["si_categoria"] = "SITE_LIMIT"
        col.objects.link(lo)
    saida["superficies"].append(R)

bpy.ops.wm.save_as_mainfile(filepath=run["blend"], compress=True)
json.dump(saida, open(run["saida"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("TIN_OK", json.dumps([{k: s.get(k) for k in ("id", "pontos")} for s in saida["superficies"]]))
