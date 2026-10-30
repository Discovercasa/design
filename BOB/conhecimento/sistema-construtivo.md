# DiscoverCasa build system (sistema construtivo)

How DiscoverCasa builds a house, layer by layer — **the company standard**. Sources: the user (from 2026-09-24) and the
company draft "Execução Técnica OBRA" (`fontes/execucao-tecnica-obra_2026-09-24.md`, still being developed — merge new
versions here). Tool numbers live in `ferramentas/modelo/sistema_construtivo.json` (keep in sync); the current rules,
rule by rule, in `metodo-construtivo.md`; the user's words in `registo-conversas.md`.
- **Always the DiscoverCasa method** (user 2026-10-09 for Sobral, 2026-10-15): "o que o arquiteto muitas vezes escreve
  não significa que tenha de ser seguido restritamente, nós usamos o nosso método construtivo sempre portanto segue o
  nosso". The drawings fix the geometry (plans, levels, openings, heights); this standard fixes how it is built; the
  licensed specialty projects (thermal, acoustic, stability) must follow these build-ups (Sobral `revisao-tecnica.md`
  #26, Torres Vedras `revisao-tecnica.md` #1).
- Status words: **confirmed** = the user said it · **draft** = company document · **ours** = our reading / assumption ·
  **OPEN** = to ask. **TV** = Torres Vedras as built (one house): the company standard only where the user said so.
  Open items and promises: "Pending" at the end.

## 1. Sequence on site
1. Concrete foundation (§8). Modules (wall panels) fixed to the base with M10 bolts, 2–3 per module.
2. Timber structure: prefabricated wall modules + site timber (§2).
3. Outside of the exterior walls: OSB 9 → Traspir 95 membrane → finish chosen by the client (§3).
4. Inside: mineral wool between the studs → OSB 15 → finish (§4).
5. Floors, ceilings and roof covering (§5–§6).

## 2. Structure — the DiscoverCasa skeleton
- Timber: **casquinha branca** = *Picea abies* (Norway spruce / European whitewood); casquinha vermelha = *Pinus
  sylvestris* (pinho nórdico). Screws Turbosharp 6×70, 6×140, 6×160 (torx).
- **Sections** (confirmed 2026-09-24, 09-30, 10-09): **exterior walls 110×35**; **interior walls 75×35** (draft 80×35 —
  which: OPEN); **110×75 at the house corners and at every opening (vão)** — at a corner two 110×75 side by side, one
  per wall; **220×75 "22×7,5"** (not 22,5×7,5 — "they are 22x7,5", 2026-10-09) for the ceiling beams, the floor joists
  and the verga of wide openings. Draft purchase mix: 110×35 40 %, 110×75 40 %, 80×35 20 %.
- **Verga 22×7,5 over wide openings** (confirmed): "a partir de 2,8 m-3m mais o menos entre esses valores" (2026-10-13);
  "lembra-te mais de 3 metros usamos 22x7,5" (2026-10-22); draft "> 3 m". Narrower openings: the 110×75 header. Model:
  2,8 (JSON `verga_grande.vao_min`). Exact threshold (2,8 / 3,0 / over 3,0; rough opening or frame): OPEN.
  TV exception: the 3,00 garage door has an 11×7,5 lintel in a 3,50 full-height module — "exatamente neste caso o nosso
  engenheiro confirmou que poderia ser a de 11x7,5 mas por norma é 22x7,5" (2026-10-19) → engineer-approved for TV
  only (TV `revisao-tecnica.md` #17).
- **Module ends** (confirmed 2026-10-09, "leave them as they are now and those are the rules"): at a mid-wall joint
  each module keeps its own 35 end stud (two 35 studs side by side, Casa CL M005); 110×75 only at the house corners and
  at openings (incl. a module end beside a doorway). (Was "11x7,5m nos vãos e fins de módulos", 2026-09-24.)
- **Module framing** (Casa CL module sheets, `fontes/estrutura-exemplo-casa-cl/`; colours inferred, no legend: red
  110×75, orange 220×75, white 110×35 / 75×35):
  - studs 35 wide, **40 cm clear** (≈ 0,435 centre to centre), laid out from one end; the last bay takes the rest;
  - **single bottom and top plates**; no noggings except the **escadas** where another wall meets (§2b item 5);
  - openings: 110×75 jambs full height both sides, 110×75 header, 110×75 sill under windows; **doors have no bottom
    plate**; wide openings: two 110×75 posts under a 220×75 lintel at the module top (Casa CL M007 4,52, M010 3,06,
    M011 4,14, also M014 2,92 and M132 2,96 — lintel at 2,12 with short studs above);
  - **short pieces 7,5×3,5 at openings — vertical only** (confirmed 2026-10-15, photo
    `fontes/fotos-teto-cobertura/1b_pecas_7,5x3,5_nos_vaos_azul.webp`): above the opening up to the top plate and below
    a window down to the bottom plate, "para dar estabilidade ao vão"; "por nroma só tem as 7,5x3,5 verticais"; "os
    nossos módulos base não possuem esse vigamento de 7,5x3,5 na horizontal nos vão mas sim vigamento vertical". The
    horizontal pieces in photo 1 were a site change: "este módulo sofreu uma alteração em obra e foi necessário
    acrescentar as vigas horizontais". Spacing = the stud spacing (model). Their section in the 110 exterior walls (model
    110×35) and against which face: OPEN (asked 2026-10-15);
  - in 75 interior walls the 110×75 is turned (75 = wall depth, 110 along the wall);
  - Casa CL heights: ground floor modules 2,97 exterior / 2,80 interior; upper floor 3,52 exterior (rising above the
    ceiling — ours) / 2,68 interior; interior doors 2,10 high.
- **Interior doors** (confirmed 2026-10-09): "usually we use 2mx0,8m doors and we leabe 3cm on top and 3,5 cm on each
  side of the door for the door to go in easily" → door 2,00 × 0,80, rough opening **0,87 × 2,03** above the finished
  floor (JSON `porta_interior`); the same at TV (D2503). Exterior doors and windows: §3b. Interior walls take doors
  only, no windows — "Só portas por norma ninguém usa janelas nas paredes interiores" (2026-10-29).

### Module size — length
- **DiscoverCasa sets it** ("Nós definimos o tamanho maximo de cada módulo", 2026-10-15). **Factory modules normally
  ≤ 3 m** — "o tamanho que normalmente fazemos em fábrica não ultrpassa os 3 metros mas dependendo da casa vê o que se
  enquadra melhor" (2026-10-19); "os módulos exteriores podem ir até 3 m" (2026-10-20 night — a maximum, not a target;
  interior not asked, TV ≤ 2,72). "já fizemos módulos de 5 metros por exemplo" (2026-10-15 — an exception, ours).
- **Bigger modules are built on site**: "esses módulos maiores são montados em obra" (2026-10-19; D2503 "* Painel a
  executar em obra"), at the length the wall / opening needs.
- **How a wall is split** (confirmed 2026-10-20 night: "consigas dividir a casa nesse diferentes módulos que falas
  dependendo dos vãos que o cliente escolher e paredes interiores"; "os módulos também vão ajustando consoante os vãos"):
  by its openings and interior walls, ours to work out → the **module divider** `ferramentas/modelo/divisor_modulos.py`
  (built 2026-10-20 night — "Avança com a fase 1: o divisor de módulos, testado contra o D2503 de Torres Vedras."):
  plain modules in whole bays (exterior 5 = 2,21; interior 4 / 6), every opening inside one module, no joint where
  another wall meets, factory ≤ 3,0, longer only round an opening that needs it (site-built). Answers 2026-10-20 night:
  - where a wall's remainder goes — "Vai com a opção que achares melhor, força nisso confiança" → **ours** (the cheapest
    split by the JSON `estrutura.divisor` costs);
  - two openings closer than a pier — "por defeito podes assumir que sim quando esta situação acontece desde que sejam
    duas janelas como neste caso" → **moved apart, half each, to a 0,32 pier, when both are windows** (TV P18, D2503
    M13; ⚠ changes the approved façade — telas finais, TV `revisao-tecnica.md` #24). With a door: OPEN (the divider
    keeps them in one module);
  - a site-built module — "depende da situação mas neste caso sim usa o tamanho que o vão precisa" → **as short as the
    opening needs** by default (TV garage 3,39, not D2503's 3,82); which situations want it longer: OPEN.
  Checked on TV: the rules hold, 19 of 50 modules identical, every difference = where a remainder goes (TV
  `docs/modulos-D2503.md`, `divisor-vs-D2503.svg`). The configurator's 3 m walls are the client's blocks, not modules.
- **Transport is not a design constraint** (confirmed 2026-10-21): "A questão do transporte não precisas de te
  preocupar, podemos sempre arranjar uma empresa especializada para transportar os módulos ou fazer os módulos em obra"
  → no limit on module height or the 2,55 road width in our designs. ⚠ A special load or site-built modules cost more —
  the price should carry them per house (ours; OPEN with the price list).
- Wish: a settings panel for "comprimentos dos módulos e a sua composição" ("Futuramente"; `discovercasa.md` Product
  vision 1).

### Module size — height and the clear height (pé direito)
- The modules follow the house ("os modulos vão de encontro ao tamanho da casa", 2026-10-15).
- **No fixed clear height — the client chooses** (confirmed 2026-10-21): "A altura não temos fixa o cliente pode
  escolher a vontade o que preferir"; "O cliente pode escolher qualquer valor mas podemos deixar sugestões por exemplo
  essas 3 sugestões que falaste que por norma são o habitual" → any value; suggestions **2,40 / 2,50 / 2,60**. In the
  configurator chosen with the total area: "quando o cliente escolhe a área total da casa deve também escolher o pé
  direito que deseja e assim já ajustamos a estrutura para isso". Our default 2,50 (= TV as built; TV architecture 2,60).
  Precedents: Casa CL modules 2,97 / 2,80, Sobral 2,58 / 2,40 (upper 2,40 kept, 2026-10-09).
- **The house may end taller than the architecture**: "sim isso é natural e também não tem qualquer tipo de problema"
  (2026-10-15); "eu sei que isto altera a altura total da casa mas não tem mal é o suposto nestas coberturas escondidas"
  (2026-10-16). ⚠ The licensed cércea / PDM (TV `revisao-tecnica.md` #7).
- **Module heights**: hidden roof — exterior = clear + ≈ 1,0 (TV 2,50 → 3,50, two slopes), more on a one-água roof (the
  rise grows with the whole run: his U 18,95 × 12,65 → parapet 3,82, 2026-10-28 — engine's arithmetic, §6), interior =
  ceiling-beam underside − 0,11 (TV 2,543; rule below); exposed roof — module ≈ clear − 0,05 under afinação 35 + amarração 75 (TV v1–v3 2,60 → 2,552;
  the builder's rule — ours).
- **Estore head at a 2,40 pé direito** (confirmed 2026-10-22): "Apenas precisamos de 20 cm portanto seria 2,40 de pé
  direito" → the estore box takes **0,20**; the **2,20 janela de correr** to the floor (rough 2,40) fits a 2,40 clear.
  (Doors take no estore — 2026-10-27, §3b; a 2,20 door's rough top is 2,225.) **When the head over the highest opening
  does not fit under the module top on an exposed roof — "opção a" (2026-10-28): the exterior modules are made taller**
  (confirmed); the false ceiling stays at the pé direito on a longer suspension (ours). At 2,40 (ours, arithmetic): the
  1,20 window with estore ≈ + 0,089, a garage door ≥ 2,75 wide ≈ + 0,134, the 4-leaf window ≈ + 0,31; the beams sit
  level on the ring, so the whole house rises; the ceiling drop grows up to ≈ 0,34 → check the réguas' length. OPEN: a
  2,5 cm clearance over the box (2,425 vs 2,40).
- ⚠ Limits (ours, general practice; the client's range was not given): (1) RGEU art. 65.º — pé-direito livre ≥ 2,40 in
  dwellings, ≥ 2,20 in vestíbulos, corredores, instalações sanitárias, despensas, arrecadações (check the current text);
  the configurator's 3,00 cap is ours. (2) Studs: exterior 110×35 = module − 0,07 (TV 3,43); at 3,00 clear ≈ 3,93 →
  stock length and buckling / wind at 0,435 → engineer per house. (3) Tremolo boards are 4,0 m (JSON
  `exterior.opcoes.A.forro`) → past ≈ 2,9–3,0 clear on a TV-like roof a horizontal joint with a drip / flashing.
  (4) Boards: OSB 2500×1250, Pladur 1200×2600 (assumed); above 2,60 longer Pladur (check the supplier) or a joint backed
  by the OSB 15 — waste, not a hard limit. (5) House height = clear + ≈ 1,0 on a hidden roof → cércea / PDM. (6) The
  price grows with the clear height. The ceiling drop (suspension 0,1185 below the ring, §5) does not depend on it.

### Hidden roof — the walls (confirmed for every hidden roof, 2026-10-21)
As built at TV (DiscoverCasa roof drawing D2503, 2026-10-16, `Construção Torres Vedras/docs/cobertura-D2503.md`) and
confirmed for every hidden roof, also over 22×7,5 beams: "sim exatamente os módulos vao inteiros ate ao topo da
platibanda" (2026-10-21).
- (1) The modules' outer face is the foundation line ("Dimensão da fundação e módulos" — the foundation is cast to the
  modules); the cladding lies outside it ("linha de pronto" ≈ 9 cm out) — TV reading.
- (2) Exterior modules run **in one piece from the base to the parapet top** (TV 3,50; roof sections Z 3,4915): no
  separate parapet module, no afinação exterior.
- (3) The **amarração 11×7,5 is a ring on the inner face** of the modules (TV Z 2,543–2,653), not on top.
- **(4b) The ceiling beams never cross the exterior modules** (confirmed 2026-10-21): "essas vigas ficam por dentro e
  encostadas as da estrutura não atravessam ou fazem com que as da estrutura sejas separadas em dois pedaços, não é
  realista"; "isso não acontece quanto muito é feito o entalhe nas vigas de 22x7,5 de forma a ficarem do comprimento
  perfeito para encaixar de um lado e do outro sem atravessar a estrutura do módulo" → lameladas and 22×7,5 alike end
  **inside, against the modules' inner face, on the ring**; the module studs are never cut; at most **the beam** is
  notched to the exact length. (Was, 2026-10-19: "sim há um entalhe feito e a viga fica por dentro" / "O entalhe é feito
  em obra", read then as a notch in the module.) Form and place of the notch, and whether lameladas get it: OPEN, low
  priority. **Beams cut to fit each house**: "Sim normalmente cortamos para "encaixar" no tipo de obra que temos, há
  casas com mais comprimento outras com menos" (2026-10-21) — D2503's 8,50 / 11,00 are the outer depths (nominal), the
  pieces the inside length (8,28 / 10,78), cut from stock (on site — ours).
- ⚠ Each beam end bears on the 75 mm ring only: the ring works as a ledger, its screws into the studs carry the whole
  reaction → engineer per house (TV `revisao-tecnica.md` #6); a notch on the underside of a beam end weakens it in shear
  (`construcao-madeira.md` §1); the cladding past the foundation edge needs the cavity bottom meshed and the Tremolo foot
  clear of the ground (TV #16).

### Exposed roof — top of the walls; interior modules
- Draft: on top of the (upper) modules **afinação exterior 110×35 + amarração 110×75** on the exterior walls (= 110) and
  **afinação interior 110×75 upright** on the interior walls (= 110), so the ceiling beams sit level on both. The
  exterior part is for exposed roofs only.
- **Interior module height — the rule** (confirmed 2026-10-19, 18:12): "Nós fazemos os módulos de forma a ficarem à
  medida certa das vigas amarração" → interior module = ceiling-beam underside − 0,11, **no packing** (TV 2,653 − 0,11 =
  **2,543**, studs 2,473). ⚠ D2503 Módulos draws **2,53** (studs 2,46, cut list 109 × 2,46) — 13 mm less: OPEN (TV
  `revisao-tecnica.md` #6). TV model v6.1 follows the rule and names the piece "Viga de amarração interior".
- **The base is checked with a laser** (confirmed 2026-10-20): "nós usamos um laser para verificar isso, exatamente como
  sugeriste" (hard shims where needed, each beam fixed to the interior piece — covered by "exatamente", ours).
- **Ceiling beams bear on the interior walls they cross** (confirmed 2026-10-19): "Por norma as vigas de apoio ao teto
  apoiam-se nas paredes dos módulos interiores também".
- Engineers' drawings may give other sections (Sobral 160×80 / 100×80); Sobral is modelled with the DiscoverCasa
  skeleton since 2026-09-30 — the engineer must re-check it.

### Site timber ("madeira obra"; pieces as long as possible)
| Piece | Section | Where |
|---|---|---|
| Vigas de amarração (tie beams) | 110×75 | on the exterior walls all round (hidden roof: a ring on the inner face, above); 3_Vigamento: on both floors, the ground-floor ones under the upper floor joists (ours, OPEN — §2a) |
| Vigas de afinação interior | 110×75 upright | on the interior modules, which are made so it meets the ceiling beams exactly |
| Vigas de afinação exterior | 110×35 | on the exterior modules — exposed roofs only (not in 3_Vigamento) |
| Vigas de apoio ao teto | 22×7,5 at ≈ 1 m (3_Vigamento 0,989) | down the slope (§6 item 2); **free span up to 8 m — the company limit** (2026-10-15); bear on interior walls too; hidden roof: on the ring, inside, against the modules (4b); the false ceiling hangs below (§5) |
| Ceiling beams past 8 m (TV D2503) | glulam 200×100 "lameladas 20x10" at 0,915 (19 bays over 17,39 between the end walls' axes) | TV main block 8,50 / wing 11,00, cut from 13,5 / 12 m stock; ceiling ≈ 0,15 under them; rev. C 2025-07-29 "Cobertura - Vigas de 16x8 para 20x10"; glulam because > 8 m (ours) |
| Exposed ceiling beams (à vista) | glulam 200×100 at 1,02 | 3_Vigamento single-storey part (§2a) |
| Floor joists | 22×7,5 at ≈ 0,61 (0,614); 0,50 over ≈ 4,8 m free; 0,466 beside the stair | §2a, §5 |
| Vigas de apoio à cobertura (madres, purlins) | 110×75 | exposed roofs ≤ 1,2 m apart (3_Vigamento 0,89); hidden roof (TV): **standing on edge**, ≈ 1,26 apart from each gutter, ridge pair ("madres de cumeeira") 0,10 apart, pieces ≤ 3,66 (4 bays) jointed on a lamelada |
| Ridge madres over the TV wing | 22×7,5 | "então é como estão no desenho com 22x7,5" (2026-10-16, night); when the company uses them: promise (7); the builder's trigger "lamelada > 9 m" is ours (JSON `estrutura.madres.cumeeira_vao_longo.lamelada_min` 9,0) |
| Porch beam and pillars (3_Vigamento) | glulam 200×100 | beam 6,00 m; "Pilares 20x10 lameladas", 2,52 high |
| Verga of wide openings | 22×7,5 | from ≈ 2,8–3 m (above) |
| Caleira oculta (hidden gutter) | 2 × 110×75 (one upright, one flat) + OSB 22, 30 cm wide + 10 cm on the roof side (draft) | §6 Hidden roof |

### 2a. Base framing sheet "3_Vigamento" (user 2026-10-15)
`fontes/vigamento-base/3_Vigamento.pdf`, another DiscoverCasa house ("tens aqui um documento que representa bem o nosso
vigamento base !! este não é o mesmo projeto mas é para perceberes como operamos"). House: ground floor 4,75 × ≈ 24 m
(one side 4×5,10 + 2,68 + 0,90, the other 2,68 + 3×5,10 — an open porch), Piso 1 4,75 × (2×5,10 + 1,505) over the last
≈ 11,7 m. Readings are ours unless quoted.
- **Floor joists** ("vigas de apoio ao teto Piso R.C (0,22x0,075) maciças"): solid 22×7,5 at **0,614–0,615**
  (continuous over a lengthwise interior wall — two spans of ≈ 2,4 m); **0,50** (last bay 0,55) over **≈ 4,8 m free**
  (porch, from the wall to a glulam beam); **0,466** beside the stair. No central / main beam ("vigamento normal").
- **Stair opening** ("ZONA ESCADAS" 3,478 × 2,605): a trimmer 1 × 2,163 across the joists + 3 short joists × 1,273 at
  0,466.
- **Vigas de amarração 11×7,5** on the exterior walls of **both** floors; the ground-floor ones also under Piso 1 → the
  Piso 1 joists sit on an amarração on the ground-floor walls (ours; OPEN, asked 2026-10-15 for Sobral). None on the
  interior walls; no afinação in the table.
- **Exposed ceiling** of the single-storey part: "vigas de apoio ao teto Piso R.C (0,20x0,10) lameladas", "Vigamento à
  vista", glulam 20×10 at **1,02** (11 × 4,90 + 1 × 6,00 + "lameladas (rés chão até ao Piso 1) = 5x7,00").
- **Ceiling beams of Piso 1**: 22×7,5 maciças, 10 × 4,90 at **0,989** (= the "1 m" of §6).
- **Purlins** ("vigas de apoio à cobertura … (0,11x0,075) maciças") lengthwise at **0,89**, 4 lines per roof in 2 pieces.
- **Porch**: glulam beam 20×10, 6,00 m, on "Pilares 20x10 lameladas" (5 × 2,52).
- **"Caleira interior com 2 tubos de queda"**, 20 cm, along one long side of each roof (draft caleira oculta: 30 + 10 cm
  — width per project? OPEN).
- OPEN: "Total Vigas lameladas 16x8 com 7,00m do Piso R.C até ao Piso 1 = 10 un" and the 5 × 7,00 "lameladas (rés chão
  até ao Piso 1)" — what they are (16x8 glulam is a company section: TV had it before revision C).
- ⚠ (keeper 2026-10-15): (1) joists over ≈ 4,8 m at 0,50 and the wall-to-wall joisting rough-checked only (Sobral
  `revisao-tecnica.md` #6) — engineer per house; (2) exterior glulam pillars (use class 3) on steel post bases keeping the
  end grain off the slab, ≥ ≈ 15 cm above the outside ground (termites, `construcao-madeira.md` §2, §4), beam ends
  protected from rain; (3) under an exposed ceiling the boards, vapour control and wool go on top of the beams (warm side
  down), sealed at the walls — how they do it: OPEN; (4) an interior gutter over the house needs an overflow and a
  membrane under it; (5) Piso 1 over an open porch is an exterior floor: thermal-project insulation, airtightness and a
  closed, ventilated soffit with insect mesh.

### 2b. Wall modules as built — D2503 Módulos (TV, user 2026-10-16)
`Construção Torres Vedras/desenhos/250828_D2503_Modulos.dwfx` ("o ficheiro original de como os módulos foram feitos …
quero que percebas o porquê do tamanho de cada módulo"); full reading in TV `docs/modulos-D2503.md` (27 exterior, 23
interior modules). Read as the company's module standard (one house — ours, unless marked confirmed):
1. **Height**: exterior **3,50** in one piece base → parapet top (studs 3,43 + plates; the rule for every hidden roof,
   §2); interior **2,53** (studs 2,46) vs the rule 2,543 — OPEN. The roof set gives the parapet top 3,4915 (8,5 mm
   less than 3,50) — which is right: OPEN.
2. **Stud grid**: plain modules are whole bays + the last stud: exterior **2,21 = 5 bays**, interior **1,78 = 4** and
   **2,65 = 6**. Why (ours): every stud on the grid, predictable OSB / Pladur joints and services, the same jigs. Why 5
   outside and 4 / 6 inside: OPEN (the tentative "transport width" answer of 2026-10-19 — "não estou a ver qual é o
   módulo 2,21 mas diria que sim" — lost its ground when exterior modules may reach 3 m, 2026-10-20).
3. **Length**: factory ≤ 2,64 exterior / 2,72 interior at TV; longer = built on site (M1 3,82 with the garage door);
   two wide openings side by side split at the pier (2,15 + 0,32 + 2,15). Rules now: §2 Module size — length.
4. **Openings**: each inside **one** module, sized round it (opening + two 11×7,5 jambs + margins; 2,15 = 2,00 + two
   11×7,5); jambs full height, lintel 11×7,5 (sill for windows), cripples on the grid. TV rough openings (bigger than
   the architect's): **janelas de correr 2,00 × 2,40** (with the estore box); **garage 3,00 × 2,20** (11×7,5 lintel —
   the engineer's exception, §2); **entrance M5 on P03 1,04 × 2,20**; **despensa door M23 on P11 0,94 × 2,20**; kitchen
   1,50 × 0,95; WC 0,75 × 0,75; P12 0,75 × 0,95; window sills ≈ 1,03–1,04; **interior doors 0,87 × 2,03**. Confirmed:
   the entrance "é uma porta maior e mais robusta que cabe naquele espaço" (fills 1,04, not the table's 0,90 — 2026-10-19);
   M23 "sim coloca a encher o vão como na principal" (fills 0,94 — 2026-10-20); the basculantes "está ótimo como
   fizeste" (0,73, D2503's 0,75 wins over the table's 0,80). Rough-opening rule: §3b.
5. **Escadas**: where another wall meets, **4 noggings** (11×3,5 / 7,5×3,5) **at 0,66** between two studs of the
   receiving module (fixing for the abutting module — ours).
6. **Corners**: one wall runs through (11×7,5 at its end), the other abuts on its own 11×7,5 — confirmed "sim e é suposto
   ser assim a lógica sempre, não temos uma regra específica para isso" (2026-10-19) → which one: per house (ours). TV:
   P11 at both its corners, P03 at the west and re-entrant corners, P01 at SE, but P14 at the wing's SW (stops 0,035
   short of P03's inner face). Suggestion (ours): a generator default the user can override — the walls carrying the
   ceiling beams run through, the gables abut, or whichever keeps whole-bay modules; draw the choice.
7. **Interior walls** run between the exterior walls' inner faces, on the plan's centre lines (± 1 cm).
8. **Sections**: exterior 11×3,5 (studs, plates, cripples, noggings) and 11×7,5 (corners, jambs, lintels, sills);
   interior 7,5×3,5 and 7,5×11 (the 11×7,5 turned). Cut lists ("COMPRIMENTO DAS VIGAS") in `modulos-D2503.md`.
- D2503 replaced the builder's v4 assumptions (2026-10-16): 3 m modules filling the walls, long modules over two
  openings, "X walls through" at every corner, the architect's opening sizes, a 22×7,5 garage lintel, no escadas, a
  separate parapet module (TV `docs/modulos-D2503.md`).

### 2c. Production drawings — the D2503 set (the format for every new project)
User 2026-10-16: "quero que sejas capaz de desenvolver um documento igual ou do género desse dos módulos e da cobertura
independemente do projeto … de forma a podermos modelar a casa sem erros e já como irá ficar no fim da construção"
(`discovercasa.md` Product vision 1). Format as TV D2503 (title block DISCOVERCASA, obra, Moradia / Habitação,
revisions A "Dimensões para execução" … E "Cobertura e Módulos - Correção para produção"):
- **Módulos** — 2 A1 sheets "Módulos Exteriores" / "Módulos Interiores", "Sem Escala": the plan with every module in
  section (black rectangle = length × 0,11 / 0,075), labelled M1, M2 … in blue; each module's elevation beside the plan
  (N and S upright, W and E turned 90°), total width dimensioned; black outline = 11×3,5 / 7,5×3,5, red hatched =
  11×7,5 / 7,5×11; "CONSIDERAÇÕES GERAIS" (40 cm clear not dimensioned, irregular spacings dimensioned, corner detail);
  "QUADRO DE DIMENSÕES E QUANTIDADES" (L × A, reference, V = door/window, P = door, "* Painel a executar em obra");
  "COMPRIMENTO DAS VIGAS" (cut list).
- **Cobertura** — 5 A3 sheets: 1 "Lameladas horizontais e amarração"; 2 "Madres (Pendentes) - Esquema geral" (gutter
  falls); 3 "Madres (Pendente) - Posicionamento"; 4 the panels ("telhas", ridge caps to order); 5 "Secções tipo" 1:50 +
  "pormenor caleira/algeroz". Legend: "Dimensão da fundação e módulos", "Dimensões ao eixo", "Dimensões de espaçamento",
  "Linhas de pronto", Módulos, Amarrações (TV `docs/cobertura-D2503.md`).
- **The generator** (built 2026-10-20 — "começa a preparar o método de geração dos documentos que falamos e gera-os,
  quero também que incluas um documento com a listagem de material"): `ferramentas/documentos/gerar.py` writes from the
  model `<obra>_Modulos.pdf`, `<obra>_Cobertura.pdf` and `<obra>_Listagem_Material.pdf` + `.csv` (by chapter, purchase
  units, caixilharia, cut list); `ferramentas/modelo/modulos_dc.py` reads a module drawing. First run: TV
  (`Construção Torres Vedras/documentos/D2503_*`; v6.4 = the members drawn in D2503, 228 / 207, D2503's own table 220 /
  199). **The user's review (2026-10-20 night): the Módulos "está absolutamente correto"**; the Cobertura and the
  Listagem: not reviewed ("ok assim o farei"); the list's format, units, suppliers and prices: not said ("Isso é um
  passo futuro").
- ⚠ (keeper): (1) the caixilharia lines must say which size they give — the approved table's (nominal) or the frame to
  order (opening − 2 × 0,025) (§3b, TV #20); (2) the hidden-gutter outlets and downpipe crossings through the parapet
  modules should appear on the module elevations, so the studs are set clear of them; (3) assumed items (pergola
  sections, remates, tiles) marked "a confirmar".

## 3. Exterior walls, outside (from the structure outwards)
1. **OSB3 9 mm** all round (sheets 2500×1250), 45 mm drywall screws.
2. **Rothoblaas TRASPIR 95** (code T95): 3-layer PP breathable membrane, 95 g/m², 0,4 mm, Sd 0,02 m, W1 (EN 1928), 3
   months UV; roll 1,5 × 50 m (75 m²); walls only. Laps ≥ 15 cm (DiscoverCasa: 20 cm), tapes Flexy / Speedy / Easy Band;
   galvanised staples. TV site photos (2026-10-16, 2026-10-19): a **HOLZ TECHNIC** membrane printed "TRASPIR HOUSE 95",
   "CE EN 13859-1/2" on the walls and rothoblaas on the top band — read as a Traspir-family membrane under a
   distributor's logo (ours); its data sheet and why two: OPEN (TV `revisao-tecnica.md` #18).
3. **Finish — the client's choice** (the three done most):
   - **A. Wood (Tremolo) — the standard** (confirmed 2026-10-15/16): "Tremolo fica na vertical como é o nosso padrão e o
     ripado na horizontal"; "o 3,75x3,5 é o nosso padrão" → **Tremolo vertical** on **horizontal battens 37,5×35** ripped
     from 75×35 (≈ 36 × 35 after the cut; TV: "dividimos essas vigas em duas pela vertical"); **every 35 cm from the
     bottom up** — "O ripado deve ser aplicado de 35 em 35 cm. Como podes ver na foto real da obra o ripado é aplicado de
     baixo para cima e depois de 35 em 35 cm" (2026-10-16; was 50 cm 2026-10-15; draft 35 cm). Centres or clear: OPEN.
     Cladding **Piveteau TREMOLO Douglas** (French Douglas fir, autoclave class 3.2, "marron"), tongue and groove 22 mm ×
     135 mm useful × 4 m; fixing Turbosharp 4×50 torx; finish wax nº 55 + Velatura Nogueira (Froschemie). Battens' wood
     and treatment: OPEN.
     - **Contra-ripado**: the user's rule of 2026-09-24 — "we do a slatted against slatted with 30x20mm … so the zone
       between tgem is a breathable zone" (draft: 30×20 casquinha, 35 cm). TV: "Nesta casa só levou ripado na horizontal
       e não levou o contra-ripado" (TV's config has none). The standard keeps the vertical contra-ripado (tools: 30×20
       at 0,35 — assumed); when a house gets it, its section and spacing: OPEN. ⚠ Vertical boards on horizontal battens
       alone close the cavity into horizontal bays (no air rising, water resting on the batten tops) → contra-ripado or
       gapped / notched battens (`construcao-madeira.md` §2; TV `revisao-tecnica.md` #3).
     - **Battens round every opening and at corners** (confirmed 2026-10-16): "o ripado nos vãos tem sempre de contornar
       os vãos"; "quando a janela não vai até ao chão leva em cima e em baixo"; "todos os vão são rodeados por ripado
       tirando quando estao em contacto com o chão"; "os cantos exteriores também levam um ripado na vertical em todos os
       cantos de ambos os lados" → every opening framed on all sides except the side on the floor; a vertical batten at
       every exterior corner on both faces. ⚠ Leave 10–20 mm gaps where horizontal battens meet vertical ones and at the
       ends of head battens (drainage, air) (TV #3, #14: a head flashing with a drip over every opening).
     - TV as built: "paredes exteriores são em tremolo no revestimento exterior", the rest the standard build-up.
   - **B. ETICS ("capoto")**: insulation boards (DiscoverCasa uses XPS; thickness from the thermal project — Sobral
     section ≈ 60 mm), plate fixings, reinforcing mesh, corner beads, base coat, paint; usually **white**.
     ⚠ (2026-09-24) XPS (μ ≈ 80–250; 60 mm → Sd ≈ 6–9 m) on the cold side of the frame, with a more open inside
     (OSB 15 + Pladur Sd ≈ 1–3 m), reverses "tighter inside than outside" → condensation risk at the outer OSB: an
     EN ISO 13788 (Glaser) check by the thermal engineer, or a vapour-open ETICS board for timber frames (EAD
     040089-00-0404: wood fibre, mineral wool, cork ICB) with the same white render, and/or the OSB 15 as the inner
     vapour control (taped joints, airtight boxes). XPS or a vapour-open board: OPEN.
   - **C. Cork**: expanded cork agglomerate **60 mm, 1000×500** (e.g. Amorim MDFachada: 140 kg/m³, λ 0,043, 40–200 mm)
     on 30×20 battens + counter-battens (ventilated); Amorim glues the boards directly, DiscoverCasa uses the ventilated
     battens. Whether cork keeps the 30×20 + contra-ripado: OPEN.
   - Other finishes on request (stone, …).

### 3b. Windows, exterior doors, garage door (caixilharia)
- Company (website): aluminium with thermal break and double glazing, PVC optional (`discovercasa.md`).
- **The standard "para já"** (confirmed 2026-10-19, 18:12): "São o nosso padrão para já mas estamos a pensar mudar quando
  o fizermos eu aviso-te" → **RAL 7016 cinza rato**, **automatic exterior shutters** (where an item has one), **painel
  liso doors** — may change, he will say (promise (1)). The sectional garage door was not in the question.
- **TV approved table** ("PROJETO APROVADO", 2026-10-19, `Construção Torres Vedras/docs/revisao-modelo/2026-10-19_projeto_aprovado_vaos.png`;
  per module in TV `docs/materiais.md`): "alumínio lacado … e rotura térmica" + "vidro duplo térmico transparente"
  (fosco in the WCs); "Basculante" (despensa, WCs, 0,8 × 0,8), "Vidro fixo" (cozinha 1,5 × 0,8), "Janela de correr 2
  folhas" (quartos, sala, 2 × 2,2); exterior doors "Painel liso em alumínio lacado de cor cinza rato com rotura térmica.
  (a escolher de acordo com o catálogo)" 0,8 / 0,9 × 2,2, "Abertura para a direita"; "Portão de garagem seccionado
  automatico" 3 × 2,2, "Abertura para cima"; "Estore exterior automático" on 6 of 11 (the windows and janelas de correr
  of quartos, sala and cozinha, the despensa basculante); 11 items, 31,06 m². In D2503 the box sits inside the rough
  opening above the window (+ 0,15 / + 0,20).
- **Doors never take an estore — only windows** (confirmed 2026-10-27): "Prtas não tem estore apenas as janelas" → no
  shutter on any porta nor the portão; a box only over windows (janelas, janelas de correr, vidro fixo, basculantes) —
  not on every window (TV WC basculantes: none; which ones per project, PO Q12). Say **janela de correr / sliding
  window**, his and the table's word (our docs said "sliding doors" until 2026-10-27). OPEN, low priority: a hinged glazed
  door to a terrace (porta-janela de batente) — window (estore) or door?
- **Sliding windows of 3 and 4 leaves** (confirmed 2026-10-22): "quero que cries opções de janelas de correr mas 3
  janelas e 4 janelas" (read as leaves — ours); over 3 m the 22×7,5 verga. Sizes, heights, estore, which leaves slide:
  OPEN.
- **Rough opening = frame + clearance** (confirmed): "acho que é apenas a medida do caixilho sem folga mas normalmente
  contamos com a folga" (2026-10-19, on the approved table); "Depende do caixilho mas normalmente 2 ,5 cm de cada lado,
  mas isto são pormenores que depois te posso dar dependendo da obra senão vai com o default de 2,5 cm" (2026-10-20);
  in height too — "Sim mas nem sempre é essa a folga lá está depende da caixilharia..." (2026-10-20, 13:25) → **2,5 cm
  each side, the company default** (JSON `caixilharia.folga` 0,025), per project when it differs (promise (3)). New
  project: width = the frame from the maker's order + 0,05; height = frame + 0,025 head + 0,025 under a window (none
  under a door to the floor — ours) + the estore box where there is one. Interior doors differ (+ 3 cm top, + 3,5 cm each
  side, §2). ⚠ TV: with the default clearance the approved table fits D2503's openings only for the two doors in width
  (janelas de correr, vidro fixo, garage: no room; basculantes 5 cm too wide / tall; doors and garage: no head room) →
  at TV the frames were made to the openings or there was no clearance (TV `revisao-tecnica.md` #20); the user's reply:
  pending.
- **Remates round every opening — the rule** (confirmed 2026-10-20, 13:25): "Todos os vão levam remates a volta da
  caixilharia de forma as diferentes camadas das nossas paredes não ficarem expostas, anota isto também". Material,
  colour, profile, sill / threshold, inside too: OPEN (per project). Model (TV v6.3, assumed; JSON
  `caixilharia.remates`): outside folded aluminium RAL 7016 (reveal to the Tremolo face, return over the clearance, 3 cm
  flange, a sill with a 3 cm drip under windows not reaching the floor); inside a 13 mm reveal lining (Pladur). TV photos
  (2026-10-20): dark surrounds on the windows, a light one on the garage door, light pieces under the east janelas de
  correr (thresholds — ours).
  ⚠ (keeper, general practice, `construcao-madeira.md` §4; TV #23): (1) the remate is the trim, not the seal — the gap
  sealed in three planes (pre-compressed tape outside, foam, airtight tape to the OSB 15 inside), the Traspir turned into
  the reveal and taped; (2) a head flashing with a drip over the head remate, lapped under the Traspir above; jamb
  remates over the sill's ends; (3) sills with an upstand, end dams at both jambs, a fall outward, drip ≥ ≈ 30 mm off the
  cladding; (4) every opening to the floor needs a threshold (soleira) with a fall and a tray (TV deck 2 cm under the
  floor, #5); (5) aluminium against copper-treated battens: separating tape, compatible screws; (6) flanges must not close
  the cavity vents; (7) H1 board or tiles in wet rooms' reveals; keep the shutter box's service access.
- ⚠ (keeper 2026-10-19): (1) the shutter box is the façade's weak point — insulated monobloco / compacto box, taped
  airtight to the OSB 15, the Traspir lapped over its head, a head flashing with a drip (TV #14, #20); (2) an outward
  basculante cannot open with the estore down (TV despensa); (3) with an accessibility plan the entrance "0,9" should be
  the clear passage (DL 163/2006: ≥ 0,77 doors, ≥ 0,87 building entrances — which applies: to check); (4) a sectional
  garage door needs headroom for shaft and springs (TV 2,20 → ceiling 2,50, ≈ 0,30) and fixings into jambs and lintel.

### 3c. Pergolas (TV as built, user 2026-10-19 / 2026-10-20)
Whether a house has a pergola, its extent, covering, gutter and fixing: **per project** (`perguntas-por-obra.md`). TV
(TV `revisao-tecnica.md` #21, #22; photos `Construção Torres Vedras/docs/revisao-modelo/2026-10-19_obra_pergola_*.webp`,
`…/2026-10-20_final_1…4_*.webp`):
- **Separate structure**: "neste caso a pérgola foi feita independentemente" — its own beams on posts at the front and,
  at the house, on a ledger fixed to the façade over the horizontal battens (photo; Tremolo cut round it).
- **Fixing varies**: "neste caso acho que foi aparafusado … mas nem sempre usamos esse método"; "quando for relevante nas
  pérgolas eu dou-te essa informação" (promise (2)).
- **Wood**: lameladas (glulam), autoclave treatment; "como estão no exterior levam um tratamento especial não me relembro
  do nome" (name: OPEN — the supplier's invoice would give it); pale timber in the photos (colourless treatment — ours).
- **As finished**: "a pérgola vai até ao comprimento total da casa e leva telha e uma caleira à vista em todo o
  comprimento" (2026-10-20); "É cerâmica" (ceramic tiles); "Um no lado oposto ao que se vê na foto" (2 downpipes: down the
  post at the wing's west face and, ours, the east corner post). From the photos (ours): from just east of the garage
  (the garage door not covered) to the east end (model v6.3 x 3,63 … 17,57), 6 posts, a timber deck under it. Model
  height "ótima"; its sections (posts 16×16, beams 16×16, ledger 7,5×16, slats 7×3 at 0,15) "não sei ao certo mas
  parecem estar ótimas" — unconfirmed. Slope (model 15 %), what is under the tiles, tile battens, gutter section, the
  downpipes' feet: OPEN.
- ⚠ (keeper, `construcao-madeira.md` §4): ceramic tiles usually want ≥ ≈ 30 %; the façade leaves ≈ 18 % in front of P03
  → a continuous waterproof sub-roof (subtelha / boards + membrane) or another slope — ask; tile battens at the tile's
  gauge (≈ 0,3–0,4), not slats at 0,15; clay ≈ 0,4–0,6 kN/m² plus wind uplift on a structure open on three sides →
  sections, ledger screws and post hold-downs by the engineer; an abutment flashing (rufo de encosto) up behind the
  Traspir, Tremolo ≈ 50 mm clear with sealed end grain, beam ends 10–20 mm off the façade, every screw through the
  Traspir sealed, structural screws into studs or the ring (sized for bending across the batten gap); post bases keeping
  the end grain ≥ ≈ 150 mm off the deck (termites); the gutter with a fall (≈ 23 m² per downpipe → ø80 enough, ≈ 1 cm²
  per m²; DR 23/95, EN 12056-3), the downpipe feet into a drain or gully, not onto the deck by the wall; a tiled roof
  along the house is covered area (telas finais / municipal limits; less daylight); a glulam treated after gluing with a
  water-borne product can check — ask the supplier.

## 4. Walls, inside
1. **Mineral wool** between the studs: **Volcalis COMFORT**, **80 mm in exterior walls, 60 mm in interior walls**
   (confirmed 2026-10-09; glass wool roll, λ 0,037, A1, widths 400 / 600; plain 50/60/70/90/100 → R 1,35/1,60/1,85/2,40/
   2,70 m²K/W; black-veil 50–120). Pushed against the outer OSB, leaving a service gap inside (30 mm in 110 walls,
   15 mm in 75 walls) — enough: "our walls serve perfectly for our pipes and connections we have been doing it this
   way", pipes "can go tuck in the mineral wool" (2026-10-09). Boxes in exterior walls pierce the OSB 15 → airtight
   boxes. **Ceilings / roofs: 100 mm Volcalis** ("we use 100mm mineral wool volcalis on the roofs aswell"), laid on the
   top-floor false ceiling between the ceiling beams — "like you modelled" (2026-10-09). Between floors: §5.
2. **OSB3 15 mm** all round: inner face of exterior walls and both faces of interior walls.
3. **Finish — the client's choice, every inner face, exterior walls included** (confirmed 2026-10-22): "Sim até porque
   como já sabes o nosso acabamento padrão nessas faces interiores é gesso cartonado mas também inclui opções de madeira,
   cerâmica etc." → standard **Pladur (gesso cartonado)** 12,5 mm "13": N standard, **H1 hidrófugo** in wet rooms, **F
   ignífugo** near heat; options wood (vertical boards on battens + counter-battens, horizontal boards on battens only —
   ventilated: "slatted against slatted if it it vertical wood or just slatted if it is horizontal wood to create the
   breathable box", 2026-09-24), ceramic, others. Joint compound per 100 m² ≈ 2 bags 1H + 1,5 bags 24H, paper tape,
   corner beads. Promise (8): "Mias tarde vou ter fornecer uma lista de materiais para acabamentos interiores".
   ⚠ (ours) On an exterior wall the OSB 15 is the airtight / vapour layer: battens, boxes and fixings through it sealed.

## 5. Floors and ceilings
- **Floor finish per room** (confirmed 2026-10-22): "a pessoa pode aplicar pavimento que desejar na divisão que desejar e
  não ter que aplicar ou cerâmico ou vinil na casa toda" — usually **vinyl plank**.
- **Ground floor** (2026-10-09, "when is just one floor"): **vinyl straight on the foundation base** — the DiscoverCasa
  base (TV: "Pavimento sobre a nossa base de fundação", 2026-10-15 — not the architect's slab on void formers). The base
  itself: "base de fundação eu explicarei mais tarde" (2026-10-13, promise); "uma laje representativa para já não tem
  mal" (2026-10-20 night). (The Sobral drawings' build-up — microcimento, betonilha, XPS 6 cm, geotêxtil, massame 15 cm,
  filme, betão de limpeza 5 cm, brita 30 cm — is not the method, Sobral `revisao-tecnica.md` #24.) ⚠ Level of the base vs
  the outside ground / deck (TV deck 117,48, floor 117,50; rule ≥ 150 mm, `construcao-madeira.md` §2) — TV #5.
- **Two storeys**: "emtermos de paredes nada muda" (2026-10-20 night) — wall modules the same on both storeys.
- **Floor between storeys** (confirmed 2026-10-09 / 10-13 / 10-15): joists **22×7,5** on edge at **≈ 0,61** (0,50 over
  ≈ 4,8 m free spans, 0,466 beside the stair — 3_Vigamento, §2a) → **11×7,5 laid flat, perpendicular, at 60 cm centre
  to centre** ("vai com 11x7,5 a 60 cm de distância"; "sao medidos em eixo"; ≈ 1,7 m per m²) → **100 mm mineral wool
  between the joists** ("fica entre as vigas e sim já o tinhamos definido") → **OSB 22** → vinyl. Depth ≈ 220 + 75 + 22
  + vinyl. Sometimes glulam joists, sometimes exposed ("you can see them on the roof"). The wool's height in the bay:
  OPEN (model: on the false ceiling below). A board / layer under the vinyl on the OSB: not said.
  - **Large rooms with no wall below**: "leva o teto falso e o vigamento normal de 22x7,5 e 11x7,5 nada muda"
    (2026-10-15, Sobral living room) — no special beam. ⚠ Long free spans (Sobral Tipo 1 ≈ 4,7 m) at ≈ 0,61 are marginal
    in deflection → 0,50 as in §2a (asked for Sobral) — engineer (Sobral `revisao-tecnica.md` #6).
  - **Upper walls stand on the floor OSB 22** ("sim", 2026-10-15) — platform framing; check a joist or batten under
    every loaded upper wall (engineer).
  - **No rim joist** at the joist ends ("não", 2026-10-15); what closes the joist bays at the façade: OPEN (Sobral #24).
- **Ceilings — teto falso** (confirmed 2026-09-30 / 10-09, photos `fontes/fotos-teto-cobertura/2_…`, products
  `fontes/produtos-teto/`): flat at the level of the amarração (it does not follow the roof); **steel** ("steel those are
  the ones we use" — was "aluminium" earlier, 2026-10-09):
  1. **Cantoneiras 3 × 3 cm** screwed round the perimeter of each room, fixed 3 m bars (Leroy Merlin ref. 15953000
     "Perfil cantoneira 30x30x0,5 mm 3 mm Pertecno", 1,39 € on 2026-10-09);
  2. **Calhas / réguas de suspensão** — notched strips fixed **vertically** to the ceiling beams (under a floor: to the
     joists);
  3. **Perfis de teto** hung on the réguas, resting on the cantoneira at the walls; Pladur (or wood) below;
  4. **Perforated angle** "only on hard corners" = outside corners ("yes that is what i mean"); what it does (hanger or
     corner bead): OPEN.
  Assumed: perfil 47×17 at 0,40, régua model and length, bar lengths.
  - **Hidden roof on 22×7,5 — the ceiling below the ring** (confirmed 2026-10-21): "Sim como já te tinha explicado nos
    chats anteriores os tetos falsos ficam presos as vigas de 22x7,5 através dos perfis de teto e das calhas de suspensão
    que até cheguei a mandar foto delas" (model suspension 0,1185 under the beams, `tetos.suspensao.folga`).
  - The false ceiling comes with the roof (§6).

## 6. Roof — structure and sandwich panels
Structure (confirmed 2026-09-30 / 10-09; photos `fontes/fotos-teto-cobertura/1_`, `3_`, `4_`):
1. **Vigas de amarração** 110×75 on the exterior walls all round (hidden roof: the inner ring, §2).
2. **Vigas de apoio ao teto 22×7,5** of casquinha branca, **1 m apart** (3_Vigamento 0,989; glulam 20×10 at 1,02 where
   the ceiling is à vista), "sempre inseridos no sentido da cobertura" = down the slope, eave wall to eave wall, on the
   amarração and the afinação interior — "always follow this logic unless told otherwise" (2026-10-09). Loads on
   interior walls: "if there is a decharge or a high load it is discharged on the wall entirely and not only on one
   structural beam"; they bear on the interior walls they cross (2026-10-19, §2). **Maximum free span 8 m**: "O nosso
   limite é precisamente 8 metros portanto tranquilo, nós sabemos que assim não irá ceder" (2026-10-15); past 8 m TV used
   glulam 20×10 at 0,915 (§2 table). ⚠ A rough EC5 check puts 8 m with the roof on prumos at the bending limit and the
   long-term sag over the usual limits → engineer per house (TV `revisao-tecnica.md` #6).
3. **Prumos** (vertical posts) standing on the ceiling beams, screwed to the purlins, "para dar a inclinação pretendida
   ao teto" (the roof slope; the ceiling is flat); one on every ceiling beam under every purlin ("the prumos are right").
   Section: assumed 110×75 — OPEN.
4. **Vigas de apoio à cobertura** (purlins / madres) 110×75 parallel to the ridge on the prumos, "que dão a inclinação
   da cobertura"; the panels are fixed to them; ≤ 1,2 m apart (Sobral 4 per slope; 3_Vigamento 0,89). Hidden roof (TV):
   on edge at ≈ 1,26 (§2 table).
5. **Gable ends (empenas)**: a framed triangle standing on the tie beam ("its fine like that", Sobral).

### Covering — always a sandwich panel
- **Always sandwich panel; telha only at a client's request** (confirmed 2026-10-21): "Nós usamos sempre painel sandwich
  a não ser que seja um pedido do cliente não usar painel sandwich e usar telha por exemplo mas para já vamos deixar no
  DiscovercasaBuilder apenas o painel sandwich como opção". A tiled house roof (later) needs its own build-up: tile
  battens + counter-battens, a sub-roof, the tile's slope (clay ≥ ≈ 30 % without a continuous sub-roof), its weight on
  the structure — OPEN.
- **Exposed roof (cobertura à vista)**:
  - **Panel = Munditelha® (Mundiperfil)** (confirmed 2026-10-22): "Sim exatamente, utilizamos o munditelha da mundiperfil
    tal como no segundo screenshot" — "PAINEL COBERTURA EM POLIURETANO (PUR ou PIR) — PAINEL MUNDITELHA® (Com chapa de Aço
    ou Alumínio lacada) — ESPESSURAS MÉDIAS: 40 - 60 mm", useful width **1000**, wave pitch **200**, relief **45** (mm),
    CE. Thickness (40 provisional), PUR / PIR, steel / aluminium, colour (dark grey / RAL 7016 provisional): OPEN; from
    the data sheet still to read: minimum slope, purlin span, overhang. Model change: JSON `cobertura.painel` relief
    0,035 → 0,045, pitch 0,35 → 0,20. (Draft list "Cobertura à vista": tile-effect panel, ridge piece, sealing tape,
    remates, Turbosharp 6×160, external gutter and downpipes. TV's architect also named Mundiperfil.)
  - **Minimum slope 15 %** (≈ 8,5°; confirmed 2026-10-21): "A inclinação mínima da cobertura à vista é 15 %." — exposed
    roofs only; above it the client's choice by the look ("Depende do aspeto que o cliente queira"). A laró / rincão at a
    90° corner falls at 15 ÷ √2 ≈ 10,6 % (≈ 6,1°) — the panel's minimum on its face and the laró pieces at ≈ 10,6 % are
    the maker's to confirm (ours). A design at exactly the minimum keeps no margin (ours). Configurator: slope in % (15 %
    default, up to 100 %), degrees shown beside.
  - **Rectangle: 2 águas with empenas** — "por regra geral definir o de 2 águas" (2026-10-21). **L / T / U: "várias
    águas"** usually — "nas casas em T,L ou U normalmente usamos várias águas penso que seja a forma mais fácil de ajustar
    os nossos telhados aos diferentes shapes" (2026-10-21); "Nas casas com cobertura á vista é que normalmente fazemos
    duas ou mais águas pelo aspeto tradicional" (2026-10-28) — exposed roofs are the less common case (Hidden roof below).
    Configurator options now (2026-10-28, "Deixa duas águas e
    várias águas apenas com empenas á vista"): rectangle — Escondida · "Duas águas, com empenas à vista"; L / T / U —
    Escondida · "Duas águas, com empenas à vista" ("Quero também com duas águas e depois várias águas", 2026-10-27) ·
    "Várias águas, com empenas à vista" (= the engine's **misto**: main body hipped, wings' ends gables — ours, not
    objected). Removed 2026-10-28: "Quatro águas, sem empenas à vista" (4 águas was offered as an option 2026-10-21 —
    "podemos dar a opção de escolha … sendo que 4 águas fica mais dispendioso não?") and "Várias águas, sem empenas à
    vista"; the engine keeps `quatro_aguas`, not offered. **Misto kept** — told that on his U it is asymmetric (one arm
    hipped as a pyramid, the other gabled): "Tranquilo depois se necessário removemos essa opção" (2026-10-28) — confirmed
    for now. Still OPEN (ours, not asked): "duas águas" on an L as one ridge / two planes (his "Sim é de duas águas" for
    TV's L hidden roof) and a cross-gabled "várias águas" without rincões → ask with the cards' images if misto is
    removed; the default card on an L / T / U (the configurator opens on Escondida). Sobral = his
    exposed-roof example (Tipo 1, two águas with empenas at 26,4°, `Construção Sobral/CLAUDE.md`).
  - Our opinion given 2026-10-21 (hip roof on L / T / U, with cautions: laró slope ÷ √2, bias-cut panels ≈ +10–15 %, the
    ridge rising with the width) → "Obrigado pelo insight depois grava junto com uma lista de insights" (`insights.md`);
    on the ridge height: "Isso é tranquilo, don´t worry mas anota na mesma" (check the cércea per house — ours).
  - **Beirado (eaves overhang)**: 0,25 (as Sobral) = the default — "Sim pode ficar mas lá está isso vai depender de
    outras condicionantes e do que o cliente desejar mas podes usar isso como default" (2026-10-21); **range 0,20–0,50** —
    minimum "O mínimo de beirado possível é 20 cm" (2026-10-22); **maximum 0,50** (confirmed 2026-10-28, after our point
    that at 0,55 a rincão's tail runs ≈ 0,8 m free): "Beirado vamos definir um máximo de 50 cm se vires que é problemático
    em algum dos modelos podemos dimnuir nesse modelo" → a lower maximum per house / model allowed when a model shows a
    problem (the 0,55 of 2026-10-22 "o máximo é 55cm" superseded 2026-10-28, see registo). At 0,50 the rincão / laró tail
    ≈ 0,50 × √2 ≈ 0,71 (ours, arithmetic). Verge overhang 0,12 (Sobral) below 0,20 if the range covers verges: OPEN;
    measured from the frame or the façade: OPEN; 0,50 = a panel cantilever → Munditelha's table.
  - **Where a wing opens into the body**: "normalmente nós utilizamos um estribo de asa externa que é neste caso onde as
    vigas da cobertura realizam a sua descarga" (2026-10-22) → **external-flange joist hangers** (as Esteba "estribo alas
    exteriores tipo B", galvanised, U seat, two outward flanges); fixed to **the header along the open side, wall to
    wall** — "Prendem-se as vigas laranja" (2026-10-28, on the sketch `configurador/docs/juncao_ala_estribos.svg`, glulam
    20×10 "viga de bordadura") — confirmed. Header section and end bearings: ours, per house. ⚠ Under 22×7,5 beams a
    200-deep header is shallower than what it carries (≥ the beam depth and the hanger height, `construcao-madeira.md`
    §6); each end is a point load on the module → posts to the base, no module joint there; past ≈ 4 m of opening the
    200×100 looks over-stressed → engineer. Hangers: every hole nailed, seat = beam width, height ≥ ≈ 0,6 × beam.
    Told 2026-10-28; he asked "Porque razão? Explica-me melhor por favor" → explained in the reply the same day; his
    answer: OPEN. The rule stays ours: at least as deep as the beams it carries, posts to the base under its ends, sized
    per span (engineer).
  - **The false ceiling comes with the roof**: "Quando se aplica a cobertura automaticamente o teto falso já entra também"
    (2026-10-22) — flat, under an exposed roof too.
  - **No gap between roof and walls**: "há um gap que fica visível entre o telhado e as paredes que não quero que esteja
    assim porque não corresponde à realidade" (2026-10-22). How the eaves line is closed (cladding to the panel, a comb
    filler, a vent with mesh): OPEN.
  - **Gutters, downpipes and trims must show**: "faltam calheiras, tubos de queda e esses elementos" (2026-10-28) →
    exterior gutter on every eave, 2 downpipes per run 0,30 from its ends, ridge and rincão caps, caleiras de laró, verge
    trims, abutment flashings; gutter 125×90 and downpipes 80 mm assumed; on the façade outside or inside the cladding on
    exposed roofs: OPEN. **Every downpipe joined to its gutter** — "os tubos de queda não estão conectados as caldeiras"
    (2026-10-28, a fault; "caldeiras" read as the gutters) → fixed: a piece from the outlet in the gutter's bottom down and
    back to the pipe (a swan-neck — ours).
  - **Ridge caps lie on the panels — "coladas"** (confirmed 2026-10-28): "As cumeeiras qaundo estão a vista estão pousada
    na cobertura e tem um gap entre elas e a cobertura, outro erro que não faz sentido tu sabes que elas estão "coladas" à
    cobertura" → folded down both slopes, lying on the panels; the same for the rincão caps, the hidden roof's ridge cap
    and the abutment flashings (ours). ⚠ "Coladas" to the eye, but under the cap a profile closure / filler on the ribs,
    sealed (CM §4) — the gap he saw was a drawing fault, the filler is not a gap.
  - ⚠ Hip / multi-água framing (ours): "beams down the slope, eave wall to eave wall" cannot hold on every face of a hip
    roof, and on an L / T / U the beams turn in each wing — the engine's answers (2026-10-28, after his U review: "parecem
    haver vigas em falta e nas junções umas vigas +assam em cima das outras" — faults confirmed): under a wing crossing its
    parent the beams run down the wing's slopes, a header on the open side; where purlins run with the beams below (hip
    end, a narrower wing's end, a crossed body's slope) they lie on the beam lines, prumos ≤ 1 m along the beam, joints
    over a prumo, a ceiling beam right under the top purlin; every purlin stops against the side of the rincão / laró
    member, **fixed with estribos** (hangers) — "estribos." (2026-10-28, answering how the purlin ends are fixed) —
    confirmed (the product, skewed / sloped or square with a bevelled end: OPEN, ours — `construcao-madeira.md` §6);
    rincões / larós meeting at a point stop at the bisector; a rincão / laró foot sits on the
    ceiling beams and runs free over the overhang (≈ beirado × √2); a beam just past a rincão's top carries it, a prumo
    under the apex; one prumo per place. Also: bias-cut panels leave the PUR core exposed (sealed, closures); a downpipe
    at every laró foot. How the company frames these: OPEN (with a sketch).
- **Hidden roof (cobertura escondida)** — "Cobertura é escondida pelas paredes da casa"; on the DiscoverCasa timber
  structure ("Cobertura sem estar a vista sobre a nossa estrutura de madeira", 2026-10-15 — not the architect's steel
  "madres ómega"). Draft list: 5-rib panel 80 mm (1 m useful), ridge, sealing tape, Turbosharp 6×160; hidden gutter in
  aluminium tile-colour panel 80 cm + self-tapping screws, sealing tape, liquid membrane, Flexiband, rivets, outlets;
  flashings + downpipe. Which panel TV used (maker, minimum slope): OPEN.
  - **Hidden roofs are the usual roof, in ONE água where it works — the best solution per house, not a pattern**
    (confirmed 2026-10-28): "Aqui depende do caso, nós tentamos sempre só fazer uma água e sempre coberturas ocultas até
    porque hoje em dia já não se usa tanto telhados"; on his U (a short middle part between the arms) "fariamos apenas uma
    água para a cobertura toda"; "Não quero que assumas um padrão mas sim a solução mais eficaz e inteligente para cada
    caso". How the engine chooses (ours, built 2026-10-28, `para_construtor.cobertura_escondida`): ONE slope falling across
    the ceiling beams to the side where every strip ends on one straight line (one straight gutter), each strip's panels in
    one length up to its own high wall, a top flashing ("remate de topo") against the high parapet instead of a ridge; TWO
    slopes (ridge mid main block, every slope ≥ 1 m) only when one slope's panels would be longer than the panel's maximum
    (JSON `cobertura.painel_oculto.comprimento_max` 13,5 — ours, a truck's length; the maker's maximum: OPEN) or no side
    is straight; the house still turned so the beams span the shorter depth. His U 18,95 × 12,65: one slope, parapet
    3,82; 9 shapes audited: 8 in one slope, a 14 × 14 square in two. Which façade takes the gutter when both are
    straight (a rectangle): south by default (ours) — the client chooses ("Podes deixar o cliente escolher",
    2026-10-29; configurator step 5, `cobertura.lado_caleira`, spec §8), per project **PO Q14**. This supersedes, for every configured house, the
    2026-10-28 morning reading below. ⚠ (ours) One água puts the whole roof's water in ONE gutter → downpipes sized for the
    whole area (≈ 1 cm² per m²: two 80×35 cavity pipes ≈ 26 cm² each serve ≈ 50 m², far less than his U) — more pipes
    or a deeper recess, and the overflow matters more (one blocked outlet floods the whole gutter); the parapet grows
    with the whole run (U 3,82 vs TV 3,49: longer studs, a taller cantilever above the ring, the cércea, more cladding,
    price); at the high wall only a few cm of parapet stand above the panels (TV at the ridge ≈ 7 cm; the engine's
    `platibanda.folga` 0,05) along its whole length → the remate de topo runs up the parapet and
    under the chapéu's inner leg, a closure under it; panels up to 13,5 m: steel-skin expansion (≈ 10–12 mm on a dark
    12 m panel) and the maker's fixing rules.
  - **The lowest slope the panel allows**: "faz com uma inclinação do mínimo que é permitido sendo que se a cumeeira tiver
    de subir pode subir, eu sei que isto altera a altura total da casa mas não tem mal é o suposto nestas coberturas
    escondidas" (2026-10-16). TV: 6 % (D2503; the architect's section showed 1,3 %). **TV is two slopes** — "Sim é de duas
    águas" (2026-10-15), D2503 — a project fact (TV keeps its own config); why TV took two when one would have fitted
    (8,50 / 11,00 runs < 13,5) — the cércea, the look, the parapet height? — OPEN (ours, worth asking: it tells when "uma
    água" gives way). Configurator, 2026-10-28 morning: "a escondida que já deve ter inclinações e deve estar a altura
    correta … deves usar a forma que seria mais efeciente para a cobertura ser montada" → shown at its real height with its
    slopes; most efficient (ours): one ridge along the house through every strip, the ridge in the middle of the main
    block (every slope ≥ 1 m) (superseded 2026-10-28 by one água — kept only as the two-slope fallback, see registo).
  - **No gaps — the roof covers the whole house** (2026-10-28, a fault: "a cobertura nao está a cobrir a casa toda esta com
    gaps", circled at the U's courtyard corners and on an L): where two strips met at a re-entrant wall a strip of the
    frame's width had no panel → fixed (`casa_planta.fechar_aguas`: the open strip's slope runs on to the wall's inner
    face) — 0 gaps on 9 shapes, one and two slopes (ours, how).
  - **The same height on every side**: "a casa é suposto ter a mesma altura em todos as arestas da mesma ou lados da
    mesma" (2026-10-16) — a parapet on the low sides too, the gutter inside it. TV: parapet top ≈ 3 cm above the ridge cap
    (3,4915 vs 3,465), ≈ 0,30 above the panels at the gutters.
  - **The gutter is inside — the caleira oculta**: "sim é por dentro mas na zona que eu dei highlight no primeiro
    screenshot. fica por dentro e ao nível daparte de baixo dos rufus" (2026-10-16; 2026-10-15: "as caleiras têm de
    ficar ao nível dos rufus de forma à água escoar através da inclinação dos rufus para as caleiras e depois para os
    tubos de queda") → at the low edge of each slope, inside the parapet, under the panel ends. Build: §2 table + the
    draft's lining. The exterior gutter is for exposed roofs only.
  - **Gutter walls are lined, not clad**: "revestimento da caleira até ao topo que depois se encontra com os chapéus da
    platibanda" (2026-10-20) → on a wall with a gutter the roof-side face is the gutter lining up to the chapéu.
    ⚠ The chapéu's inner leg laps over the lining's top edge; a membrane over the wall top (ours).
  - **Parapets without a gutter — roof side clad, never a bare frame, in the house's own façade finish**: said for TV, a
    Tremolo house (2026-10-15): "lã mineral, osb 15, membrana transpir, ripado horizontal e tremolo vertical"; **the
    façade finish runs on the whole house, the parapets' roof side included** (confirmed 2026-10-28, on an ETICS house
    drawn with a Tremolo roof side: "o capoto tem que ficar na casa toda a cobertura não tem um revestimento ou
    isolamento diferente") → wool in the frame, OSB 15, Traspir, then the house's façade build-up (A ripado + Tremolo, B
    capoto, C cork) — the OSB 15 + Traspir under it from the TV list (ours for B / C); the ripado + Tremolo is TV's
    (option A), never every house's (the reading "Tremolo on every house" superseded 2026-10-28, see registo) — JSON
    `cobertura.platibanda_interior` (_doc), `camadas.camadas_platibanda`. ⚠ (ours) With capoto both faces of the parapet
    are XPS (Sd ≈ 6–9 m each, §3 B) under a metal chapéu: the frame and its wool cannot dry → a vapour-open board (wood
    fibre / cork) on the roof side or no wool there (it has no thermal role above the insulated ceiling); the capoto's foot
    over the panels / flashing on a starter track with a drip, its lowest band a splash zone (reinforced). **Gable
    parapets**: "o forro é suposto ir ate ao final do painel sanduiche" (2026-10-19) — to the panels' end over the
    gutter; beyond, the gutter's end plate up to the top (ours). **Every parapet end over a roof closed** — clad / lined and capped on every face (2026-10-16,
    TV v3 "algo no canto do primeiro screenshot está errado"). ⚠ A trim where the cladding meets the gutter end plate, the
    Tremolo foot ≈ 50 mm clear of the panel with sealed end grain (ours).
  - **Chapéus** (the parapet copings; confirmed 2026-10-16): "Os Rufos da platibanda na realidade nós chamamos de Chapéus e
    eles envolvem a parede ou seja cobrem toda a largura e ficam junto da parede do lado de dentro e de foram cerca de 3 cm
    para baixo como se encaixassem na parede"; "Na vista de lado eles cobrem um pouco da parede esses tais 2 a 3 cm tanto da
    parte de dentro como da parte de fora" → wrap the whole wall top, legs ≈ 2–3 cm down both faces (sketch
    `Construção Torres Vedras/docs/revisao-modelo/2026-10-16_v3_3_chapeu_esboco.png`). **Round the whole perimeter of the
    hidden roof, legs ≈ 2 cm** (confirmed 2026-10-28, a fault — they did not fit on the screen): "os chapéus como eu já te
    havia dito cobrem/envolvem o perímetro todo da cobertura escondida ficando do lado com 2 cm aproximadamente para baixo
    tal como no projeto de torres vedras" → JSON `cobertura.chapeu.descida` 0,03 → 0,02 ("cerca de 3 cm" of 2026-10-16
    superseded 2026-10-28, see registo; "do lado" read as each side — ours); on the screen they now fit because the
    parapets' roof-side cladding is drawn from the engine. **Flat** — "Como está feito no modelo mais recente, está
    ótimo" (2026-10-16 night; D2503 flat). **Closed at the corners** (2026-10-15: gaps let rain
    "para dentro do revestimento"); "eles não podem deixar o topo destapado e segundo eles não dão overlap uns aos outros
    senão criaria folgas entre camadas" (2026-10-20) → every top covered, no overlaps: at a corner one chapéu folds over
    it, the other butts. In the TV photos they look continuous ("verifica também os chapéus, eles parecem ser contínuos").
    **What goes under them: promise (5)** — "Por baixo dos chapéus lembra-me mais tarde para te confirmar o que leva".
    ⚠ (ours) A fall towards the roof, legs kicked into a drip ≈ 10 mm off the cladding, a membrane over the top, a vent gap
    with insect mesh at the cavity top (TV #13); butt joints over a joint strip with a small movement gap (dark aluminium
    ≈ 5–6 mm on a 3 m piece), not a rigid sealed butt.
  - **Downpipes inside the cladding, never inside rooms**: "Os tubos de queda alguns estão diretamente dentro das divisões
    o que não é suposto mas é suposto estarem por dentro do revestimento exterior mas escondidos pelo tremolo"
    (2026-10-16); "a forma como modelaste no blender por dentro do revestimento é a forma correta" (2026-10-20) → from the
    gutter through the parapet into the batten cavity, down behind the cladding. TV itself was different: "eu sei que na
    foto os tubos de queda da cobertura estão por fora do revestimento mas nós achamos que por dentro é mais correto e
    fica melhor" (2026-10-20, 13:25; photos `…/2026-10-20_final_2_sudeste.webp`, `…_final_3_garagem.webp`). **The pipe
    ends slightly above the base**: "o fim do tubo de queda não pode estar tapado pela base de fundação tem de estar
    ligeiramente acima para a água poder sair" (2026-10-16; model 5 cm). Pipe section and where the water goes: OPEN.
  - **Outlet holes at every downpipe**: "nas caleiras nao existem os buracos par agua escoar para os tubos de queda"
    (2026-10-20, a model error). Which outlet the method uses (side outlet through the parapet — the tools — or a round
    outlet in the bottom — TV as built) and its bocal: promise — "isso depois eu digo a informação não sei neste momento"
    (2026-10-20 night).
  - **Overflow (ladrão)**: "explica-me o que é um ladrao mas penso que não" (2026-10-20 night) — tentatively none (D2503
    and TV photos show none); explained and recommended; his answer after it: OPEN.
  - ⚠ (keeper, `construcao-madeira.md` §4; TV #4, #9): an overflow through the parapet at each gutter (a blocked bocal
    otherwise spills over the madre side, only 4–5 cm, into the roof void); the lining continuous up the parapet face and
    under the panel ends; a cavity pipe sized for its roof area (≈ 1 cm² per m²: an 80×35 pipe ≈ 26 cm² is small for
    ≈ 37–46 m² → deepen the cavity locally or two pipes; never through the Traspir / OSB 9), sealed or jointless, a leaf
    guard and a cleaning access, the foot into a drain / gully or a shoe onto a splash block away from the wall; a side
    outlet as a pre-formed spigot sealed to the lining, a sealed sleeve falling outwards, the studs set clear of it.
  - **As built at TV — D2503 Cobertura** ("arranjei o documento exato sobre a cobertura de torres vedra e eu disse-te mal
    como seriam as aguas analisa este documento ao detalhe guardando exatamente como é feito de forma a perceberes o
    porquê de cada pormenor !!", 2026-10-16; full reading `Construção Torres Vedras/docs/cobertura-D2503.md`):
    1. Walls: full height, ring inside (§2).
    2. Ceiling beams: lameladas 20×10 at 0,915, wall to wall, inside (4b); ceiling ≈ 0,15 under them, at 2,50.
    3. Ridge along the house in the middle of the main block (TV y ≈ 6,75, 4,25 from the north face), two slopes at 6 %;
       over the wing the south slope runs on to the wing's gutter (panels 6,44 instead of 3,94).
    4. Madres 11×7,5 on edge on prumos on every lamelada, ≈ 1,26 apart from each gutter, ridge pair 0,10 apart, pieces
       ≤ 3,66 jointed on a lamelada; the ridge as low as possible: the longest slope's gutter madre directly on the
       lameladas, the shorter slopes' raised by the difference (6 % × 2,5 = 0,15).
    5. Caleira oculta 0,31 clear between the parapet frame and the gutter madre, on calços (0,50 long: 0,31 under the
       gutter + 0,19 under the madre), **fall ≈ 2 %** to outlets at the ends (a long gutter high in the middle), never
       closer than ≈ 4–5 cm to the madre top; lining 0,30 bottom + 0,30 parapet side + 0,10 madre side + 0,10 flange =
       **0,80** (the draft's 80 cm sheet); panels ≈ 0,10 past the madre into the gutter. Site photos 2026-10-19
       (`…/2026-10-19_obra_caleira_*.webp`): an OSB box, a red (tile-colour) sheet lining, end plate turned up, corners and
       outlet sealed, a round outlet in the bottom near the end, no overflow.
    6. Panels 5-rib, 1,00 useful, laid from one end, one length per slope (3,94 / 6,44), a strip at the far end, the
       corner panel cut in an L; ridge caps ordered by count ("ENCOMENDAR 18 CUMEEIRAS" for 17,5 m); called "telhas".
    7. Parapet top ≈ 3 cm above the ridge cap. 8. Chapéu flat.
    ⚠ (keeper 2026-10-16): madres at ≈ 1,26 vs "≤ 1,2" (check the panel's span table); 20×10 over ≈ 8,2 m — long-term
    sag ≈ 45 mm (slope near the gutters ≈ 4 % in time, TV #6); 6 % vs the 4° (≈ 7 %) some makers give (TV #8); 8,50 cut
    from 13,5 m stock wastes 5 m each (TV #12).
- **Interior gutter** (3_Vigamento, §2a): "Caleira interior com 2 tubos de queda", 20 cm, along one long side of each
  roof.

## 7. Start of construction — consumables
M10 bolts (panels to base, 2–3 per module) · 45 mm drywall screws (inner and outer OSB) · Turbosharp 70/160/200 ·
Traspir 95 = exterior wall area (20 cm laps) · galvanised staples · tar (alcatrão) · drills, auger bits, jigsaw and
reciprocating-saw blades · T25 bits.

## 8. Foundation (materials usually used — the list must be updated per foundation type)
Formwork boards 25 cm × 2,60 m, Doka 3,90 / 4,90 m + ties, spacers, wedges · rebar 8/10/12 mm × 6 m, A400 ø16, mesh
(malha sol, CQ30), wire · vigotas V2/V3 + abobadilha Leca 38×23×16 · XPS 40 mm · geotextile, dimpled membrane (tela
pitonada), black plastic, chicken wire · concrete C25/30 (waterproof version), pumping, self-levelling screed · brita
nº1, meia-areia, areão, cement · PVC pipes ø50/75/90/125 × 3 m, drain pipe ø125 with sleeve, siphon · Tricapa Lana
2,00 / 2,50 m. How the base is built: promised ("base de fundação eu explicarei mais tarde", 2026-10-13).

## 9. Services pre-installation
| A/C power | Room area | Copper pipes |
|---|---|---|
| 9 000 BTU | up to 12 m² | 1/4 + 3/8 |
| 12 000 BTU | up to 20 m² | 1/4 + 3/8 |
| 18 000 BTU | up to 30 m² | 1/2 + 1/4 |
| 24 000 BTU | > 30 m² | 1/4 + 5/8 |
A/C: power point and copper 40 cm below the false-ceiling level; above doors leave 40 cm free (50 cm for living-room
units). Heat pump: cold water pipe 40 cm above the floor, hot water 80 cm, drain and return (if any) between them.

## Pending from the user (current list; answered items are in the sections above and in the registo)
**Promises by the user**
- (1) The caixilharia standard may change — "estamos a pensar mudar quando o fizermos eu aviso-te" (2026-10-19) (§3b).
- (2) Pergola fixing per project — "quando for relevante nas pérgolas eu dou-te essa informação" (2026-10-19) (§3c).
- (3) The caixilharia clearance per project when it differs from 2,5 cm (2026-10-20) (§3b).
- (4) Ask, for every project, what varies from house to house — "Para cada obra aquelas anotações que te fui dizendo que
  depende de obra para obra anota e faz-me essas perguntas" (2026-10-20) → `perguntas-por-obra.md`.
- (5) **Remind him** to confirm what goes under the chapéus — "Por baixo dos chapéus lembra-me mais tarde para te
  confirmar o que leva" (2026-10-20, 13:25) (§6).
- (6) "Vou te mandar alguns prints da casa terminada" (2026-10-20) — read as the 4 photos sent then (closed).
- (7) When the ridge madres become 22×7,5 — "Posso te responder a isso depois" (2026-10-21; asked again by him on a U
  11,60 × 18,50: "voltaste a usar vigas laranjas e vermelhas na cumeeira, alguma razão em específico?") — until then our
  > 9 m trigger (§2 table).
- (8) A list of interior finish materials — "Mias tarde vou ter fornecer uma lista de materiais para acabamentos
  interiores" (2026-10-22) (§4).
- Also promised: the foundation base, step by step ("base de fundação eu explicarei mais tarde", 2026-10-13; an
  indicative slab meanwhile); the **materials and suppliers price list** ("futuramente eu vou-te fornecer e terás acesso a
  uma lista de materiais e fornecedores onde vais conseguir ter o preço de cada material", 2026-10-15; "Isso é um passo
  futuro", 2026-10-20 night — price from materials, labour, foundation, caixilharia, especialidades, installations,
  licensing, IVA); the hidden-gutter outlet type and bocal ("isso depois eu digo", 2026-10-20 night); his review of the
  generated Cobertura and Listagem de material ("ok assim o farei").

**OPEN — to ask when it fits**
- Structure: interior studs 75×35 or 80×35; the 7,5×3,5 pieces' section in 110 walls and the face; the verga threshold
  (2,8 / 3,0 / over 3,0; rough opening or frame); D2503 interior 2,53 vs the rule 2,543, and 3,50 vs 3,4915; why 5 bays
  outside / 4 / 6 inside; two close openings when one is a door; when a site-built module is longer than the opening;
  the form of the "entalhe nas vigas" (low priority); the amarração under the upper floor joists (asked for Sobral
  2026-10-15); the 3_Vigamento "lameladas 16x8 … 7,00" and 5 × 7,00 glulam, and TV's "16x8" labels after revision C;
  the exposed-ceiling build-up; the interior gutter width (20 / 30 cm) per project; transport / site assembly in the
  price.
- Walls outside: when a house gets the contra-ripado (section, spacing); the 35 cm — centres or clear; the battens' wood
  and treatment; cork's battens; the TV membrane's data sheet; ETICS — XPS or a vapour-open board.
- Caixilharia: the clearance over an estore box and under a door to the floor; 3- / 4-leaf sizes; the remates'
  material, colour, sill / threshold, inside; the porta-janela de batente; his reply on the TV frames vs the openings.
  Closed 2026-10-29: interior walls take **only interior doors** (0,80 × 2,00) — "Só portas por norma ninguém usa
  janelas nas paredes interiores".
- Pergola (TV): slope, what is under the tiles, tile battens, gutter section, downpipe feet, the treatment's name.
- Floors / ceilings: the wool's height in the joist bay; what closes the joist bays at the façade; 0,50 joists for the
  Sobral living room; a layer under the vinyl on the OSB 22; what the perforated angle does; perfil / régua sizes.
- Roof: the prumo section; Munditelha thickness / core / skin / colour and data sheet (minimum slope, purlin span,
  overhang); the verge overhang (0,12) vs the 0,20 minimum; beirado measured from frame or façade; how the eaves line is
  closed; exposed-roof gutters and downpipes outside or inside the cladding; "duas águas" on an L (one ridge?) — with the
  cards' images, if misto is removed (misto kept for now, 2026-10-28); the default card on an L / T / U; how the
  company frames hip ends, wings, rincões / larós (the engine's answers are ours); the estribo product for purlin ends
  at a rincão / laró (skewed?); the header — his reply to our explanation (2026-10-28), its section and end bearings
  (engineer, ours); "Num L quase quadrado em 2 águas, que direção de cumeeira preferes?" (our 2026-10-22 question,
  `insights.md`); a tiled house roof (later). Closed 2026-10-28: misto kept ("Tranquilo depois se necessário removemos
  essa opção"); the purlin-end fixing (estribos); the beirado maximum (0,50).
- Hidden roof: the overflow after the explanation; the downpipe section inside the cladding and its foot (more pressing
  with one água: one gutter for the whole roof); the chapéu joints and what goes under (promise (5)); a drip / vent gap at
  the cavity top; which panel TV used and that panel's maximum length (the engine assumes 13,5 m); why TV took two
  slopes when one would have fitted; which façade takes the one-água gutter (per house, PO Q14); how TV's bottom outlet
  reached its outside pipes (optional); under the capoto / cork on the parapet's roof side — OSB 15 + Traspir as the TV
  list (the engine) or a vapour-open board (ours); the flashing where a hidden ridge falls on a parapet line (two-slope
  case only, spec §13). Closed 2026-10-28: the parapet's roof side = the house's façade finish ("o capoto tem que ficar
  na casa toda").

Sources: rothoblaas.pt (TRASPIR 95) · volcalis.pt (COMFORT) · facadebois.com (TREMOLO) · amorimcorkinsulation.com
(MDFachada) · pladur.com · obras360.pt (tile-effect sandwich panel) · pineforest.pt / somapil.com (casquinha branca) ·
Leroy Merlin page of the 30×30 cantoneira (`fontes/produtos-teto/`) · mundiperfil (Munditelha sheet, user 2026-10-22) ·
base framing sheet of another DiscoverCasa house (`fontes/vigamento-base/3_Vigamento.pdf`).
