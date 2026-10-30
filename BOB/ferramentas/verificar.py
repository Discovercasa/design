"""Check that this device can run the DiscoverCasa tools:  python ferramentas/verificar.py"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ferramentas.comum import REPO, encontrar_blender, pasta_trabalho, powershell  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
ok = True


def linha(estado, texto):
    global ok
    ok &= estado is not False
    print({True: "[ok]  ", False: "[FALTA]", None: "[info]"}[estado], texto)


linha(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]} (need >= 3.10, standard library only)")
exe = encontrar_blender()
if exe:
    try:
        v = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=120).stdout.splitlines()[0]
    except Exception as e:  # noqa: BLE001
        v = f"(could not run: {e})"
    linha(True, f"Blender: {exe}  {v}")
else:
    linha(False, "Blender >= 4.4 not found (install it or set BLENDER_EXE)")
ps = powershell()
linha(True if ps else None, f"PowerShell/WPF for DWFx images: {ps or 'not available (non-Windows) - text/geometry tools still work'}")
try:
    qp = subprocess.run(["git", "-C", str(REPO), "config", "core.quotepath"], capture_output=True, text=True).stdout.strip()
    linha(True if qp == "false" else None,
          "git core.quotepath=false" if qp == "false" else "tip: git config core.quotepath false  (shows 'Construção' properly)")
except FileNotFoundError:
    linha(False, "git not installed")
t = pasta_trabalho("teste")
(t / "ok.txt").write_text("ok", encoding="utf-8")
linha(True, f"scratch folder writable: {t.parent}")
dw = sorted(REPO.glob("Construção */desenhos/*.dwfx"))
if dw:
    from ferramentas.dwfx.leitor import Dwfx
    try:
        info = Dwfx(dw[0]).info()
        linha(True, f"DWFx read test: {dw[0].name} -> {len(info)} sheet(s)")
    except Exception as e:  # noqa: BLE001
        linha(False, f"DWFx read test failed on {dw[0].name}: {e}")
print("\nALL GOOD" if ok else "\nSomething is missing (see [FALTA] lines).")
