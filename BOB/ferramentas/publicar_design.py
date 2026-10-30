"""Publish BOB to the public repo Discovercasa/design (user 2026-10-30).

- BOB/                  = the committed files of the current branch (git archive), WITHOUT client drawings
                          (*.dwfx, *.pdf): they carry personal data and stay on this PC only.
- public/configurador/  = the configurator build; Cloudflare Pages publishes only public/, so the
                          configurator is the only part of BOB visible on design.discovercasa.pt, and only
                          after the Hub login (public/js/porta.js, kept in the Design repo).

Usage:  python ferramentas/publicar_design.py [--sem-push]
Needs:  git, gh logged in as DinisDiscover, Node/npm (configurator build). Clone kept in _trabalho/design/.
"""
import io, os, shutil, subprocess, sys, tarfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CLONE = RAIZ / "_trabalho" / "design"
URL = "https://github.com/Discovercasa/design.git"
CONTA = "DinisDiscover"
EXCLUIR = (".dwfx", ".pdf")
PORTA = ('  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js"></script>\n'
         '  <script src="/js/design-core.js"></script>\n'
         '  <script src="/js/porta.js"></script>')


def corre(*cmd, cwd=None, captura=False, env=None):
    r = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=captura, env=env,
                       shell=(os.name == "nt" and cmd[0] in ("npm", "npx")))
    return r.stdout.strip() if captura else None


# authenticate as the Design account without touching the gh default or this clone's credentials
CREDENCIAL = ("-c", "credential.helper=", "-c",
              f"credential.helper=!f() {{ echo username={CONTA}; echo password=$(gh auth token --user {CONTA}); }}; f")


def git_design(*args, captura=False):
    return corre("git", *CREDENCIAL, *args, cwd=CLONE, captura=captura)


def main():
    sem_push = "--sem-push" in sys.argv
    if not (CLONE / ".git").exists():
        CLONE.parent.mkdir(parents=True, exist_ok=True)
        corre("git", *CREDENCIAL, "clone", URL, str(CLONE))
    git_design("fetch", "origin")
    git_design("checkout", "-q", "main")
    git_design("reset", "-q", "--hard", "origin/main")

    # BOB/: the committed tree of the current branch, minus client drawings
    destino = CLONE / "BOB"
    shutil.rmtree(destino, ignore_errors=True)
    tar = subprocess.run(["git", "archive", "--format=tar", "HEAD"], cwd=RAIZ, check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        membros = [m for m in t.getmembers() if not m.name.lower().endswith(EXCLUIR)]
        t.extractall(destino, members=membros, filter="data")
    print(f"BOB/: {sum(m.isfile() for m in membros)} files (drawings *.dwfx/*.pdf left out)")

    # public/configurador/: the configurator, built for that path
    web = RAIZ / "configurador" / "web"
    if not (web / "node_modules").exists():
        corre("npm", "ci", cwd=web)
    saida = CLONE / "public" / "configurador"
    corre("npm", "run", "motor", cwd=web)
    corre("npx", "vite", "build", "--base=/configurador/", "--outDir", str(saida), "--emptyOutDir", cwd=web)
    # behind the Design login (user 2026-10-30): the site's own gate (public/js/porta.js) runs before the app
    pagina = saida / "index.html"
    html = pagina.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n" + PORTA, 1)
    pagina.write_text(html, encoding="utf-8")

    git_design("add", "-A")
    if not git_design("status", "--porcelain", captura=True):
        print("Nothing changed."); return
    origem = corre("git", "log", "-1", "--format=%h %s", cwd=RAIZ, captura=True)
    git_design("commit", "-q", "-m", f"BOB: sync from {origem}")
    if sem_push:
        print("Committed in _trabalho/design (not pushed)."); return
    git_design("push", "origin", "main")
    print("Pushed to Discovercasa/design (site: https://design.discovercasa.pt/configurador/).")


if __name__ == "__main__":
    main()
