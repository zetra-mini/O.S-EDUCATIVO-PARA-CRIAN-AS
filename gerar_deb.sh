#!/usr/bin/env bash
# ==============================================================================
# Gerador Local de Pacote .deb — JARVIS Kids OS v3.7.0
# Compatível com antiX Linux, Debian 11/12, Ubuntu e Raspberry Pi OS
# ==============================================================================

set -e

VERSION="${1:-3.7.0}"
ARCH="all"
DEB_DIR="jarvis-kids-os_${VERSION}_${ARCH}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo "📦 Construindo pacote Debian Kiosk: jarvis-kids-os_${VERSION}.deb"
echo "=========================================================="

cd "$ROOT_DIR"
rm -rf "$DEB_DIR" "jarvis-kids-os_${VERSION}.deb"

mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/opt/jarvis-kids-os"
mkdir -p "${DEB_DIR}/usr/bin"
mkdir -p "${DEB_DIR}/usr/share/applications"

# Copia os arquivos do sistema
cp -r ./* "${DEB_DIR}/opt/jarvis-kids-os/" 2>/dev/null || true

# Limpeza de pastas desnecessárias no pacote
rm -rf "${DEB_DIR}/opt/jarvis-kids-os/${DEB_DIR}" \
       "${DEB_DIR}/opt/jarvis-kids-os/node_modules" \
       "${DEB_DIR}/opt/jarvis-kids-os/.git" \
       "${DEB_DIR}/opt/jarvis-kids-os/.cache" \
       "${DEB_DIR}/opt/jarvis-kids-os/__pycache__" \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.deb \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.tar.gz \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.zip \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.apk 2>/dev/null || true

# 1. Script executável global /usr/bin/jarvis-kids
cat << 'EOF' > "${DEB_DIR}/usr/bin/jarvis-kids"
#!/bin/sh
if [ -f /opt/jarvis-kids-os/iniciar_web_kiosk.sh ]; then
  exec /opt/jarvis-kids-os/iniciar_web_kiosk.sh "$@"
elif [ -f /opt/jarvis-kids-os/iniciar_jarvis_linux.sh ]; then
  exec /opt/jarvis-kids-os/iniciar_jarvis_linux.sh "$@"
else
  exec python3 /opt/jarvis-kids-os/run_server.py 8000 "$@"
fi
EOF
chmod +x "${DEB_DIR}/usr/bin/jarvis-kids"

# 2. Lançador .desktop do sistema
cat << 'EOF' > "${DEB_DIR}/usr/share/applications/jarvis-kids.desktop"
[Desktop Entry]
Name=JARVIS Kids OS
Comment=Sistema Operacional Educativo Inteligente para Crianças
Exec=/usr/bin/jarvis-kids
Icon=/opt/jarvis-kids-os/static/icons/icon-192.png
Terminal=false
Type=Application
Categories=Education;KidsGame;
EOF

# 3. Metadados de controle DEBIAN
cat << EOF > "${DEB_DIR}/DEBIAN/control"
Package: jarvis-kids-os
Version: ${VERSION}
Section: education
Priority: optional
Architecture: ${ARCH}
Depends: python3, python3-pip, chromium-browser | chromium | firefox-esr | firefox
Maintainer: Equipe Jarvis Kids OS <contato@jarvis-kids.local>
Description: Sistema Operacional Educativo Inteligente para Criancas (Stark Edge AI)
 O JARVIS Kids OS transforma netbooks modestos e desktops comuns em uma
 estacao educativa completa e segura, com IA afetuosa, controle dos pais e jogos.
EOF

# 4. Script postinst
cat << 'EOF' > "${DEB_DIR}/DEBIAN/postinst"
#!/bin/sh
set -e
chmod +x /usr/bin/jarvis-kids 2>/dev/null || true
chmod +x /opt/jarvis-kids-os/*.sh 2>/dev/null || true
python3 -m pip install --break-system-packages microdot edge-tts 2>/dev/null || python3 -m pip install microdot edge-tts 2>/dev/null || true
echo "✅ JARVIS Kids OS v3.7.0 instalado com sucesso em /opt/jarvis-kids-os!"
exit 0
EOF
chmod +x "${DEB_DIR}/DEBIAN/postinst"

# 5. Constrói o pacote .deb se dpkg-deb estiver disponível
if command -v dpkg-deb >/dev/null 2>&1; then
  dpkg-deb --build "${DEB_DIR}"
  mv "${DEB_DIR}.deb" "jarvis-kids-os_${VERSION}.deb"
  rm -rf "${DEB_DIR}"
  echo "✅ Pacote gerado com sucesso: jarvis-kids-os_${VERSION}.deb"
else
  echo "⚠️ Ferramenta 'dpkg-deb' não encontrada. Estrutura pronta em ${DEB_DIR}/"
fi
