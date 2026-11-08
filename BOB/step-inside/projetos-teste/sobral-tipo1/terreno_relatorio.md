# Terreno · Sobral · loteamento (Casa Tipo 1)

**Resultado: WARNING**

- existente: 10 pontos discordam de uma das verificações (mantidos)
- crs: INFERRED — terreno aproximado (posição relativa medida; georreferência por confirmar com o topógrafo)
- datum_vertical: INFERRED — terreno aproximado (posição relativa medida; georreferência por confirmar com o topógrafo)
- data_levantamento: em falta
- precisao: em falta
- pontos_controlo: em falta

Gerado por `step-inside/ferramentas/terreno/terreno.py` a partir de `terreno.json`. Só números e estados: as coordenadas reais e a origem local ficam só no PC (o levantamento localiza o terreno do cliente).

## Campos do terreno (contrato da Fase 1)

| Campo | Valor | Estado | Método | Nota |
|---|---|---|---|---|
| fonte | DWFx: SMA_012_arquitectura_pecas_desenhadas.dwfx, folha 2 | CONFIRMED | texto |  |
| crs | PT-TM06/ETRS89 (EPSG:3763), provável | INFERRED | inferencia | quadrícula M/P lida na folha (14 cruzes, resíduo 0,004 m, escala 1:500); compatível com Portugal continental em PT-TM06/ETRS89 (EPSG:3763) ou num sistema Hayford-Gauss antigo (Datum 73 / Datum Lisboa): confirmar com o topógrafo. O desenho não escreve o sistema. |
| datum_vertical | altitudes ortométricas (Marégrafo de Cascais), provável | INFERRED | inferencia | cotas entre 200,22 e 301,10 m, coerentes com altitudes em Portugal continental; o desenho não escreve o datum |
| unidade_horizontal | m | CONFIRMED | texto | rótulos da quadrícula em metros ('…mM', '…mP') e escala verificada |
| unidade_vertical | m | INFERRED | inferencia | cotas com 2 casas decimais e a gama de altitudes da região |
| limite_lote | area_m2 48505, perimetro_m 1225, vertices 1639, coordenadas só no PC (terreno_local.json) | INFERRED | geometria | linha tracejada «LIMITE DO TERRENO» reconstruída a partir dos traços |
| data_levantamento | — | MISSING | nenhum | o desenho não diz a data do levantamento (a data da folha é a do desenho de arquitetura) |
| precisao | — | MISSING | nenhum | precisão não declarada pelo topógrafo; ver a coerência medida no relatório |
| pontos_controlo | — | MISSING | nenhum | o desenho não mostra marcos nem estações do levantamento com coordenadas e cota |

## Leitura das fontes

- **SMA_012_arquitectura_pecas_desenhadas.dwfx**, folha 2 (DWFx): pontos_cotados 450, curvas_2d 400, vertices_curvas 8921, limites 1, posicao_do_ponto ponto_decimal
  - georreferência pela quadrícula: 14 cruzes, resíduo máximo 0,004 m, escala 1:500,0 × 1:500,0, rotação -0,000°

## Superfície «Terreno existente (levantamento topográfico)»

- 433 pontos cotados (0 excluídos por decisão), 400 curvas de nível 2D: 12 com cota pelo rótulo, 345 pelo terreno dos pontos, 26 retiradas por incoerência, 331 usadas.
- Equidistância: curvas mestras 2,50 m (rótulos), curvas 0,50 m (razão de comprimentos 4,17).
- Malha: 8303 vértices, 16314 triângulos, 55954 m² em planta, 410 × 277 m, cotas 200,22 a 301,10 m, inclinação mediana 13,2° (p95 29,5°). Faces viradas para baixo: 0.

| Verificação | n | média | mediana |abs| | p95 |abs| | máx |abs| |
|---|---|---|---|---|---|
| Cada ponto previsto pelos vizinhos (validação cruzada, 5 grupos) | 415 | 0,04 | 0,39 | 1,67 | 6,69 |
| Pontos contra as curvas de nível (duas fontes independentes) | 422 | 0,04 | 0,04 | 0,82 | 1,80 |

**Pontos mantidos que discordam de uma verificação:**

| Texto | Folha (mm) | Cota | Vizinhos dão | Diferença das curvas | Declive |
|---|---|---|---|---|---|
| 201.11 | [737.2, 62.3] | 201,11 | — | 1,38 | 0 % |
| 227.72 | [414.4, 139.1] | 227,72 | — | 1,76 | 19 % |
| 228.26 | [548.6, 317.8] | 228,26 | — | -1,56 | 47 % |
| 232.86 | [508.3, 360.1] | 232,86 | — | -1,78 | 12 % |
| 224.19 | [721.8, 411.7] | 224,19 | — | -1,45 | 9 % |
| 224.49 | [720.8, 422.6] | 224,49 | — | -1,69 | 8 % |
| 224.84 | [695.5, 425.2] | 224,84 | — | -1,16 | 7 % |
| 271.64 | [143.1, 455.4] | 271,64 | — | 1,81 | 29 % |
| 301.10 | [27.1, 488.2] | 301,10 | — | -1,11 | 0 % |
| 272.74 | [134.2, 506.6] | 272,74 | — | 1,74 | 43 % |

**Picos confirmados pelas curvas (terreno real):**

| Texto | Folha (mm) | Cota | Vizinhos dão | Diferença das curvas | Declive |
|---|---|---|---|---|---|
| 300.40 | [41.0, 484.2] | 300,40 | 295,41 | -1,01 | 64 % |
| 285.83 | [63.5, 488.7] | 285,83 | 292,52 | 1,33 | 35 % |
| 296.42 | [60.3, 517.5] | 296,42 | 292,73 | 0,56 | 21 % |

## Como ler

- **PASS**: medido e georreferenciado com o sistema confirmado. **WARNING**: utilizável como terreno aproximado (falta confirmar o sistema, o datum, a data ou os pontos de controlo). **NEEDS_HUMAN_REVIEW**: há pontos ou rótulos que uma pessoa tem de ver no desenho. **FAIL**: não serve.
- Uma imagem, foto ou PDF sem escala nunca dá um terreno medido (especificação §19.4).
