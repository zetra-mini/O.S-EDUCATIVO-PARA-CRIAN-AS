"""
Módulo de Configuração de Hardware e Energia para antiX Linux & Cross-Platform (config_hardware.py).
Otimizado para o netbook Acer Aspire One 532h / Asus Eee PC (Intel Atom N450 / GMA 3150):
1. Wi-Fi: Escaneamento e conexão em background via nmcli (Linux) e netsh (Windows).
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
import socket
import subprocess
from typing import Any, Dict, List, Optional

SISTEMA = platform.system().lower()


def obter_ip_local_maquina() -> str:
    """Detecta o IP local do dispositivo na rede doméstica."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class HardwareManager:
    """Gerenciador centralizado de hardware, energia e quiosque Linux."""

    def __init__(self):
        self._display_cache: Optional[str] = None

    # ==========================================================================
    # 1. GESTÃO DE WI-FI (nmcli no Linux, netsh no Windows)
    # ==========================================================================
    def obter_rede_wifi_conectada(self) -> Dict[str, Any]:
        """Obtém com precisão a rede Wi-Fi à qual o netbook está conectado no momento."""
        ip_atual = obter_ip_local_maquina()

        # 1. WINDOWS (netsh wlan show interfaces)
        if "windows" in SISTEMA:
            try:
                out = subprocess.check_output(
                    ["netsh", "wlan", "show", "interfaces"],
                    text=True,
                    errors="ignore",
                    timeout=3
                )
                ssid_m = re.search(r"^\s*SSID\s*:\s*(.+)$", out, re.M)
                estado_m = re.search(r"^\s*Estado\s*:\s*(.+)$", out, re.M)
                sinal_m = re.search(r"^\s*Sinal\s*:\s*(\d+)%", out, re.M)
                sec_m = re.search(r"^\s*Autentica..o\s*:\s*(.+)$", out, re.M)

                if ssid_m and estado_m and "conectado" in estado_m.group(1).lower():
                    ssid = ssid_m.group(1).strip()
                    if ssid:
                        return {
                            "conectado": True,
                            "ssid": ssid,
                            "signal": f"{sinal_m.group(1)}%" if sinal_m else "95%",
                            "security": sec_m.group(1).strip() if sec_m else "WPA2",
                            "ip": ip_atual,
                            "bars": "▂▄▆█",
                        }
            except Exception:
                pass
            return {"conectado": False, "ssid": None, "ip": ip_atual}

        # 2. LINUX (antiX / Debian: iwgetid, nmcli ou /proc/net/wireless)
        conectada_ssid = None
        sinal = "90%"
        seguranca = "WPA2"

        # Tentativa 1: iwgetid (mais leve e rápido no antiX Linux)
        if shutil.which("iwgetid"):
            try:
                out_iw = subprocess.check_output(["iwgetid", "-r"], stderr=subprocess.DEVNULL, timeout=2).decode().strip()
                if out_iw:
                    conectada_ssid = out_iw
            except Exception:
                pass

        # Tentativa 2: nmcli ativo
        if not conectada_ssid and shutil.which("nmcli"):
            try:
                out_active = subprocess.check_output(
                    ["nmcli", "-t", "-f", "TYPE,NAME", "connection", "show", "--active"],
                    stderr=subprocess.DEVNULL, timeout=3
                ).decode("utf-8", errors="ignore")
                for l in out_active.splitlines():
                    if l.startswith("802-11-wireless:") or l.startswith("wifi:"):
                        conectada_ssid = l.split(":", 1)[1].strip()
                        break
            except Exception:
                pass

        # Tentativa 3: nmcli dev wifi list (procura por '*')
        if not conectada_ssid and shutil.which("nmcli"):
            try:
                out_wifi = subprocess.check_output(
                    ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "dev", "wifi", "list"],
                    stderr=subprocess.DEVNULL, timeout=4
                ).decode("utf-8", errors="ignore")
                for l in out_wifi.splitlines():
                    parts = re.split(r"(?<!\\):", l.strip())
                    if len(parts) >= 4 and parts[0].strip() == "*":
                        conectada_ssid = parts[1].replace(r"\:", ":").strip()
                        sinal = f"{parts[2].strip()}%"
                        seguranca = parts[3].strip() or "WPA2"
                        break
            except Exception:
                pass

        if conectada_ssid:
            return {
                "conectado": True,
                "ssid": conectada_ssid,
                "signal": sinal,
                "security": seguranca,
                "ip": ip_atual,
                "bars": "▂▄▆█",
            }

        return {"conectado": False, "ssid": None, "ip": ip_atual}

    def escanear_wifi(self) -> List[Dict[str, Any]]:
        """Escaneia todas as redes Wi-Fi disponíveis ao redor e destaca a rede conectada."""
        redes: List[Dict[str, Any]] = []
        info_conectada = self.obter_rede_wifi_conectada()
        ssid_conectado = info_conectada.get("ssid") if info_conectada.get("conectado") else None
        ssids_vistos = set()

        # ----------------------------------------------------------------------
        # A. AMBIENTE WINDOWS (netsh wlan show networks mode=bssid)
        # ----------------------------------------------------------------------
        if "windows" in SISTEMA:
            try:
                out_net = subprocess.check_output(
                    ["netsh", "wlan", "show", "networks", "mode=bssid"],
                    text=True,
                    errors="ignore",
                    timeout=5
                )
                curr_ssid = None
                curr_sec = "Aberta"
                curr_sig = "70%"

                for line in out_net.splitlines():
                    line = line.strip()
                    if line.startswith("SSID ") and ":" in line:
                        if curr_ssid and curr_ssid not in ssids_vistos:
                            ssids_vistos.add(curr_ssid)
                            is_con = bool(ssid_conectado and curr_ssid == ssid_conectado)
                            redes.append({
                                "ssid": curr_ssid,
                                "signal": curr_sig,
                                "security": curr_sec,
                                "bars": "▂▄▆█" if int(curr_sig.replace("%", "") or "0") > 70 else "▂▄▆_",
                                "conectado": is_con,
                            })
                        parts = line.split(":", 1)
                        curr_ssid = parts[1].strip()
                        curr_sec = "Aberta"
                        curr_sig = "70%"
                    elif "Autentica" in line and ":" in line:
                        curr_sec = line.split(":", 1)[1].strip()
                    elif "Sinal" in line and ":" in line:
                        s_m = re.search(r"(\d+)%", line)
                        if s_m:
                            curr_sig = f"{s_m.group(1)}%"

                if curr_ssid and curr_ssid not in ssids_vistos:
                    ssids_vistos.add(curr_ssid)
                    is_con = bool(ssid_conectado and curr_ssid == ssid_conectado)
                    redes.append({
                        "ssid": curr_ssid,
                        "signal": curr_sig,
                        "security": curr_sec,
                        "bars": "▂▄▆█" if int(curr_sig.replace("%", "") or "0") > 70 else "▂▄▆_",
                        "conectado": is_con,
                    })
            except Exception:
                pass

            # Garante que a rede conectada esteja sempre incluída e em 1º lugar
            if ssid_conectado:
                if not any(r["ssid"] == ssid_conectado for r in redes):
                    redes.insert(0, {
                        "ssid": ssid_conectado,
                        "signal": info_conectada.get("signal", "95%"),
                        "security": info_conectada.get("security", "WPA2"),
                        "bars": "▂▄▆█",
                        "conectado": True,
                    })
                else:
                    for r in redes:
                        if r["ssid"] == ssid_conectado:
                            r["conectado"] = True
                redes.sort(key=lambda x: (not x.get("conectado", False), x["ssid"].lower()))

            return redes

        # ----------------------------------------------------------------------
        # B. AMBIENTE LINUX (antiX / Debian: nmcli & iwlist)
        # ----------------------------------------------------------------------
        # 1. Varredura com nmcli
        if shutil.which("nmcli"):
            try:
                # Tenta forçar atualização do cache Wi-Fi do NetworkManager
                subprocess.run(
                    ["nmcli", "dev", "wifi", "rescan"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
                out = subprocess.check_output(
                    ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY,BARS", "dev", "wifi", "list"],
                    stderr=subprocess.DEVNULL,
                    timeout=6,
                ).decode("utf-8", errors="ignore")

                for linha in out.splitlines():
                    partes = re.split(r"(?<!\\):", linha.strip())
                    if len(partes) >= 5:
                        in_use = partes[0].strip() == "*"
                        ssid = partes[1].replace(r"\:", ":").strip()
                        if not ssid or ssid in ssids_vistos:
                            continue
                        ssids_vistos.add(ssid)
                        if ssid_conectado and ssid == ssid_conectado:
                            in_use = True
                        redes.append({
                            "ssid": ssid,
                            "signal": f"{partes[2].strip()}%",
                            "security": partes[3].strip() or "Aberta",
                            "bars": partes[4].strip() or "▂▄▆█",
                            "conectado": in_use,
                        })
            except Exception:
                pass

        # 2. Fallback com iwlist se nmcli não estiver disponível ou falhar
        if not redes and shutil.which("iwlist"):
            try:
                out_iw = subprocess.check_output(["iwlist", "scan"], stderr=subprocess.DEVNULL, timeout=6).decode("utf-8", errors="ignore")
                for bloco in out_iw.split("Cell "):
                    ssid_m = re.search(r'ESSID:"([^"]+)"', bloco)
                    qual_m = re.search(r"Quality=([0-9/]+)", bloco)
                    enc_m = re.search(r"Encryption key:(on|off)", bloco)
                    if ssid_m:
                        ssid = ssid_m.group(1).strip()
                        if ssid and ssid not in ssids_vistos:
                            ssids_vistos.add(ssid)
                            is_con = bool(ssid_conectado and ssid == ssid_conectado)
                            redes.append({
                                "ssid": ssid,
                                "signal": "85%",
                                "security": "WPA2" if (enc_m and enc_m.group(1) == "on") else "Aberta",
                                "bars": "▂▄▆█",
                                "conectado": is_con,
                            })
            except Exception:
                pass

        # Garante que a rede conectada esteja sempre presente e no topo
        if ssid_conectado:
            if not any(r["ssid"] == ssid_conectado for r in redes):
                redes.insert(0, {
                    "ssid": ssid_conectado,
                    "signal": info_conectada.get("signal", "90%"),
                    "security": info_conectada.get("security", "WPA2"),
                    "bars": "▂▄▆█",
                    "conectado": True,
                })
            else:
                for r in redes:
                    if r["ssid"] == ssid_conectado:
                        r["conectado"] = True
            redes.sort(key=lambda x: (not x.get("conectado", False), x["ssid"].lower()))

        return redes

    def conectar_wifi(self, ssid: str, senha: str = "") -> Dict[str, Any]:
        """Conecta o netbook a uma rede Wi-Fi via nmcli (Linux) ou netsh (Windows)."""
        ssid = ssid.strip()
        if not ssid:
            return {"sucesso": False, "erro": "SSID da rede não informado."}

        # 1. WINDOWS
        if "windows" in SISTEMA:
            try:
                # Tenta conectar se o perfil já estiver salvo
                res = subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], capture_output=True, text=True, timeout=10)
                if res.returncode == 0 and "sucesso" in res.stdout.lower():
                    return {"sucesso": True, "mensagem": f"Conectado à rede '{ssid}' com sucesso!"}
                else:
                    return {"sucesso": True, "mensagem": f"Comando de conexão enviado para '{ssid}'. Verifique o ícone do Wi-Fi."}
            except Exception as e:
                return {"sucesso": False, "erro": str(e)}

        # 2. LINUX (antiX / nmcli)
        if not shutil.which("nmcli"):
            return {"sucesso": False, "erro": "nmcli não encontrado no sistema. Instale o network-manager no antiX."}

        try:
            cmd = ["nmcli", "dev", "wifi", "connect", ssid]
            if senha:
                cmd.extend(["password", senha])

            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=18)
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

    def ajustar_volume(self, volume: int) -> Dict[str, Any]:
        """Ajusta o volume do ALSA com trava segura (máximo 90% para audição infantil)."""
        vol = max(0, min(90, int(volume)))
        if "linux" not in SISTEMA or not shutil.which("amixer"):
            return {"volume": vol, "mutado": False, "sucesso": True}

        try:
            subprocess.run(["amixer", "sset", "Master", f"{vol}%", "unmute"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            return {"volume": vol, "mutado": False, "sucesso": True}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    def alternar_mute(self) -> Dict[str, Any]:
        """Alterna estado de mudo (mute/unmute) no ALSA."""
        if "linux" not in SISTEMA or not shutil.which("amixer"):
            return {"mutado": True, "sucesso": True}

        try:
            subprocess.run(["amixer", "sset", "Master", "toggle"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            return self.obter_volume_atual()
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    # ==========================================================================
    # 3. GESTÃO DE BRILHO E FILTRO NOTURNO
    # ==========================================================================
    def _obter_saida_video(self) -> str:
        """Descobre o nome da saída de vídeo primária (ex: LVDS-1 ou eDP-1 no netbook)."""
        if self._display_cache:
            return self._display_cache

        try:
            out = subprocess.check_output(["xrandr"], stderr=subprocess.DEVNULL, timeout=2).decode()
            m = re.search(r"^(\S+)\s+connected", out, re.M)
            if m:
                self._display_cache = m.group(1)
                return self._display_cache
        except Exception:
            pass
        return "LVDS-1"

    def ajustar_brilho(self, brilho: float) -> Dict[str, Any]:
        """Ajusta o brilho do visor via xrandr (valor entre 0.2 e 1.0)."""
        b = max(0.2, min(1.0, float(brilho)))
        if "linux" not in SISTEMA or not shutil.which("xrandr"):
            return {"brilho": b, "sucesso": True}

        try:
            display = self._obter_saida_video()
            env = os.environ.copy()
            if "DISPLAY" not in env:
                env["DISPLAY"] = ":0"
            subprocess.run(["xrandr", "--output", display, "--brightness", str(b)], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            return {"brilho": b, "sucesso": True}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    def aplicar_filtro_luz_noturna(self, ativar: bool = True) -> Dict[str, Any]:
        """Aplica filtro de luz noturna quente (3500K) para proteção ocular do Kaleu."""
        if "linux" not in SISTEMA:
            return {"sucesso": True, "ativo": ativar}

        env = os.environ.copy()
        if "DISPLAY" not in env:
            env["DISPLAY"] = ":0"

        try:
            if ativar:
                if shutil.which("redshift"):
                    subprocess.run(["redshift", "-P", "-O", "3500"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
                elif shutil.which("sct"):
                    subprocess.run(["sct", "3500"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
            else:
                if shutil.which("redshift"):
                    subprocess.run(["redshift", "-x"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
                elif shutil.which("sct"):
                    subprocess.run(["sct"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
            return {"sucesso": True, "ativo": ativar}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    # ==========================================================================
    # 4. KIOSK BYPASS & MANUTENÇÃO (/manutencao)
    # ==========================================================================
    def liberar_modo_kiosk(self) -> Dict[str, Any]:
        """Finaliza o navegador quiosque para que os pais acessem o desktop Linux antiX."""
        if "linux" not in SISTEMA:
            return {"sucesso": True, "mensagem": "[Simulado] Modo quiosque finalizado."}

        try:
            # Encerra navegadores quiosque comuns no antiX
            subprocess.run(["pkill", "-f", "midori"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "falkon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "chromium"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"sucesso": True, "mensagem": "Navegadores em modo quiosque encerrados. Desktop antiX liberado!"}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    # ==========================================================================
    # 5. GESTÃO DE ENERGIA DO NETBOOK
    # ==========================================================================
    def reiniciar_netbook(self) -> Dict[str, Any]:
        """Reinicia o netbook de forma segura."""
        if "linux" not in SISTEMA:
            return {"sucesso": True, "mensagem": "[Simulado] Reinicialização agendada."}
        try:
            subprocess.Popen(["sudo", "reboot"])
            return {"sucesso": True, "mensagem": "Reiniciando o sistema operacional..."}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    def desligar_netbook(self) -> Dict[str, Any]:
        """Desliga o netbook com segurança."""
        if "linux" not in SISTEMA:
            return {"sucesso": True, "mensagem": "[Simulado] Desligamento agendado."}
        try:
            subprocess.Popen(["sudo", "shutdown", "-h", "now"])
            return {"sucesso": True, "mensagem": "Desligando o computador..."}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}


hardware_mgr = HardwareManager()
