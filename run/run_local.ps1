$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Khởi chạy Hệ thống Thư viện AI (Local Python)"

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  HỆ THỐNG QUẢN LÝ THƯ VIỆN TÍCH HỢP AI - CHẠY THỦ CÔNG PYTHON" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$backendDir = Join-Path (Split-Path -Parent $PSScriptRoot) "Backend"
Set-Location $backendDir

if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Kích hoạt môi trường ảo .venv..." -ForegroundColor Gray
    & ".\.venv\Scripts\Activate.ps1"
}

Write-Host "[1/3] Nâng cấp CSDL và nạp dữ liệu mẫu..." -ForegroundColor Cyan
python -m alembic upgrade head
python scripts/seed_full.py

Write-Host ""
Write-Host "[2/3] Đang mở trình duyệt Web: http://localhost:8000/ ..." -ForegroundColor Cyan
Start-Process "http://localhost:8000/"

Write-Host ""
Write-Host "[3/3] Đang khởi động máy chủ FastAPI Backend..." -ForegroundColor Cyan
Write-Host "(Nhấn tổ hợp phím Ctrl + C để dừng máy chủ)" -ForegroundColor Yellow
Write-Host ""
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
