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
  JSON (fase, futuro) e marcar a tarefa no hub. Testes: `tests/` (Playwright, base simulada).
- **Marcar no hub o que se conclui** (pedido de 2026-11-06): sempre que uma tarefa ou uma nota de teste do hub fica feita,
  marcá-la concluída / resolvida no hub (Supabase "Design") no mesmo trabalho, com uma notificação para a equipa.
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
- **Chat da equipa** (ícone à esquerda das Sugestões; migração 0018, 2026-11-11; `public/js/hub/chat.js`): conversas
  diretas e de grupo com texto, ficheiros, imagens/vídeos e áudios; cada conversa só a veem os seus membros (nem quem
  edita); ficheiros no armazenamento privado `chat`, pasta por conversa. As conversas criam-se pela função
  `abrir_conversa`. **O Claude escreve pela base de dados** (sem sessão: `autor_id` null, `autor_nome` 'Claude', numa
  conversa `claude = true` com a pessoa como único membro) e lê as respostas na tabela `mensagens`. Comentários do
  Claude nas sugestões: `sugestoes_comentarios` com `autor_id` null (migração 0019).
- **Página de um projeto** (2026-11-11, sugestões do Geral): abas `#/projeto/<slug>/<aba>` (workflow, documentos,
  teste-ar, custos, sobre); checkpoints e tarefas começam fechados.
- **Repositório público**: nunca dados pessoais nem desenhos de clientes (`*.dwfx`, `*.pdf` estão no `.gitignore`;
  ficam só no PC).
