@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\activate.bat (
  echo Rode install.cmd primeiro.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
if "%~1"=="" (
  python -m jarvis
) else (
  python -m jarvis %*
)
