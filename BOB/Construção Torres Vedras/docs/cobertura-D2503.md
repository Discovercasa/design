# Roof as built — DiscoverCasa drawing D2503 (read 2026-10-16)

Source: `desenhos/250828_D2503_Cobertura.dwfx` (DiscoverCasa's own production set, AutoCAD LT, 28/08/2025,
"Habitação Unifamiliar LA", obra D2503; 5 A3 sheets; sheets 1–4 "Sem Escala", sheet 5 1:50). Given by the
user 2026-10-16: "o documento exato sobre a cobertura de Torres Vedras … eu disse-te mal como seriam as
águas". It replaces the architect's roof plan and the user's sketch of 2026-10-16 (one slope per part of the L).
Revisions: A 25/07/04 "Dimensões para execução" · C 25/07/29 "Cobertura - Vigas de 16x8 para 20x10" ·
D 25/07/31 "Fundação - Hidraulicas" · E 25/08/28 "Cobertura e Módulos - Correção para produção".
Measured with `ferramentas/dwfx/leitor.py` (sheet 1 at 16,72 mm/m; sheet 5 at 1:50). Plan axes as the
model: X along the house (west → east, 0 … 17,5), Y south → north (0 … 11); the wing is x 10,78–17,5, y 0–2,5.

## Sheets
| Sheet | Title | What it fixes |
|---|---|---|
| 1 | Cobertura - Lameladas horizontais e amarração | glulam beams (lameladas), their spacing and lengths, amarração ring, ridge line |
| 2 | Cobertura - Madres (Pendentes) - Esquema geral | purlins (madres) and ridge purlins in plan, spacings, madre piece lengths, gutter falls |
| 3 | Cobertura - Madres (Pendente) - Posicionamento | 4 schemes: where the madre pieces of 3,60 / 3,66 / 2,75 / 2,90 m go |
| 4 | (Telhas) | sandwich panels: 3,94 × 1,00 (28–29), 6,44 × 1,00 (7), strip 3,94 × 0,25, the cut corner panel, "ENCOMENDAR 18 CUMEEIRAS" |
| 5 | Secções tipo para as vigas de 11m e 8.5m (1:50) | the two typical sections (all heights), pormenor caleira/algeroz |

Legend used on every sheet: "Dimensão da fundação e módulos" (outer line) · "Dimensões ao eixo" (axes) ·
"Dimensões de espaçamento" (clear gaps) · "Linhas de pronto" (finished faces) · Módulos · Amarrações (11x7.5).

## The logic, piece by piece (and why)
1. **Modules on the foundation line.** The outer face of the wall modules is the foundation dimension
   (17,5 × 11; 8,5 for the main block): "Dimensão da fundação e módulos". The frame is 0,11 thick; the
   exterior cladding is outside that line ("linha de pronto" ≈ 9 cm out), OSB 15 + Pladur inside.
   *Why:* the module is the unit that is made and checked; the foundation is cast to the modules.
2. **Modules are full height, parapet included.** In both sections the module runs in one piece from the
   base (z 0) to the parapet top **z 3,49** (3,4915), the same on every wall ("mesma altura em todos os lados").
3. **Amarração 11x7.5 is a ring on the inner face** of the modules (sheet 1 pink line just inside the
   modules, all round), 0,075 into the room, **z 2,543–2,653** ("2,54" in the sections).
   *Why:* it ties the modules together and carries the beams without cutting the module's top.
4. **Lameladas 20x10 (glulam, 0,10 wide × 0,20 deep), N–S, on the amarração, z 2,653–2,853**, through the
   wall frame to the module's outer face — in a notch cut in the module, the beam inside the wall (user 2026-10-19,
   15:48: "sim há um entalhe feito e a viga fica por dentro"; cut on site — "O entalhe é feito em obra", 18:12)
   (superseded 2026-10-21, see registo: **the lameladas end inside, against the modules' inner face, on the ring — they
   never cross the module, the studs are never cut; at most the beam is notched to the exact length** — "essas vigas
   ficam por dentro e encostadas as da estrutura não atravessam"; inside length ≈ 8,28 / 10,78. ⚠ The 8,50 / 11,00
   below = the outer depths: read as the ordered / listed length, cut to fit on site — to confirm; asked 2026-10-21
   without naming the house or the sheet, the user: "A quais lameladas te referes?" — re-ask with this sheet's image and
   the labels A / B) (**answered 2026-10-21**, re-asked with this sheet, see registo: "Sim normalmente cortamos para
   "encaixar" no tipo de obra que temos, há casas com mais comprimento outras com menos" → the lameladas are **cut to
   fit each house**: 8,50 / 11,00 = the nominal length (the house's outer depth), bought from stock (13,5 / 12 m below)
   and cut to the inside length ≈ 8,28 / 10,78 — on site, our reading of the "Sim"; the model's length is the real piece)
   (A: 8,50 long, 11 in the main block; B: 11,00 long, 7 where the wing
   is, x > 11). Spacing: the 17,39 between the end walls' axes in **19 equal bays of 0,915** ("0,92" at the
   ends from the wall axis, "0,91" between, "0,81" clear). Cut from stock: A from 13,5 m (5 m waste), B from
   12 m (1 m waste) (labels still say "16x8": revision C changed 16x8 → 20x10).
   *Why:* one piece wall to wall (8,5 / 11 m; D2503 draws no intermediate support, but the interior walls below
   reach the lameladas' underside — whether they bear is to confirm, see the note below (answered 2026-10-19, see
   registo: they bear — "Por norma as vigas de apoio ao teto apoiam-se nas paredes dos módulos interiores também")); glulam because 11 m is past the
   company limit for sawn 22x7,5 (8 m); 20x10 after revision C.
5. **Ceiling under the lameladas at z ≈ 2,50** (dimension "2,5"; ceiling line in the sections): clear height
   2,50, not the architect's 2,60. The suspension hangs ≈ 0,15 under the lameladas, which leaves the
   amarração (2,543–2,653) above the ceiling.
6. **Ridge in the middle of the main block, along X, y = 6,747** (4,25 from the north face; "Linha de
   cumeeira", sheet 1). **Two slopes at 6 %** (measured 6,0 % between every pair of madres in both sections):
   north to the P11 gutter; south to the P03 gutter for x < 10,9, and **over the wing down to the P01 gutter**
   for x > 10,9 (the south slope simply runs on, 6,44 m of panel instead of 3,94).
7. **Madres 11x7.5 standing (0,075 × 0,11), along X, on vertical prumos on every lameladas.** Ridge: a pair
   ("Cumeeiras", "Madres de cumeeira") 0,10 apart (axes) — 11x7.5 in the 8,5 m section, labelled 22x7.5 in the
   11 m section (drawn 0,11 high like the others). From each gutter the madres step up the slope at ≈ 1,265
   (1,26 / 1,26), the last bay to the ridge shorter (1,21). The gutter madre axis is 0,40 from the wall axis
   (0,31 clear from the wall's inner face: the gutter width). Madre y (axes): north 10,54 / 9,28 / 8,01 /
   ridge 6,80 + 6,70; south 5,48 / 4,22 / 2,96 (gutter madre of the main block, intermediate over the wing)
   / 1,71 / 0,46 (wing gutter madre). The south madres run continuously over the main block and the wing;
   the wing adds two lines (1,25 bays).
   Madre underside above the lamelada top: main block 0,15 (gutter) · 0,23 · 0,30 · 0,38 (ridge); wing 0
   (gutter madre directly on the lameladas) · 0,08 · then 0,15 … as the main block.
   *Why the heights:* the ridge is as low as the slope allows: the **longest slope's gutter madre sits on the
   lameladas** (wing, 6,29 m run) and the shorter slopes' gutter madres are raised by the difference
   (6 % × 2,5 m = 0,15). Ridge madre top z 3,339; panel top ≈ 3,42; ridge cap z 3,465; parapet top 3,4915 —
   the roof stays hidden by ≈ 3 cm.
8. **Madre pieces ≤ 3,66 m, jointed on lameladas** (sheet 3): main block 3,60 + 3,66 + 3,66 + 2,75 + 3,60;
   wing 2,90 + 3,60 (joints on the same lameladas). *Why:* 4 bays of 0,915 = 3,66 = one stock length.
9. **Hidden gutter (caleira/algeroz) 0,31 wide between the parapet and the gutter madre**, on packing on the
   lameladas (dashed crossed boxes, 0,50 long: 0,31 under the gutter + 0,19 under the madre; height marked
   "VARIÁVEL"). Lining profile (pormenor): bottom 0,30, parapet side 0,30 (in the section it runs up the
   parapet face to the top, under the chapéu), madre side 0,10 up + 0,10 flange over the madre (under the
   panel). The panels run ≈ 0,10 past the madre into the gutter.
   **Falls ("Pendente da caleira", "Linha da telha"):** north 0 → 0,17 (high in the middle, two halves of
   8,61, outlets at both ends); main block south 0 → 0,22 (high at the wing, outlet at the west end); wing
   0 → 0,06 (high at the west end, outlet at the east end). *Why:* ≈ 2 % fall, but never closer than ≈ 4–5 cm
   to the gutter madre's top — the wing gutter madre sits on the lameladas, so its fall stops at 0,06.
   **As built — site photos** (user 2026-10-19, 18:12, "imagens reais de como ficou a cobertura";
   `revisao-modelo/2026-10-19_obra_caleira_platibanda.webp`, `…_obra_caleira_forro_saida.webp`; keeper's reading):
   the gutter is an OSB box along the parapet (bottom + roof-side upstand + end), the parapet's roof face OSB down into
   it; lining a red (tile-colour) sheet — bottom, both sides up to the rim, end plate turned up, screwed along the top
   edges, corners and outlet sealed (white); the **outlet a round hole in the bottom near the end** (vertical drop, not
   through the parapet); no overflow visible; above the lining's parapet leg the OSB bare at that stage (so the
   section's "lining up to the top" was not, or not yet, there). Photo 4 read with the caller as the P01 (wing) gutter
   looking east, the outlet at its east (low) end as drawn.
10. **Panels (sheet 4):** 5-rib sandwich, 1,00 useful width, laid from the east end: 3,94 m on the north
    slope and on the south slope of the main block (28–29 = 27 + 1–2 to cut, plus a 3,94 × 0,25 strip at the
    west end), 6,44 m over the wing (7 = 6 + 1 to cut). The panel at the re-entrant corner is one 6,44 panel cut
    in an L ("PORMENOR TELHA PARA REMATE": 3,94 full width + 2,50 × 0,47 over the wing, 0,53 cut off).
    "ENCOMENDAR 18 CUMEEIRAS" (ridge caps for 17,5 m).
11. **Chapéu** on the module top: flat, over the frame and the claddings, legs ≈ 2–3 cm down both faces. (User
    2026-10-20: the chapéus never leave a top uncovered and never overlap one another — at a corner one covers it, the
    other butts against it; `conhecimento/sistema-construtivo.md` §6.)

## Open / to confirm with the user
- Roof side of the parapets: in the sections the gutter walls' inner face is covered by the gutter lining up
  to the top ("linha de pronto" 1 cm off the frame), not by OSB 15 + Traspir + ripado + Tremolo (user
  2026-10-15). The gable parapets (P12, P18, P14) are not cut by any section. (Asked 2026-10-16; not understood by the
  user — to explain again with an image.) (Gable parapets answered 2026-10-19, 18:12, see registo: "o forro é suposto
  ir ate ao final do painel sanduiche" — their roof-side cladding runs to the end of the panels over the gutter; model
  v6.1. Gutter walls: the site photo shows the lining's parapet leg only to the rim, bare OSB above — lined to the top
  later or clad: still open, `revisao-tecnica.md` #15.) (Gutter walls answered 2026-10-20, see registo: "revestimento
  da caleira até ao topo que depois se encontra com os chapéus da platibanda" → lined up to the top, meeting the
  chapéu — as item 9's section; the photo was an earlier stage.)
- Downpipe outlet: a round hole in the gutter bottom (site photo) — how the pipe reaches the façade cavity: to ask (#9).
  (Answered 2026-10-20, see registo: "nós nesta obra fizemos de forma diferente mas a forma como modelaste no blender
  por dentro do revestimento é a forma correta" → TV's downpipes differ from the method (how: not said); the company's
  way is the modelled route inside the cladding.) (2026-10-20 ≈ 13:51, see registo: "nas caleiras nao existem os buracos
  par agua escoar para os tubos de queda" → model v6.4 has an outlet hole at each downpipe, parapet side; whether the
  method's outlet is that side outlet or a bottom one like this photo: to ask, `revisao-tecnica.md` #9.)
- Downpipes: not drawn; outlets at the gutters' low ends (above). (Answered 2026-10-16, night, see registo: as modelled
  in v4 — "como esta desenhado está perfeito".)
- Ridge madres "22x7.5" over the wing: label vs drawn size. (Answered 2026-10-16, night, see registo: **22×7,5** —
  "então é como estão no desenho com 22x7,5"; why there only: not said.) Chapéu flat confirmed the same night.
- Gutter packing under the madre (0,15) vs the gutter fall up to 0,22 under the lining (main south): at the
  high end the gutter bottom is above the madre's base.
- (Details keeper 2026-10-16) Item 4 "no interior bearing": over 11 m a 20×10 at 0,915 would be overstressed and sag
  ≈ 0,13 m in time (rough check, `revisao-tecnica.md` #6) — check on sheet 1 / the sections whether the 11 m lameladas
  bear on an interior wall (the suite's line at y ≈ 2,5) and the 8,5 m ones on any; the v4 model has an afinação
  interior. (Answered 2026-10-19: the ceiling beams bear on the interior walls they cross — the norm; model v5.1.) Item 9: the lowest rim of each gutter is the madre side at its high end (≈ 4–5 cm; wing 0,06), with the
  roof void behind it — no overflow drawn (#4).
