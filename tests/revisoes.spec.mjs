// Testes das mudanças de 2026-11-06: imagens nas tarefas e checkpoints, notas de teste/revisão, opção nova numa decisão,
// critério de saída e a fase atual de uma obra com um clique (base simulada: fake-supabase.js + fixtures).
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { deflateSync } from 'node:zlib';

const FIXTURE = readFileSync(new URL('./fixture.json', import.meta.url), 'utf8');
const FIXTURE_SOCIAL = readFileSync(new URL('./fixture_social.json', import.meta.url), 'utf8');
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
// PNG de 2×2 feito aqui (assinatura, IHDR, IDAT, IEND com CRC)
const CRC = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
const crc32 = (b) => { let c = 0xffffffff; for (const x of b) c = CRC[(c ^ x) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
const bloco = (tipo, dados) => { const t = Buffer.concat([Buffer.from(tipo), dados]); const n = Buffer.alloc(4); n.writeUInt32BE(dados.length); const c = Buffer.alloc(4); c.writeUInt32BE(crc32(t)); return Buffer.concat([n, t, c]); };
const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(2, 0); ihdr.writeUInt32BE(2, 4); ihdr[8] = 8; ihdr[9] = 2;
const PNG = Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), bloco('IHDR', ihdr),
  bloco('IDAT', deflateSync(Buffer.from([0, 0, 0, 255, 0, 0, 255, 0, 255, 0, 0, 255, 0, 0]))), bloco('IEND', Buffer.alloc(0))]);
const imagem = (nome) => ({ name: nome, mimeType: 'image/png', buffer: PNG });

async function abrir(page, { utilizador, rota = '/' } = {}) {
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
// sugestão do Geral (2026-11-11): checkpoints e tarefas começam fechados
const abrirPasso = async (passo) => { const b = passo.locator('.passo-topo'); if ((await b.getAttribute('aria-expanded')) !== 'true') await b.click(); };
const abrirTarefa = async (page, tarefa) => {
  await abrirPasso(page.locator('.passo', { has: tarefa }));
  const b = tarefa.locator('.tarefa-topo');
  if ((await b.count()) && (await b.getAttribute('aria-expanded')) !== 'true') await b.click();
};
const VER = { id: 'u-ver', nome: 'So Ver', nivel: 'ver' };

test('imagens: juntar a uma tarefa, ver em grande com setas, tirar; critério de saída e imagens no checkpoint', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/builder' });
  const dlg = page.locator('#dlg');
  const tarefa = page.locator('.tarefa', { hasText: 'Comparar as quantidades do modelo com as reais' });
  await abrirPasso(page.locator('.passo', { has: tarefa }));
  await tarefa.getByRole('button', { name: 'Editar tarefa' }).click();
  await dlg.locator('input[name="anexos-ficheiros"]').setInputFiles([imagem('quantidades-1.png'), imagem('quantidades-2.png')]);
  await expect(dlg.locator('.anexos-lista li')).toHaveCount(2);
  await expect(page.locator('.aviso', { hasText: '2 imagens guardadas' })).toBeVisible();
  await expect(dlg.locator('.anexos-lista img').first()).toHaveAttribute('src', /.+/);
  await dlg.getByRole('button', { name: 'Cancelar' }).click();
  // no workflow: a tarefa fechada diz quantas imagens tem; aberta, as miniaturas; clicar abre o visor
  await expect(tarefa.locator('.meta')).toContainText('2');
  await abrirTarefa(page, tarefa);
  await expect(tarefa.locator('.galeria-img')).toHaveCount(2);
  await tarefa.locator('.galeria-img').first().click();
  const visor = page.locator('dialog.visor');
  await expect(visor).toBeVisible();
  await expect(visor.locator('.visor-legenda')).toHaveText('quantidades-1.png · 1 de 2');
  await expect(visor.locator('.visor-img img')).toHaveAttribute('src', /.+/);
  await page.keyboard.press('ArrowRight');
  await expect(visor.locator('.visor-legenda')).toHaveText('quantidades-2.png · 2 de 2');
  await page.keyboard.press('Escape');
  await expect(visor).toBeHidden();
  // tirar uma
  await tarefa.getByRole('button', { name: 'Editar tarefa' }).click();
  await dlg.getByRole('button', { name: 'Tirar quantidades-1.png' }).click();
  await expect(dlg.locator('.anexos-lista li')).toHaveCount(1);
  expect(await db(page, () => window.__fake.db.anexos.map((a) => a.nome_ficheiro))).toEqual(['quantidades-2.png']);
  await dlg.getByRole('button', { name: 'Cancelar' }).click();
  // checkpoint: critério de saída (vem da migração) e uma imagem nova
  const cp = page.locator('.passo', { hasText: 'Validação com os materiais reais' });
  await abrirPasso(cp);
  await expect(cp.locator('.criterio')).toContainText('Tolerância de erro definida por família de material');
  await cp.getByRole('button', { name: 'Editar checkpoint' }).click();
  await expect(dlg.locator('textarea[name="criterio_saida"]')).toHaveValue(/Tolerância de erro/);
  await dlg.locator('textarea[name="criterio_saida"]').fill('Diferenças abaixo de 5 % em todas as madeiras.');
  await dlg.locator('input[name="anexos-ficheiros"]').setInputFiles([imagem('comparacao.png')]);
  await expect(dlg.locator('.anexos-lista li')).toHaveCount(1);
  await dlg.getByRole('button', { name: 'Guardar' }).click();
  await expect(cp.locator('.criterio')).toContainText('Diferenças abaixo de 5 %');
  await expect(cp.locator('.passo-detalhe > .galeria .galeria-img')).toHaveCount(1);
  // o checkpoint novo do documento de hierarquia, antes da validação
  const titulos = (await page.locator('.passo .passo-topo h3').allTextContents()).map((t) => t.trim());
  expect(titulos.slice(3, 5)).toEqual(['Corrigir defeitos geométricos conhecidos', 'Validação com os materiais reais']);
  expect(erros).toEqual([]);
});

test('notas de teste: a lista do teste do configurador, nota nova com imagem, resolver e passar a tarefa', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/build-your-house' });
  const tarefa = page.locator('.tarefa', { hasText: 'Teste completo do configurador pela equipa, com comentários' });
  await expect(tarefa.locator('.meta')).toContainText('2 notas por resolver');   // fechada: o resumo na linha
  await abrirTarefa(page, tarefa);
  await expect(tarefa.locator('.descricao')).toHaveText('Cada problema encontrado no teste fica na lista de notas: bug, a mudar ou a fazer.');
  const resumo = tarefa.locator('.notas-resumo');
  await expect(resumo).toContainText('2 por resolver · 2 bugs · 2 no total');
  await resumo.click();
  const notas = tarefa.locator('.notas-lista .nota');
  await expect(notas).toHaveCount(2);
  await expect(notas.first()).toContainText('Bug');
  await expect(notas.first()).toContainText('a parte interior da platibanda');
  // nota nova: "A mudar", com uma imagem escolhida antes de a escrever
  const f = tarefa.locator('form[data-form="nota"]');
  await f.getByRole('button', { name: 'A mudar' }).click();
  await f.locator('textarea[name="texto"]').fill('O botão de guardar devia estar sempre visível no telemóvel.');
  await f.locator('input[name="imagens-nota"]').setInputFiles([imagem('telemovel.png')]);
  await expect(f.locator('.escolhidas li')).toHaveText(['telemovel.png']);
  await f.getByRole('button', { name: 'Acrescentar nota' }).click();
  await expect(notas).toHaveCount(3);
  const nova = notas.filter({ hasText: 'O botão de guardar' });
  await expect(nova.locator('.nota-tipo')).toHaveText('A mudar');
  await expect(nova.locator('.galeria-img')).toHaveCount(1);
  expect(await db(page, () => window.__fake.db.anexos.filter((a) => a.alvo === 'nota').length)).toBe(1);
  // resolver o primeiro bug
  await notas.filter({ hasText: 'a parte interior da platibanda' }).locator('input.visto').click();
  await expect(resumo).toContainText('2 por resolver · 1 bug · 3 no total');
  const resolvida = await db(page, () => window.__fake.db.tarefas_notas.find((n) => n.id === 1));
  expect([resolvida.resolvida, resolvida.resolvida_por_nome]).toEqual([true, 'Teste Hub']);
  await expect(tarefa.locator('.nota.resolvida')).toHaveCount(1);
  // passar o outro bug a tarefa: aparece no mesmo checkpoint
  await notas.filter({ hasText: 'testeiras dos triângulos' }).getByRole('button', { name: 'Passar a tarefa' }).click();
  await expect(page.locator('.aviso', { hasText: 'Tarefa criada' })).toBeVisible();
  const cp = page.locator('.passo', { hasText: 'Respostas pendentes' });
  await expect(cp.locator('.tarefa .titulo', { hasText: 'Outro Bug é relativo as coberturas' })).toBeVisible();
  await expect(notas.filter({ hasText: 'testeiras dos triângulos' })).toContainText('passou a tarefa');
  expect(erros).toEqual([]);
});

test('tarefa de teste ou revisão: ligar a marca no editar faz aparecer a lista', async ({ page }) => {
  await abrir(page, { rota: '/#/projeto/gerador' });
  const tarefa = page.locator('.tarefa', { hasText: 'Ler DXF' });
  await page.locator('.passo', { hasText: 'Mais formatos de entrada' }).locator('.passo-topo').click();
  await expect(tarefa.locator('.notas-rev')).toHaveCount(0);
  await tarefa.getByRole('button', { name: 'Editar tarefa' }).click();
  await page.locator('#dlg label.aprovar', { hasText: 'Tarefa de teste ou revisão' }).locator('input').check();
  await page.locator('#dlg').getByRole('button', { name: 'Guardar' }).click();
  await abrirTarefa(page, tarefa);
  await expect(tarefa.locator('.notas-resumo')).toContainText('Ainda sem notas');
  // as tarefas de revisão do Gerador já vêm marcadas
  const cobertura = page.locator('.tarefa', { hasText: 'Rever o documento Cobertura' });
  await abrirTarefa(page, cobertura);
  await expect(cobertura.locator('.notas-resumo')).toBeVisible();
});

test('decisão: acrescentar uma opção que não estava na lista e escolhê-la', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/projeto/step-inside' });
  await page.locator('.bloco-lateral').getByRole('button', { name: 'Decisão' }).nth(3).click();  // GPU cloud
  const dlg = page.locator('#dlg');
  await expect(dlg.locator('label.opcao')).toHaveCount(3);
  await dlg.getByRole('button', { name: 'Outra opção' }).click();
  await dlg.getByLabel('Opção', { exact: true }).fill('Vast.ai RTX 4090');
  await dlg.getByLabel('Vantagens', { exact: true }).fill('Preço por hora baixo.');
  await dlg.getByLabel('Desvantagens', { exact: true }).fill('Hosts variáveis.');
  await dlg.locator('input[name="n_custo"]').fill('≈ 0,40 USD/h');
  await dlg.getByRole('button', { name: 'Acrescentar opção' }).click();
  await expect(dlg.locator('label.opcao')).toHaveCount(4);
  await expect(dlg.locator('label.opcao').nth(3)).toContainText('Vast.ai RTX 4090');
  await expect(dlg.locator('label.opcao').nth(3).locator('input')).toBeChecked();
  expect(await db(page, () => window.__fake.db.notificacoes.filter((n) => n.tipo === 'decisao_opcao').length)).toBe(1);
  await dlg.getByRole('button', { name: 'Registar decisão' }).click();
  await expect(dlg.locator('.registo')).toContainText('Escolhemos «Vast.ai RTX 4090» em vez de');
  expect(erros).toEqual([]);
});

test('obras: clicar no círculo marca a fase atual, desfaz e recua; uma só notificação por clique', async ({ page }) => {
  const erros = await abrir(page, { rota: '/#/social/obras' });
  const mat = () => page.locator('.obra', { hasText: 'Matosinhos' });
  const fase = (nome) => mat().locator('.fase-linha', { has: page.getByRole('button', { name: nome, exact: true }) });
  await mat().getByRole('button', { name: 'A obra está em «Estrutura»' }).click();
  await expect(fase('Estrutura')).toHaveClass(/em_curso/);
  await expect(mat()).toContainText('Agora: Estrutura');
  await expect(page.locator('.visita', { hasText: 'Matosinhos' })).toContainText('Estrutura');
  const notifs = () => db(page, () => window.__fake.db.notificacoes.filter((n) => n.tipo === 'fase_estado').map((n) => n.texto));
  expect(await notifs()).toEqual(['Teste Hub passou a obra Matosinhos para a fase «Estrutura»']);
  // desfazer
  await page.locator('.aviso', { hasText: 'Matosinhos está agora em' }).getByRole('button', { name: 'Desfazer' }).click();
  await expect(fase('Estrutura')).toHaveClass(/prevista/);
  await expect(page.locator('.visita', { hasText: 'Matosinhos' })).toHaveCount(0);
  // de novo para a Estrutura e depois recuar para a Base de fundação
  await mat().getByRole('button', { name: 'A obra está em «Estrutura»' }).click();
  await expect(fase('Estrutura')).toHaveClass(/em_curso/);
  await mat().getByRole('button', { name: 'A obra está em «Base de fundação»' }).click();
  await expect(fase('Base de fundação')).toHaveClass(/em_curso/);
  await expect(fase('Estrutura')).toHaveClass(/prevista/);
  await expect(fase('Movimento de terras')).toHaveClass(/concluida/);
  // clicar na fase em curso dá-a como concluída (com confirmação)
  await mat().getByRole('button', { name: 'Dar «Base de fundação» como concluída' }).click();
  await expect(fase('Base de fundação')).toHaveClass(/concluida/);
  const fs = await db(page, () => window.__fake.db.obras_fases.filter((f) => f.obra_id === 1).map((f) => [f.nome, f.estado, f.nome === 'Movimento de terras' ? 'igual' : !!f.concluida_em]));
  expect(fs).toEqual([['Movimento de terras', 'concluida', 'igual'], ['Base de fundação', 'concluida', true], ['Estrutura', 'prevista', false], ['Acabamentos', 'prevista', false]]);
  expect((await notifs()).length).toBe(5);   // uma por clique (5 cliques, contando o desfazer)
  expect(erros).toEqual([]);
});

test('quem só vê: escreve notas, mas não junta imagens às tarefas nem muda a fase das obras', async ({ page }) => {
  await abrir(page, { utilizador: VER, rota: '/#/projeto/build-your-house' });
  const tarefa = page.locator('.tarefa', { hasText: 'Teste completo do configurador' });
  await abrirTarefa(page, tarefa);
  await tarefa.locator('.notas-resumo').click();
  await expect(tarefa.getByRole('button', { name: 'Passar a tarefa' })).toHaveCount(0);
  await expect(tarefa.getByRole('button', { name: 'Editar tarefa' })).toHaveCount(0);
  const f = tarefa.locator('form[data-form="nota"]');
  await f.locator('textarea[name="texto"]').fill('No iPad a cobertura demora a aparecer.');
  await f.getByRole('button', { name: 'Acrescentar nota' }).click();
  await expect(tarefa.locator('.notas-lista .nota')).toHaveCount(3);
  // a sua nota pode apagá-la; as dos outros não
  await expect(tarefa.locator('.nota', { hasText: 'No iPad' }).getByRole('button', { name: 'Apagar nota' })).toHaveCount(1);
  await expect(tarefa.locator('.nota').first().getByRole('button', { name: 'Apagar nota' })).toHaveCount(0);
  await page.goto('/#/social/obras');
  await expect(page.locator('.obra').first().locator('button.marco')).toHaveCount(0);
});

test('Início: decisões em aberto agrupadas por projeto; abas pela ordem nova', async ({ page }) => {
  await abrir(page, { rota: '/#/' });
  await expect(page.getByRole('navigation', { name: 'Secções' }).getByRole('link'))
    .toHaveText(['Início', 'Gerador de documentos', 'Builder', 'Orçamentação', 'Build Your House', 'Step Inside', 'Materiais', 'Redes sociais']);
  const grupo = page.locator('#decisoes-abertas .decisoes-projeto', { hasText: 'Build Your House' });
  await expect(grupo.locator('li')).toHaveCount(5);
  await expect(grupo).toContainText('Vendemos o Build Your House e o Step Inside a outras empresas?');
  await grupo.locator('.decisoes-projeto-nome').click();
  await expect(page).toHaveURL(/#\/projeto\/build-your-house$/);
});
