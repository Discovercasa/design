# DiscoverCasa interior design — the rulebook (guidelines)

How DiscoverCasa designs and draws interiors: composition, measures, styles, pieces, light, 3D realism and the same
library for the page 3D, the 360° tour, AR and VR. Kept by the agent `designer-interiores`
(`.claude/agents/designer-interiores.md`). Hub: Páginas, checkpoint 44 «Interiores realistas por estilos».

**Version 1.0, 2026-11-27** — built from the user's «Manual de Regras — Design de Interiores» v1.0 (source, word for word:
`conhecimento/fontes/design-interiores/manual-regras-v1.0.md`), translated and tightened, every rule tagged with its
category, plus the DiscoverCasa additions (marked **(DC)**, mostly in `design/10-discovercasa.md`). No style sheets or
approved pieces yet: they come with the user's reference images (`_trabalho/referencias/<estilo>/`, local only).

## Read this first: guidelines, not rules
The user, 2026-11-27: «isto será o nosso livro de regras do design sendo que eu quero acima de tudo que sejas flexível e
não demasiado rigído com as regras, são mais guidelines do que regras na realidade.» The manual says the same: «Nenhuma
proporção estética ou medida genérica deve ser tratada como lei universal.» So:
- **Only three things are binding** (tag **[OBR]**):
  - **B1** never change the architecture silently (dimensions, openings, walls, stairs, ceiling height) — say it and keep
    the decoration proposal apart from any architectural change;
  - **B2** safety and technical requirements (structure, installations, regulations, makers' instructions) prevail;
  - **B3** honesty: never show as delivered or specified what is only illustrative, never invent data, brands, models,
    dimensions, certifications, prices or a client's tastes.
- **Everything else is a starting point.** Break it when the result is better, and say why in one line. A measure is a
  comfort reference, a proportion is a visual habit, a style list is a tendency.
- **The best interior is not the one that follows the most rules** (manual, «Princípio final»): it understands the space
  and the people, solves the real needs and turns them into an exceptional visual and emotional experience.

## Tags (manual «Como interpretar as regras»)
| Tag | Category | What the agent does |
|---|---|---|
| **[OBR]** | Obrigatória | Comply (B1–B3 only). In a conflict: stop, flag it, propose alternatives. |
| **[TEC]** | Técnica | Construction, material, modelling or digital requirement: follow the spec and validate the result. |
| **[REC]** | Recomendada | Good practice that works most of the time: apply by default, adjust when the context says so. |
| **[CTX]** | Contextual | Depends on the space, client, equipment, style or use: look at the context before deciding. |
| **[EST]** | Estética | Composition and visual language: may be broken on purpose if the result stays coherent. |
**(DC)** = added by us for DiscoverCasa (not in the manual v1.0). A tag on a heading applies to every line under it,
unless a line carries its own; lines with no tag anywhere are explanation, templates or checklists.

## Conflict hierarchy (manual §1.2) — when two guidelines clash, the higher one wins
1. Safety, structure, technical requirements → never hide an incompatibility; ask for technical validation.
2. The real architecture → never alter it silently to fit furniture.
3. Client and function (needs, routines, accessibility, budget) → solve real use first.
4. Concept and aesthetic quality → the strongest solution within 1–3; do not settle for the first functional one.
5. Product and purchase → do not shrink the concept to a catalogue too early; then find the exact product or the best equivalent.
6. Digital representation → optimise without distorting form, scale or look.
Explain the conflict and offer an alternative; never hide a broken [OBR] behind a visual change.

## Map (all in `conhecimento/design/`; read the index, then only the file(s) the task needs)
| File | Manual chapters | What it covers |
|---|---|---|
| `01-fundamentos.md` | Âmbito, 1, 2, 3 | Aim, design principles, identity without rigidity, impact; client briefing; reading the architecture |
| `02-planeamento-medidas.md` | 4, Anexo A | Planning method, circulation, living, dining, rugs, bedrooms, kitchens, bathrooms, curtains/art/pendants; quick table |
| `03-cor-materiais.md` | 5, 7, 11 | 60/30/10, whites, metals, woods, sensory ingredients, forms, focal point; compatibility; durability and authenticity |
| `04-estilos.md` | 6, Anexo B | Style sheets: structure, variations, reference images, "avoid" not "never"; template; **register of our styles** |
| `05-pecas.md` | 8, Anexo C | Anatomy of each piece (sofas, kitchens, beds, chairs, tables, wardrobes, bathroom units); 3D object sheet |
| `06-luz-styling.md` | 9, 10 | Light layers, colour temperature, quality, daylight first, scenes, light in images; styling density, objects, plants, textiles, art, per room |
| `07-realismo-digital.md` | 12, 13 | 3D realism (edges, upholstery, bedding, PBR, grain, contact, controlled imperfection, exposure); three levels for render/VR, web, AR; **our budgets (DC)** |
| `08-apresentacao-produtos.md` | 14, 15 | Impact, sophistication without excess, cameras, storytelling, visual honesty, options; concept first, investment levels, budget, product checks |
| `09-metodo-qualidade.md` | 16, Anexo D | Work sequence, learning log rules, classifying a lesson, checklists before/after the render, principles never to forget |
| `10-discovercasa.md` | (DC) | Our case: the four services, what we deliver vs staging, free sources only, files and tools, the approval loop, open items |
| `11-licoes.md` | (DC) | Lessons from the user's verdicts (format of manual §16.2), classified (§16.3) |
| `12-pecas-aprovadas.md` | (DC) | Catalogue of approved pieces, each with its approved close-up render and reference |
| `estilos/<id>.md` | (DC) | One style sheet per style (template in `04-estilos.md`), written from the user's references |

## Writing in the book
- A guideline goes into its topic file, tagged, as one short line: `- [TAG] <guideline> — <source: manual §x | user
  YYYY-MM-DD «quote» | lesson Ln>` (the manual's own text needs no source: the section heading says it).
- A user verdict is first a **lesson** (`11-licoes.md`), classified as in manual §16.3: execution error (fix the model,
  no new guideline) · client preference (that project only) · recurring principle (becomes a guideline after it holds in
  several contexts) · technical requirement (with its source). Never turn one case into a universal rule.
- An approved piece goes to `12-pecas-aprovadas.md`; a style the user approves gets status «aprovada» in its sheet.
- Keep superseded guidelines visible, marked `(superseded YYYY-MM-DD: …)`. Bump the version here with one line per change.
- English with the company's Portuguese terms; quote the user in Portuguese as written. The repo is public: no client
  names, addresses or photos; reference images stay in `_trabalho/referencias/` (copyright), described in words here.
