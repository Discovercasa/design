-- Design — notificações sobre sugestões e o chat (2026-11-11): «sugestao_estado» (uma sugestão concluída, por exemplo pelo
-- Claude) e «chat» (uma mensagem que pede atenção, como as perguntas do Claude). ref_tipo 'sugestao' abre a gaveta das
-- Sugestões; ref_tipo 'conversa' abre o chat (ref_id = a conversa, ou nada para a lista).
alter table public.notificacoes drop constraint notificacoes_tipo_check;
alter table public.notificacoes add constraint notificacoes_tipo_check check (tipo in (
  'tarefa_nova', 'tarefa_atribuida', 'tarefa_estado', 'tarefa_concluida', 'checkpoint_novo', 'checkpoint_estado',
  'checkpoint_concluido', 'decisao_nova', 'decisao_tomada', 'decisao_opcao', 'documento_novo', 'post_novo', 'post_estado',
  'post_aprovacao', 'post_comentario', 'obra_nova', 'fase_nova', 'fase_estado', 'nota_nova', 'nota_resolvida',
  'sugestao_estado', 'chat'));
