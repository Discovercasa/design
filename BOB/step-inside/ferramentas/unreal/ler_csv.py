"""Frame-time summary of an Unreal CSV profile (Step Inside Phase 4). Standard library only.

    python ler_csv.py "Profile(...).csv" [--saltar 1500] [--json out.json]

Unreal (-game -csvCaptureFrames=N -csvGpuStats) writes one row per frame; in a -game run of the editor binary the file
lands in %LOCALAPPDATA%/UnrealEngine/<version>/Saved/Profiling/CSV/ (not the project's Saved). The first frames load and
compile, so the summary skips --saltar frames (default: half). Prints, for FrameTime, GameThreadTime,
RenderThreadTime, RHIThreadTime and GPUTime (the ones present): median, p90, p99 in ms, and the FPS they mean.
"""
import argparse
import csv
import json
import statistics

COLUNAS = ["FrameTime", "GameThreadTime", "RenderThreadTime", "RHIThreadTime", "GPUTime"]


def ler(caminho):
    csv.field_size_limit(1 << 30)  # the EVENTS column can be long
    with open(caminho, newline="", encoding="utf-8", errors="replace") as f:
        linhas = list(csv.reader(f))
    cab = linhas[0]
    dados = []
    i_ft = cab.index("FrameTime") if "FrameTime" in cab else 1
    for ln in linhas[1:]:
        if not ln or ln[0].startswith("[") or len(ln) < len(cab) // 2:
            break  # metadata rows at the end ([HasHeaderRowAtEnd], [platform] …)
        try:
            float(ln[i_ft])
        except (ValueError, IndexError):
            break  # the header repeated at the end
        dados.append(ln)
    return cab, dados


def resumo(cab, dados, saltar=None):
    saltar = len(dados) // 2 if saltar is None else saltar
    dados = dados[saltar:]
    out = {"frames_total": len(dados) + saltar, "frames_usados": len(dados)}
    for c in COLUNAS:
        if c not in cab:
            continue
        i = cab.index(c)
        v = sorted(float(r[i]) for r in dados if i < len(r) and r[i] not in ("", "0"))
        if not v:
            continue
        p = lambda q: v[min(len(v) - 1, int(q * (len(v) - 1)))]
        med = statistics.median(v)
        out[c] = {"ms_mediana": round(med, 2), "ms_p90": round(p(0.9), 2), "ms_p99": round(p(0.99), 2),
                  "fps_mediana": round(1000 / med, 1), "fps_p90": round(1000 / p(0.9), 1)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--saltar", type=int)
    ap.add_argument("--json")
    a = ap.parse_args()
    cab, dados = ler(a.csv)
    r = resumo(cab, dados, a.saltar)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if a.json:
        json.dump(r, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
