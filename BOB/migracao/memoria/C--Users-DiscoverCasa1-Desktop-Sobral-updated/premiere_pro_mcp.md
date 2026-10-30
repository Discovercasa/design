---
name: premiere-pro-mcp
description: "Adobe Premiere Pro MCP server install/config on this Windows machine — paths, temp dir, CEP bridge"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e920364-4f8d-47df-a163-99f70fd18b33
  modified: 2026-07-21T15:30:04.531Z
---

Installed & configured the **Adobe Premiere Pro MCP** server (github.com/hetpatel-11/Adobe_Premiere_Pro_MCP) on 2026-07-21. Node.js/TypeScript, 280 MCP tools, verified working via a live initialize + tools/list handshake.

Key locations on this machine:
- Repo: `C:\Users\DiscoverCasa1\Desktop\Sobral updated\Adobe_Premiere_Pro_MCP` (built → `dist/index.js`)
- Node.js: installed via winget (`OpenJS.NodeJS.LTS`, v24.x) at `C:\Program Files\nodejs\node.exe`
- Registered in **Claude Desktop** config (`%APPDATA%\Claude\claude_desktop_config.json`) as server key `premiere-pro`; backup saved alongside as `.bak-20260721`
- `PREMIERE_TEMP_DIR` = `C:\Users\DiscoverCasa1\premiere-mcp-bridge` (server and CEP panel MUST use the same path)
- CEP bridge extension copied to `%APPDATA%\Adobe\CEP\extensions\MCPBridgeCEP`
- Adobe CEP debug mode enabled: `HKCU\Software\Adobe\CSXS.9..12` → `PlayerDebugMode="1"` (reversible)
- Adobe Premiere Pro 2025 is installed.

Notes:
- Repo is officially macOS-only; `npm run setup:mac`/`setup:doctor` are bash scripts that don't run on Windows. The Node server + CEP panel are cross-platform (panel `bridge-cep.js` is Windows-aware), so it was set up manually.
- PATH gotcha: freshly-spawned shells don't see the winget-installed Node; refresh with `$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")`.
- To actually control Premiere: user must restart Claude Desktop + Premiere, open `Window > Extensions > MCP Bridge (CEP)`, set Temp Directory to the path above, Save Configuration, Start Bridge.

Unrelated to the [[project-sobral]] SketchUp work — same machine, different project.
