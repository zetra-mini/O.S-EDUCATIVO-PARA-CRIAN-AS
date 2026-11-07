#!/usr/bin/env bash
# Inicia o Jarvis Kids OS no Desktop Linux
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🚀 INICIANDO JARVIS KIDS O.S. (LINUX DESKTOP)"
echo "=========================================================="

python3 deploy/desktop_app/jarvis_desktop.py
