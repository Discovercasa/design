-- Design — o Claude comenta as sugestões que fez (2026-11-11: «queria que completasses as sugestões que foram feitas
-- para o Geral»). O Claude não tem conta: o comentário entra pela base de dados (sem sessão) com autor_id null e
-- autor_nome 'Claude'. Na página continua tudo igual: a regra "Criar" (0003) obriga autor_id = quem tem a sessão.
alter table public.sugestoes_comentarios alter column autor_id drop not null;
