"""Runs INSIDE Blender (>= 4.4) on a visit model: the normalised exports (Step Inside Phase 3, hub task 63).

    blender --background visita.blend --python blender_exportar.py -- run.json

run.json = {"saida": folder, "nome": file stem, "camera": {...} | null, "resumo": out .json}
Exports what is visible in the visit (VISITA > SITE / HOUSE; STRUCT_TIMBER, ARCH_OPTIONS, ARCH_LABELS are excluded):
  FBX  (Unreal)   metres (FBX_SCALE_UNITS), Blender's default axes (-Z forward, Y up: Unreal "Convert Scene"),
                  flat shading per face, no leaf bones, textures copied next to it (spec §4.2: separate image files)
  GLB  (Android / web viewer) glTF 2.0, +Y up (the standard), custom properties as extras (si_id, si_mat_id…),
                  textures embedded
  USDZ (iPhone Quick Look) Y up, metres (metersPerUnit 1), UsdPreviewSurface materials with their textures
Also writes the reference numbers (objects, triangles, bounding box, material IDs, images) and a flat render from a
fixed camera, which the re-import test (blender_reimportar.py) compares against.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

run = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
saida = Path(run["saida"])
saida.mkdir(parents=True, exist_ok=True)
nome = run["nome"]
dg = bpy.context.evaluated_depsgraph_get()

vis = [o for o in bpy.context.view_layer.objects if o.visible_get() and o.type == "MESH"]


def stats(obs):
    tri = 0
    lo = Vector((1e18, 1e18, 1e18))
    hi = -lo
    mats, imgs = set(), set()
    for o in obs:
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        tri += len(me.loop_triangles)
        for v in me.vertices:
            w = o.matrix_world @ v.co
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
        o.evaluated_get(dg).to_mesh_clear()
        for s in o.material_slots:
            if s.material:
                mats.add(s.material.name)
                if s.material.use_nodes:
                    imgs |= {n.image.name for n in s.material.node_tree.nodes if n.type == "TEX_IMAGE" and n.image}
    return {"objetos": len(obs), "triangulos": tri, "caixa_min": [round(x, 3) for x in lo],
            "caixa_max": [round(x, 3) for x in hi], "dimensoes": [round(h - l, 3) for l, h in zip(lo, hi)],
            "materiais": sorted(mats), "imagens": len(imgs)}


ref = stats(vis)
casa = [o for o in vis if not o.get("si_categoria", "").startswith("SITE")]
ref["casa"] = stats(casa)

# fixed camera looking at the house (the same camera is rebuilt for every re-import)
cc = (Vector(ref["casa"]["caixa_min"]) + Vector(ref["casa"]["caixa_max"])) / 2
dim = max(ref["casa"]["dimensoes"][:2])
cam_loc = cc + Vector((-1.6 * dim, -2.0 * dim, 1.1 * dim))
cam_rot = (cc - cam_loc).to_track_quat("-Z", "Y").to_euler()
camera = {"loc": list(cam_loc), "rot": list(cam_rot), "lente": 28}


def render_plano(caminho):
    sc = bpy.context.scene
    cam = bpy.data.objects.new("CMP_CAM", bpy.data.cameras.new("CMP_CAM"))
    sc.collection.objects.link(cam)
    cam.location, cam.rotation_euler, cam.data.lens = camera["loc"], camera["rot"], camera["lente"]
    cam.data.clip_end = 5000
    sc.camera = cam
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "FLAT"
    sc.display.shading.color_type = "TEXTURE"
    sc.display.shading.show_cavity = False
    sc.display.shading.show_shadows = False
    sc.render.resolution_x, sc.render.resolution_y = 800, 500
    sc.render.film_transparent = True
    sc.render.filepath = str(caminho)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam, do_unlink=True)


render_plano(saida / "_ref.png")

ficheiros = {}
fbx = saida / f"{nome}.fbx"
bpy.ops.export_scene.fbx(filepath=str(fbx), use_visible=True, object_types={"MESH", "EMPTY"}, apply_unit_scale=True,
                         apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0, axis_forward="-Z", axis_up="Y",
                         mesh_smooth_type="FACE", add_leaf_bones=False, path_mode="COPY", embed_textures=False,
                         use_custom_props=True)
ficheiros["fbx"] = fbx.name
glb = saida / f"{nome}.glb"
bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_visible=True, export_extras=True, export_yup=True,
                          export_apply=True, export_image_format="AUTO", export_materials="EXPORT")
ficheiros["glb"] = glb.name
usdz = saida / f"{nome}.usdz"
bpy.ops.wm.usd_export(filepath=str(usdz), visible_objects_only=True, selected_objects_only=False, export_materials=True,
                      export_textures=True, overwrite_textures=True, relative_paths=True, convert_orientation=True,
                      export_global_forward_selection="NEGATIVE_Z", export_global_up_selection="Y",
                      meters_per_unit=1.0, usdz_downscale_size="KEEP", generate_materialx_network=False)
ficheiros["usdz"] = usdz.name

json.dump({"referencia": ref, "camera": camera, "ficheiros": ficheiros, "blender": bpy.app.version_string,
           "blend": bpy.data.filepath}, open(run["resumo"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("EXPORT_OK", json.dumps(ficheiros))
