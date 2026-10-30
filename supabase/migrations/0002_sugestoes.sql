-- Sugestões da equipa sobre as ferramentas do Design (página inicial, secção "Sugestões").
-- Quem pode ver também pode sugerir (é a ideia da secção); só quem pode editar muda o estado ou apaga.

create table public.sugestoes (
  id bigint generated always as identity primary key,
  texto text not null check (char_length(texto) between 3 and 2000),
  ferramenta text not null default 'geral'
    check (ferramenta in ('geral', 'build_your_house', 'builder', 'gerador', 'orcamentacao', 'plataforma_cliente')),
  estado text not null default 'nova' check (estado in ('nova', 'em_analise', 'feita', 'recusada')),
  autor_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  autor_nome text not null default '' check (char_length(autor_nome) <= 120),
  criada_em timestamptz not null default now()
);
create index sugestoes_autor_idx on public.sugestoes (autor_id);
create index sugestoes_criada_idx on public.sugestoes (criada_em desc);

alter table public.sugestoes enable row level security;
create policy "Ver" on public.sugestoes for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.sugestoes for insert to authenticated
  with check ((select public.pode_ver()) and autor_id = (select auth.uid()) and estado = 'nova');
create policy "Editar" on public.sugestoes for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));
create policy "Apagar" on public.sugestoes for delete to authenticated using ((select public.pode_editar()));
