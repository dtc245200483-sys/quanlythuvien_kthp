@echo off
chcp 65001 >nul
title Dừng Hệ thống Thư viện AI (Docker Compose)
color 0E

echo =====================================================================
echo   DỪNG HỆ THỐNG QUẢN LÝ THƯ VIỆN AI (DOCKER)
echo =====================================================================
echo.

cd /d "%~dp0\.."

echo Đang dừng và giải phóng container...
docker compose down

echo.
echo ✓ Đã dừng toàn bộ dịch vụ an toàn.
echo (Dữ liệu SQL Server và Vector Store vẫn được lưu trữ nguyên vẹn trên volume).
echo.
pause
