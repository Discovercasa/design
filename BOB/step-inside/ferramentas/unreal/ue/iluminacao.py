"""Runs INSIDE Unreal 5.8 (commandlet): the realistic light of the test level (Step Inside Phase 4, task 69).

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal/iluminacao.py -unattended -nop4 -NullRHI

Reads iluminacao.json next to this script:
  {"nivel": "/Game/Visita/<Nivel>", "destino": "/Game/<Obra>", "sol": {"azimute", "elevacao", "lux"},
   "candeeiro": {"padrao": "<text in the lamp actors' labels>", "lumens", "kelvin", "raio_cm"},
   "branco_k": white balance, "ev100": [min, max], "chao_m": side of the grass ground, "relva_m": grass texture size,
   "ocultas": [lower-case text of the layers never seen in a finished house: wool, OSB, membranes, battens…],
   "exposicao_ev", "tint": exposure bias and white tint, "relva_material": the terrain's glTF grass instance,
   "relva_cor": [r, g, b, a] multiplier of the grass, "ocultas_material": paint the hidden layers with this glTF
   instance instead of deleting them, "importar_resumo": importar.py's summary (the move to the origin),
   "luzes_extra": [{"nome", "blender_xy": [x, y], "altura_m" above the floor, "lumens", "kelvin"}]}
Why (first test, 2026-11-24): the glTF materials were right, the look was wrong because only the blue sky lit the
rooms, automatic exposure pushed everything up, no lamp was on, and software Lumen leaks through thin walls. So:
1. sun in real units (lux) from the afternoon side, sky atmosphere + volumetric clouds, sky light captured in real time;
2. a point light under every ceiling lamp (warm white, lumens), and the lamp shades glow;
3. one unbound post-process: white balance for daylight from the sky, auto exposure held in an EV100 range with local
   exposure (bright windows and the room both readable), Lumen at high quality with hit lighting for reflections
   (hardware ray tracing is switched on in the project's DefaultEngine.ini), little bloom, slight vignette;
4. a large grass ground under the site (the sky atmosphere's blue "planet" showed past the terrain's edge).
0. the layers inside the walls (wool, OSB, membranes, battens behind the cladding, hidden gutters): painted like the
   walls ("ocultas_material"; the model has small gaps at some wall/ceiling joints through which they showed as beige
   patches, and deleting them showed what lies behind instead) or taken out;
Idempotent: removes the SI_ actors it made before and makes them again.
"""
import json
import math
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "iluminacao.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mundo = unreal.EditorLoadingAndSavingUtils.load_map(CFG["nivel"])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
log = []


def diz(*a):
    s = " ".join(str(x) for x in a)
    log.append(s)
    unreal.log("SI_LUZ " + s)


atores = eas.get_all_level_actors()
FEITOS = ("SI_Sol", "SI_Atmosfera", "SI_LuzCeu", "SI_Nevoeiro", "SI_PosProcesso", "SI_Nuvens", "SI_Chao", "SI_Luz_")
for a in atores:
    if a.get_actor_label().startswith(FEITOS):
        eas.destroy_actor(a)
atores = eas.get_all_level_actors()
fora = [a for a in atores if isinstance(a, unreal.StaticMeshActor)
        and any(k in a.get_actor_label().lower() for k in CFG.get("ocultas", []))]
pintura = None
if CFG.get("ocultas_material"):  # paint them like the walls: the model's small gaps (wall/ceiling joints) then vanish
    for p in unreal.EditorAssetLibrary.list_assets(CFG["destino"], True, False):
        if p.split("/")[-1].split(".")[0] == CFG["ocultas_material"]:
            pintura = unreal.EditorAssetLibrary.load_asset(p)
for a in fora:
    if pintura:
        smc = a.static_mesh_component
        for i in range(len(smc.get_materials())):
            smc.set_material(i, pintura)
        smc.set_editor_property("cast_shadow", True)
    else:
        eas.destroy_actor(a)
diz("camadas interiores", "pintadas" if pintura else "retiradas", len(fora))
atores = eas.get_all_level_actors()
sy = -1  # Blender y -> Unreal -y (checked at import)

# 1. sun, sky, clouds, fog
az, el = CFG["sol"]["azimute"], CFG["sol"]["elevacao"]
dx, dy = -math.sin(math.radians(az)), -math.cos(math.radians(az))
sol = eas.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 2000),
                                 unreal.Rotator(0, -el, math.degrees(math.atan2(sy * dy, dx))))
sol.set_actor_label("SI_Sol")
lc = sol.get_component_by_class(unreal.DirectionalLightComponent)
lc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
lc.set_editor_property("intensity", float(CFG["sol"]["lux"]))
lc.set_editor_property("atmosphere_sun_light", True)
lc.set_editor_property("light_source_angle", 0.5357)  # the sun's real disc: soft shadow edges
ceu = eas.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))
ceu.set_actor_label("SI_Atmosfera")
nuv = eas.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0, 0, 0))
nuv.set_actor_label("SI_Nuvens")
sl = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 600))
sl.set_actor_label("SI_LuzCeu")
slc = sl.get_component_by_class(unreal.SkyLightComponent)
slc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
slc.set_editor_property("real_time_capture", True)
slc.set_editor_property("lower_hemisphere_is_black", False)
slc.set_editor_property("lower_hemisphere_color", unreal.LinearColor(0.08, 0.09, 0.06, 1))
nev = eas.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, -300))
nev.set_actor_label("SI_Nevoeiro")
fc = nev.get_component_by_class(unreal.ExponentialHeightFogComponent)
fc.set_editor_property("fog_density", 0.006)
fc.set_editor_property("fog_height_falloff", 0.05)

# 2. lamps
cand = CFG["candeeiro"]
n_luz = 0
for a in atores:
    rot = a.get_actor_label()
    if not isinstance(a, unreal.StaticMeshActor) or cand["padrao"].lower() not in rot.lower():
        continue
    o, e = a.get_actor_bounds(False)  # the whole pendant (cord and shade): the bulb sits 15 cm above its bottom
    p = eas.spawn_actor_from_class(unreal.PointLight, unreal.Vector(o.x, o.y, o.z - e.z + 15))
    n_luz += 1
    p.set_actor_label(f"SI_Luz_{n_luz:02d}")
    pc = p.get_component_by_class(unreal.PointLightComponent)
    pc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    pc.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    pc.set_editor_property("intensity", float(cand["lumens"]))
    pc.set_editor_property("use_temperature", True)
    pc.set_editor_property("temperature", float(cand["kelvin"]))
    pc.set_editor_property("attenuation_radius", float(cand["raio_cm"]))
    pc.set_editor_property("source_radius", 4.0)
    pc.set_editor_property("soft_source_radius", 10.0)
# extra ceiling lights where the test furniture has no lamp (e.g. the bathroom), placed in Blender world metres
try:
    with open(CFG["importar_resumo"], encoding="utf-8") as f:
        desl = json.load(f)["deslocamento_cm"]
except Exception:
    desl = None
for lx in CFG.get("luzes_extra", []):
    if desl is None:
        break
    x, y = lx["blender_xy"]
    pos = unreal.Vector(x * 100 + desl[0], sy * y * 100 + desl[1], lx["altura_m"] * 100)
    p = eas.spawn_actor_from_class(unreal.PointLight, pos)
    n_luz += 1
    p.set_actor_label(f"SI_Luz_{n_luz:02d}_{lx['nome']}")
    pc = p.get_component_by_class(unreal.PointLightComponent)
    pc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    pc.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    pc.set_editor_property("intensity", float(lx["lumens"]))
    pc.set_editor_property("use_temperature", True)
    pc.set_editor_property("temperature", float(lx["kelvin"]))
    pc.set_editor_property("attenuation_radius", 600.0)
    pc.set_editor_property("source_radius", 8.0)
diz("luzes", n_luz)

# 3. post-process
ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
ppv.set_actor_label("SI_PosProcesso")
ppv.set_editor_property("unbound", True)
ps = ppv.get_editor_property("settings")


def pp(nome, valor):
    ps.set_editor_property("override_" + nome, True)
    ps.set_editor_property(nome, valor)


pp("white_temp", float(CFG["branco_k"]))
pp("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM)
pp("auto_exposure_min_brightness", float(CFG["ev100"][0]))
pp("auto_exposure_max_brightness", float(CFG["ev100"][1]))
pp("auto_exposure_bias", float(CFG.get("exposicao_ev", 0.3)))
pp("white_tint", float(CFG.get("tint", 0.0)))
pp("auto_exposure_speed_up", 2.0)
pp("auto_exposure_speed_down", 1.5)
pp("local_exposure_highlight_contrast_scale", 0.7)
pp("local_exposure_shadow_contrast_scale", 0.85)
pp("bloom_intensity", 0.25)
pp("vignette_intensity", 0.25)
pp("lumen_scene_lighting_quality", 2.0)
pp("lumen_scene_detail", 2.0)
pp("lumen_final_gather_quality", 2.0)
pp("lumen_reflection_quality", 2.0)
pp("lumen_ray_lighting_mode", unreal.LumenRayLightingModeOverride.HIT_LIGHTING_FOR_REFLECTIONS)
pp("lumen_max_trace_distance", 20000.0)
ppv.set_editor_property("settings", ps)

# 4. grass ground under the site
terreno = [a for a in atores if isinstance(a, unreal.StaticMeshActor) and "terr" in a.get_actor_label().lower()]
zmin = min(a.get_actor_bounds(False)[0].z - a.get_actor_bounds(False)[1].z for a in terreno) if terreno else -250
mi_relva = None
if CFG.get("relva_material"):  # the terrain's glTF grass (it has the tiling parameters the ground needs)
    for p in unreal.EditorAssetLibrary.list_assets(CFG["destino"], True, False):
        if p.split("/")[-1].split(".")[0] == CFG["relva_material"]:
            mi_relva = unreal.EditorAssetLibrary.load_asset(p)
for a in terreno:
    for m in a.static_mesh_component.get_materials():
        if m and mi_relva is None:
            mi_relva = m  # the existing terrain's own material (grass)
diz("terreno", [a.get_actor_label() for a in terreno], "zmin cm", round(zmin), "relva", mi_relva.get_name() if mi_relva else None)
chao = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, zmin - 5))
chao.set_actor_label("SI_Chao")
smc = chao.static_mesh_component
smc.set_static_mesh(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane"))
lado = CFG["chao_m"] * 100
chao.set_actor_scale3d(unreal.Vector(lado / 100, lado / 100, 1))
if mi_relva:
    caminho = CFG["destino"] + "/MI_SI_Chao_Relva"
    if unreal.EditorAssetLibrary.does_asset_exist(caminho):
        unreal.EditorAssetLibrary.delete_asset(caminho)
    mi = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset("MI_SI_Chao_Relva", CFG["destino"], mi_relva)
    rep = CFG["chao_m"] / CFG["relva_m"]
    mel = unreal.MaterialEditingLibrary
    for n in mel.get_vector_parameter_names(mi):
        if str(n).endswith("_OffsetScale"):
            mel.set_material_instance_vector_parameter_value(mi, n, unreal.LinearColor(0, 0, rep, rep))
    if CFG.get("relva_cor"):  # real grass reflects ~20 %: the bright texture flooded the rooms with green light
        mel.set_material_instance_vector_parameter_value(mi, "BaseColorFactor", unreal.LinearColor(*CFG["relva_cor"]))
    mel.update_material_instance(mi)
    smc.set_material(0, mi)

unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
diz("FEITO")
if CFG.get("resumo"):
    with open(CFG["resumo"], "w", encoding="utf-8") as f:
        json.dump({"log": log}, f, ensure_ascii=False, indent=1)
