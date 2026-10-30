# Discovercasa Design

Site do Design (`https://design.discovercasa.pt`). Estático (Cloudflare Pages, pasta `public/`) + Supabase (projeto "Design").

- **Entrada:** com a conta do Hub. O Hub (permissão "Design") cria a pessoa aqui e envia um código de uso único por `postMessage`; o site troca-o por uma sessão (`verifyOtp`). O nível (`ver` / `editar`) fica em `app_metadata.nivel`.
- **Base de dados:** `supabase/migrations/`. Todas as tabelas com RLS por `pode_ver()` / `pode_editar()`.
- Regras para quem programa: `CLAUDE.md`.
