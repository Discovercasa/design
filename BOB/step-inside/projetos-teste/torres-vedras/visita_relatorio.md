# Modelo de visita · Torres Vedras · casa no lote

**Resultado: WARNING**

- materiais provisórios: mapeados a partir do sistema construtivo até chegar a lista oficial
- 36 choques entre peças de madeira > 8 mm no modelo de produção (verificar.py)
- implantação: cota_pavimento INFERRED
- implantação: plataforma INFERRED
- terreno existente entre -0,68 e 0,76 m da laje sob a casa: a plataforma (modelação simplificada) corrige-o no modelo
- terreno: WARNING

Gerado por `step-inside/ferramentas/visita/visita.py` a partir de `visita.json`. O modelo de visita fica só no PC (`_trabalho/step-inside/<obra>/visita/`): tem a posição real da casa.

## O que se reutilizou

- Modelo de produção: `Construção Torres Vedras/modelos/casa/Casa_TorresVedras.blend` (gerado por `ferramentas/modelo/construir_casa.py`, aberto sem o mudar).
- Fontes da Fase 1: `fontes.json` (dimensões, paredes e aberturas com a origem de cada valor).
- Choques da madeira: `ferramentas/modelo/verificar.py`.

## Coleções semânticas

| Coleção | Objetos | Na visita |
|---|---|---|
| ARCH_CEILINGS | 40 | sim |
| ARCH_FLOORS | 8 | sim |
| ARCH_FOUNDATION | 1 | sim |
| ARCH_LABELS | 8 | não (fica no ficheiro) |
| ARCH_OPENINGS | 50 | sim |
| ARCH_PERGOLA | 4 | sim |
| ARCH_ROOF | 116 | sim |
| ARCH_WALLS_EXT | 24 | sim |
| ARCH_WALLS_INT | 66 | sim |
| STRUCT_TIMBER | 880 | não (fica no ficheiro) |

Cada objeto tem `si_id` = `<coleção>/<nome do objeto>` (os nomes vêm dos desenhos e não mudam), `si_categoria`, `si_colecao_producao` e `si_material`.

## Implantação

| Campo | Valor | Estado | Método | Nota |
|---|---|---|---|---|
| posicao | só no PC | CONFIRMED | geometria | paredes do modelo ajustadas às tramas das paredes da planta: 154 de 163 pontos sobre as paredes (mediana 0,001 m, p90 0,038 m); a segunda orientação só tem 79 |
| rotacao_graus | 317,86 | CONFIRMED | geometria | eixo X do modelo medido a partir do eixo das abcissas do sistema de coordenadas |
| cota_pavimento | 117,50 | INFERRED | texto | cota do pavimento acabado do rés do chão (±0,00) lida nas cotas da proposta; também há '117.48' junto da casa (exterior?): confirmar |
| plataforma | margem_m 1,50, cota 117,48 | INFERRED | geometria | o levantamento é de antes da obra (março de 2024): à volta da casa o terreno fica plano à cota exterior desenhada, numa faixa de 1,5 m (modelação aproximada; a casa já está construída: confirmar com as fotos) |
| pavimento_acima_laje | 0,01 | CONFIRMED | calculo | medido no modelo: topo do pavimento acabado do rés do chão sobre o topo da laje |

## Verificações

- **Dimensões:** estrutura do modelo 17,500 × 10,999 m; fontes 17,501 × 11,000 m (diferença 0,001 m). Contorno acabado 17,632 × 11,132 m.
- **Malhas:** 309 objetos visíveis; abertas 0, normais para dentro 0, repetidos 0.
- **Aberturas:** 19 das fontes procuradas no modelo (raios horizontais através da parede, de 0,3 a 2,0 m acima do piso); fechadas: 0. Controlo: 14 troços de parede cheia, vistos como abertos: 0.
- **Choques da madeira** (verificar.py, > 8 mm): 36 em 736 peças — Prumo x Prumo: 18, Amarração x Viga: 10, Amarração x Amarração: 5, PI x PI: 3.
- **Terreno existente sob a casa** (antes da plataforma): entre -0,68 e 0,76 m da laje; acima do pavimento em 20 % da área.
- **Casa e terreno** (625 pontos sob a casa): terreno entre -0,03 e -0,00 m da laje; acima do pavimento em 0 % da área.
- **Plataforma:** terreno plano dentro do contorno da plataforma (124 vértices do terreno ajustados).

## Materiais (catálogo comum `MAT_*`)

Os materiais de produção foram trocados pelos do catálogo comum (`step-inside/materiais/catalogo.json`, mapeamento `mapeamentos/discovercasa.json`). Estados dos mapeamentos usados: INFERRED 1112.

| ID | Objetos |
|---|---|
| `MAT_BOARD_OSB` | 25 |
| `MAT_CONCRETE_SLAB` | 1 |
| `MAT_DOOR_GARAGE_SECTIONAL__RAL7016` | 1 |
| `MAT_FLOOR_VINYL_WOOD` | 8 |
| `MAT_FRAME_ALUMINIUM__RAL7016` | 19 |
| `MAT_GLASS_CLEAR` | 6 |
| `MAT_GLASS_FROSTED` | 2 |
| `MAT_INSULATION_MINERAL_WOOL` | 58 |
| `MAT_INT_PLASTER_PAINTED__WHITE` | 27 |
| `MAT_MEMBRANE_BREATHER` | 17 |
| `MAT_METAL_FLASHING__RAL7016` | 42 |
| `MAT_METAL_GALVANIZED` | 24 |
| `MAT_METAL_GUTTER__DARK_GREY` | 7 |
| `MAT_ROOF_SANDWICH_TRAPEZOIDAL__RAL8004` | 37 |
| `MAT_ROOF_TILE_CERAMIC__TERRACOTTA` | 1 |
| `MAT_TIMBER_STRUCTURE` | 803 |
| `MAT_WOOD_CLADDING__DOUGLAS_BROWN` | 17 |
| `MAT_WOOD_CLADDING__PINE_NATURAL` | 17 |
| `MAT_LANDSCAPE_SOIL` | 1 |

**Sem correspondência:** Etiqueta (ARCH_LABELS, 8)

## Ficheiros (só no PC)

- `visita.blend` (coleções VISITA > SITE / HOUSE), `visita.glb` (o que está visível), `preview.png`.
