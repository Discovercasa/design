# AR no telemóvel · Sobral · Casa Tipo 1 no lote P

**Resultado: PASS**


Gerado por `step-inside/ferramentas/ar/ar.py` a partir do modelo de visita. Os ficheiros ficam só no PC (`_trabalho/step-inside/<obra>/ar/`).

Orçamento (Google Scene Viewer  especificação §12.1): ideal até 50 000 triângulos  máximo 100 000; texturas até 2048 px; ficheiro ≈ 10 MB.

| Variante | Para quê | Triângulos (antes) | Materiais | Maior textura | GLB | USDZ | Dimensões (m) |
|---|---|---|---|---|---|---|---|
| casa | 1:1 no terreno real, para andar à volta | 11354 (12094) | 10 | 1024 px | 1,4 MB | 1,2 MB | [13.099, 11.249, 7.543] |
| maquete | com o terreno, em ponto pequeno sobre uma mesa | 11990 (12730) | 11 | 1024 px | 2,1 MB | 1,7 MB | [53.369, 51.497, 10.5] |
| casa_piso0 | piso 0 sozinho à escala 1:1, pousado no chão para andar dentro dele | 4130 (4540) | 10 | 1024 px | 0,9 MB | 0,9 MB | [13.099, 11.249, 3.152] |
| maquete_piso0 | maquete aberta até ao piso 0 (sem o que está por cima, sem teto) | 3766 (3982) | 11 | 1024 px | 1,6 MB | 1,3 MB | [53.369, 51.497, 10.5] |
| casa_piso1 | piso 1 sozinho à escala 1:1, pousado no chão para andar dentro dele | 4242 (4704) | 7 | 1024 px | 0,7 MB | 0,8 MB | [10.011, 6.261, 4.476] |
| maquete_piso1 | maquete aberta até ao piso 1 (sem o que está por cima, sem teto) | 7608 (8170) | 8 | 1024 px | 1,8 MB | 1,5 MB | [53.369, 51.497, 10.5] |

**Simplificação:**
- tiram-se as camadas que não se veem de fora (`MAT_BOARD_OSB`, `MAT_INSULATION_MINERAL_WOOL`, `MAT_INSULATION_XPS`, `MAT_METAL_GALVANIZED`, `MAT_SCREED`, `MAT_TIMBER_STRUCTURE`);
- junta-se um objeto por material;
- juntam-se os vértices repetidos (as faces no mesmo plano não: deixava frestas finas);
- as texturas descem a 1024 px (cor) e 512 px (relevo e rugosidade), em JPEG.

**Sem sombras gravadas:** o Scene Viewer e o Quick Look desenham-nas.

**Origem:** centro da planta da casa, no pavimento acabado do rés do chão (escala real em metros).

**Fundação na versão casa:** o telemóvel pousa o ponto mais baixo do modelo no chão real, por isso a fundação indicativa é cortada 0,2 m abaixo do pavimento e o soco fica visível.

**Pisos** (níveis dos pavimentos acabados, a partir do rés do chão: 0,00 m, 2,96 m):
- `casa_pisoN`: o piso N sozinho à escala real, de 0,2 m abaixo do pavimento até logo abaixo do piso de cima (o último sem a cobertura), com o pavimento na origem. O telemóvel pousa-o no chão e anda-se lá dentro.
- `maquete_pisoN`: a casa com o terreno, aberta até ao piso N (o que está por cima é cortado e os tetos desse piso tirados), para ver as divisões de cima.
- Os cortes são fechados, para as paredes não parecerem ocas vistas de cima.


**Reabertos num Blender limpo** (triângulos, dimensões, texturas):

- casa glb: 11354 triângulos, [13.099, 11.249, 7.543] m, 13 texturas, 0 em falta
- casa usdz: 11354 triângulos, [13.099, 11.249, 7.543] m, 13 texturas, 0 em falta
- maquete glb: 11990 triângulos, [53.369, 51.497, 10.5] m, 16 texturas, 0 em falta
- maquete usdz: 11990 triângulos, [53.369, 51.497, 10.5] m, 16 texturas, 0 em falta
- casa_piso0 glb: 4130 triângulos, [13.099, 11.249, 3.152] m, 11 texturas, 0 em falta
- casa_piso0 usdz: 4130 triângulos, [13.099, 11.249, 3.152] m, 13 texturas, 0 em falta
- maquete_piso0 glb: 3766 triângulos, [53.369, 51.497, 10.5] m, 14 texturas, 0 em falta
- maquete_piso0 usdz: 3766 triângulos, [53.369, 51.497, 10.5] m, 16 texturas, 0 em falta
- casa_piso1 glb: 4242 triângulos, [10.011, 6.261, 4.476] m, 8 texturas, 0 em falta
- casa_piso1 usdz: 4242 triângulos, [10.011, 6.261, 4.476] m, 11 texturas, 0 em falta
- maquete_piso1 glb: 7608 triângulos, [53.369, 51.497, 10.5] m, 14 texturas, 0 em falta
- maquete_piso1 usdz: 7608 triângulos, [53.369, 51.497, 10.5] m, 14 texturas, 0 em falta

**Por testar:** abrir em telemóveis reais (Scene Viewer num Android, Quick Look num iPhone) e medir o tempo de carregamento e a qualidade ao lado das fotos da casa construída (tarefas 84 e 158).
