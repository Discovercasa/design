// Aba «Materiais» do hub (#/materiais) e o bloco «Materiais do Hub» das páginas dos projetos que usam a lista
// (campo "materiais" em public/dados/projetos/<id>.json). Só de consulta: os dados vêm do Hub (migração 0016) e lêem-se
// com o módulo comum /js/materiais.js, que as aplicações também usam.
import * as M from '../materiais.js';
import { E } from './dados.js';
import { esc, ic, dia } from './util.js';

const MAIS = 200;
export const filtro = { q: '', categoria: '', tipo: '', fornecedor: '', limite: MAIS };

/** Lê os materiais uma vez por sessão (ou de novo com forcar). Devolve uma promessa; o estado fica em E.mat / E.matErro. */
let pedido = null;
export function garantir(forcar = false) {
  if (pedido && !forcar) return pedido;
  E.matErro = null;
  pedido = M.carregar(window.Design.sb).then((L) => { E.mat = L; }).catch((e) => { E.mat = null; E.matErro = e.message || String(e); });
  return pedido;
}
export const precisa = () => !pedido;

const eur = (v, casas = 2) => (v == null ? '—' : Number(v).toLocaleString('pt-PT', { style: 'currency', currency: 'EUR', minimumFractionDigits: casas, maximumFractionDigits: Math.max(casas, 4) }));
const pct = (v) => { const f = M.fracao(v); return f == null ? '—' : (f * 100).toLocaleString('pt-PT', { maximumFractionDigits: 2 }) + ' %'; };
const quando = (t) => (t ? new Date(t).toLocaleString('pt-PT', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '');
const porUnidade = (u) => (u ? ` / ${esc(u)}` : '');
// the Hub writes some fields in lower case without accents («sim», «nao», «imediata»): shown tidy, the CSV keeps them
const SIM_NAO = { sim: 'Sim', nao: 'Não', 'não': 'Não' };
const arrumar = (v) => { const t = String(v ?? '').trim(); return SIM_NAO[t.toLowerCase()] || (t ? t[0].toUpperCase() + t.slice(1) : ''); };

function seta(v) {
  if (!v || v.pct == null) return '';
  const sobe = v.pct > 0;
  const t = `${sobe ? '+' : '−'}${Math.abs(v.pct * 100).toLocaleString('pt-PT', { maximumFractionDigits: 1 })} %`;
  return `<span class="mat-var ${sobe ? 'mat-sobe' : 'mat-desce'}" title="De ${eur(v.de)} para ${eur(v.para)}${v.dia ? ' a ' + esc(dia(v.dia)) : ''}">${sobe ? '▲' : '▼'} ${t}</span>`;
}
function grafico(h) {
  const pts = h.filter((x) => x.preco != null);
  if (pts.length < 2) return '';
  const vs = pts.map((x) => Number(x.preco)), lo = Math.min(...vs), hi = Math.max(...vs), w = 80, a = 20;
  const xy = vs.map((v, i) => `${(i * w / (vs.length - 1)).toFixed(1)},${(hi === lo ? a / 2 : a - 2 - (v - lo) / (hi - lo) * (a - 4)).toFixed(1)}`).join(' ');
  const titulo = pts.map((x) => `${dia(x.data_atualizacao || x.registado_em)}: ${eur(x.preco)}`).join('\n');
  return `<svg class="spark" viewBox="0 0 ${w} ${a}" role="img" aria-label="Histórico do preço"><title>${esc(titulo)}</title><polyline points="${xy}" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>`;
}

function linhaPreco(p) {
  const extra = [p.dimensoes, p.detalhes].filter(Boolean).map(esc).join(' · ');
  const prazo = p.prazo_dias != null ? `${p.prazo_dias} ${p.prazo_dias === 1 ? 'dia' : 'dias'}` : '';
  return `<tr>
    <td>${esc(p.fornecedor || '—')}</td>
    <td class="mat-texto">${esc(p.designacao || '')}${extra ? `<div class="fraco mini">${extra}</div>` : ''}</td>
    <td class="num">${eur(p.preco)}${porUnidade(p.unidade)}</td><td class="num">${pct(p.desconto)}</td>
    <td class="num"><b>${eur(p.preco_desconto)}</b></td><td class="num">${pct(p.iva)}</td>
    <td class="mat-texto">${esc(arrumar(p.disponibilidade))}${prazo ? `<div class="fraco mini">${prazo}</div>` : ''}</td>
    <td class="mat-texto">${esc(arrumar(p.transporte))}${p.transporte_incluido ? `<div class="fraco mini">Incluído no preço: ${esc(arrumar(p.transporte_incluido))}</div>` : ''}</td>
    <td>${esc(dia(p.data_atualizacao))}</td><td>${grafico(p.historico)} ${seta(p.variacao)}</td>
  </tr>`;
}
function item(m) {
  const b = m.melhor, n = m.precos.length;
  return `<li class="mat" id="m-${esc(m.id)}"><details>
    <summary>
      <span class="mat-nome"><b>${esc(m.nome)}</b>${m.tipo ? ` <span class="fraco pequeno">${esc(M.TIPOS[m.tipo] || m.tipo)}</span>` : ''}</span>
      <span class="mat-preco">${b ? `desde <b>${eur(b.preco_desconto)}</b>${porUnidade(b.unidade)} <span class="fraco pequeno">${esc(b.fornecedor)}</span>` : '<span class="fraco pequeno">sem preço</span>'}</span>
      <span class="mat-meta fraco pequeno">${n} ${n === 1 ? 'preço' : 'preços'} ${seta(b && b.variacao)}</span>
    </summary>
    ${n ? `<div class="rolar-x"><table class="tabela mat-tabela"><thead><tr><th>Fornecedor</th><th>Designação</th><th class="num">Preço</th>
      <th class="num">Desconto</th><th class="num">Com desconto</th><th class="num">IVA</th><th>Disponibilidade</th><th>Transporte</th>
      <th>Data do preço</th><th>Histórico</th></tr></thead><tbody>${m.precos.map(linhaPreco).join('')}</tbody></table></div>`
      : '<p class="suave pequeno" style="padding:12px 16px">Ainda sem preços deste material.</p>'}
  </details></li>`;
}

export function lista() {
  const r = M.procurar(E.mat, filtro.q, filtro);
  if (!r.length) return '<p class="vazio">Nenhum material com estes filtros.</p>';
  const ver = r.slice(0, filtro.limite);
  const grupos = new Map();   // by category key (the list comes sorted: categories, then those without one)
  for (const m of ver) { const g = m.categoria_nome || 'Sem categoria'; (grupos.get(g) || grupos.set(g, []).get(g)).push(m); }
  return [...grupos].map(([cat, ms]) => `<section class="mat-grupo"><h2 class="mat-cat">${esc(cat)} <span class="num fraco">${ms.length}</span></h2>
    <ul class="mat-lista">${ms.map(item).join('')}</ul></section>`).join('')
    + (r.length > ver.length ? `<p class="suave pequeno mat-rodape">A mostrar ${ver.length} de ${r.length}. <button class="btn pequeno" type="button" data-acao="mat-mais">Mostrar mais</button></p>` : '');
}

export function pagina() {
  const L = E.mat;
  const cab = `<div class="cabeca-pagina"><div class="texto"><h1>Materiais e preços</h1>
    <p class="suave">Do Hub, só de consulta: os materiais, o preço de cada fornecedor (com desconto e IVA) e o histórico dos preços.
      O Hub atualiza-os nos dias úteis às 6h (Lisboa). Servem a Orçamentação, o Build Your House, o Gerador e o Step Inside.</p>
    ${L ? `<div class="para-ti"><span class="chip">${ic('pasta', 'ic-sm')}<span class="num">${L.n.materiais}</span> materiais</span>
      <span class="chip">${ic('pessoa', 'ic-sm')}<span class="num">${L.n.fornecedores}</span> fornecedores</span>
      <span class="chip">${ic('custo', 'ic-sm')}<span class="num">${L.n.precos}</span> preços</span>
      ${L.atualizado ? `<span class="chip">${ic('certo', 'ic-sm')}Atualizado ${esc(quando(L.atualizado))}</span>` : ''}</div>` : ''}
  </div>
  ${L && L.n.materiais ? `<div class="botoes"><button class="btn" type="button" data-acao="mat-csv" title="Descarrega os materiais da lista abaixo (com os filtros) para o Excel">${ic('instalar')}Descarregar CSV</button></div>` : ''}
  </div>`;
  if (E.matErro) return cab + `<div class="nota" style="border-color:var(--erro)">${ic('atencao')}<p><b>Os materiais ainda não estão disponíveis.</b> A base de dados precisa da migração 0016 (tabelas hub_*). <span class="fraco">(${esc(E.matErro)})</span></p></div>`;
  if (!L) return cab + '<p class="vazio">A carregar os materiais…</p>';
  if (!L.n.materiais) return cab + '<p class="vazio">Ainda sem materiais. O Hub envia a lista nos dias úteis às 6h (Lisboa): aparece aqui depois do próximo envio.</p>';
  return cab + `<div class="mat-filtros">
      <label class="so-leitor" for="mat-q">Procurar material</label>
      <input class="campo" id="mat-q" type="search" data-mat="q" placeholder="Procurar: nome, designação, dimensões, fornecedor…" value="${esc(filtro.q)}" autocomplete="off">
      <select class="campo" data-mat="categoria" aria-label="Categoria"><option value="">Todas as categorias</option>${L.categorias.map((c) => `<option value="${esc(c.chave)}"${c.chave === filtro.categoria ? ' selected' : ''}>${esc(c.nome)}</option>`).join('')}</select>
      ${L.tipos.length > 1 ? `<select class="campo" data-mat="tipo" aria-label="Tipo"><option value="">Materiais e serviços</option>${L.tipos.map((t) => `<option value="${esc(t)}"${t === filtro.tipo ? ' selected' : ''}>${esc(M.TIPOS[t] || t)}</option>`).join('')}</select>` : ''}
      <select class="campo" data-mat="fornecedor" aria-label="Fornecedor"><option value="">Todos os fornecedores</option>${L.fornecedores.map((f) => `<option value="${esc(f.id)}"${f.id === filtro.fornecedor ? ' selected' : ''}>${esc(f.nome)}</option>`).join('')}</select>
    </div>
    <div id="mat-lista" aria-live="polite">${lista()}</div>`;
}

/** Bloco lateral na página de um projeto que usa a lista (p.materiais diz para quê). */
export function blocoProjeto(p) {
  if (!p.materiais) return '';
  const L = E.mat;
  const estado = E.matErro ? 'Ainda indisponível (migração 0016).' : !L ? 'A carregar…'
    : L.n.materiais ? `${L.n.materiais} materiais · ${L.n.fornecedores} fornecedores${L.atualizado ? ' · atualizado ' + quando(L.atualizado) : ''}`
    : 'Ainda sem dados: o Hub envia a lista nos dias úteis às 6h.';
  return `<section class="bloco-lateral bloco-materiais"><h3>Materiais do Hub</h3>
    <p class="pequeno">${esc(p.materiais)}</p><p class="fraco mini" style="margin:8px 0 12px">${esc(estado)}</p>
    <a class="btn pequeno" href="#/materiais">${ic('pasta', 'ic-sm')}Materiais e preços</a></section>`;
}

export function descarregarCSV() {
  const r = M.procurar(E.mat, filtro.q, filtro);
  const url = URL.createObjectURL(new Blob([M.csv(E.mat, r)], { type: 'text/csv;charset=utf-8' }));
  const a = Object.assign(document.createElement('a'), { href: url, download: `materiais-hub-${new Date().toISOString().slice(0, 10)}.csv` });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
