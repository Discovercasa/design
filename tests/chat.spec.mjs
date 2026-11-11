// Chat da equipa (migração 0018, 2026-11-11): conversas privadas entre as pessoas do hub, com texto, ficheiros,
// imagens/vídeos e áudios. Base simulada (fake-supabase.js): nada toca no Supabase real.
import { test, expect } from '@playwright/test';
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const FIXTURE = readFileSync(new URL('./fixture.json', import.meta.url), 'utf8');
const FAKE = readFileSync(new URL('./fake-supabase.js', import.meta.url), 'utf8');
mkdirSync(new URL('./capturas/', import.meta.url), { recursive: true });
const captura = (page, nome) => page.screenshot({ path: fileURLToPath(new URL(`./capturas/${nome}-${test.info().project.name}.png`, import.meta.url)) });
const ehTelemovel = () => test.info().project.name === 'telemovel';

// a 1x1 PNG
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64');
const TERCEIRA = { id: 'u-terceira', nome: 'Terceira Pessoa', criado_em: '2026-11-01T00:00:00Z', notificacoes_vistas_em: '2026-11-01T00:00:00Z' };

async function abrir(page, chat = {}) {
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|Failed to load resource/.test(m.text())) erros.push(m.text()); });
  await page.addInitScript(([fx, c]) => { window.__FIXTURE = JSON.parse(fx); window.__FIXTURE_CHAT = c; }, [FIXTURE, { perfis: [TERCEIRA], ...chat }]);
  await page.route('**/@supabase/supabase-js@*/**', (r) => r.fulfill({ contentType: 'text/javascript', body: FAKE }));
  await page.goto('/');
  await expect(page.locator('.projeto-linha').first()).toBeVisible();
  return erros;
}
// a fake microphone for the audio test (Chromium)
test.use({ permissions: ['microphone'], launchOptions: { args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] } });
const enviar = (page) => page.locator('#chat').getByRole('button', { name: 'Enviar', exact: true }).click();

test('Chat: o ícone fica à esquerda das Sugestões; escrever a uma pessoa, juntar ficheiros e imagens', async ({ page }) => {
  const erros = await abrir(page);
  // the chat icon, left of the suggestions one
  await expect(page.locator('.topo-acoes > button').first()).toHaveAttribute('id', 'b-chat');
  await expect(page.locator('.topo-acoes > button').nth(1)).toHaveAttribute('id', 'b-sugestoes');
  await page.getByRole('button', { name: 'Chat', exact: true }).click();
  const chat = page.locator('#chat');
  await expect(chat.getByRole('heading', { name: 'Chat' })).toBeVisible();
  await expect(chat).toContainText('Ainda sem conversas');
  // the people of the hub: one tap opens the direct conversation
  await chat.getByRole('button', { name: 'Colega Teste' }).click();
  await expect(chat.getByRole('heading', { name: 'Colega Teste' })).toBeVisible();
  await expect(chat).toContainText('Ainda sem mensagens. Escreve a primeira a Colega Teste.');
  await chat.getByRole('textbox', { name: 'Mensagem' }).fill('Olá! Já viste o orçamento?');
  if (ehTelemovel()) await enviar(page); else await chat.getByRole('textbox', { name: 'Mensagem' }).press('Enter');
  await expect(chat.locator('.msg.minha').last()).toContainText('Olá! Já viste o orçamento?');
  await expect(chat.getByRole('textbox', { name: 'Mensagem' })).toHaveValue('');
  // a file and an image in the same message
  await chat.locator('[data-chat-ficheiros="ficheiros"]').setInputFiles({ name: 'medicoes.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4 teste') });
  await chat.locator('[data-chat-ficheiros="media"]').setInputFiles({ name: 'obra.png', mimeType: 'image/png', buffer: PNG });
  await expect(chat.locator('#chat-pendentes li')).toHaveCount(2);
  await chat.getByRole('button', { name: 'Tirar medicoes.pdf' }).click();
  await expect(chat.locator('#chat-pendentes li')).toHaveCount(1);
  await chat.locator('[data-chat-ficheiros="ficheiros"]').setInputFiles({ name: 'medicoes.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4 teste') });
  await chat.getByRole('textbox', { name: 'Mensagem' }).fill('As medições e uma foto');
  await enviar(page);
  const ultima = chat.locator('.msg.minha').last();
  await expect(ultima).toContainText('As medições e uma foto');
  await expect(ultima.locator('.msg-ficheiro')).toContainText('medicoes.pdf');
  await expect(ultima.locator('.msg-imagens img')).toHaveAttribute('src', /blob:|icone/);
  await expect(chat.locator('#chat-pendentes')).toBeHidden();
  const anexos = await page.evaluate(() => window.__fake.db.mensagens.at(-1).anexos);
  expect(anexos.map((a) => a.tipo).sort()).toEqual(['ficheiro', 'imagem']);
  expect(anexos.every((a) => /^\d+\//.test(a.caminho))).toBe(true);   // in the conversation's own folder
  // the image opens big
  await ultima.locator('.msg-imagens button').click();
  await expect(page.locator('dialog.visor')).toBeVisible();
  await page.locator('dialog.visor .visor-fechar').click();
  // the other person answers: it arrives live, already read (the conversation is open)
  await page.evaluate(() => window.__fake.comoOutro((q) => q.mensagens.insert({ conversa_id: window.__fake.db.conversas[0].id, texto: 'Vi sim, falta a margem.' })));
  await expect(chat.locator('.msg:not(.minha)').last()).toContainText('Vi sim, falta a margem.');
  await expect(chat.locator('.msg:not(.minha)').last()).toContainText('Colega Teste');
  await expect(page.locator('#contador-chat')).toBeHidden();
  await captura(page, 'chat-conversa');
  // my own message can be deleted
  page.once('dialog', (d) => d.accept());
  await chat.locator('.msg.minha').first().locator('.msg-apagar').click({ force: true });
  await expect(chat.locator('.msg.minha')).toHaveCount(1);
  expect(erros).toEqual([]);
});

test('Chat: uma mensagem nova com o chat fechado avisa e conta no ícone', async ({ page }) => {
  const erros = await abrir(page, {
    conversas: [{ id: 7, titulo: '', grupo: false, claude: false, criada_por: 'u-outro', criada_em: '2026-11-10T10:00:00Z', ultima_em: '2026-11-10T10:00:00Z' }],
    conversas_membros: [{ conversa_id: 7, utilizador_id: 'u-eu', lida_em: '2026-11-10T10:00:00Z' }, { conversa_id: 7, utilizador_id: 'u-outro', lida_em: '2026-11-10T10:00:00Z' }],
    mensagens: [],
  });
  await expect(page.locator('#contador-chat')).toBeHidden();
  await page.evaluate(() => window.__fake.comoOutro((q) => q.mensagens.insert({ conversa_id: 7, texto: 'Podes ver a tarefa 169?' })));
  await expect(page.locator('.aviso', { hasText: 'Podes ver a tarefa 169?' })).toBeVisible();
  await expect(page.locator('#contador-chat')).toHaveText('1');
  await expect(page.getByRole('button', { name: 'Chat (1 por ler)' })).toBeVisible();
  await page.locator('.aviso', { hasText: 'Podes ver a tarefa 169?' }).getByRole('button', { name: 'Abrir' }).click();
  const chat = page.locator('#chat');
  await expect(chat.getByRole('heading', { name: 'Colega Teste' })).toBeVisible();
  await expect(chat.locator('.msg').last()).toContainText('Podes ver a tarefa 169?');
  await expect(page.locator('#contador-chat')).toBeHidden();
  const lida = await page.evaluate(() => window.__fake.db.conversas_membros.find((m) => m.utilizador_id === 'u-eu').lida_em);
  expect(new Date(lida) > new Date('2026-11-10T10:00:00Z')).toBe(true);
  expect(erros).toEqual([]);
});

test('Chat: a conversa com o Claude, um grupo e as conversas dos outros não aparecem', async ({ page }) => {
  const erros = await abrir(page, {
    conversas: [
      { id: 3, titulo: 'Claude', grupo: false, claude: true, criada_por: null, criada_em: '2026-11-11T09:00:00Z', ultima_em: '2026-11-11T09:00:00Z' },
      { id: 4, titulo: '', grupo: false, claude: false, criada_por: 'u-outro', criada_em: '2026-11-11T09:00:00Z', ultima_em: '2026-11-11T09:30:00Z' },
    ],
    conversas_membros: [{ conversa_id: 3, utilizador_id: 'u-eu', lida_em: '2026-11-11T08:00:00Z' },
      { conversa_id: 4, utilizador_id: 'u-outro', lida_em: '2026-11-11T08:00:00Z' }, { conversa_id: 4, utilizador_id: 'u-terceira', lida_em: '2026-11-11T08:00:00Z' }],
    mensagens: [
      { id: 1, conversa_id: 3, autor_id: null, autor_nome: 'Claude', texto: 'Olá. Faltam-me estas informações para o preço final:\n1. Mão de obra', anexos: [], criada_em: '2026-11-11T09:00:00Z' },
      { id: 2, conversa_id: 4, autor_id: 'u-outro', autor_nome: 'Colega Teste', texto: 'Segredo entre os dois', anexos: [], criada_em: '2026-11-11T09:30:00Z' },
    ],
  });
  // at the start: the unread message is announced
  await expect(page.locator('.aviso', { hasText: 'Tens 1 mensagem por ler' })).toContainText('Claude');
  await expect(page.locator('#contador-chat')).toHaveText('1');
  await page.getByRole('button', { name: 'Chat (1 por ler)' }).click();
  const chat = page.locator('#chat');
  await expect(chat.locator('.chat-linha')).toHaveCount(1);   // conversation 4 is not mine
  await expect(chat).not.toContainText('Segredo entre os dois');
  await expect(chat.locator('.chat-linha.por-ler')).toContainText('Claude');
  await chat.locator('.chat-linha', { hasText: 'Claude' }).click();
  await expect(chat.getByText('Responde aqui: o Claude lê as respostas.')).toBeVisible();
  await expect(chat.locator('.msg.claude')).toContainText('1. Mão de obra');
  await chat.getByRole('textbox', { name: 'Mensagem' }).fill('Mão de obra: 120 €/m²');
  await enviar(page);
  await expect(chat.locator('.msg.minha')).toContainText('Mão de obra: 120 €/m²');
  // back to the list and a new group
  await chat.getByRole('button', { name: 'Voltar às conversas' }).click();
  await chat.getByRole('button', { name: 'Grupo' }).click();
  await chat.getByLabel('Nome do grupo (opcional)').fill('Obra Torres Vedras');
  await chat.getByLabel('Colega Teste').check();
  await chat.getByLabel('Terceira Pessoa').check();
  await chat.getByRole('button', { name: 'Criar grupo' }).click();
  await expect(chat.getByRole('heading', { name: 'Obra Torres Vedras' })).toBeVisible();
  await expect(chat.locator('.chat-topo')).toContainText('Colega Teste, Terceira Pessoa');
  await chat.getByRole('textbox', { name: 'Mensagem' }).fill('Bom dia a todos');
  await enviar(page);
  await expect(chat.locator('.msg.minha')).toContainText('Bom dia a todos');
  await chat.getByRole('button', { name: 'Voltar às conversas' }).click();
  await expect(chat.locator('.chat-linha').first()).toContainText('Obra Torres Vedras');
  await expect(chat.locator('.chat-linha').first()).toContainText('Tu: Bom dia a todos');
  await captura(page, 'chat-lista');
  // notifications (migration 0021): «conversa» opens the chat, «sugestao» the suggestions' checklist
  await page.keyboard.press('Escape');
  await expect(chat).toBeHidden();
  await page.evaluate(() => {
    const n = (id, tipo, texto, ref_tipo, ref_id) => ({ id, projeto: null, tipo, texto, ator_id: null, ator_nome: 'Claude', destinatario_id: null, ref_tipo, ref_id, criada_em: new Date().toISOString() });
    window.__fake.db.notificacoes.push(n(900, 'chat', 'O Claude enviou-te 11 perguntas no chat', 'conversa', 3), n(901, 'sugestao_estado', 'O Claude concluiu a sugestão «Pôr um modo escuro no hub.»', 'sugestao', 1));
    window.__fake.avisar('notificacoes');
  });
  await page.getByRole('button', { name: /Notificações/ }).click();
  const pop = page.locator('#pop-notificacoes');
  await expect(pop.locator('.notif', { hasText: 'O Claude enviou-te' })).toContainText('Chat');
  await expect(pop.locator('.notif', { hasText: 'O Claude concluiu' })).toContainText('Sugestões');
  await pop.locator('.notif', { hasText: 'O Claude enviou-te' }).locator('.notif-abrir').click();
  await expect(chat.getByRole('heading', { name: 'Claude' })).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(chat).toBeHidden();
  await page.getByRole('button', { name: /Notificações/ }).click();
  await pop.locator('.notif', { hasText: 'O Claude concluiu' }).locator('.notif-abrir').click();
  await expect(page.locator('#gaveta').getByRole('tab', { name: 'Checklist' })).toHaveAttribute('aria-selected', 'true');
  expect(erros).toEqual([]);
});

test.describe('Chat: áudio', () => {
  test('gravar e enviar um áudio', async ({ page }) => {
    const erros = await abrir(page);
    await page.getByRole('button', { name: 'Chat', exact: true }).click();
    const chat = page.locator('#chat');
    await chat.getByRole('button', { name: 'Colega Teste' }).click();
    await chat.getByRole('button', { name: 'Gravar um áudio' }).click();
    await expect(chat.getByText('A gravar áudio…')).toBeVisible();
    await page.waitForTimeout(1300);
    await expect(chat.locator('#chat-tempo')).toHaveText(/0:0[1-2]/);
    await chat.getByRole('button', { name: 'Parar e enviar o áudio' }).click();
    const audio = chat.locator('.msg.minha .msg-audio audio');
    await expect(audio).toHaveCount(1);
    await expect(audio).toHaveAttribute('src', /blob:|icone/);
    const a = await page.evaluate(() => window.__fake.db.mensagens.at(-1).anexos[0]);
    expect(a.tipo).toBe('audio');
    expect(a.mime).toMatch(/^audio\//);
    expect(a.duracao).toBeGreaterThan(1);
    // cancelling sends nothing
    await chat.getByRole('button', { name: 'Gravar um áudio' }).click();
    await expect(chat.getByText('A gravar áudio…')).toBeVisible();
    await chat.getByRole('button', { name: 'Cancelar' }).click();
    await expect(chat.getByRole('textbox', { name: 'Mensagem' })).toBeVisible();
    await page.waitForTimeout(300);
    expect(await page.evaluate(() => window.__fake.db.mensagens.length)).toBe(1);
    expect(erros).toEqual([]);
  });
});
