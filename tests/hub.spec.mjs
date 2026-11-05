// Testes do hub do Design com Playwright. A base de dados é simulada (fake-supabase.js + fixture.json, o mesmo
// conteúdo da migração 0005): nada toca no Supabase real.
import { test, expect } from '@playwright/test';
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const FIXTURE = readFileSync(new URL('./fixture.json', import.meta.url), 'utf8');
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
mkdirSync(new URL('./capturas/', import.meta.url), { recursive: true });
const captura = (page, nome) => page.screenshot({ path: fileURLToPath(new URL(`./capturas/${nome}-${test.info().project.name}.png`, import.meta.url)), fullPage: true });

async function abrir(page, { utilizador, semSessao = false, rota = '/' } = {}) {
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|Failed to load resource/.test(m.text())) erros.push(m.text()); });
  await page.addInitScript(([fx, u, s]) => { window.__FIXTURE = JSON.parse(fx); if (u) window.__UTILIZADOR = u; if (s) window.__SEM_SESSAO = true; }, [FIXTURE, utilizador || null, semSessao]);
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await page.goto(rota);
  return erros;
}
const db = (page, expr) => page.evaluate(expr);
const atualizar = (page) => page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')));
const ehTelemovel = () => test.info().project.name === 'telemovel';

test('sem sessão mostra a entrada com a conta do Hub', async ({ page }) => {
  await abrir(page, { semSessao: true });
  await expect(page.getByRole('button', { name: 'Entrar com a conta do Hub' })).toBeVisible();
  await expect(page.locator('#topo')).toBeHidden();
});

test('Início: barra de navegação, projetos, ligações, decisões e feito', async ({ page }) => {
  const erros = await abrir(page);
  const nav = page.getByRole('navigation', { name: 'Projetos' });
  await expect(nav.getByRole('link')).toHaveText(['Início', 'Build Your House', 'Builder', 'Gerador de documentos', 'Orçamentação', 'Step Inside']);
  await expect(nav.getByRole('link', { name: 'Início' })).toHaveAttribute('aria-current', 'page');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Teste');
  const linhas = page.locator('.projeto-linha');
  await expect(linhas).toHaveCount(5);
  await expect(linhas.nth(0)).toContainText('Protótipo publicado');
  await expect(linhas.nth(0)).toContainText('3 de 6 checkpoints');
  await expect(linhas.nth(0)).toContainText('Respostas pendentes');
  await expect(linhas.nth(4)).toContainText('Step Inside');
  await expect(linhas.nth(4)).toContainText('0 de 10 checkpoints');
  await expect(page.getByRole('heading', { name: 'Como os projetos se ligam' })).toBeVisible();
  await expect(page.locator('.nota').first()).toContainText('Cada aplicação funciona sozinha');
  await expect(page.locator('.ligacao')).toHaveCount(10);
  await expect(page.locator('#decisoes-abertas .decisao-pill')).toHaveCount(8);
  await expect(page.locator('.tempo li').first()).toContainText('2026');
  for (const b of ['Sugestões', 'Notificações', 'Perfil']) await expect(page.getByRole('button', { name: b })).toBeVisible();
  await captura(page, 'inicio');
  expect(erros).toEqual([]);
});

test('página do Build Your House: primeiro o estado, depois o botão para a app', async ({ page }) => {
  await abrir(page);
  await page.getByRole('navigation', { name: 'Projetos' }).getByRole('link', { name: 'Build Your House' }).click();
  await expect(page).toHaveURL(/#\/projeto\/build-your-house$/);
  await expect(page.getByRole('heading', { level: 1, name: 'Build Your House' })).toBeVisible();
  const botao = page.getByRole('link', { name: /Abrir o Build Your House/ });
  await expect(botao).toHaveAttribute('href', '/build-your-house/');
  await expect(botao).toHaveAttribute('target', '_blank');   // abre noutra janela/separador
  // o checkpoint em curso abre sozinho e mostra as tarefas, com a decisão e a app sugerida
  const passo = page.locator('.passo.em_curso');
  await expect(passo.locator('.passo-topo')).toHaveAttribute('aria-expanded', 'true');
  await expect(passo.locator('.tarefa')).toHaveCount(4);
  await expect(passo.locator('.decisao-pill')).toHaveCount(2);
  await expect(page.locator('.passo').nth(4).locator('.chip.app').first()).toContainText('Sugerido: usar Orçamentação');
  await expect(page.locator('.organizacao')).toContainText('build-your-house/<tarefa>');
  await captura(page, 'build-your-house');
});

test('Step Inside: novo nome, pipeline com custos e calculadora', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/step-inside' });
  await expect(page.getByRole('heading', { level: 1, name: 'Step Inside' })).toBeVisible();
  await expect(page.getByText('Antes: Plataforma do cliente (VR/AR)')).toBeVisible();
  const etapas = page.locator('.etapa');
  await expect(etapas).toHaveCount(10);
  await expect(etapas.nth(7)).toContainText('0,79 €/h');
  await expect(etapas.nth(5)).toContainText('0,015 USD/GB-mês');
  await expect(etapas.nth(2)).toContainText('Sugerido: usar Builder');
  const r = page.locator('#calc-resultado');
  await expect(r).toContainText('25 h');
  await expect(r).toContainText('19,83');           // 50 sessões × 30 min na RTX 4090 Secure (especificação §20.2)
  await expect(r).toContainText('1,47');            // 10 casas × 12 GB − 10 GB grátis
  await page.getByLabel('Sessões por mês').fill('200');
  await expect(r).toContainText('79,33');           // cenário Moderado
  await page.locator('select[name=tarifa]').selectOption('0.34');
  await expect(r).toContainText('30,30');
  await expect(page.locator('.passo')).toHaveCount(10);
  await captura(page, 'step-inside');
  expect(erros).toEqual([]);
});

test('decisão: todas as opções, escolher, fica registado o que escolhemos em vez das outras', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/step-inside' });
  await page.locator('.bloco-lateral').getByRole('button', { name: 'Decisão' }).nth(3).click();  // GPU cloud
  const dlg = page.locator('#dlg');
  await expect(dlg.getByRole('heading', { name: 'Que GPU cloud para as sessões dos clientes?' })).toBeVisible();
  await expect(dlg.locator('label.opcao')).toHaveCount(3);
  await expect(dlg.locator('label.opcao').first()).toContainText('0,89 USD/h ≈ 0,79 €/h');
  await expect(dlg.locator('label.opcao').first()).toContainText('Disponibilidade');  // vantagens
  await captura(page, 'decisao-aberta');
  await dlg.locator('label.opcao').nth(2).click();
  await dlg.getByLabel(/Porquê/).fill('Primeira prova sem custo por hora.');
  await dlg.getByRole('button', { name: 'Registar decisão' }).click();
  await expect(dlg.locator('.registo')).toContainText('Escolhemos «Workstation local» em vez de «RunPod RTX 4090 Secure Cloud», «RunPod RTX 4090 Community Cloud»');
  await expect(dlg.locator('.registo')).toContainText('Decidido por Teste Hub');
  await expect(dlg.locator('details.outras summary')).toContainText('Ver as outras opções (2)');
  await captura(page, 'decisao-tomada');
  await dlg.getByRole('button', { name: 'Fechar' }).click();
  await expect(page.locator('.decisao-pill.decidida')).toHaveCount(2);   // na tarefa e na lateral
  const n = await db(page, () => window.__fake.db.notificacoes.map((x) => x.texto));
  expect(n.at(-1)).toContain('escolhemos «Workstation local» em vez de');
});

test('checkpoints e tarefas: acrescentar no Início e no projeto, concluir com a data do dia', async ({ page }) => {
  await abrir(page);
  await page.getByRole('button', { name: /Acrescentar checkpoint ou tarefa/ }).click();
  const dlg = page.locator('#dlg');
  await dlg.getByLabel('Projeto').selectOption('orcamentacao');
  await dlg.getByLabel('Título').fill('Comparar dois fornecedores de OSB');
  await dlg.getByRole('button', { name: 'Acrescentar', exact: true }).click();
  await expect(dlg).toBeHidden();
  await page.getByRole('navigation', { name: 'Projetos' }).getByRole('link', { name: 'Orçamentação' }).click();
  const passo = page.locator('.passo', { hasText: 'Comparar dois fornecedores de OSB' });
  await passo.locator('.passo-topo').click();
  await passo.getByLabel('Nova tarefa neste checkpoint').fill('Pedir preço ao fornecedor A');
  await passo.getByRole('button', { name: 'Acrescentar' }).click();
  const tarefa = passo.locator('.tarefa', { hasText: 'Pedir preço ao fornecedor A' });
  await expect(tarefa).toBeVisible();
  await tarefa.getByRole('checkbox').check();
  await expect(tarefa).toHaveClass(/concluida/);
  const hoje = new Date().toLocaleDateString('pt-PT', { day: 'numeric', month: 'short' });
  await expect(tarefa.locator('.estado')).toHaveText(`Concluída a ${hoje}`);
  await expect(page.locator('.aviso').first()).toContainText('Tarefa concluída');
  const tipos = await db(page, () => window.__fake.db.notificacoes.map((x) => x.tipo));
  expect(tipos).toEqual(['checkpoint_novo', 'tarefa_nova', 'tarefa_concluida']);
});

test('nova decisão numa tarefa, com opções, vantagens, desvantagens e custo', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/gerador' });
  const passo = page.locator('.passo.em_curso');
  await passo.locator('.tarefa').first().getByRole('button', { name: 'Editar tarefa' }).click();
  await page.locator('#dlg').getByRole('button', { name: 'Acrescentar decisão' }).click();
  const dlg = page.locator('#dlg');
  await dlg.getByLabel('Pergunta').fill('Revemos a Cobertura em papel ou no ecrã?');
  await dlg.getByLabel('Nome da opção 1').fill('Em papel');
  await dlg.getByLabel('Vantagens da opção 1', { exact: true }).fill('Fácil de anotar');
  await dlg.getByLabel('Custo da opção 1').fill('Impressão A3');
  await dlg.getByLabel('Nome da opção 2').fill('No ecrã');
  await dlg.getByLabel('Desvantagens da opção 2').fill('Menos detalhe');
  await dlg.getByRole('button', { name: 'Criar decisão' }).click();
  await expect(dlg).toBeHidden();
  const pill = passo.locator('.tarefa').first().locator('.decisao-pill');
  await expect(pill).toHaveText('Decisão');
  await pill.click();
  await expect(dlg.locator('label.opcao')).toHaveCount(2);
  await expect(dlg.locator('label.opcao').first()).toContainText('Impressão A3');
});

test('notificações: outra pessoa conclui uma tarefa → aviso, contador e lista', async ({ page }) => {
  await abrir(page);
  await expect(page.locator('#contador')).toBeHidden();
  await db(page, () => window.__fake.comoOutro((x) => x.tarefas.update({ estado: 'concluida' }).eq('id', 72)));
  await atualizar(page);
  await expect(page.locator('#contador')).toHaveText('1');
  await expect(page.locator('.aviso').first()).toContainText('Colega Teste concluiu a tarefa «Testar primeiro em rede local»');
  await page.getByRole('button', { name: /Notificações/ }).click();
  const pop = page.locator('#pop-notificacoes');
  await expect(pop.locator('.notif.nao-lida')).toHaveCount(1);
  await captura(page, 'notificacoes');
  await pop.getByRole('button', { name: 'Marcar como lidas' }).click();
  await expect(page.locator('#contador')).toBeHidden();
  await pop.locator('.notif').first().click();
  await expect(page).toHaveURL(/#\/projeto\/step-inside\/t-72$/);
  await expect(page.locator('#t-72')).toBeVisible();
});

test('pop-up "Novo" na primeira vez que vejo uma tarefa acrescentada por outra pessoa', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/builder' });
  await db(page, () => window.__fake.comoOutro((x) => x.tarefas.insert({ checkpoint_id: 10, titulo: 'Pedir a listagem real por email', projeto: 'builder' })));
  await atualizar(page);
  const aviso = page.locator('.aviso', { hasText: 'Nova tarefa' });
  await expect(aviso).toContainText('«Pedir a listagem real por email» · por Colega Teste');
  await expect(page.locator('.tarefa', { hasText: 'Pedir a listagem real por email' }).locator('.chip.novo')).toBeVisible();
  const vistos = await db(page, () => window.__fake.db.vistos.length);
  expect(vistos).toBe(1);   // não volta a aparecer
  await captura(page, 'novo');
  await atualizar(page);
  await expect(page.locator('.aviso', { hasText: 'Nova tarefa' })).toHaveCount(1);
});

test('sugestões: enviar, comentar, pôr na checklist', async ({ page }) => {
  await abrir(page);
  await page.getByRole('button', { name: 'Sugestões' }).click();
  const g = page.locator('#gaveta');
  await expect(g.locator('.sug')).toHaveCount(1);
  await g.getByLabel('O que mudavas no hub?').fill('Mostrar o progresso de cada projeto em percentagem.');
  await g.getByRole('button', { name: 'Enviar sugestão' }).click();
  await expect(g.locator('.sug')).toHaveCount(2);
  const nova = g.locator('.sug').filter({ hasText: 'percentagem' });
  await nova.getByRole('button', { name: /Comentários/ }).click();
  await nova.getByLabel('Comentário').fill('Boa ideia.');
  await nova.getByRole('button', { name: 'Comentar' }).click();
  await expect(nova.locator('.comentario')).toContainText('Boa ideia.');
  await nova.getByRole('button', { name: 'Pôr na checklist' }).click();
  await g.getByRole('tab', { name: 'Checklist' }).click();
  await expect(g.locator('.check')).toHaveCount(1);
  await captura(page, 'sugestoes');
  await page.keyboard.press('Escape');
  await expect(g).toBeHidden();
});

test('perfil: área pessoal, definições (nome, tema), novidades e sair', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/gerador' });
  // atribuir-me uma tarefa
  await page.locator('.passo.em_curso .tarefa').first().getByRole('button', { name: 'Editar tarefa' }).click();
  await page.locator('#dlg').getByLabel('Responsável').selectOption({ label: 'Teste Hub' });
  await page.locator('#dlg').getByRole('button', { name: 'Guardar' }).click();
  await expect(page.locator('.passo.em_curso .tarefa').first()).toContainText('Teste Hub');
  await page.getByRole('button', { name: 'Perfil' }).click();
  const menu = page.locator('#pop-perfil');
  await expect(menu.getByRole('menuitem')).toHaveText(['Área pessoal', 'Definições', 'Novidades', 'Sair']);
  await menu.getByRole('menuitem', { name: 'Área pessoal' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Área pessoal' })).toBeVisible();
  await expect(page.locator('.cartoes-pessoal')).toContainText('Rever o documento Cobertura');
  await page.goto('/#/definicoes');
  await page.getByLabel('O teu nome').fill('Ana Teste');
  await page.getByRole('button', { name: 'Guardar nome' }).click();
  await expect(page.locator('#avatar')).toHaveText('AT');
  await page.getByRole('button', { name: 'Escuro' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.goto('/#/');
  await captura(page, 'inicio-escuro');
  await page.getByRole('button', { name: 'Perfil' }).click();
  await page.locator('#pop-perfil').getByRole('menuitem', { name: /Novidades/ }).click();
  await expect(page.locator('.novidade').first()).toContainText('Novo hub de projetos');
  await page.getByRole('button', { name: 'Perfil' }).click();
  await page.locator('#pop-perfil').getByRole('menuitem', { name: 'Sair' }).click();
  await expect(page.getByRole('button', { name: 'Entrar com a conta do Hub' })).toBeVisible();
});

test('quem só vê: sem acrescentar nem editar, mas a sua tarefa pode mudar de estado', async ({ page }) => {
  await abrir(page, { utilizador: { id: 'u-ver', nome: 'So Ver', nivel: 'ver' }, rota: '/#/projeto/builder' });
  await expect(page.getByRole('button', { name: /Checkpoint/ })).toHaveCount(0);
  await expect(page.locator('.tarefa input.visto').first()).toBeDisabled();
  await expect(page.getByRole('button', { name: 'Editar tarefa' })).toHaveCount(0);
});

test('sem as tabelas novas: aviso claro e o resto do hub funciona', async ({ page }) => {
  await page.addInitScript(() => { window.__SEM_TABELAS = true; });
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE.replace("const tab = db[this.t];", "const tab = window.__SEM_TABELAS && !['sugestoes','sugestoes_comentarios'].includes(this.t) ? null : db[this.t];") }));
  await page.addInitScript((fx) => { window.__FIXTURE = JSON.parse(fx); }, FIXTURE);
  await page.goto('/');
  await expect(page.locator('.nota').first()).toContainText('migrações 0004 e 0005');
  await expect(page.locator('.projeto-linha')).toHaveCount(5);
  await page.getByRole('button', { name: 'Sugestões' }).click();
  await expect(page.locator('#gaveta .sug')).toHaveCount(1);
});

test('sem deslocamento horizontal e páginas a caber no ecrã', async ({ page }) => {
  await abrir(page);
  for (const rota of ['/#/', '/#/projeto/step-inside', '/#/projeto/builder', '/#/projeto/gerador', '/#/projeto/orcamentacao', '/#/projeto/build-your-house', '/#/pessoal', '/#/definicoes', '/#/novidades']) {
    await page.goto(rota);
    await page.waitForTimeout(150);
    // innerWidth cresce no telemóvel quando algo é largo demais: compara com a largura real do ecrã
    const largo = await page.evaluate(() => Math.max(document.documentElement.scrollWidth, window.innerWidth)) - page.viewportSize().width;
    expect(largo, rota).toBeLessThanOrEqual(0);
  }
  if (ehTelemovel()) { await page.goto('/#/'); await captura(page, 'inicio-telemovel'); }
});

test('logótipo: volta ao Início e atualiza o hub', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/step-inside' });
  await expect(page.locator('.projeto-linha')).toHaveCount(0);
  await db(page, () => window.__fake.comoOutro((x) => x.checkpoints.insert({ projeto: 'orcamentacao', titulo: 'Escolher o software de faturação', ordem: 4 })));
  await page.getByRole('link', { name: /Discovercasa Design/ }).click();
  await expect(page).toHaveURL(/#\/$/);
  await expect(page.locator('.projeto-linha').nth(3)).toContainText('0 de 4 checkpoints');   // dado novo, sem recarregar a página
  await expect(page.locator('.aviso', { hasText: 'Novo checkpoint' })).toContainText('Escolher o software de faturação');
  // já no Início: clicar outra vez também atualiza
  await db(page, () => window.__fake.comoOutro((x) => x.tarefas.update({ estado: 'concluida' }).eq('id', 36)));
  await page.getByRole('link', { name: /Discovercasa Design/ }).click();
  await expect(page.locator('#contador')).toHaveText('2');   // o checkpoint novo e a tarefa concluída
  await expect(page.locator('.tempo li').first()).toContainText('Rever o documento Cobertura');
});

test('Abrir o Gerador: abre noutra janela, com o novo aspeto, e o motor arranca', async ({ page, context }) => {
  test.setTimeout(120000);
  const erros = await abrir(page, { rota: '/#/projeto/gerador' });
  await context.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await context.addInitScript(() => { window.__UTILIZADOR = { id: 'u-eu', nome: 'Teste Hub', nivel: 'editar' }; });
  const [nova] = await Promise.all([context.waitForEvent('page'), page.getByRole('link', { name: /Abrir o Gerador/ }).click()]);
  await nova.waitForLoadState();
  await expect(nova).toHaveURL(/\/gerador\/$/);
  await expect(page).toHaveURL(/#\/projeto\/gerador$/);              // o hub continua aberto na sua janela
  await expect(nova.getByRole('heading', { level: 1, name: 'Gerador de documentos' })).toBeVisible();
  await expect(nova.locator('.g-passos li')).toHaveCount(5);
  await expect(nova.getByRole('button', { name: /Larga aqui o ficheiro/ })).toBeVisible();
  await expect(nova.getByRole('link', { name: /voltar ao hub/ })).toHaveAttribute('href', '/');
  await expect(nova.locator('#estado')).toContainText('Pronto', { timeout: 90000 });   // Pyodide + o motor do BOB
  const largo = await nova.evaluate(() => Math.max(document.documentElement.scrollWidth, window.innerWidth)) - nova.viewportSize().width;
  expect(largo).toBeLessThanOrEqual(0);
  await nova.screenshot({ path: fileURLToPath(new URL(`./capturas/gerador-${test.info().project.name}.png`, import.meta.url)), fullPage: true });
  expect(erros).toEqual([]);
});
