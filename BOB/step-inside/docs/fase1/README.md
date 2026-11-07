# Step Inside · Fase 1 — Contrato de dados e qualidade de entrada

**Data:** 2026-11-07. **Âmbito:** tarefas 52–56 do hub (checkpoint «Fase 1 · Contrato de dados e qualidade de
entrada»). **Referência:** especificação técnica v2, §3.2, §3.3, §3.5, §13 Fase 1 e §14.1.

**Custo:** 0 €. Só Python (biblioteca padrão). Nada em produção: o motor, as configurações das casas e o site ficam
iguais. As ferramentas novas leem o que o motor já usa e escrevem uma camada por cima.

---

## 1. Resumo

| Tarefa | Estado | Entregável |
|---|---|---|
| 52 · Escolher dois projetos de teste | Decidido (utilizador, 2026-11-07: «Sobral Tipo 1») | **Torres Vedras** (térrea, construída, com levantamento real) e **Sobral Tipo 1** (dois pisos, lote plano, desenhos do engenheiro) |
| 53 · Catalogar plantas, cortes, alçados, cotas e topografia | Feito | `projetos-teste/<obra>/catalogo.md` |
| 54 · Schema com proveniência e confiança por campo | Feito | `schema/fontes_projeto.schema.json` + `ferramentas/fontes/proveniencia.py` |
| 55 · Matriz de formatos | Feito | [`matriz-formatos.md`](matriz-formatos.md) + `ferramentas/fontes/matriz.py` |
| 56 · Relatório de faltas e conflitos antes de gerar geometria | Feito | `ferramentas/fontes/relatorio.py` → `projetos-teste/<obra>/relatorio.md` |
| Nova · Proveniência para o segundo projeto (desenhos do engenheiro) | Feito | Entrada `desenhos_engenheiro` no `proveniencia.py` → `projetos-teste/sobral-tipo1/` |

**Critério de saída da especificação:** «as informações confirmadas/inferidas/em falta são distinguíveis e os conflitos
são reportados».
- **Cumprido nos dois projetos de teste**, com as duas entradas do motor: a planta de arquitetura e os desenhos do
  engenheiro.
- Os leitores existentes têm testes de regressão: voltam a ler os desenhos e têm de dar a planta e os painéis
  guardados (§6).

## 2. Como funciona

```text
desenhos (PC, fora do Git) ──catalogar.py──► catalogo.json/.md   (formato, categoria, folhas, vistas, escalas)
config.json + planta_paredes.json ─┐
modulos_reais (desenho de módulos) ├──proveniencia.py──► fontes.json   (cada valor com origem e estado)
declaracoes.json (à mão) ──────────┘                       │
                                                           └──relatorio.py──► relatorio.md (PASS / WARNING /
                                                                              NEEDS_HUMAN_REVIEW / FAIL)
```

Os comandos correm a partir de `BOB/`:

```text
python step-inside/ferramentas/fontes/catalogar.py "<pasta dos desenhos>" --json <obra>/catalogo.json --md <obra>/catalogo.md
python step-inside/ferramentas/fontes/proveniencia.py "<obra>/modelos/casa/config.json" --declaracoes <obra>/declaracoes.json --catalogo <obra>/catalogo.json --saida <obra>/fontes.json
python step-inside/ferramentas/fontes/relatorio.py <obra>/fontes.json --md <obra>/relatorio.md
python -m unittest discover -s step-inside/tests -v
```

**Cada valor (campo) leva** (especificação §3.2):
- `valor` e `unidade`;
- `tipo`: cota, nível, dimensão, geometria, escala, material ou terreno;
- `estado`: `CONFIRMED`, `INFERRED`, `MISSING` ou `NEEDS_HUMAN_REVIEW`;
- `metodo`: geometria, texto, inferência, valor por omissão, norma da empresa, desenho da empresa, utilizador ou
  cálculo;
- `fonte`: documento, folha e local;
- `nota`;
- `conflitos`: os outros valores, de onde vêm e qual prevaleceu.

**Regras sem declaração** (nada se inventa, regra 9 da especificação):
- **Geometria lida da planta:** fica com o estado da escala. Com uma escala deduzida, as paredes ficam `INFERRED`.
- **Valores escritos na configuração sem fonte conhecida:** `INFERRED`. Ficam `NEEDS_HUMAN_REVIEW` se a nota disser
  «a confirmar».
- **Valores por omissão do motor** (por exemplo, a altura de uma porta exterior quando nenhum desenho a dá):
  `NEEDS_HUMAN_REVIEW`.
- **Regras do método DiscoverCasa** (por exemplo, o vão de porta interior 0,87 × 2,03): `CONFIRMED` com a fonte «norma
  da empresa». O método decide como se constrói; não é um palpite.
- **Desenho de módulos da DiscoverCasa (`modulos_reais`), quando existe:** os vãos ficam como construídos. As diferenças
  para a planta e a configuração ficam registadas como conflitos resolvidos.
- **O que ninguém deu** (norte, CRS, terreno): `MISSING`.

**`declaracoes.json` (à mão, por obra):**
- diz de onde vêm os valores que a planta não dá, como o pé direito do D2503 ou o que o utilizador confirmou;
- as chaves são caminhos de campos, e `*` vale qualquer parte;
- uma declaração com outro valor abre um conflito;
- uma declaração que não encontra o seu campo dá um aviso.

**Resultado do relatório:**

| Resultado | Quando | Pode gerar-se a geometria? |
|---|---|---|
| `PASS` | tudo confirmado, sem conflitos | Sim |
| `WARNING` | há valores inferidos, ou em falta mas não essenciais (por exemplo, o terreno) | Sim, com os avisos marcados |
| `NEEDS_HUMAN_REVIEW` | há valores a rever, um valor essencial em falta (escala, dimensões, pé direito, paredes) ou um conflito aberto | Só depois de uma pessoa rever |
| `FAIL` | as fontes contradizem-se: vão fora da parede, vãos sobrepostos, peitoril acima do topo, erro de schema | Não |

## 3. Resultados

### Torres Vedras (casa construída; planta de arquitetura + desenhos D2503 da DiscoverCasa)

**Resultado: `WARNING`.** Pode gerar-se a geometria. Os campos ficam assim:

| Estado | Campos |
|---|---|
| CONFIRMED | 202 |
| INFERRED | 2 |
| MISSING | 10 |
| NEEDS_HUMAN_REVIEW | 0 |

Há **29 conflitos resolvidos** (ver `projetos-teste/torres-vedras/relatorio.md`).

**Os 19 vãos da planta batem um a um com os 19 do desenho D2503 Módulos.** As diferenças que ficam registadas, e em
que prevalece o D2503, são:
- **Portas de correr:** 2,40 de altura no D2503; a configuração dizia 2,20 (dos alçados).
- **Entrada e porta de serviço:** vãos de 1,04 e 0,94; a planta tem 0,91 e 0,80.
- **Janelas:** peitoril 1,035 e topos 1,785 / 1,985; a configuração dizia 1,00 / 1,75.
- **Portas interiores:** vão DiscoverCasa 0,87; a porta do arquiteto é de 0,80.
- **Tipo de vão:** 5 vãos que a planta desenha como janela ou porta e que os alçados e o D2503 corrigem.

**Duas declarações com conflito resolvido:**
- **Pé direito:** 2,50 no D2503; 2,60 na arquitetura.
- **Inclinação da cobertura:** 6 % no D2503; 1,3 % no corte B.

**Inferidos:**
- a cota absoluta do Z = 0 (117,50 é o pavimento acabado, não o topo da laje);
- a espessura da base de fundação, que é indicativa.

**Em falta:**
- o norte e o CRS;
- os 8 metadados do terreno.

Nada disto impede gerar a casa; impede a Fase 2.

### Sobral Tipo 1 (dois pisos; desenhos do engenheiro + arquitetura)

**Resultado: `NEEDS_HUMAN_REVIEW`.** Há duas perguntas reais, que já estavam abertas no projeto. Os campos ficam assim:

| Estado | Campos |
|---|---|
| CONFIRMED | 215 |
| INFERRED | 134 |
| MISSING | 10 |
| NEEDS_HUMAN_REVIEW | 1 |

Há 5 conflitos resolvidos.

**Para rever:**
- **Porta da lavandaria:** o lado nascente está aberto 1,40 m, e a configuração diz «porta (de correr?)». Falta saber
  o tipo de porta.
- **Vão do painel PI1.08:** tem 1,50 m de altura livre. Falta saber se é uma porta ou outro tipo de vão.

**O que fica confirmado ou deduzido:**
- **Escala 1:50:** confirmada, porque está escrita nas folhas usadas (catálogo).
- **Paredes:** os 53 painéis vêm dos alçados do engenheiro, colocados pela planta de paredes. Ficam `INFERRED`
  quando o encaixe dos montantes é incompleto ou a posição foi corrigida à mão.
- **Painéis retirados:** os dois painéis da conduta (PI2.09/PI2.10) ficam como conflito resolvido.
- **Paredes acrescentadas pela arquitetura:** PD1.01, PD2.01 e a porta da lavandaria, todas `INFERRED`.
- **Medidas dos vãos: `INFERRED`.** O engenheiro desenha os vãos como intervalos entre peças e não dá as medidas das
  portas e janelas (revisão técnica #5).
- **Janela do WC do piso de cima:** está corrigida pela arquitetura (folha 18). Prevalece a arquitetura sobre a
  abertura alta do engenheiro.

**Em falta:**
- o CRS e a cota absoluta;
- os 8 metadados do terreno. O lote é plano, e o levantamento do loteamento existe, com as cotas em texto.

### Sobral (loteamento): catálogo

- **Arquitetura:** 22 folhas com texto legível. Inclui o levantamento (folha 2, «LEV_PL», 1:500) e a modelação do
  terreno (folha 4, «MOD_PL»).
- **Cotas do terreno em texto:**
  - 447 dos 451 números da folha 2 e 488 dos 491 da folha 4 estão entre 200 e 300 m;
  - são coerentes com as cotas do loteamento (pisos do armazém a 201,23 e 204,50);
  - verificado a 2026-11-07, só com contagens.
- **Casa Tipo 2:** está num terreno com declive (piso inferior a −2,70). Não foi escolhida como projeto de teste.

## 4. O que se aprendeu para a Fase 2 (terreno)

- **Torres Vedras:**
  - no DWFx e no PDF, o levantamento tem as cotas desenhadas como contornos, sem texto, por isso não se leem;
  - a fonte útil é o **DWG**, exportado para **DXF**, que guarda os pontos e as curvas de nível com a cota;
  - o DXF é texto aberto e lê-se só com Python.
- **Sobral:**
  - o levantamento tem as cotas **em texto** no DWFx da arquitetura;
  - é o melhor candidato para o primeiro terreno real.
- **Em nenhum dos dois** se encontraram ainda CRS, datum, data do levantamento nem precisão declarada. É preciso ler os
  carimbos ou perguntar ao topógrafo (especificação §3.5).

## 5. Limitações e riscos

- **Entradas com proveniência:** a planta de arquitetura (Torres Vedras) e os desenhos do engenheiro (Sobral). O JSON
  do Build Your House fica para quando for preciso.
- **Pé direito e cotas dos pisos:** a entrada do engenheiro dá a cota de cada piso, não um «pé direito»; o pé direito
  de cada piso resulta do método DiscoverCasa (`docs/modelos.md` do Sobral).
- **Vãos:**
  - em Torres Vedras, as posições continuam as da planta; do desenho de módulos compara-se só a largura, o peitoril, a
    altura e o tipo;
  - no Sobral, as medidas são as dos intervalos entre peças, e o motor DiscoverCasa ajusta-as às regras de
    enquadramento;
  - uma porta com menos de 1,90 m de altura livre fica para rever.
- **As declarações são à mão:**
  - cada valor tem de citar a sua fonte;
  - o relatório avisa quando uma declaração não encontra o campo ou contradiz o modelo.
- **O texto dos PDF não é lido** pelo leitor atual. O catálogo de um PDF diz só se é vetorial ou digitalizado.
- **O catálogo não escreve o texto dos desenhos, só contagens e palavras-chave** (o repositório é público). Os nomes
  das folhas aparecem sem o nome do ficheiro DWG, que costuma ter o nome do cliente. Mesmo assim, convém lê-lo antes
  de o pôr no Git.

## 6. Testes

`step-inside/tests/test_fontes.py` tem 20 testes (`unittest`).

**Os dois projetos de teste**, a partir dos dados do modelo guardados no Git:
- validam contra o schema e não dão `FAIL`;
- em Torres Vedras, os 19 vãos batem com o D2503;
- no Sobral, a escala está escrita, a conduta foi retirada, as paredes da arquitetura entraram e as medidas dos vãos
  ficam inferidas.

**Testes de regressão dos leitores existentes** (especificação §3.2):
- voltam a ler os desenhos e têm de dar a mesma planta de Torres Vedras e os mesmos 53 painéis do Sobral;
- só correm onde estão os desenhos, porque estes não vão para o Git; noutro PC ficam por correr (*skip*);
- `STEP_INSIDE_DESENHOS` pode apontar para a pasta das obras.

**Os restantes usam uma casa sintética** em `tests/fixtures/casa_simples/`, sem dados de clientes. Cobrem:
- escala deduzida contra escala declarada;
- valores por omissão;
- norma da empresa;
- vão fora da parede, vãos sobrepostos e peitoril acima do topo (`FAIL`);
- dimensões em conflito;
- declarações com outro valor ou sem campo;
- módulos como construídos a prevalecer;
- `PASS` com tudo confirmado;
- erros de schema;
- matriz de formatos.

Resultado a 2026-11-07, neste PC (com os desenhos): **20 OK**.
