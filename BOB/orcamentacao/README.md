# Orçamentação

The price side of DiscoverCasa's applications (hub project `orcamentacao`; owner of prices in the app hierarchy).

| Path | What |
|---|---|
| `ligacoes.json` | each stable product code of the Listagem de material → the material of the Hub's price list (id only), the price unit and how the line's quantity becomes it; `hub: null` = not in the Hub list, with the reason |
| `web/` | the page `/orcamentacao/`: drop the Listagem CSV from the Gerador (or use Torres Vedras) → cost of the materials, line by line, and the table of links for the team to confirm |
| `tests/` | `python -m unittest discover -s orcamentacao/tests` (from `BOB/`): every code linked or explained, every line of the reference houses with a code, a configured house lists only the chosen facade |

- The codes are given by the engine: `ferramentas/documentos/codigos.py` (CSV column `codigo`). A new layer or product
  needs a rule there and an entry here, or the tests fail.
- The calculation is shared: `public/js/orcamento.js` (the Build Your House and the Gerador can use it later), reading
  the Hub tables through `public/js/materiais.js` with the Design session. Prices are never stored in the repo (public).
- Price rule (2026-11-11, Claude's proposal): among the Hub prices in the link's unit, each supplier's latest (the Hub keeps
  older prices of the same supplier as rows of their own), then the cheapest with discount.
- Not yet: labour, foundation, especialidades, installations, licensing, margin and the house's VAT (hub tasks 42, 43).
- Publish: `python BOB/ferramentas/construir_site.py --so orcamentacao` → `public/orcamentacao/` (with the login gate).
