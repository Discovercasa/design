# Construção Torres Vedras — single-family house (Torres Vedras)

**Already built by DiscoverCasa.** Goal (user 2026-10-15): model it with the DiscoverCasa method from the
architecture drawings and compare the model's materials with what was really used on site, so the
model builds houses "como nós" — the first test of the builder (architecture → DiscoverCasa house).

Single storey, T3 + garage, ≈ 17,50 × 8,50 m plus a 6,72 × 2,50 m wing (suite), flat-looking box with
a parapet (roof hidden), Tremolo cladding (vertical as built; the architect drew it horizontal), deck terrace. Architecture
"Estudo Prévio" July 2024, 1:200.

| Drawing (`desenhos/`) | Contents |
|---|---|
| `250828_D2503_Modulos.dwfx` | **DiscoverCasa wall modules as built** (27 exterior, 23 interior, members, cut lists) — `docs/modulos-D2503.md`; read by `ferramentas/modelo/modulos_dc.py` → `modelos/casa/modulos_D2503.json` |
| `250828_D2503_Cobertura.dwfx` | **DiscoverCasa roof as built** (lameladas, madres, gutters, panels, sections 1:50) — `docs/cobertura-D2503.md` |
| `projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx` | 4 sheets: plan + sections A/B, plan/roof + 4 elevations, details P1/P2, accessibility plan |
| `Planta de implantação F01,1.dwfx` | site plan |
| `20241024.PL_LA_muros-F05.1_MUROS.dwfx` | street retaining wall (34,91 m) |
| `Levantamento topográfico F00.0.dwfx` | topographic survey |
| `.dwg` / `.pdf` of the same, `planta localização.pdf` | sources, location |

Start at "▶ Where we stopped" in `docs/estado.md`. Drawing facts and regions: `docs/desenhos.md`.
Issues and risks: `docs/revisao-tecnica.md`.
Walls and openings extracted from the plan: `modelos/casa/planta_paredes.json`, made by
`python ferramentas/modelo/planta_arquitetura.py "Construção Torres Vedras/desenhos/projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx" --folha 1 --regiao 120 192 215 258 --escala 200 --saida "Construção Torres Vedras/modelos/casa/planta_paredes.json"`.
