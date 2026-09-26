@echo off
chcp 65001 >nul
title Khởi chạy Hệ thống Thư viện AI (Docker Compose)
color 0A

echo =====================================================================
echo   HỆ THỐNG QUẢN LÝ THƯ VIỆN TÍCH HỢP AI - CHẠY BẰNG DOCKER
echo =====================================================================
echo.

cd /d "%~dp0\.."

echo [1/4] Kiểm tra dịch vụ Docker Desktop...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [LỖI] Docker Desktop chưa được bật!
    echo Vui lòng mở ứng dụng Docker Desktop trên máy tính rồi chạy lại file này.
    echo.
    pause
    exit /b 1
)
echo   ✓ Docker Desktop đang hoạt động.
echo.

echo [2/4] Khởi động các container (Backend + SQL Server 2022)...
docker compose up -d
if %errorlevel% neq 0 (
    color 0C
    echo [LỖI] Không thể khởi động Docker Compose!
    pause
    exit /b 1
)
echo   ✓ Các container đã được bật thành công.
echo.

echo [3/4] Đồng bộ Cơ sở dữ liệu và Dữ liệu mẫu All-in-One...
:: Đảm bảo Database LibraryDB tồn tại trong SQL Server container
docker compose exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "Password123!" -C -Q "IF DB_ID('LibraryDB') IS NULL CREATE DATABASE LibraryDB;" >nul 2>&1

:: Nâng cấp bảng CSDL và nạp dữ liệu mẫu
docker compose exec backend python -m alembic upgrade head >nul 2>&1
docker compose exec backend python scripts/seed_full.py

echo.
echo [4/4] Đang mở trình duyệt vào hệ thống...
timeout /t 2 >nul
start http://localhost:8000/

echo.
echo =====================================================================
echo   🎉 HỆ THỐNG ĐÃ SẴN SÀNG!
echo   👉 Địa chỉ Web: http://localhost:8000/
echo.
echo   DANH SÁCH TÀI KHOẢN DÙNG THỬ:
echo   - Admin:      admin     / admin1
echo   - Thủ thư:    librarian / librarian1
echo   - Độc giả 1:  docgia1   / docgia1 (Có sẵn lịch sử mượn ^& phạt)
echo   - Độc giả 2:  docgia2   / docgia2
echo   - Độc giả:    reader    / reader1
echo.
echo   (Để tắt hệ thống: Chạy file '2_dung_docker.bat' trong thư mục này)
echo =====================================================================
echo.
pause
