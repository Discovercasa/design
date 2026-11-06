// Imagens do hub: reduzir fotos grandes, fazer miniaturas, URLs assinados (os armazenamentos são privados) e o visor
// que mostra uma imagem em grande dentro do hub. Usado pelas Redes sociais e pelas imagens de tarefas, checkpoints e notas.
import { esc, ic, mov } from './util.js';

const sb = () => window.Design.sb;

export const chaveFicheiro = (nome) => nome.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9._-]+/g, '-').replace(/-{2,}/g, '-').replace(/^[-.]+|[-.]+$/g, '') || 'ficheiro';
export const nomeBase = (nome) => `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}__${chaveFicheiro(nome)}`;

// miniatura (até 640 px, JPEG) feita no browser: as grelhas carregam depressa sem pedir os ficheiros originais
export async function fazerMiniatura(ficheiro) {
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

// fotos grandes reduzidas a 2048 px no lado maior (JPEG 90): chega para ver e publicar e poupa o armazenamento gratuito
export const LADO_MAXIMO = 2048;
export async function reduzir(ficheiro) {
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
// só imagens (as capturas de ecrã coladas chegam como image/png sem nome útil)
export const saoImagens = (lista) => [...(lista || [])].filter((f) => /^image\//.test(f.type) || /\.(jpe?g|png|webp|gif|heic)$/i.test(f.name));

// ---------------------------------------------------------------- URLs assinados, por armazenamento, guardados 50 min
const urls = new Map();
const k = (balde, c) => `${balde}:${c}`;
export const urlEmCache = (balde, c) => { const u = urls.get(k(balde, c)); return u && u.ate > Date.now() ? u.url : ''; };
export async function assinar(balde, caminhos) {
  const falta = [...new Set(caminhos.filter((c) => c && !urlEmCache(balde, c)))];
  if (!falta.length) return;
  const { data, error } = await sb().storage.from(balde).createSignedUrls(falta, 3600);
  if (error) return;
  const ate = Date.now() + 50 * 60 * 1000;
  (data || []).forEach((d) => { if (d.signedUrl) urls.set(k(balde, d.path), { url: d.signedUrl, ate }); });
}
// <img data-balde="anexos" data-cam="…"> desenhada sem src: põe o URL assinado
export async function hidratar(raiz) {
  const imgs = [...raiz.querySelectorAll('img[data-balde][data-cam]')].filter((i) => !i.getAttribute('src'));
  if (!imgs.length) return;
  const porBalde = new Map();
  imgs.forEach((i) => { if (!porBalde.has(i.dataset.balde)) porBalde.set(i.dataset.balde, []); porBalde.get(i.dataset.balde).push(i.dataset.cam); });
  await Promise.all([...porBalde].map(([b, cs]) => assinar(b, cs)));
  imgs.forEach((i) => { const u = urlEmCache(i.dataset.balde, i.dataset.cam); if (u) i.setAttribute('src', u); });
}
export const img = (balde, caminho, alt = '') => `<img alt="${esc(alt)}" loading="lazy" decoding="async" data-balde="${balde}" data-cam="${esc(caminho)}"${urlEmCache(balde, caminho) ? ` src="${esc(urlEmCache(balde, caminho))}"` : ''}>`;

// ---------------------------------------------------------------- visor: a imagem em grande, com setas, dentro do hub
let visor = null, lista = [], atual = 0;
function mostrar() {
  const a = lista[atual];
  visor.querySelector('.visor-img').innerHTML = `<img alt="${esc(a.nome)}" src="">`;
  visor.querySelector('.visor-legenda').textContent = `${a.nome}${lista.length > 1 ? ` · ${atual + 1} de ${lista.length}` : ''}`;
  visor.querySelectorAll('.visor-seta').forEach((b) => (b.hidden = lista.length < 2));
  assinar(a.balde, [a.caminho]).then(() => {
    const el = visor.querySelector('.visor-img img');
    if (el && lista[atual] === a) el.src = urlEmCache(a.balde, a.caminho);
  });
}
export function abrirVisor(itens, i = 0) {
  if (!itens.length) return;
  if (!visor) {
    visor = document.createElement('dialog');
    visor.className = 'visor';
    visor.setAttribute('aria-label', 'Imagem');
    visor.innerHTML = `<button class="icone-botao visor-fechar" type="button" aria-label="Fechar">${ic('fechar')}</button>
      <button class="icone-botao visor-seta" data-dir="-1" type="button" aria-label="Anterior">${ic('esquerda')}</button>
      <figure><div class="visor-img"></div><figcaption class="visor-legenda"></figcaption></figure>
      <button class="icone-botao visor-seta" data-dir="1" type="button" aria-label="Seguinte">${ic('direita')}</button>`;
    document.body.append(visor);
    visor.addEventListener('click', (e) => {
      const s = e.target.closest('.visor-seta');
      if (s) { atual = (atual + Number(s.dataset.dir) + lista.length) % lista.length; return mostrar(); }
      if (e.target.closest('.visor-fechar') || e.target === visor || e.target.classList.contains('visor-img')) visor.close();
    });
    visor.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { atual = (atual + (e.key === 'ArrowRight' ? 1 : -1) + lista.length) % lista.length; mostrar(); }
    });
  }
  lista = itens; atual = i;
  mostrar();
  if (!visor.open) visor.showModal();
  if (mov()) gsap.fromTo(visor, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, ease: 'power1.out' });
}
