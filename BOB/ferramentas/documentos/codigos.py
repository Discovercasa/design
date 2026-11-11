"""Stable product codes for the lines of the Listagem de material (Orçamentação, hub task 151, 2026-11-11).

The Listagem names its products in words that change (supplier text, notes, "a confirmar"); the price of a line is
found through its CODE instead: BOB/orcamentacao/ligacoes.json links each code to a material of the Hub's price list
(tables hub_*, read only). One code per DiscoverCasa product, the same in every house; the colour or the supplier is
not part of it (the link chooses the Hub material).

`codigo(capitulo, descricao, produto)` gives the code of one line of `gerar.linhas_material` (chapter "1".."8", "8m"
for the pergola timber, "7i" for the caixilharia items). A line the rules do not know gets "" and is listed by
`sem_codigo` (the reference houses must have none: BOB/orcamentacao/tests).
"""
import re

PRODUTOS = {
    # code: what it is (the product, not the supplier)
    "MAD-CASQ": "Madeira de casquinha branca seca, cortada à secção (módulos, amarração, madres, vigas)",
    "MAD-CASQ-22": "Casquinha branca 22x7,5 em peças compridas (madres)",
    "MAD-LAM": "Madeira lamelada 20x10 para interior (lameladas)",
    "MAD-LAM-AUT": "Madeira lamelada com tratamento autoclave (pilares e vigas da pérgola)",
    "MAD-AUT": "Madeira com tratamento autoclave em secção pequena (ripas da pérgola)",
    "FERR-BASE-PILAR": "Base metálica do pilar da pérgola",
    "VIGA-APOIO-COB": "Vigas de apoio à cobertura em casquinha 110x75",
    "OSB-09": "OSB3 9 mm",
    "OSB-15": "OSB3 15 mm",
    "OSB-22": "OSB3 22 mm (fundo da caleira oculta)",
    "MEMB-T95": "Membrana respirável Traspir 95",
    "RIPA-37x35": "Ripado 37,5x35 (viga 75x35 cortada ao meio)",
    "RIPA-30x20": "Ripado ou contra-ripado 30x20",
    "FORRO-TREMOLO": "Forro exterior Tremolo em Douglas marron 22x135",
    "XPS-60": "Isolamento XPS 60 mm",
    "CORTICA-60": "Aglomerado de cortiça expandida 60 mm (fachada)",
    "ETICS-REBOCO": "Reboco armado e acabamento do capoto (ETICS)",
    "LA-80": "Lã mineral 80 mm entre montantes (paredes)",
    "LA-100": "Lã mineral 100 mm (tetos e pavimentos entre pisos)",
    "PLADUR-13": "Placa de gesso cartonado 13 mm (Pladur N; H1 e F nas zonas próprias)",
    "FORRO-MAD-INT": "Forro de madeira interior",
    "AZULEJO": "Azulejo cerâmico 30x60 (paredes de WC e cozinha)",
    "BETONILHA": "Betonilha de regularização",
    "VINILICO": "Pavimento vinílico em régua",
    "CERAMICO-PAV": "Mosaico cerâmico 60x60 (pavimento)",
    "TETO-REGUA": "Régua de suspensão do teto falso",
    "TETO-PERFIL": "Perfil de teto TC-47",
    "TETO-CANTONEIRA": "Cantoneira perimetral 30x30 do teto",
    "PAINEL-5ONDAS-80": "Painel sandwich 5 ondas 80 mm (cobertura oculta)",
    "PAINEL-TELHA-40": "Painel sandwich imitação telha 40 mm (Munditelha)",
    "CALEIRA-OCULTA": "Caleira oculta em chapa (desenvolvimento 0,80 m)",
    "CALEIRA-BOCAL": "Bocal de saída da caleira",
    "CALEIRA": "Caleira exterior ou à vista",
    "TUBO-QUEDA": "Tubo de queda",
    "CUMEEIRA": "Remate de cumeeira",
    "REMATE-COB": "Remates da cobertura à vista na cor do painel (rincões, encostos)",
    "CALEIRA-LARO": "Caleira de laró (cobertura à vista)",
    "REMATE-TOPO": "Remate de topo e placa impermeável de topo (cobertura)",
    "CHAPEU-PLATIBANDA": "Chapéu de platibanda em chapa lacada",
    "CAIXILHARIA": "Caixilharia: janela, porta ou portão (por vão, com vidro e estore)",
    "REMATE-VAO-EXT": "Remate exterior dos vãos em alumínio quinado",
    "REMATE-VAO-INT": "Remate interior dos vãos em Pladur",
    "TELHA-CER": "Telha cerâmica (pérgola)",
    "RESUMO": "Linha de resumo: o preço está nas linhas de cada vão",
    # the house's data, for the parcels priced per m² (Orçamentação, 2026-11-11): not products, never priced
    "AREA-IMPLANTACAO": "Área de implantação (contorno da base de fundação)",
    "AREA-CONSTRUCAO": "Área de construção (implantação x número de pisos)",
}

# (chapters or None for any, the description starts with, code) — the first match wins; descriptions are the layer
# names of sistema_construtivo.json and camadas.py, with the finish option letter added by the engine, e.g. "(A)"
REGRAS = [
    (("7",), ("Aros e folhas", "Vidros", "Estores", "Portas e portão"), "RESUMO"),
    (("7i",), ("",), "CAIXILHARIA"),
    (None, ("Base metálica",), "FERR-BASE-PILAR"),
    (None, ("OSB 9",), "OSB-09"),
    (None, ("OSB 15",), "OSB-15"),
    (None, ("Membrana Traspir",), "MEMB-T95"),
    (None, ("Ripado 37,5x35",), "RIPA-37x35"),
    (None, ("Ripado 30x20", "Contra-ripado 30x20"), "RIPA-30x20"),
    (None, ("Forro Tremolo",), "FORRO-TREMOLO"),
    (None, ("Forro de madeira",), "FORRO-MAD-INT"),
    (None, ("XPS",), "XPS-60"),
    (None, ("Cortiça",), "CORTICA-60"),
    (None, ("Reboco",), "ETICS-REBOCO"),
    (None, ("Lã mineral Volcalis Comfort",), "LA-80"),
    (None, ("Lã mineral",), "LA-100"),
    (None, ("Pladur",), "PLADUR-13"),
    (None, ("Azulejo",), "AZULEJO"),
    (None, ("Betonilha",), "BETONILHA"),
    (None, ("Vinílico",), "VINILICO"),
    (None, ("Mosaico cerâmico",), "CERAMICO-PAV"),
    (None, ("Réguas de suspensão",), "TETO-REGUA"),
    (None, ("Perfis de teto",), "TETO-PERFIL"),
    (None, ("Cantoneira perimetral",), "TETO-CANTONEIRA"),
    (None, ("Vigas de apoio à cobertura",), "VIGA-APOIO-COB"),
    (None, ("Painel sandwich 5 ondas",), "PAINEL-5ONDAS-80"),
    (None, ("Painel sandwich",), "PAINEL-TELHA-40"),
    (None, ("Saída da caleira",), "CALEIRA-BOCAL"),
    (None, ("Caleira oculta",), "CALEIRA-OCULTA"),
    (None, ("Caleira de laró",), "CALEIRA-LARO"),
    (None, ("Caleira",), "CALEIRA"),
    (None, ("Tubo de queda",), "TUBO-QUEDA"),
    (None, ("Cumeeira",), "CUMEEIRA"),
    (None, ("Remate de rincão", "Remate de encosto"), "REMATE-COB"),
    (None, ("Remate de topo", "Placa impermeável de topo"), "REMATE-TOPO"),
    (None, ("Chapéu de platibanda",), "CHAPEU-PLATIBANDA"),
    (None, ("Remates exteriores dos vãos",), "REMATE-VAO-EXT"),
    (None, ("Remates interiores dos vãos",), "REMATE-VAO-INT"),
    (None, ("Telha",), "TELHA-CER"),
]

_SECCAO = re.compile(r"Madeira (\d+(?:,\d+)?)x(\d+(?:,\d+)?)")


def _madeira(capitulo, produto):
    """Timber lines ("Madeira 11x7,5", sections in cm) by chapter: the structure or the pergola."""
    m = _SECCAO.match(produto or "")
    if not m:
        return ""
    a, b = (float(x.replace(",", ".")) for x in m.groups())
    if capitulo == "8m":  # the pergola: glulam posts and beams, small battens
        return "MAD-LAM-AUT" if min(a, b) >= 7.5 else "MAD-AUT"
    if (a, b) in ((20, 10), (10, 20)):
        return "MAD-LAM"
    if (a, b) in ((22, 7.5), (7.5, 22)):
        return "MAD-CASQ-22"
    return "MAD-CASQ"


def codigo(capitulo, descricao, produto=""):
    """The code of one Listagem line, or "" when no rule knows it."""
    if capitulo in ("1", "8m") or (capitulo == "8" and (produto or "").startswith("Madeira ")):
        c = _madeira("8m" if capitulo.startswith("8") else capitulo, produto)
        if c:
            return c
    if (produto or "").startswith("Madeira OSB 22"):  # the hidden gutter's OSB deck, listed with the timber
        return "OSB-22"
    d = descricao or ""
    for caps, inicios, cod in REGRAS:
        if caps is not None and capitulo not in caps:
            continue
        if any(d.startswith(i) for i in inicios):
            return cod
    return ""


def areas(G):
    """[(code, description, m²)] of the house for the Listagem's «Dados da obra» lines: the foundation outline
    (G["fundacao"]["contorno"], the modules' outer faces) and that area times the number of floors."""
    pts = ((G.get("fundacao") or {}).get("contorno")) or G.get("contorno_estrutura") or []
    if len(pts) < 3:
        return []
    a = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2
    pisos = max(1, sum(1 for k in (G.get("niveis") or {}) if re.fullmatch(r"piso\d+", k)))
    return [("AREA-IMPLANTACAO", PRODUTOS["AREA-IMPLANTACAO"], round(a, 2)),
            ("AREA-CONSTRUCAO", PRODUTOS["AREA-CONSTRUCAO"] + f": {pisos} piso{'s' if pisos > 1 else ''}", round(a * pisos, 2))]


def sem_codigo(linhas):
    """The Listagem lines no rule knows: [(chapter, description, product)]."""
    return [(c, d, p) for c, d, p, *_ in linhas if not codigo(c, d, p)]
