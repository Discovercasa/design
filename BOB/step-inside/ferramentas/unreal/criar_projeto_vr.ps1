# Step Inside (Phase 8): creates the VR project on the home station from the repo's projeto_vr/ (copied to
# D:\BOB-posto\step-inside\projeto_vr) plus Unreal's own XR template content and input settings (5.8), and the
# script folder unreal-vr\ (the same scripts as unreal\, with the launchers of vr\ pointing at the VR project).
# Idempotent.
$ErrorActionPreference = 'Stop'
$ue = 'D:\Epic Games\UE_5.8'
$src = 'D:\BOB-posto\step-inside\projeto_vr'
$proj = 'D:\BOB-posto\unreal\StepInsideVR'
New-Item -ItemType Directory -Force "$proj\Config", "$proj\Content" | Out-Null
Copy-Item "$src\StepInsideVR.uproject" $proj -Force
Copy-Item "$src\Config\*" "$proj\Config" -Force
# the template's enhanced-input defaults (as a new VR project gets them)
Copy-Item "$ue\Templates\TP_VirtualRealityBP\Config\DefaultInput.ini" "$proj\Config\DefaultInput.ini" -Force
# the template's shared content packs, mounted where their assets expect them (/Game/<pack>)
foreach ($p in 'XRFramework', 'XRMannequins', 'VRSpectator') {
  $d = "$proj\Content\$p"
  if (-not (Test-Path $d)) { Copy-Item "$ue\Templates\TemplateResources\Standard\$p\Content" $d -Recurse }
}
# scripts: the same as for the images project; the VR launchers come from vr\ (repo: ferramentas/unreal/vr/)
$s = 'D:\BOB-posto\step-inside\unreal'
$v = 'D:\BOB-posto\step-inside\unreal-vr'
New-Item -ItemType Directory -Force $v | Out-Null
Get-ChildItem $s -Filter *.py | Copy-Item -Destination $v -Force
Get-ChildItem 'D:\BOB-posto\step-inside\vr' -Filter *.cmd | Copy-Item -Destination $v -Force
"projeto VR pronto: $proj"
(Get-ChildItem "$proj\Content" -Recurse -File | Measure-Object Length -Sum).Sum
