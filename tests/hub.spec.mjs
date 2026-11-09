// Testes do hub do Design com Playwright. A base de dados é simulada (fake-supabase.js + fixture.json, o mesmo
// conteúdo da migração 0005): nada toca no Supabase real.
import { test, expect } from '@playwright/test';
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const FIXTURE = readFileSync(new URL('./fixture.json', import.meta.url), 'utf8');
const FIXTURE_SOCIAL = readFileSync(new URL('./fixture_social.json', import.meta.url), 'utf8');
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
mkdirSync(new URL('./capturas/', import.meta.url), { recursive: true });
const captura = (page, nome) => page.screenshot({ path: fileURLToPath(new URL(`./capturas/${nome}-${test.info().project.name}.png`, import.meta.url)), fullPage: true });

async function abrir(page, { utilizador, semSessao = false, rota = '/' } = {}) {
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|Failed to load resource/.test(m.text())) erros.push(m.text()); });
  await page.addInitScript(([fx, fs, u, s]) => { window.__FIXTURE = JSON.parse(fx); window.__FIXTURE_SOCIAL = JSON.parse(fs); if (u) window.__UTILIZADOR = u; if (s) window.__SEM_SESSAO = true; }, [FIXTURE, FIXTURE_SOCIAL, utilizador || null, semSessao]);
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
  const nav = page.getByRole('navigation', { name: 'Secções' });
  await expect(nav.getByRole('link')).toHaveText(['Início', 'Gerador de documentos', 'Builder', 'Orçamentação', 'Build Your House', 'Step Inside', 'Redes sociais']);
  await expect(nav.getByRole('link', { name: 'Início' })).toHaveAttribute('aria-current', 'page');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Teste');
  const linhas = page.locator('.projeto-linha');
  await expect(linhas).toHaveCount(5);
  await expect(linhas.nth(0)).toContainText('Gerador de documentos');
  await expect(linhas.nth(3)).toContainText('Protótipo publicado');
  await expect(linhas.nth(3)).toContainText('3 de 15 checkpoints');
  await expect(linhas.nth(3)).toContainText('Respostas pendentes');
  await expect(linhas.nth(4)).toContainText('Step Inside');
  await expect(linhas.nth(4)).toContainText('0 de 10 checkpoints');
  await expect(page.getByRole('heading', { name: 'Como os projetos se ligam' })).toBeVisible();
  await expect(page.locator('.nota').first()).toContainText('Cada aplicação funciona sozinha');
  await expect(page.locator('.ligacao')).toHaveCount(10);
  await expect(page.locator('#decisoes-abertas .decisao-pill')).toHaveCount(13);
  // agrupadas por projeto, pela ordem das abas
  await expect(page.locator('#decisoes-abertas .decisoes-projeto-nome')).toHaveText([/Builder\s*1/, /Orçamentação\s*1/, /Build Your House\s*5/, /Step Inside\s*6/]);
  await expect(page.locator('.tempo li').first()).toContainText('2026');
  for (const b of ['Sugestões', 'Notificações', 'Perfil']) await expect(page.getByRole('button', { name: b })).toBeVisible();
  await captura(page, 'inicio');
  expect(erros).toEqual([]);
});

test('página do Build Your House: primeiro o estado, depois o botão para a app', async ({ page }) => {
  await abrir(page);
  await page.getByRole('navigation', { name: 'Secções' }).getByRole('link', { name: 'Build Your House' }).click();
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
  await expect(page.locator('.passo').nth(5).locator('.chip.app').first()).toContainText('Sugerido: usar Orçamentação');
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
  await page.getByRole('navigation', { name: 'Secções' }).getByRole('link', { name: 'Orçamentação' }).click();
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
  await pop.getByRole('button', { name: 'Marcar todas como vistas' }).click();
  await expect(page.locator('#contador')).toBeHidden();
  await pop.locator('.notif-abrir').first().click();
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
  await expect(page.locator('.novidade').first()).toContainText('Notificações sem saltos e ponto de situação fechado');
  await expect(page.locator('.novidade').nth(1)).toContainText('Notificações por ver');
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
  for (const rota of ['/#/', '/#/projeto/step-inside', '/#/projeto/builder', '/#/projeto/gerador', '/#/projeto/orcamentacao', '/#/projeto/build-your-house', '/#/pessoal', '/#/definicoes', '/#/novidades', '/#/social', '/#/social/obras']) {
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
  await expect(page.locator('.projeto-linha').nth(2)).toContainText('0 de 4 checkpoints');   // dado novo, sem recarregar a página
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


test('projeto: acrescentar tarefa e checkpoint na posição escolhida; mover um checkpoint', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/gerador' });
  const dlg = page.locator('#dlg');
  // tarefa a partir da página do projeto
  await page.locator('#vista').getByRole('button', { name: 'Tarefa', exact: true }).click();
  await expect(dlg.getByRole('button', { name: 'Tarefa' })).toHaveAttribute('aria-pressed', 'true');
  await expect(dlg.getByLabel('Checkpoint')).toHaveValue(String(15));            // o checkpoint em curso
  await dlg.getByLabel('Título').fill('Pedir a revisão por email');
  await dlg.getByRole('button', { name: 'Acrescentar', exact: true }).click();
  await expect(page.locator('.passo.em_curso .tarefa', { hasText: 'Pedir a revisão por email' })).toBeVisible();
  // checkpoint na posição 2
  await page.locator('#vista').getByRole('button', { name: 'Checkpoint', exact: true }).click();
  await expect(dlg.getByLabel('Posição no workflow')).toHaveValue('6');           // por defeito no fim (5 + 1)
  await dlg.getByLabel('Posição no workflow').selectOption('2');
  await dlg.getByLabel('Título').fill('Ler plantas de dois pisos');
  await dlg.getByRole('button', { name: 'Acrescentar', exact: true }).click();
  await expect(page.locator('.passo').nth(1)).toContainText('Ler plantas de dois pisos');
  await expect(page.locator('.passo').nth(1).locator('.marco')).toHaveText('2');
  await expect(page.locator('.passo').nth(2)).toContainText('Gerador online');      // os outros desceram
  await expect(page.locator('.passo')).toHaveCount(6);
  // mover o último checkpoint para primeiro
  await page.locator('.passo').nth(5).locator('.passo-topo').click();
  await page.locator('.passo').nth(5).getByRole('button', { name: 'Editar checkpoint' }).click();
  await dlg.getByLabel('Posição no workflow').selectOption('1');
  await dlg.getByRole('button', { name: 'Guardar' }).click();
  await expect(page.locator('.passo').nth(0)).toContainText('Mais formatos de entrada');
  const ordens = await db(page, () => window.__fake.db.checkpoints.filter((c) => c.projeto === 'gerador').sort((a, b) => a.ordem - b.ordem).map((c) => c.ordem));
  expect(ordens).toEqual([1, 2, 3, 4, 5, 6]);
});

test('Build Your House: as fases do Smart Land e Interiores na ordem certa, com decisões', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/build-your-house' });
  const titulos = await page.locator('.passo .passo-topo h3').allTextContents();
  expect(titulos.map((t) => t.trim())).toEqual([
    'Motor do configurador', 'Protótipo no browser', 'Publicado no Design', 'Respostas pendentes',
    'Fase 0 · Auditoria para Smart Land, Interiores e Conformidade', 'Preços reais', 'Pronto para clientes',
    'Smart Land · Fase 1 · Terreno mínimo', 'Smart Land · Fase 2 · Importação geográfica alargada', 'Smart Land · Fase 3 · Terreno 3D',
    'Implantação · Fase 4 · Implantação geométrica', 'Conformidade · Fase 5 · Piloto municipal', 'Smart Interiors · Fase 6 · Base',
    'Smart Interiors · Fase 7 · Posicionamento e decoração automática', 'Conformidade · Fase 8 · Expansão municipal e técnica']);
  await expect(page.locator('.bloco-lateral .decisao-pill')).toHaveCount(5);
  await expect(page.locator('#documentos')).toContainText('Especificação Smart Land, Smart Interiors e Conformidade');
});

test('documentos: informativos e adicionais, abrir noutra janela, carregar e apagar', async ({ page, context }) => {
  await abrir(page, { rota: '/#/projeto/step-inside' });
  const sec = page.locator('#documentos');
  await expect(sec.getByRole('heading', { name: /Documentos informativos/ })).toContainText('2');
  await expect(sec.locator('.doc', { hasText: 'Plano técnico, revisão v2 (PDF)' })).toBeVisible();
  const [nova] = await Promise.all([context.waitForEvent('page'), sec.locator('.doc', { hasText: 'Plano técnico' }).getByRole('button', { name: 'Abrir' }).click()]);
  await expect(nova).toHaveURL(/__ficheiro\?c=plataforma_cliente%2Finformativo%2Fplano__discovercasa_plano_tecnico_revisao_v2\.pdf$/);
  await nova.close();
  // carregar um documento adicional
  await sec.getByRole('button', { name: 'Documento' }).click();
  const dlg = page.locator('#dlg');
  await dlg.getByRole('button', { name: 'Adicional' }).click();
  await dlg.getByLabel('Ficheiros').setInputFiles({ name: 'Orçamento GPU.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4 teste') });
  await expect(dlg.locator('[data-escolhidos] li')).toContainText('Orçamento GPU.pdf');
  await dlg.getByLabel(/Título/).fill('Orçamento de GPU');
  await dlg.getByRole('button', { name: 'Carregar' }).click();
  await expect(dlg).toBeHidden();
  const doc = sec.locator('.doc', { hasText: 'Orçamento de GPU' });
  await expect(doc).toContainText('Orçamento GPU.pdf');
  const caminho = await db(page, () => window.__fake.db.documentos.at(-1).caminho);
  expect(caminho).toMatch(/^plataforma_cliente\/adicional\/[a-z0-9]+__orcamento-gpu\.pdf$/);
  page.once('dialog', (d) => d.accept());
  await doc.getByRole('button', { name: /Apagar/ }).click();
  await expect(doc).toHaveCount(0);
  expect(await db(page, (c) => window.__fake.ficheiros.has(c), caminho)).toBe(false);
});

test('Builder: desenhos de Torres Vedras e Sobral agrupados nos adicionais', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/builder' });
  const sec = page.locator('#documentos');
  await expect(sec.getByRole('heading', { name: /Documentos adicionais/ })).toContainText('35');
  await expect(sec.locator('details.doc-grupo summary')).toHaveText([/Torres Vedras\s*15/, /Sobral\s*4/, /Método\s*16/]);
  await sec.locator('summary', { hasText: 'Torres Vedras' }).click();
  await expect(sec.locator('.doc', { hasText: 'projeto de arquitetura geral' }).first()).toBeVisible();
  // pedidos de outros projetos que sugerem usar o Builder
  await expect(page.locator('.bloco-lateral', { hasText: 'Pedidos de outros projetos' })).toContainText('Documentar a pipeline PDF/DWFx');
  await captura(page, 'builder-documentos');
});

test('em direto: o que outra pessoa muda aparece sem recarregar, em todos os sítios', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/builder' });
  // outra pessoa acrescenta uma tarefa ao Build Your House que sugere usar o Builder
  await db(page, () => window.__fake.comoOutro((x) => x.tarefas.insert({ checkpoint_id: 4, titulo: 'Rever o divisor de módulos', app_sugerida: 'builder' })));
  await expect(page.locator('.bloco-lateral', { hasText: 'Pedidos de outros projetos' })).toContainText('Rever o divisor de módulos');   // sem visibilitychange
  await expect(page.locator('.aviso', { hasText: 'Nova tarefa' })).toBeVisible();
  // e no Início também
  await page.getByRole('link', { name: 'Início', exact: true }).click();
  await db(page, () => window.__fake.comoOutro((x) => x.checkpoints.update({ estado: 'concluido' }).eq('id', 4)));
  await expect(page.locator('.projeto-linha').nth(3)).toContainText('4 de 15 checkpoints');
  await expect(page.locator('#contador')).not.toBeHidden();
});

test('versão nova publicada: um aviso deixa recarregar a página', async ({ page }) => {
  // pedido de 2026-11-09 («Sim, avisa»): uma janela aberta há muito mostrava a versão antiga (sem a secção do AR)
  let etag = '"v1"';
  await page.route('**/js/hub/app.js', (r) => (r.request().method() === 'HEAD'
    ? r.fulfill({ status: 200, headers: { etag }, body: '' }) : r.continue()));
  await page.clock.install();
  const primeira = page.waitForRequest((q) => q.method() === 'HEAD' && q.url().endsWith('/js/hub/app.js'));
  const erros = await abrir(page, { rota: '/#/projeto/step-inside' });
  await expect(page.locator('#vista h1')).toBeVisible();
  await primeira;
  const aviso = page.locator('.aviso', { hasText: 'Há uma versão nova do hub' });
  // nada mudou: sem aviso
  await page.clock.fastForward('04:00');
  await page.waitForTimeout(300);
  await expect(aviso).toHaveCount(0);
  // publica-se uma versão nova: aviso que fica até se recarregar ou fechar
  etag = '"v2"';
  await page.clock.fastForward('04:00');
  await expect(aviso).toBeVisible();
  await page.clock.fastForward('00:30');
  await expect(aviso).toBeVisible();
  await Promise.all([page.waitForEvent('load'), aviso.getByRole('button', { name: 'Recarregar' }).click()]);
  await expect(page.locator('#vista h1')).toBeVisible();
  await expect(aviso).toHaveCount(0);
  expect(erros).toEqual([]);
});

test('projeto: o ponto de situação das fases fica fechado num acordeão', async ({ page }) => {
  // pedido de 2026-11-09: «este texto que ocupa demasiado espaço marca-o como aquilo que ele representa num acordion»
  await abrir(page, { rota: '/#/projeto/step-inside' });
  const sit = page.locator('.projeto-cabeca details.situacao');
  await expect(sit.locator('summary')).toHaveText('Ponto de situação das fases');
  await expect(sit).not.toHaveAttribute('open', '');
  await expect(sit.locator('p')).toBeHidden();
  await sit.locator('summary').click();
  await expect(sit.locator('p')).toBeVisible();
  await expect(sit.locator('p')).toContainText('Fase 7');
});

test('Step Inside: teste do AR — carregar modelos e abrir no Quick Look / Scene Viewer', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/step-inside' });
  const sec = page.locator('#teste-ar');
  await expect(sec.getByRole('heading', { name: 'Teste do AR no telemóvel' })).toBeVisible();
  await expect(sec).toContainText('Ainda sem modelos AR');
  for (const [nome, mime] of [['torres-vedras_ar_casa.usdz', 'model/vnd.usdz+zip'], ['torres-vedras_ar_casa.glb', 'model/gltf-binary']]) {
    await sec.getByRole('button', { name: 'Modelo AR' }).click();
    const dlg = page.locator('#dlg');
    await expect(dlg.getByRole('heading', { name: 'Acrescentar modelo AR' })).toBeVisible();
    await dlg.getByLabel('Ficheiros').setInputFiles({ name: nome, mimeType: mime, buffer: Buffer.from('modelo') });
    await dlg.getByLabel(/Título/).fill('Torres Vedras · casa 1:1');
    await dlg.getByRole('button', { name: 'Carregar' }).click();
    await expect(dlg).toBeHidden();
  }
  const docs = await db(page, () => window.__fake.db.documentos.filter((d) => d.tipo === 'ar').map((d) => [d.caminho, d.mime]));
  expect(docs[0][0]).toMatch(/^plataforma_cliente\/ar\/[a-z0-9]+__torres-vedras_ar_casa\.usdz$/);
  expect(docs.map((d) => d[1])).toEqual(['model/vnd.usdz+zip', 'model/gltf-binary']);
  await expect(sec.locator('details.doc-grupo summary')).toHaveText(/Torres Vedras\s*2/);
  // iPhone: <a rel="ar"> with an image as its only child, pointing at the signed file
  const ios = sec.locator('a[rel="ar"]');
  await expect(ios).not.toHaveAttribute('aria-disabled', 'true');
  await expect(ios).toHaveAttribute('href', /\/__ficheiro\?c=plataforma_cliente%2Far%2F.+\.usdz$/);
  expect(await ios.evaluate((a) => a.children.length === 1 && a.firstElementChild.tagName === 'IMG')).toBe(true);
  // Android: Scene Viewer intent with the signed GLB, AR first, coming back to this page
  const android = sec.getByRole('link', { name: /Ver em AR · Android/ });
  await expect(android).toHaveAttribute('href', /^intent:\/\/arvr\.google\.com\/scene-viewer\/1\.0\?file=http.+__ficheiro.+\.glb&mode=ar_preferred.+package=com\.google\.android\.googlequicksearchbox.+;end;$/);
  // without AR (tarefa 85, 2026-11-09): «Ver em 3D» opens the GLB in Google's <model-viewer>, with the USDZ for iPhone
  await page.route('**/@google/model-viewer@*/**', (r) => r.fulfill({ contentType: 'text/javascript',
    body: "customElements.define('model-viewer', class extends HTMLElement {});" }));
  await sec.getByRole('button', { name: 'Ver em 3D' }).click();
  const mv = page.locator('#dlg model-viewer');
  await expect(mv).toHaveAttribute('src', /\/__ficheiro\?c=plataforma_cliente%2Far%2F.+\.glb$/);
  await expect(mv).toHaveAttribute('ios-src', /\.usdz$/);
  await expect(mv).toHaveAttribute('camera-controls', '');
  await expect(page.locator('#dlg')).toContainText('Visualizador 3D para quem não tem AR');
  await page.locator('#dlg').getByRole('button', { name: 'Fechar' }).click();
  await expect(page.locator('#dlg')).toBeHidden();
  // the documents section does not list the AR models
  await expect(page.locator('#documentos')).not.toContainText('torres-vedras_ar_casa');
  await captura(page, 'step-inside-teste-ar');
  await sec.screenshot({ path: `capturas/step-inside-teste-ar-seccao-${test.info().project.name}.png` });
});
