# Technical review — Torres Vedras

Issues, risks and deviations from the drawings or good practice. The house is built: most points are checks for the
comparison and lessons for the company standard (`conhecimento/sistema-construtivo.md`). Item numbers are fixed (other
docs cite them). Condensed 2026-10-28 — current state only; the reasoning chains are in the git history; the user's
words in `conhecimento/registo-conversas.md`.

**#1 Architect's spec (P1) vs the DiscoverCasa method** — DECIDED · OPEN (certificate)
"nós usamos o nosso método construtivo sempre portanto segue o nosso" (2026-10-15). P1: ripado + caixa de ar +
isolamento térmico + OSB3 + lã de rocha 60; roof on steel "madres ómega"; slab on void formers. Built: OSB 9, Traspir,
Volcalis 80, OSB 15, Pladur; roof on DiscoverCasa timber; floor on the DiscoverCasa base. → The REH calculation, the
energy certificate (SCE) and the telas finais must describe what was built: check which build-up they used (not asked);
for new houses give our build-ups to the engineers from the start (Sobral #26).

**#2 Direction of the Tremolo** — CLOSED 2026-10-15
"Tremolo fica na vertical como é o nosso padrão e o ripado na horizontal". If the licensed elevations draw horizontal
boards, the telas finais should show the vertical Tremolo (with #1).

**#3 Battens 37,5×35 without contra-ripado** — OPEN (suggestions)
As built: horizontal battens 37,5×35 (≈ 36 × 35 after the saw cut) every 35 cm from the bottom, straight on the
membrane, no contra-ripado ("Nesta casa só levou ripado na horizontal e não levou o contra-ripado"), battens round every
opening and at every corner. ⚠ Horizontal rows closed at corners and openings leave each cavity bay closed on all sides
(air cannot rise, water rests on the batten tops) — departs from his own 2026-09-24 rule "slatted against slatted … so
the zone between tgem is a breathable zone" → for new houses the contra-ripado (or battens gapped every ≈ 1,5–2 m),
10–20 mm gaps where horizontal battens meet vertical ones and at head / sill batten ends, insect mesh at bottom and top;
battens use class 3 — autoclave-treated, the ripped faces treated; Tremolo end joints staggered or on a doubled batten.
For this house: check the cavity is open at the bottom and top; look behind a removable board after a wet winter. Not
said: when the contra-ripado is used, 35 cm centres or clear, the battens' treatment.

**#4 Hidden roof behind a timber parapet** — CLOSED (gutter type, heights, fall) · OPEN (b)–(e), (g)
Decided (user): two slopes; the gutter inside the parapet ("sim é por dentro"); the same height on every side; rufo
(chapéu) corners closed; parapets clad on the roof side (2026-10-15); gutter walls lined up to the chapéu (2026-10-20,
#15); skylights not built (#10). D2503: calços with a fall ≈ 2 % to outlets at the ends; parapet ≈ 7 cm above the panels
at the ridge (≈ 3 cm above the ridge cap), ≈ 0,30 at the gutters. Site photos 2026-10-19: an OSB box lined with a red
sheet, corners and the bottom outlet sealed, **no overflow**. Open suggestions: (b) a self-adhesive membrane over the
parapet top under the chapéu (Traspir is W1, 3 months UV — not a roof membrane); one-piece corners or butt joints over a
joint strip (no laps — the chapéus never overlap, #13); (c) low sides in shingle order, profile closures (tapa-ondas)
under the 5-rib panel; (d) near the ridge the gable abutment flashing has only ≈ 7 cm → lap it up under the chapéu's
inner leg, Tremolo ≈ 50 mm clear of the panel with sealed end grain; (e) the wool in the parapet frame is outside the
heated volume — no thermal role, could be left out; (g) **an overflow (ladrão)** through the parapet near each outlet and
at the high end, lower than the madre-side rim (only ≈ 4–5 cm above the bottom; wing 0,06) — a blocked outlet otherwise
floods the roof void over the ceiling unseen. Asked 2026-10-20 night: "explica-me o que é um ladrao mas penso que não"
— explained and recommended; his answer after it: pending.

**#5 Floor level vs the deck** — OPEN (not asked)
Inside floor 117,50, deck 117,48; with vinyl on the DiscoverCasa base the bottom plates sit ≈ at deck level vs the rule
lowest timber ≥ 150 mm above the outside ground (splash, termites). How it was solved (base raised, a drained gap /
grating, DPC, treated plates): to cover when the base is taught. The floor-level thresholds are the most exposed joints
(#23).

**#6 Ceiling beams over sala + cozinha; interior bearing; the ring** — DECIDED · OPEN (suggestions)
Decided (user): "O nosso limite é precisamente 8 metros" (22×7,5 at 1 m); past it glulam — TV has lameladas 20×10 at
0,915 (8,50 / 11,00, D2503 rev. C "Vigas de 16x8 para 20x10"); "Por norma as vigas de apoio ao teto apoiam-se nas paredes
dos módulos interiores também" (2026-10-19); interior modules "à medida certa das vigas amarração", no packing (2,543 +
0,11 = 2,653); the base laser-checked ("exatamente como sugeriste", 2026-10-20 — (f) closed); beams end inside against the
modules (2026-10-21). Rough checks (ours): 22×7,5 at 1 m over 8 m — bending ≈ 0,96 f_m,d, w_fin ≈ L/98 vs L/250 (the
model v1–v3 case); glulam 20×10 over ≈ 8,2 m clear — bending ≈ 0,7 f_m,d, w_fin ≈ 45 mm from G (L/180), ≈ 73 mm with Q
(L/112) → with the ridge at mid-span the slope near the gutters falls from 6 % to ≈ 4 % in time. Open: ⚠ D2503 draws the
interior modules **2,53** (studs 2,46, cut list 109 × 2,46) vs the rule's 2,543 — 13 mm short or done on site (low
priority; D2503 also gives 3,50 vs 3,4915); (b) the interior walls are load-bearing: ≈ 5–8 kN design per lamelada, one
75×35 stud 2,46 high takes ≈ 9 kN in buckling → the afinação spreads it; joint the afinação only over a stud, away from a
lamelada; (c) a short end span can lift off → hold-down there; (d) these interior walls cannot be removed later; (e) the
long-term sag over sala + cozinha (deeper glulam, e.g. 24×10, or closer beams past ≈ 7 m; engineer per house); each beam
end bears only on the 75 mm ring → the ring's screws carry the reaction (≈ 4–5 kN per end) → engineer check of the ledger
fixing per house.

**#7 House height and footprint vs the licence** — DECIDED · OPEN (licence check, suggestion)
As built (D2503): walls to Z 3,4915 all round (≈ +0,39 over the elevations' ≈ 3,10; parapet ≈ 121,0 vs ≈ 120,6); clear
height 2,50 (licensed 2,60; RGEU 2,40 — fine); the modules' outer face on the architect's outer line with the cladding
≈ 9 cm outside → the footprint ≈ 0,18 m larger each way (≈ 5 m² of implantação). The user: "sim isso é natural e também
não tem qualquer tipo de problema"; "eu sei que isto altera a altura total da casa mas não tem mal". → The telas finais
must show all three; for new houses give the architect our top-of-wall build-up from the start (with #1).

**#8 Roof slope** — CLOSED 2026-10-16 · OPEN (panel)
Built at 6 % (D2503; the architect's section showed 1,3 %); the principle "o mínimo que é permitido … se a cumeeira tiver
de subir pode subir". 6 % is above Masterpanel's 5 % but below the 4° (≈ 7 %) some makers (Kingspan KS1000 RW,
Europanels) give for single-length trapezoidal panels, and creep (#6) brings it to ≈ 4 % near the gutters → the maker of
the panel used: to ask.

**#9 Downpipes** — DECIDED · OPEN (outlet type, section, foot)
Method (user): inside the exterior cladding, hidden by the Tremolo, never in rooms ("é suposto estarem por dentro do
revestimento exterior mas escondidos pelo tremolo"); the end slightly above the base ("tem de estar ligeiramente acima
para a água poder sair"; model 5 cm); "a forma como modelaste no blender por dentro do revestimento é a forma correta"
(2026-10-20). **TV as built: outside the cladding** (finished photos — SE and NE corners with box heads, the face beside
the garage), "nós achamos que por dentro é mais correto e fica melhor"; the gutter outlet a round hole in the bottom near
the end (photo 2026-10-19). Model v6.4: an outlet hole in the lining at each downpipe ("nas caleiras nao existem os
buracos par agua escoar" — fixed), a side outlet through the parapet into the cavity. Open: the outlet type and bocal —
promised ("isso depois eu digo"); the section — the 80 × 35 cavity pipe (≈ 26 cm²) is small for ≈ 37 m² per pipe (north
gutter) and ≈ 45–46 m² (P01 east, P03 west) at ≈ 1 cm² per m² → a local recess for a ø80 / 100×50 or two pipes; sealed
or jointless; a sealed sleeve through the parapet, the Traspir taped round it, studs clear of it; a leaf guard and a
cleaning access; the foot — a shoe onto a splash block / gravel strip falling away, or a gully (never onto the sole plate
zone); the overflow (#4 (g)); the pipe stubs and the "ladders" of battens in the site photo; how TV's bottom outlet
reached the outside box heads (optional).

**#10 Skylights not built** — CLOSED 2026-10-16 · OPEN (telas finais)
"Não foram construidas podes não incluir as claraboias". The telas finais should drop them; if one was a room's only
daylight / ventilation, re-check that room (RGEU).

**#11 D2503 labels** — CLOSED (ridge madres) · OPEN ("16x8")
Ridge madres over the wing **22×7,5** ("então é como estão no desenho com 22x7,5" — the label right, the drawing's 0,11
height not); why 22 there: not said (promise (7)). Sheet 1 still labels the lameladas "16x8" after revision C — confirm
what was built (20x10) for the materials comparison.

**#12 Lameladas cut from stock with large waste** — OPEN (suggestion)
D2503: 8,50 from 13,5 m stock (5 m × 11 ≈ 1,1 m³ of glulam wasted), 11,00 from 12 m (1 m × 7). They are cut to fit each
house ("Sim normalmente cortamos para "encaixar""), real pieces ≈ 8,28 / 10,78 → order to length, or a 17 m stock in two
(2 × 8,28 = 16,56).

**#13 Chapéus (parapet copings)** — CLOSED (flat) · DECIDED (full cover, no overlaps) · PENDING (what goes under)
"Os Rufos da platibanda na realidade nós chamamos de Chapéus"; legs ≈ 2–3 cm both faces; flat ("Como está feito no
modelo mais recente, está ótimo"); "não podem deixar o topo destapado" and "não dão overlap uns aos outros" — at a corner
one covers, the other butts (v6.2). In the finished photos they look continuous (tight butt joints of the same colour —
a 17,5 m wall cannot be one sheet). **Pending: "Por baixo dos chapéus lembra-me mais tarde para te confirmar o que leva"
— remind him.** Suggestions: a 1–2 cm fall to the roof, legs kicked into a drip ≈ 10 mm off the face, a membrane over the
top, a 10–20 mm vent gap with insect mesh at the cavity top under the outer leg; butt joints over a joint strip with a
small movement gap (dark aluminium ≈ 5–6 mm on a 3 m piece).

**#14 Battens round the openings** — CLOSED 2026-10-16 · OPEN (suggestions)
Windows not to the floor: above and below; openings to the floor: jambs + head; a vertical batten at every exterior
corner both faces. The head batten holds the cavity water → gaps at its ends (#3) and a head flashing with a drip over
every window and door head.

**#15 Roof side of the parapets** — CLOSED 2026-10-20 · OPEN (gable face over the gutter, junctions)
Gutter walls (P01 / P03 / P11): "revestimento da caleira até ao topo que depois se encontra com os chapéus da platibanda".
Gable parapets: clad on the roof side (2026-10-15: "lã mineral, osb 15, membrana transpir, ripado horizontal e tremolo
vertical" — TV's façade is Tremolo) "até ao final do painel sanduiche" (2026-10-19). By analogy (ours): the gutter's end
plate on a gable face over the open gutter lined to the top (model v6.1). Junctions: the chapéu's inner leg over the
lining's top edge, a trim where the cladding meets the gutter's end plate, the Tremolo foot ≈ 50 mm clear with sealed end
grain.

**#16 Cladding past the foundation edge** — OPEN (suggestions)
The cladding stands ≈ 9 cm outside the base edge: the cavity bottom open over the ground (insect / rodent mesh), the
Tremolo foot and bottom battens the most splashed timber (≥ ≈ 150 mm above ground — #5), the Traspir lapped down over
the base edge (seen in the 2026-10-19 photo), an inspection strip where termite tubes would show. The downpipes end
there too (#9).

**#17 11×7,5 lintel over the 3,00 garage door** — CLOSED 2026-10-19 · OPEN (suggestions)
"exatamente neste caso o nosso engenheiro confirmou que poderia ser a de 11x7,5 mas por norma é 22x7,5". Rough check
(ours): alone ≈ 2,5–3,5× over its bending strength under ≈ 3 lameladas — it works as part of the ≈ 1,2 m sheathed frame
above (header action). Keep the engineer's note and its conditions (OSB fixings, the ring unjointed over the opening, the
door's deflection limit) on file; whether it also covered the 2,00 janelas de correr on P03 / P01 (11×7,5 under ≈ 2
lameladas each): not said.

**#18 Two membranes on the walls** — OPEN (not asked)
HOLZ TECHNIC printed "TRASPIR HOUSE 95", "CE EN 13859-1/2" on the walls (a Traspir-family 95 g/m² membrane under a
distributor's logo — ours); rothoblaas on the top band. Confirm the data sheet (Sd, W1, UV time), why the top band
differs, the laps between them (≥ 20 cm, compatible tape).

**#19 Ceiling beams and the exterior modules** — DECIDED 2026-10-21 · OPEN (notch form)
"essas vigas ficam por dentro e encostadas as da estrutura não atravessam … não é realista"; "quanto muito é feito o
entalhe nas vigas … sem atravessar a estrutura do módulo" → lameladas end inside against the modules' inner face, on the
ring; D2503 Módulos' whole studs are right; our 2026-10-19 reading (a notch in the module) and its suggestions (a), (b)
are moot. Left: the notch's form (low priority; a notch on the underside at the support weakens shear); the ring's fixing
(#6). Model v6.5 to rebuild.

**#20 Approved openings table vs the D2503 rough openings** — ANSWERED · OPEN (his reply, under a door, WC glass)
Table "PROJETO APROVADO" (`revisao-modelo/2026-10-19_projeto_aprovado_vaos.png`, per module in `materiais.md`). Answers:
the basculantes as modelled ("está ótimo como fizeste" — 0,73 in D2503's 0,75); the entrance M5 "uma porta maior e mais
robusta que cabe naquele espaço" (fills 1,04); M23 "a encher o vão como na principal" (fills 0,94); the table = "apenas a
medida do caixilho sem folga" ("acho que"); clearance 2,5 cm each side and in height by default ("depende do caixilho",
"nem sempre"). ⚠ With 2,5 cm the table fits D2503's openings only for the doors in width: janelas de correr 2,00, vidro
fixo 1,50, garage 3,00 equal their openings; basculantes 0,80 are 5 cm over 0,75 × 0,75 (M6, M18) or wider than 0,75
(M24); the 2,20 doors and garage have no head clearance; the estore items' 0,15 / 0,20 must hold box + clearance → at TV
the frames were made to the openings (table = nominal) or there was no clearance. Sent 2026-10-20 night; his reply:
pending. For new projects: frames from the maker's order + 0,05. Room names in the table: "Despensa" = Arrumo /
Lavandaria, "Quarto Suite" = Quarto 01, "Quarto 1 e 2" = Quartos 02 / 03, "WC" = WC acess., "Sala / Entrada" = Sala +
Hall. Settled by the table: kitchen = vidro fixo, garage = portão seccionado. Open: the WC row "trasnparente" vs
"Fosco" (model fosco); suggestions — insulated, airtight shutter boxes with head flashings; the despensa basculante must
not open outward under its estore; the entrance size as clear passage (DL 163/2006).

**#21 Pergola — structure** — ANSWERED 2026-10-19 · OPEN
"a altura está ótima, as medidas não sei ao certo mas parecem estar ótimas, neste caso acho que foi aparafusado mas nem
sempre usamos esse método …, neste caso a pérgola foi feita independentemente …, tratamento autoclave e são lameladas …
não me relembro do nome" → a separate structure, beams on a ledger screwed to the façade over the horizontal battens
(photo `revisao-modelo/2026-10-19_obra_pergola_vigas_encosto.webp`). Open: sections (model 16×16 / 16×16 / ledger 7,5×16
/ slats 7×3), posts and their bases, the treatment's name; suggestions — post bases ≥ ≈ 150 mm above the deck (termite
bridge), a flashing over the ledger, beam ends 10–20 mm off the façade, sealed screws into the studs or the ring (sized
for bending across the batten gap), the treatment from the supplier (pale timber — colourless product).

**#22 Pergola as finished — tiled along the south side** — CLOSED (tile, downpipes, extent) · OPEN
"a pérgola vai até ao comprimento total da casa e leva telha e uma caleira à vista em todo o comprimento"; "É cerâmica";
"Um no lado oposto ao que se vê na foto". Photos: from just east of the garage to the east end (x 3,63 … 17,57), 6 posts,
a timber deck under it, 2 downpipes (the post at the wing's west face, the east corner post). Model v6.3 (slope 15 %
assumed, ceramic 46,4 m²). Open: ⚠ ceramic usually wants ≥ ≈ 30 % and the façade leaves ≈ 18 % → a continuous sub-roof
or another slope — what is under the tiles, the tile battens (at the tile's gauge, not slats at 0,15), what is seen from
below; clay ≈ 0,4–0,6 kN/m² + uplift → engineer; abutment flashings at P03 and the wing; the gutter section (≈ 23 m² per
downpipe — ø80 enough) and the downpipes' feet (not onto the deck by the wall); ≈ 46 m² of covered terrace where the
licence drew an open pergola → telas finais / area limits, daylight in the rooms behind.

**#23 Remates round every opening** — DECIDED 2026-10-20 · OPEN
"Todos os vão levam remates a volta da caixilharia …" Model v6.3 (assumed): folded aluminium RAL 7016 outside, sills with
a 3 cm drip under the 5 windows not to the floor, 13 mm Pladur inside, 11 openings, 59,7 m. Photos: dark round the
windows, light round the garage door, light pieces under the east janelas de correr (thresholds — not in the model). Open:
material / colour per opening, thresholds, the inside finish; suggestions — the three-plane seal, head flashings, sill
end dams, thresholds with a fall and tray (deck 2 cm under the floor, #5), separating tape against treated battens,
flanges clear of the cavity vents.

**#24 P18 windows moved apart for the pier** — DECIDED 2026-10-20 · OPEN (telas finais; the door case)
The architecture draws the two janelas de correr of quartos 02 / 03 ≈ 0,14 apart; D2503 put the 0,32 pier M13 between
them (≈ 16,5 cm each) — "por defeito podes assumir que sim … desde que sejam duas janelas". The approved elevation no
longer matches → telas finais; for a licensed project, a façade change for the architect; with a door: not said.
