# Método DiscoverCasa — pisos entre andares, tetos e pavimentos (§5, §6, §10) (parte de conhecimento/metodo-construtivo.md, v8.3)

## 5. Floor between storeys
- **Two storeys: the wall modules are built the same way on both storeys** — user 2026-10-20 (night) "emtermos de paredes
  nada muda e o segundo piso eu já expliquei no outro chat como era composto o segundo piso" — confirmed —
  `estrutura_dc.py`; the builder from a plan and the configurator: single storey first ("começamos com térreas e depois
  avançamos para dois pisos", 2026-10-20). Module heights per storey: PO Q5 (Casa CL 2,97 / 3,52 reference).
- Joists 220×75 solid, on edge, wall to wall, **≤ 0,615 m** apart (equal division; 3_Vigamento 0,614 over 4,90,
  continuous over an interior wall) — user 2026-10-09 "Floor joists is also 22x7,5"; 3_Vigamento (2026-10-15 "representa
  bem o nosso vigamento base") — confirmed + company document — JSON `estrutura.pavimento.vigas.espacamento` 0,615.
- Closer joists: **0,50** where they span ≈ 4,8 m free; **0,466** beside the stair — 3_Vigamento — company document — not
  in the tools ([SB] living room ≈ 4,7 m at 0,61 marginal: 0,50 asked, SB #6).
- No main or central beam: the normal joisting also over big rooms — user 2026-10-15 "leva o teto falso e o vigamento
  normal de 22x7,5 e 11x7,5 nada muda" — confirmed — JSON `estrutura.pavimento.vigas_principais` false (L11).
- Sometimes glulam joists, sometimes à vista — user 2026-10-09 "Sometimes on the floor joist we use vigas lameladas which
  some times can be à vista" — confirmed (when: OPEN — **PO Q10**) — not in the tools.
- Barrotes 110×75 flat on the joists, perpendicular, **0,60 centre to centre** — user 2026-10-09 "put the 11x7,5 at 60
  cm"; 2026-10-13 "sao medidos em eixo" — confirmed — JSON `estrutura.pavimento.barrotes`.
- Mineral wool 100 mm between the joists — user 2026-10-09 "The insulation is 100 mm mineral wool"; 2026-10-13 "fica entre
  as vigas" — confirmed (laid on the ceiling below — assumed) — JSON `tetos.la_pavimento`.
- OSB 22 deck, then vinyl — user 2026-10-09 "with then OSB 22 and then the vinyl" — confirmed — JSON
  `estrutura.pavimento.osb`, `pavimentos.acabamento`.
- No rim joist (viga de bordadura) across the joist ends at the façades — user 2026-10-15 "não" — confirmed —
  `estrutura_dc.py`. What closes the joist bays there: OPEN.
- Stair opening: a trimmer across the joists + short joists at 0,466 to the wall (3_Vigamento "ZONA ESCADAS" 3,478 ×
  2,605) — company document — partly in `estrutura_dc.py` (trimmers + header, not 0,466).
- The extra floor depth goes up: everything above rises, clear heights stay — user 2026-10-09 "yeah no problem raise the
  roof" — confirmed — `estrutura_dc.py`.
- Floor over an open porch = an exterior floor (insulation, airtightness, closed ventilated soffit with insect mesh) —
  general practice (SC §2a ⚠5). Porch: glulam 200×100 beam (6,00) on glulam pillars 200×100 (2,52 high) — 3_Vigamento,
  company document; steel post bases keeping end grain off the slab — general practice. Not in the tools.

## 6. Ceilings (tetos)
- **Top floor: a flat false ceiling at the height of the viga de amarração; it does not follow the roof** — user 2026-09-30
  "has a fake roof at the height of the viga de amarração" — confirmed — `estrutura_dc.py`, `casa_planta.py`,
  `camadas.tetos`. **It comes with every roof, hidden or exposed** (never a separate option) — user 2026-10-22 "Quando se
  aplica a cobertura automaticamente o teto falso já entra também" — confirmed / assumed (flat under exposed roofs too, no
  vaulted ceiling; PO Q9 "teto falso em toda a casa"). [cfgr] **It must show**: a "Teto" toggle draws it from the engine
  (`camadas.tetos`, the Pladur underside at the pé direito) — user 2026-10-28 "O testo falso ainda não aparece no builder
  e quero que isso seja possível de aparecer" — confirmed (L48).
- **Vigas de apoio ao teto 220×75 casquinha branca, 1 m apart** (3_Vigamento 0,989 = equal division), **always down the
  slope** ("sempre inseridos no sentido da cobertura"), eave wall to eave wall, on the amarração and the interior viga de
  amarração; on a hidden roof between the exterior modules' inner faces (§4); **free span up to 8 m** (§13) — user
  2026-09-30; 2026-10-09 "spacing is 1 meter"; 2026-10-15 "O nosso limite é precisamente 8 metros" — confirmed — JSON
  `estrutura.vigas_teto`; cfg `cobertura.vigas_teto` (zones). Beams, glulam zones, exposed ceilings per house: **PO Q9**.
- **"Down the slope" on a roof with more than two águas** (exposed roofs) — ours (our reading of "always down the slope";
  to confirm with a sketch, §15) — `telhado_estrutura.construir`, `telhado.py` ("zonas"); checked by
  `ferramentas/configurador/auditar_cobertura.py` (E11):
  (a) **L / T / U with 2 águas per wing** (the "Duas águas" card, the wings of `misto`): each wing's beams across its own
  width, perpendicular to its ridge — the beams turn 90° from wing to wing;
  (b) **hip end** (4-água ends, the `misto` body's ends): the beams keep the main direction; the hip end's purlins run
  parallel to the beams, each purlin line on one beam, on short prumos at ≤ 1,0 along it (or on a trimmer);
  (c) **under a wing wider than its body's depth, where the wing's roof crosses the body, the beams run down the WING's
  slopes** (a header on the open side, below) — 2026-10-28 (his U: the bar's beams had stayed, 3 m of purlin bare, L51);
  (d) **wherever purlins run with the beams below** (a hip end, a narrower wing's end over its body, a crossed body's
  slope) they lie on the beam lines on prumos ≤ 1,0 along the beam, joints over a prumo, and **a beam is added right under
  the top purlin of such a slope**, the bays either side equal and ≤ the spacing;
  (e) **a beam beside an edge beam carries no second purlin**.
- **Where a wing opens into the body, the body's beam ends bear in external-flange joist hangers ("estribo de asa
  externa")** (galvanised U seat with outward perforated flanges, e.g. Esteba "estribo alas exteriores tipo B" — his
  photo) — user 2026-10-22 "…normalmente nós utilizamos um estribo de asa externa que é neste caso onde as vigas da
  cobertura realizam a sua descarga" — confirmed — **fixed to a header along the open side, wall to wall** — user
  2026-10-28 "Prendem-se as vigas laranja" (the sketch `configurador/docs/juncao_ala_estribos.svg`, its orange glulam "viga
  de bordadura") — confirmed — `telhado_estrutura.construir` (`cabecas`, "Viga de bordadura", between the edge beams on
  the side walls). **Ours** (not said): its section — the engine's standard glulam 200×100 (JSON `estrutura.lameladas`) is
  ⚠ shallower than the 22×7,5 (220) it carries → at least the beams' depth and ≥ the hanger height; its bearings — each end
  a point load: posts under it to the base, no module joint there, never through the module; its size per span — past ≈ 4
  m of opening the engineer (X4, §13). He asked why ("Porque razão? Explica-me melhor por favor", 2026-10-28) → explained
  the same day (a header shallower than its beams cannot take the hangers' full height; each end carries half the
  opening's roof); his reply OPEN; the rule stays ours (the engineer's per house). Hangers (general practice, CM §6): every hole fixed with the maker's nails / screws,
  seat as wide as the beam (75 / 100), height ≥ ≈ 0,6 × the beam, galvanised. Hangers and end posts not modelled or counted
  (X4). ⚠ The sketch labels the beams "a cada ≈ 0,60 m" — the rule is 1 m: fix if reused.
- **Past 8 m: glulam lameladas 20×10** (200 deep × 100 wide), down the slope, between the exterior modules' inner faces
  on the ring (§4), **in equal bays ≤ 0,92 between the end walls' axes** ([TV] 19 × 0,915 over 17,39; 11 × 8,50 + 7 × 11,00
  nominal, 8,28 / 10,78 inner, cut to fit) — D2503 sheet 1 (revision C "Cobertura - Vigas de 16x8 para 20x10"; labels still
  "16x8", TV #11) — company document (one house) — JSON `estrutura.lameladas`; cfg `cobertura.estrutura` "lameladas"
  (from a plan the builder does not choose glulam by span itself). They bear on the interior modules they cross (§4).
- **One beam system for the whole house once any span passes 8 m** — [cfgr] `para_construtor.py` (`LIMITE_VIGAS` 8,0;
  the U 11,60 × 18,50: lameladas 6,35 over the middle too) — assumed (ours; [TV] every span > 8 m, so D2503 does not show a
  mix) — to ask (cost). Exposed roofs choose per rectangle instead — X2.
- **On every hidden roof the false ceiling hangs below the amarração ring, from the ceiling beams by the perfis de teto and
  the calhas (réguas) de suspensão** — user 2026-10-21 "Sim como já te tinha explicado nos chats anteriores os tetos
  falsos ficam presos as vigas de 22x7,5 através dos perfis de teto e das calhas de suspensão que até cheguei a mandar foto
  delas" — confirmed / assumed (the drop: ring 0,11 + 8,5 mm = suspension 0,1185, ceiling ≈ 0,148 under the beams, as TV)
  — `camadas.teto_sob_anel` (every hidden roof; used by `casa_planta.main`, `camadas.gerar`, `motor.worker.js`),
  `para_construtor.py` 0,1185, TV cfg. JSON `tetos.suspensao.folga` stays 0,027 (exposed roofs). [TV] ceiling at 2,50 ≈
  0,15 under the lameladas; OSB 15 up to the ring (2,543), Pladur to the ceiling — D2503.
- **Réguas de suspensão (= calhas de suspensão) fixed upright to the side of each ceiling beam (or floor joist) hold the
  perfis** — user 2026-10-09 "are placed vertically onto the vigas de apoio ao teto and hold the fake roof" — confirmed (one
  per perfil per beam, 30 wide — assumed; photos `fontes/produtos-teto/2_regua_suspensao_teto_falso.png`, SC §5) — JSON
  `tetos.suspensao`. The gap: 0,027 under exposed roofs, 0,1185 under hidden ones, and on an exposed roof raised for a
  high head 0,027 + the raise (≈ 0,19 / ≈ 0,34, §3) → the régua's length must reach it (model and length OPEN) — not
  checked in the tools.
- Perfis de teto in steel at 0,40 — confirmed (steel) / assumed (≈ 47×17, spacing, bar length) — JSON `tetos.perfis`.
- **Cantoneira 30×30×0,5 steel screwed round the perimeter of every room, bars of 3 m** (e.g. Pertecno, Leroy Merlin
  15953000) — user 2026-10-09 "it has a fixed 3 meter of lenght so we gotta make calculation" — confirmed — JSON
  `tetos.cantoneira`.
- Ceiling metal is steel — user 2026-10-09 "steel those are the ones we use" — confirmed — JSON "Aço galvanizado".
- Perforated angle only on "hard corners" (outside corners) — user 2026-10-09 "only on hard corners" — confirmed (what it
  does: OPEN) — not in the tools.
- Pladur N 13 below (H1 in wet rooms, F near heat; wood possible) — user 2026-09-24 — confirmed — JSON `tetos.acabamento`
  (H1 / F not assigned to rooms).
- Wool on the top-floor ceiling: **100 mm Volcalis** on the false ceiling between the beams (cold attic) — user 2026-10-09
  "we use 100mm mineral wool volcalis on the roofs aswell" — confirmed — JSON `tetos.la`. Vapour control under it and a
  ventilated attic — general practice (SB #16).
- Every part of a room's ceiling gets Pladur and wool, thin strips included (only no perfis) — user 2026-10-15 "tem um gap
  no meio da sala" — confirmed — `camadas.tetos` (`fino`) (L4).
- Wall linings go up to the ceiling: Pladur to the false ceiling, OSB 15 to the beams (or the ring) — confirmed (L10) —
  `camadas.py`.
- Exposed ceilings (vigamento à vista): glulam 200×100 at 1,02 (3_Vigamento) — company document — not in the tools; the
  build-up over them: OPEN.

## 10. Floors (pavimentos)
- **Finish usually vinyl planks, chosen per room** — user 2026-09-24; 2026-10-22 "a pessoa pode aplicar pavimento que
  desejar na divisão que desejar e não ter que aplicar ou cerâmico ou vinil na casa toda como está de momento" — confirmed
  — **PO Q20** (default vinyl everywhere) — JSON `pavimentos.acabamento` (5 mm assumed),
  `pavimentos.acabamento_opcoes.ceramico_pav` (mosaico 60×60, 10 mm glued, waste 10 % — assumed, "a definir"); [cfgr] rooms
  found between the walls' finished faces, house file `pavimentos` [{ponto, acabamento}] → `camadas.pavimentos` (one
  collection per finish, levelled to one finished floor).
- Ground floor: vinyl straight on the base (§1); upper floor: vinyl on the OSB 22 (§5) — confirmed.
- Ceramics in kitchens and WCs — company website, not said by the user — assumed.
- At a change of floor between rooms (vinyl 5 / ceramic 10 + glue) a transition profile and the build-ups levelled —
  general practice — not in the tools.
