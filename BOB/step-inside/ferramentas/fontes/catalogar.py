"""Catalogue a project's source documents (spec §13 Fase 1 task 2, hub task 53).

For every file: format, matrix category (matriz.py), and for DWFx sheets what they show — sheet name, paper,
number of strokes, strokes in the drawing colour convention (red walls, blue glazing, magenta door swings),
kinds of view found in the text (planta, corte, alçado, levantamento...), scales written on the sheet and how
many numbers look like dimensions or levels. Only counts and keywords are written, never the text itself,
so the catalogue carries no client data (the repo is public).

    python step-inside/ferramentas/fontes/catalogar.py <pasta dos desenhos> --json out.json --md out.md
"""
import argparse
import re
import unicodedata
from pathlib import Path

from comum import escrever_json, utf8_stdout
from matriz import classificar

CORES = {"paredes_vermelho": "FF0000", "vidros_azul": "003FFF", "aberturas_magenta": "FF00FF"}
VISTAS = [("levantamento", r"LEVANTAMENTO|TOPOGRAF"), ("implantacao", r"IMPLANTA"), ("localizacao", r"LOCALIZA"),
          ("planta", r"\bPLANTA|\bPLAN\b"), ("corte", r"\bCORTE|\bCOR\b"), ("alcado", r"\bALCADO|\bALC\b"),
          ("cobertura", r"COBERTURA"), ("pormenor", r"PORMENOR|DETALHE|\bPOR CONST"), ("fundacoes", r"FUNDAC"),
          ("estrutura", r"ESTRUTURA"),
          ("modulos", r"\bMODULO"), ("modelacao_terreno", r"MODELA")]
_ESCALA = re.compile(r"\b1\s*[:/]\s*(\d{2,4})\b")
_NUMERO = re.compile(r"(?<![\d.,])[+-]?\d{1,3}[.,]\d{2,3}(?![\d.,])")


def _sem_acentos(t):
    return "".join(c for c in unicodedata.normalize("NFD", t.upper()) if unicodedata.category(c) != "Mn")


def _cor(c):
    if not c or not c.startswith("#"):
        return ""
    c = c[1:].upper()
    return c[2:] if len(c) == 8 else c  # XPS colours may carry alpha first (#AARRGGBB)


def _layout(nome, *ficheiros):
    """Sheet name without the DWG file name in front ("<dwg>-<layout>"): DWG names often carry the client's
    name, layout names do not. The catalogue still has to be read before it goes to the public repo."""
    for f in ficheiros:
        if f and nome.startswith(Path(f).stem + "-"):
            return nome[len(Path(f).stem) + 1:]
    return nome.split("-", 1)[1] if "-" in nome else nome


def folhas_dwfx(path):
    from ferramentas.dwfx.leitor import Dwfx, linhas
    d = Dwfx(path)
    out = []
    for inf in d.info():
        k = inf["folha"]
        paths = d.paths(k)
        texto = " ".join(l["text"] for l in linhas(d.glyphs(k)))
        nome = _layout(inf.get("nome", ""), inf.get("dwg"), path)
        txt = _sem_acentos(texto + " " + nome.replace("_", " "))
        cores = {nome: sum(1 for p in paths if _cor(p.get("stroke")) == hexa or _cor(p.get("fill")) == hexa)
                 for nome, hexa in CORES.items()}
        out.append({
            "folha": k, "nome": nome, "papel_mm": inf.get("papel_mm"),
            "tracos": len(paths), "cores": cores, "texto_caracteres": len(texto),
            "vistas": [v for v, rx in VISTAS if re.search(rx, txt)],
            "escalas": sorted({f"1:{m}" for m in _ESCALA.findall(texto)}, key=lambda s: int(s[2:])),
            "numeros": len(_NUMERO.findall(texto)),
        })
    return out


def catalogar(pasta):
    docs = []
    for p in sorted(Path(pasta).iterdir(), key=lambda q: q.name.lower()):
        if not p.is_file() or p.name.startswith("."):
            continue
        c = {"ficheiro": p.name, "tamanho_kb": round(p.stat().st_size / 1024)}
        c.update(classificar(p))
        if c["formato"] == "DWFX" and c["categoria"] == "DIRECT":
            c["folhas"] = folhas_dwfx(p)
        docs.append(c)
    return docs


def markdown(docs, titulo):
    L = [f"# {titulo}", "", "| Ficheiro | Formato | Categoria | Tamanho | Nota |", "|---|---|---|---|---|"]
    for d in docs:
        nota = d["nota"] + (f" Versão: {d['versao']}." if d.get("versao") else "") + \
            (" Tem modelo 3D." if d.get("tem_3d") else "")
        L.append(f"| {d['ficheiro']} | {d['formato']} | {d['categoria']} | {d['tamanho_kb']} KB | {nota} |")
    for d in docs:
        if not d.get("folhas"):
            continue
        L += ["", f"## {d['ficheiro']}", "",
              "| Folha | Nome | Papel (mm) | Traços | Vermelho / azul / magenta | Texto | Vistas no texto | Escalas | Números |",
              "|---|---|---|---|---|---|---|---|---|"]
        for f in d["folhas"]:
            c = f["cores"]
            papel = "×".join(str(round(x)) for x in f["papel_mm"]) if f.get("papel_mm") else "—"
            texto = f"{f['texto_caracteres']} car." if f["texto_caracteres"] else "sem texto (contornos)"
            L.append(f"| {f['folha']} | {f['nome']} | {papel} | {f['tracos']} | "
                     f"{c['paredes_vermelho']} / {c['vidros_azul']} / {c['aberturas_magenta']} | {texto} | "
                     f"{', '.join(f['vistas']) or '—'} | {', '.join(f['escalas']) or '—'} | {f['numeros']} |")
    return "\n".join(L) + "\n"


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta")
    ap.add_argument("--json")
    ap.add_argument("--md")
    ap.add_argument("--titulo", default="Catálogo de fontes")
    a = ap.parse_args()
    docs = catalogar(a.pasta)
    if a.json:
        escrever_json(a.json, {"documentos": docs})
    md = markdown(docs, a.titulo)
    if a.md:
        Path(a.md).parent.mkdir(parents=True, exist_ok=True)
        Path(a.md).write_text(md, encoding="utf-8")
    else:
        print(md)


if __name__ == "__main__":
    main()
