# Perguntas por obra — the per-project checklist

What varies from house to house, to ask the user **at the start of every new project**, in one message. Kept by the
agent `mestre-construtor` with the rulebook `conhecimento/metodo-construtivo.md` (each item lists the rules it feeds:
`§n` + the rule's bold title, lessons `Ln`; the rulebook marks those rules **PO Qn**). Facts and sources:
`sistema-construtivo.md`; his words: `registo-conversas.md`. Condensed 2026-10-28 (history in git).

Why: user 2026-10-20 "Para cada obra aquelas anotações que te fui dizendo que depende de obra para obra anota e
faz-me essas perguntas", and on a missing answer "senão vai com o default de 2,5 cm".

## How to use it
- Send the questions (the `>` lines) in **one message, in PT-PT, numbered 1, 2, 3 … in the order listed**, each with its
  default in brackets so he answers only what differs ("o resto default"). The **Qn ids are fixed references**: a new
  item takes the next free id in its section (Q23 sits in D) — renumber only in the message. Skip the items *só se
  aplicável* the project does not have, and any item its documents already answer (say which document).
- Before asking, Grep `registo-conversas.md` and the project's `docs/estado.md`: do not re-ask what he already said
  for this house (L13). Questions about a drawing detail go with its image and label, one point per question (§0).
- **No answer → use the default and say so** ("usei o default de …"). Record each answer with its certainty
  (confirmed / tentative "acho que" / default used) in the project's `docs/estado.md` and the config key named below.
- **Keep the list current**: on "depende da obra", "neste caso", "nesta obra", "nem sempre", "para já" or "escolha do
  cliente" add or update an item; when he fixes a value ("é sempre assim", "o nosso padrão") move it to "Rules — do not
  ask".

## A. Before modelling — the documents

**Q1 · Desenhos de produção e estado da obra** — always
> 1. Já existem desenhos de produção nossos (módulos e cobertura, como o D2503) ou somos nós a desenvolvê-los? Se a casa já está construída, tens fotos da casa terminada? (default: desenvolvemos nós a partir do projeto)
- Default: we produce the module and roof drawings from the client's project ("quero que sejas capaz de desenvolver um
  documento igual ou do género", 2026-10-16); for a built house the company's drawings and the finished photos win over
  the architecture and memory (L23, L39). Chain: these questions → the model → Módulos, Cobertura, Listagem de material
  (`ferramentas/documentos/gerar.py`, §0a).
- Feeds: §0 "A company production drawing of the house … wins"; §0a; L23, L24, L39. Answer → project `CLAUDE.md`,
  `docs/estado.md`; cfg `modulos_reais` when a module drawing exists.

**Q2 · Tabela de vãos e encomenda do caixilho** — always
> 2. Podes enviar a tabela de vãos do projeto aprovado e, se já existir, a encomenda do caixilho com as medidas reais? (default: medidas da tabela como medidas do caixilho)
- Default: the approved table's sizes as frame sizes (tentative — "acho que é apenas a medida do caixilho sem folga",
  2026-10-19); no table → the architecture's openings, flagged.
- Feeds: §0a "Inputs per house"; §3 "The exterior openings come from the project's approved openings table"; L34, L37.
  Answer → cfg `camadas.caixilharia.itens`; `docs/materiais.md`.

**Q3 · Engenheiro e projetos de especialidades** — always
> 3. O engenheiro aprovou nesta obra alguma coisa diferente da nossa norma (vergas, vigas, fixações, pérgola)? Os projetos de especialidades já contam com o nosso sistema construtivo? (default: a norma em tudo)
- Default: the norms (verga 22×7,5 over wide openings, ceiling beams 22×7,5 at 1 m up to 8 m, glulam beyond); an
  exception only with the engineer's note ("neste caso o nosso engenheiro confirmou … mas por norma é 22x7,5",
  2026-10-19); specialty projects with our build-ups (ours).
- Feeds: §0 "The licensed specialty projects …"; §3 "Verga 220×75"; §4 ring fixing; §13; L28. Answer → `docs/estado.md`,
  `docs/revisao-tecnica.md`; cfg where a section changes.

## B. Foundation and heights

**Q4 · Base de fundação** — always
> 4. Que tipo de base de fundação leva esta obra e a que cota fica o pavimento interior em relação ao terreno e ao deck? (default: laje indicativa, vinílico direto sobre a base)
- Default: an indicative 20 cm slab ("uma laje representativa para já não tem mal"; the base still to be taught — §1
  OPEN); the foundation cast to the modules' outer face (D2503); vinyl straight on the base (2026-10-09); lowest timber
  ≥ 150 mm above the finished ground (general practice).
- Feeds: §1; §10 "Ground floor". Answer → cfg `fundacao`, `camadas.pavimentos.piso0`; `docs/estado.md`.

**Q5 · Pé-direito e alturas** — always
> 5. Mantemos o pé-direito do projeto de arquitetura ou o cliente escolheu outro (em Torres Vedras ficou 2,50 em vez de 2,60)? (default: o do projeto; sem projeto, 2,50; a casa pode ficar mais alta)
- **The client's choice, no company standard**: "A altura não temos fixa o cliente pode escolher a vontade o que
  preferir"; "O cliente pode escolher qualquer valor mas podemos deixar sugestões … essas 3 sugestões … por norma são o
  habitual" (2,40 / 2,50 / 2,60; 2026-10-21). Default: the architecture's; none → 2,50 (TV). RGEU floor 2,40 (2,20 in
  WC / corridors / storage). The modules follow it ("os modulos vão de encontro ao tamanho da casa"); a taller house "é
  natural". Hidden roof: exterior modules full height to the parapet top, the false ceiling ≈ 0,15 under the beams
  (below the ring). Exposed roof: a high head makes the exterior modules taller ("opção a", 2026-10-28).
- Feeds: §0 "The architecture fixes the geometry only"; §2 "Module height follows the house", "Hidden roof as built";
  §6; §15. Answer → cfg `niveis.pe_direito` (`teto_estrutura`), `platibanda.topo`.

## C. Structure

**Q6 · Módulos: tamanho e transporte** — always
> 6. Há alguma limitação de transporte ou de acesso ao terreno que obrigue a módulos de fábrica mais curtos do que 3 m, ou algum módulo que já saibas que vai ser feito em obra — e, se sim, com que comprimento? (default: até 3 m em fábrica; os maiores montados em obra, só do tamanho que o vão precisa; divisão escolhida por nós)
- Default: exterior factory modules **up to 3 m** — a maximum ("os módulos exteriores podem ir até 3 m"); interior up to
  2,75 (assumed); whole bays of the grid; bigger ones "montados em obra", as short as the opening needs ("depende da
  situação mas neste caso sim usa o tamanho que o vão precisa"); the remainder ours ("Vai com a opção que achares
  melhor"). Transport is the company's to solve ("A questão do transporte não precisas de te preocupar", 2026-10-21) —
  the transport part of the question can go (`mestre-construtor`); the site-built part stays.
- **After the split, not up front** (from the divider's log, with the module sheet): two **windows** closer than a 0,32
  pier are moved apart — his default, not asked, but **list every move** in the delivery (the approved façade changes);
  a **door** next to another opening ("a confirmar") → ask; a site-built module better run to the wall end (as D2503 M1)
  → ask.
- Feeds: §2 module-size rules; §13 Modules; L24, L25, L44. Answer → cfg `modulos.comprimento_max` (the divider's factory
  maximum for this house; JSON `estrutura.divisor.comprimento_preferido` 3,0 / 2,75), finer overrides in cfg
  `estrutura.divisor`; moves and door cases → `docs/estado.md`.

**Q7 · Cantos** — *optional* (normally just shown in the module drawings)
> 7. Nos cantos escolhemos nós que parede passa e qual encosta (não há regra da empresa) — queres ver a proposta antes de avançarmos? (default: escolhemos nós e mostramos nos desenhos)
- Default: one through, one abutting ("é suposto ser assim a lógica sempre, não temos uma regra específica para isso");
  which one ours — builder default X walls through.
- Feeds: §2 "Corners …"; §7 chapéus; L26, L38. Answer → the module drawing (per-corner override: not in the tools).

**Q8 · Vergas em vãos largos** — *só se aplicável* (an opening ≥ 2,8 m)
> 8. Os vãos com 2,8 m ou mais levam a verga normal de 22x7,5, ou o engenheiro aprovou outra (como os 11x7,5 do portão de Torres Vedras)? (default: 22x7,5)
- Default: verga 22×7,5 ("a partir de 2,8 m-3m", 2026-10-13; "mais de 3 metros usamos 22x7,5", 2026-10-22 — the exact
  threshold OPEN). Feeds: §3 "Verga 220×75"; §13; L28. Answer → cfg (module override) + the engineer's note.

**Q9 · Vigas de teto e tetos** — always
> 9. Vigas de teto como sempre (22x7,5 a 1 m até 8 m de vão, lameladas acima disso) e teto falso em toda a casa, ou há alguma zona com vigas à vista? (default: como sempre, teto falso em toda a casa)
- Default: 22×7,5 at 1 m up to 8 m ("O nosso limite é precisamente 8 metros"), glulam 20×10 at ≤ 0,92 beyond (D2503),
  bearing on the interior modules; flat false ceiling at the amarração, with every roof. Exposed glulam ceilings
  (3_Vigamento 200×100 at 1,02) only when he says so.
- Feeds: §6 "Vigas de apoio ao teto", "Past 8 m", "Exposed ceilings"; §13; §4. Answer → cfg `cobertura.estrutura`,
  `cobertura.vigas_teto`, `tetos`.

**Q10 · Piso superior** — *só se aplicável* (two storeys)
> 10. No piso superior: vigamento normal (22x7,5 a 61,5 cm, 50 cm nos vãos grandes) ou lameladas à vista nalguma zona? E onde abre a escada? (default: vigamento normal)
- Default: joists 22×7,5 ≤ 0,615 (0,50 for ≈ 4,8 m free), 11×7,5 at 0,60, wool 100, OSB 22, vinyl; "Sometimes … vigas
  lameladas which some times can be à vista". Feeds: §5; §13. Answer → cfg `estrutura.pavimento`.

## D. Openings (vãos)

**Q11 · Folga do caixilho e caixa de estore** — always
> 11. A caixilharia desta obra leva a folga normal de 2,5 cm em todos os lados (também por cima e por baixo das janelas), ou este caixilho pede outra? E qual a altura da caixa de estore do fornecedor? (default: 2,5 cm em todos os lados, nada por baixo das portas; com estore, como em Torres Vedras — altura do vão = caixilho + 0,15 nas janelas e + 0,20 nas janelas de correr até ao chão, caixa e folga incluídas; as portas não levam estore)
- Default: 2,5 cm each side and in height, "nem sempre … depende da caixilharia" (2026-10-20); none under a door to
  the floor (ours); + the maker's shutter-box height over windows only (doors take no estore — "Prtas não tem estore
  apenas as janelas", 2026-10-27); at a 2,40 pé direito the box takes 0,20 ("Apenas precisamos de 20 cm"). Before
  answering whether frames fit the openings, check every item both ways against `docs/materiais.md` (L42).
- Feeds: §3 "Exterior rough opening = the frame + a clearance"; §13; L34, L37, L41. Answer → cfg
  `camadas.caixilharia.folga` (JSON default 0,025); the box height (no key yet).

**Q12 · Caixilharia: padrão e portão** — always
> 12. A caixilharia segue o padrão atual (alumínio RAL 7016 com rotura térmica, vidro duplo, estore exterior automático, portas em painel liso)? E o portão da garagem é seccionado automático? (default: o padrão; portão seccionado)
- Default: the standard "para já" ("São o nosso padrão para já mas estamos a pensar mudar") — check first whether he
  announced the change; estores on windows only (a rule); garage door sectional automatic as at TV (assumed). In the
  configurator the garage gate's width and height are the client's choice "respeitando as nossas regras estruturais
  (tal como no menu de portas e janelas)" (2026-10-30); on a real house the size of the gate = the table / the order.
- Feeds: §3 "Caixilharia — the company standard 'para já'"; §11. Answer → JSON `caixilharia` / cfg
  `camadas.caixilharia`.

**Q13 · Portas e janelas diferentes da tabela** — always
> 13. Há portas ou janelas que vão ficar diferentes da tabela (como a porta de entrada de Torres Vedras, maior e a encher o vão)? As portas interiores são as normais de 0,80 x 2,00? (default: como na tabela; portas interiores 0,80 x 2,00)
- Default: the table + the clearance; interior doors 2,00 × 0,80 in 0,87 × 2,03; an element visibly smaller than its
  opening is asked, not modelled silently (L37); with an accessibility plan the entrance = clear passage (DL 163/2006).
- Feeds: §3 "Interior doors", "TV exterior rough openings as built"; L37. Answer → cfg `camadas.caixilharia.itens`
  (`largura` + `largura_tabela`); `docs/materiais.md`.

**Q23 · Remates e soleiras** — always
> 23. Os remates à volta dos vãos: por fora em alumínio quinado na cor da caixilharia, com peitoril com pingadeira nas janelas, ou outro material / cor nalgum vão (em Torres Vedras o do portão parece claro)? Por dentro o vão é forrado a Pladur (hidrófugo nas casas de banho)? E nos vãos até ao chão (portas, portas de correr) que soleira levam? (default: alumínio quinado na cor da caixilharia, peitoril com pingadeira; Pladur por dentro, H1 nas casas de banho; soleira a definir — não modelada)
- The rule is fixed (below); what varies: material, colour, profile, sill, inside finish, thresholds. Default (assumed,
  JSON `caixilharia.remates`): folded aluminium 2 mm in the frame colour, a 3 cm flange, a sill with a 3 cm drip; inside
  13 mm Pladur (H1 in wet rooms); no threshold modelled — flag it. Mention when relevant: the remate is not the seal
  (three planes), head flashing with a drip, end dams, a threshold with a fall and tray (Q22).
- Feeds: §3 "Every opening gets remates …"; §9 "Opening reveals inside"; §11. Answer → cfg
  `camadas.caixilharia.remates`; thresholds not in the tools; `docs/materiais.md`.

## E. Roof (cobertura)

**Q14 · Tipo de cobertura** — always
> 14. A cobertura é oculta (escondida) atrás de platibanda ou à vista? Se for escondida: uma só água (o habitual) — para que lado cai, onde fica a caleira? Se for à vista e a nossa estrutura a subir, mantemos a inclinação ou a cota da cumeeira? (default: como no projeto; escondida numa água com a inclinação mínima do painel)
- Default: the type from the architecture; hidden is the usual roof ("nós tentamos sempre só fazer uma água e sempre
  coberturas ocultas", 2026-10-28; say "Oculta" in client-facing texts — "muda o nome para este termo "Oculta" em vez de
  escondida", 2026-10-29; the gutter only on the low side of a one-água roof, none on the high side). Hidden → **one água where it works**, two only when the panels would be too long
  (> 15 m — his "afinal o máximo do painel é 15 metros", 2026-10-30 later; 13,5 before, ours) or no side is straight — "Aqui depende do caso … Não quero que assumas um padrão mas sim a solução
  mais eficaz e inteligente para cada caso" (2026-10-28) → choose per house and say why; the gutter side per house
  (default ours: the side where every strip ends on one straight line; a rectangle: south, or the client's choice —
  "Podes deixar o cliente escolher", 2026-10-29); the lowest slope the panel
  allows, the ridge / high wall rising as needed, one top level on every side, full-height exterior modules, the
  caleira oculta inside. Exposed → minimum 15 % ("A inclinação mínima da cobertura à vista é 15 %."), above it by the
  look the client wants; usually two or more águas "pelo aspeto tradicional" (2026-10-28); rectangle 2 águas with
  empenas; L / T / U "duas águas" or "várias águas" (the configurator offers only roofs with empenas à vista — "Deixa
  duas águas e várias águas apenas com empenas á vista", 2026-10-28; misto kept, "Tranquilo depois se necessário
  removemos essa opção"); beirado 0,25, range 0,20–**0,50** ("Beirado vamos definir um máximo de 50 cm se vires que é
  problemático em algum dos modelos podemos dimnuir nesse modelo", 2026-10-28 — a lower maximum per house allowed);
  the verges: = the eaves in the configurator since 2026-10-29 night (his "não vais ter dois telhados desalinhados"; ours,
  B3 asked; 0,12 only where the drawings fix it, [SB]). Sobral: keep pitch or ridge undecided ("para ja ainda nao vou tomar essa decisão"). A house
  with a project keeps its roof.
- Feeds: §7; L6, L17, L23. Answer → cfg `cobertura` (`tipo`, `inclinacao_pct`, `cumeeira_y`, `aguas`),
  `estrutura.cobertura_manter`, `platibanda`.

**Q15 · Painel e cores** — always
> 15. Que painel sanduíche leva (marca/modelo, espessura, núcleo PUR ou PIR e cor; a obra fica perto do mar ou em ambiente agressivo?) e de que cor são os chapéus e remates? (default: oculta 5 ondas 80 mm; à vista Munditelha (Mundiperfil) na cor original do fabricante (cor telha); chapéus RAL 7016)
- Default: always sandwich panel; telha only at the client's request ("a não ser que seja um pedido do cliente") → ask
  "o cliente pediu telha ou outro revestimento?" only then. Hidden 5-rib 80 mm (draft, D2503); exposed **Munditelha
  (Mundiperfil)** 40–60 mm ("utilizamos o munditelha da mundiperfil", 2026-10-22) — ask thickness and the colour
  reference: the colour is **the maker's original, not grey** ("Mais uma vez quero a cor original do painel de sandwich
  … e não cinzenta a cobertura", 2026-10-29; the dark grey / RAL 7016 default superseded; **RAL 8004 confirmed
  2026-10-30 — "é o ral 8004 e sim é o painel de 5 ondas imitação cor telha, o cinzento foi apenas para sobral"** — the
  Munditelha and the hidden 5-ondas panel; a house whose project says grey, as Sobral Tipo 1 — "dark grey", 2026-09-24 —
  keeps it); the **roof flashings and caps in the roof colour** (L69); chapéus RAL 7016 (assumed, not said — the
  chapéus are wall copings, not roof flashings: ask when it comes). Panels: 1 m wide, length per roof ("variável"),
  interlocking (2026-10-30). **Hidden panel = Mundiperfil MC 1000/5** (data sheet given 2026-10-30 later; see
  `sistema-construtivo.md` §6): 30–100 mm, 80 mm = U 0,25; PUR (fire F) or PIR (B-s2,d0, optional — ask which per house;
  PIR near a neighbour / garage, ours); maximum length **15 m**; minimum slope 6 % without laps; lap 300 mm; supports ≤
  1,50; **standard polyester is not for marine / aggressive environments** → ask per house the distance to the sea /
  the air (a coastal house: a different coating — ask the maker); annual inspection handed to the client. **2026-10-30
  (later still): thickness — "usamos os de 80mm" → default 80 mm for the hidden 5-ondas panel (confirmed; the Munditelha's
  thickness: asked, still 40 mm "a confirmar"); the coastal check — "Sim já foi verificado" (for TV, whose purpose he
  describes as learning about the company and evaluating our suggestions) → still a per-house question (the coating
  follows the house's air; the data sheet's standard polyester is not for marine / aggressive air); PUR / PIR — "Ok tranquilo" → per
  house, PIR suggested near a neighbour / garage; 15 m panels — "Sim tranquilo".** What goes
  under the chapéus: promised (reminder of 2026-10-20) — add it here when he says.
- Feeds: §7 "Covering", "Chapéu"; §13 Panels. Answer → cfg `cobertura.painel_oculto` / `cobertura.painel`,
  `cobertura.chapeu`.

**Q16 · Caleiras e tubos de queda** — always
> 16. Caleira oculta com 31 cm de largura como em Torres Vedras, ou outra? A saída da caleira para cada tubo de queda é lateral (um furo no forro do lado da platibanda, para dentro do revestimento) ou um furo no fundo da caleira (como em Torres Vedras)? Que bocal e com que medida? Os tubos de queda vão por dentro do revestimento (o nosso método — em Torres Vedras ficaram por fora): que secção usam? Cada caleira leva ladrão (descarga / gárgula de emergência pela platibanda, uns cm acima do fundo da caleira, para a água sair à vista se o tubo entupir) — de que tipo e a que altura? No fundo dos tubos a água vai para onde (terreno, gravilha, caixa de pluviais)? (default: 31 cm; saída lateral pela platibanda, um furo à largura do tubo no ponto baixo da caleira em cada tubo de queda; tubos por dentro do revestimento, 100 × 50 (≈ 50 m² por tubo, 1 cm² por m²; a resposta dele de 2026-10-30), com rebaixo local nas placas de cortiça / capoto e só até à caixa de ar onde esta é rasa; sem ladrão no modelo, assinalado na entrega — recomendamos um por caleira, abaixo do topo da madre; a acabar 5 cm acima da base)
- Default: caleira oculta 0,31 clear, fall ≈ 2 % on calços, outlets at the low ends, lining 0,80 tile colour (D2503);
  downpipes inside the façade cladding — the method ("é a forma correta"; "achamos que por dentro é mais correto e fica
  melhor"; TV as built had them outside) — ending ≈ 5 cm above the base. Exposed roof: exterior gutter 125×90,
  downpipes 80 (assumed). Outlet holes at every downpipe are fixed (L43); the outlet **type** and bocal: promised ("isso
  depois eu digo") — default the side outlet, flagged "a confirmar". **2026-10-30**: "Normalmente 10cm de bocal mas pode
  ser maior dependendo da zona, isso depende da inclinação e da dimensão da cobertura mas vamos com dois tubos por
  caleira a nao ser que a caleira seja pequena" → bocal 10 cm by default (larger by zone / slope / roof size), **2
  downpipes per gutter, one on a small gutter** (the 37 m² per pipe rule is dropped); ask per house the bocal's size if
  the roof is large or steep and what the 10 cm measures. **2026-10-30 later**: "usa o bocal ideal para esse tubo e
  distribui como achares melhor" → the outlet = the pipe's section (80 × 35 in the cladding; **100 × 50 since 2026-10-30
  later still, "Sim usa de 100x50"**), the downpipes: 2 per gutter,
  1 on a gutter ≤ 4,0 m ("sim está bem"), more, evenly spaced, for ≈ 1 cm² of pipe per m² drained (ours, general
  practice) — nothing to ask per house but the outlet type. **Ladrão**: "explica-me o que é um ladrao mas penso
  que não" — tentatively none; explain the term when asking; default "sem ladrão no modelo", flagged. Section: our advice
  ≈ 1 cm² per m² (the tools' 80 × 35 cavity ≈ 26 cm² is too small for ≈ 37–46 m²) →
  **2026-10-30 (later still): his "Sim usa de 100x50"** → default pipe **100 × 50** (≈ 50 m² each; his L: 4 pipes, was 7);
  fits the Tremolo cavity (contra-ripado 20 + ripado 35 = 55 mm); cork (cavity 40) and ETICS (none): a local recess in
  the cork / XPS boards round the pipe; the Tremolo boards never get a hole; a house with a shallower cavity (TV: ripado
  only) → the engine warns and limits the pipe to the cavity (33 mm) — **nothing to ask about the section any more**;
  say, per house, the façade's cavity depth and that an ETICS / cork recess leaves little board (`sistema-construtivo.md`
  §6). Exposed roofs: 80 × 80 (assumed).
- Feeds: §7 gutters, downpipes, outlets, overflow; §12; §13; L40, L43. Answer → JSON `cobertura.caleira_oculta` / cfg
  `cobertura.caleiras` (`saidas`, falls); outlet type and overflow: no key yet.

**Q17 · Claraboias** — *só se aplicável* (the drawings show some)
> 17. As claraboias do projeto vão ser feitas? (em Torres Vedras não foram) (default: modelo-as como no projeto e assinalo)
- Default: model those drawn and flag them; how DiscoverCasa frames a skylight: OPEN. Feeds: §7 "Skylights". Answer →
  `docs/estado.md`.

## F. Finishes (acabamentos — the client's choice)

**Q18 · Revestimento exterior** — always
> 18. Revestimento exterior: madeira (Tremolo vertical), ETICS ou cortiça? Com contra-ripado (o padrão) ou só ripado horizontal como em Torres Vedras? (default: o do projeto; madeira com contra-ripado)
- Default: as the architecture shows; A wood = Traspir, contra-ripado 30×20, ripado 37,5×35 every 35 cm from the bottom,
  Tremolo vertical; B ETICS (XPS thickness from the thermal project); C cork 60 on battens + counter-battens.
- Feeds: §8 (A, B, C); L15, L22. Answer → cfg `camadas.exterior.opcao_visivel`, `camadas.exterior.opcoes`.

**Q19 · Acabamentos interiores** — always
> 19. Interiores em Pladur (normal, hidrófugo nas zonas húmidas, ignífugo junto a fontes de calor), ou há paredes ou tetos em madeira ou cerâmica? (default: Pladur em tudo, H1 nas casas de banho e cozinha)
- Default: Pladur 12,5 N, H1 in wet rooms, F near heat; wood on battens ("slatted against slatted if it it vertical
  wood"), ceramic on request; the inner face of exterior walls too ("o nosso acabamento padrão nessas faces interiores é
  gesso cartonado"). The interior finish list is promised ("Mias tarde vou ter fornecer …") — name the products then.
- Feeds: §9; §6. Answer → cfg `camadas.interior.acabamento`, `tetos.acabamento`.

**Q20 · Pavimentos** — always
> 20. Pavimento vinílico em toda a casa, ou cerâmico nalgumas divisões (cozinha, casas de banho)? (default: vinílico em toda a casa)
- Default: vinyl planks everywhere; chosen per room ("a pessoa pode aplicar pavimento que desejar na divisão que
  desejar", 2026-10-22). Feeds: §10; §1. Answer → cfg `camadas.pavimentos`.

## G. Extras attached to the house

**Q21 · Pérgola / alpendre** — always (when the drawings show one, or the user mentions one)
> 21. Há pérgola ou alpendre? Se sim: de onde até onde vai exatamente (em Torres Vedras não passava à frente do portão da garagem), que cobertura leva (ripas, telha cerâmica ou painel imitação telha)? Se for telha cerâmica: que inclinação e o que leva por baixo das telhas (subtelha, placas + membrana, ripas)? Caleira (secção), quantos tubos de queda e para onde descarregam? Secções, tratamento da madeira e como fixa à casa? (default: só se estiver no projeto, com a extensão do projeto; fixação a confirmar sempre)
- Default: only if drawn, with the drawn extent; a separate structure on posts and a ledger, glulam with autoclave
  treatment (TV); **the fixing always asked** ("nem sempre usamos esse método quando for relevante nas pérgolas eu
  dou-te essa informação"). TV as finished: from just east of the garage to the east end, ceramic tiles, an exposed
  gutter with 2 downpipes, 6 posts, a deck — find both ends in a photo or ask (L39). Ceramic ≥ ≈ 30 % or a continuous
  sub-roof; a covered pergola → engineer; downpipes ≈ 1 cm² per m², feet into a drain, never onto the deck by the wall.
- Configurator step 7 (2026-10-29, `sistema-construtivo.md` §3d): the client's pergola has a **maximum height** —
  2026-10-30: "até há altura máxima do PISO 0 ou seja do PISO TÉRREO … o ponto mais alto da pérgola pode ficar alinhado
  com a altura máxima desse piso térreo" (a two-storey house too); for a real house, check the pergola's top against that
  line (ring top / ceiling-beam top / parapet top: to confirm) and the eave. Garages and annexes **junto à casa** (our
  structure grows, the house's roof) or **separado** (own roof; distance **2 m** — "pode ficar 2 metros", 2026-10-30 later, after his
  3 m / 2 m; interior walls only in attached blocks; a real lot: RT-SCIE / PDM may ask more): ask the wall between house and garage (interior or insulated + fire-rated
  door — he calls it "parede interior") and whether an annex is heated; the garage gate's width / height by the
  structural limits (2026-10-30).
- Feeds: §8 pergolas; §13; L35, L39. Answer → cfg `pergola`; `docs/estado.md`.

**Q22 · Deck e outros elementos** — always
> 22. Deck, muros, telheiros, escadas exteriores, garagens ou anexos (junto à casa ou separados) ou outros elementos encostados à casa entram no nosso trabalho? A que cota fica o deck em relação ao pavimento interior? (default: não modelados, listados na entrega)
- Default: not modelled, listed as "not in the model" (L35) — except what the configurator's step 7 builds since
  2026-10-29 (pergola, garage / annex: `sistema-construtivo.md` §3d); the deck level checked against the timber's clearance (TV
  deck 117,48 vs floor 117,50 — TV #5; ≥ 150 mm). Feeds: §1; §0a; L35. Answer → `docs/estado.md`.

## Rules — do not ask every time
Fixed by the user as the method (rulebook sections in brackets); say them only if the drawings contradict them, as "o
nosso método é …, confirmas?":
- Our method over the architect's and engineers' construction notes; the drawings fix the geometry (§0).
- Modules' outer face on the architect's outer outline, the foundation cast to the modules (§2).
- Exterior 110×35 / interior 75×35, 110×75 at corners and openings, studs at 40 cm clear, every opening inside one
  module, vertical cripples only, interior doors 0,87 × 2,03 (§2, §3).
- Every opening gets remates round the frame, outside and inside ("Todos os vão levam remates a volta da caixilharia …")
  — only material, colour, sill, thresholds asked (Q23). Doors never take an estore.
- Corners: one through, one abutting — which one ours (§2; Q7).
- The module split: openings inside one module, whole bays, no joint where a wall meets; the remainder ours; two windows
  closer than a pier moved apart by default, every move listed (§2; Q6).
- Interior modules made to measure to the amarração, no packing; the base laser-checked (§2, §4).
- Ceiling beams bear on the interior modules they cross and **never cross the exterior modules nor cut their studs** —
  inside, against the modules, on the ring, at most the beam notched to fit (§4, §6; 2026-10-21; rulebook L46).
- Flat false ceiling at the amarração (hidden roofs: below the ring): réguas, steel perfis at 0,40, cantoneira in 3 m
  bars, Pladur, Volcalis 100 (§6); it comes with every roof.
- Hidden roof: one top level on every side, the caleira oculta inside the parapet, the lowest slope the panel allows,
  one água where it works (§7; the gutter side is asked in Q14).
- Chapéus round the whole perimeter of the hidden roof, wrapping the wall top, flat, legs ≈ 2 cm both faces (2026-10-28;
  was 2–3 cm); every top covered once — no uncovered top, no overlap (§7).
- Gutter walls: the gutter lining up to the chapéu; parapets without a gutter clad on the roof side to the end of the
  sandwich panels in **the house's own façade finish** — wool, OSB 15, Traspir, then the façade build-up ("o capoto tem
  que ficar na casa toda", 2026-10-28; TV's ripado + Tremolo is TV's façade); every parapet end closed (§7).
- Downpipes inside the exterior cladding, never in a room or across an opening, ending just above the base; every
  hidden gutter has its outlet hole at each downpipe (§7, L43); the hidden pipe is 100 × 50 (2026-10-30 later still);
  outlet type and overflow asked (Q16).
- Outside: OSB 9, Traspir 95 lapped 20 cm, then the finish; wood: ripado 37,5×35 horizontal every 35 cm from the
  bottom, Tremolo vertical, battens round every opening except the floor side, a vertical batten at every corner on
  both faces (§8).
- Inside: wool 80 (exterior) / 60 (interior), OSB 15, then the finish (§9).
