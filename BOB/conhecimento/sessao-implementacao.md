# Starting an implementation session (configurator, budgeting, client platform, builder)

The user develops the product implementations (`conhecimento/discovercasa.md` → "Product vision") in their own
Claude Code session, separate from the house-modelling session (user 2026-10-20: "quero que cries uma subsessão …
com todo o conhecimento que foste adquirindo e todas as ferramentas que fomos criando de forma a saberes construir
uma discovercasa"). **First implementation: item 4, the configurator in the IKEA style** (user 2026-10-20: "Nesta
subsessão vamos começar a criar o 4 ponto o configurador estilo IKEA"). The user opens the session and gives the
exact brief in their first prompt ("depois lá eu dou-te o contexto do que quero direitinho").

## 1. Work in your own folder (before editing anything)
Another session works in this checkout on `main` (house models). Start by moving to your own worktree and branch:
the `EnterWorktree` tool, or `git worktree add "../BOB Claude - configurador" -b configurador` and work there.
Commit there; push the branch when a task is finished; ask before merging into `main` (bring `main` in first).

## 2. Read (then only what each task needs)
1. `CLAUDE.md` (working rules, map).
2. `conhecimento/discovercasa.md` → "Product vision" (the 4 items) and "Working with the user".
3. `conhecimento/metodo-construtivo.md` (the METHOD rulebook, v6.4+): header, §0, §0a, §15; the rest on demand.
   Its keeper is the agent `mestre-construtor`.
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
- Prices: NOT yet (the user will give the price list with suppliers — Product vision item 2).

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
- The repo is PRIVATE (client data). Nothing goes online (a web configurator, models, prices) without the user's
  explicit OK on what and where. There is another local project of the company's website
  (`C:\Users\DiscoverCasa1\Desktop\DiscoverCasa site`, its own session "DiscoverCasa site") — ask before touching
  it or linking the configurator to it.
- Never open bulky/binary files directly (`*.dwfx`, `*.blend`, `*.glb`, `*_geometria.json`); scratch in `_trabalho/`.
- Commit messages short, in English, ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>".
  Git: origin is the private repo VascoCoelho/DiscoverCasa-Claude-BOB; pushes authenticate as VascoDiscovercasa via
  the repo-local credential helper (do not change accounts).

## 6. Open with the user (from the modelling session, 2026-10-20)
Remind them what goes under the chapéus (they asked); the hidden-gutter outlet type and bocal size (they will say);
the ladrão (explained; "penso que não"); their review of the generated Torres Vedras documents. (2026-10-20, night:
the Módulos document reviewed — "está absolutamente correto"; the Cobertura and Listagem de material: still pending.)
REA: the user runs `npx -y rea-agents@6.7.0 setup --client claude_code` and restarts (spec §8).
