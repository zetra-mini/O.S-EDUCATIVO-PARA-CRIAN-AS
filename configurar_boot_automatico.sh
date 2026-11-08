#!/usr/bin/env bash
# ==============================================================================
# J.A.R.V.I.S. Kids OS — Instalador de Persistência e Boot Automático (antiX / Debian)
# ==============================================================================
# Configura Auto-Login, inicialização de serviços, watchdog e modo quiosque contínuo.
# ==============================================================================

set -e

if [ "$EUID" -ne 0 ]; then
    echo "⚠️ Por favor, execute como root: sudo bash configurar_boot_automatico.sh"
    exit 1
fi

REAL_USER="${SUDO_USER:-$USER}"
USER_HOME=$(eval echo "~$REAL_USER")
PROJ_DIR="$USER_HOME/O.S-EDUCATIVO-PARA-CRIAN-AS"
if [ ! -d "$PROJ_DIR" ]; then
    PROJ_DIR="$USER_HOME/jarvis-kids-os"
fi

echo "🔧 Configurando Jarvis Kids OS para o usuário: $REAL_USER em $PROJ_DIR"

# 1. Instalação de utilitários essenciais de hardware (áudio ALSA, vídeo, webcam e ferramentas)
echo "📦 Instalando pacotes de suporte a hardware (áudio, webcam, zram, firewall, redshift)..."
apt-get update -qq || true
apt-get install -y --no-install-recommends \
    alsa-utils v4l-utils curl git python3-pip \
    xdotool unclutter x11-xserver-utils zram-tools ufw redshift || true

# 1.1 Otimização de Memória RAM com ZRAM (2GB rendem como 3GB)
echo "⚡ Configurando compressão de memória ZRAM (50% RAM)..."
mkdir -p /etc/default
cat << 'EOF_ZRAM' > /etc/default/zramswap
ALGO=zstd
PERCENT=50
PRIORITY=100
EOF_ZRAM
service zramswap restart > /dev/null 2>&1 || systemctl restart zramswap > /dev/null 2>&1 || true

# 1.2 Otimização de VRAM da GPU Intel GMA 3150 (SNA + TearFree)
echo "🎮 Configurando aceleração por hardware Intel GMA 3150 (SNA + TearFree)..."
mkdir -p /etc/X11/xorg.conf.d
cat << 'EOF_XORG' > /etc/X11/xorg.conf.d/20-intel.conf
Section "Device"
    Identifier "Intel Graphics"
    Driver "intel"
    Option "AccelMethod" "sna"
    Option "TearFree" "true"
EndSection
EOF_XORG

# 1.3 Blindagem de Rede com UFW (Firewall)
echo "🛡️ Configurando Firewall UFW (bloqueia entrada não autorizada)..."
ufw default deny incoming > /dev/null 2>&1 || true
ufw default allow outgoing > /dev/null 2>&1 || true
ufw allow from 127.0.0.1 > /dev/null 2>&1 || true
ufw allow 8000/tcp comment 'Jarvis Kids OS Kiosk' > /dev/null 2>&1 || true
ufw --force enable > /dev/null 2>&1 || true

# 1.4 Remoção e Desativação Total de Bluetooth (Economia de Bateria e Processos)
echo "🔋 Desativando Bluetooth para poupar bateria e ciclos de CPU..."
rfkill block bluetooth > /dev/null 2>&1 || true
systemctl disable bluetooth > /dev/null 2>&1 || true
service bluetooth stop > /dev/null 2>&1 || true

# 1.5 Agendamento do Filtro de Luz Noturna Circadiano (Redshift às 19h / 07h)
echo "🌙 Configurando filtro de luz noturna circadiano (3500K às 19h)..."
mkdir -p /etc/cron.d
cat << 'EOF_CRON' > /etc/cron.d/jarvis_filtro_luz
0 19 * * * root DISPLAY=:0 redshift -O 3500 > /dev/null 2>&1
0 7 * * * root DISPLAY=:0 redshift -x > /dev/null 2>&1
EOF_CRON
chmod 644 /etc/cron.d/jarvis_filtro_luz

# 2. Configuração de Auto-Login no LightDM ou SLiM
if [ -f "/etc/lightdm/lightdm.conf" ]; then
    echo "🔑 Configurando Auto-Login no LightDM..."
    sed -i "s/^#\?autologin-user=.*/autologin-user=$REAL_USER/" /etc/lightdm/lightdm.conf
    sed -i "s/^#\?autologin-user-timeout=.*/autologin-user-timeout=0/" /etc/lightdm/lightdm.conf
fi

if [ -f "/etc/slim.conf" ]; then
    echo "🔑 Configurando Auto-Login no SLiM..."
    sed -i "s/^#\?default_user.*/default_user $REAL_USER/" /etc/slim.conf
    sed -i "s/^#\?auto_login.*/auto_login yes/" /etc/slim.conf
fi

# 3. Trava de volume seguro ALSA a 75%
amixer set Master 75% unmute > /dev/null 2>&1 || true
alsactl store > /dev/null 2>&1 || true

# 4. Configuração do Autostart no Desktop (IceWM / Openbox)
AUTOSTART_DIR="$USER_HOME/.config/openbox"
mkdir -p "$AUTOSTART_DIR"
chown -R "$REAL_USER:$REAL_USER" "$USER_HOME/.config"

cat << 'EOF' > "$AUTOSTART_DIR/autostart"
#!/bin/bash
# Desativa protetor de tela e desligamento do visor
xset s off
xset -dpms
xset s noblank

# Oculta o cursor após 4 segundos de inatividade
unclutter -idle 4 -root &

# Aguarda o servidor estar online na porta 8000
until curl -s http://localhost:8000/api/state > /dev/null 2>&1; do
    sleep 1
done

# Laço de persistência do Navegador Quiosque: se fechar, reabre sozinho
while true; do
    if command -v midori &> /dev/null; then
        midori -e Fullscreen -a http://localhost:8000
    elif command -v falkon &> /dev/null; then
        falkon -f http://localhost:8000
    elif command -v chromium &> /dev/null; then
        chromium --app=http://localhost:8000 --start-fullscreen --kiosk --noerrdialogs --disable-infobars
    else
        firefox --kiosk http://localhost:8000
    fi
    sleep 2
done &
EOF

chmod +x "$AUTOSTART_DIR/autostart"
chown "$REAL_USER:$REAL_USER" "$AUTOSTART_DIR/autostart"

# 5. Adiciona inicialização do serviço no /etc/rc.local se existir
if [ -f "/etc/rc.local" ]; then
    if ! grep -q "iniciar_servicos.sh" /etc/rc.local; then
        sed -i -e '$i \
# Inicia servicos Jarvis Kids OS em segundo plano \
su - '"$REAL_USER"' -c "bash '"$PROJ_DIR"'/iniciar_servicos.sh > /dev/null 2>&1 &" \
' /etc/rc.local
    fi
fi

echo "=============================================================================="
echo "✅ Persistência e Boot Automático configurados com sucesso!"
echo "   Ao ligar o netbook, o Jarvis iniciará sozinho em tela cheia na porta 8000."
echo "=============================================================================="
