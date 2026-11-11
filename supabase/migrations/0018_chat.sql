-- Design — Chat da equipa (2026-11-11). O utilizador: «criasses um sistema onde fosse possível mandar mensagem aos
-- elementos que estão no hub, coloca o ícone de chat ao lado esquerdo do das sugestões. No chat deve ser possível mandar
-- mensagens, dar attach a ficheiros e a imagens/videos e mandar áudios.»
--
-- Conversas diretas (duas pessoas, sempre a mesma entre as duas) ou de grupo. Cada conversa só a veem os seus membros:
-- nem quem pode editar o Design lê as conversas dos outros. Os ficheiros (imagens, vídeos, áudios, documentos) ficam no
-- armazenamento privado "chat", numa pasta por conversa (<conversa>/<ficheiro>), com as mesmas regras.
-- O Claude não tem conta: as suas mensagens entram pela base de dados (sem sessão) com autor_id null e autor_nome
-- 'Claude', numa conversa marcada claude = true (a pessoa responde-lhe ali e o Claude lê as respostas na base).

create table public.conversas (
  id bigint generated always as identity primary key,
  titulo text not null default '' check (char_length(titulo) <= 120),
  grupo boolean not null default false,
  claude boolean not null default false,
  criada_por uuid default auth.uid() references auth.users (id) on delete set null,
  criada_em timestamptz not null default now(),
  ultima_em timestamptz not null default now()   -- a hora da última mensagem (ordem da lista)
);
create index conversas_criada_por_idx on public.conversas (criada_por);

create table public.conversas_membros (
  conversa_id bigint not null references public.conversas (id) on delete cascade,
  utilizador_id uuid not null references auth.users (id) on delete cascade,
  lida_em timestamptz not null default now(),    -- li até aqui: as mensagens dos outros depois disto estão por ler
  entrou_em timestamptz not null default now(),
  primary key (conversa_id, utilizador_id)
);
create index conversas_membros_utilizador_idx on public.conversas_membros (utilizador_id);

create table public.mensagens (
  id bigint generated always as identity primary key,
  conversa_id bigint not null references public.conversas (id) on delete cascade,
  autor_id uuid default auth.uid() references auth.users (id) on delete set null,   -- null: o Claude
  autor_nome text not null default '' check (char_length(autor_nome) <= 120),
  texto text not null default '' check (char_length(texto) <= 4000),
  -- [{caminho, nome, mime, tamanho, tipo: imagem|video|audio|ficheiro, miniatura?, largura?, altura?, duracao?}]
  anexos jsonb not null default '[]'::jsonb,
  criada_em timestamptz not null default now(),
  check (char_length(btrim(texto)) > 0 or jsonb_array_length(anexos) > 0)
);
create index mensagens_conversa_idx on public.mensagens (conversa_id, criada_em desc);
create index mensagens_autor_idx on public.mensagens (autor_id);

-- sou membro desta conversa? (security definer: a regra de conversas_membros não se pode consultar a si própria)
create or replace function public.e_membro(p_conversa bigint) returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.conversas_membros m where m.conversa_id = p_conversa and m.utilizador_id = (select auth.uid()))
$$;
revoke execute on function public.e_membro(bigint) from public, anon;
grant execute on function public.e_membro(bigint) to authenticated;
-- o mesmo para um ficheiro do armazenamento "chat" (a primeira pasta é o número da conversa)
create or replace function public.e_membro_caminho(p_nome text) returns boolean
language sql stable set search_path = '' as $$
  select case when split_part(p_nome, '/', 1) ~ '^[0-9]{1,18}$' then public.e_membro(split_part(p_nome, '/', 1)::bigint) else false end
$$;
revoke execute on function public.e_membro_caminho(text) from public, anon;
grant execute on function public.e_membro_caminho(text) to authenticated;

-- RLS: só os membros veem a conversa, os membros e as mensagens; cada um escreve em seu nome e apaga as suas.
-- As conversas criam-se pela função abrir_conversa (que junta os membros de uma vez); ninguém as muda nem apaga na página.
alter table public.conversas enable row level security;
create policy "Ver" on public.conversas for select to authenticated using ((select public.pode_ver()) and public.e_membro(id));

alter table public.conversas_membros enable row level security;
create policy "Ver" on public.conversas_membros for select to authenticated
  using ((select public.pode_ver()) and public.e_membro(conversa_id));
create policy "Ler" on public.conversas_membros for update to authenticated   -- só a minha linha e só lida_em (grant abaixo)
  using ((select public.pode_ver()) and utilizador_id = (select auth.uid()))
  with check ((select public.pode_ver()) and utilizador_id = (select auth.uid()));
revoke update on public.conversas_membros from anon, authenticated;
grant update (lida_em) on public.conversas_membros to authenticated;

alter table public.mensagens enable row level security;
create policy "Ver" on public.mensagens for select to authenticated using ((select public.pode_ver()) and public.e_membro(conversa_id));
create policy "Escrever" on public.mensagens for insert to authenticated
  with check ((select public.pode_ver()) and public.e_membro(conversa_id) and autor_id = (select auth.uid()));
create policy "Apagar" on public.mensagens for delete to authenticated
  using ((select public.pode_ver()) and autor_id = (select auth.uid()));

-- abrir (ou criar) uma conversa com estas pessoas; eu entro sempre. Duas pessoas: a conversa direta que já existir.
create or replace function public.abrir_conversa(p_membros uuid[], p_titulo text default '') returns bigint
language plpgsql security definer set search_path = '' as $$
declare
  eu uuid := (select auth.uid());
  todos uuid[];
  c bigint;
begin
  if eu is null or not public.pode_ver() then raise exception 'Sem acesso ao Design.'; end if;
  select array_agg(distinct x order by x) into todos from unnest(coalesce(p_membros, '{}'::uuid[]) || eu) x;
  if coalesce(array_length(todos, 1), 0) < 2 then raise exception 'Escolhe pelo menos uma pessoa.'; end if;
  if array_length(todos, 1) > 30 then raise exception 'No máximo 30 pessoas numa conversa.'; end if;
  if exists (select 1 from unnest(todos) x where not exists (select 1 from public.perfis p where p.id = x)) then
    raise exception 'Só se podem juntar pessoas do hub.';
  end if;
  if array_length(todos, 1) = 2 then
    select m.conversa_id into c
      from public.conversas_membros m join public.conversas k on k.id = m.conversa_id and not k.grupo and not k.claude
      group by m.conversa_id
      having array_agg(m.utilizador_id order by m.utilizador_id) = todos
      limit 1;
    if c is not null then return c; end if;
  end if;
  insert into public.conversas (titulo, grupo, criada_por)
    values (left(btrim(coalesce(p_titulo, '')), 120), array_length(todos, 1) > 2, eu) returning id into c;
  insert into public.conversas_membros (conversa_id, utilizador_id) select c, x from unnest(todos) x;
  return c;
end $$;
revoke execute on function public.abrir_conversa(uuid[], text) from public, anon;
grant execute on function public.abrir_conversa(uuid[], text) to authenticated;

-- carimbos: o autor é quem tem a sessão (sem sessão: o Claude); os anexos ficam na pasta da própria conversa
create or replace function public.mensagens_antes() returns trigger language plpgsql security definer set search_path = '' as $$
declare a jsonb;
begin
  new.criada_em := now();
  if (select auth.uid()) is null then
    new.autor_id := null; new.autor_nome := coalesce(nullif(btrim(new.autor_nome), ''), 'Claude');
  else
    new.autor_id := (select auth.uid()); new.autor_nome := public.nome_atual();
  end if;
  if jsonb_typeof(new.anexos) <> 'array' or jsonb_array_length(new.anexos) > 10 then
    raise exception 'Até 10 anexos por mensagem.';
  end if;
  for a in select value from jsonb_array_elements(new.anexos) loop
    if coalesce(a ->> 'caminho', '') not like new.conversa_id::text || '/%'
       or coalesce(a ->> 'tipo', '') not in ('imagem', 'video', 'audio', 'ficheiro') then
      raise exception 'Anexo inválido.';
    end if;
  end loop;
  return new;
end $$;
create trigger mensagens_antes before insert on public.mensagens for each row execute function public.mensagens_antes();

create or replace function public.mensagens_depois() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  update public.conversas set ultima_em = new.criada_em where id = new.conversa_id;
  if new.autor_id is not null then   -- a minha própria mensagem: li a conversa até aqui
    update public.conversas_membros set lida_em = new.criada_em where conversa_id = new.conversa_id and utilizador_id = new.autor_id;
  end if;
  return null;
end $$;
create trigger mensagens_depois after insert on public.mensagens for each row execute function public.mensagens_depois();
revoke execute on function public.mensagens_antes(), public.mensagens_depois() from public, anon, authenticated;

-- armazenamento privado "chat" (50 MB por ficheiro, como os outros)
insert into storage.buckets (id, name, public, file_size_limit) values ('chat', 'chat', false, 52428800)
  on conflict (id) do nothing;
create policy "Chat: ver" on storage.objects for select to authenticated
  using (bucket_id = 'chat' and (select public.pode_ver()) and public.e_membro_caminho(name));
create policy "Chat: carregar" on storage.objects for insert to authenticated
  with check (bucket_id = 'chat' and (select public.pode_ver()) and public.e_membro_caminho(name));
create policy "Chat: apagar" on storage.objects for delete to authenticated
  using (bucket_id = 'chat' and owner_id = (select auth.uid()::text));

-- em direto: as mensagens chegam logo a quem tem o hub aberto (o Realtime respeita as regras acima)
alter publication supabase_realtime add table public.conversas, public.conversas_membros, public.mensagens;
