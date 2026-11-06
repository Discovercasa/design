// Notificações vistas uma a uma (2026-11-06): por ver até se passar o rato (0,6 s), se abrir ou se tocar no ponto; as das
// minhas próprias ações contam como vistas. E o Início com os dados frescos ao mudar de página.
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const FIXTURE = readFileSync(new URL('./fixture.json', import.meta.url), 'utf8');
const FIXTURE_SOCIAL = readFileSync(new URL('./fixture_social.json', import.meta.url), 'utf8');
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');

async function abrir(page, rota = '/') {
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|Failed to load resource/.test(m.text())) erros.push(m.text()); });
  await page.addInitScript(([fx, fs]) => { window.__FIXTURE = JSON.parse(fx); window.__FIXTURE_SOCIAL = JSON.parse(fs); }, [FIXTURE, FIXTURE_SOCIAL]);
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await page.goto(rota);
  await expect(page.locator('#vista h1')).toBeVisible();
  return erros;
}
const db = (page, expr, arg) => page.evaluate(expr, arg);
const ehTelemovel = () => test.info().project.name === 'telemovel';

test('notificações por ver: ponto, abrir, rato; as minhas não contam; o estado fica guardado', async ({ page }) => {
  const erros = await abrir(page);
  // duas de outra pessoa e uma minha
  await db(page, () => window.__fake.comoOutro((x) => x.tarefas.update({ estado: 'concluida' }).eq('id', 72)));
  await db(page, () => window.__fake.comoOutro((x) => x.tarefas.update({ estado: 'em_curso' }).eq('id', 36)));
  await db(page, () => window.__fake.comoEu((x) => x.tarefas.update({ estado: 'em_curso' }).eq('id', 37)));
  await expect(page.locator('#contador')).toHaveText('2');
  await page.getByRole('button', { name: /Notificações/ }).click();
  const pop = page.locator('#pop-notificacoes');
  await expect(pop.locator('[data-por-ver]')).toHaveText('2 por ver');
  await expect(pop.locator('.notif.nao-lida')).toHaveCount(2);
  // a lista cabe no ecrã (também no telemóvel)
  const caixa = await pop.boundingBox();
  expect(caixa.x).toBeGreaterThanOrEqual(0);
  expect(caixa.x + caixa.width).toBeLessThanOrEqual(page.viewportSize().width);
  const minha = pop.locator('.notif.propria');
  await expect(minha).toContainText('feita por ti');
  await expect(minha.locator('.notif-marca')).toHaveCount(0);
  // tocar no ponto: vista (sem abrir)
  const primeira = pop.locator('.notif', { hasText: 'Testar primeiro em rede local' });
  await primeira.getByRole('button', { name: 'Marcar como vista' }).click();
  await expect(primeira).not.toHaveClass(/nao-lida/);
  await expect(page.locator('#contador')).toHaveText('1');
  await expect(pop.locator('[data-por-ver]')).toHaveText('1 por ver');
  expect(await db(page, () => window.__fake.db.notificacoes_lidas.length)).toBe(1);
  // e de novo por ver
  await primeira.getByRole('button', { name: 'Marcar como por ver' }).click();
  await expect(primeira).toHaveClass(/nao-lida/);
  await expect(page.locator('#contador')).toHaveText('2');
  const segunda = pop.locator('.notif', { hasText: 'Rever o documento Cobertura' });
  if (!ehTelemovel()) {
    // com o rato: vista depois de 0,6 s por cima
    await segunda.locator('.notif-abrir').hover();
    await expect(segunda).not.toHaveClass(/nao-lida/, { timeout: 3000 });
    await expect(page.locator('#contador')).toHaveText('1');
    // passar de raspão não conta
    await primeira.locator('.notif-abrir').hover();
    await page.mouse.move(5, 5);
    await page.waitForTimeout(900);
    await expect(primeira).toHaveClass(/nao-lida/);
  } else {
    await segunda.getByRole('button', { name: 'Marcar como vista' }).click();
    await expect(page.locator('#contador')).toHaveText('1');
  }
  // abrir uma: fica vista e vai para a tarefa
  await page.getByRole('button', { name: /Notificações/ }).click().catch(() => {});
  if (await pop.isHidden()) await page.getByRole('button', { name: /Notificações/ }).click();
  await pop.locator('.notif', { hasText: 'Testar primeiro em rede local' }).locator('.notif-abrir').click();
  await expect(page).toHaveURL(/#\/projeto\/step-inside\/t-72$/);
  await expect(page.locator('#contador')).toBeHidden();
  // recarregar: continua tudo visto
  await page.reload();
  await expect(page.locator('#vista h1')).toBeVisible();
  await page.waitForTimeout(400);
  await expect(page.locator('#contador')).toBeHidden();
  expect(erros).toEqual([]);
});

test('Início: o estado dos posts vem fresco ao mudar de página (mesmo sem a ligação em direto)', async ({ page }) => {
  await abrir(page, '/#/social');
  // outra pessoa publica o post desta semana noutro aparelho e a ligação em direto desta janela falhou (nada avisa)
  await db(page, () => { const p = window.__fake.db.posts.find((x) => x.titulo === 'Gaia - Aumento estrutura'); p.estado = 'publicado'; });
  await page.getByRole('navigation', { name: 'Secções' }).getByRole('link', { name: 'Início' }).click();
  const social = page.locator('section', { has: page.getByRole('heading', { name: 'Redes sociais', level: 2 }) });
  await expect(social.locator('.bloco-lateral').first()).toContainText('Publicado');
  await expect(social.locator('.bloco-lateral').nth(1)).not.toContainText('Gaia - Aumento estrutura');
});
