-- Redes sociais: o planeamento que estava no Excel "DiscoverCasa Post Mensal - publicações" (folha "Jul  Ago  Set 26":
-- julho a dezembro de 2026). Gerado por supabase/sementes/redes_sociais_iniciais.py; corre uma vez, depois de 0009.
-- Estados: semanas já passadas com legenda = publicado, sem legenda = não feito; seguintes com legenda e fotos = por
-- aprovar (hoje = 2026-11-06).
-- As fotos ficam no armazenamento privado "social" (carregadas à parte); aqui só as linhas.

insert into public.obras (nome, descricao, ordem, criado_por_nome) values
  ('Matosinhos', '', 1, 'Equipa'),
  ('Casa dos Cães', '3 publicações previstas (Mai - Ago).', 2, 'Equipa'),
  ('Boelhe', '3 publicações previstas.', 3, 'Equipa'),
  ('Ribamar', '', 4, 'Equipa'),
  ('Gaia', 'Aumento de uma casa já construída pela Discovercasa.', 5, 'Equipa'),
  ('Oliveira de Azeméis', 'Testemunho de um cliente.', 6, 'Equipa'),
  ('Lagos', '', 7, 'Equipa'),
  ('Sobral', 'Loteamento com 16 habitações e 3 estruturas de apoio.', 8, 'Equipa'),
  ('Torres Vedras', 'Casa concluída.', 9, 'Equipa');

insert into public.obras_fases (obra_id, nome, ordem, estado, periodo, posts_previstos, notas, criado_por_nome) values
  ((select id from public.obras where nome = 'Matosinhos'), 'Movimento de terras', 1, 'concluida', '', 1, '', 'Equipa'),
  ((select id from public.obras where nome = 'Matosinhos'), 'Base de fundação', 2, 'concluida', '', 3, '', 'Equipa'),
  ((select id from public.obras where nome = 'Matosinhos'), 'Estrutura', 3, 'prevista', 'Julho - Ago', 2, '', 'Equipa'),
  ((select id from public.obras where nome = 'Matosinhos'), 'Acabamentos', 4, 'prevista', 'Set - Dez', 2, '2 ou mais publicações.', 'Equipa'),
  ((select id from public.obras where nome = 'Boelhe'), 'Movimento de terras', 1, 'concluida', '', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Boelhe'), 'Base de fundação', 2, 'concluida', '', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Boelhe'), 'Estrutura', 3, 'concluida', '', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Boelhe'), 'Acabamentos', 4, 'prevista', 'Junho', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Ribamar'), 'Projetos', 1, 'concluida', '', null, 'Projetos de um gabinete parceiro.', 'Equipa'),
  ((select id from public.obras where nome = 'Ribamar'), 'Movimento de terras', 2, 'prevista', 'Jun', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Ribamar'), 'Base de fundação', 3, 'prevista', 'Jul - Ago', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Ribamar'), 'Estrutura', 4, 'prevista', 'Set - Out', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Ribamar'), 'Acabamentos', 5, 'prevista', 'Nov - Fev', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Gaia'), 'Aumento', 1, 'prevista', 'Jul', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Oliveira de Azeméis'), 'Garantia', 1, 'prevista', 'Set', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Lagos'), 'Projetos', 1, 'concluida', '', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Lagos'), 'Movimento de terras', 2, 'prevista', 'Nov ??', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Lagos'), 'Base de fundação', 3, 'prevista', 'Dez ??', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Lagos'), 'Estrutura', 4, 'prevista', '', null, '', 'Equipa'),
  ((select id from public.obras where nome = 'Lagos'), 'Acabamentos', 5, 'prevista', '', null, '', 'Equipa');

insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-07-01', 1, (select id from public.obras where nome = 'Sobral'), null, 'Sobral - Estamos de volta // projeto custoias', 'carrossel',
  'Estamos de regresso... e voltamos com um projeto que nos enche de orgulho. 🏡🌿

Depois de algum tempo a preparar grandes novidades, chegou o momento de vos mostrar o que aí vem. A Discovercasa vai dar início à construção de um novo empreendimento, pensado para unir qualidade de vida, sustentabilidade e integração com a natureza.

Este projeto contará com:
✅ 16 habitações
✅ 3 estruturas de apoio
✅ Projeto ecológico e sustentável
✅ Campo de padel e piscina

Mais do que construir casas, continuamos a criar espaços onde o conforto, o design e a qualidade caminham lado a lado.

Este é apenas o início. Ao longo dos próximos meses vamos partilhar convosco a evolução da obra e mostrar cada etapa deste novo desafio.

👉 Descubra mais sobre a Discovercasa e os nossos projetos em www.discovercasa.pt

#Discovercasa #NovoProjeto #EmConstrução #Construção #ConstruçãoPersonalizada #CasasDeSonho #Arquitetura #Design #Sustentabilidade #ProjetoSustentável #Habitação #QualidadeDeVida #Portugal #ConstruçãoEmPortugal #Inovação #ConstruçãoCivil',
  'Legendas alternativas que estavam no Excel:

Estamos de volta. E voltámos com um grande projeto. 🏡✨
Há novidades a caminho… e esta é só a primeira.
Em breve damos início à construção de um novo empreendimento que reúne inovação, sustentabilidade e qualidade de vida.
Este projeto inclui:
✔️ 16 habitações
✔️ 3 estruturas de apoio
✔️ Campo de padel e piscina
✔️ Conceito ecológico e sustentável

Este é apenas o começo. Acompanhe connosco cada etapa desta obra.
👉 Descubra mais em www.discovercasa.pt
#Discovercasa #NovoProjeto #Construção #ConstruçãoEmPortugal #CasasPersonalizadas #ProjetoSustentável #Arquitetura #Habitação #Qualidade #Inovação #Design #ConstruçãoCivil #QualidadeDeVida

— — —

Estamos a preparar uma nova fase.

Nos bastidores, continuamos a desenvolver projetos pensados com rigor, equilíbrio e atenção a cada detalhe.

Em breve, teremos novidades para partilhar.

Até lá, seguimos focados naquilo que melhor sabemos fazer: transformar ideias em espaços para viver.

👉 Descubra mais em www.discovercasa.pt
#Discovercasa #NovoProjeto #Construção #ConstruçãoEmPortugal #CasasPersonalizadas #ProjetoSustentável #Arquitetura #Habitação #Qualidade #Inovação #Design #ConstruçãoCivil #QualidadeDeVida', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-07-01', 2, (select id from public.obras where nome = 'Boelhe'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Boelhe' and f.nome = 'Base de fundação'), 'Boelhe - BF', 'carrossel',
  'Cada grande projeto começa com uma base sólida. 🏡

Mais uma fundação concluída pela equipa Discovercasa, preparada com o rigor e a qualidade que colocamos em cada construção.

Acompanhe os nossos projetos e descubra como transformamos cada etapa em sinónimo de excelência.

👉 Saiba mais em www.discovercasa.pt

#Discovercasa #Construção #Fundações #Obra #ConstruçãoCivil #CasasPersonalizadas #Qualidade #Engenharia #ConstruçãoEmPortugal #Arquitetura #Habitação #Projeto #ConstruçãoDeExcelência',
  '', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-07-01', 3, (select id from public.obras where nome = 'Torres Vedras'), null, 'Torres Vedras - Video da casa', 'carrossel',
  'Linhas modernas, espaços acolhedores e uma ligação perfeita ao exterior. 🏡✨

Hoje levamo-lo até uma das noosas mais recentes obras para conhecer mais um projeto concluído pela Discovercasa. Neste carrossel, descubra os detalhes do exterior e do interior de uma habitação pensada para oferecer conforto, funcionalidade e um estilo de vida em harmonia com a envolvente.

Deslize para conhecer todos os pormenores desta casa e inspire-se para o seu futuro lar.

👉 Saiba mais sobre os nossos projetos em www.discovercasa.pt

#Discovercasa #TorresVedras #CasaPersonalizada #Moradia #Construção #ConstruçãoEmPortugal #Arquitetura #DesignContemporâneo #Habitação #CasasDeSonho #Qualidade #Conforto #ProjetoÀMedida #ConstruçãoCivil',
  'Foto 5: Vídeo que enviei pelo wpp no fim do carrossel', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-07-01', 4, (select id from public.obras where nome = 'Boelhe'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Boelhe' and f.nome = 'Estrutura'), 'Boelhe - Estrutura', 'carrossel',
  'Da base à estrutura, o projeto começa a ganhar forma. 🏡

Depois da conclusão da fundação, avançamos para uma das etapas mais entusiasmantes da construção: a montagem da estrutura.

Cada elemento é instalado com precisão para garantir resistência, durabilidade e a qualidade que caracteriza todos os projetos Discovercasa.

É assim, passo a passo, que transformamos um projeto em realidade.

👉 Acompanhe a evolução das nossas obras e saiba mais em www.discovercasa.pt

#Discovercasa #Construção #Estrutura #Obra #ConstruçãoEmPortugal #CasasPersonalizadas #Arquitetura #Engenharia #Qualidade #Habitação #ConstruçãoCivil #ProjetoÀMedida #CasaNova #DaIdeiaÀRealidade',
  '', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-08-01', 1, (select id from public.obras where nome = 'Matosinhos'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Matosinhos' and f.nome = 'Base de fundação'), 'Matosinhos - BF', 'carrossel',
  '🚧 Mais de 100 camiões removidos para dar lugar a um novo sonho.

Antes de erguer paredes, é necessário preparar o terreno para receber uma estrutura sólida. Nesta nova obra, foram removidos mais de 100 camiões de terra, num processo essencial para garantir a estabilidade e a qualidade da construção.

Em cada projeto da DiscoverCasa criamos bases capazes de sustentar não apenas uma casa, mas o futuro de quem a vai habitar.

Este é apenas o primeiro passo de uma nova história, e mal podemos esperar para partilhar consigo todas as etapas desta transformação. 🏗️✨

Acompanhe a evolução desta obra e descubra como transformamos desafios em projetos únicos.

🌐 Visite o nosso site e conheça mais projetos: www.discovercasa.pt

#Discovercasa #NovaObra #MovimentoDeTerras #ConstruçãoDeCasas #ObraEmCurso #CasasPersonalizadas #ConstruçãoPortugal #Engenharia #Arquitetura #Moradia #ProjetoÀMedida #Fundação #ConstruçãoResidencial #CasaDeSonho',
  'Foto 5: Vídeo que vou enviar para o wpp da retroescavadora', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-08-01', 2, (select id from public.obras where nome = 'Torres Vedras'), null, 'Torres Vedras - Testemunho', 'video',
  'Hoje partilhamos o testemunho de mais um cliente satisfeito com a sua experiência com a DiscoverCasa. 🏡

Nada nos deixa mais orgulhosos do que ver a confiança dos nossos clientes transformada em realidade.

Se também sonha com uma casa em estrutura de madeira, fale conosco e descubra como podemos tornar esse projeto realidade.

📩 Entre em contacto conosco : www.discovercasa.pt

#DiscoverCasa #CasasMadeira #ConstruçãoEmMadeira #ConstruçãoSustentável #CasaDeSonho #ConstruçãoPortugal #TestemunhoCliente #Arquitetura #EficiênciaEnergética #CasaPersonalizada',
  'Foto 1: Vídeo que está no wpp', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-08-01', 3, (select id from public.obras where nome = 'Boelhe'), null, 'Boelhe - Casa', 'carrossel',
  '🌿 Linhas simples, materiais naturais e um ambiente que se funde com a paisagem envolvente.

Mais do que construir casas, procuramos criar espaços que respeitam o local onde se inserem e proporcionam uma experiência única a quem os habita.

Neste projeto, a combinação entre o revestimento em madeira, a luminosidade natural e a envolvência verde dá origem a uma habitação acolhedora, onde o conforto e a tranquilidade andam lado a lado.

Cada escolha foi pensada para equilibrar estética, funcionalidade e bem-estar, transformando um terreno num lugar para criar memórias. 🏡✨

Quer descobrir como podemos dar vida ao seu projeto?

🌐 Visite www.discovercasa.pt

#Discovercasa #CasasDeMadeira #ConstruçãoPersonalizada #ArquiteturaContemporânea #HabitaçãoModerna #ProjetoResidencial #ConstruçãoPortugal #DesignExterior #CasaNoMeioDaNatureza #ArquiteturaSustentável #Moradia #ProjetosÀMedida #CasasPortugal',
  '', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-08-01', 4, (select id from public.obras where nome = 'Casa dos Cães'), null, 'Cães - Analisar 1', 'carrossel',
  'Nesta fase, já é possível ver a identidade desta Discovercasa: linhas modernas, espaços amplos e uma construção pensada para valorizar cada área.

Ainda falta o resultado final, mas o essencial já está a acontecer.

Do projeto à realidade.

🌐 www.discovercasa.pt

#Discovercasa #Construção #CasaNova #Arquitetura #Moradia #ConstruçãoDeCasas #Portugal #CasaDeSonho',
  '', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-09-01', 1, (select id from public.obras where nome = 'Matosinhos'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Matosinhos' and f.nome = 'Base de fundação'), 'Matosinhos - BF', 'carrossel',
  '**Uma fundação que começa a ganhar forma. 🏗️**

Entre escavações, cofragens, ferro e betão, esta obra já passou da preparação do terreno para uma nova fase: a construção da base que vai sustentar toda a casa.

É aqui que o projeto começa, literalmente, a sair do papel.

👉 Quer acompanhar o processo de construção da sua futura casa? Fale connosco em **[www.discovercasa.pt](http://www.discovercasa.pt)**

#DiscoverCasa #Construção #Fundação #Obra #CasaDeMadeira #ConstruçãoDeCasas #EstruturaDeMadeira #CasaNova #ConstruçãoPortugal #ProjetoDeCasa',
  '', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-09-01', 2, (select id from public.obras where nome = 'Torres Vedras'), null, 'Torres Vedras - Testemunho', 'video',
  '',
  'Foto 1: confirmação', 'nao_feito', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-09-01', 3, (select id from public.obras where nome = 'Casa dos Cães'), null, 'Cães - Analisar 2', 'carrossel',
  '',
  '', 'nao_feito', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-09-01', 4, (select id from public.obras where nome = 'Matosinhos'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Matosinhos' and f.nome = 'Base de fundação'), 'Matosinhos - BF', 'carrossel',
  '🏗️ 3.ª etapa - O Segundo Piso Começa a Ganhar Forma

Depois da preparação do terreno e da construção da base de fundação do rés do chão, chegamos a mais um momento importante deste projeto: o segundo piso começa a ganhar vida.

Cada elemento é colocado com precisão, dando forma à estrutura e aproximando-nos, passo a passo, do resultado final. 🏡

Mais do que construir, é acompanhar cada fase e garantir que cada detalhe fica preparado para durar.

👉 Acompanhe a evolução dos nossos projetos e descubra o que podemos construir consigo.
🌐 www.discovercasa.pt

#Discovercasa #Construção #ConstruçãoDeCasas #MétodoConstrutivo #Fundação #Estrutura #SegundoPiso #CasaNova #ProjetoÀMedida #Engenharia #ConstruirParaViver #Portugal',
  '', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-10-01', 1, (select id from public.obras where nome = 'Ribamar'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Ribamar' and f.nome = 'Projetos'), 'Ribamar - Testemunho projetos', 'video',
  '',
  'Foto 1: confirmação', 'nao_feito', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-10-01', 2, (select id from public.obras where nome = 'Casa dos Cães'), null, 'Cães - Analisar 3', 'carrossel',
  '',
  '', 'nao_feito', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-10-01', 3, (select id from public.obras where nome = 'Matosinhos'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Matosinhos' and f.nome = 'Estrutura'), 'Matosinhos - Estrutura', 'carrossel',
  '🏗️ A estrutura começa a erguer-se e mais uma casa a ganhar forma.

É nesta fase que começamos a ver o projeto transformar-se numa verdadeira casa, com cada elemento da estrutura a definir os seus futuros espaços.

Mais uma etapa em progresso. E esta casa já começa a ganhar mais vida. 🌿

🌐 www.discovercasa.pt

#Discovercasa #ConstruçãoEmMadeira #EstruturaEmMadeira #CasaEmConstrução #ConstruçãoPortugal #ObraEmCurso #CasasDeMadeira #ProjetoPersonalizado #Arquitetura #Moradia #CasasPortugal',
  '', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-10-01', 4, (select id from public.obras where nome = 'Ribamar'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Ribamar' and f.nome = 'Movimento de terras'), 'Ribamar - Mov Terras', 'carrossel',
  'Um novo projeto começa a ganhar forma em Ribamar. 🌱🏗️

Nesta primeira etapa, é tempo de preparar o terreno. A movimentação de terras permite criar as condições certas para receber a futura construção, garantindo que cada fase avance sobre uma base bem planeada.

Por trás de cada casa existe muito trabalho que não se vê no resultado final. É aqui que começa.

Do terreno ao projeto. Da ideia à realidade.

Saiba mais sobre os nossos projetos em www.discovercasa.pt

#Discovercasa #Ribamar #ConstruçãoDeCasas #MovimentaçãoDeTerras #PreparaçãoDoTerreno #ConstruçãoPortugal #Engenharia #Obra #CasaDeSonho #ProjetoDeCasa #ConstruçãoCivil #CasasPersonalizadas',
  '', 'publicado', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-11-01', 1, (select id from public.obras where nome = 'Gaia'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Gaia' and f.nome = 'Aumento'), 'Gaia - Aumento estrutura', 'carrossel',
  'Crescer com a confiança de quem já construiu connosco.
Este projeto tem um significado especial: estamos a ampliar uma casa que já tinha sido construída pela Discovercasa. Um novo capítulo para uma casa que volta a ganhar vida, agora com mais espaço e novas possibilidades.
É esta confiança que nos motiva a continuar a construir, evoluir e acompanhar cada cliente ao longo do tempo. 🔨
👉 Também quer dar uma nova dimensão à sua casa? Fale connosco!
🌐 www.discovercasa.pt
#Discovercasa #AmpliaçãoDeCasas #Construção #Remodelação #ProjetosÀMedida #ConstruçãoDeCasas #Arquitetura #Engenharia #MaisEspaço #CasaDosSonhos #Portugal',
  '', 'por_aprovar', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-11-01', 2, (select id from public.obras where nome = 'Matosinhos'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Matosinhos' and f.nome = 'Estrutura'), 'Matosinhos - Estrutura', 'carrossel',
  '🏡 A estrutura já ganhou forma. Agora, reforçamos a sua proteção com a aplicação da membrana transpirável — uma camada que permite à estrutura “respirar”, ao mesmo tempo que protege da entrada de água do exterior.

Uma fase pensada para contribuir para a durabilidade e a eficiência da habitação, com o cuidado que dedicamos a cada detalhe.

Na Discovercasa, o conforto começa muito antes dos acabamentos.
👉 Quer construir a sua casa connosco? Descubra mais em:
🌐 www.discovercasa.pt
#Discovercasa #MétodoConstrutivo #ConstruçãoDeCasas #Isolamento #MembranaTranspirável #EficiênciaEnergética #ConfortoTérmico #Construção #CasaNova #Engenharia #Portugal',
  '', 'por_aprovar', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-11-01', 3, (select id from public.obras where nome = 'Ribamar'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Ribamar' and f.nome = 'Base de fundação'), 'Ribamar - BF', 'carrossel',
  '',
  '', 'ideia', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-11-01', 4, (select id from public.obras where nome = 'Gaia'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Gaia' and f.nome = 'Aumento'), 'Gaia - Aumento acabado', 'carrossel',
  '',
  '', 'ideia', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-12-01', 1, (select id from public.obras where nome = 'Oliveira de Azeméis'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Oliveira de Azeméis' and f.nome = 'Garantia'), 'Testemunho - Oliveira de Azemeis', 'video',
  '',
  '', 'ideia', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-12-01', 2, (select id from public.obras where nome = 'Ribamar'), (select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = 'Ribamar' and f.nome = 'Base de fundação'), 'Ribamar - BF', 'carrossel',
  '',
  '', 'ideia', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-12-01', 3, (select id from public.obras where nome = 'Matosinhos'), null, 'Matosinhos - ???', 'carrossel',
  '',
  '', 'ideia', 'Equipa');
insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values
  ('2026-12-01', 4, (select id from public.obras where nome = 'Casa dos Cães'), null, 'Cães - Natalicio', 'carrossel',
  '',
  '', 'ideia', 'Equipa');

insert into public.posts_media (post_id, caminho, miniatura, nome_ficheiro, mime, tamanho, largura, altura, ordem, criado_por_nome) values
  ((select id from public.posts where mes = '2026-07-01' and semana = 1 and titulo = 'Sobral - Estamos de volta // projeto custoias'), 'posts/2026-07-s1-f1__sobral-estamos-de-volta-projeto-custoias.jpg', 'miniaturas/2026-07-s1-f1__sobral-estamos-de-volta-projeto-custoias.jpg', 'sobral-estamos-de-volta-projeto-custoias-1.jpg', 'image/jpeg', 154490, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 1 and titulo = 'Sobral - Estamos de volta // projeto custoias'), 'posts/2026-07-s1-f2__sobral-estamos-de-volta-projeto-custoias.jpg', 'miniaturas/2026-07-s1-f2__sobral-estamos-de-volta-projeto-custoias.jpg', 'sobral-estamos-de-volta-projeto-custoias-2.jpg', 'image/jpeg', 193575, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 2 and titulo = 'Boelhe - BF'), 'posts/2026-07-s2-f1__boelhe-bf.jpg', 'miniaturas/2026-07-s2-f1__boelhe-bf.jpg', 'boelhe-bf-1.jpg', 'image/jpeg', 430063, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 2 and titulo = 'Boelhe - BF'), 'posts/2026-07-s2-f2__boelhe-bf.jpg', 'miniaturas/2026-07-s2-f2__boelhe-bf.jpg', 'boelhe-bf-2.jpg', 'image/jpeg', 385053, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 2 and titulo = 'Boelhe - BF'), 'posts/2026-07-s2-f3__boelhe-bf.jpg', 'miniaturas/2026-07-s2-f3__boelhe-bf.jpg', 'boelhe-bf-3.jpg', 'image/jpeg', 398494, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 2 and titulo = 'Boelhe - BF'), 'posts/2026-07-s2-f4__boelhe-bf.jpg', 'miniaturas/2026-07-s2-f4__boelhe-bf.jpg', 'boelhe-bf-4.jpg', 'image/jpeg', 406770, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 3 and titulo = 'Torres Vedras - Video da casa'), 'posts/2026-07-s3-f1__torres-vedras-video-da-casa.jpg', 'miniaturas/2026-07-s3-f1__torres-vedras-video-da-casa.jpg', 'torres-vedras-video-da-casa-1.jpg', 'image/jpeg', 269682, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 3 and titulo = 'Torres Vedras - Video da casa'), 'posts/2026-07-s3-f2__torres-vedras-video-da-casa.jpg', 'miniaturas/2026-07-s3-f2__torres-vedras-video-da-casa.jpg', 'torres-vedras-video-da-casa-2.jpg', 'image/jpeg', 152138, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 3 and titulo = 'Torres Vedras - Video da casa'), 'posts/2026-07-s3-f3__torres-vedras-video-da-casa.jpg', 'miniaturas/2026-07-s3-f3__torres-vedras-video-da-casa.jpg', 'torres-vedras-video-da-casa-3.jpg', 'image/jpeg', 236298, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 3 and titulo = 'Torres Vedras - Video da casa'), 'posts/2026-07-s3-f4__torres-vedras-video-da-casa.jpg', 'miniaturas/2026-07-s3-f4__torres-vedras-video-da-casa.jpg', 'torres-vedras-video-da-casa-4.jpg', 'image/jpeg', 218609, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 4 and titulo = 'Boelhe - Estrutura'), 'posts/2026-07-s4-f1__boelhe-estrutura.jpg', 'miniaturas/2026-07-s4-f1__boelhe-estrutura.jpg', 'boelhe-estrutura-1.jpg', 'image/jpeg', 344284, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 4 and titulo = 'Boelhe - Estrutura'), 'posts/2026-07-s4-f2__boelhe-estrutura.jpg', 'miniaturas/2026-07-s4-f2__boelhe-estrutura.jpg', 'boelhe-estrutura-2.jpg', 'image/jpeg', 337832, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 4 and titulo = 'Boelhe - Estrutura'), 'posts/2026-07-s4-f3__boelhe-estrutura.jpg', 'miniaturas/2026-07-s4-f3__boelhe-estrutura.jpg', 'boelhe-estrutura-3.jpg', 'image/jpeg', 284876, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-07-01' and semana = 4 and titulo = 'Boelhe - Estrutura'), 'posts/2026-07-s4-f4__boelhe-estrutura.jpg', 'miniaturas/2026-07-s4-f4__boelhe-estrutura.jpg', 'boelhe-estrutura-4.jpg', 'image/jpeg', 242323, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 1 and titulo = 'Matosinhos - BF'), 'posts/2026-08-s1-f1__matosinhos-bf.jpg', 'miniaturas/2026-08-s1-f1__matosinhos-bf.jpg', 'matosinhos-bf-1.jpg', 'image/jpeg', 340842, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 1 and titulo = 'Matosinhos - BF'), 'posts/2026-08-s1-f2__matosinhos-bf.jpg', 'miniaturas/2026-08-s1-f2__matosinhos-bf.jpg', 'matosinhos-bf-2.jpg', 'image/jpeg', 275850, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 1 and titulo = 'Matosinhos - BF'), 'posts/2026-08-s1-f3__matosinhos-bf.jpg', 'miniaturas/2026-08-s1-f3__matosinhos-bf.jpg', 'matosinhos-bf-3.jpg', 'image/jpeg', 265262, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 1 and titulo = 'Matosinhos - BF'), 'posts/2026-08-s1-f4__matosinhos-bf.jpg', 'miniaturas/2026-08-s1-f4__matosinhos-bf.jpg', 'matosinhos-bf-4.jpg', 'image/jpeg', 404095, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 3 and titulo = 'Boelhe - Casa'), 'posts/2026-08-s3-f1__boelhe-casa.jpg', 'miniaturas/2026-08-s3-f1__boelhe-casa.jpg', 'boelhe-casa-1.jpg', 'image/jpeg', 382016, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 3 and titulo = 'Boelhe - Casa'), 'posts/2026-08-s3-f2__boelhe-casa.jpg', 'miniaturas/2026-08-s3-f2__boelhe-casa.jpg', 'boelhe-casa-2.jpg', 'image/jpeg', 355155, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 3 and titulo = 'Boelhe - Casa'), 'posts/2026-08-s3-f3__boelhe-casa.jpg', 'miniaturas/2026-08-s3-f3__boelhe-casa.jpg', 'boelhe-casa-3.jpg', 'image/jpeg', 365361, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 3 and titulo = 'Boelhe - Casa'), 'posts/2026-08-s3-f4__boelhe-casa.jpg', 'miniaturas/2026-08-s3-f4__boelhe-casa.jpg', 'boelhe-casa-4.jpg', 'image/jpeg', 378363, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 4 and titulo = 'Cães - Analisar 1'), 'posts/2026-08-s4-f1__caes-analisar-1.jpg', 'miniaturas/2026-08-s4-f1__caes-analisar-1.jpg', 'caes-analisar-1-1.jpg', 'image/jpeg', 308842, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 4 and titulo = 'Cães - Analisar 1'), 'posts/2026-08-s4-f2__caes-analisar-1.jpg', 'miniaturas/2026-08-s4-f2__caes-analisar-1.jpg', 'caes-analisar-1-2.jpg', 'image/jpeg', 228860, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 4 and titulo = 'Cães - Analisar 1'), 'posts/2026-08-s4-f3__caes-analisar-1.jpg', 'miniaturas/2026-08-s4-f3__caes-analisar-1.jpg', 'caes-analisar-1-3.jpg', 'image/jpeg', 362988, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 4 and titulo = 'Cães - Analisar 1'), 'posts/2026-08-s4-f4__caes-analisar-1.jpg', 'miniaturas/2026-08-s4-f4__caes-analisar-1.jpg', 'caes-analisar-1-4.jpg', 'image/jpeg', 225526, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-09-01' and semana = 1 and titulo = 'Matosinhos - BF'), 'posts/2026-09-s1-f1__matosinhos-bf.jpg', 'miniaturas/2026-09-s1-f1__matosinhos-bf.jpg', 'matosinhos-bf-1.jpg', 'image/jpeg', 396613, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-09-01' and semana = 1 and titulo = 'Matosinhos - BF'), 'posts/2026-09-s1-f2__matosinhos-bf.jpg', 'miniaturas/2026-09-s1-f2__matosinhos-bf.jpg', 'matosinhos-bf-2.jpg', 'image/jpeg', 356502, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-09-01' and semana = 1 and titulo = 'Matosinhos - BF'), 'posts/2026-09-s1-f3__matosinhos-bf.jpg', 'miniaturas/2026-09-s1-f3__matosinhos-bf.jpg', 'matosinhos-bf-3.jpg', 'image/jpeg', 398581, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-09-01' and semana = 4 and titulo = 'Matosinhos - BF'), 'posts/2026-09-s4-f1__matosinhos-bf.jpg', 'miniaturas/2026-09-s4-f1__matosinhos-bf.jpg', 'matosinhos-bf-1.jpg', 'image/jpeg', 316193, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-09-01' and semana = 4 and titulo = 'Matosinhos - BF'), 'posts/2026-09-s4-f2__matosinhos-bf.jpg', 'miniaturas/2026-09-s4-f2__matosinhos-bf.jpg', 'matosinhos-bf-2.jpg', 'image/jpeg', 290565, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-09-01' and semana = 4 and titulo = 'Matosinhos - BF'), 'posts/2026-09-s4-f3__matosinhos-bf.jpg', 'miniaturas/2026-09-s4-f3__matosinhos-bf.jpg', 'matosinhos-bf-3.jpg', 'image/jpeg', 351394, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-09-01' and semana = 4 and titulo = 'Matosinhos - BF'), 'posts/2026-09-s4-f4__matosinhos-bf.jpg', 'miniaturas/2026-09-s4-f4__matosinhos-bf.jpg', 'matosinhos-bf-4.jpg', 'image/jpeg', 279717, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-10-01' and semana = 3 and titulo = 'Matosinhos - Estrutura'), 'posts/2026-10-s3-f1__matosinhos-estrutura.jpg', 'miniaturas/2026-10-s3-f1__matosinhos-estrutura.jpg', 'matosinhos-estrutura-1.jpg', 'image/jpeg', 237528, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-10-01' and semana = 3 and titulo = 'Matosinhos - Estrutura'), 'posts/2026-10-s3-f2__matosinhos-estrutura.jpg', 'miniaturas/2026-10-s3-f2__matosinhos-estrutura.jpg', 'matosinhos-estrutura-2.jpg', 'image/jpeg', 190133, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-10-01' and semana = 3 and titulo = 'Matosinhos - Estrutura'), 'posts/2026-10-s3-f3__matosinhos-estrutura.jpg', 'miniaturas/2026-10-s3-f3__matosinhos-estrutura.jpg', 'matosinhos-estrutura-3.jpg', 'image/jpeg', 285796, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-10-01' and semana = 3 and titulo = 'Matosinhos - Estrutura'), 'posts/2026-10-s3-f4__matosinhos-estrutura.jpg', 'miniaturas/2026-10-s3-f4__matosinhos-estrutura.jpg', 'matosinhos-estrutura-4.jpg', 'image/jpeg', 258830, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-10-01' and semana = 3 and titulo = 'Matosinhos - Estrutura'), 'posts/2026-10-s3-f5__matosinhos-estrutura.jpg', 'miniaturas/2026-10-s3-f5__matosinhos-estrutura.jpg', 'matosinhos-estrutura-5.jpg', 'image/jpeg', 307756, 1080, 1350, 5, 'Equipa'),
  ((select id from public.posts where mes = '2026-10-01' and semana = 4 and titulo = 'Ribamar - Mov Terras'), 'posts/2026-10-s4-f1__ribamar-mov-terras.jpg', 'miniaturas/2026-10-s4-f1__ribamar-mov-terras.jpg', 'ribamar-mov-terras-1.jpg', 'image/jpeg', 312186, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-10-01' and semana = 4 and titulo = 'Ribamar - Mov Terras'), 'posts/2026-10-s4-f2__ribamar-mov-terras.jpg', 'miniaturas/2026-10-s4-f2__ribamar-mov-terras.jpg', 'ribamar-mov-terras-2.jpg', 'image/jpeg', 294888, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-10-01' and semana = 4 and titulo = 'Ribamar - Mov Terras'), 'posts/2026-10-s4-f3__ribamar-mov-terras.jpg', 'miniaturas/2026-10-s4-f3__ribamar-mov-terras.jpg', 'ribamar-mov-terras-3.jpg', 'image/jpeg', 231850, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-10-01' and semana = 4 and titulo = 'Ribamar - Mov Terras'), 'posts/2026-10-s4-f4__ribamar-mov-terras.jpg', 'miniaturas/2026-10-s4-f4__ribamar-mov-terras.jpg', 'ribamar-mov-terras-4.jpg', 'image/jpeg', 315664, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-11-01' and semana = 1 and titulo = 'Gaia - Aumento estrutura'), 'posts/2026-11-s1-f1__gaia-aumento-estrutura.jpg', 'miniaturas/2026-11-s1-f1__gaia-aumento-estrutura.jpg', 'gaia-aumento-estrutura-1.jpg', 'image/jpeg', 200096, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-11-01' and semana = 1 and titulo = 'Gaia - Aumento estrutura'), 'posts/2026-11-s1-f2__gaia-aumento-estrutura.jpg', 'miniaturas/2026-11-s1-f2__gaia-aumento-estrutura.jpg', 'gaia-aumento-estrutura-2.jpg', 'image/jpeg', 286120, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-11-01' and semana = 1 and titulo = 'Gaia - Aumento estrutura'), 'posts/2026-11-s1-f3__gaia-aumento-estrutura.jpg', 'miniaturas/2026-11-s1-f3__gaia-aumento-estrutura.jpg', 'gaia-aumento-estrutura-3.jpg', 'image/jpeg', 257782, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-11-01' and semana = 1 and titulo = 'Gaia - Aumento estrutura'), 'posts/2026-11-s1-f4__gaia-aumento-estrutura.jpg', 'miniaturas/2026-11-s1-f4__gaia-aumento-estrutura.jpg', 'gaia-aumento-estrutura-4.jpg', 'image/jpeg', 287207, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-11-01' and semana = 2 and titulo = 'Matosinhos - Estrutura'), 'posts/2026-11-s2-f1__matosinhos-estrutura.jpg', 'miniaturas/2026-11-s2-f1__matosinhos-estrutura.jpg', 'matosinhos-estrutura-1.jpg', 'image/jpeg', 260388, 1080, 1350, 1, 'Equipa'),
  ((select id from public.posts where mes = '2026-11-01' and semana = 2 and titulo = 'Matosinhos - Estrutura'), 'posts/2026-11-s2-f2__matosinhos-estrutura.jpg', 'miniaturas/2026-11-s2-f2__matosinhos-estrutura.jpg', 'matosinhos-estrutura-2.jpg', 'image/jpeg', 359414, 1080, 1350, 2, 'Equipa'),
  ((select id from public.posts where mes = '2026-11-01' and semana = 2 and titulo = 'Matosinhos - Estrutura'), 'posts/2026-11-s2-f3__matosinhos-estrutura.jpg', 'miniaturas/2026-11-s2-f3__matosinhos-estrutura.jpg', 'matosinhos-estrutura-3.jpg', 'image/jpeg', 291943, 1080, 1350, 3, 'Equipa'),
  ((select id from public.posts where mes = '2026-11-01' and semana = 2 and titulo = 'Matosinhos - Estrutura'), 'posts/2026-11-s2-f4__matosinhos-estrutura.jpg', 'miniaturas/2026-11-s2-f4__matosinhos-estrutura.jpg', 'matosinhos-estrutura-4.jpg', 'image/jpeg', 182060, 1080, 1350, 4, 'Equipa'),
  ((select id from public.posts where mes = '2026-11-01' and semana = 2 and titulo = 'Matosinhos - Estrutura'), 'posts/2026-11-s2-f5__matosinhos-estrutura.jpg', 'miniaturas/2026-11-s2-f5__matosinhos-estrutura.jpg', 'matosinhos-estrutura-5.jpg', 'image/jpeg', 326641, 1080, 1350, 5, 'Equipa');

insert into public.posts_comentarios (post_id, media_id, texto, resolvido, autor_nome) values
  ((select id from public.posts where mes = '2026-08-01' and semana = 1 and titulo = 'Matosinhos - BF'), (select id from public.posts_media where caminho = 'posts/2026-08-s1-f4__matosinhos-bf.jpg'), 'já vi e está top', false, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 2 and titulo = 'Torres Vedras - Testemunho'), null, 'enviado ao cliente, à espera de aprovação', false, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 3 and titulo = 'Boelhe - Casa'), (select id from public.posts_media where caminho = 'posts/2026-08-s3-f3__boelhe-casa.jpg'), 'consegues tirar aquele saco?', true, 'Equipa'),
  ((select id from public.posts where mes = '2026-08-01' and semana = 3 and titulo = 'Boelhe - Casa'), (select id from public.posts_media where caminho = 'posts/2026-08-s3-f3__boelhe-casa.jpg'), 'imagina eu conseguir consigo com ai mas a imagem perde muita qualidade', true, 'Equipa');
