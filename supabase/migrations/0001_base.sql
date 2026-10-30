-- Design — base (projeto Supabase próprio; não é o do Hub).
-- As contas vêm do Hub (função design-entrar do Hub): cada pessoa tem app_metadata.nivel = 'ver' | 'editar' | 'sem'.
-- O app_metadata só o servidor muda (a pessoa não o consegue alterar), por isso as regras RLS podem confiar nele.

create or replace function public.nivel() returns text language sql stable set search_path = public as $$
  select coalesce((select auth.jwt()) -> 'app_metadata' ->> 'nivel', 'sem')
$$;
create or replace function public.pode_ver() returns boolean language sql stable set search_path = public as $$
  select public.nivel() in ('ver', 'editar')
$$;
create or replace function public.pode_editar() returns boolean language sql stable set search_path = public as $$
  select public.nivel() = 'editar'
$$;

-- Modelo para cada tabela nova (sempre com RLS):
--   alter table public.<tabela> enable row level security;
--   create policy "Ver" on public.<tabela> for select to authenticated using ((select public.pode_ver()));
--   create policy "Criar" on public.<tabela> for insert to authenticated with check ((select public.pode_editar()));
--   create policy "Editar" on public.<tabela> for update to authenticated using ((select public.pode_editar())) with check ((select public.pode_editar()));
--   create policy "Apagar" on public.<tabela> for delete to authenticated using ((select public.pode_editar()));
