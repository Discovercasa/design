# Blender models — Sobral

Procedure and pipeline internals: skill `modelo-blender-madeira`. Build-up rules and products:
`conhecimento/sistema-construtivo.md`. This page = project-specific facts.

## Conventions (all models)
- Axes: X = east from the west outer face, Y = north from the south outer face, Z = up from the top of
  the concrete slab. Metres.
- One Empty per wall module, named as in the drawings, with its timber pieces (and its mineral wool)
  as children: move the Empty to move the module. Gable triangles: Empties `EMP.O` / `EMP.E`.
- Collections follow the build sequence: 0 Fundação (indicativa) · 1 Estrutura de madeira
  (1.1–1.5 walls and floor — 1.3 = floor joists and battens; DiscoverCasa structure: 1.6 vigas de amarração e afinação, 1.7 vigas de
  apoio ao teto 220x75, 1.8 empenas, 1.9 prumos e vigas de apoio à cobertura) · 2 Paredes | camadas
  exteriores (2.1 OSB 9, 2.2 Traspir 95, 2.3/2.4/2.5 finish options A/B/C) · 3 Paredes | camadas
  interiores (3.1 lã mineral, 3.2 OSB 15, 3.3 Pladur) · 4 Pavimentos (4.3 = structural OSB 22) ·
  5 Tetos (réguas, perfis, cantoneira, Pladur, 5.5 ceiling wool, 5.6 floor wool) · 6 Cobertura |
  revestimento · 9 Etiquetas (hidden).
- Only one finish option is visible (config `camadas.exterior.opcao_visivel`; Tipo 1: **B, ETICS**,
  chosen by the user 2026-09-24); the others are hidden collections: switch with the eye icon.
  Interior linings, floors and ceilings are one object per room so a room can get another material
  (Pladur H1/F, Microcimento are in the file, unused).
- Timber colours: DiscoverCasa structure — 110x35 light wood, 75x35 green, 110x75 red, 220x75 orange
  (as in the company's module drawings); drawings' structure — orange 160x80, green 100x80.
- Properties: timber seccao, tipo, painel, piso, comprimento_m, volume_m3; layers camada, produto,
  area_m2 / comprimento_m, pecas, unidade, divisao.
- Saved with Blender 4.4 → opens in 4.4+ (tested 5.2.2). Two `.glb` for devices without Blender:
  `..._Estrutura_Madeira.glb` (structure only) and `Casa_Tipo1_Completa.glb` (house with option B).
- `config.json` → `estrutura.sistema`: `"discovercasa"` (current) or `"desenhos"` (the engineer's
  160x80 structure with sloped ceilings, as modelled until 2026-09-24).

## Casa Tipo 1 — `modelos/tipo1/`
History: structure from the drawings 2026-09-23 · build-up layers 2026-09-24 · **DiscoverCasa structure
and flat upper ceiling 2026-09-30 (user)** · 2026-10-09: doorway walls, linings up to the ceiling,
22x7,5 ceiling beams at 1 m, the company ceiling system and 100 mm ceiling wool (user's answers) ·
2026-10-13: the DiscoverCasa floor between storeys (the upper floor and the roof rise 0.139 m) ·
2026-10-15: rebuilt with the updated standard (wood option A = contra-ripado 30×20 + battens 37,5×35 at 0,50)
and the ceiling fix for thin strips of a room (they were left without Pladur: +0,6 m² of ceiling Pladur).

### Structure (DiscoverCasa, `ferramentas/modelo/estrutura_dc.py`)
- Same house as drawn: outer faces 9.86 × 6.11, interior wall centre lines, module joints, openings and
  floor levels kept. Exterior walls 110 mm (outer face fixed, so rooms gain 5 cm per exterior wall),
  interior walls 75 mm; wall ends that met a perpendicular wall follow its new face, and interior walls
  standing against an exterior wall follow its new inner face, with the wall forming a duct with them
  (duct walls PI2.09 / PI2.10 both moved 5.3 cm east, the duct keeps its 0.35 m).
- Framing per module: 110x35 / 75x35 studs at 40 cm clear, single 35 plates, no noggings; 110x75 at
  the 4 house corners (two side by side on both floors) and around every opening (jambs, header,
  window sill); short studs above/below; doors without bottom plate. PE1.09 / PE1.10 (short walls
  inside the house) are framed as interior walls. 53 modules + 2 gable triangles + 4 bandeiras.
- Changes from the architecture set (2026-10-09, config `estrutura`): `remover_paineis` PI2.09/PI2.10 (the
  duct "will not exist", user) and `paredes_extra` PD2.01 continuing PI2.08 to the east wall; PD1.01 = WC 0.6
  east wall with a 0,87 door; `portas_extra` = the lavandaria's 1,4 m east opening (bandeira above);
  `camadas.divisoes.passagens_abertas` keeps the gap inside quarto 1.5 open (no door, no bandeira).
  `aberturas_alterar` PE2.08: the bathroom 1.2 window of the alçado nascente (Z 4,05–5,04) instead of the
  engineer's tall opening.
- Doorways that the engineer's drawings leave as a gap between two modules (no wall above the door) get a
  **bandeira**: padieira 110x75 at the door head (`estrutura.porta_interior`), short
  studs, top plate (and afinação upstairs), plus 110x75 jambs (ombreiras) on the module ends beside the
  door (head 2.03 m above the finished floor = door 2.00 + 3 cm, user 2026-10-09). Doors: PI1.10/PI1.11 (ground floor, 0.86 m), PI2.03 closet (1.01), PI2.06 corridor → bedroom
  (1.00), PI2.07/PI2.08 (0.90). Before 2026-10-09 these were open from floor to roof (the "gaps").
- Upper floor: every module stands on the floor OSB (Z 3.117) and ends at Z 5.47 (eave walls' top as
  drawn + 0.139); exterior walls get afinação 110x35 + amarração 110x75, interior walls afinação 110x75
  upright → top Z 5.58; 11 vigas de apoio ao teto 220x75 N–S at 1 m (user 2026-10-09; Z 5.58–5.80). The drawings' sloped partitions and gable modules become
  2.35–2.37 m modules; the gable triangles above are framed on the tie beam.
- Roof: 8 vigas de apoio à cobertura 110x75 (4 per slope, eave ones resting on the ceiling beams over
  the walls), 66 prumos 110x75 (under every purlin except the eave ones, on every ceiling beam — user:
  right). Pitch kept at 26.37° (`estrutura.cobertura_manter` = "inclinacao"), so the whole roof sits
  **0.35 m higher than in the drawings** (0.21 the lowest purlin on the ceiling beams over the wall +
  0.139 the deeper floor): panel underside at the outer wall face Z 5.883 (drawings 5.534), on the ridge
  7.398 (7.048). Alternative "cumeeira" keeps the ridge (7.048) with a **20.93°** pitch (23.15° before
  the floor); the eaves rise 0.35 m in both cases. Visual comparison shown to the user 2026-10-13.
- Floor between storeys (DiscoverCasa method, 2026-10-13, `sistema_construtivo.json` `estrutura.pavimento`):
  joists 220x75 on edge N–S on the ground-floor walls (Z 2.80–3.02), positions at ≤ 0,615 m — 0,61 m (outer ones at
  the E/W faces) + 2 trimmers beside the stair opening; the 4 joists inside the opening stop at a 220x75
  header on its south edge (a second header lies on the north wall, the stubs there being 16 cm); the
  drawings' central beam line (double 80×160 at y 3.37–3.53, over the 2.8 m living-room gap between
  PI1.06 and PI1.10) is **not modelled since 2026-10-15** (user: "o vigamento normal de 22x7,5 e 11x7,5
  nada muda"; `estrutura.pavimento.vigas_principais` = false) — the 3 joists over the living room span
  ≈ 4,7 m from the south wall to the stair wall (rough check: fails at 0,98 m; at 0,61 m bending OK,
  deflection marginal; `revisao-tecnica.md` #6). Spacing from the company's base framing sheet
  (`conhecimento/fontes/vigamento-base/3_Vigamento.pdf`, 2026-10-15; was 0,98 m, "1 m" never confirmed).
  With `vigas_principais` = true it is kept as **2 × 220x75 side by side, flush with the joists** (y 3.375–3.525, between
  the edge joists), the joists cut and hung on it (section and hangers: engineer, `revisao-tecnica.md` #6);
  battens 110x75 laid flat E–W at **0.60 m centres** (user: "medidos em eixo"; Z 3.02–3.095, 11 rows,
  one cut by the opening); OSB 22 over the whole footprint minus the stair opening (Z 3.095–3.117,
  56.4 m²). **Assumed: every upper wall stands on the OSB** (confirmed by the user 2026-10-15: "sim") (drawings: exterior walls on rim joists at
  2.96, interior on the OSB at 2.978), so the upper floor rises 0.139 m and the upper exterior modules
  are 1.8 cm shorter than drawn (the 2.40 m clear height stays). No rim joist across the joist ends at the
  N/S faces (not said) (confirmed by the user 2026-10-15: "não" — none). Upper openings keep their height above the floor. Floor wool 100 mm (user
  2026-10-13: "fica entre as vigas"): on the ground-floor false ceiling between the joists, 43.4 m²
  (`tetos.la_pavimento`, collection 5.6; height in the bay assumed).
- Confirmed by the user 2026-10-09: ceiling beams N–S down the slope (the rule for every house), 22x7,5
  at 1 m, a post under every purlin on every beam, purlins as modelled, no 110x75 at mid-wall module joints
  (the rule), gable triangles on the tie beam. Still assumed: post section 110x75; PE1.09 / PE1.10
  framed as interior walls; door height 2.10 m.
- Timber (`quantidades.csv`): 645 pieces, ≈ 1,547 m, **9.9 m³** (drawings' structure: 18.1 m³); floor
  1.3: 220x75 21 pieces 115.8 m (joists at 0,61, stair headers), 110x75 12 pieces 104.8 m.

### Build-up layers
- Exterior (per layer ≈ 169 m²): OSB 9, Traspir 95, options A/B/C. Wall wool 196 m² (80 mm against the
  outer OSB in exterior walls, 60 mm in 75 mm interior walls — user 2026-10-09; none in the gable
  triangles since the attic is outside the insulation). OSB 15 328 m² and Pladur 317 m²: on flat-ceiling
  floors the Pladur goes up to the false ceiling and the OSB up to the beams (before 2026-10-09 both
  stopped at the module top, leaving a 5 cm band under the ceiling). Floor finish 102 m², roof panels 74 m².
- Ceilings (company system, user 2026-10-09): réguas de suspensão screwed upright to the side of each
  ceiling beam / floor joist, one per perfil (490 pieces); perfis de teto in galvanised steel (user) at 0.40 (242 m,
  47×17 assumed); cantoneira 30×30×0,5 steel on every real wall of each room (151 m = **51 bars of
  3 m**, `unidade` in `quantidades.csv`); Pladur 103 m²; upstairs 100 mm Volcalis on top of the ceiling
  between the beams (48.8 m², position assumed: user said "on the roofs"). Not modelled: the perforated
  corner angle for "hard corners" (which corners — to confirm). The ceiling level is unchanged
  (perfis 27 mm under the beams).
- Openings (not drawn as such in the engineer's drawings): inferred from the stud layout (bays ≥ 0.55 m
  between full-height studs; sills/headers from cripples) and kept in the DiscoverCasa structure, with
  heads lowered where the 110x75 header must fit under the top plate (≈ 3 cm vs the engineer's openings;
  upstairs heads ≤ Z 5.36 since the 2026-10-13 floor (were 5.22, ≈ 11 cm below the architecture's
  windows), `revisao-tecnica.md` #21): 5 doors/French windows
  + WC window PE1.12 downstairs, 5 windows + 1 French window (PE2.08) upstairs, 5 interior doors.
- Rooms = spaces between the timber walls (bandeiras close the doorways; the duct is gone since
  2026-10-09). Build of 2026-10-13: ground floor P0.01–P0.05 9.4 / 0.3 / 38.3 / 3.1 / 2.2 m²; upper floor
  P1.01–P1.07 9.3 / 9.4 / 14.7 / 5.7 / 5.3 / 3.3 / 1.0 m² (names on the `planta_piso0/1` previews).
- Levels: ground finished floor Z 0.16 (XPS 60 + screed + finish on the slab); ground ceiling Z 2.744
  (calhas 27 + perfis 17 + Pladur 12.5 under the joists) → **2.58 m clear**; upper finish on the OSB at
  Z 3.122 (2.983 before 2026-10-13; architecture +2,88 = Z 3.04); upper ceiling Z 5.524 under the ceiling
  beams → **2.40 m clear** (RGEU minimum for habitable rooms: no room for any upper-floor build-up).
- Not modelled: stair, connectors, windows/doors (frames, glass), services, chimneys (+7.50 in EE').
- `Casa_Tipo1_Estrutura_Sketchup.skp`: made by the user from the first (drawings') structure model; it
  does not update with rebuilds.
- Foundation indicative: raft outline from the plan (11.50 × 11.25 m + east bump), 20 cm slab,
  perimeter wall 0.20 and footing 0.65 × 0.40 at nominal depth.
