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
   "luzes_extra": [{"nome", "blender_xy": [x, y], "altura_m" above the floor, "lumens", "kelvin"}],
   VR (baked light, Phase 8): "mobilidade": "STATIC" (lamps baked by Lightmass), "mobilidade_sol": "STATIONARY" (sun
   and sky light: a static sun leaves the sky black), "ceu": "gradiente" (our own unlit sky dome instead of the sky
   atmosphere, which renders black in the VR project; "ceu_parametros" overrides its values), "nuvens": false (volumetric clouds
   cost too much per eye), "lumen": false (no Lumen post-process entries; the VR project has no Lumen)}
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


def ceu_gradiente(para_sol, par):
    """A sky dome: the engine's basic sphere with an unlit material M_SI_Ceu made here — horizon to zenith blue in
    real luminance (cd/m2, the units of the sun in lux), a halo and a small disc towards the sun, a dim neutral
    ground below the horizon (the sky light ignores it: lower hemisphere solid black). Movable and without shadows or collision: Lightmass ignores it (as static geometry it would block
    every sky ray of the bake) while the sky light and the reflection captures photograph it."""
    mel, eal = unreal.MaterialEditingLibrary, unreal.EditorAssetLibrary
    caminho = CFG["destino"] + "/M_SI_Ceu"
    if eal.does_asset_exist(caminho):
        m = eal.load_asset(caminho)
        mel.delete_all_material_expressions(m)
    else:
        m = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_SI_Ceu", CFG["destino"], unreal.Material,
                                                                     unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", True)
    val = {"luminancia": 9000.0, "horizonte": [0.62, 0.75, 0.95], "zenite": [0.16, 0.36, 0.85],
           "chao": [0.09, 0.09, 0.09], "halo": [1.0, 0.86, 0.62], "halo_forca": 0.5, "halo_exp": 10.0,
           "disco_forca": 6.0, "gradiente_exp": 0.5}
    val.update(par)
    xy = [0]

    def no(cls, **props):
        xy[0] += 1
        e = mel.create_material_expression(m, cls, -200 * (xy[0] % 8) - 300, 160 * (xy[0] // 8))
        for k, v in props.items():
            e.set_editor_property(k, v)
        return e

    def liga(a, b, entrada=""):
        mel.connect_material_expressions(a, "", b, entrada)

    def op(cls, a, b, **props):
        e = no(cls, **props)
        liga(a, e, "A")
        if b is not None:
            liga(b, e, "B")
        return e

    def rgb(e):  # a vector parameter gives four channels: keep three so the arithmetic types match
        k = no(unreal.MaterialExpressionComponentMask, r=True, g=True, b=True, a=False)
        liga(e, k)
        return k

    def cor(nome, c):
        return rgb(no(unreal.MaterialExpressionVectorParameter, parameter_name=nome,
                      default_value=unreal.LinearColor(c[0], c[1], c[2], 1.0)))

    def escalar(nome, v):
        return no(unreal.MaterialExpressionScalarParameter, parameter_name=nome, default_value=float(v))

    def um(cls, a, **props):
        e = no(cls, **props)
        liga(a, e, "Base" if cls == unreal.MaterialExpressionPower else "")
        return e

    olhar = op(unreal.MaterialExpressionMultiply, no(unreal.MaterialExpressionCameraVectorWS), None, const_b=-1.0)
    z = no(unreal.MaterialExpressionComponentMask, r=False, g=False, b=True, a=False)
    liga(olhar, z)
    t = um(unreal.MaterialExpressionPower, um(unreal.MaterialExpressionSaturate, z), const_exponent=val["gradiente_exp"])
    ceu_cor = no(unreal.MaterialExpressionLinearInterpolate)
    liga(cor("Horizonte", val["horizonte"]), ceu_cor, "A")
    liga(cor("Zenite", val["zenite"]), ceu_cor, "B")
    liga(t, ceu_cor, "Alpha")
    abaixo = um(unreal.MaterialExpressionSaturate, op(unreal.MaterialExpressionMultiply, z, None, const_b=-10.0))
    base = no(unreal.MaterialExpressionLinearInterpolate)
    liga(ceu_cor, base, "A")
    liga(cor("Chao", val["chao"]), base, "B")
    liga(abaixo, base, "Alpha")
    d = um(unreal.MaterialExpressionSaturate,
           op(unreal.MaterialExpressionDotProduct, olhar, cor("DirecaoSol", [para_sol.x, para_sol.y, para_sol.z])))
    halo = op(unreal.MaterialExpressionMultiply, um(unreal.MaterialExpressionPower, d, const_exponent=val["halo_exp"]),
              op(unreal.MaterialExpressionMultiply, cor("Halo", val["halo"]), escalar("HaloForca", val["halo_forca"])))
    disco = op(unreal.MaterialExpressionMultiply, um(unreal.MaterialExpressionPower, d, const_exponent=30000.0),
               escalar("DiscoForca", val["disco_forca"]))
    soma = op(unreal.MaterialExpressionAdd, op(unreal.MaterialExpressionAdd, base, halo), disco)
    final = op(unreal.MaterialExpressionMultiply, soma, escalar("Luminancia", val["luminancia"]))
    mel.connect_material_property(final, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    malha = eal.load_asset("/Engine/BasicShapes/Sphere")  # 5.8 no longer loads /Engine/EngineSky (BP_Sky_Sphere either)
    raio = malha.get_bounds().get_editor_property("sphere_radius")
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
    a.set_actor_label("SI_Ceu")
    smc = a.static_mesh_component
    smc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    smc.set_static_mesh(malha)
    smc.set_material(0, m)
    smc.set_editor_property("cast_shadow", False)
    smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    r = float(val.get("raio_m", 5000)) * 100  # beyond the sky light's 1.5 km threshold: it counts as sky
    a.set_actor_scale3d(unreal.Vector(r / raio, r / raio, r / raio))
    diz("ceu gradiente: raio da malha", round(raio), "escala", round(r / raio, 1), "sol", [round(c, 3) for c in (para_sol.x, para_sol.y, para_sol.z)])
    return a


atores = eas.get_all_level_actors()
FEITOS = ("SI_Sol", "SI_Atmosfera", "SI_Ceu", "SI_LuzCeu", "SI_Nevoeiro", "SI_PosProcesso", "SI_Nuvens", "SI_Chao", "SI_Luz_")
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
MOB = getattr(unreal.ComponentMobility, CFG.get("mobilidade", "MOVABLE"))
# the sun and the sky light may differ: a STATIC light does not exist in the game (baked only), so the sky atmosphere
# has no sun and renders black — in VR they are STATIONARY (indirect light baked, sun and sky live)
MOB_SOL = getattr(unreal.ComponentMobility, CFG.get("mobilidade_sol", CFG.get("mobilidade", "MOVABLE")))
lc.set_editor_property("mobility", MOB_SOL)
lc.set_editor_property("intensity", float(CFG["sol"]["lux"]))
lc.set_editor_property("atmosphere_sun_light", True)
lc.set_editor_property("light_source_angle", 0.5357)  # the sun's real disc: soft shadow edges
if CFG.get("ceu", "atmosfera") == "gradiente":
    # VR (forward renderer): the sky atmosphere drew a black sky there, so the sky light captured only the green
    # ground (a green cast indoors). An unlit sky dome of our own works in any renderer and costs one draw per eye
    lc.set_editor_property("atmosphere_sun_light", False)
    f = sol.get_actor_forward_vector()  # the light shines along it: the sun is the other way
    ceu = ceu_gradiente(unreal.Vector(-f.x, -f.y, -f.z), CFG.get("ceu_parametros", {}))
else:
    ceu = eas.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))
    ceu.set_actor_label("SI_Atmosfera")
if CFG.get("nuvens", True):
    nuv = eas.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0, 0, 0))
    nuv.set_actor_label("SI_Nuvens")
sl = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 600))
sl.set_actor_label("SI_LuzCeu")
slc = sl.get_component_by_class(unreal.SkyLightComponent)
slc.set_editor_property("mobility", MOB_SOL)
slc.set_editor_property("real_time_capture", MOB_SOL == unreal.ComponentMobility.MOVABLE)
if CFG.get("ceu", "atmosfera") == "gradiente":
    # baked light (VR): what comes from below is the real ground, bounced by Lightmass; a captured lower half of the
    # dome lit every ceiling (they face down) with its colour — olive-mustard ceilings in the living room
    slc.set_editor_property("lower_hemisphere_is_black", True)
    slc.set_editor_property("lower_hemisphere_color", unreal.LinearColor(0, 0, 0, 1))
else:
    slc.set_editor_property("lower_hemisphere_is_black", False)
    slc.set_editor_property("lower_hemisphere_color", unreal.LinearColor(0.08, 0.09, 0.06, 1))
if CFG.get("nevoeiro", True):  # VR: off (in the forward renderer it filled the rooms with a blue haze)
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
    pc.set_editor_property("mobility", MOB)
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
    pc.set_editor_property("mobility", MOB)
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
if CFG.get("lumen", True):
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
