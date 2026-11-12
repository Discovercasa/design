"""The client's page: ONE self-contained HTML file (opens offline, from an e-mail attachment or a phone) with
  - the photorealistic images rendered by casa_blender.py (Cycles),
  - the house in 3D (the GLB from casa_blender.py), "Realista" (real materials, sky, sun) or "Maquete" (white model),
    storeys cut from the top down, roof, exterior and terrain on/off, the project's views, a north arrow,
  - the table of storeys with the rooms' areas and the list of finishes.
It never shows how the model was made. three.js (MIT) travels inside, gzipped.

    python ferramentas/pagina/gerar_pagina.py <pagina.json> <saida.html>

pagina.json: {"titulo", "subtitulo", "modelo": "<folder with casa.glb and render_*.jpg>", "casa": "<casa.json>",
              "pisos": [{"id", "nome", "cota", "divisoes": [[nome, m2], ...]}], "cota_topo",
              "imagens": [{"vista", "titulo"}], "acabamentos": [{"parte", "texto", "cor"}], "ficha": [[k, v], ...]}
"""
import base64
import datetime
import gzip
import html
import json
import math
import posixpath
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
THREE = AQUI.parent.parent / "configurador" / "web" / "node_modules" / "three"
ENTRADAS = ["build/three.module.js", "examples/jsm/controls/OrbitControls.js", "examples/jsm/loaders/GLTFLoader.js",
            "examples/jsm/postprocessing/EffectComposer.js", "examples/jsm/postprocessing/RenderPass.js",
            "examples/jsm/postprocessing/GTAOPass.js", "examples/jsm/postprocessing/OutputPass.js",
            "examples/jsm/objects/Sky.js", "examples/jsm/environments/RoomEnvironment.js"]
IMPORTA = re.compile(r"""(?:\bfrom\s*|\bimport\s*\(\s*|\bimport\s+)(['"])([^'"\n]+)\1""")
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
         "novembro", "dezembro"]


def _modulos():
    """three's modules the page imports, with everything they import (relative paths and 'three')."""
    if not THREE.exists():
        sys.exit(f"falta {THREE}: corre 'npm install' em configurador/web")
    feitos, fila = {}, list(ENTRADAS)
    while fila:
        p = fila.pop()
        if p in feitos:
            continue
        src = (THREE / p).read_text(encoding="utf-8")
        feitos[p] = base64.b64encode(gzip.compress(src.encode("utf-8"), 9, mtime=0)).decode("ascii")
        for _, esp in IMPORTA.findall(src):
            alvo = "build/three.module.js" if esp == "three" else posixpath.normpath(posixpath.join(posixpath.dirname(p), esp))
            if (THREE / alvo).exists() and alvo not in feitos:
                fila.append(alvo)
    return feitos


def _num(v):
    return f"{v:,.2f}".replace(",", " ").replace(".", ",")


def gerar(pagina, saida):
    P = json.loads(Path(pagina).read_text(encoding="utf-8"))
    base = Path(pagina).resolve().parent
    modelo = (base / P["modelo"]).resolve()
    C = json.loads((base / P["casa"]).read_text(encoding="utf-8"))
    th = math.radians(C.get("rodar_graus", 0.0))

    def tres(p):       # plan frame (x, y, z up) -> three.js (y up, north = -z)
        x, y, z = p
        xr, yr = x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th)
        return [round(xr, 3), round(z, 3), round(-yr, 3)]
    titulos = {i["vista"]: i["titulo"] for i in P.get("imagens", [])}
    vistas = [{"nome": v["nome"], "titulo": titulos.get(v["nome"], v["nome"].capitalize()),
               "camara": tres(v["camara"]), "alvo": tres(v["alvo"])} for v in C.get("vistas", [])]
    cx, cy = C.get("centro", [0, 0])
    pisos = [{**p, "cota_txt": _num(p["cota"])} for p in P["pisos"]]
    dados = {"pisos": pisos, "cota_topo": _num(P["cota_topo"]), "vistas": vistas, "sol": C.get("sol", {}),
             "centro": tres([cx, cy, 2.0]), "acabamentos": P.get("acabamentos", [])}
    sol = dict(dados["sol"])
    sol["azimute"] = sol.get("azimute", 235)
    dados["sol"] = sol
    galeria = []
    for i in P.get("imagens", []):
        f = modelo / f"render_{i['vista']}.jpg"
        if f.exists():
            b = base64.b64encode(f.read_bytes()).decode("ascii")
            galeria.append(f'<img src="data:image/jpeg;base64,{b}" alt="{html.escape(i["titulo"])}">')
    hoje = datetime.date.today()
    valores = {
        "TITULO": html.escape(P["titulo"]),
        "SUBTITULO": html.escape(P.get("subtitulo", "")),
        "FICHA": "".join(f"<div><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>" for k, v in P.get("ficha", [])),
        "DATA": f"{hoje.day} de {MESES[hoje.month - 1]} de {hoje.year}",
        "GALERIA": "\n    ".join(galeria),
        "DADOS": json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
        "MODULOS": json.dumps(_modulos(), separators=(",", ":")),
        "GLB": base64.b64encode((modelo / "casa.glb").read_bytes()).decode("ascii"),
    }
    tpl = (AQUI / "modelo_pagina.html").read_text(encoding="utf-8")
    pagina_html = re.sub(r"__(TITULO|SUBTITULO|FICHA|DATA|GALERIA|DADOS|MODULOS|GLB)__", lambda m: valores[m.group(1)], tpl)
    Path(saida).write_text(pagina_html, encoding="utf-8")
    return len(pagina_html.encode("utf-8")), len(galeria)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    n, g = gerar(sys.argv[1], sys.argv[2])
    print(f"página: {sys.argv[2]} ({n / 1e6:.2f} MB, {g} imagens)")
