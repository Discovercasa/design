# IKEA Kreativ — what we learned for the DiscoverCasa configurator (2026-10-20)

The user asked (2026-10-20): "reverse engineer the IKEA KREATIV but for Discovercasa with our method of construction"
using the REA skill (`reverse-engineer-anything`, github.com/morluto/rea). This file records what was observed,
what we infer from it and what stays unknown. The design we take from it is in `especificacao.md`.

## How it was observed (evidence boundary)
- **Passive use as an ordinary visitor** of the Portuguese site, in the app's built-in browser, non-essential cookies
  rejected, not signed in: `https://www.ikea.com/pt/pt/home-design/` → "Construa uma divisão" (room builder, 4 steps)
  → the 3D room editor, one product added and removed from view. Page text, the resource list the browser keeps
  (`performance` entries: URL, size) and the page's own globals were read.
- **Not done:** REA's browser capture and bundle analysis (Chrome with a debugging port) — the session's permission
  system refused it as a third-party target; REA's MCP registration also waits for the user's approval (see
  `especificacao.md` §10). No IKEA script, model, texture or image was downloaded or copied, and none goes into this
  repo. IKEA's terms of use apply to its site; we only need the patterns below, not its code.

## Observed — the user flow
1. Landing "IKEA Kreativ": three ways to start — **Início rápido** (pick a ready room, empty or furnished, each with
   its m²), **Personalizável / Construa uma divisão** (build a room), **Mais personalizado / Digitalize a divisão**
   (scan with the phone app).
2. Room builder, **"Passo 1 de 4 — Escolher uma forma de divisão"**: Retangular, Formato em L, Cortado, Formato em T,
   Formato em U, Biselado (thumbnails); "Pode editá-la no próximo passo".
3. **"Passo 2 de 4 — Editar dimensões da divisão"**: a plan view with a dimension on every wall (L shape default
   600 / 480 / 300 / 240 / 300 / 240 cm); "Clique e arraste cada parede"; a toggle **Layout da secção / Pé-direito**
   (drag the walls up or down for the height); units cm or feet; flip horizontal / vertical, rotate 90°; undo / redo.
4. **"Passo 3 de 4 — Configurar as características da divisão"**: door styles (painel individual, vidro, francesa
   dupla, painel duplo, dupla bifold, dupla de vidro) and window styles (individual, dupla); a selected element shows
   "Tamanho da porta (L x A) 90.0 x 200.0 cm", **Personalizar** and **Remover**; elements are moved along the wall.
   The view switches to a 3D isometric cut-away.
5. **"Passo 4 de 4 — Decore as paredes e o chão"**: wall colour swatches and floor styles ("Carvalho natural" …),
   applied live in the 3D view; button **"Planificar esta divisão"**.
6. **3D editor**: left panel tabs **Adicionar / Lista / Favoritos** (search, room type, categories, product cards with
   price and availability); top bar: project name, actions, **the running total** (0,00 € → 149,00 € on adding a
   149 € chest — at once) with **"Resumo →"**; a toast "O seu produto foi adicionado, mas pode querer movê-lo para um
   local melhor"; a standing note **"O preço final pode ser diferente"**; bottom bar: **Vista de cima**, **Vistas
   laterais**, move, paint, edit room; zoom + / −; the canvas class `cameraInOrbitMode` (orbit camera).
7. **Lista**: every product in the room with its price, "Mais opções", delete, "Adicionar tudo ao cesto de compras".

## Observed — the technology (public page facts)
- **three.js r160** (`window.__THREE__ = "160"`) on one **WebGL2** canvas.
- A web app built with webpack (`webpack-runtime-*.js`, `framework-*.js`, `app-*.js`, `page-data/app-data.json` — the
  Gatsby / React layout).
- **`/home-design/wasm/kreativ-core-sdk.wasm`** (≈ 115 kB transferred) — a core library compiled to WebAssembly.
- **Draco** geometry decoder (Google's, 1.4.3) → compressed glTF-style meshes; geometry `.bin` buffers, **`.webp`
  textures** and thumbnails from `catalog-processed-eu.storage.home-design.ikea.com/roomassets/<id>/LOW_RES/…`; an
  **HDR environment** (`gray.hdr`) for the lighting.
- An API host `api.home-design.ikea.com` (`…/ideas/sugarcube/api/status/`) and the site's shared price / cart
  scripts (`price-package-scripts`, shopping-cart agent).

## Inferred (not proved)
- The WebAssembly core is the room / geometry logic written once and shared by the website and the phone app (the
  same core on every platform) — the size and name suggest it; its contents were not inspected.
- Assets load **low resolution first** (`LOW_RES` paths), then better ones — fast first view.
- The 4-step builder writes a room description that the 3D editor then renders; the price comes from the product
  catalogue (each product carries its price), summed client-side.

## Unknown
- What the WASM core does exactly; how dimensions snap while dragging (the drag could not be exercised in the
  emulated pane); how projects are saved (sign-in required); the full API.

## What we take for DiscoverCasa (details in `especificacao.md`)
| Kreativ | DiscoverCasa configurator |
|---|---|
| Shape first (6 shapes), then dimensions | Shape first, then the m² of the foundation (user 2026-10-20) — right angles only |
| Drag walls, dimension on every wall, pé-direito toggle | Same plan view; sides adjusted after the m²; heights are ours (method) (superseded 2026-10-21, see registo: **the client chooses the pé direito with the total area**, the structure follows it — "A altura não temos fixa o cliente pode escolher a vontade o que preferir", `especificacao.md` §2) |
| Doors / windows from a style catalogue, size L × A, move along the wall | Our caixilharia catalogue (standard RAL 7016 …), sizes, moved along the wall; rules of the method checked live |
| Wall colour / floor | Exterior finish A / B / C, interior finishes, floors, caixilharia colour |
| Running total on top, "Resumo", "Lista" with a price per item | The same — the total always visible, the base first, each wall + / − (user) |
| "O preço final pode ser diferente" | Suggested: the same kind of note for the estimate |
| three.js + WebGL2, orbit camera, top / side views | The same (the user: "3D a rodar como o do IKEA") |
| Core logic in WebAssembly, shared | Our method engine (Python) in the browser through WebAssembly (Pyodide) — one source of the rules |
| Draco glTF, webp, low-res first, HDR light | Geometry generated from the engine (no catalogue models); textures for the finishes; the same light / compression ideas |

Sources: the pages above (visited 2026-10-20); press — IKEA Kreativ uses technology from Geomagical Labs (bought by
Ingka in 2020) and reached Portugal in April 2024 (furnituretoday.com, cxmtoday.com, echoboomer.pt).
