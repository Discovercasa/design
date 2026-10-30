# BOB — DiscoverCasa's Claude workspace

DiscoverCasa (Penafiel, Portugal) designs and builds turnkey houses with a **timber-frame structure
on a concrete foundation**. This repo holds the knowledge and tools that let Claude work on
DiscoverCasa projects from any device.

## Working rules
- Talk to the user in Portuguese (PT-PT) — the user's choice since 2026-10-09 (earlier messages are in
  English). Drawings, model object names and company documents are Portuguese: keep the technical terms
  exactly as they appear in the drawings. Repo docs stay in English.
- If something is ambiguous (conflicting drawings, the goal of a task), ask a short question
  instead of guessing.
- **Every detail the user gives matters** (construction): before a task ends, record it verbatim in
  the current log (`conhecimento/registo-conversas.md`) and file each fact in its document — delegate this to the agent
  `guardiao-detalhes` (it also checks the new facts against everything recorded); when they are about how
  DiscoverCasa builds, then have `mestre-construtor` fold them into the method rulebook.
- **Always say when something looks off or could be improved**: the issue, why it matters, and what
  you suggest instead (the user asked for this, even when they already know the point).
- **Always build with the DiscoverCasa method**: architects' (and engineers') construction notes are not
  binding — they fix the geometry, DiscoverCasa decides how it is built (user 2026-10-09, 2026-10-15).
- Project DWFx drawings are fabrication drawings of prefabricated **modules** (wall panels, floor,
  roof) assembled on site. How modules are fixed to the foundation is intentionally not shown in
  them — do not report that as a gap.
- Never open binary or bulky generated files directly (`*.dwfx`, `*.blend`, `*.glb`,
  `*_geometria.json`): use the tools, which print only what is needed.
- **Implementation sessions** (configurator, budgeting, client platform, builder): read
  `conhecimento/sessao-implementacao.md` first and work in your own worktree/branch (user 2026-10-20).
- **Every new project: ask the per-project questions** of `conhecimento/perguntas-por-obra.md` (what
  changes from house to house; use the stated default when unanswered) — the user asked for it 2026-10-20.
- The repo is public (Discovercasa/design, folder `BOB/`): never write NIF, addresses, phone numbers,
  engineer IDs or personal names; client drawings (`desenhos/`, source PDFs) stay local, not in Git (user 2026-10-30).

## Map (read only what the task needs)
| Path | Contents | Read when |
|---|---|---|
| `conhecimento/discovercasa.md` | company facts, how the user works | company context |
| `conhecimento/sistema-construtivo.md` | **how DiscoverCasa builds**: structure sizes, wall layers outside/inside, finish options, floors, ceilings, sandwich roof, products, site materials lists (sources in `conhecimento/fontes/`) | anything about build-ups, materials, quantities |
| `conhecimento/construcao-madeira.md` | timber-frame method, timber↔concrete rules (with numbers), PT regulations, termites, grading, connectors, PT↔EN glossary | technical questions, drawing reviews |
| `conhecimento/registo-conversas.md` | the user's messages verbatim, dated, with where each fact was filed (one file, condensed 2026-10-28) | to find exactly what the user said (Grep, don't read it all) |
| `conhecimento/perguntas-por-obra.md` | questions to ask on every new project (items that vary per house, with defaults) | start of every new project |
| `conhecimento/insights.md` | our technical insights and suggestions to the user, dated, with status (user 2026-10-21) | before advising; add each new insight |
| `Construção Sobral/` | Loteamento Sobral project (16 houses + warehouse), has its own `CLAUDE.md` (paused 2026-10-15; two-storey houses, "estará para avançar brevemente" — 2026-10-20) | any work on that project |
| `Construção Torres Vedras/` | house already built — model it from the architecture and compare with the real materials (current focus) | any work on that project |
| `configurador/` | the client's IKEA-style house configurator (Product vision 4; branch `configurador`): spec, Kreativ study | configurator work |
| `ferramentas/` | Python / PowerShell / Blender tools | via the skills below |
| skill `ler-dwfx` | read, render, zoom and measure DWFx drawings | a .dwfx must be read |
| skill `modelo-blender-madeira` | build/update Blender models from drawings (structure + build-up layers); production documents (Módulos, Cobertura, Listagem de material: `ferramentas/documentos/gerar.py`) | 3D modelling work; documents for a house |
| agent `guardiao-detalhes` (`.claude/agents/`) | records every detail (log + docs) and checks for conflicts, pending items, improvements | end of every task with new user info; audits |
| agent `mestre-construtor` + `conhecimento/metodo-construtivo.md` (index) → `conhecimento/metodo/` (topic files) | the METHOD rulebook (how DiscoverCasa builds, rule by rule, with sources and lessons from model errors), split by topic: read the index, then only the topic file(s) needed; checks models against it | after `guardiao-detalhes` files new facts; "how do we build X?"; before/after building a model |

New project → new top-level folder `Construção <Nome>/` with the same layout
(`CLAUDE.md`, `desenhos/`, `docs/`, `modelos/`). Nothing project-specific at the repo root.

## Requirements on a new device
Python ≥ 3.10 (standard library only) · Blender ≥ 4.4 (auto-detected, or set `BLENDER_EXE`) ·
Windows PowerShell only for rendering DWFx sheets to images (text/geometry extraction works on any OS).
Check a device with `python ferramentas/verificar.py`. Scratch output goes to `_trabalho/` (git-ignored).

## Keeping the knowledge current
- This file loads in every session: keep it under ~80 lines; details belong in the linked docs.
- When you learn something durable (user decision, drawing fact, correction, new method), update
  the matching doc in the same commit as the work: status/decisions → `Construção <X>/docs/estado.md`,
  drawing facts → `docs/desenhos.md`, procedures → the skill's `SKILL.md`.
- Commit messages: short, in English. Push when a task is finished (ask if unsure).
