---
name: modelo-blender-madeira
description: Build or update the editable Blender model of a DiscoverCasa timber-frame house from its DWFx drawings (engineer's module drawings, or only the architecture plan) - timber structure plus the DiscoverCasa build-up layers (OSB, membrane, finish options, wool, Pladur, floors, ceilings, sandwich roof) - with validation, quantities and preview renders, or set up a new house type. Use for any Blender/3D modelling of DiscoverCasa houses.
---

# Timber-frame house → Blender

## Run
```bash
python ferramentas/modelo/construir_casa.py "<Construção X>/modelos/<tipo>/config.json" [--sem-extrair] [--sem-previews] [--blender PATH]
```
Steps: `extrair_casa.py` (DWFx → `<tipo>_geometria.json`) → if config `estrutura.sistema` =
`"discovercasa"`: `estrutura_dc.py` (→ `_trabalho/modelos/<tipo>/geometria_dc.json`, used by the next
steps) → `camadas.py [--geometria]` (build-up layers →
`_trabalho/modelos/<tipo>/camadas.json`) → Blender `build_casa.py` (→ `.blend`, structure `.glb`,
complete-house `.glb`) → `validar.py` (must print `issues: 0`) → `quantidades.py` (→ `quantidades.csv`)
→ `previews.py` (→ `_trabalho/renders/<tipo>/`: estrutura_SE/NW, seq_exterior_1..n (visible option), opcao_A/B/C_SE,
seq_interior_1..5, corte_transversal, alcado_sul/este, planta_piso0/1). Read 2–3 previews to confirm;
don't read the JSON/.blend. ≈ 35 s. Blender runs in background (no MCP). Only `config.json` is edited
by hand (company defaults: `ferramentas/modelo/sistema_construtivo.json`).
`python ferramentas/modelo/camadas.py config.json` alone prints layer totals and rooms (fast check).

## House from an ARCHITECTURE plan only (builder; Torres Vedras, 2026-10-15)
No module drawings: the walls come from the plan, everything else from the DiscoverCasa standard.
1. `python ferramentas/modelo/planta_arquitetura.py "<plan>.dwfx" --folha N --regiao X0 Y0 X1 Y1 --escala 200
   --saida "<model>/planta_paredes.json" [--svg check.svg]`: wall faces = red strokes (licensing
   convention) paired 0,08–0,40 m apart, walked in 1 cm steps (both faces = wall, one face = T-junction or
   a window frame drawn on the face, none + jambs crossing the wall = opening ≤ 3,6 m); door = magenta
   swing beside it; exterior side by ray casting (works for L shapes). Check the SVG against the plan.
   **A house built in the configurator** (no drawings): `python ferramentas/configurador/para_construtor.py
   "<house>.json" --saida <folder> [--construir] [--documentos]` writes this `planta_paredes.json` and the config of
   step 2 from the client's choices (format and assumptions: `configurador/docs/especificacao.md` §8; example
   `configurador/exemplos/casa_exemplo_L.json`), then go on from step 3 with that config.
2. `config.json` with `"planta"` (see `Construção Torres Vedras/modelos/casa/config.json`): `niveis.pe_direito`,
   `modulos` (`divisor`, old `comprimento_max`), `aberturas` (heights, per-wall types), `cobertura` (`tipo` "platibanda",
   ridge `cumeeira_y`, `aguas`, `vigas_teto` zones, `inclinacao_pct`; or `tipo` "a_vista" — an exposed sandwich-panel
   roof — with `forma` "duas_aguas" | "quatro_aguas" | "misto" (L / T / U: the main body hipped, the wings' ends
   gables), `inclinacao_graus`, `beirado`, `empena`), `fundacao.contorno`
   (architect's outer outline), `camadas` overrides (`null` removes a finish option).
   **Exposed roof** ("a_vista", 2026-10-21): `ferramentas/modelo/telhado.py` makes the roof surface from the outline (main
   body + wings, 2 águas with empenas or hipped, one slope; `python ferramentas/modelo/telhado.py <house>.json --svg
   <plan.svg>` prints the faces / lines and draws the plan), `telhado_estrutura.py` its timber (beams per wing down the
   slopes, headers where a wing opens, edge beams, purlins, prumos, rincão / laró members, empenas), `camadas.
   cobertura_faces` the panels, caps, gutters and downpipes, the façades cut by the roof profile (`sob_faces`); no
   parapet, exterior modules to pé direito − 0,05; validation against the roof faces. Where two roofs share a plane
   (a wing flush with the main body's eave) the earlier roof keeps the overlap (a constant half-plane in the
   subtraction — fixed 2026-10-22: a duplicate piece had hidden the eave line and doubled ≈ 8 m² of panels on the
   4-água L); check a roof's plan area = the outline with its overhangs. One slope = one plane: purlins
   (`telhado_estrutura`, one aligned set; a lower wing's own ridge purlin over its part only), panel counts
   (`camadas.cobertura_faces`) and the documents group faces by `plano`, named after the first rectangle (R1 N). The
   squarish-body ridge rule applies to 2 águas only (hipped: ridge on the longer side, beams across the short one).
   A wing wider than its parent crosses it; where the parent ENDS inside that wing it runs into it up to the wing's
   ridge without overhangs (`parar_no_cume`; else a "mini telhado" stood out of the wing's slope), and the wing's side
   on the outline there keeps its eave. `_cortar`: an edge crosses the line only from one side to the other (an end
   within EPS gave a vertex millions of metres up). Audit a change with every configurator shape × roof × slope × eave.
   Configured houses (`para_construtor`): interior walls meeting end to end make a corner (X through, Y against —
   `casa_planta` `cantos_int`); `faces_interiores` {side: finish} = an outside wall's inner face (exterior panels get
   `acabamentos`); `pavimentos` [{ponto, acabamento}] = a room's floor (`camadas.pavimentos`, a collection per finish);
   under an exposed roof the rough top may reach the pé direito and the exterior modules rise (the ceiling suspension)
   when the lintel over the highest opening needs it (a note); beirado clamped to 0,20–0,50 (JSON `beirado_min` /
   `beirado_max`; max 0,50 since 2026-10-28). Hidden roof: `cobertura_escondida` picks one água (`uma_agua`) or two
   slopes per house (`painel_oculto.comprimento_max`).
3. `construir_casa.py` runs `casa_planta.py` instead of the extraction: exterior 110 frame kept inside the
   architect's wall (inner faces kept), X walls through the corners, every wall split into modules by
   `divisor_modulos.py` (the company's way read from D2503: whole bays of the 40 cm grid — exterior 5 = 2,21,
   interior 4 / 6 —, each opening inside one module, a 0,32 pier between close openings — they are moved apart and
   the build prints "divisor: … afastados" —, no joint where another wall meets, ≤ 3 m in the factory, longer ones
   "* Painel a executar em obra"; sizes and costs in `sistema_construtivo.json` `estrutura.divisor`; config
   `modulos.divisor: false` = the old ≤ `comprimento_max` split; check it against a company module drawing with
   `python ferramentas/modelo/divisor_modulos.py --comparar "<model>/modulos_<obra>.json" --svg <file>`),
   interior doors 0,87 × 2,03, single storey (`pavimento.sem_piso`), ceiling beams in the zones,
   slopes from one ridge (`cumeeira_y`, `aguas`, slope from the drawings) on prumos + purlins; roof by
   `camadas.cobertura_platibanda` as DiscoverCasa builds it (user 2026-10-15/16): every exterior wall rises
   to the same height (parapets, piso 2, wool inside, clad on the roof side too: `cobertura.platibanda_
   interior`); on the LOW side of each slope a caleira oculta inside the parapet (casa_planta: 110x75 laid
   flat + OSB 22 + 110x75 upright, `cobertura.caleira_oculta`; panels end 5 cm into it; aluminium lining
   with end caps), downpipes from it through the parapet into the facade's batten cavity, hidden by the
   Tremolo and clear of the openings; rufo on every parapet, running on over the cladding at outside corners;
   facades stepped to the top of the walls behind (`degraus`); validation uses the frame outline
   `contorno_estrutura`. Before handing a model over, look at the close-ups that the build renders with
   `blender/pormenores.py` (`_trabalho/renders/<model>/pormenores/`: every outside corner from above, every
   re-entrant corner from the notch and from the roof, the ceiling of the largest room) — corners, chapéus,
   parapet ends, gutters and ceiling slots are what the user checks.
4. **As built at Torres Vedras (drawing D2503, `Construção Torres Vedras/docs/cobertura-D2503.md`)** — when the
   company's roof drawing exists, follow it: `paredes.exterior = "face_exterior"` (modules on the foundation
   line), `cobertura.estrutura = "lameladas"` (`estrutura.lameladas` 20×10 in equal bays ≤ 0,92 wall to wall
   through the walls, on the amarração 11×7,5 on the inner face; exterior modules framed to the amarração,
   studs running on into the parapet module; `estrutura.madres` 11×7,5 on prumos from each gutter at ≤ 1,265,
   ridge pair 0,10, the longest slope's gutter madre on the lameladas), `niveis.teto_estrutura` (underside of
   the lameladas), `cobertura.caleiras` per gutter wall (`saidas` "inicio"/"fim", `queda`), `platibanda.topo`.
   The gutters (0,31) sit on packing on every lamelada with the fall; the gutter walls are lined by the
   gutter up to the top; panels are laid from the east end (`grelha_x`).
5. **When the company's module drawings exist** (sheets "Módulos Exteriores" / "Módulos Interiores", e.g. TV
   D2503): `python ferramentas/modelo/modulos_dc.py "<modules>.dwfx" --planta "<model>/planta_paredes.json"
   --saida "<model>/modulos_<obra>.json"` (checks: every module found, openings listed, the cut-list totals vs the
   sheet's "COMPRIMENTO DAS VIGAS"), then `"modulos_reais": {"ficheiro": "modulos_<obra>.json"}` in the config: the
   builder uses those modules as they are (`Construção Torres Vedras/docs/modulos-D2503.md`).
6. **Windows and doors** from the project's table (e.g. "PROJETO APROVADO"): `config.json`
   `camadas.caixilharia.itens`, one item per opening — `modulo` (the D2503 module it sits in), `divisao`, `tipo`
   (fixo / basculante / correr / porta / seccionado), maker's `largura` × `altura`, `vidro` (transparente / fosco),
   `estore` (true → shutter box over it), descriptions. `camadas.py` `caixilharia()` centres the element in the
   module's rough opening (nearest in width) at the outer side; it is clamped to the opening minus `folga` — read the
   build's warnings and say when a table size does not fit. Defaults (profiles, materials) in the standard's
   "caixilharia".
7. **Pergola** (optional): `config.json` "pergola" — `x0`/`x1` (numbers, or "casa" = the house's finished ends),
   `y_frente`, beams `vigas_x` or `vigas_origem` + `vigas_espacamento`, `pilares_x`, `z_vigas` (top of the front
   beam), `inclinacao` (beams falling to the front), sections of `pilar`, `viga_frontal`, `viga_encosto`, `vigas`,
   `ripas`, optional `telha` and `caleira` (tubos_queda_pilares). Needs `fundacao.contorno`: `casa_planta.py` finds
   the facades facing the pergola on the finished outline (`desloca`), puts one ledger on each over the battens,
   runs every beam to its facade, the slats to the finished faces (collection 1.10; the Tremolo is cut round the
   ledgers and beam ends); `camadas.py` `pergola_cobertura` lays the tiles, the exposed gutter and the downpipes
   (collection 8). Validation skips the footprint check for 1.10.
8. **Chapéus**: every corner top is covered once — at an end where a wall stands across, the chapéu runs to that
   wall's far edge (X chapéus cover the corner, Y chapéus stop against them), whichever frame runs through. After
   changing `chapeus()` check the tops for overlaps and gaps (user 2026-10-20: they "não podem deixar o topo
   destapado" and "não dão overlap uns aos outros").
9. **Hidden-gutter outlets**: every downpipe gets a hole in the gutter lining where its stub goes through the
   parapet into the facade cavity (user 2026-10-20: "nao existem os buracos par agua escoar para os tubos de
   queda"); the pipes sit inside the gutter's length (`tubos_queda`, `cobertura_platibanda`).

## Production documents (the company's D2503 standard) — `ferramentas/documentos/gerar.py`
`python ferramentas/documentos/gerar.py "<project>/modelos/casa/config.json" [--svg]` rebuilds the model data
(casa_planta + camadas, no Blender) and writes to `<project>/documentos/`: `<obra>_Modulos.pdf` (plan of the
modules with their lengths, elevations of every module — members by section, openings —, quadro de dimensões e
quantidades with "* Painel a executar em obra", comprimento das vigas), `<obra>_Cobertura.pdf` (lameladas
+ amarração with axis / clear dims, madres + prumos heights + caleiras with falls and outlets, sandwich panels,
typical sections cut through the model at a lamelada of each length), `<obra>_Listagem_Material.pdf/.csv` (by
chapter with purchase units, caixilharia items, cut list). Config "documentos": `obra` (code), `projeto`, `local`,
`revisoes`. **Exposed roof** (geometry `cobertura.tipo` "a_vista", since 2026-10-22): `_Cobertura.pdf` becomes
`doc_cobertura_avista` — (1) águas, cumeeiras, rincões, larós (true lengths, ridge levels, slope arrows, overhangs,
area in plan / sloped), (2) vigas de apoio ao teto / lameladas by length letter, zones Z1… with count, section,
spacing and span, headers (vigas de bordadura) and edge beams, (3) madres per slope (R1 N …: lines and spacing),
rincões / larós, prumos (height range), calços, (4) panels per slope (joints at the useful width, count × longest
length) with every flashing, gutter and downpipe, (5) sections across each roof's ridge through a ceiling beam, with
the levels. `_Modulos.pdf` gets an "Empenas - Alçados" sheet (the gable triangles EMP R1N …, factory-made like the
modules) and their rows in the table; their members are in the cut list and the material list (before 2026-10-22 the
gable timber was left out of both — 63 pieces / 0,28 m³ on the 2-água test L). Since 2026-10-21 the ceiling beams of a hidden roof end at the modules' inner face, on the amarração
ring — they never cross the modules nor cut a stud (user: "essas vigas ficam por dentro e encostadas as da estrutura
não atravessam"; at most the beam is notched to length) — so the modules have whole studs and no notches; the
generator's notch drawing and the cut list's joining of split studs only matter for a model built before that.
Check the sheets with `--svg` (previews in `_trabalho/documentos/<obra>/svg/`; to look at them, render with headless
Edge from a path without spaces: `msedge --headless=new --user-data-dir=<tmp> --screenshot=<png> --window-size=1680,1188 file:///<svg>`;
headless Chrome from PowerShell works with the repo path as is, `--force-device-scale-factor=2` for a sharp image; a
close-up: copy the SVG with a smaller `viewBox` in sheet mm).
The module sheets and the cut list use `membros_fabrico` (stored by casa_planta: the members as made) and `entalhes`
(empty since 2026-10-21). TV check (2026-10-20): identical to the members drawn in D2503 (228 × 11x3,5,
50 × 11x7,5, 24 × 7,5x11, 207 × 7,5x3,5); D2503's own table says 220 / 50 / 24 / 199.

## New house type (e.g. Tipo 2)
1. Copy `modelos/tipo1/config.json` to `modelos/<tipo>/`; set `nome`, `descricao`, `dwfx`, `saida`.
2. Locate views (skill ler-dwfx): `regiao_alcados`, `plantas` {"0": GF wall plan, "1": upper}, `pavimento.regiao`,
   `cobertura.regiao` (sheet mm). Regions must fully contain their members.
3. Measure from the sections with `dwfx.py pecas/texto --regiao`: `casa` dims, `niveis`
   (topo_paredes_piso0, topo_vigas_pavimento, piso1_exterior/interior), roof `cumeeira_y/z`,
   `inclinacao` (from a rafter polygon), `apoio_z`, `frechais`; stair opening; raft `contorno` (model coords);
   `camadas`: finished ground floor `pavimentos.piso0.acabado_z`, roof overhangs `cobertura.beirado/empena`.
4. Run `extrair_casa.py` alone first; every "check …" line (studs matched < total or extra studs) needs a
   look: fix with `alias`, `rotulos_errados`, `forcar_sentido` or `correcoes` in the config.
5. Build, validate (0 issues), look at previews (planta_piso0/1 show the detected rooms), then document
   decisions in the project's `docs/modelos.md` and `docs/estado.md`.

## How extraction works (for debugging)
- Members: triangle pairs merged along their shared longest edge (`pecas.build_members`).
- Elevation = cluster of touching members in `regiao_alcados`, named by the label just below-left.
  Studs = tall thin members (deduplicated: drawn in 2 pieces around noggings). Frame = bottom plate extent.
- Placement: each plan label gives a first guess (label at the panel end; offsets in `rotulo_offsets`);
  the elevation's stud centres are matched to the plan's cut studs in both directions (±4 mm search),
  then refined by the median offset. Output: origin (elevation u = 0), direction of +u, thickness.
- Exterior facades snapped: N/S long walls run through the corners from X = 0; W/E end walls fit
  between them from Y = thickness (widths must add up, else a warning).
- Symmetric panels: direction by convention in `forcar_sentido` (exterior elevations are viewed from
  outside: N/E facades → +u points west/south). Upper panels with sloped tops are flipped automatically
  so the high end faces the ridge.
- Member depth = wall thickness, except members whose drawn face is ≈ 160 mm (verge rafters on gable
  panels) → 80 mm on the outer half.
- Roof: rafters from the roof plan (drawn TRUE LENGTH: s = distance from the ridge along the slope),
  plumb at the ridge, level-cut on the eave plate (`apoio_z`); outer gable rafters skipped (they belong
  to the gable panels); ridge blocking from `tarugos_s`. `cumeeira_z` = top of the rafters on the ridge.

## DiscoverCasa structure (`estrutura_dc.py`, standard in `sistema_construtivo.json` "estrutura")
Keeps the drawn house (outer faces, interior wall centre lines, module joints, openings, levels) and
re-frames every module (rules: `conhecimento/sistema-construtivo.md` §2, §5, §6):
- Facade modules 110 deep with the outer face fixed; interior 75 deep on the same centre line; wall
  ends that met a perpendicular wall move to its new face; interior walls standing against an exterior
  wall follow its new inner face.
- Doorways the drawings leave as a gap between modules (found with `camadas.fechos_salas` +
  `portas_virtuais`) get a "Bandeira" module above the door (`estrutura.porta_interior` 2.10 m above the
  finished floor: padieira, short studs, top plate) and the module ends beside them become 110x75
  ombreiras. Without it the doorway is open from floor to roof.
- `emoldurar`: plates (bottom plate cut at doors), 110x75 jambs / header / sill (220x75 lintel if
  ≥ `verga_grande.vao_min`, 2.8 m), 110x75 end post only at house corners (else a 35 stud), studs at 40 cm clear from the first
  end (skipped within 5 cm of a reinforcement), cripples inside openings. Openings come from the
  drawings' stud layout, clipped under the header / above the sill; they are written as explicit
  `aberturas` (used by `paineis.py` instead of re-detecting).
- Upper floor: all modules end at the eave walls' top; afinação + amarração (exterior) / afinação
  110x75 (interior) → flat ceiling; ceiling beams 220x75 N–S at 1 m (1.7), posts + purlins 110x75 (1.9),
  gable triangles `EMP.O/E` (1.8, piso 2) framed with `emoldurar_empena`.
- Roof plane = top of the purlins; the eave purlin sits on the ceiling beams over the wall.
  `estrutura.cobertura_manter`: `"inclinacao"` keeps the drawn pitch (roof rises), `"cumeeira"` keeps
  the drawn ridge (pitch flattens). The geometry's `cobertura.plano_z_cume` is used by `validar.py`.
- Intermediate floor (`estrutura.pavimento`): joists 220x75 N–S at ≤ 1 m on the ground-floor walls (outer
  ones at the E/W faces, trimmers beside the stair opening, a header closing the cut joists; the drawn
  floor's E–W main beams — pieces ≥ 2 m inside the house, not the stair trimmer — kept as 2 × 220x75 flush,
  the joists cut at them: `pavimento.vigas_principais`), battens 110x75
  flat E–W at 0.60 m centres, OSB 22 deck over the whole footprint (build_casa.py, `niveis.osb_pavimento`,
  `pavimento.deck_margem` 0). Every upper wall stands on the deck; the extra depth vs the drawings
  (`niveis.subida_pavimento`) lifts the upper floor, ceiling and roof, so the upper clear height stays.
  Upper openings keep their height above the floor. Floor wool: `tetos.la_pavimento` (5.6), laid on the
  ground-floor false ceiling between the joists. Without `pavimento` the drawn floor is kept.

## How the build-up layers work (`camadas.py`, `paineis.py`, `geometria2d.py`)
- Values: `sistema_construtivo.json` (DiscoverCasa standard) deep-merged with config `camadas`
  (project overrides). Build-up facts and products: `conhecimento/sistema-construtivo.md`.
- Openings per panel (`paineis.py`): bays ≥ 0.55 m between full-height studs (stud pieces merged; full =
  bottom plate to within 0.25 m of the frame outline top). Cripples below a member → sill (window
  above), above → header (door below); else first member ≥ 1.8 m → door head, otherwise window = gap at
  floor + 1.6 m. PI panels get doors only; walls lower than 1.8 m none. Sloped top plates are exported
  in small pieces: anything within 0.25 m of the outline top is "top plate".
- Facades = boundary of the free space outside the PE footprints (plan grid). Rooms = free spaces
  inside, per floor, after virtual closures: doorways (gap ≤ `divisoes.porta_max` 1.05 m at a wall end), ducts (parallel walls
  < 0.38 m apart); a closure isolating a space < 0.5 m² is dropped towards the smaller neighbour.
- Corners are butt joints: faces running E-W run through (extend by the outer offset at outside
  corners), N-S faces stop against them. Layers are prisms per face; sheets on a grid with a visual gap.
- Exterior layers stop under the roof covering (rafter top + purlin height, or the purlin plane in the
  DiscoverCasa structure); interior linings stop at the ceiling (flat on the ground floor; upstairs
  sloped under the rafters, or flat under the ceiling beams in the DiscoverCasa structure); wool sits
  in the stud cavities (80 mm against the outer face of facade panels, 60 mm centred in partitions).
- Flat ceilings (`tetos` in `sistema_construtivo.json`): perfis at 0.40 across the beams/joists, hung
  `suspensao.folga` under them by one régua de suspensão per perfil per beam (upright on the beam side),
  cantoneira on the room's real wall faces (bought in 3 m bars: `unidade`/`comprimento_unidade_m`),
  Pladur grid below, `tetos.la` wool on top for the floors in `la.pisos` (the gable triangles then get
  no wool). On flat-ceiling floors the wall linings run past the module top: Pladur to the ceiling
  underside, OSB to the beams.
- Finish options: every option in `exterior.opcoes` is built in its own collection; only
  `opcao_visivel` is shown (and exported to the complete GLB). Materials of alternatives (Pladur H1/F,
  Microcimento) are stored with a fake user.
- New layer or product: add it to `sistema_construtivo.json` (type `placas`, `continuo`, `ripas`,
  `tabuas`) + material colour; document it in `conhecimento/sistema-construtivo.md`.

## Known drawing traps (Sobral)
Stacked labels (PI2.09/10, PI2.11/12/13, PI2.14/15) → `alias`; upper-plan "PE2.07/08" = PI2.07/08 →
`rotulos_errados`; "0,40" = clear gap; upper exterior walls on rim joists (2.96) vs interior on OSB (2.978);
section FF' and gable elevations define the roof, not the roof plan's lengths.

## Model conventions
Axes X east / Y north / Z up from slab top, metres. One Empty per module + children (timber + wool);
collections 0 foundation · 1 structure (1.1–1.6; DiscoverCasa: 1.6 tie/levelling beams, 1.7 ceiling
beams, 1.8 gables, 1.9 posts + purlins, 1.10 pergola) · 2 outside of walls (2.1 OSB, 2.2 membrane, 2.3+ options)
· 3 inside (wool, OSB, Pladur) · 4 floors (4.3 structural OSB) · 5 ceilings (5.1 réguas de suspensão,
5.2 perfis, 5.3 cantoneira, 5.4 Pladur, 5.5 ceiling wool, 5.6 floor wool) · 6 roof covering · 7 caixilharia
(7.1 frames and leaves, 7.2 glass, 7.3 roller shutters, 7.4 doors) · 9 labels;
Portuguese names; timber properties seccao/tipo/painel/piso/comprimento_m/volume_m3, layer properties
camada/produto/area_m2/comprimento_m/pecas/unidade/divisao; timber colours as in the drawings
(DiscoverCasa: 110x75 red, 220x75 orange, like the company's module drawings).
Check gaps with a top view of one floor at ceiling level (walls + 1.6 + linings + ceilings, roof hidden)
and an interior view from below: slots there are real modelling errors, not render artefacts.
Save with the lowest installed Blender ≥ 4.4 (`ferramentas/comum.py`) so files open on every device;
`.blend1` backups are removed automatically.
Workbench renders do not cap cut objects: in section previews a sloped ceiling or a cut board can look
missing — check coordinates in `camadas.json` before "fixing" geometry.
