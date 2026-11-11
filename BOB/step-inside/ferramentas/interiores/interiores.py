"""Step Inside — furnish the visit model (hub task 167): kitchen, bathrooms, beds, wardrobes, sofas, lamps, plants.

    python step-inside/ferramentas/interiores/interiores.py step-inside/projetos-teste/<obra>/visita.json [--sem-render]

Needs: the visit model (visita.py), the CC0 models on this PC (python interiores/descarregar.py) and the layout
step-inside/projetos-teste/<obra>/interiores.json. The objects come from the common catalogue interiores/catalogo.json
(the same one the Build Your House «Smart Interiors» will use).
Outputs. Local only (_trabalho/step-inside/<obra>/): visita/visita_interiores.blend (the visit model is not touched)
and interiores/*.png (a plan from above and the eye-level views). Committed: projetos-teste/<obra>/interiores_resumo.json.
Exit code: 0 PASS / WARNING (pieces in walls, outside their room or overlapping are warnings), 1 FAIL.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "fontes"))
import comum  # noqa: E402

BOB = comum.BOB
CATALOGO = BOB / "interiores" / "catalogo.json"
MODELOS = BOB / "_trabalho" / "interiores" / "polyhaven"


def main():
    comum.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("visita")
    ap.add_argument("--sem-render", action="store_true")
    a = ap.parse_args()
    vp = Path(a.visita).resolve()
    obra = comum.ler_json(vp)["obra"]
    disp = comum.ler_json(vp.parent / "interiores.json")
    cat = {o["id"]: o for o in comum.ler_json(CATALOGO)["objetos"]}
    blend = BOB / "_trabalho" / "step-inside" / obra / "visita" / "visita.blend"
    if not blend.exists():
        raise SystemExit("primeiro o modelo de visita: python step-inside/ferramentas/visita/visita.py " + a.visita)
    falta = [p["obj"] for p in disp["pecas"] if p["obj"] not in cat]
    if falta:
        raise SystemExit(f"objetos que não estão no catálogo: {sorted(set(falta))}")
    modelos = {}
    for p in disp["pecas"]:
        o = cat[p["obj"]]
        if o["origem"]["tipo"] == "polyhaven":
            asset = o["origem"]["asset"]
            g = sorted((MODELOS / asset).glob("*.gltf"))
            if not g:
                raise SystemExit(f"falta o modelo {asset}: python interiores/descarregar.py")
            modelos[asset] = str(g[0])
    pasta = BOB / "_trabalho" / "step-inside" / obra / "interiores"
    saida = pasta / "_resumo.json"
    pasta.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump({"pecas": disp["pecas"], "catalogo": cat, "modelos": modelos, "divisoes": disp["divisoes"],
                   "vistas": disp.get("vistas", []), "blend": str(blend.parent / "visita_interiores.blend"),
                   "blend_ar": str(blend.parent / "visita_interiores_ar.blend"), "paleta": 8,
                   "pasta": str(pasta), "saida": str(saida), "render": not a.sem_render}, fh, ensure_ascii=False)
        rp = fh.name
    from ferramentas.comum import correr_blender
    code, out = correr_blender(AQUI / "blender_interiores.py", [rp], blend=blend)
    Path(rp).unlink(missing_ok=True)
    if code or "INTERIORES_OK" not in out:
        print(out[-4000:])
        raise SystemExit("interiores: o Blender falhou")
    r = comum.ler_json(saida)
    avisos = [f"{c['peca']} toca em {', '.join(c['com'])}" for c in r["choques_paredes"]]
    avisos += [f"{c['peca']} sai {c['m']:.2f} m da divisão {c['divisao']}" for c in r["fora_da_divisao"]]
    avisos += [f"{c['pecas'][0]} e {c['pecas'][1]} sobrepõem-se {c['m'][0]:.2f} × {c['m'][1]:.2f} m" for c in r["sobrepostas"]]
    avisos += [f"{p}: sem pavimento por baixo" for p in r["sem_chao"]]
    resumo = {"obra": obra, "estado": disp.get("estado", "TESTE"), "pecas": len(r["pecas"]),
              "triangulos": r["triangulos_total"], "materiais": r["materiais_interiores"], "avisos": avisos,
              "modelos": r["modelos"], "detalhe": r["pecas"], "renders": r.get("renders", []),
              "ar": {"triangulos": r["ar"]["triangulos"], "materiais": r["ar"]["materiais"],
                     "nota": "cópia leve para o telemóvel (visita_interiores_ar.blend): cada peça reduzida ao ar_tris do "
                             "catálogo, cores numa paleta de poucos materiais, sem as texturas dos móveis; "
                             "python step-inside/ferramentas/ar/ar.py <visita.json> --interiores"} if r.get("ar") else None}
    (vp.parent / "interiores_resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1) + "\n",
                                                      encoding="utf-8", newline="\n")
    print(f"{len(r['pecas'])} peças, {r['triangulos_total']} triângulos, {r['materiais_interiores']} materiais")
    if r.get("ar"):
        print(f"cópia para o AR: {r['ar']['triangulos']} triângulos, {len(r['ar']['materiais'])} materiais")
    for x in avisos:
        print("  AVISO", x)
    print(f"renders: {pasta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
