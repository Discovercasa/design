# Instruções para o Claude — Discovercasa Design

Projeto Design da Discovercasa (`design.discovercasa.pt`). Responder em português de Portugal.

## O que é e o que não é
- Este repositório e o projeto Supabase "Design" (organização "Design") são **só do Design**.
- O **Hub** (`hub.discovercasa.pt`) é outro projeto, noutra organização e noutro repositório. **Nunca** lhe mexer, nunca o procurar, nunca pedir acesso a ele.
- As contas vêm do Hub: entra-se pelo botão "Entrar com a conta do Hub" (ou pelo separador Design do Hub). **Não criar registo, palavras-passe nem outra forma de entrar.** Em Authentication, "Allow new users to sign up" fica **desligado**.

## Regras
- **Nunca credenciais privadas no código.** Só a chave pública (publishable) do Supabase, em `public/js/design-core.js`. Nada de `service_role`, passwords, tokens ou `.env` no repositório.
- **Todas as tabelas com RLS**, com as funções `public.pode_ver()` / `public.pode_editar()` (o nível vem do Hub em `app_metadata.nivel`). Escrever sempre `(select public.pode_ver())` nas regras. Modelo em `supabase/migrations/0001_base.sql`.
- Alterações à base de dados: guardar o SQL em `supabase/migrations/NNNN_nome.sql`.
- Não mudar a entrada (`design-core.js`: `esperarCodigo`, `avisarHub`, `entrarPeloHub`) sem falar com o Sebastião — é a ponte com o Hub.
- Não acrescentar dependências sem perguntar.

## Publicação
- Cloudflare Pages (projeto `design`): publica a pasta `public/` a cada push para `main`.

## Aplicações e BOB (desde 2026-11-05)
- Este é o repositório onde se fazem as mudanças a **todas as aplicações em desenvolvimento** (Build Your House,
  gerador de documentos, orçamentação, plataforma do cliente, construtor). O antigo repositório privado do BOB já não se usa.
- O conhecimento e as ferramentas da DiscoverCasa estão em `BOB/`. **Para qualquer trabalho de aplicações ou de casas, ler
  primeiro `BOB/CLAUDE.md`** (regras, mapa, registo de cada detalhe). Os caminhos nos documentos do BOB são relativos a `BOB/`.
- Os agentes `guardiao-detalhes` e `mestre-construtor` estão em `BOB/.claude/agents/`. Se não aparecerem como agentes,
  lançar um agente geral com o conteúdo desse ficheiro como instruções.
- O site serve versões compiladas: depois de mudar `BOB/configurador/web`, `BOB/gerador/web` ou o motor
  (`BOB/ferramentas/`), correr `python BOB/ferramentas/construir_site.py` e fazer commit do resultado
  (`public/build-your-house/`, `public/gerador/`) junto com a mudança.
- **Organização por projeto** (pasta, ramo `<projeto>/<tarefa>`, ficheiro de dados, id): `PROJETOS.md`. O hub
  (`public/index.html` + `public/js/hub/`) lê o texto fixo de cada projeto em `public/dados/projetos/<id>.json` e os
  checkpoints, tarefas e decisões do Supabase (migrações 0004/0005). Ao fazer uma entrega num projeto, atualizar o seu
  JSON (fase, situacao, futuro) e marcar a tarefa no hub. Testes: `tests/` (Playwright, base simulada).
- **Marcar no hub o que se conclui** (pedido de 2026-11-06): sempre que uma tarefa ou uma nota de teste do hub fica feita,
  marcá-la concluída / resolvida no hub (Supabase "Design") no mesmo trabalho, com o pormenor no Log (`registo`); uma
  notificação só se tiver impacto (tarefa ou checkpoint concluído) — pedido de 2026-11-11: «apenas deves fornecer
  notificações para coisas que têm impacto».
- **Redes sociais** (aba do hub, `#/social`): planeamento dos posts, aprovação, obras e fases (migrações 0009/0010,
  `public/js/hub/social*.js`). As fotos ficam no armazenamento privado `social`, nunca no Git.
- **Materiais do Hub** (aba do hub, `#/materiais`; migração 0016, 2026-11-10): materiais, preços por fornecedor e
  histórico de preços, nas tabelas `hub_*`. O Hub envia-as nos dias úteis às 6h (Lisboa) com a chave de serviço deste
  projeto. **Só de consulta:** nunca escrever nelas, nunca acrescentar regras de criar/editar/apagar nem mudar colunas
  sem falar com o Sebastião (o envio do Hub deixava de funcionar). Para as ler (hub e aplicações), usar o módulo comum
  `public/js/materiais.js`; os projetos que as usam dizem para quê no campo `materiais` do seu JSON.
- **Orçamentação** (`/orcamentacao/`, 2026-11-11): cada linha da Listagem de material tem um código de produto estável
  (`BOB/ferramentas/documentos/codigos.py`); `BOB/orcamentacao/ligacoes.json` liga cada código a um material do Hub (só o
  id: nunca nomes nem preços do Hub no repositório público); o cálculo comum é `public/js/orcamento.js`. As parcelas do
  preço final (mão de obra, fundação, margem, IVA…) ficam só na tabela `orcamento_parcelas` (migração 0017), nunca no código.
- **Trabalho em equipa** (2026-11-11; migrações 0022/0023; `public/js/hub/ficha.js`, `equipa.js`, `conversa.js`):
  o Início abre um pop-up por projeto (o que está em curso e precisa de atenção); cada tarefa ou checkpoint tem o seu
  ecrã (ponto de situação por tópicos, pedir ponto de situação, sugerir, pedir aprovação → estado `por_aprovar`, quem
  edita aprova ou devolve, pessoas marcadas em `marcacoes`, conversa em `atividade` com anexos no armazenamento
  privado `chat`); críticas por projeto (`criticas`), com o botão «Comentar» na barra do hub e dentro das apps
  (`public/js/comentar.js`, carregado pela `porta.js` e pela `ar-teste.html`; o projeto vem do caminho da página). **Notificações só para o que tem impacto** (checkpoint ou tarefa
  concluída, decisão aberta/tomada, crítica, pedido de aprovação de um post) **e as pessoais**; tudo o resto vai para
  o **Log** (`registo`, separador ao lado da Checklist, avisos de lado ao abrir o hub). **O Claude escreve pela base
  de dados** (sem sessão: autor 'Claude'): no Log com o pormenor (`registo.detalhe`), na conversa da tarefa
  (`atividade`) e marca pessoas (`marcacoes`); lê as respostas na `atividade`. O chat geral (0018–0020) saiu.
  Comentários do Claude nas sugestões: `sugestoes_comentarios` com `autor_id` null (migração 0019).
- **Documentos: secções e pastas** (2026-11-11, migração 0024): `documentos_seccoes` (por projeto e tipo, criadas por quem
  edita, existem vazias); cada documento tem `seccao_id` e `pasta` (o caminho da pasta de onde veio, só para mostrar; o
  ficheiro fica em `<projeto>/<tipo>/<nome>`); uma pasta carregada de uma vez tem um `lote` e uma só linha no Log
  (`documentos_lote_feito`). O Claude lê a estrutura pela base de dados; o conteúdo dos ficheiros está no armazenamento
  privado e só se lê descarregando-o: **por uma função temporária com chave de uso único** (decisão do utilizador,
  2026-11-11: «ok chave de uso único então»), desligada logo a seguir (410, `verify_jwt`) e a chave apagada, como no
  carregamento dos modelos AR. Nenhuma chave permanente guardada.
- **Aba Páginas** (2026-11-12, migração 0025; o JSON do projeto diz `"paginas": true`, hoje só o Builder): as páginas
  entregues aos clientes são documentos do tipo `pagina` no armazenamento privado `documentos` (nunca no Git: são casas de
  clientes) e abrem-se noutra janela a partir da memória; a aba tem os seus checkpoints (`checkpoints.aba = 'paginas'`,
  fora do Workflow). O Claude carrega uma página pela função temporária com chave de uso único (como os modelos AR).
- **Página de um projeto** (2026-11-11): abas Workflow, Documentos e (Step Inside) Teste do AR; pipeline e «sobre»
  dentro do Workflow; tudo fechado sempre que se abre; descrição das tarefas em acordeão; o ponto de situação do
  projeto é por tópicos no JSON (`situacao`: dia, feito, agora, falta) — atualizá-lo a cada entrega.
- **Repositório público**: nunca dados pessoais nem desenhos de clientes (`*.dwfx`, `*.pdf` estão no `.gitignore`;
  ficam só no PC).
