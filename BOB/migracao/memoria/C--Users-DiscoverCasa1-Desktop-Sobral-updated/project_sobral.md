---
name: Sobral Duas Casas - Interior Design Project
description: SketchUp interior redesign project for two houses using Japandi Luxo + Mediterranean Wabi-Sabi style, Enscape renderer
type: project
originSessionId: 9b30f01a-1be8-4dfe-b146-68dff7dc8fd2
---
Project is a SketchUp model (553MB) at `C:\Users\DiscoverCasa1\Desktop\Sobral updated\Sobral Duas Casas.skp` containing two houses with existing furniture to be replaced.

**Why:** User wants a full interior redesign following Japandi Luxo / Modern Organic style for living/kitchen/bedrooms, and Mediterranean Wabi-Sabi for bathrooms. Renders will be done in Enscape so all materials must be PBR-compatible.

**How to apply:** When working on this project always check `Scripts\DESIGN_BRIEF.txt` for room-by-room specifications and `Scripts\02_create_materials.rb` for the complete PBR material palette (all named SBR_*).

Key constraints:
- No measurements/dimensions changed
- All walls white (SBR_Wall_White)
- All doors match main wood tone (SBR_Wood_Oak_Medium)
- Bathrooms: microcement walls + matte black steel fixtures
- Living/kitchen/bedrooms: warm oak wood + white quartz + natural linen
- PBR materials required for Enscape

Floor plans:
- Casa 1 ground: Entrada 4.2m², Cozinha 8.9m², Sala 25.3m², Lavandaria 2.8m², Inst.Sanitária 1.2m²
- Casa 1 upper: 3 Quartos (9+9+12.3m²), 2 CasasBanho (2.8+5.2m²)
- Casa 2 ground: Entrada 3.5m², Cozinha 8.8m², Sala 30m², Inst.Sanitária 1.5m²
- Casa 2 upper: 3 Quartos (9+9+14m²), 2 CasasBanho (2.7+5.2m²)

Scripts created in `Scripts/` folder:
- 01_diagnostic.rb — run first, outputs model layer/component structure
- 02_create_materials.rb — creates full SBR_* PBR material library
- 03_apply_materials.rb — applies materials by layer keyword matching
- 04_furniture_guide.rb — lists existing components + furniture shopping list
- 05_kitchen_beam.rb — generates kitchen ceiling wood box beam geometry
- DESIGN_BRIEF.txt — complete room-by-room design specification
