"""Runs INSIDE Blender on a visit model: the interior views of interiores.json (house axes) in world coordinates,
for the Unreal cameras (Step Inside Phase 4).

    blender -b visita_interiores.blend --python blender_vistas.py -- <interiores.json> <out.json>

Writes {"vistas": [{"id", "nome", "de", "para", "lente"} in Blender world metres], "house_root": 4x4} — the Unreal side
turns Blender (x, y, z) m into Unreal (x, -y, z) cm (glTF via Interchange), checked against the imported bounds.
"""
import json
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
cfg = json.load(open(args[0], encoding="utf-8"))
raiz = bpy.data.objects["HOUSE_ROOT"]
M = raiz.matrix_world
out = {"house_root": [list(r) for r in M], "vistas": []}
for v in cfg.get("vistas", []):
    de, para = M @ Vector(v["de"]), M @ Vector(v["para"])
    out["vistas"].append({"id": v["id"], "nome": v["nome"], "de": [round(x, 4) for x in de],
                          "para": [round(x, 4) for x in para], "lente": v.get("lente", 18)})
json.dump(out, open(args[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("VISTAS_OK", len(out["vistas"]))
