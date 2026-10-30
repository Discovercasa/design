// The finishes the client sees: each with its name, a texture drawn here (procedural, in metres) and a 3D preview on
// a sphere (as ambientCG) — placeholders until the house gets photo-real materials (user 2026-10-21: "mais tarde vamos
// tornar ultra-realista o aspeto da casa"). Colours from sistema_construtivo.json `materiais` where the standard has
// the product (Douglas marron, Reboco branco, Cortiça, Vinílico, Pladur N, Alumínio RAL 7016).
import * as THREE from "three";

// grupo: exterior (the cladding options A / B / C), interior (the faces of interior walls — rulebook §9), pavimento,
// cobertura. tile: metres the texture covers [w, h]; desenho: how the texture is drawn
export const MATERIAIS = {
  A: { grupo: "exterior", nome: "Madeira (Tremolo)", nota: "Douglas marron, tábuas verticais 22 × 135", padrao: "Douglas marron", base: "#6E4B31", tile: [0.564, 1.2], desenho: "tabuas", tabua: 0.141, junta: 0.006, veio: true },
  B: { grupo: "exterior", nome: "ETICS (capoto branco)", nota: "Reboco armado com acabamento branco", padrao: "Reboco branco", base: "#F4F3EE", tile: [1, 1], desenho: "reboco" },
  C: { grupo: "exterior", nome: "Cortiça", nota: "Aglomerado de cortiça expandida 60 mm", padrao: "Cortiça", base: "#4A392E", tile: [1, 1], desenho: "cortica" },
  pladur: { grupo: "interior", nome: "Pintado", nota: "Pladur pintado (hidrófugo nos WC e cozinha)", padrao: "Pladur N", base: "#ECECE8", tile: [1, 1], desenho: "reboco", ruido: 0.012 },
  madeira: { grupo: "interior", nome: "Madeira", nota: "Forro de madeira vertical", base: "#C9A27A", tile: [0.48, 1.2], desenho: "tabuas", tabua: 0.12, junta: 0.004, veio: true },
  ceramico: { grupo: "interior", nome: "Cerâmico", nota: "Azulejo 30 × 60 (WC e cozinha)", base: "#F1F1EE", tile: [0.6, 0.6], desenho: "azulejo", peca: [0.3, 0.6], rejunte: "#CFCFC9" },
  vinilico: { grupo: "pavimento", nome: "Vinílico", nota: "Régua vinílica imitação carvalho", padrao: "Vinílico", base: "#B8966C", tile: [1.2, 1.2], desenho: "reguas", regua: [1.2, 0.2] },
  ceramico_pav: { grupo: "pavimento", nome: "Cerâmico", nota: "Mosaico 60 × 60", base: "#D8D6D0", tile: [1.2, 1.2], desenho: "azulejo", peca: [0.6, 0.6], rejunte: "#BDBBB4" },
  sandwich: { grupo: "cobertura", nome: "Painel sandwich", nota: "Cinza RAL 7016", padrao: "Painel sandwich RAL 7016", base: "#4A5055", tile: [1, 1], desenho: "nervuras" },
};
export const daGrupo = (g) => Object.entries(MATERIAIS).filter(([, m]) => m.grupo === g).map(([id, m]) => ({ id, ...m }));

const PX = 512;
function aleatorio(semente) { // the same picture every time
  let s = semente >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}
function tom(hex, f) { // a colour lighter (f > 0) or darker (f < 0)
  const c = new THREE.Color(hex);
  const h = {}; c.getHSL(h);
  c.setHSL(h.h, h.s, Math.min(1, Math.max(0, h.l * (1 + f))));
  return `#${c.getHexString()}`;
}

function desenhar(m, cor) {
  const cv = document.createElement("canvas");
  cv.width = cv.height = PX;
  const g = cv.getContext("2d"), r = aleatorio(m.nome.length * 7919 + PX);
  const [tw, th] = m.tile, kx = PX / tw, ky = PX / th;
  g.fillStyle = cor;
  g.fillRect(0, 0, PX, PX);
  const ruido = (n, amp, tam = 1) => {
    for (let i = 0; i < n; i++) {
      g.fillStyle = tom(cor, (r() - 0.5) * 2 * amp);
      g.globalAlpha = 0.5;
      g.fillRect(r() * PX, r() * PX, tam, tam);
    }
    g.globalAlpha = 1;
  };
  if (m.desenho === "tabuas") { // vertical boards with grain and dark joints
    const n = Math.round(tw / m.tabua), w = PX / n;
    for (let i = 0; i < n; i++) {
      g.fillStyle = tom(cor, (r() - 0.5) * 0.18);
      g.fillRect(i * w, 0, w, PX);
      if (m.veio) {
        for (let k = 0; k < 26; k++) {
          const x0 = i * w + r() * w, fase = r() * 6.28;
          g.strokeStyle = tom(cor, -0.15 - r() * 0.15);
          g.globalAlpha = 0.25 + r() * 0.3;
          g.lineWidth = 0.6 + r() * 1.2;
          g.beginPath();
          for (let y = 0; y <= PX; y += 16) g.lineTo(x0 + Math.sin(y / 60 + fase) * 2.5, y);
          g.stroke();
        }
        g.globalAlpha = 1;
      }
      g.fillStyle = tom(cor, -0.55);
      g.fillRect(i * w, 0, Math.max(2, m.junta * kx), PX);
    }
  } else if (m.desenho === "reboco") {
    ruido(26000, m.ruido ?? 0.03, 2);
  } else if (m.desenho === "cortica") {
    for (let i = 0; i < 9000; i++) {
      g.fillStyle = tom(cor, (r() - 0.5) * 0.7);
      g.beginPath();
      g.arc(r() * PX, r() * PX, 1 + r() * 3.5, 0, 6.28);
      g.fill();
    }
    g.fillStyle = tom(cor, -0.5);
    g.fillRect(0, PX / 2 - 1, PX, 2); // the 1000 x 500 boards
  } else if (m.desenho === "azulejo") {
    const [pw, ph] = m.peca, nx = Math.round(tw / pw), ny = Math.round(th / ph);
    for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
      g.fillStyle = tom(cor, (r() - 0.5) * 0.05);
      g.fillRect(i * pw * kx, j * ph * ky, pw * kx, ph * ky);
    }
    ruido(6000, 0.02, 2);
    g.fillStyle = m.rejunte;
    for (let i = 0; i <= nx; i++) g.fillRect(i * pw * kx - 2, 0, 4, PX);
    for (let j = 0; j <= ny; j++) g.fillRect(0, j * ph * ky - 2, PX, 4);
  } else if (m.desenho === "reguas") { // floor planks, staggered
    const [lw, lh] = m.regua, ny = Math.round(th / lh), h = PX / ny;
    for (let j = 0; j < ny; j++) {
      const desvio = ((j * 0.37) % 1) * lw * kx;
      for (let x = -desvio; x < PX; x += lw * kx) {
        g.fillStyle = tom(cor, (r() - 0.5) * 0.22);
        g.fillRect(x, j * h, lw * kx, h);
        for (let k = 0; k < 10; k++) {
          const y0 = j * h + r() * h;
          g.strokeStyle = tom(cor, -0.2 - r() * 0.15);
          g.globalAlpha = 0.25;
          g.beginPath(); g.moveTo(x, y0); g.bezierCurveTo(x + lw * kx / 3, y0 + 3, x + 2 * lw * kx / 3, y0 - 3, x + lw * kx, y0); g.stroke();
        }
        g.globalAlpha = 1;
        g.fillStyle = tom(cor, -0.45);
        g.fillRect(x, j * h, 2, h);
      }
      g.fillRect(0, j * h, PX, 2);
    }
  } else if (m.desenho === "nervuras") { // the panel's ribs
    for (let i = 0; i < 4; i++) {
      g.fillStyle = tom(cor, 0.25);
      g.fillRect(i * PX / 4, 0, 10, PX);
      g.fillStyle = tom(cor, -0.25);
      g.fillRect(i * PX / 4 + 10, 0, 4, PX);
    }
  }
  return cv;
}

const cache = new Map();
// the three.js material of a finish (texture in metres: the geometry's UVs are metres — see cena.js uvMetros)
export function materialTres(id, cores = {}) {
  const m = MATERIAIS[id];
  const cor = (m.padrao && cores[m.padrao] && cores[m.padrao].cor) || m.base;
  const chave = `${id}|${cor}`;
  if (!cache.has(chave)) {
    const tx = new THREE.CanvasTexture(desenhar(m, cor));
    tx.wrapS = tx.wrapT = THREE.RepeatWrapping;
    tx.repeat.set(1 / m.tile[0], 1 / m.tile[1]);
    tx.colorSpace = THREE.SRGBColorSpace;
    tx.anisotropy = 4;
    cache.set(chave, new THREE.MeshStandardMaterial({ map: tx, roughness: m.desenho === "azulejo" ? 0.35 : 0.85, metalness: 0 }));
  }
  return cache.get(chave);
}

// the 3D preview: the material on a sphere, rendered once (data URL)
let pre = null;
const imagens = new Map();
export function previa(id, cores = {}) {
  const m = MATERIAIS[id];
  const chave = `${id}|${(m.padrao && cores[m.padrao] && cores[m.padrao].cor) || m.base}`;
  if (imagens.has(chave)) return imagens.get(chave);
  if (!pre) {
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
    renderer.setSize(160, 160);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    const scene = new THREE.Scene();
    scene.add(new THREE.HemisphereLight(0xffffff, 0x666666, 1.6));
    const luz = new THREE.DirectionalLight(0xffffff, 2.4);
    luz.position.set(-2, 2.5, 3);
    scene.add(luz);
    const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 20);
    camera.position.set(0, 0, 4.1);
    const esfera = new THREE.Mesh(new THREE.SphereGeometry(1, 64, 48));
    scene.add(esfera);
    pre = { renderer, scene, camera, esfera };
  }
  const base = materialTres(id, cores), mat = base.clone();
  mat.map = base.map.clone();
  mat.map.needsUpdate = true;
  mat.map.repeat.set(Math.PI * 0.6 / m.tile[0], Math.PI * 0.3 / m.tile[1]); // a 0,6 m ball
  pre.esfera.material = mat;
  pre.renderer.render(pre.scene, pre.camera);
  const url = pre.renderer.domElement.toDataURL("image/png");
  mat.dispose();
  imagens.set(chave, url);
  return url;
}
