---
name: discovercasa-video-pipeline
description: Local testimonial-to-Shorts video pipeline built on this Windows machine (ffmpeg + faster-whisper + karaoke captions)
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e920364-4f8d-47df-a163-99f70fd18b33
  modified: 2026-08-27T16:37:59.805Z
---

Built a **local, private** pipeline (2026-07-23) to turn a raw client-interview `.mov` into vertical, captioned social clips for DiscoverCasa (a house-building company; content lives under `Desktop\DiscoverCasa Vasquinho  Conteúdo\`).

**Tooling installed via winget (permanent):** Node 24, Python 3.12 (`C:\Users\DiscoverCasa1\AppData\Local\Programs\Python\Python312\python.exe` — the bare `python` alias is the Store stub, use the full path or `py`), ffmpeg 8.1 (`Gyan.FFmpeg`). Python pkg: `faster-whisper`. This CPU runs Whisper ~0.75× realtime.

**Pipeline steps:** ffmpeg extract 16 kHz mono wav → faster-whisper `medium` transcribe (pt, `word_timestamps=True`) → label question vs answer, build a cutlist of answer windows → per-clip ASS with word-by-word karaoke (active word yellow `&H00D4FF&`, one line ≤4 words, held across pauses) → ffmpeg crop `1216:2160:1740:0` (9:16, centred on the seated subject) → scale 1080×1920 → burn ass, libx264 veryfast crf20.

**First job:** `Testemunhos\Raw\IMG_4857.mov` (~11 min 4K, client **Luís Pedro**) → 16 answer-clips in `Testemunhos\Auto-Edit\Clips\` + `transcricao.srt/json` + `_INDICE_CLIPS.md`. Caption corrections map: roof→rufo, paracadistas→paraquedistas, Diniz→Dinis, phrase "uma peste"→"perto".

**Packaged as a portable private repo (2026-07-23):** [github.com/VascoDiscovercasa/testimonial-clipper](https://github.com/VascoDiscovercasa/testimonial-clipper) (PRIVATE), local copy at `Desktop\testimonial-clipper`. Portable argparse scripts `transcribe.py` + `make_karaoke.py` (paths as args, corrections loaded from JSON), README, `examples/` (cutlist + corrections). Media gitignored. GitHub CLI (`gh`) installed and authed as account **VascoDiscovercasa** (keyring). The raw session scripts (transcribe2.py etc.) live in the ephemeral scratchpad; the repo is the durable version. Git author set locally to.

**Fixing subtitles on an already-assembled testimonial (2026-07-28):** the client's published cut `Clips_final\TESTEMUNHO_Lispedro_FINAL.mp4` (1080x1920, 141.3s) had the karaoke burned into the pixels. **Never cover with a black band** — the user's whole point of the repo is to *re-render the clips clean*. Correct workflow: (1) re-transcribe the assembled final, map the requested wording fixes as phrase/word swaps in an `.ass`; (2) recover each source clip's exact window by **audio cross-correlation** (numpy FFT, 8kHz mono) of each assembled clip vs the 4K source — gives frame-accurate `source_start`; (3) re-cut those windows CLEAN from `Raw\IMG_4857.mov` with the same crop `crop=1216:2160:1740:0,scale=1080:1920`, concat, burn the corrected `.ass` (no band), prepend intro, one libx264 crf18 pass. That final was clips **[01,03,05,11,12,13,15]** — each keeps its cutlist2 START but the user trimmed the END shorter (e.g. clip01 21.0→36.2 not →81.9). Output: `TESTEMUNHO_Lispedro_FINAL_corrigido.mp4` (has intro `intro_dark_reel.mp4`, 2.4s, DiscoverCasa "TESTEMUNHOS" branded). Gotcha: a leftover `inspect.py` in the scratchpad shadows stdlib and breaks numpy import — rename it.

**Second testimonial — Karin (Ribamar), 2026-08-27.** Lives on the **D: drive**: `D:\DISCOVERCASA\DiscoverCasa Vasquinho  Conteúdo\Testemunhos\Karin Ribamar Testemunho\`. Karin speaks **English**; captions are a **hand-written PT translation** (`translations_pt.json`, keyed `segment.chunk`), not auto-translation. Source = two WhatsApp files joined **small (16.51.16, 57.443s) then big (16.41.43, 671.08s)** = 728.5s master; both are 1024×576 with **rotation=-90**, i.e. display 576×1024, so `scale=1080:1920:flags=lanczos` (no crop) is correct. Wind noise: `highpass=f=85,afftdn=nf=-25`. A previous device also wrote `translate_transcript.py` and a `--gpu` flag for make_karaoke — **never pushed**, so those don't exist in the repo.

**Repo now has (pushed 2026-08-27):** `make_anchored.py` (caption lines pinned to explicit times + cuts clips + assembles behind an intro — use this for translated captions or when timing is wrong; `--only N` re-renders one clip and rebuilds the cut) and `align_clips.py` (audio cross-correlation to locate finished clips in a master; `--cutlist` reports whether the deltas are one consistent offset). README carries the lessons. Don't rewrite these from scratch. Note `gh` has **two accounts** — `VascoCoelho` and `VascoDiscovercasa`; only the latter can see this private repo, and if the active one is wrong `git pull` fails with "Repository not found" (fix: `gh auth switch --user VascoDiscovercasa`).

**Key gotcha:** rebuilding the master by `concat -c copy` yields a timeline **+0.086s** vs the `cutlist.json` times (verified constant across 5 clips by audio cross-correlation) — add 0.086 to every cutlist time when cutting from a rebuilt master. Also: a stray `inspect.py` in the scratchpad shadows stdlib and breaks numpy — rename it.

**Caption style is identical to Lispedro** (verified by rendering test text and pixel-measuring): Arial **74**, MarginV **430**, Outline 5, white + active word `&H00D4FF&`, ~4 words per row.

Related: user is exploring a broader AI content-automation vision — see [[premiere-pro-mcp]] and the LangGraph/Higgsfield "Fábrica de Shorts" planning (artifact).
