# 05 · Anatomy of furniture and objects
Rulebook v1.0 (2026-11-27). Manual v1.0: ch. 8 and Anexo C. Tags: see `../design-interiores.md`.

Each furniture category needs its own sheet: not only the look, but the construction, proportions, materials, physical
behaviour and the details that make it credible. (DC) This is where our current pieces fail — the user, 2026-11-26: «o meu
grande problema com a mobília desenhada por nós é muitas vezes a falta de detalhe ou não parecer realista e as vezes um
estilo não encaixar com o outro».

## 8.1 Standard sheet of a piece [REC]
- Function and context of use.
- Real dimensions and main proportions.
- Structure and visible construction method.
- Materials, thicknesses, finishes, hardware.
- Geometry: edges, chamfers, radii, curvature, transitions.
- Making details: joints, seams, gaps, handles, feet, supports.
- Physical behaviour: deformation, weight, compression, floor contact, how it reflects light.
- Geometry and material versions for render, web, AR and VR (`07-realismo-digital.md` §13).

## 8.2 Sofas and armchairs
- [TEC] Frame, arms, back, seat, feet or plinth, with their proportions.
- [TEC] Say whether the cushions are fixed, loose, separate or integrated.
- [TEC] Seams, piping, top-stitching and joins when the product has them.
- [TEC] Volume and compression consistent with the foam, filling and fabric.
- [EST] Sag subtle and consistent with use — never deform every sofa by default.
- [TEC] Creases and folds come from how the fabric behaves, not random deformation.
- [TEC] Feet, plinth and contact areas sit correctly on the floor.

## 8.3 Kitchens and joinery
- [TEC] Thickness of fronts, sides, shelves and worktops as in the design or product.
- [TEC] Joints and gaps between doors and drawers; 2–3 mm is a common visual reference but follow the system and maker.
- [TEC] Recessed plinth, levelling feet, handles, profiles and hardware when visible.
- [TEC] Respect the grain direction and the logic of the veneer or finish.
- [TEC] No doors that look like plates with no thickness or no way to open.
- [TEC] Consistent alignment, continuity and spacing between modules.

## 8.4 Beds and bedding
- [TEC] Frame, headboard, base, feet and real thicknesses.
- [EST] Bedding matches the style and the room's formality: a hotel bed can be very structured; a relaxed room has natural
  folds and volumes; a minimalist room uses few elements.
- [TEC] Duvet, sheets and throws with credible weight and drape — never floating or passing through the frame.
- [TEC] Pillows with plausible volume, compression and placement.

## 8.5 Chairs and stools
- [TEC] Seat height and depth, back angle, thickness and visual stability.
- [TEC] The relation of frame, seat, back, legs and rails.
- [TEC] No legs too thin or too thick for the real construction.
- [TEC] The chair goes under the table and there is room to use it.

## 8.6 Tables and surfaces
- [TEC] Top thickness, edge profile, structure and supports.
- [TEC] No visually impossible tops, without thickness or with supports that could not carry them.
- [TEC] Texture and finish at the right scale.
- [TEC] Table height against the chairs and the intended use.

## 8.7 Wardrobes and storage
- [TEC] Depths, divisions, doors, drawers, handles and opening systems.
- [TEC] Approach and opening space.
- [TEC] Plinths, cornices, side trims and meeting with ceiling and walls.
- [TEC] No units ending without a trim or seeming to float with no fixing.

## 8.8 Bathroom furniture
- [TEC] Wall-hung, floor-standing or on a frame — say which.
- [TEC] Basin, top, tap, trap when visible, handles and joints.
- [TEC] Materials fit for humidity and cleaning.
- [TEC] Gaps, drawer opening, access to the tap, relation to mirror and light.
- (DC) [REC] Sanitary ware, taps and appliances: the makers' free 3D models of the brands the user gives (pending) —
  real products read as real; see `10-discovercasa.md` §2.

## 8.9 Detail sheet per category
- [OBR] (B3) When a model stands for a specific product, the digital drawing follows the real reference — never generic
  details the piece does not have. A sheet holds reference images, dimensions, materials, construction details, style
  variations and export requirements.

## Anexo C · 3D object sheet (one per piece; an approved piece is listed in `12-pecas-aprovadas.md`)
| Field | What to record |
|---|---|
| Identification | name, category, version, origin, visual reference (DC: catalogue id `OBJ_<NAME>`) |
| Dimensions | width, height, depth, functional dimensions (DC: metres, x = width, y = depth, z = height, front facing −y, as `interiores/catalogo.json`) |
| Structure | components, thicknesses, supports, visible assembly |
| Materials | material per component, colour, finish, roughness, maps (DC: texture source — CC0 library or ours) |
| Geometry | bevels, radii, curvature, visual tolerances, level of detail |
| Details | seams, gaps, handles, feet, joints, hardware, trims |
| Behaviour | compression, contact, deformation, reflection, shadows |
| Render version | quality and setup for stills and VR |
| Web version | LOD, textures, materials, collisions, performance |
| AR version | scale, pivot, compatible materials, interaction (DC: triangle budget `ar_tris`) |
| Validation | comparison with the reference, confirmed dimensions, export tests (DC: the approved close-up render) |
