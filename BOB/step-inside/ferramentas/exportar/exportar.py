"""Step Inside Phase 3 — normalised export, manifest and re-import test (hub tasks 63, 64, 65).

    python step-inside/ferramentas/exportar/exportar.py step-inside/projetos-teste/<obra>/visita.json [--uma-vez]

Starts from the visit model of visita.py (local .blend). Exports it twice (FBX for Unreal, GLB for Android, USDZ for
iPhone; blender_exportar.py), compares the two runs byte for byte (determinism; where a format writes a timestamp, the
re-imported content is compared instead), re-imports every file in a fresh Blender (blender_reimportar.py) and checks
geometry, scale and axes, material IDs, textures and a flat render against the source. Writes manifest.json (spec §4.3).

Outputs. Local only (_trabalho/step-inside/<obra>/export/): the files, their textures and manifest.json (it holds the
real site origin). Committed (step-inside/projetos-teste/<obra>/): export_resumo.json and export_relatorio.md (no
coordinates). Exit code: 0 PASS / WARNING, 2 NEEDS_HUMAN_REVIEW, 1 FAIL.
"""
import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "fontes"))
import comum  # noqa: E402
import esquema  # noqa: E402

BOB = comum.BOB
ESQUEMA_MANIFEST = BOB / "step-inside" / "schema" / "manifest.schema.json"
UNREAL_ALVO = "5.8 (a confirmar na Fase 4)"
SISTEMAS = {"fonte": "Blender: metros, Z para cima, X para este, Y para norte (origem local do terreno)",
            "fbx": "FBX: metros (FBX_SCALE_UNITS), eixo -Z para a frente, Y para cima; no Unreal importar com 'Convert Scene'",
            "glb": "glTF 2.0: metros, +Y para cima (norma)", "usdz": "USD: metersPerUnit 1, upAxis Y"}
FINALIDADE = {"fbx": "Unreal (Fases 4–5)", "glb": "AR Android / visualizador 3D", "usdz": "AR Quick Look (iPhone)",
              "texture": "textura PBR do FBX (ficheiro separado, spec §4.2)", "render": "imagem de referência do teste"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def blender(script, args, blend=None, factory=False):
    from ferramentas.comum import correr_blender
    return correr_blender(script, args, blend=blend, factory=factory)


def exportar(blend, pasta, nome):
    if pasta.exists():
        shutil.rmtree(pasta)
    pasta.mkdir(parents=True)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump({"saida": str(pasta), "nome": nome, "resumo": str(pasta / "_fonte.json")}, fh)
        rp = fh.name
    code, out = blender(AQUI / "blender_exportar.py", [rp], blend=blend)
    Path(rp).unlink(missing_ok=True)
    if code or "EXPORT_OK" not in out:
        print(out[-3000:])
        raise SystemExit("exportação falhou")
    return comum.ler_json(pasta / "_fonte.json")


def reimportar(ficheiro, fmt, camera, referencia, pasta):
    res = pasta / f"_reimport_{fmt}.json"
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump({"ficheiro": str(ficheiro), "formato": fmt, "camera": camera, "render": str(pasta / f"_reimport_{fmt}.png"),
                   "referencia": str(referencia), "resumo": str(res)}, fh)
        rp = fh.name
    code, out = blender(AQUI / "blender_reimportar.py", [rp], factory=True)
    Path(rp).unlink(missing_ok=True)
    if code or "REIMPORT_OK" not in out or not res.exists():
        return {"erro": (out or "")[-600:]}
    return comum.ler_json(res)


def comparar(ref, r, fmt):
    """Problems of one re-import against the source: (falhas, avisos)."""
    falhas, avisos = [], []
    if r.get("erro"):
        return [f"{fmt}: não reabre ({r['erro'][-200:]})"], []
    if r["triangulos"] < ref["triangulos"] * 0.99:
        falhas.append(f"{fmt}: perdeu geometria ({r['triangulos']} de {ref['triangulos']} triângulos)")
    elif r["triangulos"] > ref["triangulos"] * 1.01:
        avisos.append(f"{fmt}: {r['triangulos']} triângulos contra {ref['triangulos']}")
    erro_caixa = max(max(abs(a - b) for a, b in zip(r["caixa_min"], ref["caixa_min"])),
                     max(abs(a - b) for a, b in zip(r["caixa_max"], ref["caixa_max"])))
    r["erro_caixa_m"] = round(erro_caixa, 4)
    if erro_caixa > 0.01:
        falhas.append(f"{fmt}: escala, eixos ou posição errados (caixa {r['dimensoes']} contra {ref['dimensoes']}, "
                      f"diferença {erro_caixa:.3f} m)")
    faltam = sorted(set(m for m in ref["materiais"] if m.startswith("MAT_")) - set(r["materiais"]))
    if faltam:
        falhas.append(f"{fmt}: material IDs perdidos: {', '.join(faltam[:6])}")
    if r.get("imagens_em_falta"):
        falhas.append(f"{fmt}: texturas em falta: {', '.join(r['imagens_em_falta'][:4])}")
    if r["imagens"] == 0 and ref["imagens"]:
        falhas.append(f"{fmt}: sem texturas")
    im = r.get("imagem") or {}
    if im:
        if im["silhueta_diferente"] > 0.01:
            falhas.append(f"{fmt}: a silhueta muda em {100 * im['silhueta_diferente']:.1f} % da imagem")
        elif im["pixeis_diferentes"] > 0.05:
            avisos.append(f"{fmt}: {100 * im['pixeis_diferentes']:.1f} % dos píxeis mudam de cor (materiais / texturas)")
    return falhas, avisos


def main():
    comum.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("visita")
    ap.add_argument("--uma-vez", action="store_true", help="exportar só uma vez (sem o teste de determinismo)")
    a = ap.parse_args()
    vp = Path(a.visita).resolve()
    decl = comum.ler_json(vp)
    obra = decl["obra"]
    blend = BOB / "_trabalho" / "step-inside" / obra / "visita" / "visita.blend"
    if not blend.exists():
        raise SystemExit("primeiro o modelo de visita: python step-inside/ferramentas/visita/visita.py " + a.visita)
    base = BOB / "_trabalho" / "step-inside" / obra / "export"
    nome = f"{obra}_visita"
    A = exportar(blend, base / "a", nome)
    falhas, avisos, det = [], [], {}
    if not a.uma_vez:
        exportar(blend, base / "b", nome)
        for fmt, f in A["ficheiros"].items():
            det[fmt] = sha256(base / "a" / f) == sha256(base / "b" / f)
    ref = A["referencia"]
    reimp = {}
    for fmt, f in A["ficheiros"].items():
        reimp[fmt] = reimportar(base / "a" / f, fmt, A["camera"], base / "a" / "_ref.png", base / "a")
        fa, av = comparar(ref, reimp[fmt], fmt)
        falhas += fa
        avisos += av
    for fmt, igual in det.items():
        if not igual:
            # same input, different bytes: acceptable only when the re-import of the second run gives the same content
            rb = reimportar(base / "b" / A["ficheiros"][fmt], fmt, A["camera"], base / "a" / "_ref.png", base / "b")
            chave = ("triangulos", "caixa_min", "caixa_max", "materiais", "imagens")
            if any(rb.get(k) != reimp[fmt].get(k) for k in chave):
                falhas.append(f"{fmt}: duas exportações do mesmo modelo dão conteúdo diferente")
            else:
                avisos.append(f"{fmt}: os bytes mudam entre exportações (data no ficheiro), o conteúdo é igual")
                det[fmt] = "conteudo"
    estado = "FAIL" if falhas else ("WARNING" if avisos else "PASS")

    # manifest (local: it holds the real site origin)
    pasta = base / "a"
    tl = BOB / "_trabalho" / "step-inside" / obra / "terreno" / "terreno_local.json"
    origem = comum.ler_json(tl)["origem"] if tl.exists() else None
    tr = BOB / "step-inside" / "projetos-teste" / obra / "terreno_resumo.json"
    terreno = None
    if tr.exists():
        t = comum.ler_json(tr)["terreno"]
        terreno = {k: {"valor": t[k]["valor"], "estado": t[k]["estado"]} for k in ("fonte", "crs", "datum_vertical", "data_levantamento")}
    vr = comum.ler_json(BOB / "step-inside" / "projetos-teste" / obra / "visita_resumo.json")
    git = subprocess.run(["git", "-C", str(BOB), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    agora = datetime.datetime.now(datetime.timezone.utc)
    mats = sorted(m for m in ref["materiais"] if m.startswith("MAT_"))
    assets = []
    for p in sorted(pasta.rglob("*")):
        if not p.is_file() or p.name.startswith("_") or p.name == "manifest.json":
            continue
        ext = p.suffix.lower().lstrip(".")
        tipo = ext if ext in ("fbx", "glb", "usdz") else ("texture" if ext in ("jpg", "jpeg", "png") else None)
        if not tipo:
            continue
        assets.append({"path": str(p.relative_to(pasta)).replace("\\", "/"), "type": tipo, "size_bytes": p.stat().st_size,
                       "sha256": sha256(p), "material_ids": mats if tipo in ("fbx", "glb", "usdz") else [],
                       "version": git, "purpose": FINALIDADE[tipo]})
    manifest = {"project_id": obra, "version_id": f"{obra}-{git}-{agora:%Y%m%d%H%M}",
                "source_blend_hash": "sha256:" + sha256(blend), "export_timestamp": agora.isoformat(timespec="seconds"),
                "blender_version": A["blender"], "unreal_target_version": UNREAL_ALVO, "unit_system": "métrico (1 unidade = 1 m)",
                "coordinate_system": SISTEMAS,
                "origin_transform": {"origem_local_no_sistema_do_terreno": origem, "rotacao_casa_graus":
                                     (vr["implantacao"].get("rotacao_graus") or {}).get("valor"),
                                     "nota": "as coordenadas do modelo são locais; somar a origem para voltar ao sistema do terreno"},
                "material_catalogue": {"ficheiro": "step-inside/materiais/catalogo.json",
                                       "mapeamento": f"step-inside/materiais/mapeamentos/{vr.get('construtor', 'discovercasa')}.json"},
                "assets": assets, "warnings": falhas + avisos, "validation_status": estado,
                "validation": {"referencia": ref, "reimportacao": reimp, "determinismo": det},
                "terrain_source": terreno}
    erros = esquema.validar(manifest, comum.ler_json(ESQUEMA_MANIFEST))
    if erros:
        falhas += [f"manifest: {e}" for e in erros]
        estado = manifest["validation_status"] = "FAIL"
    comum.escrever_json(pasta / "manifest.json", manifest)

    # committed summary: no origin, no absolute paths
    resumo = {k: manifest[k] for k in ("project_id", "version_id", "source_blend_hash", "export_timestamp", "blender_version",
                                        "unreal_target_version", "unit_system", "coordinate_system", "validation_status",
                                        "terrain_source")}
    resumo["origin_transform"] = {"origem_local": "só no PC (manifest.json local)",
                                  "rotacao_casa_graus": manifest["origin_transform"]["rotacao_casa_graus"]}
    resumo["assets"] = [{k: v for k, v in x.items() if k != "version"} for x in assets if x["type"] != "texture"]
    resumo["texturas"] = {"ficheiros": sum(1 for x in assets if x["type"] == "texture"),
                          "bytes": sum(x["size_bytes"] for x in assets if x["type"] == "texture")}
    resumo["warnings"] = manifest["warnings"]
    resumo["validation"] = {"referencia": {k: v for k, v in ref.items() if k not in ("caixa_min", "caixa_max")},
                            "reimportacao": {f: {k: v for k, v in r.items() if k not in ("caixa_min", "caixa_max")}
                                             for f, r in reimp.items()}, "determinismo": det}
    saida = vp.parent
    comum.escrever_json(saida / "export_resumo.json", resumo)
    (saida / "export_relatorio.md").write_text(relatorio(resumo, decl), encoding="utf-8")
    print(f"{estado}: " + "; ".join((falhas + avisos)[:6]))
    print(f"exportação local: {pasta}")
    sys.exit({"PASS": 0, "WARNING": 0, "NEEDS_HUMAN_REVIEW": 2, "FAIL": 1}[estado])


def _mb(b):
    return f"{b / 1e6:.1f}".replace(".", ",") + " MB"


def relatorio(r, decl):
    ref = r["validation"]["referencia"]
    L = [f"# Exportação · {decl.get('nome', r['project_id'])}", "", f"**Resultado: {r['validation_status']}**", ""]
    L += [f"- {w}" for w in r["warnings"]] + [""]
    L += ["Gerado por `step-inside/ferramentas/exportar/exportar.py` a partir do modelo de visita. Os ficheiros e o "
          "`manifest.json` completo ficam só no PC (`_trabalho/step-inside/<obra>/export/a/`).", "",
          f"- Versão: `{r['version_id']}` · Blender {r['blender_version']} · Unreal alvo {r['unreal_target_version']}",
          f"- Fonte: {ref['objetos']} objetos, {ref['triangulos']} triângulos, {len(ref['materiais'])} materiais, "
          f"{ref['imagens']} imagens; caixa {ref['dimensoes']} m", "",
          "| Ficheiro | Para quê | Tamanho | SHA-256 | Determinístico |", "|---|---|---|---|---|"]
    for x in r["assets"]:
        d = r["validation"]["determinismo"].get(x["type"])
        L.append(f"| `{x['path']}` | {x['purpose']} | {_mb(x['size_bytes'])} | `{x['sha256'][:12]}…` | "
                 f"{'sim (bytes iguais)' if d is True else ('conteúdo igual' if d == 'conteudo' else ('—' if d is None else 'NÃO'))} |")
    L.append(f"| texturas do FBX | {FINALIDADE['texture']} | {_mb(r['texturas']['bytes'])} | {r['texturas']['ficheiros']} ficheiros | — |")
    L += ["", "## Reimportação (Blender limpo) e comparação", "",
          "| Formato | Objetos | Triângulos | Caixa (m) | Erro da caixa | Materiais | Imagens (em falta) | Píxeis diferentes | Silhueta |",
          "|---|---|---|---|---|---|---|---|---|"]
    for f, x in r["validation"]["reimportacao"].items():
        if x.get("erro"):
            L.append(f"| {f} | não reabre | | | | | | | |")
            continue
        im = x.get("imagem") or {}
        L.append(f"| {f} | {x['objetos']} | {x['triangulos']} | {x['dimensoes']} | {x.get('erro_caixa_m', '—')} | "
                 f"{len(x['materiais'])} | {x['imagens']} ({len(x['imagens_em_falta'])}) | "
                 f"{100 * im.get('pixeis_diferentes', 0):.1f} % | {100 * im.get('silhueta_diferente', 0):.2f} % |")
    L += ["", "## Sistemas de coordenadas", ""] + [f"- **{k}**: {v}" for k, v in r["coordinate_system"].items()]
    L += ["", "A imagem de comparação usa a mesma câmara, luz plana e a cor das texturas: mede se a geometria, a "
          "posição e os materiais chegam iguais, não o aspeto final.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
