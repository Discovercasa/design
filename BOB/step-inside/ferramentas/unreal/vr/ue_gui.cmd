@echo off
rem Step Inside (Phase 8): Unreal 5.8 editor or -game on the VR project (from the logged-in desktop), caches on D:.
set "UE-LocalDataCachePath=D:\BOB-posto\unreal\DDC\Local"
"D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "D:\BOB-posto\unreal\StepInsideVR\StepInsideVR.uproject" %*
