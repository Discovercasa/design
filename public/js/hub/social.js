// Redes sociais: o planeamento dos posts (um por semana, legenda e fotos aprovadas antes de publicar) e as obras com
// as suas fases (para saber quando ir ao local tirar fotos). Rotas: #/social, #/social/post-<id>, #/social/obras,
// #/social/obras/obra-<id>. Os botões levam data-sacao e os formulários data-sform (o app.js não lhes toca).
import { E, chave } from './dados.js';
import * as S from './social-dados.js';
import { $, $$, ic, esc, dia, diaCurto, iniciais, aviso, abrirDialogo, fecharDialogo, mov, entrar } from './util.js';

let ctx = null;                 // { dlg, desenhar, depois, tentar }
let filtroObra = '';            // '' = todas
let sujo = false;               // o editor do post tem alterações por guardar
let aba = 'fotos';              // no editor: fotos ou pré-visualização
const EMOJIS = ['🏡', '🏠', '✨', '🏗️', '🚧', '🔨', '🛠️', '👷', '🧱', '🪵', '🌿', '🌱', '🌳', '☀️', '💚', '✅', '✔️', '👉', '➡️', '⬇️',
  '🌐', '📩', '📞', '📍', '📸', '🎥', '💡', '🔑', '📐', '⭐', '❤️', '🙌', '👏', '🤝', '😊', '🎉', '🎄', '🔥', '💬', '🗓️'];

const tamanho = (b) => (b >= 1e6 ? `${(b / 1e6).toLocaleString('pt-PT', { maximumFractionDigits: 1 })} MB` : `${Math.max(1, Math.round(b / 1e3))} kB`);
const opcoes = (mapa, atual) => Object.entries(mapa).map(([k, v]) => `<option value="${k}"${k === atual ? ' selected' : ''}>${esc(v)}</option>`).join('');
const cabeca = (titulo, sub = '', fechar = 'fechar-dlg') => `<div class="dlg-cabeca"><div><h2>${titulo}</h2>${sub ? `<p class="suave pequeno" style="margin-top:4px">${sub}</p>` : ''}</div>
  <button class="icone-botao" type="button" ${fechar === 'fechar-dlg' ? 'data-acao="fechar-dlg"' : `data-sacao="${fechar}"`} aria-label="Fechar">${ic('fechar')}</button></div>`;
const novo = (tipo, id) => (E.novos.has(chave(tipo, id)) ? '<span class="chip novo">Novo</span>' : '');
const estadoPost = (e) => `<span class="estado p-${e}">${esc(S.ESTADOS_POST[e])}</span>`;
const semanaRotulo = (p) => `Semana ${p.semana} · ${S.nomeMes(p.mes)}`;
const obraFase = (p) => [S.obra(p.obra_id), S.fase(p.fase_id)].filter(Boolean).map((x) => x.nome).join(' · ');
const img = (caminho, alt = '', cls = '') => `<img${cls ? ` class="${cls}"` : ''} alt="${esc(alt)}" loading="lazy" decoding="async" data-cam="${esc(caminho)}"${S.urlEmCache(caminho) ? ` src="${esc(S.urlEmCache(caminho))}"` : ''}>`;
const miniOuIcone = (m, cls = '') => (m.miniatura ? img(m.miniatura, m.nome_ficheiro, cls) : `<span class="sem-mini ${cls}">${ic(S.ehVideo(m) ? 'video' : 'imagem')}</span>`);

// ---------------------------------------------------------------- página
export function pagina(sub) {
  if (E.socialErro) return `<div class="cabeca-pagina"><div class="texto"><h1>Redes sociais</h1></div></div>
    <div class="nota" style="border-color:var(--erro)">${ic('atencao')}<p><b>As redes sociais ainda não estão disponíveis.</b> A base de dados precisa da migração 0009. <span class="fraco">(${esc(E.socialErro)})</span></p></div>`;
  const porAprovar = E.posts.filter((p) => p.estado === 'por_aprovar').length;
  const visitas = S.visitasParaFotos().length;
  const estaSemana = S.postsDe(S.mesDe(new Date()), S.semanaDeHoje())[0];
  return `
  <div class="cabeca-pagina">
    <div class="texto">
      <h1>Redes sociais</h1>
      <p class="suave">Um post por semana em cada mês. A legenda e as fotos são aprovadas antes de publicar; as obras dizem quando ir ao local tirar fotos.</p>
      <div class="para-ti">
        ${estaSemana ? `<a class="chip" href="#/social/post-${estaSemana.id}">${ic('calendario', 'ic-sm')}Esta semana: ${esc(estaSemana.titulo)}</a>` : `<span class="chip">${ic('calendario', 'ic-sm')}Sem post esta semana</span>`}
        <a class="chip" href="#/social" data-sacao="so-por-aprovar">${ic('certo', 'ic-sm')}<span class="num">${porAprovar}</span> por aprovar</a>
        <a class="chip" href="#/social/obras">${ic('camara', 'ic-sm')}<span class="num">${visitas}</span> ${visitas === 1 ? 'visita para fotos' : 'visitas para fotos'}</a>
      </div>
    </div>
    ${E.eu.editar ? `<div class="botoes"><button class="btn" type="button" data-sacao="nova-obra">${ic('mais')}Obra</button>
      <button class="btn primario grande" type="button" data-sacao="novo-post">${ic('mais')}Post</button></div>` : ''}
  </div>
  <div class="social-barra">
    <nav class="segmentado" aria-label="Redes sociais">
      <a href="#/social"${sub !== 'obras' ? ' aria-current="page"' : ''}>Planeamento</a>
      <a href="#/social/obras"${sub === 'obras' ? ' aria-current="page"' : ''}>Obras</a>
    </nav>
    ${sub !== 'obras' ? `<label class="filtro">${ic('casa', 'ic-sm')}<span class="so-leitor">Mostrar a obra</span>
      <select class="seletor" data-sacao="filtro-obra"><option value="">Todas as obras</option>${obrasOrdenadas().map((o) => `<option value="${o.id}"${String(o.id) === filtroObra ? ' selected' : ''}>${esc(o.nome)}</option>`).join('')}</select></label>` : ''}
  </div>
  ${sub === 'obras' ? paginaObras() : planeamento()}`;
}
const obrasOrdenadas = () => [...E.obras].sort((a, b) => (b.ativa - a.ativa) || a.ordem - b.ordem || a.nome.localeCompare(b.nome, 'pt'));

// ---------------------------------------------------------------- planeamento (meses × semanas)
function planeamento() {
  const atual = S.mesDe(new Date());
  const meses = S.mesesVisiveis();
  const passados = meses.filter((m) => m < atual), seguintes = meses.filter((m) => m >= atual);
  return `${passados.length ? `<details class="meses-passados"><summary>${ic('baixo', 'ic-sm')}Meses anteriores <span class="fraco num">(${passados.length})</span></summary>${passados.map(mes).join('')}</details>` : ''}
    ${seguintes.map(mes).join('')}`;
}
function mes(m) {
  const posts = S.postsDe(m).filter((p) => !filtroObra || String(p.obra_id) === filtroObra);
  const publicados = posts.filter((p) => p.estado === 'publicado').length;
  const ultima = Math.max(4, ...posts.map((p) => p.semana));
  const atual = m === S.mesDe(new Date());
  const semanas = Array.from({ length: ultima }, (_, i) => i + 1);
  return `<section class="mes" id="mes-${m.slice(0, 7)}" aria-labelledby="t-mes-${m.slice(0, 7)}" style="--semanas:${ultima}">
    <div class="mes-cabeca"><h2 id="t-mes-${m.slice(0, 7)}">${esc(S.nomeMes(m))}</h2>
      <span class="fraco pequeno num">${posts.length} ${posts.length === 1 ? 'post' : 'posts'}${posts.length ? ` · ${publicados} ${publicados === 1 ? 'publicado' : 'publicados'}` : ''}</span></div>
    <ol class="semanas">${semanas.map((s) => {
      const ps = posts.filter((p) => p.semana === s);
      const outros = filtroObra && !ps.length ? S.postsDe(m, s) : [];   // com o filtro: a semana já tem post de outra obra
      const esta = atual && s === S.semanaDeHoje();
      return `<li class="semana${esta ? ' atual' : ''}"><div class="semana-rotulo">Semana ${s}${esta ? ' <span class="chip agora">Esta semana</span>' : ''}</div>
        ${ps.map(cartao).join('')}
        ${outros.length ? `<a class="semana-vazia ocupada" href="#/social/post-${outros[0].id}">Já tem post: ${esc(outros[0].titulo)}</a>` : ''}
        ${!ps.length && !outros.length ? (E.eu.editar ? `<button type="button" class="semana-vazia" data-sacao="novo-post" data-mes="${m}" data-semana="${s}">${ic('mais', 'ic-sm')}Planear post</button>` : '<p class="semana-vazia">Sem post</p>') : ''}
      </li>`;
    }).join('')}</ol>
  </section>`;
}
function cartao(p) {
  const ms = S.mediaDe(p.id), cs = S.comentariosDe(p.id).filter((c) => !c.resolvido);
  const mostrar = ms.slice(0, 4);
  const primeira = (p.legenda || '').split('\n').find((l) => l.trim()) || '';
  return `<a class="post-cartao" id="post-${p.id}" href="#/social/post-${p.id}">
    <div class="post-fotos n${Math.min(4, mostrar.length)}">${mostrar.length ? mostrar.map((m, i) => `<span class="pf">${miniOuIcone(m)}${i === 3 && ms.length > 4 ? `<b class="mais-fotos">+${ms.length - 4}</b>` : ''}</span>`).join('')
      : `<span class="sem-fotos">${ic('camara')}<span>Sem fotos</span></span>`}</div>
    <div class="post-texto">
      ${obraFase(p) ? `<span class="post-obra">${esc(obraFase(p))}</span>` : ''}
      <h3>${esc(p.titulo)} ${novo('post', p.id)}</h3>
      ${primeira ? `<p class="post-legenda">${esc(primeira.slice(0, 140))}</p>` : '<p class="post-legenda fraco">Sem legenda</p>'}
      <div class="post-meta">${estadoPost(p.estado)}
        <span class="aprov${p.legenda_aprovada ? ' ok' : ''}" title="Legenda ${p.legenda_aprovada ? 'aprovada' : 'por aprovar'}">${ic(p.legenda_aprovada ? 'certo' : 'menos', 'ic-sm')}Legenda</span>
        <span class="aprov${p.fotos_aprovadas ? ' ok' : ''}" title="Fotos ${p.fotos_aprovadas ? 'aprovadas' : 'por aprovar'}">${ic(p.fotos_aprovadas ? 'certo' : 'menos', 'ic-sm')}Fotos <span class="num">${ms.length}</span></span>
        ${cs.length ? `<span class="aprov" title="Comentários por resolver">${ic('comentario', 'ic-sm')}<span class="num">${cs.length}</span></span>` : ''}
      </div>
    </div>
  </a>`;
}

// ---------------------------------------------------------------- obras e fases
function paginaObras() {
  const visitas = S.visitasParaFotos();
  const ativas = S.obrasAtivas(), arquivadas = E.obras.filter((o) => !o.ativa);
  return `
  <section class="seccao-primeira" aria-labelledby="t-visitas">
    <div class="seccao-cabeca"><div><h2 id="t-visitas">Visitas para fotos</h2><p>As visitas marcadas e as fases em curso que ainda não têm fotos.</p></div></div>
    ${visitas.length ? `<ul class="visitas">${visitas.map((f) => {
      const o = S.obra(f.obra_id);
      return `<li class="visita">
        <span class="visita-icone${f.fotos === 'visita_marcada' ? ' marcada' : ''}">${ic(f.fotos === 'visita_marcada' ? 'calendario' : 'camara')}</span>
        <div><b>${esc(o.nome)}</b> · ${esc(f.nome)}<p class="fraco mini">${f.fotos === 'visita_marcada' ? `Visita marcada${f.visita_em ? ` para ${dia(f.visita_em)}` : ''}` : 'Fase em curso, fotos por tirar'}${f.periodo ? ` · ${esc(f.periodo)}` : ''}</p></div>
        ${E.eu.editar ? `<div class="botoes"><button class="btn pequeno" type="button" data-sacao="marcar-visita" data-id="${f.id}">${ic('calendario', 'ic-sm')}${f.fotos === 'visita_marcada' ? 'Mudar dia' : 'Marcar visita'}</button>
          <button class="btn pequeno" type="button" data-sacao="fotos-tiradas" data-id="${f.id}">${ic('certo', 'ic-sm')}Fotos tiradas</button></div>` : ''}
      </li>`;
    }).join('')}</ul>` : '<p class="vazio">Nenhuma visita pendente. Quando uma fase passa a «Em curso», aparece aqui até as fotos estarem tiradas.</p>'}
  </section>
  <section class="seccao" aria-labelledby="t-obras">
    <div class="seccao-cabeca"><div><h2 id="t-obras">Obras</h2><p>As fases não se apagam: acrescentam-se e vão-se marcando.</p></div></div>
    ${ativas.length ? `<div class="obras-grelha">${ativas.map(cartaoObra).join('')}</div>` : '<p class="vazio">Ainda sem obras.</p>'}
    ${arquivadas.length ? `<details class="meses-passados" style="margin-top:24px"><summary>${ic('arquivo', 'ic-sm')}Obras arquivadas <span class="fraco num">(${arquivadas.length})</span></summary><div class="obras-grelha">${arquivadas.map(cartaoObra).join('')}</div></details>` : ''}
  </section>`;
}
function cartaoObra(o) {
  const fs = S.fasesDe(o.id), atual = S.faseAtual(o.id), posts = S.postsDaObra(o.id);
  return `<article class="obra" id="obra-${o.id}">
    <div class="obra-cabeca">
      <div><h3>${esc(o.nome)} ${novo('obra', o.id)}</h3>
        <p class="fraco mini">${atual ? `${atual.estado === 'em_curso' ? 'Agora' : 'Última concluída'}: <b>${esc(atual.nome)}</b>` : fs.length ? 'Ainda sem fases em curso' : 'Sem fases'} · <span class="num">${posts.length}</span> ${posts.length === 1 ? 'post' : 'posts'}</p></div>
      ${E.eu.editar ? `<button class="icone-botao" type="button" data-sacao="editar-obra" data-id="${o.id}" aria-label="Editar a obra ${esc(o.nome)}" title="Editar a obra">${ic('editar', 'ic-sm')}</button>` : ''}
    </div>
    ${o.descricao ? `<p class="suave pequeno">${esc(o.descricao)}</p>` : ''}
    ${fs.length ? `<ol class="fases">${fs.map((f) => {
      const pf = posts.filter((p) => p.fase_id === f.id), feitos = pf.filter((p) => p.estado === 'publicado').length;
      return `<li class="fase-linha ${f.estado}">
        <span class="marco" aria-hidden="true">${f.estado === 'concluida' ? ic('certo', 'ic-sm') : ''}</span>
        <div class="fase-corpo">
          ${E.eu.editar ? `<button type="button" class="fase-nome" data-sacao="editar-fase" data-id="${f.id}">${esc(f.nome)}</button>` : `<span class="fase-nome">${esc(f.nome)}</span>`}
          <span class="fase-meta"><span class="estado ${f.estado === 'concluida' ? 'concluida' : f.estado === 'em_curso' ? 'em_curso' : ''}">${S.ESTADOS_FASE[f.estado]}</span>
            ${f.periodo ? `<span>${esc(f.periodo)}</span>` : ''}
            ${f.posts_previstos != null || pf.length ? `<span class="num" title="Posts publicados desta fase / previstos">${feitos}/${f.posts_previstos ?? pf.length} posts</span>` : ''}
            ${f.estado === 'em_curso' || f.fotos !== 'por_tirar' ? `<span class="fotos-fase ${f.fotos}">${ic(f.fotos === 'tiradas' ? 'certo' : f.fotos === 'visita_marcada' ? 'calendario' : 'camara', 'ic-sm')}${f.fotos === 'visita_marcada' && f.visita_em ? `Visita ${diaCurto(f.visita_em)}` : f.fotos === 'tiradas' && f.fotos_em ? `Fotos ${diaCurto(f.fotos_em)}` : esc(S.FOTOS_FASE[f.fotos])}</span>` : ''}</span>
          ${f.notas ? `<p class="fraco mini">${esc(f.notas)}</p>` : ''}
        </div>
      </li>`;
    }).join('')}</ol>` : ''}
    ${E.eu.editar ? `<button class="btn pequeno texto" type="button" data-sacao="nova-fase" data-id="${o.id}">${ic('mais', 'ic-sm')}Fase</button>` : ''}
    ${posts.length ? `<div class="obra-posts">${posts.map((p) => `<a class="chip" href="#/social/post-${p.id}" title="${esc(S.ESTADOS_POST[p.estado])}"><span class="ponto-estado p-${p.estado}"></span>${esc(S.nomeMes(p.mes, false).slice(0, 3))} S${p.semana} · ${esc(p.titulo)}</a>`).join('')}</div>` : ''}
  </article>`;
}

// ---------------------------------------------------------------- resumo no Início
export function resumoInicio() {
  if (E.socialErro) return '';
  const estaSemana = S.postsDe(S.mesDe(new Date()), S.semanaDeHoje());
  const porAprovar = E.posts.filter((p) => p.estado === 'por_aprovar');
  const visitas = S.visitasParaFotos();
  const linha = (p) => `<li><a href="#/social/post-${p.id}" class="pequeno" style="color:inherit">${esc(p.titulo)}</a> <span class="fraco mini">${esc(semanaRotulo(p))}</span></li>`;
  return `<section class="seccao" aria-labelledby="t-social">
    <div class="seccao-cabeca"><div><h2 id="t-social">Redes sociais</h2><p>O post desta semana, o que espera aprovação e onde ir tirar fotos.</p></div>
      <a class="btn" href="#/social">Planeamento${ic('seta', 'ic-sm')}</a></div>
    <div class="social-resumo">
      <div class="bloco-lateral"><h3>${ic('calendario', 'ic-sm')}Esta semana</h3>
        ${estaSemana.length ? `<ul class="lista-simples">${estaSemana.map((p) => `<li>${estadoPost(p.estado)}<a href="#/social/post-${p.id}" class="pequeno" style="color:inherit">${esc(p.titulo)}</a></li>`).join('')}</ul>` : '<p class="suave pequeno">Sem post planeado.</p>'}</div>
      <div class="bloco-lateral"><h3>${ic('certo', 'ic-sm')}Por aprovar <span class="fraco num">${porAprovar.length}</span></h3>
        ${porAprovar.length ? `<ul class="lista-simples">${porAprovar.slice(0, 4).map(linha).join('')}</ul>` : '<p class="suave pequeno">Nada à espera.</p>'}</div>
      <div class="bloco-lateral"><h3>${ic('camara', 'ic-sm')}Visitas para fotos <span class="fraco num">${visitas.length}</span></h3>
        ${visitas.length ? `<ul class="lista-simples">${visitas.slice(0, 4).map((f) => `<li><a href="#/social/obras/obra-${f.obra_id}" class="pequeno" style="color:inherit">${esc(S.obra(f.obra_id).nome)} · ${esc(f.nome)}</a>${f.visita_em ? ` <span class="fraco mini">${diaCurto(f.visita_em)}</span>` : ''}</li>`).join('')}</ul>` : '<p class="suave pequeno">Nenhuma pendente.</p>'}</div>
    </div>
  </section>`;
}

// ---------------------------------------------------------------- diálogos: post novo e editor
const opcoesObras = (atual, vazio = 'Sem obra') => `<option value="">${vazio}</option>` + obrasOrdenadas().filter((o) => o.ativa || o.id === atual).map((o) => `<option value="${o.id}"${o.id === atual ? ' selected' : ''}>${esc(o.nome)}</option>`).join('');
const opcoesFases = (obraId, atual) => '<option value="">Sem fase</option>' + (obraId ? S.fasesDe(obraId).map((f) => `<option value="${f.id}"${f.id === atual ? ' selected' : ''}>${esc(f.nome)}${f.estado === 'em_curso' ? ' (em curso)' : ''}</option>`).join('') : '');
function opcoesMeses(atual) {
  const hoje = S.mesDe(new Date());
  const set = new Set([...Array.from({ length: 19 }, (_, i) => S.somarMeses(hoje, i - 6)), ...E.posts.map((p) => p.mes), atual].filter(Boolean));
  return [...set].sort().map((m) => `<option value="${m}"${m === atual ? ' selected' : ''}>${esc(S.nomeMes(m))}</option>`).join('');
}
const opcoesSemanas = (atual) => [1, 2, 3, 4, 5].map((s) => `<option value="${s}"${s === atual ? ' selected' : ''}>Semana ${s}</option>`).join('');

function dlgNovoPost(mes, semana) {
  const obraId = filtroObra ? Number(filtroObra) : null;
  return `<form data-sform="novo-post">${cabeca('Planear um post', 'Primeiro o essencial; as fotos e a legenda entram a seguir.')}
    <div class="dlg-corpo">
      <label class="campo-grupo"><span>Título</span><input class="campo" name="titulo" maxlength="200" required autocomplete="off" placeholder="Ex.: Boelhe - Estrutura"></label>
      <div class="grelha-campos">
        <label class="campo-grupo"><span>Obra</span><select class="campo" name="obra" data-sacao="obra-post">${opcoesObras(obraId)}</select></label>
        <label class="campo-grupo"><span>Fase da obra</span><select class="campo" name="fase">${opcoesFases(obraId)}</select></label>
        <label class="campo-grupo"><span>Mês</span><select class="campo" name="mes">${opcoesMeses(mes || S.mesDe(new Date()))}</select></label>
        <label class="campo-grupo"><span>Semana</span><select class="campo" name="semana">${opcoesSemanas(Number(semana) || S.semanaDeHoje())}</select></label>
        <label class="campo-grupo"><span>Tipo</span><select class="campo" name="tipo">${opcoes(S.TIPOS_POST, 'carrossel')}</select></label>
      </div>
      <p class="erro-msg pequeno" role="alert"></p>
    </div>
    <div class="dlg-rodape"><button class="btn" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">Criar e acrescentar fotos</button></div></form>`;
}

function htmlEditor(p) {
  const pode = E.eu.editar;
  return `<form data-sform="post" data-id="${p.id}" class="editor-post">${cabeca(esc(p.titulo), `${esc(semanaRotulo(p))}${obraFase(p) ? ' · ' + esc(obraFase(p)) : ''} · ${estadoPost(p.estado)}`, 'fechar-post')}
    <div class="dlg-corpo pe">
      <div class="pe-esquerda">
        <div class="segmentado" role="group" aria-label="Ver">
          <button type="button" data-sacao="pe-aba" data-valor="fotos" aria-pressed="${aba === 'fotos'}">${ic('imagem', 'ic-sm')}Fotos</button>
          <button type="button" data-sacao="pe-aba" data-valor="previa" aria-pressed="${aba === 'previa'}">${ic('camara', 'ic-sm')}Pré-visualizar</button>
        </div>
        <div id="pe-media"${aba === 'fotos' ? '' : ' hidden'}>${htmlMedia(p)}</div>
        <div id="pe-previa"${aba === 'previa' ? '' : ' hidden'}>${htmlPrevia(p, p.legenda)}</div>
      </div>
      <div class="pe-direita">
        <fieldset class="pe-campos"${pode ? '' : ' disabled'}>
          <legend class="so-leitor">Post</legend>
          <label class="campo-grupo"><span>Título</span><input class="campo" name="titulo" maxlength="200" required value="${esc(p.titulo)}"></label>
          <div class="grelha-campos">
            <label class="campo-grupo"><span>Obra</span><select class="campo" name="obra" data-sacao="obra-post">${opcoesObras(p.obra_id)}</select></label>
            <label class="campo-grupo"><span>Fase da obra</span><select class="campo" name="fase">${opcoesFases(p.obra_id, p.fase_id)}</select></label>
            <label class="campo-grupo"><span>Mês</span><select class="campo" name="mes">${opcoesMeses(p.mes)}</select></label>
            <label class="campo-grupo"><span>Semana</span><select class="campo" name="semana">${opcoesSemanas(p.semana)}</select></label>
            <label class="campo-grupo"><span>Tipo</span><select class="campo" name="tipo">${opcoes(S.TIPOS_POST, p.tipo)}</select></label>
            <div class="campo-grupo"><span>Redes</span><div class="redes">${Object.entries(S.REDES).map(([k, v]) => `<label class="chip-check"><input type="checkbox" name="redes" value="${k}"${p.redes.includes(k) ? ' checked' : ''}>${v}</label>`).join('')}</div></div>
          </div>
          <div class="campo-grupo">
            <div class="legenda-topo"><label for="pe-legenda">Legenda</label>
              <div class="botoes">
                <button class="btn pequeno texto" type="button" data-sacao="emojis" aria-expanded="false" aria-controls="pe-emojis">${ic('sorriso', 'ic-sm')}Emojis</button>
                <button class="btn pequeno texto" type="button" data-sacao="copiar-legenda">${ic('copiar', 'ic-sm')}Copiar</button>
              </div></div>
            <div class="emojis" id="pe-emojis" hidden>${EMOJIS.map((e) => `<button type="button" data-sacao="emoji" data-e="${e}" aria-label="Inserir ${e}">${e}</button>`).join('')}
              <p class="fraco mini">Mais emojis: tecla Windows + . (ponto) no PC; o teclado de emojis no telemóvel.</p></div>
            <textarea class="campo legenda" id="pe-legenda" name="legenda" maxlength="5000" rows="12" placeholder="Escreve a legenda como vai aparecer: emojis, parágrafos e #hashtags.">${esc(p.legenda)}</textarea>
            <div id="pe-contagem">${htmlContagem(p.legenda)}</div>
          </div>
          <label class="campo-grupo"><span>Notas <small>(para a equipa; não se publica)</small></span><textarea class="campo" name="notas" maxlength="4000" rows="3">${esc(p.notas)}</textarea></label>
          <div class="aprovacao">
            <h3>Aprovação</h3>
            <label class="aprovar"><input type="checkbox" class="visto" name="legenda_aprovada"${p.legenda_aprovada ? ' checked' : ''}><span><b>Legenda aprovada</b>${p.legenda_aprovada ? `<br><span class="fraco mini">por ${esc(p.legenda_aprovada_por_nome || 'equipa')}${p.legenda_aprovada_em ? ` a ${dia(p.legenda_aprovada_em)}` : ''}</span>` : '<br><span class="fraco mini">Mudar a legenda depois de aprovada pede nova aprovação.</span>'}</span></label>
            <label class="aprovar"><input type="checkbox" class="visto" name="fotos_aprovadas"${p.fotos_aprovadas ? ' checked' : ''}><span><b>Fotos aprovadas</b>${p.fotos_aprovadas ? `<br><span class="fraco mini">por ${esc(p.fotos_aprovadas_por_nome || 'equipa')}${p.fotos_aprovadas_em ? ` a ${dia(p.fotos_aprovadas_em)}` : ''}</span>` : '<br><span class="fraco mini">Acrescentar ou tirar fotos pede nova aprovação.</span>'}</span></label>
            <div class="grelha-campos">
              <label class="campo-grupo"><span>Estado</span><select class="campo" name="estado">${opcoes(S.ESTADOS_POST, p.estado)}</select></label>
              ${p.estado === 'publicado' ? `<p class="pequeno suave" style="align-self:end">Publicado${p.publicado_em ? ` a ${dia(p.publicado_em)}` : ''}</p>` : ''}
            </div>
          </div>
        </fieldset>
        <section class="pe-comentarios" id="pe-comentarios" aria-label="Comentários">${htmlComentarios(p)}</section>
      </div>
    </div>
    <div class="dlg-rodape">
      ${pode ? `<button class="btn texto perigo" type="button" data-sacao="apagar-post" data-id="${p.id}" style="margin-right:auto">${ic('apagar', 'ic-sm')}Apagar post</button>` : ''}
      <button class="btn" type="button" data-sacao="fechar-post">Fechar</button>
      ${pode && ['ideia', 'rascunho'].includes(p.estado) ? `<button class="btn" type="button" data-sacao="pedir-aprovacao">Guardar e pedir aprovação</button>` : ''}
      ${pode && p.estado === 'aprovado' ? `<button class="btn" type="button" data-sacao="marcar-publicado">Marcar como publicado</button>` : ''}
      ${pode ? '<button class="btn primario" type="submit">Guardar</button>' : ''}
    </div></form>`;
}
function htmlContagem(t) {
  const v = S.verificarLegenda(t || '');
  return `<p class="contagem fraco mini num"><span${v.caracteres > 2200 ? ' class="erro-msg"' : ''}>${v.caracteres.toLocaleString('pt-PT')} / 2200 caracteres</span> · <span${v.hashtags > 30 ? ' class="erro-msg"' : ''}>${v.hashtags} / 30 hashtags</span></p>
    ${v.avisos.length ? `<ul class="avisos-legenda">${v.avisos.map((a) => `<li>${ic('atencao', 'ic-sm')}${esc(a)}</li>`).join('')}</ul>` : ''}`;
}
function htmlMedia(p) {
  const ms = S.mediaDe(p.id), pode = E.eu.editar;
  const coment = (m) => S.comentariosDe(p.id).filter((c) => c.media_id === m.id && !c.resolvido).length;
  return `<div class="pe-zona" data-sacao-zona>
    ${ms.length ? `<ol class="pe-fotos">${ms.map((m, i) => `<li class="pe-foto" data-mid="${m.id}"${pode ? ' draggable="true"' : ''}>
      <button type="button" class="pe-ver" data-sacao="abrir-media" data-id="${m.id}" title="Abrir em tamanho real">${miniOuIcone(m)}<span class="so-leitor">Abrir ${esc(m.nome_ficheiro)}</span></button>
      <span class="pe-n num">${i + 1}</span>${S.ehVideo(m) ? `<span class="pe-tipo">${ic('video', 'ic-sm')}</span>` : ''}
      ${coment(m) ? `<span class="pe-coment" title="Comentários por resolver">${ic('comentario', 'ic-sm')}${coment(m)}</span>` : ''}
      <div class="pe-acoes">
        ${pode ? `<button type="button" class="icone-botao" data-sacao="mover-media" data-id="${m.id}" data-dir="-1" aria-label="Para trás"${i ? '' : ' disabled'}>${ic('esquerda', 'ic-sm')}</button>
        <button type="button" class="icone-botao" data-sacao="mover-media" data-id="${m.id}" data-dir="1" aria-label="Para a frente"${i < ms.length - 1 ? '' : ' disabled'}>${ic('direita', 'ic-sm')}</button>` : ''}
        <button type="button" class="icone-botao" data-sacao="descarregar-media" data-id="${m.id}" aria-label="Descarregar ${esc(m.nome_ficheiro)}">${ic('instalar', 'ic-sm')}</button>
        ${pode ? `<button type="button" class="icone-botao" data-sacao="apagar-media" data-id="${m.id}" aria-label="Tirar ${esc(m.nome_ficheiro)}">${ic('apagar', 'ic-sm')}</button>` : ''}
      </div>
    </li>`).join('')}</ol>` : '<p class="fraco pequeno pe-sem">Ainda sem fotos.</p>'}
    ${pode ? `<label class="pe-carregar">${ic('imagem')}<span><b>Arrasta fotos ou vídeos para aqui</b>, cola-os (Ctrl+V) ou <u>escolhe do computador</u>.<br><span class="fraco mini">Até 50 MB cada. Arrasta as fotos para mudar a ordem do carrossel.</span></span>
      <input type="file" name="media" multiple accept="image/*,video/*,.heic" class="so-leitor"></label>
      <label class="original"><input type="checkbox" id="pe-original"> <span>Manter os originais <span class="fraco">(por defeito as fotos grandes ficam com 2048 px, que chega para o Instagram e poupa espaço)</span></span></label>` : ''}
    <p class="pe-progresso pequeno suave" role="status"></p>
    ${ms.length ? `<div class="botoes"><button class="btn pequeno" type="button" data-sacao="descarregar-todas">${ic('instalar', 'ic-sm')}Descarregar todas (${ms.length})</button>
      <span class="fraco mini" style="align-self:center">${tamanho(ms.reduce((a, m) => a + Number(m.tamanho || 0), 0))}</span></div>` : ''}
  </div>`;
}
function htmlPrevia(p, legenda) {
  const ms = S.mediaDe(p.id);
  return `<div class="previa" aria-label="Pré-visualização do post">
    <div class="previa-topo"><span class="avatar pequeno">DC</span><b>discovercasa</b></div>
    <div class="previa-fotos">${ms.length ? ms.map((m) => `<div class="previa-foto">${miniOuIcone(m)}</div>`).join('') : `<div class="previa-foto vazia">${ic('camara')}<span>Sem fotos</span></div>`}</div>
    ${ms.length > 1 ? `<div class="previa-pontos" aria-hidden="true">${ms.map((_, i) => `<i${i ? '' : ' class="on"'}></i>`).join('')}</div>` : ''}
    <p class="previa-legenda"><b>discovercasa</b> ${esc(legenda || '')}</p>
    <button type="button" class="btn pequeno texto" data-sacao="previa-mais">mais</button>
  </div>`;
}
function htmlComentarios(p) {
  const cs = S.comentariosDe(p.id), ms = S.mediaDe(p.id);
  const nFoto = (id) => ms.findIndex((m) => m.id === id) + 1;
  return `<h3>${ic('comentario', 'ic-sm')}Comentários <span class="fraco num">${cs.filter((c) => !c.resolvido).length || ''}</span></h3>
    ${cs.length ? `<ul class="pe-lista-coment">${cs.map((c) => `<li class="${c.resolvido ? 'resolvido' : ''}">
      <span class="avatar pequeno">${esc(iniciais(c.autor_nome))}</span>
      <div><p class="fraco mini">${esc(c.autor_nome || 'Equipa')} · ${dia(c.criado_em)}${c.media_id && nFoto(c.media_id) ? ` · sobre a foto ${nFoto(c.media_id)}` : ''}${c.resolvido ? ' · resolvido' : ''}</p><p class="pequeno">${esc(c.texto)}</p>
        <div class="botoes">${E.eu.editar || c.autor_id === E.eu.id ? `<button class="btn pequeno texto" type="button" data-sacao="resolver-coment" data-id="${c.id}">${c.resolvido ? 'Reabrir' : 'Resolvido'}</button>
          <button class="btn pequeno texto perigo" type="button" data-sacao="apagar-coment" data-id="${c.id}">Apagar</button>` : ''}</div></div></li>`).join('')}</ul>`
      : '<p class="suave pequeno">Sem comentários. Usa-os para pedir mudanças antes de aprovar (ex.: «consegues tirar aquele saco?»).</p>'}
    <div class="pe-novo-coment">
      <textarea class="campo" id="pe-coment-texto" rows="2" maxlength="2000" placeholder="Escreve um comentário…" aria-label="Comentário"></textarea>
      <div class="botoes">${ms.length ? `<select class="seletor" id="pe-coment-foto" aria-label="Sobre"><option value="">Sobre o post</option>${ms.map((m, i) => `<option value="${m.id}">Sobre a foto ${i + 1}</option>`).join('')}</select>` : ''}
        <button class="btn pequeno" type="button" data-sacao="comentar" data-id="${p.id}">Comentar</button></div>
    </div>`;
}

// ---------------------------------------------------------------- diálogos: obra e fase
function dlgObra(o) {
  return `<form data-sform="obra"${o ? ` data-id="${o.id}"` : ''}>${cabeca(o ? 'Editar obra' : 'Nova obra', o ? '' : 'As fases servem para saber em que ponto a obra está e quando ir tirar fotos.')}
    <div class="dlg-corpo">
      <label class="campo-grupo"><span>Nome</span><input class="campo" name="nome" maxlength="120" required autocomplete="off" value="${esc(o ? o.nome : '')}" placeholder="Ex.: Matosinhos"></label>
      <label class="campo-grupo"><span>Descrição <small>(opcional)</small></span><textarea class="campo" name="descricao" maxlength="2000" rows="3">${esc(o ? o.descricao : '')}</textarea></label>
      ${o ? `<label class="aprovar"><input type="checkbox" class="visto" name="arquivada"${o.ativa ? '' : ' checked'}><span><b>Obra arquivada</b><br><span class="fraco mini">Sai da lista e dos filtros; os posts e as fases ficam guardados.</span></span></label>`
        : `<fieldset class="campo-grupo modelo-fases"><legend>Fases <small>(podes acrescentar mais depois)</small></legend>${S.FASES_MODELO.map((f) => `<label class="chip-check"><input type="checkbox" name="fases" value="${esc(f)}" checked>${esc(f)}</label>`).join('')}</fieldset>`}
      <p class="erro-msg pequeno" role="alert"></p>
    </div>
    <div class="dlg-rodape"><button class="btn" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">${o ? 'Guardar' : 'Criar obra'}</button></div></form>`;
}
function opcoesPosicaoFase(obraId, atualId) {
  const fs = S.fasesDe(obraId).filter((f) => f.id !== atualId);
  const atualPos = atualId ? S.fasesDe(obraId).findIndex((f) => f.id === atualId) + 1 : fs.length + 1;
  return fs.map((f, i) => `<option value="${i + 1}"${i + 1 === atualPos ? ' selected' : ''}>${i + 1} · antes de «${esc(f.nome)}»</option>`).join('')
    + `<option value="${fs.length + 1}"${fs.length + 1 === atualPos ? ' selected' : ''}>${fs.length + 1} · no fim</option>`;
}
function dlgFase(obraId, f) {
  const o = S.obra(obraId);
  return `<form data-sform="fase" data-obra="${obraId}"${f ? ` data-id="${f.id}"` : ''}>${cabeca(f ? esc(f.nome) : 'Nova fase', esc(o.nome))}
    <div class="dlg-corpo">
      <div class="grelha-campos">
        <label class="campo-grupo"><span>Nome</span><input class="campo" name="nome" maxlength="120" required value="${esc(f ? f.nome : '')}" placeholder="Ex.: Isolamento"></label>
        <label class="campo-grupo"><span>Posição</span><select class="campo" name="posicao">${opcoesPosicaoFase(obraId, f && f.id)}</select></label>
        <label class="campo-grupo"><span>Estado</span><select class="campo" name="estado">${opcoes(S.ESTADOS_FASE, f ? f.estado : 'prevista')}</select></label>
        <label class="campo-grupo"><span>Período <small>(ex.: Set - Out)</small></span><input class="campo" name="periodo" maxlength="80" value="${esc(f ? f.periodo : '')}"></label>
        <label class="campo-grupo"><span>Posts previstos</span><input class="campo" name="posts_previstos" type="number" min="0" max="99" inputmode="numeric" value="${f && f.posts_previstos != null ? f.posts_previstos : ''}"></label>
        <label class="campo-grupo"><span>Fotos</span><select class="campo" name="fotos" data-sacao="fotos-fase">${opcoes(S.FOTOS_FASE, f ? f.fotos : 'por_tirar')}</select></label>
        <label class="campo-grupo" data-visita${!f || f.fotos !== 'visita_marcada' ? ' hidden' : ''}><span>Dia da visita</span><input class="campo" name="visita_em" type="date" value="${f && f.visita_em ? f.visita_em : ''}"></label>
      </div>
      <label class="campo-grupo"><span>Notas <small>(opcional)</small></span><textarea class="campo" name="notas" maxlength="2000" rows="2">${esc(f ? f.notas : '')}</textarea></label>
      ${f ? `<p class="fraco mini">As fases não se apagam: ficam na lista da obra. Se já não se aplica, deixa uma nota.${f.concluida_em ? ` Concluída a ${dia(f.concluida_em)}.` : ''}</p>` : ''}
      <p class="erro-msg pequeno" role="alert"></p>
    </div>
    <div class="dlg-rodape"><button class="btn" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">${f ? 'Guardar' : 'Acrescentar fase'}</button></div></form>`;
}
function dlgVisita(f) {
  const amanha = new Date(Date.now() + 86400000).toISOString().slice(0, 10);
  return `<form data-sform="visita" data-id="${f.id}">${cabeca('Marcar visita para fotos', `${esc(S.obra(f.obra_id).nome)} · ${esc(f.nome)}`)}
    <div class="dlg-corpo"><label class="campo-grupo"><span>Dia</span><input class="campo" name="visita_em" type="date" required value="${f.visita_em || amanha}"></label>
      <p class="erro-msg pequeno" role="alert"></p></div>
    <div class="dlg-rodape"><button class="btn" type="button" data-acao="fechar-dlg">Cancelar</button><button class="btn primario" type="submit">Marcar</button></div></form>`;
}

// ---------------------------------------------------------------- editor aberto: abrir, atualizar partes, fechar
const formPost = () => ctx && ctx.dlg.open && $('form[data-sform="post"]', ctx.dlg);
export function abrirPost(id) {
  const p = S.post(Number(id));
  if (!p) return;
  sujo = false;
  abrirDialogo(ctx.dlg, htmlEditor(p));
  ctx.dlg.classList.add('largo');
  S.hidratar(ctx.dlg);
}
function redesenharEditor() {
  const f = formPost();
  if (!f) return;
  const p = S.post(Number(f.dataset.id));
  if (!p) { fecharEditor(true); return; }
  const corpo = $('.dlg-corpo', f), y = corpo ? corpo.scrollTop : 0;
  ctx.dlg.innerHTML = htmlEditor(p);
  const novo = $('.dlg-corpo', ctx.dlg); if (novo) novo.scrollTop = y;
  S.hidratar(ctx.dlg);
}
function redesenharMedia() {
  const f = formPost();
  if (!f) return;
  const p = S.post(Number(f.dataset.id));
  if (!p) return;
  $('#pe-media', f).innerHTML = htmlMedia(p);
  $('#pe-previa', f).innerHTML = htmlPrevia(p, f.elements.legenda.value);
  const nc = $('#pe-comentarios', f), texto = $('#pe-coment-texto', f).value;
  nc.innerHTML = htmlComentarios(p); $('#pe-coment-texto', f).value = texto;
  S.hidratar(f);
}
function fecharEditor(forcar) {
  if (!forcar && sujo && !confirm('Tens alterações por guardar neste post. Fechar sem guardar?')) return false;
  sujo = false;
  fecharDialogo(ctx.dlg);
  return true;
}
// depois de qualquer mudança (minha ou de outra pessoa, em direto): atualiza as partes do editor aberto que não se escrevem
export function aoMudar() {
  if (formPost()) redesenharMedia();
}
// depois de desenhar a página: imagens assinadas e o post/obra pedidos na rota
export function depoisDeDesenhar(raiz) { S.hidratar(raiz); }
export function irPara(alvo) {
  const m = /^(post|obra)-(\d+)$/.exec(alvo || '');
  if (!m) return;
  if (m[1] === 'post') return abrirPost(m[2]);
  const el = document.getElementById(alvo);
  if (!el) return;
  el.scrollIntoView({ block: 'center', behavior: mov() ? 'smooth' : 'auto' });
  el.classList.remove('alvo'); void el.offsetWidth; el.classList.add('alvo');
}

// ---------------------------------------------------------------- carregar fotos (escolher, arrastar, colar)
async function enviar(postId, lista) {
  const ficheiros = [...lista].filter((f) => /^(image|video)\//.test(f.type) || /\.(heic|jpe?g|png|webp|mp4|mov)$/i.test(f.name));
  if (!ficheiros.length) { aviso('Só se podem acrescentar fotos ou vídeos.', { icone: 'atencao' }); return; }
  const grandes = ficheiros.filter((f) => f.size > S.MAXIMO);
  if (grandes.length) aviso(`Demasiado grande (máximo 50 MB): ${esc(grandes.map((f) => f.name).join(', '))}. Para vídeos maiores, deixa uma nota no post.`, { icone: 'atencao', duracao: 8 });
  const ok = ficheiros.filter((f) => f.size <= S.MAXIMO);
  if (!ok.length) return;
  const prog = () => $('.pe-progresso', ctx.dlg);
  let ordem = S.mediaDe(postId).length, feitos = 0;
  try {
    for (const f of ok) {
      if (prog()) prog().textContent = `A carregar ${feitos + 1} de ${ok.length}: ${f.name}…`;
      await S.carregarMedia(postId, f, ++ordem, !!($('#pe-original', ctx.dlg) || {}).checked);
      feitos++;
    }
  } catch (e) {
    aviso('Não foi possível carregar: ' + esc(e.message || e), { icone: 'atencao' });
  }
  await S.carregarSocial();
  redesenharMedia();
  if (feitos) aviso(feitos === 1 ? 'Foto acrescentada.' : `${feitos} fotos acrescentadas.`, { icone: 'certo', duracao: 3 });
  ctx.depois();
}

// ---------------------------------------------------------------- ligar os eventos
export function ligar(c) {
  ctx = c;
  const dlg = c.dlg;
  dlg.addEventListener('close', () => {
    dlg.classList.remove('largo');
    if (/^#\/social\/(obras\/)?post-\d+$/.test(location.hash)) history.replaceState(null, '', '#/social');
  });
  // mudar de página com o editor aberto: fecha-o (e pergunta antes, se houver alterações por guardar)
  window.addEventListener('hashchange', (e) => {
    const f = formPost();
    if (!f || location.hash === `#/social/post-${f.dataset.id}`) return;
    if (sujo && !confirm('Tens alterações por guardar neste post. Sair sem guardar?')) { history.replaceState(null, '', e.oldURL.slice(e.oldURL.indexOf('#'))); return; }
    sujo = false;
    dlg.classList.remove('largo');
    dlg.close();
  });
  // Esc e clique fora: não perder uma legenda por guardar
  dlg.addEventListener('cancel', (e) => { if (formPost() && sujo && !confirm('Tens alterações por guardar neste post. Fechar sem guardar?')) { e.preventDefault(); e.stopImmediatePropagation(); } else sujo = false; }, true);
  dlg.addEventListener('click', (e) => { if (e.target === dlg && formPost() && sujo && !confirm('Tens alterações por guardar neste post. Fechar sem guardar?')) e.stopImmediatePropagation(); else if (e.target === dlg) sujo = false; }, true);

  document.addEventListener('click', async (e) => {
    const el = e.target.closest('[data-sacao]');
    if (!el || el.matches('select, input')) return;
    const id = Number(el.dataset.id);
    switch (el.dataset.sacao) {
      case 'novo-post': return abrirDialogo(dlg, dlgNovoPost(el.dataset.mes, el.dataset.semana), { estreito: true });
      case 'so-por-aprovar': {
        e.preventDefault();
        const p = E.posts.find((x) => x.estado === 'por_aprovar');
        if (p) location.hash = `#/social/post-${p.id}`; else aviso('Nenhum post à espera de aprovação.', { duracao: 3 });
        return;
      }
      case 'nova-obra': return abrirDialogo(dlg, dlgObra(null), { estreito: true });
      case 'editar-obra': return abrirDialogo(dlg, dlgObra(S.obra(id)), { estreito: true });
      case 'nova-fase': return abrirDialogo(dlg, dlgFase(id, null));
      case 'editar-fase': { const f = S.fase(id); return abrirDialogo(dlg, dlgFase(f.obra_id, f)); }
      case 'marcar-visita': return abrirDialogo(dlg, dlgVisita(S.fase(id)), { estreito: true });
      case 'fotos-tiradas':
        if (await c.tentar(() => S.mudarFase(id, { fotos: 'tiradas' }))) { aviso('Fotos marcadas como tiradas.', { icone: 'certo', duracao: 3 }); c.depois(); }
        return;
      case 'fechar-post': return fecharEditor(false);
      case 'pe-aba': {
        aba = el.dataset.valor;
        const f = el.closest('form');
        $$('[data-sacao="pe-aba"]', f).forEach((b) => b.setAttribute('aria-pressed', b === el));
        $('#pe-media', f).hidden = aba !== 'fotos'; $('#pe-previa', f).hidden = aba !== 'previa';
        if (aba === 'previa') { $('#pe-previa', f).innerHTML = htmlPrevia(S.post(Number(f.dataset.id)), f.elements.legenda.value); S.hidratar(f); }
        return;
      }
      case 'previa-mais': { const pv = el.closest('.previa'); pv.classList.toggle('aberta'); el.textContent = pv.classList.contains('aberta') ? 'menos' : 'mais'; return; }
      case 'emojis': { const box = $('#pe-emojis'); box.hidden = !box.hidden; el.setAttribute('aria-expanded', !box.hidden); return; }
      case 'emoji': {
        const t = $('#pe-legenda'), ini = t.selectionStart ?? t.value.length, fim = t.selectionEnd ?? ini;
        t.setRangeText(el.dataset.e, ini, fim, 'end');
        t.focus();
        t.dispatchEvent(new Event('input', { bubbles: true }));
        return;
      }
      case 'copiar-legenda': {
        const t = $('#pe-legenda').value;
        try { await navigator.clipboard.writeText(t); aviso('Legenda copiada. Cola-a no Instagram ou no Facebook.', { icone: 'certo', duracao: 3 }); }
        catch (_) { $('#pe-legenda').select(); aviso('Selecionei a legenda: copia com Ctrl+C.', { duracao: 4 }); }
        return;
      }
      case 'mover-media': {
        const f = formPost(), ids = $$('.pe-foto', f).map((x) => Number(x.dataset.mid));
        const i = ids.indexOf(id), j = i + Number(el.dataset.dir);
        if (j < 0 || j >= ids.length) return;
        [ids[i], ids[j]] = [ids[j], ids[i]];
        if (await c.tentar(() => S.ordenarMedia(ids))) redesenharMedia();
        return;
      }
      case 'apagar-media': {
        const m = E.media.find((x) => x.id === id);
        if (!confirm(`Tirar «${m.nome_ficheiro}» deste post? O ficheiro é apagado.`)) return;
        if (await c.tentar(() => S.apagarMedia(m))) { redesenharMedia(); c.depois(); }
        return;
      }
      case 'abrir-media': case 'descarregar-media': {
        const m = E.media.find((x) => x.id === id);
        const janela = el.dataset.sacao === 'abrir-media' ? window.open('about:blank', '_blank') : null;
        try {
          if (janela) { await S.assinar([m.caminho]); janela.location.href = S.urlEmCache(m.caminho); }
          else { const a = document.createElement('a'); a.href = await S.urlDescarregar(m); a.download = m.nome_ficheiro; document.body.append(a); a.click(); a.remove(); }
        } catch (err) { if (janela) janela.close(); aviso('Não foi possível abrir: ' + esc(err.message || err), { icone: 'atencao' }); }
        return;
      }
      case 'descarregar-todas': {
        const f = formPost(), ms = S.mediaDe(Number(f.dataset.id));
        for (const m of ms) {
          try { const a = document.createElement('a'); a.href = await S.urlDescarregar(m); a.download = m.nome_ficheiro; document.body.append(a); a.click(); a.remove(); }
          catch (_) { /* segue para a próxima */ }
          await new Promise((r) => setTimeout(r, 400));
        }
        return;
      }
      case 'comentar': {
        const f = formPost(), t = $('#pe-coment-texto', f), sel = $('#pe-coment-foto', f);
        const texto = t.value.trim();
        if (!texto) return t.focus();
        if (await c.tentar(() => S.comentar(id, texto, sel ? Number(sel.value) || null : null))) { t.value = ''; redesenharMedia(); c.depois(); }
        return;
      }
      case 'resolver-coment': {
        const cm = E.comentarios.find((x) => x.id === id);
        if (await c.tentar(() => S.mudarComentario(id, { resolvido: !cm.resolvido }))) { redesenharMedia(); c.depois(); }
        return;
      }
      case 'apagar-coment':
        if (!confirm('Apagar este comentário?')) return;
        if (await c.tentar(() => S.apagarComentario(id))) { redesenharMedia(); c.depois(); }
        return;
      case 'apagar-post': {
        const p = S.post(id);
        if (!confirm(`Apagar o post «${p.titulo}» com as suas fotos e comentários?`)) return;
        if (await c.tentar(() => S.apagarPost(p))) { fecharEditor(true); aviso('Post apagado.', { icone: 'certo', duracao: 3 }); c.depois(); }
        return;
      }
      case 'pedir-aprovacao': case 'marcar-publicado': {
        const f = formPost();
        f.elements.estado.value = el.dataset.sacao === 'pedir-aprovacao' ? 'por_aprovar' : 'publicado';
        f.requestSubmit();
        return;
      }
    }
  });

  document.addEventListener('change', async (e) => {
    const el = e.target;
    if (el.closest('form[data-sform="post"]') && el.name && !['media'].includes(el.name) && !el.id.startsWith('pe-coment')) sujo = true;
    switch (el.dataset.sacao) {
      case 'filtro-obra': filtroObra = el.value; return c.desenhar(false);
      case 'obra-post': { const f = el.closest('form'); f.elements.fase.innerHTML = opcoesFases(Number(el.value) || null); return; }
      case 'fotos-fase': { const f = el.closest('form'); $('[data-visita]', f).hidden = el.value !== 'visita_marcada'; return; }
    }
    if (el.name === 'media' && el.closest('form[data-sform="post"]')) {
      const f = el.closest('form');
      await enviar(Number(f.dataset.id), el.files);
      el.value = '';
    }
  });
  document.addEventListener('input', (e) => {
    const f = e.target.closest('form[data-sform="post"]');
    if (!f || !e.target.name) return;
    sujo = true;
    if (e.target.name === 'legenda') {
      $('#pe-contagem', f).innerHTML = htmlContagem(e.target.value);
      const leg = $('#pe-previa .previa-legenda', f);
      if (leg) leg.innerHTML = `<b>discovercasa</b> ${esc(e.target.value)}`;
    }
  });

  // arrastar ficheiros para o editor, e arrastar as fotos para mudar a ordem
  let arrastada = null;
  document.addEventListener('dragstart', (e) => { const li = e.target.closest && e.target.closest('.pe-foto'); if (li) { arrastada = li; li.classList.add('a-arrastar'); e.dataTransfer.effectAllowed = 'move'; } });
  document.addEventListener('dragend', () => { if (arrastada) arrastada.classList.remove('a-arrastar'); arrastada = null; $$('.pe-zona.sobre').forEach((z) => z.classList.remove('sobre')); });
  document.addEventListener('dragover', (e) => {
    const zona = e.target.closest && e.target.closest('[data-sacao-zona]');
    if (!zona || !E.eu.editar) return;
    e.preventDefault();
    if (arrastada) {
      const alvo = e.target.closest('.pe-foto');
      if (alvo && alvo !== arrastada) {
        const r = alvo.getBoundingClientRect(), depoisDe = (e.clientX - r.left) > r.width / 2;
        alvo.parentNode.insertBefore(arrastada, depoisDe ? alvo.nextSibling : alvo);
      }
    } else zona.classList.add('sobre');
  });
  document.addEventListener('dragleave', (e) => { const zona = e.target.closest && e.target.closest('[data-sacao-zona]'); if (zona && !zona.contains(e.relatedTarget)) zona.classList.remove('sobre'); });
  document.addEventListener('drop', async (e) => {
    const zona = e.target.closest && e.target.closest('[data-sacao-zona]');
    if (!zona || !E.eu.editar) return;
    e.preventDefault();
    zona.classList.remove('sobre');
    const f = formPost();
    if (arrastada) {
      const ids = $$('.pe-foto', f).map((x) => Number(x.dataset.mid));
      arrastada = null;
      if (await c.tentar(() => S.ordenarMedia(ids))) redesenharMedia();
    } else if (e.dataTransfer.files.length) await enviar(Number(f.dataset.id), e.dataTransfer.files);
  });
  document.addEventListener('paste', async (e) => {
    const f = formPost();
    if (!f || !E.eu.editar) return;
    const ficheiros = [...(e.clipboardData ? e.clipboardData.files : [])];
    if (!ficheiros.length) return;
    e.preventDefault();
    await enviar(Number(f.dataset.id), ficheiros);
  });

  document.addEventListener('submit', async (e) => {
    const f = e.target, tipo = f.dataset.sform;
    if (!tipo) return;
    e.preventDefault();
    const v = (n) => (f.elements[n] ? f.elements[n].value.trim() : '');
    const botao = f.querySelector('[type=submit]');
    if (botao) botao.disabled = true;
    try {
      switch (tipo) {
        case 'novo-post': {
          let novo = null;
          const ok = await c.tentar(async () => { novo = await S.criarPost({ titulo: v('titulo'), obra_id: Number(v('obra')) || null, fase_id: Number(v('fase')) || null, mes: v('mes'), semana: Number(v('semana')), tipo: v('tipo') }); }, f);
          if (ok) { c.depois(); location.hash = `#/social/post-${novo.id}`; }
          return;
        }
        case 'post': {
          const id = Number(f.dataset.id);
          const campos = { titulo: v('titulo'), obra_id: Number(v('obra')) || null, fase_id: Number(v('fase')) || null, mes: v('mes'), semana: Number(v('semana')), tipo: v('tipo'),
            redes: $$('input[name=redes]:checked', f).map((x) => x.value), legenda: f.elements.legenda.value.replace(/\s+$/, ''), notas: v('notas'), estado: v('estado'),
            legenda_aprovada: f.elements.legenda_aprovada.checked, fotos_aprovadas: f.elements.fotos_aprovadas.checked };
          const antes = S.post(id);
          const ok = await c.tentar(() => S.mudarPost(id, campos), f);
          if (!ok) return;
          sujo = false;
          const depois = S.post(id);
          aviso(depois.estado !== antes.estado ? `Guardado. O post está agora «${S.ESTADOS_POST[depois.estado]}».` : 'Guardado.', { icone: 'certo', duracao: 3 });
          redesenharEditor();
          c.depois();
          return;
        }
        case 'obra': {
          const id = Number(f.dataset.id);
          const ok = await c.tentar(() => (id ? S.mudarObra(id, { nome: v('nome'), descricao: v('descricao'), ativa: !f.elements.arquivada.checked })
            : S.criarObra({ nome: v('nome'), descricao: v('descricao') }, $$('input[name=fases]:checked', f).map((x) => x.value))), f);
          if (ok) { fecharDialogo(dlg); aviso(id ? 'Obra guardada.' : 'Obra criada.', { icone: 'certo', duracao: 3 }); c.depois(); }
          return;
        }
        case 'fase': {
          const obraId = Number(f.dataset.obra), id = Number(f.dataset.id);
          const n = v('posts_previstos');
          const campos = { nome: v('nome'), estado: v('estado'), periodo: v('periodo'), posts_previstos: n === '' ? null : Number(n), fotos: v('fotos'),
            visita_em: v('fotos') === 'visita_marcada' ? v('visita_em') || null : null, notas: v('notas') };
          const ok = await c.tentar(async () => {
            if (!id) return S.criarFase(obraId, campos, Number(v('posicao')));
            const antes = S.fasesDe(obraId).findIndex((x) => x.id === id) + 1;
            await S.mudarFase(id, campos);
            if (Number(v('posicao')) !== antes) await S.moverFase(S.fase(id), Number(v('posicao')));
          }, f);
          if (ok) { fecharDialogo(dlg); c.depois(); }
          return;
        }
        case 'visita': {
          const ok = await c.tentar(() => S.mudarFase(Number(f.dataset.id), { fotos: 'visita_marcada', visita_em: v('visita_em') }), f);
          if (ok) { fecharDialogo(dlg); aviso('Visita marcada. A equipa foi avisada.', { icone: 'certo', duracao: 3 }); c.depois(); }
          return;
        }
      }
    } finally { if (botao && botao.isConnected) botao.disabled = false; }
  });
}

export const animarEntrada = (v) => entrar($$('.mes, .obra, .visita, .social-barra', v));
