# Status — Construção Torres Vedras

House-specific state only. The company standard learnt from this house (D2503) is in
`conhecimento/sistema-construtivo.md` (§2, §2b, §2c, §3, §3b, §3c, §6); the user's words in
`conhecimento/registo-conversas.md`; issues in `revisao-tecnica.md` (#n below); model versions in `modelos.md`.
Condensed 2026-10-28 (the old "Where we stopped" chain and the superseded readings are in the git history).

## ▶ Where we stopped (2026-10-21) — start here
- **To do: rebuild the model (v6.5)**. The builder already ends the ceiling beams inside, against the modules (user
  2026-10-21, below): lameladas 170,49 → 166,53 m, notches 36 → 0, module pieces 702 → 696 (studs whole, as D2503
  Módulos). The committed `.blend` / `.glb`, `quantidades.csv`, `materiais.md` and `documentos/D2503_*.pdf/.csv` predate
  it (`modelos.md`).
- **Waiting for the user**: his review of the generated Cobertura and Listagem de material ("ok assim o farei" — the
  Módulos already "está absolutamente correto"); the gutter outlet type and bocal ("isso depois eu digo"); his reply to
  our corrected caixilharia answer (#20); the overflow (ladrão) after our explanation (#4 (g)).
- **Remind him**: what goes under the chapéus — "Por baixo dos chapéus lembra-me mais tarde para te confirmar o que
  leva" (2026-10-20, 13:25) (#13).
- Next: a new project through the whole chain (per-project questions → model → documents); this house's real materials
  list, when he sends it, to compare with `materiais.md`.

## Goal (user 2026-10-15)
Model this built house with the DiscoverCasa method and check that the model's materials are close to what was really
used and that the structure matches the finished work, "de forma a ficares realmente a construir as nossas casas como
nós". Not to be shown in the configurator ("Não vamos mostrar Torres Vedras", 2026-10-20).

## Model history (details in `modelos.md`)
v1 2026-10-15 from the architecture plan (builder `casa_planta.py`) · v2 2026-10-15 night (his first review) · v3
2026-10-16 (gutter inside, same height all round) · v4 2026-10-16 evening (roof as D2503 Cobertura) · v5 2026-10-16
night (modules as D2503 Módulos, battens per the site photo) · v5.1 2026-10-19 (interior walls carry the lameladas) · v6
2026-10-19 (caixilharia of the approved table, provisional pergola) · v6.1 2026-10-20 (interior modules to the
amarração, gable cladding to the panel end, entrance door) · v6.2 (chapéu corners, pergola whole length, 2,5 cm
clearance, M23) · v6.3 (finished photos: pergola from the garage east, ceramic, remates) · v6.4 (outlet holes in the
gutters; document generator first run) · v6.5 to rebuild (beams inside).

## Open questions (house-specific; company items are in `sistema-construtivo.md` Pending)
- D2503 interior modules **2,53** (studs 2,46) vs the rule 2,543 ("à medida certa das vigas amarração") — drawing
  rounding or done on site? (#6). D2503 module table 3,50 vs roof sections 3,4915; P01 2,64 (elevations) vs 2,61 (plan).
- D2503 labels "16x8" after revision C "Vigas de 16x8 para 20x10" (#11).
- Why the plain modules are 2,21 / 1,78 / 2,65 (5 / 4 / 6 bays) — not asked again since 2026-10-20.
- Which cut list the factory followed — D2503's table (220 × 11x3,5 / 199 × 7,5x3,5) or its drawing (228 / 207, what the
  generator gives); the roof panels 30 × 3,94 + 7 × 6,44 (generated) vs D2503's 28–29 + a 3,94 × 0,25 strip + 7: not
  explained yet.
- Why the garage module was built 3,82 when "usa o tamanho que o vão precisa" gives 3,39 — not said.
- The membranes in the site photos: HOLZ TECHNIC ("TRASPIR HOUSE 95", EN 13859-1/2) on the walls and rothoblaas on the
  top band — data sheet, why two (#18); the pipe stubs through the top band and the narrow "ladders" of battens (#4, #9).
- The battens' 35 cm — centres or clear.
- The downpipes: how TV's bottom outlet (photo) reached its downpipes outside the cladding (optional); their foot —
  where the water goes (#9). The chapéus: what goes under them (reminder above), a drip / vent gap at the cavity top
  (#13).
- The roof panel used (maker, minimum slope vs the 6 % built) (#8).
- The WC glass: "trasnparente" in one table row vs "Fosco" (#20).
- **Pergola** (#21, #22): sections (model posts 16×16, beams 16×16, ledger 7,5×16, slats 7×3 at 0,15 — "não sei ao certo
  mas parecem estar ótimas"), posts' bases, slope (model 15 %), what is under the ceramic tiles (sub-roof — ceramic at
  ≈ 18 % needs one), tile battens and what is seen from below, gutter section and material, where its 2 downpipes
  discharge, the exterior treatment's name ("não me relembro do nome").
- **Remates** (#23): material and colour per opening (photos: dark round the windows, light round the garage door and
  under the east janelas de correr — thresholds?), the inside reveal finish.
- Why 2,50 clear here (architecture 2,60) and whose choice it was — low priority.
- The photo of the finished house of 2026-10-20 12:00 (Instagram post) was not saved — ask for the file if needed.
- The suite's passage 1,40 between closet, WC and quarto 01 is open (no door) — as drawn. Window heights (sill ≈ 1,00,
  head ≈ 1,75) read roughly from the 1:200 elevations.

## Decision log (TV; short quotes — full words in the registo)
- 2026-10-15 — A house already built; model it and compare with the real materials; Sobral paused. Drawings: estudo
  prévio 1:200 (architecture, site plan, retaining wall, survey). Always the DiscoverCasa method, not the architect's P1
  ("nós usamos o nosso método construtivo sempre portanto segue o nosso"). No SketchUp of this house; "desenhos de
  fabrico" = the modules drawn by DiscoverCasa. Real materials list "será fornecida posteriormente" (pending).
- 2026-10-15 — As built: "paredes exteriores são em tremolo no revestimento exterior" + the standard build-up; ripado
  horizontal 3,75×3,5 ripped from 75×35; **no contra-ripado on this house** ("Nesta casa só levou ripado na horizontal e
  não levou o contra-ripado"); roof hidden on the DiscoverCasa timber; floor "sobre a nossa base de fundação". Ceiling
  beams up to 8 m ("O nosso limite é precisamente 8 metros"); a house taller than the architecture "é natural".
- 2026-10-15 — Parapets above the roof clad on the roof side: "lã mineral, osb 15, membrana transpir, ripado horizontal e
  tremolo vertical" (this house's façade is Tremolo; the gutter walls are lined instead — 2026-10-20). Rufo corners must
  be closed.
- 2026-10-16 — The gutter inside the parapet ("sim é por dentro … ao nível daparte de baixo dos rufus"); downpipes
  inside the exterior cladding, never in rooms; the same height on every side; the 2 skylights were not built.
- 2026-10-16 — Review of v3: gutters right; the bare re-entrant parapet end wrong; the downpipe end slightly above the
  base; battens always round the openings; the rufos are **chapéus** wrapping the wall ≈ 2–3 cm down both faces.
- 2026-10-16, evening — **D2503 Cobertura** ("arranjei o documento exato sobre a cobertura de torres vedra e eu disse-te
  mal como seriam as aguas"): modules on the foundation line, full height to 3,4915; amarração ring inside
  (2,543–2,653); lameladas 20×10 at 0,915 (A 8,50 × 11 main block, B 11,00 × 7 wing); ceiling 2,50; ridge Y 6,749 along
  X, two slopes at 6 %, the south slope running on over the wing; madres 11×7,5 on prumos; gutters 0,31 on calços with
  falls, outlets at the ends; panels 3,94 / 6,44; chapéu flat (`cobertura-D2503.md`).
- 2026-10-16, night — Windows not to the floor get a batten above and below; battens every 35 cm from the bottom;
  every opening framed except at the floor; a vertical batten at every exterior corner on both faces; chapéu flat
  ("está ótimo"); ridge madres over the wing **22×7,5** ("como estão no desenho com 22x7,5"); downpipes as modelled.
  **D2503 Módulos** given ("o ficheiro original de como os módulos foram feitos") → `modulos-D2503.md`; documents like
  D2503 for every new project.
- 2026-10-19 — The 11×7,5 garage lintel (3,00) approved by the company's engineer for this house ("por norma é 22x7,5")
  (#17); ceiling beams bear on the interior modules ("Por norma as vigas de apoio ao teto apoiam-se nas paredes dos
  módulos interiores também"); M1 3,82 "montados em obra"; corners — one through, one abutting, no rule for which.
- 2026-10-19 — The approved openings table "PROJETO APROVADO" (`revisao-modelo/2026-10-19_projeto_aprovado_vaos.png`,
  11 items, 31,06 m², RAL 7016, 6 estores; transcribed in `materiais.md`): the kitchen window is a **vidro fixo**, the
  garage door **seccionado** (the architecture superseded). The table gives "apenas a medida do caixilho sem folga"
  ("acho que"); RAL 7016 / estores / painel liso = "o nosso padrão para já".
- 2026-10-19, 18:12 — Interior modules "à medida certa das vigas amarração" (2,543 + 0,11 = 2,653, no packing; D2503 2,53
  — open); the basculantes as modelled ("está ótimo como fizeste" — 0,73 in D2503's 0,75 openings); the **entrance door
  M5 fills its 1,04 opening** ("uma porta maior e mais robusta que cabe naquele espaço"); the gable parapets' forro "até
  ao final do painel sanduiche" (#15); pergola: height right, screwed here ("acho que"), built separately on a ledger
  over the battens, glulam with autoclave treatment.
- 2026-10-20 — The base under the interior walls laser-checked ("exatamente como sugeriste"); the **despensa door M23
  fills its 0,94 opening** ("sim coloca a encher o vão como na principal"); downpipes: "nós nesta obra fizemos de forma
  diferente mas a forma como modelaste … por dentro do revestimento é a forma correta" — TV's run **outside the
  cladding** (finished photos), the model keeps the method; the gutter walls lined "até ao topo que depois se encontra
  com os chapéus" (#15 closed); chapéus — no uncovered top, no overlap (#13).
- 2026-10-20 — Pergola as finished: "vai até ao comprimento total da casa e leva telha e uma caleira à vista"; "É
  cerâmica"; a second downpipe "no lado oposto" (read: the east corner post); from the photos — from just east of the
  garage to the east end (x 3,63 … 17,57), 6 posts, a timber deck under it (#22).
- 2026-10-20 — Our corrected answer on the table vs the openings (sent at night): with the 2,5 cm default the frames fit
  D2503 only for the doors in width; janelas de correr 2,00, vidro fixo 1,50 and garage 3,00 equal their openings;
  basculantes 0,80 are 5 cm over 0,75 × 0,75 (M6, M18) or wider than 0,75 (M24); the 2,20 doors and garage have no head
  clearance → at TV the frames were made to the openings or the openings had no clearance (#20). His reply: pending.
- 2026-10-20 — Remates round every opening (company rule, modelled here); outlet holes at every downpipe (v6.4, side
  outlet — TV as built had a bottom outlet); documents generated (`documentos/D2503_*`); the Módulos "está
  absolutamente correto".
- 2026-10-20, night — The module divider checked here: rules hold, 19 of 50 modules identical (`modulos-D2503.md`,
  `divisor-vs-D2503.svg`); the P18 pair (two "Janela de correr 2 folhas", architect 0,14 apart) moved 16,5 cm each for a
  0,32 pier, as D2503 (#24); the model keeps D2503's modules.
- 2026-10-21 — The full-height exterior modules with the inner ring are the rule for every hidden roof. **The ceiling
  beams never cross the modules** ("essas vigas ficam por dentro e encostadas as da estrutura não atravessam"): our
  2026-10-19 reading of "sim há um entalhe feito e a viga fica por dentro" / "O entalhe é feito em obra" (a notch in the
  module) is superseded — D2503's whole studs are right (#19); v6.5 to rebuild. The lameladas are **cut to fit** ("Sim
  normalmente cortamos para "encaixar" no tipo de obra que temos") — D2503's 8,50 / 11,00 = the outer depths (nominal),
  the pieces ≈ 8,28 / 10,78 from 13,5 / 12 m stock (#12: stock waste stands). No company clear height ("A altura não
  temos fixa") — this house's 2,50 is its own.
- 2026-10-28 (said on the configurator) — The chapéus here came ≈ 2 cm down both faces: "ficando do lado com 2 cm
  aproximadamente para baixo tal como no projeto de torres vedras" (JSON `cobertura.chapeu.descida` 0,03 → 0,02, which
  this model reads — the "3 cm legs" in `modelos.md` / `materiais.md` superseded 2026-10-28, see registo). The company
  usually does a hidden roof in **one água** ("nós tentamos sempre só fazer uma água"); this house's two slopes (D2503)
  stay in its config — why two here (cércea, look?): to ask. Its parapet roof side in ripado + Tremolo stays (this house's
  façade); for other houses the roof side takes their own façade finish ("o capoto tem que ficar na casa toda").
