"""Blender: the client's house from a clean description (casa.json), with real materials, for the client page.

    blender -b --factory-startup -P ferramentas/pagina/casa_blender.py -- <casa.json> <saida/> [--render v1,v2|todas]
                                  [--amostras 160] [--res 1600x1000] [--sem-glb] [--previa] [--sem-relva]
  (--previa: half size; ~50 s per view on a GTX 1050 Ti at 32 samples. The first Cycles run compiles the GPU kernels.)
  --luz [--amostras_luz 200]: for the web model, bake the Cycles light (direct + bounced, diffuse) into lightmaps
  lm_casa/lm_exterior/lm_terreno.jpg (second UV 'lm' = TEXCOORD_1, K per map in luz.json), the sky as an equirect
  ceu.jpg (AgX like the images, centre = east) and leaf cards for the crowns (folha.png). ~10 min at 200 samples.

casa.json (local metres, x/y on the plan, z up from the reference floor; see gerar_casa in the project's _trabalho):
  materiais_cor   optional colour overrides {"ripado": "#6a4a35", ...}
  solidos   [{nome, caixa [x0,y0,z0,x1,y1,z1], mat, grupo, mats {base, topo, lados}}]   volumes that get carved
  vazios    [{caixa, em [solid names], mats {lados, chao, teto}}]   rooms, loggias, openings, roof wells
  caixas    [{caixa, mat, grupo}]                                     plain boxes (deck, copings, fins, slabs)
  vaos      [{caixa, eixo x|y, plano, paineis, tipo correr|janela|fixo|porta|garagem, grupo}] frames, glass, leaves
  guardas   [{de [x,y], ate [x,y], z0, altura, grupo}]               glass balustrades
  muros     [{pontos [[x,y,zbase,ztopo],...], esp, mat, grupo}]       walls along a line, top following the ground
  pisos_livres [{pontos [[x,y,z],...], mat, grupo}]                  a polygon surface (ramp floor)
  toros     [{pontos [[x,y,z],...], passo, altura, diam, grupo}]      timber log fence along a line (base at z);
            passo >= 1.5 m: posts with a three-wire sheep net
  faixas    [{a [[x,y,z],...], b [...] (same count), mat}]          a strip between two lines (a road between kerbs)
  terreno   {xs [...], ys [...], z [ny][nx], mat [ny-1][nx-1] (codes, -1 = hole), mats [names]}
            Renders: hair grass on "relva"/"relva_fora" (straight up, no children, the ground casts no shadow: each
            of those three avoided a patchwork of ground triangles).
  arvores   [{x, y, z, altura, copa}]   trunk + low-poly crown (web, maquette); leaves in clumps for the renders
  vistas    [{nome, camara [x,y,z], alvo [x,y,z], lente, panorama (equirect 360°, centre = alvo), res "WxH",
             exposicao (this view's exposure, e.g. brighter inside)}]
  terreno.cor  optional [ny-1][nx-1] RGB (sRGB 0-1) per cell for the material "solo" (the surroundings' ground)
  envolvente   (renders only; ferramentas/pagina/envolvente.py + the project's generator) {casas [{pontos [[x,y]],
            z0, zc, altura, telhado aguas|plano, estufa, tom, cor_cob (roof colour), moderna (large windows, parapet)}],
            estradas [{pontos [[x,y,z]], largura, mat}],
            arvores [[x, y, z, variante 0-8, altura, rotacao]], mar {z, raio, curvatura}, neblina {distancia}}:
            hipped tile roofs, rendered walls with windows, trees as instances, the sea following the earth's curve,
            far things fade into the sky's own colour (aerial perspective)
  rodar_graus   rotation of the whole model about z (plan frame -> north up)
  sol       {azimute (deg from north, clockwise), elevacao}
Output: casa.glb (web, textures 1024 px JPEG, groups in extras), casa.blend, render_<vista>.jpg (Cycles), texturas/.
"""
import json
import math
import os
import sys

import bmesh
import bpy
import numpy as np

# ---------------------------------------------------------------------------------------------- arguments
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ESPEC, SAIDA = os.path.abspath(argv[0]), os.path.abspath(argv[1])
OPC = {"render": "", "amostras": "160", "res": "1600x1000"}
i = 2
while i < len(argv):
    a = argv[i]
    if a in ("--sem-glb", "--previa", "--sem-relva", "--luz"):
        OPC[a[2:]] = True
        i += 1
    else:
        OPC[a[2:]] = argv[i + 1]
        i += 2
os.makedirs(os.path.join(SAIDA, "texturas"), exist_ok=True)
E = json.load(open(ESPEC, encoding="utf-8"))
bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene
RAIZ = bpy.data.objects.new("casa", None)
cena.collection.objects.link(RAIZ)
CORTADORES = bpy.data.collections.new("cortadores")
cena.collection.children.link(CORTADORES)
RNG = np.random.default_rng(7)


# ---------------------------------------------------------------------------------------------- textures (numpy)
def ruido(n, celulas, oitavas=4, semente=0):
    """Tileable value noise in [0,1], n x n."""
    rng = np.random.default_rng(semente)
    out = np.zeros((n, n))
    amp, tot = 1.0, 0.0
    for o in range(oitavas):
        c = celulas * 2 ** o
        g = rng.random((c, c))
        t = np.arange(n) * c / n
        i0 = np.floor(t).astype(int) % c
        i1 = (i0 + 1) % c
        f = t - np.floor(t)
        f = f * f * (3 - 2 * f)
        a = g[i0][:, i0] * (1 - f)[None, :] + g[i0][:, i1] * f[None, :]
        b = g[i1][:, i0] * (1 - f)[None, :] + g[i1][:, i1] * f[None, :]
        out += amp * (a * (1 - f)[:, None] + b * f[:, None])
        tot += amp
        amp *= 0.5
    return out / tot


def ruido_esticado(n, cu, cv, semente):
    """Noise stretched along v (wood grain): few cells across, many along."""
    rng = np.random.default_rng(semente)
    g = rng.random((cv, cu))
    tu, tv = np.arange(n) * cu / n, np.arange(n) * cv / n
    iu0, iv0 = np.floor(tu).astype(int) % cu, np.floor(tv).astype(int) % cv
    iu1, iv1 = (iu0 + 1) % cu, (iv0 + 1) % cv
    fu, fv = tu - np.floor(tu), tv - np.floor(tv)
    a = g[iv0][:, iu0] * (1 - fu) + g[iv0][:, iu1] * fu
    b = g[iv1][:, iu0] * (1 - fu) + g[iv1][:, iu1] * fu
    return a * (1 - fv)[:, None] + b * fv[:, None]


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[k:k + 2], 16) / 255 for k in (0, 2, 4)])


def tabuas(n, nt, cor, var=0.12, junta=0.07, escuro=0.35, comprimentos=None, semente=1):
    """Boards running along v (columns along u). Returns colour (n,n,3) and height (n,n)."""
    u = (np.arange(n) + 0.5) / n
    k = np.floor(u * nt).astype(int)
    fr = u * nt - k
    rng = np.random.default_rng(semente)
    tom = 1 + (rng.random(nt) - 0.5) * 2 * var
    mat = 1 + (rng.random(nt) - 0.5) * 0.10
    grao = ruido_esticado(n, nt * 6, 3, semente + 1)
    fio = ruido_esticado(n, nt * 40, 8, semente + 2)
    v = np.linspace(0, 1, n, endpoint=False)
    col = np.ones((n, n, 3)) * cor[None, None, :]
    f = (tom[k])[None, :] * (0.86 + 0.18 * grao + 0.10 * (fio - 0.5))
    col = col * f[:, :, None]
    col[:, :, 0] *= mat[k][None, :]
    h = np.ones((n, n))
    borda = np.minimum(fr, 1 - fr)
    g = borda < junta / 2
    col[:, g] *= escuro
    h[:, g] = 0.0
    h = h - 0.15 * np.clip((junta * 1.5 - borda) / (junta * 1.5), 0, 1)[None, :]
    if comprimentos:       # board ends: a joint across each board at a random v
        for b in range(nt):
            for _ in range(comprimentos):
                vv = rng.random()
                linha = np.abs(((v - vv + 0.5) % 1) - 0.5) < 0.004
                cols = k == b
                col[np.ix_(linha, cols)] *= escuro + 0.2
                h[np.ix_(linha, cols)] = 0.2
    h += 0.04 * (fio - 0.5)
    return np.clip(col, 0, 1), h


def normal_de(h, forca):
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * forca
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * forca
    nrm = np.dstack([-dx, -dy, np.ones_like(h)])
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    return nrm * 0.5 + 0.5


def imagem(nome, arr, nao_cor=False):
    n = arr.shape[0]
    rgba = np.ones((n, n, 4), dtype=np.float32)
    rgba[:, :, :3] = arr[::-1]          # Blender rows go bottom-up
    img = bpy.data.images.new(nome, n, n, alpha=False, is_data=nao_cor)
    if nao_cor:
        img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(rgba.ravel())
    img.update()
    caminho = os.path.join(SAIDA, "texturas", nome + ".png")
    img.filepath_raw = caminho
    img.file_format = "PNG"
    img.save()
    return img


COR = {"ripado": "#5c3f2c", "deck": "#8f6c4c", "soalho": "#c09e78", "interior": "#eeebe4", "betao": "#a6a39c",
       "painel": "#45322e", "metal": "#383e42", "pedra": "#c8b68f", "relva": "#6f7d3a", "relva_fora": "#66733a",
       "asfalto": "#3a3a3a", "berma": "#56703a", "brita": "#a49d90", "porta_garagem": "#5c3f2c", "tecido": "#9c968c", "toros": "#9a7a55"}
COR.update(E.get("materiais_cor", {}))
TILE = {"berma": 3.0, "ripado": 1.2, "deck": 1.4, "soalho": 1.8, "betao": 2.4, "painel": 1.0, "relva": 3.0, "relva_fora": 3.0,
        "asfalto": 3.0, "brita": 1.5, "pedra": 1.2, "porta_garagem": 1.2, "interior": 2.0, "metal": 1.0,
        "tecido": 1.0, "toros": 1.0}
N = 1024


def gerar_texturas():
    T = {}
    c, h = tabuas(N, 10, hex_rgb(COR["ripado"]), var=0.16, junta=0.08, escuro=0.25, semente=3)
    T["ripado"] = (c, normal_de(h, 6.0), 0.78)
    c, h = tabuas(N, 10, hex_rgb(COR["deck"]), var=0.14, junta=0.06, escuro=0.3, comprimentos=1, semente=5)
    T["deck"] = (c, normal_de(h, 5.0), 0.7)
    c, h = tabuas(N, 10, hex_rgb(COR["soalho"]), var=0.08, junta=0.015, escuro=0.7, comprimentos=1, semente=9)
    T["soalho"] = (c, normal_de(h, 2.0), 0.45)
    c, h = tabuas(N, 10, hex_rgb(COR["porta_garagem"]), var=0.12, junta=0.06, escuro=0.3, semente=11)
    T["porta_garagem"] = (np.transpose(c, (1, 0, 2)).copy(), normal_de(h.T.copy(), 5.0), 0.75)
    c, h = tabuas(N, 4, hex_rgb(COR["toros"]), var=0.18, junta=0.0, escuro=1.0, semente=13)
    T["toros"] = (c, normal_de(h, 1.5), 0.8)
    r = ruido(N, 8, 5, 21)
    r2 = ruido(N, 64, 2, 22)
    base = hex_rgb(COR["betao"])
    col = base[None, None, :] * (0.88 + 0.16 * r + 0.06 * (r2 - 0.5))[:, :, None]
    junta = (np.abs(((np.arange(N) / N * 2) % 1) - 0.0) < 0.002)
    col[junta, :] *= 0.8
    col[:, junta] *= 0.8
    T["betao"] = (np.clip(col, 0, 1), normal_de(0.3 * r + 0.2 * r2, 2.0), 0.85)
    u = np.arange(N) / N * 5
    fr = u - np.floor(u)
    perfil = np.clip(1 - np.abs(fr - 0.12) / 0.07, 0, 1)        # one rib every 0.2 m
    hp = np.tile(perfil, (N, 1))
    col = hex_rgb(COR["painel"])[None, None, :] * (0.92 + 0.08 * ruido(N, 4, 2, 31))[:, :, None]
    T["painel"] = (col, normal_de(hp, 8.0), 0.45)
    for nome, sem, mix in (("relva", 41, 1.0), ("relva_fora", 43, 0.85), ("berma", 45, 0.85)):
        a, b = ruido(N, 6, 5, sem), ruido(N, 48, 3, sem + 1)
        verde, palha, escuro_ = hex_rgb(COR[nome]), np.array([0.55, 0.52, 0.30]), np.array([0.25, 0.32, 0.14])
        t = np.clip((a - 0.45) * 2.5, 0, 1)[:, :, None]
        col = verde * (1 - t) + palha * t
        col = col * (0.75 + 0.5 * b[:, :, None])
        col = col * (1 - 0.35 * np.clip((0.5 - b) * 3, 0, 1)[:, :, None]) + escuro_ * 0.0
        T[nome] = (np.clip(col * mix + (1 - mix) * verde, 0, 1), normal_de(b * 0.6 + a * 0.2, 3.0), 0.95)
    for nome, sem, k in (("asfalto", 51, 0.18), ("brita", 53, 0.35), ("pedra", 55, 0.12)):
        a, b = ruido(N, 128, 2, sem), ruido(N, 10, 4, sem + 1)
        col = hex_rgb(COR[nome])[None, None, :] * (1 - k / 2 + k * a + 0.06 * (b - 0.5))[:, :, None]
        T[nome] = (np.clip(col, 0, 1), normal_de(a, 4.0 if nome == "brita" else 1.0), 0.9 if nome != "pedra" else 0.6)
    return T


# ---------------------------------------------------------------------------------------------- materials
MATS = {}


def no(nt, tipo, x, y):
    n = nt.nodes.new(tipo)
    n.location = (x, y)
    return n


def principled(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def mat_textura(nome, cor, normal, rug, metal=0.0):
    m = bpy.data.materials.new(nome)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    bsdf = principled(m)
    bsdf.inputs["Roughness"].default_value = rug
    bsdf.inputs["Metallic"].default_value = metal
    ic = no(nt, "ShaderNodeTexImage", -500, 200)
    ic.image = imagem(nome + "_cor", cor)
    nt.links.new(ic.outputs["Color"], bsdf.inputs["Base Color"])
    inn = no(nt, "ShaderNodeTexImage", -500, -200)
    inn.image = imagem(nome + "_normal", normal, nao_cor=True)
    nm = no(nt, "ShaderNodeNormalMap", -200, -200)
    nt.links.new(inn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def mat_simples(nome, cor, rug=0.8, metal=0.0):
    m = bpy.data.materials.new(nome)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = principled(m)
    b.inputs["Base Color"].default_value = (*[c ** 2.2 for c in hex_rgb(cor)], 1)
    b.inputs["Roughness"].default_value = rug
    b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*[c ** 2.2 for c in hex_rgb(cor)], 1)
    return m


def mat_vidro(nome, rug=0.0, cor=(0.92, 0.96, 0.95)):
    m = bpy.data.materials.new(nome)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = principled(m)
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Roughness"].default_value = rug
    for k in ("Transmission Weight", "Transmission"):
        if k in b.inputs:
            b.inputs[k].default_value = 1.0
            break
    b.inputs["IOR"].default_value = 1.5
    m.diffuse_color = (*cor, 0.3)
    return m


def criar_materiais():
    T = gerar_texturas()
    for nome, (c, nrm, rug) in T.items():
        MATS[nome] = mat_textura(nome, c, nrm, rug, metal=0.25 if nome == "painel" else 0.0)
    MATS["interior"] = mat_simples("interior", COR["interior"], 0.85)
    MATS["metal"] = mat_simples("metal", COR["metal"], 0.38, 0.6)
    MATS["tecido"] = mat_simples("tecido", COR["tecido"], 0.95)
    MATS["vidro"] = mat_vidro("vidro")
    MATS["vidro_guarda"] = mat_vidro("vidro_guarda", 0.12, (0.95, 0.97, 0.97))
    MATS["forro"] = MATS["ripado"]
    if (E.get("terreno") or {}).get("cor"):
        MATS["solo"] = mat_solo()


def mat_solo():
    """The surroundings' ground: the cell colour (attribute cor_solo) with large and small mottling, a little bump."""
    m = bpy.data.materials.new("solo")
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = principled(m)
    at = no(nt, "ShaderNodeAttribute", -900, 300)
    at.attribute_name = "cor_solo"
    tc = no(nt, "ShaderNodeTexCoord", -1300, 0)
    r1 = no(nt, "ShaderNodeTexNoise", -1000, 0)
    r1.inputs["Scale"].default_value = 0.06
    r1.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], r1.inputs["Vector"])
    r2 = no(nt, "ShaderNodeTexNoise", -1000, -250)
    r2.inputs["Scale"].default_value = 1.2
    nt.links.new(tc.outputs["Object"], r2.inputs["Vector"])
    v1 = no(nt, "ShaderNodeMapRange", -750, 0)
    v1.inputs["To Min"].default_value, v1.inputs["To Max"].default_value = 0.72, 1.25
    nt.links.new(r1.outputs["Fac"], v1.inputs["Value"])
    v2 = no(nt, "ShaderNodeMapRange", -750, -250)
    v2.inputs["To Min"].default_value, v2.inputs["To Max"].default_value = 0.85, 1.12
    nt.links.new(r2.outputs["Fac"], v2.inputs["Value"])
    k = no(nt, "ShaderNodeMath", -550, -100)
    k.operation = "MULTIPLY"
    nt.links.new(v1.outputs["Result"], k.inputs[0])
    nt.links.new(v2.outputs["Result"], k.inputs[1])
    mul = no(nt, "ShaderNodeVectorMath", -350, 200)
    mul.operation = "SCALE"
    nt.links.new(at.outputs["Color"], mul.inputs[0])
    nt.links.new(k.outputs["Value"], mul.inputs["Scale"])
    nt.links.new(mul.outputs["Vector"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    bp = no(nt, "ShaderNodeBump", -350, -250)
    bp.inputs["Strength"].default_value = 0.25
    nt.links.new(r2.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    m.diffuse_color = (0.25, 0.3, 0.12, 1)
    return m


# ---------------------------------------------------------------------------------------------- geometry helpers
def ligar(ob, grupo):
    cena.collection.objects.link(ob)
    ob.parent = RAIZ
    ob["grupo"] = grupo or "casa"
    return ob


def malha_caixa(nome, cx, mats_faces):
    """Box mesh with per-face materials. mats_faces: dict side -> material name (x0,x1,y0,y1,z0,z1)."""
    x0, y0, z0, x1, y1, z1 = cx
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = {"z0": (0, 3, 2, 1), "z1": (4, 5, 6, 7), "y0": (0, 1, 5, 4), "y1": (2, 3, 7, 6), "x0": (3, 0, 4, 7), "x1": (1, 2, 6, 5)}
    me = bpy.data.meshes.new(nome)
    ordem = list(f)
    me.from_pydata(v, [], [f[k] for k in ordem])
    nomes = []
    for k in ordem:
        mn = mats_faces.get(k)
        if mn not in nomes:
            nomes.append(mn)
    for mn in nomes:
        me.materials.append(MATS[mn])
    me.polygons.foreach_set("material_index", [nomes.index(mats_faces.get(k)) for k in ordem])
    me.update()
    return me


def faces_mats(base, topo=None, fundo=None, lados=None):
    lados = lados or base
    return {"x0": lados, "x1": lados, "y0": lados, "y1": lados, "z0": fundo or base, "z1": topo or base}


def caixa(nome, cx, mat, grupo, mats=None):
    me = malha_caixa(nome, cx, mats or faces_mats(mat))
    return ligar(bpy.data.objects.new(nome, me), grupo)


def poligono_extrudido(nome, pts, z0, z1, mat, grupo):
    bm = bmesh.new()
    base = [bm.verts.new((x, y, z0)) for x, y in pts]
    face = bm.faces.new(base)
    bmesh.ops.recalc_face_normals(bm, faces=[face])
    if face.normal.z > 0:
        face.normal_flip()
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    vs = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=vs, vec=(0, 0, z1 - z0))
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(MATS[mat])
    return ligar(bpy.data.objects.new(nome, me), grupo)


# ---------------------------------------------------------------------------------------------- UVs by world position
def uvs_mundo(ob):
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    mw = ob.matrix_basis
    nomes = [m.name if m else "" for m in me.materials]
    for p in me.polygons:
        n = p.normal
        t = TILE.get(nomes[p.material_index].split(".")[0], 1.2) if nomes else 1.2
        for li in p.loop_indices:
            co = mw @ me.vertices[me.loops[li].vertex_index].co
            if abs(n.z) > 0.7:
                uv[li].uv = (co.x / t, co.y / t)
            elif abs(n.x) >= abs(n.y):
                uv[li].uv = (co.y / t, co.z / t)
            else:
                uv[li].uv = (co.x / t, co.z / t)


# ---------------------------------------------------------------------------------------------- the house
def construir_solidos():
    sol = {}
    for s in E.get("solidos", []):
        mm = s.get("mats", {})
        ob = caixa(s["nome"], s["caixa"], None, s.get("grupo"),
                   faces_mats(mm.get("base", s["mat"]), mm.get("topo", "interior"), mm.get("fundo", "interior"),
                              mm.get("lados", s["mat"])))
        ob["cortes"] = []
        sol[s["nome"]] = ob
    for k, v in enumerate(E.get("vazios", [])):
        mm = v.get("mats", {})
        x0, y0, z0, x1, y1, z1 = v["caixa"]
        alvos = v.get("em") or [n for n, ob in sol.items() if _sobrepoe(E_solido(n)["caixa"], v["caixa"])]
        me = malha_caixa(f"vazio{k}", v["caixa"], faces_mats(mm.get("lados", "interior"), mm.get("teto", "interior"),
                                                              mm.get("chao", "soalho"), mm.get("lados", "interior")))
        # the cutter's faces point inward into the solid after the difference: flip so the result keeps them right
        cut = bpy.data.objects.new(f"vazio{k}", me)
        CORTADORES.objects.link(cut)
        cut.hide_render = True
        cut.display_type = "WIRE"
        for n in alvos:
            if n in sol:
                sol[n]["cortes"] = list(sol[n]["cortes"]) + [cut.name]
    dg = None
    for n, ob in sol.items():
        cortes = list(ob["cortes"])
        if not cortes:
            continue
        col = bpy.data.collections.new("c_" + n)
        for cn in cortes:
            col.objects.link(bpy.data.objects[cn])
        mod = ob.modifiers.new("vazios", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.operand_type = "COLLECTION"
        mod.collection = col
        mod.solver = "EXACT"
        try:
            mod.material_mode = "TRANSFER"
        except Exception:
            pass
        dg = bpy.context.evaluated_depsgraph_get()
        me2 = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        ob.modifiers.clear()
        velho = ob.data
        ob.data = me2
        bpy.data.meshes.remove(velho)
    for ob in list(CORTADORES.objects):
        bpy.data.objects.remove(ob)
    return sol


def E_solido(nome):
    return next(s for s in E["solidos"] if s["nome"] == nome)


def _sobrepoe(a, b):
    return a[0] < b[3] and b[0] < a[3] and a[1] < b[4] and b[1] < a[4] and a[2] < b[5] and b[2] < a[5]


def construir_vaos():
    for k, v in enumerate(E.get("vaos", [])):
        x0, y0, z0, x1, y1, z1 = v["caixa"]
        g = v.get("grupo")
        eixo, pl = v["eixo"], v["plano"]
        tipo = v.get("tipo", "correr")
        n = max(1, int(v.get("paineis", 1)))
        p = 0.06       # frame profile
        d = 0.07       # frame depth

        def peca(nome, a0, a1, b0, b1, prof, mat):     # a along the wall, b = z, prof = depth around the plane
            if eixo == "x":     # wall normal along x: runs along y
                return caixa(nome, [pl - prof / 2, a0, b0, pl + prof / 2, a1, b1], mat, g)
            return caixa(nome, [a0, pl - prof / 2, b0, a1, pl + prof / 2, b1], mat, g)
        a0, a1 = (y0, y1) if eixo == "x" else (x0, x1)
        peca(f"vao{k}_aro_b", a0, a1, z0, z0 + p * 0.6, d, "metal")
        peca(f"vao{k}_aro_t", a0, a1, z1 - p, z1, d, "metal")
        peca(f"vao{k}_aro_e", a0, a0 + p, z0, z1, d, "metal")
        peca(f"vao{k}_aro_d", a1 - p, a1, z0, z1, d, "metal")
        if tipo in ("porta", "garagem"):
            peca(f"vao{k}_folha", a0 + p, a1 - p, z0 + 0.01, z1 - p, 0.05, "porta_garagem" if tipo == "garagem" else "ripado")
            continue
        larg = (a1 - a0 - 2 * p) / n
        for j in range(1, n):
            c = a0 + p + j * larg
            peca(f"vao{k}_mont{j}", c - p / 2, c + p / 2, z0, z1, d, "metal")
        peca(f"vao{k}_vidro", a0 + p, a1 - p, z0 + p * 0.6, z1 - p, 0.024, "vidro")


def construir_extras():
    for k, c in enumerate(E.get("caixas", [])):
        caixa(c.get("nome", f"caixa{k}"), c["caixa"], c["mat"], c.get("grupo"),
              faces_mats(c["mat"], c.get("topo"), c.get("fundo"), c.get("lados")))
    for k, gd in enumerate(E.get("guardas", [])):
        (xa, ya), (xb, yb) = gd["de"], gd["ate"]
        z0, h = gd["z0"], gd.get("altura", 1.1)
        if abs(xb - xa) < abs(yb - ya):
            caixa(f"guarda{k}", [xa - 0.01, min(ya, yb), z0, xa + 0.01, max(ya, yb), z0 + h], "vidro_guarda", gd.get("grupo"))
            caixa(f"guarda{k}_base", [xa - 0.03, min(ya, yb), z0, xa + 0.03, max(ya, yb), z0 + 0.06], "metal", gd.get("grupo"))
        else:
            caixa(f"guarda{k}", [min(xa, xb), ya - 0.01, z0, max(xa, xb), ya + 0.01, z0 + h], "vidro_guarda", gd.get("grupo"))
            caixa(f"guarda{k}_base", [min(xa, xb), ya - 0.03, z0, max(xa, xb), ya + 0.03, z0 + 0.06], "metal", gd.get("grupo"))
    for k, mu in enumerate(E.get("muros", [])):
        pts, esp = mu["pontos"], mu.get("esp", 0.3)
        bm = bmesh.new()
        lados = []
        for j, (x, y, zb, zt) in enumerate(pts):
            a = pts[max(j - 1, 0)]
            b = pts[min(j + 1, len(pts) - 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L * esp / 2, dx / L * esp / 2
            lados.append([bm.verts.new((x + nx, y + ny, zb)), bm.verts.new((x - nx, y - ny, zb)),
                          bm.verts.new((x - nx, y - ny, zt)), bm.verts.new((x + nx, y + ny, zt))])
        for a, b in zip(lados, lados[1:]):
            for q in range(4):
                bm.faces.new((a[q], a[(q + 1) % 4], b[(q + 1) % 4], b[q]))
        bm.faces.new(list(reversed(lados[0])))
        bm.faces.new(lados[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(f"muro{k}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(MATS[mu.get("mat", "betao")])
        ligar(bpy.data.objects.new(f"muro{k}", me), mu.get("grupo", "envolvente"))
    for k, pl in enumerate(E.get("pisos_livres", [])):
        bm = bmesh.new()
        vs = [bm.verts.new(tuple(p)) for p in pl["pontos"]]
        f = bm.faces.new(vs)
        if f.normal.z < 0:
            f.normal_flip()
        me = bpy.data.meshes.new(f"piso_livre{k}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(MATS[pl.get("mat", "betao")])
        ligar(bpy.data.objects.new(f"piso_livre{k}", me), pl.get("grupo", "envolvente"))
    for k, fx in enumerate(E.get("faixas", [])):
        A_, B_ = fx["a"], fx["b"]
        n = len(A_)
        verts = [tuple(p) for p in A_] + [tuple(p) for p in B_]
        faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
        me = bpy.data.meshes.new(f"faixa{k}")
        me.from_pydata(verts, [], faces)
        me.update()
        for p in me.polygons:
            if p.normal.z < 0:
                p.flip()
        me.update()
        me.materials.append(MATS[fx.get("mat", "asfalto")])
        ligar(bpy.data.objects.new(f"faixa{k}", me), fx.get("grupo", "terreno"))
    # timber logs: one mesh per fence (all logs joined), cylinders of 9 sides
    for k, t in enumerate(E.get("toros", [])):
        bm = bmesh.new()
        r, h, passo = t.get("diam", 0.1) / 2, t.get("altura", 0.9), t.get("passo", 0.2)
        pts = t["pontos"]
        for (xa, ya, za), (xb, yb, zb) in zip(pts, pts[1:]):
            L = math.hypot(xb - xa, yb - ya)
            m = max(1, int(L / passo))
            for j in range(m):
                f = (j + 0.5) / m
                x, y, z = xa + (xb - xa) * f, ya + (yb - ya) * f, za + (zb - za) * f
                hh = h * (1 + (RNG.random() - 0.5) * 0.06)
                res = bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=r, radius2=r, depth=hh + 0.3)
                bmesh.ops.translate(bm, verts=res["verts"], vec=(x, y, z + (hh - 0.3) / 2))
        me = bpy.data.meshes.new(f"toros{k}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(MATS["toros"])
        ligar(bpy.data.objects.new(f"toros{k}", me), t.get("grupo", "envolvente"))
        if passo >= 1.5:          # posts with a sheep net: three wires
            from mathutils import Vector
            bm = bmesh.new()
            for (xa, ya, za), (xb, yb, zb) in zip(pts, pts[1:]):
                a, b = Vector((xa, ya, za)), Vector((xb, yb, zb))
                d = b - a
                if d.length < 0.05:
                    continue
                rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix()
                for hw in (0.2, 0.5, 0.8):
                    res = bmesh.ops.create_cone(bm, cap_ends=False, segments=4, radius1=0.004, radius2=0.004, depth=d.length)
                    bmesh.ops.rotate(bm, verts=res["verts"], cent=(0, 0, 0), matrix=rot)
                    bmesh.ops.translate(bm, verts=res["verts"], vec=(a + b) / 2 + Vector((0, 0, hw * h)))
            me = bpy.data.meshes.new(f"rede{k}")
            bm.to_mesh(me)
            bm.free()
            me.materials.append(MATS["metal"])
            ligar(bpy.data.objects.new(f"rede{k}", me), t.get("grupo", "envolvente"))


ARVORES = []


def construir_arvores():
    if not E.get("arvores"):
        return
    MATS["tronco"] = mat_simples("tronco", "#4b4036", 0.9)
    MATS["copa"] = mat_simples("copa", "#566f34", 0.9)
    for k, t in enumerate(E["arvores"]):
        x, y, z, h, c = t["x"], t["y"], t["z"], t.get("altura", 7.0), t.get("copa", 2.2)
        bm = bmesh.new()
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.04 * h / 2.5, radius2=0.05, depth=h * 0.62)
        bmesh.ops.translate(bm, verts=res["verts"], vec=(x, y, z + h * 0.31 - 0.05))
        me = bpy.data.meshes.new(f"tronco{k}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(MATS["tronco"])
        ligar(bpy.data.objects.new(f"tronco{k}", me), "envolvente")
        bm = bmesh.new()
        rng = np.random.default_rng(100 + k)
        for j in range(4):
            r = c * (0.75 if j == 0 else 0.5 + 0.15 * rng.random())
            ang = rng.random() * 2 * math.pi
            off = 0 if j == 0 else c * 0.45
            res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
            bmesh.ops.translate(bm, verts=res["verts"], vec=(x + off * math.cos(ang), y + off * math.sin(ang),
                                                             z + h - c * 0.95 + (0 if j == 0 else (rng.random() - 0.3) * c * 0.5)))
        me = bpy.data.meshes.new(f"copa{k}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(MATS["copa"])
        for p in me.polygons:
            p.use_smooth = True
        ob = ligar(bpy.data.objects.new(f"copa{k}", me), "envolvente")
        ARVORES.append((ob, x, y, z + h - c * 0.95, c))


def folhas_cycles():
    """For the renders, the low-poly crowns give way to leaves: small cards in clumps, denser near each clump's
    surface, random orientation and tone (one mesh for all trees)."""
    if not ARVORES:
        return
    V, F, T = [], [], []
    base = 0
    for k, (copa, x, y, zc, c) in enumerate(ARVORES):
        copa.hide_render = True
        rng = np.random.default_rng(300 + k)
        nc = 7
        cent = np.zeros((nc, 3))
        raio = np.zeros(nc)
        cent[0] = (x, y, zc)
        raio[0] = c * 0.62
        for j in range(1, nc):
            d = rng.normal(size=3)
            d /= np.linalg.norm(d)
            d[2] = abs(d[2]) * 0.6 - 0.15
            cent[j] = (x, y, zc) + d * c * rng.uniform(0.35, 0.6) * np.array([1, 1, 0.8])
            raio[j] = c * rng.uniform(0.38, 0.55)
        n = int(26000 * (c / 2.2) ** 2)
        peso = raio ** 3 / (raio ** 3).sum()
        qual = rng.choice(nc, size=n, p=peso)
        d = rng.normal(size=(n, 3))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        r = raio[qual] * rng.random(n) ** 0.3
        p = cent[qual] + d * r[:, None] * np.array([1, 1, 0.85])
        a = rng.normal(size=(n, 3))
        a /= np.linalg.norm(a, axis=1, keepdims=True)
        b = np.cross(a, rng.normal(size=(n, 3)))
        b /= np.linalg.norm(b, axis=1, keepdims=True)
        esc = rng.uniform(0.7, 1.35, n)[:, None]
        L, W = 0.085 * esc, 0.05 * esc
        quad = np.stack([p - a * L, p - b * W, p + a * L, p + b * W], axis=1)
        V.append(quad.reshape(-1, 3))
        F.append(base + np.arange(n * 4).reshape(n, 4))
        T.append(rng.random(n))
        base += n * 4
    V, F, T = np.concatenate(V), np.concatenate(F), np.concatenate(T)
    me = bpy.data.meshes.new("folhas")
    me.from_pydata(V.tolist(), [], F.tolist())
    at = me.attributes.new("variacao", "FLOAT", "FACE")
    at.data.foreach_set("value", T.astype(np.float32))
    m = bpy.data.materials.new("folha")
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = principled(m)
    out = next(nd for nd in nt.nodes if nd.type == "OUTPUT_MATERIAL")
    attr = no(nt, "ShaderNodeAttribute", -800, 200)
    attr.attribute_name = "variacao"
    rampa = no(nt, "ShaderNodeValToRGB", -550, 200)
    rampa.color_ramp.elements[0].color = (0.035, 0.075, 0.015, 1)
    rampa.color_ramp.elements[1].color = (0.20, 0.25, 0.05, 1)
    el = rampa.color_ramp.elements.new(0.6)
    el.color = (0.08, 0.15, 0.03, 1)
    nt.links.new(attr.outputs["Fac"], rampa.inputs["Fac"])
    nt.links.new(rampa.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.5
    tr = no(nt, "ShaderNodeBsdfTranslucent", -200, -200)
    nt.links.new(rampa.outputs["Color"], tr.inputs["Color"])
    mix = no(nt, "ShaderNodeMixShader", 200, 100)
    mix.inputs["Fac"].default_value = 0.3
    nt.links.new(b.outputs["BSDF"], mix.inputs[1])
    nt.links.new(tr.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    me.materials.append(m)
    ob = bpy.data.objects.new("folhas", me)
    cena.collection.objects.link(ob)
    ob.parent = RAIZ


def construir_terreno():
    T = E.get("terreno")
    if not T:
        return None
    xs, ys, Z, M = T["xs"], T["ys"], T["z"], T["mat"]
    nomes = T["mats"]
    nx, ny = len(xs), len(ys)
    me = bpy.data.meshes.new("terreno")
    verts = [(xs[i], ys[j], Z[j][i]) for j in range(ny) for i in range(nx)]
    faces, mi, cores = [], [], []
    CT = T.get("cor")
    for j in range(ny - 1):
        for i in range(nx - 1):
            c = M[j][i]
            if c < 0:
                continue
            a = j * nx + i
            faces.append((a, a + 1, a + nx + 1, a + nx))
            mi.append(c)
            if CT:
                q = CT[j][i] or (0.3, 0.4, 0.2)
                cores += [q[0] ** 2.2, q[1] ** 2.2, q[2] ** 2.2, 1.0]
    me.from_pydata(verts, [], faces)
    if CT:
        at = me.attributes.new("cor_solo", "FLOAT_COLOR", "FACE")
        at.data.foreach_set("color", cores)
    for n in nomes:
        me.materials.append(MATS[n])
    me.polygons.foreach_set("material_index", mi)
    me.update()
    # triangulate once: the grass grows on these very triangles (a quad split differently buried half the grass)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return ligar(bpy.data.objects.new("terreno", me), "terreno")


def relva_cycles(terreno, nome="relva", densidade=900, raio=None):
    """Hair grass on the meadow faces (render only, never exported)."""
    T = E["terreno"]
    if nome not in T["mats"]:
        return None
    k = T["mats"].index(nome)
    cx, cy = E.get("centro", [0, 0])
    me = terreno.data.copy()
    bm = bmesh.new()
    bm.from_mesh(me)
    fora = [f for f in bm.faces if f.material_index != k
            or (raio and math.hypot(f.calc_center_median().x - cx, f.calc_center_median().y - cy) > raio)]
    bmesh.ops.delete(bm, geom=fora, context="FACES")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("relva_" + nome, me)
    cena.collection.objects.link(ob)
    ob.parent = RAIZ
    ob.location.z = 0.01
    m = bpy.data.materials.new("relva_fios")
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = principled(m)
    info = no(nt, "ShaderNodeHairInfo", -700, 200)
    rampa = no(nt, "ShaderNodeValToRGB", -450, 200)
    rampa.color_ramp.elements[0].color = (0.06, 0.12, 0.02, 1)
    rampa.color_ramp.elements[1].color = (0.30, 0.30, 0.10, 1)
    el = rampa.color_ramp.elements.new(0.7)
    el.color = (0.11, 0.19, 0.04, 1)
    nt.links.new(info.outputs["Random"], rampa.inputs["Fac"])
    nt.links.new(rampa.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    for k_ in ("Specular IOR Level", "Specular"):
        if k_ in b.inputs:
            b.inputs[k_].default_value = 0.15
            break
    me.materials.clear()
    me.materials.append(m)
    mod = ob.modifiers.new("relva", "PARTICLE_SYSTEM")
    ps = mod.particle_system.settings
    ps.type = "HAIR"
    area = sum(p.area for p in me.polygons)
    ps.count = int(min(1400000, area * densidade))
    ps.hair_length = 0.15
    ps.use_advanced_hair = True
    ps.emit_from = "FACE"
    ps.distribution = "RAND"
    ps.use_even_distribution = True
    try:      # grow straight up, not along each triangle's normal (that showed the mesh as patches)
        ps.normal_factor = 0.0
        ps.object_align_factor = (0.0, 0.0, 0.15 / 4.0)      # hair length = 4 x velocity
    except Exception as e:
        print('relva vertical:', e)
    for attr, val in (("factor_random", 0.012), ("brownian_factor", 0.0), ("root_radius", 0.0025), ("tip_radius", 0.0),
                      ("radius_scale", 1.0), ("display_percentage", 5), ("render_step", 3), ("display_step", 2)):
        if hasattr(ps, attr):
            setattr(ps, attr, val)
    if False:     # children sat in a plane around each strand and half of them ended under the ground (patches)
        ps.child_type = "SIMPLE"
        ps.rendered_child_count = 2
        for attr in ("child_nbr", "child_percent", "child_display_percent"):
            if hasattr(ps, attr):
                setattr(ps, attr, 1)
        for attr, val in (("child_radius", 0.04), ("roughness_2", 0.06), ("roughness_endpoint", 0.05),
                          ("child_length", 1.0), ("child_length_threshold", 0.5)):
            if hasattr(ps, attr):
                setattr(ps, attr, val)
    ps.material = 1
    return ob


# ---------------------------------------------------------------------------------------------- light, sky, cameras
CEU = {}


def luz_e_ceu():
    sol = E.get("sol", {"azimute": 235, "elevacao": 32})
    w = bpy.data.worlds.new("mundo")
    cena.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    nt = w.node_tree
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    ceu = no(nt, "ShaderNodeTexSky", -300, 300)
    for t in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA", "HOSEK_WILKIE"):
        try:
            ceu.sky_type = t
            break
        except Exception:
            continue
    el, az = math.radians(sol["elevacao"]), math.radians(sol["azimute"])
    for attr, val in (("sun_elevation", el), ("sun_rotation", az), ("sun_disc", False),
                      ("altitude", 100.0), ("air_density", 1.0), ("aerosol_density", float(sol.get("aerossol", 0.6))),
                      ("dust_density", float(sol.get("aerossol", 0.6))),
                      ("ozone_density", 1.0)):
        if hasattr(ceu, attr):
            try:
                setattr(ceu, attr, val)
            except Exception:
                pass
    nt.links.new(ceu.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = float(sol.get("ceu", 0.35))
    CEU["no"], CEU["forca"] = ceu, float(sol.get("ceu", 0.35))
    luz = bpy.data.lights.new("sol", "SUN")
    luz.energy = float(sol.get("forca", 3.2))
    luz.angle = math.radians(0.6)
    luz.color = (1.0, 0.95, 0.88)
    ob = bpy.data.objects.new("sol", luz)
    cena.collection.objects.link(ob)
    # direction: the light points down toward -dir(sun); world frame is north-up after the root rotation
    dx, dy = math.sin(az), math.cos(az)
    ob.rotation_euler = (0.0, 0.0, 0.0)
    v = (-(dx * math.cos(el)), -(dy * math.cos(el)), -math.sin(el))
    from mathutils import Vector
    ob.rotation_euler = Vector(v).to_track_quat("-Z", "Y").to_euler()


def camaras():
    from mathutils import Vector
    out = {}
    for v in E.get("vistas", []):
        cam = bpy.data.cameras.new(v["nome"])
        cam.lens = v.get("lente", 26)
        cam.sensor_width = 36
        cam.clip_start = 0.1
        cam.clip_end = 100000 if E.get("envolvente") else 2000
        if v.get("panorama"):
            cam.type = "PANO"
            for alvo_ in (cam, getattr(cam, "cycles", None)):
                try:
                    alvo_.panorama_type = "EQUIRECTANGULAR"
                    break
                except Exception:
                    continue
        ob = bpy.data.objects.new("cam_" + v["nome"], cam)
        cena.collection.objects.link(ob)
        ob.parent = RAIZ
        ob.location = v["camara"]
        d = Vector(v["alvo"]) - Vector(v["camara"])
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        if "shift_y" in v:
            cam.shift_y = v["shift_y"]
        out[v["nome"]] = ob
    return out



# ---------------------------------------------------------------------------------------------- web: baked light, sky, leaf cards
CARTAS = []


def cartas_folhas():
    """Crowns for the web: cards carrying a cluster of leaves (alpha). They also cast dappled shadows in the bake."""
    if not ARVORES:
        return None
    n = 512
    rng = np.random.default_rng(77)
    rgba = np.zeros((n, n, 4))
    yy, xx = np.mgrid[0:n, 0:n] / n
    for _ in range(420):
        cx, cy = rng.random(2) * 0.84 + 0.08
        if (cx - 0.5) ** 2 + (cy - 0.5) ** 2 > 0.19:
            continue
        a, b = rng.uniform(0.018, 0.032), rng.uniform(0.008, 0.014)
        ang = rng.random() * math.pi
        dx, dy = xx - cx, yy - cy
        u = (dx * math.cos(ang) + dy * math.sin(ang)) / a
        v = (-dx * math.sin(ang) + dy * math.cos(ang)) / b
        m = u * u + v * v <= 1.0
        tom = rng.uniform(0.55, 1.15)
        cor = np.array([0.16, 0.26, 0.07]) * tom + rng.normal(0, 0.012, 3)
        sombra = 0.8 + 0.2 * (1 - np.clip(np.abs(v), 0, 1))
        for c_ in range(3):
            rgba[..., c_] = np.where(m, np.clip(cor[c_] * sombra, 0, 1), rgba[..., c_])
        rgba[..., 3] = np.where(m, 1.0, rgba[..., 3])
    img = bpy.data.images.new("folha_cartas", n, n, alpha=True)
    img.pixels.foreach_set(rgba[::-1].astype(np.float32).ravel())
    img.filepath_raw = os.path.join(SAIDA, "folha.png")
    img.file_format = "PNG"
    img.save()
    m = bpy.data.materials.new("folhas_cartas")
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = principled(m)
    it = no(nt, "ShaderNodeTexImage", -500, 200)
    it.image = img
    nt.links.new(it.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(it.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.6
    MATS["folhas_cartas"] = m
    for k, (copa, x, y, zc, c) in enumerate(ARVORES):
        rng = np.random.default_rng(500 + k)
        bm = bmesh.new()
        uvl = bm.loops.layers.uv.new("UVMap")
        for _ in range(int(64 * (c / 2.2) ** 2)):
            d = rng.normal(size=3)
            d /= np.linalg.norm(d)
            p = np.array([x, y, zc]) + d * c * rng.uniform(0.25, 0.85) * np.array([1, 1, 0.85])
            nrm = rng.normal(size=3)
            nrm /= np.linalg.norm(nrm)
            t1 = np.cross(nrm, [0, 0, 1] if abs(nrm[2]) < 0.9 else [1, 0, 0])
            t1 /= np.linalg.norm(t1)
            t2 = np.cross(nrm, t1)
            s = c * rng.uniform(0.55, 0.85)
            vs = [bm.verts.new(tuple(p + (t1 * a_ + t2 * b_) * s)) for a_, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            f = bm.faces.new(vs)
            for lp, uv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
                lp[uvl].uv = uv
        me = bpy.data.meshes.new(f"copa_cartas{k}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(m)
        ob = ligar(bpy.data.objects.new(f"copa_cartas{k}", me), "envolvente")
        CARTAS.append(ob)
        copa.hide_render = True          # the low-poly crown stays out of the bake and the web model
        copa.hide_set(True)
        copa.hide_viewport = True
    return img


def configurar_cycles():
    cena.render.engine = "CYCLES"
    pref = bpy.context.preferences.addons["cycles"].preferences
    try:
        pref.compute_device_type = "CUDA"
        pref.refresh_devices()
        for d in pref.devices:
            d.use = d.type == "CUDA"
        cena.cycles.device = "GPU"
    except Exception as e:
        print("GPU indisponível:", e)


def _srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def _desfocar(a, vezes=2):
    for _ in range(vezes):
        a = (a + np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)) / 5
    return a


def _limpar(px):
    """Bake noise: a light blur everywhere, a strong one where it is dark (rooms seen through the glass)."""
    leve = _desfocar(px, 2)
    forte = _desfocar(px, 8)
    lum = leve.mean(-1)
    ref = float(np.percentile(lum, 95)) or 1.0
    w = np.clip((0.25 * ref - lum) / (0.25 * ref), 0, 1)[..., None]
    return leve * (1 - w) + forte * w


def uv_luz(obs, plano=None):
    """Second UV map 'lm' for the bake: a plan projection (the ground) or islands packed into one square (the rest)."""
    for ob in obs:
        me = ob.data
        lm = me.uv_layers.get("lm") or me.uv_layers.new(name="lm")
        if plano:
            x0, y0, x1, y1 = plano
            for lp in me.loops:
                co = me.vertices[lp.vertex_index].co
                lm.data[lp.index].uv = (min(1, max(0, (co.x - x0) / (x1 - x0))), min(1, max(0, (co.y - y0) / (y1 - y0))))
        me.uv_layers.active = lm
    if plano:
        return
    bpy.ops.object.select_all(action="DESELECT")
    for ob in obs:
        ob.hide_set(False)
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004, area_weight=1.0, correct_aspect=True,
                             scale_to_bounds=False)
    bpy.ops.uv.pack_islands(margin=0.004, rotate=True)
    bpy.ops.object.mode_set(mode="OBJECT")


def gravar_luz(amostras=128):
    """Bake the light of the scene (direct + bounced, diffuse, no colour) into lightmaps, for the web model:
    'casa' (every storey, frames, copings, deck), 'exterior' (walls, ramp, road), 'terreno' (the ground near the house).
    Saved as sRGB JPEG divided by K (luz.json says K per map); the page multiplies the texture colour by it."""
    vidro = lambda ob: any(m and m.name.startswith("vidro") for m in ob.data.materials)
    meshes = [o for o in cena.objects if o.type == "MESH" and not o.hide_get() and o.data.polygons]
    grupos = {
        "casa": [o for o in meshes if o.get("grupo") in ("cave", "piso0", "piso1", "cobertura") and not vidro(o)],
        "exterior": [o for o in meshes if o.name.startswith(("muro", "piso_livre", "faixa"))],
        "terreno": [o for o in meshes if o.name == "terreno"],
    }
    tamanho = {"casa": 2048, "exterior": 1024, "terreno": 2048}
    # triangulate the baked meshes (simpler islands; the web model is triangles anyway)
    for nome in ("casa", "exterior"):
        for ob in grupos[nome]:
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            bm.to_mesh(ob.data)
            bm.free()
    uv_luz(grupos["casa"])
    uv_luz(grupos["exterior"])
    uv_luz(grupos["terreno"], plano=E.get("luz_plano", (-45, -15, 45, 55)))
    configurar_cycles()
    cena.cycles.samples = amostras
    cena.cycles.use_denoising = False
    cena.cycles.sample_clamp_indirect = 1.0     # light through the glass made bright specks inside
    cena.cycles.max_bounces = 6
    info = {}
    for nome, obs in grupos.items():
        if not obs:
            continue
        n = tamanho[nome]
        img = bpy.data.images.new("lm_" + nome, n, n, alpha=False, float_buffer=True)
        mats = {m for ob in obs for m in ob.data.materials if m}
        for m in mats:
            nt = m.node_tree
            nd = nt.nodes.get("LM") or nt.nodes.new("ShaderNodeTexImage")
            nd.name = "LM"
            nd.image = img
            nt.nodes.active = nd
        bpy.ops.object.select_all(action="DESELECT")
        for ob in obs:
            ob.select_set(True)
            ob.data.uv_layers.active = ob.data.uv_layers["lm"]
            ob["lm"] = nome
        bpy.context.view_layer.objects.active = obs[0]
        t0 = __import__("time").time()
        bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT"}, uv_layer="lm", margin=8,
                            use_clear=True, target="IMAGE_TEXTURES")
        px = np.array(img.pixels[:], dtype=np.float32).reshape(n, n, 4)[..., :3]
        px = _limpar(px)
        K = float(np.percentile(px, 99.7)) or 1.0
        enc = _srgb(px / K)
        out = bpy.data.images.new("lm_" + nome + "_8", n, n, alpha=False)
        rgba = np.ones((n, n, 4), dtype=np.float32)
        rgba[..., :3] = enc
        out.pixels.foreach_set(rgba.ravel())
        out.filepath_raw = os.path.join(SAIDA, f"lm_{nome}.jpg")
        out.file_format = "JPEG"
        cena.render.image_settings.quality = 88
        out.save()
        info[nome] = {"K": round(K, 4), "tam": n}
        print("LUZ", nome, n, "K", round(K, 3), round(__import__("time").time() - t0), "s")
        for ob in obs:
            ob.data.uv_layers.active = ob.data.uv_layers[0]
    for ob in meshes:          # texture UVs first again (TEXCOORD_0), 'lm' second (TEXCOORD_1)
        if ob.data.uv_layers:
            ob.data.uv_layers[0].active = True
            ob.data.uv_layers[0].active_render = True
    json.dump(info, open(os.path.join(SAIDA, "luz.json"), "w"))


def ceu_panorama():
    """The sky of the images as an equirectangular picture (centre = east, as three.js expects) for the web page."""
    from mathutils import Euler
    ocultos = []
    for ob in cena.objects:
        if ob.type in ("MESH", "CURVES") and not ob.hide_render:
            ob.hide_render = True
            ocultos.append(ob)
    cam = bpy.data.cameras.new("pano")
    cam.type = "PANO"
    for alvo in (cam, getattr(cam, "cycles", None)):
        if alvo is not None and hasattr(alvo, "panorama_type"):
            try:
                alvo.panorama_type = "EQUIRECTANGULAR"
            except Exception:
                pass
    ob = bpy.data.objects.new("cam_pano", cam)
    cena.collection.objects.link(ob)
    ob.location = (0, 0, 2)
    ob.rotation_euler = Euler((math.pi / 2, 0, -math.pi / 2))     # looking east
    configurar_cycles()
    cena.camera = ob
    cena.cycles.samples = 16
    cena.render.resolution_x, cena.render.resolution_y, cena.render.resolution_percentage = 2048, 1024, 100
    vt, lk, ex = cena.view_settings.view_transform, cena.view_settings.look, cena.view_settings.exposure
    try:      # the same colour transform as the images: the page shows this sky as it is (no tone mapping)
        cena.view_settings.view_transform = "AgX"
        cena.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    cena.view_settings.exposure = float(E.get("sol", {}).get("exposicao", 0.0))
    cena.render.image_settings.file_format = "JPEG"
    cena.render.image_settings.quality = 85
    cena.render.filepath = os.path.join(SAIDA, "ceu.jpg")
    bpy.ops.render.render(write_still=True)
    cena.view_settings.view_transform, cena.view_settings.look, cena.view_settings.exposure = vt, lk, ex
    for o in ocultos:
        o.hide_render = False
    bpy.data.objects.remove(ob)
    print("CEU ok")

# ---------------------------------------------------------------------------------------------- the surroundings (renders)
NEB = {"maximo": 0.85}


def neblina(m, distancia, maximo=None):
    """Aerial perspective: far surfaces fade into the sky's own colour seen in the same direction (the sky texture
    evaluated along the view ray, kept just above the horizon), maximo (1 - exp(-d / distancia)): the far hills
    stay visible, the sea horizon stays a line."""
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    if not out.inputs["Surface"].links or not CEU:
        return
    origem = out.inputs["Surface"].links[0].from_socket
    cd = no(nt, "ShaderNodeCameraData", 300, -400)
    k = no(nt, "ShaderNodeMath", 500, -400)
    k.operation = "MULTIPLY"
    k.inputs[1].default_value = -1.0 / distancia
    nt.links.new(cd.outputs["View Distance"], k.inputs[0])
    ex = no(nt, "ShaderNodeMath", 650, -400)
    ex.operation = "EXPONENT"
    nt.links.new(k.outputs["Value"], ex.inputs[0])
    f = no(nt, "ShaderNodeMath", 800, -400)
    f.operation = "SUBTRACT"
    f.inputs[0].default_value = 1.0
    nt.links.new(ex.outputs["Value"], f.inputs[1])
    fm = no(nt, "ShaderNodeMath", 950, -400)
    fm.operation = "MULTIPLY"
    fm.inputs[1].default_value = NEB["maximo"] if maximo is None else maximo
    nt.links.new(f.outputs["Value"], fm.inputs[0])
    g = no(nt, "ShaderNodeNewGeometry", 300, -650)
    inv = no(nt, "ShaderNodeVectorMath", 500, -650)
    inv.operation = "SCALE"
    inv.inputs["Scale"].default_value = -1.0
    nt.links.new(g.outputs["Incoming"], inv.inputs[0])
    sp = no(nt, "ShaderNodeSeparateXYZ", 650, -650)
    nt.links.new(inv.outputs["Vector"], sp.inputs[0])
    mz = no(nt, "ShaderNodeMath", 800, -700)
    mz.operation = "MAXIMUM"
    mz.inputs[1].default_value = 0.03
    nt.links.new(sp.outputs["Z"], mz.inputs[0])
    cb = no(nt, "ShaderNodeCombineXYZ", 950, -650)
    nt.links.new(sp.outputs["X"], cb.inputs["X"])
    nt.links.new(sp.outputs["Y"], cb.inputs["Y"])
    nt.links.new(mz.outputs["Value"], cb.inputs["Z"])
    nr = no(nt, "ShaderNodeVectorMath", 1100, -650)
    nr.operation = "NORMALIZE"
    nt.links.new(cb.outputs["Vector"], nr.inputs[0])
    ceu_w = CEU["no"]
    sk = no(nt, "ShaderNodeTexSky", 1250, -650)
    for attr in ("sky_type", "sun_elevation", "sun_rotation", "sun_disc", "altitude", "air_density",
                 "aerosol_density", "dust_density", "ozone_density"):
        if hasattr(ceu_w, attr):
            try:
                setattr(sk, attr, getattr(ceu_w, attr))
            except Exception:
                pass
    nt.links.new(nr.outputs["Vector"], sk.inputs["Vector"])
    em = no(nt, "ShaderNodeEmission", 1450, -650)
    em.inputs["Strength"].default_value = CEU["forca"]
    nt.links.new(sk.outputs["Color"], em.inputs["Color"])
    mx = no(nt, "ShaderNodeMixShader", 1650, -300)
    nt.links.new(fm.outputs["Value"], mx.inputs["Fac"])
    nt.links.new(origem, mx.inputs[1])
    nt.links.new(em.outputs["Emission"], mx.inputs[2])
    nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])


def _ramp(nt, entrada, cores, x, y, constante=True):
    r = no(nt, "ShaderNodeValToRGB", x, y)
    cr = r.color_ramp
    if constante:
        cr.interpolation = "CONSTANT"
    n = len(cores)
    while len(cr.elements) < n:
        cr.elements.new(0.5)
    for k, h in enumerate(cores):
        cr.elements[k].position = k / n if constante else k / max(1, n - 1)
        cr.elements[k].color = (*[c ** 2.2 for c in hex_rgb(h)], 1)
    nt.links.new(entrada, r.inputs["Fac"])
    return r


def mat_parede_env(dist):
    """Rendered walls (white, cream, pale yellow, light grey by 'tom') with windows from the wall UVs (u along the
    wall, v up from the ground): 1.2 m windows every 3.3 m, one row per 2.9 m storey, up to 'hjan'."""
    m = bpy.data.materials.new("parede_env")
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = principled(m)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tom = no(nt, "ShaderNodeAttribute", -1500, 400)
    tom.attribute_name = "tom"
    rp = _ramp(nt, tom.outputs["Fac"], ["#e4e0d6", "#ded3bb", "#e2d8b6", "#d4d0c8", "#e9e7e1", "#d9c9a8"], -1250, 400)
    b.inputs["Roughness"].default_value = 0.9
    tc = no(nt, "ShaderNodeTexCoord", -1700, 0)
    sp = no(nt, "ShaderNodeSeparateXYZ", -1500, 0)
    nt.links.new(tc.outputs["UV"], sp.inputs[0])
    sujo = no(nt, "ShaderNodeTexNoise", -1250, 650)
    sujo.inputs["Scale"].default_value = 0.6
    sujo.inputs["Detail"].default_value = 5.0
    nt.links.new(tc.outputs["Object"], sujo.inputs["Vector"])
    mr = no(nt, "ShaderNodeMapRange", -1050, 650)
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.86, 1.04
    nt.links.new(sujo.outputs["Fac"], mr.inputs["Value"])
    esc = no(nt, "ShaderNodeVectorMath", -850, 500)
    esc.operation = "SCALE"
    nt.links.new(rp.outputs["Color"], esc.inputs[0])
    nt.links.new(mr.outputs["Result"], esc.inputs["Scale"])
    soco_ = no(nt, "ShaderNodeMath", -1050, 350)
    soco_.operation = "LESS_THAN"
    soco_.inputs[1].default_value = 0.45
    nt.links.new(sp.outputs["Y"], soco_.inputs[0])
    mc = no(nt, "ShaderNodeMix", -650, 450)
    mc.data_type = "RGBA"
    nt.links.new(soco_.outputs["Value"], mc.inputs["Factor"])
    nt.links.new(esc.outputs["Vector"], mc.inputs["A"])
    mc.inputs["B"].default_value = (0.32, 0.30, 0.27, 1)
    nt.links.new(mc.outputs["Result"], b.inputs["Base Color"])
    hj = no(nt, "ShaderNodeAttribute", -1500, -300)
    hj.attribute_name = "hjan"
    a_ja = no(nt, "ShaderNodeAttribute", -1700, -450)
    a_ja.attribute_name = "ja"
    a_jt = no(nt, "ShaderNodeAttribute", -1700, -600)
    a_jt.attribute_name = "jt"
    a_j0 = no(nt, "ShaderNodeAttribute", -1700, -750)
    a_j0.attribute_name = "j0"

    def op(tipo, a, b_=None, x=0, y=0):
        n = no(nt, "ShaderNodeMath", x, y)
        n.operation = tipo
        for k_, val in ((0, a), (1, b_)):
            if val is None:
                continue
            if isinstance(val, (int, float)):
                n.inputs[k_].default_value = val
            else:
                nt.links.new(val, n.inputs[k_])
        return n.outputs["Value"]

    u = op("ADD", sp.outputs["X"], op("MULTIPLY", tom.outputs["Fac"], 7.0, x=-1300, y=150), x=-1150, y=100)
    cu = op("FRACT", op("DIVIDE", u, 3.3, x=-1000, y=100), x=-850, y=100)
    ja, jt = a_ja.outputs["Fac"], a_jt.outputs["Fac"]
    um_ja = op("SUBTRACT", 1.0, ja, x=-1300, y=-450)
    m1 = op("MULTIPLY", op("GREATER_THAN", cu, ja, x=-700, y=150), op("LESS_THAN", cu, um_ja, x=-700, y=50),
            x=-550, y=100)
    fv = op("FRACT", op("DIVIDE", op("SUBTRACT", sp.outputs["Y"], a_j0.outputs["Fac"], x=-1150, y=-100), 2.9,
                        x=-1000, y=-100), x=-850, y=-100)
    m2 = op("LESS_THAN", fv, jt, x=-700, y=-100)
    # the glass inside a 5 cm frame (frame = window mask minus the inner one)
    g1 = op("MULTIPLY", op("GREATER_THAN", cu, op("ADD", ja, 0.015, x=-900, y=250), x=-700, y=250),
            op("LESS_THAN", cu, op("SUBTRACT", um_ja, 0.015, x=-900, y=200), x=-700, y=200), x=-550, y=230)
    g2 = op("MULTIPLY", op("GREATER_THAN", fv, 0.02, x=-700, y=-150),
            op("LESS_THAN", fv, op("SUBTRACT", jt, 0.02, x=-900, y=-180), x=-700, y=-180), x=-550, y=-160)
    m3 = op("GREATER_THAN", sp.outputs["Y"], op("SUBTRACT", a_j0.outputs["Fac"], 0.05, x=-900, y=-220), x=-700, y=-200)
    m4 = op("LESS_THAN", sp.outputs["Y"], hj.outputs["Fac"], x=-700, y=-300)
    # not every bay has a window: a random choice per bay and storey (a regular grid read as an office block)
    baia = op("FLOOR", op("DIVIDE", u, 3.3, x=-1000, y=400), x=-850, y=400)
    andar = op("FLOOR", op("DIVIDE", op("SUBTRACT", sp.outputs["Y"], a_j0.outputs["Fac"], x=-1150, y=500), 2.9,
                           x=-1000, y=500), x=-850, y=500)
    cb = no(nt, "ShaderNodeCombineXYZ", -700, 450)
    nt.links.new(baia, cb.inputs["X"])
    nt.links.new(andar, cb.inputs["Y"])
    nt.links.new(tom.outputs["Fac"], cb.inputs["Z"])
    wn = no(nt, "ShaderNodeTexWhiteNoise", -550, 450)
    wn.noise_dimensions = "3D"
    nt.links.new(cb.outputs["Vector"], wn.inputs["Vector"])
    tem = op("GREATER_THAN", wn.outputs["Value"], 0.38, x=-400, y=450)
    mk = op("MULTIPLY", op("MULTIPLY", op("MULTIPLY", m1, m2, x=-550, y=-50), op("MULTIPLY", m3, m4, x=-550, y=-250),
                           x=-400, y=-100), tem, x=-300, y=0)
    vid = no(nt, "ShaderNodeBsdfPrincipled", -300, -500)
    vid.inputs["Base Color"].default_value = (0.03, 0.035, 0.04, 1)
    vid.inputs["Roughness"].default_value = 0.03
    for k_ in ("Specular IOR Level", "Specular"):
        if k_ in vid.inputs:
            vid.inputs[k_].default_value = 1.0
            break
    caix = no(nt, "ShaderNodeBsdfPrincipled", -300, -800)
    caix.inputs["Base Color"].default_value = (0.55, 0.55, 0.53, 1)
    caix.inputs["Roughness"].default_value = 0.5
    mv = no(nt, "ShaderNodeMixShader", -50, -600)
    nt.links.new(op("MULTIPLY", g1, g2, x=-400, y=-650), mv.inputs["Fac"])
    nt.links.new(caix.outputs["BSDF"], mv.inputs[1])
    nt.links.new(vid.outputs["BSDF"], mv.inputs[2])
    mx = no(nt, "ShaderNodeMixShader", 100, 0)
    nt.links.new(mk, mx.inputs["Fac"])
    nt.links.new(b.outputs["BSDF"], mx.inputs[1])
    nt.links.new(mv.outputs["Shader"], mx.inputs[2])
    nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])
    neblina(m, dist)
    return m


def mat_cobertura_env(dist):
    """Roofs: each building's own colour (attribute cor_cob, from the satellite view), mottled."""
    m = bpy.data.materials.new("cobertura_env")
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = principled(m)
    b.inputs["Roughness"].default_value = 0.75
    at = no(nt, "ShaderNodeAttribute", -900, 300)
    at.attribute_name = "cor_cob"
    tc = no(nt, "ShaderNodeTexCoord", -1100, 0)
    rn = no(nt, "ShaderNodeTexNoise", -900, 0)
    rn.inputs["Scale"].default_value = 1.5
    nt.links.new(tc.outputs["Object"], rn.inputs["Vector"])
    mr = no(nt, "ShaderNodeMapRange", -650, 0)
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.85, 1.12
    nt.links.new(rn.outputs["Fac"], mr.inputs["Value"])
    sc = no(nt, "ShaderNodeVectorMath", -400, 200)
    sc.operation = "SCALE"
    nt.links.new(at.outputs["Color"], sc.inputs[0])
    nt.links.new(mr.outputs["Result"], sc.inputs["Scale"])
    nt.links.new(sc.outputs["Vector"], b.inputs["Base Color"])
    neblina(m, dist)
    return m


def mat_env(nome, cor, rug, dist, ramp_cores=None, ruido=0.0):
    m = bpy.data.materials.new(nome)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = principled(m)
    b.inputs["Roughness"].default_value = rug
    fonte = None
    if ramp_cores:
        tom = no(nt, "ShaderNodeAttribute", -900, 300)
        tom.attribute_name = "tom"
        fonte = _ramp(nt, tom.outputs["Fac"], ramp_cores, -650, 300).outputs["Color"]
    else:
        b.inputs["Base Color"].default_value = (*[c ** 2.2 for c in hex_rgb(cor)], 1)
    if ruido and fonte is not None:
        tc = no(nt, "ShaderNodeTexCoord", -1100, 0)
        rn = no(nt, "ShaderNodeTexNoise", -900, 0)
        rn.inputs["Scale"].default_value = 3.0
        nt.links.new(tc.outputs["Object"], rn.inputs["Vector"])
        mr = no(nt, "ShaderNodeMapRange", -650, 0)
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1 - ruido, 1 + ruido
        nt.links.new(rn.outputs["Fac"], mr.inputs["Value"])
        sc = no(nt, "ShaderNodeVectorMath", -400, 200)
        sc.operation = "SCALE"
        nt.links.new(fonte, sc.inputs[0])
        nt.links.new(mr.outputs["Result"], sc.inputs["Scale"])
        fonte = sc.outputs["Vector"]
    if fonte is not None:
        nt.links.new(fonte, b.inputs["Base Color"])
    neblina(m, dist)
    return m


def _retangulo_minimo(pts):
    """Smallest rectangle around a footprint (rotating the convex hull's edges): area, centre, long axis u, v, half
    sizes a >= b."""
    P = np.array(pts, dtype=float)
    P = P[np.lexsort((P[:, 1], P[:, 0]))]

    def cruz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    inf, sup = [], []
    for p in P:
        while len(inf) >= 2 and cruz(inf[-2], inf[-1], p) <= 0:
            inf.pop()
        inf.append(p)
    for p in P[::-1]:
        while len(sup) >= 2 and cruz(sup[-2], sup[-1], p) <= 0:
            sup.pop()
        sup.append(p)
    H = np.array(inf[:-1] + sup[:-1])
    melhor = None
    for i in range(len(H)):
        e = H[(i + 1) % len(H)] - H[i]
        L = float(np.hypot(*e))
        if L < 1e-6:
            continue
        u = e / L
        v = np.array([-u[1], u[0]])
        pu, pv = H @ u, H @ v
        area = (pu.max() - pu.min()) * (pv.max() - pv.min())
        if melhor is None or area < melhor[0]:
            c = u * (pu.max() + pu.min()) / 2 + v * (pv.max() + pv.min()) / 2
            a, b = (pu.max() - pu.min()) / 2, (pv.max() - pv.min()) / 2
            melhor = (area, c, u, v, a, b) if a >= b else (area, c, v, -u, b, a)
    return melhor


def construir_envolvente():
    EV = E["envolvente"]
    # seen from inside, the balustrade glass must be clear (0.12 made a frosted band across the view)
    if "vidro_guarda" in MATS:
        principled(MATS["vidro_guarda"]).inputs["Roughness"].default_value = 0.02
    D = float(EV.get("neblina", {}).get("distancia", 25000.0))
    NEB["maximo"] = float(EV.get("neblina", {}).get("maximo", 0.85))
    if "solo" in MATS:
        neblina(MATS["solo"], D)
    col = bpy.data.collections.new("envolvente")
    cena.collection.children.link(col)

    def objeto(nome, me):
        ob = bpy.data.objects.new(nome, me)
        col.objects.link(ob)
        ob.parent = RAIZ
        return ob

    # ---- the sea: rings out to the horizon, falling with the earth's curve like the ground
    mar = EV.get("mar")
    if mar:
        R, curv, z0 = float(mar.get("raio", 60000)), float(mar.get("curvatura", 7.43e6)), float(mar["z"])
        raios = [0.0]
        r = 15.0
        while r < R:
            raios.append(r)
            r *= 1.05
        raios.append(R)
        na = 360
        V = [(0.0, 0.0, z0)]
        for r in raios[1:]:
            for k in range(na):
                a = 2 * math.pi * k / na
                V.append((r * math.cos(a), r * math.sin(a), z0 - r * r / (2 * curv)))
        F = [(0, 1 + k, 1 + (k + 1) % na) for k in range(na)]
        for i in range(len(raios) - 2):
            b0, b1 = 1 + i * na, 1 + (i + 1) * na
            F += [(b0 + k, b0 + (k + 1) % na, b1 + (k + 1) % na, b1 + k) for k in range(na)]
        me = bpy.data.meshes.new("mar")
        me.from_pydata(V, [], F)
        for p in me.polygons:
            p.use_smooth = True
        m = bpy.data.materials.new("mar")
        try:
            m.use_nodes = True
        except Exception:
            pass
        nt = m.node_tree
        for n_ in list(nt.nodes):
            if n_.type == "BSDF_PRINCIPLED":
                nt.nodes.remove(n_)
        out = next(n_ for n_ in nt.nodes if n_.type == "OUTPUT_MATERIAL")
        # deep blue water under a reflection held to at most ~45 % even at grazing angles (a physical flat sea mirrors
        # the pale sky near the horizon and read as sky in the views from the house)
        tc = no(nt, "ShaderNodeTexCoord", -1300, -200)
        w1 = no(nt, "ShaderNodeTexNoise", -1050, -100)
        w1.inputs["Scale"].default_value = 0.08
        w1.inputs["Detail"].default_value = 6.0
        nt.links.new(tc.outputs["Object"], w1.inputs["Vector"])
        w2 = no(nt, "ShaderNodeTexNoise", -1050, -350)
        w2.inputs["Scale"].default_value = 0.9
        w2.inputs["Detail"].default_value = 8.0
        nt.links.new(tc.outputs["Object"], w2.inputs["Vector"])
        sm = no(nt, "ShaderNodeMath", -800, -200)
        sm.operation = "ADD"
        nt.links.new(w1.outputs["Fac"], sm.inputs[0])
        nt.links.new(w2.outputs["Fac"], sm.inputs[1])
        bp = no(nt, "ShaderNodeBump", -600, -200)
        bp.inputs["Strength"].default_value = 0.3
        bp.inputs["Distance"].default_value = 0.6
        nt.links.new(sm.outputs["Value"], bp.inputs["Height"])
        agua = no(nt, "ShaderNodeBsdfDiffuse", -300, 200)
        agua.inputs["Color"].default_value = (0.004, 0.022, 0.055, 1)
        brilho = no(nt, "ShaderNodeBsdfGlossy", -300, -50)
        brilho.inputs["Roughness"].default_value = 0.03
        # the waves face the viewer and mirror the higher, bluer sky, not the white horizon: tint the reflection
        brilho.inputs["Color"].default_value = (0.30, 0.50, 0.82, 1)
        nt.links.new(bp.outputs["Normal"], brilho.inputs["Normal"])
        lw = no(nt, "ShaderNodeLayerWeight", -600, 250)
        lw.inputs["Blend"].default_value = 0.25
        nt.links.new(bp.outputs["Normal"], lw.inputs["Normal"])
        k = no(nt, "ShaderNodeMath", -350, 400)
        k.operation = "MULTIPLY"
        k.inputs[1].default_value = 0.55
        nt.links.new(lw.outputs["Fresnel"], k.inputs[0])
        mx = no(nt, "ShaderNodeMixShader", 0, 150)
        nt.links.new(k.outputs["Value"], mx.inputs["Fac"])
        nt.links.new(agua.outputs["BSDF"], mx.inputs[1])
        nt.links.new(brilho.outputs["BSDF"], mx.inputs[2])
        nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])
        neblina(m, D)
        me.materials.append(m)
        objeto("mar", me)

    # ---- buildings: walls along the footprint, hipped tile roof over its rectangle (or flat), windows in the walls
    casas = EV.get("casas", [])
    if casas:
        V, F, FM, TOM, HJ, UV, COB, JA, JT, J0 = [], [], [], [], [], [], [], [], [], []
        for q in casas:
            cob = [c ** 2.2 for c in hex_rgb(q.get("cor_cob", "#b4603e"))] + [1.0]
            moderna = bool(q.get("moderna"))
            janela = (0.22, 0.76, 0.15) if moderna else (0.33, 0.47, 0.95)
            plano = q.get("telhado") != "aguas"
            n0 = len(F)
            pts = [tuple(p) for p in q["pontos"]]
            if sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts))) < 0:
                pts = pts[::-1]
            z0, zc, h = q["z0"], q["zc"], q["altura"]
            zt = zc + h
            tom = q.get("tom", 0.5)
            mw = 3 if q.get("estufa") else 0
            u = 0.0
            for i in range(len(pts)):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
                L = math.hypot(x2 - x1, y2 - y1)
                b0 = len(V)
                ztopo = zt + (0.45 if moderna else 0.3) if plano else zt + 0.1     # parapet round a flat roof
                V += [(x1, y1, z0), (x2, y2, z0), (x2, y2, ztopo), (x1, y1, ztopo)]
                F.append((b0, b0 + 1, b0 + 2, b0 + 3))
                FM.append(mw)
                TOM.append(tom)
                HJ.append(h - 0.5)
                UV.append([(u, z0 - zc), (u + L, z0 - zc), (u + L, ztopo - zc), (u, ztopo - zc)])
                u += L
            rect = _retangulo_minimo(pts)
            area = abs(sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))) / 2
            if q.get("telhado") == "aguas" and rect and area / max(rect[0], 1e-6) > 0.72 and not q.get("estufa"):
                _, c, ua, va, a, bb = rect
                a, bb = a + 0.35, bb + 0.35
                ze = zt - 0.10
                sobe = bb * math.tan(math.radians(24))
                P1 = (*(c - ua * a - va * bb), ze)
                P2 = (*(c + ua * a - va * bb), ze)
                P3 = (*(c + ua * a + va * bb), ze)
                P4 = (*(c - ua * a + va * bb), ze)
                R1 = (*(c - ua * (a - bb)), ze + sobe)
                R2 = (*(c + ua * (a - bb)), ze + sobe)
                b0 = len(V)
                V += [tuple(float(t) for t in p) for p in (P1, P2, P3, P4, R1, R2)]
                for fc in ((0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4)):
                    F.append(tuple(b0 + k for k in fc))
                    FM.append(1)
                    TOM.append(tom)
                    HJ.append(0.0)
                    UV.append([(0.0, 0.0)] * len(fc))
            else:
                b0 = len(V)
                V += [(x, y, zt) for x, y in pts]
                F.append(tuple(range(b0, b0 + len(pts))))
                FM.append(3 if q.get("estufa") else 2)
                TOM.append(tom)
                HJ.append(0.0)
                UV.append([(0.0, 0.0)] * len(pts))
            for _ in range(len(F) - n0):
                COB += cob
                JA.append(janela[0])
                JT.append(janela[1])
                J0.append(janela[2])
        me = bpy.data.meshes.new("casas_env")
        me.from_pydata(V, [], F)
        me.polygons.foreach_set("material_index", FM)
        at = me.attributes.new("tom", "FLOAT", "FACE")
        at.data.foreach_set("value", TOM)
        at = me.attributes.new("hjan", "FLOAT", "FACE")
        at.data.foreach_set("value", HJ)
        at = me.attributes.new("cor_cob", "FLOAT_COLOR", "FACE")
        at.data.foreach_set("color", COB)
        for nome_, vals in (("ja", JA), ("jt", JT), ("j0", J0)):
            at = me.attributes.new(nome_, "FLOAT", "FACE")
            at.data.foreach_set("value", vals)
        uvl = me.uv_layers.new(name="UVMap")
        for p, uvs in zip(me.polygons, UV):
            for li, (uu, vv) in zip(p.loop_indices, uvs):
                uvl.data[li].uv = (uu, vv)
        cobertura = mat_cobertura_env(D)
        for mt in (mat_parede_env(D), cobertura, cobertura, mat_env("estufa_env", "#d9dcd8", 0.4, D)):
            me.materials.append(mt)
        objeto("casas_env", me)

    # ---- roads: ribbons on the ground
    estr = EV.get("estradas", [])
    if estr:
        V, F, FM = [], [], []
        for k, e in enumerate(estr):
            P = e["pontos"]
            w = e["largura"] / 2
            b0 = len(V)
            for i, (x, y, z) in enumerate(P):
                xa, ya = P[max(0, i - 1)][:2]
                xb, yb = P[min(len(P) - 1, i + 1)][:2]
                dx, dy = xb - xa, yb - ya
                L = math.hypot(dx, dy) or 1.0
                nx_, ny_ = -dy / L * w, dx / L * w
                zz = z + 0.003 * (k % 7)
                V += [(x + nx_, y + ny_, zz), (x - nx_, y - ny_, zz)]
            for i in range(len(P) - 1):
                a = b0 + 2 * i
                F.append((a, a + 2, a + 3, a + 1))
                FM.append(0 if e["mat"] == "asfalto" else 1)
        me = bpy.data.meshes.new("estradas_env")
        me.from_pydata(V, [], F)
        me.polygons.foreach_set("material_index", FM)
        me.materials.append(mat_env("asfalto_env", "#4d4d50", 0.85, D))
        me.materials.append(mat_env("terra_env", "#8b7a5f", 0.95, D))
        objeto("estradas_env", me)

    # ---- trees: nine models (pine x2, eucalyptus x2, broadleaf x2, bush x2, fruit tree), placed as instances
    arv = EV.get("arvores", [])
    if arv:
        modelos = bpy.data.collections.new("modelos_arvores")
        casca = mat_env("casca_env", "#4a3f35", 0.9, D)
        FOL = {"pinheiro": ["#26331a", "#2d3b1c", "#33421f"], "eucalipto": ["#4f5d3c", "#5a6845", "#46553a"],
               "folhosa": ["#3d4f22", "#4a5c27", "#56662d"], "arbusto": ["#3f4a24", "#4a5228", "#56592e"],
               "fruteira": ["#4f6227", "#5b6d2c"]}
        mats_f = {}
        for t_, cs in FOL.items():
            m = bpy.data.materials.new("folhagem_" + t_)
            try:
                m.use_nodes = True
            except Exception:
                pass
            nt = m.node_tree
            b = principled(m)
            oi = no(nt, "ShaderNodeObjectInfo", -900, 300)
            rp = _ramp(nt, oi.outputs["Random"], cs, -650, 300, constante=False)
            nt.links.new(rp.outputs["Color"], b.inputs["Base Color"])
            b.inputs["Roughness"].default_value = 0.65
            tc = no(nt, "ShaderNodeTexCoord", -900, -200)
            rn = no(nt, "ShaderNodeTexNoise", -650, -200)
            rn.inputs["Scale"].default_value = 9.0
            rn.inputs["Detail"].default_value = 4.0
            nt.links.new(tc.outputs["Object"], rn.inputs["Vector"])
            bp = no(nt, "ShaderNodeBump", -400, -200)
            bp.inputs["Strength"].default_value = 0.6
            nt.links.new(rn.outputs["Fac"], bp.inputs["Height"])
            nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
            out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
            tr = no(nt, "ShaderNodeBsdfTranslucent", -200, -400)
            nt.links.new(rp.outputs["Color"], tr.inputs["Color"])
            mx = no(nt, "ShaderNodeMixShader", 150, 100)
            mx.inputs["Fac"].default_value = 0.22
            nt.links.new(b.outputs["BSDF"], mx.inputs[1])
            nt.links.new(tr.outputs["BSDF"], mx.inputs[2])
            nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])
            neblina(m, D)
            mats_f[t_] = m

        def modelo(k, tipo, semente):
            """A tree 1 m tall (instances scale it to their height): trunk + irregular crown of blobs."""
            rng = np.random.default_rng(semente)
            bm = bmesh.new()
            t0, hc, raio, nb, achatar = {"pinheiro": (0.58, 0.40, 0.42, 6, 0.55), "eucalipto": (0.38, 0.62, 0.17, 7, 0.45),
                                         "folhosa": (0.32, 0.68, 0.36, 6, 0.0), "arbusto": (0.0, 1.0, 0.62, 3, 0.0),
                                         "fruteira": (0.34, 0.66, 0.46, 5, 0.0)}[tipo]
            if t0 > 0:
                res = bmesh.ops.create_cone(bm, cap_ends=True, segments=7,
                                            radius1=0.018 if tipo != "eucalipto" else 0.012, radius2=0.006,
                                            depth=t0 + hc * 0.5)
                bmesh.ops.translate(bm, verts=res["verts"], vec=(0, 0, (t0 + hc * 0.5) / 2))
            n_tronco = len(bm.faces)
            for j in range(nb):
                if j == 0:
                    c = (0.0, 0.0, t0 + hc * 0.55)
                    r = raio * 0.8
                else:
                    a = rng.random() * 2 * math.pi
                    c = (math.cos(a) * raio * rng.uniform(0.3, 0.65), math.sin(a) * raio * rng.uniform(0.3, 0.65),
                         t0 + hc * rng.uniform(0.25, 0.85))
                    r = raio * rng.uniform(0.45, 0.7)
                res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
                for v_ in res["verts"]:
                    jit = 1 + rng.uniform(-0.18, 0.18)
                    v_.co.x = v_.co.x * r * jit + c[0]
                    v_.co.y = v_.co.y * r * jit + c[1]
                    v_.co.z = v_.co.z * min(r, hc / 2) * jit * (1 - achatar * 0.5) + c[2]
            bm.faces.ensure_lookup_table()
            for i_, f_ in enumerate(bm.faces):
                f_.material_index = 0 if i_ < n_tronco else 1
                f_.smooth = i_ >= n_tronco
            me = bpy.data.meshes.new(f"arv_{k}")
            bm.to_mesh(me)
            bm.free()
            me.materials.append(casca)
            me.materials.append(mats_f[tipo])
            ob = bpy.data.objects.new(f"arv_{k}", me)
            modelos.objects.link(ob)
            return ob

        for k, (tipo, sem) in enumerate((("pinheiro", 1), ("pinheiro", 2), ("eucalipto", 3), ("eucalipto", 4),
                                         ("folhosa", 5), ("folhosa", 6), ("arbusto", 7), ("arbusto", 8),
                                         ("fruteira", 9))):
            modelo(k, tipo, sem)
        A = np.array(arv, dtype=float)
        me = bpy.data.meshes.new("arvores_env")
        me.from_pydata(A[:, :3].tolist(), [], [])
        for nome_, tipo_, col_ in (("variante", "INT", 3), ("escala", "FLOAT", 4), ("rot", "FLOAT", 5)):
            at = me.attributes.new(nome_, tipo_, "POINT")
            at.data.foreach_set("value", A[:, col_].astype(np.int32 if tipo_ == "INT" else np.float32))
        ob = objeto("arvores_env", me)
        ng = bpy.data.node_groups.new("arvores_instancias", "GeometryNodeTree")
        ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        gi = ng.nodes.new("NodeGroupInput")
        go = ng.nodes.new("NodeGroupOutput")
        ip = ng.nodes.new("GeometryNodeInstanceOnPoints")
        ci = ng.nodes.new("GeometryNodeCollectionInfo")
        ci.inputs["Collection"].default_value = modelos
        ci.inputs["Separate Children"].default_value = True
        ci.inputs["Reset Children"].default_value = True
        ip.inputs["Pick Instance"].default_value = True

        def atributo(nome_, tipo_):
            n = ng.nodes.new("GeometryNodeInputNamedAttribute")
            n.data_type = tipo_
            n.inputs["Name"].default_value = nome_
            return n.outputs["Attribute"]
        ng.links.new(gi.outputs[0], ip.inputs["Points"])
        ng.links.new(ci.outputs[0], ip.inputs["Instance"])
        ng.links.new(atributo("variante", "INT"), ip.inputs["Instance Index"])
        cx = ng.nodes.new("ShaderNodeCombineXYZ")
        ng.links.new(atributo("rot", "FLOAT"), cx.inputs["Z"])
        try:
            er = ng.nodes.new("FunctionNodeEulerToRotation")
            ng.links.new(cx.outputs[0], er.inputs[0])
            ng.links.new(er.outputs[0], ip.inputs["Rotation"])
        except Exception:
            ng.links.new(cx.outputs[0], ip.inputs["Rotation"])
        ng.links.new(atributo("escala", "FLOAT"), ip.inputs["Scale"])
        ng.links.new(ip.outputs["Instances"], go.inputs[0])
        mod = ob.modifiers.new("arvores", "NODES")
        mod.node_group = ng
        print("envolvente: árvores", len(arv))
    print("envolvente ok:", len(casas), "casas,", len(estr), "estradas")


# ---------------------------------------------------------------------------------------------- main
criar_materiais()
construir_solidos()
construir_vaos()
construir_extras()
terreno = construir_terreno()
construir_arvores()
RAIZ.rotation_euler = (0, 0, math.radians(E.get("rodar_graus", 0.0)))
bpy.context.view_layer.update()
for ob in cena.objects:
    if ob.type == "MESH":
        uvs_mundo(ob)
        if ob.name != "terreno":
            for p in ob.data.polygons:
                p.use_smooth = False
luz_e_ceu()
cams = camaras()
bpy.context.view_layer.update()
if OPC.get("luz"):
    cartas_folhas()
    bpy.context.view_layer.update()
    gravar_luz(int(OPC.get("amostras_luz", 128)))
    ceu_panorama()

if not OPC.get("sem-glb"):
    # web copy: textures at 512 px, JPEG inside the GLB
    for img in bpy.data.images:
        if img.size[0] > 512 and not img.name.startswith(("lm_", "folha")):
            img.scale(512, 512)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.export_scene.gltf(filepath=os.path.join(SAIDA, "casa.glb"), export_format="GLB", export_extras=True,
                              export_apply=True, export_image_format="JPEG", export_jpeg_quality=82,
                              export_cameras=False, export_lights=False, use_visible=True)
    for img in bpy.data.images:          # back to full size for Cycles
        if img.filepath_raw:
            img.reload()
    print("GLB", os.path.getsize(os.path.join(SAIDA, "casa.glb")))

if OPC["render"]:
    # the ground casts no shadow: grass roots sit on it and half the triangles shaded them (patches); it still receives
    terreno.visible_shadow = False
    if not OPC.get("sem-relva"):
        relva_cycles(terreno, "relva", 1200)
        relva_cycles(terreno, "relva_fora", 320, raio=34)
    folhas_cycles()
    for ob in CARTAS:
        ob.hide_render = True
    if E.get("envolvente"):
        construir_envolvente()
    cena.render.engine = "CYCLES"
    pref = bpy.context.preferences.addons["cycles"].preferences
    try:
        pref.compute_device_type = "CUDA"
        pref.refresh_devices()
        for d in pref.devices:
            d.use = d.type == "CUDA"
        cena.cycles.device = "GPU"
    except Exception as e:
        print("GPU indisponível:", e)
    cena.cycles.samples = int(OPC["amostras"])
    cena.cycles.use_adaptive_sampling = True
    cena.cycles.adaptive_threshold = 0.03
    try:
        cena.cycles_curves.shape = "THICK"      # ribbons took the shading of each ground triangle: patches
    except Exception:
        pass
    cena.cycles.use_denoising = True
    try:
        cena.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    cena.cycles.max_bounces = 8
    cena.cycles.transparent_max_bounces = 8
    w, h = [int(v) for v in OPC["res"].split("x")]
    cena.render.resolution_x, cena.render.resolution_y = w, h
    cena.render.resolution_percentage = 50 if OPC.get("previa") else 100
    try:
        cena.view_settings.view_transform = "AgX"
        cena.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    cena.view_settings.exposure = float(E.get("sol", {}).get("exposicao", 0.0))
    cena.render.image_settings.file_format = "JPEG"
    cena.render.image_settings.quality = 88
    nomes = list(cams) if OPC["render"] == "todas" else OPC["render"].split(",")
    VV = {v["nome"]: v for v in E.get("vistas", [])}
    for n in nomes:
        cena.camera = cams[n]
        wv, hv = [int(q) for q in VV[n].get("res", OPC["res"]).split("x")]
        cena.render.resolution_x, cena.render.resolution_y = wv, hv
        cena.view_settings.exposure = float(VV[n].get("exposicao", E.get("sol", {}).get("exposicao", 0.0)))
        cena.render.filepath = os.path.join(SAIDA, f"render_{n}.jpg")
        t0 = __import__("time").time()
        bpy.ops.render.render(write_still=True)
        print("RENDER", n, round(__import__("time").time() - t0), "s")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, "casa.blend"))
print("FEITO")
