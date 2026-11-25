"""Runs INSIDE the Unreal 5.8 editor with the GPU (VR project; the editor opens the VR level): bakes the light.

    unreal-vr\\cozer_gui.cmd   (= ue_gui.cmd -ExecCmds="py D:/BOB-posto/step-inside/unreal-vr/cozer_gui.py")

Why in the editor and not in a commandlet (2026-11-25): the sky light and the reflection captures "photograph" the
scene, which needs the GPU; baked headless (-NullRHI) they came out black — interiors lit only by the sun patch and
the lamps (dark, orange) and a white mirror. Steps, one per editor tick:
1. warm-up: wait for every in-flight compilation (shaders, meshes) until a pass compiles nothing;
2. recapture the sky light and give the renderer two ticks to photograph it (the capture runs on a later frame);
3. Lightmass at the chosen quality with the reflection captures (build_light_maps);
4. save the level and its built data, write cozer_resumo.json next to this script, close the editor.
"""
import json
import os
import time

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
try:  # cozer.json next to this script: {"qualidade": "QUALITY_PREVIEW" (checks) | "QUALITY_PRODUCTION" (final)}
    with open(os.path.join(AQUI, "cozer.json"), encoding="utf-8") as f:
        QUAL = json.load(f).get("qualidade", "QUALITY_PRODUCTION")
except OSError:
    QUAL = "QUALITY_PRODUCTION"
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
est = {"t": 0.0, "acc": 0.0, "n": 0, "t0": time.time(), "fase": "aquecer", "h": None}


def tique(dt):
    est["t"] += dt
    if est["t"] < 3:
        return
    est["t"] = 0.0
    if est["fase"] == "aquecer":
        c0 = time.time()
        unreal.AutomationUtilsBlueprintLibrary.finish_all_asset_compilation()
        w = time.time() - c0
        est["n"] += 1
        unreal.log(f"SI_COZ aquecimento {est['n']}: {w:.1f} s a compilar")
        if (w < 2 and est["n"] >= 2) or est["n"] >= 30:
            est["fase"] = "captar"
        return
    if est["fase"] == "captar":
        for a in eas.get_all_level_actors():
            if isinstance(a, unreal.SkyLight):
                a.get_component_by_class(unreal.SkyLightComponent).recapture_sky()
        est["fase"], est["espera"] = "esperar", 2
        return
    if est["fase"] == "esperar":
        est["espera"] -= 1
        if est["espera"] <= 0:
            est["fase"] = "cozer"
        return
    if est["fase"] == "cozer":
        est["fase"] = "feito"
        unreal.unregister_slate_post_tick_callback(est["h"])
        c0 = time.time()
        ok = les.build_light_maps(getattr(unreal.LightingBuildQuality, QUAL), True)
        dur = time.time() - c0
        unreal.log(f"SI_COZ build_light_maps {QUAL} ok={ok} em {dur:.0f} s")
        guardou = les.save_current_level()
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        with open(os.path.join(AQUI, "cozer_resumo.json"), "w", encoding="utf-8") as f:
            json.dump({"ok": bool(ok), "qualidade": QUAL, "cozer_s": round(dur), "total_s": round(time.time() - est["t0"]),
                       "guardou": bool(guardou)}, f, indent=1)
        unreal.log("SI_COZ FEITO")
        unreal.SystemLibrary.quit_editor()


est["h"] = unreal.register_slate_post_tick_callback(tique)
unreal.log("SI_COZ inicio")
