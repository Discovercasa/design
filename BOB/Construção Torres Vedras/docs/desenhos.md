# Drawings — Torres Vedras

**DiscoverCasa's own roof drawing `250828_D2503_Cobertura.dwfx` (D2503, 28/08/2025, 5 A3 sheets) is how the
roof was built: read in full in `docs/cobertura-D2503.md`.** It overrides the architect's roof plan, section B
slope and clear height below (user 2026-10-16).
**DiscoverCasa's module drawing `250828_D2503_Modulos.dwfx` (D2503 Módulos, 2 A1 sheets, exterior and
interior modules) is how the walls were built: read in full in `docs/modulos-D2503.md`.**

Architecture: all sheets A2 (594 × 420 mm), AutoCAD 2024, scale 1:200 (metres = sheet mm × 0.2). Architecture
"Estudo Prévio de Obras de Edificação de uma Habitação Unifamiliar", July 2024 (muros: October 2024).
It is a preliminary study: what was built may differ (to confirm with the user).

## `projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx`
- Sheet 1 (01.2 "Planta e Cortes"): CORTE A (≈ region 47 5 270 45), CORTE B (≈ 40 70 275 50), site +
  floor plan (house ≈ region 120 192 95 66). Sheet 2 (01.3): roof plan (hips, 2 skylights — not built, user
  2026-10-16: "Não foram construidas podes não incluir as claraboias"; not in the model) (hips: to re-check
  2026-10-15, see registo — the user: "é de duas águas"; the caller's re-reading: a ridge along x in the middle of
  the main block, Y 6,749, and 1,3 % in CORTE B; slope superseded 2026-10-16, see registo: as built 6 %, the south
  slope running on over the wing — D2503, `docs/cobertura-D2503.md`) + elevations
  Sudeste (≈ 62 3 100 26), Noroeste (≈ 355 5 95 22), Nordeste (≈ 160 78 66 22), Sudoeste (≈ 322 78 74 22).
  Sheet 3 (02.1 "Pormenores Construtivos"): P1, P2. Sheet 4 (03.1 "Plano de acessibilidades").
- Colours (licensing convention): **red stroke `#FF0000` = wall faces to build**, grey fill `#767676` =
  wall poche (triangulated, not usable as rectangles), blue `#003FFF` = glazing / door leaves, magenta
  `#FF00FF` = door swings and opening sashes, orange = dimensions and level marks (vector outlines).
  Room names, areas and dimensions are vector outlines, not text → `zoom`.
- Plan (model axes: X to the right of the sheet, Y up the sheet, origin at the bottom-left of the
  walls' box; `modelos/casa/planta_paredes.json`): main block 17,50 × 8,50 (X 0–17,50, Y 2,50–11,00)
  + wing X 10,78–17,50, Y 0–2,50 (suite: quarto 01, WC). Exterior walls 0,25 thick (architecture build-up),
  interior 0,14–0,15. (As built, D2503 2026-10-16: the architect's outer line = the foundation and the modules' outer
  face; the cladding ≈ 9 cm outside it — the built house is ≈ 17,68 × 11,18 over the cladding.) Rooms (drawing): Arrumo/Lavandaria 9,02 m² (3,23 × 2,79), Garagem 16,35 (3,23 ×
  5,07), Cozinha 17,86 (7,15 × 2,54), Sala 39,10 (7,15 × 5,46), WC acess. 5,93 (2,63 × 2,25), Hall 6,12,
  Closet 8,00, Quarto 03 12,41 (3,56 × 3,49), Quarto 02 11,00 (3,56 × 3,09), Quarto 01 ≈ 14,05 (3,85 ×
  3,65), WC 4,71 (2,23 × ≈ 2,1); Deck 1 ≈ 45,6 m². The suite: hall → closet → passage 1,40 (open, no
  door) → quarto 01 and WC. A 1,75 m stub wall closes the kitchen beside the island (P09).
- Pergola (sheet 1, magenta dashed lines, no dimensions; read 2026-10-19): over Deck 1, in front of the main block's
  south facade, x 3,63–10,79 (east edge on the wing); front beam centred at y −1,93; 6 beams 0,16 wide at 1,40
  centres (x 3,707 … 10,707), drawn from the front to y 3,52 (into the house — schematic). Sheet → model:
  x = 0,2·x_sheet − 24,553, y = 50,091 − 0,2·y_sheet. Sections, height, posts not drawn; the site photo of
  2026-10-19 shows 3 posts at the front, the pergola against the facade and slats on top. Used for the provisional
  pergola of model v6. (Superseded as built 2026-10-20, see registo: the finished house — "a pérgola vai até ao
  comprimento total da casa e leva telha e uma caleira à vista em todo o comprimento" — has it along the whole south
  side (main block and wing), tiled, with an exposed gutter; the plan's extent x 3,63–10,79 is the licensed design, the
  2026-10-19 photo an earlier stage — telas finais, `revisao-tecnica.md` #22. The plan's beam spacing 1,40 and front
  line y −1,93 are still used by model v6.2.) (2026-10-20, 13:25 — photos of the finished house
  `revisao-modelo/2026-10-20_final_*.webp`: the pergola **starts just east of the garage** (the garage door is not
  covered, photo 3) — so the plan's **west edge x 3,63 holds as built** — and runs to the east end of the house (photo 2):
  only the east edge moved (10,79 → 17,57). "Whole south side" (x −0,06, model v6.2) superseded 2026-10-20, see registo;
  model v6.3 x 3,63–17,57, ceramic tiles, 2 downpipes.)
- Windows and doors as approved (user's table "PROJETO APROVADO", 2026-10-19): the kitchen window is a **vidro fixo**
  1,50 × 0,80 (the elevation's two leaves superseded) and the garage door **seccionado** (not tilting); full list
  in `docs/materiais.md`. Room names in the table vs this plan: "Despensa" = Arrumo/Lavandaria, "Quarto Suite" = Quarto
  01, "Quarto 1 e 2" = Quartos 02 / 03, "WC" = WC acess., "Sala / Entrada" = Sala + Hall. ⚠ The basculantes are 0,80 ×
  0,80 in the table but 0,75 here and in D2503 Módulos (`revisao-tecnica.md` #20); the entrance 0,90 and the service
  door 0,80 match the table. (2026-10-19, 18:12, user: the basculantes as modelled, 0,73 in 0,75 — "está ótimo como
  fizeste"; the **entrance door as built is bigger** — "uma porta maior e mais robusta que cabe naquele espaço", filling
  the 1,04 rough opening, so neither this plan's nor the table's 0,90 is the built door — telas finais, #20.)
- Openings (plan + elevations): exterior doors and sliding doors 2,20 high (alçado dims); garage door 3,00
  (tilting); sala sliding 2,00; entrance 0,90; quarto 01 sliding 2,00; quartos 02/03 two-leaf sliding
  ≈ 2,00 each (east facade, to the floor); back facade: arrumo service door 0,80, kitchen window 1,50
  (two leaves) and WC window 0,75 (tilt) at mid height; west: arrumo window 0,75 and WC window 0,75
  (tilt). Interior doors 0,80 × 2,00 (sections). (Sizes superseded 2026-10-16, see registo: the rough openings as
  built are in D2503 Módulos — sliding doors 2,00 × 2,40, garage 3,00 × 2,20, entrance 0,94 × 2,20, service door
  1,04 × 2,20 (superseded 2026-10-19, see registo: entrance / service door swapped — the entrance (M5 on P03) has the
  1,04 opening, the arrumo service door (0,80, M23 on P11) the 0,94), kitchen window 1,50 × 0,95, WC windows 0,75 × 0,75,
  window sills ≈ 1,03, interior doors 0,87 × 2,03 — `docs/modulos-D2503.md`.) (2026-10-20, night, module divider: the
  two quartos 02/03 sliding doors on P18 are drawn ≈ 0,14 apart — with 11×7,5 jambs their frames overlap; as built
  D2503 put the 0,32 pier M13 between them, each door ≈ 16,5 cm off the architect's position; the divider does the
  same — `docs/modulos-D2503.md`.) (The approved table names them "Janela de correr 2 folhas" (quartos 1 e 2, 2 × 2,2)
  and the user calls them "duas janelas" (2026-10-20, night): windows to the floor, not doors — moving them apart is the
  default for two windows; `revisao-tecnica.md` #24.)
- Levels: inside finished floor 117,50; deck 117,48; top of the parapet ≈ 120,6 (one level all round — as built the
  house has the same height on every side, user 2026-10-16; the gutters are inside the walls, not drawn; as built
  ≈ 121,0 — Z 3,4915 above the base, D2503). Interior clear height
  2,60 (corte A) (as built 2,50 — D2503, superseded 2026-10-16, see registo); facade ≈ 3,09–3,10 above the deck (2,53 + 0,56 / 2,20 + 0,90); corte B total depth
  11,00 (2,00 · 5,64 · 2,32 · 2,25 across).
- P1 (architect's generic detail, not necessarily what DiscoverCasa built): wall from outside — ripado de
  madeira, sub-estrutura de madeira/caixa de ar, isolamento térmico, placa OSB3, lã de rocha 60 mm,
  estrutura de madeira/caixa de ar, calha metálica/caixa de ar, gesso cartonado; roof — painel sandwich
  imitar telha com isolamento on madres ómega "Mundiperfil", tela de impermeabilização, cantoneira
  metálica, parapet with "perfil metálico para fixação do rufo e apoio da pingadeira"; ceiling gesso
  cartonado + lã de rocha 100 mm; floor — slab on "caixa de ar / filtro plástico" (plastic void formers),
  sapata de betão armado, drain Ø160, deck outside; aluminium frames, double glazing, timber sills.
  P2: the same wall at a lawn edge.

## `250828_D2503_Cobertura.dwfx` (DiscoverCasa, given by the user 2026-10-16)
Full reading: `docs/cobertura-D2503.md`. Gaps and inconsistencies in the drawing itself (for the comparison, not
errors of the model): sheet 1 still labels the lameladas "16x8" although revision C made them 20x10; the 11 m section
labels the ridge madres "22x7.5" but draws them 0,11 high like the others (user 2026-10-16, night: "então é como estão
no desenho com 22x7,5" — built 22×7,5, the label is right); the downpipes are not drawn (as modelled in v4 = right,
user 2026-10-16 night); the gable parapets (P12, P14, P18) are not cut by any section (their roof side is not shown) —
`revisao-tecnica.md` #11, #15.

## `250828_D2503_Modulos.dwfx` (DiscoverCasa, given by the user 2026-10-16, night)
Full reading: `docs/modulos-D2503.md` (2 A1 sheets, "Sem Escala", 19,377 mm/m; 27 exterior modules, 23 interior).
Gaps and inconsistencies in the drawing itself (for the comparison, not errors of the model): P01's modules add up to
6,64 in the elevations (M9 2,61) but 6,61 in the plan (M9 2,58); the exterior modules are 3,50 high in the table
(studs 3,43 + 2 × 0,035) but the roof set's sections put the parapet top at 3,4915; the studs are drawn continuous
where the lameladas of the roof set cross the exterior modules (no pockets drawn) (not a gap — 2026-10-21, see registo:
the lameladas end inside against the modules, the studs are whole; the roof set's 8,50 / 11,00 lengths are the outer
depths — to confirm whether that is the ordered length (answered 2026-10-21, see registo: nominal lengths, the
lameladas cut to fit each house — "cortamos para "encaixar""); the downpipes are not drawn —
`revisao-tecnica.md` #19, `docs/estado.md`.

## Other sheets
- `20241024.PL_LA_muros-F05.1_MUROS.dwfx`: "MURO PARA ARRUAMENTO 34.91m" (plan + elevation, 1:200);
  house outline dimensions repeated (17,50 · 8,50 / 11,00).
- `Planta de implantação F01,1.dwfx`, `Levantamento topográfico F00.0.dwfx`: site plan and survey (not
  read in detail yet).
