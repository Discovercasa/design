"""Blender: CC0 assets for the client page (Poly Haven, public domain; user 2026-11-18: «Sim, podes»).

Photo textures (colour, normal, roughness) and furniture/plant models (glTF) from a local folder made by
ferramentas/pagina/descarregar_ativos.py (default BOB/_trabalho/assets/polyhaven, never in Git: big binaries).
A missing folder or asset returns None and the callers keep their procedural version, so the tool runs anywhere.

    iniciar(pasta, saida)                 -> True when the folder and its manifesto.json exist
    material(nome, aid, cor, ...)          a Principled material from the asset's maps; cor moves the photo's mean
                                           colour to ours (linear light): the photo's grain, the house's colour
    tamanho_m(aid)                         the texture's real width in metres (manifest)
    prototipo(aid)                         the model imported once: parts (mesh, matrix), size, bottom centre
    colocar(aid, matriz, grupo, ligar, nome) linked copies of the parts placed by matriz (origin = bottom centre,
                                           front = +y after the caller's rotation; Poly Haven fronts face -y)
"""
import json
import os

import bpy
import numpy as np
from mathutils import Matrix, Vector

PASTA = None
MAN = {}
PROTO = {}
SAIDA = "."


def iniciar(pasta, saida):
    global PASTA, MAN, SAIDA
    SAIDA = saida
    mf = os.path.join(pasta or "", "manifesto.json")
    if pasta and os.path.exists(mf):
        PASTA = pasta
        MAN = json.load(open(mf, encoding="utf-8"))
    print("ativos CC0:", len(MAN) if PASTA else 0, PASTA or "(sem pasta: só procedimentais)")
    return bool(PASTA)


def tem(aid):
    return PASTA is not None and aid in MAN and os.path.isdir(os.path.join(PASTA, aid))


def tamanho_m(aid):
    d = MAN[aid].get("dimensoes_mm") or [2000, 2000]
    return float(d[0]) / 1000.0


def _hex_lin(h):
    h = h.lstrip("#")
    return np.array([int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4)]) ** 2.2


def _ajustar(img, nome, cor=None, contraste=1.0):
    """The photo with its mean colour moved to cor and its contrast scaled (linear light); saved as JPEG."""
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    lin = np.power(np.clip(px[:, :3], 0.0, 1.0), 2.2)
    media = np.maximum(lin.mean(0), 1e-4)
    if contraste != 1.0:
        lin = media[None, :] + (lin - media[None, :]) * contraste
    if cor:
        lin = lin * (_hex_lin(cor) / media)[None, :]
    px[:, :3] = np.power(np.clip(lin, 0.0, 1.0), 1 / 2.2)
    out = bpy.data.images.new(nome, w, h, alpha=False)
    out.pixels.foreach_set(px.ravel())
    out.update()
    os.makedirs(os.path.join(SAIDA, "texturas"), exist_ok=True)
    out.filepath_raw = os.path.join(SAIDA, "texturas", nome + ".jpg")
    out.file_format = "JPEG"
    try:
        out.save(quality=92)
    except TypeError:
        out.save()
    return out, np.power(np.clip(lin.mean(0), 0, 1), 1 / 2.2)


def material(nome, aid, cor=None, forca=1.0, rug=None, rug_mult=1.0, sheen=0.0, coat=0.0, contraste=1.0):
    if not tem(aid) or "Diffuse" not in MAN[aid]["ficheiros"]:
        return None
    f = MAN[aid]["ficheiros"]
    base = os.path.join(PASTA, aid)
    m = bpy.data.materials.new(nome)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "UVMap"
    uv.location = (-900, 0)
    ic = nt.nodes.new("ShaderNodeTexImage")
    ic.location = (-500, 250)
    img = bpy.data.images.load(os.path.join(base, f["Diffuse"]), check_existing=True)
    media = None
    if cor or contraste != 1.0:
        img, media = _ajustar(img, nome + "_cor", cor, contraste)
    ic.image = img
    nt.links.new(uv.outputs["UV"], ic.inputs["Vector"])
    nt.links.new(ic.outputs["Color"], b.inputs["Base Color"])
    if "nor_gl" in f and forca > 0:
        inn = nt.nodes.new("ShaderNodeTexImage")
        inn.location = (-500, -250)
        inn.image = bpy.data.images.load(os.path.join(base, f["nor_gl"]), check_existing=True)
        inn.image.colorspace_settings.name = "Non-Color"
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.location = (-200, -250)
        nm.inputs["Strength"].default_value = forca
        nt.links.new(uv.outputs["UV"], inn.inputs["Vector"])
        nt.links.new(inn.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    if rug is None and "Rough" in f:
        ir = nt.nodes.new("ShaderNodeTexImage")
        ir.location = (-500, 0)
        ir.image = bpy.data.images.load(os.path.join(base, f["Rough"]), check_existing=True)
        ir.image.colorspace_settings.name = "Non-Color"
        nt.links.new(uv.outputs["UV"], ir.inputs["Vector"])
        if rug_mult != 1.0:
            mul = nt.nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            mul.use_clamp = True
            mul.inputs[1].default_value = rug_mult
            mul.location = (-250, 0)
            nt.links.new(ir.outputs["Color"], mul.inputs[0])
            nt.links.new(mul.outputs[0], b.inputs["Roughness"])
        else:
            nt.links.new(ir.outputs["Color"], b.inputs["Roughness"])
    else:
        b.inputs["Roughness"].default_value = 0.6 if rug is None else rug
    for k, v in (("Sheen Weight", sheen), ("Coat Weight", coat)):
        if k in b.inputs and v:
            b.inputs[k].default_value = v
    c = media if media is not None else (np.ones(3) * 0.6)
    m.diffuse_color = (*[float(x) ** 2.2 for x in c], 1.0)
    return m


# ------------------------------------------------------------------------------------------------ models
def prototipo(aid):
    """Import the asset's glTF once; keep its meshes (custom normals untouched) and their matrices; no objects left."""
    if aid in PROTO:
        return PROTO[aid]
    if not tem(aid) or "gltf" not in MAN[aid]["ficheiros"]:
        PROTO[aid] = None
        return None
    caminho = os.path.join(PASTA, aid, MAN[aid]["ficheiros"]["gltf"])
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=caminho)
    bpy.context.view_layer.update()
    novos = [o for o in bpy.data.objects if o not in antes]
    partes, lo, hi, npol = [], np.full(3, 1e9), np.full(3, -1e9), 0
    for o in novos:
        if o.type != "MESH" or not o.data.vertices:
            continue
        mw = o.matrix_world.copy()
        o.data.use_fake_user = True
        co = np.empty(len(o.data.vertices) * 3)
        o.data.vertices.foreach_get("co", co)
        co = np.c_[co.reshape(-1, 3), np.ones(len(o.data.vertices))] @ np.array(mw).T
        lo, hi = np.minimum(lo, co[:, :3].min(0)), np.maximum(hi, co[:, :3].max(0))
        npol += len(o.data.polygons)
        partes.append((o.data, mw))
    lo, hi = Vector(lo.tolist()), Vector(hi.tolist())
    for o in novos:
        bpy.data.objects.remove(o, do_unlink=True)
    # the ceiling lamp's globe: lit from inside (frosted, glowing), the light passes (no shadow from the lamp)
    for me, _ in partes:
        for mt in me.materials:
            if mt and "globe" in mt.name.lower():
                b = next((n for n in mt.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
                if b:
                    for k in ("Emission Color", "Emission"):
                        if k in b.inputs:
                            b.inputs[k].default_value = (1.0, 0.86, 0.68, 1.0)
                            break
                    if "Emission Strength" in b.inputs:
                        b.inputs["Emission Strength"].default_value = 4.0
    PROTO[aid] = {"partes": partes, "dim": hi - lo, "base": Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)),
                  "poligonos": npol}
    print("ativo", aid, len(partes), "partes", npol, "polígonos", tuple(round(x, 2) for x in (hi - lo)))
    return PROTO[aid]


def colocar(aid, matriz, grupo, ligar, nome, sem_sombra=False):
    P = prototipo(aid)
    if P is None:
        return []
    obs = []
    centro = Matrix.Translation(-P["base"])
    for me, mw in P["partes"]:
        ob = bpy.data.objects.new(f"{nome}_{aid}", me)
        ob.matrix_basis = matriz @ Matrix.Rotation(np.pi, 4, "Z") @ centro @ mw
        ob["suave"] = True
        ob["ativo"] = aid
        if P["poligonos"] > 40000:
            ob["pesado"] = True          # no lightmap bake; decimated in the web copy
        if sem_sombra:
            ob.visible_shadow = False
        obs.append(ligar(ob, grupo))
    return obs
