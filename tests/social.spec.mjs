// Testes das redes sociais do hub (planeamento dos posts, editor com fotos e legenda, aprovação, comentários, obras e
// fases). Base simulada: fake-supabase.js + fixture.json + fixture_social.json (o Excel importado pela migração 0010).
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { deflateSync } from 'node:zlib';

const FIXTURE = readFileSync(new URL('./fixture.json', import.meta.url), 'utf8');
const FIXTURE_SOCIAL = readFileSync(new URL('./fixture_social.json', import.meta.url), 'utf8');
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
const captura = (page, nome) => page.screenshot({ path: fileURLToPath(new URL(`./capturas/${nome}-${test.info().project.name}.png`, import.meta.url)), fullPage: true });
// PNG de 2×2 (vermelho) para carregar como "foto", feito aqui (assinatura, IHDR, IDAT, IEND com CRC)
const CRC = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
const crc32 = (b) => { let c = 0xffffffff; for (const x of b) c = CRC[(c ^ x) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
const bloco = (tipo, dados) => { const t = Buffer.concat([Buffer.from(tipo), dados]); const n = Buffer.alloc(4); n.writeUInt32BE(dados.length); const c = Buffer.alloc(4); c.writeUInt32BE(crc32(t)); return Buffer.concat([n, t, c]); };
const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(2, 0); ihdr.writeUInt32BE(2, 4); ihdr[8] = 8; ihdr[9] = 2;
const PNG = Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), bloco('IHDR', ihdr),
  bloco('IDAT', deflateSync(Buffer.from([0, 255, 0, 0, 255, 0, 0, 0, 255, 0, 0, 255, 0, 0]))), bloco('IEND', Buffer.alloc(0))]);

async function abrir(page, { utilizador, rota = '/#/social' } = {}) {
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|Failed to load resource/.test(m.text())) erros.push(m.text()); });
  page.on('dialog', (d) => d.accept());
  await page.addInitScript(([fx, fs, u]) => { window.__FIXTURE = JSON.parse(fx); window.__FIXTURE_SOCIAL = JSON.parse(fs); if (u) window.__UTILIZADOR = u; }, [FIXTURE, FIXTURE_SOCIAL, utilizador || null]);
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await page.goto(rota);
  await expect(page.locator('#vista h1')).toBeVisible();
  return erros;
}
const db = (page, expr, arg) => page.evaluate(expr, arg);
const editor = (page) => page.locator('#dlg form[data-sform="post"]');

test('planeamento: os meses e as semanas do Excel, com fotos, estados e o filtro por obra', async ({ page }) => {
  const erros = await abrir(page);
  const nav = page.getByRole('navigation', { name: 'Secções' });
  await expect(nav.getByRole('link', { name: 'Redes sociais' })).toHaveAttribute('aria-current', 'page');
  await expect(page.getByRole('heading', { level: 1, name: 'Redes sociais' })).toBeVisible();
  await expect(page.locator('.post-cartao')).toHaveCount(24);
  for (const m of ['julho de 2026', 'agosto de 2026', 'setembro de 2026', 'outubro de 2026', 'novembro de 2026', 'dezembro de 2026'])
    await expect(page.locator('.mes h2', { hasText: m })).toHaveCount(1);
  // os meses que já passaram ficam fechados em "Meses anteriores"
  const passados = page.locator('details.meses-passados');
  if (await passados.count()) {
    await expect(passados.locator('.post-cartao').first()).toBeHidden();
    await passados.locator('summary').click();
    await expect(passados.locator('.post-cartao').first()).toBeVisible();
  }
  const gaia = page.locator('.post-cartao', { hasText: 'Gaia - Aumento estrutura' });
  await expect(gaia).toContainText('Por aprovar');
  await expect(gaia).toContainText('Gaia · Aumento');
  await expect(gaia.locator('.pf img')).toHaveCount(4);
  await expect(gaia.locator('.pf img').first()).toHaveAttribute('src', /.+/);
  await expect(page.locator('.post-cartao', { hasText: 'Boelhe - BF' })).toContainText('Publicado');
  await expect(page.locator('.post-cartao', { hasText: 'Cães - Natalicio' })).toContainText('Sem fotos');
  // filtro: só Matosinhos
  await page.locator('select[data-sacao="filtro-obra"]').selectOption({ label: 'Matosinhos' });
  await expect(page.locator('.post-cartao')).toHaveCount(6);
  await captura(page, 'social-planeamento');
  expect(erros).toEqual([]);
});

test('editor: legenda com emojis, contagem, avisos e aprovação da legenda e das fotos', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/social/post-9' });
  // post com formatação que o Instagram não percebe (**…** e [ligação](…))
  await expect(editor(page)).toBeVisible();
  await expect(page.locator('#pe-contagem')).toContainText('/ 2200 caracteres');
  await expect(page.locator('.avisos-legenda')).toContainText('mostra tal e qual');
  await editor(page).locator('.dlg-rodape').getByRole('button', { name: 'Fechar' }).click();
  await expect(page).toHaveURL(/#\/social$/);

  // aprovar a legenda e as fotos do post desta semana → fica "Aprovado"
  await page.locator('.post-cartao', { hasText: 'Gaia - Aumento estrutura' }).click();
  await expect(editor(page)).toBeVisible();
  await expect(page).toHaveURL(/#\/social\/post-17$/);
  await page.getByRole('button', { name: 'Emojis' }).click();
  const legenda = page.locator('#pe-legenda');
  await legenda.click();
  await legenda.press('Control+End');
  await legenda.press('Enter');
  await page.getByRole('button', { name: 'Inserir 🏡' }).click();
  await legenda.pressSequentially(' Mais uma etapa! #Discovercasa');
  await expect(legenda).toHaveValue(/🏡 Mais uma etapa! #Discovercasa$/);
  await editor(page).locator('input[name=legenda_aprovada]').check();
  await editor(page).locator('input[name=fotos_aprovadas]').check();
  await editor(page).getByRole('button', { name: 'Guardar', exact: true }).click();
  await expect(page.locator('.aviso', { hasText: 'Aprovado' })).toBeVisible();
  const p = await db(page, () => window.__fake.db.posts.find((x) => x.id === 17));
  expect(p.estado).toBe('aprovado');
  expect(p.legenda).toMatch(/🏡 Mais uma etapa! #Discovercasa$/);
  expect(p.legenda_aprovada_por_nome).toBe('Teste Hub');
  await expect(editor(page)).toContainText('por Teste Hub');
  // mudar a legenda depois de aprovada pede nova aprovação
  await legenda.fill(p.legenda + ' ✨');
  await editor(page).getByRole('button', { name: 'Guardar', exact: true }).click();
  await expect.poll(() => db(page, () => window.__fake.db.posts.find((x) => x.id === 17).estado)).toBe('por_aprovar');
  await expect(editor(page).locator('input[name=legenda_aprovada]')).not.toBeChecked();
  // pré-visualizar
  await page.getByRole('button', { name: 'Pré-visualizar' }).click();
  await expect(page.locator('.previa-legenda')).toContainText('discovercasa');
  await expect(page.locator('.previa-foto img')).toHaveCount(4);
  await captura(page, 'social-editor');
  expect(erros).toEqual([]);
});

test('post novo numa semana vazia: fotos carregadas, ordenadas e tiradas; fotos novas pedem nova aprovação', async ({ page }) => {
  const erros = await abrir(page);
  await page.locator('section.mes button.semana-vazia').first().click();
  const f = page.locator('#dlg form[data-sform="novo-post"]');
  await f.locator('input[name=titulo]').fill('Ribamar - Estrutura');
  await f.locator('select[name=obra]').selectOption({ label: 'Ribamar' });
  await f.locator('select[name=fase]').selectOption({ label: 'Estrutura' });
  await f.getByRole('button', { name: 'Criar e acrescentar fotos' }).click();
  await expect(editor(page)).toBeVisible();
  const id = await db(page, () => window.__fake.db.posts.at(-1).id);
  await expect(page).toHaveURL(new RegExp(`#/social/post-${id}$`));
  await editor(page).locator('input[name=media]').setInputFiles([
    { name: 'estrutura-1.png', mimeType: 'image/png', buffer: PNG },
    { name: 'estrutura-2.png', mimeType: 'image/png', buffer: PNG },
    { name: 'estrutura-3.png', mimeType: 'image/png', buffer: PNG }]);
  await expect(editor(page).locator('.pe-foto')).toHaveCount(3);
  await expect(page.locator('.aviso', { hasText: '3 fotos acrescentadas' })).toBeVisible();
  const media = await db(page, (pid) => window.__fake.db.posts_media.filter((m) => m.post_id === pid), id);
  expect(media.map((m) => m.nome_ficheiro)).toEqual(['estrutura-1.png', 'estrutura-2.png', 'estrutura-3.png']);
  expect(media.every((m) => /^miniaturas\//.test(m.miniatura) && m.largura === 2)).toBe(true);
  // a terceira passa para segunda
  await editor(page).locator('.pe-foto').nth(2).hover();
  await editor(page).locator('.pe-foto').nth(2).getByRole('button', { name: 'Para trás' }).click();
  await expect.poll(() => db(page, (pid) => window.__fake.db.posts_media.filter((m) => m.post_id === pid).sort((a, b) => a.ordem - b.ordem).map((m) => m.nome_ficheiro), id))
    .toEqual(['estrutura-1.png', 'estrutura-3.png', 'estrutura-2.png']);
  // aprovar as fotos e depois tirar uma: as fotos voltam a precisar de aprovação
  await editor(page).locator('input[name=fotos_aprovadas]').check();
  await editor(page).getByRole('button', { name: 'Guardar', exact: true }).click();
  await expect.poll(() => db(page, (pid) => window.__fake.db.posts.find((x) => x.id === pid).fotos_aprovadas, id)).toBe(true);
  await editor(page).locator('.pe-foto').first().hover();
  await editor(page).getByRole('button', { name: 'Tirar estrutura-1.png' }).click();
  await expect(editor(page).locator('.pe-foto')).toHaveCount(2);
  await expect.poll(() => db(page, (pid) => window.__fake.db.posts.find((x) => x.id === pid).fotos_aprovadas, id)).toBe(false);
  expect(await db(page, () => window.__fake.social.has(window.__fake.db.posts_media.at(-1).caminho))).toBe(true);
  // pedir aprovação: guarda e passa a "Por aprovar"
  await editor(page).locator('#pe-legenda').fill('A estrutura já está de pé. 🏗️');
  await editor(page).getByRole('button', { name: 'Guardar e pedir aprovação' }).click();
  await expect.poll(() => db(page, (pid) => window.__fake.db.posts.find((x) => x.id === pid).estado, id)).toBe('por_aprovar');
  await editor(page).locator('.dlg-rodape').getByRole('button', { name: 'Fechar' }).click();
  await expect(page.locator('.post-cartao', { hasText: 'Ribamar - Estrutura' })).toContainText('Por aprovar');
  expect(erros).toEqual([]);
});

test('comentários de aprovação: os do Excel, um novo sobre uma foto, resolver', async ({ page }) => {
  await abrir(page, { rota: '/#/social/post-7' });
  const c = page.locator('#pe-comentarios');
  await expect(c.locator('li.resolvido')).toHaveCount(2);
  await expect(c).toContainText('consegues tirar aquele saco?');
  await expect(c).toContainText('sobre a foto 3');
  await c.locator('#pe-coment-texto').fill('Esta fica melhor como primeira.');
  await c.locator('#pe-coment-foto').selectOption({ label: 'Sobre a foto 2' });
  await c.getByRole('button', { name: 'Comentar' }).click();
  await expect(c.locator('li:not(.resolvido)')).toContainText('Esta fica melhor como primeira.');
  await expect(page.locator('.pe-foto').nth(1).locator('.pe-coment')).toBeVisible();
  await c.locator('li:not(.resolvido)').getByRole('button', { name: 'Resolvido' }).click();
  await expect(c.locator('li.resolvido')).toHaveCount(3);
  const n = await db(page, () => window.__fake.db.notificacoes.filter((x) => x.tipo === 'post_comentario').length);
  expect(n).toBe(1);
});

test('obras: fases que não se apagam, visita para fotos, fase nova na posição e obra nova', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/social/obras' });
  await expect(page.locator('.obra')).toHaveCount(9);
  const mat = page.locator('.obra', { hasText: 'Matosinhos' });
  await expect(mat.locator('.fase-linha')).toHaveCount(4);
  await expect(mat.locator('.fase-linha.concluida')).toHaveCount(2);
  await expect(mat).toContainText('Julho - Ago');
  await expect(mat.locator('.obra-posts .chip')).toHaveCount(6);
  // a Estrutura de Matosinhos passa a em curso → aparece nas visitas para fotos
  await mat.getByRole('button', { name: 'Estrutura' }).click();
  const f = page.locator('#dlg form[data-sform="fase"]');
  await expect(f).toContainText('As fases não se apagam');
  await expect(f.getByRole('button', { name: /Apagar/ })).toHaveCount(0);
  await f.locator('select[name=estado]').selectOption('em_curso');
  await f.getByRole('button', { name: 'Guardar' }).click();
  const visita = page.locator('.visita', { hasText: 'Matosinhos' });
  await expect(visita).toContainText('Estrutura');
  await expect(page.locator('.obra', { hasText: 'Matosinhos' })).toContainText('Agora: Estrutura');
  await visita.getByRole('button', { name: 'Marcar visita' }).click();
  await page.locator('#dlg input[name=visita_em]').fill('2026-11-20');
  await page.locator('#dlg').getByRole('button', { name: 'Marcar', exact: true }).click();
  await expect(page.locator('.visita', { hasText: 'Matosinhos' })).toContainText(/Visita marcada para 20/);
  expect(await db(page, () => window.__fake.db.obras_fases.find((x) => x.obra_id === 1 && x.nome === 'Estrutura').visita_em)).toBe('2026-11-20');
  await page.locator('.visita', { hasText: 'Matosinhos' }).getByRole('button', { name: 'Fotos tiradas' }).click();
  await expect(page.locator('.visita', { hasText: 'Matosinhos' })).toHaveCount(0);
  const fase = await db(page, () => window.__fake.db.obras_fases.find((x) => x.obra_id === 1 && x.nome === 'Estrutura'));
  expect(fase.fotos).toBe('tiradas');
  expect(fase.fotos_em).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  // fase nova em Ribamar na posição 3
  await page.locator('.obra', { hasText: 'Ribamar' }).getByRole('button', { name: 'Fase' }).click();
  await page.locator('#dlg input[name=nome]').fill('Licenciamento');
  await page.locator('#dlg select[name=posicao]').selectOption('3');
  await page.locator('#dlg').getByRole('button', { name: 'Acrescentar fase' }).click();
  await expect(page.locator('.obra', { hasText: 'Ribamar' }).locator('.fase-linha').nth(2)).toContainText('Licenciamento');
  const ordem = await db(page, () => window.__fake.db.obras_fases.filter((x) => x.obra_id === 4).sort((a, b) => a.ordem - b.ordem).map((x) => x.nome));
  expect(ordem).toEqual(['Projetos', 'Movimento de terras', 'Licenciamento', 'Base de fundação', 'Estrutura', 'Acabamentos']);
  // obra nova com as fases do modelo (menos "Projetos")
  await page.getByRole('button', { name: 'Obra', exact: true }).click();
  await page.locator('#dlg input[name=nome]').fill('Penafiel');
  await page.locator('#dlg label.chip-check', { hasText: 'Projetos' }).locator('input').uncheck();
  await page.locator('#dlg').getByRole('button', { name: 'Criar obra' }).click();
  const nova = page.locator('.obra', { hasText: 'Penafiel' });
  await expect(nova.locator('.fase-linha')).toHaveCount(5);
  await expect(nova.locator('.fase-linha').first()).toContainText('Movimento de terras');
  // arquivar: sai da lista, fica em "Obras arquivadas"
  await nova.getByRole('button', { name: 'Editar a obra Penafiel' }).click();
  await page.locator('#dlg input[name=arquivada]').check();
  await page.locator('#dlg').getByRole('button', { name: 'Guardar' }).click();
  await expect(page.locator('.obras-grelha').first().locator('.obra', { hasText: 'Penafiel' })).toHaveCount(0);
  await expect(page.locator('details.meses-passados summary')).toContainText('Obras arquivadas');
  // as fases não se apagam nem na base de dados
  const r = await db(page, () => window.__fake.comoOutro((x) => x.obras_fases.delete().eq('id', 1)));
  expect(r.error && r.error.message).toMatch(/não se apagam/);
  await captura(page, 'social-obras');
  expect(erros).toEqual([]);
});

test('Início: resumo das redes sociais (esta semana, por aprovar, visitas)', async ({ page }) => {
  await abrir(page, { rota: '/#/' });
  const r = page.locator('section', { has: page.getByRole('heading', { name: 'Redes sociais', level: 2 }) });
  await expect(r).toContainText('Por aprovar');
  await expect(r.locator('.bloco-lateral').nth(1)).toContainText('Gaia - Aumento estrutura');
  await r.getByRole('link', { name: /Planeamento/ }).click();
  await expect(page).toHaveURL(/#\/social$/);
});

test('quem só vê: sem planear nem editar, mas pode comentar', async ({ page }) => {
  await abrir(page, { utilizador: { id: 'u-ver', nome: 'So Ver', nivel: 'ver' }, rota: '/#/social/post-17' });
  await expect(editor(page)).toBeVisible();
  await expect(editor(page).locator('input[name=titulo]')).toBeDisabled();
  await expect(editor(page).locator('#pe-legenda')).toBeDisabled();
  await expect(editor(page).getByRole('button', { name: 'Guardar', exact: true })).toHaveCount(0);
  await expect(editor(page).locator('input[name=media]')).toHaveCount(0);
  await editor(page).locator('#pe-coment-texto').fill('Gosto muito da terceira.');
  await editor(page).getByRole('button', { name: 'Comentar' }).click();
  await expect(page.locator('#pe-comentarios')).toContainText('Gosto muito da terceira.');
  await editor(page).locator('.dlg-rodape').getByRole('button', { name: 'Fechar' }).click();
  await expect(page.getByRole('button', { name: 'Post', exact: true })).toHaveCount(0);
  await expect(page.locator('button.semana-vazia')).toHaveCount(0);
});

test('em direto: um post planeado por outra pessoa aparece logo, com o pop-up "Novo"', async ({ page }) => {
  await abrir(page);
  await db(page, () => window.__fake.comoOutro((x) => x.posts.insert({ mes: '2026-12-01', semana: 4, titulo: 'Boas festas', obra_id: null })));
  await expect(page.locator('.post-cartao', { hasText: 'Boas festas' })).toBeVisible();
  await expect(page.locator('.aviso', { hasText: 'Novo post' })).toBeVisible();
  await expect(page.locator('.post-cartao', { hasText: 'Boas festas' }).locator('.chip.novo')).toBeVisible();
  // e a notificação leva ao post
  await page.getByRole('button', { name: /Notificações/ }).click();
  await page.locator('#pop-notificacoes .notif', { hasText: 'planeou o post' }).click();
  await expect(editor(page)).toContainText('Boas festas');
});

test('mudar de página com o editor aberto fecha-o', async ({ page }) => {
  await abrir(page, { rota: '/#/social/post-18' });
  await expect(editor(page)).toBeVisible();
  await page.evaluate(() => { location.hash = '#/'; });
  await expect(page.locator('#dlg')).toBeHidden();
  await expect(page.locator('#t-social')).toBeVisible();
});
