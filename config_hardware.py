"""
Módulo de Configuração de Hardware e Energia para antiX Linux (config_hardware.py).
Otimizado para o netbook Acer Aspire One 532h / Asus Eee PC (Intel Atom N450 / GMA 3150):
1. Wi-Fi: Escaneamento e conexão em background via nmcli.
2. Áudio ALSA: Controle de volume mestre (0-100%) e alternância de Mute via amixer.
3. Brilho do Visor: Controle via xrandr (0.2 a 1.0) ou sysfs backlight.
4. Energia: Comandos seguros de desligamento e reinicialização.
5. Kiosk Bypass (/manutencao): Finaliza navegadores em modo quiosque para acesso dos pais ao desktop.
6. Filtro Noturno Circadiano: Aplicação de temperatura de cor (3500K noturno / 6500K diurno) via redshift.
"""

import os
import platform
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional

SISTEMA = platform.system().lower()


class HardwareManager:
    """Gerenciador centralizado de hardware, energia e quiosque Linux."""

    def __init__(self):
        self._display_cache: Optional[str] = None

    # ==========================================================================
    # 1. GESTÃO DE WI-FI (nmcli)
    # ==========================================================================
    def escanear_wifi(self) -> List[Dict[str, Any]]:
        """Escaneia redes Wi-Fi disponíveis ao redor do netbook via nmcli."""
        if "linux" not in SISTEMA:
            return [
                {"ssid": "Wi-Fi Casa (Simulado)", "signal": "95%", "security": "WPA2", "bars": "▂▄▆█", "conectado": True},
                {"ssid": "Visitantes_Kids", "signal": "70%", "security": "WPA2", "bars": "▂▄▆_", "conectado": False},
            ]

        if not shutil.which("nmcli"):
            return []

        try:
            # Rescan em background
            subprocess.run(["nmcli", "dev", "wifi", "rescan"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=4)
            # Lista as redes em formato tabular simples com dois-pontos
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY,BARS", "dev", "wifi", "list"],
                stderr=subprocess.DEVNULL,
                timeout=5,
            ).decode("utf-8", errors="ignore")

            redes = []
            ssids_vistos = set()
            for linha in out.splitlines():
                partes = linha.strip().split(":")
                if len(partes) >= 5:
                    in_use = partes[0] == "*"
                    ssid = partes[1].strip()
                    if not ssid or ssid in ssids_vistos:
                        continue
                    ssids_vistos.add(ssid)
                    redes.append({
                        "ssid": ssid,
                        "signal": f"{partes[2]}%",
                        "security": partes[3] or "Aberta",
                        "bars": partes[4],
                        "conectado": in_use,
                    })
            return redes
        except Exception:
            return []

    def conectar_wifi(self, ssid: str, senha: str = "") -> Dict[str, Any]:
        """Conecta o netbook a uma rede Wi-Fi via nmcli."""
        ssid = ssid.strip()
        if not ssid:
            return {"sucesso": False, "erro": "SSID da rede não informado."}

        if "linux" not in SISTEMA or not shutil.which("nmcli"):
            return {"sucesso": True, "mensagem": f"[Simulado] Conectado à rede '{ssid}' com sucesso!"}

        try:
            cmd = ["nmcli", "dev", "wifi", "connect", ssid]
            if senha:
                cmd.extend(["password", senha])

            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
            if proc.returncode == 0:
                return {"sucesso": True, "mensagem": f"Conectado à rede '{ssid}' com sucesso!"}
            else:
                erro = proc.stderr.strip() or proc.stdout.strip()
                return {"sucesso": False, "erro": erro or "Falha ao autenticar na rede."}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    # ==========================================================================
    # 2. GESTÃO DE ÁUDIO ALSA (amixer)
    # ==========================================================================
    def obter_volume_atual(self) -> Dict[str, Any]:
        """Obtém o volume percentual atual e estado do Mute."""
        if "linux" not in SISTEMA or not shutil.which("amixer"):
            return {"volume": 75, "mutado": False}

        try:
            out = subprocess.check_output(["amixer", "sget", "Master"], stderr=subprocess.DEVNULL, timeout=2).decode()
            vol_match = re.search(r"\[(\d+)%\]", out)
            mute_match = re.search(r"\[(on|off)\]", out)

            vol = int(vol_match.group(1)) if vol_match else 75
            mutado = mute_match.group(1) == "off" if mute_match else False
            return {"volume": vol, "mutado": mutado}
        except Exception:
            return {"volume": 75, "mutado": False}

    def ajustar_volume(self, valor_percentual: int) -> Dict[str, Any]:
        """Define o volume mestre ALSA (0 a 100%)."""
        valor = max(0, min(100, int(valor_percentual)))
        if "linux" in SISTEMA and shutil.which("amixer"):
            try:
                subprocess.run(["amixer", "sset", "Master", f"{valor}%"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                # Garante que desmute ao ajustar volume acima de zero
                if valor > 0:
                    subprocess.run(["amixer", "sset", "Master", "unmute"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            except Exception:
                pass
        return {"sucesso": True, "volume": valor, "mutado": valor == 0}

    def alternar_mute(self) -> Dict[str, Any]:
        """Alterna entre mudo e áudio ativo."""
        mutado_agora = False
        if "linux" in SISTEMA and shutil.which("amixer"):
            try:
                subprocess.run(["amixer", "sset", "Master", "toggle"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                st = self.obter_volume_atual()
                mutado_agora = st["mutado"]
            except Exception:
                pass
        return {"sucesso": True, "mutado": mutado_agora}

    # ==========================================================================
    # 3. GESTÃO DE BRILHO (xrandr) E TELA
    # ==========================================================================
    def _obter_saida_display(self) -> str:
        """Descobre o nome da saída de vídeo primária conectada (ex: LVDS1 ou eDP1)."""
        if self._display_cache:
            return self._display_cache

        padrao = "LVDS1"
        if "linux" in SISTEMA and shutil.which("xrandr"):
            try:
                out = subprocess.check_output(["xrandr", "-q"], stderr=subprocess.DEVNULL, timeout=2).decode()
                for linha in out.splitlines():
                    if " connected" in linha:
                        saida = linha.split()[0]
                        self._display_cache = saida
                        return saida
            except Exception:
                pass
        return padrao

    def ajustar_brilho(self, brilho_float: float) -> Dict[str, Any]:
        """Ajusta o brilho da tela (0.2 a 1.0) via xrandr."""
        brilho = max(0.2, min(1.0, float(brilho_float)))
        if "linux" in SISTEMA and shutil.which("xrandr"):
            saida = self._obter_saida_display()
            try:
                subprocess.run(
                    ["xrandr", "--output", saida, "--brightness", f"{brilho:.2f}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2,
                )
            except Exception:
                pass
        return {"sucesso": True, "brilho": brilho}

    # ==========================================================================
    # 4. FILTRO NOTURNO CIRCADIANO (redshift / sct)
    # ==========================================================================
    def aplicar_filtro_luz_noturna(self, ativar: bool = True) -> Dict[str, Any]:
        """
        Aplica filtro quente de luz noturna (3500K às 19h) ou restaura luz diurna (6500K às 07h).
        Protege os olhos e a produção de melatonina da criança.
        """
        if "linux" in SISTEMA:
            try:
                if ativar:
                    if shutil.which("redshift"):
                        subprocess.run(["redshift", "-O", "3500"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                    elif shutil.which("sct"):
                        subprocess.run(["sct", "3500"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                else:
                    if shutil.which("redshift"):
                        subprocess.run(["redshift", "-x"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                    elif shutil.which("sct"):
                        subprocess.run(["sct", "6500"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            except Exception:
                pass
        return {"sucesso": True, "filtro_noturno_ativo": ativar}

    # ==========================================================================
    # 5. KIOSK BYPASS (/manutencao)
    # ==========================================================================
    def liberar_kiosk_para_manutencao(self) -> Dict[str, Any]:
        """
        Finaliza as instâncias de navegadores em tela cheia (midori, falkon, chromium, firefox)
        para que os pais tenham acesso imediato à área de trabalho do Linux para manutenções.
        """
        encerrados = []
        if "linux" in SISTEMA:
            for navegador in ["midori", "falkon", "chromium", "firefox-esr", "firefox"]:
                try:
                    subprocess.run(["pkill", "-f", navegador], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                    encerrados.append(navegador)
                except Exception:
                    pass
        return {
            "sucesso": True,
            "mensagem": "Navegador de quiosque finalizado. A área de trabalho do Linux está liberada para manutenção!",
            "processos": encerrados,
        }

    # ==========================================================================
    # 6. ENERGIA: REINICIAR E DESLIGAR
    # ==========================================================================
    def reiniciar_netbook(self) -> Dict[str, Any]:
        """Reinicia o computador de forma segura."""
        if "linux" in SISTEMA:
            try:
                subprocess.Popen(["sudo", "reboot"])
            except Exception:
                subprocess.Popen(["reboot"])
        return {"sucesso": True, "mensagem": "Comando de reinicialização disparado com sucesso."}

    def desligar_netbook(self) -> Dict[str, Any]:
        """Desliga o computador com segurança."""
        if "linux" in SISTEMA:
            try:
                subprocess.Popen(["sudo", "shutdown", "-h", "now"])
            except Exception:
                subprocess.Popen(["shutdown", "-h", "now"])
        return {"sucesso": True, "mensagem": "Comando de desligamento disparado com sucesso."}


hardware_mgr = HardwareManager()
