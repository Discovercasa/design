// Placing the client's doors and windows on the walls (the interior walls: paredesint.js): the screen's snapping and limits only. How each
// one is built (jambs, modules, lintels, the pier between two windows) is the engine's — the repo's Python, which may
// still move an opening and says so. Plan coordinates: metres, X east, Y north, the base outline counter-clockwise.
import { lados } from "./formas.js";

// the clear height: the client chooses any value (user 2026-10-21: "A altura não temos fixa o cliente pode escolher a
// vontade o que preferir"; "O cliente pode escolher qualquer valor mas podemos deixar sugestões … essas 3 sugestões …
// que por norma são o habitual" = 2,40 / 2,50 / 2,60); 2,40 = the RGEU minimum (rulebook §13); 3,50 = ours, only a
// guard against a mistyped value; 2,50 = Torres Vedras as built
export const PE_DIREITO = { min: 2.4, max: 3.5, passo: 0.01, inicial: 2.5, sugestoes: [2.4, 2.5, 2.6] };

// the company's caixilharia "para já" (RAL 7016, thermal break, double glazing — rulebook §3, §11); default sizes from
// the Torres Vedras approved table (basculante 0,80, fixo 1,50 x 0,80, correr 2,00 x 2,20, portão 3,00 x 2,20), the
// window 1,20 x 1,20 and the door 1,00 ours
export const CATALOGO = {
  janela: { nome: "Janela", largura: 1.2, altura: 1.2, peitoril: 1.0, estore: true, chao: false, max: 3.0 },
  janela_correr: { nome: "Janela de correr", largura: 2.0, altura: 2.2, estore: true, chao: true, max: 4.0 },
  // 3 and 4 leaves (user 2026-10-22: "janelas de correr mas 3 janelas e 4 janelas"; sizes ours, to confirm); over 3 m
  // the engine puts a 22x7,5 lintel ("lembra-te mais de 3 metros usamos 22x7,5")
  janela_correr_3: { nome: "Janela de correr 3 folhas", largura: 2.7, altura: 2.2, estore: true, chao: true, max: 4.5 },
  janela_correr_4: { nome: "Janela de correr 4 folhas", largura: 3.6, altura: 2.2, estore: true, chao: true, max: 6.0 },
  porta: { nome: "Porta de entrada", largura: 1.0, altura: 2.2, estore: false, chao: true, max: 1.6 },
  basculante: { nome: "Basculante", largura: 0.8, altura: 0.8, peitoril: 1.4, estore: false, vidro: "fosco", chao: false, max: 1.5 },
  fixo: { nome: "Vidro fixo", largura: 1.5, altura: 0.8, peitoril: 1.2, estore: true, chao: false, max: 3.0 },
  portao: { nome: "Portão de garagem", largura: 3.0, altura: 2.2, estore: false, chao: true, max: 5.0 },
};
export const PORTA_INTERIOR = { largura: 0.87, altura: 2.03 }; // rough opening (method: 0,80 x 2,00 door)

const FOLGA = 0.025;  // rough opening = the frame + 2,5 cm a side (sistema_construtivo caixilharia.folga)
const CANTO = 0.3;    // a rough opening this far from a corner of the base at least (ours: corner post, jamb, other wall)
const ENTRE = 0.08;   // between two rough openings at least one jamb post (closer than a pier: the engine moves windows)
const JUNCAO = 0.15;  // from an interior wall's centre line to a rough opening or a door
const LARGURA_MIN = 0.4, ALTURA_MIN = 0.4, PEITORIL_MIN = 0.2;
const PASSO = 0.05;

export const arred = (v, p = PASSO) => Math.round(Math.round(v / p) * p * 1000) / 1000;
const m2 = (v) => v.toFixed(2).replace(".", ",");

// ---------------------------------------------------------------- doors and windows
export const meia = (v) => v.largura / 2 + FOLGA;   // half the rough opening, along the wall

// the highest frame top: the rough top (the frame + the shutter box) up to the ceiling — user 2026-10-22: "Apenas
// precisamos de 20 cm portanto seria 2,40 de pé direito" (a 2,20 sliding window to the floor + its 0,20 box under
// 2,40; doors have no shutter — 2026-10-27 "Prtas não tem estore apenas as janelas"); under an exposed roof the engine
// raises the exterior modules when the lintel over it needs it (para_construtor, a note); the boxes as para_construtor:
// +0,20 over a window to the floor, +0,15 over a window
export const semEstore = (tipo) => tipo === "porta" || tipo === "portao";
// a garage gate keeps 0,30 under the ceiling for its mechanism (a sectional door — user 2026-10-30, to "Um portão
// seccionado precisa de cerca de 30 cm por cima para o mecanismo. Ponho o limite em pé-direito − 0,30?": "sim exatamente")
export const FOLGA_PORTAO = 0.30;
export function topoMax(v, pe, escondida = true) { // eslint-disable-line no-unused-vars
  const c = CATALOGO[v.tipo];
  const folga = v.tipo === "portao" ? FOLGA_PORTAO : v.estore && !semEstore(v.tipo) ? (c.chao ? 0.2 : 0.125) : FOLGA;
  return Math.floor((pe - folga) * 100 + 1e-6) / 100;
}

// the opening with its sizes inside the limits (a copy); notes in `avisos`
export function acertarVao(v, pe, avisos = [], escondida = true) {
  const c = CATALOGO[v.tipo], n = { ...v };
  if (semEstore(n.tipo)) n.estore = false;
  n.largura = Math.min(Math.max(n.largura, LARGURA_MIN), c.max);
  const tmax = topoMax(n, pe, escondida);
  if (c.chao) {
    if (n.altura > tmax) { avisos.push(`A altura passou a ${m2(tmax)} m para caber debaixo do teto.`); n.altura = tmax; }
  } else {
    n.peitoril = Math.max(n.peitoril ?? c.peitoril, PEITORIL_MIN);
    if (n.peitoril + n.altura > tmax) {
      const alt = Math.max(ALTURA_MIN, Math.floor((tmax - n.peitoril) * 100 + 1e-6) / 100);
      n.peitoril = Math.floor(Math.min(n.peitoril, tmax - alt) * 100 + 1e-6) / 100;
      avisos.push(`A janela foi ajustada (${m2(alt)} m de altura, peitoril ${m2(n.peitoril)} m) para caber debaixo do teto.`);
      n.altura = alt;
    }
  }
  n.altura = Math.max(n.altura, ALTURA_MIN);
  return n;
}

// where interior walls (resolved: {de, ate}) meet side i: distances from the side's start
export function juncoes(cont, paredesInt, i) {
  const l = lados(cont)[i], out = [];
  for (const w of paredesInt) {
    for (const p of [w.de, w.ate]) {
      const t = (p[0] - l.p0[0]) * l.u[0] + (p[1] - l.p0[1]) * l.u[1];
      const d = Math.abs((p[0] - l.p0[0]) * l.n[0] + (p[1] - l.p0[1]) * l.n[1]);
      if (d < 0.02 && t > -0.01 && t < l.comprimento + 0.01) out.push(t);
    }
  }
  return out;
}

// the nearest free centre to c in [lo, hi] outside the blocked intervals, or null
function livreMaisPerto(c, lo, hi, bloqueados) {
  if (lo > hi + 1e-9) return null;
  const dentro = (x) => x >= lo - 1e-9 && x <= hi + 1e-9 && !bloqueados.some(([a, b]) => x > a + 1e-9 && x < b - 1e-9);
  const cand = [arred(Math.min(Math.max(c, lo), hi)), lo, hi];
  for (const [a, b] of bloqueados) cand.push(a, b);
  let melhor = null;
  for (const x of cand) if (dentro(x) && (melhor === null || Math.abs(x - c) < Math.abs(melhor - c))) melhor = x;
  return melhor === null ? null : Math.round(melhor * 1000) / 1000;
}

// the opening v at (or nearest to) centre c on its side, clear of the corners, the other openings and the interior
// walls meeting the side; null when it does not fit
export function centroVao(cont, vaos, paredesInt, v, c) {
  const l = lados(cont)[v.lado], h = meia(v);
  const bl = [];
  for (const o of vaos) if (o.id !== v.id && o.lado === v.lado) bl.push([o.centro - meia(o) - h - ENTRE, o.centro + meia(o) + h + ENTRE]);
  for (const t of juncoes(cont, paredesInt, v.lado)) bl.push([t - h - JUNCAO, t + h + JUNCAO]);
  return livreMaisPerto(c, CANTO + h, l.comprimento - CANTO - h, bl);
}

