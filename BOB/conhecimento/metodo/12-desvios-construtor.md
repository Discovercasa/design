# Método DiscoverCasa — o que o construtor ainda assume ou faz diferente (§15, X1–X20) (parte de conhecimento/metodo-construtivo.md, v8.8; split from 10 in v8.8)

### What the builder still assumes or does differently from this rulebook
(Part of §15; the questions to the user are in `10-pontos-abertos.md`. Deviations X1–X20 are cited from 03, 04, 05, 06, 08, 10.)

**With the company's module drawing** (cfg `modulos_reais` → `modulos_dc.py`, [TV] v5 on) `casa_planta.py` takes the
modules as drawn and adds: the beams cut to the inner length (= the rule); "fantasma" parapet panels for the layers; the
plan wall each module matches (P01: the plan's 2,58 for M9, not the elevation's 2,61); the interior modules raised 1,3 cm to
2,543 with the 0,11 viga on top (D2503 2,53: conflict OPEN); the caixilharia of cfg `itens` (folga 0,025, box above,
profiles assumed, the warning only beyond 2 × folga + 1 cm — L41; none when much smaller — L37); the remates (§3, assumed
profiles, no thresholds); the chapéus at the actual corners; the [TV] pergola (v6.3 — §8, sections tentative, posts with no
base, no flashing at the ledger, tiles on the slats).
**Without real modules** (every new house):
- the split by `divisor_modulos.py` (= the rules; the remainder and margins by costs — delegated). Still assumed: interior
  up to 2,75; the smallest module 0,60; a door near another opening kept in one longer module ("a confirmar"); the kind
  window / door from the plan's swing, not the table; openings moved in from a corner post (warned); the stud layout inside
  a module from one end (D2503 lays them from the corner post / jambs);
- corners: X exterior walls through (a builder default, no per-corner choice) (§2, L26);
- exterior openings at the architect's size (cfg `aberturas`, fallback 2,20 doors, windows 1,00 / 1,75) — not from the
  table + clearance (§3);
- no escadas (JSON `estrutura.escadas` not read) (§2, L29);
- on every hidden roof the exterior module modelled in two parts (framed to the ring, a parapet part) (L30); the interior
  modules, the beams on the ring and the ceiling below it = the rules;
- on exposed roofs the exterior module from the clear height with afinação + amarração on top (assumed); the interior top
  piece named "Viga de afinação interior" except with lameladas (naming only);
- the clear height from cfg `niveis.pe_direito` (= the rule); from a plan the openings capped silently under the framing
  instead of raising the modules (X1);
- **exposed roofs from a configured house** (`para_construtor.py` → cfg `cobertura.tipo` "a_vista" with `forma`, `beirado`
  0,25, verge = beirado (was 0,12 until 2026-10-29 night), `inclinacao_pct` vs JSON 15 %; `casa_planta.py` `a_vista`; `motor.worker.js` "telhado"). Test houses
  (the caller's): L 97 m², U 175 m², rectangle 12 × 8, L_misto / U_misto, the surface audit (2 064 + 1 032 cases), the
  timber audit `--formas` and his U in misto (1 033 objects). Deviations (each to confirm or fix):
  - **X1** (E1, §3) The raise for the highest head is the rule since 2026-10-28 ("opção a"). Left: (a)
    `para_construtor`'s note says "a confirmar" and names the highest rough top, not the opening → name it (e.g. "janela de
    correr 4 folhas, parede S"); (b) `casa_planta` (from a plan) caps the opening silently (`min(z1, Hf − top plate −
    lintel)`) → the same lift; (c) the longer ceiling drop (≤ ≈ 0,34) not checked against the réguas; (d) the screen offers
    no alternative when one opening lifts the house.
  - **X2** (E2, §6) Glulam per rectangle when its **outline length** passes 8,0 (`telhado_estrutura.construir`, `sec = lam
    if vao > 8`) — the rule's limit is the free span (≈ outer − 0,22 → glulam from ≈ 7,78 free) — while the hidden-roof path
    puts glulam over the whole house (§6) — ours both; one rule wanted.
  - **X3** (E2 / E4) Fixed 2026-10-22: a prumo under 3 cm becomes a packing piece "Calço" (110×75) — nothing floats. Left
    (ours): levels from the 22×7,5, glulam zones packed up 2 cm, not a plane set per section.
  - **X4** (E10, §6) The header "Viga de bordadura" along a wing's open side = their way (2026-10-28), between the edge beams.
    Left (ours): (a) its section — 200×100 shallower than the 220 beams → ≥ their depth and ≥ the hanger; (b) end posts to
    the base, no module joint there (not modelled; the divider does not know them); (c) size per span past ≈ 4 m —
    engineer; (d) the hangers — one per beam end, not modelled or counted.
  - **X5** (E6, E9) An **edge beam "Viga de bordo"** 22×7,5 (0,075 wide since 2026-10-22, centred on the frame) on every
    wall the beams run along; the empena and the hip-end eave purlin stand on it — ours (E6 says the wall's amarração; [SB]
    beam 0 over the gable wall is the precedent).
  - **X6** (E9, §6 b) Fixed 2026-10-22: hip-end purlins on the beam lines, prumos ≤ 1,0.
  - **X7** (E10) The engine's L / T / U joins (§7): no rincão at an L's outer corner (E10's alternative); the half-width run
    into a hipped end; the squarish-body threshold 1 : 1,6 (ours); the gable **encosto** (a case the rulebook does not have —
    a 220×100 header, not a standard section, not sized; "Fachada Encosto" cladding; flashing 0,20); a wing wider than its
    body takes the beams under the crossing (2026-10-28); **misto on a U whose arm is the biggest rectangle** hips one arm,
    gables the other (told 2026-10-28: "Tranquilo depois se necessário removemos essa opção" — kept) — a U might rather
    take the bar as the body (ours).
  - **X8** (E10, L47) Closed 2026-10-22: one slope = one plane — one set of purlins and one panel run across coplanar faces.
  - **X9** (E4, §11) Each purlin line one piece per continuous stretch (the U's ≈ 18,5 m) — no joint at a stock length;
    purlins end skew-cut against the rincão / laró side (`ponta_obliqua`, 2026-10-29 night; square where the member ends
    before; fixed with estribos — not modelled or counted); purlins with the beams jointed over a prumo. Left: stock
    lengths, the estribos — ours (A2, A3).
  - **X10** (§7 larós / rincões) The member 110×75 on edge under the line (dropped at a rincão so both faces clear it), on
    prumos where it crosses the beams; members mitred at a meeting point (each side to the bisector, 2026-10-29 night); foot on the beams, free over the overhang (≈ 0,71 at
    0,50 — X19); a beam past a rincão's top; one prumo per place — ours (general practice also allows purlins mitred on a
    prumo); bias cuts and the caps' seat not detailed.
  - **X11** (E7, §11) Panels one object and one area per face; no 1,0-wide count × length per slope, no bias waste, no
    closures — the order unit missing. JSON Munditelha since 2026-10-22; `para_construtor` still passes `painel_espessura`
    0,08 for the heights while 0,04 + 0,045 = 0,085 — one value wanted (⚠ 2026-10-30 later still: his "usamos os de 80mm"
    — whether the Munditelha is 80 or 40: asked, 05).
  - **X12** (E5, §11) Ridge caps, rincão caps, verge trims, abutment flashings and gutters in metres, not counts.
  - **X13** (§7 larós) The caleira de laró a flat 0,50 strip at the purlin-top level — no channel, support or lift.
  - **X14** (E8) Gutter 125×90 on every eave ✓ but laid level, centred under the panel edge; since 2026-10-29 night one
    gutter per straight run, mitred at corners (L67; was each eave piece its own gutter — two separate runs at a 4-água
    corner or a laró foot).
  - **X15** (E8–E10) 2 downpipes per run, 0,30 from its ends (= E8; confirmed 2026-10-30, one on a small run ≤ 4,0 "sim está
    bem", more evenly between for 1 cm² per m² with the 80 × 80 pipe = 64 m² each — `camadas.cobertura_faces`, the builder to
    check it) → a 4-água rectangle gets 8, two ≈ 0,6 apart at each
    corner (E9: at the corners); at a laró foot two pipes 0,30 off the corner instead of one; a run under 1,0 m gets none;
    no check against openings; 0,10 out from the frame, from 0,05 above the base ✓; the swan-neck counted (+ 0,25
    m) not drawn; no brackets; outside the cladding (E8 OPEN). The screen draws the same pieces (2026-10-28). (The hidden
    roof's pipe is his 100 × 50, 2026-10-30 later still; the exposed pipe's 80 × 80 stays ours.)
  - **X16** (E11) `validar.py` checks geometry only (structure under the roof plane, layers outside the frame, covering on
    its supports; lets "Fachada Encosto" stand over the footprint) — "0 issues" missed X3 and L51's 160 clashes. The timber
    audit `auditar_cobertura.py` now covers clashes, bearings, prumos, slope coverage. Left: gutters / pipes per eave and
    laró foot, empenas framed and clad, the laró slope vs the panel, opening heads; neither tool runs by itself in the build
    (ours: add the audit to the configurator's test run).
  - **X17** (E4, E7) Beirado from the frame's outer face = JSON default; the beirado range 0,20–0,50 in the JSON, clamped
    by `para_construtor` and the screen (`main.js` `BEIRADO`, 2026-10-28 ✓); **the verge = the beirado in the configurator
    since 2026-10-29 night** (`para_construtor` "empena": beirado, L66); the JSON `cobertura.empena` 0,12 ([SB], ours)
    only for older models ([TV]).
  - **X18** Fixed 2026-10-22: `telhado.py`'s docstring says 15 %.
  - **X19** (E11, §13; 2026-10-28, ours) The timber audit's range: (a) tolerances looser than the rules (1,30 vs purlins ≤
    1,2 and prumos ≤ 1,0 — a 1,25 bay passes); (b) the sweep runs at 15 % / 0,25 and 40 % / 0,40, pé direito 2,50 — not
    the 0,20 / 0,50 beirado ends nor 2,40 with a raised module; (c) at the 0,50 maximum a misto rincão foot runs free
    ≈ 0,71, inside the audit's 0,75 (was ≈ 0,78 at 0,55) → run the sweep at 0,50 to confirm.
  - **X20** (§7 Hidden roof; 2026-10-28, ours — to check on a close-up) The one-água **remate de topo** rose 0,10 up the
    parapet's roof-side face (`camadas.cobertura_platibanda`); since 2026-10-30 later his detail has the folded sheet and
    the flashing ≈ 0,12 up the face ("room permitting under the chapéu", JSON `cobertura.remate_topo`) while the parapet
    stands `platibanda.folga` 0,05 over the plane's top (`casa_planta`: `z_plat` = `z_topo_max` + 0,05) → at the highest wall
    it may stand ≈ 7 cm past the parapet top, through the chapéu. Fix: stop it under the chapéu's inner leg (the leg lapping
    over it), or raise the parapet on one-água roofs (≈ 0,15 upstand — general practice).
- [SB] from the engineer's drawings: `estrutura_dc.py` (beams 0 → D on the amarração, purlins ≤ 1,2 tilted, the eave one on
  the beams, prumos on every beam, empenas, verges 0,12) + `camadas.cobertura` (rectangle only: gutter flat, downpipes 0,30
  from the ends at the eave line ≈ 0,25 off the frame running to Z 0 — the "ligeiramente acima" and the swan-neck missing).
**Other assumptions** (see the lines above): wall position default "face_interior" (D2503: "face_exterior", set per
project); bandeiras; réguas one per perfil; perfis 47×17; prumos 110×75; contra-ripado 30×20 at 0,35 from the façade end;
ripado at 0,35 centres from the bottom; corner / jamb verticals in both batten layers; no gaps where battens meet; Tremolo
end joints in line; exterior gutter 125×90 and 80 mm downpipes (exposed roofs); Munditelha 40 mm (thickness, core, skin;
colour RAL 8004 confirmed 2026-10-30; ⚠ "usamos os de 80mm" of 2026-10-30 later still: the hidden panel — whether also the Munditelha: asked); the verge = the beirado (configurator; JSON 0,12 for older models); purlins flat and tilted; no ridge beam (the top
purlins meet on the line, cut to the slope — the joint A1; purlins skew-cut to a hip / valley, A2); step 7: the pergola's top ≤ the ground floor's ceiling-beam top (his rule, our reading of "top") and slatted only, a separate building ≥ 2,00 m away (his, 2026-10-30 later; item 23) at the house's pé direito, a garage gate's top 0,30 under
the ceiling (his), an attached garage's wall an interior wall (items 22–23), interior walls only in an attached block (our reading, "parece-me bem" — his test pending); on 22×7,5 hidden roofs purlins flat at ≤ 1,2 and the v3
gutter box; on lameladas (only when cfg says so — no span rule) no board under the gutter lining, the lining "Chapa cor telha" (RAL 8004 assumed since 2026-10-30; was dark grey until 2026-10-29), the
outlet (a hole in the gutter's bottom since 2026-10-29, its bocal the pipe's own 100 × 50 section — his, 2026-10-30 later still — and a stub through the parapet — the holes the rule,
the type ours: E5; two downpipes per gutter, one on one ≤ 4,0 m — the 4,0 confirmed — more evenly between for 1 cm² per m² (100 × 50 ≈ 50 m²); the lining to the top only ≤ 0,50 over the panels, else a 0,10 lap behind the cladding: E4); the ridge
madres' 9 m trigger; downpipes 100 × 50 (hidden, his; commit 0528d1b) / 80 × 80 (exposed, ours), ≥ 0,10–0,15 clear of openings, 5 cm above the base, the local recess in cork / XPS only where the cavity is shallower (the engine warns and limits the pipe to the cavity where the visible boards would be cut), no overflow
or inspection point (the old 80 × the cavity pipe was too small for TV's outlets, §13 — superseded 2026-10-30); parapet `folga` 0,05 when `platibanda.topo` is not set (D2503 ≈
0,07); one chapéu piece per wall top, no joint strip or membrane; the gutter end cap to the top over the open gutter; wool 80
mm in parapets; OSB 15 + Traspir under every façade finish on the parapets' roof side (TV's list); the hidden roof's
form (one água up to a 15 m panel — his, 2026-10-30 later; a rectangle's default gutter side south — the client may choose, two slopes mid main block ≥ 1 m otherwise, the remate de
topo his folded sheet + metal flashing 0,12 up / 0,20 on the panels — sizes ours); floor wool on the ceiling below; the 5 %
slope fallback; `cobertura_manter` "inclinacao"; the ground-floor XPS + betonilha default; all waste factors; Pladur board
size; vinyl 5 mm; XPS boards 1250×600 and render 6 mm; the caixilharia folga 0,025 in height too (none under doors — ours;
2,5 cm and a bottom profile under the janelas de correr — OPEN); the shutter box filling what is left above the frame (not
the maker's height; windows only), profiles 6 / 5 cm, glass 24 mm, box 0,10 deep at the frame's outer face; the garage door
in the opening (sectional doors usually hang behind it); door panels in "Portão seccionado RAL 7016".
