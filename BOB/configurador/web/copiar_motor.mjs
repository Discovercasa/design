// Copies the engine (the repo's Python, standard library only) and Pyodide into public/, for the browser.
// The engine stays one source: ferramentas/ — this only copies it (rulebook §0a: "never a copy" of the rules).
// Only the tools and the standard JSON: never a project folder or client data.
import { cpSync, mkdirSync, readdirSync, writeFileSync, existsSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const aqui = dirname(fileURLToPath(import.meta.url));
const raiz = resolve(aqui, "..", "..");
const motor = join(aqui, "public", "motor");
const ficheiros = [
  "ferramentas/__init__.py",
  "ferramentas/comum.py",
  "ferramentas/modelo/__init__.py",
  "ferramentas/modelo/camadas.py",
  "ferramentas/modelo/casa_planta.py",
  "ferramentas/modelo/divisor_modulos.py",
  "ferramentas/modelo/estrutura_dc.py",
  "ferramentas/modelo/geometria2d.py",
  "ferramentas/modelo/paineis.py",
  "ferramentas/modelo/pergola.py",
  "ferramentas/modelo/telhado.py",
  "ferramentas/modelo/telhado_estrutura.py",
  "ferramentas/modelo/sistema_construtivo.json",
  "ferramentas/configurador/__init__.py",
  "ferramentas/configurador/formas.py",
  "ferramentas/configurador/para_construtor.py",
];
for (const f of ficheiros) {
  const destino = join(motor, f);
  mkdirSync(dirname(destino), { recursive: true });
  cpSync(join(raiz, f), destino);
}
writeFileSync(join(motor, "lista.json"), JSON.stringify(ficheiros, null, 1));

const py = join(aqui, "node_modules", "pyodide");
const destPy = join(aqui, "public", "pyodide");
if (existsSync(py)) {
  mkdirSync(destPy, { recursive: true });
  for (const f of readdirSync(py)) {
    if (!/\.(mjs|js|wasm|zip|json)$/.test(f) || f === "package.json") continue;
    const origem = join(py, f), destino = join(destPy, f);  // only what changed: Pyodide is ~10 MB
    if (existsSync(destino) && statSync(destino).size === statSync(origem).size) continue;
    cpSync(origem, destino);
  }
}
console.log(`motor: ${ficheiros.length} ficheiros -> public/motor; pyodide -> public/pyodide`);
