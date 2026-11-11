"""Blender (background): a photo of a real product -> PBR maps the visit model reads (Color, NormalGL, Roughness).

    blender -b --factory-startup --python blender_foto.py -- <foto> <pasta_saida> <nome> <proporcao> <x0> <y0> <x1> <y1>
            <relevo> <rugosidade> <lado_max>

Steps (Step Inside Phase 3, hub task 156):
1. crop (fractions of the photo, origin top-left) and then the largest centred rectangle with the real aspect
   (width / height of the photographed area);
2. scale so the longer side is at most `lado_max` px;
3. even out the light: divide by a very blurred copy (shadows and the light falling across the photo go away; the
   texture keeps its own colour on average);
4. make it tile: cross-fade the borders with a copy rolled by half (the seams of the copy sit in the middle, where the
   original is kept);
5. normal map (OpenGL, Y up) from the luminance, roughness around the product's value (darker = a bit rougher).
"""
import sys
from pathlib import Path

import bpy
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
FOTO, SAIDA, NOME = Path(a[0]), Path(a[1]), a[2]
PROP = float(a[3])
X0, Y0, X1, Y1 = map(float, a[4:8])
RELEVO, RUG, LADO = float(a[8]), float(a[9]), int(a[10])


def carregar(p):
    im = bpy.data.images.load(str(p))
    w, h = im.size
    px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, im.channels)[:, :, :3]
    return px[::-1].copy()   # rows top-down, like the photo


def gravar(px, nome, cor=True):
    h, w = px.shape[:2]
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = px if px.ndim == 3 else px[:, :, None]
    im = bpy.data.images.new(nome, w, h, alpha=False)
    if not cor:
        im.colorspace_settings.name = "Non-Color"
    im.pixels = rgba[::-1].ravel()
    im.filepath_raw = str(SAIDA / f"{NOME}_{nome}.jpg")
    im.file_format = "JPEG"
    bpy.context.scene.render.image_settings.quality = 92
    im.save()


def redimensionar(px, w, h):
    H, W = px.shape[:2]
    ys = np.clip(((np.arange(h) + 0.5) * H / h - 0.5), 0, H - 1)
    xs = np.clip(((np.arange(w) + 0.5) * W / w - 0.5), 0, W - 1)
    y0, x0 = np.floor(ys).astype(int), np.floor(xs).astype(int)
    y1, x1 = np.minimum(y0 + 1, H - 1), np.minimum(x0 + 1, W - 1)
    fy, fx = (ys - y0)[:, None, None], (xs - x0)[None, :, None]
    if px.ndim == 2:
        fy, fx = fy[:, :, 0], fx[:, :, 0]
    a_, b_ = px[y0][:, x0], px[y0][:, x1]
    c_, d_ = px[y1][:, x0], px[y1][:, x1]
    return (a_ * (1 - fx) + b_ * fx) * (1 - fy) + (c_ * (1 - fx) + d_ * fx) * fy


def desfocar(img, r):
    """Box blur, three passes (≈ gaussian), wrapping at the borders (the texture tiles)."""
    out = img.astype(np.float32)
    for _ in range(3):
        for eixo in (0, 1):
            c = np.cumsum(np.concatenate([np.take(out, range(-r - 1, 0), axis=eixo), out, np.take(out, range(0, r), axis=eixo)], axis=eixo), axis=eixo)
            n = out.shape[eixo]
            out = (np.take(c, range(2 * r + 1, 2 * r + 1 + n), axis=eixo) - np.take(c, range(0, n), axis=eixo)) / (2 * r + 1)
    return out


px = carregar(FOTO)
H, W = px.shape[:2]
px = px[int(Y0 * H):int(Y1 * H), int(X0 * W):int(X1 * W)]
H, W = px.shape[:2]
if PROP > 0 and W / H > PROP:
    w = int(H * PROP); x = (W - w) // 2; px = px[:, x:x + w]
elif PROP > 0:
    h = int(W / PROP); y = (H - h) // 2; px = px[y:y + h]
H, W = px.shape[:2]
s = min(1.0, LADO / max(H, W))
px = redimensionar(px, max(8, int(W * s)), max(8, int(H * s)))
H, W = px.shape[:2]

# 3. even light: the photo divided by its very blurred self, back to its average colour
media = px.reshape(-1, 3).mean(0)
fundo = desfocar(px, max(4, min(H, W) // 6))
px = np.clip(px / np.maximum(fundo, 1e-3) * media, 0, 1)

# 4. tile: the borders cross-fade into a copy rolled by half
rolado = np.roll(np.roll(px, H // 2, axis=0), W // 2, axis=1)
fy = np.clip(np.minimum(np.arange(H), H - 1 - np.arange(H)) / (0.18 * H), 0, 1)
fx = np.clip(np.minimum(np.arange(W), W - 1 - np.arange(W)) / (0.18 * W), 0, 1)
peso = np.minimum(fy[:, None], fx[None, :]) ** 1.5
peso = peso * peso * (3 - 2 * peso)
px = px * peso[:, :, None] + rolado * (1 - peso[:, :, None])
gravar(px, "Color")

# 5. normal (OpenGL: green up) and roughness from the luminance
lum = desfocar(px @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32), 1)
lum = (lum - lum.min()) / max(1e-6, lum.max() - lum.min())
dx = (np.roll(lum, -1, axis=1) - np.roll(lum, 1, axis=1)) * 0.5
dy = (np.roll(lum, 1, axis=0) - np.roll(lum, -1, axis=0)) * 0.5   # rows go down: up is -row
k = RELEVO * max(H, W) / 512.0
n = np.dstack([-dx * k, -dy * k, np.ones_like(lum)])
n /= np.linalg.norm(n, axis=2, keepdims=True)
gravar(n * 0.5 + 0.5, "NormalGL", cor=False)
rug = np.clip(RUG + (0.5 - lum) * 0.25, 0.04, 1.0)
gravar(np.dstack([rug] * 3), "Roughness", cor=False)
print(f"FOTO OK {W}x{H} -> {SAIDA}")
