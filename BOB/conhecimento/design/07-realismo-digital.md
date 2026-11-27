# 07 · 3D realism — Web, AR and VR
Rulebook v1.0 (2026-11-27). Manual v1.0: ch. 12, 13. Tags: see `../design-interiores.md`.

## 12. 3D realism: geometry, materials, physical behaviour
Realism is one of the strongest drivers of credibility. The aim is not to make everything imperfect: it is to show the
construction, scale and materials correctly, and how light interacts with each object.

### 12.1 Geometry and edges [TEC]
- No mathematically perfect edges where the real product has small chamfers or rounds. A 1–3 mm chamfer is a first
  reference for some furniture, never applied blindly: stone, solid wood, lacquer, metal and upholstery each need their
  own treatment.
- Geometry follows the material and how it is made: do not round every edge by system, do not remove sharp edges that are
  part of the real design.

### 12.2 Upholstery and fabrics [TEC]
- Volume and compression consistent with filling and fabric.
- Separate cushions only when the piece is built that way.
- Seams, piping, top-stitching and creases at a realistic scale.
- Not every cushion perfectly aligned, but no artificial mess either.
- Deformation comes from gravity, contact and compression, not random noise.

### 12.3 Beds and bedding [TEC]
- Weight and drape of the duvet, folds, layers and pillows by style and atmosphere (hotel: structured, symmetrical;
  relaxed: looser fabric; minimalist: few elements). Bedding never floats, passes through the frame or has folds unrelated
  to weight.

### 12.4 PBR materials [TEC]
- Consistent maps: colour/albedo, roughness, normal, and metallic where it applies.
- Texture scale matches the material's real size.
- Bump, normal or displacement subtle and proportional.
- Roughness varies with the finish — never uniform over large surfaces without a reason.
- Metallic only for metals: never make wood, stone or ceramic metallic to get reflections.
- No uniform plastic reflections or over-perfect surfaces.
- No visible texture repetition on floors, walls, fabrics or large surfaces.
- Correct normals, UVs and transitions.
- (DC) A material missing from the free libraries is made by us from a reference, as close as possible, high quality and
  ultra-realistic, the same in Blender and Unreal (user 2026-11-26: «quando quisermos atingir um material que não temos
  numa libraria free o processo deve ser esse usar a referência de algo e tu desenvolveres o material o mais próximo
  possível … estes materiais gerados por ti devem ter alta qualidade e ser ultra-realistas»).

### 12.5 Grain, joints, construction [TEC]
- Wood grain follows the piece's construction.
- Continuous grain across kitchen fronts only when the material and design say so.
- Tile and stone joints at a realistic scale, consistent with the product.
- Skirtings, trims, profiles, silicone and joints where real construction has them.
- No surfaces ending abruptly or without a plausible build.

### 12.6 Contact with the space [TEC]
- Nothing floats without a physical reason.
- Credible contact shadows and ambient occlusion.
- Furniture feet, skirtings, bases, taps and objects meet their surfaces correctly.
- No intersections between objects, walls, floors and other furniture.
- Sockets and switches in plausible positions consistent with the project.

### 12.7 Controlled imperfection [EST]
- Chairs slightly turned, books leaning a little, textiles with natural folds, objects grouped at different heights can
  make a scene more human. Optional, by style and context; imperfection must never look like carelessness, mess or a
  modelling error.

### 12.8 Light and exposure of the render [REC]
- Balance natural and artificial light, exposure, contrast, reflections and temperature. Avoid over-lit interiors,
  shadows with no information, untextured materials or cinematic effects that distort the real colours. Make day and
  evening versions when useful.
- (DC) [REC] One time of day per image: the sky and garden seen through the windows match the interior light (daylight
  outside with evening lamps inside reads false) — lesson of the first agent review, 2026-11-27.
- (DC) [REC] Exposure and white balance: walls meant to be white read white (neutral white balance, not grey or
  yellow); a grey, under-exposed interior is corrected before showing (typically +0,5 to +1 EV); no unexplained soft
  shadows on walls (find the light that casts them).

### 12.9 Scanned and parametric pieces in one frame (DC)
- [TEC] CC0 scanned models are used at their native size: scaling them changes their real dimensions and their texture
  density; if the size does not fit, choose another model or make ours.
- [REC] Our parametric pieces reach the detail of the scanned ones next to them (thickness, edge radii, seams, fabric
  weave, roughness variation): a photo-scanned chair beside a plain box sofa is what makes a room look fake.
- [EST] A scanned piece must also fit the style: a striking model that clashes (e.g. a glam curled-steel table in a
  straight-lined Nordic room) is swapped, however real it looks.

## 13. Digital rules for Web, AR and VR
The same object may need different levels of detail by presentation mode. Optimising never changes the visual identity,
the dimensions or the reading of the product.

### 13.1 Three levels
| Aspect | Full / render / VR | Web | AR |
|---|---|---|---|
| Geometry | high detail for the hardware and distance | optimised for smoothness | optimised for real time |
| Textures | detailed resolution and maps | adapted resolution, efficient compression | adapted to the device and framing |
| Materials | detailed PBR, fine control | optimised PBR for the engine | compatible with the AR pipeline and device lighting |
| Dimensions | real scale, correct pivots | same dimensions as the original | physical scale coherent with the real space |
| Interaction | navigation, selection or VR | as the interface needs | placing, rotating, positioning |
| Performance | quality vs hardware | smoothness and loading first | stability and real-time response first |

### 13.2 Preparation [TEC]
- Apply scale and transforms before export.
- Origin/pivot in a logical place for placing, rotating and interaction.
- Coherent UV mapping, no texture distortion.
- LODs when distance or performance justify them.
- Optimise meshes, materials, draw calls and textures without destroying silhouette or essential detail.
- Collisions fit for interaction and navigation when needed.
- Consistent names, categories and metadata for asset management.
- Validate in the target engine and device, not only in the authoring software.

### 13.3 Consistency between versions [TEC]
- The web or AR version may simplify hidden or internal detail but keeps silhouette, proportion, dominant materials and
  the recognisable traits. The three versions are one conceptual asset with the same dimensions and placement.
- (DC) The detail of the full version is baked into the textures (normal/AO maps) of the light versions, so the realism
  reads the same in the four services (hub task «Mesma biblioteca no 3D, tour, AR e VR»).

### 13.4 Required tests [TEC]
- Check scale against a known dimension (DC: the project's interior doors — usually 2,00 × 0,80, but check the house:
  some projects have taller doors — and worktop 0,90, dining table 0,75, seat 0,45, the house's ceiling height).
- Test light, reflections and look in different environments.
- No inverted faces, wrong normals or missing textures.
- Test loading and smoothness in a representative scene.
- Collisions and interaction points do not block use.
- Compare the optimised version with the high-quality reference, side by side.

### 13.5 Our budgets and engines (DC)
- **Parity first:** realism must be consistent across the page 3D, the 360° tour, AR and VR — user 2026-11-26: «o
  realismo do 3D de ve estar consistente entre o 3D,TOUR, AR e VR. Ou seja o melhor posssível em todas». The page 3D is
  the base service; one Blender scene per house feeds the others. Warn the user if anything lowers the VR realism.
- **Full / stills / tour:** Blender Cycles (renders, 360° panoramas, baked light for the page 3D); Unreal path tracer for
  approval stills of the Unreal scene.
- **VR:** Unreal 5.8, forward renderer, baked light (Step Inside Phase 8, profile `VR_BAKED`); 72–90 FPS per eye, aim
  90 Hz — measured on the RTX 2060 home PC: living room 107,8 FPS, bathroom with planar mirror 111,8
  (`step-inside/docs/fase8/README.md`). Dense scanned meshes on the volumetric lightmap, our parametric pieces lightmapped.
- **AR:** ≈ 50 000 triangles for the whole house with furniture (Google Scene Viewer guidance: ideal ≤ 50k, warning
  above 100k — `step-inside/docs/fase7/README.md`); the house alone ≈ 24 000 (Torres Vedras), so ≈ 20 000 for the
  furniture of a T3; per-object budget `ar_tris` in `interiores/catalogo.json` (e.g. 3-seat sofa 1 800).
- **Web (page 3D):** no fixed budget yet — measure load time and FPS on a mid-range phone when the first furnished test
  page is built (open item, `10-discovercasa.md` §6).
