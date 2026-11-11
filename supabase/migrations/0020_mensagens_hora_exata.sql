-- Design — chat: cada mensagem com a hora exata em que entra (clock_timestamp), não a hora do início da transação.
-- Várias mensagens escritas de seguida pelo Claude (numa só ligação à base) ficavam com a mesma hora e podiam aparecer
-- por outra ordem. Igual à 0018 em tudo o resto.
create or replace function public.mensagens_antes() returns trigger language plpgsql security definer set search_path = '' as $$
declare a jsonb;
begin
  new.criada_em := clock_timestamp();
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
revoke execute on function public.mensagens_antes() from public, anon, authenticated;
