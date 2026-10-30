"""DWFx command line. Run from anywhere:

  python ferramentas/dwfx/dwfx.py info    FILE
  python ferramentas/dwfx/dwfx.py texto   FILE --folha N [--regiao X0 Y0 X1 Y1] [--procura REGEX] [--sem-numeros]
  python ferramentas/dwfx/dwfx.py pecas   FILE --folha N [--regiao X0 Y0 X1 Y1] [--escala 50]
  python ferramentas/dwfx/dwfx.py render  FILE --folha N [--dpi 55] [--saida PNG]          (Windows)
  python ferramentas/dwfx/dwfx.py zoom    FILE --folha N --regiao X Y W H [--px 1600] [--saida PNG]  (Windows)

Sheet coordinates are millimetres from the top-left corner (A1 = 841 x 594).
Tip: `render` a whole sheet at low dpi first, then `zoom` into regions; read `texto` for exact values.
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.comum import pasta_trabalho  # noqa: E402
from ferramentas.dwfx.leitor import Dwfx, linhas  # noqa: E402
from ferramentas.dwfx.pecas import build_members, in_region  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def cmd_info(a):
    d = Dwfx(a.ficheiro)
    for s in d.info():
        s.pop("parte", None)
        print(s)


def cmd_texto(a):
    d = Dwfx(a.ficheiro)
    ls = linhas(d.glyphs(a.folha))
    num = re.compile(r"^[±+-]?\d+([,.]\d+)?$")
    for l in ls:
        if a.regiao:
            x0, y0, x1, y1 = a.regiao
            if not (x0 <= l["x"] <= x1 and y0 <= l["y"] <= y1):
                continue
        if a.procura and not re.search(a.procura, l["text"], re.I):
            continue
        if a.sem_numeros and num.match(l["text"].strip()):
            continue
        print(f'{l["x"]:6.1f} {l["y"]:6.1f} a={l["ang"]:>4} h={l["h"]:.1f}  {l["text"]}')


def cmd_pecas(a):
    d = Dwfx(a.ficheiro)
    ms = build_members(d.paths(a.folha))
    if a.regiao:
        ms = in_region(ms, a.regiao)
    s = a.escala / 1000.0
    c = Counter((m["section"], m["kind"], round((m["bbox"][2] - m["bbox"][0]) * s, 2),
                 round((m["bbox"][3] - m["bbox"][1]) * s, 2)) for m in ms)
    print(f"{len(ms)} timber members (section, view/cut, width_m, height_m): count")
    for k, v in c.most_common(60):
        print(" ", k, v)


def cmd_render(a):
    from ferramentas.dwfx.render import render_folha
    out = a.saida or pasta_trabalho("renders") / f"{Path(a.ficheiro).stem}_folha{a.folha}.png"
    print(render_folha(a.ficheiro, a.folha, out, a.dpi))


def cmd_zoom(a):
    from ferramentas.dwfx.render import zoom
    x, y, w, h = a.regiao
    out = a.saida or pasta_trabalho("renders") / f"{Path(a.ficheiro).stem}_f{a.folha}_{int(x)}_{int(y)}.png"
    print(zoom(a.ficheiro, a.folha, x, y, w, h, out, a.px))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name in ("info", "texto", "pecas", "render", "zoom"):
        p = sp.add_parser(name)
        p.add_argument("ficheiro")
        if name != "info":
            p.add_argument("--folha", type=int, default=1)
        if name in ("texto", "pecas"):
            p.add_argument("--regiao", type=float, nargs=4)
        if name == "texto":
            p.add_argument("--procura")
            p.add_argument("--sem-numeros", action="store_true")
        if name == "pecas":
            p.add_argument("--escala", type=float, default=50)
        if name == "render":
            p.add_argument("--dpi", type=float, default=55)
            p.add_argument("--saida")
        if name == "zoom":
            p.add_argument("--regiao", type=float, nargs=4, required=True, metavar=("X", "Y", "W", "H"))
            p.add_argument("--px", type=int, default=1600)
            p.add_argument("--saida")
    a = ap.parse_args()
    {"info": cmd_info, "texto": cmd_texto, "pecas": cmd_pecas, "render": cmd_render, "zoom": cmd_zoom}[a.cmd](a)


if __name__ == "__main__":
    main()
