---
name: ler-dwfx
description: Read Autodesk DWFx drawings (DiscoverCasa structural/architectural sheets) - list sheets, extract text with sheet coordinates, list timber members, render sheets to PNG and zoom into regions. Use whenever a .dwfx file has to be read, measured or checked.
---

# Reading DWFx drawings

DWFx = XPS/OPC zip with vector pages. The tools read it directly (never unzip: paths exceed Windows'
260-character limit; never `Read` the .dwfx itself).

```bash
python ferramentas/dwfx/dwfx.py info   "<file>.dwfx"                       # sheets, paper, DWG, dates
python ferramentas/dwfx/dwfx.py texto  "<file>.dwfx" --folha 2 [--regiao X0 Y0 X1 Y1] [--procura REGEX] [--sem-numeros]
python ferramentas/dwfx/dwfx.py pecas  "<file>.dwfx" --folha 1 [--regiao X0 Y0 X1 Y1] [--escala 50]
python ferramentas/dwfx/dwfx.py render "<file>.dwfx" --folha 1 [--dpi 55] [--saida out.png]     # Windows
python ferramentas/dwfx/dwfx.py zoom   "<file>.dwfx" --folha 1 --regiao X Y W H [--px 1600] [--saida out.png]  # Windows
```
Default image output: `_trabalho/renders/`. Coordinates are **sheet millimetres, origin top-left**
(A1 = 841 × 594). Metres = sheet mm × scale (1:50 → × 0.05; 1:100 → × 0.10).

## Efficient workflow (token-aware)
1. `info`, then check the project's `docs/desenhos.md` — it may already map every view's region.
2. Overview: `render --dpi 55` (≈1800 px wide) and Read the PNG once to see the layout.
3. Exact values: `texto` restricted with `--regiao`/`--procura` (text is far cheaper than images).
   Titles such as "PLANTA", "ALÇADO", "CORTE", "ESTRUTURA" locate views: `--procura "PLANTA|CORTE"`.
4. Details: `zoom` on small regions (≤ 1600 px wide; 60 mm of sheet at 1600 px ≈ 680 dpi).
5. Geometry: `pecas` summarises timber members (section, view/cut, sizes) in a region; for real
   extraction use `ferramentas/dwfx/leitor.py` + `pecas.py` in Python (see skill modelo-blender-madeira).
6. Record new region maps / facts in the project's `docs/desenhos.md`.

## DiscoverCasa drawing conventions
- Timber fills: `#FFBF7F` 160×80 view · `#DD6E00` 160×80 cut · `#BFFF7F` 100×80 view · `#A5DD6E` 100×80 cut.
  Each filled rectangle = 2 triangles (merged by `pecas.build_members`).
- Dimensions in metres with decimal comma. "0,40" between members = clear gap (≈ 0.48 m c/c).
- Level marks: ±0,00 / +2,88 … (text positions follow the scale exactly).
- Text heights ≈ 0.7–1.1 mm for dimensions, 2.5 mm for panel labels, 3.3 mm for view titles.

## Troubleshooting
- "Measure … I/O error" in `render`: font references without "./" (architecture sets) — fixed in
  `render.py` (any `FontUri="…GUID.odttf"` form); delete the cache folder in `_trabalho/dwfx/` and re-render.
- Architecture sets (CAL30): room names, areas and level marks are vector outlines, not text → `zoom`.
- "Initialization of FixedDocument threw" with the XPS API = fonts not embedded; `render.py` handles it
  (de-obfuscates `.odttf`, missing fonts → Arial).
- File locked ("used by another process"): usually Autodesk Design Review — ask the user to close it.
- Not on Windows: `render`/`zoom` are unavailable; use `texto`/`pecas` and the geometry pipeline.
