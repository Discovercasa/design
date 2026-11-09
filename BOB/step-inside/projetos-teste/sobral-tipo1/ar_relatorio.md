# AR no telemóvel · Sobral · Casa Tipo 1 no lote P

**Resultado: PASS**


Gerado por `step-inside/ferramentas/ar/ar.py` a partir do modelo de visita. Os ficheiros ficam só no PC (`_trabalho/step-inside/<obra>/ar/`).

Orçamento (Google Scene Viewer  especificação §12.1): ideal até 50 000 triângulos  máximo 100 000; texturas até 2048 px; ficheiro ≈ 10 MB.

| Variante | Para quê | Triângulos (antes) | Materiais | Maior textura | GLB | USDZ | Dimensões (m) |
|---|---|---|---|---|---|---|---|
| casa | 1:1 no terreno real, para andar à volta | 10634 (11374) | 8 | 1024 px | 1,4 MB | 1,1 MB | [13.099, 11.249, 7.543] |
| maquete | com o terreno, em ponto pequeno sobre uma mesa | 11270 (12010) | 9 | 1024 px | 2,1 MB | 1,7 MB | [53.369, 51.497, 10.5] |

**Simplificação:**
- tiram-se as camadas que não se veem de fora (`MAT_BOARD_OSB`, `MAT_INSULATION_MINERAL_WOOL`, `MAT_INSULATION_XPS`, `MAT_METAL_GALVANIZED`, `MAT_SCREED`, `MAT_TIMBER_STRUCTURE`);
- junta-se um objeto por material;
- juntam-se as faces no mesmo plano;
- as texturas descem a 1024 px (cor) e 512 px (relevo e rugosidade), em JPEG.

**Sem sombras gravadas:** o Scene Viewer e o Quick Look desenham-nas.

**Origem:** centro da planta da casa, no pavimento acabado do rés do chão (escala real em metros).

**Fundação na versão casa:** o telemóvel pousa o ponto mais baixo do modelo no chão real, por isso a fundação indicativa é cortada 0,2 m abaixo do pavimento e o soco fica visível.

**Reabertos num Blender limpo** (triângulos, dimensões, texturas):

- casa glb: 10634 triângulos, [13.099, 11.249, 7.543] m, 13 texturas, 0 em falta
- casa usdz: 10634 triângulos, [13.099, 11.249, 7.543] m, 13 texturas, 0 em falta
- maquete glb: 11270 triângulos, [53.369, 51.497, 10.5] m, 16 texturas, 0 em falta
- maquete usdz: 11270 triângulos, [53.369, 51.497, 10.5] m, 16 texturas, 0 em falta

**Por testar:** abrir em telemóveis reais (Scene Viewer num Android, Quick Look num iPhone) e medir o tempo de carregamento e a qualidade ao lado das fotos da casa construída (tarefas 84 e 158).
