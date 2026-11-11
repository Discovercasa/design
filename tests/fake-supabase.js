// Supabase simulado para os testes Playwright (substitui o supabase-js do CDN). Guarda as tabelas em memória,
// imita as regras dos triggers das migrações 0004 (carimbos, dia de conclusão, notificações, nome do responsável) e
// a parte do supabase-js que o hub usa. window.__fake permite agir como outra pessoa.
(function () {
  const fx = window.__FIXTURE || {};
  const fs = window.__FIXTURE_SOCIAL || {};   // redes sociais (migração 0010)
  const fm = window.__FIXTURE_MATERIAIS || {};   // materiais vindos do Hub (migração 0016, só de consulta)
  const fc = window.__FIXTURE_CHAT || {};        // chat da equipa (migração 0018)
  const U = window.__UTILIZADOR || { id: 'u-eu', nome: 'Teste Hub', nivel: 'editar' };
  const OUTRO = { id: 'u-outro', nome: 'Colega Teste' };
  const agora = () => new Date().toISOString();
  const hoje = () => new Date().toISOString().slice(0, 10);
  const db = {
    projetos: [['build_your_house', 'Build Your House'], ['builder', 'Builder'], ['gerador', 'Gerador de documentos'], ['orcamentacao', 'Orçamentação'], ['plataforma_cliente', 'Step Inside']].map(([id, nome], i) => ({ id, nome, ordem: i + 1 })),
    perfis: [{ id: OUTRO.id, nome: OUTRO.nome, criado_em: '2026-11-01T00:00:00Z', notificacoes_vistas_em: '2026-11-01T00:00:00Z' }, ...(fc.perfis || [])],
    conversas: fc.conversas || [], conversas_membros: fc.conversas_membros || [], mensagens: fc.mensagens || [],
    checkpoints: fx.checkpoints || [], tarefas: fx.tarefas || [], decisoes: fx.decisoes || [], decisoes_opcoes: fx.decisoes_opcoes || [],
    documentos: fx.documentos || [], notificacoes: [], vistos: [],
    tarefas_notas: fx.tarefas_notas || [], anexos: [], notificacoes_lidas: [],
    obras: fs.obras || [], obras_fases: fs.obras_fases || [], posts: fs.posts || [], posts_media: fs.posts_media || [], posts_comentarios: fs.posts_comentarios || [],
    sugestoes: [{ id: 1, texto: 'Pôr um modo escuro no hub.', ferramenta: 'geral', estado: 'nova', autor_id: OUTRO.id, autor_nome: OUTRO.nome, criada_em: '2026-11-04T09:00:00Z', na_checklist: false, checklist_em: null }],
    sugestoes_comentarios: [],
    hub_fornecedores: fm.hub_fornecedores || [], hub_materiais: fm.hub_materiais || [],
    hub_material_precos: fm.hub_material_precos || [], hub_material_precos_historico: fm.hub_material_precos_historico || [],
    // the price parcels (migration 0017): the same nine rows as the migration, no values yet
    orcamento_parcelas: window.__FIXTURE_ORCAMENTO || [['materiais', 'Materiais', 'materiais_hub', null], ['caixilharia', 'Caixilharia', 'por_m2', 'vaos'],
      ['fundacao', 'Fundação', 'por_m2', 'implantacao'], ['mao_de_obra', 'Mão de obra', 'por_m2', 'construcao'], ['especialidades', 'Especialidades', 'valor_fixo', null],
      ['instalacoes', 'Instalações e pré-instalações', 'por_m2', 'construcao'], ['licenciamento', 'Licenciamento', 'valor_fixo', null],
      ['margem', 'Margem', 'percentagem_subtotal', null], ['iva', 'IVA', 'taxa_iva', null]]
      .map(([id, nome, metodo, base], i) => ({ id, nome, ordem: i + 1, metodo, base, valor: null, nota: '', atualizado_por_nome: 'Claude', atualizado_em: '2026-11-11T03:00:00Z' })),
  };
  const seq = {}; Object.keys(db).forEach((t) => (seq[t] = Math.max(0, ...db[t].map((r) => (typeof r.id === 'number' ? r.id : 0)))));
  let ator = U;  // quem está a agir (para os triggers)
  const ROT = { por_fazer: 'Por fazer', em_curso: 'Em curso', bloqueada: 'Bloqueada', concluida: 'Concluída', concluido: 'Concluído' };
  const pnome = (id) => (db.perfis.find((p) => p.id === id) || {}).nome;
  const nomeAtual = () => pnome(ator.id) || ator.nome || 'Alguém';
  function notificar(projeto, tipo, texto, ref_tipo, ref_id) {
    db.notificacoes.push({ id: ++seq.notificacoes, projeto, tipo, texto, ator_id: ator.id, ator_nome: nomeAtual(), destinatario_id: null, ref_tipo, ref_id, criada_em: agora() });
    if (typeof avisar === 'function') avisar('notificacoes');
  }
  const antes = {
    orcamento_parcelas(n, o) {   // migration 0017: RLS "Editar" + the trigger orcamento_parcelas_antes
      if (ator.nivel && ator.nivel !== 'editar') throw new Error('new row violates row-level security policy for table "orcamento_parcelas"');
      Object.assign(n, { id: o.id, ordem: o.ordem });
      if (o.metodo === 'materiais_hub') Object.assign(n, { metodo: o.metodo, valor: null });
      if (o.metodo === 'taxa_iva') n.metodo = o.metodo;
      if (n.metodo !== 'por_m2') n.base = null; else if (!n.base) n.base = 'construcao';
      Object.assign(n, { atualizado_por_nome: nomeAtual(), atualizado_em: agora() });
    },
    checkpoints(n, o) {
      if (!o) { Object.assign(n, { criado_por: ator.id, criado_por_nome: nomeAtual(), criado_em: agora() }); n.descricao ??= ''; n.ordem ??= 0; n.estado ??= 'por_fazer'; n.concluido_em ??= null; }
      else if (n.estado !== o.estado) n.concluido_em = n.estado === 'concluido' ? hoje() : null;
    },
    tarefas(n, o) {
      if (!o) { Object.assign(n, { criado_por: ator.id, criado_por_nome: nomeAtual(), criado_em: agora() }); Object.assign(n, { descricao: n.descricao ?? '', estado: n.estado ?? 'por_fazer', custo: n.custo ?? '', app_sugerida: n.app_sugerida ?? null, responsavel_id: n.responsavel_id ?? null, ordem: n.ordem ?? 0, concluida_em: null, revisao: n.revisao ?? false }); }
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
  depois.documentos = (n, o) => { if (!o) notificar(n.projeto, 'documento_novo', `${nomeAtual()} acrescentou o documento «${n.titulo}» (${n.tipo})`, 'documento', n.id); };
  antes.documentos = (n, o) => { if (!o) Object.assign(n, { criado_por: ator.id, criado_por_nome: nomeAtual(), criado_em: agora(), descricao: n.descricao ?? '' }); };
  // redes sociais (migração 0009): carimbos, aprovação e notificações
  const carimbo = (n) => Object.assign(n, { criado_por: ator.id, criado_por_nome: nomeAtual(), criado_em: agora() });
  antes.obras = (n, o) => { if (!o) { carimbo(n); n.descricao ??= ''; n.ativa ??= true; n.ordem ??= 0; } };
  depois.obras = (n, o) => { if (!o) notificar(null, 'obra_nova', `${nomeAtual()} acrescentou a obra «${n.nome}»`, 'obra', n.id); };
  antes.obras_fases = (n, o) => {
    if (!o) { carimbo(n); Object.assign(n, { estado: n.estado ?? 'prevista', periodo: n.periodo ?? '', posts_previstos: n.posts_previstos ?? null, fotos: n.fotos ?? 'por_tirar', visita_em: n.visita_em ?? null, fotos_em: null, notas: n.notas ?? '', concluida_em: n.estado === 'concluida' ? hoje() : null }); }
    else { n.obra_id = o.obra_id; if (n.estado !== o.estado) n.concluida_em = n.estado === 'concluida' ? hoje() : null; }
    if (n.fotos === 'tiradas' && (!o || o.fotos !== 'tiradas') && !n.fotos_em) n.fotos_em = hoje();
    if (n.fotos !== 'tiradas') n.fotos_em = null;
    if (n.fotos === 'por_tirar') n.visita_em = null;
  };
  depois.obras_fases = (n, o) => {
    const ob = (db.obras.find((x) => x.id === n.obra_id) || {}).nome;
    if (!o) notificar(null, 'fase_nova', `${nomeAtual()} acrescentou a fase «${n.nome}» à obra ${ob}`, 'obra', n.obra_id);
    else if (n.estado !== o.estado) notificar(null, 'fase_estado', `${nomeAtual()} marcou ${ob} · ${n.nome} como ${{ concluida: 'concluída', em_curso: 'em curso', prevista: 'prevista' }[n.estado]}`, 'obra', n.obra_id);
    else if (n.fotos !== o.fotos && n.fotos !== 'por_tirar') notificar(null, 'fase_estado', n.fotos === 'tiradas' ? `${nomeAtual()} tirou as fotos de ${ob} · ${n.nome}` : `${nomeAtual()} marcou a visita para fotos a ${ob} · ${n.nome}`, 'obra', n.obra_id);
  };
  antes.posts = (n, o) => {
    if (!o) { carimbo(n); Object.assign(n, { obra_id: n.obra_id ?? null, fase_id: n.fase_id ?? null, tipo: n.tipo ?? 'carrossel', redes: n.redes ?? ['instagram', 'facebook'], legenda: n.legenda ?? '', notas: n.notas ?? '',
      estado: n.estado ?? 'ideia', legenda_aprovada: n.legenda_aprovada ?? false, fotos_aprovadas: n.fotos_aprovadas ?? false, legenda_aprovada_por_nome: '', fotos_aprovadas_por_nome: '', legenda_aprovada_em: null, fotos_aprovadas_em: null, publicar_em: null, publicado_em: null }); }
    n.atualizado_em = agora();
    if (!o) Object.assign(n, { mes_original: null, semana_original: null });
    else if (n.mes !== o.mes || n.semana !== o.semana) {
      Object.assign(n, o.mes_original ? { mes_original: o.mes_original, semana_original: o.semana_original } : { mes_original: o.mes, semana_original: o.semana });
      if (n.mes === n.mes_original && n.semana === n.semana_original) Object.assign(n, { mes_original: null, semana_original: null });
    } else Object.assign(n, { mes_original: o.mes_original, semana_original: o.semana_original });
    if (n.fase_id && !db.obras_fases.some((f) => f.id === n.fase_id && f.obra_id === n.obra_id)) n.fase_id = null;
    if (o && n.legenda !== o.legenda && o.legenda_aprovada && n.legenda_aprovada) n.legenda_aprovada = false;
    for (const k of ['legenda', 'fotos']) {
      if (n[k + '_aprovada' + (k === 'fotos' ? 's' : '')]) {
        if (!o || !o[k + '_aprovada' + (k === 'fotos' ? 's' : '')]) { n[k + (k === 'fotos' ? '_aprovadas' : '_aprovada') + '_por_nome'] = nomeAtual(); n[k + (k === 'fotos' ? '_aprovadas' : '_aprovada') + '_em'] = hoje(); }
      } else { n[k + (k === 'fotos' ? '_aprovadas' : '_aprovada') + '_por_nome'] = ''; n[k + (k === 'fotos' ? '_aprovadas' : '_aprovada') + '_em'] = null; }
    }
    if (n.legenda_aprovada && n.fotos_aprovadas && ['ideia', 'rascunho', 'por_aprovar'].includes(n.estado)) n.estado = 'aprovado';
    else if (!(n.legenda_aprovada && n.fotos_aprovadas) && n.estado === 'aprovado') n.estado = 'por_aprovar';
    if (n.estado === 'publicado') { if (!n.publicado_em && (!o || o.estado !== 'publicado')) n.publicado_em = hoje(); } else n.publicado_em = null;
  };
  const ROTP = { ideia: 'Ideia', rascunho: 'Rascunho', por_aprovar: 'Por aprovar', aprovado: 'Aprovado', publicado: 'Publicado' };
  depois.posts = (n, o) => {
    const t = `«${n.titulo}»`;
    if (!o) return notificar(null, 'post_novo', `${nomeAtual()} planeou o post ${t}`, 'post', n.id);
    if (n.legenda_aprovada && !o.legenda_aprovada && n.fotos_aprovadas && !o.fotos_aprovadas) notificar(null, 'post_aprovacao', `${nomeAtual()} aprovou a legenda e as fotos do post ${t}`, 'post', n.id);
    else if (n.legenda_aprovada && !o.legenda_aprovada) notificar(null, 'post_aprovacao', `${nomeAtual()} aprovou a legenda do post ${t}`, 'post', n.id);
    else if (n.fotos_aprovadas && !o.fotos_aprovadas) notificar(null, 'post_aprovacao', `${nomeAtual()} aprovou as fotos do post ${t}`, 'post', n.id);
    if (n.estado !== o.estado) notificar(null, 'post_estado', n.estado === 'por_aprovar' ? `${nomeAtual()} pediu aprovação do post ${t}` : n.estado === 'publicado' ? `${nomeAtual()} publicou o post ${t}` : `${nomeAtual()} mudou o post ${t} para ${ROTP[n.estado]}`, 'post', n.id);
  };
  const desaprovarFotos = (postId) => { const p = db.posts.find((x) => x.id === postId); if (p && p.fotos_aprovadas) { const o = copia(p); p.fotos_aprovadas = false; antes.posts(p, o); depois.posts(p, o); } };
  antes.posts_media = (n, o) => { if (!o) { carimbo(n); n.ordem ??= 0; } else { n.caminho = o.caminho; n.miniatura = o.miniatura; n.post_id = o.post_id; } };
  depois.posts_media = (n, o) => { if (!o) desaprovarFotos(n.post_id); };
  antes.posts_comentarios = (n, o) => { if (!o) Object.assign(n, { autor_id: ator.id, autor_nome: nomeAtual(), criado_em: agora(), resolvido: n.resolvido ?? false, media_id: n.media_id ?? null }); };
  depois.posts_comentarios = (n, o) => { if (!o) notificar(null, 'post_comentario', `${nomeAtual()} comentou o post «${(db.posts.find((x) => x.id === n.post_id) || {}).titulo}»: ${n.texto.slice(0, 120)}`, 'post', n.post_id); };
  // notas de teste/revisão e imagens anexadas (migração 0011)
  const TIPOS_N = { bug: 'um bug', mudar: 'uma mudança', fazer: 'uma coisa a fazer', nota: 'uma nota' };
  antes.tarefas_notas = (n, o) => {
    if (!o) Object.assign(n, { autor_id: ator.id, autor_nome: nomeAtual(), criado_em: agora(), tipo: n.tipo ?? 'nota', resolvida: n.resolvida ?? false, tarefa_criada_id: n.tarefa_criada_id ?? null });
    else Object.assign(n, { autor_id: o.autor_id, autor_nome: o.autor_nome, criado_em: o.criado_em, tarefa_id: o.tarefa_id });
    n.projeto = (db.tarefas.find((t) => t.id === n.tarefa_id) || {}).projeto;
    if (n.resolvida && (!o || !o.resolvida)) Object.assign(n, { resolvida_por_nome: nomeAtual(), resolvida_em: hoje() });
    else if (!n.resolvida) Object.assign(n, { resolvida_por_nome: '', resolvida_em: null });
  };
  depois.tarefas_notas = (n, o) => {
    const t = `«${(db.tarefas.find((x) => x.id === n.tarefa_id) || {}).titulo}»`;
    if (!o) notificar(n.projeto, 'nota_nova', `${nomeAtual()} acrescentou ${TIPOS_N[n.tipo]} em ${t}: ${n.texto.slice(0, 120)}`, 'tarefa', n.tarefa_id);
    else if (n.resolvida && !o.resolvida) notificar(n.projeto, 'nota_resolvida', `${nomeAtual()} resolveu em ${t}: ${n.texto.slice(0, 120)}`, 'tarefa', n.tarefa_id);
  };
  antes.anexos = (n, o) => {
    if (o) return;
    carimbo(n);
    const tab = { checkpoint: db.checkpoints, tarefa: db.tarefas, nota: db.tarefas_notas }[n.alvo];
    const ref = tab && tab.find((x) => x.id === n.ref_id);
    if (!ref) throw new Error(`O ${n.alvo} ${n.ref_id} não existe.`);
    n.projeto = ref.projeto; n.ordem ??= 0;
  };
  // chat (migração 0018): só os membros veem a conversa; cada um escreve em seu nome; o Claude escreve sem sessão
  const membro = (cid, quem = ator) => db.conversas_membros.some((m) => m.conversa_id === cid && m.utilizador_id === quem.id);
  antes.mensagens = (n, o) => {
    if (o) return;
    if (!membro(n.conversa_id)) throw new Error('new row violates row-level security policy for table "mensagens"');
    Object.assign(n, { autor_id: ator.id, autor_nome: nomeAtual(), criada_em: agora(), texto: n.texto ?? '', anexos: n.anexos ?? [] });
    if (!n.texto.trim() && !n.anexos.length) throw new Error('new row for relation "mensagens" violates check constraint');
    if (n.anexos.some((a) => !String(a.caminho).startsWith(n.conversa_id + '/'))) throw new Error('Anexo inválido.');
  };
  depois.mensagens = (n, o) => {
    if (o) return;
    const c = db.conversas.find((x) => x.id === n.conversa_id); if (c) c.ultima_em = n.criada_em;
    const l = db.conversas_membros.find((m) => m.conversa_id === n.conversa_id && m.utilizador_id === n.autor_id); if (l) l.lida_em = n.criada_em;
    avisar('conversas');
  };
  antes.conversas_membros = (n, o) => { if (o && (o.utilizador_id !== ator.id)) throw new Error('permission denied'); if (o) Object.assign(n, { conversa_id: o.conversa_id, utilizador_id: o.utilizador_id }); };
  // em direto: cada escrita avisa os canais abertos (como o Supabase Realtime)
  const ouvintes = [];
  const avisar = (t) => setTimeout(() => ouvintes.filter((o) => o.tabela === t).forEach((o) => o.cb({ table: t })), 30);
  // armazenamento privado: guarda só os nomes e os tamanhos
  const ficheiros = new Map((fx.documentos || []).map((d) => [d.caminho, d.tamanho]));
  // armazenamento "social": caminho → URL do ficheiro (os importados mostram uma imagem qualquer)
  const social = new Map((fs.posts_media || []).flatMap((m) => [[m.caminho, null], [m.miniatura, null]]));
  const urlSocial = (c) => social.get(c) || '/img/icone-192.png';
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
    ilike(c, pat) { const re = new RegExp('^' + pat.split('%').map((s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*') + '$', 'i'); this.f.push((r) => re.test(String(r[c] ?? ''))); return this; }
    order(c, o = {}) { this.ord = [c, o.ascending !== false]; return this; }
    limit(n) { this.lim = n; return this; }
    range(a, b) { this.rng = [a, b]; return this; }
    single() { this.um = 'single'; return this; }
    maybeSingle() { this.um = 'maybe'; return this; }
    then(ok, falha) { return Promise.resolve().then(() => this.correr()).then(ok, falha); }
    correr() {
      const tab = db[this.t];
      if (!tab) return { data: null, error: { message: `relation "public.${this.t}" does not exist` } };
      if (this.t.startsWith('hub_') && this.op !== 'select') return { data: null, error: { message: `permission denied for table ${this.t}` } };   // só o Hub escreve
      try {
        let linhas;
        if (this.op === 'insert' || this.op === 'upsert') {
          linhas = this.v.map((v) => {
            const n = copia(v);
            if (this.op === 'upsert' && n.id && tab.find((r) => r.id === n.id)) { const r = tab.find((x) => x.id === n.id); Object.assign(r, n); return r; }
            if (this.t === 'perfis') { n.criado_em = agora(); n.notificacoes_vistas_em = agora(); }
            else if (this.t === 'vistos') { n.utilizador_id = ator.id; if (tab.some((r) => r.utilizador_id === n.utilizador_id && r.tipo === n.tipo && r.ref_id === n.ref_id)) throw new Error('duplicate key'); }
            else if (this.t === 'notificacoes_lidas') { Object.assign(n, { utilizador_id: ator.id, lida_em: agora() }); if (tab.some((r) => r.utilizador_id === n.utilizador_id && r.notificacao_id === n.notificacao_id)) throw new Error('duplicate key'); }
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
          const semAnexos = (alvo, ids) => { db.anexos = db.anexos.filter((a) => !(a.alvo === alvo && ids.includes(a.ref_id))); };
          if (this.t === 'checkpoints') {
            const ts = db.tarefas.filter((t) => fora.some((c) => c.id === t.checkpoint_id)).map((t) => t.id);
            const ns = db.tarefas_notas.filter((x) => ts.includes(x.tarefa_id)).map((x) => x.id);
            db.tarefas = db.tarefas.filter((t) => !ts.includes(t.id)); db.tarefas_notas = db.tarefas_notas.filter((x) => !ns.includes(x.id));
            semAnexos('checkpoint', fora.map((c) => c.id)); semAnexos('tarefa', ts); semAnexos('nota', ns);
          }
          if (this.t === 'tarefas') {
            const ns = db.tarefas_notas.filter((x) => fora.some((t) => t.id === x.tarefa_id)).map((x) => x.id);
            db.tarefas_notas = db.tarefas_notas.filter((x) => !ns.includes(x.id));
            semAnexos('tarefa', fora.map((t) => t.id)); semAnexos('nota', ns);
          }
          if (this.t === 'tarefas_notas') semAnexos('nota', fora.map((x) => x.id));
          if (this.t === 'decisoes') db.decisoes_opcoes = db.decisoes_opcoes.filter((o) => !fora.some((d) => d.id === o.decisao_id));
          if (this.t === 'posts') { db.posts_media = db.posts_media.filter((m) => !fora.some((p) => p.id === m.post_id)); db.posts_comentarios = db.posts_comentarios.filter((c) => !fora.some((p) => p.id === c.post_id)); }
          if (this.t === 'posts_media') { fora.forEach((m) => desaprovarFotos(m.post_id)); db.posts_comentarios.forEach((c) => { if (fora.some((m) => m.id === c.media_id)) c.media_id = null; }); }
          if (this.t === 'obras_fases' || this.t === 'obras') throw new Error('permission denied: as fases e as obras não se apagam');
          if (this.t === 'mensagens' && fora.some((m) => m.autor_id !== ator.id)) { db[this.t] = tab; return { data: null, error: null }; }   // RLS: só as minhas
          linhas = fora;
        } else {
          // como o PostgREST: decisoes ↔ decisoes_opcoes têm duas chaves estrangeiras, o embed sem "!<fk>" falha
          if (this.t === 'decisoes' && /decisoes_opcoes\s*\(/.test(this.cols))
            return { data: null, error: { message: "Could not embed because more than one relationship was found for 'decisoes' and 'decisoes_opcoes'" } };
          linhas = tab.filter((r) => this.f.every((f) => f(r)));
          if (this.t === 'vistos' || this.t === 'notificacoes_lidas') linhas = linhas.filter((r) => r.utilizador_id === ator.id);
          if (this.t === 'conversas') linhas = linhas.filter((r) => membro(r.id));
          if (this.t === 'conversas_membros' || this.t === 'mensagens') linhas = linhas.filter((r) => membro(r.conversa_id));
          if (this.ord) { const [c, asc] = this.ord; linhas = [...linhas].sort((a, b) => (a[c] < b[c] ? -1 : a[c] > b[c] ? 1 : 0) * (asc ? 1 : -1)); }
          if (this.lim) linhas = linhas.slice(0, this.lim);
          if (this.rng) linhas = linhas.slice(this.rng[0], this.rng[1] + 1);
          linhas = linhas.map((r) => {
            const c = copia(r);
            for (const [filho, [pai, fk]] of Object.entries(FILHOS)) if (pai === this.t && new RegExp(filho + '(![a-z_]+)?\\s*\\(').test(this.cols)) c[filho] = copia(db[filho].filter((x) => x[fk] === r.id));
            return c;
          });
        }
        if (this.op !== 'select' && linhas.length) avisar(this.t);
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
      rpc: async (fn, a) => {
        const renumerar = (pr, semId, pos) => db.checkpoints.filter((c) => c.projeto === pr && c.id !== semId).sort((x, y) => x.ordem - y.ordem || x.id - y.id)
          .forEach((c, i) => { c.ordem = i + 1 >= pos ? i + 2 : i + 1; });
        if (fn === 'inserir_checkpoint') {
          const n = db.checkpoints.filter((c) => c.projeto === a.p_projeto).length;
          const pos = Math.max(1, Math.min(a.p_posicao || n + 1, n + 1));
          renumerar(a.p_projeto, null, pos);
          const r = await new Q('checkpoints').insert({ projeto: a.p_projeto, titulo: a.p_titulo, descricao: a.p_descricao, ordem: pos }).select().single();
          return { data: r.data && r.data.id, error: r.error };
        }
        if (fn === 'mover_checkpoint') {
          const c = db.checkpoints.find((x) => x.id === a.p_id);
          const n = db.checkpoints.filter((x) => x.projeto === c.projeto).length;
          const pos = Math.max(1, Math.min(a.p_posicao, n));
          renumerar(c.projeto, c.id, pos); c.ordem = pos; avisar('checkpoints');
          return { data: null, error: null };
        }
        if (fn === 'acrescentar_opcao') {
          if (ator.nivel === 'ver' || U.nivel === 'ver') return { data: null, error: { message: 'Sem permissão para editar.' } };
          const d = db.decisoes.find((x) => x.id === a.p_decisao);
          if (!d) return { data: null, error: { message: 'Decisão inexistente.' } };
          if (d.estado !== 'aberta') return { data: null, error: { message: 'Reabre a decisão para lhe acrescentar opções.' } };
          const ordem = 1 + Math.max(0, ...db.decisoes_opcoes.filter((o) => o.decisao_id === d.id).map((o) => o.ordem));
          const o = { id: ++seq.decisoes_opcoes, decisao_id: d.id, titulo: a.p_titulo.trim(), descricao: a.p_descricao, vantagens: a.p_vantagens, desvantagens: a.p_desvantagens, custo: a.p_custo, ordem };
          db.decisoes_opcoes.push(o); avisar('decisoes_opcoes');
          notificar(d.projeto, 'decisao_opcao', `${nomeAtual()} acrescentou a opção «${o.titulo}» à decisão «${d.pergunta}»`, 'decisao', d.id);
          return { data: o.id, error: null };
        }
        if (fn === 'definir_fases') {
          if (U.nivel === 'ver') return { data: null, error: { message: 'Sem permissão para editar.' } };
          const obra = db.obras.find((x) => x.id === a.p_obra);
          for (const e of a.p_estados) {
            const f = db.obras_fases.find((x) => x.id === e.id && x.obra_id === a.p_obra);
            if (!f) return { data: null, error: { message: `A fase ${e.id} não é desta obra.` } };
            if (f.estado !== e.estado) f.concluida_em = e.estado === 'concluida' ? (e.concluida_em || hoje()) : null;
            else if (e.estado === 'concluida' && e.concluida_em) f.concluida_em = e.concluida_em;
            f.estado = e.estado;
          }
          const atual = db.obras_fases.filter((x) => x.obra_id === a.p_obra && x.estado === 'em_curso').sort((x, y) => x.ordem - y.ordem)[0];
          const todas = db.obras_fases.filter((x) => x.obra_id === a.p_obra).every((x) => x.estado === 'concluida');
          notificar(null, 'fase_estado', `${nomeAtual()}${atual ? ` passou a obra ${obra.nome} para a fase «${atual.nome}»` : todas ? ` deu todas as fases da obra ${obra.nome} como concluídas` : ` atualizou as fases da obra ${obra.nome}`}`, 'obra', a.p_obra);
          avisar('obras_fases');
          return { data: null, error: null };
        }
        if (fn === 'abrir_conversa') {   // migração 0018: a conversa direta que já existe, ou uma nova com estas pessoas
          const todos = [...new Set([...(a.p_membros || []), ator.id])].sort();
          if (todos.length < 2) return { data: null, error: { message: 'Escolhe pelo menos uma pessoa.' } };
          if (todos.some((id) => id !== ator.id && !db.perfis.some((p) => p.id === id))) return { data: null, error: { message: 'Só se podem juntar pessoas do hub.' } };
          if (todos.length === 2) {
            const c = db.conversas.find((k) => !k.grupo && !k.claude && db.conversas_membros.filter((m) => m.conversa_id === k.id).map((m) => m.utilizador_id).sort().join() === todos.join());
            if (c) return { data: c.id, error: null };
          }
          const c = { id: ++seq.conversas, titulo: (a.p_titulo || '').trim(), grupo: todos.length > 2, claude: false, criada_por: ator.id, criada_em: agora(), ultima_em: agora() };
          db.conversas.push(c);
          todos.forEach((u) => db.conversas_membros.push({ conversa_id: c.id, utilizador_id: u, lida_em: agora(), entrou_em: agora() }));
          avisar('conversas');
          return { data: c.id, error: null };
        }
        return { data: null, error: { message: `function ${fn} does not exist` } };
      },
      storage: { from: (balde) => (balde === 'social' || balde === 'anexos' || balde === 'chat' ? {
        upload: async (c, f) => { if (social.has(c)) return { data: null, error: { message: 'The resource already exists' } }; social.set(c, URL.createObjectURL(f)); return { data: { path: c }, error: null }; },
        createSignedUrls: async (cs) => ({ data: cs.map((c) => ({ path: c, signedUrl: social.has(c) ? urlSocial(c) : null, error: social.has(c) ? null : 'Object not found' })), error: null }),
        createSignedUrl: async (c) => (social.has(c) ? { data: { signedUrl: urlSocial(c) }, error: null } : { data: null, error: { message: 'Object not found' } }),
        remove: async (lista) => { lista.forEach((c) => social.delete(c)); return { data: lista, error: null }; },
      } : {
        upload: async (caminho, f) => { if (ficheiros.has(caminho)) return { data: null, error: { message: 'The resource already exists' } }; ficheiros.set(caminho, f.size); return { data: { path: caminho }, error: null }; },
        createSignedUrl: async (caminho, s, o) => (ficheiros.has(caminho) ? { data: { signedUrl: `/__ficheiro?c=${encodeURIComponent(caminho)}${o && o.download ? '&download' : ''}` }, error: null } : { data: null, error: { message: 'Object not found' } }),
        remove: async (lista) => { lista.forEach((c) => ficheiros.delete(c)); return { data: lista, error: null }; },
      }) },
      channel: () => {
        const canal = { on: (_, filtro, cb) => { ouvintes.push({ tabela: filtro.table, cb }); return canal; }, subscribe: () => canal };
        return canal;
      },
      auth: {
        getSession: async () => ({ data: { session: ligado ? sessao : null } }),
        signOut: async () => { ligado = false; sessionStorage.setItem('fake-saiu', '1'); return { error: null }; },
        verifyOtp: async () => ({ data: { session: sessao }, error: null }),
      },
    }),
  };
  // nos testes: agir como outra pessoa (acrescentar, concluir…) e ver a base
  window.__fake = {
    db, OUTRO, ficheiros, social, avisar,
    // o Claude (sem sessão) escreve numa conversa
    async comoClaude(conversa_id, texto) { const n = { id: ++seq.mensagens, conversa_id, autor_id: null, autor_nome: 'Claude', texto, anexos: [], criada_em: agora() }; db.mensagens.push(n); depois.mensagens(n, null); avisar('mensagens'); return n; },
    comoEu: (fn) => fn(new Proxy({}, { get: (_, t) => new Q(t) })),
    async comoOutro(fn) { ator = OUTRO; try { return await fn(new Proxy({}, { get: (_, t) => new Q(t) })); } finally { ator = U; } },
  };
})();
