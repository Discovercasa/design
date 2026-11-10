-- Design — Materiais vindos do Hub (só de consulta).
-- O Hub envia estas tabelas nos dias úteis às 6h (função "design-materiais" do Hub, com a chave de serviço DESTE projeto, que só o Hub guarda).
-- Aqui ninguém as altera: só há a regra "Ver". Não criar regras de criar/editar/apagar nem mudar as colunas sem falar com o Sebastião
-- (o Hub deixava de conseguir enviar).
-- Dos fornecedores vem só o nome (os contactos ficam no Hub).

create table if not exists public.hub_fornecedores (
  id uuid primary key,
  nome text not null,
  atualizado_em timestamptz
);

create table if not exists public.hub_materiais (
  id uuid primary key,
  nome text not null,
  categoria text,
  tipo text,
  atualizado_em timestamptz
);

create table if not exists public.hub_material_precos (
  id uuid primary key,
  material_id uuid references public.hub_materiais(id) on delete cascade,
  fornecedor_id uuid references public.hub_fornecedores(id) on delete set null,
  designacao text,
  dimensoes text,
  detalhes text,
  preco numeric,
  unidade text,
  desconto numeric,
  iva numeric,
  disponibilidade text,
  prazo_dias integer,
  data_atualizacao date,
  comprimento numeric,
  largura numeric,
  espessura numeric,
  qtd_embalagem numeric,
  qtd_unidade text,
  peso_kg numeric,
  kg_m3 numeric,
  transporte text,
  transporte_incluido text,
  atualizado_em timestamptz
);
create index if not exists hub_material_precos_material_ci on public.hub_material_precos (material_id);
create index if not exists hub_material_precos_fornecedor_ci on public.hub_material_precos (fornecedor_id);

create table if not exists public.hub_material_precos_historico (
  id uuid primary key,
  preco_id uuid references public.hub_material_precos(id) on delete cascade,
  preco numeric,
  desconto numeric,
  iva numeric,
  unidade text,
  data_atualizacao date,
  registado_em timestamptz
);
create index if not exists hub_material_precos_historico_preco_ci on public.hub_material_precos_historico (preco_id);

-- só leitura: quem pode ver o Design vê; ninguém (a não ser o Hub, com a chave de serviço) escreve
do $$
declare t text;
begin
  foreach t in array array['hub_fornecedores', 'hub_materiais', 'hub_material_precos', 'hub_material_precos_historico'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists "Ver" on public.%I', t);
    execute format('create policy "Ver" on public.%I for select to authenticated using ((select public.pode_ver()))', t);
    execute format('revoke insert, update, delete, truncate on public.%I from anon, authenticated', t);
    execute format('revoke all on public.%I from anon', t);
  end loop;
end $$;
