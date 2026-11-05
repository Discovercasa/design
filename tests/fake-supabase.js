// Supabase simulado para os testes Playwright (substitui o supabase-js do CDN). Guarda as tabelas em memória,
// imita as regras dos triggers das migrações 0004 (carimbos, dia de conclusão, notificações, nome do responsável) e
// a parte do supabase-js que o hub usa. window.__fake permite agir como outra pessoa.
(function () {
  const fx = window.__FIXTURE || {};
  const U = window.__UTILIZADOR || { id: 'u-eu', nome: 'Teste Hub', nivel: 'editar' };
  const OUTRO = { id: 'u-outro', nome: 'Colega Teste' };
  const agora = () => new Date().toISOString();
  const hoje = () => new Date().toISOString().slice(0, 10);
  const db = {
    projetos: [['build_your_house', 'Build Your House'], ['builder', 'Builder'], ['gerador', 'Gerador de documentos'], ['orcamentacao', 'Orçamentação'], ['plataforma_cliente', 'Step Inside']].map(([id, nome], i) => ({ id, nome, ordem: i + 1 })),
    perfis: [{ id: OUTRO.id, nome: OUTRO.nome, criado_em: '2026-11-01T00:00:00Z', notificacoes_vistas_em: '2026-11-01T00:00:00Z' }],
    checkpoints: fx.checkpoints || [], tarefas: fx.tarefas || [], decisoes: fx.decisoes || [], decisoes_opcoes: fx.decisoes_opcoes || [],
    notificacoes: [], vistos: [],
    sugestoes: [{ id: 1, texto: 'Pôr um modo escuro no hub.', ferramenta: 'geral', estado: 'nova', autor_id: OUTRO.id, autor_nome: OUTRO.nome, criada_em: '2026-11-04T09:00:00Z', na_checklist: false, checklist_em: null }],
    sugestoes_comentarios: [],
  };
  const seq = {}; Object.keys(db).forEach((t) => (seq[t] = Math.max(0, ...db[t].map((r) => (typeof r.id === 'number' ? r.id : 0)))));
  let ator = U;  // quem está a agir (para os triggers)
  const ROT = { por_fazer: 'Por fazer', em_curso: 'Em curso', bloqueada: 'Bloqueada', concluida: 'Concluída', concluido: 'Concluído' };
  const pnome = (id) => (db.perfis.find((p) => p.id === id) || {}).nome;
  const nomeAtual = () => pnome(ator.id) || ator.nome || 'Alguém';
  function notificar(projeto, tipo, texto, ref_tipo, ref_id) {
    db.notificacoes.push({ id: ++seq.notificacoes, projeto, tipo, texto, ator_id: ator.id, ator_nome: nomeAtual(), destinatario_id: null, ref_tipo, ref_id, criada_em: agora() });
  }
  const antes = {
    checkpoints(n, o) {
      if (!o) { Object.assign(n, { criado_por: ator.id, criado_por_nome: nomeAtual(), criado_em: agora() }); n.descricao ??= ''; n.ordem ??= 0; n.estado ??= 'por_fazer'; n.concluido_em ??= null; }
      else if (n.estado !== o.estado) n.concluido_em = n.estado === 'concluido' ? hoje() : null;
    },
    tarefas(n, o) {
      if (!o) { Object.assign(n, { criado_por: ator.id, criado_por_nome: nomeAtual(), criado_em: agora() }); Object.assign(n, { descricao: n.descricao ?? '', estado: n.estado ?? 'por_fazer', custo: n.custo ?? '', app_sugerida: n.app_sugerida ?? null, responsavel_id: n.responsavel_id ?? null, ordem: n.ordem ?? 0, concluida_em: null }); }
      else if (n.estado !== o.estado) n.concluida_em = n.estado === 'concluida' ? hoje() : null;
      n.projeto = db.checkpoints.find((c) => c.id === n.checkpoint_id).projeto;
      n.responsavel_nome = n.responsavel_id ? pnome(n.responsavel_id) || 'Alguém' : '';
    },
    decisoes(n, o) {
      if (!o) { Object.assign(n, { criado_por: ator.id, criado_por_nome: nomeAtual(), criado_em: agora(), estado: 'aberta', contexto: n.contexto ?? '', justificacao: '', opcao_escolhida: null, decidida_por: null, decidida_por_nome: '', decidida_em: null }); return; }
      if (n.estado === 'decidida') {
        if (!db.decisoes_opcoes.some((x) => x.id === n.opcao_escolhida && x.decisao_id === n.id)) throw new Error('Escolha uma das opções desta decisão.');
        if (o.estado !== 'decidida' || n.opcao_escolhida !== o.opcao_escolhida) Object.assign(n, { decidida_por: ator.id, decidida_por_nome: nomeAtual(), decidida_em: hoje() });
      } else Object.assign(n, { opcao_escolhida: null, decidida_por: null, decidida_por_nome: '', decidida_em: null });
    },
  };
  const depois = {
    checkpoints(n, o) {
      if (!o) notificar(n.projeto, 'checkpoint_novo', `${nomeAtual()} acrescentou o checkpoint «${n.titulo}»`, 'checkpoint', n.id);
      else if (n.estado !== o.estado) notificar(n.projeto, n.estado === 'concluido' ? 'checkpoint_concluido' : 'checkpoint_estado', n.estado === 'concluido' ? `${nomeAtual()} concluiu o checkpoint «${n.titulo}»` : `${nomeAtual()} mudou o checkpoint «${n.titulo}» para ${ROT[n.estado]}`, 'checkpoint', n.id);
    },
    tarefas(n, o) {
      const t = `«${n.titulo}»`;
      if (!o) notificar(n.projeto, 'tarefa_nova', `${nomeAtual()} acrescentou a tarefa ${t}`, 'tarefa', n.id);
      if (n.responsavel_id && (!o || n.responsavel_id !== o.responsavel_id)) notificar(n.projeto, 'tarefa_atribuida', `${nomeAtual()} atribuiu a tarefa ${t} a ${n.responsavel_nome}`, 'tarefa', n.id);
      if (o && n.estado !== o.estado) notificar(n.projeto, n.estado === 'concluida' ? 'tarefa_concluida' : 'tarefa_estado', n.estado === 'concluida' ? `${nomeAtual()} concluiu a tarefa ${t}` : `${nomeAtual()} mudou a tarefa ${t} para ${ROT[n.estado]}`, 'tarefa', n.id);
    },
    decisoes(n, o) {
      if (!o) return notificar(n.projeto, 'decisao_nova', `${nomeAtual()} abriu a decisão «${n.pergunta}»`, 'decisao', n.id);
      if (n.estado === 'decidida' && (o.estado !== 'decidida' || n.opcao_escolhida !== o.opcao_escolhida)) {
        const ops = db.decisoes_opcoes.filter((x) => x.decisao_id === n.id).sort((a, b) => a.ordem - b.ordem);
        const esc = ops.find((x) => x.id === n.opcao_escolhida), outras = ops.filter((x) => x !== esc).map((x) => `«${x.titulo}»`).join(', ');
        notificar(n.projeto, 'decisao_tomada', `${nomeAtual()} decidiu «${n.pergunta}»: escolhemos «${esc.titulo}»${outras ? ' em vez de ' + outras : ''}`, 'decisao', n.id);
      }
    },
  };
  const FILHOS = { decisoes_opcoes: ['decisoes', 'decisao_id'], sugestoes_comentarios: ['sugestoes', 'sugestao_id'] };
  const copia = (o) => JSON.parse(JSON.stringify(o));

  class Q {
    constructor(t) { this.t = t; this.op = 'select'; this.f = []; this.ord = null; this.lim = null; this.um = null; this.ret = false; }
    select(cols) { if (this.op === 'select') this.cols = cols || '*'; else this.ret = true; return this; }
    insert(v) { this.op = 'insert'; this.v = Array.isArray(v) ? v : [v]; return this; }
    upsert(v) { this.op = 'upsert'; this.v = Array.isArray(v) ? v : [v]; return this; }
    update(v) { this.op = 'update'; this.v = v; return this; }
    delete() { this.op = 'delete'; return this; }
    eq(c, v) { this.f.push((r) => r[c] === v); return this; }
    order(c, o = {}) { this.ord = [c, o.ascending !== false]; return this; }
    limit(n) { this.lim = n; return this; }
    single() { this.um = 'single'; return this; }
    maybeSingle() { this.um = 'maybe'; return this; }
    then(ok, falha) { return Promise.resolve().then(() => this.correr()).then(ok, falha); }
    correr() {
      const tab = db[this.t];
      if (!tab) return { data: null, error: { message: `relation "public.${this.t}" does not exist` } };
      try {
        let linhas;
        if (this.op === 'insert' || this.op === 'upsert') {
          linhas = this.v.map((v) => {
            const n = copia(v);
            if (this.op === 'upsert' && n.id && tab.find((r) => r.id === n.id)) { const r = tab.find((x) => x.id === n.id); Object.assign(r, n); return r; }
            if (this.t === 'perfis') { n.criado_em = agora(); n.notificacoes_vistas_em = agora(); }
            else if (this.t === 'vistos') { n.utilizador_id = ator.id; if (tab.some((r) => r.utilizador_id === n.utilizador_id && r.tipo === n.tipo && r.ref_id === n.ref_id)) throw new Error('duplicate key'); }
            else n.id = ++seq[this.t];
            if (this.t === 'sugestoes') Object.assign(n, { autor_id: ator.id, estado: 'nova', criada_em: agora(), na_checklist: false, checklist_em: null });
            if (this.t === 'sugestoes_comentarios') Object.assign(n, { autor_id: ator.id, criado_em: agora() });
            if (antes[this.t]) antes[this.t](n, null);
            tab.push(n);
            if (depois[this.t]) depois[this.t](n, null);
            return n;
          });
        } else if (this.op === 'update') {
          linhas = tab.filter((r) => this.f.every((f) => f(r)));
          linhas.forEach((r) => { const o = copia(r), n = Object.assign(copia(r), this.v); if (antes[this.t]) antes[this.t](n, o); Object.assign(r, n); if (depois[this.t]) depois[this.t](r, o); });
        } else if (this.op === 'delete') {
          const fora = tab.filter((r) => this.f.every((f) => f(r)));
          db[this.t] = tab.filter((r) => !fora.includes(r));
          if (this.t === 'checkpoints') db.tarefas = db.tarefas.filter((t) => !fora.some((c) => c.id === t.checkpoint_id));
          if (this.t === 'decisoes') db.decisoes_opcoes = db.decisoes_opcoes.filter((o) => !fora.some((d) => d.id === o.decisao_id));
          linhas = fora;
        } else {
          linhas = tab.filter((r) => this.f.every((f) => f(r)));
          if (this.t === 'vistos') linhas = linhas.filter((r) => r.utilizador_id === ator.id);
          if (this.ord) { const [c, asc] = this.ord; linhas = [...linhas].sort((a, b) => (a[c] < b[c] ? -1 : a[c] > b[c] ? 1 : 0) * (asc ? 1 : -1)); }
          if (this.lim) linhas = linhas.slice(0, this.lim);
          linhas = linhas.map((r) => {
            const c = copia(r);
            for (const [filho, [pai, fk]] of Object.entries(FILHOS)) if (pai === this.t && new RegExp(filho + '\\s*\\(').test(this.cols)) c[filho] = copia(db[filho].filter((x) => x[fk] === r.id));
            return c;
          });
        }
        let data = this.op === 'select' || this.ret ? copia(linhas) : null;
        if (this.um) { if (this.um === 'single' && data.length !== 1) return { data: null, error: { message: 'JSON object requested, multiple (or no) rows returned' } }; data = data[0] || null; }
        return { data, error: null };
      } catch (e) { return { data: null, error: { message: e.message } }; }
    }
  }
  const sessao = { user: { id: U.id, app_metadata: { nivel: U.nivel }, user_metadata: { nome: U.nome } } };
  let ligado = !window.__SEM_SESSAO && sessionStorage.getItem('fake-saiu') !== '1';
  window.supabase = {
    createClient: () => ({
      from: (t) => new Q(t),
      auth: {
        getSession: async () => ({ data: { session: ligado ? sessao : null } }),
        signOut: async () => { ligado = false; sessionStorage.setItem('fake-saiu', '1'); return { error: null }; },
        verifyOtp: async () => ({ data: { session: sessao }, error: null }),
      },
    }),
  };
  // nos testes: agir como outra pessoa (acrescentar, concluir…) e ver a base
  window.__fake = {
    db, OUTRO,
    async comoOutro(fn) { ator = OUTRO; try { return await fn(new Proxy({}, { get: (_, t) => new Q(t) })); } finally { ator = U; } },
  };
})();
