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
| `ue/capturas.py` | Unreal, editor com GPU | aquece (compila tudo o que as vistas pedem), mede o tempo de frame em cada vista e tira uma imagem por câmara |

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

A RTX 2060 chega para o visualizador a 1080p (critério de 60 FPS com margem); a decisão da placa (auditoria, «manter a
RTX 2060 até ao primeiro teste») fica: **não é preciso trocar** para o visualizador. A VR (Fase 8) é outro orçamento
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

## A seguir

1. **Tarefa 69 — materiais e luz:** material mestre + instâncias por `MAT_*` (catálogo da Fase 3), importação do FBX
   (eixos e IDs); luz interior (os candeeiros do modelo como luzes), exposição e equilíbrio de brancos; chão à volta e
   relva. Comparar outra vez com o Blender, nas mesmas câmaras, e medir os FPS de novo.
2. Tarefa 70 — andar em primeira pessoa (colisões, altura dos olhos, portas).
3. Tarefa 68 — resolução e FPS de lançamento (com os números depois da 69).
4. Tarefa 71 — aprovação visual da DiscoverCasa.
