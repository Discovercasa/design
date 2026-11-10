// Step Inside › Teste do AR, Android: the Scene Viewer link and the way into the AR test page.
// Team notes on hub task 84 (2026-11-10): «O AR no android não abriu, nem sequer apareceu que foi descarregado» and
// «anima a transição durante uma fração de segundo mas depois volta à página do Hub». The server logs showed that the
// Google app never asked for the model (only Chrome did), so the failure is before the download. The test page
// (/ar-teste.html, outside the hub) tells the causes apart on the phone itself, with no forms: Google's own sample vs our
// model, Google app vs ARCore vs Chrome's own AR (WebXR), and it detects by itself whether an app opened and how it came
// back. Nobody at Claude's side has an Android, so the page sends what it finds to the task (human in the loop).
export { intentSceneViewer, EXEMPLO_GOOGLE } from '../ar-intent.js';

export const voltaPara = (id, slug) => location.href.split('#')[0].split('?')[0] + `?ar-android=${id}#/projeto/${slug}`;

/** The test page with our model: the signed link goes in the hash (never sent to the server, kept on the phone). */
export const paginaTeste = (url, d) => '/ar-teste.html#' + new URLSearchParams({ u: url, t: d.titulo.replace(/\s+/g, ' '), doc: d.id,
  real: /1:1/.test(d.titulo) ? '1' : '0' }).toString();

/** The panel (inside the AR test section). `glb` = the first GLB model document; prepararAR fills the link. */
export function htmlDiagnostico(glb) {
  if (!glb) return '';
  return `<div class="diag-ar" id="diag-ar">
    <p class="pequeno"><b>O AR não abre num Android?</b> Abre a página de teste nesse telemóvel, no Chrome: tem 8 testes de um toque
      (o exemplo da Google e o nosso modelo, pela app Google, pelo ARCore e pelo AR do Chrome). Vê sozinha o que aconteceu em
      cada um e envia o resultado para a tarefa do teste.</p>
    <div class="botoes" style="margin-top:8px"><a class="btn pequeno" href="#" data-ar="${glb.id}" data-ar-tipo="teste" aria-disabled="true">Abrir a página de teste do AR</a></div>
  </div>`;
}
