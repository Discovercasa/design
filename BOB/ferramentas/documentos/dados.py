"""Model data for the production documents: rebuilds the geometry (casa_planta.py) and the layers (camadas.py)
of a house config into the work folder, and gives modules, members, structure pieces, layer objects, cut lists,
material totals and sections through the model. Pure Python (no Blender)."""
import json
import math
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
from ferramentas.comum import pasta_trabalho  # noqa: E402
from ferramentas.modelo.camadas import fundir  # noqa: E402

MODELO = RAIZ / "ferramentas" / "modelo"


class Modulo:
    def __init__(self, p, a):
        self.nome, self.alcado = p["nome"], a
        self.tipo = p["tipo"]                       # PE / PI
        self.exterior = p["tipo"] == "PE"
        self.rotulo = p.get("modulo") or p["nome"].split()[-1]
        partes = p["nome"].split()
        self.parede = partes[1].split(".")[0] if len(partes) > 1 else ""
        self.W, self.H, self.t = a["W"], a["H"], p["espessura"]
        self.o, self.s = p["origem"], p["sentido"]
        self.fora = p.get("fora", 0.0)
        self.eixo = "x" if abs(self.s[0]) > 0.5 else "y"
        if "membros_fabrico" in a:  # as made in the factory (casa_planta): whole studs, the notch cut on site
            self.membros = a["membros_fabrico"]
            self.entalhes = [tuple(e) for e in a.get("entalhes", [])]
        else:
            self.membros, self.entalhes = unir_entalhes(a["members"])
        self.membros_modelo = a["members"]  # as in the model (pockets cut): for the sections
        self.aberturas = a.get("aberturas", [])
        self.em_obra = a.get("em_obra", False)  # longer than a factory module (D2503 "* Painel a executar em obra")

    def pegada(self):
        ox, oy, t = self.o[0], self.o[1], self.t
        if self.eixo == "x":
            return ox, ox + self.W, oy - t / 2, oy + t / 2
        return ox - t / 2, ox + t / 2, oy, oy + self.W

    def mundo(self, u, v, w):
        nx, ny = -self.s[1], self.s[0]
        return (self.o[0] + u * self.s[0] + w * nx, self.o[1] + u * self.s[1] + w * ny, self.o[2] + v)

    def prismas(self):
        """Members as world prisms {"b", "e", "seccao", "tipo"} (through the wall thickness)."""
        nx, ny = -self.s[1], self.s[0]
        out = []
        for m in self.membros_modelo:
            base = [self.mundo(u, v, -self.t / 2) for u, v in m["poly"]]
            out.append({"b": base, "e": (nx * self.t, ny * self.t, 0.0), "seccao": m["section"], "tipo": m["tipo"]})
        return out

    def orientacao(self):
        if not self.exterior:
            return ""
        if self.eixo == "x":
            return "Norte" if self.fora > 0 else "Sul"
        return "Poente" if self.fora > 0 else "Nascente"


def comprimento_membro(m):
    """The cut length: the long side of the member's box, or its longest edge where that is longer (the true length
    of a sloped gable plate)."""
    p = m["poly"]
    us, vs = [q[0] for q in p], [q[1] for q in p]
    return max(max(us) - min(us), max(vs) - min(vs), max(math.dist(p[i], p[(i + 1) % len(p)]) for i in range(len(p))))


def area_membro(m):
    p = m["poly"]
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2


def unir_entalhes(membros, gap=(0.15, 0.25)):
    """Older models split a stud where a beam crossed the wall (pocket); since 2026-10-21 the beams end at the
    modules' inner face and no stud is cut (user: they "ficam por dentro e encostadas"), so this only merges
    the halves of a model built before that. Returns (members, notches [(u0, u1, v0, v1)])."""
    vert, out, entalhes = defaultdict(list), [], []
    for mb in membros:
        us, vs = [q[0] for q in mb["poly"]], [q[1] for q in mb["poly"]]
        if max(vs) - min(vs) > max(us) - min(us):
            vert[(mb["section"], mb["tipo"], round(min(us), 3), round(max(us), 3))].append((min(vs), max(vs), mb))
        else:
            out.append(mb)
    for (sec, tp, u0, u1), lst in vert.items():
        lst.sort(key=lambda t: t[0])
        cur = None
        for v0, v1, mb in lst:
            if cur and gap[0] <= v0 - cur[1] <= gap[1]:
                entalhes.append((u0, u1, cur[1], v0))
                cur[1] = v1
                continue
            if cur:
                out.append({"section": sec, "tipo": tp, "poly": [[u0, cur[0]], [u1, cur[0]], [u1, cur[1]], [u0, cur[1]]]})
            cur = [v0, v1]
        if cur:
            out.append({"section": sec, "tipo": tp, "poly": [[u0, cur[0]], [u1, cur[0]], [u1, cur[1]], [u0, cur[1]]]})
    return out, entalhes


class Casa:
    def __init__(self, cfg_path, reconstruir=True):
        self.cfg_path = Path(cfg_path).resolve()
        self.cfg = json.load(open(self.cfg_path, encoding="utf-8"))
        self.base = self.cfg_path.parent
        doc = self.cfg.get("documentos", {})
        self.obra = doc.get("obra") or self.cfg.get("nome", "Obra")
        self.trab = pasta_trabalho("documentos", self.obra.replace(" ", "_"))
        geo, cam = self.trab / "geometria.json", self.trab / "camadas.json"
        if reconstruir or not geo.exists():
            for args in ([str(MODELO / "casa_planta.py"), str(self.cfg_path), "--saida", str(geo)],
                         [str(MODELO / "camadas.py"), str(self.cfg_path), "--saida", str(cam), "--geometria", str(geo)]):
                r = subprocess.run([sys.executable] + args, capture_output=True, text=True, encoding="utf-8", errors="replace")
                if r.returncode:
                    raise SystemExit(f"falhou: {Path(args[0]).name}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
        self.G = json.load(open(geo, encoding="utf-8"))
        self.K = json.load(open(cam, encoding="utf-8"))
        self.S = fundir(json.load(open(MODELO / "sistema_construtivo.json", encoding="utf-8")), self.cfg.get("camadas") or {})
        al = self.G["alcados"]
        self.modulos = [Modulo(p, al[p["alcado"]]) for p in self.G["paineis"]
                        if p.get("piso") == 0 and p["tipo"] in ("PE", "PI") and not p.get("fantasma")]
        # the gable triangles of an exposed roof (EMP R1N ...): made in the factory like the modules
        self.empenas = []
        for p in self.G["paineis"]:
            if p.get("empena") and p.get("alcado") in al:
                m = Modulo(p, al[p["alcado"]])
                m.membros, m.entalhes = m.membros_modelo, []  # sloped members as they are (no stud merging)
                m.rotulo = p["nome"]
                self.empenas.append(m)
        self.extra = self.G.get("estrutura_extra", [])
        self.objetos = self.K["objetos"]
        self.contorno = [tuple(v) for v in self.G.get("contorno_estrutura") or []]

    # ------------------------------------------------------------------ walls
    def paredes(self, exterior=True):
        """{wall id: [modules ordered along the wall]}."""
        res = defaultdict(list)
        for m in self.modulos:
            if m.exterior == exterior:
                res[m.parede].append(m)
        for v in res.values():
            v.sort(key=lambda m: m.o[0] if m.eixo == "x" else m.o[1])
        return dict(res)

    # ------------------------------------------------------------------ timber
    def pecas_madeira(self):
        """Every timber piece: (group, section, length m, volume m3, kind). Modules member by member."""
        out = []
        for m in self.modulos + self.empenas:
            g = "Empenas (módulos)" if m in self.empenas else (
                "Paredes exteriores (módulos)" if m.exterior else "Paredes interiores (módulos)")
            for mb in m.membros:
                out.append((g, mb["section"], comprimento_membro(mb), area_membro(mb) * m.t, mb["tipo"]))
        nomes = self.G.get("colecoes_estrutura", {})
        for e in self.extra:
            pr = e["props"]
            g = nomes.get(e["colecao"], e["colecao"])
            g = g.split(" ", 1)[1] if g[:1].isdigit() and " " in g else g
            g = g.split(" (")[0]
            out.append((g, pr["seccao"], pr.get("comprimento_m", 0.0), pr.get("volume_m3", 0.0), pr.get("tipo", "")))
        return out

    def lista_corte(self, so_modulos=True):
        """{section: {length (cm): count}} of the module members (as cut; the gable triangles are modules too)."""
        res = defaultdict(lambda: defaultdict(int))
        for m in self.modulos + self.empenas:
            for mb in m.membros:
                res[mb["section"]][round(comprimento_membro(mb) * 100)] += 1
        if not so_modulos:
            for e in self.extra:
                pr = e["props"]
                if pr.get("tipo", "").startswith("Ripado"):
                    continue
                res[pr["seccao"]][round(pr.get("comprimento_m", 0.0) * 100)] += 1
        return res

    # ------------------------------------------------------------------ layers
    def camadas_totais(self):
        """Layer objects summed by (collection, layer): pieces, length, area, volume, purchase."""
        nomes = {c["id"]: c["nome"] for c in self.K["colecoes"]}
        tot = {}
        for o in self.objetos:
            pr = o["props"]
            cam = pr.get("camada")
            if not cam:
                continue
            k = (o["colecao"], cam)
            t = tot.setdefault(k, {"colecao": nomes.get(o["colecao"], o["colecao"]), "camada": cam, "n": 0, "comp": 0.0,
                                   "area": 0.0, "vol": 0.0, "un": "", "au": 0.0, "cu": 0.0, "desp": 0.0, "produto": ""})
            t["n"] += pr.get("pecas", 1)
            t["comp"] += pr.get("comprimento_m", 0.0) or 0.0
            t["area"] += pr.get("area_m2", 0.0) or 0.0
            t["vol"] += pr.get("volume_m3", 0.0) or 0.0
            for a, b in (("un", "unidade"), ("au", "area_unidade_m2"), ("cu", "comprimento_unidade_m"), ("desp", "desperdicio")):
                if pr.get(b):
                    t[a] = pr[b]
            if pr.get("produto") and not t["produto"]:
                t["produto"] = pr["produto"]
        for t in tot.values():
            q = ""
            if t["au"]:
                q = math.ceil(t["area"] * (1 + t["desp"]) / t["au"])
            elif t["cu"]:
                q = math.ceil(t["comp"] * (1 + t["desp"]) / t["cu"])
            t["compra"] = q
        return tot

    def objetos_de(self, prefixo):
        return [o for o in self.objetos if o["colecao"] == prefixo or o["colecao"].startswith(prefixo + ".")]


# ---------------------------------------------------------------------- geometry helpers
def _topo(pc):
    """Top face of a prism: {"b", "e"} (base + extrusion) or {"b", "t"} (base + top, e.g. the prumos of a roof on
    220x75 ceiling beams)."""
    if "t" in pc:
        return [tuple(p) for p in pc["t"]]
    return [(p[0] + pc["e"][0], p[1] + pc["e"][1], p[2] + pc["e"][2]) for p in pc["b"]]


def caixa_planta(pc):
    """Plan bounding box of a prism {"b", "e"} / {"b", "t"}."""
    pts = [tuple(p) for p in pc["b"]] + _topo(pc)
    xs, ys, zs = [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def contorno_planta(pc):
    """Plan outline of a prism (convex hull of its corners): for pieces at an angle (hips, valleys)."""
    return _casco([(p[0], p[1]) for p in [tuple(q) for q in pc["b"]] + _topo(pc)])


def _casco(pts):
    pts = sorted(set((round(a, 5), round(b, 5)) for a, b in pts))
    if len(pts) < 3:
        return pts

    def cruz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cruz(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cruz(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def corte(pc, s, eixo="x"):
    """Section by the plane x = s (eixo "x": polygon in (y, z)) or y = s (eixo "y": polygon in (x, z)), or None."""
    if eixo == "x":
        return corte_x(pc, s)
    troca = {"b": [(p[1], p[0], p[2]) for p in pc["b"]]}
    if "t" in pc:
        troca["t"] = [(p[1], p[0], p[2]) for p in pc["t"]]
    else:
        troca["e"] = (pc["e"][1], pc["e"][0], pc["e"][2])
    return corte_x(troca, s)


def corte_x(pc, xs):
    """Section of a convex prism {"b", "e"} / {"b", "t"} by the plane x = xs: polygon in (y, z), or None."""
    b = [tuple(p) for p in pc["b"]]
    t = _topo(pc)
    n = len(b)
    arestas = [(b[i], b[(i + 1) % n]) for i in range(n)] + [(t[i], t[(i + 1) % n]) for i in range(n)] + list(zip(b, t))
    pts = []
    for p, q in arestas:
        dp, dq = p[0] - xs, q[0] - xs
        if abs(dp) < 1e-9 and abs(dq) < 1e-9:
            pts += [(p[1], p[2]), (q[1], q[2])]
        elif dp * dq <= 0 and abs(dp - dq) > 1e-12:
            k = dp / (dp - dq)
            pts.append((p[1] + k * (q[1] - p[1]), p[2] + k * (q[2] - p[2])))
    h = _casco(pts)
    if len(h) < 3:
        return h if len(h) == 2 else None
    return h
