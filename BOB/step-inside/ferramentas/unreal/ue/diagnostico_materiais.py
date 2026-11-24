"""Runs INSIDE Unreal 5.8 (commandlet): dumps every material instance of the imported house (parent, scalar, vector and
texture parameters) and which static-mesh actors use it, to diagnose the look (Step Inside Phase 4, task 69).

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal/diagnostico_materiais.py -unattended -nop4 -NullRHI

Reads diagnostico.json next to this script: {"destino": "/Game/<Obra>", "saida": out .json}.
"""
import json
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagnostico.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mel = unreal.MaterialEditingLibrary
out = []
for p in unreal.EditorAssetLibrary.list_assets(CFG["destino"], True, False):
    a = unreal.EditorAssetLibrary.load_asset(p)
    if not isinstance(a, unreal.MaterialInstanceConstant):
        continue
    d = {"nome": a.get_name(), "pai": a.get_editor_property("parent").get_path_name() if a.get_editor_property("parent") else None,
         "escalares": {}, "vetores": {}, "texturas": {}}
    for n in mel.get_scalar_parameter_names(a):
        d["escalares"][str(n)] = round(mel.get_material_instance_scalar_parameter_value(a, n), 4)
    for n in mel.get_vector_parameter_names(a):
        c = mel.get_material_instance_vector_parameter_value(a, n)
        d["vetores"][str(n)] = [round(c.r, 4), round(c.g, 4), round(c.b, 4), round(c.a, 4)]
    for n in mel.get_texture_parameter_names(a):
        t = mel.get_material_instance_texture_parameter_value(a, n)
        if t:
            d["texturas"][str(n)] = {"textura": t.get_name(), "srgb": t.get_editor_property("srgb"),
                                     "compressao": str(t.get_editor_property("compression_settings"))}
    for n in mel.get_static_switch_parameter_names(a) if hasattr(mel, "get_static_switch_parameter_names") else []:
        d.setdefault("interruptores", {})[str(n)] = mel.get_material_instance_static_switch_parameter_value(a, n)
    out.append(d)
json.dump(out, open(CFG["saida"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
unreal.log(f"SI_DIAG {len(out)} instancias")
