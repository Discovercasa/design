"""Restore Claude Code's memory (and optionally the old conversations) on a new device or account.

    python migracao/restaurar_memoria.py
    python migracao/restaurar_memoria.py --pasta "OASIUM=D:\\Projetos\\OASIUM"
    python migracao/restaurar_memoria.py --conversas "D:\\backup\\conversas-claude-2026-10-13.zip"

Claude Code keeps its memory per project folder in ~/.claude/projects/<key>/memory, where <key> is the
folder's full path with every character that is not a letter or digit replaced by "-". This copies
migracao/memoria/<old key>/ to the key of the same project folder on THIS machine (the BOB repo is found
automatically; the other projects at their old Desktop paths or wherever --pasta says). Nothing is
deleted; a destination file newer than the copy is kept. Standard library only.
"""
import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
# old key -> (name, original folder; None = this repository)
PROJETOS = {
    "D--DISCOVERCASA-DiscoverCasa-Vasquinho--Conte-do-BOB-Claude": ("BOB Claude", None),
    "C--Users-DiscoverCasa1-Desktop-OASIUM": ("OASIUM", r"C:\Users\DiscoverCasa1\Desktop\OASIUM"),
    "C--Users-DiscoverCasa1-Desktop-DiscoverCasa-site": ("DiscoverCasa site", r"C:\Users\DiscoverCasa1\Desktop\DiscoverCasa site"),
    "C--Users-DiscoverCasa1-Desktop-Sobral-updated": ("Sobral updated", r"C:\Users\DiscoverCasa1\Desktop\Sobral updated"),
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def chave(pasta):
    return re.sub(r"[^A-Za-z0-9]", "-", str(Path(pasta).resolve()))


def copiar(origem, alvo):
    if alvo.exists() and alvo.stat().st_mtime >= origem.stat().st_mtime:
        return False
    alvo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, alvo)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pasta", action="append", default=[], metavar="NOME=CAMINHO",
                    help="where a project lives on this machine (names: " + ", ".join(n for n, _ in PROJETOS.values()) + ")")
    ap.add_argument("--conversas", metavar="ZIP", help="also restore the old conversations from the backup zip")
    a = ap.parse_args()
    outras = dict(x.split("=", 1) for x in a.pasta)
    base = Path.home() / ".claude" / "projects"
    novas = {}
    for velha, (nome, original) in PROJETOS.items():
        pasta = outras.get(nome) or (str(REPO) if original is None else original)
        if not Path(pasta).is_dir():
            print(f"- {nome}: pasta não encontrada ({pasta}) — use --pasta \"{nome}=CAMINHO\"")
            continue
        novas[velha] = chave(pasta)
        n = sum(copiar(f, base / novas[velha] / "memory" / f.name) for f in (AQUI / "memoria" / velha).glob("*.md"))
        print(f"+ {nome}: memória, {n} ficheiro(s) copiados -> {base / novas[velha] / 'memory'}")
    if a.conversas:
        with zipfile.ZipFile(a.conversas) as z:
            n = 0
            for info in z.infolist():
                velha, _, resto = info.filename.partition("/")
                if info.is_dir() or velha not in novas or not resto:
                    continue
                alvo = base / novas[velha] / resto
                if not alvo.exists():
                    alvo.parent.mkdir(parents=True, exist_ok=True)
                    alvo.write_bytes(z.read(info))
                    n += 1
            print(f"+ conversas: {n} ficheiro(s) repostos")


if __name__ == "__main__":
    main()
