#!/usr/bin/env bash
# ==============================================================================
# Gerador Local de Pacote .deb — JARVIS Kids OS
# Compatível com antiX Linux, Debian 11/12, Ubuntu e Raspberry Pi OS
# Suporta blindagem opcional Counter-REA via Blind LLM Agents (--bla)
# ==============================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$ROOT_DIR/VERSION" ]; then
  DEFAULT_VER="$(cat "$ROOT_DIR/VERSION" | tr -d '[:space:]')"
else
  DEFAULT_VER="3.9.7"
fi

USE_BLA="${BLA_HARDEN:-0}"
BLA_INTENSITY="${BLA_INTENSITY:-balanced}"
VERSION="$DEFAULT_VER"

for arg in "$@"; do
  case "$arg" in
    --bla)
      USE_BLA="1"
      ;;
    --bankrupt)
      USE_BLA="1"
      BLA_INTENSITY="bankrupt"
      ;;
    *)
      VERSION="$arg"
      ;;
  esac
done

ARCH="all"
DEB_DIR="jarvis-kids-os_${VERSION}_${ARCH}"

echo "=========================================================="
echo "📦 Construindo pacote Debian Kiosk: jarvis-kids-os_${VERSION}.deb"
echo "=========================================================="

cd "$ROOT_DIR"
rm -rf "$DEB_DIR" "jarvis-kids-os_${VERSION}.deb"

mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/opt/jarvis-kids-os"
mkdir -p "${DEB_DIR}/usr/bin"
mkdir -p "${DEB_DIR}/usr/share/applications"

# Copia os arquivos do sistema (incluindo .blarc se blindagem for usada)
cp -r ./* "${DEB_DIR}/opt/jarvis-kids-os/" 2>/dev/null || true
[ -f ".blarc" ] && cp ".blarc" "${DEB_DIR}/opt/jarvis-kids-os/.blarc"

# Higiene estrita de release: remove segredos locais, bancos pessoais, caches e artefatos dev
rm -rf "${DEB_DIR}/opt/jarvis-kids-os/${DEB_DIR}" \
       "${DEB_DIR}/opt/jarvis-kids-os/node_modules" \
       "${DEB_DIR}/opt/jarvis-kids-os/venv" \
       "${DEB_DIR}/opt/jarvis-kids-os/.venv" \
       "${DEB_DIR}/opt/jarvis-kids-os/.git" \
       "${DEB_DIR}/opt/jarvis-kids-os/.cache" \
       "${DEB_DIR}/opt/jarvis-kids-os/.bla-hardened" \
       "${DEB_DIR}/opt/jarvis-kids-os/dist" \
       "${DEB_DIR}/opt/jarvis-kids-os/scratch" \
       "${DEB_DIR}/opt/jarvis-kids-os/tests" \
       "${DEB_DIR}/opt/jarvis-kids-os/__pycache__" \
       "${DEB_DIR}/opt/jarvis-kids-os/static/sounds/cache_tts" \
       "${DEB_DIR}/opt/jarvis-kids-os/config.json" \
       "${DEB_DIR}/opt/jarvis-kids-os/config_nuvem.json" \
       "${DEB_DIR}/opt/jarvis-kids-os/uso_diario.json" \
       "${DEB_DIR}/opt/jarvis-kids-os/.jarvis_master.key" \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.aes.key \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.db \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.db-wal \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.db-shm \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.log \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.deb \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.tar.gz \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.zip \
       "${DEB_DIR}/opt/jarvis-kids-os"/*.apk 2>/dev/null || true

# Opcional: aplica Blindagem Counter-REA (Blind LLM Agents) no staging antes de empacotar
if [ "$USE_BLA" = "1" ]; then
  echo "🛡️ Aplicando Blindagem Counter-REA (BLA: ${BLA_INTENSITY}) no pacote .deb..."
  python3 "$ROOT_DIR/scripts/blindar_release_bla.py" \
    --out "${ROOT_DIR}/$DEB_DIR/opt/jarvis-kids-os" \
    --intensity "$BLA_INTENSITY" \
    --in-place-staging \
    --skip-tests
fi

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
cat << EOF > "${DEB_DIR}/DEBIAN/postinst"
#!/bin/sh
set -e
chmod +x /usr/bin/jarvis-kids 2>/dev/null || true
chmod +x /opt/jarvis-kids-os/*.sh 2>/dev/null || true
chmod +x /opt/jarvis-kids-os/pkg /opt/jarvis-kids-os/pkg.sh 2>/dev/null || true
ln -sf /opt/jarvis-kids-os/pkg /usr/local/bin/pkg 2>/dev/null || true
python3 -m pip install --break-system-packages microdot edge-tts 2>/dev/null || python3 -m pip install microdot edge-tts 2>/dev/null || true
echo "✅ JARVIS Kids OS v${VERSION} instalado com sucesso em /opt/jarvis-kids-os!"
echo "Use 'pkg start' para iniciar o quiosque em tela cheia!"
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
