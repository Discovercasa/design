# Materials list — Torres Vedras model (DiscoverCasa method)

Version 6.3, 2026-10-20 (version 5 plus the windows, doors with their remates and the tiled pergola below; interior modules made to the amarração; chapéu corners). Version 5, 2026-10-16: **walls as built** from DiscoverCasa's module drawing D2503 Módulos
(`docs/modulos-D2503.md`: 27 exterior modules 3,50 high, 23 interior 2,53, members and openings as drawn) and
**roof as built** from D2503 Cobertura (`docs/cobertura-D2503.md`); battens per the user's site photo (0,35 from
the bottom, openings framed, vertical battens at the corners). From `modelos/casa/quantidades.csv`. Quantities
are **as modelled** (net, pieces as cut); purchase counts use the unit and waste set in
`sistema_construtivo.json`. To be compared with the real list (user, later). Material names stay in Portuguese.

## Timber (casquinha) and glulam, 10,3 m³
| Where | Section | Pieces | Metres | m³ | D2503 cut list |
|---|---|---|---|---|---|
| Exterior modules (montantes, travessas, montantes curtos, escadas) | 110×35 | 233 | 476 | 1,83 | 220 pcs / 473 m (94 × 3,43 studs) |
| Exterior modules (cantos, ombreiras, padieiras, peitoris) | 110×75 | 51 | 140 | 1,15 | 50 pcs / 139 m (35 × 3,43, lintels 3,00 / 2,00 / 1,04 / 0,94 / 0,75) |
| Interior modules (montantes, travessas, escadas; v6.1: made to the amarração, 2,543 high) | 75×35 | 207 | 376 | 0,99 | 199 pcs / 379 m (109 × 2,46; the rule gives 2,473) |
| Interior modules (ombreiras, padieiras) | 75×110 | 24 | 46 | 0,38 | 24 pcs / 46 m (16 × 2,46 + 8 × 0,87) |
| Amarração on the inner face of the exterior modules + amarração on top of the interior modules (0,11) | 110×75 | 18 | 104 | 0,85 | (site) |
| **Lameladas** (glulam; 11 × 8,50 + 7 × 11,00) | **200×100** | 18 | 171 | 3,41 | roof D2503 |
| Madres 11×7,5 (44 pieces, ≤ 3,66) + prumos (122) + calços da caleira (65) | 110×75 | 231 | 202 | 1,71 | roof D2503 |
| Totals | | 782 | 1512 | 10,32 | |

The model's piece counts are a little higher (studs split at the lamelada pockets); the D2503 cut lists are the
real ones. Lameladas from stock (D2503): A 8,50 cut from 13,5 m (5 m waste), B 11,00 from 12 m (1 m waste).
(2026-10-21, see registo: this list predates the user's correction — no pockets, the studs whole, the lameladas end
at the modules' inner face: the builder now gives 166,53 m of lameladas (≈ 8,28 / 10,78) instead of 171 and 696 module
pieces instead of 702 → regenerate with model v6.5, `modelos.md`. Whether the order stays 8,50 / 11,00: to confirm.)
(Answered 2026-10-21, see registo: "Sim normalmente cortamos para "encaixar" no tipo de obra que temos" → cut to fit
each house: 8,50 / 11,00 = nominal (outer depth), bought from 13,5 / 12 m stock, cut to ≈ 8,28 / 10,78. In the
regenerated list give the cut length and the purchase (stock) length; the waste suggestion `revisao-tecnica.md` #12
stands.)

## Boards, membranes, insulation
| Item | Quantity | Purchase |
|---|---|---|
| OSB3 9 mm (exterior) | 166,0 m² | 59 sheets 2500×1250 (+10 %) |
| Traspir 95 (walls) | 166,1 m² | 3 rolls 1,5 × 50 m |
| OSB3 15 mm (inside of the walls, up to the amarração) | 318,9 m² | 113 sheets 2500×1250 |
| Pladur N 13 (walls, up to the ceiling) | 311,0 m² | 110 sheets 1200×2600 |
| Lã mineral Volcalis Comfort 80 mm (exterior walls and parapets) / 60 mm (interior walls) | 225,5 m² (16,3 m³) | — |
| Lã mineral Volcalis 100 mm on the ceiling | 137,1 m² (13,7 m³) | — |

## Exterior finish (Tremolo vertical on horizontal battens, no contra-ripado)
| Item | Quantity | Purchase |
|---|---|---|
| Ripado 37,5×35 horizontal every 0,35 from the bottom, round every opening (jambs, head, sill unless at the floor), vertical at every corner on both faces | 556 m (+ 11 m on the gable parapets' roof side) | — |
| Forro Piveteau TREMOLO Douglas 22×135, vertical (v6.1: cut round the pergola's ledger and beam ends; on the gable parapets to the end of the sandwich panels) | 166,3 m² (+ 5,0 m² on the gable parapets) | 366 + 11 boards of 4,0 m (+10 %) |
| Gable parapets, roof side: OSB 15 + Traspir | 4,6 m² each | 2 sheets OSB 15 |

## Ceilings (all rooms, at 2,50)
| Item | Quantity | Purchase |
|---|---|---|
| Réguas de suspensão (0,15 drop under the lameladas) | 385 pieces (90,7 m) | — |
| Perfis de teto 47×17 at 0,40 | 361 m | — |
| Cantoneira 30×30×0,5 | 148,2 m | 50 bars of 3 m |
| Pladur N 13 (ceiling) | 153,5 m² | 55 sheets 1200×2600 |

## Floor and roof
| Item | Quantity |
|---|---|
| Vinílico (on the foundation base) | 151,7 m² (useful area of the rooms) |
| Painel sandwich 5 ondas 80 mm | 30 × 3,94 + 7 × 6,44 (152,3 m²) — D2503: 28–29 × 3,94 + 3,94 × 0,25 + 7 × 6,44 |
| Caleira oculta (aluminium lining; north 17,3 m, south of the main block 10,8 m, wing 6,5 m) | 34,6 m (3 gutters) |
| Tubos de queda inside the cladding (at the outlets: north ×2, P03 west, P01 east) | 4 (11,5 m) |
| Chapéu de platibanda (all walls; developed width ≈ 0,24 on the gutter walls, ≈ 0,31 on the gable parapets) | 56,8 m |
| Cumeeira | 17,1 m (D2503: "encomendar 18 cumeeiras") |

## Windows, doors and garage door (model v6, 2026-10-19)
From the user's table "PROJETO APROVADO" (`revisao-modelo/2026-10-19_projeto_aprovado_vaos.png`): aluminium
lacado cinza rato **RAL 7016** with thermal break, double glazing; 11 items, **31,06 m²**; 6 "Estore exterior
automático". Each in its D2503 module; the rough opening (vão em bruto) is the module's:

| Module | Room | Item (maker's size L × A) | Rough opening in the module L × A (sill) | Difference |
|---|---|---|---|---|
| M24 | Despensa | basculante 0,80 × 0,80, transparent, estore | 0,75 × 0,95 (1,035) | width −0,05; height +0,15 (shutter box) |
| M23 | Despensa | porta painel liso 0,80 × 2,20, opens right — fills its opening like the entrance (user 2026-10-20) | 0,94 × 2,20 | modelled 0,89 |
| M20 | Cozinha | vidro fixo 1,50 × 0,80, estore | 1,50 × 0,95 (1,036) | height +0,15 (shutter box) |
| M18 | WC | basculante 0,80 × 0,80, fosco | 0,75 × 0,75 (1,036) | −0,05 both ways |
| M12, M14 | Quarto 1 e 2 | janela de correr 2 folhas 2,00 × 2,20, estore | 2,00 × 2,40 | height +0,20 (shutter box) |
| M9 | Quarto Suite | janela de correr 2,00 × 2,20, estore | 2,00 × 2,40 | height +0,20 |
| M6 | WC Suite | basculante 0,80 × 0,80, fosco | 0,75 × 0,75 (1,035) | −0,05 both ways |
| M5 | Sala / Entrada | porta painel liso 0,90 × 2,20, opens right — as built a bigger, sturdier door filling the opening (user 2026-10-19) | 1,04 × 2,20 | modelled 0,99 (2,5 cm clearance each side) |
| M3 | Sala / Entrada | janela de correr 2,00 × 2,20, estore | 2,00 × 2,40 | height +0,20 |
| M1 | Garagem | portão seccionado automático 3,00 × 2,20, opens up | 3,00 × 2,20 | none |

Modelled: frame, leaves and glass 20,7 m² (8 glazed items), 6 shutter boxes with guides, 2 door panels + the
garage door. Clearance 2,5 cm per side (company default, user 2026-10-20). The basculantes are 0,80 in the table, their rough openings 0,75: modelled 0,70, "está ótimo como
fizeste" (user 2026-10-19). The table gives the frame size without clearance ("normalmente contamos com a folga"). Shutter box 0,15 on the 0,80
windows and 0,20 on the 2,20 doors (from the rough openings) (corrected 2026-10-27, see registo: the 2,20 items with a
box are the **janelas de correr** M3 / M9 / M12 / M14 — doors take no estore, "Prtas não tem estore apenas as
janelas"; M5 / M23 have none, as the table). The WC row (M18) says "vidro duplo térmico trasnparente"
but "Fosco" in Observações — modelled fosco (details keeper 2026-10-19; `revisao-tecnica.md` #20).

## Remates of the openings (model v6.3)
Every opening is trimmed so the wall layers are not seen (user 2026-10-20): outside folded aluminium RAL 7016
(reveal + return over the clearance + 3 cm flange; sill with a drip under the 5 windows), inside a lining of the
reveal (Pladur assumed). 11 openings, 59,7 m of perimeter (profiles assumed). Photos of the finished house: dark
surrounds on the windows, a light surround on the garage door and light sills under the east windows (to confirm).

## Pergola (model v6.3)
From just east of the garage (x 3,63) to the east end of the house (x 17,57), front at y −2,01 (user 2026-10-20 and
the photos of the finished house); glulam with autoclave treatment; ceramic tiles; exposed gutter along the whole
front, downpipes at the post in front of the wing's west face and at the east corner post. Height at the front
confirmed; sections, slope (15 %), tile model and underlay, gutter section assumed. From `quantidades.csv`:

| Item | Quantity |
|---|---|
| Posts 16×16 (6), front beam 16×16 (13,9 m), beams 16×16 (11, falling to the front) | 18 pcs, 64,7 m, 1,65 m³ |
| Ledgers 7,5×16 screwed to the facades over the battens (P03 and the wing) | 2 pcs, 13,9 m, 0,17 m³ |
| Slats 7×3 at 0,15 | 301,8 m, 0,63 m³ |
| Ceramic tiles | 46,4 m² (along the slope) |
| Exposed gutter 12×10 along the front + 2 downpipes | 18,9 m |

## Not in the model yet
Foundation base (the user will explain it; only an indicative slab), window sills and reveal finishes (superseded
2026-10-20, see registo: modelled in v6.3 as the remates above; thresholds (soleiras) under the openings to the floor
still missing), screws, bolts and connectors (consumables), tapes, waterproofing under the chapéu and the gutter, gutter
outlets and overflows, services, deck. Waste factors only where `sistema_construtivo.json` has them.

## Assumptions behind these numbers
Everything in the roof from D2503 except: downpipes (not drawn: 80 × 35 in the batten cavity, at the
outlets); the gable parapets' roof-side cladding (user 2026-10-15; the gutter walls are lined by the gutter as
in D2503); the window head batten (two jambs + head; head assumed); chapéu flat (D2503) with 3 cm legs (superseded 2026-10-28, see registo: ≈ 2 cm);
panel thickness 80 mm. Openings and modules as in D2503 Módulos (sliding doors 2,00 × 2,40, garage 3,00 × 2,20, windows sills ≈ 1,03). Superseded: version 3 (1,3 % roof, ceiling
beams 220×75, modules inside the architect's wall line, clear height 2,60).
