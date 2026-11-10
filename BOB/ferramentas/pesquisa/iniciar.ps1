# Starts the self-hosted Firecrawl (web scraping/search for Claude's research) on this PC, in Docker.
#   powershell -ExecutionPolicy Bypass -File BOB/ferramentas/pesquisa/iniciar.ps1          start (clones/updates the first time)
#   powershell -ExecutionPolicy Bypass -File BOB/ferramentas/pesquisa/iniciar.ps1 -Parar   stop and free the memory
# Needs Docker Desktop (WSL 2). The API answers only on this PC: http://127.0.0.1:3002 (no key; see README.md).
param(
  [switch]$Parar,
  [string]$Pasta = (Join-Path (Resolve-Path "$PSScriptRoot\..\..\..") "_trabalho\firecrawl"),
  [string]$Versao = "v2.11.0"
)
$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Host "O Docker não está instalado. Instala o Docker Desktop (https://www.docker.com/products/docker-desktop/, precisa de administrador e do WSL 2) e corre este script outra vez." -ForegroundColor Yellow
  exit 1
}

# Docker Desktop installed but stopped: start it and wait for the engine
$ErrorActionPreference = "Continue"
docker info *> $null
if ($LASTEXITCODE -ne 0) {
  $exe = Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe"
  if (Test-Path $exe) { Write-Host "A arrancar o Docker Desktop..."; Start-Process $exe }
  $limite = (Get-Date).AddMinutes(3)
  do { Start-Sleep -Seconds 5; docker info *> $null } while ($LASTEXITCODE -ne 0 -and (Get-Date) -lt $limite)
  if ($LASTEXITCODE -ne 0) { Write-Host "O Docker não arrancou em 3 minutos. Abre o Docker Desktop e tenta outra vez." -ForegroundColor Yellow; exit 1 }
}
$ErrorActionPreference = "Stop"

if (-not (Test-Path (Join-Path $Pasta "docker-compose.yaml"))) {
  Write-Host "A descarregar o Firecrawl $Versao para $Pasta ..."
  git clone --depth 1 --branch $Versao https://github.com/firecrawl/firecrawl.git $Pasta
}
Copy-Item (Join-Path $PSScriptRoot "docker-compose.override.yaml") $Pasta -Force
$envFile = Join-Path $Pasta ".env"
if (-not (Test-Path $envFile)) {
  # no secrets here: local only, no authentication, no LLM key (the /extract and JSON-format features stay off)
  @(
    "USE_DB_AUTHENTICATION=false",
    "PORT=3002",
    "NUM_WORKERS_PER_QUEUE=4",
    "CRAWL_CONCURRENT_REQUESTS=5",
    "MAX_CONCURRENT_JOBS=3",
    "BROWSER_POOL_SIZE=3",
    "LOGGING_LEVEL=info"
  ) | Set-Content -Path $envFile -Encoding ascii
}

Push-Location $Pasta
try {
  if ($Parar) { docker compose down; Write-Host "Firecrawl parado."; exit 0 }
  docker compose pull
  docker compose up -d --no-build
} finally { Pop-Location }

Write-Host "À espera da API em http://127.0.0.1:3002 ..."
$limite = (Get-Date).AddMinutes(4)
while ((Get-Date) -lt $limite) {
  try {
    $r = Invoke-RestMethod -Uri "http://127.0.0.1:3002/" -TimeoutSec 5
    Write-Host "Firecrawl pronto: $($r.message). Teste: python BOB/ferramentas/pesquisa/firecrawl.py ler https://example.com" -ForegroundColor Green
    exit 0
  } catch { Start-Sleep -Seconds 5 }
}
Write-Host "A API não respondeu em 4 minutos. Ver os registos: docker compose -f `"$Pasta\docker-compose.yaml`" logs api --tail 50" -ForegroundColor Yellow
exit 1
