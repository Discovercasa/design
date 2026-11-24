# Fase 8 · Prova de conceito VR (em preparação)

Tarefas do hub 86 a 89. Especificação §13 Fase 8 (perfil `VR_BAKED`: sem Lumen, luz pré-calculada). Pedido do
utilizador (2026-11-24): «prepara tudo de forma a quando tiver os óculos ser só ligar os óculos ao PC e pedir-te para
iniciar o tour VR». Os óculos ainda não estão escolhidos (tarefa 86).

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
2. `unreal-vr\construir_nivel_vr.cmd`: importar → ajustes_materiais → iluminacao (`"mobilidade": "STATIC"`, sem nuvens,
   sem Lumen) → material_mestre → pos_processo → **vr_preparar** (UVs e resolução de lightmap por peça, volume de
   importância do Lightmass e de navegação à volta da casa, uma captura de reflexos por divisão, o PlayerStart no soalho
   da sala, definições do Lightmass) → **luz cozida e malha de navegação**
   (`-run=ResavePackages -BuildLighting -BuildNavigationData -Quality=Production`).

## Iniciar o tour VR (quando o utilizador pedir)

O utilizador: liga os óculos ao PC de casa com o software deles a correr (Meta Quest: app *Meta Quest Link* + cabo
Link ou Air Link, e «Link» ativo no óculos; Valve/HTC/Pico: *SteamVR*) e põe os óculos.

O Claude (sessão do escritório, por SSH):
1. `powershell -ExecutionPolicy Bypass -File D:\BOB-posto\step-inside\vr\verificar_vr.ps1` → JSON com `runtime`,
   `servico`, `oculos`, `projeto`, `pronto`. Se `runtime` vazio: falta instalar o software dos óculos (é o utilizador
   que o faz: pede a conta dele). Se `servico` falso: abrir a app dos óculos. Se `projeto` falso: correr
   `construir_nivel_vr.cmd`.
2. Tarefa agendada de uso único na sessão do Windows aberta:
   `schtasks /Create /TN BOB_StepInside_VR /TR D:\BOB-posto\step-inside\unreal-vr\iniciar_vr.cmd /SC ONCE /ST 23:59 /RU pc /IT /F`
   e `schtasks /Run /TN BOB_StepInside_VR`; apagar no fim (`schtasks /Delete … /F`).
3. Confirmar no registo do jogo (`C:\Users\PC\AppData\Local\UnrealEngine\5.8\Saved\Logs\StepInsideVR.log`) que o OpenXR
   arrancou (linhas `LogOpenXRHMD`); no fim, os FPS do CSV
   (`…\Saved\Profiling\CSV\`) com `ferramentas/unreal/ler_csv.py`.
4. Para fechar: o menu dos óculos (sair) ou `Stop-Process -Name UnrealEditor`.

Controlos: os do template VR do Unreal (`BP_XRPawn`): apontar com o *thumbstick* e largar para teletransportar,
rotação por passos, botão de menu.

## Sem óculos

- `fps_vr.cmd`: o custo da VR sem óculos — estéreo emulado (`-emulatestereo`), 180 % de 1920 × 1080 (≈ um par de olhos
  de um Quest 2), CSV de 3 000 frames, a vista de `camara_jogo.py`.
- `render_gui.cmd` com `render_mrq.json` no `unreal-vr\`: imagens do nível VR (aspeto da luz cozida).

## Resultados (2026-11-24)

- **Pronto e testado:** o projeto VR, o pawn VR do template, a navegação, o PlayerStart no soalho, os lançadores
  (`iniciar_vr.cmd`, `fps_vr.cmd`, `render_gui.cmd`) e `verificar_vr.ps1` (hoje: `projeto` true, `runtime` vazio —
  ainda não há software de óculos no PC de casa).
- **Cozedura** (Lightmass, 12 núcleos): 3,5–4,5 min para a casa; dados de luz ≈ 20 MB.
- **FPS em estéreo emulado** (sala, 180 % de 1920 × 1080 ≈ um par de olhos de Quest 2, forward + MSAA 4×, luz cozida):
  **59 FPS** (GPU 16,9 ms). Os óculos pedem 72–90 Hz: falta afinar (resolução ≈ 140 %, MSAA 2×) — no Quest Link
  a reprojeção (ASW) segura o que faltar.
- **Aspeto: ainda não aprovado.** Problemas encontrados e o que já se corrigiu:
  - 1.ª cozedura: o lightmap ficou no canal 0 (UVs das texturas, que se repetem) → manchas em blocos e riscas. Sem
    janela, a reconstrução das malhas é assíncrona: o índice tem de ser posto depois de
    `finish_all_asset_compilation()` e cada malha gravada (corrigido; as manchas em blocos desapareceram);
  - imagens com o material de xadrez: o render começava antes de os shaders compilarem → `render_mrq.py` aquece
    primeiro (corrigido);
  - névoa azul dentro de casa no forward → sem nevoeiro na VR (corrigido);
  - **por corrigir:** sala e cozinha sobre-expostas (a exposição +3,3 do Lumen é demais para a luz cozida); zonas
    negras em paredes e tetos (ainda 123 avisos de UVs de lightmap que se repetem ou sobrepõem: a geração do Unreal
    não serve para todas as peças); céu negro no exterior.
- **A seguir (aspeto VR):** gerar os UVs de lightmap no Blender (segundo canal no GLB, determinístico) em vez de no
  Unreal; exposição própria da VR por variantes; o céu (atmosfera com luz estacionária ou um céu HDRI); depois afinar
  os FPS para 72–90.
- Cada imagem do nível VR demora ≈ 5 min no Movie Render Queue (um PIE por trabalho); o primeiro arranque do projeto
  compila os shaders do forward.
