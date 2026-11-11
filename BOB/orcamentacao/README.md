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
- Final price (hub tasks 42–44, 2026-11-11): the parcels the user listed (materials, caixilharia, foundation, labour,
  especialidades, installations and pre-installations, licensing, VAT) + a margin (not said by the user: to confirm) live
  in the Supabase table `orcamento_parcelas` (migration 0017: method, area basis, value; editors change them on the page,
  everyone with Design access sees them). The company's values never go into this public repo. Methods: € per m² of
  construction / implantation / opening area, % of materials, fixed value, % of the sum (margin), VAT rate. `compor()` in
  `public/js/orcamento.js` gives each parcel with its sum shown; a missing value keeps the price «incompleto».
- Areas: the Listagem CSV ends with «Dados da obra» lines (`AREA-IMPLANTACAO` from the foundation outline,
  `AREA-CONSTRUCAO` = that x floors); the openings' area is the sum of the caixilharia items. Editable on the page for one sum.
- What the user still has to give (values, VAT, missing Hub materials): hub task «Informação a dar ao Claude para o preço
  final» (Orçamentação, one note per item).
- Publish: `python BOB/ferramentas/construir_site.py --so orcamentacao` → `public/orcamentacao/` (with the login gate).
