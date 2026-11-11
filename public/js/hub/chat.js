// Chat da equipa (migração 0018, 2026-11-11): «mandar mensagem aos elementos que estão no hub … mandar mensagens, dar
// attach a ficheiros e a imagens/videos e mandar áudios». Conversas diretas (uma por par de pessoas) e de grupo; cada
// conversa só a veem os seus membros. Os ficheiros ficam no armazenamento privado "chat", numa pasta por conversa.
// O Claude não tem conta: escreve pela base de dados (autor_id null), numa conversa marcada claude = true.
import { E } from './dados.js';
import { $, $$, ic, esc, iniciais, aviso, abrirDialogo, dia, diaCurto } from './util.js';
import { reduzir, fazerMiniatura, nomeBase, assinar, urlEmCache, hidratar, img, abrirVisor } from './imagens.js';

const sb = () => window.Design.sb;
const BALDE = 'chat';
const MAXIMO = 50 * 1024 * 1024;   // o limite do armazenamento (50 MB por ficheiro)
const AUDIO_MAXIMO = 5 * 60;       // segundos: um áudio pára sozinho aos 5 minutos

const C = {
  conversas: [], membros: [], recentes: [],   // recentes: as últimas mensagens de todas as conversas (lista e por ler)
  mensagens: new Map(),                       // conversa -> mensagens, da mais antiga para a mais recente
  aberta: null, vista: 'lista', pendentes: [], rascunhos: new Map(),
  erro: '', aEnviar: false, gravar: null, avisadas: new Set(),
};
let dlg = null;

// ---------------------------------------------------------------- dados
const minhaLinha = (cid) => C.membros.find((m) => m.conversa_id === cid && m.utilizador_id === E.eu.id);
const nomePessoa = (id) => (E.perfis.find((p) => p.id === id) || {}).nome || 'Alguém';
const outros = (cid) => C.membros.filter((m) => m.conversa_id === cid && m.utilizador_id !== E.eu.id).map((m) => m.utilizador_id);
export function nomeConversa(c) {
  if (!c) return '';
  if (c.claude) return 'Claude';
  if (c.titulo) return c.titulo;
  const nomes = outros(c.id).map(nomePessoa);
  return nomes.join(', ') || 'Só tu';
}
const ultima = (cid) => C.recentes.find((m) => m.conversa_id === cid);
export function porLer(cid) {
  const l = minhaLinha(cid);
  if (!l) return 0;
  const desde = new Date(l.lida_em).getTime();
  return C.recentes.filter((m) => m.conversa_id === cid && m.autor_id !== E.eu.id && new Date(m.criada_em).getTime() > desde).length;
}
export const totalPorLer = () => C.conversas.reduce((s, c) => s + porLer(c.id), 0);

async function carregar() {
  const [c, m, r] = await Promise.all([
    sb().from('conversas').select('*').order('ultima_em', { ascending: false }),
    sb().from('conversas_membros').select('conversa_id, utilizador_id, lida_em'),
    sb().from('mensagens').select('id, conversa_id, autor_id, autor_nome, texto, anexos, criada_em').order('criada_em', { ascending: false }).limit(500),
  ]);
  const falha = [c, m, r].find((x) => x.error);
  if (falha) { C.erro = falha.error.message || String(falha.error); return; }
  C.erro = '';
  C.conversas = c.data; C.membros = m.data; C.recentes = r.data;
  C.conversas.sort((a, b) => new Date(b.ultima_em) - new Date(a.ultima_em));
}
async function carregarConversa(cid) {
  const { data, error } = await sb().from('mensagens').select('id, conversa_id, autor_id, autor_nome, texto, anexos, criada_em')
    .eq('conversa_id', cid).order('criada_em', { ascending: false }).limit(300);
  if (error) throw error;
  C.mensagens.set(cid, data.reverse());
}
// li a conversa até à última mensagem (a hora do servidor, para o relógio do aparelho não contar)
async function marcarLida(cid) {
  const l = minhaLinha(cid);
  const ms = C.mensagens.get(cid) || [];
  const ate = new Date(Math.max(Date.now(), ...ms.map((m) => new Date(m.criada_em).getTime() + 1))).toISOString();
  if (!l || !porLer(cid)) return;
  l.lida_em = ate;
  contador();
  await sb().from('conversas_membros').update({ lida_em: ate }).eq('conversa_id', cid).eq('utilizador_id', E.eu.id);
}

// ---------------------------------------------------------------- contador no botão do chat
function contador() {
  const n = totalPorLer(), el = $('#contador-chat'), b = $('#b-chat');
  if (!el || !b) return;
  el.hidden = !n; el.textContent = n > 9 ? '9+' : n;
  b.setAttribute('aria-label', n ? `Chat (${n} por ler)` : 'Chat');
}

// ---------------------------------------------------------------- texto
const hora = (d) => new Date(d).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });
function quando(d) {
  const x = new Date(d), h = new Date();
  if (x.toDateString() === h.toDateString()) return hora(d);
  const ontem = new Date(h); ontem.setDate(h.getDate() - 1);
  if (x.toDateString() === ontem.toDateString()) return 'ontem';
  return diaCurto(d);
}
function rotuloDia(d) {
  const x = new Date(d), h = new Date();
  if (x.toDateString() === h.toDateString()) return 'Hoje';
  const ontem = new Date(h); ontem.setDate(h.getDate() - 1);
  if (x.toDateString() === ontem.toDateString()) return 'Ontem';
  return dia(d);
}
const duracao = (s) => (s == null || !isFinite(s) ? '' : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`);
const tamanho = (b) => (b >= 1e6 ? `${(b / 1e6).toLocaleString('pt-PT', { maximumFractionDigits: 1 })} MB` : `${Math.max(1, Math.round(b / 1e3))} kB`);
const extensao = (nome) => (String(nome).split('.').pop() || '').toUpperCase().slice(0, 4);
const ligacoes = (t) => t.replace(/https?:\/\/[^\s<]+[^\s<.,;:!?)»"']/g, (u) => `<a href="${u}" target="_blank" rel="noopener">${u}</a>`);
const ROTULO_ANEXO = { imagem: 'Imagem', video: 'Vídeo', audio: 'Áudio', ficheiro: 'Ficheiro' };
function previa(m, c) {
  if (!m) return '<span class="fraco">Ainda sem mensagens</span>';
  const quem = m.autor_id === E.eu.id ? 'Tu: ' : c.grupo ? `${m.autor_nome}: ` : '';
  const a = (m.anexos || [])[0];
  const corpo = m.texto ? m.texto.replace(/\s+/g, ' ') : a ? `${ROTULO_ANEXO[a.tipo]}${a.tipo === 'audio' && a.duracao ? ` (${duracao(a.duracao)})` : a.tipo === 'ficheiro' ? `: ${a.nome}` : ''}${m.anexos.length > 1 ? ` e mais ${m.anexos.length - 1}` : ''}` : '';
  return esc(quem + corpo);
}
const avatarConversa = (c) => (c.claude ? '<span class="avatar chat-avatar claude" aria-hidden="true">C</span>'
  : c.grupo ? `<span class="avatar chat-avatar grupo" aria-hidden="true">${ic('pessoa', 'ic-sm')}</span>`
  : `<span class="avatar chat-avatar" aria-hidden="true">${esc(iniciais(nomeConversa(c)))}</span>`);

// ---------------------------------------------------------------- desenho
const fechar = '<button class="icone-botao" type="button" data-acao="fechar-dlg" aria-label="Fechar o chat">' + ic('fechar') + '</button>';
function htmlLista() {
  const pessoas = E.perfis.filter((p) => p.id !== E.eu.id && p.nome).sort((a, b) => a.nome.localeCompare(b.nome, 'pt'));
  const corpo = C.erro
    ? `<p class="erro-msg pequeno" style="padding:16px">O chat ainda não está disponível: ${esc(C.erro)}</p>`
    : `${C.conversas.length ? `<div class="chat-grupo-titulo">Conversas</div>${C.conversas.map((c) => {
        const n = porLer(c.id), u = ultima(c.id);
        return `<button type="button" class="chat-linha${n ? ' por-ler' : ''}" data-acao="chat-abrir" data-id="${c.id}">
          ${avatarConversa(c)}
          <span class="chat-linha-corpo"><span class="chat-linha-topo"><b>${esc(nomeConversa(c))}</b>${u ? `<time class="fraco mini" datetime="${esc(u.criada_em)}">${quando(u.criada_em)}</time>` : ''}</span>
            <span class="chat-previa">${previa(u, c)}</span></span>
          ${n ? `<span class="chat-n" aria-label="${n} por ler">${n > 99 ? '99+' : n}</span>` : '<span></span>'}
        </button>`;
      }).join('')}` : '<p class="vazio pequeno" style="margin:8px">Ainda sem conversas. Escolhe uma pessoa abaixo para lhe escrever.</p>'}
      <div class="chat-grupo-titulo">Pessoas do hub</div>
      ${pessoas.length ? `<div class="chat-pessoas">${pessoas.map((p) => `<button type="button" class="chat-pessoa" data-acao="chat-pessoa" data-pessoa="${esc(p.id)}" title="Escrever a ${esc(p.nome)}">
          <span class="avatar" aria-hidden="true">${esc(iniciais(p.nome))}</span><span>${esc(p.nome)}</span></button>`).join('')}</div>`
        : '<p class="fraco pequeno" style="padding:0 12px">Ainda não há mais ninguém no hub.</p>'}`;
  return `<div class="chat-conteudo">
    <div class="chat-topo"><div class="chat-topo-texto"><h2>Chat</h2><p class="fraco mini">Mensagens entre a equipa do hub. Cada conversa só a veem as pessoas que estão nela.</p></div>
      ${C.erro ? '' : `<button class="btn pequeno" type="button" data-acao="chat-grupo">${ic('mais', 'ic-sm')}Grupo</button>`}${fechar}</div>
    <div class="chat-lista">${corpo}</div>
  </div>`;
}
function htmlNovoGrupo() {
  const pessoas = E.perfis.filter((p) => p.id !== E.eu.id && p.nome).sort((a, b) => a.nome.localeCompare(b.nome, 'pt'));
  return `<div class="chat-conteudo">
    <div class="chat-topo"><button class="icone-botao" type="button" data-acao="chat-voltar" aria-label="Voltar às conversas">${ic('esquerda')}</button>
      <div class="chat-topo-texto"><h2>Novo grupo</h2><p class="fraco mini">Uma conversa com várias pessoas do hub.</p></div>${fechar}</div>
    <form class="chat-novo" id="chat-novo">
      <label class="campo-grupo"><span>Nome do grupo <small>(opcional)</small></span><input class="campo" name="titulo" maxlength="120" autocomplete="off" placeholder="ex.: Obra Torres Vedras"></label>
      <fieldset class="chat-escolher"><legend class="campo-grupo-titulo">Pessoas</legend>
        ${pessoas.map((p) => `<label class="aprovar"><input type="checkbox" class="visto" name="pessoa" value="${esc(p.id)}"><span>${esc(p.nome)}</span></label>`).join('') || '<p class="fraco pequeno">Ainda não há mais ninguém no hub.</p>'}
      </fieldset>
      <p class="erro-msg pequeno" role="alert"></p>
      <div><button class="btn primario" type="submit">Criar grupo</button></div>
    </form>
  </div>`;
}
function htmlConversa() {
  const c = C.conversas.find((x) => x.id === C.aberta);
  if (!c) return htmlLista();
  const sub = c.claude ? 'Responde aqui: o Claude lê as respostas.' : c.grupo ? [E.eu.nome || 'Tu', ...outros(c.id).map(nomePessoa)].join(', ') : 'Conversa privada';
  return `<div class="chat-conteudo">
    <div class="chat-topo"><button class="icone-botao" type="button" data-acao="chat-voltar" aria-label="Voltar às conversas">${ic('esquerda')}</button>
      ${avatarConversa(c)}<div class="chat-topo-texto"><h2>${esc(nomeConversa(c))}</h2><p class="fraco mini">${esc(sub)}</p></div>${fechar}</div>
    <div class="chat-mensagens" id="chat-mensagens" role="log" aria-label="Mensagens">${htmlMensagens(c)}</div>
    <form class="chat-escrever" id="chat-form" novalidate>
      <ul class="chat-pendentes" id="chat-pendentes"${C.pendentes.length ? '' : ' hidden'}>${htmlPendentes()}</ul>
      <div class="chat-linha-escrever" id="chat-linha-escrever">${htmlEscrever()}</div>
      <p class="chat-estado fraco mini" id="chat-estado" role="status"></p>
    </form>
  </div>`;
}
function htmlEscrever() {
  if (C.gravar) return `<div class="chat-gravacao"><span class="ponto-gravar" aria-hidden="true"></span><span class="num" id="chat-tempo">0:00</span><span class="fraco pequeno">A gravar áudio…</span></div>
    <button class="btn pequeno texto" type="button" data-acao="chat-audio-cancelar">Cancelar</button>
    <button class="icone-botao enviar" type="button" data-acao="chat-audio-enviar" aria-label="Parar e enviar o áudio" title="Parar e enviar">${ic('enviar')}</button>`;
  const texto = C.rascunhos.get(C.aberta) || '';
  return `<button class="icone-botao" type="button" data-acao="chat-escolher" data-qual="ficheiros" aria-label="Juntar ficheiros" title="Juntar ficheiros">${ic('clipe')}</button>
    <button class="icone-botao" type="button" data-acao="chat-escolher" data-qual="media" aria-label="Juntar fotos ou vídeos" title="Fotos ou vídeos">${ic('imagem')}</button>
    <input type="file" multiple data-chat-ficheiros="ficheiros" hidden><input type="file" multiple accept="image/*,video/*" data-chat-ficheiros="media" hidden>
    <textarea class="campo" id="chat-texto" name="texto" rows="1" maxlength="4000" placeholder="Escreve uma mensagem…" aria-label="Mensagem">${esc(texto)}</textarea>
    ${'MediaRecorder' in window && navigator.mediaDevices ? `<button class="icone-botao" type="button" data-acao="chat-audio" aria-label="Gravar um áudio" title="Gravar um áudio">${ic('micro')}</button>` : ''}
    <button class="icone-botao enviar" type="submit" aria-label="Enviar" title="Enviar">${ic('enviar')}</button>`;
}
const htmlPendentes = () => C.pendentes.map((f, i) => `<li>${ic(/^image\//.test(f.type) ? 'imagem' : /^video\//.test(f.type) ? 'video' : 'ficheiro', 'ic-sm')}<span class="chat-pendente-nome">${esc(f.name || 'imagem colada')}</span><span class="fraco">${tamanho(f.size)}</span>
  <button type="button" class="icone-botao" data-acao="chat-tirar" data-i="${i}" aria-label="Tirar ${esc(f.name || 'imagem')}">${ic('fechar', 'ic-sm')}</button></li>`).join('');

function htmlAnexos(m) {
  const as = m.anexos || [];
  if (!as.length) return '';
  const imagens = as.map((a, i) => ({ a, i })).filter((x) => x.a.tipo === 'imagem');
  let h = imagens.length ? `<div class="msg-imagens${imagens.length === 1 ? ' uma' : ''}">${imagens.map(({ a, i }) => `<button type="button" data-acao="chat-imagem" data-msg="${m.id}" data-i="${i}" title="${esc(a.nome)}">${img(BALDE, a.miniatura || a.caminho, a.nome)}</button>`).join('')}</div>` : '';
  for (const a of as) {
    if (a.tipo === 'video') h += `<video class="msg-video" controls playsinline preload="metadata" data-chat-src="${esc(a.caminho)}"${a.miniatura ? ` data-chat-poster="${esc(a.miniatura)}"` : ''} aria-label="Vídeo: ${esc(a.nome)}"></video>`;
    else if (a.tipo === 'audio') h += `<div class="msg-audio">${ic('micro', 'ic-sm')}<audio controls preload="metadata" data-chat-src="${esc(a.caminho)}" aria-label="Áudio${a.duracao ? ' de ' + duracao(a.duracao) : ''}"></audio>${a.duracao ? `<span class="fraco mini num">${duracao(a.duracao)}</span>` : ''}</div>`;
    else if (a.tipo === 'ficheiro') h += `<button type="button" class="msg-ficheiro" data-acao="chat-ficheiro" data-caminho="${esc(a.caminho)}" data-nome="${esc(a.nome)}" data-mime="${esc(a.mime || '')}">
        <span class="doc-tipo" aria-hidden="true">${esc(extensao(a.nome))}</span><span><span class="msg-ficheiro-nome">${esc(a.nome)}</span><span class="fraco mini">${tamanho(a.tamanho || 0)} · abrir</span></span></button>`;
  }
  return h;
}
function htmlMensagem(m, antes) {
  const minha = m.autor_id === E.eu.id, claude = !m.autor_id;
  const seguida = antes && antes.autor_id === m.autor_id && new Date(m.criada_em) - new Date(antes.criada_em) < 5 * 60 * 1000
    && new Date(m.criada_em).toDateString() === new Date(antes.criada_em).toDateString();
  return `<div class="msg${minha ? ' minha' : ''}${claude ? ' claude' : ''}${seguida ? ' seguida' : ''}" id="msg-${m.id}">
    ${!minha && !seguida ? `<span class="msg-autor">${esc(m.autor_nome || 'Alguém')}</span>` : ''}
    <div class="msg-linha">
      <div class="msg-bolha">${htmlAnexos(m)}${m.texto ? `<p class="msg-texto">${ligacoes(esc(m.texto))}</p>` : ''}<time class="msg-hora" datetime="${esc(m.criada_em)}">${hora(m.criada_em)}</time></div>
      ${minha ? `<button class="icone-botao msg-apagar" type="button" data-acao="chat-apagar" data-id="${m.id}" aria-label="Apagar esta mensagem" title="Apagar">${ic('apagar', 'ic-sm')}</button>` : ''}
    </div>
  </div>`;
}
function htmlMensagens(c) {
  const ms = C.mensagens.get(c.id);
  if (!ms) return '<p class="fraco pequeno chat-vazio">A carregar…</p>';
  if (!ms.length) return `<p class="fraco pequeno chat-vazio">${c.claude ? 'Ainda sem mensagens.' : `Ainda sem mensagens. Escreve a primeira${c.grupo ? '' : ' a ' + esc(nomeConversa(c))}.`}</p>`;
  let h = '', diaAntes = '';
  ms.forEach((m, i) => {
    const d = new Date(m.criada_em).toDateString();
    if (d !== diaAntes) { h += `<div class="chat-dia"><span>${rotuloDia(m.criada_em)}</span></div>`; diaAntes = d; }
    h += htmlMensagem(m, i ? ms[i - 1] : null);
  });
  return h;
}

function desenhar() {
  if (!dlg) return;
  guardarRascunho();
  dlg.innerHTML = C.vista === 'conversa' ? htmlConversa() : C.vista === 'grupo' ? htmlNovoGrupo() : htmlLista();
  if (C.vista === 'conversa') { prepararMedia(dlg); ajustarAltura(); fundo(true); }
}
function desenharMensagens() {
  const caixa = $('#chat-mensagens', dlg), c = C.conversas.find((x) => x.id === C.aberta);
  if (!caixa || !c) return;
  const noFundo = caixa.scrollHeight - caixa.scrollTop - caixa.clientHeight < 80;
  caixa.innerHTML = htmlMensagens(c);
  prepararMedia(caixa);
  if (noFundo) fundo(true);
}
function fundo(ja) {
  const caixa = $('#chat-mensagens', dlg);
  if (!caixa) return;
  caixa.scrollTop = caixa.scrollHeight;
  if (ja) requestAnimationFrame(() => { caixa.scrollTop = caixa.scrollHeight; });
}
// imagens (miniaturas), vídeos e áudios com os links assinados do armazenamento privado
async function prepararMedia(raiz) {
  hidratar(raiz).then(() => fundo(false));
  const els = $$('[data-chat-src], [data-chat-poster]', raiz);
  if (!els.length) return;
  await assinar(BALDE, els.flatMap((el) => [el.dataset.chatSrc, el.dataset.chatPoster]).filter(Boolean));
  els.forEach((el) => {
    if (el.dataset.chatPoster && !el.getAttribute('poster')) el.setAttribute('poster', urlEmCache(BALDE, el.dataset.chatPoster));
    if (el.dataset.chatSrc && !el.getAttribute('src')) el.setAttribute('src', urlEmCache(BALDE, el.dataset.chatSrc));
  });
}
function guardarRascunho() {
  const t = dlg && $('#chat-texto', dlg);
  if (t && C.aberta) C.rascunhos.set(C.aberta, t.value);
}
function ajustarAltura() {
  const t = $('#chat-texto', dlg);
  if (!t) return;
  t.style.height = 'auto';
  t.style.height = `${Math.min(160, t.scrollHeight + 2)}px`;
}
function estado(txt, erro = false) {
  const e = $('#chat-estado', dlg);
  if (e) { e.textContent = txt; e.classList.toggle('erro-msg', erro); }
}
function desenharPendentes() {
  const ul = $('#chat-pendentes', dlg);
  if (!ul) return;
  ul.innerHTML = htmlPendentes();
  ul.hidden = !C.pendentes.length;
}

// ---------------------------------------------------------------- abrir
export async function abrir(cid) {
  if (!dlg) return;
  if (!dlg.open) { C.vista = cid ? 'conversa' : 'lista'; C.aberta = cid || null; abrirDialogo(dlg, ''); desenhar(); }
  try { await carregar(); } catch (_) { /* fica o que havia */ }
  contador();
  if (cid) return abrirConversa(cid);
  if (C.vista === 'lista') desenhar();
}
async function abrirConversa(cid) {
  if (C.aberta !== cid) C.pendentes = [];
  C.aberta = cid; C.vista = 'conversa';
  if (!C.conversas.some((c) => c.id === cid)) await carregar();
  desenhar();
  try { await carregarConversa(cid); } catch (e) { estado('Não foi possível carregar as mensagens: ' + (e.message || e), true); return; }
  desenharMensagens();
  fundo(true);
  await marcarLida(cid);
  const t = $('#chat-texto', dlg);
  if (t && matchMedia('(hover: hover)').matches) t.focus({ preventScroll: true });
}

// ---------------------------------------------------------------- enviar (texto e anexos)
const tipoDe = (f) => (/^image\//.test(f.type) ? 'imagem' : /^video\//.test(f.type) ? 'video' : /^audio\//.test(f.type) ? 'audio' : 'ficheiro');
async function carregarAnexo(cid, original, extra = {}) {
  const tipo = tipoDe(original);
  if (original.size > MAXIMO) throw new Error(`«${original.name}» tem mais de 50 MB.`);
  let f = original;
  if (tipo === 'imagem') { try { f = await reduzir(original); } catch (_) { /* fica o original */ } }
  const nome = original.name && original.name !== 'image.png' ? original.name : `imagem-${new Date().toISOString().slice(0, 10)}.png`;
  const base = nomeBase(f === original ? nome : f.name || nome);
  const caminho = `${cid}/${base}`;
  let mini = null;
  if (tipo === 'imagem' || tipo === 'video') { try { mini = await fazerMiniatura(f); } catch (_) { /* sem miniatura */ } }
  const up = await sb().storage.from(BALDE).upload(caminho, f, { contentType: f.type || 'application/octet-stream', upsert: false });
  if (up.error) throw up.error;
  let miniatura = null;
  if (mini && mini.blob) {
    miniatura = `${cid}/mini-${base.replace(/\.[a-z0-9]+$/i, '')}.jpg`;
    const um = await sb().storage.from(BALDE).upload(miniatura, mini.blob, { contentType: 'image/jpeg', upsert: false });
    if (um.error) miniatura = null;
  }
  const anexo = { caminho, nome: f === original ? nome : f.name, mime: f.type || '', tamanho: f.size, tipo, ...extra };
  if (miniatura) anexo.miniatura = miniatura;
  if (mini) { anexo.largura = mini.largura; anexo.altura = mini.altura; }
  return anexo;
}
async function enviar(texto, ficheiros, extra = {}) {
  const cid = C.aberta;
  if (!cid || C.aEnviar || (!texto && !ficheiros.length)) return false;
  C.aEnviar = true;
  const feitos = [];
  try {
    for (const [i, f] of ficheiros.entries()) {
      estado(ficheiros.length > 1 ? `A carregar ${i + 1} de ${ficheiros.length}…` : `A carregar «${f.name || 'ficheiro'}»…`);
      feitos.push(await carregarAnexo(cid, f, extra));
    }
    estado('A enviar…');
    const { data, error } = await sb().from('mensagens').insert({ conversa_id: cid, texto, anexos: feitos }).select().single();
    if (error) throw error;
    const ms = C.mensagens.get(cid) || [];
    if (!ms.some((m) => m.id === data.id)) ms.push(data);
    C.mensagens.set(cid, ms);
    if (!C.recentes.some((m) => m.id === data.id)) C.recentes.unshift(data);
    const c = C.conversas.find((x) => x.id === cid);
    if (c) c.ultima_em = data.criada_em;
    estado('');
    desenharMensagens();
    fundo(true);
    return true;
  } catch (e) {
    const caminhos = feitos.flatMap((a) => [a.caminho, a.miniatura]).filter(Boolean);
    if (caminhos.length) sb().storage.from(BALDE).remove(caminhos).catch(() => {});
    estado('Não foi enviada: ' + (e.message || e), true);
    return false;
  } finally { C.aEnviar = false; }
}
async function enviarFormulario() {
  const t = $('#chat-texto', dlg);
  const texto = t ? t.value.trim() : '';
  const ficheiros = [...C.pendentes];
  if (!texto && !ficheiros.length) return;
  const botao = $('#chat-form [type=submit]', dlg);
  if (botao) botao.disabled = true;
  const ok = await enviar(texto, ficheiros);
  if (botao && botao.isConnected) botao.disabled = false;
  if (!ok) return;
  if (t) { t.value = ''; ajustarAltura(); }
  C.rascunhos.delete(C.aberta);
  C.pendentes = [];
  desenharPendentes();
}
function juntar(lista) {
  const fs = [...(lista || [])];
  if (!fs.length) return;
  const grandes = fs.filter((f) => f.size > MAXIMO);
  if (grandes.length) estado(`Demasiado grande (máximo 50 MB): ${grandes.map((f) => f.name).join(', ')}`, true);
  C.pendentes.push(...fs.filter((f) => f.size <= MAXIMO));
  if (C.pendentes.length > 10) { C.pendentes = C.pendentes.slice(0, 10); estado('No máximo 10 ficheiros por mensagem.', true); }
  desenharPendentes();
}

// ---------------------------------------------------------------- áudio (MediaRecorder: mp4/AAC onde houver, para tocar em todos)
async function gravar() {
  if (C.gravar) return;
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); } catch (e) {
    estado(e && e.name === 'NotAllowedError' ? 'O microfone está bloqueado: permite-o nas definições do browser para este site.' : 'Não foi possível usar o microfone: ' + (e.message || e), true);
    return;
  }
  const tipo = ['audio/mp4;codecs=mp4a.40.2', 'audio/mp4', 'audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus'].find((t) => MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)) || '';
  const rec = new MediaRecorder(stream, tipo ? { mimeType: tipo } : undefined);
  const g = { rec, stream, partes: [], inicio: Date.now(), cancelado: false, relogio: null };
  rec.ondataavailable = (e) => { if (e.data && e.data.size) g.partes.push(e.data); };
  rec.onstop = async () => {
    clearInterval(g.relogio);
    stream.getTracks().forEach((t) => t.stop());
    C.gravar = null;
    const linha = $('#chat-linha-escrever', dlg);
    if (linha) { linha.innerHTML = htmlEscrever(); ajustarAltura(); }
    if (g.cancelado || !g.partes.length) return;
    const mime = (rec.mimeType || tipo || 'audio/webm').split(';')[0];
    const ext = mime.includes('mp4') ? 'm4a' : mime.includes('ogg') ? 'ogg' : 'webm';
    const agora = new Date();
    const nome = `audio-${agora.toISOString().slice(0, 10)}-${String(agora.getHours()).padStart(2, '0')}${String(agora.getMinutes()).padStart(2, '0')}.${ext}`;
    const f = new File(g.partes, nome, { type: mime });
    await enviar('', [f], { duracao: Math.round((Date.now() - g.inicio) / 100) / 10 });
  };
  rec.start(250);
  C.gravar = g;
  const linha = $('#chat-linha-escrever', dlg);
  if (linha) linha.innerHTML = htmlEscrever();
  g.relogio = setInterval(() => {
    const s = (Date.now() - g.inicio) / 1000, el = $('#chat-tempo', dlg);
    if (el) el.textContent = duracao(Math.floor(s));
    if (s >= AUDIO_MAXIMO) pararGravacao(false);
  }, 250);
}
function pararGravacao(cancelar) {
  const g = C.gravar;
  if (!g) return;
  g.cancelado = cancelar;
  if (g.rec.state !== 'inactive') g.rec.stop();
}

// ---------------------------------------------------------------- em direto (Realtime) e o aviso de mensagem nova
let espera = null;
function aoMudar() {
  clearTimeout(espera);
  espera = setTimeout(atualizar, 250);
}
export async function atualizar() {
  const antes = new Set(C.recentes.map((m) => m.id));
  try { await carregar(); } catch (_) { return; }
  const novas = C.recentes.filter((m) => !antes.has(m.id) && m.autor_id !== E.eu.id && !C.avisadas.has(m.id));
  const aberta = dlg && dlg.open && C.vista === 'conversa' ? C.aberta : null;
  if (aberta) {
    try { await carregarConversa(aberta); } catch (_) { /* fica a que havia */ }
    if (!C.conversas.some((c) => c.id === aberta)) { C.vista = 'lista'; C.aberta = null; desenhar(); }
    else { desenharMensagens(); if (!document.hidden) await marcarLida(aberta); }
  } else if (dlg && dlg.open && C.vista === 'lista') desenhar();
  contador();
  novas.filter((m) => m.conversa_id !== aberta || document.hidden).slice(0, 3).forEach((m) => {
    C.avisadas.add(m.id);
    const c = C.conversas.find((x) => x.id === m.conversa_id);
    aviso(`<b>${esc(c && c.grupo ? `${m.autor_nome} em ${nomeConversa(c)}` : m.autor_nome || 'Mensagem nova')}</b><br>${previa({ ...m, autor_id: null }, { grupo: false })}`,
      { icone: 'chat', duracao: 8, acoes: [{ rotulo: 'Abrir', fazer: () => abrir(m.conversa_id) }] });
  });
}

// ---------------------------------------------------------------- arranque e eventos (tudo dentro da janela do chat)
export async function iniciar() {
  dlg = $('#chat');
  const b = $('#b-chat');
  if (!dlg || !b) return;
  b.innerHTML = ic('chat') + '<span class="contador" id="contador-chat" hidden></span>';
  b.addEventListener('click', () => abrir());
  try { await carregar(); } catch (_) { /* sem a migração 0018: o chat diz porquê ao abrir */ }
  contador();
  if (!C.erro) {
    const canal = sb().channel('hub-chat');
    for (const t of ['mensagens', 'conversas', 'conversas_membros']) canal.on('postgres_changes', { event: '*', schema: 'public', table: t }, aoMudar);
    canal.subscribe();
    const n = totalPorLer();
    if (n) {
      const c = C.conversas.find((x) => porLer(x.id));
      aviso(`<b>${n === 1 ? 'Tens 1 mensagem por ler' : `Tens ${n} mensagens por ler`}</b> no chat${c ? ` (${esc(nomeConversa(c))})` : ''}.`,
        { icone: 'chat', duracao: 10, acoes: [{ rotulo: 'Abrir', fazer: () => abrir(c ? c.id : undefined) }] });
    }
  }

  dlg.addEventListener('click', async (e) => {
    const el = e.target.closest('[data-acao]');
    if (!el) return;
    switch (el.dataset.acao) {
      case 'chat-abrir': return abrirConversa(Number(el.dataset.id));
      case 'chat-voltar': guardarRascunho(); pararGravacao(true); C.vista = 'lista'; C.aberta = null; desenhar(); return;
      case 'chat-grupo': C.vista = 'grupo'; desenhar(); return;
      case 'chat-pessoa': {
        el.disabled = true;
        const { data, error } = await sb().rpc('abrir_conversa', { p_membros: [el.dataset.pessoa], p_titulo: '' });
        el.disabled = false;
        if (error) { aviso('Não foi possível abrir a conversa: ' + esc(error.message), { icone: 'atencao' }); return; }
        await carregar();
        return abrirConversa(Number(data));
      }
      case 'chat-escolher': { const i = $(`[data-chat-ficheiros="${el.dataset.qual}"]`, dlg); if (i) i.click(); return; }
      case 'chat-tirar': C.pendentes.splice(Number(el.dataset.i), 1); desenharPendentes(); return;
      case 'chat-audio': return gravar();
      case 'chat-audio-cancelar': return pararGravacao(true);
      case 'chat-audio-enviar': return pararGravacao(false);
      case 'chat-imagem': {
        const m = (C.mensagens.get(C.aberta) || []).find((x) => x.id === Number(el.dataset.msg));
        if (!m) return;
        const imagens = m.anexos.filter((a) => a.tipo === 'imagem');
        return abrirVisor(imagens.map((a) => ({ balde: BALDE, caminho: a.caminho, nome: a.nome })), imagens.indexOf(m.anexos[Number(el.dataset.i)]));
      }
      case 'chat-ficheiro': {
        const janela = window.open('about:blank', '_blank');   // já, para o browser não bloquear a janela
        const ver = /^(application\/pdf|text\/|image\/|video\/|audio\/)/.test(el.dataset.mime || '');
        const { data, error } = await sb().storage.from(BALDE).createSignedUrl(el.dataset.caminho, 300, ver ? undefined : { download: el.dataset.nome });
        if (error) { if (janela) janela.close(); aviso('Não foi possível abrir o ficheiro: ' + esc(error.message), { icone: 'atencao' }); return; }
        if (janela) janela.location.href = data.signedUrl; else location.href = data.signedUrl;
        return;
      }
      case 'chat-apagar': {
        const m = (C.mensagens.get(C.aberta) || []).find((x) => x.id === Number(el.dataset.id));
        if (!m || !confirm('Apagar esta mensagem? Deixa de aparecer para toda a gente na conversa.')) return;
        const { error } = await sb().from('mensagens').delete().eq('id', m.id);
        if (error) { aviso('Não foi possível apagar: ' + esc(error.message), { icone: 'atencao' }); return; }
        const caminhos = (m.anexos || []).flatMap((a) => [a.caminho, a.miniatura]).filter(Boolean);
        if (caminhos.length) sb().storage.from(BALDE).remove(caminhos).catch(() => {});
        C.mensagens.set(C.aberta, (C.mensagens.get(C.aberta) || []).filter((x) => x.id !== m.id));
        C.recentes = C.recentes.filter((x) => x.id !== m.id);
        desenharMensagens();
        return;
      }
    }
  });
  dlg.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (e.target.id === 'chat-form') return enviarFormulario();
    if (e.target.id === 'chat-novo') {
      const f = e.target, ids = [...f.querySelectorAll('input[name=pessoa]:checked')].map((x) => x.value);
      if (!ids.length) { $('.erro-msg', f).textContent = 'Escolhe pelo menos uma pessoa.'; return; }
      const { data, error } = await sb().rpc('abrir_conversa', { p_membros: ids, p_titulo: f.elements.titulo.value.trim() });
      if (error) { $('.erro-msg', f).textContent = 'Não foi possível criar: ' + error.message; return; }
      await carregar();
      return abrirConversa(Number(data));
    }
  });
  dlg.addEventListener('change', (e) => {
    if (!e.target.matches('[data-chat-ficheiros]')) return;
    juntar(e.target.files);
    e.target.value = '';
  });
  dlg.addEventListener('input', (e) => { if (e.target.id === 'chat-texto') ajustarAltura(); });
  dlg.addEventListener('keydown', (e) => {
    // Enter envia no computador; no telemóvel muda de linha (envia-se com o botão)
    if (e.target.id === 'chat-texto' && e.key === 'Enter' && !e.shiftKey && !e.isComposing && matchMedia('(hover: hover)').matches) {
      e.preventDefault();
      enviarFormulario();
    }
  });
  dlg.addEventListener('paste', (e) => {
    if (C.vista !== 'conversa' || !e.clipboardData || !e.clipboardData.files.length) return;
    e.preventDefault();
    juntar(e.clipboardData.files);
  });
  dlg.addEventListener('dragover', (e) => { if (C.vista === 'conversa' && [...(e.dataTransfer.types || [])].includes('Files')) { e.preventDefault(); dlg.classList.add('sobre'); } });
  dlg.addEventListener('dragleave', (e) => { if (!dlg.contains(e.relatedTarget)) dlg.classList.remove('sobre'); });
  dlg.addEventListener('drop', (e) => {
    dlg.classList.remove('sobre');
    if (C.vista !== 'conversa' || !e.dataTransfer.files.length) return;
    e.preventDefault();
    juntar(e.dataTransfer.files);
  });
  dlg.addEventListener('close', () => { guardarRascunho(); pararGravacao(true); });
}
