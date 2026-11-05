@echo off
title Servidor OpenCode LAN - JARVIS Kids OS
echo ==============================================================================
echo J.A.R.V.I.S. Kids OS - Iniciar Servidor OpenCode para Rede Local (LAN / Netbook)
echo ==============================================================================
echo.
set PORT=4096

where opencode >nul 2>nul
if %errorlevel% neq 0 (
    echo [AVISO] OpenCode CLI nao encontrado no PATH!
    echo Instalando via npm...
    npm install -g --allow-scripts=opencode-ai opencode-ai
)

echo [OK] OpenCode CLI detectado.
echo.
echo Servidor OpenCode rodando na porta %PORT%.
echo No Netbook Asus/Acer One, aponte o servidor para o IP deste computador:
echo http://192.168.1.X:%PORT%
echo.
opencode serve --port %PORT%
pause
