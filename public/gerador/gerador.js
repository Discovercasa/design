// Document generator page: drop a drawing -> the plans found -> the choices -> Módulos, Cobertura, Listagem de material.
const $ = (id) => document.getElementById(id);
const motor = new Worker(new URL("./motor.worker.js", import.meta.url), { type: "module" });
let escolhida = 0;
let pronto = false;
let urls = [];

function estado(txt, erro = false) { $("estado").textContent = txt; $("estado").className = erro ? "erro" : "ajuda"; }

motor.onmessage = ({ data }) => {
  if (data.tipo === "pronto") { pronto = true; estado("Pronto. Larga a planta de arquitetura."); }
  else if (data.tipo === "candidatos") mostrarPlantas(data.candidatos);
  else if (data.tipo === "documentos") mostrarDocs(data);
  else if (data.tipo === "erro") {
    $("gerar").disabled = false; $("gerar-estado").textContent = "";
    estado("Não foi possível: " + data.erro, true);
  }
};
motor.postMessage({ tipo: "estado" });

function abrir(f) {
  if (!f) return;
  const ext = f.name.toLowerCase().split(".").pop();
  if (ext === "pdf" || ext === "dwg") {
    estado(`${ext.toUpperCase()} ainda não é lido. No AutoCAD exporta a planta em DWFx (Publicar → DWFx) e larga esse ficheiro.`, true);
    return;
  }
  if (ext !== "dwfx") { estado("Escolhe um ficheiro DWFx do projeto de arquitetura.", true); return; }
  if (!pronto) { estado("O motor ainda está a arrancar, tenta daqui a uns segundos.", true); return; }
  ["passo-planta", "passo-escolhas", "passo-docs"].forEach((id) => { $(id).hidden = true; });
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
  if (!cs.length) { estado("Não encontrei nenhuma planta com paredes a vermelho neste ficheiro.", true); return; }
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
  $("passo-docs").scrollIntoView({ behavior: "smooth" });
}
