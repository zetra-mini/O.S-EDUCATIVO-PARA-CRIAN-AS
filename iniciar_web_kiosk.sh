#!/usr/bin/env bash
# ==============================================================================
# INICIADOR DO MODO WEB QUIOSQUE — JARVIS KIDS OS
# Otimizado para Acer Aspire One 532 (1024x600, antiX Linux)
# ==============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# 1. Encerra instâncias antigas na porta 5090 se houver
fuser -k 5090/tcp >/dev/null 2>&1 || true

# 2. Inicia o servidor Flask local ultraleve em segundo plano (< 25 MB RAM)
python3 simulador_web.py &
SERVER_PID=$!

sleep 1.2

# 3. Abre o navegador leve em modo quiosque limpo (sem abas, sem barra de navegação)
if command -v chromium >/dev/null 2>&1; then
  chromium --app=http://127.0.0.1:5090 --start-fullscreen --kiosk --process-per-site --disable-features=Translate,OptimizationHints --disable-background-networking
elif command -v chromium-browser >/dev/null 2>&1; then
  chromium-browser --app=http://127.0.0.1:5090 --start-fullscreen --kiosk --process-per-site --disable-features=Translate
elif command -v firefox-esr >/dev/null 2>&1; then
  firefox-esr --kiosk http://127.0.0.1:5090
fi

# 4. Encerra o backend ao sair do quiosque
kill $SERVER_PID >/dev/null 2>&1 || true
