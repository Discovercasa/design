-- 0027 (2026-11-21): o hub segue a barra de navegação. O utilizador: «No hub quero que coloques a orçamentação e os
-- materiais como abas do gerador de documentos e que movas a aba das Páginas de dentro do builder para a nav-bar
-- inicial, não te esqueças de ajustar tudo o que o HUB tem interligado entre setores, por exemplo nas sugestões e
-- criticas mudares o que está lá para ficar ajustado aos projetos que temos na nav-bar».
--   * Páginas passa a projeto da barra (id 'paginas'). Vai para lá o que era a aba Páginas do Builder: os seus
--     checkpoints (agora o Workflow das Páginas), as tarefas, decisões, notas, imagens, conversas, notificações e linhas
--     do Log ligadas a eles, as páginas dos clientes e as obras (documentos e documentos_seccoes do tipo 'pagina') e as
--     críticas sobre as páginas. Os ficheiros ficam onde estão no armazenamento (o caminho não muda).
--   * A Orçamentação passa a aba do Gerador de documentos: os seus checkpoints vão para o Gerador com aba
--     'orcamentacao' (o workflow dessa aba) e tudo o resto do projeto vai com eles. A linha 'orcamentacao' da tabela
--     projetos fica (a «App sugerida» de duas tarefas e a aplicação em /orcamentacao/); o hub já não a mostra.
--   * Materiais (só de consulta, tabelas hub_*) passa a aba do Gerador: nada muda na base de dados.
--   * Sugestões: «Sobre» segue a barra (sem Orçamentação; com Páginas e Redes sociais).
-- Alguns gatilhos BEFORE UPDATE mantêm o projeto de uma linha (criticas, documentos_seccoes, anexos): desligam-se só
-- durante a mudança e voltam a ligar-se logo a seguir.

insert into public.projetos (id, nome, ordem) values ('paginas', 'Páginas', 6) on conflict (id) do nothing;

alter table public.checkpoints drop constraint if exists checkpoints_aba_check;
alter table public.checkpoints add constraint checkpoints_aba_check check (aba is null or aba in ('paginas', 'orcamentacao'));

-- ---------------------------------------------------------------- o que muda de sítio
create temporary table _cp on commit drop as
  select id, case when projeto = 'builder' then 'paginas' else 'gerador' end as para from public.checkpoints
  where (projeto = 'builder' and aba = 'paginas') or projeto = 'orcamentacao';
create temporary table _t on commit drop as
  select t.id, c.para from public.tarefas t join _cp c on c.id = t.checkpoint_id;
create temporary table _n on commit drop as
  select n.id, t.para from public.tarefas_notas n join _t t on t.id = n.tarefa_id;
create temporary table _dec on commit drop as
  select d.id, t.para from public.decisoes d join _t t on t.id = d.tarefa_id
  union select d.id, 'gerador' from public.decisoes d where d.projeto = 'orcamentacao';
create temporary table _doc on commit drop as
  select id, case when projeto = 'builder' then 'paginas' else 'gerador' end as para from public.documentos
  where (projeto = 'builder' and tipo = 'pagina') or projeto = 'orcamentacao';
create temporary table _sec on commit drop as
  select id, case when projeto = 'builder' then 'paginas' else 'gerador' end as para from public.documentos_seccoes
  where (projeto = 'builder' and tipo = 'pagina') or projeto = 'orcamentacao';
create temporary table _cr on commit drop as
  select id, case when projeto = 'builder' then 'paginas' else 'gerador' end as para from public.criticas
  where (projeto = 'builder' and onde ~* 'p[áa]gina') or projeto = 'orcamentacao';

-- ---------------------------------------------------------------- checkpoints (a aba), tarefas, notas, decisões
-- (os da Orçamentação ficam depois dos do Gerador na ordem do projeto: + 100; as posições contam-se em cada aba)
update public.checkpoints c set projeto = x.para, aba = case when x.para = 'gerador' then 'orcamentacao' end,
  ordem = case when x.para = 'gerador' then c.ordem + 100 else c.ordem end
  from _cp x where x.id = c.id;
update public.tarefas t set projeto = x.para from _t x where x.id = t.id;          -- tarefas_antes: o do checkpoint
update public.tarefas_notas n set projeto = x.para from _n x where x.id = n.id;    -- idem: o da tarefa
update public.decisoes d set projeto = x.para from _dec x where x.id = d.id;

-- imagens (o gatilho mantém o projeto)
alter table public.anexos disable trigger anexos_antes;
update public.anexos a set projeto = x.para from _cp x where a.alvo = 'checkpoint' and a.ref_id = x.id;
update public.anexos a set projeto = x.para from _t x where a.alvo = 'tarefa' and a.ref_id = x.id;
update public.anexos a set projeto = x.para from _n x where a.alvo = 'nota' and a.ref_id = x.id;
alter table public.anexos enable trigger anexos_antes;

-- conversas das tarefas e dos checkpoints
update public.atividade a set projeto = x.para from _cp x where a.alvo = 'checkpoint' and a.ref_id = x.id;
update public.atividade a set projeto = x.para from _t x where a.alvo = 'tarefa' and a.ref_id = x.id;
update public.atividade set projeto = 'gerador' where projeto = 'orcamentacao';

-- ---------------------------------------------------------------- documentos: as obras primeiro (o gatilho dos
-- documentos exige que a secção seja do mesmo projeto e tipo)
alter table public.documentos_seccoes disable trigger documentos_seccoes_antes;
update public.documentos_seccoes s set projeto = x.para from _sec x where x.id = s.id;
alter table public.documentos_seccoes enable trigger documentos_seccoes_antes;
update public.documentos d set projeto = x.para from _doc x where x.id = d.id;

-- ---------------------------------------------------------------- críticas (o gatilho mantém o projeto)
alter table public.criticas disable trigger criticas_antes;
update public.criticas c set projeto = x.para from _cr x where x.id = c.id;
alter table public.criticas enable trigger criticas_antes;

-- ---------------------------------------------------------------- notificações e Log: os que apontam para o que mudou
update public.notificacoes n set projeto = x.para from _cp x where n.ref_tipo = 'checkpoint' and n.ref_id = x.id;
update public.notificacoes n set projeto = x.para from _t x where n.ref_tipo = 'tarefa' and n.ref_id = x.id;
update public.notificacoes n set projeto = x.para from _dec x where n.ref_tipo = 'decisao' and n.ref_id = x.id;
update public.notificacoes n set projeto = x.para from _doc x where n.ref_tipo = 'documento' and n.ref_id = x.id;
update public.notificacoes n set projeto = x.para from _cr x where n.ref_tipo = 'critica' and n.ref_id = x.id;
update public.notificacoes set projeto = 'gerador' where projeto = 'orcamentacao';
update public.registo r set projeto = x.para from _cp x where r.ref_tipo = 'checkpoint' and r.ref_id = x.id;
update public.registo r set projeto = x.para from _t x where r.ref_tipo = 'tarefa' and r.ref_id = x.id;
update public.registo r set projeto = x.para from _dec x where r.ref_tipo = 'decisao' and r.ref_id = x.id;
update public.registo r set projeto = x.para from _doc x where r.ref_tipo = 'documento' and r.ref_id = x.id;
update public.registo r set projeto = x.para from _cr x where r.ref_tipo = 'critica' and r.ref_id = x.id;
update public.registo set projeto = 'gerador' where projeto = 'orcamentacao';

-- ---------------------------------------------------------------- sugestões: «Sobre» = a barra de navegação
alter table public.sugestoes drop constraint if exists sugestoes_ferramenta_check;
update public.sugestoes set ferramenta = 'gerador' where ferramenta = 'orcamentacao';
alter table public.sugestoes add constraint sugestoes_ferramenta_check
  check (ferramenta in ('geral', 'gerador', 'builder', 'build_your_house', 'plataforma_cliente', 'paginas', 'social'));
