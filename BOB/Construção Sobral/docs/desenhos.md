# Sobral drawings — contents, coordinates, conventions

All sheets are A1 (841 × 594 mm), AutoCAD LT 2025, dated Jan–Feb 2026. Regions below are **sheet mm,
origin top-left** (the coordinate system of `ferramentas/dwfx/dwfx.py`). Houses at 1:50 (×0.05 m),
warehouse at 1:100 (×0.10 m).

## PD_Habitacoes A B C D E K L M N O P (1).dwfx — Casa Tipo 1 (2 sheets)
Sheet 1 "Tipo1 1de2" — Plantas estruturais, cortes, detalhes construtivos:
| Region | View |
|---|---|
| 25,12–325,275 | FUNDAÇÕES \| PLANTA — raft outline (black 0.3 mm strokes), house (78.80,66.04)–(275.99,188.24), section marks A–F |
| 405,30–565,120 | Fundações detail — slab 20 cm, perimeter wall, strip footing |
| 325,122–575,207 | FUNDAÇÕES \| CORTE TIPO — floor build-up + wall bases |
| 605,75–810,170 | notes: slab mesh, "tela impermeável", excavation (geotechnical category 1, EC7) |
| 325,205–570,400 | CORTE FF' (transverse) — levels, roof pitch |
| 568,205–820,400 | CORTE EE' (longitudinal) — stair void |
| 40,272–302,418 | ESTRUTURA DO PISO INTERMÉDIO \| PLANTA — floor joists |
| 40,418–302,578 | ESTRUTURA DA COBERTURA \| PLANTA — rafters, **true length along the slope** |
| 390,435–575,520 | stair detail (English, generic) + stair cross-section |
| 620,390–841,594 | drawing index, layer list, legend, title block |

Sheet 2 "Tipo1 2de2" — Plantas e alçados das paredes, detalhes:
| Region | View |
|---|---|
| 25,20–230,195 | CORTE AA' = east facade: PE2.07/PE2.08 (gable halves), PE1.07–PE1.10 |
| 250,55–510,195 | CORTE BB' = south facade: PE2.03–06, PE1.03–06 |
| 25,195–230,365 | CORTE DD' = west facade: PE2.01/PE2.02 (gable halves), PE1.01/02 |
| 250,195–510,365 | CORTE CC' = north facade: PE2.11–14, PE1.11–14 |
| 25,385–560,485 | ALÇADOS \| PAREDES INTERIORES \| PISO ELEVADO (PI2.xx) |
| 25,490–560,565 | ALÇADOS \| PAREDES INTERIORES \| PISO TÉRREO (PI1.xx) |
| 585,20–812,170 | PAREDES \| PLANTA DO PISO TÉRREO (panel labels + cut studs) |
| 585,176–812,326 | PAREDES \| PLANTA DO PISO ELEVADO |
| 596,332–750,434 | details: OSB nailing; stud/plate fixing |
| 598,437–770,519 | details: rafter–wall, rafter–rafter (ridge), joist–plate |

## PD_Habitacoes F G H I J.dwfx — Casa Tipo 2 (2 sheets)
Same sheet layout as Tipo 1 (verify regions with `dwfx.py render`). Differences: sloped site —
lower floor −2.70 (15 risers 0.18 × 0.28), upper floor ±0.00, eaves +2.75, ridge +4.30, chimney +5.10;
stone-hatched retaining structure ≈ 2.7 m high on the west side, 1.37 m from the house (not designed
in these drawings). Same 9.86 × 6.11 m footprint and 11.50 × 11.25 m raft layout.

## PD_Estabilidade Armazém.dwfx — warehouse (1 sheet "1de1", 1:100) → see `armazem.md`
| Region | View |
|---|---|
| 25,14–500,243 | PLANTA DO PISO SUPERIOR (level 204.50) |
| 540,14–830,305 | PLANTA DO PISO INFERIOR (level 201.23, east-wing garage) |
| 25,250–370,480 | PLANTA DO PISO SUPERIOR VISTA DO TECTO / COBERTURA (roof slabs) |
| 385,275–490,470 | Pormenor de escadas |
| 500,320–645,470 | Muro de contenção (RC retaining wall on the lot boundary) |
| 650,315–740,490 | CB.1.1 beam table; Reforço ao punçoamento |
| 745,315–835,480 | Muro de vedação (fence wall) |
| 27,485–600,575 | beam sections, slab mesh, pillars, QUADRO DE ELEMENTOS DE FUNDAÇÃO, index |

## SMA_012_arquitectura_pecas_desenhadas.dwfx — architecture set (22 sheets) — received 2026-10-09
CAL30 arquitectos, obra "Quinta da Encosta"; ANTEPROJECTO, dated October 2024
(DWG saved 2024-11-15). The user (2026-10-09): "for now the final version", shows how the houses changed.
Sheets: 1 index (A4) · 2–5 site 1:500 (survey, implantação, modelação, infraestruturas) · 6 cortes gerais
AA'–BB' · 7–8 implantação sectors A/B 1:200 · 9–11 cortes CC'–KK' 1:200 (+ rua de baixo 1:50) · 12–16
Edifício de apoio à actividade agrícola (= warehouse) 1:100 · **17–19 Casa tipo 1** (plantas + cobertura,
alçados, corte + pormenores) · **20–22 Casa tipo 2** (same) — all houses 1:50.
- Text: titles and the construction notes are text; **room names, areas and level marks are vector
  outlines** → read them with `zoom` (sheet 17: ground plan ≈ region 80 165 220 140, upper plan
  ≈ 545 75 230 150; sheet 19: section HH' ≈ 440 205 300 175).
- **Casa tipo 1** (fracções A B C D E K L M N O P, permilagem 62,5 each; cotas de soleira A B 216,50 ·
  C D E 216,90 · K L 223,40 · M N O P 223,90): levels ±0,00 / +2,88 / ridge +7,00 / chimneys +7,50,
  terrain behind +2,50 (EE', FF', GG', HH'); eaves ≈ +5,3 measured on HH'. Outside 10,00 × 6,25 m over the
  ETICS (walls 0,26) = timber frame 9,86 × 6,11 as in the engineer's drawings; windows on the south facade
  0,95 wide (chain 1,72 · 0,95 · 2,07 · 0,95 · 2,07 · 0,95 · 1,29). Ground floor ("piso de referência,
  entrada e áreas sociais"): 0.1 entrada 4,2 m² (entrance from the east, Pátio Nascente) · 0.2 cozinha 8,9
  · 0.3 sala 25,3 · 0.4 circulação 3,7 · 0.5 lavandaria 2,8 (AQS tank) · 0.6 inst. sanitária 1,2 · E.1
  escada 4,2 (16 D 0,28 × 0,18) · A.T. niche NE; stove/flue box on the sala's north wall. Upper floor
  (+2,88): 1.1 circulação 5,4 · 1.2 casa de banho 2,7 (NE) · 1.3 quarto 9 · 1.4 quarto 9 · 1.5 quarto 14,0
  (L-shaped) · 1.6 casa de banho 5,2 (NW) · 1.7 arrumo 1 · wardrobes between 1.5 and 1.4 with a round duct
  (above the stove) · a round pipe in 1.3's NE corner. Upper rooms have **sloped ceilings up to the ridge**
  (roof on the walls). Patios: Pátio Norte (serviço), Pátio Nascente (entrada, estacionamento), Pátio Sul.
- **Casa tipo 2** (bedrooms below): levels −2,70 (lower floor) / ±0,00 (entrance floor at the street) /
  +2,75 (eaves) / ridge +4,30 / chimney +5,10; dug into the slope (uphill side at ±0,00).
- Plan comparison with the model (2026-10-09): overlay calibration on the `zoom` images — ground plan zoom
  `--regiao 80 165 220 140 --px 1600`: x_px = 62,2 + x·145,45, y_px = 973,8 − y·145,45; upper plan zoom
  `--regiao 545 75 230 150 --px 1600`: x_px = 164,7 + x·139,1, y_px = 916,3 − y·139,1 (x, y = model metres
  from the timber frame's SW outer corner). Structural walls, doors and windows of the engineer's drawings
  match the architecture within a few cm. Architecture-only: lavandaria + AQS, WC 0.6 east wall, stove niche
  (= the model's tiny "P0.02") with a flue through the upstairs wardrobe, wardrobes, quarto 1.5 in L (no
  door between its two parts). South windows: architecture 0,95 wide, frame openings 1,11–1,15 (same centres).
- Architect's construction notes (sheet 19, section HH' — the licensing spec, **not** DiscoverCasa's method;
  the user 2026-10-09: build with the DiscoverCasa method and materials, not the ones the architect lists):
  roof zinc standing seam (junta agrafada) + manta pitonada + OSB 2 cm + insulation 10 cm + OSB 2 cm on
  rafters 16×8 with 16 cm rock wool between, plasterboard on profiles under the rafters, eaves in marine
  plywood, zinc chimneys; walls ETICS white + OSB 9 + membrane ~1 mm + rock wool 16 cm (or 2×8) between the
  studs + omega 17 + plasterboard 13 (tiles 10×10 in wet rooms), stone copings; floor between storeys wood
  20 mm glued + OSB 2×15 + acoustic membrane 10 + OSB 19 + omega 17 + rock wool 16 + omega 17 +
  plasterboard 13 (wet rooms: hydraulic mosaic 2 cm + Viroc 2×1,5 + acoustic membrane 1 + OSB 2); ground
  floor microcimento + betonilha (8 cm) + XPS 6 cm + geotêxtil + massame 15 cm + filme plástico + betão de
  limpeza 5 cm + brita 30 cm; windows white aluminium tilt-and-turn with thermal break, pre-aro superior
  40 mm, self-regulating ventilation grille, painted wood interior shutters; fences in timber posts, stone
  walls.

## Drawing conventions (important for extraction)
- Timber colours: `#FFBF7F` 160×80 in view, `#DD6E00` 160×80 cut, `#BFFF7F` 100×80 in view,
  `#A5DD6E` 100×80 cut. Filled rectangles are exported as 2 triangles (merged by the tools).
- Dimensions are metres with decimal comma ("2,80"). **"0,40" between studs/joists/rafters is the
  clear gap → 0.48 m centre to centre.**
- Panel names: PE = parede exterior, PI = interior; first digit 1 = ground floor, 2 = upper floor.
  Each elevation has its label just below its left end; stacked labels = identical panels
  (PI2.09/PI2.10, PI2.11/12/13, PI2.14/15).
- Plan labels sit at a panel end: horizontal text = west end (−0.6 mm), rotated −90° = north end
  (−0.5 mm), rotated +90° = south end (+0.65 mm).
- Exterior elevations are drawn as seen from outside.
- Studs are often drawn in two pieces (above/below the nogging).
- Traps: upper plan labels "PE2.07/PE2.08" (horizontal, mid-house) are the interior walls PI2.07/PI2.08;
  the real PE2.07/08 are the east gable halves. Roof plan is true length (3.41 m ↔ 3.055 m horizontal).
- Some doorways are just a gap between two modules, with nothing drawn above the door: PI1.10/PI1.11
  (ground floor, 0.86 m), PI2.03 (closet, 1.01), PI2.06 (corridor → SW bedroom, 1.00), PI2.07/PI2.08
  (0.90). Found 2026-10-09 (the "gaps" the user saw in the model); the model closes them with a
  bandeira (`modelos.md`, `revisao-tecnica.md` #5).
- Section FF' levels (Z from top of slab): GF walls 0–2.80 (double bottom plate 2×0.08); joists
  2.80–2.96; upper exterior walls from 2.96 (on rim joists), interior from 2.98 (on OSB);
  ±0.00 of the project = Z 0.16 (top of double plate), +2.88 = Z 3.04; rafters level-cut on an
  80×160 eave plate at Z 5.48 (N) / 5.49 (S); ridge top Z 6.9645; pitch 26.37°.
- The DWFx files embed only some fonts (titles fall back to Arial when rendering). Autodesk Design
  Review locks a file while open and may re-save it.

## Architectural background in the sections (grey lines, read 2026-09-24)
- FF': sloped ceilings upstairs (partitions reach the rafters) — changed by the user 2026-09-30: flat
  ceiling at the viga de amarração (`estado.md`); windows with "PRÉ ARO SUPERIOR 40 mm",
  upper window sill 1.04 m and height 1.25 m above +2.88; exterior walls drawn with ≈ 60 mm outer
  insulation; roof ≈ 140 mm insulation + profiled sheet above the rafters, eaves overhang ≈ 0.25 m from
  the frame; ridge +7.00, chimney +7.50.
- EE': stair along X in the void; verges overhang ≈ 0.10–0.12 m from the frame; two chimney boxes on the
  ridge; tiled bathrooms at both ends upstairs, WC with window under the stair downstairs (window ≈ Z 1.1–1.8).
- Wall plans: only structural walls; no room names ("VENTILAÇÃO", "A.T.", stair "16D 0,28x0,18m").

## Notes and specs printed on the house drawings
- Foundation: raft 20 cm C25/30 XC2 S3, A400NR, Ø8//30 top+bottom, cover 3 cm; perimeter wall 0.20
  (Ø8//25, height variable up to the sill) on strip footing 0.65 × 0.40 (6Ø10, stirrups Ø8//25);
  fill inside; waterproof membrane between ground and slab.
- Floor build-up (corte tipo): microcimento, betonilha, XPS 6 cm, geotêxtil, "massame 15 cm",
  filme plástico, betão de limpeza 5 cm, brita 30 cm, terreno compactado.
- Walls: "Paredes de painéis de madeira autoportantes em malha com prumos e montantes espaçados
  conforme desenhos. Travamentos transversais… forra interior e exterior em OSB3. Verificações…
  em memória descritiva (EC5). Pregos ou parafusos de resistência equivalente."
- Fixings: OSB with LBA 4×60 at 100 mm (edges) / 200 mm (field); plates to floor 2 HBS 10×180 // 300;
  studs to plates 2 HBS 10×120; double studs 2 HBS 6×90 // 250; upper walls WKR 13535 + KOP 12×140 +
  8 LBA 4×40; rafters to wall TBS EVO 8×260 // 0.5 m; rafter–rafter 2 VGZ 7×180; joist to plate
  HBS EVO 8×260. Floor deck OSB4 18 mm.
