// O ecrã de uma tarefa ou checkpoint (2026-11-11). O utilizador: «quando o utilizador clicar nessa tarefa ou checkpoint
// ou teste … ter um ecrã … com algumas informações. Dentro deste ecrã … deve ser possível ver o ponto de situação da tarefa
// em questão (por tópicos e prático), pedir um ponto de situação e fazer sugestões. A ferramenta do chat entra dentro
// deste ecrã … Dentro deste ecrã deve também ter um botão que nos leva para a página do projeto em si.»
// À esquerda: estado, ponto de situação, pessoas, ações (concluir, pedir aprovação, aprovar/devolver, pedir ponto de
// situação, sugerir), descrição e notas em acordeão. À direita: a conversa (migração 0022, tabela atividade).
import { E, projeto, tarefasDe, decisaoDaTarefa, anexosDe, notasDe, TIPOS_NOTA, marcadosEm, carregarAtividade, escrever, apagarMensagem,
  darSituacao, pedirSituacao, pedirAprovacao, decidirAprovacao, marcar, desmarcar, marcacoesVistas, mudarTarefa } from './dados.js';
import { $, ic, esc, iniciais, aviso, abrirDialogo, fecharDialogo, dia, ha, mov } from './util.js';
import { galeria } from './vistas.js';
import * as CV from './conversa.js';

export const ROTULO = { por_fazer: 'Por fazer', em_curso: 'Em curso', bloqueada: 'Bloqueada', por_aprovar: 'À espera de aprovação', concluida: 'Concluída', concluido: 'Concluído' };
const F = { alvo: null, id: null, atividade: null, pendentes: [], gravar: null, modo: 'mensagem', painel: null, rascunho: '', aEnviar: false, placeholder: '' };
let dlg = null, depois = async () => {}, aoFechar = () => {};

export const aberta = () => (dlg && dlg.open ? { alvo: F.alvo, id: F.id } : null);
const item = () => (F.alvo === 'tarefa' ? E.tarefas.find((t) => t.id === F.id) : E.checkpoints.find((c) => c.id === F.id));
const avatar = (nome, cls = 'pequeno') => `<span class="avatar ${cls}" aria-hidden="true">${esc(iniciais(nome))}</span>`;
const pessoasDe = (x) => marcadosEm(x.id).map((m) => ({ id: m.utilizador_id, nome: CV.nomePessoa(m.utilizador_id), por: m.marcado_por_nome }));

// o último pedido de ponto de situação ainda sem resposta
function pedidoPendente(x) {
  const desde = x.situacao_em ? new Date(x.situacao_em) : new Date(0);
  return (F.atividade || []).filter((a) => a.tipo === 'pedido_situacao' && new Date(a.criada_em) > desde).pop();
}

// ---------------------------------------------------------------- desenho
function html() {
  const x = item(), p = projeto(x.projeto), tarefa = F.alvo === 'tarefa';
  const cp = tarefa ? E.checkpoints.find((c) => c.id === x.checkpoint_id) : x;
  return `<div class="ficha">
    <div class="ficha-topo">
      <nav class="ficha-caminho" aria-label="Onde está"><span>${esc(p.nome)}</span>${tarefa && cp ? `<span aria-hidden="true">/</span><button type="button" class="ligacao-texto" data-acao="ficha-abrir" data-alvo="checkpoint" data-id="${cp.id}" title="Abrir o checkpoint">${esc(cp.titulo)}</button>` : ''}</nav>
      <div class="ficha-topo-acoes"><a class="btn pequeno" href="#/projeto/${p.slug}/${tarefa ? 't' : 'cp'}-${x.id}" data-acao="ficha-ir">${ic('abrir', 'ic-sm')}Abrir o projeto</a>
        <button class="icone-botao" type="button" data-acao="fechar-dlg" aria-label="Fechar">${ic('fechar')}</button></div>
    </div>
    <div class="ficha-corpo">
      <div class="ficha-principal" id="ficha-principal">${htmlPrincipal()}</div>
      <aside class="ficha-conversa" aria-label="Conversa">
        <div class="ficha-conversa-cabeca"><h3>Conversa</h3><span class="fraco mini" id="ficha-n"></span></div>
        <div class="chat-mensagens" id="ficha-mensagens" role="log" aria-label="Mensagens"><p class="fraco pequeno chat-vazio">A carregar…</p></div>
        <form class="chat-escrever" id="ficha-form" novalidate>
          <div class="segmentado ficha-modo" role="group" aria-label="Tipo de mensagem">
            <button type="button" data-acao="ficha-modo" data-valor="mensagem" aria-pressed="${F.modo === 'mensagem'}">Mensagem</button>
            <button type="button" data-acao="ficha-modo" data-valor="sugestao" aria-pressed="${F.modo === 'sugestao'}">Sugestão</button>
          </div>
          <ul class="chat-pendentes" id="ficha-pendentes" hidden></ul>
          <div class="chat-linha-escrever" id="ficha-linha">${CV.htmlLinha(F)}</div>
          <p class="chat-estado fraco mini" id="ficha-estado" role="status"></p>
        </form>
      </aside>
    </div>
  </div>`;
}

function htmlPrincipal() {
  const x = item();
  if (!x) return '<p class="vazio">Esta tarefa já não existe.</p>';
  const tarefa = F.alvo === 'tarefa', p = projeto(x.projeto);
  const ts = CV.topicos(x.situacao), pedido = pedidoPendente(x);
  const d = tarefa ? decisaoDaTarefa(x.id) : null;
  const podeEstado = tarefa && (E.eu.editar || x.responsavel_id === E.eu.id);
  const estado = x.estado;
  const tarefasCp = tarefa ? [] : tarefasDe(x.id);
  const pessoas = tarefa ? pessoasDe(x) : [];
  const livres = E.perfis.filter((q) => q.nome && !pessoas.some((m) => m.id === q.id)).sort((a, b) => a.nome.localeCompare(b.nome, 'pt'));
  const painel = (nome, rotulo, botao, obrigatorio = false, ph = '') => (F.painel === nome ? `<form class="ficha-form" data-ficha-form="${nome}">
      <label class="campo-grupo"><span>${rotulo}</span><textarea class="campo" name="texto" rows="3" maxlength="4000"${obrigatorio ? ' required' : ''} placeholder="${esc(ph)}"></textarea></label>
      <div class="botoes"><button class="btn primario pequeno" type="submit">${botao}</button><button class="btn pequeno texto" type="button" data-acao="ficha-painel" data-painel="">Cancelar</button></div>
      <p class="erro-msg pequeno" role="alert"></p></form>` : '');
  const nImagens = anexosDe(F.alvo, x.id).length;
  const ns = tarefa && x.revisao ? notasDe(x.id) : [], porResolver = ns.filter((n) => !n.resolvida).length;

  return `
  <div class="ficha-cabeca"><span class="estado ${estado}">${ROTULO[estado] || estado}</span>${tarefa && x.revisao ? '<span class="chip">Teste ou revisão</span>' : ''}${tarefa ? '' : '<span class="chip">Checkpoint</span>'}
    ${d ? `<button type="button" class="decisao-pill ${d.estado}" data-acao="ver-decisao" data-id="${d.id}">${ic('decisao', 'ic-sm')}${d.estado === 'aberta' ? 'Decisão em aberto' : 'Decidido'}</button>` : ''}</div>
  <h2 class="ficha-titulo">${esc(x.titulo)}</h2>

  <section class="ficha-bloco ficha-situacao" aria-labelledby="ficha-t-sit">
    <div class="ficha-bloco-cabeca"><h3 id="ficha-t-sit">Ponto de situação</h3>
      ${F.painel === 'situacao' ? '' : `<button class="btn pequeno" type="button" data-acao="ficha-painel" data-painel="situacao">${ic('editar', 'ic-sm')}${ts.length ? 'Atualizar' : 'Escrever'}</button>`}</div>
    ${F.painel === 'situacao' ? `<form class="ficha-form" data-ficha-form="situacao">
        <label class="campo-grupo"><span>Um tópico por linha <small>(o que está feito, o que falta, o que bloqueia)</small></span>
          <textarea class="campo" name="texto" rows="6" maxlength="4000">${esc(ts.join('\n'))}</textarea></label>
        <div class="botoes"><button class="btn primario pequeno" type="submit">Guardar</button><button class="btn pequeno texto" type="button" data-acao="ficha-painel" data-painel="">Cancelar</button></div>
        <p class="erro-msg pequeno" role="alert"></p></form>`
      : ts.length ? `<ul class="topicos">${ts.map((t) => `<li>${esc(t)}</li>`).join('')}</ul><p class="fraco mini">${esc(x.situacao_por_nome || 'Equipa')} · ${ha(x.situacao_em)}</p>`
      : '<p class="fraco pequeno">Ainda sem ponto de situação.</p>'}
    ${pedido ? `<p class="ficha-pedido">${ic('atencao', 'ic-sm')}<span><b>${esc(pedido.autor_nome)}</b> pediu o ponto de situação ${ha(pedido.criada_em)}${pedido.texto ? `: ${esc(pedido.texto)}` : ''}</span></p>` : ''}
  </section>

  <section class="ficha-bloco" aria-label="Ações">
    <div class="ficha-acoes">
      ${tarefa && E.eu.editar && !['concluida', 'por_aprovar'].includes(estado) ? `<button class="btn primario pequeno" type="button" data-acao="ficha-concluir">${ic('certo', 'ic-sm')}Concluir</button>` : ''}
      ${tarefa && estado === 'por_aprovar' && E.eu.editar ? `<button class="btn primario pequeno" type="button" data-acao="ficha-aprovar">${ic('certo', 'ic-sm')}Aprovar</button>
        <button class="btn pequeno" type="button" data-acao="ficha-painel" data-painel="devolver">Devolver</button>` : ''}
      ${tarefa && !['concluida', 'por_aprovar'].includes(estado) ? `<button class="btn pequeno" type="button" data-acao="ficha-painel" data-painel="aprovacao">Pedir aprovação</button>` : ''}
      <button class="btn pequeno" type="button" data-acao="ficha-painel" data-painel="pedido">Pedir ponto de situação</button>
      <button class="btn pequeno" type="button" data-acao="ficha-sugestao">${ic('sugestao', 'ic-sm')}Fazer uma sugestão</button>
    </div>
    ${painel('aprovacao', 'O que está feito? <small>(opcional: quem aprova vê isto)</small>', 'Pedir aprovação')}
    ${painel('devolver', 'O que falta para aprovar?', 'Devolver', true)}
    ${painel('pedido', 'O que queres saber? <small>(opcional)</small>', 'Pedir', false, 'Ex.: já há data para isto?')}
    ${tarefa && estado === 'por_aprovar' && !E.eu.editar ? '<p class="fraco mini">À espera da aprovação de quem edita o Design.</p>' : ''}
  </section>

  <dl class="ficha-info">
    ${tarefa ? `<div><dt>Responsável</dt><dd>${x.responsavel_id ? `${avatar(x.responsavel_nome)}${esc(x.responsavel_nome)}` : '<span class="fraco">Sem responsável</span>'}</dd></div>` : ''}
    <div><dt>Estado</dt><dd>${podeEstado ? `<select class="seletor" data-ficha-estado aria-label="Estado da tarefa">${['por_fazer', 'em_curso', 'bloqueada', 'por_aprovar', 'concluida']
      .filter((e) => E.eu.editar || e !== 'concluida' || estado === 'concluida').map((e) => `<option value="${e}"${e === estado ? ' selected' : ''}>${ROTULO[e]}</option>`).join('')}</select>` : esc(ROTULO[estado] || estado)}</dd></div>
    ${tarefa ? `<div class="largo"><dt>Pessoas marcadas</dt><dd><div class="ficha-pessoas">
        ${pessoas.map((m) => `<span class="chip pessoa" title="Marcado por ${esc(m.por || 'alguém')}">${avatar(m.nome)}${esc(m.nome)}<button type="button" class="icone-botao" data-acao="ficha-desmarcar" data-pessoa="${esc(m.id)}" aria-label="Desmarcar ${esc(m.nome)}">${ic('fechar', 'ic-sm')}</button></span>`).join('')}
        ${livres.length ? `<select class="seletor" data-ficha-marcar aria-label="Marcar uma pessoa nesta tarefa"><option value="">+ Marcar alguém</option>${livres.map((q) => `<option value="${esc(q.id)}">${esc(q.nome)}</option>`).join('')}</select>` : ''}
      </div></dd></div>` : `<div><dt>Tarefas</dt><dd>${tarefasCp.filter((t) => t.estado === 'concluida').length} de ${tarefasCp.length} concluídas</dd></div>`}
    <div><dt>Projeto</dt><dd>${esc(p.nome)}</dd></div>
    ${x.criado_por_nome ? `<div><dt>Criada por</dt><dd>${esc(x.criado_por_nome)}${x.criado_em ? ` · ${dia(x.criado_em)}` : ''}</dd></div>` : ''}
    ${tarefa && x.app_sugerida ? `<div><dt>App sugerida</dt><dd>${esc((projeto(x.app_sugerida) || {}).nome || x.app_sugerida)}</dd></div>` : ''}
    ${tarefa && x.custo ? `<div><dt>Custo</dt><dd>${esc(x.custo)}</dd></div>` : ''}
  </dl>

  ${x.descricao || nImagens || (!tarefa && x.criterio_saida) ? `<details class="ficha-det"><summary>${ic('baixo', 'ic-sm chev')}Descrição${nImagens ? ` · ${nImagens} ${nImagens === 1 ? 'imagem' : 'imagens'}` : ''}</summary>
    ${x.descricao ? `<p class="descricao">${esc(x.descricao)}</p>` : ''}
    ${!tarefa && x.criterio_saida ? `<p class="criterio">${ic('alvo', 'ic-sm')}<span><b>Critério de saída:</b> ${esc(x.criterio_saida)}</span></p>` : ''}
    ${galeria(F.alvo, x.id)}</details>` : ''}
  ${tarefa && x.revisao ? `<details class="ficha-det"><summary>${ic('baixo', 'ic-sm chev')}Notas do teste ou revisão · ${porResolver} por resolver de ${ns.length}</summary>
    ${ns.length ? `<ul class="ficha-notas">${ns.map((n) => `<li class="${n.resolvida ? 'resolvida' : ''}"><span class="nota-tipo ${n.tipo}">${TIPOS_NOTA[n.tipo]}</span> ${esc(n.texto)} <span class="fraco mini">· ${esc(n.autor_nome || 'Equipa')}</span></li>`).join('')}</ul>` : '<p class="fraco pequeno">Ainda sem notas.</p>'}
    <p class="pequeno"><a href="#/projeto/${p.slug}/t-${x.id}" data-acao="ficha-ir">Escrever ou resolver notas na página do projeto</a></p></details>` : ''}
  ${!tarefa ? `<section class="ficha-bloco"><h3>Tarefas</h3>${tarefasCp.length ? `<ul class="pp-lista">${tarefasCp.map((t) => `<li><button type="button" class="pp-linha" data-acao="ficha-abrir" data-alvo="tarefa" data-id="${t.id}">
      <span class="estado ${t.estado}">${ROTULO[t.estado]}</span><span class="pp-linha-texto"><b>${esc(t.titulo)}</b></span>${ic('direita', 'ic-sm')}</button></li>`).join('')}</ul>` : '<p class="fraco pequeno">Ainda sem tarefas.</p>'}</section>` : ''}`;
}

const EVENTO = { pedido_situacao: ['atencao', 'pediu o ponto de situação'], situacao: ['info', 'atualizou o ponto de situação'], pedido_aprovacao: ['certo', 'pediu aprovação'],
  aprovada: ['certo', 'aprovou a tarefa'], devolvida: ['esquerda', 'devolveu a tarefa'] };
function htmlEntrada(m, antes) {
  const minha = m.autor_id === E.eu.id, claude = !m.autor_id;
  if (EVENTO[m.tipo]) {
    const [icone, rotulo] = EVENTO[m.tipo];
    const corpo = m.tipo === 'situacao' ? `<ul class="topicos">${CV.topicos(m.texto).map((t) => `<li>${esc(t)}</li>`).join('')}</ul>` : m.texto ? `<p class="msg-texto">${CV.ligacoes(esc(m.texto))}</p>` : '';
    return `<div class="evento ${m.tipo}" id="atv-${m.id}"><p class="evento-linha">${ic(icone, 'ic-sm')}<span><b>${esc(minha ? 'Tu' : m.autor_nome)}</b> ${rotulo} · <time datetime="${esc(m.criada_em)}">${CV.hora(m.criada_em)}</time></span></p>${corpo}</div>`;
  }
  const seguida = antes && !EVENTO[antes.tipo] && antes.autor_id === m.autor_id && antes.tipo === m.tipo && new Date(m.criada_em) - new Date(antes.criada_em) < 5 * 60 * 1000;
  return `<div class="msg${minha ? ' minha' : ''}${claude ? ' claude' : ''}${seguida ? ' seguida' : ''}${m.tipo === 'sugestao' ? ' sugestao' : ''}" id="atv-${m.id}">
    ${!minha && !seguida ? `<span class="msg-autor">${esc(m.autor_nome || 'Alguém')}</span>` : ''}
    <div class="msg-linha">
      <div class="msg-bolha">${m.tipo === 'sugestao' ? `<span class="msg-etiqueta">${ic('sugestao', 'ic-sm')}Sugestão</span>` : ''}${CV.htmlAnexos(m.anexos, String(m.id))}${m.texto ? `<p class="msg-texto">${CV.ligacoes(esc(m.texto))}</p>` : ''}<time class="msg-hora" datetime="${esc(m.criada_em)}">${CV.hora(m.criada_em)}</time></div>
      ${minha || (E.eu.editar && !claude) ? `<button class="icone-botao msg-apagar" type="button" data-acao="ficha-apagar" data-id="${m.id}" aria-label="Apagar esta mensagem" title="Apagar">${ic('apagar', 'ic-sm')}</button>` : ''}
    </div>
  </div>`;
}
function htmlConversa() {
  const ms = F.atividade;
  if (!ms) return '<p class="fraco pequeno chat-vazio">A carregar…</p>';
  if (!ms.length) return '<p class="fraco pequeno chat-vazio">Ainda sem conversa. Escreve uma mensagem, faz uma sugestão ou pede um ponto de situação.</p>';
  let h = '', diaAntes = '';
  ms.forEach((m, i) => {
    const d = new Date(m.criada_em).toDateString();
    if (d !== diaAntes) { h += `<div class="chat-dia"><span>${CV.rotuloDia(m.criada_em)}</span></div>`; diaAntes = d; }
    h += htmlEntrada(m, i ? ms[i - 1] : null);
  });
  return h;
}
function fundo() { const c = $('#ficha-mensagens', dlg); if (c) { c.scrollTop = c.scrollHeight; requestAnimationFrame(() => { c.scrollTop = c.scrollHeight; }); } }
function desenharConversa(irAoFundo) {
  const caixa = $('#ficha-mensagens', dlg);
  if (!caixa) return;
  const noFundo = caixa.scrollHeight - caixa.scrollTop - caixa.clientHeight < 80;
  caixa.innerHTML = htmlConversa();
  const n = $('#ficha-n', dlg);
  if (n) n.textContent = F.atividade && F.atividade.length ? `${F.atividade.length} ${F.atividade.length === 1 ? 'registo' : 'registos'}` : '';
  CV.prepararMedia(caixa, () => { if (irAoFundo || noFundo) fundo(); });
  if (irAoFundo || noFundo) fundo();
}
function desenharPrincipal() {
  const el = $('#ficha-principal', dlg);
  if (!el) return;
  const abertos = [...el.querySelectorAll('details.ficha-det')].map((d) => d.open);
  el.innerHTML = htmlPrincipal();
  [...el.querySelectorAll('details.ficha-det')].forEach((d, i) => { if (abertos[i]) d.open = true; });
  import('./imagens.js').then((m) => m.hidratar(el));
  const f = el.querySelector('[data-ficha-form] textarea');
  if (f) f.focus();
}
function desenharLinha() {
  const l = $('#ficha-linha', dlg);
  if (l) { guardarRascunho(); l.innerHTML = CV.htmlLinha(F); CV.ajustarAltura(dlg); }
}
function desenharPendentes() {
  const ul = $('#ficha-pendentes', dlg);
  if (!ul) return;
  ul.innerHTML = CV.htmlPendentes(F.pendentes);
  ul.hidden = !F.pendentes.length;
}
function estado(txt, erro = false) { const e = $('#ficha-estado', dlg); if (e) { e.textContent = txt; e.classList.toggle('erro-msg', erro); } }
function guardarRascunho() { const t = dlg && $('[data-conv-texto]', dlg); if (t) F.rascunho = t.value; }
function mudarModo(modo) {
  F.modo = modo;
  F.placeholder = modo === 'sugestao' ? 'Escreve a tua sugestão para esta tarefa…' : 'Escreve uma mensagem…';
  dlg.querySelectorAll('[data-acao="ficha-modo"]').forEach((b) => b.setAttribute('aria-pressed', b.dataset.valor === modo));
  const t = $('[data-conv-texto]', dlg);
  if (t) { t.placeholder = F.placeholder; t.focus(); }
}

// ---------------------------------------------------------------- abrir, atualizar
export async function abrir(alvo, id) {
  if (!dlg) return;
  if (dlg.open && F.alvo === alvo && F.id === Number(id)) return;
  CV.pararGravacao(F, true);
  Object.assign(F, { alvo, id: Number(id), atividade: null, pendentes: [], modo: 'mensagem', painel: null, rascunho: '', placeholder: '' });
  const x = item();
  if (!x) { aviso(alvo === 'tarefa' ? 'Esta tarefa já não existe.' : 'Este checkpoint já não existe.', { icone: 'atencao' }); return; }
  dlg.setAttribute('aria-label', x.titulo);
  abrirDialogo(dlg, html());
  import('./imagens.js').then((m) => m.hidratar(dlg));
  if (alvo === 'tarefa') marcacoesVistas([F.id]).catch(() => {});
  await carregar();
}
async function carregar() {
  try { F.atividade = await carregarAtividade(F.alvo, F.id); } catch (e) { F.atividade = []; estado('A conversa não carregou: ' + (e.message || e), true); }
  desenharConversa(true);
  desenharPrincipal();   // o pedido de ponto de situação vem da conversa
}
// uma mudança em direto (de outra pessoa ou noutra janela)
export async function aoMudar() {
  if (!dlg || !dlg.open) return;
  if (!item()) { fecharDialogo(dlg); return; }
  const aEscrever = dlg.querySelector('[data-ficha-form]') && dlg.querySelector('[data-ficha-form]').contains(document.activeElement);
  try { F.atividade = await carregarAtividade(F.alvo, F.id); } catch (_) { return; }
  desenharConversa(false);
  if (!aEscrever) desenharPrincipal();
}
async function feito(fn, msgOk) {
  try { await fn(); } catch (e) { aviso('Não foi possível: ' + esc(e.message || e), { icone: 'atencao' }); return false; }
  F.painel = null;
  if (msgOk) aviso(msgOk, { icone: 'certo', duracao: 3 });
  await depois();
  await carregar();
  return true;
}

// ---------------------------------------------------------------- enviar mensagens
async function enviar(texto, ficheiros, extra = {}) {
  if (F.aEnviar || (!texto && !ficheiros.length)) return false;
  F.aEnviar = true;
  const feitos = [], prefixo = `${F.alvo}-${F.id}`, alvo = F.alvo, id = F.id;
  try {
    for (const [i, f] of ficheiros.entries()) {
      estado(ficheiros.length > 1 ? `A carregar ${i + 1} de ${ficheiros.length}…` : `A carregar «${f.name || 'ficheiro'}»…`);
      feitos.push(await CV.carregarAnexo(prefixo, f, extra));
    }
    estado('A enviar…');
    const m = await escrever(alvo, id, F.modo, texto, feitos);
    if (F.alvo === alvo && F.id === id) {
      if (!F.atividade.some((x) => x.id === m.id)) F.atividade.push(m);
      estado('');
      desenharConversa(true);
    }
    return true;
  } catch (e) {
    CV.apagarFicheiros(feitos);
    estado('Não foi enviada: ' + (e.message || e), true);
    return false;
  } finally { F.aEnviar = false; }
}
async function enviarFormulario() {
  const t = $('[data-conv-texto]', dlg);
  const texto = t ? t.value.trim() : '';
  const ficheiros = [...F.pendentes];
  if (!texto && !ficheiros.length) return;
  const botao = $('#ficha-form [type=submit]', dlg);
  if (botao) botao.disabled = true;
  const ok = await enviar(texto, ficheiros);
  if (botao && botao.isConnected) botao.disabled = false;
  if (!ok) return;
  if (t) { t.value = ''; CV.ajustarAltura(dlg); }
  F.rascunho = ''; F.pendentes = [];
  desenharPendentes();
  if (F.modo === 'sugestao') { mudarModo('mensagem'); aviso('Sugestão enviada.', { icone: 'certo', duracao: 3 }); }
}

// ---------------------------------------------------------------- eventos (dentro do ecrã)
export function ligar(opcoes) {
  dlg = $('#ficha');
  depois = opcoes.depois || depois;
  aoFechar = opcoes.aoFechar || aoFechar;
  if (!dlg) return;
  dlg.addEventListener('click', async (e) => {
    const el = e.target.closest('[data-acao]');
    if (!el) return;
    const x = item();
    switch (el.dataset.acao) {
      case 'ficha-abrir': return abrir(el.dataset.alvo, Number(el.dataset.id));
      case 'ficha-ir': fecharDialogo(dlg); document.querySelectorAll('dialog[open]').forEach((d) => d !== dlg && fecharDialogo(d)); return;   // o link segue para o projeto
      case 'ficha-painel': F.painel = el.dataset.painel || null; desenharPrincipal(); return;
      case 'ficha-sugestao': mudarModo('sugestao'); return;
      case 'ficha-modo': mudarModo(el.dataset.valor); return;
      case 'ficha-concluir': return feito(() => mudarTarefa(x.id, { estado: 'concluida' }), 'Tarefa concluída. A equipa foi avisada.');
      case 'ficha-aprovar': return feito(() => decidirAprovacao(x.id, true, ''), 'Aprovada: a tarefa ficou concluída.');
      case 'ficha-desmarcar': return feito(() => desmarcar(x.id, el.dataset.pessoa));
      case 'ficha-apagar': {
        const m = (F.atividade || []).find((a) => a.id === Number(el.dataset.id));
        if (!m || !confirm('Apagar esta mensagem?')) return;
        try { await apagarMensagem(m.id); } catch (err) { aviso('Não foi possível apagar: ' + esc(err.message || err), { icone: 'atencao' }); return; }
        CV.apagarFicheiros(m.anexos);
        F.atividade = F.atividade.filter((a) => a.id !== m.id);
        desenharConversa(false);
        return;
      }
      case 'conv-escolher': { const i = dlg.querySelector(`[data-conv-ficheiros="${el.dataset.qual}"]`); if (i) i.click(); return; }
      case 'conv-tirar': F.pendentes.splice(Number(el.dataset.i), 1); desenharPendentes(); return;
      case 'conv-audio': return CV.gravar(F, { aoMudar: desenharLinha, aviso: (t) => estado(t, true), aoAcabar: (f, s) => enviar('', [f], { duracao: s }) });
      case 'conv-audio-cancelar': return CV.pararGravacao(F, true);
      case 'conv-audio-enviar': return CV.pararGravacao(F, false);
      case 'conv-imagem': case 'conv-ficheiro':
        try { await CV.cliqueAnexo(el, (chave) => ((F.atividade || []).find((a) => String(a.id) === chave) || {}).anexos); }
        catch (err) { aviso('Não foi possível abrir o ficheiro: ' + esc(err.message || err), { icone: 'atencao' }); }
        return;
    }
  });
  dlg.addEventListener('submit', async (e) => {
    e.preventDefault();
    const f = e.target, x = item();
    if (f.id === 'ficha-form') return enviarFormulario();
    const qual = f.dataset.fichaForm;
    if (!qual || !x) return;
    const texto = f.elements.texto.value.trim();
    const b = f.querySelector('[type=submit]');
    if (b) b.disabled = true;
    const msg = $('.erro-msg', f);
    let ok = true;
    try {
      if (qual === 'situacao') await darSituacao(F.alvo, x.id, texto);
      else if (qual === 'pedido') await pedirSituacao(F.alvo, x.id, texto);
      else if (qual === 'aprovacao') await pedirAprovacao(x.id, texto);
      else if (qual === 'devolver') { if (!texto) throw new Error('Diz o que falta para a aprovar.'); await decidirAprovacao(x.id, false, texto); }
    } catch (err) { ok = false; if (msg) msg.textContent = err.message || String(err); }
    if (b && b.isConnected) b.disabled = false;
    if (!ok) return;
    F.painel = null;
    aviso({ situacao: 'Ponto de situação guardado.', pedido: 'Pedido enviado: quem acompanha a tarefa foi avisado.', aprovacao: 'Pedido de aprovação enviado.', devolver: 'Devolvida: quem a acompanha foi avisado.' }[qual], { icone: 'certo', duracao: 3 });
    await depois();
    await carregar();
  });
  dlg.addEventListener('change', async (e) => {
    const el = e.target, x = item();
    if (el.matches('[data-conv-ficheiros]')) { CV.juntar(F, el.files, (t) => estado(t, true)); el.value = ''; desenharPendentes(); return; }
    if (el.matches('[data-ficha-marcar]') && el.value) { const id = el.value; el.disabled = true; await feito(() => marcar(x.id, id), `${CV.nomePessoa(id)} foi marcado e avisado.`); return; }
    if (el.matches('[data-ficha-estado]')) {
      const novo = el.value;
      if (novo === 'por_aprovar') { F.painel = 'aprovacao'; desenharPrincipal(); return; }
      await feito(() => mudarTarefa(x.id, { estado: novo }));
    }
  });
  dlg.addEventListener('input', (e) => { if (e.target.matches('[data-conv-texto]')) CV.ajustarAltura(dlg); });
  dlg.addEventListener('keydown', (e) => {
    if (e.target.matches('[data-conv-texto]') && e.key === 'Enter' && !e.shiftKey && !e.isComposing && matchMedia('(hover: hover)').matches) { e.preventDefault(); enviarFormulario(); }
  });
  dlg.addEventListener('paste', (e) => {
    if (!e.target.closest('#ficha-form') || !e.clipboardData || !e.clipboardData.files.length) return;
    e.preventDefault(); CV.juntar(F, e.clipboardData.files, (t) => estado(t, true)); desenharPendentes();
  });
  dlg.addEventListener('dragover', (e) => { if ([...(e.dataTransfer.types || [])].includes('Files')) { e.preventDefault(); dlg.classList.add('sobre'); } });
  dlg.addEventListener('dragleave', (e) => { if (!dlg.contains(e.relatedTarget)) dlg.classList.remove('sobre'); });
  dlg.addEventListener('drop', (e) => {
    dlg.classList.remove('sobre');
    if (!e.dataTransfer.files.length) return;
    e.preventDefault(); CV.juntar(F, e.dataTransfer.files, (t) => estado(t, true)); desenharPendentes();
  });
  dlg.addEventListener('close', () => { CV.pararGravacao(F, true); aoFechar(); });
  if (mov()) { /* a entrada usa a animação comum dos diálogos */ }
}
