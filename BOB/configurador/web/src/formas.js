// House shapes from the m² — the same as ferramentas/configurador/formas.py (keep both equal; the Python one serves
// the scripts). UI geometry only: how the house is built always comes from the engine (the repo's Python).
// Outline counter-clockwise from the lower-left corner, metres, X east, Y north; right angles only.

export const FORMAS = { retangular: "Retangular", L: "Formato em L", T: "Formato em T", U: "Formato em U" };
const PASSO = 0.05; // sides rounded to 5 cm

const r = (v) => Math.round(Math.round(v / PASSO) * PASSO * 1000) / 1000;

export function area(cont) {
  let s = 0;
  for (let i = 0; i < cont.length; i++) {
    const [x0, y0] = cont[i], [x1, y1] = cont[(i + 1) % cont.length];
    s += x0 * y1 - x1 * y0;
  }
  return s / 2;
}

// p: comprimento (length / depth), and the cut-out of L / T / U as fractions
export function contorno(forma, areaM2, p = {}) {
  const unit = (a) => {
    const C = (p.comprimento ?? 1.6) * a;
    if (forma === "retangular") return [[0, 0], [C, 0], [C, a], [0, a]];
    if (forma === "L") {
      const rx = (p.recorte_x ?? 0.4) * C, ry = (p.recorte_y ?? 0.35) * a;
      return [[0, 0], [C - rx, 0], [C - rx, ry], [C, ry], [C, a], [0, a]];
    }
    if (forma === "T") {
      const hx = (p.haste_x ?? 0.4) * C, hy = (p.haste_y ?? 0.45) * a, x0 = (C - hx) / 2;
      return [[x0, 0], [x0 + hx, 0], [x0 + hx, hy], [C, hy], [C, a], [0, a], [0, hy], [x0, hy]];
    }
    if (forma === "U") {
      const px = (p.patio_x ?? 0.4) * C, py = (p.patio_y ?? 0.45) * a, x0 = (C - px) / 2;
      return [[0, 0], [C, 0], [C, a], [x0 + px, a], [x0 + px, a - py], [x0, a - py], [x0, a], [0, a]];
    }
    throw new Error(`forma desconhecida: ${forma}`);
  };
  const a = Math.sqrt(areaM2 / area(unit(1)));
  const pts = unit(a).map(([x, y]) => [r(x), r(y)]);
  const xmin = Math.min(...pts.map((q) => q[0]));
  return pts.map(([x, y]) => [Math.round((x - xmin) * 1000) / 1000, y]);
}

// the sides of an outline: {i, p0, p1, comprimento, u (direction), n (outward normal)}
export function lados(cont) {
  return cont.map((p0, i) => {
    const p1 = cont[(i + 1) % cont.length];
    const L = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);
    const u = [(p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L];
    return { i, p0, p1, comprimento: L, u, n: [u[1], -u[0]] }; // counter-clockwise: the outside is to the right
  });
}

// ---------------------------------------------------------------- editing the base (user 2026-10-21: "o cliente
// consiga mexer na dimensão de cada aresta e … introduzir manualmente o valor que quer em cada aresta")
export const LADO_MIN = 1.0;
const arred = (v) => Math.round(Math.round(v / PASSO) * PASSO * 1000) / 1000;

function normalizar(cont) {
  const xmin = Math.min(...cont.map((p) => p[0])), ymin = Math.min(...cont.map((p) => p[1]));
  return cont.map(([x, y]) => [arred(x - xmin), arred(y - ymin)]);
}

function cruzam(a0, a1, b0, b1) { // two axis-aligned segments cross or touch away from shared ends
  const [ax0, ax1] = [Math.min(a0[0], a1[0]), Math.max(a0[0], a1[0])], [ay0, ay1] = [Math.min(a0[1], a1[1]), Math.max(a0[1], a1[1])];
  const [bx0, bx1] = [Math.min(b0[0], b1[0]), Math.max(b0[0], b1[0])], [by0, by1] = [Math.min(b0[1], b1[1]), Math.max(b0[1], b1[1])];
  return ax0 <= bx1 + 1e-6 && bx0 <= ax1 + 1e-6 && ay0 <= by1 + 1e-6 && by0 <= ay1 + 1e-6;
}

// null when fine, else why not (every side at least LADO_MIN, the outline not crossing itself, still counter-clockwise)
export function porqueInvalida(cont) {
  const ls = lados(cont), n = ls.length;
  if (ls.some((l) => l.comprimento < LADO_MIN - 1e-6)) return `cada lado tem de ter pelo menos ${LADO_MIN.toFixed(2).replace(".", ",")} m`;
  for (let i = 0; i < n; i++) {
    for (let j = i + 2; j < n; j++) {
      if (i === 0 && j === n - 1) continue;
      if (cruzam(ls[i].p0, ls[i].p1, ls[j].p0, ls[j].p1)) return "a forma não pode cruzar-se";
    }
  }
  return area(cont) > 0 ? null : "a forma não pode cruzar-se";
}

// a side typed with a new length: the house grows (or shrinks) at that side's end — everything past it moves along it
export function mudarLado(cont, i, novo) {
  const l = lados(cont)[i], d = novo - l.comprimento;
  const novoC = cont.map(([x, y]) => {
    const alem = (x - l.p1[0]) * l.u[0] + (y - l.p1[1]) * l.u[1] >= -1e-6;
    return alem ? [x + d * l.u[0], y + d * l.u[1]] : [x, y];
  });
  return normalizar(novoC);
}

// a side dragged across (as IKEA Kreativ's walls): its two corners move out (+) or in (−); the sides next to it follow
export function moverLado(cont, i, d) {
  const l = lados(cont)[i], j = (i + 1) % cont.length;
  const novoC = cont.map((p, k) => (k === i || k === j ? [p[0] + d * l.n[0], p[1] + d * l.n[1]] : p));
  return normalizar(novoC);
}

// the whole base to a new area, the same proportions
export function escalar(cont, areaNova) {
  const f = Math.sqrt(areaNova / area(cont));
  return normalizar(cont.map(([x, y]) => [x * f, y * f]));
}
