# Wall modules as built — DiscoverCasa drawing D2503 Módulos (read 2026-10-16)

Source: `desenhos/250828_D2503_Modulos.dwfx` (DiscoverCasa production set, same job as the roof drawing
`cobertura-D2503.md`; 2 A1 sheets, "Sem Escala", one scale per sheet: 19,377 mm/m). Given by the user
2026-10-16: "o ficheiro original de como os módulos foram feitos". Read with `ferramentas/modelo/modulos_dc.py`
→ `modelos/casa/modulos_D2503.json` (every module: footprint in plan axes, height, every member, openings).
Model version 5 uses these modules as they are (`config.json` "modulos_reais").

## How the sheets are drawn (the DiscoverCasa module-drawing standard)
- Sheet "Módulos Exteriores" / "Módulos Interiores": the plan in the middle, every module in section (a black
  rectangle module length × wall thickness: 0,11 exterior, 0,075 interior) and labelled M1, M2 … (blue); the
  elevation of each module beside the plan, aligned with it (same x for walls along X, same y for walls along
  Y; the N and S elevations upright, the W and E ones turned 90°), labelled again, total width dimensioned above.
- Colours: black outline = 11×3,5 (exterior) / 7,5×3,5 (interior) pieces — studs, plates, cripples, noggings;
  red hatched = 11×7,5 (exterior) / 7,5×11 (interior) — corner studs, jambs, lintels, sills.
- "CONSIDERAÇÕES GERAIS": regular spacing 40 cm clear, the same in every module and not dimensioned; irregular
  spacings dimensioned; a detail of the 11×7,5 / 11×3,5 corner.
- Tables: "QUADRO DE DIMENSÕES E QUANTIDADES" (module L × A, reference, V = door/window, P = door, "* Painel a
  executar em obra") and "COMPRIMENTO DAS VIGAS" (cut list by length and section).
- Title block: Moradia LA, obra D2503, revisions A–E as the roof set; "Módulos Exteriores"/"Interiores".

## What the modules are (and why)
1. **Height.** Exterior modules **3,50** (A in the table; studs 3,43 + two plates 0,035) — one piece from the
   base to the parapet top, no separate parapet. Interior modules **2,53** (studs 2,46).
   ⚠ The company rule (user 2026-10-19, 18:12: "Nós fazemos os módulos de forma a ficarem à medida certa das vigas
   amarração") gives **2,543** (studs 2,473): module + the 11×7,5 on top = 2,653, the lameladas' underside, no packing.
   D2503 is 13 mm less — rounding / another datum in the drawing, or taken up on site: not said (`revisao-tecnica.md`
   #6). Model v6.1 follows the rule (`modelos.md`).
2. **The stud grid.** 40 cm clear = 0,435 between centres from one end of the module. The plain modules are
   whole numbers of bays plus the last stud: exterior **2,21 = 5 bays** (8 of the 27: M8, M11, M17, M19, M21,
   M22, M25, M26), interior **1,78 = 4 bays** (6: M5, M7, M11, M14, M16, M18) and **2,65 = 6 bays** (M2, M3,
   M13). *Why (our reading, to confirm):* every stud on the grid, the OSB and Pladur joints and the services
   predictable, the same jigs in the factory.
3. **Largest module.** Exterior ≤ 2,64 (M18), interior ≤ 2,72 (M17); the one exterior module longer than that,
   **M1 3,82 with the garage door, "a executar em obra"** (built on site). The 3 m the builder assumed (user
   2026-10-15, from memory) was not used here. (User 2026-10-19, 15:48: "esses módulos maiores são montados em obra" —
   confirmed.)
4. **Openings inside one module, framed in 11×7,5.** Jambs full height, lintel (and sill for windows) 11×7,5
   between the jambs, cripples at the grid above/below; the module is sized round the opening (opening +
   jambs + the dimensioned margins), e.g. M20 2,19 (window 1,50 × 0,95, margins 0,30 / 0,30 / 0,50), M23 2,53
   (door 0,94 × 2,20 at 0,13 + 0,075 from the corner), M12 / M14 2,15 = door 2,00 + two 11×7,5 (the door fills
   the module), M13 0,32 the pier between them.
   Rough openings as built (the architecture's were smaller/lower): garage 3,00 × 2,20 (lintel 11×7,5, not
   22×7,5); sala sliding (M3) and the three bedroom sliding doors (M9, M12, M14) **2,00 × 2,40**; entrance
   (M23) 0,94 × 2,20; service door (M5) 1,04 × 2,20 (superseded 2026-10-19, see registo: labels swapped — M23 is on P11
   at the NW corner, the **despensa service door**, 0,80 in the approved table; M5 is on P03 beside the wing, the
   **entrance**, 0,90 in the table; the sizes stand. As built the entrance door is "uma porta maior e mais robusta que
   cabe naquele espaço" — it fills M5's 1,04 (user 2026-10-19, 18:12); M23: to ask (answered 2026-10-20, see registo:
   "sim coloca a encher o vão como na principal" — the despensa door fills M23's 0,94 too; the clearance between the
   rough opening and a frame: 2,5 cm each side, the company default)); kitchen window (M20) 1,50 × 0,95; WC windows (M6, M18)
   0,75 × 0,75; P12 window (M24) 0,75 × 0,95; window sills (top of the 11×7,5) ≈ 1,03–1,04; interior doors
   **0,87 × 2,03** (exactly the company standard), 8 of them.
5. **Escadas (ladders of noggings) where another wall meets.** Four 11×3,5 / 7,5×3,5 noggings at 0,66 between
   two studs, in the receiving module, at every junction (interior walls on the exterior ones: M22 at P13,
   M19 at P15, M18 at P17 …; and at the corners, e.g. M1 west end for P12). *Why:* fixing for the abutting
   module.
6. **Corners.** The corner stud is a 11×7,5 at the end of the wall that runs through; the wall that stops ends
   on its own 11×7,5 laid across. Which wall runs through, as built: P11 (north) at both its corners, P03
   (south, main block) at the west corner and up to the re-entrant corner (it ends at x 10,78 on the outline),
   P01 (wing south) at the SE corner — but at the wing's SW corner **P14 runs through** (M6 2,57 from y 0) and P01
   starts after it; P14 then stops 0,035 short of P03's inner face (its 11×7,5 end against P03's end).
   *Why (user 2026-10-19, 15:48):* "sim e é suposto ser assim a lógica sempre, não temos uma regra específica para isso."
   — one wall through and one abutting at every corner, always; which one: no specific rule.
7. **Interior walls** run between the exterior walls' inner faces (e.g. P13: 1,10 + 2,65 + 2,65 + 1,88 = 8,28)
   and stop on the frame of the wall they meet; all 12 interior walls of the plan are there, on the plan's
   centre lines (± 1 cm).

## Cut lists (D2503) and the model
| Section | D2503 pieces / metres | Model v5 pieces / metres |
|---|---|---|
| 11×3,5 exterior | 220 / 473,0 | 233 / 475,6 (studs split at the lamelada pockets) |
| 11×7,5 exterior | 50 / 139,0 | 51 / 140,3 |
| 7,5×3,5 interior | 199 / 379,1 | 207 / 374,2 |
| 7,5×11 interior | 24 / 46,3 | 24 / 46,3 |
Exterior studs 94 × 3,43 (11×3,5) + 35 × 3,43 (11×7,5); interior 109 × 2,46 + 16 × 2,46 (7,5×11).
(2026-10-21, see registo: the "studs split at the lamelada pockets" in the model column is wrong — the user: the beams
"ficam por dentro e encostadas as da estrutura não atravessam ou fazem com que as da estrutura sejas separadas em dois
pedaços"; the studs are whole, as D2503 draws them; model v6.5, `modelos.md`.)

## Compared with the builder's modules (model v4)
| Wall | v4 (builder) | D2503 (as built) |
|---|---|---|
| P11 north | 3,00 3,00 3,00 2,75 3,00 2,75 | 2,53 2,21 2,21 2,19 2,21 2,64 2,21 1,30 |
| P03 south | 3,42 1,27 3,00 1,60 1,60 (to 10,89) | 3,82* 0,91 2,58 1,74 1,74 (to 10,78) |
| P01 wing south | 3,00 1,37 2,35 (from 10,78) | 1,81 2,21 2,58 (from 10,89; drawn 2,61) |
| P12 west | 3,00 2,74 2,54 | 1,35 2,21 2,21 2,51 |
| P14 wing west | 2,39 (y 0,11–2,50) | 2,57 (y 0–2,57) |
| P18 east | 3,00 1,91 4,35 1,52 | 2,56 2,21 2,15 0,32 2,15 1,38 |
| Interior | 3,00 maximum, joints anywhere | 1,78 / 2,65 grid modules + door and remainder modules |
What the builder got wrong and why: (1) it filled walls with 3 m modules (the user's "3 metros" from memory)
instead of grid modules of 5 / 4 / 6 bays with a 2,64–2,72 factory maximum; (2) two long modules over 3 m
(4,35 with two sliding doors) where the company splits them at the pier (2,15 + 0,32 + 2,15); (3) every
corner "X walls through" — at the wing's SW corner P14 runs through; (4) the openings at the architect's
size (2,20 doors, 2,00 sliding doors) — as built 2,40 for the sliding doors; (5) a 22×7,5 lintel over the
garage door — as built 11×7,5; (6) no escadas at the wall junctions; (7) modules 2,55 + a separate parapet —
as built one 3,50 module. Positions agree within 1 cm (both read the same architecture).

## Compared with the module divider (2026-10-20, configurator phase 1)
`ferramentas/modelo/divisor_modulos.py` splits a wall by the rules above (user 2026-10-20: "dividir a casa nesse
diferentes módulos … dependendo dos vãos que o cliente escolher e paredes interiores"; go-ahead the same night: "Avança
com a fase 1: o divisor de módulos, testado contra o D2503 de Torres Vedras."). Check: `python
ferramentas/modelo/divisor_modulos.py --comparar "Construção Torres Vedras/modelos/casa/modulos_D2503.json" --svg …`
— every wall divided with D2503's own wall ends, openings and junctions, then compared (picture:
`divisor-vs-D2503.svg`; v = with an opening, r = a remainder, * = built on site):

| Wall | D2503 | Divider |
|---|---|---|
| P11 north | 2,53v 2,21 2,21 2,19v 2,21 2,64v 2,21 1,30 | 2,53v 2,21 2,21 2,96v 2,78v 2,56r 2,25 |
| P03 south | 3,82v* 0,91 2,58v 1,74 1,73v | 3,39v* 1,34 2,47v 2,21 1,37v |
| P01 wing | 1,81 2,21 2,58v | 2,04r 2,21 2,36v |
| P12 west | 1,35 2,21 2,21 2,51v | 2,69 2,65 2,95v |
| P18 east | 2,56 2,21 2,15v 0,32 2,15v 1,38 | 2,25 2,21 2,46v 0,33 2,15v 1,38 |
| P14 wing west | 2,57v | 2,57v |
| Interior (12 walls) | 23 modules | 23 modules; 12 identical (all of P02, P04, P05, P06, P08, P09, P10, P16; one in P15, one in P17; differing: P07 D2503 1,96 + 1,78, divider 1,09r + 2,65; P13 D2503 1,10 2,64 2,65 1,88v, divider 1,78 1,77 2,64 2,08v) |

Since the user's answers of 2026-10-20 (night) — exterior modules "podem ir até 3 m" — the divider uses fewer, longer
exterior modules (48 in all instead of 50: P11 7, P12 3); with the first limit (2,65, TV's largest) it gave P11
2,53v 2,21 2,21 2,63v 2,21 1,25v 2,21 2,25 and P12 2,25 2,21 2,44v 1,38.
- **Rules**: in both, every opening sits inside one module and no joint falls where another wall meets; one module
  built on site each (the garage); one pier each (P18, the interior wall P07 meets there). The divider makes more
  plain whole-bay modules (23 vs D2503's 20) and fewer remainders (6 vs 11), with a few more irregular margins round
  the openings (23 vs 20). 19 of the 50 modules are identical, 11 of the 32 joints.
- **The differences are all where the remainder of a wall goes** — into the module of an opening, a corner module, or
  a module of its own, at which end. D2503 has no single rule for it (P11 at the east end, P12 / P18 / P13 / P15 / P17 at
  the south end, P03 between two openings, P01 in the door module), and the user leaves the split to us per house
  ("dependendo da casa vê o que se enquadra melhor", 2026-10-19). The divider picks by the costs in
  `sistema_construtivo.json` `estrutura.divisor` (ours, calibrated on this drawing). Shown to the user 2026-10-20
  (night), who left it to us: "Vai com a opção que achares melhor, força nisso confiança".
- **From the architecture alone** (the TV config without `modulos_reais`, `_trabalho/divisor/`): 25 exterior + 23
  interior modules (27 + 23 with the 2,65 limit, as D2503); the two P18 sliding windows (architect 0,14 apart, jambs
  overlapping) moved 16,5 cm each for a 0,32 pier — what D2503 did, and the default for two windows (user 2026-10-20:
  "por defeito podes assumir que sim quando esta situação acontece desde que sejam duas janelas como neste caso"); the
  garage module 3,39 "* Painel a executar em obra", as short as the opening needs (user: "depende da situação mas
  neste caso sim usa o tamanho que o vão precisa"). Builds and validates in Blender with 0 issues. The real TV model
  keeps D2503's modules (`modulos_reais`; geometry unchanged except the "*" flag on M1).
- (Answered 2026-10-20 night: where the remainder goes — ours; the exterior factory limit — "os módulos exteriores
  podem ir até 3 m", so 2,21 is not the transport limit.)

## Open (to confirm with the user)
- Why 2,21 for the plain exterior module and 1,78 / 2,65 for the interior ones (our reading: the 40 cm grid),
  and the factory maximum (≈ 2,65–2,72; M1 3,82 built on site). (Factory maximum answered: normally ≤ 3 m, user
  2026-10-19; exterior "podem ir até 3 m", 2026-10-20 night — so 2,21 is not the 2,55 transport width. Why 5 / 4 / 6
  bays: still open.)
- The corner rule (which wall runs through): P14 through at the wing's SW corner, P01 through at the SE corner.
- P01's modules add up to 6,64 in the elevations (M9 2,61) but 6,61 in the plan (M9 2,58): the model uses
  the plan.
- The lameladas (8,50 / 11,00, wall to wall in the roof drawing) cross the exterior modules, whose studs are
  drawn continuous: are the pockets cut on site? (the model cuts them). (Superseded 2026-10-21, see registo: they do
  not cross — they end inside against the modules, the studs whole as drawn; at most the beam notched to fit. Left:
  8,50 / 11,00 = the outer depths — the ordered length? `estado.md` Open questions.) (Answered 2026-10-21, see
  registo: nominal lengths; "cortamos para "encaixar" no tipo de obra que temos" — cut to fit each house.)
- The garage lintel 11×7,5 over 3,00 (the user's rule 2026-10-13: 22×7,5 from 2,8–3 m).
- (Answered 2026-10-19, see registo: factory modules normally ≤ 3 m, choose per house — why 2,21 still open, transport
  asked; the garage lintel 11×7,5 confirmed by the company's engineer, "por norma é 22x7,5"; the interior walls bear the
  lameladas (the norm); exterior rough openings = the maker's size + a clearance, a print of the openings to follow.
  Not understood, explained again with images: the corner rule and the pockets ("entalhes") — still open.)
- (Answered 2026-10-19, 15:48, see registo: M1 and the bigger modules "são montados em obra"; the corner rule — one
  through, one abutting, "não temos uma regra específica" for which; the pockets — "sim há um entalhe feito e a viga fica
  por dentro" (factory or site: not said); the print = the table "PROJETO APROVADO" (`docs/materiais.md`); the lintel
  confirmed ("sim"). Still open: why 2,21 (transport not answered); P01 2,64 vs 2,61; the exterior clearances and the
  basculantes 0,80 (table) vs 0,75 (these modules) — `revisao-tecnica.md` #20.)
- (Answered 2026-10-19, 18:12, see registo: the interior modules are made to the amarração — 2,543, not D2503's 2,53
  (conflict, item 1); the notches "feito em obra" (cut on site — why the studs are drawn whole) (reading superseded
  2026-10-21: the notch is in the beam, the studs are whole because nothing crosses them); 2,21 from transport —
  "não estou a ver qual é o módulo 2,21 mas diria que sim" (tentative); the basculantes as modelled (0,73 in these 0,75
  openings — "está ótimo como fizeste"), the entrance door fills M5; the table = frame size without clearance ("acho
  que"), a clearance normally counted. Still open: the clearance value; M23; D2503 2,53 vs 2,543; M18 2,64 over the 2,55
  transport width; P01 2,64 vs 2,61.)
- (Answered 2026-10-20, see registo: the clearance — 2,5 cm each side by default, it depends on the frame; M23 fills its
  opening. Still open: D2503 2,53 vs 2,543; M18 2,64 over 2,55; P01 2,64 vs 2,61; the clearance in height.)
  (Answered 2026-10-20, 13:25, see registo: the clearance in height too — 2,5 cm by default, depends on the frame
  ("nem sempre é essa a folga"). With it the approved table fits these rough openings only for the two doors in width —
  `revisao-tecnica.md` #20. Every opening gets remates round the frame — #23.)
- (Details keeper 2026-10-16) Checks in `revisao-tecnica.md`: #17 lintels 11×7,5 under lamelada loads (garage 3,00,
  sliding doors 2,00 on P03 / P01), #19 lamelada pockets vs the 0,435 grid, #6 interior top 2,53 vs the lameladas'
  underside 2,653; drawing gaps (3,50 vs 3,4915, P01 2,64 vs 2,61) in `desenhos.md`.
