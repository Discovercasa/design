# 11 · Lessons from the user's verdicts (DC)
Rulebook v1.0 (2026-11-27). Format: manual §16.2; classification: §16.3 (`09-metodo-qualidade.md`). Tags: see
`../design-interiores.md`.

One entry per verdict (approval with remarks, rejection or correction). A lesson is not automatically a rule: an
**execution error** is fixed in the model or the process; a **client preference** stays with that project; a **recurring
principle** becomes a guideline (in its topic file, citing the lesson) only after it holds in several contexts; a
**technical requirement** carries its source. The user's taste for DiscoverCasa's standard pages is a company preference
and goes to the style sheet or topic file with the user's words.

Entry format:
```
### Ln — YYYY-MM-DD — <piece / room / style> — <class: execution error | client preference | recurring principle | technical requirement>
- Problem: … (the user's words in Portuguese, as written)
- Context: room, dimensions, style, users, pieces involved
- Correction: what changed and why (file / tool)
- Resulting guideline: … — Applies when: … — Exceptions: …
- Filed in: <topic file / style sheet / none (execution error)>
```

## Lessons
### L1 — 2026-11-27 — Extending table page, sideboard with vases — execution error
- Problem: «o movel no fundo da sala esta na vertical e os vasos/jarros estão a flutuar da fix nisso»
- Context: real room of the extending-table page; Poly Haven sideboard imported as 3 roots (body + 2 doors), each
  rotated about its own origin, so the parts came apart and the vases stood on air.
- Correction: one common pivot for all roots of an imported multi-part scan; verified in a new render
  (`ferramentas/movel/blender_mesa.py`).
- Resulting guideline: imported multi-part scans are placed by ONE pivot, and placement is checked in a render that
  shows them (with what stands on them) before delivering — Applies when: any scan with several roots — Exceptions: none.
- Filed in: none (execution error); also here L2–L3 below, from Claude's own checks.

### L2 — 2026-11-27 — Extending table, marble — execution error (Claude's own check)
- Problem: Poly Haven `marble_01` proposed as slab marble; it is a stone paving with joints.
- Correction: ambientCG Marble021 (CC0), accepted by the user.
- Resulting guideline: look at a scan's/texture's preview before proposing it. Filed in: none.

### L3 — 2026-11-27 — Extending table, contact shadows — execution error (Claude's own check)
- Problem: contact-shadow blur with zero padding drew a frame on the rug.
- Correction: pad with edge values and feather the edges. Filed in: none.
