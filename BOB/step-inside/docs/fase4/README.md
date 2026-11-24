# Fase 4 · Unreal Viewer e aprovação visual (em curso)

Tarefas do hub 66 a 71 e 154. Especificação §13 Fase 4. Recomeçada a 2026-11-24 («sim avança»), depois de adiada a
2026-11-18 («Mais tarde»). Tudo é comandado a partir da sessão do escritório; o PC de casa só executa
(`conhecimento/posto-render.md`).

**Critério de saída:** a casa de teste abre no Unreal com materiais reais, anda-se lá dentro em primeira pessoa, e a
DiscoverCasa aprova as imagens, os FPS e as métricas.

## Versões fixadas (tarefa 66)

| Peça | Versão | Onde |
|---|---|---|
| Unreal Engine | **5.8.4** (CL 58902052, `++UE5+Release-5.8`), Epic Games Launcher | PC de casa, `D:\Epic Games\UE_5.8` |
| Plugins do projeto | PythonScriptPlugin, EditorScriptingUtilities, Interchange + InterchangeEditor (glTF), MovieRenderPipeline | `StepInside.uproject` |
| Mais tarde | PixelStreaming2 (Fase 5), OpenXR (Fase 8) | já vêm com o motor |
| Python do Unreal | 3.11.8 (embutido) | — |
| Blender (exportação) | 5.2.2 LTS | PC do escritório |
| GPU | RTX 2060 6 GB, driver 610.88, DX12 SM6 | PC de casa |

O projeto é só de conteúdo (sem C++): não precisa do Visual Studio.

## Projeto e ferramentas

`step-inside/ferramentas/unreal/`:

| Ficheiro | Corre em | Faz |
|---|---|---|
| `blender_para_unreal.py` | Blender (escritório) | o modelo de visita (com interiores) num GLB com texturas embebidas + números de controlo |
| `blender_vistas.py` | Blender (escritório) | as vistas interiores de `interiores.json` em coordenadas do mundo (as mesmas dos renders do Blender) |
| `projeto/` | — | `StepInside.uproject` e `Config/DefaultEngine.ini` (Lumen por software, sombras virtuais, DX12, TSR, caches no D:) |
| `ue_cmd.cmd`, `ue_gui.cmd` | PC de casa | lançam o Unreal (sem janela / com janela) com as caches no D: |
| `ue/importar.py` | Unreal, sem janela | nível novo, importação do GLB como cena (Interchange), verificação dos eixos, casa na origem com o pavimento a Z = 0, sol + céu + nevoeiro + pós-processo, PlayerStart e uma câmara por vista |
| `ue/capturas.py` | Unreal, editor com GPU | aquece (compila tudo o que as vistas pedem), mede o tempo de frame em cada vista e tira uma imagem por câmara (1.º teste; substituído por `render_mrq.py`) |
| `construir_nivel.cmd` | PC de casa | refaz o nível de raiz, por esta ordem: `importar` → `ajustes_materiais` → `iluminacao` → `material_mestre` → `pos_processo` |
| `ue/ajustes_materiais.py` | Unreal, sem janela | correções por material glTF (texturas, escalares, cores): soalho acetinado, cúpulas sem metal, espelho, relva |
| `ue/iluminacao.py` | Unreal, sem janela | camadas escondidas pintadas, sol/céu/nuvens/nevoeiro, luzes nos candeeiros e extra, pós-processo, chão relvado |
| `ue/material_mestre.py` | Unreal, sem janela | `M_SI_PBR` e uma instância por material opaco da casa, trocadas nas malhas |
| `ue/pos_processo.py` | Unreal, sem janela | o aspeto escolhido no pós-processo do nível e por câmara |
| `ue/variantes.py` | Unreal, sem janela | cópias de uma câmara com pós-processo próprio, para escolher o aspeto por imagens |
| `ue/render_mrq.py` + `render_gui.cmd` | Unreal, editor com GPU | imagens pelo Movie Render Queue: Lumen (aquecimento + amostras temporais) ou Path Tracer (`"modo": "path"`), passes de diagnóstico |
| `ue/camara_jogo.py` + `fps_jogo.cmd` / `fps_jogo_tsr.cmd` + `ler_csv.py` | Unreal / PC de casa / escritório | FPS em modo jogo por vista (CSV do Unreal), nativo ou com TSR 67 % |
| `ue/diagnostico_materiais.py`, `blender_rugosidade.py` | Unreal / Blender | lista os parâmetros dos materiais importados; textura de rugosidade remapeada |

No PC de casa: projeto em `D:\BOB-posto\unreal\StepInside\`, caches em `D:\BOB-posto\unreal\DDC\`, ficheiros de cada
casa em `D:\BOB-posto\step-inside\<obra>\` (nunca no Git: têm a casa do cliente). O editor com janela corre na sessão
do Windows aberta, por uma tarefa agendada de uso único criada por SSH e apagada no fim.

**Fluxo:**
1. Escritório: `blender -b visita_interiores.blend --python blender_para_unreal.py -- <glb> <resumo>` e
   `blender_vistas.py` → `scp` para o PC de casa.
2. Casa: `ue_cmd.cmd -run=pythonscript -script=…\importar.py -unattended -nop4 -nosplash -NullRHI`.
3. Casa (sessão do Windows): `ue_gui.cmd -ExecutePythonScript=…\capturas.py`.

**Armadilhas encontradas:**
- num `.cmd`, `%1…%9` partem os argumentos no «=» (`-run=pythonscript` ficava `-run pythonscript` e o Unreal arrancava
  sem correr nada): os lançadores passam `%*`;
- no 5.8 o `World` não mostra `persistent_level` ao Python: usa-se `LevelEditorSubsystem.get_current_level()`;
- o nível de arranque do projeto não se pode apagar com o editor aberto: cria-se um mapa em branco e grava-se por cima
  com `EditorLoadingAndSavingUtils.save_map`;
- as imagens só se tiram depois de `AutomationUtilsBlueprintLibrary.finish_all_asset_compilation()` não ter nada para
  esperar numa passagem por todas as câmaras (com a compilação assíncrona, os materiais aparecem cinzentos até lá).

## Primeiro teste: Torres Vedras mobilada (2026-11-24)

**Entrada:** o modelo de visita com os interiores de teste (Fase 3): 389 objetos, 535 072 triângulos (as plantas são
as peças mais pesadas), terreno, 5 vistas interiores. GLB de 135 MB.

**Importação** (Interchange, sem janela, 78 s): 377 malhas, 68 instâncias de material (os materiais glTF do
Interchange), 106 texturas, 404 atores no nível. Eixos: Blender (x, y, z) m → Unreal (x, −y, z) cm, confirmado pela
caixa do GLB (erro 0 cm). Casa deslocada para a origem, pavimento acabado a Z = 0.

**GPU (RTX 2060 6 GB, modo jogo, 1920 × 1080, DX12, Lumen por software, sombras virtuais, TSR)** — CSV do Unreal
(`fps_jogo.cmd` + `ler_csv.py`), últimos 1 500 de 3 000 frames:

| Vista | Frame | GPU | Render thread | Game thread | FPS (mediana) |
|---|---|---|---|---|---|
| Sala (a vista mais pesada: mobília, plantas, janelas) | 11,5 ms | 10,9 ms | 11,5 ms | 1,3 ms | **87** |
| Exterior (casa e terreno) | 11,0 ms | 10,3 ms | 11,0 ms | 1,3 ms | **91** |

~~A RTX 2060 chega para o visualizador a 1080p~~ (superado a 2026-11-24, ver «Tarefa 69»: estes números são do Lumen
por software, porque o ray tracing não estava ligado; com o Lumen por hardware a sala dá 31–40 FPS). A VR (Fase 8) é outro orçamento
(90 FPS por olho, perfil VR_BAKED sem Lumen). Estes números são com a luz e os materiais provisórios: voltam a
medir-se depois da tarefa 69. No editor o viewport fica nos 120 FPS (limite do editor; viewport mais pequeno).

**Imagens** (`capturas.py`, as mesmas câmaras dos renders do Blender; comparação enviada ao utilizador):
- certo: geometria, mobília, posições e lentes das câmaras;
- **luz** (tarefa 69): só o céu ilumina o interior e a exposição automática sobe tudo → tom azul e frio, teto escuro,
  manchas nas paredes (ruído do Lumen). Falta: luzes interiores, equilíbrio de brancos, exposição fixa por vista;
- **materiais** (tarefa 69): os materiais glTF automáticos não servem (o couro sai com ar metálico, o soalho de
  carvalho escuro e com reflexos brancos). Fazer um material mestre com instâncias por `MAT_*` do catálogo, com as
  nossas texturas (o FBX da Fase 3 traz os IDs);
- faixas bege em alguns cantos de paredes: camadas no mesmo plano (a confirmar);
- exterior: à volta do terreno vê-se o chão da atmosfera (azul, parece mar): falta um chão largo e a relva.

**Mais armadilhas:**
- o `take_high_res_screenshot` do Python só funciona num viewport de jogo; no editor usa-se o `HighResShot` (consola)
  com o viewport a pilotar a câmara (`pilot_level_actor`), e a imagem vai para `Saved/Screenshots/WindowsEditor/`;
- `-ExecutePythonScript` fecha o editor logo que o script acaba: para scripts que esperam por frames usa-se
  `-ExecCmds="py <script>"`;
- um editor que não está em primeiro plano fica a 8 FPS («Use Less CPU when in Background»): desligado no projeto
  (`DefaultEditorSettings.ini`) e pelo próprio script;
- em modo jogo o registo e o CSV vão para `%LOCALAPPDATA%\UnrealEngine\5.8\Saved\` (não para o projeto) e o
  `-csvExecCmds="quit"` não fecha o jogo: quem lança espera pelo CSV e fecha o processo.

## Tarefa 69 — materiais e luz (2026-11-24, «as imagens … não estavam nada boas em termos de aspeto e realismo»)

**Diagnóstico** (não adivinhar: variantes e passes do Movie Render Queue):
- os materiais glTF estavam fiéis ao Blender (texturas, fatores, normais OpenGL já invertidas pelo Interchange): o passe
  *Unlit* mostra o carvalho, o couro castanho e a mesa certos;
- o aspeto lavado (soalho cinzento, couro prateado, teto azul) vinha dos **reflexos do Lumen**: o passe
  *ReflectionsOnly* mostra o céu e as paredes a «vazar» para todas as superfícies;
- a causa de fundo: **o ray tracing nunca esteve ligado**. Com os shaders só em SM5 o RHI diz «Ray tracing is disabled.
  Reason: not supported by current RHI» e o Lumen cai para software (campos de distância), que vaza nas paredes finas
  de Pladur. É preciso `+D3D12TargetedShaderFormats=PCD3D_SM6` (e `r.RayTracing`, `r.PathTracing`,
  `r.Lumen.HardwareRayTracing`). Os FPS de cima (87–91) são com o Lumen por software: voltam a medir-se.

**Feito no nível** (`ue/iluminacao.py`, `ue/material_mestre.py`, `ue/ajustes_materiais.py`):
- tiradas as 120 peças de camadas que nunca se veem (lã mineral, OSB, membranas, ripado por trás do forro, caleira
  oculta): eram as faixas bege nos cantos;
- sol da tarde em lux reais, atmosfera com nuvens volumétricas, luz do céu captada em tempo real, os 6 candeeiros com
  luz (3000 K, 1100 lm), pós-processo (equilíbrio de brancos, exposição limitada com exposição local, Lumen alto);
- chão relvado de 3 km à volta do terreno (antes via-se o «planeta» azul da atmosfera);
- material mestre `M_SI_PBR` (cor × tom, rugosidade com mínimo e máximo, metálico, especular 4 %, normais) e uma
  instância por material da casa (58), trocadas nas malhas (314); o vidro, as folhas e a relva ficam com o glTF;
- soalho acetinado (rugosidade 0,42–0,62 em vez de 0,22–0,39, `blender_rugosidade.py`) e cúpulas dos candeeiros sem
  metal;
- imagens pelo Movie Render Queue (`ue/render_mrq.py`: aquecimento, amostras temporais; ou Path Tracer com `"modo":
  "path"`), variantes de câmara para escolher a luz (`ue/variantes.py`).

**Com o ray tracing ligado** (SM6; `construir_nivel.cmd` refaz o nível todo a partir do GLB em ≈ 3 min):
- as camadas escondidas passaram a ser **pintadas** como as paredes (`ocultas_material`) em vez de apagadas: apagadas,
  deixavam ver o que está atrás nas pequenas falhas do modelo (juntas parede/teto na cozinha, um rasgo no teto do
  quarto 01). A correção de fundo é fechar essas juntas no modelo de visita (Blender);
- WC com luz de teto (900 lm, 3500 K, `luzes_extra`) e espelho a sério (`INT_D3D9DE_06`: metal, rugosidade 0,03; no AR
  é cinzento de propósito, sem sonda de reflexos);
- relva escurecida e menos saturada (×0,42/0,46/0,36: a relva real reflete ≈ 20 %; clara, enchia as salas de luz
  verde);
- aspeto escolhido entre 13 variantes (`ue/variantes.py`): 6500 K, tint 0,12, exposição +3,3 EV; por câmara: exterior
  +0,7, quarto 01 +1,5, quarto 03 +2,7 (`ue/pos_processo.py`).

**Imagens** (enviadas ao utilizador, só no PC): **Path Tracer** a 1920 × 1080, 256 amostras, ≈ 100 s por imagem na
RTX 2060 — realista (couro castanho, carvalho, sol da tarde, luz indireta), para as imagens de aprovação; **Lumen por
hardware** a 1080p — muito perto do Path Tracer, um leve véu azulado junto às janelas; é o que o cliente vê a andar.

**FPS, modo jogo, 1920 × 1080, RTX 2060** (CSV, últimos 1 500 de 3 000 frames):

| Perfil | Sala | Exterior |
|---|---|---|
| Lumen por software (1.º teste, aspeto mau) | 87 FPS (GPU 10,9 ms) | 91 FPS |
| Lumen por hardware, qualidade 2, nativo | **31 FPS** (GPU 31,1 ms) | **39 FPS** (GPU 24,6 ms) |
| Lumen por hardware, qualidade 1, TSR 67 % → 1080p | **40 FPS** (GPU 24,4 ms) | — |

Leitura: com o realismo que o utilizador pede, a RTX 2060 fica nos 30–40 FPS (o objetivo de 60 não se atinge). É o
dado que a auditoria pedia para decidir a placa (decisão do utilizador; nenhuma compra sem autorização). Opções:
afinar mais (TSR 50 %, sombras, reflexos sem *hit lighting*) e aceitar ≈ 45–50 FPS, ou uma placa mais forte (a
especificação aponta para a classe 4070/5070 Ti), ou servir o cliente a partir de uma GPU na nuvem (Fase 5).

## A seguir

1. **Tarefa 69 — materiais e luz:** (em curso; feito o que está acima) material mestre + instâncias por `MAT_*` (catálogo da Fase 3), importação do FBX
   (eixos e IDs); luz interior (os candeeiros do modelo como luzes), exposição e equilíbrio de brancos; chão à volta e
   relva. Comparar outra vez com o Blender, nas mesmas câmaras, e medir os FPS de novo.
2. Tarefa 70 — andar em primeira pessoa (colisões, altura dos olhos, portas).
3. Tarefa 68 — resolução e FPS de lançamento (com os números depois da 69).
4. Tarefa 71 — aprovação visual da DiscoverCasa.
