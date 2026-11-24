@echo off
rem Step Inside (Phase 4): the test level as a game, 1920 x 1080 windowed, no frame cap, CSV profiler with GPU times
rem for 3000 frames (from the logged-in desktop; camara_jogo.py picks the view). The CSV lands in
rem %LOCALAPPDATA%/UnrealEngine/5.8/Saved/Profiling/CSV/ (not the project), and the game does NOT quit by itself:
rem the caller waits for the CSV, closes the process and reads it with ler_csv.py.
call "%~dp0ue_gui.cmd" -game -windowed -ResX=1920 -ResY=1080 -nosplash -ExecCmds="t.MaxFPS 0,r.VSync 0" -csvCaptureFrames=3000 -csvGpuStats
