// Redes sociais — dados: obras e as suas fases, posts (um por semana), fotos/vídeos e comentários de aprovação
// (Supabase, migração 0009; ficheiros no armazenamento privado "social"). O estado fica em E (dados.js).
import { E } from './dados.js';

const sb = () => window.Design.sb;
const BALDE = 'social';

export const ESTADOS_POST = { ideia: 'Ideia', rascunho: 'Rascunho', por_aprovar: 'Por aprovar', aprovado: 'Aprovado', publicado: 'Publicado', nao_feito: 'Não feito' };
// ordem no calendário (mês + semana) e os posts que se podem adiantar para uma semana: os seguintes ainda por publicar
export const posicao = (mes, semana) => `${mes}#${semana}`;
export const candidatosAdiantar = (mes, semana) => E.posts.filter((p) => posicao(p.mes, p.semana) > posicao(mes, semana) && !['publicado', 'nao_feito'].includes(p.estado))
  .sort((a, b) => (posicao(a.mes, a.semana) < posicao(b.mes, b.semana) ? -1 : 1) || a.id - b.id);
export const TIPOS_POST = { carrossel: 'Carrossel', foto: 'Foto', video: 'Vídeo', reel: 'Reel', story: 'Story' };
export const REDES = { instagram: 'Instagram', facebook: 'Facebook', linkedin: 'LinkedIn' };
export const ESTADOS_FASE = { prevista: 'Prevista', em_curso: 'Em curso', concluida: 'Concluída' };
export const FOTOS_FASE = { por_tirar: 'Fotos por tirar', visita_marcada: 'Visita marcada', tiradas: 'Fotos tiradas' };
// fases de uma obra nova (como no Excel: Mov, BF, Estrutura, Acabamentos); desmarca-se o que não se aplica
export const FASES_MODELO = ['Projetos', 'Movimento de terras', 'Base de fundação', 'Estrutura', 'Acabamentos', 'Entrega'];

// ---------------------------------------------------------------- leitura
export async function carregarSocial() {
  const r = await Promise.all([
    sb().from('obras').select('*').order('ordem'),
    sb().from('obras_fases').select('*').order('ordem'),
    sb().from('posts').select('*').order('mes'),
    sb().from('posts_media').select('*').order('ordem'),
    sb().from('posts_comentarios').select('*').order('criado_em'),
  ]);
  const falha = r.find((x) => x.error);
  if (falha) { E.socialErro = falha.error.message; return; }   // sem a migração 0009: o resto do hub continua
  [E.obras, E.fases, E.posts, E.media, E.comentarios] = r.map((x) => x.data);
  E.socialErro = null;
}

export const obra = (id) => E.obras.find((o) => o.id === id);
export const fase = (id) => E.fases.find((f) => f.id === id);
export const post = (id) => E.posts.find((p) => p.id === id);
export const obrasAtivas = () => E.obras.filter((o) => o.ativa).sort((a, b) => a.ordem - b.ordem || a.nome.localeCompare(b.nome, 'pt'));
export const fasesDe = (obraId) => E.fases.filter((f) => f.obra_id === obraId).sort((a, b) => a.ordem - b.ordem || a.id - b.id);
export const mediaDe = (postId) => E.media.filter((m) => m.post_id === postId).sort((a, b) => a.ordem - b.ordem || a.id - b.id);
export const comentariosDe = (postId) => E.comentarios.filter((c) => c.post_id === postId);
export const postsDe = (mes, semana) => E.posts.filter((p) => p.mes === mes && (!semana || p.semana === semana)).sort((a, b) => a.semana - b.semana || a.id - b.id);
export const postsDaObra = (obraId) => E.posts.filter((p) => p.obra_id === obraId).sort((a, b) => (a.mes < b.mes ? -1 : a.mes > b.mes ? 1 : a.semana - b.semana));
// a fase em que a obra está: a primeira em curso; senão a última concluída
export function faseAtual(obraId) {
  const fs = fasesDe(obraId);
  return fs.find((f) => f.estado === 'em_curso') || [...fs].reverse().find((f) => f.estado === 'concluida') || null;
}
// onde ir tirar fotos: visitas marcadas (pelo dia) e fases em curso com fotos por tirar
export function visitasParaFotos() {
  const ativas = new Set(obrasAtivas().map((o) => o.id));
  const marcadas = E.fases.filter((f) => ativas.has(f.obra_id) && f.fotos === 'visita_marcada').sort((a, b) => String(a.visita_em || '9').localeCompare(String(b.visita_em || '9')));
  const porTirar = E.fases.filter((f) => ativas.has(f.obra_id) && f.estado === 'em_curso' && f.fotos === 'por_tirar');
  return [...marcadas, ...porTirar];
}

// meses: o dia 1 de cada mês em texto (AAAA-MM-01)
export const mesDe = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`;
export const somarMeses = (mes, n) => { const d = new Date(mes + 'T12:00:00'); d.setDate(1); d.setMonth(d.getMonth() + n); return mesDe(d); };
export const nomeMes = (mes, ano = true) => new Date(mes + 'T12:00:00').toLocaleDateString('pt-PT', ano ? { month: 'long', year: 'numeric' } : { month: 'long' });
// a semana do mês de hoje (1–5; como no Excel, cada mês tem as suas semanas)
export const semanaDeHoje = () => Math.min(5, Math.ceil(new Date().getDate() / 7));
// do primeiro mês com posts até dois meses depois do atual (ou do último post)
export function mesesVisiveis() {
  const atual = mesDe(new Date());
  const meses = E.posts.map((p) => p.mes);
  let ini = meses.length ? meses.reduce((a, b) => (a < b ? a : b)) : atual;
  let fim = [somarMeses(atual, 2), ...meses].reduce((a, b) => (a > b ? a : b));
  if (ini > atual) ini = atual;
  const lista = [];
  for (let m = ini; m <= fim; m = somarMeses(m, 1)) lista.push(m);
  return lista;
}

// verificações da legenda antes de publicar (o Instagram não formata nada: o que se escreve é o que aparece)
export function verificarLegenda(t) {
  const hashtags = (t.match(/(^|\s)#[\p{L}\p{N}_]+/gu) || []).length;
  const avisos = [];
  if (t.length > 2200) avisos.push(`Tem ${t.length} caracteres: o Instagram aceita até 2200.`);
  if (hashtags > 30) avisos.push(`Tem ${hashtags} hashtags: o Instagram aceita até 30.`);
  if (/\*\*[^*]+\*\*/.test(t) || /\[[^\]]+\]\(https?:[^)]+\)/.test(t)) avisos.push('Tem formatação (**negrito** ou [ligação](…)) que o Instagram mostra tal e qual, com os asteriscos e os parênteses.');
  if (/\bconosco\b/i.test(t)) avisos.push('«conosco» é a forma do Brasil; em Portugal escreve-se «connosco».');
  if (/\bnoosas\b/i.test(t)) avisos.push('«noosas» parece uma gralha de «nossas».');
  return { caracteres: [...t].length, hashtags, avisos };
}

// ---------------------------------------------------------------- escrita
async function feito(p) { const r = await p; if (r.error) throw r.error; await carregarSocial(); return r.data; }
export const criarPost = (campos) => feito(sb().from('posts').insert(campos).select().single());
export const mudarPost = (id, campos) => feito(sb().from('posts').update(campos).eq('id', id));
export async function apagarPost(p) {
  const caminhos = mediaDe(p.id).flatMap((m) => [m.caminho, m.miniatura].filter(Boolean));
  await feito(sb().from('posts').delete().eq('id', p.id));
  if (caminhos.length) await sb().storage.from(BALDE).remove(caminhos);
}
const nomeRepetido = (e) => { throw (/obras_nome_idx|duplicate key/.test(e.message || '') ? new Error('Já existe uma obra com esse nome.') : e); };
export const criarObra = async (campos, fases) => {
  const nova = await feito(sb().from('obras').insert({ ...campos, ordem: E.obras.length + 1 }).select().single()).catch(nomeRepetido);
  if (fases.length) await feito(sb().from('obras_fases').insert(fases.map((nome, i) => ({ obra_id: nova.id, nome, ordem: i + 1 }))));
  return nova;
};
export const mudarObra = (id, campos) => feito(sb().from('obras').update(campos).eq('id', id)).catch(nomeRepetido);
export const mudarFase = (id, campos) => feito(sb().from('obras_fases').update(campos).eq('id', id));
// fase nova na posição escolhida (1 = primeira): as seguintes descem uma posição
export async function criarFase(obraId, campos, posicao) {
  const fs = fasesDe(obraId);
  const pos = Math.max(1, Math.min(posicao || fs.length + 1, fs.length + 1));
  for (const [i, f] of fs.entries()) {
    const ordem = i + 1 >= pos ? i + 2 : i + 1;
    if (f.ordem !== ordem) { const r = await sb().from('obras_fases').update({ ordem }).eq('id', f.id); if (r.error) throw r.error; }
  }
  return feito(sb().from('obras_fases').insert({ ...campos, obra_id: obraId, ordem: pos }));
}
export async function moverFase(f, posicao) {
  const fs = fasesDe(f.obra_id).filter((x) => x.id !== f.id);
  fs.splice(posicao - 1, 0, f);
  for (const [i, x] of fs.entries()) if (x.ordem !== i + 1) { const r = await sb().from('obras_fases').update({ ordem: i + 1 }).eq('id', x.id); if (r.error) throw r.error; }
  await carregarSocial();
}
export const comentar = (postId, texto, mediaId) => feito(sb().from('posts_comentarios').insert({ post_id: postId, texto, media_id: mediaId || null, autor_nome: E.eu.nome }));
export const mudarComentario = (id, campos) => feito(sb().from('posts_comentarios').update(campos).eq('id', id));
export const apagarComentario = (id) => feito(sb().from('posts_comentarios').delete().eq('id', id));

// ---------------------------------------------------------------- fotos e vídeos
const chaveFicheiro = (nome) => nome.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9._-]+/g, '-').replace(/-{2,}/g, '-').replace(/^[-.]+|[-.]+$/g, '') || 'ficheiro';
const MIMES = { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', webp: 'image/webp', gif: 'image/gif', heic: 'image/heic', mp4: 'video/mp4', mov: 'video/quicktime', webm: 'video/webm' };
export const ehVideo = (m) => /^video\//.test(m.mime || '');
export const MAXIMO = 50 * 1024 * 1024;

// miniatura (até 640 px, JPEG) feita no browser: as grelhas carregam depressa sem pedir as fotos originais
async function fazerMiniatura(ficheiro) {
  let fonte, largura, altura, limpar = () => {};
  if (ficheiro.type.startsWith('image/')) {
    fonte = await createImageBitmap(ficheiro);
    largura = fonte.width; altura = fonte.height; limpar = () => fonte.close && fonte.close();
  } else if (ficheiro.type.startsWith('video/')) {
    const url = URL.createObjectURL(ficheiro);
    const v = document.createElement('video');
    v.muted = true; v.playsInline = true; v.preload = 'auto'; v.src = url;
    await new Promise((ok, falha) => { v.onloadeddata = ok; v.onerror = falha; setTimeout(falha, 8000); });
    v.currentTime = Math.min(0.5, (v.duration || 1) / 2);
    await new Promise((ok) => { v.onseeked = ok; setTimeout(ok, 3000); });
    fonte = v; largura = v.videoWidth; altura = v.videoHeight; limpar = () => URL.revokeObjectURL(url);
  } else return null;
  try {
    const s = Math.min(1, 640 / Math.max(largura, altura));
    const c = document.createElement('canvas');
    c.width = Math.max(1, Math.round(largura * s)); c.height = Math.max(1, Math.round(altura * s));
    c.getContext('2d').drawImage(fonte, 0, 0, c.width, c.height);
    const blob = await new Promise((ok) => c.toBlob(ok, 'image/jpeg', 0.82));
    return { blob, largura, altura };
  } finally { limpar(); }
}

// fotos grandes reduzidas a 2048 px no lado maior (JPEG 90): o Instagram mostra até 1080 px e o armazenamento gratuito
// do Supabase tem 1 GB; quem precisar do ficheiro original marca "Manter os originais"
export const LADO_MAXIMO = 2048;
async function reduzir(ficheiro) {
  if (!/^image\/(jpeg|png|webp)$/.test(ficheiro.type)) return ficheiro;
  const bmp = await createImageBitmap(ficheiro);
  try {
    const s = Math.min(1, LADO_MAXIMO / Math.max(bmp.width, bmp.height));
    if (s === 1 && ficheiro.size < 1.5e6) return ficheiro;
    const c = document.createElement('canvas');
    c.width = Math.round(bmp.width * s); c.height = Math.round(bmp.height * s);
    c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
    const blob = await new Promise((ok) => c.toBlob(ok, 'image/jpeg', 0.9));
    if (!blob || blob.size >= ficheiro.size) return ficheiro;
    return new File([blob], ficheiro.name.replace(/\.[a-z0-9]+$/i, '') + '.jpg', { type: 'image/jpeg' });
  } finally { bmp.close && bmp.close(); }
}

export async function carregarMedia(postId, ficheiro, ordem, original = false) {
  if (!original) { try { ficheiro = await reduzir(ficheiro); } catch (_) { /* fica o original */ } }
  const ext = (ficheiro.name.split('.').pop() || '').toLowerCase();
  const mime = ficheiro.type || MIMES[ext] || 'application/octet-stream';
  const base = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}__${chaveFicheiro(ficheiro.name)}`;
  const caminho = `posts/${base}`;
  let mini = null;
  try { mini = await fazerMiniatura(ficheiro); } catch (_) { /* HEIC e afins: fica sem miniatura */ }
  const up = await sb().storage.from(BALDE).upload(caminho, ficheiro, { contentType: mime, upsert: false });
  if (up.error) throw up.error;
  let miniatura = null;
  if (mini && mini.blob) {
    miniatura = `miniaturas/${base.replace(/\.[a-z0-9]+$/, '')}.jpg`;
    const um = await sb().storage.from(BALDE).upload(miniatura, mini.blob, { contentType: 'image/jpeg', upsert: false });
    if (um.error) miniatura = null;
  }
  const { error } = await sb().from('posts_media').insert({ post_id: postId, caminho, miniatura, nome_ficheiro: ficheiro.name, mime, tamanho: ficheiro.size,
    largura: mini ? mini.largura : null, altura: mini ? mini.altura : null, ordem });
  if (error) { await sb().storage.from(BALDE).remove([caminho, miniatura].filter(Boolean)); throw error; }
}
export async function apagarMedia(m) {
  const { error } = await sb().from('posts_media').delete().eq('id', m.id);
  if (error) throw error;
  await sb().storage.from(BALDE).remove([m.caminho, m.miniatura].filter(Boolean));
  await carregarSocial();
}
// nova ordem das fotos de um post (lista de ids)
export async function ordenarMedia(ids) {
  for (const [i, id] of ids.entries()) {
    const m = E.media.find((x) => x.id === id);
    if (m && m.ordem !== i + 1) { const r = await sb().from('posts_media').update({ ordem: i + 1 }).eq('id', id); if (r.error) throw r.error; }
  }
  await carregarSocial();
}

// URLs assinados (o armazenamento é privado): pedidos aos molhos e guardados 50 min
const urls = new Map();
export const urlEmCache = (caminho) => { const u = urls.get(caminho); return u && u.ate > Date.now() ? u.url : ''; };
export async function assinar(caminhos) {
  const falta = [...new Set(caminhos.filter((c) => c && !urlEmCache(c)))];
  if (!falta.length) return;
  const { data, error } = await sb().storage.from(BALDE).createSignedUrls(falta, 3600);
  if (error) return;
  const ate = Date.now() + 50 * 60 * 1000;
  (data || []).forEach((d) => { if (d.signedUrl) urls.set(d.path, { url: d.signedUrl, ate }); });
}
// põe o src nas imagens desenhadas sem URL (data-cam = caminho no armazenamento)
export async function hidratar(raiz) {
  const imgs = [...raiz.querySelectorAll('[data-cam]')].filter((i) => !i.getAttribute('src'));
  if (!imgs.length) return;
  await assinar(imgs.map((i) => i.dataset.cam));
  imgs.forEach((i) => { const u = urlEmCache(i.dataset.cam); if (u) i.setAttribute('src', u); });
}
export async function urlDescarregar(m) {
  const { data, error } = await sb().storage.from(BALDE).createSignedUrl(m.caminho, 300, { download: m.nome_ficheiro });
  if (error) throw error;
  return data.signedUrl;
}
