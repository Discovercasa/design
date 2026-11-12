// Trabalho em equipa (migração 0022, 2026-11-11): o pop-up de cada projeto no Início, o ecrã de cada tarefa (ponto de
// situação por tópicos, pedidos, aprovação, pessoas marcadas, conversa com anexos e áudio), o pop-up das marcações,
// as críticas e o Log. Base simulada (fake-supabase.js): nada toca no Supabase real.
import { test, expect } from '@playwright/test';
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const FIXTURE = readFileSync(new URL('./fixture.json', import.meta.url), 'utf8');
const FIXTURE_SOCIAL = readFileSync(new URL('./fixture_social.json', import.meta.url), 'utf8');
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
mkdirSync(new URL('./capturas/', import.meta.url), { recursive: true });
const captura = (page, nome) => page.screenshot({ path: fileURLToPath(new URL(`./capturas/${nome}-${test.info().project.name}.png`, import.meta.url)) });
const ehTelemovel = () => test.info().project.name === 'telemovel';
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64');
const TERCEIRA = { id: 'u-terceira', nome: 'Terceira Pessoa', criado_em: '2026-11-01T00:00:00Z', notificacoes_vistas_em: '2026-11-01T00:00:00Z' };
// a fake microphone for the audio message (Chromium)
test.use({ permissions: ['microphone'], launchOptions: { args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] } });

async function abrir(page, { equipa = {}, utilizador, rota = '/' } = {}) {
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|Failed to load resource/.test(m.text())) erros.push(m.text()); });
  page.on('dialog', (d) => d.accept());
  await page.addInitScript(([fx, fs, eq, u]) => { window.__FIXTURE = JSON.parse(fx); window.__FIXTURE_SOCIAL = JSON.parse(fs); window.__FIXTURE_EQUIPA = eq; if (u) window.__UTILIZADOR = u; },
    [FIXTURE, FIXTURE_SOCIAL, { perfis: [TERCEIRA], ...equipa }, utilizador || null]);
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await page.goto(rota);
  await expect(page.locator('#vista h1')).toBeVisible();
  return erros;
}
const db = (page, expr, arg) => page.evaluate(expr, arg);
const ficha = (page) => page.locator('#ficha');

test('Início: cada projeto abre um pop-up com o que está em curso e o que precisa de atenção', async ({ page }) => {
  const erros = await abrir(page);
  // the topbar has no general chat any more
  await expect(page.getByRole('button', { name: 'Chat', exact: true })).toHaveCount(0);
  // a task waiting for approval and a blocked one in Build Your House
  await db(page, () => window.__fake.comoOutro(async (x) => { await x.tarefas.update({ estado: 'bloqueada' }).eq('id', 37); }));
  await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')));
  await page.locator('.projeto-linha', { hasText: 'Build Your House' }).click();
  await expect(page).toHaveURL(/:4321\/(#\/)?$/);   // it does not leave the Início
  const pop = page.locator('#projeto-pop');
  await expect(pop.getByRole('heading', { level: 2 })).toContainText('Build Your House');
  await expect(pop.locator('details.situacao')).toHaveAttribute('open', '');
  await expect(pop.locator('.pp-grupo', { has: page.getByRole('heading', { name: /^Em curso/ }) })).toContainText('Várias águas');
  // each task shows once, in the group that needs most attention: the team test has notes to resolve
  await expect(pop.locator('.pp-grupo', { has: page.getByRole('heading', { name: /^Testes com notas/ }) })).toContainText('Teste completo do configurador');
  await expect(pop.locator('.pp-grupo', { hasText: 'Checkpoint atual' })).toContainText('Respostas pendentes');
  await expect(pop.getByRole('link', { name: 'Abrir o projeto' })).toHaveAttribute('href', '#/projeto/build-your-house');
  await captura(page, 'equipa-popup-projeto');
  // a task opens its screen on top of the pop-up; closing it goes back to the pop-up
  await pop.locator('.pp-linha', { hasText: 'Teste completo do configurador' }).click();
  await expect(ficha(page).getByRole('heading', { name: /Teste completo do configurador/ })).toBeVisible();
  await ficha(page).locator('.ficha-topo').getByRole('button', { name: 'Fechar' }).click();
  await expect(ficha(page)).toBeHidden();
  await expect(pop).toBeVisible();
  // «Abrir o projeto»
  await pop.getByRole('link', { name: 'Abrir o projeto' }).click();
  await expect(page).toHaveURL(/#\/projeto\/build-your-house$/);
  await expect(pop).toBeHidden();
  expect(erros).toEqual([]);
});

test('ecrã da tarefa: ponto de situação por tópicos, marcar, pedir, mensagem com ficheiro e áudio, sugestão', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/orcamentacao' });
  // everything collapsed: open the checkpoint, then the task title opens its screen
  await page.locator('.passo', { hasText: 'Composição do preço final' }).locator('.passo-topo').click();
  await page.locator('.tarefa-titulo', { hasText: 'Definir como se calcula cada parcela' }).click();
  const f = ficha(page);
  await expect(f.getByRole('heading', { name: 'Definir como se calcula cada parcela do preço' })).toBeVisible();
  await expect(f.locator('.ficha-caminho')).toContainText('Orçamentação');
  await expect(f.locator('.ficha-situacao')).toContainText('Ainda sem ponto de situação');
  // the status, one topic per line
  await f.getByRole('button', { name: 'Escrever' }).click();
  await f.locator('[data-ficha-form="situacao"] textarea').fill('Proposta feita para cada parcela\n- Falta a decisão da mão de obra\nIVA por confirmar');
  await f.getByRole('button', { name: 'Guardar' }).click();
  await expect(f.locator('.ficha-situacao .topicos li')).toHaveText(['Proposta feita para cada parcela', 'Falta a decisão da mão de obra', 'IVA por confirmar']);
  await expect(f.locator('.evento.situacao')).toContainText('Falta a decisão da mão de obra');
  // tag a person: she is notified (personal notification)
  await f.locator('[data-ficha-marcar]').selectOption({ label: 'Colega Teste' });
  await expect(f.locator('.ficha-pessoas .chip.pessoa')).toContainText('Colega Teste');
  const marcado = await db(page, () => window.__fake.db.notificacoes.filter((n) => n.tipo === 'marcado').map((n) => [n.destinatario_id, n.texto]));
  expect(marcado).toEqual([['u-outro', 'Teste Hub marcou-te na tarefa «Definir como se calcula cada parcela do preço»']]);
  // ask for a status: the people following the task are notified
  await f.getByRole('button', { name: 'Pedir ponto de situação' }).click();
  await f.locator('[data-ficha-form="pedido"] textarea').fill('Já há valores?');
  await f.getByRole('button', { name: 'Pedir', exact: true }).click();
  await expect(f.locator('.evento.pedido_situacao')).toContainText('Já há valores?');
  expect(await db(page, () => window.__fake.db.notificacoes.filter((n) => n.tipo === 'pedido_situacao').map((n) => n.destinatario_id))).toEqual(['u-outro']);
  // a message with a file, then a suggestion
  await f.locator('[data-conv-ficheiros="ficheiros"]').setInputFiles({ name: 'parcelas.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4') });
  await f.locator('[data-conv-ficheiros="media"]').setInputFiles({ name: 'quadro.png', mimeType: 'image/png', buffer: PNG });
  await expect(f.locator('#ficha-pendentes li')).toHaveCount(2);
  await f.getByRole('textbox', { name: 'Mensagem' }).fill('Junto o quadro das parcelas');
  await f.getByRole('button', { name: 'Enviar', exact: true }).click();
  const msg = f.locator('.msg.minha').last();
  await expect(msg).toContainText('Junto o quadro das parcelas');
  await expect(msg.locator('.msg-ficheiro')).toContainText('parcelas.pdf');
  await expect(msg.locator('.msg-imagens img')).toHaveAttribute('src', /blob:|icone/);
  const anexos = await db(page, () => window.__fake.db.atividade.filter((a) => a.tipo === 'mensagem').at(-1).anexos.map((a) => a.caminho));
  expect(anexos.every((c) => c.startsWith('tarefa-'))).toBe(true);
  await f.getByRole('button', { name: 'Fazer uma sugestão' }).click();
  await f.getByRole('textbox', { name: 'Mensagem' }).fill('E se a margem for por m²?');
  await f.getByRole('button', { name: 'Enviar', exact: true }).click();
  await expect(f.locator('.msg.sugestao')).toContainText('E se a margem for por m²?');
  // the person marked gets a notification for each message
  expect(await db(page, () => window.__fake.db.notificacoes.filter((n) => n.tipo === 'mensagem' && n.destinatario_id === 'u-outro').length)).toBe(2);
  // an audio message
  await f.getByRole('button', { name: 'Gravar um áudio' }).click();
  await expect(f.getByText('A gravar áudio…')).toBeVisible();
  await page.waitForTimeout(1200);
  await f.getByRole('button', { name: 'Parar e enviar o áudio' }).click();
  await expect(f.locator('.msg.minha .msg-audio audio')).toHaveCount(1);
  // the other person answers: it arrives live
  await db(page, () => window.__fake.comoOutro((x) => x.atividade.insert({ alvo: 'tarefa', ref_id: window.__fake.db.tarefas.find((t) => t.titulo.startsWith('Definir como se calcula')).id, texto: 'Mão de obra: 120 €/m²' })));
  await expect(f.locator('.msg:not(.minha)').last()).toContainText('Mão de obra: 120 €/m²');
  await captura(page, 'equipa-ficha');
  // the project button
  await f.getByRole('link', { name: 'Abrir o projeto' }).click();
  await expect(f).toBeHidden();
  await expect(page).toHaveURL(/#\/projeto\/orcamentacao\/t-\d+$/);
  expect(erros).toEqual([]);
});

test('aprovação: quem só vê deixa a tarefa à espera de aprovação; quem edita aprova ou devolve', async ({ page, browser }) => {
  // a collaborator (view only) asks for approval
  const erros = await abrir(page, { utilizador: { id: 'u-ver', nome: 'Colaborador', nivel: 'ver' }, rota: '/#/projeto/gerador' });
  await page.locator('.passo.em_curso .passo-topo').click();
  await page.locator('.tarefa-titulo', { hasText: 'Rever o documento Cobertura' }).click();
  const f = ficha(page);
  await expect(f.getByRole('button', { name: 'Concluir' })).toHaveCount(0);
  await f.getByRole('button', { name: 'Pedir aprovação' }).click();
  await f.locator('[data-ficha-form="aprovacao"] textarea').fill('Revisto: só falta a cota da cumeeira.');
  await f.getByRole('button', { name: 'Pedir aprovação' }).last().click();
  await expect(f.locator('.ficha-cabeca .estado')).toHaveText('À espera de aprovação');
  await expect(f.locator('.evento.pedido_aprovacao')).toContainText('Revisto: só falta a cota da cumeeira.');
  await expect(f.getByText('À espera da aprovação de quem edita o Design.')).toBeVisible();
  const pedidos = await db(page, () => window.__fake.db.notificacoes.filter((n) => n.tipo === 'pedido_aprovacao').map((n) => n.destinatario_id));
  expect(pedidos).toEqual(['u-outro']);   // the editors (the fake's other person)
  expect(erros).toEqual([]);
});

test('aprovação: quem edita devolve com o que falta e depois aprova', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/gerador' });
  const id = await db(page, () => window.__fake.db.tarefas.find((t) => t.titulo === 'Rever o documento Cobertura').id);
  await db(page, (i) => window.__fake.comoOutro((x) => x.tarefas.update({ estado: 'por_aprovar' }).eq('id', i)), id);
  await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')));
  await page.locator('.passo.em_curso .passo-topo').click();
  await expect(page.locator(`#t-${id}`)).toContainText('À espera de aprovação');
  await page.locator(`#t-${id} .tarefa-titulo`).click();
  const f = ficha(page);
  await f.getByRole('button', { name: 'Devolver' }).click();
  await f.getByRole('button', { name: 'Devolver' }).last().click();   // without a reason: refused
  await expect(f.locator('[data-ficha-form="devolver"] textarea')).toBeVisible();
  await f.locator('[data-ficha-form="devolver"] textarea').fill('Falta a cota da cumeeira.');
  await f.getByRole('button', { name: 'Devolver' }).last().click();
  await expect(f.locator('.evento.devolvida')).toContainText('Falta a cota da cumeeira.');
  await expect(f.locator('.ficha-cabeca .estado')).toHaveText('Em curso');
  await db(page, (i) => window.__fake.comoOutro((x) => x.tarefas.update({ estado: 'por_aprovar' }).eq('id', i)), id);
  await expect(f.getByRole('button', { name: 'Aprovar' })).toBeVisible();
  await f.getByRole('button', { name: 'Aprovar' }).click();
  await expect(f.locator('.ficha-cabeca .estado')).toHaveText('Concluída');
  await expect(f.locator('.evento.aprovada')).toBeVisible();
  expect(await db(page, () => window.__fake.db.notificacoes.filter((n) => n.tipo === 'tarefa_concluida').length)).toBe(1);   // the team is told
  expect(erros).toEqual([]);
});

test('marcado numa tarefa: um pop-up ao abrir o hub leva ao ecrã da tarefa', async ({ page }) => {
  const erros = await abrir(page, { equipa: { marcacoes: [
    { tarefa_id: 72, utilizador_id: 'u-eu', marcado_por: 'u-outro', marcado_por_nome: 'Colega Teste', criada_em: '2026-11-11T10:00:00Z', vista_em: null },
  ] } });
  const t169 = 'Testar primeiro em rede local';   // task 72 of the fixture
  const pop = page.locator('#dlg');
  await expect(pop.getByRole('heading', { name: 'Foste marcado numa tarefa' })).toBeVisible();
  await expect(pop.locator('.pp-linha')).toContainText(t169);
  await expect(pop.locator('.pp-linha')).toContainText('marcado por Colega Teste');
  await pop.locator('.pp-linha').click();
  await expect(ficha(page).getByRole('heading', { name: t169 })).toBeVisible();
  expect(await db(page, () => window.__fake.db.marcacoes[0].vista_em)).not.toBeNull();
  await ficha(page).locator('.ficha-topo').getByRole('button', { name: 'Fechar' }).click();
  await expect(pop).toBeHidden();   // nothing left to see (the fake database starts over on a reload: not tested here)
  expect(erros).toEqual([]);
});

test('marcado numa tarefa, já vista: conta no Início e abre-se pela área pessoal', async ({ page }) => {
  // 2026-11-12: o Dinis foi marcado em 4 tarefas, o Início dizia «0 tarefas tuas» e depois não as voltava a abrir
  const erros = await abrir(page, { equipa: { marcacoes: [
    { tarefa_id: 72, utilizador_id: 'u-eu', marcado_por: 'u-outro', marcado_por_nome: 'Colega Teste', criada_em: '2026-11-11T10:00:00Z', vista_em: '2026-11-11T11:00:00Z' },
  ] } });
  const t72 = 'Testar primeiro em rede local';
  const esperado = await db(page, () => window.__fake.db.tarefas.filter((t) => t.estado !== 'concluida' && (t.responsavel_id === 'u-eu' || t.id === 72)).length);
  const chip = page.locator('.para-ti a[href="#/pessoal"]');
  await expect(chip).toContainText(`${esperado} tarefa`);
  await expect(page.locator('#dlg')).toBeHidden();   // already seen: no pop-up
  await chip.click();
  const linha = page.locator('.cartoes-pessoal .pp-linha', { hasText: t72 });
  await expect(linha).toContainText('marcado por Colega Teste');
  await linha.click();
  await expect(ficha(page).getByRole('heading', { name: t72 })).toBeVisible();
  expect(erros).toEqual([]);
});

test('críticas: deixar uma crítica com imagem, a equipa é avisada, passar a tarefa e resolver', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/gerador' });
  await page.getByRole('button', { name: 'Deixar uma crítica ou comentário' }).click();
  const d = page.locator('#dlg');
  await d.getByRole('button', { name: 'Algo correu mal' }).click();
  await d.getByLabel('O que aconteceu?').fill('Larguei a planta e o PDF da Cobertura saiu em branco.');
  await d.getByLabel(/Onde\?/).fill('Documento Cobertura');
  await d.locator('input[name="critica-ficheiros"]').setInputFiles({ name: 'branco.png', mimeType: 'image/png', buffer: PNG });
  await expect(d.locator('[data-critica-pendentes] li')).toHaveCount(1);
  await d.getByRole('button', { name: 'Enviar' }).click();
  await expect(d).toBeHidden();
  const bloco = page.locator('#criticas');
  await expect(bloco.locator('.critica')).toContainText('o PDF da Cobertura saiu em branco');
  await expect(bloco.locator('.critica-tipo')).toHaveText('Algo correu mal');
  await expect(bloco.locator('.critica .msg-imagens img')).toHaveAttribute('src', /blob:|icone/);
  const n = await db(page, () => window.__fake.db.notificacoes.filter((x) => x.tipo === 'critica_nova').map((x) => [x.destinatario_id, x.texto]));
  expect(n).toEqual([[null, 'Teste Hub deixou uma crítica no Gerador de documentos (Algo correu mal): Larguei a planta e o PDF da Cobertura saiu em branco.']]);
  // the Início shows it needs attention
  await page.goto('/#/');
  await expect(page.locator('.projeto-linha', { hasText: 'Gerador de documentos' }).locator('.chip.atencao')).toContainText('1 precisa de atenção');
  await page.locator('.projeto-linha', { hasText: 'Gerador de documentos' }).click();
  const pop = page.locator('#projeto-pop');
  await expect(pop.locator('#pp-criticas')).toContainText('saiu em branco');
  // becomes a task in the current checkpoint, then resolved
  await pop.getByRole('button', { name: 'Passar a tarefa' }).click();
  await expect(page.locator('.aviso', { hasText: 'Tarefa criada' })).toBeVisible();
  await expect(pop.locator('.critica')).toContainText('Passou a tarefa');
  await pop.getByRole('button', { name: 'Resolvida' }).click();
  await expect(pop.locator('#pp-criticas')).toHaveCount(0);
  expect(await db(page, () => window.__fake.db.criticas[0].estado)).toBe('resolvida');
  expect(erros).toEqual([]);
});

test('Log: ao lado da checklist, com filtro; avisos de lado do que mudou; desligar nas Definições', async ({ page }) => {
  const erros = await abrir(page, { equipa: { registo: [
    { id: 1, projeto: 'orcamentacao', tipo: 'situacao', texto: 'Claude enviou 11 perguntas ao Dinis', detalhe: 'Itens 1 a 11 da tarefa 169.', ator_id: null, ator_nome: 'Claude', ref_tipo: 'tarefa', ref_id: 169, criada_em: '2026-11-10T09:00:00Z' },
  ] } });
  // another person changes things: a notice on the side, from the Log (not a notification)
  await db(page, () => window.__fake.comoOutro((x) => x.tarefas.update({ estado: 'em_curso' }).eq('id', 72)));
  await expect(page.locator('.aviso', { hasText: 'mudou a tarefa «Testar primeiro em rede local»' })).toBeVisible();
  await expect(page.locator('#contador')).toBeHidden();
  // the Log tab, next to the checklist
  await page.getByRole('button', { name: 'Sugestões' }).click();
  const g = page.locator('#gaveta');
  await expect(g.getByRole('tab')).toHaveText(['Sugestões', 'Checklist', 'Log']);
  await g.getByRole('tab', { name: 'Log' }).click();
  await expect(g.locator('.log-linha').first()).toContainText('mudou a tarefa «Testar primeiro em rede local»');
  const claude = g.locator('.log-linha.claude');
  await expect(claude).toContainText('Claude enviou 11 perguntas');
  await claude.locator('summary').click();
  await expect(claude).toContainText('Itens 1 a 11 da tarefa 169.');
  await g.locator('[data-log="projeto"]').selectOption('orcamentacao');
  await expect(g.locator('.log-linha')).toHaveCount(1);
  await captura(page, 'equipa-log');
  await page.keyboard.press('Escape');
  // Definições: switch the Log notices off
  await page.goto('/#/definicoes');
  await page.locator('.definicao', { hasText: 'Avisos do Log' }).getByRole('button', { name: 'Desligados' }).click();
  expect(await db(page, () => window.__fake.db.perfis.find((p) => p.id === 'u-eu').avisos_registo)).toBe(false);
  expect(erros).toEqual([]);
});

test('projeto: cada vez que se abre, os checkpoints e as descrições estão fechados', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/builder' });
  const passo = page.locator('.passo').nth(4);
  await passo.locator('.passo-topo').click();
  await expect(passo.locator('.tarefa').first()).toBeVisible();
  await page.goto('/#/projeto/builder/documentos');
  await page.goto('/#/projeto/builder');
  await expect(page.locator('.passo-topo[aria-expanded="true"]')).toHaveCount(0);
  await expect(page.locator('.tarefa').first()).toBeHidden();
  // a link to a task opens only its checkpoint
  const id = await db(page, () => window.__fake.db.tarefas.find((t) => t.titulo === 'Comparar as quantidades do modelo com as reais').id);
  await page.goto(`/#/projeto/builder/t-${id}`);
  await expect(page.locator(`#t-${id}`)).toBeVisible();
  await expect(page.locator('.passo-topo[aria-expanded="true"]')).toHaveCount(1);
  if (ehTelemovel()) await captura(page, 'equipa-projeto-telemovel');
  expect(erros).toEqual([]);
});

test('Comentar em todas as abas do hub: o botão da barra de cima, já com o projeto da aba', async ({ page }) => {
  const erros = await abrir(page);
  // Início: chooses the project
  await page.getByRole('button', { name: 'Crítica ou comentário sobre um projeto' }).click();
  const d = page.locator('#dlg');
  await d.getByRole('button', { name: 'Não gostei' }).click();
  await d.getByLabel('O que aconteceu?').fill('As cores do preço final confundem.');
  await d.getByRole('button', { name: 'Enviar' }).click();
  await expect(d).toBeVisible();   // without a project the form does not go
  await d.getByLabel('Sobre que projeto?').selectOption('orcamentacao');
  await d.getByRole('button', { name: 'Enviar' }).click();
  await expect(d).toBeHidden();
  expect(await db(page, () => window.__fake.db.criticas.map((c) => [c.projeto, c.tipo]))).toEqual([['orcamentacao', 'nao_gostei']]);
  // on a project tab the project is already chosen
  await page.goto('/#/projeto/builder');
  await page.getByRole('button', { name: 'Crítica ou comentário sobre um projeto' }).click();
  await expect(d.getByLabel('Sobre que projeto?')).toHaveCount(0);
  await expect(d).toContainText('Builder · toda a equipa vê');
  expect(erros).toEqual([]);
});

for (const [rota, nome, projeto] of [['/gerador/', 'Gerador de documentos', 'gerador'], ['/orcamentacao/', 'Orçamentação', 'orcamentacao']]) {
  test(`Comentar dentro da app: ${nome}`, async ({ page }) => {
    const erros = [];
    page.on('pageerror', (e) => erros.push(e.message));
    await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
    await page.goto(rota);
    const botao = page.getByRole('button', { name: `Crítica ou comentário sobre o ${nome}` });
    await expect(botao).toBeVisible();
    await botao.click();
    const d = page.locator('dialog.dc-com-dlg');
    await expect(d.getByRole('heading', { name: 'Crítica ou comentário' })).toBeVisible();
    await expect(d.getByLabel(/Onde\?/)).toHaveValue(new RegExp(`^${nome}`));
    await d.getByRole('button', { name: 'Sugestão' }).click();
    await d.getByLabel('O que aconteceu?').fill('Podia dizer quanto tempo falta.');
    await d.locator('input[name="ficheiros"]').setInputFiles({ name: 'ecra.png', mimeType: 'image/png', buffer: PNG });
    await expect(d.locator('[data-com-lista] li')).toHaveCount(1);
    await d.getByRole('button', { name: 'Enviar' }).click();
    await expect(d.getByRole('heading', { name: 'Obrigado!' })).toBeVisible();
    const c = await db(page, () => window.__fake.db.criticas.map((x) => ({ projeto: x.projeto, tipo: x.tipo, texto: x.texto, anexos: x.anexos.map((a) => a.caminho) })));
    expect(c).toHaveLength(1);
    expect(c[0]).toMatchObject({ projeto, tipo: 'sugestao', texto: 'Podia dizer quanto tempo falta.' });
    expect(c[0].anexos[0]).toMatch(/^critica\/.+__ecra\.png$/);
    expect(await db(page, () => window.__fake.db.notificacoes.filter((n) => n.tipo === 'critica_nova').length)).toBe(1);
    if (projeto === 'gerador') await captura(page, 'comentar-app');
    expect(erros).toEqual([]);
  });
}

test('Comentar no Build Your House: o botão fica acima da barra de vistas', async ({ page }) => {
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await page.goto('/build-your-house/');
  const botao = page.locator('.dc-com-botao');
  await expect(botao).toBeVisible();
  // in the visible part of the screen, above the views bar (the app is wider than a phone: the page corner is off screen)
  const pos = await botao.evaluate((b) => { const r = b.getBoundingClientRect(), v = window.visualViewport;
    return { abaixo: v.offsetTop + v.height - r.bottom, direita: v.offsetLeft + v.width - r.right, esquerda: r.left - v.offsetLeft }; });
  expect(pos.abaixo).toBeGreaterThanOrEqual(64 + 16 - 1);
  expect(pos.direita).toBeGreaterThanOrEqual(15);
  expect(pos.esquerda).toBeGreaterThanOrEqual(0);
});
