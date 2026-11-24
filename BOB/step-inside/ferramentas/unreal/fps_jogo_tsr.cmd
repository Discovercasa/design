@echo off
rem Step Inside (Phase 4): like fps_jogo.cmd, with the real-time profile under test: internal resolution 67 % rebuilt
rem to 1920 x 1080 by TSR (the usual 'quality' upscaling). The Lumen quality comes from the level's post-process.
call "%~dp0ue_gui.cmd" -game -windowed -ResX=1920 -ResY=1080 -nosplash -ExecCmds="t.MaxFPS 0,r.VSync 0,r.ScreenPercentage 67" -csvCaptureFrames=3000 -csvGpuStats
