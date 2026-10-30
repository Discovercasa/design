"""Render DWFx sheets to PNG (Windows only: uses WPF through PowerShell, nothing to install).

Why not the standard XPS loader: DWFx pages reference fonts that were never embedded, which makes
System.Windows.Xps fail. We instead:
  1. de-obfuscate the embedded .odttf fonts (XOR first 32 bytes with the GUID in the file name),
  2. rewrite each FixedPage as standalone XAML pointing at those fonts (missing fonts -> Arial),
  3. load the XAML with XamlReader and draw it with RenderTargetBitmap (wpf_render.ps1).
"""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.comum import pasta_trabalho, powershell  # noqa: E402
from ferramentas.dwfx.leitor import Dwfx  # noqa: E402

PS1 = Path(__file__).with_name("wpf_render.ps1")
ARIAL = "file:///C:/Windows/Fonts/arial.ttf"


def _deobfuscate(data, guid):
    g = guid.replace("-", "")
    key = bytes(int(g[i:i + 2], 16) for i in range(30, -2, -2))
    return bytes(data[i] ^ key[i % 16] for i in range(32)) + data[32:]


def preparar(dwfx_path):
    """Write fonts + one XAML per sheet into a cache folder. Returns list of XAML paths (sheet 1..n)."""
    p = Path(dwfx_path)
    st = p.stat()
    tag = hashlib.sha1(f"{p.resolve()}|{st.st_size}|{st.st_mtime_ns}".encode()).hexdigest()[:10]
    cache = pasta_trabalho("dwfx", f"{re.sub(r'[^A-Za-z0-9]+', '_', p.stem)[:40]}_{tag}")
    fonts = cache / "fonts"
    fonts.mkdir(exist_ok=True)
    d = Dwfx(p)
    xamls = [cache / f"folha{k}.xaml" for k in range(1, len(d.pages) + 1)]
    if all(x.exists() for x in xamls):
        return xamls
    for n in d.names:
        if n.endswith(".odttf"):
            guid = Path(n).stem
            (fonts / f"{guid}.ttf").write_bytes(_deobfuscate(d.zip.read(n), guid))
    base = "file:///" + str(fonts.resolve()).replace("\\", "/")
    for k, page in enumerate(d.pages):
        xml = d.zip.read(page).decode("utf-8")

        def font(m):
            guid = m.group(1)
            return f'FontUri="{base}/{guid}.ttf"' if (fonts / f"{guid}.ttf").exists() else f'FontUri="{ARIAL}"'

        xml = re.sub(r'FontUri="(?:\./|/)?(?:[^"/]*/)*([0-9A-Fa-f-]+)\.odttf"', font, xml)  # "./x", "x" or a path
        xml = re.sub(r"<Canvas\.Resources>.*?</Canvas\.Resources>", "", xml, flags=re.S)
        xamls[k].write_text(xml, encoding="utf-8")
    return xamls


def _run_ps(args):
    ps = powershell()
    if not ps:
        raise SystemExit("Rendering DWFx sheets needs Windows (WPF). Use `dwfx.py texto` / `pecas` instead.")
    cmd = [ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(PS1), *args]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        raise SystemExit("Render failed:\n" + out)
    return out.strip()


def render_folha(dwfx_path, folha, saida, dpi=55):
    xaml = preparar(dwfx_path)[folha - 1]
    return _run_ps(["-Xaml", str(xaml), "-Out", str(saida), "-Dpi", str(dpi)])


def zoom(dwfx_path, folha, x, y, w, h, saida, px=1600):
    """Render the sheet region (x, y, w, h) in sheet millimetres, `px` pixels wide."""
    xaml = preparar(dwfx_path)[folha - 1]
    return _run_ps(["-Xaml", str(xaml), "-Out", str(saida), "-X", str(x), "-Y", str(y),
                    "-W", str(w), "-H", str(h), "-PixelWidth", str(px)])
