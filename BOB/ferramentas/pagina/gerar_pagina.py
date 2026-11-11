"""The client's page: ONE self-contained HTML file with the house's 3D model (three.js travels inside, gzipped,
so it opens offline, from an e-mail attachment or a phone). Input: the page model written by modelo_dxf.py.

    python ferramentas/pagina/gerar_pagina.py <modelo.json> <saida.html> [--subtitulo "..."]

The page shows the model (storeys, roof and terrain on/off, "maquete" or "realista" look, furniture, views),
a levels diagram and the table of storeys with their rooms' areas. It never shows how the model was made.
"""
import argparse
import base64
import datetime
import gzip
import html
import json
import math
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
THREE = AQUI.parent.parent / "configurador" / "web" / "node_modules" / "three"
FICHEIROS = {"CORE": "build/three.core.js", "MOD": "build/three.module.js", "ORBIT": "examples/jsm/controls/OrbitControls.js"}
EXTERIOR = re.compile(r"deck|varanda|terra[cç]o|alpendre|p[áa]tio|logradouro", re.I)
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
         "novembro", "dezembro"]


def _embalar(rel):
    p = THREE / rel
    if not p.exists():
        sys.exit(f"falta {p}: corre 'npm install' em configurador/web")
    return base64.b64encode(gzip.compress(p.read_bytes(), 9, mtime=0)).decode("ascii")


def _num(v):
    return f"{v:,.2f}".replace(",", " ").replace(".", ",")


def ponto_interior(piso):
    """Eye inside the reference storey looking out through its widest glazing (camera x, y, target x, y)."""
    cont = piso["contorno"]
    cx = sum(x for x, _ in cont) / len(cont)
    cy = sum(y for _, y in cont) / len(cont)
    vidros = [f for f in piso.get("fachada", []) if f["tipo"] != "parede"]
    if not vidros:
        return [cx, cy, cont[0][0], cont[0][1]]
    f = max(vidros, key=lambda f: math.dist(f["p0"], f["p1"]))
    mx, my = (f["p0"][0] + f["p1"][0]) / 2, (f["p0"][1] + f["p1"][1]) / 2
    d = math.hypot(cx - mx, cy - my) or 1.0
    k = min(5.0, 0.8 * d) / d
    return [round(mx + (cx - mx) * k, 2), round(my + (cy - my) * k, 2), round(mx, 2), round(my, 2)]


def gerar(modelo, saida, subtitulo=None):
    M = json.loads(Path(modelo).read_text(encoding="utf-8"))
    pisos = sorted(M["pisos"], key=lambda p: p["z"])
    ref = next((p for p in pisos if p["id"] == M.get("referencia")), pisos[0])
    M["interior"] = ponto_interior(ref)
    util = sum(a for p in pisos for n, a in p.get("divisoes", []) if not EXTERIOR.search(n))
    ext = sum(a for p in pisos for n, a in p.get("divisoes", []) if EXTERIOR.search(n))
    topo = pisos[-1]
    ficha = [("Pisos", str(len(pisos))),
             ("Área útil interior", f"{_num(util)} m²" if util else "—"),
             ("Áreas exteriores", f"{_num(ext)} m²" if ext else "—"),
             (f"Cota {ref['nome']}", _num(ref["cota"])),
             ("Cota da cobertura", _num(topo["cota"] + topo["z_acima"] - topo["z"])),
             ("Altura acima do " + ref["nome"], f"{_num(topo['z_acima'] - ref['z'])} m")]
    nomes = ", ".join(p["nome"].split("·")[-1].strip().lower() for p in pisos)
    sub = subtitulo or (f"Moradia em {len(pisos)} pisos ({nomes}) sobre o terreno. Arraste para rodar, use a roda do "
                        "rato ou dois dedos para aproximar e escolha o que quer ver.")
    hoje = datetime.date.today()
    valores = {
        "TITULO": html.escape(M["nome"]),
        "SUBTITULO": html.escape(sub),
        "FICHA": "".join(f"<div><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>" for k, v in ficha),
        "DATA": f"{hoje.day} de {MESES[hoje.month - 1]} de {hoje.year}",
        "DADOS": json.dumps(M, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
    }
    valores.update({k: _embalar(v) for k, v in FICHEIROS.items()})
    modelo_html = (AQUI / "modelo_pagina.html").read_text(encoding="utf-8")
    pagina = re.sub(r"__(TITULO|SUBTITULO|FICHA|DATA|DADOS|CORE|MOD|ORBIT)__", lambda m: valores[m.group(1)], modelo_html)
    Path(saida).write_text(pagina, encoding="utf-8")
    return len(pagina.encode("utf-8"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("modelo")
    ap.add_argument("saida")
    ap.add_argument("--subtitulo")
    a = ap.parse_args()
    n = gerar(a.modelo, a.saida, a.subtitulo)
    print(f"página: {a.saida} ({n / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
