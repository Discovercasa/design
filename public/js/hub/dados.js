// Dados do hub: o texto fixo de cada projeto (public/dados/projetos/<id>.json) e o que muda (Supabase: checkpoints,
// tarefas, decisões, perfis, vistos, notificações; migrações 0004/0005). Tudo passa por aqui.
// As redes sociais (obras, fases, posts) carregam-se em social-dados.js e ficam também em E.
import { carregarSocial } from './social-dados.js';
import { reduzir, fazerMiniatura, nomeBase } from './imagens.js';

// ordem das abas e das listas (pedido de 2026-11-06)
export const IDS = ['gerador', 'builder', 'orcamentacao', 'build_your_house', 'plataforma_cliente'];

export const E = {
  eu: { id: null, nome: '', editar: false },
  perfil: null,            // a minha linha em perfis
  projetos: [],            // JSON de cada projeto
  checkpoints: [], tarefas: [], decisoes: [], perfis: [], notificacoes: [], documentos: [],
  obras: [], fases: [], posts: [], media: [], comentarios: [], socialErro: null,   // redes sociais
  notas: [], anexos: [],  // notas de teste/revisão e imagens anexadas (migração 0011)
  lidas: new Set(),        // notificações que já vi (migração 0014)
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
  const [docs, notas, anexos] = await Promise.all([
    sb().from('documentos').select('*').order('criado_em'),   // à parte: sem esta tabela o resto continua
    sb().from('tarefas_notas').select('*').order('criado_em'), // idem (migração 0011)
    sb().from('anexos').select('*').order('ordem'),
    carregarSocial(),                                          // idem (migração 0009)
  ]);
  const falha = r.find((x) => x.error);
  if (falha) throw falha.error;
  [E.checkpoints, E.tarefas, E.decisoes, E.perfis] = r.map((x) => x.data);
  E.decisoes.forEach((d) => (d.decisoes_opcoes || []).sort((a, b) => a.ordem - b.ordem || a.id - b.id));
  E.vistos = new Set(r[4].data.map((v) => chave(v.tipo, v.ref_id)));
  E.documentos = docs.error ? [] : docs.data;
  E.notas = notas.error ? [] : notas.data;
  E.anexos = anexos.error ? [] : anexos.data;
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
  const l = await sb().from('notificacoes_lidas').select('notificacao_id').order('lida_em', { ascending: false }).limit(1000);
  if (!l.error) E.lidas = new Set(l.data.map((x) => x.notificacao_id));   // sem a tabela (antes da 0014) fica como estava
  return novas;
}
// por ver: de outra pessoa, ainda sem "visto" meu e depois de "Marcar todas como vistas"; as minhas próprias ações não contam
export const propria = (n) => !!n.ator_id && n.ator_id === E.eu.id;
export const ehPorVer = (n) => {
  const vistas = E.perfil ? new Date(E.perfil.notificacoes_vistas_em) : new Date(0);
  return !propria(n) && !E.lidas.has(n.id) && new Date(n.criada_em) > vistas;
};
export const naoLidas = () => E.notificacoes.filter(ehPorVer);
// vista ao passar o rato (0,6 s), ao clicar ou ao tocar no ponto; o ponto também a volta a pôr por ver
export async function marcarLida(id, lida = true) {
  if (lida === E.lidas.has(id)) return;
  if (lida) E.lidas.add(id); else E.lidas.delete(id);
  const r = lida ? await sb().from('notificacoes_lidas').insert({ notificacao_id: id })
    : await sb().from('notificacoes_lidas').delete().eq('notificacao_id', id).eq('utilizador_id', E.eu.id);
  if (r.error && !/duplicate/i.test(r.error.message || '')) { if (lida) E.lidas.delete(id); else E.lidas.add(id); throw r.error; }
}
export async function marcarNotificacoesLidas() {
  const por = naoLidas().map((n) => n.id);
  por.forEach((id) => E.lidas.add(id));
  if (por.length) await sb().from('notificacoes_lidas').insert(por.map((id) => ({ notificacao_id: id })));
  const agora = new Date().toISOString();   // e as mais antigas, que não estão na lista
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
export async function criarCheckpoint(c, posicao) {
  const { data, error } = await sb().rpc('inserir_checkpoint', { p_projeto: c.projeto, p_titulo: c.titulo, p_descricao: c.descricao || '', p_posicao: posicao });
  if (error) throw error;
  if (c.criterio_saida) { const r = await sb().from('checkpoints').update({ criterio_saida: c.criterio_saida }).eq('id', data); if (r.error) throw r.error; }
  await carregarTudo();
  return data;
}
export const moverCheckpoint = (id, posicao) => feito(sb().rpc('mover_checkpoint', { p_id: id, p_posicao: posicao }));
export const mudarCheckpoint = (id, campos) => feito(sb().from('checkpoints').update(campos).eq('id', id));
export async function apagarCheckpoint(id) {
  const ficheiros = ficheirosDe('checkpoint', id);
  await feito(sb().from('checkpoints').delete().eq('id', id));
  apagarFicheiros(ficheiros);
}
export const criarTarefa = (t) => feito(sb().from('tarefas').insert(t));
export const mudarTarefa = (id, campos) => feito(sb().from('tarefas').update(campos).eq('id', id));
export async function apagarTarefa(id) {
  const ficheiros = ficheirosDe('tarefa', id);
  await feito(sb().from('tarefas').delete().eq('id', id));
  apagarFicheiros(ficheiros);
}
export async function criarDecisao(d, opcoes) {
  const { data, error } = await sb().from('decisoes').insert(d).select().single();
  if (error) throw error;
  const r = await sb().from('decisoes_opcoes').insert(opcoes.map((o, i) => ({ ...o, decisao_id: data.id, ordem: i + 1 })));
  if (r.error) { await sb().from('decisoes').delete().eq('id', data.id); throw r.error; }
  await carregarTudo();
}
export const decidir = (id, opcao, justificacao) => feito(sb().from('decisoes').update({ estado: 'decidida', opcao_escolhida: opcao, justificacao }).eq('id', id));
// uma opção nova numa decisão em aberto (a base de dados avisa a equipa)
export const acrescentarOpcao = (decisao, o) => feito(sb().rpc('acrescentar_opcao', { p_decisao: decisao, p_titulo: o.titulo, p_descricao: o.descricao || '',
  p_vantagens: o.vantagens || '', p_desvantagens: o.desvantagens || '', p_custo: o.custo || '' }));
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
const MIMES = { pdf: 'application/pdf', md: 'text/plain; charset=utf-8', txt: 'text/plain; charset=utf-8', csv: 'text/csv', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp',
  usdz: 'model/vnd.usdz+zip', glb: 'model/gltf-binary' };   // AR: the phone's viewer needs the right type
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
  const descarregar = !/^(application\/pdf|text\/|image\/|model\/)/.test(doc.mime || '');
  const { data, error } = await sb().storage.from('documentos').createSignedUrl(doc.caminho, 300, descarregar ? { download: doc.nome_ficheiro } : undefined);
  if (error) throw error;
  return data.signedUrl;
}
// AR models (Step Inside): a signed link that the phone's AR viewer opens directly (Quick Look / Scene Viewer fetch it)
export async function urlAR(doc, segundos = 3600) {
  const { data, error } = await sb().storage.from('documentos').createSignedUrl(doc.caminho, segundos);
  if (error) throw error;
  return new URL(data.signedUrl, location.href).href;   // absolute: Scene Viewer fetches it from another app
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
  for (const t of ['checkpoints', 'tarefas', 'decisoes', 'decisoes_opcoes', 'documentos', 'notificacoes', 'obras', 'obras_fases', 'posts', 'posts_media', 'posts_comentarios', 'tarefas_notas', 'anexos', 'notificacoes_lidas'])
    canal.on('postgres_changes', { event: '*', schema: 'public', table: t }, () => aoMudar(t));
  canal.subscribe();
  return canal;
}

// ---------------------------------------------------------------- notas de teste/revisão (bugs, a mudar, a fazer)
export const TIPOS_NOTA = { bug: 'Bug', mudar: 'A mudar', fazer: 'A fazer', nota: 'Nota' };
export const notasDe = (tarefaId) => E.notas.filter((n) => n.tarefa_id === tarefaId)
  .sort((a, b) => (a.resolvida - b.resolvida) || (new Date(a.criado_em) - new Date(b.criado_em)));
export const podeMexerNota = (n) => E.eu.editar || n.autor_id === E.eu.id;
export async function criarNota(tarefaId, tipo, texto, imagens = []) {
  const { data, error } = await sb().from('tarefas_notas').insert({ tarefa_id: tarefaId, tipo, texto, autor_nome: E.eu.nome }).select().single();
  if (error) throw error;
  for (const [i, f] of imagens.entries()) await carregarAnexo('nota', data.id, f, i + 1);
  await carregarTudo();
  return data;
}
export const mudarNota = (id, campos) => feito(sb().from('tarefas_notas').update(campos).eq('id', id));
export async function apagarNota(n) {
  const ficheiros = ficheirosDe('nota', n.id);
  await feito(sb().from('tarefas_notas').delete().eq('id', n.id));
  apagarFicheiros(ficheiros);
}
// "Passar a tarefa": uma tarefa nova no mesmo checkpoint, com o texto da nota; a nota fica ligada a ela
export async function passarNotaATarefa(n) {
  const t = E.tarefas.find((x) => x.id === n.tarefa_id);
  const titulo = (n.texto.split('\n')[0] || n.texto).slice(0, 140).trim() + (n.texto.length > 140 ? '…' : '');
  const { data, error } = await sb().from('tarefas').insert({ checkpoint_id: t.checkpoint_id, projeto: t.projeto, titulo: titulo.length >= 2 ? titulo : 'Nota do teste',
    descricao: `${TIPOS_NOTA[n.tipo]} encontrado em «${t.titulo}»:\n${n.texto}`, ordem: tarefasDe(t.checkpoint_id).length + 1 }).select().single();
  if (error) throw error;
  await feito(sb().from('tarefas_notas').update({ tarefa_criada_id: data.id }).eq('id', n.id));
  return data;
}

// ---------------------------------------------------------------- imagens anexadas (armazenamento privado "anexos")
export const anexosDe = (alvo, id) => E.anexos.filter((a) => a.alvo === alvo && a.ref_id === id).sort((a, b) => a.ordem - b.ordem || a.id - b.id);
export const visorDe = (lista) => lista.map((a) => ({ balde: 'anexos', caminho: a.caminho, nome: a.nome_ficheiro }));
export async function carregarAnexo(alvo, refId, ficheiro, ordem) {
  try { ficheiro = await reduzir(ficheiro); } catch (_) { /* fica o original */ }
  const nome = ficheiro.name && ficheiro.name !== 'image.png' ? ficheiro.name : `imagem-${new Date().toISOString().slice(0, 10)}.png`;
  const base = nomeBase(nome);
  const caminho = `${alvo}/${base}`;
  let mini = null;
  try { mini = await fazerMiniatura(ficheiro); } catch (_) { /* sem miniatura */ }
  const up = await sb().storage.from('anexos').upload(caminho, ficheiro, { contentType: ficheiro.type || 'image/jpeg', upsert: false });
  if (up.error) throw up.error;
  let miniatura = null;
  if (mini && mini.blob) {
    miniatura = `miniaturas/${alvo}-${base.replace(/\.[a-z0-9]+$/, '')}.jpg`;
    const um = await sb().storage.from('anexos').upload(miniatura, mini.blob, { contentType: 'image/jpeg', upsert: false });
    if (um.error) miniatura = null;
  }
  const { error } = await sb().from('anexos').insert({ alvo, ref_id: refId, caminho, miniatura, nome_ficheiro: nome, mime: ficheiro.type || '',
    tamanho: ficheiro.size, largura: mini ? mini.largura : null, altura: mini ? mini.altura : null, ordem: ordem || anexosDe(alvo, refId).length + 1 });
  if (error) { await sb().storage.from('anexos').remove([caminho, miniatura].filter(Boolean)); throw error; }
}
export async function apagarAnexo(a) {
  const { error } = await sb().from('anexos').delete().eq('id', a.id);
  if (error) throw error;
  apagarFicheiros([a.caminho, a.miniatura]);
  await carregarTudo();
}
// os ficheiros de um checkpoint (e das suas tarefas e notas), de uma tarefa (e das suas notas) ou de uma nota
function ficheirosDe(alvo, id) {
  const tarefas = alvo === 'checkpoint' ? E.tarefas.filter((t) => t.checkpoint_id === id).map((t) => t.id) : alvo === 'tarefa' ? [id] : [];
  const notas = alvo === 'nota' ? [id] : E.notas.filter((n) => tarefas.includes(n.tarefa_id)).map((n) => n.id);
  return E.anexos.filter((a) => (a.alvo === 'checkpoint' && alvo === 'checkpoint' && a.ref_id === id) || (a.alvo === 'tarefa' && tarefas.includes(a.ref_id))
    || (a.alvo === 'nota' && notas.includes(a.ref_id))).flatMap((a) => [a.caminho, a.miniatura]);
}
function apagarFicheiros(caminhos) {
  const c = caminhos.filter(Boolean);
  if (c.length) sb().storage.from('anexos').remove(c).catch(() => {});
}

