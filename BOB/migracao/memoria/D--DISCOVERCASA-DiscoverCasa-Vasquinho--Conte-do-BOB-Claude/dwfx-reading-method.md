---
name: dwfx-reading-method
description: How DWFx drawings are read/rendered here — use the repo tool ferramentas/dwfx/dwfx.py (skill ler-dwfx); the Autodesk connector cannot open files
metadata:
  node_type: memory
  type: reference
  originSessionId: c8378e88-b7fa-4d21-b82b-f405c200786a
  modified: 2026-09-23T17:14:12.783Z
---

Use `python ferramentas/dwfx/dwfx.py info|texto|pecas|render|zoom`. The full procedure is in the repo skill `ler-dwfx`.

Key non-obvious facts:
- DWFx is an XPS zip. Don't extract it to disk (paths get too long).
- The System.Windows.Xps loader fails because pages reference fonts that aren't embedded. The tool de-obfuscates the `.odttf` fonts and renders standalone XAML through WPF in PowerShell.
- The Autodesk MCP connector only searches help docs; it can't open files.
- pdftoppm, PIL and PyMuPDF are not installed on this PC.

Related: [[project-wood-structure-analysis]]
