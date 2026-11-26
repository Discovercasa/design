"""Runs INSIDE Unreal 5.8 (commandlet, VR project): readies the visit level for baked light and the VR pawn
(Step Inside Phase 8, profile VR_BAKED). Run after importar / ajustes_materiais / iluminacao (mobilidade STATIC) /
material_mestre / pos_processo, before the light bake.

    unreal-vr\\ue_cmd.cmd -run=pythonscript -script=D:/BOB-posto/step-inside/unreal-vr/vr_preparar.py -unattended -nop4 -NullRHI

Reads vr_preparar.json next to this script:
  {"nivel", "vistas": vistas.json (Blender world), "importar_resumo": importar.py's summary (the move to the origin),
   "uv_lightmap": "glb" (UV channel 1 comes in the GLB, made in Blender — preferred) or "gerar" (Unreal generates it),
   "texel_m": lightmap texels per metre, "res_min", "res_max", "res_chao", "nav_margem_m",
   "lightmass": {"ressaltos", "escala", "qualidade_indireta", "suavidade", "celula_volumetrica_cm"},
   "nanite": false (default; the forward VR renderer has no Nanite and drew, and Lightmass baked, each mesh's Nanite
   FALLBACK — simplified at relative error 1.0: thin boards moved, the OSB behind poked through the plasterboard as
   dark wedges, gaps opened at corners, the lightmap UVs warped; 2026-11-26),
   "volumetrico": label prefixes lit by the volumetric lightmap instead of a lightmap (furniture: dense meshes whose
   per-face lightmap UVs showed triangle facets; the build-up layers hidden inside walls and ceilings: no lightmap
   texels to bake, they still block light), "ressalto": {label prefix: Lightmass diffuse boost} (the sunlit grass
   and the wood floor bounced so much colour that the white living-room ceiling came out lime, then mustard; this damps
   their bounce in the bake without changing how they look), "lightmass": {"ressaltos_ceu": sky light bounces,
   "comprimir": false (uncompressed lightmaps)}}
1. every static mesh: lightmap UVs generated in channel 1 (build settings), static mobility, a lightmap resolution
   that follows the piece's size (texels per metre of its largest face, powers of two, clamped); the 3 km grass
   ground gets a small fixed one;
2. a Lightmass Importance Volume and a NavMesh Bounds Volume around the house (not the whole ground): Lightmass spends
   its photons on the house, the VR pawn teleports on the navigation mesh;
3. a sphere reflection capture in every room of the interior views (the forward renderer reflects from them);
4. the PlayerStart on the living-room floor (the VR pawn stands on it; the headset adds the eye height);
5. Lightmass: indirect bounces, finer static lighting scale, quality and smoothness of the indirect light.
"""
import json
import math
import os

import unreal

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vr_preparar.json"), encoding="utf-8") as f:
    CFG = json.load(f)
mundo = unreal.EditorLoadingAndSavingUtils.load_map(CFG["nivel"])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
# in a commandlet the editor subsystem can be None: the (older) static library has the same functions
# in a commandlet the static mesh editor module is not loaded: without it the subsystem is None and the old
# EditorStaticMeshLibrary fallback silently returned defaults (it logged "0 UV channels", set nothing)
unreal.SystemLibrary.execute_console_command(None, "Module Load StaticMeshEditor")
sme = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
with open(CFG["importar_resumo"], encoding="utf-8") as f:
    desl = json.load(f)["deslocamento_cm"]
with open(CFG["vistas"], encoding="utf-8") as f:
    VISTAS = json.load(f)["vistas"]


def diz(*a):
    unreal.log("SI_VRP " + " ".join(str(x) for x in a))


def ue(x, y):  # Blender world metres -> level cm (Unreal y is Blender -y; the house was moved to the origin)
    return x * 100 + desl[0], -y * 100 + desl[1]


def pot2(v):
    return 2 ** max(0, math.ceil(math.log2(max(v, 1))))


# 1. lightmaps
malhas_feitas, n_uv, n_act, n_vol, n_boost, n_nan = set(), 0, 0, 0, 0, 0
casa_lo, casa_hi = [1e18] * 3, [-1e18] * 3
for a in eas.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor):
        continue
    smc = a.static_mesh_component
    sm = smc.get_editor_property("static_mesh")
    if not sm:
        continue
    rot = a.get_actor_label()
    if rot == "SI_Ceu":  # the sky dome (iluminacao.py): movable on purpose, outside Lightmass and the house box
        continue
    # the engine's own meshes (the grass ground is /Engine/BasicShapes/Plane) are left alone: never edit engine content
    if sm.get_path_name() not in malhas_feitas and not sm.get_path_name().startswith("/Engine/"):
        malhas_feitas.add(sm.get_path_name())
        bs = sme.get_lod_build_settings(sm, 0)
        gerar = CFG.get("uv_lightmap", "gerar") == "gerar"  # "glb": UV channel 1 made in Blender (blender_para_unreal.py --lightmap)
        if bs.get_editor_property("generate_lightmap_u_vs") != gerar:
            bs.set_editor_property("generate_lightmap_u_vs", gerar)
            bs.set_editor_property("src_lightmap_index", 0)
            bs.set_editor_property("dst_lightmap_index", 1)
            sme.set_lod_build_settings(sm, 0, bs)
            n_uv += 1
        ns = sm.get_editor_property("nanite_settings")
        if ns.get_editor_property("enabled") != bool(CFG.get("nanite", False)):
            ns.set_editor_property("enabled", bool(CFG.get("nanite", False)))
            sm.set_editor_property("nanite_settings", ns)
            n_nan += 1
    smc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    vol = rot.startswith(tuple(CFG.get("volumetrico", [])))
    smc.set_editor_property("lightmap_type", unreal.LightmapType.FORCE_VOLUMETRIC if vol else unreal.LightmapType.DEFAULT)
    n_vol += vol
    boost = next((float(b) for pre, b in CFG.get("ressalto", {}).items() if rot.startswith(pre)), 1.0)
    lms = smc.get_editor_property("lightmass_settings")
    lms.set_editor_property("diffuse_boost", boost)
    smc.set_editor_property("lightmass_settings", lms)
    n_boost += boost != 1.0
    o, e = a.get_actor_bounds(False)
    dims = sorted([e.x * 2 / 100, e.y * 2 / 100, e.z * 2 / 100], reverse=True)  # metres, largest first
    if rot == "SI_Chao":
        res = CFG["res_chao"]
    else:
        res = min(CFG["res_max"], max(CFG["res_min"], pot2(max(dims[0], 0.1) * CFG["texel_m"])))
        if not rot.startswith("SITE_"):
            for i, (c, x) in enumerate(((o.x, e.x), (o.y, e.y), (o.z, e.z))):
                casa_lo[i], casa_hi[i] = min(casa_lo[i], c - x), max(casa_hi[i], c + x)
    smc.set_editor_property("override_light_map_res", True)
    smc.set_editor_property("overridden_light_map_res", int(res))
    n_act += 1
# the mesh builds are asynchronous: only once they are done does channel 1 exist; then point the lightmap at it and
# save each mesh (set before the build finished, the index was lost and Lightmass baked on the texture UVs: blocks
# and stripes of light)
unreal.AutomationUtilsBlueprintLibrary.finish_all_asset_compilation()
for caminho in sorted(malhas_feitas):
    sm = unreal.EditorAssetLibrary.load_asset(caminho)
    sm.set_editor_property("light_map_coordinate_index", 1)
    sm.set_editor_property("light_map_resolution", 64)
    unreal.EditorAssetLibrary.save_loaded_asset(sm, False)
amostra = unreal.EditorAssetLibrary.load_asset(sorted(malhas_feitas)[0])
diz("lightmaps: malhas", len(malhas_feitas), "definicoes mudadas", n_uv, "nanite mudado", n_nan, "atores", n_act, "amostra: canais",
    sme.get_num_uv_channels(amostra, 0), "indice", amostra.get_editor_property("light_map_coordinate_index"))
diz("iluminados pelo lightmap volumetrico", n_vol, "ressalto mudado", n_boost, CFG.get("ressalto", {}))
diz("caixa da casa cm", [round(x) for x in casa_lo], [round(x) for x in casa_hi])


# 2. volumes around the house (a spawned volume is a 200 cm cube: scale it)
def volume(cls, rotulo, margem_cm, z0=None, z1=None):
    lo = [casa_lo[0] - margem_cm, casa_lo[1] - margem_cm, casa_lo[2] if z0 is None else z0]
    hi = [casa_hi[0] + margem_cm, casa_hi[1] + margem_cm, casa_hi[2] if z1 is None else z1]
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == rotulo:
            eas.destroy_actor(a)
    v = eas.spawn_actor_from_class(cls, unreal.Vector(*[(l + h) / 2 for l, h in zip(lo, hi)]))
    v.set_actor_label(rotulo)
    v.set_actor_scale3d(unreal.Vector(*[(h - l) / 200 for l, h in zip(lo, hi)]))
    return v


volume(unreal.LightmassImportanceVolume, "SI_VR_Lightmass", 300)
volume(unreal.NavMeshBoundsVolume, "SI_VR_Navegacao", CFG["nav_margem_m"] * 100, -150, 350)

# 3. reflection captures, 4. player start
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("SI_VR_Reflexo"):
        eas.destroy_actor(a)
for v in VISTAS:
    x, y = ue(v["de"][0], v["de"][1])
    r = eas.spawn_actor_from_class(unreal.SphereReflectionCapture, unreal.Vector(x, y, 150))
    r.set_actor_label("SI_VR_Reflexo_" + v["id"])
    r.get_component_by_class(unreal.SphereReflectionCaptureComponent).set_editor_property("influence_radius", 700.0)
sala = next(v for v in VISTAS if v["id"] == "sala")
x, y = ue(sala["de"][0], sala["de"][1])
px, py = ue(sala["para"][0], sala["para"][1])
inicio = next(a for a in eas.get_all_level_actors() if isinstance(a, unreal.PlayerStart))
inicio.set_actor_location(unreal.Vector(x, y, 2), False, False)
inicio.set_actor_rotation(unreal.Rotator(0, 0, math.degrees(math.atan2(py - y, px - x))), False)
diz("inicio", [round(x), round(y), 2])

# 5. Lightmass
ws = mundo.get_world_settings()
lm = ws.get_editor_property("lightmass_settings")
L = CFG["lightmass"]
lm.set_editor_property("num_indirect_lighting_bounces", int(L["ressaltos"]))
lm.set_editor_property("static_lighting_level_scale", float(L["escala"]))
lm.set_editor_property("indirect_lighting_quality", float(L["qualidade_indireta"]))
lm.set_editor_property("indirect_lighting_smoothness", float(L["suavidade"]))
lm.set_editor_property("use_ambient_occlusion", True)
if L.get("ressaltos_ceu"):
    lm.set_editor_property("num_sky_lighting_bounces", int(L["ressaltos_ceu"]))
if L.get("celula_volumetrica_cm"):  # the volumetric lightmap lights the furniture: finer than the 2 m default
    lm.set_editor_property("volumetric_lightmap_detail_cell_size", float(L["celula_volumetrica_cm"]))
if "comprimir" in L:  # uncompressed lightmaps: no block artefacts in the soft gradients of white walls (4x the memory)
    lm.set_editor_property("compress_lightmaps", bool(L["comprimir"]))
ws.set_editor_property("lightmass_settings", lm)
diz("lightmass", {k: str(lm.get_editor_property(k)) for k in (
    "num_indirect_lighting_bounces", "static_lighting_level_scale", "indirect_lighting_quality",
    "indirect_lighting_smoothness", "num_sky_lighting_bounces", "compress_lightmaps")})
unreal.EditorLoadingAndSavingUtils.save_map(mundo, CFG["nivel"])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
diz("FEITO")
