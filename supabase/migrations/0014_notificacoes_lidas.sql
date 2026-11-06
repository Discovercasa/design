-- Notificações vistas uma a uma (2026-11-07): "queria saber quais foram ou não vistas portanto a partir do momento que dão
-- hover ou clicam na notificação significa que já viram". Cada pessoa guarda as que já viu; as das suas próprias ações
-- contam como vistas. (perfis.notificacoes_vistas_em continua a valer para "Marcar todas como vistas" das mais antigas.)

create table public.notificacoes_lidas (
  utilizador_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  notificacao_id bigint not null references public.notificacoes (id) on delete cascade,
  lida_em timestamptz not null default now(),
  primary key (utilizador_id, notificacao_id)
);
create index notificacoes_lidas_notificacao_idx on public.notificacoes_lidas (notificacao_id);
alter table public.notificacoes_lidas enable row level security;
create policy "Ver" on public.notificacoes_lidas for select to authenticated using (utilizador_id = (select auth.uid()));
create policy "Criar" on public.notificacoes_lidas for insert to authenticated
  with check ((select public.pode_ver()) and utilizador_id = (select auth.uid()));
create policy "Apagar" on public.notificacoes_lidas for delete to authenticated using (utilizador_id = (select auth.uid()));

-- as outras janelas da mesma pessoa (computador e telemóvel) ficam a saber logo
alter publication supabase_realtime add table public.notificacoes_lidas;
