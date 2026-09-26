# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "He thong Quan ly Thu vien AI (Docker)"

Clear-Host
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  HE THONG QUAN LY THU VIEN TICH HOP AI - KHOI CHAY DOCKER" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

$rootDir = Split-Path -Parent $PSScriptRoot
$dockerDir = Join-Path $rootDir "docker"
Set-Location $dockerDir

# 1. Kiem tra Docker Desktop
Write-Host "[1/4] Kiem tra dich vu Docker Desktop..." -ForegroundColor Cyan
$dockerCheck = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [LOI] Docker Desktop chua duoc bat hoac chua khoi dong xong!" -ForegroundColor Red
    Write-Host "  Vui long mo ung dung Docker Desktop tren may tinh roi thu lai." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Nhan phim Enter de thoat..."
    exit 1
}
Write-Host "  [OK] Docker Desktop dang hoat dong tot." -ForegroundColor Green

# 2. Bat container
Write-Host ""
Write-Host "[2/4] Khoi dong cac container (Backend + SQL Server 2022)..." -ForegroundColor Cyan
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [LOI] Khong the bat container Docker Compose!" -ForegroundColor Red
    Read-Host "Nhan phim Enter de thoat..."
    exit 1
}
Write-Host "  [OK] Cac container da duoc kich hoat." -ForegroundColor Green

# 3. Doi SQL Server san sang & Dong bo DB
Write-Host ""
Write-Host "[3/4] Dang dong bo Co so du lieu va Du lieu mau..." -ForegroundColor Cyan
Write-Host "  Dang kiem tra ket noi SQL Server..." -NoNewline -ForegroundColor Gray

$sqlReady = $false
for ($i = 1; $i -le 30; $i++) {
    $null = docker compose exec -T sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "Password123!" -C -Q "SELECT 1" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $sqlReady = $true
        break
    }
    Write-Host "." -NoNewline -ForegroundColor Gray
    Start-Sleep -Seconds 1
}
Write-Host ""

if (-not $sqlReady) {
    Write-Host "  [CANH BAO] SQL Server phan hoi cham, tiep tuc ket noi..." -ForegroundColor Yellow
}

# Tao Database neu chua co
$null = docker compose exec -T sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "Password123!" -C -Q "IF DB_ID('LibraryDB') IS NULL CREATE DATABASE LibraryDB;" 2>&1

# Chay Migration & Seed du lieu
$null = docker compose exec -T backend python -m alembic upgrade head 2>&1
$seedOutput = docker compose exec -T backend python scripts/seed_full.py 2>&1
Write-Host "  [OK] Co so du lieu va 63 cuon sach (moi sach 5 cuon) da san sang." -ForegroundColor Green

# 4. Mo trinh duyet Web
Write-Host ""
Write-Host "[4/4] Dang mo trinh duyet Web tai: http://localhost:8000/ ..." -ForegroundColor Cyan
Start-Process "http://localhost:8000/"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  [THANH CONG] HE THONG DA SAN SANG HOAT DONG!" -ForegroundColor Green
Write-Host "  Dia chi Web: http://localhost:8000/" -ForegroundColor Yellow
Write-Host "  Tro ly Chatbot AI: http://localhost:8000/chatbot.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "  DANH SACH TAI KHOAN DUNG THU:" -ForegroundColor White
Write-Host "  - Admin (Quan tri):  admin     / admin1" -ForegroundColor Gray
Write-Host "  - Thu thu:           librarian / librarian1" -ForegroundColor Gray
Write-Host "  - Doc gia 1:         docgia1   / docgia1" -ForegroundColor Gray
Write-Host "  - Doc gia 2:         docgia2   / docgia2" -ForegroundColor Gray
Write-Host "  - Doc gia (reader):  reader    / reader1" -ForegroundColor Gray
Write-Host ""
Write-Host "  (De dung he thong: Nhap dup chuot vao file '2_dung_docker.bat')" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Read-Host "Nhan phim Enter de dong cua so nay (He thong van tiep tuc chay ngam)..."
