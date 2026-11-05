@echo off
cd /d "%~dp0"
echo Iniciando Simulador Web J.A.R.V.I.S. Kids OS...
start "" pythonw simulador_web.py
timeout /t 1 /nobreak >nul
start http://127.0.0.1:5090
echo Pronto! Servidor ativo em http://127.0.0.1:5090
