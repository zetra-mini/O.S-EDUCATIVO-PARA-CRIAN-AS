#!/usr/bin/env bash
# ==============================================================================
# J.A.R.V.I.S. Kids OS — Atualização Remota em Um Clique via GitHub
# Executado em segundo plano de forma desanexada a partir do Painel dos Pais.
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "🔄 [JARVIS UPDATE] Iniciando processo de atualização remota..."
# Aguarda 2 segundos para o servidor responder à requisição HTTP do celular dos pais
sleep 2

# Puxa as atualizações do repositório remoto descartando conflitos locais de código
echo "📥 Baixando novidades do GitHub (git fetch & reset)..."
git fetch origin main || true
git reset --hard origin/main || true
chmod +x "$DIR/pkg" "$DIR"/*.sh 2>/dev/null || true

# Atualiza dependências leves respeitando venv ou PEP 668 (--break-system-packages)
if [ -f "requirements.txt" ]; then
    echo "📦 Checando dependências leves..."
    if [ -f "$DIR/venv/bin/pip" ]; then
        "$DIR/venv/bin/pip" install -r requirements.txt --no-cache-dir 2>/dev/null || true
    else
        python3 -m pip install --break-system-packages -r requirements.txt --no-cache-dir 2>/dev/null || \
        python3 -m pip install --user -r requirements.txt --no-cache-dir 2>/dev/null || true
    fi
fi

echo "🚀 Reiniciando servidor Jarvis Kids OS de forma resiliente..."
if [ -x "$DIR/pkg" ]; then
    "$DIR/pkg" stop >/dev/null 2>&1 || true
    "$DIR/pkg" start
else
    pkill -f "run_server.py" 2>/dev/null || true
    sleep 1
    PY_BIN="python3"
    [ -f "$DIR/venv/bin/python" ] && PY_BIN="$DIR/venv/bin/python"
    nohup "$PY_BIN" "$DIR/run_server.py" 8000 > "$DIR/jarvis_server.log" 2>&1 &
fi

# Opcional: Atualiza navegadores leves que não recarreguem automaticamente
pkill -f "midori|falkon" 2>/dev/null || true

echo "✅ Atualização concluída com sucesso!"
