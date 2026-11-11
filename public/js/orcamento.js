// Orçamentação: o custo dos materiais de uma Listagem de material com os preços da lista do Hub (2026-11-11).
// Módulo comum (como /js/materiais.js): a página /orcamentacao/ e, depois, o Build Your House (preço em direto) e o
// Gerador. Funções puras: a lista do Hub chega já carregada por materiais.js (`carregar`), as ligações por `ligacoes`.
//
// Cada linha da Listagem traz um CÓDIGO estável (BOB/ferramentas/documentos/codigos.py); o ficheiro de ligações
// (BOB/orcamentacao/ligacoes.json, publicado em /orcamentacao/ligacoes.json) diz, para cada código, o material do Hub,
// a unidade do preço e como a quantidade da linha passa a essa unidade. Só se usam os preços do Hub nessa unidade, o
// mais recente de cada fornecedor; de entre eles, o mais barato com desconto. Nunca se inventa um preço: o que falta
// aparece com o motivo.

const NUM = (v) => {
  if (v == null || v === '') return null;
  const n = Number(String(v).trim().replace(/\s/g, '').replace(',', '.'));
  return Number.isFinite(n) ? n : null;
};
const normalUn = (u) => String(u || '').trim().toLowerCase().replace(/^m²$/, 'm2').replace(/^m³$/, 'm3').replace(/^m\.?l\.?$/, 'ml');

/** Lê o CSV da Listagem de material (separador ;, aspas, BOM). Aceita o CSV antigo sem a coluna «codigo». */
export function lerCsv(texto) {
  const linhas = [];
  let campo = '', linha = [], aspas = false;
  const t = String(texto || '').replace(/^﻿/, '');
  for (let i = 0; i < t.length; i++) {
    const c = t[i];
    if (aspas) {
      if (c === '"' && t[i + 1] === '"') { campo += '"'; i++; } else if (c === '"') aspas = false; else campo += c;
    } else if (c === '"') aspas = true;
    else if (c === ';') { linha.push(campo); campo = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && t[i + 1] === '\n') i++;
      linha.push(campo); campo = '';
      if (linha.some((x) => x !== '')) linhas.push(linha);
      linha = [];
    } else campo += c;
  }
  linha.push(campo);
  if (linha.some((x) => x !== '')) linhas.push(linha);
  if (!linhas.length) return [];
  const cab = linhas[0].map((h) => h.trim().toLowerCase());
  if (!cab.includes('descricao')) throw new Error('Este ficheiro não parece a Listagem de material do Gerador (falta a coluna «descricao»).');
  return linhas.slice(1).map((l, i) => {
    const o = { n: i + 1 };
    cab.forEach((h, k) => { o[h] = l[k] ?? ''; });
    for (const k of ['pecas', 'comprimento_m', 'area_m2', 'volume_m3', 'quantidade_compra']) o[k] = NUM(o[k]);
    o.codigo = (o.codigo || '').trim();
    return o;
  });
}

/** A quantidade da linha na unidade do preço do Hub, ou null quando falta um dado (com o motivo em `porque`). */
export function quantidade(linha, q = {}) {
  let v;
  if (q.base === 'volume') {
    v = linha.volume_m3;
    if (!v && q.seccao_m2 && linha.comprimento_m) v = linha.comprimento_m * q.seccao_m2;
  } else if (q.base === 'area') v = linha.area_m2;
  else if (q.base === 'comprimento') v = linha.comprimento_m;
  else if (q.base === 'pecas') v = linha.pecas;
  else if (q.base === 'compra') v = linha.quantidade_compra;
  if (v == null || !(v > 0)) return { valor: null, porque: 'a linha não tem a quantidade de que o preço precisa' };
  if ('divisor' in q && !(q.divisor > 0)) return { valor: null, porque: 'falta a conversão para a unidade do preço' };
  v = v * (q.fator ?? 1) / (q.divisor ?? 1);
  if (q.arredondar) v = Math.ceil(v - 1e-9);
  return { valor: v };
}

const fracao = (v) => (v == null || v === '' || isNaN(v) ? 0 : Number(v) > 1 ? Number(v) / 100 : Number(v));

/** The prices of a Hub material that count, cheapest first (with discount): only those in `unidade`, and the Hub keeps
 *  older prices of the same supplier as rows of their own (e.g. April and November), so only each supplier's latest. */
export function precosValidos(m, unidade) {
  const un = normalUn(unidade), ultimo = new Map();
  for (const p of ((m && m.precos) || []).filter((x) => normalUn(x.unidade) === un && x.preco_desconto != null)) {
    const k = p.fornecedor_id || p.fornecedor || p.id, o = ultimo.get(k);
    const d = p.data_atualizacao || '', od = o ? o.data_atualizacao || '' : '';
    if (!o || d > od || (d === od && p.preco_desconto < o.preco_desconto)) ultimo.set(k, p);
  }
  return [...ultimo.values()].sort((a, b) => a.preco_desconto - b.preco_desconto);
}

/** Preço de cada linha. `L` = materiais.carregar(); `lig` = o JSON das ligações.
 *  Estado de cada linha: ok | resumo | sem_codigo | sem_ligacao | fora_do_hub | material_em_falta | unidade | quantidade.
 *  Devolve { linhas, total, total_iva, com_preco, sem_preco, capitulos: [{nome, total, linhas}] }. */
export function precificar(linhas, lig, L) {
  const porId = new Map((L.materiais || []).map((m) => [m.id, m]));
  const ligs = (lig && lig.ligacoes) || {};
  const out = linhas.map((l) => {
    const r = { ...l, estado: 'ok', motivo: '', material: null, preco: null, qtd: null, unidade: '', unitario: null, total: null, iva: null };
    const g = l.codigo ? ligs[l.codigo] : null;
    r.ligacao = g;
    if (!l.codigo) return Object.assign(r, { estado: 'sem_codigo', motivo: 'Linha sem código (CSV antigo ou produto novo): gera a Listagem outra vez no Gerador.' });
    if (!g) return Object.assign(r, { estado: 'sem_ligacao', motivo: `O código ${l.codigo} ainda não está ligado a um material do Hub.` });
    if (g.resumo) return Object.assign(r, { estado: 'resumo', motivo: g.nota || 'Linha de resumo.' });
    if (!g.hub) return Object.assign(r, { estado: 'fora_do_hub', motivo: g.nota || 'Não está na lista do Hub.' });
    const m = porId.get(g.hub);
    if (!m) return Object.assign(r, { estado: 'material_em_falta', motivo: 'O material ligado já não está na lista do Hub (mudou ou foi apagado): rever a ligação.' });
    r.material = m;
    const compat = precosValidos(m, g.unidade);
    r.alternativas = compat.length;
    if (!compat.length) {
      const tem = [...new Set((m.precos || []).map((p) => p.unidade).filter(Boolean))].join(', ') || 'nenhuma';
      return Object.assign(r, { estado: 'unidade', motivo: `O Hub não tem preço deste material em ${g.unidade} (tem: ${tem}).` });
    }
    const q = quantidade(l, g.quantidade);
    if (q.valor == null) return Object.assign(r, { estado: 'quantidade', motivo: (g.nota ? g.nota + ' ' : '') + `(${q.porque})` });
    const p = compat[0];
    const iva = fracao(p.iva);
    return Object.assign(r, { preco: p, qtd: q.valor, unidade: g.unidade, unitario: p.preco_desconto, total: q.valor * p.preco_desconto, iva });
  });
  const ok = out.filter((r) => r.estado === 'ok');
  const capitulos = [];
  for (const r of out) {
    let c = capitulos.find((x) => x.nome === r.capitulo);
    if (!c) capitulos.push((c = { nome: r.capitulo, total: 0, linhas: [] }));
    c.linhas.push(r);
    c.total += r.total || 0;
  }
  return {
    linhas: out, capitulos,
    total: ok.reduce((s, r) => s + r.total, 0),
    total_iva: ok.reduce((s, r) => s + r.total * (1 + r.iva), 0),
    com_preco: ok.length,
    sem_preco: out.filter((r) => !['ok', 'resumo'].includes(r.estado)).length,
  };
}

// ------------------------------------------------------------------ o preço final (tarefas 42, 43 e 44)
// As parcelas vêm da tabela orcamento_parcelas (migração 0017): método, base e valor de cada uma. Os valores da
// empresa ficam só na base de dados; um valor null quer dizer «ainda não fornecido» e o preço fica incompleto.

export const BASES = { construcao: 'área de construção', implantacao: 'área de implantação', vaos: 'área dos vãos' };
export const METODOS = {
  materiais_hub: 'Listagem de material com os preços do Hub', por_m2: '€ por m²', percentagem_materiais: '% dos materiais',
  valor_fixo: 'valor fixo por obra', percentagem_subtotal: '% da soma das parcelas', taxa_iva: 'taxa de IVA',
};

/** As áreas da obra para as parcelas por m²: as linhas «Dados da obra» da Listagem e a área dos vãos (caixilharia). */
export function dadosDaObra(linhas) {
  const area = (c) => (linhas.find((l) => l.codigo === c) || {}).area_m2 ?? null;
  const vaos = linhas.filter((l) => l.codigo === 'CAIXILHARIA').reduce((s, l) => s + (l.area_m2 || 0), 0);
  return { construcao: area('AREA-CONSTRUCAO'), implantacao: area('AREA-IMPLANTACAO'), vaos: vaos || null };
}

/** O preço final, parcela a parcela, com a conta de cada uma à vista.
 *  `res` = precificar(); `parcelas` = linhas de orcamento_parcelas (ordenadas); `dados` = { construcao, implantacao, vaos } m².
 *  Devolve { linhas: [{ id, nome, metodo, base, valor, quantidade, conta, total, falta }], subtotal, margem, iva, total,
 *  falta: [nomes], completo }. A margem (% da soma) e o IVA (taxa) aplicam-se por esta ordem, no fim. */
export function compor(res, parcelas, dados = {}) {
  const fmt = (v, d = 2) => Number(v).toLocaleString('pt-PT', { maximumFractionDigits: d });
  const eur = (v) => Number(v).toLocaleString('pt-PT', { style: 'currency', currency: 'EUR' });
  const linhas = [], falta = [];
  let subtotal = 0, margem = 0, iva = 0;
  const ordem = [...parcelas].sort((a, b) => (a.ordem ?? 0) - (b.ordem ?? 0));
  const porTipo = (t) => ordem.filter((p) => p.metodo === t);
  const normais = ordem.filter((p) => !['percentagem_subtotal', 'taxa_iva'].includes(p.metodo));
  const v = (p) => (p.valor == null || p.valor === '' ? null : Number(p.valor));
  for (const p of normais) {
    const l = { id: p.id, nome: p.nome, metodo: p.metodo, base: p.base, valor: v(p), quantidade: null, conta: '', total: null, falta: '', nota: p.nota || '' };
    if (p.metodo === 'materiais_hub') {
      l.total = res ? res.total : null;
      l.conta = res ? `${res.com_preco} linhas com preço do Hub` + (res.sem_preco ? ` (${res.sem_preco} ainda sem preço)` : '') : '';
      if (!res) l.falta = 'falta a Listagem de material';
    } else if (p.metodo === 'por_m2') {
      const a = dados[p.base || 'construcao'];
      l.quantidade = a;
      if (l.valor == null) l.falta = `falta o valor em € por m² de ${BASES[p.base || 'construcao']}`;
      else if (!(a > 0)) l.falta = `falta a ${BASES[p.base || 'construcao']}`;
      else { l.total = a * l.valor; l.conta = `${fmt(a)} m² × ${eur(l.valor)}/m²`; }
    } else if (p.metodo === 'percentagem_materiais') {
      if (l.valor == null) l.falta = 'falta a percentagem';
      else if (!res) l.falta = 'falta a Listagem de material';
      else { l.total = res.total * l.valor / 100; l.conta = `${fmt(l.valor)} % de ${eur(res.total)}`; }
    } else if (p.metodo === 'valor_fixo') {
      if (l.valor == null) l.falta = 'falta o valor';
      else { l.total = l.valor; l.conta = 'valor fixo por obra'; }
    }
    if (l.falta) falta.push(p.nome);
    else subtotal += l.total || 0;
    linhas.push(l);
  }
  for (const p of porTipo('percentagem_subtotal')) {
    const l = { id: p.id, nome: p.nome, metodo: p.metodo, base: null, valor: v(p), quantidade: subtotal, conta: '', total: null, falta: '', nota: p.nota || '' };
    if (l.valor == null) { l.falta = 'falta a percentagem'; falta.push(p.nome); }
    else { l.total = subtotal * l.valor / 100; margem += l.total; l.conta = `${fmt(l.valor)} % de ${eur(subtotal)}`; }
    linhas.push(l);
  }
  for (const p of porTipo('taxa_iva')) {
    const base = subtotal + margem;
    const l = { id: p.id, nome: p.nome, metodo: p.metodo, base: null, valor: v(p), quantidade: base, conta: '', total: null, falta: '', nota: p.nota || '' };
    if (l.valor == null) { l.falta = 'falta a taxa de IVA'; falta.push(p.nome); }
    else { l.total = base * l.valor / 100; iva += l.total; l.conta = `${fmt(l.valor)} % de ${eur(base)}`; }
    linhas.push(l);
  }
  return { linhas, subtotal, margem, iva, total: subtotal + margem + iva, falta, completo: !falta.length && !!res && !res.sem_preco };
}

/** CSV com os preços (separador ;, vírgula decimal, BOM): a Listagem e, por linha, o material, o fornecedor e o custo. */
export function csv(res) {
  const n = (v, d = 2) => (v == null ? '' : (Math.round(v * 10 ** d) / 10 ** d).toString().replace('.', ','));
  const c = (v) => { const s = String(v ?? ''); return /[;"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  const cab = ['Capítulo', 'Código', 'Descrição', 'Produto', 'Material do Hub', 'Fornecedor', 'Designação do fornecedor', 'Quantidade',
    'Unidade', 'Preço unitário (com desconto, sem IVA)', 'Total sem IVA', 'IVA', 'Data do preço', 'Estado', 'Motivo'];
  const linhas = res.linhas.map((r) => [r.capitulo, r.codigo, r.descricao, r.produto, r.material?.nome, r.preco?.fornecedor, r.preco?.designacao,
    n(r.qtd, 3), r.unidade, n(r.unitario, 4), n(r.total), r.iva == null ? '' : `${Math.round(r.iva * 100)} %`, r.preco?.data_atualizacao,
    r.estado, r.motivo].map(c).join(';'));
  linhas.push(['', '', 'Total dos materiais com preço (sem IVA)', '', '', '', '', '', '', '', n(res.total), '', '', '', ''].map(c).join(';'));
  return '﻿' + [cab.map(c).join(';'), ...linhas].join('\r\n');
}

export const ESTADOS = {
  ok: 'Com preço', resumo: 'Resumo', sem_codigo: 'Sem código', sem_ligacao: 'Sem ligação', fora_do_hub: 'Não está no Hub',
  material_em_falta: 'Material em falta', unidade: 'Unidade diferente', quantidade: 'Falta a conversão',
};
