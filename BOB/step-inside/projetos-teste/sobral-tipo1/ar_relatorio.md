# AR no telemóvel · Sobral · Casa Tipo 1 no lote P

**Resultado: PASS**


Gerado por `step-inside/ferramentas/ar/ar.py` a partir do modelo de visita. Os ficheiros ficam só no PC (`_trabalho/step-inside/<obra>/ar/`).

Orçamento (Google Scene Viewer  especificação §12.1): ideal até 50 000 triângulos  máximo 100 000; texturas até 2048 px; ficheiro ≈ 10 MB.

| Variante | Para quê | Triângulos (antes) | Materiais | Maior textura | GLB | USDZ | Dimensões (m) |
|---|---|---|---|---|---|---|---|
| casa | 1:1 no terreno real, para andar à volta | 13286 (12094) | 11 | 2048 px | 3,1 MB | 1,8 MB | [13.099, 11.249, 7.543] |
| maquete | com o terreno, em ponto pequeno sobre uma mesa | 14594 (12974) | 13 | 2048 px | 4,6 MB | 2,2 MB | [53.549, 51.699, 13.143] |
| casa_piso0 | piso 0 sozinho à escala 1:1, pousado no chão para andar dentro dele | 5410 (4540) | 11 | 2048 px | 2,6 MB | 1,5 MB | [13.104, 11.254, 3.152] |
| maquete_piso0 | maquete aberta até ao piso 0 (sem o que está por cima, sem teto) | 5402 (4226) | 13 | 2048 px | 4,0 MB | 1,8 MB | [53.549, 51.699, 13.143] |
| casa_piso1 | piso 1 sozinho à escala 1:1, pousado no chão para andar dentro dele | 5554 (4704) | 8 | 2048 px | 2,3 MB | 1,4 MB | [10.021, 6.271, 4.476] |
| maquete_piso1 | maquete aberta até ao piso 1 (sem o que está por cima, sem teto) | 10000 (8414) | 10 | 2048 px | 4,2 MB | 2,0 MB | [53.549, 51.699, 13.143] |

**Simplificação:**
- tiram-se as camadas que não se veem de fora (`MAT_BOARD_OSB`, `MAT_INSULATION_MINERAL_WOOL`, `MAT_INSULATION_XPS`, `MAT_METAL_GALVANIZED`, `MAT_SCREED`, `MAT_TIMBER_STRUCTURE`);
- junta-se um objeto por material;
- juntam-se os vértices repetidos (as faces no mesmo plano não: deixava frestas finas);
- as texturas descem a 1024 px (cor) e 512 px (relevo e rugosidade), em JPEG.

**Sombras:** a do sol não fica gravada (o Scene Viewer e o Quick Look desenham-na). Fica gravada a **oclusão ambiente** (sombra suave dos cantos, dos beirais, dos vãos e debaixo da pérgola) numa película fina (`AR_OCLUSAO`), a 5 mm de cada superfície: preta, com a transparência tirada da oclusão, com UVs próprios. Assim funciona também no iPhone, que só lê um conjunto de UVs (as texturas da casa repetem-se nos seus). Só as faces com alguma sombra levam película; a cobertura só por baixo (beirais).

**Maquete:** um bloco de terreno com a borda direita. O retângulo é o maior à volta da casa, até ao raio, que o levantamento cobre todo; os lados descem a um fundo plano (cor da terra do catálogo), por isso assenta direito na mesa. O chão é cozido numa só imagem por cima do bloco: a textura do catálogo à escala real misturada com uma cópia maior e rodada, uma variação larga de cor e a sombra suave da casa. Já não se vê o padrão a repetir.

**Origem:** centro da planta da casa, no pavimento acabado do rés do chão (escala real em metros).

**Fundação na versão casa:** o telemóvel pousa o ponto mais baixo do modelo no chão real, por isso a fundação indicativa é cortada 0,2 m abaixo do pavimento e o soco fica visível.

**Pisos** (níveis dos pavimentos acabados, a partir do rés do chão: 0,00 m, 2,96 m):
- `casa_pisoN`: o piso N sozinho à escala real, de 0,2 m abaixo do pavimento até logo abaixo do piso de cima (o último sem a cobertura), com o pavimento na origem. O telemóvel pousa-o no chão e anda-se lá dentro.
- `maquete_pisoN`: a casa com o terreno, aberta até ao piso N (o que está por cima é cortado e os tetos desse piso tirados), para ver as divisões de cima.
- Os cortes são fechados, para as paredes não parecerem ocas vistas de cima.


**Reabertos num Blender limpo** (triângulos, dimensões, texturas):

- casa glb: 13286 triângulos, [13.099, 11.249, 7.543] m, 14 texturas, 0 em falta
- casa usdz: 13286 triângulos, [13.099, 11.249, 7.543] m, 14 texturas, 0 em falta
- maquete glb: 14594 triângulos, [53.549, 51.699, 13.143] m, 15 texturas, 0 em falta
- maquete usdz: 14594 triângulos, [53.549, 51.699, 13.143] m, 15 texturas, 0 em falta
- casa_piso0 glb: 5410 triângulos, [13.104, 11.254, 3.152] m, 12 texturas, 0 em falta
- casa_piso0 usdz: 5410 triângulos, [13.104, 11.254, 3.152] m, 14 texturas, 0 em falta
- maquete_piso0 glb: 5402 triângulos, [53.549, 51.699, 13.143] m, 13 texturas, 0 em falta
- maquete_piso0 usdz: 5402 triângulos, [53.549, 51.699, 13.143] m, 15 texturas, 0 em falta
- casa_piso1 glb: 5554 triângulos, [10.021, 6.271, 4.476] m, 9 texturas, 0 em falta
- casa_piso1 usdz: 5554 triângulos, [10.021, 6.271, 4.476] m, 12 texturas, 0 em falta
- maquete_piso1 glb: 10000 triângulos, [53.549, 51.699, 13.143] m, 13 texturas, 0 em falta
- maquete_piso1 usdz: 10000 triângulos, [53.549, 51.699, 13.143] m, 13 texturas, 0 em falta

**Por testar:** abrir em telemóveis reais (Scene Viewer num Android, Quick Look num iPhone) e medir o tempo de carregamento e a qualidade ao lado das fotos da casa construída (tarefas 84 e 158).
