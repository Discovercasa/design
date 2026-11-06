// Dados do hub: o texto fixo de cada projeto (public/dados/projetos/<id>.json) e o que muda (Supabase: checkpoints,
// tarefas, decisões, perfis, vistos, notificações; migrações 0004/0005). Tudo passa por aqui.
// As redes sociais (obras, fases, posts) carregam-se em social-dados.js e ficam também em E.
import { carregarSocial } from './social-dados.js';

export const IDS = ['build_your_house', 'builder', 'gerador', 'orcamentacao', 'plataforma_cliente'];

export const E = {
  eu: { id: null, nome: '', editar: false },
  perfil: null,            // a minha linha em perfis
  projetos: [],            // JSON de cada projeto
  checkpoints: [], tarefas: [], decisoes: [], perfis: [], notificacoes: [], documentos: [],
  obras: [], fases: [], posts: [], media: [], comentarios: [], socialErro: null,   // redes sociais
  vistos: new Set(),       // "tarefa:12"
  novos: new Set(),        // o que é novo para mim nesta visita (mostra a etiqueta "Novo")
  erro: null,
};
const sb = () => window.Design.sb;

export const projeto = (id) => E.projetos.find((p) => p.id === id);
export const projetoPorSlug = (slug) => E.projetos.find((p) => p.slug === slug);
export const nomeProjeto = (id) => (projeto(id) || {}).nome || id;
export const checkpointsDe = (id) => E.checkpoints.filter((c) => c.projeto === id).sort((a, b) => a.ordem - b.ordem || a.id - b.id);
export const tarefasDe = (cpId) => E.tarefas.filter((t) => t.checkpoint_id === cpId).sort((a, b) => a.ordem - b.ordem || a.id - b.id);
export const decisaoDaTarefa = (tId) => E.decisoes.find((d) => d.tarefa_id === tId);
export const decisoesDe = (id) => E.decisoes.filter((d) => d.projeto === id);
export const chave = (tipo, id) => `${tipo}:${id}`;

export async function carregarProjetos() {
  E.projetos = await Promise.all(IDS.map((id) => fetch(`/dados/projetos/${id}.json`).then((r) => r.json())));
}

// perfil: cria a minha linha na primeira visita (o nome vem do Hub); depois fica o que eu escrever nas Definições
export async function garantirPerfil(sessao) {
  const id = sessao.user.id, nomeHub = (sessao.user.user_metadata && sessao.user.user_metadata.nome) || '';
  let { data, error } = await sb().from('perfis').select('*').eq('id', id).maybeSingle();
  if (error) throw error;
  if (!data) {
    ({ data, error } = await sb().from('perfis').insert({ id, nome: nomeHub }).select().single());
    if (error) throw error;
  }
  E.perfil = data;
  E.eu.nome = data.nome || nomeHub;
}

export async function carregarTudo() {
  const r = await Promise.all([
    sb().from('checkpoints').select('*').order('ordem'),
    sb().from('tarefas').select('*').order('ordem'),
    // duas ligações entre as tabelas (opção → decisão e decisão → opção escolhida): dizer qual se quer
    sb().from('decisoes').select('*, decisoes_opcoes!decisoes_opcoes_decisao_id_fkey(*)').order('criado_em'),
    sb().from('perfis').select('id, nome'),
    sb().from('vistos').select('tipo, ref_id'),
  ]);
  const [docs] = await Promise.all([
    sb().from('documentos').select('*').order('criado_em'),   // à parte: sem esta tabela o resto continua
    carregarSocial(),                                          // idem (migração 0009)
  ]);
  const falha = r.find((x) => x.error);
  if (falha) throw falha.error;
  [E.checkpoints, E.tarefas, E.decisoes, E.perfis] = r.map((x) => x.data);
  E.decisoes.forEach((d) => (d.decisoes_opcoes || []).sort((a, b) => a.ordem - b.ordem || a.id - b.id));
  E.vistos = new Set(r[4].data.map((v) => chave(v.tipo, v.ref_id)));
  E.documentos = docs.error ? [] : docs.data;
  E.erro = null;
}

// o que outra pessoa acrescentou depois da minha primeira visita e eu ainda não vi
export function porVer() {
  const desde = E.perfil ? new Date(E.perfil.criado_em) : new Date();
  const novo = (tipo, x) => x.criado_por && x.criado_por !== E.eu.id && new Date(x.criado_em) > desde && !E.vistos.has(chave(tipo, x.id));
  return [
    ...E.checkpoints.filter((x) => novo('checkpoint', x)).map((x) => ({ tipo: 'checkpoint', x })),
    ...E.tarefas.filter((x) => novo('tarefa', x)).map((x) => ({ tipo: 'tarefa', x })),
    ...E.decisoes.filter((x) => novo('decisao', x)).map((x) => ({ tipo: 'decisao', x })),
    ...E.documentos.filter((x) => novo('documento', x)).map((x) => ({ tipo: 'documento', x })),
    ...E.posts.filter((x) => novo('post', x)).map((x) => ({ tipo: 'post', x })),
    ...E.obras.filter((x) => novo('obra', x)).map((x) => ({ tipo: 'obra', x })),
  ];
}
export async function marcarVistos(itens) {
  if (!itens.length) return;
  itens.forEach((i) => E.vistos.add(chave(i.tipo, i.x.id)));
  await sb().from('vistos').insert(itens.map((i) => ({ tipo: i.tipo, ref_id: i.x.id })));
}

let notificacoesCarregadas = false;
export async function carregarNotificacoes() {
  const { data, error } = await sb().from('notificacoes').select('*').order('criada_em', { ascending: false }).limit(40);
  if (error) throw error;
  const antes = new Set(E.notificacoes.map((n) => n.id));
  const novas = notificacoesCarregadas ? data.filter((n) => !antes.has(n.id) && n.ator_id !== E.eu.id) : [];  // à 1.ª, nada é "nova"
  E.notificacoes = data;
  notificacoesCarregadas = true;
  return novas;
}
export const naoLidas = () => {
  const vistas = E.perfil ? new Date(E.perfil.notificacoes_vistas_em) : new Date(0);
  return E.notificacoes.filter((n) => n.ator_id !== E.eu.id && new Date(n.criada_em) > vistas);
};
export async function marcarNotificacoesLidas() {
  const agora = new Date().toISOString();
  E.perfil.notificacoes_vistas_em = agora;
  await sb().from('perfis').update({ notificacoes_vistas_em: agora }).eq('id', E.eu.id);
}
export async function mudarNome(nome) {
  const { error } = await sb().from('perfis').update({ nome }).eq('id', E.eu.id);
  if (error) throw error;
  E.perfil.nome = nome; E.eu.nome = nome;
}

// escrita: cada função devolve o erro (ou null) e volta a carregar
async function feito(p) { const { error } = await p; if (error) throw error; await carregarTudo(); }
// checkpoints entram na posição escolhida (1 = primeiro); os outros são renumerados na base de dados
export const criarCheckpoint = (c, posicao) => feito(sb().rpc('inserir_checkpoint', { p_projeto: c.projeto, p_titulo: c.titulo, p_descricao: c.descricao || '', p_posicao: posicao }));
export const moverCheckpoint = (id, posicao) => feito(sb().rpc('mover_checkpoint', { p_id: id, p_posicao: posicao }));
export const mudarCheckpoint = (id, campos) => feito(sb().from('checkpoints').update(campos).eq('id', id));
export const apagarCheckpoint = (id) => feito(sb().from('checkpoints').delete().eq('id', id));
export const criarTarefa = (t) => feito(sb().from('tarefas').insert(t));
export const mudarTarefa = (id, campos) => feito(sb().from('tarefas').update(campos).eq('id', id));
export const apagarTarefa = (id) => feito(sb().from('tarefas').delete().eq('id', id));
export async function criarDecisao(d, opcoes) {
  const { data, error } = await sb().from('decisoes').insert(d).select().single();
  if (error) throw error;
  const r = await sb().from('decisoes_opcoes').insert(opcoes.map((o, i) => ({ ...o, decisao_id: data.id, ordem: i + 1 })));
  if (r.error) { await sb().from('decisoes').delete().eq('id', data.id); throw r.error; }
  await carregarTudo();
}
export const decidir = (id, opcao, justificacao) => feito(sb().from('decisoes').update({ estado: 'decidida', opcao_escolhida: opcao, justificacao }).eq('id', id));
export const reabrirDecisao = (id) => feito(sb().from('decisoes').update({ estado: 'aberta' }).eq('id', id));
export const apagarDecisao = (id) => feito(sb().from('decisoes').delete().eq('id', id));

// números de cada projeto para o Início
export function resumo(id) {
  const cps = checkpointsDe(id);
  const feitos = cps.filter((c) => c.estado === 'concluido').length;
  const atual = cps.find((c) => c.estado === 'em_curso') || cps.find((c) => c.estado === 'por_fazer');
  const tarefasAbertas = atual ? tarefasDe(atual.id).filter((t) => t.estado !== 'concluida') : [];
  const proxima = tarefasAbertas.find((t) => t.estado === 'em_curso') || tarefasAbertas.find((t) => t.estado === 'por_fazer') || tarefasAbertas[0];
  const ultimo = feitosDe(id)[0];
  const abertas = decisoesDe(id).filter((d) => d.estado === 'aberta').length;
  return { cps, feitos, total: cps.length, atual, proxima, ultimo, abertas };
}
// o que foi feito e quando (só o dia): tarefas e checkpoints concluídos, mais recentes primeiro
export function feitosDe(id) {
  const t = E.tarefas.filter((x) => (!id || x.projeto === id) && x.estado === 'concluida' && x.concluida_em)
    .map((x) => ({ dia: x.concluida_em, texto: x.titulo, projeto: x.projeto, tipo: 'tarefa', id: x.id }));
  const d = E.decisoes.filter((x) => (!id || x.projeto === id) && x.estado === 'decidida' && x.decidida_em)
    .map((x) => ({ dia: x.decidida_em, texto: `Decidido: ${x.pergunta}`, projeto: x.projeto, tipo: 'decisao', id: x.id }));
  return [...t, ...d].sort((a, b) => (a.dia < b.dia ? 1 : a.dia > b.dia ? -1 : b.id - a.id));
}

// ---------------------------------------------------------------- documentos (armazenamento privado "documentos")
export const documentosDe = (id, tipo) => E.documentos.filter((d) => d.projeto === id && (!tipo || d.tipo === tipo));
const chaveFicheiro = (nome) => nome.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9._-]+/g, '-').replace(/-{2,}/g, '-').replace(/^[-.]+|[-.]+$/g, '') || 'ficheiro';
const MIMES = { pdf: 'application/pdf', md: 'text/plain; charset=utf-8', txt: 'text/plain; charset=utf-8', csv: 'text/csv', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp' };
export async function carregarDocumento(projetoId, tipo, ficheiro, titulo, descricao) {
  const ext = (ficheiro.name.split('.').pop() || '').toLowerCase();
  const mime = MIMES[ext] || ficheiro.type || 'application/octet-stream';
  const caminho = `${projetoId}/${tipo}/${Date.now().toString(36)}__${chaveFicheiro(ficheiro.name)}`;
  const up = await sb().storage.from('documentos').upload(caminho, ficheiro, { contentType: mime, upsert: false });
  if (up.error) throw up.error;
  const { error } = await sb().from('documentos').insert({ projeto: projetoId, tipo, titulo: titulo || ficheiro.name, descricao: descricao || '',
    caminho, nome_ficheiro: ficheiro.name, tamanho: ficheiro.size, mime });
  if (error) { await sb().storage.from('documentos').remove([caminho]); throw error; }
}
export async function urlDocumento(doc) {
  const descarregar = !/^(application\/pdf|text\/|image\/)/.test(doc.mime || '');
  const { data, error } = await sb().storage.from('documentos').createSignedUrl(doc.caminho, 300, descarregar ? { download: doc.nome_ficheiro } : undefined);
  if (error) throw error;
  return data.signedUrl;
}
export async function apagarDocumento(doc) {
  const { error } = await sb().from('documentos').delete().eq('id', doc.id);
  if (error) throw error;
  await sb().storage.from('documentos').remove([doc.caminho]);
  await carregarTudo();
}

// ---------------------------------------------------------------- em direto: qualquer mudança chega a quem tem o hub aberto
export function ouvirMudancas(aoMudar) {
  const canal = sb().channel('hub-mudancas');
  for (const t of ['checkpoints', 'tarefas', 'decisoes', 'decisoes_opcoes', 'documentos', 'notificacoes', 'obras', 'obras_fases', 'posts', 'posts_media', 'posts_comentarios'])
    canal.on('postgres_changes', { event: '*', schema: 'public', table: t }, () => aoMudar(t));
  canal.subscribe();
  return canal;
}
