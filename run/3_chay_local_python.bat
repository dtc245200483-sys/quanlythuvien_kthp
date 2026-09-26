@echo off
chcp 65001 >nul
title Khởi chạy Hệ thống Thư viện AI (Python Cục bộ)
color 0B

echo =====================================================================
echo   HỆ THỐNG QUẢN LÝ THƯ VIỆN TÍCH HỢP AI - CHẠY THỦ CÔNG PYTHON
echo =====================================================================
echo.

cd /d "%~dp0\..\Backend"

if exist ".venv\Scripts\activate.bat" (
    echo Kích hoạt môi trường ảo .venv...
    call .venv\Scripts\activate.bat
) else (
    echo [Thông báo] Không tìm thấy thư mục .venv, dùng Python hệ thống...
)

echo.
echo [1/3] Nâng cấp CSDL và nạp dữ liệu mẫu...
python -m alembic upgrade head
python scripts/seed_full.py

echo.
echo [2/3] Đang mở trình duyệt: http://localhost:8000/ ...
timeout /t 2 >nul
start http://localhost:8000/

echo.
echo [3/3] Đang khởi động máy chủ FastAPI Backend...
echo (Nhấn tổ hợp phím Ctrl + C để dừng máy chủ)
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
