# Registo das conversas (continuação, desde 2026-11-10) — what the user said, verbatim

Continues `registo-conversas.md`, which reached ~1 560 lines on 2026-11-09 (its entries run until that day). Same
rules: every message in which the user gives information, verbatim (typos included), dated, with what it answered and
where each fact was filed. Oldest first. Kept by the agent `guardiao-detalhes`. Grep both files for the user's exact
words (`registo-conversas*.md`). When this file passes about 1 500 lines, continue in `registo-conversas-2026-4.md`
(or `<year>-<n>`) and link it here.

### 2026-11-09 — AR test on the phone: three bugs [Torres Vedras, Sobral]
> ok há alguns bugs :
>
> 1. dentro da casa tem paredes que estão abertas e o testo nota-se algumas linhas, principalmente nas portas não estão fechadas, da para ver o interior das paredes.
> 2. Da parte de fora na pérgola tem falhas visuais nas vigas superiores e dá para ver um gap enorme entre o teto e o telhado.
> 3. O nosso revestimento exterior o tremolo não tem o aspeto da textura de madeira que usaste, é um tremolo vertical mais fino e mais claro que o que usaste podes rever na fotos penso que tenhas acesso, se não tiveres diz-me que eu mando-te uma foto do aspeto do nosso tremolo
- Context: feedback after testing the AR models from the hub on a phone (hub tasks 84, 157).
- Filed in: `step-inside/docs/fase7/README.md` → bugs 1-3, causes and fixes (version 2 of the 8 AR files);
  `conhecimento/sistema-construtivo.md` → finish option A, "Look of the real Tremolo" (vertical, finer, lighter;
  photo pending); bugs 1-2 are AR-export issues (openings lined, pergola timber visible), no method change.
- Pending: the user's photo of the real Tremolo (look, board width, colour) — replaces the provisional #8E6A48.
  (closed 2026-11-09, see the next entry)

### 2026-11-09 — Photo of the built Torres Vedras house: colour, AR gaps bug, flat plasterboard [Torres Vedras]
> esta é na realidade a casa de torres vedras, e tinha-me esquecido de mencionar um ponto, havia pequenos gaps no tremolo e conseguia-se ver o interior através desses pequenos gaps
> o gesso cartonado do interior é plano não tem relevo nem imperfeições
- Context: sent with a photo of the built house (marketing photo, garden side; not stored in Git), after the AR
  test entry above (bug 3, Tremolo look). The "gaps" sentence is one more AR bug ("tinha-me esquecido de mencionar um
  ponto"): gaps between the cladding pieces of the 3D model showed the interior once the membrane was removed in the
  AR. Not a statement about the real façade (Piveteau 22×135 tongue and groove stands). Fix: the membrane behind the
  cladding stays visible in the AR, so the gaps between model pieces no longer show the interior.
- Filed in: `Construção Torres Vedras/docs/estado.md` → "As-built look: photo of the built house" (colours, pergola,
  surroundings, reference for task 158); `conhecimento/sistema-construtivo.md` → §2 finish A (colour from the photo,
  note that the gaps were an AR bug) and §4 item 3 (smooth plasterboard);
  `step-inside/docs/fase7/README.md` → AR version 3 (done by the caller).
- Pending: the user approves or comments on AR version 3 (phone, next to the photo).
  (closed 2026-11-09, see the next entry)

### 2026-11-09 — AR version 3 approved; four new tasks; notify the team member [Torres Vedras, Sobral]
> está aprovada mas encaixa as seguintes tarefas no nosso workflow onde achas que elas deviam de ficar:
>
> 1. Fix no tremolo, continua com gaps entre as madeiras do revestimento exterior.
> 2. Adicionar interiores, para o cliente ter uma experiência o amis próximo possível de caminhar dentro da sua própria casa.
> 3. Se casa tiver dois pisos ou mais como é que o cliente pode ver o piso de cima ou o de baixo dependendo da casa ?
> 4. Nas portas interiores o chão na zona das portas está em cimento.
>
> Quero que notifiques o [membro da equipa] no HUB a dizer que versão teste AR está pronta e pode ser testada e que também pode escrever na descrição mudanças ou coisas que ele ache que estão bem ou mal.
- Context: reply to "A versão 3 está próxima da casa real?" (Step Inside, AR phase 7).
- Filed in: `step-inside/docs/fase7/README.md` → «Versão 3 aprovada e o que ficou» (items 1-4 placed in the
  workflow: hub tasks 164, 165, 166, 167; task 158 concluded; task 84 invites the team to write what is good / bad;
  the team member notified in the hub); `step-inside/docs/fase3/README.md` → «A seguir» item 2 (interiors library, task
  167); `public/dados/projetos/plataforma_cliente.json`; `Construção Torres Vedras/docs/estado.md` → AR v3 approved
  against the photo (one line); item 1 = AR / visit-model defect, not a real-façade fact (the real Tremolo is
  tongue and groove, no open joints; see the previous entry); item 4 = model defect (floor finish stops at the wall).
- Pending: task 164 (do the gaps also exist in the production Builder model?), 165 (cause unconfirmed), 166 (floor
  proposal to confirm with the user), 167 (scope: only what DiscoverCasa delivers vs also furniture; model source;
  downloads need authorization); the team member's feedback in task 84.

### 2026-11-09 — Go ahead with the two defects (Tremolo gaps, floor at doors) [Torres Vedras, Sobral]
> Sim, começa
- Context: answer to "Começo pelos dois defeitos (frestas no Tremolo e chão nas portas)?" (hub tasks 164 and 165).
- Filed in: `step-inside/docs/fase7/README.md` → «Versão 4» and `step-inside/docs/fase2/README.md` → «O que a visita
  acrescenta ao modelo de produção» (done by the caller; `plataforma_cliente.json` updated, tasks 164/165 concluded,
  AR v4 uploaded, same 8 documents). Cause of the gaps (measured by rays): the production model draws each Tremolo
  board 129 mm wide with a 6 mm `junta` (Pladur 2 mm) so pieces can be counted; without the hidden layers each joint
  was a slit in the visit/AR model. Fix in the visit model only: `step-inside/ferramentas/visita/juntas.py` closes the
  joints of finish layers in walls / ceilings / roof (floors, pergola untouched); the production JSON is unchanged. The
  real façade is tongue and groove (already recorded), consistent. Door floors: the finish stopped at the wall face, so
  doors showed the slab (TV 5 mm below the vinyl; Sobral a 16 cm step; Sobral upper floor a hole down to the
  ground-floor ceiling); fix = each side's floor runs to the middle of the wall, exterior doors take the inside floor
  to the outside face. This rule is INFERRED, not stated by the user.
  `conhecimento/perguntas-por-obra.md` → Q23: new OPEN item "floor at interior door openings" with this default.
- Pending: the user confirms DiscoverCasa's rule for the floor at interior doors (continuous vs transition profile /
  threshold) and the exterior threshold (Q23); the user's check of AR v4 on the phone.

### 2026-11-09 — Interior doors: the floor is continuous [Torres Vedras, Sobral]
> Sim, contínuo
- Context: answer to "Nas portas interiores, o pavimento continua por baixo da porta?" (choices: «Sim, contínuo» /
  «Leva perfil ou soleira»); follows the entry above (OPEN item under Q23).
- Filed in: `conhecimento/perguntas-por-obra.md` → Q23: interior-door part CONFIRMED (continuous floor under interior
  doors); the position of a change of finish stays INFERRED (under the door leaf, our choice); exterior threshold stays
  open. `conhecimento/sistema-construtivo.md` → §5 Floors: one line (floor continuous under interior doors).
  `step-inside/docs/fase2`, `fase7`, hub task 165 and `blender_visita.py` comment: done by the caller.
- Pending: (a) exterior-door threshold (Q23); (b) production-model quantity gap: `ferramentas/modelo/camadas.py`
  `pavimentos()` (~lines 1018-1026) lays each room's floor finish only over the usable area (room minus wall linings), so
  the strip under each interior door (≈ 0,87 × wall thickness, ≈ 0,1 m² per door) is neither modelled nor in the material
  list; to be proposed to the user (model change, not done).

### 2026-11-09 — Correct the production model: floor under the doors [Torres Vedras, Sobral]
> Sim, corrige
- Context: answer to "Corrijo já o modelo de produção para contar o chão por baixo das portas?" (the pending item (b) of
  the entry above).
- Filed in: `conhecimento/perguntas-por-obra.md` → Q23: PENDING (production model) closed 2026-11-09.
  `Construção Torres Vedras/docs/estado.md` and `Construção Sobral/docs/estado.md` → decision log: production model
  regenerated 2026-11-09 (floor under interior doors counted; quantities file also carries the 06-07/11 builder changes).
  `step-inside/docs/fase7` «Versão 4.1», `fase2`, hub task 165 and AR v4.1: done by the caller.
- Done (by the caller): `ferramentas/modelo/camadas.py` new `portas_paineis` + `faixas_portas`; `salas()` stores
  `casa.portas_salas[piso]`; `pavimentos()` extends each room's floor (finish; on the ground floor also the build-up
  layers) to the middle of the wall in each interior door; exterior doors left out (threshold open, Q23); usable room
  areas unchanged; finish objects carry `area_sob_portas_m2`. Rebuilt: TV vinyl 151,6 → 152,5 m² (8 interior doors);
  Sobral Tipo 1 vinyl 101,9 → 102,5 m², XPS 60 and betonilha 55,2 → 55,3 m²; validar issues 0.
- Side effect: the committed production outputs dated 2026-10-30, so the rebuild also brought in the builder changes of
  2026-11-06/07 (vergas; parapet roof-side face; hidden-gutter outlets 'Saída da caleira oculta (bocal)'; sandwich
  panel name 'Painel sandwich Munditelha'; Sobral option A ripado 413,7 → 633,5 m; TV timber total 1892,9 → 1891,9 m;
  'Remate lateral' gone in Sobral). Verified with the old `camadas.py` on the same geometry: only the floor rows are
  from this fix.

### 2026-11-09 — Hub UI: notification popover scroll, phase display order, phase-text accordion, AR on desktop [Step Inside, hub]
> no hub quando passamos sobre uma notificação com o rato desaparece que está por ler mas não deve levar de volta ao inicio senão não se consegue ler a notificação. Sei que antecipamos a fase 7 mas deve permanecer no lugar da fase 7 e não mexer na ordem visualmente. apenas mostrar que estamos a progredir na fase 7 e é isso.
- Context: user's own observation on the hub. Filed in: nothing in BOB (code fix in the design repo: `public/js/hub/app.js` `redesenharPop()` redraws the popover only when something changed and keeps the scroll; test `tests/notificacoes.spec.mjs`). Phase order: `conhecimento/discovercasa.md` (Phase order line) and `step-inside/docs/fase7/README.md` → display order = phase numbers; work order unchanged. Step Inside checkpoints in Supabase: Fase 7 back to position 8 (after Fase 6), still "em curso".

> (with a screenshot of the Step Inside project page, the long phase-status paragraph circled) colocaste aqui este texto que ocupa demasiado espaço marca-o como aquilo que ele representa num acordion
- Context: the long `fase_detalhe` text on the project page. Filed in: nothing in BOB (code: closed accordion «Ponto de situação das fases», `public/js/hub/vistas.js`, `public/css/hub.css`, for every project; test `tests/hub.spec.mjs`).

> e a secção de AR não aparece no HUB no desktop, foi propositado?
- Context: question. Answer: not removed; the live site shows AR on desktop; the user's page was an old open tab (still had the pre-today phase text). The hub does not refresh itself on a new deploy; reload fixes it. Filed in: `public/dados/novidades.json` (hub news, 2026-11-09). Possible improvement: auto-refresh/notice on a new deploy.

