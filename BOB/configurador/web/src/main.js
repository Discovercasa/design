// Configurador DiscoverCasa — prototype: the shape, the m² and the clear height with the base's price, the exterior
// walls 3 m at a time, the interior walls and the floor, the cladding and the roof, the doors and windows — with the
// running total and the 3D turning; and the house built by the engine (the repo's Python in the browser) once the
// walls close it. Step order: user 2026-10-21 ("o menu de paredes interiores seja o step 4 … Passo 5 deverá ser o
// revestimento exterior … No passo 5 inclui também os tipos de cobertura … Passo 6 entra o menu da caixilharia").
// The client never sees the word "módulo" (user 2026-10-20); ?interno=1 shows the company's details.
import { Cena, caixaEstore } from "./cena.js";
import { CATALOGO, PE_DIREITO, acertarVao, arred, centroVao, juncoes, semEstore } from "./colocar.js";
import { FORMAS, area, contorno, escalar, lados, moverLado, mudarLado, porqueInvalida } from "./formas.js";
import { IMAGENS } from "./imagens.js";
import { MATERIAIS, daGrupo, materialTres, previa } from "./materiais.js";
import { paredesPossiveis, proximaParede } from "./paredes.js";
import * as EX from "./exteriores.js";
import * as PI from "./paredesint.js";
import { PRECOS_EXEMPLO, euros, orcamento } from "./precos.js";

const INTERNO = new URLSearchParams(location.search).has("interno");
// step 7 after the doors and windows (user 2026-10-29: "Acrescentar depois do menu de portas e janelas um menu de
// Pérgolas e Garagens e Espaços exteriores que seja necessário construção por exemplo um anexo")
const PASSOS = ["Forma", "Tamanho", "Paredes exteriores", "Paredes interiores", "Exterior e cobertura", "Portas e janelas", "Pérgolas, garagens e anexos"];
const CHAVE = "discovercasa-configurador-prototipo-v2"; // the design in progress, in this browser only
// % — the exposed roof's minimum slope, from sistema_construtivo.json once the engine is up (user 2026-10-21: "A
// inclinação mínima da cobertura à vista é 15 %")
let INCLINACAO_MIN = 15;
// the roof types (user 2026-10-21: hidden, or exposed in sandwich panel — 2 águas the rule, 4 an option); the names
// (user 2026-10-22: "escondida, duas águas com empenas à vista e sem empenas ou várias águas, sem epenas à vista e
// várias águas, com empenas à vista"; 2026-10-27 "Quero também com duas águas e depois várias águas"; 2026-10-28
// "Deixa duas águas e várias águas apenas com empenas á vista" — spec §13): a rectangle, Escondida · Duas águas com
// empenas; an L / T / U, Escondida · Duas águas com empenas (every end a gable) · Várias águas com empenas (the main
// body hipped, the wings' ends gables — "misto", our reading). The roofs without gables (every end hipped, the
// engine's "quatro_aguas") are no longer offered; a design kept with one opens with the nearest card
// "Oculta" on the screen, the same roof as "escondida" (user 2026-10-29: "muda o nome para este termo "Oculta" em vez
// de escondida, sendo que ambas são a mesma coisa mas é para ficar mais profissional no online builder"); the saved
// designs and the engine keep the key "escondida"
const COBERTURAS = {
  escondida: { nome: "Oculta", nota: "atrás da platibanda, com a caleira por dentro", img: "escondida" },
  duas_aguas: { nome: "Duas águas, com empenas à vista", nota: "empenas (triângulos) nas pontas", img: "duas_aguas" },
  misto: { nome: "Várias águas, com empenas à vista", nota: "corpo com rincões, alas com empenas", img: "misto" },
};
const ORDEM_COB = { ret: ["escondida", "duas_aguas"], varias: ["escondida", "duas_aguas", "misto"] };
const BEIRADO = { min: 0.2, max: 0.5 }; // user 2026-10-22: "O mínimo de beirado possível é 20 cm"; max 2026-10-28: "Beirado vamos definir um máximo de 50 cm"
const $ = (s) => document.querySelector(s);
const m2 = (v) => v.toFixed(2).replace(".", ",");
const painel = $("#painel");
const cena = new Cena($("#tela"));
const motor = new Worker(new URL("./motor.worker.js", import.meta.url), { type: "module" });

const est = {
  passo: 1, forma: null, cont: null, pe: PE_DIREITO.inicial, erroBase: "", erro: "", avisos: [],
  paredes: [], ladoEscolhido: null, ultima: null,
  interiores: [], vaos: [],
  acabamentos: { exterior: "A", pavimento: "vinilico" },
  pavimentos: [],   // the floor of a room: [{ponto: [x, y] inside it, material}] (user 2026-10-22: per room)
  facesExt: {},     // the finish of an outside wall's inner face, by side (user 2026-10-22)
  desenho: null,    // drawing interior walls: where the next one starts (paredesint.inicio), or null
  cobertura: { tipo: "escondida", inclinacao: INCLINACAO_MIN, beirado: 0.25 },
  verCobertura: true, ferramenta: null, pincel: null, sel: null, arr: null, menu: null, prox: 1,
  ambas: false,     // the HUD's "Aplicar às duas faces", kept ticked while the client paints
  verTeto: false, teto: null, // the false ceiling shown, and its pieces from the engine (worker teto_casa)
  // step 7: the pergolas [{id, lado, s0, s1, projecao, altura (null = the highest)}] and the garages / annexes
  // [{id, tipo, modo "junto" (part of the house: rect, ligacao (the wall with the door into the house), base) |
  // "separado" (a building of its own: x, y, rot, largura, profundidade, cobertura)}]; form7 = what the panel is set
  // to add; sep = the engine's answer for each separate building (not kept)
  exteriores: { pergolas: [], blocos: [] }, form7: null, sep: {}, regrasPergola: null,
  G: null, aCalcular: false, motorPronto: false, resultado: null, verEstrutura: false, materiais: {}, faces: null, zBeirado: null,
};

// ---------------------------------------------------------------- engine
let pedido = 0, pedidoTelhado = 0, pedidoCob = 0, adiado = null, adiadoCob = null;
const idsPergolas = {}; // per roof request, the pergolas' ids in the order sent
motor.onmessage = (ev) => {
  const m = ev.data;
  if (m.tipo === "pronto") {
    est.motorPronto = true;
    est.materiais = m.materiais || {};
    est.foraPorOpcao = (m.regras && m.regras.fora) || {}; // each cladding's depth outside the base edge
    est.regrasPergola = (m.regras && m.regras.pergola) || null; // the pergola's limits (JSON pergola)
    pedirEdificios();
    if (m.regras && m.regras.inclinacao_min_avista_pct) {
      INCLINACAO_MIN = m.regras.inclinacao_min_avista_pct;
      est.cobertura.inclinacao = Math.max(est.cobertura.inclinacao, INCLINACAO_MIN);
    }
    estado(`Motor pronto (${(m.ms / 1000).toFixed(1)} s)`);
    pedirTelhado();
    cena3D();
    desenhar();
  } else if (m.tipo === "estrutura" && m.pedido === pedido) {
    const d = JSON.parse(m.dados);
    est.aCalcular = false;
    est.G = d.G;
    cena.estrutura(d.G, d.materiais, mapearDe(d.rodada));
    const mods = d.G.paineis.filter((p) => p.piso === 0 && !p.fantasma && (p.tipo === "PE" || p.tipo === "PI"));
    est.resultado = {
      ms: m.ms, ext: mods.filter((p) => p.tipo === "PE").length, int: mods.filter((p) => p.tipo === "PI").length,
      notas: d.notas, resumo: d.resumo, avisos: paraOCliente(d.G.avisos_divisor || []), avisosInternos: d.G.avisos_divisor || [],
    };
    // the openings the engine moved (a pier between two windows) now show where they will be built
    let moveu = false;
    for (const mv of d.movidas || []) {
      const v = est.vaos.find((x) => x.lado === mv.lado && Math.abs(x.centro - mv.de) < 0.02);
      if (v) { v.centro = Math.round(mv.para * 1000) / 1000; moveu = true; }
    }
    if (moveu) { guardarLocal(); cena3D(); }
    estado(`Estrutura calculada pelo método DiscoverCasa em ${(m.ms / 1000).toFixed(1)} s`);
    desenhar();
  } else if (m.tipo === "telhado" && m.pedido === pedidoTelhado) {
    est.faces = m.faces;
    est.zBeirado = m.zBeirado ?? null;
    cena3D();
    if (est.passo === 5) desenhar();
  } else if (m.tipo === "cobertura" && m.pedido === pedidoCob) {
    est.cob = { objetos: m.objetos, zPlat: m.z_platibanda ?? null, rodada: m.rodada, umaAgua: !!m.uma_agua, caleira: m.caleira || null,
      caleiras: m.caleiras || [], plat: m.platibandas || {}, pergolas: m.pergolas || [], pergolaMax: m.pergola_max ?? null,
      pergolaIds: idsPergolas[m.pedido] || [], pergolasMax: m.pergolas_max || [] };
    cena3D();
    if (est.passo === 5) desenhar();
  } else if (m.tipo === "edificio" && pedidosEd[m.id] === m.pedido) { // a separate garage / annex, as built
    est.sep[m.id] = { objetos: m.objetos, zPlat: m.z_platibanda ?? null, rodada: m.rodada, plat: m.platibandas || {},
      faces: m.faces, zBeirado: m.z_beirado ?? null, caleiras: m.caleiras || [], caleira: m.caleira || null,
      chave: est.sep[m.id] && est.sep[m.id].chave };
    cena3D();
    if (est.passo === 7) desenhar();
  } else if (m.tipo === "erro_edificio" && pedidosEd[m.id] === m.pedido) {
    est.sep[m.id] = { erro: m.msg, chave: est.sep[m.id] && est.sep[m.id].chave };
    console.warn("edifício:", m.msg);
  } else if (m.tipo === "erro" && m.pedido === -1e6 - pedidoCob) {
    est.cob = null;
    console.warn("cobertura:", m.msg);
  } else if (m.tipo === "teto" && m.pedido === pedidoTeto) {
    est.teto = { objetos: m.objetos, rodada: m.rodada };
    cena3D();
  } else if (m.tipo === "erro" && m.pedido === -2e6 - pedidoTeto) {
    est.teto = null;
    console.warn("teto:", m.msg);
  } else if (m.tipo === "erro" && m.pedido === undefined) {
    estado(`O motor não arrancou: ${m.msg}`);
    console.error("motor:", m.msg);
  } else if (m.tipo === "erro" && m.pedido === pedido) {
    est.aCalcular = false;
    estado("Não foi possível calcular a estrutura");
    est.resultado = { erro: m.msg };
    desenhar();
  } else if (m.tipo === "erro" && m.pedido === -pedidoTelhado) {
    est.faces = null;
    console.warn("telhado:", m.msg);
  }
};
motor.onerror = (e) => { estado(`O motor não arrancou: ${e.message || "erro no worker"}`); console.error("motor:", e); };
motor.postMessage({ tipo: "carregar" });

// the false ceiling from the engine (worker teto_casa — camadas.tetos, never a plane drawn here), asked only while shown
let pedidoTeto = 0, adiadoTeto = null;
function pedirTeto() {
  clearTimeout(adiadoTeto);
  if (!est.verTeto || (est.teto && !est.teto.velho) || !est.motorPronto || !est.cont || !fechada()) return;
  adiadoTeto = setTimeout(() => {
    pedidoTeto += 1;
    motor.postMessage({ tipo: "teto", pedido: pedidoTeto, casa: casaConfigurada() });
  }, 400);
}

// each separate garage / annex computed by the engine as a house of its own (exteriores.casaSeparada)
const pedidosEd = {};
let adiadoEd = null;
function pedirEdificios() {
  clearTimeout(adiadoEd);
  if (!est.motorPronto || !est.cont || !fechada()) return;
  adiadoEd = setTimeout(() => {
    const casa = casaConfigurada();
    for (const e of est.exteriores.blocos.filter((b) => b.modo === "separado")) {
      const chave = JSON.stringify([e.largura, e.profundidade, e.tipo, e.cobertura, casa.acabamentos, casa.pe_direito]);
      if (est.sep[e.id] && est.sep[e.id].chave === chave) continue;
      pedidosEd[e.id] = (pedidosEd[e.id] || 0) + 1;
      est.sep[e.id] = { ...(est.sep[e.id] || {}), chave, velho: true };
      motor.postMessage({ tipo: "edificio", id: e.id, pedido: pedidosEd[e.id], casa: EX.casaSeparada(e, casa) });
    }
  }, 350);
}

function construirComMetodo() {
  est.aCalcular = true;
  pedido += 1;
  estado("A calcular a casa pelo método DiscoverCasa…");
  motor.postMessage({ tipo: "construir", pedido, casa: casaConfigurada() });
  desenhar();
}

// the engine's plan -> the screen's (a hidden roof's house may be turned 90° for the ceiling beams)
function mapearDe(rodada) {
  const Y = Math.max(...est.cont.map((p) => p[1]));
  return rodada ? (xr, yr) => [yr, Y - xr] : (x, y) => [x, y];
}

// the side (index) a compass word names: the longest side facing it on the outline's edge (+y north)
function ladoDaBussola(b) {
  const [nx, ny] = { norte: [0, 1], sul: [0, -1], nascente: [1, 0], poente: [-1, 0] }[b];
  const ls = lados(est.cont).filter((l) => Math.abs(l.n[0] - nx) < 1e-6 && Math.abs(l.n[1] - ny) < 1e-6);
  const fim = Math.max(...ls.map((l) => l.p0[0] * nx + l.p0[1] * ny));
  return ls.filter((l) => Math.abs(l.p0[0] * nx + l.p0[1] * ny - fim) < 1e-6).sort((a, b2) => b2.comprimento - a.comprimento)[0].i;
}

// the roof comes from the engine (the roof is the method's — never drawn by a copy of its rules here): the exposed
// roof's faces at once, then the whole roof as built a moment later (gutters, downpipes, caps, the hidden roof's
// slopes and the parapets' height — camadas.py); `novo` when the design changed (the old pieces go)
function pedirTelhado(novo = false) {
  // only for a closed house: the converter refuses a side its walls do not close yet (step 3 halfway)
  if (!est.cont || !est.motorPronto || !fechada()) { est.faces = null; est.zBeirado = null; est.cob = null; return; }
  if (novo) est.cob = null;
  if (est.cobertura.tipo !== "escondida") {
    pedidoTelhado += 1;
    motor.postMessage({ tipo: "telhado", pedido: pedidoTelhado, casa: casaConfigurada() });
  } else { est.faces = null; est.zBeirado = null; }
  clearTimeout(adiadoCob);
  adiadoCob = setTimeout(() => {
    pedidoCob += 1;
    idsPergolas[pedidoCob] = est.exteriores.pergolas.map((p) => p.id); // the engine answers in this order
    motor.postMessage({ tipo: "cobertura", pedido: pedidoCob, casa: casaConfigurada() });
  }, 300);
}

// the divider's notes in the client's words (no "módulo"): exterior walls P01.. are the sides in order
function paraOCliente(avisos) {
  const n = est.cont ? est.cont.length : 0;
  return avisos.map((a) => {
    const k = Number((a.match(/^P(\d+):/) || [])[1]), lado = k && k <= n ? `No lado ${k}` : "Numa parede interior";
    let r = a.match(/afastados ([\d.]+) cm para um pilar/);
    if (r) return `${lado}, dois vãos muito juntos foram afastados ${m2(Number(r[1]) / 100)} m para caber o pilar entre eles.`;
    r = a.match(/afastado ([\d.]+) cm do topo/);
    if (r) return `${lado}, um vão foi afastado ${m2(Number(r[1]) / 100)} m da ponta da parede.`;
    if (/porta junto a outro vão/.test(a)) return `${lado}, uma porta ficou junto a outro vão: vamos confirmar a melhor solução.`;
    return null;
  }).filter(Boolean);
}

// the configured house (format discovercasa-configurador/1 — configurador/docs/especificacao.md §8)
function casaConfigurada() {
  const c = est.cobertura;
  return {
    formato: "discovercasa-configurador/1", nome: "Casa configurada", obra: "CFG",
    base: { forma: est.forma, contorno: est.cont },
    paredes_exteriores: est.paredes.map(({ lado, s0, s1 }) => ({ lado, s0, s1 })),
    vaos: est.vaos.map((v) => ({
      lado: v.lado, tipo: v.tipo, centro: v.centro, largura: v.largura, altura: v.altura,
      ...(CATALOGO[v.tipo].chao ? {} : { peitoril: v.peitoril }), estore: !!v.estore && !semEstore(v.tipo), ...(v.vidro ? { vidro: v.vidro } : {}), divisao: "",
    })),
    paredes_interiores: rs().filter((r) => !PI.porqueNao(est.cont, est.vaos, rs(), r)).map((r) => ({
      de: r.de, ate: r.ate, portas: r.portas.map((p) => ({ centro: Math.round((p.s - r.a) * 1000) / 1000 })),
      faces: r.o === "h" ? { norte: r.faces.pos, sul: r.faces.neg } : { nascente: r.faces.pos, poente: r.faces.neg },
    })),
    cobertura: c.tipo === "escondida" ? { tipo: "escondida", ...(c.caleira ? { lado_caleira: c.caleira } : {}) } : { tipo: c.tipo, inclinacao_pct: c.inclinacao, beirado: c.beirado, painel: "sandwich" },
    acabamentos: { exterior: est.acabamentos.exterior, pavimento: est.acabamentos.pavimento }, pe_direito: est.pe,
    // the floor of each room the client set apart from the house's (a point well inside it — its label's)
    pavimentos: ds().filter((d) => pavDe(d) !== est.acabamentos.pavimento).map((d) => ({ ponto: d.rotulo, acabamento: pavDe(d) })),
    faces_interiores: Object.fromEntries(Object.entries(est.facesExt).filter(([, m]) => m && m !== "pladur")),
    // step 7: the pergolas (the engine builds them, pergola.py); an attached garage / annex is already in the outline,
    // a separate one is a configured house of its own (exteriores.casaSeparada), kept here with its place
    exteriores: {
      pergolas: est.exteriores.pergolas.map(({ lado, s0, s1, projecao, altura }) => ({ lado, s0, s1, projecao, altura })),
      separados: est.exteriores.blocos.filter((b) => b.modo === "separado").map(({ tipo, x, y, rot, largura, profundidade, cobertura, portao }) => ({ tipo, x, y, rot, largura, profundidade, cobertura, ...(portao ? { portao } : {}) })),
    },
  };
}

// the rooms (the floor between the walls) and the floor finish of each
const ds = () => (est.cont && fechada() ? PI.divisoes(est.cont, rs()) : []);
function pavDe(d) {
  for (let i = est.pavimentos.length - 1; i >= 0; i--) if (PI.divisaoEm([d], est.pavimentos[i].ponto)) return est.pavimentos[i].material;
  return est.acabamentos.pavimento;
}

// ---------------------------------------------------------------- state helpers
const fechada = () => !!est.cont && est.paredes.length === paredesPossiveis(lados(est.cont)).length;
const rs = () => (est.cont ? PI.resolver(est.cont, est.interiores) : []);
// to the parapet top (hidden roof: the engine's — the parapet rises to hide the ridge, user 2026-10-28 "deve estar a
// altura correta que vai ficar para ter essas inclinações"; TV 2,50 -> 3,50) or to the eaves line (exposed: the
// engine's); an estimate only until the engine answers
const alturaExt = () => (est.cobertura.tipo === "escondida" ? (est.cob && est.cob.zPlat) || est.pe + 1.0 : est.zBeirado ?? est.pe + 0.36);
const matDe = (id) => materialTres(id, est.materiais);
const vaoDe = (id) => est.vaos.find((v) => v.id === id);
const paredeDe = (id) => est.interiores.find((w) => w.id === id);
const casaRet = () => est.cont && est.cont.length === 4;
const nomeCob = (k) => COBERTURAS[k].nome;
// a roof card this shape offers: the hipped roof of an older design ("quatro_aguas") becomes the nearest one with
// gables, and the wings' roof ("misto") on a rectangle its 2 águas
function acertarCobertura() {
  const c = est.cobertura, ret = casaRet();
  if (c.tipo === "quatro_aguas") c.tipo = ret ? "duas_aguas" : "misto";
  if (ret && c.tipo === "misto") c.tipo = "duas_aguas";
  if (!COBERTURAS[c.tipo]) c.tipo = "escondida";
}
const escondida = () => est.cobertura.tipo === "escondida";

function zFrame(v) {
  return CATALOGO[v.tipo].chao ? { z0: 0, z1: v.altura } : { z0: v.peitoril, z1: v.peitoril + v.altura };
}

function mudou(telhado = false, doHistorico = false) {
  est.G = null;
  est.resultado = null;
  if (est.teto) est.teto.velho = true; // shown until the engine's new one comes
  pedirTeto();
  if (!doHistorico) registar();
  guardarLocal();
  if (telhado) pedirTelhado(true);
  else if (est.passo >= 5) pedirTelhado(); // an opening may raise the exterior modules, and the roof with them
  pedirEdificios();
  if (est.verEstrutura && fechada()) {
    clearTimeout(adiado);
    adiado = setTimeout(construirComMetodo, 350);
    return;
  }
  cena.estrutura(null);
  if (est.verEstrutura) { // the house is open again: back to the client's walls
    est.verEstrutura = false;
    mostrar("estrutura", false);
    mostrar("paredes", true);
  }
}

function guardarLocal() {
  try {
    const { passo, forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt, exteriores } = est;
    localStorage.setItem(CHAVE, JSON.stringify({ v: 3, passo, forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt, exteriores }));
  } catch { /* no storage here: the design simply is not kept */ }
}

// ---------------------------------------------------------------- undo / redo: the design's states, every change of
// it passes through mudou() (dragging shows only the picture and comes here once, at the end)
const HIST = { atras: [], frente: [], atual: null, max: 100 };
function instantaneo() {
  const { forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt, exteriores } = est;
  return JSON.stringify({ forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt, exteriores });
}
function botoesHistorico() {
  $("#desfazer").disabled = !HIST.atras.length;
  $("#refazer").disabled = !HIST.frente.length;
}
function registar() {
  const s = instantaneo();
  if (s === HIST.atual) return;
  if (HIST.atual !== null && JSON.parse(HIST.atual).cont) { // never back to "no house yet"
    HIST.atras.push(HIST.atual);
    if (HIST.atras.length > HIST.max) HIST.atras.shift();
  }
  HIST.atual = s;
  HIST.frente = [];
  botoesHistorico();
}
function historico(passo) { // -1 undo, +1 redo; the step on the screen stays
  const de = passo < 0 ? HIST.atras : HIST.frente, para = passo < 0 ? HIST.frente : HIST.atras;
  if (!de.length) return;
  para.push(HIST.atual);
  HIST.atual = de.pop();
  Object.assign(est, JSON.parse(HIST.atual), { sel: null, ferramenta: null, pincel: null, menu: null, arr: null, desenho: null, erro: "", avisos: [] });
  if (est.verEstrutura && !fechada()) verEstrutura(false);
  cena.previa(null);
  cena.base(est.cont);
  cotas(est.cont);
  mudou(true, true);
  cena3D();
  desenhar();
  botoesHistorico();
}

function repor(d) {
  if (!d || (d.v !== 2 && d.v !== 3) || !d.cont) return false;
  if (d.v === 2 && d.cobertura && d.cobertura.inclinacao) // version 2 kept the slope in degrees, version 3 in %
    d.cobertura.inclinacao = Math.round(Math.tan((d.cobertura.inclinacao * Math.PI) / 180) * 100);
  Object.assign(est, {
    passo: d.passo || 2, forma: d.forma, cont: d.cont, pe: d.pe || PE_DIREITO.inicial, paredes: d.paredes || [],
    vaos: d.vaos || [], interiores: d.interiores || [], acabamentos: { ...est.acabamentos, ...(d.acabamentos || {}) },
    cobertura: { ...est.cobertura, ...(d.cobertura || {}) }, prox: d.prox || 1,
    pavimentos: d.pavimentos || [], facesExt: d.facesExt || {}, desenho: null,
    exteriores: { pergolas: [], blocos: [], ...(d.exteriores || {}) }, form7: null,
    sel: null, ferramenta: null, pincel: null, G: null, resultado: null, verEstrutura: false, cob: null,
  });
  // a design kept before 2026-10-22 may hold an eave outside 0,20-0,50 (0,55 until 2026-10-28); before 2026-10-28 a roof without gables
  est.cobertura.beirado = Math.min(BEIRADO.max, Math.max(BEIRADO.min, est.cobertura.beirado ?? 0.25));
  acertarCobertura();
  cena.base(est.cont);
  cena.enquadrar(est.cont);
  return true;
}

// ---------------------------------------------------------------- the base: a shape, then its area and its sides
function escolherForma(forma) {
  est.forma = forma;
  est.erroBase = "";
  novaBase(contorno(forma, 120));
  cena.enquadrar(est.cont);
}

// a new outline (from the area, a typed side or a dragged side): kept only if it is a valid house
function novaBase(cont, mostrarSo = false) {
  const erro = porqueInvalida(cont);
  if (erro) {
    est.erroBase = `Não é possível: ${erro}.`;
    if (!mostrarSo) { cena.base(est.cont); cotas(est.cont); desenhar(); } // back to the last valid base
    return false;
  }
  est.erroBase = "";
  cena.base(cont);
  cotas(cont);
  if (mostrarSo) return true; // while dragging: only the picture
  est.cont = cont;
  acertarCobertura();
  est.paredes = [];
  est.vaos = [];
  est.interiores = [];
  est.sel = null;
  mudou(true);
  cena3D();
  return true;
}

function cotas(cont) {
  if (!cont) return;
  const editavel = est.passo === 2;
  cena.cotas(lados(cont).map((l) => ({ i: l.i, meio: [(l.p0[0] + l.p1[0]) / 2, (l.p0[1] + l.p1[1]) / 2], n: l.n, valor: l.comprimento })),
    editavel ? (i, v) => { if (v > 0) { novaBase(mudarLado(est.cont, i, v)); desenhar(); } } : null);
  cena.editar(editavel ? {
    lados: lados(cont),
    aoArrastar: (i, d, fim) => {
      const novo = moverLado(est.cont, i, d);
      if (fim) { if (!novaBase(novo)) novaBase(est.cont, true); desenhar(); } else novaBase(novo, true);
    },
  } : null);
}

function mudarPe(v) {
  const pe = Math.min(PE_DIREITO.max, Math.max(PE_DIREITO.min, arred(v, PE_DIREITO.passo)));
  est.pe = pe;
  est.avisos = [];
  est.vaos = est.vaos.map((x) => acertarVao(x, pe, est.avisos, escondida()));
  mudou(true);
  cena3D();
}

// ---------------------------------------------------------------- the 3D picture of the client's house
function cena3D() {
  const cont = est.cont;
  if (!cont) return;
  const H = alturaExt(), fe = fechada();
  const vs = fe ? est.vaos.map((v) => ({ ...v, s0: v.centro - v.largura / 2, s1: v.centro + v.largura / 2, ...zFrame(v) })) : [];
  const furos = vs.map((v) => ({ ...v, z1: v.z1 + caixaEstore(v) })); // the wall's hole holds the shutter box too
  // the hidden roof shown: the parapets' roof side, from above the ceiling, in the facade's own cladding (user
  // 2026-10-28: "o capoto tem que ficar na casa toda a cobertura não tem um revestimento ou isolamento diferente")
  const parapeito = fe && est.passo >= 5 && est.verCobertura && est.cobertura.tipo === "escondida" ? est.pe + 0.3 : null;
  cena.fora = (est.foraPorOpcao && est.foraPorOpcao[est.acabamentos.exterior]) || 0.09; // the chosen cladding's depth
  // the parapet as wide as the engine builds it — the chapéu covers exactly that (user 2026-10-29: "o chapéu não esta a
  // cobrir a largura toda")
  const dentroPlat = (lado) => (parapeito && est.cob && est.cob.plat ? est.cob.plat[lado] : null);
  cena.paredes(cont, est.paredes, { altura: H, material: matDe(est.acabamentos.exterior), ultima: est.passo === 3 ? est.ultima : null, vaos: furos, parapeito, dentroPlat,
    interior: (lado) => matDe(est.facesExt[lado] || "pladur"), selLado: est.passo === 4 && est.sel && est.sel.tipo === "exterior" ? est.sel.lado : null });
  cena.vaos(cont, vs, est.sel && est.sel.tipo === "vao" ? est.sel.id : null);
  cena.interiores(rs(), est.pe, { sel: est.sel && { ...est.sel, ambas: est.ambas, troco: trocoSel() }, matDe });
  if (est.ferramenta !== "parede") medidasSelecao(); // (while drawing: pairarDesenho's)
  cena.teto(fe && est.verTeto && est.teto ? est.teto.objetos : null, est.materiais, est.teto ? mapearDe(est.teto.rodada) : undefined);
  if (fe && est.passo >= 4) {
    const lista = ds(), selD = est.sel && est.sel.tipo === "divisao" ? lista.indexOf(PI.divisaoEm(lista, est.sel.ponto)) : null;
    cena.divisoes(lista, { matDe: (i) => matDe(pavDe(lista[i])), sel: selD, rotulos: est.passo === 4 });
  } else cena.chao(null);
  if (!fe || est.passo < 4) cena.telhado(null);
  else if (est.cobertura.tipo === "escondida") {
    if (est.cob) cena.limpar("telhado"); else cena.telhado(cont, H - 0.45, matDe("sandwich")); // until the engine answers
  } else cena.telhadoFaces(est.faces, matDe("sandwich"));
  if (fe && est.passo >= 4 && est.cob) cena.pecasCobertura(est.cob.objetos, est.materiais, mapearDe(est.cob.rodada));
  cena.empenas(fe && est.cobertura.tipo !== "escondida" ? cont : null, est.faces, H, matDe(est.acabamentos.exterior));
  // step 7: the pergolas as the engine builds them (by id: the engine answers for the list it was sent) and the
  // separate garages / annexes
  const pgs = fe && est.cob && est.cob.pergolas ? est.exteriores.pergolas.map((p) => {
    const k = (est.cob.pergolaIds || []).indexOf(p.id);
    return { id: p.id, objetos: k >= 0 ? est.cob.pergolas[k] || [] : [] };
  }) : [];
  cena.pergolas(pgs, est.materiais, est.cob ? mapearDe(est.cob.rodada) : undefined, est.sel && est.sel.tipo === "pergola" ? est.sel.id : null);
  desenharSeparados();
  cena.mostrar("telhado", est.verCobertura && !est.verEstrutura);
  hud();
}

// ---------------------------------------------------------------- step 4: interior walls, their faces, the floor
// which face of interior wall r a point (on it) is on
const faceDe = (r, ponto) => (ponto && (r.o === "h" ? ponto[1] : ponto[0]) < r.c ? "neg" : "pos");

// the piece of the selected interior wall clicked, between the walls that meet it (user 2026-10-29: "deve ser possível
// selecionar apenas esse "pedaço" de parede interior"): [s0, s1], or null when nothing meets it on the way
function trocoSel() {
  const s = est.sel;
  if (!s || s.tipo !== "interior" || s.s === undefined) return null;
  const lista = rs(), r = lista.find((x) => x.id === s.id);
  return r && PI.trocos(lista, r).length > 1 ? PI.trocoEm(lista, r, s.s) : null;
}

function pertoDe(p) { // the interior wall (or its door) near a floor point: a 13 cm wall is thin to click from above
  if (!p) return null;
  let melhor = null;
  for (const r of rs()) {
    const { c, s } = PI.naParede(r.o, p), d = Math.abs(c - r.c);
    if (d > 0.35 || s < r.a || s > r.b || (melhor && d >= melhor.d)) continue;
    const pt = r.portas.find((q) => Math.abs(q.s - s) <= 0.435);
    melhor = { d, alvo: pt ? { porta: pt.id, interior: r.id } : { interior: r.id } };
  }
  return melhor && melhor.alvo;
}

function pintar(id, face, material) { // a finish on one face (or both) of an interior wall
  const w = paredeDe(id);
  if (!w) return;
  w.faces = face === "ambas" ? { pos: material, neg: material } : { ...w.faces, [face]: material };
  mudou();
  cena3D(); desenhar();
}

// the selected wall's distances to the ends of the wall it starts on, typed on the floor to move it there (user
// 2026-10-28: "a pessoa quer começar uma divisória precisamente a 4 metros desse canto")
function medidasSelecao() {
  const s = est.sel, r = est.passo === 4 && !est.verEstrutura && s && s.tipo === "interior" ? rs().find((x) => x.id === s.id) : null;
  const v = est.passo === 6 && !est.verEstrutura && s && s.tipo === "vao" ? vaoDe(s.id) : null;
  if (v) { // a window / door chosen: its distances to the nearest axes, typed to move it
    const ms = medidasVao(v.lado, v.centro - v.largura / 2, v.centro + v.largura / 2);
    cena.medidas(ms, (i, val) => posicionarVao(v.id, ms[i], val));
    return;
  }
  if (!r) { cena.medidas(null); return; }
  const ref = r.ini.tipo !== "livre" ? r.ini : r.fim;
  const ms = PI.aosCantos(est.cont, rs(), ref, r.c, ref === r.refA ? 1 : -1);
  cena.medidas(ms, (i, v) => posicionar(r.id, ms[i], v));
}

function posicionar(id, m, v) { // wall id moved across so that it stands v from the end m.canto
  const w = paredeDe(id);
  if (!w || !m || !Number.isFinite(v) || v < 0) { cena3D(); return; }
  const d = [(m.ponto[0] - m.canto[0]) / m.valor, (m.ponto[1] - m.canto[1]) / m.valor];
  const p = [m.canto[0] + d[0] * v, m.canto[1] + d[1] * v], c0 = w.c;
  w.c = Math.round((w.o === "h" ? p[1] : p[0]) * 1000) / 1000;
  const erro = PI.porqueNaoTodas(est.cont, est.vaos, est.interiores);
  if (erro) { w.c = c0; est.erro = `Assim não: ${erro}.`; } else { est.erro = ""; mudou(); }
  cena3D(); desenhar();
}

// ---- drawing interior walls by clicks (user 2026-10-22: "quando seleciono a tool de parede interior não quero ter que
// arrastar posso simplesmente clicar nela e no sítio … snap também para as extremidades das paredes"): a click on a wall
// (or on a wall's free end: a corner) starts it, the next click ends it; drawing goes on from its free end until a wall
// meets another (a room closed); Esc stops
// the distances from a start on a wall to that wall's ends (user 2026-10-28: "deve dizer a distância de cada canto"):
// not at a corner or a free end, where they are the walls' own lengths
const aosCantos = (ini) => (ini && !ini.ponta && !ini.opcoes ? PI.aosCantos(est.cont, rs(), ini.ref, ini.c, ini.dentro) : null);

function pairarDesenho(info) {
  if (!info.chao) { cena.previa(null); cena.marca(null); cena.medidas(null); return; }
  const lista = rs();
  if (!est.desenho) {
    const ini = PI.inicio(est.cont, lista, info.chao);
    cena.previa(null);
    cena.marca(ini ? ini.ponto : null);
    cena.medidas(aosCantos(ini));
    cena.cursor(ini ? "crosshair" : "not-allowed");
    return;
  }
  const ini = PI.sentido(est.desenho, info.chao); // from a corner or a free start: along the way the pointer goes
  const { w, fecha } = PI.segmento(est.cont, lista, ini, info.chao, -1, est.desenho.origem);
  const nova = PI.comNova(est.interiores, ini, w);
  const r = PI.resolver(est.cont, nova).find((x) => x.id === -1);
  const erro = PI.porqueNaoTodas(est.cont, est.vaos, nova, ini.ref.tipo === "livre" ? -1 : null);
  if (!r) { cena.previa(null); cena.marca(null); cena.medidas(null); return; }
  const longe = Math.abs(r.a - ini.s0) < Math.abs(r.b - ini.s0) ? r.b : r.a;
  // in line with the first point of the walls being drawn: a dashed line to it — the next wall closes the room
  const guia = fecha && !erro ? [PI.pt(r.o, r.c, longe), est.desenho.origem] : null;
  cena.previa({ tipo: "parede", o: r.o, c: r.c, a: r.a, b: r.b, pe: est.pe, guia }, !!erro);
  cena.marca(PI.pt(r.o, r.c, longe), !!erro);
  cena.medidas(aosCantos(est.desenho)); // (from a corner: none)
  cena.cursor("crosshair");
  est.erro = erro ? `Aqui não: ${erro}.` : "";
  const er = $("#erro"); if (er) er.textContent = est.erro;
}

// the drawing stops (Esc, another tool, another step): a room's first wall left alone in the middle of the house, both
// ends free, goes — a wall touches another one
function pararDesenho() {
  const id = est.desenho && est.desenho.solta, w = id != null ? paredeDe(id) : null;
  est.desenho = null;
  if (w && w.ini.tipo === "livre" && w.fim.tipo === "livre") {
    est.interiores = est.interiores.filter((x) => x.id !== id);
    est.erro = "A parede solta saiu: no meio da casa, desenhe a divisão de seguida, parede a parede, até a fechar.";
    mudou();
  }
}

function colocarSegmento(info) {
  const ini = PI.sentido(est.desenho, info.chao), { origem } = est.desenho;
  const { w, junta } = PI.segmento(est.cont, rs(), ini, info.chao, est.prox, origem);
  const nova = PI.comNova(est.interiores, ini, w);
  const solta = ini.ref.tipo === "livre" ? w.id : est.desenho.solta; // a room's first wall in the middle of the house
  const erro = PI.porqueNaoTodas(est.cont, est.vaos, nova, ini.ref.tipo === "livre" ? w.id : null);
  if (erro) { est.erro = `Aqui não: ${erro}.`; desenhar(); return; }
  est.interiores = nova;
  est.prox += 1;
  const seguir = junta ? null : PI.pontaLivre(est.cont, est.interiores, w.id); // go on from its free end
  est.desenho = seguir && { ...seguir, origem, solta };
  est.sel = null;
  est.erro = "";
  mudou();
  cena3D(); desenhar();
  pairarDesenho(info);
}

const interacaoInteriores = {
  premir(info) {
    est.erro = "";
    if (est.ferramenta === "parede") { // drawing: clicks only (no drag)
      if (!info.chao) return false;
      if (!est.desenho) {
        const ini = PI.inicio(est.cont, rs(), info.chao);
        if (!ini) { est.erro = "Comece dentro da casa."; desenhar(); return false; }
        est.desenho = { ...ini, origem: ini.ponto };
        pairarDesenho(info);
      } else colocarSegmento(info);
      return false;
    }
    const a0 = info.alvo && info.alvo.divisao === undefined ? info.alvo : null;
    const a = (a0 && a0.lado === undefined && a0) || pertoDe(info.chao);
    if (est.pincel) { // a finish picked in the menu: it goes on the face clicked, once (then clicks select again)
      const m = est.pincel;
      est.pincel = null;
      if (a && a.interior !== undefined && a.porta === undefined) {
        const r = rs().find((x) => x.id === a.interior);
        pintar(r.id, faceDe(r, info.ponto || info.chao), m);
        return false;
      }
      if (a0 && a0.lado !== undefined) { pintarExterior(a0.lado, m); return false; }
      cena3D(); desenhar();
    }
    if (a && a.ponta !== undefined) {
      est.sel = { tipo: "interior", id: a.ponta, face: (est.sel && est.sel.face) || "pos" };
      est.arr = { esticar: a.ponta, ok: JSON.stringify(paredeDe(a.ponta)) };
      return true;
    }
    if (a && a.porta !== undefined) {
      est.sel = { tipo: "porta", id: a.porta, parede: a.interior };
      est.arr = { porta: a.porta, parede: a.interior };
      cena3D(); desenhar();
      return true;
    }
    if (a && a.interior !== undefined && info.chao) {
      const r = rs().find((x) => x.id === a.interior);
      est.sel = { tipo: "interior", id: r.id, face: faceDe(r, info.ponto || info.chao), s: PI.naParede(r.o, info.ponto || info.chao).s };
      est.arr = { mover: r.id, c0: r.c, p0: info.chao, ok: r.c };
      cena3D(); desenhar();
      return true;
    }
    if (a0 && a0.lado !== undefined) { // an outside wall: its inner face's finish (user 2026-10-22)
      est.sel = { tipo: "exterior", lado: a0.lado };
      cena3D(); desenhar();
      return false;
    }
    const d = info.chao && PI.divisaoEm(ds(), info.chao);
    if (d) { // a room: its floor (user 2026-10-22: "aplicar pavimento que desejar na divisão que desejar")
      est.sel = { tipo: "divisao", ponto: info.chao };
      cena3D(); desenhar();
      return false;
    }
    if (est.sel) { est.sel = null; cena3D(); desenhar(); }
    return false;
  },
  arrastar(info) {
    const A = est.arr;
    if (!A || !info.chao) return;
    if (A.esticar !== undefined) {
      const w = paredeDe(A.esticar), novo = PI.esticar(est.cont, rs(), w, PI.naParede(w.o, info.chao).s);
      const lista = est.interiores.map((x) => (x.id === w.id ? novo : x));
      const erro = PI.porqueNaoTodas(est.cont, est.vaos, lista);
      if (!erro) { Object.assign(w, novo); est.erro = ""; } else est.erro = `Aqui não: ${erro}.`;
      cena3D(); desenharSelecao();
    } else if (A.mover !== undefined) {
      const w = paredeDe(A.mover), d = PI.naParede(w.o, info.chao).c - PI.naParede(w.o, A.p0).c;
      w.c = arred(A.c0 + d);
      if (PI.porqueNaoTodas(est.cont, est.vaos, est.interiores)) w.c = A.ok; else A.ok = w.c;
      cena3D(); desenharSelecao();
    } else if (A.porta !== undefined) {
      const lista = rs(), r = lista.find((x) => x.id === A.parede), p = paredeDe(A.parede).portas.find((x) => x.id === A.porta);
      const c = PI.centroPorta(lista, r, p, arred(PI.naParede(r.o, info.chao).s));
      if (c !== null && Math.abs(c - p.s) > 1e-6) { p.s = c; cena3D(); desenharSelecao(); }
    }
  },
  largar() { est.arr = null; mudou(); cena3D(); desenhar(); },
  pairar(info) {
    if (est.ferramenta === "parede") { pairarDesenho(info); return; }
    const a0 = info.alvo && info.alvo.divisao === undefined ? info.alvo : null;
    const a = (a0 && a0.lado === undefined && a0) || pertoDe(info.chao);
    if (est.pincel) cena.cursor((a && a.interior !== undefined) || (a0 && a0.lado !== undefined) ? "copy" : "not-allowed");
    else cena.cursor(a && a.ponta !== undefined ? "ew-resize" : a && (a.porta !== undefined || a.interior !== undefined) ? "grab"
      : (a0 && a0.lado !== undefined) || (info.alvo && info.alvo.divisao !== undefined) ? "pointer" : "");
  },
};

function pintarExterior(lado, material) { // the finish of an outside wall's inner face (the whole side)
  est.facesExt = { ...est.facesExt, [lado]: material };
  mudou();
  cena3D(); desenhar();
}

function pavimentar(ponto, material) { // the floor of the room holding the point
  const d = PI.divisaoEm(ds(), ponto);
  if (!d) return;
  // the earlier choices inside this room go: one entry per room
  est.pavimentos = [...est.pavimentos.filter((x) => !PI.divisaoEm([d], x.ponto)), { ponto: d.rotulo, material }];
  if (est.sel && est.sel.tipo === "divisao") est.sel.ponto = d.rotulo;
  mudou();
  cena3D(); desenhar();
}

function maisPorta(w) {
  const lista = rs(), r = lista.find((x) => x.id === w.id);
  const p = { id: est.prox, s: 0 };
  const c = PI.centroPorta(lista, r, p, (r.a + r.b) / 2);
  if (c === null) { est.erro = "Não cabe mais uma porta nesta parede."; return; }
  p.s = c;
  est.prox += 1;
  w.portas.push(p);
  est.sel = { tipo: "porta", id: p.id, parede: w.id };
  mudou();
}

function comprimento(w, v) { // a typed length: the free end moves (stopped by a wall in the way)
  const lista = rs(), r = lista.find((x) => x.id === w.id);
  const fixoIni = w.fim.tipo === "livre", sFixo = fixoIni ? (w.ini === r.refA ? r.a : r.b) : (w.fim === r.refA ? r.a : r.b);
  const sLivre = fixoIni ? (w.fim === r.refA ? r.a : r.b) : (w.ini === r.refA ? r.a : r.b);
  const dir = sLivre >= sFixo ? 1 : -1;
  const novo = PI.esticar(est.cont, lista, w, sFixo + dir * Math.max(PI.COMPRIMENTO_MIN, v));
  const erro = PI.porqueNaoTodas(est.cont, est.vaos, est.interiores.map((x) => (x.id === w.id ? novo : x)));
  if (erro) { est.erro = `Assim não: ${erro}.`; return; }
  Object.assign(w, novo);
  est.erro = "";
  mudou();
}

function remover(troco = true) {
  const s = est.sel;
  if (!s) return;
  if (s.tipo === "vao") est.vaos = est.vaos.filter((v) => v.id !== s.id);
  else if (s.tipo === "porta") { const w = paredeDe(s.parede); if (w) w.portas = w.portas.filter((p) => p.id !== s.id); }
  else if (s.tipo === "interior" && troco && trocoSel()) { // only the piece selected
    const out = PI.removerTroco(est.cont, est.interiores, s.id, trocoSel(), est.prox);
    if (out.erro) { est.erro = `Assim não: ${out.erro}.`; desenhar(); return; }
    const lista = out.lista.map((w) => ({ ...w }));
    for (const w of lista) { // the doors next to the new end keep clear of it, or go
      const r = PI.resolver(est.cont, lista).find((x) => x.id === w.id);
      w.portas = w.portas.flatMap((p) => { const c = PI.centroPorta(PI.resolver(est.cont, lista), r, p, p.s); return c === null ? [] : [{ ...p, s: c }]; });
    }
    const erro = PI.porqueNaoTodas(est.cont, est.vaos, lista);
    if (erro) { est.erro = `Assim não: ${erro}.`; desenhar(); return; }
    est.interiores = lista;
    est.prox += 1;
    est.erro = out.removidas ? `Também saíram ${out.removidas} parede(s) que só se apoiavam nesse troço.` : "";
  } else if (s.tipo === "interior") {
    const { lista, removidas } = PI.remover(est.interiores, s.id);
    est.interiores = lista;
    est.erro = removidas ? `Também saíram ${removidas} parede(s) que só se apoiavam nesta.` : "";
  }
  est.sel = null;
  mudou(); cena3D(); desenhar();
}

// ---------------------------------------------------------------- dragging from the side menu (a wall, a finish)
function arrastarDoMenu(e, tipo, id) {
  e.preventDefault();
  const fant = $("#fantasma"), x0 = e.clientX, y0 = e.clientY;
  fant.innerHTML = e.currentTarget.querySelector(".fig")?.innerHTML || "";
  est.menu = { tipo, id, moveu: false };
  const sobreTela = (ev) => { const el = document.elementFromPoint(ev.clientX, ev.clientY); return el && el.closest && el.closest("#tela"); };
  const nova = (ev) => {
    const info = cena.info(ev), lista = rs();
    if (!info.chao) return null;
    const perto = PI.paredePerto(est.cont, lista, info.chao);
    if (!perto) return { erro: "solte-a dentro da casa" };
    const w = PI.novaParede(est.cont, lista, perto, info.chao, est.prox);
    const novaLista = [...est.interiores, w];
    const r = PI.resolver(est.cont, novaLista).find((x) => x.id === w.id);
    return { w, r, erro: PI.porqueNaoTodas(est.cont, est.vaos, novaLista) };
  };
  const mover = (ev) => {
    if (!est.menu.moveu && Math.hypot(ev.clientX - x0, ev.clientY - y0) > 5) {
      est.menu.moveu = true;
      if (est.sel) { est.sel = null; cena3D(); } // a drag: the HUD would cover the house while dropping
    }
    if (!est.menu.moveu) return;
    fant.hidden = false;
    fant.style.left = `${ev.clientX + 8}px`;
    fant.style.top = `${ev.clientY + 8}px`;
    if (!sobreTela(ev)) { cena.previa(null); return; }
    if (tipo === "parede") {
      const n = nova(ev);
      if (n && n.r) cena.previa({ tipo: "parede", o: n.r.o, c: n.r.c, a: n.r.a, b: n.r.b, pe: est.pe }, !!n.erro);
      else cena.previa(null);
      est.erro = n && n.erro ? `Aqui não: ${n.erro}.` : "";
      const er = $("#erro"); if (er) er.textContent = est.erro;
    }
  };
  const largar = (ev) => {
    window.removeEventListener("pointermove", mover);
    window.removeEventListener("pointerup", largar);
    fant.hidden = true;
    cena.previa(null);
    const moveu = est.menu.moveu;
    est.menu = null;
    if (!moveu) { // a click
      if (tipo === "parede") { // the wall tool: then clicks draw walls (user 2026-10-22: "não quero ter que arrastar")
        est.ferramenta = est.ferramenta === "parede" ? null : "parede";
        est.erro = ""; pararDesenho(); est.sel = null; est.pincel = null;
        cena.previa(null); cena.marca(null); cena.medidas(null); cena3D(); desenhar();
      } else if (tipo === "material") { // on the face selected, else the next face clicked (once)
        const s = est.sel;
        if (s && s.tipo === "interior") pintar(s.id, est.ambas ? "ambas" : s.face || "pos", id);
        else if (s && s.tipo === "exterior") pintarExterior(s.lado, id);
        else { est.pincel = est.pincel === id ? null : id; est.ferramenta = null; pararDesenho(); cena.marca(null); cena3D(); desenhar(); }
      } else if (tipo === "pavimento") { // the room selected, else the whole house
        const s = est.sel;
        if (s && s.tipo === "divisao") pavimentar(s.ponto, id);
        else { est.acabamentos.pavimento = id; mudou(); cena3D(); desenhar(); }
      }
      return;
    }
    if (!sobreTela(ev)) return;
    if (tipo === "parede") {
      const n = nova(ev);
      if (n && n.w && !n.erro) {
        est.interiores.push(n.w);
        est.prox += 1;
        est.sel = { tipo: "interior", id: n.w.id, face: "pos" };
        est.erro = "";
        mudou();
      }
    } else if (tipo === "material") {
      const info = cena.info(ev), a = (info.alvo && info.alvo.interior !== undefined && info.alvo) || pertoDe(info.chao);
      if (a && a.interior !== undefined) { const r = rs().find((x) => x.id === a.interior); pintar(r.id, faceDe(r, info.ponto || info.chao), id); return; }
      if (info.alvo && info.alvo.lado !== undefined) { pintarExterior(info.alvo.lado, id); return; }
    } else if (tipo === "pavimento") { // a floor dropped on a room
      const info = cena.info(ev);
      if (info.chao && PI.divisaoEm(ds(), info.chao)) { pavimentar(info.chao, id); return; }
    }
    cena3D(); desenhar();
  };
  window.addEventListener("pointermove", mover);
  window.addEventListener("pointerup", largar);
}

// the small panel next to the selected interior wall (user 2026-10-21: "quando clica nela deve aparecer um pequeno hud
// onde pode substituir o material da face da parede que selecionou ou eliminar a parede")
function hud() {
  const el = $("#hud"), s = est.sel;
  if (!s || est.passo !== 4 || !["interior", "porta", "exterior", "divisao"].includes(s.tipo) || est.verEstrutura) { el.hidden = true; return; }
  const botoesMat = (grupo, atual, attr) => `<div class="mini-mat">${daGrupo(grupo).map((m) => `<button class="${atual === m.id ? "ativo" : ""}" ${attr}="${m.id}" title="${m.nome}"><img src="${previa(m.id, est.materiais)}" alt=""><span>${m.nome}</span></button>`).join("")}</div>`;
  if (s.tipo === "exterior" || s.tipo === "divisao") {
    const d = s.tipo === "divisao" ? PI.divisaoEm(ds(), s.ponto) : null;
    if (s.tipo === "divisao" && !d) { el.hidden = true; return; }
    el.innerHTML = s.tipo === "exterior"
      ? `<div class="hud-cab"><strong>Parede exterior · lado ${s.lado + 1}</strong><button class="x" id="hud-x" title="Fechar">×</button></div>
        <label>Material da face interior</label>${botoesMat("interior", est.facesExt[s.lado] || "pladur", "data-face-ext")}
        <p class="info">Todo este lado, por dentro. Por defeito, gesso cartonado pintado.</p>`
      : `<div class="hud-cab"><strong>Divisão · ${d.area.toFixed(1).replace(".", ",")} m²</strong><button class="x" id="hud-x" title="Fechar">×</button></div>
        <label>Pavimento desta divisão</label>${botoesMat("pavimento", pavDe(d), "data-pav-div")}
        <p class="info">Área do pavimento, entre as faces acabadas das paredes.</p>`;
    el.hidden = false;
    posicionarHud();
    $("#hud-x").onclick = () => { est.sel = null; cena3D(); desenhar(); };
    el.querySelectorAll("[data-face-ext]").forEach((b) => b.onclick = () => pintarExterior(s.lado, b.dataset.faceExt));
    el.querySelectorAll("[data-pav-div]").forEach((b) => b.onclick = () => pavimentar(s.ponto, b.dataset.pavDiv));
    return;
  }
  const lista = rs(), r = lista.find((x) => x.id === (s.tipo === "porta" ? s.parede : s.id));
  if (!r) { el.hidden = true; return; }
  if (s.tipo === "porta") {
    el.innerHTML = `<div class="hud-cab"><strong>Porta interior · 0,80 × 2,00 m</strong><button class="x" id="hud-x" title="Fechar">×</button></div>
      <p class="info">Arraste-a ao longo da parede.</p><div class="acoes"><button class="btn" id="hud-del">Eliminar porta</button></div>`;
  } else {
    const livre = r.fimA === "livre" || r.fimB === "livre", tr = trocoSel();
    const atual = r.faces[s.face || "pos"];
    el.innerHTML = `<div class="hud-cab"><strong>Parede interior</strong><button class="x" id="hud-x" title="Fechar">×</button></div>
      ${tr ? `<p class="info">Troço escolhido: <strong>${m2(tr[1] - tr[0])} m</strong> (parede de ${m2(r.comp)} m)</p>` : ""}
      ${livre ? `<label>Comprimento</label><div class="numero"><input type="number" id="hud-comp" min="${PI.COMPRIMENTO_MIN}" step="0.05" value="${r.comp.toFixed(2)}"><span>m</span></div>`
        : tr ? "" : `<p class="info">De parede a parede: ${m2(r.comp)} m</p>`}
      <label>Material desta face</label>
      <div class="mini-mat">${daGrupo("interior").map((m) => `<button class="${atual === m.id ? "ativo" : ""}" data-face-mat="${m.id}" title="${m.nome}"><img src="${previa(m.id, est.materiais)}" alt=""><span>${m.nome}</span></button>`).join("")}</div>
      <label class="caixa"><input type="checkbox" id="hud-ambas" ${est.ambas ? "checked" : ""}> Aplicar às duas faces</label>
      <div class="acoes"><button class="btn cheio" id="hud-porta">+ Porta</button>${tr ? `<button class="btn" id="hud-troco">Eliminar troço</button>` : ""}<button class="btn" id="hud-del">Eliminar parede</button></div>`;
  }
  el.hidden = false;
  posicionarHud();
  $("#hud-x").onclick = () => { est.sel = null; cena3D(); desenhar(); };
  $("#hud-del").onclick = () => remover(false);
  if ($("#hud-troco")) $("#hud-troco").onclick = () => remover(true);
  if ($("#hud-comp")) $("#hud-comp").onchange = (e) => { comprimento(paredeDe(r.id), Number(e.target.value)); cena3D(); desenhar(); };
  if ($("#hud-porta")) $("#hud-porta").onclick = () => { maisPorta(paredeDe(r.id)); cena3D(); desenhar(); };
  el.querySelectorAll("[data-face-mat]").forEach((b) => b.onclick = () => pintar(r.id, est.ambas ? "ambas" : s.face || "pos", b.dataset.faceMat));
  // both faces (user 2026-10-28: "A opção de pintar ambas as face do hud de materiais não está a funcionar" — the box
  // did nothing by itself and came back unticked): ticked, this face's finish goes on the other one at once, and it
  // stays ticked for the next finish picked
  if ($("#hud-ambas")) $("#hud-ambas").onchange = (e) => {
    est.ambas = e.target.checked;
    if (est.ambas) pintar(r.id, "ambas", r.faces[s.face || "pos"] || "pladur"); else { cena3D(); desenhar(); }
  };
}

// the HUD beside what it is about, never over it (user 2026-10-22: "o hud fica demasiado em cima da parede atrapalhando
// o processo e tapando até o ponto onde podemos arrastar a parede"): the selection's box on the screen, the HUD on the
// side with room (right, left, above, below), else a corner of the view
function posicionarHud() {
  const el = $("#hud"), s = est.sel;
  if (el.hidden || !s) return;
  let pts = [];
  if (s.tipo === "exterior") {
    const l = lados(est.cont)[s.lado];
    if (l) pts = [[...l.p0, 0], [...l.p1, 0], [...l.p0, est.pe], [...l.p1, est.pe]];
  } else if (s.tipo === "divisao") {
    const d = PI.divisaoEm(ds(), s.ponto);
    if (d) pts = d.celulas.flatMap((c) => [[c[0], c[2], 0], [c[1], c[3], 0]]);
  } else {
    const r = rs().find((x) => x.id === (s.tipo === "porta" ? s.parede : s.id));
    if (r) pts = [r.a, r.b].flatMap((v) => [[...PI.pt(r.o, r.c, v), 0], [...PI.pt(r.o, r.c, v), est.pe + 0.4]]);
  }
  const ps = pts.map((p) => cena.paraEcra(p)).filter(Boolean), V = $("#vista");
  if (!ps.length) return;
  const x0 = Math.min(...ps.map((p) => p[0])), x1 = Math.max(...ps.map((p) => p[0]));
  const y0 = Math.min(...ps.map((p) => p[1])), y1 = Math.max(...ps.map((p) => p[1]));
  const w = el.offsetWidth, h = el.offsetHeight, W = V.clientWidth, H = V.clientHeight - 60, g = 16;
  const ym = Math.min(Math.max(8, (y0 + y1) / 2 - h / 2), H - h);
  const xm = Math.min(Math.max(8, (x0 + x1) / 2 - w / 2), W - w - 8);
  const opcoes = [[x1 + g, ym, x1 + g + w <= W - 8], [x0 - g - w, ym, x0 - g - w >= 8], [xm, y0 - g - h, y0 - g - h >= 8], [xm, y1 + g, y1 + g + h <= H]];
  const [l, t] = (opcoes.find((o) => o[2]) || [W - w - 8, 8]);
  el.style.left = `${l}px`;
  el.style.top = `${t}px`;
}
(function seguirHud() { posicionarHud(); requestAnimationFrame(seguirHud); })();

// ---------------------------------------------------------------- step 6: doors and windows on the walls
function noLado(info, l) { // distance along side l of the pointer (on the wall's plane)
  const p = cena.pontoNaParede(info.evento, l);
  return p ? (p[0] - l.p0[0]) * l.u[0] + (p[1] - l.p0[1]) * l.u[1] : null;
}
const centro = (v, c) => centroVao(est.cont, est.vaos, rs(), v, c);
// the interior doors here too (user 2026-10-28: "Adicionar portas interiores ao menu de portas e janelas e permitir
// colocar portas e janelas nas paredes interiores"): the method's door, on an interior wall only; the windows and the
// outside doors stay on the outside walls (a window in an interior wall: not in the engine yet)
const PORTA_INT = "porta_interior";
const nomeTipo = (k) => (k === PORTA_INT ? "Porta interior" : CATALOGO[k].nome);
const nPortasInt = () => rs().reduce((n, r) => n + r.portas.length, 0);
function portaEm(info) { // the interior door under the pointer — its leaf, or the wall over it ({porta, interior})
  const a = info.alvo;
  if (!a || a.interior === undefined) return null;
  const d = a.porta !== undefined ? a : pertoDe(info.ponto || info.chao);
  return d && d.porta !== undefined ? d : null;
}
function interiorEm(info) { // the interior wall under the pointer (resolved) and the point on it
  const a = (info.alvo && info.alvo.interior !== undefined && info.alvo) || pertoDe(info.chao);
  const r = a ? rs().find((x) => x.id === a.interior) : null;
  const p = (info.alvo && info.alvo.interior !== undefined && info.ponto) || info.chao;
  return r && p ? { r, s: arred(PI.naParede(r.o, p).s) } : null;
}

const interacaoVaos = {
  premir(info) {
    est.erro = "";
    const a = info.alvo;
    if (est.ferramenta === PORTA_INT) {
      const e = interiorEm(info), p = { id: est.prox, s: 0 };
      const c = e && PI.centroPorta(rs(), e.r, p, e.s);
      cena.previa(null);
      if (!e) { est.erro = "A porta interior vai numa parede interior: clique numa delas."; desenhar(); return false; }
      if (c === null) { est.erro = "Porta interior: não cabe nesta parede (pontas, outras portas ou paredes que a encontram)."; desenhar(); return false; }
      p.s = c;
      est.prox += 1;
      paredeDe(e.r.id).portas.push(p);
      est.sel = { tipo: "porta", id: p.id, parede: e.r.id };
      est.ferramenta = null;
      est.arr = { porta: p.id, parede: e.r.id };
      cena3D(); desenhar();
      return true;
    }
    if (est.ferramenta && a && a.interior !== undefined) {
      est.erro = `${nomeTipo(est.ferramenta)}: só nas paredes exteriores — numa parede interior vai a porta interior.`;
      desenhar();
      return false;
    }
    const ap = portaEm(info);
    if (ap) { // an interior door (or the wall over it): chosen, and dragged along its wall
      est.sel = { tipo: "porta", id: ap.porta, parede: ap.interior };
      est.arr = { porta: ap.porta, parede: ap.interior };
      cena3D(); desenhar();
      return true;
    }
    if (est.ferramenta && a && a.lado !== undefined) {
      const l = lados(est.cont)[a.lado], c0 = CATALOGO[est.ferramenta];
      const v = acertarVao({ id: est.prox, lado: a.lado, tipo: est.ferramenta, largura: c0.largura, altura: c0.altura,
        peitoril: c0.peitoril, estore: c0.estore, vidro: c0.vidro, centro: 0 }, est.pe, (est.avisos = []), escondida());
      const c = centro(v, arred(noLado(info, l) ?? l.comprimento / 2));
      cena.previa(null);
      if (c === null) { est.erro = `${c0.nome}: não cabe nesta parede (cantos, outros vãos ou paredes interiores).`; desenhar(); return false; }
      v.centro = c;
      est.prox += 1;
      est.vaos.push(v);
      est.sel = { tipo: "vao", id: v.id };
      est.ferramenta = null;
      est.arr = { vao: v.id };
      cena3D(); desenhar();
      return true;
    }
    if (a && a.vao !== undefined) {
      est.sel = { tipo: "vao", id: a.vao };
      est.arr = { vao: a.vao };
      cena3D(); desenhar();
      return true;
    }
    if (est.sel) { est.sel = null; cena3D(); desenhar(); }
    return false;
  },
  arrastar(info) {
    if (est.arr && est.arr.porta !== undefined) { interacaoInteriores.arrastar(info); return; } // an interior door
    const v = est.arr && vaoDe(est.arr.vao);
    if (!v) return;
    const s = noLado(info, lados(est.cont)[v.lado]);
    if (s === null) return;
    const c = centro(v, arred(s));
    if (c !== null && Math.abs(c - v.centro) > 1e-6) { v.centro = c; cena3D(); desenharSelecao(); }
  },
  largar() { if (est.arr) { est.arr = null; mudou(); desenhar(); } },
  pairar(info) {
    const a = info.alvo;
    if (est.ferramenta === PORTA_INT) {
      const e = interiorEm(info), c = e && PI.centroPorta(rs(), e.r, { id: -1, s: 0 }, e.s);
      cena.previa(e ? { tipo: "porta", o: e.r.o, c: e.r.c, s: c ?? e.s } : null, c === null);
      cena.cursor(e && c !== null ? "copy" : "not-allowed");
    } else if (est.ferramenta && a && a.interior !== undefined) {
      cena.previa(null);
      cena.cursor("not-allowed");
    } else if (est.ferramenta && a && a.lado !== undefined) {
      const l = lados(est.cont)[a.lado], c0 = CATALOGO[est.ferramenta];
      const v = acertarVao({ id: -1, lado: a.lado, tipo: est.ferramenta, largura: c0.largura, altura: c0.altura, peitoril: c0.peitoril, estore: c0.estore }, est.pe, [], escondida());
      const s = noLado(info, l), c = s === null ? null : centro(v, arred(s));
      cena.previa({ tipo: "vao", cont: est.cont, lado: a.lado, s0: (c ?? s) - v.largura / 2, s1: (c ?? s) + v.largura / 2, ...zFrame(v) }, c === null);
      cena.medidas(s === null ? null : medidasVao(a.lado, (c ?? s) - v.largura / 2, (c ?? s) + v.largura / 2));
      cena.cursor(c === null ? "not-allowed" : "copy");
    } else {
      cena.previa(null);
      if (est.ferramenta) medidasSelecao();
      cena.cursor(a && (a.vao !== undefined || portaEm(info)) ? "grab" : "");
    }
  },
};

// the distances of an opening (s0..s1 along side `lado`, its frame's edges) to the nearest axis each way — a corner of
// the base or an interior wall meeting that side (user 2026-10-30: "No menu de portas e janelas é necessário haver uma
// régua tipo a das paredes interiores que quando a pessoa está a colocar a janela que lhe diz a distância a que está do
// eixo mais próximo"): drawn on the floor inside, as the interior walls' ([{de, ate, valor, n, lado: "ant" | "seg", t}])
function medidasVao(lado, s0, s1) {
  const l = est.cont && lados(est.cont)[lado];
  if (!l) return null;
  const eixos = [0, l.comprimento];
  for (const r of rs()) for (const [ref, sr] of [[r.refA, r.a], [r.refB, r.b]]) {
    if (!ref || ref.tipo !== "ext" || ref.lado !== lado || !Number.isFinite(sr)) continue;
    const q = PI.pt(r.o, r.c, sr);
    eixos.push((q[0] - l.p0[0]) * l.u[0] + (q[1] - l.p0[1]) * l.u[1]);
  }
  const P = (t) => [l.p0[0] + l.u[0] * t, l.p0[1] + l.u[1] * t], n = [-l.n[0], -l.n[1]];
  const ant = Math.max(...eixos.filter((t) => t <= s0 + 1e-6)), seg = Math.min(...eixos.filter((t) => t >= s1 - 1e-6));
  const out = [];
  if (Number.isFinite(ant) && s0 - ant > 0.01) out.push({ de: P(ant), ate: P(s0), valor: Math.round((s0 - ant) * 1000) / 1000, n, lado: "ant", t: ant });
  if (Number.isFinite(seg) && seg - s1 > 0.01) out.push({ de: P(s1), ate: P(seg), valor: Math.round((seg - s1) * 1000) / 1000, n, lado: "seg", t: seg });
  return out;
}
function posicionarVao(id, m, val) { // the opening moved so that it stands val from that axis
  const v = vaoDe(id);
  if (!v || !m || !Number.isFinite(val) || val < 0) { cena3D(); return; }
  const alvo = m.lado === "ant" ? m.t + val + v.largura / 2 : m.t - val - v.largura / 2;
  const c = centro(v, alvo);
  if (c === null || Math.abs(c - alvo) > 0.002) { est.erro = "Assim não cabe (cantos, outros vãos ou paredes interiores)."; desenhar(); cena3D(); return; }
  v.centro = c;
  est.erro = "";
  mudou(); cena3D(); desenhar();
}

// ---------------------------------------------------------------- step 7: pergolas, garages and annexes
// (user 2026-10-29: "Pérgolas o cliente deve poder escolher a largura e onde quer colocar a pérgola dando snap para o
// sítio no forro exterior, a altura tem de ter um máximo como sabes. Garagens deve indicar os metros quadrados,
// cobertura, se quer junto à casa ou separado, se for junto neste caso com ligação para a casa deves juntar a nossa
// estrutura o espaço a mais e a cobertura tem de ser a mesma que escolheu para a casa, se for separado pode escolher a
// cobertura que quiser. Mesma lógica das garagens para anexos.")
const NOME7 = { pergola: "Pérgola", garagem: "Garagem", anexo: "Anexo" };
const NOTA7 = { pergola: "encostada a uma fachada", garagem: "junto à casa ou separada", anexo: "junto à casa ou separado" };
// a separate building at least 2 m from the house (user 2026-10-30: "deve ter pelo menos 2 metros de distância da casa"
// — 3 m in his answer just before: to confirm), 1 m from another separate one (ours), never over a pergola
const AFASTAR_CASA = 2.0, AFASTAR_SEP = 1.0;
const PG = () => est.regrasPergola || { altura_min: 2.2, projecao: [1.5, 5.0], largura_min: 1.5, acima_do_anel: 0.1, inclinacao: 0.05 };
// the highest a pergola's beams may sit at the facade (the engine's — "a altura tem de ter um máximo"): the ring's top
// + 0,10, where its ledger is bolted (pergola.maximo), and under an exposed roof clear of the overhang and its gutter;
// known once the engine has built the house with it
function alturaMaxPg(pg = null) {
  const k = pg && est.cob && est.cob.pergolaIds ? est.cob.pergolaIds.indexOf(pg.id) : -1;
  if (k >= 0 && est.cob.pergolasMax && est.cob.pergolasMax[k] != null) return Math.floor(est.cob.pergolasMax[k] * 100) / 100;
  // its highest point at the ground floor's top (user 2026-10-30), until the engine gives each one's
  return est.cob && est.cob.pergolaMax != null ? Math.floor(est.cob.pergolaMax * 100) / 100 : null;
}
const pergolaDe = (id) => est.exteriores.pergolas.find((p) => p.id === id);
const blocoDe = (id) => est.exteriores.blocos.find((b) => b.id === id);
const nomeCobSep = (k) => (k === "escondida" ? "Oculta" : "Duas águas, com empenas à vista");
const separad = (tipo) => (tipo === "garagem" ? "separada" : "separado");
const profundidade = (areaM2, largura) => Math.max(2.0, Math.round((areaM2 / largura) * 20) / 20);

// the separate garages / annexes: each drawn as the engine builds it (a house of its own), at its place
function desenharSeparados() {
  const seps = est.cont && fechada() ? est.exteriores.blocos.filter((b) => b.modo === "separado") : [];
  cena.edificiosVivos(seps.map((e) => e.id));
  for (const e of seps) {
    const cont = EX.contornoSeparado(e), d = est.sep[e.id] || {}, casa = EX.casaSeparada(e, { acabamentos: est.acabamentos, pe_direito: est.pe });
    const oculta = e.cobertura.tipo === "escondida";
    const H = oculta ? d.zPlat || est.pe + 1.0 : d.zBeirado ?? est.pe + 0.36;
    const vs = casa.vaos.map((v, k) => ({ ...v, id: `${e.id}.${k}`, s0: v.centro - v.largura / 2, s1: v.centro + v.largura / 2, z0: 0, z1: v.altura }));
    const parapeito = oculta && est.verCobertura ? est.pe + 0.3 : null;
    const Y = e.profundidade, mapear = d.rodada ? (xr, yr) => [yr, Y - xr] : (x, y) => [x, y];
    cena.emEdificio(e.id, e, () => {
      cena.base(cont);
      cena.paredes(cont, casa.paredes_exteriores, { altura: H, material: matDe(est.acabamentos.exterior), vaos: vs, parapeito,
        dentroPlat: (l) => (parapeito && d.plat ? d.plat[l] : null) });
      cena.vaos(cont, vs);
      if (!oculta) cena.telhadoFaces(d.faces, matDe("sandwich"));
      else if (d.objetos) cena.limpar("telhado");
      else cena.telhado(cont, H - 0.45, matDe("sandwich")); // until the engine answers
      if (d.objetos) cena.pecasCobertura(d.objetos, est.materiais, mapear);
      cena.empenas(oculta ? null : cont, d.faces, H, matDe(est.acabamentos.exterior));
    });
  }
}

// their lines in the Lista: a pergola by its area, a separate building as a house of its own
function linhasExteriores() {
  const P = PRECOS_EXEMPLO, out = [];
  if (!est.cont || !fechada()) return out;
  for (const pg of est.exteriores.pergolas) {
    const W = pg.s1 - pg.s0;
    out.push({ rotulo: `Pérgola ${m2(W)} × ${m2(pg.projecao)} m (lado ${pg.lado + 1})`, valor: W * pg.projecao * P.pergola_por_m2 });
  }
  for (const e of est.exteriores.blocos.filter((b) => b.modo === "separado")) {
    const casa = EX.casaSeparada(e, { acabamentos: est.acabamentos, pe_direito: est.pe }), d = est.sep[e.id] || {};
    const oculta = e.cobertura.tipo === "escondida";
    const o = orcamento({ area: e.largura * e.profundidade, altura: oculta ? d.zPlat || est.pe + 1.0 : d.zBeirado ?? est.pe + 0.36, pe: est.pe,
      paredes: casa.paredes_exteriores, vaos: casa.vaos, interiores: [],
      acabamentos: { ...est.acabamentos, pavimento: e.tipo === "garagem" ? "ceramico_pav" : est.acabamentos.pavimento },
      cobertura: { ...e.cobertura, nome: nomeCobSep(e.cobertura.tipo) }, divisoes: [], facesExt: [] });
    for (const l of o.linhas) out.push({ rotulo: `${EX.TIPOS_EXT[e.tipo].nome} ${separad(e.tipo)} · ${l.rotulo}`, valor: l.valor });
  }
  return out;
}

// ---- pergolas: against a wall's cladding, along it, never past its side
function posicionarPergola(pg, s0) { // flush with a corner when close
  const L = lados(est.cont)[pg.lado].comprimento, W = pg.s1 - pg.s0;
  let a = arred(s0);
  if (a < EX.ENCOSTAR) a = 0;
  if (L - (a + W) < EX.ENCOSTAR) a = L - W;
  a = Math.max(0, Math.min(a, L - W));
  pg.s0 = Math.round(a * 1000) / 1000;
  pg.s1 = Math.round((a + W) * 1000) / 1000;
}
function porqueNaoPergola(pg) {
  const r = EX.retPergola(est.cont, pg, cena.fora);
  if (!r) return "esse lado não existe";
  if (EX.sobreACasa(est.cont, r)) return "ficava por cima de outra parte da casa";
  for (const o of est.exteriores.pergolas) if (o.id !== pg.id && o.lado === pg.lado && Math.min(o.s1, pg.s1) - Math.max(o.s0, pg.s0) > 0.01) return "já há uma pérgola nesse troço";
  for (const b of est.exteriores.blocos.filter((x) => x.modo === "separado")) {
    const f = EX.pegadaSeparado(b);
    if (r.x0 < f.x1 && r.x1 > f.x0 && r.y0 < f.y1 && r.y1 > f.y0) return `fica por cima de ${b.tipo === "garagem" ? "uma garagem" : "um anexo"}`;
  }
  return null;
}
function novaPergola(lado, sc) {
  const l = lados(est.cont)[lado], R = PG(), W = Math.min(4.0, l.comprimento);
  if (W < R.largura_min) { est.erro = `Este lado é curto demais para uma pérgola (pelo menos ${m2(R.largura_min)} m).`; return null; }
  const pg = { id: est.prox, lado, s0: 0, s1: W, projecao: 3.0, altura: null };
  posicionarPergola(pg, sc - W / 2);
  const erro = porqueNaoPergola(pg);
  if (erro) { est.erro = `Aqui não: ${erro}.`; return null; }
  est.prox += 1;
  est.exteriores.pergolas.push(pg);
  return pg;
}
function acertarPergola(pg, m) {
  const R = PG(), L = lados(est.cont)[pg.lado].comprimento, antes = { ...pg };
  est.erro = "";
  if (m.largura !== undefined) {
    const W = Math.min(L, Math.max(R.largura_min, arred(m.largura || 0))), c = (pg.s0 + pg.s1) / 2;
    pg.s1 = pg.s0 + W;
    posicionarPergola(pg, c - W / 2);
  }
  if (m.s0 !== undefined) posicionarPergola(pg, m.s0 || 0);
  if (m.projecao !== undefined) pg.projecao = Math.min(R.projecao[1], Math.max(R.projecao[0], arred(m.projecao || R.projecao[0])));
  if (m.altura !== undefined) {
    const mx = alturaMaxPg(pg);
    let a = Math.max(R.altura_min, Math.round((m.altura || 0) * 100) / 100);
    if (mx !== null && a > mx) {
      a = mx;
      est.erro = `A altura máxima junto à casa é ${m2(mx)} m: ${est.cobertura.tipo !== "escondida" ? "fica por baixo do beirado e da caleira" : "a viga de encosto aperta à estrutura da parede"}.`;
    }
    pg.altura = mx !== null && Math.abs(a - mx) < 1e-6 ? null : a; // null: the highest
  }
  const erro = porqueNaoPergola(pg);
  if (erro) { Object.assign(pg, antes); est.erro = `Assim não: ${erro}.`; } else mudou();
  cena3D(); desenhar();
}
function fantasmaPergola(pg, erro = false) { // while it moves: its place (the engine redraws it once let go)
  const r = EX.retPergola(est.cont, pg, cena.fora);
  cena.previa(r ? { tipo: "caixa", ...r, z0: 0, z1: (pg.altura ?? alturaMaxPg(pg) ?? est.pe + 0.25) + 0.2 } : null, erro);
}

// ---- an attached garage / annex: the house grows by it (one structure, one roof), the wall between them takes a door
// into the house, a garage its gate on its front
function juntarBloco(tipo, lado, sc, largura, areaM2, silencioso = false) {
  const D = profundidade(areaM2, largura), l = lados(est.cont)[lado];
  const b = EX.blocoJunto(est.cont, lado, sc, largura, D);
  if (!b) return { erro: `a frente (${m2(largura)} m) é maior do que esta parede (${m2(l.comprimento)} m)` };
  const r = EX.combinar(est.cont, b.rect, "uniao");
  if (r.erro) return { erro: r.erro };
  const bloco = { id: est.prox, tipo, modo: "junto", largura, area: areaM2, rect: null, ligacao: null, base: null };
  est.prox += 1;
  aplicarContorno(r.cont, r.d, { lado, s0: b.s0, s1: b.s1, D, bloco }, null, silencioso);
  return { bloco };
}
function tirarBloco(b, silencioso = false) {
  const r = EX.combinar(est.cont, b.rect, "diferenca");
  if (r.erro) { est.erro = `Não foi possível tirá-lo: ${r.erro}.`; return null; }
  aplicarContorno(r.cont, r.d, null, { bloco: b }, silencioso);
  return r.d;
}
function editarJunto(b, m) {
  const T = EX.TIPOS_EXT[b.tipo], antes = instantaneo();
  const areaM2 = Math.min(T.area_max, Math.max(T.area_min, m.area ?? b.area)), largura = Math.max(T.largura_min, arred(m.largura ?? b.largura));
  est.erro = "";
  const d = tirarBloco(b, true);
  if (!d) { cena3D(); desenhar(); return; }
  const q = EX.ladoPor(est.cont, [b.base.ponto[0] + d[0], b.base.ponto[1] + d[1]], b.base.n);
  const r = q ? juntarBloco(b.tipo, q.lado, q.s, largura, areaM2, true) : { erro: "a parede onde estava mudou" };
  if (r.erro) { // back as it was
    Object.assign(est, JSON.parse(antes), { sel: { tipo: "bloco", id: b.id } });
    est.erro = `Assim não: ${r.erro}.`;
    cena.base(est.cont); cotas(est.cont);
  } else est.sel = { tipo: "bloco", id: r.bloco.id };
  mudou(true);
  cena3D(); desenhar();
}

// the outline changed by an attached block (added: junta, or taken away: sai): the doors, windows, walls, floors,
// pergolas and separate buildings carried over (moved by d when the outline's corner moved); what the block now covers
// goes, with a note
function aplicarContorno(novo, d, junta = null, sai = null, silencioso = false) {
  const velho = est.cont, avisos = [];
  const mv = ([x, y]) => [Math.round((x + d[0]) * 1000) / 1000, Math.round((y + d[1]) * 1000) / 1000];
  const ld = junta ? lados(velho)[junta.lado] : null;
  const noLadoV = (s, e = 0) => mv([ld.p0[0] + ld.u[0] * s + ld.n[0] * e, ld.p0[1] + ld.u[1] * s + ld.n[1] * e]);
  // the wall into the house: the old side's stretch the block covers, between the block's two sides — its house side
  // flush with the walls beside it (user 2026-10-30: "tem de ficar alinhada com as paredes ao seu lado porque agora está
  // a ficar mais dentro das paredes"; it stood on the old outline's line), linha = that line
  let lig = null;
  if (junta) {
    const o = Math.abs(ld.u[0]) > 0.5 ? "h" : "v", ax = o === "h" ? 0 : 1, cr = 1 - ax;
    const A = noLadoV(junta.s0), B = noLadoV(junta.s1), c = A[cr];
    const ka = EX.ladoEm(novo, o, c, Math.min(A[ax], B[ax])), kb = EX.ladoEm(novo, o, c, Math.max(A[ax], B[ax]));
    if (ka !== null && kb !== null) {
      lig = { id: est.prox, o, c: Math.round((c - ld.n[cr] * (PI.FACE_EXT - PI.FACE_INT)) * 1000) / 1000, linha: c,
        ini: { tipo: "ext", lado: ka, canto: true }, fim: { tipo: "ext", lado: kb, canto: true },
        faces: { pos: "pladur", neg: "pladur" }, portas: [], ligacao: junta.bloco.id };
      est.prox += 1;
    }
  }
  const ligSai = sai ? est.interiores.find((w) => w.id === sai.bloco.ligacao) : null;
  const vaos = [];
  for (const v of est.vaos) {
    const q = EX.noNovo(velho, novo, d, v.lado, v.centro);
    if (q) vaos.push({ ...v, lado: q.lado, centro: q.s });
    else if (sai) avisos.push(`${CATALOGO[v.tipo].nome} do lado ${v.lado + 1} saiu com ${sai.bloco.tipo === "garagem" ? "a garagem" : "o anexo"}.`);
    else avisos.push(`${CATALOGO[v.tipo].nome} do lado ${v.lado + 1} ficou por dentro e saiu.`);
  }
  const interiores = [];
  for (const w0 of est.interiores) {
    if (ligSai && w0.id === ligSai.id) continue;
    const ax = w0.o === "h" ? 0 : 1, cr = 1 - ax;
    const ref = (r) => {
      if (r.tipo === "livre") return { ...r, s: Math.round((r.s + d[ax]) * 1000) / 1000 };
      if (r.tipo === "int") {
        if (!ligSai || r.id !== ligSai.id) return r;
        const k = EX.ladoEm(novo, w0.o, w0.c + d[cr], (ligSai.linha ?? ligSai.c) + d[ax]); // the outside wall is back there
        return k === null ? null : { tipo: "ext", lado: k };
      }
      const k = EX.ladoNoNovo(velho, novo, d, r.lado, w0.o, w0.c, !!r.canto);
      if (k !== null) return { ...r, lado: k };
      // it met the stretch the block now covers: the wall into it
      const t = ld && (Math.abs(ld.u[0]) > 0.5 ? (w0.c - ld.p0[0]) / ld.u[0] : (w0.c - ld.p0[1]) / ld.u[1]);
      const sobre = junta && r.lado === junta.lado && t > junta.s0 - 0.01 && t < junta.s1 + 0.01;
      if (lig && sobre) return { tipo: "int", id: lig.id };
      // else it stays where it is, that end free (an interior wall never goes nor moves for a block — user 2026-10-30:
      // "ao adicionar estas divisões à casa em si não deve mexer com a geometria das paredes interiores já criadas")
      const lv = lados(velho)[r.lado];
      return lv ? { tipo: "livre", s: Math.round((lv.p0[ax] + d[ax]) * 1000) / 1000 } : null;
    };
    const ini = ref(w0.ini), fim = ref(w0.fim);
    if (!ini || !fim) { avisos.push("Uma parede interior saiu com a mudança."); continue; }
    interiores.push({ ...w0, c: Math.round((w0.c + d[cr]) * 1000) / 1000, ini, fim,
      portas: w0.portas.map((p) => ({ ...p, s: Math.round((p.s + d[ax]) * 1000) / 1000 })) });
  }
  const pergolas = [];
  for (const p of est.exteriores.pergolas) {
    const a = EX.noNovo(velho, novo, d, p.lado, p.s0), b = EX.noNovo(velho, novo, d, p.lado, p.s1);
    if (a && b && a.lado === b.lado) pergolas.push({ ...p, lado: a.lado, s0: Math.min(a.s, b.s), s1: Math.max(a.s, b.s) });
    else avisos.push(`A pérgola do lado ${p.lado + 1} saiu: a parede onde estava mudou.`);
  }
  const blocos = [];
  for (const b of est.exteriores.blocos) {
    if (sai && b.id === sai.bloco.id) continue;
    if (b.modo === "separado") blocos.push({ ...b, x: Math.round((b.x + d[0]) * 1000) / 1000, y: Math.round((b.y + d[1]) * 1000) / 1000 });
    else blocos.push({ ...b, rect: { x0: b.rect.x0 + d[0], x1: b.rect.x1 + d[0], y0: b.rect.y0 + d[1], y1: b.rect.y1 + d[1] }, base: { ...b.base, ponto: mv(b.base.ponto) } });
  }
  if (junta) {
    const q = [noLadoV(junta.s0), noLadoV(junta.s1, junta.D)];
    Object.assign(junta.bloco, {
      rect: { x0: Math.min(q[0][0], q[1][0]), x1: Math.max(q[0][0], q[1][0]), y0: Math.min(q[0][1], q[1][1]), y1: Math.max(q[0][1], q[1][1]) },
      base: { ponto: noLadoV((junta.s0 + junta.s1) / 2), n: ld.n }, ligacao: lig ? lig.id : null,
    });
    blocos.push(junta.bloco);
  }
  const facesExt = {}; // an outside wall's inner face finish on the sides that stay on its line
  for (const [k, m] of Object.entries(est.facesExt)) {
    const lv = lados(velho)[k];
    if (!lv) continue;
    for (const l of lados(novo)) {
      if (l.n[0] * lv.n[0] + l.n[1] * lv.n[1] < 0.999) continue;
      if (Math.abs((l.p0[0] - lv.p0[0] - d[0]) * l.n[0] + (l.p0[1] - lv.p0[1] - d[1]) * l.n[1]) > 1e-4) continue;
      const t0 = (lv.p0[0] + d[0] - l.p0[0]) * l.u[0] + (lv.p0[1] + d[1] - l.p0[1]) * l.u[1];
      if (Math.min(l.comprimento, Math.max(t0, t0 + lv.comprimento)) - Math.max(0, Math.min(t0, t0 + lv.comprimento)) > 0.05) facesExt[l.i] = m;
    }
  }
  if (lig) interiores.push(lig);
  Object.assign(est, { cont: novo, paredes: paredesPossiveis(lados(novo)), vaos, interiores, facesExt,
    pavimentos: est.pavimentos.map((x) => ({ ...x, ponto: mv(x.ponto) })), exteriores: { pergolas, blocos }, sel: null, ultima: null });
  if (lig) { // the door into the house, in the middle of that wall
    const rs1 = rs(), r = rs1.find((x) => x.id === lig.id), p = { id: est.prox, s: 0 };
    const c = r ? PI.centroPorta(rs1, r, p, (r.a + r.b) / 2) : null;
    if (c !== null) { p.s = c; est.prox += 1; paredeDe(lig.id).portas.push(p); } else avisos.push("A porta para a casa não coube na parede entre as duas: acerte a frente.");
  }
  if (junta && junta.bloco.tipo === "garagem") { // the gate on the garage's front
    const q = EX.ladoPor(novo, noLadoV((junta.s0 + junta.s1) / 2, junta.D), ld.n), W = junta.s1 - junta.s0;
    const v = q && acertarVao({ id: est.prox, lado: q.lado, tipo: "portao", largura: Math.min(3.0, Math.floor((W - 0.65) * 20) / 20), altura: 2.2, estore: false, centro: 0 }, est.pe, [], escondida());
    const c = v && v.largura >= 2.0 ? centro(v, q.s) : null;
    if (c !== null) { v.centro = c; est.prox += 1; est.vaos.push(v); junta.bloco.portao = v.id; } else avisos.push("O portão não coube na frente da garagem: acerte a frente ou ponha-o no passo 6.");
  }
  est.avisos = avisos;
  cena.base(est.cont);
  cotas(est.cont);
  if (!silencioso) { mudou(true); cena3D(); }
}

// ---- a separate garage / annex: a building of its own on the ground, at least AFASTAR_SEP from the rest
function porqueNaoSeparado(e) {
  const f = EX.pegadaSeparado(e);
  if (EX.distanciaACasa(est.cont, f) < AFASTAR_CASA - 1e-6) return `fica a menos de ${m2(AFASTAR_CASA)} m da casa (para a juntar, escolha "Junto à casa")`;
  for (const o of est.exteriores.blocos) {
    if (o.id === e.id || o.modo !== "separado") continue;
    const g = EX.pegadaSeparado(o);
    if (f.x0 < g.x1 + AFASTAR_SEP && f.x1 > g.x0 - AFASTAR_SEP && f.y0 < g.y1 + AFASTAR_SEP && f.y1 > g.y0 - AFASTAR_SEP) return "fica junto de outra construção";
  }
  for (const p of est.exteriores.pergolas) {
    const r = EX.retPergola(est.cont, p, cena.fora);
    if (r && f.x0 < r.x1 && f.x1 > r.x0 && f.y0 < r.y1 && f.y1 > r.y0) return "fica por cima de uma pérgola";
  }
  return null;
}
function colocarSeparado(f, ponto) {
  const W = f.largura, D = profundidade(f.area, f.largura);
  const e = { id: est.prox, tipo: f.tipo, modo: "separado", x: arred(ponto[0] - W / 2), y: arred(ponto[1] - D / 2), rot: 0,
    largura: W, profundidade: D, cobertura: { ...f.cobertura } };
  const erro = porqueNaoSeparado(e);
  if (erro) return { erro };
  est.prox += 1;
  est.exteriores.blocos.push(e);
  return { e };
}
function acertarSeparado(e, m) {
  const T = EX.TIPOS_EXT[e.tipo], antes = JSON.stringify(e);
  const f0 = EX.pegadaSeparado(e), cx = (f0.x0 + f0.x1) / 2, cy = (f0.y0 + f0.y1) / 2; // turned about its middle
  if (m.largura !== undefined) e.largura = Math.min(12, Math.max(T.largura_min, arred(m.largura || 0)));
  if (m.profundidade !== undefined) e.profundidade = Math.min(12, Math.max(2.0, arred(m.profundidade || 0)));
  if (m.rot !== undefined) e.rot = m.rot;
  if (m.cobertura) e.cobertura = m.cobertura;
  if (m.portao) { // the gate: the opening's limits (step 6), within the front
    const v = acertarVao({ id: -1, tipo: "portao", largura: m.portao.largura, altura: m.portao.altura, estore: false, centro: 0 }, est.pe, [], (e.cobertura || {}).tipo === "escondida");
    e.portao = { largura: Math.max(2.0, Math.min(v.largura, Math.round((e.largura - 0.65) * 20) / 20)), altura: Math.max(2.0, v.altura) };
  }
  const f1 = EX.pegadaSeparado(e);
  e.x = arred(e.x + cx - (f1.x0 + f1.x1) / 2);
  e.y = arred(e.y + cy - (f1.y0 + f1.y1) / 2);
  const erro = porqueNaoSeparado(e);
  if (erro) { Object.assign(e, JSON.parse(antes)); est.erro = `Assim não: ${erro}.`; } else { est.erro = ""; mudou(); }
  cena3D(); desenhar();
}

// a garage's gate: the opening on an attached one's front (the client edits it here as in step 6 — user 2026-10-30:
// "Colocar a porta da garagem ajustável de forma ao cliente poder escolher a largura e altura respeitando as nossas regras
// estruturais"), a separate one's {largura, altura}
function portaoDe(b) {
  if (b.tipo !== "garagem") return null;
  if (b.modo === "separado") {
    const c = EX.casaSeparada(b, { acabamentos: est.acabamentos, pe_direito: est.pe }).vaos[0];
    return { largura: c.largura, altura: c.altura };
  }
  const v = b.portao != null ? vaoDe(b.portao) : null;
  if (v) return v;
  const n = b.base && b.base.n, r = b.rect;
  if (!n || !r) return null;
  const D = Math.abs(n[0]) > 0.5 ? r.x1 - r.x0 : r.y1 - r.y0, q = EX.ladoPor(est.cont, [b.base.ponto[0] + n[0] * D, b.base.ponto[1] + n[1] * D], n);
  return q ? est.vaos.find((x) => x.tipo === "portao" && x.lado === q.lado) || null : null;
}

function remover7() {
  const s = est.sel;
  if (!s) return;
  if (s.tipo === "pergola") est.exteriores.pergolas = est.exteriores.pergolas.filter((p) => p.id !== s.id);
  else {
    const b = blocoDe(s.id);
    if (!b) return;
    if (b.modo === "junto") { est.sel = null; tirarBloco(b); cena3D(); desenhar(); return; }
    est.exteriores.blocos = est.exteriores.blocos.filter((x) => x.id !== b.id);
  }
  est.sel = null;
  mudou(); cena3D(); desenhar();
}

const interacaoExteriores = {
  premir(info) {
    est.erro = "";
    const f = est.form7, a = info.alvo;
    if (f && f.tipo === "pergola") { // on a wall's cladding, centred where clicked
      if (!a || a.lado === undefined) { est.erro = "A pérgola encosta-se a uma parede exterior: clique numa delas."; desenhar(); return false; }
      const l = lados(est.cont)[a.lado], s = noLado(info, l);
      const pg = novaPergola(a.lado, s ?? l.comprimento / 2);
      cena.previa(null);
      if (!pg) { desenhar(); return false; }
      est.sel = { tipo: "pergola", id: pg.id }; est.form7 = null; est.ferramenta = null;
      mudou(); cena3D(); desenhar();
      return false;
    }
    if (f && f.modo === "junto") {
      if (!a || a.lado === undefined) { est.erro = `Clique numa parede da casa para juntar ${f.tipo === "garagem" ? "a garagem" : "o anexo"}.`; desenhar(); return false; }
      const l = lados(est.cont)[a.lado], s = noLado(info, l);
      cena.previa(null);
      const r = juntarBloco(f.tipo, a.lado, s ?? l.comprimento / 2, f.largura, f.area);
      if (r.erro) { est.erro = `Aqui não: ${r.erro}.`; desenhar(); return false; }
      est.sel = { tipo: "bloco", id: r.bloco.id }; est.form7 = null; est.ferramenta = null;
      cena3D(); desenhar();
      return false;
    }
    if (f && f.modo === "separado") {
      if (!info.chao) return false;
      cena.previa(null);
      const r = colocarSeparado(f, info.chao);
      if (r.erro) { est.erro = `Aqui não: ${r.erro}.`; desenhar(); return false; }
      est.sel = { tipo: "bloco", id: r.e.id }; est.form7 = null; est.ferramenta = null;
      mudou(); cena3D(); desenhar();
      return false;
    }
    // nothing being added: a pergola (dragged along its wall), a separate building (dragged on the ground), an attached one
    if (a && a.pergola !== undefined) {
      const pg = pergolaDe(a.pergola), s = pg && noLado(info, lados(est.cont)[pg.lado]);
      if (pg) {
        est.sel = { tipo: "pergola", id: pg.id }; est.arr = { pergola: pg.id, ds: (s ?? pg.s0) - pg.s0 };
        cena3D(); desenhar();
        return true;
      }
    }
    const p = info.chao;
    const dentro = (r) => p && p[0] > r.x0 && p[0] < r.x1 && p[1] > r.y0 && p[1] < r.y1;
    const sep = est.exteriores.blocos.find((b) => b.modo === "separado" && dentro(EX.pegadaSeparado(b)));
    if (sep) {
      est.sel = { tipo: "bloco", id: sep.id }; est.arr = { sep: sep.id, p0: p, x0: sep.x, y0: sep.y, ok: [sep.x, sep.y] };
      cena3D(); desenhar();
      return true;
    }
    const jb = est.exteriores.blocos.find((b) => b.modo === "junto" && dentro(b.rect));
    if (jb) { est.sel = { tipo: "bloco", id: jb.id }; cena3D(); desenhar(); return false; }
    if (est.sel) { est.sel = null; cena3D(); desenhar(); }
    return false;
  },
  arrastar(info) {
    const A = est.arr;
    if (!A) return;
    if (A.pergola !== undefined) {
      const pg = pergolaDe(A.pergola), s = noLado(info, lados(est.cont)[pg.lado]);
      if (s === null) return;
      const antes = { ...pg };
      posicionarPergola(pg, s - A.ds);
      if (porqueNaoPergola(pg)) Object.assign(pg, antes);
      A.moveu = A.moveu || antes.s0 !== pg.s0;
      fantasmaPergola(pg);
      desenharSelecao7();
    } else if (A.sep !== undefined && info.chao) {
      const e = blocoDe(A.sep);
      e.x = arred(A.x0 + info.chao[0] - A.p0[0]);
      e.y = arred(A.y0 + info.chao[1] - A.p0[1]);
      if (porqueNaoSeparado(e)) [e.x, e.y] = A.ok; else { A.moveu = A.moveu || e.x !== A.x0 || e.y !== A.y0; A.ok = [e.x, e.y]; }
      desenharSeparados();
    }
  },
  largar() {
    if (!est.arr) return;
    const moveu = est.arr.moveu;
    est.arr = null;
    cena.previa(null);
    if (moveu) mudou();
    cena3D(); desenhar();
  },
  pairar(info) {
    const f = est.form7, a = info.alvo;
    if (f && (f.tipo === "pergola" || f.modo === "junto")) { // a ghost where it would go
      if (!a || a.lado === undefined) { cena.previa(null); cena.cursor("not-allowed"); return; }
      const l = lados(est.cont)[a.lado], s = noLado(info, l) ?? l.comprimento / 2;
      if (f.tipo === "pergola") {
        const W = Math.min(4.0, l.comprimento), pg = { id: -1, lado: a.lado, s0: 0, s1: W, projecao: 3.0, altura: null };
        posicionarPergola(pg, s - W / 2);
        fantasmaPergola(pg, !!porqueNaoPergola(pg));
      } else {
        const b = EX.blocoJunto(est.cont, a.lado, s, f.largura, profundidade(f.area, f.largura));
        cena.previa(b ? { tipo: "caixa", ...b.rect, z0: 0, z1: est.pe + 0.3 } : null, !b || !!EX.combinar(est.cont, b.rect, "uniao").erro);
      }
      cena.cursor("copy");
      return;
    }
    if (f && f.modo === "separado") {
      if (!info.chao) { cena.previa(null); return; }
      const W = f.largura, D = profundidade(f.area, f.largura);
      const e = { id: -1, x: arred(info.chao[0] - W / 2), y: arred(info.chao[1] - D / 2), rot: 0, largura: W, profundidade: D };
      cena.previa({ tipo: "caixa", ...EX.pegadaSeparado(e), z0: 0, z1: est.pe + 0.3 }, !!porqueNaoSeparado(e));
      cena.cursor("copy");
      return;
    }
    cena.previa(null);
    const p = info.chao, sobreSep = p && est.exteriores.blocos.some((b) => b.modo === "separado" && (() => { const r = EX.pegadaSeparado(b); return p[0] > r.x0 && p[0] < r.x1 && p[1] > r.y0 && p[1] < r.y1; })());
    cena.cursor((a && a.pergola !== undefined) || sobreSep ? "grab" : "");
  },
};

function painel7() {
  const f = est.form7;
  const cartoes = ["pergola", "garagem", "anexo"].map((k) => `<button class="cartao${f && f.tipo === k ? " ativo" : ""}" data-ext7="${k}">
    <span class="fig">${IMAGENS[k]}</span><strong>${NOME7[k]}</strong><span>${NOTA7[k]}</span></button>`).join("");
  return `${cab(7, "Pérgolas, garagens e anexos")}
    <p>Uma pérgola numa fachada; uma garagem ou um anexo junto à casa (mesma estrutura e cobertura, porta para a casa) ou
    separado, a ${m2(AFASTAR_CASA)} m ou mais (cobertura à escolha).</p>
    <div class="cartoes">${cartoes}</div>
    ${formulario7()}
    <p class="erro" id="erro">${est.erro}</p>
    <div id="selecao">${htmlSelecao7()}</div>
    ${est.avisos.length ? `<div class="nota">${est.avisos.map((x) => `<p>${x}</p>`).join("")}</div>` : ""}
    ${listaExteriores()}
    ${est.cobertura.tipo !== "escondida" && est.motorPronto && est.cob && !est.faces ? `<p class="aviso">A cobertura à vista ainda não pôde ser calculada para esta forma.</p>` : ""}
    ${blocoEstrutura()}${navegar()}`;
}

function formulario7() {
  const f = est.form7;
  if (!f) return "";
  if (f.tipo === "pergola") {
    const mx = alturaMaxPg();
    return `<p class="info"><strong>Clique na parede onde a quer.</strong> Depois acerte largura, projeção e altura${mx ? ` (até ${m2(mx)} m: o topo da pérgola fica à altura do piso térreo)` : ""}. Esc cancela.</p>`;
  }
  const T = EX.TIPOS_EXT[f.tipo], sep = f.modo === "separado";
  return `<div class="grelha">
      <label>Área</label>${numero("e7-area", f.area.toFixed(1), T.area_min, T.area_max, 0.5, "m²")}
      <label>Frente</label>${numero("e7-larg", f.largura.toFixed(2), T.largura_min, 12, 0.05)}
    </div>
    <p class="info">Fundo: ${m2(profundidade(f.area, f.largura))} m.</p>
    <div class="escolhas"><button class="escolha${sep ? "" : " ativo"}" data-modo7="junto">Junto à casa (com ligação)</button><button class="escolha${sep ? " ativo" : ""}" data-modo7="separado">${separad(f.tipo)[0].toUpperCase()}${separad(f.tipo).slice(1)}</button></div>
    ${sep ? `<label>Cobertura</label><div class="escolhas">${["escondida", "duas_aguas"].map((k) => `<button class="escolha${f.cobertura.tipo === k ? " ativo" : ""}" data-cob7="${k}">${nomeCobSep(k)}</button>`).join("")}</div>`
      : `<p class="info">Com a estrutura e a cobertura da casa; uma porta interior para a casa.</p>`}
    <p class="info"><strong>${sep ? `Clique no terreno, a ${m2(AFASTAR_CASA)} m ou mais da casa.` : "Clique na parede da casa onde a quer."}</strong> Esc cancela.</p>`;
}

function htmlSelecao7() {
  const s = est.sel;
  if (!s) return "";
  if (s.tipo === "pergola") {
    const pg = pergolaDe(s.id);
    if (!pg) return "";
    const l = lados(est.cont)[pg.lado], mx = alturaMaxPg(pg), R = PG();
    return `<div class="selecao"><h3>Pérgola · lado ${pg.lado + 1}</h3><div class="grelha">
      <label>Largura</label>${numero("p7-larg", (pg.s1 - pg.s0).toFixed(2), R.largura_min, l.comprimento.toFixed(2), 0.05)}
      <label>Projeção</label>${numero("p7-proj", pg.projecao.toFixed(2), R.projecao[0], R.projecao[1], 0.05)}
      <label>Altura junto à casa</label>${numero("p7-alt", Math.min(pg.altura ?? mx ?? 2.6, mx ?? 9).toFixed(2), R.altura_min, mx ?? 3, 0.01)}
      <label>Ao início do lado</label>${numero("p7-pos", pg.s0.toFixed(2), 0, l.comprimento, 0.05)}
    </div><p class="info">Altura das vigas junto à fachada${mx ? ` (máx. ${m2(mx)} m${est.cobertura.tipo !== "escondida" ? ", debaixo do beirado" : ""})` : ""}; caem ${Math.round(R.inclinacao * 100)} % para a frente. Arraste-a ao longo da parede.</p><div class="acoes"><button class="btn" id="remover7">Remover</button></div></div>`;
  }
  const b = blocoDe(s.id);
  if (!b) return "";
  const T = EX.TIPOS_EXT[b.tipo];
  const pt = portaoDe(b), PC = CATALOGO.portao;
  const camposPortao = (id) => (b.tipo !== "garagem" ? "" : pt
    ? `<label>Portão: largura</label>${numero(`${id}-pl`, pt.largura.toFixed(2), 2.0, PC.max, 0.05)}<label>Portão: altura</label>${numero(`${id}-pa`, pt.altura.toFixed(2), 2.0, 3.0, 0.05)}`
    : "");
  const dentro = `<p class="info">Paredes por dentro: no passo 4 (Paredes interiores).</p>`;
  if (b.modo === "junto") return `<div class="selecao"><h3>${T.nome} junto à casa · ${m2(b.area)} m²</h3><div class="grelha">
      <label>Área</label>${numero("b7-area", b.area.toFixed(1), T.area_min, T.area_max, 0.5, "m²")}
      <label>Frente</label>${numero("b7-larg", b.largura.toFixed(2), T.largura_min, 12, 0.05)}
      ${camposPortao("b7")}
    </div><p class="info">Mesma estrutura e cobertura da casa; porta para a casa.${b.tipo === "garagem" && !pt ? " Sem portão: não coube na frente." : ""}</p>${dentro}
    <div class="acoes"><button class="btn" id="remover7">Remover</button></div></div>`;
  return `<div class="selecao"><h3>${T.nome} ${separad(b.tipo)} · ${m2(b.largura * b.profundidade)} m²</h3><div class="grelha">
      <label>Frente</label>${numero("s7-larg", b.largura.toFixed(2), T.largura_min, 12, 0.05)}
      <label>Fundo</label>${numero("s7-prof", b.profundidade.toFixed(2), 2, 12, 0.05)}
      ${camposPortao("s7")}
    </div><label>Cobertura</label><div class="escolhas">${["escondida", "duas_aguas"].map((k) => `<button class="escolha${b.cobertura.tipo === k ? " ativo" : ""}" data-scob7="${k}">${nomeCobSep(k)}</button>`).join("")}</div>
    <p class="info">Arraste-${b.tipo === "garagem" ? "a" : "o"} no terreno (a ${m2(AFASTAR_CASA)} m ou mais da casa). Sem paredes interiores: só junto à casa.</p>
    <div class="acoes"><button class="btn" id="rodar7">Rodar 90°</button><button class="btn" id="remover7">Remover</button></div></div>`;
}

function listaExteriores() {
  const it = [...est.exteriores.pergolas.map((p) => ({ k: "pergola", id: p.id, t: `Pérgola ${m2(p.s1 - p.s0)} × ${m2(p.projecao)} m · lado ${p.lado + 1}` })),
    ...est.exteriores.blocos.map((b) => ({ k: "bloco", id: b.id,
      t: `${EX.TIPOS_EXT[b.tipo].nome} ${b.modo === "junto" ? "junto à casa" : separad(b.tipo)} · ${m2(b.modo === "junto" ? b.area : b.largura * b.profundidade)} m²` }))];
  if (!it.length) return "";
  return `<label>Acrescentados</label><div class="lista7">${it.map((x) => `<button class="escolha${est.sel && est.sel.tipo === x.k && est.sel.id === x.id ? " ativo" : ""}" data-sel7="${x.k}:${x.id}">${x.t}</button>`).join("")}</div>`;
}

function desenharSelecao7() { // during a drag: only the selection's numbers
  const el = $("#selecao");
  if (el) { el.innerHTML = htmlSelecao7(); ligarSelecao7(); }
  preco();
}

function ligar7() {
  const q = (sel) => painel.querySelectorAll(sel);
  q("[data-ext7]").forEach((b) => b.onclick = () => {
    const k = b.dataset.ext7;
    if (est.form7 && est.form7.tipo === k) est.form7 = null;
    else est.form7 = k === "pergola" ? { tipo: k } : { tipo: k, modo: "junto", area: EX.TIPOS_EXT[k].area, largura: EX.TIPOS_EXT[k].largura,
      cobertura: { tipo: "escondida", inclinacao: INCLINACAO_MIN, beirado: 0.25 } };
    est.ferramenta = est.form7 ? k : null;
    est.sel = null; est.erro = "";
    cena.previa(null);
    if (est.verEstrutura) verEstrutura(false);
    cena3D(); desenhar();
  });
  q("[data-modo7]").forEach((b) => b.onclick = () => { est.form7.modo = b.dataset.modo7; cena.previa(null); desenhar(); });
  q("[data-cob7]").forEach((b) => b.onclick = () => { est.form7.cobertura.tipo = b.dataset.cob7; desenhar(); });
  if ($("#e7-area")) $("#e7-area").onchange = (e) => {
    const T = EX.TIPOS_EXT[est.form7.tipo];
    est.form7.area = Math.min(T.area_max, Math.max(T.area_min, Number(e.target.value) || T.area));
    desenhar();
  };
  if ($("#e7-larg")) $("#e7-larg").onchange = (e) => {
    const T = EX.TIPOS_EXT[est.form7.tipo];
    est.form7.largura = Math.min(12, Math.max(T.largura_min, arred(Number(e.target.value) || T.largura)));
    desenhar();
  };
  q("[data-sel7]").forEach((b) => b.onclick = () => {
    const [k, id] = b.dataset.sel7.split(":");
    est.sel = { tipo: k, id: Number(id) }; est.form7 = null; est.ferramenta = null;
    cena3D(); desenhar();
  });
  ligarSelecao7();
}

function ligarSelecao7() {
  const s = est.sel;
  if ($("#remover7")) $("#remover7").onclick = remover7;
  if (!s) return;
  if (s.tipo === "pergola") {
    const pg = pergolaDe(s.id);
    if (!pg || !$("#p7-larg")) return;
    $("#p7-larg").onchange = (e) => acertarPergola(pg, { largura: Number(e.target.value) });
    $("#p7-proj").onchange = (e) => acertarPergola(pg, { projecao: Number(e.target.value) });
    $("#p7-alt").onchange = (e) => acertarPergola(pg, { altura: Number(e.target.value) });
    $("#p7-pos").onchange = (e) => acertarPergola(pg, { s0: Number(e.target.value) });
    return;
  }
  const b = blocoDe(s.id);
  if (!b) return;
  if (b.modo === "junto") {
    if ($("#b7-area")) $("#b7-area").onchange = (e) => editarJunto(b, { area: Number(e.target.value) });
    if ($("#b7-larg")) $("#b7-larg").onchange = (e) => editarJunto(b, { largura: Number(e.target.value) });
    const v = portaoDe(b);
    if (v && $("#b7-pl")) $("#b7-pl").onchange = (e) => editarVao(v, (x) => ({ ...x, largura: Number(e.target.value) }));
    if (v && $("#b7-pa")) $("#b7-pa").onchange = (e) => editarVao(v, (x) => ({ ...x, altura: Number(e.target.value) }));
    return;
  }
  if ($("#s7-pl")) $("#s7-pl").onchange = (e) => acertarSeparado(b, { portao: { ...portaoDe(b), largura: Number(e.target.value) } });
  if ($("#s7-pa")) $("#s7-pa").onchange = (e) => acertarSeparado(b, { portao: { ...portaoDe(b), altura: Number(e.target.value) } });
  if ($("#s7-larg")) $("#s7-larg").onchange = (e) => acertarSeparado(b, { largura: Number(e.target.value) });
  if ($("#s7-prof")) $("#s7-prof").onchange = (e) => acertarSeparado(b, { profundidade: Number(e.target.value) });
  painel.querySelectorAll("[data-scob7]").forEach((x) => x.onclick = () => acertarSeparado(b, { cobertura: { ...b.cobertura, tipo: x.dataset.scob7 } }));
  if ($("#rodar7")) $("#rodar7").onclick = () => acertarSeparado(b, { rot: ((b.rot || 0) + 1) % 4 });
}

// ---------------------------------------------------------------- price (always visible)
function preco() {
  const o = orcamento({
    area: est.cont ? area(est.cont) : 0, altura: alturaExt(), pe: est.pe, paredes: est.paredes,
    vaos: fechada() ? est.vaos : [], interiores: rs().filter((r) => !PI.porqueNao(est.cont, est.vaos, rs(), r)),
    acabamentos: est.acabamentos, cobertura: fechada() ? { ...est.cobertura, nome: nomeCob(est.cobertura.tipo) } : null,
    divisoes: ds().map((d) => ({ area: d.area, material: pavDe(d) })),
    facesExt: Object.entries(est.facesExt).map(([lado, material]) => ({ area: (lados(est.cont)[lado]?.comprimento || 0) * est.pe, material })),
  });
  for (const l of linhasExteriores()) { o.linhas.push(l); o.total += l.valor; }
  $("#total-valor").textContent = euros(o.total);
  $("#lista-linhas").innerHTML = o.linhas.map((l) => `<li><span>${l.rotulo}</span><strong>${euros(l.valor)}</strong></li>`).join("")
    || "<li><span>Ainda nada escolhido</span></li>";
  $("#lista-aviso").textContent = PRECOS_EXEMPLO.aviso;
}
$("#total").onclick = () => { $("#lista").hidden = !$("#lista").hidden; };

// ---------------------------------------------------------------- the steps
function estado(t) { $("#estado").textContent = t; }

function mostrar(grupo, sim) {
  const grupos = grupo === "paredes" ? ["paredes", "empenas", "vaos", "interiores", "chao", "exteriores"] : grupo === "cobertura" ? ["telhado"] : [grupo];
  for (const g of grupos) cena.mostrar(g, sim);
  if (grupo === "paredes") cena.mostrar("telhado", sim && est.verCobertura);
  const b = document.querySelector(`[data-mostrar="${grupo}"]`);
  if (b) b.classList.toggle("ativo", sim);
}

function verEstrutura(sim) {
  est.verEstrutura = sim;
  mostrar("estrutura", sim);
  mostrar("paredes", !sim);
  if (sim && !est.G && !est.aCalcular) construirComMetodo();
  cena3D();
  desenhar();
}

function irPara(passo) {
  est.passo = passo;
  est.sel = null;
  est.ferramenta = null;
  est.pincel = null;
  pararDesenho();
  est.erro = "";
  cena.previa(null);
  cena.marca(null);
  cotas(est.cont);
  est.form7 = null;
  cena.interagir(passo === 4 ? interacaoInteriores : passo === 6 ? interacaoVaos : passo === 7 ? interacaoExteriores : null);
  if (passo === 7) est.verCobertura = true;
  // the roof hidden to draw the inside, shown to choose it; the button stays from step 4 on (user 2026-10-21)
  if (passo === 4) est.verCobertura = false;
  if (passo === 5) est.verCobertura = true;
  const b = document.querySelector('[data-mostrar="cobertura"]');
  b.hidden = passo < 4;
  b.classList.toggle("ativo", est.verCobertura);
  const bt = document.querySelector('[data-mostrar="teto"]'); // the false ceiling, from the inside steps on
  bt.hidden = passo < 4;
  bt.classList.toggle("ativo", est.verTeto);
  // the camera stays where the client left it (user 2026-10-29: "quero que continue na câmara que o cliente estava
  // anteriormente"); it is framed only for a new base and by the 3D / Vista de cima buttons
  guardarLocal();
  if (passo >= 4) pedirTelhado();
  cena3D();
  desenhar();
}

function miniatura(forma) {
  const c = contorno(forma, 100);
  const xs = c.map((p) => p[0]), ys = c.map((p) => p[1]);
  const W = Math.max(...xs), H = Math.max(...ys), k = Math.min(110 / W, 60 / H);
  const pts = c.map(([x, y]) => `${(5 + x * k).toFixed(1)},${(65 - y * k).toFixed(1)}`).join(" ");
  return `<svg viewBox="0 0 120 70"><polygon points="${pts}" fill="#e7e9ec" stroke="#1d1f21" stroke-width="1.5"/></svg>`;
}

function planta() {
  const c = est.cont, ls = lados(c);
  const xs = c.map((p) => p[0]), ys = c.map((p) => p[1]);
  const W = Math.max(...xs), H = Math.max(...ys), k = Math.min(280 / W, 160 / H);
  const P = ([x, y]) => [15 + x * k, 175 - y * k];
  let s = `<svg class="planta" viewBox="0 0 310 190">`;
  s += `<polygon points="${c.map((p) => P(p).join(",")).join(" ")}" fill="#f3f4f6"/>`;
  for (const l of ls) {
    const [a, b] = [P(l.p0), P(l.p1)];
    s += `<line class="lado${est.ladoEscolhido === l.i ? " escolhido" : ""}" data-lado="${l.i}" x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}"><title>Lado ${l.i + 1}: ${l.comprimento.toFixed(2)} m</title></line>`;
  }
  for (const p of est.paredes) {
    const l = ls[p.lado], d = [(l.p1[0] - l.p0[0]) / l.comprimento, (l.p1[1] - l.p0[1]) / l.comprimento];
    const a = P([l.p0[0] + d[0] * (p.s0 + 0.05), l.p0[1] + d[1] * (p.s0 + 0.05)]);
    const b = P([l.p0[0] + d[0] * (p.s1 - 0.05), l.p0[1] + d[1] * (p.s1 - 0.05)]);
    s += `<line class="parede" x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}"/>`;
  }
  return s + "</svg>";
}

const cab = (n, titulo) => `<h2>Passo ${n} de ${PASSOS.length} · ${PASSOS[n - 1]}</h2><h1>${titulo}</h1>`;
const numero = (id, valor, min, max, passo, un = "m") =>
  `<div class="numero"><input type="number" id="${id}" min="${min}" max="${max}" step="${passo}" value="${valor}"><span>${un}</span></div>`;
const cartaoMat = (m, ativo, attr) => `<button class="cartao${ativo ? " ativo" : ""}" ${attr}>
  <span class="fig"><img src="${previa(m.id, est.materiais)}" alt=""></span><strong>${m.nome}</strong><span>${m.nota}</span></button>`;

function blocoEstrutura() {
  if (!fechada()) return "";
  const r = est.resultado;
  let s = `<div class="acoes"><button class="btn${est.verEstrutura ? "" : " cheio"}" id="metodo" ${est.aCalcular ? "disabled" : ""}>${
    est.aCalcular ? "A calcular…" : est.verEstrutura ? "Ver a casa acabada" : "Ver como a construímos"}</button></div>`;
  if (r && r.avisos && r.avisos.length) s += `<div class="nota">${r.avisos.map((a) => `<p>${a}</p>`).join("")}</div>`;
  if (r && r.erro && !INTERNO) s += `<p class="aviso">Não foi possível calcular esta casa — experimente mudar uma parede ou um vão.</p>`;
  if (INTERNO && r && !r.erro) s += `<div class="interno">(interno) ${r.ext} módulos exteriores, ${r.int} interiores; ${(r.ms / 1000).toFixed(2)} s\n${[...(r.notas || []), ...(r.avisosInternos || [])].join("\n")}</div>`;
  else if (INTERNO && r && r.erro) s += `<div class="interno">(interno) erro: ${r.erro}</div>`;
  return s;
}

const navegar = (podeSeguir = true) => `<div class="navegar"><button class="btn" id="voltar">Voltar</button>${
  est.passo < PASSOS.length ? `<button class="btn cheio" id="seguinte" ${podeSeguir ? "" : "disabled"}>Seguinte</button>` : "<span></span>"}</div>`;

// the selected opening: its values, typed (the panel part that follows a drag)
function htmlSelecao() {
  const s = est.sel;
  if (s && s.tipo === "porta") return `<div class="selecao"><h3>Porta interior · 0,80 × 2,00 m</h3>
    <p class="info">Arraste-a ao longo da parede interior.</p><div class="acoes"><button class="btn" id="remover">Remover</button></div></div>`;
  if (!s || s.tipo !== "vao") return "";
  const v = vaoDe(s.id);
  if (!v) return "";
  const c = CATALOGO[v.tipo], l = lados(est.cont)[v.lado];
  return `<div class="selecao"><h3>${c.nome} · lado ${v.lado + 1}</h3>
    <div class="grelha">
      <label>Largura</label>${numero("v-larg", v.largura.toFixed(2), 0.4, c.max, 0.05)}
      <label>Altura</label>${numero("v-alt", v.altura.toFixed(2), 0.4, 3, 0.05)}
      ${c.chao ? "" : `<label>Peitoril</label>${numero("v-peit", v.peitoril.toFixed(2), 0.2, 2, 0.05)}`}
      <label>Ao início do lado</label>${numero("v-pos", (v.centro - v.largura / 2).toFixed(2), 0, l.comprimento, 0.05)}
    </div>
    ${v.tipo === "porta" || v.tipo === "portao" ? "" : `<label class="caixa"><input type="checkbox" id="v-est" ${v.estore ? "checked" : ""}> Estore exterior</label>`}
    ${c.chao ? "" : `<label class="caixa"><input type="checkbox" id="v-fosco" ${v.vidro === "fosco" ? "checked" : ""}> Vidro fosco</label>`}
    <div class="acoes"><button class="btn" id="remover">Remover</button></div></div>`;
}

// an opening changed (step 6, and the garage gate in step 7): within the method's limits, where it fits
function editarVao(v, f) {
  est.erro = "";
  const novo = acertarVao(f({ ...v }), est.pe, (est.avisos = []), escondida());
  const c = centro(novo, novo.centro);
  if (c === null) { est.erro = "Assim não cabe nesta parede."; desenhar(); return; }
  Object.assign(v, novo, { centro: c });
  mudou(); cena3D(); desenhar();
}

function ligarSelecao() {
  const s = est.sel;
  if ($("#remover")) $("#remover").onclick = () => remover();
  if (!s || s.tipo !== "vao") return;
  const v = vaoDe(s.id);
  if (!v || !$("#v-larg")) return;
  const aplicar = (f) => editarVao(v, f);
  $("#v-larg").onchange = (e) => aplicar((x) => ({ ...x, largura: Number(e.target.value) }));
  $("#v-alt").onchange = (e) => aplicar((x) => ({ ...x, altura: Number(e.target.value) }));
  if ($("#v-peit")) $("#v-peit").onchange = (e) => aplicar((x) => ({ ...x, peitoril: Number(e.target.value) }));
  $("#v-pos").onchange = (e) => aplicar((x) => ({ ...x, centro: Number(e.target.value) + x.largura / 2 }));
  if ($("#v-est")) $("#v-est").onchange = (e) => aplicar((x) => ({ ...x, estore: e.target.checked }));
  if ($("#v-fosco")) $("#v-fosco").onchange = (e) => aplicar((x) => ({ ...x, vidro: e.target.checked ? "fosco" : "transparente" }));
}

function desenharSelecao() { // during a drag: only the selection's numbers and the message
  const el = $("#selecao");
  if (el) { el.innerHTML = htmlSelecao(); ligarSelecao(); }
  const er = $("#erro");
  if (er) er.textContent = est.erro;
  hud();
  preco();
}

function desenhar() {
  preco();
  const n = est.passo;
  let html = "";
  if (n === 1) {
    html = `${cab(1, "Escolha a forma da sua casa")}
      <p>Escolha a forma que mais se parece com a casa que quer. No passo seguinte define o tamanho.</p>
      <div class="formas">${Object.entries(FORMAS).map(([k, nome]) =>
        `<button class="forma${est.forma === k ? " ativo" : ""}" data-forma="${k}">${miniatura(k)}${nome}</button>`).join("")}</div>
      <div class="navegar"><span></span><button class="btn cheio" id="seguinte" ${est.forma ? "" : "disabled"}>Seguinte</button></div>`;
  } else if (n === 2) {
    html = `${cab(2, "O tamanho da casa")}
      <p>A base de fundação aparece com o seu preço. Escreva a área total, ou acerte cada lado na vista: escreva a medida
      na etiqueta do lado, ou arraste o lado para fora ou para dentro.</p>
      <label>Área total da base</label>${numero("area-n", area(est.cont).toFixed(1), 30, 400, 1, "m²")}
      ${est.erroBase ? `<p class="erro">${est.erroBase}</p>` : ""}
      <p class="info">Até à face exterior da estrutura; ${lados(est.cont).length} lados.</p>
      <label>Pé direito (altura do chão ao teto)</label>${numero("pe-n", est.pe.toFixed(2), PE_DIREITO.min, PE_DIREITO.max, PE_DIREITO.passo)}
      <div class="escolhas sugestoes">${PE_DIREITO.sugestoes.map((s) =>
        `<button class="escolha${Math.abs(est.pe - s) < 1e-6 ? " ativo" : ""}" data-pe="${s}">${m2(s)} m</button>`).join("")}</div>
      <p class="info">As alturas mais habituais; pode escrever outra (a partir de ${m2(PE_DIREITO.min)} m, o mínimo legal). A estrutura da casa é feita para esta altura.</p>
      ${est.avisos.length ? `<div class="nota">${est.avisos.map((a) => `<p>${a}</p>`).join("")}</div>` : ""}
      ${navegar()}`;
  } else if (n === 3) {
    const ls = lados(est.cont), possiveis = paredesPossiveis(ls);
    const prox = proximaParede(possiveis, est.paredes, est.ladoEscolhido);
    html = `${cab(3, "Monte as paredes")}
      <p>Cada parede tem 3 metros; a última de cada lado fica com o que falta. Clique num lado da planta para escolher onde a próxima parede vai.</p>
      ${planta()}
      <p class="info">${est.paredes.length} de ${possiveis.length} paredes${prox ? ` · próxima no lado ${prox.lado + 1}: ${m2(prox.s1 - prox.s0)} m` : ""}</p>
      <div class="acoes">
        <button class="btn cheio" id="mais" ${prox ? "" : "disabled"}>+ Parede</button>
        <button class="btn" id="menos" ${est.paredes.length ? "" : "disabled"}>− Parede</button>
        <button class="btn" id="todas" ${prox ? "" : "disabled"}>Fechar a casa</button>
      </div>
      ${fechada() ? `<p>A casa está fechada. Siga para as paredes interiores, ou veja como a construímos, pelo nosso método.</p>` : ""}
      ${blocoEstrutura()}${navegar(fechada())}`;
  } else if (n === 4) {
    const nint = rs().length, lista = ds(), aDesenhar = est.ferramenta === "parede";
    html = `${cab(4, "Paredes interiores e pavimento")}
      <p>Clique em <strong>Parede interior</strong> e marque os cantos na casa, clique a clique. Esc para parar.</p>
      <div class="cartoes um"><button class="cartao arrastavel${aDesenhar ? " ativo" : ""}" data-arrastar="parede">
        <span class="fig">${IMAGENS.parede_interior}</span><strong>Parede interior</strong><span>${aDesenhar ? "A desenhar — Esc para parar" : "Clique e desenhe na casa"}</span></button></div>
      <p class="erro" id="erro">${est.erro}</p>
      <label>Materiais das paredes</label>
      <p class="info">${est.pincel ? `<strong>A aplicar: ${MATERIAIS[est.pincel].nome}</strong> — clique numa face (Esc cancela).` : "Clique numa parede e depois no material, ou arraste-o para a parede."}</p>
      <div class="cartoes">${daGrupo("interior").map((m) => cartaoMat(m, est.pincel === m.id, `data-arrastar="material" data-id="${m.id}"`)).join("")}</div>
      <label>Pavimento</label>
      <p class="info">${est.sel && est.sel.tipo === "divisao" ? "Para a divisão escolhida." : "Para a casa toda, ou arraste-o para uma divisão."}</p>
      <div class="cartoes">${daGrupo("pavimento").map((m) => cartaoMat(m, est.acabamentos.pavimento === m.id, `data-arrastar="pavimento" data-id="${m.id}"`)).join("")}</div>
      <p class="info">${nint} ${nint === 1 ? "parede" : "paredes"} · ${lista.length} ${lista.length === 1 ? "divisão" : "divisões"}${lista.length > 1 ? ` (${lista.map((d) => `${d.area.toFixed(1).replace(".", ",")} m²`).join(", ")})` : ""}</p>
      ${blocoEstrutura()}${navegar()}`;
  } else if (n === 5) {
    const c = est.cobertura, ret = casaRet();
    html = `${cab(5, "Exterior e cobertura")}
      <label>Revestimento exterior</label>
      <div class="cartoes">${daGrupo("exterior").map((m) => cartaoMat(m, est.acabamentos.exterior === m.id, `data-ext="${m.id}"`)).join("")}</div>
      <label>Cobertura</label>
      <div class="cartoes">${ORDEM_COB[ret ? "ret" : "varias"].map((k) => { const t = COBERTURAS[k]; return `<button class="cartao${c.tipo === k ? " ativo" : ""}" data-cob="${k}">
        <span class="fig">${IMAGENS[t.img]}</span><strong>${nomeCob(k)}</strong><span>${t.nota}</span></button>`; }).join("")}</div>
      ${c.tipo === "escondida" ? `${est.cob && est.cob.caleiras.length > 1 ? `<label>Lado da caleira (para onde cai a água)</label>
        <div class="escolhas">${est.cob.caleiras.map((b) => `<button class="escolha${est.cob.caleira === b ? " ativo" : ""}" data-caleira="${b}">Lado ${ladoDaBussola(b) + 1}</button>`).join("")}</div>` : ""}
        <p class="info">${est.cob && !est.cob.umaAgua
          ? "Painel sandwich oculto atrás da platibanda, em duas águas com a inclinação mínima e as caleiras por dentro da platibanda (numa só água os painéis ficariam compridos demais); a platibanda sobe até ocultar a cumeeira"
          : `Painel sandwich oculto atrás da platibanda, numa só água com a inclinação mínima e a caleira por dentro da platibanda${est.cob && est.cob.caleira ? ` no lado ${ladoDaBussola(est.cob.caleira) + 1}` : ""}, só do lado baixo; no lado alto um remate fecha o topo dos painéis contra a platibanda, que sobe até ocultar esse lado`}${est.cob && est.cob.zPlat ? ` (${m2(est.cob.zPlat)} m acima da base)` : ""}.</p>` : `
        <div class="grelha">
          <label>Inclinação</label>${numero("cob-inc", c.inclinacao, INCLINACAO_MIN, 100, 1, "%")}
          <label>Beirado</label>${numero("cob-beir", c.beirado.toFixed(2), BEIRADO.min, BEIRADO.max, 0.05)}
        </div>
        <p class="info">Painel sandwich Munditelha (Mundiperfil) na sua cor original, cor telha; inclinação a partir de ${INCLINACAO_MIN} % (agora ${(Math.atan(c.inclinacao / 100) * 180 / Math.PI).toFixed(1).replace(".", ",")}°).${c.tipo === "misto" ? " Rincões: mais cortes no painel e mais remates." : ""}</p>
        ${est.motorPronto && !est.faces ? `<p class="aviso">A cobertura à vista ainda não pôde ser calculada para esta forma.</p>` : ""}`}
      ${blocoEstrutura()}${navegar()}`;
  } else if (n === 6) {
    html = `${cab(6, "Portas e janelas")}
      <p>Escolha um tipo e clique numa parede para o colocar. Arraste-o ao longo da parede para o mudar de sítio.</p>
      <div class="cartoes">${Object.entries(CATALOGO).map(([k, c]) => `<button class="cartao${est.ferramenta === k ? " ativo" : ""}" data-tipo="${k}">
        <span class="fig">${IMAGENS[k]}</span><strong>${c.nome}</strong><span>${m2(c.largura)} × ${m2(c.altura)} m</span></button>`).join("")}
        <button class="cartao${est.ferramenta === PORTA_INT ? " ativo" : ""}" data-tipo="${PORTA_INT}">
        <span class="fig">${IMAGENS.porta_interior}</span><strong>Porta interior</strong><span>0,80 × 2,00 m · nas paredes interiores</span></button></div>
      ${est.ferramenta ? `<p class="info">Clique na parede${est.ferramenta === PORTA_INT ? " interior" : ""} onde quer a ${nomeTipo(est.ferramenta).toLowerCase()} (Esc para cancelar).</p>` : ""}
      <p class="erro" id="erro">${est.erro}</p>
      <div id="selecao">${htmlSelecao()}</div>
      ${est.avisos.length ? `<div class="nota">${est.avisos.map((a) => `<p>${a}</p>`).join("")}</div>` : ""}
      <p class="info">${est.vaos.length} ${est.vaos.length === 1 ? "vão" : "vãos"} · caixilharia em alumínio cinza (RAL 7016) com rotura térmica, vidro duplo.${
        nPortasInt() ? ` ${nPortasInt()} ${nPortasInt() === 1 ? "porta interior" : "portas interiores"}.` : ""}</p>
      ${blocoEstrutura()}${navegar()}`;
  } else {
    html = painel7();
  }
  painel.innerHTML = html;
  ligar();
  hud();
}

function ligar() {
  const n = est.passo;
  const q = (s) => painel.querySelectorAll(s);
  if ($("#voltar")) $("#voltar").onclick = () => irPara(n - 1);
  if ($("#seguinte")) $("#seguinte").onclick = () => irPara(n + 1);
  if ($("#metodo")) $("#metodo").onclick = () => verEstrutura(!est.verEstrutura);
  if (n === 1) {
    q("[data-forma]").forEach((b) => b.onclick = () => { escolherForma(b.dataset.forma); desenhar(); });
  } else if (n === 2) {
    $("#area-n").onchange = (e) => {
      const v = Number(e.target.value);
      if (v >= 30 && v <= 400) novaBase(escalar(est.cont, v));
      else est.erroBase = "Não é possível: a área tem de estar entre 30 e 400 m².";
      desenhar();
    };
    $("#pe-n").onchange = (e) => { mudarPe(Number(e.target.value)); desenhar(); };
    q("[data-pe]").forEach((b) => b.onclick = () => { mudarPe(Number(b.dataset.pe)); desenhar(); });
  } else if (n === 3) {
    const possiveis = paredesPossiveis(lados(est.cont));
    const prox = proximaParede(possiveis, est.paredes, est.ladoEscolhido);
    q("[data-lado]").forEach((el) => el.onclick = () => { est.ladoEscolhido = Number(el.dataset.lado); desenhar(); });
    $("#mais").onclick = () => { est.paredes.push(prox); est.ultima = prox; mudou(true); cena3D(); desenhar(); };
    $("#menos").onclick = () => {
      est.paredes.pop();
      est.ultima = est.paredes[est.paredes.length - 1] || null;
      if (est.verEstrutura) verEstrutura(false);
      mudou(); cena3D(); desenhar();
    };
    $("#todas").onclick = () => {
      let p;
      while ((p = proximaParede(possiveis, est.paredes))) est.paredes.push(p);
      est.ultima = null;
      mudou(true); cena3D(); desenhar();
    };
  } else if (n === 4) {
    q("[data-arrastar]").forEach((b) => b.onpointerdown = (e) => arrastarDoMenu(e, b.dataset.arrastar, b.dataset.id));
  } else if (n === 5) {
    q("[data-ext]").forEach((b) => b.onclick = () => { est.acabamentos.exterior = b.dataset.ext; mudou(); cena3D(); desenhar(); });
    q("[data-cob]").forEach((b) => b.onclick = () => {
      est.cobertura.tipo = b.dataset.cob;
      est.avisos = [];  // under an exposed roof the openings have less room under the ceiling
      est.vaos = est.vaos.map((x) => acertarVao(x, est.pe, est.avisos, escondida()));
      mudou(true); cena3D(); desenhar();
    });
    q("[data-caleira]").forEach((b) => b.onclick = () => { est.cobertura.caleira = b.dataset.caleira; mudou(true); cena3D(); desenhar(); });
    if ($("#cob-inc")) $("#cob-inc").onchange = (e) => {
      est.cobertura.inclinacao = Math.min(100, Math.max(INCLINACAO_MIN, Math.round(Number(e.target.value) || INCLINACAO_MIN)));
      mudou(true); desenhar();
    };
    if ($("#cob-beir")) $("#cob-beir").onchange = (e) => {
      est.cobertura.beirado = Math.min(BEIRADO.max, Math.max(BEIRADO.min, arred(Number(e.target.value) || BEIRADO.min)));
      mudou(true); desenhar();
    };
  } else if (n === 7) {
    ligar7();
  } else {
    q("[data-tipo]").forEach((b) => b.onclick = () => {
      est.ferramenta = est.ferramenta === b.dataset.tipo ? null : b.dataset.tipo;
      est.sel = null; est.erro = "";
      if (est.verEstrutura) verEstrutura(false);
      if (est.ferramenta === PORTA_INT && est.verCobertura) { est.verCobertura = false; mostrar("cobertura", false); } // the inside seen
      cena3D(); desenhar();
    });
    ligarSelecao();
  }
}

// ---------------------------------------------------------------- view bar, keys, saving
document.querySelectorAll("[data-vista]").forEach((b) => b.onclick = () => {
  document.querySelectorAll("[data-vista]").forEach((x) => x.classList.toggle("ativo", x === b));
  if (est.cont) cena.enquadrar(est.cont, b.dataset.vista === "cima");
});
document.querySelectorAll("[data-mostrar]").forEach((b) => b.onclick = () => {
  const sim = !b.classList.contains("ativo");
  if (b.dataset.mostrar === "estrutura") { if (fechada()) verEstrutura(sim); else mostrar("estrutura", sim); }
  else if (b.dataset.mostrar === "cobertura") { est.verCobertura = sim; mostrar("cobertura", sim && !est.verEstrutura); b.classList.toggle("ativo", sim); }
  else if (b.dataset.mostrar === "teto") { est.verTeto = sim; b.classList.toggle("ativo", sim); pedirTeto(); cena3D(); }
  else mostrar(b.dataset.mostrar, sim);
});
window.addEventListener("keydown", (e) => {
  if (e.target.closest && e.target.closest("input")) return;
  const k = e.key.toLowerCase();
  if ((e.ctrlKey || e.metaKey) && (k === "z" || k === "y")) {
    e.preventDefault();
    historico(k === "y" || e.shiftKey ? 1 : -1);
    return;
  }
  if (e.key === "Escape") { // drawing walls: first the wall being drawn, then the tool
    est.erro = "";
    if (est.desenho) pararDesenho();
    else { est.ferramenta = null; est.pincel = null; est.sel = null; est.form7 = null; }
    cena.previa(null); cena.marca(null); cena.medidas(null); cena3D(); desenhar();
  }
  if ((e.key === "Delete" || e.key === "Backspace") && est.sel) { e.preventDefault(); if (est.passo === 7) remover7(); else remover(); }
});

$("#guardar").onclick = () => { // the configured house as a file (with the screen's own state, to open it again)
  if (!est.cont) return;
  const { passo, forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt, exteriores } = est;
  const dados = { ...casaConfigurada(), _prototipo: { v: 3, passo, forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt, exteriores } };
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(dados, null, 1)], { type: "application/json" }));
  a.download = "casa-discovercasa.json";
  a.click();
  URL.revokeObjectURL(a.href);
};
// the brand goes back to the start, the shape of the foundation base (user 2026-10-29: "Botão da discovercasa deve
// levar para o menu inicial dos de escolher a forma da base de fundação"); the design stays until a shape is picked
$("#marca").onclick = () => { if (est.verEstrutura) verEstrutura(false); irPara(1); };
$("#desfazer").onclick = () => historico(-1);
$("#refazer").onclick = () => historico(1);
$("#abrir").onclick = () => $("#ficheiro").click();
$("#ficheiro").onchange = async (e) => {
  const f = e.target.files[0];
  if (!f) return;
  try {
    if (!repor(JSON.parse(await f.text())._prototipo)) throw new Error("sem dados desta versão do configurador");
    mudou(true); irPara(est.passo);
  } catch (err) { estado(`Não foi possível abrir o ficheiro: ${err.message}`); }
  e.target.value = "";
};
$("#recomecar").onclick = () => {
  try { localStorage.removeItem(CHAVE); } catch { /* nothing kept */ }
  location.reload();
};

if (INTERNO) Object.assign(window, { _est: est, _cena: cena, _casa: casaConfigurada, _rs: rs, _juntarBloco: juntarBloco, _desenhar: () => { cena3D(); desenhar(); } }); // checks in the console

// how to move round the house: at the start (until "Não voltar a mostrar"), and from the ? button
const AJUDA = "discovercasa-configurador-ajuda-vista";
function ajuda(sim) {
  $("#ajuda").hidden = !sim;
  if (sim) $("#ajuda-ok").focus();
}
$("#ver-ajuda").onclick = () => ajuda(true);
$("#ajuda-ok").onclick = () => {
  if ($("#ajuda-nao").checked) try { localStorage.setItem(AJUDA, "1"); } catch { /* private window: shown again next time */ }
  ajuda(false);
};
$("#ajuda").onclick = (e) => { if (e.target === $("#ajuda")) ajuda(false); };
window.addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("#ajuda").hidden) { e.stopImmediatePropagation(); ajuda(false); } }, true);
try { if (!localStorage.getItem(AJUDA)) ajuda(true); } catch { ajuda(true); }

let guardado = null;
try { guardado = JSON.parse(localStorage.getItem(CHAVE) || "null"); } catch { guardado = null; }
if (repor(guardado)) irPara(est.passo); else desenhar();
HIST.atual = instantaneo(); // the design as opened: the first state to come back to
