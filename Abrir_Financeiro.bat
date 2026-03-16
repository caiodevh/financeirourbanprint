@echo off
setlocal
cd /d "%~dp0"

if exist "dist\FinanceiroUrbanoPrint.exe" (
  start "" "dist\FinanceiroUrbanoPrint.exe"
  exit /b 0
)

if exist ".venv\Scripts\python.exe" (
  start "" ".venv\Scripts\python.exe" "run.py"
  exit /b 0
)

python "run.py"
