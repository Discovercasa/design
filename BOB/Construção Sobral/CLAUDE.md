# Construção Sobral — Loteamento Sobral (Sobral de Monte Agraço)

16 single-family timber-frame houses + 1 warehouse building ("fração única").
Requerente: DiscoverCasa, Lda. Structural project ("Estabilidade"): engineer (name and ID removed), Feb 2026, AutoCAD LT.
Site: Sobral de Monte Agraço (Lisbon district, higher seismic hazard). Ground elevations ≈ 200–205 m.

| Type | Units | Site | Layout | Drawing (`desenhos/`) | Model |
|---|---|---|---|---|---|
| Tipo 1 | A B C D E K L M N O P (11) | flat | living GF, bedrooms upstairs; FFL +2.88, ridge +7.00 | `PD_Habitacoes A B C D E K L M N O P (1).dwfx` | `modelos/tipo1/` ✅ DiscoverCasa structure + build-up layers |
| Tipo 2 | F G H I J (5) | slope | entrance/living upstairs ±0.00, bedrooms −2.70; eaves +2.75, ridge +4.30 | `PD_Habitacoes F G H I J.dwfx` | not yet |
| Armazém | 1 building, 3 wings | slope | concrete frame in drawings → to be redesigned in timber | `PD_Estabilidade Armazém.dwfx` | not yet |

Both house types (drawings): footprint 9.86 × 6.11 m, 2 storeys, gable roof 26.4°, studs 160×80 /
100×80 at 0.48 m c/c, OSB3 12 mm both faces, joists 160×80, rafters 80×160. **Tipo 1 is modelled with
the DiscoverCasa skeleton** (user 2026-09-30: 110×35 / 75×35, 110×75 at corners and openings, flat
upper ceiling at the tie beam, roof on posts and purlins) and the DiscoverCasa build-up (OSB 9 + 15);
the engineer must re-check (`docs/revisao-tecnica.md` #15, #16, #20–22, #24).
Tipo 1 finishes (user, 2026-09-24): exterior walls **ETICS / white capoto (option B)**; roof exposed
tile-effect sandwich panel, dark grey. Architecture set (CAL30, both house types) in
`desenhos/SMA_012_arquitectura_pecas_desenhadas.dwfx` — "for now the final version" (user 2026-10-09).
Start at "▶ Where we stopped" in `docs/estado.md`. Pending from the user: roof option (A keep pitch /
B keep ridge), the foundation base (to be taught), living-room joist spacing, tie beam on the ground-floor
walls, section of the opening pieces in 110 walls.

## Documents (read only what the task needs)
- `docs/desenhos.md` — sheet-by-sheet contents, sheet coordinates, drawing conventions and traps. Read before extracting data.
- `docs/revisao-tecnica.md` — issues found in the drawings (status of each).
- `docs/modelos.md` — how the Blender models are built; Tipo 1 decisions, levels, quantities.
- `docs/armazem.md` — warehouse facts and notes for the timber redesign.
- `docs/estado.md` — status, next steps, open questions, decision log. **Update at the end of every task.**

## Folders
- `desenhos/` — original DWFx from the engineer. Never edit; a new issue replaces the file (log it in estado.md).
- `modelos/<tipo>/` — `config.json` (the only hand-edited file; its `camadas` key overrides the company
  build-up for this project) → generated `*_geometria.json`, `.blend`, two `.glb` (structure / complete
  house), `quantidades.csv`.

Rebuild Tipo 1: `python ferramentas/modelo/construir_casa.py "Construção Sobral/modelos/tipo1/config.json"`
