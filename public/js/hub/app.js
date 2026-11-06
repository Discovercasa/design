// Hub do Design: entrada (conta do Hub), barra de navegação, rotas (#/, #/projeto/<slug>, #/pessoal, #/definicoes,
// #/novidades, #/social), notificações, sugestões, decisões e o pop-up "Novo".
import * as D from './dados.js';
import { E } from './dados.js';
import * as V from './vistas.js';
import * as P from './paineis.js';
import * as SO from './social.js';
import { $, $$, ic, esc, iniciais, aviso, abrirDialogo, fecharDialogo, entrar, encherBarras, mov, luz } from './util.js';

const { sb, nivel } = window.Design;
const dlg = $('#dlg'), gaveta = $('#gaveta');
let novidades = [], pedidoInstalar = null, rotaAnterior = '', relogio = null;
const sug = { sep: 'sugestoes', lista: [], abertas: new Set(), erro: '' };

// ---------------------------------------------------------------- entrada
function mostrarEntrada(msg, erro) {
  $('#ecra-entrar').hidden = false; $('#topo').hidden = true; $('#vista').hidden = true;
  if (msg != null) { $('#entrar-msg').textContent = msg; $('#entrar-msg').className = erro ? 'erro-msg pequeno' : 'suave pequeno'; }
}
async function entrarComCodigo() {
  try { await arrancar(await Design.esperarCodigo()); } catch (e) { mostrarEntrada(e.message, true); }
}
$('#entrar').addEventListener('click', () => {
  try { entrarComCodigo(); Design.entrarPeloHub(); mostrarEntrada('A entrar com a conta do Hub…'); } catch (e) { mostrarEntrada(e.message, true); }
});

(async () => {
  const { data: { session } } = await sb.auth.getSession();
  if (session && nivel(session) !== 'sem') return arrancar(session);
  if (session) { mostrarEntrada('A tua conta não tem acesso ao Design. Pede a permissão "Design" no Hub.', true); return; }
  mostrarEntrada();
  if (window.opener && window.name === 'hub-design') { mostrarEntrada('A entrar com a conta do Hub…'); entrarComCodigo(); Design.avisarHub(); }
})();

async function arrancar(sessao) {
  if (!sessao || nivel(sessao) === 'sem') return mostrarEntrada('A tua conta não tem acesso ao Design.', true);
  // veio de uma página interna (porta.js): depois de entrar, volta para lá
  const voltar = new URLSearchParams(location.search).get('voltar');
  if (voltar && /^\/(build-your-house|gerador)\//.test(voltar)) return location.replace(voltar);
  E.eu = { id: sessao.user.id, nome: (sessao.user.user_metadata && sessao.user.user_metadata.nome) || '', editar: nivel(sessao) === 'editar' };
  $('#ecra-entrar').hidden = true; $('#topo').hidden = false; $('#vista').hidden = false;
  $('#vista').innerHTML = V.esqueleto();
  $('#b-sugestoes').innerHTML = ic('sugestao');
  $('#b-notificacoes').innerHTML = ic('sino') + '<span class="contador" id="contador" hidden></span>';
  await D.carregarProjetos();
  novidades = await fetch('/dados/novidades.json').then((r) => r.json()).catch(() => []);
  desenharNav();
  try {
    await D.garantirPerfil(sessao);
    await D.carregarTudo();
    await D.carregarNotificacoes();
  } catch (e) {
    E.erro = e.message || String(e);
  }
  $('#avatar').textContent = iniciais(E.eu.nome);
  atualizarContador();
  desenhar(true);
  if (!E.erro) mostrarNovos();
  clearInterval(relogio);
  relogio = setInterval(atualizar, 60000);   // reserva, se a ligação em direto cair
  if (!E.erro) D.ouvirMudancas(emDireto);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) atualizar(); });
}

// ---------------------------------------------------------------- navegação e rotas
function rota() {
  const h = location.hash.replace(/^#\/?/, '');
  const [a, b, c] = h.split('/');
  if (a === 'projeto') return { nome: 'projeto', p: D.projetoPorSlug(b), alvo: c };
  if (['pessoal', 'definicoes', 'novidades'].includes(a)) return { nome: a };
  if (a === 'social') return { nome: 'social', sub: b === 'obras' ? 'obras' : 'planeamento', alvo: b === 'obras' ? c : b };
  return { nome: 'inicio' };
}
function desenharNav() {
  const r = rota();
  $('#nav').innerHTML = `<a href="#/"${r.nome === 'inicio' ? ' aria-current="page"' : ''}>Início</a>` +
    E.projetos.map((p) => `<a href="#/projeto/${p.slug}"${r.nome === 'projeto' && r.p === p ? ' aria-current="page"' : ''}>${esc(p.nome)}</a>`).join('') +
    `<a class="nav-separada" href="#/social"${r.nome === 'social' ? ' aria-current="page"' : ''}>Redes sociais</a>`;
  const atual = $('#nav [aria-current]');
  if (atual) atual.scrollIntoView({ block: 'nearest', inline: 'nearest' });
}
function desenhar(mudouRota) {
  const r = rota(), v = $('#vista');
  const aviso_ = E.erro ? `<div class="nota" style="margin-bottom:32px;border-color:var(--erro)">${ic('atencao')}<p><b>Os checkpoints, tarefas e decisões ainda não estão disponíveis.</b> A base de dados do hub precisa das migrações 0004 e 0005. <span class="fraco">(${esc(E.erro)})</span></p></div>` : '';
  let html;
  if (r.nome === 'projeto' && r.p) { html = V.paginaProjeto(r.p); document.title = `${r.p.nome} · Discovercasa Design`; }
  else if (r.nome === 'pessoal') { html = V.pessoal(); document.title = 'Área pessoal · Discovercasa Design'; }
  else if (r.nome === 'definicoes') { html = V.definicoes(!!pedidoInstalar); document.title = 'Definições · Discovercasa Design'; }
  else if (r.nome === 'social') { html = SO.pagina(r.sub); document.title = 'Redes sociais · Discovercasa Design'; }
  else if (r.nome === 'novidades') { html = V.novidades(novidades); document.title = 'Novidades · Discovercasa Design'; marcarNovidadesVistas(); }
  else { html = V.inicio(); document.title = 'Início · Discovercasa Design'; }
  const y = window.scrollY;
  v.innerHTML = aviso_ + html;
  encherBarras(v);
  SO.depoisDeDesenhar(v);
  const calc = $('form[data-form="calculadora"]', v);
  if (calc) V.calcular(calc, r.p.cambio.usd_eur);
  if (mudouRota) {
    window.scrollTo(0, 0);
    entrar($$('.projeto-linha, .passo, .cabeca-pagina, .projeto-cabeca, .cta-app, .bloco-lateral, .novidade, .cartoes-pessoal > *, .social-barra, .mes, .obra, .visita', v));
    if (r.alvo) irPara(r.alvo);
  } else window.scrollTo(0, y);
}
function irPara(alvo) {
  if (/^(post|obra)-\d+$/.test(alvo || '')) return SO.irPara(alvo);
  const m = /^(t|cp|doc)-(\d+)$/.exec(alvo || '');
  if (!m) return;
  const id = Number(m[2]);
  if (m[1] === 'doc') { const g = document.getElementById(alvo); const det = g && g.closest('details'); if (det) det.open = true; }
  const cpId = m[1] === 't' ? (E.tarefas.find((t) => t.id === id) || {}).checkpoint_id : m[1] === 'cp' ? id : null;
  if (cpId && !V.abertos.has(cpId)) { V.abertos.add(cpId); desenhar(false); }
  const el = document.getElementById(alvo);
  if (!el) return;
  el.scrollIntoView({ block: 'center', behavior: mov() ? 'smooth' : 'auto' });
  el.classList.remove('alvo'); void el.offsetWidth; el.classList.add('alvo');
}
window.addEventListener('hashchange', () => {
  if (!E.eu.id) return;
  const r = rota();
  const chaveRota = r.nome + (r.p ? r.p.id : '') + (r.sub || '');
  fecharPops();
  desenharNav();
  if (chaveRota === rotaAnterior && r.alvo) return irPara(r.alvo);
  rotaAnterior = chaveRota;
  desenhar(true);
});
rotaAnterior = (() => { const r = rota(); return r.nome + (r.p ? r.p.id : '') + (r.sub || ''); })();
luz($('#vista'));
SO.ligar({ dlg, desenhar, depois, tentar });

// o logótipo "Discovercasa Design": volta ao Início e atualiza o hub (dados e notificações)
$('.marca').addEventListener('click', async (e) => {
  e.preventDefault();
  if (!E.eu.id) return;
  fecharPops();
  if (location.hash.replace(/^#\/?/, '')) location.hash = '#/';  // o hashchange desenha o Início
  else desenhar(true);
  try {
    await D.carregarNotificacoes();
    await D.carregarTudo();
    E.erro = null;
  } catch (err) { E.erro = err.message || String(err); }
  atualizarContador();
  desenhar(false);
  if (!E.erro) mostrarNovos();
});

// âncoras dentro da página (ex.: #decisoes-abertas) não mudam a rota
document.addEventListener('click', (e) => {
  const a = e.target.closest('a[href^="#"]:not([href^="#/"])');
  if (!a) return;
  const el = document.getElementById(a.getAttribute('href').slice(1));
  if (el) { e.preventDefault(); el.scrollIntoView({ behavior: mov() ? 'smooth' : 'auto' }); }
});

// ---------------------------------------------------------------- notificações e "Novo"
function atualizarContador() {
  const n = D.naoLidas().length, c = $('#contador');
  if (!c) return;
  c.hidden = !n; c.textContent = n > 9 ? '9+' : n;
  $('#b-notificacoes').setAttribute('aria-label', n ? `Notificações (${n} por ler)` : 'Notificações');
}
async function atualizar() {
  if (E.erro || document.hidden) return;
  try {
    const novas = await D.carregarNotificacoes();
    await D.carregarTudo();
    novas.slice(0, 3).forEach((n) => aviso(esc(n.texto), { icone: 'sino', acoes: [{ rotulo: 'Ver', fazer: () => irNotif(n.projeto, n.ref_tipo, n.ref_id) }] }));
    atualizarContador();
    if (!dlg.open && !gaveta.open && !document.activeElement.matches('input, textarea, select')) desenhar(false);
    mostrarNovos();
  } catch (_) { /* sem rede: tenta no próximo minuto */ }
}
// em direto: uma mudança feita por qualquer pessoa (ou noutra janela) atualiza já todos os sítios onde aparece
let emDiretoEspera = null, mudouNotificacoes = false;
function emDireto(tabela) {
  if (tabela === 'notificacoes') mudouNotificacoes = true;
  clearTimeout(emDiretoEspera);
  emDiretoEspera = setTimeout(async () => {
    try {
      const novas = mudouNotificacoes ? await D.carregarNotificacoes() : [];
      mudouNotificacoes = false;
      await D.carregarTudo();
      novas.slice(0, 3).forEach((n) => aviso(esc(n.texto), { icone: 'sino', acoes: [{ rotulo: 'Ver', fazer: () => irNotif(n.projeto, n.ref_tipo, n.ref_id) }] }));
      atualizarContador();
      if (!dlg.open && !document.activeElement.matches('input, textarea, select')) desenhar(false);
      SO.aoMudar();
      mostrarNovos();
    } catch (_) { /* tenta na próxima mudança ou no relógio */ }
  }, 350);
}

// pop-up na primeira vez que vejo um checkpoint, tarefa ou decisão acrescentados por outra pessoa
function mostrarNovos() {
  const itens = D.porVer();
  if (!itens.length) return;
  itens.forEach((i) => E.novos.add(D.chave(i.tipo, i.x.id)));
  const nomeTipo = { checkpoint: 'Novo checkpoint', tarefa: 'Nova tarefa', decisao: 'Nova decisão', documento: 'Novo documento', post: 'Novo post', obra: 'Nova obra' };
  const onde = (i) => (i.x.projeto ? D.nomeProjeto(i.x.projeto) : 'Redes sociais'), nome = (i) => i.x.titulo || i.x.pergunta || i.x.nome;
  const ir = (i) => irNotif(i.x.projeto, i.tipo, i.x.id);
  if (itens.length > 3) {
    aviso(`<b>${itens.length} novidades nos projetos</b><br>${itens.slice(0, 4).map((i) => `${nomeTipo[i.tipo]} em ${esc(onde(i))}: «${esc(nome(i))}»`).join('<br>')}${itens.length > 4 ? '<br>…' : ''}`,
      { icone: 'novo', duracao: 10, acoes: [{ rotulo: 'Ver a primeira', fazer: () => ir(itens[0]) }] });
  } else itens.forEach((i) => aviso(`<b>${nomeTipo[i.tipo]}</b> em ${esc(onde(i))}<br>«${esc(nome(i))}» · por ${esc(i.x.criado_por_nome || 'alguém')}`,
    { icone: 'novo', duracao: 10, acoes: [{ rotulo: 'Ver', fazer: () => ir(i) }] }));
  D.marcarVistos(itens).catch(() => {});
  desenhar(false);
}
function irNotif(projetoId, tipo, id) {
  if (tipo === 'post') { location.hash = `#/social/post-${id}`; return; }
  if (tipo === 'obra') { location.hash = `#/social/obras/obra-${id}`; return; }
  const p = D.projeto(projetoId);
  if (!p) return;
  if (tipo === 'decisao') {
    location.hash = `#/projeto/${p.slug}`;
    const d = E.decisoes.find((x) => x.id === Number(id));
    if (d) setTimeout(() => abrirDialogo(dlg, P.dlgDecisao(d)), 50);
    return;
  }
  location.hash = `#/projeto/${p.slug}/${tipo === 'checkpoint' ? 'cp' : tipo === 'documento' ? 'doc' : 't'}-${id}`;
}

// ---------------------------------------------------------------- popovers (notificações e perfil)
function abrirPop(botao, pop, html) {
  const aberto = !pop.hidden;
  fecharPops();
  if (aberto) return;
  pop.innerHTML = html;
  const r = botao.getBoundingClientRect();
  pop.style.top = `${r.bottom + 8}px`;
  pop.style.right = `${Math.max(16, window.innerWidth - r.right)}px`;
  pop.hidden = false;
  botao.setAttribute('aria-expanded', 'true');
  if (mov()) gsap.fromTo(pop, { autoAlpha: 0, y: -6 }, { autoAlpha: 1, y: 0, duration: 0.2, ease: 'expo.out', clearProps: 'transform' });
  const primeiro = pop.querySelector('button, a');
  if (primeiro) primeiro.focus({ preventScroll: true });
}
function fecharPops() {
  [['#pop-notificacoes', '#b-notificacoes'], ['#pop-perfil', '#b-perfil']].forEach(([p, b]) => { $(p).hidden = true; $(b).setAttribute('aria-expanded', 'false'); });
}
const novidadeNova = () => { try { return !!novidades[0] && localStorage.getItem('hub-novidades-vista') !== novidades[0].dia; } catch (_) { return false; } };
function marcarNovidadesVistas() { try { if (novidades[0]) localStorage.setItem('hub-novidades-vista', novidades[0].dia); } catch (_) {} }
$('#b-notificacoes').addEventListener('click', (e) => { e.stopPropagation(); abrirPop(e.currentTarget, $('#pop-notificacoes'), P.htmlNotificacoes()); });
$('#b-perfil').addEventListener('click', (e) => { e.stopPropagation(); abrirPop(e.currentTarget, $('#pop-perfil'), P.htmlPerfil(novidadeNova())); });
$('#b-sugestoes').addEventListener('click', () => { abrirDialogo(gaveta, P.htmlGaveta(sug.sep, sug.lista, sug.abertas, sug.erro)); carregarSugestoes(); });
document.addEventListener('click', (e) => { if (!e.target.closest('.pop')) fecharPops(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') fecharPops(); });
[dlg, gaveta].forEach((d) => {
  d.addEventListener('click', (e) => { if (e.target === d) fecharDialogo(d); });  // clique fora
  d.addEventListener('cancel', (e) => { e.preventDefault(); fecharDialogo(d); });
});

// ---------------------------------------------------------------- sugestões
async function carregarSugestoes() {
  const { data, error } = await sb.from('sugestoes')
    .select('id, texto, ferramenta, estado, autor_id, autor_nome, criada_em, na_checklist, checklist_em, sugestoes_comentarios (id, texto, autor_id, autor_nome, criado_em)')
    .order('criada_em', { ascending: false }).limit(200);
  sug.erro = error ? error.message : '';
  if (!error) { data.forEach((g) => (g.sugestoes_comentarios || []).sort((a, b) => new Date(a.criado_em) - new Date(b.criado_em))); sug.lista = data; }
  if (gaveta.open) {
    const corpo = $('.gaveta-corpo', gaveta), y = corpo ? corpo.scrollTop : 0;
    gaveta.innerHTML = P.htmlGaveta(sug.sep, sug.lista, sug.abertas, sug.erro);
    const novo = $('.gaveta-corpo', gaveta); if (novo) novo.scrollTop = y;
  }
}
async function mudarSugestao(id, campos) {
  const { error } = await sb.from('sugestoes').update(campos).eq('id', id);
  if (error) aviso('Não foi possível mudar a sugestão: ' + esc(error.message), { icone: 'atencao' });
  carregarSugestoes();
}

// ---------------------------------------------------------------- ações (cliques)
async function tentar(fn, form) {
  const msg = form && $('.erro-msg', form);
  try { await fn(); return true; } catch (e) {
    if (msg) msg.textContent = 'Não foi possível guardar: ' + (e.message || e);
    else aviso('Não foi possível guardar: ' + esc(e.message || e), { icone: 'atencao' });
    return false;
  }
}
async function depois() { try { await D.carregarNotificacoes(); } catch (_) {} atualizarContador(); desenhar(false); }

document.addEventListener('click', async (e) => {
  const el = e.target.closest('[data-acao]');
  if (!el || el.matches('select, input[type=checkbox]')) return;
  const id = Number(el.dataset.id);
  switch (el.dataset.acao) {
    case 'alternar-cp': {
      const det = document.getElementById('cpd-' + id), li = el.closest('.passo');
      const abrir = det.hidden;
      if (abrir) V.abertos.add(id); else V.abertos.delete(id);
      det.hidden = !abrir; li.classList.toggle('aberto', abrir); el.setAttribute('aria-expanded', abrir);
      if (abrir && mov()) gsap.from(det, { autoAlpha: 0, y: -4, duration: 0.25, ease: 'expo.out', clearProps: 'all' });
      return;
    }
    case 'acrescentar': return abrirDialogo(dlg, P.dlgAcrescentar(el.dataset.projeto || (rota().p || {}).id, null, el.dataset.tipo));
    case 'acrescentar-doc': return abrirDialogo(dlg, P.dlgDocumento(el.dataset.projeto), { estreito: true });
    case 'tipo-doc': {
      const f = el.closest('form'); f.elements.tipo.value = el.dataset.valor;
      $$('[data-acao="tipo-doc"]', f).forEach((b) => b.setAttribute('aria-pressed', b === el));
      return;
    }
    case 'abrir-doc': {
      const d = E.documentos.find((x) => x.id === id);
      const janela = window.open('about:blank', '_blank');  // já, para o browser não bloquear a janela
      try { const url = await D.urlDocumento(d); if (janela) janela.location.href = url; else location.href = url; }
      catch (err) { if (janela) janela.close(); aviso('Não foi possível abrir o documento: ' + esc(err.message || err), { icone: 'atencao' }); }
      return;
    }
    case 'apagar-doc': {
      const d = E.documentos.find((x) => x.id === id);
      if (!confirm(`Apagar o documento «${d.titulo}»? O ficheiro deixa de estar disponível para a equipa.`)) return;
      if (await tentar(() => D.apagarDocumento(d))) depois();
      return;
    }
    case 'tipo-novo': {
      const f = el.closest('form'), t = el.dataset.valor;
      f.elements.tipo.value = t;
      $$('[data-acao="tipo-novo"]', f).forEach((b) => b.setAttribute('aria-pressed', b === el));
      $$('.so-tarefa', f).forEach((x) => (x.hidden = t !== 'tarefa'));
      $$('.so-checkpoint', f).forEach((x) => (x.hidden = t !== 'checkpoint'));
      return;
    }
    case 'editar-tarefa': return abrirDialogo(dlg, P.dlgEditarTarefa(E.tarefas.find((t) => t.id === id)));
    case 'editar-cp': return abrirDialogo(dlg, P.dlgEditarCheckpoint(E.checkpoints.find((c) => c.id === id)), { estreito: true });
    case 'ver-decisao': return abrirDialogo(dlg, P.dlgDecisao(E.decisoes.find((d) => d.id === id)));
    case 'nova-decisao': {
      const t = E.tarefas.find((x) => x.id === Number(el.dataset.tarefa));
      return abrirDialogo(dlg, P.dlgNovaDecisao(t, t ? t.projeto : (rota().p || E.projetos[0]).id));
    }
    case 'mais-opcao': {
      const c = $('#opcoes-edicao'); c.insertAdjacentHTML('beforeend', P.htmlOpcaoEdicao(c.children.length + 1));
      c.lastElementChild.querySelector('input').focus(); return;
    }
    case 'tirar-opcao': { const c = $('#opcoes-edicao'); if (c.children.length > 2) el.closest('[data-opcao]').remove(); return; }
    case 'reabrir-decisao':
      if (!confirm('Reabrir esta decisão? A escolha registada deixa de valer até se decidir outra vez.')) return;
      if (await tentar(() => D.reabrirDecisao(id))) { abrirDialogo(dlg, P.dlgDecisao(E.decisoes.find((d) => d.id === id))); depois(); }
      return;
    case 'apagar-decisao':
      if (!confirm('Apagar esta decisão e as suas opções?')) return;
      if (await tentar(() => D.apagarDecisao(id))) { fecharDialogo(dlg); depois(); }
      return;
    case 'apagar-tarefa':
      if (!confirm('Apagar esta tarefa?')) return;
      if (await tentar(() => D.apagarTarefa(id))) { fecharDialogo(dlg); depois(); }
      return;
    case 'apagar-cp':
      if (!confirm('Apagar este checkpoint e todas as suas tarefas?')) return;
      if (await tentar(() => D.apagarCheckpoint(id))) { fecharDialogo(dlg); depois(); }
      return;
    case 'fechar-dlg': return fecharDialogo(el.closest('dialog'));
    case 'ler-todas': await D.marcarNotificacoesLidas(); atualizarContador(); $('#pop-notificacoes').innerHTML = P.htmlNotificacoes(); return;
    case 'ir-notif': fecharPops(); return irNotif(el.dataset.projeto, el.dataset.ref, el.dataset.id);
    case 'sair': await sb.auth.signOut(); location.replace('/'); return;
    case 'tema': {
      const v = el.dataset.valor;
      try { if (v === 'sistema') localStorage.removeItem('hub-tema'); else localStorage.setItem('hub-tema', v); } catch (_) {}
      if (v === 'sistema') delete document.documentElement.dataset.theme; else document.documentElement.dataset.theme = v;
      return desenhar(false);
    }
    case 'movimento': {
      const v = el.dataset.valor;
      try { localStorage.setItem('hub-movimento', v); } catch (_) {}
      if (v === 'reduzido') document.documentElement.dataset.movimento = 'reduzido'; else delete document.documentElement.dataset.movimento;
      return desenhar(false);
    }
    case 'instalar':
      if (!pedidoInstalar) return;
      pedidoInstalar.prompt(); try { await pedidoInstalar.userChoice; } catch (_) {}
      pedidoInstalar = null; return desenhar(false);
    // sugestões
    case 'sug-sep': sug.sep = el.dataset.valor; gaveta.innerHTML = P.htmlGaveta(sug.sep, sug.lista, sug.abertas, sug.erro); return;
    case 'sug-comentarios': if (sug.abertas.has(id)) sug.abertas.delete(id); else sug.abertas.add(id); gaveta.innerHTML = P.htmlGaveta(sug.sep, sug.lista, sug.abertas, sug.erro); return;
    case 'sug-checklist': {
      const g = sug.lista.find((x) => x.id === id);
      return mudarSugestao(id, { na_checklist: true, checklist_em: new Date().toISOString(), ...(g && g.estado === 'nova' ? { estado: 'em_analise' } : {}) });
    }
    case 'sug-tirar': return mudarSugestao(id, { na_checklist: false, checklist_em: null });
    case 'sug-apagar': {
      if (!confirm('Eliminar esta sugestão e os seus comentários?')) return;
      const { error } = await sb.from('sugestoes').delete().eq('id', id);
      if (error) aviso('Não foi possível eliminar: ' + esc(error.message), { icone: 'atencao' });
      return carregarSugestoes();
    }
    case 'sug-apagar-comentario': {
      if (!confirm('Apagar este comentário?')) return;
      const { error } = await sb.from('sugestoes_comentarios').delete().eq('id', id);
      if (error) aviso('Não foi possível apagar o comentário: ' + esc(error.message), { icone: 'atencao' });
      return carregarSugestoes();
    }
  }
});

// ---------------------------------------------------------------- ações (mudanças em seletores e caixas)
document.addEventListener('change', async (e) => {
  const el = e.target;
  const id = Number(el.dataset.id);
  switch (el.dataset.acao) {
    case 'concluir': {
      const estado = el.checked ? 'concluida' : 'em_curso';
      if (await tentar(() => D.mudarTarefa(id, { estado }))) {
        if (estado === 'concluida') aviso('Tarefa concluída. A equipa foi avisada.', { icone: 'certo', duracao: 3 });
        depois();
      } else el.checked = !el.checked;
      return;
    }
    case 'estado-tarefa': if (await tentar(() => D.mudarTarefa(id, { estado: el.value }))) depois(); return;
    case 'estado-cp': if (await tentar(() => D.mudarCheckpoint(id, { estado: el.value }))) depois(); return;
    case 'projeto-novo': { const f = el.closest('form'); f.elements.checkpoint.innerHTML = P.opcoesCheckpoints(el.value); f.elements.posicao.innerHTML = P.opcoesPosicao(el.value); return; }
    case undefined:
      if (el.name === 'ficheiros') {
        const lista = el.closest('form').querySelector('[data-escolhidos]');
        lista.innerHTML = [...el.files].map((x) => `<li>${esc(x.name)} · ${(x.size / 1e6).toLocaleString('pt-PT', { maximumFractionDigits: 1 })} MB</li>`).join('');
      }
      return;
    case 'sug-estado': return mudarSugestao(id, { estado: el.value });
    case 'sug-concluir': return mudarSugestao(id, { estado: el.checked ? 'feita' : 'em_analise' });
  }
});
document.addEventListener('input', (e) => {
  const f = e.target.closest('form[data-form="calculadora"]');
  if (f) V.calcular(f, (rota().p || {}).cambio.usd_eur);
});

// ---------------------------------------------------------------- formulários
document.addEventListener('submit', async (e) => {
  const f = e.target, tipo = f.dataset.form;
  if (!tipo || tipo === 'calculadora') return;
  e.preventDefault();
  const v = (n) => (f.elements[n] ? f.elements[n].value.trim() : '');
  const botao = f.querySelector('[type=submit]');
  if (botao) botao.disabled = true;
  let ok = false;
  try {
    switch (tipo) {
      case 'nova-tarefa':
        ok = await tentar(() => D.criarTarefa({ checkpoint_id: Number(f.dataset.cp), titulo: v('titulo'), projeto: E.checkpoints.find((c) => c.id === Number(f.dataset.cp)).projeto, ordem: D.tarefasDe(Number(f.dataset.cp)).length + 1 }));
        if (ok) { await depois(); const campo = $(`form[data-cp="${f.dataset.cp}"] input`); if (campo) campo.focus(); }
        return;
      case 'acrescentar': {
        const projetoId = v('projeto');
        if (v('tipo') === 'checkpoint') {
          ok = await tentar(() => D.criarCheckpoint({ projeto: projetoId, titulo: v('titulo'), descricao: v('descricao') }, Number(v('posicao')) || null), f);
        } else {
          const cp = Number(v('checkpoint'));
          if (!cp) { $('.erro-msg', f).textContent = 'Este projeto ainda não tem checkpoints: acrescenta primeiro um checkpoint.'; return; }
          ok = await tentar(() => D.criarTarefa({ checkpoint_id: cp, projeto: projetoId, titulo: v('titulo'), descricao: v('descricao'), responsavel_id: v('responsavel') || null,
            app_sugerida: v('app') || null, custo: v('custo'), ordem: D.tarefasDe(cp).length + 1 }), f);
          if (ok) V.abertos.add(cp);
        }
        if (ok) { fecharDialogo(dlg); aviso('Acrescentado. Quem entrar a seguir vai vê-lo como novo.', { icone: 'certo', duracao: 3 }); depois(); }
        return;
      }
      case 'editar-tarefa':
        ok = await tentar(() => D.mudarTarefa(Number(f.dataset.id), { titulo: v('titulo'), descricao: v('descricao'), checkpoint_id: Number(v('checkpoint')), estado: v('estado'),
          responsavel_id: v('responsavel') || null, app_sugerida: v('app') || null, custo: v('custo') }), f);
        if (ok) { fecharDialogo(dlg); depois(); }
        return;
      case 'editar-cp':
        ok = await tentar(async () => {
          const id = Number(f.dataset.id), c = E.checkpoints.find((x) => x.id === id);
          const antes = D.checkpointsDe(c.projeto).findIndex((x) => x.id === id) + 1, depoisPos = Number(v('posicao'));
          await D.mudarCheckpoint(id, { titulo: v('titulo'), descricao: v('descricao'), estado: v('estado') });
          if (depoisPos && depoisPos !== antes) await D.moverCheckpoint(id, depoisPos);
        }, f);
        if (ok) { fecharDialogo(dlg); depois(); }
        return;
      case 'decidir': {
        const escolha = f.querySelector('input[name=opcao]:checked');
        if (!escolha) { $('.erro-msg', f).textContent = 'Escolhe uma opção.'; return; }
        const id = Number(f.dataset.id);
        ok = await tentar(() => D.decidir(id, Number(escolha.value), v('justificacao')), f);
        if (ok) { abrirDialogo(dlg, P.dlgDecisao(E.decisoes.find((d) => d.id === id))); depois(); }
        return;
      }
      case 'nova-decisao': {
        const opcoes = $$('[data-opcao]', f).map((o) => ({ titulo: o.querySelector('[name=o_titulo]').value.trim(), descricao: o.querySelector('[name=o_descricao]').value.trim(),
          vantagens: o.querySelector('[name=o_vantagens]').value.trim(), desvantagens: o.querySelector('[name=o_desvantagens]').value.trim(), custo: o.querySelector('[name=o_custo]').value.trim() })).filter((o) => o.titulo);
        if (opcoes.length < 2) { $('.erro-msg', f).textContent = 'Uma decisão precisa de pelo menos duas opções.'; return; }
        ok = await tentar(() => D.criarDecisao({ projeto: f.dataset.projeto, tarefa_id: Number(f.dataset.tarefa) || null, pergunta: v('pergunta'), contexto: v('contexto') }, opcoes), f);
        if (ok) { fecharDialogo(dlg); depois(); }
        return;
      }
      case 'documento': {
        const ficheiros = [...f.elements.ficheiros.files];
        if (!ficheiros.length) return;
        const grandes = ficheiros.filter((x) => x.size > 50 * 1024 * 1024);
        if (grandes.length) { $('.erro-msg', f).textContent = `Demasiado grande (máximo 50 MB): ${grandes.map((x) => x.name).join(', ')}`; return; }
        if (botao) botao.textContent = 'A carregar…';
        ok = await tentar(async () => {
          for (const x of ficheiros) await D.carregarDocumento(f.dataset.projeto, v('tipo'), x, ficheiros.length === 1 ? v('titulo') : '', v('descricao'));
          await D.carregarTudo();
        }, f);
        if (botao) botao.textContent = 'Carregar';
        if (ok) { fecharDialogo(dlg); aviso(ficheiros.length === 1 ? 'Documento carregado.' : `${ficheiros.length} documentos carregados.`, { icone: 'certo', duracao: 3 }); depois(); }
        return;
      }
      case 'nome':
        ok = await tentar(() => D.mudarNome(v('nome')));
        if (ok) { $('#avatar').textContent = iniciais(E.eu.nome); aviso('Nome guardado.', { icone: 'certo', duracao: 3 }); }
        return;
      case 'sugestao': {
        const msg = $('[data-msg]', f);
        const { error } = await sb.from('sugestoes').insert({ texto: v('texto'), ferramenta: v('ferramenta'), autor_nome: E.eu.nome });
        if (error) { msg.textContent = 'Não foi enviada: ' + error.message; return; }
        f.reset(); aviso('Obrigado! Sugestão enviada.', { icone: 'certo', duracao: 3 });
        return carregarSugestoes();
      }
      case 'comentario': {
        const { error } = await sb.from('sugestoes_comentarios').insert({ sugestao_id: Number(f.dataset.id), texto: v('texto'), autor_nome: E.eu.nome });
        if (error) { aviso('O comentário não foi enviado: ' + esc(error.message), { icone: 'atencao' }); return; }
        return carregarSugestoes();
      }
    }
  } finally { if (botao && botao.isConnected) botao.disabled = false; }
});

// ---------------------------------------------------------------- instalar como app
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});
window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); pedidoInstalar = e; });
window.addEventListener('appinstalled', () => { pedidoInstalar = null; });
