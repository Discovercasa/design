-- Conteúdo inicial do hub (2026-11-05): checkpoints, tarefas e decisões de cada projeto, tirados do histórico do BOB
-- (datas reais de cada entrega, só o dia) e, para o Step Inside, da especificação técnica de 2026-11-05 (fases 0–9,
-- decisões do §16.1, custos dos §15 e §20; câmbio 1 USD = 0,89131 EUR). Sem sessão: não gera notificações.
-- Corre uma vez, depois de 0004.

create function pg_temp.cp(p text, titulo text, descricao text, ordem int, estado text, dia date default null)
returns bigint language plpgsql as $$
declare i bigint;
begin
  insert into public.checkpoints (projeto, titulo, descricao, ordem, estado, concluido_em, criado_por_nome)
  values (p, titulo, descricao, ordem, estado, dia, 'Equipa') returning id into i;
  return i;
end $$;

create function pg_temp.tf(c bigint, titulo text, estado text default 'por_fazer', dia date default null,
                           app text default null, custo text default '', descricao text default '')
returns bigint language plpgsql as $$
declare i bigint; o int;
begin
  select coalesce(max(t.ordem), 0) + 1 into o from public.tarefas t where t.checkpoint_id = c;
  insert into public.tarefas (checkpoint_id, projeto, titulo, estado, concluida_em, app_sugerida, custo, descricao, ordem, criado_por_nome)
  values (c, (select projeto from public.checkpoints where id = c), titulo, estado, dia, app, custo, descricao, o, 'Equipa')
  returning id into i;
  return i;
end $$;

create function pg_temp.dc(p text, tarefa bigint, pergunta text, contexto text) returns bigint language plpgsql as $$
declare i bigint;
begin
  insert into public.decisoes (projeto, tarefa_id, pergunta, contexto, criado_por_nome)
  values (p, tarefa, pergunta, contexto, 'Equipa') returning id into i;
  return i;
end $$;

create function pg_temp.op(d bigint, titulo text, vantagens text, desvantagens text, custo text default '', descricao text default '')
returns void language plpgsql as $$
begin
  insert into public.decisoes_opcoes (decisao_id, titulo, descricao, vantagens, desvantagens, custo, ordem)
  values (d, titulo, descricao, vantagens, desvantagens, custo,
          (select coalesce(max(ordem), 0) + 1 from public.decisoes_opcoes where decisao_id = d));
end $$;

do $$
declare c bigint; t bigint; d bigint;
begin
  -- ===== Build Your House (configurador) =====
  c := pg_temp.cp('build_your_house', 'Motor do configurador', 'As regras de construção vêm do método Discovercasa; o motor é o Python do BOB a correr no browser.', 1, 'concluido', '2026-10-20');
  perform pg_temp.tf(c, 'Especificação v0.1 e estudo do IKEA Kreativ', 'concluida', '2026-10-20');
  perform pg_temp.tf(c, 'Divisor de módulos, verificado com Torres Vedras (D2503)', 'concluida', '2026-10-20', 'builder');
  perform pg_temp.tf(c, 'Formato da casa configurada e conversão para o Builder', 'concluida', '2026-10-20', 'builder');

  c := pg_temp.cp('build_your_house', 'Protótipo no browser', 'Do formato e m² até às pérgolas, com o preço em direto.', 2, 'concluido', '2026-10-29');
  perform pg_temp.tf(c, 'Forma, m² e preço base; paredes de 3 m com o total a correr', 'concluida', '2026-10-20');
  perform pg_temp.tf(c, 'Pé direito, portas e janelas, paredes interiores, acabamentos, guardar', 'concluida', '2026-10-21');
  perform pg_temp.tf(c, 'Cobertura à vista em painel sandwich (2 / 4 águas, L / T / U)', 'concluida', '2026-10-21');
  perform pg_temp.tf(c, 'Paredes desenhadas por cliques e divisões com pavimento', 'concluida', '2026-10-27');
  perform pg_temp.tf(c, 'Passo 7: pérgolas, garagens e anexos', 'concluida', '2026-10-29');

  c := pg_temp.cp('build_your_house', 'Publicado no Design', 'Em /build-your-house/, só com a entrada do Design.', 3, 'concluido', '2026-10-30');
  perform pg_temp.tf(c, 'Publicar como Build Your House atrás da entrada do Design', 'concluida', '2026-10-30');

  c := pg_temp.cp('build_your_house', 'Respostas pendentes', 'Pontos que só a Discovercasa pode confirmar (especificação §13).', 4, 'em_curso');
  t := pg_temp.tf(c, 'Confirmar a leitura de "Várias águas" nas casas L / T / U', 'em_curso');
  d := pg_temp.dc('build_your_house', t, 'Como se lê "Várias águas" nas casas em L, T e U?',
    'O motor tem hoje o tipo "misto": corpo principal de 4 águas e empenas nas pontas das alas. É a nossa leitura e falta confirmar.');
  perform pg_temp.op(d, 'Corpo de 4 águas e empenas nas alas', 'Já está construído e auditado em todas as formas.', 'É uma leitura nossa, ainda por confirmar.');
  perform pg_temp.op(d, 'Só 2 águas com empenas em cada corpo', 'A cobertura e a estrutura mais simples.', 'O cliente deixa de ter o corpo de 4 águas.');
  perform pg_temp.op(d, 'Corpo e alas todos de 4 águas', 'Aspeto uniforme, sem empenas.', 'O motor não oferece hoje 4 águas em L / T / U: é trabalho novo.');
  perform pg_temp.tf(c, 'Geometria do estribo na junção das alas (esboço juncao_ala_estribos.svg)', 'por_fazer');
  t := pg_temp.tf(c, 'Pérgola do passo 7: só ripada ou também coberta?', 'por_fazer');
  d := pg_temp.dc('build_your_house', t, 'A pérgola do passo 7 é só ripada ou também pode ser coberta?',
    'Hoje está construída a pérgola ripada. Torres Vedras tem uma pérgola coberta de telha.');
  perform pg_temp.op(d, 'Só ripada', 'Simples de configurar e de orçamentar.', 'Não serve quem quer sombra e chuva tapadas.', 'Preço a definir (lista de preços)');
  perform pg_temp.op(d, 'Ripada ou coberta com telha (como Torres Vedras)', 'Já sabemos construí-la; combina com a casa.', 'Mais estrutura e mais peças no motor.', 'Preço a definir (lista de preços)');
  perform pg_temp.op(d, 'Ripada ou coberta com painel sandwich', 'Mesma lógica da cobertura à vista da casa.', 'Aspeto mais industrial; mais regras a confirmar.', 'Preço a definir (lista de preços)');
  perform pg_temp.tf(c, 'Teste completo do configurador pela equipa, com comentários', 'por_fazer');

  c := pg_temp.cp('build_your_house', 'Preços reais', 'Os preços são provisórios até existir a lista de preços (Orçamentação).', 5, 'por_fazer');
  perform pg_temp.tf(c, 'Trocar os preços provisórios pelos da lista de preços', 'bloqueada', null, 'orcamentacao', '', 'À espera da lista de materiais e fornecedores.');
  perform pg_temp.tf(c, 'Mostrar as contas até ao preço final', 'por_fazer', null, 'orcamentacao');

  c := pg_temp.cp('build_your_house', 'Pronto para clientes', 'Nada vai online com dados de clientes sem o OK da Discovercasa.', 6, 'por_fazer');
  perform pg_temp.tf(c, 'Testar em telemóvel e tablet');
  perform pg_temp.tf(c, 'Aprovação da Discovercasa antes de abrir a clientes');
  perform pg_temp.tf(c, 'Funcionar também fora do método Discovercasa (futuro)', 'por_fazer', null, null, '', 'Hoje segue o método Discovercasa. Fica como está, mas o motor deve poder receber outros métodos.');

  -- ===== Builder =====
  c := pg_temp.cp('builder', 'Base de conhecimento e método', 'Como a Discovercasa constrói, regra a regra (mestre-construtor).', 1, 'concluido', '2026-10-15');
  perform pg_temp.tf(c, 'Sistema construtivo e regras madeira ↔ betão', 'concluida', '2026-09-23');
  perform pg_temp.tf(c, 'Livro de regras do método (agente mestre-construtor)', 'concluida', '2026-10-15');

  c := pg_temp.cp('builder', 'Primeiro modelo: Sobral Tipo 1', 'Loteamento Sobral, casa Tipo 1 com a estrutura Discovercasa.', 2, 'concluido', '2026-09-30');
  perform pg_temp.tf(c, 'Modelo Tipo 1 com a estrutura Discovercasa e teto superior plano', 'concluida', '2026-09-30');

  c := pg_temp.cp('builder', 'Torres Vedras a partir da arquitetura', 'Casa já construída: aprender a empresa e comparar com o que se gastou de verdade.', 3, 'concluido', '2026-10-20');
  perform pg_temp.tf(c, 'Primeiro modelo e lista de materiais', 'concluida', '2026-10-15');
  perform pg_temp.tf(c, 'Cobertura e módulos reais do desenho D2503', 'concluida', '2026-10-16');
  perform pg_temp.tf(c, 'Portas e janelas da tabela aprovada', 'concluida', '2026-10-19');
  perform pg_temp.tf(c, 'Pérgola, remates de vãos e saídas de caleira', 'concluida', '2026-10-20');

  c := pg_temp.cp('builder', 'Validação com os materiais reais', 'Os valores do modelo têm de estar perto do que a obra realmente gastou.', 4, 'em_curso');
  perform pg_temp.tf(c, 'Verificação das madeiras sem Blender (choques, peças fora do sítio)', 'concluida', '2026-10-30');
  perform pg_temp.tf(c, 'Receber a listagem real de materiais de Torres Vedras', 'bloqueada', null, null, '', 'À espera da Discovercasa.');
  perform pg_temp.tf(c, 'Comparar as quantidades do modelo com as reais', 'por_fazer', null, 'gerador');

  c := pg_temp.cp('builder', 'Sobral: casas de dois pisos', 'Loteamento de 16 casas e um armazém; em pausa desde 2026-10-15.', 5, 'por_fazer');
  perform pg_temp.tf(c, 'Retomar o loteamento Sobral quando avançar');

  c := pg_temp.cp('builder', 'Painel de definições', 'Hoje as medidas estão em sistema_construtivo.json.', 6, 'por_fazer');
  perform pg_temp.tf(c, 'Painel para comprimentos e composição dos módulos');
  perform pg_temp.tf(c, 'Funcionar também fora do método Discovercasa (futuro)', 'por_fazer', null, null, '', 'Hoje segue o método Discovercasa. Fica como está, mas deve poder receber outros métodos.');

  -- ===== Gerador de documentos =====
  c := pg_temp.cp('gerador', 'Documentos de produção', 'Módulos, Cobertura e Listagem de material para cada obra. O documento Módulos foi aprovado.', 1, 'concluido', '2026-10-20');
  perform pg_temp.tf(c, 'Gerar Módulos, Cobertura e Listagem de material', 'concluida', '2026-10-20', 'builder');

  c := pg_temp.cp('gerador', 'Gerador online', 'Larga-se a planta e recebem-se os documentos, tudo no browser.', 2, 'concluido', '2026-10-30');
  perform pg_temp.tf(c, 'Encontrar as plantas sozinho num DWFx de arquitetura', 'concluida', '2026-10-30');
  perform pg_temp.tf(c, 'Ler plantas em PDF vetorial', 'concluida', '2026-10-30');
  perform pg_temp.tf(c, 'Vista 3D da casa gerada', 'concluida', '2026-10-30');

  c := pg_temp.cp('gerador', 'Revisão da Discovercasa', 'Falta a revisão de dois dos três documentos.', 3, 'em_curso');
  perform pg_temp.tf(c, 'Rever o documento Cobertura');
  perform pg_temp.tf(c, 'Rever a Listagem de material');

  c := pg_temp.cp('gerador', 'Mais formatos de entrada', 'Os mesmos leitores servem o Step Inside (especificação §19).', 4, 'por_fazer');
  perform pg_temp.tf(c, 'Ler DXF', 'por_fazer', null, 'plataforma_cliente');
  perform pg_temp.tf(c, 'Ler IFC2x3 / IFC4', 'por_fazer', null, 'plataforma_cliente');

  -- ===== Orçamentação =====
  c := pg_temp.cp('orcamentacao', 'Lista de materiais e fornecedores', 'A Discovercasa vai fornecer a lista com o preço de cada material.', 1, 'por_fazer');
  perform pg_temp.tf(c, 'Receber a lista de materiais e fornecedores com preços', 'bloqueada', null, null, '', 'À espera da Discovercasa.');
  perform pg_temp.tf(c, 'Ligar cada linha da Listagem de material a um preço', 'por_fazer', null, 'gerador');

  c := pg_temp.cp('orcamentacao', 'Composição do preço final', 'Materiais, mão de obra, fundação, caixilharia, especialidades, instalações e pré-instalações, licenciamento e IVA.', 2, 'por_fazer');
  perform pg_temp.tf(c, 'Definir como se calcula cada parcela do preço');
  perform pg_temp.tf(c, 'Confirmar a taxa de IVA a aplicar');
  perform pg_temp.tf(c, 'Mostrar as contas à vista até ao preço final');

  c := pg_temp.cp('orcamentacao', 'Preço em direto no Build Your House', 'O configurador passa a usar os preços reais.', 3, 'por_fazer');
  perform pg_temp.tf(c, 'Ligar a orçamentação ao Build Your House', 'por_fazer', null, 'build_your_house');

  -- ===== Step Inside (plataforma AR/VR; id plataforma_cliente) =====
  c := pg_temp.cp('plataforma_cliente', 'Fase 0 · Auditoria do sistema atual', 'Conhecer o hub, a Cloudflare, o Supabase e a pipeline Blender antes de escrever código. Sem alterações em produção.', 1, 'por_fazer');
  perform pg_temp.tf(c, 'Inspecionar repositório, scripts, deployments e variáveis (sem mostrar segredos)');
  perform pg_temp.tf(c, 'Mapear a Cloudflare: Pages, rotas, domínios e limites');
  perform pg_temp.tf(c, 'Mapear o Supabase: tabelas, Auth, RLS, Storage, plano e quotas');
  perform pg_temp.tf(c, 'Documentar a pipeline PDF/DWFx → Blender que já existe', 'por_fazer', null, 'builder');
  t := pg_temp.tf(c, 'Inventariar a workstation local antes de qualquer compra', 'por_fazer', null, null, 'Compra única a cotar; energia = kW × horas × €/kWh');
  d := pg_temp.dc('plataforma_cliente', t, 'Que GPU para a workstation de desenvolvimento?',
    'A workstation serve para Blender, Unreal Editor, cook e testes; não é a máquina que serve os clientes. Decidir só depois de inventariar o PC atual (CPU, RAM, fonte, caixa, PCIe).');
  perform pg_temp.op(d, 'RTX 5070 Ti 16 GB', 'Mínimo prático recomendado; menor consumo.', '16 GB de VRAM podem limitar cenas pesadas.', 'Preço a cotar; 300 W, fonte de 750 W');
  perform pg_temp.op(d, 'RTX 4090 24 GB', 'Nível confortável; 24 GB de VRAM.', 'Geração anterior; 450 W.', 'Preço a cotar (usada ou nova); fonte de 850 W');
  perform pg_temp.op(d, 'RTX 5090 32 GB', 'Mais margem para cenas pesadas e produção.', 'A mais cara; 575 W, exige caixa e refrigeração à medida.', 'Preço a cotar; fonte de 1000 W');
  perform pg_temp.op(d, 'Manter a GPU atual por agora', 'Sem investimento imediato.', 'Pode não chegar ao Unreal com Lumen; só se sabe com benchmark.', '0 € (só energia)');
  perform pg_temp.tf(c, 'Relatório da arquitetura atual (docs/audit/current-architecture.md)');

  c := pg_temp.cp('plataforma_cliente', 'Fase 1 · Contrato de dados e qualidade de entrada', 'Cada informação extraída guarda a origem e a confiança: CONFIRMED, INFERRED, MISSING ou NEEDS_HUMAN_REVIEW. Nunca inventar cotas.', 2, 'por_fazer');
  perform pg_temp.tf(c, 'Escolher dois projetos de teste (terreno simples e com declive)');
  perform pg_temp.tf(c, 'Catalogar plantas, cortes, alçados, cotas e topografia');
  perform pg_temp.tf(c, 'Schema normalizado com proveniência e confiança por campo');
  perform pg_temp.tf(c, 'Matriz de formatos: DIRECT, CONVERT_REQUIRED, REFERENCE_ONLY, UNSUPPORTED', 'por_fazer', null, 'gerador');
  perform pg_temp.tf(c, 'Relatório de faltas e conflitos antes de gerar geometria');

  c := pg_temp.cp('plataforma_cliente', 'Fase 2 · Modelo Blender e terreno', 'O Blender é a fonte de verdade da geometria. Terreno rigoroso só com levantamento.', 3, 'por_fazer');
  perform pg_temp.tf(c, 'Reutilizar a geração Blender que já existe', 'por_fazer', null, 'builder', '0 € (Blender é gratuito)');
  perform pg_temp.tf(c, 'Collections semânticas (SITE_TERRAIN, ARCH_WALLS, ARCH_ROOF…)');
  perform pg_temp.tf(c, 'Terreno a partir de DEM, curvas de nível, XYZ ou LandXML');
  perform pg_temp.tf(c, 'Validar CRS, datum, unidades e cotas de controlo');
  perform pg_temp.tf(c, 'Relatório de validação: PASS, WARNING, NEEDS_HUMAN_REVIEW, FAIL');

  c := pg_temp.cp('plataforma_cliente', 'Fase 3 · Materiais e exportação', 'Ligar Blender e Unreal sem depender de converter shaders.', 4, 'por_fazer');
  perform pg_temp.tf(c, 'IDs estáveis de material (MAT_WOOD_OAK, MAT_GLASS_CLEAR…) e mapas PBR');
  perform pg_temp.tf(c, 'Presets de exportação: FBX para Unreal, GLB e USDZ para AR');
  perform pg_temp.tf(c, 'manifest.json com SHA-256, versões e avisos');
  perform pg_temp.tf(c, 'Teste de reimportação e comparação visual');

  c := pg_temp.cp('plataforma_cliente', 'Fase 4 · Unreal Viewer e aprovação visual', 'Primeira visita desktop de qualidade, com uma casa de referência.', 5, 'por_fazer');
  perform pg_temp.tf(c, 'Fixar a versão do Unreal e dos plugins');
  t := pg_temp.tf(c, 'Comparar build por projeto com runtime comum + pacotes de conteúdo');
  d := pg_temp.dc('plataforma_cliente', t, 'Como empacotar cada projeto no Unreal?',
    'Fazer um protótipo das duas e registar a decisão num ADR. Para a primeira demonstração, o caminho de menor risco.');
  perform pg_temp.op(d, 'A · Build próprio por projeto/versão', 'Mais fácil de validar; resultado mais rápido.', 'Duplica executáveis e recursos; atualizações mais pesadas.', '2–8 GB de conteúdo Unreal por projeto (R2)');
  perform pg_temp.op(d, 'B · Runtime comum + pacotes de conteúdo', 'Não duplica o viewer; escala melhor.', 'Exige provar cook, chunks e carregamento em runtime na versão exata do Unreal.', 'Menos armazenamento por projeto; mais tempo de desenvolvimento');
  t := pg_temp.tf(c, 'Definir a resolução e os FPS de lançamento');
  d := pg_temp.dc('plataforma_cliente', t, 'Que resolução e FPS para a visita desktop?',
    'Valores a validar com benchmark de uma casa real. Mais qualidade aumenta bitrate, GPU e VRAM: pode exigir uma GPU superior ou menos sessões por GPU.');
  perform pg_temp.op(d, '1080p a 60 FPS', 'Alvo inicial recomendado; menor exigência de GPU e de rede.', 'Menos nitidez em ecrãs grandes.', '≈ 0,79 €/h por sessão (RTX 4090 Secure)');
  perform pg_temp.op(d, '1440p', 'Mais nitidez.', 'Mais bitrate e GPU; a medir.', 'Mesma tarifa/hora se couber na mesma GPU; pode exigir GPU superior');
  perform pg_temp.op(d, '4K só em casos específicos', 'Máxima qualidade para apresentações.', 'Só depois de benchmark; menos sessões por GPU.', 'Provável GPU superior: custo/hora a cotar');
  perform pg_temp.tf(c, 'Master materials, iluminação, Lumen/Nanite e texture streaming');
  perform pg_temp.tf(c, 'Navegação em primeira pessoa, colisões, loading e saída');
  perform pg_temp.tf(c, 'Aprovação visual da Discovercasa (imagens, FPS, métricas)');

  c := pg_temp.cp('plataforma_cliente', 'Fase 5 · Prova de conceito Pixel Streaming', 'Mostrar a casa por link a partir de uma GPU remota.', 6, 'por_fazer');
  perform pg_temp.tf(c, 'Testar primeiro em rede local', 'por_fazer', null, null, '0 €');
  t := pg_temp.tf(c, 'Lançar a aplicação numa GPU cloud de teste (com autorização)', 'por_fazer', null, null, '≈ 0,79 €/h (RTX 4090 Secure)');
  d := pg_temp.dc('plataforma_cliente', t, 'Que GPU cloud para as sessões dos clientes?',
    'Custo = tarifa × horas faturáveis × GPUs ativas. Contar arranque, preload, espera e encerramento. Preços RunPod de 2026-11-05; confirmar no checkout.');
  perform pg_temp.op(d, 'RunPod RTX 4090 Secure Cloud', 'Disponibilidade e condições de host mais seguras.', 'Mais cara que a Community.', '0,89 USD/h ≈ 0,79 €/h · piloto 25 h/mês ≈ 19,83 €');
  perform pg_temp.op(d, 'RunPod RTX 4090 Community Cloud', 'Muito mais barata.', 'Risco de host e disponibilidade: não serve para prometer serviço.', '0,34 USD/h ≈ 0,30 €/h');
  perform pg_temp.op(d, 'Workstation local', 'Sem custo por hora; boa para a primeira prova.', 'Não é um serviço 24/7; depende do PC de trabalho.', '0 €/h (só energia)');
  perform pg_temp.tf(c, 'Integrar o stream numa página do hub');
  perform pg_temp.tf(c, 'Medir FPS, latência, bitrate, VRAM e custo por sessão');
  perform pg_temp.tf(c, 'Encerrar e libertar a instância no fim da sessão');

  c := pg_temp.cp('plataforma_cliente', 'Fase 6 · Ligar Cloudflare, Supabase e R2', 'Do upload ao link do cliente sem abrir os sistemas técnicos.', 7, 'por_fazer');
  perform pg_temp.tf(c, 'Migrations só para as tabelas em falta (projetos, versões, assets, jobs, sessões, links)');
  t := pg_temp.tf(c, 'Criar o armazenamento privado dos ficheiros 3D (com autorização)', 'por_fazer', null, null, '8–15 GB por projeto');
  d := pg_temp.dc('plataforma_cliente', t, 'Onde guardar os ficheiros 3D pesados?',
    'Cada casa ocupa 8–15 GB por versão (até 30 GB nas mais pesadas). Confirmar o plano Supabase atual antes de decidir.');
  perform pg_temp.op(d, 'Cloudflare R2', 'Sem custo de saída de dados; já usamos a Cloudflare.', 'Mais um serviço a configurar (bucket, URLs assinados).', '0,015 USD/GB-mês, 10 GB grátis · 10 casas ≈ 0,94–1,87 €/mês');
  perform pg_temp.op(d, 'Supabase Storage', 'Já está no projeto; mesma autenticação.', 'Plano Free tem só 1 GB e 5 GB de saída; a saída é faturada.', 'Pro a partir de 25 USD/mês');
  perform pg_temp.tf(c, 'Upload direto com URLs assinados e multipart (retomar, checksum)');
  perform pg_temp.tf(c, 'Jobs de processamento com estado no hub');
  perform pg_temp.tf(c, 'Links privados com validade e revogação');

  c := pg_temp.cp('plataforma_cliente', 'Fase 7 · AR no telemóvel', 'Um modelo próprio, simplificado, que corre no telemóvel do cliente (sem GPU cloud).', 8, 'por_fazer');
  perform pg_temp.tf(c, 'Simplificar: 30–50 mil triângulos, texturas até 2048, ≈ 10 MB');
  perform pg_temp.tf(c, 'Gerar GLB (Android) e USDZ (iPhone)', 'por_fazer', null, null, '0 € de serviço');
  perform pg_temp.tf(c, 'Testar em pelo menos um iPhone e um Android reais');
  perform pg_temp.tf(c, 'Visualizador 3D para quem não tem AR');

  c := pg_temp.cp('plataforma_cliente', 'Fase 8 · Prova de conceito VR', 'Risco técnico crítico: o Lumen não suporta VR e o Pixel Streaming VR é experimental.', 9, 'por_fazer');
  perform pg_temp.tf(c, 'Escolher o headset, o browser e o modo de acesso', 'por_fazer', null, null, 'Headset a cotar');
  perform pg_temp.tf(c, 'Perfil VR_BAKED sem Lumen, com iluminação pré-calculada');
  perform pg_temp.tf(c, 'Medir frame rate, latência, conforto e estabilidade');
  t := pg_temp.tf(c, 'Decisão escrita sobre a VR em produção');
  d := pg_temp.dc('plataforma_cliente', t, 'Como entregamos a VR aos clientes?',
    'Não declarar a VR concluída só porque aparece imagem no headset.');
  perform pg_temp.op(d, 'Pixel Streaming 2 VR por link', 'O cliente não instala nada; mesma GPU cloud.', 'Experimental no Unreal 5.8; latência e conforto por provar.', '≈ 0,79 €/h por sessão + tráfego');
  perform pg_temp.op(d, 'Aplicação VR nativa (headset ou PC)', 'Qualidade e conforto mais previsíveis.', 'O cliente instala uma app; mais desenvolvimento e manutenção.', 'Sem GPU cloud; custo de desenvolvimento');
  perform pg_temp.op(d, 'Adiar a VR', 'Foco no 3D por link e na AR.', 'Perde-se a VR que hoje se faz com Enscape.', '0 €');

  c := pg_temp.cp('plataforma_cliente', 'Fase 9 · Produção e escala', 'Operação segura, observável e com custos medidos.', 10, 'por_fazer');
  perform pg_temp.tf(c, 'Testes com clientes internos e externos controlados');
  perform pg_temp.tf(c, 'Alertas de sessões, erros, custos e GPU; orçamento mensal');
  perform pg_temp.tf(c, 'Backups com restauração testada e política de retenção');
  perform pg_temp.tf(c, 'Confirmar por escrito com a Epic a licença do Unreal', 'por_fazer', null, null, 'Gratuito abaixo de 1 M USD de receita anual: confirmar');
end $$;
