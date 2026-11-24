"""Runs INSIDE Unreal 5.8 (commandlet): sets the look chosen from the variants on the level's own post-process volume
(SI_PosProcesso, made by iluminacao.py) — Step Inside Phase 4, task 69.

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal/pos_processo.py -unattended -nop4 -NullRHI

Reads pos_processo.json next to this script: {"nivel", "valores": {post-process property: value},
"camaras": {"<id>": {property: value}}} (enums as "Enum.VALUE", as in variantes.py). Only the given properties change;
"camaras" overrides on SI_CAM_<id> itself (e.g. the outside view needs less exposure than the rooms).
"""
import json
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pos_processo.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mundo = unreal.EditorLoadingAndSavingUtils.load_map(CFG["nivel"])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ppv = next(a for a in eas.get_all_level_actors() if a.get_actor_label() == "SI_PosProcesso")
ps = ppv.get_editor_property("settings")
for k, v in CFG["valores"].items():
    if isinstance(v, str) and "." in v:
        en, val = v.split(".", 1)
        v = getattr(getattr(unreal, en), val)
    elif isinstance(v, int) and not isinstance(v, bool):
        v = float(v)
    ps.set_editor_property("override_" + k, True)
    ps.set_editor_property(k, v)
ppv.set_editor_property("settings", ps)


def conv(v):
    if isinstance(v, str) and "." in v:
        en, val = v.split(".", 1)
        return getattr(getattr(unreal, en), val)
    return float(v) if isinstance(v, int) and not isinstance(v, bool) else v


for cid, props in CFG.get("camaras", {}).items():
    cam = next(a for a in eas.get_all_level_actors() if a.get_actor_label() == "SI_CAM_" + cid)
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cps = cc.get_editor_property("post_process_settings")
    for k, v in props.items():
        cps.set_editor_property("override_" + k, True)
        cps.set_editor_property(k, conv(v))
    cc.set_editor_property("post_process_settings", cps)
    cc.set_editor_property("post_process_blend_weight", 1.0)
    unreal.log(f"SI_PP camara {cid} {props}")
unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"])
unreal.log(f"SI_PP {CFG['valores']}")
