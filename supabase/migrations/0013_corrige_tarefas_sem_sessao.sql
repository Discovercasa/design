-- Correção (2026-11-07): a regra "quem só vê muda apenas o estado da sua tarefa" (tarefas_antes) também se aplicava às
-- migrações, que correm sem sessão; por isso a 0012 não conseguiu marcar as tarefas de teste/revisão nem mudar a
-- descrição do teste do configurador. A regra passa a valer só para pessoas com sessão; e repetem-se essas mudanças.

create or replace function public.tarefas_antes() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    if (select auth.uid()) is not null then
      new.criado_por := (select auth.uid()); new.criado_por_nome := public.nome_atual(); new.criado_em := now();
    end if;
    if new.estado = 'concluida' and new.concluida_em is null then new.concluida_em := current_date; end if;
  else
    if (select auth.uid()) is not null and not public.pode_editar() then   -- o responsável que só vê: muda apenas o estado
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

update public.tarefas set revisao = true where (projeto, titulo) in (
  ('build_your_house', 'Teste completo do configurador pela equipa, com comentários'),
  ('build_your_house', 'Testar em telemóvel e tablet'),
  ('build_your_house', 'Aprovação da Discovercasa antes de abrir a clientes'),
  ('build_your_house', 'Validar o plano com a Discovercasa antes da Fase 1'),
  ('gerador', 'Rever o documento Cobertura'),
  ('gerador', 'Rever a Listagem de material'),
  ('builder', 'Comparar as quantidades do modelo com as reais'),
  ('plataforma_cliente', 'Aprovação visual da Discovercasa (imagens, FPS, métricas)'),
  ('plataforma_cliente', 'Testar em pelo menos um iPhone e um Android reais'),
  ('plataforma_cliente', 'Testes com clientes internos e externos controlados'));

update public.tarefas set descricao = 'Cada problema encontrado no teste fica na lista de notas: bug, a mudar ou a fazer.'
  where projeto = 'build_your_house' and titulo = 'Teste completo do configurador pela equipa, com comentários';
