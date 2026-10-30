// Porta das páginas internas (ex.: /configurador/): só com sessão do Design (entrada pela conta do Hub).
// Sem sessão, volta à página inicial para entrar e depois regressa aqui (?voltar=).
(function () {
  const raiz = document.documentElement;
  raiz.style.visibility = 'hidden';
  Design.sb.auth.getSession().then(({ data: { session } }) => {
    if (session && Design.nivel(session) !== 'sem') { raiz.style.visibility = ''; return; }
    location.replace('/?voltar=' + encodeURIComponent(location.pathname));
  }, () => location.replace('/'));
})();
