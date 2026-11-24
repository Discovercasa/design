@echo off
rem Step Inside (Phase 4): rebuilds the test level from the GLB, in order (each step a commandlet, settings in the
rem .json next to each script): import -> material corrections (glTF instances) -> light, sky, ground, hidden layers
rem -> master material instances -> chosen post-process. Then render_gui.cmd (stills) or fps_jogo.cmd (frame times).
setlocal
set "S=%~dp0"
for %%P in (importar ajustes_materiais iluminacao material_mestre pos_processo) do (
  echo == %%P
  call "%S%ue_cmd.cmd" -run=pythonscript -script=%S%%%P.py -unattended -nop4 -nosplash -NullRHI >nul 2>&1
)
echo == fim
