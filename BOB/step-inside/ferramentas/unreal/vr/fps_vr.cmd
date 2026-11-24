@echo off
rem Step Inside (Phase 8): the VR cost without a headset. Emulated stereo (both eyes side by side), internal resolution
rem 180 % of 1920 x 1080 (about a Quest 2 eye pair), no frame cap, CSV profiler with GPU times for 3000 frames.
rem The view is the one camera_jogo.py set. The CSV goes to %LOCALAPPDATA%/UnrealEngine/5.8/Saved/Profiling/CSV/ and
rem the game does not quit by itself: the caller waits for the CSV and closes it.
call "%~dp0ue_gui.cmd" /Game/Visita/TV_VR -game -emulatestereo -windowed -ResX=1920 -ResY=1080 -nosplash -ExecCmds="t.MaxFPS 0,r.VSync 0,r.ScreenPercentage 180" -csvCaptureFrames=3000 -csvGpuStats
