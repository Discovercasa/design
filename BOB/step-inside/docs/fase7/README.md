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

**Falta** carregar os 8 ficheiros no hub. Tem de ser com a conta do utilizador, porque a conta vem do Hub e o Claude
não entra com palavras-passe.

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
- **Fotos e materiais reais** (tarefas 156 e 163): texturas e lista oficial de materiais.
- **Aprovação visual** ao lado das fotos da casa construída de Torres Vedras (tarefa 158).
- **Visualizador 3D** para quem não tem AR (tarefa 85):
  - o mais simples é o componente `<model-viewer>` da Google, que mostra o GLB e passa ao AR no Android e no iPhone;
  - é uma dependência nova, por isso é preciso perguntar antes (regra do repositório).
