# Status — Construção Matosinhos

The user's words: `conhecimento/registo-conversas-2026-3.md` (entries 2026-11-20 evening); drawing facts:
`docs/desenhos.md`. Drawings stay on the PC, never in Git.

## ▶ Where we stopped (2026-11-20)
- Client page in progress. Claude kept the hub's 3D page (obra Matosinhos, «Habitação bifamiliar · Guifões — modelo 3D»,
  doc 112, made outside this repo, rev7) whole and added Cycles images, a 360° tour, a table of floors and areas and a
  materials list. The 3D geometry for the renders was exported from that page (local `_trabalho/matosinhos/`, never in Git).
- Renders running overnight on the office PC (user 2026-11-20: «faças os renders deste novo projeto no pc da empresa»;
  timings and finals in `conhecimento/posto-render.md`).

## Delivered 2026-11-21 (~01:40)
- Client page in the hub, obra Matosinhos, doc 119 «Habitação bifamiliar · Guifões — imagens, 3D e visita 360°» (6,9 MB).
  Keeps the hub page's 3D whole (doc 112 stays there too) and adds 7 Cycles images (rua, entradas, aérea, sala A, cozinha A,
  quarto principal A, sala B), a 360° tour with 6 points (sala A, quarto A, varanda A, sala B, quarto B, jardim A), floors
  and areas, materials, in PT/EN.
- Renders on the office PC (GTX 1050 Ti): images 1800×1125 at 96 samples (~1.5–4 min each), panoramas 3072×1536 at 64
  (~7–13 min each). Dropped as weak: an aerial from the west (mostly neighbours' roofs) and the fração B garden (blank wall).
- Interiors (user 2026-11-20): kitchen of fração A as on the hub page; the rest from the architect's plans; modern minimalist
  furniture — rule in `conhecimento/discovercasa.md` (client page, «Interiors when a 3D page already exists»).
- Known: the dining chairs read a bit blocky (solid oak seat and back).

## Requirement (user 2026-11-20)
«mantem as features que estão na página que esta disponivel no hub» — keep: storeys, sun hour/season, walls whole/cut,
doors and windows open/closed, shutters, electrical layout, surroundings on/off, views Geral/Da rua/Tardoz/De cima/Pessoa
(walk mode)/Caixilharias (window tour)/Rodar, levels panel, PT/EN switch, full screen.

## Differences: hub page vs architect's notes
- Hub page: dark window frames (DiscoverCasa standard RAL 7016), sandwich-panel roof behind the parapet, aluminium-looking
  slats; calls the units "T4" and "T2". Architect: white PVC, flat roof with gravel, wooden ripado envernizado.
- The user's file is named "Matosinhos_T3".

## Decision log (user 2026-11-20, late evening; log: `registo-conversas-2026-3.md`)
Answers to the five open points: «1. T4 / 2. RAL 7016 como no HUB / 3. painel sandwich / 4. as que estão com revestimento com
ripado na página levam ripado mas são apenas aqueles detalhes que estão lá, a maioria é etics / 5. sim exatamente».
1. **Typology:** fração A = **T4**; fração B = T2. The hub page's labels were right; the file name "Matosinhos_T3" is not the typology.
2. **Windows:** aluminium **RAL 7016** as on the hub page (not the architect's white PVC).
3. **Roof:** **sandwich panel** (not the architect's gravel flat roof on XPS + waterproofing).
4. **Façade:** **mostly ETICS**; timber ripado only on the details the hub page shows with it (slatted screens at the Piso 1
   entrances, soffits under the balconies, high band at fração B's north end). **Project-specific exception** to «o capoto tem
   que ficar na casa toda» (user 2026-10-28), decided by the user for this house; not a general rule.
5. **Shutters (estores):** on windows only, never on doors (company rule, user 2026-10-27), confirmed.

## Open questions
- None from the first list. Still to verify when modelling: exact extent of the ripado details against the hub page (the answer
  refers to "those details", not listed one by one); which openings are windows vs doors for the estores (rule applied per opening);
  with fração A = T4, check which rooms count as the four bedrooms (Quarto 16,40, "Closet" 14,00, Quarto 10,80, and the Piso 1
  Arrumos with I.S.?) — not asked, do not assume.
