-- Páginas por obra (2026-11-19). O utilizador: «Na Aba das páginas dentro do builder e dentro da secção das páginas cria
-- Collapsables onde cada projeto tem as suas páginas». Cada obra (uma casa) é uma secção dos documentos
-- (documentos_seccoes, migração 0024) do tipo 'pagina'; as páginas ficam nela por documentos.seccao_id (o trigger
-- documentos_antes já exige que a secção seja do mesmo projeto e tipo).
alter table public.documentos_seccoes drop constraint if exists documentos_seccoes_tipo_check;
alter table public.documentos_seccoes add constraint documentos_seccoes_tipo_check
  check (tipo in ('informativo', 'adicional', 'pagina'));
