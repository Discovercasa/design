# AR no telemóvel · Torres Vedras · casa no lote

**Resultado: PASS**


Gerado por `step-inside/ferramentas/ar/ar.py` a partir do modelo de visita. Os ficheiros ficam só no PC (`_trabalho/step-inside/<obra>/ar/`).

Orçamento (Google Scene Viewer  especificação §12.1): ideal até 50 000 triângulos  máximo 100 000; texturas até 2048 px; ficheiro ≈ 10 MB.

| Variante | Para quê | Triângulos (antes) | Materiais | Maior textura | GLB | USDZ | Dimensões (m) |
|---|---|---|---|---|---|---|---|
| casa | 1:1 no terreno real, para andar à volta | 22888 (23288) | 13 | 1024 px | 2,5 MB | 2,0 MB | [19.261, 21.691, 3.697] |
| maquete | com o terreno, em ponto pequeno sobre uma mesa | 25236 (27843) | 14 | 1024 px | 3,3 MB | 2,6 MB | [60.263, 58.26, 5.545] |

**Simplificação:**
- tiram-se as camadas que não se veem de fora (`MAT_BOARD_OSB`, `MAT_INSULATION_MINERAL_WOOL`, `MAT_INSULATION_XPS`, `MAT_MEMBRANE_BREATHER`, `MAT_MEMBRANE_BREATHER__DARK`, `MAT_METAL_GALVANIZED`, `MAT_SCREED`, `MAT_TIMBER_STRUCTURE`);
- junta-se um objeto por material;
- juntam-se as faces no mesmo plano;
- as texturas descem a 1024 px (cor) e 512 px (relevo e rugosidade), em JPEG.

**Sem sombras gravadas:** o Scene Viewer e o Quick Look desenham-nas.

**Origem:** centro da planta da casa, no pavimento acabado do rés do chão (escala real em metros).

**Fundação na versão casa:** o telemóvel pousa o ponto mais baixo do modelo no chão real, por isso a fundação indicativa é cortada 0,2 m abaixo do pavimento e o soco fica visível.

**Reabertos num Blender limpo** (triângulos, dimensões, texturas):

- casa glb: 22888 triângulos, [19.261, 21.691, 3.697] m, 20 texturas, 0 em falta
- casa usdz: 22888 triângulos, [19.261, 21.691, 3.697] m, 20 texturas, 0 em falta
- maquete glb: 25236 triângulos, [60.263, 58.26, 5.545] m, 23 texturas, 0 em falta
- maquete usdz: 25236 triângulos, [60.263, 58.26, 5.545] m, 23 texturas, 0 em falta

**Por testar:** abrir em telemóveis reais (Scene Viewer num Android, Quick Look num iPhone) e medir o tempo de carregamento e a qualidade ao lado das fotos da casa construída (tarefas 84 e 158).
