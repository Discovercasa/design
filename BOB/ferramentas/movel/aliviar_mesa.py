"""Lighten the extending table's outputs for the page, from the scene saved by blender_mesa.py (--guardar), without
baking again (the room's lightmap UVs stay as they were baked):
- the room GLB again with lighter textures — colour of the floor, walls and ceiling 2048, the rest 1024, small objects'
  normal/roughness 512, WebP quality 80 — and the scanned plant reduced to ~22 000 triangles (70 000: the heaviest
  part of the page); sala_m.glb for phones (1024 / 512);
- the HDR panoramas as sRGB JPEG over K (luz.json "env": {modo: K}): the page multiplies by K (12 MB of HDR -> ~1 MB);
- the powder-coat normal map at 512 (it tiles 12.5 times per metre); the 4096 colour maps at WebP 80;
- the outside's lightmaps and the linen colour at 1024;
- --bordas: contact shadows of an older bake faded at their edges (sombra_limpa does it in new bakes).

    blender -b <saida>/mesa.blend --python ferramentas/movel/aliviar_mesa.py -- <saida>
"""
import json
import os
import sys

import bpy
import numpy as np

SAIDA = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
TEX = os.path.join(SAIDA, "tex")
PEQUENOS = ("ceramic_vase", "potted_plant", "moldura", "arte", "pendente", "cabo", "caixilho", "soleira", "rodape")


def rgba_de(img, lado):
    c = img.copy()
    w, h = c.size
    f = min(1.0, lado / max(w, h))
    nw, nh = max(1, int(w * f)), max(1, int(h * f))
    if f < 1:
        c.scale(nw, nh)
    px = np.array(c.pixels[:], dtype=np.float32)
    ch = len(px) // (nw * nh)
    px = px.reshape(nh, nw, ch)
    rgba = np.ones((nh, nw, 4), dtype=np.float32)
    rgba[..., :3] = px[..., :1] if ch < 3 else px[..., :3]
    if ch in (2, 4):
        rgba[..., 3] = px[..., ch - 1]
    bpy.data.images.remove(c)
    return rgba, nw, nh


def imagens(obs, movel):
    feitos = {}
    for o in obs:
        for m in o.data.materials:
            if not m or not m.node_tree:
                continue
            for n in m.node_tree.nodes:
                if n.type != "TEX_IMAGE" or not n.image or n.name == "LM":
                    continue
                img = n.image
                cor = img.colorspace_settings.name != "Non-Color"
                grande = cor and m.name in ("soalho", "parede", "teto")
                pequeno = any(p in (o.name + m.name) for p in PEQUENOS)
                lado = (2048 if grande else 1024 if (cor or not pequeno) else 512) // (2 if movel else 1)
                chave = (img.name, lado)
                if chave not in feitos:
                    rgba, nw, nh = rgba_de(img, lado)
                    alfa = bool((rgba[..., 3] < 0.99).any())
                    novo = bpy.data.images.new(img.name + f"_{lado}", nw, nh, alpha=alfa)
                    novo.colorspace_settings.name = img.colorspace_settings.name
                    novo.pixels.foreach_set(rgba.ravel())
                    novo.pack()
                    feitos[chave] = novo
                n.image = feitos[chave]


def exportar(obs, caminho):
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.hide_viewport = False
        o.hide_set(False)
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.export_scene.gltf(filepath=caminho, export_format="GLB", use_selection=True, export_apply=True,
                              export_extras=True, export_materials="EXPORT", export_image_format="WEBP",
                              export_image_quality=80, export_texcoords=True, export_normals=True, export_yup=True,
                              export_cameras=False, export_lights=False)
    print("GLB", os.path.basename(caminho), round(os.path.getsize(caminho) / 1e6, 2), "MB")


def planta(obs):
    for o in obs:
        if "potted_plant" in o.name or "potted_plant" in (o.data.materials[0].name if o.data.materials else ""):
            n0 = len(o.data.polygons)
            if n0 > 8000:
                md = o.modifiers.new("dec", "DECIMATE")
                md.ratio = 22000 / max(n0, 1) if n0 > 22000 else 1.0
                bpy.context.view_layer.objects.active = o
                bpy.ops.object.modifier_apply(modifier=md.name)
                print("PLANTA", o.name, n0, "->", len(o.data.polygons))


def env_jpeg(info):
    """HDR panorama -> sRGB JPEG of value / K (K = the 99.95th percentile; the few brighter pixels clip)."""
    info["env"] = {}
    for k in ("dia", "noite", "ceu"):
        f = os.path.join(SAIDA, f"env_{k}.hdr")
        if not os.path.exists(f):
            continue
        im = bpy.data.images.load(f)
        w, h = im.size
        px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
        K = float(np.percentile(px, 99.95)) or 1.0
        x = np.clip(px / K, 0, 1)
        enc = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
        out = bpy.data.images.new(f"env_{k}_8", w, h, alpha=False)
        rgba = np.ones((h, w, 4), dtype=np.float32)
        rgba[..., :3] = enc
        out.pixels.foreach_set(rgba.ravel())
        out.filepath_raw = os.path.join(SAIDA, f"env_{k}.jpg")
        out.file_format = "JPEG"
        bpy.context.scene.render.image_settings.quality = 95
        out.save()
        info["env"][k] = round(K, 5)
        print("ENV", k, "K", round(K, 3))
        bpy.data.images.remove(out)
        bpy.data.images.remove(im)


def po():
    f = os.path.join(TEX, "po_nor.png")
    if not os.path.exists(f):
        return
    im = bpy.data.images.load(f)
    if im.size[0] > 512:
        im.scale(512, 512)
        im.save()
    print("PO", im.size[:])


def webp_80():
    """The 4096 veneer and marble colour maps at WebP quality 80 (88: 4.3 MB for the oak alone)."""
    for k in ("oak", "walnut", "marble"):
        f = os.path.join(TEX, f"{k}_Diffuse.webp")
        if os.path.exists(f):
            im = bpy.data.images.load(f)
            im.file_format = "WEBP"
            im.filepath_raw = f
            im.save(quality=80)
            print("WEBP", k, round(os.path.getsize(f) / 1e6, 2), "MB")
            bpy.data.images.remove(im)


def sombras_bordas():
    """Contact shadows faded to nothing at their edges (bakes made before sombra_limpa in blender_mesa.py drew a
    frame on the rug)."""
    import glob
    for f in glob.glob(os.path.join(SAIDA, "sombra_*.png")):
        im = bpy.data.images.load(f)
        w, h = im.size
        px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        fy = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / (0.08 * h), 0, 1)
        fx = np.clip(np.minimum(np.arange(w), np.arange(w)[::-1]) / (0.08 * w), 0, 1)
        oc = px[..., 1] * np.outer(fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx))
        px[..., 0] = px[..., 1] = px[..., 2] = oc
        im.pixels.foreach_set(px.ravel())
        im.save()
        bpy.data.images.remove(im)


def reduzir_mapas():
    """1024 px where more is not seen: the outside's lightmaps (lawn and trees, only through the window) and the
    chairs' linen colour (a 0.27 m weave: 1024 px is 0.26 mm per pixel). Keeps the desktop page under 30 MiB."""
    for f in [os.path.join(SAIDA, f"lm_{m}_fora.jpg") for m in ("dia", "noite")] + [os.path.join(TEX, "linho_cor.jpg")]:
        if not os.path.exists(f):
            continue
        im = bpy.data.images.load(f)
        if im.size[0] > 1024:
            im.scale(1024, 1024)
            im.file_format = "JPEG"
            bpy.context.scene.render.image_settings.quality = 90
            im.save()
        print("MAPA", os.path.basename(f), im.size[:], round(os.path.getsize(f) / 1e6, 2), "MB")
        bpy.data.images.remove(im)


def main():
    info = json.load(open(os.path.join(SAIDA, "luz.json"), encoding="utf-8"))
    sala = [o for o in bpy.data.objects if o.type == "MESH" and o.get("grupo") in ("sala", "moveis", "fora", "scan")]
    if not sala:                        # no saved scene (a test bake): only the panoramas and the maps
        print("sem a cena guardada: só os panoramas e os mapas")
    else:
        aliviar_sala(sala)
    env_jpeg(info)
    po()
    webp_80()
    reduzir_mapas()
    if "--bordas" in sys.argv:
        sombras_bordas()
    json.dump(info, open(os.path.join(SAIDA, "luz.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("FEITO")


def aliviar_sala(sala):
    planta(sala)
    originais = {}
    for o in sala:
        for m in o.data.materials:
            if m and m.node_tree:
                for n in m.node_tree.nodes:
                    if n.type == "TEX_IMAGE":
                        originais[(m.name, n.name)] = n.image
    imagens(sala, movel=False)
    exportar(sala, os.path.join(SAIDA, "sala.glb"))
    for o in sala:                       # back to the originals, then the phone's sizes
        for m in o.data.materials:
            if m and m.node_tree:
                for n in m.node_tree.nodes:
                    if (m.name, n.name) in originais:
                        n.image = originais[(m.name, n.name)]
    imagens(sala, movel=True)
    exportar(sala, os.path.join(SAIDA, "sala_m.glb"))


main()
