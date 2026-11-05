-- Build Your House: checkpoints e tarefas da "Especificação de Desenvolvimento — Smart Land, Smart Interiors e
-- Conformidade da Construção" (2026-11-05), na ordem certa face ao que já existe no hub. Corre uma vez, depois de 0006.
--
-- Ordem (o que já existe fica; os novos entram assim):
--   1–3 Motor, Protótipo, Publicado (concluídos) · 4 Respostas pendentes (em curso)
--   5 Fase 0 · Auditoria — NOVO: não mexe em código, pode começar já (a especificação manda começar por aqui)
--   6 Preços reais · 7 Pronto para clientes — o configurador base abre a clientes antes das extensões
--   8–15 Fases 1–8 da especificação, pela ordem dela (terreno → importação → 3D → implantação → conformidade →
--        interiores → decoração automática → expansão)

-- abre espaço: Preços reais 5 → 6, Pronto para clientes 6 → 7
update public.checkpoints set ordem = ordem + 1 where projeto = 'build_your_house' and ordem >= 5;

create function pg_temp.cp(p text, titulo text, descricao text, ordem int)
returns bigint language plpgsql as $$
declare i bigint;
begin
  insert into public.checkpoints (projeto, titulo, descricao, ordem, estado, criado_por_nome)
  values (p, titulo, descricao, ordem, 'por_fazer', 'Equipa') returning id into i;
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

do $$
declare c bigint; t bigint; d bigint; p constant text := 'build_your_house';
begin
  c := pg_temp.cp(p, 'Fase 0 · Auditoria para Smart Land, Interiores e Conformidade',
    'Antes de qualquer código: conhecer o configurador, o motor 3D, o Supabase e a Cloudflare e escrever o plano de integração. Nenhum código existente muda.', 5);
  perform pg_temp.tf(c, 'Identificar o motor 3D e como se guardam casas, pisos, divisões, paredes, portas e janelas');
  perform pg_temp.tf(c, 'Inventariar tabelas, regras RLS, armazenamento e tarefas assíncronas');
  perform pg_temp.tf(c, 'Mapear as fontes externas usáveis sem credenciais privadas (DGT, CAOP, cadastro, LiDAR)', 'plataforma_cliente');
  perform pg_temp.tf(c, 'Escrever docs/AUDITORIA_SMART_LAND_INTERIORES.md: arquitetura, migrações, riscos, fases e testes');
  perform pg_temp.tf(c, 'Validar o plano com a Discovercasa antes da Fase 1');

  c := pg_temp.cp(p, 'Smart Land · Fase 1 · Terreno mínimo',
    'Localizar o terreno, propor parcelas e deixar o cliente confirmar, desenhar ou importar o limite. A imagem aérea não é cadastro.', 8);
  perform pg_temp.tf(c, 'Mapa e pesquisa de localização');
  perform pg_temp.tf(c, 'Consultar a CAOP e a coleção cadastral da DGT (Continente)');
  perform pg_temp.tf(c, 'Lista de parcelas candidatas e confirmação pelo cliente');
  perform pg_temp.tf(c, 'Desenho manual do limite');
  perform pg_temp.tf(c, 'Importar GeoJSON e KML/KMZ (incluindo o KML do BUPi dado pelo proprietário)', null, '', 'Guardar a origem BUPI_KML_USER_SUPPLIED: não equivale a certificar limites nem titularidade.');
  perform pg_temp.tf(c, 'Guardar a geometria com a origem e reabrir o projeto sem a perder');

  c := pg_temp.cp(p, 'Smart Land · Fase 2 · Importação geográfica alargada',
    'Ficheiros válidos entram; ambíguos ou malformados são recusados com uma explicação útil.', 9);
  perform pg_temp.tf(c, 'Importar DXF, GeoPackage e Shapefile', 'gerador');
  perform pg_temp.tf(c, 'Importar GeoTIFF e LAS/LAZ (através do processador)', 'plataforma_cliente');
  perform pg_temp.tf(c, 'Conversão de sistemas de coordenadas e diagnóstico dos ficheiros');
  t := pg_temp.tf(c, 'Leitura de DWG');
  d := pg_temp.dc(p, t, 'Como lemos ficheiros DWG?',
    'A especificação deixa o DWG dependente de uma solução de conversão licenciada e testada. Hoje pedimos PDF ou DWFx exportados do AutoCAD.');
  perform pg_temp.op(d, 'Continuar a pedir PDF / DWFx / DXF', 'Já funciona no Gerador; sem licenças.', 'Um passo a mais para quem só tem DWG.', '0 €');
  perform pg_temp.op(d, 'Conversor licenciado (SDK)', 'Lê o DWG direto.', 'Licença e integração por testar.', 'Licença a cotar');
  perform pg_temp.op(d, 'Conversão manual pela equipa', 'Sem desenvolvimento.', 'Trabalho manual em cada obra.', 'Tempo da equipa');

  c := pg_temp.cp(p, 'Smart Land · Fase 3 · Terreno 3D',
    'A casa no terreno com elevação coerente; dados públicos preliminares distintos de levantamento importado. Um MDT público é contexto, não levantamento.', 10);
  perform pg_temp.tf(c, 'Consultar a cobertura LiDAR e recortar o MDT do local', 'plataforma_cliente');
  perform pg_temp.tf(c, 'Processamento assíncrono e malha do terreno com níveis de detalhe', 'plataforma_cliente', 'Medir antes de criar infraestrutura paga');
  perform pg_temp.tf(c, 'Integrar o terreno com a casa do configurador');
  perform pg_temp.tf(c, 'Guardar a precisão e a origem (MDT ≠ MDS; 2 m não é precisão centimétrica)');

  c := pg_temp.cp(p, 'Implantação · Fase 4 · Implantação geométrica',
    'Validar o contorno real das casas L, U e irregulares, nunca um retângulo envolvente.', 11);
  perform pg_temp.tf(c, 'Extrair o contorno de implantação da casa (formas L, U e irregulares)', 'builder');
  perform pg_temp.tf(c, 'Converter coordenadas locais para o sistema do terreno');
  perform pg_temp.tf(c, 'Validação geométrica no PostGIS');
  perform pg_temp.tf(c, 'Afastamentos só a partir de regras confirmadas');
  perform pg_temp.tf(c, 'Resultado visual e relatório');

  c := pg_temp.cp(p, 'Conformidade · Fase 5 · Piloto municipal',
    'Regras só com fonte, artigo, vigência, revisor e testes. Sem regra: SEM_DADOS ou POR_CONFIRMAR, nunca um resultado positivo. A CRUS não decide licenciamento.', 12);
  perform pg_temp.tf(c, 'Catálogo de documentos e instrumentos (PDM, planos, loteamentos)');
  perform pg_temp.tf(c, 'Painel administrativo de regras com extração assistida');
  perform pg_temp.tf(c, 'Escolher 2 a 4 municípios-piloto depois de avaliar as fontes', null, '', 'Critérios: PDM e cartografia acessíveis, dados vetoriais, regulamentos, colaboração com técnicos locais, volume de projetos.');
  perform pg_temp.tf(c, 'Revisão das regras por um profissional qualificado', null, 'Custo do revisor a definir');
  perform pg_temp.tf(c, 'Pacotes municipais versionados e relatório de cobertura');

  c := pg_temp.cp(p, 'Smart Interiors · Fase 6 · Base',
    'Decorar por estilo e mudar objetos à mão sem perder os dados do projeto.', 13);
  perform pg_temp.tf(c, 'Estrutura do catálogo e fichas dos objetos (licença, escala, materiais)');
  perform pg_temp.tf(c, 'Carregar GLB/glTF e categorias por divisão', 'plataforma_cliente');
  perform pg_temp.tf(c, 'Oito estilos iniciais configuráveis', null, '', 'Minimalista, Contemporâneo, Japandi, Clássico, Mediterrânico, Escandinavo, Industrial, Orgânico contemporâneo.');
  perform pg_temp.tf(c, 'Três variantes sugeridas por objeto');
  perform pg_temp.tf(c, 'Selecionar, mover, rodar, substituir e mudar materiais; guardar e recuperar');
  t := pg_temp.tf(c, 'Origem dos modelos 3D do catálogo', null, 'Licenças a cotar');
  d := pg_temp.dc(p, t, 'De onde vêm os modelos 3D do catálogo de interiores?',
    'Antes de integrar cada modelo: licença, atribuição, uso comercial, redistribuição (especificação §12.3). Começar com um catálogo pequeno e coerente.');
  perform pg_temp.op(d, 'Modelos feitos por nós', 'Direitos totais; estilo coerente.', 'Mais tempo de produção.', 'Tempo da equipa');
  perform pg_temp.op(d, 'Bibliotecas com licença comercial', 'Rápido; catálogo grande.', 'Licenças a verificar uma a uma; estilos misturados.', 'Licenças a cotar');
  perform pg_temp.op(d, 'Modelos dos fabricantes', 'Produtos reais que se podem vender.', 'Formatos e qualidade variáveis; acordos com cada marca.', 'A negociar');

  c := pg_temp.cp(p, 'Smart Interiors · Fase 7 · Posicionamento e decoração automática',
    'Nenhuma proposta automática é aceite sem passar pelas regras de posicionamento e colisão. A IA sugere; a colocação é geométrica.', 14);
  perform pg_temp.tf(c, 'Colisões simplificadas e restrições de parede, porta e janela');
  perform pg_temp.tf(c, 'Estados dos objetos: gerido pelo estilo, alterado pelo utilizador, bloqueado');
  perform pg_temp.tf(c, 'Até três propostas automáticas por divisão ("Decorar divisão")', null, 'Medir o custo se usar IA');
  perform pg_temp.tf(c, 'Verificação geométrica das propostas');

  c := pg_temp.cp(p, 'Conformidade · Fase 8 · Expansão municipal e técnica',
    'Cada área só é declarada coberta com fontes, testes, revisor e procedimento de atualização.', 15);
  perform pg_temp.tf(c, 'Expandir a cobertura municipal de forma auditável');
  perform pg_temp.tf(c, 'Condicionantes e regimes setoriais (REN, RAN, domínio hídrico, património, servidões)');
  perform pg_temp.tf(c, 'Validações técnicas com especialistas (RGEU / futuro Código da Construção)');
  perform pg_temp.tf(c, 'Procedimento de atualização legislativa e relatórios técnicos preliminares');
end $$;
