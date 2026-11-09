# Fase 3 · Materiais e exportação (em curso)

Tarefas do hub 62 a 65 e 156. Especificação §3.4, §4.2 a §4.4 e §13 Fase 3.

**Critério de saída:**
- exportação determinística;
- sem materiais nem recursos críticos em falta;
- materiais com texturas PBR reais, prontos para o AR realista (pedido de 2026-11-07).

## Princípio: um catálogo comum e um mapeamento por construtor

O utilizador (2026-11-09): «se formos vender a terceiros precisamos de uma listagem comum para construções diferentes da Discovercasa».

| Ficheiro | O que é |
|---|---|
| `step-inside/materiais/catalogo.json` | **Catálogo comum**: IDs técnicos estáveis, independentes do construtor e do nome mostrado ao cliente (§3.4). Para cada um: categoria, nome PT/EN, valores PBR e textura prevista. |
| `step-inside/materiais/mapeamentos/<construtor>.json` | **Os produtos de um construtor** ligados aos IDs do catálogo. Pode trazer a cor do próprio produto, estado (CONFIRMED / INFERRED…), fonte e nota. |
| `step-inside/ferramentas/materiais/materiais.py` | Valida o catálogo e os mapeamentos e resolve cada produto no ID final e nos valores PBR. |

**IDs:**
- `MAT_<MESTRE>` é o material mestre, por exemplo `MAT_FRAME_ALUMINIUM`.
- Uma cor ou acabamento é uma variante: `MAT_<MESTRE>__<VARIANTE>`, por exemplo `MAT_FRAME_ALUMINIUM__RAL7016`.
- No Unreal fica um *master material* com instâncias. No GLB e no USDZ fica um material por variante.

**Um construtor novo** precisa só de um `mapeamentos/<construtor>.json` e de `"construtor": "<nome>"` no `visita.json`.
Um produto sem correspondência aparece no relatório do modelo de visita e pede revisão.

**DiscoverCasa:** o mapeamento é **provisório** (INFERRED), feito a partir de `ferramentas/modelo/sistema_construtivo.json`.
- O utilizador vai associar a lista oficial de materiais durante a semana de 2026-11-09.
- Cada entrada passa então a CONFIRMED, com o produto oficial como fonte.

## Estado (2026-11-09)

- **Catálogo:** 45 materiais mestre em 8 categorias:
  - fachadas;
  - coberturas, remates e drenagem;
  - vãos;
  - pavimentos;
  - interiores;
  - estrutura e camadas escondidas;
  - terreno e arranjos exteriores;
  - provisório.
- **Mapeamento DiscoverCasa:** 44 produtos ligados a 33 IDs.
- **Modelos de visita:** os dois (Sobral Tipo 1 e Torres Vedras) já trocam os materiais de produção pelos do
  catálogo. Cada objeto guarda:
  - `si_mat_id`;
  - `si_material`, o nome de produção;
  - o material, com `si_mat_id`, `si_mestre` e `si_variante`.
- **Falhas:** nenhum material visível ficou sem correspondência. Só as etiquetas das divisões, que não entram na
  visita, ficaram de fora.

## Texturas (2026-11-09, autorizado: «Sim, descarrega»)

- **Origem:** 16 texturas gratuitas **CC0** do ambientCG, em 2K JPG (359 MB), para 26 materiais do catálogo.
  - Escolhidas limpas e modernas, sem envelhecimento.
  - Cada material tem no catálogo a fonte, o *asset*, a licença, o tamanho real (`tile_m`) e a pasta local.
- **Onde ficam:** as imagens ficam **só no PC**, em `_trabalho/step-inside/texturas/` (fora do Git). Noutro PC:
  `python step-inside/ferramentas/materiais/texturas.py` volta a descarregá-las, verifica o tamanho anunciado e só
  extrai imagens.
- **Três usos:**
  - `cor`: a cor da própria textura (telha, madeira, terreno);
  - `tingir`: a textura levada à cor do catálogo ou da variante, por exemplo reboco branco ou ripado de pinho ou de
    Douglas. Como o GLB e o USDZ não deixam clarear uma textura no material, a cópia tingida é gravada como imagem
    (`texturas/derivadas/`);
  - `relevo`: a cor lisa do produto com o relevo (normal) e a rugosidade da textura. Serve para metais lacados e
    painéis RAL, e a cor RAL fica exata.
- **UVs à escala real:** cada objeto recebe UVs à escala real, por projeção em caixa, em metros a dividir por
  `tile_m`. São medidas no referencial da casa, para a textura continuar de um objeto para o seguinte. O terreno usa
  as coordenadas do terreno.
- **Resultado nos dois modelos de visita:**
  - pré-visualização em EEVEE com sol;
  - GLB de cerca de 110 MB, com as texturas 2K embebidas. O AR (Fase 7) terá de baixar para cerca de 10 MB.
- **Provisório:** as texturas da DiscoverCasa passam às fotos dos produtos reais quando houver (tarefa 156). O terreno
  ainda mostra a repetição da textura e está claro demais (a afinar na Fase 7).

## A seguir

1. Fotos dos materiais reais da DiscoverCasa para substituir as CC0.
2. **Predefinições de exportação** (tarefa 63): FBX para o Unreal, GLB para Android e USDZ para iPhone, em metros, com
   origem e eixos fixos.
3. **`manifest.json`** (tarefa 64), com os campos da §4.3:
   - IDs do projeto e da versão;
   - hash do `.blend`;
   - versões;
   - unidades e sistema de coordenadas;
   - transformação da origem;
   - para cada ficheiro: SHA-256, tamanho, IDs de material e finalidade;
   - avisos;
   - estado da validação;
   - origem do terreno.
4. **Reimportação e comparação visual** (tarefa 65).
