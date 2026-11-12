// Trabalho em equipa (2026-11-11): o pop-up de cada projeto no Início («em vez de cada ligação na aba dos Projetos levar
// diretamente para a página de cada projeto abrir um pop-up onde estão presentes as tarefas em curso ou que necessitam da
// atenção de alguém»), o pop-up das tarefas em que fui marcado, as críticas e comentários sobre um projeto e o Log
// (todas as mudanças, ao lado da checklist; avisa ao abrir o hub do que veio desde a última visita).
import { E, projeto, nomeProjeto, resumo, decisoesDe, tarefasDe, notasDe, marcadosEm, marcacoesPorVer, criticasDe, TIPOS_CRITICA } from './dados.js';
import { $, ic, esc, iniciais, dia, ha, abrirDialogo } from './util.js';
import { htmlSituacao } from './vistas.js';
import * as CV from './conversa.js';
import { ROTULO } from './ficha.js';

const avatar = (nome) => `<span class="avatar pequeno" aria-hidden="true">${esc(iniciais(nome))}</span>`;
const pessoas = (t) => [...new Set([t.responsavel_id, ...marcadosEm(t.id).map((m) => m.utilizador_id)].filter(Boolean))];

// uma linha clicável (tarefa ou checkpoint) que abre o ecrã da tarefa
export function linhaTarefa(t, extra = '') {
  const cp = E.checkpoints.find((c) => c.id === t.checkpoint_id);
  const ps = pessoas(t);
  const sub = [cp ? cp.titulo : '', ps.map(CV.nomePessoa).join(', '), t.situacao_em ? `ponto de situação ${ha(t.situacao_em)}` : '', extra].filter(Boolean).join(' · ');
  return `<li><button type="button" class="pp-linha" data-acao="abrir-ficha" data-alvo="tarefa" data-id="${t.id}">
    <span class="estado ${t.estado}">${ROTULO[t.estado]}</span>
    <span class="pp-linha-texto"><b>${esc(t.titulo)}</b>${sub ? `<span class="fraco mini">${esc(sub)}</span>` : ''}</span>
    <span class="pp-pessoas">${ps.slice(0, 3).map((id) => avatar(CV.nomePessoa(id))).join('')}</span>${ic('direita', 'ic-sm')}</button></li>`;
}
const grupo = (titulo, itens, explica = '') => (itens.length ? `<section class="pp-grupo"><h3>${titulo} <span class="fraco num">${itens.length}</span></h3>${explica ? `<p class="fraco mini">${explica}</p>` : ''}<ul class="pp-lista">${itens.join('')}</ul></section>` : '');

// ---------------------------------------------------------------- críticas e comentários
const ROT_CRITICA_ESTADO = { nova: 'Nova', vista: 'Vista', resolvida: 'Resolvida' };
export function linhaCritica(c) {
  const pode = E.eu.editar || c.autor_id === E.eu.id;
  const tarefa = c.tarefa_id ? E.tarefas.find((t) => t.id === c.tarefa_id) : null;
  return `<li class="critica ${c.tipo} ${c.estado}" id="critica-${c.id}">
    <div class="critica-cabeca"><span class="critica-tipo ${c.tipo}">${esc(TIPOS_CRITICA[c.tipo])}</span><span class="fraco mini">${esc(c.autor_nome || 'Alguém')} · ${ha(c.criada_em)}${c.onde ? ` · ${esc(c.onde)}` : ''} · ${ROT_CRITICA_ESTADO[c.estado]}${c.resolvida_por_nome ? ` por ${esc(c.resolvida_por_nome)}` : ''}</span></div>
    <p class="critica-texto">${CV.ligacoes(esc(c.texto))}</p>
    ${CV.htmlAnexos(c.anexos, 'critica-' + c.id)}
    <div class="critica-acoes">
      ${tarefa ? `<button type="button" class="btn pequeno texto" data-acao="abrir-ficha" data-alvo="tarefa" data-id="${tarefa.id}">${ic('seta', 'ic-sm')}Passou a tarefa: ${esc(tarefa.titulo)}</button>`
        : E.eu.editar && c.estado !== 'resolvida' ? `<button type="button" class="btn pequeno" data-acao="critica-tarefa" data-id="${c.id}">Passar a tarefa</button>` : ''}
      ${E.eu.editar && c.estado !== 'resolvida' ? `<button type="button" class="btn pequeno" data-acao="critica-estado" data-id="${c.id}" data-valor="resolvida">${ic('certo', 'ic-sm')}Resolvida</button>` : ''}
      ${E.eu.editar && c.estado === 'nova' ? `<button type="button" class="btn pequeno texto" data-acao="critica-estado" data-id="${c.id}" data-valor="vista">Vista</button>` : ''}
      ${E.eu.editar && c.estado === 'resolvida' ? `<button type="button" class="btn pequeno texto" data-acao="critica-estado" data-id="${c.id}" data-valor="vista">Reabrir</button>` : ''}
      ${pode ? `<button type="button" class="btn pequeno texto perigo" data-acao="critica-apagar" data-id="${c.id}">Apagar</button>` : ''}
    </div>
  </li>`;
}
export function htmlCriticas(pid, { todas = false } = {}) {
  const cs = criticasDe(pid);
  const abertas = cs.filter((c) => c.estado !== 'resolvida');
  const lista = todas ? cs : abertas;
  return `${lista.length ? `<ul class="criticas">${lista.map(linhaCritica).join('')}</ul>` : `<p class="fraco pequeno">${cs.length ? 'Todas resolvidas.' : 'Ainda sem críticas nem comentários.'}</p>`}
    ${!todas && cs.length > abertas.length ? `<button type="button" class="btn pequeno texto" data-acao="criticas-todas" data-projeto="${pid}">Ver também as resolvidas (${cs.length - abertas.length})</button>` : ''}`;
}
// o formulário (no diálogo comum #dlg): tipo, o que aconteceu, onde, imagens ou ficheiros
const C = { pendentes: [] };
export function dlgCritica(pid) {
  C.pendentes = [];
  const p = pid ? projeto(pid) : null;
  return `<form data-form="critica" data-projeto="${esc(pid || '')}">
    <div class="dlg-cabeca"><div><h2>Crítica ou comentário</h2><p class="suave pequeno" style="margin-top:4px">${p ? esc(p.nome) + ' · ' : ''}toda a equipa vê; quem edita é avisado.</p></div>
      <button class="icone-botao" type="button" data-acao="fechar-dlg" aria-label="Fechar">${ic('fechar')}</button></div>
    <div class="dlg-corpo">
      <div class="segmentado" role="group" aria-label="O que é">${Object.entries(TIPOS_CRITICA).map(([k, v], i) => `<button type="button" data-acao="tipo-critica" data-valor="${k}" aria-pressed="${i === 0}">${v}</button>`).join('')}</div>
      <input type="hidden" name="tipo" value="erro">
      ${p ? '' : `<label class="campo-grupo"><span>Sobre que projeto?</span><select class="campo" name="projeto" required><option value="">Escolhe o projeto</option>${E.projetos.map((x) => `<option value="${x.id}">${esc(x.nome)}</option>`).join('')}</select></label>`}
      <label class="campo-grupo"><span>O que aconteceu?</span><textarea class="campo" name="texto" required minlength="2" maxlength="4000"
        placeholder="O que fizeste, o que esperavas e o que aconteceu. Podes colar capturas de ecrã (Ctrl+V)."></textarea></label>
      <label class="campo-grupo"><span>Onde? <small>(opcional: a página, o passo, o documento)</small></span><input class="campo" name="onde" maxlength="300" autocomplete="off"></label>
      <div class="critica-anexos"><label class="btn pequeno texto">${ic('clipe', 'ic-sm')}Juntar imagens ou ficheiros<input type="file" name="critica-ficheiros" multiple class="so-leitor"></label>
        <ul class="chat-pendentes" data-critica-pendentes hidden></ul></div>
      <p class="erro-msg pequeno" role="alert"></p>
    </div>
    <div class="dlg-rodape"><button class="btn texto" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">Enviar</button></div>
  </form>`;
}
export function juntarCritica(lista, form) {
  CV.juntar(C, lista, (t) => { const m = $('.erro-msg', form); if (m) m.textContent = t; });
  const ul = $('[data-critica-pendentes]', form);
  if (ul) { ul.innerHTML = CV.htmlPendentes(C.pendentes).replaceAll('data-acao="conv-tirar"', 'data-acao="critica-tirar"'); ul.hidden = !C.pendentes.length; }
}
export function tirarCritica(i, form) { C.pendentes.splice(i, 1); juntarCritica([], form); }
export async function enviarCritica(form, criar) {
  const v = (n) => form.elements[n].value.trim();
  const pid = form.elements.projeto ? form.elements.projeto.value : form.dataset.projeto;
  if (!pid) throw new Error('escolhe o projeto.');
  const feitos = [];
  try {
    for (const f of C.pendentes) feitos.push(await CV.carregarAnexo('critica', f));
    await criar({ projeto: pid, tipo: v('tipo'), texto: v('texto'), onde: v('onde'), anexos: feitos });
    C.pendentes = [];
    return true;
  } catch (e) { CV.apagarFicheiros(feitos); throw e; }
}
export const anexosCritica = (chave) => ((E.criticas.find((c) => 'critica-' + c.id === chave) || {}).anexos);

// ---------------------------------------------------------------- o pop-up de um projeto (Início)
export function htmlProjeto(p, { criticas = false } = {}) {
  const r = resumo(p.id);
  const ts = E.tarefas.filter((t) => t.projeto === p.id && t.estado !== 'concluida');
  const usadas = new Set();
  const tira = (lista) => lista.filter((t) => !usadas.has(t.id) && usadas.add(t.id));
  const aprovar = tira(ts.filter((t) => t.estado === 'por_aprovar'));
  const bloqueadas = tira(ts.filter((t) => t.estado === 'bloqueada'));
  const minhas = tira(ts.filter((t) => t.responsavel_id === E.eu.id || marcadosEm(t.id).some((m) => m.utilizador_id === E.eu.id)));
  const testes = tira(ts.filter((t) => t.revisao && notasDe(t.id).some((n) => !n.resolvida)));
  const emCurso = tira(ts.filter((t) => t.estado === 'em_curso'));
  const proximas = r.atual ? tira(tarefasDe(r.atual.id).filter((t) => t.estado === 'por_fazer')).slice(0, 4) : [];
  const decs = decisoesDe(p.id).filter((d) => d.estado === 'aberta');
  const cs = criticasDe(p.id).filter((c) => c.estado !== 'resolvida');
  const nota = (t) => { const n = notasDe(t.id).filter((x) => !x.resolvida).length; return `${n} ${n === 1 ? 'nota por resolver' : 'notas por resolver'}`; };
  const nada = !aprovar.length && !bloqueadas.length && !minhas.length && !testes.length && !emCurso.length && !cs.length && !decs.length;
  return `<div class="pp" data-projeto="${p.id}">
    <div class="dlg-cabeca"><div><h2>${esc(p.nome)} <span class="fase">${esc(p.fase)}</span></h2>
      <p class="suave pequeno" style="margin-top:6px"><span class="num">${r.feitos} de ${r.total}</span> checkpoints${r.atual ? ` · agora: <b>${esc(r.atual.titulo)}</b>` : ''}</p></div>
      <button class="icone-botao" type="button" data-acao="fechar-dlg" aria-label="Fechar">${ic('fechar')}</button></div>
    <div class="pp-acoes">
      <a class="btn primario pequeno" href="#/projeto/${p.slug}" data-acao="pp-ir">${ic('seta', 'ic-sm')}Abrir o projeto</a>
      <button class="btn pequeno" type="button" data-acao="nova-critica" data-projeto="${p.id}">${ic('comentario', 'ic-sm')}Deixar uma crítica ou comentário</button>
      ${p.app ? `<a class="btn pequeno texto" href="${esc(p.app.url)}" target="_blank" rel="noopener">${ic('abrir', 'ic-sm')}${esc(p.app.rotulo)}</a>` : ''}
    </div>
    <div class="dlg-corpo pp-corpo">
      ${htmlSituacao(p, true)}
      ${grupo('À espera de aprovação', aprovar.map((t) => linhaTarefa(t)), 'Quase concluídas: falta quem edita aprovar ou devolver.')}
      ${grupo('Bloqueadas', bloqueadas.map((t) => linhaTarefa(t)))}
      ${grupo('Para ti', minhas.map((t) => linhaTarefa(t)), 'És o responsável ou foste marcado.')}
      ${cs.length ? `<section class="pp-grupo" id="pp-criticas"><h3>Críticas e comentários <span class="fraco num">${cs.length}</span></h3>${htmlCriticas(p.id)}</section>` : ''}
      ${decs.length ? `<section class="pp-grupo"><h3>Decisões em aberto <span class="fraco num">${decs.length}</span></h3><ul class="lista-simples">${decs.map((d) => `<li><button type="button" class="decisao-pill aberta" data-acao="ver-decisao" data-id="${d.id}">${ic('decisao', 'ic-sm')}Decisão</button><span class="pequeno">${esc(d.pergunta)}</span></li>`).join('')}</ul></section>` : ''}
      ${grupo('Testes com notas por resolver', testes.map((t) => linhaTarefa(t, nota(t))))}
      ${grupo('Em curso', emCurso.map((t) => linhaTarefa(t)))}
      ${r.atual ? `<section class="pp-grupo"><h3>Checkpoint atual</h3><ul class="pp-lista"><li><button type="button" class="pp-linha" data-acao="abrir-ficha" data-alvo="checkpoint" data-id="${r.atual.id}">
          <span class="estado ${r.atual.estado}">${ROTULO[r.atual.estado]}</span><span class="pp-linha-texto"><b>${esc(r.atual.titulo)}</b><span class="fraco mini">${tarefasDe(r.atual.id).filter((t) => t.estado === 'concluida').length} de ${tarefasDe(r.atual.id).length} tarefas</span></span>${ic('direita', 'ic-sm')}</button></li>
          ${proximas.map((t) => linhaTarefa(t)).join('')}</ul></section>` : ''}
      ${nada && !r.atual ? '<p class="vazio">Nada em curso neste projeto.</p>' : ''}
      ${criticas && !cs.length ? `<section class="pp-grupo" id="pp-criticas"><h3>Críticas e comentários</h3>${htmlCriticas(p.id, { todas: true })}</section>` : ''}
    </div>
  </div>`;
}
let popDlg = null, popProjeto = null, popCriticas = false;
export function abrirProjeto(pid, { criticas = false } = {}) {
  popDlg = popDlg || $('#projeto-pop');
  const p = projeto(pid);
  if (!p || !popDlg) return;
  popProjeto = pid; popCriticas = criticas;
  popDlg.setAttribute('aria-label', p.nome);
  abrirDialogo(popDlg, htmlProjeto(p, { criticas }));
  import('./imagens.js').then((m) => m.hidratar(popDlg));
  CV.prepararMedia(popDlg);
  if (criticas) { const s = $('#pp-criticas', popDlg); if (s) s.scrollIntoView({ block: 'start' }); }
}
// redesenha o pop-up aberto (dados novos), sem perder o sítio
export function redesenharProjeto() {
  if (!popDlg || !popDlg.open || !projeto(popProjeto)) return;
  const corpo = $('.pp-corpo', popDlg), y = corpo ? corpo.scrollTop : 0;
  popDlg.innerHTML = htmlProjeto(projeto(popProjeto), { criticas: popCriticas });
  const novo = $('.pp-corpo', popDlg); if (novo) novo.scrollTop = y;
  import('./imagens.js').then((m) => m.hidratar(popDlg));
  CV.prepararMedia(popDlg);
}

// ---------------------------------------------------------------- foste marcado (pop-up ao abrir o hub)
export function htmlMarcacoes() {
  const ms = marcacoesPorVer();
  if (!ms.length) return '';
  return `<div data-marcacoes>
    <div class="dlg-cabeca"><div><h2>${ms.length === 1 ? 'Foste marcado numa tarefa' : `Foste marcado em ${ms.length} tarefas`}</h2>
      <p class="suave pequeno" style="margin-top:4px">Toca numa para ver o ponto de situação e a conversa.</p></div>
      <button class="icone-botao" type="button" data-acao="fechar-dlg" aria-label="Fechar">${ic('fechar')}</button></div>
    <div class="dlg-corpo"><ul class="pp-lista">${ms.map((m) => linhaTarefa(E.tarefas.find((t) => t.id === m.tarefa_id), `${nomeProjeto(E.tarefas.find((t) => t.id === m.tarefa_id).projeto)} · marcado por ${m.marcado_por_nome || 'alguém'} ${ha(m.criada_em)}`)).join('')}</ul></div>
    <div class="dlg-rodape"><a class="btn texto" href="#/pessoal" data-acao="ir-pessoal">Ver todas as tarefas para ti</a><button class="btn texto" type="button" data-acao="marcacoes-vistas">Marcar todas como vistas</button><button class="btn" type="button" data-acao="fechar-dlg">Mais tarde</button></div>
  </div>`;
}

// ---------------------------------------------------------------- o Log
export const IMPACTO = new Set(['checkpoint_concluido', 'decisao_nova', 'decisao_tomada', 'tarefa_concluida', 'critica_nova']);
export const filtroLog = { projeto: '', meus: false };
export function htmlLog(erro) {
  if (erro) return `<p class="erro-msg">Não consegui carregar o Log: ${esc(erro)}</p>`;
  const lista = E.registo.filter((r) => (!filtroLog.projeto || r.projeto === filtroLog.projeto) && (!filtroLog.meus || r.ator_id !== E.eu.id));
  let h = '', diaAntes = '';
  for (const r of lista) {
    const d = new Date(r.criada_em).toDateString();
    if (d !== diaAntes) { h += `${diaAntes ? '</ul>' : ''}<h4 class="log-dia">${CV.rotuloDia(r.criada_em)}</h4><ul class="log-lista">`; diaAntes = d; }
    h += `<li class="log-linha${r.ator_nome === 'Claude' ? ' claude' : ''}"><time class="fraco mini num" datetime="${esc(r.criada_em)}">${CV.hora(r.criada_em)}</time>
      <div><p>${esc(r.texto)}</p><p class="fraco mini">${esc(r.projeto ? nomeProjeto(r.projeto) : r.ref_tipo === 'post' || r.ref_tipo === 'obra' ? 'Redes sociais' : 'Hub')} · ${esc(r.ator_nome || 'Alguém')}</p>
        ${r.detalhe ? `<details class="log-detalhe"><summary>Pormenor</summary><p>${CV.ligacoes(esc(r.detalhe))}</p></details>` : ''}</div>
      ${r.ref_tipo && r.ref_id ? `<button type="button" class="btn pequeno texto" data-acao="log-ver" data-projeto="${esc(r.projeto || '')}" data-ref="${esc(r.ref_tipo)}" data-id="${r.ref_id}">Ver</button>` : '<span></span>'}</li>`;
  }
  if (diaAntes) h += '</ul>';
  return `<p class="suave pequeno">Todas as mudanças no hub, mais recentes primeiro, e o pormenor do que o Claude faz. As notificações ficam só para o que tem impacto.</p>
    <div class="log-filtros"><select class="campo" data-log="projeto" aria-label="Projeto"><option value="">Todos os projetos</option>${E.projetos.map((p) => `<option value="${p.id}"${p.id === filtroLog.projeto ? ' selected' : ''}>${esc(p.nome)}</option>`).join('')}</select>
      <label class="fraco mini log-meus"><input type="checkbox" data-log="meus"${filtroLog.meus ? ' checked' : ''}> Esconder o que eu fiz</label></div>
    ${h || '<p class="vazio">Ainda sem mudanças registadas.</p>'}`;
}
// os avisos (de lado) do que entrou no Log desde a última visita; ao vivo só o que não chega já como notificação
export function avisosLog(novos, { aviso, ir, verLog, aoVivo = false }) {
  const lista = aoVivo ? novos.filter((r) => !IMPACTO.has(r.tipo)) : novos;
  if (!lista.length) return;
  if (lista.length > 3) {
    aviso(`<b>${lista.length} alterações no Log${aoVivo ? '' : ' desde a tua última visita'}</b><br>${lista.slice(0, 4).map((r) => esc(r.texto)).join('<br>')}${lista.length > 4 ? '<br>…' : ''}`,
      { icone: 'novidades', duracao: 12, acoes: [{ rotulo: 'Ver o Log', fazer: verLog }] });
    return;
  }
  lista.slice().reverse().forEach((r) => aviso(`${esc(r.texto)}<br><span class="fraco mini">${esc(r.projeto ? nomeProjeto(r.projeto) : 'Hub')} · ${dia(r.criada_em)}</span>`,
    { icone: 'novidades', duracao: 10, acoes: r.ref_tipo && r.ref_id ? [{ rotulo: 'Ver', fazer: () => ir(r.projeto, r.ref_tipo, r.ref_id) }] : [] }));
}
