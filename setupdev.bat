@echo off
:: ============================================================
:: setupdev.bat — Inventory Management System: Development Setup
:: Sets up Python venv + installs backend deps + installs frontend
:: ============================================================
title Inventory Management — Dev Setup

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║     Inventory Management System — Dev Setup          ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: ── Verify Python ────────────────────────────────────────────
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found. Please install Python 3.11+ and try again.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo  [OK] Found %%v

:: ── Verify Node.js ───────────────────────────────────────────
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Node.js not found. Please install Node.js 18+ and try again.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version') do echo  [OK] Found Node.js %%v

:: ── Verify npm ───────────────────────────────────────────────
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] npm not found. Please install Node.js (includes npm).
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('npm --version') do echo  [OK] Found npm v%%v

echo.
echo  ── Setting up Backend ───────────────────────────────────
echo.

:: Navigate to backend
cd /d "%~dp0backend"

:: Create virtual environment
if not exist "env\" (
    echo  Creating Python virtual environment...
    python -m venv env
    if %errorlevel% neq 0 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
) else (
    echo  [OK] Virtual environment already exists, skipping.
)

:: Activate and install dependencies
echo  Installing Python dependencies...
call env\Scripts\activate
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [ERROR] pip install failed. Check requirements.txt and your internet connection.
    pause
    exit /b 1
)
echo  [OK] Backend dependencies installed.

:: Run Alembic migrations
echo  Running database migrations...
alembic upgrade head
if %errorlevel% neq 0 (
    echo  [WARN] Alembic migration failed. The app will still create tables on startup.
)
echo  [OK] Database ready.

:: Optional: seed the database
if exist "inventory.db" (
    echo  [INFO] inventory.db already exists, skipping seed.
) else (
    echo  Seeding database with sample data...
    sqlite3 inventory.db < seed_data.sql >nul 2>&1
    if %errorlevel% equ 0 (
        echo  [OK] Sample data loaded.
    ) else (
        echo  [INFO] sqlite3 CLI not found — seed data can be loaded manually.
    )
)

echo.
echo  ── Setting up Frontend ──────────────────────────────────
echo.

cd /d "%~dp0frontend"

echo  Installing Node.js dependencies...
npm install --silent
if %errorlevel% neq 0 (
    echo  [ERROR] npm install failed.
    pause
    exit /b 1
)
echo  [OK] Frontend dependencies installed.

echo.
echo  ── Running Backend Tests ────────────────────────────────
echo.

cd /d "%~dp0backend"
call env\Scripts\activate
echo  Running unit tests...
python -m pytest tests/ -v --tb=short
if %errorlevel% neq 0 (
    echo  [WARN] Some tests failed — review output above.
) else (
    echo  [OK] All tests passed!
)

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   Setup Complete! Run runapplication.bat to start.  ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
pause
