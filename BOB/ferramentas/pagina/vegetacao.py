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
TECNICA = a[a.index("--tecnica") + 1] if "--tecnica" in a else "cartoes"
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


def juntar(objs):
    objs = [o for o in objs if o]
    if len(objs) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.join()
    return objs[0] if objs else None


def imagem_da_folha(lf):
    """The leaf material's colour image node (its Color and Alpha sockets feed the Principled)."""
    m = next(m for m in lf.data.materials if folha(m))
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    no = b.inputs["Base Color"].links[0].from_node
    while no.type != "TEX_IMAGE" and no.inputs and any(i.is_linked for i in no.inputs):
        no = next(i for i in no.inputs if i.is_linked).links[0].from_node
    return no.image


def atlas_de_folhas(lf, centros, chaves, cont, v, lado, px):
    """Renders lado x lado leaf sprays of the scan itself (orthographic, emission = the leaf colour, alpha kept) into
    one atlas image: each tile is a cube of side v cut out of the crown by the camera's clip planes."""
    img = imagem_da_folha(lf)
    tmp = bpy.data.materials.new("so_cor")
    tmp.use_nodes = True
    nt = tmp.node_tree
    nt.nodes.clear()
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    em, tr, mx = nt.nodes.new("ShaderNodeEmission"), nt.nodes.new("ShaderNodeBsdfTransparent"), nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tx.outputs["Color"], em.inputs["Color"])
    nt.links.new(tx.outputs["Alpha"], mx.inputs["Fac"])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    guardados = list(lf.data.materials)
    for i in range(len(lf.data.materials)):
        lf.data.materials[i] = tmp
    cena = bpy.context.scene
    cena.render.engine = "CYCLES"
    cena.cycles.samples = 16
    cena.cycles.use_denoising = False
    cena.render.film_transparent = True
    cena.render.resolution_x = cena.render.resolution_y = px
    cena.view_settings.view_transform = "Standard"
    cena.render.image_settings.file_format = "PNG"
    cena.render.image_settings.color_mode = "RGBA"
    w = bpy.data.worlds.new("preto")
    w.color = (0, 0, 0)
    cena.world = w
    cam = bpy.data.objects.new("cam_atlas", bpy.data.cameras.new("cam_atlas"))
    cena.collection.objects.link(cam)
    cena.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = v
    import numpy as np
    rng = np.random.default_rng(11)
    # tiles from cubes spread over the density range (sparse edge to dense core), so each cube can get a spray as
    # full as its own leaves: dense tiles everywhere made the crown a dark solid block (first test)
    ok = np.nonzero(cont >= 3)[0]
    ordem = ok[np.argsort(cont[ok])]
    escolha = ordem[np.linspace(len(ordem) * 0.15, len(ordem) - 1, lado * lado).astype(int)]
    atl = np.zeros((lado * px, lado * px, 4), dtype=np.float32)
    for k, iv in enumerate(escolha):
        c = centros[chaves == iv].mean(axis=0)
        ang = rng.uniform(0, 2 * math.pi)
        d = np.array([math.cos(ang), math.sin(ang), 0.0])
        dist = 5.0
        pos = c + d * dist
        cam.location = pos.tolist()
        cam.rotation_euler = (math.pi / 2, 0, ang + math.pi / 2)  # looks along -d, horizontal
        cam.data.clip_start, cam.data.clip_end = dist - v / 2, dist + v / 2
        cam.data.ortho_scale = v
        f = os.path.join(SAIDA, f"_tile_{k}.png")
        cena.render.filepath = f
        bpy.ops.render.render(write_still=True)
        t = bpy.data.images.load(f)
        p = np.empty(px * px * 4, dtype=np.float32)
        t.pixels.foreach_get(p)
        bpy.data.images.remove(t)
        os.remove(f)
        p = p.reshape(px, px, 4)
        # the leaf texture also carries twig and bark slivers: near-black in the render, they showed as dark polygons
        # round the crown — cut them out (the leaves are far brighter)
        lum = 0.2126 * p[..., 0] + 0.7152 * p[..., 1] + 0.0722 * p[..., 2]
        p[..., 3] = np.where(lum < 0.03, 0.0, p[..., 3])
        r, col = divmod(k, lado)
        atl[r * px:(r + 1) * px, col * px:(col + 1) * px] = p  # rows bottom-up, as the UVs
    for i, m in enumerate(guardados):
        lf.data.materials[i] = m
    a = bpy.data.images.new(f"{AID}_folhas_atlas", lado * px, lado * px, alpha=True)
    a.pixels.foreach_set(atl.ravel())
    a.filepath_raw = os.path.join(SAIDA, f"{AID}_folhas_atlas.png")
    a.file_format = "PNG"
    a.save()
    return a, cont[escolha]


def cartoes(lf, orc_folhas, lado=4, px=512):
    """Leaf-cluster cards: the crown cut into cubes of side v (as large as the budget needs); in each occupied cube a
    quad at the leaves' centre (two crossed in the cubes twice as dense as the median), textured with one of the
    scan's own leaf sprays chosen by density (as many leaves as the cube really has), normals pointing out of the
    crown (soft foliage light). Replaces the leaf object; returns the cube side."""
    import numpy as np
    n = len(lf.data.polygons)
    centros = np.empty(n * 3, dtype=np.float32)
    lf.data.polygons.foreach_get("center", centros)
    centros = centros.reshape(n, 3)
    lo = centros.min(axis=0)
    v = 0.25
    while True:
        ijk = np.floor((centros - lo) / v).astype(np.int64)
        chave = ijk[:, 0] * 1_000_003 + ijk[:, 1] * 1009 + ijk[:, 2]
        uniq, inv, cont = np.unique(chave, return_inverse=True, return_counts=True)
        ocup = (cont >= 3).sum()
        if ocup * 2 * 1.3 <= orc_folhas or v > 3:  # one card (2 triangles) per cube, a second in the dense ones
            break
        v *= 1.15
    atlas, dens_tile = atlas_de_folhas(lf, centros, inv, cont, v, lado, px)
    ordem_t = np.argsort(dens_tile)
    mediana = float(np.median(cont[cont >= 3]))
    meio = centros.mean(axis=0)
    rng = np.random.default_rng(5)
    verts, faces, uvs, normais = [], [], [], []
    s = v * 0.5  # half size = the cube: each tile shows exactly its cube's leaves (larger cards stacked them 2.5x)
    for iv in np.nonzero(cont >= 3)[0]:
        c = centros[inv == iv].mean(axis=0)
        yaw = rng.uniform(0, math.pi)
        tilt = rng.uniform(-0.35, 0.35)
        out = c - meio
        nrm = out / (np.linalg.norm(out) + 1e-6)
        n_i = cont[iv]
        perto = ordem_t[np.argsort(np.abs(np.log(dens_tile[ordem_t] / n_i)))[:3]]  # the 3 tiles nearest in density
        for q in ((0, math.pi / 2) if n_i > 2 * mediana else (0,)):
            a = yaw + q
            ux = np.array([math.cos(a), math.sin(a), 0.0])
            uz = np.array([-math.sin(a) * math.sin(tilt), math.cos(a) * math.sin(tilt), math.cos(tilt)])
            b = len(verts)
            for du, dv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                verts.append((c + ux * du * s + uz * dv * s).tolist())
                normais.append(nrm.tolist())
            faces.append((b, b + 1, b + 2, b + 3))
            t = int(rng.choice(perto))
            r, col = divmod(t, lado)
            u0, v0 = col / lado, r / lado
            uvs += [(u0, v0), (u0 + 1 / lado, v0), (u0 + 1 / lado, v0 + 1 / lado), (u0, v0 + 1 / lado)]
    me = bpy.data.meshes.new(f"{AID}_cartoes")
    me.from_pydata(verts, [], faces)
    uvl = me.uv_layers.new(name="UVMap")
    for i, uv in enumerate(uvs):
        uvl.data[i].uv = uv
    me.normals_split_custom_set_from_vertices(normais)
    mat = bpy.data.materials.new(f"{AID}_folhas_cartoes")
    mat.use_nodes = True
    mat.use_backface_culling = False
    try:
        mat.blend_method = "CLIP"  # older exporters read it; newer ones read the Math cut below
    except (AttributeError, TypeError):
        pass
    nt = mat.node_tree
    b = next(x for x in nt.nodes if x.type == "BSDF_PRINCIPLED")
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = atlas
    corte = nt.nodes.new("ShaderNodeMath")
    corte.operation = "GREATER_THAN"
    corte.inputs[1].default_value = 0.5
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tx.outputs["Alpha"], corte.inputs[0])
    nt.links.new(corte.outputs[0], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.6
    me.materials.append(mat)
    ob = bpy.data.objects.new(f"{AID}_cartoes", me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.data.objects.remove(lf)
    return ob, v


relatorio = {"id": AID, "fonte": f"https://polyhaven.com/a/{AID}", "licenca": "CC0", "niveis": {},
             "tecnica": TECNICA}
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
        if TECNICA == "cartoes":
            lf, v = cartoes(juntar(folhas), resto)
            folhas = [lf]
            relatorio.setdefault("cubo_m", {})[nome] = round(v, 3)
        else:
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
