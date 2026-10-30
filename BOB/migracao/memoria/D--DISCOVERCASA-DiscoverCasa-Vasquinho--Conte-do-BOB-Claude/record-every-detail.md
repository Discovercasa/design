---
name: record-every-detail
description: "The user wants every detail from our conversations memorised. Record it in the repo (verbatim log + the matching doc) before a task ends, using the agent guardiao-detalhes"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c8378e88-b7fa-4d21-b82b-f405c200786a
  modified: 2026-09-24T16:55:40.990Z
---

Nothing the user says may be lost, even small details. Before a task ends:
- Append the user's words **verbatim** to the repo file `conhecimento/registo-conversas.md`, with the date, the context, and where each fact was filed.
- File each fact in its document: `sistema-construtivo.md`, or the project's `docs/estado.md`, `desenhos.md` or `revisao-tecnica.md`.
- Check the new facts against what is already recorded.

The agent `.claude/agents/guardiao-detalhes.md` in the repo does this. It does not see the conversation, so pass it the user's text verbatim.

**Why:** the user asked for this on 2026-09-24: "Memorize what we talk about even the small detail because in construction it matter". They also asked for an agent that stores every detail and keeps track of everything that matters. The repo travels to other devices; this local memory does not.

**How to apply:** use the repo files, not local memory, for project facts. Keep promises of later information ("I will inform you later") as pending items in `docs/estado.md`.

Related: [[flag-issues-with-suggestions]], [[project-wood-structure-analysis]], [[repo-git-setup]]
