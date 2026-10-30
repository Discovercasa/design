"""Runs INSIDE Blender on a saved model: quantities per collection.
    blender --background model.blend --python quantidades.py -- [output.csv]
Timber (objects with "seccao"): pieces AS DRAWN per collection and section (studs split at noggings
count as 2 pieces) - not purchase lengths.
Layers (objects with "camada"): area / length / volume per collection and layer, plus an indicative
purchase quantity from the unit size and waste in sistema_construtivo.json. Finish options B and C are
alternatives to A (not additional).
"""
import csv
import math
import sys
from collections import defaultdict

import bpy

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
tot = defaultdict(lambda: [0, 0.0, 0.0])
cam = defaultdict(lambda: {"n": 0, "comp": 0.0, "vol": 0.0, "area": 0.0, "un": "", "au": 0.0, "cu": 0.0, "desp": 0.0})
for ob in bpy.data.objects:
    if ob.type != "MESH" or not ob.users_collection:
        continue
    col = ob.users_collection[0].name
    if "seccao" in ob.keys():
        t = tot[(col, ob["seccao"])]
        t[0] += 1
        t[1] += ob.get("comprimento_m", 0.0)
        t[2] += ob.get("volume_m3", 0.0)
    elif "camada" in ob.keys():
        c = cam[(col, ob["camada"])]
        c["n"] += ob.get("pecas", 1)
        c["comp"] += ob.get("comprimento_m", 0.0)
        c["vol"] += ob.get("volume_m3", 0.0)
        c["area"] += ob.get("area_m2", 0.0)
        c["un"] = ob.get("unidade", c["un"])
        c["au"] = ob.get("area_unidade_m2", c["au"])
        c["cu"] = ob.get("comprimento_unidade_m", c["cu"])
        c["desp"] = ob.get("desperdicio", c["desp"])
rows = [[g, s, n, round(ln, 1), round(v, 3), "", "", ""] for (g, s), (n, ln, v) in sorted(tot.items())]
rows.append(["TOTAL madeira", "", sum(r[2] for r in rows), round(sum(r[3] for r in rows), 1),
             round(sum(r[4] for r in rows), 2), "", "", ""])
for (g, s), c in sorted(cam.items()):
    qtd = ""
    if c["au"]:
        qtd = math.ceil(c["area"] * (1 + c["desp"]) / c["au"])
    elif c["cu"]:
        qtd = math.ceil(c["comp"] * (1 + c["desp"]) / c["cu"])
    rows.append([g, s, c["n"], round(c["comp"], 1) or "", round(c["vol"], 3) or "", round(c["area"], 1) or "",
                 c["un"] if qtd != "" else "", qtd])
for r in rows:
    print("QTY |", " | ".join(str(x) for x in r))
if args:
    with open(args[0], "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["colecao", "seccao_ou_camada", "pecas", "comprimento_m", "volume_m3", "area_m2",
                    "unidade_compra", "quantidade_compra"])
        w.writerows(rows)
