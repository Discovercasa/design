// Placeholder prices for the prototype — NOT DiscoverCasa prices. The real ones will come from the materials, labour,
// foundation, caixilharia, especialidades, installations, licensing and IVA (user 2026-10-20; Product vision 2), as
// unit prices × the engine's quantities. Until then these round numbers only show the running total working.
import { CATALOGO } from "./colocar.js";
import { MATERIAIS } from "./materiais.js";

export const PRECOS_EXEMPLO = {
  aviso: "Preços de exemplo do protótipo — não são preços DiscoverCasa",
  base_por_m2: 120,
  parede_exterior_por_m2: 215,           // the wall face (length × height to the parapet / eaves)
  exterior_extra_por_m2: { A: 0, B: 15, C: 30 },
  vao_por_m2: 450,                       // the frame (L × A)
  vao_un: { porta: 1800, portao: 3200 },  // per door / gate instead
  estore_un: 350,
  parede_interior_por_m2: 95,            // length × clear height
  face_extra_por_m2: { pladur: 0, madeira: 40, ceramico: 30 },
  porta_interior_un: 450,
  pavimento_por_m2: { vinilico: 35, ceramico_pav: 45 },
  cobertura_por_m2: { escondida: 95, duas_aguas: 85, misto: 92 }, // per m² of base (exposed: × 1 / cos of the slope)
  teto_por_m2: 32,                       // the false ceiling, with every roof (user 2026-10-22: "Quando se aplica a
                                         // cobertura automaticamente o teto falso já entra também")
};

const eur = new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
export const euros = (v) => eur.format(v);
const n2 = (v) => v.toFixed(2).replace(".", ",");

// [{rotulo, valor}] and the total: the base first, then each element (user: "vai acumulando ou descendo")
// casa: {area, altura (exterior walls), pe, paredes, vaos, interiores (resolved), acabamentos, cobertura, divisoes
// ([{area, material}] the rooms' floors), facesExt ([{area, material}] outside walls' inner faces)}
export function orcamento(casa, P = PRECOS_EXEMPLO) {
  const linhas = [];
  const { area, altura, pe, paredes = [], vaos = [], interiores = [], acabamentos = {}, cobertura = null, divisoes = [], facesExt = [] } = casa;
  if (area > 0) linhas.push({ rotulo: `Base de fundação (${area.toFixed(1).replace(".", ",")} m²)`, valor: area * P.base_por_m2 });
  const m = paredes.reduce((s, p) => s + (p.s1 - p.s0), 0);
  if (paredes.length) {
    linhas.push({ rotulo: `Paredes exteriores (${paredes.length}, ${n2(m)} m, ${n2(altura)} m de altura)`, valor: m * altura * P.parede_exterior_por_m2 });
    const ex = acabamentos.exterior || "A", extra = P.exterior_extra_por_m2[ex] || 0;
    if (extra) linhas.push({ rotulo: `Revestimento exterior: ${MATERIAIS[ex].nome}`, valor: m * altura * extra });
  }
  if (interiores.length) {
    const mi = interiores.reduce((s, w) => s + w.comp, 0);
    linhas.push({ rotulo: `Paredes interiores (${interiores.length}, ${n2(mi)} m)`, valor: mi * pe * P.parede_interior_por_m2 });
    const porMat = {};
    for (const w of interiores) for (const f of ["pos", "neg"]) porMat[w.faces[f]] = (porMat[w.faces[f]] || 0) + w.comp * pe;
    for (const [id, a] of Object.entries(porMat)) {
      const x = P.face_extra_por_m2[id] || 0;
      if (x) linhas.push({ rotulo: `Faces em ${MATERIAIS[id].nome.toLowerCase()} (${a.toFixed(1).replace(".", ",")} m²)`, valor: a * x });
    }
    const np = interiores.reduce((s, w) => s + w.portas.length, 0);
    if (np) linhas.push({ rotulo: `Portas interiores (${np}, 0,80 × 2,00)`, valor: np * P.porta_interior_un });
  }
  for (const f of facesExt) { // outside walls' inner faces in another finish than the standard
    const x = P.face_extra_por_m2[f.material] || 0;
    if (x) linhas.push({ rotulo: `Faces interiores das paredes exteriores em ${MATERIAIS[f.material].nome.toLowerCase()} (${f.area.toFixed(1).replace(".", ",")} m²)`, valor: f.area * x });
  }
  if (cobertura && area > 0) {
    const k = cobertura.tipo === "escondida" ? 1 : Math.hypot(1, cobertura.inclinacao / 100); // the slope in %
    const nome = cobertura.tipo === "escondida" ? "escondida" : `à vista: ${(cobertura.nome || cobertura.tipo).toLowerCase()}`;
    linhas.push({ rotulo: `Cobertura ${nome}`, valor: area * k * P.cobertura_por_m2[cobertura.tipo] });
    const ateto = divisoes.length ? divisoes.reduce((s, d) => s + d.area, 0) : area;
    linhas.push({ rotulo: `Teto falso em gesso cartonado (${ateto.toFixed(1).replace(".", ",")} m²)`, valor: ateto * P.teto_por_m2 });
  }
  for (const v of vaos) {
    const c = CATALOGO[v.tipo];
    const base = P.vao_un[v.tipo] ?? v.largura * v.altura * P.vao_por_m2;
    linhas.push({ rotulo: `${c.nome} ${n2(v.largura)} × ${n2(v.altura)}${v.estore ? " com estore" : ""}`, valor: base + (v.estore ? P.estore_un : 0) });
  }
  if (paredes.length && area > 0) { // by room when the rooms are known (the floor area between the finished faces)
    const porMat = {};
    if (divisoes.length) for (const d of divisoes) porMat[d.material] = (porMat[d.material] || 0) + d.area;
    else porMat[acabamentos.pavimento || "vinilico"] = area;
    for (const [pv, a] of Object.entries(porMat)) {
      linhas.push({ rotulo: `Pavimento ${MATERIAIS[pv].nome.toLowerCase()} (${a.toFixed(1).replace(".", ",")} m²)`, valor: a * (P.pavimento_por_m2[pv] || 0) });
    }
  }
  return { linhas, total: linhas.reduce((s, l) => s + l.valor, 0) };
}
