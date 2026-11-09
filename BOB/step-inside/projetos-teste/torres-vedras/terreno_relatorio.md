# Terreno · Torres Vedras · lote da casa

**Resultado: WARNING**

- precisao: em falta
- pontos_controlo: em falta

Gerado por `step-inside/ferramentas/terreno/terreno.py` a partir de `terreno.json`. Só números e estados: as coordenadas reais e a origem local ficam só no PC (o levantamento localiza o terreno do cliente).

## Campos do terreno (contrato da Fase 1)

| Campo | Valor | Estado | Método | Nota |
|---|---|---|---|---|
| fonte | DXF: Levantamento topográfico F00.0.dxf | CONFIRMED | texto |  |
| crs | EPSG:3763 | CONFIRMED | texto | declarado no próprio ficheiro |
| datum_vertical | altitudes ortométricas (ligação à rede GNSS com correção ao geóide) | CONFIRMED | texto | a correção ao geóide dá altitudes ortométricas (datum altimétrico nacional, Cascais); o nome do modelo de geóide não está escrito |
| unidade_horizontal | m | CONFIRMED | texto | o DXF não tem $INSUNITS; os rótulos GNSS e o sistema dizem metros |
| unidade_vertical | m | CONFIRMED | texto |  |
| limite_lote | area_m2 1665, perimetro_m 162, vertices 19, coordenadas só no PC (terreno_local.json) | INFERRED | geometria | linha tracejada «LIMITE DO TERRENO» reconstruída a partir dos traços |
| data_levantamento | março de 2024 | CONFIRMED | texto | as folhas do arquiteto são de junho e julho de 2024 |
| precisao | — | MISSING | nenhum | precisão não declarada pelo topógrafo; ver a coerência medida no relatório |
| pontos_controlo | — | MISSING | nenhum | sem marcos nem estações com coordenadas; verificação interna: 92 dos 93 pontos GNSS com E/N/h escritos (camada GPS) coincidem com os pontos 3D do desenho a menos de 1 cm |

## Leitura das fontes

- **Levantamento topográfico F00.0.dxf** (DXF): entidades {'TEXT': 372, 'LWPOLYLINE': 13, 'POINT': 278, 'POLYLINE': 160}, pontos 278, curvas 0, quebras 0, linhas_2d 173, faces 0, rotulos_numericos 0, copias_do_levantamento 3, gnss_escritos 93, gnss_que_coincidem 92, gnss_junto_da_copia_usada 83, pontos_na_copia_usada 92, curvas_2d_usadas 54
  - aviso: $INSUNITS ausente ou 0: o DXF não diz a unidade
  - aviso: o ficheiro tem 3 cópias do levantamento; usada a que tem à volta os pontos GNSS escritos que coincidem com os pontos 3D (83 de 92), com 15 m à volta do limite (92 de 278 pontos)

## Superfície «Terreno existente (levantamento topográfico GNSS)»

- 92 pontos cotados (0 excluídos por decisão), 54 curvas de nível 2D: 0 com cota pelo rótulo, 54 pelo terreno dos pontos, 0 retiradas por incoerência, 54 usadas.
- Equidistância: curvas mestras 1,00 m (rótulos), curvas 0,20 m (razão de comprimentos —).
- Malha: 4073 vértices, 8009 triângulos, 2672 m² em planta, 81 × 83 m, cotas 115,30 a 121,52 m, inclinação mediana 7,2° (p95 23,9°). Faces viradas para baixo: 0.

| Verificação | n | média | mediana |abs| | p95 |abs| | máx |abs| |
|---|---|---|---|---|---|
| Cada ponto previsto pelos vizinhos (validação cruzada, 5 grupos) | 81 | -0,00 | 0,07 | 0,33 | 0,55 |
| Pontos contra as curvas de nível (duas fontes independentes) | 79 | 0,00 | 0,03 | 0,09 | 0,12 |

## Como ler

- **PASS**: medido e georreferenciado com o sistema confirmado. **WARNING**: utilizável como terreno aproximado (falta confirmar o sistema, o datum, a data ou os pontos de controlo). **NEEDS_HUMAN_REVIEW**: há pontos ou rótulos que uma pessoa tem de ver no desenho. **FAIL**: não serve.
- Uma imagem, foto ou PDF sem escala nunca dá um terreno medido (especificação §19.4).
