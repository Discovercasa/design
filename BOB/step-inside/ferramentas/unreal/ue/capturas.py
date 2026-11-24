"""Runs INSIDE the Unreal 5.8 editor with the GPU (from the logged-in desktop; the editor opens the test level):
images of every SI_CAM_* camera and the frame time at each view (Step Inside Phase 4, first GPU test).

    capturas_gui.cmd   (= ue_gui.cmd -ExecCmds="py D:/BOB-posto/step-inside/unreal/capturas.py"; NOT
                        -ExecutePythonScript, which closes the editor as soon as the script returns)

Reads capturas.json next to this script: {"pasta": output folder, "res": [w, h], "espera_s": warm-up seconds,
"amostra_frames": frames measured per view}. Steps, one per editor tick (nothing blocks the editor):
1. viewport in real time and game view; warm-up: passes over every camera, each time waiting for all in-flight
   compilation (shaders, meshes, distance fields), until a whole pass waits < 2 s and espera_s has gone by;
2. per camera: the viewport takes the camera's place, frames settle, the frame times are recorded (median, p90 ->
   FPS), then a high-resolution screenshot through that camera;
3. writes capturas_resumo.json and closes the editor; the images land in the project's Saved/Screenshots/WindowsEditor/.
The frame time is the editor's (the whole window draws, viewport at its own size): a reference only; the real figure
comes from a -game run at 1920 x 1080 with the CSV profiler.
"""
import json
import os
import statistics
import time

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(AQUI, "capturas.json"), encoding="utf-8") as f:
    CFG = json.load(f)
PASTA = CFG["pasta"]
os.makedirs(PASTA, exist_ok=True)
W, H = CFG.get("res", [1920, 1080])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cams = sorted((a for a in eas.get_all_level_actors() if a.get_actor_label().startswith("SI_CAM_")),
              key=lambda a: a.get_actor_label())
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
estado = {"fase": "aquecer", "t0": time.time(), "i": 0, "frames": [], "espera": 0, "res": []}
# started by a scheduled task the editor is not the foreground window: without this it is held at 8 FPS
# ("Use Less CPU when in Background"); the project's Config/DefaultEditorSettings.ini says the same
try:
    unreal.get_default_object(unreal.EditorPerformanceSettings).set_editor_property(
        "throttle_cpu_when_not_foreground", False)
except Exception as ex:
    unreal.log_warning(f"SI_CAP throttle: {ex}")
les.editor_set_game_view(True)
les.editor_set_viewport_realtime(True)
for cmd in ("t.MaxFPS 0", "r.VSync 0"):
    unreal.SystemLibrary.execute_console_command(None, cmd)
les.pilot_level_actor(cams[0])  # the viewport looks through the camera (its position, lens and aspect)


def fps(ft):
    med = statistics.median(ft)
    p90 = sorted(ft)[int(0.9 * (len(ft) - 1))]
    return {"frames": len(ft), "ms_mediana": round(med * 1000, 1), "ms_p90": round(p90 * 1000, 1),
            "fps_mediana": round(1 / med, 1), "fps_p10": round(1 / p90, 1)}


def tique(dt):
    e = estado
    agora = time.time()
    if e["fase"] == "aquecer":
        # passes over every camera: at each one the viewport draws for 3 s (the materials in sight ask for their
        # shaders), then the editor waits for every in-flight compilation (shaders, meshes, distance fields).
        # Done when a whole pass compiled nothing (< 2 s of waiting) and espera_s has gone by.
        e["espera"] += dt
        if e["espera"] < 3:
            return
        c0 = time.time()
        unreal.AutomationUtilsBlueprintLibrary.finish_all_asset_compilation()
        e["compilar_s"] = e.get("compilar_s", 0) + time.time() - c0
        e["k"] = e.get("k", 0) + 1
        if e["k"] % len(cams) == 0:
            passagem = e["compilar_s"]
            unreal.log(f"SI_CAP passagem {e['k'] // len(cams)}: espera de compilacao {passagem:.1f} s")
            e["compilar_s"] = 0
            if (passagem < 2 and agora - e["t0"] > CFG.get("espera_s", 240)) or agora - e["t0"] > 1800:
                e["aquecer_s"] = round(time.time() - e["t0"])
                unreal.log(f"SI_CAP aquecido em {e['aquecer_s']} s")
                e["fase"], e["espera"] = "posicionar", 0
                return
        les.pilot_level_actor(cams[e["k"] % len(cams)])
        e["espera"] = 0
        return
    if e["i"] >= len(cams):
        if e["fase"] != "fim":
            e["fase"] = "fim"
            json.dump({"motor": unreal.SystemLibrary.get_engine_version(), "res_captura": [W, H],
                       "aquecer_s": e.get("aquecer_s"), "vistas": e["res"]},
                      open(os.path.join(PASTA, "capturas_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False,
                      indent=1)
            les.eject_pilot_level_actor()
            unreal.log("SI_CAP FEITO")
            unreal.SystemLibrary.quit_editor()
        return
    cam = cams[e["i"]]
    nome = cam.get_actor_label()[len("SI_CAM_"):]
    if e["fase"] == "posicionar":
        les.pilot_level_actor(cam)
        e["fase"], e["espera"], e["frames"] = "assentar", 0, []
    elif e["fase"] == "assentar":  # Lumen and auto exposure settle at the new view
        e["espera"] += dt
        if e["espera"] > 8:
            e["fase"] = "medir"
    elif e["fase"] == "medir":
        e["frames"].append(dt)
        if len(e["frames"]) >= CFG.get("amostra_frames", 300):
            r = fps(e["frames"])
            r["vista"] = nome
            r["imagem"] = f"ue_{nome}.png"
            e["res"].append(r)
            unreal.log(f"SI_CAP {nome} {r}")
            # the editor's HighResShot draws the active viewport (piloting the camera) at W x H; take_high_res_screenshot
            # only works in a game viewport. The file goes to Saved/Screenshots/WindowsEditor/ (copied out at the end).
            unreal.SystemLibrary.execute_console_command(ues.get_editor_world(),
                                                         f"HighResShot {W}x{H} filename=ue_{nome}")
            e["fase"], e["espera"] = "foto", 0
    elif e["fase"] == "foto":
        e["espera"] += dt
        if e["espera"] > 4:
            e["i"] += 1
            e["fase"] = "posicionar"


estado["handle"] = unreal.register_slate_post_tick_callback(tique)
unreal.log(f"SI_CAP inicio: {len(cams)} camaras")
