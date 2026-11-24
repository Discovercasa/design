@echo off
rem Step Inside (Phase 8): rebuilds the VR level from the GLB (settings in the .json next to each script, folder
rem unreal-vr\): import -> material corrections -> light (static) -> master material -> post-process -> VR prep ->
rem light bake (Lightmass) and navigation mesh. Then iniciar_vr.cmd (headset) or render_gui.cmd / fps_vr.cmd.
setlocal
set "S=%~dp0"
for %%P in (importar ajustes_materiais iluminacao material_mestre pos_processo vr_preparar) do (
  echo == %%P
  call "%S%ue_cmd.cmd" -run=pythonscript -script=%S%%%P.py -unattended -nop4 -nosplash -NullRHI >nul 2>&1
)
echo == luz cozida e navegacao
call "%S%ue_cmd.cmd" -run=ResavePackages -BuildLighting -BuildNavigationData -Quality=Production -Map=/Game/Visita/TV_VR -AllowCommandletRendering -ProjectOnly -unattended -nop4 -nosplash > "%S%cozer.log" 2>&1
echo == fim
