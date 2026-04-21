@echo off
:: ============================================================
:: runapplication.bat — Inventory Management System: Run App
:: Starts FastAPI backend + ReactJS frontend in separate windows
:: ============================================================
title Inventory Management — Launch

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║     Inventory Management System — Starting Up        ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: ── Check virtual env exists ─────────────────────────────────
if not exist "%~dp0backend\env\Scripts\activate" (
    echo  [ERROR] Backend environment not found.
    echo         Please run setupdev.bat first.
    pause
    exit /b 1
)

:: ── Check frontend node_modules ───────────────────────────────
if not exist "%~dp0frontend\node_modules" (
    echo  [ERROR] Frontend node_modules not found.
    echo         Please run setupdev.bat first.
    pause
    exit /b 1
)

echo  Starting FastAPI Backend on http://localhost:8000 ...
start "Inventory API — Backend" cmd /k "cd /d "%~dp0backend" && call env\Scripts\activate && python main.py"

:: Brief pause so backend has time to initialize
timeout /t 3 /nobreak >nul

echo  Starting ReactJS Frontend on http://localhost:3000 ...
start "Inventory UI — Frontend" cmd /k "cd /d "%~dp0frontend" && set NODE_OPTIONS=--max_old_space_size=4096 && npm start"

echo.
echo  ── Services starting ──────────────────────────────────────
echo.
echo   Backend API : http://localhost:8000
echo   Swagger UI  : http://localhost:8000/docs
echo   ReDoc       : http://localhost:8000/redoc
echo   OpenAPI JSON: http://localhost:8000/openapi.json
echo   Frontend UI : http://localhost:3000
echo.
echo   Two terminal windows have been opened.
echo   Close them to stop the services.
echo.

:: Open the browser after a short delay
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo  [OK] Browser opening...
pause
