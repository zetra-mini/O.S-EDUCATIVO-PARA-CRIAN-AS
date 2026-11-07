#!/usr/bin/env bash
# ==============================================================================
# JARVIS Kids OS - Instalador Dedicado para Linux Kiosk (Hardware Intel Atom N450)
# Desenvolvido especificamente para hardware com tela 1024x600, GMA 3150 e 1GB/2GB RAM.
# Instala SOMENTE os componentes do SO Kiosk leve (sem ambiente de desktop pesado).
# ==============================================================================

set -e

echo "=========================================================="
echo "🚀 INSTALADOR DO JARVIS KIDS O.S. (MODO KIOSK DEDICADO)"
echo "Alvo: Netbooks / PCs Educativos (Resolução: 1024x600)"
echo "=========================================================="

if [ "$EUID" -ne 0 ]; then
  echo "❌ Por favor, execute este instalador como root (sudo ./install_linux_os.sh)"
  exit 1
fi

INSTALL_DIR="/opt/jarvis-kids-os"
APP_USER="jarvis"

echo "📦 1. Atualizando pacotes e instalando dependências mínimas do SO..."
apt-get update -y
apt-get install -y --no-install-recommends \
  python3 \
  python3-pip \
  python3-venv \
  xorg \
  openbox \
  chromium-browser \
  alsa-utils \
  pulseaudio \
  unclutter \
  curl \
  git

echo "👤 2. Criando usuário de sistema '$APP_USER'..."
if ! id "$APP_USER" &>/dev/null; then
  useradd -m -s /bin/bash -G audio,video,input "$APP_USER"
  passwd -d "$APP_USER" # Sem senha para auto-login kiosk
fi

echo "📂 3. Instalando arquivos do Jarvis Kids OS em $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r ./* "$INSTALL_DIR/" || true
chown -R "$APP_USER:$APP_USER" "$INSTALL_DIR"

echo "🐍 4. Configurando ambiente Python ultraleve..."
cd "$INSTALL_DIR"
python3 -m pip install --break-system-packages microdot edge-tts || \
python3 -m pip install microdot edge-tts || true

echo "⚙️ 5. Configurando serviço de sistema Systemd (jarvis-kids.service)..."
cat << 'EOF' > /etc/systemd/system/jarvis-kids.service
[Unit]
Description=JARVIS Kids OS Backend Ultraleve (Microdot)
After=network.target sound.target

[Service]
Type=simple
User=jarvis
WorkingDirectory=/opt/jarvis-kids-os
ExecStart=/usr/bin/python3 /opt/jarvis-kids-os/run_server.py 8000
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1
Environment=JARVIS_PORT=8000

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable jarvis-kids.service

echo "🖥️ 6. Configurando inicialização Kiosk em X11 (1024x600)..."
mkdir -p /home/"$APP_USER"/.config/openbox
cat << 'EOF' > /home/"$APP_USER"/.config/openbox/autostart
# Esconde o cursor do mouse após 4 segundos de inatividade
unclutter -idle 4 -root &

# Força resolução 1024x600 caso o driver de vídeo suporte xrandr
xrandr --output default --mode 1024x600 2>/dev/null || true

# Aguarda o backend subir
sleep 2

# Inicia o Chromium em modo Kiosk seguro (sem barras, sem atalhos perigosos)
chromium-browser \
  --kiosk \
  --noerrdialogs \
  --disable-infobars \
  --no-first-run \
  --fast \
  --fast-start \
  --disable-translate \
  --disable-features=Translate \
  --disable-pinch \
  --overscroll-history-navigation=0 \
  --autoplay-policy=no-user-gesture-required \
  --window-size=1024,600 \
  --window-position=0,0 \
  "http://127.0.0.1:8000" &
EOF

chown -R "$APP_USER:$APP_USER" /home/"$APP_USER"/.config

echo "🔒 7. Bloqueando atalhos de saída no Openbox..."
cat << 'EOF' > /home/"$APP_USER"/.config/openbox/rc.xml
<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <keyboard>
    <!-- Desativa Alt+F4 e atalhos de fechar janela para a criança -->
  </keyboard>
</openbox_config>
EOF
chown -R "$APP_USER:$APP_USER" /home/"$APP_USER"/.config

echo "🔊 8. Ajustando volume ALSA para 85%..."
amixer set Master 85% unmute 2>/dev/null || true
amixer set PCM 85% unmute 2>/dev/null || true

echo "=========================================================="
echo "✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "O Jarvis Kids OS iniciará automaticamente no boot do Linux."
echo "Para testar agora: systemctl start jarvis-kids"
echo "=========================================================="
