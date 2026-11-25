@echo off
rem Step Inside (Phase 8): the VR tour. Opens the baked visit level straight in the headset (OpenXR, the runtime the
rem headset's PC software made active), from the logged-in desktop (a one-off scheduled task started over SSH).
rem The frame times of the first 6000 frames go to the CSV profiler (%LOCALAPPDATA%/UnrealEngine/5.8/Saved/Profiling/CSV/).
rem Controls: those of Unreal's VR template (BP_XRPawn): thumbstick to aim and release to teleport, snap turn, menu.
rem Optional: iniciar_vr.cmd <pixel density> <MSAA samples>. Defaults 0.78 and 4: on the RTX 2060 (emulated stereo,
rem 2026-11-25) 0.78 of a Quest 2 eye pair with MSAA 4x took 9.1 ms of GPU (102 FPS: room for 90 Hz and the Link
rem encoder); the full density took 13.2 ms (72 FPS: only 72 Hz, with reprojection).
setlocal
set "PD=%~1"
if "%PD%"=="" set "PD=0.78"
set "AA=%~2"
if "%AA%"=="" set "AA=4"
call "%~dp0ue_gui.cmd" /Game/Visita/TV_VR -game -vr -nosplash -ExecCmds="vr.PixelDensity %PD%,r.MSAACount %AA%" -csvCaptureFrames=6000 -csvGpuStats
