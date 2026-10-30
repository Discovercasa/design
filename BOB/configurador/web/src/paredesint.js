// Interior walls as the client draws them (user 2026-10-21): dragged from the menu to a wall, the new wall starts on it
// (outside or interior wall) at right angles, and stretches as far as the client wants — the length shown as it goes,
// or typed — stopping at the first wall in its way (it joins it). The screen's geometry only: how each wall is built
// (interior modules, jambs, escadas where it meets another) is the engine's.
//
// A wall: {id, o: "h" (along X) | "v" (along Y), c (its line: y for "h", x for "v"), ini, fim, faces: {pos, neg},
// portas: [{id, s}]}; ini / fim = {tipo: "ext", lado, canto?} (the outline side it meets; canto: at the side's end — the
// wall into an attached garage / annex) | {tipo: "int", id} (another interior
// wall) | {tipo: "livre", s} (a free end at s along the axis); "pos" = the face towards +y ("h") or +x ("v"). A room may
// stand free in the middle of the house (user 2026-10-29: "imaginemos que ele quer fazer quatro paredes no meio da casa
// isso não é possível e quero que seja possível"): its first wall starts free and the last one closes on it.
import { lados } from "./formas.js";
import { CATALOGO, meia } from "./colocar.js";

export const COMPRIMENTO_MIN = 0.6;  // ours: a shorter piece of wall is no wall
export const JUNTAR = 0.35;          // a free end this close to a wall joins it (the converter snaps within 0,35 too)
const AFASTAR_EXT = 0.8, AFASTAR_INT = 0.7, JUNCAO = 0.15, PORTA = 0.87; // ours (spec §11); door rough opening 0,87
export const FACE_EXT = 0.16, FACE_INT = 0.065; // the finished inner face of an outside wall / half an interior wall
const E = 1e-6;
const m2 = (v) => v.toFixed(2).replace(".", ",");
export const arred = (v, p = 0.05) => Math.round(Math.round(v / p) * p * 1000) / 1000;

const eixo = (o) => (o === "h" ? 0 : 1); // the coordinate along the wall
export const pt = (o, c, s) => (o === "h" ? [s, c] : [c, s]);
export const naParede = (o, p) => (o === "h" ? { c: p[1], s: p[0] } : { c: p[0], s: p[1] });

export function dentroDaBase(cont, [x, y]) {
  let ins = false;
  for (let i = 0, j = cont.length - 1; i < cont.length; j = i++) {
    const [xi, yi] = cont[i], [xj, yj] = cont[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) ins = !ins;
  }
  return ins;
}

// the sides of the outline across a wall of orientation o at line c: [{lado, s (where it crosses)}]
function ladosAtravessados(cont, o, c) {
  const ax = eixo(o), cr = 1 - ax, out = [];
  for (const l of lados(cont)) {
    if (Math.abs(l.u[ax]) > 0.5) continue; // parallel
    const q0 = Math.min(l.p0[cr], l.p1[cr]), q1 = Math.max(l.p0[cr], l.p1[cr]);
    if (c > q0 + E && c < q1 - E) out.push({ lado: l.i, s: l.p0[ax] });
  }
  return out;
}

function coord(cont, porId, w, ref) {
  if (ref.tipo === "livre") return ref.s;
  if (ref.tipo === "int") { const q = porId.get(ref.id); return q ? q.c : NaN; }
  const l = lados(cont)[ref.lado];
  return l ? l.p0[eixo(w.o)] : NaN;
}

// every wall with its ends: {...w, a, b (a < b), fimA, fimB ("ext" | "int" | "livre"), refA, refB, de, ate, comp}
export function resolver(cont, lista) {
  const porId = new Map(lista.map((w) => [w.id, w]));
  return lista.map((w) => {
    const si = coord(cont, porId, w, w.ini), sf = coord(cont, porId, w, w.fim);
    const [a, refA, b, refB] = si <= sf ? [si, w.ini, sf, w.fim] : [sf, w.fim, si, w.ini];
    return { ...w, a, b, refA, refB, fimA: refA.tipo, fimB: refB.tipo, de: pt(w.o, w.c, a), ate: pt(w.o, w.c, b), comp: b - a };
  });
}

// why wall r (resolved, in rs) cannot stay so, or null
export function porqueNao(cont, vaos, rs, r, aceitar = null) {
  if (!Number.isFinite(r.a) || !Number.isFinite(r.b)) return "a parede perdeu a parede onde se apoiava";
  if (r.comp < COMPRIMENTO_MIN - E) return `a parede tem de ter pelo menos ${m2(COMPRIMENTO_MIN)} m`;
  // (aceitar: the first wall of a room being drawn in the middle of the house — the next one starts on its end)
  if (r.fimA === "livre" && r.fimB === "livre" && r.id !== aceitar) return "a parede tem de encostar a outra parede";
  if (!dentroDaBase(cont, pt(r.o, r.c, (r.a + r.b) / 2))) return "a parede tem de ficar dentro da casa";
  const porId = new Map(rs.map((q) => [q.id, q]));
  for (const ref of [r.refA, r.refB]) { // each end still on the wall it meets
    // (an end at a block's corner — the wall into an attached garage / annex, step 7 — stands on that side's end)
    if (ref.tipo === "ext" && !ref.canto && !ladosAtravessados(cont, r.o, r.c).some((x) => x.lado === ref.lado)) return "a parede saiu da parede exterior onde encostava";
    if (ref.tipo === "int") {
      const q = porId.get(ref.id);
      if (!q || q.o === r.o || r.c < q.a - 0.01 || r.c > q.b + 0.01) return "a parede saiu da parede interior onde encostava";
    }
  }
  for (const x of ladosAtravessados(cont, r.o, r.c)) if (x.s > r.a + 0.01 && x.s < r.b - 0.01) return "a parede não pode atravessar uma parede exterior";
  for (const q of rs) {
    if (q.id === r.id || q.o === r.o) continue;
    if (q.c > r.a + 0.01 && q.c < r.b - 0.01 && r.c > q.a + 0.01 && r.c < q.b - 0.01) return "as paredes não se podem cruzar";
  }
  const ax = eixo(r.o), cr = 1 - ax;
  for (const l of lados(cont)) { // room to use between it and a parallel wall
    if (Math.abs(l.u[ax]) < 0.5) continue;
    const s0 = Math.min(l.p0[ax], l.p1[ax]), s1 = Math.max(l.p0[ax], l.p1[ax]);
    if (Math.min(s1, r.b) - Math.max(s0, r.a) > 0.05 && Math.abs(l.p0[cr] - r.c) < AFASTAR_EXT) return `fica a menos de ${m2(AFASTAR_EXT)} m de uma parede exterior`;
  }
  for (const q of rs) {
    if (q.id === r.id || q.o !== r.o) continue;
    if (Math.min(q.b, r.b) - Math.max(q.a, r.a) > 0.05 && Math.abs(q.c - r.c) < AFASTAR_INT) return `fica a menos de ${m2(AFASTAR_INT)} m de outra parede interior`;
  }
  for (const ref of [r.refA, r.refB]) { // an end on an outside wall misses its openings
    if (ref.tipo !== "ext") continue;
    const l = lados(cont)[ref.lado];
    const p = pt(r.o, r.c, ref === r.refA ? r.a : r.b), t = (p[0] - l.p0[0]) * l.u[0] + (p[1] - l.p0[1]) * l.u[1];
    for (const v of vaos) if (v.lado === ref.lado && Math.abs(t - v.centro) < meia(v) + JUNCAO)
      return `encontra a parede exterior onde está um vão (${CATALOGO[v.tipo].nome.toLowerCase()})`;
  }
  for (const p of r.portas) if (centroPorta(rs, r, p, p.s) === null || Math.abs(centroPorta(rs, r, p, p.s) - p.s) > 1e-3) return "uma porta deixava de caber";
  return null;
}

export function porqueNaoTodas(cont, vaos, lista, aceitar = null) {
  const rs = resolver(cont, lista);
  for (const r of rs) { const e = porqueNao(cont, vaos, rs, r, aceitar); if (e) return e; }
  return null;
}

// the wall a new one starts on: the nearest outside wall's inner face or interior wall face (within 'raio'), the
// point's projection on it: {ref, o (the wall met), c (its line), s (along it), dentro (+1/-1: the side the new wall
// goes to), dist} — dropped anywhere in a room, the new wall runs from the nearest wall to that point
export function paredePerto(cont, rs, p, raio = Infinity) {
  if (!dentroDaBase(cont, p)) return null;
  let melhor = null;
  for (const l of lados(cont)) {
    const t = (p[0] - l.p0[0]) * l.u[0] + (p[1] - l.p0[1]) * l.u[1];
    const d = (p[0] - l.p0[0]) * -l.n[0] + (p[1] - l.p0[1]) * -l.n[1]; // inwards
    if (t < 0.45 || t > l.comprimento - 0.45 || d < -0.2 || d > raio) continue;
    if (!melhor || d < melhor.dist) {
      const o = Math.abs(l.u[0]) > 0.5 ? "h" : "v";
      melhor = { ref: { tipo: "ext", lado: l.i }, o, c: l.p0[o === "h" ? 1 : 0], s: o === "h" ? p[0] : p[1], dentro: o === "h" ? -l.n[1] : -l.n[0], dist: d };
    }
  }
  for (const q of rs) {
    const { c, s } = naParede(q.o, p), d = Math.abs(c - q.c);
    if (s < q.a + 0.45 || s > q.b - 0.45 || d > raio) continue;
    if (!melhor || d < melhor.dist) melhor = { ref: { tipo: "int", id: q.id }, o: q.o, c: q.c, s, dentro: c >= q.c ? 1 : -1, dist: d };
  }
  return melhor;
}

// a new wall started on the wall 'perto' (from paredePerto), its free end towards p (at least 1 m in when dropped
// right on the wall)
export function novaParede(cont, rs, perto, p, id) {
  const o = perto.o === "h" ? "v" : "h", c = arred(perto.s);
  const alvo = naParede(o, p).s;
  const s0 = perto.c, longe = Math.max(1.0, Math.abs(alvo - s0));
  const w = { id, o, c, ini: perto.ref, fim: { tipo: "livre", s: s0 + perto.dentro * longe }, faces: { pos: "pladur", neg: "pladur" }, portas: [] };
  return esticar(cont, rs, w, s0 + perto.dentro * longe);
}

// the wall with its free end moved to 'alvo' (along its axis): whole 5 cm of length, at least the minimum, stopped by
// the first wall in its way (joined to it when it reaches it or comes within JUNTAR)
export function esticar(cont, rs, w, alvo) {
  const fixo = w.fim.tipo === "livre" ? "ini" : w.ini.tipo === "livre" ? "fim" : null;
  if (!fixo) return w; // wall to wall: no free end
  const solto = fixo === "ini" ? "fim" : "ini";
  const porId = new Map(rs.map((q) => [q.id, q]));
  const s0 = coord(cont, porId, w, w[fixo]);
  const dir = alvo >= s0 ? 1 : -1;
  let comp = Math.max(COMPRIMENTO_MIN, arred(Math.abs(alvo - s0)));
  // what stands in the way, nearest first: outside walls crossing the line, interior walls crossing it
  const obst = [];
  for (const x of ladosAtravessados(cont, w.o, w.c)) obst.push({ s: x.s, ref: { tipo: "ext", lado: x.lado } });
  for (const q of rs) if (q.id !== w.id && q.o !== w.o && w.c > q.a - 0.01 && w.c < q.b + 0.01) obst.push({ s: q.c, ref: { tipo: "int", id: q.id } });
  let prox = null;
  for (const ob of obst) {
    const d = (ob.s - s0) * dir;
    if (d > 0.05 && (!prox || d < prox.d)) prox = { ...ob, d };
  }
  const novo = { ...w };
  if (prox && comp >= prox.d - JUNTAR) novo[solto] = prox.ref;
  else novo[solto] = { tipo: "livre", s: Math.round((s0 + dir * comp) * 1000) / 1000 };
  return novo;
}

// ---------------------------------------------------------------- drawing walls by clicks (user 2026-10-22: "posso
// simplesmente clicar nela e no sítio que depois que quiser fazer uma parede … dar snap também para as extremidades das
// paredes facilitando a forma de fazer divisões"; "o fim de uma das paredes pelo menos deve fazer 90º perfeitamente")
export const ENCAIXE = 0.45;   // a click this close to a wall's free end starts from it: a corner
const ALINHAR = 0.2;           // a line or an end this close to another wall's line or end takes it (rooms that square)

// the nearest value of 'alvos' within 'raio' of v, else v
function encaixar(v, alvos, raio = ALINHAR) {
  let m = null;
  for (const a of alvos) if (Math.abs(a - v) <= raio && (m === null || Math.abs(a - v) < Math.abs(m - v))) m = a;
  return m === null ? v : m;
}

// lines a new wall of orientation o may take (5 cm, else another wall's line or end in line with it)
function linhasDe(cont, rs, o) {
  const out = [];
  for (const q of rs) {
    if (q.o === o) out.push(q.c);
    else out.push(q.a, q.b);
  }
  for (const k of cantosInteriores(cont)) for (const x of k.opcoes) if (x.o === o) out.push(x.c); // flush with an inner corner
  return out;
}

// the house's inner corners (an L, T or U — user 2026-10-29: "Não me está a deixar iniciar paredes interiores nos cantos
// da casa e isso deve ser possível por exemplo numa estrutura em L ou em U ou em T"): a wall goes on from the corner in
// line with one of its two outside walls, one face flush with that wall's finished inner face (ours); the start on the
// other outside wall, at its end (canto). [{ponto (the finished corner), opcoes: [{ref, o, c, s0, dentro}]}]
const RENTE = FACE_EXT - FACE_INT; // a wall flush with an outside wall's inner face: its line this far in from the outline
export function cantosInteriores(cont) {
  const ls = lados(cont), out = [];
  for (let i = 0; i < ls.length; i++) {
    const a = ls[(i - 1 + ls.length) % ls.length], b = ls[i]; // a ends where b starts
    if (b.u[0] * a.n[0] + b.u[1] * a.n[1] < 0.5) continue; // b turns inwards: an outer corner
    const P = b.p0, opcoes = [];
    for (const [l, outro] of [[a, b], [b, a]]) {
      const o = Math.abs(l.u[0]) > 0.5 ? "h" : "v", cr = o === "h" ? 1 : 0;
      opcoes.push({ ref: { tipo: "ext", lado: outro.i, canto: true }, o, c: Math.round((P[cr] - l.n[cr] * RENTE) * 1000) / 1000,
        s0: P[1 - cr], dentro: -outro.n[1 - cr] });
    }
    out.push({ ponto: [P[0] - (a.n[0] + b.n[0]) * FACE_EXT, P[1] - (a.n[1] + b.n[1]) * FACE_EXT], opcoes });
  }
  return out;
}

// where a wall drawn from point p starts: a free end of an interior wall (the new one turns 90° there — a corner), else
// the nearest wall face (outside or interior) within 'raio': {ref (the wall it starts on), o (the NEW wall's
// orientation), c (its line), s0 (its start along its axis), dentro (+1 / -1 into the room; 0 = either way, a corner),
// ponta ({id, fim} of the wall whose free end it turns at, or null), ponto ([x, y] the start)}
export function inicio(cont, rs, p, raio = 0.6) {
  if (!p) return null;
  let melhor = null;
  for (const q of rs) {
    for (const [fim, s, ref] of [["a", q.a, q.refA], ["b", q.b, q.refB]]) {
      if (!ref || ref.tipo !== "livre") continue;
      const e = pt(q.o, q.c, s), d = Math.hypot(p[0] - e[0], p[1] - e[1]);
      if (d < ENCAIXE && (!melhor || d < melhor.d)) {
        const o = q.o === "h" ? "v" : "h";
        melhor = { d, ref: { tipo: "int", id: q.id }, o, c: s, s0: q.c, dentro: 0, ponta: { id: q.id, fim }, ponto: e };
      }
    }
  }
  // else a corner or a T of interior walls (user 2026-10-28: "não me deixa dar snap num dos cantos que fica na área
  // interior para fazer outra divisão logo ao lado dessa"): the new wall goes on in line with one of them, past the
  // other — which one, the way the pointer then goes (sentido); {..., opcoes: [the starts it may take]}
  const porId = new Map(rs.map((q) => [q.id, q]));
  const emLinha = (x, s) => rs.some((y) => y.id !== x.id && y.o === x.o && Math.abs(y.c - x.c) < 0.02 && (Math.abs(y.a - s) < 0.02 || Math.abs(y.b - s) < 0.02));
  for (const q of melhor ? [] : rs) {
    for (const [s, ref, para] of [[q.a, q.refA, -1], [q.b, q.refB, 1]]) {
      const w = ref && ref.tipo === "int" ? porId.get(ref.id) : null;
      if (!w || w.o === q.o) continue;
      const e = pt(q.o, q.c, s), d = Math.hypot(p[0] - e[0], p[1] - e[1]);
      if (d >= ENCAIXE || (melhor && d >= melhor.d)) continue;
      const opcoes = [];
      if (!emLinha(q, s)) opcoes.push({ ref: { tipo: "int", id: w.id }, o: q.o, c: q.c, s0: w.c, dentro: para }); // q's line, past w
      const fimW = Math.abs(w.a - q.c) < 0.02 ? -1 : Math.abs(w.b - q.c) < 0.02 ? 1 : 0;
      if (fimW && !emLinha(w, q.c)) opcoes.push({ ref: { tipo: "int", id: q.id }, o: w.o, c: w.c, s0: q.c, dentro: fimW }); // w's line, past q
      if (opcoes.length) melhor = { d, ...opcoes[0], ponta: null, ponto: e, opcoes: opcoes.map((x) => ({ d, ...x, ponta: null, ponto: e })) };
    }
  }
  for (const k of melhor ? [] : cantosInteriores(cont)) { // an inner corner of the house
    const d = Math.hypot(p[0] - k.ponto[0], p[1] - k.ponto[1]);
    if (d >= ENCAIXE || (melhor && d >= melhor.d)) continue;
    const opcoes = k.opcoes.map((x) => ({ d, ...x, ponta: null, ponto: k.ponto }));
    melhor = { ...opcoes[0], opcoes };
  }
  if (melhor) return melhor;
  const perto = paredePerto(cont, rs, p, raio);
  if (!perto) { // away from every wall: a free start (a room in the middle of the house), in line with the walls near
    if (!dentroDaBase(cont, p)) return null;
    const x = encaixar(arred(p[0]), linhasDe(cont, rs, "v")), y = encaixar(arred(p[1]), linhasDe(cont, rs, "h"));
    const opcoes = [{ ref: { tipo: "livre", s: x }, o: "h", c: y, s0: x }, { ref: { tipo: "livre", s: y }, o: "v", c: x, s0: y }]
      .map((q) => ({ d: Infinity, ...q, dentro: 0, ponta: null, ponto: [x, y], livre: true }));
    return { ...opcoes[0], opcoes };
  }
  const o = perto.o === "h" ? "v" : "h";
  const c = encaixar(arred(perto.s), linhasDe(cont, rs, o));
  return { d: perto.dist, ref: perto.ref, o, c, s0: perto.c, dentro: perto.dentro, ponta: null, ponto: pt(o, c, perto.c) };
}

// a start at a corner (inicio's opcoes) goes on along the wall the pointer moves along
export function sentido(ini, p) {
  if (!ini || !ini.opcoes || !p) return ini;
  const o = Math.abs(p[0] - ini.ponto[0]) >= Math.abs(p[1] - ini.ponto[1]) ? "h" : "v";
  return ini.opcoes.find((x) => x.o === o) || ini.opcoes[0];
}

// how far a wall on line c, starting on the wall 'ref', stands from that wall's ends (user 2026-10-28: "deve dizer a
// distância de cada canto de forma a por exemplo a pessoa quer começar uma divisória precisamente a 4 metros desse
// canto"): as the base's sides and the walls' lengths are measured — from the corner of the base (or the other
// interior wall's centre line) to the new wall's centre line, so the 5 cm steps give round numbers (ours, to confirm);
// [{de, ate (plan points along that wall), valor, n (the side to show them: into the house / the room), canto (that
// end), ponto (where the wall stands)}]
export function aosCantos(cont, rs, ref, c, dentro = 1) {
  let A, B, X, n;
  if (ref && ref.tipo === "ext") {
    const l = lados(cont)[ref.lado];
    if (!l) return [];
    const ax = Math.abs(l.u[0]) > 0.5 ? 0 : 1, t = (c - l.p0[ax]) * l.u[ax];
    [A, B, X, n] = [l.p0, l.p1, [l.p0[0] + l.u[0] * t, l.p0[1] + l.u[1] * t], [-l.n[0], -l.n[1]]];
  } else if (ref && ref.tipo === "int") {
    const q = rs.find((x) => x.id === ref.id);
    if (!q || !Number.isFinite(q.a) || !Number.isFinite(q.b)) return [];
    [A, B, X] = [pt(q.o, q.c, q.a), pt(q.o, q.c, q.b), pt(q.o, q.c, c)];
    n = q.o === "h" ? [0, dentro || 1] : [dentro || 1, 0];
  } else return [];
  const out = [];
  for (const [de, ate, canto] of [[A, X, A], [X, B, B]]) {
    const valor = Math.hypot(ate[0] - de[0], ate[1] - de[1]);
    if (valor > 0.04) out.push({ de, ate, valor: Math.round(valor * 1000) / 1000, n, canto, ponto: X });
  }
  return out;
}

// the wall drawn from 'ini' towards p: along ini.o, its far end at p (5 cm; another wall's line or end in line within
// 0,2), stopped by the first wall in its way and joined to it; {w (the new wall), junta (the far end met a wall), fecha
// (the far end in line with 'origem', the first point of the walls being drawn: the next wall closes the room — user
// 2026-10-29: "deve haver um snap que alinha a ultima parede com o canto da primeira parede criada, não um snap
// obrigatório mas apenas como sugestão")}
export const FECHAR = 0.4;
export function segmento(cont, rs, ini, p, id, origem = null) {
  const s = naParede(ini.o, p).s;
  const dir = ini.dentro || (s >= ini.s0 ? 1 : -1);
  let alvo = ini.s0 + dir * Math.max(COMPRIMENTO_MIN, Math.abs(s - ini.s0));
  const pref = origem ? naParede(ini.o, origem).s : null;
  const fecha = pref !== null && Math.abs(alvo - pref) <= FECHAR && (pref - ini.s0) * dir >= COMPRIMENTO_MIN - E;
  alvo = fecha ? pref : encaixar(alvo, linhasDe(cont, rs, ini.o === "h" ? "v" : "h").filter((v) => (v - ini.s0) * dir >= COMPRIMENTO_MIN - E));
  const w = { id, o: ini.o, c: ini.c, ini: ini.ref, fim: { tipo: "livre", s: Math.round(alvo * 1000) / 1000 },
    faces: { pos: "pladur", neg: "pladur" }, portas: [] };
  let novo = esticar(cont, rs, w, alvo);
  if (novo.fim.tipo === "livre") { // a click short of a wall (its finished face is up to 0,16 in): it reaches it
    const mais = esticar(cont, rs, w, alvo + dir * 0.25);
    if (mais.fim.tipo !== "livre") novo = mais;
  }
  return { w: novo, junta: novo.fim.tipo !== "livre", fecha };
}

// the list with a new wall from 'ini': the wall whose free end it turns at now ends on it (the corner)
export function comNova(lista, ini, w) {
  const out = lista.map((q) => {
    // the new wall ends on q's free end (the last wall of a room closing on the first): that end turns the corner too
    if (w.fim.tipo === "int" && w.fim.id === q.id) for (const k of ["ini", "fim"]) if (q[k].tipo === "livre" && Math.abs(q[k].s - w.c) < 0.02) return { ...q, [k]: { tipo: "int", id: w.id } };
    if (!ini.ponta || q.id !== ini.ponta.id) return q;
    // its free end (a wall touches another at one end at least; with two free ends, the one at the corner point)
    const fimLivre = q.fim.tipo === "livre" && (q.ini.tipo !== "livre" || Math.abs(q.fim.s - ini.c) <= Math.abs(q.ini.s - ini.c)) ? "fim" : "ini";
    return { ...q, [fimLivre]: { tipo: "int", id: w.id } };
  });
  return [...out, w];
}

// the free end of wall w, to go on drawing from it (a chain of walls), or null when both ends meet walls (both free —
// a room's first wall in the middle of the house: the end drawn last, its 'fim')
export function pontaLivre(cont, lista, id) {
  const r = resolver(cont, lista).find((x) => x.id === id);
  if (!r) return null;
  const fim = r.fimA === "livre" && r.fimB === "livre" ? (r.refB === r.fim ? "b" : "a") : r.fimB === "livre" ? "b" : r.fimA === "livre" ? "a" : null;
  if (!fim) return null;
  const s = fim === "b" ? r.b : r.a;
  return { ref: { tipo: "int", id }, o: r.o === "h" ? "v" : "h", c: s, s0: r.c, dentro: 0, ponta: { id, fim }, ponto: pt(r.o, r.c, s) };
}

// ---------------------------------------------------------------- rooms: the floor between the walls
// (user 2026-10-22: "quando crio duas paredes que fecham uma divisão quero que diga os metros quadrados dessa divisão
// no chão da mesma e a pessoa pode aplicar pavimento que desejar na divisão que desejar")
// the floor cut by the walls' finished faces into rectangles (the outline's sides and the walls' faces as grid lines),
// joined where no wall stands between: [{area (m², to the finished faces), celulas: [[x0, x1, y0, y1]], rotulo: [x, y]}]
export function divisoes(cont, rs) {
  const solidos = [];
  for (const l of lados(cont)) { // a band along each side, the finished inner face of the outside wall
    const x0 = Math.min(l.p0[0], l.p1[0]), x1 = Math.max(l.p0[0], l.p1[0]);
    const y0 = Math.min(l.p0[1], l.p1[1]), y1 = Math.max(l.p0[1], l.p1[1]);
    const nx = -l.n[0], ny = -l.n[1]; // inwards
    solidos.push([Math.min(x0, x1 + nx * FACE_EXT) - FACE_EXT * Math.abs(l.u[0]), Math.max(x1, x0 + nx * FACE_EXT) + FACE_EXT * Math.abs(l.u[0]),
      Math.min(y0, y1 + ny * FACE_EXT) - FACE_EXT * Math.abs(l.u[1]), Math.max(y1, y0 + ny * FACE_EXT) + FACE_EXT * Math.abs(l.u[1])]);
  }
  for (const r of rs) {
    if (!Number.isFinite(r.a) || !Number.isFinite(r.b)) continue;
    const [p0, p1] = [pt(r.o, r.c - FACE_INT, r.a), pt(r.o, r.c + FACE_INT, r.b)];
    solidos.push([Math.min(p0[0], p1[0]), Math.max(p0[0], p1[0]), Math.min(p0[1], p1[1]), Math.max(p0[1], p1[1])]);
  }
  const xs = [...new Set([...cont.map((p) => p[0]), ...solidos.flatMap((s) => [s[0], s[1]])].map((v) => Math.round(v * 1e4) / 1e4))].sort((a, b) => a - b);
  const ys = [...new Set([...cont.map((p) => p[1]), ...solidos.flatMap((s) => [s[2], s[3]])].map((v) => Math.round(v * 1e4) / 1e4))].sort((a, b) => a - b);
  const nx = xs.length - 1, ny = ys.length - 1;
  const livre = [];
  for (let i = 0; i < nx; i++) {
    livre.push([]);
    for (let j = 0; j < ny; j++) {
      const cx = (xs[i] + xs[i + 1]) / 2, cy = (ys[j] + ys[j + 1]) / 2;
      livre[i].push(xs[i + 1] - xs[i] > 1e-4 && ys[j + 1] - ys[j] > 1e-4 && dentroDaBase(cont, [cx, cy])
        && !solidos.some((s) => cx > s[0] && cx < s[1] && cy > s[2] && cy < s[3]));
    }
  }
  const visto = livre.map((c) => c.map(() => false)), out = [];
  for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
    if (!livre[i][j] || visto[i][j]) continue;
    const celulas = [], pilha = [[i, j]];
    visto[i][j] = true;
    let a = 0, maior = null;
    while (pilha.length) {
      const [p, q] = pilha.pop();
      const c = [xs[p], xs[p + 1], ys[q], ys[q + 1]], ac = (c[1] - c[0]) * (c[3] - c[2]);
      celulas.push(c);
      a += ac;
      if (!maior || ac > maior[1]) maior = [c, ac];
      for (const [dp, dq] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const p2 = p + dp, q2 = q + dq;
        if (p2 >= 0 && p2 < nx && q2 >= 0 && q2 < ny && livre[p2][q2] && !visto[p2][q2]) { visto[p2][q2] = true; pilha.push([p2, q2]); }
      }
    }
    if (a < 0.5) continue; // a sliver between two walls, no room
    const c = maior[0];
    out.push({ area: a, celulas, rotulo: [(c[0] + c[1]) / 2, (c[2] + c[3]) / 2] });
  }
  return out;
}

// the room (of divisoes) holding point p, or null
export const divisaoEm = (ds, p) => (p ? ds.find((d) => d.celulas.some((c) => p[0] >= c[0] - 1e-6 && p[0] <= c[1] + 1e-6 && p[1] >= c[2] - 1e-6 && p[1] <= c[3] + 1e-6)) || null : null);

// a door centre on wall r at (or nearest to) s: clear of the ends, the other doors and the walls that meet it
export function centroPorta(rs, r, porta, s) {
  const h = PORTA / 2, bl = [];
  for (const p of r.portas) if (p.id !== porta.id) bl.push([p.s - 2 * h - 0.08, p.s + 2 * h + 0.08]);
  for (const q of rs) {
    if (q.id === r.id || q.o === r.o) continue;
    for (const e of [q.a, q.b]) {
      const pq = pt(q.o, q.c, e), across = r.o === "h" ? pq[1] : pq[0], along = r.o === "h" ? pq[0] : pq[1];
      if (Math.abs(across - r.c) < 0.02 && along > r.a - 0.01 && along < r.b + 0.01) bl.push([along - h - JUNCAO, along + h + JUNCAO]);
    }
  }
  const fim = (k) => (k === "ext" ? 0.46 : 0.3);
  const lo = r.a + fim(r.fimA) + h, hi = r.b - fim(r.fimB) - h;
  if (lo > hi + E) return null;
  const livre = (x) => x >= lo - E && x <= hi + E && !bl.some(([a, b]) => x > a + E && x < b - E);
  const cand = [arred(Math.min(Math.max(s, lo), hi)), lo, hi, ...bl.flat()];
  let melhor = null;
  for (const x of cand) if (livre(x) && (melhor === null || Math.abs(x - s) < Math.abs(melhor - s))) melhor = x;
  return melhor === null ? null : Math.round(melhor * 1000) / 1000;
}

// removing a wall: the walls that met it keep their place with a free end; one left touching nothing goes too
export function remover(lista, id) {
  let resto = lista.filter((w) => w.id !== id), fora = [id];
  for (;;) {
    const soltar = (w) => {
      const f = (ref, s) => (ref.tipo === "int" && fora.includes(ref.id) ? { tipo: "livre", s } : ref);
      const porId = new Map(lista.map((q) => [q.id, q]));
      const cIni = w.ini.tipo === "int" && porId.get(w.ini.id) ? porId.get(w.ini.id).c : w.ini.s;
      const cFim = w.fim.tipo === "int" && porId.get(w.fim.id) ? porId.get(w.fim.id).c : w.fim.s;
      return { ...w, ini: f(w.ini, cIni), fim: f(w.fim, cFim) };
    };
    resto = resto.map(soltar);
    const sozinhas = resto.filter((w) => w.ini.tipo === "livre" && w.fim.tipo === "livre").map((w) => w.id);
    if (!sozinhas.length) return { lista: resto, removidas: fora.length - 1 };
    fora = [...fora, ...sozinhas];
    resto = resto.filter((w) => !sozinhas.includes(w.id));
  }
}

// ---------------------------------------------------------------- the pieces of a wall between the walls that meet it
// (user 2026-10-29: "quando o cliente faz uma parede demasiado comprida … deve ser possível selecionar apenas esse
// "pedaço" de parede interior"): [[s0, s1]] along wall r (resolved), one piece when nothing meets it on the way
export function trocos(rs, r) {
  const js = [];
  for (const q of rs) {
    if (q.id === r.id || q.o === r.o || !(q.c > r.a + 0.02 && q.c < r.b - 0.02)) continue;
    if (Math.abs(q.a - r.c) < 0.02 || Math.abs(q.b - r.c) < 0.02) js.push(q.c);
  }
  const s = [r.a, ...[...new Set(js.map((v) => Math.round(v * 1000) / 1000))].sort((x, y) => x - y), r.b];
  return s.slice(1).map((v, i) => [s[i], v]);
}
export const trocoEm = (rs, r, s) => trocos(rs, r).find(([a, b]) => s >= a - 1e-6 && s <= b + 1e-6) || [r.a, r.b];

// the list without the piece [s0, s1] of wall id: an end piece shortens the wall to the wall met there (a corner), a
// middle piece splits it in two (the far part a new wall, novoId); the walls that met the piece taken away get a free
// end (one left touching nothing goes too), the doors on it go. {lista, removidas} or {erro}
export function removerTroco(cont, lista, id, [s0, s1], novoId) {
  const rs = resolver(cont, lista), r = rs.find((x) => x.id === id);
  if (!r) return { erro: "a parede já não existe" };
  if (s0 <= r.a + 1e-3 && s1 >= r.b - 1e-3) return remover(lista, id);
  const w = lista.find((x) => x.id === id);
  const kA = r.refA === w.ini ? "ini" : "fim", kB = kA === "ini" ? "fim" : "ini"; // w's ends at a and at b
  const naJuncao = (s) => rs.find((q) => q.id !== id && q.o !== r.o && Math.abs(q.c - s) < 0.002
    && (Math.abs(q.a - r.c) < 0.02 || Math.abs(q.b - r.c) < 0.02));
  const ref = (s) => { const q = naJuncao(s); return q ? { tipo: "int", id: q.id } : { tipo: "livre", s }; };
  let partes; // [[the new wall, its range]]
  if (s0 <= r.a + 1e-3) partes = [[{ ...w, [kA]: ref(s1) }, [s1, r.b]]];
  else if (s1 >= r.b - 1e-3) partes = [[{ ...w, [kB]: ref(s0) }, [r.a, s0]]];
  else partes = [[{ ...w, [kB]: ref(s0) }, [r.a, s0]], [{ ...w, id: novoId, ini: ref(s1), fim: w[kB], faces: { ...w.faces } }, [s1, r.b]]];
  partes = partes.map(([p, [a, b]]) => [{ ...p, portas: w.portas.filter((d) => d.s > a && d.s < b).map((d) => ({ ...d })) }, [a, b]]);
  const dono = (q) => { // the part a wall meeting w now meets (by where it stands along w), or null: it met the piece taken
    const v = q.c;
    const k = partes.find(([, [a, b]]) => v >= a - 0.01 && v <= b + 0.01);
    return k ? k[0].id : null;
  };
  const porId = new Map(rs.map((q) => [q.id, q]));
  let resto = lista.filter((q) => q.id !== id).map((q) => {
    let n = q;
    for (const k of ["ini", "fim"]) {
      if (q[k].tipo !== "int" || q[k].id !== id) continue;
      const d = dono(porId.get(q.id));
      const rq = porId.get(q.id), s = q[k] === rq.refA ? rq.a : rq.b;
      n = { ...n, [k]: d === null ? { tipo: "livre", s } : { tipo: "int", id: d } };
    }
    return n;
  });
  resto = [...resto, ...partes.map(([p]) => p)];
  let removidas = 0; // a wall left touching nothing goes too (as remover)
  for (;;) {
    const sozinha = resto.find((q) => q.ini.tipo === "livre" && q.fim.tipo === "livre");
    if (!sozinha) break;
    const out = remover(resto, sozinha.id);
    resto = out.lista;
    removidas += 1 + out.removidas;
  }
  return { lista: resto, removidas };
}
