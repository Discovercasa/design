# Blender model — Torres Vedras

`modelos/casa/`: `config.json` (hand-edited), `planta_paredes.json` (walls and openings from the plan),
`Casa_TorresVedras.blend`, `Casa_TorresVedras_Estrutura.glb`, `Casa_TorresVedras_Completa.glb`,
`quantidades.csv`. Rebuild: `python ferramentas/modelo/construir_casa.py "Construção Torres Vedras/modelos/casa/config.json"`.
Materials list: `docs/materiais.md`.
(2026-10-20, night, configurator phase 1) The model is unchanged: `config.json` "modulos_reais" keeps D2503's modules.
Without it the builder now splits the walls with `ferramentas/modelo/divisor_modulos.py` (TV test in `_trabalho/divisor/`:
27 + 23 modules, as D2503) — `docs/modulos-D2503.md` "Compared with the module divider". (Since the user's answers of
2026-10-20 night — exterior modules up to 3 m: 25 + 23.)

## Version 6.5 — NEEDED: the ceiling beams inside the modules (2026-10-21, not rebuilt yet)
- The user (configurator session, 2026-10-21, registo): the ceiling beams "ficam por dentro e encostadas as da
  estrutura não atravessam ou fazem com que as da estrutura sejas separadas em dois pedaços, não é realista"; at most
  "o entalhe nas vigas … de forma a ficarem do comprimento perfeito" → the lameladas end at the exterior modules'
  inner face, on the amarração ring; no notch in the modules; the studs whole (as D2503 Módulos draws them).
- The builder already does it (per the caller, `ferramentas/modelo/casa_planta.py`; TV run): lameladas 170,49 →
  **166,53 m** (≈ 11 × 8,28 + 7 × 10,78 — our check), notches 36 → **0**, module pieces 702 → **696**.
- **The committed model predates this**: `Casa_TorresVedras.blend`, both `.glb`, `quantidades.csv`, `docs/materiais.md`
  and `documentos/D2503_Modulos.pdf` / `_Cobertura.pdf` / `_Listagem_Material.pdf/.csv` (they show the 36 notches
  "feito em obra" and the lameladas to the outer face) → rebuild, regenerate the documents, update `materiais.md`.
- ⚠ D2503 lists the lameladas 8,50 / 11,00 (the outer depths): read as the ordered length, cut to fit on site — to
  confirm (`docs/estado.md` Open questions); the order lengths / stock in the material list should follow the answer.
  (Answered 2026-10-21, see registo: "Sim normalmente cortamos para "encaixar" no tipo de obra que temos" — cut to fit
  each house; the model's inside length is right; the material list: cut length + purchase (stock) length.)

## Version 6.4 — gutter outlets; production documents generated (2026-10-20)
- **Outlets in the hidden gutters** (user: "um erro que esta presente é nas caleiras nao existem os buracos par
  agua escoar para os tubos de queda"): each downpipe's stub now goes through a hole in the gutter lining on the
  parapet side, at the gutter's low end, into the facade cavity (side outlet, the method's route: no joints in the
  roof void); the stub is hollow and the pipes sit inside the gutter's length (they straddled its ends). TV itself
  had a round outlet in the gutter bottom (site photo `2026-10-19_obra_caleira_forro_saida.webp`) and the pipes
  outside — to confirm which outlet the method uses.
- **Production documents** in the company's D2503 standard, generated from this model by
  `ferramentas/documentos/gerar.py` into `Construção Torres Vedras/documentos/`: `D2503_Modulos.pdf` (6 sheets),
  `D2503_Cobertura.pdf` (4), `D2503_Listagem_Material.pdf` (3 pages) + `.csv`. The module sheets and the cut list
  use the members AS MADE IN THE FACTORY (`membros_fabrico` in the geometry: whole studs, the escadas kept; the
  36 lamelada crossings drawn as notches "feito em obra" — superseded 2026-10-21, see registo: no notches, v6.5). Check: identical to the members drawn in D2503 —
  228 × 11x3,5 / 478 m, 50 × 11x7,5 / 140,5 m, 24 × 7,5x11 / 46 m, 207 × 7,5x3,5 / 376 m (interior studs 1,3 cm
  longer: made to the amarração). D2503's own cut-list table says 220 / 473, 50 / 139, 24 / 46, 199 / 379: its
  table and its drawing differ by 8 pieces in 11x3,5 and 7,5x3,5 (to ask). Panels 30 × 3,94 + 7 × 6,44.
  (2026-10-20, night, see registo: explained to the user — the generator follows D2503's drawing, the 8 pieces are
  D2503's table vs its drawing; which one the factory cut to: not answered. The user's review of the generated Módulos:
  "está absolutamente correto". The earlier figure 225 × 11x3,5 / 477 m (registo 13:43, rulebook §0a) is superseded by
  this check.)

## Version 6.3 — photos of the finished house, remates round every opening (2026-10-20)
- **Photos of the finished house** (`revisao-modelo/2026-10-20_final_1…4`): the pergola starts just east of the
  garage (the garage door is not covered — photo 3) and runs to the east end of the house (photo 2), so `x0` is
  back to the plan's 3,63; ceramic tiles ("É cerâmica"); two downpipes on the pergola: the post in front of the
  wing's west face (photo 4) and the post at the east corner (photo 2: "Um no lado oposto ao que se vê na foto");
  6 posts (3 of the construction photo + 3 in front of the wing). Slope raised to 15 % (assumed: ceramic tiles
  normally want ≥ 30 %, the 3,49 parapet allows ≈ 18 % in front of P03).
- **Remates round every opening** (user: "Todos os vão levam remates a volta da caixilharia de forma as diferentes
  camadas das nossas paredes não ficarem expostas"): outside a folded aluminium RAL 7016 lining of the reveal from
  the frame to the Tremolo face, a return over the clearance and a 3 cm flange on the cladding, and a sill with a
  3 cm drip under the windows (none at floor-level openings); inside a 13 mm lining of the reveal to the interior
  finish (`camadas.py` `caixilharia`, collections 7.5 / 7.6; standard `caixilharia.remates`). Profiles, colours
  and the interior material assumed. 59,7 m of opening perimeter.
- Validation 0 issues; no chapéu overlaps (the build now warns if two chapéus overlap).

## Version 6.2 — chapéu corners, the tiled pergola along the whole house (2026-10-20)
- **Chapéus at the corners** (user's screenshot `revisao-modelo/2026-10-20_v6_3_chapeus_cantos.png`: they "não podem
  deixar o topo destapado" and "não dão overlap uns aos outros senão criaria folgas entre camadas"): at every end
  where a wall stands across (whichever frame runs through), the chapéu runs on to that wall's far edge; the X
  chapéus cover the corner and fold down its end, the Y chapéus stop against them; at a re-entrant corner the outer
  leg stops where the wall across begins (`camadas.py` `chapeus`, `ate_parede`). Checked: 0 overlaps between
  chapéu tops, no uncovered top along the outline. (v6.1 left the wing's SW corner top uncovered and overlapped the
  chapéus there and at the P03 / P14 re-entrant corner, because P01 abuts P14 there instead of running through.)
- **Pergola along the whole south side, tiled, exposed gutter** (user, photo of the finished house): front beam
  from the west to the east finished face (x −0,06 … 17,57) at y −1,93 (plan); beams at 1,40 (plan, origin 3,707)
  over the whole length, falling to the front (10 %, assumed), resting on the front beam and on one ledger per
  facade (P03 and the wing's south face) screwed over the battens; slats 7×3 at 0,15; **tiles** on the slats up to
  the finished faces (`camadas.py` `pergola_cobertura`, collection 8.1); an **exposed gutter** 12×10 under the
  front edge over the whole length and one downpipe down post 4 (x 10,7, as in the photo) (8.2). Posts: 7
  (the 3 of the site photo + both ends + 2 in front of the wing). Built by `casa_planta.py` from the facades of the
  finished outline (`desloca`, `dentro_x`). Sections, slope, tile type, gutter section: assumed.
- **Clearance 2,5 cm per side** between the rough opening and the frame (the company default, user 2026-10-20);
  the despensa door M23 fills its 0,94 opening like the entrance.
- Downpipes of the hidden gutters inside the cladding confirmed as the right way ("a forma como modelaste no
  blender por dentro do revestimento é a forma correta"; TV itself was done differently). Gutter walls lined up to
  the top, meeting the chapéus — as modelled.

## Version 6.1 — the user's answers of 2026-10-19 evening (built 2026-10-20)
- **Interior modules made to the amarração** ("Nós fazemos os módulos de forma a ficarem à medida certa das vigas
  amarração"): interior module 2,543 + amarração 11×7,5 = 2,653, the lameladas' underside — no packing, the
  interior amarração at the level of the exterior ring (2,543–2,653). The D2503 modules are drawn 2,53 (studs 2,46):
  `casa_planta.py` raises their top plate 1,3 cm and lengthens the studs reaching it (config
  `modulos_reais.interior_a_medida_da_amarracao`); the piece on top is now "Viga de amarração interior" 110×75,
  0,11 high (v5.1–v6 had a 0,123 "afinação").
- **Roof side of the gable parapets** (user's screenshot `revisao-modelo/2026-10-19_v6_2_canto_forro_platibanda.png`:
  "o forro é suposto ir até ao final do painel sanduíche"): the cladding now runs over the gutter to the end of
  the sandwich panels (it stopped at the gutter madre, 0,10 short); the gutter's end cap lines the parapet up to
  the top only between the gutter wall and the panel ends (`camadas.py`).
- **Entrance door M5** fills its 1,04 opening ("uma porta maior e mais robusta que cabe naquele espaço"); the
  table's 0,90 is kept in the config as `largura_tabela`. The other items stay as modelled ("está ótimo como
  fizeste"), the basculantes 0,73 in their 0,75 openings.
- **Pergola as built** (site photo `revisao-modelo/2026-10-19_obra_pergola_vigas_encosto.webp`): the glulam beams
  rest on the front beam and on a ledger screwed to the facade over the battens (in the Tremolo plane, under the
  beams); the Tremolo is cut round the ledger and the beam ends. Glulam with autoclave treatment (user); sections
  still assumed ("as medidas não sei ao certo mas parecem estar ótimas"), height confirmed.
- Validation 0 issues.

## Version 6 — windows and doors from the approved table, provisional pergola (2026-10-19)
- **Caixilharia** (`camadas.py` `caixilharia()`, collection 7; defaults in `sistema_construtivo.json`
  "caixilharia", items in `config.json` camadas.caixilharia.itens): the user's table "PROJETO APROVADO"
  (`revisao-modelo/2026-10-19_projeto_aprovado_vaos.png`), 11 items, 31,06 m², aluminium RAL 7016 with thermal
  break. Each item names its D2503 module (M24, M23, M20, M18, M12, M14, M9, M6, M5, M3, M1); the element (maker's
  size) is centred in the module's rough opening at the outer side of the frame; where the table has "Estore
  exterior automático" (6 items) a roller-shutter box fills the rough opening above the element. Types: fixo,
  basculante, correr (2 leaves on 2 tracks), porta (painel liso), seccionado (garage door, 5 sections). Profiles and
  depths are assumed (visual model): frame 6 cm face × 7 cm deep, leaf 5 cm, glass 24 mm, clearance 1 cm.
- **Pergola** (`casa_planta.py`, collection 1.10, `config.json` "pergola"), **provisional**: in front of P03,
  x 3,63 → the wing's finished face (10,71), y −2,01 → P03's finished face (2,43). Positions from the architecture
  plan (sheet 1, magenta dashed: 6 beams 0,16 wide at 1,40 centres, front beam at y −1,93); from the site photo
  (`revisao-modelo/2026-10-19_obra_pergola_foto.webp`): 3 posts at the front, against the facade, slats on top.
  Assumed: posts 16×16, front beam 16×16 on the posts (top 2,45), ledger 7,5×16 on the facade, beams 16×16 on the
  front beam (2,45–2,61), slats 7×3 at 0,15 (top 2,64) — 41 pieces, 1,56 m³. To confirm with the user.
- Validation 0 issues (`validar.py` now skips the footprint check for 1.10; `construir_casa.py` prints
  "VALIDATE FAILED" with the log if the validation crashes instead of printing nothing).

## Version 5.1 — interior walls bear the lameladas (2026-10-19)
Per the caller, after the user's "Por norma as vigas de apoio ao teto apoiam-se nas paredes dos módulos interiores
também" (registo 2026-10-19): with lameladas the interior afinação now runs from the module top (2,53) to the
lameladas' underside (2,653), 0,123 high (`casa_planta.py`: `topo_af = z_teto if lam`) — the 13 mm gap of v5 is gone.
How the 0,123 is really filled (afinação 110 + packing?) is not drawn in D2503 — assumed (`revisao-tecnica.md` #6).
(Superseded 2026-10-19, 18:12, see registo: nothing fills it — the interior modules are made to the amarração, 2,543 +
0,11; v6.1. The section `revisao-modelo/2026-10-19_P6_afinacao_lameladas.svg` shows the old 1,3 cm gap.)

## Version 5 — the real modules, from D2503 Módulos (2026-10-16)
The walls are now the company's own modules (`docs/modulos-D2503.md`): `ferramentas/modelo/modulos_dc.py`
reads `desenhos/250828_D2503_Modulos.dwfx` into `modelos/casa/modulos_D2503.json` (27 exterior modules 3,50
high, 23 interior 2,53, every member and opening as drawn) and `casa_planta.py` uses it (`config.json`
"modulos_reais"): each module goes to the plan wall on its line; the wall's frame, ends, joints, members and
openings are the drawing's — no placement, corner, joint or framing rule of the builder. The exterior modules
are one piece to 3,50; above the lameladas a "ghost" parapet panel per module (`fantasma`) carries only the
layers (chapéu, roof-side cladding, gutter walls). Lamelada pockets cut in the X walls' studs (to confirm).
Openings as built (sliding doors 2,00 × 2,40, garage 3,00 × 2,20 …). Battens (user 2026-10-16, site photo):
horizontal from the bottom every 0,35, round every opening (jambs + head, + sill when it does not reach the
floor), a vertical batten at both ends of every facade face (the corners, on both faces), stopping at the
downpipes. Cut lists match D2503 within 1,3 %; validation 0 issues; re-entrant corner closed (P14 stops
0,035 short of P03's inner face: its cladding and chapéu run on to the lined face).

## Version 4 — as built, from DiscoverCasa's roof drawing D2503 (2026-10-16)
Everything about the roof, the heights and the wall line now follows `docs/cobertura-D2503.md` (the user's
"documento exato sobre a cobertura"; his earlier sketch of one slope per part of the L was a mistake and was
dropped before delivery). Config: `paredes.exterior = face_exterior`, `cobertura.estrutura = lameladas`,
`niveis.teto_estrutura 2,653`, `pe_direito 2,50`, `platibanda.topo 3,4915`, `caleiras` (outlets, falls).
- Walls: the modules' outer face on the foundation line (architect's outer faces, 17,5 × 11), cladding
  outside it — rooms ≈ 11 cm wider each side than in version 3. Exterior modules framed to the amarração
  (lintels there), the studs running on past the lameladas (pockets cut in the X walls — superseded 2026-10-21, see
  registo: no pockets, the lameladas end at the inner face, v6.5) into the parapet
  module above with no plates in between, one top plate at Z 3,4915 on every wall.
- Amarração 11×7,5 all round on the inner face, Z 2,543–2,653; lameladas 20×10 (glulam) N–S, 18 in 19 equal
  bays of 0,915 between the end walls' axes, wall to wall through the frames (11 × 8,50, 7 × 11,00), Z 2,653–2,853
  ("through the frames" superseded 2026-10-21, see registo: inner face to inner face, 8,28 / 10,78 — v6.5).
- Ceiling at 2,50 hung 0,15 under the lameladas (réguas, `tetos.suspensao.folga` 0,1185); interior OSB up to
  the amarração (2,543), Pladur to the ceiling.
- Roof: ridge along X at Y 6,749 (middle of the main block); two slopes at 6 %: north to P11; south to P03
  for x < 10,888 and over the wing down to P01 for x > 10,888. Madres 11×7,5 standing on prumos 110×75 on every
  lamelada, at Y 0,458 / 1,707 (wing) / 2,955 / 4,220 / 5,486 / ridge pair 6,699 + 6,799 / 8,011 / 9,276 / 10,540;
  undersides 0 / 0,075 / 0,15 / 0,226 / 0,302 / 0,375 above the lameladas (D2503: 0 / 0,08 / 0,15 / 0,23 / 0,30
  / 0,38); pieces ≤ 3,66 jointed on lameladas (wing 2,90 + 3,61 as drawn; main 3,61 + 3 × 3,66 + 2,69 —
  D2503 orders them 3,60 / 3,66 / 3,66 / 2,75 / 3,60).
- Gutters 0,31 wide between the parapet and the gutter madre, on packing (calços) on each lamelada: under the
  channel the fall (north 0 → 0,17 → 0 with outlets at both ends; P03 0 → 0,22, outlet west; P01 0,06 → 0,
  outlet east), under the madre 0,15 (main block) / none (wing). Lining: bottom, parapet side up to the top
  under the chapéu, madre side + 0,10 flange over the madre, end caps up the gable parapets; at the free end of
  P03 (over the wing roof) it turns round the end of the gable cladding. 4 downpipes at the outlets, in the
  facade's batten cavity, ending 5 cm above the base; the battens stop at them.
- Panels 5 ondas 80 mm laid from the east end: 30 × 3,94 (incl. the west strip and the part of the L-cut
  panel) + 7 × 6,44 — D2503: 28–29 × 3,94 + 3,94 × 0,25 + 7 × 6,44. Panel top at the ridge 3,42, parapet
  3,4915. Ridge cap 17,1 m (D2503: 18 cumeeiras).
- Parapets' roof side: the gutter walls (P01, P03, P11) are lined by the gutter, no cladding (D2503); the gable
  parapets (P12, P14, P18) keep OSB 15 + Traspir + ripado + Tremolo between the gutters (user 2026-10-15) — to
  confirm. Chapéu flat (D2503), over the whole width, 3 cm legs both sides (superseded 2026-10-28, see registo: ≈ 2 cm,
  "tal como no projeto de torres vedras" — JSON `cobertura.chapeu.descida` 0,02 on the next rebuild).
- Battens round every opening: two jambs + the head (user 2026-10-16; head assumed — to confirm) (superseded
  2026-10-16 night, see registo: head and below for windows not reaching the floor, corner battens, every 0,35 — v5).
- Validation 0 issues; close-ups (`pormenores.py`, now also the re-entrant corner from the notch and from the
  roof) checked.

## Errors the user found in version 3 (fixed in version 4, 2026-10-16)
Bare structure at the re-entrant corner (the end of P03 standing over the wing roof) · downpipe end covered by the
foundation base (it must end slightly above it so the water can leave) · rufo as a flat plate on the wall top instead
of a chapéu wrapping the wall (≈ 3 cm down both faces) · battens not round the openings (a rule the user had not given
yet: "Um pormenor que me esqueci de te dizer") · roof from the architect's 1,3 % (the user's one-slope-per-part
sketch, then withdrawn for D2503's 6 %). Screenshots and sketches: `docs/revisao-modelo/2026-10-16_v3_*`.

## How it is built (first house from an architecture plan, 2026-10-15)
(Versions 1–3; the roof, heights and wall line below are superseded by version 4 above.)
- `ferramentas/modelo/planta_arquitetura.py` → `planta_paredes.json` (18 walls, 6 exterior).
- `ferramentas/modelo/casa_planta.py` (the builder) frames every wall the DiscoverCasa way:
  - exterior 110×35 at 40 cm clear, the frame placed so that frame + OSB 15 + Pladur end on the architect's
    inner face (rooms keep their size; the architect's 0,25 wall keeps ≈ 4 cm spare outside); interior 75×35
    on the architect's centre line; 110×75 at the corners and around openings; verga 220×75 over the garage
    door (3,00 ≥ 2,8) (superseded 2026-10-16 night, see registo: as built 11×7,5 — D2503 Módulos, v5);
  - X walls run through the corners, Y walls stop against them, interior walls stop at the frame they meet;
    the re-entrant corner of the L (left out of both walls by the architect) is closed (corners superseded
    2026-10-16 night: as built P14 runs through at the wing's SW corner — `modulos-D2503.md`, v5);
  - modules ≤ 3,0 m (user), joints never within 10 cm of an opening: 43 wall modules (two longer than 3 m:
    3,30 with the garage door, 4,34 with the two sliding doors of quartos 02/03) + 21 parapet modules (superseded
    2026-10-16 night, see registo: the D2503 modules — grid bays, ≤ 2,64 / 2,72, M1 3,82 on site, the sliding doors
    split at the pier, one 3,50 module with the parapet — v5);
  - heights: vinyl 5 mm on the foundation base (Z 0), clear height 2,60 → Pladur ceiling 2,605, ceiling
    beams 2,662–2,882, modules 2,552 high (exterior and interior), afinação 35 + amarração 75 (exterior) /
    afinação 110×75 (interior) on top;
  - roof hidden by the walls (version 2, after the user's review 2026-10-15): vigas de apoio ao teto
    220×75 N–S at ≤ 1 m (west zone from the south wall of the main block, wing zone from the wing's south
    wall, both to the north wall; up to ≈ 8 m — the company limit); two slopes at 1,3 % (section B) from a
    ridge along x at Y 6,749 (middle of the main block, roof plan): north slope, south slope of the main
    block, south slope of the wing; vigas de apoio à cobertura 110×75 at ≤ 1,2 m on prumos; panel 5 ondas
    80 mm. Version 3 (user 2026-10-16): every exterior wall rises to the same height — parapet frames 110×35
    to Z 3,30 (5 cm above the panels at the ridge), X walls through the corners, wool inside, clad on the roof
    side with OSB 15 + Traspir + ripado + Tremolo; on the low side of each slope (north wall, south wall of the
    main block, south wall of the wing) a caleira oculta inside the parapet: 110×75 laid flat on the ceiling
    beams + OSB 22 + 110×75 upright (channel 30 cm, 11 cm deep on the longest slope, deeper on the shorter
    ones), aluminium lining with end caps; panels end 5 cm into it; 2 downpipes per gutter, from the channel
    through the parapet into the facade's batten cavity and down, hidden by the Tremolo, clear of the
    openings; rufo over every parapet, closed at the corners, falling 2 cm towards the roof (the water runs into the
    gutters, user 2026-10-16) with a drip leg over the cladding (fall and leg assumed) (superseded 2026-10-16, see
    registo: the chapéu — wraps the wall, ≈ 3 cm legs both faces, flat as in D2503 — version 4); the 2 skylights of
    the roof plan were not built.
- Layers: OSB 9, Traspir 95, ripado 37,5×35 horizontal at 0,50 (superseded 2026-10-16 night, see registo: 0,35 from
  the bottom — v5), Tremolo vertical — the standard option A
  without its contra-ripado (this house had none: config override; options B/C removed in the config); wool 80 / 60 in the walls,
  OSB 15 + Pladur inside; ceilings with réguas, perfis, cantoneira, Pladur and 100 mm wool (thin strips of
  a room get Pladur and wool too — the slot in the sala ceiling, fixed); vinyl straight on the base.
- Validation 0 issues (exterior layers checked against the real frame outline `contorno_estrutura`).

## Differences from the architecture (answered by the user 2026-10-15)
- Height: version 1 (5 % slope) ended at 3,49; with the drawings' 1,3 % the parapets end at 3,17 (≈ 3,10).
  A taller house than the architecture "é natural". (Superseded 2026-10-16, see registo: as built 3,4915 on every
  wall, 6 % — D2503, version 4.)
- Sala + cozinha: the N–S ceiling beams span ≈ 8 m — "o nosso limite é precisamente 8 metros". (As built, D2503
  2026-10-16: glulam lameladas 20×10 at 0,915, 8,50 / 11,00 — version 4.)
- Modules longer than 3 m (3,30 / 4,34) — built on site, so the exact wall length.
- Interior doors use the DiscoverCasa rough opening 0,87 × 2,03 (architect: 0,80 leaves).

## Errors the user found in version 2 (fixed in version 3, 2026-10-16)
Gutter walls lower than the side parapets (the house must have the same height on every side) · exterior
gutters (the gutter is inside, at the level of the rufos' underside) · downpipes in front of openings /
reading as inside the rooms (they run inside the exterior cladding, hidden by the Tremolo).

## Errors the user found in version 1 (fixed)
Rufo corners open (water into the cladding) · parapets bare on the roof side · gutters hidden behind the
parapet, below the rufo (now at the rufo level: modelled as exterior gutters — exterior or the company's
caleira oculta at the wall head is asked) · a slot across the sala ceiling (thin strip skipped) · battens
at 0,35 (0,50) · slope 5 % instead of the drawings' 1,3 %.
