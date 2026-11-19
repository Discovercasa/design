"""The «Compra» column of the Listagem de material: every line in the unit the company buys it in (user 2026-11-19:
"utiliza a secção de compra que criaste no documento como referência para cada produto").

Where it comes from:
- BOB/orcamentacao/ligacoes.json: the line's product code -> the Hub material, its price unit and how the line's
  quantity becomes it (the same conversion as public/js/orcamento.js `quantidade()`);
- the Hub material's own size (a roll of 10 x 1,2 m, a 2500x1250 plate, a 3 m bar, timber in 230x78 boards), from a
  LOCAL copy of the Hub's materials, BOB/_trabalho/hub/materiais.json (git-ignored: the Hub's names never go in this
  public repo; written from the Design Supabase tables hub_materiais / hub_material_precos by Claude).
Without the copy (the browser, another PC) the standard's purchase units stay and the rest is left as before.
A purchase the standard already gives (plates, rolls of membrane, boards of Tremolo, bars of angle) is kept as it is:
the Orçamentação converts those lines from it.

Timber: the company's sections are cut from casquinha branca 230x78 boards (the Hub's casquinha is that board, sold
per m³; a normal stock up to 5,70 m and a longer one over 6 m), so the purchase is the volume of 230x78 board those pieces
need: per 230x78 section 4 × 11x3,5, 6 × 7,5x3,5, 2 × 11x7,5, 1 × 22x7,5, 12 × 3,75x3,5 (ripado: 7,5x3,5 cut in half)
— the cutting yield is OUR reading of the sections (to confirm); the length offcuts are not counted.
"""
import json
import math
import re
from pathlib import Path

BOB = Path(__file__).resolve().parents[2]
LIGACOES = BOB / "orcamentacao" / "ligacoes.json"
MATERIAIS = BOB / "_trabalho" / "hub" / "materiais.json"
TABUA = (0.23, 0.078)          # the casquinha board the sections are cut from (m)
TABUA_MAX = 5.70               # longest board of the normal stock; longer pieces need the long (over 6 m) stock
RENDIMENTO = {(110, 35): 4, (75, 35): 6, (110, 75): 2, (220, 75): 1, (37.5, 35): 12}
CASQUINHA = ("MAD-CASQ", "MAD-CASQ-22", "RIPA-37x35", "VIGA-APOIO-COB")


def carregar():
    """(links, materials): {} when the files are not there (the browser, a PC without the local copy)."""
    lig, mat = {}, {}
    try:
        lig = json.load(open(LIGACOES, encoding="utf-8"))["ligacoes"]
    except (OSError, ValueError, KeyError):
        pass
    try:
        mat = json.load(open(MATERIAIS, encoding="utf-8"))["materiais"]
    except (OSError, ValueError, KeyError):
        pass
    return lig, mat


def fmt(v, casas=2):
    s = f"{v:.{casas}f}".rstrip("0").rstrip(".")
    return (s or "0").replace(".", ",")


def seccao_mm(texto):
    """'Madeira 11x3,5' / 'Ripado 37,5x35' -> (110, 35) / (37.5, 35) in mm, or None."""
    m = re.search(r"(\d+(?:,\d+)?)x(\d+(?:,\d+)?)", texto or "")
    if not m:
        return None
    a, b = (float(x.replace(",", ".")) for x in m.groups())
    if texto.lstrip().startswith("Madeira"):  # the Listagem writes timber in cm
        a, b = a * 10, b * 10
    return (round(a, 1), round(b, 1))


def tabua_m3(seccao, comprimento):
    """m³ of 230x78 board the pieces of a section need (cutting yield above), or None for a section not cut from it."""
    k = RENDIMENTO.get(tuple(sorted(seccao, reverse=True))) if seccao else None
    if not k:
        return None
    return comprimento * TABUA[0] * TABUA[1] / k


def _quantidade(q, n, L, A, V):
    """As public/js/orcamento.js quantidade(): the line's quantity in the Hub price unit, or None."""
    base = q.get("base")
    v = {"area": A, "comprimento": L, "pecas": n}.get(base)
    if base == "volume":
        v = V or (L * q["seccao_m2"] if q.get("seccao_m2") and L else None)
    if not v or v <= 0 or ("divisor" in q and not q["divisor"]):
        return None
    v = v * q.get("fator", 1) / (q.get("divisor") or 1)
    return math.ceil(v - 1e-9) if q.get("arredondar") else v


def _preco(m, unidade):
    rows = (m or {}).get("precos") or []
    return next((p for p in rows if p.get("unidade") == unidade), rows[0] if rows else {})


def compra(cod, desc, prod, n, L, A, V, q, u, lig, mat):
    """(purchase qty, purchase unit, reference = the Hub material bought) of one Listagem line."""
    ln = lig.get(cod) or {}
    if ln.get("resumo"):
        return q, u, ""
    m = mat.get(ln.get("hub") or "")
    ref = (m or {}).get("nome", "") if ln.get("hub") else ("não está na lista do Hub" if cod in lig else "")
    if cod in CASQUINHA:
        sec = seccao_mm(prod if (prod or "").startswith("Madeira") else desc)
        t = tabua_m3(sec, L) if L else None
        if t:
            return round(math.ceil(t * 100 - 1e-9) / 100, 2), "m3 tábua 230x78", ref
    if q != "" and q is not None:
        return q, u, ref
    if not ln.get("hub"):
        if L:
            return math.ceil(L - 1e-9), "m", ref
        if A:
            return math.ceil(A - 1e-9), "m2", ref
        return (n, "un", ref) if n else ("", "", ref)
    un = ln.get("unidade", "")
    v = _quantidade(ln.get("quantidade") or {}, n, L, A, V)
    if v is None:
        return "", "", ref
    p = _preco(m, un)
    c, w = p.get("comprimento"), p.get("largura")
    if un == "m2" and c and w:
        k = math.ceil(v / (c * w) - 1e-9)
        nome = "rolo" if c >= 5 else ("barra" if w < 0.5 else "placa")
        return k, f"{nome} {fmt(c)} x {fmt(w)} m", ref
    if un in ("ml", "un") and c and c < 20 and not ln["quantidade"].get("divisor"):
        k = math.ceil(v / c - 1e-9) if un == "ml" else math.ceil(v - 1e-9)
        return k, f"barra {fmt(c)} m" if un == "ml" else "un", ref
    if un == "un":
        return math.ceil(v - 1e-9), (f"barra {fmt(c)} m" if c and c < 20 else "un"), ref
    if un == "m3":
        return round(math.ceil(v * 100 - 1e-9) / 100, 2), "m3", ref
    return math.ceil(v * 10 - 1e-9) / 10, un, ref


def totais_madeira(pecas, mat=None, lig=None):
    """Timber totals by section (user 2026-11-19: "madeira total de 22x7,5, madeira total de 11x7,5 …"):
    [(section, pieces, length m, volume m³, board m³ or None, pieces longer than 5,70 m)]."""
    t = {}
    for _g, sec, L, vol, _tp in pecas:
        r = t.setdefault(sec, [0, 0.0, 0.0, 0.0, 0])
        r[0] += 1
        r[1] += L
        r[2] += vol
        a, b = (float(x) for x in sec.lower().split("x"))
        tb = tabua_m3((a, b), L)
        r[3] = None if tb is None or r[3] is None else r[3] + tb
        r[4] += L > TABUA_MAX and tb is not None   # glulam comes in 13,5 m: the 5,70 m board limit is the casquinha's
    return [(sec, r[0], r[1], r[2], r[3], r[4]) for sec, r in t.items()]
