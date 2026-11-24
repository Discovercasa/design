"""Runs INSIDE Unreal 5.8 (commandlet): per-material corrections of the imported glTF material instances
(Step Inside Phase 4, task 69).

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal/ajustes_materiais.py -unattended -nop4 -NullRHI

Reads ajustes_materiais.json next to this script:
  {"destino": "/Game/<Obra>",
   "texturas": [{"ficheiro": png, "nome": asset name, "srgb": false}],      imported into <destino>/SI_Ajustes
   "materiais": {"<instance name>": {"escalares": {param: value}, "vetores": {param: [r, g, b, a]},
                                    "texturas": {param: texture asset name}}}}
Why: the glTF instances are faithful to Blender, but some values read differently under Lumen (2026-11-24): the
floor's 0.2-0.4 roughness gave white sheets of sky reflection (now a satin 0.42-0.62 texture made by
blender_rugosidade.py), the pendant shades' partly metallic map made them look chrome (metal factor 0), the bright
grass of the ground and terrain flooded the rooms with green bounce light in the path tracer (darker, less saturated).
"""
import json
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ajustes_materiais.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mel = unreal.MaterialEditingLibrary
pasta = CFG["destino"] + "/SI_Ajustes"
tex = {}
for t in CFG.get("texturas", []):
    tarefa = unreal.AssetImportTask()
    tarefa.set_editor_property("filename", t["ficheiro"])
    tarefa.set_editor_property("destination_path", pasta)
    tarefa.set_editor_property("destination_name", t["nome"])
    tarefa.set_editor_property("automated", True)
    tarefa.set_editor_property("replace_existing", True)
    tarefa.set_editor_property("save", True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([tarefa])
    a = unreal.EditorAssetLibrary.load_asset(f"{pasta}/{t['nome']}")
    a.set_editor_property("srgb", bool(t.get("srgb", False)))
    a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    unreal.EditorAssetLibrary.save_loaded_asset(a)
    tex[t["nome"]] = a
    unreal.log(f"SI_AJ textura {t['nome']} {a is not None}")
mis = {}
for p in unreal.EditorAssetLibrary.list_assets(CFG["destino"], True, False):
    d = unreal.EditorAssetLibrary.find_asset_data(p)
    if str(d.asset_class_path.asset_name) == "MaterialInstanceConstant":
        mis[str(d.asset_name)] = p
for nome, aj in CFG["materiais"].items():
    if nome not in mis:
        unreal.log_warning(f"SI_AJ sem material {nome}")
        continue
    mi = unreal.EditorAssetLibrary.load_asset(mis[nome])
    for k, v in aj.get("escalares", {}).items():
        mel.set_material_instance_scalar_parameter_value(mi, k, float(v))
    for k, v in aj.get("vetores", {}).items():
        mel.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(*[float(x) for x in v]))
    for k, v in aj.get("texturas", {}).items():
        mel.set_material_instance_texture_parameter_value(mi, k, tex[v])
    mel.update_material_instance(mi)
    unreal.EditorAssetLibrary.save_loaded_asset(mi)
    unreal.log(f"SI_AJ {nome} {aj}")
unreal.log("SI_AJ FEITO")
