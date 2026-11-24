@echo off
rem Step Inside (Phase 8): Movie Render Queue stills of the VR level (baked light), from the logged-in desktop.
call "%~dp0ue_gui.cmd" -ExecCmds="py D:/BOB-posto/step-inside/unreal-vr/render_mrq.py" -nosplash
