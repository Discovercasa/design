# Modelo de visita · Sobral · Casa Tipo 1 no lote P

**Resultado: WARNING**

- implantação: cota_pavimento INFERRED
- implantação: rotacao_graus INFERRED
- implantação: plataforma INFERRED
- terreno existente entre 0,89 e 2,55 m da laje sob a casa: a plataforma (modelação simplificada) corrige-o no modelo
- terreno: WARNING

Gerado por `step-inside/ferramentas/visita/visita.py` a partir de `visita.json`. O modelo de visita fica só no PC (`_trabalho/step-inside/<obra>/visita/`): tem a posição real da casa.

## O que se reutilizou

- Modelo de produção: `Construção Sobral/modelos/tipo1/Casa_Tipo1_Estrutura_Madeira.blend` (gerado por `ferramentas/modelo/construir_casa.py`, aberto sem o mudar).
- Fontes da Fase 1: `fontes.json` (dimensões, paredes e aberturas com a origem de cada valor).
- Choques da madeira: `ferramentas/modelo/verificar.py`.

## Coleções semânticas

| Coleção | Objetos | Na visita |
|---|---|---|
| ARCH_CEILINGS | 58 | sim |
| ARCH_FLOORS | 26 | sim |
| ARCH_FOUNDATION | 3 | sim |
| ARCH_LABELS | 12 | não (fica no ficheiro) |
| ARCH_OPTIONS | 24 | não (fica no ficheiro) |
| ARCH_ROOF | 33 | sim |
| ARCH_WALLS_EXT | 16 | sim |
| ARCH_WALLS_INT | 81 | sim |
| STRUCT_TIMBER | 705 | não (fica no ficheiro) |

Cada objeto tem `si_id` = `<coleção>/<nome do objeto>` (os nomes vêm dos desenhos e não mudam), `si_categoria`, `si_colecao_producao` e `si_material`.

## Implantação

| Campo | Valor | Estado | Método | Nota |
|---|---|---|---|---|
| canto | só no PC | CONFIRMED | texto | canto NO do contorno da casa P: coordenadas escritas no desenho; confere com a quadrícula da folha a 0,23 m (posição do rótulo) |
| cota_pavimento | 223,88 | INFERRED | texto | cota com seta dentro do contorno da casa, lida como a do pavimento acabado do rés do chão |
| rotacao_graus | 0,00 | INFERRED | inferencia | o contorno da casa é um retângulo alinhado com a quadrícula (lado maior E-O, como o modelo); falta confirmar se a casa está virada como no desenho do engenheiro (0°) ou rodada 180° |
| pavimento_acima_laje | 0,16 | CONFIRMED | calculo | pavimento acabado do rés do chão a Z 0,16 sobre o topo da laje (modelo DiscoverCasa) |
| contorno_desenho_m | 10,02 × 6,25 | CONFIRMED | geometria | contorno exterior acabado da casa na implantação |
| plataforma | area_m2 189,6, vertices 8, cota laje + 0,00 m | INFERRED | geometria | modelação simplificada (folha 4): o lote P fica plano à cota do topo da laje dentro do contorno desenhado à volta da casa; os muros e taludes da modelação ainda não estão no modelo |

## Verificações

- **Dimensões:** estrutura do modelo 9,861 × 6,110 m; fontes 9,860 × 6,110 m (diferença 0,001 m). Contorno acabado 10,011 × 6,261 m; contorno da implantação 10,020 × 6,255 m (diferença 0,009 m).
- **Malhas:** 217 objetos visíveis; abertas 0, normais para dentro 0, repetidos 0.
- **Aberturas:** 19 das fontes procuradas no modelo (raios horizontais através da parede, de 0,3 a 2,0 m acima do piso); fechadas: 0. Controlo: 40 troços de parede cheia, vistos como abertos: 0.
- **Choques da madeira** (verificar.py, > 8 mm): 0 em 364 peças.
- **Terreno existente sob a casa** (antes da plataforma): entre 0,89 e 2,55 m da laje; acima do pavimento em 100 % da área.
- **Casa e terreno** (625 pontos sob a casa): terreno entre -0,02 e 0,01 m da laje; acima do pavimento em 0 % da área.
- **Plataforma:** terreno plano dentro do contorno da plataforma (64 vértices do terreno ajustados).

## Ficheiros (só no PC)

- `visita.blend` (coleções VISITA > SITE / HOUSE), `visita.glb` (o que está visível), `preview.png`.
