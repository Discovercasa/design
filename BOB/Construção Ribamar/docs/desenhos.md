# Drawings — Construção Ribamar

Facts read from the drawings (2026-11-19). Every drawing stays on the PC, never in Git: `desenhos/` (architecture
PDFs, DWG/DXF, `desenho.dwfx` — from the Builder's hub section, 2026-11-11) and `desenhos/modulos/` (the 4 module
sheets — generator › Documentos adicionais › «Ribamar» › pasta «Ribamar Módulos», 2026-11-19). The architecture sheets
ARQ.03–ARQ.12 of the generator's section (pasta «Ribamar Documentos Projetos etc») were saved only in the scratch folder
`_trabalho/ribamar_listagem/hub/arquitetura/` (git-ignored, may be cleared) — copy them to `desenhos/` if needed again.
Module sheets plotted to PDF are read by `ferramentas/documentos/modulos_pdf.py`.

## Module sheets — DiscoverCasa production drawings, as built
- Files: «modulos piso 1 ext», «modulos piso 1 int v2», «modulos piso 2 ext», «modulos piso 2 int». **Byte-identical to
  the "Casa CL" sheets of 2026-09-30** (`conhecimento/fontes/estrutura-exemplo-casa-cl/`): title block «CASA CL», D2512,
  2 storeys, none below ground — a template title block (our reading; see `estado.md`).
- Naming: sheet «piso 1» = Piso 0, «piso 2» = Piso 1 of the architecture. The cave (Piso -1) is concrete, not in them.
- 59 modules. Heights:
  - Piso 0 exterior M001–M020: **2,97**; M003 (return at the entrance porch) and M008 (deck step) **2,67**.
  - Piso 0 interior M030 A/B, M031, M032, M034–M039 (no M033): **2,80** and **2,60**.
  - Piso 1 exterior M120–M138: **3,52** on the two side walls (the gutter sides, with the parapet), **2,97** on the front
    wall, **2,94** on the back wall (glazed openings to the varandas), **2,67** on the varanda returns (M126, M128, M129).
  - Piso 1 interior M101–M110: **2,68**.
- Wide openings — portal modules: two 110×75 posts under a 22×7,5 lintel at the module top, no plates; clear rough
  opening between the posts: Piso 0 M007 4,37, M010 2,91, M011 3,99, M014 2,77 (× 2,76 / 2,72); Piso 1 M125 4,02, M127
  4,11 (× 2,72). M132 is framed differently: the verga sits on a 2,09 head with 110×75 jamb pieces over its ends and
  studs above to the top plate (2,81 × 2,09, down to the Piso 1 floor, onto the lower roof). (`sistema-construtivo.md` §2 gives the Piso 0 ones as 4,52 / 3,06 / 4,14 / 2,92 and M132
  2,96: the same openings measured over the two posts, + 0,15.)
- Interior openings **1,69 × 2,06** (M031, M103, M106, M109): wider than the standard interior door (rough 0,87 × 2,03)
  — double or pocket doors? (open, `estado.md`).
- Exterior cladding on both faces: the varanda returns M128, M129; M124 beside varanda 1 (1,48 of its 2,30); M020 at
  the porch (1,34 of its 2,19).
- Drawing slips: M019's elevation 0,98 vs its dimension 1,29; neighbouring plates drawn overlapping 7 cm
  (M135 / M136 / M137).

## Plans of the module sheets (outer faces of the modules) — they agree with the architecture
- Piso 0: outline 14,11 × 9,01 minus the deck notch 9,47 × 1,48 (M008) and the entrance porch 1,34 × 2,78 = 109,31 m².
- Piso 1: 10,99 × 9,00 over the porch side; closed 10,99 × 7,52 = 82,66 m²; two varandas 1,48 deep, 4,35 and 5,02 long
  (≈ 6,4 and 7,4 m²; the architecture says 6,40 and 7,30), over the atelier wing (M007) and over the deck.
- The strip of Piso 0 not under Piso 1: 3,12 × 7,53, with its own lower roof.
- The Piso 1 end wall 4,52 + 2,71 + 0,29 = modules M130–M132.

## Architecture (ARQ.03–ARQ.12) — notes not binding for the build; they fix the geometry
- Section B: pé direito 2,8 (Piso 0), 2,5 (Piso 1); stair run 3,10.
- Roof: "painel sandwich (5 ondas), isolamento 80 mm, RAL 8017"; Piso 1 two slopes at 7 % behind parapets (top 71,50);
  the lower roof over the strip ≈ 68,2–68,4, 7 %, parapet 0,45 drawn.
- Caixilharia "alumínio lacado RAL 7016, vidro duplo incolor". Façade "reguado de madeira Tremollo Douglas Marron";
  ARQ.11 also has a façade detail "C/ REV. CAPOTO" (ETICS) — which façades: not read.
