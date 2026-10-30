# DiscoverCasa construction method (método construtivo) — the rulebook

How DiscoverCasa builds a house, ordered like the work on site. Kept by the agent `mestre-construtor`
(`.claude/agents/mestre-construtor.md`).
**INDEX — the rulebook is split by topic** (2026-10-29, user "Sim, divide o livro do método por temas"): this file holds the
version, how to use the book, the section map and the legend; the rules are in `conhecimento/metodo/`, one file per topic,
text unchanged, § numbers and rule IDs kept ("rulebook §7", "metodo-construtivo.md §13" resolve through the map below).

**Version 8.8, 2026-10-30 (later still)** — latest notes. **v8.8** (his answers to our five points): **the hidden-roof downpipe is
100 × 50** ("Sim usa de 100x50": ≈ 50 m² per pipe, his L 4 pipes not 7, [TV] 2 = as built; fits the standard Tremolo cavity —
contra-ripado 20 + ripado 35 —, a local recess in cork / XPS where shallower, never a hole in the visible boards: one more
reason to keep the contra-ripado; supersedes the 80 × 35; PO Q16's section part closed); the **hidden sandwich panel is 80 mm**
("usamos os de 80mm" — whether also the Munditelha: asked, open) with the 15 m panel's transport / movement accepted ("Sim
tranquilo"); PIR vs PUR and the marine-air coating per house ("Ok tranquilo"; "já foi verificado" for TV); **what [TV] is**
("um projeto usado para tu aprenderes sobre nós e nós irmos também avaliando as tuas sugestões"); interior walls only in an
attached block stays our reading ("parece-me bem", his test pending) (§0, §7, §8, §11, §15; L70). **Files**: 06 split — the
hidden gutter / downpipe detail moved to the new `11-caleiras-tubos-oculta.md`; 10 split — the builder's deviations (X1–X20)
moved to the new `12-desvios-construtor.md`. **v8.7** (his answers, later the same day): downpipe outlet = the pipe's own
section (80 × 35 hidden / 80 × 80 exposed), two per gutter, one on one ≤ 4,0 m, more by area (1 cm² per m²); the one-água high
side closed per his detail (folded waterproof sheet + metal flashing, E3 closed); hidden panel Mundiperfil MC 1000/5, maximum
15 m (E2 closed); garage gate top 0,30 under the ceiling; a separate building ≥ 2,00 m (closes 3 vs 2); interior walls only in
attached blocks (§3, §7, §8, §15; supersedes the 10 cm bocal and the 13,5 m). **v8.6** (his answers to the roof questionnaire
and step 7): panel colour RAL 8004 (Munditelha and the hidden 5-ondas; Sobral's grey = [SB]; flashings, lining assumed the
same), downpipes two per gutter / one on a small one (replaces "one per 37 m²"), pergola top ≤ the ground floor's top, an
attached block's wall flush with its neighbours (§7, §8, §11, §15; L70).
Older notes (v8.5, v8.4, v8.3, v8.1–v8.2, v8.0: condensed at the user's
request; before it: git) and the original header paragraph in full: `metodo/00-historico.md`. The user's words in full:
`conhecimento/registo-conversas.md`; the "why" of each detail: the topic docs.

## How to use (read ≈ 20–50 KB per task, not 190 KB)
1. Read this index, then **only the topic file(s) the task touches** (map below); roof work: 05 and/or 06 (gutters and downpipes
   of the hidden roof: 11), usually with §6 in 04.
2. Find a rule by ID or word: `grep -rn "X15" conhecimento/metodo/`. IDs: **E1–E11** exposed-roof build steps (05) ·
   **L1–L70** lessons (09) · **X1–X20** builder deviations (defined in 12, cited in 03/04/05/06/08/10) · **PO Qn** = question n
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
| 14 | `09-licoes.md` | Lessons L1–L70 from model errors: what went wrong → the rule → where it lives |
| 15 | `10-pontos-abertos.md` | Still unknown or assumed: promised, pending, the roof questionnaire (A1–E8), to ask / tell, ours |
| 15 | `12-desvios-construtor.md` | What the builder still assumes or does differently from the rulebook (X1–X20, other assumptions) |
| header | `00-historico.md` | The original version paragraph (v8.0–v8.3) |

## Legend — line format, scope, sources, status (valid in every file)
**Line format:** `- rule — source — status — where applied`
- **Scope**: no tag = **company standard** (every house). **[TV]** = Torres Vedras only, **[SB]** = Sobral only — a
  project fact (that project's cfg and `docs/`), never copied to another house without the user calling it the norm
  (§0 "Scope"). **Why [TV] is in the book** — his words, 2026-10-30 (later still): "torres vedras foi um projeto usado para
  tu aprenderes sobre nós e nós irmos também avaliando as tuas sugestões": a house already built, given to us to learn how
  DiscoverCasa builds and where our suggestions are evaluated; its as-built facts teach and test, they are not the standard
  by themselves (§0 "What [TV] is"). **[cfgr]** = a configurator product rule (the spec `configurador/docs/especificacao.md` is its home).
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
