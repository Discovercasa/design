# AR no telemóvel · Torres Vedras · casa no lote

**Resultado: PASS**


Gerado por `step-inside/ferramentas/ar/ar.py` a partir do modelo de visita. Os ficheiros ficam só no PC (`_trabalho/step-inside/<obra>/ar/`).

Orçamento (Google Scene Viewer  especificação §12.1): ideal até 50 000 triângulos  máximo 100 000; texturas até 2048 px; ficheiro ≈ 10 MB.

| Variante | Para quê | Triângulos (antes) | Materiais | Maior textura | GLB | USDZ | Dimensões (m) |
|---|---|---|---|---|---|---|---|
| casa | 1:1 no terreno real, para andar à volta | 24056 (25188) | 18 | 1024 px | 2,9 MB | 2,7 MB | [17.667, 13.325, 3.702] |
| maquete | com o terreno, em ponto pequeno sobre uma mesa | 28000 (27938) | 20 | 2048 px | 4,0 MB | 3,1 MB | [34.665, 43.325, 5.012] |

**Simplificação:**
- tiram-se as camadas que não se veem de fora (`MAT_BOARD_OSB`, `MAT_INSULATION_MINERAL_WOOL`, `MAT_INSULATION_XPS`, `MAT_METAL_GALVANIZED`, `MAT_SCREED`, `MAT_TIMBER_STRUCTURE`);
- junta-se um objeto por material;
- juntam-se os vértices repetidos (as faces no mesmo plano não: deixava frestas finas);
- as texturas descem a 1024 px (cor) e 512 px (relevo e rugosidade), em JPEG.

**Sombras:** a do sol não fica gravada (o Scene Viewer e o Quick Look desenham-na). Fica gravada a **oclusão ambiente** (sombra suave dos cantos, dos beirais, dos vãos e debaixo da pérgola) numa película fina (`AR_OCLUSAO`), a 5 mm de cada superfície: preta, com a transparência tirada da oclusão, com UVs próprios. Assim funciona também no iPhone, que só lê um conjunto de UVs (as texturas da casa repetem-se nos seus). Só as faces com alguma sombra levam película; a cobertura só por baixo (beirais).

**Maquete:** um bloco de terreno com a borda direita. O retângulo é o maior à volta da casa, até ao raio, que o levantamento cobre todo; os lados descem a um fundo plano (cor da terra do catálogo), por isso assenta direito na mesa. O chão é cozido numa só imagem por cima do bloco: a textura do catálogo à escala real misturada com uma cópia maior e rodada, uma variação larga de cor e a sombra suave da casa. Já não se vê o padrão a repetir.

**Frente e origem** (notas do teste da equipa, 2026-11-10): a casa roda para os seus eixos e para a fachada da entrada ficar virada para quem vê (+Z). Na versão 1:1, a origem — onde o telemóvel pousa o modelo — fica 2 m à frente da casa, ao centro dessa fachada, no pavimento acabado: começa-se à frente da casa, não dentro dela. Na maquete, a origem fica no centro da planta. Fachada da entrada: porta de entrada (M5 Sala / Entrada). Escala real em metros.

**Fundação na versão casa:** o telemóvel pousa o ponto mais baixo do modelo no chão real, por isso a fundação indicativa é cortada 0,2 m abaixo do pavimento e o soco fica visível.


**Reabertos num Blender limpo** (triângulos, dimensões, texturas):

- casa glb: 24056 triângulos, [17.667, 13.325, 3.702] m, 21 texturas, 0 em falta
- casa usdz: 24056 triângulos, [17.667, 13.325, 3.702] m, 21 texturas, 0 em falta
- maquete glb: 28000 triângulos, [34.665, 43.325, 5.012] m, 22 texturas, 0 em falta
- maquete usdz: 28000 triângulos, [34.665, 43.325, 5.012] m, 22 texturas, 0 em falta

**Por testar:** abrir em telemóveis reais (Scene Viewer num Android, Quick Look num iPhone) e medir o tempo de carregamento e a qualidade ao lado das fotos da casa construída (tarefas 84 e 158).
