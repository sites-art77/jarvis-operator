@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
  echo Instale Python 3.11+ em https://www.python.org/downloads/
  echo Marque "Add python.exe to PATH" no instalador.
  pause
  exit /b 1
)

echo [1/4] Criando ambiente virtual...
py -3 -m venv .venv
if errorlevel 1 (
  echo Falhou ao criar .venv
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
echo [2/4] Instalando dependencias reais de controle do PC...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo pip install falhou
  pause
  exit /b 1
)

if not exist .env (
  copy .env.example .env >nul
)

echo [3/4] Abra o .env e cole NVIDIA_API_KEY=nvapi-SUA_CHAVE
notepad .env

echo [4/4] Teste de controle real: o mouse vai se mover sozinho.
echo Failsafe: jogue o mouse no canto SUPERIOR ESQUERDO para abortar.
pause
python -m jarvis --self-test
echo.
echo Pronto. Para conversar:  rodar.cmd
echo Ou:  python -m jarvis "abra o bloco de notas e escreva olá senhor"
pause
