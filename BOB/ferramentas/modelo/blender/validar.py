"""Runs INSIDE Blender on a saved model: geometric sanity checks.
    blender --background model.blend --python validar.py -- geometria.json [camadas.json | -]
Structure (collection 1): nothing above the roof, below the slab or outside the footprint (the purlins of
collection 1.9 may overhang the gables). Layers: exterior (2) outside the frame and under the roof
covering; interior, floors, ceilings (3-5) inside the footprint and under the roof; roof covering
(6.1-6.2) on or above its supports.
Roof plane: top of the rafters (drawings' structure) or underside of the panels = top of the purlins
(DiscoverCasa structure, geometry "cobertura.sistema" = "discovercasa").
"""
import json
import math
import re
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
G = json.load(open(args[0], encoding="utf-8"))
K = json.load(open(args[1], encoding="utf-8")) if len(args) > 1 and args[1] != "-" else {}
L, D = G["casa"]["comprimento"], G["casa"]["profundidade"]
C = G["cobertura"]
DC = C.get("sistema") == "discovercasa"
yr, tn = C["cumeeira_y"], math.tan(math.radians(C["inclinacao"]))
z_estr = C["plano_z_cume"] if DC else C["cumeeira_z"]  # highest allowed plane for the structure
z_cob = K.get("z_cobertura_cume", z_estr)             # underside of the roof covering on the ridge line
tol = 0.01 if DC else 0.03
FACES = C.get("faces") if C.get("tipo") == "a_vista" else None  # an exposed roof of several slopes (casa_planta.py)


def z_faces(x, y, junta=max):
    """The exposed roof's plane (top of the purlins = underside of the panels) above (x, y), or None outside it; where
    faces meet at a step (a verge over a lower eave) `junta` picks the higher or the lower."""
    zs = []
    for f in FACES:
        p, n = f["pts"], len(f["pts"])
        # within 0,1 mm of the face (Blender keeps the vertices in 32-bit floats: a point on the edge may fall just out)
        if all(((p[(i + 1) % n][0] - p[i][0]) * (y - p[i][1]) - (p[(i + 1) % n][1] - p[i][1]) * (x - p[i][0])) >=
               -1e-4 * math.hypot(p[(i + 1) % n][0] - p[i][0], p[(i + 1) % n][1] - p[i][1]) for i in range(n)):
            zs.append(f["z0"] + f["gx"] * x + f["gy"] * y)
    return junta(zs) if zs else None


def acima(w, z_ref, folga):
    """Above the roof plane: the single-ridge plane, or the exposed roof's faces."""
    if FACES:
        z = z_faces(w.x, w.y)
        return z is not None and w.z > z + folga
    return w.z > z_ref - tn * abs(w.y - yr) + folga


def cid(ob):
    m = re.match(r"(\d+(?:\.\d+)*) ", ob.users_collection[0].name) if ob.users_collection else None
    return m.group(1) if m else ""


CONT = G.get("contorno_estrutura")  # houses built from a plan: real outline of the exterior frames
# box of the house: the frame outline when known (the module drawings may differ by mm from the architecture)
X0, X1 = (min(0.0, min(x for x, _y in CONT)), max(L, max(x for x, _y in CONT))) if CONT else (0.0, L)
Y0, Y1 = (min(0.0, min(y for _x, y in CONT)), max(D, max(y for _x, y in CONT))) if CONT else (0.0, D)


def dentro_contorno(x, y, folga=0.002):
    """Strictly inside the frame outline (more than `folga` from its edges)."""
    dentro_ = False
    n = len(CONT)
    for i in range(n):
        (x1, y1), (x2, y2) = CONT[i], CONT[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            dentro_ = not dentro_
        # distance to the edge (axis-parallel edges)
        if abs(x1 - x2) < 1e-9 and min(y1, y2) - folga <= y <= max(y1, y2) + folga and abs(x - x1) < folga:
            return False
        if abs(y1 - y2) < 1e-9 and min(x1, x2) - folga <= x <= max(x1, x2) + folga and abs(y - y1) < folga:
            return False
    return dentro_


issues, n, grupos = [], 0, {}
for ob in bpy.data.objects:
    if ob.type != "MESH":
        continue
    n += 1
    c = cid(ob)
    g = c.split(".")[0]
    grupos[g] = grupos.get(g, 0) + 1
    ws = [ob.matrix_world @ v.co for v in ob.data.vertices]
    if g in ("0", ""):
        continue
    if g == "1" or c == K.get("colecao_osb_pavimento"):
        if ob.name.startswith(("Fundação", "Cobertura")):
            continue
        for w in ws:
            if acima(w, z_estr, tol):
                issues.append(("structure above roof", ob.name, round(w.y, 3), round(w.z, 3)))
                break
            if w.z < -0.001:
                issues.append(("structure below slab", ob.name, round(w.z, 3)))
                break
            # 1.9 runs over the parapets; 1.10 is the pergola, outside the house
            if c not in ("1.9", "1.10") and not (-0.05 <= w.x <= L + 0.05 and -0.05 <= w.y <= D + 0.05):
                issues.append(("structure outside footprint", ob.name, round(w.x, 3), round(w.y, 3)))
                break
    elif g == "2":
        sobre_cobertura = "Fachada Encosto" in ob.name  # a gable over a lower roof: over the house's footprint
        for w in ws:
            if not sobre_cobertura and (dentro_contorno(w.x, w.y) if CONT else (0.002 < w.x < L - 0.002 and 0.002 < w.y < D - 0.002)):
                issues.append(("exterior layer inside the frame", ob.name, round(w.x, 3), round(w.y, 3)))
                break
            if acima(w, z_cob, 0.003) or w.z < -0.001:
                issues.append(("exterior layer above the roof covering / below slab", ob.name, round(w.y, 3), round(w.z, 3)))
                break
    elif g in ("3", "4", "5"):
        for w in ws:
            if not (X0 - 0.002 <= w.x <= X1 + 0.002 and Y0 - 0.002 <= w.y <= Y1 + 0.002) or w.z < -0.001:
                issues.append(("interior layer outside the house", ob.name, round(w.x, 3), round(w.y, 3), round(w.z, 3)))
                break
            if acima(w, z_estr, 0.003):
                issues.append(("interior layer above the roof structure", ob.name, round(w.y, 3), round(w.z, 3)))
                break
    elif c in ("6.1", "6.2") and C.get("tipo") == "platibanda":
        for w in ws:  # hidden roof: on or above the purlin plane of its slope
            for t in C["telhados"]:
                if t["x0"] - 0.01 <= w.x <= t["x1"] + 0.01 and min(t["y_baixo"], t["y_cume"]) - 0.01 <= w.y <= \
                        max(t["y_baixo"], t["y_cume"]) + 0.01:
                    if w.z < t["z_cume"] - t["inclinacao"] * abs(w.y - t["y_cume"]) - 0.003:
                        issues.append(("roof covering below its supports", ob.name, round(w.y, 3), round(w.z, 3)))
                    break
            else:
                continue
            if issues and issues[-1][1] == ob.name:
                break
    elif c in ("6.1", "6.2") and FACES:
        for w in ws:  # exposed roof: on or above the purlin plane of its face
            z = z_faces(w.x, w.y, min)
            if z is not None and w.z < z - 0.003:
                issues.append(("roof covering below its supports", ob.name, round(w.y, 3), round(w.z, 3)))
                break
    elif c in ("6.1", "6.2"):
        for w in ws:
            if w.z < (z_cob if DC else z_estr) - tn * abs(w.y - yr) - 0.003:
                issues.append(("roof covering below its supports", ob.name, round(w.y, 3), round(w.z, 3)))
                break
print(f"VALIDATE checked {n} objects ({', '.join(f'{k}: {v}' for k, v in sorted(grupos.items()))}); issues: {len(issues)}")
for i in issues[:50]:
    print("VALIDATE  ", i)
