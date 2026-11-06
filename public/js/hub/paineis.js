// Painéis e diálogos: notificações, menu do perfil, sugestões (gaveta), decisões, acrescentar/editar checkpoints e tarefas.
import { E, projeto, nomeProjeto, checkpointsDe, naoLidas, anexosDe } from './dados.js';
import { img } from './imagens.js';
import { ic, esc, dia, ha, iniciais, abrirDialogo } from './util.js';

const ESTADOS_T = { por_fazer: 'Por fazer', em_curso: 'Em curso', bloqueada: 'Bloqueada', concluida: 'Concluída' };
const ESTADOS_C = { por_fazer: 'Por fazer', em_curso: 'Em curso', concluido: 'Concluído' };
const opcoes = (mapa, atual) => Object.entries(mapa).map(([k, v]) => `<option value="${k}"${k === atual ? ' selected' : ''}>${esc(v)}</option>`).join('');
const opcoesProjetos = (atual, vazio) => (vazio ? `<option value="">${vazio}</option>` : '') + E.projetos.map((p) => `<option value="${p.id}"${p.id === atual ? ' selected' : ''}>${esc(p.nome)}</option>`).join('');
const opcoesPessoas = (atual) => '<option value="">Sem responsável</option>' + E.perfis.filter((p) => p.nome).map((p) => `<option value="${p.id}"${p.id === atual ? ' selected' : ''}>${esc(p.nome)}</option>`).join('');
const cabeca = (titulo, sub = '') => `<div class="dlg-cabeca"><div><h2>${titulo}</h2>${sub ? `<p class="suave pequeno" style="margin-top:4px">${sub}</p>` : ''}</div>
  <button class="icone-botao" type="button" data-acao="fechar-dlg" aria-label="Fechar">${ic('fechar')}</button></div>`;

// ---------------------------------------------------------------- notificações
export function htmlNotificacoes() {
  const nl = new Set(naoLidas().map((n) => n.id));
  return `<div class="pop-cabeca"><h2>Notificações</h2>${nl.size ? '<button class="btn pequeno texto" type="button" data-acao="ler-todas">Marcar como lidas</button>' : ''}</div>
    <div class="pop-corpo">${E.notificacoes.length ? E.notificacoes.map((n) => `<button type="button" class="notif${nl.has(n.id) ? ' nao-lida' : ''}" data-acao="ir-notif" data-projeto="${esc(n.projeto || '')}" data-ref="${esc(n.ref_tipo || '')}" data-id="${n.ref_id || ''}">
      <span class="ponto" aria-hidden="true"></span><span><p>${esc(n.texto)}</p><p class="quando">${esc(n.projeto ? nomeProjeto(n.projeto) : 'Redes sociais')} · ${ha(n.criada_em)}${nl.has(n.id) ? ' · <span class="so-leitor">não lida</span>' : ''}</p></span></button>`).join('')
      : '<p class="suave pequeno" style="padding:16px">Sem notificações. Aparecem aqui quando alguém atribui, muda ou conclui uma tarefa.</p>'}</div>`;
}

// ---------------------------------------------------------------- menu do perfil
export function htmlPerfil(novidadeNova) {
  return `<div class="menu">
    <div class="menu-cabeca"><span class="avatar">${esc(iniciais(E.eu.nome))}</span><div><b>${esc(E.eu.nome || 'Sem nome')}</b><p class="fraco mini">Acesso: ${E.eu.editar ? 'editar' : 'ver'}</p></div></div>
    <a href="#/pessoal" role="menuitem">${ic('pessoa')}Área pessoal</a>
    <a href="#/definicoes" role="menuitem">${ic('definicoes')}Definições</a>
    <a href="#/novidades" role="menuitem">${ic('novidades')}Novidades${novidadeNova ? '<span class="ponto-novo" aria-label="Há novidades"></span>' : ''}</a>
    <div class="separador"></div>
    <button type="button" role="menuitem" data-acao="sair">${ic('sair')}Sair</button>
  </div>`;
}

// ---------------------------------------------------------------- acrescentar / editar
// posição de um checkpoint novo (1..n+1, por defeito no fim) ou de um que já existe (1..n)
export function opcoesPosicao(pid, atualId) {
  const cps = checkpointsDe(pid).filter((c) => c.id !== atualId);
  const atualPos = atualId ? checkpointsDe(pid).findIndex((c) => c.id === atualId) + 1 : cps.length + 1;
  const ops = cps.map((c, i) => `<option value="${i + 1}"${i + 1 === atualPos ? ' selected' : ''}>${i + 1} · antes de «${esc(c.titulo)}»</option>`);
  ops.push(`<option value="${cps.length + 1}"${cps.length + 1 === atualPos ? ' selected' : ''}>${cps.length + 1} · no fim</option>`);
  return ops.join('');
}

export function dlgAcrescentar(projetoId, cpId, tipoInicial) {
  const pid = projetoId || E.projetos[0].id;
  const tarefa = tipoInicial ? tipoInicial === 'tarefa' : !!cpId;
  return `<form data-form="acrescentar">${cabeca('Acrescentar', 'Um checkpoint é uma meta do projeto; uma tarefa é um passo pequeno dentro de um checkpoint.')}
    <div class="dlg-corpo">
      <div class="segmentado" role="group" aria-label="O que acrescentar">
        <button type="button" data-acao="tipo-novo" data-valor="tarefa" aria-pressed="${tarefa}">Tarefa</button>
        <button type="button" data-acao="tipo-novo" data-valor="checkpoint" aria-pressed="${!tarefa}">Checkpoint</button>
      </div>
      <input type="hidden" name="tipo" value="${tarefa ? 'tarefa' : 'checkpoint'}">
      <div class="grelha-campos">
        <label class="campo-grupo"><span>Projeto</span><select class="campo" name="projeto" data-acao="projeto-novo">${opcoesProjetos(pid)}</select></label>
        <label class="campo-grupo so-tarefa"${tarefa ? '' : ' hidden'}><span>Checkpoint</span><select class="campo" name="checkpoint">${opcoesCheckpoints(pid, cpId)}</select></label>
        <label class="campo-grupo so-checkpoint"${tarefa ? ' hidden' : ''}><span>Posição no workflow</span><select class="campo" name="posicao">${opcoesPosicao(pid)}</select></label>
      </div>
      <label class="campo-grupo"><span>Título</span><input class="campo" name="titulo" maxlength="200" required autocomplete="off"></label>
      <label class="campo-grupo"><span>Descrição <small>(opcional)</small></span><textarea class="campo" name="descricao" maxlength="4000"></textarea></label>
      <label class="campo-grupo so-checkpoint"${tarefa ? ' hidden' : ''}><span>Critério de saída <small>(opcional: o que tem de ser verdade para o dar como concluído)</small></span><textarea class="campo" name="criterio_saida" maxlength="2000" rows="2"></textarea></label>
      <label class="aprovar so-tarefa"${tarefa ? '' : ' hidden'}><input type="checkbox" class="visto" name="revisao"><span><b>Tarefa de teste ou revisão</b><br><span class="fraco mini">Mostra uma lista de notas (bugs, coisas a mudar, coisas a fazer). As imagens juntam-se depois, ao editar.</span></span></label>
      <div class="grelha-campos so-tarefa"${tarefa ? '' : ' hidden'}>
        <label class="campo-grupo"><span>Responsável</span><select class="campo" name="responsavel">${opcoesPessoas(null)}</select></label>
        <label class="campo-grupo"><span>App sugerida <small>(se poupa tempo)</small></span><select class="campo" name="app">${opcoesProjetos(null, 'Nenhuma')}</select></label>
        <label class="campo-grupo"><span>Custo <small>(opcional)</small></span><input class="campo" name="custo" maxlength="300" placeholder="ex.: ≈ 0,79 €/h"></label>
      </div>
      <p class="erro-msg pequeno" role="alert"></p>
    </div>
    <div class="dlg-rodape"><button class="btn texto" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">Acrescentar</button></div>
  </form>`;
}
export function opcoesCheckpoints(pid, atual) {
  const cps = checkpointsDe(pid);
  if (!cps.length) return '<option value="">Este projeto ainda não tem checkpoints</option>';
  const def = atual || (cps.find((c) => c.estado === 'em_curso') || cps.find((c) => c.estado !== 'concluido') || cps[0]).id;
  return cps.map((c) => `<option value="${c.id}"${c.id === def ? ' selected' : ''}>${esc(c.titulo)}</option>`).join('');
}

// imagens de um checkpoint ou de uma tarefa no diálogo de edição: arrastar, colar (Ctrl+V) ou escolher
export function htmlAnexosEdicao(alvo, id) {
  const as = anexosDe(alvo, id);
  return `<div class="anexos-edicao" data-alvo="${alvo}" data-ref="${id}">
    <span class="campo-grupo-titulo">Imagens <small class="fraco">(${as.length})</small></span>
    ${as.length ? `<ul class="anexos-lista">${as.map((a, i) => `<li><button type="button" class="galeria-img" data-acao="ver-anexo" data-alvo="${alvo}" data-ref="${id}" data-i="${i}" title="${esc(a.nome_ficheiro)}">${a.miniatura ? img('anexos', a.miniatura, a.nome_ficheiro) : img('anexos', a.caminho, a.nome_ficheiro)}</button>
      <button type="button" class="icone-botao anexo-tirar" data-acao="apagar-anexo" data-id="${a.id}" aria-label="Tirar ${esc(a.nome_ficheiro)}">${ic('fechar', 'ic-sm')}</button></li>`).join('')}</ul>` : ''}
    <label class="anexos-zona">${ic('imagem')}<span><b>Arrasta imagens para aqui</b>, cola-as (Ctrl+V) ou <u>escolhe do computador</u>.<br><span class="fraco mini">Ficam guardadas logo; as fotos grandes ficam com 2048 px.</span></span>
      <input type="file" name="anexos-ficheiros" data-alvo="${alvo}" data-ref="${id}" multiple accept="image/*" class="so-leitor"></label>
    <p class="anexos-progresso pequeno suave" role="status"></p>
  </div>`;
}

export function dlgEditarTarefa(t) {
  return `<form data-form="editar-tarefa" data-id="${t.id}">${cabeca('Editar tarefa', esc(nomeProjeto(t.projeto)))}
    <div class="dlg-corpo">
      <label class="campo-grupo"><span>Título</span><input class="campo" name="titulo" maxlength="300" required value="${esc(t.titulo)}"></label>
      <label class="campo-grupo"><span>Descrição</span><textarea class="campo" name="descricao" maxlength="4000">${esc(t.descricao)}</textarea></label>
      <div class="grelha-campos">
        <label class="campo-grupo"><span>Checkpoint</span><select class="campo" name="checkpoint">${opcoesCheckpoints(t.projeto, t.checkpoint_id)}</select></label>
        <label class="campo-grupo"><span>Estado</span><select class="campo" name="estado">${opcoes(ESTADOS_T, t.estado)}</select></label>
        <label class="campo-grupo"><span>Responsável</span><select class="campo" name="responsavel">${opcoesPessoas(t.responsavel_id)}</select></label>
        <label class="campo-grupo"><span>App sugerida</span><select class="campo" name="app">${opcoesProjetos(t.app_sugerida, 'Nenhuma')}</select></label>
        <label class="campo-grupo"><span>Custo</span><input class="campo" name="custo" maxlength="300" value="${esc(t.custo)}"></label>
      </div>
      <label class="aprovar"><input type="checkbox" class="visto" name="revisao"${t.revisao ? ' checked' : ''}><span><b>Tarefa de teste ou revisão</b><br><span class="fraco mini">Mostra uma lista de notas (bugs, coisas a mudar, coisas a fazer) onde a equipa regista o que encontrou.</span></span></label>
      ${htmlAnexosEdicao('tarefa', t.id)}
      <p class="fraco mini">Acrescentada por ${esc(t.criado_por_nome || 'Equipa')} a ${dia(t.criado_em)}.</p>
      <p class="erro-msg pequeno" role="alert"></p>
    </div>
    <div class="dlg-rodape" style="justify-content:space-between">
      <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn texto perigo" type="button" data-acao="apagar-tarefa" data-id="${t.id}">${ic('apagar', 'ic-sm')}Apagar</button>
        ${E.decisoes.some((d) => d.tarefa_id === t.id) ? '' : `<button class="btn texto" type="button" data-acao="nova-decisao" data-tarefa="${t.id}">${ic('decisao', 'ic-sm')}Acrescentar decisão</button>`}</div>
      <div style="display:flex;gap:8px"><button class="btn texto" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">Guardar</button></div>
    </div>
  </form>`;
}

export function dlgEditarCheckpoint(c) {
  return `<form data-form="editar-cp" data-id="${c.id}">${cabeca('Editar checkpoint', esc(nomeProjeto(c.projeto)))}
    <div class="dlg-corpo">
      <label class="campo-grupo"><span>Título</span><input class="campo" name="titulo" maxlength="200" required value="${esc(c.titulo)}"></label>
      <label class="campo-grupo"><span>Descrição</span><textarea class="campo" name="descricao" maxlength="4000">${esc(c.descricao)}</textarea></label>
      <div class="grelha-campos">
        <label class="campo-grupo"><span>Estado</span><select class="campo" name="estado">${opcoes(ESTADOS_C, c.estado)}</select></label>
        <label class="campo-grupo"><span>Posição no workflow</span><select class="campo" name="posicao">${opcoesPosicao(c.projeto, c.id)}</select></label>
      </div>
      <label class="campo-grupo"><span>Critério de saída <small>(opcional: o que tem de ser verdade para o dar como concluído)</small></span><textarea class="campo" name="criterio_saida" maxlength="2000" rows="2">${esc(c.criterio_saida || '')}</textarea></label>
      ${htmlAnexosEdicao('checkpoint', c.id)}
      <p class="erro-msg pequeno" role="alert"></p>
    </div>
    <div class="dlg-rodape" style="justify-content:space-between">
      <button class="btn texto perigo" type="button" data-acao="apagar-cp" data-id="${c.id}">${ic('apagar', 'ic-sm')}Apagar checkpoint</button>
      <div style="display:flex;gap:8px"><button class="btn texto" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">Guardar</button></div>
    </div>
  </form>`;
}

// ---------------------------------------------------------------- decisões
const prosContras = (o) => `<div class="pros-contras">
  ${o.vantagens ? `<div class="pro">${ic('mais', 'ic-sm')}<span>${esc(o.vantagens)}</span></div>` : '<div></div>'}
  ${o.desvantagens ? `<div class="contra">${ic('menos', 'ic-sm')}<span>${esc(o.desvantagens)}</span></div>` : '<div></div>'}</div>`;
const corpoOpcao = (o) => `<h4>${esc(o.titulo)} ${o.custo ? `<span class="chip custo">${ic('custo', 'ic-sm')}${esc(o.custo)}</span>` : ''}</h4>
  ${o.descricao ? `<p class="suave pequeno">${esc(o.descricao)}</p>` : ''}${prosContras(o)}`;

export function dlgDecisao(d) {
  const ops = d.decisoes_opcoes || [];
  const tarefa = d.tarefa_id ? E.tarefas.find((t) => t.id === d.tarefa_id) : null;
  const sub = `${esc(nomeProjeto(d.projeto))}${tarefa ? ' · tarefa «' + esc(tarefa.titulo) + '»' : ''}`;
  if (d.estado === 'decidida') {
    const esc_ = ops.find((o) => o.id === d.opcao_escolhida);
    const outras = ops.filter((o) => o.id !== d.opcao_escolhida);
    return `<div>${cabeca(esc(d.pergunta), sub)}
      <div class="dlg-corpo">
        <div class="registo"><p><b>Escolhemos «${esc(esc_ ? esc_.titulo : '?')}»</b>${outras.length ? ' em vez de ' + outras.map((o) => '«' + esc(o.titulo) + '»').join(', ') : ''}.</p>
          <p class="suave pequeno">Decidido por ${esc(d.decidida_por_nome || 'Equipa')} a ${dia(d.decidida_em)}.</p>
          ${d.justificacao ? `<p class="pequeno">Porquê: ${esc(d.justificacao)}</p>` : ''}</div>
        ${d.contexto ? `<p class="suave">${esc(d.contexto)}</p>` : ''}
        ${esc_ ? `<div class="opcao escolhida">${corpoOpcao(esc_)}</div>` : ''}
        ${outras.length ? `<details class="outras"><summary>Ver as outras opções (${outras.length})</summary><div class="opcoes">${outras.map((o) => `<div class="opcao">${corpoOpcao(o)}</div>`).join('')}</div></details>` : ''}
      </div>
      ${E.eu.editar ? `<div class="dlg-rodape"><button class="btn texto" type="button" data-acao="reabrir-decisao" data-id="${d.id}">Reabrir decisão</button></div>` : ''}
    </div>`;
  }
  return `<form data-form="decidir" data-id="${d.id}">${cabeca(esc(d.pergunta), sub)}
    <div class="dlg-corpo">
      ${d.contexto ? `<p class="suave">${esc(d.contexto)}</p>` : ''}
      <fieldset class="opcoes" style="border:0;padding:0;margin:0"><legend class="so-leitor">Opções</legend>
        ${ops.map((o) => E.eu.editar
          ? `<label class="opcao"><input type="radio" name="opcao" value="${o.id}" required>${corpoOpcao(o)}</label>`
          : `<div class="opcao">${corpoOpcao(o)}</div>`).join('')}
      </fieldset>
      ${E.eu.editar ? `<div class="outra-opcao">
        <button type="button" class="btn pequeno" data-acao="mostrar-outra-opcao" aria-expanded="false" aria-controls="outra-opcao-${d.id}">${ic('mais', 'ic-sm')}Outra opção</button>
        <div class="opcao-edicao" id="outra-opcao-${d.id}" hidden>
          <label class="campo-grupo"><span>Opção</span><input class="campo" name="n_titulo" maxlength="200" autocomplete="off" placeholder="Uma alternativa que não está na lista"></label>
          <label class="campo-grupo"><span>Descrição <small>(opcional)</small></span><input class="campo" name="n_descricao" maxlength="2000"></label>
          <div class="grelha-campos">
            <label class="campo-grupo"><span>Vantagens</span><textarea class="campo" name="n_vantagens" rows="2" maxlength="2000"></textarea></label>
            <label class="campo-grupo"><span>Desvantagens</span><textarea class="campo" name="n_desvantagens" rows="2" maxlength="2000"></textarea></label>
          </div>
          <label class="campo-grupo"><span>Custo <small>(opcional)</small></span><input class="campo" name="n_custo" maxlength="300"></label>
          <div class="botoes"><button type="button" class="btn pequeno primario" data-acao="acrescentar-opcao" data-id="${d.id}">Acrescentar opção</button></div>
        </div>
      </div>` : ''}
      ${E.eu.editar ? `<label class="campo-grupo"><span>Porquê <small>(fica registado com a decisão)</small></span><textarea class="campo" name="justificacao" maxlength="4000"></textarea></label>` : '<p class="fraco pequeno">Quem tem acesso de editar regista a decisão.</p>'}
      <p class="erro-msg pequeno" role="alert"></p>
    </div>
    ${E.eu.editar ? `<div class="dlg-rodape" style="justify-content:space-between"><button class="btn texto perigo" type="button" data-acao="apagar-decisao" data-id="${d.id}">${ic('apagar', 'ic-sm')}Apagar</button>
      <div style="display:flex;gap:8px"><button class="btn texto" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">Registar decisão</button></div></div>` : ''}
  </form>`;
}

export const htmlOpcaoEdicao = (n) => `<div class="opcao-edicao" data-opcao>
  <div style="display:flex;justify-content:space-between;align-items:center"><b class="pequeno">Opção ${n}</b><button class="btn pequeno texto" type="button" data-acao="tirar-opcao">Tirar</button></div>
  <input class="campo" name="o_titulo" maxlength="200" placeholder="Nome da opção" aria-label="Nome da opção ${n}" required>
  <textarea class="campo" name="o_descricao" maxlength="2000" placeholder="O que é (opcional)" aria-label="Descrição da opção ${n}" style="min-height:56px"></textarea>
  <div class="grelha-campos"><input class="campo" name="o_vantagens" maxlength="2000" placeholder="Vantagens" aria-label="Vantagens da opção ${n}">
    <input class="campo" name="o_desvantagens" maxlength="2000" placeholder="Desvantagens" aria-label="Desvantagens da opção ${n}"></div>
  <input class="campo" name="o_custo" maxlength="300" placeholder="Custo (se houver)" aria-label="Custo da opção ${n}">
</div>`;
export function dlgNovaDecisao(tarefa, projetoId) {
  return `<form data-form="nova-decisao" data-tarefa="${tarefa ? tarefa.id : ''}" data-projeto="${projetoId}">${cabeca('Nova decisão', tarefa ? 'Para a tarefa «' + esc(tarefa.titulo) + '»' : esc(nomeProjeto(projetoId)))}
    <div class="dlg-corpo">
      <label class="campo-grupo"><span>Pergunta</span><input class="campo" name="pergunta" maxlength="300" required placeholder="Vamos usar isto ou aquilo?"></label>
      <label class="campo-grupo"><span>Contexto <small>(opcional)</small></span><textarea class="campo" name="contexto" maxlength="4000"></textarea></label>
      <div class="opcoes" id="opcoes-edicao">${htmlOpcaoEdicao(1)}${htmlOpcaoEdicao(2)}</div>
      <button class="btn" type="button" data-acao="mais-opcao" style="justify-self:start">${ic('mais', 'ic-sm')}Outra opção</button>
      <p class="erro-msg pequeno" role="alert"></p>
    </div>
    <div class="dlg-rodape"><button class="btn texto" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">Criar decisão</button></div>
  </form>`;
}

// ---------------------------------------------------------------- sugestões (gaveta): sugestões + checklist
const FERRAMENTAS = { geral: 'Geral (o hub)', gerador: 'Gerador de documentos', builder: 'Builder', orcamentacao: 'Orçamentação', build_your_house: 'Build Your House', plataforma_cliente: 'Step Inside' };
const ESTADOS_S = { nova: 'Nova', em_analise: 'Em análise', feita: 'Concluída', recusada: 'Recusada' };
const COR_S = { nova: 'por_fazer', em_analise: 'em_curso', feita: 'concluida', recusada: 'bloqueada' };
export function htmlGaveta(sep, sugestoes, abertas, erro) {
  const podeApagar = (g) => E.eu.editar || (g.autor_id === E.eu.id && !g.na_checklist);
  const lista = sep === 'checklist' ? sugestoes.filter((g) => g.na_checklist).sort((a, b) => new Date(a.checklist_em) - new Date(b.checklist_em)) : sugestoes;
  const corpo = erro ? `<p class="erro-msg">Não consegui carregar as sugestões: ${esc(erro)}</p>` : sep === 'checklist'
    ? (lista.length ? `<p class="suave pequeno">As sugestões que escolhemos fazer. <span class="num">${lista.filter((g) => g.estado === 'feita').length} de ${lista.length}</span> concluídas.</p>` + lista.map((g) => `<div class="check">
        <input type="checkbox" class="visto" data-acao="sug-concluir" data-id="${g.id}" aria-label="Concluída"${g.estado === 'feita' ? ' checked' : ''}${E.eu.editar ? '' : ' disabled'}>
        <div><p class="pequeno" style="white-space:pre-wrap">${esc(g.texto)}</p><div class="meta" style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px;align-items:center">
          <span class="estado ${COR_S[g.estado]}">${ESTADOS_S[g.estado]}</span><span class="fraco mini">${esc(FERRAMENTAS[g.ferramenta] || g.ferramenta)}</span>
          ${E.eu.editar ? `<select class="seletor" data-acao="sug-estado" data-id="${g.id}" aria-label="Estado">${opcoes({ em_analise: 'Em análise', feita: 'Concluída', recusada: 'Recusada' }, g.estado === 'nova' ? 'em_analise' : g.estado)}</select>
          <button class="btn pequeno texto" type="button" data-acao="sug-tirar" data-id="${g.id}">Tirar da checklist</button>` : ''}</div></div></div>`).join('')
      : `<p class="vazio">${E.eu.editar ? 'Ainda não há tarefas: em cada sugestão, "Pôr na checklist".' : 'Ainda não há tarefas.'}</p>`)
    : `<form data-form="sugestao" style="display:grid;gap:10px">
        <label class="campo-grupo"><span>O que mudavas no hub?</span><textarea class="campo" name="texto" maxlength="2000" minlength="3" required placeholder="Uma ideia, um erro, algo que falta…"></textarea></label>
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center"><select class="campo" name="ferramenta" style="width:auto" aria-label="Sobre">${opcoes(FERRAMENTAS, 'geral')}</select>
          <button class="btn primario" type="submit">Enviar sugestão</button><span class="suave pequeno" role="status" data-msg></span></div>
      </form>
      ${lista.length ? lista.map((g) => {
        const n = (g.sugestoes_comentarios || []).length;
        return `<article class="sug"><div class="meta"><span class="estado ${COR_S[g.estado]}">${ESTADOS_S[g.estado]}</span><span>${esc(FERRAMENTAS[g.ferramenta] || g.ferramenta)}</span><span>· ${esc(g.autor_nome || 'Alguém')} · ${dia(g.criada_em)}</span>
          ${E.eu.editar ? `<select class="seletor" data-acao="sug-estado" data-id="${g.id}" aria-label="Estado">${opcoes(ESTADOS_S, g.estado)}</select>` : ''}</div>
          <p>${esc(g.texto)}</p>
          <div class="acoes"><button type="button" class="btn pequeno" data-acao="sug-comentarios" data-id="${g.id}" aria-expanded="${abertas.has(g.id)}">Comentários (${n})</button>
            ${g.na_checklist ? '<span class="chip">' + ic('certo', 'ic-sm') + 'Na checklist</span>' : E.eu.editar ? `<button type="button" class="btn pequeno" data-acao="sug-checklist" data-id="${g.id}">Pôr na checklist</button>` : ''}
            ${podeApagar(g) ? `<button type="button" class="btn pequeno texto perigo" data-acao="sug-apagar" data-id="${g.id}">Eliminar</button>` : ''}</div>
          ${abertas.has(g.id) ? `<div class="comentarios">${(g.sugestoes_comentarios || []).map((c) => `<div class="comentario"><div class="meta">${esc(c.autor_nome || 'Alguém')} · ${dia(c.criado_em)}
              ${E.eu.editar || c.autor_id === E.eu.id ? `<button type="button" class="btn pequeno texto perigo" data-acao="sug-apagar-comentario" data-id="${c.id}">Apagar</button>` : ''}</div><p>${esc(c.texto)}</p></div>`).join('') || '<p class="fraco pequeno">Ainda sem comentários.</p>'}
            <form data-form="comentario" data-id="${g.id}" style="display:flex;gap:8px"><input class="campo" name="texto" maxlength="2000" required placeholder="Escreve um comentário…" aria-label="Comentário"><button class="btn pequeno" type="submit">Comentar</button></form></div>` : ''}
        </article>`;
      }).join('') : '<p class="vazio">Ainda não há sugestões. Sê o primeiro.</p>'}`;
  return `<div class="gaveta-conteudo">${cabeca('Sugestões', 'Qualquer pessoa pode sugerir mudanças ao hub do Design; toda a equipa vê e comenta.')}
    <div class="separadores" role="tablist">
      <button type="button" role="tab" data-acao="sug-sep" data-valor="sugestoes" aria-selected="${sep !== 'checklist'}">Sugestões</button>
      <button type="button" role="tab" data-acao="sug-sep" data-valor="checklist" aria-selected="${sep === 'checklist'}">Checklist</button>
    </div>
    <div class="gaveta-corpo">${corpo}</div></div>`;
}
// carregar documentos (um ou vários ficheiros de uma vez)
export function dlgDocumento(projetoId) {
  return `<form data-form="documento" data-projeto="${projetoId}">${cabeca('Acrescentar documento', esc(nomeProjeto(projetoId)) + ' · fica guardado em privado, só para quem entra no Design.')}
    <div class="dlg-corpo">
      <div class="segmentado" role="group" aria-label="Tipo de documento">
        <button type="button" data-acao="tipo-doc" data-valor="informativo" aria-pressed="true">Informativo</button>
        <button type="button" data-acao="tipo-doc" data-valor="adicional" aria-pressed="false">Adicional</button>
      </div>
      <input type="hidden" name="tipo" value="informativo">
      <p class="fraco mini" data-explica>Informativo: o que o projeto é (especificações, planos). Adicional: conhecimento extra (desenhos de obras, fichas, fotografias).</p>
      <label class="campo-grupo"><span>Ficheiros</span><input class="campo" type="file" name="ficheiros" multiple required></label>
      <ul class="ficheiros-escolhidos" data-escolhidos></ul>
      <label class="campo-grupo"><span>Título <small>(se for um só ficheiro; vazio = o nome do ficheiro)</small></span><input class="campo" name="titulo" maxlength="200"></label>
      <label class="campo-grupo"><span>Descrição <small>(opcional)</small></span><textarea class="campo" name="descricao" maxlength="2000" style="min-height:64px"></textarea></label>
      <p class="erro-msg pequeno" role="alert"></p>
    </div>
    <div class="dlg-rodape"><button class="btn texto" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">Carregar</button></div>
  </form>`;
}
export { abrirDialogo, projeto };
