# DiscoverCasa configurator — specification (current state 2026-10-29)

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

Always on screen (Kreativ): the 3D view, Vista de cima and side views, Desfazer / Refazer, **the total price**, a
**Lista** with every element's price. Saving / sharing a design online and "pedir orçamento": later (a server and a
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
  +y north; added 2026-10-29), the finishes, the pé direito.
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
- **Step 5**: cladding A / B / C with 3D sphere previews (`src/materiais.js`, textures drawn in the browser — to be
  replaced by photo-real ones; ambientCG-type assets are CC0 — check each licence). **Roof cards** (2026-10-28, "Deixa
  duas águas e várias águas apenas com empenas á vista"): rectangle — Escondida · "Duas águas, com empenas à vista"; L /
  T / U — Escondida · "Duas águas, com empenas à vista" (every end an empena, engine `duas_aguas`) · "Várias águas, com
  empenas à vista" (engine `misto`: the main body hipped, the wings' ends gables — ours, OPEN). The engine keeps
  `quatro_aguas` (not offered; a saved one opens as duas_aguas / misto). Slope in **%** from 15 % (default 15 %, up to
  100 %), degrees shown beside; beirado 0,20–**0,50** (max "Beirado vamos definir um máximo de 50 cm", 2026-10-28;
  `BEIRADO.max` 0,5, JSON `beirado_max`, the converter clamps), default 0,25. The roof drawn as the engine builds it:
  exposed — the exterior gutter on every eave, 2 downpipes per run 0,30 from its ends **joined to the gutter** (a piece
  from the outlet in the gutter's bottom down and back to the pipe — fixed 2026-10-28), ridge / rincão caps **folded down
  both slopes, lying on the panels** ("coladas à cobertura" — fixed 2026-10-28), caleiras de laró, verge trims, abutment
  flashings (gutter 125×90, downpipes 80 mm — assumed); hidden — **one água where it works, else two** (2026-10-28 "nós
  tentamos sempre só fazer uma água … Não quero que assumas um padrão"; engine `para_construtor.cobertura_escondida`:
  one slope across the beams to the side where every strip ends on one straight line, one straight gutter, each strip's
  panels in one length to its own high wall, a "remate de topo" against the high parapet; two slopes with the ridge mid
  main block, every slope ≥ 1 m, only if a panel would pass 13,5 m or no side is straight; a rectangle's gutter side
  chosen by the client with the buttons "Lado n" — default south, poente on a turned house; was south only, superseded
  2026-10-29, see registo), at the panel's minimum, no gaps where strips meet (`casa_planta.fechar_aguas`, fixed
  2026-10-28), caleira oculta, **chapéus round the whole perimeter, ≈ 2 cm down both faces** (2026-10-28), downpipes
  inside the cladding, the parapet at its height. **The parapets' roof side in the house's own façade finish** — OSB 15
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
- **Prices** (`src/precos.js`, placeholders): base 120 €/m²; exterior walls 215 €/m² of face (to the parapet); ETICS +15,
  cork +30 €/m²; windows 450 €/m² of frame, door 1 800, gate 3 200, estore 350; interior walls 95 €/m² (length × pé
  direito), wood +40, ceramic +30 €/m² a face; interior door 450; floor vinyl 35 / ceramic 45 €/m²; roof per m²
  (misto 92 €/m² — between 85 and 98); the false ceiling with every roof. One line per element in the Lista.
- **Saving**: localStorage (this browser); "Guardar" downloads the design, "Abrir", "Recomeçar"; Desfazer / Refazer
  (Ctrl+Z / Ctrl+Y), up to 100 states, never back to "no house yet".
- **The exposed roof in the engine**: `ferramentas/modelo/telhado.py` (the roof of an orthogonal outline: the main body =
  the biggest rectangle, wings run into it; faces as plan polygons; lines cumeeira / rincão / laró / beirado / empena /
  encosto; types duas_aguas, quatro_aguas, misto) and `telhado_estrutura.py` (ceiling beams per wing down its slopes,
  22×7,5 ≤ 8 m free span, glulam beyond; a glulam **header** where a wing opens — the hangers fixed to it, confirmed
  2026-10-28 "Prendem-se as vigas laranja"; edge beams under the empenas; purlins 110×75 ≤ 1,2 in equal bays, pieces
  ≤ 3,67 jointed over a beam; prumos on every beam under them, ≤ 1 m on hip ends; a 110×75 under every rincão / laró;
  purlin ends stopped against those members; a ceiling beam under every top purlin of a slope running with the beams;
  packing where a prumo would be < 3 cm). `casa_planta.py` "a_vista" (modules to pé direito − 0,05, raised for a high
  head); `camadas.py` `cobertura_faces`; production documents `gerar.py` `doc_cobertura_avista`. Checks:
  `ferramentas/configurador/auditar_cobertura.py` (one house or `--formas`) — 0 clashes on every audited shape;
  Blender validation 0 issues.

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

## 13. Pending from the user (current)
- **Roofs**: misto kept ("Tranquilo depois se necessário removemos essa opção", 2026-10-28) — if it goes, ask "duas
  águas" on an L as one ridge / two planes and a cross-gabled "várias águas" with the cards' images; the header — his
  reply to our explanation of 2026-10-28; the hidden roof: the panel's maximum length (13,5 assumed), why TV took two slopes; the default card on an L / T / U (now
  Escondida, fitting "sempre coberturas ocultas" — ours); the ridge direction on a squarish 2-água L ("Num L quase quadrado em 2 águas, que direção de cumeeira
  preferes?" — unanswered since 2026-10-22); whether the 0,20 beirado minimum covers the verges (0,12 now); Munditelha's
  thickness, core, skin, colour and data sheet (minimum slope, purlin span, overhang); exposed-roof downpipes outside or
  inside the cladding; how the eaves line is closed; the ridge madres' criterion (promise (7)).
- **Openings**: the verga threshold (2,8 / 3,0 / over 3,0); the 3- / 4-leaf sizes; a 2,5 cm clearance over the estore
  box (2,425 vs 2,40); two close openings when one is a door.
- **Interior walls**: the distance shown to the corners — from the base corner to the wall's centre line (ours) or from
  the finished inner corner to the wall's face (what a tape measures; ≈ 0,2 m less) — to confirm.
- **Finishes**: the list of interior finish materials — "Mias tarde vou ter fornecer uma lista de materiais para
  acabamentos interiores" (promise (8)); the palette waits for it.
- **Prices**: the price list (Product vision 2); the IVA rate.
- **Ours, not to ask**: the header's section and end bearings (engineer per house — a 200-deep header under 220 beams,
  posts under its ends, past ≈ 4 m over-stressed); the one-água gutter's downpipes sized for the whole roof (the 2 per
  gutter are too few on a big roof) and the remate de topo lapped under the chapéu; the flashing where a hidden ridge
  falls on a parapet line (two-slope case); the pé direito input (§7 q.12); the divider's preferred exterior length (§3).
  Closed 2026-10-28: the parapet's roof side (= the façade finish). Closed 2026-10-29: windows in interior walls (doors
  only — "Só portas por norma ninguém usa janelas nas paredes interiores"); a rectangle's hidden-roof gutter side (the
  client chooses — "Podes deixar o cliente escolher").
