"""Terrain readers (Step Inside Phase 2, hub task 59). Standard library only.

Every reader returns the same *levantamento* dict:
    formato, ficheiro,
    pontos   [[x, y, z]]                       measured points (metres)
    linhas   [{"tipo", "z", "pts", "camada"}]  tipo: "curva" (contour, one z), "quebra" (3D breakline, z per
                                                vertex) or "linha2d" (no height: never used as heights, spec §19.4)
    faces    [[i, j, k]]                       triangles over `pontos` when the file has a surface (LandXML)
    limites  [[[x, y], ...]]                   lot / survey boundary polygons
    rotulos  [[x, y, valor]]                   numbers written as text (DXF): only used if declared
    unidade  "m" | "mm" | "cm" | "ft" | None   as stated by the file (None = the file does not say)
    crs      {"epsg", "horizontal", "vertical", "nome"} as stated by the file ({} = nothing)
    avisos   [str]                             what was skipped or looks odd
    contagens {...}

Formats: XYZ/CSV/TXT points, LandXML (points, surfaces, breaklines, contours), DXF ASCII (points, 3D polylines,
contours with elevation, 3D faces, blocks), ESRI ASCII grid (.asc DEM) and DWFx survey sheets (spot heights written
as text + the coordinate grid, georef.py). GeoTIFF and LAS/LAZ are not read here (see docs/fase2/README.md).
"""
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from . import georef
except ImportError:  # run as a script from this folder
    import georef

NUM = re.compile(r"^[-+]?\d+(?:[.,]\d+)?$")


def _novo(formato, ficheiro):
    return {"formato": formato, "ficheiro": Path(ficheiro).name, "pontos": [], "linhas": [], "faces": [],
            "limites": [], "rotulos": [], "unidade": None, "crs": {}, "avisos": [], "contagens": {}}


def _f(s):
    return float(str(s).strip().replace(",", "."))


# ------------------------------------------------------------------ XYZ / CSV
_NOMES_X = ("x", "e", "este", "easting", "m", "meridiana", "east")
_NOMES_Y = ("y", "n", "norte", "northing", "p", "perpendicular", "north")
_NOMES_Z = ("z", "h", "cota", "cotas", "elev", "elevation", "altitude", "alt", "altura")


def ler_xyz(path, colunas=None):
    """Points from a text table. colunas: optional {"x": i, "y": j, "z": k} (0-based) when the file has no header.
    Detects the separator (; , tab or spaces) and the decimal comma."""
    lev = _novo("XYZ", path)
    texto = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    linhas = [l for l in texto.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not linhas:
        lev["avisos"].append("ficheiro vazio")
        return lev
    amostra = linhas[: min(20, len(linhas))]
    sep = None
    for s in (";", "\t", ","):
        if all(s in l for l in amostra[1:] or amostra):
            sep = s
            break

    def partes(l):
        return [t.strip() for t in (l.split(sep) if sep else l.split())]

    cab = partes(linhas[0])
    tem_cab = not all(NUM.match(t) for t in cab if t)
    idx = dict(colunas or {})
    if tem_cab:
        nomes = [t.lower().strip('"') for t in cab]
        for chave, cands in (("x", _NOMES_X), ("y", _NOMES_Y), ("z", _NOMES_Z)):
            for i, nm in enumerate(nomes):
                if nm in cands and chave not in idx:
                    idx[chave] = i
                    break
        linhas = linhas[1:]
    if not {"x", "y", "z"} <= set(idx):
        n = len(partes(linhas[0]))
        if n == 3:
            idx = {"x": 0, "y": 1, "z": 2}
        elif n >= 4:  # id x y z (survey exports put the point number first)
            idx = {"x": 1, "y": 2, "z": 3}
            lev["avisos"].append("sem cabeçalho e 4+ colunas: assumido 'id x y z' (confirmar)")
        else:
            raise ValueError("não encontrei as colunas X, Y e Z")
    maus = 0
    for l in linhas:
        t = partes(l)
        try:
            lev["pontos"].append([_f(t[idx["x"]]), _f(t[idx["y"]]), _f(t[idx["z"]])])
        except (ValueError, IndexError):
            maus += 1
    if maus:
        lev["avisos"].append(f"{maus} linhas sem números válidos foram ignoradas")
    lev["contagens"] = {"pontos": len(lev["pontos"]), "colunas": idx, "cabecalho": tem_cab}
    return lev


# ------------------------------------------------------------------ LandXML
_UNIDADES_XML = {"meter": "m", "metre": "m", "millimeter": "mm", "centimeter": "cm", "foot": "ft", "USSurveyFoot": "ft"}


def _sem_ns(el):
    for e in el.iter():
        if isinstance(e.tag, str) and "}" in e.tag:
            e.tag = e.tag.split("}", 1)[1]
    return el


def _nez(texto):
    """LandXML coordinates are 'northing easting [elevation]'. Returns (x=E, y=N, z or None)."""
    v = [_f(t) for t in texto.split()]
    return v[1], v[0], (v[2] if len(v) > 2 else None)


def ler_landxml(path):
    lev = _novo("LandXML", path)
    raiz = _sem_ns(ET.parse(path).getroot())
    met = raiz.find("Units/Metric")
    imp = raiz.find("Units/Imperial")
    if met is not None:
        lev["unidade"] = _UNIDADES_XML.get(met.get("linearUnit", ""), met.get("linearUnit"))
    elif imp is not None:
        lev["unidade"] = _UNIDADES_XML.get(imp.get("linearUnit", ""), "ft")
    cs = raiz.find("CoordinateSystem")
    if cs is not None:
        lev["crs"] = {k: v for k, v in (("epsg", cs.get("epsgCode")), ("horizontal", cs.get("horizontalDatum")),
                                         ("vertical", cs.get("verticalDatum")), ("nome", cs.get("name")),
                                         ("wkt", cs.get("ogcWktCode"))) if v}
    for cg in raiz.iter("CgPoint"):
        if cg.text and cg.text.strip():
            x, y, z = _nez(cg.text)
            if z is not None:
                lev["pontos"].append([x, y, z])
    n_cg = len(lev["pontos"])
    for sup in raiz.iter("Surface"):
        ids = {}
        for p in sup.iter("P"):
            if p.text and p.text.strip():
                x, y, z = _nez(p.text)
                ids[p.get("id")] = len(lev["pontos"])
                lev["pontos"].append([x, y, z])
        for f in sup.iter("F"):
            if f.text and f.get("i") != "1":  # i="1": invisible face (outside the surface)
                t = f.text.split()
                if len(t) >= 3 and all(k in ids for k in t[:3]):
                    lev["faces"].append([ids[k] for k in t[:3]])
        for bl in sup.iter("Breakline"):
            pl = bl.find("PntList3D")
            if pl is not None and pl.text:
                v = [_f(t) for t in pl.text.split()]
                pts = [[v[i + 1], v[i], v[i + 2]] for i in range(0, len(v) - 2, 3)]
                lev["linhas"].append({"tipo": "quebra", "z": None, "pts": pts, "camada": "Breakline"})
        for ct in sup.iter("Contour"):
            pl = ct.find("PntList2D")
            if pl is not None and pl.text and ct.get("elev"):
                v = [_f(t) for t in pl.text.split()]
                z = _f(ct.get("elev"))
                pts = [[v[i + 1], v[i], z] for i in range(0, len(v) - 1, 2)]
                lev["linhas"].append({"tipo": "curva", "z": z, "pts": pts, "camada": "Contour"})
    for pb in raiz.iter("Parcel"):
        cg = pb.find("CoordGeom")
        if cg is not None:
            pts = []
            for seg in cg:
                for tag in ("Start", "End"):
                    e = seg.find(tag)
                    if e is not None and e.text:
                        x, y, _z = _nez(e.text)
                        if not pts or pts[-1] != [x, y]:
                            pts.append([x, y])
            if len(pts) >= 3:
                lev["limites"].append(pts)
    lev["contagens"] = {"pontos_cg": n_cg, "pontos_superficie": len(lev["pontos"]) - n_cg, "faces": len(lev["faces"]),
                        "linhas": len(lev["linhas"]), "limites": len(lev["limites"])}
    if not lev["unidade"]:
        lev["avisos"].append("o ficheiro não diz a unidade (Units)")
    return lev


# ------------------------------------------------------------------ DXF (ASCII)
_INSUNITS = {0: None, 1: "in", 2: "ft", 4: "mm", 5: "cm", 6: "m"}


def _pares_dxf(texto):
    ls = texto.splitlines()
    for i in range(0, len(ls) - 1, 2):
        try:
            yield int(ls[i].strip()), ls[i + 1].strip()
        except ValueError:
            continue


def _entidades(pares):
    """Group (code, value) pairs into entities of the ENTITIES section: [(type, [(code, value)])]. Also returns
    the HEADER variables."""
    sec, ents, header, cur, var = None, [], {}, None, None
    for c, v in pares:
        if c == 0:
            if cur is not None:
                ents.append(cur)
                cur = None
            if v == "SECTION":
                sec = "?"
            elif v == "ENDSEC":
                sec = None
            elif sec == "ENTITIES":
                cur = (v, [])
            continue
        if sec == "?" and c == 2:
            sec = v
            continue
        if sec == "HEADER":
            if c == 9:
                var = v
            elif var:
                header.setdefault(var, {})[c] = v
        elif cur is not None:
            cur[1].append((c, v))
    if cur is not None:
        ents.append(cur)
    return ents, header


def _g(codes, c, default=None):
    for k, v in codes:
        if k == c:
            return v
    return default


def ler_dxf(path, camadas=None):
    """camadas: optional list of layer names (or regex) to keep; default all.
    Heights are taken only from real 3D data: POINT/INSERT with z, 3D polylines, 3D faces, LINE with z, and contours
    (LWPOLYLINE / 2D POLYLINE) with a non-zero elevation. Flat 2D lines become 'linha2d' (never heights)."""
    lev = _novo("DXF", path)
    dados = Path(path).read_bytes()
    if dados.startswith(b"AutoCAD Binary DXF"):
        raise ValueError("DXF binário: voltar a exportar como DXF ASCII")
    texto = dados.decode("utf-8", errors="replace")
    ents, header = _entidades(_pares_dxf(texto))
    ins = header.get("$INSUNITS", {}).get(70)
    lev["unidade"] = _INSUNITS.get(int(ins)) if ins is not None and ins.lstrip("-").isdigit() else None
    filtro = [re.compile(c, re.I) for c in (camadas or [])]

    def quero(camada):
        return not filtro or any(f.fullmatch(camada or "") for f in filtro)

    cont = {}
    i = 0
    while i < len(ents):
        tipo, cs = ents[i]
        i += 1
        camada = _g(cs, 8, "0")
        if not quero(camada):
            if tipo == "POLYLINE":  # skip its vertices too
                while i < len(ents) and ents[i][0] in ("VERTEX", "SEQEND"):
                    i += 1
            continue
        cont[tipo] = cont.get(tipo, 0) + 1
        if tipo in ("POINT", "INSERT"):
            z = _f(_g(cs, 30, "0"))
            if z != 0:
                lev["pontos"].append([_f(_g(cs, 10)), _f(_g(cs, 20)), z])
        elif tipo == "LINE":
            p0 = [_f(_g(cs, 10)), _f(_g(cs, 20)), _f(_g(cs, 30, "0"))]
            p1 = [_f(_g(cs, 11)), _f(_g(cs, 21)), _f(_g(cs, 31, "0"))]
            if p0[2] or p1[2]:
                lev["linhas"].append({"tipo": "quebra", "z": None, "pts": [p0, p1], "camada": camada})
            else:
                lev["linhas"].append({"tipo": "linha2d", "z": None, "pts": [p0[:2] + [None], p1[:2] + [None]],
                                      "camada": camada})
        elif tipo == "LWPOLYLINE":
            xs = [_f(v) for c, v in cs if c == 10]
            ys = [_f(v) for c, v in cs if c == 20]
            elev = _f(_g(cs, 38, "0"))
            fech = int(_g(cs, 70, "0")) & 1
            pts = [[x, y] for x, y in zip(xs, ys)]
            if fech and pts:
                pts.append(pts[0][:])
            if elev:
                lev["linhas"].append({"tipo": "curva", "z": elev, "pts": [p + [elev] for p in pts], "camada": camada})
            else:
                lev["linhas"].append({"tipo": "linha2d", "z": None, "pts": [p + [None] for p in pts], "camada": camada})
        elif tipo == "POLYLINE":
            flag = int(_g(cs, 70, "0"))
            elev = _f(_g(cs, 30, "0"))
            vs = []
            while i < len(ents) and ents[i][0] in ("VERTEX", "SEQEND"):
                t2, c2 = ents[i]
                i += 1
                if t2 == "VERTEX":
                    vs.append([_f(_g(c2, 10)), _f(_g(c2, 20)), _f(_g(c2, 30, "0"))])
            if flag & 1 and vs:
                vs.append(vs[0][:])
            if flag & (16 | 64):
                lev["avisos"].append(f"malha POLYLINE (flag {flag}) na camada {camada}: lida só como pontos")
                lev["pontos"] += [v for v in vs if v[2]]
            elif flag & 8 and any(v[2] for v in vs):
                lev["linhas"].append({"tipo": "quebra", "z": None, "pts": vs, "camada": camada})
            elif flag & 8:  # a "3D" polyline with every z = 0 has no heights: it is a 2D line
                lev["linhas"].append({"tipo": "linha2d", "z": None, "pts": [[x, y, None] for x, y, _ in vs],
                                      "camada": camada})
            elif elev:
                lev["linhas"].append({"tipo": "curva", "z": elev, "pts": [[x, y, elev] for x, y, _ in vs],
                                      "camada": camada})
            else:
                lev["linhas"].append({"tipo": "linha2d", "z": None, "pts": [[x, y, None] for x, y, _ in vs],
                                      "camada": camada})
        elif tipo == "3DFACE":
            k0 = len(lev["pontos"])
            vs = [[_f(_g(cs, 10 + j)), _f(_g(cs, 20 + j)), _f(_g(cs, 30 + j, "0"))] for j in range(4)]
            if not any(v[2] for v in vs):  # a flat face at z = 0: drawing, not terrain
                continue
            if vs[3] == vs[2]:
                vs = vs[:3]
            lev["pontos"] += vs
            lev["faces"].append([k0, k0 + 1, k0 + 2])
            if len(vs) == 4:
                lev["faces"].append([k0, k0 + 2, k0 + 3])
        elif tipo in ("TEXT", "MTEXT"):
            t = (_g(cs, 1, "") or "").strip()
            t = re.sub(r"\\[A-Za-z][^;]*;|[{}]", "", t)  # MTEXT formatting codes
            if NUM.match(t):
                lev["rotulos"].append([_f(_g(cs, 10)), _f(_g(cs, 20)), _f(t)])
    # GNSS point labels written as text, one value per text ("E=-10000.123m.", "N=…", "h=…"): kept in file order
    cur = {}
    lev["gnss"] = []
    for tipo, cs in ents:
        if tipo not in ("TEXT", "MTEXT"):
            continue
        t = (_g(cs, 1, "") or "").strip()
        m = re.match(r"^\s*([ENhHZ])\s*=\s*(-?\d+(?:[.,]\d+)?)", t)
        if m:
            cur[{"E": "E", "N": "N"}.get(m.group(1), "h")] = _f(m.group(2))
            if len(cur) == 3:
                lev["gnss"].append([cur["E"], cur["N"], cur["h"]])
                cur = {}
    # the coordinate system written on the drawing, in any text (survey legends are often blocks: "... EPSG:3763")
    for c, v in _pares_dxf(texto):
        if c in (1, 3) and (m := re.search(r"EPSG\s*:?\s*(\d{4,5})", v)):
            lev["crs"] = {"epsg": m.group(1), "nome": re.sub(r"\\[A-OQ-Za-z][^;]*;|[{}]|\\P", " ", v).strip()[:120]}
            break
    curvas = [l for l in lev["linhas"] if l["tipo"] == "curva"]
    planas = [l for l in lev["linhas"] if l["tipo"] == "linha2d"]
    lev["contagens"] = {"entidades": cont, "pontos": len(lev["pontos"]), "curvas": len(curvas),
                        "quebras": sum(1 for l in lev["linhas"] if l["tipo"] == "quebra"), "linhas_2d": len(planas),
                        "faces": len(lev["faces"]), "rotulos_numericos": len(lev["rotulos"])}
    if planas and not curvas and not lev["pontos"]:
        lev["avisos"].append("só linhas 2D sem cota: não dão terreno (exportar com elevação ou pontos 3D)")
    if lev["unidade"] is None:
        lev["avisos"].append("$INSUNITS ausente ou 0: o DXF não diz a unidade")
    return lev


# ------------------------------------------------------------------ ESRI ASCII grid (DEM)
def ler_asc(path, passo=1):
    """ESRI ASCII grid. passo: keep every n-th cell in both directions (thin a dense DEM)."""
    lev = _novo("ASC", path)
    cab, dados = {}, []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for linha in fh:
            t = linha.split()
            if not t:
                continue
            if len(cab) < 6 and re.match(r"[A-Za-z]", t[0]):
                cab[t[0].lower()] = _f(t[1])
                continue
            dados.append(t)
    nc, nr, cel = int(cab["ncols"]), int(cab["nrows"]), cab["cellsize"]
    nd = cab.get("nodata_value")
    if "xllcenter" in cab:
        x0, y0 = cab["xllcenter"], cab["yllcenter"]
    else:
        x0, y0 = cab["xllcorner"] + cel / 2, cab["yllcorner"] + cel / 2
    vals = [v for row in dados for v in row]
    if len(vals) != nc * nr:
        lev["avisos"].append(f"esperava {nc * nr} valores e li {len(vals)}")
    vazios = 0
    for r in range(0, nr, passo):
        for c in range(0, nc, passo):
            k = r * nc + c
            if k >= len(vals):
                break
            z = _f(vals[k])
            if nd is not None and z == nd:
                vazios += 1
                continue
            lev["pontos"].append([x0 + c * cel, y0 + (nr - 1 - r) * cel, z])
    lev["contagens"] = {"colunas": nc, "linhas": nr, "celula": cel, "sem_dados": vazios, "pontos": len(lev["pontos"])}
    lev["avisos"].append("ESRI ASCII grid não tem unidade nem CRS: declarar (ou ler do .prj ao lado)")
    return lev


# ------------------------------------------------------------------ DWFx survey sheet
def _estilo(p, regra):
    if "fill" in regra:
        return (p["fill"] or "").upper() == regra["fill"].upper() and not p["stroke"]
    return (p["stroke"] or "").upper() == regra.get("stroke", "").upper() and \
        abs(p["sw"] - regra.get("sw", p["sw"])) < 0.015


def tracejado(paths, regra, comprimento=(0.8, 6.0), folga=3.0, folga_juntar=10.0, folga_fechar=60.0):
    """A dashed line drawn as small filled quads (AutoCAD plots of thick dashed linetypes): join the dashes
    into polylines. Returns [[(x, y), ...]] in sheet mm, longest first. A chain whose ends are closer than
    folga_fechar is closed (the caller reports the length of the closing gap)."""
    tracos = []
    for p in paths:
        if not _estilo(p, regra):
            continue
        for pts, _cl in p["subs"]:
            q = pts[:-1] if len(pts) == 5 and pts[0] == pts[-1] else pts
            if len(q) != 4:
                continue
            lados = [math.dist(q[i], q[(i + 1) % 4]) for i in range(4)]
            k = 0 if lados[0] + lados[2] < lados[1] + lados[3] else 1  # the two short sides
            a = ((q[k][0] + q[k + 1][0]) / 2, (q[k][1] + q[k + 1][1]) / 2)
            b = ((q[k + 2][0] + q[(k + 3) % 4][0]) / 2, (q[k + 2][1] + q[(k + 3) % 4][1]) / 2)
            if comprimento[0] <= math.dist(a, b) <= comprimento[1] and min(lados) < 1.0:
                tracos.append((a, b))
    livres = set(range(len(tracos)))
    cadeias = []
    while livres:
        i = livres.pop()
        cad = [tracos[i][0], tracos[i][1]]
        for _lado in (0, 1):
            while True:
                fim = cad[-1]
                melhor, md, inv = None, folga, False
                for j in livres:
                    for e, rev in ((tracos[j][0], False), (tracos[j][1], True)):
                        dd = math.dist(fim, e)
                        if dd < md:
                            melhor, md, inv = j, dd, rev
                if melhor is None:
                    break
                livres.discard(melhor)
                a, b = tracos[melhor]
                cad += [b, a] if inv else [a, b]
            cad.reverse()
        cadeias.append(cad)

    def comp(c):
        return sum(math.dist(c[i], c[i + 1]) for i in range(len(c) - 1))

    # second pass: corners leave bigger gaps between dashes; join chain ends closer than folga_juntar
    juntou = True
    while juntou and len(cadeias) > 1:
        juntou = False
        cadeias.sort(key=lambda c: -comp(c))
        a = cadeias[0]
        melhor = None
        for j, b in enumerate(cadeias[1:], 1):
            for fa, fb, ra, rb in ((a[-1], b[0], False, False), (a[-1], b[-1], False, True),
                                   (a[0], b[-1], True, True), (a[0], b[0], True, False)):
                dd = math.dist(fa, fb)
                if dd < folga_juntar and (melhor is None or dd < melhor[0]):
                    melhor = (dd, j, ra, rb)
        if melhor:
            _dd, j, ra, rb = melhor
            b = cadeias.pop(j)
            a = a[::-1] if ra else a
            b = b[::-1] if rb else b
            cadeias[0] = a + b
            juntou = True
    for c in cadeias:
        if len(c) > 6 and math.dist(c[0], c[-1]) < folga_fechar:
            c.append(c[0])
    cadeias.sort(key=lambda c: -comp(c))
    return cadeias


def ler_dwfx(path, folha, cfg):
    """Spot heights written as text on a survey sheet, plus (optional) contour and boundary strokes.
    cfg (from the project's terreno.json, all optional):
      pontos_cotados: {"altura_texto": [min, max] mm, "angulo": 0, "intervalo_z": [min, max], "posicao": "origem"|"centro"}
      curvas: [{"stroke": "#808080", "sw": 0.08}, ...]   contour strokes (2D: z found later from the points)
      limite: {"stroke": "#000000", "sw": 0.19}          boundary stroke
      escala: 500                                        only used when the sheet has no coordinate grid
    Coordinates: the sheet's coordinate grid (georef.grelha_dwfx) when there is one, else sheet metres (local)."""
    import sys
    from pathlib import Path as _P
    bob = _P(__file__).resolve().parents[3]
    if str(bob) not in sys.path:
        sys.path.insert(0, str(bob))
    from ferramentas.dwfx.leitor import Dwfx, linhas as juntar

    lev = _novo("DWFx", path)
    d = Dwfx(path)
    tx = juntar(d.glyphs(folha))
    paths = d.paths(folha)
    g = georef.grelha_dwfx(tx, paths)
    pc = cfg.get("pontos_cotados", {})
    hmin, hmax = pc.get("altura_texto", [1.0, 3.0])
    zmin, zmax = pc.get("intervalo_z", [-500, 5000])
    ang = pc.get("angulo", 0)
    posicao = pc.get("posicao", "origem")
    if g:
        coef = g["coef"]

        def mundo(x, y):
            return georef.aplicar(coef, (x, y))
        lev["georef"] = {k: v for k, v in g.items() if k != "pares"}
        lev["georef"]["controlos"] = []
        for s, w in georef.pontos_coordenados(tx):
            X, Y = mundo(*s)
            lev["georef"]["controlos"].append({"folha_mm": [round(s[0], 2), round(s[1], 2)], "rotulo": list(w),
                                               "erro_m": round(math.hypot(X - w[0], Y - w[1]), 3)})
    else:
        esc = cfg.get("escala")
        if not esc:
            raise ValueError("a folha não tem quadrícula de coordenadas: declarar 'escala' no terreno.json")
        f = esc / 1000.0

        def mundo(x, y):
            return (x * f, -y * f)
        lev["avisos"].append("sem quadrícula de coordenadas: coordenadas locais da folha (sem georreferência)")
    for l in tx:
        t = l["text"].strip()
        if l["ang"] != ang or not (hmin <= l["h"] <= hmax) or not NUM.match(t):
            continue
        z = _f(t)
        if not (zmin <= z <= zmax):
            continue
        x, y = l["x"], l["y"]
        if posicao == "centro":  # middle of the label (character advance ~0.55 h)
            x, y = x + len(t) * l["h"] * 0.55 / 2, y - l["h"] / 2
        elif posicao == "ponto_decimal":  # PT convention: the decimal point is the surveyed point
            k = max(t.find("."), t.find(","))
            if k > 0:  # digits ~0.556 em wide, the point ~0.278 em, centred just above the baseline
                x, y = x + k * 0.556 * l["h"] + 0.139 * l["h"], y - 0.05 * l["h"]
        lev["pontos"].append(list(mundo(x, y)) + [z])
        lev.setdefault("pontos_folha", []).append([round(l["x"], 1), round(l["y"], 1), t])  # where to look
    rc = cfg.get("rotulos_curvas")  # contour value labels, written along the line (centre on the contour)
    if rc:
        h0, h1 = rc.get("altura_texto", [1.75, 1.9])
        for l in tx:
            t = l["text"].strip()
            if not (h0 <= l["h"] <= h1) or not NUM.match(t) or not (zmin <= _f(t) <= zmax):
                continue
            a = math.radians(l["ang"])
            meio = len(t) * l["h"] * 0.55 / 2
            x = l["x"] + math.cos(a) * meio - math.sin(a) * l["h"] / 2
            y = l["y"] - math.sin(a) * meio - math.cos(a) * l["h"] / 2
            lev["rotulos"].append(list(mundo(x, y)) + [_f(t)])
    for regra_curva in cfg.get("curvas", []):
        for p in paths:
            if _estilo(p, regra_curva):
                for pts, _cl in p["subs"]:
                    if len(pts) >= 2:
                        lev["linhas"].append({"tipo": "linha2d", "z": None, "pts": [list(mundo(*q)) + [None] for q in pts],
                                              "camada": "curva " + regra_curva.get("stroke", ""),
                                              "papel": regra_curva.get("papel", "curva")})
    lim = cfg.get("limite")
    if lim and lim.get("tracejado"):  # dashes drawn as filled quads: the longest chain is the boundary
        cad = tracejado(paths, lim)
        if cad:
            lev["limites"].append([list(mundo(*q)) for q in cad[0]])
            fechado = cad[0][0] == cad[0][-1]
            if not fechado:
                lev["avisos"].append("limite do terreno: a linha tracejada não fecha (ver o desenho)")
    elif lim:
        for p in paths:
            if _estilo(p, lim):
                for pts, _cl in p["subs"]:
                    if len(pts) >= 3:
                        lev["limites"].append([list(mundo(*q)) for q in pts])
    lev["unidade"] = "m"
    lev["contagens"] = {"pontos_cotados": len(lev["pontos"]), "curvas_2d": len(lev["linhas"]),
                        "vertices_curvas": sum(len(l["pts"]) for l in lev["linhas"]), "limites": len(lev["limites"]),
                        "posicao_do_ponto": posicao}
    return lev


LEITORES = {".xyz": ler_xyz, ".csv": ler_xyz, ".txt": ler_xyz, ".pts": ler_xyz, ".xml": ler_landxml,
            ".landxml": ler_landxml, ".dxf": ler_dxf, ".asc": ler_asc}


def ler(path, **kw):
    """Pick the reader by extension (DWFx needs ler_dwfx with the sheet and its rules)."""
    ext = Path(path).suffix.lower()
    if ext not in LEITORES:
        raise ValueError(f"sem leitor de terreno para {ext}")
    return LEITORES[ext](path, **kw)
