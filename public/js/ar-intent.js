// The Android links that open a 3D model in AR (Google Scene Viewer), shared by the hub and the AR test page
// (/ar-teste.html). Pure functions: no hub state, no Supabase.
//   Google app  intent://arvr.google.com/scene-viewer/<versao>?…#Intent;package=com.google.android.googlequicksearchbox
//               '1.2' exactly as Google's <model-viewer> 4.0.0 builds it; '1.0' the documentation example
//   ARCore      the documentation's AR-only form, through «Serviços Google Play para RA» (com.google.ar.core), without
//               the Google app (https://developers.google.com/ar/develop/scene-viewer)
export const EXEMPLO_GOOGLE = 'https://modelviewer.dev/shared-assets/models/Astronaut.glb';

const fim = (pacote, volta) => `#Intent;scheme=https;package=${pacote};action=android.intent.action.VIEW;`
  + `S.browser_fallback_url=${encodeURIComponent(volta)};end;`;

/** Scene Viewer through the Google app. `real`: 1:1 model, no pinch-to-scale. `volta`: where Chrome goes if it fails. */
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
  return `intent://arvr.google.com/scene-viewer/${versao}?${q}` + fim('com.google.android.googlequicksearchbox', volta);
}

/** Scene Viewer in AR only, through ARCore (Google Play Services for AR) instead of the Google app. */
export function intentArcore(url, { titulo = '', real = false, volta = location.href } = {}) {
  const q = 'file=' + encodeURIComponent(url) + '&mode=ar_only' + (titulo ? '&title=' + encodeURIComponent(titulo) : '') + (real ? '&resizable=false' : '');
  return `intent://arvr.google.com/scene-viewer/1.0?${q}` + fim('com.google.ar.core', volta);
}
