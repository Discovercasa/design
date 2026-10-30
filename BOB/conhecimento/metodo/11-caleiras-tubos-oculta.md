# Método DiscoverCasa — cobertura oculta: caleiras, saídas e tubos de queda (§7, Hidden roof) (parte de conhecimento/metodo-construtivo.md, v8.8; split from 06 in v8.8)

### Hidden roof — gutters, outlets, downpipes (cont. of `06-cobertura-oculta.md`; one água: the low side only, one gutter per low wall — there)
- **Gutters at the level of the rufos**: the water runs down the rufo slope into the gutter, then the downpipes — user
  2026-10-15 "as caleiras têm de ficar ao nível dos rufus de forma à água escoar através da inclinação dos rufus para as
  caleiras e depois para os tubos de queda" — confirmed — read after D2503 as the flashing at the panel ends, not the flat
  chapéu (our reading).
- **The gutter is the caleira oculta, INSIDE the parapet**, along the low edge of each slope, at the level of the
  underside of the rufos — user 2026-10-16 "sim é por dentro mas na zona que eu dei highlight no primeiro screenshot. fica
  por dentro e ao nível daparte de baixo dos rufus"; on v3 "isso as caleiras agora estão corretas"; draft "Caleira oculta"
  with "Cobertura oculta" — confirmed — JSON `cobertura.caleira_oculta`; `casa_planta.construir`,
  `camadas.cobertura_platibanda`. The exterior gutter belongs to exposed roofs only (L3).
- Caleira oculta, company build (draft "SE TIVER CALEIRA OCULTA"): 2 × 110×75 along the gutter ("uma trabalha ao alto e
  outra trabalha deitada"), "Quanto maior o comprimento melhor"; OSB 22 "30cm de largura em todo o comprimento e 10 cm do
  lado da cobertura"; lined with aluminium tile-colour sheet 80 cm, self-tapping screws, sealing tape, tela líquida,
  Flexiband, rivets, bocais — company document — JSON `cobertura.caleira_oculta.produto`. Our reading after D2503: the "ao
  alto" one = the gutter madre on edge, "30 … 10 cm" = the bottom and madre-side leg; where the "deitada" one goes: OPEN.
- [TV] **Caleira oculta as built** (D2503 sheets 2, 5) — company document, one house; the standard's default (PO Q16):
  **0,31 clear between the parapet frame face and the gutter madre** (the madre, 110×75 on edge, is the roof-side wall); the
  bottom on **calços on every lamelada** (0,50 long: 0,31 + 0,19 under the madre; height "VARIÁVEL") giving a **fall ≈ 2 %
  to outlets at the gutter ends** (long gutter high in the middle, outlets at both ends — north 0 → 0,17, two halves of
  8,61; shorter ones one outlet — main-block south 0 → 0,22 west, wing 0 → 0,06 east), **never closer than ≈ 4–5 cm to the
  madre's top**; **lining 0,30 bottom + 0,30 parapet side + 0,10 madre side + 0,10 flange over the madre = 0,80 = the
  draft's 80 cm sheet**; the panels ≈ 0,10 into the gutter — JSON `cobertura.caleira_oculta` (`largura` 0,31, `queda_pct`
  2,0, `folga_min` 0,04), `estrutura.madres.calco_madre` 0,19; TV cfg `cobertura.caleiras`. The lining runs up the parapet
  face to the top (Parapets, in 06): with the 80 cm sheet a second piece lapped over the 0,30 leg or a wider sheet — OPEN,
  low priority. At the main-block south gutter's high end its bottom (0,22) is above the madre's 0,15 packing — reread.
- [TV] **Site photos (2026-10-19)** — user "afixei também imagens reais de como ficou a cobertura"
  (`Construção Torres Vedras/docs/revisao-modelo/2026-10-19_obra_caleira_*.webp`): an **OSB box** along the parapet (= the
  draft's OSB 22 — our reading), a **red (tile-colour) lining**, end plate turned up, corners and outlet sealed, the **outlet
  a round hole in the gutter bottom near the end**, no overflow — our reading (not stated as rules, L14). Tools' deviation:
  no board under the lining on lameladas. **Lining colour: "Chapa cor telha"** — the draft's "painel de alumínio cor
  telha de 80 cm", red at [TV] — assumed (**RAL 8004 as the roof, 2026-10-30 — ours: he named the RAL of the panel, not of
  the lining**; to confirm, §15 E4) — JSON `cobertura.caleira_oculta.material` "Chapa cor telha" (#8F4E35) (was #A3482C
  until 2026-10-30, dark grey "Caleira" #3A3F43 until 2026-10-29).
- Caleira oculta as the tools build it **on 22×7,5 ceiling beams** (from TV v3; differs from D2503): a 110×75 flat on the
  beams, OSB 22 from the parapet face to the roof side of an upright 110×75 (30 + 7,5 cm), channel 30 wide, 110 deep on the
  longest slope, lining up the parapet frame face to 2 cm under the chapéu (only where the parapet stands ≤ 0,50 over the panels — Gutter
  walls, in 06) and up the upright, end caps, panels 5 cm in,
  channel flat — assumed — JSON `cobertura.caleira_oculta` (`largura` 0,31, `altura` 0,11). Where the flat 110×75 goes (the
  OSB's parapet edge has no bearer), an overflow: OPEN.
- Caleira interior 20 cm with 2 downpipes along one long side (3_Vigamento) — company document — not in the tools; the
  same as the caleira oculta (20 cm vs 30 in the draft vs 0,31 at TV, per project?): OPEN — **PO Q16** (default 0,31).
- **Downpipes: TWO per gutter, at its ends; ONE on a small gutter (≤ 4,0 m); more, evenly spaced between, for 1 cm² of
  pipe per m² drained; the pipe is 100 × 50 and the outlet (bocal) is the pipe's own section — inside the cladding** — user
  2026-10-30 "vamos com dois tubos por caleira a nao ser que a caleira seja pequena"; "small" = ≤ 4,0 m "sim está bem"; the
  outlet and the spread left to us "então usa o bocal ideal para esse tubo e distribui como achares melhor"; **the section
  — our suggestion of a bigger pipe (100 × 50 in a local recess instead of 7 pipes on his L) — his, 2026-10-30 later still:
  "Sim usa de 100x50"** — confirmed (two per gutter, one on a small one, the 4,0, the 100 × 50) / delegated (the bocal = the
  pipe's section; the distribution — "a nossa escolha") / general practice (1 cm² per m² drained, CM §4, SC §6) — a
  100 × 50 pipe ≈ 50 cm² serves ≈ 50 m²: a gutter > 4,0 m gets 2 at its ends, plus more between when its roof area passes
  50 m² per pipe. Our arithmetic: his L's gutter (≈ 196 m²) gets **4 pipes (it got 7 with 80 × 35)**; [TV]'s north gutter
  (≈ 74 m²) gets 2 = as built (it would have got 3 with 80 × 35; D2503, TV cfg `saidas` — a project fact, it works there).
  **It fits the standard Tremolo cavity (contra-ripado 20 + ripado 35 = 55 mm) with no recess; with a shallower cavity the
  boards behind the pipe — cork, ETICS XPS — get a local recess round it; the visible boards (Tremolo) never get a hole**:
  a cavity too shallow behind them ([TV] as built: no contra-ripado, 35 mm) needs the contra-ripado — the engine warns and
  limits the pipe to the cavity — ours (general practice: never a cut in Traspir / OSB 9 / wool); **one more reason to
  keep the contra-ripado in the standard** (§8) — JSON `cobertura.caleira_oculta.tubo` (`largura` 0,10, `profundidade`
  0,05, `m2_por_cm2` 1, `caleira_pequena` 4,0, `folga_base` 0,05); `camadas.tubos_queda` + the façade layer loop (commit
  0528d1b); `casa_planta.construir`. **Closes the section part of PO Q16** (left: the outlet's type, the overflow, the
  foot). Exposed roofs keep the exterior pipe 80 × 80 (ours, §7 E8) — he spoke of the hidden roof. (superseded 2026-10-30
  later still: "the pipe 80 × 35 ≈ 28 cm² → ≈ 28 m² each" — ours, from the cavity depth, JSON `tubo.largura` 0,08 /
  `profundidade` 0,035; earlier 2026-10-30: "the outlet (bocal) 10 cm by default, larger by the zone, the slope and the
  roof's size" — his first answer "Normalmente 10cm de bocal mas pode ser maior dependendo da zona, isso depende da
  inclinação e da dimensão da cobertura", JSON `tubo.bocal` 0,10; before it "one per 37 m² drained, ≥ 2 per gutter" —
  ours, from TV's 74 m² / 2, JSON `tubo.area_max_m2` 37 — L70; before: 2 per gutter at 0,45 from its ends until
  2026-10-29.)
- **Downpipes INSIDE the exterior cladding, hidden by the Tremolo — never inside the rooms** — from the gutter through the
  parapet into the batten cavity and down the façade — user 2026-10-16 "…não é suposto mas é suposto estarem por dentro do
  revestimento exterior mas escondidos pelo tremolo" — confirmed; **the method**, re-confirmed 2026-10-20 "pois nós nesta
  obra fizemos de forma diferente mas a forma como modelaste no blender por dentro do revestimento é a forma correta" and
  (13:25) "nós achamos que por dentro é mais correto e fica melhor" — confirmed (preference) — `camadas.tubos_queda`,
  `camadas.cobertura_platibanda`. [TV] **as built: outside the cladding** (finished photos — SE and NE corners with box heads,
  the face beside the garage; TV #9) — a project fact (L40). How the pipe leaves the gutter: next lines. As the tools
  place them: at cfg outlets, else two per gutter near its ends, one on a gutter ≤ 4,0 m, more evenly between by area
  (above; was one per 37 m² until 2026-10-30, a flat 2 per gutter 0,45 from its ends until 2026-10-29), ≥ 0,15 clear of
  openings; section **100 × 50** (above; was 80 × 35 earlier on 2026-10-30, before 80 mm × the cavity depth: [TV] ≈ 33; ≈ 53
  with the contra-ripado); a horizontal piece through the parapet just above the gutter bottom; battens stop at the pipe —
  assumed — JSON `cobertura.caleira_oculta.tubo`. **Conditions that make the inside route work** (general practice, our
  advice 2026-10-20 13:25; CM §4, SC §6): (a) size the pipes for the roof (1 cm² per m²: the 100 × 50 pipe ≈ 50 cm² serves
  ≈ 50 m², more pipes evenly spaced on a big roof; [TV]'s ≈ 37–46 m² per pipe is within it; the standard cavity takes the
  pipe, a shallower one a local recess in the cork / XPS boards only — never a cut in Traspir / OSB 9 / wool); (b) one
  continuous pipe or sealed joints, a sealed bocal and collar at the parapet, Traspir taped round; (c) an inspection point
  at the top, a leaf guard at each bocal; (d) an overflow at every hidden gutter; (e) the foot into the drain or a gully —
  the company's foot and overflow: OPEN, **PO Q16** — not in the tools.
- **Downpipes end slightly above the foundation base**, never covered by it — user 2026-10-16 "o fim do tubo de queda não
  pode estar tapado pela base de fundação tem de estar ligeiramente acima para a água poder sair do tubo de queda" —
  confirmed (5 cm assumed) — JSON `cobertura.caleira_oculta.tubo.folga_base` 0,05. Where the water goes then: OPEN — **PO
  Q16**. ⚠ A shoe throwing it ≥ ≈ 0,3 m onto a splash block / gravel, or a gully — general practice (TV #9, #16).
- **Downpipes at the gutter outlets — the low ends of each gutter's fall** ([TV] 4: north 2, main-block south 1 west, wing
  1 east), ending 5 cm above the base — user 2026-10-16 (night) "como esta desenhado está perfeito" — confirmed (the method,
  not TV as built — L40) — TV cfg `cobertura.caleiras.*.saidas`; `casa_planta.construir` (outlets ≥ 0,10 clear of openings).
- **Every hidden gutter has an outlet hole in its lining at each downpipe, at a low end, the pipe inside the gutter's
  length; a downpipe without its hole is a model error** — user 2026-10-20 (≈ 13:51) "um erro que esta presente é nas
  caleiras nao existem os buracos par agua escoar para os tubos de queda"; **asked again 2026-10-29** "estão em falta os
  buracos para os tubos de queda" (the second time) — confirmed / assumed (at the low ends, inside the
  length; **since 2026-10-29 the hole is in the gutter's BOTTOM, round as [TV]'s photos, against the parapet over each
  downpipe — visible from above — feeding the downpipe; its bocal the pipe's own section, 100 × 50 since 2026-10-30 later
  still (was 80 × 35, and 10 cm before), above**; before, a
  0,08 × 0,06 hole in the parapet-side plate, unseen from above) — `camadas.tubos_queda` (`furo_z`; with cfg `saidas` the pipe
  clamped inside the gutter), `camadas.cobertura_platibanda` (lining cut round each hole) (L43, L62). ⚠ Without
  cfg `saidas` the fallback is placed by the ends, not the falls. Validation wanted: every downpipe meets a hole at a low
  end, every low end has a downpipe. Not in the tools: sleeve, leaf guard, overflow.
- **Which gutter outlet — a round hole in the gutter bottom ([TV] as built; what the tools draw since 2026-10-29, with a
  bocal and a short stub through the parapet into the façade cavity — ours) or sideways through the parapet (the tools'
  default before): its type and fitting still OPEN, promised** ("isso depois eu digo a informação não sei
  neste momento", 2026-10-20 night) — **the bocal's size is answered: the pipe's own section, 100 × 50 ("usa o bocal ideal
  para esse tubo", then "Sim usa de 100x50", 2026-10-30; Downpipes above)** — **PO Q16**, §15 E5; flag "a confirmar" in
  deliveries — JSON `cobertura.caleira_oculta.tubo`,
  `camadas.tubos_queda` (side only). General practice: a side outlet keeps joints out of the roof void but crosses the
  parapet module → a pre-formed outlet sealed to the lining, a sealed sleeve falling outward, Traspir taped, studs set clear
  (§0a); a bottom outlet drops into the void and must turn through the wall (unseen joints); either way a leaf guard and an
  overflow.
- **Overflow (ladrão)**: through the parapet near each outlet and at the high end, below the gutter's lowest rim, spilling
  where it is seen — general practice (CM §4, SC §6, TV #4 g, #15); [TV] the madre side at the high end only ≈ 4–5 cm above
  the bottom. Asked 2026-10-20 night — user "explica-me o que é um ladrao mas penso que não" → **tentatively none**
  (agrees with D2503 and the photos); explained and recommended, **his answer after the explanation pending** — not in the
  tools; flag **"sem ladrão no modelo"** in every delivery (PO Q16, §15 E5).
