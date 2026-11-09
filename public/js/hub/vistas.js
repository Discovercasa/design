// As páginas do hub, desenhadas a partir do estado E (dados.js). Os botões levam data-acao; o app.js trata dos cliques.
import { E, projeto, nomeProjeto, checkpointsDe, tarefasDe, decisaoDaTarefa, decisoesDe, resumo, feitosDe, chave, documentosDe, anexosDe, notasDe, TIPOS_NOTA, podeMexerNota } from './dados.js';
import { img } from './imagens.js';
import { ic, esc, dia, diaCurto, iniciais, euros } from './util.js';
import { resumoInicio } from './social.js';

const ROTULO = { por_fazer: 'Por fazer', em_curso: 'Em curso', bloqueada: 'Bloqueada', concluida: 'Concluída', concluido: 'Concluído' };
export const abertos = new Set();   // checkpoints abertos (ficam abertos ao redesenhar)
export const notasAbertas = new Set();   // tarefas com a lista de notas aberta
let abertosIniciados = new Set();   // projetos cujos checkpoints "em curso" já abrimos por defeito

const saudacao = () => { const h = new Date().getHours(); return h < 6 ? 'Boa noite' : h < 13 ? 'Bom dia' : h < 20 ? 'Boa tarde' : 'Boa noite'; };
const novo = (tipo, id) => (E.novos.has(chave(tipo, id)) ? '<span class="chip novo">Novo</span>' : '');
const linkProjeto = (id) => `#/projeto/${(projeto(id) || {}).slug || id}`;
const appChip = (id) => (id ? `<a class="chip app" href="${linkProjeto(id)}" title="Esta tarefa poupa tempo com outra aplicação">${ic('app', 'ic-sm')}Sugerido: usar ${esc(nomeProjeto(id))}</a>` : '');
const custoChip = (c) => (c ? `<span class="chip custo">${ic('custo', 'ic-sm')}${esc(c)}</span>` : '');
const pillDecisao = (d) => (d ? `<button type="button" class="decisao-pill ${d.estado}" data-acao="ver-decisao" data-id="${d.id}">${ic('decisao', 'ic-sm')}${d.estado === 'aberta' ? 'Decisão' : 'Decidido'}</button>` : '');

// ---------------------------------------------------------------- Início
export function inicio() {
  const minhas = E.tarefas.filter((t) => t.responsavel_id === E.eu.id && t.estado !== 'concluida');
  const abertas = E.decisoes.filter((d) => d.estado === 'aberta');
  const feitos = feitosDe().slice(0, 8);
  const ligacoes = E.projetos.flatMap((p) => (p.ligacoes || []).map((l) => ({ de: p.id, ...l })));

  return `
  <div class="cabeca-pagina">
    <div class="saudacao">
      <h1>${saudacao()}${E.eu.nome ? ', ' + esc(E.eu.nome.split(' ')[0]) : ''}</h1>
      <p class="suave">Cada projeto da Discovercasa num só sítio: o que é, em que fase está, o que já foi feito e o que vem a seguir.</p>
      <div class="para-ti">
        <a class="chip" href="#/pessoal">${ic('pessoa', 'ic-sm')}<span class="num">${minhas.length}</span> ${minhas.length === 1 ? 'tarefa tua' : 'tarefas tuas'}</a>
        <a class="chip" href="#decisoes-abertas">${ic('decisao', 'ic-sm')}<span class="num">${abertas.length}</span> ${abertas.length === 1 ? 'decisão em aberto' : 'decisões em aberto'}</a>
      </div>
    </div>
    ${E.eu.editar ? `<button class="btn primario grande" type="button" data-acao="acrescentar">${ic('mais')}Acrescentar checkpoint ou tarefa</button>` : ''}
  </div>

  <section aria-labelledby="t-projetos">
    <div class="seccao-cabeca"><h2 id="t-projetos">Projetos</h2></div>
    <div class="projetos" id="lista-projetos">
      ${E.projetos.map((p) => {
        const r = resumo(p.id);
        return `<a class="projeto-linha" href="${linkProjeto(p.id)}">
          <div><h3>${esc(p.nome)}</h3><p class="suave pequeno">${esc(p.resumo)}</p></div>
          <div class="progresso">
            <div class="linha-topo"><span class="fase">${esc(p.fase)}</span><span class="num suave">${r.feitos} de ${r.total} checkpoints</span></div>
            <div class="barra${r.total && r.feitos === r.total ? ' ok' : ''}" role="img" aria-label="${r.feitos} de ${r.total} checkpoints concluídos"><i data-p="${r.total ? r.feitos / r.total : 0}"></i></div>
          </div>
          <div class="agora">
            ${r.atual ? `<span><span class="fraco">Agora</span> <b>${esc(r.atual.titulo)}</b></span>` : '<span class="fraco">Sem checkpoints em aberto</span>'}
            ${r.proxima ? `<span class="suave">Próximo passo: ${esc(r.proxima.titulo)}</span>` : ''}
            ${r.ultimo ? `<span class="fraco">Último feito a ${diaCurto(r.ultimo.dia)}: ${esc(r.ultimo.texto)}</span>` : ''}
          </div>
          <span class="seta">${ic('seta')}</span>
        </a>`;
      }).join('')}
    </div>
  </section>

  ${resumoInicio()}

  <section class="seccao" aria-labelledby="t-objetivos">
    <div class="seccao-cabeca"><h2 id="t-objetivos">Objetivos e o que vem a seguir</h2></div>
    <div class="rolar-x"><table class="tabela">
      <thead><tr><th>Projeto</th><th>Objetivo principal</th><th>A seguir</th></tr></thead>
      <tbody>${E.projetos.map((p) => `<tr><td><a href="${linkProjeto(p.id)}">${esc(p.nome)}</a></td><td>${esc((p.objetivos || [])[0] || '')}</td><td class="suave">${esc((p.futuro || [])[0] || '')}</td></tr>`).join('')}</tbody>
    </table></div>
  </section>

  <div class="grelha-2 seccao">
    <section aria-labelledby="t-ligacoes">
      <div class="seccao-cabeca"><h2 id="t-ligacoes">Como os projetos se ligam</h2></div>
      <div class="nota" style="margin-bottom:16px">${ic('info')}<p>Cada aplicação funciona sozinha: podes usar uma sem as outras. Só as juntamos quando isso poupa tempo e tokens; nesses casos a tarefa mostra <span class="chip app">${ic('app', 'ic-sm')}Sugerido: usar …</span>. O Build Your House e o Builder seguem hoje o método Discovercasa; no futuro devem servir também outros métodos.</p></div>
      <div class="ligacoes">
        ${ligacoes.map((l) => `<div class="ligacao"><a class="de" href="${linkProjeto(l.de)}">${esc(nomeProjeto(l.de))}</a>${ic('seta', 'ic-sm')}<a class="para" href="${linkProjeto(l.com)}">${esc(nomeProjeto(l.com))}</a><p>${esc(l.texto)}</p></div>`).join('')}
      </div>
    </section>
    <aside class="lateral">
      <section class="bloco-lateral" id="decisoes-abertas" aria-labelledby="t-dec">
        <h3 id="t-dec">Decisões em aberto</h3>
        ${abertas.length ? E.projetos.filter((p) => abertas.some((d) => d.projeto === p.id)).map((p) => {
          const ds = abertas.filter((d) => d.projeto === p.id);
          return `<div class="decisoes-projeto"><a class="decisoes-projeto-nome" href="${linkProjeto(p.id)}">${esc(p.nome)} <span class="fraco num">${ds.length}</span></a>
            <ul class="lista-simples">${ds.map((d) => `<li><span>${pillDecisao(d)}</span><span class="pequeno">${esc(d.pergunta)}</span></li>`).join('')}</ul></div>`;
        }).join('') : '<p class="suave pequeno">Nenhuma decisão à espera.</p>'}
      </section>
      <section class="bloco-lateral" aria-labelledby="t-feito">
        <h3 id="t-feito">Feito recentemente</h3>
        ${feitos.length ? `<ol class="tempo">${feitos.map((f) => `<li><time datetime="${f.dia}">${dia(f.dia)}</time><span>${esc(f.texto)}<br><span class="proj">${esc(nomeProjeto(f.projeto))}</span></span></li>`).join('')}</ol>`
          : '<p class="suave pequeno">Ainda nada concluído.</p>'}
      </section>
    </aside>
  </div>`;
}

// ---------------------------------------------------------------- página de um projeto
export function paginaProjeto(p) {
  const cps = checkpointsDe(p.id);
  if (!abertosIniciados.has(p.id)) {  // à primeira, abre o checkpoint em curso (ou o primeiro por fazer)
    abertosIniciados.add(p.id);
    const atual = cps.find((c) => c.estado === 'em_curso') || cps.find((c) => c.estado === 'por_fazer');
    if (atual) abertos.add(atual.id);
  }
  const r = resumo(p.id);
  const proximos = cps.filter((c) => c.estado !== 'concluido').flatMap((c) => tarefasDe(c.id).filter((t) => t.estado !== 'concluida')).slice(0, 4);
  const feitos = feitosDe(p.id);
  const decs = decisoesDe(p.id);

  return `
  <div class="projeto-cabeca">
    <div class="linha"><h1>${esc(p.nome)}</h1><span class="fase">${esc(p.fase)}</span></div>
    ${p.nome_antigo ? `<p class="fraco pequeno">Antes: ${esc(p.nome_antigo)}</p>` : ''}
    <p class="descricao">${esc(p.descricao)}</p>
    ${p.fase_detalhe ? `<details class="situacao"><summary>Ponto de situação das fases</summary><p class="suave pequeno">${esc(p.fase_detalhe)}</p></details>` : ''}
  </div>
  ${p.app ? `<div class="cta-app"><div><h3>${esc(p.nome)} está online</h3><p>Lê primeiro em que ponto está e o próximo passo; depois abre a aplicação.</p></div>
    <a class="btn primario grande" href="${esc(p.app.url)}" target="_blank" rel="noopener" title="Abre noutra janela">${esc(p.app.rotulo)}${ic('abrir')}<span class="so-leitor"> (abre noutra janela)</span></a></div>` : ''}

  <div class="grelha-2">
    <div>
      <section aria-labelledby="t-workflow">
        <div class="seccao-cabeca">
          <div><h2 id="t-workflow">Workflow</h2><p>Os checkpoints por ordem e as tarefas para chegar a cada um. <span class="num">${r.feitos} de ${r.total}</span> concluídos.</p></div>
          ${E.eu.editar ? `<div class="botoes"><button class="btn" type="button" data-acao="acrescentar" data-projeto="${p.id}" data-tipo="checkpoint">${ic('mais')}Checkpoint</button>
            <button class="btn" type="button" data-acao="acrescentar" data-projeto="${p.id}" data-tipo="tarefa"${cps.length ? '' : ' disabled title="Acrescenta primeiro um checkpoint"'}>${ic('mais')}Tarefa</button></div>` : ''}
        </div>
        ${cps.length ? `<ol class="workflow">${cps.map((c, i) => passo(c, i)).join('')}</ol>` : '<p class="vazio">Ainda sem checkpoints. Acrescenta o primeiro objetivo deste projeto.</p>'}
      </section>
      ${documentos(p)}
      ${p.teste_ar ? testeAR(p) : ''}
      ${p.pipeline ? pipeline(p) : ''}
    </div>

    <aside class="lateral">
      <section class="bloco-lateral"><h3>Próximos passos</h3>
        ${proximos.length ? `<ul class="lista-simples">${proximos.map((t) => `<li>${ic('alvo', 'ic-sm')}<a href="#/projeto/${p.slug}/t-${t.id}" class="pequeno" style="color:inherit">${esc(t.titulo)}</a></li>`).join('')}</ul>` : '<p class="suave pequeno">Nada em aberto.</p>'}
      </section>
      ${pedidos(p)}
      <section class="bloco-lateral"><h3>Objetivos</h3><ul class="lista-simples">${(p.objetivos || []).map((o) => `<li>${ic('certo', 'ic-sm')}<span class="pequeno">${esc(o)}</span></li>`).join('')}</ul></section>
      <section class="bloco-lateral"><h3>Futuro</h3><ul class="lista-simples">${(p.futuro || []).map((o) => `<li>${ic('seta', 'ic-sm')}<span class="pequeno">${esc(o)}</span></li>`).join('')}</ul></section>
      <section class="bloco-lateral"><h3>Decisões</h3>
        ${decs.length ? `<ul class="lista-simples">${decs.map((d) => `<li><span>${pillDecisao(d)}</span><span class="pequeno">${esc(d.pergunta)}</span></li>`).join('')}</ul>` : '<p class="suave pequeno">Nenhuma decisão registada.</p>'}
      </section>
      <section class="bloco-lateral"><h3>Feito</h3>
        ${feitos.length ? `<ol class="tempo">${feitos.slice(0, 10).map((f) => `<li><time datetime="${f.dia}">${dia(f.dia)}</time><span class="pequeno">${esc(f.texto)}</span></li>`).join('')}</ol>` : '<p class="suave pequeno">Ainda nada concluído.</p>'}
      </section>
      <section class="bloco-lateral"><h3>Ligações</h3>
        <ul class="lista-simples">${(p.ligacoes || []).map((l) => `<li>${ic('ligacao', 'ic-sm')}<span class="pequeno"><a href="${linkProjeto(l.com)}">${esc(nomeProjeto(l.com))}</a>: ${esc(l.texto)}</span></li>`).join('')}</ul>
        <p class="fraco mini" style="margin-top:10px">${esc(p.metodo || '')}</p>
      </section>
      <section class="bloco-lateral"><h3>Organização</h3>
        <dl class="organizacao"><dt>Código</dt><dd>${esc(p.organizacao.codigo)}</dd><dt>Publicado</dt><dd>${esc(p.organizacao.publicado)}</dd><dt>Ramo</dt><dd>${esc(p.organizacao.ramo)}</dd></dl>
      </section>
    </aside>
  </div>`;
}

// imagens anexadas (checkpoint, tarefa ou nota): miniaturas que abrem em grande no visor
export function galeria(alvo, id) {
  const as = anexosDe(alvo, id);
  if (!as.length) return '';
  return `<div class="galeria">${as.map((a, i) => `<button type="button" class="galeria-img" data-acao="ver-anexo" data-alvo="${alvo}" data-ref="${id}" data-i="${i}" title="${esc(a.nome_ficheiro)}">${a.miniatura ? img('anexos', a.miniatura, a.nome_ficheiro) : img('anexos', a.caminho, a.nome_ficheiro)}</button>`).join('')}</div>`;
}

function passo(c, i) {
  const ts = tarefasDe(c.id), feitas = ts.filter((t) => t.estado === 'concluida').length, aberto = abertos.has(c.id);
  return `<li class="passo ${c.estado}${aberto ? ' aberto' : ''}" id="cp-${c.id}">
    <div class="marco">${c.estado === 'concluido' ? ic('certo', 'ic-sm') : i + 1}</div>
    <div class="passo-corpo">
      <button class="passo-topo" type="button" data-acao="alternar-cp" data-id="${c.id}" aria-expanded="${aberto}" aria-controls="cpd-${c.id}">
        <div><h3>${esc(c.titulo)} ${novo('checkpoint', c.id)}</h3>
          <div class="meta"><span class="estado ${c.estado}">${ROTULO[c.estado]}</span><span class="num">${feitas}/${ts.length} tarefas</span>${c.concluido_em ? `<span>Concluído a ${dia(c.concluido_em)}</span>` : ''}</div></div>
        <span class="chev">${ic('baixo')}</span>
      </button>
      <div class="passo-detalhe" id="cpd-${c.id}"${aberto ? '' : ' hidden'}>
        ${c.descricao ? `<p class="passo-descricao">${esc(c.descricao)}</p>` : ''}
        ${galeria('checkpoint', c.id)}
        ${c.criterio_saida ? `<p class="criterio">${ic('alvo', 'ic-sm')}<span><b>Critério de saída:</b> ${esc(c.criterio_saida)}</span></p>` : ''}
        <div class="passo-tarefas">
          ${ts.map(tarefa).join('') || '<p class="suave pequeno" style="padding:14px 16px">Ainda sem tarefas.</p>'}
          ${E.eu.editar ? `<form class="form-linha" data-form="nova-tarefa" data-cp="${c.id}">
            <input class="campo" name="titulo" maxlength="300" placeholder="Nova tarefa…" aria-label="Nova tarefa neste checkpoint" required>
            <button class="btn" type="submit">${ic('mais', 'ic-sm')}Acrescentar</button></form>` : ''}
        </div>
        ${E.eu.editar ? `<div class="passo-acoes">
          <select class="seletor" data-acao="estado-cp" data-id="${c.id}" aria-label="Estado do checkpoint">${['por_fazer', 'em_curso', 'concluido'].map((e) => `<option value="${e}"${e === c.estado ? ' selected' : ''}>${ROTULO[e]}</option>`).join('')}</select>
          <button class="btn pequeno texto" type="button" data-acao="editar-cp" data-id="${c.id}">${ic('editar', 'ic-sm')}Editar checkpoint</button>
        </div>` : ''}
      </div>
    </div>
  </li>`;
}

function tarefa(t) {
  const d = decisaoDaTarefa(t.id);
  const posso = E.eu.editar || t.responsavel_id === E.eu.id;
  return `<div class="tarefa ${t.estado}" id="t-${t.id}">
    <input type="checkbox" class="visto" data-acao="concluir" data-id="${t.id}" aria-label="Concluída: ${esc(t.titulo)}"${t.estado === 'concluida' ? ' checked' : ''}${posso ? '' : ' disabled'}>
    <div>
      <p class="titulo">${esc(t.titulo)} ${novo('tarefa', t.id)}</p>
      ${t.descricao ? `<p class="descricao">${esc(t.descricao)}</p>` : ''}
      ${galeria('tarefa', t.id)}
      <div class="meta">
        <span class="estado ${t.estado}">${ROTULO[t.estado]}${t.concluida_em ? ' a ' + diaCurto(t.concluida_em) : ''}</span>
        ${t.responsavel_id ? `<span class="chip"><span class="avatar pequeno">${esc(iniciais(t.responsavel_nome))}</span>${esc(t.responsavel_nome)}</span>` : ''}
        ${appChip(t.app_sugerida)}${custoChip(t.custo)}
      </div>
      ${t.revisao ? notas(t) : ''}
    </div>
    <div class="direita">
      ${pillDecisao(d)}
      ${posso ? `<select class="seletor" data-acao="estado-tarefa" data-id="${t.id}" aria-label="Estado da tarefa">${['por_fazer', 'em_curso', 'bloqueada', 'concluida'].map((e) => `<option value="${e}"${e === t.estado ? ' selected' : ''}>${ROTULO[e]}</option>`).join('')}</select>` : ''}
      ${E.eu.editar ? `<button class="icone-botao" type="button" data-acao="editar-tarefa" data-id="${t.id}" aria-label="Editar tarefa" title="Editar">${ic('editar', 'ic-sm')}</button>` : ''}
    </div>
  </div>`;
}

// ---------------------------------------------------------------- notas de teste/revisão
function notas(t) {
  const ns = notasDe(t.id), abertas = ns.filter((n) => !n.resolvida), bugs = abertas.filter((n) => n.tipo === 'bug').length;
  const aberto = notasAbertas.has(t.id);
  const resumo = ns.length ? `<b>${abertas.length} por resolver</b>${bugs ? ` · ${bugs} ${bugs === 1 ? 'bug' : 'bugs'}` : ''} · ${ns.length} no total` : 'Ainda sem notas';
  return `<div class="notas-rev" id="notas-${t.id}">
    <button type="button" class="notas-resumo" data-acao="alternar-notas" data-id="${t.id}" aria-expanded="${aberto}" aria-controls="notas-corpo-${t.id}">
      ${ic('comentario', 'ic-sm')}<span>Notas do teste ou revisão: ${resumo}</span>${ic('baixo', 'ic-sm chev')}</button>
    <div class="notas-corpo" id="notas-corpo-${t.id}"${aberto ? '' : ' hidden'}>
      ${ns.length ? `<ul class="notas-lista">${ns.map((n) => linhaNota(n)).join('')}</ul>` : ''}
      <form class="nota-nova" data-form="nota" data-tarefa="${t.id}">
        <div class="segmentado" role="group" aria-label="Tipo de nota">${Object.entries(TIPOS_NOTA).map(([k, v], i) => `<button type="button" data-acao="tipo-nota" data-valor="${k}" aria-pressed="${i === 0}">${v}</button>`).join('')}</div>
        <input type="hidden" name="tipo" value="bug">
        <textarea class="campo" name="texto" rows="2" maxlength="4000" required placeholder="O que encontraste? Podes colar capturas de ecrã (Ctrl+V)." aria-label="Nota"></textarea>
        <div class="nota-nova-fundo">
          <label class="btn pequeno texto">${ic('imagem', 'ic-sm')}Imagens<input type="file" name="imagens-nota" data-tarefa="${t.id}" multiple accept="image/*" class="so-leitor"></label>
          <ul class="escolhidas" data-escolhidas-nota="${t.id}"></ul>
          <button class="btn pequeno primario" type="submit">Acrescentar nota</button>
        </div>
      </form>
    </div>
  </div>`;
}
function linhaNota(n) {
  const pode = podeMexerNota(n), tarefa = n.tarefa_criada_id ? E.tarefas.find((x) => x.id === n.tarefa_criada_id) : null;
  return `<li class="nota ${n.tipo}${n.resolvida ? ' resolvida' : ''}" id="nota-${n.id}">
    <input type="checkbox" class="visto" data-acao="resolver-nota" data-id="${n.id}" aria-label="Resolvida"${n.resolvida ? ' checked' : ''}${pode ? '' : ' disabled'}>
    <div class="nota-corpo">
      <p class="nota-texto"><span class="nota-tipo ${n.tipo}">${TIPOS_NOTA[n.tipo]}</span> ${esc(n.texto)}</p>
      ${galeria('nota', n.id)}
      <p class="fraco mini">${esc(n.autor_nome || 'Equipa')} · ${dia(n.criado_em)}${n.resolvida ? ` · resolvida${n.resolvida_por_nome ? ' por ' + esc(n.resolvida_por_nome) : ''}${n.resolvida_em ? ' a ' + diaCurto(n.resolvida_em) : ''}` : ''}${tarefa ? ` · <a href="#/projeto/${projeto(tarefa.projeto).slug}/t-${tarefa.id}">passou a tarefa</a>` : ''}</p>
    </div>
    <div class="nota-acoes">
      ${E.eu.editar && !n.tarefa_criada_id && !n.resolvida ? `<button class="btn pequeno texto" type="button" data-acao="passar-nota" data-id="${n.id}" title="Cria uma tarefa neste checkpoint com o texto da nota">Passar a tarefa</button>` : ''}
      ${pode ? `<button class="icone-botao" type="button" data-acao="apagar-nota" data-id="${n.id}" aria-label="Apagar nota" title="Apagar">${ic('apagar', 'ic-sm')}</button>` : ''}
    </div>
  </li>`;
}

// ---------------------------------------------------------------- documentos do projeto (informativos e adicionais)
const tamanho = (b) => (b >= 1e6 ? `${(b / 1e6).toLocaleString('pt-PT', { maximumFractionDigits: 1 })} MB` : `${Math.max(1, Math.round(b / 1e3))} kB`);
const extensao = (nome) => (String(nome).split('.').pop() || '').toUpperCase().slice(0, 4);
function linhaDoc(d) {
  const titulo = d.titulo.includes(' · ') ? d.titulo.split(' · ').slice(1).join(' · ') : d.titulo;
  return `<li class="doc" id="doc-${d.id}">
    <span class="doc-tipo" aria-hidden="true">${esc(extensao(d.nome_ficheiro))}</span>
    <div class="doc-corpo"><p class="doc-titulo">${esc(titulo)} ${novo('documento', d.id)}</p>
      <p class="doc-meta">${esc(d.nome_ficheiro)} · ${tamanho(d.tamanho)} · ${dia(d.criado_em)} · ${esc(d.criado_por_nome || 'Equipa')}</p>
      ${d.descricao ? `<p class="doc-desc">${esc(d.descricao)}</p>` : ''}</div>
    <div class="doc-acoes"><button class="btn pequeno" type="button" data-acao="abrir-doc" data-id="${d.id}">${ic('abrir', 'ic-sm')}Abrir</button>
      ${E.eu.editar ? `<button class="icone-botao" type="button" data-acao="apagar-doc" data-id="${d.id}" aria-label="Apagar ${esc(titulo)}" title="Apagar">${ic('apagar', 'ic-sm')}</button>` : ''}</div>
  </li>`;
}
function grupoDocs(tipo, titulo, explica, p) {
  const docs = documentosDe(p.id, tipo);
  const grupos = new Map();   // "Torres Vedras · …" agrupa por obra / origem
  for (const d of docs) { const g = d.titulo.includes(' · ') ? d.titulo.split(' · ')[0] : ''; if (!grupos.has(g)) grupos.set(g, []); grupos.get(g).push(d); }
  const corpo = !docs.length ? `<p class="vazio pequeno">Ainda sem documentos ${tipo === 'informativo' ? 'informativos' : 'adicionais'}.</p>`
    : [...grupos].map(([g, lista]) => g
      ? `<details class="doc-grupo"${lista.length <= 4 ? ' open' : ''}><summary>${esc(g)} <span class="fraco num">${lista.length}</span></summary><ul class="docs-lista">${lista.map(linhaDoc).join('')}</ul></details>`
      : `<ul class="docs-lista">${lista.map(linhaDoc).join('')}</ul>`).join('');
  return `<div class="docs-tipo"><div class="docs-tipo-cabeca"><h3>${titulo} <span class="fraco num">${docs.length}</span></h3><p class="fraco mini">${explica}</p></div>${corpo}</div>`;
}
function documentos(p) {
  return `<section class="seccao" id="documentos" aria-labelledby="t-docs">
    <div class="seccao-cabeca"><div><h2 id="t-docs">Documentos</h2><p>Tudo o que foi partilhado com este projeto. Ficam guardados em privado: só quem entra no Design os abre.</p></div>
      ${E.eu.editar ? `<button class="btn" type="button" data-acao="acrescentar-doc" data-projeto="${p.id}">${ic('mais')}Documento</button>` : ''}</div>
    <div class="docs-grelha">
      ${grupoDocs('informativo', 'Documentos informativos', 'O que o projeto é: especificações, planos, decisões escritas.', p)}
      ${grupoDocs('adicional', 'Documentos adicionais', 'Conhecimento extra para o projeto: desenhos de obras, fichas, fotografias.', p)}
    </div>
  </section>`;
}
// ---------------------------------------------------------------- Step Inside: teste do AR no telemóvel
// USDZ -> iPhone / iPad (AR Quick Look: an <a rel="ar"> whose only child is an image, opened in Safari);
// GLB -> Android (Google Scene Viewer through an intent: link). The links are signed and temporary; app.js fills them.
const IMG_AR_IPHONE = "data:image/svg+xml," + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="196" height="40" viewBox="0 0 196 40"><rect width="196" height="40" rx="9" fill="#1f2937"/><text x="98" y="25" font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="14" font-weight="600" fill="#fff" text-anchor="middle">Ver em AR · iPhone</text></svg>');
function linhaAR(d) {
  const ios = /\.usdz$/i.test(d.nome_ficheiro);
  const titulo = d.titulo.includes(' · ') ? d.titulo.split(' · ').slice(1).join(' · ') : d.titulo;
  const botao = ios
    ? `<a rel="ar" href="#" class="ar-ios" data-ar="${d.id}" data-ar-tipo="ios" aria-disabled="true"><img src="${IMG_AR_IPHONE}" alt="Ver em AR no iPhone: ${esc(titulo)}" width="196" height="40"></a>`
    : `<button class="btn pequeno" type="button" data-acao="ver-3d" data-id="${d.id}">${ic('cubo', 'ic-sm')}Ver em 3D</button>
       <a href="#" class="btn primario pequeno" data-ar="${d.id}" data-ar-tipo="android" aria-disabled="true">${ic('app', 'ic-sm')}Ver em AR · Android</a>`;
  return `<li class="doc" id="doc-${d.id}">
    <span class="doc-tipo" aria-hidden="true">${esc(extensao(d.nome_ficheiro))}</span>
    <div class="doc-corpo"><p class="doc-titulo">${esc(titulo)} ${novo('documento', d.id)}</p>
      <p class="doc-meta">${esc(d.nome_ficheiro)} · ${tamanho(d.tamanho)} · ${ios ? 'iPhone / iPad (Quick Look)' : 'Android (Scene Viewer)'}</p>
      ${d.descricao ? `<p class="doc-desc">${esc(d.descricao)}</p>` : ''}</div>
    <div class="doc-acoes">${botao}
      ${E.eu.editar ? `<button class="icone-botao" type="button" data-acao="apagar-doc" data-id="${d.id}" aria-label="Apagar ${esc(titulo)}" title="Apagar">${ic('apagar', 'ic-sm')}</button>` : ''}</div>
  </li>`;
}
function testeAR(p) {
  const docs = documentosDe(p.id, 'ar');
  const grupos = new Map();   // "Torres Vedras · casa (1:1)" agrupa por obra
  for (const d of docs) { const g = d.titulo.includes(' · ') ? d.titulo.split(' · ')[0] : 'Modelos'; if (!grupos.has(g)) grupos.set(g, []); grupos.get(g).push(d); }
  const tarefa = E.tarefas.find((t) => t.projeto === p.id && /iPhone e um Android/.test(t.titulo));
  const lista = !docs.length
    ? `<p class="vazio pequeno">Ainda sem modelos AR. ${E.eu.editar ? 'Carrega os ficheiros <code>.usdz</code> (iPhone) e <code>.glb</code> (Android) com o botão «Modelo AR».' : ''}</p>`
    : [...grupos].map(([g, l]) => `<details class="doc-grupo" open><summary>${esc(g)} <span class="fraco num">${l.length}</span></summary><ul class="docs-lista">${l.map(linhaAR).join('')}</ul></details>`).join('');
  return `<section class="seccao" id="teste-ar" aria-labelledby="t-ar">
    <div class="seccao-cabeca"><div><h2 id="t-ar">Teste do AR no telemóvel</h2><p>Abre esta página no telemóvel e toca no botão do modelo: a casa aparece à escala real no sítio onde apontares. Os modelos ficam em privado e cada link dura uma hora.</p></div>
      ${E.eu.editar ? `<button class="btn" type="button" data-acao="acrescentar-doc" data-projeto="${p.id}" data-tipo-doc="ar">${ic('mais')}Modelo AR</button>` : ''}</div>
    <div class="docs-grelha">
      <div class="docs-tipo"><div class="docs-tipo-cabeca"><h3>Modelos <span class="fraco num">${docs.length}</span></h3><p class="fraco mini">«casa»: à escala 1:1, pousa no chão e anda-se à volta. «maquete»: com o terreno, para ver em ponto pequeno. Nas casas com mais de um piso: «piso N (1:1)» é só esse piso, pousado no chão para andar lá dentro; «maquete do piso N» é a casa aberta até esse piso.</p></div>${lista}</div>
      <div class="docs-tipo"><div class="docs-tipo-cabeca"><h3>Como testar</h3><p class="fraco mini">iPhone ou iPad: abre no Safari e toca em «Ver em AR · iPhone». Android: abre no Chrome e toca em «Ver em AR · Android» (precisa da app Google e de um telemóvel com ARCore). Sem AR (no computador, ou num telemóvel sem AR): «Ver em 3D» abre o modelo aqui, para rodar e aproximar.</p></div>
        <ul class="lista-simples">
          ${['A casa fica do tamanho certo? (mede uma porta: ≈ 2,1 m)', 'Assenta no chão, sem flutuar nem afundar?', 'Está virada como esperavas (fachadas, entrada)?', 'Quanto tempo demora a abrir?', 'Os materiais parecem reais ou «de plástico»?'].map((x) => `<li>${ic('certo', 'ic-sm')}<span class="pequeno">${x}</span></li>`).join('')}
        </ul>
        ${tarefa ? `<p class="pequeno" style="margin-top:10px"><a href="#/projeto/${p.slug}/t-${tarefa.id}">${ic('comentario', 'ic-sm')}Escrever o resultado do teste na tarefa «${esc(tarefa.titulo)}»</a></p>` : ''}
      </div>
    </div>
  </section>`;
}

// tarefas de outros projetos que sugerem usar esta app: aparecem também aqui
function pedidos(p) {
  const lista = E.tarefas.filter((t) => t.app_sugerida === p.id && t.projeto !== p.id && t.estado !== 'concluida');
  if (!lista.length) return '';
  return `<section class="bloco-lateral"><h3>Pedidos de outros projetos <span class="fraco num">${lista.length}</span></h3>
    <p class="fraco mini" style="margin:-6px 0 10px">Tarefas noutros projetos que sugerem usar o ${esc(p.nome)}.</p>
    <ul class="lista-simples">${lista.slice(0, 8).map((t) => `<li>${ic('app', 'ic-sm')}<span class="pequeno"><a href="#/projeto/${projeto(t.projeto).slug}/t-${t.id}" style="color:inherit">${esc(t.titulo)}</a><br><span class="fraco mini">${esc(nomeProjeto(t.projeto))} · ${ROTULO[t.estado]}</span></span></li>`).join('')}</ul></section>`;
}

// ---------------------------------------------------------------- Step Inside: pipeline com custos e calculadora
function pipeline(p) {
  return `
  <section class="seccao" id="pipeline" aria-labelledby="t-pipeline">
    <div class="seccao-cabeca"><div><h2 id="t-pipeline">Pipeline e custos</h2><p>Do documento ao cliente, etapa a etapa: o que faz, quanto custa e o que ter em conta. Câmbio 1 USD = ${p.cambio.usd_eur.toLocaleString('pt-PT')} € (${dia(p.cambio.dia)}); preços sem IVA, a confirmar antes de contratar.</p></div></div>
    <ol class="pipeline">${p.pipeline.map((e) => `<li class="etapa"><div class="marco"></div><div class="etapa-corpo">
      <div class="linha"><h3>${esc(e.nome)}</h3>${appChip(e.app)}</div>
      <p class="suave pequeno">${esc(e.faz)}</p>
      <div class="linha">${custoChip(e.custo)}${e.espaco ? `<span class="chip">${ic('pasta', 'ic-sm')}${esc(e.espaco)}</span>` : ''}</div>
      <ul>${e.atencao.map((a) => `<li>${esc(a)}</li>`).join('')}</ul>
    </div></li>`).join('')}</ol>
  </section>

  <section class="seccao" id="calculadora" aria-labelledby="t-calc">
    <div class="seccao-cabeca"><div><h2 id="t-calc">Quanto custa por mês</h2><p>GPU e armazenamento R2. ${esc(p.custos_excluidos)}</p></div></div>
    <form class="painel painel-pad" data-form="calculadora" onsubmit="return false">
      <div class="calculadora">
        <label>Sessões por mês<input class="campo num" type="number" name="sessoes" min="0" max="100000" value="50"></label>
        <label>Minutos por sessão<input class="campo num" type="number" name="minutos" min="1" max="600" value="30"></label>
        <label>Minutos extra faturados (arranque, espera)<input class="campo num" type="number" name="extra" min="0" max="120" value="0"></label>
        <label>GPU<select class="campo" name="tarifa"><option value="0.89">RTX 4090 Secure · 0,89 USD/h</option><option value="0.34">RTX 4090 Community · 0,34 USD/h</option></select></label>
        <label>Casas guardadas<input class="campo num" type="number" name="casas" min="0" max="10000" value="10"></label>
        <label>GB por casa<input class="campo num" type="number" name="gb" min="1" max="100" value="12"></label>
      </div>
      <div class="resultado" id="calc-resultado" aria-live="polite"></div>
    </form>
    <div class="rolar-x" style="margin-top:24px"><table class="tabela">
      <caption class="so-leitor">Cenários de referência da especificação</caption>
      <thead><tr><th>Cenário</th><th>Pressupostos</th><th class="num">GPU</th><th class="num">R2</th><th class="num">Subtotal</th></tr></thead>
      <tbody>${p.cenarios.map((c) => `<tr><td>${esc(c.nome)}</td><td class="suave">${esc(c.pressupostos)}</td><td class="num">${esc(c.gpu)}</td><td class="num">${esc(c.r2)}</td><td class="num">${esc(c.total)}</td></tr>`).join('')}</tbody>
    </table></div>
  </section>`;
}
export function calcular(form, cambio) {
  const v = (n) => Math.max(0, Number(form.elements[n].value) || 0);
  const horas = (v('sessoes') * (v('minutos') + v('extra'))) / 60;
  const gpu = horas * v('tarifa') * cambio;
  const gbTotal = v('casas') * v('gb');
  const r2 = Math.max(0, gbTotal - 10) * 0.015 * cambio;
  const porSessao = v('sessoes') ? gpu / v('sessoes') : 0;
  form.querySelector('#calc-resultado').innerHTML = `
    <div><span>Horas de GPU</span><b>${horas.toLocaleString('pt-PT', { maximumFractionDigits: 1 })} h</b></div>
    <div><span>GPU por mês</span><b>${euros(gpu)}</b></div>
    <div><span>Por sessão</span><b>${euros(porSessao)}</b></div>
    <div><span>R2 (${gbTotal.toLocaleString('pt-PT')} GB)</span><b>${euros(r2)}</b></div>
    <div><span>Subtotal conhecido</span><b>${euros(gpu + r2)}</b></div>`;
}

// ---------------------------------------------------------------- área pessoal
export function pessoal() {
  const minhas = E.tarefas.filter((t) => t.responsavel_id === E.eu.id);
  const grupo = (titulo, lista) => `<section class="bloco-lateral"><h3>${titulo} <span class="fraco num">${lista.length}</span></h3>
    ${lista.length ? `<ul class="lista-simples">${lista.map((t) => `<li>${ic('alvo', 'ic-sm')}<span class="pequeno"><a href="#/projeto/${projeto(t.projeto).slug}/t-${t.id}" style="color:inherit">${esc(t.titulo)}</a><br><span class="fraco mini">${esc(nomeProjeto(t.projeto))}</span></span></li>`).join('')}</ul>` : '<p class="suave pequeno">Nada aqui.</p>'}</section>`;
  const decididas = E.decisoes.filter((d) => d.decidida_por === E.eu.id);
  return `
  <div class="cabeca-pagina"><div class="texto"><h1>Área pessoal</h1><p class="suave">As tarefas atribuídas a ti, em todos os projetos, e as decisões que tomaste.</p></div></div>
  <div class="cartoes-pessoal">
    ${grupo('Em curso', minhas.filter((t) => t.estado === 'em_curso'))}
    ${grupo('Por fazer', minhas.filter((t) => t.estado === 'por_fazer'))}
    ${grupo('Bloqueadas', minhas.filter((t) => t.estado === 'bloqueada'))}
    ${grupo('Concluídas', minhas.filter((t) => t.estado === 'concluida'))}
  </div>
  <section class="seccao"><div class="seccao-cabeca"><h2>Decisões que tomaste</h2></div>
    ${decididas.length ? `<ul class="lista-simples">${decididas.map((d) => `<li>${pillDecisao(d)}<span class="pequeno">${esc(d.pergunta)} <span class="fraco">· ${dia(d.decidida_em)}</span></span></li>`).join('')}</ul>` : '<p class="vazio">Ainda não tomaste nenhuma decisão.</p>'}
  </section>`;
}

// ---------------------------------------------------------------- definições
export function definicoes(podeInstalar) {
  const tema = (localStorage.getItem('hub-tema') || 'sistema');
  const movimento = localStorage.getItem('hub-movimento') || 'normal';
  const seg = (nome, valor, opcoes) => `<div class="segmentado" role="group">${opcoes.map(([v, r]) => `<button type="button" data-acao="${nome}" data-valor="${v}" aria-pressed="${v === valor}">${r}</button>`).join('')}</div>`;
  return `
  <div class="cabeca-pagina"><div class="texto"><h1>Definições</h1><p class="suave">O teu nome na equipa e o aspeto do hub neste aparelho.</p></div></div>
  <div style="max-width:720px">
    <form class="definicao" data-form="nome">
      <div><h3>O teu nome</h3><p>É o nome que a equipa vê nas tarefas, decisões e notificações.</p>
        <input class="campo" name="nome" maxlength="120" value="${esc(E.eu.nome)}" style="margin-top:10px;max-width:320px" aria-label="O teu nome" required></div>
      <button class="btn" type="submit">Guardar nome</button>
    </form>
    <div class="definicao"><div><h3>Tema</h3><p>Claro, escuro ou o do sistema.</p></div>${seg('tema', tema, [['sistema', 'Sistema'], ['light', 'Claro'], ['dark', 'Escuro']])}</div>
    <div class="definicao"><div><h3>Animações</h3><p>Reduzidas: o hub muda sem movimento.</p></div>${seg('movimento', movimento, [['normal', 'Normais'], ['reduzido', 'Reduzidas']])}</div>
    <div class="definicao"><div><h3>Acesso</h3><p>Decidido no Hub (permissão "Design").</p></div><span class="fase">${E.eu.editar ? 'Editar' : 'Ver'}</span></div>
    ${podeInstalar ? `<div class="definicao"><div><h3>Instalar como app</h3><p>Abre o Design como uma aplicação neste aparelho.</p></div><button class="btn" type="button" data-acao="instalar">${ic('instalar', 'ic-sm')}Instalar</button></div>` : ''}
  </div>`;
}

// ---------------------------------------------------------------- novidades
export function novidades(lista) {
  return `
  <div class="cabeca-pagina"><div class="texto"><h1>Novidades</h1><p class="suave">O que mudou no hub do Design.</p></div></div>
  <div style="max-width:820px">${lista.map((n) => `<article class="novidade"><time class="fraco pequeno num" datetime="${n.dia}">${dia(n.dia)}</time>
    <div><h3>${esc(n.titulo)}</h3><ul>${n.itens.map((i) => `<li>${esc(i)}</li>`).join('')}</ul></div></article>`).join('')}</div>`;
}

export function esqueleto() {
  return `<div class="cabeca-pagina"><div class="texto"><div class="esqueleto" style="width:320px;height:40px"></div></div></div>${'<div class="esqueleto"></div>'.repeat(5)}`;
}
