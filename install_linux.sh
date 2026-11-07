#!/usr/bin/env bash
# ==============================================================================
# 🚀 INSTALADOR AUTOMÁTICO UNIVERSAL — J.A.R.V.I.S. KIDS OS
# Compatível com: antiX Linux (32/64 bits), Debian, Ubuntu, Linux Mint, Raspberry Pi OS
# Otimizado para Hardware Modesto: Intel Atom, AMD C-Series, Celeron, 1GB a 2GB RAM
# ==============================================================================

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}   🚀 INSTALAÇÃO AUTOMÁTICA DO J.A.R.V.I.S. KIDS OS (STARK SYSTEM) ${NC}"
echo -e "${CYAN}==================================================================${NC}"
echo -e "Sistema Educativo, Companheiro Emocional e Assistente de Estudos"
echo -e "Desenvolvido com Engenharia de Alta Eficiência para Hardware Leve\n"

# Verifica se o script está sendo rodado como usuário normal (não diretamente como root)
if [ "$EUID" -eq 0 ]; then
  echo -e "${RED}[!] Atenção: Execute este script com o usuário comum do sistema (ex: a criança ou pai).${NC}"
  echo -e "    O script solicitará privilégios 'sudo' apenas quando estritamente necessário."
  exit 1
fi

APP_DIR="$HOME/jarvis-kids-os"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Se não estiver no diretório final, copia os arquivos
if [ "$SCRIPT_DIR" != "$APP_DIR" ]; then
  echo -e "${YELLOW}[1/6] Configurando pasta do sistema em ${APP_DIR}...${NC}"
  mkdir -p "$APP_DIR"
  cp -r "$SCRIPT_DIR/"* "$APP_DIR/"
  cd "$APP_DIR"
else
  echo -e "${YELLOW}[1/6] Pasta do sistema localizada em ${APP_DIR}.${NC}"
  cd "$APP_DIR"
fi

# Detecta gerenciador de pacotes
echo -e "${YELLOW}[2/6] Atualizando repositórios e instalando dependências essenciais do Linux...${NC}"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -qq || true
  sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-tk \
    alsa-utils \
    espeak-ng \
    mpg123 \
    x11-xserver-utils \
    unclutter \
    chromium-browser || sudo apt-get install -y chromium || sudo apt-get install -y firefox-esr || true
elif command -v pacman >/dev/null 2>&1; then
  sudo pacman -Sy --noconfirm python python-pip alsa-utils espeak-ng mpg123 chromium || true
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf install -y python3 python3-pip alsa-utils espeak-ng mpg123 chromium || true
fi

# Instala dependências Python (prioriza venv ou pip local)
echo -e "${YELLOW}[3/6] Instalando dependências de inteligência e servidores em Python...${NC}"
if [ ! -d "$APP_DIR/venv" ]; then
  python3 -m venv "$APP_DIR/venv" 2>/dev/null || true
fi

if [ -f "$APP_DIR/venv/bin/pip" ]; then
  "$APP_DIR/venv/bin/pip" install --upgrade pip --no-cache-dir
  "$APP_DIR/venv/bin/pip" install microdot bottle edge-tts google-genai requests --no-cache-dir || true
else
  python3 -m pip install --user --break-system-packages microdot bottle edge-tts google-genai requests --no-cache-dir 2>/dev/null || \
  python3 -m pip install --user microdot bottle edge-tts google-genai requests --no-cache-dir || true
fi

# Otimização de ZRAM e Memória RAM para netbooks
echo -e "${YELLOW}[4/6] Otimizando consumo de memória e latência do sistema operacional...${NC}"
if [ -f /etc/default/zramswap ]; then
  sudo sed -i 's/^#*ALGO=.*/ALGO=lz4/' /etc/default/zramswap || true
  sudo sed -i 's/^#*PERCENT=.*/PERCENT=50/' /etc/default/zramswap || true
  sudo service zramswap restart 2>/dev/null || true
fi
if [ -d /etc/sysctl.d ]; then
  echo "vm.swappiness=15" | sudo tee /etc/sysctl.d/99-jarvis-kids.conf >/dev/null 2>&1 || true
fi

# Cria script de inicialização do quiosque
echo -e "${YELLOW}[5/6] Gerando scripts de inicialização rápida em modo Quiosque Kiosk...${NC}"
cat > "$APP_DIR/iniciar_jarvis.sh" << 'EOF'
#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Determina executável python
if [ -f "$DIR/venv/bin/python" ]; then
  PYTHON="$DIR/venv/bin/python"
else
  PYTHON="python3"
fi

# Ativa som
amixer set Master 75% unmute >/dev/null 2>&1 || true

# Inicia servidor web em background se ainda não estiver ativo
if ! pgrep -f "run_server.py 8000" >/dev/null; then
  $PYTHON run_server.py 8000 >/dev/null 2>&1 &
  sleep 2
fi

# Oculta cursor do mouse ocioso após 4 segundos (opcional)
unclutter -idle 4 -root >/dev/null 2>&1 &

# Abre navegador em modo quiosque tela cheia
URL="http://127.0.0.1:8000"

if command -v chromium-browser >/dev/null 2>&1; then
  chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 --disable-translate --autoplay-policy=no-user-gesture-required "$URL"
elif command -v chromium >/dev/null 2>&1; then
  chromium --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 --disable-translate --autoplay-policy=no-user-gesture-required "$URL"
elif command -v firefox-esr >/dev/null 2>&1; then
  firefox-esr --kiosk "$URL"
elif command -v firefox >/dev/null 2>&1; then
  firefox --kiosk "$URL"
else
  $PYTHON jarvis_os.py --kiosk
fi
EOF
chmod +x "$APP_DIR/iniciar_jarvis.sh"
chmod +x "$APP_DIR/run_server.py"

# Configuração de Autostart e Atalhos na Área de Trabalho
echo -e "${YELLOW}[6/6] Criando atalhos na Área de Trabalho e autostart no boot...${NC}"

# 1. antiX Linux (~/.desktop-session/startup)
if [ -d "$HOME/.desktop-session" ]; then
  if ! grep -q "iniciar_jarvis.sh" "$HOME/.desktop-session/startup" 2>/dev/null; then
    cat >> "$HOME/.desktop-session/startup" << EOF

# --- JARVIS KIDS OS AUTOSTART ---
bash "$APP_DIR/iniciar_jarvis.sh" &
EOF
  fi
fi

# 2. XDG Autostart padrão (Debian / Ubuntu / Raspberry Pi OS / Mint)
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/jarvis-kids-os.desktop" << EOF
[Desktop Entry]
Type=Application
Name=JARVIS Kids OS
Comment=Central Educativa Infantil do Homem de Ferro
Exec=bash $APP_DIR/iniciar_jarvis.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

# 3. Atalhos na Área de Trabalho
for DESK in "$HOME/Desktop" "$HOME/Área de Trabalho"; do
  if [ -d "$DESK" ]; then
    cat > "$DESK/JARVIS-Kids-OS.desktop" << EOF
[Desktop Entry]
Type=Application
Name=JARVIS Kids OS
Comment=Iniciar o JARVIS Educativo
Exec=bash $APP_DIR/iniciar_jarvis.sh
Icon=applications-games
Terminal=false
EOF
    chmod +x "$DESK/JARVIS-Kids-OS.desktop" 2>/dev/null || true
  fi
done

# Permissões finais
chmod +x "$APP_DIR"/*.sh 2>/dev/null || true

echo -e "\n${GREEN}==================================================================${NC}"
echo -e "${GREEN}  ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO! O JARVIS KIDS OS ESTÁ PRONTO!${NC}"
echo -e "${GREEN}==================================================================${NC}"
echo -e "👉 Para iniciar agora mesmo, execute:"
echo -e "   ${CYAN}bash $APP_DIR/iniciar_jarvis.sh${NC}\n"
echo -e "👉 Painel Administrativo dos Pais:"
echo -e "   ${CYAN}http://127.0.0.1:8000/pais${NC} (ou pelo IP da sua rede Wi-Fi)\n"
echo -e "O sistema iniciará automaticamente sempre que o computador for ligado!"
