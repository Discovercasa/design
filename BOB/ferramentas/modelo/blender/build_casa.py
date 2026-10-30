"""Runs INSIDE Blender (>= 4.4). Builds the editable house model: timber structure from the geometry JSON
plus the DiscoverCasa build-up layers from camadas.json (ferramentas/modelo/camadas.py).

    blender --background --factory-startup --python build_casa.py -- run.json
run.json = {"geometria": ..., "camadas": ... (optional), "blend": ..., "glb": ..., "glb_completa": ...}

Conventions: one Empty per wall module (named as in the drawings) with its members as children;
numbered collections that follow the build sequence (0 foundation, 1 structure, 2 outside of the walls,
3 inside of the walls, 4 floors, 5 ceilings, 6 roof covering); custom properties on every piece
(seccao, tipo, comprimento_m, volume_m3 / camada, produto, area_m2 ...); drawing colours for the timber.
"""
import json
import math
import re
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from ferramentas.modelo.geometria2d import analyse, area, clean  # noqa: E402

run = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
K = json.load(open(run["camadas"], encoding="utf-8")) if run.get("camadas") else None
G = json.load(open(run["geometria"], encoding="utf-8"))
E = G["alcados"]
NV = G["niveis"]
CASA = G["casa"]
L, D, T = CASA["comprimento"], CASA["profundidade"], CASA["espessura_exterior"]

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for coll in (bpy.data.collections, bpy.data.meshes, bpy.data.materials):
    for it in list(coll):
        coll.remove(it)

sc = bpy.context.scene
sc.name = G["nome"]
sc.unit_settings.system = "METRIC"
sc.unit_settings.scale_length = 1.0
sc.unit_settings.length_unit = "METERS"


def srgb(h):
    c = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def material(name, hexcol, rough=0.75):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    col = srgb(hexcol)
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*col, 1.0)
    b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*col, 1.0)
    m.roughness = rough
    return m


MAT = {"160x80": material("Madeira 160x80", "#F2B574"), "100x80": material("Madeira 100x80", "#A8D98A"),
       "cobertura": material("Madeira cobertura 160x80", "#E3A15E"), "osb": material("OSB", "#CDAE78", 0.9),
       "betao": material("Betão", "#A6A6A6", 0.95)}
# DiscoverCasa sections (colours as in the company's module drawings: red 110x75, orange 220x75)
for _sec, _cor in (("110x35", "#EDCF9E"), ("75x35", "#B9DDA0"), ("110x75", "#E2604A"), ("220x75", "#F29A3B"),
                   ("200x100", "#7C86C8")):  # 200x100: glulam beams (lameladas), blue as in drawing D2503
    MAT[_sec] = material(f"Madeira {_sec}", _cor)
DC = G["cobertura"].get("sistema") == "discovercasa"  # structure rebuilt by estrutura_dc.py


def natural(cid):
    return [int(x) for x in cid.split(".")]


# collection tree: id -> name. Layer collections (2..6) come from camadas.json; created in id order
DEF = {"0": "0 Fundação (indicativa)", "1": "1 Estrutura de madeira",
       "1.1": "1.1 Piso 0 | Paredes exteriores", "1.2": "1.2 Piso 0 | Paredes interiores",
       "1.3": "1.3 Piso 1 | Estrutura do pavimento", "1.4": "1.4 Piso 1 | Paredes exteriores",
       "1.5": "1.5 Piso 1 | Paredes interiores", "1.6": "1.6 Cobertura | estrutura"}
PLAT = G["cobertura"].get("tipo") == "platibanda"  # single storey, roof hidden behind a parapet
if DC:
    DEF.update({"1.6": "1.6 Vigas de amarração e afinação", "1.7": "1.7 Vigas de apoio ao teto 220x75",
                "1.8": "1.8 Platibanda (módulos sobre a amarração)" if PLAT else "1.8 Empenas (triângulos sobre a amarração)",
                "1.9": "1.9 Prumos e vigas de apoio à cobertura 110x75"})
DEF.update(G.get("colecoes_estrutura", {}))  # names set by the builder (e.g. lameladas, casa_planta.py)
DECK = K["colecao_osb_pavimento"] if K else "1.7"
SEM_PISO = G["pavimento"].get("sem_piso", False)  # no floor between storeys
if SEM_PISO:
    DEF.pop("1.3", None)
    DEF.pop("1.4", None)
    DEF.pop("1.5", None)
DEF[DECK] = f"{DECK} Piso 1 | OSB {round(NV.get('osb_pavimento', 0.018) * 1000)} mm (estrutural)"
VIS = {}
for c in (K["colecoes"] if K else []):
    DEF[c["id"]] = c["nome"]
    VIS[c["id"]] = c["visivel"]
if K:
    DEF["9"] = "9 Etiquetas das divisões"
    VIS["9"] = False
ROOT = bpy.data.collections.new(G["nome"])
sc.collection.children.link(ROOT)
CID = {}
for cid in sorted(DEF, key=natural):
    parent = CID.get(cid.rsplit(".", 1)[0]) if "." in cid else ROOT
    c = bpy.data.collections.new(DEF[cid])
    (parent or ROOT).children.link(c)
    CID[cid] = c
COL = {"fund": CID["0"], "p0e": CID["1.1"], "p0i": CID["1.2"], "pav": CID.get("1.3"), "p1e": CID.get("1.4"),
       "p1i": CID.get("1.5"), "cob": CID["1.6"], "osbf": CID[DECK], "emp": CID.get("1.8")}


def prism(name, pts, ext):
    c = Vector((0, 0, 0))
    for p in pts:
        c += p + ext / 2
    c /= len(pts)
    bm = bmesh.new()
    v0 = [bm.verts.new(p - c) for p in pts]
    v1 = [bm.verts.new(p + ext - c) for p in pts]
    bm.faces.new(v0)
    bm.faces.new(list(reversed(v1)))
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new([v0[i], v0[j], v1[j], v1[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me, c


def add(name, me, col, parent=None, loc=Vector((0, 0, 0)), mat=None, props=None):
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    ob.location = loc
    if mat is not None:
        me.materials.append(mat)
    for k, v in (props or {}).items():
        ob[k] = v
    return ob


def box(name, x0, x1, y0, y1, z0, z1, col, parent=None, ploc=Vector((0, 0, 0)), mat=None, props=None):
    me, c = prism(name, [Vector((x0, y0, z0)), Vector((x1, y0, z0)), Vector((x1, y1, z0)), Vector((x0, y1, z0))],
                  Vector((0, 0, z1 - z0)))
    return add(name, me, col, parent, c - ploc, mat, props)


def empty(name, col, loc, rot=0.0, size=0.35):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "ARROWS"
    e.empty_display_size = size
    col.objects.link(e)
    e.location = Vector(loc)
    e.rotation_euler = (0, 0, rot)
    return e


CENTRO = Vector((L / 2, D / 2, 0))
N = {"pecas": 0, "camadas": 0}


def build_panel(p):
    e = E[p["alcado"]]
    lvl, name, t = p["piso"], p["nome"], p["espessura"]
    col = COL["emp"] if lvl == 2 else COL[("p0" if lvl == 0 else "p1") + ("e" if p["tipo"] == "PE" else "i")]
    dc = e.get("sistema") == "discovercasa"  # members carry their own type and section
    ux, uy = p["sentido"]
    emp = empty(name, col, p["origem"], math.atan2(uy, ux))
    for k, v in (("painel", name), ("desenho_alcado", p["alcado"]), ("piso", lvl), ("espessura_parede_m", t),
                 ("largura_m", round(e["frame_u1"] - e["frame_u0"], 3)), ("altura_m", round(e["H"], 3))):
        emp[k] = v
    if p.get("fantasma"):  # parapet part of a full-height module: the members are in the module
        emp["fantasma"] = True
        return
    ly = Vector((-uy, ux, 0))
    o = Vector(p["origem"])
    fora = 1.0 if (o + ly * 0.1 - CENTRO).length > (o - ly * 0.1 - CENTRO).length else -1.0
    polys = [clean(m["poly"]) for m in e["members"]]
    infos = [analyse(pl) if len(pl) >= 3 else None for pl in polys]
    frame = [i for i, a in enumerate(infos) if a and not (a["sloped"] and a["tperp"] > 0.12)]
    hf = max(infos[i]["vmax"] for i in frame)  # top of the frame (plates classification)
    dupla_base = lvl == 0 and any(a and abs(a["vmin"] - 0.08) < 0.01 and a["du"] > 0.3 for a in infos)
    cnt = {}
    for pl, a, m in zip(polys, infos, e["members"]):
        if not a or area(pl) < 1e-5:
            continue
        depth, yc, length = t, 0.0, a["du"]
        if dc:
            tipo, length = m["tipo"], (a["longest"] if a["sloped"] else max(a["du"], a["dv"]))
        elif a["sloped"] and a["tperp"] > 0.12:
            tipo, depth, yc, length = "Viga de cobertura (empena)", 0.08, fora * (t / 2 - 0.04), a["longest"]
        elif a["sloped"]:
            tipo, length = "Travessa superior inclinada", a["longest"]
        elif a["dv"] > a["du"]:
            tipo, length = "Montante", a["dv"]
        else:
            if a["vmin"] < 0.01:
                tipo = "Soleira" if dupla_base else "Travessa inferior"
            elif lvl == 0 and abs(a["vmin"] - 0.08) < 0.01 and a["du"] > 0.3:
                tipo = "Travessa inferior"
            elif a["vmax"] > hf - 0.09:
                tipo = "Travessa superior"
            else:
                tipo = "Travessa intermédia"
        cnt[tipo] = cnt.get(tipo, 0) + 1
        on = f"{name} | {tipo} {cnt[tipo]:02d}"
        me, c = prism(on, [Vector((u, yc - depth / 2, v)) for u, v in pl], Vector((0, depth, 0)))
        sec = m["section"] if dc else ("160x80" if depth == 0.08 and t != 0.08 else m["section"])
        add(on, me, col, emp, c, MAT[sec] if sec in MAT else MAT["160x80"],
            {"seccao": sec, "tipo": tipo, "painel": name, "piso": lvl, "comprimento_m": round(length, 3),
             "volume_m3": round(area(pl) * depth, 5)})
        N["pecas"] += 1


for p in G["paineis"]:
    build_panel(p)

# ---------------------------------------------------------------- upper floor structure
# DiscoverCasa floor: joists and battens come in estrutura_extra; only the OSB deck is built here
PDC = G["pavimento"].get("sistema") == "discovercasa"
z0, z1 = NV["topo_paredes_piso0"], NV.get("topo_vigas_pavimento", NV["topo_paredes_piso0"])
pav = None if SEM_PISO else empty("Pavimento Piso 1", COL["pav"], (0, 0, z0), size=0.5)
cnt = {"Vigota": 0, "Viga": 0}
for f in ([] if PDC else G["pavimento"]["pecas"]):
    dx, dy = f["x1"] - f["x0"], f["y1"] - f["y0"]
    tipo = "Vigota" if dy >= dx else "Viga"
    cnt[tipo] += 1
    box(f"Pavimento | {tipo} {cnt[tipo]:02d}", f["x0"], f["x1"], f["y0"], f["y1"], z0, z1, COL["pav"], pav,
        Vector((0, 0, z0)), MAT["160x80"], {"seccao": "160x80", "tipo": tipo, "piso": 1,
                                             "comprimento_m": round(max(dx, dy), 3),
                                             "volume_m3": round(dx * dy * (z1 - z0), 5)})
    N["pecas"] += 1
ab = G["pavimento"].get("abertura_escada")
to = NV.get("osb_pavimento", 0.018)
mg = G["pavimento"].get("deck_margem", T)  # drawings: the upper exterior walls stand on rim joists
deck = [(mg, L - mg, mg, D - mg)]
if ab:
    ax0, ax1, ay0, ay1 = ab
    deck = [(mg, ax0, mg, D - mg), (ax1, L - mg, mg, D - mg), (ax0, ax1, mg, ay0)]
    if ay1 < D - mg - 0.01:
        deck.append((ax0, ax1, ay1, D - mg))
osb_nome = f"OSB {round(to * 1000)} mm (pavimento estrutural)"
for k, (a, b, c_, d_) in enumerate([] if SEM_PISO else deck, 1):
    box(f"Pavimento | OSB {k:02d}", a, b, c_, d_, z1, z1 + to, COL["osbf"], pav, Vector((0, 0, z0)), MAT["osb"],
        {"material": "OSB4 18 mm" if not PDC else "OSB/3 22 mm", "area_m2": round((b - a) * (d_ - c_), 3),
         **({"camada": osb_nome, "produto": "OSB/3 22 mm sobre os barrotes (utilizador 2026-10-09)"} if PDC else {})})

# ---------------------------------------------------------------- roof (gable, ridge along X)
if not DC:
    C = G["cobertura"]
    yr, zr = C["cumeeira_y"], C["cumeeira_z"]
    th = math.radians(C["inclinacao"])
    tn = math.tan(th)
    dz = C["altura_viga"] / math.cos(th)
    cob = empty("Cobertura", COL["cob"], (0, yr, zr), size=0.5)
    rafters = {}
    for r in G["cobertura_planta"]:
        dx, ds = r["x1"] - r["x0"], r["s1"] - r["s0"]
        if ds > dx and ds > 2.0 and 0.04 <= r["x0"] <= L - 0.12:  # outer gable rafters belong to the gable panels
            rafters[("N" if r["s0"] > 0 else "S", round(r["x0"], 3))] = r
    k = {"N": 0, "S": 0}
    for (side, _x), r in sorted(rafters.items()):
        sg = 1 if side == "N" else -1
        zc = C["apoio_z"][side]
        dt, db = (zr - zc) / tn, (zr - dz - zc) / tn
        pts = [Vector((r["x0"], yr, zr)), Vector((r["x0"], yr + sg * dt, zc)), Vector((r["x0"], yr + sg * db, zc)),
               Vector((r["x0"], yr, zr - dz))]
        k[side] += 1
        on = f"Cobertura | Viga {side} {k[side]:02d}"
        me, c = prism(on, pts, Vector((r["x1"] - r["x0"], 0, 0)))
        ln = math.hypot(dt, zr - zc)
        add(on, me, COL["cob"], cob, c - cob.location, MAT["cobertura"],
            {"seccao": "160x80", "tipo": "Viga de cobertura", "vertente": side, "comprimento_m": round(ln, 3),
             "volume_m3": round(0.08 * C["altura_viga"] * ln, 5)})
        N["pecas"] += 1
    s0, s1 = C.get("tarugos_s", [0.088, 0.124])
    kb = 0
    for r in G["cobertura_planta"]:
        dx, ds = r["x1"] - r["x0"], r["s1"] - r["s0"]
        if dx <= ds or dx < 0.2 or min(abs(abs(r["s0"]) - s0), abs(abs(r["s1"]) - s0)) > 0.01:
            continue
        sg = 1 if r["s0"] + r["s1"] > 0 else -1
        ptop = [Vector((r["x0"], yr + sg * s * math.cos(th), zr - s * math.sin(th))) for s in (s0, s1)]
        nrm = Vector((0, -sg * math.sin(th), -math.cos(th))) * C["altura_viga"]
        kb += 1
        on = f"Cobertura | Tarugo cumeeira {kb:02d}"
        me, c = prism(on, [ptop[0], ptop[1], ptop[1] + nrm, ptop[0] + nrm], Vector((dx, 0, 0)))
        add(on, me, COL["cob"], cob, c - cob.location, MAT["cobertura"],
            {"seccao": f"{round((s1 - s0) * 1000)}x160", "tipo": "Tarugo de cumeeira", "comprimento_m": round(dx, 3),
             "volume_m3": round(dx * (s1 - s0) * C["altura_viga"], 5)})
        N["pecas"] += 1
    for fr in C.get("frechais", []):
        (x0, x1), (y0, y1), zb = fr["x"], fr["y"], fr["z"]
        box(f"Cobertura | Frechal beirado {fr['lado']}", x0, x1, y0, y1, zb, zb + 0.16, COL["cob"], cob, cob.location,
            MAT["cobertura"], {"seccao": "80x160", "tipo": "Frechal de beirado", "comprimento_m": round(x1 - x0, 3),
                               "volume_m3": round((x1 - x0) * 0.08 * 0.16, 5)})
        N["pecas"] += 1

# ---------------------------------------------------------------- foundation (indicative)
F = G.get("fundacao")
if F:
    raft = [Vector((x, y, 0)) for x, y in F["contorno"]]

    def offset(poly, d):
        out = []
        for i in range(len(poly)):
            e1 = (poly[i] - poly[i - 1]).normalized()
            e2 = (poly[(i + 1) % len(poly)] - poly[i]).normalized()
            out.append(poly[i] + (Vector((-e1.y, e1.x, 0)) + Vector((-e2.y, e2.x, 0))) * d)
        return out

    def ring(name, outer, inner, za, zb):
        bm = bmesh.new()
        ob_ = [bm.verts.new((p.x, p.y, za)) for p in outer]
        ot_ = [bm.verts.new((p.x, p.y, zb)) for p in outer]
        ib_ = [bm.verts.new((p.x, p.y, za)) for p in inner]
        it_ = [bm.verts.new((p.x, p.y, zb)) for p in inner]
        for i in range(len(outer)):
            j = (i + 1) % len(outer)
            for f in ([ot_[i], ot_[j], it_[j], it_[i]], [ob_[i], ib_[i], ib_[j], ob_[j]],
                      [ob_[i], ob_[j], ot_[j], ot_[i]], [ib_[i], it_[i], it_[j], ib_[j]]):
                bm.faces.new(f)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        add(name, me, COL["fund"], None, Vector((0, 0, 0)), MAT["betao"])

    e_l = F.get("espessura_laje", 0.20)
    me, c = prism("Fundação | Laje", [p + Vector((0, 0, -e_l)) for p in raft], Vector((0, 0, e_l)))
    add("Fundação | Laje", me, COL["fund"], None, c, MAT["betao"], {"nota": F.get("nota", "")})
    mu, sa = F.get("muro", {}), F.get("sapata", {})
    if mu:
        ring("Fundação | Muro perimetral (altura indicativa)", raft, offset(raft, mu["largura"]), mu["base_z"], -e_l)
    if sa:
        fora = sa.get("fora", 0.225)
        ring("Fundação | Sapata corrida", offset(raft, -fora), offset(raft, sa["largura"] - fora),
             sa["base_z"], sa["base_z"] + sa["altura"])

# ---------------------------------------------------------------- build-up layers (camadas.json)
def malha(nome, pecas):
    """One mesh with every piece as an island. Pieces: {"b": base polygon, "e": extrusion} or {"b", "t"}."""
    bm = bmesh.new()
    for pc in pecas:
        b = [Vector(q) for q in pc["b"]]
        t = [q + Vector(pc["e"]) for q in b] if "e" in pc else [Vector(q) for q in pc["t"]]
        v0 = [bm.verts.new(q) for q in b]
        v1 = [bm.verts.new(q) for q in t]
        n = len(b)
        for f in (v0, list(reversed(v1))) + tuple([v0[i], v0[(i + 1) % n], v1[(i + 1) % n], v1[i]] for i in range(n)):
            try:
                bm.faces.new(f)
            except ValueError:  # degenerate side of a sliver piece
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    c = Vector((0, 0, 0))
    if bm.verts:
        lo = Vector([min(v.co[i] for v in bm.verts) for i in range(3)])
        hi = Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
        c = (lo + hi) / 2
        for v in bm.verts:
            v.co -= c
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    return me, c


for o in G.get("estrutura_extra", []):  # tie beams, ceiling beams, posts, purlins (estrutura_dc.py)
    me, c = malha(o["nome"], o["pecas"])
    sec_o = o["props"]["seccao"]
    add(o["nome"], me, CID[o["colecao"]], None, c, MAT.get(sec_o, MAT["osb"] if sec_o.startswith("OSB") else MAT["160x80"]), o["props"])
    N["pecas"] += 1

if K:
    for nome, m in K["materiais"].items():
        if nome in bpy.data.materials:  # already created above (timber sections)
            MAT[nome] = bpy.data.materials[nome]
        elif nome not in MAT:
            MAT[nome] = material(nome, m["cor"], m.get("rug", 0.8))
            MAT[nome].use_fake_user = True  # alternatives (e.g. Pladur H1 / F, Microcimento) stay available
    bpy.context.view_layer.update()
    for o in K["objetos"]:
        me, c = malha(o["nome"], o["pecas"])
        ob = add(o["nome"], me, CID[o["colecao"]], None, c, MAT[o["material"]], o["props"])
        if o.get("pai") and o["pai"] in bpy.data.objects:
            emp = bpy.data.objects[o["pai"]]
            ob.parent = emp
            ob.matrix_parent_inverse = emp.matrix_world.inverted()
        N["camadas"] += len(o["pecas"])
    MAT["etiqueta"] = material("Etiqueta", "#1E1E1E", 1.0)
    for e in K.get("etiquetas", []):
        cu = bpy.data.curves.new(e["texto"], "FONT")
        cu.materials.append(MAT["etiqueta"])
        cu.body, cu.size, cu.align_x, cu.align_y = e["texto"], 0.22, "CENTER", "CENTER"
        tx = bpy.data.objects.new(e["texto"], cu)
        tx.location = Vector(e["pos"])
        CID["9"].objects.link(tx)

# ---------------------------------------------------------------- views, camera, notes, save
vl = bpy.context.view_layer


def lc(layer, name):
    if layer.collection.name == name:
        return layer
    for ch in layer.children:
        r = lc(ch, name)
        if r:
            return r


def mostrar(visivel):
    """visivel(cid) -> bool for every numbered collection (eye icon + render)."""
    for cid, col in CID.items():
        on = visivel(cid)
        lc(vl.layer_collection, col.name).hide_viewport = not on
        col.hide_render = not on


def padrao(cid):
    """Default view: the complete house with the visible finish option. Only the top collection of an
    alternative is switched off, so turning its eye on shows all its layers."""
    return VIS.get(cid, True)


cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
cam.data.lens = 30
sc.collection.objects.link(cam)
cam.location = Vector((L / 2 + 14, D / 2 - 16.5, 11))
cam.rotation_euler = (Vector((L / 2, D / 2, 2.6)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
sun = bpy.data.objects.new("Sol", bpy.data.lights.new("Sol", "SUN"))
sun.data.energy = 3.0
sc.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
sc.world = sc.world or bpy.data.worlds.new("World")
sc.world.color = (0.8, 0.84, 0.9)
for scr in bpy.data.screens:
    for area_ in scr.areas:
        if area_.type == "VIEW_3D":
            for sp in area_.spaces:
                if sp.type == "VIEW_3D":
                    sp.shading.type = "SOLID"
                    sp.shading.color_type = "MATERIAL"
                    sp.shading.show_cavity = True
                    sp.region_3d.view_location = (L / 2, D / 2, 3.0)
                    sp.region_3d.view_distance = 24.0
                    sp.region_3d.view_rotation = Euler((math.radians(62), 0, math.radians(35))).to_quaternion()
                    sp.region_3d.view_perspective = "PERSP"

notes = "\n".join(f"- {n}" for n in G.get("notas_modelo", []))
opcoes = "\n".join(f"  Opção {k}: {v}" + ("  (visível)" if K and k == K["opcao_visivel"] else "")
                   for k, v in (K["opcoes"].items() if K else []))
divisoes = ", ".join(f"{k} {v} m²" for k, v in (K["divisoes"].items() if K else []))
estrutura_txt = ("ESTRUTURA DISCOVERCASA (mesmas dimensões e vãos dos desenhos): montantes 110x35 nas paredes "
                 "exteriores e 75x35 nas interiores a 40 cm livres, 110x75 nos cantos e vãos, sem travessas "
                 "intermédias; pavimento entre pisos com vigas 220x75 a 1 m e barrotes 110x75 deitados a 0,60 m (1.3) "
                 "sob o OSB 22; piso 1 com teto falso plano à altura da viga de amarração (1.6), vigas de apoio ao "
                 "teto 220x75 (1.7), empenas em triângulo (1.8), prumos e vigas de apoio à cobertura 110x75 (1.9)."
                 if DC else "ESTRUTURA COMO NOS DESENHOS DO ENGENHEIRO (montantes 160x80 / 100x80, vigas de cobertura).")
bpy.data.texts.new("LEIA-ME").write(f"""{G['nome'].upper()} - MODELO DA CASA (ESTRUTURA + CAMADAS DISCOVERCASA)
{G.get('descricao', '')}
Estrutura gerada a partir de: {G.get('origem_desenhos', '')}
Camadas: sistema construtivo DiscoverCasa (ferramentas/modelo/sistema_construtivo.json + config.json).

UNIDADES E EIXOS: metros. X = Este (face exterior Oeste = 0), Y = Norte (face exterior Sul = 0),
Z = cima (topo da laje = 0). Casa {L} x {D} m (estrutura).

{estrutura_txt}

COLEÇÕES (ordem da obra - ligar/desligar no ícone do olho):
  0 Fundação (indicativa)
  1 Estrutura de madeira (módulos: 1 Empty por painel, peças filhas; pavimento; cobertura)
  2 Paredes | camadas exteriores: 2.1 OSB 9 mm -> 2.2 Membrana Traspir 95 -> acabamento (escolha do cliente)
{opcoes}
     Para trocar de acabamento: desligar a opção visível e ligar outra (olho).
  3 Paredes | camadas interiores: 3.1 lã mineral (dentro dos módulos, filha de cada painel) -> 3.2 OSB 15 mm -> 3.3 Pladur
  4 Pavimentos (piso 0: XPS + betonilha; piso 1: OSB estrutural) + revestimento de piso
  5 Tetos: réguas de suspensão + perfis + cantoneira + Pladur; lã por cima (teto do piso 1 e entre as vigas
    do pavimento)
  6 Cobertura: vigas de apoio, painel sandwich imitação telha, cumeeira, remates, caleiras, tubos de queda
  9 Etiquetas das divisões (desligada)

DIVISÕES (espaços entre paredes de madeira, área útil): {divisoes}
  Revestimentos interiores, pavimento e teto têm 1 objeto por divisão: para zonas húmidas trocar o
  material para "Pladur H1 (hidrófugo)", junto a fontes de calor "Pladur F (ignífugo)" (Material > lista).

PROPRIEDADES (Object > Custom Properties): estrutura - seccao, tipo, comprimento_m, volume_m3;
camadas - camada, produto, area_m2 / comprimento_m, pecas, unidade.
Vãos (portas/janelas) deduzidos da estrutura: confirmar com o projeto de arquitetura.

NOTAS
{notes}

Regenerar: python ferramentas/modelo/construir_casa.py "<pasta do modelo>/config.json"
""")

# GLB 1: timber structure only (as before); GLB 2: complete house with the visible option; then save
if run.get("glb"):
    mostrar(lambda cid: cid.split(".")[0] in ("0", "1"))
    bpy.ops.export_scene.gltf(filepath=run["glb"], export_format="GLB", use_visible=True, export_extras=True)
mostrar(padrao)
if run.get("glb_completa") and K:
    bpy.ops.export_scene.gltf(filepath=run["glb_completa"], export_format="GLB", use_visible=True, export_extras=True)
bpy.ops.wm.save_as_mainfile(filepath=run["blend"], compress=True)
print("BUILD_OK", json.dumps(N), "objects", len(bpy.data.objects))
