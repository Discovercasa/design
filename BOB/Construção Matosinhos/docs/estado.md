# Status — Construção Matosinhos

The user's words: `conhecimento/registo-conversas-2026-3.md` (entries 2026-11-20 evening); drawing facts:
`docs/desenhos.md`. Drawings stay on the PC, never in Git.

## ▶ Where we stopped (2026-11-20)
- Client page in progress. Claude kept the hub's 3D page (obra Matosinhos, «Habitação bifamiliar · Guifões — modelo 3D»,
  doc 112, made outside this repo, rev7) whole and added Cycles images, a 360° tour, a table of floors and areas and a
  materials list. The 3D geometry for the renders was exported from that page (local `_trabalho/matosinhos/`, never in Git).
- Renders running overnight on the office PC (user 2026-11-20: «faças os renders deste novo projeto no pc da empresa»;
  timings and finals in `conhecimento/posto-render.md`).

## Current page: doc 121 (uploaded 2026-11-24 ~14:30, without the approval preview: user 24/11 «prossehue entao com tudo e publica»)
- «Habitação bifamiliar · Guifões», hub → Páginas, obra Matosinhos: rounds 3, 4 and 5 (below) in one upload; 24-point tour;
  images rua, entradas, aérea, sala A (24/11) and cozinha A (23/11, nothing that changed shows in it). Doc 120 renamed
  «… (versão de 21/11, 2.ª)». Hub Log entry 118.
- The page embeds the GLB gzipped (base64, decompressed in the browser with DecompressionStream): 38,2 MB, under the
  bucket's 50 MiB file limit (it was 58,7 MB uncompressed).
- Render speed: the office PC (GTX 1050 Ti, 4 GB) ran out of video memory with the furnished, planted model (other apps
  and the preview tabs hold VRAM): sala A took 4 h (was 8–30 min), panoramas 11 min–2,7 h. Close WebGL previews before a
  batch; heavy batches belong on the home render station (RTX 2060, `conhecimento/posto-render.md`).
- Still rendering (same batch): cozinha A redone, sala B and quarto principal A (new views) → a page update when done.

## Earlier page: doc 120 (uploaded 2026-11-21 ~16:15, user asked to be told: «quando deres upload avisa-me por favor»)
- Final page «Habitação bifamiliar · Guifões», hub → Páginas (project 'paginas'), obra Matosinhos. Doc 119 was renamed
  «Habitação bifamiliar · Guifões (versão de 21/11, 1.ª)» and is the earlier version (the «doc 119» mentions below describe it).
- Fixed before upload (Piso 1 bedroom): wardrobe faced the wall (now faces the room); floor was the garage concrete (now a timber
  floor over the slab, also in the nook by the I.S. door).

## Round 3 (2026-11-21, evening; log: `registo-conversas-2026-3.md`, entries «about 16:40», «shortly after 16:40», «evening»)
User's defect list on doc 120's 3D («dá fix a tudo»), all fixed in the export / model:
- **Black stains:** the hub's 3D put a 2 cm black backing box behind each ripado; it stuck out of our 77 mm Tremolo cladding.
  Left out of the export.
- **Entrance doors** (single doors next to the garages): used the hub's own slat texture; now our ripado material (same colour
  and texture as the ripado details, as decided 2026-11-21 13:15).
- **Balcony soffits** were single faces (fração B's balcony had no cover above): now boards with thickness; fração B's balcony
  has a cover slab. (The user also said the balcony ripado was «completamente fora do sítio»: addressed by this rebuild of the
  balcony soffit/cover; to confirm visually on the new render.)
- **Roof parapet invisible from inside:** inner faces were inverted in the export; orientation fixed in the exporter.
- **Behind fração B's rear bedrooms:** stone and grass replaced by timber deck. (extended, see «Found and done since» below)
- **Dividing wall between the two rear gardens:** was 2.4–3.7 m tall and stepped; now one wall 1.65 m above the garden
  (top ≈ 51.70), as on the rear elevation (sheet 08).
- **Walls:** L corners were open (notches) and the 15 mm plasterboard and skirting ran into the perpendicular walls (black
  corners in the baked light). Now L corners closed; plasterboard and skirting stop at the face of the wall they meet.
- **Furniture** 2–4 cm inside walls moved out. Camera points are now chosen automatically at the clearest spot of each room
  (the old living-room point of fração A was inside the sofa).
- **360° tour: 24 points** (supersedes the 6 points of doc 119): fração A: sala, cozinha, quartos 1–4, WCs 1–3, varanda,
  garagem, arrumos, entrada; fração B: sala, cozinha, quartos 1–2, circulação, WC, varanda, entrada, garagem; plus one view of
  each house from its back garden. Links follow the doors and the stairs. Standing rule: `conhecimento/discovercasa.md`.
- **Light baked per storey** (separate lightmaps per floor) for sharper interiors. **Cut mode** now also cuts glass.
- **VR project:** user 2026-11-21: the team's VR project (SketchUp/GLB/panoramas, kept in the company's VR folder, not in Git)
  is the same house; our version follows the licensing drawings (DWFx rev 3), which have some plan changes against it.
  Where the two differ, the licensing drawings rule.
- **Status / pending:** (superseded 2026-11-21 evening, see registo «about 19:00» and below) overnight render running (bake,
  7 images, 24 panoramas); the page will be uploaded as a new version in
  the hub's Páginas (doc 120 becomes the «2.ª» version of 21/11). The user is to be told at upload (standing request).
  Pending: check the new render against the defect list (balcony ripado, dividing wall, corners).

### Found and done since round 3 was filed (2026-11-21, evening)
- **Deck (3 zones):** the licensing plan of Piso 2 draws three deck zones at 50,00 (striped hatch) that together make the
  «deck 30,00 m²» of the area table: (1) behind fração B's bedrooms, from their back wall to the line of fração A's back wall
  (about 6,1 × 1,4 m); (2) by fração B's side door, from the wall to the boundary wall (about 3,5 × 3,2 m); (3) fração A's
  terrace by the slanted wall of the living room (triangle, about 10 m²). The 3D had stone and grass in all three; all three
  are timber deck now. The earlier «T_claro → deck» change was a mistake (that material is a light strip by the gates): back
  to stone slabs. Fração A's terrace was stone slabs in the hub's 3D; made deck because the plan hatches it like the other
  two. **Pending: the user to confirm** (question asked).
- **Hub «Tardoz» camera** sat inside the neighbouring building: moved over the rear road.
- **Web 3D light:** baked per storey and now denoised (OIDN, compositor Denoise node) instead of blurred: blotches on the
  room walls gone. «Pessoa» mode opens up indoors (exposure × 1,6). Piso 1 cut: earth behind the garages in an earth colour
  (was black); fração A's terrace deck hides with Piso 2.
- **Lamps:** every Piso 2 downlight and pendant hung 65 cm under the Piso 2 floor (ceiling height given relative where the tool
  expects absolute): Piso 2 bathrooms dark, lamps showed as discs under the Piso 1 ceilings. Fixed. Every toured room without
  a downlight got lights (60 W bathrooms and store room, 40 W garages, 24 W elsewhere): windowless rooms had come out black in
  the 360° renders.
- **Black line across fração A's Piso 1 bedroom ceiling:** fração A's terrace slab overlapped the house slab by 2,4 cm in the
  same plane (under the slanted wall): overlap removed. Bottoms of the Piso 2 outer walls sat in the plane of the slab
  underside: lifted 6 mm (removed black patches on the entrance ceiling).
- **Entrances:** the two entrances run 0,65 m in front of the garages past the Piso 1 slab: grass showed through the floor;
  floor now carries on. Fração A's Piso 1 I.S., store room and both entrances (up to the stairs' landings) get the house's
  timber floor like the Piso 1 bedroom (were bare concrete); the garages stay concrete.
- **Fração A garden 360° point** moved clear of the trees.
- **Status (2026-11-21 evening):** the 3D was shown to the user (8 captures) and the 24 panoramas (two contact sheets);
  awaiting approval. The final page is built after the last web bake; upload ONLY after approval (user, about 19:00 and a few
  minutes later; rule in `conhecimento/discovercasa.md`).

## Round 4 (2026-11-22, midday; log: `registo-conversas-2026-3.md`, entry «around midday»)
User's message with the circled faulty zones (kitchen A plinth band, door-frame corners in the bathrooms, stair foot at the
entrances, black on the boundary wall / gate / beside the entrance doors / under the balconies, timber band over fração B's big window).
- **Floors (user decision for this house; also a sensible default):** «o chão apenas da garagem é de microcimento todas as outra
  zonas usam o pavimento comum das outras divisões» — **only the garage floor is microcement; every other room uses the same
  floor as the other rooms (the common timber floor)**, including the Piso 1 entrances, the Piso 1 I.S., the store room and the
  Piso 1 bedroom. Supersedes «the garages stay concrete» (Found and done since round 3, Entrances) (superseded 2026-11-22, see registo).
- **Ripado over a window (detail):** the timber cladding *replaces* the ETICS render in that zone, flush with the render and across
  the full width of the facade (corner to corner); it must not look like a board laid over the render and projecting. Fração B's
  band is now x 10,75 → 15,20 (the whole front of the volume), at the hub detail's height (52,18 → 52,75), only 3 mm proud.
  Supersedes the 77 mm-proud cladding boxes for this band (Round 2) (superseded 2026-11-22, see registo).
- **Root causes of the black zones, fixed:** (1) door/window frames: uprights and head/sill overlapped at the corners in one
  plane → black squares at the door tops; uprights now stop between head and sill. (2) Round-3 wall-corner closing extended a wall
  exactly to the next wall's face (two faces in one plane) → black patches at junctions; now 2 mm short. (3) A general check runs on
  the whole exported geometry: any two same-facing overlapping coplanar faces (slab edges behind outer walls, site walls built of
  overlapping segments, frames on walls…) are layered 1,5 mm apart; afterwards no overlapping faces remain (checked). (4) Kitchen
  plinths were in the near-black worktop colour: now the units' light colour. (5) Web 3D: frosted side lights of the entrance
  doors showed the dark hall (black strips) → pale milky pane; bathroom mirrors (black) → pale glass tone; light outside (site walls,
  gates, ground by the house) baked at 4× resolution. (6) Grass came up through the entrances' floor in the 360° renders → no grass
  under that floor.
- **Status:** full re-render running (web 3D bake, 24 panoramas, 7 images, about 8 h); preview for the user's approval before
  uploading (standing rule). The earlier «waiting for approval» preview is superseded by this round.

## Round 5 (2026-11-23, morning; log: `registo-conversas-2026-3.md`, entry «morning» of 23/11)
User's message with 3 screenshots of the 3D street view; meta-point: these are errors a **logical** review of the 3D should
catch before showing it («se tu analisares o 3D de um ponto de vista lógico tu não deverias cometer»), so the model is reviewed
logically, not only visually, before every preview. «Dá fix neles e noutros que encontres.»
- **Fração B ripado band (screenshot 1):** the band must be **flush with the exterior render/ETICS face** (same thickness plane,
  not recessed) and only **as wide as the facade above the window (x 10,80 → 15,20 in our plan frame)**, not running out over
  the balcony. Refines Round 4's «x 10,75 → 15,20 … 3 mm proud» (10,75 superseded 2026-11-23, see registo).
- **Balcony furniture (screenshot 2):** the left balcony (fração A) chair passed through the railing, and it was an indoor chair.
  Balcony/terrace furniture must be **outdoor furniture** (we now use black-metal bistro sets); nothing may pass through a
  railing or wall.
- **Pier/pillar (screenshot 3):** the ripado cladding of the pier did not reach the ground; it must go **down to the ground**
  (also its side return).
- **Our fixes:** `forro()` puts the ripado face 3 mm proud of the render face (flush to the eye) and its back 74 mm into the wall
  (replacing the ETICS; was a 77 mm-proud box); pier cladding from ground level (zt − 0,02) to 2,90; a collision check
  (`_colisoes` in the local `gerar_casa.py`) between furniture and railings/walls runs before every render.
- **B's front in one plane (found in the close-up check, 23/11):** the hub drew the volume's walls at y −5,20 (x 10,755 →
  15,205) but its roof slab and parapet 5 cm proud (−5,25, x 10,80 → 15,20). A band flush with the parapet stood 5 cm proud of
  the walls beside the window, so the walls beside and under the window get render out to −5,25 (the RAL 7016 shutter guides
  at 11,03 and 14,915 stay in the reveal) and the band runs the walls' full width, 10,755 → 15,205 (supersedes [10,80 → 15,20]).
- **Black patches from our own boxes (23/11):** box faces lying in the plane of a hub face (the B pier's ends, the band's top
  corner on the roof slab's side, the lintel bands' undersides, the pier's side return on its front) rendered black. Every
  box face in a coplanar overlap now moves 2 mm outwards automatically (`_caixas_sem_coplanares` in the local `gerar_casa.py`,
  after `_sem_sobrepostas` for the hub's own faces). Garden tree trunks: 16 sides, smooth (they read as posts close up).
- **Publishing without the preview (user 2026-11-24 ~01:50):** «prossehue entao com tudo e publica» — the user authorised
  publishing round 5 in the hub when the batch is done, without the approval preview, for this version only; the standing
  preview rule stays for later versions (see registo-2026-3, 24/11).
- **Status:** (superseded 2026-11-24, see «Current page: doc 121») final batch running (web model final_web8, the 6 panoramas
  that see the balconies, the 7 images); page not yet re-uploaded.

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
