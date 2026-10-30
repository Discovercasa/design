# Migração para a conta enterprise do Claude (2026-10-13)

Tudo o que o Claude usa para trabalhar convosco, e onde está. O que não está no Git está marcado.

| O quê | Onde está | Vai com o repositório? |
|---|---|---|
| Conhecimento DiscoverCasa, Sobral, ferramentas, modelos, desenhos | este repositório `VascoCoelho/DiscoverCasa-Claude-BOB` | ✅ |
| Skills `ler-dwfx` e `modelo-blender-madeira` | `.claude/skills/` deste repositório | ✅ (ativam-se sozinhas ao abrir a pasta) |
| Agente `guardiao-detalhes` | `.claude/agents/` deste repositório | ✅ |
| Regras de trabalho (português, registar tudo, apontar problemas…) | `CLAUDE.md` + `conhecimento/discovercasa.md` | ✅ |
| Registo palavra a palavra das conversas | `conhecimento/registo-conversas.md` | ✅ |
| Memória automática do Claude dos 4 projetos (BOB, OASIUM, DiscoverCasa site, Sobral updated) | `migracao/memoria/` (cópia de `~/.claude/projects/*/memory`) | ✅ — repor com o script |
| Definições do Claude (plugin `mattpocock-skills`) | `migracao/claude-settings.json` | ✅ — reinstalar o plugin |
| Repositório OASIUM | `VascoCoelho/OASIUM` (tudo enviado a 2026-10-13) | ✅ (é outro repositório) |
| Conversas antigas completas (4 projetos, 49 ficheiros) | `_trabalho/migracao/conversas-claude-2026-10-13.zip` (121 MB, **fora do Git**) | ❌ copiar à mão (pen, OneDrive) |
| Site: `Desktop\DiscoverCasa site\discovercasa` | repositório `VascoCoelho/DiscoverCasaSite` (main e 6 ramos no GitHub) | ✅ — só o ramo `sobre-hero-foto` (1 commit wip de 20/08) estava apenas no PC |
| Site: `tools/estrutura3d/estrutura.blend` e `render/` (108 MB) | só no PC (ignorados pelo git) | não fazem falta: o modelo é gerado por `estrutura.py` e o site usa os WebP já em `draft/assets/estrutura/` |
| Site: `Desktop\DiscoverCasa site\.claude` (fora do repositório) | `launch.json` (servidor: `python tools/devserver.py 4321 draft`), permissões locais, cópia das skills GSAP | não faz falta (as skills GSAP estão no repositório) |
| Pasta `Desktop\Sobral updated` | só neste PC (não é repositório git) | ❌ copiar à mão, ou criar repositório |
| Conversas, projetos e artefactos no claude.ai da conta antiga | na nuvem da conta antiga | ❌ claude.ai → Settings → Privacy → Export data |

## Mesmo PC, só muda a conta
1. Terminar sessão no Claude (app/Claude Code) e entrar com a conta enterprise.
2. Abrir a pasta `BOB Claude` como antes: o `CLAUDE.md`, as skills e o agente carregam sozinhos.
3. A memória e as conversas ficam em `C:\Users\<utilizador>\.claude` e normalmente continuam lá. Se a
   memória não aparecer (ou a organização a desativar), correr `python migracao/restaurar_memoria.py`.
4. Se o plugin não aparecer: no Claude Code, `/plugin marketplace add mattpocock/skills` e
   `/plugin install mattpocock-skills@mattpocock` (ou copiar `migracao/claude-settings.json` para
   `~/.claude/settings.json` se este ainda não tiver nada).

## PC novo
1. Instalar Git, Python ≥ 3.10, Blender ≥ 4.4 e o Claude (app ou Claude Code); `gh auth login` com a
   conta GitHub que tem acesso (VascoCoelho, ou VascoDiscovercasa que tem escrita).
2. `git clone https://github.com/VascoCoelho/DiscoverCasa-Claude-BOB.git` (e o OASIUM, se preciso).
3. `cd DiscoverCasa-Claude-BOB` → `git config core.quotepath false` → `python ferramentas/verificar.py`.
4. Copiar as pastas `DiscoverCasa site` e `Sobral updated` (se forem precisas) e o zip das conversas.
5. `python migracao/restaurar_memoria.py --conversas "<caminho do zip>"`, com
   `--pasta "OASIUM=<caminho>"` (e o mesmo para as outras) se não estiverem no Desktop.
6. Reinstalar o plugin (passo 4 acima).

## Claude na web (sessões na nuvem)
Lá não existe a memória local: tudo o que importa já está no repositório (`CLAUDE.md`, `conhecimento/`,
`Construção Sobral/docs/estado.md` com o ponto de retoma). O administrador da organização tem de dar
acesso ao repositório no GitHub (app do Claude no GitHub).

## Notas
- A memória é por pasta: a chave é o caminho completo da pasta com tudo o que não é letra ou algarismo
  trocado por "-". O script calcula a chave nova sozinho.
- Para atualizar esta cópia mais tarde (antes de mudar de vez): voltar a copiar `~/.claude/projects/*/memory`
  para `migracao/memoria/` e fazer commit.
