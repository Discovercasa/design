-- Documentos: secções e pastas (2026-11-11). O utilizador: «nos documentos adicionais ou documentos informativos deve
-- ser possível criar uma secção tal como tu fizeste nos documentos adicionais do builder … quero que seja possível
-- adicionar essa subseção e depois adicionar os ficheiros que pretendo lá, deve ser também possível adicionar pastas de
-- ficheiros».
--  * documentos_seccoes: as secções de cada projeto e tipo (informativo / adicional), criadas por quem edita; existem
--    vazias (cria-se a secção, depois acrescentam-se ficheiros).
--  * documentos.seccao_id: a secção do documento (nenhuma = fora das secções); documentos.pasta: o caminho da pasta de
--    onde veio quando se carrega uma pasta inteira ("Desenhos/Arquitetura"); os ficheiros continuam guardados no mesmo
--    armazenamento privado, no caminho <projeto>/<tipo>/<nome> (a pasta é só como se mostram).
--  * documentos.lote: os ficheiros carregados de uma vez (uma pasta) — um só registo no Log em vez de um por ficheiro
--    (documentos_lote_feito).
--  * As secções que existiam só no título («Torres Vedras · …») passam a secções verdadeiras.

create table public.documentos_seccoes (
  id bigint generated always as identity primary key,
  projeto text not null references public.projetos (id) on delete cascade,
  tipo text not null check (tipo in ('informativo', 'adicional')),
  nome text not null check (char_length(btrim(nome)) between 1 and 120),
  ordem integer not null default 0,
  criado_por uuid default auth.uid(),
  criado_por_nome text not null default '' check (char_length(criado_por_nome) <= 120),
  criado_em timestamptz not null default now(),
  unique (projeto, tipo, nome)
);
create index documentos_seccoes_projeto_idx on public.documentos_seccoes (projeto, tipo);
alter table public.documentos_seccoes enable row level security;
create policy "Ver" on public.documentos_seccoes for select to authenticated using ((select public.pode_ver()));
create policy "Criar" on public.documentos_seccoes for insert to authenticated with check ((select public.pode_editar()));
create policy "Editar" on public.documentos_seccoes for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));
create policy "Apagar" on public.documentos_seccoes for delete to authenticated using ((select public.pode_editar()));

create or replace function public.documentos_seccoes_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  new.nome := btrim(new.nome);
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
  else
    new.projeto := old.projeto; new.tipo := old.tipo;
    new.criado_por := old.criado_por; new.criado_por_nome := old.criado_por_nome; new.criado_em := old.criado_em;
  end if;
  return new;
end $$;
create trigger documentos_seccoes_antes before insert or update on public.documentos_seccoes
  for each row execute function public.documentos_seccoes_antes();
revoke execute on function public.documentos_seccoes_antes() from public, anon, authenticated;

alter table public.documentos add column seccao_id bigint references public.documentos_seccoes (id) on delete set null;
alter table public.documentos add column pasta text not null default ''
  check (char_length(pasta) <= 500 and pasta !~ '(^/|/$|\.\.)');
alter table public.documentos add column lote text check (lote is null or lote ~ '^[a-z0-9-]{4,40}$');
create index documentos_seccao_idx on public.documentos (seccao_id);
create index documentos_lote_idx on public.documentos (lote) where lote is not null;

-- a section must be of the document's own project and type
create or replace function public.documentos_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if new.seccao_id is not null and not exists (select 1 from public.documentos_seccoes s
      where s.id = new.seccao_id and s.projeto = new.projeto and s.tipo = new.tipo) then
    raise exception 'A secção não é deste projeto e tipo de documento.';
  end if;
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

-- one Log line per file, except for a batch (a folder): documentos_lote_feito writes one line for it
create or replace function public.documentos_depois() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if new.lote is not null then
    return null;
  end if;
  perform public.notificar(new.projeto, 'documento_novo', public.nome_atual() || ' acrescentou o documento «' || new.titulo || '»'
    || case when new.tipo = 'informativo' then ' (informativo)' else ' (adicional)' end, 'documento', new.id);
  return null;
end $$;

create or replace function public.documentos_lote_feito(p_lote text) returns void language plpgsql security definer
set search_path = '' as $$
declare
  d record;
  n integer;
  sec text;
begin
  if not (select public.pode_editar()) then
    raise exception 'Sem permissão para editar.';
  end if;
  select count(*) into n from public.documentos where lote = p_lote;
  if n = 0 then
    return;
  end if;
  select * into d from public.documentos where lote = p_lote order by id limit 1;
  select nome into sec from public.documentos_seccoes where id = d.seccao_id;
  perform public.notificar(d.projeto, 'documento_novo', public.nome_atual() || ' acrescentou ' || n
    || case when n = 1 then ' documento' else ' documentos' end
    || case when sec is not null then ' à secção «' || sec || '»' else '' end
    || case when d.pasta <> '' then ' (pasta «' || split_part(d.pasta, '/', 1) || '»)' else '' end
    || case when d.tipo = 'informativo' then ' (informativos)' else ' (adicionais)' end, 'documento', d.id);
end $$;
revoke execute on function public.documentos_lote_feito(text) from public, anon;
grant execute on function public.documentos_lote_feito(text) to authenticated;

-- the sections that lived in the titles («Torres Vedras · …») become real sections; the title keeps the rest
insert into public.documentos_seccoes (projeto, tipo, nome, ordem, criado_por, criado_por_nome)
select projeto, tipo, nome, (row_number() over (partition by projeto, tipo order by min_id))::integer, null, 'Claude'
from (select projeto, tipo, split_part(titulo, ' · ', 1) as nome, min(id) as min_id
      from public.documentos where tipo in ('informativo', 'adicional') and titulo like '% · %'
      group by 1, 2, 3) g;
update public.documentos d set seccao_id = s.id, titulo = substr(d.titulo, char_length(s.nome) + 4)
from public.documentos_seccoes s
where d.projeto = s.projeto and d.tipo = s.tipo and d.titulo like s.nome || ' · %' and d.seccao_id is null;

alter publication supabase_realtime add table public.documentos_seccoes;
