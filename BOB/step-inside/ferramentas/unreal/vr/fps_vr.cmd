@echo off
rem Step Inside (Phase 8): the VR cost without a headset. Emulated stereo (both eyes side by side), internal resolution
rem 180 % of 1920 x 1080 (about a Quest 2 eye pair), no frame cap, CSV profiler with GPU times for 3000 frames.
rem Optional: fps_vr.cmd <screen percentage> <MSAA samples>  (defaults 180 and 4) to compare settings.
rem The view is the one camera_jogo.py set. The CSV goes to %LOCALAPPDATA%/UnrealEngine/5.8/Saved/Profiling/CSV/ and
rem the game does not quit by itself: the caller waits for the CSV and closes it.
setlocal
set "SP=%~1"
if "%SP%"=="" set "SP=180"
set "AA=%~2"
if "%AA%"=="" set "AA=4"
call "%~dp0ue_gui.cmd" /Game/Visita/TV_VR -game -emulatestereo -windowed -ResX=1920 -ResY=1080 -nosplash -ExecCmds="t.MaxFPS 0,r.VSync 0,r.ScreenPercentage %SP%,r.MSAACount %AA%" -csvCaptureFrames=3000 -csvGpuStats
