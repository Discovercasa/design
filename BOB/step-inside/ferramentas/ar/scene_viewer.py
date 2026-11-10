"""Make a GLB acceptable to Google Scene Viewer (Android AR) and check it against Scene Viewer's own validator rules.

Why (team note on hub task 84, 2026-11-10: «No Android quando se tenta abrir o AR ele anima a transição durante uma
fração de segundo mas depois volta à página do Hub»): Blender's glTF exporter wrote `KHR_materials_specular` for the
ambient-occlusion film (specular 0, version 6, 2026-11-09). Scene Viewer's validator treats any extension it does not
support as an ERROR (`UNSUPPORTED_GLTF_EXTENSION_USED`, https://developers.google.com/ar/develop/scene-viewer), so the
Google app could not show the model and sent Chrome back to the fallback page (the hub). Quick Look (USDZ) and the
browser viewer (three.js) accept the extension, which is why only Android failed.

Rules (Scene Viewer validator, read 2026-11-10):
  ERROR    unsupported extension (supported: KHR_materials_pbrSpecularGlossiness, KHR_materials_unlit,
           KHR_texture_transform); vertex colours; morph targets; more than 1 animation; primitive modes other than
           4/5/6; more than 1 UV set per mesh (hard limit); file over 15 MB
  WARNING  more than 10 materials (2 of them alpha); textures over 2048 px; more than 100 000 triangles; over 10 MB

    python step-inside/ferramentas/ar/scene_viewer.py FILE.glb [...]    check (and clean) GLB files in place
"""
import json
import struct
import sys
from pathlib import Path

SUPORTADAS = {"KHR_materials_pbrSpecularGlossiness", "KHR_materials_unlit", "KHR_texture_transform"}
MATERIAIS_MAX, ALFA_MAX, TEXTURA_MAX, TRI_MAX = 10, 2, 2048, 100_000
MB_AVISO, MB_ERRO = 10.0, 15.0


def ler(dados):
    """GLB bytes -> (gltf dict, BIN chunk bytes or b'')."""
    magia, versao, total = struct.unpack_from("<4sII", dados, 0)
    if magia != b"glTF" or versao != 2:
        raise ValueError("não é um GLB 2.0")
    n, tipo = struct.unpack_from("<I4s", dados, 12)
    if tipo != b"JSON":
        raise ValueError("o primeiro bloco do GLB não é JSON")
    gltf = json.loads(dados[20:20 + n])
    resto, binario = 20 + n, b""
    if resto < min(total, len(dados)):
        nb, tb = struct.unpack_from("<I4s", dados, resto)
        if tb == b"BIN\x00":
            binario = dados[resto + 8:resto + 8 + nb]
    return gltf, binario


def escrever(gltf, binario):
    """(gltf dict, BIN bytes) -> GLB bytes, chunks padded to 4 bytes (JSON with spaces, BIN with zeros)."""
    j = json.dumps(gltf, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    j += b" " * (-len(j) % 4)
    partes = [struct.pack("<I4s", len(j), b"JSON"), j]
    if binario:
        b = binario + b"\x00" * (-len(binario) % 4)
        partes += [struct.pack("<I4s", len(b), b"BIN\x00"), b]
    corpo = b"".join(partes)
    return struct.pack("<4sII", b"glTF", 2, 12 + len(corpo)) + corpo


def _tirar_extensoes(no, tiradas):
    """Remove unsupported entries from every 'extensions' object in the glTF tree (in place)."""
    if isinstance(no, dict):
        ext = no.get("extensions")
        if isinstance(ext, dict):
            for k in [k for k in ext if k not in SUPORTADAS]:
                tiradas.add(k)
                del ext[k]
            if not ext:
                del no["extensions"]
        for v in no.values():
            _tirar_extensoes(v, tiradas)
    elif isinstance(no, list):
        for v in no:
            _tirar_extensoes(v, tiradas)


def _dimensoes_imagem(d):
    if d[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", d[16:24])
    i = 2
    while i + 9 < len(d):   # JPEG: walk the markers to the start-of-frame
        if d[i] != 0xFF:
            i += 1
            continue
        if d[i + 1] in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", d[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack(">H", d[i + 2:i + 4])[0]
    return 0, 0


def verificar(gltf, binario, tamanho):
    """Scene Viewer validator rules -> (erros, avisos), in Portuguese for the reports."""
    erros, avisos = [], []
    usadas = set(gltf.get("extensionsUsed", [])) | set(gltf.get("extensionsRequired", []))
    for e in sorted(usadas - SUPORTADAS):
        erros.append(f"extensão {e} não suportada pelo Scene Viewer")
    prims = [p for m in gltf.get("meshes", []) for p in m.get("primitives", [])]
    if any(a.startswith("COLOR_") for p in prims for a in p.get("attributes", {})):
        erros.append("cores por vértice (o Scene Viewer não aceita)")
    if any(p.get("targets") for p in prims):
        erros.append("morph targets (o Scene Viewer não aceita)")
    if len(gltf.get("animations", [])) > 1:
        erros.append(f"{len(gltf['animations'])} animações (máximo 1)")
    if any(p.get("mode", 4) not in (4, 5, 6) for p in prims):
        erros.append("primitivas que não são triângulos")
    if any(sum(a.startswith("TEXCOORD_") for a in p.get("attributes", {})) > 1 for p in prims):
        erros.append("mais de um conjunto de UV numa malha (limite do Scene Viewer: 1)")
    mb = tamanho / 1e6
    if mb > MB_ERRO:
        erros.append(f"{mb:.1f} MB (máximo do Scene Viewer: {MB_ERRO:g} MB)")
    elif mb > MB_AVISO:
        avisos.append(f"{mb:.1f} MB (recomendado pelo Scene Viewer: até {MB_AVISO:g} MB)")
    mats = gltf.get("materials", [])
    alfa = sum(m.get("alphaMode", "OPAQUE") != "OPAQUE" for m in mats)
    if len(mats) > MATERIAIS_MAX or alfa > ALFA_MAX:
        avisos.append(f"{len(mats)} materiais, {alfa} com transparência (recomendado pelo Scene Viewer: até "
                      f"{MATERIAIS_MAX}, {ALFA_MAX} com transparência)")
    acc = gltf.get("accessors", [])
    tri = sum(acc[p["indices"]]["count"] // 3 if "indices" in p else acc[p["attributes"]["POSITION"]]["count"] // 3
              for p in prims)
    if tri > TRI_MAX:
        avisos.append(f"{tri} triângulos (recomendado pelo Scene Viewer: até {TRI_MAX})")
    for im in gltf.get("images", []):
        if "bufferView" in im and binario:
            bv = gltf["bufferViews"][im["bufferView"]]
            o = bv.get("byteOffset", 0)
            w, h = _dimensoes_imagem(binario[o:o + bv["byteLength"]])
            if max(w, h) > TEXTURA_MAX:
                avisos.append(f"textura {im.get('name', '?')} com {w}×{h} px (máximo recomendado {TEXTURA_MAX})")
    return erros, avisos


def preparar(caminho):
    """Clean a GLB in place for Scene Viewer and check it. Returns {extensoes_tiradas, erros, avisos}.
    Unsupported extensions only in extensionsUsed are dropped (the model stays valid glTF without them); one in
    extensionsRequired cannot be dropped safely and stays as an error."""
    p = Path(caminho)
    gltf, binario = ler(p.read_bytes())
    obrigatorias = set(gltf.get("extensionsRequired", [])) - SUPORTADAS
    tiradas = set()
    if not obrigatorias:
        _tirar_extensoes(gltf, tiradas)
        usadas = [e for e in gltf.get("extensionsUsed", []) if e in SUPORTADAS]
        tiradas |= set(gltf.get("extensionsUsed", [])) - set(usadas)
        if usadas:
            gltf["extensionsUsed"] = usadas
        else:
            gltf.pop("extensionsUsed", None)
        if tiradas:
            p.write_bytes(escrever(gltf, binario))
    erros, avisos = verificar(gltf, binario, p.stat().st_size)
    return {"extensoes_tiradas": sorted(tiradas), "erros": erros, "avisos": avisos}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    mau = False
    for f in sys.argv[1:]:
        r = preparar(f)
        mau |= bool(r["erros"])
        print(f"{Path(f).name}: tiradas {r['extensoes_tiradas'] or '—'}; erros {r['erros'] or '—'}; avisos {r['avisos'] or '—'}")
    sys.exit(1 if mau else 0)
