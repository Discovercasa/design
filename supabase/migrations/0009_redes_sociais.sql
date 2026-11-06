-- Redes sociais (2026-11-06): "mais uma aba que quero adicionar ao nosso Hub de Design: os nossos posts/social media".
-- Os posts são planeados antes (um por semana) para a legenda e as fotos serem aprovadas; as obras (Matosinhos, Casa dos
-- Cães, Boelhe, Ribamar, Gaia…) têm fases que "não se apagam", só se acrescentam e se vão marcando, para saber quando ir
-- ao local tirar fotos e extrair conteúdo.
-- (mais tarde) "às vezes há posts que não são feitos … fazemos o post seguinte ou dois posts à frente": estado "Não feito"
-- e mudar um post de semana (adiantar), guardando a semana em que estava planeado.

-- ---------------------------------------------------------------- obras e fases
create table public.obras (
  id bigint generated always as identity primary key,
  nome text not null check (char_length(nome) between 2 and 120),
  descricao text not null default '' check (char_length(descricao) <= 2000),
  ativa boolean not null default true,          -- arquivar em vez de apagar
  ordem int not null default 0,
  criado_por uuid default auth.uid(),
  criado_por_nome text not null default '' check (char_length(criado_por_nome) <= 120),
  criado_em timestamptz not null default now()
);
create unique index obras_nome_idx on public.obras (lower(nome));

-- fases de cada obra, por ordem: nunca se apagam (não há regra de apagar), só mudam de estado
create table public.obras_fases (
  id bigint generated always as identity primary key,
  obra_id bigint not null references public.obras (id) on delete cascade,
  nome text not null check (char_length(nome) between 1 and 120),
  ordem int not null default 0,
  estado text not null default 'prevista' check (estado in ('prevista', 'em_curso', 'concluida')),
  periodo text not null default '' check (char_length(periodo) <= 80),     -- como no Excel: "Set - Out"
  posts_previstos int check (posts_previstos between 0 and 99),           -- quantas publicações queremos desta fase
  fotos text not null default 'por_tirar' check (fotos in ('por_tirar', 'visita_marcada', 'tiradas')),
  visita_em date,                                                          -- dia marcado para ir tirar fotos
  fotos_em date,                                                           -- dia em que as fotos foram tiradas
  notas text not null default '' check (char_length(notas) <= 2000),
  concluida_em date,
  criado_por uuid default auth.uid(),
  criado_por_nome text not null default '' check (char_length(criado_por_nome) <= 120),
  criado_em timestamptz not null default now()
);
create index obras_fases_obra_idx on public.obras_fases (obra_id, ordem);

-- ---------------------------------------------------------------- posts
create table public.posts (
  id bigint generated always as identity primary key,
  mes date not null check (extract(day from mes) = 1),                     -- o mês (dia 1)
  semana int not null check (semana between 1 and 5),                      -- semana do mês
  obra_id bigint references public.obras (id) on delete set null,
  fase_id bigint references public.obras_fases (id) on delete set null,
  titulo text not null check (char_length(titulo) between 2 and 200),     -- "Boelhe - BF"
  tipo text not null default 'carrossel' check (tipo in ('carrossel', 'foto', 'video', 'reel', 'story')),
  redes text[] not null default '{instagram,facebook}' check (redes <@ array['instagram', 'facebook', 'linkedin']::text[]),
  legenda text not null default '' check (char_length(legenda) <= 5000),
  notas text not null default '' check (char_length(notas) <= 4000),
  estado text not null default 'ideia' check (estado in ('ideia', 'rascunho', 'por_aprovar', 'aprovado', 'publicado', 'nao_feito')),
  legenda_aprovada boolean not null default false,
  legenda_aprovada_por_nome text not null default '',
  legenda_aprovada_em date,
  fotos_aprovadas boolean not null default false,
  fotos_aprovadas_por_nome text not null default '',
  fotos_aprovadas_em date,
  publicar_em date,                                                        -- dia previsto (opcional)
  mes_original date,                                                       -- onde estava planeado antes de mudar de semana
  semana_original int,
  publicado_em date,
  criado_por uuid default auth.uid(),
  criado_por_nome text not null default '' check (char_length(criado_por_nome) <= 120),
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);
create index posts_mes_idx on public.posts (mes, semana);
create index posts_obra_idx on public.posts (obra_id);
create index posts_fase_idx on public.posts (fase_id);

-- fotos e vídeos de cada post: o ficheiro original e uma miniatura no armazenamento privado "social"
create table public.posts_media (
  id bigint generated always as identity primary key,
  post_id bigint not null references public.posts (id) on delete cascade,
  caminho text not null check (caminho ~ '^posts/[^/]+$'),
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
create index posts_media_post_idx on public.posts_media (post_id, ordem);

-- comentários de aprovação ("consegues tirar aquele saco?"): sobre o post ou sobre uma foto; quem vê também comenta
create table public.posts_comentarios (
  id bigint generated always as identity primary key,
  post_id bigint not null references public.posts (id) on delete cascade,
  media_id bigint references public.posts_media (id) on delete set null,
  texto text not null check (char_length(texto) between 1 and 2000),
  resolvido boolean not null default false,
  autor_id uuid default auth.uid(),
  autor_nome text not null default '' check (char_length(autor_nome) <= 120),
  criado_em timestamptz not null default now()
);
create index posts_comentarios_post_idx on public.posts_comentarios (post_id, criado_em);
create index posts_comentarios_media_idx on public.posts_comentarios (media_id);

-- ---------------------------------------------------------------- RLS
alter table public.obras enable row level security;
create policy "Ver" on public.obras for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.obras for insert to authenticated with check ((select public.pode_editar()));
create policy "Editar" on public.obras for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));

alter table public.obras_fases enable row level security;
create policy "Ver" on public.obras_fases for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.obras_fases for insert to authenticated with check ((select public.pode_editar()));
create policy "Editar" on public.obras_fases for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));

alter table public.posts enable row level security;
create policy "Ver" on public.posts for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.posts for insert to authenticated with check ((select public.pode_editar()));
create policy "Editar" on public.posts for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));
create policy "Apagar" on public.posts for delete to authenticated using ((select public.pode_editar()));

alter table public.posts_media enable row level security;
create policy "Ver" on public.posts_media for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.posts_media for insert to authenticated with check ((select public.pode_editar()));
create policy "Editar" on public.posts_media for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));
create policy "Apagar" on public.posts_media for delete to authenticated using ((select public.pode_editar()));

alter table public.posts_comentarios enable row level security;
create policy "Ver" on public.posts_comentarios for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.posts_comentarios for insert to authenticated
  with check ((select public.pode_ver()) and autor_id = (select auth.uid()));
create policy "Editar" on public.posts_comentarios for update to authenticated
  using ((select public.pode_editar()) or autor_id = (select auth.uid()))
  with check ((select public.pode_editar()) or autor_id = (select auth.uid()));
create policy "Apagar" on public.posts_comentarios for delete to authenticated
  using ((select public.pode_editar()) or autor_id = (select auth.uid()));

-- ---------------------------------------------------------------- notificações e "Novo"
alter table public.notificacoes drop constraint notificacoes_tipo_check;
alter table public.notificacoes add constraint notificacoes_tipo_check check (tipo in ('tarefa_nova', 'tarefa_atribuida',
  'tarefa_estado', 'tarefa_concluida', 'checkpoint_novo', 'checkpoint_estado', 'checkpoint_concluido', 'decisao_nova',
  'decisao_tomada', 'documento_novo', 'post_novo', 'post_estado', 'post_aprovacao', 'post_comentario', 'obra_nova',
  'fase_nova', 'fase_estado'));
alter table public.vistos drop constraint vistos_tipo_check;
alter table public.vistos add constraint vistos_tipo_check check (tipo in ('checkpoint', 'tarefa', 'decisao', 'documento', 'post', 'obra'));

create or replace function public.rotulo_post(e text) returns text language sql immutable set search_path = '' as $$
  select case e when 'ideia' then 'Ideia' when 'rascunho' then 'Rascunho' when 'por_aprovar' then 'Por aprovar'
                when 'aprovado' then 'Aprovado' when 'publicado' then 'Publicado' when 'nao_feito' then 'Não feito' else e end
$$;

-- ---------------------------------------------------------------- triggers: carimbos, aprovação e notificações
create or replace function public.obras_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
  else
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
  end if;
  return new;
end $$;
create trigger obras_antes before insert or update on public.obras for each row execute function public.obras_antes();
create or replace function public.obras_depois() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  perform public.notificar(null, 'obra_nova', public.nome_atual() || ' acrescentou a obra «' || new.nome || '»', 'obra', new.id);
  return null;
end $$;
create trigger obras_depois after insert on public.obras for each row execute function public.obras_depois();

create or replace function public.obras_fases_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
    if new.estado = 'concluida' and new.concluida_em is null then new.concluida_em := current_date; end if;
  else
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
    new.obra_id := old.obra_id;   -- uma fase não muda de obra
    if new.estado is distinct from old.estado then
      new.concluida_em := case when new.estado = 'concluida' then current_date end;
    end if;
  end if;
  if new.fotos = 'tiradas' and (tg_op = 'INSERT' or old.fotos <> 'tiradas') and new.fotos_em is null then new.fotos_em := current_date; end if;
  if new.fotos <> 'tiradas' then new.fotos_em := null; end if;
  if new.fotos = 'por_tirar' then new.visita_em := null; end if;
  return new;
end $$;
create trigger obras_fases_antes before insert or update on public.obras_fases for each row execute function public.obras_fases_antes();
create or replace function public.obras_fases_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare o text := (select nome from public.obras where id = new.obra_id); f text := '«' || new.nome || '»';
begin
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
create trigger obras_fases_depois after insert or update on public.obras_fases for each row execute function public.obras_fases_depois();

create or replace function public.posts_antes() returns trigger language plpgsql security definer set search_path = '' as $$
declare quem text := public.nome_atual();
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := quem; new.criado_em := now();
    end if;
  else
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
  end if;
  new.atualizado_em := now();
  -- mudou de semana: guarda a primeira semana planeada (volta a limpar se regressar a ela)
  if tg_op = 'UPDATE' and (new.mes, new.semana) is distinct from (old.mes, old.semana) then
    if old.mes_original is null then new.mes_original := old.mes; new.semana_original := old.semana;
    else new.mes_original := old.mes_original; new.semana_original := old.semana_original; end if;
    if (new.mes, new.semana) = (new.mes_original, new.semana_original) then new.mes_original := null; new.semana_original := null; end if;
  elsif tg_op = 'UPDATE' then new.mes_original := old.mes_original; new.semana_original := old.semana_original;
  end if;
  -- a fase tem de ser da obra do post
  if new.fase_id is not null and not exists (select 1 from public.obras_fases f where f.id = new.fase_id and f.obra_id = new.obra_id) then
    new.fase_id := null;
  end if;
  -- quem aprovou e quando (só o dia); mudar a legenda depois de aprovada pede nova aprovação
  if tg_op = 'UPDATE' and new.legenda is distinct from old.legenda and old.legenda_aprovada and new.legenda_aprovada then
    new.legenda_aprovada := false;
  end if;
  if new.legenda_aprovada and (tg_op = 'INSERT' or not old.legenda_aprovada) then
    if (select auth.uid()) is not null then new.legenda_aprovada_por_nome := quem; new.legenda_aprovada_em := current_date;
    elsif new.legenda_aprovada_em is null then new.legenda_aprovada_em := current_date; end if;
  elsif not new.legenda_aprovada then new.legenda_aprovada_por_nome := ''; new.legenda_aprovada_em := null;
  end if;
  if new.fotos_aprovadas and (tg_op = 'INSERT' or not old.fotos_aprovadas) then
    if (select auth.uid()) is not null then new.fotos_aprovadas_por_nome := quem; new.fotos_aprovadas_em := current_date;
    elsif new.fotos_aprovadas_em is null then new.fotos_aprovadas_em := current_date; end if;
  elsif not new.fotos_aprovadas then new.fotos_aprovadas_por_nome := ''; new.fotos_aprovadas_em := null;
  end if;
  -- legenda e fotos aprovadas → o post fica aprovado; se uma deixar de estar, volta a "por aprovar"
  if new.legenda_aprovada and new.fotos_aprovadas and new.estado in ('ideia', 'rascunho', 'por_aprovar') then new.estado := 'aprovado';
  elsif not (new.legenda_aprovada and new.fotos_aprovadas) and new.estado = 'aprovado' then new.estado := 'por_aprovar';
  end if;
  -- o dia em que foi publicado (os posts importados do Excel ficam sem dia: não se sabe)
  if new.estado = 'publicado' then
    if new.publicado_em is null and ((tg_op = 'UPDATE' and old.estado <> 'publicado') or (select auth.uid()) is not null) then
      new.publicado_em := current_date;
    end if;
  else new.publicado_em := null;
  end if;
  return new;
end $$;
create trigger posts_antes before insert or update on public.posts for each row execute function public.posts_antes();

create or replace function public.posts_depois() returns trigger language plpgsql security definer set search_path = '' as $$
declare t text := '«' || new.titulo || '»'; quem text := public.nome_atual();
begin
  if tg_op = 'INSERT' then
    perform public.notificar(null, 'post_novo', quem || ' planeou o post ' || t, 'post', new.id);
    return null;
  end if;
  if new.legenda_aprovada and not old.legenda_aprovada and new.fotos_aprovadas and not old.fotos_aprovadas then
    perform public.notificar(null, 'post_aprovacao', quem || ' aprovou a legenda e as fotos do post ' || t, 'post', new.id);
  elsif new.legenda_aprovada and not old.legenda_aprovada then
    perform public.notificar(null, 'post_aprovacao', quem || ' aprovou a legenda do post ' || t, 'post', new.id);
  elsif new.fotos_aprovadas and not old.fotos_aprovadas then
    perform public.notificar(null, 'post_aprovacao', quem || ' aprovou as fotos do post ' || t, 'post', new.id);
  end if;
  if new.estado is distinct from old.estado then
    perform public.notificar(null, 'post_estado', quem || case new.estado
      when 'por_aprovar' then ' pediu aprovação do post ' || t
      when 'publicado' then ' publicou o post ' || t
      else ' mudou o post ' || t || ' para ' || public.rotulo_post(new.estado) end, 'post', new.id);
  end if;
  return null;
end $$;
create trigger posts_depois after insert or update on public.posts for each row execute function public.posts_depois();

create or replace function public.posts_media_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
  else
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
    new.caminho := old.caminho; new.miniatura := old.miniatura; new.post_id := old.post_id;
  end if;
  return new;
end $$;
create trigger posts_media_antes before insert or update on public.posts_media for each row execute function public.posts_media_antes();
-- fotos novas ou tiradas: as fotos aprovadas deixam de estar (é preciso voltar a aprovar)
create or replace function public.posts_media_depois() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if (select auth.uid()) is not null then
    update public.posts set fotos_aprovadas = false where id = coalesce(new.post_id, old.post_id) and fotos_aprovadas;
  end if;
  return null;
end $$;
create trigger posts_media_depois after insert or delete on public.posts_media for each row execute function public.posts_media_depois();

create or replace function public.posts_comentarios_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then new.autor_id := (select auth.uid()); new.autor_nome := public.nome_atual(); new.criado_em := now(); end if;
  else
    new.autor_id := old.autor_id; new.autor_nome := old.autor_nome; new.criado_em := old.criado_em; new.post_id := old.post_id;
    if not public.pode_editar() then new.texto := old.texto; end if;
  end if;
  return new;
end $$;
create trigger posts_comentarios_antes before insert or update on public.posts_comentarios for each row execute function public.posts_comentarios_antes();
create or replace function public.posts_comentarios_depois() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  perform public.notificar(null, 'post_comentario', public.nome_atual() || ' comentou o post «'
    || (select titulo from public.posts where id = new.post_id) || '»: ' || left(new.texto, 120), 'post', new.post_id);
  return null;
end $$;
create trigger posts_comentarios_depois after insert on public.posts_comentarios for each row execute function public.posts_comentarios_depois();

revoke execute on function public.obras_antes(), public.obras_depois(), public.obras_fases_antes(), public.obras_fases_depois(),
  public.posts_antes(), public.posts_depois(), public.posts_media_antes(), public.posts_media_depois(),
  public.posts_comentarios_antes(), public.posts_comentarios_depois() from public, anon, authenticated;

-- ---------------------------------------------------------------- armazenamento privado "social"
-- fotos e vídeos dos posts: só quem vê o Design abre (URL assinado e temporário); só quem edita carrega ou apaga
insert into storage.buckets (id, name, public, file_size_limit)
  values ('social', 'social', false, 52428800)
  on conflict (id) do nothing;
create policy "Social: ver" on storage.objects for select to authenticated
  using (bucket_id = 'social' and (select public.pode_ver()));
create policy "Social: carregar" on storage.objects for insert to authenticated
  with check (bucket_id = 'social' and (select public.pode_editar()));
create policy "Social: mudar" on storage.objects for update to authenticated
  using (bucket_id = 'social' and (select public.pode_editar())) with check (bucket_id = 'social' and (select public.pode_editar()));
create policy "Social: apagar" on storage.objects for delete to authenticated
  using (bucket_id = 'social' and (select public.pode_editar()));

-- ---------------------------------------------------------------- em direto
alter publication supabase_realtime add table public.obras, public.obras_fases, public.posts, public.posts_media,
  public.posts_comentarios;
