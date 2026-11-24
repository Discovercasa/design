"""Runs INSIDE the Unreal 5.8 editor with the GPU: still images of every SI_CAM_* camera with the Movie Render Queue
(Step Inside Phase 4, task 69). Render quality, not a viewport screenshot: engine and render warm-up frames (shaders,
Lumen history, auto exposure settle), temporal samples accumulated per image, cinematic scalability.

    render_gui.cmd   (= ue_gui.cmd -ExecCmds="py D:/BOB-posto/step-inside/unreal/render_mrq.py")

Reads render_mrq.json next to this script: {"nivel": "/Game/Visita/<Nivel>", "pasta": output folder,
"res": [w, h], "amostras": temporal samples, "aquecer": render warm-up frames, "camaras": [ids] or null (= all),
"passes_extra": optional diagnosis passes, e.g. ["Unlit", "LightingOnly", "ReflectionsOnly"],
"modo": "path" for the Path Tracer (with "amostras_pt" samples per pixel) instead of Lumen}.
1. one Level Sequence per camera (/Game/Visita/Sequencias/SEQ_<id>): one frame, a camera cut to that camera;
2. one Movie Render Queue job per sequence: deferred pass, PNG, the resolution, anti-aliasing by temporal samples,
   game overrides (cinematic quality, flush shader and asset compilation before rendering);
3. renders with the PIE executor, writes render_resumo.json and closes the editor when the queue is done.
"""
import json
import os
import time

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(AQUI, "render_mrq.json"), encoding="utf-8") as f:
    CFG = json.load(f)
os.makedirs(CFG["pasta"], exist_ok=True)
W, H = CFG.get("res", [1920, 1080])
t0 = time.time()
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
cams = sorted((a for a in eas.get_all_level_actors() if a.get_actor_label().startswith("SI_CAM_")),
              key=lambda a: a.get_actor_label())
if CFG.get("camaras"):
    cams = [c for c in cams if c.get_actor_label()[7:] in CFG["camaras"]]
ferr = unreal.AssetToolsHelpers.get_asset_tools()
PASTA_SEQ = "/Game/Visita/Sequencias"
seqs = []
for cam in cams:
    nome = cam.get_actor_label()[7:]
    caminho = f"{PASTA_SEQ}/SEQ_{nome}"
    if unreal.EditorAssetLibrary.does_asset_exist(caminho):
        unreal.EditorAssetLibrary.delete_asset(caminho)
    seq = ferr.create_asset(f"SEQ_{nome}", PASTA_SEQ, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_playback_start(0)
    seq.set_playback_end(1)
    lig = seq.add_possessable(cam)
    corte = seq.add_track(unreal.MovieSceneCameraCutTrack).add_section()
    corte.set_range(0, 1)
    corte.set_camera_binding_id(seq.get_binding_id(lig))
    unreal.EditorAssetLibrary.save_loaded_asset(seq)
    seqs.append((nome, seq))

fila_sub = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
fila = fila_sub.get_queue()
fila.delete_all_jobs()
for nome, seq in seqs:
    job = fila.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.set_editor_property("job_name", nome)
    job.set_editor_property("sequence", unreal.SoftObjectPath(seq.get_path_name()))
    job.set_editor_property("map", unreal.SoftObjectPath(CFG["nivel"] + "." + CFG["nivel"].split("/")[-1]))
    cfg = job.get_configuration()
    saida = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    saida.set_editor_property("output_directory", unreal.DirectoryPath(CFG["pasta"]))
    saida.set_editor_property("file_name_format", "ue_{job_name}{render_pass}" if CFG.get("passes_extra") else "ue_{job_name}")
    saida.set_editor_property("output_resolution", unreal.IntPoint(W, H))
    saida.set_editor_property("override_existing_output", True)
    if CFG.get("modo") == "path":
        # Path Tracer (hardware ray tracing): physically based like Cycles, no Lumen artefacts; the stills for approval
        pt = cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPass_PathTracer)
        try:
            pt.set_editor_property("reference_motion_blur", False)
        except Exception:
            pass
    else:
        cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    for passe in CFG.get("passes_extra", []):  # diagnosis: Unlit (base colour), LightingOnly, ReflectionsOnly
        cfg.find_or_add_setting_by_class(getattr(unreal, "MoviePipelineDeferredPass_" + passe))
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    aa = cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
    if CFG.get("modo") == "path":  # samples per pixel = spatial x temporal; the path tracer denoises the result
        aa.set_editor_property("spatial_sample_count", int(CFG.get("amostras_pt", 128)))
        aa.set_editor_property("temporal_sample_count", 1)
    else:
        aa.set_editor_property("spatial_sample_count", 1)
        aa.set_editor_property("temporal_sample_count", int(CFG.get("amostras", 8)))
    aa.set_editor_property("override_anti_aliasing", True)
    aa.set_editor_property("anti_aliasing_method", unreal.AntiAliasingMethod.AAM_NONE)
    aa.set_editor_property("engine_warm_up_count", 32)
    aa.set_editor_property("render_warm_up_count", int(CFG.get("aquecer", 64)))
    jogo = cfg.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting)
    jogo.set_editor_property("cinematic_quality_settings", True)
    for p in ("flush_shader_compiler", "flush_asset_compiler"):
        try:
            jogo.set_editor_property("override_b_" + p, True)
            jogo.set_editor_property(p, True)
        except Exception as ex:
            unreal.log_warning(f"SI_MRQ {p}: {ex}")
unreal.log(f"SI_MRQ fila com {len(seqs)} trabalhos: {[n for n, _ in seqs]}")


def acabou(executor, ok):
    imgs = sorted(x for x in os.listdir(CFG["pasta"]) if x.startswith("ue_") and x.endswith(".png"))
    with open(os.path.join(CFG["pasta"], "render_resumo.json"), "w", encoding="utf-8") as f:
        json.dump({"ok": bool(ok), "segundos": round(time.time() - t0), "imagens": imgs, "res": [W, H],
                   "amostras": CFG.get("amostras", 8), "aquecer": CFG.get("aquecer", 64)}, f, ensure_ascii=False,
                  indent=1)
    unreal.log(f"SI_MRQ FEITO ok={ok} {len(imgs)} imagens em {time.time() - t0:.0f} s")
    unreal.SystemLibrary.quit_editor()


EXEC = fila_sub.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)
EXEC.on_executor_finished_delegate.add_callable(acabou)
