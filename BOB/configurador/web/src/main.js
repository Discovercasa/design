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
import * as PI from "./paredesint.js";
import { PRECOS_EXEMPLO, euros, orcamento } from "./precos.js";

const INTERNO = new URLSearchParams(location.search).has("interno");
const PASSOS = ["Forma", "Tamanho", "Paredes exteriores", "Paredes interiores", "Exterior e cobertura", "Portas e janelas"];
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
const COBERTURAS = {
  escondida: { nome: "Escondida", nota: "atrás da platibanda, com caleiras por dentro", img: "escondida" },
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
  G: null, aCalcular: false, motorPronto: false, resultado: null, verEstrutura: false, materiais: {}, faces: null, zBeirado: null,
};

// ---------------------------------------------------------------- engine
let pedido = 0, pedidoTelhado = 0, pedidoCob = 0, adiado = null, adiadoCob = null;
motor.onmessage = (ev) => {
  const m = ev.data;
  if (m.tipo === "pronto") {
    est.motorPronto = true;
    est.materiais = m.materiais || {};
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
    est.cob = { objetos: m.objetos, zPlat: m.z_platibanda ?? null, rodada: m.rodada, umaAgua: !!m.uma_agua, caleira: m.caleira || null, caleiras: m.caleiras || [] };
    cena3D();
    if (est.passo === 5) desenhar();
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
    const { passo, forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt } = est;
    localStorage.setItem(CHAVE, JSON.stringify({ v: 3, passo, forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt }));
  } catch { /* no storage here: the design simply is not kept */ }
}

// ---------------------------------------------------------------- undo / redo: the design's states, every change of
// it passes through mudou() (dragging shows only the picture and comes here once, at the end)
const HIST = { atras: [], frente: [], atual: null, max: 100 };
function instantaneo() {
  const { forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt } = est;
  return JSON.stringify({ forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt });
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
  cena.paredes(cont, est.paredes, { altura: H, material: matDe(est.acabamentos.exterior), ultima: est.passo === 3 ? est.ultima : null, vaos: furos, parapeito,
    interior: (lado) => matDe(est.facesExt[lado] || "pladur"), selLado: est.passo === 4 && est.sel && est.sel.tipo === "exterior" ? est.sel.lado : null });
  cena.vaos(cont, vs, est.sel && est.sel.tipo === "vao" ? est.sel.id : null);
  cena.interiores(rs(), est.pe, { sel: est.sel && { ...est.sel, ambas: est.ambas }, matDe });
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
  cena.mostrar("telhado", est.verCobertura && !est.verEstrutura);
  hud();
}

// ---------------------------------------------------------------- step 4: interior walls, their faces, the floor
// which face of interior wall r a point (on it) is on
const faceDe = (r, ponto) => (ponto && (r.o === "h" ? ponto[1] : ponto[0]) < r.c ? "neg" : "pos");

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
  const ini = PI.sentido(est.desenho, info.chao); // from a corner: along the wall the pointer goes
  const { w } = PI.segmento(est.cont, lista, ini, info.chao, -1);
  const nova = PI.comNova(est.interiores, ini, w);
  const r = PI.resolver(est.cont, nova).find((x) => x.id === -1);
  const erro = PI.porqueNaoTodas(est.cont, est.vaos, nova);
  if (!r) { cena.previa(null); cena.marca(null); cena.medidas(null); return; }
  const longe = Math.abs(r.a - ini.s0) < Math.abs(r.b - ini.s0) ? r.b : r.a;
  cena.previa({ tipo: "parede", o: r.o, c: r.c, a: r.a, b: r.b, pe: est.pe }, !!erro);
  cena.marca(PI.pt(r.o, r.c, longe), !!erro);
  cena.medidas(aosCantos(est.desenho)); // (from a corner: none)
  cena.cursor("crosshair");
  est.erro = erro ? `Aqui não: ${erro}.` : "";
  const er = $("#erro"); if (er) er.textContent = est.erro;
}

function colocarSegmento(info) {
  const ini = PI.sentido(est.desenho, info.chao);
  const { w, junta } = PI.segmento(est.cont, rs(), ini, info.chao, est.prox);
  const nova = PI.comNova(est.interiores, ini, w);
  const erro = PI.porqueNaoTodas(est.cont, est.vaos, nova);
  if (erro) { est.erro = `Aqui não: ${erro}.`; desenhar(); return; }
  est.interiores = nova;
  est.prox += 1;
  est.desenho = junta ? null : PI.pontaLivre(est.cont, est.interiores, w.id); // go on from its free end
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
        if (!ini) { est.erro = "Comece junto a uma parede, ou na ponta de uma parede interior."; desenhar(); return false; }
        est.desenho = ini;
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
      est.sel = { tipo: "interior", id: r.id, face: faceDe(r, info.ponto || info.chao) };
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

function remover() {
  const s = est.sel;
  if (!s) return;
  if (s.tipo === "vao") est.vaos = est.vaos.filter((v) => v.id !== s.id);
  else if (s.tipo === "porta") { const w = paredeDe(s.parede); if (w) w.portas = w.portas.filter((p) => p.id !== s.id); }
  else if (s.tipo === "interior") {
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
        est.desenho = null; est.sel = null; est.pincel = null; est.erro = "";
        cena.previa(null); cena.marca(null); cena.medidas(null); cena3D(); desenhar();
      } else if (tipo === "material") { // on the face selected, else the next face clicked (once)
        const s = est.sel;
        if (s && s.tipo === "interior") pintar(s.id, est.ambas ? "ambas" : s.face || "pos", id);
        else if (s && s.tipo === "exterior") pintarExterior(s.lado, id);
        else { est.pincel = est.pincel === id ? null : id; est.ferramenta = null; est.desenho = null; cena.marca(null); cena3D(); desenhar(); }
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
    const livre = r.fimA === "livre" || r.fimB === "livre";
    const atual = r.faces[s.face || "pos"];
    el.innerHTML = `<div class="hud-cab"><strong>Parede interior</strong><button class="x" id="hud-x" title="Fechar">×</button></div>
      ${livre ? `<label>Comprimento</label><div class="numero"><input type="number" id="hud-comp" min="${PI.COMPRIMENTO_MIN}" step="0.05" value="${r.comp.toFixed(2)}"><span>m</span></div>`
        : `<p class="info">De parede a parede: ${m2(r.comp)} m</p>`}
      <label>Material desta face</label>
      <div class="mini-mat">${daGrupo("interior").map((m) => `<button class="${atual === m.id ? "ativo" : ""}" data-face-mat="${m.id}" title="${m.nome}"><img src="${previa(m.id, est.materiais)}" alt=""><span>${m.nome}</span></button>`).join("")}</div>
      <label class="caixa"><input type="checkbox" id="hud-ambas" ${est.ambas ? "checked" : ""}> Aplicar às duas faces</label>
      <div class="acoes"><button class="btn cheio" id="hud-porta">+ Porta</button><button class="btn" id="hud-del">Eliminar parede</button></div>`;
  }
  el.hidden = false;
  posicionarHud();
  $("#hud-x").onclick = () => { est.sel = null; cena3D(); desenhar(); };
  $("#hud-del").onclick = remover;
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
      cena.cursor(c === null ? "not-allowed" : "copy");
    } else {
      cena.previa(null);
      cena.cursor(a && (a.vao !== undefined || portaEm(info)) ? "grab" : "");
    }
  },
};

// ---------------------------------------------------------------- price (always visible)
function preco() {
  const o = orcamento({
    area: est.cont ? area(est.cont) : 0, altura: alturaExt(), pe: est.pe, paredes: est.paredes,
    vaos: fechada() ? est.vaos : [], interiores: rs().filter((r) => !PI.porqueNao(est.cont, est.vaos, rs(), r)),
    acabamentos: est.acabamentos, cobertura: fechada() ? { ...est.cobertura, nome: nomeCob(est.cobertura.tipo) } : null,
    divisoes: ds().map((d) => ({ area: d.area, material: pavDe(d) })),
    facesExt: Object.entries(est.facesExt).map(([lado, material]) => ({ area: (lados(est.cont)[lado]?.comprimento || 0) * est.pe, material })),
  });
  $("#total-valor").textContent = euros(o.total);
  $("#lista-linhas").innerHTML = o.linhas.map((l) => `<li><span>${l.rotulo}</span><strong>${euros(l.valor)}</strong></li>`).join("")
    || "<li><span>Ainda nada escolhido</span></li>";
  $("#lista-aviso").textContent = PRECOS_EXEMPLO.aviso;
}
$("#total").onclick = () => { $("#lista").hidden = !$("#lista").hidden; };

// ---------------------------------------------------------------- the steps
function estado(t) { $("#estado").textContent = t; }

function mostrar(grupo, sim) {
  const grupos = grupo === "paredes" ? ["paredes", "empenas", "vaos", "interiores", "chao"] : grupo === "cobertura" ? ["telhado"] : [grupo];
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
  est.desenho = null;
  est.erro = "";
  cena.previa(null);
  cena.marca(null);
  cotas(est.cont);
  cena.interagir(passo === 4 ? interacaoInteriores : passo === 6 ? interacaoVaos : null);
  // the roof hidden to draw the inside, shown to choose it; the button stays from step 4 on (user 2026-10-21)
  if (passo === 4) est.verCobertura = false;
  if (passo === 5) est.verCobertura = true;
  const b = document.querySelector('[data-mostrar="cobertura"]');
  b.hidden = passo < 4;
  b.classList.toggle("ativo", est.verCobertura);
  const bt = document.querySelector('[data-mostrar="teto"]'); // the false ceiling, from the inside steps on
  bt.hidden = passo < 4;
  bt.classList.toggle("ativo", est.verTeto);
  if (est.cont && passo >= 4) {
    cena.enquadrar(est.cont);
    document.querySelectorAll("[data-vista]").forEach((x) => x.classList.toggle("ativo", x.dataset.vista === "3d"));
  }
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

function ligarSelecao() {
  const s = est.sel;
  if ($("#remover")) $("#remover").onclick = remover;
  if (!s || s.tipo !== "vao") return;
  const v = vaoDe(s.id);
  if (!v || !$("#v-larg")) return;
  const aplicar = (f) => {
    est.erro = "";
    const novo = acertarVao(f({ ...v }), est.pe, (est.avisos = []), escondida());
    const c = centro(novo, novo.centro);
    if (c === null) { est.erro = "Assim não cabe nesta parede."; desenhar(); return; }
    Object.assign(v, novo, { centro: c });
    mudou(); cena3D(); desenhar();
  };
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
      <p>Clique em <strong>Parede interior</strong> e depois na casa: um clique junto a uma parede (ou na ponta ou no canto
      de outra parede interior) começa a parede, outro clique acaba-a. Continua a partir da ponta até encostar a outra parede —
      assim fecha uma divisão. Esc para parar. As distâncias aos cantos aparecem no chão; numa parede escolhida pode
      escrevê-las. Clique numa parede, numa divisão ou numa parede exterior para mudar o material.</p>
      <div class="cartoes um"><button class="cartao arrastavel${aDesenhar ? " ativo" : ""}" data-arrastar="parede">
        <span class="fig">${IMAGENS.parede_interior}</span><strong>Parede interior</strong><span>${aDesenhar ? "A desenhar — Esc para parar" : "Clique e desenhe na casa"}</span></button></div>
      <p class="erro" id="erro">${est.erro}</p>
      <label>Materiais das paredes</label>
      <p class="info">Com uma parede escolhida, clique num material para essa face; sem nada escolhido, clique num material e depois na face (interior ou de uma parede exterior), ou arraste-o para lá.${est.pincel ? ` <strong>A aplicar: ${MATERIAIS[est.pincel].nome}</strong> — clique numa face (Esc para cancelar).` : ""}</p>
      <div class="cartoes">${daGrupo("interior").map((m) => cartaoMat(m, est.pincel === m.id, `data-arrastar="material" data-id="${m.id}"`)).join("")}</div>
      <label>Pavimento</label>
      <p class="info">${est.sel && est.sel.tipo === "divisao" ? "Clique num pavimento para a divisão escolhida." : "Para toda a casa; para uma só divisão, clique na divisão (ou arraste o pavimento para ela)."}</p>
      <div class="cartoes">${daGrupo("pavimento").map((m) => cartaoMat(m, est.acabamentos.pavimento === m.id, `data-arrastar="pavimento" data-id="${m.id}"`)).join("")}</div>
      <p class="info">${nint} ${nint === 1 ? "parede interior" : "paredes interiores"}; ${lista.length} ${lista.length === 1 ? "divisão" : "divisões"}${lista.length > 1 ? ` (${lista.map((d) => `${d.area.toFixed(1).replace(".", ",")} m²`).join(", ")})` : ""}; portas interiores de 0,80 × 2,00 m.</p>
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
          ? "Painel sandwich escondido atrás da platibanda, em duas águas com a inclinação mínima e as caleiras por dentro da platibanda (numa só água os painéis ficariam compridos demais); a platibanda sobe até esconder a cumeeira"
          : `Painel sandwich escondido atrás da platibanda, numa só água com a inclinação mínima e a caleira por dentro da platibanda${est.cob && est.cob.caleira ? ` no lado ${ladoDaBussola(est.cob.caleira) + 1}` : ""}; a platibanda sobe até esconder o lado alto`}${est.cob && est.cob.zPlat ? ` (${m2(est.cob.zPlat)} m acima da base)` : ""}.</p>` : `
        <div class="grelha">
          <label>Inclinação</label>${numero("cob-inc", c.inclinacao, INCLINACAO_MIN, 100, 1, "%")}
          <label>Beirado</label>${numero("cob-beir", c.beirado.toFixed(2), BEIRADO.min, BEIRADO.max, 0.05)}
        </div>
        <p class="info">Painel sandwich cinza (RAL 7016); inclinação a partir de ${INCLINACAO_MIN} % (agora ${(Math.atan(c.inclinacao / 100) * 180 / Math.PI).toFixed(1).replace(".", ",")}°).${c.tipo === "misto" ? " Rincões: mais cortes no painel e mais remates." : ""}</p>
        ${est.motorPronto && !est.faces ? `<p class="aviso">A cobertura à vista ainda não pôde ser calculada para esta forma.</p>` : ""}`}
      ${blocoEstrutura()}${navegar()}`;
  } else {
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
    if (est.desenho) est.desenho = null;
    else { est.ferramenta = null; est.pincel = null; est.sel = null; }
    est.erro = ""; cena.previa(null); cena.marca(null); cena.medidas(null); cena3D(); desenhar();
  }
  if ((e.key === "Delete" || e.key === "Backspace") && est.sel) { e.preventDefault(); remover(); }
});

$("#guardar").onclick = () => { // the configured house as a file (with the screen's own state, to open it again)
  if (!est.cont) return;
  const { passo, forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt } = est;
  const dados = { ...casaConfigurada(), _prototipo: { v: 3, passo, forma, cont, pe, paredes, vaos, interiores, acabamentos, cobertura, prox, pavimentos, facesExt } };
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(dados, null, 1)], { type: "application/json" }));
  a.download = "casa-discovercasa.json";
  a.click();
  URL.revokeObjectURL(a.href);
};
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

if (INTERNO) Object.assign(window, { _est: est, _cena: cena, _casa: casaConfigurada, _rs: rs }); // checks in the console

let guardado = null;
try { guardado = JSON.parse(localStorage.getItem(CHAVE) || "null"); } catch { guardado = null; }
if (repor(guardado)) irPara(est.passo); else desenhar();
HIST.atual = instantaneo(); // the design as opened: the first state to come back to
