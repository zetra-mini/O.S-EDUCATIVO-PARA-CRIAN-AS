@echo off
cd /d "%~dp0"
title J.A.R.V.I.S. Kids OS - Servidor Ultraleve
echo ==============================================================================
echo   J.A.R.V.I.S. KIDS OS - STARK EDUCATIONAL SYSTEM (Porta 8000)
echo ==============================================================================

curl -s -o nul http://127.0.0.1:8000/api/state
if %ERRORLEVEL% equ 0 (
    echo [*] O servidor ja esta rodando com sucesso na porta 8000!
    echo [*] Abrindo interface no navegador...
    start http://127.0.0.1:8000
    timeout /t 3 >nul
    exit /b 0
)

echo [*] Iniciando servidor Microdot ultraleve...
start "" python run_server.py 8000
timeout /t 2 /nobreak >nul

echo [*] Abrindo interface no navegador...
start http://127.0.0.1:8000
echo ==============================================================================
echo   Pronto! Servidor ativo: http://127.0.0.1:8000
echo   Painel dos Pais:        http://127.0.0.1:8000/pais
echo ==============================================================================
