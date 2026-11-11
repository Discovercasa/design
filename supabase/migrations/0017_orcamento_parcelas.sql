-- Design — Orçamentação: as parcelas do preço final (tarefas 42, 43 e 44 do hub, 2026-11-11).
-- O utilizador (2026-10-20): «O preço vamos definir baseado em materiais, mão de obra, fundação, caixilharia,
-- especialidades, instalações e pré-instalações, licenciamento e IVA.» Cada parcela diz COMO se calcula (método, base)
-- e o VALOR (taxa, €/m², % ou valor fixo). Os valores da empresa (mão de obra, margem…) ficam só aqui, atrás da regra
-- "Ver" — nunca no repositório, que é público. valor null = ainda não fornecido: o preço final fica "incompleto".
-- Vê quem pode ver o Design; muda quem pode editar (página /orcamentacao/). Não se criam nem apagam parcelas na página.

create table if not exists public.orcamento_parcelas (
  id text primary key,
  nome text not null,
  ordem int not null default 0,
  -- materiais_hub: a soma da Listagem com os preços do Hub (automática)
  -- por_m2: valor €/m² x a área da base escolhida; percentagem_materiais: valor % dos materiais;
  -- valor_fixo: valor €; percentagem_subtotal: valor % da soma das parcelas anteriores (margem); taxa_iva: valor %
  metodo text not null check (metodo in ('materiais_hub', 'por_m2', 'percentagem_materiais', 'valor_fixo', 'percentagem_subtotal', 'taxa_iva')),
  base text check (base in ('construcao', 'implantacao', 'vaos')),
  valor numeric check (valor is null or valor >= 0),
  nota text not null default '',
  atualizado_por_nome text not null default '',
  atualizado_em timestamptz not null default now()
);
alter table public.orcamento_parcelas enable row level security;
create policy "Ver" on public.orcamento_parcelas for select to authenticated using ((select public.pode_ver()));
create policy "Editar" on public.orcamento_parcelas for update to authenticated
  using ((select public.pode_editar())) with check ((select public.pode_editar()));

create or replace function public.orcamento_parcelas_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  new.id := old.id; new.ordem := old.ordem;   -- a página muda só o método, a base, o valor e a nota
  if old.metodo = 'materiais_hub' then new.metodo := old.metodo; new.valor := null; end if;
  if old.metodo = 'taxa_iva' then new.metodo := old.metodo; end if;
  if new.metodo <> 'por_m2' then new.base := null; elsif new.base is null then new.base := 'construcao'; end if;
  new.atualizado_por_nome := public.nome_atual(); new.atualizado_em := now();
  return new;
end $$;
drop trigger if exists orcamento_parcelas_antes on public.orcamento_parcelas;
create trigger orcamento_parcelas_antes before update on public.orcamento_parcelas
  for each row execute function public.orcamento_parcelas_antes();
revoke execute on function public.orcamento_parcelas_antes() from public, anon, authenticated;

-- the parcels the user listed + the margin (not said: to confirm). Methods proposed by Claude; every value to give.
insert into public.orcamento_parcelas (id, nome, ordem, metodo, base, nota, atualizado_por_nome) values
  ('materiais', 'Materiais', 1, 'materiais_hub', null, 'Da Listagem de material com os preços da lista do Hub. Os produtos que não estão na lista do Hub ainda não entram.', 'Claude'),
  ('caixilharia', 'Caixilharia', 2, 'por_m2', 'vaos', 'Janelas, portas exteriores, portão, vidros e estores: não estão na lista do Hub. Proposta: € por m² de vão.', 'Claude'),
  ('fundacao', 'Fundação', 3, 'por_m2', 'implantacao', 'Base de fundação. Proposta: € por m² de área de implantação.', 'Claude'),
  ('mao_de_obra', 'Mão de obra', 4, 'por_m2', 'construcao', 'Fábrica (módulos) e montagem em obra. Proposta: € por m² de área de construção.', 'Claude'),
  ('especialidades', 'Especialidades', 5, 'valor_fixo', null, 'Projetos de especialidades. Proposta: valor fixo por obra.', 'Claude'),
  ('instalacoes', 'Instalações e pré-instalações', 6, 'por_m2', 'construcao', 'Eletricidade, águas e esgotos, pré-instalações (AC, bomba de calor). Proposta: € por m² de área de construção.', 'Claude'),
  ('licenciamento', 'Licenciamento', 7, 'valor_fixo', null, 'Taxas e processo na câmara. Proposta: valor fixo por obra.', 'Claude'),
  ('margem', 'Margem', 8, 'percentagem_subtotal', null, 'Não foi dita: confirmar se há uma margem à parte ou se já está dentro das outras parcelas (então fica 0).', 'Claude'),
  ('iva', 'IVA', 9, 'taxa_iva', null, '23 % (taxa normal) ou 6 % (empreitada de habitação própria e permanente ou para arrendamento, DL 97/2026, verba 2.42 da lista I do CIVA, obras iniciadas até 31/12/2029, com limite de valor): a confirmar com a contabilidade.', 'Claude')
on conflict (id) do nothing;
