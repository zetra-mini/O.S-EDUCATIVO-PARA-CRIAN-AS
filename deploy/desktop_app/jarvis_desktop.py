"""
Lançador Desktop Universal para o JARVIS Kids OS.
Funciona em Windows, Linux e macOS com detecção automática do navegador nativo
em modo aplicação dedicada (Chrome, Edge, Brave, Chromium) ou navegador padrão.
"""

import os
import sys
import time
import socket
import webbrowser
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
PORT = 8000
URL = f"http://127.0.0.1:{PORT}"


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def iniciar_servidor_se_necessario():
    if is_port_in_use(PORT):
        print(f"✅ Servidor Jarvis já está ativo em {URL}")
        return None

    print(f"🚀 Iniciando servidor backend do Jarvis Kids OS na porta {PORT}...")
    server_script = os.path.join(PROJECT_DIR, "run_server.py")
    if not os.path.exists(server_script):
        server_script = os.path.join(BASE_DIR, "run_server.py")

    proc = subprocess.Popen(
        [sys.executable, server_script, str(PORT)],
        cwd=os.path.dirname(server_script),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Aguarda o servidor subir
    for _ in range(30):
        if is_port_in_use(PORT):
            print("✨ Backend inicializado com sucesso!")
            return proc
        time.sleep(0.2)
    return proc


def abrir_janela_app(url: str):
    """Tenta abrir em modo janela dedicada (--app) para experiência 100% nativa."""
    # Candidatos a executáveis de navegadores modernos
    browsers = []
    if sys.platform == "win32":
        browsers = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]
    else:
        for b in ["google-chrome", "chromium-browser", "chromium", "brave-browser", "microsoft-edge"]:
            p = shutil.which(b)
            if p:
                browsers.append(p)

    for b_path in browsers:
        if os.path.exists(b_path):
            try:
                cmd = [b_path, f"--app={url}", "--window-size=1040,640", "--window-position=center"]
                subprocess.Popen(cmd)
                return
            except Exception:
                pass

    # Fallback se nenhum browser suportar --app
    webbrowser.open(url)


if __name__ == "__main__":
    proc = iniciar_servidor_se_necessario()
    time.sleep(0.5)
    abrir_janela_app(URL)
    print("🌟 Jarvis Kids OS Desktop iniciado!")
