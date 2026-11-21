"""Blender: the inside of the client's house (casa.json "interior"), for casa_blender.py.

    "interior": {
      "escadas":  [{de [x,y,z], ate [x,y,z], largura, degraus, tipo madeira|betao, corrimao true, grupo}]
                  straight flight from the first tread's front edge (de) to the top floor's edge (ate)
      "portas":   [{caixa [x0,y0,z0,x1,y1,z1] (the doorway), eixo x|y (the wall's axis), abre +1|-1, grupo}]
      "pecas":    [{tipo, x, y, z, rot (deg; 0 = the piece's front faces +y), grupo, ...per type}]
      "rodapes":  [{caixa (a room's inner box), grupo}]       skirting along the room's walls
    }
Piece types (the front of a piece looks at +y before rotation): sofa, maple, mesa_centro, mesa_jantar, cadeira,
tapete, pendente, candeeiro_pe, candeeiro_mesa, foco (ceiling downlight), cozinha, lareira, cama, mesinha, roupeiro,
secretaria, cadeira_escritorio, estante, sanita, lavatorio, duche, espelho, planta, quadro, jarra, livros,
espreguicadeira, mesa_exterior, cadeira_exterior, aparador.
Every piece is built from bevelled boxes, cylinders and spheres (real geometry: the web model gets it too); lights are
real Cycles lights (warm white), switched on in the renders. Sizes default to common furniture sizes.
With the CC0 assets (ativos.py) the woods and fabrics get photo textures, and plants, vases, the armchair, the round
coffee table, the sideboard and the pendant lamps are real models (Poly Haven); without them, the procedural ones.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

M = {}            # materials of the interior
ctx = {}          # from casa_blender: MATS, ligar, RNG, mat_simples, mat_vidro
LUZES = []        # (object) all interior lights: on in the renders


def _cor(h):
    h = h.lstrip("#")
    return tuple((int(h[i:i + 2], 16) / 255.0) ** 2.2 for i in (0, 2, 4))


def _mat(nome, cor, rug=0.6, metal=0.0, brilho=0.0, sheen=0.0, coat=0.0, emissao=None, forca=0.0, trans=0.0):
    if nome in M:
        return M[nome]
    m = bpy.data.materials.new("int_" + nome)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    c = _cor(cor)
    b.inputs["Base Color"].default_value = (*c, 1)
    b.inputs["Roughness"].default_value = rug
    b.inputs["Metallic"].default_value = metal
    for k, v in (("Sheen Weight", sheen), ("Coat Weight", coat), ("Specular IOR Level", 0.5 + brilho)):
        if k in b.inputs and v:
            b.inputs[k].default_value = v
    if emissao:
        for k in ("Emission Color", "Emission"):
            if k in b.inputs:
                b.inputs[k].default_value = (*_cor(emissao), 1)
                break
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = forca
    if trans:
        for k in ("Transmission Weight", "Transmission"):
            if k in b.inputs:
                b.inputs[k].default_value = trans
                break
        b.inputs["IOR"].default_value = 1.45
    m.diffuse_color = (*c, 1)
    M[nome] = m
    return m


def materiais():
    MATS = ctx["MATS"]
    M["carvalho"] = MATS["soalho"]                  # oak: the floor's own boards (light oak)
    _mat("nogueira", "#5e4330", 0.45, coat=0.2)
    _mat("lacado", "#f1efea", 0.35, coat=0.15)      # white lacquer (doors, wardrobes, kitchen fronts)
    _mat("frente", "#d9d2c5", 0.4)                  # kitchen fronts: warm greige
    _mat("bancada", "#e9e6e1", 0.18, coat=0.3)      # quartz worktop
    _mat("microcimento", "#9d978d", 0.75)
    _mat("tecido", "#b9b1a4", 0.95, sheen=0.6)      # linen sofa
    _mat("tecido_sofa", "#8d887f", 0.95, sheen=0.5)  # the tailored sofa: grey-beige linen
    _mat("tecido_escuro", "#58534d", 0.95, sheen=0.6)
    _mat("almofada", "#d9cbb3", 0.95, sheen=0.7)
    _mat("almofada2", "#8a6f57", 0.95, sheen=0.7)
    _mat("roupa", "#f3f1ec", 0.92, sheen=0.5)        # bed linen
    _mat("manta", "#a98f72", 0.95, sheen=0.8)
    _mat("la", "#cfc4b3", 1.0, sheen=0.4)           # wool rug
    _mat("la_escura", "#6c6359", 1.0, sheen=0.4)
    _mat("metal_preto", "#1c1c1c", 0.35, 0.9)
    _mat("latao", "#b08d57", 0.28, 1.0)
    _mat("inox", "#c8c8c8", 0.22, 1.0)
    _mat("loica", "#f6f6f4", 0.08, coat=0.6)
    _mat("vidro_preto", "#0b0b0b", 0.03, coat=1.0)
    _mat("espelho", "#ffffff", 0.0, 1.0)
    _mat("vidro_int", "#f2f6f6", 0.0, trans=1.0)
    _mat("vaso", "#c7b8a3", 0.8)
    _mat("vaso_escuro", "#3d3a36", 0.6)
    _mat("folha", "#3f5a2a", 0.55, sheen=0.3)
    _mat("terra", "#2b2118", 1.0)
    _mat("papel", "#efe9dd", 0.9)                   # lamp shades
    _mat("lampada", "#ffffff", 0.5, emissao="#ffd9a8", forca=12.0)
    _mat("led", "#ffffff", 0.5, emissao="#ffdcb0", forca=6.0)
    _mat("chama", "#000000", 1.0, emissao="#ff8a2a", forca=18.0)
    _mat("brasa", "#2a1408", 1.0, emissao="#ff5a10", forca=2.0)
    _mat("tela1", "#c9b79c", 0.9)
    _mat("tela2", "#8c9a8a", 0.9)
    _mat("tela3", "#b2765a", 0.9)
    _mat("exterior_tecido", "#d8d2c4", 0.95, sheen=0.4)
    for i, c in enumerate(("#7d5a44", "#3f5268", "#a7a08f", "#6b3a33", "#d9cfbd", "#2f3a33", "#c29b5d")):
        _mat(f"livro{i}", c, 0.7)
    A = ctx.get("ativos")
    if not A:
        return
    # CC0 photo textures in our colours: (asset, colour, normal strength, size factor, extra)
    for nome, (aid, cor, forca, esc, extra) in {
            "carvalho": ("oak_veneer_01", "#c09a6e", 0.4, 1.0, {"coat": 0.1}),
            "nogueira": ("wood_table_001", "#5e4330", 0.4, 1.0, {"coat": 0.2}),
            "bancada": ("marble_01", "#e9e6e1", 0.3, 1.0, {"rug": 0.15, "coat": 0.3}),
            "microcimento": ("concrete_floor_02", "#9d978d", 0.4, 0.5, {}),
            "tecido": ("rough_linen", "#b9b1a4", 0.8, 1.0, {"sheen": 0.6}),
            "tecido_sofa": ("rough_linen", "#8d887f", 0.9, 0.7, {"sheen": 0.5}),
            "tecido_escuro": ("rough_linen", "#58534d", 0.8, 1.0, {"sheen": 0.6}),
            "almofada": ("velour_velvet", "#d9cbb3", 0.6, 1.0, {"sheen": 0.8}),
            "almofada2": ("velour_velvet", "#8a6f57", 0.6, 1.0, {"sheen": 0.8}),
            "roupa": ("rough_linen", "#f3f1ec", 0.6, 1.0, {"sheen": 0.5}),
            "manta": ("velour_velvet", "#a98f72", 0.8, 1.0, {"sheen": 0.8}),
            "la": ("rough_linen", "#cfc4b3", 1.0, 2.5, {"sheen": 0.4}),
            "la_escura": ("rough_linen", "#6c6359", 1.0, 2.5, {"sheen": 0.4}),
            "exterior_tecido": ("rough_linen", "#d8d2c4", 0.8, 1.0, {"sheen": 0.4}),
    }.items():
        if A.tem(aid):
            m = A.material("int_" + nome, aid, cor=cor, forca=forca, **extra)
            if m:
                M[nome] = m
                ctx["TILE"]["int_" + nome] = A.tamanho_m(aid) * esc


# ------------------------------------------------------------------------------------------------ the piece builder
class Peca:
    """A piece in its own frame (x right, y front, z up; origin on the floor at its centre), placed by x, y, z, rot."""

    def __init__(self, nome, d):
        self.nome = nome
        self.grupo = d.get("grupo", "interior")
        self.T = Matrix.Translation((d.get("x", 0.0), d.get("y", 0.0), d.get("z", 0.0))) @ \
            Matrix.Rotation(math.radians(d.get("rot", 0.0)), 4, "Z")
        self.bms = {}

    def _bm(self, mat):
        if mat not in self.bms:
            self.bms[mat] = bmesh.new()
        return self.bms[mat]

    def caixa(self, mat, x0, y0, z0, x1, y1, z1, b=0.0, seg=2):
        bm = self._bm(mat)
        tmp = bmesh.new()
        bmesh.ops.create_cube(tmp, size=1.0)
        for v in tmp.verts:
            v.co = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0), (y0 + y1) / 2 + v.co.y * (y1 - y0),
                           (z0 + z1) / 2 + v.co.z * (z1 - z0)))
        b = min(b, (x1 - x0) / 2.05, (y1 - y0) / 2.05, (z1 - z0) / 2.05)
        if b > 0.0005:
            bmesh.ops.bevel(tmp, geom=list(tmp.edges), offset=b, segments=seg, profile=0.5, affect="EDGES",
                            clamp_overlap=True)
        self._juntar(bm, tmp)

    def cil(self, mat, cx, cy, z0, z1, r, r2=None, seg=24, eixo="z", tampa=True):
        bm = self._bm(mat)
        tmp = bmesh.new()
        bmesh.ops.create_cone(tmp, cap_ends=tampa, segments=seg, radius1=r, radius2=r if r2 is None else r2,
                              depth=abs(z1 - z0))
        if eixo == "x":
            bmesh.ops.rotate(tmp, verts=tmp.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
        elif eixo == "y":
            bmesh.ops.rotate(tmp, verts=tmp.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
        # (cx, cy, (z0+z1)/2) is the centre; along x or y the length is |z1 - z0|
        bmesh.ops.translate(tmp, verts=tmp.verts, vec=(cx, cy, (z0 + z1) / 2))
        for f in tmp.faces:
            f.smooth = True
        self._juntar(bm, tmp)

    def tubo(self, mat, a, b, r, seg=12):
        """A cylinder between two points (handrails, legs at an angle, cords)."""
        a, b = Vector(a), Vector(b)
        d = b - a
        bm = self._bm(mat)
        tmp = bmesh.new()
        bmesh.ops.create_cone(tmp, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
        rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix()
        bmesh.ops.rotate(tmp, verts=tmp.verts, cent=(0, 0, 0), matrix=rot)
        bmesh.ops.translate(tmp, verts=tmp.verts, vec=(a + b) / 2)
        for f in tmp.faces:
            f.smooth = True
        self._juntar(bm, tmp)

    def esfera(self, mat, cx, cy, cz, r, esc=(1, 1, 1), sub=2):
        bm = self._bm(mat)
        tmp = bmesh.new()
        bmesh.ops.create_icosphere(tmp, subdivisions=sub, radius=r)
        for v in tmp.verts:
            v.co = Vector((cx + v.co.x * esc[0], cy + v.co.y * esc[1], cz + v.co.z * esc[2]))
        for f in tmp.faces:
            f.smooth = True
        self._juntar(bm, tmp)

    def malha(self, mat, verts, faces, suave=True):
        bm = self._bm(mat)
        tmp = bmesh.new()
        vs = [tmp.verts.new(v) for v in verts]
        for f in faces:
            try:
                tmp.faces.new([vs[i] for i in f]).smooth = suave
            except ValueError:
                pass
        self._juntar(bm, tmp)

    @staticmethod
    def _juntar(bm, tmp):
        me = bpy.data.meshes.new("tmp")
        tmp.to_mesh(me)
        tmp.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)

    def luz(self, tipo, x, y, z, potencia, raio=0.05, cor=(1.0, 0.78, 0.55), direcao=None, angulo=None):
        lz = bpy.data.lights.new(f"{self.nome}_luz", tipo)
        lz.energy = potencia
        lz.color = cor
        if tipo in ("POINT", "SPOT"):
            lz.shadow_soft_size = raio
        if tipo == "SPOT":
            lz.spot_size = math.radians(angulo or 70)
            lz.spot_blend = 0.6
        if tipo == "AREA":
            lz.shape = "RECTANGLE"
            lz.size, lz.size_y = raio
        ob = bpy.data.objects.new(f"{self.nome}_luz", lz)
        bpy.context.scene.collection.objects.link(ob)
        ob.parent = ctx["RAIZ"]
        ob.matrix_parent_inverse = Matrix.Identity(4)
        p = self.T @ Vector((x, y, z))
        ob.location = p
        if direcao:
            dv = (self.T.to_3x3() @ Vector(direcao)).normalized()
            ob.rotation_euler = dv.to_track_quat("-Z", "Y").to_euler()
        ob["interior_luz"] = True
        LUZES.append(ob)
        return ob

    # -------------------------------------------------------------------------------- soft shapes (upholstery, bedding)
    def _soltar(self, mat, verts, faces, M=None):
        """Faces from verts (piece frame, after M), duplicates merged, smooth shading."""
        tmp = bmesh.new()
        vs = [tmp.verts.new(M @ Vector(v) if M else v) for v in verts]
        for f in faces:
            q = [vs[i] for i in f]
            if len(set(q)) == len(q):
                try:
                    tmp.faces.new(q)
                except ValueError:
                    pass
        bmesh.ops.remove_doubles(tmp, verts=tmp.verts, dist=1e-5)
        for f in tmp.faces:
            f.smooth = True
        self._juntar(self._bm(mat), tmp)

    def macio(self, mat, cx, cy, cz, a, b, c, e1=0.45, e2=0.25, puff=0.0, eixo="z", inclinar=0.0, seg=(56, 28)):
        """A soft upholstered volume: a superellipsoid of half sizes a (x), b (y), c (z); e1 rounds the profile, e2 the
        plan (0 = box, 1 = ellipsoid). puff bulges the face toward +eixo (a cushion's filling); inclinar tilts it
        about x (deg, + leans the top toward -y)."""
        def sg(w, m, f):
            v = f(w)
            return math.copysign(abs(v) ** m, v)
        nu, nv = seg
        verts, faces = [], []
        for j in range(nv + 1):
            u = -math.pi / 2 + math.pi * j / nv
            cu, su = sg(u, e1, math.cos), sg(u, e1, math.sin)
            for i in range(nu):
                v = -math.pi + 2 * math.pi * i / nu
                x, y, z = a * cu * sg(v, e2, math.cos), b * cu * sg(v, e2, math.sin), c * su
                if puff and eixo == "z" and z > 0:
                    z += puff * max(0.0, 1 - (x / a) ** 2) * max(0.0, 1 - (y / b) ** 2) * (z / c)
                elif puff and eixo == "y" and y > 0:
                    y += puff * max(0.0, 1 - (x / a) ** 2) * max(0.0, 1 - (z / c) ** 2) * (y / b)
                verts.append((x, y, z))
        for j in range(nv):
            for i in range(nu):
                i2 = (i + 1) % nu
                faces.append((j * nu + i, j * nu + i2, (j + 1) * nu + i2, (j + 1) * nu + i))
        M = Matrix.Translation((cx, cy, cz)) @ Matrix.Rotation(math.radians(-inclinar), 4, "X")
        self._soltar(mat, verts, faces, M)

    def travesseiro(self, mat, cx, cy, cz, a, c, b, inclinar=0.0, n=26):
        """A pillow standing up: 2a wide (x), 2c high (z), 2b thick in the middle (y), thin at the seam all round,
        its sides drawn in a little; inclinar leans it back (deg, the top toward -y)."""
        verts, faces = [], []
        for lado in (1, -1):
            base = len(verts)
            for j in range(n + 1):
                t = -1 + 2 * j / n
                for i in range(n + 1):
                    s_ = -1 + 2 * i / n
                    th = b * max(0.0, (1 - abs(s_) ** 4) * (1 - abs(t) ** 4)) ** 0.55
                    x = a * s_ * (1 - 0.07 * (1 - t * t))
                    z = c * t * (1 - 0.07 * (1 - s_ * s_))
                    verts.append((x, lado * th, z))
            for j in range(n):
                for i in range(n):
                    q = (base + j * (n + 1) + i, base + j * (n + 1) + i + 1, base + (j + 1) * (n + 1) + i + 1,
                         base + (j + 1) * (n + 1) + i)
                    faces.append(q if lado < 0 else q[::-1])
        M = Matrix.Translation((cx, cy, cz)) @ Matrix.Rotation(math.radians(-inclinar), 4, "X")
        self._soltar(mat, verts, faces, M)

    def lencol(self, mat, x0, y0, x1, y1, z, cair, r=0.06, esq=True, dir=True, frente=True, rugas=0.012,
               passo=0.025, semente=0):
        """A cover (duvet, throw) lying flat on x0..x1 / y0..y1 at height z, rolling over a rounded edge (radius r)
        and hanging cair metres on the left, right and front (+y) sides, with soft folds where it hangs."""
        rng = ctx["RNG"]
        Ld = r * math.pi / 2 + max(0.0, cair - r)
        ua, ub = x0 - (Ld if esq else 0.0), x1 + (Ld if dir else 0.0)
        vb = y1 + (Ld if frente else 0.0)
        nu, nv = max(4, int((ub - ua) / passo)), max(4, int((vb - y0) / passo))
        fase = [rng.uniform(0, 6.3) for _ in range(6)]
        lam = [rng.uniform(0.32, 0.46), rng.uniform(0.55, 0.8), rng.uniform(0.21, 0.27)]   # broad, uneven folds

        def dobrar(d, e, sgn):            # distance d past the edge e (outward sign) -> position across, height drop
            if d <= 0:
                return None
            if d < r * math.pi / 2:
                th = d / r
                return e + sgn * r * math.sin(th), r * (1 - math.cos(th)), d
            return e + sgn * r, r + (d - r * math.pi / 2), d

        verts, faces = [], []
        for j in range(nv + 1):
            v = y0 + (vb - y0) * j / nv
            for i in range(nu + 1):
                u = ua + (ub - ua) * i / nu
                x, y, hz, dmax = u, v, 0.0, 0.0
                fx = dobrar(x0 - u, x0, -1) if u < x0 else dobrar(u - x1, x1, 1) if u > x1 else None
                fy = dobrar(v - y1, y1, 1) if v > y1 else None
                if fx:
                    x, hz, dmax = fx[0], fx[1], fx[2]
                if fy:
                    y = fy[0]
                    hz = max(hz, fy[1]) + (0.35 * min(hz, fy[1]) if fx else 0.0)
                    dmax = max(dmax, fy[2])
                hz = min(hz, cair * 1.1)
                # folds: grow with how far the cloth hangs; the top only undulates a little
                k = min(1.0, dmax / 0.18)
                ao_longo = v if (fx and not fy) else u          # folds run down the cloth, varying along the edge
                w = rugas * (0.15 + 0.85 * k) * (math.sin(2 * math.pi * ao_longo / lam[0] + fase[0])
                                                 + 0.7 * math.sin(2 * math.pi * ao_longo / lam[1] + fase[1])
                                                 + 0.3 * math.sin(2 * math.pi * ao_longo / lam[2] + fase[2]))
                if fx and not fy:
                    x += math.copysign(w * k, x - (x0 + x1) / 2)
                elif fy:
                    y += w * k
                zz = z - hz + (0.0 if dmax else 0.12 * w)
                verts.append((x, y, zz))
        for j in range(nv):
            for i in range(nu):
                a_ = j * (nu + 1) + i
                faces.append((a_, a_ + 1, a_ + nu + 2, a_ + nu + 1))
        self._soltar(mat, verts, faces)

    def modelo(self, aid, x=0.0, y=0.0, z=0.0, rot=0.0, alt=None, larg=None, esc=None, sem_sombra=False):
        """A CC0 model (ativos.py) at (x, y, z) of the piece, its front to +y turned by rot; scaled to alt (height) or
        esc (uniform), larg stretches the width only. None when the asset is not there (the caller builds its own)."""
        A = ctx.get("ativos")
        P = A.prototipo(aid) if A and A.tem(aid) else None
        if P is None:
            return None
        s = esc or (alt / P["dim"].z if alt else 1.0)
        sx = larg / P["dim"].x if larg else s
        S = Matrix.Diagonal((sx, s, s, 1.0))
        R = Matrix.Rotation(math.radians(rot), 4, "Z")
        return A.colocar(aid, self.T @ Matrix.Translation((x, y, z)) @ R @ S, self.grupo, ctx["ligar"], self.nome,
                         sem_sombra=sem_sombra)

    def fim(self):
        obs = []
        for mat, bm in self.bms.items():
            bm.transform(self.T)
            me = bpy.data.meshes.new(f"{self.nome}_{mat}")
            bm.to_mesh(me)
            bm.free()
            me.materials.append(M[mat] if mat in M else ctx["MATS"][mat])
            ob = bpy.data.objects.new(f"{self.nome}_{mat}", me)
            ob["suave"] = True
            obs.append(ctx["ligar"](ob, self.grupo))
        return obs


# ------------------------------------------------------------------------------------------------ the pieces
def sofa(p, d):
    """A minimalist modern sofa (user 2026-11-20: the rounded one «parece demasiado fake»; «procura algo moderno ou
    modela tu consoante uma referência mais moderna e minimalista»): low and straight, after the slim-armed sofas of
    current Scandinavian design — a thin upholstered frame on slim black legs, straight arms the height of the back,
    firm cushions with crisp edges (one seat cushion per place, low back cushions), one flat scatter cushion.
    Fabric: mat (default the grey-beige linen "tecido_sofa"). A narrow one (larg ~1.1) is the single-seat «mini
    sofá» of the same style (user 2026-11-20, in place of the armchair)."""
    L, P = d.get("larg", 2.4), d.get("prof", 0.9)
    x0, x1, y0, y1 = -L / 2, L / 2, -P / 2, P / 2
    tec = d.get("mat", "tecido_sofa")
    pe = d.get("pes", "metal_preto")
    h0, hs, ha, ba, bt = 0.15, 0.30, 0.66, 0.11, 0.13   # legs, frame top under the seat, arms/back top, arm width, back
    for sx in (-1, 1):                                                                             # slim legs
        for sy in (-1, 1):
            p.caixa(pe, sx * (L / 2 - 0.06) - 0.012, sy * (P / 2 - 0.06) - 0.012, 0.0,
                    sx * (L / 2 - 0.06) + 0.012, sy * (P / 2 - 0.06) + 0.012, h0, 0.003)
    p.caixa(tec, x0, y0, h0, x1, y1, hs, 0.012, 2)                                                 # frame
    for sx in (-1, 1):                                                                             # arms
        p.caixa(tec, x1 - ba if sx > 0 else x0, y0, hs - 0.01, x1 if sx > 0 else x0 + ba, y1, ha, 0.015, 3)
    p.caixa(tec, x0 + ba - 0.005, y0, hs - 0.01, x1 - ba + 0.005, y0 + bt, ha, 0.015, 3)          # back
    n = max(1, round((L - 2 * ba) / 0.8))
    w = (L - 2 * ba) / n
    for i in range(n):
        cx = x0 + ba + (i + 0.5) * w
        dy = (P - bt) / 2
        p.caixa(tec, cx - w / 2 + 0.004, y0 + bt + 0.004, hs, cx + w / 2 - 0.004, y1 - 0.004, hs + 0.13,
                0.022, 4)                                                                          # seat cushions
        p.macio(tec, cx, y0 + bt + 0.07, hs + 0.13 + 0.19, w / 2 - 0.008, 0.07, 0.19,
                e1=0.12, e2=0.06, puff=0.006, eixo="y", inclinar=6)                                # back cushions
    p.travesseiro("almofada", x0 + ba + 0.26, y0 + bt + 0.2, hs + 0.13 + 0.2, 0.2, 0.2, 0.055, inclinar=12)


def maple(p, d):
    if p.modelo(d.get("modelo", "modern_arm_chair_01")):
        return
    tec = d.get("mat", "tecido_escuro")
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.tubo("nogueira", (sx * 0.3, sy * 0.3, 0), (sx * 0.33, sy * 0.33, 0.2), 0.018)
    p.caixa(tec, -0.38, -0.38, 0.2, 0.38, 0.4, 0.42, 0.04, 3)
    p.caixa(tec, -0.38, -0.4, 0.42, 0.38, -0.24, 0.85, 0.06, 3)
    p.caixa(tec, -0.4, -0.4, 0.3, -0.3, 0.38, 0.62, 0.04, 3)
    p.caixa(tec, 0.3, -0.4, 0.3, 0.4, 0.38, 0.62, 0.04, 3)
    p.caixa(tec, -0.32, -0.24, 0.42, 0.32, 0.36, 0.52, 0.05, 3)
    p.caixa("almofada", -0.2, -0.26, 0.5, 0.2, -0.14, 0.82, 0.06, 3)


def mesa_centro(p, d):
    L, P, h = d.get("larg", 1.1), d.get("prof", 0.6), d.get("alt", 0.38)
    s = min(1.0, max(L * 0.82, P * 1.5) / 1.3)               # the round table (1.30 m) as wide as the piece allows
    if p.modelo("coffee_table_round_01", esc=s):
        h = 0.49 * s
        livros(p, {"n": 3, "deitados": True}, (-0.18 * s, 0.0, h))
        jarra(p, {"alt": 0.22}, (0.22 * s, 0.08, h))
        return
    p.caixa("carvalho", -L / 2, -P / 2, h - 0.04, L / 2, P / 2, h, 0.008)
    p.caixa("carvalho", -L / 2 + 0.06, -P / 2 + 0.06, 0.0, L / 2 - 0.06, P / 2 - 0.06, 0.1, 0.008)
    for sx in (-1, 1):
        p.caixa("carvalho", sx * (L / 2 - 0.08) - 0.03, -P / 2 + 0.06, 0.1, sx * (L / 2 - 0.08) + 0.03, P / 2 - 0.06,
                h - 0.04, 0.005)
    livros(p, {"n": 3}, (-L / 4, 0.0, h))
    jarra(p, {}, (L / 4, 0.05, h))


def mesa_jantar(p, d):
    """Dining table and chairs. redonda: a round top of diameter larg on a pedestal (mat_base), the chairs around it.
    mat (top), cadeira {estrutura, assento}: the materials, to match the room (user 2026-11-20: «a mesa e cadeiras
    devem combinar com a envolvente»)."""
    L, P, h = d.get("larg", 1.8), d.get("prof", 0.9), 0.75
    cd = d.get("cadeira", {})
    if d.get("redonda"):
        r, tampo = L / 2, d.get("mat", "carvalho")
        p.cil(tampo, 0, 0, h - 0.035, h, r, seg=64)
        p.cil(d.get("mat_base", "metal_preto"), 0, 0, 0.03, h - 0.035, 0.045, seg=24)
        p.cil(d.get("mat_base", "metal_preto"), 0, 0, 0.0, 0.03, 0.26, seg=48)
        jarra(p, {"alt": 0.28}, (0.0, 0.0, h))
        n = d.get("cadeiras", 4)
        for k in range(n):
            a = math.radians(d.get("angulo0", 45) + 360 * k / n)
            cadeira(p, cd, ((r + 0.04) * math.cos(a), (r + 0.04) * math.sin(a), 0), math.degrees(a) + 90)
        return
    p.caixa("carvalho", -L / 2, -P / 2, h - 0.04, L / 2, P / 2, h, 0.006)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.caixa("carvalho", sx * (L / 2 - 0.12) - 0.035, sy * (P / 2 - 0.1) - 0.035, 0,
                    sx * (L / 2 - 0.12) + 0.035, sy * (P / 2 - 0.1) + 0.035, h - 0.04, 0.006)
    p.caixa("carvalho", -L / 2 + 0.12, -0.02, h - 0.12, L / 2 - 0.12, 0.02, h - 0.04)
    jarra(p, {"alt": 0.3}, (0.0, 0.0, h))
    n = d.get("cadeiras", 6)
    lado = (n - 2) // 2 if n > 4 else n // 2
    xs = [(-L / 2 + (i + 0.5) * L / lado) for i in range(lado)]
    for sy, r in ((-1, 0), (1, 180)):
        for x in xs:
            cadeira(p, cd, (x, sy * (P / 2 + 0.05), 0), r)
    if n > 4:
        cadeira(p, cd, (-L / 2 - 0.08, 0, 0), -90)
        cadeira(p, cd, (L / 2 + 0.08, 0, 0), 90)


def cadeira(p, d, o=(0, 0, 0), rot=0):
    """Dining chair; its back is on the far side from the table: front faces +y in its own frame, rotated by rot."""
    R = Matrix.Rotation(math.radians(rot), 3, "Z")

    def P_(x, y, z):
        v = R @ Vector((x, y, z))
        return (o[0] + v.x, o[1] + v.y, o[2] + v.z)

    def cx(mat, x0, y0, z0, x1, y1, z1, b=0.0):
        a, c = P_(x0, y0, z0), P_(x1, y1, z1)
        p.caixa(mat, min(a[0], c[0]), min(a[1], c[1]), z0 + o[2], max(a[0], c[0]), max(a[1], c[1]), z1 + o[2], b)
    est, ass = d.get("estrutura", "nogueira"), d.get("assento", "tecido_escuro")   # frame, seat (and back)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.tubo(est, P_(sx * 0.2, sy * 0.2 - 0.25, 0), P_(sx * 0.21, sy * 0.21 - 0.25, 0.45), 0.014)
    cx(est, -0.23, -0.48, 0.44, 0.23, -0.02, 0.47, 0.01)
    cx(ass, -0.22, -0.46, 0.47, 0.22, -0.04, 0.51, 0.015)
    p.tubo(est, P_(-0.2, -0.46, 0.47), P_(-0.21, -0.5, 0.82), 0.014)
    p.tubo(est, P_(0.2, -0.46, 0.47), P_(0.21, -0.5, 0.82), 0.014)
    cx(d.get("costas", est), -0.22, -0.52, 0.66, 0.22, -0.47, 0.82, 0.01)


def tapete(p, d):
    L, P = d.get("larg", 2.4), d.get("prof", 1.7)
    p.caixa(d.get("mat", "la"), -L / 2, -P / 2, 0.0, L / 2, P / 2, 0.014, 0.006)


def pendente(p, d):
    h = d.get("teto", 2.94) - d.get("z", 0.0)
    zb = d.get("altura", 1.65)
    A = ctx.get("ativos")
    if A and A.tem("modern_ceiling_lamp_01"):           # the glass globe lamp: lit from inside, its cord to the ceiling
        for dx in d.get("lampadas", [0.0]):
            obs = p.modelo("modern_ceiling_lamp_01", dx, 0, zb, sem_sombra=True)
            topo = zb + A.prototipo("modern_ceiling_lamp_01")["dim"].z
            if obs and topo < h - 0.01:
                p.tubo("metal_preto", (dx, 0, h), (dx, 0, topo), 0.003, 6)
            p.luz("POINT", dx, 0, zb + 0.2, d.get("potencia", 45), 0.08)
        p.cil("metal_preto", 0, 0, h - 0.015, h, 0.05)
        return
    for k, dx in enumerate(d.get("lampadas", [0.0])):
        p.tubo("metal_preto", (dx, 0, h), (dx, 0, zb + 0.22), 0.003, 6)
        p.cil(d.get("mat", "latao"), dx, 0, zb, zb + 0.22, d.get("raio", 0.2), 0.04, 32, tampa=False)
        p.esfera("lampada", dx, 0, zb + 0.06, 0.035)
        p.luz("POINT", dx, 0, zb + 0.07, d.get("potencia", 45), 0.04)
    p.cil("metal_preto", 0, 0, h - 0.015, h, 0.05)


def candeeiro_pe(p, d):
    p.cil("metal_preto", 0, 0, 0, 0.02, 0.15)
    p.tubo("metal_preto", (0, 0, 0.02), (0, 0, 1.35), 0.01)
    p.cil("papel", 0, 0, 1.25, 1.6, 0.2, 0.17, 32, tampa=False)
    p.luz("POINT", 0, 0, 1.42, d.get("potencia", 35), 0.06)


def candeeiro_mesa(p, d, o=(0, 0, 0)):
    x, y, z = o
    p.cil("vaso", x, y, z, z + 0.25, 0.07, 0.05, 24)
    p.cil("papel", x, y, z + 0.25, z + 0.45, 0.14, 0.12, 32, tampa=False)
    p.luz("POINT", x, y, z + 0.33, d.get("potencia", 15), 0.04)


def foco(p, d):
    h = d.get("teto", 2.94) - d.get("z", 0.0)
    p.cil("metal_preto", 0, 0, h - 0.005, h, 0.045)
    p.cil("led", 0, 0, h - 0.008, h - 0.004, 0.03)
    p.luz("SPOT", 0, 0, h - 0.02, d.get("potencia", 18), 0.03, direcao=(0, 0, -1), angulo=d.get("angulo", 80),
          cor=tuple(d.get("cor", (1.0, 0.78, 0.55))))


def cozinha(p, d):
    """Linear kitchen along the wall behind (y = -P): plinth, base units with fronts, worktop, hob, sink with a tap,
    tall units at the end(s), a hood and an open shelf with a LED strip."""
    L, P = d["larg"], 0.62
    x0 = -L / 2
    altas = d.get("altas", [])                     # [[a, b], ...] tall units (local x from the left end)
    p.caixa("metal_preto", x0, -P + 0.05, 0, x0 + L, -0.06, 0.1)
    corridas = []
    a = x0
    for ta, tb in sorted(altas):
        if ta + x0 > a:
            corridas.append((a, ta + x0))
        p.caixa(d.get("frente", "frente"), ta + x0 + 0.002, -P, 0.1, tb + x0 - 0.002, 0.0, 2.3, 0.004)
        n = max(1, round((tb - ta) / 0.6))
        for i in range(1, n):
            xx = ta + x0 + i * (tb - ta) / n
            p.caixa("metal_preto", xx - 0.002, -0.003, 0.1, xx + 0.002, 0.001, 2.3)
        p.caixa("metal_preto", ta + x0, -0.003, 1.2, tb + x0, 0.001, 1.204)
        a = tb + x0
    if a < x0 + L:
        corridas.append((a, x0 + L))
    for ca, cb in corridas:
        p.caixa(d.get("frente", "frente"), ca, -P, 0.1, cb, -0.03, 0.86)
        n = max(1, round((cb - ca) / 0.6))
        for i in range(n):
            fa, fb = ca + i * (cb - ca) / n, ca + (i + 1) * (cb - ca) / n
            p.caixa(d.get("frente", "frente"), fa + 0.002, -0.03, 0.1, fb - 0.002, 0.0, 0.86, 0.003)
            p.caixa("metal_preto", fa + 0.06, 0.0, 0.83, fb - 0.06, 0.012, 0.845, 0.002)
        p.caixa("bancada", ca, -P - 0.02, 0.86, cb, 0.02, 0.9, 0.004)
    px = d.get("placa")
    if px is not None:
        p.caixa("vidro_preto", x0 + px - 0.3, -0.52, 0.9, x0 + px + 0.3, -0.04, 0.905, 0.003)
        for dx, dy in ((-0.15, -0.16), (0.15, -0.16), (-0.15, -0.38), (0.15, -0.38)):
            p.cil("metal_preto", x0 + px + dx, dy, 0.905, 0.9055, 0.09, seg=32)
        p.caixa("inox", x0 + px - 0.45, -P + 0.02, 1.55, x0 + px + 0.45, -P + 0.5, 1.6, 0.006)       # hood
        p.caixa("inox", x0 + px - 0.14, -P + 0.02, 1.6, x0 + px + 0.14, -P + 0.28, 2.6, 0.004)
        p.caixa("led", x0 + px - 0.35, -P + 0.25, 1.548, x0 + px + 0.35, -P + 0.3, 1.55)
    sx = d.get("lava")
    if sx is not None:
        p.caixa("inox", x0 + sx - 0.3, -0.48, 0.74, x0 + sx + 0.3, -0.08, 0.903, 0.01)
        p.caixa("metal_preto", x0 + sx - 0.28, -0.46, 0.745, x0 + sx + 0.28, -0.1, 0.76)
        p.tubo("inox", (x0 + sx, -0.55, 0.9), (x0 + sx, -0.55, 1.22), 0.014)
        p.tubo("inox", (x0 + sx, -0.55, 1.22), (x0 + sx, -0.36, 1.22), 0.012)
        p.tubo("inox", (x0 + sx, -0.36, 1.22), (x0 + sx, -0.36, 1.12), 0.01)
    for sa, sb in d.get("prateleiras", []):        # open oak shelves on the wall, with things on them
        for zz in (1.45, 1.85):
            p.caixa("carvalho", x0 + sa, -P, zz, x0 + sb, -P + 0.28, zz + 0.04, 0.005)
            p.caixa("led", x0 + sa + 0.02, -P + 0.24, zz - 0.004, x0 + sb - 0.02, -P + 0.26, zz)
            jarra(p, {"alt": 0.22}, (x0 + sa + 0.2, -P + 0.14, zz + 0.04))
            livros(p, {"n": 5}, (x0 + sb - 0.25, -P + 0.12, zz + 0.04))
    if d.get("tabua", True) and px is not None:
        p.caixa("carvalho", x0 + px + 0.45, -0.58, 0.9, x0 + px + 0.85, -0.56, 1.2, 0.01)
        planta(p, {"alt": 0.35, "vaso": "vaso"}, (x0 + px + 1.2, -0.4, 0.9))


def lareira(p, d):
    L, P, h = d.get("larg", 3.3), d.get("prof", 0.62), d.get("alt", 0.42)
    p.caixa("microcimento", -L / 2, -P, 0, L / 2, 0, h, 0.01)
    w = d.get("fogo", 0.9)
    p.caixa("metal_preto", -w / 2 - 0.06, -P + 0.02, h, w / 2 + 0.06, -0.04, h + 0.6, 0.01)
    p.caixa("vidro_int", -w / 2, -0.06, h + 0.06, w / 2, -0.04, h + 0.54, 0.003)
    p.caixa("metal_preto", -w / 2, -P + 0.08, h + 0.06, w / 2, -0.07, h + 0.08)
    for i, dx in enumerate((-0.2, 0.0, 0.2)):
        p.tubo("brasa", (dx - 0.12, -0.32, h + 0.11), (dx + 0.12, -0.22, h + 0.11), 0.035)
    p.esfera("chama", 0, -0.27, h + 0.2, 0.12, (1.8, 0.4, 0.9))
    p.esfera("chama", -0.15, -0.27, h + 0.17, 0.08, (1.2, 0.4, 1.0))
    p.luz("POINT", 0, -0.2, h + 0.25, 25, 0.12, (1.0, 0.55, 0.25))
    p.cil("metal_preto", 0, -P / 2, h + 0.6, d.get("teto", 2.94), 0.09)
    jarra(p, {"alt": 0.4}, (-L / 2 + 0.3, -P / 2, h))
    livros(p, {"n": 6, "deitados": True}, (L / 2 - 0.4, -P / 2, h))
    planta(p, {"alt": 0.8}, (L / 2 + 0.35, -0.35, 0))


def cama(p, d):
    """Bed with its head against the wall behind (y = -C/2): upholstered headboard and base, a rounded mattress, a duvet
    that rolls over the sides and the foot, a throw across the foot, sleeping pillows and a cushion leaning back."""
    L, C = d.get("larg", 1.8), d.get("comp", 2.05)
    y0, y1 = -C / 2, C / 2
    p.macio("tecido", 0, y0 - 0.02, 0.6, L / 2 + 0.05, 0.045, 0.55, e1=0.2, e2=0.15, puff=0.01, eixo="y")   # headboard
    p.macio("tecido", 0, 0.01, 0.19, L / 2, C / 2 - 0.01, 0.13, e1=0.22, e2=0.08)                   # base
    p.caixa("metal_preto", -L / 2 + 0.1, y0 + 0.12, 0, L / 2 - 0.1, y1 - 0.1, 0.06)
    p.macio("roupa", 0, 0.02, 0.42, L / 2 - 0.02, C / 2 - 0.04, 0.11, e1=0.3, e2=0.08, puff=0.01)    # mattress
    p.lencol("roupa", -L / 2 + 0.01, y0 + 0.62, L / 2 - 0.01, y1 - 0.03, 0.555, 0.27, r=0.07, rugas=0.01,
             semente=1)                                                                            # duvet
    p.lencol("manta", -L / 2 + 0.01, y1 - 0.62, L / 2 - 0.01, y1 - 0.06, 0.585, 0.3, r=0.085, frente=False,
             rugas=0.014, semente=2)                                                               # throw
    n = 2 if L > 1.2 else 1
    for i in range(n):
        cx = -L / 2 + (i + 0.5) * L / n
        p.travesseiro("roupa", cx, y0 + 0.2, 0.72, 0.34, 0.2, 0.09, inclinar=28)
        p.travesseiro("almofada", cx + (0.06 if i else -0.06), y0 + 0.36, 0.68, 0.22, 0.15, 0.07, inclinar=20)
    if d.get("mesinhas", True):
        for sx in (-1, 1):
            mesinha(p, {}, (sx * (L / 2 + 0.33), y0 + 0.25, 0))
    if d.get("tapete", True):
        p.caixa("la", -L / 2 - 0.55, y0 + 0.5, 0.0, L / 2 + 0.55, y1 + 0.75, 0.014, 0.006)


def mesinha(p, d, o=(0, 0, 0)):
    x, y, z = o
    p.caixa("nogueira", x - 0.24, y - 0.2, z + 0.12, x + 0.24, y + 0.2, z + 0.5, 0.008)
    p.caixa("metal_preto", x - 0.2, y - 0.16, z, x + 0.2, y + 0.16, z + 0.12)
    candeeiro_mesa(p, {}, (x, y - 0.03, z + 0.5))


def roupeiro(p, d):
    L, P, h = d["larg"], d.get("prof", 0.6), d.get("alt", 2.4)
    p.caixa("lacado", -L / 2, -P, 0.0, L / 2, -0.02, h)
    n = max(2, round(L / 0.5))
    for i in range(n):
        a, b = -L / 2 + i * L / n, -L / 2 + (i + 1) * L / n
        p.caixa(d.get("mat", "lacado"), a + 0.002, -0.02, 0.08, b - 0.002, 0.0, h - 0.002, 0.003)
        lado = b - 0.05 if i % 2 == 0 else a + 0.05
        p.caixa("latao", lado - 0.008, 0.0, 0.95, lado + 0.008, 0.02, 1.25, 0.004)


def secretaria(p, d):
    L, P = d.get("larg", 1.5), d.get("prof", 0.65)
    p.caixa("carvalho", -L / 2, -P / 2, 0.71, L / 2, P / 2, 0.75, 0.006)
    for sx in (-1, 1):
        p.caixa("metal_preto", sx * (L / 2 - 0.05) - 0.02, -P / 2 + 0.05, 0, sx * (L / 2 - 0.05) + 0.02, P / 2 - 0.05,
                0.71)
    p.caixa("metal_preto", -0.3, -0.05, 0.75, 0.3, -0.04, 1.08, 0.004)                                # screen
    p.caixa("metal_preto", -0.04, -0.12, 0.75, 0.04, -0.05, 0.85)
    candeeiro_mesa(p, {"potencia": 10}, (L / 2 - 0.2, -0.15, 0.75))
    livros(p, {"n": 4, "deitados": True}, (-L / 2 + 0.25, -0.1, 0.75))
    cadeira(p, {}, (0, P / 2 + 0.1, 0), 180)


def estante(p, d):
    L, P, h = d.get("larg", 1.6), d.get("prof", 0.35), d.get("alt", 2.0)
    for sx in (-1, 0, 1):
        x = sx * (L / 2 - 0.015) if sx else 0
        p.caixa("carvalho", x - 0.015, -P, 0, x + 0.015, 0, h, 0.003)
    rng = ctx["RNG"]
    for i, zz in enumerate([0.0] + [h * k / 5 for k in range(1, 5)] + [h - 0.03]):
        p.caixa("carvalho", -L / 2, -P, zz, L / 2, 0, zz + 0.03, 0.003)
        if 0 < i < 5:
            for half in (-1, 1):
                if rng.random() < 0.75:
                    livros(p, {"n": int(rng.integers(5, 12))}, (half * L / 4 + rng.uniform(-0.1, 0.1), -P / 2, zz + 0.03))
                else:
                    jarra(p, {"alt": 0.2}, (half * L / 4, -P / 2, zz + 0.03))


def livros(p, d, o=(0, 0, 0)):
    x, y, z = o
    rng = ctx["RNG"]
    n = d.get("n", 6)
    if d.get("deitados"):
        zz = z
        for i in range(n):
            t = rng.uniform(0.02, 0.04)
            w, l = rng.uniform(0.15, 0.2), rng.uniform(0.22, 0.28)
            p.caixa(f"livro{int(rng.integers(0, 7))}", x - l / 2, y - w / 2, zz, x + l / 2, y + w / 2, zz + t, 0.003)
            zz += t
        return
    xx = x - n * 0.016
    for i in range(n):
        t, h, w = rng.uniform(0.02, 0.04), rng.uniform(0.18, 0.27), rng.uniform(0.14, 0.2)
        p.caixa(f"livro{int(rng.integers(0, 7))}", xx, y - w / 2, z, xx + t, y + w / 2, z + h, 0.002)
        xx += t + 0.002


JARRAS = ["ceramic_vase_01", "ceramic_vase_04", "ceramic_vase_02"]


def jarra(p, d, o=(0, 0, 0)):
    x, y, z = o
    h = d.get("alt", 0.25)
    aid = JARRAS[int(ctx["RNG"].integers(0, len(JARRAS)))]
    if p.modelo(aid, x, y, z, rot=float(ctx["RNG"].uniform(0, 360)), alt=h * 1.3):
        return
    p.cil(d.get("mat", "vaso"), x, y, z, z + h * 0.7, 0.06 * h / 0.25, 0.09 * h / 0.25, 24)
    p.cil(d.get("mat", "vaso"), x, y, z + h * 0.7, z + h, 0.09 * h / 0.25, 0.04 * h / 0.25, 24)


def planta(p, d, o=(0, 0, 0)):
    """A potted plant: a pot and leaves (curved blades) fanning out of it."""
    x, y, z = o
    h = d.get("alt", 1.2)
    aid = "potted_plant_02" if h >= 0.6 else "potted_plant_04"     # leafy plant in a clay pot / succulent
    if p.modelo(aid, x, y, z, rot=float(ctx["RNG"].uniform(0, 360)), alt=min(h, 0.97 if h >= 0.6 else 0.45)):
        return
    rv = 0.11 + h * 0.08
    p.cil(d.get("vaso", "vaso_escuro"), x, y, z, z + rv * 1.6, rv * 0.8, rv, 24)
    p.cil("terra", x, y, z + rv * 1.5, z + rv * 1.55, rv * 0.95, seg=24)
    rng = ctx["RNG"]
    zt = z + rv * 1.5
    nfol = int(14 + h * 18)
    verts, faces = [], []
    for k in range(nfol):
        az = rng.uniform(0, 2 * math.pi)
        incl = rng.uniform(0.15, 1.15)
        comp = rng.uniform(0.45, 1.0) * h
        larg = rng.uniform(0.04, 0.09) * (0.6 + h * 0.4)
        d_ = Vector((math.cos(az), math.sin(az), 0))
        lado = Vector((-math.sin(az), math.cos(az), 0))
        base = len(verts)
        segs = 6
        for s in range(segs + 1):
            t = s / segs
            ang = incl * t * 1.4
            c = Vector((x, y, zt)) + d_ * (math.sin(ang) * comp * t * 0.9) + Vector((0, 0, math.cos(ang * 0.8) * comp * t))
            w = larg * math.sin(math.pi * min(1, t * 1.1 + 0.05))
            verts += [tuple(c - lado * w / 2), tuple(c + lado * w / 2)]
        for s in range(segs):
            faces.append((base + 2 * s, base + 2 * s + 1, base + 2 * s + 3, base + 2 * s + 2))
    p.malha("folha", verts, faces)


def quadro(p, d):
    L, h = d.get("larg", 0.9), d.get("alt", 0.65)
    zc = d.get("zc", 1.5)
    p.caixa("nogueira", -L / 2, -0.03, zc - h / 2, L / 2, 0.0, zc + h / 2, 0.003)
    p.caixa("papel", -L / 2 + 0.04, 0.0, zc - h / 2 + 0.04, L / 2 - 0.04, 0.002, zc + h / 2 - 0.04)
    rng = ctx["RNG"]
    for i in range(3):                    # an abstract print: three soft colour blocks
        a = -L / 2 + 0.1 + i * (L - 0.2) / 3
        hh = rng.uniform(0.3, 0.8) * (h - 0.2)
        p.caixa(f"tela{i + 1}", a + 0.01, 0.002, zc - h / 2 + 0.1, a + (L - 0.2) / 3 - 0.01, 0.004, zc - h / 2 + 0.1 + hh)


def sanita(p, d):
    """Wall-hung toilet against the wall behind (y = 0 the wall, the bowl toward +y): a slim panel in the wall's own
    finish with the flush plate, a rounded bowl (wider at the rim) and a soft-close lid."""
    e = 0.035                       # the panel stands proud of the wall (a face on the wall itself flickered)
    p.caixa(d.get("painel", "interior"), -0.3, 0.0, 0.0, 0.3, e, 1.12, 0.006)
    p.caixa("inox", -0.11, e, 0.98, 0.11, e + 0.006, 1.06, 0.003)
    p.macio("loica", 0, e + 0.27, 0.36, 0.175, 0.27, 0.075, e1=0.55, e2=0.45)                      # bowl
    p.macio("loica", 0, e + 0.29, 0.425, 0.185, 0.28, 0.022, e1=0.35, e2=0.5)                       # rim
    p.macio("loica", 0, e + 0.28, 0.462, 0.18, 0.275, 0.014, e1=0.3, e2=0.5)                        # lid
    p.caixa("loica", -0.12, e, 0.3, 0.12, e + 0.08, 0.44, 0.03, 3)                                 # where it meets the wall


def lavatorio(p, d):
    """Vanity against the wall behind (y = 0 the wall, front at +y): counter, basins, taps, a mirror above."""
    L, P = d.get("larg", 1.2), d.get("prof", 0.48)
    bacias = d.get("bacias", [0.0])
    p.caixa("carvalho", -L / 2, 0.0, 0.45, L / 2, P, 0.82, 0.006)
    p.caixa("bancada", -L / 2, 0.0, 0.82, L / 2, P + 0.01, 0.85, 0.003)
    for bx in bacias:
        p.cil("loica", bx, P * 0.55, 0.85, 0.98, 0.19, 0.2, 40)
        p.cil("metal_preto", bx, 0.06, 0.85, 1.12, 0.012)
        p.tubo("metal_preto", (bx, 0.06, 1.12), (bx, 0.2, 1.12), 0.01)
    p.caixa("espelho", -L / 2 + 0.05, 0.0, 1.1, L / 2 - 0.05, 0.01, 1.9, 0.004)
    p.caixa("led", -L / 2 + 0.05, 0.0, 1.9, L / 2 - 0.05, 0.02, 1.91)
    planta(p, {"alt": 0.3, "vaso": "vaso"}, (L / 2 - 0.12, 0.12, 0.85))


def duche(p, d):
    L, P = d.get("larg", 1.4), d.get("prof", 0.85)       # tray from y = 0 (wall) toward +y
    p.caixa("microcimento", -L / 2, 0.0, 0.0, L / 2, P, 0.03, 0.003)
    p.caixa("vidro_int", -L / 2 + 0.6, P - 0.01, 0.03, L / 2, P, 2.0)
    p.caixa("metal_preto", -L / 2 + 0.6, P - 0.015, 1.98, L / 2, P + 0.005, 2.0)
    p.cil("metal_preto", 0.0, 0.25, 2.1, 2.11, 0.15, seg=32)
    p.tubo("metal_preto", (0.0, 0.0, 2.11), (0.0, 0.25, 2.11), 0.01)
    p.tubo("metal_preto", (0.0, 0.01, 0.9), (0.0, 0.01, 1.2), 0.012)


def espelho(p, d):
    L, h = d.get("larg", 0.6), d.get("alt", 1.6)
    p.caixa("metal_preto", -L / 2, -0.02, d.get("z0", 0.3), L / 2, 0.0, d.get("z0", 0.3) + h, 0.005)
    p.caixa("espelho", -L / 2 + 0.015, 0.0, d.get("z0", 0.3) + 0.015, L / 2 - 0.015, 0.002, d.get("z0", 0.3) + h - 0.015)


def aparador(p, d):
    L, P, h = d.get("larg", 1.6), d.get("prof", 0.42), d.get("alt", 0.75)
    if p.modelo("modern_wooden_cabinet", 0, -P + 0.26, 0, larg=L):   # slatted sideboard 0,52 deep, back on the wall (y = -P)
        jarra(p, {"alt": 0.35}, (-L / 4, -P + 0.26, 0.68))
        livros(p, {"n": 3, "deitados": True}, (L / 4, -P + 0.26, 0.68))
        return
    p.caixa("nogueira", -L / 2, -P, 0.12, L / 2, 0.0, h, 0.008)
    for sx in (-1, 1):
        p.tubo("metal_preto", (sx * (L / 2 - 0.08), -P / 2, 0), (sx * (L / 2 - 0.08), -P / 2, 0.12), 0.015)
    jarra(p, {"alt": 0.35}, (-L / 4, -P / 2, h))
    livros(p, {"n": 3, "deitados": True}, (L / 4, -P / 2, h))


def espreguicadeira(p, d):
    p.caixa("carvalho", -0.33, -0.95, 0.0, 0.33, 0.95, 0.3, 0.01)
    p.caixa("exterior_tecido", -0.31, -0.93, 0.3, 0.31, 0.45, 0.38, 0.03, 3)
    v = [(-0.31, 0.45, 0.33), (0.31, 0.45, 0.33), (0.31, 0.93, 0.85), (-0.31, 0.93, 0.85)]
    p.malha("exterior_tecido", v + [(x, y + 0.08, z) for x, y, z in v], [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
                                                                         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], False)


def mesa_exterior(p, d):
    L, P = d.get("larg", 1.6), d.get("prof", 0.9)
    p.caixa("carvalho", -L / 2, -P / 2, 0.71, L / 2, P / 2, 0.75, 0.006)
    for sx in (-1, 1):
        p.caixa("metal_preto", sx * (L / 2 - 0.1) - 0.02, -P / 2 + 0.05, 0, sx * (L / 2 - 0.1) + 0.02, P / 2 - 0.05, 0.71)
    for sy, r in ((-1, 0), (1, 180)):
        for x in (-L / 4, L / 4):
            cadeira(p, {}, (x, sy * (P / 2 + 0.05), 0), r)
    jarra(p, {"alt": 0.25, "mat": "vaso_escuro"}, (0, 0, 0.75))


PECAS = {"sofa": sofa, "maple": maple, "mesa_centro": mesa_centro, "mesa_jantar": mesa_jantar, "tapete": tapete,
         "pendente": pendente, "candeeiro_pe": candeeiro_pe, "foco": foco, "cozinha": cozinha, "lareira": lareira,
         "cama": cama, "roupeiro": roupeiro, "secretaria": secretaria, "estante": estante, "sanita": sanita,
         "lavatorio": lavatorio, "duche": duche, "espelho": espelho, "quadro": quadro, "aparador": aparador,
         "espreguicadeira": espreguicadeira, "mesa_exterior": mesa_exterior,
         "planta": lambda p, d: planta(p, d), "jarra": lambda p, d: jarra(p, d),
         "livros": lambda p, d: livros(p, d), "cadeira": lambda p, d: cadeira(p, d),
         "mesinha": lambda p, d: mesinha(p, d), "candeeiro_mesa": lambda p, d: candeeiro_mesa(p, d)}


# ------------------------------------------------------------------------------------------------ stairs, doors, skirting
def escada(k, e):
    """A straight flight: oak treads on two steel stringers (open risers) or a concrete flight, with a handrail."""
    a, b = Vector(e["de"]), Vector(e["ate"])
    n = int(e.get("degraus", 16))
    larg = e.get("largura", 1.0)
    d = Vector((b.x - a.x, b.y - a.y, 0))
    run = d.length
    u = d.normalized()
    lado = Vector((-u.y, u.x, 0))
    rise = (b.z - a.z) / n
    tread = run / (n - 1) if n > 1 else run
    p = Peca(f"escada{k}", {"grupo": e.get("grupo", "interior")})
    madeira = e.get("tipo", "madeira") == "madeira"
    for i in range(n - 1):
        c0 = a + u * (i * tread)
        z = a.z + (i + 1) * rise
        pts = [c0 - lado * larg / 2 - u * 0.02, c0 + lado * larg / 2 - u * 0.02, c0 + lado * larg / 2 + u * (tread + 0.02),
               c0 - lado * larg / 2 + u * (tread + 0.02)]
        xs, ys = [q.x for q in pts], [q.y for q in pts]
        if madeira:
            p.caixa("carvalho", min(xs), min(ys), z - 0.045, max(xs), max(ys), z, 0.004)
        else:
            p.caixa("microcimento", min(xs), min(ys), a.z if i == 0 else z - rise - 0.15, max(xs), max(ys), z, 0.003)
    if madeira:                       # two stringers
        for s in (-1, 1):
            q0 = a + lado * s * (larg / 2 - 0.03) + Vector((0, 0, rise - 0.12))
            q1 = b + lado * s * (larg / 2 - 0.03) - Vector((0, 0, 0.12))
            p.tubo("metal_preto", q0, q1, 0.02, 6)
    if e.get("corrimao", True):
        s = e.get("lado_corrimao", 1)
        q0 = a + lado * s * (larg / 2 - 0.05) + Vector((0, 0, rise + 0.9))
        q1 = b + lado * s * (larg / 2 - 0.05) + Vector((0, 0, 0.9))
        p.tubo("metal_preto", q0, q1, 0.02)
        for t in (0.15, 0.5, 0.85):
            m = q0.lerp(q1, t)
            p.tubo("metal_preto", m - Vector((0, 0, 0.9)), m, 0.01)
    return p.fim()


def porta(k, e):
    """Interior door: lacquered jambs and a leaf left open 90 degrees against the wall."""
    x0, y0, z0, x1, y1, z1 = e["caixa"]
    p = Peca(f"porta{k}", {"grupo": e.get("grupo", "interior")})
    j = 0.03
    if e.get("eixo", "x") == "x":        # wall along y: the doorway spans y0..y1 through the wall's thickness x0..x1
        p.caixa("lacado", x0 - 0.005, y0 - j, z0, x1 + 0.005, y0, z1 + j)
        p.caixa("lacado", x0 - 0.005, y1, z0, x1 + 0.005, y1 + j, z1 + j)
        p.caixa("lacado", x0 - 0.005, y0 - j, z1, x1 + 0.005, y1 + j, z1 + j)
        s = e.get("abre", 1)
        xf = x1 if s > 0 else x0
        p.caixa("lacado", min(xf, xf + s * (y1 - y0 - 0.02)), y0, z0 + 0.01, max(xf, xf + s * (y1 - y0 - 0.02)), y0 + 0.04,
                z1 - 0.005, 0.003)
    else:
        p.caixa("lacado", x0 - j, y0 - 0.005, z0, x0, y1 + 0.005, z1 + j)
        p.caixa("lacado", x1, y0 - 0.005, z0, x1 + j, y1 + 0.005, z1 + j)
        p.caixa("lacado", x0 - j, y0 - 0.005, z1, x1 + j, y1 + 0.005, z1 + j)
        s = e.get("abre", 1)
        yf = y1 if s > 0 else y0
        p.caixa("lacado", x0, min(yf, yf + s * (x1 - x0 - 0.02)), z0 + 0.01, x0 + 0.04, max(yf, yf + s * (x1 - x0 - 0.02)),
                z1 - 0.005, 0.003)
    return p.fim()


def rodape(k, e):
    x0, y0, z0, x1, y1, z1 = e["caixa"]
    p = Peca(f"rodape{k}", {"grupo": e.get("grupo", "interior")})
    t, h = 0.012, 0.08
    p.caixa("lacado", x0, y0, z0, x1, y0 + t, z0 + h)
    p.caixa("lacado", x0, y1 - t, z0, x1, y1, z0 + h)
    p.caixa("lacado", x0, y0, z0, x0 + t, y1, z0 + h)
    p.caixa("lacado", x1 - t, y0, z0, x1, y1, z0 + h)
    return p.fim()


def construir(E, contexto):
    ctx.update(contexto)
    I = E.get("interior") or {}
    if not I:
        return []
    materiais()
    obs = []
    for k, e in enumerate(I.get("escadas", [])):
        obs += escada(k, e)
    for k, e in enumerate(I.get("portas", [])):
        obs += porta(k, e)
    for k, e in enumerate(I.get("rodapes", [])):
        obs += rodape(k, e)
    for k, d in enumerate(I.get("pecas", [])):
        p = Peca(f"{d['tipo']}{k}", d)
        PECAS[d["tipo"]](p, d)
        obs += p.fim()
    print("interior:", len(obs), "objetos,", len(LUZES), "luzes")
    return obs
