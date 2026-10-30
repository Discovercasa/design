// Step 7 — pergolas, garages and annexes (user 2026-10-29: "Acrescentar depois do menu de portas e janelas um menu de
// Pérgolas e Garagens e Espaços exteriores que seja necessário construção por exemplo um anexo"): the screen's geometry
// only — the outline grown by an attached garage / annex, the doors, windows and walls carried over to it, a separate
// building as a configured house of its own. How each is built is the engine's (the repo's Python): an attached one
// is part of the house ("deves juntar a nossa estrutura o espaço a mais e a cobertura tem de ser a mesma que escolheu
// para a casa"), a separate one a house of its own with the roof the client picks ("se for separado pode escolher a
// cobertura que quiser"), a pergola ferramentas/modelo/pergola.py.
import { area, lados, porqueInvalida } from "./formas.js";
import { dentroDaBase } from "./paredesint.js";
import { paredesPossiveis } from "./paredes.js";

const R4 = (v) => Math.round(v * 1e4) / 1e4;
export const ENCOSTAR = 0.6; // a block this close to a corner of the side goes flush with it (ours)

// the defaults of each kind (ours: a garage for one car with a 3,00 gate between 0,30 piers; an annex a small room)
export const TIPOS_EXT = {
  garagem: { nome: "Garagem", largura: 3.7, area: 22.2, area_min: 12, area_max: 80, largura_min: 3.0 },
  anexo: { nome: "Anexo", largura: 3.0, area: 12, area_min: 6, area_max: 60, largura_min: 2.0 },
};

// ---------------------------------------------------------------- an outline plus / minus a rectangle
// (orthogonal outlines as cells between their coordinates; the boundary of the cells traced back, counter-clockwise from
// the lower-left corner, then moved so its lowest corner is at 0, 0): {cont, d: [dx, dy]} or {erro}
export function combinar(cont, rect, modo = "uniao") {
  const xs = [...new Set([...cont.map((p) => R4(p[0])), R4(rect.x0), R4(rect.x1)])].sort((a, b) => a - b);
  const ys = [...new Set([...cont.map((p) => R4(p[1])), R4(rect.y0), R4(rect.y1)])].sort((a, b) => a - b);
  const nx = xs.length - 1, ny = ys.length - 1;
  const dentro = [];
  for (let i = 0; i < nx; i++) {
    dentro.push([]);
    for (let j = 0; j < ny; j++) {
      const c = [(xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2];
      const naCasa = dentroDaBase(cont, c), noRet = c[0] > rect.x0 && c[0] < rect.x1 && c[1] > rect.y0 && c[1] < rect.y1;
      if (modo === "uniao" && naCasa && noRet) return { erro: "fica por cima da casa" };
      dentro[i].push(modo === "uniao" ? naCasa || noRet : naCasa && !noRet);
    }
  }
  const den = (i, j) => i >= 0 && j >= 0 && i < nx && j < ny && dentro[i][j];
  const arestas = new Map(); // start -> [end]: the boundary, the inside on the left
  const pt = (i, j) => `${i},${j}`;
  const add = (a, b) => { if (!arestas.has(a)) arestas.set(a, []); arestas.get(a).push(b); };
  let n = 0;
  for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
    if (!dentro[i][j]) continue;
    if (!den(i, j - 1)) { add(pt(i, j), pt(i + 1, j)); n++; }
    if (!den(i + 1, j)) { add(pt(i + 1, j), pt(i + 1, j + 1)); n++; }
    if (!den(i, j + 1)) { add(pt(i + 1, j + 1), pt(i, j + 1)); n++; }
    if (!den(i - 1, j)) { add(pt(i, j + 1), pt(i, j)); n++; }
  }
  if ([...arestas.values()].some((l) => l.length > 1)) return { erro: "a casa ficava presa só por um canto" };
  const ini = [...arestas.keys()][0];
  if (!ini) return { erro: "não fica nada" };
  const volta = [ini];
  for (let k = arestas.get(ini)[0]; k !== ini; k = arestas.get(k)[0]) {
    volta.push(k);
    if (volta.length > n) return { erro: "a forma não fecha" };
  }
  if (volta.length !== n) return { erro: "ficava um pátio fechado ou duas partes" };
  let pts = volta.map((k) => { const [i, j] = k.split(",").map(Number); return [xs[i], ys[j]]; });
  pts = pts.filter((p, k) => { // corners only
    const a = pts[(k + pts.length - 1) % pts.length], b = pts[(k + 1) % pts.length];
    return Math.abs((p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0])) > 1e-9;
  });
  const x0 = Math.min(...pts.map((p) => p[0])), y0 = Math.min(...pts.map((p) => p[1]));
  const k0 = pts.reduce((m, p, k) => (p[1] < pts[m][1] - 1e-9 || (Math.abs(p[1] - pts[m][1]) < 1e-9 && p[0] < pts[m][0]) ? k : m), 0);
  const novo = [...pts.slice(k0), ...pts.slice(0, k0)].map(([x, y]) => [R4(x - x0), R4(y - y0)]);
  const erro = porqueInvalida(novo);
  return erro ? { erro } : { cont: novo, d: [-x0, -y0] };
}

// ---------------------------------------------------------------- an attached block on a side
// the block on side `lado` around sc (along the side), W along it, D out: flush with the side's corner when close
// (ENCOSTAR); {s0, s1, rect} or null when the side is too short
export function blocoJunto(cont, lado, sc, W, D) {
  const l = lados(cont)[lado];
  if (!l || W > l.comprimento + 1e-6) return null;
  let s0 = sc - W / 2;
  if (s0 < ENCOSTAR) s0 = 0;
  if (l.comprimento - (s0 + W) < ENCOSTAR) s0 = l.comprimento - W;
  s0 = Math.round(Math.max(0, Math.min(s0, l.comprimento - W)) * 20) / 20;
  const s1 = s0 + W;
  const P = (s, d) => [l.p0[0] + l.u[0] * s + l.n[0] * d, l.p0[1] + l.u[1] * s + l.n[1] * d];
  const q = [P(s0, 0), P(s1, 0), P(s0, D), P(s1, D)];
  return { s0, s1, rect: { x0: Math.min(...q.map((p) => p[0])), x1: Math.max(...q.map((p) => p[0])), y0: Math.min(...q.map((p) => p[1])), y1: Math.max(...q.map((p) => p[1])) } };
}

// a point on side `lado` of the old outline, s along it, on the new outline (moved by d): {lado, s} or null (covered)
export function noNovo(contV, contN, d, lado, s) {
  const lv = lados(contV)[lado];
  if (!lv) return null;
  const P = [lv.p0[0] + lv.u[0] * s + d[0], lv.p0[1] + lv.u[1] * s + d[1]];
  for (const l of lados(contN)) {
    if (l.u[0] * lv.u[0] + l.u[1] * lv.u[1] < 0.999) continue;
    if (Math.abs((P[0] - l.p0[0]) * l.n[0] + (P[1] - l.p0[1]) * l.n[1]) > 1e-4) continue;
    const t = (P[0] - l.p0[0]) * l.u[0] + (P[1] - l.p0[1]) * l.u[1];
    if (t > -1e-4 && t < l.comprimento + 1e-4) return { lado: l.i, s: Math.round(t * 1000) / 1000 };
  }
  return null;
}

// an interior wall's end on an outside wall of the old outline, on the new one: the side on the same line, the same
// way out, across the wall's line c (moved by d) — null when that stretch is now inside (a block attached over it)
export function ladoNoNovo(contV, contN, d, lado, o, c, canto = false) {
  const lv = lados(contV)[lado];
  if (!lv) return null;
  // (an end at a corner: the wall's line just past the side's end — a wall flush with an inner corner, 0,095 off it)
  const ax = o === "h" ? 0 : 1, cr = 1 - ax, linha = lv.p0[ax] + d[ax], cc = c + d[cr], e = canto ? 0.2 : -1e-4;
  for (const l of lados(contN)) {
    if (Math.abs(l.u[ax]) > 0.5 || l.n[ax] * lv.n[ax] < 0.5 || Math.abs(l.p0[ax] - linha) > 1e-4) continue;
    const q0 = Math.min(l.p0[cr], l.p1[cr]), q1 = Math.max(l.p0[cr], l.p1[cr]);
    if (cc > q0 - e && cc < q1 + e) return l.i;
  }
  return null;
}

// the side across a wall of orientation o (its line c) standing at s along the wall — ends included (a block's corner)
export function ladoEm(cont, o, c, s) {
  const ax = o === "h" ? 0 : 1, cr = 1 - ax;
  for (const l of lados(cont)) {
    if (Math.abs(l.u[ax]) > 0.5 || Math.abs(l.p0[ax] - s) > 1e-4) continue;
    const q0 = Math.min(l.p0[cr], l.p1[cr]), q1 = Math.max(l.p0[cr], l.p1[cr]);
    if (c > q0 - 1e-4 && c < q1 + 1e-4) return l.i;
  }
  return null;
}

// the side through point P facing n (outwards): {lado, s} or null
export function ladoPor(cont, P, n) {
  for (const l of lados(cont)) {
    if (l.n[0] * n[0] + l.n[1] * n[1] < 0.999) continue;
    if (Math.abs((P[0] - l.p0[0]) * l.n[0] + (P[1] - l.p0[1]) * l.n[1]) > 1e-4) continue;
    const t = (P[0] - l.p0[0]) * l.u[0] + (P[1] - l.p0[1]) * l.u[1];
    if (t > -1e-4 && t < l.comprimento + 1e-4) return { lado: l.i, s: Math.round(t * 1000) / 1000 };
  }
  return null;
}

// a rectangle over the house (any of it inside, a 5 cm margin)
export function sobreACasa(cont, r) {
  for (let x = r.x0 + 0.05; x < r.x1 - 0.04; x += Math.max(0.05, (r.x1 - r.x0 - 0.1) / 12))
    for (let y = r.y0 + 0.05; y < r.y1 - 0.04; y += Math.max(0.05, (r.y1 - r.y0 - 0.1) / 12))
      if (dentroDaBase(cont, [x, y])) return true;
  return false;
}

// the plan rectangle of a pergola: along its side from s0 to s1, from the finished face (fora out of the base edge)
// out by its projection
export function retPergola(cont, pg, fora) {
  const l = lados(cont)[pg.lado];
  if (!l) return null;
  const P = (s, d) => [l.p0[0] + l.u[0] * s + l.n[0] * d, l.p0[1] + l.u[1] * s + l.n[1] * d];
  const q = [P(pg.s0, fora), P(pg.s1, fora), P(pg.s0, fora + pg.projecao), P(pg.s1, fora + pg.projecao)];
  return { x0: Math.min(...q.map((p) => p[0])), x1: Math.max(...q.map((p) => p[0])), y0: Math.min(...q.map((p) => p[1])), y1: Math.max(...q.map((p) => p[1])) };
}

// ---------------------------------------------------------------- a separate building: a configured house of its own
// at its place (x, y of its lower-left corner, turned rot × 90°), its gate / door on its front (side 0), its walls in
// the house's cladding, its roof the client's (format discovercasa-configurador/1, especificacao.md §8)
export function contornoSeparado(e) {
  return [[0, 0], [e.largura, 0], [e.largura, e.profundidade], [0, e.profundidade]];
}
export function casaSeparada(e, casa) {
  const cont = contornoSeparado(e), c = e.cobertura || { tipo: "escondida" };
  // the gate as the client set it (user 2026-10-30: "Colocar a porta da garagem ajustável"), else 3,00 x 2,20 where it fits
  const pg = e.portao || {};
  const porta = e.tipo === "garagem"
    ? { lado: 0, tipo: "portao", centro: e.largura / 2, largura: Math.min(pg.largura ?? 3.0, Math.round((e.largura - 0.65) * 20) / 20), altura: pg.altura ?? 2.2, estore: false }
    : { lado: 0, tipo: "porta", centro: e.largura / 2, largura: 1.0, altura: 2.2, estore: false };
  return {
    formato: "discovercasa-configurador/1", nome: `${TIPOS_EXT[e.tipo].nome} separada`, obra: "CFG",
    base: { forma: "retangular", contorno: cont },
    paredes_exteriores: paredesPossiveis(lados(cont)).map(({ lado, s0, s1 }) => ({ lado, s0, s1 })),
    vaos: [{ ...porta, divisao: TIPOS_EXT[e.tipo].nome }], paredes_interiores: [],
    cobertura: c.tipo === "escondida" ? { tipo: "escondida", ...(c.caleira ? { lado_caleira: c.caleira } : {}) }
      : { tipo: c.tipo, inclinacao_pct: c.inclinacao, beirado: c.beirado, painel: "sandwich" },
    acabamentos: casa.acabamentos, pe_direito: casa.pe_direito,
  };
}

// its footprint in the house's plan (the corners of its outline turned and moved)
export function pegadaSeparado(e) {
  const r = ((e.rot || 0) % 4 + 4) % 4, cs = [1, 0, -1, 0][r], sn = [0, 1, 0, -1][r];
  const pts = contornoSeparado(e).map(([x, y]) => [e.x + x * cs - y * sn, e.y + x * sn + y * cs]);
  return { x0: Math.min(...pts.map((p) => p[0])), x1: Math.max(...pts.map((p) => p[0])), y0: Math.min(...pts.map((p) => p[1])), y1: Math.max(...pts.map((p) => p[1])) };
}

// the distance from a rectangle to the house outline (0 when they touch or overlap)
export function distanciaACasa(cont, r) {
  const c = [(r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2];
  if (dentroDaBase(cont, c) || cont.some(([x, y]) => x > r.x0 && x < r.x1 && y > r.y0 && y < r.y1)) return 0;
  let d = Infinity;
  for (const l of lados(cont)) {
    for (let k = 0; k <= 20; k++) { // along the side, sampled (sides and rectangles are axis-aligned)
      const p = [l.p0[0] + (l.p1[0] - l.p0[0]) * k / 20, l.p0[1] + (l.p1[1] - l.p0[1]) * k / 20];
      const dx = Math.max(r.x0 - p[0], 0, p[0] - r.x1), dy = Math.max(r.y0 - p[1], 0, p[1] - r.y1);
      d = Math.min(d, Math.hypot(dx, dy));
    }
    const xs0 = Math.min(l.p0[0], l.p1[0]), xs1 = Math.max(l.p0[0], l.p1[0]), ys0 = Math.min(l.p0[1], l.p1[1]), ys1 = Math.max(l.p0[1], l.p1[1]);
    if (xs1 - xs0 < 1e-9 && ys0 < r.y1 && ys1 > r.y0) d = Math.min(d, Math.max(r.x0 - xs0, xs0 - r.x1, 0)); // a side along y facing it
    if (ys1 - ys0 < 1e-9 && xs0 < r.x1 && xs1 > r.x0) d = Math.min(d, Math.max(r.y0 - ys0, ys0 - r.y1, 0));
  }
  return d;
}

export const areaDe = (cont) => area(cont);
