"""Runs INSIDE Unreal 5.8 (Python; a commandlet is enough): builds the Step Inside test level of one house.

    ue_cmd.cmd -run=pythonscript -script="D:\\BOB-posto\\step-inside\\unreal\\importar.py" -unattended -nop4 -nosplash -NullRHI

Reads importar.json next to this script:
  {"glb": visit GLB (blender_para_unreal.py), "vistas": vistas.json (blender_vistas.py), "destino": "/Game/<Obra>",
   "nivel": "/Game/Visita/<Nivel>", "chao_m": finished floor level in Blender metres, "sol": {"azimute", "elevacao"},
   "resumo": out .json}
1. a new level; the GLB imported as a scene by Interchange (static meshes, PBR materials and textures, one actor per
   object, in the hierarchy of the file);
2. axes checked against the GLB's own box (Blender x, y, z m -> Unreal x, -y, z cm), then the whole house moved so the
   finished floor is at Z = 0 and the house near the origin (large coordinates cost precision in Unreal);
3. sun (directional light driving the sky atmosphere), sky light (real-time capture), height fog and an unbound
   post-process volume; a PlayerStart and one CameraActor per interior view (the same views as the Blender renders);
4. saves the level and the imported assets; writes the numbers to "resumo".
"""
import json
import math
import os
import time

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(AQUI, "importar.json"), encoding="utf-8"))
t0 = time.time()
log = []


def diz(*a):
    s = " ".join(str(x) for x in a)
    log.append(s)
    unreal.log("SI_IMPORT " + s)


les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

# a blank map, saved over the level's path at the end (the editor may have opened the old level at start-up: it is
# the project's startup map, so it cannot be deleted first)
mundo = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
if unreal.EditorAssetLibrary.does_directory_exist(CFG["destino"]):
    unreal.EditorAssetLibrary.delete_directory(CFG["destino"])
diz("novo nivel", mundo is not None)

# 1. the GLB as a scene
mgr = unreal.InterchangeManager.get_interchange_manager_scripted()
src = unreal.InterchangeManager.create_source_data(CFG["glb"])
par = unreal.ImportAssetParameters()
par.is_automated = True
par.replace_existing = True
nivel_atual = les.get_current_level()  # (World has no Python-visible persistent_level in 5.8)
if nivel_atual:
    par.import_level = nivel_atual
diz("import_scene", mgr.import_scene(CFG["destino"], src, par))
mgr.wait_until_all_tasks_done(False)
atores = eas.get_all_level_actors()
malhas = [a for a in atores if isinstance(a, unreal.StaticMeshActor)]
diz("atores", len(atores), "malhas", len(malhas), f"{time.time() - t0:.0f} s")


def caixa(lista):
    lo, hi = [1e18] * 3, [-1e18] * 3
    for a in lista:
        o, e = a.get_actor_bounds(False)
        for i, (c, x) in enumerate(((o.x, e.x), (o.y, e.y), (o.z, e.z))):
            lo[i], hi[i] = min(lo[i], c - x), max(hi[i], c + x)
    return lo, hi


# 2. axes and the move to the origin
G = json.load(open(os.path.join(os.path.dirname(CFG["glb"]), "resumo_glb.json"), encoding="utf-8"))
lo, hi = caixa(malhas)
bmin, bmax = G["caixa_min"], G["caixa_max"]
esperado_flip = ([bmin[0] * 100, -bmax[1] * 100, bmin[2] * 100], [bmax[0] * 100, -bmin[1] * 100, bmax[2] * 100])
esperado_igual = ([bmin[0] * 100, bmin[1] * 100, bmin[2] * 100], [bmax[0] * 100, bmax[1] * 100, bmax[2] * 100])
err = lambda e: max(abs(a - b) for a, b in zip(lo + hi, e[0] + e[1]))
sy = -1 if err(esperado_flip) <= err(esperado_igual) else 1
diz("caixa UE cm", [round(x) for x in lo], [round(x) for x in hi], "eixo Y", "invertido" if sy < 0 else "igual",
    "erro cm", round(min(err(esperado_flip), err(esperado_igual)), 1))
V = json.load(open(CFG["vistas"], encoding="utf-8"))
cx = sum(v["de"][0] for v in V["vistas"]) / len(V["vistas"])
cy = sum(v["de"][1] for v in V["vistas"]) / len(V["vistas"])
desl = unreal.Vector(-cx * 100, -sy * cy * 100, -CFG["chao_m"] * 100)


def ue(p):  # Blender world metres -> Unreal level cm (after the move)
    return unreal.Vector(p[0] * 100, sy * p[1] * 100, p[2] * 100) + desl


raizes = [a for a in atores if a.get_attach_parent_actor() is None]
for a in raizes:
    a.set_actor_location(a.get_actor_location() + desl, False, False)
lo2, hi2 = caixa(malhas)
diz("deslocado", [round(desl.x), round(desl.y), round(desl.z)], "raizes", len(raizes),
    "nova caixa", [round(x) for x in lo2], [round(x) for x in hi2])

# 3. light, sky, post-process, player start, cameras
az, el = CFG["sol"]["azimute"], CFG["sol"]["elevacao"]
dx, dy = -math.sin(math.radians(az)), -math.cos(math.radians(az))  # towards where the light goes (east x, north y)
yaw = math.degrees(math.atan2(sy * dy, dx))
sol = eas.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0, -el, yaw))
sol.set_actor_label("SI_Sol")
lc = sol.get_component_by_class(unreal.DirectionalLightComponent)
lc.set_editor_property("atmosphere_sun_light", True)
lc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
ceu = eas.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))
ceu.set_actor_label("SI_Atmosfera")
sl = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500))
sl.set_actor_label("SI_LuzCeu")
slc = sl.get_component_by_class(unreal.SkyLightComponent)
slc.set_editor_property("real_time_capture", True)
slc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
nev = eas.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, -200))
nev.set_actor_label("SI_Nevoeiro")
ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
ppv.set_actor_label("SI_PosProcesso")
ppv.set_editor_property("unbound", True)
ps = ppv.get_editor_property("settings")
ps.set_editor_property("override_auto_exposure_bias", True)
ps.set_editor_property("auto_exposure_bias", 0.5)
ppv.set_editor_property("settings", ps)

sala = next(v for v in V["vistas"] if v["id"] == "sala")
inicio = eas.spawn_actor_from_class(unreal.PlayerStart, ue([sala["de"][0], sala["de"][1], CFG["chao_m"] + 0.95]))
inicio.set_actor_label("SI_Inicio")
cams = []
for v in V["vistas"]:
    de, para = ue(v["de"]), ue(v["para"])
    d = para - de
    rot = unreal.Rotator(0, math.degrees(math.atan2(-d.z, math.hypot(d.x, d.y))) * -1, math.degrees(math.atan2(d.y, d.x)))
    cam = eas.spawn_actor_from_class(unreal.CameraActor, de, rot)
    cam.set_actor_label("SI_CAM_" + v["id"])
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", math.degrees(2 * math.atan(36.0 / (2 * v["lente"]))))
    cc.set_editor_property("constrain_aspect_ratio", False)
    cams.append(v["id"])
# an outside view from the south-west, at eye level 25 m away from the house centre
fora = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(-2200, sy * -2200, 250),
                                   unreal.Rotator(0, -4, math.degrees(math.atan2(sy * 2200, 2200))))
fora.set_actor_label("SI_CAM_exterior")
fora.get_component_by_class(unreal.CameraComponent).set_editor_property("field_of_view", 70.0)
cams.append("exterior")
diz("camaras", cams)

# 4. save
diz("guardar nivel", unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"]))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
mats = unreal.EditorAssetLibrary.list_assets(CFG["destino"], True, False)
n = {"Material": 0, "MaterialInstanceConstant": 0, "Texture2D": 0, "StaticMesh": 0}
for p in mats:
    c = unreal.EditorAssetLibrary.find_asset_data(p).asset_class_path.asset_name
    n[str(c)] = n.get(str(c), 0) + 1
diz("assets", n, f"total {time.time() - t0:.0f} s")
json.dump({"motor": unreal.SystemLibrary.get_engine_version(), "atores": len(eas.get_all_level_actors()),
           "malhas": len(malhas), "assets": n, "eixo_y": "invertido" if sy < 0 else "igual",
           "deslocamento_cm": [desl.x, desl.y, desl.z], "caixa_cm": [lo2, hi2], "camaras": cams,
           "segundos": round(time.time() - t0), "log": log}, open(CFG["resumo"], "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
diz("FEITO")
