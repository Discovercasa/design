# Exportação · Sobral · Casa Tipo 1 no lote P

**Resultado: WARNING**

- fbx: os bytes mudam entre exportações (data no ficheiro), o conteúdo é igual
- usdz: os bytes mudam entre exportações (data no ficheiro), o conteúdo é igual

Gerado por `step-inside/ferramentas/exportar/exportar.py` a partir do modelo de visita. Os ficheiros e o `manifest.json` completo ficam só no PC (`_trabalho/step-inside/<obra>/export/a/`).

- Versão: `sobral-tipo1-8232d36-202611101631` · Blender 4.4.3 · Unreal alvo 5.8 (a confirmar na Fase 4)
- Fonte: 261 objetos, 53902 triângulos, 16 materiais, 19 imagens; caixa [409.727, 276.992, 100.88] m

| Ficheiro | Para quê | Tamanho | SHA-256 | Determinístico |
|---|---|---|---|---|
| `sobral-tipo1_visita.fbx` | Unreal (Fases 4–5) | 2,1 MB | `0e47074da64a…` | conteúdo igual |
| `sobral-tipo1_visita.glb` | AR Android / visualizador 3D | 106,1 MB | `7ad3a3cdf706…` | sim (bytes iguais) |
| `sobral-tipo1_visita.usdz` | AR Quick Look (iPhone) | 94,5 MB | `6eadd0f91fd6…` | conteúdo igual |
| texturas do FBX | textura PBR do FBX (ficheiro separado, spec §4.2) | 91,5 MB | 19 ficheiros | — |

## Reimportação (Blender limpo) e comparação

| Formato | Objetos | Triângulos | Caixa (m) | Erro da caixa | Materiais | Imagens (em falta) | Píxeis diferentes | Silhueta |
|---|---|---|---|---|---|---|---|---|
| fbx | 261 | 53902 | [409.727, 276.992, 100.88] | 0.0 | 16 | 19 (0) | 1.1 % | 0.00 % |
| glb | 261 | 53902 | [409.727, 276.992, 100.88] | 0.0 | 16 | 19 (0) | 0.0 % | 0.00 % |
| usdz | 261 | 53902 | [409.727, 276.992, 100.88] | 0.0 | 16 | 19 (0) | 0.5 % | 0.04 % |

## Sistemas de coordenadas

- **fonte**: Blender: metros, Z para cima, X para este, Y para norte (origem local do terreno)
- **fbx**: FBX: metros (FBX_SCALE_UNITS), eixo -Z para a frente, Y para cima; no Unreal importar com 'Convert Scene'
- **glb**: glTF 2.0: metros, +Y para cima (norma)
- **usdz**: USD: metersPerUnit 1, upAxis Y

A imagem de comparação usa a mesma câmara, luz plana e a cor das texturas: mede se a geometria, a posição e os materiais chegam iguais, não o aspeto final.
