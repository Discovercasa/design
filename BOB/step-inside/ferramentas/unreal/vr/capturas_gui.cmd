@echo off
rem Step Inside (Phase 8): quick editor captures of every SI_CAM_* of the VR level (ue/capturas.py; images in the
rem VR project's Saved/Screenshots/WindowsEditor/), from the logged-in desktop.
call "%~dp0ue_gui.cmd" -ExecCmds="py D:/BOB-posto/step-inside/unreal-vr/capturas.py" -nosplash
