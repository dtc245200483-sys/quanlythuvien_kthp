$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Hệ thống Quản lý Thư viện AI (Docker)"

Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  HỆ THỐNG QUẢN LÝ THƯ VIỆN TÍCH HỢP AI - KHỞI CHẠY DOCKER" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

Write-Host "[1/4] Kiểm tra dịch vụ Docker Desktop..." -ForegroundColor Cyan
$dockerCheck = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [LỖI] Docker Desktop chưa được bật hoặc chưa khởi động xong!" -ForegroundColor Red
    Write-Host "  Vui lòng mở ứng dụng Docker Desktop trên máy tính rồi thử lại." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Nhấn Enter để thoát..."
    exit 1
}
Write-Host "  [OK] Docker Desktop đang hoạt động tốt." -ForegroundColor Green

Write-Host ""
Write-Host "[2/4] Khởi động các container (Backend + SQL Server 2022)..." -ForegroundColor Cyan
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [LỖI] Không thể bật container Docker Compose!" -ForegroundColor Red
    Read-Host "Nhấn Enter để thoát..."
    exit 1
}
Write-Host "  [OK] Các container đã sẵn sàng." -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] Kiểm tra Cơ sở dữ liệu và Dữ liệu mẫu..." -ForegroundColor Cyan
docker compose exec -T sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "Password123!" -C -Q "IF DB_ID('LibraryDB') IS NULL CREATE DATABASE LibraryDB;" | Out-Null
docker compose exec -T backend python -m alembic upgrade head | Out-Null
docker compose exec -T backend python scripts/seed_full.py
Write-Host "  [OK] Cơ sở dữ liệu và dữ liệu mẫu đã hoàn tất." -ForegroundColor Green

Write-Host ""
Write-Host "[4/4] Đang mở trình duyệt Web tại: http://localhost:8000/ ..." -ForegroundColor Cyan
Start-Process "http://localhost:8000/"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  [THANH CONG] HE THONG DA SAN SANG HOAT DONG!" -ForegroundColor Green
Write-Host "  Dia chi Web: http://localhost:8000/" -ForegroundColor Yellow
Write-Host ""
Write-Host "  DANH SACH TAI KHOAN DUNG THU:" -ForegroundColor White
Write-Host "  - Admin:      admin     / admin1" -ForegroundColor Gray
Write-Host "  - Thu thu:    librarian / librarian1" -ForegroundColor Gray
Write-Host "  - Doc gia 1:  docgia1   / docgia1 (Co san lich su muon va phat)" -ForegroundColor Gray
Write-Host "  - Doc gia 2:  docgia2   / docgia2" -ForegroundColor Gray
Write-Host "  - Doc gia:    reader    / reader1" -ForegroundColor Gray
Write-Host ""
Write-Host "  (De dung he thong, ban click dup file 2_dung_docker.bat)" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Read-Host "Nhan Enter de dong cua so nay (He thong van tiep tuc chay ngam)..."
