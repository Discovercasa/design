"""A photo of a real DiscoverCasa product becomes its texture in the visit and AR models (Step Inside Phase 3, task 156).

    python step-inside/ferramentas/materiais/foto.py <foto.jpg> --produto "Douglas marron" --largura-m 1.2
        [--altura-m 0.8] [--recorte 0.1 0.2 0.9 0.8] [--relevo 2] [--rotacao-uv 90]

- The photo stays on this PC: the maps go to _trabalho/step-inside/texturas/fotos/<nome>/ (git-ignored), and only the
  reference (size in metres, date, use) goes into the builder's mapping (mapeamentos/discovercasa.json): the common
  catalogue is not touched, so other builders keep the free textures.
- --largura-m / --altura-m: the real size of the photographed area (measure it, or count boards: 6 Tremolo boards =
  6 × 0,135 m). Without --altura-m the crop's aspect gives it.
- --recorte x0 y0 x1 y1: fractions of the photo (origin top-left) to keep, e.g. only the flat wall without the window.

How to photograph (so the texture looks real): straight on, the phone parallel to the surface; overcast light or full
shade (no sun patches); an area of about 1–1,5 m with nothing in front; full resolution, no filters.
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BOB = AQUI.parents[2]
sys.path.insert(0, str(AQUI))
import materiais  # noqa: E402
# BOB's ferramentas/comum.py by path: step-inside/ferramentas/fontes has a comum.py of its own
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("bob_comum", BOB / "ferramentas" / "comum.py")
comum = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comum)
correr_blender = comum.correr_blender


def chave(nome):
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "produto"


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Foto de um produto real -> textura (Color, NormalGL, Roughness)")
    ap.add_argument("foto")
    ap.add_argument("--produto", required=True, help="nome do produto no mapeamento (ex.: «Douglas marron»)")
    ap.add_argument("--largura-m", type=float, required=True)
    ap.add_argument("--altura-m", type=float)
    ap.add_argument("--recorte", type=float, nargs=4, default=[0, 0, 1, 1], metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--relevo", type=float, default=2.0, help="força do relevo (normal); 0 = liso")
    ap.add_argument("--rotacao-uv", type=float)
    ap.add_argument("--lado-max", type=int, default=2048)
    ap.add_argument("--construtor", default="discovercasa")
    ap.add_argument("--mapeamento", help="outro ficheiro de mapeamento (testes)")
    ap.add_argument("--saida", help="outra pasta para as imagens (testes)")
    a = ap.parse_args(argv)

    foto = Path(a.foto).resolve()
    if not foto.exists():
        raise SystemExit(f"A foto não existe: {foto}")
    cat, mp = materiais.ler(a.construtor)
    caminho_mp = Path(a.mapeamento) if a.mapeamento else BOB / "step-inside" / "materiais" / "mapeamentos" / f"{a.construtor}.json"
    if a.mapeamento:
        mp = json.loads(caminho_mp.read_text(encoding="utf-8"))
    if a.produto not in mp["materiais"]:
        raise SystemExit(f"«{a.produto}» não está no mapeamento. Produtos: {', '.join(sorted(mp['materiais']))}")
    x0, y0, x1, y1 = a.recorte
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise SystemExit("--recorte: frações entre 0 e 1, x0 < x1 e y0 < y1")

    e = mp["materiais"][a.produto]
    tab = materiais.resolver(cat, mp)
    rug = tab[a.produto]["pbr"].get("roughness", 0.7)
    nome = chave(a.produto)
    saida = Path(a.saida) if a.saida else BOB / "_trabalho" / "step-inside" / "texturas" / "fotos" / nome
    saida.mkdir(parents=True, exist_ok=True)
    # the real aspect of the area: given, or the crop's (read by Blender from the photo's own size)
    prop = a.largura_m / a.altura_m if a.altura_m else 0.0   # 0: Blender keeps the crop's aspect
    rc, out = correr_blender(AQUI / "blender_foto.py", [foto, saida, nome, prop, x0, y0, x1, y1, a.relevo, rug, a.lado_max],
                             factory=True)
    m = re.search(r"FOTO OK (\d+)x(\d+)", out)
    if rc != 0 or not m:
        raise SystemExit("O Blender falhou:\n" + out[-2000:])
    w, h = int(m.group(1)), int(m.group(2))
    altura = a.altura_m or round(a.largura_m * h / w, 4)

    tx = {"tile_m": [a.largura_m, altura], "mapas": ["base_color", "normal", "roughness"], "uso": "cor",
          "fonte": {"biblioteca": "foto", "asset": nome, "resolucao": f"{w}x{h}", "licenca": f"fotografia própria ({a.construtor})",
                    "fotografado": date.fromtimestamp(foto.stat().st_mtime).isoformat(), "convertido": date.today().isoformat(),
                    "pasta_local": saida.relative_to(BOB).as_posix() + "/" if saida.is_relative_to(BOB) else str(saida)},
          "nota": "textura do produto real, a partir de uma foto (step-inside/ferramentas/materiais/foto.py)"}
    rot = a.rotacao_uv if a.rotacao_uv is not None else ((tab[a.produto].get("textura") or {}).get("rotacao_uv"))
    if rot:
        tx["rotacao_uv"] = rot
    e["textura"] = tx
    caminho_mp.write_text(json.dumps(mp, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"«{a.produto}»: textura da foto {foto.name} ({w}×{h} px = {a.largura_m} × {altura} m) em {saida}")
    print("A seguir: refazer o modelo de visita e o AR da obra (step-inside/ferramentas/visita, ferramentas/ar).")


if __name__ == "__main__":
    main()
