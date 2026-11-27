"""Download the client page's CC0 assets from Poly Haven (public domain, commercial use free; user 2026-11-18:
«Sim, podes») into <pasta>/<id>/ plus manifesto.json (source, licence, authors, real size, polygons, files).
Textures: Diffuse, nor_gl, Rough (jpg). Models: glTF with its files. Used by ativos.py (casa_blender.py --ativos).
Skies (CEUS, .hdr at the listed resolutions): the Step Inside VR sky (Phase 8; user 2026-11-26: «então descarrega»).
Never in Git (big binaries): BOB/_trabalho/assets/polyhaven here; D:/BOB-posto/assets on the home render station.

    python ferramentas/pagina/descarregar_ativos.py [pasta] [resolução 2k]      (no arguments: the standard set)
    python ferramentas/pagina/descarregar_ativos.py --ceus [pasta]               (only the skies)
    python ferramentas/pagina/descarregar_ativos.py --texturas=a,b [pasta] [resolução]   (only these textures)
    python ferramentas/pagina/descarregar_ativos.py --ambientcg=Marble021 [pasta] 4k     (ambientCG, CC0)
A resolution other than 2k goes to <pasta>/<id>/<res>/ (manifest key "<id>@<res>"), so the 2k set stays as it is.
Extending table, 4k veneers and marble (user 2026-11-27: «Sim, 4K»).
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
escolha = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--texturas=")), None)
args = [a for a in sys.argv[1:] if not a.startswith("--")]
dest = Path(args[0] if args else Path(__file__).resolve().parents[2] / "_trabalho" / "assets" / "polyhaven")
res = args[1] if len(args) > 1 else "2k"
ids_tex, ids_mod = ([], []) if so_ceus else (escolha.split(","), []) if escolha else (TEXTURAS, MODELOS)
if escolha:
    CEUS = {}


def obter(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def gravar(url, p):
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_bytes(obter(url))
    return p.stat().st_size


def ambientcg(ids):
    """ambientCG materials (CC0) for what Poly Haven lacks — a marble slab for the extending table (user 2026-11-27:
    «ambientCG Marble021»; Poly Haven's marble_01 is a paving of stone slabs with joints). Only the colour, normal (GL)
    and roughness JPEGs are taken from the zip, under the Poly Haven names, in <pasta>/acg_<id>/<res>/."""
    import io
    import zipfile
    mapas_acg = {"Color": "Diffuse.jpg", "NormalGL": "nor_gl.jpg", "Roughness": "Rough.jpg"}
    mf = dest / "manifesto.json"
    manifesto = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    for aid in ids:
        info = json.loads(obter(f"https://ambientcg.com/api/v2/full_json?id={aid}&include=downloadData,dimensionsData"))
        a = info["foundAssets"][0]
        alvo = f"{res.upper()}-JPG"
        f = next(d for c in a["downloadFolders"]["default"]["downloadFiletypeCategories"].values()
                 for d in c["downloads"] if d["attribute"] == alvo)
        pasta = dest / f"acg_{aid}" / res
        pasta.mkdir(parents=True, exist_ok=True)
        z = zipfile.ZipFile(io.BytesIO(obter(f["downloadLink"])))
        tot, mapas = 0, {}
        for nome in z.namelist():
            for chave, saida in mapas_acg.items():
                if nome.endswith(f"_{chave}.jpg"):
                    dados = z.read(nome)
                    (pasta / saida).write_bytes(dados)
                    tot += len(dados)
                    mapas[chave] = saida
        manifesto[f"acg:{aid}@{res}"] = {"tipo": "textura", "fonte": f"https://ambientcg.com/view?id={aid}",
                                         "licenca": "CC0", "dimensoes": a.get("dimensionX") and
                                         [a.get("dimensionX"), a.get("dimensionY")], "resolucao": res,
                                         "ficheiros": mapas, "bytes": tot}
        print("ambientCG", aid, round(tot / 1e6, 1), "MB", sorted(mapas))
    mf.write_text(json.dumps(manifesto, indent=1, ensure_ascii=False), encoding="utf-8")


acg = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ambientcg=")), None)
if acg:
    ambientcg(acg.split(","))
    sys.exit(0)


manifesto = {}
mf = dest / "manifesto.json"
if mf.exists():
    manifesto = json.loads(mf.read_text(encoding="utf-8"))
for kind, ids in (("textura", ids_tex), ("modelo", ids_mod)):
    for aid in ids:
        info = json.loads(obter(f"https://api.polyhaven.com/info/{aid}"))
        files = json.loads(obter(f"https://api.polyhaven.com/files/{aid}"))
        pasta = dest / aid if res == "2k" else dest / aid / res
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
        manifesto[aid if res == "2k" else f"{aid}@{res}"] = {"tipo": kind, "fonte": f"https://polyhaven.com/a/{aid}", "licenca": "CC0",
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
