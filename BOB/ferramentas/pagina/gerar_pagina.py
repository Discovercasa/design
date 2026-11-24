"""The client's page: ONE self-contained HTML file (opens offline, from an e-mail attachment or a phone) with
  - the photorealistic images rendered by casa_blender.py (Cycles),
  - the house in 3D (the GLB from casa_blender.py), "Realista" (real materials, sky, sun) or "Maquete" (white model),
    storeys cut from the top down, roof, exterior and terrain on/off, the project's views, a north arrow,
  - the table of storeys with the rooms' areas and the list of finishes.
It never shows how the model was made. three.js (MIT) travels inside, gzipped.

    python ferramentas/pagina/gerar_pagina.py <pagina.json> <saida.html>

pagina.json: {"titulo", "subtitulo", "modelo": "<folder with casa.glb and render_*.jpg>", "casa": "<casa.json>",
              "pisos": [{"id", "nome", "cota", "divisoes": [[nome, m2], ...]}], "cota_topo",
              "imagens": [{"vista", "titulo"}], "acabamentos": [{"parte", "texto", "cor"}], "ficha": [[k, v], ...],
              optional: "renders" (folder of the images and panoramas, default "modelo"),
              "legal" (the footer's line), "planta_inicial" (the plan shown first), "textos" {exterior: the 3D's
              sub-label for the outside}, "en" {PT text: EN text} + "en_padroes" [[regex, replacement: $1 the group, {1} the group translated]]
              (a PT/EN switch),
              "tecnico" {html, titulo, texto, botao, itens} (another 3D page of the project, opened on demand),
              "camada" (an ES module added to OUR 3D: default export (ctx) -> Promise; ctx.API has definirSol
              (a sun of its own: the baked light gives way to the sun's), cortarParedes ({g, y}: a storey's walls cut
              by a plane, the cut drawn solid), grupos/visivel (storeys shown), parar, voarPara/colocar, aCadaPasso
              (dt; true when it placed the camera itself), depois (after each frame), aoMudarModo (the 360° tour)).
              No «Como construímos» and no closing section (user 2026-11-18).}
Standard (user 2026-11-21): ONE interactive 3D at our quality with the 360° tour inside it. When the project has a 3D on
the hub, its controls are rebuilt as a "camada" on our baked model (Matosinhos: the hub's static meshes exported without
the parts that move, baked; the layer draws only doors, windows, gates, shutters, the electrical symbols and the
neighbours, and keeps the hub's walls and floors invisible for walking) — never a second, flat technical model.
The tour (casa.json "visita": points with camara, olhar, liga) shows render_pano_<id>.jpg, as a mode of the 3D viewer
(the house from outside, a circle per point, fly in, walk panorama to panorama); the plans are drawn from
casa.json (storey volumes, rooms, openings, stairs, the furniture's footprints, "divisoes" for names and areas).
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
            "examples/jsm/environments/RoomEnvironment.js"]
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


PEGADAS = {   # furniture footprints on the plans: local rectangle (front = +y) from the piece's own sizes
    "sofa": lambda d: [-d.get("larg", 2.5) / 2, -d.get("prof", 0.95) / 2, d.get("larg", 2.5) / 2, d.get("prof", 0.95) / 2],
    "maple": lambda d: [-0.4, -0.4, 0.4, 0.4],
    "mesa_centro": lambda d: [-d.get("larg", 1.1) / 2, -d.get("prof", 0.6) / 2, d.get("larg", 1.1) / 2, d.get("prof", 0.6) / 2],
    "mesa_jantar": lambda d: [-d.get("larg", 1.8) / 2, -d.get("prof", 0.9) / 2, d.get("larg", 1.8) / 2, d.get("prof", 0.9) / 2],
    "mesa_exterior": lambda d: [-d.get("larg", 1.6) / 2, -d.get("prof", 0.9) / 2, d.get("larg", 1.6) / 2, d.get("prof", 0.9) / 2],
    "secretaria": lambda d: [-d.get("larg", 1.5) / 2, -d.get("prof", 0.65) / 2, d.get("larg", 1.5) / 2, d.get("prof", 0.65) / 2],
    "cozinha": lambda d: [-d["larg"] / 2, -0.62, d["larg"] / 2, 0.0],
    "lareira": lambda d: [-d.get("larg", 3.3) / 2, -d.get("prof", 0.62), d.get("larg", 3.3) / 2, 0.0],
    "roupeiro": lambda d: [-d["larg"] / 2, -d.get("prof", 0.6), d["larg"] / 2, 0.0],
    "estante": lambda d: [-d.get("larg", 1.6) / 2, -d.get("prof", 0.35), d.get("larg", 1.6) / 2, 0.0],
    "aparador": lambda d: [-d.get("larg", 1.6) / 2, -d.get("prof", 0.42), d.get("larg", 1.6) / 2, 0.0],
    "cama": lambda d: [-d.get("larg", 1.8) / 2 - 0.05, -d.get("comp", 2.05) / 2 - 0.06, d.get("larg", 1.8) / 2 + 0.05,
                       d.get("comp", 2.05) / 2],
    "sanita": lambda d: [-0.18, 0.0, 0.18, 0.56],
    "lavatorio": lambda d: [-d.get("larg", 1.2) / 2, 0.0, d.get("larg", 1.2) / 2, d.get("prof", 0.48)],
    "duche": lambda d: [-d.get("larg", 1.4) / 2, 0.0, d.get("larg", 1.4) / 2, d.get("prof", 0.85)],
    "espreguicadeira": lambda d: [-0.33, -0.95, 0.33, 0.95],
}


def _poligono(d, r):
    a = math.radians(d.get("rot", 0.0))
    c, s = math.cos(a), math.sin(a)
    return [[round(d["x"] + c * lx - s * ly, 3), round(d["y"] + s * lx + c * ly, 3)]
            for lx, ly in ((r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3]))]


def _planta(C, pisos):
    """Per storey: volumes, rooms (interior / exterior), glazing, stairs, furniture footprints, the rooms' names."""
    I = C.get("interior") or {}
    out = []
    for p in pisos:
        pid = p["id"]
        vz = [v for v in C.get("vazios", []) if pid in (v.get("em") or [])]
        if not vz:
            continue
        chao = min(v["caixa"][2] for v in vz)
        sol = [s["caixa"] for s in C.get("solidos", []) if s["nome"] == pid]
        vaz = [[*v["caixa"][:2], *v["caixa"][3:5], "ext" if (v.get("mats") or {}).get("lados") == "ripado" else "int"]
               for v in vz if v["caixa"][2] <= chao + 0.6 and (v.get("mats") or {}).get("chao") != "painel"]
        ext = [[c["caixa"][0], c["caixa"][1], c["caixa"][3], c["caixa"][4]] for c in C.get("caixas", [])
               if c.get("grupo") == pid and c.get("mat") == "deck"]
        vaos = [[*va["caixa"][:2], *va["caixa"][3:5], va["eixo"]] for va in C.get("vaos", []) if va.get("grupo") == pid]
        esc = []
        for e in I.get("escadas", []):
            a, b = e["de"], e["ate"]
            if not (e.get("grupo") == pid or abs(b[2] - chao) < 0.4 or abs(a[2] - chao) < 0.4):
                continue
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            ux, uy, w = dx / L, dy / L, e.get("largura", 1.0) / 2
            n = int(e.get("degraus", 16))
            lado = (-uy * w, ux * w)
            cont = [[a[0] + lado[0], a[1] + lado[1]], [b[0] + lado[0], b[1] + lado[1]],
                    [b[0] - lado[0], b[1] - lado[1]], [a[0] - lado[0], a[1] - lado[1]]]
            deg = []
            for i in range(n):
                t = i / max(1, n - 1)
                cx, cy = a[0] + dx * t, a[1] + dy * t
                deg.append([[round(cx + lado[0], 3), round(cy + lado[1], 3)], [round(cx - lado[0], 3), round(cy - lado[1], 3)]])
            esc.append({"contorno": [[round(x, 3), round(y, 3)] for x, y in cont], "degraus": deg})
        mov = []
        for d in I.get("pecas", []):
            if d.get("grupo") == pid and d["tipo"] in PEGADAS:
                mov.append(_poligono(d, PEGADAS[d["tipo"]](d)))
                if d["tipo"] == "cama" and d.get("mesinhas", True):
                    L, Cc = d.get("larg", 1.8), d.get("comp", 2.05)
                    for sx in (-1, 1):
                        cx = sx * (L / 2 + 0.33)
                        mov.append(_poligono(d, [cx - 0.24, -Cc / 2 + 0.05, cx + 0.24, -Cc / 2 + 0.45]))
        div = [d for d in C.get("divisoes", []) if d.get("piso") == pid]
        out.append({"id": pid, "nome": p["nome"], "solidos": [[b[0], b[1], b[3], b[4]] for b in sol], "vazios": vaz,
                    "exteriores": ext, "vaos": vaos, "escadas": esc, "moveis": mov, "divisoes": div})
    return {"rodar": C.get("rodar_graus", 0.0), "pisos": out}


def gerar(pagina, saida):
    P = json.loads(Path(pagina).read_text(encoding="utf-8"))
    base = Path(pagina).resolve().parent
    modelo = (base / P["modelo"]).resolve()
    renders = (base / P.get("renders", P["modelo"])).resolve()
    C = json.loads((base / P["casa"]).read_text(encoding="utf-8"))
    th = math.radians(C.get("rodar_graus", 0.0))

    def tres(p):       # plan frame (x, y, z up) -> three.js (y up, north = -z)
        x, y, z = p
        xr, yr = x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th)
        return [round(xr, 3), round(z, 3), round(-yr, 3)]
    titulos = {i["vista"]: i["titulo"] for i in P.get("imagens", [])}
    # the 3D's view buttons: the images' cameras (in the images' order); never the panoramas' or unused cameras
    # (they showed up as «Pano_sala_a», «Tardoz»…)
    porNome = {v["nome"]: v for v in C.get("vistas", []) if not v.get("panorama")}
    vistas = [{"nome": n, "titulo": titulos[n], "camara": tres(porNome[n]["camara"]), "alvo": tres(porNome[n]["alvo"]),
               "lente": porNome[n].get("lente", 26)} for n in titulos if n in porNome]
    cx, cy = C.get("centro", [0, 0])
    pisos = [{**p, "cota_txt": _num(p["cota"])} for p in P["pisos"]]
    dados = {"pisos": pisos, "cota_topo": _num(P["cota_topo"]), "cota_topo_num": P["cota_topo"], "vistas": vistas, "sol": C.get("sol", {}),
             "centro": tres([cx, cy, 2.0]), "acabamentos": P.get("acabamentos", []), "rodar": C.get("rodar_graus", 0.0)}
    sol = dict(dados["sol"])
    sol["azimute"] = sol.get("azimute", 235)
    dados["sol"] = sol
    # the baked light (casa_blender.py --luz): lightmaps, the sky of the images, the leaf cards
    texturas = {}
    luz = modelo / "luz.json"
    if luz.exists():
        dados["luz"] = json.loads(luz.read_text(encoding="utf-8"))
        for k in dados["luz"]:
            texturas["lm_" + k] = "data:image/jpeg;base64," + base64.b64encode((modelo / f"lm_{k}.jpg").read_bytes()).decode("ascii")
    for chave, nome, tipo in (("ceu", "ceu.jpg", "jpeg"), ("folha", "folha.png", "png")):
        if (modelo / nome).exists():
            texturas[chave] = f"data:image/{tipo};base64," + base64.b64encode((modelo / nome).read_bytes()).decode("ascii")
    if P.get("ajuste"):
        dados["ajuste"] = P["ajuste"]
    visita = [v for v in C.get("visita", []) if (renders / f"render_pano_{v['id']}.jpg").exists()]
    ids = {v["id"] for v in visita}
    dados["visita"] = [{**v, "p3": tres(v["camara"]), "liga": [o for o in v.get("liga", []) if o in ids]} for v in visita]
    # the plans: from casa.json's volumes and rooms, or drawn by the project's generator (casa.json "planta": a house
    # whose 3D came from elsewhere, with "poligonos" [{pts, f chao|ext|parede}] and vaos [x0, y0, x1, y1, "l"])
    dados["planta"] = C["planta"] if C.get("planta") else _planta(C, P["pisos"])
    if P.get("planta_inicial"):
        dados["planta"]["inicial"] = P["planta_inicial"]
    if P.get("textos"):
        dados["textos"] = P["textos"]
    panos = "\n".join(f'<script type="text/plain" id="pano-{v["id"]}">'
                       + base64.b64encode((renders / f"render_pano_{v['id']}.jpg").read_bytes()).decode("ascii")
                       + "</script>" for v in visita)
    fotos = []
    for i in P.get("imagens", []):
        f = renders / f"render_{i['vista']}.jpg"
        if f.exists():
            fotos.append((base64.b64encode(f.read_bytes()).decode("ascii"), html.escape(i["titulo"])))
    hero = galeria = ""
    if fotos:
        b, tit = fotos[0]
        hero = (f'<button data-foto data-titulo="{tit}" aria-label="Ver em ecrã inteiro: {tit}" '
                f'style="all:unset;display:block;width:100%;height:100%"><img src="data:image/jpeg;base64,{b}" alt="{tit}"></button>')
        galeria = "\n      ".join(
            f'<figure><button data-foto data-titulo="{tit}" aria-label="Ver em ecrã inteiro: {tit}">'
            f'<img src="data:image/jpeg;base64,{b}" alt="{tit}" loading="lazy"></button><figcaption>{tit}</figcaption></figure>'
            for b, tit in fotos[1:])
    # English (optional): the PT -> EN dictionary of the page's texts, and a switch on the opening photograph
    lingua = ""
    if P.get("en"):
        dados["en"], dados["en_padroes"], dados["titulo"] = P["en"], P.get("en_padroes", []), P["titulo"]
        lingua = ('<div class="lingua" id="lingua" role="group" aria-label="Idioma / Language">'
                  '<button data-l="pt" aria-pressed="true">PT</button><button data-l="en" aria-pressed="false">EN</button></div>')
    # the project's technical model (optional): another 3D page (e.g. the hub's), gzipped, opened on demand
    tecnico = menu_tecnico = ""
    if P.get("tecnico"):
        T = P["tecnico"]
        bruto = (base / T["html"]).read_bytes()
        itens = "".join(f"<li>{html.escape(i)}</li>" for i in T.get("itens", []))
        tecnico = (f'<section class="bloco tecnico" aria-labelledby="h-tecnico"><div class="largura">'
                   f'<div class="cab"><h2 id="h-tecnico">{html.escape(T.get("titulo", "Modelo técnico"))}</h2>'
                   f'<p>{html.escape(T.get("texto", ""))}</p></div>'
                   f'<div class="quadro" id="quadroTecnico"><div class="abrir"><ul>{itens}</ul>'
                   f'<button id="abrirTecnico" data-titulo="{html.escape(T.get("titulo", "Modelo técnico"))}">'
                   f'{html.escape(T.get("botao", "Abrir o modelo técnico"))}</button></div></div></div></section>'
                   f'<script id="tecnico-html" type="text/plain">'
                   + base64.b64encode(gzip.compress(bruto, 9, mtime=0)).decode("ascii") + "</script>")
        menu_tecnico = f'<a href="#h-tecnico">{html.escape(T.get("titulo", "Modelo técnico"))}</a>'
    # the project's layer (optional): an ES module whose default export (ctx) adds controls and parts to the 3D, e.g.
    # the hub's interactive model rebuilt on our baked one (floors, sun, cut walls, doors, shutters, walking...)
    camada = ""
    if P.get("camada"):
        src = (base / P["camada"]).read_bytes()
        camada = ('<script id="camada" type="text/plain">'
                  + base64.b64encode(gzip.compress(src, 9, mtime=0)).decode("ascii") + "</script>")
    hoje = datetime.date.today()
    legal = P.get("legal", "Imagens ilustrativas: o mobiliário, a decoração e a envolvente (casas vizinhas, "
                           "vegetação, céu) são indicativos. Áreas do projeto de arquitetura.")
    valores = {
        "TITULO": html.escape(P["titulo"]),
        "SUBTITULO": html.escape(P.get("subtitulo", "")),
        "FICHA": "".join(f"<div><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>" for k, v in P.get("ficha", [])),
        "DATA": f"{hoje.day} de {MESES[hoje.month - 1]} de {hoje.year}",
        "HERO": hero,
        "GALERIA": galeria,
        "DADOS": json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
        "MODULOS": json.dumps(_modulos(), separators=(",", ":")),
        # gzipped (about 40 % of the GLB): pages with furniture, trees and grass stay under the hub's 50 MB file limit
        "GLB": base64.b64encode(gzip.compress((modelo / "casa.glb").read_bytes(), 9, mtime=0)).decode("ascii"),
        "TEXTURAS": json.dumps(texturas, separators=(",", ":")),
        "PANOS": panos,
        "LEGAL": html.escape(legal),
        "LINGUA": lingua,
        "TECNICO": tecnico,
        "MENU_TECNICO": menu_tecnico,
        "CAMADA": camada,
    }
    tpl = (AQUI / "modelo_pagina.html").read_text(encoding="utf-8")
    pagina_html = re.sub(r"__(" + "|".join(valores) + ")__", lambda m: valores[m.group(1)], tpl)
    Path(saida).write_text(pagina_html, encoding="utf-8")
    return len(pagina_html.encode("utf-8")), len(fotos)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    n, g = gerar(sys.argv[1], sys.argv[2])
    print(f"página: {sys.argv[2]} ({n / 1e6:.2f} MB, {g} imagens)")
