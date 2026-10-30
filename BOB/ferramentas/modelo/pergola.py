"""A timber pergola against one facade of a plan house (the configurator's step 7), as Torres Vedras' was built
(casa_planta.py 1.10, user 2026-10-19 / 2026-10-20): a separate structure — posts under a front beam, beams falling to
the front, resting on the front beam and on a ledger screwed to the facade over the battens (the cladding cut round
it), slats across on the beams; glulam with autoclave treatment. Pure Python.

The client places it on a wall and picks its width along it, its projection and its height (user 2026-10-29:
"Pérgolas o cliente deve poder escolher a largura e onde quer colocar a pérgola dando snap para o sítio no forro
exterior, a altura tem de ter um máximo"): the height is the beams' underside at the facade, where the ledger is bolted
to the wall's solid framing — its highest point at most the ground floor's top (user 2026-10-30, maximo); the sections, the beam and slat spacing and the post spacing come from sistema_construtivo.json `pergola`
(Torres Vedras' tentative sections, "parecem estar ótimas"); each post on a steel base, its end grain off the ground.

    pecas = construir(lado, s0, s1, projecao, altura, P, esp_rev, esp_rip)
lado: {"p0": [x, y], "u": [ux, uy] (along the side, unit), "n": [nx, ny] (outwards, unit)}; s0, s1 along the side from
p0 (the pergola's width); projecao from the finished facade; altura of the beams' underside at the facade; P the JSON
`pergola`; esp_rev the cladding's depth outside the base edge, esp_rip up to the battens' face. Returns items
{"nome", "colecao" "1.10", "material", "pecas" (convex prisms), "props"} as casa_planta's estrutura_extra.
"""
import math


def _prisma(base, ext):
    return {"b": [[round(v, 4) for v in p] for p in base], "e": [round(v, 4) for v in ext]}


def maximo(z_topo_piso0, P):
    """The highest the beams' underside may sit at the facade: the pergola's highest point (the slats on the beams)
    at the ground floor's top — the top of its ceiling beams (user 2026-10-30: "A pérgola pode ir até há altura
    máxima do PISO 0 ou seja do PISO TÉRREO, se existirem casas de dois andares o ponto mais alto da pérgola pode
    ficar alinhado com a altura máxima desse piso térreo"; was the ring's top + 0,10, ours from Torres Vedras)."""
    return round(z_topo_piso0 - P["vigas"]["altura"] - P["ripas"]["espessura"], 3)


def construir(lado, s0, s1, projecao, altura, P, esp_rev, esp_rip, nome="Pérgola"):
    (px, py), (ux, uy), (nx, ny) = lado["p0"], lado["u"], lado["n"]

    def mundo(a, b, z):  # a along the facade (from p0), b out from the base edge, z up
        return (px + ux * a + nx * b, py + uy * a + ny * b, z)

    def caixa(a0, a1, b0, b1, z0, z1):
        return _prisma([mundo(a0, b0, z0), mundo(a1, b0, z0), mundo(a1, b1, z0), mundo(a0, b1, z0)], (0, 0, z1 - z0))

    def inclinada(a0, a1, b0, b1, dz0, dz1):  # along b following the slope, dz over the beams' underside
        base = [mundo(a0, b0, zb(b0) + dz0), mundo(a0, b1, zb(b1) + dz0), mundo(a0, b1, zb(b1) + dz1), mundo(a0, b0, zb(b0) + dz1)]
        return _prisma(base, (ux * (a1 - a0), uy * (a1 - a0), 0.0))

    pil, vf, ve, vg, rp = P["pilar"], P["viga_frontal"], P["viga_encosto"], P["vigas"], P["ripas"]
    incl = P.get("inclinacao", 0.05)
    b_led = esp_rip + ve["espessura"]          # the ledger on the battens: its outer face
    b_fr = esp_rev + projecao                  # the front beam's outer face (the projection from the finished face)

    def zb(b):  # the beams' underside, falling to the front
        return altura - incl * (b - b_led)

    mat = P.get("material", "Madeira pérgola")
    props = {"produto": P.get("produto", "")} if P.get("produto") else {}
    itens = []

    def item(n, tipo, sec, pecas, comp, vol, **kw):
        itens.append({"nome": f"{nome} | {n}", "colecao": "1.10", "material": mat, "pecas": pecas,
                      "props": {"seccao": sec, "tipo": tipo, "comprimento_m": round(comp, 3), "volume_m3": round(vol, 5),
                                **props, **kw}})

    W = s1 - s0
    # the front beam and its posts (at both ends, the rest in equal bays <= pilar.espacamento_max)
    zf1 = zb(b_fr - vf["largura"])
    zf0 = zf1 - vf["altura"]
    item("viga frontal", "Viga frontal da pérgola", vf["seccao"], [caixa(s0, s1, b_fr - vf["largura"], b_fr, zf0, zf1)],
         W, W * vf["largura"] * vf["altura"])
    lp = pil["largura"]
    n_p = max(1, math.ceil((W - lp) / pil.get("espacamento_max", 3.5) - 1e-9))
    bp, zt = P.get("base_pilar"), P.get("z_terreno", P.get("z_base", 0.0))
    for k in range(n_p + 1):
        a = s0 + lp / 2 + (W - lp) * k / n_p
        bc = b_fr - vf["largura"] / 2
        z0 = P.get("z_base", 0.0)
        item(f"pilar {k + 1}", "Pilar da pérgola", pil["seccao"],
             [caixa(a - lp / 2, a + lp / 2, bc - lp / 2, bc + lp / 2, z0, zf0)], zf0 - z0, lp * lp * (zf0 - z0))
        if bp and z0 - zt > 0.005:  # on a steel base: the end grain off the ground (general practice, >= 0,15)
            hb = bp["largura"] / 2
            itens.append({"nome": f"{nome} | base do pilar {k + 1}", "colecao": "1.10", "material": bp.get("material", "Aço galvanizado"),
                          "pecas": [caixa(a - hb, a + hb, bc - hb, bc + hb, zt, z0)],
                          "props": {"tipo": "Base metálica do pilar da pérgola", "produto": bp.get("produto", ""), "unidades": 1}})
    # the ledger over the battens, screwed to the wall's framing (the cladding cut round it)
    h_e = ve.get("altura", vg["altura"])
    item("viga de encosto", "Viga de encosto da pérgola (aparafusada à fachada, sobre o ripado)", ve["seccao"],
         [caixa(s0, s1, esp_rip, b_led, zb(b_led) - h_e, zb(b_led))], W, W * ve["espessura"] * h_e)
    # the beams: from the battens to the front beam's outer face, one at each end, the rest <= vigas.espacamento_max
    lv = vg["largura"]
    n_v = max(1, math.ceil((W - lv) / vg.get("espacamento_max", 1.4) - 1e-9))
    comp_v = (b_fr - esp_rip) * math.sqrt(1 + incl * incl)
    for k in range(n_v + 1):
        a = s0 + lv / 2 + (W - lv) * k / n_v
        item(f"viga {k + 1}", "Viga da pérgola", vg["seccao"],
             [inclinada(a - lv / 2, a + lv / 2, esp_rip, b_fr, 0.0, vg["altura"])], comp_v, comp_v * lv * vg["altura"])
    # the slats across the beams, from the finished face to the front
    pecas_r, b = [], esp_rev + 0.02
    while b + rp["largura"] <= b_fr + 1e-6:
        pecas_r.append(inclinada(s0, s1, b, b + rp["largura"], vg["altura"], vg["altura"] + rp["espessura"]))
        b += rp["espacamento"]
    item("ripado", "Ripado da pérgola", rp["seccao"], pecas_r, W * len(pecas_r), W * len(pecas_r) * rp["largura"] * rp["espessura"],
         n_ripas=len(pecas_r))
    return itens
