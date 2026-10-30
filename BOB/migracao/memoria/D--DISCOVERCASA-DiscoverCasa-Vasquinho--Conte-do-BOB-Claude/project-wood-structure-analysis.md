---
name: project-wood-structure-analysis
description: Loteamento Sobral project knowledge lives in the git repo (Construção Sobral/ folder); memory only points there
metadata:
  node_type: memory
  type: project
  originSessionId: c8378e88-b7fa-4d21-b82b-f405c200786a
  modified: 2026-09-23T17:14:09.264Z
---

Since 2026-09-23, all knowledge for the Sobral project (16 timber houses: Tipo 1 ×11, Tipo 2 ×5, plus a warehouse to redesign in timber) lives in the repo in this working folder, under `Construção Sobral/`:
- `CLAUDE.md` for the summary;
- `docs/estado.md` for status, next steps and open questions;
- `docs/desenhos.md` for the sheet maps;
- `docs/revisao-tecnica.md`, `docs/modelos.md` and `docs/armazem.md` for the rest.

The Tipo 1 Blender model is in `Construção Sobral/modelos/tipo1/` and is rebuilt with `python ferramentas/modelo/construir_casa.py`.

**Why:** the user wants any device that pulls the repo to be able to continue the work. Local memory doesn't travel with the repo.
**How to apply:** read and update the repo docs, not this memory. Update `docs/estado.md` at the end of every task and commit it with the work.

Related: [[repo-git-setup]], [[discovercasa-company]]
