# DiscoverCasa — company context

- DiscoverCasa, Lda, Penafiel (Porto district), Portugal — discovercasa.pt. 15+ years building houses
  north to south of Portugal (including islands).
- Designs, licenses and builds single-family houses from scratch, delivered ready to live in ("chave na mão"). Main
  differentiator: **timber structure** on a **concrete foundation**, built with prefabricated modules (wall panels,
  floor and roof elements) assembled on site. Handles the architecture + engineering projects and the licensing.
- 10-year guarantee against construction / material defects; contractual deadlines with compensation.
- **Fully customisable houses — a company strength**: "Um dos nossos pontos positivos é sermos completamente
  personalizáveis" (2026-10-20).

## Standard system as marketed (discovercasa.pt model pages)
The build-up really used is in `sistema-construtivo.md`. Marketed: external walls of posts and beams in solid Nordic
pine and glulam; timber cladding, double-ventilated over a waterproof membrane (options thermo-treated cork, ETICS
"capoto", stone); plasterboard walls and ceilings, floating floor, ceramic tiles in kitchens / WCs (options OSB, Viroc,
cork, timber lining, solid wood floors); insulation in every cavity, energy certificates up to A++; aluminium windows
with thermal break and double glazing (PVC optional) — the current standard "para já": RAL 7016, automatic exterior
shutters, painel liso doors (`sistema-construtivo.md` §3b); certified installations (water, electricity, ITED).

## Product vision (user 2026-10-15)
Why Claude learns the method; "vamos passo a passo" — an overall idea, then an implementation plan per item.
1. **Builder** in "o nosso software": as soon as a client has a finished project, the house is ready in the builder
   (structure, layers, quantities). Pieces: `ferramentas/modelo/planta_arquitetura.py` (walls and openings from an
   architecture plan), `casa_planta.py`, the module divider `divisor_modulos.py`; first test `Construção Torres Vedras/`
   (2026-10-30, later still, on a note about the panel's coating for coastal air: "Sim já foi verificado e torres vedras
   foi um projeto usado para tu aprenderes sobre nós e nós irmos também avaliando as tuas sugestões" → TV is where
   Claude learns the company **and** where the company evaluates our suggestions — a suggestion is judged against what
   TV did and they say "já foi verificado" where they have already covered it).
   Settings panel wished ("Futuramente"): "um painel onde podemos definir este tipo de coisas, comprimentos dos módulos
   e a sua composição" — today in `sistema_construtivo.json` (`estrutura.divisor`) and each `config.json`.
   **Production documents for every new project** (2026-10-16 night): "quero que sejas capaz de desenvolver um
   documento igual ou do género desse dos módulos e da cobertura independemente do projeto … de forma a podermos modelar
   a casa sem erros e já como irá ficar no fim da construção"; with "um documento com a listagem de material"
   (2026-10-20) → `ferramentas/documentos/gerar.py` (Módulos, Cobertura, Listagem de material; `sistema-construtivo.md`
   §2c). The Módulos reviewed "está absolutamente correto"; the other two: his review pending.
2. **Budgeting from the materials**: "futuramente eu vou-te fornecer e terás acesso a uma lista de materiais e
   fornecedores onde vais conseguir ter o preço de cada material" (PENDING), showing how the sums are made. The price:
   "materiais, mão de obra, fundação, caixilharia, especialidades, instalações e pré-instalações, licenciamento e IVA"
   (especialidades = the specialty projects — ours; IVA rate not said); "Isso é um passo futuro podes anotar".
3. **Client platform instead of Enscape + Chaos Cloud**. Today SketchUp → Enscape (VR tours, AR on mobile, 360 renders)
   → Chaos Cloud Virtual Tours shared with clients. Goal: a client area on the website where each client sees their
   house or project whenever they want.
   **Named "Step Inside" (2026-11-05, our naming at the user's request: "more of a name you would give to a project
   that will be for commercial use, a service we will sell"; internal id stays `plataforma_cliente`; the user may still
   rename it; no alternatives chosen).** The user supplied a technical spec dated 2026-11-05
   (`Discovercasa_Especificacao_Tecnica_Claude_Code_v2.md` + `Discovercasa_Plano_Tecnico_Revisao_v2.pdf`, same content;
   kept locally, not in Git). Key points only: pipeline documents → Claude Code parsers → Blender → exports
   FBX/GLB/USDZ → Unreal build → Cloudflare R2 → Supabase + GPU runtime with Pixel Streaming → hub → client 3D/AR/VR;
   phases 0–9, starting with Phase 0 (audit). Rules: no paid cloud resources, GPUs, buckets, DNS or production changes
   without explicit human approval; never invent dimensions (mark NEEDS_HUMAN_REVIEW). Reference costs (to show per
   workflow component in the hub): RunPod RTX 4090 Secure 0.89 USD/h, Community 0.34 USD/h; R2 0.015 USD/GB-month, 10 GB
   free, no egress; 1 USD = 0.89131 EUR on 2026-11-05; 8–15 GB per house. VR risk: Lumen does not support VR, Pixel
   Streaming VR is experimental. Decisions for DiscoverCasa are listed in the spec's §16.1 (become "decisão" tasks in the hub).
4. **Configurator** like IKEA Builder / Kreativ — "DiscovercasaBuilder" (his name, 2026-10-21): the client picks the
   shape, then the m² and the pé direito, sees the base with its price, builds with 3 m walls ("Estilo como se construía
   no jogo SIMS"), never sees "módulo", the price live; prices predefined before any launch ("não temos qualquer tipo de
   problema de transparência"). Developed since 2026-10-20 in its own session (worktree `BOB Claude - configurador`,
   branch `configurador`; brief `sessao-implementacao.md`) — current state, requests and history:
   `configurador/docs/especificacao.md`. (The 2026-10-15 wording "neste caso módulo a módulo" and "the m² first" were
   superseded 2026-10-20.) 2026-10-29: after the openings a **step 7** — his "menu de Pérgolas e Garagens e Espaços
   exteriores que seja necessário construção por exemplo um anexo" (the screen's title "Pérgolas, garagens e anexos" is
   ours): (a pergola; a garage or an annex, attached under the house's roof or separate with its own) — `sistema-construtivo.md`
   §3d; the DISCOVERCASA brand returns to the shape (step 1) — spec §2. "Online builder" is his term for it too.
- **Validation**: model houses already built and compare with the materials really used ("se os valores de materiais
  gastos estão perto do que nós realmente usamos") — Torres Vedras; its company drawings D2503 (roof, modules) received
  2026-10-16; the real materials list: pending.
- Not defined (not asked): what "o nosso software" is; the website's platform. Items 3–4 mean publishing on the web —
  the repo is private (client data).

## Design hub and project organisation (user 2026-11-05)
- **Goal of the hub**: a way of working where someone who knows nothing about a project can open it and see what it
  is, its goals, phase, what was done and on which day (day only), future goals and steps, and how projects connect.
  "Início" = clean, precise, some detail, not cluttered. Every page opens with a detailed step-by-step workflow to the
  next checkpoint. Anyone can add checkpoints/small tasks (on the project page or on Início); new ones are flagged as
  "added" the first time they are seen (small pop-up). Navbar: Início + one page per project; profile menu (Área
  pessoal, Definições, Novidades, Sair); Sugestões icon (anyone suggests hub changes); notifications bell ("User x task
  x is concluded": assigned, concluded, state changed). Build Your House page: describe first, then a button to the app.
- **Decisions in tasks**: a task that needs a decision shows a "decisão" pop-up with all options, pros/cons and costs;
  every decision is recorded as "we chose X instead of Y" with the other options kept.
- **App independence rule**: the apps are connected but independent, usable without each other; they help each other
  only when it saves time and tokens, shown as "Sugerido: usar <app>" (also explained on Início). Builder and Build
  Your House follow the DiscoverCasa method for now; later they should also work for non-DiscoverCasa work ("for now
  keep it as it is but have that in mind").
- **Organisation (ours)**: each project has a code folder, a published folder and a branch prefix
  (build-your-house/, builder/, gerador/, orcamentacao/, step-inside/), documented in `PROJETOS.md` (repo root).
- **Status** (2026-11-05): LIVE on design.discovercasa.pt (`hub/inicio-projetos` merged into main); migrations
  0004/0005 applied to the Design Supabase after the user's "Sim, aplica"; Playwright 28/28 (simulated database). The user asked for design inspiration from
  GSAP skills, React Bits, taste-skill and impeccable, and a final Playwright check with feedback.
- **Pending with the user**: confirm the name Step Inside (migrations applied and hub published 2026-11-05).

## Social media (user 2026-11-06)
- Instagram/Facebook posts are planned in advance in a Google Sheets workbook ("DiscoverCasa Post Mensal - publicações"):
  one post per week, each month = 4 weeks (Semana 1-4); a post = title "<Obra> - <topic>" (e.g. "Boelhe - BF",
  "Matosinhos - Estrutura", "Ribamar - Mov Terras"), up to 5 photos (Foto 1-5) and the caption with emojis and hashtags.
  Caption and photos are approved before publishing (approval comments in the sheet).
- Obras followed for content: Matosinhos, Casa dos Cães, Boelhe, Ribamar, Gaia, Oliveira de Azeméis, Lagos (plus Sobral and
  Torres Vedras in posts). Content phases per obra: Projetos, Mov (movimento de terras), BF (base de fundação), Estrutura,
  Acabamentos; Gaia "Aumento" (extension of a house DiscoverCasa built), Oliveira de Azeméis "Garantia" (client testimonial).
  Matosinhos plan: 1 terras, 3 BF, 2 estrutura, 2+ acabamento posts. Older sheets (Maio 2025?... MarçoAbril, "Geral" with a
  daily plan) exist, not imported.
- Hub tab "Redes sociais" (#/social) built 2026-11-06 on branch hub/redes-sociais (not yet published or applied).
- Pending: confirm import assumptions (past weeks with caption = Publicado; Nov with caption+photos = Por aprovar; no caption = Ideia).

## Working with the user
**Language and words**
- Talk in **Portuguese (PT-PT)** since 2026-10-09 ("from now on lets try to talk always in portuguese"); docs stay in
  English with the Portuguese terms exactly as he writes them. A Brazilian-style "Atingi meu limite de uso … continue de
  onde parou" (2026-10-20) is the app's text — keep PT-PT. He sometimes mixes English ("dont worry", "keep going").
- He does not know English trade terms ("the terms sill and header i have no idea", 2026-10-09) → peitoril, padieira,
  verga, ombreira (glossary `construcao-madeira.md` §7) and plain words. He may not know a technical term ("explica-me o
  que é um ladrao mas penso que não", 2026-10-20) → say what the thing is and does; an answer given before the
  explanation is tentative.
- The company's own names win: "Os Rufos da platibanda na realidade nós chamamos de Chapéus" → **chapéu**; janela de
  correr (not "sliding door"); "roof" in his early English also meant the ceiling ("fake roof" = teto falso).
- "de encontro a" in his writing = "ao encontro de" (in line with): "os modulos vão de encontro ao tamanho da casa".
- "o builder" = the configurator ("O testo falso ainda não aparece no builder", 2026-10-28; "testo" = teto); "online
  builder" too (2026-10-29).
- **Client-facing names are chosen for a professional look**: "Oculta" instead of "escondida" on the screen ("sendo que
  ambas são a mesma coisa mas é para ficar mais profissional no online builder", 2026-10-29) — same thing, only the
  label changes; the engine keys stay. Ask him for the client-facing word when a screen label is new.
- **Client-facing screen text: short, and the first visit explained** (configurator, 2026-10-29): "Otimiza também as
  descrições da secção de interiores e pavimentos, estão demasiado extensas"; "Para ser mais user friendly no início de
  tudo adiciona um pop-up no meio de ecrã que explica como o cliente navega pela casa" (left button rotates, wheel zoom,
  pan …) → write every new screen text short; a first-time hint where a control is not obvious. The camera must stay
  where the client left it ("quero que continue na câmara que o cliente estava anteriormente"). Spec §11.
- "ele" / "o outro chat" = the other Claude session (2026-10-20) — say which session is meant in a log.

**What he wants from us**
- **Every detail matters** — logged verbatim in `registo-conversas.md` and filed (agent `guardiao-detalhes`): "what i
  want truly is for you to understand how we built and every detail we use or do" (2026-10-09). "Não te esqueças de ir
  aprendendo e evoluindo com cada chat que temos porque muitos insights que te vou dando devem ser relembrados"
  (2026-10-15).
- **Always say what looks off or could be improved** — the issue, why, the better option, even when he knows it
  (2026-09-24). He wants our opinion ("mas diz-me também a tua opinião", 2026-10-21) and our insights kept ("Obrigado
  pelo insight depois grava junto com uma lista de insights que tenhas por favor" → `insights.md`); note even what he
  does not worry about ("Isso é tranquilo, don´t worry mas anota na mesma").
- **The reason behind every detail**, not only the geometry: "analisa este documento ao detalhe guardando exatamente como
  é feito de forma a perceberes o porquê de cada pormenor !!" (2026-10-16). Explain "precisely what happens and why"
  (2026-10-09); visual explanations of hard choices ("Faz-me um esboço…", "volta-me a dar este problema que surgiu com
  uma demonstração visual"); "demonstra-me isso por favor" → a section drawing.
- **Always the DiscoverCasa method** — "o que o arquiteto muitas vezes escreve não significa que tenha de ser seguido
  restritamente, nós usamos o nosso método construtivo sempre portanto segue o nosso" (2026-10-15; Sobral 2026-10-09).
  Still say when it touches the licensed projects (Sobral `revisao-tecnica.md` #26, TV #1).
- Rules he gives hold for every house unless he says otherwise ("those are the rules", "always follow this logic unless
  told otherwise", 2026-10-09). His defaults come with conditions ("por defeito … desde que sejam duas janelas",
  "depende da situação") → record the condition; ask the case it leaves out when it comes.
- **Design choices left to us**: "dependendo da casa vê o que se enquadra melhor, nesta casa por exemplo terias desenhado
  os módulos de forma diferente ?" (2026-10-19); "Vai com a opção que achares melhor, força nisso confiança" (2026-10-20)
  → choose, and say what was chosen and why. He leaves the order of work to us ("Preferes fazer já as alterações …?").
  **No fixed pattern — the best solution per case**: "Não quero que assumas um padrão mas sim a solução mais eficaz e
  inteligente para cada caso" (2026-10-28, on roof shapes) → decide each house on its own geometry and say why.
- **No shortcuts**: "são bastantes tarefas não vás por shortcuts, capricha em cada uma delas" (2026-10-21).
- **Per-project questions**: "Para cada obra aquelas anotações que te fui dizendo que depende de obra para obra anota e
  faz-me essas perguntas" (2026-10-20) → `perguntas-por-obra.md`, asked at the start of each new project; unanswered →
  the default he gave. Add to it whenever he says "depende da obra", "neste caso", "nesta obra", "nem sempre", "para já".
- He asks our opinion on the company's own choices ("nós achamos que por dentro é mais correto e fica melhor, qual a tua
  opinião já agora?") → pros, cons, the conditions that make it work; "achamos" = a preference, kept as the method.
- He pushes back with evidence when our concern looks disproven ("não estou a perceber o teu ponto … está absolutamente
  correto", with the PDF) → state a concern with the concrete case where it fails, naming both documents and numbers.

**How to ask him**
- Grep the log and the docs before asking; quote his earlier words and ask only the new part — re-asking irritates him
  ("Sim como já te tinha explicado nos chats anteriores …", "lá está eu expliquei em cima", 2026-10-21); read the whole
  message before taking a numbered answer alone.
- Questions on our own terms get lost (2026-10-19: "não percebi a questão podes-me exemplificar o que queres dizer?",
  "Com entalhes queres dizer o que especificamente ?") → ask with the drawing image and its own label, his words, a plain
  description, one point per question; name the house and the sheet ("A quais lameladas te referes?", 2026-10-21 — the
  re-ask with D2503 sheet 1 was answered at once). Show a photo again when asking about it ("recorda-me da imagem outra
  vez por favor"); a module named only by its size is not enough ("não estou a ver qual é o módulo 2,21").
- He answers by number, attaches evidence (a print, a site photo, a photo marked in blue — "percebeste a lógica?") and
  expects the work to go on ("continua já te respondi as questões") — open points do not block it.
- **How sure he is**: "acho que", "diria que sim", "não sei ao certo", "não me relembro do nome" → tentative; confirm with
  a document before it becomes a rule. He may change his mind inside one message ("Mas pensando bem faz mais sentido …
  3 metros", then "pelo menos 2 metros" two paragraphs later, 2026-10-30) → record both figures, do not pick the later
  silently, ask. He defers whole questions ("esta pergunta depois eu respondo-te quando abordar as questões todas das
  coberturas", 2026-10-30) and promises material ("vou-te fornecer uma imagem") → pending items, nothing modelled before.
  A figure said from memory ("acredita que o máximo de comprimento seja 25 metros") can be corrected a message later
  ("afinal o máximo do painel é 15 metros", 2026-10-30 later) → log both, use the last, never the first; he hands over
  the data sheet itself (a PDF) and the detail drawing (an image) → save both in the repo (`conhecimento/fontes/`,
  `configurador/docs/revisao/`) the moment they arrive.
- **Promises and reminders**: "Posso te responder a isso depois", "isso depois eu digo", "lembra-me mais tarde para te
  confirmar o que leva" → a pending item (`sistema-construtivo.md` Pending, the project's `estado.md` ▶); raise it in the
  next message that fits; do not model the answer before he gives it.
- **"Faz todas as questões que precisares"** (2026-10-29 night, on the roofs: "pareces ter muitas dúvidas de momento faz
  todas as questões que precisares para começarmos a fazer as coberturas sem falhas algumas!!") → when he sees many
  doubts, he wants **every** question in one go, not drip by drip: one numbered questionnaire (codes A1…E8, each with
  its sketch and the current default), no re-asking of what he settled ("estribos.", 2026-10-28). Sent 2026-10-29 night,
  unanswered; he may answer by code. Spec §13 Roofs.

**How he reviews**
- **The screen must look like a real finished house**: "O teto falso dá para ver as linhas, numa obra real isso não se
  vê portanto faz com que seja liso também" (2026-10-30; also "não corresponde à realidade", 2026-10-22) → no
  construction lines, joints or profiles drawn where a real building shows none; he also tests behaviour by using it ("aconteceu-me
  adicionar uma garagem e as paredes interiores algumas desapareceram") → after each new element, check that what was
  already drawn is unchanged.
- **Visually**: Blender / configurator screenshots with the problem circled in red, hand sketches with named views,
  site photos of how it was built; he opens the `.blend` in his own Blender before answering ("dá-me o ficheiro e eu mal
  consiga abrir no meu blender eu respondo-te às questões") → send the file with a guide. He catches what a DiscoverCasa
  house never has (open corners where rain gets in, a bare frame, a gap, members through one another) and missing
  functional details ("nas caleiras nao existem os buracos par agua escoar para os tubos de queda") → check every face
  clad, every water path connected, before showing; each error becomes a lesson in `metodo-construtivo.md`. Repeated
  basic faults annoy him: "Estas a cometer erros que não fazem sentido" (2026-10-28 — roof gaps, downpipes not joined
  to the gutters, chapéus not round the whole roof, caps floating over the panels, a façade finish not on the whole
  house) → before showing a roof: every m² covered, every downpipe joined, every cap / flashing on the panels, one
  façade finish all round, and things he already said ("como eu já te havia dito") checked against the docs.
  Again 2026-10-29: the gutter's outlet holes (asked 2026-10-20, now "estão em falta os buracos para os tubos de queda"),
  the roof colour ("Mais uma vez quero a cor original … e não cinzenta"), "Revê isso mais uma vez", a chapéu not
  covering the whole parapet → before showing: grep his earlier words on the thing, and look at the model from above and
  from the side (a hole in a face seen edge-on is a hole nobody can see). Again 2026-10-29 night: "as caleiras na parte
  mais alta da cobertura oculta continuam lá" (the high-side fault of the same day, still seen — we had only recoloured
  the top flashing), flashings "que têm de ser da cor da cobertura", two roofs "desalinhados" → when he reports a fault,
  look at what he can see on the screen (a flicker between two faces, a shape that reads as a gutter), not only at the
  engine's parts; and after a fix, re-check the same screenshot's view.
- **Company drawings win over descriptions from memory**: "arranjei o documento exato … eu disse-te mal como seriam as
  aguas" (2026-10-16) → for a built house ask first for the company's production drawings.
- **Finished-house photos** win over construction-stage photos and the licensed plan, but a stage photo is not wrong —
  ask what was added later. "nós nesta obra fizemos de forma diferente mas a forma como modelaste … é a forma correta" →
  record both the method and what that house has. Site photos can show modules changed on site ("este módulo sofreu uma
  alteração em obra") → ask before turning a photo detail into a rule.
- He shares documents of other DiscoverCasa houses to teach the method (Casa CL modules 2026-09-30; "3_Vigamento"
  2026-10-15 — "este não é o mesmo projeto mas é para perceberes como operamos") → company standard
  (`sistema-construtivo.md`), files in `fontes/`.
- He audits the knowledge agents ("diz-me se o nosso agente de detalhes … anotou tudo o que era importante e percebeu a
  lógica") → answer with a comparison of what was filed against the source. 2026-10-29, on token cost: "perguntar sobre
  otimização dos nossos tokens, se o guardião,mestre estão a anotar toda a informação ou a filtrar aquilo que apontam"
  → asked in the reply; **his decision on any change: pending**. How they work (the keeper's own account): the log
  keeps his words verbatim, in full; the topic docs get each fact in short form; the keeper sees only what the caller
  passes, so a summarised message reaches it already filtered; the rulebook keeps the current rule + source, not the
  history. Where tokens went: reading `metodo-construtivo.md` (≈ 1 800 lines) and the 700-line log on every run.
  **Decided 2026-10-29** ("Sim, divide o livro do método por temas"): the rulebook is an index + topic files in
  `conhecimento/metodo/` — each run reads the index and only the topic it needs.

**Keepers of the knowledge** (2026-10-15: "Quero que cries um agente que a função dele é guardar pontos chave e toda a
informação de como construir uma casa como nós"): `guardiao-detalhes` logs his words and files each fact in the topic
docs; then `mestre-construtor` folds the method facts into `metodo-construtivo.md` and checks models against it.
**Clean-ups allowed** (2026-10-28): "Se estiveres com informação a mais e começas a confundir informações realiza uma
limpeza aos nossos ficheiros sintetizando tudo e resumindo aquilo que conseguires resumir, para além disto qualquer tipo
de conversa ou informação que consideres inútil podes remover" → condense the docs when they grow confusing (done
2026-10-28: the knowledge base condensed, the log in one file, the rulebook v8.0); his words verbatim and the
decisions stay (the history is in git).

**Practical**
- He works from more than one PC (2026-10-21, a PC whose user folder is "PC"; this one "DiscoverCasa1") → run
  instructions say how to get the code there (a clone of the branch), the folder to run from, and that `localhost` is
  only the PC where the server runs; push first.
- 2026-10-30: "antes de mais fornece-me acesso ao local host e os comandos necessários para dar git pull se necessário" →
  start the reply with the exact commands for his PC (`git pull origin configurador`, `npm install --prefix
  configurador/web`, `npm run dev --prefix configurador/web`, open http://localhost:5173; spec §9) and say that
  `localhost` is only the PC where the server runs — a cloud session cannot expose it to him; push first.
- 2026-10-30 (later still): `npm run dev` failed with "Port 5173 is already in use" (screenshot; he wrote "está-me a
  dar erro e aproveito e já te respondo a isso") — a dev server was already running on his PC (another window or an
  earlier start); `package.json` starts vite with `--strictPort` on purpose, so it never moves to another port. He may
  run it from more than one window → the run instructions say: close the old window (Ctrl+C) or end its node process,
  then start again (spec §9). He answered our numbered points in the same message as the error report.
- Tokens: the 2026-10-09 "stop with enough tokens … to push" was that moment's wish, "not a rule"; leave a restart point
  ("▶ Where we stopped" in the project's `estado.md`).
- 2026-10-29: "A outra sessão estava pesado, vamos recomeçar aqui já que na outra sessão disse que guardou os
  screenshots enviados" → a heavy session is restarted from the repo, and he expects the screenshots he sent to be saved;
  `_trabalho/` is git-ignored, so a new session (another device, the cloud) never sees them — they were lost this time.
  Save review screenshots in the repo (configurator: `configurador/docs/revisao/`, generic designs, no client data; TV:
  `revisao-modelo/` does it already) and say in the log where (our suggestion, 2026-10-29 — to put to him; no reply yet).
- 2026-10-29: the agents `guardiao-detalhes` and `mestre-construtor` run on the Sonnet model (`model: sonnet` in
  `.claude/agents/`, was `inherit`) to spend fewer tokens — "Sim passa" to our "Passo o guardião e o mestre para o
  modelo Sonnet, que gasta muito menos?".
- 2026-10-13: moving to an enterprise Claude account — everything to continue is in the repo (`migracao/LEIA-ME.md`).
- GitHub: `VascoCoelho/DiscoverCasa-Claude-BOB` (private; moved from `VascoDiscovercasa` 2026-09-26, which keeps write
  access). "you can push to VascoCoelho i prefer there since i use more that github account than the other"
  (2026-09-30); this PC's `origin` points there but commits / pushes as `VascoDiscovercasa` (switching not decided).
  Tools run locally (Python + Blender); no cloud services needed. (Partly superseded 2026-10-30, see below and registo.)
- 2026-10-30 — new GitHub + Supabase: "pretendo colocar o BOB(e os pushes todos deste PC) lá dentro". GitHub account
  `DinisDiscover` (logged into `gh` on this PC, now gh's active account). Repo `Discovercasa/design` — **PUBLIC**, org
  `Discovercasa`; DinisDiscover has push, not admin/maintain (outside collaborator, not an org member; cannot see the private BOB repo; checked 2026-11-05). BOB lives in its folder `BOB/`, published with a fresh history
  WITHOUT `*.dwfx` / `*.pdf` (client drawings stay on this PC only); the old history stays private at
  `VascoCoelho/DiscoverCasa-Claude-BOB` (still the git `origin`; consider archiving). Site `design.discovercasa.pt` =
  Cloudflare Pages publishing only `public/` on push to `main`, behind the Hub login; the Design repo has its own
  `CLAUDE.md` rules (Supabase publishable key only, RLS, do not touch the Hub login). Only visible part: the configurator
  build at `public/configurador/` → https://design.discovercasa.pt/configurador/ (verified live 2026-10-30; behind the Design/Hub login since 2026-10-30, "Para já atrás do login" — gate public/js/porta.js; configurator shown as "Build Your House" at /build-your-house/ (2026-10-30); home page = panel of 5 tool cards + Sugestões (table sugestoes) with status (2026-10-30); Sugestões: delete, comments, Checklist coloured by status (2026-11-03; migration 0003 applied; page pushed 2026-11-05 (053ebe0), live); document generator at /gerador/ (drop a DWFx or vector PDF → documents, in the browser; ferramentas/documentos/de_desenhos.py + dwfx/leitor_pdf.py; checks (modelo/verificar.py) + 3D view of the timber; DWG not yet); worker
  paths follow Vite `BASE_URL`). ~~Publish with `python ferramentas/publicar_design.py` (clone in `_trabalho/design`;
  `--sem-push` = dry run), run from branch `configurador`~~ (superseded 2026-11-05, see registo: the script was removed
  from Design; new flow: work in Design and run `python BOB/ferramentas/construir_site.py [--so configurador|gerador]`,
  then commit and push; see the 2026-11-05 "Sim, prepara" note below). (A/B below superseded 2026-11-05, see the DECISION after them
  and registo.) 2026-11-05 — pending the user's choice, how cloud sessions
  (claude.ai/code, phone) can push to `Discovercasa/design`: a cloud session uses ONE GitHub connection per claude.ai
  account; `/web-setup` (in a `claude` terminal) sends the local gh token and replaces the browser connection.
  (A) VascoCoelho invites DinisDiscover on the private BOB repo, then `/login` + `/web-setup` on this PC; sessions with
  both repos attached push to both. (B) a Discovercasa org owner gives the GitHub account connected to Claude write
  access on `Discovercasa/design` (maybe approve the Claude GitHub App on the org). On this PC pushing already works
  (gh as DinisDiscover). Supabase: connector (MCP) connected to project "Design", ref
  `uuofvywhouhffmfqojoc`, eu-west-1, Postgres 17.
- 2026-11-05 — **DECISION (user): `Discovercasa/design` is now the repo where changes to ALL applications in development
  are made** (configurator / Build Your House, document generator, budgeting, client platform, builder); the private BOB
  (`VascoCoelho/DiscoverCasa-Claude-BOB`) is no longer their working repo. Goal: cloud sessions (claude.ai/code) on the
  user's Claude account can push to Design. Route (supersedes A/B above): in a `claude` terminal on this PC (gh active =
  DinisDiscover) `/login` if asked, then `/web-setup` (replaces the GitHub connection; any repo the gh token reaches; no
  Claude GitHub App needed), then start cloud sessions on `Discovercasa/design`. If `/web-setup` is missing
  (Team/Enterprise) an Owner enables "Quick setup" (Organization settings > Claude Code). Alternative: reconnect in the
  browser as DinisDiscover (likely needs the Claude GitHub App approved on the org). Cloud sessions can no longer open
  the private BOB repo (accepted). **Pending: user runs `/web-setup`** (not confirmed) — **RESOLVED 2026-11-05, see registo: `/web-setup` and Quick setup are NOT needed.** The cloud push to `Discovercasa/design` worked with the GitHub connection the Claude account already has (test: branch `teste-push` exists on Design, pushed from a cloud session, environment "Discovercasa Nest"). The plan is Claude Team with Quick setup off (`/web-setup` = "Unknown command"); what decides the push is the GitHub account connected to the Claude account, not the Claude login. Next time: in claude.ai/code pick the repo with the "Repositório" button → `Discovercasa/design`. Pending: delete test branch `teste-push`. Open points flagged 2026-11-05 (status after the user's go-ahead "Sim, prepara", same day):
  (1) `ferramentas/publicar_design.py` would erase work done in Design: DONE, removed from Design (blocked in the private BOB);
  (2) client drawings (`*.dwfx` / `*.pdf`) never go to Design (public): DONE via `.gitignore` (`BOB/.gitignore` ignores
  `*.dwfx`, `*.pdf`; root ignores `_trabalho/`, `*.dwfx`, `.claude/settings.local.json`); work needing drawings stays on
  this PC; (3) build step inside Design: DONE, `BOB/ferramentas/construir_site.py` (see below); (4) skills and agents in
  `BOB/.claude/`: skills OK (found as directory-scoped skills under `BOB/`), agents NOT VERIFIED from Design's root
  (fallback written in root `CLAUDE.md`); (5) reconcile `BOB/CLAUDE.md` with Design's `CLAUDE.md`: DONE (root section
  "Aplicações e BOB"; BOB/CLAUDE.md, `sessao-implementacao.md` §1/§5/git line and `configurador/CLAUDE.md` updated);
  (6) this PC works in a Design clone: PENDING (being done 2026-11-05).
- 2026-11-05 — user "Sim, prepara" (to "Preparo o Design para ser o repositório de trabalho?"). Done: final sync of the
  private BOB (a095e7b) into Design with the old script (Design commit "BOB: sync from a095e7b"; it also dropped the stale
  debug pages `public/build-your-house/motor/_cobertura.html` and `_telhados.html`). New `BOB/ferramentas/construir_site.py`
  builds in place `public/build-your-house/` (Vite build of `BOB/configurador/web` + Design login gate) and
  `public/gerador/` (page, engine files, three.js): `python BOB/ferramentas/construir_site.py [--so configurador|gerador]`,
  then commit and push (tested: same output as the old script apart from line endings). Root `.claude/launch.json` added
  (`npm run dev --prefix BOB/configurador/web`, port 5173). The old private BOB is kept as history only. Still pending:
  user runs `/web-setup` (cloud sessions push as DinisDiscover); this PC moves to a Design clone. (`/web-setup` item
  RESOLVED 2026-11-05: not needed, see the note above and registo.)
- 2026-11-05 — how pushes work now (answer to the user): local sessions opened in the folder "Discovercasa Design" push
  as DinisDiscover (git configured so); cloud sessions started on `Discovercasa/design` push too. Pushing to `main`
  publishes the site at once (Cloudflare Pages): use a branch for work in progress, `main` when the user wants it live.
  After app changes run `BOB/ferramentas/construir_site.py`; not yet verified that the cloud environment has Node/npm for
  it. The old "BOB Claude" folder still pushes to the private BOB (history only).
- 2026-10-30 — **the repo is public: never write NIF, addresses, phones, engineer IDs or personal names in it.** Personal
  data were removed from the records that day (company NIF, engineer OET ID, site addresses, licensing process number,
  architects' / client's names, a personal email) — "Tudo o que seja esse tipo de informações podes eliminar dos nossos
  registos visto que são fúteis para nós".
