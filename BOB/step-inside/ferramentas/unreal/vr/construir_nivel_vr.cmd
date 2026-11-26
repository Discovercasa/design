@echo off
rem Step Inside (Phase 8): rebuilds the VR level from the GLB (settings in the .json next to each script, folder
rem unreal-vr\): import -> material corrections -> light (static) -> master material -> our glass -> VR prep ->
rem mirrors (planar reflections) -> post-process (its interior volume follows VR prep's Lightmass volume) -> navigation
rem mesh. Then cozer_gui.cmd (light, in the editor with the GPU), then iniciar_vr.cmd / fps_vr.cmd.
setlocal
set "S=%~dp0"
for %%P in (importar ajustes_materiais iluminacao material_mestre vidros vr_preparar espelhos pos_processo) do (
  echo == %%P
  call "%S%ue_cmd.cmd" -run=pythonscript -script=%S%%%P.py -unattended -nop4 -nosplash -NullRHI >nul 2>&1
)
echo == navegacao
call "%S%ue_cmd.cmd" -run=ResavePackages -BuildNavigationData -Map=/Game/Visita/TV_VR -ProjectOnly -unattended -nop4 -nosplash > "%S%navegacao.log" 2>&1
echo == fim (a luz coze-se no editor com GPU: cozer_gui.cmd, a partir da sessao do Windows)
