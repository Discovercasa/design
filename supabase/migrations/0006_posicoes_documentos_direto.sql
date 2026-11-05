-- Hub (2026-11-05, mais tarde): "Quando adicionamos um checkpoint deve ser possível escolher em que ordem entra";
-- "uma secção dentro de cada projeto ... chamada documentos" (Documentos Informativos e Documentos Adicionais);
-- "Sempre que há uma mudança nas tarefas ou checkpoints os outros sítios ... devem ser atualizados".

-- ---------------------------------------------------------------- posição dos checkpoints
-- Os checkpoints de um projeto ficam numerados 1..n; inserir ou mover abre espaço e renumera os outros.
create or replace function public.inserir_checkpoint(p_projeto text, p_titulo text, p_descricao text, p_posicao int)
returns bigint language plpgsql security invoker set search_path = '' as $$
declare n int; i bigint;
begin
  if not public.pode_editar() then raise exception 'Sem permissão para editar.'; end if;
  select count(*) into n from public.checkpoints where projeto = p_projeto;
  p_posicao := greatest(1, least(coalesce(p_posicao, n + 1), n + 1));
  with r as (select id, row_number() over (order by ordem, id) as rn from public.checkpoints where projeto = p_projeto)
  update public.checkpoints c set ordem = case when r.rn >= p_posicao then r.rn + 1 else r.rn end
    from r where c.id = r.id and c.ordem is distinct from (case when r.rn >= p_posicao then r.rn + 1 else r.rn end);
  insert into public.checkpoints (projeto, titulo, descricao, ordem)
    values (p_projeto, p_titulo, coalesce(p_descricao, ''), p_posicao) returning id into i;
  return i;
end $$;

create or replace function public.mover_checkpoint(p_id bigint, p_posicao int)
returns void language plpgsql security invoker set search_path = '' as $$
declare pr text; n int;
begin
  if not public.pode_editar() then raise exception 'Sem permissão para editar.'; end if;
  select projeto into pr from public.checkpoints where id = p_id;
  if pr is null then raise exception 'Checkpoint inexistente.'; end if;
  select count(*) into n from public.checkpoints where projeto = pr;
  p_posicao := greatest(1, least(coalesce(p_posicao, n), n));
  with r as (select id, row_number() over (order by ordem, id) as rn from public.checkpoints where projeto = pr and id <> p_id)
  update public.checkpoints c set ordem = case when r.rn >= p_posicao then r.rn + 1 else r.rn end
    from r where c.id = r.id and c.ordem is distinct from (case when r.rn >= p_posicao then r.rn + 1 else r.rn end);
  update public.checkpoints set ordem = p_posicao where id = p_id and ordem is distinct from p_posicao;
end $$;
revoke execute on function public.inserir_checkpoint(text, text, text, int), public.mover_checkpoint(bigint, int) from public, anon;
grant execute on function public.inserir_checkpoint(text, text, text, int), public.mover_checkpoint(bigint, int) to authenticated;

-- ---------------------------------------------------------------- documentos de cada projeto
-- informativo = descreve o projeto (especificações, planos); adicional = conhecimento extra (ex.: desenhos de obras).
-- O ficheiro fica no armazenamento privado "documentos" (Supabase Storage), no caminho <projeto>/<tipo>/<nome>.
create table public.documentos (
  id bigint generated always as identity primary key,
  projeto text not null references public.projetos (id) on delete cascade,
  tipo text not null check (tipo in ('informativo', 'adicional')),
  titulo text not null check (char_length(titulo) between 1 and 200),
  descricao text not null default '' check (char_length(descricao) <= 2000),
  caminho text not null check (caminho ~ '^[a-z_]+/(informativo|adicional)/[^/]+$'),
  nome_ficheiro text not null check (char_length(nome_ficheiro) between 1 and 300),
  tamanho bigint not null default 0,
  mime text not null default '',
  criado_por uuid default auth.uid(),
  criado_por_nome text not null default '' check (char_length(criado_por_nome) <= 120),
  criado_em timestamptz not null default now()
);
create index documentos_projeto_idx on public.documentos (projeto, tipo);
alter table public.documentos enable row level security;
create policy "Ver" on public.documentos for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.documentos for insert to authenticated with check ((select public.pode_editar()));
create policy "Editar" on public.documentos for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));
create policy "Apagar" on public.documentos for delete to authenticated using ((select public.pode_editar()));

alter table public.notificacoes drop constraint notificacoes_tipo_check;
alter table public.notificacoes add constraint notificacoes_tipo_check check (tipo in ('tarefa_nova', 'tarefa_atribuida',
  'tarefa_estado', 'tarefa_concluida', 'checkpoint_novo', 'checkpoint_estado', 'checkpoint_concluido', 'decisao_nova',
  'decisao_tomada', 'documento_novo'));

create or replace function public.documentos_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
  else
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
    new.caminho := old.caminho;
  end if;
  return new;
end $$;
create trigger documentos_antes before insert or update on public.documentos
  for each row execute function public.documentos_antes();
create or replace function public.documentos_depois() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  perform public.notificar(new.projeto, 'documento_novo', public.nome_atual() || ' acrescentou o documento «' || new.titulo || '»'
    || case when new.tipo = 'informativo' then ' (informativo)' else ' (adicional)' end, 'documento', new.id);
  return null;
end $$;
create trigger documentos_depois after insert on public.documentos
  for each row execute function public.documentos_depois();
revoke execute on function public.documentos_antes(), public.documentos_depois() from public, anon, authenticated;

-- o pop-up "Novo" também para documentos acrescentados por outra pessoa
alter table public.vistos drop constraint vistos_tipo_check;
alter table public.vistos add constraint vistos_tipo_check check (tipo in ('checkpoint', 'tarefa', 'decisao', 'documento'));

-- armazenamento privado: só quem vê o Design abre (por URL assinado e temporário); só quem edita carrega ou apaga
insert into storage.buckets (id, name, public, file_size_limit)
  values ('documentos', 'documentos', false, 52428800)
  on conflict (id) do nothing;
create policy "Documentos: ver" on storage.objects for select to authenticated
  using (bucket_id = 'documentos' and (select public.pode_ver()));
create policy "Documentos: carregar" on storage.objects for insert to authenticated
  with check (bucket_id = 'documentos' and (select public.pode_editar()));
create policy "Documentos: mudar" on storage.objects for update to authenticated
  using (bucket_id = 'documentos' and (select public.pode_editar())) with check (bucket_id = 'documentos' and (select public.pode_editar()));
create policy "Documentos: apagar" on storage.objects for delete to authenticated
  using (bucket_id = 'documentos' and (select public.pode_editar()));

-- ---------------------------------------------------------------- atualização em direto (Supabase Realtime)
-- Cada mudança chega logo a quem tem o hub aberto (as regras RLS de "Ver" aplicam-se também aqui).
alter publication supabase_realtime add table public.checkpoints, public.tarefas, public.decisoes,
  public.decisoes_opcoes, public.documentos, public.notificacoes;
