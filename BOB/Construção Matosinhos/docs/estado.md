# Status — Construção Matosinhos

The user's words: `conhecimento/registo-conversas-2026-3.md` (entries 2026-11-20 evening); drawing facts:
`docs/desenhos.md`. Drawings stay on the PC, never in Git.

## ▶ Where we stopped (2026-11-20)
- Client page in progress. Claude kept the hub's 3D page (obra Matosinhos, «Habitação bifamiliar · Guifões — modelo 3D»,
  doc 112, made outside this repo, rev7) whole and added Cycles images, a 360° tour, a table of floors and areas and a
  materials list. The 3D geometry for the renders was exported from that page (local `_trabalho/matosinhos/`, never in Git).
- Renders running overnight on the office PC (user 2026-11-20: «faças os renders deste novo projeto no pc da empresa»;
  timings and finals in `conhecimento/posto-render.md`).

## Current page: doc 120 (uploaded 2026-11-21 ~16:15, user asked to be told: «quando deres upload avisa-me por favor»)
- Final page «Habitação bifamiliar · Guifões», hub → Páginas (project 'paginas'), obra Matosinhos. Doc 119 was renamed
  «Habitação bifamiliar · Guifões (versão de 21/11, 1.ª)» and is the earlier version (the «doc 119» mentions below describe it).
- Fixed before upload (Piso 1 bedroom): wardrobe faced the wall (now faces the room); floor was the garage concrete (now a timber
  floor over the slab, also in the nook by the I.S. door).

## Delivered 2026-11-21 (~01:40) — first version, doc 119
- Client page in the hub, obra Matosinhos, doc 119 «Habitação bifamiliar · Guifões — imagens, 3D e visita 360°» (6,9 MB).
  Keeps the hub page's 3D whole (doc 112 stays there too) and adds 7 Cycles images (rua, entradas, aérea, sala A, cozinha A,
  quarto principal A, sala B), a 360° tour with 6 points (sala A, quarto A, varanda A, sala B, quarto B, jardim A), floors
  and areas, materials, in PT/EN.
- Renders on the office PC (GTX 1050 Ti): images 1800×1125 at 96 samples (~1.5–4 min each), panoramas 3072×1536 at 64
  (~7–13 min each). Dropped as weak: an aerial from the west (mostly neighbours' roofs) and the fração B garden (blank wall).
- Interiors (user 2026-11-20): kitchen of fração A as on the hub page; the rest from the architect's plans; modern minimalist
  furniture — rule in `conhecimento/discovercasa.md` (client page, «Interiors when a 3D page already exists»).
- Known: the dining chairs read a bit blocky (solid oak seat and back). (superseded 2026-11-21: rebuilt slimmer, see Round 2)

## Round 2 (2026-11-21; log: `registo-conversas-2026-3.md`, entries "morning" and "about 12:50")
Supersedes the doc-119 layout above («keeps the hub page's 3D whole … adds» a separate viewer): (superseded 2026-11-21, see registo).
- **One interactive 3D at our quality** (user: «quando digo o 3D digo mesmo o 3D interativo»): the hub page's 3D with all its
  controls (Pisos, Sol with hour and 4 dates, Paredes inteiras/em corte, Portas e janelas, Estores, Eletricidade, Envolvente,
  Ecrã inteiro, views Geral/Da rua/Tardoz/De cima/Pessoa/Caixilharias/Rodar, Níveis) but on our Blender-baked model with real
  materials. No separate low-quality «modelo técnico» (removed). The 360° tour is a mode inside this 3D (Modo Explorar | Visita 360°),
  as on Ribamar. Hub static parts exported without moving parts (doors, windows, gates, garage doors), baked in Blender; a
  «camada» (ES module) draws only what moves plus shutters, electrical symbols and neighbours (scripts local in `_trabalho/matosinhos`).
  Baked light = hub sun 21 Sep 10:00; moving the sun switches to live sun and shadows.
- **Ripado modelled real** (user: «devem ser reais e em concordância com a área que ocupam»): Tremolo boards cover exactly each zone
  (pillars, strips over garages and entrances, over fração B's corner window; rest ETICS, decision 2026-11-20). Built as cladding
  boxes **70 mm proud** of the wall face (boards on battens) with a metal drip flashing under the horizontal strips.
  **MODELLING ASSUMPTION, not a user decision** — to confirm with the method / the user.
- **Dining chairs slimmer** (user: «podes refazer as cadeiras mai finas»): 8 mm tube legs and rails, 15 mm seat, curved backrest. Closes "Known: chairs blocky".
- **Final page for the client** (user: «quero uma página final para apresentar ao cliente») delivered in the hub, obra Matosinhos.
- Standing rule from this: `conhecimento/discovercasa.md` (client page standard).
- **Corrections 2026-11-21 (about 13:15):** «eu errei, o painel sandwich é com a cor imitação telha» — roof panel in the
  tile-imitation colour, company Munditelha RAL 8004 (screen #8F4E35), on the hidden flat roof behind the parapet; supersedes the
  grey shown in the page (decision 3 above stays «painel sandwich»; the colour is the company's, grey was Sobral only, see
  `sistema-construtivo.md:611`). «as portas devem ter a mesma cor e textura do ripado usado nos detalhes» — entrance doors
  (frações A and B, Piso 1) = Tremolo ripado look (vertical boards, Marron, varnished). Garage doors: «Não, só as portas» —
  stay sectional, dark grey (closes the earlier question wood vs grey: grey).
- **Cladding depth corrected 70 → 77 mm** (counter-battens 20 + battens 35 + Tremolo ~22, `sistema-construtivo.md`); the drip
  flashing under the horizontal strips stays a MODELLING ASSUMPTION. (The 70 mm above is superseded.)
- **Fração A's four bedrooms (user 2026-11-21 ~13:40, «Closet e Arrumos 17 m²»):** Quarto 16,40 and Quarto 10,80 (Piso 2), the
  14,00 m² «Closet» (Piso 2) and the 17,00 m² «Arrumos» (Piso 1, next to the 2,10 m² I.S., own glazed door to the street and a
  door to the garage). On the client page both are named «Quarto» (plans, areas table) and furnished as bedrooms: the Closet
  already had the double bed on the plan; the Piso 1 room got a double bed against the south wall between its sockets, a 1,8 m
  wardrobe on the garage wall, a downlight. The licensing drawings keep their own names. CLOSED.
- Pending (still open): none.

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
  with fração A = T4, which rooms are the four bedrooms — ANSWERED 2026-11-21: Quarto 16,40, Quarto 10,80, Closet 14,00 and
  Arrumos 17,00 (see Round 2).
