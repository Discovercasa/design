// The 3D view (three.js, as IKEA Kreativ): the base, the client's walls with their doors and windows, the interior
// walls, and the structure the engine builds. Plan coordinates (x east, y north, z up) -> three.js (x, z up as y, -y as z).
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DObject, CSS2DRenderer } from "three/addons/renderers/CSS2DRenderer.js";

const COR = {
  base: 0xb9b6ae, parede: 0x6e4b31, destaque: 0x9a6a44, caixilho: 0x383e42, vidro: 0x9fc3d6, fosco: 0xdfe7ea,
  interior: 0xf1efe9, porta: 0xd9cdb8, aro: 0xcdbfa8, telhado: 0x55595e, realce: 0xe2a43a, chao: 0xc9b79c,
};
// finished walls: cladding outside the base edge (until the engine gives the chosen cladding's — Cena.fora), frame
// and lining inside
const FORA = 0.09, DENTRO = 0.16, ESP_INT = 0.13;
const MEIA_PORTA = 0.435, ALTURA_PORTA = 2.03;     // interior door rough opening 0,87 x 2,03 (method)
const FOLHAS = { janela_correr: 2, janela_correr_3: 3, janela_correr_4: 4 }; // the leaves of the sliding windows
// the shutter box over a frame (the rough opening above it, para_construtor: + 0,20 over a window to the floor, + 0,15
// over a window less the 2,5 cm clearance)
export const caixaEstore = (v) => (v.estore ? (v.z0 > 0.01 ? 0.125 : 0.2) : 0);
const GRUPOS = ["base", "chao", "paredes", "empenas", "vaos", "interiores", "telhado", "teto", "exteriores", "previa", "medidas", "estrutura", "cotas", "realce"];
const cor = (c) => (typeof c === "string" ? new THREE.Color(c) : c);

// the engine's pieces — convex prisms {b: base polygon, e: extrusion | t: top polygon}, plan metres, z up — as one
// mesh per colour; add(colour, prisms) collects them, meshes() gives the meshes
function prismas(mapear = (x, y) => [x, y]) {
  const porCor = new Map();
  const v3 = ([x, y, z]) => { const [a, b] = mapear(x, y); return [a, z, -b]; };
  const tri = (c, t) => { if (!porCor.has(c)) porCor.set(c, []); porCor.get(c).push(...t); };
  return {
    add(c, pecas, lados = true) { // lados false: only the faces top and bottom (a surface of pieces, no joints seen)
      for (const pc of pecas) {
        const topo = pc.t || pc.b.map(([x, y, z]) => [x + pc.e[0], y + pc.e[1], z + pc.e[2]]);
        const B = pc.b.map(v3), T = topo.map(v3), n = B.length;
        for (let i = 1; i < n - 1; i++) {
          tri(c, [...B[0], ...B[i + 1], ...B[i]]);
          tri(c, [...T[0], ...T[i], ...T[i + 1]]);
        }
        for (let i = 0; lados && i < n; i++) {
          const j = (i + 1) % n;
          tri(c, [...B[i], ...B[j], ...T[j]]);
          tri(c, [...B[i], ...T[j], ...T[i]]);
        }
      }
    },
    meshes(rug = 0.8) {
      return [...porCor].map(([c, arr]) => {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.Float32BufferAttribute(arr, 3));
        geo.computeVertexNormals();
        return new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: c, roughness: rug, flatShading: true, side: THREE.DoubleSide }));
      });
    },
  };
}

export class Cena {
  constructor(el) {
    this.el = el;
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    el.appendChild(this.renderer.domElement);
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xeef0f2);
    this.camera = new THREE.PerspectiveCamera(40, 1, 0.1, 500);
    this.camera.position.set(22, 18, 26);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.maxPolarAngle = Math.PI / 2 - 0.02;
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x8d8d8d, 2.0));
    const sol = new THREE.DirectionalLight(0xffffff, 2.2);
    sol.position.set(18, 30, 14);
    this.scene.add(sol);
    const chao = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ color: 0xdfe3e6, roughness: 1 }));
    chao.rotation.x = -Math.PI / 2;
    chao.position.y = -0.201;
    this.scene.add(chao);
    this.fora = FORA; // the cladding's depth outside the base edge: the engine's, for the cladding chosen
    this.grupos = {};
    for (const g of GRUPOS) {
      this.grupos[g] = new THREE.Group();
      this.scene.add(this.grupos[g]);
    }
    this.rotulos = new CSS2DRenderer(); // the dimension of every side of the base, editable (as IKEA Kreativ)
    this.rotulos.domElement.className = "rotulos";
    el.appendChild(this.rotulos.domElement);
    this.raio = new THREE.Raycaster();
    this.plano = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    this.edicao = null;    // {lados, aoArrastar(i, d, fim)} while the base can be edited
    this.interacao = null; // {premir(info) -> true to take the drag, arrastar(info), largar(info), pairar(info)}
    this.arrasto = null;
    this.arrastoI = false;
    const tela = this.renderer.domElement;
    tela.addEventListener("pointerdown", (e) => this.premir(e), { capture: true }); // before the orbit controls
    tela.addEventListener("pointermove", (e) => this.mover(e));
    tela.addEventListener("pointerup", (e) => this.largar(e));
    new ResizeObserver(() => this.redimensionar()).observe(el);
    this.redimensionar();
    const loop = () => {
      this.controls.update();
      this.renderer.render(this.scene, this.camera);
      this.rotulos.render(this.scene, this.camera);
      requestAnimationFrame(loop);
    };
    loop();
  }

  redimensionar() {
    const w = this.el.clientWidth || 1, h = this.el.clientHeight || 1;
    this.renderer.setSize(w, h);
    this.rotulos.setSize(w, h);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  limpar(nome) {
    const g = this.grupos[nome];
    for (const o of [...g.children]) {
      g.remove(o);
      o.geometry?.dispose();
      if (o.element) o.element.remove();
    }
  }

  // a box along a plan direction: from s0 to s1 along (p0, u), across from w0 to w1 (along n_in, the inside), z0..z1;
  // its UVs in metres (along the wall, up), so a finish's texture keeps its real size and runs on across pieces
  caixa(grupo, p0, u, s0, s1, w0, w1, z0, z1, material, dados = null) {
    const L = s1 - s0, W = w1 - w0, H = z1 - z0;
    if (L < 1e-3 || W < 1e-3 || H < 1e-3) return null;
    const n = [-u[1], u[0]]; // inward for a counter-clockwise outline
    const sm = (s0 + s1) / 2, wm = (w0 + w1) / 2;
    const geo = new THREE.BoxGeometry(L, H, W);
    const pos = geo.attributes.position, uv = geo.attributes.uv;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i) + L / 2, y = pos.getY(i) + H / 2, z = pos.getZ(i) + W / 2, f = Math.floor(i / 4);
      if (f >= 4) uv.setXY(i, s0 + x, z0 + y);        // the two faces of the wall
      else if (f >= 2) uv.setXY(i, s0 + x, w0 + z);   // top, bottom
      else uv.setXY(i, w0 + z, z0 + y);               // the ends
    }
    const m = new THREE.Mesh(geo, material);
    m.position.set(p0[0] + u[0] * sm + n[0] * wm, (z0 + z1) / 2, -(p0[1] + u[1] * sm + n[1] * wm));
    m.rotation.y = Math.atan2(u[1], u[0]);
    if (dados) m.userData = dados;
    this.grupos[grupo].add(m);
    return m;
  }

  // ---------------------------------------------------------------- dimensions and dragging the sides of the base
  // cotas: [{i, meio:[x,y], n:[nx,ny], valor}]; aoMudar(i, metros) when a value is typed (null = read only)
  cotas(cotas, aoMudar = null) {
    this.limpar("cotas");
    for (const c of cotas) {
      const div = document.createElement("div");
      div.className = "cota";
      if (aoMudar) {
        const inp = document.createElement("input");
        inp.type = "number";
        inp.step = "0.05";
        inp.min = "1";
        inp.value = c.valor.toFixed(2);
        inp.title = `Lado ${c.i + 1}: escreva a medida e carregue em Enter`;
        inp.addEventListener("change", () => aoMudar(c.i, Number(inp.value)));
        inp.addEventListener("pointerdown", (e) => e.stopPropagation());
        div.append(inp, document.createTextNode(" m"));
      } else {
        div.textContent = `${c.valor.toFixed(2).replace(".", ",")} m`;
      }
      const o = new CSS2DObject(div);
      o.position.set(c.meio[0] + c.n[0] * 0.9, 0.05, -(c.meio[1] + c.n[1] * 0.9));
      this.grupos.cotas.add(o);
    }
  }

  pontoNoChao(e) {
    this.apontar(e);
    const p = new THREE.Vector3();
    return this.raio.ray.intersectPlane(this.plano, p) ? [p.x, -p.z] : null;
  }

  apontar(e) {
    const r = this.renderer.domElement.getBoundingClientRect();
    const ndc = new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    this.raio.setFromCamera(ndc, this.camera);
  }

  // the point on the vertical plane of a side of the base {p0, n}: [x, y, z] or null (dragging along a wall)
  pontoNaParede(e, l) {
    this.apontar(e);
    const nrm = new THREE.Vector3(l.n[0], 0, -l.n[1]);
    const pl = new THREE.Plane().setFromNormalAndCoplanarPoint(nrm, new THREE.Vector3(l.p0[0], 0, -l.p0[1]));
    const p = new THREE.Vector3();
    return this.raio.ray.intersectPlane(pl, p) ? [p.x, -p.z, p.y] : null;
  }

  // what is under the pointer: {chao: [x, y], alvo: the object's data ({lado} / {vao} / {interior} / {porta}), ponto}
  info(e) {
    const chao = this.pontoNoChao(e);
    const objs = [];
    for (const g of ["vaos", "interiores", "paredes", "chao", "exteriores"]) if (this.grupos[g].visible) objs.push(...this.grupos[g].children.filter((o) => o.isMesh));
    const h = this.raio.intersectObjects(objs, false).find((x) => x.object.userData && Object.keys(x.object.userData).length);
    return { chao, alvo: h ? h.object.userData : null, ponto: h ? [h.point.x, -h.point.z, h.point.y] : null, evento: e };
  }

  ladoPerto(p) { // the side of the base under the pointer (within 0,6 m)
    if (!this.edicao || !p) return null;
    let melhor = null;
    for (const l of this.edicao.lados) {
      const [ax, ay] = l.p0, [bx, by] = l.p1, L = l.comprimento;
      const t = Math.max(0, Math.min(1, ((p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay)) / (L * L)));
      const dist = Math.hypot(p[0] - (ax + t * (bx - ax)), p[1] - (ay + t * (by - ay)));
      if (dist < 0.6 && (!melhor || dist < melhor.dist)) melhor = { l, dist };
    }
    return melhor && melhor.l;
  }

  realcar(l) {
    this.limpar("realce");
    if (!l) return;
    const geo = new THREE.BoxGeometry(l.comprimento, 0.06, 0.18);
    const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: COR.realce }));
    const mx = (l.p0[0] + l.p1[0]) / 2, my = (l.p0[1] + l.p1[1]) / 2;
    m.position.set(mx, 0.03, -my);
    m.rotation.y = Math.atan2(l.u[1], l.u[0]);
    this.grupos.realce.add(m);
  }

  editar(edicao) {
    this.edicao = edicao;
    if (!edicao) { this.realcar(null); this.renderer.domElement.style.cursor = ""; }
  }

  interagir(h) {
    this.interacao = h;
    if (!h) this.renderer.domElement.style.cursor = "";
  }

  cursor(c) { this.renderer.domElement.style.cursor = c || ""; }

  premir(e) {
    if (this.edicao) {
      const p = this.pontoNoChao(e), l = this.ladoPerto(p);
      if (!l) return;
      this.arrasto = { l, p0: p, d: 0 };
    } else if (this.interacao) {
      if (!this.interacao.premir(this.info(e))) return;
      this.arrastoI = true;
    } else return;
    this.controls.enabled = false;
    this.renderer.domElement.setPointerCapture(e.pointerId);
  }

  mover(e) {
    if (this.arrasto) {
      const p = this.pontoNoChao(e);
      if (!p) return;
      const { l, p0 } = this.arrasto;
      const d = Math.round(((p[0] - p0[0]) * l.n[0] + (p[1] - p0[1]) * l.n[1]) / 0.05) * 0.05;
      if (Math.abs(d - this.arrasto.d) > 1e-9) {
        this.arrasto.d = d;
        this.edicao.aoArrastar(l.i, d, false);
      }
      return;
    }
    if (this.arrastoI) { this.interacao.arrastar(this.info(e)); return; }
    if (this.interacao) { this.interacao.pairar(this.info(e)); return; }
    const l = this.ladoPerto(this.pontoNoChao(e));
    this.realcar(l);
    this.cursor(l ? (Math.abs(l.u[0]) > 0.5 ? "ns-resize" : "ew-resize") : "");
  }

  largar(e) {
    if (this.arrasto) {
      const { l, d } = this.arrasto;
      this.arrasto = null;
      if (this.edicao) this.edicao.aoArrastar(l.i, d, true);
    } else if (this.arrastoI) {
      this.arrastoI = false;
      if (this.interacao) this.interacao.largar(this.info(e));
    } else return;
    this.controls.enabled = true;
    this.renderer.domElement.releasePointerCapture(e.pointerId);
  }

  enquadrar(cont, deCima = false) {
    const xs = cont.map((p) => p[0]), ys = cont.map((p) => p[1]);
    const cx = (Math.min(...xs) + Math.max(...xs)) / 2, cy = (Math.min(...ys) + Math.max(...ys)) / 2;
    const d = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys), 6);
    this.controls.target.set(cx, deCima ? 0 : 1.2, -cy);
    if (deCima) this.camera.position.set(cx, d * 2.2, -cy + 0.01);
    else this.camera.position.set(cx + d * 0.9, d * 0.85, -cy + d * 1.15);
  }

  poligono(cont, grupo, z, material) { // a flat polygon of the outline at height z (UVs = plan metres)
    this.limpar(grupo);
    if (!cont) return;
    const geo = new THREE.ShapeGeometry(new THREE.Shape(cont.map(([x, y]) => new THREE.Vector2(x, y))));
    geo.rotateX(-Math.PI / 2);
    const mat = material && material.isMaterial ? material : new THREE.MeshStandardMaterial({ color: cor(material), roughness: 0.9 });
    const m = new THREE.Mesh(geo, mat);
    m.position.y = z;
    this.grupos[grupo].add(m);
  }

  // where a plan point shows on the screen (the HUD next to a wall): [x, y] in the view's pixels, or null behind
  paraEcra([x, y, z]) {
    const v = new THREE.Vector3(x, z, -y).project(this.camera);
    if (v.z > 1) return null;
    const r = this.renderer.domElement.getBoundingClientRect();
    return [((v.x + 1) / 2) * r.width, ((1 - v.y) / 2) * r.height];
  }

  base(cont) {
    this.limpar("base");
    if (!cont) return;
    const forma = new THREE.Shape(cont.map(([x, y]) => new THREE.Vector2(x, y)));
    const geo = new THREE.ExtrudeGeometry(forma, { depth: 0.2, bevelEnabled: false });
    geo.rotateX(-Math.PI / 2); // (x, y, z) -> (x, z, -y): the plan on the ground, the slab upwards
    geo.translate(0, -0.2, 0);
    this.grupos.base.add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: COR.base, roughness: 0.95 })));
  }

  // the floor finish and the roof hidden behind the parapet (seen from above only)
  chao(cont, material) { this.poligono(cont, "chao", 0.004, material || COR.chao); }

  // the floor room by room (paredesint.divisoes): each in its finish, its m² written on it (rotulos), the selected one
  // lit; opc: {matDe(i) -> material, sel (index), rotulos}
  divisoes(ds, opc = {}) {
    this.limpar("chao");
    const { matDe = () => null, sel = null, rotulos = false } = opc;
    ds.forEach((d, i) => {
      let m = matDe(i) || new THREE.MeshStandardMaterial({ color: COR.chao, roughness: 0.9 });
      if (i === sel) { m = m.clone(); m.emissive = new THREE.Color(0x5a3e10); }
      const arr = [], uvs = [];
      for (const [x0, x1, y0, y1] of d.celulas) {
        for (const [x, y] of [[x0, y0], [x1, y0], [x1, y1], [x0, y0], [x1, y1], [x0, y1]]) { arr.push(x, 0.004, -y); uvs.push(x, y); }
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.Float32BufferAttribute(arr, 3));
      geo.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
      geo.computeVertexNormals();
      const malha = new THREE.Mesh(geo, m);
      malha.userData = { divisao: i };
      this.grupos.chao.add(malha);
      if (rotulos) {
        const div = document.createElement("div");
        div.className = `cota area${i === sel ? " escolhida" : ""}`;
        div.textContent = `${d.area.toFixed(1).replace(".", ",")} m²`;
        const o = new CSS2DObject(div);
        o.position.set(d.rotulo[0], 0.05, -d.rotulo[1]);
        this.grupos.chao.add(o);
      }
    });
  }

  // a ring on the floor where a click would start or end a wall (snapping), or nothing
  marca(p, erro = false) {
    this.limpar("realce");
    if (!p) return;
    const m = new THREE.Mesh(new THREE.RingGeometry(0.1, 0.17, 28), new THREE.MeshBasicMaterial({ color: erro ? 0xd0453a : COR.realce, depthTest: false, transparent: true, opacity: 0.9 }));
    m.rotation.x = -Math.PI / 2;
    m.position.set(p[0], 0.02, -p[1]);
    this.grupos.realce.add(m);
  }
  telhado(cont, z, material) { this.poligono(cont, "telhado", z, material || COR.telhado); }

  // an exposed roof: its faces (plan polygons with their planes, from the engine) as panels — a slab from the plane
  // (the top of the purlins, where the walls and gables stop) up by the panel's thickness, its edges closed: drawn as a
  // sheet 6 cm above the plane it left a gap over every wall (user 2026-10-22: "um gap que fica visível entre o
  // telhado e as paredes")
  telhadoFaces(faces, material, espessura = 0.06) {
    this.limpar("telhado");
    for (const f of faces || []) {
      const z = ([x, y]) => f.z0 + f.gx * x + f.gy * y; // the plane: z = z0 + gx x + gy y
      const pts = f.pts, n = pts.length;
      const arr = [], uvs = [];
      const [ex, ey] = f.subida; // up the slope (unit, plan): the panel texture runs that way
      const uvDe = ([x, y]) => [x * -ey + y * ex, (x * ex + y * ey) * Math.hypot(1, Math.hypot(f.gx, f.gy))];
      const v = (p, dz) => { arr.push(p[0], z(p) + dz, -p[1]); uvs.push(...uvDe(p)); };
      for (let i = 1; i < n - 1; i++) {
        for (const p of [pts[0], pts[i], pts[i + 1]]) v(p, espessura); // top
        for (const p of [pts[0], pts[i + 1], pts[i]]) v(p, 0); // underside
      }
      for (let i = 0; i < n; i++) { // the edges
        const a = pts[i], b = pts[(i + 1) % n];
        v(a, 0); v(b, 0); v(b, espessura);
        v(a, 0); v(b, espessura); v(a, espessura);
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.Float32BufferAttribute(arr, 3));
      geo.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
      geo.computeVertexNormals();
      const m = new THREE.Mesh(geo, material);
      m.material.side = THREE.DoubleSide;
      this.grupos.telhado.add(m);
    }
  }

  // the gable triangles of an exposed roof: on every side of the base, the wall from the eaves line up to the roof's
  // underside, in vertical strips between the corners of the roof's profile (the faces come from the engine)
  empenas(cont, faces, zE, material) {
    this.limpar("empenas");
    if (!cont || !faces) return;
    const n = cont.length;
    const dentro = (f, x, y) => f.pts.every((p, i) => {
      const q = f.pts[(i + 1) % f.pts.length];
      return (q[0] - p[0]) * (y - p[1]) - (q[1] - p[1]) * (x - p[0]) >= -1e-6;
    });
    const zf = (f, x, y) => f.z0 + f.gx * x + f.gy * y;
    for (let i = 0; i < n; i++) {
      const p0 = cont[i], p1 = cont[(i + 1) % n];
      const L = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]), u = [(p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L];
      const fora = [u[1], -u[0]], d = this.fora * 0.5; // on the cladding's middle
      const P = (s) => [p0[0] + u[0] * s + fora[0] * d, p0[1] + u[1] * s + fora[1] * d];
      const cortes = new Set([0, L]);
      for (const f of faces) for (let k = 0; k < f.pts.length; k++) { // where the side crosses a face's edge
        const a = f.pts[k], b = f.pts[(k + 1) % f.pts.length];
        const da = (a[0] - p0[0]) * fora[0] + (a[1] - p0[1]) * fora[1] - d, db = (b[0] - p0[0]) * fora[0] + (b[1] - p0[1]) * fora[1] - d;
        if (da * db < 0) {
          const t = da / (da - db), x = a[0] + (b[0] - a[0]) * t, y = a[1] + (b[1] - a[1]) * t;
          const s = (x - p0[0]) * u[0] + (y - p0[1]) * u[1];
          if (s > 0 && s < L) cortes.add(s);
        }
      }
      const ss = [...cortes].sort((a, b) => a - b);
      for (let k = 0; k + 1 < ss.length; k++) {
        const sa = ss[k], sb = ss[k + 1];
        if (sb - sa < 1e-3) continue;
        const [mx, my] = P((sa + sb) / 2);
        const fs = faces.filter((f) => dentro(f, mx, my));
        if (!fs.length) continue;
        const f = fs.reduce((a, b) => (zf(b, mx, my) > zf(a, mx, my) ? b : a));
        const za = zf(f, ...P(sa)), zb = zf(f, ...P(sb));
        if (Math.max(za, zb) <= zE + 0.005) continue;
        // a prism with a sloped top: a box from zE to the higher end, its top corners moved down to the profile
        const m = this.caixa("empenas", p0, u, sa, sb, -this.fora, DENTRO, zE - 0.002, Math.max(za, zb), material, { lado: i });
        const pos = m.geometry.attributes.position;
        const H = Math.max(za, zb) - (zE - 0.002);
        for (let v = 0; v < pos.count; v++) {
          if (pos.getY(v) > 0) { // the top corners: x along the strip (local), from -(sb - sa) / 2 to +
            const t = (pos.getX(v) + (sb - sa) / 2) / (sb - sa);
            pos.setY(v, H / 2 - (Math.max(za, zb) - (za + (zb - za) * t)));
          }
        }
        pos.needsUpdate = true;
        m.geometry.computeVertexNormals();
      }
    }
  }

  // the client's walls (3 m blocks) on the base edge, with the holes of the doors and windows; the last placed lighter
  // opc: {altura, material (the cladding), ultima, vaos: [{lado, s0, s1, z0, z1}] rough openings, parapeito (z from
  // which a hidden roof's parapet stands), dentroPlat(lado) (the parapet's roof-side face from the base edge, as the
  // engine builds it: its cladding, or only the gutter's lining — the chapéu covers exactly that width)}
  paredes(cont, paredes, opc = {}) {
    this.limpar("paredes");
    const H = opc.altura || 3.0;
    const mat = opc.material || new THREE.MeshStandardMaterial({ color: COR.parede, roughness: 0.8 });
    const matU = mat.clone();
    matU.emissive = new THREE.Color(0x4a3410); // the wall just placed, lit up
    const liso = new THREE.MeshStandardMaterial({ color: COR.interior, roughness: 0.9 });
    const n = cont.length;
    const dir = (i) => { const a = cont[i], b = cont[(i + 1) % n], L = Math.hypot(b[0] - a[0], b[1] - a[1]); return [(b[0] - a[0]) / L, (b[1] - a[1]) / L, L]; };
    // the inner face in its finish (user 2026-10-22: the client chooses it — gesso cartonado the standard); the box's
    // -z face is the inner one (+z = outwards)
    const porLado = new Map();
    const mats = (lado, m) => {
      const k = `${lado}|${m === matU}`;
      if (!porLado.has(k)) {
        let dentro = (opc.interior && opc.interior(lado)) || liso;
        if (opc.selLado === lado) { dentro = dentro.clone(); dentro.emissive = new THREE.Color(0x6a4a12); }
        porLado.set(k, [m, m, m, m, m, dentro]);
      }
      return porLado.get(k);
    };
    for (const p of paredes) {
      const p0 = cont[p.lado];
      const [ux, uy, L] = dir(p.lado), u = [ux, uy];
      const m = mats(p.lado, p === opc.ultima ? matU : mat), dados = { lado: p.lado };
      // the walls joined, no joint between the client's 3 m blocks (user 2026-10-21: "as paredes devem estar unidas");
      // each side closes the corner at its end: past an outside corner by the cladding, past an inside one by the
      // frame + lining (the other side's wall starts at the corner), 0,5 mm short so no two faces fight
      const dentroP = (k) => (opc.dentroPlat && opc.dentroPlat(k)) || DENTRO;
      let a = p.s0, b = p.s1, bP = p.s1;
      if (Math.abs(p.s1 - L) < 1e-6) {
        const [vx, vy] = dir((p.lado + 1) % n), convexo = ux * vy - uy * vx > 0;
        b += (convexo ? this.fora : DENTRO) - 0.0005;
        bP += (convexo ? this.fora : dentroP((p.lado + 1) % n)) - 0.0005;
      }
      // a parapet's roof side (hidden roof, the roof shown) in the facade's cladding (camadas.platibanda_interior), as
      // wide as the engine builds it
      const zc = opc.parapeito, fora = m[0], dP = dentroP(p.lado);
      const bloco = (s0, s1, z0, z1) => {
        if (!zc || zc >= z1) return this.caixa("paredes", p0, u, s0, s1, -this.fora, DENTRO, z0, z1, m, dados);
        if (zc > z0) this.caixa("paredes", p0, u, s0, s1, -this.fora, DENTRO, z0, zc, m, dados);
        // 3 mm short of the roof-side face: that face is the engine's (its cladding, or the gutter's lining on a
        // gutter wall) — drawn on the same plane the two fought (user 2026-10-29: "a parte de dentro da platibanda
        // fica com a cor do painel sandwich")
        this.caixa("paredes", p0, u, s0, s1 === b ? bP : s1, -this.fora, dP - 0.003, Math.max(z0, zc), z1, fora, dados);
      };
      let s = a;
      const vs = (opc.vaos || []).filter((v) => v.lado === p.lado && v.s1 > a && v.s0 < b).sort((x, y) => x.s0 - y.s0);
      for (const v of vs) {
        const v0 = Math.max(v.s0, a), v1 = Math.min(v.s1, b);
        bloco(s, v0, 0, H);
        bloco(v0, v1, 0, v.z0);
        bloco(v0, v1, v.z1, H);
        s = v1;
      }
      bloco(s, b, 0, H);
    }
  }

  // the frames, glass and door leaves; vaos: [{id, lado, tipo, s0, s1 (frame), z0, z1 (frame), vidro}]
  vaos(cont, vaos, selId = null) {
    this.limpar("vaos");
    const caix = new THREE.MeshStandardMaterial({ color: COR.caixilho, roughness: 0.5 });
    const sel = new THREE.MeshStandardMaterial({ color: COR.realce, roughness: 0.5 });
    const vidro = new THREE.MeshStandardMaterial({ color: COR.vidro, roughness: 0.1, transparent: true, opacity: 0.45 });
    const fosco = new THREE.MeshStandardMaterial({ color: COR.fosco, roughness: 0.3, transparent: true, opacity: 0.85 });
    for (const v of vaos) {
      const p0 = cont[v.lado], p1 = cont[(v.lado + 1) % cont.length];
      const L = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]), u = [(p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L];
      const m = v.id === selId ? sel : caix, d = { vao: v.id }, f = 0.06, w0 = 0.0, w1 = 0.07;
      this.caixa("vaos", p0, u, v.s0, v.s1, w0, w1, v.z1 - f, v.z1, m, d);
      this.caixa("vaos", p0, u, v.s0, v.s0 + f, w0, w1, v.z0, v.z1, m, d);
      this.caixa("vaos", p0, u, v.s1 - f, v.s1, w0, w1, v.z0, v.z1, m, d);
      // the bottom rail, a window to the floor too (user 2026-10-28: "as janelas ficaram sem a caixilharia na parte de
      // baixo, aparece como se o vidro estivesse diretamente encostado à base"); the garage door runs to the floor
      const baixo = v.tipo !== "portao";
      if (baixo) this.caixa("vaos", p0, u, v.s0, v.s1, w0, w1, v.z0, v.z0 + f, m, d);
      const opaco = v.tipo === "porta" || v.tipo === "portao";
      const zb = baixo ? v.z0 + f : v.z0;
      this.caixa("vaos", p0, u, v.s0 + f, v.s1 - f, 0.025, 0.045, zb, v.z1 - f, opaco ? m : v.vidro === "fosco" ? fosco : vidro, d);
      const folhas = FOLHAS[v.tipo] || 1; // a sliding window's leaves meet on a bar
      for (let k = 1; k < folhas; k++) {
        const s = v.s0 + ((v.s1 - v.s0) * k) / folhas;
        this.caixa("vaos", p0, u, s - f / 2, s + f / 2, w0, w1, v.z0, v.z1, m, d);
      }
      // the exterior shutter's box over the frame, in the rough opening (+0,15 over a window, +0,20 over a window to the
      // floor — why the opening in the structure is taller than the window, user 2026-10-22)
      if (v.estore) this.caixa("vaos", p0, u, v.s0 - 0.025, v.s1 + 0.025, -this.fora + 0.005, 0.10, v.z1, v.z1 + caixaEstore(v), m, d);
    }
  }

  // interior walls (resolved: {id, o, c, a, b, fimA, fimB, faces: {pos, neg}, portas: [{id, s}]}) with their door
  // openings and leaves, each face in its finish; the selected one lit, with a handle on its free end and its length
  // opc: {sel: {tipo, id, face}, matDe(id) -> material}
  interiores(lista, pe, opc = {}) {
    this.limpar("interiores");
    const { sel = null, matDe = () => null } = opc;
    const liso = new THREE.MeshStandardMaterial({ color: COR.interior, roughness: 0.9 });
    const porta = new THREE.MeshStandardMaterial({ color: COR.porta, roughness: 0.7 });
    const portaS = new THREE.MeshStandardMaterial({ color: COR.realce, roughness: 0.7 });
    const aro = new THREE.MeshStandardMaterial({ color: COR.aro, roughness: 0.7 });
    const metal = new THREE.MeshStandardMaterial({ color: 0xc3c7cb, metalness: 0.5, roughness: 0.35 });
    const aceso = (m, forte) => { const c = m.clone(); c.emissive = new THREE.Color(forte ? 0x6a4a12 : 0x2e2008); return c; };
    const porId = new Map(lista.map((q) => [q.id, q]));
    // a face of wall w in its finish, lit when w is selected (that face, or both — "ambas")
    const faceDe = (w, k) => {
      const m = matDe((w.faces || {})[k] || "pladur") || liso;
      return sel && sel.tipo === "interior" && sel.id === w.id ? aceso(m, sel.face === k || !!sel.ambas) : m;
    };
    // the line of wall x goes on through s (along its axis): x runs past it, or another wall in line with x ends there
    const seguida = (x, s) => (s > x.a + 0.02 && s < x.b - 0.02)
      || lista.some((p) => p.id !== x.id && p.o === x.o && Math.abs(p.c - x.c) < 0.02 && (Math.abs(p.a - s) < 0.02 || Math.abs(p.b - s) < 0.02));
    for (const r of lista) {
      if (!Number.isFinite(r.a) || !Number.isFinite(r.b)) continue;
      const u = r.o === "h" ? [1, 0] : [0, 1], p0 = r.o === "h" ? [0, r.c] : [r.c, 0];
      const escolhida = sel && sel.tipo === "interior" && sel.id === r.id;
      const topo = escolhida ? aceso(liso, false) : liso;
      // an end on another interior wall: against its face (a T); two walls in line on it meet on its centre line; at a
      // corner (that wall ends there too — user 2026-10-22: "deve fazer 90º perfeitamente") the X wall runs through to
      // the far face, the Y wall stops — the X wall's end is then the Y wall's face round the corner, in its finish (user
      // 2026-10-28: "esse lado que faz o canto da parede quando se aplica a textura a parede nao fica com a textura,
      // fica branco"). {t: the trim, m: the end face's material, canto}
      const fim = (k, ref, lado) => {
        if (k === "ext") return { t: DENTRO, m: topo };
        if (k !== "int") return { t: 0, m: topo };
        const q = porId.get(ref.id);
        if (!q || seguida(q, r.c)) return { t: ESP_INT / 2, m: topo };
        if (seguida(r, q.c)) return { t: 0, m: topo };
        if (r.o !== "h") return { t: ESP_INT / 2, m: topo };
        return { t: -ESP_INT / 2, m: faceDe(q, lado === "b" ? "pos" : "neg"), canto: true };
      };
      const fA = fim(r.fimA, r.refA, "a"), fB = fim(r.fimB, r.refB, "b");
      const a = r.a + fA.t, b = r.b - fB.t;
      // BoxGeometry faces: +x (the b end), -x (the a end), +y, -y, +z, -z; +z is the plan's -y for an "h" wall, +x
      // for a "v" wall
      const faces = r.o === "h" ? [faceDe(r, "neg"), faceDe(r, "pos")] : [faceDe(r, "pos"), faceDe(r, "neg")];
      const mats = (ini, ult) => [ult ? fB.m : topo, ini ? fA.m : topo, topo, topo, ...faces];
      const canto = (m, ini, ult) => { // a corner end: the texture runs on from the other wall's face (along plan y)
        if (!m) return;
        const pos = m.geometry.attributes.position, uv = m.geometry.attributes.uv;
        for (const [k, sim] of [[0, ult && fB.canto], [1, ini && fA.canto]]) if (sim) for (let i = k * 4; i < k * 4 + 4; i++) uv.setX(i, r.c - pos.getZ(i));
        uv.needsUpdate = true;
      };
      const d = { interior: r.id };
      let s = a, ini = true;
      for (const pt of [...r.portas].sort((x, y) => x.s - y.s)) {
        const d0 = pt.s - MEIA_PORTA, d1 = pt.s + MEIA_PORTA;
        canto(this.caixa("interiores", p0, u, s, d0, -ESP_INT / 2, ESP_INT / 2, 0, pe, mats(ini, false), d), ini, false);
        ini = false;
        this.caixa("interiores", p0, u, d0, d1, -ESP_INT / 2, ESP_INT / 2, ALTURA_PORTA, pe, mats(false, false), d);
        const sp = sel && sel.tipo === "porta" && sel.id === pt.id;
        this.portaInterior(p0, u, d0, d1, sp ? portaS : aro, sp ? portaS : porta, metal, { porta: pt.id, interior: r.id });
        s = d1;
      }
      canto(this.caixa("interiores", p0, u, s, b, -ESP_INT / 2, ESP_INT / 2, 0, pe, mats(ini, true), d), ini, true);
      if (escolhida) {
        const livre = r.fimB === "livre" ? b : r.fimA === "livre" ? a : null;
        if (livre !== null) { // the handle to stretch it
          const pega = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.06, 24), new THREE.MeshStandardMaterial({ color: COR.realce, roughness: 0.4 }));
          const [x, y] = r.o === "h" ? [livre, r.c] : [r.c, livre];
          pega.position.set(x, pe + 0.05, -y);
          pega.userData = { ponta: r.id };
          this.grupos.interiores.add(pega);
        }
        this.rotuloParede(r, pe);
        if (sel.troco) { // the piece chosen (between the walls that meet it): a lit sleeve over it
          const [t0, t1] = [Math.max(sel.troco[0], a), Math.min(sel.troco[1], b)];
          const luva = new THREE.MeshBasicMaterial({ color: COR.realce, transparent: true, opacity: 0.4, depthWrite: false });
          this.caixa("interiores", p0, u, t0, t1, -ESP_INT / 2 - 0.015, ESP_INT / 2 + 0.015, 0, pe + 0.015, luva, d);
        }
      }
    }
  }

  // an interior door in its rough opening d0..d1 (0,87 x 2,03 — the 80 x 200 leaf): the frame lining the reveals
  // (3,5 cm at the jambs, 3 cm at the head, the wall's depth), the architraves on both faces, the leaf and a lever
  // handle on each side (user 2026-10-29: "estão com um gap dos lados e na parte de cima e não tem um aspeto de porta
  // interior, estão apenas um retângulo")
  portaInterior(p0, u, d0, d1, mAro, mFolha, metal, dados) {
    const H = ALTURA_PORTA, e = ESP_INT / 2, a = 0.035, at = 0.03, g = 0.07, eg = 0.012;
    const k = (s0, s1, w0, w1, z0, z1, m) => this.caixa("interiores", p0, u, s0, s1, w0, w1, z0, z1, m, dados);
    k(d0, d0 + a, -e, e, 0, H, mAro);                                       // the frame
    k(d1 - a, d1, -e, e, 0, H, mAro);
    k(d0 + a, d1 - a, -e, e, H - at, H, mAro);
    const ls = d1 - a - 0.065;                                               // the lock side
    for (const f of [1, -1]) {
      const w = (x0, x1) => (f > 0 ? [x0, x1] : [-x1, -x0]);
      const gi0 = d0 + a - 0.005, gi1 = d1 - a + 0.005, gz = H - at + 0.005; // the architraves, 5 mm of frame showing
      k(gi0 - g, gi0, ...w(e, e + eg), 0, gz, mAro);
      k(gi1, gi1 + g, ...w(e, e + eg), 0, gz, mAro);
      k(gi0 - g, gi1 + g, ...w(e, e + eg), gz, gz + g, mAro);
      k(ls - 0.022, ls + 0.022, ...w(0.02, 0.028), 1.028, 1.072, metal);     // the rose, the spindle, the lever
      k(ls - 0.008, ls + 0.008, ...w(0.028, 0.052), 1.042, 1.058, metal);
      k(ls - 0.13, ls + 0.008, ...w(0.048, 0.064), 1.041, 1.059, metal);
    }
    k(d0 + a + 0.002, d1 - a - 0.002, -0.02, 0.02, 0.008, H - at - 0.002, mFolha); // the leaf
  }

  // the length of a wall over its middle (while placed, stretched or selected)
  rotuloParede(r, pe) {
    const div = document.createElement("div");
    div.className = "cota comprimento";
    div.textContent = `${(r.b - r.a).toFixed(2).replace(".", ",")} m`;
    const o = new CSS2DObject(div), m = (r.a + r.b) / 2;
    const [x, y] = r.o === "h" ? [m, r.c] : [r.c, m];
    o.position.set(x, pe + 0.35, -y);
    this.grupos.interiores.add(o);
  }

  // a ghost of what is being placed: {tipo: "vao", lado, s0, s1, z0, z1, cont} or {tipo: "parede", o, c, a, b, pe}
  previa(p, erro = false) {
    this.limpar("previa");
    if (!p) return;
    const mat = new THREE.MeshBasicMaterial({ color: erro ? 0xd0453a : COR.realce, transparent: true, opacity: 0.55, depthTest: false });
    if (p.tipo === "vao") {
      const p0 = p.cont[p.lado], p1 = p.cont[(p.lado + 1) % p.cont.length];
      const L = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]), u = [(p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L];
      this.caixa("previa", p0, u, p.s0, p.s1, -this.fora - 0.02, DENTRO + 0.02, p.z0, p.z1, mat);
    } else if (p.tipo === "caixa") { // a block on the plan {x0, x1, y0, y1, z0, z1} (a garage, an annex, a pergola)
      this.caixa("previa", [p.x0, p.y0], [1, 0], 0, p.x1 - p.x0, 0, p.y1 - p.y0, p.z0, p.z1, mat);
    } else if (p.tipo === "porta") { // an interior door on interior wall {o, c} at s
      const u = p.o === "h" ? [1, 0] : [0, 1], p0 = p.o === "h" ? [0, p.c] : [p.c, 0];
      this.caixa("previa", p0, u, p.s - MEIA_PORTA, p.s + MEIA_PORTA, -ESP_INT / 2 - 0.02, ESP_INT / 2 + 0.02, 0, ALTURA_PORTA, mat);
    } else {
      const u = p.o === "h" ? [1, 0] : [0, 1], p0 = p.o === "h" ? [0, p.c] : [p.c, 0];
      this.caixa("previa", p0, u, p.a, p.b, -ESP_INT / 2 - 0.02, ESP_INT / 2 + 0.02, 0, p.pe, mat);
      const div = document.createElement("div");
      div.className = `cota comprimento${erro ? " erro" : ""}`;
      div.textContent = `${(p.b - p.a).toFixed(2).replace(".", ",")} m`;
      const o = new CSS2DObject(div), m = (p.a + p.b) / 2;
      const [x, y] = p.o === "h" ? [m, p.c] : [p.c, m];
      o.position.set(x, p.pe + 0.35, -y);
      this.grupos.previa.add(o);
      if (p.guia) { // to the first point of the walls being drawn: the next wall closes the room (dashed, on the floor)
        const [[x0, y0], [x1, y1]] = p.guia, L = Math.hypot(x1 - x0, y1 - y0);
        const traco = new THREE.MeshBasicMaterial({ color: COR.realce, depthTest: false, transparent: true, opacity: 0.95 });
        if (L > 0.05) for (let t = 0; t < L; t += 0.25) this.caixa("previa", [x0, y0], [(x1 - x0) / L, (y1 - y0) / L], t, Math.min(t + 0.15, L), -0.03, 0.03, 0.02, 0.03, traco);
        const alvo = new THREE.Mesh(new THREE.RingGeometry(0.1, 0.17, 28), traco);
        alvo.rotation.x = -Math.PI / 2;
        alvo.position.set(x1, 0.03, -y1);
        this.grupos.previa.add(alvo);
      }
    }
  }

  // the distances from where an interior wall starts (or stands) to the ends of the wall it starts on (user 2026-10-28:
  // "deve dizer a distância de cada canto"): [{de, ate (plan points on that wall), valor, n (the side to draw them on)}];
  // aoMudar(i, metros) makes them typed (as the base's sides), else read only; null clears
  medidas(lista, aoMudar = null) {
    this.limpar("medidas");
    if (!lista) return;
    const mat = new THREE.LineBasicMaterial({ color: COR.realce, depthTest: false, transparent: true });
    lista.forEach((m, i) => {
      const [nx, ny] = m.n, off = 0.35, tq = 0.12;
      const P = ([x, y]) => new THREE.Vector3(x + nx * off, 0.03, -(y + ny * off));
      const risco = (p) => [[p[0] - nx * tq, p[1] - ny * tq], [p[0] + nx * tq, p[1] + ny * tq]];
      const linha = new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints([m.de, m.ate, ...risco(m.de), ...risco(m.ate)].map(P)), mat);
      linha.renderOrder = 5;
      this.grupos.medidas.add(linha);
      const div = document.createElement("div");
      div.className = "cota medida";
      if (aoMudar) {
        const inp = document.createElement("input");
        inp.type = "number";
        inp.step = "0.05";
        inp.min = "0";
        inp.value = m.valor.toFixed(2);
        inp.title = "Distância ao canto: escreva a medida e carregue em Enter";
        inp.addEventListener("change", () => aoMudar(i, Number(inp.value)));
        inp.addEventListener("pointerdown", (e) => e.stopPropagation());
        div.append(inp, document.createTextNode(" m"));
      } else {
        div.textContent = `${m.valor.toFixed(2).replace(".", ",")} m`;
        div.classList.add("so-ler"); // never in the way of the click that places the wall
      }
      const o = new CSS2DObject(div);
      o.position.copy(P([(m.de[0] + m.ate[0]) / 2, (m.de[1] + m.ate[1]) / 2]));
      this.grupos.medidas.add(o);
    });
  }

  // the false ceiling as the engine builds it — Pladur on its steel profiles, the perimeter angle (camadas.tetos; user
  // 2026-10-28: "O testo falso ainda não aparece no builder e quero que isso seja possível de aparecer"): pieces
  // {nome, material, pecas}
  teto(objetos, materiais, mapear) {
    if (objetos && objetos === this.tetoDe) return; // the same pieces already drawn (redrawn only when they change)
    this.tetoDe = objetos;
    this.limpar("teto");
    if (!objetos) return;
    // smooth, as a finished ceiling is (user 2026-10-30: "O teto falso dá para ver as linhas, numa obra real isso não
    // se vê"): the boards' faces only, no joints between them
    const P = prismas(mapear);
    for (const o of objetos) P.add((materiais[o.material] && materiais[o.material].cor) || "#e9e9e5", o.pecas, false);
    for (const m of P.meshes(0.9)) { m.material.flatShading = false; this.grupos.teto.add(m); }
  }

  // the structure built by the engine: wall framing (panels) and the pieces on top (beams, purlins, posts)
  estrutura(G, materiais, mapear = (x, y) => [x, y]) {
    this.limpar("estrutura");
    if (!G) return;
    const corDe = (nome) => (materiais[nome] && materiais[nome].cor) || "#c8a878";
    const P = prismas(mapear);
    for (const p of G.paineis) {
      const a = G.alcados[p.alcado];
      if (!a || p.fantasma) continue;
      const [ox, oy, oz] = p.origem, [ux, uy] = p.sentido, t = p.espessura;
      const mundo = (u, v, w) => [ox + u * ux - w * uy, oy + u * uy + w * ux, oz + v];
      for (const m of a.members) {
        P.add(corDe(`Madeira ${m.section}`), [{ b: m.poly.map(([u, v]) => mundo(u, v, -t / 2)), t: m.poly.map(([u, v]) => mundo(u, v, t / 2)) }]);
      }
    }
    for (const it of G.estrutura_extra || []) P.add(corDe(it.material), it.pecas);
    for (const m of P.meshes()) this.grupos.estrutura.add(m);
  }

  // the roof as the engine builds it, over the panels already drawn: gutters, downpipes, ridge / hip caps, verge and
  // abutment trims, valley gutters, the parapets' caps, the hidden roof's panels (user 2026-10-28: "faltam calheiras,
  // tubos de queda e esses elementos") — pieces {nome, material, pecas} from camadas.py
  pecasCobertura(objetos, materiais, mapear) {
    const P = prismas(mapear);
    for (const o of objetos || []) P.add((materiais[o.material] && materiais[o.material].cor) || "#3a3f43", o.pecas);
    for (const m of P.meshes(0.5)) this.grupos.telhado.add(m);
  }

  mostrar(nome, sim) {
    this.grupos[nome].visible = sim;
    for (const e of (this.edificios || new Map()).values()) e.grupos[nome].visible = sim; // separate buildings too
  }

  // the pergolas (step 7) as the engine builds them (pergola.py): [{id, objetos}], each pickable ({pergola: id}), the
  // selected one lit
  pergolas(lista, materiais, mapear, selId = null) {
    this.limpar("exteriores");
    for (const pg of lista || []) {
      const P = prismas(mapear);
      for (const o of pg.objetos) P.add((materiais[o.material] && materiais[o.material].cor) || "#c9a06a", o.pecas);
      for (const m of P.meshes(0.75)) {
        if (pg.id === selId) m.material.emissive = new THREE.Color(0x5a3e10);
        m.userData = { pergola: pg.id };
        this.grupos.exteriores.add(m);
      }
    }
  }

  // a separate building (a garage, an annex — step 7) drawn by the same methods into groups of its own, turned rot ×
  // 90° and moved to x, y (plan): emEdificio(id, {x, y, rot}, () => { this.base(...); this.paredes(...); ... })
  emEdificio(id, pos, desenhar) {
    if (!this.edificios) this.edificios = new Map();
    if (!this.edificios.has(id)) {
      const raiz = new THREE.Group(), grupos = {};
      for (const g of GRUPOS) { grupos[g] = new THREE.Group(); grupos[g].visible = this.grupos[g].visible; raiz.add(grupos[g]); }
      this.scene.add(raiz);
      this.edificios.set(id, { raiz, grupos });
    }
    const e = this.edificios.get(id);
    e.raiz.position.set(pos.x, 0, -pos.y);
    e.raiz.rotation.y = ((pos.rot || 0) * Math.PI) / 2;
    const g0 = this.grupos;
    this.grupos = e.grupos;
    try { desenhar(); } finally { this.grupos = g0; }
  }

  // the separate buildings still in the design stay; the others go
  edificiosVivos(ids) {
    for (const [id, e] of this.edificios || new Map()) {
      if (ids.includes(id)) continue;
      const g0 = this.grupos;
      this.grupos = e.grupos;
      for (const g of GRUPOS) this.limpar(g);
      this.grupos = g0;
      this.scene.remove(e.raiz);
      this.edificios.delete(id);
    }
  }
}
