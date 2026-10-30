// Document generator page: drop a drawing -> the plans found -> the choices -> checks + 3D -> Módulos, Cobertura, Listagem.
import * as THREE from "three";
import { OrbitControls } from "./vendor/OrbitControls.js";

const $ = (id) => document.getElementById(id);
const motor = new Worker(new URL("./motor.worker.js", import.meta.url), { type: "module" });
let escolhida = 0;
let pronto = false;
let urls = [];

function estado(txt, erro = false) { $("estado").textContent = txt; $("estado").className = erro ? "erro" : "ajuda"; }

motor.onmessage = ({ data }) => {
  if (data.tipo === "pronto") { pronto = true; estado("Pronto. Larga a planta de arquitetura."); }
  else if (data.tipo === "candidatos") mostrarPlantas(data.candidatos);
  else if (data.tipo === "documentos") { mostrarDocs(data); mostrarVerificacao(data); }
  else if (data.tipo === "erro") {
    $("gerar").disabled = false; $("gerar-estado").textContent = "";
    estado("Não foi possível: " + data.erro, true);
  }
};
motor.postMessage({ tipo: "estado" });

function abrir(f) {
  if (!f) return;
  const ext = f.name.toLowerCase().split(".").pop();
  if (ext === "dwg") {
    estado("DWG ainda não é lido. No AutoCAD exporta a planta em PDF ou DWFx (Publicar) e larga esse ficheiro.", true);
    return;
  }
  if (ext !== "dwfx" && ext !== "pdf") { estado("Escolhe um ficheiro DWFx ou PDF do projeto de arquitetura.", true); return; }
  if (!pronto) { estado("O motor ainda está a arrancar, tenta daqui a uns segundos.", true); return; }
  ["passo-planta", "passo-escolhas", "passo-ver", "passo-docs"].forEach((id) => { $(id).hidden = true; });
  estado(`A ler ${f.name}…`);
  f.arrayBuffer().then((bytes) => motor.postMessage({ tipo: "analisar", nome: f.name, bytes }, [bytes]));
}

const zona = $("largar");
zona.addEventListener("click", () => $("ficheiro").click());
zona.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("ficheiro").click(); } });
$("ficheiro").addEventListener("change", (e) => abrir(e.target.files[0]));
zona.addEventListener("dragover", (e) => { e.preventDefault(); zona.classList.add("sobre"); });
zona.addEventListener("dragleave", () => zona.classList.remove("sobre"));
zona.addEventListener("drop", (e) => { e.preventDefault(); zona.classList.remove("sobre"); abrir(e.dataTransfer.files[0]); });

const m2 = (v) => v.toFixed(2).replace(".", ",");

function mostrarPlantas(cs) {
  if (!cs.length) {
    estado("Não encontrei nenhuma planta com paredes a vermelho neste ficheiro. Se for um PDF digitalizado (uma imagem), não tem linhas para ler: usa o PDF ou o DWFx exportado do AutoCAD.", true);
    return;
  }
  estado(`${cs.length === 1 ? "Encontrei 1 planta" : `Encontrei ${cs.length} plantas`}. A primeira é a mais provável.`);
  const box = $("plantas");
  box.innerHTML = "";
  cs.forEach((c, i) => {
    const el = document.createElement("div");
    el.className = "planta" + (i === 0 ? " escolhida" : "");
    el.tabIndex = 0;
    el.innerHTML = c.svg + `<p><strong>Folha ${c.folha}</strong> · escala 1:${c.escala}</p>` +
      `<p class="ajuda">${m2(c.largura)} × ${m2(c.profundidade)} m · ${c.exteriores} paredes exteriores, ` +
      `${c.paredes - c.exteriores} interiores · ${c.vaos} vãos</p>`;
    const escolher = () => { escolhida = i; box.querySelectorAll(".planta").forEach((p, k) => p.classList.toggle("escolhida", k === i)); };
    el.addEventListener("click", escolher);
    el.addEventListener("keydown", (e) => { if (e.key === "Enter") escolher(); });
    box.appendChild(el);
  });
  escolhida = 0;
  $("passo-planta").hidden = false;
  $("passo-escolhas").hidden = false;
}

$("gerar").addEventListener("click", () => {
  const f = new FormData($("escolhas"));
  const escolhas = Object.fromEntries(f.entries());
  escolhas.pe_direito = parseFloat(escolhas.pe_direito) || 2.5;
  $("gerar").disabled = true;
  $("gerar-estado").textContent = "A construir a casa e a desenhar os documentos…";
  motor.postMessage({ tipo: "gerar", indice: escolhida, escolhas });
});

function mostrarDocs({ ficheiros, notas, avisos }) {
  $("gerar").disabled = false;
  $("gerar-estado").innerHTML = '<span class="ok">Documentos prontos.</span>';
  urls.forEach((u) => URL.revokeObjectURL(u));
  urls = [];
  const box = $("docs");
  box.innerHTML = "";
  const ordem = (n) => ["Modulos.pdf", "Cobertura.pdf", "Listagem_Material.pdf", "Listagem_Material.csv"].findIndex((s) => n.endsWith(s));
  ficheiros.sort((a, b) => ordem(a.nome) - ordem(b.nome)).forEach(({ nome, bytes }) => {
    const tipo = nome.endsWith(".pdf") ? "application/pdf" : "text/csv";
    const url = URL.createObjectURL(new Blob([bytes], { type: tipo }));
    urls.push(url);
    const a = document.createElement("a");
    a.href = url; a.download = nome; a.target = "_blank";
    a.innerHTML = `<span>${nome}</span><span class="ajuda">${(bytes.length / 1024).toFixed(0)} kB · descarregar</span>`;
    box.appendChild(a);
  });
  $("notas").innerHTML = [...(avisos || []), ...(notas || [])].map((t) => `<li>${t.replace(/</g, "&lt;")}</li>`).join("");
  $("passo-docs").hidden = false;
}

const esc = (t) => String(t).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

function mostrarVerificacao({ verificacao: v, pecas, contorno }) {
  const mau = v.choques.length + v.fora.length;
  $("selo").textContent = mau ? `${mau} ${mau === 1 ? "problema" : "problemas"}` : "Sem problemas";
  $("selo").className = "selo" + (mau ? " mau" : "");
  $("ver-resumo").textContent = `${v.pecas} peças de madeira verificadas: peças a atravessar outras (mais de 8 mm) e peças fora do sítio.`;
  const n = (x) => String(x).replace(".", ",");
  $("ver-lista").innerHTML = [
    ...v.choques.map((c) => `<li><strong>${n(c.cm)} cm</strong> · ${esc(c.a)} atravessa ${esc(c.b)} (perto de x ${n(c.perto[0])}, y ${n(c.perto[1])}, z ${n(c.perto[2])} m)</li>`),
    ...v.fora.map((f) => `<li>${esc(f.peca)}: ${esc(f.porque)}</li>`),
  ].join("");
  $("passo-ver").hidden = false;
  desenhar(pecas, contorno);
  $("passo-ver").scrollIntoView({ behavior: "smooth" });
}

// ---------------------------------------------------------------- 3D (model: z up -> three: y up, (x, z, -y))
let cena = null;
function cor(p) {
  if (p.erro) return 0xd62828;
  if (/^(Montante|Ombreira|Travessa|Verga|Padieira|Peitoril)/.test(p.tipo)) return 0xc9a36b;
  if (/(Amarra|Lamelada|Viga)/.test(p.tipo + p.nome)) return 0x8d6e4a;
  return 0xb8b0a0;
}

function desenhar(pecas, contorno) {
  const canvas = $("vista");
  if (!cena) {
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 500);
    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xeceae4);
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8170, 1.6));
    const sol = new THREE.DirectionalLight(0xffffff, 1.6);
    sol.position.set(20, 30, 15);
    scene.add(sol);
    cena = { renderer, camera, controls, scene, grupo: null };
    const tamanho = () => {
      const w = canvas.clientWidth, h = canvas.clientHeight;
      if (!w || !h) return;
      renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
    };
    new ResizeObserver(tamanho).observe(canvas);
    tamanho();
    (function animar() { requestAnimationFrame(animar); controls.update(); renderer.render(scene, camera); })();
  }
  if (cena.grupo) { cena.scene.remove(cena.grupo); cena.grupo.traverse((o) => o.geometry && o.geometry.dispose()); }
  const grupo = new THREE.Group();
  const porCor = new Map();
  for (const p of pecas) {
    const c = cor(p);
    if (!porCor.has(c)) porCor.set(c, []);
    porCor.get(c).push(p);
  }
  const V = (q) => [q[0], q[2], -q[1]];
  for (const [c, lista] of porCor) {
    const pos = [];
    for (const { b, t } of lista) {
      const tri = (a, bb, cc) => pos.push(...V(a), ...V(bb), ...V(cc));
      const k = b.length;
      for (let i = 1; i < k - 1; i++) { tri(b[0], b[i + 1], b[i]); tri(t[0], t[i], t[i + 1]); }
      for (let i = 0; i < k; i++) { const j = (i + 1) % k; tri(b[i], b[j], t[j]); tri(b[i], t[j], t[i]); }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    g.computeVertexNormals();
    grupo.add(new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: c, roughness: 0.85, side: THREE.DoubleSide,
      ...(c === 0xd62828 ? { emissive: 0x550000 } : {}) })));
  }
  if (contorno && contorno.length > 2) { // the foundation base, a thin slab under the outline
    const forma = new THREE.Shape(contorno.map(([x, y]) => new THREE.Vector2(x, y)));
    const laje = new THREE.Mesh(new THREE.ExtrudeGeometry(forma, { depth: 0.15, bevelEnabled: false }),
      new THREE.MeshStandardMaterial({ color: 0xa7a59e, roughness: 1 }));
    laje.rotation.x = -Math.PI / 2;
    laje.position.y = -0.15;
    grupo.add(laje);
  }
  cena.scene.add(grupo);
  cena.grupo = grupo;
  const caixa = new THREE.Box3().setFromObject(grupo);
  const centro = caixa.getCenter(new THREE.Vector3());
  const raio = caixa.getSize(new THREE.Vector3()).length() / 2;
  cena.controls.target.copy(centro);
  cena.camera.position.set(centro.x + raio * 1.1, centro.y + raio * 0.9, centro.z + raio * 1.3);
  cena.camera.near = raio / 100; cena.camera.far = raio * 20; cena.camera.updateProjectionMatrix();
}
