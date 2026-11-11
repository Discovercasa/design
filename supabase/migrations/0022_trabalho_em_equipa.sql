-- Design — trabalho em equipa (2026-11-11). O utilizador: «O hub neste momento está ótimo mas não está muito prático
-- para o trabalho em equipa … Imagina que és o manager e precisas que os teu colaboradores te ajudem ou até deixem uma
-- tarefa praticamente concluída só à espera da tua aprovação.»
--   1. O chat geral sai («vamos implementar de outra forma e não como chat geral»): a conversa passa para dentro de cada
--      tarefa ou checkpoint (tabela atividade), com texto, ficheiros, imagens/vídeos e áudios (armazenamento "chat").
--   2. Ponto de situação por tópicos em cada tarefa e checkpoint; pedir um ponto de situação; pedir aprovação (estado
--      novo «por_aprovar») e aprovar ou devolver (só quem edita).
--   3. Marcar pessoas nas tarefas (marcacoes): a pessoa vê-as num pop-up ao abrir o hub.
--   4. Críticas e comentários sobre cada projeto («não gostou de alguma coisa … algo correu mal … não funcionou»).
--   5. Notificações só para o que tem impacto (checkpoint concluído, decisão aberta ou tomada, crítica, tarefa concluída,
--      pedido de aprovação de um post) e as pessoais (marcado, atribuída, pedido de ponto de situação ou de aprovação,
--      mensagem numa tarefa tua); tudo o resto vai para o Log (registo), que todos veem e que avisa ao abrir o hub.

-- ------------------------------------------------------------------ 1. sai o chat geral (0018–0020)
drop policy if exists "Chat: ver" on storage.objects;
drop policy if exists "Chat: carregar" on storage.objects;
drop policy if exists "Chat: apagar" on storage.objects;
drop table if exists public.mensagens, public.conversas_membros, public.conversas cascade;
drop function if exists public.abrir_conversa(uuid[], text);
drop function if exists public.e_membro_caminho(text);
drop function if exists public.e_membro(bigint);
drop function if exists public.mensagens_antes();
drop function if exists public.mensagens_depois();
-- o armazenamento "chat" fica, agora para os anexos das conversas das tarefas e das críticas (quem vê o Design vê-os)
create policy "Chat: ver" on storage.objects for select to authenticated using (bucket_id = 'chat' and (select public.pode_ver()));
create policy "Chat: carregar" on storage.objects for insert to authenticated with check (bucket_id = 'chat' and (select public.pode_ver()));
create policy "Chat: apagar" on storage.objects for delete to authenticated
  using (bucket_id = 'chat' and ((select public.pode_editar()) or owner_id = (select auth.uid()::text)));

-- ------------------------------------------------------------------ 5. o Log e as notificações com impacto
create table public.registo (
  id bigint generated always as identity primary key,
  projeto text references public.projetos (id) on delete set null,
  tipo text not null,
  texto text not null check (char_length(texto) <= 1000),
  detalhe text not null default '' check (char_length(detalhe) <= 8000),   -- o Claude escreve aqui o pormenor
  ator_id uuid,
  ator_nome text not null default '',
  ref_tipo text,
  ref_id bigint,
  criada_em timestamptz not null default now()
);
create index registo_criada_idx on public.registo (criada_em desc);
alter table public.registo enable row level security;
create policy "Ver" on public.registo for select to authenticated using ((select public.pode_ver()));
-- (sem regras de escrita: entra pelas funções abaixo e pelo Claude)

alter table public.perfis
  add column registo_visto_em timestamptz not null default now(),   -- os avisos do Log ao abrir: o que veio depois disto
  add column avisos_registo boolean not null default true;          -- cada pessoa desliga-os nas Definições

create or replace function public.registar(p_projeto text, p_tipo text, p_texto text, p_ref_tipo text, p_ref_id bigint,
                                           p_detalhe text default '') returns void
language sql security definer set search_path = '' as $$
  insert into public.registo (projeto, tipo, texto, detalhe, ator_id, ator_nome, ref_tipo, ref_id)
  values (p_projeto, p_tipo, left(p_texto, 1000), left(coalesce(p_detalhe, ''), 8000), (select auth.uid()),
          case when (select auth.uid()) is null then 'Claude' else public.nome_atual() end, p_ref_tipo, p_ref_id)
$$;

-- sem destinatário: vai para o Log e, se tiver impacto, notifica a equipa; com destinatário: só a notificação pessoal
create or replace function public.notificar(p_projeto text, p_tipo text, p_texto text, p_ref_tipo text, p_ref_id bigint,
                                            p_dest uuid default null) returns void
language plpgsql security definer set search_path = '' as $$
declare eu uuid := (select auth.uid());
begin
  if eu is null then return; end if;   -- migrações e o Claude escrevem à parte
  if p_dest is null then
    perform public.registar(p_projeto, p_tipo, p_texto, p_ref_tipo, p_ref_id);
    if p_tipo not in ('checkpoint_concluido', 'decisao_nova', 'decisao_tomada', 'tarefa_concluida', 'critica_nova')
       and not (p_tipo = 'post_estado' and p_texto like '%pediu aprovação%') then
      return;
    end if;
  elsif p_dest = eu then
    return;   -- nunca a mim próprio
  end if;
  insert into public.notificacoes (projeto, tipo, texto, ator_id, ator_nome, destinatario_id, ref_tipo, ref_id)
  values (p_projeto, p_tipo, left(p_texto, 600), eu, public.nome_atual(), p_dest, p_ref_tipo, p_ref_id);
end $$;

alter table public.notificacoes drop constraint notificacoes_tipo_check;
alter table public.notificacoes add constraint notificacoes_tipo_check check (tipo in (
  'tarefa_nova', 'tarefa_atribuida', 'tarefa_estado', 'tarefa_concluida', 'checkpoint_novo', 'checkpoint_estado',
  'checkpoint_concluido', 'decisao_nova', 'decisao_tomada', 'decisao_opcao', 'documento_novo', 'post_novo', 'post_estado',
  'post_aprovacao', 'post_comentario', 'obra_nova', 'fase_nova', 'fase_estado', 'nota_nova', 'nota_resolvida',
  'sugestao_estado', 'chat', 'marcado', 'pedido_situacao', 'situacao', 'pedido_aprovacao', 'aprovada', 'devolvida',
  'mensagem', 'critica_nova'));

-- ------------------------------------------------------------------ 2. ponto de situação e aprovação
alter table public.tarefas
  add column situacao text not null default '' check (char_length(situacao) <= 4000),   -- um tópico por linha
  add column situacao_em timestamptz,
  add column situacao_por_nome text not null default '' check (char_length(situacao_por_nome) <= 120);
alter table public.checkpoints
  add column situacao text not null default '' check (char_length(situacao) <= 4000),
  add column situacao_em timestamptz,
  add column situacao_por_nome text not null default '' check (char_length(situacao_por_nome) <= 120);
alter table public.tarefas drop constraint tarefas_estado_check;
alter table public.tarefas add constraint tarefas_estado_check check (estado in ('por_fazer', 'em_curso', 'bloqueada', 'por_aprovar', 'concluida'));

create or replace function public.rotulo_estado(e text) returns text language sql immutable set search_path = '' as $$
  select case e when 'por_fazer' then 'Por fazer' when 'em_curso' then 'Em curso' when 'bloqueada' then 'Bloqueada'
                when 'por_aprovar' then 'À espera de aprovação' when 'concluida' then 'Concluída' when 'concluido' then 'Concluído' else e end
$$;

-- a tarefa atribuída avisa só a pessoa (antes avisava toda a equipa)
create or replace function public.tarefas_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare t text := '«' || new.titulo || '»'; quem text := public.nome_atual();
begin
  if tg_op = 'INSERT' then
    perform public.notificar(new.projeto, 'tarefa_nova', quem || ' acrescentou a tarefa ' || t, 'tarefa', new.id);
  end if;
  if new.responsavel_id is not null and (tg_op = 'INSERT' or new.responsavel_id is distinct from old.responsavel_id) then
    perform public.registar(new.projeto, 'tarefa_atribuida', quem || ' atribuiu a tarefa ' || t || ' a ' || new.responsavel_nome, 'tarefa', new.id);
    perform public.notificar(new.projeto, 'tarefa_atribuida', quem || ' atribuiu-te a tarefa ' || t, 'tarefa', new.id, new.responsavel_id);
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

-- ------------------------------------------------------------------ 3. marcar pessoas numa tarefa
create table public.marcacoes (
  tarefa_id bigint not null references public.tarefas (id) on delete cascade,
  utilizador_id uuid not null references auth.users (id) on delete cascade,
  marcado_por uuid default auth.uid() references auth.users (id) on delete set null,
  marcado_por_nome text not null default '' check (char_length(marcado_por_nome) <= 120),
  criada_em timestamptz not null default now(),
  vista_em timestamptz,   -- a pessoa já a viu (o pop-up ao abrir o hub mostra as que ainda não viu)
  primary key (tarefa_id, utilizador_id)
);
create index marcacoes_utilizador_idx on public.marcacoes (utilizador_id);
create index marcacoes_marcado_por_idx on public.marcacoes (marcado_por);
alter table public.marcacoes enable row level security;
create policy "Ver" on public.marcacoes for select to authenticated using ((select public.pode_ver()));
create policy "Marcar" on public.marcacoes for insert to authenticated
  with check ((select public.pode_ver()) and marcado_por = (select auth.uid()));
create policy "Desmarcar" on public.marcacoes for delete to authenticated using ((select public.pode_ver()));
create policy "Vista" on public.marcacoes for update to authenticated   -- só a minha e só vista_em (grant abaixo)
  using ((select public.pode_ver()) and utilizador_id = (select auth.uid()))
  with check ((select public.pode_ver()) and utilizador_id = (select auth.uid()));
revoke update on public.marcacoes from anon, authenticated;
grant update (vista_em) on public.marcacoes to authenticated;

create or replace function public.marcacoes_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if not exists (select 1 from public.perfis p where p.id = new.utilizador_id) then raise exception 'Só se podem marcar pessoas do hub.'; end if;
  new.marcado_por := (select auth.uid());
  new.marcado_por_nome := case when (select auth.uid()) is null then coalesce(nullif(new.marcado_por_nome, ''), 'Claude') else public.nome_atual() end;
  new.criada_em := now(); new.vista_em := null;
  return new;
end $$;
create trigger marcacoes_antes before insert on public.marcacoes for each row execute function public.marcacoes_antes();

create or replace function public.marcacoes_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare t public.tarefas; quem text := public.nome_atual(); nome text;
begin
  select * into t from public.tarefas where id = new.tarefa_id;
  select coalesce(nullif(p.nome, ''), 'Alguém') into nome from public.perfis p where p.id = new.utilizador_id;
  perform public.registar(t.projeto, 'marcado', quem || ' marcou ' || nome || ' na tarefa «' || t.titulo || '»', 'tarefa', t.id);
  perform public.notificar(t.projeto, 'marcado', quem || ' marcou-te na tarefa «' || t.titulo || '»', 'tarefa', t.id, new.utilizador_id);
  return null;
end $$;
create trigger marcacoes_depois after insert on public.marcacoes for each row execute function public.marcacoes_depois();

-- ------------------------------------------------------------------ 1. a conversa de cada tarefa ou checkpoint
create table public.atividade (
  id bigint generated always as identity primary key,
  alvo text not null check (alvo in ('tarefa', 'checkpoint')),
  ref_id bigint not null,
  projeto text references public.projetos (id) on delete cascade,
  tipo text not null default 'mensagem' check (tipo in ('mensagem', 'sugestao', 'pedido_situacao', 'situacao',
    'pedido_aprovacao', 'aprovada', 'devolvida')),
  autor_id uuid default auth.uid() references auth.users (id) on delete set null,   -- null: o Claude
  autor_nome text not null default '' check (char_length(autor_nome) <= 120),
  texto text not null default '' check (char_length(texto) <= 4000),
  -- [{caminho, nome, mime, tamanho, tipo: imagem|video|audio|ficheiro, miniatura?, largura?, altura?, duracao?}]
  anexos jsonb not null default '[]'::jsonb,
  criada_em timestamptz not null default now(),
  check (char_length(btrim(texto)) > 0 or jsonb_array_length(anexos) > 0)
);
create index atividade_ref_idx on public.atividade (alvo, ref_id, criada_em);
create index atividade_autor_idx on public.atividade (autor_id);
alter table public.atividade enable row level security;
create policy "Ver" on public.atividade for select to authenticated using ((select public.pode_ver()));
create policy "Escrever" on public.atividade for insert to authenticated
  with check ((select public.pode_ver()) and autor_id = (select auth.uid()) and tipo in ('mensagem', 'sugestao'));
create policy "Apagar" on public.atividade for delete to authenticated
  using ((select public.pode_editar()) or ((select public.pode_ver()) and autor_id = (select auth.uid()) and tipo in ('mensagem', 'sugestao')));

create or replace function public.atividade_antes() returns trigger language plpgsql security definer set search_path = '' as $$
declare a jsonb;
begin
  new.criada_em := clock_timestamp();
  if (select auth.uid()) is null then
    new.autor_id := null; new.autor_nome := coalesce(nullif(btrim(new.autor_nome), ''), 'Claude');
  else
    new.autor_id := (select auth.uid()); new.autor_nome := public.nome_atual();
  end if;
  if new.alvo = 'tarefa' then select projeto into new.projeto from public.tarefas where id = new.ref_id;
  else select projeto into new.projeto from public.checkpoints where id = new.ref_id; end if;
  if new.projeto is null then raise exception 'A % % não existe.', new.alvo, new.ref_id; end if;
  if jsonb_typeof(new.anexos) <> 'array' or jsonb_array_length(new.anexos) > 10 then raise exception 'Até 10 anexos por mensagem.'; end if;
  for a in select value from jsonb_array_elements(new.anexos) loop
    if coalesce(a ->> 'caminho', '') not like new.alvo || '-' || new.ref_id || '/%'
       or coalesce(a ->> 'tipo', '') not in ('imagem', 'video', 'audio', 'ficheiro') then
      raise exception 'Anexo inválido.';
    end if;
  end loop;
  return new;
end $$;
create trigger atividade_antes before insert on public.atividade for each row execute function public.atividade_antes();

-- quem acompanha uma tarefa: o responsável e as pessoas marcadas
create or replace function public.pessoas_da_tarefa(p_tarefa bigint) returns setof uuid
language sql stable security definer set search_path = '' as $$
  select responsavel_id from public.tarefas where id = p_tarefa and responsavel_id is not null
  union select utilizador_id from public.marcacoes where tarefa_id = p_tarefa
$$;
-- quem pode editar o Design (aprova as tarefas)
create or replace function public.editores() returns setof uuid
language sql stable security definer set search_path = '' as $$
  select u.id from auth.users u join public.perfis p on p.id = u.id where u.raw_app_meta_data ->> 'nivel' = 'editar'
$$;

create or replace function public.atividade_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare titulo text; quem text := new.autor_nome; d uuid; texto text;
begin
  if new.tipo not in ('mensagem', 'sugestao') then return null; end if;   -- os outros tipos avisam nas suas funções
  if new.alvo = 'tarefa' then select '«' || t.titulo || '»' into titulo from public.tarefas t where t.id = new.ref_id;
  else select '«' || c.titulo || '»' into titulo from public.checkpoints c where c.id = new.ref_id; end if;
  texto := quem || case when new.tipo = 'sugestao' then ' sugeriu em ' else ' escreveu em ' end || titulo
    || coalesce(': ' || nullif(left(new.texto, 120), ''), ' (anexo)');
  perform public.registar(new.projeto, new.tipo, texto, new.alvo, new.ref_id);
  if new.alvo = 'tarefa' then
    for d in select * from public.pessoas_da_tarefa(new.ref_id) loop
      perform public.notificar(new.projeto, 'mensagem', texto, 'tarefa', new.ref_id, d);
    end loop;
  end if;
  return null;
end $$;
create trigger atividade_depois after insert on public.atividade for each row execute function public.atividade_depois();

-- a tarefa ou o checkpoint apagado leva a sua conversa
create or replace function public.atividade_orfa() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  delete from public.atividade where alvo = tg_argv[0] and ref_id = old.id;
  return null;
end $$;
create trigger atividade_orfa after delete on public.tarefas for each row execute function public.atividade_orfa('tarefa');
create trigger atividade_orfa after delete on public.checkpoints for each row execute function public.atividade_orfa('checkpoint');

-- o ponto de situação (um tópico por linha): quem vê o Design pode escrevê-lo; avisa quem o tinha pedido
create or replace function public.dar_situacao(p_alvo text, p_ref bigint, p_texto text) returns void
language plpgsql security definer set search_path = '' as $$
declare txt text := left(btrim(coalesce(p_texto, '')), 4000); proj text; tit text; desde timestamptz; d uuid;
begin
  if (select auth.uid()) is null or not public.pode_ver() then raise exception 'Sem acesso ao Design.'; end if;
  if p_alvo = 'tarefa' then
    select projeto, '«' || titulo || '»', situacao_em into proj, tit, desde from public.tarefas where id = p_ref;
    update public.tarefas set situacao = txt, situacao_em = now(), situacao_por_nome = public.nome_atual() where id = p_ref;
  elsif p_alvo = 'checkpoint' then
    select projeto, '«' || titulo || '»', situacao_em into proj, tit, desde from public.checkpoints where id = p_ref;
    update public.checkpoints set situacao = txt, situacao_em = now(), situacao_por_nome = public.nome_atual() where id = p_ref;
  else raise exception 'Alvo inválido.'; end if;
  if proj is null then raise exception 'Não existe.'; end if;
  if txt <> '' then insert into public.atividade (alvo, ref_id, tipo, texto) values (p_alvo, p_ref, 'situacao', txt); end if;
  perform public.registar(proj, 'situacao', public.nome_atual() || ' atualizou o ponto de situação de ' || tit, p_alvo, p_ref, txt);
  for d in select distinct a.autor_id from public.atividade a where a.alvo = p_alvo and a.ref_id = p_ref and a.tipo = 'pedido_situacao'
             and a.autor_id is not null and a.criada_em > coalesce(desde, '-infinity'::timestamptz) loop
    perform public.notificar(proj, 'situacao', public.nome_atual() || ' respondeu ao teu pedido: ponto de situação de ' || tit, p_alvo, p_ref, d);
  end loop;
end $$;

create or replace function public.pedir_situacao(p_alvo text, p_ref bigint, p_texto text default '') returns void
language plpgsql security definer set search_path = '' as $$
declare proj text; tit text; d uuid; n int := 0;
  txt text := coalesce(nullif(left(btrim(coalesce(p_texto, '')), 4000), ''), 'Podes atualizar o ponto de situação?');
begin
  if (select auth.uid()) is null or not public.pode_ver() then raise exception 'Sem acesso ao Design.'; end if;
  if p_alvo = 'tarefa' then select projeto, '«' || titulo || '»' into proj, tit from public.tarefas where id = p_ref;
  elsif p_alvo = 'checkpoint' then select projeto, '«' || titulo || '»' into proj, tit from public.checkpoints where id = p_ref;
  else raise exception 'Alvo inválido.'; end if;
  if proj is null then raise exception 'Não existe.'; end if;
  insert into public.atividade (alvo, ref_id, tipo, texto) values (p_alvo, p_ref, 'pedido_situacao', txt);
  perform public.registar(proj, 'pedido_situacao', public.nome_atual() || ' pediu o ponto de situação de ' || tit, p_alvo, p_ref, txt);
  if p_alvo = 'tarefa' then
    for d in select * from public.pessoas_da_tarefa(p_ref) loop
      perform public.notificar(proj, 'pedido_situacao', public.nome_atual() || ' pede-te o ponto de situação de ' || tit, p_alvo, p_ref, d);
      n := n + 1;
    end loop;
  end if;
  if n = 0 then   -- ninguém a acompanhar: pergunta a quem edita
    for d in select * from public.editores() loop
      perform public.notificar(proj, 'pedido_situacao', public.nome_atual() || ' pede o ponto de situação de ' || tit, p_alvo, p_ref, d);
    end loop;
  end if;
end $$;

-- deixar a tarefa à espera de aprovação (qualquer pessoa da equipa); quem edita aprova (conclui) ou devolve
create or replace function public.pedir_aprovacao(p_tarefa bigint, p_texto text default '') returns void
language plpgsql security definer set search_path = '' as $$
declare t public.tarefas; d uuid; txt text := left(btrim(coalesce(p_texto, '')), 4000);
begin
  if (select auth.uid()) is null or not public.pode_ver() then raise exception 'Sem acesso ao Design.'; end if;
  select * into t from public.tarefas where id = p_tarefa;
  if t.id is null then raise exception 'A tarefa não existe.'; end if;
  if t.estado = 'concluida' then raise exception 'A tarefa já está concluída.'; end if;
  update public.tarefas set estado = 'por_aprovar' where id = p_tarefa;
  insert into public.atividade (alvo, ref_id, tipo, texto) values ('tarefa', p_tarefa, 'pedido_aprovacao', coalesce(nullif(txt, ''), 'Está pronta: falta a tua aprovação.'));
  for d in select * from public.editores() loop
    perform public.notificar(t.projeto, 'pedido_aprovacao', public.nome_atual() || ' pede a tua aprovação: «' || t.titulo || '»', 'tarefa', p_tarefa, d);
  end loop;
end $$;

create or replace function public.decidir_aprovacao(p_tarefa bigint, p_aprovar boolean, p_texto text default '') returns void
language plpgsql security definer set search_path = '' as $$
declare t public.tarefas; d uuid; txt text := left(btrim(coalesce(p_texto, '')), 4000);
begin
  if (select auth.uid()) is null or not public.pode_editar() then raise exception 'Só quem edita o Design aprova.'; end if;
  select * into t from public.tarefas where id = p_tarefa;
  if t.id is null then raise exception 'A tarefa não existe.'; end if;
  if p_aprovar then
    update public.tarefas set estado = 'concluida' where id = p_tarefa;   -- a equipa é avisada (tarefa concluída)
    insert into public.atividade (alvo, ref_id, tipo, texto) values ('tarefa', p_tarefa, 'aprovada', coalesce(nullif(txt, ''), 'Aprovada.'));
  else
    if txt = '' then raise exception 'Diz o que falta para a aprovar.'; end if;
    update public.tarefas set estado = 'em_curso' where id = p_tarefa;
    insert into public.atividade (alvo, ref_id, tipo, texto) values ('tarefa', p_tarefa, 'devolvida', txt);
    for d in select * from public.pessoas_da_tarefa(p_tarefa)
             union select a.autor_id from public.atividade a where a.alvo = 'tarefa' and a.ref_id = p_tarefa and a.tipo = 'pedido_aprovacao' and a.autor_id is not null loop
      perform public.notificar(t.projeto, 'devolvida', public.nome_atual() || ' devolveu «' || t.titulo || '»: ' || left(txt, 200), 'tarefa', p_tarefa, d);
    end loop;
  end if;
end $$;

-- ------------------------------------------------------------------ 4. críticas e comentários sobre um projeto
create table public.criticas (
  id bigint generated always as identity primary key,
  projeto text not null references public.projetos (id) on delete cascade,
  tipo text not null check (tipo in ('erro', 'nao_gostei', 'sugestao', 'comentario')),
  texto text not null check (char_length(btrim(texto)) between 2 and 4000),
  onde text not null default '' check (char_length(onde) <= 300),   -- onde aconteceu (página, passo, documento)
  anexos jsonb not null default '[]'::jsonb,
  estado text not null default 'nova' check (estado in ('nova', 'vista', 'resolvida')),
  tarefa_id bigint references public.tarefas (id) on delete set null,   -- passou a tarefa
  autor_id uuid default auth.uid() references auth.users (id) on delete set null,
  autor_nome text not null default '' check (char_length(autor_nome) <= 120),
  criada_em timestamptz not null default now(),
  resolvida_por_nome text not null default '',
  resolvida_em timestamptz
);
create index criticas_projeto_idx on public.criticas (projeto, criada_em desc);
create index criticas_autor_idx on public.criticas (autor_id);
create index criticas_tarefa_idx on public.criticas (tarefa_id);
alter table public.criticas enable row level security;
create policy "Ver" on public.criticas for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.criticas for insert to authenticated with check ((select public.pode_ver()) and autor_id = (select auth.uid()));
create policy "Editar" on public.criticas for update to authenticated
  using ((select public.pode_editar()) or ((select public.pode_ver()) and autor_id = (select auth.uid())))
  with check ((select public.pode_editar()) or ((select public.pode_ver()) and autor_id = (select auth.uid())));
create policy "Apagar" on public.criticas for delete to authenticated
  using ((select public.pode_editar()) or ((select public.pode_ver()) and autor_id = (select auth.uid())));

create or replace function public.criticas_antes() returns trigger language plpgsql security definer set search_path = '' as $$
declare a jsonb;
begin
  if tg_op = 'INSERT' then
    new.autor_id := (select auth.uid());
    new.autor_nome := case when (select auth.uid()) is null then coalesce(nullif(new.autor_nome, ''), 'Claude') else public.nome_atual() end;
    new.criada_em := now(); new.estado := 'nova'; new.resolvida_por_nome := ''; new.resolvida_em := null;
  else
    new.autor_id := old.autor_id; new.autor_nome := old.autor_nome; new.criada_em := old.criada_em; new.projeto := old.projeto;
    if new.estado = 'resolvida' and old.estado <> 'resolvida' then new.resolvida_por_nome := public.nome_atual(); new.resolvida_em := now();
    elsif new.estado <> 'resolvida' then new.resolvida_por_nome := ''; new.resolvida_em := null; end if;
  end if;
  if jsonb_typeof(new.anexos) <> 'array' or jsonb_array_length(new.anexos) > 10 then raise exception 'Até 10 anexos.'; end if;
  for a in select value from jsonb_array_elements(new.anexos) loop
    if coalesce(a ->> 'caminho', '') not like 'critica/%' or coalesce(a ->> 'tipo', '') not in ('imagem', 'video', 'audio', 'ficheiro') then
      raise exception 'Anexo inválido.';
    end if;
  end loop;
  return new;
end $$;
create trigger criticas_antes before insert or update on public.criticas for each row execute function public.criticas_antes();

create or replace function public.criticas_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare nome text := (select p.nome from public.projetos p where p.id = new.projeto);
  rot text := case new.tipo when 'erro' then 'Algo correu mal' when 'nao_gostei' then 'Não gostei' when 'sugestao' then 'Sugestão' else 'Comentário' end;
begin
  if tg_op = 'INSERT' then
    perform public.notificar(new.projeto, 'critica_nova', public.nome_atual() || ' deixou uma crítica no ' || nome || ' (' || rot || '): '
      || left(new.texto, 160), 'critica', new.id);
  elsif new.estado is distinct from old.estado and new.estado = 'resolvida' then
    perform public.registar(new.projeto, 'critica_resolvida', public.nome_atual() || ' resolveu a crítica sobre o ' || nome || ': '
      || left(new.texto, 160), 'critica', new.id);
  end if;
  return null;
end $$;
create trigger criticas_depois after insert or update on public.criticas for each row execute function public.criticas_depois();

-- ------------------------------------------------------------------ funções: quem as pode chamar
revoke execute on function public.registar(text, text, text, text, bigint, text), public.marcacoes_antes(), public.marcacoes_depois(),
  public.atividade_antes(), public.atividade_depois(), public.atividade_orfa(), public.criticas_antes(), public.criticas_depois(),
  public.pessoas_da_tarefa(bigint), public.editores() from public, anon, authenticated;
revoke execute on function public.notificar(text, text, text, text, bigint, uuid) from public, anon, authenticated;
revoke execute on function public.dar_situacao(text, bigint, text), public.pedir_situacao(text, bigint, text),
  public.pedir_aprovacao(bigint, text), public.decidir_aprovacao(bigint, boolean, text) from public, anon;
grant execute on function public.dar_situacao(text, bigint, text), public.pedir_situacao(text, bigint, text),
  public.pedir_aprovacao(bigint, text), public.decidir_aprovacao(bigint, boolean, text) to authenticated;

-- em direto
alter publication supabase_realtime add table public.registo, public.marcacoes, public.atividade, public.criticas;
