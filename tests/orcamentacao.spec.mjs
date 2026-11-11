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
  await expect(page.locator('#estado')).toContainText('Lista do Hub: 5 materiais e 7 preços');
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
