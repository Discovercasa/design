# DiscoverCasa construction method (método construtivo) — the rulebook

How DiscoverCasa builds a house, ordered like the work on site. Kept by the agent `mestre-construtor`
(`.claude/agents/mestre-construtor.md`).
**INDEX — the rulebook is split by topic** (2026-10-29, user "Sim, divide o livro do método por temas"): this file holds the
version, how to use the book, the section map and the legend; the rules are in `conhecimento/metodo/`, one file per topic,
text unchanged, § numbers and rule IDs kept ("rulebook §7", "metodo-construtivo.md §13" resolve through the map below).

**Version 8.18, 2026-11-23** — ripado cladding on an ETICS facade replaces the ETICS zone, flush with the render, corner to corner; pier cladding to the ground (§8); L76 (Matosinhos 3D review before any preview). Depth 66 vs 74 vs 77 mm open.
**Version 8.17, 2026-11-19** — **the Listagem gives a total per timber section (pieces, m, m³) and a «Compra» for every product in the Hub material the company buys** (user rule, §0a); ours: timber as m³ of casquinha 230x78 board by our cutting yield, pieces > 5,70 m flagged (§0a, §11; open: §15 item 27).
**Version 8.16, 2026-11-19** — **"Casa CL" = Ribamar's module sheets as built** (byte-identical, found 2026-11-19, to confirm;
new scope tag **[RB]**): module heights read again — upper exterior 3,52 only on the two gutter sides (was our "upper 3,52 ext",
§2, §5); wide openings given as clear rough openings, M014's verga over 2,77 = as-built evidence for the OPEN threshold (§3,
§13); the PDF module-sheet readers (§0a, §5); Ribamar's points against the rulebook (§15 [RB], X-list [RB]). No new user rule.
**Version 8.15, 2026-11-10** — an opening cuts only the faces parallel to its module, never the perpendicular façade at a corner (§3, L75; AR-test model error, fixed in `camadas.aberturas_face`).
Older notes (v8.14 moved in v8.17; v8.13 … v8.6 moved in v8.16; v8.5, v8.4, v8.3, v8.1–v8.2, v8.0: condensed at the user's
request; before it: git) and the original header paragraph in full: `metodo/00-historico.md`. The user's words in full:
`conhecimento/registo-conversas*.md` (since 2026-11-09 `-2026-3`); the "why" of each detail: the topic docs.

## How to use (read ≈ 20–50 KB per task, not 190 KB)
1. Read this index, then **only the topic file(s) the task touches** (map below); roof work: 05 and/or 06 (gutters and downpipes
   of the hidden roof: 11), usually with §6 in 04.
2. Find a rule by ID or word: `grep -rn "X15" conhecimento/metodo/`. IDs: **E1–E11** exposed-roof build steps (05) ·
   **L1–L75** lessons (09) · **X1–X20** builder deviations (defined in 12, cited in 03/04/05/06/08/10) · **PO Qn** = question n
   of `conhecimento/perguntas-por-obra.md`. References inside the files ("§7", "L46") keep these numbers.
3. Writing: a rule goes into its topic file under its §; a new topic = a new file + a row below. The version and its notes
   live only here (a topic file's first line names the version at the split — leave it). Read every file only for a full audit.

## Map: § → file (all in `conhecimento/metodo/`)
| § | File | What it covers |
|---|---|---|
| 0 | `01-principios.md` | Principles: the DiscoverCasa method over architects' notes; geometry vs method; scope; how to ask; clear height; spacings |
| 0a | `01-principios.md` | Production documents of every house (Módulos, Cobertura, Listagem de material; the D2503 format) |
| 1, 2 | `02-fundacao-modulos.md` | Foundation base; wall modules: sections, studs, plates, module length and splitting, height and position, corners |
| 3, 4 | `03-vaos-topo-paredes.md` | Openings (vãos: ombreiras, padieira, peitoril, verga, doors, caixilharia, remates); top of the walls (afinação, amarração) |
| 5, 6, 10 | `04-pisos-tetos.md` | Floor between storeys; ceilings (tetos: beams, 8 m limit, glulam, suspension); finish floors (pavimentos) |
| 7 | `05-coberturas-vista.md` | Roofs: choice, covering (sandwich), structure (prumos, purlins, madres), slope; exposed roof and its build in order (E1–E11) |
| 7 | `06-cobertura-oculta.md` | Hidden roof (Oculta): one água, slope, covering (the 80 mm MC 1000/5 panel, 15 m), parapets, chapéus, how the engine builds it |
| 7 | `11-caleiras-tubos-oculta.md` | Hidden roof, the water: caleira oculta (company build, [TV] as built), **downpipes 100 × 50** (count by area, recess), outlet holes, overflow |
| 8, 9 | `07-paredes-exterior-interior.md` | Exterior walls outside (OSB, Traspir, finishes A/B/C, battens; pergolas, garages, annexes); walls inside (wool, Pladur) |
| 11, 12, 13 | `08-produtos-limites.md` | Products, brands, purchase units, waste; site consumables; spans and limits the company uses |
| 14 | `09-licoes.md` | Lessons L1–L75 from model errors: what went wrong → the rule → where it lives |
| 15 | `10-pontos-abertos.md` | Still unknown or assumed: promised, pending, the roof questionnaire (A1–E8), [SB] / [RB] points, to ask / tell, ours |
| 15 | `12-desvios-construtor.md` | What the builder still assumes or does differently from the rulebook (X1–X20, other assumptions) |
| header | `00-historico.md` | The original version paragraph (v8.0–v8.3) |

## Legend — line format, scope, sources, status (valid in every file)
**Line format:** `- rule — source — status — where applied`
- **Scope**: no tag = **company standard** (every house). **[TV]** = Torres Vedras only, **[SB]** = Sobral only, **[RB]** =
  Ribamar only (since v8.16: the house behind "Casa CL", `Construção Ribamar/docs/`) — a
  project fact (that project's cfg and `docs/`), never copied to another house without the user calling it the norm
  (§0 "Scope"). **Why [TV] is in the book** — his words, 2026-10-30 (later still): "torres vedras foi um projeto usado para
  tu aprenderes sobre nós e nós irmos também avaliando as tuas sugestões": a house already built, given to us to learn how
  DiscoverCasa builds and where our suggestions are evaluated; its as-built facts teach and test, they are not the standard
  by themselves (§0 "What [TV] is"). **[cfgr]** = a configurator product rule (the spec `configurador/docs/especificacao.md` is its home).
- Sources: `user YYYY-MM-DD "quote"` (verbatim in the registo, `registo-conversas*.md`) · **draft** =
  company draft "Execução Técnica OBRA" (`fontes/execucao-tecnica-obra_2026-09-24.md`; its foundation list "Copiado de
  Ribamar") · **Casa CL** = company module drawings (`fontes/estrutura-exemplo-casa-cl/`) = **Ribamar's module sheets as
  built** — byte-identical to the hub's «Ribamar Módulos», the «CASA CL» title block a template (found 2026-11-19; user
  "tens os módulos direitinhos de como foram feitos para ribamar"; **to confirm with him**): its general framing teaches the
  method, its house-specific features are **[RB]** project facts (§0 Scope; read in `Construção Ribamar/docs/desenhos.md`;
  sheet «piso 1» = Piso 0, «piso 2» = Piso 1) · **3_Vigamento** = company base-framing sheet of another house
  (`fontes/vigamento-base/3_Vigamento.pdf`) · **D2503** = DiscoverCasa's roof production drawing of TV, the roof as built
  (`Construção Torres Vedras/desenhos/250828_D2503_Cobertura.dwfx`; read in TV `docs/cobertura-D2503.md`) · **D2503
  Módulos** = the wall-module production drawing of TV (`…/250828_D2503_Modulos.dwfx`; TV `docs/modulos-D2503.md`) ·
  project drawings. Topic docs: **SC** = `sistema-construtivo.md`, **CM** = `construcao-madeira.md`; **TV** / **SB** / **RB** =
  `Construção Torres Vedras/` / `Construção Sobral/` / `Construção Ribamar/` docs (`#n` = item in that project's
  `docs/revisao-tecnica.md`; RB: `docs/estado.md` "Open questions" Qn).
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
