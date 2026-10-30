---
name: gsap-skills-no-repo
description: "As skills oficiais do GSAP estão versionadas dentro do repo DiscoverCasa, ao contrário do resto do .claude/"
metadata: 
  node_type: memory
  type: project
  originSessionId: 6e56afae-4330-46a8-b0b7-418b9b00bba4
  modified: 2026-08-28T15:47:41.800Z
---

O repositório DiscoverCasa versiona as 8 skills oficiais do GSAP em
`.claude/skills/gsap-*/` (de github.com/greensock/gsap-skills, MIT). Instaladas
em 2026-08-28 a pedido do utilizador.

**Why:** todo o site é GSAP + ScrollTrigger + Lenis, e o utilizador trabalha em
duas máquinas — queria que as skills viajassem com o repositório em vez de
serem reinstaladas à mão em cada uma.

**How to apply:** o `.gitignore` do repo ignora `.claude/` inteiro porque é
gerado pelo instalador do ECC; as skills do GSAP são a única excepção, escrita
como `.claude/skills/*` + `!.claude/skills/gsap-*/`. Tem de ser `skills/*` e
não `skills/`: com a pasta ignorada o git não entra lá dentro e a negação nunca
é lida. O Claude Code procura o `.claude/` a SUBIR a partir da pasta actual,
portanto se a sessão abrir na raiz do workspace é preciso copiá-las para lá —
o passo 2.3 do SETUP.md tem o comando. Ver [[discovercasa-ambiente]].
