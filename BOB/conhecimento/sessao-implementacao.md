# Starting an implementation session (configurator, budgeting, client platform, builder)

The user develops the product implementations (`conhecimento/discovercasa.md` → "Product vision") in their own
Claude Code session, separate from the house-modelling session (user 2026-10-20: "quero que cries uma subsessão …
com todo o conhecimento que foste adquirindo e todas as ferramentas que fomos criando de forma a saberes construir
uma discovercasa"). **First implementation: item 4, the configurator in the IKEA style** (user 2026-10-20: "Nesta
subsessão vamos começar a criar o 4 ponto o configurador estilo IKEA"). The user opens the session and gives the
exact brief in their first prompt ("depois lá eu dou-te o contexto do que quero direitinho").

## 1. Where to work (before editing anything)
Since 2026-11-05 the working repo for every application is **Discovercasa/design** (PUBLIC; BOB in its folder `BOB/`,
the site in `public/`) — user: "A partir de agora o repositório que vai ser utilizado para realizar mudanças em todas
as aplicações que temos em desenvolvimento vai ser o Discovercasa/Design". The old private repo and its branch
`configurador` are history only. Commit to Design; a push to `main` publishes `public/` (Cloudflare Pages), so after
changing `BOB/configurador/web`, `BOB/gerador/web` or the engine run `python BOB/ferramentas/construir_site.py` and
commit its output with the change. Work on a branch and merge into `main` when the user wants it live; ask before
pushing to `main` if unsure. Read the repo root `CLAUDE.md` (Design rules: Supabase, RLS, the Hub login) too.

## 2. Read (then only what each task needs)
1. `CLAUDE.md` (working rules, map).
2. `conhecimento/discovercasa.md` → "Product vision" (the 4 items) and "Working with the user".
3. `conhecimento/metodo-construtivo.md` (the METHOD rulebook, split by topic; index with the § → file map), then
   `metodo/01-principios.md` (§0, §0a) and `metodo/10-pontos-abertos.md` (§15); the other topic files in
   `conhecimento/metodo/` on demand (Grep a rule ID). Its keeper is the agent `mestre-construtor`.
4. `conhecimento/sistema-construtivo.md` (how DiscoverCasa builds: modules, layers, products, quantities, purchase
   units) and `conhecimento/perguntas-por-obra.md` (what varies per house, with defaults).
5. `Construção Torres Vedras/docs/estado.md` ("▶ Where we stopped"), `docs/modelos.md`, `docs/materiais.md`: the
   first house modelled end to end.
6. Skills `modelo-blender-madeira` (whole toolchain + "Production documents") and `ler-dwfx`; agents
   `guardiao-detalhes`, `mestre-construtor`.

## 3. What exists that a configurator can use
- The method as data: `ferramentas/modelo/sistema_construtivo.json` (structure sizes, module rules, build-up
  layers, finish options A/B/C, roof, caixilharia, materials with colours) + each house's `config.json`.
- The builder: `ferramentas/modelo/casa_planta.py` (walls → modules ≤ 3 m (superseded 2026-10-20, see registo: walls →
  the company's modules by `divisor_modulos.py`, configurator phase 1), amarração, lameladas, madres, gutters,
  parapets, pergola), `camadas.py` (layers, windows/doors, remates, roof covering), Blender build/validate/
  quantities, `ferramentas/documentos/gerar.py` (Módulos / Cobertura / Listagem de material). Pure Python except the
  Blender steps; `construir_casa.py` runs them.
- A complete house as reference: Torres Vedras (`modelos/casa/`, GLB `Casa_TorresVedras_Completa.glb`, material
  list `documentos/D2503_Listagem_Material.csv`).
- Team work in the hub (2026-11-11, supersedes the general chat 0018–0021): conversation lives in each task/checkpoint
  (table `atividade`, migrations 0022/0023). Claude writes through the database (no account): detail in the Log
  (`registo.detalhe`), questions to a person in the task's conversation tagging them (`marcacoes`); notify the team only for
  impact (task/checkpoint concluded, decision, critique). Read replies in `atividade` at the start of a session. Awaiting
  Dinis's answers (hub task 169 conversation, items 1–11) → file into `orcamento_parcelas` and the Orçamentação docs.
- Prices: since 2026-11-10 the price list comes from the Hub (the company's other system) into the Design Supabase,
  tables `hub_fornecedores`, `hub_materiais`, `hub_material_precos` (price per supplier: unit, discount, VAT, lead time,
  transport, dimensions…) and `hub_material_precos_historico`, sent on working days at 6:00 Lisbon (migration
  `supabase/migrations/0016_materiais_hub.sql`). READ ONLY: never write to them nor change their columns (the Hub's
  send would break). Read them with `public/js/materiais.js` (same origin and session as the apps); the team sees them
  in the hub's Materiais tab (`#/materiais`), with a CSV download for offline tools. Supplier contacts stay in the Hub.
  Discount and VAT come as fractions (0.23 = 23 %; first send, 2026-11-10: 54 suppliers, 971 materials of which 74
  services, 1 090 prices; most materials have no category yet). The module also accepts 0–100.
- Costing (Orçamentação, 2026-11-11): every Listagem line carries a stable product code (`ferramentas/documentos/codigos.py`,
  CSV column `codigo`); `orcamentacao/ligacoes.json` links each code to a Hub material id (never names or prices: public
  repo) with the price unit and how the line's quantity becomes it; `public/js/orcamento.js` prices a Listagem (cheapest
  price with discount in that unit; every missing price says why); page `/orcamentacao/` (source `orcamentacao/web/`,
  published by `construir_site.py`). Links are INFERRED until the team confirms them. Tests: `orcamentacao/tests/`,
  `tests/orcamentacao.spec.mjs`. A new layer or product in the engine needs a code rule, or the reference test fails.
  Final price: table `orcamento_parcelas` (migration 0017; values only in the database, never in the repo), `compor()`
  in `orcamento.js`, section «Preço final» of the page; areas from the Listagem's «Dados da obra» lines.

## 4. What the user said about the configurator (Product vision item 4)
"like IKEA Builder / IKEA Kreativ" for DiscoverCasa houses: the client gives the m² → the foundation base appears →
they assemble the house wall by wall, "neste caso módulo a módulo", seeing the price as they go; prices predefined
before any launch; "não temos qualquer tipo de problema de transparência". Everything else (platform, where it
runs, who uses it first, what a module offers, how the price is built) — ask the user. (Superseded 2026-10-20, night —
answered, see registo and `conhecimento/discovercasa.md` → Product vision 4; the spec is `configurador/docs/especificacao.md`:)
- the client uses it on the company website; browser first, then the website; the best way to build it — ours to
  recommend (spec §5); where the rules run — "logo veremos";
- shape first (several options), then the m² → the foundation base with its price → walls of 3 m, the last one on a
  side takes the rest, never past the base → doors and windows → interior walls; everything customisable;
- the client never sees "módulo" (wall by wall, "Estilo … jogo SIMS"); the engine divides the house into the company's
  modules by the openings and interior walls — the first thing to build;
- the price live and always on screen (+ / − per element); built from materials, labour, foundation, caixilharia,
  especialidades, installations and pre-installations, licensing and IVA; the prices are a future step;
- 3D that turns like IKEA's; single storey first; the foundation an indicative slab for now; Torres Vedras never shown.

## 5. Rules that matter most here
- PT-PT with the user, plain words; docs and code comments in English; refer to the user as they/them.
- Every detail the user gives: `guardiao-detalhes` logs it verbatim in `conhecimento/registo-conversas.md`
  and files it; method facts then go to `mestre-construtor`. Both sessions share these files — keep entries in date
  order when merging.
- Flag what looks off with a better option; build with the DiscoverCasa method; ask when in doubt.
- The repo is PUBLIC (since 2026-10-30): never personal data (NIF, addresses, phones, engineer IDs, personal names),
  never client drawings (`*.dwfx` / `*.pdf` are git-ignored; they stay on the PC). Nothing new goes online (models,
  prices) without the user's explicit OK on what and where. There is another local project of the company's website
  (`C:\Users\DiscoverCasa1\Desktop\DiscoverCasa site`, its own session "DiscoverCasa site") — ask before touching
  it or linking the configurator to it.
- Never open bulky/binary files directly (`*.dwfx`, `*.blend`, `*.glb`, `*_geometria.json`); scratch in `_trabalho/`.
- Commit messages short, in English, ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>".
  Git: origin is Discovercasa/design; pushes need a GitHub account with write there (DinisDiscover; cloud sessions:
  the account connected with `/web-setup`).

## 6. Open with the user (from the modelling session, 2026-10-20)
Remind them what goes under the chapéus (they asked); the hidden-gutter outlet type and bocal size (they will say);
the ladrão (explained; "penso que não"); their review of the generated Torres Vedras documents. (2026-10-20, night:
the Módulos document reviewed — "está absolutamente correto"; the Cobertura and Listagem de material: still pending.)
REA: the user runs `npx -y rea-agents@6.7.0 setup --client claude_code` and restarts (spec §8).
