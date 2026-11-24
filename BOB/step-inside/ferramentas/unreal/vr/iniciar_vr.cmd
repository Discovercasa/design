@echo off
rem Step Inside (Phase 8): the VR tour. Opens the baked visit level straight in the headset (OpenXR, the runtime the
rem headset's PC software made active), from the logged-in desktop (a one-off scheduled task started over SSH).
rem The frame times of the first 6000 frames go to the CSV profiler (%LOCALAPPDATA%/UnrealEngine/5.8/Saved/Profiling/CSV/).
rem Controls: those of Unreal's VR template (BP_XRPawn): thumbstick to aim and release to teleport, snap turn, menu.
call "%~dp0ue_gui.cmd" /Game/Visita/TV_VR -game -vr -nosplash -csvCaptureFrames=6000 -csvGpuStats
