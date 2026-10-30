# Método DiscoverCasa — vãos e topo das paredes (§3, §4) (parte de conhecimento/metodo-construtivo.md, v8.3)

## 3. Openings (vãos)
- **Every opening lies inside ONE module, sized round it**: opening + two 11×7,5 jambs + dimensioned margins; interior
  doors the same in the interior modules — D2503 Módulos [TV M20 2,19 with the window 1,50 × 0,95, margins 0,30 / 0,30 /
  0,50; M23 2,53 with the despensa door 0,94 at 0,13 + 0,075 from the corner; M12 / M14 2,15 = door 2,00 + two jambs] —
  company document (one house) — `divisor_modulos.py` (margins by costs — delegated, §2).
- **An opening at a wall end**: at a house corner the 110×75 corner post stays beside the jamb (an opening drawn closer is
  moved in, with a warning); where the wall ends against another wall a jamb may end the module ([TV] M6, P14 at P03) —
  D2503 Módulos (our reading) — `divisor_modulos.blocos`. Show the move.
- **Ombreiras (jambs) 110×75 full height on both sides of every opening** ([TV] 3,43 in exterior modules) — Casa CL; D2503;
  user 2026-09-24 "11x7,5m nos vãos" — confirmed — `estrutura_dc.emoldurar`.
- **Padieira 110×75** over openings below ≈ 2,8 m, between the jambs, directly over the opening; flat in exterior walls
  (75 high), turned in 75 walls (110 high) — Casa CL; D2503 Módulos — company document — JSON
  `estrutura.exterior/interior.padieira`.
- **Peitoril 110×75** under every window, between the jambs ([TV] sill tops ≈ 1,03–1,04) — Casa CL; D2503 — company
  document — `estrutura_dc.emoldurar`.
- **Verga 220×75 over wide openings**, under the top plate, the two 110×75 posts stopping under it (Casa CL 2,92 · 2,96 ·
  3,06 · 4,14 · 4,52) — user 2026-10-13 "a partir de 2,8 m-3m mais o menos entre esses valores"; 2026-10-22 "lembra-te mais
  de 3 metros usamos 22x7,5" — confirmed (over 3 m) / **OPEN: the threshold — 2,8, 3,0 or over 3,0, on the rough opening
  or the frame** — JSON `estrutura.verga_grande.vao_min` **2,8** (the lower end kept — ours; measured on the rough opening:
  `para_construtor` frame + 0,05, `casa_planta` / `estrutura_dc` the opening). **The norm in every module, full-height
  ones included** — user 2026-10-19 "exatamente neste caso o nosso engenheiro confirmou que poderia ser a de 11x7,5 mas por
  norma é 22x7,5" — confirmed. **[TV] 11×7,5 over the 3,00 garage door (M1) = an engineer-approved exception** (the
  lintel alone ≈ 2,5–3,5× over; the ≈ 1,2 m of sheathed frame above with the ring acts as header) — keep the engineer's
  note and conditions (OSB fixings for shear, ring unjointed over the opening, deflection) in the project file (TV #17);
  per house **PO Q8** (with Q3). Whether the engineer also covered TV's 2,00 janelas de correr on P03 / P01: OPEN. Upper
  verga limit: OPEN (widest seen 4,52).
- **Vertical 7,5×3,5 pieces (cripples)** above every opening up to the top plate and below every window down to the bottom
  plate, "para dar estabilidade ao vão"; no horizontal pieces — user 2026-10-15 "por nroma só tem as 7,5x3,5 verticais",
  "os nossos módulos base não possuem esse vigamento de 7,5x3,5 na horizontal nos vão" — confirmed —
  `estrutura_dc.emoldurar` (Montante curto). On the stud grid, 11×3,5 in exterior modules (full depth) — D2503 Módulos
  (one house) — the tools use 110×35 at the stud spacing. (The horizontal pieces of a 2026-10-09 photo were a site
  change — L14.)
- Doors: no bottom plate across the opening — Casa CL — `estrutura_dc.emoldurar`.
- **Interior doors 2,00 × 0,80 → rough opening 0,87 × 2,03** above the finished floor (3 cm on top, 3,5 cm each side) —
  user 2026-10-09 "usually we use 2mx0,8m doors and we leabe 3cm on top and 3,5 cm on each side" — confirmed — JSON
  `estrutura.porta_interior`; `casa_planta` centres it on the architect's door (assumed). [TV] all 8 = 0,87 × 2,03 (D2503).
  Other sizes: **PO Q13**. [cfgr] a **"Porta interior"** card (0,80 × 2,00, rough 0,87 × 2,03) on interior walls — user
  2026-10-28 "Adicionar portas interiores ao menu de portas e janelas e permitir colocar portas e janelas nas paredes
  interiores" — confirmed — `colocar.js` → `para_construtor` (doors only on interior walls). **Interior walls take doors
  only (0,80 × 2,00), no windows** — user 2026-10-29 "Só portas por norma ninguém usa janelas nas paredes interiores" —
  confirmed — `colocar.js` / `para_construtor` (`camadas.caixilharia` frames only exterior modules). (superseded
  2026-10-29: windows in interior walls an open item.) [cfgr] **The rough opening is drawn filled**: a frame lining the
  reveals (3,5 at the jambs, 3 at the head, the wall's depth), 7 cm architraves on both faces, the leaf and a lever handle
  each side — user 2026-10-29 "Portas interiores estão com um gap dos lados e na parte de cima e não tem um aspeto de porta
  interior" — frame product and architrave size assumed (ours, §15) — `cena.js` portaInterior.
- **The exterior openings come from the project's approved openings table** (type, quantity, L × A, protection, glass,
  opening side): it fixes what goes in each opening and its nominal size; the architecture fixes where; the company module
  drawing sizes the module and the rough opening — user 2026-10-19 "já te vou fornecer um print com os vãos para os
  modelares" → "está anexado o print" — confirmed — **PO Q2** (table and maker's order), **PO Q13** (elements different
  from the table) — TV cfg `camadas.caixilharia.itens`; `camadas.caixilharia()`. The table's sizes are the frames without
  the clearance — **tentative** ("acho que é apenas a medida do caixilho sem folga mas normalmente contamos com a folga",
  2026-10-19 18:12) — and not always the element built ([TV] entrance, basculantes). Where table and architecture differ
  the table wins ([TV] the kitchen window a vidro fixo, the garage door seccionado) — assumed. The builder without real
  modules does not size rough openings from the table (cfg `aberturas`, fallback 2,20 doors, windows 1,00 / 1,75) — not in
  the tools.
- **Exterior rough opening = frame (caixilho) + a clearance (folga) of 2,5 cm each side — in width and in height — by
  default; it depends on the frame** — user 2026-10-20 "Depende do caixilho mas normalmente 2 ,5 cm de cada lado, mas isto
  são pormenores que depois te posso dar dependendo da obra senão vai com o default de 2,5 cm"; (13:25) "Sim mas nem sempre
  é essa a folga lá está depende da caixilharia..." — confirmed (default) — **PO Q11** — JSON `caixilharia.folga` 0,025;
  `camadas.caixilharia()` (an element filling its opening = opening − 2 × folga). For a new project: **width = frame +
  0,05; height = frame + 0,025 at the head + 0,025 under a window + the maker's shutter-box height where there is an
  estore** — assumed: none under a door to the floor; the box height (D2503 shows only the allowance, TV + 0,15 / + 0,20).
  ⚠ The tools treat the janelas de correr (to the floor) as windows (2,5 cm under, a bottom profile) — whether they get the
  clearance under them: OPEN, with the thresholds (PO Q23). (was "the maker's size + a clearance", our wording answered
  "Sim exatamente", until 2026-10-19 — L34.)
- [TV] **Rough openings as built** (D2503 Módulos): janelas de correr "2 folhas" (sala M3, quartos M9, M12, M14) **2,00 ×
  2,40**; garage M1 **3,00 × 2,20**; entrance M5 (P03) **1,04 × 2,20** — table 0,90, as built a bigger door filling it
  (user 2026-10-19 18:12 "neste caso é uma porta maior e mais robusta que cabe naquele espaço", L37); despensa door M23
  (P11, NW corner) **0,94 × 2,20** — table 0,80, fills it too (user 2026-10-20 "sim coloca a encher o vão como na
  principal"); kitchen M20 **1,50 × 0,95**; WC M6, M18 **0,75 × 0,75**; despensa window M24 (P12) **0,75 × 0,95**; sills
  ≈ 1,03–1,04. Table → D2503: janelas de correr 2,00 × 2,20 → + 0,20 box in height; vidro fixo 1,50 × 0,80 → + 0,15 box;
  doors 0,80 / 0,90 → + 0,14 in width (≈ a 7 cm door frame a side — ours); garage the same; basculantes 0,80 × 0,80 → 0,75
  × 0,75 (WC, no estore) / 0,75 × 0,95 (despensa, estore) — D2503's 0,75 stands, the element modelled 0,73 (user
  2026-10-19 18:12 "está ótimo como fizeste"). The shutter box sits inside the rough opening, above the element. ⚠ CONFLICT
  with the 2,5 cm default (TV only, low priority, TV #20): the frames come out 5 cm under the table in width; in height the
  WC basculantes 0,80 in 0,75, doors and garage 2,20 in 2,20 (no head clearance), boxes ≤ 0,10 (M20, M24) / ≤ 0,175
  (janelas de correr) → the table fits D2503 only for the two doors, in width (corrected answer sent 2026-10-20 night,
  reply pending — L41, L42). The model keeps D2503's openings and shrinks the frames.
- **Caixilharia — the company standard "para já"**: aluminium lacado cinza rato **RAL 7016** with **rotura térmica**,
  **vidro duplo térmico**, **estore exterior automático** (windows only, which ones from the table), exterior doors **painel
  liso** in the same aluminium — user 2026-10-19 (18:12) "São o nosso padrão para já mas estamos a pensar mudar quando o
  fizermos eu aviso-te" — confirmed (for now; a promise, §15) — **PO Q12** — JSON `caixilharia.material` "Alumínio RAL
  7016". ⚠ JSON `caixilharia.material_portas` "Portão seccionado RAL 7016" is used for the painel liso doors too. The
  sectional garage door: standard or TV only — OPEN. Company website: PVC optional.
- [TV] caixilharia as approved: "lacado de cor cinza rato", "rotura térmica", "vidro duplo térmico" (transparente; fosco
  in the WCs — the WC row also says "trasnparente": modelled fosco, OPEN, TV #20); estore on 6 of 11 (quartos, sala,
  cozinha, despensa basculante); doors "Painel liso … (a escolher de acordo com o catálogo)", "Abertura para a direita";
  "Portão de garagem seccionado automatico", "Abertura para cima"; 11 items, 31,06 m² — TV cfg `camadas.caixilharia.itens`
  (M5 `largura` 1,04 / `largura_tabela` 0,90; M23 0,94 / 0,80).
- **Doors never take an estore — only windows** (no box over a porta nor a portão de garagem) — user 2026-10-27 "Prtas não
  tem estore apenas as janelas" — confirmed / assumed (a window may have one, not must — PO Q12) — [cfgr] `colocar.js`
  `semEstore`; `para_construtor.py` drops one ("as portas não levam estore — ignorado"). Consequence (ours): a door's rough
  top = 2,225; under an exposed roof the module top is pé direito − 0,0535 (2,3465 at 2,40) and a door head needs 2,225 +
  0,075 + 0,035 = 2,335 → **every door narrower than 2,75 fits even at 2,40**. A porta-janela de batente (window or door?):
  ask when a client wants one.
- **Sliding windows of 3 and 4 leaves are in the range** — user 2026-10-22 "quero que cries opções de janelas de correr mas
  3 janelas e 4 janelas" — confirmed ("janelas" read as folhas) — [cfgr] defaults (ours): 3 folhas **2,70 × 2,20**, 4 folhas
  **3,60 × 2,20**, to the floor, with an estore. Sizes, heights, estore, which leaves slide: OPEN. The 3-leaf (rough 2,75)
  takes the padieira; the 4-leaf (rough 3,65) the 22×7,5 verga and a module past 3 m, site-built (§2) — ours.
- **Every opening gets remates (trims) round the frame, so the wall's layers are never exposed** (windows, exterior doors,
  garage door; outside through OSB 9, Traspir, battens, cladding; inside through OSB 15, wool, finish) — user 2026-10-20
  (13:25) "Todos os vão levam remates a volta da caixilharia de forma as diferentes camadas das nossas paredes não ficarem
  expostas, anota isto também" — confirmed (every opening) / assumed (both faces, material) — **PO Q23** — JSON
  `caixilharia.remates` (`espessura` 0,002, `aba` 0,03, `pingadeira` 0,03, "Remate RAL 7016", `espessura_interior` 0,013,
  `material_interior` "Pladur N"); `camadas.caixilharia()` collections 7.5 / 7.6. As modelled (assumed): outside folded
  aluminium RAL 7016 from frame to cladding face, a return over the clearance, a 3 cm flange, a sill with a 3 cm drip under
  windows not reaching the floor; inside a 13 mm lining. **Thresholds (soleiras) at openings to the floor: OPEN, not
  modelled.** [TV photos: dark surrounds; a light one on the garage; light pieces under the east janelas de correr M12 /
  M14 → the colour is not always the frame's — ask, TV #23.] General practice (CM §4; SC §3b; TV #23): the remate is the
  trim, not the seal — clearance sealed in three planes (tape / sealant outside, foam, airtight tape frame → OSB 15), the
  Traspir turned into the reveal and taped; a head flashing with drip lapped under the Traspir above; jamb remates over
  the sill's ends; sill with upstand, stop-ends, fall, drip ≈ 30 mm clear; at floor openings a threshold with a fall and a
  tray ([TV] deck 2 cm under the floor, TV #5); separating tape where aluminium meets copper-treated battens; flanges clear
  of the cavity vents; H1 or tiles in wet-room reveals; the shutter box's access free — not in the tools.
- How a window / door is set in the wall (plane, fixings, airtight tape, sill, head flashing, shutter-box type): OPEN.
  General practice (SC §3b, TV #14, #20): frame in the airtight plane taped to the OSB 15, membrane lapped to the frame,
  an insulated shutter box (monobloco) taped airtight with the Traspir over its head; a basculante under an estore must not
  open outward; a sectional garage door needs ≈ 0,30 headroom (his rule since 2026-10-30, below); the entrance "0,9" should be the clear passage under an
  accessibility plan (DL 163/2006 — check). Model (`camadas.caixilharia()`, collection 7): the table size centred at the
  frame's outer face, folga 0,025, the box filling above, profiles 6 / 5 cm, glass 24 mm; a warning only beyond 2 × folga
  + 1 cm (smaller misfits shrunk silently — L41); none when an element is much smaller than its opening (L37).
- **Openings stay under the ceiling: the rough-opening top at most the pé direito** (the box top may reach the ceiling line)
  — user 2026-10-22 "Apenas precisamos de 20 cm portanto seria 2,40 de pé direito" (a 2,20 janela de correr + 0,20 estore
  at a 2,40 pé direito) — confirmed (the 2,40) / assumed (as the limit for every opening) — [cfgr] `colocar.js` `topoMax` =
  pé direito − the box (0,20 to the floor; 0,125 over a window's frame top) or − 2,5 cm, every roof; `para_construtor`
  notes a rough top above the pé direito; `casa_planta` does not check. (was pé direito − 0,10 hidden / − 0,16 exposed —
  ours — until 2026-10-22 / 28.) Interior doors fit from 2,40.
- **The garage gate (portão seccionado): its top 0,30 under the ceiling, for the sectional door's mechanism** — user
  2026-10-30 "sim exatamente" (to our reading: the gate needs ≈ 0,30 headroom under the ceiling for the track and
  mechanism, as [TV]'s 2,20 gate under a 2,50 pé direito) — confirmed (general practice until then, line above) — [cfgr]
  `colocar.js` `FOLGA_PORTAO` 0,30 (the gate's `topoMax` = pé direito − 0,30; the client adjusts the gate's height in step
  7 (garages) within the limits step 6 (openings) gives). Our arithmetic: at a 2,40 pé direito the gate is ≤ ≈ 2,10 high;
  the "+ 0,134 from ≈ 2,54" for a ≥ 2,75 garage door in the raise line below assumed its top at the pé direito → recompute
  (the builder to check, X1). (supersedes the "≈ 0,30 headroom" of the general-practice line above as only our advice.)
- **Under an exposed roof, when the head over the highest opening does not fit under the exterior module top, the exterior
  modules are made taller** (rough top + lintel 0,075 or verga 0,22 + top plate 0,035 − module top pé direito − 0,0535) —
  user 2026-10-28 "opção a" (options: (a) taller exterior modules, (b) the lintel in the travessa / amarração zone, (c)
  other) — confirmed / assumed: **for the whole house** (the beams level on the ring, the interior modules follow) and the
  **false ceiling kept at the pé direito on longer réguas** — `para_construtor.converter` (X1). What raises them at 2,40
  (ours): the 2,20 janela de correr + estore **+ 0,164** (fits without a raise from ≈ 2,57); the screen's default window
  1,20 at sill 1,00 with estore + 0,089 (from ≈ 2,49); a garage door ≥ 2,75 wide (22×7,5 verga) + 0,134 (from ≈ 2,54); the
  4-leaf 3,60 (verga) **≈ + 0,31** (0,309; from ≈ 2,71); no door. ⚠ Ours: one opening lifts the whole house (cladding,
  cércea, price) → name the opening, offer an alternative (X1); the ceiling drop grows to ≈ 0,19 (2-leaf) / ≈ 0,34
  (4-leaf) → réguas long enough (§6); a 2,5 cm clearance over the box (2,425 vs 2,40): not said (PO Q11). Under a hidden
  roof nothing changes (full-height modules). ⚠ From a plan, `casa_planta` still caps every opening silently under its own
  framing (`min(z1, Hf − top plate − lintel)` ≈ pé direito − 0,16 exposed; − 0,107 with the verga) → it should raise as
  `para_construtor` does (X1).
- **In a full-height exterior module (hidden roof) the lintel sits directly over the opening, the cripples run on the
  grid up to the module's top plate** (the ring on the inner face across them), jambs full height — D2503 Módulos [TV doors
  2,20 / 2,40 under a ring at 2,543] — company document; the same on 22×7,5 roofs — assumed. The builder without real
  modules frames under the ring (`casa_planta` `continuar`).
- An opening head is lowered so the padieira / verga fits under the top plate; a window sill ≥ bottom plate + peitoril +
  5 cm — assumed — `casa_planta.construir` ([SB] heads ≈ 3 cm lower, SB #21). (On exposed roofs superseded by "opção a",
  not yet in `casa_planta` — X1.)
- A doorway left as a gap between two modules gets a bandeira (padieira at the door head, short studs, top plate,
  afinação; 110×75 jambs on the module ends) — assumed (after "There are gaps in between the walls … why ?", 2026-10-09;
  how DiscoverCasa closes it: OPEN) — `estrutura_dc.emoldurar_bandeira`. In the company's own drawings every door is inside
  a module — the gap arises only from third-party drawings (SB engineer).

## 4. Top of the walls (afinação, amarração)
- **Exposed roofs: viga de afinação exterior 110×35 on the exterior modules, then the viga de amarração 110×75 round the
  whole house** — draft "Vigas de afinação exterior … 11*3.5 … Por cima dos módulos exteriores", "Vigas de amarração … À
  volta da casa toda"; user 2026-09-30 (ceiling beams "assentam sobre vigas de amarração") — company document + confirmed
  / assumed (that these top pieces are the exposed-roof rule; every hidden roof has full-height modules) — JSON
  `estrutura.afinacao_exterior`, `estrutura.amarracao`; `casa_planta.construir` when not `anel`. The ceiling beams run
  over the wall to its outer face — assumed.
- **Hidden roofs: no afinação; the amarração 110×75 is a ring on the inner face of the full-height modules** — 75 into the
  room, 110 high ([TV] Z 2,543–2,653), all round, under the ceiling beams — D2503 sheet 1 "Amarrações (11x7.5)" — company
  document; every hidden roof, 22×7,5 too (user 2026-10-21, §2) — confirmed — JSON `estrutura.lameladas.amarracao`,
  `estrutura.platibanda_modulos_inteiros`; `casa_planta.construir` (`anel`, `apoio_vigas`). *Why*: it ties the modules and
  carries the beams without cutting them. ⚠ The ring works as a ledger: each beam reaction (≈ 4–5 kN design) reaches the
  studs through its screws → engineer per house (TV #6); no ring joint over an opening (part of the header — TV #17) —
  general practice.
- **The ceiling beams never cross the exterior modules nor cut their studs — lameladas and 22×7,5 alike**: inside the house,
  against the modules, on the ring; at most the **beam** is notched on site ("entalhe nas vigas") to the exact length —
  user 2026-10-21 "essas vigas ficam por dentro e encostadas as da estrutura não atravessam ou fazem com que as da estrutura
  sejas separadas em dois pedaços, não é realista"; "quanto muito é feito o entalhe nas vigas de 22x7,5 de forma a ficarem
  do comprimento perfeito para encaixar de um lado e do outro sem atravessar a estrutura do módulo" — confirmed —
  `casa_planta.apoio_vigas` (inner face to inner face, no pockets; [TV] lameladas 170,49 → 166,53 m, 36 notches → 0, module
  pieces 702 → 696; the TV rebuild = v6.5). The notch's shape (square cut to length, or a seat over the ring): not said —
  the model cuts square on the ring — OPEN, low priority (a notch under a beam end weakens it in shear, CM §1). (was: the
  lameladas notched through the studs, from "sim há um entalhe feito e a viga fica por dentro", until 2026-10-21 — L46.)
- **The ceiling beams are cut to fit each house** — user 2026-10-21 (later) "Sim normalmente cortamos para "encaixar" no
  tipo de obra que temos, há casas com mais comprimento outras com menos, percebeste a lógica...." — confirmed → [TV]
  D2503's 8,50 / 11,00 are nominal (the outer depths); the piece is the inside length (≈ 8,28 / 10,78), bought from stock
  (13,5 / 12 m) and cut on site (our reading); the 22×7,5 too ("do comprimento perfeito") — `casa_planta.apoio_vigas`.
  The material list should give cut and stock length (§11).
- **The ceiling beams bear on the interior wall modules they cross — lameladas included** — user 2026-10-09 "it is
  discharged on the wall entirely and not only on one structural beam"; 2026-10-19 "Por norma as vigas de apoio ao teto
  apoiam-se nas paredes dos módulos interiores também" — confirmed — `casa_planta.py`, `estrutura_dc.py`; how: the interior
  module made to measure (§2). ⚠ General practice (TV #6 b–f, engineer per house): these walls are load-bearing (≈ 5–8 kN
  design per lamelada; a 75×35 stud ≈ 2,47 high ≈ 9 kN in buckling → the viga spreads it; joint the viga only over a stud,
  never under a beam); bearing across the grain at the plates; a short end span (< ≈ 0,4 × the next) lifts → hold-down; the
  walls cannot be removed later (client changes, the configurator).
- **Interior walls: viga de amarração (interior) 110×75 upright** ("Trabalha ao alto") on the made-to-measure modules,
  level with the exterior top (§2) — draft (as "Vigas de afinação interior") + user 2026-10-19 (18:12) — JSON
  `estrutura.afinacao_interior`; `casa_planta.construir` names it "Viga de amarração interior" with lameladas, "Viga de
  afinação interior" on 22×7,5 (naming only). Use "viga de amarração" with him.
- Site timber as long as possible ("Quanto maior o comprimento melhor"), jointed over supports — draft — not in the tools.
  ⚠ [TV] D2503 cuts the madres into pieces ≤ 3,66 jointed on a lamelada — which rule for which piece: OPEN.
- Two storeys: vigas de amarração 110×75 also on the ground-floor exterior walls, under the floor joists (3_Vigamento;
  none on interior walls; no afinação) — company document (our reading) — OPEN ([SB] asked 2026-10-15) — not in the tools
  (`estrutura_dc` puts the joists on the top plate).
