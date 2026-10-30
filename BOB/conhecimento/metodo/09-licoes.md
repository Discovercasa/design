# Método DiscoverCasa — lições dos erros de modelo (§14) (parte de conhecimento/metodo-construtivo.md, v8.3)

## 14. Lessons from model errors
Each: what went wrong → the rule it produced → where the fix lives. He reviews models from screenshots with the problem
circled (`discovercasa.md`).
- **L1** (TV v1, 2026-10-15) Rufo / chapéu corners left open → water into the cladding ("onde se chovesse a água entraria
  para dentro do revestimento") → the chapéu runs on over the cladding at every outside corner, every top covered once (L38)
  (§7) → `camadas.chapeus`.
- **L2** (TV v1) Parapet frame bare on the roof side ("não é suposto") → a parapet is an exterior wall on both faces, clad
  on the roof side (§7; its finish = the house's façade finish — L52) → JSON `cobertura.platibanda_interior`,
  `camadas.platibanda_interior`.
- **L3** (TV v1–v2) Gutters sunk below the rufo, then moved outside the wall → the gutter is the caleira oculta inside the
  parapet at the rufos' underside; the exterior gutter only on exposed roofs; when a company document lists a part for a
  roof type, model that part first (§7) → JSON `cobertura.caleira_oculta`, `casa_planta.construir`,
  `camadas.cobertura_platibanda`.
- **L4** (TV v1) A slot across the sala ceiling ("tem um gap no meio da sala") — strips < 5 cm skipped → every part of a
  room's ceiling gets Pladur and wool (§6) → `camadas.tetos` (`fino`).
- **L5** (TV v1) Façade cladding short at an outside corner under a parapet → the highest wall behind sets the cladding top
  (§7) → `camadas.degraus`.
- **L6** (TV v1) Slope 5 % assumed instead of the drawings' → the slope comes from the drawings / the rule, asked if missing
  (§7; TV is 6 %, D2503) → cfg `cobertura.inclinacao_pct`; ⚠ the 5 % fallback still in `casa_planta.py`.
- **L7** (TV v1) Battens 30×20 at 0,35 from the draft → the user's standard ripado 37,5×35 ("o 3,75x3,5 é o nosso
  padrão"), at 0,35 since L31 (§8) → JSON `exterior.opcoes.A.ripado`.
- **L8** (TV v1, flags that were not errors) 8 m beams, a taller house, long modules → check §13 / §2 before flagging;
  still say when the engineer or the licence is affected.
- **L9** ([SB], 2026-09-30) The engineer's structure (160×80, sloped ceilings) modelled → always the company method; the
  drawings fix the geometry (§0) → `estrutura_dc.py`, cfg `estrutura.sistema`.
- **L10** ([SB], 2026-10-09) "There are gaps in between the walls and on the tetos falsos why ?" → no gaps: bandeiras over
  open doorways, Pladur to the false ceiling, OSB 15 to the beams (§3, §6) → `estrutura_dc.emoldurar_bandeira`, `camadas.py`.
- **L11** ([SB], 2026-10-13/15) A drawing's central floor beam dropped, then invented → never drop or invent a structural
  piece silently — ask ("nada muda") (§5) → JSON `estrutura.pavimento.vigas_principais`.
- **L12** ([SB]) Ambiguous words used as facts for days ("22,5x7,5", a trailing "1 meter") → mark readings assumed and
  confirm early; company documents may already answer → the status column.
- **L13** (2026-10-13, 2026-10-21) Asking again what he had answered ("sim já o tinhamos definido"; "Sim como já te tinha
  explicado …") → grep the registo first; a new consequence of a known rule is asked stating the known rule in his words
  (§0) → `discovercasa.md`.
- **L14** (2026-10-09/15) A photo detail read as a rule (horizontal 7,5×3,5 pieces = a site change) → ask first (§0, §3).
- **L15** (TV v2 and the standard, 2026-10-15) "Nesta casa … não levou o contra-ripado" applied to the standard → a
  one-house fact goes in that project's cfg; the standard changes only with "o nosso padrão" / "por norma"; check new facts
  against older rules (§0, §8) → JSON keeps the contra-ripado, TV cfg removes it.
- **L16** (tools, 2026-10-15) L1, L4, L5 found by the user, the validation counted pieces only → every build renders
  close-ups of each outside corner (rufo, gutters, parapets, cladding), re-entrant corners from the notch and the roof,
  and the largest room's ceiling — look before handing over → `ferramentas/modelo/blender/pormenores.py` via
  `construir_casa.py` (`_trabalho/renders/<model>/pormenores/`). Limits: other rooms' ceilings; `validar.py` checks no chapéu
  corners, parapet ends or ceiling coverage.
- **L17** (TV v2) Gutter walls lower than the side parapets ("isso está mal") → one top level all round on a hidden roof,
  parapets on every exterior wall (§7) → `casa_planta.construir` (`z_plat`). Check idea: every parapet top at one Z.
- **L18** (TV v2) Downpipes read as inside rooms ("não é suposto") → a downpipe runs inside the exterior cladding, never in a
  room or across an opening (§7; the method, L40) → `camadas.tubos_queda`. Check idea: every pipe in a cladding zone, clear
  of openings.
- **L19** (TV v3) Bare frame at a parapet end over the wing roof ("algo no canto … está errado") → every parapet end over a
  roof is clad / lined and capped (§7) → `camadas.cobertura_platibanda`, `camadas.platibanda_interior`, `camadas.chapeus`;
  `pormenores.py` renders re-entrant corners.
- **L20** (TV v3) Downpipe to Z 0, covered by the base → it ends slightly above the base (§7) → JSON
  `tubo.folga_base` 0,05.
- **L21** (TV v3) Coping a flat plate → the chapéu wraps the wall top, ≈ 2 cm down both faces (≈ 3 until 2026-10-28,
  L56); use his names ("nós chamamos de Chapéus") (§7) → JSON `cobertura.chapeu`, `camadas.chapeus`.
- **L22** (TV v3) Battens not round the openings; with TV's contra-ripado dropped the jambs lost theirs → battens always
  round the openings; when a project drops a layer, move that layer's jobs to the layers left (§8) → `contorno_vaos`,
  `camadas.dispor`.
- **L23** (TV v1–v3) Roof from the architect's section, then from his sketch from memory → the company's production drawing
  (D2503) wins; ask for it first and record the why (§0, §7) → TV `docs/cobertura-D2503.md`, TV cfg.
- **L24** (TV v1–v4 modules, vs D2503 Módulos) 3 m modules from one end, from "neste caso foi 3 metros" (memory) → factory
  modules are whole grid bays, opening modules sized round their opening, the 3 m a maximum; numbers from memory lose to
  the drawing (§2, §3) → `divisor_modulos.py` (2026-10-20 night; L44).
- **L25** (TV v1–v4) One 4,35 module over two janelas de correr → split at the pier (2,15 + 0,32 + 2,15); only an opening
  too wide for a factory module is one site-built module, marked (§2) → `divisor_modulos.py`.
- **L26** (TV v1–v4) "X walls run through" used as fact → one through / one abutting always, no rule for which; a modelling
  convention is never presented as the company rule (§2 Corners) → builder default, per-corner choice wanted.
- **L27** (TV v1–v4) Exterior openings at the architect's sizes → the table gives the elements, the module drawing the
  rough openings (§3) → TV real modules; cfg `aberturas` unchanged.
- **L28** (TV v1–v4) 22×7,5 over the 3,00 garage vs D2503's 11×7,5 → not a model error: the 22×7,5 is the norm, TV's an
  engineer-approved exception; a company drawing departing from a rule may be a one-house engineering decision — ask,
  record it in the project (§3) → JSON `estrutura.verga_grande` unchanged.
- **L29** (TV v1–v4) "No noggings" (Casa CL) → escadas at every junction (§2) → JSON `estrutura.escadas`; not generated by
  the builder.
- **L30** (TV v4) Exterior module + a separate parapet part → one 3,50 module from base to parapet top (§2) → TV real
  modules; the builder still splits it for modelling.
- **L31** (TV v4) No batten under the windows, battens at 0,50 → windows framed above and below, every opening except the
  floor side, corner battens both faces, ripado every 35 cm from the bottom; when he describes one case, model the open
  side as a question, not a silent choice (§8) → `contorno_vaos`, `espacamento` 0,35.
- **L32** (TV v5) Interior walls 13 mm under the lameladas (D2503's 2,53 + 110), so they did not bear → the beams bear on
  the interior modules, made to measure; a gap a drawing leaves where the method says "bears" is a question, not a fact, and
  never filled with an invented piece (§2, §4) → `casa_planta.construir`; cfg `modulos_reais.interior_a_medida_da_amarracao`.
- **L33** (TV docs v5) Entrance / despensa door labels swapped (M5 / M23) → match a module to its wall, room and the table
  before naming it; use the table's room names (§3) → TV cfg `camadas.caixilharia.itens`.
- **L34** (TV, 2026-10-19) "Maker's size + a clearance" recorded as confirmed from "Sim exatamente" to our wording; the table
  then disagreed → a "sim" to our wording confirms the gist; test against the first numbers; a misfit is reported, never
  forced (§0, §3) → `camadas.caixilharia()` warns.
- **L35** (TV v1–v5) The plan's pergola (magenta dashed) not read until v6 → read every line type; list unmodelled elements
  in each delivery; ask for the openings table and the attached elements at the start (§0a, §8) → TV cfg `pergola`.
- **L36** (TV v6) A gable parapet's roof-side cladding stopped at the gutter madre ("o forro é suposto ir ate ao final do
  painel sanduiche") → bound every finish layer by the element it must meet, not a structural line (§7) →
  `camadas.platibanda_interior`, `camadas.cobertura_platibanda`.
- **L37** (TV v6) Entrance at the table's 0,90 centred in a 1,04 opening → an element visibly smaller than its opening is a
  question (the door filled it) (§3) → TV cfg M5 / M23 `largura`; a warning wanted.
- **L38** (TV v6.1) Chapéus overlapping and a top left bare at a corner where X abuts Y ("não podem deixar o topo
  destapado … não dão overlap") → every wall top covered once, from the actual corner (§7) → `camadas.chapeus` `ate_parede`.
- **L39** (TV v6–v6.1) Pergola from the plan and a stage photo; then stretched to the whole house on "comprimento total"
  → finished photos show the built house; words of extent are read against the photos, else ask "até onde vai?" (§0, §8;
  PO Q1, Q21) → TV cfg `pergola` `x0` 3,63.
- **L40** (TV, 2026-10-20) "Como esta desenhado está perfeito" read as TV's downpipes as built; then the side outlet read
  as confirmed → an approval can approve the method, not the house, and covers only the point asked (§0, §7; PO Q16).
- **L41** (TV v6–v6.2) Table vs D2503 openings compared in width only; the model shrank frames silently → compare frame and
  opening both ways with clearance and box, report every misfit (§3) → TV #20; a per-item fit table in the build log wanted.
- **L42** (TV, 2026-10-20) A draft answer "heights fit everywhere" written before checking (never sent) → check a numeric
  answer item by item against the project data before sending; record an answer as sent only when it was (§0).
- **L43** (TV v3–v6.3, the user ≈ 13:51) Downpipes without outlet holes in the gutter lining → check that every water path is
  connected — chapéu → lining → gutter → outlet → pipe → foot (§7) → `camadas.tubos_queda` (`furo_z`),
  `camadas.cobertura_platibanda`; validation wanted.
- **L44** (2026-10-20 night, the divider vs D2503) Only 19 of 50 modules identical, all differences in where a remainder
  goes → the company's rules are hard constraints, its per-house choice is ours by costs (delegated); judge the match by
  rules and counts; every moved opening reaches the user (§2) → `divisor_modulos.py --comparar`, `estrutura.divisor.custos`.
- **L45** (2026-10-20 night, configurator) A hidden roof on 22×7,5 built the draft's way (full height seen only on TV's
  glulam) → a way of building belongs to the case that defines it (the hidden roof); ask the scope before keeping two
  builds for one roof type; fit-check every new combination (§2, §4) → `anel` for every hidden roof.
- **L46** (prototype, 2026-10-21; TV v5–v6.4 too) Ceiling beams through the exterior modules, studs cut ("isso nunca
  acontece … não é realista") → the beams stop at the modules' inner face on the ring, the beam notched to fit; re-ask a
  both-sides answer with images; question our reading, not the company drawing; analogies carry misreadings (§0, §4) →
  `casa_planta.apoio_vigas`. Check idea: no exterior stud split by a beam.
- **L47** (2026-10-21) Madre lines broken at the re-entrant corner; the ridge pair changing at two places; the reason for a
  22×7,5 ridge not visible (asked twice) → build a line across zones as one line, then cut it; a pair is a pair; the reason
  for a differing piece goes with the model (§7) → `casa_planta.construir` (`dentro_da_casa`, `troca`).
- **L48** (configurator, 2026-10-21 / 10-22 / 10-28) Walls not joined in 3D, a gap roof–walls, the hidden roof drawn flat
  with no gutters → every view the client sees is a model of the method: draw nothing the engine does not build, leave out
  nothing it does (§2, §7) → `cena.js`, worker `cobertura_casa`.
- **L49** (2026-10-22, exposed-roof documents) Two roofs on one plane counted the overlap twice (≈ 8 m²), empenas missing
  from the lists, one eave's gutter in three runs, coplanar slopes as two → check a roof's plan area against the outline
  with overhangs; a document that filters the model says what it leaves out; draw the production sheets of every new roof
  case (§7) → `telhado.py`, `documentos/dados.py` `Casa.empenas`, `telhado_estrutura` (slopes by plane).
- **L50** (2026-10-22) Roofs shooting to the sky (a near-zero denominator in the clipping) and a "mini telhado" out of a
  crossing wing's slope → a roof is one closed surface drained to its eaves; a body ending inside a crossing wing runs into
  it to its ridge; audit every shape × roof × slope × eave with sums; a "on the line" tolerance never feeds a division (§7)
  → `telhado.py` `_cortar`, `telhados` (`parar_no_cume`).
- **L51** (2026-10-28, his U in misto) Beams missing (3 m of bare purlin) and 160 members through one another after a
  Blender "0 issues" → purlins need a beam and a prumo; no member through another; new rules §6 (c)–(e), §7 "How the rincão
  / laró members meet"; a check's "0 issues" is only as wide as what it checks; a plan and 3D of the timber with every new
  roof case; try a default on every shape (E11) → `telhado.py` ("zonas"), `telhado_estrutura.construir`,
  `ferramentas/configurador/auditar_cobertura.py` (a later 108-case sweep fixed a T stem's overhang, a beam under every
  rincão / laró top, beams ending at a header's face).
- **L52** (configurator, 2026-10-28) The parapets' roof side drawn in Tremolo on every house, whatever the façade — the
  2026-10-15 list (said on TV, a Tremolo house) applied as a standard; the user: "o capoto tem que ficar na casa toda" → a
  rule said on one house is checked for what depends on that house before going to every house; the parapet's roof side
  takes the house's façade finish (§0 Scope, §7 Parapets) → `camadas.camadas_platibanda` (OSB 15 + Traspir + the façade
  option's layers), worker `cobertura_casa`.
- **L53–L56** (configurator, 2026-10-28, his screenshots: "Estas a cometer erros que não fazem sentido") — rules he had
  already given ("como eu já te havia dito", "tu sabes que …") not carried to the screen's roofs → before a model reaches
  him, check each: the roof covers the whole outline, every water path is joined, every trim wraps what it covers, every
  cap lies on what it caps (§0, E11):
  - **L53** Hidden roof with gaps — where two strips met at a re-entrant wall, a strip of the frame's width had no panel
    ("a cobertura nao está a cobrir a casa toda esta com gaps") → the open strip's slope runs on to the wall's inner face;
    check the panels against the outline (§7 Hidden roof) → `casa_planta.fechar_aguas`.
  - **L54** Exposed-roof downpipes not joined to their gutters ("os tubos de queda não estão conectados as caldeiras") →
    a piece from the outlet down and back to the pipe; L43's water path holds on every roof (§7 E8) →
    `camadas.cobertura_faces` (`ligacao`).
  - **L55** Ridge caps floating over the panels ("estão pousada na cobertura e tem um gap … elas estão "coladas" à
    cobertura") → caps and flashings folded down onto the panels (§7 Covering) → `camadas.cobertura_faces` (`dobrada`),
    `camadas.cobertura_platibanda`.
  - **L56** Chapéus not wrapping the whole hidden roof on the screen ("cobrem/envolvem o perímetro todo da cobertura
    escondida ficando do lado com 2 cm aproximadamente para baixo") — they did not fit the roof-side cladding drawn
    apart from the engine → round the whole perimeter, legs ≈ 2 cm, sized on the engine's own parapet build-up (§7
    Parapets, L48, L52) → JSON `cobertura.chapeu.descida` 0,02, `camadas.chapeus`, worker `cobertura_casa`.
- **L57–L64** (configurator, 2026-10-29, review 4 — his screenshots stayed on his PC, reproduced from his text and the
  engine; "Revê isso mais uma vez", "Mais uma vez") — exposed-roof timber and hidden-roof water paths wrong again →
  after a fix, look at the same view he uses and re-run `auditar_cobertura.py --formas` (E11):
  - **L57** Ridge purlins stopped short of the ridge, straight and close ("não encaixam nas cumeeiras") → the two top
    purlins meet on the ridge line, cut to the slope; the joint's detail is OPEN (§7 E4, E5) → `telhado_estrutura.construir`.
  - **L58** Prumos turned across their beam, half of the prumo off it, flat tops under sloping members → each prumo turned
    with its beam (110 along, 75 across), top cut to the member above (§7 E3) → `telhado_estrutura.construir` (`prumo`).
  - **L59** Prumos on a beam line standing past the beam's end → none past a beam's end (E3) → audit "prumos past a beam's
    edge".
  - **L60** Gable frames overlapping the eave purlin (3,5 cm through the bottom plate, end members into the edge beam, a
    valley's foot through the gable) → the empena starts past the eave purlin; a "Calço da empena" where it would leave a
    gap (E6) → `telhado_estrutura.construir`; audit "empenas' members against the roof timber".
  - **L61** A gutter on the high side of a one-água roof, and a stray piece in the middle of the gutters (a gutter per
    strip, end caps, a plate to the parapet top, paired downpipes) → the gutter only on the side the panel falls to, one
    continuous gutter per low wall (§7 Hidden roof) → `casa_planta.construir`, `camadas.cobertura_platibanda`.
  - **L62** Outlet holes drawn in an invisible plate (the parapet-side plate — unseen from above; asked 2026-10-20 and again
    2026-10-29) → the hole in the gutter's bottom, visible from above; a fix to a fault he has reported is checked from the
    angle he looks from (L43) → `camadas.tubos_queda` (`furo_z`).
  - **L63** The chapéu narrower on screen than in the engine (every parapet drawn 0,16 deep inside, 0,09 outside, against
    the engine's own build-up per wall and façade option) → the screen draws the parapet as the engine builds it (L48, L56)
    → worker `cobertura_casa`.
  - **L64** The roof panel shown grey ("Mais uma vez … não cinzenta") → the maker's tile colour on the exposed Munditelha
    (and, ours, the hidden panel — confirmed RAL 8004 2026-10-30); a colour he has asked once is a per-roof-type check (§7 Exposed roof) → JSON `materiais`.
- **L65–L69** (configurator, 2026-10-29 night, review 5 — his L in step 5, five screenshots; "faz todas as questões que
  precisares para começarmos a fazer as coberturas sem falhas algumas!!") — the roof's joints, overhangs, gutters and trims
  still unfinished at the corners and meeting points → look at every node (hip, valley, corner, ridge end, where a gable meets a
  wing's eave), not only the straight runs; his questions to settle are in §15 (the roof questionnaire A1–E8):
  - **L65** Purlin ends cut square against a hip / valley member left a triangle open at every hip ("existem ainda gaps entre
    as vigas, no máximo podemos cortar a vigas com a diagonal necessária") → purlins end on the skew against the member's
    side, hip / valley members mitred at a node (§7 E4, "How the rincão / laró members meet") →
    `telhado_estrutura.ponta_obliqua`; audit gaps at nodes, not only clashes.
  - **L66** A 0,12 verge met a 0,25 eave out of line where a gable met a wing's eave ("não vais ter dois telhados
    desalinhados um com o outro ainda por cima quando a água de um deles é escoada pela caleira do outro") → one overhang round
    the roof: verge = eave in the configurator (§7 Eaves overhang) → `para_construtor` "empena": beirado.
  - **L67** Every eave piece its own gutter crossed the next at a corner ("caleiras todas bugadas") → one gutter per straight
    run, mitred at the corners (§7 E8) → `camadas.cobertura_faces`.
  - **L68** A tall one-água gutter-wall parapet (≈ 0,7) lined to its top read as the panel colour ("a parte de dentro da
    platibanda fica co a cor do painel sandwich"), and the screen drew its face on the lining's plane → the lining to the top
    only where the parapet stands ≤ 0,50 over the panels, else it laps 0,10 behind the cladding and the façade finish goes
    above (§7 Gutter walls) → JSON `cobertura.caleira_oculta.forro_ate_topo` / `forro_sobre`, `camadas.forro_caleira_ate`,
    worker `cobertura_casa`.
  - **L69** RAL 7016 caps and verge trims on a tile-red roof ("aquelas proteções das cumeeiras que têm de ser da cor da
    cobertura"; the dark grey round the gable's triangle "não é suposto"; a cap not joined to the next) → every roof flashing
    and cap in the roof colour, caps overlapping 0,20 at a node, the high side's remate de topo in the panel colour too (§7
    Covering, Hidden roof) → JSON `cobertura.remates.material`, `camadas.cobertura_faces`. L64's check holds for trims, not only
    the panel.
- **L70** (configurator, 2026-10-30, his answers to the roof questionnaire and step 7) A figure we derived from one house or
  from our own arithmetic had been built as if it were the company's: **one downpipe per 37 m²** (from [TV]'s 2 for ≈ 74 m²)
  → his rule is two per gutter, one on a small one (more by area since his "distribui como achares melhor" — ours, flagged);
  **the 80 × 35 pipe** (the cavity's depth, ours: 7 pipes on his L) → **his 100 × 50** ("Sim usa de 100x50": 4 on the L,
  the standard cavity takes it, a recess behind cork / XPS where shallower);
  **the pergola's top ≤ ring + 0,10** (from [TV]'s ledger) → the ground floor's top; **the hidden panel in grey**
  (Sobral's) → RAL 8004; the 13,5 m panel limit and the 1,00 m separation → 15 m and 2 m (his, later the same day). Rule: a number from one project or from our arithmetic is flagged **ours** and put in
  the questionnaire, and the geometry that depends on it stays easy to change (a JSON key) → §7 (06, 11), §8, §11, §15; JSON
  `caleira_oculta.tubo` / `caleira_pequena`, `pergola.maximo`. (His reading of Torres Vedras, 2026-10-30 later still: a
  project "usado para tu aprenderes sobre nós e nós irmos também avaliando as tuas sugestões" — Legend, index.)
