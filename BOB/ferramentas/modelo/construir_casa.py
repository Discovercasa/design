"""One command: DWFx -> geometry JSON -> [DiscoverCasa structure] -> build-up layers -> Blender model
(.blend + .glb) -> checks -> quantities -> previews.

    python ferramentas/modelo/construir_casa.py "<project>/modelos/<type>/config.json"
        [--sem-extrair]   reuse the existing geometry JSON (only rebuild the Blender file)
        [--sem-previews]  skip preview renders
        [--blender PATH]  Blender executable (default: env BLENDER_EXE or lowest installed version >= 4.4)

Outputs next to config.json (committed): <saida.blend>, <saida.glb> (structure), <saida.glb_completa>
(complete house), <saida.geometria>, quantidades.csv. Layers JSON and previews go to
_trabalho/modelos/<model folder>/ and _trabalho/renders/<model folder>/ (git-ignored).
Set "camadas": false in config.json to build the timber structure only. With "estrutura": {"sistema":
"discovercasa"} the drawings' layout is re-framed with DiscoverCasa's sections, flat upper ceiling and
purlin roof (estrutura_dc.py -> _trabalho/modelos/<model folder>/geometria_dc.json).
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.comum import correr_blender, encontrar_blender, pasta_trabalho  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent


def linhas(out, *prefixos):
    return "\n".join(l for l in out.splitlines() if l.startswith(prefixos))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--sem-extrair", action="store_true")
    ap.add_argument("--sem-previews", action="store_true")
    ap.add_argument("--blender")
    a = ap.parse_args()
    cfg_path = Path(a.config).resolve()
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    base = cfg_path.parent
    geo = base / cfg["saida"]["geometria"]
    blend = base / cfg["saida"]["blend"]
    glb = base / cfg["saida"]["glb"] if cfg["saida"].get("glb") else None
    glb2 = base / cfg["saida"]["glb_completa"] if cfg["saida"].get("glb_completa") else None
    exe = a.blender or encontrar_blender()
    print(f"Blender: {exe}")

    if cfg.get("planta"):  # house from an architecture plan (planta_arquitetura.py -> casa_planta.py)
        geo = pasta_trabalho("modelos", base.name) / "geometria_dc.json"
        r = subprocess.run([sys.executable, str(AQUI / "casa_planta.py"), str(cfg_path), "--saida", str(geo)])
        if r.returncode:
            raise SystemExit("builder from the plan (casa_planta.py) failed")
    elif not a.sem_extrair:
        r = subprocess.run([sys.executable, str(AQUI / "extrair_casa.py"), str(cfg_path)])
        if r.returncode:
            raise SystemExit("extraction failed")

    if not cfg.get("planta") and (cfg.get("estrutura") or {}).get("sistema") == "discovercasa":
        geo = pasta_trabalho("modelos", base.name) / "geometria_dc.json"
        r = subprocess.run([sys.executable, str(AQUI / "estrutura_dc.py"), str(cfg_path), "--saida", str(geo)])
        if r.returncode:
            raise SystemExit("DiscoverCasa structure (estrutura_dc.py) failed")

    camadas = ""
    if cfg.get("camadas", {}) is not False:
        camadas = pasta_trabalho("modelos", base.name) / "camadas.json"
        r = subprocess.run([sys.executable, str(AQUI / "camadas.py"), str(cfg_path), "--saida", str(camadas),
                            "--geometria", str(geo)])
        if r.returncode:
            raise SystemExit("layers (camadas.py) failed")

    # pass paths through an ASCII temp file (non-ASCII folder names are safe inside JSON)
    run = {"geometria": str(geo), "camadas": str(camadas), "blend": str(blend), "glb": str(glb) if glb else "",
           "glb_completa": str(glb2) if glb2 else ""}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump(run, fh, ensure_ascii=False)
        run_path = fh.name
    code, out = correr_blender(AQUI / "blender" / "build_casa.py", [run_path], factory=True, blender=exe)
    print(linhas(out, "BUILD_OK", "Error", "Traceback") or out[-3000:])
    if code or "BUILD_OK" not in out:
        raise SystemExit("Blender build failed")
    Path(str(blend) + "1").unlink(missing_ok=True)  # Blender's automatic backup (.blend1)

    code, out = correr_blender(AQUI / "blender" / "validar.py", [geo, camadas or "-"], blend=blend, blender=exe)
    print(linhas(out, "VALIDATE") or "VALIDATE FAILED\n" + out[-2000:])  # a crash must not pass silently
    code, out = correr_blender(AQUI / "blender" / "quantidades.py", [base / "quantidades.csv"], blend=blend, blender=exe)
    print(linhas(out, "QTY"))
    if not a.sem_previews:
        pv = pasta_trabalho("renders", base.name)
        casa = cfg["casa"]
        code, out = correr_blender(AQUI / "blender" / "previews.py",
                                   [pv, casa["comprimento"], casa["profundidade"]], blend=blend, blender=exe)
        print(linhas(out, "PREVIEW_OK") or out[-2000:])
        # close-ups of every outside corner and of the ceiling (check before handing the model over)
        pm = pv / "pormenores"
        pm.mkdir(parents=True, exist_ok=True)
        code, out = correr_blender(AQUI / "blender" / "pormenores.py", [geo, pm], blend=blend, blender=exe)
        print(linhas(out, "PORMENORES_OK") or out[-1500:])
    Path(run_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
