// Aba Páginas (migração 0025). O utilizador (2026-11-12): «Dentro do projeto do Builder cria uma aba que vai ter as nossas
// páginas … Quero também que cries tarefas e checkpoints nessa aba». Base de dados simulada: nada toca no Supabase real.
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const FIXTURE = readFileSync(new URL('./fixture.json', import.meta.url), 'utf8');
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
const PAGINA = '<!doctype html><html lang="pt"><head><meta charset="utf-8"><title>Casa Teste</title></head><body><h1>Casa Teste em 3D</h1></body></html>';

async function abrir(page, { utilizador, rota = '/' } = {}) {
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  await page.addInitScript(([fx, u]) => { window.__FIXTURE = JSON.parse(fx); if (u) window.__UTILIZADOR = u; }, [FIXTURE, utilizador || null]);
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  // the fake storage keeps only the size: serve the page's HTML for its signed link
  await page.route('**/__ficheiro?*', (r) => r.fulfill({ contentType: 'text/html; charset=utf-8', body: PAGINA }));
  await page.goto(rota);
  return erros;
}
const db = (page, expr, arg) => page.evaluate(expr, arg);

test('Páginas: a aba do Builder carrega uma página e abre-a noutra janela', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/builder/paginas' });
  const abas = page.locator('#sub-abas');
  await expect(abas.getByRole('link', { name: 'Páginas' })).toHaveAttribute('aria-current', 'page');
  await expect(page.getByRole('heading', { level: 2, name: 'Páginas', exact: true })).toBeVisible();
  await expect(page.getByText('Ainda sem páginas.')).toBeVisible();
  await page.locator('input[name="pagina-ficheiro"]').setInputFiles({ name: 'casa-teste.html', mimeType: 'text/html', buffer: Buffer.from(PAGINA) });
  const cartao = page.locator('.pagina-cartao', { hasText: 'Casa Teste' });
  await expect(cartao).toBeVisible();   // the title comes from the page's <title>
  expect(await db(page, () => window.__fake.db.documentos.filter((d) => d.tipo === 'pagina').map((d) => [d.projeto, d.caminho.split('/')[1]]))).toEqual([['builder', 'pagina']]);
  await expect(abas.getByRole('link', { name: /Páginas/ })).toContainText('1');
  // it is not a document of the Documentos tab
  await abas.getByRole('link', { name: /Documentos/ }).click();
  await expect(page.locator('.doc', { hasText: 'Casa Teste' })).toHaveCount(0);
  await abas.getByRole('link', { name: /Páginas/ }).click();
  // «Abrir a página»: another window, the page from memory
  const [janela] = await Promise.all([page.waitForEvent('popup'), cartao.getByRole('button', { name: 'Abrir a página' }).click()]);
  await expect(janela.getByRole('heading', { name: 'Casa Teste em 3D' })).toBeVisible();
  expect(janela.url()).toMatch(/^blob:/);
  await janela.close();
  expect(erros).toEqual([]);
});

// 2026-11-19: «cria Collapsables onde cada projeto tem as suas páginas» → uma obra por casa (secção do tipo 'pagina')
test('Páginas: por obra, em colapsáveis; carregar numa obra e mudar uma página de obra', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/builder/paginas' });
  const dlg = page.locator('#dlg');
  await page.locator('.seccao-cabeca input[name="pagina-ficheiro"]').setInputFiles({ name: 'casa-teste.html', mimeType: 'text/html', buffer: Buffer.from(PAGINA) });
  await expect(page.locator('.pagina-cartao', { hasText: 'Casa Teste' })).toBeVisible();
  // a new obra: created open and empty; the loose page goes under «Sem obra»
  await page.getByRole('button', { name: 'Nova obra' }).click();
  await expect(dlg.getByRole('heading', { name: 'Nova obra' })).toBeVisible();
  await dlg.getByLabel('Nome').fill('Ribamar');
  await dlg.getByRole('button', { name: 'Criar obra' }).click();
  const obra = page.locator('details.pag-obra', { hasText: 'Ribamar' });
  await expect(obra).toHaveAttribute('open', '');
  await expect(obra).toContainText('Ainda sem páginas desta obra.');
  await expect(page.getByRole('heading', { name: 'Sem obra' })).toBeVisible();
  expect(await db(page, () => window.__fake.db.documentos_seccoes.filter((s) => s.tipo === 'pagina').map((s) => [s.projeto, s.nome]))).toEqual([['builder', 'Ribamar']]);
  // move the loose page into the obra
  await page.locator('.pagina-cartao', { hasText: 'Casa Teste' }).getByRole('button', { name: /Mudar de obra/ }).click();
  await dlg.getByLabel('Obra').selectOption({ label: 'Ribamar' });
  await dlg.getByRole('button', { name: 'Mudar' }).click();
  await expect(obra.locator('.pagina-cartao', { hasText: 'Casa Teste' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Sem obra' })).toHaveCount(0);
  // a page loaded straight into the obra
  await obra.locator('input[name="pagina-ficheiro"]').setInputFiles({ name: 'casa-dois.html', mimeType: 'text/html', buffer: Buffer.from(PAGINA.replace('Casa Teste', 'Casa Dois')) });
  await expect(obra.locator('.pagina-cartao', { hasText: 'Casa Dois' })).toBeVisible();
  await expect(obra.locator('summary')).toContainText('2 páginas');
  expect(await db(page, () => { const f = window.__fake.db; const s = f.documentos_seccoes.find((x) => x.nome === 'Ribamar');
    return f.documentos.filter((d) => d.tipo === 'pagina').every((d) => d.seccao_id === s.id); })).toBe(true);
  // an obra with pages cannot be deleted
  await obra.getByRole('button', { name: /Apagar a obra/ }).click();
  await expect(page.getByText(/Para apagar a obra «Ribamar»/)).toBeVisible();
  // closed again when the tab is opened again
  await page.locator('#sub-abas').getByRole('link', { name: /Workflow/ }).click();
  await page.locator('#sub-abas').getByRole('link', { name: /Páginas/ }).click();
  await expect(page.locator('details.pag-obra', { hasText: 'Ribamar' })).not.toHaveAttribute('open', '');
  expect(erros).toEqual([]);
});

test('Páginas: checkpoints e tarefas próprios da aba, fora do Workflow', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/builder/paginas' });
  await page.locator('[data-acao="acrescentar"][data-tipo="checkpoint"][data-aba="paginas"]').click();
  const dlg = page.locator('#dlg');
  await expect(dlg.getByLabel('Posição no workflow')).toBeHidden();   // they go to the end of the tab
  await dlg.getByLabel('Título').fill('Estrutura da página');
  await dlg.getByRole('button', { name: 'Acrescentar' }).click();
  const cp = page.locator('.passo', { hasText: 'Estrutura da página' });
  await expect(cp).toBeVisible();
  expect(await db(page, () => window.__fake.db.checkpoints.find((c) => c.titulo === 'Estrutura da página').aba)).toBe('paginas');
  // a task in it, from the tab's «Tarefa» button: only this tab's checkpoints are offered
  await page.locator('[data-acao="acrescentar"][data-tipo="tarefa"][data-aba="paginas"]').click();
  await expect(dlg.getByLabel('Checkpoint')).toHaveText('Estrutura da página');
  await dlg.getByLabel('Título').fill('Pormenores da página');
  await dlg.getByRole('button', { name: 'Acrescentar' }).click();
  await expect(cp).toContainText('Pormenores da página');
  // the Workflow tab does not show them; a link to the task opens the Páginas tab
  await page.locator('#sub-abas').getByRole('link', { name: /Workflow/ }).click();
  await expect(page.locator('.passo', { hasText: 'Estrutura da página' })).toHaveCount(0);
  const tid = await db(page, () => window.__fake.db.tarefas.find((t) => t.titulo === 'Pormenores da página').id);
  await page.goto(`/#/projeto/builder/t-${tid}`);
  await expect(page.locator('#sub-abas').getByRole('link', { name: /Páginas/ })).toHaveAttribute('aria-current', 'page');
  expect(erros).toEqual([]);
});

test('Páginas: só os projetos com a aba a mostram', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/gerador' });
  await expect(page.locator('#sub-abas').getByRole('link', { name: /Workflow/ })).toBeVisible();
  await expect(page.locator('#sub-abas').getByRole('link', { name: /Páginas/ })).toHaveCount(0);
});
