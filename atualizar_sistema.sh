#!/usr/bin/env bash
# ==============================================================================
# J.A.R.V.I.S. Kids OS — Atualização Remota em Um Clique via GitHub
# ==============================================================================
# Executado em segundo plano de forma desanexada a partir do Painel dos Pais.
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "🔄 [JARVIS UPDATE] Iniciando processo de atualização remota..."
# Aguarda 2 segundos para o servidor responder à requisição HTTP do celular dos pais
sleep 2

# Puxa as atualizações do repositório remoto descartando conflitos locais
echo "📥 Baixando novidades do GitHub (git fetch & reset)..."
git fetch origin main || true
git reset --hard origin/main || true

# Atualiza dependências leves caso haja requirements.txt
if [ -f "requirements.txt" ]; then
    echo "📦 Checando dependências leves..."
    pip install -r requirements.txt --no-cache-dir || true
fi

echo "🚀 Reiniciando servidor Jarvis Kids OS..."
# Encerra o processo do servidor. O loop supervisor (watchdog) irá reabri-lo em 3s
pkill -f "run_server.py" || true

# Opcional: Atualiza a tela do navegador quiosque para recarregar as novidades
pkill -f "midori|falkon" || true

echo "✅ Atualização concluída com sucesso!"
