// Materiais vindos do Hub (migração 0016_materiais_hub, 2026-11-10): materiais, preços por fornecedor e histórico de
// preços. O Hub envia as tabelas hub_* nos dias úteis às 6h (Lisboa) com a chave de serviço; aqui são SÓ DE CONSULTA:
// este módulo nunca escreve nelas (não há regras de criar/editar/apagar; mudar colunas só falando com o Sebastião).
//
// Um só módulo para todo o Design, na mesma origem e com a mesma sessão (regra "Ver" = public.pode_ver()):
//   - o hub (aba Materiais, #/materiais) e o bloco «Materiais do Hub» dos projetos;
//   - as aplicações: Orçamentação (preço final), Build Your House (preço em direto), Gerador (Listagem de material).
// Uso:  import * as M from '/js/materiais.js';  const L = await M.carregar(window.Design.sb);  M.procurar(L, 'OSB')
//
// Desconto e IVA vêm em fração (0,23 = 23 %: primeiro envio, 2026-11-10); `fracao` aceita também 0–100, por segurança.

const PAGINA = 1000;   // o PostgREST devolve no máximo 1000 linhas de cada vez
const TABELAS = ['hub_fornecedores', 'hub_materiais', 'hub_material_precos', 'hub_material_precos_historico'];

async function tudo(sb, tabela) {
  const linhas = [];
  for (let de = 0; ; de += PAGINA) {
    const { data, error } = await sb.from(tabela).select('*').order('id').range(de, de + PAGINA - 1);
    if (error) throw error;
    linhas.push(...data);
    if (data.length < PAGINA) return linhas;
  }
}

export const fracao = (v) => (v == null || v === '' || isNaN(v) ? null : Number(v) > 1 ? Number(v) / 100 : Number(v));
export const comDesconto = (p) => (p.preco == null ? null : Number(p.preco) * (1 - (fracao(p.desconto) || 0)));
export const comIva = (p) => { const v = comDesconto(p); return v == null ? null : v * (1 + (fracao(p.iva) || 0)); };
const quando = (h) => h.data_atualizacao || h.registado_em || '';

/** Lê as quatro tabelas e junta: cada material com os seus preços (do mais barato para o mais caro, com desconto),
 *  cada preço com o fornecedor e o histórico (do mais antigo para o mais recente). */
export async function carregar(sb) {
  const [fornecedores, materiais, precos, historico] = await Promise.all(TABELAS.map((t) => tudo(sb, t)));
  const forn = new Map(fornecedores.map((f) => [f.id, f]));
  const hist = new Map();
  for (const h of historico) (hist.get(h.preco_id) || hist.set(h.preco_id, []).get(h.preco_id)).push(h);
  const porMaterial = new Map();
  for (const p of precos) {
    const linha = { ...p, fornecedor: (forn.get(p.fornecedor_id) || {}).nome || '', historico: (hist.get(p.id) || []).sort((a, b) => (quando(a) < quando(b) ? -1 : quando(a) > quando(b) ? 1 : 0)) };
    linha.preco_desconto = comDesconto(linha);
    linha.variacao = variacao(linha);
    (porMaterial.get(p.material_id) || porMaterial.set(p.material_id, []).get(p.material_id)).push(linha);
  }
  // categories as the Hub writes them can differ in case («Acabamentos Interiores» / «… interiores»): one key, the most
  // used spelling as its name; materials without a category go last
  const nomes = new Map();
  for (const m of materiais) {
    const k = normal(m.categoria).trim();
    if (!k) continue;
    const c = nomes.get(k) || nomes.set(k, new Map()).get(k);
    c.set(m.categoria.trim(), (c.get(m.categoria.trim()) || 0) + 1);
  }
  const categorias = [...nomes].map(([chave, c]) => ({ chave, nome: [...c].sort((a, b) => b[1] - a[1])[0][0] }))
    .sort((a, b) => a.nome.localeCompare(b.nome, 'pt'));
  const nomeCat = new Map(categorias.map((c) => [c.chave, c.nome]));
  const lista = materiais.map((m) => {
    const ps = (porMaterial.get(m.id) || []).sort((a, b) => (a.preco_desconto ?? Infinity) - (b.preco_desconto ?? Infinity));
    const chave = normal(m.categoria).trim();
    return { ...m, categoria_chave: chave, categoria_nome: nomeCat.get(chave) || '', precos: ps, melhor: ps.find((p) => p.preco_desconto != null) || null };
  }).sort((a, b) => (!a.categoria_chave - !b.categoria_chave) || a.categoria_nome.localeCompare(b.categoria_nome, 'pt') || a.nome.localeCompare(b.nome, 'pt'));
  const datas = [...fornecedores, ...materiais, ...precos].map((x) => x.atualizado_em).filter(Boolean).sort();
  return {
    materiais: lista, fornecedores: [...fornecedores].sort((a, b) => a.nome.localeCompare(b.nome, 'pt')),
    n: { materiais: materiais.length, fornecedores: fornecedores.length, precos: precos.length, historico: historico.length },
    atualizado: datas.length ? datas[datas.length - 1] : null,
    categorias, tipos: [...new Set(materiais.map((m) => m.tipo).filter(Boolean))].sort(),
  };
}
export const TIPOS = { material: 'Material', servico: 'Serviço' };

/** A última mudança de preço de uma linha (histórico): { de, para, pct, dia } ou null. */
export function variacao(linha) {
  const h = (linha.historico || []).filter((x) => x.preco != null);
  for (let i = h.length - 1; i > 0; i--) {
    if (Number(h[i].preco) !== Number(h[i - 1].preco)) {
      const de = Number(h[i - 1].preco), para = Number(h[i].preco);
      return { de, para, pct: de ? (para - de) / de : null, dia: quando(h[i]) };
    }
  }
  return null;
}

function normal(t) { return String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
/** Filtra por texto (nome, categoria, tipo, designação, dimensões, fornecedor), categoria (a chave), tipo e fornecedor. */
export function procurar(L, texto = '', { categoria = '', tipo = '', fornecedor = '' } = {}) {
  const q = normal(texto).split(/\s+/).filter(Boolean);
  return L.materiais.filter((m) => {
    if (categoria && m.categoria_chave !== categoria) return false;
    if (tipo && m.tipo !== tipo) return false;
    if (fornecedor && !m.precos.some((p) => p.fornecedor_id === fornecedor)) return false;
    if (!q.length) return true;
    const alvo = normal([m.nome, m.categoria, m.tipo, ...m.precos.flatMap((p) => [p.designacao, p.dimensoes, p.fornecedor])].join(' '));
    return q.every((w) => alvo.includes(w));
  });
}

/** CSV (separador ;, vírgula decimal, BOM) para o Excel e para as ferramentas do BOB: uma linha por preço. */
export function csv(L, materiais = L.materiais) {
  const n = (v) => (v == null || v === '' ? '' : String(v).replace('.', ','));
  const c = (v) => { const s = String(v ?? ''); return /[;"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  const cab = ['Material', 'Categoria', 'Tipo', 'Fornecedor', 'Designação', 'Dimensões', 'Preço', 'Unidade', 'Desconto', 'Preço com desconto',
    'IVA', 'Disponibilidade', 'Prazo (dias)', 'Data do preço', 'Transporte', 'Transporte incluído', 'Comprimento', 'Largura', 'Espessura',
    'Qtd. embalagem', 'Unidade da embalagem', 'Peso (kg)', 'kg/m³', 'Detalhes'];
  const linhas = materiais.flatMap((m) => (m.precos.length ? m.precos : [{}]).map((p) => [m.nome, m.categoria_nome || m.categoria, TIPOS[m.tipo] || m.tipo, p.fornecedor, p.designacao,
    p.dimensoes, n(p.preco), p.unidade, n(p.desconto), n(p.preco_desconto != null ? Math.round(p.preco_desconto * 10000) / 10000 : null), n(p.iva),
    p.disponibilidade, p.prazo_dias, p.data_atualizacao, p.transporte, p.transporte_incluido, n(p.comprimento), n(p.largura), n(p.espessura),
    n(p.qtd_embalagem), p.qtd_unidade, n(p.peso_kg), n(p.kg_m3), p.detalhes].map(c).join(';')));
  return '﻿' + [cab.map(c).join(';'), ...linhas].join('\r\n');
}
