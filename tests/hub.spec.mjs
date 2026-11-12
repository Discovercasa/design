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
  await expect(nav.getByRole('link')).toHaveText(['Início', 'Gerador de documentos', 'Builder', 'Orçamentação', 'Build Your House', 'Step Inside', 'Materiais', 'Redes sociais']);
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
  // sugestão do Geral (2026-11-11): tudo fechado ao abrir; o checkpoint em curso abre com um clique
  const passo = page.locator('.passo.em_curso');
  await expect(page.locator('.passo-topo[aria-expanded="true"]')).toHaveCount(0);
  await expect(passo.locator('.tarefa').first()).toBeHidden();
  await passo.locator('.passo-topo').click();
  await expect(passo.locator('.passo-topo')).toHaveAttribute('aria-expanded', 'true');
  await expect(passo.locator('.tarefa')).toHaveCount(4);
  await expect(passo.locator('.decisao-pill')).toHaveCount(2);
  // a descrição de cada tarefa é um acordeão fechado (utilizador, 2026-11-11)
  const t = passo.locator('.tarefa', { has: page.locator('details.tarefa-desc') }).first();
  await expect(t.locator('.descricao')).toBeHidden();
  await t.locator('details.tarefa-desc summary').click();
  await expect(t.locator('.descricao')).toBeVisible();
  await expect(page.locator('.passo').nth(5).locator('.chip.app').first()).toContainText('Sugerido: usar Orçamentação');
  // «Sobre o projeto» voltou para dentro do Workflow (objetivos, futuro, ligações, organização na coluna ao lado)
  await expect(page.locator('.organizacao')).toContainText('build-your-house/<tarefa>');
  await captura(page, 'build-your-house');
  // abas: Workflow e Documentos (no Step Inside também Teste do AR); voltar a abrir uma aba fecha tudo outra vez
  const abas = page.getByRole('navigation', { name: 'Secções do projeto' });
  await expect(abas.getByRole('link')).toHaveText([/Workflow\s*3\/15/, /Documentos/]);
  await abas.getByRole('link', { name: /Documentos/ }).click();
  await expect(page).toHaveURL(/#\/projeto\/build-your-house\/documentos$/);
  await expect(page.locator('.workflow')).toHaveCount(0);
  await page.goBack();
  await expect(page.locator('.workflow')).toBeVisible();
  await expect(abas.getByRole('link', { name: /Workflow/ })).toHaveAttribute('aria-current', 'page');
  await expect(page.locator('.passo-topo[aria-expanded="true"]')).toHaveCount(0);
});

test('Step Inside: novo nome, pipeline com custos e calculadora', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/step-inside' });
  await expect(page.getByRole('heading', { level: 1, name: 'Step Inside' })).toBeVisible();
  await expect(page.getByText('Antes: Plataforma do cliente (VR/AR)')).toBeVisible();
  await expect(page.locator('.passo')).toHaveCount(10);
  // a pipeline e a calculadora voltaram para baixo do Workflow (utilizador, 2026-11-11)
  await expect(page.getByRole('navigation', { name: 'Secções do projeto' }).getByRole('link')).toHaveText([/Workflow/, /Documentos/, /Teste do AR/]);
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
  // tudo vai para o Log; só a tarefa concluída (impacto) é notificação (utilizador, 2026-11-11)
  expect(await db(page, () => window.__fake.db.registo.map((x) => x.tipo))).toEqual(['checkpoint_novo', 'tarefa_nova', 'tarefa_concluida']);
  expect(await db(page, () => window.__fake.db.notificacoes.map((x) => x.tipo))).toEqual(['tarefa_concluida']);
});

test('nova decisão numa tarefa, com opções, vantagens, desvantagens e custo', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/gerador' });
  const passo = page.locator('.passo.em_curso');
  await passo.locator('.passo-topo').click();
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
  // a notificação abre o ecrã da tarefa (utilizador, 2026-11-11: «quando clicadas levam para a tarefa»)
  await pop.locator('.notif-abrir').first().click();
  await expect(page.locator('#ficha').getByRole('heading', { name: 'Testar primeiro em rede local' })).toBeVisible();
});

test('pop-up "Novo" na primeira vez que vejo uma tarefa acrescentada por outra pessoa', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/builder' });
  await db(page, () => window.__fake.comoOutro((x) => x.tarefas.insert({ checkpoint_id: 10, titulo: 'Pedir a listagem real por email', projeto: 'builder' })));
  await atualizar(page);
  // o aviso de lado vem do Log (2026-11-11)
  const aviso = page.locator('.aviso', { hasText: 'acrescentou a tarefa' });
  await expect(aviso).toContainText('Colega Teste acrescentou a tarefa «Pedir a listagem real por email»');
  await page.locator('#cp-10 .passo-topo').click();
  await expect(page.locator('.tarefa', { hasText: 'Pedir a listagem real por email' }).locator('.chip.novo')).toBeVisible();
  const vistos = await db(page, () => window.__fake.db.vistos.length);
  expect(vistos).toBe(1);   // não volta a aparecer
  await captura(page, 'novo');
  await atualizar(page);
  await expect(page.locator('.aviso', { hasText: 'acrescentou a tarefa' })).toHaveCount(1);
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
  await page.locator('.passo.em_curso .passo-topo').click();
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
  await expect(page.locator('.novidade').first()).toContainText('Tarefas para ti: também as que te marcaram');
  await expect(page.locator('.novidade').nth(1)).toContainText('Documentos: secções e pastas');
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
  await expect(page.locator('.aviso', { hasText: 'acrescentou o checkpoint' })).toContainText('Escolher o software de faturação');
  // já no Início: clicar outra vez também atualiza
  await db(page, () => window.__fake.comoOutro((x) => x.tarefas.update({ estado: 'concluida' }).eq('id', 36)));
  await page.getByRole('link', { name: /Discovercasa Design/ }).click();
  await expect(page.locator('#contador')).toHaveText('1');   // a tarefa concluída (o checkpoint novo só vai para o Log)
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
  await page.goto('/#/projeto/build-your-house/documentos');
  await expect(page.locator('#documentos')).toContainText('Especificação Smart Land, Smart Interiors e Conformidade');
});

test('documentos: informativos e adicionais, abrir noutra janela, carregar e apagar', async ({ page, context }) => {
  await abrir(page, { rota: '/#/projeto/step-inside/documentos' });
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
  await abrir(page, { rota: '/#/projeto/builder/documentos' });
  const sec = page.locator('#documentos');
  await expect(sec.getByRole('heading', { name: /Documentos adicionais/ })).toContainText('35');
  await expect(sec.locator('details.doc-grupo summary')).toHaveText([/Torres Vedras\s*15/, /Sobral\s*4/, /Método\s*16/]);
  await sec.locator('summary', { hasText: 'Torres Vedras' }).click();
  await expect(sec.locator('.doc', { hasText: 'projeto de arquitetura geral' }).first()).toBeVisible();
  await captura(page, 'builder-documentos');
  // pedidos de outros projetos que sugerem usar o Builder (na aba Workflow)
  await page.getByRole('navigation', { name: 'Secções do projeto' }).getByRole('link', { name: /Workflow/ }).click();
  await expect(page.locator('.bloco-lateral', { hasText: 'Pedidos de outros projetos' })).toContainText('Documentar a pipeline PDF/DWFx');
});

test('em direto: o que outra pessoa muda aparece sem recarregar, em todos os sítios', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/builder' });
  // outra pessoa acrescenta uma tarefa ao Build Your House que sugere usar o Builder
  await db(page, () => window.__fake.comoOutro((x) => x.tarefas.insert({ checkpoint_id: 4, titulo: 'Rever o divisor de módulos', app_sugerida: 'builder' })));
  await expect(page.locator('.bloco-lateral', { hasText: 'Pedidos de outros projetos' })).toContainText('Rever o divisor de módulos');   // sem visibilitychange
  await expect(page.locator('.aviso', { hasText: 'acrescentou a tarefa' })).toBeVisible();
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
  // 2026-11-11: «o objetivo de um ponto de situação é ser por tópicos e preciso e claro»
  const sit = page.locator('.projeto-cabeca details.situacao');
  await expect(sit.locator('summary')).toContainText('Ponto de situação');
  await expect(sit).not.toHaveAttribute('open', '');
  await expect(sit.locator('.sit')).toBeHidden();
  await sit.locator('summary').click();
  await expect(sit.locator('.sit-grupo h4')).toHaveText(['Feito', 'Agora', 'Falta ou à espera']);
  await expect(sit.locator('.sit-grupo.feito li', { hasText: 'Fase 7' })).toHaveCount(1);
});

// Materiais vindos do Hub (migração 0016, 2026-11-10): só de consulta, o Hub envia-os nos dias úteis às 6h
const F1 = 'f0000000-0000-4000-8000-000000000001', F2 = 'f0000000-0000-4000-8000-000000000002';
const A1 = 'a0000000-0000-4000-8000-000000000001', A2 = 'a0000000-0000-4000-8000-000000000002', A3 = 'a0000000-0000-4000-8000-000000000003';
const P1 = 'b0000000-0000-4000-8000-000000000001', P2 = 'b0000000-0000-4000-8000-000000000002', P3 = 'b0000000-0000-4000-8000-000000000003';
const MATERIAIS = {
  hub_fornecedores: [{ id: F1, nome: 'Madeiras do Norte', atualizado_em: '2026-11-11T06:01:00Z' }, { id: F2, nome: 'Isolamentos Lda', atualizado_em: '2026-11-11T06:01:00Z' }],
  hub_materiais: [
    { id: A1, nome: 'OSB 3 12 mm', categoria: 'Placas', tipo: 'Painel', atualizado_em: '2026-11-11T06:01:00Z' },
    { id: A2, nome: 'Lã mineral 140 mm', categoria: 'Isolamentos', tipo: 'Rolo', atualizado_em: '2026-11-11T06:02:00Z' },
    { id: A3, nome: 'Pladur N 13 mm', categoria: 'Placas', tipo: 'Painel', atualizado_em: '2026-11-11T06:01:00Z' },
  ],
  hub_material_precos: [
    { id: P1, material_id: A1, fornecedor_id: F1, designacao: 'OSB/3 2500x1250x12', dimensoes: '2500 x 1250 x 12', preco: 20, unidade: 'placa', desconto: 10, iva: 23,
      disponibilidade: 'Em stock', prazo_dias: 3, data_atualizacao: '2026-11-11', transporte: 'Camião', transporte_incluido: 'Não', atualizado_em: '2026-11-11T06:01:00Z' },
    { id: P2, material_id: A1, fornecedor_id: F2, designacao: 'OSB 12', preco: 19.5, unidade: 'placa', desconto: 0, iva: 0.23, data_atualizacao: '2026-11-10', atualizado_em: '2026-11-11T06:01:00Z' },
    { id: P3, material_id: A2, fornecedor_id: F2, designacao: 'Rolo 140', preco: 4.2, unidade: 'm²', desconto: 0.05, iva: 23, data_atualizacao: '2026-11-11', atualizado_em: '2026-11-11T06:01:00Z' },
  ],
  hub_material_precos_historico: [
    { id: 'c0000000-0000-4000-8000-000000000001', preco_id: P1, preco: 16, data_atualizacao: '2026-10-01', registado_em: '2026-10-01T06:00:00Z' },
    { id: 'c0000000-0000-4000-8000-000000000002', preco_id: P1, preco: 20, data_atualizacao: '2026-11-11', registado_em: '2026-11-11T06:00:00Z' },
  ],
};

test('Materiais: aba só de consulta — preço por fornecedor, histórico, filtros, CSV e o bloco dos projetos', async ({ page }) => {
  await page.addInitScript((m) => { window.__FIXTURE_MATERIAIS = m; }, MATERIAIS);
  const erros = await abrir(page, { rota: '/#/materiais' });
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Materiais e preços');
  await expect(page.locator('.cabeca-pagina')).toContainText('3 materiais');
  await expect(page.locator('.cabeca-pagina')).toContainText('2 fornecedores');
  await expect(page.locator('.mat-cat')).toHaveText([/Isolamentos\s*1/, /Placas\s*2/]);
  // the cheapest price with the discount (20 € − 10 % = 18 €) and its last change (16 → 20: +25 %)
  const osb = page.locator(`#m-${A1}`);
  await expect(osb.locator('summary')).toContainText('desde 18,00 €');
  await expect(osb.locator('summary')).toContainText('Madeiras do Norte');
  await expect(osb.locator('summary .mat-var')).toContainText('+25 %');
  await expect(page.locator(`#m-${A3} summary`)).toContainText('sem preço');
  await osb.locator('summary').click();
  const linhas = osb.locator('tbody tr');
  await expect(linhas).toHaveCount(2);
  for (const t of ['Madeiras do Norte', '20,00 €', '10 %', '18,00 €', '23 %', '3 dias', 'Em stock']) await expect(linhas.first()).toContainText(t);
  await expect(linhas.nth(1)).toContainText('19,50 €');   // IVA 0,23 read as 23 %
  await expect(linhas.nth(1)).toContainText('23 %');
  await expect(linhas.first().locator('svg.spark')).toHaveCount(1);
  await captura(page, 'materiais');
  // search and filters (the box keeps its focus)
  await page.getByPlaceholder(/Procurar/).fill('la mineral');
  await expect(page.locator('.mat')).toHaveCount(1);
  await expect(page.getByPlaceholder(/Procurar/)).toBeFocused();
  await page.getByPlaceholder(/Procurar/).fill('');
  await page.getByLabel('Fornecedor').selectOption({ label: 'Isolamentos Lda' });
  await expect(page.locator('.mat')).toHaveCount(2);
  await page.getByLabel('Fornecedor').selectOption('');
  // CSV for Excel and BOB's tools: one line per price, ; and decimal comma
  const [dl] = await Promise.all([page.waitForEvent('download'), page.getByRole('button', { name: 'Descarregar CSV' }).click()]);
  expect(dl.suggestedFilename()).toMatch(/^materiais-hub-\d{4}-\d{2}-\d{2}\.csv$/);
  const csv = readFileSync(await dl.path(), 'utf8');
  expect(csv.startsWith('﻿Material;Categoria;Tipo;Fornecedor')).toBe(true);
  expect(csv).toContain('OSB 3 12 mm;Placas;Painel;Madeiras do Norte;OSB/3 2500x1250x12;2500 x 1250 x 12;20;placa;10;18;23');
  expect(csv.trim().split('\r\n')).toHaveLength(1 + 3 + 1);   // header, 3 prices, Pladur without a price
  // a deep link opens the material
  await page.goto(`/#/materiais/m-${A2}`);
  await expect(page.locator(`#m-${A2} details`)).toHaveAttribute('open', '');
  // the projects that use the list say what for and link to it
  await page.goto('/#/projeto/orcamentacao/sobre');
  const bloco = page.locator('.bloco-materiais');
  await expect(bloco).toContainText('Materiais do Hub');
  await expect(bloco).toContainText('3 materiais · 2 fornecedores');
  await expect(bloco.getByRole('link', { name: 'Materiais e preços' })).toHaveAttribute('href', '#/materiais');
  await page.goto('/#/projeto/builder/sobre');
  await expect(page.locator('.organizacao')).toBeVisible();
  await expect(page.locator('.bloco-materiais')).toHaveCount(0);
  expect(erros).toEqual([]);
});

test('Materiais: ainda sem dados do Hub — diz quando chegam', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/materiais' });
  await expect(page.locator('.vazio')).toContainText('Ainda sem materiais. O Hub envia a lista nos dias úteis às 6h');
  await expect(page.getByRole('button', { name: 'Descarregar CSV' })).toHaveCount(0);
  expect(erros).toEqual([]);
});

test('Step Inside: o Scene Viewer não abriu no Android — o hub diz porquê e oferece o 3D', async ({ page }) => {
  // the intent's fallback brings the phone back with ?ar-android=<doc> (team note 2026-11-10: «nem sequer apareceu»)
  const erros = await abrir(page, { rota: '/?ar-android=999#/projeto/step-inside' });
  const av = page.locator('.aviso, [role="status"], [role="alert"]').filter({ hasText: 'O AR não abriu neste telemóvel' });
  await expect(av).toBeVisible();
  await expect(av.getByRole('button', { name: 'Ver na Play Store' })).toBeVisible();
  await expect(page).not.toHaveURL(/ar-android/);
  await expect(page).toHaveURL(/#\/projeto\/step-inside$/);
  expect(erros).toEqual([]);
});

test('Step Inside: teste do AR — carregar modelos e abrir no Quick Look / Scene Viewer', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/step-inside/teste-ar' });
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
  // a 1:1 model keeps its real size (team note 2026-11-10): no pinch-to-scale in Quick Look
  await expect(ios).toHaveAttribute('href', /\/__ficheiro\?c=plataforma_cliente%2Far%2F.+\.usdz#allowsContentScaling=0$/);
  expect(await ios.evaluate((a) => a.children.length === 1 && a.firstElementChild.tagName === 'IMG')).toBe(true);
  // Android (2026-11-11): a button that opens the viewer and goes into Chrome's AR (Scene Viewer is broken in the Google
  // app since October 2026: it closes ~90 ms after launch, the team's Pixel 6 and Xiaomi too)
  const android = sec.getByRole('button', { name: /Ver em AR · Android/ });
  // on an Android, the page says whether this phone has AR (ARCore); the test browser has none
  if (ehTelemovel()) await expect(sec.locator('#ar-este-telemovel')).toContainText('não tem AR (ARCore)');
  else await expect(sec.locator('#ar-este-telemovel')).toBeHidden();
  // without AR (tarefa 85, 2026-11-09): «Ver em 3D» opens the GLB in Google's <model-viewer>, with the USDZ for iPhone
  await page.route('**/@google/model-viewer@*/**', (r) => r.fulfill({ contentType: 'text/javascript',
    body: "customElements.define('model-viewer', class extends HTMLElement {});" }));
  await sec.getByRole('button', { name: 'Ver em 3D', exact: true }).click();
  const mv = page.locator('#dlg model-viewer');
  await expect(mv).toHaveAttribute('src', /\/__ficheiro\?c=plataforma_cliente%2Far%2F.+\.glb$/);
  await expect(mv).toHaveAttribute('ios-src', /\.usdz$/);
  await expect(mv).toHaveAttribute('camera-controls', '');
  await expect(mv).toHaveAttribute('ar-scale', 'fixed');
  await expect(mv.locator('[slot="ar-button"]')).toHaveText('Ver no teu espaço (AR)');
  await expect(page.locator('#dlg')).toContainText('Visualizador 3D para quem não tem AR');
  // team note 2026-11-10: turning the model and letting go outside the dialog closed it and the page behind took the drag
  await expect(mv).toHaveAttribute('touch-action', 'none');
  const caixa = await mv.boundingBox();
  await page.mouse.move(caixa.x + caixa.width / 2, caixa.y + caixa.height / 2);
  await page.mouse.down();
  await page.mouse.move(4, caixa.y + caixa.height / 2, { steps: 5 });
  await page.mouse.up();
  await expect(page.locator('#dlg')).toBeVisible();
  await page.mouse.click(4, 4);   // a real click outside still closes it
  await expect(page.locator('#dlg')).toBeHidden();
  await sec.getByRole('button', { name: 'Ver em 3D', exact: true }).click();
  await expect(page.locator('#dlg model-viewer')).toBeVisible();
  await page.locator('#dlg').getByRole('button', { name: 'Fechar' }).click();
  await expect(page.locator('#dlg')).toBeHidden();
  // iPhone / iPad (2026-11-11: «no dispositivos IOS também seja possível ver em 3D tal como nos androids»): the USDZ row
  // has «Ver em 3D» too — the same viewer with the twin GLB, and the USDZ for the AR button (Quick Look)
  const linhaIos = sec.locator('.doc', { hasText: 'torres-vedras_ar_casa.usdz' });
  await linhaIos.getByRole('button', { name: /Ver em 3D/ }).click();
  await expect(page.locator('#dlg model-viewer')).toHaveAttribute('src', /\.glb$/);
  await expect(page.locator('#dlg model-viewer')).toHaveAttribute('ios-src', /\.usdz$/);
  await expect(page.locator('#dlg model-viewer')).toHaveAttribute('ar-modes', /quick-look/);
  await page.locator('#dlg').getByRole('button', { name: 'Fechar' }).click();
  await expect(page.locator('#dlg')).toBeHidden();
  // «Ver em AR · Android»: the viewer opens with Chrome's AR only (WebXR; iPhone's Quick Look stays) …
  await android.click();
  const mvAR = page.locator('#dlg model-viewer');
  await expect(mvAR).toHaveAttribute('ar-modes', 'webxr quick-look');
  await expect(mvAR).toHaveAttribute('ar-scale', 'fixed');
  // … and goes straight into AR while the tap still counts
  await mvAR.evaluate((m) => { m.canActivateAR = true; m.activateAR = () => { window.__arAtivado = true; return Promise.resolve(); }; m.dispatchEvent(new Event('load')); });
  await expect.poll(() => page.evaluate(() => window.__arAtivado === true)).toBe(true);
  await page.locator('#dlg').getByRole('button', { name: 'Fechar' }).click();
  // a phone without ARCore (a Redmi Note 14 Pro 5G, not on Google's list, 2026-11-10): the model stays in 3D, with the
  // notice and the Play Store link (user: «se o cliente tiver um dispositivo qualquer tem de conseguir ver»)
  await android.click();
  await page.locator('#dlg model-viewer').evaluate((m) => { m.canActivateAR = false; m.dispatchEvent(new Event('load')); });
  const semAR = page.locator('.aviso').filter({ hasText: 'O AR não abriu neste telemóvel' });
  await expect(semAR).toBeVisible({ timeout: 5000 });
  await expect(semAR.getByRole('button', { name: 'Ver na Play Store' })).toBeVisible();
  await expect(page.locator('#dlg model-viewer')).toBeVisible();
  await page.locator('#dlg').getByRole('button', { name: 'Fechar' }).click();
  // Android (team note 10, 2026-11-10): the panel opens the AR test page (outside the hub) with our signed GLB in the hash
  const teste = sec.locator('#diag-ar').getByRole('link', { name: 'Abrir a página de teste do AR' });
  await expect(teste).toHaveAttribute('href', /^\/ar-teste\.html#u=http.+__ficheiro.+\.glb&t=Torres\+Vedras.+&doc=\d+&real=1$/);
  await captura(page, 'step-inside-teste-ar');
  await sec.screenshot({ path: `capturas/step-inside-teste-ar-seccao-${test.info().project.name}.png` });
  // the documents tab does not list the AR models
  await page.getByRole('navigation', { name: 'Secções do projeto' }).getByRole('link', { name: /Documentos/ }).click();
  await expect(page.locator('#documentos')).toBeVisible();
  await expect(page.locator('#documentos')).not.toContainText('torres-vedras_ar_casa');
});
