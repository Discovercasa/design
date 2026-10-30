---
name: repo-git-setup
description: "Git/GitHub setup of the BOB Claude folder — private repo VascoCoelho/DiscoverCasa-Claude-BOB (moved 2026-09-26; user prefers that account); this clone pushes as VascoDiscovercasa via a repo-local credential helper"
metadata:
  node_type: memory
  type: reference
  originSessionId: c8378e88-b7fa-4d21-b82b-f405c200786a
  modified: 2026-09-30T17:04:53.938Z
---

- The private repo lives at https://github.com/VascoCoelho/DiscoverCasa-Claude-BOB (branch main). It was created 2026-09-23 under VascoDiscovercasa and transferred to VascoCoelho on 2026-09-26 (user, from another device). VascoDiscovercasa keeps write access; the old URL redirects.
- The user prefers the VascoCoelho account ("i use more that github account", 2026-09-30) and asked to push there.
- Since 2026-09-30 this clone's `origin` = `https://VascoDiscovercasa@github.com/VascoCoelho/DiscoverCasa-Claude-BOB.git` (user-authorized repoint; fetch/push work directly).
- This PC has two GitHub CLI accounts: VascoCoelho (the active default; leave it that way) and VascoDiscovercasa (git `user.name` of this clone).
- A repo-local credential helper for https://github.com runs `gh auth token --user VascoDiscovercasa`, so pushes authenticate as VascoDiscovercasa without switching the gh account. For `gh` commands against the repo, prefix `GH_TOKEN="$(gh auth token --hostname github.com --user VascoDiscovercasa)"`.
- Switching this PC's push login and commit author to VascoCoelho was offered on 2026-09-30, not done. It changes credential config, so only do it on the user's explicit OK.
- Other devices push too: `git fetch` before pushing; on rejection, rebase and resolve log/doc conflicts in date order.
- The file `PD_Habitacoes A B C D E K L M N O P (1).dwfx` at the folder root is the user's copy, re-saved by Design Review. It is ignored by git (`/*.dwfx`). The repo keeps the 16:08 original in `Construção Sobral/desenhos/`.
- Commit or push only when the user asks, or at the end of a task the user requested.

Related: [[project-wood-structure-analysis]]
