"""Step Inside Phase 3 — common material catalogue and per-builder mappings (hub task 62). Standard library only.

    python step-inside/ferramentas/materiais/materiais.py [--construtor discovercasa]

catalogo.json holds the builder-agnostic IDs (MAT_<MASTER>, variants MAT_<MASTER>__<VARIANT>) with their PBR values;
mapeamentos/<construtor>.json maps a builder's product names (as its generator writes them) to those IDs.
validar() checks both; resolver() gives, for every product name, the final ID and PBR values (master + variant).
The visit model (visita/blender_visita.py) replaces the production materials with these catalogue materials.
"""
import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2] / "materiais"
ID = re.compile(r"^MAT_[A-Z0-9]+(?:_[A-Z0-9]+)*$")
VARIANTE = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)*$")
COR = re.compile(r"^#[0-9A-Fa-f]{6}$")
ESTADOS = ("CONFIRMED", "INFERRED", "MISSING", "NEEDS_HUMAN_REVIEW")


def ler(construtor="discovercasa"):
    cat = json.loads((RAIZ / "catalogo.json").read_text(encoding="utf-8"))
    mp = json.loads((RAIZ / "mapeamentos" / f"{construtor}.json").read_text(encoding="utf-8"))
    return cat, mp


def _pbr_ok(p, onde, erros, completo=True):
    if completo and not {"base_color", "roughness", "metallic"} <= set(p):
        erros.append(f"{onde}: pbr precisa de base_color, roughness e metallic")
    if "base_color" in p and not COR.match(p["base_color"]):
        erros.append(f"{onde}: base_color {p['base_color']!r} não é #RRGGBB")
    for k in ("roughness", "metallic", "opacity"):
        if k in p and not (0.0 <= p[k] <= 1.0):
            erros.append(f"{onde}: {k} fora de 0–1")


def validar(cat, mp=None):
    """List of errors (empty = valid)."""
    erros, vistos = [], set()
    for m in cat["materiais"]:
        i = m.get("id", "?")
        if not ID.match(i) or "__" in i:
            erros.append(f"{i}: id inválido (MAT_<MAIÚSCULAS>, sem '__' no mestre)")
        if i in vistos:
            erros.append(f"{i}: id repetido")
        vistos.add(i)
        if m.get("categoria") not in cat["categorias"]:
            erros.append(f"{i}: categoria {m.get('categoria')!r} desconhecida")
        if not m.get("nome", {}).get("pt"):
            erros.append(f"{i}: falta o nome em português")
        _pbr_ok(m.get("pbr", {}), i, erros)
        for v, p in (m.get("variantes") or {}).items():
            if not VARIANTE.match(v):
                erros.append(f"{i}__{v}: variante inválida")
            _pbr_ok(p, f"{i}__{v}", erros, completo=False)
    if mp:
        for nome, e in mp["materiais"].items():
            mestre, _, var = e["mat"].partition("__")
            m = next((x for x in cat["materiais"] if x["id"] == mestre), None)
            if not m:
                erros.append(f"{mp['construtor']}: «{nome}» -> {e['mat']}: material não existe no catálogo")
            elif var and var not in (m.get("variantes") or {}):
                erros.append(f"{mp['construtor']}: «{nome}» -> {e['mat']}: variante não existe")
            if e.get("estado", mp.get("estado_padrao")) not in ESTADOS:
                erros.append(f"{mp['construtor']}: «{nome}»: estado inválido")
    return erros


def resolver(cat, mp):
    """{product name: {"id", "mestre", "variante", "pbr", "visivel", "categoria", "estado", "fonte", "nota"}};
    catalogue IDs map to themselves (materials the Step Inside tools create, e.g. the terrain)."""
    por_id = {m["id"]: m for m in cat["materiais"]}
    out = {}
    for m in cat["materiais"]:
        out[m["id"]] = {"id": m["id"], "mestre": m["id"], "variante": "", "pbr": dict(m["pbr"]), "visivel": m["visivel"],
                        "categoria": m["categoria"], "estado": "CONFIRMED", "fonte": {"documento": "catalogo.json"}, "nota": ""}
    for nome, e in mp["materiais"].items():
        mestre, _, var = e["mat"].partition("__")
        m = por_id[mestre]
        pbr = dict(m["pbr"])
        pbr.update((m.get("variantes") or {}).get(var, {}))
        pbr.update(e.get("pbr", {}))  # a product's own colour, when the official list gives one
        out[nome] = {"id": e["mat"], "mestre": mestre, "variante": var, "pbr": pbr, "visivel": m["visivel"],
                     "categoria": m["categoria"], "estado": e.get("estado", mp.get("estado_padrao", "INFERRED")),
                     "fonte": e.get("fonte", mp.get("fonte_padrao")), "nota": e.get("nota", "")}
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--construtor", default="discovercasa")
    a = ap.parse_args()
    cat, mp = ler(a.construtor)
    erros = validar(cat, mp)
    for e in erros:
        print("ERRO", e)
    tab = resolver(cat, mp)
    usados = sorted({v["id"] for k, v in tab.items() if k in mp["materiais"]})
    print(f"catálogo: {len(cat['materiais'])} materiais mestre; {a.construtor}: {len(mp['materiais'])} produtos -> "
          f"{len(usados)} IDs; estados: " + ", ".join(f"{s} {sum(1 for k in mp['materiais'] if tab[k]['estado'] == s)}"
                                                      for s in ESTADOS))
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
