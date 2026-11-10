"""Runs INSIDE Blender (>= 4.4) on a visit model: the mobile AR asset (Step Inside Phase 7, hub tasks 82, 83, 157).

    blender --background visita.blend --python blender_ar.py -- run.json

run.json = {"variante": "casa" | "maquete", "piso": None | k, "ocultos": [MAT ids not seen from outside],
            "raio_terreno_m": 20, "textura_max": 1024, "glb": path, "usdz": path, "resumo": path}
  casa     the house alone at 1:1, its entrance façade facing the viewer, origin 2 m in front of it on the finished
           ground floor: placed on the real ground, the client starts in front of the house and walks around it
  maquete  the house on a block of its terrain, origin at the centre of the footprint: seen scaled down on a table
  piso k   (houses of two or more storeys, user 2026-11-09: «como é que o cliente pode ver o piso de cima ou o de
           baixo»): casa → storey k alone at 1:1, from 0,2 m under its floor to just under the next floor (the top
           storey without its roof), set down so its floor is at the origin — the client walks inside it on the real
           ground; maquete → the house open down to storey k (what is above cut off, its ceilings and roof left out),
           on the terrain. The storeys are the levels of the visible floor finishes (resumo "niveis").
Steps: drop what is not seen (excluded collections, hidden layers: OSB, wool, membranes, structure…), join the meshes
per material (few draw calls), merge coplanar faces (same shape, fewer triangles), scale the textures down, move the
origin, export GLB (Scene Viewer) and USDZ (Quick Look). The sun's shadow is not baked (spec §8: the viewers draw
it); the ambient occlusion is (task 157, 2026-11-09): a thin film on the shaded faces (2d), and in the table model the
ground (2c), cut as a clean block (2b, maquete.py).
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

run = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
OCULTOS = set(run.get("ocultos", []))
vl = bpy.context.view_layer
dg = bpy.context.evaluated_depsgraph_get()

# 1. what stays: visible meshes, not hidden layers; the terrain only in the table model
manter = []
for o in list(vl.objects):
    if o.type != "MESH" or not o.visible_get():
        continue
    cat = o.get("si_categoria", "")
    if cat.startswith("SITE"):
        if run["variante"] == "maquete" and cat == "SITE_TERRAIN":
            manter.append(o)
        continue
    if o.get("si_mat_id") in OCULTOS:
        continue
    manter.append(o)
manter_n = {o.name for o in manter}
casa = [o for o in manter if not o.get("si_categoria", "").startswith("SITE")]

sys.path.insert(0, str(Path(sys.argv[sys.argv.index("--python") + 1]).resolve().parent))
import maquete as MQ  # noqa: E402


# Orientation and origin (team note on the phone test, 2026-11-10: «quando se abre a casa deve estar orientado de
# frente para nós e quando encontra a superfície não devemos começar dentro da casa ou dentro de uma parede mas sim com
# a casa a nossa frente»). The phones place the model's origin on the floor in front of the viewer, its front (+Z in
# glTF and USD = Blender -Y) facing them. So: the house is turned to its own axes (undoing HOUSE_ROOT, its placement on
# the site) and then so the façade with the entrance (maquete.frente) faces -Y; at 1:1 the origin is `frente_m` in
# front of the house's front-most element, centred, at the finished ground floor; the table model keeps the centre.
def caixa_A(obs, A):
    lo_ = Vector((1e18, 1e18, 1e18))
    hi_ = -lo_
    for o in obs:
        for c in o.bound_box:
            w = A @ o.matrix_world @ Vector(c)
            lo_, hi_ = Vector(map(min, lo_, w)), Vector(map(max, hi_, w))
    return lo_, hi_


raiz = bpy.data.objects.get("HOUSE_ROOT")
A0 = raiz.matrix_world.inverted() if raiz else Matrix.Identity(4)
pisos = [o for o in casa if o.get("si_categoria") == "ARCH_FLOORS"]
plo, phi = caixa_A([o for o in casa if o.get("si_categoria") == "ARCH_WALLS_EXT"] or casa, A0)
z0 = min(max((A0 @ o.matrix_world @ Vector(c)).z for c in o.bound_box) for o in pisos) if pisos else plo.z
vaos = [(o.name, *caixa_A([o], A0)) for o in casa if o.get("si_categoria") == "ARCH_OPENINGS"]
(fx, fy), FRENTE_REGRA = MQ.frente([(n, tuple(a), tuple(b)) for n, a, b in vaos], (plo.x, plo.y, phi.x, phi.y), z0)
GIRO = -math.pi / 2 - math.atan2(fy, fx)   # the entrance façade's outward direction onto -Y
A = Matrix.Rotation(GIRO, 4, "Z") @ A0
lo, hi = caixa_A(casa, A)
if run["variante"] == "casa":
    origem = Vector(((lo.x + hi.x) / 2, lo.y - run.get("frente_m", 2.0), z0))
else:
    origem = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, z0))


def caixa_mundo(o):
    """An object's box in the turned frame (A), like the world box before."""
    return caixa_A([o], A)


# storeys: the levels of the visible floor finishes (relative to the origin), with at least 4 m² of floor each
tops = []
for o in pisos:
    a_, b_ = caixa_mundo(o)
    tops.append((b_.z - origem.z, (b_.x - a_.x) * (b_.y - a_.y)))
grupos_n = []
for z, ar_ in sorted(tops):
    if grupos_n and z - grupos_n[-1][0] < 0.3:
        grupos_n[-1][1] += ar_
    else:
        grupos_n.append([z, ar_])
niveis = [round(z, 3) for z, ar_ in grupos_n if ar_ >= 4.0]
PISO = run.get("piso")
corte_sup = corte_inf = None
desce = 0.0
if PISO is not None:
    if PISO + 1 < len(niveis):
        corte_sup = niveis[PISO + 1] - 0.01   # just under the next storey's floor finish
    topo = PISO == len(niveis) - 1
    tirar = []
    for o in manter:
        cat = o.get("si_categoria", "")
        a_, b_ = caixa_mundo(o)
        if topo and cat == "ARCH_ROOF":
            tirar.append(o)  # the top storey without its roof
        elif run["variante"] == "maquete" and cat == "ARCH_CEILINGS" and a_.z - origem.z >= niveis[PISO] - 0.05 and \
                (corte_sup is None or b_.z - origem.z <= corte_sup + 0.05):
            tirar.append(o)  # the table model is open from above: no ceiling over the storey shown
    manter = [o for o in manter if o not in tirar]
    if run["variante"] == "casa":
        corte_inf = niveis[PISO] - run.get("corte_abaixo_m", 0.2)
        desce = niveis[PISO]
        # the front is measured on what this storey keeps (a ground-floor terrace is cut away from the upper storey)
        fica = [o for o in casa if o in manter and caixa_mundo(o)[1].z - z0 > corte_inf
                and (corte_sup is None or caixa_mundo(o)[0].z - z0 < corte_sup)]
        if fica:
            origem.y = caixa_A(fica, A)[0].y - run.get("frente_m", 2.0)

# 2. bake every kept object into one mesh per material, in coordinates relative to the origin
porm, CATS = {}, {}
for o in manter:
    me = o.evaluated_get(dg).to_mesh()
    M = Matrix.Translation(-origem) @ A @ o.matrix_world
    mat = o.active_material
    porm.setdefault(mat.name if mat else "_sem", []).append((me.copy(), M, mat))
    CATS.setdefault(mat.name if mat else "_sem", set()).add(o.get("si_categoria", ""))
    o.evaluated_get(dg).to_mesh_clear()
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
sc = bpy.context.scene
col = bpy.data.collections.new("AR")
sc.collection.children.link(col)
raio = run.get("raio_terreno_m", 20.0)
RET, TERRENOS = None, []
tri_antes = 0
for nome, partes in porm.items():
    bm = bmesh.new()
    for me, M, mat in partes:
        me.transform(M)
        if me.polygons and mat is not None and me.materials:
            pass
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    terreno = nome.startswith("MAT_LANDSCAPE") or (partes and partes[0][2] and partes[0][2].name.startswith("MAT_LANDSCAPE"))
    if terreno:
        # table model: a clean rectangular block (maquete.py) — the largest rectangle around the house, at most `raio`
        # beyond it, that the survey covers; cut straight. Fallback: the old crop (whole triangles within `raio`).
        tris = [((f.verts[0].co.x, f.verts[0].co.y), (f.verts[k].co.x, f.verts[k].co.y),
                 (f.verts[k + 1].co.x, f.verts[k + 1].co.y)) for f in bm.faces for k in range(1, len(f.verts) - 1)]
        RET = RET or MQ.retangulo(tris, (lo.x - origem.x, lo.y - origem.y, hi.x - origem.x, hi.y - origem.y), raio)
        if RET:
            for ax, val, s in ((0, RET[0], -1), (0, RET[2], 1), (1, RET[1], -1), (1, RET[3], 1)):
                co_, no_ = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
                co_[ax], no_[ax] = val, float(s)
                geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
                bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co_, plane_no=no_, clear_outer=True)
            TERRENOS.append(nome)
        else:
            fora = [f for f in bm.faces if any(
                max(abs(v.co.x) - (hi.x - lo.x) / 2, abs(v.co.y) - (hi.y - lo.y) / 2) > raio for v in f.verts)]
            bmesh.ops.delete(bm, geom=fora, context="FACES")
    if run["variante"] == "casa" and PISO is None:
        # the phone sets the model's lowest point on the real ground: nothing may hang below it (the indicative
        # foundation goes ~1 m down). Cut at corte_abaixo_m under the finished floor: the plinth stays visible.
        corte = -run.get("corte_abaixo_m", 0.2)
        if bm.verts and min(v.co.z for v in bm.verts) < corte:
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(0, 0, corte), plane_no=(0, 0, 1), clear_inner=True)
    if PISO is not None and not terreno:
        # one storey: cut above (and, at 1:1, below) and close the cut, so no wall is seen hollow from above
        for z_c, acima in ((corte_sup, True), (corte_inf, False)):
            if z_c is None or not bm.verts:
                continue
            zs_ = [v.co.z for v in bm.verts]
            if (acima and max(zs_) <= z_c) or (not acima and min(zs_) >= z_c):
                continue
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            r_ = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(0, 0, z_c), plane_no=(0, 0, 1),
                                        clear_outer=acima, clear_inner=not acima)
            cortadas = [e for e in r_["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
            if cortadas:
                bmesh.ops.holes_fill(bm, edges=cortadas, sides=0)
        if desce:
            bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, -desce))
    tri_antes += sum(len(f.verts) - 2 for f in bm.faces)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    # no coplanar merging: it saved < 2 % of the triangles and its T-junctions showed as hairline cracks (2026-11-09)
    if not bm.faces:   # all of it cut away (e.g. the slab in an upper storey): an empty object would put (0,0,0) in boxes
        bm.free()
        continue
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    mat = partes[0][2] if partes else None
    if mat:
        me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = False
    ob = bpy.data.objects.new(nome, me)
    ob["si_mat_id"] = nome
    col.objects.link(ob)


# 2b-2d. Realism (task 157): the table model as a clean block, its ground baked once (no visible repetition, the
# house's soft shadow on it) and a soft shadow in the corners of the house (ambient occlusion). Baked with Cycles.
def _lin(h):
    h = h.lstrip("#")
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4)
                 for x in (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def material_simples(nome, cor, rugosidade=0.95):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*cor, 1.0)
    b.inputs["Roughness"].default_value = rugosidade
    return m


def sk(sockets, ident):
    return next(s for s in sockets if s.identifier == ident)


def cycles(amostras):
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = amostras
    sc.render.bake.margin = 4


def cozer(ob, tipo):
    for o in col.objects:
        o.select_set(False)
    ob.select_set(True)
    vl.objects.active = ob
    bpy.ops.object.bake(type=tipo, margin=4, use_clear=False, target="IMAGE_TEXTURES")


def caixa_z(obs):
    return min(min(o.bound_box[i][2] for i in range(8)) for o in obs)


# 2b. the block: vertical sides from the straight cut down to a flat bottom under everything (it sits flat on a table;
# the ground used to end in a saw-tooth edge). Colour: the catalogue's soil (run "cor_base_maquete").
BASE = {}
if RET and TERRENOS:
    z_base = caixa_z(list(col.objects)) - run.get("base_abaixo_m", 0.3)
    arestas = []
    for nome in TERRENOS:
        bm = bmesh.new()
        bm.from_mesh(bpy.data.objects[nome].data)
        arestas += [(tuple(e.verts[0].co), tuple(e.verts[1].co)) for e in bm.edges if e.is_boundary]
        bm.free()
    quads, fundo = MQ.saia(arestas, RET, z_base)
    vs, fs = [], []
    for q in quads + [fundo]:
        fs.append(tuple(range(len(vs), len(vs) + len(q))))
        vs += q
    me = bpy.data.meshes.new("MAQUETE_BASE")
    me.from_pydata(vs, [], fs)
    me.materials.append(material_simples("MAQUETE_BASE", _lin(run.get("cor_base_maquete", "#73624A"))))
    ob = bpy.data.objects.new("MAQUETE_BASE", me)
    ob["si_mat_id"] = "MAQUETE_BASE"
    col.objects.link(ob)
    BASE = {"retangulo_m": [round(x, 2) for x in RET], "z_base_m": round(z_base, 2), "faces_laterais": len(quads),
            "margens_m": [round(x, 2) for x in (lo.x - origem.x - RET[0], RET[2] - (hi.x - origem.x),
                                                 lo.y - origem.y - RET[1], RET[3] - (hi.y - origem.y))]}

# 2c. the ground of the table model baked into one picture over the block: the catalogue texture at its real size mixed
# with a second, larger and turned copy through a noise mask, a broad colour variation, and the house's ambient
# occlusion — the 2-3 m tile no longer shows as a pattern, and the house sits on its soft shadow.
TERRENO = {}
if RET and TERRENOS and run.get("cozer_terreno", True):
    TPX = run.get("terreno_px", 2048)
    w_m, h_m = RET[2] - RET[0], RET[3] - RET[1]
    W = TPX if w_m >= h_m else max(256, int(round(TPX * w_m / h_m / 64)) * 64)
    H = TPX if h_m >= w_m else max(256, int(round(TPX * h_m / w_m / 64)) * 64)
    cycles(run.get("terreno_amostras", 16))
    for nome in TERRENOS:
        ob = bpy.data.objects[nome]
        me = ob.data
        m0 = me.materials[0]
        b0 = next((n for n in m0.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if m0.use_nodes else None
        lk = b0.inputs["Base Color"].links if b0 else []
        img0 = lk[0].from_node.image if lk and lk[0].from_node.type == "TEX_IMAGE" else None
        cor0 = tuple(b0.inputs["Base Color"].default_value[:3]) if b0 else (0.3, 0.3, 0.3)
        rug0 = b0.inputs["Roughness"].default_value if b0 else 0.95
        tile = list(m0.get("si_tile_m", [2.0, 2.0]))
        while len(me.uv_layers) > 1:
            me.uv_layers.remove(me.uv_layers[-1])
        uvl = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name="UVMap")
        for lp in me.loops:
            co = me.vertices[lp.vertex_index].co
            uvl.data[lp.index].uv = ((co.x - RET[0]) / w_m, (co.y - RET[1]) / h_m)
        alvo = bpy.data.images.new("AR_TERRENO", W, H)
        alvo.file_format = "JPEG"
        mb = bpy.data.materials.new("AR_COZER_TERRENO")
        mb.use_nodes = True
        N, L = mb.node_tree.nodes, mb.node_tree.links
        for n in list(N):
            N.remove(n)
        out = N.new("ShaderNodeOutputMaterial")
        em = N.new("ShaderNodeEmission")
        L.new(em.outputs["Emission"], out.inputs["Surface"])
        geo = N.new("ShaderNodeNewGeometry")

        def camada(escala, ang, dx, dy):
            mp = N.new("ShaderNodeMapping")
            mp.vector_type = "POINT"
            mp.inputs["Location"].default_value = (dx, dy, 0.0)
            mp.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(ang))
            mp.inputs["Scale"].default_value = (1 / (tile[0] * escala), 1 / (tile[1] * escala), 1.0)
            L.new(geo.outputs["Position"], mp.inputs["Vector"])
            tx = N.new("ShaderNodeTexImage")
            tx.image = img0
            L.new(mp.outputs["Vector"], tx.inputs["Vector"])
            return tx.outputs["Color"]

        def ruido(escala, de, ate, para0, para1, detalhe=2.0):
            ns = N.new("ShaderNodeTexNoise")
            ns.inputs["Scale"].default_value = escala
            ns.inputs["Detail"].default_value = detalhe
            L.new(geo.outputs["Position"], ns.inputs["Vector"])
            mr = N.new("ShaderNodeMapRange")
            mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = de, ate
            mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = para0, para1
            L.new(ns.outputs["Fac"], mr.inputs["Value"])
            return mr.outputs["Result"]

        def mistura(tipo, fator, a_, b_):
            mx = N.new("ShaderNodeMix")
            mx.data_type, mx.blend_type = "RGBA", tipo
            if isinstance(fator, float):
                sk(mx.inputs, "Factor_Float").default_value = fator
            else:
                L.new(fator, sk(mx.inputs, "Factor_Float"))
            L.new(a_, sk(mx.inputs, "A_Color"))
            L.new(b_, sk(mx.inputs, "B_Color"))
            return sk(mx.outputs, "Result_Color")

        if img0:
            cor = mistura("MIX", ruido(0.15, 0.42, 0.58, 0.0, 1.0), camada(1.0, 0.0, 0.0, 0.0), camada(2.3, 37.0, 0.31, 0.71))
        else:
            rgb = N.new("ShaderNodeRGB")
            rgb.outputs[0].default_value = (*cor0, 1.0)
            cor = rgb.outputs[0]
        cor = mistura("MULTIPLY", 1.0, cor, ruido(0.05, 0.35, 0.65, 0.9, 1.08, 1.0))
        ao = N.new("ShaderNodeAmbientOcclusion")
        ao.samples = 16
        ao.inputs["Distance"].default_value = run.get("ao_distancia_terreno_m", 1.5)
        L.new(cor, ao.inputs["Color"])
        L.new(ao.outputs["Color"], em.inputs["Color"])
        t = N.new("ShaderNodeTexImage")
        t.image = alvo
        N.active = t
        me.materials[0] = mb
        cozer(ob, "EMIT")
        m0.name = m0.name + "_tile"
        mf = bpy.data.materials.new(nome)
        mf.use_nodes = True
        b = mf.node_tree.nodes.get("Principled BSDF")
        t = mf.node_tree.nodes.new("ShaderNodeTexImage")
        t.image = alvo
        mf.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = rug0
        me.materials[0] = mf
        TERRENO[nome] = {"px": [W, H], "textura_base": img0.name if img0 else None, "tile_m": tile}

# 2d. ambient occlusion of the house: Quick Look (iPhone) reads one set of UVs only, and the house's textures repeat
# on theirs, so the shading cannot go in the texture. A thin film ("AR_OCLUSAO") a few mm off each surface carries it:
# black, its transparency baked from the ambient occlusion (own UVs), so it darkens the corners, the eaves, under the
# pergola and the window reveals. Only the faces that get some shade keep their film.
OCL = {}
if run.get("oclusao", True):
    import numpy as np

    AO_D, FORCA = run.get("ao_distancia_m", 1.0), run.get("ao_forca", 0.7)
    EPS, APX = run.get("ao_afastamento_m", 0.005), run.get("ao_px", 1024)   # 1024: as in the USDZ, lighter on phones
    sc.world = sc.world or bpy.data.worlds.new("W")
    sc.world.light_settings.distance = AO_D

    def transparente(o):
        m = o.active_material
        return bool(m) and (getattr(m, "surface_render_method", "") == "BLENDED" or getattr(m, "blend_method", "") == "BLEND")

    fontes = [o for o in col.objects if o.name not in TERRENOS and o.name != "MAQUETE_BASE" and not transparente(o)]
    vidros = [o for o in col.objects if transparente(o)]
    bm = bmesh.new()
    for o in fontes:
        n0 = len(bm.faces)
        bm.from_mesh(o.data)
        if "ARCH_ROOF" in CATS.get(o.name, ()):
            # the roof covering keeps its film only underneath (the eaves): on top it faces the open sky and its only
            # shade was a hard, broken line at the lip of each row of tiles (Sobral, 2026-11-09); the tile relief is
            # already in the texture
            bm.faces.ensure_lookup_table()
            bm.normal_update()
            bmesh.ops.delete(bm, geom=[f for f in bm.faces[n0:] if f.normal.z > -0.7], context="FACES")
    bm.normal_update()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_area() < 1e-6], context="FACES")
    # Faces covered by another surface closer than the film's offset get no film (team note on the phone test,
    # 2026-11-10: «aparecem texturas com glitch a aparecer e a desaparecer»): the slab's top under the 5 mm vinyl floor
    # put its film exactly on the floor's surface (153 m² at Torres Vedras) and the two fought for each pixel.
    from mathutils.bvhtree import BVHTree
    bm_todos = bmesh.new()
    for o in fontes + vidros:
        bm_todos.from_mesh(o.data)
    arvore = BVHTree.FromBMesh(bm_todos)
    ALCANCE = EPS + run.get("ao_folga_m", 0.007)
    tapadas = []
    for f in bm.faces:
        c = f.calc_center_median()
        pts = [c] + [c.lerp(v.co, 0.8) for v in f.verts]
        n_hits = sum(1 for p in pts if arvore.ray_cast(p + f.normal * 1e-4, f.normal, ALCANCE)[0] is not None)
        if n_hits >= 0.4 * len(pts):
            tapadas.append(f)
    bm_todos.free()
    bmesh.ops.delete(bm, geom=tapadas, context="FACES")
    bmesh.ops.split_edges(bm, edges=[e for e in bm.edges if e.calc_face_angle(10.0) > math.radians(10)])
    bm.normal_update()
    for v in bm.verts:
        n_ = Vector()
        for f in v.link_faces:
            n_ += f.normal * f.calc_area()
        if n_.length > 1e-12:
            v.co += n_.normalized() * EPS
    me = bpy.data.meshes.new("AR_OCLUSAO")
    bm.to_mesh(me)
    bm.free()
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    me.uv_layers.new(name="UVMap")
    me.materials.clear()
    ob = bpy.data.objects.new("AR_OCLUSAO", me)
    col.objects.link(ob)
    chao = None
    if run["variante"] == "casa":  # the phone sets the model on the real ground: shade the walls' feet
        z_ = caixa_z(fontes)
        mc = bpy.data.meshes.new("_chao")
        mc.from_pydata([(-200, -200, z_), (200, -200, z_), (200, 200, z_), (-200, 200, z_)], [], [(0, 1, 2, 3)])
        chao = bpy.data.objects.new("_chao", mc)
        col.objects.link(chao)
    for o in vidros:
        o.hide_render = True  # glass lets the light in

    def desembrulhar():
        for o in col.objects:
            o.select_set(False)
        ob.select_set(True)
        vl.objects.active = ob
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(30), island_margin=0.004, area_weight=0.0,
                                 correct_aspect=True, scale_to_bounds=False)
        bpy.ops.object.mode_set(mode="OBJECT")

    def cozer_ao(px, amostras):
        img = bpy.data.images.new("_ao", px, px, is_data=True)
        img.generated_color = (1.0, 1.0, 1.0, 1.0)
        m = bpy.data.materials.new("_ao")
        m.use_nodes = True
        t = m.node_tree.nodes.new("ShaderNodeTexImage")
        t.image = img
        m.node_tree.nodes.active = t
        me.materials.clear()
        me.materials.append(m)
        cycles(amostras)
        cozer(ob, "AO")
        return np.array(img.pixels[:], dtype=np.float32).reshape(px, px, 4)[..., 0]

    def ao_por_face(a):
        H_, W_ = a.shape
        uv = me.uv_layers.active.data
        res = []
        for p in me.polygons:
            us = [(uv[i].uv.x, uv[i].uv.y) for i in p.loop_indices]
            cu, cv = sum(u[0] for u in us) / len(us), sum(u[1] for u in us) / len(us)
            # the shade often lies in a thin line along an edge (a step, a corner): sample next to corners and edges
            bordas = us + [((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2) for a_, b_ in zip(us, us[1:] + us[:1])]
            pts = [(cu, cv)] + [(x * k + cu * (1 - k), y * k + cv * (1 - k)) for x, y in bordas for k in (0.5, 0.85, 0.97)]
            vals = [a[min(H_ - 1, max(0, int(y * H_))), min(W_ - 1, max(0, int(x * W_)))] for x, y in pts]
            res.append((min(vals), max(vals)))
        return res

    faces0 = len(me.polygons)
    desembrulhar()
    a = cozer_ao(max(512, APX // 2), 24)
    tirar = {i for i, (mn, mx_) in enumerate(ao_por_face(a)) if mn >= 0.97 or mx_ <= 0.12}  # unshaded / enclosed
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in tirar], context="FACES")
    bm.to_mesh(me)
    bm.free()
    desembrulhar()
    a = cozer_ao(APX, run.get("ao_amostras", 64))
    a = sum(np.roll(np.roll(a, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.0  # soften the bake noise
    rgba = np.zeros((APX, APX, 4), dtype=np.float32)
    rgba[..., 3] = np.clip(FORCA * (1.0 - a), 0.0, 1.0)
    imgf = bpy.data.images.new("AR_OCLUSAO", APX, APX, alpha=True)
    imgf.pixels.foreach_set(rgba.ravel())
    imgf.file_format = "PNG"
    mf = bpy.data.materials.new("AR_OCLUSAO")
    mf.use_nodes = True
    b = mf.node_tree.nodes.get("Principled BSDF")
    t = mf.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = imgf
    mf.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
    mf.node_tree.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 1.0
    b.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.0
    if hasattr(mf, "surface_render_method"):
        mf.surface_render_method = "BLENDED"
    else:
        mf.blend_method = "BLEND"
    mf.use_backface_culling = True
    me.materials.clear()
    me.materials.append(mf)
    ob["si_mat_id"] = "AR_OCLUSAO"
    for o in vidros:
        o.hide_render = False
    if chao:
        bpy.data.objects.remove(chao, do_unlink=True)
    me.calc_loop_triangles()
    OCL = {"faces_tapadas": len(tapadas), "faces_candidatas": faces0, "faces": len(me.polygons), "triangulos": len(me.loop_triangles),
           "px": APX, "distancia_m": AO_D, "forca": FORCA, "afastamento_m": EPS}

# 3. textures down to textura_max (colour) and half of it for normal / roughness; the baked pictures (AR_*) keep their
# size (≤ 2048)
tmax = run.get("textura_max", 1024)
imgs = {}
for m in bpy.data.materials:
    if not m.use_nodes or m.users == 0:
        continue
    for n in m.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image and n.image.name.startswith("AR_"):
            imgs[n.image.name] = list(n.image.size)
        elif n.type == "TEX_IMAGE" and n.image and n.image.name not in imgs:
            img = n.image
            alvo = tmax if img.colorspace_settings.name != "Non-Color" else max(256, tmax // 2)
            if max(img.size) > alvo:
                k = alvo / max(img.size)
                img.scale(max(1, int(img.size[0] * k)), max(1, int(img.size[1] * k)))
            imgs[img.name] = list(img.size)

dg = bpy.context.evaluated_depsgraph_get()
tri = 0
for o in col.objects:
    o.data.calc_loop_triangles()
    tri += len(o.data.loop_triangles)
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.export_scene.gltf(filepath=run["glb"], export_format="GLB", use_visible=True, export_yup=True, export_apply=True,
                          export_image_format="JPEG", export_image_quality=85, export_materials="EXPORT",
                          export_extras=True)
bpy.ops.wm.usd_export(filepath=run["usdz"], visible_objects_only=True, export_materials=True, export_textures=True,
                      overwrite_textures=True, relative_paths=True, convert_orientation=True,
                      export_global_forward_selection="NEGATIVE_Z", export_global_up_selection="Y", meters_per_unit=1.0,
                      usdz_downscale_size=str(tmax) if str(tmax) in ("256", "512", "1024", "2048", "4096") else "KEEP",
                      generate_materialx_network=False)
caixa = [list(map(min, *[o.bound_box[i] for o in col.objects for i in range(8)])),
         list(map(max, *[o.bound_box[i] for o in col.objects for i in range(8)]))]
nome_var = run["variante"] + (f"_piso{PISO}" if PISO is not None else "")
json.dump({"variante": nome_var, "base": run["variante"], "piso": PISO, "niveis": niveis,
           "objetos": len(col.objects), "materiais": sorted(o.name for o in col.objects),
           "triangulos": tri, "triangulos_antes_de_simplificar": tri_antes, "imagens": imgs,
           "oclusao": OCL, "maquete_base": BASE, "terreno_cozido": TERRENO,
           "textura_maior": max((max(s) for s in imgs.values()), default=0),
           "dimensoes": [round(b - a, 3) for a, b in zip(*caixa)],
           "origem": (f"{run.get('frente_m', 2.0):g} m à frente da casa, ao centro da fachada da entrada"
                      if run["variante"] == "casa" else "centro da planta da casa") + ", no pavimento acabado " + (
               f"do piso {PISO}" if PISO is not None and run["variante"] == "casa" else "do rés do chão"),
           "frente": {"regra": FRENTE_REGRA, "rotacao_graus": round(math.degrees(GIRO) % 360, 1),
                      "nota": "a fachada da frente fica virada para quem vê (+Z no glTF e no USD)"},
           "z_min": round(min(o.bound_box[i][2] for o in col.objects for i in range(8)), 3)},
          open(run["resumo"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("AR_OK", tri)
