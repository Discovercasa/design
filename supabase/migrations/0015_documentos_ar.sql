-- Step Inside (2026-11-09): "adiciona uma secção de teste onde tem essas componentes" — the AR models (USDZ for
-- iPhone Quick Look, GLB for Android Scene Viewer) are project documents of a third kind, 'ar', shown in their own
-- "Teste do AR" section with buttons that open the phone's AR viewer. Same private bucket and the same RLS as the
-- other documents (see 0006): only who sees the Design opens them, by a signed, temporary URL.
alter table public.documentos drop constraint documentos_tipo_check;
alter table public.documentos add constraint documentos_tipo_check check (tipo in ('informativo', 'adicional', 'ar'));
alter table public.documentos drop constraint documentos_caminho_check;
alter table public.documentos add constraint documentos_caminho_check
  check (caminho ~ '^[a-z_]+/(informativo|adicional|ar)/[^/]+$');
