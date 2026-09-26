$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Dừng Hệ thống Thư viện AI (Docker)"

Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host "  DỪNG HỆ THỐNG QUẢN LÝ THƯ VIỆN AI (DOCKER)" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host ""

$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

Write-Host "Đang dừng và giải phóng container..." -ForegroundColor Cyan
docker compose down

Write-Host ""
Write-Host "  [OK] Đã dừng toàn bộ dịch vụ an toàn." -ForegroundColor Green
Write-Host "  (Dữ liệu SQL Server và Vector Store vẫn được lưu trữ nguyên vẹn trên volume)." -ForegroundColor Gray
Write-Host ""
Read-Host "Nhấn Enter để đóng cửa sổ..."
