// Ligação ao projeto Supabase do Design (outro projeto, noutra organização: não é o do Hub).
// Só a chave PÚBLICA (publishable) pode estar aqui. Nunca a chave de serviço, nem nada do Hub.
(function () {
  const URL = 'https://uuofvywhouhffmfqojoc.supabase.co';
  const CHAVE_PUBLICA = 'sb_publishable_kmMtb5iL4rGxmBz6vQ7H_w_vX-PHrxp';
  const HUB = 'https://hub.discovercasa.pt';

  const sb = window.supabase.createClient(URL, CHAVE_PUBLICA);

  // nível da pessoa no Design ("ver" / "editar"), decidido no Hub (permissão "Design") e guardado em app_metadata
  const nivel = (sessao) => (sessao && sessao.user && sessao.user.app_metadata && sessao.user.app_metadata.nivel) || 'sem';

  // Entrada com a conta do Hub: o Hub manda um código de uso único por postMessage (nunca no endereço).
  // - aberto pelo Hub (separador Design → "Abrir o Design"): avisa a janela do Hub que está pronto e espera o código;
  // - aberto à parte: "Entrar com a conta do Hub" abre o Hub numa janela que devolve o código.
  function esperarCodigo() {
    return new Promise((ok, falha) => {
      window.addEventListener('message', async function ouvir(e) {
        if (e.origin !== HUB || !e.data) return;
        if (e.data.tipo === 'design-erro') { window.removeEventListener('message', ouvir); falha(new Error(e.data.erro)); return; }
        if (e.data.tipo !== 'design-entrada' || !e.data.token_hash) return;
        window.removeEventListener('message', ouvir);
        const { data, error } = await sb.auth.verifyOtp({ token_hash: e.data.token_hash, type: 'email' });
        if (error) falha(new Error('O código de entrada expirou. Volte a abrir o Design a partir do Hub.')); else ok(data.session);
      });
    });
  }
  function avisarHub() {
    if (window.opener && window.name === 'hub-design') { window.opener.postMessage({ tipo: 'design-pronto' }, HUB); return true; }
    return false;
  }
  function entrarPeloHub() {
    const j = window.open(HUB + '/design', 'hub-design-entrar');
    if (!j) throw new Error('O browser bloqueou a janela do Hub. Permita janelas deste site e tente outra vez.');
  }

  window.Design = { sb, nivel, esperarCodigo, avisarHub, entrarPeloHub, HUB };
})();
