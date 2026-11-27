"""The extending table (MESA_EXTENSIVEL) in Blender, ultra-realistic, for its web page (user 2026-11-27: «quero torna-la
ultra realista com a maior qualidade possível!!»). One run builds the scene, bakes the light and writes everything the
page needs; the same scene renders the Cycles reference images the page is compared with.

    blender -b --factory-startup --python ferramentas/movel/blender_mesa.py -- <pasta> [opções]
      <pasta>             _trabalho/moveis/mesa_extensivel (geometria.json from extrair_pagina.py); output in <pasta>/saida
      --ativos <pasta>    the CC0 assets (default BOB/_trabalho/assets/polyhaven)
      --luz               bake: room lightmaps (day, night), environment panoramas, contact shadows
      --amostras 512      bake samples (the panoramas use the same; contact shadows 128); --lm_escala 0.25: small
                          lightmaps (a quick test of the page)
      --previa a,b        Cycles reference images of these views (geral, frente, lado, cima, pormenor, baixo), day and
                          night, table A closed with its chairs; --amostras_previa 256; --meia (half size)
      --guardar           also save the .blend (for inspection); --sem_exportar: previews only

What is built (Blender axes: x = the table's length, y = its width, z up; three.js = (x, z, -y)):
- the table, 4 variants, from the STEP tessellation of the source page (1 mm round edges, ~3 degrees per segment on the
  curves): welded, smooth by angle (35 degrees); the parts shared by both halves (base, middle layer, apron) cut at x = 0
  with their cut faces closed, so the table opens without showing a hollow part; texture UVs in metres with the grain
  along the construction (tops along the length, the top's edge banding along the edge — an arc-length coordinate —,
  legs vertical) and a different region of the veneer for each panel; the 500 mm extension leaf (3 layers).
- our dining chair: the source page's idea made for real (upholstered curved back band, cushion with a piped edge, oak
  frame with tapered legs; the back legs run up into the band).
- the room of the source page (7.2 x 5.8 x 2.8 m, a 3.2 x 2.1 m window), real: oak floor, plaster walls and ceiling,
  skirting, an aluminium window, Poly Haven sideboard, vases and plant, a rug, a framed print, the bronze linear pendant;
  outside, a lawn, trees (our leaf-card trees) and the photographed sky.
- light: the photographed sky (its sun capped) and a sun lamp in the source page's direction; at night three spots in the
  pendant and its glowing diffuser.
Bakes (--luz), split so that what moves in the page (table, chairs) and the light that must cast their shadows stay real
time: lm_<modo>_<grupo>.jpg = (direct + bounced) - (direct of the real-time lights) for the room ('sala', 'moveis'); the
outside ('fora') keeps everything. env_<modo>.hdr: the room seen from the table (no table, no chairs) for the table's
reflections and ambient light. sombra_<V>_<n>.png / sombra_cadeira.png: ambient occlusion of the table (variant V, n
leaves) and of a chair on the floor. luz.json: K of each lightmap (the page multiplies by pi*K), sun and spots.
"""
import hashlib
import json
import math
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Vector

ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
try:
    sys.stdout.reconfigure(line_buffering=True)        # the log shows each step as it happens (runs over SSH)
except Exception:  # noqa: BLE001
    pass
AQUI = os.path.dirname(os.path.abspath(__file__))


def opc(nome, padrao=None):
    return ARGV[ARGV.index(nome) + 1] if nome in ARGV else padrao


PASTA = os.path.abspath(ARGV[0])
SAIDA = os.path.join(PASTA, "saida")
TEX = os.path.join(SAIDA, "tex")
os.makedirs(TEX, exist_ok=True)
ATIVOS = os.path.abspath(opc("--ativos", os.path.join(AQUI, "..", "..", "_trabalho", "assets", "polyhaven")))
CFG = json.load(open(os.path.join(AQUI, "mesa_extensivel.json"), encoding="utf-8"))
GEO = json.load(open(os.path.join(PASTA, "geometria.json"), encoding="utf-8"))
AMOSTRAS = int(opc("--amostras", 512))
SALA, LUZ, ACAB = CFG["sala"], CFG["luz"], CFG["acabamentos"]
RW, RD, RH, T = SALA["largura"], SALA["fundo"], SALA["altura"], SALA["parede"]
LEAF = 0.5

bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene
cena.unit_settings.system = "METRIC"
cena.render.engine = "CYCLES"
cena.view_settings.view_transform = "AgX"
cena.view_settings.look = "None"
cena.view_settings.exposure = float(LUZ.get("exposicao", 0.0))


def colecao(nome, pai=None):
    c = bpy.data.collections.new(nome)
    (pai or cena.collection).children.link(c)
    return c


def semente(txt):
    return int(hashlib.md5(txt.encode()).hexdigest()[:8], 16)


def srgb_lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


# ---------------------------------------------------------------------------------------------- procedural textures
def gravar_img(nome, arr, nao_cor=True, fmt="PNG"):
    """arr (h, w, 3|4) floats 0..1 -> image file in TEX and a Blender image."""
    h, w = arr.shape[:2]
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :arr.shape[2]] = arr[..., :4]
    img = bpy.data.images.new(nome, w, h, alpha=False)
    if nao_cor:
        img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(rgba[::-1].ravel())
    ext = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}[fmt]
    img.filepath_raw = os.path.join(TEX, f"{nome}.{ext}")
    img.file_format = fmt
    img.save()
    return img


def normal_de_altura(h, forca):
    gy, gx = np.gradient(h)
    n = np.dstack([-gx * forca, gy * forca, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


def ruido_suave(n, celulas, rng):
    g = rng.random((celulas + 1, celulas + 1))
    x = np.linspace(0, celulas, n, endpoint=False)
    i = x.astype(int)
    f = x - i
    f = f * f * (3 - 2 * f)
    a = g[i][:, i] * (1 - f)[None, :] + g[i][:, (i + 1) % (celulas + 1)] * f[None, :]
    b = g[(i + 1) % (celulas + 1)][:, i] * (1 - f)[None, :] + g[(i + 1) % (celulas + 1)][:, (i + 1) % (celulas + 1)] * f[None, :]
    return a * (1 - f)[:, None] + b * f[:, None]


def texturas_proprias():
    """Our own maps (no free scan fits): brushed metal (fine lines along v + soft roughness patches), powder coat
    (fine orange peel), lacquer (very soft orange peel), and the linen recoloured to the chair's greige (the Poly Haven
    linen is dyed blue; its weave stays, its colour is ours)."""
    rng = np.random.default_rng(7)
    n = 1024
    linhas = rng.normal(0, 1, (1, n)).repeat(n, 0)                   # one value per column: lines along v
    linhas += 0.35 * rng.normal(0, 1, (n, n)) * (rng.random((n, n)) < 0.02)
    k = np.exp(-np.linspace(-3, 3, 9) ** 2)
    k /= k.sum()
    for _ in range(2):
        linhas = np.apply_along_axis(lambda c: np.convolve(c, k, "same"), 0, linhas)
    gravar_img("escovado_nor", normal_de_altura(linhas * 0.02, 6.0))
    manchas = ruido_suave(n, 6, rng) * 0.6 + ruido_suave(n, 23, rng) * 0.4
    gravar_img("escovado_rug", np.dstack([0.85 + 0.3 * manchas] * 3))
    casca = ruido_suave(n, 90, rng) * 0.6 + ruido_suave(n, 180, rng) * 0.4
    gravar_img("po_nor", normal_de_altura(casca, 1.6))
    gravar_img("laca_nor", normal_de_altura(ruido_suave(n, 40, rng), 0.35))
    # the linen: luminance of the scan x the greige
    src = bpy.data.images.load(os.path.join(ATIVOS, CFG["tecido"]["tex"], "Diffuse.jpg"))
    w, h = src.size
    px = np.array(src.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
    lum = px @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    lum = lum / max(float(lum.mean()), 1e-4)
    alvo = np.array(srgb_lin(CFG["tecido"]["cor"]), dtype=np.float32)
    lin = np.clip(lum[..., None] ** 0.8 * alvo, 0, 1)
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    img = gravar_img("linho_cor", srgb[::-1], nao_cor=False, fmt="JPEG")
    bpy.data.images.remove(src)
    return img


# ---------------------------------------------------------------------------------------------- materials
def no(nt, tipo, x=0, y=0):
    n = nt.nodes.new(tipo)
    n.location = (x, y)
    return n


def cor_normalizada(d, alvo, nome, variacao=1.0):
    """A scan's colour map scaled channel by channel so that its mean is `alvo` (linear), saved as TEX/<nome>_cor.jpg:
    the plaster scan is grey concrete, the walls are a warm white; the lawn is brown-green, ours a real lawn's albedo.
    A JPEG of our own instead of a colour multiply, so the GLB carries it as it is."""
    src = bpy.data.images.load(os.path.join(d, "Diffuse.jpg"))
    w, h = src.size
    px = np.array(src.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
    lin = np.where(px <= 0.04045, px / 12.92, ((px + 0.055) / 1.055) ** 2.4)
    media = np.maximum(lin.reshape(-1, 3).mean(0), 1e-4)
    lin = media + (lin - media) * variacao           # painted plaster: the scan's blotches softened (concrete otherwise)
    lin *= np.array(srgb_lin(alvo), dtype=np.float32) / media
    lin = np.clip(lin, 0, 1)
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    bpy.data.images.remove(src)
    return gravar_img(f"{nome}_cor", srgb[::-1], nao_cor=False, fmt="JPEG")


def mat_pbr(nome, pasta=None, tamanho=1.0, cor=None, rug=(0.5, 0.5), normal=1.0, metal=0.0, verniz=None,
            imagem_cor=None, nor_proprio=None, rug_proprio=None, anis=0.0, emissao=None, variacao=1.0):
    """Principled material; `pasta` holds Diffuse/nor_gl/Rough (Poly Haven names); rug = (min, max) the roughness map is
    remapped to; verniz = (weight, roughness) of a clear coat; anis = brushed-metal anisotropy along v."""
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    uv = no(nt, "ShaderNodeUVMap", -1200, 0)
    uv.uv_map = "UVMap"
    mp = no(nt, "ShaderNodeMapping", -1000, 0)
    mp.inputs["Scale"].default_value = (1 / tamanho, 1 / tamanho, 1)
    nt.links.new(uv.outputs[0], mp.inputs[0])

    def img(caminho, nao_cor, x, y):
        t = no(nt, "ShaderNodeTexImage", x, y)
        t.image = bpy.data.images.load(caminho, check_existing=True)
        if nao_cor:
            t.image.colorspace_settings.name = "Non-Color"
        nt.links.new(mp.outputs[0], t.inputs[0])
        return t

    if pasta:
        d = os.path.join(ATIVOS, pasta)
        if cor:                         # the scan's texture brought to our colour (mean), its variation kept
            tc = no(nt, "ShaderNodeTexImage", -700, 300)
            tc.image = cor_normalizada(d, cor, nome, variacao)
            nt.links.new(mp.outputs[0], tc.inputs[0])
        else:
            tc = img(os.path.join(d, "Diffuse.jpg"), False, -700, 300)
        nt.links.new(tc.outputs[0], b.inputs["Base Color"])
        tr = img(os.path.join(d, "Rough.jpg"), True, -700, 0)
        mr = no(nt, "ShaderNodeMapRange", -400, 0)
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = rug
        nt.links.new(tr.outputs[0], mr.inputs[0])
        nt.links.new(mr.outputs[0], b.inputs["Roughness"])
        tn = img(os.path.join(d, "nor_gl.jpg"), True, -700, -300)
        nm = no(nt, "ShaderNodeNormalMap", -400, -300)
        nm.inputs["Strength"].default_value = normal
        nt.links.new(tn.outputs[0], nm.inputs["Color"])
        nt.links.new(nm.outputs[0], b.inputs["Normal"])
    else:
        if imagem_cor is not None:
            t = no(nt, "ShaderNodeTexImage", -700, 300)
            t.image = imagem_cor
            nt.links.new(mp.outputs[0], t.inputs[0])
            nt.links.new(t.outputs[0], b.inputs["Base Color"])
        else:
            b.inputs["Base Color"].default_value = (*srgb_lin(cor or "#cccccc"), 1)
        b.inputs["Roughness"].default_value = rug[0]
        if rug_proprio:
            t = no(nt, "ShaderNodeTexImage", -700, 0)
            t.image = bpy.data.images.load(os.path.join(TEX, rug_proprio), check_existing=True)
            t.image.colorspace_settings.name = "Non-Color"
            nt.links.new(mp.outputs[0], t.inputs[0])
            mm = no(nt, "ShaderNodeMath", -400, 0)
            mm.operation = "MULTIPLY"
            mm.inputs[1].default_value = rug[0]
            nt.links.new(t.outputs[0], mm.inputs[0])
            nt.links.new(mm.outputs[0], b.inputs["Roughness"])
        if nor_proprio:
            t = no(nt, "ShaderNodeTexImage", -700, -300)
            t.image = bpy.data.images.load(os.path.join(TEX, nor_proprio), check_existing=True)
            t.image.colorspace_settings.name = "Non-Color"
            nt.links.new(mp.outputs[0], t.inputs[0])
            nm = no(nt, "ShaderNodeNormalMap", -400, -300)
            nm.inputs["Strength"].default_value = normal
            nt.links.new(t.outputs[0], nm.inputs["Color"])
            nt.links.new(nm.outputs[0], b.inputs["Normal"])
    b.inputs["Metallic"].default_value = metal
    if verniz:
        b.inputs["Coat Weight"].default_value = verniz[0]
        b.inputs["Coat Roughness"].default_value = verniz[1]
    if anis:
        b.inputs["Anisotropic"].default_value = anis
        tg = no(nt, "ShaderNodeTangent", -400, -600)
        tg.direction_type = "UV_MAP"
        tg.uv_map = "UVMap"
        nt.links.new(tg.outputs[0], b.inputs["Tangent"])
        b.inputs["Anisotropic Rotation"].default_value = 0.25          # along v
    if emissao:
        b.inputs["Emission Color"].default_value = (*srgb_lin(emissao[0]), 1)
        b.inputs["Emission Strength"].default_value = emissao[1]
    return m


def mat_acabamento(chave):
    a = ACAB[chave]
    if a.get("tex"):
        return mat_pbr("acab_" + chave, a["tex"], a["tamanho_m"], rug=tuple(a["rug"]), normal=a.get("normal", 1.0),
                       verniz=a.get("verniz"))
    if a.get("metal"):
        return mat_pbr("acab_" + chave, cor=a["cor"], rug=tuple(a["rug"]), metal=1.0, nor_proprio="escovado_nor.png",
                       rug_proprio="escovado_rug.png", normal=0.25, tamanho=0.25, anis=a.get("escovado", 0.0))
    if a.get("po"):
        return mat_pbr("acab_" + chave, cor=a["cor"], rug=tuple(a["rug"]), nor_proprio="po_nor.png", normal=0.15,
                       tamanho=0.08)
    return mat_pbr("acab_" + chave, cor=a["cor"], rug=tuple(a["rug"]), verniz=a.get("verniz"), nor_proprio="laca_nor.png",
                   normal=0.1, tamanho=0.5)


# ---------------------------------------------------------------------------------------------- meshes and UVs
def malha_de(nome, v, f, col, mat):
    n = len(v) // 3
    verts = [(v[3 * i], -v[3 * i + 2], v[3 * i + 1]) for i in range(n)]
    faces = [f[3 * i:3 * i + 3] for i in range(len(f) // 3)]
    me = bpy.data.meshes.new(nome)
    me.from_pydata(verts, [], faces)
    me.validate()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0002)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    col.objects.link(ob)
    me.materials.append(mat)
    return ob


def suavizar(ob, angulo=35):
    ob.data.shade_smooth()
    ob.data.set_sharp_from_angle(angle=math.radians(angulo))


def partir_ao_meio(ob):
    """Cut a part that spans both halves at x = 0: two closed solids (L keeps x <= 0)."""
    metades = []
    for lado in ("L", "R"):
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6,
                                   plane_co=(0, 0, 0), plane_no=(1, 0, 0), clear_outer=(lado == "L"),
                                   clear_inner=(lado == "R"))
        corte = [e for e in r["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
        bmesh.ops.holes_fill(bm, edges=corte, sides=0)
        me = bpy.data.meshes.new(ob.name + "_" + lado)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(ob.data.materials[0])
        nv = bpy.data.objects.new(ob.name + "_" + lado, me)
        for c in ob.users_collection:
            c.objects.link(nv)
        for k in ob.keys():
            nv[k] = ob[k]
        nv["lado"] = "S" + lado
        metades.append(nv)
    bpy.data.objects.remove(ob)
    return metades


def uv_veio(ob, papel):
    """UVs in metres, grain along v (the veneer scans run along v). Top layers: top/bottom faces v = x (the length),
    edges v = arc length along the outline (the edge banding follows the edge), cut faces v = y. Legs: v = z. A
    different region of the veneer for each part (seeded by its name)."""
    me = ob.data
    uv = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    co = np.array([v.co[:] for v in me.vertices])
    rng = np.random.default_rng(semente(ob.name))
    du, dv = rng.uniform(0, 3), rng.uniform(0, 3)
    s_de = None
    if papel == "tampo":
        lados = [p for p in me.polygons if abs(p.normal.z) < 0.5 and not (abs(p.normal.x) > 0.99 and abs(p.center.x) < 1e-3)]
        idx = sorted({i for p in lados for i in p.vertices})
        if len(idx) > 3:
            xy = co[idx, :2]
            L = max(np.abs(co[:, 0]).max(), 1e-3)
            W = max(np.abs(co[:, 1]).max(), 1e-3)
            cx = 0.0 if co[:, 0].min() < -0.01 and co[:, 0].max() > 0.01 else float(co[:, 0].mean())
            th = np.arctan2(xy[:, 1] / W, (xy[:, 0] - cx) / L)
            o = np.argsort(th)
            pts = np.unique(np.round(xy[o], 4), axis=0)
            tp = np.arctan2(pts[:, 1] / W, (pts[:, 0] - cx) / L)
            oo = np.argsort(tp)
            pts, tp = pts[oo], tp[oo]
            s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])

            def s_de(x, y):
                return float(np.interp(math.atan2(y / W, (x - cx) / L), tp, s))
    for p in me.polygons:
        n = p.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for li in p.loop_indices:
            x, y, z = co[me.loops[li].vertex_index]
            if papel == "tampo":
                if az >= 0.5:
                    u, v = y, x
                elif ax > 0.99 and abs(p.center.x) < 1e-3:
                    u, v = z, y
                else:
                    u, v = z, s_de(x, y) if s_de else x
            else:                       # legs, apron, runners: grain up (legs) or along the longest side
                if az >= max(ax, ay):
                    u, v = x, y
                elif ax >= ay:
                    u, v = y, z
                else:
                    u, v = x, z
            uv.data[li].uv = (u + du, v + dv)


# ---------------------------------------------------------------------------------------------- the table
MAT = {}
VAR = {}            # key -> {"L": [...], "R": [...], "C": [...], "tabua": [...], "col": collection}


def construir_mesa():
    raiz = colecao("mesa")
    for k in ("oak", "walnut", "lacq", "marble", "bronze", "steel", "black", "runner"):
        MAT[k] = mat_acabamento(k)
    for v in GEO["variants"]:
        K = v["key"]
        col = colecao("mesa_" + K, raiz)
        grupos = {"L": [], "R": [], "C": [], "tabua": []}
        for i, p in enumerate(v["parts"]):
            papel = p["role"]
            mat = MAT["runner"] if papel == "guia" else MAT["bronze"] if papel in ("pe", "pe_nucleo") else MAT["oak"]
            ob = malha_de(f"{K}_{i:02d}_{papel}", p["v"], p["f"], col, mat)
            ob["papel"], ob["lado"], ob["nome"], ob["variante"] = papel, p["side"], p["name"], K
            obs = partir_ao_meio(ob) if p["side"] == "S" else [ob]
            for o in obs:
                suavizar(o)
                uv_veio(o, "tampo" if papel in ("tampo", "aro") else papel)
                grupos["L" if o["lado"] in ("L", "SL") else "R" if o["lado"] in ("R", "SR") else "C"].append(o)
        for i, p in enumerate(v["leaf"]):
            ob = malha_de(f"{K}_tabua_{i}", p["v"], p["f"], col, MAT["oak"])
            for vt in ob.data.vertices:
                vt.co.x *= LEAF                     # the source leaf is 1 m long and scaled by the page: ours is 500 mm
            ob["papel"], ob["lado"], ob["nome"], ob["variante"] = "tampo", "tabua", p["name"], K
            suavizar(ob)
            uv_veio(ob, "tampo")
            grupos["tabua"].append(ob)
        grupos["col"] = col
        VAR[K] = grupos
        print("MESA", K, {g: len(o) for g, o in grupos.items() if g != "col"})


def estado_mesa(K, tabuas, visiveis=True):
    """Table K with n leaves (0, 1, 2): halves apart, runners stretched, leaves in place (as the page does it)."""
    g = VAR[K]
    gap = tabuas * LEAF
    for o in g["L"]:
        o.location.x = -gap / 2
    for o in g["R"]:
        o.location.x = gap / 2
    for o in g["C"]:
        o.scale.x = 1 + gap / 1.5
    for k in list(g.get("copias", [])):
        bpy.data.objects.remove(k)
    g["copias"] = []
    for o in g["tabua"]:
        o.hide_render = o.hide_viewport = tabuas == 0 or not visiveis
        if tabuas:
            o.location.x = -gap / 2 + LEAF * 0.5
    if tabuas == 2:
        for o in g["tabua"]:
            c = o.copy()
            g["col"].objects.link(c)
            c.location.x = -gap / 2 + LEAF * 1.5
            c.hide_render = c.hide_viewport = not visiveis
            g["copias"].append(c)
    for o in g["L"] + g["R"] + g["C"]:
        o.hide_render = o.hide_viewport = not visiveis


def mostrar_mesa(K):
    for k in VAR:
        estado_mesa(k, 0, visiveis=(k == K))


# ---------------------------------------------------------------------------------------------- the chair
def tubo_conico(nome, a, b, r0, r1, col, mat, segs=20):
    """A tapered round member from a (r0) to b (r1)."""
    a, b = Vector(a), Vector(b)
    bm = bmesh.new()
    eixo = (b - a)
    q = eixo.to_track_quat("Z", "Y")
    aneis = []
    for t, r in ((0.0, r0), (1.0, r1)):
        anel = []
        for k in range(segs):
            ang = 2 * math.pi * k / segs
            p = q @ Vector((r * math.cos(ang), r * math.sin(ang), 0)) + a + eixo * t
            anel.append(bm.verts.new(p))
        aneis.append(anel)
    for k in range(segs):
        bm.faces.new((aneis[0][k], aneis[0][(k + 1) % segs], aneis[1][(k + 1) % segs], aneis[1][k]))
    for anel, inv in ((aneis[0], True), (aneis[1], False)):
        f = bm.faces.new(anel[::-1] if inv else anel)
        bmesh.ops.bevel(bm, geom=f.edges[:], offset=min(r0, r1) * 0.25, segments=3, profile=0.5, affect="EDGES",
                        clamp_overlap=True)
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    col.objects.link(ob)
    me.materials.append(mat)
    suavizar(ob, 50)
    return ob


def caixa_estofada(nome, dx, dy, dz, centro, raio, coroa, col, mat, sub=2):
    """A cushion: a box with round edges (bevel), softened (subdivision) and its top slightly crowned."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * dx, v.co.y * dy, v.co.z * dz))
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=raio, segments=4, profile=0.55, affect="EDGES", clamp_overlap=True)
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    col.objects.link(ob)
    me.materials.append(mat)
    md = ob.modifiers.new("sub", "SUBSURF")
    md.levels = md.render_levels = sub
    aplicar(ob)
    for v in ob.data.vertices:
        if v.co.z > 0:
            fx, fy = min(1, abs(v.co.x) / (dx / 2)), min(1, abs(v.co.y) / (dy / 2))
            v.co.z += coroa * (1 - fx ** 4) * (1 - fy ** 4)
    ob.location = centro
    aplicar_transformacao(ob)
    suavizar(ob, 80)
    return ob


def aplicar(ob):
    bpy.context.view_layer.objects.active = ob
    for m in list(ob.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def aplicar_transformacao(ob):
    """Bake the object's transform into its mesh (matrix_basis: matrix_world is only updated by the depsgraph, and
    an object just moved still had the old one — the first chairs had their seats on the floor)."""
    ob.data.transform(ob.matrix_basis)
    ob.matrix_basis.identity()


def curva_para_malha(nome, pontos, raio, col, mat, fechada=True, perfil=None, tampas=True):
    cu = bpy.data.curves.new(nome, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(len(pontos) - 1)
    for p, c in zip(sp.points, pontos):
        p.co = (*c, 1)
    sp.use_cyclic_u = fechada
    if perfil is not None:
        cu.bevel_mode = "OBJECT"
        cu.bevel_object = perfil
        cu.use_fill_caps = tampas
    else:
        cu.bevel_depth = raio
        cu.bevel_resolution = 4
    ob = bpy.data.objects.new(nome, cu)
    col.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    obm = bpy.data.objects.new(nome, me)
    col.objects.link(obm)
    me.materials.clear()
    me.materials.append(mat)
    suavizar(obm, 70)
    return obm


def retangulo_arredondado(cx, cy, w, h, r, z, n=6):
    pts = []
    for (ox, oy, a0) in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                         (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a), z))
    return pts


def construir_cadeira():
    """Our dining chair (front to +y, its back at -y; placed by the page): the source page's chair made real —
    seat cushion 460 x 440 at 450 mm with a piped top edge on an oak frame, four tapered oak legs, the back legs running
    up into an upholstered curved back band (radius ~0.23 m, ~120 degrees, 620–820 mm)."""
    col = colecao("cadeira")
    tecido = mat_pbr("tecido", imagem_cor=bpy.data.images.load(os.path.join(TEX, "linho_cor.jpg"), check_existing=True),
                     tamanho=CFG["tecido"]["tamanho_m"], rug=(0.92, 0.92))
    # the linen's own weave relief and roughness on top of our colour
    nt = tecido.node_tree
    b = nt.nodes["Principled BSDF"]
    mp = next(n for n in nt.nodes if n.type == "MAPPING")
    d = os.path.join(ATIVOS, CFG["tecido"]["tex"])
    tn = no(nt, "ShaderNodeTexImage", -700, -300)
    tn.image = bpy.data.images.load(os.path.join(d, "nor_gl.jpg"), check_existing=True)
    tn.image.colorspace_settings.name = "Non-Color"
    nt.links.new(mp.outputs[0], tn.inputs[0])
    nm = no(nt, "ShaderNodeNormalMap", -400, -300)
    nm.inputs["Strength"].default_value = 1.0
    nt.links.new(tn.outputs[0], nm.inputs["Color"])
    nt.links.new(nm.outputs[0], b.inputs["Normal"])
    b.inputs["Sheen Weight"].default_value = 0.6
    b.inputs["Sheen Roughness"].default_value = 0.5
    madeira = MAT["oak"]
    obs = []
    obs.append(caixa_estofada("assento", 0.46, 0.44, 0.07, (0, 0, 0.415), 0.022, 0.008, col, tecido))
    obs.append(curva_para_malha("debrum", retangulo_arredondado(0, 0, 0.462, 0.442, 0.03, 0.437), 0.0028, col, tecido))
    # oak frame under the cushion
    for nome, a, b2 in (("travessa_f", (-0.19, 0.17, 0.355), (0.19, 0.17, 0.355)),
                        ("travessa_t", (-0.19, -0.18, 0.355), (0.19, -0.18, 0.355)),
                        ("travessa_e", (-0.19, -0.18, 0.355), (-0.19, 0.17, 0.355)),
                        ("travessa_d", (0.19, -0.18, 0.355), (0.19, 0.17, 0.355))):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        a, b2 = Vector(a), Vector(b2)
        comp = (b2 - a).length
        ao_longo_x = abs((b2 - a).x) > abs((b2 - a).y)
        for v in bm.verts:
            v.co = Vector((v.co.x * (comp if ao_longo_x else 0.022), v.co.y * (0.022 if ao_longo_x else comp), v.co.z * 0.05))
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.002, segments=2, affect="EDGES", clamp_overlap=True)
        me = bpy.data.meshes.new(nome)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(nome, me)
        col.objects.link(ob)
        ob.location = (a + b2) / 2
        aplicar_transformacao(ob)
        me.materials.append(madeira)
        suavizar(ob, 40)
        obs.append(ob)
    # legs: front ones nearly upright, the back ones splayed and running up into the band
    for sx in (-1, 1):
        obs.append(tubo_conico(f"perna_f{sx}", (sx * 0.195, 0.19, 0.0), (sx * 0.19, 0.17, 0.38), 0.011, 0.016, col, madeira))
        obs.append(tubo_conico(f"perna_t{sx}", (sx * 0.195, -0.215, 0.0), (sx * 0.19, -0.18, 0.38), 0.011, 0.016, col, madeira))
        obs.append(tubo_conico(f"montante{sx}", (sx * 0.19, -0.18, 0.38), (sx * 0.185, -0.155, 0.74), 0.016, 0.013, col, madeira))
    # the curved back band: a rounded profile swept along an arc behind the seat
    pc = bpy.data.curves.new("perfil_costas", "CURVE")
    sp = pc.splines.new("POLY")
    perfil = [(x, z, 0) for (x, z, _) in retangulo_arredondado(0, 0, 0.034, 0.19, 0.014, 0, 5)]
    sp.points.add(len(perfil) - 1)
    for p, c in zip(sp.points, perfil):
        p.co = (*c, 1)
    sp.use_cyclic_u = True
    perfil_ob = bpy.data.objects.new("perfil_costas", pc)
    col.objects.link(perfil_ob)
    arco = []
    for k in range(41):
        a = math.radians(-62 + 124 * k / 40)
        arco.append((0.232 * math.sin(a), -0.02 - 0.232 * math.cos(a), 0.725))
    obs.append(curva_para_malha("costas", arco, 0, col, tecido, fechada=False, perfil=perfil_ob, tampas=True))
    bpy.data.objects.remove(perfil_ob)
    bpy.data.curves.remove(pc)
    for ob in obs:
        uv_veio(ob, "pe")              # metres, so the weave and the grain keep their real size
        ob["mat"] = ob.data.materials[0].name if ob.data.materials[0] != madeira else "madeira"
    return col


# ---------------------------------------------------------------------------------------------- the room
# scan: the Poly Haven scans (sideboard, vases, plant) — no lightmap: thousands of faces become thousands of tiny
# islands with a few texels each (the vases came out dark); the page lights them in real time (panorama, sun, spots)
SALA_OBS = {"sala": [], "moveis": [], "fora": [], "scan": []}


def caixa(nome, cx, cy, cz, dx, dy, dz, mat, grupo, col, parede=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((cx + v.co.x * dx, cy + v.co.y * dy, cz + v.co.z * dz))
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    col.objects.link(ob)
    me.materials.append(mat)
    uv_mundo(ob)
    if parede:
        ob["parede"] = parede
    SALA_OBS[grupo].append(ob)
    return ob


def uv_mundo(ob):
    me = ob.data
    uv = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    for p in me.polygons:
        n = p.normal
        for li in p.loop_indices:
            c = me.vertices[me.loops[li].vertex_index].co
            if abs(n.z) >= max(abs(n.x), abs(n.y)):
                u, v = c.x, c.y
            elif abs(n.x) >= abs(n.y):
                u, v = c.y, c.z
            else:
                u, v = c.x, c.z
            uv.data[li].uv = (u, v)


def importar(caminho, col):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=caminho)
    novos = [o for o in bpy.data.objects if o not in antes]
    for o in novos:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
    raiz = [o for o in novos if o.parent is None]
    return novos, raiz


def assentar(novos, raiz, x, y, rz, z=0.0):
    """Place an imported model by its bounding box: centred on (x, y), resting on z, rotated rz degrees."""
    # one pivot for every root (a model can come as several roots — the sideboard's body and its two doors: each
    # turned about its own origin, they came apart and the vases stood on air, user 2026-11-27)
    from mathutils import Matrix
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in novos if o.type == "MESH" for c in o.bound_box]
    piv = Vector(((min(p.x for p in pts) + max(p.x for p in pts)) / 2, (min(p.y for p in pts) + max(p.y for p in pts)) / 2, 0))
    rot = Matrix.Translation(piv) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Translation(-piv)
    for r in raiz:
        r.matrix_world = rot @ r.matrix_world
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in novos if o.type == "MESH" for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    d = Vector((x - (mn.x + mx.x) / 2, y - (mn.y + mx.y) / 2, z - mn.z))
    for r in raiz:
        r.location += d
    bpy.context.view_layer.update()
    return mn + d, mx + d


def fixar(novos, grupo):
    """Imported meshes: transforms applied (the page and the bake want world-space meshes), into a group."""
    meshes = [o for o in novos if o.type == "MESH"]
    for o in meshes:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
        if o.data.users > 1:
            o.data = o.data.copy()
        aplicar_transformacao(o)
    for o in novos:
        if o.type != "MESH":
            bpy.data.objects.remove(o)
    SALA_OBS[grupo].extend(meshes)
    return meshes


def arte():
    """The source page's print (a terracotta circle and a dark bar on warm paper), on paper with a grain."""
    rng = np.random.default_rng(11)
    w, h = 700, 960
    yy, xx = np.mgrid[0:h, 0:w]
    papel = np.array(srgb_lin("#e9e4da"))
    img = np.ones((h, w, 3)) * papel
    grao = ruido_suave(1024, 200, rng)[:h, :w] * 0.04 - 0.02
    img = img * (1 + grao[..., None])
    circ = ((xx - w * 0.45) ** 2 + (yy - h * 0.40) ** 2) < (w * 0.26) ** 2
    borda = ruido_suave(1024, 60, rng)[:h, :w] * 0.8
    img[circ] = np.array(srgb_lin("#c4512a")) * (0.94 + 0.08 * borda[circ][:, None])
    barra = (xx > w * 0.2) & (xx < w * 0.8) & (yy > h * 0.66) & (yy < h * 0.71)
    img[barra] = np.array(srgb_lin("#1d2a33"))
    lin = np.clip(img, 0, 1)
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    return gravar_img("arte", srgb, nao_cor=False, fmt="JPEG")


def construir_sala():
    col = colecao("sala")
    fora = colecao("fora")
    s = SALA
    est = s["estuque"]
    m_parede = mat_pbr("parede", est["tex"], est["tamanho_m"], cor=est["cor"], rug=tuple(est["rug"]), normal=0.35,
                       variacao=est.get("variacao", 0.3))
    m_teto = mat_pbr("teto", est["tex"], est["tamanho_m"], cor=est["teto"], rug=tuple(est["rug"]), normal=0.3,
                     variacao=est.get("variacao", 0.3))
    so = s["soalho"]
    m_soalho = mat_pbr("soalho", so["tex"], so["tamanho_m"], rug=tuple(so["rug"]), normal=0.8, verniz=(0.25, 0.3))
    m_rodape = mat_pbr("rodape", cor="#f4f1ec", rug=(0.45, 0.45))
    m_caixilho = mat_pbr("caixilho", cor="#3a3d40", rug=(0.4, 0.4), metal=0.6)
    m_tapete = mat_pbr("tapete", imagem_cor=bpy.data.images.load(os.path.join(TEX, "linho_cor.jpg"), check_existing=True),
                       tamanho=0.8, rug=(0.97, 0.97))
    m_arte = mat_pbr("arte", imagem_cor=arte(), rug=(0.8, 0.8))
    m_moldura = mat_pbr("moldura", cor="#2a2a2a", rug=(0.55, 0.55))
    hx, hy = RW / 2, RD / 2
    # floor and ceiling
    caixa("soalho", 0, 0, -0.01, RW, RD, 0.02, m_soalho, "sala", col)
    caixa("teto", 0, 0, RH + 0.05, RW + 2 * T, RD + 2 * T, 0.1, m_teto, "sala", col, parede="teto")
    # walls (the back one has the window), the page hides the ones between the camera and the room
    j = s["janela"]
    ww, wh, sill = j["largura"], j["altura"], j["peitoril"]
    yb = hy + T / 2
    lado = hx + T - ww / 2              # from the window's jamb to the outer corner (the corner block included)
    caixa("parede_tras_e", -(ww / 2 + lado / 2), yb, RH / 2, lado, T, RH, m_parede, "sala", col, "tras")
    caixa("parede_tras_d", ww / 2 + lado / 2, yb, RH / 2, lado, T, RH, m_parede, "sala", col, "tras")
    caixa("parede_tras_peitoril", 0, yb, sill / 2, ww, T, sill, m_parede, "sala", col, "tras")
    caixa("parede_tras_padieira", 0, yb, RH - (RH - sill - wh) / 2, ww, T, RH - sill - wh, m_parede, "sala", col, "tras")
    caixa("parede_frente", 0, -yb, RH / 2, RW + 2 * T, T, RH, m_parede, "sala", col, "frente")
    caixa("parede_esq", -hx - T / 2, 0, RH / 2, T, RD, RH, m_parede, "sala", col, "esq")
    caixa("parede_dir", hx + T / 2, 0, RH / 2, T, RD, RH, m_parede, "sala", col, "dir")
    for nome, cx, cy, dx, dy, par in (("rodape_tras", 0, hy - 0.0075, RW, 0.015, "tras"), ("rodape_frente", 0, -hy + 0.0075, RW, 0.015, "frente"),
                                      ("rodape_esq", -hx + 0.0075, 0, 0.015, RD, "esq"), ("rodape_dir", hx - 0.0075, 0, 0.015, RD, "dir")):
        caixa(nome, cx, cy, 0.04, dx, dy, 0.08, m_rodape, "sala", col, par)
    # window: aluminium frame with a mullion; the glass only in the page (the bake sees the opening)
    yj = hy + T * 0.65
    for nome, cx, cz, dx, dz in (("caixilho_e", -ww / 2 + 0.025, sill + wh / 2, 0.05, wh), ("caixilho_d", ww / 2 - 0.025, sill + wh / 2, 0.05, wh),
                                 ("caixilho_m", 0, sill + wh / 2, 0.06, wh), ("caixilho_b", 0, sill + 0.025, ww, 0.05),
                                 ("caixilho_c", 0, sill + wh - 0.025, ww, 0.05)):
        caixa(nome, cx, yj, cz, dx, 0.07, dz, m_caixilho, "sala", col, "tras")
    caixa("soleira", 0, hy + T / 2, sill - 0.01, ww + 0.04, T + 0.04, 0.02, mat_pbr("pedra_soleira", cor="#d8d2c6", rug=(0.4, 0.4)),
          "sala", col, "tras")
    # rug
    tw, td = s["tapete"]
    caixa("tapete", 0, 0, 0.004, tw, td, 0.008, m_tapete, "moveis", col)
    # print on the right wall
    caixa("moldura", hx - 0.02, 0, 1.5, 0.03, 0.82, 1.12, m_moldura, "moveis", col, "dir")
    q = caixa("arte", hx - 0.036, 0, 1.5, 0.002, 0.74, 1.02, m_arte, "moveis", col, "dir")
    for p in q.data.polygons:                       # the print's own UVs (0..1 on the face looking into the room)
        for li in p.loop_indices:
            c = q.data.vertices[q.data.loops[li].vertex_index].co
            q.data.uv_layers["UVMap"].data[li].uv = (1 - (c.y + 0.37) / 0.74, (c.z - 0.99) / 1.02)
    # sideboard, vases, plant (Poly Haven, native size)
    nov, raiz = importar(os.path.join(ATIVOS, "modern_wooden_cabinet", "modern_wooden_cabinet_2k.gltf"), col)
    mn, mx = assentar(nov, raiz, -hx + 0.27, 0.0, 90)
    topo = mx.z
    fixar(nov, "scan")
    for nome, y, rz in (("ceramic_vase_01", 0.75, 20), ("ceramic_vase_04", 0.48, 70), ("ceramic_vase_02", -0.6, 0)):
        nov, raiz = importar(os.path.join(ATIVOS, nome, f"{nome}_2k.gltf"), col)
        assentar(nov, raiz, -hx + 0.27, y, rz, z=topo)
        fixar(nov, "scan")
    nov, raiz = importar(os.path.join(ATIVOS, "potted_plant_02", "potted_plant_02_2k.gltf"), col)
    assentar(nov, raiz, -hx + 0.55, hy - 0.55, 35)
    fixar(nov, "scan")
    # the bronze linear pendant (bar 1.6 m, its bottom at 1.62 m), diffuser and cables
    m_difusor = mat_pbr("difusor", cor="#fbf4e6", rug=(0.5, 0.5), emissao=("#ffe2b0", 0.0))
    caixa("pendente", 0, 0, 1.62 + 0.0175, 1.6, 0.06, 0.035, MAT["bronze"], "moveis", col)
    caixa("difusor", 0, 0, 1.6205, 1.56, 0.04, 0.003, m_difusor, "moveis", col)
    for x in (-0.7, 0.7):
        tubo_conico(f"cabo{x}", (x, 0, 1.655), (x, 0, RH), 0.0012, 0.0012, col, MAT["black"], 8)
        SALA_OBS["moveis"].append(bpy.data.objects[f"cabo{x}"])
    # outside: lawn, trees, the sky (world)
    rv = s["relva"]
    m_relva = mat_pbr("relva", rv["tex"], rv["tamanho_m"], cor=rv.get("cor"), rug=(0.8, 1.0), normal=1.0)
    caixa("relva", 0, hy + 22, -0.06, 60, 40, 0.02, m_relva, "fora", fora)
    vg = os.path.join(ATIVOS, "..", "vegetacao")
    for nome, x, y, rz in (("island_tree_02_web.glb", -6.5, hy + 9, 10), ("island_tree_02_web.glb", 7.0, hy + 13, 140),
                           ("island_tree_02_web.glb", 1.5, hy + 19, 60)):
        caminho = os.path.join(vg, nome)
        if os.path.exists(caminho):
            nov, raiz = importar(caminho, fora)
            assentar(nov, raiz, x, y, rz, z=-0.05)
            fixar(nov, "fora")
    return col


# ---------------------------------------------------------------------------------------------- light
LUZES = {}


def ceu():
    """World: the photographed sky, its sun capped to the brightest cloud (the sun lamp gives the sun) and turned so
    the photo's sun is where the lamp is."""
    w = bpy.data.worlds.new("mundo")
    cena.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    img = bpy.data.images.load(os.path.join(ATIVOS, LUZ["ceu"]))
    W, H = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)
    lum = px[..., :3] @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    r, c = np.unravel_index(np.argmax(lum), lum.shape)
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot((xx - c) * 360 / W, (yy - r) * 180 / H)
    teto = float(lum[dist > 6].max())
    excesso = np.clip(lum / max(teto, 1e-6), 1, None)[..., None]
    px[..., :3] /= np.where(dist[..., None] < 8, excesso, 1)
    img.pixels.foreach_set(px.ravel())
    sol_u = (c + 0.5) / W                  # Cycles: u = 0.5 - atan2(d.y, d.x) / 2pi (centre = +x)
    d = Vector(LUZ["sol_de"])
    d = Vector((d.x, -d.z, d.y)).normalized()              # three.js -> Blender
    phi_alvo = math.atan2(d.y, d.x)
    phi0 = (0.5 - sol_u) * 2 * math.pi     # the photo's sun with no rotation; the Mapping turns the lookup by +theta
    tc = no(nt, "ShaderNodeTexEnvironment", -500, 0)
    tc.image = img
    co = no(nt, "ShaderNodeTexCoord", -900, 0)
    mp = no(nt, "ShaderNodeMapping", -700, 0)
    mp.inputs["Rotation"].default_value = (0, 0, phi0 - phi_alvo)
    nt.links.new(co.outputs["Generated"], mp.inputs[0])
    nt.links.new(mp.outputs[0], tc.inputs[0])
    nt.links.new(tc.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = LUZ["ceu_forca"]
    LUZES["fundo"] = bg
    LUZES["sol_dir"] = d
    print("CEU", W, "x", H, "sol na coluna", c, "linha", r, "teto", round(teto, 2), "rodar", round(math.degrees(phi0 - phi_alvo), 1))


def luzes():
    ceu()
    sl = bpy.data.lights.new("sol", "SUN")
    sl.energy = LUZ["sol_forca"]
    sl.angle = math.radians(0.6)
    so = bpy.data.objects.new("sol", sl)
    cena.collection.objects.link(so)
    so.rotation_euler = (-LUZES["sol_dir"]).to_track_quat("-Z", "Y").to_euler()
    LUZES["sol"] = so
    N = LUZ["noite"]
    LUZES["focos"] = []
    for x in N["focos_x"]:
        lt = bpy.data.lights.new(f"foco{x}", "SPOT")
        lt.energy = N["focos_w"]
        lt.color = srgb_lin(N.get("cor", "#ffffff"))       # warm, as a home's lamp (the source page's 0xffd7a0)
        lt.spot_size = N["angulo"] * 2
        lt.spot_blend = N["suave"]
        lt.shadow_soft_size = 0.02
        ob = bpy.data.objects.new(f"foco{x}", lt)
        cena.collection.objects.link(ob)
        ob.location = (x, 0, N["focos_y"])
        ob.hide_render = True
        LUZES["focos"].append(ob)


def modo_luz(modo, so_tempo_real=False):
    """'dia' or 'noite'; so_tempo_real: only the lights the page draws itself (the sun by day, the spots at night)."""
    dia = modo == "dia"
    cena.view_settings.exposure = float(LUZ.get("exposicao" if dia else "exposicao_noite", 0.0))
    LUZES["fundo"].inputs[1].default_value = 0.0 if so_tempo_real else (LUZ["ceu_forca"] if dia else LUZ["noite"]["ceu_forca"])
    LUZES["sol"].hide_render = not dia
    for f in LUZES["focos"]:
        f.hide_render = dia
    if "difusor" in bpy.data.materials:
        d = bpy.data.materials["difusor"].node_tree.nodes["Principled BSDF"]
        d.inputs["Emission Strength"].default_value = 0.0 if (dia or so_tempo_real) else LUZ["noite"]["brilho_barra"]


# ---------------------------------------------------------------------------------------------- bakes
def usar_gpu():
    pref = bpy.context.preferences.addons["cycles"].preferences
    for tipo in ("OPTIX", "CUDA"):
        try:
            pref.compute_device_type = tipo
            pref.refresh_devices()
            gpus = [d for d in pref.devices if d.type == tipo]
            if tipo == "OPTIX":
                gpus = [d for d in gpus if "RTX" in d.name.upper()]
            if gpus:
                for d in pref.devices:
                    d.use = d.type == tipo
                cena.cycles.device = "GPU"
                print("GPU:", tipo, ", ".join(d.name for d in gpus))
                return
        except Exception as e:  # noqa: BLE001
            print("GPU", tipo, "indisponível:", e)
    print("Sem GPU: Cycles no processador")


def sem_ruido(img, w, h):
    """OIDN (the compositor's Denoise node) on a baked image; float pixels (h, w, 3)."""
    sc = bpy.data.scenes.new("_sem_ruido")
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 1
    nt = bpy.data.node_groups.new("_sem_ruido", "CompositorNodeTree")
    sc.compositing_node_group = nt
    nt.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    saida, ni, dn = nt.nodes.new("NodeGroupOutput"), nt.nodes.new("CompositorNodeImage"), nt.nodes.new("CompositorNodeDenoise")
    ni.image = img
    nt.links.new(ni.outputs[0], dn.inputs[0])
    nt.links.new(dn.outputs[0], saida.inputs[0])
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.filepath = os.path.join(SAIDA, "_sem_ruido.exr")
    bpy.ops.render.render(write_still=True, scene=sc.name)
    res = bpy.data.images.load(sc.render.filepath)
    px = np.array(res.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3].copy()
    bpy.data.images.remove(res)
    os.remove(sc.render.filepath)
    bpy.data.node_groups.remove(nt)
    bpy.data.scenes.remove(sc)
    return np.clip(px, 0, None)


def uv_luz(obs):
    for ob in obs:
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(ob.data)
        bm.free()
        me = ob.data
        if not me.uv_layers:
            me.uv_layers.new(name="UVMap")
        lm = me.uv_layers.get("lm") or me.uv_layers.new(name="lm")
        me.uv_layers.active = lm
    bpy.ops.object.select_all(action="DESELECT")
    for ob in obs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.003, area_weight=1.0, correct_aspect=True,
                             scale_to_bounds=False)
    bpy.ops.uv.pack_islands(margin=0.003, rotate=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    for ob in obs:
        ob.data.uv_layers[0].active = True
        ob.data.uv_layers[0].active_render = True


def cozer_imagem(obs, nome, n, filtro):
    img = bpy.data.images.new(nome, n, n, alpha=False, float_buffer=True)
    for m in {m for ob in obs for m in ob.data.materials if m}:
        nt = m.node_tree
        nd = nt.nodes.get("LM") or nt.nodes.new("ShaderNodeTexImage")
        nd.name = "LM"
        nd.image = img
        nt.nodes.active = nd
    bpy.ops.object.select_all(action="DESELECT")
    for ob in obs:
        ob.select_set(True)
        ob.data.uv_layers.active = ob.data.uv_layers["lm"]
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.bake(type="DIFFUSE", pass_filter=filtro, uv_layer="lm", margin=8, margin_type="EXTEND",
                        use_clear=True, target="IMAGE_TEXTURES")
    px = sem_ruido(img, n, n)
    bpy.data.images.remove(img)
    for ob in obs:
        ob.data.uv_layers.active = ob.data.uv_layers[0]
    return px


def gravar_lm(px, nome):
    n = px.shape[0]
    K = float(np.percentile(px, 99.7)) or 1.0
    x = np.clip(px / K, 0, 1)
    enc = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    out = bpy.data.images.new(nome, n, n, alpha=False)
    rgba = np.ones((n, n, 4), dtype=np.float32)
    rgba[..., :3] = enc
    out.pixels.foreach_set(rgba.ravel())
    out.filepath_raw = os.path.join(SAIDA, nome + ".jpg")
    out.file_format = "JPEG"
    cena.render.image_settings.quality = 90
    out.save()
    bpy.data.images.remove(out)
    return round(K, 5)


TAMANHOS = {k: max(256, int(v * float(opc("--lm_escala", 1)))) for k, v in {"sala": 4096, "moveis": 2048, "fora": 2048}.items()}


def cozer_luz(info):
    usar_gpu()
    cena.cycles.samples = AMOSTRAS
    cena.cycles.use_denoising = False
    cena.cycles.sample_clamp_indirect = 2.0
    cena.cycles.max_bounces = 8
    for coisa in [o for g in VAR.values() for k in ("L", "R", "C", "tabua") for o in g[k]] + list(bpy.data.collections["cadeira"].objects):
        coisa.hide_render = True
    for modo in ("dia", "noite"):
        for grupo, obs in SALA_OBS.items():
            if not obs or grupo == "scan":
                continue
            t0 = time.time()
            n = TAMANHOS[grupo]
            modo_luz(modo)
            a = cozer_imagem(obs, f"A_{modo}_{grupo}", n, {"DIRECT", "INDIRECT"})
            if grupo != "fora":
                modo_luz(modo, so_tempo_real=True)
                b = cozer_imagem(obs, f"B_{modo}_{grupo}", n, {"DIRECT"})
                a = np.clip(a - b, 0, None)
            info.setdefault("lm", {})[f"{modo}_{grupo}"] = {"K": gravar_lm(a, f"lm_{modo}_{grupo}"), "tam": n}
            print("LUZ", modo, grupo, n, round(time.time() - t0), "s")
    modo_luz("dia")


def panorama(modo, ceu=False):
    """The room seen from above the table's centre (three.js (0, 0.95, 0)), no table, no chairs: the table's
    reflections and ambient light. Equirectangular, centre = +x (three.js's convention), linear HDR.
    ceu: the sky alone (every mesh hidden; env_ceu.hdr), for the sky the page shows through the window."""
    from mathutils import Euler
    ocultos = []
    if ceu:
        for o in cena.objects:
            if o.type == "MESH" and not o.hide_render:
                o.hide_render = True
                ocultos.append(o)
    cam = bpy.data.cameras.new("pano")
    cam.type = "PANO"
    cam.panorama_type = "EQUIRECTANGULAR"
    ob = bpy.data.objects.new("cam_pano", cam)
    cena.collection.objects.link(ob)
    ob.location = (0, 0, 0.95)
    ob.rotation_euler = Euler((math.pi / 2, 0, -math.pi / 2))
    cena.camera = ob
    modo_luz(modo)
    cena.render.resolution_x, cena.render.resolution_y = 2048, 1024
    cena.render.resolution_percentage = 100
    cena.cycles.samples = AMOSTRAS
    cena.cycles.use_denoising = True
    cena.render.image_settings.file_format = "HDR"
    cena.render.filepath = os.path.join(SAIDA, "env_ceu.hdr" if ceu else f"env_{modo}.hdr")
    if ceu:
        cena.cycles.samples = 16
    vt, ex = cena.view_settings.view_transform, cena.view_settings.exposure
    cena.view_settings.view_transform = "Standard"
    cena.view_settings.exposure = 0.0                   # linear radiance, as the lightmaps
    bpy.ops.render.render(write_still=True)
    cena.view_settings.view_transform, cena.view_settings.exposure = vt, ex
    bpy.data.objects.remove(ob)
    for o in ocultos:
        o.hide_render = False
    print("PANORAMA", "ceu" if ceu else modo)


def sombra_limpa(oc):
    """Soften the baked occlusion (a 5-tap box blur three times, the edges repeated — zero padding darkened the
    borders and the page showed a frame round every shadow, on the rug) and fade it to nothing at the plane's edges."""
    k = np.ones(5) / 5
    for _ in range(3):
        for eixo in (0, 1):
            pad = [(2, 2) if e == eixo else (0, 0) for e in (0, 1)]
            oc = np.apply_along_axis(lambda c: np.convolve(c, k, "valid"), eixo, np.pad(oc, pad, mode="edge"))
    h, w = oc.shape
    fy = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / (0.08 * h), 0, 1)
    fx = np.clip(np.minimum(np.arange(w), np.arange(w)[::-1]) / (0.08 * w), 0, 1)
    borda = np.outer(fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx))
    return oc * borda


def sombras(info):
    """Ambient occlusion of each table state (variant, 0–2 leaves) and of a chair on a floor plane: the page lays
    them on the floor (the room's light is baked without the table)."""
    for o in cena.objects:
        o["_hr"] = o.hide_render
        o.hide_render = True
    cena.world.light_settings.distance = 0.8
    cena.cycles.samples = 128
    col = bpy.data.collections.new("_sombra")
    cena.collection.children.link(col)
    m = bpy.data.materials.new("_chao")
    m.use_nodes = True
    info["sombras"] = {}

    def plano(dx, dy, n_x, n_y, nome):
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
        for v in bm.verts:
            v.co = Vector((v.co.x * dx, v.co.y * dy, 0.0005))
        me = bpy.data.meshes.new(nome)
        bm.to_mesh(me)
        bm.free()
        me.uv_layers.new(name="UVMap")
        for p in me.polygons:
            for li in p.loop_indices:
                c = me.vertices[me.loops[li].vertex_index].co
                me.uv_layers[0].data[li].uv = (c.x / dx + 0.5, c.y / dy + 0.5)
        me.materials.append(m)
        ob = bpy.data.objects.new(nome, me)
        col.objects.link(ob)
        img = bpy.data.images.new(nome, n_x, n_y, alpha=False, float_buffer=True)
        nd = m.node_tree.nodes.get("LM") or m.node_tree.nodes.new("ShaderNodeTexImage")
        nd.name = "LM"
        nd.image = img
        m.node_tree.nodes.active = nd
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.bake(type="AO", margin=4, use_clear=True, target="IMAGE_TEXTURES")
        px = np.array(img.pixels[:], dtype=np.float32).reshape(n_y, n_x, 4)[..., 0]
        oc = sombra_limpa(np.clip(1 - px, 0, 1))
        out = bpy.data.images.new(nome + "_8", n_x, n_y, alpha=False)
        rgba = np.ones((n_y, n_x, 4), dtype=np.float32)
        rgba[..., 0] = rgba[..., 1] = rgba[..., 2] = oc
        out.pixels.foreach_set(rgba.ravel())
        out.filepath_raw = os.path.join(SAIDA, nome + ".png")
        out.file_format = "PNG"
        out.save()
        for x in (img, out):
            bpy.data.images.remove(x)
        bpy.data.objects.remove(ob)

    for K, g in VAR.items():
        for n in (0, 1, 2):
            estado_mesa(K, n)
            for kk in VAR:
                if kk != K:
                    estado_mesa(kk, 0, visiveis=False)
            L = 2.7 + n * LEAF + 1.2
            plano(L, 1.2 + 1.2, int(L * 160), int(2.4 * 160), f"sombra_{K}_{n}")
            info["sombras"][f"{K}_{n}"] = [round(L, 3), 2.4]
            print("SOMBRA", K, n)
    for K in VAR:
        estado_mesa(K, 0, visiveis=False)
    for o in bpy.data.collections["cadeira"].objects:
        o.hide_render = False
    plano(1.0, 1.0, 160, 160, "sombra_cadeira")
    info["sombras"]["cadeira"] = [1.0, 1.0]
    for o in bpy.data.collections["cadeira"].objects:
        o.hide_render = True
    for o in cena.objects:
        if "_hr" in o:
            o.hide_render = o["_hr"]
            del o["_hr"]
    bpy.data.collections.remove(col)


# ---------------------------------------------------------------------------------------------- reference images
VISTAS = {"geral": ((3.1, 2.0, 3.4), (0, 0.5, 0)), "frente": ((0, 1.05, 4.6), (0, 0.5, 0)), "lado": ((4.9, 1.05, 0), (0, 0.5, 0)),
          "aparador": ((-0.9, 1.35, 1.4), (-3.3, 0.6, -0.1)),
          "cima": ((0, 5.6, 0.01), (0, 0.7, 0)), "pormenor": ((1.75, 0.98, 1.0), (1.3, 0.72, 0.55)), "baixo": ((2.2, 0.12, 2.0), (0, 0.62, 0))}


def cadeiras_previa(K, n):
    """Chairs as the page places them: per side max(3, round((L-0.3)/0.78)) and one at each end."""
    col = bpy.data.collections.get("_cadeiras") or colecao("_cadeiras")
    for o in list(col.objects):
        bpy.data.objects.remove(o)
    fonte = list(bpy.data.collections["cadeira"].objects)
    L, W = 2.7 + n * LEAF, 1.2
    k = max(3, round((L - 0.3) / 0.78))
    span = L - 0.9
    pos = []
    for i in range(k):
        x = -span / 2 + span * i / (k - 1)
        pos += [(x, -(W / 2 + 0.12), 0.0), (x, W / 2 + 0.12, math.pi)]      # three z -> Blender -y
    pos += [(-(L / 2 + 0.18), 0, -math.pi / 2), (L / 2 + 0.18, 0, math.pi / 2)]
    for x, y, rz in pos:
        for o in fonte:
            c = o.copy()
            c.location = (x, y, 0)
            c.rotation_euler = (0, 0, rz)
            c.hide_render = False
            col.objects.link(c)


PAREDES = {"tras": ((0, RD / 2, 0), (0, -1, 0)), "frente": ((0, -RD / 2, 0), (0, 1, 0)), "esq": ((-RW / 2, 0, 0), (1, 0, 0)),
           "dir": ((RW / 2, 0, 0), (-1, 0, 0)), "teto": ((0, 0, RH), (0, 0, -1))}


def paredes_para(cam):
    """As the page does: a wall (or the ceiling) shows only when the camera is on the room's side of it."""
    for o in cena.objects:
        if o.get("parede"):
            pos, n = PAREDES[o["parede"]]
            o.hide_render = (Vector(cam) - Vector(pos)).dot(Vector(n)) <= 0


def previas(vistas, meia):
    from mathutils import Euler  # noqa: F401
    usar_gpu()
    cena.cycles.samples = int(opc("--amostras_previa", 256))
    cena.cycles.use_denoising = True
    cena.render.resolution_x, cena.render.resolution_y = (800, 450) if meia else (1600, 900)
    cena.render.image_settings.file_format = "JPEG"
    mostrar_mesa("A")
    for o in bpy.data.collections["cadeira"].objects:
        o.hide_render = True
    cadeiras_previa("A", 0)
    cam = bpy.data.cameras.new("previa")
    cam.sensor_fit = "VERTICAL"
    cam.angle_y = math.radians(38)
    ob = bpy.data.objects.new("previa", cam)
    cena.collection.objects.link(ob)
    cena.camera = ob
    for modo in ("dia", "noite"):
        modo_luz(modo)
        for v in vistas:
            p, t = VISTAS[v]
            pb, tb = Vector((p[0], -p[2], p[1])), Vector((t[0], -t[2], t[1]))
            ob.location = pb
            ob.rotation_euler = (tb - pb).to_track_quat("-Z", "Y").to_euler()
            paredes_para(pb)
            cena.render.filepath = os.path.join(SAIDA, f"previa_{modo}_{v}.jpg")
            t0 = time.time()
            bpy.ops.render.render(write_still=True)
            print("PREVIA", modo, v, round(time.time() - t0), "s")
    for o in cena.objects:
        if o.get("parede"):
            o.hide_render = False
    modo_luz("dia")


# ---------------------------------------------------------------------------------------------- exports
def imagens_leves(obs, limite_cor=2048, limite=1024):
    """The room's textures for the page: colour maps of the floor and walls at 2048, the rest at 1024, every map made
    RGB(A) (WebP has no one-channel images: the scanned models' roughness maps failed to export)."""
    feitos = {}
    for m in {m for o in obs for m in o.data.materials if m}:
        for n in m.node_tree.nodes:
            if n.type != "TEX_IMAGE" or not n.image or n.name == "LM":
                continue
            img = n.image
            if img.name in feitos:
                n.image = feitos[img.name]
                continue
            w, h = img.size
            if not w:
                continue
            grande = img.colorspace_settings.name != "Non-Color" and m.name in ("soalho", "parede", "teto")
            f = min(1.0, (limite_cor if grande else limite) / max(w, h))
            c = img.copy()
            nw, nh = max(1, int(w * f)), max(1, int(h * f))
            if f < 1:
                c.scale(nw, nh)
            px = np.array(c.pixels[:], dtype=np.float32)
            ch = len(px) // (nw * nh)
            px = px.reshape(nh, nw, ch)
            rgba = np.ones((nh, nw, 4), dtype=np.float32)
            rgba[..., :3] = px[..., :1] if ch < 3 else px[..., :3]
            if ch in (2, 4):
                rgba[..., 3] = px[..., ch - 1]
            alfa = bool(ch in (2, 4) and (rgba[..., 3] < 0.99).any())
            novo = bpy.data.images.new(img.name + "_web", nw, nh, alpha=alfa)
            novo.colorspace_settings.name = img.colorspace_settings.name
            novo.pixels.foreach_set(rgba.ravel())
            novo.pack()
            bpy.data.images.remove(c)
            feitos[img.name] = novo
            n.image = novo
    print("IMAGENS da sala:", len(feitos))


def exportar(obs, caminho, materiais="EXPORT", formato="AUTO"):
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.hide_viewport = False
        o.hide_set(False)
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.export_scene.gltf(filepath=caminho, export_format="GLB", use_selection=True, export_apply=True,
                              export_extras=True, export_materials=materiais, export_image_format=formato,
                              export_image_quality=85, export_texcoords=True, export_normals=True, export_yup=True,
                              export_cameras=False, export_lights=False)
    print("GLB", os.path.basename(caminho), round(os.path.getsize(caminho) / 1e6, 2), "MB")


def texturas_pagina():
    """The finishes' maps for the page, as WebP: colour at 4096 (2048 for phones), normal and roughness at 2048
    (1024), the linen and our own maps as they are."""
    feitas = {}
    for k, a in list(ACAB.items()) + [("tecido", CFG["tecido"])]:
        if not a.get("tex"):
            continue
        for mapa, nao_cor in (("Diffuse", False), ("nor_gl", True), ("Rough", True)):
            if k == "tecido" and mapa == "Diffuse":
                continue
            src = bpy.data.images.load(os.path.join(ATIVOS, a["tex"], f"{mapa}.jpg"), check_existing=False)
            for suf, lado in (("", 4096 if mapa == "Diffuse" else 2048), ("_m", 2048 if mapa == "Diffuse" else 1024)):
                im = src.copy()
                if im.size[0] > lado:
                    im.scale(lado, lado)
                ext = "webp" if mapa != "Rough" else "jpg"        # WebP has no one-channel images
                im.filepath_raw = os.path.join(TEX, f"{k}_{mapa}{suf}.{ext}")
                im.file_format = "WEBP" if ext == "webp" else "JPEG"
                try:
                    im.save(quality=88)
                except TypeError:
                    im.save()
                bpy.data.images.remove(im)
                feitas[f"{k}_{mapa}{suf}"] = f"{k}_{mapa}{suf}.{ext}"
            bpy.data.images.remove(src)
    return feitas


def main():
    t0 = time.time()
    if "--so_ceu" in ARGV:              # the sky panorama alone (no scene needed)
        luzes()
        usar_gpu()
        panorama("dia", ceu=True)
        return
    texturas_proprias()
    construir_mesa()
    construir_cadeira()
    construir_sala()
    luzes()
    for o in bpy.data.collections["cadeira"].objects:
        o.hide_render = True
    mostrar_mesa("A")
    todos = [o for g in SALA_OBS.values() for o in g]
    for grupo, obs in SALA_OBS.items():
        for o in obs:
            o["grupo"] = grupo
        if obs and grupo != "scan":
            uv_luz(obs)
    info = {"sol": {"de": LUZ["sol_de"], "forca": LUZ["sol_forca"]}, "exposicao": LUZ.get("exposicao", 0.0),
            "exposicao_noite": LUZ.get("exposicao_noite", 0.0),
            "noite": LUZ["noite"], "ceu_forca": LUZ["ceu_forca"]}
    if "--luz" in ARGV:
        cozer_luz(info)
        for modo in ("dia", "noite"):
            for o in [o for g in VAR.values() for k in ("L", "R", "C", "tabua") for o in g[k]]:
                o.hide_render = True
            panorama(modo)
        panorama("dia", ceu=True)
        sombras(info)
    if opc("--previa"):
        previas(opc("--previa").split(","), "--meia" in ARGV)
    if "--sem_exportar" in ARGV:
        print("FEITO", round(time.time() - t0), "s")
        return
    # exports: the table (every variant, at rest), the chair, the room
    for K in VAR:
        estado_mesa(K, 0, visiveis=True)
    mesa = [o for g in VAR.values() for k in ("L", "R", "C", "tabua") for o in g[k]]
    exportar(mesa, os.path.join(SAIDA, "mesa.glb"), "PLACEHOLDER")       # the page gives each part its finish
    exportar(list(bpy.data.collections["cadeira"].objects), os.path.join(SAIDA, "cadeira.glb"), "PLACEHOLDER")
    imagens_leves(todos)
    exportar(todos, os.path.join(SAIDA, "sala.glb"), formato="WEBP")
    info["texturas"] = texturas_pagina()
    json.dump(info, open(os.path.join(SAIDA, "luz.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if "--guardar" in ARGV:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, "mesa.blend"))
    print("FEITO", round(time.time() - t0), "s")


main()
