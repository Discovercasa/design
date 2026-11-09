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
- **Defeitos da versão 3:**
  - frestas entre as tábuas do Tremolo (tarefa 164);
  - cimento à vista no chão dos vãos das portas interiores (tarefa 165).
- **Um modelo por piso** nas casas de dois ou mais pisos (tarefa 166).
- **Fotos e materiais reais** (tarefas 156 e 163): texturas e lista oficial de materiais.
- **Interiores** (tarefa 167, Fase 3): entram no AR na versão leve.
- **Visualizador 3D** para quem não tem AR (tarefa 85):
  - o mais simples é o componente `<model-viewer>` da Google, que mostra o GLB e passa ao AR no Android e no iPhone;
  - é uma dependência nova, por isso é preciso perguntar antes (regra do repositório).
