@echo off
rem Step Inside (Phase 4): Unreal 5.8 editor or -game on the home station (run from the logged-in desktop, e.g. by a
rem scheduled task started over SSH), caches on D:.
set "UE-LocalDataCachePath=D:\BOB-posto\unreal\DDC\Local"
"D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "D:\BOB-posto\unreal\StepInside\StepInside.uproject" %*
