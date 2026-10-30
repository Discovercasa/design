"""Checks of a built house's timber, without Blender (pure Python; runs in the browser with the document generator).

    python ferramentas/modelo/verificar.py <config.json> [--tol 0.008] [-v]

Every timber piece as built by casa_planta.py — the modules' members (placed in 3D from their elevations), the ring
(amarração), lameladas / ceiling beams, purlins, prumos, packers, hips, valleys, gables — as a convex solid, then:
  - clashes: two pieces through one another by more than `tol` (separating-axis test, the same as
    configurador/auditar_cobertura.py, which only covered exposed roofs) — user 2026-10-30: "pode haver vigas a passar
    umas no meio das outras";
  - outside: a piece below the foundation base or outside the outline (structure), other than the roof's overhangs.
Returns {"pecas", "choques": [{"a", "b", "cm", "perto"}], "fora": [...], "ok"}; the CLI prints it.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.configurador.auditar_cobertura import penetracao, solido  # noqa: E402

TOL = 0.008  # m: deeper than this is a clash (packers and notches sit flush)
# roof pieces allowed past the outline (overhangs, gutters' supports)
BEIRAL = ("Pérgola", "Viga de apoio à cobertura", "Madre", "Rincão", "Laró", "Viga de bordo", "Viga de bordadura", "Calço", "Prumo")


def pecas_madeira(G):
    """[solid + {"nome", "tipo", "grupo"}] for every timber piece of the house."""
    out = []
    for p in G["paineis"]:
        if p.get("piso", 0) != 0 or p.get("fantasma") or p["tipo"] not in ("PE", "PI") and not p.get("empena"):
            continue
        a = G["alcados"].get(p["alcado"])
        if not a:
            continue
        ox, oy, oz = p["origem"]
        ux, uy = p["sentido"]
        t = p["espessura"]

        def mundo(u, v, w, ox=ox, oy=oy, oz=oz, ux=ux, uy=uy):
            return [ox + u * ux - w * uy, oy + u * uy + w * ux, oz + v]
        membros = a.get("members") or []
        for k, m in enumerate(membros):
            poly = m["poly"]
            if len(poly) < 3:
                continue
            s = solido({"b": [mundo(u, v, -t / 2) for u, v in poly], "t": [mundo(u, v, t / 2) for u, v in poly]})
            s.update({"nome": f"{p['nome']} · {m.get('tipo', 'membro')} {k + 1}", "tipo": m.get("tipo", "membro"),
                      "grupo": p["nome"]})
            out.append(s)
    for o in G.get("estrutura_extra", []):
        tipo = (o.get("props") or {}).get("tipo") or o["nome"]
        for k, pc in enumerate(o["pecas"]):
            if len(pc.get("b", [])) < 3:
                continue
            s = solido(pc)
            s.update({"nome": o["nome"] + (f" ({k + 1})" if len(o["pecas"]) > 1 else ""), "tipo": tipo, "grupo": o["nome"]})
            out.append(s)
    return out


def _dentro(poly, x, y, folga):
    n, dentro = len(poly), False
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            dentro = not dentro
    if dentro:
        return True
    for i in range(n):  # within `folga` of an edge counts as inside
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy or 1e-12
        t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / L2))
        if (x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2 <= folga * folga:
            return True
    return False


def verificar(G, tol=TOL):
    pecas = pecas_madeira(G)
    choques = []
    todas = sorted(pecas, key=lambda s: s["lo"][0])
    for i, s1 in enumerate(todas):
        for s2 in todas[i + 1:]:
            if s2["lo"][0] > s1["hi"][0] - tol:
                break
            if any(s1["lo"][k] > s2["hi"][k] - tol or s2["lo"][k] > s1["hi"][k] - tol for k in (1, 2)):
                continue
            p = penetracao(s1, s2)
            if p > tol:
                c = [round((max(s1["lo"][k], s2["lo"][k]) + min(s1["hi"][k], s2["hi"][k])) / 2, 2) for k in range(3)]
                choques.append({"a": s1["nome"], "b": s2["nome"], "tipos": sorted((s1["tipo"], s2["tipo"])),
                                "cm": round(p * 100, 1), "perto": c})
    choques.sort(key=lambda c: -c["cm"])
    fora = []
    cont = G.get("contorno_estrutura") or []
    for s in pecas:
        if s["lo"][2] < -0.01:
            fora.append({"peca": s["nome"], "porque": f"abaixo da base ({s['lo'][2]:.2f} m)"})
            continue
        if cont and not any(s["tipo"].startswith(b) or s["nome"].startswith(b) for b in BEIRAL):
            for x, y, _z in s["V"]:
                if not _dentro(cont, x, y, 0.02):
                    fora.append({"peca": s["nome"], "porque": f"fora do contorno perto de ({x:.2f}, {y:.2f})"})
                    break
    return {"pecas": len(pecas), "tipos": dict(Counter(s["tipo"].split(" ")[0] for s in pecas)),
            "choques": choques, "fora": fora, "ok": not choques and not fora}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("config")
    ap.add_argument("--tol", type=float, default=TOL)
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    from ferramentas.modelo.camadas import fundir, teto_sob_anel
    from ferramentas.modelo.casa_planta import construir
    cp = Path(a.config).resolve()
    cfg = json.load(open(cp, encoding="utf-8"))
    planta = json.load(open(cp.parent / cfg["planta"], encoding="utf-8"))
    S0 = json.load(open(Path(__file__).with_name("sistema_construtivo.json"), encoding="utf-8"))
    S = teto_sob_anel(fundir(S0, cfg.get("camadas") or {}), cfg)
    E = fundir(S["estrutura"], {k: v for k, v in (cfg.get("estrutura") or {}).items() if k != "sistema"})
    G, _ = construir(cfg, S, E, planta)
    r = verificar(G, a.tol)
    print(f"VERIFICAR {r['pecas']} peças; choques > {a.tol * 1000:.0f} mm: {len(r['choques'])}; fora: {len(r['fora'])}")
    por = Counter(" x ".join(c["tipos"]) for c in r["choques"])
    for k, n in por.most_common():
        print(f"  {k}: {n}")
    for c in r["choques"][: (40 if a.v else 8)]:
        print(f"    {c['cm']:5.1f} cm  {c['a']}  <>  {c['b']}  perto de {c['perto']}")
    for f in r["fora"][: (40 if a.v else 8)]:
        print(f"  fora: {f['peca']}: {f['porque']}")


if __name__ == "__main__":
    main()
