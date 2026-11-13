# Render stations (postos de render) — any PC, started from the hub

**Role (user 2026-11-13):** the GPU work of the client pages (Cycles images, the light baked for the web 3D, the 360°
tour, the open-data surroundings) and the Step Inside Unreal/VR. Later, the unattended worker of the Builder app (hub
task 178), once the Hub side gives each station a technical account (doc for Sebastião: «Postos de render e contas
técnicas: o que é preciso», 2026-11-13).

**Any PC (user 2026-11-13):** «quero que seja possível fazer isto em qualquer PC por exemplo se o sebastião quiser
fazer os renders no PC dele, visto que é superior ao meu. Mas quero que antes de começar a usar a gráfica seja
possível nos no HUB darmos a ordem de começar o uso do PC desejado.» So: every station runs the same program with
its own technical account; the hub lists the stations (name, GPU, last signal, free/busy, an «available» switch its
owner controls); each request gets a chosen station and the «Começar neste PC» order — **without that order no PC
uses its GPU**. The first station is the user's home PC (below); Sebastião's PC can be another (asked in the doc).
The setup below is the same on every station.

## Station 1: the user's home PC
Inventory 2026-11-07 (script output); GPU confirmed by the user 2026-11-13 («sim é uma RTX 2060»):
Ryzen 9 5900X (12 cores) · 32 GB DDR4-3200 · **RTX 2060 6 GB** (Turing: Cycles uses OptiX) · SATA SSDs, one with
~200 GB free (2026-11-13) · no NVMe yet (2 TB planned before the Unreal phase). Already there (user): Blender
(5.2.2 seen 2026-11-07), Unreal — check the versions.

**Disk budget.** Client pages: tools ~2 GB; per house the drawings, the open data (OSM ~25 MB, terrain ~10 MB), the
Blender scene and the renders/panoramas/page ~1–2 GB → 200 GB is plenty. Unreal 5: engine ~60 GB, each project
10–50 GB plus tens of GB of derived-data cache → a first Unreal test fits; the NVMe when projects grow.

## Privacy
Client drawings, the open-data extracts (they locate a house) and the pages stay under `BOB/_trabalho/` (git-ignored)
and in the hub's private storage — never in Git. BitLocker on that disk, a password on the Windows account. The user
wants this work on that PC (2026-11-13), which implies it may hold client files — confirm once.

## Setting up a station (any PC)
**The user (once):**
1. Install the Claude desktop app and sign in with the same account.
2. Git for Windows and the GitHub CLI if missing; `gh auth login` with the account that pushes Discovercasa/design.
3. Clone on the disk with space, e.g. `git clone https://github.com/Discovercasa/design.git D:\DiscoverCasa\design`.
4. Open that folder in the Code tab and write: «Configura este PC como posto de render: segue
   BOB/conhecimento/posto-render.md». (Another station: the same, with that PC's owner.)

**The Claude session on that PC** (each download or install: name, source, size, and the user's yes first):
1. `git config core.quotepath false`; `python BOB/ferramentas/verificar.py` (Python ≥ 3.10, Blender, git, scratch).
2. Blender in the same family as the office (5.2.x); `BLENDER_EXE` if not found. GPU check:
   `blender -b --factory-startup --python-expr "import bpy; p=bpy.context.preferences.addons['cycles'].preferences; p.compute_device_type='OPTIX'; p.refresh_devices(); print([d.name for d in p.devices])"`
   must list the RTX 2060. `ferramentas/pagina/casa_blender.py` picks OptiX on RTX cards by itself (prints
   `GPU: OPTIX …`), CUDA otherwise (the office GTX 1050 Ti: OptiX lists it but its kernel fails).
3. A recent NVIDIA Studio driver (ask before installing).
4. ODA File Converter (free, DWG → DXF; ask before downloading).
5. Python packages: none for the BOB tools (standard library); numpy only inside Blender.
6. Unreal: note the installed version (Step Inside targets 5.8).
7. Report what was missing and what was installed; record it in `conhecimento/registo-conversas-2026-3.md` and here.

## Working on it
- **Phase 1 (now):** the heavy jobs run in a Claude session on that PC (repo + tools there). Client files come from
  the hub's private storage by the one-time-key route, or the user copies them.
- **Following from elsewhere (optional, ask first):** Remote Control in the Claude app (phone, office); later SSH
  (OpenSSH + a VPN such as Tailscale) so an office session can start jobs there.
- **Memory:** a session there does not see the office conversations; the shared memory is the repo (`BOB/CLAUDE.md`,
  `conhecimento/`) — keep it current.
- **Phase 2 (hub task 178):** the worker — the same small Python program on every station. Idle by default: it sends
  a heartbeat and only takes a request whose station is itself AND whose «Começar neste PC» order was given in the
  hub; then it downloads the drawings, runs the reader and Blender, uploads the page «por aprovar», writes the Log
  (which station) and deletes the downloaded drawings. It signs in with its station's technical account; the secret
  lives only in that PC's Windows Credential Manager. Waits for Sebastião (accounts, unattended sign-in).
