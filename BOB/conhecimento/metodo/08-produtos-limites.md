# Método DiscoverCasa — produtos, consumíveis e vãos/limites usados (§11, §12, §13) (parte de conhecimento/metodo-construtivo.md, v8.3)

## 11. Products, brands, purchase units and waste
- Structural and site timber: casquinha branca (*Picea abies*), solid; glulam where exposed, at a porch or past 8 m —
  draft, 3_Vigamento, D2503 — company document — JSON `materiais`; purchase lengths not computed.
- **Glulam lameladas 20×10** (grade not given; GL24h in our checks): **cut to fit each house** (§4) — [TV] from stock 13,5
  m → 8,50 (≈ 5 m waste each, × 11 ≈ 1,1 m³) and 12 m → 11,00 (1 m, × 7) — D2503 sheet 1 — company document. The material
  list should give each beam's cut length, the stock length and the offcut — ours, not in the tools
  (`documentos/dados.py` lists modelled lengths). ⚠ Order lengths per house to cut the waste ([TV] 2 × 8,28 from a 17 m
  stock), or glulam made to length — suggestion (TV #12, `insights.md`). The 22×7,5 too; the longest stock bought: OPEN.
- Madres 110×75: pieces ≤ 3,66 (4 bays of 0,915; one stock length — ours) jointed on a lamelada — D2503 sheet 3 —
  counted as pieces by `casa_planta`.
- OSB3 9 and 15 mm: sheet 2500×1250, waste 10 % (assumed) — JSON `exterior.osb`, `interior.osb`. OSB 22: sheet not given.
- Traspir 95: roll 1,5 × 50 m = 75 m², 65 m² useful with 20 cm laps, waste 5 % (assumed) — JSON `exterior.membrana`.
- Tremolo: board 4,0 m, waste 10 % (assumed) — JSON `exterior.opcoes.A.forro`.
- Ripado: bought as 75×35 and ripped in two — user 2026-10-15 "dividimos essas vigas em duas pela vertical" — confirmed —
  metres only (purchase = metres ÷ 2 of 75×35 in stock lengths — not given, not in the tools).
- Module timber: D2503 Módulos gives a cut list per house ([TV] 11×3,5 220 pcs / 473,0 m; 11×7,5 50 / 139,0; 7,5×3,5 199 /
  379,1; 7,5×11 24 / 46,3; studs 3,43 ext / 2,46 int) — company document — the model gives pieces and metres per section;
  stock lengths and the cutting plan not computed. By volume ≈ the draft's 40 / 40 / 20 (§2).
- Contra-ripado 30×20 and cork battens: product, length, purchase unit — OPEN — metres only.
- Pladur N / H1 / F 13: board 1200×2600 (assumed), waste 10 % (assumed) — JSON. ⚠ Walls floor to ceiling = the pé direito:
  past 2,60 longer boards (2,70 / 2,80 / 3,00 — supplier) or a joint backed by the OSB 15 — ours; the tools count boards by
  area (fine while offcuts are reused).
- Volcalis COMFORT rolls (λ 0,037; widths 400 / 600) — product data — no purchase unit in the tools.
- Cantoneira 30×30×0,5: bars of 3 m from the perimeter — confirmed — JSON `tetos.cantoneira` (waste 0; SC "plus cutting
  waste"). Perfis and réguas: model and bar length OPEN.
- Vinyl waste 8 %, XPS 5 %, cork 8 % — assumed — JSON.
- **Sandwich panels** 1 m useful, ordered as a count per slope length and the ridge caps by count ([TV] 28–29 × 3,94 + 7 ×
  6,44, the strip and the L-cut panel cut from them; "ENCOMENDAR 18 CUMEEIRAS") — D2503 sheet 4 — company document — the
  tools count panels on hidden roofs, give the caps in metres. Exposed: **Munditelha** (§7) — one area per face, no count ×
  length (X11).
- **External-flange joist hangers ("estribo de asa externa")** where a beam end has no wall under it, one per beam end,
  sized to the beam (75 / 100 wide), the maker's fixings in every hole — user 2026-10-22 — confirmed (the connector; Esteba
  is his photo's brand, not said as the supplier); **on a header along the open side** (user 2026-10-28 — §6) — a purchase
  line too (section ours / engineer's) — hangers and end posts not modelled or counted (X4). **Purlin ends at a rincão /
  laró: estribos too** (user 2026-10-28 "estribos." — §7) — the product (skewed / sloped) OPEN; not counted (X9).
- Interior finishes (wood, ceramic, others): the list promised (§9) — JSON `interior.acabamento_opcoes` /
  `pavimentos.acabamento_opcoes` assumed meanwhile.
- Chapéus, gutters, downpipes, ridge caps: lengths only — assumed — `camadas.cobertura*`, `camadas.chapeus`. Caleira oculta:
  aluminium tile-colour sheet "de 80 cm" (draft; [TV] photo red) = the D2503 lining 0,80 developed, counted in metres of
  gutter; timber = calços (pieces) on lameladas, the box 2 × 110×75 + OSB 22 on 22×7,5. The downpipe product: section
  **100 × 50** (hidden — his, 2026-10-30 later still); material, bar length: OPEN.
- **Caixilharia**: bought per item of the approved table (type, L × A, quantity, protection, glass, side; [TV] 11 items,
  31,06 m², 6 motorised shutters) in the company standard for now (§3); the order, not the table, gives the frames (the
  table tentatively frames without clearance, not always the element built) — TV cfg `camadas.caixilharia.itens`; the
  model counts items and m² per collection ([TV] 7.1 frames 11 / 31,1; 7.2 glass 8 / 20,7; 7.3 shutters 6 / 19,4; 7.4 doors
  and garage 3 / 10,3); the maker, frame and box sizes, sills, flashings: OPEN. ⚠ The door panels take the material
  "Portão seccionado RAL 7016" (JSON `caixilharia.material_portas`).
- **Remates**: counted as metres of rough-opening perimeter — windows 4 sides, floor-level openings 3 ([TV] 11 openings,
  59,7 m outside = inside, collections 7.5 / 7.6) — `camadas.caixilharia()`. Product, colour, thickness, developed width,
  bar length: OPEN (folded aluminium RAL 7016 2 mm, inside Pladur 13 assumed). For purchase (ours): the developed width per
  opening, the sills with drip separate ([TV] 5 windows ≈ 4,5 m), folded lengths ≈ 3–6 m, thresholds.
- [TV] **Pergola**: glulam with autoclave (+ an exterior treatment, name OPEN); 160×160 / 160×75 / 70×30 tentative; v6.3 ≈
  2,45 m³ (posts 6, front beam and beams 160×160 18 pcs 64,7 m 1,65 m³; ledgers 160×75 2 pcs 13,9 m 0,17 m³; slats 70×30
  301,8 m 0,63 m³) + ceramic tiles 46,4 m² + gutter + 2 downpipes 18,9 m — TV `materiais.md`; inside TV "TOTAL madeira"
  12,86 m³. ⚠ Ceramic tiles are bought by the piece (≈ 10–13 per m² Lusa / Marselha) plus ridge / verge / eaves pieces and
  battens — the model gives m²; the pergola glulam would be clearer on its own line — ours.
- Fixings: Turbosharp 6×70 / 6×140 / 6×160 (modules), 6×160 (roof panels), 70 / 160 / 200 (start), 4×50 (cladding); 45 mm
  drywall screws (OSB, ripado); M10 (modules to base); galvanised staples (Traspir) — draft — company document — not in the
  tools.
- Prices: a list of materials and suppliers "futuramente" — OPEN (`discovercasa.md` Product vision 2) — transport / site
  assembly per house to include (§2).

## 12. Site consumables (start of construction)
- M10 bolts (2–3 per module), 45 mm drywall screws, Turbosharp 70 / 160 / 200, Traspir 95 = exterior wall area (20 cm
  laps), galvanised staples, alcatrão, brocas and brocas PUA, tico-tico and sabre-saw blades, T25 bits — draft "INÍCIO DE
  CONSTRUÇÃO" — company document — not in the tools.
- Hidden-gutter consumables: tela líquida, Flexiband, rivets, bocais (one per outlet hole — [TV] 4), sealing tape;
  "Capeamento de rufos e Tubo de escoamento" — draft — company document — named in JSON
  `cobertura.caleira_oculta.produto`, not counted in the Listagem (its footer says so).

## 13. Spans and limits the company uses
Each line points to the rule's home section.
- **Ceiling beams 22×7,5 at 1 m: up to 8 m span** — user 2026-10-15 "O nosso limite é precisamente 8 metros portanto
  tranquilo, nós sabemos que assim não irá ceder" — confirmed (given on TV v1; TV was built in glulam) — no check in the
  tools (§6). Whether 8 m is also the longest piece bought: OPEN. ⚠ Rough EC5 check (TV #6): bending ≈ 0,96 f_m,d,
  long-term sag w_fin ≈ 82 mm (L/98) vs L/250 = 32 mm; with the ridge at mid-span it flattens a low slope → engineer above
  ≈ 6 m free span; options from 3_Vigamento: 0,50 spacing, doubled, glulam — general practice.
- **Past 8 m: glulam lameladas 20×10 in equal bays ≤ 0,92**, cut to fit, bearing on the interior modules (§4, §6). ⚠ Rough
  EC5 check (GL24h, SC1, k_def 0,6, G ≈ 0,37 kN/m, Q roof H 0,4 kN/m²): ≈ 8,2 m clear — bending ≈ 0,7 f_m,d, w_fin ≈ 45 mm
  (G, L/180) / ≈ 73 mm (with Q, L/112) vs L/250 ≈ 33 mm, slope near the gutters 6 → ≈ 4 % in time; 11 m unsupported —
  bending ≈ 1,15 f_m,d, w_fin ≈ 0,13 m → it must bear on a wall (it does); the ring's screws ≈ 4–5 kN per end → engineer
  per house; deeper glulam (24×10 ≈ 1,7× stiffer) or closer beams past ≈ 7 m — general practice (TV #6).
- Floor joists 220×75: 0,614 for ≈ 4,9 m with an interior wall below; 0,50 for ≈ 4,8 m free — 3_Vigamento — engineer per
  house (SB #6) — JSON 0,615 only (§5). Barrotes 0,60 → OSB 22 ≈ 0,49 m clear (≤ ≈ 0,6 m) — general practice — closed.
- Purlins 110×75 ≤ 1,2 ([SB]; 3_Vigamento 0,89); madres 110×75 on edge ≤ 1,265 under the 5-rib 80 mm panel ([TV]) — §7.
- **Exposed-roof timber bearings** (ours, 2026-10-28): a purlin on a prumo at every beam (≤ 1,0 apart, ≤ 0,92 on glulam);
  a purlin running with the beams on prumos ≤ 1,0 along its beam; a rincão / laró crossing the beams at 45° every
  ≤ ≈ 1,41; a rincão / laró foot cantilevers ≈ beirado × √2 (≈ 0,71 at the 0,50 maximum); purlin ends on the rincão /
  laró in estribos (confirmed); the audit allows 1,30 / 1,45, free ends 0,75 — looser (X19). Panel cantilever past the
  eave purlin = the beirado → Munditelha's table (OPEN).
- **Header ("viga de bordadura") where a wing opens into the body** (§6): section and span not given — ours (explained to
  him 2026-10-28, his reply OPEN): ≥ the beams' depth (the engine's 200×100 is 2 cm shallower than 220) and ≥ the hanger;
  posts under its ends, no module joint there; past ≈ 4 m of opening → engineer (X4). The encosto header 220×100 (X7):
  not a standard section, not sized.
- Caleira oculta: fall ≈ 2 %, bottom never closer than ≈ 4–5 cm to the madre's top, 0,31 clear ([TV]) — §7.
- **Verga 220×75 from ≈ 2,8–3 m** (over 3 m confirmed; threshold OPEN; JSON 2,8), the norm in every module; widest seen
  4,52 (Casa CL M007); upper limit OPEN; [TV] 11×7,5 at 3,00 engineer-approved — §3.
- **Modules**: factory normally ≤ 3 m, exterior up to 3 m, interior 2,75 (ours), 5 m done once; bigger ones site-built,
  as short as the opening needs by default (PO Q6); pier ≥ 0,32; smallest 0,60 (ours); plain 2,21 / 1,78 / 2,65 (5 / 4 / 6
  bays); [TV] factory ≤ ≈ 2,64 / 2,72, M1 3,82 site-built — §2. JSON `estrutura.divisor` (`comprimento_max` 3,0,
  `comprimento_preferido` 3,0 / 2,75, `pilar_min` 0,32, `comprimento_min` 0,60).
- **Panels' slopes**: exposed ≥ 15 % (≈ 8,5°; JSON `cobertura.inclinacao_min_avista_pct` 15), the client's look above, our
  default 15 %, the configurator to 100 %; ridge + 0,15 per metre of run at 15 %; larós / rincões = face ÷ √2 (≈ 10,6 %);
  tile-effect generic ≥ 10 % (Munditelha's own: OPEN); 5-rib ≈ 5–7 % (≈ 3 % some single-length); hidden roofs the panel's
  minimum ([TV] 6 %) — §7. **Hidden-roof panel in one length ≤ 15 m** (user 2026-10-30 "afinal o máximo do painel é 15
  metros"; was 13,5 ours; length "váriavel", 1 m wide, panels interlock; the MC 1000/5 sheet,
  `conhecimento/fontes/ficha_MC_1000-5_PUR_PIR.pdf`: lap 300 mm, supports ≤ 1,50 m, cut cold and treat the ends, not for
  marine air — it states no maximum length; **80 mm confirmed, "usamos os de 80mm", and the 15 m's transport / movement
  accepted, "Sim tranquilo", 2026-10-30 later still**; the coating for marine air: checked for TV, per house) — the limit between one água and two (JSON
  `cobertura.painel_oculto.comprimento_max` 15) — §7. **Panel colour: RAL 8004, the tile colour** — Munditelha and
  the hidden 5-ondas, flashings too (JSON `materiais`; user 2026-10-30; [SB]'s grey is Sobral's only) — §7.
- **Exposed-roof overhangs**: beirado 0,25 default, 0,20–0,50, lower per house if a model shows a problem (JSON
  `beirado_min` / `beirado_max`; was 0,55 until 2026-10-28); verge = the eave's overhang in the configurator (user
  2026-10-29 night, eaves and verges must meet — §7; 0,12 kept for older models, §15 B3). A tiled pergola: clay ≥ ≈ 30 % (lower only over a continuous
  sub-roof), tile-effect panel ≥ 10 % — general practice (§8).
- **Caixilharia clearance 2,5 cm each side and in height** by default, "nem sempre" — rough opening = frame + 0,05 wide,
  + 0,025 head + 0,025 under a window (none under a door — assumed) + the maker's box — §3, PO Q11.
- **Downpipes (every gutter, hidden or exposed): at least TWO per gutter, ONE on a small one (hidden: ≤ 4,0 m, ours),
  more evenly between when the area drained passes 1 cm² of pipe per m²** (**hidden 100 × 50 ≈ 50 m² each — his**, exposed
  80 × 80 ≈ 64 m², ours); **the outlet (bocal) is the pipe's own section** — user 2026-10-30 "vamos com dois tubos por
  caleira a nao ser que a caleira seja pequena", then "usa o bocal ideal para esse tubo e distribui como achares melhor",
  then (later still) **"Sim usa de 100x50"** (the count by area: ours, to confirm — his L's ≈ 196 m² gutter gets 4, [TV]'s
  74 m² gutter 2 = as built) — JSON `caleira_oculta.tubo` (`largura` 0,10, `profundidade` 0,05, `m2_por_cm2` 1,
  `caleira_pequena` 4,0), `caleira.tubo` 0,08 — §7 (11). (superseded 2026-10-30 later still: the 80 × 35 pipe ≈ 28 m²
  each — ours, from the cavity; the bocal 10 cm; before that "one per 37 m² drained, ≥ 2 per gutter" — ours, from [TV]'s 2
  for ≈ 74 m².)
- **Pergola** (step 7, ours / TV's tentative sections): posts 160×160 ≤ 3,5 apart, beams 160×160 ≤ 1,40, slats 70×30 at
  0,15, highest point ≤ the top of the ground floor (ceiling beams' top — ours; user 2026-10-30; was beams' underside ≤ ring
  top + 0,10) (min 2,20), projection 1,50–5,00, width ≥ 1,50, 5 % fall — §8, JSON `pergola`.
- **Downpipes**: 2 per gutter (3_Vigamento, one roof); [TV] one at each low end of a fall (4 for 3 gutters, ≈ 37–46 m² per
  outlet), each with its outlet hole (§7); sizing rule of thumb ≈ 1 cm² per m² (general practice; DR 23/95, EN 12056-3)
  → the tools' 80 × the cavity (≈ 26 cm² at TV) too small; **since 2026-10-30 (later still) his 100 × 50 pipe (≈ 50 cm²),
  with more pipes by area (above) — the section answered (PO Q16 left: outlet type, overflow, foot)**. [TV] pergola: 2 for
  ≈ 46 m². **One água: one gutter for the whole roof** → the pipes carry its whole area (100 × 50 ≈ 50 m² each: more than
  two on a long one) and an overflow — ours, to tell (§7).
- [SB] Upper-floor clear height 2,40 = RGEU minimum: keep it — user 2026-10-09 "keep it but note it" — confirmed (SB #21).
- **Pé direito**: the client's, any value; 2,40 / 2,50 / 2,60 usual; [cfgr] 2,40 (RGEU DL 38 382/1951 art. 65.º — 2,20 in WC
  / corridors / storage, one height per house here; check the current text, CM §3) to a 3,50 guard (ours), default 2,50
  (TV, ours) — §2. A 2,20 janela de correr + estore fits 2,40 (box 20 cm); under an exposed roof the modules rise for it
  (+ 0,164; 4-leaf ≈ + 0,31; ceiling drop ≈ 0,19 / ≈ 0,34) — §3.
