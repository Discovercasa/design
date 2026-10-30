"""Runs INSIDE Blender on a saved model: Workbench preview renders (the .blend is not modified).
    blender --background model.blend --python previews.py -- OUT_DIR LENGTH DEPTH

Structure: estrutura_SE, estrutura_NW. With build-up layers also:
  seq_exterior_1..n  build sequence of the outside of the walls (visible option) at the south-east corner
  opcao_A/B/C_SE     complete house with each finish option
  seq_interior_1..5  longitudinal section (cut at y = 1.2 m, looking north): structure, wool, OSB, finishes
  corte_transversal  section at x = 3.0 m looking east (compare with CORTE FF')
  alcado_sul, alcado_este, planta_piso0, planta_piso1 (top views of each floor with room labels)
"""
import os
import re
import sys

import bpy
from mathutils import Vector

out, L, D = sys.argv[sys.argv.index("--") + 1:][:3]
L, D = float(L), float(D)
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light, sh.color_type, sh.show_cavity, sh.show_object_outline = "STUDIO", "MATERIAL", True, True
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
cam = sc.camera
vl = bpy.context.view_layer
COLS = {}
for col in bpy.data.collections:
    m = re.match(r"(\d+(?:\.\d+)*) ", col.name)
    if m:
        COLS[m.group(1)] = col


def lc(name, layer=None):
    layer = layer or vl.layer_collection
    if layer.collection.name == name:
        return layer
    for ch in layer.children:
        r = lc(name, ch)
        if r:
            return r


def show(ids):
    """Show the collections whose id is in `ids` (with their children and ancestors), hide the rest."""
    for cid, col in COLS.items():
        on = any(cid == s or cid.startswith(s + ".") or s.startswith(cid + ".") for s in ids)
        layer = lc(col.name)
        if layer:
            layer.hide_viewport = not on
            col.hide_render = not on


def shoot(name, loc, target, ortho=None, clip=0.1, lens=30):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO" if ortho else "PERSP"
    cam.data.lens = lens
    if ortho:
        cam.data.ortho_scale = ortho
    cam.data.clip_start, cam.data.clip_end = clip, 500
    sc.render.filepath = os.path.join(out, name)
    bpy.ops.render.render(write_still=True)


c = (L / 2, D / 2)
estr = ["0", "1"]
opcoes = sorted((k for k in COLS if re.fullmatch(r"2\.\d+", k) and k not in ("2.1", "2.2")),
                key=lambda k: int(k.split(".")[1]))
# the finish option visible in the saved file (config `opcao_visivel`) drives the sequences and sections
visiveis = [k for k in opcoes if lc(COLS[k].name) and not lc(COLS[k].name).hide_viewport]
A = (visiveis or opcoes or [None])[0]
far_SE = ((c[0] + 14, c[1] - 16.5, 11), (c[0], c[1], 2.6))
show(estr)
shoot("estrutura_SE.png", *far_SE)
shoot("estrutura_NW.png", (c[0] - 15, c[1] + 15, 10), (c[0], c[1], 2.6))
if "2" in COLS:
    base = estr + ["2.1", "2.2", "3", "4", "5", "6"]
    subs = sorted((k for k in COLS if k.startswith(A + ".")), key=lambda k: int(k.split(".")[-1]))
    seq = [estr, estr + ["2.1"], estr + ["2.1", "2.2"]] + [estr + ["2.1", "2.2"] + subs[:k] for k in range(1, len(subs) + 1)]
    seq[-1] = seq[-1] + ["6"]
    for i, ids in enumerate(seq, 1):
        show(ids)
        shoot(f"seq_exterior_{i}.png", (L + 4.6, -5.2, 4.0), (L - 2.2, 1.0, 2.9))
    for k, o in enumerate(opcoes):
        show(base + [o])
        shoot(f"opcao_{'ABCDEFG'[k]}_SE.png", *far_SE)
    # interior sequence: section looking north, everything nearer than y = 1.2 is clipped away
    corte = dict(ortho=L + 2.0, clip=20 + 1.2)
    seq_i = [estr, estr + ["3.1"], estr + ["3.1", "3.2"], estr + ["3.1", "3.2", "3.3", "4", "5"], base + [A]]
    for i, ids in enumerate(seq_i, 1):
        show(ids)
        shoot(f"seq_interior_{i}.png", (c[0], -20, 3.6), (c[0], 0, 3.6), **corte)
    show(base + [A])
    shoot("corte_transversal.png", (-20, c[1], 3.6), (0, c[1], 3.6), ortho=12.4, clip=23.0)
    shoot("alcado_sul.png", (c[0], -30, 3.6), (c[0], 0, 3.6), ortho=L + 2.5)
    shoot("alcado_este.png", (L + 30, c[1], 3.6), (0, c[1], 3.6), ortho=12.4)
    # plans: top views of one floor (walls, linings, floors, room labels); Workbench does not cap cut
    # objects, so instead of cutting, everything above that floor is hidden
    for piso, cols in ((0, ["0", "1.1", "1.2", "2", "3", "4.1", "4.2", "4.4", "9"]),
                       (1, ["1.4", "1.5", "2", "3", "4.3", "4.4", "9"])):
        show([k for k in cols if k != "2"] + ["2.1", "2.2", A])
        outro = (f"P{1 - piso}.", f"PE{2 - piso}.", f"PI{2 - piso}.")
        for ob in bpy.data.objects:
            ob.hide_render = any(t in ob.name for t in outro)
        shoot(f"planta_piso{piso}.png", (c[0], c[1], 30), (c[0], c[1] + 1e-4, 0), ortho=L + 1.5)
    for ob in bpy.data.objects:
        ob.hide_render = False
else:
    show(estr)
    shoot("alcado_este.png", (L + 25, c[1], 3.5), (0, c[1], 3.5), ortho=max(L, D) + 3)
print("PREVIEW_OK", out)
