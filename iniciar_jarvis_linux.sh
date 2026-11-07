#!/usr/bin/env bash
# ==========================================================
# Inicia o Jarvis Kids OS no Desktop Linux / Netbook
# ==========================================================
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🚀 INICIANDO JARVIS KIDS O.S. (LINUX DESKTOP / NETBOOK)"
echo "=========================================================="

if [ -f "deploy/desktop_app/jarvis_desktop.py" ]; then
    python3 deploy/desktop_app/jarvis_desktop.py
elif [ -f "jarvis_desktop.py" ]; then
    python3 jarvis_desktop.py
elif [ -f "iniciar_web_kiosk.sh" ]; then
    bash iniciar_web_kiosk.sh
else
    python3 run_server.py 8000
fi
