"""The surroundings of a house from open data, for the client page and the 360° tour (standard library only).

What the windows see, without photos of the site (user 2026-11-12: «não vamos conseguir ter fotos das casas»):
  - near: the project's own survey (the house description does it);
  - middle (~2 km): OpenStreetMap — buildings (height from height / building:levels, else by footprint), roads,
    land use (fields, scrub, woods, beach, water), single trees; ODbL, © OpenStreetMap contributors;
  - far (~25 km): a terrain model (Copernicus GLO-30 DSM, 1 arc-second GeoTIFF; or any lon/lat float GeoTIFF) for the
    hills and the skyline; the sea at 0 m.
Coordinates: projects are surveyed in PT-TM06 (EPSG:3763, ETRS89); OSM and the DEM are lon/lat (ETRS89 ~ WGS84).
Everything leaves this module in the house frame (rotation `rot` about origin `O`, z = 0 at the reference floor `z0`).
The data files stay local next to the project (`_trabalho/<obra>/envolvente/`): they locate a client's house.

    python ferramentas/pagina/envolvente.py ptm06 <E> <N>            -> lat lon (check)
    python ferramentas/pagina/envolvente.py osm <lat> <lon> <raio_m> <saida.json>   (downloads: ask the user first)
    python ferramentas/pagina/envolvente.py dem-info <ficheiro.tif>
"""
import json
import math
import struct
import sys
import urllib.parse
import urllib.request
import zlib

# ---------------------------------------------------------------------------------------------- PT-TM06 <-> lat/lon
_A, _F = 6378137.0, 1 / 298.257222101            # GRS80
_N = _F / (2 - _F)
_AA = _A / (1 + _N) * (1 + _N ** 2 / 4 + _N ** 4 / 64)
_AL = (_N / 2 - 2 * _N ** 2 / 3 + 5 * _N ** 3 / 16, 13 * _N ** 2 / 48 - 3 * _N ** 3 / 5, 61 * _N ** 3 / 240)
_BE = (_N / 2 - 2 * _N ** 2 / 3 + 37 * _N ** 3 / 96, _N ** 2 / 48 + _N ** 3 / 15, 17 * _N ** 3 / 480)
_DE = (2 * _N - 2 * _N ** 2 / 3 - 2 * _N ** 3, 7 * _N ** 2 / 3 - 8 * _N ** 3 / 5, 56 * _N ** 3 / 15)
_LAT0, _LON0 = math.radians(39 + 40 / 60 + 5.73 / 3600), math.radians(-(8 + 7 / 60 + 59.19 / 3600))
_C = 2 * math.sqrt(_N) / (1 + _N)


def _xi_eta(lat, dlon):
    s = math.sin(lat)
    t = math.sinh(math.atanh(s) - _C * math.atanh(_C * s))
    xi, eta = math.atan2(t, math.cos(dlon)), math.atanh(math.sin(dlon) / math.sqrt(1 + t * t))
    x = xi + sum(a * math.sin(2 * j * xi) * math.cosh(2 * j * eta) for j, a in enumerate(_AL, 1))
    e = eta + sum(a * math.cos(2 * j * xi) * math.sinh(2 * j * eta) for j, a in enumerate(_AL, 1))
    return x, e


_XI0 = _xi_eta(_LAT0, 0.0)[0]


def latlon_para_ptm06(lat, lon):
    x, e = _xi_eta(math.radians(lat), math.radians(lon) - _LON0)
    return _AA * e, _AA * (x - _XI0)


def ptm06_para_latlon(E, N):
    xi, eta = N / _AA + _XI0, E / _AA
    x = xi - sum(b * math.sin(2 * j * xi) * math.cosh(2 * j * eta) for j, b in enumerate(_BE, 1))
    e = eta - sum(b * math.cos(2 * j * xi) * math.sinh(2 * j * eta) for j, b in enumerate(_BE, 1))
    chi = math.asin(math.sin(x) / math.cosh(e))
    lat = chi + sum(d * math.sin(2 * j * chi) for j, d in enumerate(_DE, 1))
    return math.degrees(lat), math.degrees(_LON0 + math.atan2(math.sinh(e), math.cos(x)))


# ---------------------------------------------------------------------------------------------- OpenStreetMap
OVERPASS = "https://overpass-api.de/api/interpreter"


def descarregar_osm(lat, lon, raio, saida):
    """Buildings, roads, land use, natural areas, trees and water inside a square of half-side `raio` metres."""
    dlat = raio / 111320.0
    dlon = raio / (111320.0 * math.cos(math.radians(lat)))
    bb = f"{lat - dlat:.5f},{lon - dlon:.5f},{lat + dlat:.5f},{lon + dlon:.5f}"
    q = f"""[out:json][timeout:120];
(
  way["building"]({bb}); relation["building"]({bb});
  way["highway"]({bb});
  way["landuse"]({bb}); relation["landuse"]({bb});
  way["natural"]({bb}); relation["natural"]({bb}); node["natural"="tree"]({bb});
  way["leisure"]({bb}); way["waterway"]({bb}); way["barrier"="wall"]({bb});
);
out geom;"""
    pedido = urllib.request.Request(OVERPASS, data=urllib.parse.urlencode({"data": q}).encode(),
                                    headers={"User-Agent": "BOB-envolvente/1.0"})
    with urllib.request.urlopen(pedido, timeout=200) as r:
        dados = r.read()
    open(saida, "wb").write(dados)
    return len(dados)


# ---------------------------------------------------------------------------------------------- GeoTIFF (lon/lat DEM)
class Dem:
    """Minimal GeoTIFF reader: one band, int16/float32, tiled or stripped, no/deflate/LZW compression, predictor
    1/2/3, geographic ModelPixelScale + ModelTiepoint. Reads only the tiles that are sampled."""

    def __init__(self, caminho):
        self.f = open(caminho, "rb")
        cab = self.f.read(8)
        self.e = "<" if cab[:2] == b"II" else ">"
        if struct.unpack(self.e + "H", cab[2:4])[0] != 42:
            raise ValueError("BigTIFF não suportado")
        off = struct.unpack(self.e + "I", cab[4:8])[0]
        self.tags = self._ifd(off)
        t = self.tags
        self.w, self.h = t[256][0], t[257][0]
        self.bits = t[258][0]
        self.comp = t.get(259, [1])[0]
        self.pred = t.get(317, [1])[0]
        self.fmt = t.get(339, [1])[0]
        if 322 in t:
            self.tw, self.th = t[322][0], t[323][0]
            self.offs, self.lens = t[324], t[325]
        else:
            self.tw, self.th = self.w, t.get(278, [self.h])[0]
            self.offs, self.lens = t[273], t[279]
        esc, tie = t[33550], t[33922]
        self.dx, self.dy = esc[0], esc[1]
        self.x0, self.y0 = tie[3] - tie[0] * esc[0], tie[4] + tie[1] * esc[1]   # top-left corner of pixel (0, 0)
        self.nodata = None
        if 42113 in t:
            try:
                self.nodata = float(bytes(t[42113]).decode().strip("\x00 "))
            except Exception:
                pass
        self.tpl = (self.w + self.tw - 1) // self.tw
        self.cache = {}

    def _ifd(self, off):
        e, f = self.e, self.f
        f.seek(off)
        n = struct.unpack(e + "H", f.read(2))[0]
        tags = {}
        tam = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 11: 4, 12: 8, 16: 8}
        cod = {1: "B", 2: "B", 3: "H", 4: "I", 5: "II", 7: "B", 11: "f", 12: "d", 16: "Q"}
        ents = [struct.unpack(e + "HHI4s", f.read(12)) for _ in range(n)]
        for tag, tipo, cnt, val in ents:
            nb = tam.get(tipo, 1) * cnt
            if nb <= 4:
                raw = val[:nb]
            else:
                f.seek(struct.unpack(e + "I", val)[0])
                raw = f.read(nb)
            c = cod.get(tipo, "B")
            k = cnt * (2 if tipo == 5 else 1)
            v = list(struct.unpack(e + c[0] * k if tipo != 5 else e + "I" * k, raw[:k * struct.calcsize(c[0])]))
            tags[tag] = v
        return tags

    def _bloco(self, k):
        if k in self.cache:
            return self.cache[k]
        self.f.seek(self.offs[k])
        raw = self.f.read(self.lens[k])
        if self.comp in (8, 32946):
            raw = zlib.decompress(raw)
        elif self.comp == 5:
            raw = _lzw(raw)
        elif self.comp != 1:
            raise ValueError(f"compressão {self.comp} não suportada")
        nb = self.bits // 8
        tw = self.tw
        if self.pred == 3:              # floating point: bytes split by significance, then differenced
            b = bytearray(raw)
            linha = tw * nb
            for r in range(len(b) // linha):
                s = r * linha
                for i in range(s + 1, s + linha):
                    b[i] = (b[i] + b[i - 1]) & 0xFF
            out = bytearray(len(b))
            for r in range(len(b) // linha):
                s = r * linha
                for j in range(nb):              # big-endian byte order inside each sample
                    pos = j if self.e == ">" else nb - 1 - j
                    out[s + pos:s + linha:nb] = b[s + j * tw:s + (j + 1) * tw]
            raw = bytes(out)
        cod = {(32, 3): "f", (16, 2): "h", (16, 1): "H", (32, 2): "i"}[(self.bits, self.fmt)]
        n = len(raw) // nb
        v = list(struct.unpack(self.e + cod * n, raw[:n * nb]))
        if self.pred == 2:
            for r in range(len(v) // tw):
                s = r * tw
                for i in range(s + 1, s + tw):
                    v[i] += v[i - 1]
        self.cache[k] = v
        return v

    def _px(self, c, r):
        c = min(max(c, 0), self.w - 1)
        r = min(max(r, 0), self.h - 1)
        k = (r // self.th) * self.tpl + (c // self.tw) if self.tw != self.w else r // self.th
        v = self._bloco(k)[(r % self.th) * self.tw + (c % self.tw)]
        return 0.0 if (self.nodata is not None and v == self.nodata) or v < -1000 else v

    def dentro(self, lat, lon):
        return self.x0 <= lon <= self.x0 + self.w * self.dx and self.y0 - self.h * self.dy <= lat <= self.y0

    def z(self, lat, lon):
        """Bilinear height at (lat, lon); pixel-is-area centres."""
        c = (lon - self.x0) / self.dx - 0.5
        r = (self.y0 - lat) / self.dy - 0.5
        c0, r0 = math.floor(c), math.floor(r)
        tc, tr = c - c0, r - r0
        a, b = self._px(c0, r0), self._px(c0 + 1, r0)
        d, e = self._px(c0, r0 + 1), self._px(c0 + 1, r0 + 1)
        return (a * (1 - tc) + b * tc) * (1 - tr) + (d * (1 - tc) + e * tc) * tr


def _lzw(dados):
    out, tab = bytearray(), [bytes([i]) for i in range(256)] + [b"", b""]
    bits, pos, ant = 9, 0, None
    nbits = len(dados) * 8
    while pos + bits <= nbits:
        b0 = pos >> 3
        chunk = int.from_bytes(dados[b0:b0 + 4].ljust(4, b"\0"), "big")
        codigo = (chunk >> (32 - (pos & 7) - bits)) & ((1 << bits) - 1)
        pos += bits
        if codigo == 256:
            tab = tab[:258]
            bits, ant = 9, None
            continue
        if codigo == 257:
            break
        if ant is None:
            s = tab[codigo]
        elif codigo < len(tab):
            s = tab[codigo]
            tab.append(ant + s[:1])
        else:
            s = ant + ant[:1]
            tab.append(s)
        out += s
        ant = s
        if len(tab) + 1 >= (1 << bits) and bits < 12:
            bits += 1
    return bytes(out)


# ---------------------------------------------------------------------------------------------- the house frame
class Envolvente:
    """OSM + DEM seen from the house frame. origem = PT-TM06 point of the frame's (0, 0); rot = degrees the site was
    rotated to make the plan's walls axis-aligned (local = R(rot) · (site - origem)); z0 = reference floor altitude."""

    USO = {   # land use / natural -> ground class
        "farmland": "campo", "meadow": "prado", "grass": "prado", "orchard": "pomar", "vineyard": "vinha",
        "forest": "mata", "wood": "mata", "scrub": "mato", "heath": "mato", "grassland": "prado",
        "residential": "quintal", "farmyard": "quintal", "industrial": "urbano", "commercial": "urbano",
        "retail": "urbano", "construction": "terra", "quarry": "rocha", "beach": "areia", "sand": "areia",
        "bare_rock": "rocha", "cliff": "rocha", "water": "agua", "reservoir": "agua", "basin": "agua",
        "wetland": "prado", "cemetery": "urbano", "allotments": "pomar", "greenhouse_horticulture": "estufa",
        "brownfield": "terra", "village_green": "prado", "recreation_ground": "prado", "plant_nursery": "pomar",
    }

    def __init__(self, osm_json, dem_tif, origem, rot, z0):
        self.O, self.z0 = origem, z0
        self.c, self.s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        self.osm = json.load(open(osm_json, encoding="utf-8"))["elements"] if osm_json else []
        self.dem = Dem(dem_tif) if dem_tif else None
        self.dz = 0.0                     # DEM datum/offset correction (set by alinhar)
        self._usos = None

    # frames
    def local(self, E, N):
        rx, ry = E - self.O[0], N - self.O[1]
        return rx * self.c - ry * self.s, rx * self.s + ry * self.c

    def site(self, x, y):
        return self.O[0] + x * self.c + y * self.s, self.O[1] - x * self.s + y * self.c

    def local_ll(self, lat, lon):
        return self.local(*latlon_para_ptm06(lat, lon))

    def ll(self, x, y):
        return ptm06_para_latlon(*self.site(x, y))

    # terrain
    def z_dem(self, x, y):
        """DEM height in the house frame (z = 0 at the reference floor), sea at 0 m."""
        lat, lon = self.ll(x, y)
        if not self.dem.dentro(lat, lon):
            return -self.z0
        z = self.dem.z(lat, lon)
        if z <= 0.05:                     # the sea (GLO-30 sets it to 0): sea level, not shifted
            return -self.z0
        return z + self.dz * min(1.0, z / 5.0) - self.z0

    def alinhar(self, pontos):
        """Shift the DEM so that it matches the survey (median over survey points (x, y, z) in the house frame).
        GLO-30 is a surface model 30 m wide and on another vertical datum: only a small shift is expected."""
        d = sorted(p[2] - (self.z_dem(p[0], p[1]) - self.dz) for p in pontos)
        self.dz = d[len(d) // 2] if d else 0.0
        return self.dz

    # OSM geometry
    def _anel(self, geom):
        return [self.local_ll(p["lat"], p["lon"]) for p in geom]

    def _poligonos(self, el):
        if el["type"] == "way" and "geometry" in el:
            g = self._anel(el["geometry"])
            return [g] if len(g) >= 4 and g[0] == g[-1] or len(g) >= 3 else []
        if el["type"] == "relation":
            return [self._anel(m["geometry"]) for m in el.get("members", [])
                    if m.get("role") == "outer" and "geometry" in m and len(m["geometry"]) >= 3]
        return []

    def usos(self):
        """[(class, polygon)] land use areas, largest first (smaller ones drawn on top)."""
        if self._usos is None:
            out = []
            for el in self.osm:
                t = el.get("tags", {})
                k = self.USO.get(t.get("landuse")) or self.USO.get(t.get("natural")) or self.USO.get(t.get("leisure"))
                if t.get("natural") == "water" or t.get("water"):
                    k = "agua"
                if not k or "building" in t:
                    continue
                for p in self._poligonos(el):
                    out.append((k, p, _bbox(p), abs(_area(p))))
            out.sort(key=lambda u: -u[3])
            self._usos = out
        return self._usos

    def uso(self, x, y, com_id=False):
        """Ground class at (x, y) (None outside every polygon); com_id: (class, polygon index) for a tone per parcel."""
        k = None
        for n, (cl, p, bb, _) in enumerate(self.usos()):
            if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and _dentro(p, x, y):
                k = (cl, n) if com_id else cl            # the last (smallest) containing polygon wins
        return k

    def casas(self, raio, excluir=None):
        """Buildings within raio: footprint (house frame), height to the eaves, roof type, wall/roof tones."""
        out = []
        for el in self.osm:
            t = el.get("tags", {})
            if "building" not in t or t.get("building") in ("roof", "no", "construction"):
                continue
            for p in self._poligonos(el):
                if p[0] == p[-1]:
                    p = p[:-1]
                if len(p) < 3:
                    continue
                cx, cy = sum(q[0] for q in p) / len(p), sum(q[1] for q in p) / len(p)
                if math.hypot(cx, cy) > raio or (excluir and excluir(cx, cy)):
                    continue
                area = abs(_area(p))
                if area < 6:
                    continue
                h = None
                try:
                    h = float(str(t.get("height", "")).replace("m", "").strip())
                except ValueError:
                    pass
                if h is None and t.get("building:levels"):
                    try:
                        h = 3.0 * float(t["building:levels"]) + 0.4
                    except ValueError:
                        pass
                tipo = t.get("building")
                if h is None:     # by use and size: sheds and garages 1 storey, houses 2 storeys, big blocks 2-3
                    if tipo in ("garage", "garages", "shed", "hut", "barn", "farm_auxiliary", "cabin", "service"):
                        h = 3.0
                    elif tipo in ("industrial", "warehouse", "greenhouse", "retail", "commercial"):
                        h = 6.5
                    elif area < 55:
                        h = 3.2
                    elif area > 400:
                        h = 7.5
                    else:
                        h = 6.2
                hs = _hash(el["id"])
                plano = tipo in ("industrial", "warehouse", "retail", "commercial", "apartments") or area > 600
                out.append({"osm": el["id"], "pontos": [[round(a, 2), round(b, 2)] for a, b in p], "altura": round(h, 2),
                            "telhado": "plano" if plano or tipo == "greenhouse" else "aguas",
                            "estufa": tipo == "greenhouse", "tom": round(hs, 3)})
        return out

    LARG = {"motorway": 11, "trunk": 9, "primary": 8, "secondary": 7, "tertiary": 6, "unclassified": 5,
            "residential": 5, "living_street": 4.5, "service": 3.5, "track": 3.0, "path": 1.2, "footway": 1.5,
            "cycleway": 2.0, "pedestrian": 4.0, "motorway_link": 6, "primary_link": 6, "secondary_link": 6,
            "tertiary_link": 5, "trunk_link": 6, "road": 5, "steps": 1.5, "bridleway": 2.0}

    def estradas(self, raio, excluir=None):
        out = []
        for el in self.osm:
            t = el.get("tags", {})
            hw = t.get("highway")
            if el["type"] != "way" or hw not in self.LARG or "geometry" not in el:
                continue
            g = self._anel(el["geometry"])
            if all(math.hypot(x, y) > raio for x, y in g):
                continue
            sup = t.get("surface", "")
            terra = hw in ("track", "path", "footway", "bridleway") or sup in ("unpaved", "dirt", "ground", "gravel",
                                                                               "compacted", "fine_gravel", "sand")
            if excluir:
                g = [q for q in g if not excluir(*q)]
                if len(g) < 2:
                    continue
            out.append({"pontos": [[round(a, 2), round(b, 2)] for a, b in g],
                        "largura": float(t.get("width", "0").split()[0] or 0) or self.LARG[hw],
                        "mat": "terra_batida" if terra else "asfalto"})
        return out

    def arvores_isoladas(self, raio):
        out = []
        for el in self.osm:
            if el["type"] == "node" and el.get("tags", {}).get("natural") == "tree":
                x, y = self.local_ll(el["lat"], el["lon"])
                if math.hypot(x, y) <= raio:
                    out.append((x, y))
        return out

    # vegetation: (x, y, kind, height) points, from the land use. Coastal Portugal by default: pine and eucalyptus
    # woods, scrub with bushes and a few pines, orchards in rows, garden trees around the houses, trees and hedges
    # along some field edges. `livre(x, y)` says whether a point is free (not a road, a building or the house's lot).
    MISTURA = {"mata": (("eucalipto", 0.5, 13, 22), ("pinheiro", 0.4, 9, 16), ("folhosa", 0.1, 7, 11)),
               "mato": (("arbusto", 0.9, 0.9, 2.4), ("pinheiro", 0.1, 4, 8)),
               "pomar": (("fruteira", 1.0, 2.8, 4.5),),
               "quintal": (("folhosa", 0.5, 4, 8), ("fruteira", 0.3, 3, 5), ("pinheiro", 0.2, 7, 12))}
    PASSO = {"mata": 5.5, "mato": 4.5, "pomar": 5.0, "quintal": 22.0}

    def vegetacao(self, raio, livre, semente=11, raio_arbustos=900):
        import random
        rnd = random.Random(semente)
        out = []

        def escolher(cl):
            r, acc = rnd.random(), 0.0
            for tipo, p, h0, h1 in self.MISTURA[cl]:
                acc += p
                if r <= acc:
                    return tipo, rnd.uniform(h0, h1)
            tipo, _, h0, h1 = self.MISTURA[cl][-1]
            return tipo, rnd.uniform(h0, h1)

        for cl, p, bb, area in self.usos():
            if cl not in self.MISTURA:
                continue
            lim_cl = raio_arbustos if cl == "mato" else raio
            if bb[2] < -lim_cl or bb[0] > lim_cl or bb[3] < -lim_cl or bb[1] > lim_cl:
                continue
            s = self.PASSO[cl]
            ang = rnd.random() * math.pi if cl == "pomar" else 0.0
            ca, sa = math.cos(ang), math.sin(ang)
            if cl == "pomar":         # rotated rows: walk the rotated bounding box
                cs_ = [(qx * ca + qy * sa, -qx * sa + qy * ca) for qx, qy in p]
                b0 = (min(q[0] for q in cs_), min(q[1] for q in cs_), max(q[0] for q in cs_), max(q[1] for q in cs_))
            else:
                b0 = (max(bb[0], -lim_cl), max(bb[1], -lim_cl), min(bb[2], lim_cl), min(bb[3], lim_cl))
            x = b0[0]
            while x <= b0[2]:
                y = b0[1]
                while y <= b0[3]:
                    if cl == "pomar":      # rows at the orchard's own angle
                        px, py = x * ca - y * sa, x * sa + y * ca
                        jx, jy = rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3)
                    else:
                        px, py = x, y
                        jx, jy = rnd.uniform(-0.45, 0.45) * s, rnd.uniform(-0.45, 0.45) * s
                    qx, qy = px + jx, py + jy
                    d = math.hypot(qx, qy)
                    lim = raio_arbustos if cl == "mato" else raio
                    if d <= lim and _dentro(p, qx, qy) and livre(qx, qy):
                        tipo, h = escolher(cl)
                        if not (tipo == "arbusto" and d > raio_arbustos):
                            out.append((qx, qy, tipo, h))
                    y += s
                x += s
        # field edges: a tree now and then, short hedges
        for cl, p, bb, area in self.usos():
            if cl not in ("campo", "prado"):
                continue
            for i in range(len(p) - 1):
                (x1, y1), (x2, y2) = p[i], p[i + 1]
                L = math.hypot(x2 - x1, y2 - y1)
                k = 0.0
                while k < L:
                    t = k / L if L else 0
                    qx, qy = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                    r = rnd.random()
                    if math.hypot(qx, qy) <= raio and livre(qx, qy):
                        if r < 0.10:
                            out.append((qx, qy, "folhosa", rnd.uniform(6, 10)))
                        elif r < 0.22 and math.hypot(qx, qy) <= raio_arbustos:
                            out.append((qx, qy, "arbusto", rnd.uniform(1.2, 2.2)))
                    k += 9.0
        for x, y in self.arvores_isoladas(raio):
            if livre(x, y):
                out.append((x, y, "folhosa", rnd.uniform(7, 10)))
        return out


def _area(p):
    return sum(p[i - 1][0] * p[i][1] - p[i][0] * p[i - 1][1] for i in range(len(p))) / 2


def _bbox(p):
    return (min(q[0] for q in p), min(q[1] for q in p), max(q[0] for q in p), max(q[1] for q in p))


def _dentro(p, x, y):
    r = False
    for i in range(len(p)):
        (x1, y1), (x2, y2) = p[i - 1], p[i]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            r = not r
    return r


def _hash(n):
    n = (int(n) * 2654435761) & 0xFFFFFFFF
    return ((n ^ (n >> 15)) & 0xFFFF) / 65535.0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "ptm06":
        print("%.6f %.6f" % ptm06_para_latlon(float(a[1]), float(a[2])))
    elif a and a[0] == "latlon":
        print("%.2f %.2f" % latlon_para_ptm06(float(a[1]), float(a[2])))
    elif a and a[0] == "osm":
        print("OSM bytes:", descarregar_osm(float(a[1]), float(a[2]), float(a[3]), a[4]))
    elif a and a[0] == "dem-info":
        d = Dem(a[1])
        print({k: (v if len(v) < 8 else f"{len(v)} valores") for k, v in d.tags.items()})
    else:
        print(__doc__)
