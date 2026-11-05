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
- **Repositório público**: nunca dados pessoais nem desenhos de clientes (`*.dwfx`, `*.pdf` estão no `.gitignore`;
  ficam só no PC).
