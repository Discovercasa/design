-- Conteúdo (2026-11-06), depois de 0011. Do documento de hierarquia e roadmap (aceite com as nossas reservas):
-- Builder · checkpoint para os defeitos geométricos conhecidos (avança sem a listagem de Torres Vedras); Gerador · política
-- de libertação dos documentos; Orçamentação · modelo de dados com dados de teste e códigos de produto estáveis; 3 decisões
-- novas; critério de saída nos checkpoints; Fase 0 conjunta do Build Your House e do Step Inside.
-- Do pedido do utilizador: tarefas de teste/revisão marcadas e as notas do teste do configurador passadas a lista.

create function pg_temp.abrir(p text, a_partir int) returns void language sql as $$
  update public.checkpoints set ordem = ordem + 1 where projeto = p and ordem >= a_partir
$$;
create function pg_temp.cp(p text, titulo text, descricao text, ordem int) returns bigint language plpgsql as $$
declare i bigint;
begin
  insert into public.checkpoints (projeto, titulo, descricao, ordem, estado, criado_por_nome)
  values (p, titulo, descricao, ordem, 'por_fazer', 'Equipa') returning id into i;
  return i;
end $$;
create function pg_temp.cpx(p text, titulo_ text) returns bigint language plpgsql as $$
declare i bigint;
begin
  select id into i from public.checkpoints where projeto = p and titulo = titulo_;
  if i is null then raise exception 'Checkpoint «%» não encontrado em %', titulo_, p; end if;
  return i;
end $$;
create function pg_temp.tf(c bigint, titulo text, app text default null, custo text default '', descricao text default '')
returns bigint language plpgsql as $$
declare i bigint; o int;
begin
  select coalesce(max(t.ordem), 0) + 1 into o from public.tarefas t where t.checkpoint_id = c;
  insert into public.tarefas (checkpoint_id, projeto, titulo, estado, app_sugerida, custo, descricao, ordem, criado_por_nome)
  values (c, (select projeto from public.checkpoints where id = c), titulo, 'por_fazer', app, custo, descricao, o, 'Equipa')
  returning id into i;
  return i;
end $$;
create function pg_temp.tx(p text, titulo_ text) returns bigint language plpgsql as $$
declare i bigint;
begin
  select id into i from public.tarefas where projeto = p and titulo = titulo_ order by id limit 1;
  if i is null then raise exception 'Tarefa «%» não encontrada em %', titulo_, p; end if;
  return i;
end $$;
create function pg_temp.dc(p text, tarefa bigint, pergunta text, contexto text) returns bigint language plpgsql as $$
declare i bigint;
begin
  insert into public.decisoes (projeto, tarefa_id, pergunta, contexto, criado_por_nome)
  values (p, tarefa, pergunta, contexto, 'Equipa') returning id into i;
  return i;
end $$;
create function pg_temp.op(d bigint, titulo text, vantagens text, desvantagens text, custo text default '')
returns void language plpgsql as $$
begin
  insert into public.decisoes_opcoes (decisao_id, titulo, vantagens, desvantagens, custo, ordem)
  values (d, titulo, vantagens, desvantagens, custo, (select coalesce(max(ordem), 0) + 1 from public.decisoes_opcoes where decisao_id = d));
end $$;
create function pg_temp.crit(c bigint, texto text) returns void language sql as $$
  update public.checkpoints set criterio_saida = texto where id = c
$$;
create function pg_temp.desc_cp(c bigint, texto text) returns void language sql as $$
  update public.checkpoints set descricao = texto where id = c
$$;
create function pg_temp.desc_t(t bigint, texto text) returns void language sql as $$
  update public.tarefas set descricao = texto where id = t
$$;
create function pg_temp.rev(t bigint) returns void language sql as $$
  update public.tarefas set revisao = true where id = t
$$;
-- nota escrita por quem fez o teste (a primeira pessoa que mexeu na tarefa no hub); sem ninguém, fica "Equipa"
create function pg_temp.nota(t bigint, tipo text, texto text) returns void language plpgsql as $$
declare a uuid;
begin
  select n.ator_id into a from public.notificacoes n where n.ref_tipo = 'tarefa' and n.ref_id = t and n.ator_id is not null
    order by n.criada_em limit 1;
  insert into public.tarefas_notas (tarefa_id, projeto, tipo, texto, autor_id, autor_nome)
  values (t, (select projeto from public.tarefas where id = t), tipo, texto, a,
          coalesce((select nullif(p.nome, '') from public.perfis p where p.id = a), 'Equipa'));
end $$;

do $$
declare c bigint; t bigint; d bigint;
begin
  -- ------------------------------------------------------------ Builder: defeitos geométricos conhecidos (posição 4)
  perform pg_temp.abrir('builder', 4);
  c := pg_temp.cp('builder', 'Corrigir defeitos geométricos conhecidos',
    'Os problemas que a verificação das madeiras encontrou em Torres Vedras. Avança já, sem esperar pela listagem real de materiais.', 4);
  perform pg_temp.tf(c, 'Regra de encontro do anel de amarração nos cantos e nos T');
  perform pg_temp.tf(c, 'Comprimento dos montantes por cima das vergas');
  perform pg_temp.tf(c, 'Sobreposições dos prumos em pares');
  perform pg_temp.tf(c, 'Sobreposição dos módulos interiores');
  perform pg_temp.tf(c, 'Completar a verificação da cobertura oculta');
  perform pg_temp.tf(c, 'Completar a verificação de paredes e módulos');
  perform pg_temp.tf(c, 'Tolerâncias por tipo de ligação, folga e peça');
  perform pg_temp.tf(c, 'Testes de referência a cada mudança do motor', 'gerador', '',
    'Torres Vedras, uma casa regular, uma em L, uma em U/T, cobertura oculta, cobertura à vista e um caso com pérgola. O Gerador volta a gerar os documentos de referência.');
  perform pg_temp.crit(c, 'Os testes de referência passam sem colisões não intencionais; as sobreposições intencionais estão documentadas; a lista de corte bate com a geometria.');

  -- ------------------------------------------------------------ Gerador: política de libertação (posição 4)
  perform pg_temp.abrir('gerador', 4);
  c := pg_temp.cp('gerador', 'Política de libertação dos documentos',
    'Um rascunho nunca se pode confundir com um documento validado para produção.', 4);
  perform pg_temp.tf(c, 'Separar erros bloqueantes, avisos e informação em falta');
  perform pg_temp.tf(c, 'Marcar os documentos com erros bloqueantes: «COM PROBLEMAS — NÃO UTILIZAR EM FÁBRICA»');
  perform pg_temp.tf(c, 'Rascunho só com a marca inequívoca de não aprovado');
  perform pg_temp.tf(c, 'Exceções só com aprovação e motivo registados');
  perform pg_temp.tf(c, 'Guardar com cada documento a versão do motor, os dados de entrada e o relatório de verificação');
  perform pg_temp.crit(c, 'Não é possível confundir um documento de rascunho com um documento validado para produção.');

  -- ------------------------------------------------------------ Orçamentação: começar sem esperar pelos preços reais
  c := pg_temp.cpx('orcamentacao', 'Lista de materiais e fornecedores');
  perform pg_temp.tf(c, 'Modelo de dados do catálogo (códigos, unidades, fornecedores, validade) com dados de teste', null, '',
    'Pode começar já. Os dados de teste ficam marcados como teste e nunca aparecem como preços reais.');
  perform pg_temp.tf(c, 'Códigos de produto estáveis em cada linha da Listagem de material', 'gerador', '',
    'A ligação entre a Listagem e a lista de preços faz-se pelo código, não pelo nome.');
  c := pg_temp.cpx('orcamentacao', 'Composição do preço final');
  perform pg_temp.tf(c, 'Aceitar também listas de quantidades manuais ou importadas (CSV / Excel)', null, '',
    'A Orçamentação não depende só do Gerador: serve obras antigas e orçamentos rápidos.');

  -- ------------------------------------------------------------ decisões novas
  d := pg_temp.dc('build_your_house', null, 'Vendemos o Build Your House e o Step Inside a outras empresas? Quando?',
    'O documento de hierarquia (2026-11-06) desenha tudo para terceiros: várias organizações, isolamento entre clientes, métodos construtivos de outras empresas. As contas do Design vêm do Hub, por isso vender a terceiros obriga a repensar a entrada. Até decidir, não se constrói para terceiros, mas também não se fecham portas.');
  perform pg_temp.op(d, 'Só uso interno por agora', 'Sem trabalho extra; foco em abrir aos nossos clientes.', 'Decidir mais tarde pode obrigar a adaptar dados e contas.', '0 €');
  perform pg_temp.op(d, 'Primeiro o Build Your House a terceiros', 'É o produto mais avançado; receita mais cedo.', 'Exige contas próprias fora do Hub, isolamento por empresa, termos e preços por cliente.', 'Desenvolvimento a estimar');
  perform pg_temp.op(d, 'Os dois, com plataforma para várias organizações', 'Uma base comum para vender os dois.', 'Meses de infraestrutura antes de ter clientes externos.', 'Desenvolvimento a estimar; plano Supabase pago provável');

  d := pg_temp.dc('builder', null, 'Que contrato de dados fazemos já entre as aplicações?',
    'O documento de hierarquia propõe um Contrato de Intercâmbio com 9 módulos. Hoje há dois consumidores reais: a casa configurada → Builder e a Listagem de material → Orçamentação.');
  perform pg_temp.op(d, 'Mínimo: arquitetura e quantidades agora; o resto quando houver um segundo consumidor', 'Rápido; responde ao que já é preciso.', 'Os outros módulos ficam por definir.', 'Pouco tempo de desenvolvimento');
  perform pg_temp.op(d, 'Completo já (os 9 módulos)', 'Tudo pensado de uma vez.', 'Muito trabalho antes de haver valor visível; partes podem mudar antes de serem usadas.', 'Semanas a meses de desenvolvimento');

  d := pg_temp.dc('orcamentacao', null, 'Quem mantém os códigos de produto usados pela Listagem e pelos preços?',
    'A Listagem de material (Builder/Gerador) e a lista de preços (Orçamentação) têm de falar dos mesmos produtos.');
  perform pg_temp.op(d, 'A Orçamentação (catálogo); o Builder liga os seus materiais por uma tabela de correspondência', 'Um só dono dos códigos; os preços continuam só na Orçamentação.', 'Mais uma tabela a manter quando entra um material novo.', '');
  perform pg_temp.op(d, 'O Builder define os códigos e a Orçamentação segue-os', 'Os códigos nascem com os materiais do método.', 'Mistura dados comerciais com o método construtivo.', '');
  perform pg_temp.op(d, 'Lista mantida à mão pela equipa', 'Simples no início.', 'Erros e duplicados com o tempo.', '');

  -- ------------------------------------------------------------ Fase 0 conjunta e Step Inside sem depender do Blender
  c := pg_temp.cpx('build_your_house', 'Fase 0 · Auditoria para Smart Land, Interiores e Conformidade');
  perform pg_temp.desc_cp(c, 'Antes de qualquer código: conhecer o configurador, o motor 3D, o Supabase e a Cloudflare e escrever o plano de integração. Nenhum código existente muda. Feita em conjunto com a Fase 0 do Step Inside: um só relatório da infraestrutura, com uma secção por aplicação.');
  perform pg_temp.crit(c, 'Arquitetura atual documentada e plano de integração aprovado, sem alterações destrutivas.');
  c := pg_temp.cpx('plataforma_cliente', 'Fase 0 · Auditoria do sistema atual');
  perform pg_temp.desc_cp(c, 'Conhecer o hub, a Cloudflare, o Supabase e a pipeline Blender antes de escrever código. Feita em conjunto com a Fase 0 do Build Your House: um só relatório da infraestrutura, com uma secção por aplicação. Sem alterações de produção e sem despesas.');
  perform pg_temp.crit(c, 'Relatório da arquitetura atual, sem alterações de produção e sem despesas.');
  c := pg_temp.cpx('plataforma_cliente', 'Fase 2 · Modelo Blender e terreno');
  perform pg_temp.desc_cp(c, 'Nas obras Discovercasa parte-se do modelo do Builder; aceita também modelos e documentos de outros arquitetos e construtores. O ficheiro Blender é uma saída editável: a verdade é o modelo estruturado, com IDs, medidas e origem. Terreno rigoroso só com levantamento (o terreno vem do Smart Land).');

  -- ------------------------------------------------------------ critérios de saída
  perform pg_temp.crit(pg_temp.cpx('build_your_house', 'Respostas pendentes'), 'Decisões que mudam a geometria registadas; teste da equipa concluído; bugs críticos resolvidos ou aceites.');
  perform pg_temp.crit(pg_temp.cpx('build_your_house', 'Preços reais'), 'Nenhum preço provisório aparece como real; cada preço mostra a versão e a data.');
  perform pg_temp.crit(pg_temp.cpx('build_your_house', 'Pronto para clientes'), 'Testado em telemóvel e tablet; aprovação formal da Discovercasa; termos e permissões revistos.');
  perform pg_temp.crit(pg_temp.cpx('builder', 'Validação com os materiais reais'), 'Tolerância de erro definida por família de material; as diferenças fora da tolerância estão explicadas, corrigidas ou aceites.');
  perform pg_temp.crit(pg_temp.cpx('gerador', 'Revisão da Discovercasa'), 'Módulos, Cobertura e Listagem de material aprovados e testados contra o Builder e uma obra de referência.');
  perform pg_temp.crit(pg_temp.cpx('gerador', 'Mais formatos de entrada'), 'Matriz de formatos publicada; testes com ficheiros válidos, ambíguos e inválidos.');
  perform pg_temp.crit(pg_temp.cpx('orcamentacao', 'Lista de materiais e fornecedores'), 'Cada linha com preço tem código, unidade e fonte do preço; as exceções estão à vista.');
  perform pg_temp.crit(pg_temp.cpx('orcamentacao', 'Composição do preço final'), 'Orçamento reproduzível e comparável entre revisões, com as contas à vista.');
  perform pg_temp.crit(pg_temp.cpx('plataforma_cliente', 'Fase 1 · Contrato de dados e qualidade de entrada'), 'Nenhum dado inferido aparece como confirmado; NEEDS_HUMAN_REVIEW trava o que depende dele.');
  perform pg_temp.crit(pg_temp.cpx('plataforma_cliente', 'Fase 2 · Modelo Blender e terreno'), 'Um projeto de outro arquiteto e um projeto Discovercasa preparados para a visita.');
  perform pg_temp.crit(pg_temp.cpx('plataforma_cliente', 'Fase 3 · Materiais e exportação'), 'Exportação reproduzível, sem perder os IDs e as relações.');
  perform pg_temp.crit(pg_temp.cpx('plataforma_cliente', 'Fase 4 · Unreal Viewer e aprovação visual'), 'Casa de referência aprovada, desempenho medido e custo do build conhecido.');
  perform pg_temp.crit(pg_temp.cpx('plataforma_cliente', 'Fase 5 · Prova de conceito Pixel Streaming'), 'Custo completo por sessão e capacidade por GPU medidos, antes de prometer o serviço.');
  perform pg_temp.crit(pg_temp.cpx('plataforma_cliente', 'Fase 6 · Ligar Cloudflare, Supabase e R2'), 'Um cliente nunca abre o projeto de outro (testado); backups e restauração testados.');
  perform pg_temp.crit(pg_temp.cpx('plataforma_cliente', 'Fase 7 · AR no telemóvel'), 'Escala, ancoragem, materiais e desempenho aceitáveis nos telemóveis de teste.');
  perform pg_temp.crit(pg_temp.cpx('plataforma_cliente', 'Fase 8 · Prova de conceito VR'), 'Prova real com pessoas e critérios de conforto atingidos (não basta aparecer imagem no headset).');
  perform pg_temp.crit(pg_temp.cpx('plataforma_cliente', 'Fase 9 · Produção e escala'), 'Operação segura e auditável, com custos por casa e por sessão conhecidos.');

  -- ------------------------------------------------------------ tarefas de teste ou revisão
  perform pg_temp.rev(pg_temp.tx('build_your_house', 'Teste completo do configurador pela equipa, com comentários'));
  perform pg_temp.rev(pg_temp.tx('build_your_house', 'Testar em telemóvel e tablet'));
  perform pg_temp.rev(pg_temp.tx('build_your_house', 'Aprovação da Discovercasa antes de abrir a clientes'));
  perform pg_temp.rev(pg_temp.tx('build_your_house', 'Validar o plano com a Discovercasa antes da Fase 1'));
  perform pg_temp.rev(pg_temp.tx('gerador', 'Rever o documento Cobertura'));
  perform pg_temp.rev(pg_temp.tx('gerador', 'Rever a Listagem de material'));
  perform pg_temp.rev(pg_temp.tx('builder', 'Comparar as quantidades do modelo com as reais'));
  perform pg_temp.rev(pg_temp.tx('plataforma_cliente', 'Aprovação visual da Discovercasa (imagens, FPS, métricas)'));
  perform pg_temp.rev(pg_temp.tx('plataforma_cliente', 'Testar em pelo menos um iPhone e um Android reais'));
  perform pg_temp.rev(pg_temp.tx('plataforma_cliente', 'Testes com clientes internos e externos controlados'));

  -- ------------------------------------------------------------ o teste do configurador: da descrição para a lista
  t := pg_temp.tx('build_your_house', 'Teste completo do configurador pela equipa, com comentários');
  perform pg_temp.nota(t, 'bug', 'Quando se muda os revestimentos exteriores e a casa tem cobertura oculta, a parte interior da platibanda que também tem revestimento não atualiza para dar match ao revestimento exterior e tem de o fazer porque se a casa for de capoto o revestimento do interior da platibanda que fica à mostra também é de capoto.');
  perform pg_temp.nota(t, 'bug', 'Outro Bug é relativo as coberturas que podes já tirar mesmo antes de eu te dar a informação toda sobre as coberturas. Quando é sem ser oculta estas a colocar uma peça de metal ou da cor do telhado a acompanhar as testeiras dos triângulos e isso não acontece.');
  perform pg_temp.desc_t(t, 'Cada problema encontrado no teste fica na lista de notas: bug, a mudar ou a fazer.');
end $$;
