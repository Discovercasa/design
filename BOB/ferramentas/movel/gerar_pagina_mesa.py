"""The extending table's page: ONE self-contained HTML file (opens offline) with exactly the functions of the source
page (user 2026-11-27: «a nossa página para esta mesa deve ter exatamente as mesmas funcionalidades que a página que te
enviei tem») — 4 variants, 0–2 leaves, top and leg finishes, dimensions, exploded view, chairs, room or studio, day or
night, PT/EN, the six views and turning, full screen, plan and elevation, parts list — on our ultra-realistic scene
(blender_mesa.py: scanned veneers and marble, our chairs, the real room, the light baked in Cycles).

    python ferramentas/movel/gerar_pagina_mesa.py <pasta> <saida.html> [--movel]
      <pasta>   _trabalho/moveis/mesa_extensivel: geometria.json (extrair_pagina.py), saida/ (blender_mesa.py --luz),
                origem/*.html (the source page: its fonts, Barlow and JetBrains Mono, SIL OFL)
      --movel   the phone version: 2048 colour maps, 1024 normal maps, no post-processing (see the page's MOBILE)

three.js (MIT) travels inside, gzipped, as in gerar_pagina.py; the models (GLB) gzipped (sala_m.glb for phones); the
textures, lightmaps, contact shadows and the panoramas (JPEG over K, from aliviar_mesa.py) as data URIs. The page is a client's/designer's piece: never in Git.
"""
import base64
import datetime
import gzip
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "pagina"))
import gerar_pagina as gp  # noqa: E402  (its three.js bundler)

gp.ENTRADAS = ["build/three.module.js", "examples/jsm/controls/OrbitControls.js", "examples/jsm/loaders/GLTFLoader.js",
               "examples/jsm/postprocessing/EffectComposer.js",
               "examples/jsm/postprocessing/RenderPass.js", "examples/jsm/postprocessing/GTAOPass.js",
               "examples/jsm/postprocessing/OutputPass.js", "examples/jsm/environments/RoomEnvironment.js"]
MIME = {".webp": "image/webp", ".jpg": "image/jpeg", ".png": "image/png"}


def uri(p):
    return f"data:{MIME[p.suffix]};base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def gz(p):
    return base64.b64encode(gzip.compress(p.read_bytes(), 9, mtime=0)).decode("ascii")


def texturas(movel):
    """Logical names the page asks for -> files written by blender_mesa.py (tex/)."""
    t = {}
    for k in ("oak", "walnut", "marble"):
        t[k + "_cor"] = f"{k}_Diffuse_m.webp" if movel else f"{k}_Diffuse.webp"
        t[k + "_nor"] = f"{k}_nor_gl_m.webp" if movel else f"{k}_nor_gl.webp"
        t[k + "_rug"] = f"{k}_Rough.jpg" if (k == "marble" and not movel) else f"{k}_Rough_m.jpg"
    t.update({"linho_cor": "linho_cor.jpg", "tecido_nor": "tecido_nor_gl_m.webp", "tecido_rug": "tecido_Rough_m.jpg",
              "escovado_nor": "escovado_nor.png", "escovado_rug": "escovado_rug.png", "po_nor": "po_nor.png",
              "laca_nor": "laca_nor.png"})
    return t


def gerar(pasta, saida, movel=False):
    pasta = Path(pasta)
    out = pasta / "saida"
    geo = json.loads((pasta / "geometria.json").read_text(encoding="utf-8"))
    cfg = json.loads((AQUI / "mesa_extensivel.json").read_text(encoding="utf-8"))
    luz = json.loads((out / "luz.json").read_text(encoding="utf-8"))
    if "lm" not in luz or "env" not in luz:
        sys.exit("falta a luz cozida (blender_mesa.py --luz) ou o passo aliviar_mesa.py: luz.json sem 'lm' ou 'env'")
    origem = next((pasta / "origem").glob("*.html"))
    fontes = "\n".join(re.findall(r"^@font-face\{.*\}$", origem.read_text(encoding="utf-8"), re.M))
    variantes = [{k: v[k] for k in ("key", "name", "L", "W", "legx", "plan", "list")} for v in geo["variants"]]
    dados = {"variants": variantes, "acab": cfg["acabamentos"], "tecido": cfg["tecido"], "sala": cfg["sala"],
             "luz": {**luz, "noite": cfg["luz"]["noite"], "ceu_forca": cfg["luz"]["ceu_forca"]}, "movel": movel}
    dados["luz"].pop("texturas", None)
    pg = cfg["luz"].get("pagina", {})             # set against the Cycles references (mesa_extensivel.json)
    dados["luz"]["exposicao"] = pg.get("exposicao", {}).get("dia", dados["luz"]["exposicao"])
    dados["luz"]["exposicao_noite"] = pg.get("exposicao", {}).get("noite", dados["luz"]["exposicao_noite"])
    dados["luz"]["difusa_ibl"] = pg.get("difusa_ibl", {"dia": 1, "noite": 1})
    ativos = []

    def junta(chave, valor):
        ativos.append(f'<script type="text/plain" data-a="{chave}">{valor}</script>')

    for k in ("mesa", "cadeira", "sala"):
        f = out / (f"{k}_m.glb" if (movel and (out / f"{k}_m.glb").exists()) else f"{k}.glb")
        junta(f"glb/{k}", gz(f))
    for k in ("dia", "noite", "ceu"):
        junta(f"env/{k}", uri(out / f"env_{k}.jpg"))
    for k in luz["lm"]:
        junta(f"lm/{k}", uri(out / f"lm_{k}.jpg"))
    for k in luz.get("sombras", {}):
        junta(f"sombra/{k}", uri(out / f"sombra_{k}.png"))
    for k, f in texturas(movel).items():
        junta(f"tex/{k}", uri(out / "tex" / f))
    valores = {"FONTES": fontes, "DATA": datetime.date.today().strftime("%d-%m-%Y"),
               "DADOS": json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
               "MODULOS": json.dumps(gp._modulos(), separators=(",", ":")), "ATIVOS": "\n".join(ativos)}
    tpl = (AQUI / "modelo_mesa.html").read_text(encoding="utf-8")
    html = re.sub(r"__(" + "|".join(valores) + ")__", lambda m: valores[m.group(1)], tpl)
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    Path(saida).write_text(html, encoding="utf-8")
    return len(html.encode("utf-8"))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    n = gerar(args[0], args[1], movel="--movel" in sys.argv)
    print(f"página: {args[1]} ({n / 1e6:.1f} MB)")
