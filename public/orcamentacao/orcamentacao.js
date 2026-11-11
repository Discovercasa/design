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
}

// ------------------------------------------------------------------ the Listagem
function abrir(texto, nomeFicheiro) {
  let linhas;
  try { linhas = O.lerCsv(texto); } catch (e) { estado(e.message, true); return; }
  if (!linhas.length) { estado('O ficheiro não tem linhas.', true); return; }
  if (!L) { estado('A lista do Hub ainda não carregou: tenta daqui a uns segundos.', true); return; }
  nome = (nomeFicheiro || 'listagem').replace(/\.csv$/i, '');
  res = O.precificar(linhas, LIG, L);
  mostrar();
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
  $('capitulos').innerHTML = res.capitulos.map((c) => {
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
$('baixar').addEventListener('click', () => {
  if (!res) return;
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([O.csv(res)], { type: 'text/csv;charset=utf-8' }));
  a.download = `${nome}_com_precos.csv`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
});

iniciar();
