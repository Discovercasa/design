-- Design — correção da 0022: nas funções do ponto de situação a variável «titulo» tinha o nome de uma coluna
-- (PostgreSQL: «column reference titulo is ambiguous»). Passa a chamar-se «tit».
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

