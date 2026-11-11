// A conversa de uma tarefa ou checkpoint (e os anexos das críticas): mensagens com ficheiros, imagens/vídeos e áudios
// gravados no próprio browser. Os ficheiros ficam no armazenamento privado "chat" (migração 0022), numa pasta por
// tarefa (tarefa-12/…), por checkpoint (checkpoint-3/…) ou nas críticas (critica/…). Veio do chat geral (2026-11-11),
// que o utilizador trocou por uma conversa dentro de cada tarefa.
import { E } from './dados.js';
import { $, $$, ic, esc, dia, diaCurto } from './util.js';
import { reduzir, fazerMiniatura, nomeBase, assinar, urlEmCache, hidratar, img, abrirVisor } from './imagens.js';

const sb = () => window.Design.sb;
export const BALDE = 'chat';
export const MAXIMO = 50 * 1024 * 1024;   // o limite do armazenamento (50 MB por ficheiro)
const AUDIO_MAXIMO = 5 * 60;              // segundos: um áudio pára sozinho aos 5 minutos

// ---------------------------------------------------------------- texto
export const hora = (d) => new Date(d).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });
export function quando(d) {
  const x = new Date(d), h = new Date();
  if (x.toDateString() === h.toDateString()) return hora(d);
  const ontem = new Date(h); ontem.setDate(h.getDate() - 1);
  if (x.toDateString() === ontem.toDateString()) return 'ontem';
  return diaCurto(d);
}
export function rotuloDia(d) {
  const x = new Date(d), h = new Date();
  if (x.toDateString() === h.toDateString()) return 'Hoje';
  const ontem = new Date(h); ontem.setDate(h.getDate() - 1);
  if (x.toDateString() === ontem.toDateString()) return 'Ontem';
  return dia(d);
}
export const duracao = (s) => (s == null || !isFinite(s) ? '' : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`);
export const tamanho = (b) => (b >= 1e6 ? `${(b / 1e6).toLocaleString('pt-PT', { maximumFractionDigits: 1 })} MB` : `${Math.max(1, Math.round(b / 1e3))} kB`);
const extensao = (nome) => (String(nome).split('.').pop() || '').toUpperCase().slice(0, 4);
export const ligacoes = (t) => t.replace(/https?:\/\/[^\s<]+[^\s<.,;:!?)»"']/g, (u) => `<a href="${u}" target="_blank" rel="noopener">${u}</a>`);
// tópicos: um por linha (tira marcas de lista que a pessoa tenha escrito)
export const topicos = (t) => String(t || '').split('\n').map((l) => l.replace(/^\s*[-•*·]\s*/, '').trim()).filter(Boolean);

// ---------------------------------------------------------------- anexos
const tipoDe = (f) => (/^image\//.test(f.type) ? 'imagem' : /^video\//.test(f.type) ? 'video' : /^audio\//.test(f.type) ? 'audio' : 'ficheiro');
// carrega um ficheiro para a pasta (prefixo) e devolve o anexo para guardar na mensagem
export async function carregarAnexo(prefixo, original, extra = {}) {
  const tipo = tipoDe(original);
  if (original.size > MAXIMO) throw new Error(`«${original.name}» tem mais de 50 MB.`);
  let f = original;
  if (tipo === 'imagem') { try { f = await reduzir(original); } catch (_) { /* fica o original */ } }
  const nome = original.name && original.name !== 'image.png' ? original.name : `imagem-${new Date().toISOString().slice(0, 10)}.png`;
  const base = nomeBase(f === original ? nome : f.name || nome);
  const caminho = `${prefixo}/${base}`;
  let mini = null;
  if (tipo === 'imagem' || tipo === 'video') { try { mini = await fazerMiniatura(f); } catch (_) { /* sem miniatura */ } }
  const up = await sb().storage.from(BALDE).upload(caminho, f, { contentType: f.type || 'application/octet-stream', upsert: false });
  if (up.error) throw up.error;
  let miniatura = null;
  if (mini && mini.blob) {
    miniatura = `${prefixo}/mini-${base.replace(/\.[a-z0-9]+$/i, '')}.jpg`;
    const um = await sb().storage.from(BALDE).upload(miniatura, mini.blob, { contentType: 'image/jpeg', upsert: false });
    if (um.error) miniatura = null;
  }
  const anexo = { caminho, nome: f === original ? nome : f.name, mime: f.type || '', tamanho: f.size, tipo, ...extra };
  if (miniatura) anexo.miniatura = miniatura;
  if (mini) { anexo.largura = mini.largura; anexo.altura = mini.altura; }
  return anexo;
}
export const caminhosDe = (anexos) => (anexos || []).flatMap((a) => [a.caminho, a.miniatura]).filter(Boolean);
export const apagarFicheiros = (anexos) => { const c = caminhosDe(anexos); if (c.length) sb().storage.from(BALDE).remove(c).catch(() => {}); };

export function htmlAnexos(anexos, chave) {
  const as = anexos || [];
  if (!as.length) return '';
  const imagens = as.map((a, i) => ({ a, i })).filter((x) => x.a.tipo === 'imagem');
  let h = imagens.length ? `<div class="msg-imagens${imagens.length === 1 ? ' uma' : ''}">${imagens.map(({ a, i }) => `<button type="button" data-acao="conv-imagem" data-chave="${esc(chave)}" data-i="${i}" title="${esc(a.nome)}">${img(BALDE, a.miniatura || a.caminho, a.nome)}</button>`).join('')}</div>` : '';
  for (const a of as) {
    if (a.tipo === 'video') h += `<video class="msg-video" controls playsinline preload="metadata" data-chat-src="${esc(a.caminho)}"${a.miniatura ? ` data-chat-poster="${esc(a.miniatura)}"` : ''} aria-label="Vídeo: ${esc(a.nome)}"></video>`;
    else if (a.tipo === 'audio') h += `<div class="msg-audio">${ic('micro', 'ic-sm')}<audio controls preload="metadata" data-chat-src="${esc(a.caminho)}" aria-label="Áudio${a.duracao ? ' de ' + duracao(a.duracao) : ''}"></audio>${a.duracao ? `<span class="fraco mini num">${duracao(a.duracao)}</span>` : ''}</div>`;
    else if (a.tipo === 'ficheiro') h += `<button type="button" class="msg-ficheiro" data-acao="conv-ficheiro" data-caminho="${esc(a.caminho)}" data-nome="${esc(a.nome)}" data-mime="${esc(a.mime || '')}">
        <span class="doc-tipo" aria-hidden="true">${esc(extensao(a.nome))}</span><span><span class="msg-ficheiro-nome">${esc(a.nome)}</span><span class="fraco mini">${tamanho(a.tamanho || 0)} · abrir</span></span></button>`;
  }
  return h;
}
// imagens (miniaturas), vídeos e áudios com os links assinados do armazenamento privado
export async function prepararMedia(raiz, depois) {
  hidratar(raiz).then(() => depois && depois());
  const els = $$('[data-chat-src], [data-chat-poster]', raiz);
  if (!els.length) return;
  await assinar(BALDE, els.flatMap((el) => [el.dataset.chatSrc, el.dataset.chatPoster]).filter(Boolean));
  els.forEach((el) => {
    if (el.dataset.chatPoster && !el.getAttribute('poster')) el.setAttribute('poster', urlEmCache(BALDE, el.dataset.chatPoster));
    if (el.dataset.chatSrc && !el.getAttribute('src')) el.setAttribute('src', urlEmCache(BALDE, el.dataset.chatSrc));
  });
}
// cliques nas imagens (visor) e nos ficheiros (abrir ou descarregar); anexosPor(chave) devolve os anexos da mensagem
export async function cliqueAnexo(el, anexosPor) {
  if (el.dataset.acao === 'conv-imagem') {
    const as = anexosPor(el.dataset.chave) || [];
    const imagens = as.filter((a) => a.tipo === 'imagem');
    abrirVisor(imagens.map((a) => ({ balde: BALDE, caminho: a.caminho, nome: a.nome })), imagens.indexOf(as[Number(el.dataset.i)]));
    return true;
  }
  if (el.dataset.acao === 'conv-ficheiro') {
    const janela = window.open('about:blank', '_blank');   // já, para o browser não bloquear a janela
    const ver = /^(application\/pdf|text\/|image\/|video\/|audio\/)/.test(el.dataset.mime || '');
    const { data, error } = await sb().storage.from(BALDE).createSignedUrl(el.dataset.caminho, 300, ver ? undefined : { download: el.dataset.nome });
    if (error) { if (janela) janela.close(); throw error; }
    if (janela) janela.location.href = data.signedUrl; else location.href = data.signedUrl;
    return true;
  }
  return false;
}

// ---------------------------------------------------------------- escrever (texto, ficheiros, áudio)
// htmlEscrever(estado): a linha de escrever; estado = { pendentes, gravar, rascunho, placeholder, modo? }
export const htmlPendentes = (pendentes) => pendentes.map((f, i) => `<li>${ic(/^image\//.test(f.type) ? 'imagem' : /^video\//.test(f.type) ? 'video' : 'ficheiro', 'ic-sm')}<span class="chat-pendente-nome">${esc(f.name || 'imagem colada')}</span><span class="fraco">${tamanho(f.size)}</span>
  <button type="button" class="icone-botao" data-acao="conv-tirar" data-i="${i}" aria-label="Tirar ${esc(f.name || 'imagem')}">${ic('fechar', 'ic-sm')}</button></li>`).join('');
export function htmlLinha(st) {
  if (st.gravar) return `<div class="chat-gravacao"><span class="ponto-gravar" aria-hidden="true"></span><span class="num" data-conv-tempo>0:00</span><span class="fraco pequeno">A gravar áudio…</span></div>
    <button class="btn pequeno texto" type="button" data-acao="conv-audio-cancelar">Cancelar</button>
    <button class="icone-botao enviar" type="button" data-acao="conv-audio-enviar" aria-label="Parar e enviar o áudio" title="Parar e enviar">${ic('enviar')}</button>`;
  return `<button class="icone-botao" type="button" data-acao="conv-escolher" data-qual="ficheiros" aria-label="Juntar ficheiros" title="Juntar ficheiros">${ic('clipe')}</button>
    <button class="icone-botao" type="button" data-acao="conv-escolher" data-qual="media" aria-label="Juntar fotos ou vídeos" title="Fotos ou vídeos">${ic('imagem')}</button>
    <input type="file" multiple data-conv-ficheiros="ficheiros" hidden><input type="file" multiple accept="image/*,video/*" data-conv-ficheiros="media" hidden>
    <textarea class="campo" data-conv-texto rows="1" maxlength="4000" placeholder="${esc(st.placeholder || 'Escreve uma mensagem…')}" aria-label="Mensagem">${esc(st.rascunho || '')}</textarea>
    ${'MediaRecorder' in window && navigator.mediaDevices ? `<button class="icone-botao" type="button" data-acao="conv-audio" aria-label="Gravar um áudio" title="Gravar um áudio">${ic('micro')}</button>` : ''}
    <button class="icone-botao enviar" type="submit" aria-label="Enviar" title="Enviar">${ic('enviar')}</button>`;
}
export function ajustarAltura(raiz) {
  const t = $('[data-conv-texto]', raiz);
  if (!t) return;
  t.style.height = 'auto';
  t.style.height = `${Math.min(160, t.scrollHeight + 2)}px`;
}
export function juntar(st, lista, aviso) {
  const fs = [...(lista || [])];
  if (!fs.length) return;
  const grandes = fs.filter((f) => f.size > MAXIMO);
  if (grandes.length) aviso(`Demasiado grande (máximo 50 MB): ${grandes.map((f) => f.name).join(', ')}`);
  st.pendentes.push(...fs.filter((f) => f.size <= MAXIMO));
  if (st.pendentes.length > 10) { st.pendentes = st.pendentes.slice(0, 10); aviso('No máximo 10 ficheiros por mensagem.'); }
}

// áudio (MediaRecorder): mp4/AAC onde houver, para tocar em todos os telemóveis; devolve o ficheiro e a duração
export async function gravar(st, { aoMudar, aoAcabar, aviso }) {
  if (st.gravar) return;
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); } catch (e) {
    aviso(e && e.name === 'NotAllowedError' ? 'O microfone está bloqueado: permite-o nas definições do browser para este site.' : 'Não foi possível usar o microfone: ' + (e.message || e));
    return;
  }
  const tipo = ['audio/mp4;codecs=mp4a.40.2', 'audio/mp4', 'audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus'].find((t) => MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)) || '';
  const rec = new MediaRecorder(stream, tipo ? { mimeType: tipo } : undefined);
  const g = { rec, stream, partes: [], inicio: Date.now(), cancelado: false, relogio: null };
  rec.ondataavailable = (e) => { if (e.data && e.data.size) g.partes.push(e.data); };
  rec.onstop = () => {
    clearInterval(g.relogio);
    stream.getTracks().forEach((t) => t.stop());
    st.gravar = null;
    aoMudar();
    if (g.cancelado || !g.partes.length) return;
    const mime = (rec.mimeType || tipo || 'audio/webm').split(';')[0];
    const ext = mime.includes('mp4') ? 'm4a' : mime.includes('ogg') ? 'ogg' : 'webm';
    const agora = new Date();
    const nome = `audio-${agora.toISOString().slice(0, 10)}-${String(agora.getHours()).padStart(2, '0')}${String(agora.getMinutes()).padStart(2, '0')}.${ext}`;
    aoAcabar(new File(g.partes, nome, { type: mime }), Math.round((Date.now() - g.inicio) / 100) / 10);
  };
  rec.start(250);
  st.gravar = g;
  aoMudar();
  g.relogio = setInterval(() => {
    const s = (Date.now() - g.inicio) / 1000;
    $$('[data-conv-tempo]').forEach((el) => (el.textContent = duracao(Math.floor(s))));
    if (s >= AUDIO_MAXIMO) pararGravacao(st, false);
  }, 250);
}
export function pararGravacao(st, cancelar) {
  const g = st.gravar;
  if (!g) return;
  g.cancelado = cancelar;
  if (g.rec.state !== 'inactive') g.rec.stop();
}
// quem é: o nome de uma pessoa do hub
export const nomePessoa = (id) => (E.perfis.find((p) => p.id === id) || {}).nome || 'Alguém';
