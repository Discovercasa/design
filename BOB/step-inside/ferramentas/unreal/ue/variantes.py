"""Runs INSIDE Unreal 5.8 (commandlet): look-development variants of one view (Step Inside Phase 4, task 69).

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal/variantes.py -unattended -nop4 -NullRHI

Reads variantes.json next to this script: {"nivel", "base": "<camera id>", "variantes": {"<id>": {post-process
property: value, ...}}}. For each variant makes the camera SI_CAM_<base>_<id> (a copy of SI_CAM_<base>, same place and
lens) whose own post-process overrides the level's: white balance, exposure, reflection method… Then render_mrq.py
renders them side by side (its "camaras" list) and the look is chosen from the images, not guessed. Values that name
an enum are given as "Enum.VALUE" (e.g. "AutoExposureMethod.AEM_MANUAL"). Old variant cameras are removed first.
"""
import json
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "variantes.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mundo = unreal.EditorLoadingAndSavingUtils.load_map(CFG["nivel"])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
base = None
for a in eas.get_all_level_actors():
    rot = a.get_actor_label()
    if rot == "SI_CAM_" + CFG["base"]:
        base = a
    elif rot.startswith("SI_CAM_" + CFG["base"] + "_"):
        eas.destroy_actor(a)
fov = base.get_component_by_class(unreal.CameraComponent).get_editor_property("field_of_view")
for vid, props in CFG["variantes"].items():
    cam = eas.spawn_actor_from_class(unreal.CameraActor, base.get_actor_location(), base.get_actor_rotation())
    cam.set_actor_label(f"SI_CAM_{CFG['base']}_{vid}")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", fov)
    cc.set_editor_property("constrain_aspect_ratio", False)
    ps = cc.get_editor_property("post_process_settings")
    for k, v in props.items():
        if isinstance(v, str) and "." in v:
            en, val = v.split(".", 1)
            v = getattr(getattr(unreal, en), val)
        elif isinstance(v, int) and not isinstance(v, bool):
            v = float(v)
        ps.set_editor_property("override_" + k, True)
        ps.set_editor_property(k, v)
    cc.set_editor_property("post_process_settings", ps)
    cc.set_editor_property("post_process_blend_weight", 1.0)
    unreal.log(f"SI_VAR {vid} {props}")
unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"])
