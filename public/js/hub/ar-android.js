// Step Inside › Teste do AR, Android: the Scene Viewer link and the in-phone diagnosis.
// Team notes on hub task 84 (2026-11-10): «O AR no android não abriu, nem sequer apareceu que foi descarregado» and
// «anima a transição durante uma fração de segundo mas depois volta à página do Hub». Nobody at the PC has an Android,
// so the diagnosis runs on the tester's phone and sends what it finds to the task as a note (human-in-the-loop):
//   A/B  Google's own sample, link as 1.0 (ours until now) and as 1.2 (Google's <model-viewer> 4.0.0)
//   C/D  our model, the same two links;   E  our model in Chrome's own AR (WebXR, «Ver em 3D» › «Ver no teu espaço»)
//   plus what the phone supports and whether our signed file downloads (status, type, glTF header).
import { E } from './dados.js';
import { esc } from './util.js';

export const EXEMPLO_GOOGLE = 'https://modelviewer.dev/shared-assets/models/Astronaut.glb';

/** The intent that opens Scene Viewer (the Google app). versao '1.2' is built exactly as Google's <model-viewer> 4.0.0
 *  builds it (the model URL's own query, mode, disable_occlusion, resizable, then file); '1.0' is the form used here
 *  until 2026-11-10 (Google's documentation example). */
export function intentSceneViewer(url, { versao = '1.2', titulo = '', real = false, volta = location.href } = {}) {
  let q;
  if (versao === '1.0') {
    q = 'file=' + encodeURIComponent(url) + '&mode=ar_preferred' + (titulo ? '&title=' + encodeURIComponent(titulo) : '') + (real ? '&resizable=false' : '');
  } else {
    const p = new URLSearchParams(new URL(url).search);
    p.set('mode', 'ar_preferred');
    if (!p.has('disable_occlusion')) p.set('disable_occlusion', 'true');
    if (real) p.set('resizable', 'false');
    if (titulo) p.set('title', titulo);
    q = p.toString() + '&file=' + encodeURIComponent(url);
  }
  return `intent://arvr.google.com/scene-viewer/${versao}?${q}#Intent;scheme=https;package=com.google.android.googlequicksearchbox;action=android.intent.action.VIEW;S.browser_fallback_url=${encodeURIComponent(volta)};end;`;
}
export const voltaPara = (id, slug) => location.href.split('#')[0].split('?')[0] + `?ar-android=${id}#/projeto/${slug}`;

// ---------------------------------------------------------------- diagnosis
const TESTES = [
  ['A', 'Exemplo da Google · link 1.0'], ['B', 'Exemplo da Google · link 1.2'],
  ['C', 'O nosso modelo · link 1.0 (o de antes)'], ['D', 'O nosso modelo · link 1.2 (o do botão agora)'],
  ['E', 'O nosso modelo · AR no Chrome («Ver em 3D» › «Ver no teu espaço»)'],
];
const RESPOSTAS = ['abriu e mostrou o modelo', 'abriu e fechou logo', 'não fez nada', 'deu erro (escreve qual em notas)'];
export const diag = { res: {}, info: null, notas: '', aberto: false };
// the panel stays open across redraws (the phone check finishes after the first draw and redraws the page)
document.addEventListener('toggle', (e) => { if (e.target.id === 'diag-ar') diag.aberto = e.target.open; }, true);

/** The panel (inside the AR test section). `glb` = the first GLB model document; its id gets the C/D links. */
export function htmlDiagnostico(glb, slug) {
  if (!glb) return '';
  const linha = ([k, rotulo]) => {
    const alvo = k === 'A' || k === 'B'
      ? `<a href="${esc(intentSceneViewer(EXEMPLO_GOOGLE, { versao: k === 'A' ? '1.0' : '1.2', titulo: 'Exemplo da Google', volta: voltaPara(0, slug) }))}" data-ar-exemplo="${k}">${esc(rotulo)}</a>`
      : k === 'E' ? `<button class="btn pequeno" type="button" data-acao="ver-3d" data-id="${glb.id}">${esc(rotulo)}</button>`
      : `<a href="#" data-ar="${glb.id}" data-ar-tipo="android-${k === 'C' ? '1.0' : '1.2'}" aria-disabled="true">${esc(rotulo)}</a>`;
    return `<li><span class="diag-teste"><b>${k}</b> ${alvo}</span>
      <select class="seletor" data-diag-res="${k}" aria-label="Resultado do teste ${k}"><option value="">o que aconteceu?</option>${RESPOSTAS.map((r) => `<option${diag.res[k] === r ? ' selected' : ''}>${r}</option>`).join('')}</select></li>`;
  };
  return `<details class="diag-ar" id="diag-ar"${diag.aberto ? ' open' : ''}><summary>Diagnóstico do AR no Android</summary>
    <p class="fraco mini">Num Android, no Chrome: toca em cada teste, volta a esta página e escolhe o que aconteceu. No fim, «Enviar resultado»: vai para a tarefa do teste e o Claude descobre onde está o problema.</p>
    <div class="fraco mini" id="diag-info">${diag.info ? esc(resumoInfo()) : 'A verificar este telemóvel…'}</div>
    <ol class="diag-lista">${TESTES.map(linha).join('')}</ol>
    <textarea class="campo" data-diag-notas rows="2" placeholder="Notas (modelo do telemóvel, mensagens que apareceram…)">${esc(diag.notas)}</textarea>
    <div class="botoes" style="margin-top:8px"><button class="btn primario pequeno" type="button" data-acao="diag-enviar">Enviar resultado</button></div>
  </details>`;
}

/** What the phone supports and whether our signed file downloads — run once per page. */
export async function verificar(urlGlb) {
  const i = { ua: navigator.userAgent, ecra: `${screen.width}x${screen.height}@${devicePixelRatio}` };
  try { i.webxr_ar = !!(navigator.xr && await navigator.xr.isSessionSupported('immersive-ar')); } catch (e) { i.webxr_ar = 'erro: ' + e.message; }
  if (urlGlb) {
    try {
      const r = await fetch(urlGlb, { headers: { Range: 'bytes=0-11' }, cache: 'no-store' });
      const b = new Uint8Array(await r.arrayBuffer());
      i.ficheiro = { estado: r.status, tipo: r.headers.get('content-type'), tamanho: r.headers.get('content-range') || r.headers.get('content-length'),
        gltf: String.fromCharCode(...b.slice(0, 4)) === 'glTF' };
    } catch (e) { i.ficheiro = { erro: e.message }; }
    try { const h = await fetch(urlGlb, { method: 'HEAD', cache: 'no-store' }); i.ficheiro_head = h.status; } catch (e) { i.ficheiro_head = 'erro: ' + e.message; }
  }
  diag.info = i;
  return i;
}
function resumoInfo() {
  const i = diag.info, f = i.ficheiro || {};
  return `Este telemóvel: AR no Chrome (WebXR) ${i.webxr_ar === true ? 'sim' : i.webxr_ar === false ? 'não' : i.webxr_ar}; o nosso ficheiro: `
    + (f.erro ? `não descarrega (${f.erro})` : `${f.estado} ${f.tipo || ''}, ${f.gltf ? 'glTF válido' : 'cabeçalho estranho'}; HEAD ${i.ficheiro_head}`);
}
export function textoResultado() {
  const i = diag.info || {};
  return ['Diagnóstico do AR no Android (enviado pelo hub)',
    ...TESTES.map(([k, r]) => `${k}. ${r}: ${diag.res[k] || '(não testado)'}`),
    `Notas: ${diag.notas || '—'}`,
    `Telemóvel: ${i.ua || '?'} · ecrã ${i.ecra || '?'} · WebXR AR: ${i.webxr_ar}`,
    `Ficheiro (link assinado): ${JSON.stringify(i.ficheiro || {})} · HEAD ${i.ficheiro_head}`].join('\n');
}
export const tarefaTeste = (projetoId) => E.tarefas.find((t) => t.projeto === projetoId && /iPhone e um Android/.test(t.titulo));
