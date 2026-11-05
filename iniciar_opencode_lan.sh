#!/usr/bin/env bash
# ==============================================================================
# J.A.R.V.I.S. Kids OS — Iniciar Servidor OpenCode para Rede Local (LAN / Netbook)
# ==============================================================================
# Execute este script no seu PC principal para servir o OpenCode para o Netbook,
# ou execute no próprio netbook com AntiX Linux.
# ==============================================================================

PORT=4096
echo "🚀 Iniciando Servidor OpenCode para o J.A.R.V.I.S. Kids OS na porta ${PORT}..."

if ! command -v opencode &> /dev/null; then
    echo "⚠️ OpenCode CLI não encontrado! Instalando globalmente via npm..."
    npm install -g --allow-scripts=opencode-ai opencode-ai
fi

echo "✅ OpenCode disponível: $(opencode --version)"
echo "🌐 Conecte o Netbook inserindo o endereço deste computador no HUD dos Pais:"
echo "   http://$(hostname -I | awk '{print $1}'):${PORT}"
echo ""
echo "Iniciando serviço..."
opencode serve --port ${PORT}
