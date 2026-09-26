[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Dung He thong Thu vien AI (Docker)"

Clear-Host
Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host "  DUNG HE THONG QUAN LY THU VIEN AI (DOCKER)" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host ""

$rootDir = Split-Path -Parent $PSScriptRoot
$dockerDir = Join-Path $rootDir "docker"
Set-Location $dockerDir

Write-Host "Dang dung va giai phong cac container..." -ForegroundColor Cyan
docker compose down

Write-Host ""
Write-Host "  [OK] Da dung toan bo dich vu an toan." -ForegroundColor Green
Write-Host "  [OK] Du lieu SQL Server va Vector Store van duoc luu tru nguyen ven tren volume." -ForegroundColor Gray
Write-Host ""
Read-Host "Nhan phim Enter de dong cua so..."
