# Fase 7 · AR no telemóvel (em curso)

Tarefas do hub 82 a 85, 157 e 158. Especificação §8, §12.1, §13 Fase 7 e §14.3. A ordem foi decidida a 2026-11-07:
o AR vem logo depois da Fase 3 e tem de ser realista, «não aparentar ter materiais simples».

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
- **Sem dependências novas:** só links. O visualizador 3D para quem não tem AR (tarefa 85) continua por fazer.
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
- **Maquete:** um ficheiro por piso, com a casa aberta.
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

## Em falta

- **Telemóveis reais** (tarefa 84):
  - abrir no Scene Viewer de um Android e no Quick Look de um iPhone;
  - confirmar a escala, a posição no chão e a orientação;
  - medir o tempo de carregamento.
- **Mais realismo** (tarefa 157):
  - vidro e caixilho nos vãos do Sobral (hoje os vãos são buracos);
  - oclusão ambiente (sombra suave dos cantos);
  - terreno sem a repetição visível da textura;
  - borda do terreno da maquete mais limpa.
- **Soleira das portas exteriores** (pergunta 23 por obra). O pavimento das portas interiores é contínuo
  (confirmado a 2026-11-09).
- **Um modelo por piso** nas casas de dois ou mais pisos (tarefa 166).
- **Fotos e materiais reais** (tarefas 156 e 163): texturas e lista oficial de materiais.
- **Interiores** (tarefa 167, Fase 3): entram no AR na versão leve.
- **Visualizador 3D** para quem não tem AR (tarefa 85):
  - o mais simples é o componente `<model-viewer>` da Google, que mostra o GLB e passa ao AR no Android e no iPhone;
  - é uma dependência nova, por isso é preciso perguntar antes (regra do repositório).
