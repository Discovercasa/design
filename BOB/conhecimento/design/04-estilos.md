# 04 · Style sheets (fichas de estilo) and identity
Rulebook v1.0 (2026-11-27). Manual v1.0: ch. 6 and Anexo B. Tags: see `../design-interiores.md`.

A style sheet teaches the language of a style — what defines it, how it turns into materials and how it can vary without
losing its identity — instead of tying a label to a picture.

## Register of our styles (DC)
| Id (file in `estilos/`) | Style | Status | References (local only) |
|---|---|---|---|
| — | contemporâneo quente (light oak, linen, sand, matt black) | proposed by Claude 2026-11-26, awaiting the user's choice | `_trabalho/referencias/<subfolder>/` |
| — | nórdico claro (light wood, white, greys, textured fabrics) | proposed, awaiting the user's choice | — |
| — | mediterrâneo natural (microcement/terracotta, natural fibres, olive green) | proposed, awaiting the user's choice | — |
The user may swap or add styles. A sheet is written from the user's 5–10 reference images per style (whole rooms and
close-ups) and gets status: rascunho → para aprovação → aprovada (date, user's words).

## 6.1 Fields of every sheet [REC]
| Field | Content |
|---|---|
| Identity and philosophy | the atmosphere, references, values and core traits |
| Reference images | selected and annotated: which ones are for form, colour, furniture, material, light |
| Colour palette | main, secondary and accent colours; undertones, saturation, relations |
| Materials | woods, stones, ceramics, metals, fabrics, floors, wall finishes |
| Language of forms | proportions, silhouettes, lines, curves, geometries, relation of volumes |
| Furniture and signature pieces | piece types, visual traits and proportions that make the style recognisable |
| Light | daylight, lamp types, intensity, colour temperature, atmosphere |
| Decoration and styling | art, objects, textiles, plants, books, visual density |
| Per room | how the style shows in living rooms, kitchens, bedrooms, bathrooms, workspaces |
| Combinations | compatible influences and styles; conditions for a good mix |
| To avoid | what usually weakens the identity — why, and the exceptions |
| Internal variations | more minimalist, warmer, classic, contemporary, rustic or refined versions |

## 6.2 Variations within a style [EST]
- A style is not one recipe: Japandi can be more minimalist, warmer and organic, or more contemporary. The sheet allows
  changes of intensity, texture and formality without losing the recognisable principles.

## 6.3 Reference images [REC]
- Never copy a whole image without understanding its logic: extract the principles that matter.
- Separate what transfers to the real space from what depends on the photographed architecture.
- Do not mix images of different styles without explaining the link between them.
- Prefer references that show materials, scale, light and proportions clearly.
- When the client's references conflict, name the tensions and propose one coherent visual direction.
- (DC) [OBR] (B2: copyright, public repo) The images stay in `_trabalho/referencias/`: the sheet describes them in words and
  names the file, it never copies them into Git.

## 6.4 "Avoid", not "never" [EST]
- Replace "never use" lists by "elements to avoid": explain why the element usually clashes with the style and when an
  exception can work. An unexpected piece can enrich a room when deliberate and well integrated.

## Anexo B · Style sheet template (copy into `estilos/<id>.md`)
```
# <Style name and variation> (e.g. Japandi contemporâneo quente)
Status: rascunho | para aprovação | aprovada YYYY-MM-DD («user's words») · References: _trabalho/referencias/<folder>/
- Philosophy and atmosphere: what it conveys, its principles.
- Colour palette: base, secondary, accents, undertones (with hex values and the real material each one comes from).
- Main materials: woods, stones, metals, fabrics, ceramics, finishes (with the texture set used: CC0 source or ours).
- Forms and silhouettes: lines, curves, volumes, proportions.
- Signature furniture: key pieces, scale, structure, details (→ piece sheets, 05-pecas.md).
- Light: daylight, layers, colour temperature, lamp types.
- Decoration and art: objects, density, plants, textures, composition.
- Per room: living, kitchen, bedroom, bathroom, office, circulation.
- Bridges with other styles: compatibilities, conditions, difficult mixes.
- To avoid: what usually weakens the language, and why.
- Reference images: one line per image — file name, what it is a reference for, the principle taken from it.
- Variations: more minimalist, refined, warmer or relaxed versions.
- Confidence: what is well established and what is the agent's interpretation.
```
