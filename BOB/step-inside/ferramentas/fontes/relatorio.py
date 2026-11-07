"""Gaps-and-conflicts report before generating geometry (spec §13 Fase 1 task 5, hub task 56).

Reads fontes.json and answers one question: can the geometry be generated from these sources?
    PASS                everything needed is CONFIRMED and nothing conflicts
    WARNING             it can, but some values are INFERRED or missing outside the essentials (e.g. terrain)
    NEEDS_HUMAN_REVIEW  a person has to look first (a value to confirm, an essential value missing, an open conflict)
    FAIL                the sources contradict themselves (e.g. an opening outside its wall); fix them first

    python step-inside/ferramentas/fontes/relatorio.py <fontes.json> [--md relatorio.md]
"""
import argparse
import fnmatch
import re
import sys
from collections import OrderedDict
from pathlib import Path

from comum import CONFIRMED, INFERRED, MISSING, REVIEW, campos, ler_json, utf8_stdout
from esquema import validar

# fields without which the house cannot be generated; MISSING here is not a mere warning
ESSENCIAIS = ["escala", "dimensoes.*", "niveis.pe_direito", "paredes.*"]
PASS, WARNING, FAIL = "PASS", "WARNING", "FAIL"
_EXPLICA = {
    PASS: "pode gerar-se a geometria.",
    WARNING: "pode gerar-se a geometria; os avisos ficam marcados no modelo.",
    REVIEW: "uma pessoa tem de rever os pontos abaixo antes de gerar a geometria.",
    FAIL: "as fontes contradizem-se; corrigir antes de gerar a geometria.",
}


def _padrao(caminho):
    """paredes.P03.aberturas.1.altura -> paredes.*.aberturas.*.altura (to group repeated fields)."""
    return re.sub(r"\.(P\d+|\d+)(?=\.|$)", ".*", caminho)


def _essencial(caminho):
    return any(fnmatch.fnmatchcase(caminho, p) for p in ESSENCIAIS)


def avaliar(doc):
    """(result, reasons, schema_errors)."""
    erros = validar(doc)
    porque = []
    if erros:
        porque.append(f"{len(erros)} erro(s) de schema")
    abertos = [c for c in doc["conflitos"] if c["estado"] == "aberto"]
    if erros or any(c["gravidade"] == FAIL for c in abertos):
        return FAIL, porque + [c["nota"] for c in abertos if c["gravidade"] == FAIL], erros
    todos = list(campos(doc))
    rever = [p for p, c in todos if c["estado"] == REVIEW]
    falta_ess = [p for p, c in todos if c["estado"] == MISSING and _essencial(p)]
    conf_rev = [c for c in abertos if c["gravidade"] == REVIEW]
    if rever or falta_ess or conf_rev:
        if rever:
            porque.append(f"{len(rever)} campo(s) a rever")
        if falta_ess:
            porque.append(f"{len(falta_ess)} campo(s) essencial(is) em falta")
        if conf_rev:
            porque.append(f"{len(conf_rev)} conflito(s) aberto(s)")
        return REVIEW, porque, erros
    inf = sum(1 for _, c in todos if c["estado"] == INFERRED)
    falta = sum(1 for _, c in todos if c["estado"] == MISSING)
    avisos = [c for c in abertos if c["gravidade"] == WARNING]
    if inf or falta or avisos:
        porque += [f"{inf} campo(s) inferido(s)"] * bool(inf) + [f"{falta} campo(s) em falta, não essenciais"] * \
            bool(falta) + [f"{len(avisos)} aviso(s)"] * bool(avisos)
        return WARNING, porque, erros
    return PASS, porque, erros


def _fonte_txt(f):
    if not f:
        return "—"
    t = f.get("documento", "")
    if f.get("folha"):
        t += f", folha {f['folha']}"
    if f.get("local"):
        t += f" ({f['local']})"
    return t


def _valor_txt(c):
    v = c["valor"]
    if v is None:
        return "—"
    if isinstance(v, list):
        return f"{len(v)} pontos"
    return f"{v:g} {c.get('unidade', '')}".strip() if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v)


def _agrupar(itens):
    """Group fields of the same section with the same method, source and note into one row."""
    g = OrderedDict()
    for p, c in itens:
        k = (p.split(".", 1)[0], c["metodo"], _fonte_txt(c["fonte"]), c.get("nota", ""))
        g.setdefault(k, []).append((p, c))
    return g


def markdown(doc):
    res, porque, erros = avaliar(doc)
    r = doc["resumo"]
    todos = list(campos(doc))
    L = [f"# Relatório de faltas e conflitos — {doc['projeto']['nome']}", "",
         f"Gerado a partir de `fontes.json` (entrada: {doc['projeto']['entrada']}; configuração "
         f"`{doc['projeto'].get('config', '')}`). Antes de gerar a geometria.", "",
         f"**Resultado: {res}** — {_EXPLICA[res]}" + (f" ({'; '.join(porque)})" if porque else ""), "",
         "| CONFIRMED | INFERRED | MISSING | NEEDS_HUMAN_REVIEW | Conflitos abertos | Conflitos resolvidos |",
         "|---|---|---|---|---|---|",
         f"| {r[CONFIRMED]} | {r[INFERRED]} | {r[MISSING]} | {r[REVIEW]} | {r['conflitos_abertos']} | "
         f"{r['conflitos_resolvidos']} |"]
    if erros:
        L += ["", "## Erros de schema", ""] + [f"- {e}" for e in erros[:30]]
    abertos = [c for c in doc["conflitos"] if c["estado"] == "aberto"]
    for grav, titulo in ((FAIL, "Bloqueios"), (REVIEW, "Conflitos abertos"), (WARNING, "Avisos")):
        cs = [c for c in abertos if c["gravidade"] == grav]
        if cs:
            L += ["", f"## {titulo}", ""] + [f"- `{c['campo']}`: {c['nota']}" for c in cs]
    for est, titulo in ((REVIEW, "Para rever (NEEDS_HUMAN_REVIEW)"), (MISSING, "Em falta (MISSING)"),
                        (INFERRED, "Inferidos (INFERRED)")):
        itens = [(p, c) for p, c in todos if c["estado"] == est]
        if not itens:
            continue
        L += ["", f"## {titulo}", "", "| Campo | N.º | Valor | Método | Fonte | Nota |", "|---|---|---|---|---|---|"]
        for (_, met, fon, nota), grupo in _agrupar(itens).items():
            pads = list(dict.fromkeys(_padrao(p) for p, _ in grupo))
            vals = sorted({_valor_txt(c) for _, c in grupo})
            v = vals[0] if len(vals) == 1 else f"{len(vals)} valores"
            ess = " ⚠ essencial" if est == MISSING and any(_essencial(p) for p, _ in grupo) else ""
            nomes = ", ".join(f"`{x}`" for x in pads)
            L.append(f"| {nomes}{ess} | {len(grupo)} | {v} | {met} | {fon} | {nota.replace('|', '/')} |")
    res_list = [(p, c, cf) for p, c in todos for cf in c["conflitos"] if cf.get("estado") == "resolvido"]
    if res_list:
        L += ["", "## Conflitos resolvidos (o que prevaleceu)", "",
              "| Campo | Usado | Fonte usada | Outro valor | Outra fonte | Resolução |", "|---|---|---|---|---|---|"]
        for p, c, cf in res_list:
            outro = cf["valor"] if cf["valor"] is not None else "—"
            L.append(f"| `{p}` | {_valor_txt(c)} | {_fonte_txt(c['fonte'])} | {outro} | {_fonte_txt(cf['fonte'])} | "
                     f"{cf.get('resolucao', '')} |")
    if doc["documentos"]:
        L += ["", "## Documentos", "", "| Ficheiro | Formato | Categoria | Usado para |", "|---|---|---|---|"]
        for d in doc["documentos"]:
            L.append(f"| {d['ficheiro']} | {d['formato']} | {d['categoria']} | {', '.join(d.get('usado_para', [])) or '—'} |")
    return "\n".join(L) + "\n", res


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fontes")
    ap.add_argument("--md")
    a = ap.parse_args()
    md, res = markdown(ler_json(a.fontes))
    if a.md:
        Path(a.md).parent.mkdir(parents=True, exist_ok=True)
        Path(a.md).write_text(md, encoding="utf-8")
        print(f"{a.md}: {res}")
    else:
        print(md)
    sys.exit({PASS: 0, WARNING: 0, REVIEW: 2, FAIL: 1}[res])


if __name__ == "__main__":
    main()
