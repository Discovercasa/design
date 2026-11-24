"""Runs INSIDE Unreal 5.8 (commandlet): the Step Inside master material and one instance of it per material of the
house (Step Inside Phase 4, task 69).

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal/material_mestre.py -unattended -nop4 -NullRHI

Reads material_mestre.json next to this script:
  {"nivel", "destino": "/Game/<Obra>", "mestre": "/Game/SI_Materiais/M_SI_PBR",
   "ajustes": {"<glTF material name>": {"RugMin", "RugMax", "Metal", "Especular"}}}
Why (2026-11-24): the glTF instances of the Interchange importer were faithful to Blender in their values, yet under
Lumen they read too reflective (the oak floor turned into a grey sheen, leather into silver). M_SI_PBR is plain and
under our control:
  BaseColor = T_Cor (sRGB) x Cor;  Roughness = lerp(RugMin, RugMax, T_MR.G);  Metallic = T_MR.B x Metal;
  Specular = Especular (0.5 = the standard 4 %);  Normal = T_Normal (OpenGL maps arrive already flipped).
Every opaque glTF instance on the level's meshes becomes MI_SI_<name> of M_SI_PBR with the same textures and factors
(T_MR keeps the glTF metal-rough texture: G roughness, B metal), plus the "ajustes"; the meshes get the new instances.
Glass (blend), leaves (mask) and our own MI_SI_* (the grass ground) stay as they are. Idempotent.
"""
import json
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "material_mestre.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
ferr = unreal.AssetToolsHelpers.get_asset_tools()
mundo = unreal.EditorLoadingAndSavingUtils.load_map(CFG["nivel"])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def diz(*a):
    unreal.log("SI_MM " + " ".join(str(x) for x in a))


# default textures: the ones the glTF instances use when a slot is empty (found on the instances themselves)
PADRAO = {}
for p in eal.list_assets(CFG["destino"], True, False):
    a = eal.load_asset(p)
    if isinstance(a, unreal.MaterialInstanceConstant):
        for n in mel.get_texture_parameter_names(a):
            t = mel.get_material_instance_texture_parameter_value(a, n)
            if t and t.get_name() in ("T_White_srgb", "T_White_Linear", "T_Generic_N"):
                PADRAO[t.get_name()] = t
    if len(PADRAO) == 3:
        break
diz("texturas padrao", sorted(PADRAO))

# 1. the master material
pasta, nome = CFG["mestre"].rsplit("/", 1)
if eal.does_asset_exist(CFG["mestre"]):
    m = eal.load_asset(CFG["mestre"])
    mel.delete_all_material_expressions(m)
else:
    m = ferr.create_asset(nome, pasta, unreal.Material, unreal.MaterialFactoryNew())
m.set_editor_property("two_sided", True)


def no(cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def liga(a, sa, b, eb):
    if not mel.connect_material_expressions(a, sa, b, eb):
        raise RuntimeError(f"ligacao {a.get_name()}.{sa} -> {b.get_name()}.{eb}")


T = unreal.MaterialSamplerType
t_cor = no(unreal.MaterialExpressionTextureSampleParameter2D, -900, -300, parameter_name="T_Cor",
           sampler_type=T.SAMPLERTYPE_COLOR, texture=PADRAO["T_White_srgb"])
cor = no(unreal.MaterialExpressionVectorParameter, -900, -60, parameter_name="Cor",
         default_value=unreal.LinearColor(1, 1, 1, 1))
masc = no(unreal.MaterialExpressionComponentMask, -650, -60, r=True, g=True, b=True, a=False)
liga(cor, "", masc, "")
base = no(unreal.MaterialExpressionMultiply, -400, -200)
liga(t_cor, "RGB", base, "A")
liga(masc, "", base, "B")
mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)

t_mr = no(unreal.MaterialExpressionTextureSampleParameter2D, -900, 150, parameter_name="T_MR",
          sampler_type=T.SAMPLERTYPE_LINEAR_COLOR, texture=PADRAO["T_White_Linear"])
rmin = no(unreal.MaterialExpressionScalarParameter, -650, 120, parameter_name="RugMin", default_value=0.0)
rmax = no(unreal.MaterialExpressionScalarParameter, -650, 200, parameter_name="RugMax", default_value=1.0)
rug = no(unreal.MaterialExpressionLinearInterpolate, -400, 150)
liga(rmin, "", rug, "A")
liga(rmax, "", rug, "B")
liga(t_mr, "G", rug, "Alpha")
mel.connect_material_property(rug, "", unreal.MaterialProperty.MP_ROUGHNESS)
metal = no(unreal.MaterialExpressionScalarParameter, -650, 320, parameter_name="Metal", default_value=0.0)
met = no(unreal.MaterialExpressionMultiply, -400, 320)
liga(t_mr, "B", met, "A")
liga(metal, "", met, "B")
mel.connect_material_property(met, "", unreal.MaterialProperty.MP_METALLIC)
esp = no(unreal.MaterialExpressionScalarParameter, -400, 450, parameter_name="Especular", default_value=0.5)
mel.connect_material_property(esp, "", unreal.MaterialProperty.MP_SPECULAR)
t_n = no(unreal.MaterialExpressionTextureSampleParameter2D, -900, 550, parameter_name="T_Normal",
         sampler_type=T.SAMPLERTYPE_NORMAL, texture=PADRAO["T_Generic_N"])
mel.connect_material_property(t_n, "RGB", unreal.MaterialProperty.MP_NORMAL)
mel.recompile_material(m)
eal.save_loaded_asset(m)
diz("mestre", CFG["mestre"])

# 2. one instance per opaque glTF instance, 3. the meshes get them
novos = {}


def converte(gl):
    nome = gl.get_name()
    if nome in novos:
        return novos[nome]
    caminho = f"{CFG['destino']}/SI_Materiais/MI_SI_{nome}"
    if eal.does_asset_exist(caminho):
        mi = eal.load_asset(caminho)
    else:
        mi = ferr.create_asset(f"MI_SI_{nome}", f"{CFG['destino']}/SI_Materiais", unreal.MaterialInstanceConstant,
                               unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, m)
    tex = lambda n: mel.get_material_instance_texture_parameter_value(gl, n)
    esc = lambda n: mel.get_material_instance_scalar_parameter_value(gl, n)
    for gn, sn in (("BaseColorTexture", "T_Cor"), ("MetallicRoughnessTexture", "T_MR"), ("NormalTexture", "T_Normal")):
        t = tex(gn)
        if t and t.get_name() not in PADRAO:
            mel.set_material_instance_texture_parameter_value(mi, sn, t)
    mel.set_material_instance_vector_parameter_value(mi, "Cor",
                                                     mel.get_material_instance_vector_parameter_value(gl, "BaseColorFactor"))
    val = {"RugMin": 0.0, "RugMax": esc("RoughnessFactor"), "Metal": esc("MetallicFactor"), "Especular": 0.5}
    val.update(CFG.get("ajustes", {}).get(nome, {}))
    for k, v in val.items():
        mel.set_material_instance_scalar_parameter_value(mi, k, float(v))
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)
    novos[nome] = mi
    return mi


trocas = 0
for a in eas.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor):
        continue
    smc = a.static_mesh_component
    for i, mat in enumerate(smc.get_materials()):
        if not isinstance(mat, unreal.MaterialInstanceConstant) or mat.get_name().startswith("MI_SI_"):
            continue
        pai = mat.get_editor_property("parent")
        if not pai or "Opaque" not in pai.get_name():
            continue  # glass (blend) and leaves (mask) keep the glTF material
        smc.set_material(i, converte(mat))
        trocas += 1
diz("instancias", len(novos), "trocas", trocas)
unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
diz("FEITO")
