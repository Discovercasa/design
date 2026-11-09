"""Runs INSIDE a fresh Blender (--factory-startup): re-import one exported file and measure it the same way as the
source (Step Inside Phase 3, hub task 65).

    blender --background --factory-startup --python blender_reimportar.py -- run.json
run.json = {"ficheiro": path, "formato": "fbx" | "glb" | "usdz", "camera": {...}, "render": out .png, "resumo": out .json}
"""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

run = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
f = run["ficheiro"]
fmt = run["formato"]
if fmt == "fbx":
    bpy.ops.import_scene.fbx(filepath=f)
elif fmt == "glb":
    bpy.ops.import_scene.gltf(filepath=f)
else:
    bpy.ops.wm.usd_import(filepath=f)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
obs = [o for o in bpy.context.view_layer.objects if o.type == "MESH"]
tri = 0
lo = Vector((1e18, 1e18, 1e18))
hi = -lo
mats, imgs, faltam = set(), set(), set()
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
            mats.add(s.material.name.split(".")[0])
            if s.material.use_nodes:
                for n in s.material.node_tree.nodes:
                    if n.type == "TEX_IMAGE" and n.image:
                        imgs.add(n.image.name)
                        if not n.image.has_data and not n.image.packed_file:
                            try:
                                n.image.reload()
                            except RuntimeError:
                                pass
                            if not n.image.has_data and not Path(bpy.path.abspath(n.image.filepath)).exists():
                                faltam.add(n.image.name)
sc = bpy.context.scene
cam = bpy.data.objects.new("CMP_CAM", bpy.data.cameras.new("CMP_CAM"))
sc.collection.objects.link(cam)
c = run["camera"]
cam.location, cam.rotation_euler, cam.data.lens = c["loc"], c["rot"], c["lente"]
cam.data.clip_end = 5000
sc.camera = cam
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "FLAT"
sc.display.shading.color_type = "TEXTURE"
sc.display.shading.show_cavity = False
sc.display.shading.show_shadows = False
sc.render.resolution_x, sc.render.resolution_y = 800, 500
sc.render.film_transparent = True
sc.render.filepath = run["render"]
bpy.ops.render.render(write_still=True)
json.dump({"objetos": len(obs), "triangulos": tri, "caixa_min": [round(x, 3) for x in lo],
           "caixa_max": [round(x, 3) for x in hi], "dimensoes": [round(h - l, 3) for l, h in zip(lo, hi)],
           "materiais": sorted(mats), "imagens": len(imgs), "imagens_em_falta": sorted(faltam)},
          open(run["resumo"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("REIMPORT_OK")

# visual comparison with the source render (same camera, flat texture colour, transparent background)
if run.get("referencia") and Path(run["referencia"]).exists():
    import numpy as np
    a = bpy.data.images.load(run["referencia"])
    b = bpy.data.images.load(run["render"])
    pa = np.empty(a.size[0] * a.size[1] * 4, dtype=np.float32)
    pb = np.empty(b.size[0] * b.size[1] * 4, dtype=np.float32)
    a.pixels.foreach_get(pa)
    b.pixels.foreach_get(pb)
    pa, pb = pa.reshape(-1, 4), pb.reshape(-1, 4)
    d = np.abs(pa - pb).max(axis=1)
    cobertura = float(((pa[:, 3] > 0.5) | (pb[:, 3] > 0.5)).mean())
    out = json.load(open(run["resumo"], encoding="utf-8"))
    out["imagem"] = {"diferenca_media": round(float(d.mean()), 4), "pixeis_diferentes": round(float((d > 0.1).mean()), 4),
                     "silhueta_diferente": round(float(((pa[:, 3] > 0.5) != (pb[:, 3] > 0.5)).mean()), 4),
                     "cobertura": round(cobertura, 3)}
    json.dump(out, open(run["resumo"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
