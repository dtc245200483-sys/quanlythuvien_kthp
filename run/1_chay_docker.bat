@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title Khoi chay He thong Thu vien AI (Docker)

if not exist "%~dp0run_docker.ps1" (
    echo [LOI] Khong tim thay file run_docker.ps1 trong thu muc %~dp0
    echo Vui long kiem tra lai ma nguon!
    echo.
    pause
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_docker.ps1"
if %errorlevel% neq 0 (
    echo.
    echo [CANH BAO] Qua trinh khoi chay Docker gap loi hoac bi huy!
    echo.
    pause
)
