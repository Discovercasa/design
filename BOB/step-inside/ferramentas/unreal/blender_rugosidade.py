"""Runs INSIDE Blender (no file needed): a roughness texture remapped for Unreal (Step Inside Phase 4, task 69).

    blender -b --python blender_rugosidade.py -- <in.png|jpg> <out.png> <min> <max>

The glTF metal-rough texture keeps roughness in G (B = metal, R unused). Cycles renders the floor's 0.2-0.4 roughness as
a satin varnish; Unreal's Lumen shows it as white sheets of sky reflection. G is remapped linearly from the texture's
own range [lo, hi] (2nd and 98th percentile) to [min, max]; R and B stay as they were.
"""
import sys

import bpy
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
im = bpy.data.images.load(a[0])
im.colorspace_settings.name = "Non-Color"
w, h = im.size
px = np.array(im.pixels[:], dtype=np.float32).reshape(-1, 4)
g = px[:, 1]
lo, hi = np.percentile(g, 2), np.percentile(g, 98)
px[:, 1] = np.clip(float(a[2]) + (g - lo) / max(hi - lo, 1e-3) * (float(a[3]) - float(a[2])), 0, 1)
out = bpy.data.images.new("rug", w, h, alpha=False, float_buffer=False)
out.colorspace_settings.name = "Non-Color"
out.pixels[:] = px.ravel()
out.filepath_raw = a[1]
out.file_format = "PNG"
out.save()
print("RUG_OK", f"{lo:.2f}-{hi:.2f} -> {a[2]}-{a[3]}", w, h)
