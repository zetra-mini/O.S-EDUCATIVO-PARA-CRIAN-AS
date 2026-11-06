#!/usr/bin/env bash
# ==============================================================================
# J.A.R.V.I.S. Kids OS — Inicialização e Supervisão do Servidor (Watchdog Loop)
# ==============================================================================
# Inicia o backend Python e o Cloudflare Tunnel em segundo plano com auto-restart.
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# 1. Inicia o túnel do Cloudflare para acesso remoto seguro dos pais (se configurado)
if [ -n "$CLOUDFLARE_TUNNEL_TOKEN" ]; then
    echo "🌐 Iniciando Cloudflare Tunnel seguro para o Painel dos Pais..."
    cloudflared tunnel run --token "$CLOUDFLARE_TUNNEL_TOKEN" > /dev/null 2>&1 &
elif command -v cloudflared &> /dev/null && [ -f "$HOME/.cloudflared/config.yml" ]; then
    echo "🌐 Iniciando Cloudflare Tunnel configurado localmente..."
    cloudflared tunnel run > /dev/null 2>&1 &
fi

# 2. Laço de persistência do Servidor Jarvis Kids OS (Auto-Restart se cair)
echo "🛡️ Iniciando laço supervisor do Servidor Jarvis Kids OS..."
while true; do
    echo "🚀 [$(date '+%Y-%m-%d %H:%M:%S')] Subindo Servidor Jarvis (Microdot / Porta 8000)..."
    python3 run_server.py
    EXIT_CODE=$?
    echo "⚠️ Servidor encerrou com código $EXIT_CODE. Reiniciando em 3 segundos..."
    sleep 3
done
