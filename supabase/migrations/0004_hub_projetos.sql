-- Hub de projetos (2026-11-05): "criar um hub onde os nossos projetos vivem" — cada projeto com checkpoints e tarefas,
-- decisões com opções (vantagens, desvantagens, custos) que ficam registadas, notificações de tarefas e o "Novo" da
-- primeira vez que alguém vê um checkpoint ou tarefa acrescentados por outra pessoa.
-- O texto fixo de cada projeto (o que é, objetivos, fase, histórico, ligações) está em public/dados/projetos/<id>.json.

-- Projetos: o id é estável (o nome que aparece pode mudar: plataforma_cliente chama-se agora "Step Inside").
create table public.projetos (
  id text primary key check (id ~ '^[a-z_]{2,40}$'),
  nome text not null check (char_length(nome) between 2 and 80),
  ordem int not null default 0
);
insert into public.projetos (id, nome, ordem) values
  ('build_your_house', 'Build Your House', 1),
  ('builder', 'Builder', 2),
  ('gerador', 'Gerador de documentos', 3),
  ('orcamentacao', 'Orçamentação', 4),
  ('plataforma_cliente', 'Step Inside', 5);
alter table public.projetos enable row level security;
create policy "Ver" on public.projetos for select to authenticated using ((select public.pode_ver()));
create policy "Editar" on public.projetos for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));

-- Perfis: o nome de cada pessoa (para atribuir tarefas) e até quando já viu as notificações. Cada um escreve o seu.
create table public.perfis (
  id uuid primary key default auth.uid() references auth.users (id) on delete cascade,
  nome text not null default '' check (char_length(nome) <= 120),
  criado_em timestamptz not null default now(),
  notificacoes_vistas_em timestamptz not null default now()
);
alter table public.perfis enable row level security;
create policy "Ver" on public.perfis for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.perfis for insert to authenticated
  with check ((select public.pode_ver()) and id = (select auth.uid()));
create policy "Editar" on public.perfis for update to authenticated
  using (id = (select auth.uid())) with check (id = (select auth.uid()));

create or replace function public.nome_atual() returns text language sql stable set search_path = '' as $$
  select coalesce(nullif((select p.nome from public.perfis p where p.id = (select auth.uid())), ''),
                  nullif((select auth.jwt()) -> 'user_metadata' ->> 'nome', ''), 'Alguém')
$$;

-- Checkpoints: as metas de cada projeto, por ordem; cada um junta tarefas pequenas.
create table public.checkpoints (
  id bigint generated always as identity primary key,
  projeto text not null references public.projetos (id) on delete cascade,
  titulo text not null check (char_length(titulo) between 2 and 200),
  descricao text not null default '' check (char_length(descricao) <= 4000),
  ordem int not null default 0,
  estado text not null default 'por_fazer' check (estado in ('por_fazer', 'em_curso', 'concluido')),
  criado_por uuid default auth.uid(),
  criado_por_nome text not null default '' check (char_length(criado_por_nome) <= 120),
  criado_em timestamptz not null default now(),
  concluido_em date  -- só o dia
);
create index checkpoints_projeto_idx on public.checkpoints (projeto, ordem);

-- Tarefas: dentro de um checkpoint; quem a tem atribuída pode mudar o estado (mesmo só com "ver").
create table public.tarefas (
  id bigint generated always as identity primary key,
  checkpoint_id bigint not null references public.checkpoints (id) on delete cascade,
  projeto text not null references public.projetos (id) on delete cascade,  -- copiado do checkpoint (trigger)
  titulo text not null check (char_length(titulo) between 2 and 300),
  descricao text not null default '' check (char_length(descricao) <= 4000),
  estado text not null default 'por_fazer' check (estado in ('por_fazer', 'em_curso', 'bloqueada', 'concluida')),
  responsavel_id uuid references public.perfis (id) on delete set null,
  responsavel_nome text not null default '' check (char_length(responsavel_nome) <= 120),
  app_sugerida text references public.projetos (id) on delete set null,  -- "Sugerido: usar <app>"
  custo text not null default '' check (char_length(custo) <= 300),
  ordem int not null default 0,
  criado_por uuid default auth.uid(),
  criado_por_nome text not null default '' check (char_length(criado_por_nome) <= 120),
  criado_em timestamptz not null default now(),
  concluida_em date  -- só o dia
);
create index tarefas_checkpoint_idx on public.tarefas (checkpoint_id, ordem);
create index tarefas_projeto_idx on public.tarefas (projeto);
create index tarefas_responsavel_idx on public.tarefas (responsavel_id);
create index tarefas_app_idx on public.tarefas (app_sugerida);

-- Decisões: "vamos usar isto ou aquilo?" — todas as opções com vantagens, desvantagens e custos; ao decidir fica
-- registado o que escolhemos em vez das outras (as outras continuam guardadas).
create table public.decisoes (
  id bigint generated always as identity primary key,
  projeto text not null references public.projetos (id) on delete cascade,
  tarefa_id bigint references public.tarefas (id) on delete set null,
  pergunta text not null check (char_length(pergunta) between 3 and 300),
  contexto text not null default '' check (char_length(contexto) <= 4000),
  estado text not null default 'aberta' check (estado in ('aberta', 'decidida')),
  opcao_escolhida bigint,
  justificacao text not null default '' check (char_length(justificacao) <= 4000),
  decidida_por uuid,
  decidida_por_nome text not null default '' check (char_length(decidida_por_nome) <= 120),
  decidida_em date,
  criado_por uuid default auth.uid(),
  criado_por_nome text not null default '' check (char_length(criado_por_nome) <= 120),
  criado_em timestamptz not null default now()
);
create index decisoes_projeto_idx on public.decisoes (projeto);
create index decisoes_tarefa_idx on public.decisoes (tarefa_id);

create table public.decisoes_opcoes (
  id bigint generated always as identity primary key,
  decisao_id bigint not null references public.decisoes (id) on delete cascade,
  titulo text not null check (char_length(titulo) between 1 and 200),
  descricao text not null default '' check (char_length(descricao) <= 2000),
  vantagens text not null default '' check (char_length(vantagens) <= 2000),
  desvantagens text not null default '' check (char_length(desvantagens) <= 2000),
  custo text not null default '' check (char_length(custo) <= 300),
  ordem int not null default 0
);
create index decisoes_opcoes_decisao_idx on public.decisoes_opcoes (decisao_id, ordem);
alter table public.decisoes add constraint decisoes_opcao_escolhida_fkey
  foreign key (opcao_escolhida) references public.decisoes_opcoes (id) on delete set null;
create index decisoes_opcao_idx on public.decisoes (opcao_escolhida);

-- Notificações: escritas só pelos triggers. destinatario_id nulo = toda a equipa.
create table public.notificacoes (
  id bigint generated always as identity primary key,
  projeto text references public.projetos (id) on delete cascade,
  tipo text not null check (tipo in ('tarefa_nova', 'tarefa_atribuida', 'tarefa_estado', 'tarefa_concluida',
    'checkpoint_novo', 'checkpoint_estado', 'checkpoint_concluido', 'decisao_nova', 'decisao_tomada')),
  texto text not null,
  ator_id uuid,
  ator_nome text not null default '',
  destinatario_id uuid,
  ref_tipo text,
  ref_id bigint,
  criada_em timestamptz not null default now()
);
create index notificacoes_criada_idx on public.notificacoes (criada_em desc);
create index notificacoes_projeto_idx on public.notificacoes (projeto);
alter table public.notificacoes enable row level security;
create policy "Ver" on public.notificacoes for select to authenticated
  using ((select public.pode_ver()) and (destinatario_id is null or destinatario_id = (select auth.uid())));

-- Vistos: o que cada pessoa já viu (para o pop-up "Novo" aparecer só a primeira vez).
create table public.vistos (
  utilizador_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  tipo text not null check (tipo in ('checkpoint', 'tarefa', 'decisao')),
  ref_id bigint not null,
  visto_em timestamptz not null default now(),
  primary key (utilizador_id, tipo, ref_id)
);
alter table public.vistos enable row level security;
create policy "Ver" on public.vistos for select to authenticated using (utilizador_id = (select auth.uid()));
create policy "Criar" on public.vistos for insert to authenticated
  with check ((select public.pode_ver()) and utilizador_id = (select auth.uid()));
create policy "Apagar" on public.vistos for delete to authenticated using (utilizador_id = (select auth.uid()));

-- RLS de checkpoints, tarefas e decisões: quem vê, vê; quem edita cria, muda e apaga; o responsável muda o estado
-- da sua tarefa (o trigger tarefas_antes repõe os outros campos para quem só vê).
alter table public.checkpoints enable row level security;
create policy "Ver" on public.checkpoints for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.checkpoints for insert to authenticated with check ((select public.pode_editar()));
create policy "Editar" on public.checkpoints for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));
create policy "Apagar" on public.checkpoints for delete to authenticated using ((select public.pode_editar()));

alter table public.tarefas enable row level security;
create policy "Ver" on public.tarefas for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.tarefas for insert to authenticated with check ((select public.pode_editar()));
create policy "Editar" on public.tarefas for update to authenticated
  using ((select public.pode_editar()) or ((select public.pode_ver()) and responsavel_id = (select auth.uid())))
  with check ((select public.pode_editar()) or ((select public.pode_ver()) and responsavel_id = (select auth.uid())));
create policy "Apagar" on public.tarefas for delete to authenticated using ((select public.pode_editar()));

alter table public.decisoes enable row level security;
create policy "Ver" on public.decisoes for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.decisoes for insert to authenticated with check ((select public.pode_editar()));
create policy "Editar" on public.decisoes for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));
create policy "Apagar" on public.decisoes for delete to authenticated using ((select public.pode_editar()));

alter table public.decisoes_opcoes enable row level security;
create policy "Ver" on public.decisoes_opcoes for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.decisoes_opcoes for insert to authenticated with check ((select public.pode_editar()));
create policy "Editar" on public.decisoes_opcoes for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));
create policy "Apagar" on public.decisoes_opcoes for delete to authenticated using ((select public.pode_editar()));

-- ---------------------------------------------------------------------------------------------------------------
-- Triggers: carimbos (quem, quando — só o dia ao concluir) e notificações. Sem sessão (migrações) não notificam.
create or replace function public.notificar(p_projeto text, p_tipo text, p_texto text, p_ref_tipo text, p_ref_id bigint,
                                            p_dest uuid default null) returns void
language sql security definer set search_path = '' as $$
  insert into public.notificacoes (projeto, tipo, texto, ator_id, ator_nome, destinatario_id, ref_tipo, ref_id)
  select p_projeto, p_tipo, left(p_texto, 600), (select auth.uid()), public.nome_atual(), p_dest, p_ref_tipo, p_ref_id
  where (select auth.uid()) is not null
$$;
revoke execute on function public.notificar(text, text, text, text, bigint, uuid) from public, anon, authenticated;

create or replace function public.rotulo_estado(e text) returns text language sql immutable set search_path = '' as $$
  select case e when 'por_fazer' then 'Por fazer' when 'em_curso' then 'Em curso' when 'bloqueada' then 'Bloqueada'
                when 'concluida' then 'Concluída' when 'concluido' then 'Concluído' else e end
$$;

create or replace function public.checkpoints_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
    if new.estado = 'concluido' and new.concluido_em is null then new.concluido_em := current_date; end if;
  else
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
    if new.estado is distinct from old.estado then
      new.concluido_em := case when new.estado = 'concluido' then current_date end;
    end if;
  end if;
  return new;
end $$;
create trigger checkpoints_antes before insert or update on public.checkpoints
  for each row execute function public.checkpoints_antes();

create or replace function public.checkpoints_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare t text := '«' || new.titulo || '»';
begin
  if tg_op = 'INSERT' then
    perform public.notificar(new.projeto, 'checkpoint_novo', public.nome_atual() || ' acrescentou o checkpoint ' || t, 'checkpoint', new.id);
  elsif new.estado is distinct from old.estado then
    if new.estado = 'concluido' then
      perform public.notificar(new.projeto, 'checkpoint_concluido', public.nome_atual() || ' concluiu o checkpoint ' || t, 'checkpoint', new.id);
    else
      perform public.notificar(new.projeto, 'checkpoint_estado', public.nome_atual() || ' mudou o checkpoint ' || t || ' para '
        || public.rotulo_estado(new.estado), 'checkpoint', new.id);
    end if;
  end if;
  return null;
end $$;
create trigger checkpoints_depois after insert or update on public.checkpoints
  for each row execute function public.checkpoints_depois();

create or replace function public.tarefas_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
    if new.estado = 'concluida' and new.concluida_em is null then new.concluida_em := current_date; end if;
  else
    if not public.pode_editar() then  -- o responsável que só vê: muda apenas o estado
      new.titulo := old.titulo; new.descricao := old.descricao; new.checkpoint_id := old.checkpoint_id;
      new.responsavel_id := old.responsavel_id; new.responsavel_nome := old.responsavel_nome;
      new.app_sugerida := old.app_sugerida; new.custo := old.custo; new.ordem := old.ordem;
    end if;
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
    if new.estado is distinct from old.estado then
      new.concluida_em := case when new.estado = 'concluida' then current_date end;
    end if;
  end if;
  select c.projeto into new.projeto from public.checkpoints c where c.id = new.checkpoint_id;
  if new.responsavel_id is null then
    new.responsavel_nome := '';
  elsif tg_op = 'INSERT' or new.responsavel_id is distinct from old.responsavel_id then
    new.responsavel_nome := coalesce((select nullif(p.nome, '') from public.perfis p where p.id = new.responsavel_id),
                                     nullif(new.responsavel_nome, ''), 'Alguém');
  end if;
  return new;
end $$;
create trigger tarefas_antes before insert or update on public.tarefas
  for each row execute function public.tarefas_antes();

create or replace function public.tarefas_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare t text := '«' || new.titulo || '»'; quem text := public.nome_atual();
begin
  if tg_op = 'INSERT' then
    perform public.notificar(new.projeto, 'tarefa_nova', quem || ' acrescentou a tarefa ' || t, 'tarefa', new.id);
  end if;
  if new.responsavel_id is not null and (tg_op = 'INSERT' or new.responsavel_id is distinct from old.responsavel_id) then
    perform public.notificar(new.projeto, 'tarefa_atribuida', quem || ' atribuiu a tarefa ' || t || ' a ' || new.responsavel_nome, 'tarefa', new.id);
  end if;
  if tg_op = 'UPDATE' and new.estado is distinct from old.estado then
    if new.estado = 'concluida' then
      perform public.notificar(new.projeto, 'tarefa_concluida', quem || ' concluiu a tarefa ' || t, 'tarefa', new.id);
    else
      perform public.notificar(new.projeto, 'tarefa_estado', quem || ' mudou a tarefa ' || t || ' para ' || public.rotulo_estado(new.estado), 'tarefa', new.id);
    end if;
  end if;
  return null;
end $$;
create trigger tarefas_depois after insert or update on public.tarefas
  for each row execute function public.tarefas_depois();

create or replace function public.decisoes_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
  else
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
  end if;
  if new.estado = 'decidida' then
    if new.opcao_escolhida is null or not exists (
        select 1 from public.decisoes_opcoes o where o.id = new.opcao_escolhida and o.decisao_id = new.id) then
      raise exception 'Escolha uma das opções desta decisão.';
    end if;
    if tg_op = 'INSERT' or old.estado <> 'decidida' or new.opcao_escolhida is distinct from old.opcao_escolhida then
      if (select auth.uid()) is not null then
        new.decidida_por := (select auth.uid()); new.decidida_por_nome := public.nome_atual(); new.decidida_em := current_date;
      elsif new.decidida_em is null then new.decidida_em := current_date;
      end if;
    end if;
  else
    new.opcao_escolhida := null; new.decidida_por := null; new.decidida_por_nome := ''; new.decidida_em := null;
  end if;
  return new;
end $$;
create trigger decisoes_antes before insert or update on public.decisoes
  for each row execute function public.decisoes_antes();

create or replace function public.decisoes_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare escolhida text; outras text;
begin
  if tg_op = 'INSERT' then
    perform public.notificar(new.projeto, 'decisao_nova', public.nome_atual() || ' abriu a decisão «' || new.pergunta || '»', 'decisao', new.id);
  elsif new.estado = 'decidida' and (old.estado <> 'decidida' or new.opcao_escolhida is distinct from old.opcao_escolhida) then
    select o.titulo into escolhida from public.decisoes_opcoes o where o.id = new.opcao_escolhida;
    select string_agg('«' || o.titulo || '»', ', ' order by o.ordem) into outras
      from public.decisoes_opcoes o where o.decisao_id = new.id and o.id <> new.opcao_escolhida;
    perform public.notificar(new.projeto, 'decisao_tomada', public.nome_atual() || ' decidiu «' || new.pergunta || '»: escolhemos «'
      || escolhida || '»' || coalesce(' em vez de ' || outras, ''), 'decisao', new.id);
  end if;
  return null;
end $$;
create trigger decisoes_depois after insert or update on public.decisoes
  for each row execute function public.decisoes_depois();

-- as funções dos triggers não se chamam diretamente
revoke execute on function public.checkpoints_antes(), public.checkpoints_depois(), public.tarefas_antes(),
  public.tarefas_depois(), public.decisoes_antes(), public.decisoes_depois() from public, anon, authenticated;
