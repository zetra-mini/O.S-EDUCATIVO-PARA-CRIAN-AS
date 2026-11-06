#!/usr/bin/env bash
# ==============================================================================
# INICIADOR DO MODO WEB QUIOSQUE — JARVIS KIDS OS
# Otimizado para Acer Aspire One 532 (1024x600, antiX Linux / Intel Atom N450)
# Microdot Server Ultraleve (< 15 MB RAM) + Chromium/Firefox Kiosk
# ==============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# 1. Encerra instâncias antigas na porta 8000 se houver
fuser -k 8000/tcp >/dev/null 2>&1 || true

# 2. Inicia o servidor Microdot ultraleve em segundo plano (< 15 MB RAM)
python3 run_server.py 8000 &
SERVER_PID=$!

sleep 1.5

# 3. Abre o navegador leve em modo quiosque limpo (sem abas, sem barra de navegação)
# Flags de otimização de baixo consumo de RAM e GPU GMA 3150
KIOSK_URL="http://127.0.0.1:8000"

if command -v chromium >/dev/null 2>&1; then
  chromium --app="$KIOSK_URL" \
    --start-fullscreen \
    --kiosk \
    --incognito \
    --noerrdialogs \
    --disable-infobars \
    --overscroll-history-navigation=0 \
    --process-per-site \
    --disable-features=Translate,OptimizationHints,MediaRouter \
    --disable-background-networking \
    --disable-smooth-scrolling \
    --disable-gpu-vsync \
    --disk-cache-size=10485760
elif command -v chromium-browser >/dev/null 2>&1; then
  chromium-browser --app="$KIOSK_URL" \
    --start-fullscreen \
    --kiosk \
    --incognito \
    --noerrdialogs \
    --disable-infobars \
    --overscroll-history-navigation=0 \
    --process-per-site \
    --disable-features=Translate,OptimizationHints \
    --disable-background-networking \
    --disk-cache-size=10485760
elif command -v firefox-esr >/dev/null 2>&1; then
  firefox-esr --kiosk "$KIOSK_URL"
elif command -v midori >/dev/null 2>&1; then
  midori -e Fullscreen -a "$KIOSK_URL"
fi

# 4. Encerra o backend ao sair do quiosque
kill $SERVER_PID >/dev/null 2>&1 || true
