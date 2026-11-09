# Registo das conversas (continuação, desde 2026-11-10) — what the user said, verbatim

Continues `registo-conversas.md`, which reached ~1 560 lines on 2026-11-09 (its entries run until that day). Same
rules: every message in which the user gives information, verbatim (typos included), dated, with what it answered and
where each fact was filed. Oldest first. Kept by the agent `guardiao-detalhes`. Grep both files for the user's exact
words (`registo-conversas*.md`). When this file passes about 1 500 lines, continue in `registo-conversas-2026-4.md`
(or `<year>-<n>`) and link it here.

### 2026-11-09 — AR test on the phone: three bugs [Torres Vedras, Sobral]
> ok há alguns bugs :
>
> 1. dentro da casa tem paredes que estão abertas e o testo nota-se algumas linhas, principalmente nas portas não estão fechadas, da para ver o interior das paredes.
> 2. Da parte de fora na pérgola tem falhas visuais nas vigas superiores e dá para ver um gap enorme entre o teto e o telhado.
> 3. O nosso revestimento exterior o tremolo não tem o aspeto da textura de madeira que usaste, é um tremolo vertical mais fino e mais claro que o que usaste podes rever na fotos penso que tenhas acesso, se não tiveres diz-me que eu mando-te uma foto do aspeto do nosso tremolo
- Context: feedback after testing the AR models from the hub on a phone (hub tasks 84, 157).
- Filed in: `step-inside/docs/fase7/README.md` → bugs 1-3, causes and fixes (version 2 of the 8 AR files);
  `conhecimento/sistema-construtivo.md` → finish option A, "Look of the real Tremolo" (vertical, finer, lighter;
  photo pending); bugs 1-2 are AR-export issues (openings lined, pergola timber visible), no method change.
- Pending: the user's photo of the real Tremolo (look, board width, colour) — replaces the provisional #8E6A48.
  (closed 2026-11-09, see the next entry)

### 2026-11-09 — Photo of the built Torres Vedras house: colour, AR gaps bug, flat plasterboard [Torres Vedras]
> esta é na realidade a casa de torres vedras, e tinha-me esquecido de mencionar um ponto, havia pequenos gaps no tremolo e conseguia-se ver o interior através desses pequenos gaps
> o gesso cartonado do interior é plano não tem relevo nem imperfeições
- Context: sent with a photo of the built house (marketing photo, garden side; not stored in Git), after the AR
  test entry above (bug 3, Tremolo look). The "gaps" sentence is one more AR bug ("tinha-me esquecido de mencionar um
  ponto"): gaps between the cladding pieces of the 3D model showed the interior once the membrane was removed in the
  AR. Not a statement about the real façade (Piveteau 22×135 tongue and groove stands). Fix: the membrane behind the
  cladding stays visible in the AR, so the gaps between model pieces no longer show the interior.
- Filed in: `Construção Torres Vedras/docs/estado.md` → "As-built look: photo of the built house" (colours, pergola,
  surroundings, reference for task 158); `conhecimento/sistema-construtivo.md` → §2 finish A (colour from the photo,
  note that the gaps were an AR bug) and §4 item 3 (smooth plasterboard);
  `step-inside/docs/fase7/README.md` → AR version 3 (done by the caller).
- Pending: the user approves or comments on AR version 3 (phone, next to the photo).

