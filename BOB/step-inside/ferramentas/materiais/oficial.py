"""The official DiscoverCasa materials list (the Hub's list, user 2026-11-10) confirms the products of the mapping
(Step Inside Phase 3, hub task 163; user 2026-11-11: «avança … com a Lista oficial de materiais que já tens acesso»).

    python step-inside/ferramentas/materiais/oficial.py            # update mapeamentos/discovercasa.json
    python step-inside/ferramentas/materiais/oficial.py --ver      # only show what would change

A product becomes CONFIRMED when every one of its Listagem codes reaches a material of the official list
(orcamentacao/ligacoes.json, Hub material ids only: no Hub names or prices go into this public repo) and the official
product is the same thing the mapping shows. The exceptions below stay INFERRED, with the reason. The rest (not on the
official list yet: caixilharia, cortiça, cerâmico, azulejo, caleiras…) stay INFERRED until the list has them.
"""
import argparse
import json
import sys
from pathlib import Path

BOB = Path(__file__).resolve().parents[3]
MAPA = BOB / "step-inside" / "materiais" / "mapeamentos" / "discovercasa.json"
LIGACOES = BOB / "orcamentacao" / "ligacoes.json"
DATA = "2026-11-11"
# on the official list, but not the same thing the model shows
EXCECOES = {
    "Painel sandwich RAL 7016": "a lista oficial só tem o painel imitação telha em RAL 8004; o Sobral Tipo 1 usa-o em RAL 7016",
    "Pladur H1 (hidrófugo)": "a lista oficial só tem a placa standard; a hidrófuga ainda não está lá",
    "Pladur F (ignífugo)": "a lista oficial só tem a placa standard; a ignífuga ainda não está lá",
    "Saída de caleira": "a lista oficial tem o bocal de saída da caleira interior em branco brilhante; o modelo mostra-o preto (confirmar a cor à vista)",
}


def oficiais(mp, lig):
    """{product: [Hub material ids] or None when a code is missing from the official list}."""
    out = {}
    for nome, e in mp["materiais"].items():
        cods = e.get("codigos") or []
        ids = [(lig.get(c) or {}).get("hub") for c in cods]
        out[nome] = sorted(set(ids)) if cods and all(ids) else None
    return out


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", action="store_true")
    ap.add_argument("--mapeamento", default=str(MAPA))
    a = ap.parse_args(argv)
    caminho = Path(a.mapeamento)
    mp = json.loads(caminho.read_text(encoding="utf-8"))
    lig = json.loads(LIGACOES.read_text(encoding="utf-8"))["ligacoes"]
    conf = falta = 0
    for nome, ids in oficiais(mp, lig).items():
        e = mp["materiais"][nome]
        if ids and nome not in EXCECOES:
            e["estado"] = "CONFIRMED"
            e["fonte"] = {"documento": "lista oficial de materiais (Hub), por orcamentacao/ligacoes.json", "hub": ids, "data": DATA}
            conf += 1
        else:
            e.pop("estado", None)   # back to the mapping's default (INFERRED)
            e.pop("fonte", None)
            if nome in EXCECOES:
                e["oficial"] = EXCECOES[nome]
            falta += 1
        if ids is None or nome in EXCECOES:
            print(f"  INFERRED  {nome}{' — ' + EXCECOES[nome] if nome in EXCECOES else ' (não está na lista oficial)'}")
    print(f"{conf} produtos confirmados pela lista oficial; {falta} ficam INFERRED")
    if not a.ver:
        caminho.write_text(json.dumps(mp, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return conf, falta


if __name__ == "__main__":
    main()
