# Configurador — the client's IKEA-style house builder (Product vision item 4)

Developed in its own session and git branch `configurador` (worktree `../BOB Claude - configurador`); brief
`conhecimento/sessao-implementacao.md`. Merge into `main` only with the user's OK, bringing `main` in first.

- `docs/especificacao.md` — **the spec**: what the user asked (verbatim), the client's steps, how the walls become
  modules, the price, the architecture, the plan, open questions. Start here.
- `docs/ikea-kreativ.md` — how IKEA Kreativ works (observed / inferred / unknown) and what we take from it.
- `exemplos/` — configured houses (generic, no client data), e.g. `casa_exemplo_L.json`; the engine code is in
  `ferramentas/configurador/` (`formas.py` shapes from the m², `para_construtor.py` → the builder's inputs).

Rules that matter here: the client never sees the word "módulo"; the build rules come only from
`conhecimento/metodo-construtivo.md` (index; rules in `conhecimento/metodo/`) and `ferramentas/modelo/sistema_construtivo.json` (the engine is the repo's
Python, run in the browser — never a copy of the rules); nothing goes online without the user's OK (client data);
prices are placeholders until the price list exists (Product vision 2).

Status (2026-10-20): spec v0.1 written; phase 1 done — the module divider `ferramentas/modelo/divisor_modulos.py`
(checked against TV D2503; the user's answers of 2026-10-20 night applied — remainder ours, exterior ≤ 3 m; spec §3, §7);
phase 2 done — the configured-house format and `para_construtor.py` (the example builds, validates with 0 issues and
gets its documents; spec §8); phase 3 built — the browser prototype `web/` (run: `npm run dev --prefix
configurador/web`, open http://localhost:5173; spec §9 — on another PC first a clone of the `configurador` branch), the
user's first try failed only because it ran on another PC outside the repo (2026-10-21); the user's feedback of
2026-10-21 applied — each base side typed or dragged (the panel keeps only the total area), roof beams inside against
the modules (never through them), continuous madres / roof purlins over an L; phase 4 built 2026-10-21 — the pé
direito in step 2, doors and windows, interior walls, finishes, saving (spec §11; the exposed roof and real prices
still to come); the user's review of phase 4 (2026-10-21, later — new step order, materials with images, free interior
walls, hide the roof) built the same day, with the exposed sandwich-panel roof (2 / 4 águas, L / T / U) in the engine
(`ferramentas/modelo/telhado.py`, `telhado_estrutura.py`) — spec §12; exposed-roof answers and open points spec §7 q.13.
2026-10-22: the rulebook check's fixes, the exposed roof's production documents (`--documentos`), one slope per plane,
the interior wood finish in its layers, Desfazer / Refazer — spec §12. 2026-10-22, later: the user's answers (estribo,
Munditelha, estore 20 cm → 2,40, exterior walls' inner faces) and review 2 (interior walls, rooms and floors, roofs,
sliding windows) — spec §13, built the same day (walls drawn by clicks with corners, rooms with m² and a floor each,
outside walls' inner faces, every shape × roof audited and fixed, 3 / 4-leaf sliding windows, the shutter box drawn).
2026-10-27: answers — L / T / U get "Duas águas" then "Várias águas" (sem / com empenas: the new roof type `misto`,
body hipped + wings' gables, our reading to confirm); doors never take an estore; the hanger question re-asked with a
sketch (`configurador/docs/juncao_ala_estribos.svg`) — spec §13.
2026-10-28: review 3 (his screenshots of a U) — the exposed roof's timber fixed (members through one another, purlins
with no prumo where a wider wing crosses its body; check every shape with `python ferramentas/configurador/
auditar_cobertura.py --formas`); only the roofs with gables offered; the roof drawn as the engine builds it (gutters,
downpipes, caps; the hidden roof's slopes and parapet height — worker `cobertura_casa`); hangers on the glulam header
and taller modules for the 2,40 head confirmed — spec §13.
2026-10-28, later: his "erros que não fazem sentido" fixed (roof gaps, downpipes, chapéus ≈ 2 cm, caps on the panels,
the façade finish on the parapets' roof side), hidden roofs in one água per house, beirado max 0,50, interior-wall and
step-6 fixes, the "Teto" toggle — spec §11, §12, §13.
2026-10-29: interior walls take doors only ("por norma ninguém usa janelas nas paredes interiores"); the client
chooses the hidden roof's gutter side where two sides are straight (`cobertura.lado_caleira`, step 5) — spec §8, §13.
2026-10-29, later (new cloud session; his screenshots stayed on the PC): "Oculta" on screen; hidden roof — one gutter
per low wall, outlets in its bottom, top flashing on the panels, parapet as wide as the chapéu; exposed roof — top
purlins meet on the ridge, prumos turned with their beam, empenas clear of the eave purlin; Munditelha colour; brand →
step 1; **step 7 Pérgolas, garagens e anexos** (`web/src/exteriores.js`, engine `ferramentas/modelo/pergola.py`) — spec
§2, §8, §11, §13. Run `python ferramentas/configurador/auditar_cobertura.py --formas` after every roof change.
2026-10-29, later still: step 4 — walls from the house's inner corners, rooms in the middle of the house (closing
snap), a wall's piece selected / removed, a real interior door, the camera kept between steps, the navigation pop-up —
spec §11, §12.
