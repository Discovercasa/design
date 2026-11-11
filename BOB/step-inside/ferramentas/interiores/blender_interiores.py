"""Runs INSIDE Blender on a visit model: furnishes it from interiores.json (Step Inside hub task 167).

    blender --background visita.blend --python blender_interiores.py -- run.json

run.json = {"pecas": [...], "catalogo": {OBJ id: object}, "modelos": {asset: gltf path}, "divisoes": {...},
            "vistas": [...], "blend": out .blend, "pasta": renders folder, "saida": summary json, "render": bool}
1. every piece in the house model's own axes, hung on HOUSE_ROOT (so it follows the house on the site): Poly Haven
   models imported once (joined, origin at the centre of the footprint on the floor) and shared by every copy;
   parametric pieces built by pecas.py;
2. set on the finished floor under it (ray down onto ARCH_FLOORS), or hung from the ceiling (ray up onto ARCH_CEILINGS);
3. checks: each piece against the walls, openings and reveals (mesh overlap), inside its room, and pairs of pieces;
4. a soft light per room, then renders: a plan from above (roof and ceilings hidden) and the eye-level views.
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

run = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
sys.path.insert(0, str(Path(sys.argv[sys.argv.index("--python") + 1]).resolve().parent))
import pecas as PC  # noqa: E402

sc = bpy.context.scene
vl = bpy.context.view_layer
OUT = {"pecas": [], "modelos": {}, "choques_paredes": [], "fora_da_divisao": [], "sobrepostas": [], "sem_chao": []}
raiz = bpy.data.objects["HOUSE_ROOT"]
RW = raiz.matrix_world.copy()
RI = RW.inverted()


def por_categoria(*cats):
    return [o for o in bpy.data.objects if o.type == "MESH" and o.get("si_categoria") in cats and o.visible_get()]


def bvh_mundo(obs):
    vs, fs, donos = [], [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in obs:
        me = o.evaluated_get(dg).to_mesh()
        n = len(vs)
        mw = o.matrix_world
        vs += [mw @ v.co for v in me.vertices]
        for p in me.polygons:
            fs.append([n + i for i in p.vertices])
            donos.append(o)
        o.evaluated_get(dg).to_mesh_clear()
    return (BVHTree.FromPolygons(vs, fs), donos) if fs else (None, [])


BV_CHAO, _ = bvh_mundo(por_categoria("ARCH_FLOORS", "ARCH_OPENINGS"))
BV_TETO, _ = bvh_mundo(por_categoria("ARCH_CEILINGS"))
BV_PAR, DONOS_PAR = bvh_mundo(por_categoria("ARCH_WALLS_EXT", "ARCH_WALLS_INT", "ARCH_OPENINGS", "ARCH_REVEALS"))


def nivel(x, y, para_cima=False):
    """Finished floor (or ceiling) height in the house's own frame under / over (x, y)."""
    p = RW @ Vector((x, y, 1.2))
    d = (RW.to_3x3() @ Vector((0, 0, 1 if para_cima else -1))).normalized()
    h = (BV_TETO if para_cima else BV_CHAO).ray_cast(p, d, 4.0)
    return (RI @ h[0]).z if h[0] is not None else None


# ------------------------------------------------------------------ materials
MATS = {}


def _lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def material(hexa, rug=0.5, alfa=1.0, metal=0.0):
    k = f"INT_{hexa.lstrip('#').upper()}_{int(rug * 100):02d}" + (f"_A{int(alfa * 100)}" if alfa < 1 else "") + (f"_M{int(metal * 10)}" if metal else "")
    if k not in MATS:
        m = bpy.data.materials.new(k)
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (*_lin(hexa), 1)
        b.inputs["Roughness"].default_value = rug
        b.inputs["Metallic"].default_value = metal
        if alfa < 1:
            b.inputs["Alpha"].default_value = alfa
            if hasattr(m, "surface_render_method"):
                m.surface_render_method = "BLENDED"
            m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
        m.diffuse_color = (*_lin(hexa), alfa)
        MATS[k] = m
    return MATS[k]


# ------------------------------------------------------------------ the collection
col = bpy.data.collections.get("INTERIORES")
if col:
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new("INTERIORES")
    pai = next((c for c in bpy.data.collections if raiz.name in c.objects), None)
    avo = next((c for c in bpy.data.collections if pai and pai.name in c.children), None)
    (avo or sc.collection).children.link(col)


# ------------------------------------------------------------------ 1. the models
def importar(asset, caminho):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=caminho)
    novos = [o for o in bpy.data.objects if o not in antes]
    malhas = [o for o in novos if o.type == "MESH"]
    me = bpy.data.meshes.new(f"PH_{asset}")
    bm = bmesh.new()
    slots = []
    for o in malhas:
        tmp = o.data.copy()
        tmp.transform(o.matrix_world)
        idx = []
        for m in tmp.materials:
            if m not in slots:
                slots.append(m)
            idx.append(slots.index(m))
        if idx:
            for p in tmp.polygons:
                p.material_index = idx[p.material_index] if p.material_index < len(idx) else 0
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    lo = Vector([min(v.co[i] for v in bm.verts) for i in range(3)])
    hi = Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
    centro = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for v in bm.verts:
        v.co -= centro
    bm.to_mesh(me)
    bm.free()
    for m in slots:
        me.materials.append(m)
    for o in novos:
        bpy.data.objects.remove(o, do_unlink=True)
    return me, [round(v, 3) for v in (hi - lo)]


def parametrico(o, medidas, param):
    me = bpy.data.meshes.new(f"PAR_{o['id']}")
    bm = bmesh.new()
    lista = []

    def mat(hexa, rug=0.5, alfa=1.0, metal=0.0):
        m = material(hexa, rug, alfa, metal)
        if m not in lista:
            lista.append(m)
        return lista.index(m)

    PC.GERADORES[o["origem"]["gerador"]](bm, *medidas, o.get("cores", {}), mat, param or {})
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for m in lista:
        me.materials.append(m)
    return me


MALHAS = {}
for asset, caminho in run["modelos"].items():
    me, dim = importar(asset, caminho)
    MALHAS[asset] = me
    OUT["modelos"][asset] = {"medidas_m": dim, "triangulos": sum(len(p.vertices) - 2 for p in me.polygons),
                             "materiais": len(me.materials)}

# ------------------------------------------------------------------ 2. place
cat = run["catalogo"]
objs = {}
for p in run["pecas"]:
    o = cat[p["obj"]]
    if o["origem"]["tipo"] == "polyhaven":
        me = MALHAS[o["origem"]["asset"]]
    else:
        me = parametrico(o, p.get("medidas") or o["medidas_m"], p.get("param"))
    ob = bpy.data.objects.new(f"INT_{p['id']}", me)
    col.objects.link(ob)
    ob.parent = raiz
    ob.matrix_parent_inverse = Matrix.Identity(4)
    x, y = p["xy"]
    piso = nivel(x, y)
    if piso is None:
        OUT["sem_chao"].append(p["id"])
        piso = 0.0
    z = piso + p.get("z", 0.0)
    if p.get("teto"):
        t = nivel(x, y, para_cima=True)
        alto = max(v.co.z for v in me.vertices)
        z = (t if t is not None else piso + 2.6) - alto
    ob.location = (x, y, z)
    ob.rotation_euler = (0, 0, PC.angulo(p.get("frente", "S")))
    ob["si_categoria"] = "INTERIORES"
    ob["si_id"] = f"INTERIORES/{p['id']}"
    ob["si_obj"] = p["obj"]
    ob["si_divisao"] = p.get("divisao", "")
    objs[p["id"]] = ob
    OUT["pecas"].append({"id": p["id"], "obj": p["obj"], "piso": round(piso, 3), "z": round(z - piso, 3),
                         "triangulos": sum(len(f.vertices) - 2 for f in me.polygons)})
vl.update()


# ------------------------------------------------------------------ 3. checks
def bvh_ob(ob, encolher=0.0):
    mw = ob.matrix_world
    me = ob.data
    vs = [mw @ v.co for v in me.vertices]
    if encolher:
        c = sum(vs, Vector()) / len(vs)
        vs = [c + (v - c) * (1 - encolher) for v in vs]
    return BVHTree.FromPolygons(vs, [list(f.vertices) for f in me.polygons])


def caixa_local(ob):
    """Footprint box of the piece in the house frame."""
    M = RI @ ob.matrix_world
    pts = [M @ v.co for v in ob.data.vertices]
    return [min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts),
            max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)]


cx = {k: caixa_local(o) for k, o in objs.items()}
for p in run["pecas"]:
    ob = objs[p["id"]]
    if BV_PAR:
        pares = bvh_ob(ob, 0.004).overlap(BV_PAR)
        if pares:
            nomes = sorted({DONOS_PAR[j].name for _, j in pares})
            OUT["choques_paredes"].append({"peca": p["id"], "com": nomes[:6]})
    d = run["divisoes"].get(p.get("divisao", ""))
    if d:
        a = cx[p["id"]]
        x0, y0, x1, y1 = d["caixa"]
        fora = max(x0 - a[0], y0 - a[1], a[3] - x1, a[4] - y1)
        if fora > 0.02:
            OUT["fora_da_divisao"].append({"peca": p["id"], "divisao": p["divisao"], "m": round(fora, 3)})
ids = list(objs)
for i, a in enumerate(ids):
    for b in ids[i + 1:]:
        A, B = cx[a], cx[b]
        ox = min(A[3], B[3]) - max(A[0], B[0])
        oy = min(A[4], B[4]) - max(A[1], B[1])
        oz = min(A[5], B[5]) - max(A[2], B[2])
        if ox > 0.03 and oy > 0.03 and oz > 0.01:
            OUT["sobrepostas"].append({"pecas": [a, b], "m": [round(ox, 3), round(oy, 3), round(oz, 3)]})
OUT["triangulos_total"] = sum(p["triangulos"] for p in OUT["pecas"])
OUT["materiais_interiores"] = len({m.name for o in objs.values() for m in o.data.materials if m})

# ------------------------------------------------------------------ 4. lights and renders
for d_id, d in run["divisoes"].items():
    x0, y0, x1, y1 = d["caixa"]
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    t = nivel(xm, ym, para_cima=True) or 2.6
    luz = bpy.data.lights.new(f"INT_LUZ_{d_id}", "AREA")
    luz.shape = "RECTANGLE"
    luz.size, luz.size_y = (x1 - x0) * 0.6, (y1 - y0) * 0.6
    luz.energy = 35.0 * (x1 - x0) * (y1 - y0)
    luz.color = (1.0, 0.94, 0.86)
    lo = bpy.data.objects.new(f"INT_LUZ_{d_id}", luz)
    col.objects.link(lo)
    lo.parent = raiz
    lo.matrix_parent_inverse = Matrix.Identity(4)
    lo.location = (xm, ym, t - 0.05)

bpy.ops.wm.save_as_mainfile(filepath=run["blend"], compress=True)

if run.get("render", True):
    pasta = Path(run["pasta"])
    pasta.mkdir(parents=True, exist_ok=True)
    motores = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in motores else "BLENDER_EEVEE"
    ee = sc.eevee
    for k, v in (("use_raytracing", True), ("taa_render_samples", 48), ("use_shadows", True), ("use_gtao", True)):
        if hasattr(ee, k):
            setattr(ee, k, v)
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
    sc.view_settings.look = "None"
    OUT["renders"] = []

    def camara(nome, de, para, lente=18, orto=None):
        cam = bpy.data.objects.new(nome, bpy.data.cameras.new(nome))
        sc.collection.objects.link(cam)
        cam.parent = raiz
        cam.matrix_parent_inverse = Matrix.Identity(4)
        cam.location = de
        cam.rotation_euler = (Vector(para) - Vector(de)).to_track_quat("-Z", "Y").to_euler()
        cam.data.clip_start, cam.data.clip_end = 0.05, 500
        if orto:
            cam.data.type = "ORTHO"
            cam.data.ortho_scale = orto
        else:
            cam.data.lens = lente
        sc.camera = cam
        return cam

    # plan from above: roof, ceilings, pergola, labels and the ceiling lamps hidden
    escondidos = []
    for o in bpy.data.objects:
        if o.get("si_categoria") in ("ARCH_ROOF", "ARCH_CEILINGS", "ARCH_PERGOLA", "ARCH_LABELS") or \
                (o.name.startswith("INT_") and o.get("si_obj") == "OBJ_CEILING_LAMP"):
            if not o.hide_render:
                o.hide_render = True
                escondidos.append(o)
    sc.render.resolution_x, sc.render.resolution_y = 1800, 1150
    sc.render.film_transparent = False
    cam = camara("INT_CAM_PLANTA", (8.75, 5.5, 25.0), (8.75, 5.5001, 0.0), orto=18.6)
    sc.render.filepath = str(pasta / "planta.png")
    bpy.ops.render.render(write_still=True)
    OUT["renders"].append("planta.png")
    for o in escondidos:
        o.hide_render = False
    bpy.data.objects.remove(cam, do_unlink=True)

    sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
    for v in run.get("vistas", []):
        de, para = list(v["de"]), list(v["para"])
        f = nivel(de[0], de[1]) or 0.0
        de[2] += f
        para[2] += f
        cam = camara(f"INT_CAM_{v['id']}", de, para, v.get("lente", 18))
        sc.render.filepath = str(pasta / f"{v['id']}.png")
        bpy.ops.render.render(write_still=True)
        OUT["renders"].append(f"{v['id']}.png")
        bpy.data.objects.remove(cam, do_unlink=True)

# ------------------------------------------------------------------ 5. the light copy for the phones (ar.py --interiores)
# Each piece down to its catalogue budget (ar_tris, Decimate) and its materials to a palette of a few flat colours
# (Scene Viewer recommends few materials; the house already has ≈ 18): the average colour of each material's base
# colour texture, grouped by k-means. The textures of the furniture do not go to the phone.
if run.get("blend_ar"):
    import numpy as np

    for o in [o for o in col.objects if o.type == "LIGHT"]:
        bpy.data.objects.remove(o, do_unlink=True)

    def cor_media(m):
        b = m.node_tree.nodes.get("Principled BSDF") if m and m.use_nodes else None
        if b is None:
            return np.array((m.diffuse_color[:3] if m else (0.6, 0.6, 0.6)), dtype=np.float32), 0.6
        rug = b.inputs["Roughness"].default_value
        ent = b.inputs["Base Color"]
        if ent.is_linked and ent.links[0].from_node.type == "TEX_IMAGE" and ent.links[0].from_node.image:
            im = ent.links[0].from_node.image
            px = np.empty(len(im.pixels), dtype=np.float32)
            im.pixels.foreach_get(px)
            c = px.reshape(-1, im.channels)[::7, :3]
            if im.colorspace_settings.name.lower().startswith("srgb"):
                c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
            return c.mean(0), rug
        return np.array(ent.default_value[:3], dtype=np.float32), rug

    usados = {m for o in col.objects if o.type == "MESH" for m in o.data.materials if m}
    cores = {m.name: cor_media(m) for m in usados}
    nomes = sorted(cores)
    X = np.array([cores[n][0] for n in nomes])
    k = min(int(run.get("paleta", 8)), len(nomes))
    centros = [X[np.argmax(X.sum(1))]]
    while len(centros) < k:   # farthest-point start, then k-means
        d = np.min([((X - c) ** 2).sum(1) for c in centros], axis=0)
        centros.append(X[int(np.argmax(d))])
    C = np.array(centros)
    for _ in range(20):
        lab = np.argmin(((X[:, None, :] - C[None]) ** 2).sum(2), axis=1)
        C = np.array([X[lab == i].mean(0) if (lab == i).any() else C[i] for i in range(k)])
    pal = []
    for i in range(k):
        m = bpy.data.materials.new(f"INT_AR_{i}")
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (*C[i], 1)
        rugs = [cores[n][1] for n, l in zip(nomes, lab) if l == i]
        b.inputs["Roughness"].default_value = float(np.mean(rugs)) if rugs else 0.6
        m.diffuse_color = (*C[i], 1)
        pal.append(m)
    mapa = {n: pal[l] for n, l in zip(nomes, lab)}
    # glass stays glass (shower screen): its own transparent material
    for n in nomes:
        m = bpy.data.materials[n]
        b = m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
        if b is not None and b.inputs["Alpha"].default_value < 1:
            mapa[n] = m
    dg = bpy.context.evaluated_depsgraph_get()
    leves, ar = {}, {"triangulos": 0, "pecas": {}}
    for p in run["pecas"]:
        ob = objs[p["id"]]
        alvo = int(cat[p["obj"]].get("ar_tris", 1500))
        chave = (ob.data.name, alvo)
        if chave not in leves:
            tri = sum(len(f.vertices) - 2 for f in ob.data.polygons)
            tmp = bpy.data.objects.new("_tmp", ob.data)
            sc.collection.objects.link(tmp)
            if tri > alvo:
                md = tmp.modifiers.new("dec", "DECIMATE")
                md.ratio = max(0.002, alvo / tri)
                md.use_collapse_triangulate = True
            dg.update()
            me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
            bpy.data.objects.remove(tmp, do_unlink=True)
            for i, m in enumerate(me.materials):
                if m is not None:
                    me.materials[i] = mapa.get(m.name, m)
            while me.uv_layers:   # flat colours: no UVs (Scene Viewer allows one UV set; the house keeps its own)
                me.uv_layers.remove(me.uv_layers[0])
            # one mesh per material: blender_ar.py bakes each object with its active material only (the house's
            # objects have one each), so a piece with several would come out in one colour and the glass opaque
            partes = []
            for m in dict.fromkeys(x for x in me.materials if x is not None):
                bm = bmesh.new()
                bm.from_mesh(me)
                bmesh.ops.delete(bm, geom=[f for f in bm.faces if me.materials[f.material_index] is not m], context="FACES")
                if bm.faces:
                    for f in bm.faces:
                        f.material_index = 0
                    mp = bpy.data.meshes.new(f"{me.name}_{m.name}")
                    bm.to_mesh(mp)
                    mp.materials.append(m)
                    partes.append(mp)
                bm.free()
            leves[chave] = partes or [me]
        partes = leves[chave]
        ob.data = partes[0]
        for i, mp in enumerate(partes[1:], 1):
            extra = bpy.data.objects.new(f"{ob.name}.{i}", mp)
            col.objects.link(extra)
            extra.parent = raiz
            extra.matrix_parent_inverse = Matrix.Identity(4)
            extra.matrix_basis = ob.matrix_basis.copy()
            for k in ("si_categoria", "si_obj", "si_divisao"):
                extra[k] = ob[k]
            extra["si_id"] = f"{ob['si_id']}.{i}"
        t = sum(len(f.vertices) - 2 for mp in partes for f in mp.polygons)
        ar["pecas"][p["id"]] = t
        ar["triangulos"] += t
    ar["materiais"] = sorted({m.name for o in col.objects if o.type == "MESH" for m in o.data.materials if m})
    OUT["ar"] = ar
    bpy.ops.wm.save_as_mainfile(filepath=run["blend_ar"], compress=True)

json.dump(OUT, open(run["saida"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("INTERIORES_OK")
