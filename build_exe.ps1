Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

Write-Host "=== Framework Brief Desk : build EXE ==="

$py = $null
foreach ($c in @("py -3", "python", "python3")) { }
if (Get-Command py -ErrorAction SilentlyContinue) { $py = "py -3" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $py = "python" }
elseif (Get-Command python3 -ErrorAction SilentlyContinue) { $py = "python3" }

if (-not $py) {
  Write-Host "[ERROR] Python was not found."
  exit 1
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
  Invoke-Expression "$py -m venv .venv"
}

& ".venv\Scripts\python.exe" -m pip install -U pip
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt -r requirements-build.txt
& ".venv\Scripts\python.exe" -c "from aio_logo import write_build_icon; write_build_icon('icon.ico')"
& ".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean FrameworkBriefDesk.spec
Write-Host "EXE: $PWD\dist\FrameworkBriefDesk.exe"
