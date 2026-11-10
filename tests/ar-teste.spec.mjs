// The Android AR test page (/ar-teste.html), outside the hub (team note 10 on task 84, 2026-11-10: the Google app never
// asked for the model). The page must build the right links and work out by itself what happened after each tap.
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const FIXTURE = readFileSync(new URL('./fixture.json', import.meta.url), 'utf8');
const FIXTURE_SOCIAL = readFileSync(new URL('./fixture_social.json', import.meta.url), 'utf8');
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
const NOSSO = 'http://localhost:4321/__ficheiro?c=plataforma_cliente%2Far%2Fabc__torres-vedras_ar_casa.glb';

async function abrir(page, rota) {
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  await page.addInitScript(([fx, fs]) => { window.__FIXTURE = JSON.parse(fx); window.__FIXTURE_SOCIAL = JSON.parse(fs); }, [FIXTURE, FIXTURE_SOCIAL]);
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await page.goto(rota);
  return erros;
}
const resultado = (page, id) => page.locator(`[data-res="${id}"]`);
// the intent itself cannot open in a desktop browser: keep the tap, stop the navigation
const semNavegar = (page, id) => page.evaluate((i) => document.querySelector(`[data-teste="${i}"]`).addEventListener('click', (e) => e.preventDefault()), id);
const visibilidade = (page, v) => page.evaluate((v) => {
  Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => v });
  document.dispatchEvent(new Event('visibilitychange'));
}, v);

test('página de teste do AR: oito testes, os links certos e o resultado sozinho', async ({ page }) => {
  const erros = await abrir(page, '/ar-teste.html#' + new URLSearchParams({ u: NOSSO, t: 'Torres Vedras · casa 1:1', doc: '43', real: '1' }));
  await expect(page.locator('#testes > li')).toHaveCount(8);
  await expect(page).toHaveURL(/\/ar-teste\.html$/);   // the signed link does not stay in the address
  // Google's sample through the Google app (1.0 and 1.2) and through ARCore; our model the same way
  await expect(page.locator('[data-teste="G1"]')).toHaveAttribute('href', /^intent:\/\/arvr\.google\.com\/scene-viewer\/1\.0\?file=https%3A%2F%2Fmodelviewer\.dev%2Fshared-assets%2Fmodels%2FAstronaut\.glb&mode=ar_preferred.*package=com\.google\.android\.googlequicksearchbox;.*browser_fallback_url=http%3A%2F%2Flocalhost%3A4321%2Far-teste\.html%3Fvolta%3DG1;end;$/);
  await expect(page.locator('[data-teste="G2"]')).toHaveAttribute('href', /^intent:\/\/arvr\.google\.com\/scene-viewer\/1\.2\?mode=ar_preferred&disable_occlusion=true.+&file=https%3A%2F%2Fmodelviewer\.dev.+Astronaut\.glb#Intent;/);
  await expect(page.locator('[data-teste="G3"]')).toHaveAttribute('href', /^intent:\/\/arvr\.google\.com\/scene-viewer\/1\.0\?file=.+Astronaut\.glb&mode=ar_only.*#Intent;scheme=https;package=com\.google\.ar\.core;/);
  await expect(page.locator('[data-teste="N2"]')).toHaveAttribute('href', /^intent:\/\/arvr\.google\.com\/scene-viewer\/1\.2\?c=plataforma_cliente.+&resizable=false&title=Torres\+Vedras.+&file=http%3A%2F%2Flocalhost%3A4321%2F__ficheiro.+\.glb#Intent;.*googlequicksearchbox/);
  await expect(page.locator('[data-teste="N3"]')).toHaveAttribute('href', /mode=ar_only&title=.+&resizable=false#Intent;.*package=com\.google\.ar\.core;.*volta%3DN3;end;$/);
  await expect(page.locator('[data-webxr="G4"]')).toBeVisible();
  await expect(page.locator('#info')).toContainText('Nosso modelo');
  await expect(page.locator('#info')).toContainText('Torres Vedras · casa 1:1');

  // 1. tap, nothing happens for 4 s (no app, no fallback)
  await semNavegar(page, 'G1');
  await page.locator('[data-teste="G1"]').click();
  await expect(resultado(page, 'G1')).toHaveText('a testar…');
  await expect(resultado(page, 'G1')).toContainText('nada aconteceu em 4 s', { timeout: 6000 });

  // 2. tap, another app takes over and gives the screen back by itself (no fallback): the team's symptom
  await semNavegar(page, 'N2');
  await page.locator('[data-teste="N2"]').click();
  await visibilidade(page, 'hidden');
  await page.waitForTimeout(300);
  await visibilidade(page, 'visible');
  await expect(resultado(page, 'N2')).toContainText('abriu outra app e voltou sozinho');
  await page.evaluate(() => delete document.visibilityState);   // back to the browser's own (hidden on unload)

  // 3. Chrome followed the fallback link after the Google app had opened (the page was hidden well before it unloaded)
  await page.evaluate(() => {
    const e = JSON.parse(localStorage.getItem('design-ar-teste'));
    e.toque = { id: 'G2', t: Date.now() - 2000, escondida: 250, visivel: null, saiu: 1600 };
    localStorage.setItem('design-ar-teste', JSON.stringify(e));
  });
  await page.goto('/ar-teste.html?volta=G2');
  await expect(resultado(page, 'G2')).toContainText('voltou pelo link de recurso');
  await expect(resultado(page, 'G2')).toContainText('Outra app abriu 0,3 s depois do toque');
  await expect(page).toHaveURL(/\/ar-teste\.html$/);
  // the earlier results are still there (kept on the phone)
  await expect(resultado(page, 'G1')).toContainText('nada aconteceu');

  // 4. Chrome went straight to the fallback (no app opened: hidden and unloaded at the same moment)
  await page.evaluate(() => {
    const e = JSON.parse(localStorage.getItem('design-ar-teste'));
    e.toque = { id: 'N3', t: Date.now() - 500, escondida: 40, visivel: null, saiu: 45 };
    localStorage.setItem('design-ar-teste', JSON.stringify(e));
  });
  await page.goto('/ar-teste.html?volta=N3');
  await expect(resultado(page, 'N3')).toContainText('Nenhuma app chegou a abrir');

  // 5. the Google app opened, Chrome showed the page again for a moment and then followed the fallback link
  await semNavegar(page, 'G3');
  await page.locator('[data-teste="G3"]').click();
  await visibilidade(page, 'hidden');
  await page.waitForTimeout(200);
  await visibilidade(page, 'visible');
  await page.evaluate(() => delete document.visibilityState);
  await page.goto('/ar-teste.html?volta=G3');
  await expect(resultado(page, 'G3')).toContainText('voltou pelo link de recurso');
  await expect(resultado(page, 'G3')).toContainText('Outra app abriu');

  // 6. send it to the AR test task (the person's own session), with what the page found out
  await page.locator('#notas').fill('Telemóvel de teste');
  await page.getByRole('button', { name: 'Enviar para a tarefa do teste' }).click();
  await expect(page.locator('#estado-envio')).toHaveText('Enviado para a tarefa do teste. Obrigado!');
  const nota = await page.evaluate(() => window.__fake.db.tarefas_notas.at(-1));
  const tarefa = await page.evaluate(() => window.__fake.db.tarefas.find((t) => /iPhone e um Android/.test(t.titulo)).id);
  expect(nota.tarefa_id).toBe(tarefa);
  expect(nota.tipo).toBe('nota');
  expect(nota.texto).toContain('Teste do AR no Android (página de teste, fora do hub)');
  expect(nota.texto).toContain('G1. Exemplo da Google · app Google · link 1.0: nada aconteceu em 4 s');
  expect(nota.texto).toContain('N2. O nosso modelo · app Google · link 1.2 (o do botão do hub): abriu outra app e voltou sozinho');
  expect(nota.texto).toContain('Nosso modelo: Torres Vedras · casa 1:1 (documento 43)');
  expect(nota.texto).toContain('Notas: Telemóvel de teste');
  await page.screenshot({ path: `capturas/ar-teste-${test.info().project.name}.png`, fullPage: true });
  expect(erros).toEqual([]);
});

test('página de teste do AR aberta sem o hub: só o exemplo da Google', async ({ page }) => {
  const erros = await abrir(page, '/ar-teste.html');
  await page.evaluate(() => localStorage.removeItem('design-ar-teste'));
  await page.reload();
  await expect(page.locator('[data-teste="G1"]')).toBeVisible();
  await expect(page.locator('[data-teste="N2"]')).toHaveCount(0);
  await expect(page.locator('#testes')).toContainText('Abre esta página a partir do hub');
  await page.getByRole('button', { name: 'Enviar para a tarefa do teste' }).click();
  await expect(page.locator('#estado-envio')).toHaveText('Faz primeiro pelo menos um teste.');
  expect(erros).toEqual([]);
});
