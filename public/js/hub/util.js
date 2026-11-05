// Utilitários do hub: ícones (um só conjunto SVG, traço 1,75 — desenhos ao estilo Lucide, licença ISC), texto,
// datas, movimento (GSAP quando existe e o movimento não está reduzido), avisos e diálogos.

const P = {
  sugestao: '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
  sino: '<path d="M10.268 21a2 2 0 0 0 3.464 0"/><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/>',
  pessoa: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  definicoes: '<path d="M20 7h-9"/><path d="M14 17H5"/><circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/>',
  novidades: '<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
  sair: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>',
  seta: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  baixo: '<path d="m6 9 6 6 6-6"/>',
  mais: '<path d="M5 12h14"/><path d="M12 5v14"/>',
  fechar: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  certo: '<path d="M20 6 9 17l-5-5"/>',
  menos: '<path d="M5 12h14"/>',
  abrir: '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
  ramo: '<path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>',
  decisao: '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
  ligacao: '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
  novo: '<path d="M12 3l1.9 5.8L20 10l-6.1 1.2L12 17l-1.9-5.8L4 10l6.1-1.2z"/><path d="M19 17v4"/><path d="M17 19h4"/>',
  alvo: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
  editar: '<path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/>',
  apagar: '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>',
  custo: '<circle cx="8" cy="8" r="6"/><path d="M18.09 10.37A6 6 0 1 1 10.34 18"/><path d="M7 6h1v4"/>',
  instalar: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
  app: '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
  atencao: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
  pasta: '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
};
export const ic = (nome, cls = '') => `<svg class="ic ${cls}" viewBox="0 0 24 24" aria-hidden="true">${P[nome] || ''}</svg>`;

export const $ = (s, r = document) => r.querySelector(s);
export const $$ = (s, r = document) => [...r.querySelectorAll(s)];
export const esc = (t) => String(t ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export const iniciais = (nome) => (String(nome || '?').trim().split(/\s+/).filter(Boolean).map((p) => p[0]).slice(0, 2).join('') || '?').toUpperCase();

// datas: só o dia (pt-PT), e "há x" para as notificações
const paraData = (d) => (typeof d === 'string' && d.length === 10 ? new Date(d + 'T12:00:00') : new Date(d));
export const dia = (d) => (d ? paraData(d).toLocaleDateString('pt-PT', { day: 'numeric', month: 'short', year: 'numeric' }) : '');
export const diaCurto = (d) => (d ? paraData(d).toLocaleDateString('pt-PT', { day: 'numeric', month: 'short' }) : '');
export function ha(d) {
  const s = (Date.now() - new Date(d).getTime()) / 1000;
  if (s < 60) return 'agora';
  if (s < 3600) return `há ${Math.floor(s / 60)} min`;
  if (s < 86400) return `há ${Math.floor(s / 3600)} h`;
  if (s < 7 * 86400) return `há ${Math.floor(s / 86400)} d`;
  return dia(d);
}
export const euros = (v, casas = 2) => v.toLocaleString('pt-PT', { style: 'currency', currency: 'EUR', minimumFractionDigits: casas, maximumFractionDigits: casas });

// movimento: GSAP só quando carregou e a pessoa não pediu menos movimento (sistema ou Definições)
export const mov = () => !!window.gsap && !matchMedia('(prefers-reduced-motion: reduce)').matches && document.documentElement.dataset.movimento !== 'reduzido';

export function entrar(alvos, opcoes = {}) {
  const els = typeof alvos === 'string' ? $$(alvos) : alvos;
  if (!mov() || !els || !els.length) return;
  gsap.from(els, { autoAlpha: 0, y: 10, duration: 0.35, ease: 'expo.out', stagger: { amount: Math.min(0.25, els.length * 0.04) }, clearProps: 'opacity,visibility,transform', ...opcoes });
}
export function encherBarras(raiz = document) {
  const barras = $$('.barra > i', raiz);
  barras.forEach((b) => (b.style.transform = `scaleX(${b.dataset.p || 0})`));
  if (mov() && barras.length) gsap.from(barras, { scaleX: 0, duration: 0.6, ease: 'expo.out', stagger: 0.04 });
}
export function contar(el, ate) {
  el.textContent = ate;
  if (!mov() || !ate) return;
  const o = { v: 0 };
  gsap.to(o, { v: ate, duration: 0.8, ease: 'expo.out', snap: { v: 1 }, onUpdate: () => (el.textContent = o.v) });
}
// luz que segue o cursor nas linhas de projeto (SpotlightCard do react-bits, refeito com variáveis CSS)
export function luz(raiz) {
  raiz.addEventListener('pointermove', (e) => {
    const l = e.target.closest('.projeto-linha');
    if (!l) return;
    const r = l.getBoundingClientRect();
    l.style.setProperty('--x', `${e.clientX - r.left}px`);
    l.style.setProperty('--y', `${e.clientY - r.top}px`);
  });
}

// avisos (toasts): ficam 5 s, param com o rato por cima
export function aviso(html, { icone = 'info', acoes = [], duracao = 5 } = {}) {
  const el = document.createElement('div');
  el.className = 'aviso';
  el.setAttribute('role', 'status');
  el.innerHTML = `${ic(icone)}<div>${html}${acoes.length ? `<div class="acoes">${acoes.map((a, i) => `<button type="button" class="btn pequeno${i === 0 ? ' primario' : ''}" data-i="${i}">${esc(a.rotulo)}</button>`).join('')}</div>` : ''}</div>
    <button type="button" class="icone-botao fechar" aria-label="Fechar">${ic('fechar', 'ic-sm')}</button>`;
  $('#avisos').append(el);
  let tl = null;
  const tirar = () => {
    if (tl) tl.kill();
    if (!mov()) return el.remove();
    gsap.to(el, { autoAlpha: 0, x: 16, duration: 0.15, ease: 'power1.in', onComplete: () => el.remove() });
  };
  el.querySelector('.fechar').onclick = tirar;
  el.querySelectorAll('[data-i]').forEach((b) => (b.onclick = () => { acoes[+b.dataset.i].fazer(); tirar(); }));
  if (mov()) {
    tl = gsap.timeline().from(el, { autoAlpha: 0, y: 12, duration: 0.25, ease: 'expo.out' });
    if (duracao) tl.to(el, { autoAlpha: 0, duration: 0.15, ease: 'power1.in', onComplete: () => el.remove() }, `+=${duracao}`);
    el.onpointerenter = () => tl && tl.pause();
    el.onpointerleave = () => tl && tl.play();
  } else if (duracao) setTimeout(() => el.isConnected && el.remove(), duracao * 1000);
  return el;
}

// diálogos (<dialog>): abrir e fechar com movimento curto
export function abrirDialogo(d, html, { estreito = false } = {}) {
  if (html != null) d.innerHTML = html;
  d.classList.toggle('estreito', estreito);
  if (!d.open) d.showModal();
  if (mov()) gsap.fromTo(d, { autoAlpha: 0, y: d.classList.contains('gaveta') ? 0 : 8, x: d.classList.contains('gaveta') ? 24 : 0 },
    { autoAlpha: 1, y: 0, x: 0, duration: 0.25, ease: 'expo.out', overwrite: 'auto', clearProps: 'transform' });
  return d;
}
export function fecharDialogo(d) {
  if (!d.open) return;
  if (!mov()) return d.close();
  gsap.to(d, { autoAlpha: 0, y: d.classList.contains('gaveta') ? 0 : 4, x: d.classList.contains('gaveta') ? 24 : 0, duration: 0.15, ease: 'power2.in', overwrite: 'auto',
    onComplete: () => { d.close(); gsap.set(d, { clearProps: 'all' }); } });
}
