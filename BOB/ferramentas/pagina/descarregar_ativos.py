"""Download the client page's CC0 assets from Poly Haven (public domain, commercial use free; user 2026-11-18:
«Sim, podes») into <pasta>/<id>/ plus manifesto.json (source, licence, authors, real size, polygons, files).
Textures: Diffuse, nor_gl, Rough (jpg). Models: glTF with its files. Used by ativos.py (casa_blender.py --ativos).
Skies (CEUS, .hdr at the listed resolutions): the Step Inside VR sky (Phase 8; user 2026-11-26: «então descarrega»).
Never in Git (big binaries): BOB/_trabalho/assets/polyhaven here; D:/BOB-posto/assets on the home render station.

    python ferramentas/pagina/descarregar_ativos.py [pasta] [resolução 2k]      (no arguments: the standard set)
    python ferramentas/pagina/descarregar_ativos.py --ceus [pasta]               (only the skies)
"""
import json
import sys
import urllib.request
from pathlib import Path

TEXTURAS = ["japanese_cedar_planks", "oak_wood_planks", "wood_floor_deck", "painted_plaster_wall", "concrete_floor_02",
            "rough_linen", "velour_velvet", "leafy_grass", "gravel_floor_02", "asphalt_02", "marble_tiles", "marble_01",
            "oak_veneer_01", "wood_table_001"]
MODELOS = ["modern_ceiling_lamp_01", "modern_arm_chair_01", "mid_century_lounge_chair", "potted_plant_02",
           "potted_plant_04", "ceramic_vase_01", "ceramic_vase_02", "ceramic_vase_04", "modern_wooden_cabinet",
           "coffee_table_round_01"]
# the VR sky: partly cloudy, its sun about 38 degrees up (the level's sun is 28: the nearest clear one; the 28-degree
# Kloofendal sky is misty). 8k for the dome seen in the headset, 2k for checks
CEUS = {"kloofendal_38d_partly_cloudy_puresky": ("8k", "2k")}
UA = {"User-Agent": "asset-fetch/1.0"}
so_ceus = "--ceus" in sys.argv
args = [a for a in sys.argv[1:] if a != "--ceus"]
dest = Path(args[0] if args else Path(__file__).resolve().parents[2] / "_trabalho" / "assets" / "polyhaven")
res = args[1] if len(args) > 1 else "2k"
ids_tex, ids_mod = ([], []) if so_ceus else (TEXTURAS, MODELOS)


def obter(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def gravar(url, p):
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_bytes(obter(url))
    return p.stat().st_size


manifesto = {}
mf = dest / "manifesto.json"
if mf.exists():
    manifesto = json.loads(mf.read_text(encoding="utf-8"))
for kind, ids in (("textura", ids_tex), ("modelo", ids_mod)):
    for aid in ids:
        info = json.loads(obter(f"https://api.polyhaven.com/info/{aid}"))
        files = json.loads(obter(f"https://api.polyhaven.com/files/{aid}"))
        pasta = dest / aid
        tot, mapas = 0, {}
        if kind == "textura":
            for k in ("Diffuse", "nor_gl", "Rough"):
                if k in files and res in files[k]:
                    f = files[k][res]["jpg"]
                    nome = f"{k}.jpg"
                    tot += gravar(f["url"], pasta / nome)
                    mapas[k] = nome
        else:
            if "gltf" not in files:
                print("sem glTF:", aid)
                continue
            g = files["gltf"][res]["gltf"]
            tot += gravar(g["url"], pasta / Path(g["url"]).name)
            mapas["gltf"] = Path(g["url"]).name
            for rel, inc in g.get("include", {}).items():
                tot += gravar(inc["url"], pasta / rel)
        manifesto[aid] = {"tipo": kind, "fonte": f"https://polyhaven.com/a/{aid}", "licenca": "CC0",
                          "autores": list(info.get("authors", {}).keys()), "dimensoes_mm": info.get("dimensions"),
                          "poligonos": info.get("polycount"), "resolucao": res, "ficheiros": mapas, "bytes": tot}
        print(kind, aid, round(tot / 1e6, 1), "MB", info.get("dimensions"), info.get("polycount"))
        mf.write_text(json.dumps(manifesto, indent=1, ensure_ascii=False), encoding="utf-8")   # after each one
for aid, resolucoes in CEUS.items():
    info = json.loads(obter(f"https://api.polyhaven.com/info/{aid}"))
    files = json.loads(obter(f"https://api.polyhaven.com/files/{aid}"))
    pasta = dest / aid
    tot, mapas = 0, {}
    for r in resolucoes:
        f = files["hdri"][r]["hdr"]
        mapas[r] = f"{aid}_{r}.hdr"
        tot += gravar(f["url"], pasta / mapas[r])
    manifesto[aid] = {"tipo": "ceu", "fonte": f"https://polyhaven.com/a/{aid}", "licenca": "CC0",
                      "autores": list(info.get("authors", {}).keys()), "resolucao": list(resolucoes),
                      "balanco_brancos_k": info.get("whitebalance"), "ficheiros": mapas, "bytes": tot}
    print("ceu", aid, round(tot / 1e6, 1), "MB")
    mf.write_text(json.dumps(manifesto, indent=1, ensure_ascii=False), encoding="utf-8")
