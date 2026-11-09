"""Step Inside Phase 7 — AR assets for phones (hub tasks 82, 83, 157): GLB for Android Scene Viewer and USDZ for
iPhone Quick Look, light enough for the phone (spec §8, §12.1).

    python step-inside/ferramentas/ar/ar.py step-inside/projetos-teste/<obra>/visita.json [--textura-max 1024]

Two variants per house, from the visit model (blender_ar.py):
  casa     the house alone at 1:1 — placed on the real ground, the client walks around it
  maquete  the house with the terrain within raio_terreno_m — viewed scaled down on a table
Budget (Google Scene Viewer reference, spec §12.1): ideal 30–50k triangles, at most 100k; textures ≤ 2048; file
about 10 MB. Each file is re-opened in a clean Blender (scale, axes, materials, textures).

Outputs. Local only (_trabalho/step-inside/<obra>/ar/): the GLB and USDZ files. Committed
(step-inside/projetos-teste/<obra>/): ar_resumo.json, ar_relatorio.md. Exit code: 0 PASS / WARNING, 1 FAIL.
"""
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "fontes"))
sys.path.insert(0, str(AQUI.parent / "materiais"))
sys.path.insert(0, str(AQUI.parent / "exportar"))
import comum  # noqa: E402
import materiais  # noqa: E402
from exportar import reimportar  # noqa: E402

BOB = comum.BOB
TRI_IDEAL, TRI_MAX = 50_000, 100_000
MB_ALVO, MB_MAX = 10.0, 25.0


def ocultos(construtor):
    """IDs of materials not seen from outside (catalogue 'visivel': false), unless the variant says it is visible."""
    cat, mp = materiais.ler(construtor)
    mestres = {m["id"]: m for m in cat["materiais"]}
    out = set()
    for e in materiais.resolver(cat, mp).values():
        m = mestres[e["mestre"]]
        var = (m.get("variantes") or {}).get(e["variante"], {})
        if not var.get("visivel", m["visivel"]):
            out.add(e["id"])
    return sorted(out)


def avaliar(v, ficheiros, reimp):
    falhas, avisos = [], []
    t = v["triangulos"]
    if t > TRI_MAX:
        falhas.append(f"{v['variante']}: {t} triângulos (máximo {TRI_MAX})")
    elif t > TRI_IDEAL:
        avisos.append(f"{v['variante']}: {t} triângulos (ideal até {TRI_IDEAL})")
    if v["variante"] == "casa" and v.get("z_min", 0) < -0.25:
        falhas.append(f"casa: o modelo desce {-v['z_min']:.2f} m abaixo do pavimento: no telemóvel fica a flutuar")
    if v["textura_maior"] > 2048:
        falhas.append(f"{v['variante']}: textura de {v['textura_maior']} px (máximo 2048)")
    for fmt, f in ficheiros.items():
        mb = f["bytes"] / 1e6
        if mb > MB_MAX:
            falhas.append(f"{v['variante']} {fmt}: {mb:.1f} MB (máximo {MB_MAX:g})")
        elif mb > MB_ALVO:
            avisos.append(f"{v['variante']} {fmt}: {mb:.1f} MB (alvo ≈ {MB_ALVO:g} MB)")
        r = reimp.get(fmt) or {}
        if r.get("erro"):
            falhas.append(f"{v['variante']} {fmt}: não reabre")
            continue
        if abs(r["triangulos"] - t) > 0.01 * t:
            falhas.append(f"{v['variante']} {fmt}: {r['triangulos']} triângulos ao reabrir (eram {t})")
        if any(abs(a - b) > 0.01 for a, b in zip(r["dimensoes"], v["dimensoes"])):
            falhas.append(f"{v['variante']} {fmt}: dimensões {r['dimensoes']} ao reabrir (eram {v['dimensoes']}): escala ou eixos")
        if r.get("imagens_em_falta"):
            falhas.append(f"{v['variante']} {fmt}: texturas em falta")
    return falhas, avisos


def main():
    comum.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("visita")
    ap.add_argument("--textura-max", type=int, default=1024)
    ap.add_argument("--raio-terreno", type=float, default=20.0)
    a = ap.parse_args()
    vp = Path(a.visita).resolve()
    decl = comum.ler_json(vp)
    obra = decl["obra"]
    blend = BOB / "_trabalho" / "step-inside" / obra / "visita" / "visita.blend"
    if not blend.exists():
        raise SystemExit("primeiro o modelo de visita: python step-inside/ferramentas/visita/visita.py " + a.visita)
    pasta = BOB / "_trabalho" / "step-inside" / obra / "ar"
    pasta.mkdir(parents=True, exist_ok=True)
    oc = ocultos(decl.get("construtor", "discovercasa"))
    from ferramentas.comum import correr_blender
    variantes, falhas, avisos = [], [], []
    for var in ("casa", "maquete"):
        glb, usdz, res = pasta / f"{obra}_ar_{var}.glb", pasta / f"{obra}_ar_{var}.usdz", pasta / f"_{var}.json"
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump({"variante": var, "ocultos": oc, "raio_terreno_m": a.raio_terreno, "textura_max": a.textura_max,
                       "glb": str(glb), "usdz": str(usdz), "resumo": str(res)}, fh)
            rp = fh.name
        code, out = correr_blender(AQUI / "blender_ar.py", [rp], blend=blend)
        Path(rp).unlink(missing_ok=True)
        if code or "AR_OK" not in out:
            print(out[-3000:])
            raise SystemExit(f"AR ({var}) falhou")
        v = comum.ler_json(res)
        fich = {fmt: {"ficheiro": p.name, "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                for fmt, p in (("glb", glb), ("usdz", usdz))}
        cam = {"loc": [-1.6 * max(v["dimensoes"][:2]), -2.0 * max(v["dimensoes"][:2]), 1.1 * max(v["dimensoes"][:2])],
               "rot": [1.15, 0.0, -0.67], "lente": 28}
        reimp = {fmt: reimportar(pasta / f["ficheiro"], fmt, cam, Path("_nao_existe"), pasta) for fmt, f in fich.items()}
        fa, av = avaliar(v, fich, reimp)
        falhas += fa
        avisos += av
        v["ficheiros"] = fich
        v["reimportacao"] = {f: {k: r.get(k) for k in ("triangulos", "dimensoes", "materiais", "imagens", "imagens_em_falta", "erro")}
                             for f, r in reimp.items()}
        variantes.append(v)
    estado = "FAIL" if falhas else ("WARNING" if avisos else "PASS")
    resumo = {"obra": obra, "resultado": estado, "motivos": falhas + avisos, "textura_max": a.textura_max,
              "raio_terreno_m": a.raio_terreno, "materiais_ocultos": oc, "variantes": variantes,
              "orcamento": {"triangulos_ideal": TRI_IDEAL, "triangulos_max": TRI_MAX, "textura_max_px": 2048,
                            "mb_alvo": MB_ALVO, "mb_max": MB_MAX}}
    comum.escrever_json(vp.parent / "ar_resumo.json", resumo)
    (vp.parent / "ar_relatorio.md").write_text(relatorio(resumo, decl), encoding="utf-8")
    print(f"{estado}: " + "; ".join((falhas + avisos)[:6]))
    print(f"ficheiros AR: {pasta}")
    sys.exit(1 if estado == "FAIL" else 0)


def _mb(b):
    return f"{b / 1e6:.1f}".replace(".", ",") + " MB"


def relatorio(r, decl):
    L = [f"# AR no telemóvel · {decl.get('nome', r['obra'])}", "", f"**Resultado: {r['resultado']}**", ""]
    L += [f"- {m}" for m in r["motivos"]] + [""]
    L += ["Gerado por `step-inside/ferramentas/ar/ar.py` a partir do modelo de visita. Os ficheiros ficam só no PC "
          "(`_trabalho/step-inside/<obra>/ar/`).", "",
          f"Orçamento (Google Scene Viewer, especificação §12.1): ideal até {TRI_IDEAL:,} triângulos, máximo "
          f"{TRI_MAX:,}; texturas até 2048 px; ficheiro ≈ {MB_ALVO:g} MB.".replace(",", " "), "",
          "| Variante | Para quê | Triângulos (antes) | Materiais | Maior textura | GLB | USDZ | Dimensões (m) |",
          "|---|---|---|---|---|---|---|---|"]
    para = {"casa": "1:1 no terreno real, para andar à volta", "maquete": "com o terreno, em ponto pequeno sobre uma mesa"}
    for v in r["variantes"]:
        L.append(f"| {v['variante']} | {para[v['variante']]} | {v['triangulos']} ({v['triangulos_antes_de_simplificar']}) | "
                 f"{len(v['materiais'])} | {v['textura_maior']} px | {_mb(v['ficheiros']['glb']['bytes'])} | "
                 f"{_mb(v['ficheiros']['usdz']['bytes'])} | {v['dimensoes']} |")
    L += ["", "**Simplificação:**",
          "- tiram-se as camadas que não se veem de fora (" + ", ".join(f"`{m}`" for m in r["materiais_ocultos"]) + ");",
          "- junta-se um objeto por material;",
          "- juntam-se as faces no mesmo plano;",
          f"- as texturas descem a {r['textura_max']} px (cor) e {max(256, r['textura_max'] // 2)} px (relevo e "
          "rugosidade), em JPEG.",
          "",
          "**Sem sombras gravadas:** o Scene Viewer e o Quick Look desenham-nas.",
          "",
          "**Origem:** centro da planta da casa, no pavimento acabado do rés do chão (escala real em metros).",
          "",
          "**Fundação na versão casa:** o telemóvel pousa o ponto mais baixo do modelo no chão real, por isso a "
          "fundação indicativa é cortada 0,2 m abaixo do pavimento e o soco fica visível.",
          "",
          "**Reabertos num Blender limpo** (triângulos, dimensões, texturas):", ""]
    for v in r["variantes"]:
        for f, x in v["reimportacao"].items():
            L.append(f"- {v['variante']} {f}: " + (f"não reabre ({x['erro'][-120:]})" if x.get("erro") else
                     f"{x['triangulos']} triângulos, {x['dimensoes']} m, {x['imagens']} texturas, "
                     f"{len(x['imagens_em_falta'] or [])} em falta"))
    L += ["", "**Por testar:** abrir em telemóveis reais (Scene Viewer num Android, Quick Look num iPhone) e medir o "
          "tempo de carregamento e a qualidade ao lado das fotos da casa construída (tarefas 84 e 158).", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
