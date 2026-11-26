"""Runs INSIDE Blender (no file needed): a sky photo (.hdr, equirectangular) made ready for the VR sky dome (Step
Inside Phase 8, ue/ceu_hdri.py).

    blender -b --python blender_ceu.py -- <in.hdr> <out.exr> <report.json> [degrees around the sun left as it is: 6]

Why: Unreal imports a .hdr as a cube map, an .exr as a plain 2D texture. The dome samples the 2D panorama itself
(ceu_hdri.py), so it can turn the photo until its sun lies where the level's sun is.
The level has its own sun (a directional light, its shadow baked): the photo's sun would light everything a second
time through the sky light and show a second disc. So every pixel is capped at the brightest pixel more than
<degrees> away from the photo's sun (a bright cloud edge): the glow stays, the disc's energy goes.
The report gives what ceu_hdri.py needs: the sun's column (0-1 from the left) and elevation, and the mean luminance of
the upper half (weighted by solid angle, after the cap) to scale the photo to the sky the level was tuned with.
Writes a half-float RGB OpenEXR (ZIP), linear like the source.
"""
import json
import math
import sys

import bpy
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
graus = float(a[3]) if len(a) > 3 else 6.0
im = bpy.data.images.load(a[0])
im.colorspace_settings.name = "Linear Rec.709"
w, h = im.size
px = np.empty(w * h * 4, dtype=np.float32)
im.pixels.foreach_get(px)
px = px.reshape(h, w, 4)[::-1]  # Blender stores rows bottom-up: row 0 = top of the panorama from here on
lum = 0.2126 * px[..., 0] + 0.7152 * px[..., 1] + 0.0722 * px[..., 2]
ys, xs = np.unravel_index(np.argmax(lum), lum.shape)
el_sol = 90 - (ys + 0.5) / h * 180
az_sol = (xs + 0.5) / w * 2 * math.pi
lat = (0.5 - (np.arange(h) + 0.5) / h) * math.pi
lon = (np.arange(w) + 0.5) / w * 2 * math.pi
cl, sl = np.cos(lat)[:, None], np.sin(lat)[:, None]
d = sl * math.sin(math.radians(el_sol)) + cl * math.cos(math.radians(el_sol)) * np.cos(lon[None, :] - az_sol)
longe = d < math.cos(math.radians(graus))
teto = float(lum[longe].max())
pico = float(lum.max())
f = np.minimum(1.0, teto / np.maximum(lum, 1e-9))
px[..., :3] *= f[..., None]
lum = lum * f
cima = slice(0, h // 2)
peso = np.repeat(np.cos(lat)[cima, None], w, axis=1)
media = float((lum[cima] * peso).sum() / peso.sum())
zenite = float(lum[: max(1, h // 36)].mean())          # the top 5 degrees
horizonte = float(lum[h // 2 - max(1, h // 36): h // 2].mean())  # the 5 degrees above the horizon
out = bpy.data.images.new("ceu", w, h, alpha=False, float_buffer=True)
out.colorspace_settings.name = "Linear Rec.709"
out.pixels.foreach_set(px[::-1].ravel())
cena = bpy.context.scene
cena.view_settings.view_transform = "Standard"  # EXR is written scene-linear; never a display look on top
cena.view_settings.look = "None"
cena.render.image_settings.file_format = "OPEN_EXR"
cena.render.image_settings.color_depth = "16"
cena.render.image_settings.exr_codec = "ZIP"
cena.render.image_settings.color_mode = "RGB"
out.save_render(a[1], scene=cena)
rel = {"fonte": a[0], "largura": w, "altura": h, "sol_coluna": (xs + 0.5) / w, "sol_elevacao_graus": round(el_sol, 2),
       "pico": pico, "teto": teto, "graus_poupados": graus, "media_metade_cima": media, "zenite": zenite,
       "horizonte": horizonte}
with open(a[2], "w", encoding="utf-8") as fh:
    json.dump(rel, fh, indent=1)
print("CEU_OK", json.dumps(rel))
