# Exportação · Torres Vedras · casa no lote

**Resultado: WARNING**

- fbx: os bytes mudam entre exportações (data no ficheiro), o conteúdo é igual
- usdz: os bytes mudam entre exportações (data no ficheiro), o conteúdo é igual

Gerado por `step-inside/ferramentas/exportar/exportar.py` a partir do modelo de visita. Os ficheiros e o `manifest.json` completo ficam só no PC (`_trabalho/step-inside/<obra>/export/a/`).

- Versão: `torres-vedras-ccc3f10-202611090125` · Blender 4.4.3 · Unreal alvo 5.8 (a confirmar na Fase 4)
- Fonte: 310 objetos, 52839 triângulos, 18 materiais, 26 imagens; caixa [80.899, 82.831, 6.226] m

| Ficheiro | Para quê | Tamanho | SHA-256 | Determinístico |
|---|---|---|---|---|
| `torres-vedras_visita.fbx` | Unreal (Fases 4–5) | 2,1 MB | `d7284c499458…` | conteúdo igual |
| `torres-vedras_visita.glb` | AR Android / visualizador 3D | 109,1 MB | `9a6289f76321…` | sim (bytes iguais) |
| `torres-vedras_visita.usdz` | AR Quick Look (iPhone) | 95,9 MB | `d3ce4864476d…` | conteúdo igual |
| texturas do FBX | textura PBR do FBX (ficheiro separado, spec §4.2) | 93,1 MB | 26 ficheiros | — |

## Reimportação (Blender limpo) e comparação

| Formato | Objetos | Triângulos | Caixa (m) | Erro da caixa | Materiais | Imagens (em falta) | Píxeis diferentes | Silhueta |
|---|---|---|---|---|---|---|---|---|
| fbx | 310 | 52839 | [80.899, 82.831, 6.226] | 0.0 | 18 | 26 (0) | 0.9 % | 0.00 % |
| glb | 310 | 52839 | [80.899, 82.831, 6.226] | 0.0 | 18 | 26 (0) | 0.9 % | 0.00 % |
| usdz | 310 | 52839 | [80.899, 82.831, 6.226] | 0.0 | 18 | 26 (0) | 0.3 % | 0.00 % |

## Sistemas de coordenadas

- **fonte**: Blender: metros, Z para cima, X para este, Y para norte (origem local do terreno)
- **fbx**: FBX: metros (FBX_SCALE_UNITS), eixo -Z para a frente, Y para cima; no Unreal importar com 'Convert Scene'
- **glb**: glTF 2.0: metros, +Y para cima (norma)
- **usdz**: USD: metersPerUnit 1, upAxis Y

A imagem de comparação usa a mesma câmara, luz plana e a cor das texturas: mede se a geometria, a posição e os materiais chegam iguais, não o aspeto final.
