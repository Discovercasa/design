"""Runs INSIDE Unreal 5.8 (commandlet): real reflections in the mirrors of the VR level (Step Inside Phase 8).

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal-vr/espelhos.py -unattended -nop4 -NullRHI

Reads espelhos.json next to this script:
  {"nivel", "materiais": [mirror material names, e.g. "MI_SI_INT_D3D9DE_06"], "mestre": "/Game/SI_Materiais/M_SI_Espelho",
   "cor": [r, g, b], "rugosidade", "percentagem_ecra": 50, "distancia_max_cm": 1500, "desvanecer_cm": [start, end]}
Why (2026-11-26): with baked light the forward renderer reflects only the reflection captures (one small sphere
"photo" per room, taken from its middle), so a mirror showed a flat grey sheet. A planar reflection renders the scene
again, mirrored, for the pixels on its plane: the mirror shows the room as it is. It needs the project setting
r.AllowGlobalClipPlane=True (projeto_vr/Config/DefaultEngine.ini) and, in the forward renderer, a material that asks
for it ("Planar Reflections" in its Forward Shading settings): without it the mirror stayed grey. So the mirror gets
its own material M_SI_Espelho (metal, "cor" and "rugosidade", planar reflections on), not the shared M_SI_PBR — the
other surfaces do not pay for it.
Each mirror is found from its geometry: the vertices of the mesh section with a mirror material (world space), the
vertical plane through them with the least spread, facing the nearest room (SI_VR_Reflexo_*), at the front face.
One PlanarReflection SI_VR_Espelho_<actor> per mirror, sized to it (its bounds decide when it renders), fading out
within a centimetre or two of the plane, so the wall behind the mirror is not touched. Idempotent.
"""
import json
import math
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "espelhos.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mundo = unreal.EditorLoadingAndSavingUtils.load_map(CFG["nivel"])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
# in a commandlet the static mesh editor module is not loaded: without it the subsystem is None and the old
# EditorStaticMeshLibrary fallback silently returned defaults (it logged "0 UV channels", set nothing)
unreal.SystemLibrary.execute_console_command(None, "Module Load StaticMeshEditor")
sme = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)


def diz(*a):
    unreal.log("SI_ESP " + " ".join(str(x) for x in a))


for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("SI_VR_Espelho_"):
        eas.destroy_actor(a)

# the mirror material: metal, planar reflections on in the forward renderer
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
pasta, nome = CFG["mestre"].rsplit("/", 1)
if eal.does_asset_exist(CFG["mestre"]):
    ESP = eal.load_asset(CFG["mestre"])
    mel.delete_all_material_expressions(ESP)
else:
    ESP = unreal.AssetToolsHelpers.get_asset_tools().create_asset(nome, pasta, unreal.Material,
                                                                  unreal.MaterialFactoryNew())
P = unreal.MaterialProperty
cor = mel.create_material_expression(ESP, unreal.MaterialExpressionConstant3Vector, -400, -100)
cor.set_editor_property("constant", unreal.LinearColor(*[float(x) for x in CFG.get("cor", [0.92, 0.92, 0.92])], 1.0))
mel.connect_material_property(cor, "", P.MP_BASE_COLOR)
um = mel.create_material_expression(ESP, unreal.MaterialExpressionConstant, -400, 50)
um.set_editor_property("r", 1.0)
mel.connect_material_property(um, "", P.MP_METALLIC)
rug = mel.create_material_expression(ESP, unreal.MaterialExpressionConstant, -400, 150)
rug.set_editor_property("r", float(CFG.get("rugosidade", 0.02)))
mel.connect_material_property(rug, "", P.MP_ROUGHNESS)
for k in ("use_planar_forward_reflections", "planar_forward_reflections", "b_use_planar_forward_reflections"):
    try:
        ESP.set_editor_property(k, True)
        diz("material: planar", k)
        break
    except Exception:
        pass
else:
    diz("material: SEM propriedade de reflexos planares")
mel.recompile_material(ESP)
eal.save_loaded_asset(ESP)
CFG["materiais"] = list(CFG["materiais"]) + [nome]
salas = [a.get_actor_location() for a in eas.get_all_level_actors()
         if a.get_actor_label().startswith("SI_VR_Reflexo_")]

# the preview plane's own size (local half extents at scale 1), to size each reflection to its mirror
t = eas.spawn_actor_from_class(unreal.PlanarReflection, unreal.Vector(0, 0, -100000), unreal.Rotator(0, 0, 0))
_, BASE = t.get_actor_bounds(False)
eas.destroy_actor(t)
diz("base", [round(x, 1) for x in (BASE.x, BASE.y, BASE.z)])


def pontos(smc, slot):
    malha = smc.static_mesh
    tr = smc.get_world_transform()
    pts = []
    for s in range(malha.get_num_sections(0)):
        try:
            ms = sme.get_lod_material_slot(malha, 0, s)
        except Exception:
            ms = s
        if ms == slot:
            v = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(malha, 0, s)[0]
            pts += [tr.transform_location(p) for p in v]
    return pts


def poe(def_, nomes, valor):
    for n in nomes:
        try:
            def_.set_editor_property(n, valor)
            return n
        except Exception:
            pass
    diz("sem propriedade", nomes)


feitos = []
for a in eas.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor):
        continue
    smc = a.static_mesh_component
    for slot, mat in enumerate(smc.get_materials()):
        if not mat or mat.get_name() not in CFG["materiais"]:
            continue
        smc.set_material(slot, ESP)
        p = pontos(smc, slot)
        if len(p) < 3:
            diz("sem vertices", a.get_actor_label(), slot)
            continue
        cx, cy, cz = (sum(getattr(q, k) for q in p) / len(p) for k in "xyz")
        # the vertical plane with the least spread of the vertices along its normal
        th = min((i * 0.25 for i in range(720)), key=lambda g: sum(
            ((q.x - cx) * math.cos(math.radians(g)) + (q.y - cy) * math.sin(math.radians(g))) ** 2 for q in p))
        n = unreal.Vector(math.cos(math.radians(th)), math.sin(math.radians(th)), 0)
        sala = min(salas, key=lambda s: (s.x - cx) ** 2 + (s.y - cy) ** 2)
        if (sala.x - cx) * n.x + (sala.y - cy) * n.y < 0:
            n = unreal.Vector(-n.x, -n.y, 0)
        u = unreal.Vector(-n.y, n.x, 0)
        dn = [q.x * n.x + q.y * n.y for q in p]
        du = [q.x * u.x + q.y * u.y for q in p]
        dz = [q.z for q in p]
        frente = max(dn) - (cx * n.x + cy * n.y)
        mu = (max(du) + min(du)) / 2 - (cx * u.x + cy * u.y)
        loc = unreal.Vector(cx + n.x * (frente + 0.1) + u.x * mu, cy + n.y * (frente + 0.1) + u.y * mu,
                            (max(dz) + min(dz)) / 2)
        larg, alt = max(du) - min(du), max(dz) - min(dz)
        rot = unreal.MathLibrary.make_rot_from_zx(n, unreal.Vector(0, 0, 1))  # plane normal = local Z, local X up
        pr = eas.spawn_actor_from_class(unreal.PlanarReflection, loc, rot)
        pr.set_actor_label("SI_VR_Espelho_" + a.get_actor_label())
        pr.set_actor_scale3d(unreal.Vector(alt / (2 * BASE.x) * 1.05, larg / (2 * BASE.y) * 1.05, 1))
        c = pr.get_component_by_class(unreal.PlanarReflectionComponent)
        poe(c, ["normal_distortion_strength"], 0.0)
        poe(c, ["prefilter_roughness"], 0.0)
        poe(c, ["screen_percentage"], int(CFG.get("percentagem_ecra", 50)))
        poe(c, ["max_view_distance_override"], float(CFG.get("distancia_max_cm", 1500)))
        d0, d1 = CFG.get("desvanecer_cm", [0.5, 2.0])
        poe(c, ["distance_from_plane_fadeout_start", "distance_from_plane_fade_start"], float(d0))
        poe(c, ["distance_from_plane_fadeout_end", "distance_from_plane_fade_end"], float(d1))
        feitos.append(pr.get_actor_label())
        diz(a.get_actor_label(), "slot", slot, "vertices", len(p), "normal", [round(n.x, 3), round(n.y, 3)],
            "plano", [round(loc.x), round(loc.y), round(loc.z)], "largura x altura cm", round(larg), round(alt),
            "espessura cm", round(max(dn) - min(dn), 1))
diz("espelhos", len(feitos), feitos)
unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
diz("FEITO")
