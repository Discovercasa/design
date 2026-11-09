"""Runs INSIDE Blender (>= 4.4): the VISIT model of a house (Step Inside Phase 2, hub tasks 57, 58, 61).

    blender --background --python blender_visita.py -- run.json        (opens run["casa_blend"] itself)

Starts from the production model that construir_casa.py already builds (reused, not rewritten) and, without
changing that file:
  1. moves every object into semantic collections (SITE_*, ARCH_*, STRUCT_TIMBER) and gives it a stable id
     (si_id = "<category>/<object name>"; the generator's names come from the drawings and do not change);
  2. hangs the house on one Empty, HOUSE_ROOT, placed on the site (corner, rotation, slab level from run.json);
  3. appends the terrain surfaces built by terreno/blender_tin.py, optionally with a platform cut into them;
  4. checks: closed meshes with outward normals, duplicates, plan dimensions against the sources, every opening of
     the sources open in the model, house against terrain;
  5. saves the visit .blend, a GLB of what is visible and a preview image.
run.json: see visita.py. Coordinates are local to the site origin (Blender keeps 32-bit floats).
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt

run = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
OUT = {"avisos": []}

# ------------------------------------------------------------------ 1. semantic collections
CATEGORIA = {"0": "ARCH_FOUNDATION", "1": "STRUCT_TIMBER", "2": "ARCH_WALLS_EXT", "3": "ARCH_WALLS_INT",
             "4": "ARCH_FLOORS", "5": "ARCH_CEILINGS", "6": "ARCH_ROOF", "7": "ARCH_OPENINGS", "8": "ARCH_PERGOLA",
             "9": "ARCH_LABELS"}
VISIVEIS = ("ARCH_FOUNDATION", "ARCH_WALLS_EXT", "ARCH_WALLS_INT", "ARCH_FLOORS", "ARCH_CEILINGS", "ARCH_ROOF",
            "ARCH_OPENINGS", "ARCH_REVEALS", "ARCH_PERGOLA")
A_VISTA = run.get("estrutura_a_vista", [])  # structure that is seen (e.g. the pergola): {"colecao_contem", "produto"}
sc = bpy.context.scene
vl = bpy.context.view_layer
raiz_prod = [c for c in sc.collection.children]


def layer_col(lc, nome):
    if lc.collection.name == nome:
        return lc
    for ch in lc.children:
        r = layer_col(ch, nome)
        if r:
            return r
    return None


def oculta(col_nome):
    """Hidden in the production file's default view (alternative finishes, labels)."""
    lc = layer_col(vl.layer_collection, col_nome)
    return bool(lc and (lc.hide_viewport or lc.exclude or lc.collection.hide_viewport))


def topo_numerado(col, pais):
    """The top numbered collection ('2 Paredes | …') above col; pais: child -> parent map."""
    c = col
    while c is not None:
        cid = c.name.split(" ", 1)[0]
        if cid[:1].isdigit() and "." not in cid:
            return c
        c = pais.get(c.name)
    return None


pais = {}
for c in bpy.data.collections:
    for ch in c.children:
        pais[ch.name] = c


def oculta_cadeia(col):
    c = col
    while c is not None:
        if oculta(c.name):
            return True
        c = pais.get(c.name)
    return False


cats = {}
for ob in list(bpy.data.objects):
    if ob.type in ("CAMERA", "LIGHT"):
        continue
    if not ob.users_collection:
        continue
    col = ob.users_collection[0]
    topo = topo_numerado(col, pais)
    cat = CATEGORIA.get(topo.name.split(" ", 1)[0], "ARCH_OTHER") if topo else "ARCH_OTHER"
    if oculta_cadeia(col) and cat not in ("ARCH_LABELS",):
        cat = "ARCH_OPTIONS" if cat in VISIVEIS else cat
    if cat == "STRUCT_TIMBER":
        regra = next((r for r in A_VISTA if r["colecao_contem"] in col.name), None)
        if regra:  # exposed structure: part of the visit, with the builder's product for it
            cat = "ARCH_PERGOLA" if "rgola" in col.name else "ARCH_OTHER"
            ob["si_produto_forcado"] = regra["produto"]
    cats[ob.name] = (cat, col.name)

VISITA = bpy.data.collections.new("VISITA")
sc.collection.children.link(VISITA)
grupos = {}
for nome, filhos in (("SITE", ("SITE_TERRAIN", "SITE_LIMIT")),
                     ("HOUSE", VISIVEIS + ("STRUCT_TIMBER", "ARCH_OPTIONS", "ARCH_LABELS", "ARCH_OTHER"))):  # noqa
    g = bpy.data.collections.new(nome)
    VISITA.children.link(g)
    for f in filhos:
        c = bpy.data.collections.new(f)
        g.children.link(c)
        grupos[f] = c
for nome, (cat, origem) in cats.items():
    ob = bpy.data.objects[nome]
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    grupos[cat].objects.link(ob)
    ob["si_id"] = f"{cat}/{nome}"
    ob["si_categoria"] = cat
    ob["si_colecao_producao"] = origem
    if ob.active_material:
        ob["si_material"] = ob.active_material.name
for c in raiz_prod:  # the production tree is now empty
    def apagar(col):
        for ch in list(col.children):
            apagar(ch)
        bpy.data.collections.remove(col)
    apagar(c)
for f in ("STRUCT_TIMBER", "ARCH_OPTIONS", "ARCH_LABELS"):  # not part of the visit (kept in the file)
    layer_col(vl.layer_collection, f).exclude = True
OUT["objetos_por_categoria"] = {k: len(c.objects) for k, c in grupos.items() if len(c.objects)}

# ------------------------------------------------------------------ 1b. common catalogue materials (Phase 3)
TAB = run.get("materiais") or {}
MATS = {}


def _lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


BOB_DIR = Path(run.get("bob_dir", "."))
DERIVADAS = BOB_DIR / "_trabalho" / "step-inside" / "texturas" / "derivadas"
FALTAM_TEXTURAS = set()


def _imagem(caminho, non_color=False):
    img = bpy.data.images.load(str(caminho), check_existing=True)
    if non_color:
        img.colorspace_settings.name = "Non-Color"
    return img


def _tingida(img, alvo_hex, nome):
    """A copy of the colour texture with its mean moved to the catalogue colour (cached as JPEG on the PC):
    GLB / USDZ cannot brighten a texture in the material, so the tint is baked into the image."""
    import numpy as np
    DERIVADAS.mkdir(parents=True, exist_ok=True)
    f = DERIVADAS / f"{nome}_{alvo_hex.lstrip('#').upper()}_Color.jpg"  # the colour is part of the key
    if f.exists() and f.stat().st_mtime > Path(img.filepath_from_user()).stat().st_mtime:
        return _imagem(f)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    media = px[:, :3].mean(axis=0)
    alvo = np.array(_lin(alvo_hex), dtype=np.float32)
    fator = np.clip(alvo / np.maximum(media, 1e-4), 0.0, 8.0)
    px[:, :3] = np.clip(px[:, :3] * fator, 0.0, 1.0)
    nova = bpy.data.images.new(f"{nome}_Color", w, h)
    nova.pixels.foreach_set(px.ravel())
    nova.filepath_raw = str(f)
    nova.file_format = "JPEG"
    nova.save()
    bpy.data.images.remove(nova)
    return _imagem(f)


def _texturas(e, m, bsdf):
    """Image nodes for the catalogue texture (Phase 3): colour (own / tinted) or flat colour + relief, normal, roughness."""
    tx = e.get("textura") or {}
    fonte = tx.get("fonte")
    if not fonte:
        return False
    pasta = BOB_DIR / fonte["pasta_local"]
    ficheiros = {k: next(iter(sorted(pasta.glob(f"*_{k}.jpg"))), None) for k in ("Color", "NormalGL", "Roughness")}
    if not pasta.exists() or not ficheiros["Color"]:
        FALTAM_TEXTURAS.add(fonte["asset"])
        return False
    nt = m.node_tree
    uso = tx.get("uso", "cor")
    x = -700
    if uso in ("cor", "tingir"):
        img = _imagem(ficheiros["Color"])
        if uso == "tingir":
            img = _tingida(img, e["pbr"]["base_color"], e["id"])
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image, n.location = img, (x, 300)
        nt.links.new(n.outputs["Color"], bsdf.inputs["Base Color"])
    if ficheiros["Roughness"]:
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image, n.location = _imagem(ficheiros["Roughness"], True), (x, 0)
        nt.links.new(n.outputs["Color"], bsdf.inputs["Roughness"])
    if ficheiros["NormalGL"]:
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image, n.location = _imagem(ficheiros["NormalGL"], True), (x, -300)
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.location = (-300, -300)
        nt.links.new(n.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    m["si_textura"] = f"{fonte['biblioteca']}:{fonte['asset']} ({fonte['licenca']}, {uso})"
    return True


def mat_catalogo(e):
    """One Blender material per catalogue ID (master + variant): Principled BSDF with the catalogue's PBR values and,
    when the catalogue has one, its texture."""
    if e["id"] in MATS:
        return MATS[e["id"]]
    m = bpy.data.materials.get(e["id"]) or bpy.data.materials.new(e["id"])
    m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    p = e["pbr"]
    cor = _lin(p["base_color"])
    a = p.get("opacity", 1.0)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*cor, 1.0)
        bsdf.inputs["Roughness"].default_value = p["roughness"]
        bsdf.inputs["Metallic"].default_value = p["metallic"]
        bsdf.inputs["Alpha"].default_value = a
    m.diffuse_color = (*cor, a)
    m.roughness = p["roughness"]
    m.metallic = p["metallic"]
    if a < 1.0:
        if hasattr(m, "surface_render_method"):
            m.surface_render_method = "BLENDED"
        elif hasattr(m, "blend_method"):
            m.blend_method = "BLEND"
    m["si_mat_id"] = e["id"]
    m["si_mestre"] = e["mestre"]
    m["si_variante"] = e["variante"]
    m["si_tile_m"] = list((e.get("textura") or {}).get("tile_m", [1.0, 1.0]))
    if (e.get("textura") or {}).get("rotacao_uv"):
        m["si_rotacao_uv"] = int(e["textura"]["rotacao_uv"])
    if bsdf and run.get("texturas", True):
        _texturas(e, m, bsdf)
    MATS[e["id"]] = m
    return m


def uv_real(ob, ref=None):
    """UVs in real metres divided by the material's tile size: box projection by the face's main axis, in the frame
    `ref` (the house root, so textures run on across the house's objects; the world for the terrain)."""
    if ob.type != "MESH" or not ob.data.polygons:
        return
    mat = ob.active_material
    tile = list(mat.get("si_tile_m", [1.0, 1.0])) if mat else [1.0, 1.0]
    girar = bool(mat and mat.get("si_rotacao_uv"))  # boards running vertical (e.g. Tremolo)
    M = (ref.inverted() if ref else Matrix.Identity(4)) @ ob.matrix_world
    R = M.to_3x3()
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = (R @ f.normal)
        ax = max(range(3), key=lambda i: abs(n[i]))
        for lp in f.loops:
            p = M @ lp.vert.co
            if ax == 2:      # horizontal face: plan
                u, v = p.x, p.y
            elif ax == 0:    # facing east / west
                u, v = p.y, p.z
            else:            # facing north / south
                u, v = p.x, p.z
            if girar and ax != 2:
                u, v = v, u
            lp[uv].uv = (u / tile[0], v / tile[1])
    bm.to_mesh(ob.data)
    bm.free()


def aplicar_materiais(obs):
    sem, usados, estados = {}, {}, {}
    for ob in obs:
        if not hasattr(ob, "material_slots"):
            continue
        ids = []
        for slot in ob.material_slots:
            if not slot.material:
                continue
            nome = ob.get("si_produto_forcado") or slot.material.get("si_producao", slot.material.name)
            if ob.get("si_categoria") == "SITE_TERRAIN" and run.get("material_terreno"):
                nome = run["material_terreno"]  # what covers the ground in this project (e.g. a lawn)
            e = TAB.get(nome)
            if not e:
                k = (nome, ob.get("si_categoria", ""))
                sem[k] = sem.get(k, 0) + 1
                continue
            novo = mat_catalogo(e)
            novo["si_producao"] = nome if nome != e["id"] else novo.get("si_producao", "")
            slot.link = "OBJECT" if slot.link == "OBJECT" else "DATA"
            slot.material = novo
            ids.append(e["id"])
            usados[e["id"]] = usados.get(e["id"], 0) + 1
            estados[e["estado"]] = estados.get(e["estado"], 0) + 1
        if ids:
            ob["si_mat_id"] = ids[0]
            if len(set(ids)) > 1:
                ob["si_mat_ids"] = ",".join(sorted(set(ids)))
    return sem, usados, estados


if TAB:
    _sem, _us, _est = aplicar_materiais([o for o in bpy.data.objects if o.name in cats])
    OUT["materiais"] = {"sem_mapa": [{"material": k[0], "categoria": k[1], "objetos": n} for k, n in sorted(_sem.items())],
                        "usados": dict(sorted(_us.items())), "estados": _est}

# ------------------------------------------------------------------ 1c. close the joints of the finish layers
# The production model draws each board / sheet with its joint (Tremolo 6 mm, Pladur 2 mm) so the pieces can be
# counted; on site the joints are closed (tongue and groove; taped and filled). Without the hidden layers behind, a
# joint is a slit into the wall (user 2026-11-09). Rule and tests: juntas.py. Floors and the pergola keep their gaps.
sys.path.insert(0, str(Path(sys.argv[sys.argv.index("--python") + 1]).resolve().parent))
import juntas as J  # noqa: E402

FECHAR_JUNTAS = ("ARCH_WALLS_EXT", "ARCH_WALLS_INT", "ARCH_CEILINGS", "ARCH_ROOF")


def ilhas_e_caixas(ob, bm):
    """The loose pieces of a mesh (islands of faces) and their boxes in model coordinates."""
    M = ob.matrix_world
    ilhas, visto = [], set()
    for f in bm.faces:
        if f in visto:
            continue
        pilha, vs = [f], set()
        visto.add(f)
        while pilha:
            g = pilha.pop()
            vs.update(g.verts)
            for e in g.edges:
                for h in e.link_faces:
                    if h not in visto:
                        visto.add(h)
                        pilha.append(h)
        ilhas.append(list(vs))
    caixas = []
    for vs in ilhas:
        pts = [M @ v.co for v in vs]
        caixas.append((tuple(min(p[k] for p in pts) for k in range(3)), tuple(max(p[k] for p in pts) for k in range(3))))
    return ilhas, caixas


def fechar_juntas(ob):
    """Each piece grows half the joint towards its neighbours (juntas.extensoes). Returns (closed, left after)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    M = ob.matrix_world
    R_inv = M.to_3x3().inverted()
    n = 0
    for _passo in range(3):  # a grown piece can meet a neighbour it did not overlap before: pass again
        ilhas, caixas = ilhas_e_caixas(ob, bm)
        ext, k = J.extensoes(caixas)
        if not k:
            break
        n += k
        for i, lados in ext.items():
            lo, hi = caixas[i]
            for v in ilhas[i]:
                p = M @ v.co
                d = Vector((0, 0, 0))
                for (a, s), dist in lados.items():
                    if s > 0 and p[a] >= hi[a] - 1e-4:
                        d[a] += dist
                    elif s < 0 and p[a] <= lo[a] + 1e-4:
                        d[a] -= dist
                if d.length:
                    v.co += R_inv @ d
    resto = J.extensoes(ilhas_e_caixas(ob, bm)[1])[1] if n else 0
    bm.to_mesh(ob.data)
    bm.free()
    return n, resto


_jf, _jr, _partilhadas = {}, 0, 0
for _cat in FECHAR_JUNTAS:
    for _ob in grupos[_cat].objects:
        if _ob.type != "MESH" or not _ob.data.polygons:
            continue
        if _ob.data.users > 1:  # a shared mesh would be changed for every object that uses it
            _partilhadas += 1
            continue
        _n, _r = fechar_juntas(_ob)
        if _n:
            _jf[_cat] = _jf.get(_cat, 0) + _n
        _jr += _r
OUT["juntas"] = {"fechadas": _jf, "restantes": _jr, "malhas_partilhadas_ignoradas": _partilhadas}


def objetos(*categorias, malhas=True):
    return [o for k in categorias for o in grupos[k].objects if not malhas or o.type == "MESH"]


def caixa(obs):
    pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    if not pts:
        return None
    return (Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)]))


# ------------------------------------------------------------------ 2. checks in model coordinates (before placing)
vl.update()
# the walls' timber (roof members overhang the walls: left out, as in ferramentas/modelo/verificar.py)
BEIRAL = ("Pérgola", "Viga de apoio à cobertura", "Madre", "Rincão", "Laró", "Viga de bordo", "Viga de bordadura", "Calço",
          "Prumo", "Empena", "EMP")
est_paredes = caixa([o for o in objetos("STRUCT_TIMBER") if not o.name.startswith(BEIRAL)
                     and not (o.parent and o.parent.name.startswith(BEIRAL))])
acab = caixa(objetos("ARCH_WALLS_EXT"))
D = {}
if est_paredes:
    D["estrutura_planta_m"] = [round(est_paredes[1].x - est_paredes[0].x, 3), round(est_paredes[1].y - est_paredes[0].y, 3)]
    D["estrutura_origem_m"] = [round(est_paredes[0].x, 3), round(est_paredes[0].y, 3)]
if acab:
    D["acabamento_planta_m"] = [round(acab[1].x - acab[0].x, 3), round(acab[1].y - acab[0].y, 3)]
    D["acabamento_canto_so_m"] = [round(acab[0].x, 3), round(acab[0].y, 3)]
casa_toda = caixa(objetos(*VISIVEIS))
if casa_toda:
    D["altura_total_m"] = round(casa_toda[1].z - casa_toda[0].z, 3)
    D["z_min_m"] = round(casa_toda[0].z, 3)
OUT["dimensoes_modelo"] = D

# closed meshes, outward normals, duplicates (visible house only)
abertas, invertidas, vistos, duplicados = [], [], {}, []
dg = bpy.context.evaluated_depsgraph_get()
for ob in objetos(*VISIVEIS):
    bm = bmesh.new()
    bm.from_object(ob, dg)
    if not bm.faces:
        bm.free()
        continue
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    vol = bm.calc_volume(signed=True)
    if nm:
        abertas.append({"objeto": ob.name, "arestas_abertas": nm})
    elif vol < -1e-9:
        invertidas.append({"objeto": ob.name, "volume_m3": round(vol, 4)})
    b = caixa([ob])
    chave = (tuple(round(v, 3) for v in b[0]) + tuple(round(v, 3) for v in b[1]), len(bm.verts), ob.get("si_material", ""))
    if chave in vistos:
        duplicados.append([vistos[chave], ob.name])
    else:
        vistos[chave] = ob.name
    bm.free()
OUT["malhas"] = {"verificadas": len(objetos(*VISIVEIS)), "abertas": abertas[:30], "n_abertas": len(abertas),
                 "normais_invertidas": invertidas[:30], "n_invertidas": len(invertidas),
                 "duplicados": duplicados[:30], "n_duplicados": len(duplicados)}

# every opening of the sources must be open in the model: horizontal rays across the wall at several heights
# walls only: what fills an opening (frames, glass, doors, shutters: ARCH_OPENINGS) is meant to be there
bvh_obs = objetos("ARCH_WALLS_EXT", "ARCH_WALLS_INT", "STRUCT_TIMBER")
verts, polys = [], []
for ob in bvh_obs:
    me = ob.evaluated_get(dg).to_mesh()
    k0 = len(verts)
    mw = ob.matrix_world
    verts += [mw @ v.co for v in me.vertices]
    polys += [[k0 + i for i in p.vertices] for p in me.polygons]
    ob.evaluated_get(dg).to_mesh_clear()
BVH_CASA = BVHTree.FromPolygons(verts, polys) if polys else None


def livre(p0, direcao, comp, eixo_parede, meia_espessura):
    """True when nothing of the house is hit within meia_espessura of the wall axis along the ray."""
    o = p0.copy()
    restante = comp
    while restante > 0:
        hit = BVH_CASA.ray_cast(o, direcao, restante)
        if hit[0] is None:
            return True
        d_eixo = abs((hit[0] - eixo_parede).dot(direcao))
        if d_eixo < meia_espessura:
            return False
        avanco = (hit[0] - o).length + 1e-4
        o = hit[0] + direcao * 1e-4
        restante -= avanco
    return True


def aberta(a, fracoes=(0.5, 0.3, 0.7), alturas=None):
    """The heights (above the storey's floor) at which the wall is open across the span a["inicio"]..a["fim"].
    0.3-2.0 m: clear of the floor build-up and of the space above the wall heads, inside every door and window."""
    zp = a["z_piso"]
    livres = []
    for fr in fracoes:
        s = a["inicio"] + (a["fim"] - a["inicio"]) * fr
        topo = min(20, int(round((a["altura_max"] - 0.1) * 10))) if a.get("altura_max") else 20
        for k in range(3, topo + 1):  # a low wall (altura_max) is open above its head: not tested there
            z = zp + 0.1 * k
            if a["eixo"] == "x":  # wall along x at y = posicao: ray along y
                p0, dr = Vector((s, a["posicao"] - 1.0, z)), Vector((0, 1, 0))
                eixo = Vector((s, a["posicao"], z))
            else:
                p0, dr = Vector((a["posicao"] - 1.0, s, z)), Vector((1, 0, 0))
                eixo = Vector((a["posicao"], s, z))
            if BVH_CASA and livre(p0, dr, 2.0, eixo, max(0.12, a.get("espessura", 0.16) / 2 + 0.12)):
                livres.append(round(0.1 * k, 1))
        if livres:
            return livres
    return livres


vaos = [{"parede": a["parede"], "abertura": a["id"], "tipo": a.get("tipo"), "aberta": bool(aberta(a))}
        for a in run.get("aberturas", [])]
# negative control: a solid stretch of each wall must come out closed, or the test itself is broken
controlo = []
for c in run.get("paredes_cheias", []):
    zl = aberta(c, (0.5,))
    controlo.append({"parede": c["parede"], "aberta": bool(zl), "alturas_livres": zl[:3] + zl[-2:] if zl else []})
OUT["aberturas"] = {"verificadas": len(vaos), "fechadas": [v for v in vaos if not v["aberta"]],
                    "controlo_paredes_cheias": len(controlo),
                    "controlo_abertas_por_engano": [c["parede"] for c in controlo if c["aberta"]],
                    "controlo_detalhe": [c for c in controlo if c["aberta"]]}

# ------------------------------------------------------------------ 2b. reveals: line every opening across the wall
# Without the hidden layers (studs, OSB, wool) the wall is two skins: at a door or window you see into the wall.
# The real hole is measured with rays (clear height and width), the wall faces next to it, and a thin lining
# (recessed into the wall, so the opening does not shrink) closes jambs, head and sill. Openings that already have
# trims in the model (frames / "remates" in ARCH_OPENINGS) are left as they are.
def hits_atraves(p0, dr, comp):
    """Distances of every hit along the ray (walls BVH)."""
    out, o, rest = [], p0.copy(), comp
    while rest > 0 and BVH_CASA:
        h = BVH_CASA.ray_cast(o, dr, rest)
        if h[0] is None:
            break
        d = (h[0] - p0).dot(dr)
        out.append(d)
        o = h[0] + dr * 1e-4
        rest = comp - d - 1e-4
    return out


def vao_aberto(a, s, z):
    if a["eixo"] == "x":
        p0, dr, eixo = Vector((s, a["posicao"] - 1.0, z)), Vector((0, 1, 0)), Vector((s, a["posicao"], z))
    else:
        p0, dr, eixo = Vector((a["posicao"] - 1.0, s, z)), Vector((1, 0, 0)), Vector((a["posicao"], s, z))
    return livre(p0, dr, 2.0, eixo, max(0.12, a.get("espessura", 0.16) / 2 + 0.12))


def ponto(a, s, n, z):
    return Vector((s, n, z)) if a["eixo"] == "x" else Vector((n, s, z))


def bvh_com_donos(obs):
    vs, ps, donos = [], [], []
    for ob in obs:
        me = ob.evaluated_get(dg).to_mesh()
        k0 = len(vs)
        mw = ob.matrix_world
        vs += [mw @ v.co for v in me.vertices]
        for p in me.polygons:
            ps.append([k0 + i for i in p.vertices])
            donos.append(ob)
        ob.evaluated_get(dg).to_mesh_clear()
    return (BVHTree.FromPolygons(vs, ps), donos) if ps else (None, [])


# Doors: the floor finish of each room stops at the wall face, so the opening showed the slab («o chão na zona das
# portas está em cimento», user 2026-11-09) — or, upstairs, a hole down to the ceiling below. The floor of the room
# on each side runs on to the middle of the wall (a change of finish falls under the door leaf); an exterior door
# takes the inside floor to the outside face (the threshold is not defined: question 23 per project).
BVH_PISOS, DONOS_PISOS = bvh_com_donos(objetos("ARCH_FLOORS"))
BAIXO = Vector((0, 0, -1))


def chao_do_vao(a, s0, s1, n0, n1, z0):
    """For a door: the floor pieces to add [(n_a, n_b, z_bottom, z_top, floor object)], or [] when the opening
    already has a floor (or a threshold) or there is no floor next to it."""
    if not BVH_PISOS:
        return []
    sm = (s0 + s1) / 2
    lados = []
    for nn in (n0 - 0.25, n1 + 0.25):
        h = BVH_PISOS.ray_cast(ponto(a, sm, nn, z0 + 0.4), BAIXO, 1.0)
        lados.append((h[0].z, DONOS_PISOS[h[2]]) if h[0] is not None else None)
    tem = [x for x in lados if x]
    if not tem:
        return []
    z_top = max(x[0] for x in tem)
    hc = BVH_CHAO.ray_cast(ponto(a, sm, (n0 + n1) / 2, z0 + 0.4), BAIXO, 1.0)
    if hc[0] is not None and hc[0].z >= z_top - 0.003:
        return []
    z_bot = min(z0 - E_FORRO, min(x[0] for x in tem) - 0.01)
    nm = (n0 + n1) / 2
    if len(tem) == 2 and tem[0][1].active_material != tem[1][1].active_material:
        return [(n0, nm, z_bot, tem[0][0], tem[0][1]), (nm, n1, z_bot, tem[1][0], tem[1][1])]
    return [(n0, n1, z_bot, z_top, max(tem, key=lambda x: x[0])[1])]


def caixa_malha(nome, blocos):
    bm = bmesh.new()
    for c1, c2 in blocos:
        lo_p, hi_p = Vector(map(min, c1, c2)), Vector(map(max, c1, c2))
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co = Vector((lo_p[i] + (v.co[i] + 0.5) * (hi_p[i] - lo_p[i]) for i in range(3)))
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    return me


aberturas_obs = [caixa([o]) for o in objetos("ARCH_OPENINGS")]
forros, saltados = [], 0
chaos, portas_com_chao = [], 0
E_FORRO = 0.015
BVH_CHAO, _ = bvh_com_donos(objetos("ARCH_FLOORS", "ARCH_OPENINGS"))
portas_meio = []
for a in run.get("aberturas", []) if TAB else []:
    if a.get("espessura", 0.16) < 0.01:  # an opening with no wall (e.g. an open passage added by the architecture)
        continue
    sc_ = (a["inicio"] + a["fim"]) / 2
    zp = a["z_piso"]
    zs = [zp + 0.02 * k for k in range(1, 161)]
    abertos = [z for z in zs if vao_aberto(a, sc_, z)]
    if not abertos:
        continue
    # the open run that holds the middle of the opening
    meio = abertos[len(abertos) // 2]
    z0 = z1 = meio
    while any(abs(z - (z0 - 0.02)) < 1e-6 for z in abertos):
        z0 -= 0.02
    while any(abs(z - (z1 + 0.02)) < 1e-6 for z in abertos):
        z1 += 0.02
    zm = (z0 + z1) / 2
    s0 = s1 = sc_
    while s0 > a["inicio"] - 0.5 and vao_aberto(a, s0 - 0.01, zm):
        s0 -= 0.01
    while s1 < a["fim"] + 0.5 and vao_aberto(a, s1 + 0.01, zm):
        s1 += 0.01
    # wall faces next to the opening (first and last hit across the wall)
    # only hits within this wall's band (structure + finishes), so a wall meeting at a corner is not counted;
    # of the two sides, the thinner reading is the wall itself
    faixa = a.get("espessura", 0.16) / 2 + 0.09
    faces = []
    for s_ in (s0 - 0.06, s1 + 0.06):
        p0 = ponto(a, s_, a["posicao"] - 0.8, zm)
        dr = Vector((0, 1, 0)) if a["eixo"] == "x" else Vector((1, 0, 0))
        hs = [d for d in hits_atraves(p0, dr, 1.6) if abs(d - 0.8) < faixa]
        if len(hs) >= 2:
            faces.append((min(hs) - 0.8, max(hs) - 0.8))
    if not faces:
        continue
    f_ = min(faces, key=lambda f: f[1] - f[0])
    n0, n1 = a["posicao"] + f_[0], a["posicao"] + f_[1]
    caixa_vao = (ponto(a, s0, n0, z0), ponto(a, s1, n1, z1))
    lo_v = Vector(map(min, *caixa_vao))
    hi_v = Vector(map(max, *caixa_vao))
    porta = z0 <= zp + 0.1 or a.get("tipo") == "porta"  # a door may measure open only above a plate left across it
    z_base = z0  # where the jambs start
    if porta:
        portas_meio.append((f"{a['parede']}#{a['id']}", ponto(a, (s0 + s1) / 2, (n0 + n1) / 2, z0 + 0.4)))
        pecas_chao = chao_do_vao(a, s0, s1, n0, n1, z0)
        if not pecas_chao:
            portas_com_chao += 1
        for k, (na, nb, zb_, zt_, piso) in enumerate(pecas_chao):
            nome = f"Chão do vão {a['parede']}#{a['id']}" + (f" ({'ab'[k]})" if len(pecas_chao) > 1 else "")
            me = caixa_malha(nome, [(ponto(a, s0, na, zb_), ponto(a, s1, nb, zt_))])
            ob = bpy.data.objects.new(nome, me)
            grupos["ARCH_FLOORS"].objects.link(ob)
            if piso.active_material:
                me.materials.append(piso.active_material)
            ob["si_categoria"] = "ARCH_FLOORS"
            ob["si_id"] = f"ARCH_FLOORS/{nome}"
            ob["si_material"] = piso.get("si_material", "")
            if piso.get("si_mat_id"):
                ob["si_mat_id"] = piso["si_mat_id"]
            cats[ob.name] = ("ARCH_FLOORS", "gerado: chão dos vãos das portas")
            chaos.append({"abertura": f"{a['parede']}#{a['id']}", "pavimento": piso.get("si_mat_id") or piso.name,
                          "z": [round(zb_, 3), round(zt_, 3)]})
            z_base = min(z_base, zb_)
    if any(b and all(b[0][i] < hi_v[i] + 0.02 and b[1][i] > lo_v[i] - 0.02 for i in range(3)) for b in aberturas_obs):
        saltados += 1
        continue
    zj = z0 - E_FORRO if not porta else z_base  # a door's jambs go down to its floor (no slit at the bottom)
    pecas = [(s0 - E_FORRO, s0, zj, z1 + E_FORRO),                                       # jamb
             (s1, s1 + E_FORRO, zj, z1 + E_FORRO),                                       # jamb
             (s0 - E_FORRO, s1 + E_FORRO, z1, z1 + E_FORRO)]                              # head
    if not porta:
        pecas.append((s0 - E_FORRO, s1 + E_FORRO, z0 - E_FORRO, z0))                      # sill
    me = caixa_malha(f"Forro do vão {a['parede']}#{a['id']}",
                     [(ponto(a, sa, n0, za), ponto(a, sb, n1, zb)) for sa, sb, za, zb in pecas])
    ob = bpy.data.objects.new(me.name, me)
    grupos["ARCH_REVEALS"].objects.link(ob)
    ob["si_categoria"] = "ARCH_REVEALS"
    ob["si_id"] = f"ARCH_REVEALS/{a['parede']}#{a['id']}"
    e = TAB.get("Pladur N") or TAB.get("MAT_INT_PLASTER_PAINTED__WHITE")
    if e:
        me.materials.append(mat_catalogo(e))
        ob["si_mat_id"] = e["id"]
        ob["si_material"] = "forro do vão (gerado)"
    cats[ob.name] = ("ARCH_REVEALS", "gerado: forro dos vãos")
    forros.append({"abertura": f"{a['parede']}#{a['id']}", "largura": round(s1 - s0, 3), "altura": round(z1 - z0, 3),
                   "espessura_parede": round(n1 - n0, 3)})
OUT["forros_vaos"] = {"criados": len(forros), "ja_com_remates": saltados, "detalhe": forros[:40]}
# check, independent of how the pieces were made: straight down from the middle of every door, the first thing hit
# is a floor (or a threshold) at the finished level, not the slab or the void of the floor below
_bvh_f, _donos_f = bvh_com_donos(objetos("ARCH_FLOORS", "ARCH_OPENINGS", "ARCH_FOUNDATION", "ARCH_CEILINGS"))
sem_chao = []
for _nome, _p in portas_meio:
    _h = _bvh_f.ray_cast(_p, BAIXO, 3.0) if _bvh_f else (None,)
    if _h[0] is None or _donos_f[_h[2]].get("si_categoria") not in ("ARCH_FLOORS", "ARCH_OPENINGS"):
        sem_chao.append({"abertura": _nome, "bate_em": _donos_f[_h[2]].name if _h[0] is not None else None})
OUT["chao_vaos"] = {"portas": len(portas_meio), "criados": len(chaos), "ja_com_chao": portas_com_chao,
                    "sem_chao": sem_chao, "detalhe": chaos[:40]}

# ------------------------------------------------------------------ 3. place the house on the site
C = run.get("colocacao")
root = bpy.data.objects.new("HOUSE_ROOT", None)
grupos["ARCH_OTHER"].objects.link(root)
root["si_id"] = "HOUSE_ROOT"
for ob in bpy.data.objects:
    if ob is not root and ob.parent is None and ob.name in cats:
        mw = ob.matrix_world.copy()
        ob.parent = root
        ob.matrix_world = mw
if C and "cota_pavimento" in C:  # slab level from the finished-floor level and the model's own floor build-up
    pisos = [o for o in objetos("ARCH_FLOORS") if caixa([o])[1].z < 1.0]
    pav = round(max(caixa([o])[1].z for o in pisos), 3) if pisos else 0.0
    C["z_laje"] = C["cota_pavimento"] - pav
    OUT["colocacao"] = {"pavimento_rc_modelo_m": pav}
if C and "origem_xy" in C:  # the model's (0, 0) placed directly (fit to the site plan's walls)
    rot = math.radians(C.get("rotacao_graus", 0.0))
    root.rotation_euler = (0, 0, rot)
    root.location = (C["origem_xy"][0], C["origem_xy"][1], C["z_laje"])
    OUT.setdefault("colocacao", {}).update({"rotacao_graus": C.get("rotacao_graus", 0.0), "z_laje": round(C["z_laje"], 3)})
elif C and acab:
    canto = {"NO": (acab[0].x, acab[1].y), "SO": (acab[0].x, acab[0].y), "NE": (acab[1].x, acab[1].y),
             "SE": (acab[1].x, acab[0].y)}[C["canto"]]
    rot = math.radians(C.get("rotacao_graus", 0.0))
    R = Matrix.Rotation(rot, 4, "Z")
    c_rot = R @ Vector((canto[0], canto[1], 0))
    root.rotation_euler = (0, 0, rot)
    root.location = (C["alvo_xy"][0] - c_rot.x, C["alvo_xy"][1] - c_rot.y, C["z_laje"])
    OUT["colocacao"] = {"canto_modelo": [round(canto[0], 3), round(canto[1], 3)], "rotacao_graus": C.get("rotacao_graus", 0.0),
                        "z_laje": C["z_laje"]}
vl.update()

# ------------------------------------------------------------------ 4. terrain (+ platform)
terreno = None
if run.get("terreno_blend"):
    with bpy.data.libraries.load(run["terreno_blend"], link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n.startswith(("SITE_TERRAIN", "SITE_LIMIT"))]
    for ob in dst.objects:
        if ob is None:
            continue
        cat = "SITE_TERRAIN" if ob.name.startswith("SITE_TERRAIN") else "SITE_LIMIT"
        grupos[cat].objects.link(ob)
        ob["si_categoria"] = cat
        ob["si_id"] = f"{cat}/{ob.name}"
    if TAB:
        _sem, _us, _est = aplicar_materiais([o for o in dst.objects if o is not None])
        OUT.setdefault("materiais", {"sem_mapa": [], "usados": {}, "estados": {}})
        for k, n in _us.items():
            OUT["materiais"]["usados"][k] = OUT["materiais"]["usados"].get(k, 0) + n
        OUT["materiais"]["sem_mapa"] += [{"material": k[0], "categoria": k[1], "objetos": n} for k, n in _sem.items()]
    alvo = run.get("superficie", "existente").upper()
    cand = [o for o in grupos["SITE_TERRAIN"].objects if o.name.endswith(alvo)] or list(grupos["SITE_TERRAIN"].objects)
    terreno = cand[0] if cand else None


def bvh_de(ob):
    me = ob.data
    mw = ob.matrix_world
    return BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])


def cota_terreno(bvh, x, y):
    h = bvh.ray_cast(Vector((x, y, 1e5)), Vector((0, 0, -1)))
    return h[0].z if h[0] is not None else None


def casa_terreno(bvh_t):
    """The ground under the house footprint against the slab top."""
    mw = root.matrix_world
    difs, fora = [], 0
    n = 24
    for i in range(n + 1):
        for j in range(n + 1):
            p = mw @ Vector((acab[0].x + (acab[1].x - acab[0].x) * i / n, acab[0].y + (acab[1].y - acab[0].y) * j / n, 0))
            z = cota_terreno(bvh_t, p.x, p.y)
            if z is None:
                fora += 1
            else:
                difs.append(z - C["z_laje"])
    if not difs:
        return {"amostras": 0, "fora_do_terreno": fora}
    acima_pav = [d for d in difs if d > run.get("pavimento_acima_laje", 0.16) + 0.02]
    return {"amostras": len(difs), "fora_do_terreno": fora, "terreno_menos_laje_min_m": round(min(difs), 2),
            "terreno_menos_laje_max_m": round(max(difs), 2),
            "fracao_terreno_acima_do_pavimento": round(len(acima_pav) / len(difs), 3)}


if terreno is not None and acab and C:
    OUT["casa_terreno_existente"] = casa_terreno(bvh_de(terreno))

PL = run.get("plataforma")
if terreno is not None and PL:
    # rebuild the surface with the platform outline as constrained edges; inside it the ground is flat at PL["z"]
    me = terreno.data
    pts = [(v.co.x, v.co.y) for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    if PL.get("contorno_casa"):  # the finished outline + margin, in site coordinates
        m = PL.get("margem_m", 1.0)
        mw = root.matrix_world
        cantos = [(acab[0].x - m, acab[0].y - m), (acab[1].x + m, acab[0].y - m), (acab[1].x + m, acab[1].y + m),
                  (acab[0].x - m, acab[1].y + m)]
        PL["contorno"] = [list((mw @ Vector((x, y, 0)))[:2]) for x, y in cantos]
    poly = PL["contorno"]

    def dentro(x, y):
        c = False
        for i in range(len(poly)):
            x0, y0 = poly[i]
            x1, y1 = poly[(i + 1) % len(poly)]
            if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                c = not c
        return c
    bvh_t0 = bvh_de(terreno)

    def na_borda(x, y, tol=0.01):
        for i in range(len(poly)):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
            dx, dy = x1 - x0, y1 - y0
            L2 = dx * dx + dy * dy or 1e-12
            t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
            if math.hypot(x0 + t * dx - x, y0 + t * dy - y) < tol:
                return True
        return False
    k0 = len(pts)
    pts += [tuple(q) for q in poly]
    zs += [PL["z"]] * len(poly)
    arestas = [(k0 + i, k0 + (i + 1) % len(poly)) for i in range(len(poly))]
    arestas += [tuple(e.vertices) for e in me.edges]  # keep the survey surface's own triangles outside the platform
    vs, _e, fs, orig, _oe, _of = delaunay_2d_cdt([Vector(p) for p in pts], arestas, [], 0, 1e-6, True)
    bm = bmesh.new()
    bv = []
    mudados = 0
    for i, v in enumerate(vs):
        k = orig[i][0] if orig[i] else None
        z = zs[k] if k is not None else (cota_terreno(bvh_t0, v.x, v.y) or PL["z"])
        if dentro(v.x, v.y) or na_borda(v.x, v.y):
            z = PL["z"]
            mudados += 1
        bv.append(bm.verts.new((v.x, v.y, z)))
    for f in fs:
        cx = sum(vs[i].x for i in f) / 3
        cy = sum(vs[i].y for i in f) / 3
        if cota_terreno(bvh_t0, cx, cy) is None:  # outside the trimmed survey surface
            continue
        try:
            bm.faces.new([bv[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    novo = bpy.data.meshes.new(me.name + "_PLATAFORMA")
    bm.to_mesh(novo)
    bm.free()
    for m in me.materials:
        novo.materials.append(m)
    terreno.data = novo
    terreno["si_plataforma"] = PL.get("nota", "")
    OUT["plataforma"] = {"vertices_rebaixados_ou_subidos": mudados, "z": PL["z"]}

if terreno is not None and acab and C:
    OUT["casa_terreno"] = casa_terreno(bvh_de(terreno))

G = run.get("chao_provisorio")  # no survey yet: a flat, clearly named placeholder (never presented as terrain)
if terreno is None and G:
    me = bpy.data.meshes.new("SITE_GROUND_PLACEHOLDER")
    h = G.get("tamanho", 60.0) / 2
    c = caixa(objetos(*VISIVEIS))
    cx, cy = ((c[0] + c[1]) / 2).x, ((c[0] + c[1]) / 2).y
    z = G.get("z", 0.0)
    me.from_pydata([(cx - h, cy - h, z), (cx + h, cy - h, z), (cx + h, cy + h, z), (cx - h, cy + h, z)], [], [(0, 1, 2, 3)])
    mat = mat_catalogo(TAB["MAT_SITE_PLACEHOLDER"]) if "MAT_SITE_PLACEHOLDER" in TAB else bpy.data.materials.new("MAT_SITE_PLACEHOLDER")
    me.materials.append(mat)
    ob = bpy.data.objects.new("SITE_GROUND_PLACEHOLDER", me)
    ob["si_categoria"] = "SITE_GROUND_PLACEHOLDER"
    ob["si_id"] = "SITE_GROUND_PLACEHOLDER"
    ob["si_nota"] = "chão provisório: NÃO é terreno (levantamento em falta)"
    grupos["SITE_TERRAIN"].objects.link(ob)
    OUT["chao_provisorio"] = {"z": z, "tamanho_m": 2 * h}

# ------------------------------------------------------------------ 4b. real-scale UVs (textures)
if TAB and run.get("texturas", True):
    raiz_m = root.matrix_world.copy()
    vistos_me = set()
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.data.name in vistos_me:
            continue
        vistos_me.add(ob.data.name)
        if ob.get("si_categoria", "").startswith("SITE"):
            uv_real(ob)
        elif ob.name in cats:
            if ob.data.users > 1:
                ob.data = ob.data.copy()  # shared mesh: UVs depend on where each copy sits
            uv_real(ob, raiz_m)
    OUT.setdefault("materiais", {})["texturas_em_falta"] = sorted(FALTAM_TEXTURAS)
    OUT["materiais"]["com_textura"] = sorted(k for k, m in MATS.items() if m.get("si_textura"))

# ------------------------------------------------------------------ 5. save, GLB, preview
for nome in ("SITE_LIMIT",):
    layer_col(vl.layer_collection, nome).exclude = False
mat_t = bpy.data.materials.get("MAT_SITE_TERRAIN")
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
if run.get("texturas", True) and TAB:
    motores = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in motores else "BLENDER_EEVEE"
    sol = bpy.data.objects.new("PREVIEW_SUN", bpy.data.lights.new("PREVIEW_SUN", "SUN"))
    sol.data.energy = 2.5
    sol.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
    sc.collection.objects.link(sol)
    sc.world = sc.world or bpy.data.worlds.new("World")
    sc.world.use_nodes = True
    bg = next((n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND"), None)
    if bg:
        bg.inputs["Color"].default_value = (0.55, 0.65, 0.8, 1.0)
        bg.inputs["Strength"].default_value = 0.5
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
else:
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "MATERIAL"
    sc.display.shading.show_cavity = True
    sc.display.shading.show_shadows = True
if run.get("glb"):
    bpy.ops.export_scene.gltf(filepath=run["glb"], export_format="GLB", use_visible=True, export_extras=True)
if run.get("preview"):
    alvo = caixa(objetos(*VISIVEIS))
    c = (alvo[0] + alvo[1]) / 2
    dim = max((alvo[1] - alvo[0]).x, (alvo[1] - alvo[0]).y)
    cam = bpy.data.objects.new("PREVIEW_CAM", bpy.data.cameras.new("PREVIEW_CAM"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = 28
    cam.data.clip_end = 3000
    cam.location = c + Vector((-1.6 * dim, -2.0 * dim, 1.1 * dim))
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = run["preview"]
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=run["blend"], compress=True)
json.dump(OUT, open(run["saida"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("VISITA_OK", json.dumps({k: OUT.get(k) for k in ("objetos_por_categoria",)}))
