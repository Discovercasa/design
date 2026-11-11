// Porta das páginas internas (ex.: /configurador/): só com sessão do Design (entrada pela conta do Hub).
// Sem sessão, volta à página inicial para entrar e depois regressa aqui (?voltar=).
(function () {
  const raiz = document.documentElement;
  raiz.style.visibility = 'hidden';
  Design.sb.auth.getSession().then(({ data: { session } }) => {
    if (session && Design.nivel(session) !== 'sem') { raiz.style.visibility = ''; comentar(); return; }
    location.replace('/?voltar=' + encodeURIComponent(location.pathname));
  }, () => location.replace('/'));
  // o botão «Comentar» (críticas e comentários sobre a app, 2026-11-11): só depois de confirmar a sessão
  function comentar() {
    const s = document.createElement('script');
    s.src = '/js/comentar.js';
    document.head.appendChild(s);
  }
})();
