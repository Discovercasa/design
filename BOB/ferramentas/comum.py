"""Shared helpers: repo paths, scratch folder, Blender / PowerShell discovery. Standard library only."""
import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TRABALHO = REPO / "_trabalho"  # git-ignored scratch folder for caches, renders, temp files


def pasta_trabalho(*partes):
    p = TRABALHO.joinpath(*partes)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _versao(caminho):
    m = re.search(r"Blender[ _-]?(\d+)\.(\d+)", str(caminho), re.I)
    return (int(m.group(1)), int(m.group(2))) if m else None


def encontrar_blender(minimo=(4, 4)):
    """Return the Blender executable to use.

    Order: env BLENDER_EXE, then installed versions. Prefers the LOWEST version >= `minimo`
    so that saved .blend files open on as many devices as possible (newer Blender opens older files).
    """
    env = os.environ.get("BLENDER_EXE")
    if env and Path(env).exists():
        return env
    cands = []
    if sys.platform == "win32":
        for base in {os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramW6432", ""),
                     os.environ.get("ProgramFiles(x86)", "")}:
            if base:
                cands += glob.glob(os.path.join(base, "Blender Foundation", "Blender*", "blender.exe"))
                cands += glob.glob(os.path.join(base, "Steam", "steamapps", "common", "Blender", "blender.exe"))
    elif sys.platform == "darwin":
        cands += glob.glob("/Applications/Blender*.app/Contents/MacOS/Blender")
    w = shutil.which("blender")
    if w:
        cands.append(w)
    conhecidas = [(v, c) for c in cands if (v := _versao(c))]
    desconhecidas = [c for c in cands if not _versao(c)]
    ok = sorted([vc for vc in conhecidas if vc[0] >= minimo])
    if ok:
        return ok[0][1]
    if conhecidas:
        return sorted(conhecidas)[-1][1]
    return desconhecidas[0] if desconhecidas else None


def correr_blender(script, args=(), blend=None, factory=False, blender=None):
    """Run a Python script inside Blender in background mode. Returns (returncode, output)."""
    exe = blender or encontrar_blender()
    if not exe:
        raise SystemExit("Blender not found. Install Blender >= 4.4 or set the BLENDER_EXE environment variable.")
    cmd = [exe, "--background"]
    if factory:
        cmd.append("--factory-startup")
    if blend:
        cmd.append(str(blend))
    cmd += ["--python", str(script), "--", *[str(a) for a in args]]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def powershell():
    """Windows PowerShell (needed for WPF rendering of DWFx sheets)."""
    if sys.platform != "win32":
        return None
    return shutil.which("powershell") or r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
