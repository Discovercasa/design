# Fase 2 · Modelo Blender e terreno

Tarefas do hub 57 a 61. Especificação §13 Fase 2, §14.1 e §19.4.

**Objetivo:**
- juntar a geração da casa no Blender (a que já existe) com o terreno do levantamento;
- validar unidades, coordenadas e cotas;
- produzir um modelo de visita com coleções semânticas e um relatório PASS / WARNING / NEEDS_HUMAN_REVIEW / FAIL.

## Comandos

Correm a partir de `BOB/`, por esta ordem:

```bash
python step-inside/ferramentas/terreno/terreno.py step-inside/projetos-teste/<obra>/terreno.json
python step-inside/ferramentas/visita/visita.py  step-inside/projetos-teste/<obra>/visita.json
python -m unittest discover -s step-inside/tests
```

Os dois comandos usam o Blender (≥ 4.4) em segundo plano. No Sobral, o terreno demora cerca de 1,5 min e a visita cerca de 15 s.

**Código de saída:**
- 0 = PASS ou WARNING;
- 2 = NEEDS_HUMAN_REVIEW;
- 1 = FAIL.

## O que se reutiliza

| Já existia | Uso na Fase 2 |
|---|---|
| `ferramentas/modelo/construir_casa.py` e o `.blend` de produção | O modelo de visita abre esse `.blend` e não o reconstrói nem o altera. |
| `ferramentas/modelo/verificar.py` | Verifica os choques entre peças de madeira. |
| `ferramentas/modelo/estrutura_dc.py` | Gera a estrutura DiscoverCasa, onde estão os choques a verificar. |
| `ferramentas/dwfx/leitor.py` | Lê o texto e os traços das folhas DWFx: levantamento e implantação. |
| `step-inside/ferramentas/fontes/` (Fase 1) | Dá os campos com estado, método e fonte, e o `fontes.json` (dimensões, paredes, aberturas). |

## Entrada 1: `terreno.json` (declaração do terreno)

Vai para o Git e **não tem coordenadas**. Diz onde estão as fontes e como se leem, e regista os factos declarados por
pessoas.

```json
{
 "obra": "sobral-tipo1",                       // pasta de saída
 "obra_pasta": "Sobral",                       // procura em "Construção <obra_pasta>/desenhos/"
 "nome": "…",
 "superficies": [{
   "id": "existente", "nome": "Terreno existente (levantamento topográfico)",
   "fontes": [{ "ficheiro": "…dwfx", "folha": 2, "local": "…",
     "pontos_cotados": {"altura_texto": [1.6, 1.75], "angulo": 0, "intervalo_z": [150, 400],
                        "posicao": "ponto_decimal"},          // "origem" | "centro" | "ponto_decimal"
     "rotulos_curvas": {"altura_texto": [1.75, 1.9]},          // valores escritos nas curvas mestras
     "curvas": [{"stroke": "#808080", "sw": 0.08, "papel": "intermedia"},
                {"stroke": "#725639", "sw": 0.08, "papel": "mestra"}],
     "limite": {"fill": "#000000", "tracejado": true} }],
   "excluir_pontos": [],                       // índices que uma pessoa decidiu tirar (depois de ver o desenho)
   "equidistancia": {},                        // {"mestras": 2.5, "curvas": 0.5} se se quiser fixar
   "incerteza_xy_m": 1.0 }],                   // incerteza da posição dos pontos (rótulos a 1:500 ≈ 1 m)
 "metadados": {                                // factos declarados: {"valor","estado","metodo","fonte","nota"}
   "crs": {"valor": "EPSG:3763", "estado": "CONFIRMED", "metodo": "utilizador", "fonte": {…}} }
}
```

**DXF de um levantamento** (Torres Vedras):
- `camadas`: só as camadas que interessam (pontos, curvas, limite e rótulos GNSS);
- `curvas_camadas`: `{"CVD": "mestra", "CV": "intermedia"}`. Só as linhas 2D destas camadas são curvas de nível;
  muros, caminhos e edifícios também são linhas 2D;
- `limite_camadas`: as polilinhas fechadas destas camadas são o limite do lote;
- `escolher_copia: true` e `margem_m`: quando o ficheiro tem várias cópias do levantamento (uma por folha), usa-se a
  que tem à volta os pontos GNSS escritos que coincidem com os pontos 3D. Fica o que está até `margem_m` do limite,
  mais os pontos GNSS um pouco mais longe;
- `equidistancia`: quando as curvas não têm rótulos, declara-se a da legenda.

**Outros formatos** de fonte: em vez de `folha` e das regras DWFx, indica-se só o ficheiro. Opções:
- `colunas` (XYZ sem cabeçalho);
- `camadas` (DXF: lista de nomes ou expressões regulares);
- `passo` (DEM denso);
- `rotulos_como_pontos: true` (DXF com as cotas escritas em texto no próprio ponto).

| Formato | Leitor | O que dá | Regras |
|---|---|---|---|
| DWFx (folha de levantamento) | `ler_dwfx` | Pontos cotados escritos em texto, curvas 2D, limite tracejado | Georreferência pela quadrícula M/P da folha (cruzes e rótulos). Sem quadrícula, coordenadas locais (precisa de `escala`). |
| XYZ / CSV / TXT | `ler_xyz` | Pontos | Deteta o separador e a vírgula decimal. Com 4 colunas sem cabeçalho assume `id x y z` e avisa. |
| LandXML | `ler_landxml` | Pontos, superfícies (faces), linhas de quebra, curvas, parcelas | A ordem do LandXML é **norte, este, cota**. A unidade e o CRS vêm do ficheiro. |
| DXF ASCII | `ler_dxf` | Pontos 3D, polilinhas 3D, curvas com elevação, faces 3D, rótulos GNSS (`E=`, `N=`, `h=`), o EPSG escrito numa legenda | **Uma linha 2D sem cota nunca dá alturas** (§19.4); uma polilinha «3D» com todas as cotas a zero é 2D. Texto numérico só se for declarado. O DXF binário é recusado. |
| ESRI ASCII grid (`.asc`) | `ler_asc` | DEM em grelha | Sem unidade nem CRS: declarar. |
| GeoTIFF / DEM | — | — | CONVERT_REQUIRED: converter para `.asc` ou XYZ. |
| LAS / LAZ | — | — | UNSUPPORTED (nuvem de pontos). |
| DWG | — | — | CONVERT_REQUIRED: converter para DXF com o ODA File Converter (gratuito; extraído no PC da empresa a 2026-11-08 em `%LOCALAPPDATA%\Programs\ODAFileConverter`): `ODAFileConverter.exe <pasta DWG> <pasta DXF> ACAD2018 DXF 0 1 "*.DWG"`. Os DXF ficam em `desenhos/` (`*.dxf` está no `.gitignore`). |

## Como se faz o terreno (`terreno/blender_tin.py`)

1. **Triangulação de Delaunay** dos pontos (`mathutils.geometry.delaunay_2d_cdt`).
2. **Validação cruzada** em 5 grupos. Cada ponto é previsto pelos outros. Um ponto muito longe do previsto é um
   **pico**: rótulo mal lido, ou um ponto que não é do chão.
3. **Curvas de nível 2D.**
   - As mestras recebem a cota do rótulo que está em cima delas (≤ 1 m).
   - A equidistância das mestras sai dos rótulos (2,5 m no Sobral).
   - A equidistância das curvas sai da razão entre os comprimentos das intermédias e das mestras (4 intermédias, 0,5 m).
   - As restantes curvas recebem a cota pelo terreno dos pontos e das já cotadas, arredondada à equidistância, só
     quando não há ambiguidade.
   - Cada curva é depois testada contra todas as outras: se ficar a mais de meia equidistância, sai.
4. **Pontos contra curvas.** São duas fontes independentes do mesmo chão.
   - Um ponto que discorda **dos vizinhos e das curvas**, para lá do que a inclinação explica, é afastado da superfície
     e listado para alguém ver.
   - Um pico que as curvas confirmam é terreno real e fica.
5. **Superfície final:** pontos e curvas como arestas obrigatórias. Aparam-se os triângulos compridos da borda. Todas
   as faces ficam viradas para cima.

**Coordenadas:** tudo é passado para uma origem local (grelha de 10 m), porque o Blender guarda floats de 32 bits. A
origem real fica só no PC.

## Entrada 2: `visita.json` (modelo de visita)

```json
{
 "obra": "…", "obra_pasta": "…", "nome": "…",
 "casa": {"config": "Construção <obra>/modelos/<tipo>/config.json"},
 "fontes": "step-inside/projetos-teste/<obra>/fontes.json",
 "terreno": {"declaracao": ".../terreno.json", "superficie": "existente"},
 "implantacao": {
   "lote": "P", "canto": "NO",                     // canto do contorno ACABADO da casa (NO, SO, NE, SE)
   "coordenadas": {"ficheiro": "…", "folha": 4, "perto_mm": [x, y]},  // rótulos …mM / …mP lidos no PC
   "cota": {"ficheiro": "…", "folha": 4, "perto_mm": [x, y]},         // cota do pavimento
   "rotacao_graus": {"valor": 0.0, "estado": "INFERRED", …},
   "pavimento_acima_laje": {"valor": 0.16, "estado": "CONFIRMED", …},
   "contorno_desenho_m": {"valor": [10.02, 6.255], "estado": "CONFIRMED", …} },
 "plataforma": {"ficheiro": "…", "folha": 4, "contem_mm": [x, y], "estilo": {"stroke": "#000000", "sw": 0.08},
                "acima_da_laje": 0.0, "nota": "…"},
 "chao_provisorio": {"z": 0.0, "tamanho": 60}       // só sem levantamento; nunca é apresentado como terreno
}
```

**Implantação pelo DXF** (`ajuste.py`): quando a proposta está desenhada nas coordenadas reais por cima do
levantamento, em vez de `coordenadas` / `cota` / `canto` usa-se:

```json
"implantacao": {"metodo": "ajuste_tramas_dxf", "ficheiro": "….dxf", "camada": "0_PROP.trama", "tipo_trama": "SOLID",
                "raio_m": 40, "area_max_m2": 60, "cota_pavimento": {"valor": 117.50, "estado": "INFERRED", …}},
"plataforma": {"tipo": "contorno_casa", "margem_m": 1.5, "cota": {"valor": 117.48, …}, "nota": "…"}
```

**Como funciona o ajuste:**
1. As tramas das paredes (poché) à volta do lote dão pontos sobre as faces das paredes.
2. Procura-se a rotação e a posição que põem mais pontos em cima das paredes do modelo (`fontes.json`):
   - primeiro pelo eixo do retângulo mínimo;
   - depois pesquisa grossa e fina da posição;
   - por fim um afinamento do ângulo e da posição sobre as faces.
3. Fica CONFIRMED com ≥ 80 % dos pontos nas paredes, mediana ≤ 5 cm e uma orientação claramente melhor do que as
   outras. Caso contrário fica NEEDS_HUMAN_REVIEW.
4. A altura do pavimento sobre a laje é medida no próprio modelo.

### Coleções semânticas (`blender_visita.py`)

| Coleção de produção | Coleção da visita | Na visita |
|---|---|---|
| 0 Fundação | `ARCH_FOUNDATION` | sim |
| 1 Estrutura de madeira | `STRUCT_TIMBER` | não (fica no ficheiro) |
| 2 Paredes, camadas exteriores (opção visível) | `ARCH_WALLS_EXT` | sim |
| 2 Opções de acabamento escondidas | `ARCH_OPTIONS` | não |
| 3 Paredes, camadas interiores | `ARCH_WALLS_INT` | sim |
| 4 Pavimentos | `ARCH_FLOORS` | sim |
| 5 Tetos | `ARCH_CEILINGS` | sim |
| 6 Cobertura | `ARCH_ROOF` | sim |
| 7 Caixilharia | `ARCH_OPENINGS` | sim |
| 8 Pérgola | `ARCH_PERGOLA` | sim |
| 9 Etiquetas | `ARCH_LABELS` | não |
| Terreno, limite do lote | `SITE_TERRAIN`, `SITE_LIMIT` | sim |

**Propriedades** de cada objeto:
- `si_id = "<coleção>/<nome>"`: os nomes vêm dos desenhos e não mudam entre gerações;
- `si_categoria`;
- `si_colecao_producao`;
- `si_material`.

A Fase 3 liga `si_material` aos IDs `MAT_*`. A casa fica pendurada num único Empty, `HOUSE_ROOT`, colocado no lote.

### Verificações e resultado

| Verificação | Como | Dá |
|---|---|---|
| Dimensões | Caixa da estrutura das paredes contra `fontes.json` (comprimento e profundidade) | FAIL se > 2 cm de um valor CONFIRMED |
| Contorno da implantação | Contorno acabado do modelo contra o contorno do desenho | WARNING se > 5 cm |
| Normais e malhas | Volume com sinal (normais para fora), arestas abertas | FAIL / WARNING |
| Duplicados | Mesma caixa, mesmo número de vértices e mesmo material | WARNING |
| Aberturas | Raios horizontais através de cada parede, de 0,3 a 2,0 m acima do piso, em 3 pontos do vão; só contam as paredes (o vidro e os caixilhos estão lá de propósito) | NEEDS_HUMAN_REVIEW se um vão das fontes estiver fechado |
| Controlo do teste | O mesmo teste num troço de parede cheia tem de dar fechado. Paredes baixas só abaixo da sua altura (alçado do engenheiro). | NEEDS_HUMAN_REVIEW se falhar |
| Choques da madeira | `verificar.py` (> 8 mm) | WARNING (problema do modelo de produção) |
| Casa e terreno | Terreno sob a casa contra a laje, antes e depois da plataforma | WARNING |
| Terreno | Resultado de `terreno.py` | WARNING / NEEDS_HUMAN_REVIEW |

## Saídas e privacidade

| Ficheiro | Onde | Git |
|---|---|---|
| `terreno_resumo.json`, `terreno_relatorio.md` | `projetos-teste/<obra>/` | sim: só números e estados |
| `visita_resumo.json`, `visita_relatorio.md` | `projetos-teste/<obra>/` | sim: só números e estados |
| `terreno_local.json` (origem e pontos em coordenadas reais), `terreno.blend`, `tin.json` | `_trabalho/step-inside/<obra>/terreno/` | **não** |
| `visita.blend`, `visita.glb`, `preview.png` | `_trabalho/step-inside/<obra>/visita/` | **não** |

Um levantamento georreferenciado localiza o terreno do cliente. Fica no PC, como os desenhos.

## Resultados nos projetos de teste (2026-11-08)

**Sobral, terreno: WARNING** (terreno aproximado).
- **Georreferência:** quadrícula M/P lida em 14 cruzes, resíduo 4 mm, escala 1:500.
- **Pontos:** 450 cotas lidas. Pela convenção portuguesa, o **ponto decimal** marca o ponto medido. A escolha foi
  verificada contra as curvas: mediana de 0,04 m com o ponto decimal, 0,28 m com a origem do texto.
- **Curvas de nível:** 400, com equidistância de 0,5 m e mestras de 2,5 m; 331 usadas.
- **Coerência entre as duas fontes:**
  - pontos contra curvas: mediana 0,04 m, p95 0,82 m;
  - pontos entre si: mediana 0,39 m.
- **Metadados:**
  - CRS: PT-TM06/ETRS89 provável (INFERRED);
  - datum de Cascais: provável (INFERRED);
  - data do levantamento, precisão e pontos de controlo: MISSING.
- 10 pontos discordam de uma verificação e mantêm-se.

**Sobral, visita (Casa Tipo 1 no lote P): WARNING.**
- **Implantação:** canto NO com as coordenadas escritas na folha 4, cota de pavimento 223,88 e rotação 0°. Cota e
  rotação são INFERRED.
- **Dimensões:**
  - estrutura 9,861 × 6,110 m, contra 9,860 × 6,110 m nas fontes;
  - contorno acabado 10,011 × 6,261 m, contra 10,020 × 6,255 m na implantação.
- **Aberturas:** as 19 estão abertas; o controlo deu 40 paredes cheias fechadas.
- **Malhas e madeira:** 0 normais invertidas, 0 duplicados, 0 choques da madeira.
- **Terreno:** o terreno existente fica 0,9 a 2,6 m acima da laje. A plataforma da folha 4 (189,6 m²) corrige isto no
  modelo.

**Torres Vedras, terreno: WARNING** (só faltam a precisão e os pontos de controlo, que não estão escritos).
- **Conversão:** o DWG do levantamento foi convertido para DXF com o ODA File Converter.
- **Metadados confirmados pelo próprio ficheiro:**
  - sistema ETRS89/PT-TM06 (EPSG:3763);
  - ligação à rede GNSS com correção ao geóide (altitudes ortométricas);
  - levantamento de março de 2024;
  - curvas de 0,20 m e mestras de 1,00 m.
- **Três cópias:** o ficheiro tem três cópias do levantamento, uma por folha, a cerca de 100 m umas das outras.
  - Foi usada a cópia nas coordenadas reais.
  - 92 dos 93 pontos GNSS escritos coincidem com os pontos 3D a menos de 1 cm.
- **Dados usados:** 92 pontos e 54 curvas (53 com cota).
- **Coerência:**
  - pontos contra curvas: mediana 0,03 m, p95 0,09 m;
  - pontos entre si: mediana 0,07 m.

**Torres Vedras, visita (casa no lote): WARNING.**
- **Implantação:** as paredes do modelo foram ajustadas às tramas das paredes da proposta, desenhada no levantamento.
  - 154 de 163 pontos ficam sobre as paredes (mediana 1 mm, p90 4 cm), com rotação de 317,86°;
  - a outra orientação só tem 79 pontos, por isso posição e rotação ficam CONFIRMED.
- **Cotas:** pavimento a 117,50 (INFERRED). O vinílico assenta na laje, com 5 mm medidos no modelo.
- **Dimensões:** estrutura 17,500 × 10,999 m, contra 17,501 × 11,000 m nas fontes.
- **Aberturas:** as 19 estão abertas; o controlo deu 14 paredes cheias fechadas.
- **Terreno:** o levantamento é de antes da obra. O terreno ia de 0,68 m abaixo a 0,76 m acima da laje sob a casa.
  Ficou uma faixa plana de 1,5 m à cota exterior 117,48 (aproximada).
- **Choques:** **36 choques de madeira** no modelo de produção (verificar.py). A maioria é Prumo × Prumo e na viga de
  amarração: são defeitos já conhecidos do construtor (hub, Construtor › «Corrigir defeitos geométricos conhecidos»,
  tarefas 137, 139 e 140).

## Em aberto

- **Torres Vedras:** confirmar a cota do pavimento (117,50) e a exterior (117,48), por exemplo com fotos da casa
  construída.
- **Sobral:** confirmar com o topógrafo o CRS, o datum, a data e a precisão do levantamento.
- **Sobral:** confirmar a orientação da casa no lote (0° como no desenho do engenheiro, ou 180°).
- **Modelação do terreno:** completar a modelação (muros, taludes, arruamentos da folha 4). Para já há só uma
  plataforma plana à volta da casa.
- **Torres Vedras:** os 36 choques de madeira resolvem-se no construtor (tarefas 137, 139 e 140 do hub), não no Step Inside.
- **Formatos sem leitor:** GeoTIFF e LAS só quando houver um ficheiro real para testar.
