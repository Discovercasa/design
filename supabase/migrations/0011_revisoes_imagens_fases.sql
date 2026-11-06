-- Hub (2026-11-07): "anexar imagens às descrições de tarefas/checkpoints"; "adicionar uma opção de decisão sem ser as que
-- são apresentadas"; nas tarefas de teste ou revisão "uma lista onde podemos adicionar notas sobre essas revisões/testes"
-- (bugs, coisas a mudar, coisas a fazer); nas obras "clicar no círculo que corresponde ao estado atual da obra … tanto
-- isso como regredir"; abas por ordem Início · Gerador de documentos · Builder · Orçamentação · Build Your House · Step
-- Inside. Do documento de hierarquia: um "critério de saída" opcional em cada checkpoint.

-- ---------------------------------------------------------------- ordem dos projetos (abas e listas)
update public.projetos set ordem = case id when 'gerador' then 1 when 'builder' then 2 when 'orcamentacao' then 3
  when 'build_your_house' then 4 when 'plataforma_cliente' then 5 else ordem end;

-- ---------------------------------------------------------------- critério de saída e tarefas de teste/revisão
-- critério de saída: o que tem de ser verdade para o checkpoint se dar como concluído (opcional, só texto)
alter table public.checkpoints add column criterio_saida text not null default '' check (char_length(criterio_saida) <= 2000);
-- tarefa de teste ou revisão: mostra a lista de notas (bugs, a mudar, a fazer)
alter table public.tarefas add column revisao boolean not null default false;

-- quem só vê e é responsável muda apenas o estado (agora também não muda a marca de revisão)
create or replace function public.tarefas_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
    if new.estado = 'concluida' and new.concluida_em is null then new.concluida_em := current_date; end if;
  else
    if not public.pode_editar() then
      new.titulo := old.titulo; new.descricao := old.descricao; new.checkpoint_id := old.checkpoint_id;
      new.responsavel_id := old.responsavel_id; new.responsavel_nome := old.responsavel_nome;
      new.app_sugerida := old.app_sugerida; new.custo := old.custo; new.ordem := old.ordem; new.revisao := old.revisao;
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

-- ---------------------------------------------------------------- notas de teste/revisão
create table public.tarefas_notas (
  id bigint generated always as identity primary key,
  tarefa_id bigint not null references public.tarefas (id) on delete cascade,
  projeto text not null references public.projetos (id) on delete cascade,     -- copiado da tarefa (trigger)
  tipo text not null default 'nota' check (tipo in ('bug', 'mudar', 'fazer', 'nota')),
  texto text not null check (char_length(texto) between 1 and 4000),
  resolvida boolean not null default false,
  resolvida_por_nome text not null default '',
  resolvida_em date,
  tarefa_criada_id bigint references public.tarefas (id) on delete set null,  -- "Passar a tarefa"
  autor_id uuid default auth.uid(),
  autor_nome text not null default '' check (char_length(autor_nome) <= 120),
  criado_em timestamptz not null default now()
);
create index tarefas_notas_tarefa_idx on public.tarefas_notas (tarefa_id, criado_em);
create index tarefas_notas_criada_idx on public.tarefas_notas (tarefa_criada_id);
alter table public.tarefas_notas enable row level security;
create policy "Ver" on public.tarefas_notas for select to authenticated using ((select public.pode_ver()));
-- toda a equipa escreve notas (também quem só vê); resolve e apaga quem edita ou quem a escreveu
create policy "Criar" on public.tarefas_notas for insert to authenticated
  with check ((select public.pode_ver()) and autor_id = (select auth.uid()));
create policy "Editar" on public.tarefas_notas for update to authenticated
  using ((select public.pode_editar()) or autor_id = (select auth.uid()))
  with check ((select public.pode_editar()) or autor_id = (select auth.uid()));
create policy "Apagar" on public.tarefas_notas for delete to authenticated
  using ((select public.pode_editar()) or autor_id = (select auth.uid()));

create or replace function public.tarefas_notas_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.autor_id := (select auth.uid()); new.autor_nome := public.nome_atual(); new.criado_em := now();
    end if;
  else
    new.autor_id := old.autor_id; new.autor_nome := old.autor_nome; new.criado_em := old.criado_em; new.tarefa_id := old.tarefa_id;
  end if;
  select t.projeto into new.projeto from public.tarefas t where t.id = new.tarefa_id;
  if new.resolvida and (tg_op = 'INSERT' or not old.resolvida) then
    if (select auth.uid()) is not null then new.resolvida_por_nome := public.nome_atual(); end if;
    new.resolvida_em := coalesce(new.resolvida_em, current_date);
  elsif not new.resolvida then
    new.resolvida_por_nome := ''; new.resolvida_em := null;
  end if;
  return new;
end $$;
create trigger tarefas_notas_antes before insert or update on public.tarefas_notas
  for each row execute function public.tarefas_notas_antes();

create or replace function public.tarefas_notas_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare t text := (select '«' || titulo || '»' from public.tarefas where id = new.tarefa_id);
begin
  if tg_op = 'INSERT' then
    perform public.notificar(new.projeto, 'nota_nova', public.nome_atual() || ' acrescentou '
      || case new.tipo when 'bug' then 'um bug' when 'mudar' then 'uma mudança' when 'fazer' then 'uma coisa a fazer' else 'uma nota' end
      || ' em ' || t || ': ' || left(new.texto, 120), 'tarefa', new.tarefa_id);
  elsif new.resolvida and not old.resolvida then
    perform public.notificar(new.projeto, 'nota_resolvida', public.nome_atual() || ' resolveu em ' || t || ': ' || left(new.texto, 120),
      'tarefa', new.tarefa_id);
  end if;
  return null;
end $$;
create trigger tarefas_notas_depois after insert or update on public.tarefas_notas
  for each row execute function public.tarefas_notas_depois();

-- ---------------------------------------------------------------- imagens anexadas (checkpoints, tarefas e notas)
-- os ficheiros ficam no armazenamento privado "anexos": <alvo>/<nome> e a miniatura em miniaturas/<nome>
create table public.anexos (
  id bigint generated always as identity primary key,
  alvo text not null check (alvo in ('checkpoint', 'tarefa', 'nota')),
  ref_id bigint not null,
  projeto text references public.projetos (id) on delete cascade,
  caminho text not null check (caminho ~ '^(checkpoint|tarefa|nota)/[^/]+$'),
  miniatura text check (miniatura ~ '^miniaturas/[^/]+$'),
  nome_ficheiro text not null check (char_length(nome_ficheiro) between 1 and 300),
  mime text not null default '',
  tamanho bigint not null default 0,
  largura int, altura int,
  ordem int not null default 0,
  criado_por uuid default auth.uid(),
  criado_por_nome text not null default '' check (char_length(criado_por_nome) <= 120),
  criado_em timestamptz not null default now()
);
create index anexos_alvo_idx on public.anexos (alvo, ref_id, ordem);
create index anexos_projeto_idx on public.anexos (projeto);
alter table public.anexos enable row level security;
create policy "Ver" on public.anexos for select to authenticated using ((select public.pode_ver()));
-- quem edita anexa a checkpoints e tarefas; nas notas anexa também quem escreveu a nota
create policy "Criar" on public.anexos for insert to authenticated with check (
  (select public.pode_editar()) or ((select public.pode_ver()) and alvo = 'nota'
    and exists (select 1 from public.tarefas_notas n where n.id = ref_id and n.autor_id = (select auth.uid()))));
create policy "Editar" on public.anexos for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));
create policy "Apagar" on public.anexos for delete to authenticated
  using ((select public.pode_editar()) or criado_por = (select auth.uid()));

create or replace function public.anexos_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
    new.projeto := case new.alvo
      when 'checkpoint' then (select projeto from public.checkpoints where id = new.ref_id)
      when 'tarefa' then (select projeto from public.tarefas where id = new.ref_id)
      else (select projeto from public.tarefas_notas where id = new.ref_id) end;
    if new.projeto is null then raise exception 'O % % não existe.', new.alvo, new.ref_id; end if;
  else
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
    new.alvo := old.alvo; new.ref_id := old.ref_id; new.caminho := old.caminho; new.miniatura := old.miniatura; new.projeto := old.projeto;
  end if;
  return new;
end $$;
create trigger anexos_antes before insert or update on public.anexos for each row execute function public.anexos_antes();

-- apagar um checkpoint, uma tarefa ou uma nota apaga as linhas das suas imagens (os ficheiros apaga-os o hub)
create or replace function public.anexos_orfaos() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  delete from public.anexos where alvo = tg_argv[0] and ref_id = old.id;
  return null;
end $$;
create trigger checkpoints_anexos after delete on public.checkpoints for each row execute function public.anexos_orfaos('checkpoint');
create trigger tarefas_anexos after delete on public.tarefas for each row execute function public.anexos_orfaos('tarefa');
create trigger tarefas_notas_anexos after delete on public.tarefas_notas for each row execute function public.anexos_orfaos('nota');

insert into storage.buckets (id, name, public, file_size_limit)
  values ('anexos', 'anexos', false, 52428800)
  on conflict (id) do nothing;
create policy "Anexos: ver" on storage.objects for select to authenticated
  using (bucket_id = 'anexos' and (select public.pode_ver()));
create policy "Anexos: carregar" on storage.objects for insert to authenticated
  with check (bucket_id = 'anexos' and ((select public.pode_editar())
    or ((select public.pode_ver()) and (name like 'nota/%' or name like 'miniaturas/nota-%'))));
create policy "Anexos: apagar" on storage.objects for delete to authenticated
  using (bucket_id = 'anexos' and ((select public.pode_editar()) or owner_id = (select auth.uid()::text)));

-- ---------------------------------------------------------------- acrescentar uma opção a uma decisão em aberto
create or replace function public.acrescentar_opcao(p_decisao bigint, p_titulo text, p_descricao text, p_vantagens text,
                                                    p_desvantagens text, p_custo text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare d public.decisoes; i bigint;
begin
  if not public.pode_editar() then raise exception 'Sem permissão para editar.'; end if;
  select * into d from public.decisoes where id = p_decisao;
  if d.id is null then raise exception 'Decisão inexistente.'; end if;
  if d.estado <> 'aberta' then raise exception 'Reabre a decisão para lhe acrescentar opções.'; end if;
  insert into public.decisoes_opcoes (decisao_id, titulo, descricao, vantagens, desvantagens, custo, ordem)
    values (p_decisao, trim(p_titulo), coalesce(p_descricao, ''), coalesce(p_vantagens, ''), coalesce(p_desvantagens, ''),
            coalesce(p_custo, ''), (select coalesce(max(o.ordem), 0) + 1 from public.decisoes_opcoes o where o.decisao_id = p_decisao))
    returning id into i;
  perform public.notificar(d.projeto, 'decisao_opcao', public.nome_atual() || ' acrescentou a opção «' || trim(p_titulo)
    || '» à decisão «' || d.pergunta || '»', 'decisao', d.id);
  return i;
end $$;
revoke execute on function public.acrescentar_opcao(bigint, text, text, text, text, text) from public, anon;
grant execute on function public.acrescentar_opcao(bigint, text, text, text, text, text) to authenticated;

-- ---------------------------------------------------------------- fase atual de uma obra num só passo
-- o hub manda o estado de cada fase (a clicada em curso, as anteriores concluídas, as seguintes previstas; ou o estado
-- anterior, para desfazer). Uma só notificação em vez de uma por fase.
create or replace function public.obras_fases_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
    if new.estado = 'concluida' and new.concluida_em is null then new.concluida_em := current_date; end if;
  else
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
    new.obra_id := old.obra_id;
    if new.estado is distinct from old.estado then
      -- ao concluir fica o dia de hoje, salvo quando se repõe o dia antigo (desfazer)
      new.concluida_em := case when new.estado = 'concluida' then coalesce(new.concluida_em, current_date) end;
    end if;
  end if;
  if new.fotos = 'tiradas' and (tg_op = 'INSERT' or old.fotos <> 'tiradas') and new.fotos_em is null then new.fotos_em := current_date; end if;
  if new.fotos <> 'tiradas' then new.fotos_em := null; end if;
  if new.fotos = 'por_tirar' then new.visita_em := null; end if;
  return new;
end $$;

create or replace function public.obras_fases_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare o text := (select nome from public.obras where id = new.obra_id); f text := '«' || new.nome || '»';
begin
  if current_setting('hub.fases_em_lote', true) = '1' then return null; end if;   -- definir_fases avisa uma só vez
  if tg_op = 'INSERT' then
    perform public.notificar(null, 'fase_nova', public.nome_atual() || ' acrescentou a fase ' || f || ' à obra ' || o, 'obra', new.obra_id);
  elsif new.estado is distinct from old.estado then
    perform public.notificar(null, 'fase_estado', public.nome_atual() || ' marcou ' || o || ' · ' || new.nome || ' como '
      || case new.estado when 'concluida' then 'concluída' when 'em_curso' then 'em curso' else 'prevista' end, 'obra', new.obra_id);
  elsif new.fotos is distinct from old.fotos and new.fotos <> 'por_tirar' then
    perform public.notificar(null, 'fase_estado', public.nome_atual() || case when new.fotos = 'tiradas'
      then ' tirou as fotos de ' || o || ' · ' || new.nome
      else ' marcou a visita para fotos a ' || o || ' · ' || new.nome || coalesce(' (' || to_char(new.visita_em, 'DD/MM') || ')', '') end, 'obra', new.obra_id);
  end if;
  return null;
end $$;

create or replace function public.definir_fases(p_obra bigint, p_estados jsonb)
returns void language plpgsql security definer set search_path = '' as $$
declare o text; e jsonb; n int; atual text;
begin
  if not public.pode_editar() then raise exception 'Sem permissão para editar.'; end if;
  select nome into o from public.obras where id = p_obra;
  if o is null then raise exception 'Obra inexistente.'; end if;
  perform set_config('hub.fases_em_lote', '1', true);
  for e in select * from jsonb_array_elements(p_estados) loop
    update public.obras_fases f set estado = e ->> 'estado',
      concluida_em = case when e ->> 'estado' = 'concluida' then coalesce((e ->> 'concluida_em')::date, f.concluida_em) end
      where f.id = (e ->> 'id')::bigint and f.obra_id = p_obra;
    get diagnostics n = row_count;
    if n = 0 then raise exception 'A fase % não é desta obra.', e ->> 'id'; end if;
  end loop;
  perform set_config('hub.fases_em_lote', '', true);
  select f.nome into atual from public.obras_fases f where f.obra_id = p_obra and f.estado = 'em_curso' order by f.ordem limit 1;
  perform public.notificar(null, 'fase_estado', public.nome_atual() || case
      when atual is not null then ' passou a obra ' || o || ' para a fase «' || atual || '»'
      when not exists (select 1 from public.obras_fases f where f.obra_id = p_obra and f.estado <> 'concluida') then ' deu todas as fases da obra ' || o || ' como concluídas'
      else ' atualizou as fases da obra ' || o end, 'obra', p_obra);
end $$;
revoke execute on function public.definir_fases(bigint, jsonb) from public, anon;
grant execute on function public.definir_fases(bigint, jsonb) to authenticated;

-- ---------------------------------------------------------------- notificações e em direto
alter table public.notificacoes drop constraint notificacoes_tipo_check;
alter table public.notificacoes add constraint notificacoes_tipo_check check (tipo in ('tarefa_nova', 'tarefa_atribuida',
  'tarefa_estado', 'tarefa_concluida', 'checkpoint_novo', 'checkpoint_estado', 'checkpoint_concluido', 'decisao_nova',
  'decisao_tomada', 'decisao_opcao', 'documento_novo', 'post_novo', 'post_estado', 'post_aprovacao', 'post_comentario',
  'obra_nova', 'fase_nova', 'fase_estado', 'nota_nova', 'nota_resolvida'));

revoke execute on function public.tarefas_notas_antes(), public.tarefas_notas_depois(), public.anexos_antes(),
  public.anexos_orfaos() from public, anon, authenticated;

alter publication supabase_realtime add table public.tarefas_notas, public.anexos;
