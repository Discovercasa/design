# Matriz de formatos (tarefa 55)

Fonte de verdade em código: `step-inside/ferramentas/fontes/matriz.py` (o catálogo usa-a). Atualiza a tabela da §6 da
auditoria: o DXF passou a `CONVERT_REQUIRED` e entraram os formatos de terreno.

| Categoria | Significado |
|---|---|
| `DIRECT` | Há um leitor; tiram-se geometria e valores |
| `CONVERT_REQUIRED` | Serve depois de exportado para um formato `DIRECT` |
| `REFERENCE_ONLY` | Só para ver; não se tira nada dele |
| `UNSUPPORTED` | Ainda sem leitor |

| Formato | Categoria | Leitor ou o que fazer | Nota |
|---|---|---|---|
| DWFx | DIRECT | `ferramentas/dwfx/leitor.py` | Plot 2D: traços com cor e espessura, e texto quando o AutoCAD o escreve como texto. Só tem 3D se trouxer um modelo (o catálogo verifica). |
| PDF vetorial | DIRECT | `ferramentas/dwfx/leitor_pdf.py` | Os mesmos traços do DWFx, **sem texto**. |
| PDF digitalizado ou imagem | REFERENCE_ONLY | — | Não dá geometria. O catálogo distingue-o pelo número de traços. |
| JSON do configurador | DIRECT | `ferramentas/configurador/para_construtor.py` | Casa do Build Your House. |
| DWG | CONVERT_REQUIRED | Exportar para DWFx ou PDF (plantas, cortes), ou para DXF (levantamento) | Formato fechado, sem leitor. Tem a informação toda, incluindo as cotas 3D do levantamento. |
| DXF | CONVERT_REQUIRED | Exportar para DWFx/PDF; ou um leitor DXF na Fase 2 | Texto aberto: um leitor só com Python é viável para pontos e curvas de nível 3D. |
| DWF (antigo) | CONVERT_REQUIRED | Voltar a exportar como DWFx | Binário. |
| IFC, Revit | UNSUPPORTED | Pedir DWFx/PDF | Só se algum arquiteto entregar BIM. |
| SketchUp `.skp` | REFERENCE_ONLY | — | Só para ver. |
| Imagens e fotos | REFERENCE_ONLY | — | Nunca se faz um terreno a partir de uma imagem aérea (especificação §3.5). |
| Memória descritiva, mapas (`.docx`, `.xlsx`, `.txt`) | REFERENCE_ONLY | — | Para ler e confrontar com os desenhos. |
| GeoTIFF / DEM (`.tif`) | UNSUPPORTED | Leitor previsto na Fase 2 | Se for só uma imagem: REFERENCE_ONLY. |
| LandXML | UNSUPPORTED | Leitor previsto na Fase 2 | Superfície topográfica. |
| Pontos XYZ / CSV | UNSUPPORTED | Leitor previsto na Fase 2 | Precisa de unidade, CRS e cota. |
| Nuvem de pontos LAS/LAZ | UNSUPPORTED | — | Só se houver levantamento por drone ou laser. |

**Regra:** um formato só passa a `DIRECT` quando houver um leitor com testes.
