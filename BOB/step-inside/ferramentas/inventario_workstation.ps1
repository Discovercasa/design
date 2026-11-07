# Step Inside · inventário de uma workstation candidata (só leitura: não instala nem muda nada).
# Uso:  powershell -ExecutionPolicy Bypass -File .\inventario_workstation.ps1
# Escreve o resultado no ecrã e em "inventario_workstation.txt" no Ambiente de Trabalho.
# Não recolhe nomes, números de série, nome do computador nem rede.
param([string]$Saida = (Join-Path ([Environment]::GetFolderPath('Desktop')) 'inventario_workstation.txt'))

$linhas = New-Object System.Collections.Generic.List[string]
function L($t) { $linhas.Add($t); Write-Output $t }
function Avalia($ok, $texto) { if ($ok) { L "  [OK]     $texto" } else { L "  [ABAIXO] $texto" } }

L "Step Inside · inventário da workstation · $(Get-Date -Format 'yyyy-MM-dd')"
L ""

$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
L "CPU: $($cpu.Name.Trim()) · $($cpu.NumberOfCores) núcleos / $($cpu.NumberOfLogicalProcessors) threads"

$ramGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
$mods = Get-CimInstance Win32_PhysicalMemory
$tipos = @{ 20 = 'DDR'; 21 = 'DDR2'; 24 = 'DDR3'; 26 = 'DDR4'; 34 = 'DDR5' }
$modTxt = ($mods | ForEach-Object {
    $t = $tipos[[int]$_.SMBIOSMemoryType]; if (-not $t) { $t = '?' }
    "$([math]::Round($_.Capacity / 1GB)) GB $t-$($_.Speed)" }) -join ', '
$arr = Get-CimInstance Win32_PhysicalMemoryArray | Select-Object -First 1
$maxGB = if ($arr.MaxCapacityEx) { [math]::Round($arr.MaxCapacityEx / 1MB) } else { [math]::Round($arr.MaxCapacity / 1MB) }
L "RAM: $ramGB GB ($modTxt) · ranhuras: $($arr.MemoryDevices) · máximo da motherboard: $maxGB GB"

$board = Get-CimInstance Win32_BaseBoard | Select-Object -First 1
L "Motherboard: $($board.Manufacturer) $($board.Product)"

$vram = @{}
Get-ItemProperty -Path "HKLM:\SYSTEM\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0*" -ErrorAction SilentlyContinue |
    Where-Object { $_.'HardwareInformation.qwMemorySize' } |
    ForEach-Object { $vram[$_.DriverDesc] = [math]::Round($_.'HardwareInformation.qwMemorySize' / 1GB) }
$gpus = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notmatch 'Virtual|Remote|Basic' }
foreach ($g in $gpus) {
    $v = $vram[$g.Name]; if (-not $v) { $v = '?' }
    L "GPU: $($g.Name) · $v GB · driver $($g.DriverVersion)"
}

$discos = Get-PhysicalDisk | Sort-Object DeviceId
foreach ($d in $discos) { L "Disco: $($d.FriendlyName) · $($d.MediaType) · $($d.BusType) · $([math]::Round($d.Size / 1GB)) GB" }
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    L "  Volume $($_.DeviceID) $([math]::Round($_.Size / 1GB)) GB, livres $([math]::Round($_.FreeSpace / 1GB)) GB" }

$os = Get-CimInstance Win32_OperatingSystem
L "Sistema: $($os.Caption) · versão $($os.Version) (build $($os.BuildNumber))"

L ""
L "Programas relevantes:"
$chaves = 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
          'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
          'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
Get-ItemProperty $chaves -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -match 'Blender|Unreal|Epic Games|Visual Studio [0-9]|Visual Studio Community|Meta Horizon|Oculus|SteamVR|NVIDIA Graphics Driver|Python 3\.[0-9.]+ \(64-bit\)$|Node\.js|^Git ' } |
    Sort-Object DisplayName, DisplayVersion -Unique | ForEach-Object { L "  $($_.DisplayName) $($_.DisplayVersion)" }
Get-ChildItem 'C:\Program Files\Blender Foundation' -Directory -ErrorAction SilentlyContinue | ForEach-Object { L "  Pasta Blender: $($_.Name)" }
Get-ChildItem 'C:\Program Files\Epic Games' -Directory -ErrorAction SilentlyContinue | ForEach-Object { L "  Pasta Epic Games: $($_.Name)" }

L ""
L "Comparação com o mínimo para o Unreal Engine 5 (Epic) e a especificação do Step Inside (§6.2):"
Avalia ($cpu.NumberOfCores -ge 4) "CPU com 4 ou mais núcleos (Epic: 4 núcleos a 2,5 GHz; especificação: plataforma moderna)"
Avalia ($ramGB -ge 32) "RAM ≥ 32 GB (Epic); a especificação recomenda 64 GB"
$maxV = ($vram.Values | Measure-Object -Maximum).Maximum
Avalia ($maxV -ge 8) "VRAM ≥ 8 GB (Epic); a especificação pede 16 GB no mínimo (RTX 5070 Ti)"
Avalia ([bool]($gpus | Where-Object { $_.Name -match 'RTX|RX [6-9][0-9]{3}|Arc' })) "GPU com ray tracing por hardware (Lumen: RTX 2000+, RX 6000+, Arc)"
Avalia ([int]$os.BuildNumber -ge 22000) "Windows 11 (recomendado pela Epic)"
Avalia ([bool]($discos | Where-Object { $_.BusType -eq 'NVMe' })) "Disco NVMe (especificação: 2 TB no mínimo)"
L ""
L "Não se lê por software: fonte de alimentação (W) e tamanho da caixa. Indique-os à mão se os souber."

$linhas | Out-File -FilePath $Saida -Encoding utf8
Write-Output ""
Write-Output "Guardado em: $Saida"
