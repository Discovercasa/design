// Orçamentação (/orcamentacao/, 2026-11-11): a Listagem de material do Gerador com os preços da lista do Hub.
// Base simulada (fake-supabase.js): os materiais usam os ids reais de BOB/orcamentacao/ligacoes.json.
import { test, expect } from '@playwright/test';
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
const LIG = JSON.parse(readFileSync(new URL('../public/orcamentacao/ligacoes.json', import.meta.url), 'utf8')).ligacoes;
mkdirSync(new URL('./capturas/', import.meta.url), { recursive: true });
const captura = (page, nome) => page.screenshot({ path: fileURLToPath(new URL(`./capturas/${nome}-${test.info().project.name}.png`, import.meta.url)), fullPage: true });

const F1 = 'f0000000-0000-4000-8000-000000000001', F2 = 'f0000000-0000-4000-8000-000000000002';
const t = '2026-11-10T13:48:19Z';
const mat = (cod, nome) => ({ id: LIG[cod].hub, nome, categoria: null, tipo: 'material', atualizado_em: t });
let np = 0;
const preco = (cod, f, preco, unidade, desconto = 0, iva = 0.23) => ({ id: `b0000000-0000-4000-8000-${String(++np).padStart(12, '0')}`, material_id: LIG[cod].hub,
  fornecedor_id: f, designacao: `${cod} ${unidade}`, preco, unidade, desconto, iva, data_atualizacao: '2026-11-04', atualizado_em: t });
const MATERIAIS = {
  hub_fornecedores: [{ id: F1, nome: 'Madeiras Teste', atualizado_em: t }, { id: F2, nome: 'Perfis Teste', atualizado_em: t }],
  hub_materiais: [mat('OSB-09', 'OSB 9 mm'), mat('FORRO-TREMOLO', 'Forro Tremolo'), mat('MEMB-T95', 'Traspir 95'), mat('TETO-PERFIL', 'Perfil TC-47'),
    mat('TELHA-CER', 'Telha cerâmica')],
  hub_material_precos: [
    preco('OSB-09', F1, 3.33, 'm2'), preco('OSB-09', F2, 3.9, 'm2'),
    { ...preco('OSB-09', F1, 2.5, 'm2'), data_atualizacao: '2025-01-10' },   // an older price of the same supplier: not used
    preco('FORRO-TREMOLO', F1, 19.45, 'm2', 0, 0),
    preco('MEMB-T95', F1, 64.07, 'un'),
    preco('TETO-PERFIL', F2, 0.83, 'ml', 0.41), preco('TETO-PERFIL', F2, 1.72, 'un', 0.05),   // a 3 m bar: other unit, ignored
    preco('TELHA-CER', F1, 1, 'un', 0.1),   // per tile: tiles per m² still missing
  ],
  hub_material_precos_historico: [],
};

async function abrir(page) {
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|Failed to load resource/.test(m.text())) erros.push(m.text()); });
  await page.addInitScript((m) => { window.__FIXTURE_MATERIAIS = m; }, MATERIAIS);
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await page.goto('/orcamentacao/');
  await expect(page.locator('#estado')).toContainText('Lista do Hub: 5 materiais e 8 preços');
  return erros;
}

test('Orçamentação: a Listagem de Torres Vedras com os preços do Hub', async ({ page }) => {
  const erros = await abrir(page);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Orçamentação');
  await page.getByRole('button', { name: 'Usar a de Torres Vedras (D2503)' }).click();
  const res = page.locator('#resultado');
  await expect(res).toBeVisible();
  // OSB 9: 59 placas x 3,125 m² x 3,33 € (the cheaper of the two suppliers)
  const osb = res.locator('tr', { hasText: 'OSB 9 mm' });
  await expect(osb).toContainText('OSB-09');
  await expect(osb).toContainText('184,38 m²');
  await expect(osb).toContainText(/613,97\s€/);
  await expect(osb).toContainText('o mais barato de 2');
  // Tremolo: the Spanish supplier without IVA is flagged
  await expect(res.locator('tr', { hasText: 'Forro Tremolo 22x135 (A)' })).toContainText('IVA 0 %');
  // the ceiling profiles use the price per metre, not the 3 m bar
  await expect(res.locator('tr', { hasText: 'Perfis de teto' })).toContainText('/m');
  // what the Hub list does not have says why
  await expect(res.locator('tr', { hasText: 'M1 Garagem - Portão seccionado' })).toContainText('A caixilharia (janelas, portas, portão, vidros e estores) não está na lista do Hub.');
  await expect(res.locator('tr', { hasText: 'Telha da pérgola' })).toContainText('Falta a conversão');
  await expect(res.locator('tr', { hasText: 'Lã mineral Volcalis Comfort' })).toContainText('Material em falta');
  await expect(page.locator('#res-numeros')).toContainText('Linhas com preço');
  // only the lines without a price
  await page.getByLabel('Só as linhas sem preço').check();
  await expect(res.locator('tr', { hasText: 'OSB 9 mm' })).toHaveCount(0);
  await expect(res.locator('tr', { hasText: 'Lã mineral Volcalis Comfort' })).toHaveCount(1);
  await page.getByLabel('Só as linhas sem preço').uncheck();
  // the CSV with the prices
  const [dl] = await Promise.all([page.waitForEvent('download'), page.getByRole('button', { name: 'Descarregar CSV com preços' }).click()]);
  expect(dl.suggestedFilename()).toBe('D2503_Listagem_Material_com_precos.csv');
  // the links table for the team: every code but the summary line, Claude's proposals to confirm
  const lig = page.locator('#ligacoes tbody tr');
  await expect(lig).toHaveCount(Object.values(LIG).filter((x) => !x.resumo).length);
  await expect(page.locator('#ligacoes tr', { hasText: 'OSB-09' })).toContainText('A confirmar');
  await expect(page.locator('#ligacoes tr', { hasText: 'CAIXILHARIA' })).toContainText('Não está no Hub');
  await captura(page, 'orcamentacao');
  expect(erros).toEqual([]);
});

test('Orçamentação: um CSV antigo sem códigos e um ficheiro errado', async ({ page }) => {
  const erros = await abrir(page);
  const antigo = '﻿capitulo;descricao;produto;pecas;comprimento_m;area_m2;volume_m3;quantidade_compra;unidade_compra\r\n'
    + 'Paredes - camadas exteriores;OSB 9 mm;OSB3 9 mm 2500x1250;147;;166.21;;59;placa 1250x2500\r\n';
  await page.locator('#ficheiro').setInputFiles({ name: 'antigo.csv', mimeType: 'text/csv', buffer: Buffer.from(antigo) });
  await expect(page.locator('#resultado tr', { hasText: 'OSB 9 mm' })).toContainText('Sem código');
  await page.locator('#ficheiro').setInputFiles({ name: 'outro.csv', mimeType: 'text/csv', buffer: Buffer.from('a;b\n1;2\n') });
  await expect(page.locator('#estado')).toContainText('não parece a Listagem de material');
  expect(erros).toEqual([]);
});

test('Orçamentação: o preço final, parcela a parcela (quem edita guarda os valores)', async ({ page }) => {
  const erros = await abrir(page);
  await page.getByRole('button', { name: 'Usar a de Torres Vedras (D2503)' }).click();
  const p = page.locator('#preco');
  await expect(p).toBeVisible();
  await expect(page.locator('#capitulos h3', { hasText: 'Dados da obra' })).toHaveCount(0);
  // the areas come from the Listagem: the foundation outline and the openings of the caixilharia
  await expect(p.getByLabel('Área de construção em m²')).toHaveValue('165,59');
  await expect(p.getByLabel('Área dos vãos em m²')).toHaveValue('31,68');
  await expect(p.locator('tr.o-final')).toContainText('Preço final (incompleto)');
  await expect(p.locator('.o-incompleto')).toContainText('Faltam valores em: Caixilharia, Fundação, Mão de obra');
  // labour per m² of construction area
  await p.getByLabel('Valor: Mão de obra').fill('100');
  await p.getByLabel('Valor: Mão de obra').press('Tab');
  await expect(page.locator('#preco-guardado')).toHaveText('Guardado: Mão de obra.');
  const mo = p.locator('tbody tr', { hasText: 'Mão de obra' });
  await expect(mo).toContainText('165,59 m² × 100,00 €/m²');
  await expect(mo).toContainText(/16\s?559,00\s€/);
  // the foundation as a fixed value; VAT at 6 %
  await p.getByLabel('Como se calcula: Fundação').selectOption('valor_fixo');
  await expect(page.locator('#preco-guardado')).toHaveText('Guardado: Fundação.');
  await expect(p.getByLabel('Área: Fundação')).toHaveCount(0);
  await p.getByLabel('Valor: Fundação').fill('5000');
  await p.getByLabel('Valor: Fundação').press('Tab');
  await expect(p.locator('tbody tr', { hasText: 'Fundação' })).toContainText(/5000,00\s€|5\s?000,00\s€/);
  await p.getByLabel('Valor: IVA').fill('6');
  await p.getByLabel('Valor: IVA').press('Tab');
  await expect(p.locator('tbody tr', { hasText: 'IVA' }).last()).toContainText('6 % de');
  // a wrong number is not saved
  await p.getByLabel('Valor: Licenciamento').fill('abc');
  await p.getByLabel('Valor: Licenciamento').press('Tab');
  await expect(page.locator('#preco-guardado')).not.toHaveText('Guardado: Licenciamento.');
  // the area can be corrected for this sum only
  await p.getByLabel('Área de construção em m²').fill('200');
  await p.getByLabel('Área de construção em m²').press('Tab');
  await expect(p.locator('tbody tr', { hasText: 'Mão de obra' })).toContainText(/20\s?000,00\s€/);
  await captura(page, 'orcamentacao-preco');
  expect(erros).toEqual([]);
});

test('Orçamentação: quem só vê não muda os valores do preço', async ({ page }) => {
  await page.addInitScript(() => { window.__UTILIZADOR = { id: 'u-ver', nome: 'Só Vê', nivel: 'ver' }; });
  const erros = await abrir(page);
  await page.getByRole('button', { name: 'Usar a de Torres Vedras (D2503)' }).click();
  const p = page.locator('#preco');
  await expect(p).toBeVisible();
  await expect(p.locator('input[data-parcela], select[data-parcela]')).toHaveCount(0);
  await expect(p.locator('tbody tr', { hasText: 'Mão de obra' })).toContainText('por fornecer');
  await expect(p.locator('.o-incompleto')).toContainText('Quem pode editar o Design escreve os valores aqui.');
  expect(erros).toEqual([]);
});
