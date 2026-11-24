@echo off
rem Step Inside (Phase 4): Movie Render Queue stills of the test level (from the logged-in desktop; see ue/render_mrq.py).
call "%~dp0ue_gui.cmd" -ExecCmds="py D:/BOB-posto/step-inside/unreal/render_mrq.py" -nosplash
