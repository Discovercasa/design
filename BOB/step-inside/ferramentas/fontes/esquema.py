"""Minimal JSON Schema check for fontes_projeto.schema.json (standard library only, no jsonschema package).

Supports the subset the schema uses: type (one or a list), required, properties, additionalProperties
(bool or schema), items, enum and local $ref ("#/$defs/..."). Plus one rule JSON Schema cannot say simply:
a MISSING field has valor null.

    python step-inside/ferramentas/fontes/esquema.py <fontes.json>
"""
import sys

from comum import ESQUEMA, MISSING, campos, ler_json, utf8_stdout

_TIPOS = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _tipo_ok(v, t):
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, _TIPOS[t])


def _validar(v, s, raiz, caminho, erros):
    if "$ref" in s:
        nome = s["$ref"].rsplit("/", 1)[-1]
        _validar(v, raiz["$defs"][nome], raiz, caminho, erros)
        s = {k: x for k, x in s.items() if k not in ("$ref", "description")}
        if not s:
            return
    t = s.get("type")
    if t is not None:
        ts = t if isinstance(t, list) else [t]
        if not any(_tipo_ok(v, x) for x in ts):
            erros.append(f"{caminho}: tipo {type(v).__name__}, esperado {t}")
            return
    if "enum" in s and v not in s["enum"]:
        erros.append(f"{caminho}: {v!r} não está em {s['enum']}")
    if isinstance(v, dict):
        for k in s.get("required", []):
            if k not in v:
                erros.append(f"{caminho}: falta «{k}»")
        props = s.get("properties", {})
        extra = s.get("additionalProperties", True)
        for k, x in v.items():
            if k in props:
                _validar(x, props[k], raiz, f"{caminho}.{k}", erros)
            elif extra is False:
                erros.append(f"{caminho}: chave não prevista «{k}»")
            elif isinstance(extra, dict):
                _validar(x, extra, raiz, f"{caminho}.{k}", erros)
    if isinstance(v, list) and "items" in s:
        for i, x in enumerate(v):
            _validar(x, s["items"], raiz, f"{caminho}[{i}]", erros)


def validar(doc, esquema=None):
    """Return a list of error strings (empty = valid)."""
    raiz = esquema or ler_json(ESQUEMA)
    erros = []
    _validar(doc, raiz, raiz, "$", erros)
    for caminho, c in campos(doc):
        if c["estado"] == MISSING and c["valor"] is not None:
            erros.append(f"{caminho}: MISSING com valor {c['valor']!r}")
    return erros


if __name__ == "__main__":
    utf8_stdout()
    e = validar(ler_json(sys.argv[1]))
    print("\n".join(e) if e else "válido")
    sys.exit(1 if e else 0)
