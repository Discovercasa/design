"""Module divider: splits a wall of a DiscoverCasa house into its prefabricated modules, the company's way.
Pure Python (standard library) — the builder uses it, and the configurator will run the same code in the browser.

    python ferramentas/modelo/divisor_modulos.py --comparar "<project>/modelos/casa/modulos_D2503.json"

--comparar divides every wall of a company module drawing (read by modulos_dc.py) with the drawing's own wall
ends, openings and wall junctions, and compares the result with the company's modules.

The method (conhecimento/metodo-construtivo.md §2–§4; sistema-construtivo.md §2b — D2503 Módulos, Torres Vedras):
  - studs 35 at 40 cm clear: a bay = 0,435; a plain module = whole bays (exterior 5 = 2,21, interior 4 / 6 =
    1,78 / 2,65); a house-corner end is a 110x75;
  - every opening inside ONE module, between two jambs (110x75 exterior, 75x110 interior); the module round it is
    tight to a jamb, whole bays, or takes the wall's remainder;
  - openings too close for a pier share one module when it fits the preferred length (exterior 3,0, interior 2,75),
    or — two windows — are moved apart to a pier module (D2503 M13
    0,32; user 2026-10-20 "por defeito podes assumir que sim … desde que sejam duas janelas") when the shared module
    would pass the factory length; a door next to another opening stays put, in one module with it (to confirm);
  - factory modules up to 3 m (user 2026-10-20: "os módulos exteriores podem ir até 3 m"); longer only round an
    opening that needs it, built on site ("* Painel a executar em obra"), as short as the opening needs (user
    2026-10-20: "depende da situação mas neste caso sim usa o tamanho que o vão precisa");
  - no joint where another wall meets (that wall is fixed to an escada inside a module).
Where a wall leaves a choice (where the remainder goes, the margins round an opening) the cheapest split by the
costs of sistema_construtivo.json `estrutura.divisor` wins — our reading of D2503; the user leaves it to us (2026-10-20:
"Vai com a opção que achares melhor, força nisso confiança").

A wall: {"id", "exterior", "a", "b" (frame ends along the wall), "fim_a"/"fim_b" ("canto" = a house corner,
anything else = a plain stud), "aberturas": [[s0, s1, kind], ...] rough openings (kind "janela" — the default — or
"porta"), "juncoes": [[centre, thickness], ...]
walls meeting it}. Result: {"modulos": [{"s0", "s1", "comprimento", "tipo": "vao" | "liso" | "resto" | "pilar",
"vaos": [[s0, s1]], "vaos_grelha": bays or None, "obra": built on site}], "aberturas": the openings (moved if they
had to be), "avisos": [...], "custo"}.
"""
import argparse
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
EPS = 1e-6
MAX_LISOS = 4  # plain modules tried per stretch between two openings


def parametros(E, exterior):
    """Sizes and costs for one wall kind, from sistema_construtivo.json `estrutura`."""
    cls, D = E["exterior" if exterior else "interior"], E["divisor"]
    lado = "exterior" if exterior else "interior"
    return {"vao": E["vao_livre"] + cls["montante"], "montante": cls["montante"], "ombreira": cls["reforco"],
            "canto": cls["reforco"], "vaos_lisos": D["vaos_lisos"][lado], "vaos_min": D["vaos_min"],
            "preferido": D["comprimento_preferido"][lado], "max": D["comprimento_max"], "min": D["comprimento_min"],
            "pilar_min": D["pilar_min"], "folga_juncao": D["folga_juncao"], "tol": D["tolerancia"], "c": D["custos"]}


def vaos_inteiros(L, w0, w1, P):
    """Bays of 40 cm clear in a stretch L between end pieces w0 and w1 (0 = the stretch ends on a jamb), or None."""
    k = round((L - w0 - w1 + P["montante"]) / P["vao"])
    if k >= 1 and abs(L - (w0 + w1 - P["montante"] + k * P["vao"])) <= P["tol"]:
        return k
    return None


# ============================================================================ openings
def blocos(parede, P, avisos):
    """The openings with their jambs, in order: [[b0, b1, [openings], [kinds]]]. Openings closer than a pier share
    one block (one module) when it fits the factory length; else two windows are moved apart to a pier (user
    2026-10-20: "por defeito podes assumir que sim quando esta situação acontece desde que sejam duas janelas"), and a
    door next to another opening stays put in one module with them (to confirm); openings too close to a wall end
    are moved in."""
    J, a, b = P["ombreira"], parede["a"], parede["b"]
    # at a house corner the corner post stays beside the jamb; at another wall the jamb may end the module (D2503 M6)
    w_a = P["canto"] if parede.get("fim_a") == "canto" else 0.0
    w_b = P["canto"] if parede.get("fim_b") == "canto" else 0.0
    out = []
    for v in sorted(parede.get("aberturas", [])):
        s0, s1 = v[0], v[1]
        tipo = v[2] if len(v) > 2 else "janela"  # "janela" (incl. sliding windows to the floor) or "porta"
        if s0 - J < a + w_a - P["tol"]:
            d = a + w_a - (s0 - J)
            avisos.append(f"{parede['id']}: vão {s0:.3f}-{s1:.3f} afastado {d * 100:.1f} cm do topo da parede")
            s0, s1 = s0 + d, s1 + d
        if s1 + J > b - w_b + P["tol"]:
            d = s1 + J - (b - w_b)
            avisos.append(f"{parede['id']}: vão {s0:.3f}-{s1:.3f} afastado {d * 100:.1f} cm do topo da parede")
            s0, s1 = s0 - d, s1 - d
        bl = [s0 - J, s1 + J, [[s0, s1]], [tipo]]
        if out and bl[0] - out[-1][1] < P["pilar_min"] - P["tol"]:
            prev = out[-1]
            juntos = s0 - prev[2][-1][1] >= J - EPS  # room for one jamb post between them
            if bl[1] - prev[0] <= P["preferido"] + EPS and juntos:
                prev[1], prev[2], prev[3] = bl[1], prev[2] + bl[2], prev[3] + bl[3]  # one module, a shared post
                continue
            if juntos and "porta" in prev[3] + bl[3]:  # a door: kept where it is, one (longer) module for both
                avisos.append(f"{parede['id']}: porta junto a outro vão ({prev[2][-1][0]:.3f}-{prev[2][-1][1]:.3f} e "
                              f"{s0:.3f}-{s1:.3f}) — no mesmo módulo, a confirmar")
                prev[1], prev[2], prev[3] = bl[1], prev[2] + bl[2], prev[3] + bl[3]
                continue
            d = P["pilar_min"] - (bl[0] - prev[1])  # a pier module between them: each moves half
            avisos.append(f"{parede['id']}: vãos {prev[2][-1][0]:.3f}-{prev[2][-1][1]:.3f} e {s0:.3f}-{s1:.3f} "
                          f"afastados {d * 100:.1f} cm para um pilar de {P['pilar_min']:.2f}"
                          + ("" if "porta" not in prev[3] + bl[3] else " (com uma porta — a confirmar)"))
            prev[0] -= d / 2
            prev[1] -= d / 2
            prev[2] = [[v0 - d / 2, v1 - d / 2] for v0, v1 in prev[2]]
            bl = [bl[0] + d / 2, bl[1] + d / 2, [[s0 + d / 2, s1 + d / 2]], [tipo]]
        out.append(bl)
    return out


# ============================================================================ costs
def zonas_juncao(parede, P):
    return [(c - t / 2 - P["folga_juncao"], c + t / 2 + P["folga_juncao"]) for c, t in parede.get("juncoes", [])]


def junta_livre(s, zonas):
    return all(not (z0 < s < z1) for z0, z1 in zonas)


# The same plain modules and joints come up thousands of times while one wall is divided (every order of the same
# modules, every margin): their costs are kept for the wall being divided — exact keys, so nothing changes but the time
# (a 14,95 m wall with another wall meeting it: 1,6 s before). Cleared by dividir() for each wall.
_MEMO = {}


def _custo_liso_memo(s0, s1, parede, P, pilar):
    k = ("liso", s0, s1, pilar)
    if k not in _MEMO:
        _MEMO[k] = custo_liso(s0, s1, parede, P, pilar=pilar)
    return _MEMO[k]


def _junta_memo(s, zonas):
    k = ("junta", s)
    if k not in _MEMO:
        _MEMO[k] = junta_livre(s, zonas)
    return _MEMO[k]


def custo_liso(s0, s1, parede, P, pilar=False):
    """(cost, kind, bays, is_remainder) of a module without openings, or None if not allowed."""
    c, L = P["c"], s1 - s0
    w0 = P["canto"] if abs(s0 - parede["a"]) < EPS and parede.get("fim_a") == "canto" else P["montante"]
    w1 = P["canto"] if abs(s1 - parede["b"]) < EPS and parede.get("fim_b") == "canto" else P["montante"]
    if L > P["max"] + EPS:
        return None
    if L < P["min"] - EPS:
        if pilar and L >= P["pilar_min"] - P["tol"]:
            return c["modulo"] + c["pilar"], "pilar", None, False
        if not (abs(s0 - parede["a"]) < EPS and abs(s1 - parede["b"]) < EPS):  # a short wall is one module
            return None
    k = vaos_inteiros(L, w0, w1, P)
    longo = c["longo"] if L > P["preferido"] + EPS else 0.0
    if k is not None and k >= P["vaos_min"]:
        return c["modulo"] + (0.0 if k in P["vaos_lisos"] else c["vaos_outros"]) + longo, "liso", k, False
    custo = c["modulo"] + c["resto"] + c["resto_por_metro"] * L + longo
    if abs(s0 - parede["a"]) > EPS:
        custo += c["resto_fora_do_inicio"]  # the remainder rather at the start of the wall (D2503: 7 walls of 9)
    return custo, "resto", None, True


def custo_margem(m, w, P):
    """Cost of the stretch m between a module end (end piece w) and the jamb of its opening, or None."""
    if m <= P["tol"]:
        return 0.0
    if m < w - P["tol"]:
        return None  # no room for the module's end piece
    return P["c"]["margem_inteira"] if vaos_inteiros(m, w, 0.0, P) else P["c"]["margem_irregular"]


def custo_vao(x0, x1, bls, parede, P):
    """(cost, built on site) of a module [x0, x1] holding the opening blocks bls, or None."""
    c = P["c"]
    w0 = P["canto"] if abs(x0 - parede["a"]) < EPS and parede.get("fim_a") == "canto" else P["montante"]
    w1 = P["canto"] if abs(x1 - parede["b"]) < EPS and parede.get("fim_b") == "canto" else P["montante"]
    m0, m1 = custo_margem(bls[0][0] - x0, w0, P), custo_margem(x1 - bls[-1][1], w1, P)
    if m0 is None or m1 is None:
        return None
    L = x1 - x0
    if len(bls) > 1 and L > P["preferido"] + EPS:
        return None  # several openings share a module only within the factory length
    # what the opening itself needs: its block, and the corner post when the module reaches a house corner
    preciso = (bls[-1][1] - bls[0][0]) + (w0 if w0 > P["montante"] else 0.0) * (abs(x0 - parede["a"]) < EPS) + \
        (w1 if w1 > P["montante"] else 0.0) * (abs(x1 - parede["b"]) < EPS)
    custo, obra = c["modulo"] + m0 + m1, False
    if L > P["max"] + EPS:
        if preciso <= P["max"] + EPS:
            return None
        custo += c["obra"] + c["obra_por_metro"] * max(0.0, L - preciso)  # built on site, kept as short as it can
        obra = True
    elif L > P["preferido"] + EPS:
        custo += c["longo"]
    return custo, obra


# ============================================================================ stretches between openings
def arranjos(x0, x1, esq, dir_, parede, P, zonas):
    """Ways to fill the stretch [x0, x1] between an opening block on the left (esq) and one on the right (dir_), or
    a wall end: [(mL, mR, plain modules [(s0, s1, cost, kind, bays)], cost, remainders)] — mL / mR: the part taken by
    the opening module on that side."""
    g = x1 - x0
    if g < -P["tol"]:
        return []
    g = max(g, 0.0)  # a jamb within the tolerance of the wall end
    v, mt = P["vao"], P["montante"]

    def margens(lado):
        if not lado:
            return [0.0]
        out, k = [0.0], 1
        while k * v <= g + P["tol"]:
            out.append(k * v)
            k += 1
        return out

    # plain modules: whole bays between two studs; at a house corner the end module ends on the 110x75 corner post
    inteiros = [round(mt + k * v, 4) for k in range(P["vaos_min"], 8) if mt + k * v <= P["max"] + EPS]
    grandes = [c for c in inteiros if c >= mt + 4 * v - EPS] or inteiros  # long stretches: modules of 4+ bays
    de_canto = [round(P["canto"] + k * v, 4) for k in range(P["vaos_min"], 8) if P["canto"] + k * v <= P["max"] + EPS]
    inicios = [()] + [(c,) for c in de_canto] if not esq and parede.get("fim_a") == "canto" else [()]
    fins = [()] + [(c,) for c in de_canto] if not dir_ and parede.get("fim_b") == "canto" else [()]
    com_juncoes = any(x0 < z1 and z0 < x1 for z0, z1 in zonas)
    res = []
    vistos = set()
    for mL in margens(esq):
        for mR in margens(dir_):
            for ini in inicios:
                for fim in fins:
                    livre = g - mL - mR - sum(ini) - sum(fim)
                    if livre < -P["tol"]:
                        continue
                    # a module costs more than any other choice: only the fewest that can fill it, and one more
                    n_lo = max(0, -int(-(livre - P["max"]) // max(inteiros)))
                    n_max = int(max(livre, 0.0) // min(grandes)) + 1
                    for n in range(n_lo, min(n_max, n_lo + 2) + 1):
                        for multi in itertools.combinations_with_replacement(inteiros if n <= MAX_LISOS else grandes, n):
                            resto = livre - sum(multi)
                            if resto < -P["tol"]:
                                continue
                            for meio in _ordens(multi, com_juncoes):
                                res += _montar(x0, x1, mL, mR, ini + meio + fim, resto, esq, dir_, parede, P, zonas,
                                               vistos)
    melhores = {}  # the DP only needs the cheapest filling for each pair of margins (and remainder count)
    for op in res:
        chave = (round(op[0], 4), round(op[1], 4), min(op[4], 2))
        if chave not in melhores or op[3] < melhores[chave][3] - EPS:
            melhores[chave] = op
    return list(melhores.values())


def _ordens(multi, com_juncoes):
    """Orders to try for a set of plain modules. Without a wall meeting the stretch the order changes nothing (one
    order); with one, every order for a few modules, else the rotations both ways (to move a joint off it)."""
    if len(multi) <= 1 or not com_juncoes:
        return [tuple(multi)]
    if len(multi) <= MAX_LISOS:
        return set(itertools.permutations(multi))
    asc = tuple(multi)
    out = set()
    for base in (asc, asc[::-1]):
        for r in range(len(base)):
            out.add(base[r:] + base[:r])
    return out


def _montar(x0, x1, mL, mR, ordem, resto, esq, dir_, parede, P, zonas, vistos):
    """The variants of one choice of margins and plain modules: the remainder (if any) as its own module at either
    end, or taken by the left or right opening module."""
    out = []
    variantes = []
    if resto <= P["tol"]:
        variantes.append((mL, mR, None))
    else:
        if esq:
            variantes.append((mL + resto, mR, None))
        if dir_:
            variantes.append((mL, mR + resto, None))
        variantes += [(mL, mR, "inicio"), (mL, mR, "fim")]  # custo_liso says whether it may stand alone
    for ml, mr, onde in variantes:
        comps = list(ordem)
        if onde == "inicio":
            comps = [resto] + comps
        elif onde == "fim":
            comps = comps + [resto]
        chave = (ml, mr, tuple(comps))  # exact: a twin differing by float noise only costs a little time, never the result
        if chave in vistos:
            continue
        vistos.add(chave)
        s, mods, custo, nresto, ok = x0 + ml, [], 0.0, 0, True
        if (esq and not _junta_memo(s, zonas)) or (dir_ and not _junta_memo(x1 - mr, zonas)):
            continue
        for L in comps:
            e = s + L
            if abs(e - (x1 - mr)) < 2 * P["tol"]:
                e = x1 - mr
            if e < x1 - mr - EPS and not _junta_memo(e, zonas):
                ok = False
                break
            pilar = esq and dir_ and len(comps) == 1 and ml <= P["tol"] and mr <= P["tol"]  # between two tight jambs
            cl = _custo_liso_memo(s, e, parede, P, pilar)
            if cl is None:
                ok = False
                break
            custo += cl[0]
            nresto += cl[3]
            mods.append((s, e, cl[0], cl[1], cl[2]))
            s = e
        if ok and abs(s - (x1 - mr)) <= 2 * P["tol"]:
            out.append((ml, mr, mods, custo, nresto))
    return out


# ============================================================================ the wall
def dividir(parede, P):
    """Split one wall into modules (see the module docstring)."""
    _MEMO.clear()
    avisos = []
    a, b = parede["a"], parede["b"]
    zonas = zonas_juncao(parede, P)
    bls = blocos(parede, P, avisos)
    for c_, t_ in parede.get("juncoes", []):
        if any(v0 < c_ + t_ / 2 and c_ - t_ / 2 < v1 for bl in bls for v0, v1 in bl[2]):
            avisos.append(f"{parede['id']}: uma parede encontra-a sobre um vão (em {c_:.2f})")
    c = P["c"]

    def com_restos(estado_resto, n):
        """Extra cost of n more remainder modules in a wall that already has one (estado_resto) or not."""
        if n == 0:
            return 0.0
        return c["resto_extra"] * (n if estado_resto else n - 1)

    if not bls:
        melhor = None
        for _, _, mods, custo, n in arranjos(a, b, False, False, parede, P, zonas):
            t = custo + com_restos(False, n)
            if melhor is None or t < melhor[0] - EPS:
                melhor = (t, mods)
        if melhor is None:
            raise ValueError(f"{parede['id']}: sem divisão possível")
        return _resultado(melhor[1], [], bls, melhor[0], avisos)

    # states: (start of the open opening module, index of its first block, has a remainder) -> (cost, modules)
    estados = {}
    for _, mR, mods, custo, n in arranjos(a, bls[0][0], False, True, parede, P, zonas):
        chave = (round(bls[0][0] - mR, 4), 0, n > 0)
        t = custo + com_restos(False, n)
        if chave not in estados or t < estados[chave][0] - EPS:
            estados[chave] = (t, list(mods))
    for i in range(len(bls)):
        ultimo = i == len(bls) - 1
        x0, x1 = bls[i][1], (b if ultimo else bls[i + 1][0])
        ops = arranjos(x0, x1, True, not ultimo, parede, P, zonas)
        novos = {}
        for (xs, i0, tem_resto), (custo0, mods0) in estados.items():
            if not ultimo:  # or the next opening in the same module (custo_vao judges its length when it closes)
                chave = (xs, i0, tem_resto)
                if chave not in novos or custo0 < novos[chave][0] - EPS:
                    novos[chave] = (custo0, mods0)
            for mL, mR, mods, custo, n in ops:
                xe = x0 + mL
                cv = custo_vao(xs, xe, bls[i0:i + 1], parede, P)
                if cv is None:
                    continue
                t = custo0 + cv[0] + custo + com_restos(tem_resto, n)
                modulo = (xs, xe, cv[0], "vao", None, bls[i0:i + 1], cv[1])
                chave = ("fim",) if ultimo else (round(x1 - mR, 4), i + 1, tem_resto or n > 0)
                if chave not in novos or t < novos[chave][0] - EPS:
                    novos[chave] = (t, mods0 + [modulo] + list(mods))
        estados = novos
    if ("fim",) not in estados:
        raise ValueError(f"{parede['id']}: sem divisão possível (vãos {[(round(x[0], 2), round(x[1], 2)) for x in bls]})")
    custo, mods = estados[("fim",)]
    return _resultado(mods, [v for bl in bls for v in bl[2]], bls, custo, avisos)


def _resultado(mods, aberturas, bls, custo, avisos):
    out = []
    for m in mods:
        s0, s1, _, tipo, k = m[:5]
        d = {"s0": round(s0, 4), "s1": round(s1, 4), "comprimento": round(s1 - s0, 4), "tipo": tipo, "vaos": [],
             "vaos_grelha": k, "obra": False}
        if tipo == "vao":
            d["vaos"] = [[round(v0, 4), round(v1, 4)] for bl in m[5] for v0, v1 in bl[2]]
            d["obra"] = m[6]
        out.append(d)
    return {"modulos": out, "aberturas": [[round(v0, 4), round(v1, 4)] for v0, v1 in aberturas], "avisos": avisos,
            "custo": round(custo, 3)}


def juntas(resultado):
    """Module joints of a divided wall, from start to end (as casa_planta.juntas returns them)."""
    ms = resultado["modulos"]
    return [ms[0]["s0"]] + [m["s1"] for m in ms]


# ============================================================================ check against a company drawing
def paredes_do_desenho(modulos):
    """The walls of a company module drawing (modulos_dc.py JSON): ends, openings and junctions as drawn."""
    grupos = defaultdict(list)
    for m in modulos:
        x0, x1, y0, y1 = m["pegada"]
        s0, s1, c0, c1 = (x0, x1, y0, y1) if m["eixo"] == "x" else (y0, y1, x0, x1)
        grupos[(m["tipo"] == "exterior", m["eixo"], round((c0 + c1) / 2, 2))].append((s0, s1, c0, c1, m))
    paredes = []
    for (ext, eixo, _), ms in grupos.items():
        ms.sort(key=lambda t: t[0])
        corridas = [[ms[0]]]
        for t in ms[1:]:
            (corridas.append([t]) if t[0] - corridas[-1][-1][1] > 0.05 else corridas[-1].append(t))
        for cr in corridas:
            f0, f1 = min(t[2] for t in cr), max(t[3] for t in cr)
            fim = "canto" if ext else "parede"
            paredes.append({"id": "+".join(t[4]["nome"] for t in cr), "exterior": ext, "eixo": eixo,
                            "c": (f0 + f1) / 2, "f0": f0, "f1": f1, "a": cr[0][0], "b": cr[-1][1],
                            "fim_a": fim, "fim_b": fim, "juncoes": [],
                            "aberturas": [[round(t[0] + o["u"][0], 4), round(t[0] + o["u"][1], 4)]
                                          for t in cr for o in t[4]["aberturas"]],
                            "desenho": [(t[0], t[1], t[4]["nome"]) for t in cr]})
    for w in paredes:
        for q in paredes:
            if q is w or q["eixo"] == w["eixo"] or not (w["a"] + 0.2 < q["c"] < w["b"] - 0.2):
                continue
            if any(abs(s - f) < 0.05 for s in (q["a"], q["b"]) for f in (w["f0"], w["f1"])):
                w["juncoes"].append([round(q["c"], 4), round(q["f1"] - q["f0"], 4)])
    return paredes


def classificar(mods, parede, P):
    """Judge any split of a wall [(s0, s1)] by the divider's rules: {kind: count} and the total cost."""
    bls = [(v0 - P["ombreira"], v1 + P["ombreira"]) for v0, v1 in sorted(parede.get("aberturas", []))]
    zonas = zonas_juncao(parede, P)
    n = defaultdict(int)
    custo = 0.0
    for i, (s0, s1) in enumerate(mods):
        dentro = [bl for bl in bls if s0 - P["tol"] <= bl[0] and bl[1] <= s1 + P["tol"]]
        if any(bl[0] < s1 - P["tol"] and s0 + P["tol"] < bl[1] for bl in bls if bl not in dentro):
            n["vão cortado por uma junta"] += 1
        if i and not junta_livre(s0, zonas):
            n["junta onde encontra outra parede"] += 1
        if dentro:
            cv = custo_vao(s0, s1, [[b0, b1, []] for b0, b1 in dentro], parede, P)
            w0 = P["canto"] if abs(s0 - parede["a"]) < EPS and parede.get("fim_a") == "canto" else P["montante"]
            w1 = P["canto"] if abs(s1 - parede["b"]) < EPS and parede.get("fim_b") == "canto" else P["montante"]
            for m, w in ((dentro[0][0] - s0, w0), (s1 - dentro[-1][1], w1)):
                c = custo_margem(m, w, P)
                n["margem justa" if c == 0.0 else "margem em vãos inteiros" if c == P["c"]["margem_inteira"]
                  else "margem irregular"] += 1
            n["módulo com vão"] += 1
            n["montado em obra"] += bool(cv and cv[1])
            custo += cv[0] if cv else 99.0
        else:
            pilar = 0 < i < len(mods) - 1 and s1 - s0 < P["min"]
            cl = custo_liso(s0, s1, parede, P, pilar=pilar)
            n[{"liso": "liso em vãos inteiros", "resto": "sobra", "pilar": "pilar"}[cl[1]] if cl else "fora das regras"] += 1
            custo += cl[0] if cl else 99.0
        if s1 - s0 > P["preferido"] + EPS:
            n["mais comprido que o preferido"] += 1
    return dict(n), custo


def svg_comparacao(linhas, caminho):
    """Each wall twice — the company's modules and the divider's — as a picture (SVG)."""
    k, x0, alt, passo = 46.0, 210.0, 22.0, 78.0
    larg = x0 + max(w["b"] - w["a"] for w, _, _ in linhas) * k + 40
    cores = {"liso": "#CFE8C8", "resto": "#F6C38B", "vao": "#BFD6F2", "pilar": "#E0E0E0"}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{larg:.0f}" height="{passo * len(linhas) + 70:.0f}" '
           f'font-family="Arial" font-size="11"><rect width="100%" height="100%" fill="white"/>',
           '<text x="10" y="20" font-size="14" font-weight="bold">Divisor de módulos vs D2503 Módulos (Torres Vedras)</text>',
           '<text x="10" y="38">verde = liso em vãos inteiros · laranja = sobra · azul = com vão (branco = vão em bruto) · '
           'cinza = pilar · traço vermelho = parede que encontra · * = montado em obra</text>']
    y = 60.0
    for w, des, div in linhas:
        out.append(f'<text x="10" y="{y + 15:.0f}" font-weight="bold">{"Exterior" if w["exterior"] else "Interior"} '
                   f'{w["eixo"]} = {w["c"]:.2f}</text><text x="10" y="{y + 29:.0f}" fill="#555">{w["id"][:30]}</text>')
        for fila, (rot, mods) in enumerate((("D2503", des), ("divisor", div))):
            yy = y + fila * (alt + 4)
            out.append(f'<text x="{x0 - 8:.0f}" y="{yy + 15:.0f}" text-anchor="end">{rot}</text>')
            for s0, s1, tipo, obra in mods:
                xa, xb = x0 + (s0 - w["a"]) * k, x0 + (s1 - w["a"]) * k
                out.append(f'<rect x="{xa:.1f}" y="{yy:.1f}" width="{xb - xa:.1f}" height="{alt}" fill="{cores[tipo]}" '
                           f'stroke="#333" stroke-width="1"/>')
                for v0, v1 in w["aberturas"]:
                    if s0 - 0.01 <= v0 and v1 <= s1 + 0.01:
                        out.append(f'<rect x="{x0 + (v0 - w["a"]) * k:.1f}" y="{yy + 4:.1f}" width="{(v1 - v0) * k:.1f}" '
                                   f'height="{alt - 8}" fill="white" stroke="#555" stroke-dasharray="2,2"/>')
                out.append(f'<text x="{(xa + xb) / 2:.1f}" y="{yy + 15:.1f}" text-anchor="middle">'
                           f'{s1 - s0:.2f}{"*" if obra else ""}</text>')
        for c, _ in w["juncoes"]:
            xc = x0 + (c - w["a"]) * k
            out.append(f'<line x1="{xc:.1f}" y1="{y - 3:.1f}" x2="{xc:.1f}" y2="{y + 2 * alt + 7:.1f}" stroke="red" stroke-width="2"/>')
        y += passo
    out.append("</svg>")
    Path(caminho).write_text("\n".join(out), encoding="utf-8")


def comparar(caminho, E, svg=None):
    modulos = json.load(open(caminho, encoding="utf-8"))["modulos"]
    paredes = paredes_do_desenho(modulos)
    tot = {"modulos_desenho": 0, "modulos_divisor": 0, "iguais": 0, "juntas_desenho": 0, "juntas_iguais": 0}
    regras = {"desenho": defaultdict(int), "divisor": defaultdict(int)}
    custos = {"desenho": 0.0, "divisor": 0.0}
    linhas = []
    paredes.sort(key=lambda w: (not w["exterior"], w["eixo"], w["c"]))
    for w in paredes:
        P = parametros(E, w["exterior"])
        r = dividir(w, P)
        des = [(s0, s1) for s0, s1, _ in w["desenho"]]
        div = [(m["s0"], m["s1"]) for m in r["modulos"]]
        for qual, mods in (("desenho", des), ("divisor", div)):
            n, c = classificar(mods, w, P)
            custos[qual] += c
            for t, q in n.items():
                regras[qual][t] += q
        tipos_d = []
        for i, (s0, s1) in enumerate(des):
            tem = any(s0 - 0.01 <= o[0] and o[1] <= s1 + 0.01 for o in w["aberturas"])
            cl = None if tem else custo_liso(s0, s1, w, P, pilar=0 < i < len(des) - 1 and s1 - s0 < P["min"])
            tipos_d.append((s0, s1, "vao" if tem else (cl[1] if cl else "resto"), s1 - s0 > P["max"] + EPS))
        linhas.append((w, tipos_d, [(m["s0"], m["s1"], m["tipo"], m["obra"]) for m in r["modulos"]]))
        jd = [s1 for _, s1 in des[:-1]]
        jv = [s1 for _, s1 in div[:-1]]
        iguais = sum(any(abs(d0 - v0) < 0.02 and abs(d1 - v1) < 0.02 for v0, v1 in div) for d0, d1 in des)
        ji = sum(any(abs(j - k) < 0.02 for k in jv) for j in jd)
        tot["modulos_desenho"] += len(des)
        tot["modulos_divisor"] += len(div)
        tot["iguais"] += iguais
        tot["juntas_desenho"] += len(jd)
        tot["juntas_iguais"] += ji
        print(f"\n{'EXT' if w['exterior'] else 'INT'} {w['eixo']} {w['c']:.2f}  {w['a']:.3f}-{w['b']:.3f}  ({w['id']})"
              f"  vãos {len(w['aberturas'])}  junções {len(w['juncoes'])}")
        print("  desenho: " + "  ".join(f"{s1 - s0:.2f}{'v' if any(s0 - 0.01 <= o[0] and o[1] <= s1 + 0.01 for o in w['aberturas']) else ''}"
                                         for s0, s1 in des))
        print("  divisor: " + "  ".join(f"{m['comprimento']:.2f}{'v' if m['tipo'] == 'vao' else 'r' if m['tipo'] == 'resto' else 'p' if m['tipo'] == 'pilar' else ''}"
                                         f"{'*' if m['obra'] else ''}" for m in r["modulos"])
              + f"   módulos iguais {iguais}/{len(des)}, juntas iguais {ji}/{len(jd)}")
        for a_ in r["avisos"]:
            print("  aviso:", a_)
    print(f"\nTOTAL módulos: desenho {tot['modulos_desenho']}, divisor {tot['modulos_divisor']}; iguais "
          f"{tot['iguais']}/{tot['modulos_desenho']}; juntas iguais {tot['juntas_iguais']}/{tot['juntas_desenho']}")
    print("(v = com vão, r = sobra, p = pilar, * = montado em obra)")
    print("\nRegras (contagem)                     desenho  divisor")
    for t in sorted(set(regras["desenho"]) | set(regras["divisor"])):
        print(f"  {t:<36}{regras['desenho'][t]:>7}  {regras['divisor'][t]:>7}")
    print(f"  {'custo total (menor = mais regular)':<36}{custos['desenho']:>7.1f}  {custos['divisor']:>7.1f}")
    if svg:
        svg_comparacao(linhas, svg)
        print("svg:", svg)
    return tot


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--comparar", required=True, help="module drawing JSON (modulos_dc.py)")
    ap.add_argument("--svg", help="also draw every wall, company vs divider, into this SVG file")
    a = ap.parse_args()
    S = json.load(open(AQUI / "sistema_construtivo.json", encoding="utf-8"))
    comparar(a.comparar, S["estrutura"], a.svg)


if __name__ == "__main__":
    main()
