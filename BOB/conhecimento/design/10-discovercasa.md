# 10 · DiscoverCasa: our case, our sources, our loop (DC)
Rulebook v1.0 (2026-11-27). Not in the manual v1.0 — added for DiscoverCasa. Tags: see `../design-interiores.md`.

## 1. Our case
- DiscoverCasa designs and builds **turnkey timber-frame houses** (Penafiel). The interiors we draw show the client the
  house they are buying, on four services built from **one Blender scene per house**: the client page's interactive 3D
  (the **base service**), the 360° tour inside it, Step Inside AR and VR; Build Your House «Smart Interiors» uses the same
  catalogue (`interiores/catalogo.json`: «one catalogue, not two»).
- [CTX] The page is often made **before any interior briefing**. Defaults, until the client says otherwise: the style
  chosen for the house (or the one closest to its architecture and finishes), a bed in every bedroom (main bedroom
  double, the others as the project shows or single), no personal objects. Say them to the user when showing.
- [REC] Proposed (not yet asked of the user): add 3–4 interior questions to `conhecimento/perguntas-por-obra.md` —
  style, who lives there (children, pets), home office, furniture they keep.
- [EST] The interior talks to the house: the style follows the façade and the finishes the client chose.

## 2. The aim: the client falls in love with the house
- User 2026-11-27: «apenas com os interiores estarem os mais impressionantes possíveis e que o cliente se apaixone pela casa»; «nao te preocupes com o que a discovercasa entrega».
- [EST] Draw whatever makes each room most impressive and most real — kitchen, lighting (downlights, coves, lamps),
  furniture, art, plants — with no split between what the house includes and staging, and no "illustrative" labels.
- [REC] Sanitary ware, taps and appliances: when the user gives the brands (with the prompt to analyse the reference
  images; hub task «Marcas de sanitários, torneiras e eletrodomésticos»), use the makers' free 3D models — real
  products read as real. Until then, the best-looking credible piece.
- (superseded 2026-11-27: «what we deliver versus staging» — delivered products as the real product, staging marked
  illustrative; the user: «nao te preocupes com o que a discovercasa entrega»)

## 3. Sources: free only
- **User decision (binding, not a design guideline):** «Pagar uma libraria está fora de questão» (2026-11-26): no paid
  libraries or packs.
- CC0 sources in use: **Poly Haven** — textures, HDRIs, models (local library `_trabalho/assets/polyhaven/`, downloader
  `ferramentas/pagina/descarregar_ativos.py`; interior models in `_trabalho/interiores/`, downloader
  `interiores/descarregar.py`, licences in `interiores/fontes.json`). Poly Haven has no beds, toilets or modern kitchens
  → those pieces are ours (parametric) and must reach the realism of the scanned ones.
- **ambientCG** (CC0) first used by the downloader on 2026-11-27 (Marble021 for the extending table, user: «ambientCG
  Marble021 (Recommended)»); Poly Haven 4K textures for that table (oak_veneer_01, walnut_veneer). Poly Haven
  `marble_01` is a stone paving with joints: not for slab tops.
- [REC] A new free source (another CC0 library, a maker's site) and every download need the user's OK first (repo rule).
- Sanitary ware, taps, appliances: the makers' free 3D models of the brands the user gives (pending).
- Missing materials: made by us from a reference, ultra-realistic, same in Blender and Unreal (`07-realismo-digital.md` §12.4).
- [OBR] (B2) Never in Git: reference images (`_trabalho/referencias/`, copyright), downloaded models and textures
  (`_trabalho/`), client houses (Páginas pages live in the hub's private storage).

## 4. Files and tools (where the furniture lives today)
- Page 3D: `ferramentas/pagina/interior.py` — ≈ 30 piece types drawn from boxes and cylinders (the pieces the user finds
  lacking detail and not realistic: to be remodelled, hub task «Remodelar as peças com detalhe real, por estilo»);
  `ferramentas/pagina/vegetacao.py`, `casa_blender.py` (house and materials), `gerar_pagina.py`, `modelo_pagina.html`.
- Extending table (2026-11-27, `ferramentas/movel/`): `extrair_pagina.py` (decodes the source page's geometry),
  `blender_mesa.py` (scene: table, our chair, real room, day/night light, bakes, Cycles reference renders),
  `mesa_extensivel.json` (finishes/room/light), `aliviar_mesa.py` (lighter page assets from the saved scene),
  `gerar_pagina_mesa.py` + `modelo_mesa.html` (the page, same functions as the source). `pagina/descarregar_ativos.py`
  gained `--texturas=a,b` (other resolutions into `<id>/<res>/`) and `--ambientcg=ID`. The page is delivered as a file
  to the user only (not hub, not Git).
- Step Inside: `interiores/catalogo.json` (27 objects: 16 Poly Haven CC0 + 11 parametric — kitchen, island, fridge column,
  wardrobe, beds, dining table, WC, vanity, shower, TV), `step-inside/ferramentas/interiores/` (`pecas.py`,
  `interiores.py`, `blender_interiores.py`).
- Which pieces are scanned CC0 and which are ours: Step Inside → `origem` in `interiores/catalogo.json`; page → the
  `p.modelo("<asset>")` calls in `interior.py` (everything else there is ours). A fix says "swap" for a scanned model,
  "remodel" for ours. One list for both comes with the common library.
- Target (hub task «Mesma biblioteca no 3D, tour, AR e VR»): one library for the four services — each piece in three
  levels (full, web, AR) with the full version's detail baked into the light versions' textures.
- [TEC] Our walls: timber frame, OSB 15 and Pladur inside (`sistema-construtivo.md`); interior doors 2,00 × 0,80; interior
  walls take doors only. The interior is placed on the house model's real geometry (B1).

## 5. The approval loop (user-approved plan, 2026-11-26)
1. **Style sheet** from the user's references (`04-estilos.md`, `estilos/<id>.md`) → the user approves it.
2. **Piece**: its sheet (`05-pecas.md`, Anexo C) and model with real detail, by style.
3. **Close-up render next to the reference**, same framing and light where possible → the user's verdict.
4. Approved → `12-pecas-aprovadas.md` (with the render path and the three versions); rejected or corrected → a lesson in
   `11-licoes.md`, classified (manual §16.3), and the piece goes back to step 2.
5. Only approved pieces furnish a page: first a **furnished test page** in one style with images, tour, AR and VR for the
   user to approve (hub task «Página de teste mobilada só com peças aprovadas»).
- Before showing anything: checklist `09-metodo-qualidade.md` §16.4–16.5 and, for a client page, a preview of the 3D and
  the 360° renders for approval before upload (client page standard).

## 6. Open items
- Styles to do first and their references (user, in progress: folder `_trabalho/referencias/`).
- Brands and models of sanitary ware, taps and appliances (user, with the prompt to analyse the images).
- Web budget for the page 3D (load time, FPS on a mid-range phone) — measure on the first furnished test page.
- Interior questions in `perguntas-por-obra.md` — propose to the user.
- How heavy wall-hung pieces fix in our walls (method has no rule) — ask when a design depends on it.

## 7. Baseline: first review of our current interiors (2026-11-27)
The agent's first test reviewed the latest page stills of a recent test house (living room, kitchen, bedroom; renders
of 2026-11-24). Not yet a user verdict — a starting list for the remodelling task:
- Pieces to remodel first, by realism gained: (1) sofa and armchair — flat grey slabs, no weave, seams or cushion crown;
  (2) bedding — regular sine-wave hems, flat top, rigid wedge pillows; (3) kitchen — plate fronts with pure-black gaps, no
  hardware, no visible hood, empty worktops; (4) rugs — 14 mm slab with no pile (a cheap win); (5) bedside table and
  lamp — plain crates with no drawer, lamp bases glowing as if translucent.
- Quick fixes in the code, no remodel: the coffee table (Poly Haven `coffee_table_round_01`, scaled down in
  `interior.py` `mesa_centro()`, a glam curled-steel base in a straight-lined room) → swap for a simple model at native
  size; the glass pendant (`pendente()`) gets our black ceiling disc on top of the model's own canopy → one canopy only.
- Image-level: daylight outside with evening lamps inside, grey and under-exposed interiors, a soft wall shadow with no
  cause, bare walls with no focal point, repeated props, a pitched-down wide camera in the bedroom, no curtains on a
  full-height window, two oaks almost but not quite matching (table/chairs vs floor).
- (superseded 2026-11-27: the review's two "delivered vs illustrative" points — generic delivered products, downlights
  not confirmed — the user: «nao te preocupes com o que a discovercasa entrega»)
