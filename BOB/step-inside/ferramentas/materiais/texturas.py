"""Download the catalogue's textures to this PC (Step Inside Phase 3, hub task 156). Standard library only.

    python step-inside/ferramentas/materiais/texturas.py            # what is missing
    python step-inside/ferramentas/materiais/texturas.py --verificar  # only list what is there / missing

The images never go to Git: they live in _trabalho/step-inside/texturas/<biblioteca>/<asset>/ (git-ignored), as the
catalogue's textura.fonte.pasta_local says. Only CC0 libraries are fetched automatically (ambientCG); photos of a
builder's real products are copied there by hand. Each zip is checked against the size the library announces and
only flat image files are extracted.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

BOB = Path(__file__).resolve().parents[3]
CATALOGO = BOB / "step-inside" / "materiais" / "catalogo.json"
UA = {"User-Agent": "StepInside/0.1 (DiscoverCasa texture fetch)"}


def ambientcg(asset, pasta, resolucao="2K-JPG"):
    url = "https://ambientcg.com/api/v2/full_json?" + urllib.parse.urlencode({"id": asset, "include": "downloadData"})
    d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())
    a = d["foundAssets"][0]
    dl = [x for x in a["downloadFolders"]["default"]["downloadFiletypeCategories"]["zip"]["downloads"]
          if x["attribute"] == resolucao][0]
    zips = pasta.parent / "_zips"
    zips.mkdir(parents=True, exist_ok=True)
    z = zips / dl["fileName"]
    if not z.exists() or z.stat().st_size != dl["size"]:
        z.write_bytes(urllib.request.urlopen(urllib.request.Request(dl["downloadLink"], headers=UA), timeout=600).read())
    if z.stat().st_size != dl["size"]:
        raise RuntimeError(f"{asset}: tamanho {z.stat().st_size} ≠ {dl['size']} anunciado")
    pasta.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(z) as zf:
        for n in zf.namelist():
            nome = Path(n).name
            if n == nome and re.fullmatch(r"[A-Za-z0-9_.-]+\.(jpg|png)", nome):
                (pasta / nome).write_bytes(zf.read(n))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args()
    cat = json.loads(CATALOGO.read_text(encoding="utf-8"))
    fontes = {}
    for m in cat["materiais"]:
        f = (m.get("textura") or {}).get("fonte")
        if f:
            fontes.setdefault((f["biblioteca"], f["asset"], f["pasta_local"]), []).append(m["id"])
    falta = 0
    for (bib, asset, local), ids in sorted(fontes.items()):
        pasta = BOB / local
        ok = pasta.exists() and any(pasta.glob("*_Color.*"))
        print(f"{'ok   ' if ok else 'FALTA'} {bib}:{asset} -> {', '.join(ids)}")
        if ok or a.verificar:
            falta += not ok
            continue
        if bib != "ambientCG":
            print(f"      {bib}: copiar as imagens à mão para {local}")
            falta += 1
            continue
        ambientcg(asset, pasta)
        print("      descarregado")
    sys.exit(1 if falta else 0)


if __name__ == "__main__":
    main()
