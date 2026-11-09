"""Format matrix (spec §13 Fase 1, hub task 55): what each input format is to the pipeline.

    DIRECT            read by an existing tool, geometry/values can be extracted
    CONVERT_REQUIRED  usable after exporting it to a DIRECT format (e.g. DWG -> DWFx / vector PDF)
    REFERENCE_ONLY    for people to look at; no geometry or values are taken from it
    UNSUPPORTED       no reader yet
Terrain formats (Phase 2): step-inside/ferramentas/terreno/leitores.py.

classificar(path) looks inside the file when the extension is not enough (vector vs scanned PDF, DWFx with 3D).
"""
import re
import zipfile
from pathlib import Path

import comum  # noqa: F401  (puts BOB/ on sys.path for ferramentas.dwfx)

DIRECT, CONVERT, REFERENCE, UNSUPPORTED = "DIRECT", "CONVERT_REQUIRED", "REFERENCE_ONLY", "UNSUPPORTED"

# extension -> (category, reader / what to do, note)
FORMATOS = {
    ".dwfx": (DIRECT, "ferramentas/dwfx/leitor.py",
              "Plot 2D do AutoCAD: traços com cor, espessura e texto. Só tem 3D se o DWFx incluir um modelo."),
    ".pdf": (DIRECT, "ferramentas/dwfx/leitor_pdf.py",
             "PDF vetorial (plot): dá os mesmos traços do DWFx, sem texto. Digitalizado ou imagem: REFERENCE_ONLY."),
    ".json": (DIRECT, "ferramentas/configurador/para_construtor.py", "JSON do configurador (Build Your House)."),
    ".dwg": (CONVERT, "exportar para DWFx ou PDF vetorial (AutoCAD / DWG TrueView); terreno: DXF pelo ODA File Converter",
             "Sem leitor. O DWG tem a informação toda (camadas, 3D, cotas como objetos), mas é um formato fechado."),
    ".dxf": (DIRECT, "step-inside/ferramentas/terreno/leitores.py (terreno)",
             "DXF ASCII: pontos 3D, polilinhas 3D, curvas com elevação, faces 3D (Fase 2). Plantas em DXF: exportar para "
             "DWFx ou PDF vetorial. Linhas 2D sem cota nunca dão alturas."),
    ".dwf": (CONVERT, "voltar a exportar como DWFx", "DWF antigo (binário)."),
    ".ifc": (UNSUPPORTED, "—", "BIM aberto. Sem leitor; só se algum arquiteto o entregar."),
    ".rvt": (UNSUPPORTED, "—", "Revit: pedir DWFx/PDF ou IFC."),
    ".skp": (REFERENCE, "—", "Modelo SketchUp: só para ver."),
    ".tif": (CONVERT, "converter o DEM para ESRI ASCII (.asc) ou XYZ (ex.: gdal_translate -of AAIGrid)",
             "GeoTIFF/DEM: sem leitor direto (exige TIFF comprimido e georreferência). Se for só uma imagem: REFERENCE_ONLY."),
    ".tiff": (CONVERT, "como .tif", "Como .tif."),
    ".asc": (DIRECT, "step-inside/ferramentas/terreno/leitores.py", "DEM em ESRI ASCII grid: declarar unidade e CRS."),
    ".xml": (DIRECT, "step-inside/ferramentas/terreno/leitores.py", "LandXML: pontos, superfícies, linhas de quebra, curvas."),
    ".landxml": (DIRECT, "step-inside/ferramentas/terreno/leitores.py", "LandXML (superfície topográfica)."),
    ".las": (UNSUPPORTED, "—", "Nuvem de pontos."),
    ".laz": (UNSUPPORTED, "—", "Nuvem de pontos comprimida."),
    ".xyz": (DIRECT, "step-inside/ferramentas/terreno/leitores.py", "Pontos X Y Z: declarar unidade e CRS."),
    ".csv": (DIRECT, "step-inside/ferramentas/terreno/leitores.py", "Pontos X Y Z (com ou sem cabeçalho, vírgula decimal)."),
    ".docx": (REFERENCE, "—", "Memória descritiva ou caderno de encargos: texto para ler e confrontar."),
    ".doc": (REFERENCE, "—", "Como .docx."),
    ".xlsx": (REFERENCE, "—", "Mapa de quantidades ou de vãos: para ler e confrontar."),
    ".txt": (REFERENCE, "—", "Texto. Pontos X Y Z em .txt: lidos pelo terreno se declarados em terreno.json."),
}
for _e in (".jpg", ".jpeg", ".png", ".webp", ".heic", ".gif", ".bmp"):
    FORMATOS[_e] = (REFERENCE, "—", "Imagem ou foto: só para ver (nunca se tira um terreno de uma imagem aérea).")

_VERSOES_DWG = {"AC1015": "AutoCAD 2000", "AC1018": "AutoCAD 2004", "AC1021": "AutoCAD 2007",
                "AC1024": "AutoCAD 2010", "AC1027": "AutoCAD 2013", "AC1032": "AutoCAD 2018 ou mais recente"}


def _pdf_vetorial(path):
    """(category, note): a plot with many vector strokes is DIRECT; a scan / picture is REFERENCE_ONLY."""
    from ferramentas.dwfx.leitor_pdf import Pdf
    b = Path(path).read_bytes()
    imagens = len(re.findall(rb"/Subtype\s*/Image", b))
    try:
        pdf = Pdf(b)
        tracos = [len(pdf.paths(k)) for k in range(1, len(pdf.pages) + 1)]
    except Exception as e:  # noqa: BLE001 - any parse failure means a human has to look
        return REFERENCE, f"Não foi possível ler o PDF ({type(e).__name__}); ver à mão.", {"imagens": imagens}
    extra = {"paginas": len(tracos), "tracos_por_pagina": tracos, "imagens": imagens}
    if max(tracos or [0]) >= 200:
        return DIRECT, "PDF vetorial.", extra
    return REFERENCE, ("PDF com imagem (digitalizado ou raster): não dá geometria." if imagens
                       else "PDF quase sem traços: ver à mão."), extra


def classificar(path):
    """Return dict(formato, categoria, leitor, nota, ...extra) for one file."""
    p = Path(path)
    ext = p.suffix.lower()
    cat, leitor, nota = FORMATOS.get(ext, (UNSUPPORTED, "—", "Formato desconhecido."))
    out = {"formato": ext.lstrip(".").upper() or "?", "categoria": cat, "leitor": leitor, "nota": nota}
    if ext == ".pdf":
        cat, nota2, extra = _pdf_vetorial(p)
        out.update(categoria=cat, nota=nota2, **extra)
        if cat != DIRECT:
            out["leitor"] = "—"
    elif ext == ".dwg":
        cab = p.read_bytes()[:6].decode("ascii", "replace")
        out["versao"] = _VERSOES_DWG.get(cab, cab)
    elif ext == ".dwfx":
        try:
            nomes = zipfile.ZipFile(p).namelist()
            out["tem_3d"] = any(n.lower().endswith(".w3d") for n in nomes)
        except zipfile.BadZipFile:
            out.update(categoria=UNSUPPORTED, nota="DWFx danificado (não é um zip).")
    return out
