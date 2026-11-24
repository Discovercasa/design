"""Runs INSIDE Blender on a visit model (with or without interiors): the GLB the Unreal test project imports
(Step Inside Phase 4, first test).

    blender -b visita_interiores.blend --python blender_para_unreal.py -- <out.glb> <out_resumo.json>

Exports what is visible in the visit (as blender_exportar.py) as one GLB with embedded textures: Unreal's Interchange
glTF importer makes the PBR materials from it and turns Y-up metres into Z-up centimetres by itself. Each object keeps
its si_* properties as glTF extras. Writes the numbers the Unreal side checks against (objects, triangles, box).
"""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
glb, resumo = Path(args[0]), Path(args[1])
glb.parent.mkdir(parents=True, exist_ok=True)
dg = bpy.context.evaluated_depsgraph_get()
vis = [o for o in bpy.context.view_layer.objects if o.visible_get() and o.type == "MESH"]
tri, lo, hi, cat = 0, Vector((1e18,) * 3), Vector((-1e18,) * 3), {}
for o in vis:
    me = o.evaluated_get(dg).to_mesh()
    me.calc_loop_triangles()
    tri += len(me.loop_triangles)
    for v in me.vertices:
        w = o.matrix_world @ v.co
        lo, hi = Vector(map(min, lo, w)), Vector(map(max, hi, w))
    o.evaluated_get(dg).to_mesh_clear()
    c = o.get("si_categoria", "?")
    cat[c] = cat.get(c, 0) + 1
bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_visible=True, export_extras=True, export_yup=True,
                          export_apply=True, export_image_format="AUTO", export_materials="EXPORT")
json.dump({"objetos": len(vis), "triangulos": tri, "caixa_min": [round(x, 3) for x in lo],
           "caixa_max": [round(x, 3) for x in hi], "categorias": cat, "blender": bpy.app.version_string,
           "glb_bytes": glb.stat().st_size}, open(resumo, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("UNREAL_GLB_OK", glb.stat().st_size, tri)
