"""Runs INSIDE Unreal 5.8 (commandlet): our own glass material for the VR level, put on the meshes in place of chosen
glTF glass instances (Step Inside Phase 8).

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal-vr/vidros.py -unattended -nop4 -NullRHI

Reads vidros.json next to this script:
  {"nivel", "destino": "/Game/<Obra>", "mestre": "/Game/SI_Materiais/M_SI_Vidro",
   "vidros": {"<glTF material name>": {"Cor": [r, g, b], "Opacidade", "OpacidadeRasante", "Rugosidade", "Especular"}}}
Why (2026-11-26): the shower glass (glTF instance of MI_Default_Blend_DS) came out as an opaque white sheet in the
forward renderer, whatever its colour, alpha, roughness or specular. M_SI_Vidro is plain and under our control:
translucent, lit per pixel ("Surface ForwardShading": the reflection captures show in it), two-sided, no refraction
(cheap in VR); BaseColor = Cor, Roughness, Specular, Metallic 0, and Opacity = lerp(Opacidade, OpacidadeRasante,
Fresnel): nearly clear seen straight on, more reflective at a grazing angle, like real glass.
Each listed glTF instance becomes MI_SI_Vidro_<name> and the meshes that use it get it.
The white sheet itself was the sun: a STATIONARY sun lights translucent surfaces live but without its baked shadow,
so glass inside the closed bathroom (and the window panes, seen from inside: two-sided, lit from behind) got full
sunlight — 'ShowFlag.DirectionalLights 0' made the glass clear (2026-11-26). So with "sem_sol": true every mesh with a
translucent material moves to lighting channel 1 only (the sun stays on channel 0): it keeps the sky light, the
baked light (volumetric lightmap) and the reflection captures, loses only the sun. A mesh that mixes glass with
opaque parts (the shower: frame and tray) loses the sun on those too — fine indoors. Idempotent.
"""
import json
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vidros.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
ferr = unreal.AssetToolsHelpers.get_asset_tools()
mundo = unreal.EditorLoadingAndSavingUtils.load_map(CFG["nivel"])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def diz(*a):
    unreal.log("SI_VID " + " ".join(str(x) for x in a))


# 1. the glass material
pasta, nome = CFG["mestre"].rsplit("/", 1)
if eal.does_asset_exist(CFG["mestre"]):
    m = eal.load_asset(CFG["mestre"])
    mel.delete_all_material_expressions(m)
else:
    m = ferr.create_asset(nome, pasta, unreal.Material, unreal.MaterialFactoryNew())
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
m.set_editor_property("translucency_lighting_mode", unreal.TranslucencyLightingMode.TLM_SURFACE)
m.set_editor_property("two_sided", True)


def no(cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def liga(a, sa, b, eb):
    if not mel.connect_material_expressions(a, sa, b, eb):
        raise RuntimeError(f"ligacao {a.get_name()}.{sa} -> {b.get_name()}.{eb}")


P = unreal.MaterialProperty
cor = no(unreal.MaterialExpressionVectorParameter, -600, -200, parameter_name="Cor",
         default_value=unreal.LinearColor(0.02, 0.025, 0.025, 1))
masc = no(unreal.MaterialExpressionComponentMask, -350, -200, r=True, g=True, b=True, a=False)
liga(cor, "", masc, "")
mel.connect_material_property(masc, "", P.MP_BASE_COLOR)
mel.connect_material_property(no(unreal.MaterialExpressionConstant, -350, -80, r=0.0), "", P.MP_METALLIC)
mel.connect_material_property(no(unreal.MaterialExpressionScalarParameter, -350, 0, parameter_name="Especular",
                                 default_value=0.5), "", P.MP_SPECULAR)
mel.connect_material_property(no(unreal.MaterialExpressionScalarParameter, -350, 80, parameter_name="Rugosidade",
                                 default_value=0.05), "", P.MP_ROUGHNESS)
op = no(unreal.MaterialExpressionScalarParameter, -600, 220, parameter_name="Opacidade", default_value=0.1)
oprs = no(unreal.MaterialExpressionScalarParameter, -600, 300, parameter_name="OpacidadeRasante", default_value=0.6)
fres = no(unreal.MaterialExpressionFresnel, -600, 380, exponent=5.0, base_reflect_fraction=0.0)
mist = no(unreal.MaterialExpressionLinearInterpolate, -350, 260)
liga(op, "", mist, "A")
liga(oprs, "", mist, "B")
liga(fres, "", mist, "Alpha")
mel.connect_material_property(mist, "", P.MP_OPACITY)
mel.recompile_material(m)
eal.save_loaded_asset(m)
diz("mestre", CFG["mestre"])

# 2. one instance per listed glTF glass, 3. the meshes get it
novos = {}
for gl, val in CFG["vidros"].items():
    caminho = f"{CFG['destino']}/SI_Materiais/MI_SI_Vidro_{gl}"
    if eal.does_asset_exist(caminho):
        mi = eal.load_asset(caminho)
    else:
        mi = ferr.create_asset(f"MI_SI_Vidro_{gl}", f"{CFG['destino']}/SI_Materiais", unreal.MaterialInstanceConstant,
                               unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, m)
    for k, v in val.items():
        if isinstance(v, list):
            mel.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(*[float(x) for x in v], 1.0))
        else:
            mel.set_material_instance_scalar_parameter_value(mi, k, float(v))
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)
    novos[gl] = mi
trocas = []
for a in eas.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor):
        continue
    smc = a.static_mesh_component
    for i, mat in enumerate(smc.get_materials()):
        if not mat:
            continue
        gl = mat.get_name()[len("MI_SI_Vidro_"):] if mat.get_name().startswith("MI_SI_Vidro_") else mat.get_name()
        if gl in novos:
            smc.set_material(i, novos[gl])
            trocas.append(f"{a.get_actor_label()}[{i}]")
diz("instancias", len(novos), "trocas", trocas)

# 4. glass without the sun (lighting channel 1 only)
if CFG.get("sem_sol"):
    canal = []
    for a in eas.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor):
            continue
        smc = a.static_mesh_component
        if any(mat and mat.get_blend_mode() == unreal.BlendMode.BLEND_TRANSLUCENT for mat in smc.get_materials()):
            smc.set_editor_property("lighting_channels", unreal.LightingChannels(False, True, False))
            canal.append(a.get_actor_label())
    diz("sem sol", len(canal), canal)
unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
diz("FEITO")
