"""Runs INSIDE Blender (>= 4.4) on a visit model: the mobile AR asset (Step Inside Phase 7, hub tasks 82, 83, 157).

    blender --background visita.blend --python blender_ar.py -- run.json

run.json = {"variante": "casa" | "maquete", "piso": None | k, "ocultos": [MAT ids not seen from outside],
            "raio_terreno_m": 20, "textura_max": 1024, "glb": path, "usdz": path, "resumo": path}
  casa     the house alone at 1:1, origin at the centre of its footprint on the finished ground floor: placed on the
           real ground, the client walks around it
  maquete  the house with the terrain around it (cropped), same origin: seen scaled down on a table
  piso k   (houses of two or more storeys, user 2026-11-09: «como é que o cliente pode ver o piso de cima ou o de
           baixo»): casa → storey k alone at 1:1, from 0,2 m under its floor to just under the next floor (the top
           storey without its roof), set down so its floor is at the origin — the client walks inside it on the real
           ground; maquete → the house open down to storey k (what is above cut off, its ceilings and roof left out),
           on the terrain. The storeys are the levels of the visible floor finishes (resumo "niveis").
Steps: drop what is not seen (excluded collections, hidden layers: OSB, wool, membranes, structure…), join the meshes
per material (few draw calls), merge coplanar faces (same shape, fewer triangles), scale the textures down, move the
origin, export GLB (Scene Viewer) and USDZ (Quick Look). No baked shadows (spec §8: the viewers draw them).
"""
import json
import math
import sys

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

# origin: centre of the house footprint, at the finished ground floor (lowest top of the floors)
lo = Vector((1e18, 1e18, 1e18))
hi = -lo
for o in casa:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        lo, hi = Vector(map(min, lo, w)), Vector(map(max, hi, w))
pisos = [o for o in casa if o.get("si_categoria") == "ARCH_FLOORS"]
z0 = min(max((o.matrix_world @ Vector(c)).z for c in o.bound_box) for o in pisos) if pisos else lo.z
origem = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, z0))


def caixa_mundo(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector(map(min, *pts)), Vector(map(max, *pts))


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

# 2. bake every kept object into one mesh per material, in coordinates relative to the origin
porm = {}
for o in manter:
    me = o.evaluated_get(dg).to_mesh()
    M = Matrix.Translation(-origem) @ o.matrix_world
    mat = o.active_material
    porm.setdefault(mat.name if mat else "_sem", []).append((me.copy(), M, mat))
    o.evaluated_get(dg).to_mesh_clear()
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
sc = bpy.context.scene
col = bpy.data.collections.new("AR")
sc.collection.children.link(col)
raio = run.get("raio_terreno_m", 20.0)
tri_antes = 0
for nome, partes in porm.items():
    bm = bmesh.new()
    for me, M, mat in partes:
        me.transform(M)
        if me.polygons and mat is not None and me.materials:
            pass
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    if nome == "MAT_LANDSCAPE_SOIL" or (partes and partes[0][2] and partes[0][2].name.startswith("MAT_LANDSCAPE")):
        # table model: keep the ground within `raio` of the house footprint
        fora = [f for f in bm.faces if any(
            max(abs(v.co.x) - (hi.x - lo.x) / 2, abs(v.co.y) - (hi.y - lo.y) / 2) > raio for v in f.verts)]
        bmesh.ops.delete(bm, geom=fora, context="FACES")
    terreno = nome.startswith("MAT_LANDSCAPE") or (partes and partes[0][2] and partes[0][2].name.startswith("MAT_LANDSCAPE"))
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

# 3. textures down to textura_max (colour) and half of it for normal / roughness
tmax = run.get("textura_max", 1024)
imgs = {}
for m in bpy.data.materials:
    if not m.use_nodes or m.users == 0:
        continue
    for n in m.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image and n.image.name not in imgs:
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
           "textura_maior": max((max(s) for s in imgs.values()), default=0),
           "dimensoes": [round(b - a, 3) for a, b in zip(*caixa)],
           "origem": "centro da planta da casa, no pavimento acabado " + (
               f"do piso {PISO}" if PISO is not None and run["variante"] == "casa" else "do rés do chão"),
           "z_min": round(min(o.bound_box[i][2] for o in col.objects for i in range(8)), 3)},
          open(run["resumo"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("AR_OK", tri)
