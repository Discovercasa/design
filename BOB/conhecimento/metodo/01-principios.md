# Método DiscoverCasa — princípios e documentos de produção (§0, §0a) (parte de conhecimento/metodo-construtivo.md, v8.3)

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
  **What [TV] is**: a house already built that DiscoverCasa gave us to learn from, and the case where our suggestions are
  evaluated — user 2026-10-30 (later still) "torres vedras foi um projeto usado para tu aprenderes sobre nós e nós irmos
  também avaliando as tuas sugestões" — confirmed (his words; the consequence — its as-built facts teach the method and
  test our proposals but are one house's, not the standard by themselves — is the Scope rule above, L40, L70).
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
