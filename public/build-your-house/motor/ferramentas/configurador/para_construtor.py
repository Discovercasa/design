"""A house built in the configurator -> the builder's inputs (planta_paredes.json + config.json). Pure Python.

    python ferramentas/configurador/para_construtor.py "<house>.json" --saida <folder> [--construir] [--documentos]

The configured house (format "discovercasa-configurador/1", configurador/docs/especificacao.md §2) holds what the
client chose — the foundation outline, the 3 m walls along it, the openings, the interior walls, the roof and the
finishes. This turns it into the same inputs an architecture plan gives the builder (casa_planta.py), so a configured
house goes through the whole chain: module division (divisor_modulos.py), layers, quantities, the production
documents (Módulos, Cobertura, Listagem de material). How it is built is always the DiscoverCasa method
(conhecimento/metodo-construtivo.md); the client never sees the modules.

--construir runs casa_planta.py + camadas.py (no Blender) and prints the modules; --documentos also runs gerar.py.
The 3D model: python ferramentas/modelo/construir_casa.py "<folder>/config.json".

Configured house:
  "base": {"forma": "L", "contorno": [[x, y], ...]}  outline of the foundation = the modules' outer faces, right
      angles only, counter-clockwise; side i runs from point i to point i + 1
  "paredes_exteriores": [{"lado": i, "s0": 0.0, "s1": 3.0}, ...]  the client's walls (3 m, the last one of a side
      the rest — user 2026-10-20), measured from the start of side i; they must cover every side
  "vaos": [{"lado": i, "tipo": "janela" | "janela_correr" | "basculante" | "fixo" | "porta" | "portao",
      "centro": distance from the start of the side, "largura", "altura" (the frame), "peitoril" (windows: frame
      bottom above the floor), "estore": true/false (windows only — user 2026-10-27 "Prtas não tem estore apenas
      as janelas"), "divisao": room name}]
  "paredes_interiores": [{"de": [x, y], "ate": [x, y], "portas": [{"centro": distance from "de"}]}]  centre lines
  "cobertura": {"tipo": "escondida"}   hidden behind a parapet, or {"tipo": "duas_aguas" | "quatro_aguas" | "misto"
      (the main body hipped, the wings' ends in empenas — L / T / U),
      "inclinacao_pct": 15 (at least 15 % — user 2026-10-21), "beirado": 0.25} exposed in sandwich panel
  "acabamentos": {"exterior": "A" | "B" | "C", "contra_ripado": true, "interior": "pladur" | "madeira" | "ceramico",
      "pavimento": "vinilico" | "ceramico"}  (interior and floor kept in the config; the layers still use Pladur / vinyl)
  "exteriores": {"pergolas": [{"lado": i, "s0", "s1" (along side i), "projecao" (from the finished facade),
      "altura" (the beams' underside at the facade; none = the highest allowed)}]}   step 7 (user 2026-10-29); a
      separate garage / annex is a configured house of its own (the configurator keeps it with its place)
  "pe_direito": 2.50   the clear height, the client's choice (user 2026-10-21: "A altura não temos fixa o cliente
      pode escolher a vontade o que preferir"); 2,50 = the default (Torres Vedras); not below 2,40 (RGEU)
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.configurador.formas import area  # noqa: E402
from ferramentas.modelo import telhado as telhado_av  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
MODELO = RAIZ / "ferramentas" / "modelo"
ESP_EXT, ESP_INT = 0.25, 0.14  # wall thickness in the plan (only the outer face counts: "face_exterior")
PE_MIN, PE_MAX = 2.40, 3.50  # the clear height: RGEU art. 65 minimum; the configurator's guard (ours — rulebook §13)
LIMITE_VIGAS = 8.0  # ceiling beams 22x7,5 up to 8 m, glulam beyond (user 2026-10-15 "O nosso limite é precisamente 8 metros")
TIPOS = {"janela": ("basculante", "Janela"), "janela_correr": ("correr", "Janela de correr 2 folhas"),
         # 3 and 4 leaves (user 2026-10-22: "janelas de correr mas 3 janelas e 4 janelas")
         "janela_correr_3": ("correr", "Janela de correr 3 folhas"), "janela_correr_4": ("correr", "Janela de correr 4 folhas"),
         "basculante": ("basculante", "Basculante"), "fixo": ("fixo", "Vidro fixo"),
         "porta": ("porta", "Porta painel liso"), "portao": ("seccionado", "Portão de garagem seccionado automático")}
ATE_AO_CHAO = {"janela_correr", "janela_correr_3", "janela_correr_4", "porta", "portao"}
NOME_FACE = {("x", -1): "norte", ("x", 1): "sul", ("y", 1): "poente", ("y", -1): "nascente"}  # an outside wall's inner
# face by the way it looks (eixo, "fora"): the south wall's inner face looks north


class Erro(ValueError):
    pass


# ============================================================================ geometry
def lados(cont):
    """The sides of the outline: [{"i", "p0", "p1", "eixo", "sentido" (+1/-1 along the axis), "c" (line), "s0",
    "s1" (extent), "fora" (+1/-1: the outside, across the axis)}]."""
    out = []
    n = len(cont)
    for i in range(n):
        (x0, y0), (x1, y1) = cont[i], cont[(i + 1) % n]
        if abs(y1 - y0) < 1e-6:  # along X; counter-clockwise: the outside is to the right of the direction
            sg = 1 if x1 > x0 else -1
            out.append({"i": i, "p0": (x0, y0), "p1": (x1, y1), "eixo": "x", "sentido": sg, "c": y0,
                        "s0": min(x0, x1), "s1": max(x0, x1), "fora": -sg})
        elif abs(x1 - x0) < 1e-6:
            sg = 1 if y1 > y0 else -1
            out.append({"i": i, "p0": (x0, y0), "p1": (x1, y1), "eixo": "y", "sentido": sg, "c": x0,
                        "s0": min(y0, y1), "s1": max(y0, y1), "fora": sg})
        else:
            raise Erro(f"lado {i}: só ângulos retos (de {cont[i]} a {cont[(i + 1) % n]})")
    return out


def faixas(cont):
    """Strips across X: [(x0, x1, y0, y1)] — the outline's depth in Y between consecutive corner abscissas."""
    xs = sorted({p[0] for p in cont})
    ls = [l for l in lados(cont) if l["eixo"] == "x"]
    out = []
    for xa, xb in zip(xs, xs[1:]):
        xm = (xa + xb) / 2
        ys = sorted(l["c"] for l in ls if l["s0"] < xm < l["s1"])
        if len(ys) != 2:
            raise Erro("forma ainda não suportada (a casa não pode ter dois corpos na mesma faixa)")
        out.append((xa, xb, ys[0], ys[1]))
    return out


def rodar(casa):
    """The house turned 90° (x, y) -> (Y - y, x): the ceiling beams run along Y over the shorter depth."""
    Y = max(p[1] for p in casa["base"]["contorno"])

    def r(p):
        return [round(Y - p[1], 4), round(p[0], 4)]

    novo = json.loads(json.dumps(casa))
    novo["base"]["contorno"] = [r(p) for p in casa["base"]["contorno"]]
    vira = {"norte": "poente", "poente": "sul", "sul": "nascente", "nascente": "norte"}  # the faces turn with the house
    for w in novo.get("paredes_interiores", []):
        w["de"], w["ate"] = r(w["de"]), r(w["ate"])
        if w.get("faces"):
            w["faces"] = {vira.get(k, k): v for k, v in w["faces"].items()}
    for d in novo.get("pavimentos", []):  # the floor of each room: a point inside it
        d["ponto"] = r(d["ponto"])
    novo["_rodada"] = True
    return novo


# ============================================================================ conversion
def converter(casa, S):
    """(planta_paredes, config, notes) for the builder."""
    notas = []
    pe = casa.get("pe_direito", 2.5)
    if pe < PE_MIN - 1e-6:
        raise Erro(f"pé direito {pe:.2f} abaixo do mínimo legal {PE_MIN:.2f} (RGEU)")
    if pe > PE_MAX + 1e-6:  # past the configurator's guard: the studs (engineer) and the boards — to check
        notas.append(f"pé direito {pe:.2f} acima de {PE_MAX:.2f} — montantes e placas a confirmar")
    cont = [list(map(float, p)) for p in casa["base"]["contorno"]]
    if area(cont) < 0:
        raise Erro("o contorno tem de ir no sentido contrário ao dos ponteiros do relógio")
    cob_in = casa.get("cobertura", {})
    avista = cob_in.get("tipo") in ("duas_aguas", "quatro_aguas", "misto")  # exposed: the beams follow each slope, no turning
    prof = 0.0 if avista else max(f[3] - f[2] for f in faixas(cont))
    casa_r = rodar(casa)
    try:
        prof_r = float("inf") if avista else max(f[3] - f[2] for f in faixas(casa_r["base"]["contorno"]))
    except Erro:  # turned, this shape has two bodies in one strip (a U open to the side): keep it as it is
        prof_r = float("inf")
    if prof_r < prof - 1e-6:  # the beams across the shorter depth
        casa, cont, prof = casa_r, casa_r["base"]["contorno"], prof_r
        notas.append("casa rodada 90° para as vigas do teto vencerem o vão mais curto")
    ls = lados(cont)

    # the client's walls cover every side, and stay on the base
    for l in ls:
        comp = l["s1"] - l["s0"]
        pw = sorted((p["s0"], p["s1"]) for p in casa.get("paredes_exteriores", []) if p["lado"] == l["i"])
        s = 0.0
        for a, b in pw:
            if a > s + 0.01:
                break
            s = max(s, b)
        if pw and (s < comp - 0.01 or pw[-1][1] > comp + 0.01):
            raise Erro(f"lado {l['i']}: as paredes não fecham o lado ({comp:.2f} m) ou passam da base")
        if not pw:
            notas.append(f"lado {l['i']}: sem paredes colocadas — fechado com a parede do método")

    # exterior walls of the plan, the architect's way: outer face on the outline, full outer length
    paredes, nomes = [], {}
    faces_ext = casa.get("faces_interiores") or {}  # the client's finish on an outside wall's inner face, by side
    for l in ls:
        pid = f"P{len(paredes) + 1:02d}"
        nomes[l["i"]] = pid
        fi = faces_ext.get(str(l["i"])) or faces_ext.get(l["i"])
        paredes.append({"id": pid, "eixo": l["eixo"], "s0": round(l["s0"], 4), "s1": round(l["s1"], 4),
                        "c": round(l["c"] - l["fora"] * ESP_EXT / 2, 4), "espessura": ESP_EXT, "exterior": True,
                        "lado_exterior": l["fora"], "aberturas": [], "_lado": l,
                        # user 2026-10-22: the inner face of the outside walls is the client's choice too (gesso
                        # cartonado the standard, wood / ceramic options)
                        **({"faces": {NOME_FACE[(l["eixo"], l["fora"])]: fi}} if fi and fi != "pladur" else {})})

    # openings: rough opening = the frame + the company clearance (2,5 cm each side, at the head and under a
    # window — user 2026-10-20) + the shutter box (PO Q11 default: + 0,15 over a window, + 0,20 over a window to the
    # floor; doors none)
    C = S["caixilharia"]
    fg = C.get("folga", 0.025)
    itens, por_parede = [], {}
    topo_vaos = cabeca = 0.0  # the highest rough top; the highest head (lintel + top plate) over one
    for k, v in enumerate(casa.get("vaos", [])):
        if v["tipo"] not in TIPOS:
            raise Erro(f"vão {k}: tipo {v['tipo']} desconhecido ({', '.join(TIPOS)})")
        w = next((p for p in paredes if p["_lado"]["i"] == v["lado"]), None)
        if w is None:
            raise Erro(f"vão {k}: lado {v['lado']} não existe")
        l = w["_lado"]
        centro = (l["p0"][0] if l["eixo"] == "x" else l["p0"][1]) + l["sentido"] * v["centro"]
        L = v["largura"] + 2 * fg
        chao = v["tipo"] in ATE_AO_CHAO
        porta = v["tipo"] in ("porta", "portao")
        if porta and v.get("estore"):  # user 2026-10-27: "Prtas não tem estore apenas as janelas"
            notas.append(f"vão {k}: as portas não levam estore — ignorado")
            v = {**v, "estore": False}
        if chao:
            z0 = 0.0
            z1 = v["altura"] + (0.20 if v.get("estore") else fg)
        else:
            z0 = v["peitoril"] - fg
            z1 = z0 + v["altura"] + (0.15 if v.get("estore") else 2 * fg)
        if centro - L / 2 < w["s0"] or centro + L / 2 > w["s1"]:
            raise Erro(f"vão {k}: sai do lado {v['lado']}")
        # the rough top up to the ceiling (user 2026-10-22: "Apenas precisamos de 20 cm portanto seria 2,40 de pé
        # direito" — a 2,20 sliding window to the floor with its 0,20 shutter box under a 2,40 ceiling; doors have no
        # shutter, 2026-10-27); under an exposed roof the modules rise when a head needs it (below)
        if z1 > pe + 1e-6:
            notas.append(f"vão {k}: topo em bruto {z1:.2f} acima do pé direito {pe:.2f} — a confirmar")
        topo_vaos = max(topo_vaos, z1)
        Es = S["estrutura"]  # the head over it: lintel (22x7,5 from verga_grande.vao_min) + the top plate
        cabeca = max(cabeca, z1 + (Es["verga_grande"]["altura"] if L >= Es["verga_grande"]["vao_min"] - 1e-9
                                   else Es["exterior"]["padieira"]) + Es["placa"])
        w["aberturas"].append({"s0": round(centro - L / 2, 4), "s1": round(centro + L / 2, 4),
                               "tipo": "porta" if v["tipo"] in ("porta", "portao") else "janela",
                               "_z": [round(z0, 4), round(z1, 4)], "_porta": chao})
        tipo_c, desc = TIPOS[v["tipo"]]
        vidro = "" if v["tipo"] in ("porta", "portao") else v.get("vidro", "transparente")
        itens.append({"parede": w["id"], "s": round(centro, 4), "divisao": v.get("divisao", ""), "tipo": tipo_c,
                      "largura": v["largura"], "altura": v["altura"], "vidro": vidro, "estore": bool(v.get("estore")),
                      "descricao": f"{desc} em {C.get('material', 'alumínio RAL 7016')} com rotura térmica"
                                   + (" + vidro duplo" if vidro else ""), "descricao_curta": desc, "observacoes": ""})
    for w in paredes:
        w["aberturas"].sort(key=lambda o: o["s0"])
        por_parede[w["id"]] = [{"i": i, "tipo": "porta" if o["_porta"] else "janela", "z": o.pop("_z")}
                               for i, o in enumerate(w["aberturas"])]
        for o in w["aberturas"]:
            o.pop("_porta")

    # interior walls: centre lines, each end taken into the wall it meets (the builder stops it at that wall's face)
    for k, wi in enumerate(casa.get("paredes_interiores", [])):
        (xa, ya), (xb, yb) = wi["de"], wi["ate"]
        if abs(ya - yb) < 1e-6:
            eixo, c, sa, sb = "x", ya, xa, xb
        elif abs(xa - xb) < 1e-6:
            eixo, c, sa, sb = "y", xa, ya, yb
        else:
            raise Erro(f"parede interior {k}: só paredes a direito, ao longo de X ou de Y")
        sg = 1 if sb > sa else -1
        ends = []
        for s_ in (sa, sb):
            alvo = s_
            for q in paredes:
                if q["eixo"] == eixo or not (q["s0"] - 0.05 <= c <= q["s1"] + 0.05):
                    continue
                if abs(q["c"] - s_) < 0.35:  # snap onto the centre line of the wall it meets
                    alvo = q["c"]
            ends.append(alvo)
        pid = f"P{len(paredes) + 1:02d}"
        portas = []
        for d in wi.get("portas", []):
            m = sa + sg * d["centro"]
            portas.append({"s0": round(m - 0.40, 4), "s1": round(m + 0.40, 4), "tipo": "porta"})
        paredes.append({"id": pid, "eixo": eixo, "s0": round(min(ends), 4), "s1": round(max(ends), 4), "c": round(c, 4),
                        "espessura": ESP_INT, "exterior": False, "lado_exterior": 0,
                        "aberturas": sorted(portas, key=lambda o: o["s0"]),
                        # each face's finish, by the side it faces (the client's choice; "pladur" = the standard)
                        **({"faces": wi["faces"]} if wi.get("faces") else {})})

    if avista:  # exposed sandwich-panel roof (telhado.py builds its surface, telhado_estrutura.py its timber)
        # the slope in % (the company's unit; minimum 15 % — user 2026-10-21: "A inclinação mínima da cobertura à
        # vista é 15 %"); a house given in degrees is read too
        minimo = S["cobertura"].get("inclinacao_min_avista_pct", 15.0)
        pct = float(cob_in["inclinacao_pct"]) if "inclinacao_pct" in cob_in else \
            100.0 * math.tan(math.radians(float(cob_in.get("inclinacao_graus", math.degrees(math.atan(minimo / 100))))))
        if pct < minimo - 1e-6:
            notas.append(f"inclinação {pct:.1f} % abaixo do mínimo da cobertura à vista ({minimo:.0f} %)")
        # the eaves overhang 0,20 to 0,50 (user 2026-10-22: "O mínimo de beirado possível é 20 cm"; 2026-10-28: "Beirado
        # vamos definir um máximo de 50 cm se vires que é problemático em algum dos modelos podemos dimnuir nesse modelo")
        b_min, b_max = S["cobertura"].get("beirado_min", 0.20), S["cobertura"].get("beirado_max", 0.50)
        beirado = float(cob_in.get("beirado", S["cobertura"]["beirado"]))
        if not b_min - 1e-6 <= beirado <= b_max + 1e-6:
            notas.append(f"beirado {beirado:.2f} fora de {b_min:.2f}-{b_max:.2f}: usado {min(max(beirado, b_min), b_max):.2f}")
            beirado = min(max(beirado, b_min), b_max)
        cobertura = {"tipo": "a_vista", "forma": cob_in["tipo"], "inclinacao_pct": round(pct, 3),
                     "inclinacao_graus": round(math.degrees(math.atan(pct / 100.0)), 4),
                     # the verges overhang as the eaves: where a gable meets a wing's eave the two edges meet in
                     # one corner (user 2026-10-29: "o beirado do triângulo nao coincide com o beirado da outra
                     # cobertura... não vais ter dois telhados desalinhados um com o outro") — was 0,12
                     "beirado": beirado, "empena": beirado,
                     "painel_espessura": round(S["cobertura"]["painel"]["nucleo"] + S["cobertura"]["painel"].get("relevo", 0.0), 4),
                     "_doc": "Cobertura à vista em painel sandwich (user 2026-10-21: 2 águas a regra, 4 águas opção, "
                             "várias águas em L / T / U; mínimo 15 %; beirado 0,25 por defeito)."}
        try:
            telhado_av.decompor(cont)
        except ValueError as e:
            raise Erro(str(e)) from None
    else:
        cobertura = cobertura_escondida(casa, cont, prof, notas, S)

    ac = casa.get("acabamentos", {})
    camadas = {"exterior": {"opcao_visivel": ac.get("exterior", "A")},
               "pavimentos": {"piso0": {"acabado_z": 0.005, "camadas": []}},
               "tetos": {"la": {"pisos": [0]}, "la_pavimento": {"pisos": []}},
               "caixilharia": {"itens": itens}}
    opc_pav = S["pavimentos"].get("acabamento_opcoes") or {}
    pav = ac.get("pavimento", "vinilico")  # the floor the client chose for the house
    if pav in opc_pav:
        camadas["pavimentos"]["acabamento"] = opc_pav[pav]
    # and per room (user 2026-10-22: "a pessoa pode aplicar pavimento que desejar na divisão que desejar"): a point
    # inside the room, its finish (the standard's "vinilico" = pavimentos.acabamento)
    divs = [{"ponto": [round(float(d["ponto"][0]), 4), round(float(d["ponto"][1]), 4)],
             "acabamento": opc_pav.get(d["acabamento"]) or S["pavimentos"]["acabamento"]}
            for d in casa.get("pavimentos", []) if d.get("acabamento")]
    if divs:
        camadas["pavimentos"]["divisoes"] = divs
    if not avista:  # hidden roof: the ceiling hangs below the amarração ring on the modules' inner face, as at Torres
        # Vedras (confirmed 2026-10-21; the drop 0,1185 = the ring 0,11 + 8,5 mm — assumed)
        camadas["tetos"]["suspensao"] = {"folga": round(S["estrutura"]["lameladas"]["amarracao"]["altura"] + 0.0085, 4)}
    else:  # exposed roof: the exterior modules end under the ceiling beams at about pé direito - 0,05; a head that
        # does not fit (a 2,20 sliding window with its box at 2,40 — user 2026-10-22) raises them, the false ceiling
        # staying at the pé direito on longer hangers — ours, how they frame that head: to confirm
        T_, Es = S["tetos"], S["estrutura"]
        teto_plano = T_["suspensao"]["folga"] + T_["perfis"]["altura"] + T_["acabamento"]["espessura"]
        h_mod = pe + teto_plano - Es["afinacao_exterior"]["altura"] - Es["amarracao"]["altura"]
        if cabeca > h_mod + 1e-4:
            sobe = math.ceil((cabeca - h_mod) * 1000) / 1000
            camadas["tetos"]["suspensao"] = {"folga": round(T_["suspensao"]["folga"] + sobe, 4)}
            notas.append(f"módulos exteriores {sobe * 100:.1f} cm mais altos para a padieira do vão mais alto (topo em "
                         f"bruto {topo_vaos:.2f}); o teto falso fica a {pe:.2f} — a confirmar")
    if ac.get("exterior", "A") == "A" and ac.get("contra_ripado", True) is False:
        camadas["exterior"]["opcoes"] = {"A": {"camadas": [c for c in S["exterior"]["opcoes"]["A"]["camadas"]
                                                           if c["id"] != "contra_ripado"]}}
    return _config(casa, cont, paredes, por_parede, cobertura, camadas, ac, notas)


def cobertura_escondida(casa, cont, prof, notas, S=None):
    """The roof hidden behind the parapet, the gutters inside the parapets on the low side (rulebook §7); glulam
    lameladas past 8 m of depth (D2503). The shape chosen per house, the most effective one (user 2026-10-28: "nós
    tentamos sempre só fazer uma água e sempre coberturas ocultas … Não quero que assumas um padrão mas sim a solução
    mais eficaz e inteligente para cada caso"; on a U with a short middle part: "fariamos apenas uma água para a
    cobertura toda"):
      - ONE SLOPE over the whole house, falling across the ceiling beams to the side where every strip ends on one
        straight line (one gutter, straight), each strip's panels in one length from that gutter up to its own high
        wall, the parapets hiding the top; the house is turned so the beams span the shorter depth (converter);
      - two slopes only when one slope's panels would be longer than the panel's maximum length (JSON
        `cobertura.painel_oculto.comprimento_max`) or no side is straight: one ridge along X through every strip, in
        the middle of the main block as near as a ridge through every strip allows, every slope at least 1 m (as
        Torres Vedras, D2503 — ours for other shapes)."""
    fx = faixas(cont)
    zonas = []
    for x0, x1, y0, y1 in fx:
        if zonas and abs(zonas[-1][2] - y0) < 1e-6 and abs(zonas[-1][3] - y1) < 1e-6:
            zonas[-1][1] = x1
        else:
            zonas.append([x0, x1, y0, y1])
    comp_max = ((S or {}).get("cobertura", {}).get("painel_oculto", {}) or {}).get("comprimento_max", 15.0)
    retos = [lado for lado, k in (("S", 2), ("N", 3)) if all(abs(f[k] - fx[0][k]) < 1e-6 for f in fx)]
    if retos and max(f[3] - f[2] for f in fx) <= comp_max + 1e-6:
        # both straight (a rectangle): the client chooses the gutter's side (user 2026-10-29 "Podes deixar o cliente
        # escolher"), in the configurator's own compass (+y north; a turned house's S is the client's west); the south
        # when not chosen or not possible
        bussola = {"S": "poente", "N": "nascente"} if casa.get("_rodada") else {"S": "sul", "N": "norte"}
        pedido = casa.get("cobertura", {}).get("lado_caleira")
        lado = next((l for l in retos if bussola[l] == pedido), retos[0])
        if pedido and bussola[lado] != pedido:
            notas.append(f"caleira a {pedido} não é possível nesta casa: fica a {bussola[lado]}")
        aguas = []
        for x0, x1, y0, y1 in fx:  # each strip its own água, up to its own high wall
            y_fim, y_topo = (y0, y1) if lado == "S" else (y1, y0)
            if aguas and abs(aguas[-1]["y_topo"] - y_topo) < 1e-6 and abs(aguas[-1]["x"][1] - x0) < 1e-6:
                aguas[-1]["x"][1] = x1
            else:
                aguas.append({"x": [x0, x1], "lado": lado, "y_fim": y_fim, "y_topo": y_topo})
        topo = max(a["y_topo"] for a in aguas) if lado == "S" else min(a["y_topo"] for a in aguas)
        cobertura = {"tipo": "platibanda", "uma_agua": True,
                     "inclinacao_pct": casa.get("cobertura", {}).get("inclinacao_pct", 6.0),
                     "painel_espessura": 0.08, "cumeeira_y": topo, "aguas": aguas, "vigas_teto": zonas,
                     "lado_caleira": bussola[lado], "lados_caleira": [bussola[l] for l in retos],
                     "_doc": "Cobertura escondida pela platibanda (método DiscoverCasa): uma água (user 2026-10-28), "
                             "a caleira no lado baixo, cada faixa até à sua parede alta; inclinação 6 % como Torres "
                             "Vedras (a mínima do painel — assumido)."}
        if prof > LIMITE_VIGAS + 1e-6:
            cobertura["estrutura"] = "lameladas"
            notas.append(f"profundidade {prof:.2f} m > {LIMITE_VIGAS:.0f} m: vigas lameladas (como Torres Vedras)")
        return cobertura
    ya, yb = max(f[2] for f in fx), min(f[3] for f in fx)
    if ya >= yb:
        raise Erro("forma ainda não suportada pela cobertura escondida (nenhuma cumeeira atravessa a casa toda)")
    m = telhado_av.decompor(cont)[0]
    d = min(1.0, (yb - ya) / 2)
    yr = round(min(max((m["y0"] + m["y1"]) / 2, ya + d), yb - d), 4)
    notas.append(f"cobertura escondida em duas águas: numa água os painéis passariam de {comp_max:g} m".replace(".", ",") if retos else
                 "cobertura escondida em duas águas: nenhum lado da casa é reto para a caleira de uma água")
    aguas = []
    for lado in ("N", "S"):
        for x0, x1, y0, y1 in fx:
            y_fim = y1 if lado == "N" else y0
            if aguas and aguas[-1]["lado"] == lado and abs(aguas[-1]["y_fim"] - y_fim) < 1e-6 and \
                    abs(aguas[-1]["x"][1] - x0) < 1e-6:
                aguas[-1]["x"][1] = x1
            else:
                aguas.append({"x": [x0, x1], "lado": lado, "y_fim": y_fim})
    cobertura = {"tipo": "platibanda", "inclinacao_pct": casa.get("cobertura", {}).get("inclinacao_pct", 6.0),
                 "painel_espessura": 0.08, "cumeeira_y": yr, "aguas": aguas, "vigas_teto": zonas,
                 "_doc": "Cobertura escondida pela platibanda (método DiscoverCasa); cumeeira ao longo de X; inclinação "
                         "6 % como Torres Vedras (a mínima do painel — assumido)."}
    if prof > LIMITE_VIGAS + 1e-6:
        cobertura["estrutura"] = "lameladas"
        notas.append(f"profundidade {prof:.2f} m > {LIMITE_VIGAS:.0f} m: vigas lameladas (como Torres Vedras)")
    return cobertura


def _config(casa, cont, paredes, por_parede, cobertura, camadas, ac, notas):
    X, Y = max(p[0] for p in cont), max(p[1] for p in cont)
    nome = casa.get("nome", "Casa configurada")
    cfg = {"nome": nome, "descricao": f"Casa montada no configurador ({casa['base'].get('forma', '')}, "
                                      f"{area(cont):.1f} m² de base). Gerado por para_construtor.py.",
           "planta": "planta_paredes.json", "casa": {"comprimento": X, "profundidade": Y},
           "niveis": {"pe_direito": casa.get("pe_direito", 2.5)},
           "modulos": {}, "aberturas": {"por_parede": por_parede}, "cobertura": cobertura,
           "fundacao": {"contorno": cont, "espessura_laje": 0.2,
                        "nota": "Base indicativa (laje 20 cm) — o utilizador vai ensinar a base de fundação."},
           "estrutura": {"sistema": "discovercasa"}, "camadas": camadas, "paredes": {"exterior": "face_exterior"},
           "saida": {"geometria": "casa_geometria.json", "blend": "Casa_Configurada.blend",
                     "glb": "Casa_Configurada_Estrutura.glb", "glb_completa": "Casa_Configurada_Completa.glb"},
           "documentos": {"obra": casa.get("obra", "CFG"), "projeto": nome, "local": "Configurador DiscoverCasa"},
           "configurador": {"acabamentos": ac}}
    # pergolas against the facades (step 7, user 2026-10-29): the side, the stretch along it, the projection and the
    # height of the beams at the facade (casa_planta builds them with pergola.py; the height kept under its maximum)
    ls = {l["i"]: l for l in lados(cont)}
    pgs = []
    for k, pg in enumerate((casa.get("exteriores") or {}).get("pergolas", [])):
        l = ls.get(pg.get("lado"))
        if l is None:
            raise Erro(f"pérgola {k}: lado {pg.get('lado')} não existe")
        comp = l["s1"] - l["s0"]
        s0, s1 = max(0.0, float(pg["s0"])), min(comp, float(pg["s1"]))
        if s1 - s0 < 0.5:
            raise Erro(f"pérgola {k}: não cabe no lado {pg['lado']}")
        pgs.append({"lado": l["i"], "s0": round(s0, 4), "s1": round(s1, 4), "projecao": float(pg.get("projecao", 3.0)),
                    "altura": float(pg["altura"]) if pg.get("altura") is not None else None})
    if pgs:
        cfg["pergolas"] = pgs
    for w in paredes:
        w.pop("_lado", None)
    planta = {"origem": "configurador", "contorno": [0.0, X, 0.0, Y], "paredes": paredes}
    return planta, cfg, notas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("casa")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--construir", action="store_true")
    ap.add_argument("--documentos", action="store_true")
    a = ap.parse_args()
    casa = json.load(open(a.casa, encoding="utf-8"))
    S = json.load(open(MODELO / "sistema_construtivo.json", encoding="utf-8"))
    try:
        planta, cfg, notas = converter(casa, S)
    except Erro as e:
        raise SystemExit(f"casa não convertida: {e}")
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "planta_paredes.json").write_text(json.dumps(planta, ensure_ascii=False, indent=1), encoding="utf-8")
    (saida / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"CONVERTIDA {saida}: {len([p for p in planta['paredes'] if p['exterior']])} paredes exteriores, "
          f"{len([p for p in planta['paredes'] if not p['exterior']])} interiores, "
          f"{sum(len(p['aberturas']) for p in planta['paredes'])} vãos; base {area(cfg['fundacao']['contorno']):.1f} m²")
    for n in notas:
        print("  nota:", n)
    if a.construir or a.documentos:
        geo = saida / "geometria.json"
        r = subprocess.run([sys.executable, str(MODELO / "casa_planta.py"), str(saida / "config.json"), "--saida", str(geo)])
        if r.returncode:
            raise SystemExit("casa_planta.py falhou")
        G = json.load(open(geo, encoding="utf-8"))
        mods = [p for p in G["paineis"] if p["tipo"] in ("PE", "PI") and p.get("piso") == 0 and not p.get("fantasma")]
        print(f"  módulos: {sum(p['tipo'] == 'PE' for p in mods)} exteriores, {sum(p['tipo'] == 'PI' for p in mods)} interiores")
        if a.documentos:
            r = subprocess.run([sys.executable, str(RAIZ / "ferramentas" / "documentos" / "gerar.py"),
                                str(saida / "config.json"), "--saida", str(saida / "documentos")])
            if r.returncode:
                raise SystemExit("gerar.py falhou")


if __name__ == "__main__":
    main()
