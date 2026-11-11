"""Build the site parts made from BOB, in place, inside the Discovercasa/design repo (user 2026-11-05: Discovercasa/design
is the working repo for all the applications; this replaces the old publicar_design.py, which copied from the private BOB).

- public/build-your-house/ = Vite build of BOB/configurador/web (base /build-your-house/), behind the Design login
- public/gerador/          = BOB/gerador/web + the Python engine it runs in the browser + three.js (self-hosted)
- public/orcamentacao/     = BOB/orcamentacao/web + ligacoes.json (product code -> Hub material) + the Torres Vedras
                             Listagem as the example (prices are read at run time with the Design session, never stored)

Run after changing BOB/configurador/web, BOB/gerador/web or the engine (BOB/ferramentas/...), then commit and push
as usual: Cloudflare Pages publishes public/ on every push to main.

Usage:  python BOB/ferramentas/construir_site.py [--so configurador | --so gerador | --so orcamentacao]
Needs:  Node/npm (first run: npm ci in BOB/configurador/web).
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

BOB = Path(__file__).resolve().parents[1]
RAIZ = BOB.parent                      # the Discovercasa/design repo
PUBLICO = RAIZ / "public"
# the site's own login gate (public/js/porta.js), injected before the app (user 2026-10-30: "Para já atrás do login")
PORTA = ('  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js"></script>\n'
         '  <script src="/js/design-core.js"></script>\n'
         '  <script src="/js/porta.js"></script>')
# the Python the document generator runs in the browser (ferramentas/documentos/de_desenhos.py and what it imports)
MOTOR_GERADOR = ("ferramentas/__init__.py", "ferramentas/comum.py", "ferramentas/dwfx/__init__.py", "ferramentas/dwfx/leitor*.py",
                 "ferramentas/modelo/*.py", "ferramentas/modelo/sistema_construtivo.json", "ferramentas/documentos/*.py",
                 "ferramentas/configurador/*.py", "ferramentas/planta/__init__.py", "ferramentas/planta/analisar.py",
                 "ferramentas/planta/mascara.py")


def corre(*cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, shell=(os.name == "nt"))


def com_porta(pagina: Path):
    html = pagina.read_text(encoding="utf-8")
    if "/js/porta.js" not in html:
        pagina.write_text(html.replace("<head>", "<head>\n" + PORTA, 1), encoding="utf-8")


def configurador(web: Path):
    if not (web / "node_modules").exists():
        corre("npm", "ci", cwd=web)
    saida = PUBLICO / "build-your-house"
    corre("npm", "run", "motor", cwd=web)
    corre("npx", "vite", "build", "--base=/build-your-house/", "--outDir", str(saida), "--emptyOutDir", cwd=web)
    com_porta(saida / "index.html")
    print("public/build-your-house/: built")


def gerador(web: Path):
    destino = PUBLICO / "gerador"
    shutil.rmtree(destino, ignore_errors=True)
    shutil.copytree(BOB / "gerador" / "web", destino)
    lista = []
    for padrao in MOTOR_GERADOR:
        for f in sorted(BOB.glob(padrao)):
            rel = f.relative_to(BOB).as_posix()
            (destino / "motor" / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, destino / "motor" / rel)
            lista.append(rel)
    if not (web / "node_modules" / "three").exists():  # three.js: the configurator's own copy (same version)
        corre("npm", "ci", cwd=web)
    vendor = destino / "vendor"
    vendor.mkdir(exist_ok=True)
    for f in ("build/three.module.js", "build/three.core.js", "examples/jsm/controls/OrbitControls.js"):
        shutil.copy2(web / "node_modules" / "three" / f, vendor / Path(f).name)
    (destino / "motor" / "lista.json").write_text(json.dumps(lista, indent=1), encoding="utf-8")
    com_porta(destino / "index.html")
    print(f"public/gerador/: page + {len(lista)} engine files")


def orcamentacao():
    destino = PUBLICO / "orcamentacao"
    shutil.rmtree(destino, ignore_errors=True)
    shutil.copytree(BOB / "orcamentacao" / "web", destino)
    shutil.copy2(BOB / "orcamentacao" / "ligacoes.json", destino / "ligacoes.json")
    (destino / "exemplos").mkdir()
    shutil.copy2(BOB / "Construção Torres Vedras" / "documentos" / "D2503_Listagem_Material.csv", destino / "exemplos")
    com_porta(destino / "index.html")
    print("public/orcamentacao/: page + links + example")


def main():
    if not (PUBLICO / "js" / "porta.js").exists():
        sys.exit("Not inside the Discovercasa/design repo (public/js/porta.js missing).")
    so = sys.argv[sys.argv.index("--so") + 1] if "--so" in sys.argv else None
    web = BOB / "configurador" / "web"
    if so in (None, "configurador"):
        configurador(web)
    if so in (None, "gerador"):
        gerador(web)
    if so in (None, "orcamentacao"):
        orcamentacao()
    print("Done. Commit and push to main to publish (Cloudflare Pages).")


if __name__ == "__main__":
    main()
