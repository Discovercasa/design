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
