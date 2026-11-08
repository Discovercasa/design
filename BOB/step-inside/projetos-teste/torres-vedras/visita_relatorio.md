# Modelo de visita · Torres Vedras · casa

**Resultado: WARNING**

- 36 choques entre peças de madeira > 8 mm no modelo de produção (verificar.py)
- chão provisório plano: não é terreno (falta o levantamento)

Gerado por `step-inside/ferramentas/visita/visita.py` a partir de `visita.json`. O modelo de visita fica só no PC (`_trabalho/step-inside/<obra>/visita/`): tem a posição real da casa.

## O que se reutilizou

- Modelo de produção: `Construção Torres Vedras/modelos/casa/Casa_TorresVedras.blend` (gerado por `ferramentas/modelo/construir_casa.py`, aberto sem o mudar).
- Fontes da Fase 1: `fontes.json` (dimensões, paredes e aberturas com a origem de cada valor).
- Choques da madeira: `ferramentas/modelo/verificar.py`.

## Coleções semânticas

| Coleção | Objetos | Na visita |
|---|---|---|
| ARCH_CEILINGS | 40 | sim |
| ARCH_FLOORS | 8 | sim |
| ARCH_FOUNDATION | 1 | sim |
| ARCH_LABELS | 8 | não (fica no ficheiro) |
| ARCH_OPENINGS | 50 | sim |
| ARCH_PERGOLA | 4 | sim |
| ARCH_ROOF | 116 | sim |
| ARCH_WALLS_EXT | 24 | sim |
| ARCH_WALLS_INT | 66 | sim |
| STRUCT_TIMBER | 880 | não (fica no ficheiro) |

Cada objeto tem `si_id` = `<coleção>/<nome do objeto>` (os nomes vêm dos desenhos e não mudam), `si_categoria`, `si_colecao_producao` e `si_material`.

## Implantação

| Campo | Valor | Estado | Método | Nota |
|---|---|---|---|---|

## Verificações

- **Dimensões:** estrutura do modelo 17,500 × 10,999 m; fontes 17,501 × 11,000 m (diferença 0,001 m). Contorno acabado 17,632 × 11,132 m.
- **Malhas:** 309 objetos visíveis; abertas 0, normais para dentro 0, repetidos 0.
- **Aberturas:** 19 das fontes procuradas no modelo (raios horizontais através da parede, de 0,3 a 2,0 m acima do piso); fechadas: 0. Controlo: 14 troços de parede cheia, vistos como abertos: 0.
- **Choques da madeira** (verificar.py, > 8 mm): 36 em 736 peças — Prumo x Prumo: 18, Amarração x Viga: 10, Amarração x Amarração: 5, PI x PI: 3.
- **Chão provisório:** plano de 60 m à cota 0,00 do modelo. Não é terreno: falta o levantamento.

## Ficheiros (só no PC)

- `visita.blend` (coleções VISITA > SITE / HOUSE), `visita.glb` (o que está visível), `preview.png`.
