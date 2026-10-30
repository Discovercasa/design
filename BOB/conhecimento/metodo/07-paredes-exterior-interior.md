# Método DiscoverCasa — paredes exteriores e interiores (§8, §9) (parte de conhecimento/metodo-construtivo.md, v8.3)

## 8. Exterior walls, outside
- **OSB3 9 mm all round** (2500×1250), 45 mm drywall screws — user 2026-09-24 "OSB 9mm all around the house"; draft —
  confirmed — JSON `exterior.osb`.
- **Rothoblaas TRASPIR 95** round the OSB (walls), laps 20 cm, galvanised staples — user 2026-09-24; draft "sobrepõem
  20cm" — confirmed — JSON `exterior.membrana`. ⚠ [TV] site photos: a **HOLZ TECHNIC** membrane on the walls (printed
  "TRASPIR HOUSE 95", "CE EN 13859-1/2" — a Traspir-family 95 g/m², our reading) and rothoblaas only on the top band —
  which product, why two, how they lap: OPEN (TV #18); the tools count Traspir 95 only.
- **Finish = the client's choice**: the three done most — **A wood, B ETICS, C cork**; others on request (stone) — user
  2026-09-24 — confirmed — JSON `exterior.opcoes`, `opcao_visivel` ([SB] B, [TV] A). Per house, with or without the
  contra-ripado: **PO Q18**. The finish covers the whole house, parapets' roof side included (§7 Parapets; user 2026-10-28
  "o capoto tem que ficar na casa toda").
- **A. Wood: Piveteau TREMOLO Douglas vertical** (class 3.2 "marron", T&G 22 × 135 useful × 4 m) — user 2026-10-15
  "Tremolo fica na vertical como é o nosso padrão" — confirmed — JSON `exterior.opcoes.A.forro`. ⚠ On a hidden roof the
  boards run the full-height module (≈ pé direito + 1,0) → past ≈ 2,9–3,0 of pé direito a horizontal joint with a drip /
  flashing — ours / general practice (CM §2); how the company joins Tremolo in height: not asked; the tools cut at 4 m
  from the bottom.
- **A and C: never on the membrane — two crossed batten layers ("slatted against slatted") make a breathable cavity** —
  user 2026-09-24 "we don´t apply it direclty onto the tela tyveck we do a slatted against slatted with 30x20mm and the apply
  it onto the slatted against slatted so the zone between tgem is a breathable zone" — confirmed — JSON
  `exterior.opcoes.A` / `.C` (contra_ripado + ripado) (L15).
- **A. Contra-ripado vertical 30×20 at 0,35** against the Traspir — section user 2026-09-24 ("30x20mm"), spacing the draft's
  ("Casquinha branca 2*3 … 35 / 35 cm") — assumed (section and spacing to confirm) — JSON `exterior.opcoes.A.contra_ripado`.
  ⚠ At 0,35 from the façade end they miss the studs (≈ 0,435) → lay them on the stud lines — general practice (CM §2).
- **A. Ripado horizontal 37,5×35** (a 75×35 ripped in two), on the contra-ripado — user 2026-10-15 "o 3,75x3,5 é o nosso
  padrão" — confirmed — **laid from the bottom up, every 35 cm** — user 2026-10-16 (night) "O ripado deve ser aplicado de
  35 em 35 cm. Como podes ver na foto real da obra o ripado é aplicado de baixo para cima e depois de 35 em 35 cm" —
  confirmed (centres or clear: OPEN; the tools lay 0,35 centres from the bottom) — JSON `exterior.opcoes.A.ripado`
  (`espacamento` 0,35); `camadas.dispor`. (was 0,50, "O espaçamento do ripado é de 50 cm" 2026-10-15, until 2026-10-16
  night — L31.)
- [TV] **No contra-ripado** (ripado straight on the Traspir) — user 2026-10-15 "Nesta casa só levou ripado na horizontal e
  não levou o contra-ripado" — confirmed, TV only — TV cfg `camadas.exterior.opcoes.A`. Why, and when other houses go
  without: OPEN. ⚠ Horizontal battens alone under vertical boards close the cavity into bays (no air rise, water on the
  batten tops) → contra-ripado or gapped battens; at TV check the cavity open top and bottom with mesh — general practice
  (CM §2, TV #3). The photo's narrow "ladders" of battens (downpipe runs?): OPEN (TV #9).
- **A. The battens go round every opening on all sides except the side touching the floor**: jambs + head always; a window
  not reaching the floor gets a horizontal batten above AND below; doors, janelas de correr to the floor and the garage door
  jambs + head — user 2026-10-16 "o ripado nos vãos tem sempre de contornar os vãos"; (night) "todos os vão são rodeados por
  ripado tirando quando estao em contacto com o chão"; draft "Perímetro dos vãos exteriores" — confirmed — JSON
  `exterior.opcoes.A.ripado.contorno_vaos` (`ombreiras`, `padieira`, `peitoril` true); `camadas.dispor` (L22, L31). Option C
  (cork) has no `contorno_vaos` yet (heads and sills only) — whether "todos os vãos" covers cork: OPEN. A head flashing with
  a drip over every opening — general practice (TV #14).
- **A. A vertical batten at every exterior corner, on both faces** — user 2026-10-16 (night) "os cantos exteriores também
  levam um ripado na vertical em todos os cantos de ambos os lados"; draft "Cantos" — confirmed (also without a
  contra-ripado) — JSON `contorno_vaos.cantos` true; `camadas.dispor`. ⚠ With a contra-ripado the tools put corner and jamb
  verticals in both layers — whether the outer layer needs them: ours, to check.
- A. Leave 10–20 mm gaps (or notches) where horizontal battens meet vertical ones (corners, jambs, head / sill ends) so the
  cavity drains and breathes — general practice (CM §2, TV #3), a suggestion — not in the tools.
- A. Cladding screws Turbosharp 4×50 torx; battens with 45 mm drywall screws; finish wax nº 55 + Velatura Nogueira
  (Froschemie) — draft — company document — not in the tools. Battens use class 3 → treated, cut faces treated; ripping
  leaves ≈ 36 × 35; Tremolo end joints on one 35 mm batten leave ≈ 17 mm per board → stagger or double the batten —
  general practice (TV #3); the tools cut the boards at 4 m from the bottom (joints in line).
- **B. ETICS (capoto)**: XPS (thickness from the thermal project; [SB] ≈ 60), plate fixings, mesh, corner beads, base coat,
  white finish — user 2026-09-24; draft — confirmed — JSON `exterior.opcoes.B` (XPS 60, boards 1250×600, render 6 mm —
  assumed). On the whole house, parapets included (user 2026-10-28, §7). ⚠ XPS outside is tighter to vapour than the inside
  → a Glaser check or a vapour-open board (SC §3 B, SB #19) — OPEN.
- **C. Cork 60 mm 1000×500** (e.g. Amorim MDFachada) on battens + counter-battens 30×20, ventilated, not glued — user
  2026-09-24 — confirmed — JSON `exterior.opcoes.C` (both layers 30×20 at 0,35; whether option A's 37,5×35 applies: OPEN).

### Attached to the façade (pergolas)
- **Per project**: whether a house has a pergola, its extent, covering (slats / tiles / panel), slope, gutter and
  downpipes, sections, treatment and fixing — **PO Q21**; the fixing to the house varies and he gives it when it matters —
  user 2026-10-19 (18:12) "nem sempre usamos esse método quando for relevante nas pérgolas eu dou-te essa informação" —
  confirmed (a promise) — no JSON default (cfg `pergola`).
- [TV] **A separate structure** — beams on a front beam on posts and, at the house, on a **ledger (viga de encosto) screwed
  to the façade over the horizontal battens** (the Tremolo cut round it) — user 2026-10-19 (18:12) "neste caso a pérgola foi
  feita independentemente tal como na ultima foto que anexei", "neste caso acho que foi aparafusado" — confirmed (separate;
  ledger over the battens = the photo) / tentative (screwed) — TV cfg `pergola.viga_encosto`; `casa_planta.py` 1.10.
  Whether every pergola is a separate structure: not said ("neste caso").
- [TV] **Pergola wood: glulam (lameladas) with autoclave treatment, plus a special exterior treatment whose name he does not
  remember** — user 2026-10-19 (18:12) "tratamento autoclave e são lameladas como estão no exterior levam um tratamento
  especial não me relembro do nome" — confirmed (glulam, autoclave; "como estão no exterior" may be general — our reading)
  / OPEN (the treatment's name; ask the supplier the treatment and use class, EN 335 class 3 — general practice) — TV cfg
  `pergola.produto`.
- [TV] **As finished** (photos of the finished house 2026-10-20, `…/revisao-modelo/2026-10-20_final_1…4_*.webp`): **from
  just east of the garage (x 3,63, the garage door uncovered) to the east end (x 17,57)**, **ceramic tiles** ("É cerâmica"),
  an exposed gutter along the front with **2 downpipes** ("Um no lado oposto ao que se vê na foto" — the wing's west face
  post with a goose-neck and the east corner post, our reading), **6 posts**, a timber deck under it (not modelled — PO
  Q22) — user 2026-10-20, 13:25 — confirmed / our reading of the photos (L39) — TV cfg `pergola` (`x0` 3,63, `telha`,
  `caleira`); `casa_planta.py` 1.10, `camadas.pergola_cobertura` (v6.3: ceramic 46,4 m², gutter + 2 downpipes 18,9 m).
  Height right ("a altura está ótima": beams 2,45–2,61); sections tentative ("as medidas não sei ao certo mas parecem estar
  ótimas"): posts, front beam and beams 16×16, ledger 7,5×16, slats 7×3 at 0,15 — ≈ 2,45 m³ in v6.3. **OPEN** (TV #21,
  #22): the slope and what is under the tiles (ceramic normally ≥ ≈ 30 %; the façade leaves ≈ 18 % in front of P03 → a
  continuous sub-roof, or another slope; model 15 % assumed), the tile battens (at the tile's gauge ≈ 0,3–0,4, not the
  slats), the gutter section (12×10 assumed), where the 2 downpipes discharge (≈ 23 m² each — ø80 enough; never onto the
  deck by the wall), the post bases (posts from Z 0 in the model), clay ≈ 0,4–0,6 kN/m² on 16×16 at 1,40 → engineer.
- Attached pergolas — **general practice, not company rules** (CM §4; TV #21, #22): posts use class 3–4, treated, on steel
  bases keeping end grain ≥ ≈ 150 mm up, capped ends; a pergola on the ground bolted to the house is a **termite bridge** →
  a gap or brackets, inspection; the ledger is a water trap → stand-offs through the cladding, every fixing through the
  Traspir sealed, a flashing above, bolts into solid framing ([TV] the ring 2,543–2,653, studs, jambs) — never into OSB or
  battens nor over a lintel not designed for it; or its own posts at the façade too; a covered (tiled) pergola is an
  alpendre — the covering fixes the minimum slope (clay ≥ ≈ 30 %, tile-effect panel ≥ 10 %), heavier and lifted by wind →
  engineer; an abutment flashing up behind the Traspir; the gutter with a fall, sized for its area (DR 23/95, EN 12056-3),
  its foot into the drain; a covered roof beyond a licensed pergola → telas finais / area limits — not in the tools.

### Pergolas, garages and annexes in the configurator (step 7, after the openings — user 2026-10-29)
[cfgr] scope: the client's menu "Pérgolas e Garagens e Espaços exteriores que seja necessário construção por exemplo um
anexo" (`src/exteriores.js`, engine `ferramentas/modelo/pergola.py` + `exteriores.combinar`, JSON `pergola`; spec §11 step 7).
The [TV] pergola above stays a project fact; these are the product's rules, built like it where said.
- **Pergola: the client picks the wall and the width along it, snapping to the exterior cladding ("forro exterior")** —
  user 2026-10-29 "o cliente deve poder escolher a largura e onde quer colocar a pérgola dando snap para o sítio no forro
  exterior" — confirmed — width ≥ 1,50 and projection 1,50–5,00 (ours) — JSON `pergola.largura_min`, `projecao`.
- **Pergola height: its highest point may reach the top of the ground floor (PISO 0 / piso térreo); on a two-storey house
  it may line up with the ground floor's maximum height** — user 2026-10-29 "a altura tem de ter um máximo como sabes";
  2026-10-30 "A pérgola pode ir até há altura máxima do PISO 0 ou seja do PISO TÉRREO, se existirem casas de dois andares o
  ponto mais alto da pérgola pode ficar alinhado com a altura máxima desse piso térreo" — confirmed (the rule) / **assumed
  (ours): "the ground floor's top" = the top of the ground floor's ceiling beams** — minimum 2,20 (ours), **lower under an
  exposed roof: clear of the eave and its gutter** (ours) — JSON `pergola.maximo`, `altura_min` 2,2; `pergola.py`
  `maximo()`. (superseded 2026-10-30: "the beams' underside at the façade ≤ the wall ring's top + 0,10", JSON
  `acima_do_anel` — ours, from [TV]'s ledger top 2,75 on a ring top 2,653, "a altura está ótima" 2026-10-19; compare when
  rebuilt.) Closes §15 item 22's height.
- **Pergola build — TV's, sections tentative**: posts 160×160 ≤ 3,5 apart; front beam 160×160; **ledger (viga de encosto)
  160×75 screwed to the wall's framing over the battens, the cladding cut round it**; beams 160×160 ≤ 1,40; slats 70×30
  at 0,15; **5 % fall to the front** (ours); glulam, autoclave treatment — user 2026-10-19/20 "as medidas não sei ao certo
  mas parecem estar ótimas" — tentative (TV's sections) / assumed (spacings, the fall) — JSON `pergola` (`pilar`,
  `viga_frontal`, `viga_encosto`, `vigas`, `ripas`, `inclinacao` 0,05); `pergola.py` `construir()`. Slatted only; **a covered
  pergola (telha as TV / sandwich panel): OPEN** (§15; TV's tiled one: the lines above).
- **Each post on a galvanised steel base, the timber ≥ 15 cm off the ground** — general practice (CM §4), not a company
  rule — assumed (ours) — JSON `pergola.base_pilar` (100 mm base, "Aço galvanizado").
- **Garage / annex: the client gives the m², the roof, and attached or separate** — user 2026-10-29 "Garagens deve indicar
  os metros quadrados, cobertura, se quer junto à casa ou separado"; "Mesma lógica das garagens para anexos" — confirmed
  (annexes follow the garage's logic) — defaults ours: garage 3,70 × 6,00 = 22,2 m² (12–80), annex 3,00 × 4,00 = 12 m²
  (6–60). **2026-10-30: the aim is that the client may add a garage or an annex anywhere on the house, "mas pensando bem
  faz mais sentido ficar separado da casa"** — so a **separate** building is the offer's default, attached stays possible
  (below) — confirmed (the default: ours, from his "faz mais sentido").
- **Attached ("junto à casa", with a connection to the house): our structure grows by the extra space — the outline
  merges with the house's — and the roof is the same as the one chosen for the house** — user 2026-10-29 "se for junto
  neste caso com ligação para a casa deves juntar a nossa estrutura o espaço a mais e a cobertura tem de ser a mesma que
  escolheu para a casa" — confirmed — `exteriores.combinar` (the roof of the merged outline: the engine's, §7); doors,
  windows, interior walls, floors and pergolas carried to the new outline; a garage gets the 3,00 sectional gate (TV's
  table) on its front, its top 0,30 under the ceiling (§3, his rule 2026-10-30; the client adjusts its height in step 7
  within step 6's limits), an annex a door — ours. **The wall between an attached block and the house has its house side
  flush with the walls beside it, and an attached block never moves or removes interior walls** — user 2026-10-30 "tem de
  ficar alinhada com as paredes ao seu lado" — confirmed (the flush wall; the interior walls as relayed by the caller) —
  `exteriores.combinar` (the builder to check both). **What that wall is**: an interior wall with a Porta interior now (ours, to confirm) — **OPEN**
  (§15): an insulated exterior-type wall with a fire-rated door instead (general practice, CM §4; thermal / fire engineers).
- **Separate: a building of its own, any roof the client likes** — user 2026-10-29 "se for separado pode escolher a
  cobertura que quiser" — confirmed — the engine builds it as a configured house of its own (worker `edificio_casa`; the
  roofs offered: Oculta / Duas águas), **at least 2,00 m from the house (and never colliding with the house or a
  pergola)**, the house's cladding and pé direito — user 2026-10-30 "pode ficar 2 metros" (asked which of his two: first
  "dá um espaçamento de 3 metros pelo menos", then "deve ter pelo menos 2 metros de distância da casa") — confirmed (2,00
  minimum; **closes the 3 vs 2 m conflict, §15 item 23**) / ours (the cladding, the pé direito); licensing OPEN —
  configurator `exteriores.js` (`distanciaACasa`, the screen's check; the number: the builder's). (was ≥ 1,00 m — ours —
  until 2026-10-30; 3 m was his first message the same day.)
- **Interior walls only in an attached garage / annex; a separate building has none** — user 2026-10-30 "Não deixa apenas
  ficar ser possível ficar com paredes quando são junto a casa" — his wording is terse; our reading: interior walls are
  possible only where the building is attached to the house; **put to him, 2026-10-30
  later still: "Depois quando abrir o configurador e testar digo-te mas parece-me bem" — it seems right to him; the final
  word after he tests the configurator (pending)** — tentative (our reading, "parece-me bem") — configurator
  `exteriores.js` / `exteriores.combinar` (the builder to check).

## 9. Walls, inside
- **Mineral wool Volcalis COMFORT between the studs: 80 mm in exterior walls, 60 mm in interior walls**, against the outer
  OSB, a service gap inside — user 2026-10-09 "we use 60 mm wool on the interior walls and 80mm wool on the outside walls"
  — confirmed — JSON `interior.la_mineral`; `camadas.isolamento`.
- Pipes and cables run inside the walls — user 2026-10-09 "they can go tuck in the mineral wool" — confirmed — not in the
  tools. Boxes in exterior walls pierce the OSB 15 → airtight boxes — general practice (SC §3 B).
- **OSB3 15 mm** on the inner face of exterior walls and both faces of interior walls (buy: interior wall area × 2 +
  exterior wall area) — user 2026-09-24 "an OSB 15mm"; draft — confirmed — JSON `interior.osb`.
- **Finish = the client's choice, face by face, the inner face of the exterior walls included**: usually Pladur 12,5
  ("13") — N standard, H1 in wet rooms, F near heat; or wood (vertical boards on battens + counter-battens, horizontal on
  battens only — "slatted against slatted if it it vertical wood or just slatted if it is horizontal wood to create the
  breathable box"), ceramics, others — user 2026-09-24; 2026-10-21 "o user pode escolher o material de ambas as faces da
  parede"; 2026-10-22 "como já sabes o nosso acabamento padrão nessas faces interiores é gesso cartonado mas também inclui
  opções de madeira, cerâmica etc." — confirmed — **PO Q19** — JSON `interior.acabamento` (H1 / F not assigned to rooms),
  `interior.acabamento_opcoes`: **madeira** (on the OSB 15: contra-ripado 30×20 vertical @ 0,60 + ripado 30×20 horizontal @
  0,40 + vertical boards 19 mm, 0,12 wide, 3,0 m — 59 mm), **cerâmico** (azulejo 30×60 on Pladur H1 13, 22,5 mm) — products
  and spacings assumed ("a definir"); [cfgr] step 4 (an outside wall's inner face per side), house file `faces_interiores`
  → `para_construtor` → `casa_planta` `acabamentos` → `camadas.interior`. **A list of interior finish materials is promised**
  ("Mias tarde vou ter fornecer uma lista de materiais para acabamentos interiores", 2026-10-22). ⚠ On an exterior wall the
  OSB 15 is the airtight / vapour-control layer → battens, boxes and adhesive leave it sealed (tape every penetration);
  ceramics on Pladur H1 in wet rooms — general practice.
- Opening reveals inside: lined to the finish — the inside remate (§3; Pladur N 13 assumed, JSON
  `caixilharia.remates.material_interior`); H1 or tiles in wet rooms, the shutter box's access free — general practice —
  **PO Q23**.
- Pladur joint compound per 100 m²: 2 bags 1H + 1,5 bags 24H, paper tape, corner beads — draft — not in the tools.
- Services pre-installation (A/C power and copper 40 cm below the false ceiling; heat-pump pipes 40 / 80 cm above the
  floor — SC §9) — draft — not in the tools.
