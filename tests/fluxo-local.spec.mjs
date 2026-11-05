// O fluxo completo do Gerador com uma planta real que fica no PC (os desenhos não vão para o Git):
//   PLANTA="caminho/para/planta.dwfx" npx playwright test fluxo-local.spec.mjs
// Sem PLANTA, este teste é saltado.
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
const PLANTA = process.env.PLANTA;
test('gerador: fluxo completo com uma planta real', async ({ page }) => {
  test.skip(!PLANTA, 'sem PLANTA (desenho local)');
  test.setTimeout(240000);
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await page.goto('/gerador/');
  await expect(page.locator('#estado')).toContainText('Pronto', { timeout: 90000 });
  await page.locator('#ficheiro').setInputFiles(PLANTA);
  await expect(page.locator('#passo-planta')).toBeVisible({ timeout: 90000 });
  await page.getByRole('button', { name: 'Gerar documentos' }).click();
  await expect(page.locator('#passo-docs')).toBeVisible({ timeout: 120000 });
  await expect(page.locator('.docs a')).not.toHaveCount(0);
  await page.waitForTimeout(800);
  const cap = (n) => fileURLToPath(new URL(`./capturas/${n}-${test.info().project.name}.png`, import.meta.url));
  await page.screenshot({ path: cap('gerador-fluxo'), fullPage: true });
  console.log('docs:', await page.locator('.docs a .g-doc-nome').allTextContents(), 'erros:', erros);
});
