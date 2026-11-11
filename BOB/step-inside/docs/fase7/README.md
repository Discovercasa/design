# Fase 7 · AR no telemóvel (em curso)

Tarefas do hub 82 a 85, 157 e 158. Especificação §8, §12.1, §13 Fase 7 e §14.3. A ordem foi decidida a 2026-11-07:
o AR vem logo depois da Fase 3 e tem de ser realista, «não aparentar ter materiais simples».
Ordem de apresentação (2026-11-09): no hub as fases aparecem pela numeração (0…9), a Fase 7 no seu lugar, após a Fase 6; a ordem de trabalho (2 → 3 → 7 → 4 …) não mudou.

**Critério de saída:** o AR abre e coloca o modelo corretamente nos telemóveis suportados.

## Comando

```bash
python step-inside/ferramentas/ar/ar.py step-inside/projetos-teste/<obra>/visita.json [--textura-max 1024] [--raio-terreno 20]
```

Parte do modelo de visita, já com os materiais do catálogo e as texturas (`blender_ar.py`).

**Duas variantes por casa:**
- **casa**: a casa sozinha à escala 1:1, para pousar no terreno real e andar à volta.
  - O telemóvel pousa o ponto mais baixo do modelo no chão, por isso a fundação indicativa é cortada 0,2 m abaixo
    do pavimento. Sem isso a casa ficaria a flutuar 1 m no ar.
- **maquete**: a casa com o terreno até `raio_terreno_m` à volta, para ver em ponto pequeno sobre uma mesa.

**Origem:** centro da planta da casa, no pavimento acabado do rés do chão. Escala real, em metros.

**Simplificação:**
1. Tiram-se as camadas que não se veem de fora (OSB, lãs, membranas, betonilha, perfis, estrutura de madeira). São os
   materiais com `visivel: false` no catálogo; a madeira lamelada da pérgola fica.
2. Junta-se um objeto por material, para haver poucas chamadas de desenho.
3. Juntam-se as faces no mesmo plano. A forma fica igual e as UVs continuam certas.
4. As texturas descem a 1024 px (cor) e 512 px (relevo e rugosidade), em JPEG a 85 %.
5. Não há sombras gravadas: o Scene Viewer e o Quick Look desenham-nas (§8).

**Orçamento** (Google Scene Viewer, §12.1):
- triângulos: ideal até 50 000, máximo 100 000;
- texturas até 2048 px;
- ficheiro ≈ 10 MB (acima de 25 MB falha).

Cada ficheiro é reaberto num Blender limpo para conferir os triângulos, as dimensões (escala e eixos) e as texturas.

## Resultados (2026-11-09)

| Casa | Variante | Triângulos | GLB | USDZ |
|---|---|---|---|---|
| Sobral Tipo 1 | casa | 8 686 | 1,5 MB | 1,2 MB |
| Sobral Tipo 1 | maquete | 9 165 | 2,1 MB | 1,7 MB |
| Torres Vedras | casa | 22 888 | 2,5 MB | 2,0 MB |
| Torres Vedras | maquete | 25 236 | 3,3 MB | 2,6 MB |

**PASS nas duas casas:** tudo reabre com as dimensões certas e sem texturas em falta. Antes da Fase 7 o GLB tinha
≈ 110 MB e o USDZ ≈ 100 MB.

**Ficheiros:** ficam só no PC (`_trabalho/step-inside/<obra>/ar/`). A 2026-11-09 foram enviados ao utilizador para
os experimentar no telemóvel. Para clientes vão precisar de links privados com validade, a ver na Fase 6 ou com o
armazenamento privado do Supabase. Nada é publicado sem autorização.

## Teste pelo hub (2026-11-09)

O utilizador pediu: «sim adiciona uma secção de teste onde tem essas componentes».

O projeto Step Inside no hub (design.discovercasa.pt) tem agora a secção **«Teste do AR no telemóvel»**:
- **Carregar:** o botão «Modelo AR» carrega ficheiros `.usdz` e `.glb`. Ficam como documentos do tipo `ar`, no mesmo
  armazenamento privado dos outros documentos (migração `supabase/migrations/0015_documentos_ar.sql`).
  - O título «Obra · variante» agrupa-os por obra.
- **iPhone / iPad:** cada `.usdz` tem o botão «Ver em AR · iPhone».
  - É um `<a rel="ar">` cujo único filho é uma imagem, como o Safari exige para abrir o AR Quick Look.
  - O link é assinado e dura 1 hora. É preparado antes do toque, porque o Safari só abre o Quick Look a partir de um
    toque num link verdadeiro.
- **Android:** cada `.glb` tem o botão «Ver em AR · Android», um link `intent://` para o Google Scene Viewer em modo
  AR, com regresso à página do hub.
- **O que verificar:**
  - tamanho (uma porta ≈ 2,1 m);
  - assenta no chão;
  - orientação;
  - tempo de abertura;
  - aspeto dos materiais.

  O resultado escreve-se na tarefa «Testar em pelo menos um iPhone e um Android reais».
- **Sem dependências novas:** só links. O visualizador 3D para quem não tem AR (tarefa 85) veio depois, com o `<model-viewer>` (ver abaixo).
- **Teste automático:** `tests/hub.spec.mjs` («Step Inside: teste do AR»), no computador e no telemóvel.

**Carregamento dos modelos (2026-11-09).** O utilizador pediu «sim … podem ficar disponíveis para qualquer pessoa
testar com acesso ao HUB de Design».
- Os 8 ficheiros foram carregados por uma Edge Function temporária, `carregar-ar`, no Supabase do Design.
  - Foi protegida por uma chave de uso único, que não ficou no repositório.
  - Depois do carregamento passou a um *stub* que responde 410 (como `carregar-documentos-iniciais`); fica `verify_jwt`.
- Ficaram 8 documentos `ar` (ids 42–49), já com os tipos certos:
  - `model/vnd.usdz+zip` para o iPhone;
  - `model/gltf-binary` para o Android.
- Títulos:
  - «Torres Vedras · casa 1:1»;
  - «Torres Vedras · maquete»;
  - «Sobral Tipo 1 (lote P) · casa 1:1»;
  - «Sobral Tipo 1 (lote P) · maquete».
- Quem entra no hub do Design vê-os e abre-os em AR.
- **Atualizações:** quando os modelos mudarem, carregam-se de novo pelo botão «Modelo AR». Na Fase 6 isto passa a
  automático.

## Correções depois do primeiro teste no telemóvel (2026-11-09)

O utilizador reportou três problemas.

**1. Paredes abertas nas portas e linhas no teto e nas paredes.**
- **Causa:** sem as camadas escondidas, a parede fica com duas peles. Num vão vê-se o interior, e a textura de
  «estuque pintado» tinha fissuras.
- **Correção:** o modelo de visita cria um **forro em cada vão** (`ARCH_REVEALS`: ombreiras, padieira e peitoril).
  - O vão real é medido com raios (largura e altura livres) e a espessura da parede só dentro da faixa da própria
    parede, para não apanhar a parede de um canto.
  - O forro entra 15 mm na parede, por isso o vão não fica mais estreito.
  - Ficam de fora os vãos que já têm remates no modelo (as janelas e portas exteriores de Torres Vedras) e as
    passagens sem parede (a `PORTA_EXTRA` da lavandaria do Sobral).
  - Resultado: Torres Vedras 8 forros, Sobral 18.
  - Verificado por raio: do meio de cada porta interior de Torres Vedras, de lado, o raio batia a 1,4–2,7 m dentro
    da parede ou não batia em nada; agora bate no forro a 0,43 m, que é meia largura.
- O Pladur pintado passa a cor lisa.
- O AR deixou de juntar faces coplanares: poupava menos de 2 % dos triângulos e deixava frestas finas.

**2. Pérgola com falhas nas vigas e um espaço entre o teto e o telhado.**
- **Causa:** as 21 peças da pérgola estão na coleção da estrutura (`1.10 Pérgola`), que não entra na visita. E a
  «Membrana de topo» das platibandas era tratada como escondida.
- **Correção:** a regra `estrutura_a_vista` no mapeamento do construtor põe a pérgola na visita com o produto
  «Madeira pérgola» (lamelada).
- A variante escura da membrana (`MAT_MEMBRANE_BREATHER__DARK`) passou a visível.

**3. Tremolo.**
- O revestimento da DiscoverCasa é um Tremolo **vertical, mais fino e mais claro**.
- Por agora a textura de madeira roda 90° (`rotacao_uv`), as tábuas ficam mais estreitas (`tile_m` 1 m) e a cor
  mais clara (#8E6A48).
- **A acertar com uma foto do Tremolo real**, que o utilizador ofereceu.

**Nos testes:** os 8 ficheiros do hub foram substituídos pela versão 2, no mesmo documento e com o mesmo link (a
função temporária foi desligada outra vez). A exportação da Fase 3 e o AR voltaram a passar nas duas casas.

## Versão 3: comparação com a foto da casa construída (2026-11-09)

O utilizador enviou uma foto de Torres Vedras construída. É a referência da aprovação visual (tarefa 158). Disse
ainda:
- «havia pequenos gaps no tremolo e conseguia-se ver o interior através desses pequenos gaps»;
- «o gesso cartonado do interior é plano não tem relevo nem imperfeições». Já estava liso na versão 2.

**Tremolo:**
- **Cor medida na foto:** castanho-avermelhado quente, ≈ #C0935C ao sol e ≈ #895332 à sombra. No catálogo ficou
  `MAT_WOOD_CLADDING__DOUGLAS_BROWN` = #A0653C.
- **Largura:** tábuas verticais de 135 mm (Tremolo Piveteau 22×135, dos registos). A textura WoodSiding009 tem 8
  tábuas na altura da imagem; rodada 90°, com `tile_m` [2,16 m, 1,08 m], dá 135 mm por tábua.
- **Erro corrigido:** as texturas tingidas ficavam em cache pelo nome do material, por isso uma cor nova não mudava
  nada. Agora a chave inclui a cor.

**Frestas no Tremolo:** eram um defeito do modelo AR. Entre as peças do revestimento do modelo havia pequenas
aberturas, e sem a membrana de trás via-se o interior por elas. A fachada real é de macho-fêmea, sem juntas
abertas. `MAT_MEMBRANE_BREATHER` passou a visível, por trás do revestimento, e as frestas deixam de mostrar o
interior.

**Pérgola:** a madeira lamelada passou ao mesmo tom quente (#A8743F).

**Terreno:** `material_terreno` no `visita.json` põe relva à volta de Torres Vedras, como na foto.

**Imagem de comparação:** `_trabalho/step-inside/torres-vedras/ar/comparacao_foto_v3.png` (só no PC).

Os 8 ficheiros do hub passaram à versão 3, nos mesmos links.

## Versão 3 aprovada e o que ficou (2026-11-09)

O utilizador aprovou a versão 3 («está aprovada»; tarefa 158 concluída) e pediu para encaixar quatro pontos no
fluxo de trabalho. A equipa foi avisada no hub de que pode testar e escrever na tarefa 84 o que está bem ou mal.

| Pedido do utilizador | Tarefa | Fase | Porquê aí |
|---|---|---|---|
| «Fix no tremolo, continua com gaps entre as madeiras do revestimento exterior» | 164 | 7 | Defeito do modelo AR: a versão 3 só tapou o fundo com a membrana, as aberturas entre as peças continuam. Falta ver se vêm do modelo de produção ou só do de visita. |
| «Nas portas interiores o chão na zona das portas está em cimento» | 165 | 7 | Defeito do modelo AR, ao lado dos forros dos vãos. Causa provável, a confirmar: o pavimento para na parede e, no vão, vê-se a laje. Pavimento contínuo ou perfil/soleira: pergunta 23 por obra, em aberto. |
| Ver o piso de cima ou o de baixo numa casa de dois ou mais pisos | 166 | 7 (e 4) | O Sobral Tipo 1, já no teste, tem dois pisos. Ver a proposta abaixo. A navegação do Unreal (tarefa 70, Fase 4) passa a incluir escadas e um menu de pisos. |
| «Adicionar interiores», para o cliente caminhar dentro da sua própria casa | 167 | 3 | Biblioteca comum de peças, como o catálogo de materiais, partilhada com o «Smart Interiors» do Build Your House (tarefas 123, 124, 128); a versão leve vai para o AR e a completa para o Unreal. |

**Proposta para os pisos (tarefa 166).**
- **Problema:** à escala 1:1 o piso de cima do Sobral Tipo 1 fica 2,88 m acima do chão e o cliente não lhe chega.
- **Um modelo por piso no Teste do AR:**
  - «Piso 0»: sem o que está por cima;
  - «Piso 1»: sem a cobertura e pousado no chão, para se andar dentro dele à escala real.
- **Maquete:** um ficheiro por piso, com a casa aberta. *(Deixou de se fazer na versão 7.2: só uma maquete com terreno.)*
- **Escolha do piso:** no hub, com um botão por piso. O Quick Look e o Scene Viewer não têm botões dentro do modelo.
- **Visualizador 3D (tarefa 85) e Unreal:** o piso escolhe-se num menu e sobem-se as escadas.

## Versão 4: frestas do Tremolo e chão das portas (2026-11-09)

O utilizador disse «Sim, começa» para as tarefas 164 e 165. As duas causas foram medidas no modelo antes de mudar
o código.

**Frestas do Tremolo (tarefa 164).**
- **Medição:** um varrimento por raios nas fachadas de Torres Vedras via a membrana numa fresta vertical em toda a
  altura, entre todas as tábuas.
- **Causa:** o modelo de produção desenha cada tábua com 129 mm e uma junta de 6 mm (`junta` em
  `sistema_construtivo.json`), para as contar. O Pladur tem juntas de 2 mm.
- **Correção:** o modelo de visita fecha as juntas dos acabamentos (`ferramentas/visita/juntas.py`, ver a Fase 2).
  - Juntas fechadas: Torres Vedras 1 961, Sobral 1 704. Nenhuma ficou por fechar.
  - Uma tábua cortada estreita (39 mm ao lado de um vão) também conta: a espessura é a das peças vizinhas.
- **Verificação:** varrimento de 2 em 2 mm nas quatro fachadas de Torres Vedras, a 4 alturas. A membrana atrás do
  Tremolo já não aparece em nenhum ponto.
- **Fachada real:** macho-fêmea, sem juntas abertas. A textura continua a mostrar a linha entre as tábuas de 135 mm.

**Chão das portas (tarefa 165).**
- **Medição:** o raio a descer do meio de cada porta batia na laje.
  - Torres Vedras: o vinílico está 5 mm acima da laje.
  - Sobral: um degrau de 16 cm.
  - Piso de cima do Sobral: atravessava até ao teto do rés do chão.
- **Correção:** chão em cada porta, com o pavimento de cada lado até ao meio da parede, e aros que descem até ao
  chão.
  - A porta PI2.08 do Sobral mede aberta só 12 cm acima do piso. Agora conta como porta pelo tipo das fontes.
  - Torres Vedras: 10 portas com chão novo e 5 que já tinham chão ou soleira. Sobral: 11. Nenhuma ficou sem chão.
- **Confirmado** pelo utilizador («Sim, contínuo»): o pavimento continua por baixo das portas interiores. Falta a
  soleira das portas exteriores (pergunta 23).

**AR:** PASS nas duas casas, com a exportação da Fase 3 a passar outra vez.

| Casa | Variante | Triângulos | GLB | USDZ |
|---|---|---|---|---|
| Torres Vedras | casa | 22 166 | 2,2 MB | 1,9 MB |
| Torres Vedras | maquete | 26 721 | 3,1 MB | 2,6 MB |
| Sobral Tipo 1 | casa | 9 214 | 1,3 MB | 1,1 MB |
| Sobral Tipo 1 | maquete | 9 850 | 2,0 MB | 1,6 MB |

Há menos triângulos do que na versão 3: com as juntas fechadas, as peças encostam e o AR junta os vértices.

**Hub:** os 8 ficheiros passaram à versão 4, nos mesmos links (função temporária com chave de uso único, desligada
outra vez com 410 e `verify_jwt`; a chave foi apagada).

**Imagens de verificação** (só no PC): `_trabalho/step-inside/torres-vedras/ar/v4_tremolo*.png` e
`v4_porta_P05.png`; `_trabalho/step-inside/sobral-tipo1/ar/v4_porta_PI2.04.png`.

## Versão 4.1: o chão das portas no modelo de produção (2026-11-09)

O utilizador confirmou «Sim, contínuo» (o pavimento continua por baixo das portas interiores) e, para a correção
do modelo de produção, «Sim, corrige».

**Construtor:** `ferramentas/modelo/camadas.py`, funções `faixas_portas` e `portas_paineis`.
- **Que portas conta:**
  - os vãos entre painéis;
  - as portas dentro de um painel.
- **O que faz:** o pavimento de cada divisão (e, no rés do chão, as camadas por baixo) continua até ao meio da
  parede.
- **Portas exteriores:** ficam de fora, porque a soleira está por definir (pergunta 23).
- **Área útil das divisões:** não muda.
- **Lista de material:**

| Casa | Vinílico | XPS e betonilha |
|---|---|---|
| Torres Vedras | 151,6 → 152,5 m² (8 portas) | — |
| Sobral Tipo 1 | 101,9 → 102,5 m² | 55,2 → 55,3 m² |

**Verificação independente:** no modelo de visita, todas as portas interiores já trazem chão do modelo de produção
(Torres Vedras 13 de 15, Sobral 6 de 11). As restantes são as portas exteriores.
- **Melhoria no Sobral:** duas passagens do piso de cima, entre módulos, não estão nas fontes, por isso a versão 4
  não lhes pôs chão. Agora também o têm.
- **Validação:** issues 0 nas duas casas.
- **AR:** PASS. Triângulos e tamanhos:
  - Torres Vedras: casa 22 468 (2,2 MB), maquete 27 023 (3,1 MB);
  - Sobral: casa 10 634 (1,4 MB), maquete 11 270 (2,1 MB).
- **Hub:** os 8 ficheiros passaram à versão 4.1 (mesmo procedimento; função desligada outra vez e chave apagada).

**Outras diferenças ao gerar de novo os modelos:** os ficheiros de produção no Git eram de 2026-10-30. Gerá-los agora
traz também as mudanças do construtor de 06 e 07/11, que nunca lhes tinham chegado:
- vergas;
- face da platibanda do lado da cobertura;
- saídas das caleiras ocultas;
- nome do painel sandwich;
- ripado da opção A do Sobral 413,7 → 633,5 m.

Correr o construtor antigo nos mesmos ficheiros confirmou que só as linhas do pavimento vêm desta correção.

## Versão 5: um modelo por piso e a caixilharia do Sobral (2026-11-09)

O utilizador disse «Sim, avança» para as tarefas 166 e 157.

**Pisos (tarefa 166, concluída).** Nas casas com mais de um piso, `ar.py` gera, além de `casa` e `maquete`:
- `casa_pisoN`: só o piso N à escala real.
  - Vai de 0,2 m abaixo do pavimento até logo abaixo do pavimento do piso de cima.
  - O último piso fica sem a cobertura.
  - O pavimento fica na origem: o telemóvel pousa-o no chão e anda-se lá dentro.
- `maquete_pisoN`: a casa com o terreno, aberta até ao piso N, sem o que está por cima nem os tetos desse piso.
  *Deixou de se gerar na versão 7.2 (utilizador, 2026-11-10): o Sobral fica com quatro modelos, a maquete com terreno
  e a casa, o piso 0 e o piso 1 sem terreno. As linhas `maquete_piso*` das tabelas abaixo são históricas.*
- Os pisos são os níveis dos pavimentos acabados visíveis, com pelo menos 4 m² cada (Sobral: 0 e 2,96 m).
- Os cortes ficam fechados (`holes_fill`), para as paredes não parecerem ocas vistas de cima.
- A regra de não flutuar vale também para `casa_pisoN`.
- Torres Vedras tem um só piso e não leva variantes.

| Sobral Tipo 1 | Triângulos | GLB | USDZ |
|---|---|---|---|
| casa | 11 354 | 1,4 MB | 1,2 MB |
| maquete | 11 990 | 2,1 MB | 1,7 MB |
| casa_piso0 | 4 130 | 0,9 MB | 0,9 MB |
| casa_piso1 | 4 242 | 0,7 MB | 0,8 MB |
| maquete_piso0 | 3 766 | 1,6 MB | 1,3 MB |
| maquete_piso1 | 7 608 | 1,8 MB | 1,5 MB |

**Hub:** cada piso tem o seu botão no Teste do AR.
- «Sobral Tipo 1 (lote P) · piso 0 (1:1)»;
- «· piso 1 (1:1)»;
- «· maquete do piso 0»;
- «· maquete do piso 1».

São 8 documentos novos (ids 50–57). A casa e a maquete do Sobral (ids 46–49) passaram à versão 5.

**Caixilharia do Sobral (parte da tarefa 157).**
- **Antes:** os vãos exteriores eram buracos. O construtor só põe caixilharia a partir da tabela de vãos do projeto e
  só no rés do chão; o Sobral não tem essa tabela.
- **Agora:** o modelo de visita põe um caixilho de alumínio RAL 7016 e vidro em cada vão exterior sem caixilho. É o
  padrão da empresa (pergunta 12 por obra), com os perfis assumidos de `sistema_construtivo.json`.
  - Um vão é exterior quando há camadas exteriores na parede ao lado; o caixilho fica do lado de fora.
  - As portas ficam assentes no pavimento.
- **Resultado:** 12 vãos (5 portas até ao chão, 7 janelas).
- **É INFERRED:** o tipo de cada vão (fixo, basculante, de correr, porta em painel) vem com a tabela de vãos do
  projeto. A porta de entrada, pelo padrão, seria de painel liso.
- O modelo de produção e as quantidades não mudam.

**Imagens de verificação** (só no PC): `_trabalho/step-inside/sobral-tipo1/ar/v5_*.png`.

## Visualizador 3D para quem não tem AR (tarefa 85, 2026-11-09)

O utilizador autorizou a dependência nova («Sim, podes»).
- **No hub:** no Teste do AR, cada modelo GLB tem o botão «Ver em 3D». Abre-o numa janela do próprio hub com o
  componente `<model-viewer>` da Google, versão 4.0.0 fixada, a partir do jsDelivr.
  - O componente só é carregado da primeira vez que se abre um modelo.
  - Usa os mesmos links assinados e privados dos botões de AR, e o USDZ da mesma variante como `ios-src`.
- **Como se usa:** roda-se com o rato ou o dedo e aproxima-se com a roda ou dois dedos.
- **No telemóvel:** num telemóvel com AR, o botão do próprio visualizador passa ao AR (WebXR, Scene Viewer ou Quick
  Look). Serve também de alternativa aos botões de AR.
- **Código:** `public/js/hub/app.js` (`verEm3D`, `carregarModelViewer`) e `paineis.js` (`htmlVisor3D`).
- **Teste:** `tests/hub.spec.mjs` («teste do AR»), com o componente simulado.
- **Verificado:** com o componente verdadeiro e os modelos reais de Torres Vedras (casa) e do Sobral (maquete do
  piso 1). Num browser sem GPU a luz fica um pouco lavada; a confirmar num computador normal.

## Versão 6: sombra dos cantos, terreno e borda da maquete (tarefa 157, 2026-11-09)

O utilizador disse «avança com a próxima tarefa»: os três pontos que faltavam na tarefa 157.

**Oclusão ambiente (sombra suave dos cantos).**
- **Porquê:** sem ela, as paredes brancas do interior ficam todas com a mesma luz. No visualizador 3D, os cantos
  desapareciam: duas paredes pareciam uma só superfície. Os telemóveis também iluminam por igual.
- **Problema:** o caminho normal (mapa de oclusão num segundo conjunto de UVs) não serve no iPhone, porque o Quick Look
  só lê um conjunto de UVs. As texturas da casa repetem-se nos seus, por isso a sombra também não pode ir na textura.
- **Solução:** uma película fina, `AR_OCLUSAO`, a 5 mm de cada superfície. É preta e a sua transparência é cozida da
  oclusão (Cycles, distância 1 m, força 0,7), com UVs próprios, em PNG de 2048 px.
  - Só ficam as faces com alguma sombra (cerca de um quarto): ver a tabela abaixo.
  - A cobertura só leva película por baixo (beirais). Em cima, a única sombra era uma linha dura e partida em cada
    fiada de telha, que parecia sujidade; o relevo das telhas já está na textura.
  - O vidro não faz sombra. Na casa 1:1 o cozimento usa um chão provisório, para as paredes escurecerem junto ao chão
    real.
- **Verificado:** no `<model-viewer>` (o motor do «Ver em 3D»), com e sem a película:
  - os cantos do interior e os vãos das janelas passam a ler-se;
  - sem riscas nem cintilação nas paredes.
  - O USDZ leva a mesma película: textura com transparência e um só conjunto de UVs (`st`).

**Borda da maquete.**
- **Antes:** a borda era em serra, porque o recorte apagava os triângulos inteiros do levantamento.
- **Agora:** um bloco retangular, como uma maquete de arquitetura (`ferramentas/ar/maquete.py`, testado).
  - O retângulo é o maior à volta da casa, até ao raio, que o levantamento cobre todo (sem entalhes).
  - O terreno é cortado a direito e os lados descem a um fundo plano, 0,3 m abaixo do ponto mais baixo, na cor da
    terra do catálogo. A maquete assenta direita na mesa.

**Terreno sem repetição.**
- **Antes:** a textura do catálogo repetia-se a cada 2–3 m, e na maquete via-se o padrão (riscas em diagonal no
  Sobral).
- **Agora:** o chão da maquete é cozido numa só imagem por cima do bloco (até 2048 px), com:
  - a textura à escala real misturada com uma cópia 2,3 vezes maior e rodada 37°, através de uma máscara de ruído;
  - uma variação larga de cor;
  - a sombra suave da casa no chão.

**Resultados (PASS nas duas casas):** tudo reabre com os mesmos triângulos e sem texturas em falta.

| Casa | Variante | Triângulos | Dos quais película | GLB | USDZ | Bloco da maquete |
|---|---|---|---|---|---|---|
| Torres Vedras | casa | 24 572 | 2 104 | 3,9 MB | 2,6 MB | — |
| Torres Vedras | maquete | 26 449 | 2 024 | 4,8 MB | 2,9 MB | 1,5–5 m à volta da casa |
| Sobral Tipo 1 | casa | 13 286 | 1 932 | 3,1 MB | 1,8 MB | — |
| Sobral Tipo 1 | maquete | 14 594 | 2 026 | 4,6 MB | 2,2 MB | 20 m em todos os lados |
| Sobral Tipo 1 | casa_piso0 | 5 410 | 1 280 | 2,6 MB | 1,5 MB | — |
| Sobral Tipo 1 | casa_piso1 | 5 554 | 1 312 | 2,3 MB | 1,4 MB | — |
| Sobral Tipo 1 | maquete_piso0 | 5 402 | 1 058 | 4,0 MB | 1,8 MB | 20 m |
| Sobral Tipo 1 | maquete_piso1 | 10 000 | 1 814 | 4,2 MB | 2,0 MB | 20 m |

- Os ficheiros cresceram 0,5–2,5 MB: a imagem da película (PNG) e, nas maquetes, a do chão. Continuam abaixo dos
  10 MB do alvo. No USDZ as duas imagens descem a 1024 px (`usdz_downscale_size`).
- **Torres Vedras:** o levantamento acaba de forma irregular perto da casa, por isso o maior retângulo coberto deixa
  só 1,5–5 m de relva à volta (a versão 5 ia até 20 m, com a borda em serra). Alternativa, se se quiser mais jardim:
  seguir o contorno do levantamento com lados direitos.
- **Visto de passagem:** o Tremolo de Torres Vedras mostra uma linha horizontal a meia altura. É a emenda da
  textura de madeira (repete-se a cada 2,16 m ao longo da tábua), não da película. As tábuas reais são inteiras na
  altura da parede.

**Imagens de verificação:** só no PC, em `_trabalho/step-inside/<obra>/ar/v6_*.png` (e `v5_maquete_antes.png`).

**No hub:** o utilizador autorizou o carregamento («Sim, carrega»). Os 16 ficheiros da versão 6 substituíram os
documentos 42–57 do Teste do AR, nos mesmos links, com os tamanhos confirmados. Depois, a função temporária voltou a
estar desligada e a chave foi apagada. A equipa foi avisada na tarefa 84.

## Versão 7: notas do primeiro teste da equipa (2026-11-10)

A equipa testou a versão 6 e deixou cinco notas na tarefa 84 do hub. O utilizador pediu: «lê analisa e corrige ou
executa as mudanças necessárias».

**1. «Quando se roda no 3D e mesmo no AR aparecem texturas com glitch a aparecer e a desaparecer, e também com
stutter».**
- **Causa (medida):** a película de sombra da versão 6 ficava 5 mm à frente de todas as faces, também das escondidas.
  - A face de cima da laje está por baixo do vinil, que tem 5 mm. A película dela caía exatamente na superfície do
    pavimento: 153 m² em Torres Vedras.
  - As duas superfícies no mesmo plano lutavam pelo mesmo píxel (z-fighting), e o pavimento piscava ao rodar.
  - Um detetor de faces no mesmo plano confirmou que, no modelo de visita, as coincidências estão todas escondidas
    (vinil em cima da laje, membrana atrás do Tremolo, ripados). Só a película as punha à vista.
- **Correção:** a película salta as faces tapadas por outra superfície a menos de 12 mm (raios ao longo da normal):
  - Torres Vedras: 1 196 faces;
  - coincidências da película: de 153 m² para 0,6 m².
- **Leveza:** a imagem da película passa a 1024 px também no GLB (como no USDZ).
- **Stutter:** não foi possível medir sem o telemóvel. Os modelos têm 5–28 mil triângulos e até 4 MB. Se continuar,
  medir com o telemóvel; o próximo passo seria comprimir as texturas (KTX2).

**2. «Os pilares da pérgola ficam no ar não assentando no chão».**
- **Causa (medida):** o levantamento de Torres Vedras é anterior à obra. A plataforma plana à cota exterior (117,48)
  só cobria 1,5 m à volta das paredes. A pérgola sai mais da fachada, e os pilares ficavam 5–70 cm acima do terreno
  antigo, que desce ao longo da fachada.
- **Correção:** a plataforma passa a incluir a pérgola (`ARCH_PERGOLA`) mais a margem, no modelo de visita. Os
  pilares ficam a 1,5 cm do chão: a cota exterior desenhada está 2 cm abaixo do pavimento.
  - É INFERRED: a forma real do terreno arranjado é a das fotos.

**3. «O AR no android não abriu, nem sequer apareceu que foi descarregado».**
- **Análise:**
  - O link segue o formato da Google, o mesmo que o `<model-viewer>` usa.
  - O hub não corre dentro de uma moldura (`X-Frame-Options: DENY`).
  - Um toque antes de o link estar pronto já mostrava um aviso.
  - Portanto, o Chrome tentou abrir o Scene Viewer da app Google e, como não conseguiu, seguiu o link de recurso, que
    era a própria página do hub: parecia que nada acontecia.
  - Causas prováveis: a app Google desatualizada ou desativada, sem os «Serviços Google Play para RA», ou outro
    browser.
- **Correções no hub:**
  - O link de recurso volta com `?ar-android=<id>`: o hub diz porque não abriu e oferece «Abrir em 3D».
  - No visualizador 3D há o botão «Ver no teu espaço (AR)». No Android usa o WebXR do próprio Chrome e não precisa da
    app Google.
  - Os links são preparados todos ao mesmo tempo (antes, um a um).
- **A confirmar:** modelo do telemóvel e browser usados no teste.

**4. «Quando se abre a casa deve estar orientado de frente para nós e quando encontra a superfície não devemos
começar dentro da casa ou dentro de uma parede mas sim com a casa a nossa frente».**
- **Causa:** a origem do modelo 1:1 era o centro da planta, e o telemóvel pousa a origem à frente de quem está a ver.
  Torres Vedras estava ainda rodado cerca de 45° (os eixos do terreno).
- **Correção:**
  - A casa é alinhada pelos seus eixos (desfaz-se `HOUSE_ROOT`).
  - A casa roda para a fachada da entrada ficar virada para quem vê (+Z no glTF e no USD).
  - Na versão 1:1, a origem fica 2 m à frente do elemento mais saliente dessa fachada, ao centro.
  - A maquete fica com a origem ao centro, também virada pela entrada. O bloco de terreno fica alinhado com a casa: em
    Torres Vedras tem agora 7–20 m de relva à volta, em vez de 1,5–5 m.
- **Fachada da entrada (`maquete.frente`, testado):**
  - a porta com «entrada» no nome (Torres Vedras: M5 «Sala / Entrada»);
  - senão, a fachada com mais portas no rés do chão (Sobral: INFERRED, até se saber a orientação, tarefa 161);
  - senão, a mais comprida.
- **Escala real nos modelos 1:1:** Quick Look sem «beliscar» (`#allowsContentScaling=0`), Scene Viewer com
  `resizable=false` e o visualizador 3D com `ar-scale="fixed"`.

**5. «Como se pode ver na imagem está a faltar parte da parede nessa zona».**
- A foto da nota está no armazenamento privado do hub e o Claude não a consegue abrir. O utilizador mandou-a na
  conversa: Torres Vedras, maquete, uma faixa vertical clara ao lado da porta.
- **Causa (no modelo de produção, `ferramentas/modelo/camadas.py`):**
  - Cada fachada junta os módulos cuja borda fica no seu plano. O módulo do portão da garagem (M1, Fachada Sul 2)
    também toca no plano da Fachada Oeste com a ponta, e entrava com os seus 11 cm de espessura.
  - O vão dele (o portão, até 2,20 m) era passado para a Fachada Oeste: cortava 11 cm × 2,20 m de Tremolo no canto.
  - Via-se o ripado de pinho, claro.
- **Correção:** os vãos de um módulo só cortam as faces paralelas a ele (`aberturas_face`).
  - O módulo perpendicular continua a contar para o revestimento da sua ponta (a ombreira de uma passagem entre
    módulos leva Pladur). Excluí-lo de vez tirava 7 m² de OSB e Pladur às ombreiras do Sobral.
  - Torres Vedras: Tremolo 164,8 → 165,0 m² (629 tábuas em vez de 631: dois bocados voltam a ser tábuas inteiras);
    OSB 9 mm e membrana +0,2 m².
  - Sobral: sem mudanças.
- **Verificado:** raios de fora para o modelo de visita e para o AR de Torres Vedras; o ripado já não se vê.
- **No hub:** os quatro ficheiros de Torres Vedras estão por carregar (a função temporária ficou por autorizar).

**Também corrigido.** Nos modelos de um só piso do Sobral:
- A laje ficava sem geometria depois do corte. O objeto vazio punha (0,0,0) na caixa do resumo, e a verificação de
  reabertura falhava (FAIL). Os objetos vazios já não se exportam.
- A frente desses modelos mede-se no que o piso guarda. O terraço do rés do chão já não empurra a origem do piso 1.

**Resultados (PASS nas duas casas):**

| Casa | Variante | Triângulos | Dos quais película | GLB | USDZ | Bloco da maquete |
|---|---|---|---|---|---|---|
| Torres Vedras | casa | 24 056 | 1 556 | 3,0 MB | 2,7 MB | — |
| Torres Vedras | maquete | 28 000 | 1 668 | 4,0 MB | 3,1 MB | 7–20 m à volta da casa |
| Sobral Tipo 1 | casa | 12 916 | 1 714 | 2,2 MB | 1,9 MB | — |
| Sobral Tipo 1 | maquete | 14 244 | 1 676 | 3,6 MB | 2,3 MB | 20 m em todos os lados |
| Sobral Tipo 1 | casa_piso0 | 5 110 | 1 064 | 1,6 MB | 1,5 MB | — |
| Sobral Tipo 1 | casa_piso1 | 5 262 | 1 068 | 1,3 MB | 1,3 MB | — |
| Sobral Tipo 1 | maquete_piso0 | 5 160 | 816 | 3,0 MB | 1,8 MB | 20 m |
| Sobral Tipo 1 | maquete_piso1 | 9 638 | 1 452 | 3,3 MB | 2,0 MB | 20 m |

**Imagens de verificação** (só no PC): `_trabalho/step-inside/<obra>/ar/v7_*.png`.

## Versão 7.2: o chão do Sobral, quatro modelos e o Android (2026-11-10)

Notas que continuavam abertas na tarefa 84, e o pedido do utilizador (2026-11-10): «a textura de sobral que fica junto
ao chão está bugada», «sobral em AR deve apenas ter uma maquete total da casa com terreno, uma da casa total sem
terreno, uma do piso 0 e uma do piso 1 ambas sem terreno» e «o AR no android continua sem funcionar».

**Sobral junto ao chão (nota 11).**
- **Causa:** o lote plano à volta da casa (P, 189,6 m²) ficava à cota exata do topo da laje. No AR, as duas superfícies
  coincidiam à volta da casa e a textura piscava.
- **Correção:** o lote fica 2 cm abaixo do topo da laje (`visita.json`: `"acima_da_laje": -0.02`, lido por
  `visita.py`; antes era fixo em 0). Terreno menos laje junto à casa: −0,03 a 0,00 m (antes −0,02 a +0,01).

**Quatro modelos no Sobral.** Por piso, o `ar.py` só gera o modelo 1:1, sem terreno; as maquetes por piso deixaram
de se gerar (PASS):

| Variante | O que é | Triângulos | GLB | USDZ |
|---|---|---|---|---|
| maquete | a casa toda com o terreno | 14 244 | 3,6 MB | 2,3 MB |
| casa | a casa toda, 1:1, sem terreno | 12 916 | 2,1 MB | 1,9 MB |
| casa_piso0 | o rés do chão, 1:1, sem terreno | 5 110 | 1,6 MB | 1,4 MB |
| casa_piso1 | o piso 1, 1:1, sem terreno | 5 262 | 1,3 MB | 1,3 MB |

**No hub (2026-11-10, autorizado pelo utilizador: «Sim, carrega»):** os oito ficheiros (documentos 46–53) foram
substituídos nos mesmos links e os documentos «maquete do piso 0/1» (54–57) foram apagados, com os ficheiros. A
função temporária voltou a estar desligada (410, recusa 401 confirmada) e a chave foi apagada. Nota 11 resolvida.

**Android (nota 10): revisão de tudo o que foi feito.**
- **Sintomas:** no primeiro teste o Scene Viewer não abriu nem descarregou nada; no segundo, a transição anima uma
  fração de segundo e volta ao hub. Quer dizer que o link chega à app Google e o Scene Viewer fecha logo.
- **O que se encontrou:** o link era o exemplo da documentação da Google (`scene-viewer/1.0?file=…`). O `<model-viewer>`
  4.0.0 da Google, que funciona nos Android de hoje, faz outro: `scene-viewer/1.2`, a query do próprio URL do modelo
  copiada para o link, `mode=ar_preferred`, `disable_occlusion=true`, `resizable=false` (1:1), o título e, no fim,
  `file=`. O botão do hub passou a fazer o link igual (`public/js/hub/ar-android.js`, `intentSceneViewer`).
- **Outras causas possíveis, que só um Android real separa:** o telemóvel sem «Google Play Services para RA» ou com a
  app Google desatualizada; o Scene Viewer não conseguir ler o link assinado do Supabase; algo no nosso GLB.
- **Diagnóstico no telemóvel** (o Claude não tem um Android para testar): em Step Inside › Teste do AR, o painel
  «Diagnóstico do AR no Android» tem cinco testes:
  - A/B: o modelo de exemplo da Google, com o link antigo (1.0) e o novo (1.2);
  - C/D: o nosso modelo, com os mesmos dois links;
  - E: o nosso modelo no AR do próprio Chrome («Ver em 3D» › «Ver no teu espaço»).
  O painel também vê sozinho se o Chrome do telemóvel tem AR (WebXR) e se o nosso ficheiro descarrega (estado,
  tipo, cabeçalho glTF). «Enviar resultado» põe tudo numa nota da tarefa 84, que o Claude lê.
- **Como ler o resultado:** A e B falham → é o telemóvel (ARCore ou app Google); B abre e D não → é o nosso ficheiro ou
  o link assinado; D abre → estava resolvido pelo link 1.2.

## Versão 7.3: a causa do Android (2026-11-10)

O utilizador, depois da 7.2: «o AR no mobile android continua a não abrir verifica o processo todo de deploy que fizeste
e encontra a falha. O que acontece é clicamos no botão e depois anima a transição para o ecrã mas volta logo ao hub nem
sequer chega a aparecer o menu seguinte».

**Revisão do processo todo**, do Blender ao telemóvel:
- O link (1.2, igual ao `<model-viewer>`), o link assinado (HTTPS, uma hora) e o GLB (glTF 2.0, uma camada de UV,
  só triângulos, índices de 16 bits, sem cores por vértice, texturas JPEG/PNG até 2048 px, 2–4 MB): tudo dentro das
  regras.
- **A falha:** todos os GLB tinham a extensão `KHR_materials_specular`. O Blender escreve-a na película de sombra
  (`AR_OCLUSAO`, especular 0), desde a versão 6 (09/11), um dia antes do primeiro teste num Android.
- O validador do Scene Viewer trata qualquer extensão que não suporta como **erro**
  (`UNSUPPORTED_GLTF_EXTENSION_USED`; suportadas: `KHR_materials_pbrSpecularGlossiness`, `KHR_materials_unlit`,
  `KHR_texture_transform`; https://developers.google.com/ar/develop/scene-viewer).
- Quando o Scene Viewer não consegue mostrar o modelo, a app Google manda o Chrome para o link de recurso
  (`browser_fallback_url`), que é o próprio hub. É o sintoma da nota: a transição anima e volta ao hub.
- O iPhone (USDZ) e o «Ver em 3D» (three.js) aceitam a extensão; por isso só o Android falhava.
- A confirmação final é no telemóvel. O validador da Google não existe fora da página dele, e o Claude não tem um
  Android.

**Correção:** `step-inside/ferramentas/ar/scene_viewer.py`, chamado pelo `ar.py` logo a seguir a cada exportação.
- Tira do GLB as extensões que o Scene Viewer não suporta (só quando não são obrigatórias; a película continua
  transparente e a geometria fica igual).
- Verifica as regras do validador: erro (extensão, cores por vértice, morph targets, mais de uma animação, mais de uma
  camada de UV, mais de 15 MB); aviso (mais de 10 materiais ou 2 transparentes, texturas acima de 2048 px, mais de
  100 mil triângulos, mais de 10 MB).
- Testes: `step-inside/tests/test_ar.py` (`TestSceneViewer`, com um GLB igual ao que o Blender exporta). O GLB do
  Sobral que estava no hub dá o erro; os novos não.
- O USDZ não muda.

**Resultado:** as duas casas sem erros. Os GLB ficam cerca de 110 bytes mais pequenos, com os mesmos triângulos.
Fica o aviso de materiais: Sobral 11–13 (2 transparentes) e Torres Vedras 18–20 (3 transparentes), contra os 10
recomendados. A Google só o recomenda; juntar materiais fica como melhoria.

**No hub (2026-11-10, autorizado pelo utilizador: «Sim, carrega»):** os seis GLB novos (Torres Vedras 43 e 45;
Sobral 47, 49, 51 e 53) substituíram os antigos nos mesmos links, com a descrição «versão 7.3». Os USDZ ficaram como
estavam. A função temporária voltou a estar desligada (recusa 401 confirmada) e a chave foi apagada. A equipa foi
avisada na tarefa 84; a nota 10 fica aberta até ao teste num Android. O aviso do hub quando o Scene Viewer não abre pede agora o diagnóstico, em vez de culpar o telemóvel.

## Versão 7.4: o que os registos do servidor mostram, e a página de teste (2026-11-10)

O utilizador, depois da 7.3: «ainda não funciona, faz um proper debugging de todas as causas que pode ser e verifica
também que pode estar haver algum tipo de conflito ao abrir no HUB sendo que para ios funciona perfeitamente».

**O que os registos do Supabase provam** (pedidos aos ficheiros AR nas últimas 24 h, por aparelho):
- iPhone: o Safari pede o link e o próprio Quick Look descarrega o USDZ (`NetworkingExtension … iOS`).
- Android (dois telemóveis, Chrome 152 e 156): só o Chrome pediu ficheiros (o «Ver em 3D» e o diagnóstico).
  **A app Google nunca pediu o modelo**, nem com o link 1.0 nem com o 1.2, nem antes nem depois da versão 7.3.
- Último teste (21:58): o hub preparou os links; cerca de 3 s depois a página carregou toda de novo (nova ligação em
  direto, os dados todos, o diagnóstico outra vez). Não houve nenhum pedido da app Google pelo meio.
- Conclusão: a falha é **antes** de descarregar. A extensão corrigida na 7.3 não era a causa deste sintoma (a correção
  continua certa: com ela o Scene Viewer recusaria o ficheiro depois de o descarregar).

**Causas que ficam, e o que as separa:**
1. Telemóvel sem a app Google, com ela desativada ou desatualizada, ou sem «Serviços Google Play para RA». O exemplo
   da Google também falha pela app Google; pelo ARCore ou pelo AR do Chrome pode abrir.
2. A app Google recebe o pedido mas não o aceita: abre e devolve logo, sem descarregar. Vê-se se outra app abriu e
   quanto tempo ficou.
3. Conflito do hub. Exemplos: aberto como app instalada no ecrã inicial (o hub é instalável), ou algo na página. A
   página de teste está fora do hub e mostra se foi aberta como app instalada.
4. O nosso link (assinado). O exemplo da Google abre e o nosso não.

**Página de teste:** `public/ar-teste.html` + `public/js/ar-teste.js`, fora do hub, com 8 testes de um toque:
- G1–G4: o exemplo da Google pela app Google (links 1.0 e 1.2), pelo ARCore (`com.google.ar.core`, só AR) e pelo AR do
  Chrome (WebXR);
- N1–N4: o nosso modelo pelos mesmos quatro caminhos.

O que a página regista sozinha:
- se a página ficou escondida depois do toque (abriu outra app) e quanto tempo;
- se voltou pelo link de recurso e, nesse caso, se uma app chegou a abrir antes;
- se não aconteceu nada em 4 s;
- o modelo do telemóvel, a versão do Android e do Chrome, se está aberta como app instalada e se o Chrome tem WebXR;
- se o nosso ficheiro descarrega.

O resultado vai para a tarefa do teste com a sessão da pessoa, ou copia-se.
- O link assinado do nosso modelo vai do hub na parte `#` do endereço: não chega a nenhum servidor e a página tira-o
  da barra.
- Os links são do módulo comum `public/js/ar-intent.js`, o mesmo que o hub usa.
- No hub, o painel do Teste do AR abre a página com o primeiro GLB. O aviso que aparece quando o Scene Viewer volta ao
  hub tem «Testar este Android».
- O painel antigo, com escolhas por teste, saiu.
- Testes: `tests/ar-teste.spec.mjs`.

## Página de teste, ronda 1 e ronda 2 (2026-11-10)

O utilizador: «já testamos em dois 3 dispositivos android diferentes mas isso não deve interessar porque se o cliente
tiver um dispositivo qualquer tem de conseguir ver sendo que neste caso nenhum deles era de uma gama média/baixa»;
«acabou agora de fazer o teste falhou todos os steps e apareceu mensagens de erro em todos».

**Ronda 1** (nota 12 da tarefa 84, enviada pela página):
- Telemóvel: modelo 24115RA8EG (Xiaomi/Redmi pelo código, INFERRED), Android 15, Chrome 152.
- O Chrome diz que tem AR (WebXR: sim). O nosso ficheiro descarrega (206, GLB válido).
- Os 8 testes falharam, também com o modelo da própria Google:
  - app Google (links 1.0 e 1.2): «nada aconteceu em 4 s», e a página nunca ficou escondida. O tester viu que
    «começa a abrir uma janela lateral e fecha logo»;
  - ARCore: voltou logo pelo link de recurso, sem nenhuma app abrir;
  - AR do Chrome pelo visualizador: «falhou ao abrir».
- **Conclusão:** não é o nosso ficheiro, nem o nosso link, nem o hub. O exemplo da Google falha da mesma maneira,
  fora do hub. O que falha é o arranque do AR / Scene Viewer no telemóvel.
- Há relatos públicos de AR a falhar em telemóveis Xiaomi com HyperOS, mesmo em aparelhos da lista do ARCore.
  Exemplos: Live View do Google Maps e apps de AR.

**Requisito do utilizador:** qualquer Android de cliente tem de conseguir ver a casa. Na página do cliente, quando o
AR não abre, o visualizador 3D na própria página tem de aparecer sozinho.

**Ronda 2** (a página limpa os resultados da ronda 1), 8 testes:
- T1: a câmara para o site (`getUserMedia`, com o erro exato);
- T2: a sessão de AR do Chrome direta (`requestSession('immersive-ar')`, com o erro exato);
- G1/N1: o Scene Viewer a abrir **em 3D** (`mode=3d_preferred`, sem câmara no arranque);
- G2/N2: o Scene Viewer a abrir em AR, como até agora;
- G3/N3: o AR do Chrome pelo visualizador, com as mensagens da consola.

A página também deteta uma janela que abre por cima sem esconder a página (perde o foco). Regista a licença da câmara
para o site e o tamanho da janela.

**Resultado da ronda 2** (o mesmo telemóvel, notas 13–16 da tarefa 84; as 14–16 repetem a 13):
- T1: a câmara abriu no site.
- T2: a sessão de AR do Chrome falhou com `NotSupportedError: The specified session configuration is not supported`.
  O mesmo Chrome dizia «AR: sim» (`isSessionSupported`): é só um «talvez».
- G1, G2, N1, N2 (Scene Viewer em 3D e em AR, o exemplo da Google e o nosso): a página perdeu o foco 0,1 s depois do
  toque e voltou ao fim de 0,2 s. Uma janela da app Google aparece e fecha, e o Scene Viewer nunca abre, nem em 3D.
- G3/N3 (AR do Chrome pelo visualizador): falhou; o visualizador passou ao modo seguinte.
- Na ronda 1, o link para o pacote do ARCore não encontrou nenhuma app: o ARCore não está instalado.
- O Redmi Note 14 Pro 5G (24115RA8EG) **não está na lista de telemóveis compatíveis com ARCore** da Google
  (https://developers.google.com/ar/devices, lida a 2026-11-10; o Redmi Note 14 e o Note 14 5G estão).
- **Causa:** este telemóvel não tem o ARCore e a Google não lho dá. Sem ele, nenhum caminho de AR da Google funciona:
  nem o Scene Viewer, nem o AR do Chrome. Não é corrigível do nosso lado: só o 3D funciona neste telemóvel.

**O que o hub faz agora** (o requisito: qualquer cliente tem de conseguir ver):
- Depois do toque em «Ver em AR · Android», se a página não ficar escondida em 3 s, o Scene Viewer não tomou conta do
  ecrã. O hub abre o modelo em 3D na própria página e mostra um aviso: precisa da app «Serviços Google Play para RA»,
  com o botão «Ver na Play Store», onde se vê se o telemóvel a pode instalar.
- O mesmo acontece quando o Chrome volta pelo link de recurso.
- A caixa do telemóvel já não diz «tem AR» quando o Chrome diz que sim. Agora diz que talvez tenha e que precisa da
  app.
- A página de teste não envia o mesmo resultado duas vezes.

## A causa do Android: um erro da app Google; o botão passa ao AR do Chrome (2026-11-11)

O utilizador: «fizeram o teste agora no outro telemovel».

**Ronda 2 no segundo telemóvel** (notas 17–19; repetidas por toques no «Enviar» antes da proteção):
- Telemóvel: Pixel 6, Android 17, Chrome 157, o hub aberto como app instalada.
- Câmara: sim.
- **AR do Chrome direto: abriu.**
- **AR do Chrome pelo visualizador: abriu, com o exemplo da Google e com o nosso modelo.**
- Scene Viewer (3D e AR, o exemplo da Google e o nosso): a janela da app Google pisca 0,1 s e fecha, como no
  Xiaomi.

**Causa do Scene Viewer:** um erro da própria app Google. A app fecha o Scene Viewer cerca de 90 ms depois de o abrir,
nas versões 17.66–17.72 (desde cerca de 23/10), em Pixel, Samsung e outros, e com o exemplo oficial da Google. Está
reportado e aberto, sem resposta da Google a 2026-11-11:
- https://github.com/google-ar/arcore-android-sdk/issues/1795
- https://github.com/google-ar/arcore-android-sdk/issues/1797

Não é o nosso ficheiro, nem o link, nem o hub. O Xiaomi, além disso, não tem ARCore (secção anterior).

**Correção:** «Ver em AR · Android» passa a ser um botão. Abre o visualizador do hub com o AR do Chrome (`<model-viewer
ar-modes="webxr quick-look">`) e entra logo em AR enquanto o toque ainda conta para o Chrome (cerca de 5 s). Se o modelo
demorar mais, aparece «Ver no teu espaço (AR)» para um segundo toque.
- Sem ARCore (o Xiaomi), o AR falha e o modelo fica em 3D, com o aviso e o link da Play Store.
- O Scene Viewer saiu do botão e do visualizador. A página de teste continua a testá-lo, para se ver quando a Google o
  corrigir.
- Testes: `tests/hub.spec.mjs` (o botão abre o visualizador só com WebXR e Quick Look, entra em AR sozinho, e fica em
  3D com o aviso quando o telemóvel não tem AR).

**O que cada telemóvel vê agora:**

| Telemóvel | Resultado |
|---|---|
| iPhone | AR (Quick Look) |
| Android com ARCore (Pixel 6) | AR no Chrome |
| Android sem ARCore (o Xiaomi) | 3D no hub |

## «Ver em 3D» também no iPhone (2026-11-11)

O utilizador: «uma coisa eu quero que no projeto step inside no dispositivos IOS também seja possível ver em 3D tal como
nos androids. Depois disso vamos progredir nas tarefas do step inside.»
- Feito (commit 65a3cfb): as linhas do iPhone no Teste do AR têm «Ver em 3D» (o GLB gémeo no visualizador; o USDZ
  continua para o Quick Look).
- Substitui, para o iPhone, a tabela acima («iPhone: AR (Quick Look)») só no sentido de acrescentar o 3D; o AR não muda.

## Em falta

- **Telemóveis reais** (tarefa 84):
  - abrir no Scene Viewer de um Android e no Quick Look de um iPhone;
  - confirmar a escala, a posição no chão e a orientação;
  - medir o tempo de carregamento;
  - ver a película de sombra (versão 6) no iPhone.
- **Soleira das portas exteriores** (pergunta 23 por obra). O pavimento das portas interiores é contínuo
  (confirmado a 2026-11-09).
- **Tabela de vãos do Sobral:** o tipo de cada vão, para trocar a caixilharia padrão (INFERRED) pela real.
- **Fotos e materiais reais** (tarefas 156 e 163): texturas e lista oficial de materiais.
- **Interiores** (tarefa 167, Fase 3): entram no AR na versão leve.
