// Documentos: secções e pastas (migração 0024). O utilizador (2026-11-11): «deve ser possível criar uma secção … e
// depois adicionar os ficheiros que pretendo lá, deve ser também possível adicionar pastas de ficheiros».
// Base de dados simulada (fake-supabase.js + fixture.json): nada toca no Supabase real.
import { test, expect } from '@playwright/test';
import { readFileSync, mkdirSync, mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const FIXTURE = readFileSync(new URL('./fixture.json', import.meta.url), 'utf8');
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
mkdirSync(new URL('./capturas/', import.meta.url), { recursive: true });
const captura = (page, nome) => page.screenshot({ path: fileURLToPath(new URL(`./capturas/${nome}-${test.info().project.name}.png`, import.meta.url)), fullPage: true });

async function abrir(page, { utilizador, rota = '/' } = {}) {
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  await page.addInitScript(([fx, u]) => { window.__FIXTURE = JSON.parse(fx); if (u) window.__UTILIZADOR = u; }, [FIXTURE, utilizador || null]);
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await page.goto(rota);
  return erros;
}
const db = (page, expr, arg) => page.evaluate(expr, arg);

// a folder on disk: «Obra Teste» with a file, a subfolder with another, and a hidden file (left out)
function pastaTeste() {
  const raiz = mkdtempSync(join(tmpdir(), 'docs-'));
  const obra = join(raiz, 'Obra Teste');
  mkdirSync(join(obra, 'Cortes'), { recursive: true });
  writeFileSync(join(obra, 'planta.pdf'), '%PDF-1.4 planta');
  writeFileSync(join(obra, 'Cortes', 'corte A.pdf'), '%PDF-1.4 corte');
  writeFileSync(join(obra, '.DS_Store'), 'x');
  return obra;
}

test('secções: criar, carregar ficheiros e uma pasta inteira, mudar de secção, mudar o nome e apagar', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/builder/documentos' });
  const sec = page.locator('#documentos');
  const info = sec.locator('.docs-tipo[data-tipo-docs="informativo"]');
  // as secções que vinham do título continuam a aparecer (Builder: adicionais)
  await expect(sec.locator('.docs-tipo[data-tipo-docs="adicional"] details.doc-grupo summary')).toHaveText([/Torres Vedras\s*15/, /Sobral\s*4/, /Método\s*16/]);

  // nova secção nos informativos
  await info.getByRole('button', { name: 'Nova secção' }).click();
  const dlg = page.locator('#dlg');
  await dlg.getByLabel('Nome').fill('Desenhos de execução');
  await dlg.getByRole('button', { name: 'Criar secção' }).click();
  await expect(dlg).toBeHidden();
  const s = info.locator('details.doc-grupo', { hasText: 'Desenhos de execução' });
  await expect(s).toHaveAttribute('open', '');
  await expect(s).toContainText('Secção vazia');
  // o mesmo nome outra vez: recusado
  await info.getByRole('button', { name: 'Nova secção' }).click();
  await dlg.getByLabel('Nome').fill('Desenhos de execução');
  await dlg.getByRole('button', { name: 'Criar secção' }).click();
  await expect(dlg.locator('.erro-msg')).toContainText('Já existe uma secção');
  await dlg.getByRole('button', { name: 'Cancelar' }).click();

  // ficheiros soltos para a secção
  const [esc1] = await Promise.all([page.waitForEvent('filechooser'), s.getByRole('button', { name: 'Ficheiros' }).click()]);
  await esc1.setFiles([{ name: 'Memória descritiva.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4 m') },
    { name: 'Mapa de vãos.xlsx', mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', buffer: Buffer.from('PK') }]);
  await expect(s.locator('summary')).toContainText('2');
  await expect(s.locator('.doc', { hasText: 'Memória descritiva.pdf' })).toBeVisible();

  // uma pasta inteira (com a subpasta; o ficheiro escondido fica de fora)
  const [esc2] = await Promise.all([page.waitForEvent('filechooser'), s.getByRole('button', { name: 'Pasta' }).click()]);
  await esc2.setFiles(pastaTeste());
  await expect(s.locator('summary').first()).toContainText('4');
  const obra = s.locator('details.doc-pasta', { hasText: 'Obra Teste' }).first();
  await expect(obra).toHaveAttribute('open', '');
  await expect(obra.locator('> summary')).toContainText('2');
  await expect(obra.locator('details.doc-pasta > summary', { hasText: 'Cortes' })).toBeVisible();
  await expect(obra.locator('.doc', { hasText: 'corte A.pdf' })).toBeVisible();
  const linhas = await db(page, () => window.__fake.db.documentos.filter((d) => d.pasta.startsWith('Obra Teste')).map((d) => ({ pasta: d.pasta, lote: d.lote, nome: d.nome_ficheiro })));
  expect(linhas.map((l) => l.pasta).sort()).toEqual(['Obra Teste', 'Obra Teste/Cortes']);
  expect(new Set(linhas.map((l) => l.lote)).size).toBe(1);
  expect(linhas.some((l) => l.nome === '.DS_Store')).toBe(false);
  // um só registo no Log para a pasta (e um para os dois ficheiros soltos)
  const reg = await db(page, () => window.__fake.db.registo.filter((r) => r.tipo === 'documento_novo').map((r) => r.texto));
  expect(reg.filter((t) => t.includes('pasta «Obra Teste»'))).toHaveLength(1);
  expect(reg.filter((t) => /acrescentou 2 documentos à secção «Desenhos de execução»$/.test(t))).toHaveLength(1);
  await captura(page, 'documentos-seccoes');

  // mudar um documento de secção (para nenhuma)
  await s.locator('.doc', { hasText: 'Mapa de vãos.xlsx' }).getByRole('button', { name: /Mudar de secção/ }).click();
  await dlg.getByLabel('Secção').selectOption('');
  await dlg.getByRole('button', { name: 'Mudar' }).click();
  await expect(dlg).toBeHidden();
  await expect(s.locator('summary').first()).toContainText('3');
  await expect(info.locator(':scope > .docs-lista .doc', { hasText: 'Mapa de vãos.xlsx' })).toBeVisible();

  // mudar o nome da secção
  await s.getByRole('button', { name: /Mudar o nome da secção/ }).click();
  await dlg.getByLabel('Nome').fill('Projeto de execução');
  await dlg.getByRole('button', { name: 'Guardar' }).click();
  await expect(info.locator('details.doc-grupo summary', { hasText: 'Projeto de execução' })).toBeVisible();

  // apagar: com documentos não; vazia sim
  const s2 = info.locator('details.doc-grupo', { hasText: 'Projeto de execução' });
  await s2.getByRole('button', { name: /Apagar a secção/ }).click();
  await expect(page.locator('.aviso', { hasText: 'apaga primeiro os seus 3 documentos' })).toBeVisible();
  await info.getByRole('button', { name: 'Nova secção' }).click();
  await dlg.getByLabel('Nome').fill('Vazia');
  await dlg.getByRole('button', { name: 'Criar secção' }).click();
  const vazia = info.locator('details.doc-grupo', { hasText: 'Vazia' });
  page.once('dialog', (d) => d.accept());
  await vazia.getByRole('button', { name: /Apagar a secção/ }).click();
  await expect(vazia).toHaveCount(0);
  expect(erros).toEqual([]);
});

test('secções: arrastar ficheiros para uma secção; o diálogo «Documento» escolhe a secção', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/builder/documentos' });
  const sec = page.locator('#documentos');
  const sobral = sec.locator('details.doc-grupo', { hasText: 'Sobral' });
  await sobral.locator('summary').click();
  const dt = await page.evaluateHandle(() => {
    const d = new DataTransfer();
    d.items.add(new File(['%PDF-1.4 a'], 'Alçado norte.pdf', { type: 'application/pdf' }));
    return d;
  });
  await sobral.dispatchEvent('dragover', { dataTransfer: dt });
  await sobral.dispatchEvent('drop', { dataTransfer: dt });
  await expect(sobral.locator('summary')).toContainText('5');
  await expect(sobral.locator('.doc', { hasText: 'Alçado norte.pdf' })).toBeVisible();

  // o diálogo «Documento»: escolher a secção «Torres Vedras» (adicionais)
  await sec.getByRole('button', { name: 'Documento', exact: true }).click();
  const dlg = page.locator('#dlg');
  await dlg.getByLabel('Secção').selectOption({ label: 'Torres Vedras' });
  await dlg.getByLabel('Ficheiros').setInputFiles({ name: 'Fotografia da obra.jpg', mimeType: 'image/jpeg', buffer: Buffer.from('jpg') });
  await dlg.getByRole('button', { name: 'Carregar' }).click();
  await expect(dlg).toBeHidden();
  const tv = sec.locator('details.doc-grupo', { hasText: 'Torres Vedras' });
  await expect(tv.locator('summary')).toContainText('16');
  const d = await db(page, () => window.__fake.db.documentos.at(-1));
  expect(d.tipo).toBe('adicional');
  expect(d.seccao_id).toBe((await db(page, () => window.__fake.db.documentos_seccoes.find((s) => s.projeto === 'builder' && s.nome === 'Torres Vedras'))).id);
});

test('secções: quem só vê não tem botões para criar, carregar ou mudar', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/builder/documentos', utilizador: { id: 'u-ver', nome: 'Só Ver', nivel: 'ver' } });
  const sec = page.locator('#documentos');
  await expect(sec.locator('details.doc-grupo summary', { hasText: 'Torres Vedras' })).toBeVisible();
  await expect(sec.getByRole('button', { name: 'Nova secção' })).toHaveCount(0);
  await sec.locator('summary', { hasText: 'Torres Vedras' }).click();
  await expect(sec.getByRole('button', { name: 'Pasta' })).toHaveCount(0);
  await expect(sec.getByRole('button', { name: /Mudar de secção/ })).toHaveCount(0);
});
