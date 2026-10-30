# DiscoverCasa · Claude BOB

Knowledge base and tools that let Claude (Claude Code / Claude desktop) work on DiscoverCasa
timber-frame projects from any device: read the engineers' DWFx drawings, review them, and build
editable Blender models of the houses — timber structure plus the DiscoverCasa build-up layers
(OSB, membrane, cladding options, insulation, Pladur, floors, ceilings, sandwich roof).

## Layout
```
CLAUDE.md                 short instructions loaded by Claude in every session (map of the repo)
conhecimento/             company, build system (sistema construtivo) and timber-construction knowledge
ferramentas/              tools: dwfx/ (read & render drawings), modelo/ (drawings + build-up -> Blender), verificar.py
.claude/skills/           step-by-step procedures Claude loads only when needed
Construção Sobral/        Loteamento Sobral project
  CLAUDE.md               project summary
  desenhos/               original DWFx drawings
  docs/                   drawing map, technical review, models, warehouse, status & decisions
  modelos/tipo1/          config.json (edit) -> .blend / 2 x .glb (structure, complete) / quantidades.csv
_trabalho/                local scratch (renders, caches) - not in git
```

## Set up a new device
1. Install Git, Python 3.10+, Blender 4.4 or newer, and Claude Code (or the Claude desktop app).
2. `gh auth login` (or any Git login) with the account that has access, then
   `git clone https://github.com/VascoCoelho/DiscoverCasa-Claude-BOB.git`
3. `cd DiscoverCasa-Claude-BOB && git config core.quotepath false && python ferramentas/verificar.py`
4. Open the folder in Claude Code and ask for what you need — Claude reads `CLAUDE.md` automatically.
5. New Claude account or device: `python migracao/restaurar_memoria.py` restores Claude's memory (see
   `migracao/LEIA-ME.md`, in Portuguese).

Rendering DWFx sheets to images needs Windows; everything else works on Windows, macOS and Linux.

## Everyday commands
```bash
python ferramentas/dwfx/dwfx.py info "Construção Sobral/desenhos/PD_Habitacoes F G H I J.dwfx"
python ferramentas/modelo/construir_casa.py "Construção Sobral/modelos/tipo1/config.json"
```
Open `.blend` files with Blender (4.4+): collections follow the build sequence and can be switched on
and off (eye icon), e.g. to show another cladding option. Open `.glb` files with any 3D viewer
(Windows 3D Viewer, online glTF viewers, phones).

## Notes
- Public repository (Discovercasa/design, folder `BOB/`): no personal data (NIF, addresses, IDs, names);
  client drawings stay local only (user 2026-10-30).
- Binary files (`.dwfx`, `.blend`, `.glb`) are stored directly in Git (small). If they grow past
  ~50 MB each, move them to Git LFS.
- The repo moved from `VascoDiscovercasa` to `VascoCoelho` on 2026-09-26 (`VascoDiscovercasa` keeps
  write access). Older clones still work through GitHub's redirect; point them at the new URL once:
  `git remote set-url origin https://github.com/VascoCoelho/DiscoverCasa-Claude-BOB.git`
