"""Runs INSIDE Unreal 5.8 (commandlet): the game (-game) looks through one SI_CAM_* camera of the test level.

    ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal/camara_jogo.py -unattended -nop4 -NullRHI

Reads camara_jogo.json next to this script: {"nivel": "/Game/Visita/<Nivel>", "camara": "<id>"}. Sets "Auto Activate
for Player" = Player 0 on SI_CAM_<id> and Disabled on the others, then saves the level. Used by fps_jogo.cmd to measure
the frame time of one view in a real game window (the editor's own figure is not representative).
"""
import json
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "camara_jogo.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mundo = unreal.EditorLoadingAndSavingUtils.load_map(CFG["nivel"])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n = 0
for a in eas.get_all_level_actors():
    rot = a.get_actor_label()
    if rot.startswith("SI_CAM_"):
        quer = rot == "SI_CAM_" + CFG["camara"]
        a.set_editor_property("auto_activate_for_player",
                              unreal.AutoReceiveInput.PLAYER0 if quer else unreal.AutoReceiveInput.DISABLED)
        n += quer
unreal.log(f"SI_JOGO camara {CFG['camara']} ativa: {n == 1}")
unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"])
