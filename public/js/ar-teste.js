// AR test page for Android (/ar-teste.html), outside the hub on purpose (team note 10 on task 84, 2026-11-10: «anima a
// transição durante uma fração de segundo mas depois volta à página do Hub»; the server logs showed the Google app never
// asked for the model). One tap per test, no forms; the page works out what happened by itself:
//   - the page went hidden after the tap  -> another app opened (and how long it stayed)
//   - it came back through ?volta=<test>  -> Scene Viewer did not open and Chrome followed the fallback link; if the page
//     went hidden well before it unloaded, an app opened first and sent it back; if not, Chrome never opened an app
//   - nothing within 4 s                   -> no app opened and no fallback
//   - the page lost the focus without going hidden -> a window opened on top (a side or floating window, a sheet)
// Google's own sample tells the phone apart from our model; Scene Viewer opening in 3D vs in AR, Chrome's own AR through
// the viewer and directly (with the exact error), and the camera, tell which part of the phone fails. Round 1 (2026-11-10,
// a Xiaomi with Android 15 and WebXR) failed everything, Google's sample too: the Google app links «did nothing» while
// «a side window starts to open and closes», the ARCore links fell back at once, Chrome's AR failed. Results stay in this phone's localStorage until sent to the test task (Supabase, the person's
// own session) or copied. Our model's signed link comes from the hub in the hash, so it never reaches a server log.
import { EXEMPLO_GOOGLE, intentSceneViewer } from './ar-intent.js';

const CHAVE = 'design-ar-teste';
const MODEL_VIEWER = 'https://cdn.jsdelivr.net/npm/@google/model-viewer@4.0.0/dist/model-viewer.min.js';
const LINK_VALIDO_MS = 55 * 60 * 1000;   // the hub signs the link for an hour
const $ = (s, r = document) => r.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const seg = (ms) => (ms / 1000).toFixed(1).replace('.', ',') + ' s';

function ler() { try { return JSON.parse(localStorage.getItem(CHAVE)) || {}; } catch (_) { return {}; } }
function guardar() { try { localStorage.setItem(CHAVE, JSON.stringify(E)); } catch (_) {} }
const VERSAO = 2;   // round 2 (2026-11-10): other tests under the same ids — old results must not show under new names
const E = Object.assign({ res: {}, toque: null, info: null, modelo: null, notas: '' }, ler());
if (E.versao !== VERSAO) Object.assign(E, { versao: VERSAO, res: {}, toque: null, ultimo: null });
const recarregar = () => Object.assign(E, { res: {}, toque: null }, ler());   // another tab may have written

// our model, from the hub (#u=&t=&doc=&real=): a new model starts a new round of tests
const h = new URLSearchParams(location.hash.slice(1));
if (h.get('u')) {
  Object.assign(E, { modelo: { u: h.get('u'), t: h.get('t') || 'o nosso modelo', doc: Number(h.get('doc')) || null, real: h.get('real') === '1', em: Date.now() }, res: {}, toque: null, info: null });
  guardar();
  history.replaceState(null, '', location.pathname + location.search);
}
const modeloValido = () => E.modelo && Date.now() - E.modelo.em < LINK_VALIDO_MS;

const TESTES = [
  { id: 'T1', nome: 'A câmara do telemóvel, neste site', acao: 'camara' },
  { id: 'T2', nome: 'O AR do próprio Chrome, direto (diz o erro exato)', acao: 'sessao' },
  { id: 'G1', nome: 'Exemplo da Google · Scene Viewer a abrir em 3D', link: (u, v) => intentSceneViewer(u, { titulo: 'Exemplo da Google', volta: v, modo: '3d_preferred' }) },
  { id: 'G2', nome: 'Exemplo da Google · Scene Viewer a abrir em AR', link: (u, v) => intentSceneViewer(u, { titulo: 'Exemplo da Google', volta: v }) },
  { id: 'G3', nome: 'Exemplo da Google · AR do Chrome pelo visualizador', webxr: true },
  { id: 'N1', nosso: true, nome: 'O nosso modelo · Scene Viewer a abrir em 3D', link: (u, v, m) => intentSceneViewer(u, { titulo: m.t, real: m.real, volta: v, modo: '3d_preferred' }) },
  { id: 'N2', nosso: true, nome: 'O nosso modelo · Scene Viewer a abrir em AR (o do botão do hub)', link: (u, v, m) => intentSceneViewer(u, { titulo: m.t, real: m.real, volta: v }) },
  { id: 'N3', nosso: true, nome: 'O nosso modelo · AR do Chrome pelo visualizador', webxr: true },
];
const urlDe = (t) => (t.nosso ? E.modelo.u : EXEMPLO_GOOGLE);
const voltaDe = (id) => location.origin + location.pathname + '?volta=' + id;   // /ar-teste on the site (no redirect)

// ---------------------------------------------------------------- what happened (automatic)
const novaAba = !sessionStorage.getItem('ar-teste-aba');
try { sessionStorage.setItem('ar-teste-aba', '1'); } catch (_) {}
const volta = new URLSearchParams(location.search).get('volta');
if (volta && TESTES.some((t) => t.id === volta)) {
  // the tap still open, or the one just closed by the page becoming visible again (Chrome may show the tab for a moment
  // before it follows the fallback link)
  const k = E.toque && E.toque.id === volta ? E.toque
    : E.ultimo && E.ultimo.id === volta && Date.now() - E.ultimo.t < 120000 ? E.ultimo : null;
  let texto = 'voltou pelo link de recurso: o Scene Viewer não abriu';
  if (!k) texto += ' (sem registo do toque)';
  else if (k.escondida != null && (k.saiu == null || k.saiu - k.escondida > 400)) {
    texto += `. Outra app abriu ${seg(k.escondida)} depois do toque e mandou o Chrome de volta`
      + (k.saiu != null ? ` ${seg(k.saiu - k.escondida)} depois` : '');
  } else texto += '. Nenhuma app chegou a abrir: o Chrome foi logo para o link de recurso';
  texto += novaAba ? ' (a página voltou num separador novo).' : ' (no mesmo separador).';
  E.res[volta] = { estado: 'mau', texto, recurso: true, ms: k && { escondida: k.escondida, saiu: k.saiu, total: Date.now() - k.t } };
  E.toque = null;
  E.ultimo = null;
  guardar();
  history.replaceState(null, '', location.pathname);
}
document.addEventListener('visibilitychange', () => {
  recarregar();
  const k = E.toque;
  if (!k || Date.now() - k.t > 120000) return;
  if (document.visibilityState === 'hidden') {
    if (k.escondida == null) { k.escondida = Date.now() - k.t; guardar(); }
  } else if (k.escondida != null && k.visivel == null) {
    k.visivel = Date.now() - k.t;
    const fora = k.visivel - k.escondida;
    E.res[k.id] = fora < 2500
      ? { estado: 'mau', texto: `abriu outra app e voltou sozinho ao fim de ${seg(fora)}, sem passar pelo link de recurso.`, ms: { escondida: k.escondida, fora } }
      : { estado: 'confirmar', texto: `abriu outra app durante ${seg(fora)}. Viste o modelo?`, ms: { escondida: k.escondida, fora } };
    E.ultimo = { ...k };
    E.toque = null;
    guardar();
    atualizar();
  }
});
window.addEventListener('pagehide', () => { recarregar(); const k = E.toque; if (k && k.saiu == null) { k.saiu = Date.now() - k.t; guardar(); } });
// a window on top (side/floating window, a system sheet) takes the focus but does not hide the page
window.addEventListener('blur', () => { recarregar(); const k = E.toque; if (k && k.desfocada == null && Date.now() - k.t < 15000) { k.desfocada = Date.now() - k.t; guardar(); } });
window.addEventListener('focus', () => { recarregar(); const k = E.toque; if (k && k.desfocada != null && k.focada == null) { k.focada = Date.now() - k.t; guardar(); } });

function tocou(id) {
  E.toque = { id, t: Date.now(), escondida: null, visivel: null, saiu: null, desfocada: null, focada: null };
  E.res[id] = { estado: 'a-testar', texto: 'a testar…' };
  guardar();
  atualizar();
  setTimeout(() => {
    recarregar();
    if (E.toque && E.toque.id === id && E.toque.escondida == null && document.visibilityState === 'visible') {
      const k = E.toque;
      E.res[id] = k.desfocada != null
        ? { estado: 'mau', texto: `abriu uma janela por cima (sem esconder esta página) ${seg(k.desfocada)} depois do toque`
            + (k.focada != null ? `, que fechou ao fim de ${seg(k.focada - k.desfocada)}` : ', que ainda não fechou') + '; o Scene Viewer não apareceu.' }
        : { estado: 'mau', texto: 'nada aconteceu em 4 s: nenhuma app nem janela abriu e o Chrome não foi para o link de recurso.' };
      E.toque = null;
      guardar();
      atualizar();
    }
  }, 4000);
}

// ---------------------------------------------------------------- Chrome's own AR (WebXR, through <model-viewer>)
let mvPronto = null;
function carregarModelViewer() {
  if (customElements.get('model-viewer')) return Promise.resolve();
  mvPronto = mvPronto || new Promise((ok, falha) => {
    const s = document.createElement('script');
    s.type = 'module'; s.src = MODEL_VIEWER;
    s.onload = () => customElements.whenDefined('model-viewer').then(ok);
    s.onerror = () => falha(new Error('não consegui carregar o visualizador'));
    document.head.appendChild(s);
  });
  return mvPronto;
}
async function prepararWebXR(t, caixa) {
  caixa.innerHTML = '<p class="fraco mini">A carregar o modelo…</p>';
  try { await carregarModelViewer(); } catch (e) { return marcar(t.id, 'mau', e.message); }
  const real = t.nosso && E.modelo.real;
  caixa.innerHTML = `<model-viewer src="${esc(urlDe(t))}" alt="${esc(t.nome)}" camera-controls ar ar-modes="webxr" ar-placement="floor"${real ? ' ar-scale="fixed"' : ''}>
    <button slot="ar-button" class="btn primario pequeno" type="button" style="position:absolute;bottom:8px;right:8px">Ver no teu espaço</button></model-viewer>`;
  const mv = $('model-viewer', caixa);
  mv.addEventListener('load', () => setTimeout(() => {
    if (!mv.canActivateAR) marcar(t.id, 'mau', 'o modelo abriu em 3D, mas este Chrome não tem AR (WebXR): falta o ARCore ou o telemóvel não o suporta.');
    else if (!E.res[t.id] || E.res[t.id].estado === 'a-testar') marcar(t.id, 'a-testar', 'pronto: toca em «Ver no teu espaço».');
  }, 600));
  mv.addEventListener('error', () => marcar(t.id, 'mau', 'o modelo não carregou no Chrome.'));
  mv.addEventListener('ar-status', (e) => {
    if (e.detail.status === 'session-started') marcar(t.id, 'bom', 'o AR do Chrome abriu.');
    else if (e.detail.status === 'failed') marcar(t.id, 'mau', 'o AR do Chrome falhou ao abrir.' + ultimosAvisos());
  });
}
function marcar(id, estado, texto) { recarregar(); E.res[id] = { estado, texto }; guardar(); atualizar(); }

// what the viewer and the browser say when AR fails (model-viewer only reports «failed»)
const avisosConsola = [];
for (const nivel of ['error', 'warn']) {
  const original = console[nivel].bind(console);
  console[nivel] = (...a) => { avisosConsola.push(a.map((x) => (x && x.message) || String(x)).join(' ').slice(0, 200)); if (avisosConsola.length > 6) avisosConsola.shift(); original(...a); };
}
window.addEventListener('error', (e) => { avisosConsola.push(String(e.message).slice(0, 200)); });
window.addEventListener('unhandledrejection', (e) => { avisosConsola.push(String((e.reason && (e.reason.name + ': ' + e.reason.message)) || e.reason).slice(0, 200)); });
const ultimosAvisos = () => (avisosConsola.length ? ' Mensagens: ' + avisosConsola.slice(-3).join(' | ') : '');

// T1: can this site open the camera at all (Chrome's AR needs it)
async function testarCamara() {
  marcar('T1', 'a-testar', 'a pedir a câmara…');
  try {
    const st = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    st.getTracks().forEach((x) => x.stop());
    marcar('T1', 'bom', 'a câmara abriu neste site.');
  } catch (e) { marcar('T1', 'mau', `a câmara não abriu: ${e.name}: ${e.message}`); }
}
// T2: Chrome's own AR session, without any viewer, so the exact error shows (called straight from the tap)
function testarSessao() {
  if (!navigator.xr) { marcar('T2', 'mau', 'este Chrome não tem WebXR.'); return; }
  marcar('T2', 'a-testar', 'a abrir a sessão de AR…');
  navigator.xr.requestSession('immersive-ar', { optionalFeatures: ['local-floor', 'hit-test', 'dom-overlay'], domOverlay: { root: document.body } })
    .then((s) => { marcar('T2', 'bom', 'a sessão de AR do Chrome abriu (a câmara do AR funcionou); fecha sozinha.'); setTimeout(() => s.end().catch(() => {}), 1500); })
    .catch((e) => marcar('T2', 'mau', `a sessão de AR não abriu: ${e.name}: ${e.message}`));
}

// ---------------------------------------------------------------- the page
function montar() {
  $('#testes').innerHTML = TESTES.map((t) => {
    const falta = t.nosso && !E.modelo ? 'Abre esta página a partir do hub (Step Inside › Teste do AR) para testar o nosso modelo.'
      : t.nosso && !modeloValido() ? 'O link do nosso modelo expirou (dura uma hora): abre outra vez a partir do hub.' : '';
    const acao = falta ? `<span class="fraco mini">${esc(falta)}</span>`
      : t.webxr ? `<button class="btn pequeno" type="button" data-webxr="${t.id}">Preparar</button>`
      : t.acao ? `<button class="btn primario pequeno" type="button" data-acao-teste="${t.acao}">Testar</button>`
      : `<a class="btn primario pequeno" href="${esc(t.link(urlDe(t), voltaDe(t.id), E.modelo))}" data-teste="${t.id}">Testar</a>`;
    return `<li><div class="linha"><span class="nome"><span class="id">${t.id}</span>${esc(t.nome)}</span>${acao}</div>
      ${t.webxr ? `<div data-caixa="${t.id}"></div>` : ''}<div class="teste-res" data-res="${t.id}"></div><div class="teste-conf" data-conf-caixa="${t.id}"></div></li>`;
  }).join('');
  $('#notas').value = E.notas || '';
}
function atualizar() {
  for (const t of TESTES) {
    const r = E.res[t.id], el = $(`[data-res="${t.id}"]`), conf = $(`[data-conf-caixa="${t.id}"]`);
    if (!el) continue;
    el.textContent = r ? r.texto : '';
    el.className = 'teste-res' + (r && r.estado === 'mau' ? ' mau' : r && r.estado === 'bom' ? ' bom' : '');
    conf.innerHTML = r && r.estado === 'confirmar'
      ? `<button class="btn pequeno" type="button" data-conf="${t.id}" data-v="sim">Sim, vi o modelo</button><button class="btn pequeno" type="button" data-conf="${t.id}" data-v="nao">Não</button>` : '';
  }
}
function desenharInfo() {
  const i = E.info || {};
  const linhas = [
    ['Telemóvel', [i.modelo, i.android && 'Android ' + i.android].filter(Boolean).join(' · ') || (i.android_ua ? 'Android (modelo escondido pelo Chrome)' : 'não é um Android')],
    ['Chrome', i.chrome || '?'],
    ['Aberto como', i.modo || '?'],
    ['AR do Chrome (WebXR)', i.webxr === true ? 'sim' : i.webxr === false ? 'não' : (i.webxr || '?')],
    ['Câmara para este site', { granted: 'permitida', denied: 'bloqueada', prompt: 'ainda não pedida' }[i.camara] || i.camara || '?'],
    ['Janela', i.janela || '?'],
    ['Nosso modelo', E.modelo ? `${E.modelo.t}${modeloValido() ? '' : ' (link expirado)'}` : '— (abre a partir do hub)'],
  ];
  if (E.modelo) linhas.push(['Ficheiro', i.ficheiro || 'a verificar…']);
  $('#info').innerHTML = linhas.map(([a, b]) => `<dt>${esc(a)}</dt><dd>${esc(b)}</dd>`).join('');
}
async function verificarTelemovel() {
  const i = { ua: navigator.userAgent, android_ua: /Android/.test(navigator.userAgent) };
  try {
    if (navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {
      const v = await navigator.userAgentData.getHighEntropyValues(['model', 'platformVersion', 'fullVersionList']);
      i.modelo = v.model || null;
      i.android = v.platform === 'Android' || i.android_ua ? v.platformVersion : null;
      const c = (v.fullVersionList || []).find((b) => /Google Chrome|Chromium/.test(b.brand));
      i.chrome = c ? c.version : null;
    }
  } catch (_) {}
  if (!i.chrome) { const m = navigator.userAgent.match(/Chrome\/([\d.]+)/); i.chrome = m ? m[1] : null; }
  i.modo = matchMedia('(display-mode: standalone)').matches ? 'app instalada no ecrã inicial' : 'separador do Chrome';
  try { i.webxr = !!(navigator.xr && await navigator.xr.isSessionSupported('immersive-ar')); } catch (e) { i.webxr = 'erro: ' + e.message; }
  try { i.camara = (await navigator.permissions.query({ name: 'camera' })).state; } catch (_) { i.camara = '?'; }
  i.janela = `${innerWidth}×${innerHeight} de ${screen.width}×${screen.height}`;
  if (modeloValido()) {
    try {
      const r = await fetch(E.modelo.u, { headers: { Range: 'bytes=0-11' }, cache: 'no-store' });
      const b = new Uint8Array(await r.arrayBuffer());
      i.ficheiro = `responde ${r.status} (${r.headers.get('content-type') || '?'}), ${String.fromCharCode(...b.slice(0, 4)) === 'glTF' ? 'é um GLB válido' : 'cabeçalho estranho'}`;
    } catch (e) { i.ficheiro = 'não descarrega: ' + e.message; }
  }
  recarregar();
  E.info = i;
  guardar();
  desenharInfo();
}

export function textoResultado() {
  const i = E.info || {};
  return ['Teste do AR no Android (página de teste, fora do hub, ronda 2)',
    `Telemóvel: ${i.modelo || '?'} · Android ${i.android || '?'} · Chrome ${i.chrome || '?'} · ${i.modo || '?'} · AR do Chrome (WebXR): ${i.webxr === true ? 'sim' : i.webxr === false ? 'não' : i.webxr} · câmara: ${i.camara || '?'} · janela ${i.janela || '?'}`,
    E.modelo ? `Nosso modelo: ${E.modelo.t} (documento ${E.modelo.doc}) · ficheiro: ${i.ficheiro || '?'}` : 'Nosso modelo: não testado (página aberta sem o hub)',
    ...TESTES.map((t) => `${t.id}. ${t.nome}: ${(E.res[t.id] && E.res[t.id].texto) || '(não testado)'}`),
    `Notas: ${E.notas || '—'}`,
    `UA: ${i.ua || navigator.userAgent}`].join('\n');
}

async function enviar() {
  const estado = $('#estado-envio');
  if (!Object.values(E.res).some((r) => r && r.estado !== 'a-testar')) { estado.textContent = 'Faz primeiro pelo menos um teste.'; return; }
  const sb = window.Design && window.Design.sb;
  try {
    const { data: { session } } = await sb.auth.getSession();
    if (!session) { estado.textContent = 'Este telemóvel não tem sessão no Design: entra no hub e volta, ou usa «Copiar o resultado» e cola numa nota da tarefa.'; return; }
    const { data: tarefas, error: e1 } = await sb.from('tarefas').select('id, titulo').ilike('titulo', '%iPhone e um Android%').limit(1);
    if (e1 || !tarefas || !tarefas.length) throw e1 || new Error('não encontrei a tarefa do teste do AR');
    const { data: perfil } = await sb.from('perfis').select('nome').eq('id', session.user.id).maybeSingle();
    const { error } = await sb.from('tarefas_notas').insert({ tarefa_id: tarefas[0].id, tipo: 'nota', texto: textoResultado(), autor_nome: (perfil && perfil.nome) || 'Teste do AR' });
    if (error) throw error;
    estado.textContent = 'Enviado para a tarefa do teste. Obrigado!';
  } catch (e) { estado.textContent = 'Não consegui enviar (' + (e.message || e) + '). Usa «Copiar o resultado».'; }
}

// ---------------------------------------------------------------- events
document.addEventListener('click', (e) => {
  const a = e.target.closest('[data-teste]');
  if (a) return tocou(a.dataset.teste);   // no preventDefault: the tap itself opens the app
  const w = e.target.closest('[data-webxr]');
  if (w) { const t = TESTES.find((x) => x.id === w.dataset.webxr); E.res[t.id] = { estado: 'a-testar', texto: 'a preparar…' }; guardar(); atualizar(); return prepararWebXR(t, $(`[data-caixa="${t.id}"]`)); }
  const x = e.target.closest('[data-acao-teste]');
  if (x) return x.dataset.acaoTeste === 'camara' ? testarCamara() : testarSessao();
  const c = e.target.closest('[data-conf]');
  if (c) {
    const r = E.res[c.dataset.conf] || {};
    return marcar(c.dataset.conf, c.dataset.v === 'sim' ? 'bom' : 'mau',
      (c.dataset.v === 'sim' ? 'abriu e mostrou o modelo' : 'abriu outra app, mas não mostrou o modelo') + (r.ms ? ` (fora ${seg(r.ms.fora)})` : '') + '.');
  }
});
$('#notas').addEventListener('input', (e) => { E.notas = e.target.value; guardar(); });
$('#enviar').addEventListener('click', enviar);
$('#copiar').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(textoResultado()); $('#estado-envio').textContent = 'Copiado.'; }
  catch (_) { $('#notas').value = textoResultado(); $('#estado-envio').textContent = 'Não consegui copiar: o resultado ficou nas notas, copia-o daí.'; }
});
$('#limpar').addEventListener('click', () => { Object.assign(E, { res: {}, toque: null, notas: '' }); guardar(); montar(); atualizar(); });

montar();
atualizar();
desenharInfo();
verificarTelemovel();
