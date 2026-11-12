#!/bin/bash
# ==============================================================================
# Script de Instalação e Otimização — Jarvis OS (Intel Atom N450 / 1GB-2GB RAM)
# Desenvolvido para antiX Linux, Debian e Ubuntu em netbooks (1024x600)
# Deve ser executado com privilégios de root (sudo bash instalar_otimizado.sh)
# ==============================================================================

set -e

echo "=========================================================="
echo "🚀 Iniciando deploy otimizado do Jarvis Kids OS..."
echo "=========================================================="

# Verificação de privilégios de root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Erro: Este script precisa ser executado como root (use: sudo bash instalar_otimizado.sh)"
  exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/jarvis-kids-os"
APP_USER="jarvis"
JARVIS_PORT="${JARVIS_PORT:-8000}"

# 1. Otimização de Kernel (ZRAM, Swappiness e VFS Cache)
echo "⚡ [1/7] Aplicando ajustes finos no Kernel para Intel Atom N450..."
cat <<EOF > /etc/sysctl.d/99-jarvis-otimizado.conf
vm.swappiness=80
vm.vfs_cache_pressure=50
EOF
sysctl -p /etc/sysctl.d/99-jarvis-otimizado.conf || sysctl -e -p /etc/sysctl.d/99-jarvis-otimizado.conf || true

# 2. Configuração do ZRAM e dependências do Quiosque
echo "📦 [2/7] Instalando e configurando ZRAM e unclutter..."
apt-get update && apt-get install -y zram-tools unclutter
if [ -f /etc/default/zramswap ]; then
  sed -i 's/^#*ALGO=.*/ALGO=lz4/' /etc/default/zramswap
  sed -i 's/^#*PERCENT=.*/PERCENT=50/' /etc/default/zramswap
  service zramswap restart || systemctl restart zramswap || true
fi

# 3. Otimização de I/O no disco (FSTAB)
echo "💾 [3/7] Reduzindo overhead de leitura no disco (noatime, nodiratime)..."
# Substitui relatime por noatime e nodiratime para poupar I/O no disco
if grep -q "relatime" /etc/fstab; then
  sed -i 's/relatime/noatime,nodiratime/g' /etc/fstab
fi

# 4. Injeção de Flags no script de Kiosk do repositório
echo "🖥️ [4/7] Otimizando renderização web no iniciar_web_kiosk.sh..."
KIOSK_SCRIPT="$PROJECT_DIR/iniciar_web_kiosk.sh"
if [ -f "$KIOSK_SCRIPT" ]; then
  # Injeta as flags de baixo consumo diretamente no script existente (porta 8000 oficial do Jarvis)
  sed -i 's/chromium-browser.*/chromium-browser --kiosk --disable-gpu --disable-dev-shm-usage --disable-background-networking --disable-extensions --js-flags="--max_old_space_size=256" --app=http:\/\/localhost:'"$JARVIS_PORT"' \&/g' "$KIOSK_SCRIPT"
  chmod +x "$KIOSK_SCRIPT"
fi

# 5. Configuração de Permissões Globais e Estrutura de Diretórios
echo "🔧 [5/7] Ajustando permissões dos scripts executáveis e diretórios..."
cd "$PROJECT_DIR"
chmod +x *.sh || true
if [ -d "deploy/linux_os_kiosk" ]; then
  chmod +x deploy/linux_os_kiosk/*.sh 2>/dev/null || true
fi

# Garante a existência do usuário e diretório de instalação para o serviço systemd
if ! id "$APP_USER" &>/dev/null; then
  useradd -m -s /bin/bash -G audio,video,input "$APP_USER" || true
  passwd -d "$APP_USER" 2>/dev/null || true
fi

mkdir -p "$INSTALL_DIR"
if [ "$PROJECT_DIR" != "$INSTALL_DIR" ]; then
  cp -ru "$PROJECT_DIR/"* "$INSTALL_DIR/" 2>/dev/null || cp -r "$PROJECT_DIR/"* "$INSTALL_DIR/" || true
fi
chown -R "$APP_USER:$APP_USER" "$INSTALL_DIR" || true

# 6. Instalação do Serviço do Sistema (Systemd com fallback SysVinit para antiX)
echo "⚙️ [6/7] Habilitando daemon principal do Jarvis Kids OS..."
if [ -f "deploy/linux_os_kiosk/jarvis-kids.service" ]; then
  cp deploy/linux_os_kiosk/jarvis-kids.service /etc/systemd/system/
fi

if command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
  systemctl daemon-reload
  systemctl enable jarvis-kids.service
  systemctl restart jarvis-kids.service || systemctl start jarvis-kids.service
else
  echo "ℹ️ Systemd não ativo (modo antiX/SysVinit). Configurando inicialização de segundo plano..."
  nohup su - "$APP_USER" -c "python3 $INSTALL_DIR/run_server.py $JARVIS_PORT" >/var/log/jarvis.log 2>&1 &
fi

# 7. Prevenção de Vazamento de Memória (Manutenção Automática)
echo "🧹 [7/7] Criando rotina de limpeza de cache na madrugada (03h00)..."
if command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
  CRON_JOB="0 3 * * * systemctl restart jarvis-kids.service && echo 3 > /proc/sys/vm/drop_caches"
else
  CRON_JOB="0 3 * * * pkill -f run_server.py; su - $APP_USER -c 'python3 $INSTALL_DIR/run_server.py $JARVIS_PORT' >/dev/null 2>&1 & echo 3 > /proc/sys/vm/drop_caches"
fi
(crontab -l 2>/dev/null | grep -v "jarvis-kids\|run_server.py"; echo "$CRON_JOB") | crontab -

echo ""
echo "=========================================================="
echo "✅ Deploy otimizado concluído com sucesso!"
echo "   Porta ativa: http://localhost:$JARVIS_PORT"
echo "   Diretório: $INSTALL_DIR"
echo "=========================================================="
