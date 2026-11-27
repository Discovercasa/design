# Fase 8 · Prova de conceito VR (pronta a testar com óculos)

Tarefas do hub 86 a 89. Especificação §13 Fase 8 (perfil `VR_BAKED`: sem Lumen, luz pré-calculada). Pedido do
utilizador (2026-11-24): «prepara tudo de forma a quando tiver os óculos ser só ligar os óculos ao PC e pedir-te para
iniciar o tour VR». Os óculos ainda não estão escolhidos (tarefa 86).

## Objetivo comercial e projeto de teste (utilizador, 2026-11-26)

- **Torres Vedras é o projeto TESTE**: serve para perceber até onde chega o realismo da VR antes de avançar para um
  projeto real. O mobiliário deve ser realista; a envolvente (vista aérea das páginas dos clientes e vistas das janelas)
  deve aproximar-se do exterior real, como nos exemplos do Twinmotion que o utilizador viu.
- **A página do cliente tem três níveis pagos**, conforme o que o cliente decide e paga: (1) 3D realista + tour;
  (2) 3D realista + tour + AR; (3) 3D realista + tour + AR + VR. O nível 1 é o padrão das Páginas (um 3D com a nossa
  qualidade e a visita 360° dentro dele); a AR vem da Fase 7; a VR é esta fase.
- **Pergunta em aberto (2026-11-26): como se entrega o nível 3 (VR)?** A VR em casa do cliente precisa de um PC com
  placa gráfica mais os óculos. Opções (insights 2026-11-26): sessão na DiscoverCasa com o nosso PC; versão autónoma
  para Quest (muito menos realista); streaming na cloud (custo à hora). Por decidir. Também por definir: preços de cada
  nível e como a página liga AR e VR ao 3D (hoje a AR está na página de teste do hub, a VR só no PC de casa).

## Porquê um projeto à parte

A VR precisa de 72–90 FPS **por olho** a uma resolução acima de 1080p. Com o Lumen por hardware a RTX 2060 dá 31–40 FPS
a 1080p (Fase 4), por isso a VR usa o perfil do template VR do próprio Unreal: renderizador *forward*, *instanced stereo*
(os dois olhos numa passagem), MSAA 4×, sem sombras virtuais, **luz cozida pelo Lightmass**. Estas definições são do
projeto inteiro e não convivem com o Lumen/Path Tracer das imagens: o projeto `StepInsideVR` é à parte, com a mesma casa
construída pelos mesmos scripts.

| | Imagens / tempo real (Fase 4) | VR (Fase 8) |
|---|---|---|
| Projeto | `D:\BOB-posto\unreal\StepInside` | `D:\BOB-posto\unreal\StepInsideVR` |
| Scripts e definições | `D:\BOB-posto\step-inside\unreal\` | `D:\BOB-posto\step-inside\unreal-vr\` |
| Nível | `/Game/Visita/TV_Visita` | `/Game/Visita/TV_VR` |
| Luz | Lumen (hardware) / Path Tracer | Lightmass (cozida) + capturas de reflexos |
| Repositório | `ferramentas/unreal/projeto/`, `ue/` | `ferramentas/unreal/projeto_vr/`, `vr/`, `ue/vr_preparar.py` |

## Montagem (uma vez; feita a 2026-11-24)

1. `criar_projeto_vr.ps1` (no PC de casa): o projeto (`projeto_vr/`), as definições de entrada do template VR e os seus
   pacotes de conteúdo, montados onde os assets os esperam — `/Game/XRFramework` (o pawn VR `BP_XRPawn` com
   teletransporte e rotação, o modo de jogo `BP_XRGameMode`, o menu), `/Game/XRMannequins` (as mãos),
   `/Game/VRSpectator` — copiados de `D:\Epic Games\UE_5.8\Templates\TemplateResources\Standard\`.
2. O GLB da VR sai do Blender com um **segundo canal de UVs só para o lightmap** (`blender_para_unreal.py --lightmap`:
   cada peça desdobrada sem sobreposições, determinístico) — os UVs gerados pelo Unreal davam manchas em peças finas.
3. `unreal-vr\construir_nivel_vr.cmd`: importar → ajustes_materiais → iluminacao (lâmpadas `"mobilidade": "STATIC"`,
   sol e luz do céu `"mobilidade_sol": "STATIONARY"`, **`"ceu": "gradiente"`**, sem nuvens, sem nevoeiro, sem Lumen) →
   material_mestre → **vr_preparar** (lightmap no canal 1 do GLB e resolução por peça, volume de importância do
   Lightmass e de navegação à volta da casa, uma captura de reflexos por divisão, o PlayerStart no soalho da sala,
   definições do Lightmass) → pos_processo (depois do vr_preparar: o volume do interior segue o do Lightmass) → malha de
   navegação.
4. **`unreal-vr\cozer_gui.cmd`** (no editor, com a GPU; tarefa agendada na sessão do Windows): espera que os shaders
   compilem, fotografa o céu para a luz do céu, coze a luz (`build_light_maps`, qualidade em `cozer.json`) com as
   capturas de reflexos e grava. Sem janela (`-NullRHI`) a luz do céu e os reflexos saíam negros.

**O céu da VR.** No renderizador *forward* o `SkyAtmosphere` desenhava um céu negro, e a luz do céu fotografava só a
relva (interiores verdes); o `BP_Sky_Sphere` do motor já não carrega no 5.8. Por isso `iluminacao.py` faz uma cúpula
própria (`M_SI_Ceu`, sem iluminação): azul do horizonte ao zénite em luminância real (cd/m², coerente com o sol em lux),
um halo e um disco pequeno na direção do sol, terra cinzenta abaixo do horizonte; móvel e sem sombras, para o Lightmass a
ignorar (estática, bloqueava todos os raios do céu) enquanto a luz do céu e as capturas de reflexos a fotografam.
Valores em `"ceu_parametros"`. A luz do céu tem a metade de baixo negra: o que vem do chão é a relva verdadeira,
refletida pelo Lightmass.

**A luz cozida, peça a peça** (`vr_preparar.json`, `material_mestre.json`), com o que cada escolha corrigiu:
- **Móveis e decoração** (`"volumetrico": ["INT_", "PH_"]`): iluminados pelo *lightmap* volumétrico (células de 50 cm,
  `"celula_volumetrica_cm"`) em vez de um lightmap por peça — os UVs de lightmap por face das malhas densas davam
  facetas triangulares nos sofás, cadeiras e pufes.
- **Reflexos de cor** (`"lightmass_dessaturar": 0.9` no material-mestre, nó `LightmassReplace`): o Lightmass faz a luz
  ressaltar numa cor 90 % dessaturada; o que se vê não muda. O soalho laranja e a relva verde, a ressaltar entre o chão
  e o teto branco, deixavam o teto da sala verde-lima, depois mostarda (0,6) e azeitona (diagnóstico: sem a luz
  indireta cozida, `ShowFlag.GlobalIllumination 0`, o teto ficava negro e as paredes neutras).
- **Força dos ressaltos** (`"ressalto"`: relva e terreno 0,5, soalho 0,85) e 3 ressaltos da luz do céu
  (`"ressaltos_ceu"`).
- **Manchas nas paredes** (ruído da luz indireta): escala da luz estática 1,0 (a 0,5 o ruído e o tempo sobem muito),
  qualidade indireta 4, suavidade 0,9, lightmaps sem compressão (`"comprimir": false`). A cozedura de produção com 0,5 e
  qualidade 2 demorou 99 min e ainda manchava; com os valores novos a pré-visualização demora 2,5 min e a produção
  2 h 17 min (sem manchas visíveis; mais escura que a pré-visualização, que sobrestima a luz indireta — a exposição
  escolhe-se sobre a de produção).
- **Exposição** (`pos_processo.json`): exposição local (`local_exposure_highlight_contrast_scale` 0,6,
  `…shadow…` 0,85: a janela deixa de queimar a sala) e, só dentro de casa, o volume `SI_PosProcesso_Interior`
  (`"interior"`: +2,2 EV, branco a 7500 K, exposição local mais forte — realces 0,5, sombras 0,45 —; transição de 1,5 m
  nas paredes): o jardim fica com a sua exposição — como o olho, que se adapta ao entrar. A exposição automática
  (histograma) baixa na sala, que vê as janelas grandes: subir só o +EV queimava os quartos; levantar as sombras com a
  exposição local clareia a sala e a cozinha (teto incluído) e deixa os quartos como estavam. Limitar o
  `auto_exposure_max_brightness` (9 e 8,5) não mudou nada. Escolhida por variantes de câmara (`variantes.json`, duas
  rondas de 4), sem voltar a cozer.
- **Diagnóstico**: `capturas.json` aceita `"camaras"` (só estas) e `"modos"` (uma volta por modo, com comandos de
  consola, p. ex. `ShowFlag.GlobalIllumination 0`, `ShowFlag.SkyLighting 0`, `ShowFlag.ReflectionEnvironment 0`).
- **Vidro** (`vidros.py` + `vidros.json`, 2026-11-26): o vidro do duche era uma folha branca opaca, fosse qual fosse a
  cor, a opacidade ou a rugosidade. Causa: o sol é **estacionário** e ilumina as superfícies translúcidas ao vivo mas
  **sem a sombra cozida** — o vidro dentro do WC fechado recebia o sol inteiro (com `ShowFlag.DirectionalLights 0`
  ficava transparente); o mesmo nas janelas vistas de dentro (vidro dos dois lados, iluminado por trás). Correção:
  `"sem_sol": true` põe cada malha com material translúcido só no canal de luz 1 (o sol fica no canal 0): guarda a luz
  do céu, a luz cozida (lightmap volumétrico) e as capturas de reflexos; não é preciso voltar a cozer. E um vidro
  próprio, `M_SI_Vidro` (translúcido, iluminado por píxel, dos dois lados, sem refração — barato em VR; opacidade
  0,08 de frente e 0,5 de raspão, pelo Fresnel), no lugar do `INT_CFE0E8_05_A22` do glTF.
- **Espelhos** (`espelhos.py` + `espelhos.json`, 2026-11-26): com luz cozida o *forward* só reflete as capturas de
  reflexos (uma «fotografia» esférica pequena por divisão) — o espelho era uma folha cinzenta. Agora cada espelho tem um
  reflexo planar (`PlanarReflection` `SI_VR_Espelho_*`, encontrado pela geometria da secção com o material do espelho,
  do tamanho dele, a desvanecer a 0,5–2 cm do plano para não tocar a parede) e um material próprio `M_SI_Espelho`
  (metal, «Planar Reflections» ligado nas definições Forward Shading — sem isto o *forward* ignora o reflexo planar).
  Precisa de `r.AllowGlobalClipPlane=True` (`projeto_vr/Config/DefaultEngine.ini`; recompila os shaders). O custo
  (uma segunda renderização da cena, a 50 % de resolução, só quando o espelho está à vista) ainda está por medir com o
  PC livre: a primeira medição (77 FPS no WC a 140 %/4×) foi feita com o PC a ser usado.
- **Nanite desligado** (`"nanite": false` em `vr_preparar.json`, 2026-11-26): as 377 malhas vinham do glTF com Nanite,
  que o *forward* da VR não suporta — desenhava (e o Lightmass cozia) a **malha de recurso simplificada** de cada uma
  (erro relativo 1,0). Nas placas finas a simplificação mexia os vértices: o OSB de trás atravessava o Pladur (as
  cunhas escuras nas juntas parede/teto), abriam-se frestas nos cantos e os UVs de lightmap deformavam-se (manchas,
  faixas). Diagnóstico: raios da câmara contra os triângulos (o primeiro acerto era o `OSB_15_mm`, à frente do Pladur,
  com 1,5–3° de desvio), quando no Blender e no GLB as placas são paralelas. As camadas escondidas (OSB, lã mineral,
  membrana, perfis e réguas do teto) ficam com o lightmap mais pequeno (4 texels, `"minimo"`): quase nada a cozer e
  continuam superfícies normais para o Lightmass. Lightmaps a 56 texels/m. Confirmado na cozedura de 2026-11-26 (1 h 42
  min): as cunhas, frestas e faixas desapareceram.
- **Base dos móveis branca** (cozedura de 2026-11-26): a parte de baixo de todos os móveis iluminados pelo lightmap
  volumétrico brilhava a branco até ≈ 30 cm. Não era o sol, os candeeiros, a luz do céu, os reflexos, a exposição local,
  o ressalto do chão, o Nanite, os espelhos nem o `r.AllowGlobalClipPlane` (cada um desligado à vez, em cozeduras de
  pré-visualização de 2 min). Era o **volume do Lightmass**: começava na face de baixo da laje (z −20) e a primeira
  camada de amostras do lightmap volumétrico, que sai sempre clara, ficava aí; tudo até à camada seguinte (+30 cm,
  células de 50 cm) misturava-se com ela. Prova: com o volume a começar a +5 cm o branco subiu até 55 cm. Correção:
  `"importancia_z_cm": [-150, null]` (o volume começa 1,5 m abaixo do chão). Também: o terreno tinha um buraco debaixo
  da casa e a laje flutuava 2 m acima da relva, aberta ao céu dos lados — um bloco de solo enche-o (`"solo_sob"`).
- **Móveis paramétricos com lightmap** (`"volumetrico_malhas": ["PH_"]`, 2026-11-26): pelo lightmap volumétrico, as peças
  nossas (malhas `PAR_OBJ_*`: cozinha, roupeiros, camas, mesas, sanitários) só tapavam a luz na cozedura e não a
  devolviam — a parede e o teto à volta dos armários brancos da cozinha ficavam escuros (o canto que o utilizador
  marcou). Com lightmap (UV 1 do Blender) ficam claros; as peças digitalizadas (`PH_*`, malhas densas) continuam
  volumétricas, porque com lightmap ficam manchadas.
- **Céu fotográfico** (`ceu_hdri.py` + `ceu_hdri.json`, `blender_ceu.py`, 2026-11-26, utilizador: «então descarrega»):
  `kloofendal_38d_partly_cloudy_puresky` (Poly Haven, CC0, 8k) na cúpula SI_Ceu, rodado para o sol da foto ficar no
  azimute do sol do nível; o sol da foto é cortado ao brilho da nuvem mais clara (o nível tem o seu sol cozido) e a
  escala dá a mesma luminância média do céu desenhado (4566 cd/m²). Sem nova cozedura (a cúpula é móvel).
- `vr_preparar.py` e `espelhos.py` carregam o módulo `StaticMeshEditor` (numa *commandlet* o subsistema vinha vazio e a
  antiga `EditorStaticMeshLibrary` devolvia valores por omissão em silêncio: os registos «0 canais de UV» eram falsos);
  as malhas do motor (`/Engine/…`, o chão de relva é o `Plane`) já não são alteradas nem gravadas.

## Iniciar o tour VR (quando o utilizador pedir)

O utilizador: liga os óculos ao PC de casa com o software deles a correr (Meta Quest: app *Meta Quest Link* + cabo
Link ou Air Link, e «Link» ativo no óculos; Valve/HTC/Pico: *SteamVR*) e põe os óculos.

O Claude (sessão do escritório, por SSH):
1. `powershell -ExecutionPolicy Bypass -File D:\BOB-posto\step-inside\vr\verificar_vr.ps1` → JSON com `runtime`,
   `servico`, `oculos`, `projeto`, `pronto`. Se `runtime` vazio: falta instalar o software dos óculos (é o utilizador
   que o faz: pede a conta dele). Se `servico` falso: abrir a app dos óculos. Se `projeto` falso: correr
   `construir_nivel_vr.cmd`.
2. Tarefa agendada de uso único na sessão do Windows aberta:
   `schtasks /Create /TN BOB_StepInside_VR /TR D:\BOB-posto\step-inside\unreal-vr\iniciar_vr.cmd /SC ONCE /SD 01/01/2020 /ST 00:00 /RU pc /IT /F`
   e `schtasks /Run /TN BOB_StepInside_VR`; apagar no fim (`schtasks /Delete … /F`). A data no passado faz com que a
   tarefa nunca arranque sozinha («Next Run Time: N/A»): a 2026-11-26 uma tarefa com `/ST 23:59` ficou por apagar (a
   sessão terminou antes) e voltou a abrir o Unreal à meia-noite. `iniciar_vr.cmd [densidade] [MSAA]`:
   por omissão densidade 0,78 e MSAA 4× (dá para 90 Hz na RTX 2060, ver «Resultados»); com óculos a 72 Hz pode subir-se
   a 0,9 (`/TR "…\iniciar_vr.cmd 0.9 4"`) — mais nítido. Antes do tour, `camara_jogo.json` com `"camara": "nenhuma"`
   (está assim desde 2026-11-25).
3. Confirmar no registo do jogo (`C:\Users\PC\AppData\Local\UnrealEngine\5.8\Saved\Logs\StepInsideVR.log`) que o OpenXR
   arrancou (linhas `LogOpenXRHMD`); no fim, os FPS do CSV
   (`…\Saved\Profiling\CSV\`) com `ferramentas/unreal/ler_csv.py`.
4. Para fechar: o menu dos óculos (sair) ou `Stop-Process -Name UnrealEditor`.

Controlos: os do template VR do Unreal (`BP_XRPawn`): apontar com o *thumbstick* e largar para teletransportar,
rotação por passos, botão de menu.

## Sem óculos

- `fps_vr.cmd [percentagem] [MSAA]`: o custo da VR sem óculos — estéreo emulado (`-emulatestereo`), por omissão 180 %
  de 1920 × 1080 (≈ um par de olhos de um Quest 2) e MSAA 4×, CSV de 3 000 frames, a vista de `camara_jogo.py`
  (antes de um tour a sério, `camara_jogo.json` com `"camara": "nenhuma"`: a vista volta a ser a do pawn VR).
- `capturas_gui.cmd`: capturas rápidas no editor de cada `SI_CAM_*` (aspeto da luz cozida).
- `render_gui.cmd` com `render_mrq.json` no `unreal-vr\`: imagens do nível VR (aspeto da luz cozida).

## Resultados (2026-11-25)

- **Pronto e testado:** o projeto VR, o pawn VR do template, a navegação, o PlayerStart no soalho, os lançadores
  (`iniciar_vr.cmd`, `fps_vr.cmd`, `cozer_gui.cmd`, `capturas_gui.cmd`) e `verificar_vr.ps1` (`projeto` true,
  `runtime` vazio — ainda não há software de óculos no PC de casa).
- **Aspeto:** luz cozida em produção (2 h 17 min na RTX 2060 + 12 núcleos), exposição escolhida por variantes; imagens
  de cada divisão em `_trabalho/step-inside/torres-vedras/unreal_vr/cap17/` (local). O que se corrigiu, por ordem: UVs de
  lightmap do Blender (manchas em blocos), céu próprio (céu negro e interiores verdes), móveis pelo lightmap volumétrico
  (facetas), `LightmassReplace` (teto verde-lima), escala 1,0 / qualidade 4 / sem compressão (manchas), volume de
  exposição do interior com exposição local (salas escuras, quartos queimados).
- **FPS em estéreo emulado** (sala, forward, luz cozida; 100 % = 1920 × 1080; 180 % ≈ um par de olhos de Quest 2):

  | Resolução | MSAA | FPS (mediana) | GPU (mediana) |
  |---|---|---|---|
  | 180 % | 4× | 72 | 13,2 ms |
  | 160 % | 4× | 86 | 11,0 ms |
  | 140 % | 4× | 102 | 9,1 ms |
  | 140 % | 2× | 129 | 7,1 ms |
  | 120 % | 2× | 157 | 5,8 ms |

  A 90 Hz cada imagem tem 11,1 ms, e os óculos (compositor, codificação do Link) levam ≈ 1–2 ms: por omissão o tour usa
  densidade 0,78 (= 140 %) e MSAA 4×; com óculos a 72–80 Hz, 0,9 (= 160 %) é mais nítido. Ontem, antes dos móveis pelo lightmap volumétrico, 180 %/4× dava 59 FPS.
- **Resultados (2026-11-27, cozedura final de 2026-11-26, 1 h 47 min):** paredes sem cunhas nem frestas; a base dos
  móveis escura e com sombra de contacto; o canto por cima dos armários da cozinha claro (só a sombra suave junto ao
  armário). FPS em estéreo emulado a 140 %/MSAA 4×: sala 107,8 (ontem 102); WC com espelho 111,8, sem espelho 165 — o
  espelho custa ≈ 3 ms e cabe nos 90 Hz. Defeito novo: os reflexos têm um tom verde (cadeiras de couro, caixilhos,
  puxadores) — vem das capturas de reflexos feitas nesta cozedura (sem elas as cadeiras ficam neutras); por resolver.
- **Falta (com os óculos):** latência, conforto e os FPS reais no CSV do tour (tarefa 88); escolher os óculos (tarefa 86).
- **Melhorias possíveis** (não bloqueiam o teste): relva e terreno do exterior lisos e facetados, o alpendre negro visto de
  fora, o WC demasiado quente, janelas queimadas vistas de dentro (como numa foto); vegetação real à volta (árvores
  digitalizadas com versões leves — `ferramentas/pagina/vegetacao.py`; a primeira técnica, folhas rareadas e
  aumentadas, dá folhas grandes demais: falta a dos cartões com cachos de folhas). Resolvidos a 2026-11-26: o vidro do
  duche branco («Vidro»), os espelhos cinzentos («Espelhos»), as cunhas e frestas («Nanite desligado»), a base branca
  dos móveis e o canto escuro por cima dos armários (secções acima), o céu desenhado («Céu fotográfico»).
- Cada imagem do nível VR no Movie Render Queue demora ≈ 5 min (um PIE por trabalho); `capturas_gui.cmd` tira as 6 vistas
  em ≈ 2 min; o primeiro arranque do projeto compila os shaders do forward.
