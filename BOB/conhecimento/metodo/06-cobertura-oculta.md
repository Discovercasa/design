# Método DiscoverCasa — cobertura oculta (§7, Hidden roof) (parte de conhecimento/metodo-construtivo.md, v8.3)

### Hidden roof (cobertura oculta)
- **On the client's screen it is called "Oculta", not "escondida"** — user 2026-10-29 "muda o nome para este termo
  "Oculta" em vez de escondida, sendo que ambas são a mesma coisa mas é para ficar mais profissional no online builder"
  — confirmed (a screen name; same roof) — [cfgr] `main.js` roof cards and texts; the engine, the JSON, cfg and saved
  designs keep the key `escondida` (ours); this rulebook says either.
- **Hidden by the house walls, in ONE água where it works — the best solution per house, not a pattern** — user
  2026-10-15 "Cobertura é escondida pelas paredes da casa"; 2026-10-28 "Aqui depende do caso, nós tentamos sempre só fazer
  uma água e sempre coberturas ocultas"; on his U (a short middle part) "fariamos apenas uma água para a cobertura toda";
  "Não quero que assumas um padrão mas sim a solução mais eficaz e inteligente para cada caso" — confirmed — cfg
  `cobertura` (`tipo` platibanda, `uma_agua`, `cumeeira_y`, `aguas`, `inclinacao_pct`); `casa_planta.construir`. Hidden or
  exposed, and the gutter side: **PO Q14**. [TV] **two slopes** ("Sim é de duas águas", 2026-10-15; D2503) — a project
  fact (TV cfg); why TV took two when one would have fitted (runs 8,50 / 11,00 < the panel's 15 m — cércea, look, parapet height?):
  OPEN — it tells when one água gives way (§15).
- **How the engine chooses** (ours, built 2026-10-28): **ONE slope** falling across the ceiling beams to the side where
  every strip ends on one straight line (one straight gutter); each strip's panels in one length from that gutter up to
  its own high wall; **a "remate de topo" against the high parapet** instead of a ridge (a folded waterproof sheet up the
  parapet's face under a metal flashing, 0,12 up / 0,20 on the panels — his detail, One água below); the house turned so the beams span the shorter depth ("casa rodada 90° …").
  **TWO slopes** — one ridge along the house through every strip, in the middle of the main block (the biggest rectangle,
  D2503's rule) as near as that allows, every slope ≥ 1 m — only when one slope's panels would pass the panel's maximum
  (JSON `cobertura.painel_oculto.comprimento_max` **15** — his, 2026-10-30, Covering below; was 13,5 ours until then) or no
  side is straight. **The gutter side: where both long sides are straight (a rectangle) the client chooses it** (configured-house
  `cobertura.lado_caleira`, the configurator's compass, +y north), only among the sides across the ceiling beams (the
  beams span the shorter depth; on a turned house poente / nascente); default south (poente on a turned house); an
  impossible choice falls back to the default with a note; L / T / U (one straight side) and two-água houses (panels over
  15 m) get no choice — user 2026-10-29 "Podes deixar o cliente escolher" — confirmed (the default: ours) — (superseded
  2026-10-29: "gutter on the south — assumed", PO Q14) — the form: assumed — `para_construtor.cobertura_escondida`
  (`uma_agua`, `cumeeira_y`, `aguas`, `vigas_teto` zones, `lado_caleira`), `rodar`;
  `casa_planta.construir` on 22×7,5 and on lameladas (one plane, a top madre / purlin against each strip's high wall, no
  ridge pair); `camadas.cobertura_platibanda` (remate de topo). 9 shapes audited: 8 in one slope, a 14 × 14 square in
  two; his U 18,95 × 12,65 one slope, parapet 3,82. *Why the 1 m* (two slopes): at the band's edge the ridge fell on a
  wall line (a slope of nothing, a cap on a parapet). (superseded 2026-10-28: "the most efficient = one ridge, two slopes
  mid main block" — the morning's reading of "a forma que seria mais efeciente", now only the fallback.)
- **One água: the gutter only on the low side — the side the panel falls to; none on the high side** — user 2026-10-29
  "como neste caso só tem uma água nós apenas precisamos de ter caleiras no lado para o qual o painel fica inclinado, não
  faz sentido ter no lado que fica mais alta a cobertura" — confirmed (the fault: a "caleira" drawn on the high side — our
  reading: the remate de topo's flat 12 cm shelf; no gutter was built there) — `camadas.cobertura_platibanda`,
  `casa_planta.construir`. **The high side gets a remate de topo lying on the panels** (a flashing — ≈ 0,20 on the panels,
  ≈ 0,12 up the parapet's face under the chapéu, his detail below — not a gutter), **in the panel colour** (user 2026-10-29 night "as caleiras na parte mais
  alta da cobertura oculta continuam lá" — our reading: the dark flashing still read as a gutter — confirmed (the fault) /
  ours (the reading, the colour) — JSON `cobertura.remates.material` "Remate cor da cobertura", §7 Covering; L69) — ours;
  **how DiscoverCasa closes the panels' top end there (his detail, `configurador/docs/revisao/2026-10-30_remate_topo_paineis.png`):
  a waterproof sheet folded from the panels up the parapet's face, under a metal flashing ("remate em metal", in the panel
  colour) that runs from the parapet's face (≈ 0,12 up, room permitting under the chapéu) down onto the panels (≈ 0,20)** —
  user 2026-10-30 "vou-te fornecer uma imagem que demonstra como fechamos a ponta dos painéis, mas leva uma placa
  impermeável basicamente que drobra e leva o remate em metal" (then the image) — confirmed (the build: sheet + flashing) /
  ours (the sizes 0,12 and 0,20 read from the detail; the sheet's product; the lap under the chapéu) — JSON
  `cobertura.remate_topo`; `camadas.cobertura_platibanda` (the builder to check it uses it). **Closes §15 E3.** (superseded
  2026-10-30: the remate de topo "a flange 0,12 on the panels + 0,10 up the parapet's roof-side cladding" — ours, a
  placeholder until his image; X20.) The sides along the slope: no gutter, the parapet's roof side clad (ours — confirm). Two-slope roofs: a gutter on
  both low sides, a ridge cap at the top (as D2503).
- **One continuous gutter per straight low wall — never a gutter per strip**: strips side by side along one low wall share
  one gutter (one fall, outlets at its low points) — user 2026-10-29 "tinha uma peça aleatória no meio das caleiras" —
  confirmed (the fault: on a one-água L / T / U every strip had its own gutter — end caps, a lining plate up to the parapet
  top, two downpipes side by side where two strips met — our reading) / ours (the build) — `casa_planta.construir`,
  `camadas.cobertura_platibanda` (L61).
- **Downpipes: TWO per gutter, at its ends; ONE on a small gutter (≤ 4,0 m); more, evenly spaced between, for 1 cm² of
  pipe per m² drained; the pipe is 100 × 50, the bocal its own section — inside the cladding** — user 2026-10-30 "vamos com
  dois tubos por caleira a nao ser que a caleira seja pequena", "sim está bem" (≤ 4,0), "usa o bocal ideal para esse tubo e
  distribui como achares melhor", and later still **"Sim usa de 100x50"** — confirmed / delegated (bocal, spread) / general
  practice (1 cm² per m²) — a 100 × 50 pipe ≈ 50 m² (his L: 4 pipes, were 7 with 80 × 35; [TV]'s 74 m²: 2 = as built); fits
  the standard cavity (contra-ripado 20 + ripado 35); the full rule, the recess and the superseded 80 × 35 / 10 cm / 37 m²:
  `11-caleiras-tubos-oculta.md` — JSON `cobertura.caleira_oculta.tubo` (`largura` 0,10, `profundidade` 0,05, `m2_por_cm2` 1,
  `caleira_pequena` 4,0); `casa_planta.construir`.
- ⚠ **What one água changes** (ours — to tell, §15): (a) **one gutter takes the whole roof** → the downpipes follow its
  area (above: 1 cm² per m², a 100 × 50 pipe ≈ 50 m² — a long one-água gutter gets more than two, evenly between), and
  **an overflow** (one blocked outlet floods the whole gutter) stays unanswered; (b) **the high wall's upstand above the
  panels is small** (`platibanda.folga` 0,05 along its whole length; usual abutment ≈ 150 mm) → his folded sheet and metal
  flashing go ≈ 0,12 up the parapet's face only as far as the chapéu allows, or the parapet is raised there (X20); (c) the
  parapet grows with the run (3,82 vs TV 3,49: longer studs, a taller cantilever above the ring, the cércea, cladding,
  price — §2); (d) panels up to 15 m: steel-skin expansion ≈ 13–15 mm on a dark 15 m panel (our arithmetic) and a 13,6 m
  truck shorter than the panel — told 2026-10-30, **his "Sim tranquilo": accepted, nothing to change** (the maker's fixing
  rules and the transport stay his; Covering below).
- **Slope: the lowest the panel allows; the ridge — and the house — rise as needed** — user 2026-10-16 "faz com uma
  inclinação do mínimo que é permitido sendo que se a cumeeira tiver de subir pode subir, eu sei que isto altera a altura
  total da casa mas não tem mal é o suposto nestas coberturas escondidas" — confirmed — cfg `cobertura.inclinacao_pct`; no
  panel minimum in the JSON, no check. [TV] **6 %** on every slope (architect's section B 1,3 %) — D2503 — TV cfg
  `inclinacao_pct` 6,0. **The panel's own minimum, Mundiperfil MC 1000/5: 6 % without longitudinal laps — one length per
  slope, so 6 % holds** (Covering below; 2026-10-30). (⚠ before the data sheet: 6 % > Masterpanel's 5 % but < the ≈ 7 % (4°)
  Kingspan KS1000 RW / Europanels give — TV #8, now answered for the MC 1000/5.)
- [TV] **On an L: the ridge along the house in the middle of the main block** (y 6,747, 4,25 from the north face), the
  wing covered by **running the main block's slope on** over it to the wing's own gutter (south panels 6,44 instead of
  3,94) — D2503 sheet 1 "Linha de cumeeira" — company document (one house) — cfg `cumeeira_y`, `aguas` (by hand from a
  plan).
- [cfgr] **The hidden roof at its real height, with its slopes, built the most efficient way** — user 2026-10-28 "nas
  coberturas apresentas a escondida que já deve ter inclinações e deve estar a altura correta … deves usar a forma que
  seria mais efeciente para a cobertura ser montada" — confirmed (the aim) — the form above (no larós or rincões, one
  panel length per strip, straight cuts).
- **No gaps — the roof covers the whole house**: where two strips meet at a re-entrant wall, the open strip's slope runs on
  to that wall's inner face (its panels end against the corner's other wall) — user 2026-10-28 "a cobertura nao está a
  cobrir a casa toda esta com gaps" (circled at a U's courtyard corners and on an L) — confirmed (the fault) / ours (how)
  — `casa_planta.fechar_aguas` (0 gaps on 9 shapes, one and two slopes) (L53).
- **Two slopes — the ridge as low as the slope allows**: the longest slope's gutter madre sits directly on the lameladas,
  the shorter slopes' on packing raised by the difference ([TV] 0,15 = 6 % × 2,5 m); the other madres step up with the slope ([TV]
  undersides above the lamelada top: main block 0,15 / 0,23 / 0,30 / 0,38 at the ridge; wing 0 / 0,08) — D2503 sheet 5 —
  company document — JSON `estrutura.madres`; `casa_planta.construir` (`z_cume` from the longest run).
- **The same height on every side**: every exterior wall rises to one top level — a parapet (platibanda) on every exterior
  wall, the gutter sides included, the chapéu on all, the corners closed — user 2026-10-16 "a casa é suposto ter a mesma
  altura em todos as arestas da mesma ou lados da mesma"; draft "Cobertura oculta em todas as fachadas" — confirmed ("é
  suposto" on one model, kept as a rule — L17) — `casa_planta.construir` (one `z_plat`). **The parapet is the top of the
  exterior modules, one piece from the base, on every hidden roof** (§2) — JSON `estrutura.platibanda_modulos_inteiros`.
- **Parapet top ≈ 3 cm above the ridge cap** — the roof just hidden ([TV] 3,4915 vs cap 3,465; ≈ 7 cm above the panel top
  at the ridge 3,42; ≈ 0,30 above the panel ends at the main block's gutters, ≈ 0,45 at the wing — our arithmetic) — D2503
  sheet 5 — company document — TV cfg `platibanda.topo` (3,4915 v4; 3,50 v5 = the module table — which was built: OPEN).
  ⚠ Without `platibanda.topo`, `casa_planta.py` puts it `platibanda.folga` 0,05 above the panel top at the ridge (≈ 2 cm
  under D2503, below the cap); on one água the same 0,05 runs along the whole high wall (above). ⚠ Near the ridge the
  gable abutment flashing has only ≈ 7 cm (usual ≈ 150 mm) → lap it up under the chapéu's inner leg — general practice
  (TV #4). ⚠ To check (ours): the remate de topo's ≈ 0,12 up the parapet's face vs the parapet's 0,05 over the plane's top — at the
  highest wall it may stand ≈ 7 cm past the parapet top, through the chapéu → stop it under the chapéu's inner leg or raise
  the parapet there (X20).
- **Covering: 5-rib (5 ondas) sandwich panel 80 mm**, 1 m useful, lengths from the project, ridge (2 águas), sealing tape,
  Turbosharp 6×160 — draft — company document — JSON `cobertura.painel_oculto` (`espessura` 0,08). **The 80 mm is confirmed:
  user 2026-10-30 (later still), on our 15 m panel point, "Sim tranquilo já agora usamos os de 80mm"** — confirmed (the
  hidden panel's thickness; whether it also covers the exposed roof's Munditelha: OPEN, asked — 05). Maker, colour and the chapéu
  colour per house: **PO Q15**. **The hidden panel is the 5-ondas panel imitating tile, colour RAL 8004 — the same tile
  colour as the Munditelha, never grey; the grey was only Sobral's** — user 2026-10-30 "é o ral 8004 e sim é o painel de 5
  ondas imitação cor telha, o cinzento foi apenas para sobral"; before, 2026-10-29 "cor original do painel de sandwich … e
  não cinzenta a cobertura" — confirmed (closes §15 B1 colour, E1) — JSON `materiais."Painel sandwich 5 ondas"` #8F4E35
  (was #9A4F33 assumed until 2026-10-30, grey #9AA0A6 until 2026-10-29); [SB] Sobral's grey stays a project fact. **Panel
  length variable, 1 m wide, one panel interlocks with the next — "eles já são produzidos de forma a isto ser possível fazer
  sem problemas"** (user 2026-10-30 "Comprimento do painel é váriavel a largura é de um metro e nós encaixamos um painel no
  outro") — confirmed (the maximum: next line) — JSON `cobertura.painel_oculto`.
- **The hidden panel is the Mundiperfil MC 1000/5; its maximum length is 15 m** — data sheet
  `conhecimento/fontes/ficha_MC_1000-5_PUR_PIR.pdf`: thickness 30–100 mm; core PUR (fire reaction F) or PIR (B-s2,d0);
  U 0,25 W/m²K at 80 mm; 12,45 kg/m² (steel 0,5 / 0,5); ribs 35 mm high at 250 (5 ondas over 1 m); laps 300 mm over a
  support; **minimum slope 6 % without longitudinal laps**; supports ≤ 1,50 m — user 2026-10-30 "afinal o máximo do painel
  é 15 metros" (he first wrote 25, then corrected) — confirmed (15 m) / company document (the data sheet) — JSON
  `cobertura.painel_oculto.comprimento_max` **15** (was 13,5, ours, a truck's length, until 2026-10-30). **Closes §15 E2.**
  **Our points on 15 m (a panel longer than a 13,6 m truck; steel-skin movement ≈ 13–15 mm; check with Mundiperfil) —
  his "Sim tranquilo" (2026-10-30 later still): accepted, nothing to change.** Core: **PUR or PIR per house (PO Q15)** — our
  advice, PIR (B-s2,d0) near neighbours or a garage — "Ok tranquilo": taken, still per house. Thickness 80 mm: confirmed
  (Covering above). Not for marine / aggressive air with the standard coating — **already checked for TV** (his "já foi
  verificado", 2026-10-30 later still), stays per house (PO Q15). Supports ≤ 1,50 m vs the madres' spacing: the builder to
  check.
- **Panels: one length per slope** (no end laps; [TV] 3,94 north and main-block south, 6,44 over the wing), **laid from one
  end with the cut strip at the other** ([TV] from the east, a 3,94 × 0,25 strip at the west); at the re-entrant corner
  one long panel **cut in an L** ("PORMENOR TELHA PARA REMATE": 3,94 + 2,50 × 0,47, 0,53 cut off); **ridge caps ordered by
  count** ("ENCOMENDAR 18 CUMEEIRAS" for 17,5 m); the panels run ≈ 0,10 past the gutter madre into the gutter — D2503 sheet
  4 (it calls the panels "telhas") — company document — `camadas.cobertura_platibanda` (from the east end; [TV] 30 × 3,94 +
  7 × 6,44), JSON `estrutura.madres.beiral` 0,10; the ridge cap (two slopes) folded onto the panels ("coladas", Covering),
  counted in metres — X12-like, not by count. One água: one length per strip, the remate de topo at the top.
- **The gutter (caleira oculta) and its downpipes** — gutters at the level of the rufos; the caleira oculta INSIDE the parapet
  (company build, [TV] as built 0,31 / calços / fall 2 %, the site photos, on 22×7,5); the caleira interior 20 cm; **the
  downpipes (100 × 50)**, inside the cladding, ending above the base, at the low ends; the outlet holes and their type; the
  overflow — all moved to `11-caleiras-tubos-oculta.md` (v8.8; same § 7, text kept, the section updated).
- **Parapets are clad on the roof side too — an exterior wall on both faces, in the house's own façade finish** (gutter
  walls excepted while ≤ 0,50 over the panels, next line): from inside out **wool in the frame, OSB 15, Traspir, then the house's façade build-up** (A
  ripado + Tremolo with the façade's contra-ripado, B capoto, C cork — §8) — user 2026-10-15 "essa paredes que ficam acima
  do rufu levam também as seguintes camadas (ordem de dentro para fora): lã mineral, osb 15, membrana transpir, ripado
  horizontal e tremolo vertical" (said on TV, a Tremolo house: TV's finish, not every house's); 2026-10-28 "o capoto tem
  que ficar na casa toda a cobertura não tem um revestimento ou isolamento diferente" — confirmed (the façade finish on
  the roof side) / assumed (OSB 15 + Traspir under capoto / cork, from TV's list) — `camadas.camadas_platibanda` (OSB 15
  + Traspir of JSON `cobertura.platibanda_interior.camadas` + the layers of `exterior.opcoes[opcao_visivel]`),
  `camadas.platibanda_interior`, [cfgr] worker `cobertura_casa` (L52). (was TV's Tremolo list on every house until
  2026-10-28.) **What goes under the capoto there: OPEN** — ⚠ ours: with capoto both faces of the parapet are XPS (Sd
  ≈ 6–9 m each) under a metal chapéu → the frame and its wool cannot dry → a vapour-open board (wood fibre / cork) on the
  roof side, or no wool there; the capoto's foot over the panels / flashing on a starter track with a drip, its lowest
  band reinforced (splash). Wool 80 assumed; ⚠ wool above the insulated ceiling has no thermal role and holds water
  against the frame — general practice (TV #4 e). The parapet ripado follows the façade's 0,35 from the bottom (§8).
- **Gutter walls: the gutter lining runs up to the top of the wall, where it meets the chapéu** (no cladding on their roof
  side) — **only where the parapet stands ≤ 0,50 over the panels' ends** (D2503, [TV] 0,32 / 0,47 as built) — user
  2026-10-20 "revestimento da caleira até ao topo que depois se encontra com os chapéus da platibanda" —
  confirmed (as D2503's sections; the 2026-10-19 photo was an earlier stage) — JSON
  `cobertura.platibanda_interior.paredes_com_caleira` false; `camadas.cobertura_platibanda`. **Taller** (a one-água's low
  side, ≈ 0,7): **the lining laps 0,10 behind the parapet's cladding and the façade finish goes up above it, to the chapéu**
  — user 2026-10-29 (night) "a parte de dentro da platibanda fica co a cor do painel sandwich" (the lined 0,7 wall read as
  the panel's colour — our reading, L68) — confirmed (the fault) / ours, to confirm (0,50 and the 0,10 lap; §15 E4) — JSON
  `cobertura.caleira_oculta.forro_ate_topo` 0,50 / `forro_sobre` 0,10, `camadas.forro_caleira_ate`; the screen draws the
  parapet's face on the engine's plane (worker `cobertura_casa`). (superseded 2026-10-29 night: the lining to the top on every
  height.) Junction (general practice, SC §6): the chapéu's inner leg laps over the lining's top (shingle order), the
  fixings under the leg, a membrane over the wall top.
- **Gable parapets: the roof-side cladding runs to the END OF THE SANDWICH PANELS** (over the strip where the panels
  overhang the gutter, ≈ 0,10 past the madre) — user 2026-10-19 (18:12) "esse canto está mal feito porque o forro é suposto
  ir ate ao final do painel sanduiche" — confirmed — `camadas.platibanda_interior` (L36). Past the panel ends, over the open
  gutter, the gutter's end cap lines the gable face up to the top — assumed (by analogy with the gutter walls; to confirm,
  low priority, TV #15). Junction (general practice): a trim on the vertical joint, the end plate lapped behind the Traspir,
  the cladding foot ≈ 50 mm clear of panel and gutter, end grain sealed — not in the tools.
- **Chapéu = the parapet rufo** ("Os Rufos da platibanda na realidade nós chamamos de Chapéus"): **round the whole
  perimeter of the hidden roof**, it **wraps the wall top** — the whole width (frame + both claddings), tight to the wall,
  legs **≈ 2 cm down both faces**, "como se encaixassem na parede" — user 2026-10-16 "eles envolvem a parede ou seja cobrem
  toda a largura e ficam junto da parede do lado de dentro e de foram cerca de 3 cm para baixo"; 2026-10-28 "os chapéus
  como eu já te havia dito cobrem/envolvem o perímetro todo da cobertura escondida ficando do lado com 2 cm
  aproximadamente para baixo tal como no projeto de torres vedras" ("do lado" read as each side); **2026-10-29** "Há um dos
  lados na cobertura oculta em que o chapéu não esta a cobrir a largura toda" — **on every wall of the perimeter it covers
  the parapet's full width as built** (frame + the claddings of both faces, or the frame + the gutter's lining ≈ 0,11 deep
  on a gutter wall) — confirmed (a repeated fault, on the screen: L63) — **flat**
  (D2503 sheet 5; user 2026-10-16 night "Como está feito no modelo mais recente, está ótimo") — JSON `cobertura.chapeu`
  (`descida` **0,02**, `queda` 0, 2 mm); `camadas.chapeus`. (was ≈ 3 cm, `descida` 0,03, until 2026-10-28.)
  Product (sheet, thickness, colour, bar length): OPEN (JSON "chapa lacada"; the roof's other flashings are in the panel
  colour — RAL 8004 since 2026-10-30 — whether the chapéu follows: §15 B2). ⚠ A leg tight to
  the boards draws water and closes the cavity top → legs kicked out into a drip ≈ 10 mm off, a 10–20 mm meshed vent gap,
  a membrane under, a 1–2 cm fall to the roof side — general practice (CM §4, TV #13).
- **Chapéus closed at the corners, covering every wall top once and never overlapping**: at each corner one chapéu runs on
  to the far edge of the wall across and folds down its end, the other butts against it; at a re-entrant corner the outer
  leg stops where the wall across begins; this follows the actual corner, whichever frame runs through — user 2026-10-15
  "falhas nos cantos do rufo de platibanda onde se chovesse a água entraria para dentro do revestimento"; 2026-10-20 "eles
  não podem deixar o topo destapado e segundo eles não dão overlap uns aos outros senão criaria folgas entre camadas" —
  confirmed / assumed (which one covers the corner) — `camadas.chapeus` (`ate_parede`) (L1, L38). How the butt joints and
  corners are made watertight: OPEN — general practice: a joint strip (cobre-junta) with a gasket under each butt joint
  (a dark aluminium chapéu moves ≈ 2 mm per metre, ≈ 5–6 mm on 3 m) or one-piece folded corners, over a membrane on the
  wall top.
- **Chapéus look continuous in the finished house; what goes under them the user will confirm — remind him** — user
  2026-10-20 (13:25) "Por baixo dos chapéus lembra-me mais tarde para te confirmar o que leva" — promised (§15); do not model
  it before he answers (§15 E6). Our view given: tight butt joints of the same colour (folded lengths ≈ 3–6 m). The tools model one
  piece per wall top, no joints, no membrane.
- **Every parapet end standing over a roof is closed** — clad or lined and capped on every face, its end included ([TV]
  P03's end over the wing roof) — user 2026-10-16 "algo no canto do primeiro screenshot está errado" — confirmed —
  `camadas.cobertura_platibanda`, `camadas.platibanda_interior`, `camadas.chapeus`; `pormenores.py` (L19).
- Façade cladding goes up to the top of the highest wall behind it (parapet or roof edge), past the outside corners — L5
  — confirmed — `camadas.degraus`.
- Coping and abutment details to agree (general practice, CM §4, SC §6, TV #4 b–e): a self-adhesive membrane over the
  parapet top under the chapéu (Traspir is not a roof membrane); low sides in shingle order with profile closures
  (tapa-ondas) under the 5-rib profile; cladding ends ≈ 50 mm clear of the panel, end grain sealed — not in the tools.
- [cfgr] **The configurator shows the hidden roof as built** (worker `cobertura_casa`, 2026-10-28): one água or two at the
  panel's minimum (6 %) at their real height, no gaps, the caleira oculta, the chapéus round the whole perimeter, the
  remate de topo or ridge cap, downpipes inside the cladding, the parapets at the engine's height, the gutter walls lined,
  the other parapets clad on the roof side **in the house's façade finish** (Parapets above) — user 2026-10-28 — confirmed
  (that it must show) — L48, L52, L53, L56. 2026-10-29 (his "Erros nas coberturas ocultas"): the screen draws the parapet as
  wide as the engine builds it (each façade option's own depth outside — A 0,0865, B 0,0755, C 0,1095 — not a flat 0,09 /
  0,16), the gutter only on the low side, one gutter per low wall, the outlet holes in the gutter's bottom, the panel in
  its tile colour (L61–L64). 2026-10-29 (night): the gutter lining's height rule and the flashings in the panel colour
  (L68, L69).
- Skylights: [TV] none built — the 2 of the roof plan left out — user 2026-10-16 "Não foram construidas podes não incluir as
  claraboias" — confirmed (TV #10); per project **PO Q17**. How DiscoverCasa frames one (a kerb and flashing on a low-slope
  panel roof — general practice): OPEN — not in the tools.
