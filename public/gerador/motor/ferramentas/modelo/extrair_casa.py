"""Extract the geometry of a timber-frame house from its DWFx drawings, driven by a config.json.

    python ferramentas/modelo/extrair_casa.py "<project>/modelos/<type>/config.json"

Output: <config dir>/<saida.geometria> (compact JSON, model coordinates in metres):
    X = east from the west outer face, Y = north from the south outer face, Z = up from top of slab.

Method (see .claude/skills/modelo-blender-madeira/SKILL.md for the full reasoning):
  - wall panels: clusters of timber members in the elevation region, named by the label below-left;
  - placement: each plan label gives a first guess; the panel's stud pattern is matched against the
    cut studs of the plan (both directions); median refinement; exterior panels snapped per facade;
  - config corrections for drawing errors; sloped-top upper panels must face the ridge.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.dwfx.leitor import Dwfx  # noqa: E402
from ferramentas.dwfx.pecas import build_members, cluster, in_region  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def elevations(members, glyphs, cfg, S):
    pw = cfg["paredes"]
    pref = tuple(pw.get("prefixos", ["PE", "PI"]))
    labels = [g for g in glyphs if g[2] == 0 and g[4].strip().startswith(pref)]
    out = {}
    for c in cluster(in_region(members, pw["regiao_alcados"])):
        x0, y0, x1, y1 = c["bbox"]
        cands = [l for l in labels if x0 - 3 <= l[0] <= x0 + 25 and y1 - 1 <= l[1] <= y1 + 12]
        if not cands:
            continue
        name = min(cands, key=lambda l: abs(l[1] - y1) + abs(l[0] - x0))[4].strip()
        mems = []
        for m in c["members"]:
            poly = [((px - x0) * S, (y1 - py) * S) for px, py in m["poly"]]
            us = [p[0] for p in poly]
            vs = [p[1] for p in poly]
            if max(us) - min(us) < 0.02 or max(vs) - min(vs) < 0.02:
                continue  # drawing slivers
            mems.append({"section": m["section"], "poly": [[round(u, 5), round(v, 5)] for u, v in poly]})
        studs = []
        for m in mems:
            us = [p[0] for p in m["poly"]]
            vs = [p[1] for p in m["poly"]]
            du, dv = max(us) - min(us), max(vs) - min(vs)
            if dv > 2.5 * du and dv > 0.4 and du < 0.2:
                cu = (min(us) + max(us)) / 2
                if all(abs(cu - s) > 0.02 for s in studs):  # studs are often drawn in 2 pieces (above/below nogging)
                    studs.append(cu)
        bots = [m for m in mems if min(p[1] for p in m["poly"]) < 0.01 and
                max(p[0] for p in m["poly"]) - min(p[0] for p in m["poly"]) > 0.15]
        out[name] = {"W": (x1 - x0) * S, "H": (y1 - y0) * S, "members": mems, "studs": sorted(studs),
                     "frame_u0": min(min(p[0] for p in m["poly"]) for m in bots),
                     "frame_u1": max(max(p[0] for p in m["poly"]) for m in bots),
                     "section": mems[0]["section"]}
    return out


def place_panels(members, glyphs, elev, cfg, S):
    pw = cfg["paredes"]
    pref = tuple(pw.get("prefixos", ["PE", "PI"]))
    offs = {int(k): v for k, v in pw.get("rotulo_offsets", {"0": -0.6, "-90": -0.5, "90": 0.65}).items()}
    alias = pw.get("alias", {})
    wrong = pw.get("rotulos_errados", [])
    casa = cfg["casa"]
    t_ext = casa["espessura_exterior"]
    niv = cfg["niveis"]
    panels = []
    for lvl_s, region in pw["plantas"].items():
        lvl = int(lvl_s)
        pm = in_region(members, region)
        hx0 = min(m["bbox"][0] for m in pm)
        hy1 = max(m["bbox"][3] for m in pm)
        studs = [((m["bbox"][0] + m["bbox"][2]) / 2, (m["bbox"][1] + m["bbox"][3]) / 2) for m in pm
                 if m["kind"] == "corte" and min(m["bbox"][2] - m["bbox"][0], m["bbox"][3] - m["bbox"][1]) * S >= 0.05]
        x0r, y0r, x1r, y1r = region
        for lx, ly, ang, _h, text in glyphs:
            name = text.strip()
            if not name.startswith(pref) or not (x0r <= lx <= x1r + 6 and y0r - 6 <= ly <= y1r):
                continue
            ename = alias.get(name, name)
            for w in wrong:
                if w["rotulo"] == name and w["piso"] == lvl and w.get("angulo", ang) == ang:
                    ename = w["alcado"]
            if ename not in elev:
                print(f"  ! no elevation for label {name} (level {lvl})")
                continue
            E = elev[ename]
            W = E["W"] / S
            horiz = ang == 0
            guess = (lx if horiz else ly) + offs.get(ang, 0.0)
            if ang == 90:
                guess -= W
            perp_label = ly if horiz else lx
            along = [((x if horiz else y), (y if horiz else x)) for x, y in studs]
            best = None
            bands = sorted(set(round(p) for a, p in along if abs(p - perp_label) < 9 and guess - 3 <= a <= guess + W + 3))
            for band in bands:
                pts = [a for a, p in along if abs(p - band) <= 1.2]
                perps = [p for a, p in along if abs(p - band) <= 1.2]
                perp = sum(perps) / len(perps)
                for d in (1, -1):
                    for k in range(-80, 81):
                        a0 = guess + k * 0.05
                        pred = [a0 + (s / S if d == 1 else W - s / S) for s in E["studs"]]
                        hit = sum(1 for q in pred if min(abs(q - p) for p in pts) < 0.5)
                        inside = [p for p in pts if a0 + 0.3 < p < a0 + W - 0.3]
                        extra = sum(1 for p in inside if min((abs(p - q) for q in pred), default=99) > 0.6)
                        score = hit - 0.7 * extra - 0.03 * abs(k)
                        if best is None or score > best[0] + 1e-9:
                            best = (score, perp, d, a0, hit, extra, pts)
            if best is None:
                print(f"  ! could not place {name}")
                continue
            _s, perp, d, a0, hit, extra, pts = best
            diffs = sorted(p - q for q in (a0 + (s / S if d == 1 else W - s / S) for s in E["studs"])
                           for p in [min(pts, key=lambda p, q=q: abs(p - q))] if abs(p - q) < 0.5)
            if diffs:
                a0 += diffs[len(diffs) // 2]
            if horiz:
                sx0 = a0 if d == 1 else a0 + W
                ox, oy = (sx0 - hx0) * S, (hy1 - perp) * S
                ux, uy = (1.0, 0.0) if d == 1 else (-1.0, 0.0)
            else:
                sy0 = a0 if d == 1 else a0 + W
                ox, oy = (perp - hx0) * S, (hy1 - sy0) * S
                ux, uy = (0.0, -1.0) if d == 1 else (0.0, 1.0)
            kind = "PI" if ename.startswith("PI") else "PE"
            z0 = niv["piso0"] if lvl == 0 else (niv["piso1_exterior"] if kind == "PE" else niv["piso1_interior"])
            nome = ename if (kind == "PI" and name.startswith("PE")) else name
            panels.append({"nome": nome, "alcado": ename, "piso": lvl, "tipo": kind, "origem": [ox, oy, z0],
                           "sentido": [ux, uy], "espessura": 0.16 if E["section"] == "160x80" else 0.10,
                           "encaixe": f"{hit}/{len(E['studs'])}", "extra": extra})

    # symmetric panels: convention (exterior elevations are drawn as seen from outside)
    for p in panels:
        if p["nome"] in pw.get("forcar_sentido", {}):
            e = elev[p["alcado"]]
            nu = pw["forcar_sentido"][p["nome"]]
            if nu != p["sentido"]:
                f0, f1 = e["frame_u0"], e["frame_u1"]
                ux, uy = p["sentido"]
                p["origem"][0] += ux * (f0 + f1)
                p["origem"][1] += uy * (f0 + f1)
                p["sentido"] = [float(nu[0]), float(nu[1])]

    # exterior facades: long walls (N/S) run through the corners, end walls (W/E) fit between them
    L, D, t = casa["comprimento"], casa["profundidade"], t_ext
    for lvl in {p["piso"] for p in panels}:
        for fac, axis, fixed, start, total in (("N", 0, D - t / 2, 0.0, L), ("S", 0, t / 2, 0.0, L),
                                               ("W", 1, t / 2, t, D - 2 * t), ("E", 1, L - t / 2, t, D - 2 * t)):
            grp = [p for p in panels if p["piso"] == lvl and p["tipo"] == "PE"
                   and abs(p["sentido"][axis]) > 0.5 and abs(p["origem"][1 - axis] - fixed) < 0.05]
            if not grp:
                continue
            def fmin(p):
                e = elev[p["alcado"]]
                return min(p["origem"][axis] + p["sentido"][axis] * e["frame_u0"],
                           p["origem"][axis] + p["sentido"][axis] * e["frame_u1"])
            grp.sort(key=fmin)
            widths = [elev[p["alcado"]]["frame_u1"] - elev[p["alcado"]]["frame_u0"] for p in grp]
            if abs(sum(widths) - total) > 0.03:
                print(f"  ! facade {fac} level {lvl}: widths sum {sum(widths):.3f} != {total:.3f} (not snapped)")
                continue
            pos = start
            for p, w in zip(grp, widths):
                e = elev[p["alcado"]]
                a, b = pos, pos + w
                o = a - e["frame_u0"] if p["sentido"][axis] > 0 else b + e["frame_u0"]
                p["origem"][axis] = o
                p["origem"][1 - axis] = fixed
                pos = b

    # manual corrections (drawing inconsistencies)
    for p in panels:
        c = pw.get("correcoes", {}).get(p["nome"])
        if not c:
            continue
        if "origem_x" in c:
            p["origem"][0] = c["origem_x"]
        if "origem_y" in c:
            p["origem"][1] = c["origem_y"]
        if "origem" in c:
            p["origem"][0], p["origem"][1] = c["origem"]
        if "sentido" in c:
            p["sentido"] = [float(v) for v in c["sentido"]]
        if "espessura" in c:
            p["espessura"] = c["espessura"]

    # upper floor panels with sloped tops: the high end must face the ridge line
    cob = cfg.get("cobertura", {})
    if "cumeeira_y" in cob:
        yr = cob["cumeeira_y"]
        for p in panels:
            if p["piso"] != 1 or abs(p["sentido"][1]) < 0.5:
                continue
            e = elev[p["alcado"]]
            f0, f1 = e["frame_u0"], e["frame_u1"]
            pts = [q for m in e["members"] for q in m["poly"]]
            top0 = max(v for u, v in pts if u <= f0 + 0.12)
            top1 = max(v for u, v in pts if u >= f1 - 0.12)
            if abs(top0 - top1) < 0.2:
                continue
            ox, oy = p["origem"][0], p["origem"][1]
            ux, uy = p["sentido"]
            ys, ye = oy + uy * f0, oy + uy * f1
            hi, lo = (ys, ye) if top0 > top1 else (ye, ys)
            if abs(hi - yr) > abs(lo - yr):
                print(f"  flipped {p['nome']} (sloped top must face the ridge)")
                p["origem"] = [ox + ux * (f0 + f1), oy + uy * (f0 + f1), p["origem"][2]]
                p["sentido"] = [-ux, -uy]
    for p in panels:
        p["origem"] = [round(v, 4) for v in p["origem"]]
    return panels


def plan_members(members, region, S, mode):
    ms = in_region(members, region)
    x0 = min(m["bbox"][0] for m in ms)
    y1 = max(m["bbox"][3] for m in ms)
    ymid = (min(m["bbox"][1] for m in ms) + y1) / 2
    out = []
    for m in ms:
        bx0, by0, bx1, by1 = m["bbox"]
        if min(bx1 - bx0, by1 - by0) * S < 0.03:
            continue
        if mode == "pavimento":
            out.append({"x0": round((bx0 - x0) * S, 4), "x1": round((bx1 - x0) * S, 4),
                        "y0": round((y1 - by1) * S, 4), "y1": round((y1 - by0) * S, 4)})
        else:  # roof plan: s = distance from the ridge measured on the drawing (true length along the slope)
            out.append({"x0": round((bx0 - x0) * S, 4), "x1": round((bx1 - x0) * S, 4),
                        "s0": round((ymid - by1) * S, 4), "s1": round((ymid - by0) * S, 4)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    a = ap.parse_args()
    cfg_path = Path(a.config).resolve()
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    base = cfg_path.parent
    S = cfg.get("escala", 50) / 1000.0
    dw = Dwfx(base / cfg["dwfx"])
    fw = cfg["folhas"]["paredes"]
    fe = cfg["folhas"]["estrutura"]
    mw = build_members(dw.paths(fw))
    gw = dw.glyphs(fw)
    elev = elevations(mw, gw, cfg, S)
    panels = place_panels(mw, gw, elev, cfg, S)
    me = build_members(dw.paths(fe))
    geo = {
        "nome": cfg["nome"], "descricao": cfg.get("descricao", ""), "casa": cfg["casa"], "niveis": cfg["niveis"],
        "cobertura": cfg.get("cobertura", {}), "fundacao": cfg.get("fundacao", {}),
        "notas_modelo": cfg.get("notas_modelo", []), "origem_desenhos": cfg["dwfx"],
        "alcados": elev, "paineis": panels,
        "pavimento": {"pecas": plan_members(me, cfg["pavimento"]["regiao"], S, "pavimento"),
                      "abertura_escada": cfg["pavimento"].get("abertura_escada")},
        "cobertura_planta": plan_members(me, cfg["cobertura"]["regiao"], S, "cobertura"),
    }
    out = base / cfg["saida"]["geometria"]
    out.write_text(json.dumps(geo, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    weak = [p for p in panels if p["extra"] or p["encaixe"].split("/")[0] != p["encaixe"].split("/")[1]]
    print(f"elevations: {len(elev)}  panels placed: {len(panels)}  floor pieces: {len(geo['pavimento']['pecas'])}"
          f"  roof pieces: {len(geo['cobertura_planta'])}")
    for p in weak:
        print(f"  check {p['nome']}: studs matched {p['encaixe']}, extra {p['extra']}")
    print(f"written {out}")


if __name__ == "__main__":
    main()
