"""Download the free CC0 models of the interiors catalogue (Poly Haven, glTF with 1K textures) to the PC only.

    python interiores/descarregar.py            # every 'polyhaven' object of interiores/catalogo.json
    python interiores/descarregar.py --ver      # only list what would be downloaded, with sizes

User 2026-11-11: «Gratuitos CC0 (Recomendado)» and «Sim, descarrega» (16 models, ≈ 30 MB). The files go to
_trabalho/interiores/polyhaven/<asset>/ (git-ignored: never in this public repo); a model already downloaded with the
same size is skipped. Licence: CC0 (public domain), source polyhaven.com, recorded in interiores/fontes.json.
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path, PurePosixPath

BOB = Path(__file__).resolve().parents[1]
CATALOGO = BOB / "interiores" / "catalogo.json"
FONTES = BOB / "interiores" / "fontes.json"
DESTINO = BOB / "_trabalho" / "interiores" / "polyhaven"
API = "https://api.polyhaven.com/files/"
AGENTE = {"User-Agent": "step-inside-interiores/0.1"}
RESOLUCAO = "1k"


def obter(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=AGENTE), timeout=60) as r:
        return r.read()


def ficheiros(asset):
    """[(relative path, url, size)] of the glTF in 1K: the .gltf, its .bin and its textures."""
    info = json.loads(obter(API + asset))
    g = info["gltf"][RESOLUCAO]["gltf"]
    out = [(PurePosixPath(g["url"]).name, g["url"], g["size"])]
    for rel, f in (g.get("include") or {}).items():
        p = PurePosixPath(rel)
        if p.is_absolute() or ".." in p.parts:
            raise ValueError(f"{asset}: caminho estranho no glTF: {rel}")
        out.append((str(p), f["url"], f["size"]))
    return out


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", action="store_true")
    a = ap.parse_args(argv)
    cat = json.loads(CATALOGO.read_text(encoding="utf-8"))
    assets = [o["origem"]["asset"] for o in cat["objetos"] if o["origem"]["tipo"] == "polyhaven"]
    fontes, total = {}, 0
    for asset in assets:
        lista = ficheiros(asset)
        tam = sum(s for _, _, s in lista)
        total += tam
        pasta = DESTINO / asset
        novos = 0
        for rel, url, s in lista:
            alvo = pasta / rel
            if alvo.exists() and alvo.stat().st_size == s:
                continue
            novos += 1
            if not a.ver:
                alvo.parent.mkdir(parents=True, exist_ok=True)
                alvo.write_bytes(obter(url))
        fontes[asset] = {"fonte": f"https://polyhaven.com/a/{asset}", "licenca": "CC0", "resolucao": RESOLUCAO,
                         "gltf": lista[0][0], "bytes": tam}
        print(f"  {asset:28s} {tam / 1e6:5.1f} MB  {len(lista)} ficheiros{'' if novos else ' (já estava)'}")
    print(f"{len(assets)} modelos, {total / 1e6:.1f} MB -> {DESTINO}")
    if not a.ver:
        FONTES.write_text(json.dumps({"_doc": "Origem e licença dos modelos descarregados por interiores/descarregar.py "
                                      "(os ficheiros ficam só no PC, em _trabalho/interiores/).", "modelos": fontes},
                                     ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
