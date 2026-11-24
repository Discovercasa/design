@echo off
rem Step Inside (Phase 8): Unreal 5.8 commandlet run (no window) on the VR project, caches on D:.
set "UE-LocalDataCachePath=D:\BOB-posto\unreal\DDC\Local"
"D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "D:\BOB-posto\unreal\StepInsideVR\StepInsideVR.uproject" %*
