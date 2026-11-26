"""Runs INSIDE Unreal 5.8 (commandlet): a real sky photo on the VR level's sky dome (Step Inside Phase 8).

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal-vr/ceu_hdri.py -unattended -nop4 -NullRHI

Reads ceu_hdri.json next to this script:
  {"nivel", "destino", "exr": "<blender_ceu.py's .exr on this PC>", "relatorio": "<its .json>",
   "media_alvo_cd": mean luminance (cd/m2) of the upper sky the level was tuned with, "espelhar": false,
   "usar": "hdri" | "gradiente" (back to iluminacao.py's M_SI_Ceu)}
Why (2026-11-26, user: the Twinmotion examples' surroundings look real; «então descarrega»): the drawn gradient sky
looked drawn from the windows. The photo (Poly Haven, CC0; its sun already capped by blender_ceu.py, since the level
has its own baked sun) goes on the same dome SI_Ceu, which stays movable and unlit: no new bake. What changes:
1. the .exr becomes T_SI_Ceu (2D, HDR-compressed BC6H, no mips: the dome samples the full size, 8k = about 23 pixels
   per degree, close to a Quest 2's pixels; Unreal reads a .hdr as a cube map, hence the .exr);
2. M_SI_CeuHDRI: the eye's direction → longitude and latitude → the panorama, turned so the photo's sun column lies at
   the azimuth of the level's sun SI_Sol (the photo's sun is 38 degrees up, the level's 28: the nearest clear sky),
   times "Escala" = media_alvo_cd / the photo's mean, so the sky light and the interiors keep their balance;
3. SI_Ceu gets it. The stationary sky light photographs the dome again when the level loads; the reflection captures
   keep the old sky until the next light bake (cozer_gui.py).
"""
import json
import math
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ceu_hdri.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mundo = unreal.EditorLoadingAndSavingUtils.load_map(CFG["nivel"])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mel, eal = unreal.MaterialEditingLibrary, unreal.EditorAssetLibrary


def diz(*a):
    unreal.log("SI_CEU " + " ".join(str(x) for x in a))


atores = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
cupula, sol = atores.get("SI_Ceu"), atores.get("SI_Sol")
if not cupula or not sol:
    raise RuntimeError("sem SI_Ceu ou SI_Sol: correr iluminacao.py com \"ceu\": \"gradiente\" primeiro")

if CFG.get("usar", "hdri") == "gradiente":
    cupula.static_mesh_component.set_material(0, eal.load_asset(CFG["destino"] + "/M_SI_Ceu"))
    diz("cupula: gradiente")
else:
    with open(CFG["relatorio"], encoding="utf-8") as f:
        REL = json.load(f)
    # 1. the panorama
    pasta = CFG["destino"] + "/SI_Ceu"
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", CFG["exr"])
    t.set_editor_property("destination_path", pasta)
    t.set_editor_property("destination_name", "T_SI_Ceu")
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", False)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    tex = eal.load_asset(pasta + "/T_SI_Ceu")
    if not isinstance(tex, unreal.Texture2D):
        raise RuntimeError(f"T_SI_Ceu nao e Texture2D: {type(tex)}")
    for k, v in (("compression_settings", unreal.TextureCompressionSettings.TC_HDR_COMPRESSED),
                 ("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),
                 ("lod_group", unreal.TextureGroup.TEXTUREGROUP_WORLD),  # the Skybox group caps at 2048 in places
                 ("srgb", False), ("never_stream", True),
                 ("address_x", unreal.TextureAddress.TA_WRAP), ("address_y", unreal.TextureAddress.TA_CLAMP)):
        tex.set_editor_property(k, v)
    eal.save_loaded_asset(tex)
    diz("textura", tex.blueprint_get_size_x(), "x", tex.blueprint_get_size_y())

    # 2. the material
    caminho = CFG["destino"] + "/M_SI_CeuHDRI"
    if eal.does_asset_exist(caminho):
        m = eal.load_asset(caminho)
        mel.delete_all_material_expressions(m)
    else:
        m = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_SI_CeuHDRI", CFG["destino"], unreal.Material,
                                                                     unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", True)
    xy = [0]

    def no(cls, **props):
        xy[0] += 1
        e = mel.create_material_expression(m, cls, -220 * (xy[0] % 6) - 300, 170 * (xy[0] // 6))
        for k, v in props.items():
            e.set_editor_property(k, v)
        return e

    def liga(a, b, entrada=""):
        if not mel.connect_material_expressions(a, "", b, entrada):
            raise RuntimeError(f"ligacao {a.get_name()} -> {b.get_name()}.{entrada}")

    def mascara(e, canal):
        k = no(unreal.MaterialExpressionComponentMask, r=canal == "r", g=canal == "g", b=canal == "b", a=False)
        liga(e, k)
        return k

    olhar = no(unreal.MaterialExpressionMultiply, const_b=-1.0)  # from the eye outwards
    liga(no(unreal.MaterialExpressionCameraVectorWS), olhar, "A")
    x, y, z = (mascara(olhar, c) for c in "rgb")
    fi = no(unreal.MaterialExpressionArctangent2)
    liga(y, fi, "Y")
    liga(x, fi, "X")
    # Unreal is left-handed (X forward, Y right): turning right raises atan2(y, x), as moving right in the photo
    s = -1.0 if CFG.get("espelhar") else 1.0
    f = sol.get_actor_forward_vector()  # the light shines along it: the sun is the other way
    fi_sol = math.atan2(-f.y, -f.x)
    desvio = (REL["sol_coluna"] - s * fi_sol / (2 * math.pi)) % 1.0
    u0 = no(unreal.MaterialExpressionMultiply, const_b=s / (2 * math.pi))
    liga(fi, u0, "A")
    u1 = no(unreal.MaterialExpressionAdd)
    liga(u0, u1, "A")
    liga(no(unreal.MaterialExpressionScalarParameter, parameter_name="Desvio", default_value=desvio), u1, "B")
    u = no(unreal.MaterialExpressionFrac)
    liga(u1, u)
    zc = no(unreal.MaterialExpressionClamp, min_default=-1.0, max_default=1.0)
    liga(z, zc)
    th = no(unreal.MaterialExpressionArccosine)
    liga(zc, th)
    v = no(unreal.MaterialExpressionMultiply, const_b=1.0 / math.pi)
    liga(th, v, "A")
    uv = no(unreal.MaterialExpressionAppendVector)
    liga(u, uv, "A")
    liga(v, uv, "B")
    amostra = no(unreal.MaterialExpressionTextureSampleParameter2D, parameter_name="Ceu", texture=tex,
                 sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR,
                 mip_value_mode=unreal.TextureMipValueMode.TMVM_MIP_LEVEL, const_mip_value=0)
    liga(uv, amostra, "UVs")
    rgb = no(unreal.MaterialExpressionComponentMask, r=True, g=True, b=True, a=False)
    liga(amostra, rgb)
    escala = float(CFG["media_alvo_cd"]) / float(REL["media_metade_cima"])
    final = no(unreal.MaterialExpressionMultiply)
    liga(rgb, final, "A")
    liga(no(unreal.MaterialExpressionScalarParameter, parameter_name="Escala", default_value=escala), final, "B")
    mel.connect_material_property(final, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)

    # 3. the dome
    cupula.static_mesh_component.set_material(0, m)
    diz("cupula: hdri", os.path.basename(CFG["exr"]), "sol do nivel azimute", round(math.degrees(fi_sol), 1),
        "coluna do sol na foto", round(REL["sol_coluna"], 4), "desvio", round(desvio, 4), "escala", round(escala),
        "zenite cd", round(REL["zenite"] * escala), "horizonte cd", round(REL["horizonte"] * escala))
unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
diz("FEITO")
