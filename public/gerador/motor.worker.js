// The document generator's engine: the repo's own Python (ferramentas/), run in the browser by Pyodide.
// Same engine as the builder on the PC (one source; the publish script only copies it here).
let py = null;

async function iniciar() {
  const base = new URL("./", self.location.href);
  const { loadPyodide } = await import(new URL("/build-your-house/pyodide/pyodide.mjs", self.location.origin).href);
  py = await loadPyodide({ indexURL: new URL("/build-your-house/pyodide/", self.location.origin).href });
  const lista = await (await fetch(new URL("motor/lista.json", base))).json();
  for (const f of lista) {
    const txt = await (await fetch(new URL(`motor/${f}`, base))).text();
    const partes = f.split("/");
    let dir = "/bob";
    for (const p of partes.slice(0, -1)) { dir += "/" + p; try { py.FS.mkdirTree(dir); } catch { /* exists */ } }
    py.FS.writeFile(`/bob/${f}`, txt);
  }
  py.runPython(`
import sys, json, shutil
from pathlib import Path
sys.path.insert(0, "/bob")
from ferramentas.documentos import de_desenhos as DD
CANDIDATOS = []

def analisar(caminho):
    global CANDIDATOS
    CANDIDATOS = DD.candidatos(caminho)
    out = []
    for c in CANDIDATOS:
        ps = c["planta"]["paredes"]
        out.append({"folha": c["folha"], "nome": c["nome"], "escala": c["escala"], "nota": c["nota"],
                    "largura": c["planta"]["contorno"][1], "profundidade": c["planta"]["contorno"][3],
                    "paredes": len(ps), "exteriores": sum(p["exterior"] for p in ps),
                    "vaos": sum(len(p["aberturas"]) for p in ps), "svg": DD.svg_planta(c["planta"], 420)})
    return json.dumps(out, ensure_ascii=False)

def gerar(indice, escolhas_json):
    escolhas = json.loads(escolhas_json)
    casa, avisos = DD.planta_para_casa(CANDIDATOS[indice]["planta"], escolhas)
    saida = Path("/saida")
    shutil.rmtree(saida, ignore_errors=True)
    fich, notas, ver = DD.gerar(casa, saida, escolhas)
    return json.dumps({"ficheiros": fich, "notas": notas, "avisos": avisos, **ver}, ensure_ascii=False)
`);
}

const pronto = iniciar();

self.onmessage = async ({ data }) => {
  try {
    await pronto;
    if (data.tipo === "analisar") {
      const nome = "/entrada/" + data.nome.replace(/[^\w.-]+/g, "_");
      try { py.FS.mkdirTree("/entrada"); } catch { /* exists */ }
      py.FS.writeFile(nome, new Uint8Array(data.bytes));
      const r = JSON.parse(py.globals.get("analisar")(nome));
      self.postMessage({ tipo: "candidatos", candidatos: r });
    } else if (data.tipo === "gerar") {
      const r = JSON.parse(py.globals.get("gerar")(data.indice, JSON.stringify(data.escolhas)));
      const ficheiros = r.ficheiros.map((f) => ({ nome: f.split("/").pop(), bytes: py.FS.readFile(f) }));
      self.postMessage({ tipo: "documentos", ficheiros, notas: r.notas, avisos: r.avisos,
        verificacao: r.verificacao, pecas: r.pecas, contorno: r.contorno });
    } else if (data.tipo === "estado") {
      self.postMessage({ tipo: "pronto" });
    }
  } catch (e) {
    const msg = String(e && e.message || e);
    self.postMessage({ tipo: "erro", erro: msg.split("\n").filter(Boolean).slice(-3).join("\n") });
  }
};
