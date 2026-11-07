# Relatório de faltas e conflitos — Casa Torres Vedras (construída; obra D2503)

Gerado a partir de `fontes.json` (entrada: planta_arquitetura; configuração `config.json`). Antes de gerar a geometria.

**Resultado: WARNING** — pode gerar-se a geometria; os avisos ficam marcados no modelo. (2 campo(s) inferido(s); 10 campo(s) em falta, não essenciais)

| CONFIRMED | INFERRED | MISSING | NEEDS_HUMAN_REVIEW | Conflitos abertos | Conflitos resolvidos |
|---|---|---|---|---|---|
| 202 | 2 | 10 | 0 | 0 | 29 |

## Em falta (MISSING)

| Campo | N.º | Valor | Método | Fonte | Nota |
|---|---|---|---|---|---|
| `referencial.norte` | 1 | — | nenhum | — | Os alçados chamam-se Sudeste, Noroeste, Nordeste e Sudoeste: os eixos da casa estão rodados em relação ao norte. A direção exata lê-se na planta de implantação (Fase 2). |
| `referencial.crs` | 1 | — | nenhum | — | Sem georreferência: o modelo está em coordenadas locais. |
| `terreno.crs`, `terreno.datum_vertical`, `terreno.unidade_horizontal`, `terreno.unidade_vertical`, `terreno.limite_lote`, `terreno.data_levantamento`, `terreno.precisao`, `terreno.pontos_controlo` | 8 | — | nenhum | — | No DWFx e no PDF do levantamento as cotas estão desenhadas como contornos (sem texto): para as ler é preciso o DWG exportado para DXF (Fase 2). |

## Inferidos (INFERRED)

| Campo | N.º | Valor | Método | Fonte | Nota |
|---|---|---|---|---|---|
| `referencial.cota_referencia` | 1 | 117.5 m | inferencia | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (CORTE A) | 117,50 é a cota do pavimento interior acabado; o Z = 0 do modelo é o topo da laje, uns milímetros abaixo (espessura do pavimento). Confirmar com o levantamento na Fase 2. |
| `lajes.fundacao.espessura` | 1 | 0.2 m | inferencia | config.json (configuração do modelo) (fundacao.espessura_laje) | Base de fundação DiscoverCasa — o utilizador vai explicar como a fazem; aqui só indicativa (laje 20 cm sob a casa). |

## Conflitos resolvidos (o que prevaleceu)

| Campo | Usado | Fonte usada | Outro valor | Outra fonte | Resolução |
|---|---|---|---|---|---|
| `niveis.pe_direito` | 2.5 m | 250828_D2503_Cobertura.dwfx, folha 5 (Secções 1:50) | 2.6 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (CORTE A) | Prevalece o D2503 (como construído). |
| `paredes.P01.aberturas.0.tipo` | porta | 250828_D2503_Modulos.dwfx (módulo M9) | janela | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P01.aberturas.0.altura` | 2.4 m | 250828_D2503_Modulos.dwfx (módulo M9) | 2.2 | config.json (configuração do modelo) (aberturas.porta_exterior.altura) | Prevalece o desenho de módulos (como construído). |
| `paredes.P02.aberturas.0.largura` | 0.87 m | 250828_D2503_Modulos.dwfx (módulo M15) | 0.8 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P03.aberturas.0.tipo` | porta | 250828_D2503_Modulos.dwfx (módulo M1) | janela | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P03.aberturas.1.altura` | 2.4 m | 250828_D2503_Modulos.dwfx (módulo M3) | 2.2 | config.json (configuração do modelo) (aberturas.porta_exterior.altura) | Prevalece o desenho de módulos (como construído). |
| `paredes.P03.aberturas.2.largura` | 1.04 m | 250828_D2503_Modulos.dwfx (módulo M5) | 0.91 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P05.aberturas.0.largura` | 0.87 m | 250828_D2503_Modulos.dwfx (módulo M12) | 0.8 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P08.aberturas.0.largura` | 0.87 m | 250828_D2503_Modulos.dwfx (módulo M6) | 0.8 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P10.aberturas.0.largura` | 0.87 m | 250828_D2503_Modulos.dwfx (módulo M8) | 0.8 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P11.aberturas.0.largura` | 0.94 m | 250828_D2503_Modulos.dwfx (módulo M23) | 0.8 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P11.aberturas.1.peitoril` | 1.036 m | 250828_D2503_Modulos.dwfx (módulo M20) | 1.0 | config.json (configuração do modelo) (aberturas.janela.peitoril) | Prevalece o desenho de módulos (como construído). |
| `paredes.P11.aberturas.1.altura` | 1.986 m | 250828_D2503_Modulos.dwfx (módulo M20) | 1.75 | config.json (configuração do modelo) (aberturas.janela.topo) | Prevalece o desenho de módulos (como construído). |
| `paredes.P11.aberturas.2.peitoril` | 1.036 m | 250828_D2503_Modulos.dwfx (módulo M18) | 1.0 | config.json (configuração do modelo) (aberturas.janela.peitoril) | Prevalece o desenho de módulos (como construído). |
| `paredes.P11.aberturas.2.altura` | 1.785 m | 250828_D2503_Modulos.dwfx (módulo M18) | 1.75 | config.json (configuração do modelo) (aberturas.janela.topo) | Prevalece o desenho de módulos (como construído). |
| `paredes.P12.aberturas.0.peitoril` | 1.035 m | 250828_D2503_Modulos.dwfx (módulo M24) | 1.0 | config.json (configuração do modelo) (aberturas.janela.peitoril) | Prevalece o desenho de módulos (como construído). |
| `paredes.P12.aberturas.0.altura` | 1.985 m | 250828_D2503_Modulos.dwfx (módulo M24) | 1.75 | config.json (configuração do modelo) (aberturas.janela.topo) | Prevalece o desenho de módulos (como construído). |
| `paredes.P13.aberturas.0.largura` | 0.871 m | 250828_D2503_Modulos.dwfx (módulo M4) | 0.8 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P14.aberturas.0.tipo` | janela | 250828_D2503_Modulos.dwfx (módulo M6) | porta | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P14.aberturas.0.peitoril` | 1.035 m | 250828_D2503_Modulos.dwfx (módulo M6) | 1.0 | config.json (configuração do modelo) (aberturas.janela.peitoril) | Prevalece o desenho de módulos (como construído). |
| `paredes.P14.aberturas.0.altura` | 1.785 m | 250828_D2503_Modulos.dwfx (módulo M6) | 1.75 | config.json (configuração do modelo) (aberturas.janela.topo) | Prevalece o desenho de módulos (como construído). |
| `paredes.P15.aberturas.0.largura` | 0.871 m | 250828_D2503_Modulos.dwfx (módulo M17) | 0.8 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P17.aberturas.0.largura` | 0.871 m | 250828_D2503_Modulos.dwfx (módulo M21) | 0.8 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P17.aberturas.1.largura` | 0.871 m | 250828_D2503_Modulos.dwfx (módulo M21) | 0.8 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P18.aberturas.0.tipo` | porta | 250828_D2503_Modulos.dwfx (módulo M12) | janela | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P18.aberturas.0.altura` | 2.4 m | 250828_D2503_Modulos.dwfx (módulo M12) | 2.2 | config.json (configuração do modelo) (aberturas.porta_exterior.altura) | Prevalece o desenho de módulos (como construído). |
| `paredes.P18.aberturas.1.tipo` | porta | 250828_D2503_Modulos.dwfx (módulo M14) | janela | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (planta, região 120–215 × 192–258 mm da folha) | Prevalece o desenho de módulos (como construído). |
| `paredes.P18.aberturas.1.altura` | 2.4 m | 250828_D2503_Modulos.dwfx (módulo M14) | 2.2 | config.json (configuração do modelo) (aberturas.porta_exterior.altura) | Prevalece o desenho de módulos (como construído). |
| `cobertura.inclinacao_pct` | 6 % | 250828_D2503_Cobertura.dwfx, folha 2 (Vigas de pendente (madres)) | 1.3 | projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx, folha 1 (CORTE B) | Prevalece o D2503 (como construído). |

## Documentos

| Ficheiro | Formato | Categoria | Usado para |
|---|---|---|---|
| projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx | DWFX | DIRECT | planta (paredes e vãos) |
| 250828_D2503_Modulos.dwfx | DWFX | DIRECT | vãos e módulos como construídos |
| 250828_D2503_Cobertura.dwfx | DWFX | DIRECT | níveis (secções 1:50), cobertura como construída |
| Levantamento topográfico F00.0.dwg | DWG | CONVERT_REQUIRED | terreno (Fase 2) |
| Planta de implantação F01,1.dwfx | DWFX | DIRECT | implantação no lote (Fase 2) |
| 20241024.PL_LA_muros-F05.1_MUROS.dwfx | DWFX | DIRECT | — |
| 20241024.PL_LA_muros-F05.1_MUROS.dwg | DWG | CONVERT_REQUIRED | — |
| 20241024.PL_LA_muros-F05.1_MUROS.pdf | PDF | DIRECT | — |
| Levantamento topográfico F00.0.dwfx | DWFX | DIRECT | — |
| Levantamento topográfico F00.0.pdf | PDF | DIRECT | — |
| Planta de implantação F01,1.dwg | DWG | CONVERT_REQUIRED | — |
| Planta de implantação F01,1.pdf | PDF | DIRECT | — |
| planta localização.pdf | PDF | DIRECT | — |
| projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwg | DWG | CONVERT_REQUIRED | — |
| projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.pdf | PDF | DIRECT | — |
