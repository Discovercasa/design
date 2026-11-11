// Orçamentação (página /orcamentacao/): larga-se a Listagem de material do Gerador (CSV) e vê-se o custo dos materiais
// com os preços da lista do Hub. Os preços só se leem com a sessão do Design (regra "Ver"); nada fica guardado.
import * as M from '/js/materiais.js';
import * as O from '/js/orcamento.js';

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const EUR = new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' });
const eur = (v) => (v == null ? '—' : EUR.format(v));
const num = (v, d = 2) => (v == null ? '' : v.toLocaleString('pt-PT', { maximumFractionDigits: d }));
const UN = { m2: 'm²', m3: 'm³', ml: 'm', un: 'un' };
const dia = (t) => (t ? new Date(t).toLocaleDateString('pt-PT', { day: 'numeric', month: 'short', year: 'numeric' }) : '');
let L = null, LIG = null, res = null, nome = 'listagem';
let PARCELAS = null, parcelasErro = '', editor = false, dados = {};

function estado(txt, erro = false, ocupado = false) {
  const e = $('estado');
  e.textContent = txt;
  e.className = erro ? 'erro' : 'ajuda' + (ocupado ? ' ocupado' : '');
}

async function iniciar() {
  try {
    [LIG, L] = await Promise.all([fetch('./ligacoes.json').then((r) => { if (!r.ok) throw new Error('ligações em falta'); return r.json(); }),
      M.carregar(window.Design.sb)]);
  } catch (e) {
    estado('Não foi possível ler a lista de materiais do Hub: ' + (e.message || e), true);
    return;
  }
  if (!L.n.materiais) estado('Ainda não há materiais do Hub (o Hub envia a lista nos dias úteis às 6h). Sem eles não há preços.', true);
  else estado(`Lista do Hub: ${L.n.materiais} materiais e ${L.n.precos} preços${L.atualizado ? `, atualizada a ${dia(L.atualizado)}` : ''}.`);
  ligacoes();
  // the price parcels (migration 0017): values only in the database, never in this public repo
  try {
    const { data: { session } } = await window.Design.sb.auth.getSession();
    editor = window.Design.nivel(session) === 'editar';
    const { data, error } = await window.Design.sb.from('orcamento_parcelas').select('*').order('ordem');
    if (error) throw error;
    PARCELAS = data;
  } catch (e) { parcelasErro = e.message || String(e); }
}

// ------------------------------------------------------------------ the Listagem
function abrir(texto, nomeFicheiro) {
  let linhas;
  try { linhas = O.lerCsv(texto); } catch (e) { estado(e.message, true); return; }
  if (!linhas.length) { estado('O ficheiro não tem linhas.', true); return; }
  if (!L) { estado('A lista do Hub ainda não carregou: tenta daqui a uns segundos.', true); return; }
  nome = (nomeFicheiro || 'listagem').replace(/\.csv$/i, '');
  res = O.precificar(linhas, LIG, L);
  dados = O.dadosDaObra(linhas);
  mostrar();
  preco();
  $('preco').hidden = false;
  $('resultado').hidden = false;
  $('resultado').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
}

function mostrar() {
  const tot = res.linhas.filter((r) => r.estado !== 'resumo').length;
  $('res-obra').textContent = `${nome} · ${tot} linhas`;
  $('res-numeros').innerHTML = `
    <div><b class="num">${eur(res.total)}</b><span>Materiais com preço, sem IVA</span></div>
    <div><b class="num">${eur(res.total_iva)}</b><span>Com o IVA de cada fornecedor</span></div>
    <div><b class="num">${res.com_preco} / ${tot}</b><span>Linhas com preço</span></div>
    <div class="${res.sem_preco ? 'o-falta' : ''}"><b class="num">${res.sem_preco}</b><span>Linhas sem preço (motivo em cada uma)</span></div>`;
  const so = $('so-falta').checked;
  $('capitulos').innerHTML = res.capitulos.filter((c) => c.nome !== 'Dados da obra').map((c) => {
    const ls = c.linhas.filter((r) => !so || !['ok', 'resumo'].includes(r.estado));
    if (!ls.length) return '';
    return `<section class="o-cap"><h3>${esc(c.nome)} <span class="num fraco">${eur(c.total)}</span></h3>
      <div class="rolar-x"><table class="tabela o-tabela"><thead><tr><th>Descrição</th><th>Material do Hub</th><th class="num">Quantidade</th>
        <th class="num">Preço</th><th class="num">Total</th></tr></thead><tbody>${ls.map(linha).join('')}</tbody></table></div></section>`;
  }).join('') || '<p class="vazio">Todas as linhas têm preço.</p>';
}

function linha(r) {
  const desc = `<td class="o-desc">${esc(r.descricao)}${r.codigo ? ` <span class="chip o-cod">${esc(r.codigo)}</span>` : ''}
    ${r.produto ? `<div class="fraco mini">${esc(r.produto)}</div>` : ''}</td>`;
  if (r.estado !== 'ok') {
    return `<tr class="o-${esc(r.estado)}">${desc}<td colspan="4"><span class="chip o-estado">${esc(O.ESTADOS[r.estado])}</span>
      <span class="pequeno">${esc(r.motivo)}</span></td></tr>`;
  }
  const iva = r.iva === 0 ? ' <span class="chip o-aviso" title="O fornecedor não cobra IVA (ex.: fornecedor de fora de Portugal): o IVA português é pago à parte.">IVA 0 %</span>' : '';
  return `<tr>${desc}<td><a href="/#/materiais/m-${esc(r.material.id)}">${esc(r.material.nome)}</a>
      <div class="fraco mini">${esc(r.preco.fornecedor || '')}${r.alternativas > 1 ? ` · o mais barato de ${r.alternativas}` : ''}${r.preco.data_atualizacao ? ` · preço de ${esc(dia(r.preco.data_atualizacao))}` : ''}</div></td>
    <td class="num" data-rotulo="Quantidade">${num(r.qtd, 2)} ${esc(UN[r.unidade] || r.unidade)}</td>
    <td class="num" data-rotulo="Preço">${eur(r.unitario)}<span class="fraco">/${esc(UN[r.unidade] || r.unidade)}</span>${iva}</td>
    <td class="num" data-rotulo="Total"><b>${eur(r.total)}</b></td></tr>`;
}

// ------------------------------------------------------------------ the final price, parcel by parcel (tasks 42–44)
const m2 = (v) => (v == null ? '' : String(Math.round(v * 100) / 100).replace('.', ','));
const lerNum = (t) => { const n = Number(String(t).trim().replace(/\s/g, '').replace(',', '.')); return String(t).trim() === '' || !Number.isFinite(n) ? null : n; };
const unidade = (p) => (p.metodo === 'por_m2' ? '€/m²' : ['percentagem_materiais', 'percentagem_subtotal', 'taxa_iva'].includes(p.metodo) ? '%' : '€');

function como(p) {
  if (p.metodo === 'materiais_hub') return `<span class="pequeno">${esc(O.METODOS[p.metodo])}</span>`;
  const base = p.metodo === 'por_m2' ? ` de ${esc(O.BASES[p.base || 'construcao'])}` : '';
  if (!editor) return `<span class="pequeno">${esc(O.METODOS[p.metodo])}${base}: <b>${p.valor == null ? 'por fornecer' : `${esc(num(Number(p.valor)))} ${unidade(p)}`}</b></span>`;
  const metodos = p.metodo === 'taxa_iva' ? [] : ['por_m2', 'percentagem_materiais', 'valor_fixo', 'percentagem_subtotal'];
  return `<div class="o-como">
    ${metodos.length ? `<select class="campo" data-parcela="${esc(p.id)}" data-campo="metodo" aria-label="Como se calcula: ${esc(p.nome)}">${metodos.map((m) => `<option value="${m}"${m === p.metodo ? ' selected' : ''}>${esc(O.METODOS[m])}</option>`).join('')}</select>` : ''}
    ${p.metodo === 'por_m2' ? `<select class="campo" data-parcela="${esc(p.id)}" data-campo="base" aria-label="Área: ${esc(p.nome)}">${Object.entries(O.BASES).map(([k, t]) => `<option value="${k}"${k === (p.base || 'construcao') ? ' selected' : ''}>${esc(t)}</option>`).join('')}</select>` : ''}
    <span class="o-com-un"><input class="campo num" inputmode="decimal" data-parcela="${esc(p.id)}" data-campo="valor" value="${p.valor == null ? '' : m2(Number(p.valor))}" placeholder="por fornecer" aria-label="Valor: ${esc(p.nome)}"><span class="fraco">${unidade(p)}</span></span>
  </div>`;
}

function preco() {
  if (parcelasErro || !PARCELAS) {
    $('preco-corpo').innerHTML = `<p class="vazio">As parcelas do preço ainda não estão disponíveis${parcelasErro ? ` (${esc(parcelasErro)})` : ''}.</p>`;
    return;
  }
  const c = O.compor(res, PARCELAS, dados);
  const campoArea = (k, rot) => `<label class="campo-grupo"><span>${rot}</span><span class="o-com-un"><input class="campo num" inputmode="decimal" data-area="${k}" value="${m2(dados[k])}" aria-label="${rot} em m²"><span class="fraco">m²</span></span></label>`;
  const porId = new Map(PARCELAS.map((p) => [p.id, p]));
  $('preco-corpo').innerHTML = `
    <div class="o-areas">${campoArea('construcao', 'Área de construção')}${campoArea('implantacao', 'Área de implantação')}${campoArea('vaos', 'Área dos vãos')}</div>
    <p class="fraco mini">Da Listagem (contorno da base de fundação e vãos da caixilharia). Pode-se acertar aqui: só muda esta conta, não fica guardado.</p>
    <div class="rolar-x"><table class="tabela o-tabela o-parcelas"><thead><tr><th>Parcela</th><th>Como se calcula</th><th>Conta</th><th class="num">Valor</th></tr></thead><tbody>
    ${c.linhas.map((l) => `<tr class="${l.falta ? 'o-por-fornecer' : ''}"><td class="o-desc"><b>${esc(l.nome)}</b><div class="fraco mini">${esc(l.nota)}</div></td>
        <td>${como(porId.get(l.id))}</td>
        <td class="pequeno">${l.falta ? `<span class="chip o-aviso">${esc(l.falta)}</span>` : esc(l.conta)}</td>
        <td class="num" data-rotulo="Valor">${l.total == null ? '—' : `<b>${eur(l.total)}</b>`}</td></tr>`).join('')}
    </tbody><tfoot>
      <tr><td colspan="3">Soma das parcelas</td><td class="num">${eur(c.subtotal)}</td></tr>
      <tr><td colspan="3">Margem</td><td class="num">${eur(c.margem)}</td></tr>
      <tr><td colspan="3">IVA</td><td class="num">${eur(c.iva)}</td></tr>
      <tr class="o-final"><td colspan="3">Preço final${c.completo ? '' : ' (incompleto)'}</td><td class="num"><b>${eur(c.total)}</b></td></tr>
    </tfoot></table></div>
    ${c.completo ? '' : `<div class="nota o-incompleto"><p><b>Ainda não é o preço final.</b>${c.falta.length ? ` Faltam valores em: ${esc(c.falta.join(', '))}.` : ''}${res && res.sem_preco ? ` ${res.sem_preco} linhas da Listagem ainda não têm preço no Hub (ver acima).` : ''}${editor ? ' Os valores escrevem-se aqui e ficam guardados para todas as obras.' : ' Quem pode editar o Design escreve os valores aqui.'}</p></div>`}
    ${editor ? '<p class="fraco mini" id="preco-guardado" role="status"></p>' : ''}`;
}

async function guardar(id, campo, valor) {
  const p = PARCELAS.find((x) => x.id === id);
  if (!p) return;
  const muda = { metodo: p.metodo, base: p.base, valor: p.valor, [campo]: valor };
  const g = $('preco-guardado');
  if (g) g.textContent = 'A guardar…';
  const { data, error } = await window.Design.sb.from('orcamento_parcelas').update(muda).eq('id', id).select().single();
  if (error) { if (g) g.textContent = 'Não foi possível guardar: ' + error.message; return; }
  Object.assign(p, data || muda);
  preco();
  const g2 = $('preco-guardado');
  if (g2) g2.textContent = `Guardado: ${p.nome}.`;
}

// ------------------------------------------------------------------ the links (for the team to check)
function ligacoes() {
  const porId = new Map(L.materiais.map((m) => [m.id, m]));
  const g = LIG.ligacoes;
  const n = Object.values(g).filter((x) => x.hub).length, fora = Object.values(g).filter((x) => !x.resumo && !x.hub).length;
  $('ligacoes').innerHTML = `<p class="pequeno suave">${n} produtos ligados a um material do Hub; ${fora} ainda não estão na lista do Hub.</p>
    <div class="rolar-x"><table class="tabela o-tabela"><thead><tr><th>Código</th><th>Produto</th><th>Material do Hub</th><th class="num">Melhor preço</th><th>Estado</th></tr></thead><tbody>
    ${Object.entries(g).filter(([, x]) => !x.resumo).map(([cod, x]) => {
      const m = x.hub ? porId.get(x.hub) : null;
      const un = x.unidade;
      const p = m && O.precosValidos(m, un)[0];
      const est = !x.hub ? '<span class="chip o-estado">Não está no Hub</span>' : !m ? '<span class="chip o-estado">Material em falta</span>'
        : x.estado === 'CONFIRMED' ? '<span class="chip o-ok">Confirmada</span>' : '<span class="chip o-aviso">A confirmar</span>';
      return `<tr><td><span class="chip o-cod">${esc(cod)}</span></td><td>${esc(x.produto)}<div class="fraco mini">${esc(x.nota || '')}</div></td>
        <td>${m ? `<a href="/#/materiais/m-${esc(m.id)}">${esc(m.nome)}</a>` : '<span class="fraco">—</span>'}</td>
        <td class="num" data-rotulo="Melhor preço">${p ? `${eur(p.preco_desconto)}<span class="fraco">/${esc(UN[un] || un)}</span><div class="fraco mini">${esc(p.fornecedor || '')}</div>` : '<span class="fraco">—</span>'}</td>
        <td>${est}</td></tr>`;
    }).join('')}</tbody></table></div>`;
}

// ------------------------------------------------------------------ input
const ler = (f) => { if (!f) return; if (!/\.csv$/i.test(f.name)) { estado('Escolhe o CSV da Listagem de material (.csv).', true); return; } f.text().then((t) => abrir(t, f.name)); };
const zona = $('largar');
zona.addEventListener('click', () => $('ficheiro').click());
zona.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); $('ficheiro').click(); } });
zona.addEventListener('dragover', (e) => { e.preventDefault(); zona.classList.add('por-cima'); });
zona.addEventListener('dragleave', () => zona.classList.remove('por-cima'));
zona.addEventListener('drop', (e) => { e.preventDefault(); zona.classList.remove('por-cima'); ler(e.dataTransfer.files[0]); });
$('ficheiro').addEventListener('change', (e) => { ler(e.target.files[0]); e.target.value = ''; });
$('exemplo').addEventListener('click', () => fetch('./exemplos/D2503_Listagem_Material.csv').then((r) => r.text()).then((t) => abrir(t, 'D2503_Listagem_Material.csv')));
$('so-falta').addEventListener('change', () => res && mostrar());
$('preco-corpo').addEventListener('change', (e) => {
  const t = e.target;
  if (t.dataset.area) { dados[t.dataset.area] = lerNum(t.value); preco(); return; }
  if (!t.dataset.parcela) return;
  if (t.dataset.campo === 'valor') {
    const v = lerNum(t.value);
    if (t.value.trim() !== '' && (v == null || v < 0)) { t.setCustomValidity('Escreve um número (ex.: 120 ou 12,5).'); t.reportValidity(); return; }
    t.setCustomValidity('');
    guardar(t.dataset.parcela, 'valor', v);
  } else guardar(t.dataset.parcela, t.dataset.campo, t.value);
});
$('baixar').addEventListener('click', () => {
  if (!res) return;
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([O.csv(res)], { type: 'text/csv;charset=utf-8' }));
  a.download = `${nome}_com_precos.csv`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
});

iniciar();
