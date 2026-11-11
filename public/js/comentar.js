// «Comentar» dentro das aplicações do Design (2026-11-11). O utilizador: «alguém testou o gerador de documentos ou o build
// your house … e não gostou de alguma coisa ou quer fazer uma sugestão ou algo correu mal … o utilizador deve conseguir
// fazer uma critica ou um comentário», e depois: «sim põe em todas as abas».
// Um botão fixo abre um formulário curto (o que é, o que aconteceu, onde, imagens ou ficheiros) que grava na tabela
// criticas do Design (migração 0022): a equipa vê-a no hub e quem edita é avisado. Os anexos vão para o armazenamento
// privado "chat" (critica/…). Carregado pela porta (porta.js) nas páginas internas, depois de confirmar a sessão.
(function () {
  if (window.__comentar || !window.Design) return;
  window.__comentar = true;
  // página → projeto do hub (id, nome, slug) e quanto subir o botão (barras em baixo da própria app)
  const APPS = [
    [/^\/build-your-house\//, 'build_your_house', 'Build Your House', 'build-your-house', 64],
    [/^\/gerador\//, 'gerador', 'Gerador de documentos', 'gerador', 0],
    [/^\/orcamentacao\//, 'orcamentacao', 'Orçamentação', 'orcamentacao', 0],
    [/^\/ar-teste\.html/, 'plataforma_cliente', 'Step Inside', 'step-inside', 0],
  ];
  const app = APPS.find((a) => a[0].test(location.pathname));
  if (!app) return;
  const [, PROJETO, NOME, SLUG, ACIMA] = app;
  const sb = window.Design.sb;
  const TIPOS = [['erro', 'Algo correu mal'], ['nao_gostei', 'Não gostei'], ['sugestao', 'Sugestão'], ['comentario', 'Comentário']];
  const MAXIMO = 50 * 1024 * 1024;
  const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const IC = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>';
  let pendentes = [], utilizador = null;

  const CSS = `
  .dc-com-botao { position: fixed; right: 16px; bottom: calc(16px + ${ACIMA}px); z-index: 2147483000; display: inline-flex; align-items: center; gap: 8px;
    height: 44px; padding: 0 16px 0 14px; border-radius: 22px; border: 1px solid rgba(255,255,255,.14); background: #22262b; color: #fff; cursor: pointer;
    font: 600 14px/1 system-ui, -apple-system, "Segoe UI", sans-serif; box-shadow: 0 6px 20px rgba(0,0,0,.2); }
  .dc-com-botao:hover { background: #31363d; }
  .dc-com-botao:focus-visible { outline: 2px solid #5b8fd6; outline-offset: 2px; }
  @media (max-width: 640px) { .dc-com-botao { width: 44px; padding: 0; justify-content: center; } .dc-com-botao span { display: none; } }
  .dc-com-dlg { width: min(480px, calc(100vw - 32px)); max-height: calc(100dvh - 32px); padding: 0; border: 0; border-radius: 16px; overflow: auto;
    background: #fff; color: #1d2024; font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; box-shadow: 0 16px 48px rgba(0,0,0,.25); }
  .dc-com-dlg::backdrop { background: rgba(20,22,24,.38); }
  .dc-com-dlg * { box-sizing: border-box; }
  .dc-com-dlg form, .dc-com-ok { display: grid; gap: 14px; padding: 20px; }
  .dc-com-cab { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
  .dc-com-cab h2 { margin: 0; font-size: 18px; line-height: 1.3; }
  .dc-com-cab p, .dc-com-fraco { margin: 4px 0 0; font-size: 13px; color: #676d75; }
  .dc-com-x { border: 0; background: none; font-size: 22px; line-height: 1; cursor: pointer; color: #676d75; padding: 4px 8px; border-radius: 8px; }
  .dc-com-x:hover { background: rgba(0,0,0,.06); }
  .dc-com-tipos { display: flex; flex-wrap: wrap; gap: 6px; }
  .dc-com-tipos button { border: 1px solid rgba(0,0,0,.16); background: #fff; color: inherit; border-radius: 99px; padding: 6px 12px; font: inherit; font-size: 13px; cursor: pointer; }
  .dc-com-tipos button[aria-pressed="true"] { background: #22262b; color: #fff; border-color: #22262b; }
  .dc-com-dlg label { display: grid; gap: 6px; font-size: 14px; font-weight: 500; }
  .dc-com-dlg label small { font-weight: 400; color: #676d75; }
  .dc-com-dlg textarea, .dc-com-dlg input[type=text] { width: 100%; font: inherit; font-size: 14px; font-weight: 400; color: inherit; background: #fff;
    border: 1px solid rgba(0,0,0,.2); border-radius: 8px; padding: 8px 10px; }
  .dc-com-dlg textarea { min-height: 96px; resize: vertical; }
  .dc-com-anexos { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .dc-com-anexos label { display: inline-flex; font-weight: 500; font-size: 13px; cursor: pointer; color: #2a5a9a; }
  .dc-com-anexos input { position: absolute; width: 1px; height: 1px; opacity: 0; }
  .dc-com-anexos li { list-style: none; display: inline-flex; gap: 6px; align-items: center; font-size: 12px; padding: 2px 4px 2px 10px; border: 1px solid rgba(0,0,0,.16); border-radius: 99px; }
  .dc-com-anexos ul { display: contents; margin: 0; padding: 0; }
  .dc-com-anexos li button { border: 0; background: none; cursor: pointer; font-size: 15px; color: #676d75; }
  .dc-com-rodape { display: flex; justify-content: flex-end; gap: 8px; }
  .dc-com-rodape button { border-radius: 10px; padding: 9px 16px; font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; border: 1px solid rgba(0,0,0,.16); background: #fff; color: inherit; }
  .dc-com-rodape .dc-com-enviar { background: #22262b; color: #fff; border-color: #22262b; }
  .dc-com-rodape button:disabled { opacity: .55; cursor: progress; }
  .dc-com-erro { color: #b3261e; font-size: 13px; margin: 0; }
  .dc-com-erro:empty { display: none; }
  .dc-com-ok a { color: #2a5a9a; }
  @media (prefers-color-scheme: dark) {
    .dc-com-dlg { background: #23262a; color: #eceef0; }
    .dc-com-cab p, .dc-com-fraco, .dc-com-dlg label small, .dc-com-x, .dc-com-anexos li button { color: #a6acb3; }
    .dc-com-tipos button, .dc-com-dlg textarea, .dc-com-dlg input[type=text], .dc-com-rodape button { background: #2c3035; border-color: rgba(255,255,255,.18); }
    .dc-com-tipos button[aria-pressed="true"], .dc-com-rodape .dc-com-enviar { background: #eceef0; color: #1d2024; border-color: #eceef0; }
    .dc-com-anexos label, .dc-com-ok a { color: #8fb6ea; }
    .dc-com-anexos li { border-color: rgba(255,255,255,.2); }
  }`;

  // onde está a pessoa: o passo da app (quando o diz), a página e o aparelho — para quem for ver o que correu mal
  function onde() {
    const texto = (document.body && document.body.innerText) || '';
    const passo = (texto.match(/Passo \d+ de \d+[^\n]{0,40}/) || [])[0];
    const chrome = (navigator.userAgent.match(/(Chrome|Firefox|Version)\/(\d+)/) || [])[0] || '';
    const naveg = chrome.replace('Version', 'Safari');
    return [NOME, passo, location.hash && location.hash.length > 1 ? location.hash : '', `${naveg} ${window.innerWidth}×${window.innerHeight}`.trim()]
      .filter(Boolean).join(' · ').slice(0, 300);
  }
  const chaveFicheiro = (n) => String(n).normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9._-]+/g, '-').replace(/-{2,}/g, '-').replace(/^[-.]+|[-.]+$/g, '') || 'ficheiro';
  const tipoDe = (f) => (/^image\//.test(f.type) ? 'imagem' : /^video\//.test(f.type) ? 'video' : /^audio\//.test(f.type) ? 'audio' : 'ficheiro');

  function formulario() {
    return `<form novalidate>
      <div class="dc-com-cab"><div><h2>Crítica ou comentário</h2><p>Sobre o ${esc(NOME)}. A equipa vê no hub e quem edita é avisado.</p></div>
        <button type="button" class="dc-com-x" data-com="fechar" aria-label="Fechar">×</button></div>
      <div class="dc-com-tipos" role="group" aria-label="O que é">${TIPOS.map(([k, v], i) => `<button type="button" data-tipo="${k}" aria-pressed="${i === 0}">${v}</button>`).join('')}</div>
      <label>O que aconteceu?<textarea name="texto" maxlength="4000" required placeholder="O que fizeste, o que esperavas e o que aconteceu. Podes colar capturas de ecrã (Ctrl+V)."></textarea></label>
      <label>Onde? <small>(já preenchido com o passo, a página e o aparelho; podes mudar)</small><input type="text" name="onde" maxlength="300" value="${esc(onde())}"></label>
      <div class="dc-com-anexos"><label>+ Imagens ou ficheiros<input type="file" name="ficheiros" multiple></label><ul data-com-lista></ul></div>
      <p class="dc-com-erro" role="alert"></p>
      <div class="dc-com-rodape"><button type="button" data-com="fechar">Cancelar</button><button type="submit" class="dc-com-enviar">Enviar</button></div>
    </form>`;
  }
  function desenharAnexos(dlg) {
    const ul = dlg.querySelector('[data-com-lista]');
    if (ul) ul.innerHTML = pendentes.map((f, i) => `<li>${esc(f.name || 'imagem colada')}<button type="button" data-com-tirar="${i}" aria-label="Tirar ${esc(f.name || 'imagem')}">×</button></li>`).join('');
  }
  function juntar(dlg, lista) {
    const fs = [...(lista || [])];
    const grandes = fs.filter((f) => f.size > MAXIMO);
    dlg.querySelector('.dc-com-erro').textContent = grandes.length ? `Demasiado grande (máximo 50 MB): ${grandes.map((f) => f.name).join(', ')}` : '';
    pendentes.push(...fs.filter((f) => f.size <= MAXIMO));
    pendentes = pendentes.slice(0, 10);
    desenharAnexos(dlg);
  }
  async function enviar(dlg, form) {
    const texto = form.elements.texto.value.trim();
    const erro = dlg.querySelector('.dc-com-erro');
    if (texto.length < 2) { erro.textContent = 'Escreve o que aconteceu.'; form.elements.texto.focus(); return; }
    const tipo = (dlg.querySelector('[data-tipo][aria-pressed="true"]') || {}).dataset.tipo || 'comentario';
    const botao = form.querySelector('[type=submit]');
    botao.disabled = true; botao.textContent = 'A enviar…'; erro.textContent = '';
    const feitos = [];
    try {
      for (const f of pendentes) {
        const nome = f.name && f.name !== 'image.png' ? f.name : `captura-${new Date().toISOString().slice(0, 10)}.png`;
        const caminho = `critica/${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}__${chaveFicheiro(nome)}`;
        const up = await sb.storage.from('chat').upload(caminho, f, { contentType: f.type || 'application/octet-stream', upsert: false });
        if (up.error) throw up.error;
        feitos.push({ caminho, nome, mime: f.type || '', tamanho: f.size, tipo: tipoDe(f) });
      }
      const { error } = await sb.from('criticas').insert({ projeto: PROJETO, tipo, texto, onde: form.elements.onde.value.trim(), anexos: feitos, autor_id: utilizador });
      if (error) throw error;
    } catch (e) {
      if (feitos.length) sb.storage.from('chat').remove(feitos.map((a) => a.caminho)).catch(() => {});
      erro.textContent = 'Não foi enviada: ' + (e.message || e);
      botao.disabled = false; botao.textContent = 'Enviar';
      return;
    }
    pendentes = [];
    dlg.innerHTML = `<div class="dc-com-ok" role="status"><div class="dc-com-cab"><div><h2>Obrigado!</h2><p>A crítica ficou no hub, no ${esc(NOME)}; quem edita foi avisado.</p></div>
      <button type="button" class="dc-com-x" data-com="fechar" aria-label="Fechar">×</button></div>
      <p class="dc-com-fraco"><a href="/#/projeto/${SLUG}" target="_blank" rel="noopener">Ver as críticas no hub</a></p>
      <div class="dc-com-rodape"><button type="button" class="dc-com-enviar" data-com="fechar">Fechar</button></div></div>`;
  }
  function abrir(dlg) {
    pendentes = [];
    dlg.innerHTML = formulario();
    if (!dlg.open) dlg.showModal();
    setTimeout(() => { const t = dlg.querySelector('textarea'); if (t) t.focus(); }, 30);
  }

  async function montar() {
    let sessao = null;
    try { ({ data: { session: sessao } } = await sb.auth.getSession()); } catch (_) { return; }
    if (!sessao || window.Design.nivel(sessao) === 'sem') return;   // sem sessão do Design: sem botão
    utilizador = sessao.user.id;
    const st = document.createElement('style');
    st.textContent = CSS;
    document.head.appendChild(st);
    const botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'dc-com-botao';
    botao.title = `Crítica ou comentário sobre o ${NOME}`;
    botao.setAttribute('aria-label', `Crítica ou comentário sobre o ${NOME}`);
    botao.innerHTML = `${IC}<span>Comentar</span>`;
    const dlg = document.createElement('dialog');
    dlg.className = 'dc-com-dlg';
    dlg.setAttribute('aria-label', 'Crítica ou comentário');
    document.body.append(botao, dlg);
    botao.addEventListener('click', () => abrir(dlg));
    // sempre no canto da parte visível do ecrã: numa página mais larga do que o telemóvel (o Build Your House ainda não
    // está adaptado), o canto da página fica fora da vista
    const vv = window.visualViewport;
    const posicionar = () => {
      if (!vv) return;
      const r = botao.getBoundingClientRect();
      const dentro = Math.abs(vv.offsetLeft) < 1 && Math.abs(vv.offsetTop) < 1 && Math.abs(vv.width - document.documentElement.clientWidth) < 2
        && Math.abs(vv.height - window.innerHeight) < 2;
      if (dentro) { botao.style.left = botao.style.top = ''; return; }   // o normal: o CSS (direita, em baixo) chega
      botao.style.left = `${vv.offsetLeft + vv.width - r.width - 16}px`;
      botao.style.top = `${vv.offsetTop + vv.height - r.height - 16 - ACIMA}px`;
    };
    if (vv) { vv.addEventListener('resize', posicionar); vv.addEventListener('scroll', posicionar); }
    window.addEventListener('resize', posicionar);
    posicionar();
    setTimeout(posicionar, 500);
    dlg.addEventListener('click', (e) => {
      if (e.target === dlg) { dlg.close(); return; }   // clique fora
      const el = e.target.closest('button');
      if (!el) return;
      if (el.dataset.com === 'fechar') dlg.close();
      else if (el.dataset.tipo) dlg.querySelectorAll('[data-tipo]').forEach((b) => b.setAttribute('aria-pressed', b === el));
      else if (el.dataset.comTirar != null) { pendentes.splice(Number(el.dataset.comTirar), 1); desenharAnexos(dlg); }
    });
    dlg.addEventListener('change', (e) => { if (e.target.name === 'ficheiros') { juntar(dlg, e.target.files); e.target.value = ''; } });
    dlg.addEventListener('paste', (e) => { if (e.clipboardData && e.clipboardData.files.length) { e.preventDefault(); juntar(dlg, e.clipboardData.files); } });
    dlg.addEventListener('submit', (e) => { e.preventDefault(); enviar(dlg, e.target); });
    // as teclas da app não reagem enquanto se escreve (ex.: atalhos do Build Your House)
    dlg.addEventListener('keydown', (e) => e.stopPropagation());
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', montar); else montar();
})();
