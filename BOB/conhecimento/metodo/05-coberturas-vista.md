# Método DiscoverCasa — coberturas: geral, estrutura e cobertura à vista (§7) (parte de conhecimento/metodo-construtivo.md, v8.3)

## 7. Roofs (coberturas)
- **Hidden roofs are the usual roof today; exposed roofs usually two or more águas "pelo aspeto tradicional"** — user
  2026-10-28 "nós tentamos sempre só fazer uma água e sempre coberturas ocultas até porque hoje em dia já não se usa tanto
  telhados"; "Nas casas com cobertura á vista é que normalmente fazemos duas ou mais águas pelo aspeto tradicional" —
  confirmed — **PO Q14** (default: the architecture's type; hidden, one água where it works — Hidden roof).

### Covering (every roof)
- **Always a sandwich panel; telha or another covering only at the client's request; "para já" the configurator offers
  only the sandwich panel** — user 2026-10-21 "Nós usamos sempre painel sandwich a não ser que seja um pedido do cliente não
  usar painel sandwich e usar telha por exemplo mas para já vamos deixar no DiscovercasaBuilder apenas o painel sandwich
  como opção" — confirmed — JSON `cobertura.painel` (exposed), `cobertura.painel_oculto` (hidden); [cfgr] `main.js`
  `COBERTURAS`. Exposed: Munditelha (below); hidden: 5-rib 80 mm (Hidden roof). A tiled house roof (on request, later)
  needs its own build-up (battens, counter-battens, an underlay, clay usually ≥ ≈ 30 % without a continuous sub-roof,
  ≈ 0,4–0,6 kN/m² more) — general practice — OPEN, not in the tools.
- **Caps and flashings lie on the panels ("coladas")**: ridge and rincão caps, the hidden roof's ridge cap, abutment
  flashings and the one-água remate de topo folded down onto the panels, no gap under their edges — user 2026-10-28 "As
  cumeeiras qaundo estão a vista estão pousada na cobertura e tem um gap entre elas e a cobertura, outro erro que não faz
  sentido tu sabes que elas estão "coladas" à cobertura" — confirmed (ridge caps) / ours (the others, the same detail) —
  `camadas.cobertura_faces` (`dobrada`), `camadas.cobertura_platibanda` (L55). "Coladas" to the eye: under the cap a
  profile closure / filler on the ribs, sealed — general practice (CM §4) — not in the tools.
- **Every roof flashing and cap is in the roof's colour — cumeeira, rincão, laró, remate lateral, encosto, remate de topo —
  never grey** — user 2026-10-29 (night) "aquelas proteções das cumeeiras que têm de ser da cor da cobertura"; the grey
  round the empena's triangle "não é suposto" — confirmed (caps; the other pieces ours, the same detail) — JSON
  `cobertura.remates.material` "Remate cor da cobertura" (#8F4E35 = RAL 8004 since 2026-10-30, once he named the panel's RAL;
  was #9A4F33; superseded 2026-10-29 night: "Remate RAL 7016") (L69).
  **Caps run on 0,20 over a node where another cap or a valley meets at an angle, overlapping — never ending short of the
  next** — user (same) "a proteção da cumeeira fica ali não unida a outra proteção" — confirmed (the fault) / ours (0,20) —
  `camadas.cobertura_faces`. The chapéu (hidden roofs) is not in this list — its colour per house, PO Q15 (§7 Hidden roof).

### Structure (every roof)
- **Prumos** (vigas verticais) standing on the ceiling beams and screwed to the purlins, one on every beam under every
  purlin — user 2026-09-30 "as vigas verticais … são precisamente para dar a inclinação pretendida", 2026-10-09 "the
  prumos are right" — confirmed (110×75 assumed) — JSON `estrutura.prumos`.
- **Purlins (vigas de apoio à cobertura) 110×75**, perpendicular to the beams (parallel to the ridge), give the slope, the
  panels screwed to them, **≤ 1,2 apart** (SB 4 per slope; 3_Vigamento 0,89) — user 2026-09-30 "que dão a inclinação da
  cobertura", 2026-10-09 "the vigas de apoio a cobertura are right" — confirmed + company document — JSON
  `cobertura.vigas_apoio.espacamento_max` 1,2 (laid flat — assumed).
- **Hidden roof on lameladas: madres 110×75 on edge** (75 wide × 110 high), parallel to the ridge, on prumos on every
  lamelada; from each gutter up the slope at **≈ 1,26 (≤ 1,265)**, the last bay to the ridge shorter ([TV] 1,21); a
  **ridge pair 0,10 apart** (axes); the gutter madre's axis 0,40 from the wall axis (0,31 clear = the gutter); **pieces
  ≤ 3,66** (4 bays of 0,915) jointed on a lamelada — D2503 sheets 2, 3, 5 [TV] — company document — JSON
  `estrutura.madres` (`espacamento_max` 1,265, `cumeeira_entre_eixos` 0,10, `peca_max` 3,67); `casa_planta.construir`.
  ⚠ 1,26 > the purlins' ≤ 1,2: the panel's span table decides — general practice. Flat or on edge over 22×7,5 beams: OPEN
  (the builder lays them flat).
- **Every madre line is one line across the house**, from the inner face of one exterior wall to the next, continuous where
  two slopes meet with no wall between them, jointed only on a lamelada — user 2026-10-21 "algumas vigas não estão
  interligadas" — confirmed (the break is wrong) / assumed (wording) — `casa_planta.construir` (`dentro_da_casa`). Not
  checked on 22×7,5 roofs (L47).
- **Ridge madres over long lameladas: 22×7,5** ([TV] over the wing's 11 m lameladas, as D2503's label — "então é como estão
  no desenho com 22x7,5", user 2026-10-16 — confirmed); **both ridge madres change section at the same place, on the last
  long lamelada** — assumed (a pair is one detail, L47) — JSON `estrutura.madres.cumeeira_vao_longo` (`lamelada_min` 9,0;
  top level with the 11×7,5 ones, prumos 0,11 shorter); `casa_planta.construir` (`troca`). **The company's criterion —
  promised** ("Posso te responder a isso depois", 2026-10-21); until then the > 9 m trigger is OURS, said so in every
  delivery, and the reason should show with the model ("22×7,5 — sobre lameladas > 9 m, critério nosso a confirmar") — not
  in the tools. He asked twice (TV, the U 11,60 × 18,50).
- On DiscoverCasa timber, never the architect's steel purlins — user 2026-10-15 "Cobertura sem estar a vista sobre a nossa
  estrutura de madeira" — confirmed.
- **Slope**: exposed roofs — the client's look, ≥ 15 % (Exposed roof); hidden roofs — the lowest the panel allows (Hidden
  roof); a house with a project — the project's slope (PO Q14; an exposed slope under 15 % → ask) — user 2026-10-15 "a
  inclinação deverá estar descriminada nos desenhos fornecidos penso eu" — confirmed — cfg `cobertura.inclinacao_pct`.
  ⚠ `casa_planta.py` falls back to 5 % when the key is missing (L6).
- The slope must suit the panel and the beams' sag: 5-rib panels usually ≥ ≈ 5–7 % (≈ 3 % for some single-length
  panels), tile-effect ≥ ≈ 10 % (Munditelha's own figure OPEN); with larós / rincões the check is on the laró (face ÷ √2);
  a ridge at mid-span of long beams loses slope near the gutters with creep ([TV] glulam ≈ 8,2 m: 6 → ≈ 4 %) — general
  practice (CM §4, TV #6, #8) — the only check in the tools: an exposed roof under 15 % gets a note.

### Exposed roof (cobertura à vista)
- **Gable ends (empenas): a framed triangle on the tie beam** — user 2026-10-09 "its fine like that" — confirmed —
  `estrutura_dc.emoldurar_empena` (build: E6).
- **The covering: Munditelha® (Mundiperfil)** — tile-profile sandwich panel, PUR or PIR core, lacquered steel or aluminium
  skins, 40–60 mm, useful width 1000, wave pitch 200, relief 45, CE — user 2026-10-22 "Sim exatamente, utilizamos o
  munditelha da mundiperfil tal como no segundo screenshot" — confirmed (product) / company document (the maker's sheet) —
  JSON `cobertura.painel` ("Painel sandwich Munditelha", relevo 0,045, passo 0,20, largura 1,0, núcleo 0,04 assumed, steel
  assumed). Not said: thickness, PUR / PIR, skin — **PO Q15**, §15 B1. ⚠ **2026-10-30 later still, on our 15 m panel
  point (hidden roof), he wrote "já agora usamos os de 80mm"** — said of the hidden 5-ondas panel (80 mm confirmed there,
  06); **whether it also covers the Munditelha is ambiguous and asked — OPEN: the core stays 0,04 (assumed), not 80**
  (the maker's Munditelha sheet gives 40–60 mm, so 80 would be outside it — our reading, to confirm). **Colour: the maker's original tile colour, never grey**
  — user 2026-10-29 "Mais uma vez quero a cor original do painel de sandwich (mundiperfil painel sandwich) e não cinzenta
  a cobertura" — confirmed (original, not grey; "mais uma vez" = said before, no earlier message in the registo);
  **the colour is RAL 8004** — user 2026-10-30 "é o ral 8004" — confirmed (closes §15 B1's colour; the maker's own reference name still
  not asked) — JSON `materiais."Painel sandwich Munditelha"` #8F4E35 (was #9A4F33 assumed; dark grey RAL 7016 provisional
  until 2026-10-29); [SB] Tipo 1 keeps its own "dark grey" (user 2026-09-24 — a project fact, SB cfg; "o cinzento foi
  apenas para sobral", 2026-10-30), never copied. From Mundiperfil's
  data sheet, still to read: minimum slope (vs 15 % faces, ≈ 10,6 % larós), purlin span (vs ≤ 1,2), overhang allowed (vs
  0,50), ridge / rincão / laró / verge pieces, closures — OPEN; the order unit missing (X11). Draft's parts kept: ridge
  (2 slopes), sealing tape between panels, remates laterais, Turbosharp 6×160 — company document.
- **Slope: by the look the client wants, minimum 15 % (≈ 8,5°)** — user 2026-10-21 "A inclinação mínima da cobertura à
  vista é 15 %"; "Depende do aspeto que o cliente queira" — confirmed — JSON **`cobertura.inclinacao_min_avista_pct` 15**
  (read by `para_construtor.py` — a note under it, not a refusal — and the configurator's `INCLINACAO_MIN`); our default =
  the minimum; [cfgr] 15–100 % in 1 % steps (100 % cap ours), designs v3 in %, v2 (degrees) converted; `telhado.py` in %.
  At 15 % the ridge rises 0,15 per metre of run (a 9 m-wide 2-água body ≈ 0,68 m over the eave purlin); a 90° laró /
  rincão falls at 15 ÷ √2 ≈ **10,6 % (≈ 6,1°)** — against the panel's minimum (a generic 10 % leaves ≈ 0,6 points). The
  ridge rising with the width — "Isso é tranquilo, don´t worry mas anota na mesma" (2026-10-21) — confirmed. [SB] 26,4°
  (≈ 49,6 %).
- [cfgr] **Only exposed roofs with empenas à vista are offered**: a **rectangle: Oculta · "Duas águas, com empenas à
  vista"** (the card "Escondida" until 2026-10-29 — screen name only, Hidden roof); an **L / T / U: Oculta · "Duas águas, com empenas à vista" (every free end an empena, engine `duas_aguas`) ·
  "Várias águas, com empenas à vista" (engine `misto`: the main body hipped, the wings' ends gables)** — user 2026-10-28
  "Deixa duas águas e várias águas apenas com empenas á vista"; 2026-10-27 "Quero também com duas águas e depois várias
  águas" — confirmed (only roofs with empenas; an L / T / U also gets "Duas águas") / assumed (the meaning of each card);
  **`misto` kept for now** — told it is asymmetric on his U: "Tranquilo depois se necessário removemos essa opção"
  (2026-10-28) — confirmed — `main.js` `COBERTURAS` / `ORDEM_COB`; `acertarCobertura` (a saved `quatro_aguas` opens as
  `duas_aguas` on a rectangle, `misto` on an L / T / U; a rectangle never gets `misto`). `quatro_aguas` stays in the engine
  (the misto body's ends, a project's hipped roof — E9), not offered. **OPEN** (§15): misto keeps rincões on its body — is
  that "com empenas"? On an L his "duas águas" may mean one ridge and two planes (TV's hidden L: "Sim é de duas águas",
  2026-10-15) and "várias águas com empenas" the cross-gabled roof; the default card on an L / T / U (his "normalmente
  usamos várias águas", 2026-10-21, points to "várias águas"). **A house with a project keeps its own roof** (hipped
  included) — **PO Q14**. A rectangle "por regra geral … o de 2 águas" (2026-10-21) stands; 4 águas dearer — yes in general
  (four rincões, bias-cut panels ≈ +10–15 %, gutters on four sides; no empenas) — ours, moot for the configurator.
- **How the engine builds an L / T / U** (`telhado.py` `decompor` / `telhados`; ours, to confirm with a sketch): the
  outline cut into rectangles — **the main body = the biggest rectangle**, the wings the biggest free rectangles touching
  one already placed; one slope and eaves height everywhere; each rectangle 2 águas with empenas at its free ends (or
  hipped, `quatro_aguas`; per rectangle in `misto` — body hipped, wings gabled); the body's ridge along its longer side,
  but a squarish 2-água body (sides < 1 : 1,6) along the edges the wings meet (hipped bodies keep the longer side); **a
  wing's ridge runs to the body, its roof running on into the body's slope up to the body's ridge in two larós — no rincão
  at an L's outer corner**; a wing at a hipped end goes in by half its width; a wing wider than the body runs across it, and
  **a body ending inside such a wing's span runs into the wing up to the wing's ridge with no overhang there** (L50); a T
  stem crossing its bar: the bar's overhang taken off in front of the stem's gable; a wing at a body's gable end **abuts
  the gable ("encosto")** — the gable framed whole, a glulam header 220×100 under it where no wall is below, the façade clad
  above the lower roof, an abutment flashing (X7). ⚠ Ours: on a **U whose arm is the biggest rectangle** (his 25 × 10: arms
  10 × 10 = 100 m², bar 25 × 3 = 75 m²) misto hips that arm into a pyramid and gables the other — asymmetric (X7; told 2026-10-28, kept).
  Audited (the caller's): 2 064 + 1 032 surface cases (2026-10-27); timber `auditar_cobertura.py --formas` 0 clashes on the
  offered roofs, 108 more cases 2026-10-28 (L51). Our three cautions given 2026-10-21 (`insights.md`): the laró's slope,
  the bias cuts (the laró is where leaks happen), the ridge rising with the width.
- **Larós and rincões** (general practice, CM §4): at a 90° plan corner the line falls at face ÷ √2 (15 % → ≈ 10,6 %; [SB]
  26,4° → ≈ 19,3°) → the panel's and the caleira de laró's minimum checked on the laró; each line needs a member, the
  panels cut on the bias (core sealed, closures under the cap), a **rincão cap** over every rincão, a **caleira de laró** on
  its own support under every laró with the panel ends cut parallel and lifted clear, a **downpipe at every laró foot** —
  not in the draft or the JSON; in the tools in part (member 110×75 on edge on prumos; rincão cap and a flat caleira de laró
  strip — `camadas.cobertura_faces`; X10, X13, X15).
- **How the rincão / laró members meet the rest — nothing passes through anything** — after the user's 2026-10-28 "nas
  junções umas vigas +assam em cima das outras" (160 members inside one another on his U) — the fault confirmed, the rules
  ours — `telhado_estrutura.construir`, checked by `auditar_cobertura.py` (E11): (1) **every purlin ends against the side
  of the rincão / laró member, cut on the skew — each long edge to the member's side, 2 mm off; square where the member
  ends before — its end fixed with estribos (hangers)** — user 2026-10-28 "estribos." (asked how the purlin ends are
  fixed); 2026-10-29 (night) "existem ainda gaps entre as vigas, no máximo podemos cortar a vigas com a diagonal
  necessária para encaixar as vigas umas na outras mas desta forma não pode ficar" — confirmed (no gaps; the skew cut is
  acceptable, "no máximo") / ours (2 mm) — `telhado_estrutura.ponta_obliqua` (superseded 2026-10-29 night: a square stop
  at the member — it left a triangle open at every hip, L65); the product (skewed / sloped hangers, or square ones with a
  bevelled purlin end) and the joint itself: OPEN (§15 A2), ours (CM §6); not modelled or counted (X9); (2) **members
  meeting at a node are mitred — each side cut to the bisector, not square** — ours, from the same remark
  (superseded 2026-10-29 night: members stopped at the bisector with a square trim) — `telhado_estrutura.construir`; (3) **over the house a
  rincão / laró foot sits on the ceiling beams, cut to them; over the overhang it runs free** to the panel corner —
  ≈ beirado × √2 (≈ 0,35 at 0,25, ≈ 0,57 at 0,40, **≈ 0,71 at the 0,50 maximum**); (4) **a ceiling beam under the top of
  every rincão / laró, a prumo under the apex**; (5) **one prumo per place**. ⚠ Ours: a 110×75 cantilevering ≈ 0,7 under
  the panels' corner wants a check (X19; was ≈ 0,78 at the old 0,55 maximum, past the audit's 0,75).
- **Eaves overhang (beirado) 0,25 by default, from 0,20 to 0,50; a lower maximum per house when a model shows a
  problem** — user 2026-10-21 "Sim pode ficar mas lá está isso vai depender de outras condicionantes e do que o cliente
  desejar mas podes usar isso como default"; 2026-10-22 "O mínimo de beirado possível é 20 cm"; 2026-10-28 "Beirado vamos
  definir um máximo de 50 cm se vires que é problemático em algum dos modelos podemos dimnuir nesse modelo" (after our
  point on the rincão tail at 0,55) — confirmed — **PO Q14** — JSON `cobertura.beirado` 0,25, `beirado_min` 0,20,
  `beirado_max` 0,50; `para_construtor` clamps with a note; [cfgr] `main.js` `BEIRADO` 0,20–0,50 clamps (typed and
  saved designs). (was 0,55, "o máximo é 55cm" 2026-10-22, until 2026-10-28.) A per-house lower maximum: not in the
  tools (cfg — ours). Measured from the frame's outer face ([SB] "≈ 0.25 m from the frame"; ≈ 0,16–0,19 past a finished
  façade) — assumed. **Verge (empena) overhang = the eave overhang** (the client's beirado 0,20–0,50) in the configurator —
  user 2026-10-29 (night) "o beirado do triângulo nao coincide com o beirado da outra cobertura... não vais ter dois
  telhados desalinhados um com o outro ainda por cima quando a água de um deles é escoada pela caleira do outro" —
  confirmed (the fault: one roof's overhang out of line with the other's) / ours (verge = eave everywhere; closes "does the
  0,20 minimum bind the verges?") — `para_construtor` "empena": beirado (L66). The JSON `cobertura.empena` **0,12** ([SB],
  "≈ 0.10–0.12 m from the frame") stays for older models ([TV]) (superseded 2026-10-29 night as the configurator's verge: 0,12
  ours, "below the 0,20 minimum — OPEN"). A 0,50 eave is a panel cantilever → Munditelha's table (general practice: check
  past ≈ 0,3–0,4).
- When the DiscoverCasa structure raises the roof: keep the pitch or the ridge — [SB] OPEN (user 2026-10-15 "para ja ainda
  nao vou tomar essa decisão", SB #22) — JSON `estrutura.cobertura_manter` "inclinacao". Hidden roofs: the ridge rises
  (Hidden roof); configured houses: the client's slope kept, the ridge follows (ours).
- **No gap between the roof and the walls** — the façade layers and the empenas run up to the panels' underside — user
  2026-10-22 "há um gap que fica visível entre o telhado e as paredes que não quero que esteja assim porque não corresponde
  à realidade" — confirmed — `camadas.sob_faces` (gables included) ✓; [cfgr] `cena.js` (L48). How the eaves line is closed
  (cladding to the panel, a profile closure / comb filler, a vent with insect mesh for the cold attic): OPEN (§15 B4) — general
  practice: closures under the profile at eaves and ridge, the attic ventilated — not in the tools.
- [cfgr] **The screen draws each roof as the engine builds it** — the exposed roof's gutters, downpipes, ridge / rincão caps,
  caleiras de laró, verge trims, abutment flashings from `camadas.py` (worker `cobertura_casa`) — user 2026-10-28 "faltam
  calheiras, tubos de queda e esses elementos" — confirmed (they must show) — L48.

### Exposed roof — the build, in order
Built from a configured house by `casa_planta.py` `a_vista` (surface `telhado.py`, timber `telhado_estrutura.py`,
covering `camadas.cobertura_faces`, façade layers under it `camadas.sob_faces`; read against E1–E11 2026-10-22 — "engine
✓" = matches, deviations **X1–X19** in §15; timber audited by `auditar_cobertura.py` since 2026-10-28); [SB] from the
engineer's drawings by `estrutura_dc.py` + `camadas.cobertura`.
- **E1 Walls**: exterior and interior modules framed to the clear height — module top = floor + pé direito + 0,0565
  (régua 27 + perfil 17 + Pladur 12,5) − 0,11 ≈ **pé direito − 0,05** ([TV] v1–v3: 2,60 → 2,552); on every exterior wall
  the **afinação 110×35 + amarração 110×75 on top, all round**, on interior walls the viga de amarração upright, level with
  it; the false ceiling at the 27 mm suspension (no `teto_sob_anel`) — draft + user 2026-09-30, 2026-10-19 — company
  document + confirmed / assumed (the draft's top pieces as the exposed-roof rule) — `casa_planta.construir` (not-`anel`),
  `estrutura_dc.py`. **Modules raised for the highest opening head** ("opção a", §3). Engine ✓; the raise in
  `para_construtor` ✓ (its note to name the opening), not from a plan — X1.
- **E2 Ceiling beams**: 22×7,5 at ≤ 1 m (equal division), perpendicular to the ridge, eave wall to eave wall, on the
  amarração, **over the wall to its outer face**; free span ≤ 8 m; past 8 m glulam 20×10 at ≤ 0,92; bearing on the
  interior walls — user 2026-09-30, 2026-10-09, 2026-10-15, 2026-10-19 — confirmed / assumed (to the outer face; glulam on
  an exposed roof) — `estrutura_dc.py`. Wings, hip ends, crossings, open sides: §6 (a)–(e) and the header. Engine ✓ (per
  rectangle, equal bays ≤ 1,0 / ≤ 0,92); glulam trigger and levels X2, X3; open side X4.
- **E3 Prumos 110×75** (section assumed) on **every ceiling beam under every purlin**, screwed to the purlin; none under the
  eave purlin (it rests on the beams) nor over a gable wall (the empena carries it); one prumo per place; under a rincão's
  apex; ≤ 1,0 along a beam where purlins run with the beams — user 2026-09-30, 2026-10-09 "the prumos are right" — confirmed
  / ours (the 2026-10-28 additions) — `estrutura_dc.py` ([SB] 66). Engine ✓; hip ends and larós X6, X10.
  **How a prumo stands (2026-10-29): turned with the beam it carries — its wide face (110) along the beam, 75 across it —
  its top cut (bevel) to the underside of the member above (purlin plane, rincão / laró line), the whole foot on the beam;
  never standing past a beam's end; a prumo under a top purlin sits on a beam (a ceiling beam right under each of the two
  top purlins of a zone)** — user 2026-10-29 "as vigas que dão a inclinação que se encontram na vertical apenas tem uma
  viga pousada a metade da sua largura e a viga nem encaixa totalmente nessa peça vertical que referia. Revê isso mais
  uma vez" — confirmed (the fault: half off the beam, the purlin on part of the prumo) / ours (the build: 75 / 110 turned
  per wing, bevelled top) — `telhado_estrutura.construir` (`prumo`, `eixo_viga`); `auditar_cobertura.py` checks every prumo
  on a beam and none past its edge (L58, L59).
- **E4 Purlins 110×75**, parallel to the ridge, **≤ 1,2 apart** in equal bays, laid flat and tilted to the slope; **the eave
  purlin on the beams right over the wall** (its outer top corner at the frame's outer face); **the top purlins of the two
  slopes meet on the ridge line, each cut to its slope (the pair is the ridge, ≈ 1 mm apart) — never straight and short of
  it** — user 2026-10-29 "junto as cumeeiras as vigas não encaixam nas cumeeiras estão simplesmente retas e próximas das
  cumeeiras o que não é suposto" — confirmed (the fault; the joint itself OPEN, E5) (superseded 2026-10-29: the top purlin
  of each slope 0,05 from the ridge line, a 0,10 gap — ours; the hidden roof on lameladas keeps its ridge madres 0,10
  apart as built at [TV], D2503, a different roof — §7 Structure); **at a lower wing's gable the purlins run on over the
  first beam under the higher body's gable (no free cantilever — they hung 0,86)** — ours; **each line one piece across the
  house, jointed over a beam** (L47), **running past
  every empena by the verge = the eave overhang** (configurator; below); every purlin ends against the side of a rincão /
  laró member cut on the skew (below), fixed with estribos (2026-10-28; product OPEN) — user
  2026-09-30, 2026-10-09 — confirmed (purlins, spacing, eave one on the beams) / assumed (flat, tilted)
  — `telhado_estrutura.construir` (the ridge pair; lower wings); JSON `cobertura.vigas_apoio`, `cobertura.empena` 0,12 (older
  models only — below). **Not the engineer's [SB] 80×160 rafters on an 80×160 frechal**
  — the drawings' structure (cfg `estrutura.sistema` "desenhos"), not the method (L9). Engine ✓; continuity and lengths X8,
  X9.
- **E5 Ridge**: no ridge beam — the two top purlins carry the panels' ends, a ridge cap (≈ 0,20 each side) over the joint,
  **folded down both slopes onto the panels ("coladas", 2026-10-28 — Covering)**; ridge height = eave purlin top + run × slope (≥ 15 %) — draft "Cumeeira (2 águas)" — company document / assumed (no ridge
  beam) — `estrutura_dc.py`, `camadas.cobertura`. **The joint of the two top purlins on the ridge is OPEN** (§15 A1): his
  "encaixam" (2026-10-29, E4) is not defined — butted and screwed, bevelled, lapped, over a ridge beam or plate; the engine
  meets them on the line, cut to the slope — ours, to confirm with a sketch (the "no ridge beam" reading is
  ours too). **Caps in the roof colour, each running 0,20 over the next at a node (Covering).** Caps ordered by count, as
  D2503 ("ENCOMENDAR 18 CUMEEIRAS") — ours. Engine
  ✓; counted in metres — X12.
- **E6 Empenas**: a framed triangle on the gable wall's amarração — bottom plate 35, sloped top plates under the purlins,
  110×75 corner posts, 110×35 studs at 40 cm clear, a stud under the ridge — user 2026-10-09 "its fine like that" —
  confirmed — `estrutura_dc.emoldurar_empena` (every gable wall; every wing end). Clad outside like the façade up to the
  panels (L5); no wool (cold attic); inside unlined — assumed ([SB] model). Engine ✓ (on an edge beam — X5; a gable over a
  lower wing — X7; inside not checked). **Nothing overlaps at the triangle's corners (2026-10-29): the empena starts past
  the eave purlin (and past a valley member's foot), is framed only where a bottom plate and a top plate fit, and where the
  frame would leave a gap under the panel a "Calço da empena" packs it on the edge beam; the panel at its full width, the
  cladding to the corner** — user 2026-10-29 "vigas a sobreporem-se umas as outras nos cantos do triângulo da empena" —
  confirmed (the fault: the eave purlin ran 3,5 cm through the bottom plate, the end members dipped into the edge beam) /
  ours (the build, the packing) — `telhado_estrutura.construir` ("Calço da empena"); `auditar_cobertura.py` checks the
  empenas' members against the roof timber (L60).
- **E7 Panels**: Munditelha (above), **one length per slope** from the eave edge (frame face + beirado) to the ridge, laid
  from one end, screwed to every purlin (Turbosharp 6×160), sealing tape between panels, remates laterais on every empena
  — draft + user 2026-10-22 — company document / confirmed — `camadas.cobertura`. Closures under the profile at eaves and
  caps — general practice — not in the tools. Engine: faces ✓; one area per face, no lengths, widths, waste or closures —
  X11.
- **E8 Gutters and downpipes**: an **exterior gutter along every eave** under the panel edge (draft "Caleira exterior e
  tubos de queda"; 125×90 assumed), falling to its outlets (general practice ≈ 0,3–0,5 %); **2 downpipes per gutter, 0,30
  from its ends** (3_Vigamento's "2 tubos de queda"; **confirmed for the company 2026-10-30 "vamos com dois tubos por
  caleira a nao ser que a caleira seja pequena" — a run ≤ 4,0 m gets one ("sim está bem")**), **and more, evenly spaced
  between, for 1 cm² of pipe per m² drained — the same rule as the hidden roof (§7 Hidden roof), with the 80 × 80 exterior
  pipe (≈ 64 cm² → 64 m² each); the spread is ours ("distribui como achares melhor", 2026-10-30, delegated)**, on the façade with a swan-neck and brackets, **ending ≈ 5 cm above the base** (user 2026-10-16 "o
  fim do tubo de queda não pode estar tapado pela base de fundação" — said on a hidden roof, for every downpipe our reading)
  — company document / confirmed (two, one on a small run) / delegated (the spread) / assumed (sizes, positions, route) —
  JSON `cobertura.caleira`; `camadas.cobertura`, `camadas.cobertura_faces` (the rule by area). **Every downpipe
  joined to its gutter** — a piece from the outlet in the gutter's bottom down and back to the pipe's top (a swan-neck) —
  user 2026-10-28 "os tubos de queda não estão conectados as caldeiras" ("caldeiras" = the gutters, our reading) —
  confirmed (the fault) / ours (the piece) — `camadas.cobertura_faces` (`ligacao`) (L54). **Outside or inside the
  cladding on an exposed roof: OPEN** (§15 C2; inside is the method on hidden roofs). Engine ✓ on every eave, laid level — X14,
  X15; drawn on the configurator's screen from the same layers (2026-10-28). **One gutter per straight run of eave, mitred
  where two runs meet at a corner — never one gutter per eave piece** — user 2026-10-29 (night) "umas caleiras todas
  bugadas" — confirmed (the fault: each eave piece its own gutter crossed the next at a corner) / ours (the build) —
  `camadas.cobertura_faces` (L67). (The 2 downpipes above count per run.)
- **E9 4 águas / hip ends** (not offered in the configurator since 2026-10-28; the build stays for the misto body and a
  project's hipped roof — PO Q14): all four walls are eave walls (afinação + amarração, no empena); with equal slopes the
  rincões run at 45°, **ridge length = L − W**, ridge height = W/2 × slope above the eaves; the hip ends' purlins on the
  beam lines, prumos ≤ 1 m (§6 (b)); a member and a cap on every rincão, bias-cut panels; a gutter on all four eaves,
  downpipes at the corners or ≥ 1 per gutter by area — ours — `telhado.py` `quatro_aguas` ✓; X5, X6, X10–X12, X15.
- **E10 L / T / U**: the cards (Exposed roof above) — "Duas águas" (`duas_aguas`: each wing 2 águas with empenas at its
  free ends, ridge along the wing, beams across it — §6 (a)); "Várias águas, com empenas" (`misto`: body hipped — E9 on its
  ends — wings gabled — E6); the engine's joins (above); every laró with its member, caleira de laró and a downpipe at its
  foot; coplanar faces' purlins continuous (L47); where a wing opens into the body the beam ends in **external-flange
  hangers on a header along the open side, wall to wall** (§6 — confirmed; its section, bearings, hangers — ours / the
  engineer's, X4) — ours / confirmed (header) — `main.js` `COBERTURAS` / `ORDEM_COB`; `telhado.py`; deviations X4, X7,
  X8, X13, X15.
- **E11 Checks to run on every exposed roof** (ours, L45–L47, L51): every eave a gutter, every outlet / laró foot a
  downpipe; every purlin borne by a prumo (or the beams) at every beam it crosses, purlins parallel to the beams on one;
  every empena framed under its purlins and clad; every face ≥ 15 %; ridge height = eave + run × slope; the laró slope ≥ the
  panel's (and caleira de laró's) minimum; every opening + box (windows only) + lintel under the module top, a raise noted
  with the opening causing it; no exterior stud split by a beam (L46); **no member through another**. **Run
  `python ferramentas/configurador/auditar_cobertura.py <casa.json>` (`--tipo`, `--pct`, `--beirado`) or `--formas` (the
  sweep: rectangle 12 × 8, three L's, a T, three U's incl. his 25 × 10; duas águas / misto; 15 % at 0,25 and 40 % at 0,40)
  after every roof change** — it reports clashes > 8 mm, purlins / rincões / larós borne every ≤ 1,30 (≤ 1,45 along a
  rincão / laró), free ends ≤ 0,75 (an end fixed to a rincão / laró side counts as borne), every prumo on a beam and none
  past a beam's edge, the empenas' members against the roof timber (both since 2026-10-29; the ridge pair meeting on the
  line is built, not checked), slope
  coverage (panels ≤ 1,30 between purlins, ≤ 0,25 short of the ridge, ≤ 0,70 past the eave purlin). ⚠ Looser than the
  rules and short of the screen's range — X19. Checked by no tool yet: gutters / pipes per eave and laró foot, empenas
  framed and clad, the laró slope vs the panel, the opening heads (X16).
