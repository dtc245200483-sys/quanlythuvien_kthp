[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Khoi chay He thong Thu vien AI (Local Python)"

Clear-Host
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  HE THONG QUAN LY THU VIEN TICH HOP AI - CHAY LOCAL PYTHON" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $rootDir "Backend"
Set-Location $backendDir

if (Test-Path "$rootDir\.venv\Scripts\Activate.ps1") {
    Write-Host "Kich hoat moi truong ao .venv..." -ForegroundColor Gray
    & "$rootDir\.venv\Scripts\Activate.ps1"
} elseif (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Kich hoat moi truong ao .venv..." -ForegroundColor Gray
    & ".\.venv\Scripts\Activate.ps1"
}

Write-Host "[1/3] Nang cap CSDL va nap du lieu mau..." -ForegroundColor Cyan
python -m alembic upgrade head
python scripts/seed_full.py

Write-Host ""
Write-Host "[2/3] Dang mo trinh duyet Web: http://localhost:8000/ ..." -ForegroundColor Cyan
Start-Process "http://localhost:8000/"

Write-Host ""
Write-Host "[3/3] Dang khoi dong may chu FastAPI Backend..." -ForegroundColor Cyan
Write-Host "(Nhan to hop phim Ctrl + C de dung may chu)" -ForegroundColor Yellow
Write-Host ""
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
