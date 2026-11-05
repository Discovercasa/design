# Projetos: pastas, ramos e hierarquia

Cada projeto tem o seu sítio para nada se misturar. O hub (`public/index.html`) mostra-os a todos; cada projeto tem
uma página (`#/projeto/<slug>`), um ficheiro de dados, uma pasta de código e um prefixo de ramo.

| Projeto | id (base de dados) | Página | Dados fixos | Código | Publicado em | Ramos |
|---|---|---|---|---|---|---|
| Build Your House | `build_your_house` | `#/projeto/build-your-house` | `public/dados/projetos/build_your_house.json` | `BOB/configurador/` | `public/build-your-house/` | `build-your-house/<tarefa>` |
| Builder | `builder` | `#/projeto/builder` | `public/dados/projetos/builder.json` | `BOB/ferramentas/modelo/`, `BOB/conhecimento/` | (ainda sem página) | `builder/<tarefa>` |
| Gerador de documentos | `gerador` | `#/projeto/gerador` | `public/dados/projetos/gerador.json` | `BOB/gerador/web/`, `BOB/ferramentas/documentos/` | `public/gerador/` | `gerador/<tarefa>` |
| Orçamentação | `orcamentacao` | `#/projeto/orcamentacao` | `public/dados/projetos/orcamentacao.json` | `BOB/orcamentacao/` (a criar) | (ainda sem página) | `orcamentacao/<tarefa>` |
| Step Inside (VR/AR) | `plataforma_cliente` | `#/projeto/step-inside` | `public/dados/projetos/plataforma_cliente.json` | `BOB/step-inside/` (a criar) | (ainda sem página) | `step-inside/<fase>-<tarefa>` |
| Hub do Design | — | `#/` | `public/dados/novidades.json` | `public/index.html`, `public/js/hub/`, `public/css/hub.css` | `public/` | `hub/<tarefa>` |

## Regras
- **Um ramo por tarefa**, com o prefixo do projeto (ex.: `gerador/ler-dxf`). `main` = o que está online: um push para
  `main` publica o site (Cloudflare Pages). Junta-se a `main` quando a tarefa está pronta e testada.
- **Uma tarefa mexe só na pasta do seu projeto.** O que é partilhado (o motor em `BOB/ferramentas/`, `BOB/conhecimento/`,
  `public/js/design-core.js`) muda num ramo próprio e diz-se na página dos projetos afetados.
- **O id do projeto nunca muda** (é a chave na base de dados); o nome que aparece pode mudar no JSON e na tabela `projetos`.
- **O texto fixo de um projeto** (o que é, objetivos, fase, futuro, ligações, organização) está no seu JSON: atualiza-o
  no mesmo commit que muda o projeto. **O que muda todos os dias** (checkpoints, tarefas, decisões) vive no Supabase e
  edita-se no próprio hub.
- **Aplicações independentes**: cada uma funciona sozinha. Só se usam juntas quando isso poupa tempo e tokens; nesse caso
  a tarefa leva "App sugerida" e o hub mostra "Sugerido: usar <app>".
- **Documentos de cada projeto** (secção Documentos do hub): *informativos* = o que o projeto é (especificações, planos);
  *adicionais* = conhecimento extra (desenhos de obras, fichas, fotografias). Os ficheiros ficam no armazenamento privado
  `documentos` do Supabase (caminho `<id>/<tipo>/<nome>`), nunca no Git; carregam-se no próprio hub.
- **Base de dados**: cada mudança é uma migração nova em `supabase/migrations/NNNN_nome.sql` (nunca editar uma já aplicada).
- **Testes**: `cd tests && npm install && npx playwright install chromium && npm test` (base simulada, não toca na produção).
