"""Read the furniture data of a 3D furniture page (the `window.__MODEL={...}` script of the extending-table page made
from a STEP file) and write it decoded, for Blender and for our own page.

    python ferramentas/movel/extrair_pagina.py <pagina.html> <saida.json>

The page stores each part as base64: positions int16 (metres x 2000, i.e. 0.5 mm steps; three.js axes: x length,
y up, z width) and indices uint16 or uint32 ("n32"). The output keeps every other field as it is (key, name, L, W,
legx, plan, list, role, side, name) and replaces "p"/"i" with "v" (metres, [x, y, z] flat) and "f" (flat indices).
The part data is a client's or a designer's drawing: the output belongs in _trabalho/ (never in Git).
"""
import base64
import json
import re
import struct
import sys
from pathlib import Path


def descodificar(parte):
    pu, iu = base64.b64decode(parte.pop("p")), base64.b64decode(parte.pop("i"))
    pos = struct.unpack(f"<{len(pu) // 2}h", pu)
    n32 = parte.pop("n32", False)
    idx = struct.unpack(f"<{len(iu) // (4 if n32 else 2)}{'I' if n32 else 'H'}", iu)
    parte["v"] = [round(q / 2000, 4) for q in pos]
    parte["f"] = list(idx)
    return parte


def main(origem, saida):
    texto = Path(origem).read_text(encoding="utf-8")
    m = re.search(r"window\.__MODEL\s*=\s*(\{.*?\})\s*;?\s*</script>", texto, re.S)
    if not m:
        sys.exit("não encontrei window.__MODEL na página")
    modelo = json.loads(m.group(1))
    for v in modelo["variants"]:
        v["parts"] = [descodificar(p) for p in v["parts"]]
        v["leaf"] = [descodificar(p) for p in v["leaf"]]
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    Path(saida).write_text(json.dumps(modelo, ensure_ascii=False), encoding="utf-8")
    for v in modelo["variants"]:
        tri = sum(len(p["f"]) // 3 for p in v["parts"] + v["leaf"])
        print(v["key"], v["name"], len(v["parts"]), "peças +", len(v["leaf"]), "da tábua,", tri, "triângulos")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
