"""Wall-panel analysis from the geometry JSON (pure Python): member roles, openings, stud cavities,
plan footprint and panel-local -> world transform.

Panel frame: u along the wall (elevation x), v up (elevation y), w across the wall (local +y, left of +u).
The panel origin lies on the wall centre line, so the wall occupies w in [-t/2, t/2].
"""
import math

from ferramentas.modelo.geometria2d import analyse, clean, corte_vertical, hull

TOL_STUD = 0.015


class Painel:
    def __init__(self, p, e, centro):
        self.nome, self.piso, self.tipo = p["nome"], p["piso"], p["tipo"]
        self.fantasma = p.get("fantasma", False)  # parapet part of a full-height module (layers only)
        self.acabamentos = p.get("acabamentos") or {}  # an interior wall's finish per face (configurator)
        self.alcado = p["alcado"]
        self.ox, self.oy, self.oz = p["origem"]
        self.ux, self.uy = p["sentido"]
        self.t = p["espessura"]
        self.f0, self.f1 = e["frame_u0"], e["frame_u1"]
        polys = [clean(m["poly"]) for m in e["members"]]
        self.membros = []
        for pl in polys:
            if len(pl) < 3:
                continue
            a = analyse(pl)
            if a["sloped"] and a["tperp"] > 0.12:
                papel = "empena"  # verge rafter on the outer half of a gable panel (not part of the frame)
            elif a["sloped"]:
                papel = "inclinada"
            elif a["dv"] > a["du"]:
                papel = "montante"
            else:
                papel = "horizontal"
            self.membros.append({"poly": pl, "a": a, "papel": papel})
        frame = [m for m in self.membros if m["papel"] != "empena"]
        self.frame = frame
        self.hf = max(m["a"]["vmax"] for m in frame)
        self.contorno = clean(hull([q for m in frame for q in m["poly"]]))
        hz = [m for m in frame if m["papel"] == "horizontal"]
        self.bases = [m for m in hz if m["a"]["vmin"] < 0.09]
        self.bot = max([m["a"]["vmax"] for m in self.bases] or [0.0])
        # sloped top plates are exported in many small pieces: anything within 0.25 m of the outline top
        # is treated as part of the top plate, the rest are noggings / sills / headers
        self.horizontais = [m for m in hz if m not in self.bases and
                            m["a"]["vmax"] < self.topo_contorno((m["a"]["umin"] + m["a"]["umax"]) / 2) - 0.25]
        mx = self.ox + self.ux * (self.f0 + self.f1) / 2
        my = self.oy + self.uy * (self.f0 + self.f1) / 2
        dp = math.dist((mx - self.uy * 0.1, my + self.ux * 0.1), centro)
        dm = math.dist((mx + self.uy * 0.1, my - self.ux * 0.1), centro)
        self.fora = 1.0 if dp > dm else -1.0  # side (sign of w) facing away from the house centre
        if p.get("fora"):  # generated from a plan (casa_planta.py): known, also for L-shaped houses
            self.fora = float(p["fora"])
        self._montantes()
        # generated modules (estrutura_dc.py) carry their openings; drawings need them inferred
        self.aberturas = [tuple(a) for a in e["aberturas"]] if "aberturas" in e else self._aberturas()

    # ------------------------------------------------------------------ transforms
    def mundo(self, u, v, w):
        return (self.ox + u * self.ux - w * self.uy, self.oy + u * self.uy + w * self.ux, self.oz + v)

    def pegada(self):
        """Plan footprint (x0, x1, y0, y1) of the frame."""
        pts = [self.mundo(u, 0, w)[:2] for u in (self.f0, self.f1) for w in (-self.t / 2, self.t / 2)]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs), max(xs), min(ys), max(ys))

    def s_de_u(self, u):
        """World coordinate along the wall axis (x for walls running E-W, y for N-S) of elevation u."""
        return self.ox + u * self.ux if abs(self.ux) > 0.5 else self.oy + u * self.uy

    # ------------------------------------------------------------------ studs and top line
    def topo_contorno(self, u):
        c = corte_vertical(self.contorno, u)
        return c[1] if c else self.hf

    def membro_acima(self, u, vref):
        """Underside of the first non-stud member above height vref at elevation u."""
        cands = []
        for m in self.frame:
            if m["papel"] == "montante":
                continue
            c = corte_vertical(m["poly"], u)
            if c and c[0] > vref + 0.01:
                cands.append(c[0])
        return min(cands) if cands else self.topo_contorno(u)

    def _montantes(self):
        grupos = []
        for m in self.membros:
            if m["papel"] != "montante":
                continue
            a = m["a"]
            for g in grupos:
                if abs(g["umin"] - a["umin"]) < TOL_STUD and abs(g["umax"] - a["umax"]) < TOL_STUD:
                    g["vmin"] = min(g["vmin"], a["vmin"])
                    g["vmax"] = max(g["vmax"], a["vmax"])
                    break
            else:
                grupos.append({"umin": a["umin"], "umax": a["umax"], "vmin": a["vmin"], "vmax": a["vmax"]})
        for g in grupos:
            uc = (g["umin"] + g["umax"]) / 2
            g["inteiro"] = g["vmin"] <= self.bot + 0.03 and g["vmax"] >= self.topo_contorno(uc) - 0.25
        self.montantes = sorted(grupos, key=lambda g: g["umin"])

    # ------------------------------------------------------------------ openings
    def _aberturas(self):
        """Door/window openings = bays >= 0.55 m between full-height studs.

        Cripple studs below a member make it a sill (window above it); cripples above a member make it a
        header (door below it). Without cripples: a first member >= 1.8 m above the floor plate is a door
        head, otherwise the highest member is the sill of a window reaching the top plate.
        Interior panels (PI) only get doors. Real door/window sizes are not in the structural drawings.
        """
        full = [g for g in self.montantes if g["inteiro"]]
        out = []
        if self.hf < 1.8:  # low walls (e.g. stair support) have no openings
            return out
        for a, b in zip(full, full[1:]):
            u0, u1 = a["umax"], b["umin"]
            if u1 - u0 < 0.55:
                continue
            mid = (u0 + u1) / 2
            inner = sorted((m["a"] for m in self.horizontais
                            if m["a"]["umin"] < mid < m["a"]["umax"] and m["a"]["vmin"] >= self.bot - 0.001),
                           key=lambda h: h["vmin"])
            vref = inner[-1]["vmax"] if inner else self.bot
            # the jamb studs reach the underside of the (possibly sloped) top plate
            top = min(a["vmax"], b["vmax"], self.membro_acima(mid, vref))
            crip = [g for g in self.montantes if not g["inteiro"] and u0 - 0.001 <= (g["umin"] + g["umax"]) / 2 <= u1 + 0.001]
            below = [g for g in crip if g["vmin"] <= self.bot + 0.03]
            above = [g for g in crip if g["vmax"] >= top - 0.03 and g["vmin"] > self.bot + 0.03]
            if not inner:
                op = (self.bot, top, "porta")
            elif below or above:
                v0, v1, kind = self.bot, top, "porta"
                if below:
                    ref = max(g["vmax"] for g in below)
                    sill = min(inner, key=lambda h: abs(h["vmin"] - ref))
                    v0, kind = sill["vmax"], "janela"
                if above:
                    ref = min(g["vmin"] for g in above)
                    head = min(inner, key=lambda h: abs(h["vmax"] - ref))
                    v1 = head["vmin"]
                op = (v0, v1, kind)
            elif inner[0]["vmin"] - self.bot >= 1.8:
                op = (self.bot, inner[0]["vmin"], "porta")
            else:
                # window: a gap above the first member (sill); prefer the one at eye height (floor + 1.6 m)
                gaps = [(inner[i]["vmax"], inner[i + 1]["vmin"]) for i in range(len(inner) - 1)]
                gaps = [g for g in gaps + [(inner[-1]["vmax"], top)] if g[1] - g[0] > 0.3]
                if not gaps:
                    continue
                alvo = self.bot + 1.6
                sel = [g for g in gaps if g[0] <= alvo <= g[1]]
                g = sel[0] if sel else max(gaps, key=lambda g: g[1] - g[0])
                op = (g[0], g[1], "janela")
            if self.tipo == "PI" and op[2] != "porta":
                continue
            if op[1] - op[0] >= 0.3:
                out.append((u0, u1, op[0], op[1], op[2]))
        return out

    # ------------------------------------------------------------------ cavities (for insulation)
    def cavidades(self, min_largura=0.03, min_area=0.005):
        """Free trapezoids between members inside the frame outline, excluding openings (elevation u, v)."""
        bloqueios = [m["poly"] for m in self.membros if m["papel"] != "empena"]
        bloqueios += [[(u0, v0), (u1, v0), (u1, v1), (u0, v1)] for u0, u1, v0, v1, _k in self.aberturas]
        xs = []
        for x in sorted(p[0] for pl in bloqueios + [self.contorno] for p in pl):
            if not xs or x - xs[-1] > 1e-7:
                xs.append(x)
        out = []
        for a, b in zip(xs, xs[1:]):
            if b - a < min_largura:
                continue
            c = (a + b) / 2
            eps = min(1e-4, (b - a) / 10)  # boundaries are linear inside a slab: sample just inside its ends
            oc = corte_vertical(self.contorno, c)
            if not oc:
                continue
            ivs = []
            for pl in bloqueios:
                r = corte_vertical(pl, c)
                if r and r[1] > oc[0] and r[0] < oc[1]:
                    ivs.append((r[0], r[1], pl))
            ivs.sort(key=lambda r: r[0])
            # walk up the slab collecting the free gaps between blocking members
            cur, below = oc[0], None
            gaps = []
            for lo, hi, pl in ivs:
                if lo > cur + 0.02:
                    gaps.append((below, pl))
                if hi > cur:
                    cur, below = hi, pl
            if oc[1] > cur + 0.02:
                gaps.append((below, None))
            for pb, pt in gaps:
                def fundo(u, pb=pb):
                    r = corte_vertical(pb if pb else self.contorno, u)
                    return r[1] if pb else r[0]

                def topo(u, pt=pt):
                    r = corte_vertical(pt if pt else self.contorno, u)
                    return r[0] if pt else r[1]

                try:
                    q = [(a, fundo(a + eps)), (b, fundo(b - eps)), (b, topo(b - eps)), (a, topo(a + eps))]
                except TypeError:
                    continue
                if q[3][1] - q[0][1] < 0.02 or q[2][1] - q[1][1] < 0.02:
                    continue
                ar = ((q[3][1] - q[0][1]) + (q[2][1] - q[1][1])) / 2 * (b - a)
                if ar >= min_area:
                    out.append(q)
        return out
