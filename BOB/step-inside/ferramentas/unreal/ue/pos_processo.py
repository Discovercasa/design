"""Runs INSIDE Unreal 5.8 (commandlet): sets the look chosen from the variants on the level's own post-process volume
(SI_PosProcesso, made by iluminacao.py) — Step Inside Phase 4, task 69.

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal/pos_processo.py -unattended -nop4 -NullRHI

Reads pos_processo.json next to this script: {"nivel", "valores": {post-process property: value},
"camaras": {"<id>": {property: value}}} (enums as "Enum.VALUE", as in variantes.py). Only the given properties change;
"camaras" overrides on SI_CAM_<id> itself (e.g. the outside view needs less exposure than the rooms).
VR (one level walked inside and out): "interior": {"valores": {...}, "margem_cm", "transicao_cm"} makes the bounded
volume SI_PosProcesso_Interior over the house (the Lightmass importance volume less its margin) that wins over the
level's look indoors, blending over "transicao_cm" at the walls — the rooms get their own exposure, the garden keeps its.
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
INT = CFG.get("interior")
caixa = None
if INT:  # VR: one level, inside and outside; the rooms need more exposure than the garden (the eye adapts)
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == "SI_PosProcesso_Interior":
            eas.destroy_actor(a)
    caixa = next((a for a in eas.get_all_level_actors() if a.get_actor_label() == INT.get("volume", "SI_VR_Lightmass")), None)
    if caixa is None:
        unreal.log_error("SI_PP sem o volume da casa: correr vr_preparar.py antes")
if caixa is not None:
    o, e = caixa.get_actor_bounds(False)
    m = float(INT.get("margem_cm", 300))  # the Lightmass volume is the house box plus 300 cm
    v = eas.spawn_actor_from_class(unreal.PostProcessVolume, o)  # a 200 cm cube: scale it to the house
    v.set_actor_label("SI_PosProcesso_Interior")
    v.set_actor_scale3d(unreal.Vector(max(e.x - m, 50) / 100, max(e.y - m, 50) / 100, max(e.z, 50) / 100))
    v.set_editor_property("unbound", False)
    v.set_editor_property("priority", 1.0)
    v.set_editor_property("blend_radius", float(INT.get("transicao_cm", 150)))
    vps = v.get_editor_property("settings")
    for k, val in INT["valores"].items():
        vps.set_editor_property("override_" + k, True)
        vps.set_editor_property(k, conv(val))
    v.set_editor_property("settings", vps)
    unreal.log(f"SI_PP interior {[round(x) for x in (o.x, o.y, o.z)]} meia-caixa {[round(x) for x in (e.x - m, e.y - m, e.z)]} {INT['valores']}")
unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"])
unreal.log(f"SI_PP {CFG['valores']}")
