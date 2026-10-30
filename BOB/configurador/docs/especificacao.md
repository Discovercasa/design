# DiscoverCasa configurator — specification (current state 2026-10-30)

The client builds a DiscoverCasa house in the browser, "like IKEA Kreativ", and sees the price change with every
element. Product vision item 4 (`conhecimento/discovercasa.md`); brief `conhecimento/sessao-implementacao.md`; how
Kreativ works: `ikea-kreativ.md`; the method facts: `conhecimento/sistema-construtivo.md` (rules:
`conhecimento/metodo-construtivo.md`); the user's words verbatim: `conhecimento/registo-conversas.md`.
Status: **confirmed** (the user said it) · **ours** (our reading / choice) · **OPEN**. Condensed 2026-10-28: the
per-review history is in §12 (changelog) and the git history.

## 1. What it is
- **For the client, on the website**: "Isto é suposto ser o cliente a usar, o cliente chega por exemplo ao nosso website
  e pode instantaneamente montar a sua casa como desejar." — confirmed.
- **Browser first, then the website**: "objetivo final é ser implementado no browser e depois no nosso site" —
  confirmed. The website is another project (`C:\Users\DiscoverCasa1\Desktop\DiscoverCasa site`): ask before touching
  or linking it.
- **3D that turns, like IKEA's**: "3D a rodar como o do IKEA" — confirmed. "mais tarde vamos tornar ultra-realista o
  aspeto da casa" (2026-10-21).
- **Everything can be changed**: "Tudo o que mencionaste quero que o cliente possa mudar. Um dos nossos pontos positivos
  é sermos completamente personalizáveis." — confirmed. Except the roof **covering**: sandwich panel only for now — "para
  já vamos deixar no DiscovercasaBuilder apenas o painel sandwich como opção" (2026-10-21).
- **Name**: "DiscovercasaBuilder" (2026-10-21) — read as this configurator; whether it names the whole software
  (Product vision 1, the "Builder"): not said.
- **The client never sees "módulo"**: "O cliente nunca deve ver a palavra módulo sequer a aparecer no seu ecrã" — the
  client builds wall by wall, "Estilo como se construía no jogo SIMS"; the modules adjust behind — confirmed.
- **Single storey first**: "começamos com térreas e depois avançamos para dois pisos" — confirmed; for two storeys
  "emtermos de paredes nada muda" (`sistema-construtivo.md` §5).
- **Order of work**: "vamos primeiro focar em ter o builder a funcionar direito e depois nos pormenores"; the foundation
  as an indicative slab until he teaches it ("uma laje representativa para já não tem mal") — confirmed. "não vás por
  shortcuts, capricha em cada uma delas" (2026-10-21).

## 2. The client's steps (current order, confirmed 2026-10-21)
"Quero que o menu de paredes interiores seja o step 4", "Passo 5 deverá ser o revestimento exterior … No passo 5 inclui
também os tipos de cobertura", "Passo 6 entra o menu da caixilharia":

| Step | What the client does | Source / status |
|---|---|---|
| 1 Forma | Picks the shape: Retangular, L, T, U | "escolher o shape podemos dar várias opções" — confirmed; the four shapes and right angles only — ours |
| 2 Tamanho | Total area; the **base appears with its price**; every side editable (typed or dragged); **the pé direito** | "aparece X valor total isto apenas da base"; "quero que o cliente consiga mexer na dimensão de cada aresta e que consiga introduzir manualmente o valor que quer em cada aresta … apenas deixas a área total no menu do lado esquerdo"; "quando o cliente escolhe a área total da casa deve também escolher o pé direito que deseja e assim já ajustamos a estrutura para isso"; "O cliente pode escolher qualquer valor mas podemos deixar sugestões … essas 3 sugestões … por norma são o habitual" (2,40 / 2,50 / 2,60) — confirmed. m² = the base = the modules' outer faces (ours); show the useful area too (suggestion) |
| 3 Paredes exteriores | Walls of **3,00 m** along the base edge, the last of a side the rest, **never past the base** | "cada parede que o cliente escolha seja de 3 em 3 metros … a ultima parede … irá ter que ter obrigatoriamente 2 metros, a parede não fica para além da base de fundação" — confirmed |
| 4 Paredes interiores e pavimento | Interior walls drawn freely; each face's material (HUD, palette with name + image); rooms with their m², **the floor per room**; the inner face of the exterior walls too; "hide the roof" from here on | confirmed 2026-10-21 / 2026-10-22: "Tem de haver uma opção de esconder a cobertura … deste passo em frente essa opção deve estar sempre presente"; "a pessoa pode aplicar pavimento que desejar na divisão que desejar"; inner faces of exterior walls: "o nosso acabamento padrão nessas faces interiores é gesso cartonado mas também inclui opções de madeira, cerâmica etc." |
| 5 Exterior e cobertura | Cladding A Madeira / B ETICS / C Cortiça (image or 3D preview); the roof type, slope, beirado | "pode escolher uma das opções … imagem ilustrativa … podes usar um 3d preview do material"; "a pessoa pode escolher qual tipo quer escondida ou sem ser escondida" — confirmed; options §11 |
| 6 Portas e janelas | Doors and windows on the walls, with an image per type | "quero que tenha imagens representativas de cada opção" — confirmed; catalogue = the company caixilharia "para já" (`sistema-construtivo.md` §3b) |
| 7 Pérgolas, garagens e anexos | A **pergola** against a facade (width, place snapped to the cladding, projection, height up to a maximum); a **garage** or an **annex**: m², **junto à casa** (part of the house — our structure grows by it, the house's roof, a door into the house) or **separado** (its own roof, the client's choice) | "Acrescentar depois do menu de portas e janelas um menu de Pérgolas e Garagens e Espaços exteriores que seja necessário construção por exemplo um anexo. Pérgolas o cliente deve poder escolher a largura e onde quer colocar a pérgola dando snap para o sítio no forro exterior, a altura tem de ter um máximo como sabes. Garagens deve indicar os metros quadrados, cobertura, se quer junto à casa ou separado, se for junto neste caso com ligação para a casa deves juntar a nossa estrutura o espaço a mais e a cobertura tem de ser a mesma que escolheu para a casa, se for separado pode escolher a cobertura que quiser. Mesma lógica das garagens para anexos." (2026-10-29) — confirmed; how (§11 step 7) ours |

Always on screen (Kreativ): the 3D view, Vista de cima and side views, Desfazer / Refazer, **the total price**, a
**Lista** with every element's price; the **DISCOVERCASA** brand goes back to step 1 ("Botão da discovercasa deve levar
para o menu inicial dos de escolher a forma da base de fundação", 2026-10-29 — the design stays until a shape is picked). Saving / sharing a design online and "pedir orçamento": later (a server and a
privacy notice).

## 3. Behind the screen: the walls become DiscoverCasa modules
- The 3,00 m walls are the client's blocks, **not** modules: "nós vamos ajustando e os módulos também vão ajustando
  consoante os vãos"; "consigas dividir a casa nesse diferentes módulos … dependendo dos vãos que o cliente escolher e
  paredes interiores" — confirmed.
- **The module divider** `ferramentas/modelo/divisor_modulos.py` (phase 1, 2026-10-20; sizes and costs in
  `sistema_construtivo.json` `estrutura.divisor`; used by `casa_planta.py` for every house without the company's module
  drawing) follows `sistema-construtivo.md` §2 / §2b:
  1. stud grid 40 cm clear = 0,435 centres; plain modules = whole bays (exterior 5 = 2,21; interior 4 / 6 = 1,78 / 2,65);
  2. factory modules ≤ 3,0 — "os módulos exteriores podem ir até 3 m" (a maximum); longer only round an opening, built
     on site ("* Painel a executar em obra"), as short as the opening needs ("depende da situação mas neste caso sim usa
     o tamanho que o vão precisa");
  3. every opening inside one module; two openings closer than a 0,32 pier moved apart, half each, **when both are
     windows** ("desde que sejam duas janelas"); with a door: kept in one module, "a confirmar" (OPEN);
  4. corners: one wall through, one abutting — which one ours; escadas where another wall meets; no joint at a junction;
  5. where a wall's remainder goes: the cheapest split by the costs — "Vai com a opção que achares melhor, força nisso
     confiança" (ours);
  6. verga 22×7,5 over wide openings; ceiling beams 22×7,5 up to 8 m, glulam beyond; hidden roof: exterior modules in one
     piece to the parapet top with the amarração ring inside ("sim exatamente os módulos vao inteiros ate ao topo da
     platibanda"); interior modules made to the amarração; **the ceiling beams never cross the exterior modules** — they
     end inside against the modules' inner face, at most the beam notched ("essas vigas ficam por dentro e encostadas as
     da estrutura não atravessam").
- Checked on Torres Vedras vs D2503: the rules hold; 19 of 50 modules identical, every difference = where a remainder goes
  (`Construção Torres Vedras/docs/modulos-D2503.md`, `divisor-vs-D2503.svg`); < 1 s per house. ⚠ (keeper) With preferred
  = max = 3,0 the divider favours fewer, longer exterior modules (TV P12 2,69 2,65 2,95v, no 2,21; 25 exterior from the
  architecture vs D2503's 27) — D2503's plain exterior module is 5 bays; our choice to review.
- For the screen (ours): the frame stops at the base edge but the cladding stands ≈ 9 cm past it; the interior walls
  carry the ceiling beams, so placing or removing one can change spans and price; an opening the divider moves comes
  back to the screen at its new place with a note ("dois vãos muito juntos foram afastados … para caber o pilar").

## 4. The price
- **Always visible, live**: "à medida que a pessoa vai colocando elementos o preço deve ir variando e estar sempre
  presente … já começa com a base de fundação … depois adiciona uma parede aparece mais x … remove uma parede menos x" —
  confirmed.
- **What it includes**: "materiais, mão de obra, fundação, caixilharia, especialidades, instalações e pré-instalações,
  licenciamento e IVA" — confirmed. The price list: "Isso é um passo futuro" (Product vision 2, pending).
- Design (ours): unit prices × the engine's quantities + per-house items + IVA (rate OPEN); transport / site assembly
  per house (`sistema-construtivo.md` §2, ours). Until the list exists: **placeholder prices**, marked "Preços de exemplo
  do protótipo — não são preços DiscoverCasa" (§11). Suggestion: a standing note like Kreativ's "O preço final pode ser
  diferente".

## 5. How it is built (our recommendation; "Ok logo veremos a melhor opção")
- A **static web app** (no server yet), tested locally: Vite + plain JavaScript + three.js 0.186.1 (React when the
  interface grows); Kreativ uses three.js r160 on WebGL2.
- **One source of the rules**: the engine is the repo's Python (`ferramentas/modelo`, standard library only) run in the
  browser through **Pyodide 314.0.7** in a worker (`src/motor.worker.js`: `para_construtor.converter` +
  `casa_planta.construir`, `telhado_casa`, `cobertura_casa`) — never a JavaScript copy of the rules. Shapes drawn in
  JavaScript (`src/formas.js` = `formas.py`) so the first steps need no engine.
- The 3D is drawn from the engine's geometry and layers; colours / materials from `sistema_construtivo.json`.
- **Privacy**: the app carries only the engine, the standard JSON and the price table — never a project folder or client
  data; nothing online without the user's OK; Torres Vedras never shown ("Não vamos mostrar Torres Vedras").
- A configured house is saved as the builder's inputs, so it goes through the same chain: model, Módulos, Cobertura,
  Listagem de material (§8).

## 6. Plan
| Phase | What | State |
|---|---|---|
| 0 | This spec + the Kreativ study | done 2026-10-20 |
| 1 | The module divider ("Avança com a fase 1: o divisor de módulos, testado contra o D2503 de Torres Vedras.") | done 2026-10-20 |
| 2 | The configured-house format → builder inputs | done 2026-10-20 (§8) |
| 3 | Browser prototype ("Avança para a fase 3: o protótipo no browser.") | built 2026-10-20; runs on his other PC ("sim consigo", 2026-10-21) |
| 4 | Doors / windows, interior walls, roof, finishes ("avança com a fase 4") | built 2026-10-21; reviewed and rebuilt 2026-10-21 / 22 / 27 / 28 (§12) |
| 5 | Real prices (Product vision 2), the website, two storeys | — |

## 7. Questions (numbers kept; answered ones closed in one line)
1. A side whose remainder is tiny (12,20 = 4 × 3,00 + 0,20): a 0,20 wall, or the last two shared? — OPEN.
2. Does the client place each wall or fill a side at once? Where does the first wall start? — OPEN.
3. Interior walls: answered 2026-10-21 / 22 — drawn freely by clicks (§11).
4. Door / window sizes: free within limits, the catalogue's defaults — ours, to confirm.
5. The IVA rate; an "estimativa" note (his "Não" to our point 9 — whether it also rejects a note: unclear) — OPEN.
6. Openings placed on the side, independent of the 3 m walls — built (ours).
7. Per-house price items (especialidades, licensing): shown from the start or at the end? — OPEN.
8. Exterior factory limit: answered — up to 3 m (§3; keeper note there).
9. Two close openings when one is a door — OPEN (the divider keeps them in one module).
10. When the ridge madres become 22×7,5 — promised: "Posso te responder a isso depois" (`sistema-construtivo.md`
    promise (7)); our > 9 m trigger stays, flagged as ours.
11. The form of the "entalhe nas vigas" — OPEN, low priority (a notch on the underside at the support weakens shear).
12. The pé direito: any value, suggestions 2,40 / 2,50 / 2,60 (answered 2026-10-21). ⚠ The screen still offers 2,40–3,00
    in 0,05 steps → accept a typed value to the cm with the three as quick picks; keep 2,40 (RGEU) as the floor; past
    ≈ 3,0 a warning (studs, the 4,0 m Tremolo, the cércea) rather than a block — ours, to build. Transport is not a
    limit.
13. The exposed roof: answered — sandwich panel always (Munditelha), minimum 15 %, rectangle 2 águas with empenas,
    beirado 0,20–0,50 default 0,25 (max 0,50 since 2026-10-28, lower per house if a model needs it), hangers on the
    header, taller modules for a high head, misto kept, estribos at purlin ends. Still OPEN: §13.

## 8. The configured house (phase 2)
- **Format** `discovercasa-configurador/1` — what the client chose, nothing about modules: the base outline (right
  angles, counter-clockwise; side i = point i → i + 1), the client's 3 m walls per side, the openings (side, centre, type
  janela / janela_correr / basculante / fixo / porta / portao, frame L × A, sill, estore, room), the interior walls
  (centre lines, doors only, `faces` finishes), the roof (`tipo`, `inclinacao_pct`, beirado; a hidden roof's gutter side
  `cobertura: {tipo: "escondida", lado_caleira: "norte" | "sul" | "nascente" | "poente"}` — the configurator's compass,
  +y north; added 2026-10-29), the finishes, the pé direito; step 7 (2026-10-29): `exteriores: {pergolas: [{lado, s0,
  s1, projecao, altura (null = the highest)}], separados: [{tipo garagem | anexo, x, y, rot, largura, profundidade,
  cobertura}]}` — an attached garage / annex is already part of `base.contorno` (the screen keeps its block to edit or
  remove it), a separate one is a configured house of its own (`configurador/web/src/exteriores.js` `casaSeparada`).
  Shapes from the m²: `ferramentas/configurador/formas.py`. Full description: `ferramentas/configurador/para_construtor.py`
  docstring. Example (generic, no client): `configurador/exemplos/casa_exemplo_L.json`.
- **Conversion** `python ferramentas/configurador/para_construtor.py <house>.json --saida <folder> [--construir]
  [--documentos]` → `planta_paredes.json` + `config.json` → divider, layers, quantities, Módulos / Cobertura / Listagem
  de material, the Blender model (`construir_casa.py`).
- What the converter decides (ours unless said): the modules' outer face on the base edge; rough opening = frame + 2,5 cm
  a side and in height (+ the estore box over windows only — doors take no estore, "Prtas não tem estore apenas as
  janelas"; an estore on a door is ignored with a note "as portas não levam estore — ignorado"); interior doors 0,87 ×
  2,03; the house turned 90° when that gives the ceiling beams the shorter span (not for exposed roofs); 22×7,5 beams up
  to 8 m free span, glulam beyond; hidden roof: one água where the panels fit (≤ JSON `painel_oculto.comprimento_max`
  13,5 — ours) and a side is straight, else one ridge mid main block — chosen per house (2026-10-28, §11 step 5); the
  gutter side: where both straight sides across the ceiling beams qualify (a rectangle) the client's `lado_caleira`
  ("Podes deixar o cliente escolher", 2026-10-29), default south (poente on a turned house), an impossible choice falls
  back to the default with a note; L / T / U (one straight side) and two-água houses: no choice; the config's cobertura
  carries `lado_caleira` and `lados_caleira`; gutters
  inside the parapets, slope 6 % (TV),
  full-height exterior modules with the inner ring, the ceiling hung 0,1185 below the beams (confirmed "Sim");
  `pe_direito` default 2,50 (TV as built — ours); ground floor vinyl on the base; ceiling wool.
- Example check (2026-10-20): the L of 97 m² → 19 exterior + 7 interior modules, 4 rooms, the three documents; Blender
  validation 0 issues.

## 9. Running the prototype
- On this PC: `npm install --prefix configurador/web` once, `npm run dev --prefix configurador/web`, open
  `http://localhost:5173` (`?interno=1` adds the company's details: modules counted, the engine's notes and time). Node
  ≥ 22. After changing the engine's Python: `npm run motor --prefix configurador/web` (copies `ferramentas/…` into
  `public/motor`, git-ignored) and reload.
- **On another PC**: `localhost` is always the PC you are on — clone the branch into its own folder (`git clone -b
  configurador https://github.com/VascoCoelho/DiscoverCasa-Claude-BOB.git "<folder>"`), then **from that folder** `npm
  install --prefix configurador/web` and `npm run dev --prefix configurador/web`. That PC only gets what is committed and
  pushed.
- "Port 5173 is already in use" (2026-10-30): a dev server is already running on that PC (another window or an earlier
  start; `npm run dev` uses `--strictPort`, so it does not take another port) → close the old window (Ctrl+C) or end its
  node process, then run it again.
- Measured (2026-10-20): the engine ready ≈ 4,5 s after the page opens; a house computed in 0,4–1,1 s (with the
  structure shown, every change rebuilds it in the background, ≈ 0,4–4 s).

## 10. Tools — REA (reverse-engineer-anything)
- Requested 2026-10-20: "Instal and setup this repo without missing a thing" (github.com/morluto/rea) "… i want you to
  reverse engineer the IKEA KREATIV but for Discovercasa". Package `rea-agents` 6.7.0 (npm, MIT).
- Not finished from the session (its setup writes Claude Code's configuration — refused by the permission system; a
  global install from the desktop app lands in its private MSIX storage) → **the user runs** `npx -y rea-agents@6.7.0
  setup --client claude_code`, approves, restarts Claude Code; check with `npx -y rea-agents@6.7.0 doctor --client
  claude_code --json` (pending). Optional engines (Ghidra, IDA, JADX…) are for native programs — not needed here. The
  Kreativ study used the public site passively (`ikea-kreativ.md`).

## 11. The screen as it is now (2026-10-28)
- **Step 2**: total area only in the side panel; an editable dimension on every side in 3D (typed or dragged, the
  neighbours following; sides ≥ 1,00, the outline never crossing itself); pé direito 2,40–3,00 in 0,05 steps, default
  2,50 (to change, §7 q.12). A changed pé direito lowers any opening that no longer fits, with a note.
- **Step 3**: "+ Parede" / "− Parede" / "Fechar a casa"; the walls drawn as one finished wall per side, closed at the
  corners (no gap, no notch — "as paredes devem estar unidas"). "Seguinte" past step 3 only once the house is closed;
  "Ver como a construímos" shows the engine's structure.
- **Step 4** (`src/paredesint.js`): the "Parede interior" tool — a click near a wall (or a free end) starts a wall, the
  next ends it, it goes on until a wall meets another (a room closed), Esc stops; snapping 5 cm, the lines and ends of
  the other walls and the corners within 0,2; corners at 90° (the X wall through, the Y against it); **rooms** with
  their **m² on the floor**, a click on a room → its floor (Vinílico / Cerâmico) in the HUD; a click on an outside wall →
  its inner face's finish; the HUD beside what it is about, never over the wall or its handle; the finish palette
  (Pintado / Madeira / Cerâmico — sphere previews) as a brush that applies once; interior door 0,80 × 2,00 (rough 0,87 ×
  2,03); the "Cobertura" button (hide / show the roof) from step 4 on. Phase-4 limits (ours): a wall ≥ 0,80 from a
  parallel outside wall, ≥ 0,70 from a parallel interior wall, its end never on an opening; a door ≥ 0,30 (0,46 at an
  outside wall) from the wall's end. In the layers: wood = contra-ripado + ripado + boards ("slatted against slatted"),
  ceramic = tiles 30×60 on Pladur H1, ceramic floor 60×60 (products and spacings assumed).
  Fixed / added 2026-10-28 (his list "Coisas a mudar/acrescentar"): a closed room's corner face now takes the finish
  (was white — "quando se aplica a testura a parede nao fica com a textura, fica branco"); a click on an interior wall's
  corner / T starts the next room ("não me deixa dar snap num dos cantos que fica na área interior … Aparece o símbolo de
  proibido"); a wall starting on an exterior wall shows live its distance to both corners of that wall ("deve dizer a
  distância de cada canto … a 4 metros desse canto"), and a selected wall takes typed distances — measured from the base
  corner to the new wall's centre line (ours, to confirm: a tape inside measures from the finished corner to the wall's
  face, ≈ 0,2 m less); "ambas" in the materials HUD paints both faces and stays ticked ("A opção de pintar ambas as face
  do hud de materiais não está a funcionar").
  2026-10-29, later (his message with a screenshot of a wall run too long): **inner corners of an L / T / U** start a wall
  ("Não me está a deixar iniciar paredes interiores nos cantos da casa") — in line with either outside wall, one face
  flush with its finished inner face (line 0,095 in from the outline — ours), the way the pointer goes; **a room in the
  middle of the house** ("imaginemos que ele quer fazer quatro paredes no meio da casa … quero que seja possível"): a
  click away from every wall starts a free wall (in line with the walls near), the chain goes on and the last wall
  closes on the first, its free end becoming the corner; a first wall left alone on Esc goes (a wall touches another);
  **the closing snap** ("um snap que alinha a ultima parede com o canto da primeira parede criada, não um snap
  obrigatório mas apenas como sugestão"): within 0,40 the far end takes the first point's line, a dashed guide and a
  ring show it; **a piece of a wall** ("deve ser possível selecionar apenas esse "pedaço" de parede interior"): a click
  selects the piece between the walls that meet it (lit), the HUD offers "Eliminar troço" (an end piece shortens the
  wall to a corner, a middle piece splits it in two; walls that met only that piece get a free end) besides "Eliminar
  parede"; the **interior door** drawn as one (frame 3,5 cm / 3 cm head, architraves 7 cm both faces, the 80 × 200 leaf,
  a lever handle each side — "estão com um gap dos lados e na parte de cima … estão apenas um retângulo"); the
  **camera stays** where the client left it from step to step ("quero que continue na câmara que o cliente estava
  anteriormente"); shorter texts in step 4; a **"Como navegar pela casa"** pop-up at the start (rotate / zoom / pan /
  pick, touch; "Não voltar a mostrar"; again from the **?** button). The engine builds a free room and a corner wall
  (checked: an L with both, 7 walls, 0 notes).
- **Step 5**: cladding A / B / C with 3D sphere previews (`src/materiais.js`, textures drawn in the browser — to be
  replaced by photo-real ones; ambientCG-type assets are CC0 — check each licence). **Roof cards** (2026-10-28, "Deixa
  duas águas e várias águas apenas com empenas á vista"): rectangle — **Oculta** · "Duas águas, com empenas à vista"; L /
  T / U — Oculta · "Duas águas, com empenas à vista" (every end an empena, engine `duas_aguas`) · "Várias águas, com
  empenas à vista" (engine `misto`: the main body hipped, the wings' ends gables — ours, OPEN). The engine keeps
  `quatro_aguas` (not offered; a saved one opens as duas_aguas / misto). Slope in **%** from 15 % (default 15 %, up to
  100 %), degrees shown beside; beirado 0,20–**0,50** (max "Beirado vamos definir um máximo de 50 cm", 2026-10-28;
  `BEIRADO.max` 0,5, JSON `beirado_max`, the converter clamps), default 0,25. The roof drawn as the engine builds it:
  exposed — the exterior gutter on every eave, 2 downpipes per run 0,30 from its ends **joined to the gutter** (a piece
  from the outlet in the gutter's bottom down and back to the pipe — fixed 2026-10-28), ridge / rincão caps **folded down
  both slopes, lying on the panels** ("coladas à cobertura" — fixed 2026-10-28), caleiras de laró, verge trims, abutment
  flashings (gutter 125×90, downpipes 80 mm — assumed); the panels in the **Munditelha's own colour**, tile red with its
  waves (RAL 8004 — confirmed 2026-10-30 "é o ral 8004", hex #8F4E35; was "≈ RAL 8004, exact reference OPEN"; the hidden 5-ondas panel too — "Mais uma vez quero a cor original do painel de
  sandwich(mundiperfil painel sandwich) e não cinzenta a cobertura", 2026-10-29; was RAL 7016 grey); hidden ("**Oculta**"
  on screen since 2026-10-29: "muda o nome para este termo "Oculta" em vez de escondida … mais profissional no online
  builder" — the engine and saved designs keep the key "escondida") — **one água where it works, else two** (2026-10-28 "nós
  tentamos sempre só fazer uma água … Não quero que assumas um padrão"; engine `para_construtor.cobertura_escondida`:
  one slope across the beams to the side where every strip ends on one straight line, one straight gutter, each strip's
  panels in one length to its own high wall, a "remate de topo" against the high parapet; two slopes with the ridge mid
  main block, every slope ≥ 1 m, only if a panel would pass 15 m (13,5 until 2026-10-30 later) or no side is straight; a rectangle's gutter side
  chosen by the client with the buttons "Lado n" — default south, poente on a turned house; was south only, superseded
  2026-10-29, see registo), at the panel's minimum, no gaps where strips meet (`casa_planta.fechar_aguas`, fixed
  2026-10-28), caleira oculta **only on the low side** ("só tem uma água nós apenas precisamos de ter caleiras no lado
  para o qual o painel fica inclinado", 2026-10-29) — **one continuous gutter along a straight low wall** for strips side
  by side (one fall, outlets at its ends; each strip had its own, with end caps, a lining plate up to the parapet and two
  pipes side by side in the middle — "tinha uma peça aleatória no meio das caleiras", fixed 2026-10-29), the **outlets a
  hole in the gutter's bottom** against the parapet over each downpipe, the outlet under it ("estão em falta os buracos
  para os tubos de queda" — they had been holes in the parapet-side plate, unseen from above; outlet type OPEN),
  downpipes by drained area (one per 37 m², as Torres Vedras: at least 2, at the ends, more between — JSON
  `tubo.area_max_m2` — **superseded 2026-10-30, see §12 and registo**: 2 per gutter, 1 on a small one, bocal 10 cm; and
  2026-10-30 later: the outlet = the pipe, more pipes by 1 cm² per m²; 2026-10-30 later still: the hidden pipe **100 × 50**
  ≈ 50 m² each, his L 4 pipes, a recess in cork / ETICS boards, see §12); at the high side
  **no gutter, a top flashing lying on the panels** with a short leg up under the chapéu (it had a flat 12 cm shelf and
  looked like a gutter — ours; **his detail 2026-10-30 later: a waterproof sheet folded up the parapet + the metal
  flashing from its face down onto the panels**, `cobertura.remate_topo`); **chapéus round the whole perimeter, ≈ 2 cm down both faces** (2026-10-28),
  the parapet drawn as wide as the engine builds it — each cladding's own depth outside, its roof-side cladding or only
  the gutter's lining inside — so the chapéu covers the whole top ("o chapéu não esta a cobrir a largura toda", fixed
  2026-10-29), downpipes inside the cladding, the parapet at its height. **The parapets' roof side in the house's own façade finish** — OSB 15
  + Traspir + the façade build-up (`camadas.camadas_platibanda`) — "o capoto tem que ficar na casa toda" (2026-10-28;
  was Tremolo on every house, superseded 2026-10-28, see registo). The false ceiling comes with every roof ("Quando se
  aplica a cobertura automaticamente o teto falso já entra também"); a **"Teto"** toggle shows it from the engine
  (`camadas.tetos`: the Pladur underside at the pé direito) — "O testo falso ainda não aparece no builder e quero que
  isso seja possível de aparecer" (2026-10-28); no gap between roof and walls (the 3D roof a slab from the purlins' top).
- **Step 6** (`src/colocar.js`, drawings in `src/imagens.js`): catalogue — Janela 1,20 × 1,20 (sill 1,00, estore),
  Janela de correr 2,00 × 2,20 (estore), 3 folhas 2,70 × 2,20 and 4 folhas 3,60 × 2,20 (ours — "quero que cries opções de
  janelas de correr mas 3 janelas e 4 janelas"), Porta de entrada 1,00 × 2,20, Basculante 0,80 × 0,80 (sill 1,40,
  fosco), Vidro fixo 1,50 × 0,80 (sill 1,20, estore), Portão de garagem 3,00 × 2,20 (TV's table; the window, door and
  sills ours); doors and the portão never with an estore. Widths 0,40 to 1,50 (basculante) / 1,60 (door) / 3,00 (window,
  fixo) / 4,00 (sliding; 3 / 4 leaves wider) / 5,00 (gate). Limits (ours; the engine may still move an opening): rough
  opening = frame + 2,5 cm a side; ≥ 0,30 from a base corner; ≥ 0,08 between rough openings; ≥ 0,15 from an interior-wall
  junction; the shutter box drawn over the frame (the answer to "porque razão" the windows looked small); rough top
  under a hidden roof ≤ pé direito − 0,10; under an exposed roof the engine raises the exterior modules for the highest
  head ("opção a", confirmed 2026-10-28) with a note — it should name the opening that causes it (ours).
  Added 2026-10-28 ("Adicionar portas interiores ao menu de portas e janelas e permitir colocar portas e janelas nas
  paredes interiores"): a **"Porta interior"** card (0,80 × 2,00, rough 0,87 × 2,03) placed on interior walls; interior
  walls take **doors only** — "Só portas por norma ninguém usa janelas nas paredes interiores" (2026-10-29; the screen
  and the converter already allowed only doors there). Every opening but the garage door shows its **bottom rail** again
  ("as janelas ficaram sem a caixilharia na parte de baixo, aparece como se o vidro estivesse diretamente encostado à
  base").
- **Step 7** (2026-10-29; `src/exteriores.js`, `main.js` "step 7"; the engine `ferramentas/modelo/pergola.py`, JSON
  `pergola`): cards Pérgola · Garagem · Anexo, a list of what was added (click to select), Delete / Remover.
  (**2026-10-30 changes — see §12 and registo; the lines below are the 2026-10-29 state**: pergola's maximum = the top of the
  ground floor's ceiling beams; the shared wall of an attached block flush; interior walls never moved; separate ≥ 2,00 from
  the house; the gate adjustable; shorter texts.)
  **Pergola**: a click on an exterior wall places it against the cladding ("dando snap para o sítio no forro exterior"),
  4,00 wide by default, flush with a corner within 0,60, dragged along its wall, never past its side nor over the house,
  another pergola or a separate building; width (≥ 1,50), projection 1,50–5,00 (default 3,00), **height = the beams'
  underside at the facade, default and maximum = the top of the wall's ring + 0,10** (the ledger bolted to the ring, as
  TV: ring 2,653, ledger top 2,75) **and, under an exposed roof, clear of the eave and its gutter** (e.g. 2,47 under a
  15 % eave, 2,66 on a gable side) — "a altura tem de ter um máximo como sabes", our reading, to confirm; minimum 2,20;
  built as TV's pergola (posts 160×160 ≤ 3,5 apart, front beam 160×160, ledger 160×75 over the battens, beams 160×160 ≤
  1,40, slats 70×30 at 0,15; slope 5 % to the front — ours), slatted only (a covered one: ask); drawn from the engine's
  pieces. **Garage / annex** — area (m²) and front → the depth; **"Junto à casa (com ligação)"**: a click on a wall, the
  block there (flush with a corner within 0,60) — the outline grows by it (`exteriores.combinar`), so it is part of the
  house: our structure, the house's roof ("a cobertura tem de ser a mesma"); the old wall between them becomes an
  interior wall with a Porta interior (ends `canto` at the block's corners); a garage gets the 3,00 portão on its front;
  every door, window, interior wall, floor, inner-face finish and pergola is carried over to the new outline (what the
  block covers goes, with a note); editable (area, front) and removable (the outline shrinks back); **"Separada(o)"**:
  a click on the ground ≥ 1,00 m from the house and other buildings (ours), its roof the client's (Oculta / Duas águas),
  the house's cladding and pé direito, its portão (garage) or door (annex) on its front, dragged on the ground, "Rodar
  90°"; computed by the engine as a configured house of its own (worker `edificio_casa`) and priced the same way.
  Defaults (ours): garage 3,70 × 6,00 = 22,2 m² (12–80), annex 3,00 × 4,00 = 12 m² (6–60). Not yet: the structure view of
  a separate building; a separate building's openings beyond its door; a covered pergola.
- **Prices** (`src/precos.js`, placeholders): base 120 €/m²; exterior walls 215 €/m² of face (to the parapet); ETICS +15,
  cork +30 €/m²; windows 450 €/m² of frame, door 1 800, gate 3 200, estore 350; interior walls 95 €/m² (length × pé
  direito), wood +40, ceramic +30 €/m² a face; interior door 450; floor vinyl 35 / ceramic 45 €/m²; roof per m²
  (misto 92 €/m² — between 85 and 98); the false ceiling with every roof; a pergola 160 €/m² (width × projection); a
  separate garage / annex priced as a house of its own (a garage's floor ceramic). One line per element in the Lista.
- **Saving**: localStorage (this browser); "Guardar" downloads the design, "Abrir", "Recomeçar"; Desfazer / Refazer
  (Ctrl+Z / Ctrl+Y), up to 100 states, never back to "no house yet".
- **The exposed roof in the engine**: `ferramentas/modelo/telhado.py` (the roof of an orthogonal outline: the main body =
  the biggest rectangle, wings run into it; faces as plan polygons; lines cumeeira / rincão / laró / beirado / empena /
  encosto; types duas_aguas, quatro_aguas, misto) and `telhado_estrutura.py` (ceiling beams per wing down its slopes,
  22×7,5 ≤ 8 m free span, glulam beyond; a glulam **header** where a wing opens — the hangers fixed to it, confirmed
  2026-10-28 "Prendem-se as vigas laranja"; edge beams under the empenas; purlins 110×75 ≤ 1,2 in equal bays, pieces
  ≤ 3,67 jointed over a beam; prumos on every beam under them, ≤ 1 m on hip ends; a 110×75 under every rincão / laró;
  purlin ends stopped against those members; a ceiling beam under every top purlin of a slope running with the beams;
  packing where a prumo would be < 3 cm). Fixed 2026-10-29 ("junto as cumeeiras as vigas não encaixam nas cumeeiras …";
  "as vigas que dão a inclinação que se encontram na vertical apenas tem uma viga pousada a metade da sua largura";
  "vigas a sobreporem-se umas as outras nos cantos do triângulo da empena"): **the two top purlins of a ridge meet on the
  ridge line** (they stood 0,05 off it); **every prumo turned with its beam** (75 across it, 110 along) and its top cut
  to the member above; prumos on a beam line kept on the beam; **an empena starts past the eave purlin** (and a valley at
  its foot), framed where a plate and a top plate fit, a wedge packing between, the panel at its full width; a lower
  wing's purlins run on over the first beam under the higher body's gable. `casa_planta.py` "a_vista" (modules to pé direito − 0,05, raised for a high
  head); `camadas.py` `cobertura_faces`; production documents `gerar.py` `doc_cobertura_avista`. Checks:
  `ferramentas/configurador/auditar_cobertura.py` (one house or `--formas`, now with a rectangle + garage in L and T;
  the empenas' members against the roof timber and prumos past their beam's edge checked too, 2026-10-29) — 0 clashes,
  supports ok on every audited shape (2 single bare grid points on the U 25 × 10, as before); Blender validation 0 issues.

## 12. Changelog
- **2026-10-20** — spec v0.1 and the Kreativ study; phase 1 the divider (checked on TV); his answers: remainder ours,
  exterior ≤ 3 m, two close windows moved apart, site-built module as short as the opening; phase 2 the house format;
  phase 3 the browser prototype (shape, area + base price, 3 m walls, 3D).
- **2026-10-21** — his first review: every base side editable, only the total area in the panel; madres joined over an
  L; ceiling beams end inside against the modules ("não é realista" otherwise). Full-height exterior modules on every
  hidden roof. Phase 4: pé direito, doors and windows, interior walls, finishes, saving. His review of phase 4: walls
  joined at the corners, images for every option, the new step order, free interior walls, "hide the roof"; the exposed
  roof in the engine; the slope in % (15 % minimum).
- **2026-10-22** — the rulebook check's fixes (X1–X18: packing, edge beams, hip-end prumos ≤ 1 m, glulam by free span,
  purlin pieces, panels per slope, downpipes 0,30 from the ends, moved openings shown); the exposed roof's production
  documents and gable triangles; the interior finishes in the layers; Desfazer / Refazer. His answers (estribo de asa
  externa, Munditelha, estore 20 cm → 2,40, exterior walls' inner faces) and review 2 built: interior walls by clicks with
  snapping and 90° corners, rooms with m² and a floor each, HUD placement, the brush bug, every shape × roof audited
  (2 064 cases: the roof "to the sky" and the "mini telhado" fixed), beirado 0,20–0,55, Munditelha, 3- / 4-leaf sliding
  windows, the shutter box drawn.
- **2026-10-27** — roof cards: L / T / U also "Duas águas" ("Quero também com duas águas e depois várias águas"), new
  engine type `misto`; doors never take an estore (forced off); the hanger question re-asked with the sketch
  `configurador/docs/juncao_ala_estribos.svg` (its "22×7,5 a cada ≈ 0,60 m" is wrong — the rule is 1 m; fix if reused).
- **2026-10-28** — review 3 on his U 25 × 10 ("parecem haver vigas em falta e nas junções umas vigas +assam em cima das
  outras"): beams down a crossing wing's slopes, members stopped against one another (160 clashes → 0), a beam under the
  top of every rincão / laró, a T's bar eave stopped at the stem's gable; only roofs with empenas à vista; the hidden roof
  drawn as built at its height ("a forma que seria mais efeciente para a cobertura ser montada"); gutters and downpipes
  drawn ("faltam calheiras, tubos de queda e esses elementos"); hangers on the header and "opção a" confirmed.
- **2026-10-28, later** — "Estas a cometer erros que não fazem sentido": hidden-roof gaps where strips met (0 on 9
  shapes), exposed downpipes joined to the gutter, chapéus round the whole hidden roof ≈ 2 cm down, caps lying on the
  panels, the parapets' roof side in the house's façade finish. Answers: misto kept, beirado max 0,50, estribos at purlin
  ends, hidden roofs in one água chosen per house (his U: one slope, parapet 3,82; 8 of 9 shapes one slope); the
  header's "porquê" explained. Built: interior-wall corner faces, snapping to interior corners, distances to the
  corners, "ambas", the Porta interior card, the windows' bottom rail, the "Teto" toggle. The clean-up he allowed done
  (the knowledge base condensed).
- **2026-10-29** — his answers: the keeper and the rulebook agent on Sonnet ("Sim passa"); interior walls doors only
  ("Só portas …" — no change); the hidden roof's gutter side on a rectangle chosen by the client in step 5 ("Podes
  deixar o cliente escolher"; `cobertura.lado_caleira`, §8) — checked on 9 shapes, every side asked, 0 points without a
  panel.

- **2026-10-29, later** — his review in a new session (the screenshots stayed on his PC — not seen; reproduced from his
  text): "Oculta" on screen; the hidden roof's gutter only on the low side, one continuous gutter per low wall, outlets
  in the gutter's bottom, downpipes by area, the top flashing lying on the panels, the parapet as wide as the chapéu; the
  exposed roof's top purlins meeting on the ridge, prumos turned with their beam and cut to the member, empenas clear
  of the eave purlin; the Munditelha colour; the brand back to step 1; **step 7 Pérgolas, garagens e anexos**.
- **2026-10-29, later still** — the rulebook split by topic ("Sim, divide o livro do método por temas":
  `conhecimento/metodo-construtivo.md` index + `conhecimento/metodo/`); step 4: walls from the inner corners, rooms in
  the middle of the house with the closing snap, a wall's piece selected and removed, the interior door with frame,
  architraves and handle, the camera kept between steps, shorter texts, the navigation pop-up (§11).
- **2026-10-29, night** — his review of an L (12,35 × 11,90 + 8,05 × 6,10) in the three roofs, five screenshots:
  hidden roof — the gutter wall's parapet fought with the gutter lining on the screen (drawn 3 mm behind it now) and
  was lined red to its top: a parapet standing > 0,50 over the panels' ends (one água, its low side ~0,7) is now clad in
  the façade finish above a 0,10 lining lap (≤ 0,50 lined to the top as D2503 — TV 0,32 / 0,47; JSON
  `caleira_oculta.forro_ate_topo`, ours); the top flashing on the high side in the panel's colour (it read as a dark
  gutter); exposed roofs — every flashing and cap in the roof colour (`Remate cor da cobertura`; the dark grey round the
  gable "não é suposto"), the verges overhang as the eaves (a 0,12 verge met a 0,25 eave out of line — "não vais ter dois
  telhados desalinhados"), caps run 0,20 over a node so they overlap, eave gutters one per straight run with mitred
  corners (each eave piece had been its own gutter, crossing the next); the timber — purlins cut on the skew against the
  side of a hip / valley member, hip / valley members mitred where they meet ("no máximo podemos cortar a vigas com a
  diagonal necessária para encaixar as vigas umas na outras"). Audit 0 clashes on every shape. His request: "faz todas as
  questões que precisares para começarmos a fazer as coberturas sem falhas algumas" — the roof questionnaire (§13
  Roofs; sketch `configurador/docs/perguntas_coberturas_unioes.svg`).

- **2026-10-30** — his answers to the questions of 2026-10-29: the high side's closing — a waterproof board folded with
  a metal flashing (image promised); the outlet "Normalmente 10cm de bocal" (more by zone, slope, roof size) and "dois
  tubos por caleira a não ser que a caleira seja pequena" (one on a gutter ≤ 4,0 m, ours; was one per 37 m²); "é o ral
  8004", the hidden 5-ondas panel "imitação cor telha" too, grey only for Sobral; the panel's length variable, 1 m wide,
  the panels interlocking; the pergola's highest point at the ground floor's top ("até há altura máxima do PISO 0");
  garages / annexes — "faz mais sentido ficar separado da casa, dá um espaçamento de 3 metros pelo menos", then for the
  menu "pelo menos 2 metros" (2,00 built — to confirm). Built: step 6's ruler (each way to the nearest axis — a base
  corner or an interior wall meeting that side — typed when the opening is chosen); the false ceiling smooth (the
  boards' faces only, no profiles); step 7 — the wall into an attached garage / annex with its house side flush with the
  walls beside it, an attached block never moves nor removes interior walls (an end it can't keep becomes free), a
  separate one anywhere ≥ 2,00 from the house, ≥ 1,00 from another, never over a pergola, the garage gate's width and
  height in step 7 with step 6's limits, interior walls of an attached block in step 4 (a note says so), shorter texts.
  Not yet: interior walls inside a separate garage / annex (step 4 edits the house's outline only).

- **2026-10-30, later** — his answers: separate buildings 2 m ("pode ficar 2 metros"); interior walls only in attached
  garages / annexes ("apenas … quando são junto a casa" — a separate one says so); "usa o bocal ideal para esse tubo e
  distribui como achares melhor" → the outlet is the pipe's section (80 × 35 — **100 × 50 from 2026-10-30 later still,
  see the entry below**), downpipes two per gutter (one ≤ 4,0 m —
  "sim está bem") and more, evenly, for 1 cm² of pipe per m² drained (his L's hidden roof: 7 with the 80 × 35, 4 with the
  100 × 50; exposed runs likewise, ø 80 square pipes); the garage gate 0,30 under the ceiling ("sim exatamente"); the step-6 ruler from the opening's edge
  ("está perfeito"); the panels' top end at the high side as his detail (`configurador/docs/revisao/
  2026-10-30_remate_topo_paineis.png`: a waterproof sheet folded from the panels up the parapet, the metal flashing over
  it from the parapet's face down onto the panels — JSON `cobertura.remate_topo`, sizes read from the detail); the hidden
  panel's data sheet (`conhecimento/fontes/ficha_MC_1000-5_PUR_PIR.pdf`: Mundiperfil MC 1000/5, 30–100 mm, PUR / PIR,
  laps 300 mm over a support, ≥ 6 % without longitudinal laps, supports ≤ 1,50) and its maximum length "afinal o máximo
  do painel é 15 metros" (was 13,5 ours; he first wrote 25).

- **2026-10-30, later still** — his answers 1–5 to our five points (registo; he answered them with a `npm run dev`
  "Port 5173 is already in use" error, §9): **"1. Sim usa de 100x50"** → the hidden roof's downpipe is **100 × 50** (JSON
  `cobertura.caleira_oculta.tubo` `largura` 0,10, `profundidade` 0,05; ≈ 50 cm² → ≈ 50 m² per pipe at 1 cm² per m²);
  still ≥ 2 per gutter, 1 on a gutter ≤ 4,0 m, more evenly spaced by area — **his L now gets 4 pipes (was 7)**; the
  outlet (bocal) stays the pipe's section, so 100 × 50. It fits the standard Tremolo cavity (contra-ripado 20 + ripado 35
  = 55 mm); for **cork** (cavity 40 mm) and **ETICS** (no cavity) the cork / XPS boards get a **local recess round the
  pipe**; the visible boards (Tremolo) never get a hole; where the cavity behind them is too shallow (**Torres Vedras as
  built**: ripado 35 only, no contra-ripado) the engine prints a **warning** and limits the pipe to the cavity (33 mm) —
  code `ferramentas/modelo/camadas.py` `tubos_queda` and the façade layer loop, commit 0528d1b; exposed roofs keep 80 × 80.
  **"2. Sim tranquilo já agora usamos os de 80mm"** → the 15 m transport / movement points accepted; "os de 80mm" read as
  the sandwich panels being 80 mm = the hidden panel's `painel_oculto.espessura` 0,08, now confirmed (whether it also
  covers the Munditelha — ours 40 mm, "a confirmar" — is ambiguous and asked; nothing changed). "3." the coastal check
  was done (for TV — "um projeto usado para tu aprenderes sobre nós e nós irmos também avaliando as tuas sugestões");
  "4. Ok tranquilo" (PUR / PIR per house); "5. Depois quando abrir o configurador e testar digo-te mas parece-me bem"
  (the separate-blocks-keep-no-walls reading stays ours until he tests it, §13).

## 13. Pending from the user (current)
- **Step 7** — answered 2026-10-30 (registo; built, §12): the pergola's maximum height ("A pérgola pode ir até há altura
  máxima do PISO 0 ou seja do PISO TÉRREO … o ponto mais alto da pérgola pode ficar alinhado com a altura máxima desse
  piso térreo" — ring + 0,10 superseded 2026-10-30; built as the top of the ground floor's ceiling beams, ours: **ask which
  line he means** — ring top, ceiling-beam top or parapet top — and whether "ponto mais alto" is the top of the pergola's
  highest member, not the beams' underside at the façade); the shared wall of an attached garage / annex is "a parede
  interior … partilhada com a casa", flush with the walls beside it, and an attached block never moves or removes the
  interior walls ("aconteceu-me adicionar uma garagem e as paredes interiores algumas desapareceram"); separate:
  anywhere but over something placed (the house, a pergola …), "pelo menos 2 metros de distância da casa"; interior walls
  inside the garage / annex: the client builds them in step 4, step 7 only says so; the garage gate adjustable in width
  and height "respeitando as nossas regras estruturais (tal como no menu de portas e janelas)". ~~**Conflict to ask:**
  2026-10-30 answer 6 "dá um espaçamento de 3 metros pelo menos" vs the same message's "pelo menos 2 metros de
  distância da casa" (2,00 built)~~ — **closed 2026-10-30 (later): "pode ficar 2 metros"** (registo). **Closed 2026-10-30
  (later) too**: interior walls inside a separate garage / annex — "Não deixa apenas ficar ser possível ficar com paredes
  quando são junto a casa" (only attached blocks have interior walls; a separate one says so — our reading of a garbled
  sentence — **2026-10-30 (later still), our point 5 put it back to him: "Depois quando abrir o configurador e testar
  digo-te mas parece-me bem"** → still our reading, to be confirmed by him after testing the configurator); the garage
  gate capped at pé direito − 0,30 for the sectional door's mechanism — "sim exatamente". Also: "apenas deixe colocar … junto a casa" vs "se o cliente desejar … independente"
  (read: both kept). **Still open (ours, to confirm)**: slatted only or covered too (telha as TV / sandwich); the 5 %
  slope; the attached garage's wall — he calls it an interior wall (built: Porta interior), but a garage is unheated and a
  fire-risk neighbour (insulated wall + fire-rated door? — `insights.md` 2026-10-29) and an annex's heating; the
  separate buildings' pé direito (= the house's, ours) and the ≥ 1,00 m between two separate buildings (ours); each pergola
  post on a galvanised steel base, the timber ≥ 15 cm off the ground (general practice, ours); whether a garage / annex
  needs licensing (the screen does not say yet); ~~interior walls inside a SEPARATE building (not supported …)~~ (answered
  2026-10-30 later: none — only attached blocks); ~~the garage gate's height limit vs the sectional door's headroom (≈
  0,30)~~ (answered 2026-10-30 later: pé direito − 0,30; check the gate's cap on screen is this, not step 6's
  "pé direito − 0,10").
- **Roof questionnaire** (asked 2026-10-29 night — "faz todas as questões que precisares para começarmos a fazer as
  coberturas sem falhas algumas"; sketch `perguntas_coberturas_unioes.svg`; **not answered as a whole** — he promised it:
  "em relação ás perguntas das coberturas eu irei responder a tudo direitinho e fornecer-te esta informação" (2026-10-30);
  it supersedes the "Roof finish" and "Roofs" bullets where they are the same; he answers by these codes). **Answered in
  part 2026-10-30 (his answers to our reply's six questions, registo):** A1 deferred ("esta pergunta depois eu respondo-te
  quando abordar as questões todas das coberturas"); B1 colour **RAL 8004** (confirmed; the thickness / core / skin still
  open); E1 the hidden 5-ondas panel is "imitação cor telha" (taken as RAL 8004 too — ours); E2 the length "é variável",
  1 m wide, the panels interlock ("encaixamos um painel no outro") — ~~no maximum length given: 13,5 stays ours~~ →
  **closed 2026-10-30 (later): "acredita que o máximo de comprimento seja 25 metros", then "afinal o máximo do painel é 15
  metros"** (15 m; the data sheet MC 1000/5 handed over, `conhecimento/fontes/ficha_MC_1000-5_PUR_PIR.pdf`); E3 the
  top end is closed with a **waterproof sheet / board ("placa impermeável") that folds, plus a metal flashing** —
  ~~pending the image~~ → **closed 2026-10-30 (later): the image received** (`configurador/docs/revisao/
  2026-10-30_remate_topo_paineis.png`, "sim está bem"), built from it (JSON `cobertura.remate_topo`; the sheet as board vs
  membrane and the fold's height stay ours); E5 the outlet (**closed 2026-10-30 later: "usa o bocal ideal para esse tubo
  e distribui como achares melhor"** → outlet = the pipe's section (80 × 35; **100 × 50 since 2026-10-30 later still,
  "Sim usa de 100x50"**), 2 per gutter, 1 ≤ 4,0 m "sim está bem", more
  evenly spaced for 1 cm² per m²; the older text follows): "Normalmente 10cm de bocal mas pode ser maior dependendo da zona …
  inclinação … dimensão da cobertura" (what the 10 cm measures is not said), "dois tubos por caleira a não ser que a
  caleira seja pequena" — the one-per-37 m² rule is dropped (built: 2 per gutter, 1 on a gutter ≤ 4,0 m — "pequena" is
  ours; the exposed eave gutters the same — ours, he spoke of the hidden "caleira"); C2's "2 per run or 1 per 37 m²" is
  therefore closed for the hidden gutter (2 per gutter). **Still open there**: A2–A6, B1 thickness / core / skin (the
  hidden 5-ondas panel's thickness is 80 mm — "2. … usamos os de 80mm", 2026-10-30 later still, our reading; whether it
  also covers the Munditelha is asked, 40 mm stays "a confirmar"), B2–B5,
  C1, C3, D1–D4, E4 height rule and the lining's colour (assumed = RAL 8004), E5 overflow and the outlet's type, E6–E8
  (E2 number, E3 image, the bocal's size and a bigger roof's pipes: closed 2026-10-30 later):
  **A timber** — A1 ridge joint of the top purlins (a butted, cut to the slope — now / b on a ridge board-beam / c
  other); A2 purlin to hip / valley (a skew cut against its side — now / b over it / c other; fixing: inclined hanger,
  screw — "estribos." was said 2026-10-28, only the hanger's geometry is open); A3 purlins 110×75 flat ≤ 1,20 apart, joints
  over beams, pieces ≤ 3,67; A4 prumos 75×110 on the ceiling beams every ≤ 1,00 on beam lines; A5 glulam over the whole
  house past 8 m or only there; A6 ceiling beams across each wing. **B exposed roof** — B1 Munditelha thickness / core / skin
  / RAL; B2 flashings in the panel colour and Mundiperfil's pieces; B3 verge = eave overhang; B4 how the eave line is
  closed underneath; B5 a maximum slope, one slope for the whole house. **C gutters** — C1 eave gutter model / size
  (125 × 90 now) / colour (dark grey now); C2 exposed downpipes outside the cladding or inside, 2 per run or 1 per 37 m²,
  one at an inner corner instead of two; C3 valley gutter 0,50 wide in the panel colour, emptying into the eave gutter's
  corner. **D shapes** — D1 "Duas águas" on an L = each part its own ridge with gables and valleys (his screenshot 5), and on
  his L the main ridge on the 12,35 × 11,90 block (N / S gables) vs along the 20,40; D2 ridges at different heights (same
  slope) vs one height (different slopes); D3 "várias águas" body hipped, wings gabled — a nearly square body gives an
  almost-pyramid (his screenshot 3) — acceptable?; D4 default roof card on L / T / U. **E Oculta** — E1 hidden 5-ondas
  panel colour; E2 the panel's maximum length (13,5 now → **15 m, 2026-10-30 later**); E3 how the panels' top end is closed
  at the high side (he saw "caleiras" there twice → **his detail image, 2026-10-30 later**); E4 the gutter lining's height rule (§12 night: ≤ 0,50 lined to the top, taller 0,10 lap + the
  façade finish — ours; his 2026-10-20 "até ao topo" vs 2026-10-28 "o capoto … na casa toda") and colour; E5 outlet type /
  size, 1 downpipe per 37 m², overflow; E6 what goes under the chapéus (promise (5)); E7 parapet roof side OSB 15 + Traspir +
  façade finish; E8 a minimum parapet height over the panel (now ~5 cm at the high point plus the chapéu). Do not model any
  answer before he replies.
- **Roof finish**: closed 2026-10-30 — the Munditelha's colour is **RAL 8004** and the hidden 5-ondas panel is "imitação
  cor telha" (same colour — ours); "o cinzento foi apenas para sobral"; one downpipe per 37 m² → "dois tubos por
  caleira a não ser que a caleira seja pequena". **Closed 2026-10-30 (later)**: the remate de topo at a one-água roof's high side (his image, built;
  "sim está bem"); the bocal ("usa o bocal ideal para esse tubo e distribui como achares melhor" → the pipe's section
  80 × 35, 2 pipes per gutter, 1 ≤ 4,0 m, more evenly spaced for 1 cm² per m² — the cavity pipe's 28 cm² no longer
  limits the count; **2026-10-30 later still: the pipe 100 × 50, "Sim usa de 100x50", 4 on his L — closed**). Still open: the hidden gutter's lining colour —
  "Chapa cor telha" (the company's "Painel de alumínio cor telha de 80 cm", red at Torres Vedras) assumed = RAL 8004; the
  outlet's TYPE in the gutter (bottom, round, as Torres Vedras' photos, or side).
- **Roofs**: at a ridge the top purlins now meet on the ridge line, cut to the slope ("as vigas não encaixam nas
  cumeeiras", 2026-10-29) — how DiscoverCasa joins them there (a ridge beam, a plate, lapped?) to confirm (**deferred
  2026-10-30**: "esta pergunta depois eu respondo-te quando abordar as questões todas das coberturas" = A1); misto kept ("Tranquilo depois se necessário removemos essa opção", 2026-10-28) — if it goes, ask "duas
  águas" on an L as one ridge / two planes and a cross-gabled "várias águas" with the cards' images; the header — his
  reply to our explanation of 2026-10-28; the hidden roof: ~~the panel's maximum length (13,5 assumed)~~ (15 m, 2026-10-30 later), why TV took two slopes; the default card on an L / T / U (now
  Oculta, fitting "sempre coberturas ocultas" — ours); the ridge direction on a squarish 2-água L ("Num L quase quadrado em 2 águas, que direção de cumeeira
  preferes?" — unanswered since 2026-10-22); whether the 0,20 beirado minimum covers the verges (verges = eaves since 2026-10-29 night, ours — B3); Munditelha's
  thickness, core, skin, colour and data sheet (minimum slope, purlin span, overhang); exposed-roof downpipes outside or
  inside the cladding; how the eaves line is closed; the ridge madres' criterion (promise (7)).
- **Openings**: the verga threshold (2,8 / 3,0 / over 3,0); the 3- / 4-leaf sizes; a 2,5 cm clearance over the estore
  box (2,425 vs 2,40); two close openings when one is a door. Step 6's ruler (2026-10-30: "uma régua tipo a das paredes
  interiores … a distância a que está do eixo mais próximo", built): ~~does the distance run from the opening's edge or its
  centre to the axis~~ → **closed 2026-10-30 (later): from the opening's edge, "está perfeito"** (our question 6). The
  garage gate (step 7, adjustable in width and height with step 6's limits): max width by the
  verga rule (> 3,0 m wide: the glulam / engineer exception of TV's 11×7,5 — `metodo/03`; still ours); its height: the
  sectional door's headroom — **asked and confirmed 2026-10-30 later: pé direito − 0,30, "sim exatamente"**.
- **Interior walls**: the distance shown to the corners — from the base corner to the wall's centre line (ours) or from
  the finished inner corner to the wall's face (what a tape measures; ≈ 0,2 m less) — to confirm. At an inner corner of
  an L / T / U (2026-10-29) the wall's face is flush with the outside wall's finished inner face (line 0,095 in from the
  outline — ours): does he expect it centred on the outside wall's line instead? A room standing free in the middle
  touches no outside wall — its walls are held only by their corners, the floor and the ceiling beams (fine for
  partitions): tell him, and ask whether any of those walls must carry anything (ceiling beams that cross an interior
  wall bear on it — 2026-10-19; the concrete under it then takes a line load).
- **Finishes**: the list of interior finish materials — "Mias tarde vou ter fornecer uma lista de materiais para
  acabamentos interiores" (promise (8)); the palette waits for it.
- **Prices**: the price list (Product vision 2); the IVA rate.
- **Screenshots**: his review screenshots stay on his PC (`_trabalho/` is not in git) — suggested: save them in
  `configurador/docs/revisao/` so another session or device can see them (2026-10-29, later still: his step-4
  screenshot — a wall run too long past a T, circled red — is also only in the chat; the folder now exists — it holds his panel-top detail of 2026-10-30 later, the first image saved there; 2026-10-29 night: the 5 roof screenshots of his L — not in the repo
  either).
- **Promised answers** (2026-10-29, "Vai trabalhando nestes pontos enquanto eu preparo a resposta as outras perguntas"):
  he answered six of our reply's questions on 2026-10-30 (above; his words in the registo): the RAL (8004) and the hidden
  panel's colour, the remate de topo (described; **the image is promised**: "vou-te fornecer uma imagem que demonstra como
  fechamos a ponta dos painéis"), the outlet (10 cm) and downpipes (2 per gutter), the pergola's maximum height, the
  garage / annex ("faz mais sentido ficar separado da casa, dá um espaçamento de 3 metros pelo menos"), the Sobral grey
  (his own); the ridge joint deferred to the roof questionnaire. **Not answered**: the covered pergolas, the attached
  garage's wall (insulated / fire-rated door), the pé direito of separate buildings, licensing — keep the defaults, ask
  with the questionnaire. Pending from him now: ~~(a) the image of the panels' top end~~ (received 2026-10-30 later, built;
  kept at `configurador/docs/revisao/2026-10-30_remate_topo_paineis.png`); (b) the **whole roof
  questionnaire** ("eu irei responder a tudo direitinho"). He also answered
  only the first of our three token options ("Sim, divide o livro do método por temas"). **2026-10-30 (later)**: he
  answered our seven follow-up questions (registo): separate buildings 2 m, interior walls only in attached blocks,
  the outlet = the pipe, the garage gate pé direito − 0,30, the step-6 ruler from the edge, the panels' top-end detail
  (+ the Mundiperfil MC 1000/5 data sheet) and the panel's maximum 15 m (after a first "25"). **2026-10-30 (later
  still)**: he answered our five points (registo): the downpipe 100 × 50 (built), the 15 m panel "tranquilo" and "usamos
  os de 80mm", the coastal check done for TV, PIR noted. **Pending from him**: (c) after testing the configurator, his
  word on "interior walls only in blocks attached to the house" ("testar digo-te mas parece-me bem"); (d) whether
  "os de 80mm" covers the Munditelha too (asked).
- **Ours, not to ask**: the header's section and end bearings (engineer per house — a 200-deep header under 220 beams,
  posts under its ends, past ≈ 4 m over-stressed); the remate de topo lapped under the chapéu; the roof sweep to grow
  (a U with a garage); the flashing where a hidden ridge
  falls on a parapet line (two-slope case); the pé direito input (§7 q.12); the divider's preferred exterior length (§3).
  Closed 2026-10-28: the parapet's roof side (= the façade finish). Closed 2026-10-29: windows in interior walls (doors
  only — "Só portas por norma ninguém usa janelas nas paredes interiores"); a rectangle's hidden-roof gutter side (the
  client chooses — "Podes deixar o cliente escolher"); the one-água gutter's downpipes sized for the whole roof (one
  per 37 m², outlets between the ends — superseded 2026-10-30: "dois tubos por caleira a não ser que a caleira seja
  pequena", see the Roof finish bullet and `insights.md` 2026-10-30: a big one-água gutter on 2 pipes). Closed
  2026-10-30: the Munditelha / hidden-panel colour (RAL 8004); Sobral's grey (his own); the pergola's maximum height
  (answered, line to confirm); the false ceiling's visible lines (smooth). Closed 2026-10-30 (later): the separation of a
  separate garage / annex (2 m — the 3 m vs 2 m conflict); interior walls inside a separate block (none — to be
  confirmed by him after testing, 2026-10-30 later still); the outlet's
  size and the downpipes' number / spacing (the pipe's section, ours — 1 cm² per m²; the section itself 100 × 50, his,
  2026-10-30 later still); the garage gate's headroom cap (pé
  direito − 0,30); the step-6 ruler's origin (the opening's edge); the remate de topo (his image); the hidden panel's
  maximum length (15 m). Still ours: "pequena" ≤ 4,0 m (his "sim está bem" may only mean the detail).
