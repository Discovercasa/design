-- Páginas (2026-11-12): «Dentro do projeto do Builder cria uma aba que vai ter as nossas páginas ... Quero também que
-- cries tarefas e checkpoints nessa aba». A aba «Páginas» de um projeto (o JSON do projeto diz "paginas": true) tem:
--   - as páginas entregues aos clientes: documentos do tipo 'pagina' (um ficheiro HTML com tudo lá dentro), no
--     armazenamento privado "documentos" em <projeto>/pagina/<nome>; nunca no Git (são casas de clientes);
--   - os seus checkpoints e tarefas: checkpoints.aba = 'paginas' (sem aba = o Workflow).
alter table public.checkpoints add column if not exists aba text check (aba is null or aba in ('paginas'));

alter table public.documentos drop constraint if exists documentos_tipo_check;
alter table public.documentos add constraint documentos_tipo_check check (tipo in ('informativo', 'adicional', 'ar', 'pagina'));
alter table public.documentos drop constraint if exists documentos_caminho_check;
alter table public.documentos add constraint documentos_caminho_check check (caminho ~ '^[a-z_]+/(informativo|adicional|ar|pagina)/[^/]+$');

-- the notification / Log line says what kind of document it is
create or replace function public.documentos_depois() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if new.lote is not null then
    return null;
  end if;
  perform public.notificar(new.projeto, 'documento_novo', public.nome_atual() || ' acrescentou '
    || case when new.tipo = 'pagina' then 'a página «' || new.titulo || '»'
            else 'o documento «' || new.titulo || '»' || case when new.tipo = 'informativo' then ' (informativo)'
                                                              when new.tipo = 'ar' then ' (modelo AR)' else ' (adicional)' end end,
    'documento', new.id);
  return null;
end $$;
revoke execute on function public.documentos_depois() from public, anon, authenticated;
