#!/usr/bin/env bash
# ==============================================================================
# INICIADOR DO MODO WEB QUIOSQUE — JARVIS KIDS OS
# Otimizado para Acer Aspire One 532 (1024x600, 1 GB RAM, Intel Atom N450 / antiX)
# Microdot Server Ultraleve (< 20 MB RAM) + Chromium/Firefox Kiosk Baixo Consumo
# ==============================================================================

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
cd "$DIR"

PORT="${1:-8000}"

# Determina Python (prioriza venv do projeto) e reduz sobrecarga de allocator em 1 GB RAM
if [ -f "$DIR/venv/bin/python" ]; then
  PYTHON="$DIR/venv/bin/python"
else
  PYTHON="python3"
fi
export PYTHONOPTIMIZE=1
export MALLOC_ARENA_MAX=2

# 1. Inicia o servidor se não estiver ativo
if ! pgrep -f "run_server.py.*$PORT" >/dev/null 2>&1 && ! pgrep -f "run_server.py" >/dev/null 2>&1; then
  nohup "$PYTHON" "$DIR/run_server.py" "$PORT" > "$DIR/jarvis_server.log" 2>&1 &
  SERVER_PID=$!
  sleep 1.8
else
  SERVER_PID=$(pgrep -f "run_server.py" | head -n1)
fi

KIOSK_URL="http://127.0.0.1:${PORT}"

# Se estiver em VPS / ambiente sem interface gráfica, mantém o servidor ativo e sai
if [ -z "$DISPLAY" ]; then
  echo "J.A.R.V.I.S. Kids OS ativo em http://127.0.0.1:${PORT}"
  echo "Ambiente Headless detectado (sem display gráfico)."
  exit 0
fi

CHROMIUM_FLAGS=(
  --app="$KIOSK_URL"
  --start-fullscreen
  --kiosk
  --incognito
  --noerrdialogs
  --disable-infobars
  --overscroll-history-navigation=0
  --disable-gpu
  --disable-dev-shm-usage
  --renderer-process-limit=1
  --process-per-site
  --js-flags="--max-old-space-size=192"
  --disable-extensions
  --disable-features=Translate,OptimizationHints,MediaRouter
  --disable-background-networking
  --disable-smooth-scrolling
  --disable-gpu-vsync
  --disk-cache-size=10485760
)

# 2. Abre o navegador leve em modo quiosque limpo (otimizado para 1 GB RAM)
if command -v chromium >/dev/null 2>&1; then
  chromium "${CHROMIUM_FLAGS[@]}"
elif command -v chromium-browser >/dev/null 2>&1; then
  chromium-browser "${CHROMIUM_FLAGS[@]}"
elif command -v firefox-esr >/dev/null 2>&1; then
  firefox-esr --kiosk "$KIOSK_URL"
elif command -v firefox >/dev/null 2>&1; then
  firefox --kiosk "$KIOSK_URL"
elif command -v midori >/dev/null 2>&1; then
  midori -e Fullscreen -a "$KIOSK_URL"
fi
