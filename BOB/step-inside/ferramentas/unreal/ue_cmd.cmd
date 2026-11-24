@echo off
rem Step Inside (Phase 4): Unreal 5.8 commandlet run (no window) on the home station, caches on D:.
rem   ue_cmd.cmd -run=pythonscript -script="D:\BOB-posto\step-inside\unreal\x.py" -unattended ...
set "UE-LocalDataCachePath=D:\BOB-posto\unreal\DDC\Local"
"D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "D:\BOB-posto\unreal\StepInside\StepInside.uproject" %*
