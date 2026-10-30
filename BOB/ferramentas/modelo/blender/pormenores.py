"""Runs INSIDE Blender on a saved model: close-up renders to check the details before handing a model over.
    blender --background model.blend --python pormenores.py -- geometria.json out_dir

One view of every outside corner of the frame outline (geometry "contorno_estrutura", or the house box)
from outside and above, looking at the top of the walls (chapéu, gutters, parapets, cladding at the corner);
every re-entrant corner from the notch and from above the roof (the parapet ends standing over the roof);
plus a view of the ceiling of the house from below. Workbench, 1000x800 PNG files named canto_XX_<x>_<y>.png
and teto.png. Lessons that made this tool (Torres Vedras 2026-10-15): rufo corners left open, cladding
stopping short at a corner, a slot across a ceiling.
"""
import json
import math
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
G = json.load(open(args[0], encoding="utf-8"))
out = args[1]
L, D = G["casa"]["comprimento"], G["casa"]["profundidade"]
cont = G.get("contorno_estrutura") or [[0, 0], [L, 0], [L, D], [0, D]]
z_top = G["niveis"].get("platibanda") or G["cobertura"].get("plano_z_cume", 3.0)

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.color_type = "MATERIAL"
sc.display.shading.show_cavity = True
sc.render.resolution_x, sc.render.resolution_y = 1000, 800
cam = bpy.data.objects.get("Camera") or bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
if cam.name not in sc.collection.objects and not cam.users_collection:
    sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 35


def area2(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly))) / 2


sentido = 1 if area2(cont) > 0 else -1  # counter-clockwise outline: outward normal = right of each edge
n = len(cont)
k = 0
for i in range(n):
    p, a, b = Vector(cont[i]), Vector(cont[i - 1]), Vector(cont[(i + 1) % n])
    e1, e2 = (p - a).normalized(), (b - p).normalized()
    convexo = (e1.x * e2.y - e1.y * e2.x) * sentido > 0
    n1 = Vector((e1.y, -e1.x)) * sentido
    n2 = Vector((e2.y, -e2.x)) * sentido
    fora = (n1 + n2).normalized()
    if convexo:
        vistas = [("canto", Vector((p.x + fora.x * 1.6, p.y + fora.y * 1.6, z_top + 0.9)), z_top - 0.3)]
    else:  # re-entrant corner (an L): from the notch outside, and from above the roof looking at the parapet ends
        # (Torres Vedras 2026-10-16: the structure was seen at the end of a parapet standing over the roof)
        vistas = [("reentrante", Vector((p.x + fora.x * 2.2, p.y + fora.y * 2.2, z_top + 0.7)), z_top - 0.5),
                  ("reentrante_cob", Vector((p.x - fora.x * 1.8, p.y - fora.y * 1.8, z_top + 1.2)), z_top - 0.1)]
    for nome, loc, z_alvo in vistas:
        cam.location = loc
        cam.rotation_euler = (Vector((p.x, p.y, z_alvo)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        k += 1
        sc.render.filepath = f"{out}/{nome}_{k:02d}_{p.x:.1f}_{p.y:.1f}.png"
        bpy.ops.render.render(write_still=True)

# ceiling of the largest room from below (its Pladur object), looking up along the room
tetos = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Pladur") and "(teto)" in o.name]
if tetos:
    o = max(tetos, key=lambda o: o.get("area_m2", 0.0))
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    x0, x1 = min(c.x for c in cs), max(c.x for c in cs)
    y0, y1 = min(c.y for c in cs), max(c.y for c in cs)
    zc = min(c.z for c in cs)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cam.location = Vector((cx, y0 + 0.4, 1.2))
    cam.rotation_euler = (Vector((cx, min(y1, cy + 1.5), zc)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = f"{out}/teto.png"
bpy.ops.render.render(write_still=True)
print(f"PORMENORES_OK {k} corners")
