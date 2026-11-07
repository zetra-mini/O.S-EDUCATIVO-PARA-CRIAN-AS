@echo off
title JARVIS Kids OS - Desktop Launcher
chcp 65001 >nul
cd /d "%~dp0..\.."

echo ==========================================================
echo 🚀 INICIANDO JARVIS KIDS O.S. NO SEU COMPUTADOR
echo ==========================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não foi encontrado no PATH!
    echo Por favor, instale o Python 3.10+ para executar o Jarvis Kids OS.
    pause
    exit /b 1
)

python deploy\desktop_app\jarvis_desktop.py
