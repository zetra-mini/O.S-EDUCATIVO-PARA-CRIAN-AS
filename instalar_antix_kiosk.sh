#!/usr/bin/env bash
# ==============================================================================
# INSTALADOR AUTOMÁTICO — JARVIS KIDS OS (MODO QUIOSQUE INFANTIL)
# Otimizado especificamente para: Acer Aspire One 532h (Atom N450 / GMA 3150 / 1GB-2GB RAM / 1024x600)
# Sistemas recomendados: antiX Linux (32-bit ou 64-bit) ou Q4OS / Debian 12
# ==============================================================================

set -e

echo "============================================================"
echo "  INICIANDO CONFIGURAÇÃO DO JARVIS KIDS OS (ASPIRE ONE 532)"
echo "============================================================"

if [ "$EUID" -eq 0 ]; then
  echo "[!] Execute este script com o usuário normal da criança (não como root)."
  echo "    O script pedirá 'sudo' apenas quando necessário."
  exit 1
fi

APP_DIR="$HOME/jarvis-kids-os"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/6] Atualizando repositórios e instalando pacotes leves + ferramentas educativas..."
sudo apt-get update
sudo apt-get install -y \
  python3 \
  python3-tk \
  espeak-ng \
  alsa-utils \
  x11-xserver-utils \
  gcompris-qt \
  tuxpaint \
  gamine \
  zram-tools || true

echo "[2/6] Copiando arquivos do JARVIS Kids OS para $APP_DIR ..."
mkdir -p "$APP_DIR"
if [ "$SCRIPT_DIR" != "$APP_DIR" ]; then
  cp -r "$SCRIPT_DIR/"* "$APP_DIR/"
fi
chmod +x "$APP_DIR/jarvis_os.py"

echo "[3/6] Otimizando memória RAM (ZRAM + Swappiness) para o Intel Atom N450..."
if [ -f /etc/default/zramswap ]; then
  sudo sed -i 's/^#*ALGO=.*/ALGO=lz4/' /etc/default/zramswap || true
  sudo sed -i 's/^#*PERCENT=.*/PERCENT=50/' /etc/default/zramswap || true
  sudo service zramswap restart || true
fi
echo "vm.swappiness=15" | sudo tee /etc/sysctl.d/99-jarvis-kids.conf >/dev/null

echo "[4/6] Configurando GCompris para GPU Intel GMA 3150 (Renderização por Software + PT-BR + 4 Anos)..."
mkdir -p "$HOME/.config/gcompris"
cat > "$HOME/.config/gcompris/gcompris-qt.conf" << 'EOF'
[General]
enableAutomaticDownloads=false
fullscreen=true
locale=pt_BR.UTF-8
renderer=software
virtualKeyboard=false
filterLevelMin=1
filterLevelMax=2
isAudioVoicesEnabled=true
isAudioEffectsEnabled=true
EOF

echo "[5/6] Configurando Tux Paint para tela 1024x600 sem travas para crianças de 4 anos..."
cat > "$HOME/.tuxpaintrc" << 'EOF'
fullscreen=yes
windowsize=1024x600
simpleshapes=yes
uppercase=yes
noprint=yes
nolockfile=yes
quit=no
lang=brazilian-portuguese
EOF

echo "[6/6] Configurando inicialização automática em Modo Quiosque (antiX / Desktop Linux)..."
# 1. Para antiX Linux (usa ~/.desktop-session/startup)
if [ -d "$HOME/.desktop-session" ]; then
  if ! grep -q "jarvis_os.py" "$HOME/.desktop-session/startup" 2>/dev/null; then
    cat >> "$HOME/.desktop-session/startup" << EOF

# --- JARVIS KIDS OS AUTOSTART ---
xset s off -dpms &
amixer set Master 85% unmute >/dev/null 2>&1 &
python3 "$APP_DIR/jarvis_os.py" --kiosk &
EOF
  fi
fi

# 2. Padrão XDG Autostart (Q4OS, LXQt, XFCE, Debian)
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/jarvis-kids-os.desktop" << EOF
[Desktop Entry]
Type=Application
Name=JARVIS Kids OS
Comment=Central Educativa Infantil Estilo Homem de Ferro
Exec=python3 $APP_DIR/jarvis_os.py --kiosk
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

# 3. Atalho na Área de Trabalho
mkdir -p "$HOME/Desktop" "$HOME/Área de Trabalho" 2>/dev/null || true
for DESK in "$HOME/Desktop" "$HOME/Área de Trabalho"; do
  if [ -d "$DESK" ]; then
    cat > "$DESK/JARVIS-Kids.desktop" << EOF
[Desktop Entry]
Type=Application
Name=JARVIS Kids OS
Exec=python3 $APP_DIR/jarvis_os.py --kiosk
Icon=applications-games
Terminal=false
EOF
    chmod +x "$DESK/JARVIS-Kids.desktop"
  fi
done

echo ""
echo "============================================================"
echo "  CONCLUÍDO! O JARVIS KIDS OS ESTÁ PRONTO NO NETBOOK!"
echo "  Para testar agora mesmo, digite:"
echo "    python3 $APP_DIR/jarvis_os.py --kiosk"
echo "  Ao reiniciar o Acer Aspire One 532, ele abrirá sozinho!"
echo "============================================================"
