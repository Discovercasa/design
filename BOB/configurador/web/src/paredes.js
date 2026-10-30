// The client's walls: 3 m each along every side of the base, the last one of a side the rest, never past the base
// (user 2026-10-20: "cada parede que o cliente escolha seja de 3 em 3 metros … a ultima parede … obrigatoriamente
// 2 metros, a parede não fica para além da base de fundação"). Building blocks for the client only — the engine
// divides the walls into the company's modules behind the screen.

export const COMPRIMENTO_PAREDE = 3.0;

// every wall the house can get, side by side: [{lado, s0, s1}] in the order they are placed (around the house)
export function paredesPossiveis(lados) {
  const out = [];
  for (const l of lados) {
    let s = 0;
    while (l.comprimento - s > 1e-6) {
      const s1 = Math.min(l.comprimento, s + COMPRIMENTO_PAREDE);
      out.push({ lado: l.i, s0: Math.round(s * 1000) / 1000, s1: Math.round(s1 * 1000) / 1000 });
      s = s1;
    }
  }
  return out;
}

// the next wall to place: on the chosen side if it has room, else the first free one going round
export function proximaParede(possiveis, colocadas, ladoEscolhido = null) {
  const livre = (p) => !colocadas.some((c) => c.lado === p.lado && Math.abs(c.s0 - p.s0) < 1e-6);
  if (ladoEscolhido !== null) {
    const p = possiveis.find((q) => q.lado === ladoEscolhido && livre(q));
    if (p) return p;
  }
  return possiveis.find(livre) || null;
}
