# Relatório de faltas e conflitos — Sobral · Casa Tipo 1 (loteamento; 11 casas)

Gerado a partir de `fontes.json` (entrada: desenhos_engenheiro; configuração `config.json`). Antes de gerar a geometria.

**Resultado: NEEDS_HUMAN_REVIEW** — uma pessoa tem de rever os pontos abaixo antes de gerar a geometria. (1 campo(s) a rever; 1 conflito(s) aberto(s))

| CONFIRMED | INFERRED | MISSING | NEEDS_HUMAN_REVIEW | Conflitos abertos | Conflitos resolvidos |
|---|---|---|---|---|---|
| 215 | 134 | 10 | 1 | 1 | 5 |

## Conflitos abertos

- `paredes.PI1.08.aberturas.0.altura`: Porta com 1.50 m de altura livre: confirmar se é uma porta ou outro tipo de vão.

## Para rever (NEEDS_HUMAN_REVIEW)

| Campo | N.º | Valor | Método | Fonte | Nota |
|---|---|---|---|---|---|
| `paredes.*.aberturas.*.tipo` | 1 | porta | inferencia | arquitetura (configuração: estrutura.paredes_extra / portas_extra) (PORTA_EXTRA.0) | Tipo de porta por confirmar: Lavandaria 0.5: lado nascente aberto em 1,4 m com porta (de correr?) — bandeira por cima (arquitetura SMA_012 f.17). |

## Em falta (MISSING)

| Campo | N.º | Valor | Método | Fonte | Nota |
|---|---|---|---|---|---|
| `referencial.crs`, `referencial.cota_referencia` | 2 | — | nenhum | — | Sem georreferência: o modelo está em coordenadas locais. (+1 nota(s) diferente(s); ver fontes.json) |
| `terreno.crs`, `terreno.datum_vertical`, `terreno.unidade_horizontal`, `terreno.unidade_vertical`, `terreno.limite_lote`, `terreno.data_levantamento`, `terreno.precisao`, `terreno.pontos_controlo` | 8 | — | nenhum | — | Lote plano (Casa Tipo 1). O levantamento do loteamento tem as cotas em texto (folhas 2 e 4 da arquitetura, cerca de 200–300 m): ler na Fase 2. |

## Inferidos (INFERRED)

| Campo | N.º | Valor | Método | Fonte | Nota |
|---|---|---|---|---|---|
| `referencial.norte` | 1 | +Y | inferencia | PD_Habitacoes A B C D E K L M N O P (1).dwfx, folha 2 (cortes das fachadas) | O extrator põe Y para norte, pelas fachadas identificadas nos desenhos (docs/desenhos.md); falta confirmar com a planta de implantação. |
| `niveis.osb_pavimento` | 1 | 0.018 m | inferencia | config.json (configuração do modelo) (niveis.osb_pavimento) |  |
| `paredes.*.aberturas.*.tipo`, `paredes.*.aberturas.*.inicio`, `paredes.*.aberturas.*.fim`, `paredes.*.aberturas.*.peitoril`, `paredes.*.aberturas.*.altura`, `paredes.*.inicio`, `paredes.*.fim`, `paredes.*.posicao`, `paredes.*.espessura` | 94 | 52 valores | geometria | PD_Habitacoes A B C D E K L M N O P (1).dwfx, folha 2 (18 locais) |  (+5 nota(s) diferente(s); ver fontes.json) |
| `paredes.*.aberturas.*.largura` | 17 | 11 valores | calculo | PD_Habitacoes A B C D E K L M N O P (1).dwfx, folha 2 (17 locais) | Intervalo entre as peças do painel: as portas e janelas não têm medidas nos desenhos do engenheiro. Acima da base do painel (piso estrutural). |
| `paredes.*.aberturas.*.tipo`, `paredes.*.aberturas.*.peitoril`, `paredes.*.aberturas.*.altura` | 3 | 3 valores | inferencia | arquitetura (configuração: estrutura.aberturas_alterar) (PE2.08) | Janela da casa de banho 1.2 no alçado nascente (arquitetura SMA_012 f.18: topo +4,88 = Z 5,04, cerca de 0,47 x 0,99 m); nos desenhos do engenheiro era uma abertura alta. |
| `paredes.*.inicio`, `paredes.*.fim`, `paredes.*.posicao`, `paredes.*.aberturas.*.tipo`, `paredes.*.aberturas.*.inicio`, `paredes.*.aberturas.*.fim` | 14 | 12 valores | inferencia | arquitetura (configuração: estrutura.paredes_extra / portas_extra) (3 locais) | WC 0.6 (inst. sanitária): parede nascente com porta 0,87 para a entrada (arquitetura SMA_012 f.17). (+2 nota(s) diferente(s); ver fontes.json) |
| `paredes.*.aberturas.*.largura` | 2 | 2 valores | calculo | arquitetura (configuração: estrutura.paredes_extra / portas_extra) (2 locais) |  |
| `cobertura.cumeeira_y`, `cobertura.cumeeira_z` | 2 | 2 valores | inferencia | config.json (configuração do modelo) (2 locais) |  |

## Conflitos resolvidos (o que prevaleceu)

| Campo | Usado | Fonte usada | Outro valor | Outra fonte | Resolução |
|---|---|---|---|---|---|
| `paredes.PE2.08.aberturas.0.tipo` | janela | arquitetura (configuração: estrutura.aberturas_alterar) (PE2.08) | porta | PD_Habitacoes A B C D E K L M N O P (1).dwfx, folha 2 (alçado PE2.08) | Prevalece a arquitetura (vão corrigido na configuração). |
| `paredes.PE2.08.aberturas.0.peitoril` | 1.09 m | arquitetura (configuração: estrutura.aberturas_alterar) (PE2.08) | 0.08 | PD_Habitacoes A B C D E K L M N O P (1).dwfx, folha 2 (alçado PE2.08) | Prevalece a arquitetura (vão corrigido na configuração). |
| `paredes.PE2.08.aberturas.0.altura` | 2.08 m | arquitetura (configuração: estrutura.aberturas_alterar) (PE2.08) | 2.768 | PD_Habitacoes A B C D E K L M N O P (1).dwfx, folha 2 (alçado PE2.08) | Prevalece a arquitetura (vão corrigido na configuração). |

## Documentos

| Ficheiro | Formato | Categoria | Usado para |
|---|---|---|---|
| PD_Habitacoes A B C D E K L M N O P (1).dwfx | DWFX | DIRECT | paredes, vãos, pavimento e cobertura (desenhos do engenheiro) |
| SMA_012_arquitectura_pecas_desenhadas.dwfx | DWFX | DIRECT | vãos e paredes corrigidos pela arquitetura (folhas 17–18), terreno do loteamento (folhas 2 e 4, Fase 2) |
| PD_Estabilidade Armazém.dwfx | DWFX | DIRECT | — |
| PD_Habitacoes F G H I J.dwfx | DWFX | DIRECT | — |
