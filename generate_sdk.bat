@echo off
:: ============================================================
:: generate_sdk.bat — Generate Python SDK via OpenAPI Generator CLI
:: ============================================================
title Inventory Management — SDK Generation

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║     Generating Python SDK via OpenAPI Generator CLI  ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: ── Set Java Memory Limits to prevent Out of Memory crashes ─
set JAVA_OPTS=-Xmx256m -Xms128m

:: ── Check npm (needed for openapi-generator-cli) ─────────────
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] npm not found. Install Node.js first.
    pause
    exit /b 1
)

:: ── Install openapi-generator-cli globally (if not present) ──
where openapi-generator-cli >nul 2>&1
if %errorlevel% neq 0 (
    echo  Installing @openapitools/openapi-generator-cli globally...
    npm install -g @openapitools/openapi-generator-cli
    if %errorlevel% neq 0 (
        echo  [ERROR] Failed to install openapi-generator-cli.
        pause
        exit /b 1
    )
    echo  [OK] openapi-generator-cli installed.
) else (
    echo  [OK] openapi-generator-cli already installed.
)

echo.
echo  NOTE: Ensure the backend is running at http://localhost:8000
echo        (run runapplication.bat or start backend manually first)
echo.

:: ── Generate SDK ──────────────────────────────────────────────
cd /d "%~dp0"
set SDK_OUTPUT=inventory_sdk

echo  Generating Python SDK into: %CD%\%SDK_OUTPUT%
echo.

openapi-generator-cli generate ^
    -i http://localhost:8000/openapi.json ^
    -g python ^
    -o "%SDK_OUTPUT%" ^
    --skip-validate-spec ^
    --additional-properties=packageName=inventory_sdk,projectName=inventory-sdk,packageVersion=1.0.0

if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] SDK generation failed.
    echo         Make sure the backend is running at http://localhost:8000
    pause
    exit /b 1
)

echo.
echo  [OK] SDK generated successfully in: %SDK_OUTPUT%
echo.
echo  ── Usage Example ────────────────────────────────────────────
echo.
echo    cd inventory_sdk
echo    pip install -e .
echo.
echo    Then in Python:
echo      from inventory_sdk.api.items_api import ItemsApi
echo      from inventory_sdk.api_client import ApiClient
echo      client = ApiClient()
echo      api = ItemsApi(client)
echo      result = api.list_items_items_get()
echo      print(result)
echo.
pause
