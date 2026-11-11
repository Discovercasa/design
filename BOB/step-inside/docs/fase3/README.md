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
- Confirmado em 2026-11-10: a lista oficial chega do Hub (tabelas `hub_*`, `#/materiais`); próximo passo: mapear cada MAT_* para um id de material do Hub.
- Cada entrada passa então a CONFIRMED, com o produto oficial como fonte.
- 2026-11-11: cada produto do mapeamento tem os seus `codigos` de produto da Listagem de material
  (`ferramentas/documentos/codigos.py`); pelo ficheiro `orcamentacao/ligacoes.json`, cada código chega ao material da
  lista oficial do Hub (27 de 43 produtos estão na lista; os outros dizem porquê). As entradas ficam INFERRED até a
  equipa confirmar as ligações na página da Orçamentação (`/orcamentacao/`). A lista do Hub não traz cores: a cor de
  cada produto continua a vir do sistema construtivo.

## Lista oficial e texturas dos produtos reais (2026-11-11)

O utilizador: «Fase 3 avança com as texturas reais dos materiais Discovercasa e com a Lista oficial de materiais que já
tens acesso... e depois para os interiores.»

- **Lista oficial → mapeamento** (tarefa 163): `python step-inside/ferramentas/materiais/oficial.py`.
  - Um produto passa a **CONFIRMED** quando todos os seus códigos da Listagem chegam a um material da lista oficial do
    Hub (`orcamentacao/ligacoes.json`) e o produto oficial é o que o modelo mostra. A fonte guarda só os ids do Hub
    (nunca nomes nem preços: o repositório é público).
  - Resultado: **21 de 44 confirmados** (forro Tremolo Douglas, ripado, painéis imitação telha e 5 ondas RAL 8004,
    telha da pérgola, vinílico, Pladur standard, OSB, membrana, lãs, XPS, madeiras).
  - Ficam INFERRED, com o motivo no campo `oficial`:
    - o painel do Sobral em RAL 7016 (a lista só tem RAL 8004);
    - o Pladur hidrófugo e o ignífugo (a lista só tem o standard);
    - o bocal de saída da caleira interior: a lista tem-no **branco brilhante**, o modelo mostra-o preto — a confirmar.
  - Também INFERRED: o que ainda não está na lista oficial (reboco/ETICS, cortiça, caixilharia, remates RAL 7016,
    caleiras, cerâmico, azulejo, betonilha, microcimento, betão, a base do pilar da pérgola).
- **Medidas e cores da lista oficial nas texturas gratuitas:**
  - vinílico: tábuas de 1524 × 228 mm → WoodFloor043 (carvalho com nós, 8 tábuas na altura da imagem) com
    `tile_m` 3,648 × 1,824 m;
  - cortiça (até aqui só cor lisa): Cork003, aglomerado de grão grosso, tingido à cor da cortiça expandida;
  - forro Tremolo (Piveteau, Douglas maciço com autoclave castanho): já tinha tábuas de 135 mm e a cor medida na
    foto da casa construída de Torres Vedras.
  - Não há texturas dos fabricantes para reutilizar (Tremolo, Munditelha, vinílico, telha): as fotos dos produtos
    reais continuam a ser o passo para o aspeto exato.
- **Foto de um produto real → textura** (tarefa 156): `python step-inside/ferramentas/materiais/foto.py <foto>
  --produto "<nome no mapeamento>" --largura-m <largura real> [--altura-m …] [--recorte x0 y0 x1 y1]`.
  - O Blender recorta à proporção real, uniformiza a luz (divide pela foto muito desfocada), faz a imagem repetir sem
    emendas e tira o relevo (normal OpenGL) e a rugosidade da luminância.
  - As imagens ficam só no PC (`_trabalho/step-inside/texturas/fotos/<produto>/`); no mapeamento do construtor fica a
    referência (medidas, data, licença «fotografia própria»). O catálogo comum não muda: os outros construtores
    continuam com as texturas gratuitas.
  - **Como fotografar:** de frente, o telemóvel paralelo à superfície; dia encoberto ou sombra total (sem manchas de
    sol); uma área de 1 a 1,5 m sem nada à frente; resolução máxima, sem filtros; dizer a largura real fotografada
    (ou contar as tábuas).
  - Experimentado num recorte da foto da casa de Torres Vedras: funciona, mas a foto é pequena demais (145 px).

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

## Exportação, manifest e reimportação (2026-11-09, «Sim, avança»)

```bash
python step-inside/ferramentas/exportar/exportar.py step-inside/projetos-teste/<obra>/visita.json
```

**Predefinições** (`blender_exportar.py`). Exporta-se o que está visível na visita (sem estrutura, opções nem
etiquetas):

| Formato | Para | Unidades e eixos | Texturas |
|---|---|---|---|
| FBX | Unreal (Fases 4–5) | metros (`FBX_SCALE_UNITS`), −Z para a frente, Y para cima; no Unreal importar com *Convert Scene* (a validar na Fase 4) | ficheiros à parte (spec §4.2) |
| GLB | AR Android, visualizador 3D | glTF 2.0, +Y para cima; propriedades `si_*` como *extras* | embebidas |
| USDZ | AR Quick Look (iPhone) | `metersPerUnit` 1, Y para cima | embebidas (UsdPreviewSurface) |

**Teste:**
- **Duas exportações:** a casa exporta-se duas vezes e os ficheiros comparam-se byte a byte. Se um formato grava a
  data, compara-se o conteúdo reimportado.
- **Reimportação:** cada ficheiro reabre num Blender limpo (`blender_reimportar.py`) e compara-se com a fonte:
  - objetos e triângulos;
  - caixa envolvente, que confirma a escala, os eixos e a posição;
  - IDs `MAT_*`;
  - texturas presentes;
  - uma imagem com a mesma câmara e luz plana (píxeis e silhueta).

**`manifest.json`** (spec §4.3, esquema `step-inside/schema/manifest.schema.json`). Fica com os ficheiros, só no PC,
porque tem a origem real. Contém:
- o projeto e a versão (`<obra>-<commit>-<data>`);
- o SHA-256 do `.blend`;
- a data e as versões do Blender e do Unreal alvo;
- as unidades e os sistemas de coordenadas;
- a origem e a rotação da casa;
- o catálogo de materiais usado;
- cada ficheiro, com tamanho, SHA-256, IDs de material e finalidade;
- os avisos, o resultado da validação e a origem do terreno.

No Git ficam `export_resumo.json` e `export_relatorio.md`, sem coordenadas.

**Resultados:**

| Casa | Objetos | Triângulos | Caixa | Materiais e texturas | GLB | USDZ | FBX + texturas | Píxeis diferentes |
|---|---|---|---|---|---|---|---|---|
| Sobral Tipo 1 | 218 | 50 790 | erro 0,0 mm nos 3 formatos | 14 / 22, nenhuma em falta | 112,8 MB, bytes iguais | 100,4 MB, conteúdo igual | 1,9 + 97,5 MB, conteúdo igual | ≤ 1,4 % |
| Torres Vedras | 310 | 52 839 | erro 0,0 mm nos 3 formatos | 18 / 26, nenhuma em falta | 109,1 MB, bytes iguais | 95,9 MB, conteúdo igual | 2,1 + 93,1 MB, conteúdo igual | ≤ 0,9 % |

Nos dois casos as silhuetas são iguais e o resultado é WARNING: o FBX e o USDZ mudam de bytes só pela data.

**Critério de saída da fase:**
- **Cumprido:** exportação determinística, sem materiais nem recursos críticos em falta.
- **Ainda provisório:** as texturas reais da DiscoverCasa (fotos) e a lista oficial de materiais.

## A seguir

1. Lista oficial de materiais da DiscoverCasa (tarefa 163) e fotos dos materiais reais (tarefa 156): trocar as
   texturas CC0.
2. **Interiores** (tarefa 167, pedido de 2026-11-09: o cliente deve ter uma experiência o mais próxima possível de
   caminhar dentro da sua própria casa).
   - Ficam na Fase 3 porque são uma biblioteca comum, como o catálogo de materiais: IDs estáveis, fonte e licença de
     cada peça, para a DiscoverCasa e para terceiros.
   - **Um só catálogo de objetos** para as duas aplicações: o do Build Your House («Smart Interiors», tarefas 123,
     124 e 128 do hub), com os materiais deste catálogo comum. Não se faz um segundo.
   - Cada casa usa-os no modelo de visita: versão leve no AR (orçamento de 50 mil triângulos, Fase 7) e completa no
     Unreal (Fase 4). Quando o cliente decorar a casa no Build Your House, a visita mostra o que ele escolheu.
   - A decidir:
     - só o que a DiscoverCasa entrega (portas interiores com folha, rodapés, cozinha, louças, base de duche,
       interruptores, luzes) ou também mobiliário de decoração;
     - de onde vêm os modelos (gratuitos CC0 ou dos fornecedores). Descarregá-los precisa de autorização.
3. Na Fase 4 (Unreal), validar a importação do FBX (eixos e materiais mestre por ID).

A redução do GLB e do USDZ para o telemóvel, que estava aqui, foi feita na Fase 7 (de ≈ 100 MB para 1–3 MB).
