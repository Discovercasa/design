"""Blender: light versions of a photo-scanned CC0 plant (Poly Haven) for real-time use — the VR and the web 3D — that
keep the scan's own leaves, bark and silhouette (user 2026-11-26: «a vegetação deverá ter um aspeto mais real também
e não parecerem árvores modeladas deliberadamente»).

    blender -b --factory-startup -P ferramentas/pagina/vegetacao.py -- <polyhaven folder> <asset id> <out folder>
            [--niveis vr:60000,web:15000] [--escala_max 2]

The full scan (often 1–4 million triangles, every leaf a small card with an alpha texture) stays for Cycles (images,
360° tour). Each level keeps the triangle budget it is given:
- trunk and branches (the materials without alpha): Decimate (collapse) to a quarter of the budget;
- leaves (the material whose alpha is textured): whole leaf cards are kept at random (Geometry Nodes: Mesh Island →
  Random Value per island → Delete Geometry), and each kept card grows by 1/sqrt(share) about its own centre (Scale
  Elements), so the crown keeps its density and outline while the leaves stay the scan's real leaves.
  Growth is capped at --escala_max (default 2): first test (island_tree_02, 2026-11-26), at 60k and 15k triangles the
  leaves grew 4x and 8x and the tree read as another species. Past the cap the level goes over its budget (reported).
  The real fix for small budgets is leaf-cluster cards (cards textured with renders of the scan's own leaf sprays, as
  game trees are made) — still to do.
Writes <out>/<id>_<level>.glb (textures at 1k for "web", 2k otherwise) and <out>/<id>_niveis.json (triangles per
level).
"""
import json
import math
import os
import sys

import bpy

a = sys.argv[sys.argv.index("--") + 1:]
PASTA, AID, SAIDA = a[0], a[1], a[2]
NIVEIS = {"vr": 60000, "web": 15000}
if "--niveis" in a:
    NIVEIS = {k: int(v) for k, v in (p.split(":") for p in a[a.index("--niveis") + 1].split(","))}
ESC_MAX = float(a[a.index("--escala_max") + 1]) if "--escala_max" in a else 2.0
os.makedirs(SAIDA, exist_ok=True)


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def folha(m):
    """A leaf material: its Principled Alpha comes from a texture."""
    if not m or not m.use_nodes:
        return False
    b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    return bool(b and b.inputs["Alpha"].is_linked)


def carregar():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    pasta = os.path.join(PASTA, AID)
    g = next(f for f in os.listdir(pasta) if f.endswith(".gltf"))
    bpy.ops.import_scene.gltf(filepath=os.path.join(pasta, g))
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in objs:  # apply transforms so every level shares one frame
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return objs


def separar_por_folha(o):
    """Split one object into (bark part, leaf part) by material."""
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")
    idx_folha = {i for i, m in enumerate(o.data.materials) if folha(m)}
    for p in o.data.polygons:
        p.select = p.material_index in idx_folha
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.separate(type="SELECTED")
    bpy.ops.object.mode_set(mode="OBJECT")
    partes = [x for x in bpy.context.selected_objects]
    lf = next((x for x in partes if x is not o), None)
    return o, lf


def rarear(o, parte):
    """Keep a share `parte` of the leaf cards, each grown by 1/sqrt(parte) about its centre."""
    ng = bpy.data.node_groups.new("rarear", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n = ng.nodes
    ent, sai = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    ilha = n.new("GeometryNodeInputMeshIsland")
    rnd = n.new("FunctionNodeRandomValue")
    rnd.data_type = "BOOLEAN"
    rnd.inputs["Probability"].default_value = 1.0 - parte  # True = delete
    rnd.inputs["Seed"].default_value = 7
    apagar = n.new("GeometryNodeDeleteGeometry")
    apagar.domain = "FACE"
    esc = n.new("GeometryNodeScaleElements")
    esc.domain = "FACE"
    esc.inputs["Scale"].default_value = 1.0 / math.sqrt(parte)
    L = ng.links
    L.new(ilha.outputs["Island Index"], rnd.inputs["ID"])
    L.new(ent.outputs[0], apagar.inputs["Geometry"])
    L.new(rnd.outputs[3], apagar.inputs["Selection"])  # the boolean output
    L.new(apagar.outputs["Geometry"], esc.inputs["Geometry"])
    L.new(esc.outputs["Geometry"], sai.inputs[0])
    mod = o.modifiers.new("rarear", "NODES")
    mod.node_group = ng
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=mod.name)


def dizimar(o, alvo):
    t = tris(o)
    if t <= alvo:
        return
    mod = o.modifiers.new("diz", "DECIMATE")
    mod.ratio = max(alvo / t, 0.002)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=mod.name)


relatorio = {"id": AID, "fonte": f"https://polyhaven.com/a/{AID}", "licenca": "CC0", "niveis": {}}
objs = carregar()
relatorio["niveis"]["completo"] = sum(tris(o) for o in objs)
for nome, orc in NIVEIS.items():
    objs = carregar()
    casca, folhas = [], []
    for o in objs:
        c, f = separar_por_folha(o)
        casca.append(c)
        if f:
            folhas.append(f)
    t_casca = sum(tris(o) for o in casca)
    t_folhas = sum(tris(o) for o in folhas)
    alvo_casca = min(t_casca, orc // 4) if folhas else orc
    for o in casca:
        dizimar(o, max(200, int(alvo_casca * tris(o) / max(t_casca, 1))))
    resto = orc - sum(tris(o) for o in casca)
    if folhas and t_folhas > resto:
        parte = max(resto / t_folhas, 1.0 / ESC_MAX ** 2)
        for o in folhas:
            rarear(o, parte)
    total = sum(tris(o) for o in casca + folhas)
    relatorio["niveis"][nome] = total
    res = "1k" if nome == "web" else "2k"
    for img in bpy.data.images:  # the web level: halve the 2k textures
        if res == "1k" and img.size[0] > 1024:
            img.scale(img.size[0] // 2, img.size[1] // 2)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=os.path.join(SAIDA, f"{AID}_{nome}.glb"), export_format="GLB",
                              use_selection=True, export_apply=True)
    print("VEG", AID, nome, total)
with open(os.path.join(SAIDA, f"{AID}_niveis.json"), "w", encoding="utf-8") as fh:
    json.dump(relatorio, fh, indent=1)
print("VEG_OK", json.dumps(relatorio))
