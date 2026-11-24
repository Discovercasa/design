# Step Inside (Phase 8): is the home station ready for the VR tour? Read-only. Prints one JSON line:
#   runtime  = the active OpenXR runtime (the headset's PC software: Meta Quest Link, SteamVR, Windows MR, Pico…)
#   servico  = that runtime's service/process is running
#   oculos   = a headset seen on USB (Quest by cable) — empty for Air Link / Wi-Fi, which is fine if servico is true
#   projeto  = the VR project and its baked level exist
#   pronto   = runtime + servico + projeto
$r = [ordered]@{ runtime = ''; ficheiro = ''; servico = $false; oculos = @(); projeto = $false; pronto = $false }
$k = Get-ItemProperty 'HKLM:\SOFTWARE\Khronos\OpenXR\1' -ErrorAction SilentlyContinue
if ($k -and $k.ActiveRuntime) {
  $r.ficheiro = $k.ActiveRuntime
  $f = [IO.Path]::GetFileName($k.ActiveRuntime).ToLower()
  if ($f -like 'oculus*') { $r.runtime = 'Meta Quest Link'; $r.servico = [bool](Get-Process OVRServer_x64, OVRService -ErrorAction SilentlyContinue) }
  elseif ($f -like 'steamxr*') { $r.runtime = 'SteamVR'; $r.servico = [bool](Get-Process vrserver -ErrorAction SilentlyContinue) }
  elseif ($f -like '*mixedreality*') { $r.runtime = 'Windows Mixed Reality'; $r.servico = $true }
  elseif ($f -like '*pico*') { $r.runtime = 'PICO'; $r.servico = [bool](Get-Process *pico* -ErrorAction SilentlyContinue) }
  elseif ($f -like '*virtualdesktop*') { $r.runtime = 'Virtual Desktop'; $r.servico = [bool](Get-Process *VirtualDesktop* -ErrorAction SilentlyContinue) }
  else { $r.runtime = $f; $r.servico = $true }
}
$r.oculos = @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue |
  Where-Object { $_.FriendlyName -match 'Quest|Oculus|Meta|Vive|Index|Pico|Reverb|Mixed Reality|HMD' } |
  Select-Object -ExpandProperty FriendlyName -Unique)
$r.projeto = (Test-Path 'D:\BOB-posto\unreal\StepInsideVR\Content\Visita\TV_VR.umap') -and
             (Test-Path 'D:\BOB-posto\unreal\StepInsideVR\Content\Visita\TV_VR_BuiltData.uasset')
$r.pronto = [bool]($r.runtime -and $r.servico -and $r.projeto)
$r | ConvertTo-Json -Compress
