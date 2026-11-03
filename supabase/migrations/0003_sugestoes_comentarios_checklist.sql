-- Sugestões: apagar, comentar e checklist (2026-11-03: "quero que seja possível eliminar sugestões, comentar sugestões
-- e adicionar sugestões a uma checklist").

-- Checklist: quem edita põe uma sugestão na checklist (regra "Editar" de 0002); a tarefa toma a cor do seu estado
-- (em_analise amarelo, feita = concluída verde, recusada vermelho).
alter table public.sugestoes
  add column na_checklist boolean not null default false,
  add column checklist_em timestamptz;
create index sugestoes_checklist_idx on public.sugestoes (checklist_em) where na_checklist;

-- Apagar: quem edita apaga qualquer uma; quem a escreveu apaga a sua enquanto não está na checklist (aí já é uma tarefa
-- da equipa). Uma só regra: duas regras "permissive" para a mesma ação são avaliadas as duas (o advisor assinala).
drop policy "Apagar" on public.sugestoes;
create policy "Apagar" on public.sugestoes for delete to authenticated
  using ((select public.pode_editar())
         or ((select public.pode_ver()) and autor_id = (select auth.uid()) and not na_checklist));

-- Comentários: quem vê comenta (em seu nome); quem o escreveu ou quem edita apaga. Não se editam.
create table public.sugestoes_comentarios (
  id bigint generated always as identity primary key,
  sugestao_id bigint not null references public.sugestoes (id) on delete cascade,
  texto text not null check (char_length(texto) between 1 and 2000),
  autor_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  autor_nome text not null default '' check (char_length(autor_nome) <= 120),
  criado_em timestamptz not null default now()
);
create index sugestoes_comentarios_sugestao_idx on public.sugestoes_comentarios (sugestao_id, criado_em);
create index sugestoes_comentarios_autor_idx on public.sugestoes_comentarios (autor_id);

alter table public.sugestoes_comentarios enable row level security;
create policy "Ver" on public.sugestoes_comentarios for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.sugestoes_comentarios for insert to authenticated
  with check ((select public.pode_ver()) and autor_id = (select auth.uid()));
create policy "Apagar" on public.sugestoes_comentarios for delete to authenticated
  using ((select public.pode_editar()) or ((select public.pode_ver()) and autor_id = (select auth.uid())));
