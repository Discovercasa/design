@echo off
rem Step Inside (Phase 8): bakes the VR level's light in the editor with the GPU (ue/cozer_gui.py), from the
rem logged-in desktop: the sky light and the reflection captures need it.
call "%~dp0ue_gui.cmd" -ExecCmds="py D:/BOB-posto/step-inside/unreal-vr/cozer_gui.py" -nosplash
