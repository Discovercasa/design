"""Shared helpers for the Step Inside Phase 1 source tools (standard library only).

A *campo* (field) is one value with its provenance, as the spec §3.2 asks:
    {"valor", "unidade", "tipo", "estado", "metodo", "fonte", "nota", "conflitos"}
estado: CONFIRMED | INFERRED | MISSING | NEEDS_HUMAN_REVIEW (spec rule 9: never invent a value).
"""
import json
import sys
from pathlib import Path

BOB = Path(__file__).resolve().parents[3]          # .../BOB
if str(BOB) not in sys.path:
    sys.path.insert(0, str(BOB))                   # ferramentas.dwfx.leitor (the existing readers)

ESQUEMA = BOB / "step-inside" / "schema" / "fontes_projeto.schema.json"
VERSAO_ESQUEMA = "1.0"

CONFIRMED, INFERRED, MISSING, REVIEW = "CONFIRMED", "INFERRED", "MISSING", "NEEDS_HUMAN_REVIEW"
ESTADOS = (CONFIRMED, INFERRED, MISSING, REVIEW)
# weakest first: a value derived from several inputs takes the weakest state among them
_FORCA = {REVIEW: 0, MISSING: 0, INFERRED: 1, CONFIRMED: 2}

METODOS = ("geometria", "texto", "ocr", "inferencia", "valor_omissao", "norma_empresa", "desenho_empresa",
           "utilizador", "calculo", "nenhum")


def campo(valor, estado, metodo, *, unidade="", tipo="", fonte=None, nota="", conflitos=None):
    if estado == MISSING:
        valor = None
    return {"valor": valor, "unidade": unidade, "tipo": tipo, "estado": estado, "metodo": metodo,
            "fonte": fonte, "nota": nota, "conflitos": list(conflitos or [])}


def em_falta(tipo="", nota="", unidade=""):
    return campo(None, MISSING, "nenhum", unidade=unidade, tipo=tipo, nota=nota)


def fonte(documento, folha=None, local="", data=""):
    return {"documento": documento, "folha": folha, "local": local, "data": data}


def mais_fraco(*estados):
    return min(estados, key=lambda e: _FORCA[e])


def ler_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def escrever_json(p, dados):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def campos(no, caminho=""):
    """Yield (path, campo) for every field in a provenance document (a dict with 'estado' and 'metodo')."""
    if isinstance(no, dict):
        if "estado" in no and "metodo" in no and "valor" in no:
            yield caminho, no
            return
        for k, v in no.items():
            if k in ("conflitos", "resumo", "documentos", "projeto"):
                continue
            yield from campos(v, f"{caminho}.{k}" if caminho else k)
    elif isinstance(no, list):
        for i, v in enumerate(no):
            chave = v.get("id", v.get("elemento", i)) if isinstance(v, dict) else i
            yield from campos(v, f"{caminho}.{chave}")


def utf8_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
