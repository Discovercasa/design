# Status — Construção Sobral

House-specific state only. Company facts learnt here are in `conhecimento/sistema-construtivo.md`; the user's words in
`conhecimento/registo-conversas.md`; issues in `revisao-tecnica.md` (#n); model details in `modelos.md`. Condensed
2026-10-28 (the old "Where we stopped" chain is in the git history).

## ▶ Where we stopped (2026-10-15) — start here when Sobral resumes
- **Paused** since 2026-10-15 ("Para já vamos dar uma pausa no projeto de sobral"); "estará para avançar brevemente"
  (2026-10-20 night — when: not said).
- State of Casa Tipo 1 (`modelos/tipo1/`): DiscoverCasa skeleton and build-up, floor between storeys the DiscoverCasa way
  (joists 22×7,5 at 0,61, 11×7,5 flat at 0,60 centres, OSB 22, 100 mm wool between the joists), no central floor beam,
  ceiling beams 22×7,5 at 1 m, flat upper false ceiling at the tie beam, exposed roof on prumos and purlins; Blender
  validation 0 issues; timber 645 pieces, 9,9 m³.
- Waiting for the user: the roof option A / B ("para ja ainda nao vou tomar essa decisão"); the questions of 2026-10-15
  (a)–(c) below; the foundation base (promised: "base de fundação eu explicarei mais tarde").
- Next, in order: (1) apply the answers to (a)–(c) and rebuild; (2) the perforated angle on the outside corners — model
  and count; (3) Casa Tipo 2 (architecture sheets 20–22 + engineer's PD_Habitacoes F G H I J; levels −2,70 / ±0,00); (4)
  stair, connectors, windows; (5) the roof option when chosen; (6) the warehouse in timber (`armazem.md`) once the uses
  per wing are confirmed. On resuming: run the per-project questions (`conhecimento/perguntas-por-obra.md`) and apply
  the method facts learnt since (Munditelha, beirado range, the module divider, full-height modules on hidden roofs).

## Model history (`modelos.md`)
2026-09-23 Tipo 1 from the engineer's drawings · 2026-09-24 all build-up layers (finish A / B / C; option B shown) ·
2026-09-30 rebuilt with the DiscoverCasa skeleton (110×35 / 75×35 / 110×75), flat upper ceiling at the tie beam, roof on
posts and purlins, ceiling system on both floors · 2026-10-09 the user's answers (bandeiras over the doorway gaps
PI1.10/PI1.11, PI2.03, PI2.06, PI2.07/PI2.08; linings to the ceiling; duct removed; ceiling beams 22×7,5 at 1 m; steel
ceiling metal; doors 0,87 × 2,03); plan comparison with the architecture SMA_012 (`config.json`: PD2.01, the WC 0.6
door, Lavandaria 1,4 m opening with bandeira, quarto 1.5 one room 14,7 m², PE2.08 a window) · 2026-10-13 floor between
storeys (upper floor Z 3,117, +0,139) · 2026-10-15 central floor beam removed; floor joists ≤ 0,615.

## Open questions
- **Roof option** (#22): with 22×7,5 ceiling beams and the deeper floor the roof plane is ≈ +0,35 vs the drawings. A keep
  the 26,4° pitch → ridge panel underside Z 7,398 (drawings 7,048), ridge ≈ +7,35; B keep the ridge → pitch 20,93°. Eaves
  ≈ +5,65 in both → either changes the licensed volume — the architect must agree. Shown as an interactive section
  2026-10-13; postponed 2026-10-15.
- **Asked 2026-10-15, not answered**: (a) the living-room joists (≈ 4,7 m free, x ≈ 3,95 / 4,93 / 5,91) at 0,50 like
  the base framing sheet's porch? (at 0,61: w_inst ≈ L/276 vs L/300 — marginal; engineer, #6); (b) vigas de amarração
  11×7,5 on the ground-floor walls under the floor joists, as in 3_Vigamento? (+0,075; +0,11 with an afinação → roof
  #22, stair #24); (c) the vertical 7,5×3,5 pieces above / below openings in the 110 exterior walls — 7,5×3,5 or 110×35
  (model), and against which face?
- Floor: the wool's height in the joist bay (model: on the ground-floor false ceiling); what closes the joist bays at
  the N/S façades with no rim joist — blocking? (#24); Tipo 2: does the extra floor depth go up or down (the entrance at
  ±0,00 meets the street)?
- Ground floor: the drawings' build-up (XPS 60 + betonilha + microcimento on the massame, finished Z 0,16) vs the
  method's vinyl straight on the base — waits for the foundation base; whether the 2026-10-09 "yes" confirms insulation
  under the slab: unclear. DPC / membrane and treated plates under the bottom plates; the "alcatrão" of the start list
  there? (#1).
- Doorway gaps between modules: modelled with a bandeira (padieira 110×75 + short studs, 110×75 ombreiras) — is that how
  DiscoverCasa closes them? (#5).
- Ceiling products: what the perforated angle does (hanger or corner bead); perfil section (47×17 assumed) and bar
  length; régua model and length; prumo section (110×75 assumed).
- ETICS: XPS or a vapour-open board (#19).
- The roof panel for Sobral: Munditelha (company, 2026-10-22) — thickness not said (model 40 mm, provisional); colour:
  the user's 2026-09-24 "dark grey" is Sobral's own (kept, RAL 7016), while for the configurator he asked for the maker's
  original colour, not grey (2026-10-29, `sistema-construtivo.md` §6) — **confirmed 2026-10-30: "é o ral 8004 … o
  cinzento foi apenas para sobral"** (Sobral's grey stands, a project fact; the house standard is RAL 8004 tile colour); the verge 0,12 vs the 0,20 beirado minimum (`sistema-construtivo.md` §6).
- The licensed projects (REH, acoustic, stability) must follow the DiscoverCasa build-ups; the visible changes (zinc →
  sandwich panel, ridge above +7,00) need the architect (#22, #26). Is there a "memória descritiva e justificativa"
  (timber grades, loads, seismic data)?
- Warehouse: which wing becomes the group room, the gym and the refrigerated store; same footprint and levels?
- `PD_Habitacoes A B C D E K L M N O P (1).dwfx`: the repo holds the 16:08 original (the model's source); Autodesk Design
  Review re-saved the user's copy at 16:33 (157 bytes smaller), kept outside Git — the user's choice.

## Decision log (Sobral; short quotes — full words in the registo)
- 2026-09-23 — The drawings are module fabrication drawings; the foundation fixing is handled separately. Roof plan read
  as true length (section FF' and gable elevations). Blender files saved with the lowest installed Blender ≥ 4.4.
- 2026-09-24 — Build-up layers by the DiscoverCasa standard, not the drawings' OSB 12 (the company is aware of the
  difference). **Exterior finish option B, ETICS / white capoto** ("In this house we will use the option B"); A and C kept
  in the model. Roof modelling (purlins 110×75 ≤ 1,2 m, 40 mm tile-effect panel, RAL 7016) "perfectly fine" for now.
  Ground floor Z 0,16 from the drawings; overhangs 0,25 eaves / 0,12 verges (sections FF' / EE').
- 2026-09-30 — **Same house dimensions with the DiscoverCasa timber** (110×75 at corners and openings, 110×35 exterior,
  75×35 interior); the engineer must re-check (#20). **The upper ceiling is flat at the viga de amarração** ("is has a
  fake roof at the height of the viga de amarração"), hung from the 22×7,5 ceiling beams; roof on prumos and purlins.
- 2026-10-09 — The user's answers on the model (module joints as modelled — "those are the rules"; "they are 22x7,5";
  ceiling beams down the slope — "always follow this logic unless told otherwise"; 1 m apart, prumos and purlins right;
  gables on the tie beam — "its fine like that"; beams on interior walls fine; walls fine for pipes; wool 80 / 60 / 100;
  steel ceiling metal; doors 2,00 × 0,80 → 0,87 × 2,03) — company facts, `sistema-construtivo.md` §2, §4–§6.
- 2026-10-09 — **Upper clear height 2,40 kept**: "keep it but note it" (#21). **"yeah no problem raise the roof"** — the
  extra floor depth goes up (#22). The duct PI2.09 / PI2.10 "will not exist" (#25 closed). The architecture set SMA_012
  is "for now the final version"; two house types (Tipo 1 living downstairs / Tipo 2 bedrooms downstairs). Its
  construction notes are not followed: "vais usar o nosso método construtivo com os nossos materiais e não os que ele
  menciona" (#26). Heights not disputed: "I didnt say it was wrong i just asked to know where you got that".
- 2026-10-09 / 10-13 — Floor between storeys: 11×7,5 flat at 60 cm, "sao medidos em eixo"; wool "fica entre as vigas";
  verga 22×7,5 from ≈ 2,8–3 m (no Tipo 1 opening reaches it).
- 2026-10-15 — Roof option postponed. Living room: "leva o teto falso e o vigamento normal de 22x7,5 e 11x7,5 nada muda"
  → no central beam (removed). Upper walls on the floor OSB ("sim"); no rim joist ("não"). The 7,5×3,5 pieces at
  openings vertical only (the horizontal ones in photo 1 were a site change). Floor joists ≈ 0,61 from the company's base
  framing sheet (replaces our reading "1 m"). **Sobral paused.**
- 2026-10-20, night — "ele já tem informação sobre a construção de sobral que estará para avançar brevemente e são de
  dois pisos as habitações"; "emtermos de paredes nada muda" (does not answer (b) above).
- 2026-10-22 — The exposed-roof panel is Munditelha (Mundiperfil) — the model's 40 mm tile-effect panel is that
  product; beirado range 0,20–0,55 (Tipo 1 0,25 inside it) (max superseded 2026-10-28, see registo: 0,50 — Tipo 1's
  0,25 still inside).
