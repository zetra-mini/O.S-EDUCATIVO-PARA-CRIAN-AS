@echo off
cd /d "%~dp0"
echo ==============================================================================
echo Iniciando J.A.R.V.I.S. Kids OS (Microdot Ultraleve - Porta 8000)...
echo ==============================================================================
start "" python run_server.py 8000
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000
echo Pronto! Servidor ativo em http://127.0.0.1:8000
