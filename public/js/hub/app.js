// Hub do Design: entrada (conta do Hub), barra de navegação, rotas (#/, #/projeto/<slug>, #/pessoal, #/definicoes,
// #/novidades, #/social), notificações, sugestões, decisões. Trabalho em equipa (2026-11-11): o ecrã de cada tarefa
// (ficha.js), o pop-up de cada projeto, as marcações, as críticas e o Log (equipa.js).
import * as D from './dados.js';
import { E } from './dados.js';
import * as V from './vistas.js';
import * as P from './paineis.js';
import * as SO from './social.js';
import * as MV from './materiais-vista.js';
import * as AA from './ar-android.js';
import * as FI from './ficha.js';
import * as EQ from './equipa.js';
import { abrirVisor, hidratar, saoImagens } from './imagens.js';
import { $, $$, ic, esc, iniciais, aviso, abrirDialogo, fecharDialogo, entrar, encherBarras, mov, luz } from './util.js';

const { sb, nivel } = window.Design;
const dlg = $('#dlg'), gaveta = $('#gaveta'), ficha = $('#ficha'), projetoPop = $('#projeto-pop');
let novidades = [], pedidoInstalar = null, rotaAnterior = '', relogio = null;
const sug = { sep: 'sugestoes', lista: [], abertas: new Set(), erro: '', logErro: '' };
// a gaveta das sugestões: Sugestões, Checklist e o Log (ao lado da checklist, pedido de 2026-11-11)
const htmlGaveta = () => P.htmlGaveta(sug.sep, sug.lista, sug.abertas, sug.erro, sug.sep === 'log' ? EQ.htmlLog(sug.logErro) : '');
function redesenharGaveta() {
  if (!gaveta.open) return;
  const corpo = $('.gaveta-corpo', gaveta), y = corpo ? corpo.scrollTop : 0;
  gaveta.innerHTML = htmlGaveta();
  const novo = $('.gaveta-corpo', gaveta); if (novo) novo.scrollTop = y;
}
async function abrirLog() {
  sug.sep = 'log';
  if (!gaveta.open) abrirDialogo(gaveta, htmlGaveta());
  try { await D.carregarRegisto(); sug.logErro = ''; } catch (e) { sug.logErro = e.message || String(e); }
  redesenharGaveta();
}

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
  if (voltar && /^\/(build-your-house|gerador|orcamentacao)\//.test(voltar)) return location.replace(voltar);
  E.eu = { id: sessao.user.id, nome: (sessao.user.user_metadata && sessao.user.user_metadata.nome) || '', editar: nivel(sessao) === 'editar' };
  $('#ecra-entrar').hidden = true; $('#topo').hidden = false; $('#vista').hidden = false;
  $('#vista').innerHTML = V.esqueleto();
  $('#b-sugestoes').innerHTML = ic('sugestao');
  $('#b-critica').innerHTML = ic('comentario');
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
  if (!E.erro) { mostrarNovos(); avisosDoLog(); mostrarMarcacoes(); }
  clearInterval(relogio);
  relogio = setInterval(atualizar, 60000);   // reserva, se a ligação em direto cair
  if (!E.erro) D.ouvirMudancas(emDireto);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) atualizar(); });
  guardarVersao();
  arAndroidFalhou();
}

// Step Inside: the Android «Ver em AR» opens Google's Scene Viewer through an intent. When the phone cannot open it, the
// page shows the model in 3D by itself (user, 2026-11-10: «se o cliente tiver um dispositivo qualquer tem de conseguir
// ver»). Two ways it fails (AR test page, 2026-11-10, a Redmi Note 14 Pro 5G, not on Google's ARCore list):
//   - Chrome follows the fallback link and comes back here with ?ar-android=<doc>;
//   - the Google app flashes a window for 0.2 s and nothing opens, the page never goes hidden (no fallback at all).
// Scene Viewer and Chrome's AR both need ARCore («Serviços Google Play para RA»), which Google only offers for the phones
// on its list: the notice links to it in the Play Store (it says whether this phone can install it).
const PLAY_ARCORE = 'https://play.google.com/store/apps/details?id=com.google.ar.core';
function arAndroidNaoAbriu(id, { jaAberto = false } = {}) {
  const d = E.documentos.find((x) => x.id === id);
  if (d && !jaAberto) verEm3D(id);
  aviso('O AR não abriu neste telemóvel: o AR da Google precisa da app «Serviços Google Play para RA» (ARCore), que só existe '
    + 'para os telemóveis da lista da Google. Abrimos o modelo em 3D aqui. Na Play Store vês se este telemóvel a pode instalar.',
    { icone: 'atencao', duracao: 0, acoes: [
      { rotulo: 'Ver na Play Store', fazer: () => { location.href = PLAY_ARCORE; } },
      ...(d ? [{ rotulo: 'Testar este Android', fazer: async () => { try { location.href = AA.paginaTeste(await D.urlAR(d), d); } catch (err) { aviso(err.message || String(err), { icone: 'atencao' }); } } }] : [])] });
}
function arAndroidFalhou() {
  const q = new URLSearchParams(location.search);
  if (!q.has('ar-android')) return;
  const id = Number(q.get('ar-android'));
  q.delete('ar-android');
  history.replaceState(null, '', location.pathname + (q.toString() ? '?' + q : '') + location.hash);
  arAndroidNaoAbriu(id);
}

// ---------------------------------------------------------------- versão nova do hub publicada
// Uma janela aberta mostra a versão em que foi aberta: o hub não se recarrega sozinho. Ao abrir guarda-se a
// assinatura (ETag) dos ficheiros do hub que a página carregou; de 3 em 3 minutos (no relógio de atualizar e ao voltar
// à janela) compara-se com a do site e, se mudou, um aviso deixa recarregar (utilizador, 2026-11-09: «Sim, avisa»).
const VERSAO_CADA = 3 * 60 * 1000;
let versao = null, versaoVista = 0, versaoAvisada = false;
function ficheirosDoHub() {
  // o que a página carregou (os módulos importados só aparecem aqui) + o que a própria página declara
  const urls = [...(performance.getEntriesByType ? performance.getEntriesByType('resource').map((r) => r.name) : []),
    ...$$('script[src], link[rel="stylesheet"][href]').map((el) => el.src || el.href)];
  const caminhos = urls.map((n) => { try { return new URL(n, location.href); } catch (_) { return null; } })
    .filter((u) => u && u.origin === location.origin && /^\/(js\/hub\/|css\/|dados\/)/.test(u.pathname)).map((u) => u.pathname);
  return [...new Set([...Object.keys(versao || {}), ...caminhos])];
}
async function assinaturas(caminhos) {
  const out = {};
  await Promise.all(caminhos.map(async (c) => {
    try {
      const r = await fetch(c, { method: 'HEAD', cache: 'no-store' });
      if (r.ok) out[c] = r.headers.get('etag') || r.headers.get('last-modified') || '';
    } catch (_) { /* sem rede: fica para a próxima */ }
  }));
  return out;
}
async function guardarVersao() {
  versao = await assinaturas(ficheirosDoHub());
  versaoVista = Date.now();
}
async function verificarVersao() {
  if (!versao || versaoAvisada || document.hidden || Date.now() - versaoVista < VERSAO_CADA) return;
  versaoVista = Date.now();
  const agora = await assinaturas(ficheirosDoHub());
  const mudou = Object.keys(agora).some((c) => versao[c] && agora[c] && agora[c] !== versao[c]);
  Object.keys(agora).forEach((c) => { if (!versao[c]) versao[c] = agora[c]; });   // carregados depois (outra página)
  if (!mudou || versaoAvisada) return;
  versaoAvisada = true;
  aviso('Há uma versão nova do hub. Recarrega a página para a veres.', { icone: 'info', duracao: 0,
    acoes: [{ rotulo: 'Recarregar', fazer: () => location.reload() }] });
}

// ---------------------------------------------------------------- navegação e rotas
function rota() {
  const h = location.hash.replace(/^#\/?/, '');
  const [a, b, c] = h.split('/');
  if (a === 'projeto') return { nome: 'projeto', p: D.projetoPorSlug(b), alvo: c };
  if (['pessoal', 'definicoes', 'novidades'].includes(a)) return { nome: a };
  if (a === 'social') return { nome: 'social', sub: b === 'obras' ? 'obras' : 'planeamento', alvo: b === 'obras' ? c : b };
  if (a === 'materiais') return { nome: 'materiais', alvo: b };
  return { nome: 'inicio' };
}
function desenharNav() {
  const r = rota();
  $('#nav').innerHTML = `<a href="#/"${r.nome === 'inicio' ? ' aria-current="page"' : ''}>Início</a>` +
    E.projetos.map((p) => `<a href="#/projeto/${p.slug}"${r.nome === 'projeto' && r.p === p ? ' aria-current="page"' : ''}>${esc(p.nome)}</a>`).join('') +
    `<a class="nav-separada" href="#/materiais"${r.nome === 'materiais' ? ' aria-current="page"' : ''}>Materiais</a>` +
    `<a class="nav-separada" href="#/social"${r.nome === 'social' ? ' aria-current="page"' : ''}>Redes sociais</a>`;
  const atual = $('#nav [aria-current]');
  if (atual) atual.scrollIntoView({ block: 'nearest', inline: 'nearest' });
}
function desenhar(mudouRota) {
  const r = rota(), v = $('#vista');
  const aviso_ = E.erro ? `<div class="nota" style="margin-bottom:32px;border-color:var(--erro)">${ic('atencao')}<p><b>Os checkpoints, tarefas e decisões ainda não estão disponíveis.</b> A base de dados do hub precisa das migrações 0004 e 0005. <span class="fraco">(${esc(E.erro)})</span></p></div>` : '';
  let html;
  if (r.nome === 'projeto' && r.p) { html = V.paginaProjeto(r.p, V.abaDe(r.p, r.alvo)); document.title = `${r.p.nome} · Discovercasa Design`; }
  else if (r.nome === 'pessoal') { html = V.pessoal(); document.title = 'Área pessoal · Discovercasa Design'; }
  else if (r.nome === 'definicoes') { html = V.definicoes(!!pedidoInstalar); document.title = 'Definições · Discovercasa Design'; }
  else if (r.nome === 'social') { html = SO.pagina(r.sub); document.title = 'Redes sociais · Discovercasa Design'; }
  else if (r.nome === 'materiais') { html = MV.pagina(); document.title = 'Materiais · Discovercasa Design'; }
  else if (r.nome === 'novidades') { html = V.novidades(novidades); document.title = 'Novidades · Discovercasa Design'; marcarNovidadesVistas(); }
  else { html = V.inicio(); document.title = 'Início · Discovercasa Design'; }
  // materials from the Hub (migration 0016): read once, when the Materiais tab or a project that uses them is opened
  if (MV.precisa() && (r.nome === 'materiais' || (r.nome === 'projeto' && r.p && r.p.materiais))) MV.garantir().then(() => desenhar(false));
  const y = window.scrollY;
  v.innerHTML = aviso_ + html;
  encherBarras(v);
  SO.depoisDeDesenhar(v);
  hidratar(v);
  const calc = $('form[data-form="calculadora"]', v);
  if (calc) V.calcular(calc, r.p.cambio.usd_eur);
  prepararAR(v);
  if (mudouRota) {
    window.scrollTo(0, 0);
    entrar($$('.projeto-linha, .passo, .cabeca-pagina, .projeto-cabeca, .cta-app, .bloco-lateral, .novidade, .cartoes-pessoal > *, .social-barra, .mes, .obra, .visita', v));
    if (r.alvo) irPara(r.alvo);
  } else window.scrollTo(0, y);
}
function irPara(alvo) {
  if (/^(post|obra)-\d+$/.test(alvo || '')) return SO.irPara(alvo);
  if (/^m-[0-9a-f-]+$/.test(alvo || '')) {   // a material of the Materiais tab: open it
    const el = document.getElementById(alvo);
    if (!el) return;
    el.querySelector('details').open = true;
    el.scrollIntoView({ block: 'center', behavior: mov() ? 'smooth' : 'auto' });
    return;
  }
  const m = /^(t|cp|doc)-(\d+)$/.exec(alvo || '');
  if (!m) return;
  const id = Number(m[2]);
  if (m[1] === 'doc') { const g = document.getElementById(alvo); const det = g && g.closest('details'); if (det) det.open = true; }
  const cpId = m[1] === 't' ? (E.tarefas.find((t) => t.id === id) || {}).checkpoint_id : m[1] === 'cp' ? id : null;
  if (m[1] === 't' && (E.tarefas.find((t) => t.id === id) || {}).revisao && !V.notasAbertas.has(id)) { V.notasAbertas.add(id); desenhar(false); }
  if (cpId && !V.abertos.has(cpId)) { V.abertos.add(cpId); desenhar(false); }
  const el = document.getElementById(alvo);
  if (!el) return;
  el.scrollIntoView({ block: 'center', behavior: mov() ? 'smooth' : 'auto' });
  el.classList.remove('alvo'); void el.offsetWidth; el.classList.add('alvo');
}
const chaveDe = (r) => r.nome + (r.p ? r.p.id + ':' + V.abaDe(r.p, r.alvo) : '') + (r.sub || '');
window.addEventListener('hashchange', () => {
  if (!E.eu.id) return;
  const r = rota();
  const chaveRota = chaveDe(r);
  fecharPops();
  desenharNav();
  if (chaveRota === rotaAnterior && r.alvo) return irPara(r.alvo);
  const outraAba = r.nome === 'projeto' && r.p && rotaAnterior.startsWith('projeto' + r.p.id + ':');
  if (r.nome === 'projeto' && chaveRota !== rotaAnterior) V.fecharTudo();   // «sempre que abrimos um separador do projeto … tudo collapsed»
  rotaAnterior = chaveRota;
  if (outraAba) {   // the same project, another tab: the tab bar stays where it was
    const barra = $('#sub-abas'), topo = barra ? barra.getBoundingClientRect().top + window.scrollY - 72 : 0;
    desenhar(false);
    if (window.scrollY > topo) window.scrollTo(0, topo);
    if (r.alvo) irPara(r.alvo);
  } else desenhar(true);
  refrescarAoMudar();
});
// os dados de novo a cada mudança de página; só redesenha se algo mudou (sem interromper a entrada da página)
const assinatura = () => JSON.stringify([E.checkpoints, E.tarefas, E.decisoes, E.documentos, E.posts, E.fases, E.obras, E.notas, E.anexos].map((l) => l.length))
  + JSON.stringify([E.tarefas, E.checkpoints, E.posts, E.fases, E.notas].map((l) => l.map((x) => x.estado ?? x.resolvida).join()));
async function refrescarAoMudar() {
  if (E.erro) return;
  const antes = assinatura();
  try { await D.carregarTudo(); await D.carregarNotificacoes(); } catch (_) { return; }
  atualizarContador();
  if (assinatura() !== antes && !dlg.open && !document.activeElement.matches('input, textarea, select')) desenhar(false);
}
rotaAnterior = chaveDe(rota());
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
  if (e.target.closest('[data-ar][aria-disabled]')) {   // AR link still being prepared (signed URL)
    e.preventDefault();
    aviso('A preparar o link do modelo AR… tenta outra vez dentro de um segundo.', { icone: 'info', duracao: 3 });
    return;
  }
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
  verificarVersao();
  if (E.erro || document.hidden) return;
  try {
    const novas = await D.carregarNotificacoes();
    await D.carregarTudo();
    FI.aoMudar();
    novas.slice(0, 3).forEach((n) => aviso(esc(n.texto), { icone: 'sino', acoes: [{ rotulo: 'Ver', fazer: () => irNotif(n.projeto, n.ref_tipo, n.ref_id) }] }));
    atualizarContador();
    if (!dlg.open && !gaveta.open && !document.activeElement.matches('input, textarea, select')) desenhar(false);
    mostrarNovos();
  } catch (_) { /* sem rede: tenta no próximo minuto */ }
}
// em direto: uma mudança feita por qualquer pessoa (ou noutra janela) atualiza já todos os sítios onde aparece
let emDiretoEspera = null, mudouNotificacoes = false, mudouRegisto = false;
function emDireto(tabela) {
  if (tabela === 'notificacoes' || tabela === 'notificacoes_lidas') mudouNotificacoes = true;
  if (tabela === 'registo') mudouRegisto = true;
  clearTimeout(emDiretoEspera);
  emDiretoEspera = setTimeout(async () => {
    try {
      const novas = mudouNotificacoes ? await D.carregarNotificacoes() : [];
      mudouNotificacoes = false;
      await D.carregarTudo();
      FI.aoMudar();
      EQ.redesenharProjeto();
      if (mudouRegisto) { mudouRegisto = false; avisosDoLog(true); }
      novas.slice(0, 3).forEach((n) => aviso(esc(n.texto), { icone: 'sino', acoes: [{ rotulo: 'Ver', fazer: () => { marcarNotif(n.id, true); irNotif(n.projeto, n.ref_tipo, n.ref_id); } }] }));
      atualizarContador();
      const pop = $('#pop-notificacoes');
      if (!pop.hidden && !pop.querySelector('[data-espera]')) redesenharPop(pop);   // outra janela viu uma
      if (!dlg.open && !document.activeElement.matches('input, textarea, select')) desenhar(false);
      SO.aoMudar();
      refrescarAnexosDlg();
      mostrarNovos();
    } catch (_) { /* tenta na próxima mudança ou no relógio */ }
  }, 350);
}

// a lista de notificações desenhada outra vez no mesmo sítio: só quando mudou alguma coisa e sem perder a posição.
// Ver uma com o rato volta pela ligação em direto; redesenhar a lista do início não deixava ler a notificação
// (utilizador, 2026-11-09).
const chavePop = () => E.notificacoes.map((n) => `${n.id}${D.ehPorVer(n) ? '*' : ''}${E.lidas.has(n.id) ? 'v' : ''}`).join(',');
function redesenharPop(pop) {
  const k = chavePop();
  if (pop.dataset.chave === k) return;
  const corpo = pop.querySelector('.pop-corpo'), y = corpo ? corpo.scrollTop : 0;
  pop.innerHTML = P.htmlNotificacoes();
  pop.dataset.chave = k;
  const novo = pop.querySelector('.pop-corpo');
  if (novo) novo.scrollTop = y;
}
// notificação vista (ou de novo por ver): a linha e o contador mudam já; a base de dados guarda-o
async function marcarNotif(id, lida) {
  if (!id) return;
  try { await D.marcarLida(id, lida); } catch (_) { /* fica como estava */ }
  const linha = document.querySelector(`#pop-notificacoes .notif[data-notif="${id}"]`), n = E.notificacoes.find((x) => x.id === id);
  if (linha && n) linha.outerHTML = P.linhaNotif(n);
  const resumo = $('#pop-notificacoes [data-por-ver]'), k = D.naoLidas().length;
  if (resumo) resumo.textContent = k ? `${k} por ver` : 'Tudo visto';
  if (linha) $('#pop-notificacoes').dataset.chave = chavePop();  // a lista já mostra este estado
  atualizarContador();
}
// com o rato: vista depois de 0,6 s por cima (no telemóvel não há hover: abre-se ou toca-se no ponto)
document.addEventListener('pointerover', (e) => {
  if (e.pointerType !== 'mouse') return;
  const linha = e.target.closest && e.target.closest('#pop-notificacoes .notif.nao-lida');
  if (!linha || linha.dataset.espera) return;
  linha.dataset.espera = '1';
  const id = Number(linha.dataset.notif);
  const t = setTimeout(() => { if (linha.isConnected && linha.matches(':hover')) marcarNotif(id, true); else delete linha.dataset.espera; }, 600);
  linha.addEventListener('pointerleave', () => { clearTimeout(t); delete linha.dataset.espera; }, { once: true });
});

// o que outra pessoa acrescentou e eu ainda não vi: fica com a etiqueta «Novo» nesta visita (os avisos de lado vêm do Log)
function mostrarNovos() {
  const itens = D.porVer();
  if (!itens.length) return;
  itens.forEach((i) => E.novos.add(D.chave(i.tipo, i.x.id)));
  D.marcarVistos(itens).catch(() => {});
  desenhar(false);
}
// o Log: ao abrir o hub, um aviso de lado com o que mudou desde a última visita (utilizador, 2026-11-11: «eu recebo
// notificações das alterações do log … em pop-up de lado sempre que abro o hub»); ao vivo, o que não vem já como notificação
async function avisosDoLog(aoVivo = false) {
  try { await D.carregarRegisto(aoVivo ? 60 : 300); } catch (_) { return; }
  const novos = D.registoNovo();
  if (!novos.length) return;
  if (!E.perfil || E.perfil.avisos_registo !== false) EQ.avisosLog(novos, { aviso, aoVivo, ir: irNotif, verLog: abrirLog });
  D.registoVisto().catch(() => {});
  if (gaveta.open && sug.sep === 'log') redesenharGaveta();
}
// as tarefas em que fui marcado e ainda não vi: um pop-up que leva ao ecrã de cada uma
function mostrarMarcacoes() {
  const html = EQ.htmlMarcacoes();
  if (!html || (dlg.open && !dlg.querySelector('[data-marcacoes]'))) return;
  abrirDialogo(dlg, html, { estreito: true });
}
function irNotif(projetoId, tipo, id) {
  // sugestões (migração 0021): a checklist das sugestões; chat: a conversa (ou a lista)
  if (tipo === 'sugestao') { sug.sep = 'checklist'; abrirDialogo(gaveta, htmlGaveta()); carregarSugestoes(); return; }
  if (tipo === 'tarefa' || tipo === 'checkpoint') { FI.abrir(tipo, Number(id)); return; }
  if (tipo === 'critica') { EQ.abrirProjeto(projetoId, { criticas: true }); return; }
  if (tipo === 'conversa') return;   // o chat geral de 11/11 já não existe
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
  // encostada ao botão, mas sempre dentro do ecrã (no telemóvel o botão está perto da margem e a lista é larga)
  const largura = Math.min(380, window.innerWidth - 32);
  let direita = Math.max(16, window.innerWidth - r.right);
  if (window.innerWidth - direita - largura < 16) direita = 16;
  pop.style.right = `${direita}px`;
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
$('#b-notificacoes').addEventListener('click', (e) => {
  e.stopPropagation();
  abrirPop(e.currentTarget, $('#pop-notificacoes'), P.htmlNotificacoes());
  $('#pop-notificacoes').dataset.chave = chavePop();
});
$('#b-perfil').addEventListener('click', (e) => { e.stopPropagation(); abrirPop(e.currentTarget, $('#pop-perfil'), P.htmlPerfil(novidadeNova())); });
// críticas e comentários: em todas as abas (utilizador, 2026-11-11: «sim põe em todas as abas»), já com o projeto da aba
$('#b-critica').addEventListener('click', () => { fecharPops(); abrirDialogo(dlg, EQ.dlgCritica((rota().p || {}).id || null)); });
$('#b-sugestoes').addEventListener('click', () => { if (sug.sep === 'log') sug.sep = 'sugestoes'; abrirDialogo(gaveta, htmlGaveta()); carregarSugestoes(); });
document.addEventListener('click', (e) => { if (!e.target.closest('.pop')) fecharPops(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') fecharPops(); });
[dlg, gaveta, ficha, projetoPop].forEach((d) => {
  // clique fora: only when the press also started outside (team note 2026-11-10: turning the 3D model and letting go
  // past the dialog's edge counted as a click outside, closed the dialog and the drag went to the page behind)
  let baixo = null;
  d.addEventListener('pointerdown', (e) => { baixo = e.target; });
  d.addEventListener('click', (e) => { if (e.target === d && baixo === d) fecharDialogo(d); baixo = null; });
  d.addEventListener('cancel', (e) => { e.preventDefault(); fecharDialogo(d); });
});

// ---------------------------------------------------------------- sugestões
async function carregarSugestoes() {
  const { data, error } = await sb.from('sugestoes')
    .select('id, texto, ferramenta, estado, autor_id, autor_nome, criada_em, na_checklist, checklist_em, sugestoes_comentarios (id, texto, autor_id, autor_nome, criado_em)')
    .order('criada_em', { ascending: false }).limit(200);
  sug.erro = error ? error.message : '';
  if (!error) { data.forEach((g) => (g.sugestoes_comentarios || []).sort((a, b) => new Date(a.criado_em) - new Date(b.criado_em))); sug.lista = data; }
  redesenharGaveta();
}
async function mudarSugestao(id, campos) {
  const { error } = await sb.from('sugestoes').update(campos).eq('id', id);
  if (error) aviso('Não foi possível mudar a sugestão: ' + esc(error.message), { icone: 'atencao' });
  carregarSugestoes();
}

// ---------------------------------------------------------------- trabalho em equipa
// Início: cada projeto abre o seu pop-up (tarefas em curso e o que precisa de atenção); Ctrl/⌘ + clique abre a página
document.addEventListener('click', (e) => {
  const linha = e.target.closest('a.projeto-linha[data-projeto]');
  if (!linha || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
  e.preventDefault();
  EQ.abrirProjeto(linha.dataset.projeto);
});
// as descrições das tarefas (acordeão) ficam abertas enquanto se está no projeto
document.addEventListener('toggle', (e) => {
  const d = e.target;
  if (!d.matches || !d.matches('details[data-desc]')) return;
  const id = Number(d.dataset.desc);
  if (d.open) { V.descricoesAbertas.add(id); hidratar(d); } else V.descricoesAbertas.delete(id);
}, true);
FI.ligar({
  depois: async () => { await depois(); EQ.redesenharProjeto(); },
  aoFechar: () => {   // voltar ao pop-up das marcações (sem as já vistas) e ao pop-up do projeto
    if (dlg.open && dlg.querySelector('[data-marcacoes]')) { const h = EQ.htmlMarcacoes(); if (h) dlg.innerHTML = h; else fecharDialogo(dlg); }
    EQ.redesenharProjeto();
  },
});
async function acaoCritica(el) {
  const c = E.criticas.find((x) => x.id === Number(el.dataset.id));
  if (!c) return;
  if (el.dataset.acao === 'critica-estado') { if (await tentar(() => D.mudarCritica(c.id, { estado: el.dataset.valor }))) { depois(); EQ.redesenharProjeto(); } return; }
  if (el.dataset.acao === 'critica-apagar') {
    if (!confirm('Apagar esta crítica?')) return;
    if (await tentar(() => D.apagarCritica(c))) { import('./conversa.js').then((m) => m.apagarFicheiros(c.anexos)); depois(); EQ.redesenharProjeto(); }
    return;
  }
  if (el.dataset.acao === 'critica-tarefa') {
    let t = null;
    if (await tentar(async () => { t = await D.criticaATarefa(c); })) {
      aviso(`Tarefa criada: «${esc(t.titulo)}».`, { icone: 'certo', duracao: 5, acoes: [{ rotulo: 'Ver', fazer: () => FI.abrir('tarefa', t.id) }] });
      depois(); EQ.redesenharProjeto();
    }
  }
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
// Step Inside: fill the AR buttons with signed links (an hour) — the tap must open the viewer straight away
// (Safari only starts AR Quick Look from a real link tap, so the link cannot be fetched after the tap)
const LINKS_AR = new Map();   // doc id -> { url, ate }
// The models at 1:1 keep their real size: Quick Look without pinch-to-scale (#allowsContentScaling=0), Scene Viewer
// with resizable=false. The links are prepared all at once (they were one after the other: slow on a phone).
async function prepararAR(raiz) {
  await Promise.all($$('[data-ar]', raiz).map(async (a) => {
    const id = Number(a.dataset.ar);
    const d = E.documentos.find((x) => x.id === id);
    if (!d) return;
    try {
      let l = LINKS_AR.get(id);
      if (!l || l.ate < Date.now() + 5 * 60 * 1000) { l = { url: await D.urlAR(d), ate: Date.now() + 60 * 60 * 1000 }; LINKS_AR.set(id, l); }
      const real = /1:1/.test(d.titulo);
      if (a.dataset.arTipo === 'ios') a.href = l.url + (real ? '#allowsContentScaling=0' : '');
      else if (a.dataset.arTipo === 'teste') a.href = AA.paginaTeste(l.url, d);   // the Android AR test page (outside the hub)
      else {   // Scene Viewer: the link as Google's <model-viewer> builds it (1.2)
        a.href = AA.intentSceneViewer(l.url, { titulo: d.titulo.replace(/\s+/g, ' '), real, volta: AA.voltaPara(id, (rota().p || {}).slug) });
      }
      a.removeAttribute('aria-disabled');
    } catch (err) { a.title = 'Não foi possível preparar o link: ' + (err.message || err); }
  }));
  // Android: what this phone can do, on screen (team note 10: the AR bounced back even from «Ver no teu espaço»)
  const linha = $('#ar-este-telemovel', raiz);
  if (linha) AA.esteTelemovel().then((i) => { if (i && linha.isConnected) { linha.textContent = AA.textoTelemovel(i); linha.classList.toggle('mau', !i.webxr); linha.hidden = false; } });
}

// Step Inside: the 3D viewer for who has no AR — Google's <model-viewer> (a new dependency, authorised 2026-11-09),
// loaded only the first time a model is opened
const MODEL_VIEWER = 'https://cdn.jsdelivr.net/npm/@google/model-viewer@4.0.0/dist/model-viewer.min.js';
let modelViewer = null;
function carregarModelViewer() {
  if (customElements.get('model-viewer')) return Promise.resolve();
  return modelViewer || (modelViewer = new Promise((ok, falha) => {
    const s = document.createElement('script');
    s.type = 'module';
    s.src = MODEL_VIEWER;
    s.onload = () => customElements.whenDefined('model-viewer').then(ok);
    s.onerror = () => { modelViewer = null; falha(new Error('o visualizador não carregou (sem rede?)')); };
    document.head.append(s);
  }));
}
// «Ver em AR · Android» (2026-11-11): the Google app closes Scene Viewer ~90 ms after launch since its October update
// (https://github.com/google-ar/arcore-android-sdk/issues/1795, the team's Pixel 6 and Xiaomi too), while Chrome's own AR
// (WebXR) opened our model on the Pixel 6. So the button opens the viewer and goes straight into Chrome's AR: on its own
// while the tap still counts (Chrome allows about 5 s), otherwise with a tap on «Ver no teu espaço». Without ARCore
// (a phone not on Google's list) the AR fails and the model stays in 3D with the notice.
function entrarEmAR(mv, id, toque) {
  if (!mv) return;
  let auto = false;
  mv.addEventListener('ar-status', (e) => {
    if (e.detail.status !== 'failed') return;
    if (auto) { auto = false; aviso('Toca em «Ver no teu espaço (AR)» para abrir o AR.', { icone: 'info', duracao: 5 }); }
    else arAndroidNaoAbriu(id, { jaAberto: true });
  });
  mv.addEventListener('load', async () => {
    for (let i = 0; i < 15 && !mv.canActivateAR; i++) await new Promise((r) => setTimeout(r, 100));   // decided asynchronously
    if (!mv.canActivateAR) return arAndroidNaoAbriu(id, { jaAberto: true });
    if (Date.now() - toque < 4500) { auto = true; try { await mv.activateAR(); } catch (_) {} }
    else aviso('Modelo pronto: toca em «Ver no teu espaço (AR)».', { icone: 'info', duracao: 5 });
  }, { once: true });
}

async function verEm3D(id, { ar = false, toque = 0 } = {}) {
  const d = E.documentos.find((x) => x.id === id);
  if (!d) return;
  const ios = E.documentos.find((x) => x.tipo === 'ar' && x.projeto === d.projeto && x.titulo === d.titulo && /\.usdz$/i.test(x.nome_ficheiro));
  abrirDialogo(dlg, P.htmlVisor3D(d));
  try {
    const [url, urlIos] = await Promise.all([D.urlAR(d), ios ? D.urlAR(ios) : null, carregarModelViewer()]);
    if (dlg.open && dlg.querySelector('[data-a-carregar]')) {
      dlg.innerHTML = P.htmlVisor3D(d, url, urlIos);
      if (ar) entrarEmAR(dlg.querySelector('model-viewer'), id, toque);
    }
  } catch (err) {
    if (dlg.open) dlg.innerHTML = P.htmlVisor3D(d, null, null, err.message || String(err));
  }
}

async function depois() { try { await D.carregarNotificacoes(); } catch (_) {} atualizarContador(); desenhar(false); }

// Materiais tab: search and filters redraw only the list (the search box keeps its focus)
function filtrarMateriais(e) {
  const el = e.target.closest('[data-mat]');
  if (!el || !$('#mat-lista')) return;
  MV.filtro[el.dataset.mat] = el.value;
  MV.filtro.limite = 200;
  $('#mat-lista').innerHTML = MV.lista();
}
document.addEventListener('input', filtrarMateriais);
document.addEventListener('change', filtrarMateriais);

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
    case 'abrir-ficha': return FI.abrir(el.dataset.alvo, id);
    case 'pp-ir': fecharDialogo(projetoPop); return;   // o link segue para a página do projeto
    case 'nova-critica': return abrirDialogo(dlg, EQ.dlgCritica(el.dataset.projeto));
    case 'tipo-critica': {
      const f = el.closest('form'); f.elements.tipo.value = el.dataset.valor;
      $$('[data-acao="tipo-critica"]', f).forEach((b) => b.setAttribute('aria-pressed', b === el));
      return;
    }
    case 'critica-tirar': return EQ.tirarCritica(Number(el.dataset.i), el.closest('form'));
    case 'critica-estado': case 'critica-apagar': case 'critica-tarefa': return acaoCritica(el);
    case 'criticas-todas': return EQ.abrirProjeto(el.dataset.projeto, { criticas: true });
    case 'conv-imagem': case 'conv-ficheiro':   // anexos das críticas (os da conversa trata o ecrã da tarefa)
      if (el.closest('#ficha')) return;
      try { await import('./conversa.js').then((m) => m.cliqueAnexo(el, EQ.anexosCritica)); } catch (err) { aviso('Não foi possível abrir: ' + esc(err.message || err), { icone: 'atencao' }); }
      return;
    case 'marcacoes-vistas': await D.marcacoesVistas(D.marcacoesPorVer().map((m) => m.tarefa_id)); fecharDialogo(dlg); return;
    case 'log-ver': { const ir = () => irNotif(el.dataset.projeto, el.dataset.ref, el.dataset.id); if (['tarefa', 'checkpoint', 'critica', 'decisao'].includes(el.dataset.ref)) return ir(); fecharDialogo(gaveta); return ir(); }
    case 'avisos-registo': {
      const ligados = el.dataset.valor === '1';
      if (await tentar(() => D.mudarAvisosRegisto(ligados))) aviso(ligados ? 'Vais receber os avisos do Log ao abrir o hub.' : 'Avisos do Log desligados.', { icone: 'certo', duracao: 3 });
      return desenhar(false);
    }
    case 'acrescentar': return abrirDialogo(dlg, P.dlgAcrescentar(el.dataset.projeto || (rota().p || {}).id, null, el.dataset.tipo));
    case 'acrescentar-doc': return abrirDialogo(dlg, P.dlgDocumento(el.dataset.projeto, el.dataset.tipoDoc), { estreito: true });
    case 'tipo-doc': {
      const f = el.closest('form'); f.elements.tipo.value = el.dataset.valor;
      $$('[data-acao="tipo-doc"]', f).forEach((b) => b.setAttribute('aria-pressed', b === el));
      return;
    }
    case 'ver-3d': return verEm3D(id);
    case 'ar-android': return verEm3D(id, { ar: true, toque: Date.now() });
    case 'mat-csv': return MV.descarregarCSV();
    case 'mat-mais': MV.filtro.limite += 200; $('#mat-lista').innerHTML = MV.lista(); return;
    case 'abrir-doc': {
      const d = E.documentos.find((x) => x.id === id);
      const janela = window.open('about:blank', '_blank');  // já, para o browser não bloquear a janela
      try { const url = await D.urlDocumento(d); if (janela) janela.location.href = url; else location.href = url; }
      catch (err) { if (janela) janela.close(); aviso('Não foi possível abrir o documento: ' + esc(err.message || err), { icone: 'atencao' }); }
      return;
    }
    case 'nova-seccao': return abrirDialogo(dlg, P.dlgSeccao(el.dataset.projeto, el.dataset.tipoDoc), { estreito: true });
    case 'sec-renomear': {
      const s = E.seccoes.find((x) => x.id === Number(el.dataset.seccao));
      return s && abrirDialogo(dlg, P.dlgSeccao(s.projeto, s.tipo, s), { estreito: true });
    }
    case 'sec-apagar': {
      const s = E.seccoes.find((x) => x.id === Number(el.dataset.seccao));
      if (!s) return;
      const n = E.documentos.filter((d) => d.seccao_id === s.id).length;
      if (n) return aviso(`Para apagar a secção «${esc(s.nome)}», muda de secção ou apaga primeiro os seus ${n} ${n === 1 ? 'documento' : 'documentos'}.`, { icone: 'atencao' });
      if (!confirm(`Apagar a secção «${s.nome}»?`)) return;
      if (await tentar(() => D.apagarSeccao(s.id))) depois();
      return;
    }
    case 'sec-ficheiros': case 'sec-pasta': {
      const s = E.seccoes.find((x) => x.id === Number(el.dataset.seccao));
      if (!s) return;
      alvoCarga = { projeto: s.projeto, tipo: s.tipo, seccao: s.id };
      const entrada = $(`#documentos input[data-entrada="${el.dataset.acao === 'sec-pasta' ? 'pasta' : 'ficheiros'}"]`);
      if (entrada) entrada.click();
      return;
    }
    case 'mover-doc': {
      const d = E.documentos.find((x) => x.id === id);
      return d && abrirDialogo(dlg, P.dlgMover(d), { estreito: true });
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
    case 'editar-tarefa': abrirDialogo(dlg, P.dlgEditarTarefa(E.tarefas.find((t) => t.id === id))); return hidratar(dlg);
    case 'editar-cp': abrirDialogo(dlg, P.dlgEditarCheckpoint(E.checkpoints.find((c) => c.id === id)), { estreito: true }); return hidratar(dlg);
    // notas de teste/revisão
    case 'alternar-notas': {
      const corpo = document.getElementById('notas-corpo-' + id), abrir = corpo.hidden;
      if (abrir) V.notasAbertas.add(id); else V.notasAbertas.delete(id);
      corpo.hidden = !abrir; el.setAttribute('aria-expanded', abrir);
      if (abrir) { hidratar(corpo); if (mov()) gsap.from(corpo, { autoAlpha: 0, y: -4, duration: 0.2, ease: 'expo.out', clearProps: 'all' }); }
      return;
    }
    case 'tipo-nota': {
      const f = el.closest('form'); f.elements.tipo.value = el.dataset.valor;
      $$('[data-acao="tipo-nota"]', f).forEach((b) => b.setAttribute('aria-pressed', b === el));
      return;
    }
    case 'apagar-nota': {
      const n = E.notas.find((x) => x.id === id);
      if (!confirm('Apagar esta nota?')) return;
      if (await tentar(() => D.apagarNota(n))) depois();
      return;
    }
    case 'passar-nota': {
      const n = E.notas.find((x) => x.id === id);
      let nova = null;
      if (await tentar(async () => { nova = await D.passarNotaATarefa(n); })) {
        aviso(`Tarefa criada: «${esc(nova.titulo)}».`, { icone: 'certo', duracao: 5, acoes: [{ rotulo: 'Ver', fazer: () => irNotif(nova.projeto, 'tarefa', nova.id) }] });
        depois();
      }
      return;
    }
    // imagens anexadas
    case 'ver-anexo': return abrirVisor(D.visorDe(D.anexosDe(el.dataset.alvo, Number(el.dataset.ref))), Number(el.dataset.i));
    case 'apagar-anexo': {
      const a = E.anexos.find((x) => x.id === id);
      if (!confirm(`Tirar a imagem «${a.nome_ficheiro}»?`)) return;
      if (await tentar(() => D.apagarAnexo(a))) { refrescarAnexosDlg(); depois(); }
      return;
    }
    // decisões: uma opção que não estava na lista
    case 'mostrar-outra-opcao': {
      const caixa = document.getElementById(el.getAttribute('aria-controls')), abrir = caixa.hidden;
      caixa.hidden = !abrir; el.setAttribute('aria-expanded', abrir);
      if (abrir) caixa.querySelector('input').focus();
      return;
    }
    case 'acrescentar-opcao': {
      const f = el.closest('form'), v = (n) => f.elements[n].value.trim();
      if (v('n_titulo').length < 1) { $('.erro-msg', f).textContent = 'Escreve o nome da opção.'; f.elements.n_titulo.focus(); return; }
      const o = { titulo: v('n_titulo'), descricao: v('n_descricao'), vantagens: v('n_vantagens'), desvantagens: v('n_desvantagens'), custo: v('n_custo') };
      if (await tentar(() => D.acrescentarOpcao(id, o), f)) {
        const d = E.decisoes.find((x) => x.id === id);
        abrirDialogo(dlg, P.dlgDecisao(d));
        const nova = (d.decisoes_opcoes || []).find((x) => x.titulo === o.titulo);
        const r = nova && dlg.querySelector(`input[name=opcao][value="${nova.id}"]`);
        if (r) r.checked = true;
        aviso('Opção acrescentada. A equipa foi avisada.', { icone: 'certo', duracao: 3 });
        depois();
      }
      return;
    }
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
    case 'ler-todas': await D.marcarNotificacoesLidas(); atualizarContador(); redesenharPop($('#pop-notificacoes')); return;
    case 'ir-notif': fecharPops(); marcarNotif(Number(el.dataset.notif), true); return irNotif(el.dataset.projeto, el.dataset.ref, el.dataset.id);
    case 'alternar-lida': return marcarNotif(id, !E.lidas.has(id) && D.ehPorVer(E.notificacoes.find((n) => n.id === id)));
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
    case 'sug-sep': if (el.dataset.valor === 'log') return abrirLog(); sug.sep = el.dataset.valor; gaveta.innerHTML = htmlGaveta(); return;
    case 'sug-comentarios': if (sug.abertas.has(id)) sug.abertas.delete(id); else sug.abertas.add(id); gaveta.innerHTML = htmlGaveta(); return;
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
    case 'resolver-nota':
      if (await tentar(() => D.mudarNota(id, { resolvida: el.checked }))) { if (el.checked) aviso('Marcada como resolvida.', { icone: 'certo', duracao: 3 }); depois(); }
      else el.checked = !el.checked;
      return;
    case 'estado-cp': if (await tentar(() => D.mudarCheckpoint(id, { estado: el.value }))) depois(); return;
    case 'projeto-novo': { const f = el.closest('form'); f.elements.checkpoint.innerHTML = P.opcoesCheckpoints(el.value); f.elements.posicao.innerHTML = P.opcoesPosicao(el.value); return; }
    case undefined:
      if ((el.name === 'ficheiros' || el.name === 'pasta') && el.closest('form')) {
        const f = el.closest('form'), lista = f.querySelector('[data-escolhidos]');
        const fs = [...(f.elements.ficheiros ? f.elements.ficheiros.files : [])];
        const ps = [...(f.elements.pasta ? f.elements.pasta.files : [])].filter((x) => !IGNORAR.test(x.name));
        const raiz = ps.length ? (ps[0].webkitRelativePath || '').split('/')[0] : '';
        lista.innerHTML = fs.map((x) => `<li>${esc(x.name)} · ${(x.size / 1e6).toLocaleString('pt-PT', { maximumFractionDigits: 1 })} MB</li>`).join('')
          + (ps.length ? `<li>${ic('pasta', 'ic-sm')}Pasta «${esc(raiz)}»: ${ps.length} ${ps.length === 1 ? 'ficheiro' : 'ficheiros'}</li>` : '');
      }
      if (el.dataset.entrada) {   // the hidden inputs of a section's «Ficheiros» / «Pasta» buttons
        const itens = [...el.files].map((x) => ({ ficheiro: x, pasta: el.dataset.entrada === 'pasta' ? pastaDe(x.webkitRelativePath) : '' }));
        el.value = '';
        if (alvoCarga && itens.length) await carregarVarios(alvoCarga.projeto, alvoCarga.tipo, alvoCarga.seccao, itens);
        return;
      }
      if (el.name === 'anexos-ficheiros') { await enviarAnexos(el.dataset.alvo, Number(el.dataset.ref), el.files); el.value = ''; }
      if (el.name === 'imagens-nota') { juntarImagensNota(Number(el.dataset.tarefa), el.files); el.value = ''; }
      if (el.name === 'critica-ficheiros') { EQ.juntarCritica(el.files, el.closest('form')); el.value = ''; }
      if (el.dataset.log) { EQ.filtroLog[el.dataset.log] = el.type === 'checkbox' ? el.checked : el.value; redesenharGaveta(); }
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
      case 'nota': {
        const tid = Number(f.dataset.tarefa), imagens = notasPendentes.get(tid) || [];
        if (botao) botao.textContent = imagens.length ? 'A carregar…' : 'Acrescentar nota';
        ok = await tentar(() => D.criarNota(tid, v('tipo'), f.elements.texto.value.trim(), imagens), f);
        if (botao) botao.textContent = 'Acrescentar nota';
        if (ok) {
          notasPendentes.delete(tid);
          await depois();
          const campo = $(`form[data-form="nota"][data-tarefa="${tid}"] textarea`); if (campo) campo.focus();
        }
        return;
      }
      case 'acrescentar': {
        const projetoId = v('projeto');
        if (v('tipo') === 'checkpoint') {
          ok = await tentar(() => D.criarCheckpoint({ projeto: projetoId, titulo: v('titulo'), descricao: v('descricao'), criterio_saida: v('criterio_saida') }, Number(v('posicao')) || null), f);
        } else {
          const cp = Number(v('checkpoint'));
          if (!cp) { $('.erro-msg', f).textContent = 'Este projeto ainda não tem checkpoints: acrescenta primeiro um checkpoint.'; return; }
          ok = await tentar(() => D.criarTarefa({ checkpoint_id: cp, projeto: projetoId, titulo: v('titulo'), descricao: v('descricao'), responsavel_id: v('responsavel') || null,
            app_sugerida: v('app') || null, custo: v('custo'), revisao: f.elements.revisao.checked, ordem: D.tarefasDe(cp).length + 1 }), f);
          if (ok) V.abertos.add(cp);
        }
        if (ok) { fecharDialogo(dlg); aviso('Acrescentado. Quem entrar a seguir vai vê-lo como novo.', { icone: 'certo', duracao: 3 }); depois(); }
        return;
      }
      case 'editar-tarefa':
        ok = await tentar(() => D.mudarTarefa(Number(f.dataset.id), { titulo: v('titulo'), descricao: v('descricao'), checkpoint_id: Number(v('checkpoint')), estado: v('estado'),
          responsavel_id: v('responsavel') || null, app_sugerida: v('app') || null, custo: v('custo'), revisao: f.elements.revisao.checked }), f);
        if (ok) { fecharDialogo(dlg); depois(); }
        return;
      case 'editar-cp':
        ok = await tentar(async () => {
          const id = Number(f.dataset.id), c = E.checkpoints.find((x) => x.id === id);
          const antes = D.checkpointsDe(c.projeto).findIndex((x) => x.id === id) + 1, depoisPos = Number(v('posicao'));
          await D.mudarCheckpoint(id, { titulo: v('titulo'), descricao: v('descricao'), estado: v('estado'), criterio_saida: v('criterio_saida') });
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
      case 'seccao': {
        const s = f.dataset.seccao ? Number(f.dataset.seccao) : null;
        let nova = null;
        ok = await tentar(async () => { if (s) await D.renomearSeccao(s, v('nome')); else nova = await D.criarSeccao(f.dataset.projeto, f.dataset.tipoDoc, v('nome')); }, f);
        if (ok) {
          fecharDialogo(dlg);
          if (nova) { V.seccoesAbertas.add(`sec:${nova.id}`); aviso(`Secção «${esc(nova.nome)}» criada. Acrescenta-lhe ficheiros ou uma pasta.`, { icone: 'certo', duracao: 4 }); }
          depois();
        }
        return;
      }
      case 'mover-doc': {
        const sel = f.elements.seccao.value ? Number(f.elements.seccao.value) : null;
        ok = await tentar(() => D.moverDocumento(Number(f.dataset.id), sel), f);
        if (ok) { fecharDialogo(dlg); if (sel) V.seccoesAbertas.add(`sec:${sel}`); depois(); }
        return;
      }
      case 'documento': {
        if (f.elements.pasta || f.elements.seccao) {   // informative / additional documents: files and folders, into a section
          const fs = [...f.elements.ficheiros.files].map((x) => ({ ficheiro: x, pasta: '' }));
          const ps = [...(f.elements.pasta ? f.elements.pasta.files : [])].map((x) => ({ ficheiro: x, pasta: pastaDe(x.webkitRelativePath) }));
          if (!fs.length && !ps.length) { $('.erro-msg', f).textContent = 'Escolhe ficheiros ou uma pasta.'; return; }
          const opt = f.elements.seccao && f.elements.seccao.selectedOptions[0];
          const seccao = opt && opt.value ? Number(opt.value) : null;
          const tipo = (opt && opt.dataset.tipo) || v('tipo');
          fecharDialogo(dlg);
          await carregarVarios(f.dataset.projeto, tipo, seccao, [...fs, ...ps], { titulo: v('titulo'), descricao: v('descricao') });
          return;
        }
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
      case 'critica': {
        const msg = $('.erro-msg', f);
        if (botao) botao.textContent = 'A enviar…';
        try { await EQ.enviarCritica(f, D.criarCritica); ok = true; } catch (err) { if (msg) msg.textContent = 'Não foi enviada: ' + (err.message || err); }
        if (botao) botao.textContent = 'Enviar';
        if (ok) { fecharDialogo(dlg); aviso('Obrigado! A equipa vê a crítica e quem edita foi avisado.', { icone: 'certo', duracao: 4 }); depois(); EQ.redesenharProjeto(); }
        return;
      }
      case 'comentario': {
        const { error } = await sb.from('sugestoes_comentarios').insert({ sugestao_id: Number(f.dataset.id), texto: v('texto'), autor_nome: E.eu.nome });
        if (error) { aviso('O comentário não foi enviado: ' + esc(error.message), { icone: 'atencao' }); return; }
        return carregarSugestoes();
      }
    }
  } finally { if (botao && botao.isConnected) botao.disabled = false; }
});

// ---------------------------------------------------------------- imagens: tarefas e checkpoints (já existem) e notas (antes de as criar)
async function enviarAnexos(alvo, ref, lista) {
  const imagens = saoImagens(lista);
  if (!imagens.length) return aviso('Só se podem juntar imagens.', { icone: 'atencao' });
  const prog = () => $('.anexos-progresso', dlg);
  let feitas = 0;
  try {
    for (const f of imagens) {
      if (prog()) prog().textContent = `A carregar ${feitas + 1} de ${imagens.length}…`;
      await D.carregarAnexo(alvo, ref, f);
      feitas++;
    }
  } catch (e) { aviso('Não foi possível carregar: ' + esc(e.message || e), { icone: 'atencao' }); }
  await D.carregarTudo();
  refrescarAnexosDlg();
  if (feitas) aviso(feitas === 1 ? 'Imagem guardada.' : `${feitas} imagens guardadas.`, { icone: 'certo', duracao: 3 });
  depois();
}
function refrescarAnexosDlg() {
  const caixa = dlg.open && $('.anexos-edicao', dlg);
  if (!caixa) return;
  caixa.outerHTML = P.htmlAnexosEdicao(caixa.dataset.alvo, Number(caixa.dataset.ref));
  hidratar(dlg);
}
// imagens de uma nota ainda por escrever: ficam à espera e carregam quando a nota é criada
const notasPendentes = new Map();
function juntarImagensNota(tid, lista) {
  const imagens = saoImagens(lista);
  if (!imagens.length) return;
  notasPendentes.set(tid, [...(notasPendentes.get(tid) || []), ...imagens]);
  const ul = $(`[data-escolhidas-nota="${tid}"]`);
  if (ul) ul.innerHTML = notasPendentes.get(tid).map((f) => `<li>${ic('imagem', 'ic-sm')}${esc(f.name || 'imagem colada')}</li>`).join('');
}
document.addEventListener('paste', (e) => {
  const ficheiros = saoImagens(e.clipboardData ? e.clipboardData.files : []);
  if (!ficheiros.length) return;
  const nota = e.target.closest && e.target.closest('form[data-form="nota"]');
  if (nota) { e.preventDefault(); return juntarImagensNota(Number(nota.dataset.tarefa), ficheiros); }
  const critica = e.target.closest && e.target.closest('form[data-form="critica"]');
  if (critica) { e.preventDefault(); return EQ.juntarCritica(ficheiros, critica); }
  const caixa = dlg.open && $('.anexos-edicao', dlg);
  if (caixa && E.eu.editar) { e.preventDefault(); enviarAnexos(caixa.dataset.alvo, Number(caixa.dataset.ref), ficheiros); }
});
document.addEventListener('dragover', (e) => {
  const zona = e.target.closest && e.target.closest('.anexos-edicao, form[data-form="nota"]');
  if (!zona) return;
  e.preventDefault(); zona.classList.add('sobre');
});
document.addEventListener('dragleave', (e) => { const zona = e.target.closest && e.target.closest('.anexos-edicao, form[data-form="nota"]'); if (zona && !zona.contains(e.relatedTarget)) zona.classList.remove('sobre'); });
document.addEventListener('drop', (e) => {
  const zona = e.target.closest && e.target.closest('.anexos-edicao, form[data-form="nota"]');
  if (!zona || !e.dataTransfer.files.length) return;
  e.preventDefault(); zona.classList.remove('sobre');
  if (zona.matches('form')) juntarImagensNota(Number(zona.dataset.tarefa), e.dataTransfer.files);
  else enviarAnexos(zona.dataset.alvo, Number(zona.dataset.ref), e.dataTransfer.files);
});

// ---------------------------------------------------------------- documentos: secções, ficheiros e pastas (migração 0024)
// O utilizador (2026-11-11): criar uma secção nos documentos informativos ou adicionais, pôr lá os ficheiros que quiser
// e também pastas inteiras (com as subpastas). Quem edita: botões da secção, o diálogo «Documento», ou arrastar.
const IGNORAR = /^(\.|~\$)|^(thumbs\.db|desktop\.ini)$/i;   // hidden and system files of a folder
let alvoCarga = null;   // the section a «Ficheiros» / «Pasta» button is loading into
function pastaDe(relativo) {   // "Obra/Desenhos/planta.pdf" -> "Obra/Desenhos"
  return String(relativo || '').split('/').slice(0, -1).filter((x) => x && x !== '.' && x !== '..').join('/').slice(0, 500);
}
function novoLote() {
  return (crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10)).toLowerCase();
}
// many files (a folder) into a section: three at a time, progress in a notice, one Log line for the batch
async function carregarVarios(projeto, tipo, seccao, itens, { titulo = '', descricao = '' } = {}) {
  itens = itens.filter((x) => !IGNORAR.test(x.ficheiro.name));
  const grandes = itens.filter((x) => x.ficheiro.size > 50 * 1024 * 1024);
  const bons = itens.filter((x) => x.ficheiro.size <= 50 * 1024 * 1024);
  if (!bons.length) {
    if (grandes.length) aviso(`Demasiado grande (máximo 50 MB): ${grandes.map((x) => esc(x.ficheiro.name)).join(', ')}`, { icone: 'atencao' });
    return;
  }
  const lote = bons.length > 1 ? novoLote() : null;
  const so = bons.length === 1;
  const prog = aviso(`<span data-prog>A carregar 0 de ${bons.length}…</span>`, { icone: 'info', duracao: 0 });
  const falhas = [];
  let i = 0, feitos = 0;
  const um = async () => {
    while (i < bons.length) {
      const x = bons[i++];
      try { await D.carregarDocumento(projeto, tipo, x.ficheiro, so ? titulo : '', so ? descricao : '', { seccao_id: seccao, pasta: x.pasta, lote }); }
      catch (e) { falhas.push(`${x.ficheiro.name}: ${e.message || e}`); }
      feitos++;
      const s = prog.querySelector('[data-prog]');
      if (s) s.textContent = `A carregar ${feitos} de ${bons.length}…`;
    }
  };
  await Promise.all([um(), um(), um()]);
  prog.remove();
  if (lote && feitos > falhas.length) { try { await D.loteFeito(lote); } catch (_) { /* the Log line is not essential */ } }
  try { await D.carregarTudo(); } catch (_) { /* the redraw shows what is there */ }
  if (seccao) {
    V.seccoesAbertas.add(`sec:${seccao}`);
    for (const x of bons) {   // the folders just loaded open too
      let k = `sec:${seccao}`;
      for (const parte of x.pasta.split('/').filter(Boolean)) { k += `/${parte}`; V.seccoesAbertas.add(k); }
    }
  }
  depois();
  const n = bons.length - falhas.length;
  if (n) aviso(`${n === 1 ? 'Documento carregado' : `${n} documentos carregados`}${seccao ? ` na secção «${esc((E.seccoes.find((s) => s.id === seccao) || {}).nome || '')}»` : ''}.`, { icone: 'certo', duracao: 4 });
  if (falhas.length || grandes.length) {
    aviso(`<b>Não foram carregados:</b><br>${[...grandes.map((x) => `${esc(x.ficheiro.name)}: maior do que 50 MB`), ...falhas.map(esc)].slice(0, 8).join('<br>')}`, { icone: 'atencao', duracao: 15 });
  }
}
// files and whole folders dragged onto a section (or onto the documents of a type: no section)
async function itensArrastados(dt) {
  const entradas = [...(dt.items || [])].map((it) => (it.kind === 'file' && it.webkitGetAsEntry ? it.webkitGetAsEntry() : null)).filter(Boolean);
  if (!entradas.length) return [...dt.files].map((f) => ({ ficheiro: f, pasta: '' }));
  const out = [];
  const ler = (dir) => new Promise((res) => {
    const r = dir.createReader(), todas = [];
    const mais = () => r.readEntries((es) => { if (!es.length) return res(todas); todas.push(...es); mais(); }, () => res(todas));
    mais();
  });
  async function andar(e, caminho) {
    if (e.isFile) {
      try { out.push({ ficheiro: await new Promise((res, rej) => e.file(res, rej)), pasta: caminho }); } catch (_) { /* unreadable: skipped */ }
    } else if (e.isDirectory) {
      const dentro = caminho ? `${caminho}/${e.name}` : e.name;
      for (const c of await ler(e)) await andar(c, dentro);
    }
  }
  for (const e of entradas) await andar(e, '');
  return out;
}
const zonaDocs = (e) => E.eu.editar && e.target.closest && e.target.closest('#documentos details[data-seccao], #documentos .docs-tipo[data-tipo-docs]');
document.addEventListener('dragover', (e) => {
  const z = zonaDocs(e);
  if (!z || ![...(e.dataTransfer.types || [])].includes('Files')) return;
  e.preventDefault();
  $$('#documentos .sobre').forEach((x) => x !== z && x.classList.remove('sobre'));
  z.classList.add('sobre');
});
document.addEventListener('dragleave', (e) => { const z = zonaDocs(e); if (z && !z.contains(e.relatedTarget)) z.classList.remove('sobre'); });
document.addEventListener('drop', async (e) => {
  const z = zonaDocs(e);
  if (!z || !e.dataTransfer.files.length) return;
  e.preventDefault();
  z.classList.remove('sobre');
  const itens = await itensArrastados(e.dataTransfer);
  const caixa = z.closest('.docs-tipo');
  const s = z.matches('details[data-seccao]') ? E.seccoes.find((x) => x.id === Number(z.dataset.seccao)) : null;
  await carregarVarios(caixa.dataset.projeto, s ? s.tipo : caixa.dataset.tipoDocs, s ? s.id : null, itens);
});
// sections and folders stay open while one works in the tab
document.addEventListener('toggle', (e) => {
  const d = e.target;
  if (!d.matches || !d.matches('#documentos details[data-aberto]')) return;
  if (d.open) V.seccoesAbertas.add(d.dataset.aberto); else V.seccoesAbertas.delete(d.dataset.aberto);
}, true);

// ---------------------------------------------------------------- instalar como app
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});
window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); pedidoInstalar = e; });
window.addEventListener('appinstalled', () => { pedidoInstalar = null; });
