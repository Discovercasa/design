# DiscoverCasa construction method (método construtivo) — the rulebook

How DiscoverCasa builds a house, ordered like the work on site. Kept by the agent `mestre-construtor`
(`.claude/agents/mestre-construtor.md`).
**Version 8.2, 2026-10-29** — v8.0 **condensed at the user's request** ("realiza uma limpeza aos nossos ficheiros sintetizando
tudo e resumindo aquilo que conseguires resumir"): each rule once, in its current form, in its home section (other
sections point to it); superseded chains, narration and settled arithmetic removed — **history in git** (v1 2026-10-15
… v7.8 2026-10-28). v8.1: his second message of 2026-10-28 ("erros que não fazem sentido") — hidden roofs in one água
per case, no roof gaps, chapéus ≈ 2 cm, caps "coladas", the façade finish on the parapets, beirado ≤ 0,50, estribos
(§0, §2, §6, §7, §11, §13–§15). v8.2: his 2026-10-29 answers — interior walls doors only (§3, §15 item 17 closed); the
client chooses a one-água rectangle's gutter side, default south (§7, §15). The user's words in full: `conhecimento/registo-conversas*.md`; background and the "why" of each
detail: the topic docs.

**Line format:** `- rule — source — status — where applied`
- **Scope**: no tag = **company standard** (every house). **[TV]** = Torres Vedras only, **[SB]** = Sobral only — a
  project fact (that project's cfg and `docs/`), never copied to another house without the user calling it the norm
  (§0 "Scope"). **[cfgr]** = a configurator product rule (the spec `configurador/docs/especificacao.md` is its home).
- Sources: `user YYYY-MM-DD "quote"` (verbatim in the registo, `registo-conversas.md`) · **draft** =
  company draft "Execução Técnica OBRA" (`fontes/execucao-tecnica-obra_2026-09-24.md`) · **Casa CL** = company module
  drawings (`fontes/estrutura-exemplo-casa-cl/`) · **3_Vigamento** = company base-framing sheet of another house
  (`fontes/vigamento-base/3_Vigamento.pdf`) · **D2503** = DiscoverCasa's roof production drawing of TV, the roof as built
  (`Construção Torres Vedras/desenhos/250828_D2503_Cobertura.dwfx`; read in TV `docs/cobertura-D2503.md`) · **D2503
  Módulos** = the wall-module production drawing of TV (`…/250828_D2503_Modulos.dwfx`; TV `docs/modulos-D2503.md`) ·
  project drawings. Topic docs: **SC** = `sistema-construtivo.md`, **CM** = `construcao-madeira.md`; **TV** / **SB** =
  `Construção Torres Vedras/` / `Construção Sobral/` docs (`#n` = item in that project's `docs/revisao-tecnica.md`).
- Status: **confirmed** (the user said it) · **tentative** (said with "acho que", "diria que sim", "não sei ao certo",
  "parecem" — confirm with a document before building on it) · **company document** · **assumed** (ours, not said) ·
  **delegated** (he left the choice to us — "vai com a opção que achares melhor": ours to make and change, never cited as
  company practice — "a nossa escolha") · **general practice** (from CM, not a company rule) · **OPEN** (unknown — §15).
- Where applied: **JSON** `key` = `ferramentas/modelo/sistema_construtivo.json` (the standard) · **cfg** `key` = a
  project's `modelos/<tipo>/config.json` (overrides for that house) · functions in `ferramentas/modelo/`
  (`casa_planta.py` builder from a plan, `estrutura_dc.py` skeleton from engineer's drawings, `camadas.py` layers,
  `divisor_modulos.py` module split, `telhado.py` / `telhado_estrutura.py` exposed roofs) · configurator
  `ferramentas/configurador/para_construtor.py`, `configurador/web/src/*.js` · "not in the tools".
- **PO Qn** = varies per project: asked at the start as item Qn of `conhecimento/perguntas-por-obra.md` (with its default).
- **(was … until date)** = a superseded value kept only where it matters for reading old models.
- Sizes in mm (the user writes cm: "11x7,5" = 110×75, "3,75x3,5" = 37,5×35); metres with a decimal comma.

## 0. Principles
- **Always the DiscoverCasa method**; architects' and engineers' construction notes are not binding — user 2026-10-15 "nós
  usamos o nosso método construtivo sempre portanto segue o nosso"; 2026-10-09 "vais usar o nosso método construtivo com
  os nossos materiais e não os que ele menciona" — confirmed — cfg `estrutura.sistema` "discovercasa"; `casa_planta.py`,
  `estrutura_dc.py`. (was "project drawings win", e.g. SB studs 160×80, until 2026-10-15 — L9.)
- **The architecture fixes the geometry only**: plan and room sizes, levels, openings' positions, roof type — user
  2026-10-15 "Essa informação não está disponível no projeto de arquitetura ?", "a inclinação deverá estar descriminada
  nos desenhos fornecidos penso eu" — confirmed (the list = our reading) — cfg `niveis`, `cobertura.*`,
  `planta_paredes.json`. [TV] DiscoverCasa kept the outer outline, the openings' positions and the roof type but set its
  own rough openings (§3), clear height (2,60 → 2,50) and slope (1,3 → 6 %) — D2503. Hidden roofs: the lowest slope the
  panel allows (§7).
- **The clear height (pé direito) is the client's choice — no company standard**; any value, 2,40 / 2,50 / 2,60 the usual
  suggestions — user 2026-10-21 "A altura não temos fixa o cliente pode escolher a vontade o que preferir"; (later) "O
  cliente pode escolher qualquer valor mas podemos deixar sugestões por exemplo essas 3 sugestões que falaste que por norma
  são o habitual" — confirmed — PO Q5; §2. Who chose TV's 2,50: not said (low priority).
- A house ending taller than the architecture is normal — user 2026-10-15 "sim isso é natural e também não tem qualquer
  tipo de problema" — confirmed — `casa_planta.construir`. ⚠ The licensed height still matters (TV #7, SB #22).
- Rules the user gives hold for every house unless told otherwise — user 2026-10-09 "always follow this logic unless told
  otherwise" — confirmed.
- **Scope — company standard vs one house**: a fact about one house ("nesta casa", "neste caso") is a project fact → that
  project's cfg / docs, tagged [TV] / [SB] here; the standard changes only when he calls it the norm ("o nosso padrão",
  "por norma") — user 2026-10-15 "Tremolo fica na vertical como é o nosso padrão … Nesta casa só levou ripado na
  horizontal e não levou o contra-ripado" — assumed (our reading; L15) — cfg `camadas` merged over the JSON
  (`camadas.fundir`). A correction of a model worded "é suposto" is kept as a company rule until he says it was one
  house (L17, L18). **A rule said while looking at one house is checked for what in it depends on that house (its façade
  finish, roof type, beams) before it is applied to every house** — the parapet's roof side listed in Tremolo on TV was
  drawn in Tremolo on every configured house; user 2026-10-28 "o capoto tem que ficar na casa toda" — ours (L52).
- **Every new project starts with the per-project questions** (`perguntas-por-obra.md` Q1–Q23, each with its default;
  unanswered → the default, said in the delivery) — user 2026-10-20 "Para cada obra aquelas anotações que te fui dizendo
  que depende de obra para obra anota e faz-me essas perguntas", "senão vai com o default de 2,5 cm" — confirmed / assumed
  (items and defaults ours) — answers → the project's `docs/estado.md` and cfg; every new "depende" / "neste caso" adds an
  item there and a PO Qn mark here. Then the model, then the documents (§0a).
- **The method vs this house**: when he calls a model detail "a forma correta" while the house was built otherwise, the
  model's way is the method (here, JSON) and the house's way a project fact — user 2026-10-20 "pois nós nesta obra fizemos
  de forma diferente mas a forma como modelaste no blender por dentro do revestimento é a forma correta" — confirmed
  (wording) / working rule ours (L40). An approval covers the point that was asked, not every detail of the modelled
  thing (L40); a site photo contradicting an approved model → ask "method or this house?" first.
- Company documents (draft, Casa CL, 3_Vigamento) show the company standard — user 2026-10-15 "este não é o mesmo projeto
  mas é para perceberes como operamos" — confirmed.
- **A company production drawing of a built house (TV: D2503) wins over descriptions from memory**, his included: ask for
  the production drawings (roof, modules, framing) first — user 2026-10-16 "arranjei o documento exato sobre a cobertura
  de torres vedra e eu disse-te mal como seriam as aguas" — confirmed (L23, L24). Keep the reason of each detail ("de
  forma a perceberes o porquê de cada pormenor", 2026-10-16) — confirmed. A rule he states in words with a photo ("Como
  podes ver na foto real da obra …") is a rule.
- **Photos**: a site photo may show a site change ("este módulo sofreu uma alteração em obra", 2026-10-15 — L14) — ask
  before making it a rule; finished-house photos show the built house, a stage photo a stage — ask for finished photos at
  the start (PO Q1) and what came later before calling a stage photo wrong (2026-10-20 "como podes ver nessa foto terminada
  da casa …" — L39) — working rules.
- **How to ask** (working rules, ours, each from a question he did not understand): one point per question; the house,
  sheet and drawing label with the image ("A quais lameladas te referes?", 2026-10-21 → re-asked so, answered); his word
  for each element and the approved table's (janela de correr, porta, portão, basculante, vidro fixo), checking the premise
  first ("Prtas não tem estore apenas as janelas", 2026-10-27); a module by its label with its sheet ("não estou a ver qual
  é o módulo 2,21", 2026-10-19); a product with the maker's image and name, not a draft word ("Como assim com um painel
  imitação telha? Nós usamos sempre painel sandwich", 2026-10-21); how members carry each other **with a sketch** ("Não
  percebi …", 2026-10-27 → with the sketch: "Prendem-se as vigas laranja", 2026-10-28); lettered options kept as sent in
  the registo / spec, each naming what the engine does ("opção a", 2026-10-28). When a question is a new consequence of a
  known rule, state the known rule in his words first (L13).
- **Record his certainty**: "acho que", "diria que sim", "não sei ao certo", "parecem", "não me relembro" → tentative; "o
  nosso padrão para já" → the standard for now (he will say when it changes) — user 2026-10-19 (18:12) — working rule.
- A "sim" to a question in our own words confirms the gist — test it against the first real numbers (L34); an answer that
  takes words from both sides of an either/or is asked again with an image of each (L46) — ours.
- **Check a numeric answer against the project's data before sending it** (`docs/materiais.md`, cfg, module data, every
  direction, clearance and box included); say what was checked, the rest "a confirmar" — ours (L41, L42).
- **Design choices left to us** ("vê o que se enquadra melhor"; "não temos uma regra específica para isso", 2026-10-19):
  propose per house within the rules, a tools default overridable per case, shown in the production drawings, saying where
  we would draw the company's drawing differently ("nesta casa por exemplo terias desenhado os módulos de forma
  diferente ?") — confirmed (ours to choose) / assumed (default + override). Shown the alternatives, "Vai com a opção que
  achares melhor, força nisso confiança" (2026-10-20 night) → **delegated**.
- **The most effective and intelligent solution for each case, not a pattern** — user 2026-10-28 "Não quero que assumas um
  padrão mas sim a solução mais eficaz e inteligente para cada caso" (said on the hidden roof's shape) — confirmed: a
  tools default is a starting point, chosen per house and said why in the delivery (e.g. one or two águas, §7) — ours
  (how). **Faults he calls "erros que não fazem sentido"** (gaps, water paths not joined, trims not wrapping, caps
  floating) are checked on every model before he sees it (L53–L56).
- Walls are prefabricated modules, factory- or site-built; module drawings ("os módulos desenhados por nós") do not show
  the fixing to the base — user 2026-09-23, 2026-10-15 — confirmed — `divisor_modulos.py` via `casa_planta.py`
  (`casa_planta.juntas` only with cfg `modulos.divisor` false), `estrutura_dc.py`, `modulos_dc.py` (reads company module
  drawings); fixing to the base not in the tools.
- The licensed specialty projects (thermal, acoustic, stability) must describe the DiscoverCasa build-ups → give them at
  the start — ours (SB #26, TV #1) — **PO Q3**.
- **Spacings**: wall studs by the clear gap (40 cm livre); floor barrotes centre to centre ("sao medidos em eixo", user
  2026-10-13); the others not said — the tools divide floor joists, barrotes, ceiling beams and purlins equally at ≤ the
  value and lay battens and perfis at the value from one end, the last bay taking the rest — assumed — `casa_planta.py`,
  `estrutura_dc.py`, `camadas.dispor`, `camadas.tetos`. The ripado starts at the bottom (§8).
- **No shortcuts** — user 2026-10-21 "são bastantes tarefas não vás por shortcuts, capricha em cada uma delas" —
  confirmed: a rule carried to a new case (an L, an exposed roof, a hip end) is checked against every rule here, not
  copied by analogy (L45, L46).
- **Insights** we give him are listed in `conhecimento/insights.md` — user 2026-10-21 "Obrigado pelo insight depois grava
  junto com uma lista de insights" — confirmed — an insight is not a rule until he answers.

## 0a. Production documents — what DiscoverCasa draws for every house (the D2503 format)
- **For every new project, produce the module and roof drawings "igual ou do género" of D2503, then model the house as
  it will be built** — user 2026-10-16 "quero que sejas capaz de desenvolver um documento igual ou do género desse dos
  módulos e da cobertura independemente do projeto … de forma a podermos modelar a casa sem erros e já como irá ficar no
  fim da construção" — confirmed — `ferramentas/documentos/gerar.py`; `modulos_dc.py` reads such a module drawing (TV →
  `modulos_D2503.json`, cfg `modulos_reais`). The OPEN points of §2–§4 are assumed in the documents too.
- **The set: Módulos + Cobertura + Listagem de material (pdf + csv), generated from the model** — user 2026-10-20 (13:43)
  "começa a preparar o método de geração dos documentos … quero também que incluas um documento com a listagem de
  material" — confirmed (the set) / assumed (list format: chapters 1–8 — structure timber, exterior layers, insulation and
  interior layers, floors, ceilings, roof, caixilharia and remates, pergola; net quantity and purchase = quantity × (1 +
  waste) / purchase unit; the cut list as an annex) — `python ferramentas/documentos/gerar.py
  "<project>/modelos/casa/config.json"` → `<project>/documentos/<obra>_Modulos.pdf`, `_Cobertura.pdf`,
  `_Listagem_Material.pdf` + `.csv` (cfg `documentos`: `obra`, `projeto`, `local`, `revisoes`). The list's footer names
  what it leaves out: consumables (§12), foundation, interior doors, installations. [TV] run: Módulos 6 sheets, Cobertura 4.
- **The chain: per-project questions → model → documents**; he reviews the documents — confirmed (each step) / assumed
  (order). ⚠ His wording runs documents → model; one source means they never disagree, but the module choices (split,
  corners, openings) must be reviewable on the documents before the model is final — tell him.
- **Whole studs: no module is notched for a beam** (beams stop at the modules' inner face, §4) — user 2026-10-21 "não
  atravessam ou fazem com que as da estrutura sejas separadas em dois pedaços" — confirmed — `casa_planta.py` (no pockets),
  `documentos/dados.py`. ⚠ `gerar.py`'s material-list footer still says "montantes inteiros, entalhe feito em obra" — stale.
- **Review**: [TV] the generated Módulos "está absolutamente correto" — user 2026-10-20 (night) — confirmed — it covers
  sheets drawn from D2503's own modules (cfg `modulos_reais`), not the divider's split (not reviewed yet). Cobertura and
  Listagem: review promised (§15).
- [TV] **Cut-list check**: generated = D2503's drawing — exterior 50 × 11x7,5 / 140,5 m, 228 × 11x3,5 / 478 m; interior 207
  × 7,5x3,5 / 376 m (studs 1,3 cm longer, made to measure), 24 × 7,5x11 / 46 m; D2503's own table 50 / 139, 220 / 473, 199
  / 379, 24 / 46 → the 8-piece differences are D2503's table vs its drawing (explained 2026-10-20 night); which one the
  factory cut to: not asked. Panels 30 × 3,94 + 7 × 6,44 vs D2503 28–29 + a 3,94 × 0,25 strip + 7: OPEN. Recheck on the
  TV rebuild v6.5.
- The set should also (ours, not in the tools): (1) say which caixilharia size each line gives (table nominal or frame to
  order = opening − 2 × 0,025; today the cfg item's modelled size); (2) draw the gutter outlets and downpipe crossings on
  the module elevations (the only cuts through a module frame) so studs are set clear; (3) mark assumed items "a
  confirmar"; (4) the corner choice at every corner, the made-to-measure interior height, each opening's table item.
- **Inputs per house: the architecture (geometry) + the approved openings table** (TV "PROJETO APROVADO") — user
  2026-10-19 "já te vou fornecer um print com os vãos para os modelares" — confirmed — TV cfg `camadas.caixilharia.itens`
  (typed by hand; no reader). Also the maker's order when there is one, and the attached elements (pergola, deck) —
  `perguntas-por-obra.md` Q1–Q3, Q21–Q22.
- **Módulos** (D2503 Módulos, company document): 2 A1 sheets "Módulos Exteriores" / "Módulos Interiores", "Sem Escala";
  plan in the middle, every module in section labelled M1, M2 … in blue; each module's elevation beside the plan, aligned
  (N, S upright; W, E turned 90°), total width dimensioned; black outline = 11×3,5 / 7,5×3,5 (studs, plates, cripples,
  noggings), red hatched = 11×7,5 / 7,5×11 (corner studs, jambs, lintels, sills); "CONSIDERAÇÕES GERAIS" (40 cm clear, not
  dimensioned; irregular spacings dimensioned; corner detail); "QUADRO DE DIMENSÕES E QUANTIDADES" (L × A, V = door/window,
  P = door, "* Painel a executar em obra"); cut list "COMPRIMENTO DAS VIGAS" — `modulos_dc.py` reads, `gerar.py`
  `doc_modulos` draws ("*" from the divider's site-built flag; a real module longer than the factory maximum flagged too).
- **Cobertura** (D2503): 5 A3 sheets — 1 "Lameladas horizontais e amarração"; 2 "Madres (Pendentes) - Esquema geral" with
  the gutter falls; 3 "Madres (Pendente) - Posicionamento"; 4 the panels ("telhas", ridge caps to order); 5 "Secções tipo"
  1:50 + "pormenor caleira/algeroz" — company document — `gerar.py` `doc_cobertura` in 4 sheets; whether the pormenor is
  drawn: not checked.
- Title block DISCOVERCASA, obra, revisions (TV A "Dimensões para execução" … C "Cobertura - Vigas de 16x8 para 20x10" … E
  "Cobertura e Módulos - Correção para produção") — company document. ⚠ D2503 kept stale labels ("16x8") and view
  mismatches (P01 2,64 / 2,61; module 3,50 / parapet 3,4915) → update every label from one source and cross-check the
  sheets — ours (TV #11).
- Each module carries its reason (grid bays, opening + jambs + margins, site-built) — user 2026-10-16 "o porquê do tamanho
  de cada módulo" — confirmed — TV `modulos-D2503.md`.
- **Implementations** (builder, budgeting, client platform, configurator — `discovercasa.md` Product vision 1–4) run in
  their own session and branch, with this rulebook and the same registo, merged back often; they take build rules from
  here and the JSON, never a copy — user 2026-10-20 (night) "…crie uma subsessão … de forma a saberes construir uma
  discovercasa" — confirmed / assumed (worktree, merges) — `conhecimento/sessao-implementacao.md`. [cfgr] The client never
  sees "módulo" ("O cliente nunca deve ver a palavra módulo sequer a aparecer no seu ecrã"); its 3,00 m walls are building
  blocks, made into modules by §2 behind the screen.

## 1. Foundation base (base de fundação)
- Concrete foundation; how DiscoverCasa builds its base will be taught step by step — user 2026-10-09 "i will teach you
  how we build our foundation bases step by step"; 2026-10-13 "base de fundação eu explicarei mais tarde" — OPEN — **PO
  Q4** (type, floor level against ground and deck). **An indicative slab is fine for now** — user 2026-10-20 (night) "uma
  laje representativa para já não tem mal visto que vamos primeiro focar em ter o builder a funcionar direito" — confirmed
  — cfg `fundacao` (20 cm slab).
- Ground floor: **vinyl straight on the base**, no other layer — user 2026-10-09 "when is just one floor it does not get
  anything is straight vinyl on the foundation base" — confirmed — cfg `camadas.pavimentos.piso0` (`acabado_z` 0,005).
  ⚠ JSON `pavimentos.piso0` still defaults to SB's XPS 60 + betonilha (finished Z 0,16). [TV] "Pavimento sobre a nossa base
  de fundação" (not the architect's slab) — user 2026-10-15.
- Modules fixed to the base with M10 bolts, 2–3 per module — draft — company document — not in the tools.
- Foundation materials: the draft list (SC §8) "must be updated per foundation type" — company document.
- **The foundation is cast to the modules**: its outline = the modules' outer face (D2503 legend "Dimensão da fundação e
  módulos"); the cladding overhangs the base edge ≈ 9 cm [TV] — company document — cfg `paredes.exterior`
  "face_exterior", `fundacao.contorno`; `camadas` `exterior.cota_base`. The overhang wants the batten cavity meshed at the
  bottom, the Traspir lapped down over the base edge, the Tremolo foot ≥ ≈ 150 mm above ground, an inspection strip (TV
  #16) — general practice.
- To cover when the base is taught (general practice, CM §2, §4): lowest timber ≥ 150 mm above finished ground; DPC under
  every ground-floor bottom plate; treated bottom plates; anchors against sliding and uplift; termites in all mainland
  Portugal. ⚠ [TV] floor 117,50 vs deck 117,48 (TV #5); SB #1. Deck and attached elements: **PO Q22**. The "alcatrão" of
  the start list: OPEN. Where downpipe water goes at the foot: OPEN (§7).

## 2. Wall modules
### Sections and framing
- Exterior walls 110 deep: studs and plates **110×35** — user 2026-09-24 "every piece of timber used on the outside is
  11x3.5" — confirmed — JSON `estrutura.exterior`.
- Interior walls 75 deep: **75×35** — user 2026-09-30 "on the inside panels 7,5x3,5m" — confirmed (80×35 also named,
  2026-09-24 "8x3.5 or 7,5x3,5" — OPEN; [TV] 7,5×3,5 and 7,5×11 only, D2503 Módulos) — JSON `estrutura.interior`.
- **110×75 at the house corners — two side by side, one per wall — and at every opening** — user 2026-09-30 "11x7,5m on
  the corners and on the vãos (… two timbers of 11x7,5m one next to each other)" — confirmed — `estrutura_dc.emoldurar`;
  JSON `estrutura.*.seccao_reforco`. In 75 walls turned (75 across, 110 along) — Casa CL — JSON
  `estrutura.interior.reforco` 0,11.
- **Studs at 40 cm clear** (≈ 0,435 centres), from one end, the last bay taking the rest — Casa CL; D2503 Módulos
  ("CONSIDERAÇÕES GERAIS": same in every module, not dimensioned) — company document — JSON `estrutura.vao_livre` 0,40.
  (D2503 lays them from the corner post / jambs — not reproduced, §15 X-list.)
- Single bottom and top plates 35 — Casa CL, D2503 Módulos — company document — JSON `estrutura.placa`.
- **Escadas: 4 noggings at 0,66 between two studs of the receiving module at every wall junction** (11×3,5 exterior,
  7,5×3,5 interior; interior walls on exterior ones and at corners) — *why (ours)*: fixing for the abutting module — D2503
  Módulos — company document (one house; "escadas" is our word — check his) — JSON `estrutura.escadas` (`travessas` 4,
  `espacamento` 0,66); only with real modules — **not generated by the builder** (the divider keeps joints out of a meeting
  wall, so they can be added). (was "no noggings", Casa CL, until 2026-10-16 — L29.)
- **Mid-wall module joint**: each module keeps its own 35 end stud; 110×75 only at corners and openings (incl. a module end
  beside a doorway) — user 2026-10-09 "leave them as they are now and those are the rules" — confirmed —
  `estrutura_dc.emoldurar`.
- An extra stud near a wall junction (Casa CL, ≈ 0,1 from the module end) — company document (our reading) — not in the
  tools; the same job as the escadas: OPEN.
- Module timber purchase mix 110×35 40 % · 110×75 40 % · 80×35 20 % — draft — company document; [TV] by volume 42 / 35 /
  23 % (D2503 cut list ≈ 4,34 m³) → a volume mix (ours) — not in the tools (§11).
- Module screws Turbosharp 6×70, 6×140, 6×160 (torx) — draft — company document — not in the tools.

### Module length and splitting
- **Factory modules normally ≤ 3 m; exterior factory modules up to 3 m** (a maximum, not a target); 5 m done once (an
  exception); site-built modules may be the exact wall length — user 2026-10-15 "Valor base dos módulos qaundo produzidos
  em fábrica 3 metros mas isto depende do transporte", "já fizemos módulos de 5 metros", "se forem feitos em obra os
  módulos podem ser feitos na medida exata da parede"; 2026-10-19 "o tamanho que normalmente fazemos em fábrica não
  ultrpassa os 3 metros mas dependendo da casa vê o que se enquadra melhor"; 2026-10-20 (night) "os módulos exteriores
  podem ir até 3 m" — confirmed — JSON `estrutura.divisor` (`comprimento_max` 3,0; `comprimento_preferido` exterior 3,0 /
  **interior 2,75** — TV's M17 2,72, assumed, not asked); per house cfg `modulos.comprimento_max` (**PO Q6**).
- **Bigger modules are assembled on site, marked "* Painel a executar em obra"** — user 2026-10-19 (15:48) "ok tranquilo,
  mas sim esses módulos maiores são montados em obra" — confirmed; [TV] only M1 3,82 (garage door 3,00) — D2503 Módulos —
  `divisor_modulos.py` flag `obra` → "*" in `gerar.py`; a real module (cfg `modulos_reais`) longer than the factory
  maximum flagged by `casa_planta.py`.
- **A site-built module is as short as its opening needs, by default** — user 2026-10-20 (night) "depende da situação mas
  neste caso sim usa o tamanho que o vão precisa" (asked: TV garage 3,39 vs D2503 M1 3,82) — confirmed (default) — PO Q6 —
  JSON `estrutura.divisor.custos` (`obra_por_metro`). When it should run longer (to the wall end, the whole wall): OPEN.
- **Transport is not a design constraint** — user 2026-10-21 "A questão do transporte não precisas de te preocupar,
  podemos sempre arranjar uma empresa especializada para transportar os módulos ou fazer os módulos em obra" — confirmed —
  no transport or module-height cap in the tools; the 3 m factory maximum is their rule and stays. ⚠ Cost: special
  transport / site assembly belongs in the price per house — ours (§15).
- **Plain modules are whole bays of the grid + the last stud**: exterior **2,21 = 5 bays**; interior **1,78 = 4 bays**,
  **2,65 = 6 bays**; the rest of a wall = opening modules (§3) and remainder modules — D2503 Módulos [TV: 2,21 = M8, M11,
  M17, M19, M21, M22, M25, M26; 1,78 = M5, M7, M11, M14, M16, M18; 2,65 = M2, M3, M13] — company document (one house) —
  `divisor_modulos.py` (JSON `estrutura.divisor.vaos_lisos` exterior [5] / interior [4, 6]; other whole-bay counts ≥ 2
  at a cost — ours). *Why (ours)*: studs on the grid, predictable board joints, the same jigs. Why 5 bays outside: OPEN,
  low priority (our transport hypothesis, "diria que sim" 2026-10-19 — tentative — no longer holds as a limit). ⚠ The
  divider now also makes 6-bay 2,65 exterior plain modules and opening modules near 3 m, which D2503 never did outside
  (≤ 2,64) — show them with the next house.
- [TV] factory modules as built ≤ ≈ 2,64 exterior (M18) / 2,72 interior (M17) — D2503 Módulos.
- **Two wide openings side by side → three modules split at the pier** — D2503 Módulos [TV P18: 2,15 + 0,32 + 2,15, each
  2,15 = a janela de correr 2,00 + two 11×7,5 jambs; M13 0,32 the pier] — company document — `divisor_modulos.blocos`
  (JSON `estrutura.divisor.pilar_min` 0,32).
- **Two openings closer than a 0,32 pier share one module when it fits the preferred length** ([TV] interior M21 — our
  reading); **else, when both are windows, they are moved apart, half each, to a 0,32 pier** — user 2026-10-20 (night)
  "…por defeito podes assumir que sim quando esta situação acontece desde que sejam duas janelas como neste caso" —
  confirmed (default) — `divisor_modulos.blocos` (warning in the build log). "A window" = the drawing's kind (no door swing),
  so a janela de correr to the floor is a window (our reading). **With a door**: the door stays, both in one longer module
  (site-built if > 3 m), warned "a confirmar" — assumed, ask when it arises. ⚠ Moving an opening changes the approved
  façade → show every move (configurator: moved openings shown on the client's screen since 2026-10-22; plan houses: in
  the delivery). A table "porta de correr" with no swing drawn would be moved too — OPEN (ours: take the kind from the
  table — not in the tools).
- **The split …** — **driven by the openings and the interior walls, ours to work out from the rules** (every opening in
  one module, §3; whole-bay plain modules; escadas where a wall meets; one wall through at each corner) — user 2026-10-20
  (night) "pretendo que com as informações que já tens sobre os nossos módulos que consigas dividir a casa nesse
  diferentes módulos que falas dependendo dos vãos que o cliente escolher e paredes interiores" — confirmed —
  `divisor_modulos.py` (JSON `estrutura.divisor`; used by `casa_planta.py` for every house without cfg `modulos_reais`;
  cfg `modulos.divisor` false = the old `casa_planta.juntas`). Tested against [TV] D2503 (`--comparar`, TV
  `divisor-vs-D2503.svg`): the rules hold in both; the differences are only where a wall's remainder goes (D2503 not
  consistent there); 48 modules vs 50 — plain whole-bay 23 vs 20, remainders 6 vs 11, irregular margins 23 vs 20; from the
  architecture alone 25 + 23. **No joint inside the thickness of a wall that meets** (D2503 M20's joint 3 mm before P10) —
  company document — JSON `folga_juncao` 0. Smallest module **0,60** except a pier ≥ 0,32 or a whole short wall — ours
  (`comprimento_min` 0,60).
- **Where a wall's remainder goes and the margins round an opening: by costs** — fewer modules; plain whole bays; one short
  remainder per wall, preferably at its start; margins tight to a jamb or whole bays (irregular at a cost); up to the
  preferred length; site-built only when an opening needs it — user 2026-10-20 (night) "Vai com a opção que achares
  melhor, força nisso confiança" — **delegated** — JSON `estrutura.divisor.custos` (calibrated on TV; retune per house,
  saying so). A per-wall override: not in the tools (ours).

### Module height and position
- **Module height follows the house** — user 2026-10-15 "os modulos vão de encontro ao tamanho da casa" — confirmed (the
  formula ours) — `casa_planta.construir`: ceiling beams' underside = finished floor + pé direito + ceiling build-up
  (régua gap 27 — 118,5 on hidden roofs, §6 — + perfil 17 + Pladur 12,5). Then: **exterior modules on exposed roofs** =
  underside − afinação 35 − amarração 75 ≈ **pé direito − 0,05** (assumed — the draft's top pieces, §4), raised for a high
  opening head (§3 "opção a"); **exterior modules on hidden roofs** = full height to the parapet top (below);
  **interior modules on every roof** = underside − 0,11 (made to measure, below).
- **The pé direito is chosen per house by the client and the whole structure follows it** — user 2026-10-21 "quando o
  cliente escolhe a área total da casa deve também escolher o pé direito que deseja e assim já ajustamos a estrutura para
  isso" — confirmed — [cfgr] `colocar.js` `PE_DIREITO` {min 2,40, max 3,50, passo 0,01, inicial 2,50, sugestoes [2,40,
  2,50, 2,60]} → `para_construtor.py` (`PE_MIN` 2,40 refuses below; `PE_MAX` 3,50 notes "montantes e placas a confirmar")
  → cfg `niveis.pe_direito` → `casa_planta.construir` (checked: 2,60 → beams' underside 2,753, parapet top 3,541). 2,40 =
  RGEU art. 65.º (the law); 3,50 = our guard; **2,50 default = TV as built** (ours). From a plan: cfg `niveis.pe_direito`
  (**PO Q5**). What follows (ours; hidden roof, ceiling 0,148 under the beams): interior modules = pé direito + 0,043
  (studs pé direito − 0,027); exterior full-height ≈ pé direito + 1,00 at TV (two slopes; depends on beams and roof
  rise), studs ≈ + 0,93; **more on a one-água roof — the rise grows with the whole run** (his U 18,95 × 12,65: parapet
  3,82 vs TV 3,49 — the engine's arithmetic, §7). Heights built elsewhere: Casa CL ground floor 2,97 ext / 2,80 int, upper 3,52 ext / 2,68 int (reference);
  SB 2,58, upper 2,40 (§13).
- ⚠ **What a taller pé direito changes** (ours, to tell — not limits): exterior studs ≈ pé direito + 0,93 → past ≈ 3,0
  stock length and buckling / wind on 110×35 → engineer (CM §1); the 4,0 m Tremolo needs a joint in height (§8); Pladur
  past 2,60 (§11); the licensed height (cércea, PDM — TV #7) and the price. At the low end (2,40) a 2,20 janela de correr
  with its estore fits — §3.
- **Hidden roofs (cobertura escondida atrás de platibanda): the exterior modules run in one piece from the base to the
  parapet top — on every hidden roof, on 22×7,5 ceiling beams as on lameladas**; no separate parapet module, no afinação
  exterior — user 2026-10-21 "sim exatamente os módulos vao inteiros ate ao topo da platibanda"; 2026-10-16 "eu sei que
  isto altera a altura total da casa mas não tem mal é o suposto nestas coberturas escondidas" — confirmed —
  `casa_planta.construir` (`anel` for every cfg `cobertura.tipo` "platibanda"; JSON
  `estrutura.platibanda_modulos_inteiros` true). The ring and the beams on it: §4. Without real modules the builder models
  the one module in two parts (framed to the ring, studs running on into a parapet part, joints `juntas_w`) — a modelling
  split (L30).
- [TV] **Module heights as built: exterior 3,50 in one piece** (studs 3,43 + two plates), **interior 2,53** (studs 2,46)
  — D2503 Módulos. ⚠ CONFLICTS, OPEN, low priority: the roof sections put the parapet top at 3,4915; the interior 2,53 is
  13 mm under the made-to-measure 2,543 (rounding / another datum / taken up on site — TV #6); the model follows the rule.
- **Interior modules are made to measure to the ceiling beams**: height = the beams' underside (lameladas or 22×7,5) −
  0,11, the 110×75 viga de amarração upright on top, no packing; on a hidden roof level with the exterior ring — user
  2026-10-19 (18:12) "Nós fazemos os módulos de forma a ficarem à medida certa das vigas amarração" — confirmed (the
  arithmetic ours: TV 2,653 − 0,11 = 2,543, studs 2,473) — JSON `estrutura.afinacao_interior` (altura 0,11, the draft's
  name); `casa_planta.construir`; real modules: cfg `modulos_reais.interior_a_medida_da_amarracao` (+1,3 cm, TV v6.1). His
  word is "viga de amarração"; the draft says "viga de afinação interior".
- **The base level under the interior walls is laser-checked before the ceiling beams go on** — user 2026-10-20 "nós
  usamos um laser para verificar isso, exatamente como sugeriste" — confirmed (company practice) — not in the tools (a note
  for the production drawings). Hard shims where needed and each beam fixed to the interior viga — assumed (the rest of
  that suggestion).
- **Position: the modules' outer face on the foundation line** = the architect's outer faces; the cladding outside it
  ("linha de pronto" ≈ 9 cm out), OSB 15 + Pladur inside; interior frames on the architect's centre lines ([TV] all 12 ±
  1 cm) — D2503 legend "Dimensão da fundação e módulos" — company document — cfg `paredes.exterior` "face_exterior";
  ⚠ `casa_planta.py` defaults to "face_interior" when the key is missing. ⚠ Against the licence: [TV] rooms ≈ 11 cm wider
  each side, footprint ≈ 9 cm per side larger over the cladding (TV #7).

### Corners
- **At every corner one wall runs through and the other abuts — always; which one: no company rule** — user 2026-10-19
  (15:48) "sim e é suposto ser assim a lógica sempre, não temos uma regra específica para isso." — confirmed. The corner
  stud is an 11×7,5 at the end of the through wall; the abutting wall ends on its own 11×7,5 across — D2503 Módulos —
  company document. [TV as built: P11 through at both corners; P03 at the west corner and on to the re-entrant corner;
  P01 at the SE corner; at the wing's SW corner P14 through, P01 starting after it (from 10,89), P14 stopping 0,035 short
  of P03's inner face.]
- **Which wall runs through is chosen per house and corner (by us)**: "X exterior walls through, Y walls abut" (or "the
  walls carrying the ceiling beams run through") is a **BUILDER DEFAULT, not a company rule** — assumed (SC §2b item 6) —
  `casa_planta.construir` (fixed, no per-corner choice yet); the chapéus follow the actual corner (`camadas.chapeus`
  `ate_parede`, L38); optional **PO Q7**. For the generator: the default + a per-corner override drawn in the module
  sheets — ours, not in the tools (L26).
- **Interior walls run between the exterior walls' inner faces and stop on the frame of the wall they meet** ([TV] P13:
  1,10 + 2,65 + 2,65 + 1,88 = 8,28) — D2503 Módulos — company document — `casa_planta.construir`. Two interior walls
  meeting end to end: the X wall through to the Y wall's far face — ours ([cfgr] user 2026-10-22 "o fim de uma das paredes
  pelo menos deve fazer 90º perfeitamente"). [cfgr] An interior wall starting on an exterior wall shows its distance to
  both corners — user 2026-10-28 "deve dizer a distância de cada canto" — confirmed; **measured from the base corner to
  the wall's centre line** — ours, to confirm (a tape inside measures finished corner → wall face, ≈ 0,2 less) (§15).
- Upper-storey walls stand on the floor OSB 22 (platform framing) — user 2026-10-15 "sim" — confirmed — `estrutura_dc.py`.
  ⚠ A joist or batten under every upper wall carrying roof or ceiling load — engineer (SC §5).

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
  2026-10-29: windows in interior walls an open item.)
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
  open outward; a sectional garage door needs ≈ 0,30 headroom; the entrance "0,9" should be the clear passage under an
  accessibility plan (DL 163/2006 — check). Model (`camadas.caixilharia()`, collection 7): the table size centred at the
  frame's outer face, folga 0,025, the box filling above, profiles 6 / 5 cm, glass 24 mm; a warning only beyond 2 × folga
  + 1 cm (smaller misfits shrunk silently — L41); none when an element is much smaller than its opening (L37).
- **Openings stay under the ceiling: the rough-opening top at most the pé direito** (the box top may reach the ceiling line)
  — user 2026-10-22 "Apenas precisamos de 20 cm portanto seria 2,40 de pé direito" (a 2,20 janela de correr + 0,20 estore
  at a 2,40 pé direito) — confirmed (the 2,40) / assumed (as the limit for every opening) — [cfgr] `colocar.js` `topoMax` =
  pé direito − the box (0,20 to the floor; 0,125 over a window's frame top) or − 2,5 cm, every roof; `para_construtor`
  notes a rough top above the pé direito; `casa_planta` does not check. (was pé direito − 0,10 hidden / − 0,16 exposed —
  ours — until 2026-10-22 / 28.) Interior doors fit from 2,40.
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

## 5. Floor between storeys
- **Two storeys: the wall modules are built the same way on both storeys** — user 2026-10-20 (night) "emtermos de paredes
  nada muda e o segundo piso eu já expliquei no outro chat como era composto o segundo piso" — confirmed —
  `estrutura_dc.py`; the builder from a plan and the configurator: single storey first ("começamos com térreas e depois
  avançamos para dois pisos", 2026-10-20). Module heights per storey: PO Q5 (Casa CL 2,97 / 3,52 reference).
- Joists 220×75 solid, on edge, wall to wall, **≤ 0,615 m** apart (equal division; 3_Vigamento 0,614 over 4,90,
  continuous over an interior wall) — user 2026-10-09 "Floor joists is also 22x7,5"; 3_Vigamento (2026-10-15 "representa
  bem o nosso vigamento base") — confirmed + company document — JSON `estrutura.pavimento.vigas.espacamento` 0,615.
- Closer joists: **0,50** where they span ≈ 4,8 m free; **0,466** beside the stair — 3_Vigamento — company document — not
  in the tools ([SB] living room ≈ 4,7 m at 0,61 marginal: 0,50 asked, SB #6).
- No main or central beam: the normal joisting also over big rooms — user 2026-10-15 "leva o teto falso e o vigamento
  normal de 22x7,5 e 11x7,5 nada muda" — confirmed — JSON `estrutura.pavimento.vigas_principais` false (L11).
- Sometimes glulam joists, sometimes à vista — user 2026-10-09 "Sometimes on the floor joist we use vigas lameladas which
  some times can be à vista" — confirmed (when: OPEN — **PO Q10**) — not in the tools.
- Barrotes 110×75 flat on the joists, perpendicular, **0,60 centre to centre** — user 2026-10-09 "put the 11x7,5 at 60
  cm"; 2026-10-13 "sao medidos em eixo" — confirmed — JSON `estrutura.pavimento.barrotes`.
- Mineral wool 100 mm between the joists — user 2026-10-09 "The insulation is 100 mm mineral wool"; 2026-10-13 "fica entre
  as vigas" — confirmed (laid on the ceiling below — assumed) — JSON `tetos.la_pavimento`.
- OSB 22 deck, then vinyl — user 2026-10-09 "with then OSB 22 and then the vinyl" — confirmed — JSON
  `estrutura.pavimento.osb`, `pavimentos.acabamento`.
- No rim joist (viga de bordadura) across the joist ends at the façades — user 2026-10-15 "não" — confirmed —
  `estrutura_dc.py`. What closes the joist bays there: OPEN.
- Stair opening: a trimmer across the joists + short joists at 0,466 to the wall (3_Vigamento "ZONA ESCADAS" 3,478 ×
  2,605) — company document — partly in `estrutura_dc.py` (trimmers + header, not 0,466).
- The extra floor depth goes up: everything above rises, clear heights stay — user 2026-10-09 "yeah no problem raise the
  roof" — confirmed — `estrutura_dc.py`.
- Floor over an open porch = an exterior floor (insulation, airtightness, closed ventilated soffit with insect mesh) —
  general practice (SC §2a ⚠5). Porch: glulam 200×100 beam (6,00) on glulam pillars 200×100 (2,52 high) — 3_Vigamento,
  company document; steel post bases keeping end grain off the slab — general practice. Not in the tools.

## 6. Ceilings (tetos)
- **Top floor: a flat false ceiling at the height of the viga de amarração; it does not follow the roof** — user 2026-09-30
  "has a fake roof at the height of the viga de amarração" — confirmed — `estrutura_dc.py`, `casa_planta.py`,
  `camadas.tetos`. **It comes with every roof, hidden or exposed** (never a separate option) — user 2026-10-22 "Quando se
  aplica a cobertura automaticamente o teto falso já entra também" — confirmed / assumed (flat under exposed roofs too, no
  vaulted ceiling; PO Q9 "teto falso em toda a casa"). [cfgr] **It must show**: a "Teto" toggle draws it from the engine
  (`camadas.tetos`, the Pladur underside at the pé direito) — user 2026-10-28 "O testo falso ainda não aparece no builder
  e quero que isso seja possível de aparecer" — confirmed (L48).
- **Vigas de apoio ao teto 220×75 casquinha branca, 1 m apart** (3_Vigamento 0,989 = equal division), **always down the
  slope** ("sempre inseridos no sentido da cobertura"), eave wall to eave wall, on the amarração and the interior viga de
  amarração; on a hidden roof between the exterior modules' inner faces (§4); **free span up to 8 m** (§13) — user
  2026-09-30; 2026-10-09 "spacing is 1 meter"; 2026-10-15 "O nosso limite é precisamente 8 metros" — confirmed — JSON
  `estrutura.vigas_teto`; cfg `cobertura.vigas_teto` (zones). Beams, glulam zones, exposed ceilings per house: **PO Q9**.
- **"Down the slope" on a roof with more than two águas** (exposed roofs) — ours (our reading of "always down the slope";
  to confirm with a sketch, §15) — `telhado_estrutura.construir`, `telhado.py` ("zonas"); checked by
  `ferramentas/configurador/auditar_cobertura.py` (E11):
  (a) **L / T / U with 2 águas per wing** (the "Duas águas" card, the wings of `misto`): each wing's beams across its own
  width, perpendicular to its ridge — the beams turn 90° from wing to wing;
  (b) **hip end** (4-água ends, the `misto` body's ends): the beams keep the main direction; the hip end's purlins run
  parallel to the beams, each purlin line on one beam, on short prumos at ≤ 1,0 along it (or on a trimmer);
  (c) **under a wing wider than its body's depth, where the wing's roof crosses the body, the beams run down the WING's
  slopes** (a header on the open side, below) — 2026-10-28 (his U: the bar's beams had stayed, 3 m of purlin bare, L51);
  (d) **wherever purlins run with the beams below** (a hip end, a narrower wing's end over its body, a crossed body's
  slope) they lie on the beam lines on prumos ≤ 1,0 along the beam, joints over a prumo, and **a beam is added right under
  the top purlin of such a slope**, the bays either side equal and ≤ the spacing;
  (e) **a beam beside an edge beam carries no second purlin**.
- **Where a wing opens into the body, the body's beam ends bear in external-flange joist hangers ("estribo de asa
  externa")** (galvanised U seat with outward perforated flanges, e.g. Esteba "estribo alas exteriores tipo B" — his
  photo) — user 2026-10-22 "…normalmente nós utilizamos um estribo de asa externa que é neste caso onde as vigas da
  cobertura realizam a sua descarga" — confirmed — **fixed to a header along the open side, wall to wall** — user
  2026-10-28 "Prendem-se as vigas laranja" (the sketch `configurador/docs/juncao_ala_estribos.svg`, its orange glulam "viga
  de bordadura") — confirmed — `telhado_estrutura.construir` (`cabecas`, "Viga de bordadura", between the edge beams on
  the side walls). **Ours** (not said): its section — the engine's standard glulam 200×100 (JSON `estrutura.lameladas`) is
  ⚠ shallower than the 22×7,5 (220) it carries → at least the beams' depth and ≥ the hanger height; its bearings — each end
  a point load: posts under it to the base, no module joint there, never through the module; its size per span — past ≈ 4
  m of opening the engineer (X4, §13). He asked why ("Porque razão? Explica-me melhor por favor", 2026-10-28) → explained
  the same day (a header shallower than its beams cannot take the hangers' full height; each end carries half the
  opening's roof); his reply OPEN; the rule stays ours (the engineer's per house). Hangers (general practice, CM §6): every hole fixed with the maker's nails / screws,
  seat as wide as the beam (75 / 100), height ≥ ≈ 0,6 × the beam, galvanised. Hangers and end posts not modelled or counted
  (X4). ⚠ The sketch labels the beams "a cada ≈ 0,60 m" — the rule is 1 m: fix if reused.
- **Past 8 m: glulam lameladas 20×10** (200 deep × 100 wide), down the slope, between the exterior modules' inner faces
  on the ring (§4), **in equal bays ≤ 0,92 between the end walls' axes** ([TV] 19 × 0,915 over 17,39; 11 × 8,50 + 7 × 11,00
  nominal, 8,28 / 10,78 inner, cut to fit) — D2503 sheet 1 (revision C "Cobertura - Vigas de 16x8 para 20x10"; labels still
  "16x8", TV #11) — company document (one house) — JSON `estrutura.lameladas`; cfg `cobertura.estrutura` "lameladas"
  (from a plan the builder does not choose glulam by span itself). They bear on the interior modules they cross (§4).
- **One beam system for the whole house once any span passes 8 m** — [cfgr] `para_construtor.py` (`LIMITE_VIGAS` 8,0;
  the U 11,60 × 18,50: lameladas 6,35 over the middle too) — assumed (ours; [TV] every span > 8 m, so D2503 does not show a
  mix) — to ask (cost). Exposed roofs choose per rectangle instead — X2.
- **On every hidden roof the false ceiling hangs below the amarração ring, from the ceiling beams by the perfis de teto and
  the calhas (réguas) de suspensão** — user 2026-10-21 "Sim como já te tinha explicado nos chats anteriores os tetos
  falsos ficam presos as vigas de 22x7,5 através dos perfis de teto e das calhas de suspensão que até cheguei a mandar foto
  delas" — confirmed / assumed (the drop: ring 0,11 + 8,5 mm = suspension 0,1185, ceiling ≈ 0,148 under the beams, as TV)
  — `camadas.teto_sob_anel` (every hidden roof; used by `casa_planta.main`, `camadas.gerar`, `motor.worker.js`),
  `para_construtor.py` 0,1185, TV cfg. JSON `tetos.suspensao.folga` stays 0,027 (exposed roofs). [TV] ceiling at 2,50 ≈
  0,15 under the lameladas; OSB 15 up to the ring (2,543), Pladur to the ceiling — D2503.
- **Réguas de suspensão (= calhas de suspensão) fixed upright to the side of each ceiling beam (or floor joist) hold the
  perfis** — user 2026-10-09 "are placed vertically onto the vigas de apoio ao teto and hold the fake roof" — confirmed (one
  per perfil per beam, 30 wide — assumed; photos `fontes/produtos-teto/2_regua_suspensao_teto_falso.png`, SC §5) — JSON
  `tetos.suspensao`. The gap: 0,027 under exposed roofs, 0,1185 under hidden ones, and on an exposed roof raised for a
  high head 0,027 + the raise (≈ 0,19 / ≈ 0,34, §3) → the régua's length must reach it (model and length OPEN) — not
  checked in the tools.
- Perfis de teto in steel at 0,40 — confirmed (steel) / assumed (≈ 47×17, spacing, bar length) — JSON `tetos.perfis`.
- **Cantoneira 30×30×0,5 steel screwed round the perimeter of every room, bars of 3 m** (e.g. Pertecno, Leroy Merlin
  15953000) — user 2026-10-09 "it has a fixed 3 meter of lenght so we gotta make calculation" — confirmed — JSON
  `tetos.cantoneira`.
- Ceiling metal is steel — user 2026-10-09 "steel those are the ones we use" — confirmed — JSON "Aço galvanizado".
- Perforated angle only on "hard corners" (outside corners) — user 2026-10-09 "only on hard corners" — confirmed (what it
  does: OPEN) — not in the tools.
- Pladur N 13 below (H1 in wet rooms, F near heat; wood possible) — user 2026-09-24 — confirmed — JSON `tetos.acabamento`
  (H1 / F not assigned to rooms).
- Wool on the top-floor ceiling: **100 mm Volcalis** on the false ceiling between the beams (cold attic) — user 2026-10-09
  "we use 100mm mineral wool volcalis on the roofs aswell" — confirmed — JSON `tetos.la`. Vapour control under it and a
  ventilated attic — general practice (SB #16).
- Every part of a room's ceiling gets Pladur and wool, thin strips included (only no perfis) — user 2026-10-15 "tem um gap
  no meio da sala" — confirmed — `camadas.tetos` (`fino`) (L4).
- Wall linings go up to the ceiling: Pladur to the false ceiling, OSB 15 to the beams (or the ring) — confirmed (L10) —
  `camadas.py`.
- Exposed ceilings (vigamento à vista): glulam 200×100 at 1,02 (3_Vigamento) — company document — not in the tools; the
  build-up over them: OPEN.

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
  assumed). Not said: thickness, PUR / PIR, skin, colour (dark grey RAL 7016 provisional) — **PO Q15**. From Mundiperfil's
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
- [cfgr] **Only exposed roofs with empenas à vista are offered**: a **rectangle: Escondida · "Duas águas, com empenas à
  vista"**; an **L / T / U: Escondida · "Duas águas, com empenas à vista" (every free end an empena, engine `duas_aguas`) ·
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
  ours — `telhado_estrutura.construir`, checked by `auditar_cobertura.py` (E11): (1) **every purlin stops against the side
  of the rincão / laró member, its end fixed with estribos (hangers)** — user 2026-10-28 "estribos." (asked how the purlin
  ends are fixed) — confirmed; the product (skewed / sloped hangers, or square ones with a bevelled purlin end): OPEN, ours
  (CM §6); not modelled or counted (X9); (2) members meeting at a point stop at the bisector; (3) **over the house a
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
  façade) — assumed. **Verge (empena) overhang 0,12** ([SB], "≈ 0.10–0.12 m from the frame") — ours as the default, not
  asked — JSON `cobertura.empena`; **below the 0,20 minimum if the range covers the verges — OPEN**. A 0,50 eave is a
  panel cantilever → Munditelha's table (general practice: check past ≈ 0,3–0,4).
- When the DiscoverCasa structure raises the roof: keep the pitch or the ridge — [SB] OPEN (user 2026-10-15 "para ja ainda
  nao vou tomar essa decisão", SB #22) — JSON `estrutura.cobertura_manter` "inclinacao". Hidden roofs: the ridge rises
  (Hidden roof); configured houses: the client's slope kept, the ridge follows (ours).
- **No gap between the roof and the walls** — the façade layers and the empenas run up to the panels' underside — user
  2026-10-22 "há um gap que fica visível entre o telhado e as paredes que não quero que esteja assim porque não corresponde
  à realidade" — confirmed — `camadas.sob_faces` (gables included) ✓; [cfgr] `cena.js` (L48). How the eaves line is closed
  (cladding to the panel, a profile closure / comb filler, a vent with insect mesh for the cold attic): OPEN — general
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
- **E4 Purlins 110×75**, parallel to the ridge, **≤ 1,2 apart** in equal bays, laid flat and tilted to the slope; **the eave
  purlin on the beams right over the wall** (its outer top corner at the frame's outer face); the top purlin of each slope
  0,05 from the ridge line (a 0,10 gap); **each line one piece across the house, jointed over a beam** (L47), **running past
  every empena by the verge 0,12**; every purlin stops against the side of a rincão / laró member, fixed with estribos
  (2026-10-28; product OPEN) — user
  2026-09-30, 2026-10-09 — confirmed (purlins, spacing, eave one on the beams) / assumed (flat, tilted, the gap, the verge)
  — JSON `cobertura.vigas_apoio`, `cobertura.empena` 0,12. **Not the engineer's [SB] 80×160 rafters on an 80×160 frechal**
  — the drawings' structure (cfg `estrutura.sistema` "desenhos"), not the method (L9). Engine ✓; continuity and lengths X8,
  X9.
- **E5 Ridge**: no ridge beam — the two top purlins carry the panels' ends, a ridge cap (≈ 0,20 each side) over the joint,
  **folded down both slopes onto the panels ("coladas", 2026-10-28 — Covering)**; ridge height = eave purlin top + run × slope (≥ 15 %) — draft "Cumeeira (2 águas)" — company document / assumed (no ridge
  beam) — `estrutura_dc.py`, `camadas.cobertura`. Caps ordered by count, as D2503 ("ENCOMENDAR 18 CUMEEIRAS") — ours. Engine
  ✓; counted in metres — X12.
- **E6 Empenas**: a framed triangle on the gable wall's amarração — bottom plate 35, sloped top plates under the purlins,
  110×75 corner posts, 110×35 studs at 40 cm clear, a stud under the ridge — user 2026-10-09 "its fine like that" —
  confirmed — `estrutura_dc.emoldurar_empena` (every gable wall; every wing end). Clad outside like the façade up to the
  panels (L5); no wool (cold attic); inside unlined — assumed ([SB] model). Engine ✓ (on an edge beam — X5; a gable over a
  lower wing — X7; inside not checked).
- **E7 Panels**: Munditelha (above), **one length per slope** from the eave edge (frame face + beirado) to the ridge, laid
  from one end, screwed to every purlin (Turbosharp 6×160), sealing tape between panels, remates laterais on every empena
  — draft + user 2026-10-22 — company document / confirmed — `camadas.cobertura`. Closures under the profile at eaves and
  caps — general practice — not in the tools. Engine: faces ✓; one area per face, no lengths, widths, waste or closures —
  X11.
- **E8 Gutters and downpipes**: an **exterior gutter along every eave** under the panel edge (draft "Caleira exterior e
  tubos de queda"; 125×90 assumed), falling to its outlets (general practice ≈ 0,3–0,5 %); **2 downpipes per gutter, 0,30
  from its ends** (3_Vigamento's "2 tubos de queda" — ours for every eave), sized ≈ 1 cm² per m² of roof (an 80 mm pipe is
  plenty for ≈ 18 m²), on the façade with a swan-neck and brackets, **ending ≈ 5 cm above the base** (user 2026-10-16 "o
  fim do tubo de queda não pode estar tapado pela base de fundação" — said on a hidden roof, for every downpipe our reading)
  — company document / assumed (sizes, positions, route) — JSON `cobertura.caleira`; `camadas.cobertura`. **Every downpipe
  joined to its gutter** — a piece from the outlet in the gutter's bottom down and back to the pipe's top (a swan-neck) —
  user 2026-10-28 "os tubos de queda não estão conectados as caldeiras" ("caldeiras" = the gutters, our reading) —
  confirmed (the fault) / ours (the piece) — `camadas.cobertura_faces` (`ligacao`) (L54). **Outside or inside the
  cladding on an exposed roof: OPEN** (inside is the method on hidden roofs). Engine ✓ on every eave, laid level — X14,
  X15; drawn on the configurator's screen from the same layers (2026-10-28).
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
  rincão / laró), free ends ≤ 0,75 (an end fixed to a rincão / laró side counts as borne), every prumo on a beam, slope
  coverage (panels ≤ 1,30 between purlins, ≤ 0,25 short of the ridge, ≤ 0,70 past the eave purlin). ⚠ Looser than the
  rules and short of the screen's range — X19. Checked by no tool yet: gutters / pipes per eave and laró foot, empenas
  framed and clad, the laró slope vs the panel, the opening heads (X16).

### Hidden roof (cobertura oculta)
- **Hidden by the house walls, in ONE água where it works — the best solution per house, not a pattern** — user
  2026-10-15 "Cobertura é escondida pelas paredes da casa"; 2026-10-28 "Aqui depende do caso, nós tentamos sempre só fazer
  uma água e sempre coberturas ocultas"; on his U (a short middle part) "fariamos apenas uma água para a cobertura toda";
  "Não quero que assumas um padrão mas sim a solução mais eficaz e inteligente para cada caso" — confirmed — cfg
  `cobertura` (`tipo` platibanda, `uma_agua`, `cumeeira_y`, `aguas`, `inclinacao_pct`); `casa_planta.construir`. Hidden or
  exposed, and the gutter side: **PO Q14**. [TV] **two slopes** ("Sim é de duas águas", 2026-10-15; D2503) — a project
  fact (TV cfg); why TV took two when one would have fitted (runs 8,50 / 11,00 < 13,5 — cércea, look, parapet height?):
  OPEN — it tells when one água gives way (§15).
- **How the engine chooses** (ours, built 2026-10-28): **ONE slope** falling across the ceiling beams to the side where
  every strip ends on one straight line (one straight gutter); each strip's panels in one length from that gutter up to
  its own high wall; **a "remate de topo" against the high parapet** instead of a ridge (a flange 0,12 on the panels + 0,10
  up the parapet's roof-side cladding); the house turned so the beams span the shorter depth ("casa rodada 90° …").
  **TWO slopes** — one ridge along the house through every strip, in the middle of the main block (the biggest rectangle,
  D2503's rule) as near as that allows, every slope ≥ 1 m — only when one slope's panels would pass the panel's maximum
  (JSON `cobertura.painel_oculto.comprimento_max` **13,5** — ours, a truck's length; the maker's: OPEN) or no side is
  straight. **The gutter side: where both long sides are straight (a rectangle) the client chooses it** (configured-house
  `cobertura.lado_caleira`, the configurator's compass, +y north), only among the sides across the ceiling beams (the
  beams span the shorter depth; on a turned house poente / nascente); default south (poente on a turned house); an
  impossible choice falls back to the default with a note; L / T / U (one straight side) and two-água houses (panels over
  13,5 m) get no choice — user 2026-10-29 "Podes deixar o cliente escolher" — confirmed (the default: ours) — (superseded
  2026-10-29: "gutter on the south — assumed", PO Q14) — the form: assumed — `para_construtor.cobertura_escondida`
  (`uma_agua`, `cumeeira_y`, `aguas`, `vigas_teto` zones, `lado_caleira`), `rodar`;
  `casa_planta.construir` on 22×7,5 and on lameladas (one plane, a top madre / purlin against each strip's high wall, no
  ridge pair); `camadas.cobertura_platibanda` (remate de topo). 9 shapes audited: 8 in one slope, a 14 × 14 square in
  two; his U 18,95 × 12,65 one slope, parapet 3,82. *Why the 1 m* (two slopes): at the band's edge the ridge fell on a
  wall line (a slope of nothing, a cap on a parapet). (superseded 2026-10-28: "the most efficient = one ridge, two slopes
  mid main block" — the morning's reading of "a forma que seria mais efeciente", now only the fallback.)
- ⚠ **What one água changes** (ours — to tell, §15): (a) **one gutter takes the whole roof** → downpipes sized by area
  (≈ 1 cm² per m²: two 80×35 cavity pipes ≈ 26 cm² each serve ≈ 50 m² — far less than his U) → more pipes or a deeper
  recess, and **an overflow** (one blocked outlet floods the whole gutter); (b) **the high wall's upstand above the panels
  is small** (`platibanda.folga` 0,05 along its whole length; usual abutment ≈ 150 mm) → the remate de topo up under the
  chapéu's inner leg, a closure under it, or the parapet raised there; (c) the parapet grows with the run (3,82 vs TV
  3,49: longer studs, a taller cantilever above the ring, the cércea, cladding, price — §2); (d) panels up to 13,5 m:
  steel-skin expansion ≈ 10–12 mm on a dark 12 m panel, the maker's fixing rules.
- **Slope: the lowest the panel allows; the ridge — and the house — rise as needed** — user 2026-10-16 "faz com uma
  inclinação do mínimo que é permitido sendo que se a cumeeira tiver de subir pode subir, eu sei que isto altera a altura
  total da casa mas não tem mal é o suposto nestas coberturas escondidas" — confirmed — cfg `cobertura.inclinacao_pct`; no
  panel minimum in the JSON, no check. [TV] **6 %** on every slope (architect's section B 1,3 %) — D2503 — TV cfg
  `inclinacao_pct` 6,0. ⚠ 6 % > Masterpanel's 5 % but < the ≈ 7 % (4°) Kingspan KS1000 RW / Europanels give → the maker of
  the panel used decides (TV #8; which panel: not asked).
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
  (TV #4). ⚠ To check (ours): the remate de topo's 0,10 upstand vs the parapet's 0,05 over the plane's top — at the
  highest wall it may stand ≈ 5 cm past the parapet top, through the chapéu (X20).
- **Covering: 5-rib (5 ondas) sandwich panel 80 mm**, 1 m useful, lengths from the project, ridge (2 águas), sealing tape,
  Turbosharp 6×160 — draft — company document — JSON `cobertura.painel_oculto`. Maker, thickness, colour and the chapéu
  colour per house: **PO Q15**.
- **Panels: one length per slope** (no end laps; [TV] 3,94 north and main-block south, 6,44 over the wing), **laid from one
  end with the cut strip at the other** ([TV] from the east, a 3,94 × 0,25 strip at the west); at the re-entrant corner
  one long panel **cut in an L** ("PORMENOR TELHA PARA REMATE": 3,94 + 2,50 × 0,47, 0,53 cut off); **ridge caps ordered by
  count** ("ENCOMENDAR 18 CUMEEIRAS" for 17,5 m); the panels run ≈ 0,10 past the gutter madre into the gutter — D2503 sheet
  4 (it calls the panels "telhas") — company document — `camadas.cobertura_platibanda` (from the east end; [TV] 30 × 3,94 +
  7 × 6,44), JSON `estrutura.madres.beiral` 0,10; the ridge cap (two slopes) folded onto the panels ("coladas", Covering),
  counted in metres — X12-like, not by count. One água: one length per strip, the remate de topo at the top.
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
  face to the top (Parapets, below): with the 80 cm sheet a second piece lapped over the 0,30 leg or a wider sheet — OPEN,
  low priority. At the main-block south gutter's high end its bottom (0,22) is above the madre's 0,15 packing — reread.
- [TV] **Site photos (2026-10-19)** — user "afixei também imagens reais de como ficou a cobertura"
  (`Construção Torres Vedras/docs/revisao-modelo/2026-10-19_obra_caleira_*.webp`): an **OSB box** along the parapet (= the
  draft's OSB 22 — our reading), a **red (tile-colour) lining**, end plate turned up, corners and outlet sealed, the **outlet
  a round hole in the gutter bottom near the end**, no overflow — our reading (not stated as rules, L14). Tools' deviations:
  no board under the lining on lameladas; the lining dark grey (JSON "Caleira" #3A3F43).
- Caleira oculta as the tools build it **on 22×7,5 ceiling beams** (from TV v3; differs from D2503): a 110×75 flat on the
  beams, OSB 22 from the parapet face to the roof side of an upright 110×75 (30 + 7,5 cm), channel 30 wide, 110 deep on the
  longest slope, lining up the parapet frame face to 2 cm under the chapéu and up the upright, end caps, panels 5 cm in,
  channel flat — assumed — JSON `cobertura.caleira_oculta` (`largura` 0,31, `altura` 0,11). Where the flat 110×75 goes (the
  OSB's parapet edge has no bearer), an overflow: OPEN.
- Caleira interior 20 cm with 2 downpipes along one long side (3_Vigamento) — company document — not in the tools; the
  same as the caleira oculta (20 cm vs 30 in the draft vs 0,31 at TV, per project?): OPEN — **PO Q16** (default 0,31).
- **Downpipes INSIDE the exterior cladding, hidden by the Tremolo — never inside the rooms** — from the gutter through the
  parapet into the batten cavity and down the façade — user 2026-10-16 "…não é suposto mas é suposto estarem por dentro do
  revestimento exterior mas escondidos pelo tremolo" — confirmed; **the method**, re-confirmed 2026-10-20 "pois nós nesta
  obra fizemos de forma diferente mas a forma como modelaste no blender por dentro do revestimento é a forma correta" and
  (13:25) "nós achamos que por dentro é mais correto e fica melhor" — confirmed (preference) — `camadas.tubos_queda`,
  `camadas.cobertura_platibanda`. [TV] **as built: outside the cladding** (finished photos — SE and NE corners with box heads,
  the face beside the garage; TV #9) — a project fact (L40). How the pipe leaves the gutter: next lines. As the tools
  place them: at cfg outlets, else 2 per gutter 0,45 from its ends, ≥ 0,15 clear of openings; section 80 mm × the cavity
  depth ([TV] ≈ 33; ≈ 53 with the contra-ripado); a horizontal piece through the parapet just above the gutter bottom;
  battens stop at the pipe — assumed — JSON `cobertura.caleira_oculta.tubo` (`largura` 0,08), `.tubos` 2. **Conditions
  that make the inside route work** (general practice, our advice 2026-10-20 13:25; CM §4, SC §6): (a) size the pipe for its
  roof (≈ 1 cm² per m²; [TV] ≈ 37–46 m² per pipe → the 80 × 35 cavity pipe ≈ 26 cm² is too small, 100×35 ≈ 32 still short
  → a local recess with deeper battens for ø80 (≈ 50 cm²) or 100×50, never a cut in Traspir / OSB 9 / wool, or two pipes);
  (b) one continuous pipe or sealed joints, a sealed bocal and collar at the parapet, Traspir taped round; (c) an inspection
  point at the top, a leaf guard at each bocal; (d) an overflow at every hidden gutter; (e) the foot into the drain or a
  gully — the company's section and overflow: OPEN, **PO Q16** — not in the tools.
- **Downpipes end slightly above the foundation base**, never covered by it — user 2026-10-16 "o fim do tubo de queda não
  pode estar tapado pela base de fundação tem de estar ligeiramente acima para a água poder sair do tubo de queda" —
  confirmed (5 cm assumed) — JSON `cobertura.caleira_oculta.tubo.folga_base` 0,05. Where the water goes then: OPEN — **PO
  Q16**. ⚠ A shoe throwing it ≥ ≈ 0,3 m onto a splash block / gravel, or a gully — general practice (TV #9, #16).
- **Downpipes at the gutter outlets — the low ends of each gutter's fall** ([TV] 4: north 2, main-block south 1 west, wing
  1 east), ending 5 cm above the base — user 2026-10-16 (night) "como esta desenhado está perfeito" — confirmed (the method,
  not TV as built — L40) — TV cfg `cobertura.caleiras.*.saidas`; `casa_planta.construir` (outlets ≥ 0,10 clear of openings).
- **Every hidden gutter has an outlet hole in its lining at each downpipe, at a low end, the pipe inside the gutter's
  length; a downpipe without its hole is a model error** — user 2026-10-20 (≈ 13:51) "um erro que esta presente é nas
  caleiras nao existem os buracos par agua escoar para os tubos de queda" — confirmed / assumed (at the low ends, inside the
  length) — `camadas.tubos_queda` (`furo_z`: a hole 0,08 wide × 0,06 from the gutter bottom, flush outlet; with cfg
  `saidas` the pipe clamped inside the gutter), `camadas.cobertura_platibanda` (lining cut round each hole) (L43). ⚠ Without
  cfg `saidas` the fallback is placed by the ends, not the falls. Validation wanted: every downpipe meets a hole at a low
  end, every low end has a downpipe. Not in the tools: bocal, sleeve, leaf guard, overflow.
- **Which gutter outlet — sideways through the parapet into the façade cavity (the tools' default) or a round hole in the
  gutter bottom ([TV] as built) — and its size and fitting: OPEN, promised** ("isso depois eu digo a informação não sei
  neste momento", 2026-10-20 night) — **PO Q16**; flag "a confirmar" in deliveries — JSON `cobertura.caleira_oculta.tubo`,
  `camadas.tubos_queda` (side only). General practice: a side outlet keeps joints out of the roof void but crosses the
  parapet module → a pre-formed outlet sealed to the lining, a sealed sleeve falling outward, Traspir taped, studs set clear
  (§0a); a bottom outlet drops into the void and must turn through the wall (unseen joints); either way a leaf guard and an
  overflow.
- **Overflow (ladrão)**: through the parapet near each outlet and at the high end, below the gutter's lowest rim, spilling
  where it is seen — general practice (CM §4, SC §6, TV #4 g, #15); [TV] the madre side at the high end only ≈ 4–5 cm above
  the bottom. Asked 2026-10-20 night — user "explica-me o que é um ladrao mas penso que não" → **tentatively none**
  (agrees with D2503 and the photos); explained and recommended, **his answer after the explanation pending** — not in the
  tools; flag **"sem ladrão no modelo"** in every delivery (PO Q16).
- **Parapets are clad on the roof side too — an exterior wall on both faces, in the house's own façade finish** (gutter
  walls excepted, next line): from inside out **wool in the frame, OSB 15, Traspir, then the house's façade build-up** (A
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
  side) — user 2026-10-20 "revestimento da caleira até ao topo que depois se encontra com os chapéus da platibanda" —
  confirmed (as D2503's sections; the 2026-10-19 photo was an earlier stage) — JSON
  `cobertura.platibanda_interior.paredes_com_caleira` false; `camadas.cobertura_platibanda`. Junction (general practice, SC
  §6): the chapéu's inner leg laps over the lining's top (shingle order), the fixings under the leg, a membrane over the
  wall top.
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
  aproximadamente para baixo tal como no projeto de torres vedras" ("do lado" read as each side) — confirmed — **flat**
  (D2503 sheet 5; user 2026-10-16 night "Como está feito no modelo mais recente, está ótimo") — JSON `cobertura.chapeu`
  (`descida` **0,02**, `queda` 0, 2 mm); `camadas.chapeus`. (was ≈ 3 cm, `descida` 0,03, until 2026-10-28.)
  Product (sheet, thickness, colour, bar length): OPEN (JSON "chapa lacada", "Remate RAL 7016" assumed). ⚠ A leg tight to
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
  it before he answers. Our view given: tight butt joints of the same colour (folded lengths ≈ 3–6 m). The tools model one
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
  (that it must show) — L48, L52, L53, L56.
- Skylights: [TV] none built — the 2 of the roof plan left out — user 2026-10-16 "Não foram construidas podes não incluir as
  claraboias" — confirmed (TV #10); per project **PO Q17**. How DiscoverCasa frames one (a kerb and flashing on a low-slope
  panel roof — general practice): OPEN — not in the tools.

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

## 10. Floors (pavimentos)
- **Finish usually vinyl planks, chosen per room** — user 2026-09-24; 2026-10-22 "a pessoa pode aplicar pavimento que
  desejar na divisão que desejar e não ter que aplicar ou cerâmico ou vinil na casa toda como está de momento" — confirmed
  — **PO Q20** (default vinyl everywhere) — JSON `pavimentos.acabamento` (5 mm assumed),
  `pavimentos.acabamento_opcoes.ceramico_pav` (mosaico 60×60, 10 mm glued, waste 10 % — assumed, "a definir"); [cfgr] rooms
  found between the walls' finished faces, house file `pavimentos` [{ponto, acabamento}] → `camadas.pavimentos` (one
  collection per finish, levelled to one finished floor).
- Ground floor: vinyl straight on the base (§1); upper floor: vinyl on the OSB 22 (§5) — confirmed.
- Ceramics in kitchens and WCs — company website, not said by the user — assumed.
- At a change of floor between rooms (vinyl 5 / ceramic 10 + glue) a transition profile and the build-ups levelled —
  general practice — not in the tools.

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
  gutter; timber = calços (pieces) on lameladas, the box 2 × 110×75 + OSB 22 on 22×7,5. The downpipe product (section,
  material, bar): OPEN.
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
  minimum ([TV] 6 %) — §7. **Hidden-roof panel in one length ≤ 13,5 m** (ours, a truck's length; the maker's: OPEN) — the
  limit between one água and two (JSON `cobertura.painel_oculto.comprimento_max`) — §7.
- **Exposed-roof overhangs**: beirado 0,25 default, 0,20–0,50, lower per house if a model shows a problem (JSON
  `beirado_min` / `beirado_max`; was 0,55 until 2026-10-28); verge 0,12 (ours —
  under the 0,20 if the range covers verges: OPEN) — §7. A tiled pergola: clay ≥ ≈ 30 % (lower only over a continuous
  sub-roof), tile-effect panel ≥ 10 % — general practice (§8).
- **Caixilharia clearance 2,5 cm each side and in height** by default, "nem sempre" — rough opening = frame + 0,05 wide,
  + 0,025 head + 0,025 under a window (none under a door — assumed) + the maker's box — §3, PO Q11.
- **Downpipes**: 2 per gutter (3_Vigamento, one roof); [TV] one at each low end of a fall (4 for 3 gutters, ≈ 37–46 m² per
  outlet), each with its outlet hole (§7); sizing rule of thumb ≈ 1 cm² per m² (general practice; DR 23/95, EN 12056-3)
  → the tools' 80 × the cavity (≈ 26 cm² at TV) too small; ø80 (≈ 50 cm²) or 100×50 in a local recess, or two pipes — the
  company's section OPEN (PO Q16). [TV] pergola: 2 for ≈ 46 m². **One água: one gutter for the whole roof** → pipes by
  its whole area (two cavity pipes ≈ 50 m²) and an overflow — ours, to tell (§7).
- [SB] Upper-floor clear height 2,40 = RGEU minimum: keep it — user 2026-10-09 "keep it but note it" — confirmed (SB #21).
- **Pé direito**: the client's, any value; 2,40 / 2,50 / 2,60 usual; [cfgr] 2,40 (RGEU DL 38 382/1951 art. 65.º — 2,20 in WC
  / corridors / storage, one height per house here; check the current text, CM §3) to a 3,50 guard (ours), default 2,50
  (TV, ours) — §2. A 2,20 janela de correr + estore fits 2,40 (box 20 cm); under an exposed roof the modules rise for it
  (+ 0,164; 4-leaf ≈ + 0,31; ceiling drop ≈ 0,19 / ≈ 0,34) — §3.

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

## 15. Still unknown or assumed
### Promised by the user (wait; remind only where it says so)
- **What goes under the chapéus** — "Por baixo dos chapéus lembra-me mais tarde para te confirmar o que leva" (2026-10-20
  13:25) → **remind him** in the next message that fits; do not model it before (§7).
- **Which hidden-gutter outlet** (side / bottom) and the **bocal size** — "isso depois eu digo a informação não sei neste
  momento" (2026-10-20 night) (§7, PO Q16).
- **His review of the generated Cobertura and Listagem de material** against D2503, and what the list should look like —
  "ok assim o farei" (2026-10-20 night) (§0a). (Módulos reviewed: correct.)
- **When the ridge madres become 22×7,5** — "Posso te responder a isso depois" (2026-10-21) (§7); our > 9 m trigger meanwhile.
- **A list of interior finish materials** — "Mias tarde vou ter fornecer uma lista …" (2026-10-22) (§9, §11).
- **When the caixilharia standard changes** — "quando o fizermos eu aviso-te" (2026-10-19) (§3).
- **The pergola fixing per project** — "quando for relevante nas pérgolas eu dou-te essa informação" (2026-10-19) (§8).
- **The caixilharia clearance per project** when not 2,5 cm (2026-10-20) (§3, PO Q11).
- The foundation base step by step ("explicarei mais tarde"; an indicative slab for now) (§1); the TV real materials list;
  the price list ("futuramente"; "Isso é um passo futuro", 2026-10-20 night).
### Asked, answer pending
- The **overflow (ladrão)** after our explanation — tentatively none ("penso que não"); "sem ladrão no modelo" flagged
  meanwhile (§7, PO Q16).
- His reply to our corrected answer on the [TV] frame sizes (sent 2026-10-20 night) (§3, TV #20).
- Our 2026-10-22 "Num L quase quadrado em 2 águas, que direção de cumeeira preferes?" (the 1 : 1,6 rule is ours, §7).
- The **header** ("viga de bordadura"): "Porque razão? Explica-me melhor por favor" → explained 2026-10-28; his reply
  (§6, §13; the rule stays ours / the engineer's).
### To ask now (one point per question, with the images / sketch named; §0)
1. **"Apenas com empenas" and misto's rincões** — misto hips the main body: is that "várias águas com empenas", or no rincão
   at all (all-gable)? With it: on an L / T / U is his "duas águas" one ridge and two planes (TV's hidden L) and "várias
   águas com empenas" the cross-gabled roof? — three images (one-ridge L, cross-gabled L, misto L) (§7, E10).
2. (Answered 2026-10-28: misto on his asymmetric U — "Tranquilo depois se necessário removemos essa opção"; kept. If it
   is removed, ask (1) with the images.)
3. **Why TV took two slopes** when one água would have fitted (runs 8,50 / 11,00 < 13,5 — the cércea, the look, the
   parapet height?) — it tells when one água gives way; with it, **the panel's maximum length** (13,5 ours) (§7 Hidden
   roof). (Answered 2026-10-28: "a forma mais eficiente" = one água where it works, per case.)
4. **The rincão / laró detail** — the member (110×75 on edge, ours), caps, caleira de laró, a downpipe at each laró foot,
   and **which estribo at a purlin end** (skewed / sloped, or square with a bevelled end; answered "estribos."
   2026-10-28) — sketch (§7).
5. **The beam directions under multi-água roofs** — each wing across its width, a crossing wing's beams down its slopes,
   purlins with the beams on the beam lines (§6 (a)–(e), ours) — sketch.
6. **The default roof card on an L / T / U** (Duas águas or Várias águas com empenas) (§7).
7. **What goes under the capoto on the parapets' roof side** — OSB 15 + Traspir as TV's list (the engine), or a
   vapour-open board (ours: XPS on both faces under a metal chapéu traps the frame's moisture) (§7 Parapets; the façade
   finish there confirmed 2026-10-28 — L52).
8. **Exposed-roof downpipes**: outside the cladding (the tools) or inside as on hidden roofs (E8).
9. **The verga threshold**: "mais de 3 metros" vs "a partir de 2,8 m-3m" and the 3,00 garage "por norma" — 2,8, 3,0 or
   over 3,0, on the rough opening or the frame (§3).
10. **Does the beirado's 0,20 minimum bind the verges?** — ours 0,12 (§7).
11. **Munditelha per house and its data sheet**: thickness 40 / 50 / 60, PUR or PIR, steel or aluminium, colour (PO Q15);
    from the sheet: minimum slope (15 % faces, ≈ 10,6 % larós), purlin span (≤ 1,2), overhang (0,50), ridge / rincão / laró
    / verge pieces (§7).
12. **Sliding windows of 3 and 4 leaves**: sizes, heights, usually an estore?, which leaves slide (§3).
13. **How the eaves line is closed** (cladding to the panel, a profile closure, a vent with mesh) (§7).
14. **The opening details**: the maker's shutter-box height and a 2,5 cm over the box (2,425 vs 2,40) (PO Q11); the head
    remate at the ceiling edge; the remates' material / colour / sill / inside finish and the **thresholds**; whether the
    janelas de correr get a clearance under them (§3, PO Q23).
15. **The downpipe section inside the cladding** and the chapéu butt joints' sealing (§7, PO Q16).
16. **Lameladas over the whole house** once a span passes 8 m, or 22×7,5 over the shorter spans (cost) (§6).
17. ~~**Windows in interior walls**~~ — CLOSED 2026-10-29: doors only, "ninguém usa janelas nas paredes interiores" (§3).
18. **Interior-wall distances on the screen** — from the base corner to the wall's centre line (ours), or from the
    finished corner to the wall's face as a tape measures it (≈ 0,2 less) (§2 Corners).
### [TV] to ask, low priority (TV comparison)
- The pergola: slope and what is under the ceramic tiles, tile battens, gutter section and material, where the 2 downpipes
  discharge, sections and post bases, the exterior glulam treatment's name (§8, TV #21, #22).
- D2503's interior 2,53 vs the rule's 2,543; 3,50 (module table) vs 3,4915 (roof sections); P01 2,64 vs 2,61; the "16x8"
  labels (TV #6, #11).
- Why 2,21 = 5 bays outside, 1,78 / 2,65 inside (§2); which cut list the factory cut to; the panel count difference (§0a).
- What closes the gable face over the open gutter (model: the end cap to the top); the 80 cm lining above its 0,30 leg;
  how TV's downpipes ran from the bottom outlet to the outside box heads (§7).
- The WC row "trasnparente" vs "Fosco"; the sectional garage door as the standard (PO Q12); whether the engineer also
  covered the 2,00 janelas de correr on P03 / P01 (§3).
- The membranes HOLZ TECHNIC / rothoblaas (TV #18); the pipe stubs through the top band (outlets or overflows?); the batten
  "ladders" (TV #9); the OSB box under the gutter lining — the rule for every caleira oculta? (§7, §8).
- Who chose TV's 2,50 (architecture 2,60) (§0).
### To ask when it first arises (with the module sheet and labels)
- A **door** closer than a pier to another opening — moved or one module (ours: one module, "a confirmar") (§2).
- A table "porta de correr" (no swing drawn) — one of the "duas janelas"? (§2).
- When a site-built module runs longer than its opening needs (PO Q6) (§2).
- Interior modules up to 3 m (2,75 kept); 6-bay 2,65 exterior plain modules — show them (§2).
- A porta-janela de batente — window (estore) or door (none)? (§3).
- A tiled house roof on request — build-up, slope, weight (§7).
### [SB] open (Sobral paused, "estará para avançar brevemente")
- Vigas de amarração on the ground-floor walls under the floor joists (with an afinação?) (§4); living-room joists at 0,50
  (§5); keep pitch or keep ridge (SB #22, §7).
### Not asked yet (worth asking, low priority)
- Battens: contra-ripado section / spacing / on the stud lines; why TV went without and when others do; ripado 35 cm centres
  or clear; cork battens 37,5×35 and round its openings; vertical battens in the outer layer too; batten wood and treatment;
  gaps where battens meet (§8).
- Framing: interior studs 80×35 too?; the Casa CL extra stud vs the escadas; the company's word for the escadas and the
  0,66; how a doorway gap between modules is closed (bandeira) (§2, §3).
- Floors and ceilings: what closes the joist bays at the façades; the wool's height in the bay; exposed-ceiling build-up
  over glulam à vista; 3_Vigamento "Vigas lameladas 16x8 com 7,00m" (10) and the 5 × 7,00 glulam; the perforated angle's
  job; perfil section and bar; régua model and length (the ≈ 0,34 drop, §6); prumo section (§5, §6).
- Timber: the longest 22×7,5 bought; the glulam grade and stock lengths; the beam notch's shape (§4, §11).
- Envelope: ETICS — XPS or a vapour-open board; DPC / treated bottom plates / alcatrão at the base; how windows and doors are
  set in the wall (plane, fixings, tape, sill, head flashing, shutter-box type); the despensa basculante's opening direction
  under its estore (§1, §3, §8).
- Roofs: madres flat or on edge over 22×7,5; the hidden-roof panel used (maker, minimum slope vs 6 %, span for 1,265); the
  chapéu product, drip, vent gap, membrane; the draft's flat 110×75 ("deitada"); caleira oculta 0,31 vs caleira interior 20
  cm (PO Q16); where the downpipe water goes at the foot (PO Q16); skylight framing; site timber as long as possible vs the
  madres ≤ 3,66 (§4, §7).
- Pergolas in general: post bases, sections, treatment, a covered one's covering, slope, gutter (PO Q21) (§8).
### To tell (not to ask)
- Transport / site assembly in the price when the price list comes (§2); past ≈ 3,0 of pé direito the exterior studs want
  the engineer, the Tremolo a joint, Pladur longer boards (§2, §8, §11); a tiled roof on request needs its own build-up (§7).
- **One-água hidden roofs** (§7, ours, one line each): size the one gutter's downpipes by the whole roof area (≈ 1 cm² per
  m²; two cavity pipes serve ≈ 50 m²) and give it an overflow; the high wall stands only ≈ 5 cm above the panels → the
  remate de topo up under the chapéu's inner leg (or the parapet raised there); the parapet grows with the run (his U
  3,82 vs TV 3,49 — cércea, price).
### Ours, not to ask (the engine's / the engineer's)
- The header's section (≥ the beams' depth), end posts and size per span (§6, §13, X4); the encosto header 220×100 (X7).
- The réguas de suspensão for drops up to ≈ 0,34 (§6).
- Name the opening that raises the modules in the converter's note, drop "a confirmar", offer an alternative; the plan path
  to raise as the converter does (§3, X1).
- The audit's range and tolerances (X19); one beam-system rule (X2); fix the sketch's "a cada ≈ 0,60 m" if reused (§6).
- The remate de topo's upstand vs the parapet top (X20); a per-house lower beirado maximum in the cfg (§7); the gutter
  side of a one-água rectangle: the client's (`cobertura.lado_caleira`, user 2026-10-29), default south (ours) (§7).
- JSON keys still to add: the exposed roof types per shape (today only `main.js` `COBERTURAS` / `ORDEM_COB`); `cobertura.caleira`
  with a fall, `folga_base` and pipes per gutter; `cobertura.rincao` / `cobertura.laro` (cap, caleira de laró, member); the
  hangers and their header (§6, X4); the beam-direction rule (§6 (a)–(e)) in `estrutura.vigas_teto`; the audit's limits;
  a per-house `beirado_max` (cfg). (Done 2026-10-28: the parapet roof-side finish follows the façade option —
  `camadas.camadas_platibanda`, L52.)
### For the generator (§0a — points `gerar.py` still takes from the model's assumptions)
- The rough openings: frame (the table tentatively; better the maker's order) + 2,5 cm a side and in height + the maker's
  box on windows; [TV]'s relations do not fit it (§3); a reader for the openings table; the remates and thresholds in the
  module / opening details (PO Q23).
- The corner choice per corner drawn; the made-to-measure interior height; each opening's table item; outlets and downpipe
  crossings on the module elevations; "a confirmar" marks; the stale "entalhe feito em obra" footer (§0a).

### What the builder still assumes or does differently from this rulebook
**With the company's module drawing** (cfg `modulos_reais` → `modulos_dc.py`, [TV] v5 on) `casa_planta.py` takes the
modules as drawn and adds: the beams cut to the inner length (= the rule); "fantasma" parapet panels for the layers; the
plan wall each module matches (P01: the plan's 2,58 for M9, not the elevation's 2,61); the interior modules raised 1,3 cm to
2,543 with the 0,11 viga on top (D2503 2,53: conflict OPEN); the caixilharia of cfg `itens` (folga 0,025, box above,
profiles assumed, the warning only beyond 2 × folga + 1 cm — L41; none when much smaller — L37); the remates (§3, assumed
profiles, no thresholds); the chapéus at the actual corners; the [TV] pergola (v6.3 — §8, sections tentative, posts with no
base, no flashing at the ledger, tiles on the slats).
**Without real modules** (every new house):
- the split by `divisor_modulos.py` (= the rules; the remainder and margins by costs — delegated). Still assumed: interior
  up to 2,75; the smallest module 0,60; a door near another opening kept in one longer module ("a confirmar"); the kind
  window / door from the plan's swing, not the table; openings moved in from a corner post (warned); the stud layout inside
  a module from one end (D2503 lays them from the corner post / jambs);
- corners: X exterior walls through (a builder default, no per-corner choice) (§2, L26);
- exterior openings at the architect's size (cfg `aberturas`, fallback 2,20 doors, windows 1,00 / 1,75) — not from the
  table + clearance (§3);
- no escadas (JSON `estrutura.escadas` not read) (§2, L29);
- on every hidden roof the exterior module modelled in two parts (framed to the ring, a parapet part) (L30); the interior
  modules, the beams on the ring and the ceiling below it = the rules;
- on exposed roofs the exterior module from the clear height with afinação + amarração on top (assumed); the interior top
  piece named "Viga de afinação interior" except with lameladas (naming only);
- the clear height from cfg `niveis.pe_direito` (= the rule); from a plan the openings capped silently under the framing
  instead of raising the modules (X1);
- **exposed roofs from a configured house** (`para_construtor.py` → cfg `cobertura.tipo` "a_vista" with `forma`, `beirado`
  0,25, verge 0,12, `inclinacao_pct` vs JSON 15 %; `casa_planta.py` `a_vista`; `motor.worker.js` "telhado"). Test houses
  (the caller's): L 97 m², U 175 m², rectangle 12 × 8, L_misto / U_misto, the surface audit (2 064 + 1 032 cases), the
  timber audit `--formas` and his U in misto (1 033 objects). Deviations (each to confirm or fix):
  - **X1** (E1, §3) The raise for the highest head is the rule since 2026-10-28 ("opção a"). Left: (a)
    `para_construtor`'s note says "a confirmar" and names the highest rough top, not the opening → name it (e.g. "janela de
    correr 4 folhas, parede S"); (b) `casa_planta` (from a plan) caps the opening silently (`min(z1, Hf − top plate −
    lintel)`) → the same lift; (c) the longer ceiling drop (≤ ≈ 0,34) not checked against the réguas; (d) the screen offers
    no alternative when one opening lifts the house.
  - **X2** (E2, §6) Glulam per rectangle when its **outline length** passes 8,0 (`telhado_estrutura.construir`, `sec = lam
    if vao > 8`) — the rule's limit is the free span (≈ outer − 0,22 → glulam from ≈ 7,78 free) — while the hidden-roof path
    puts glulam over the whole house (§6) — ours both; one rule wanted.
  - **X3** (E2 / E4) Fixed 2026-10-22: a prumo under 3 cm becomes a packing piece "Calço" (110×75) — nothing floats. Left
    (ours): levels from the 22×7,5, glulam zones packed up 2 cm, not a plane set per section.
  - **X4** (E10, §6) The header "Viga de bordadura" along a wing's open side = their way (2026-10-28), between the edge beams.
    Left (ours): (a) its section — 200×100 shallower than the 220 beams → ≥ their depth and ≥ the hanger; (b) end posts to
    the base, no module joint there (not modelled; the divider does not know them); (c) size per span past ≈ 4 m —
    engineer; (d) the hangers — one per beam end, not modelled or counted.
  - **X5** (E6, E9) An **edge beam "Viga de bordo"** 22×7,5 (0,075 wide since 2026-10-22, centred on the frame) on every
    wall the beams run along; the empena and the hip-end eave purlin stand on it — ours (E6 says the wall's amarração; [SB]
    beam 0 over the gable wall is the precedent).
  - **X6** (E9, §6 b) Fixed 2026-10-22: hip-end purlins on the beam lines, prumos ≤ 1,0.
  - **X7** (E10) The engine's L / T / U joins (§7): no rincão at an L's outer corner (E10's alternative); the half-width run
    into a hipped end; the squarish-body threshold 1 : 1,6 (ours); the gable **encosto** (a case the rulebook does not have —
    a 220×100 header, not a standard section, not sized; "Fachada Encosto" cladding; flashing 0,20); a wing wider than its
    body takes the beams under the crossing (2026-10-28); **misto on a U whose arm is the biggest rectangle** hips one arm,
    gables the other (told 2026-10-28: "Tranquilo depois se necessário removemos essa opção" — kept) — a U might rather
    take the bar as the body (ours).
  - **X8** (E10, L47) Closed 2026-10-22: one slope = one plane — one set of purlins and one panel run across coplanar faces.
  - **X9** (E4, §11) Each purlin line one piece per continuous stretch (the U's ≈ 18,5 m) — no joint at a stock length;
    purlins stop against the rincão / laró side (fixed with estribos — 2026-10-28; not modelled or counted); purlins
    with the beams jointed over a prumo. Left: stock lengths, the estribos — ours.
  - **X10** (§7 larós / rincões) The member 110×75 on edge under the line (dropped at a rincão so both faces clear it), on
    prumos where it crosses the beams; bisector at a meeting point; foot on the beams, free over the overhang (≈ 0,71 at
    0,50 — X19); a beam past a rincão's top; one prumo per place — ours (general practice also allows purlins mitred on a
    prumo); bias cuts and the caps' seat not detailed.
  - **X11** (E7, §11) Panels one object and one area per face; no 1,0-wide count × length per slope, no bias waste, no
    closures — the order unit missing. JSON Munditelha since 2026-10-22; `para_construtor` still passes `painel_espessura`
    0,08 for the heights while 0,04 + 0,045 = 0,085 — one value wanted.
  - **X12** (E5, §11) Ridge caps, rincão caps, verge trims, abutment flashings and gutters in metres, not counts.
  - **X13** (§7 larós) The caleira de laró a flat 0,50 strip at the purlin-top level — no channel, support or lift.
  - **X14** (E8) Gutter 125×90 on every eave ✓ but laid level, centred under the panel edge; runs joined only in line — at a
    4-água corner or a laró foot two separate runs.
  - **X15** (E8–E10) 2 downpipes per run, 0,30 from its ends (= E8) → a 4-água rectangle gets 8, two ≈ 0,6 apart at each
    corner (E9: at the corners); at a laró foot two pipes 0,30 off the corner instead of one; a run under 1,0 m gets none;
    no check by area or against openings; 0,10 out from the frame, from 0,05 above the base ✓; the swan-neck counted (+ 0,25
    m) not drawn; no brackets; outside the cladding (E8 OPEN). The screen draws the same pieces (2026-10-28).
  - **X16** (E11) `validar.py` checks geometry only (structure under the roof plane, layers outside the frame, covering on
    its supports; lets "Fachada Encosto" stand over the footprint) — "0 issues" missed X3 and L51's 160 clashes. The timber
    audit `auditar_cobertura.py` now covers clashes, bearings, prumos, slope coverage. Left: gutters / pipes per eave and
    laró foot, empenas framed and clad, the laró slope vs the panel, opening heads; neither tool runs by itself in the build
    (ours: add the audit to the configurator's test run).
  - **X17** (E4, E7) Verge 0,12 ([SB], ours) and beirado from the frame's outer face = JSON defaults; the beirado range
    0,20–0,50 in the JSON, clamped by `para_construtor` and the screen (`main.js` `BEIRADO`, 2026-10-28 ✓); the verge
    under 0,20 if the range covers verges.
  - **X18** Fixed 2026-10-22: `telhado.py`'s docstring says 15 %.
  - **X19** (E11, §13; 2026-10-28, ours) The timber audit's range: (a) tolerances looser than the rules (1,30 vs purlins ≤
    1,2 and prumos ≤ 1,0 — a 1,25 bay passes); (b) the sweep runs at 15 % / 0,25 and 40 % / 0,40, pé direito 2,50 — not
    the 0,20 / 0,50 beirado ends nor 2,40 with a raised module; (c) at the 0,50 maximum a misto rincão foot runs free
    ≈ 0,71, inside the audit's 0,75 (was ≈ 0,78 at 0,55) → run the sweep at 0,50 to confirm.
  - **X20** (§7 Hidden roof; 2026-10-28, ours — to check on a close-up) The one-água **remate de topo** rises 0,10 up the
    parapet's roof-side face (`camadas.cobertura_platibanda`) while the parapet stands `platibanda.folga` 0,05 over the
    plane's top (`casa_planta`: `z_plat` = `z_topo_max` + 0,05) → at the highest wall it may stand ≈ 5 cm past the parapet
    top, through the chapéu. Fix: stop it under the chapéu's inner leg (the leg lapping over it), or raise the parapet on
    one-água roofs (≈ 0,15 upstand — general practice).
- [SB] from the engineer's drawings: `estrutura_dc.py` (beams 0 → D on the amarração, purlins ≤ 1,2 tilted, the eave one on
  the beams, prumos on every beam, empenas, verges 0,12) + `camadas.cobertura` (rectangle only: gutter flat, downpipes 0,30
  from the ends at the eave line ≈ 0,25 off the frame running to Z 0 — the "ligeiramente acima" and the swan-neck missing).
**Other assumptions** (see the lines above): wall position default "face_interior" (D2503: "face_exterior", set per
project); bandeiras; réguas one per perfil; perfis 47×17; prumos 110×75; contra-ripado 30×20 at 0,35 from the façade end;
ripado at 0,35 centres from the bottom; corner / jamb verticals in both batten layers; no gaps where battens meet; Tremolo
end joints in line; exterior gutter 125×90 and 80 mm downpipes (exposed roofs); Munditelha 40 mm (thickness, core, skin,
colour); the verge 0,12; purlins flat and tilted; no ridge beam; on 22×7,5 hidden roofs purlins flat at ≤ 1,2 and the v3
gutter box; on lameladas (only when cfg says so — no span rule) no board under the gutter lining, the lining dark grey, the
side outlet (a 0,08 × 0,06 hole flush with the gutter bottom — the holes the rule, the side type the default); the ridge
madres' 9 m trigger; downpipes 80 mm × the cavity, ≥ 0,10–0,15 clear of openings, 5 cm above the base, no recess, overflow
or inspection point (too small for TV's outlets, §13); parapet `folga` 0,05 when `platibanda.topo` is not set (D2503 ≈
0,07); one chapéu piece per wall top, no joint strip or membrane; the gutter end cap to the top over the open gutter; wool 80
mm in parapets; OSB 15 + Traspir under every façade finish on the parapets' roof side (TV's list); the hidden roof's
form (one água up to a 13,5 m panel, a rectangle's default gutter side south — the client may choose, two slopes mid main block ≥ 1 m otherwise, the remate de
topo 0,12 + 0,10); floor wool on the ceiling below; the 5 %
slope fallback; `cobertura_manter` "inclinacao"; the ground-floor XPS + betonilha default; all waste factors; Pladur board
size; vinyl 5 mm; XPS boards 1250×600 and render 6 mm; the caixilharia folga 0,025 in height too (none under doors — ours;
2,5 cm and a bottom profile under the janelas de correr — OPEN); the shutter box filling what is left above the frame (not
the maker's height; windows only), profiles 6 / 5 cm, glass 24 mm, box 0,10 deep at the frame's outer face; the garage door
in the opening (sectional doors usually hang behind it); door panels in "Portão seccionado RAL 7016".
