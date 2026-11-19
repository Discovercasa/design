# Status — Construção Ribamar

House-specific state only. Two-storey house: Piso -1 (cave, concrete — not in the timber modules), Piso 0 and Piso 1
in DiscoverCasa timber modules. The user's words: `conhecimento/registo-conversas-2026-3.md` (entries 2026-11-11 …
2026-11-19 naming Ribamar); drawing facts: `docs/desenhos.md`. Drawings stay on the PC, never in Git.

## ▶ Where we stopped (2026-11-19) — start here
- **Delivered: Listagem de material from the real module sheets** — hub › gerador › Documentos adicionais › «Ribamar» ›
  pasta «Ribamar Listagem de material» (documents 113 PDF, 114 CSV; hub Log 102). Made by
  `ferramentas/documentos/listagem_modulos.py` with `modelos/listagem/config.json` (assumptions below).
- **Waiting for the user**: confirm that "Casa CL" = Ribamar; the open questions below (asked 2026-11-19).
- **Not asked yet**: the per-project questions (`conhecimento/perguntas-por-obra.md`) — the Listagem used the defaults.
  Ask them in one message, skipping what the drawings already answer; also the stage of the obra (Ribamar is an obra
  followed for social content, `conhecimento/discovercasa.md` "Social media").

## "Casa CL" = Ribamar's modules (found 2026-11-19 — ours, to confirm)
- The 4 module sheets of the hub's «Ribamar Módulos» are byte-identical to the 4 PDFs the user sent on 2026-09-30 ("it is
  a different house" — i.e. not Sobral), filed as "Casa CL" and cited as "Casa CL" in the rulebook and in
  `sistema-construtivo.md`; their plans match Ribamar's architecture (`desenhos.md`). User 2026-11-19: "tens os módulos
  direitinhos de como foram feitos para ribamar" → "Casa CL" = Ribamar's modules as built, on a template title block.
- The company draft's foundation materials list also says "Copiado de Ribamar"
  (`conhecimento/fontes/execucao-tecnica-obra_2026-09-24.md`).
- So Ribamar is the house behind two company references: its project-specific features (below) are not company
  standard just because "Casa CL" is cited as a company document.

## Project facts (architecture notes: they fix the geometry; DiscoverCasa decides the build)
- Pé direito 2,8 (Piso 0), 2,5 (Piso 1) — section B. Module sheets «piso 1» = Piso 0, «piso 2» = Piso 1.
- Roof: 5-ondas sandwich panel 80 mm, **RAL 8017**; Piso 1 two slopes at 7 % behind parapets; a lower roof over the strip
  of Piso 0 not under Piso 1 (3,12 × 7,53, 7 %, parapet 0,45 drawn).
- Caixilharia aluminium lacado RAL 7016, vidro duplo incolor (= the company standard, PO Q12).
- Façade: Tremolo Douglas marron boards (finish A); ARQ.11 also details a capoto (ETICS) façade — which façades: unknown.
- The client page (Builder › Páginas, obra «Ribamar») shows the same finishes (roof RAL 8017, rufos RAL 7016).
- Areas: implantação 109,31 m² (Piso 0 module outline); construção 191,97 m² (Piso 0 + Piso 1 closed 82,66); varandas
  13,9 m² (Listagem, 2026-11-19). The client page's table, from the architecture: 183,01 m² interior, 43,97 m² deck and
  balconies (2026-11-11).

## Differences from the company standard (this house only — check each with the user)
- Roof colour RAL 8017; the company's hidden 5-ondas panel is RAL 8004 (`metodo/06-cobertura-oculta.md` §7 Covering).
  Precedent: a colour named in a house's project is kept for that house (Sobral's grey, `perguntas-por-obra.md` Q15).
- Piso 1 exterior modules reach the parapet only on the two gutter sides (3,52); front 2,97 and back 2,94 do not — the
  rule is "the exterior modules run in one piece from the base to the parapet top — on every hidden roof"
  (`metodo/02-fundacao-modulos.md`, user 2026-10-21). Same on the lower roof (modules 2,97, parapet 0,45 drawn).
- Mixed façade (Tremolo + capoto) vs "the finish covers the whole house" (`metodo/07-paredes-exterior-interior.md`).
- Interior openings 1,69 × 2,06 vs the standard interior door rough opening 0,87 × 2,03.

## Listagem 2026-11-19 — what was assumed (defaults, `perguntas-por-obra.md`)
- Q18: finish A Tremolo on every façade (the capoto detail not applied). Q20: vinyl on both storeys.
- Q9: ceiling beams 22×7,5 at 1 m (free span < 8 m thanks to the interior walls).
- Q10: floor joists 22×7,5 at 0,598, one piece wall to wall (8,89 m, 19 pieces); barrotes 110×75 at 0,60; OSB 22;
  wool 100 in the heated part only.
- Amarração 110×75 also on the Piso 0 exterior walls under the joists (rule OPEN, metodo §4).
- Q14/Q16: Piso 1 roof two slopes at 7 % (architecture), gutters along the side parapets, 4 downpipes; the lower roof a
  hidden one-slope roof towards its outer façade, 1 gutter, 2 downpipes, remate de topo against the Piso 1 wall.
- Q15: 5-ondas panel 80 mm — the Listagem line does not name a colour (RAL 8017 project / RAL 8004 standard: open).
- Stair opening 3,10 × 1,10 (run from section B; width assumed).
- Q2: no window schedule — 12 exterior openings listed as rough openings.
- Totals: timber 632 pieces, 1 751,6 m, 13,28 m³; façade 218,8 m²; OSB 15 / Pladur 320,1 m²; vinyl 171,9 m²; roof
  panels 111,3 m².

## Open questions
Asked 2026-11-19:
1. "Casa CL" = Ribamar's modules — confirm.
2. Window schedule (mapa de vãos): types and frame sizes.
3. Varandas: exterior floor finish, edge beam over the open side, soffit; the 1,48 m cantilever of varanda 2 over the
   deck (its joists over M009–M011's wide openings) → engineer.
4. Lower roof: its parapet (0,45 in the architecture, not in the 2,97 modules); M132's 2,81 × 2,09 opening down to the
   Piso 1 floor onto it — a terrace or a roof?
5. How the roof edges are closed over the 2,97 front and 2,94 back walls of Piso 1.
6. Which façades get capoto (ARQ.11).
Not asked yet (ours, from the 2026-11-19 check):
7. Roof colour: RAL 8017 (project) or RAL 8004 (company)?
8. Interior openings 1,69 × 2,06: double doors or pocket (correr embutida) doors?
9. How the floor sits on the Piso 0 walls: exterior 2,97, interior 2,80 — by the made-to-measure rule the joists bear at
   ≈ 2,91 on the interior walls, so on the exterior walls they cannot sit on top (2,97 + amarração); hung inside the
   exterior modules on a ring, as the hidden roof? (our arithmetic) — decides the amarração rule and the façade band
   (config `faixa_piso` 0,39 assumes the stack).
10. Piso 1 clear height: 2,5 (architecture) or ≈ 2,64 (interior modules 2,68 + amarração 0,11 − false ceiling 0,148,
    our arithmetic)? The Listagem uses 2,50 for the walls' Pladur.
11. 8,89 m joists in one piece: the longest 22×7,5 stock bought is OPEN (`metodo/08-produtos-limites.md`).
12. Stage of the obra (built? which phase?).
