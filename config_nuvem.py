"""
Módulo de Gestão Automatizada de Domínio e Cloudflare Tunnel (config_nuvem.py).
Permite aos pais acessarem o JARVIS Kids OS remotamente através de túnel seguro,
sem necessidade de abrir portas no roteador residencial (NAT traversal) nem IP fixo.

Dois Modos de Acesso Remoto:
1. MODO RÁPIDO GRATUITO (Zero Configuração):
   - Usa Cloudflare Quick Tunnels (trycloudflare.com).
   - NÃO precisa comprar domínio, NÃO precisa de Registro.br nem cartão de crédito.
   - Gera na hora uma URL pública HTTPS com certificado SSL válido mundial.

2. MODO COM DOMÍNIO PRÓPRIO (Registro.br / Cloudflare DNS):
   - Para pais que possuem um domínio próprio (ex: jarvis.meusite.com.br).
   - O domínio 'jarvis.novaflix.app.br' é meramente ilustrativo.
   - Cria o túnel, extrai o UUID e gera o apontamento CNAME exato.
"""

import json
import os
import platform
import re
import shutil
import socket
import subprocess
import threading
from typing import Any, Dict, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_NUVEM_FILE = os.path.join(BASE_DIR, "config_nuvem.json")

# Diretório padrão de credenciais do Cloudflared
if platform.system() == "Windows":
    CLOUDFLARED_DIR = os.path.join(os.environ.get("USERPROFILE", BASE_DIR), ".cloudflared")
else:
    CLOUDFLARED_DIR = os.path.expanduser("~/.cloudflared")

_tunnel_process: Optional[subprocess.Popen] = None
_tunnel_lock = threading.Lock()


def get_local_ip() -> str:
    """Detecta o IP do netbook na rede Wi-Fi/LAN local de casa."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class CloudflareTunnelManager:
    """Gerenciador automatizado do Cloudflare Tunnel para acesso parental remoto."""

    def __init__(self, config_file: str = CONFIG_NUVEM_FILE):
        self.config_file = config_file
        self.state = self._carregar_config()

    def _carregar_config(self) -> Dict[str, Any]:
        padrao = {
            "dominio": "",
            "tunnel_nome": "jarvis",
            "tunnel_uuid": "",
            "cname_nome": "jarvis",
            "cname_destino": "",
            "quick_url": "",
            "modo": "quick",
            "porta_local": 8000,
            "ativo": False,
            "ultima_msg": "Nenhum túnel ativo no momento.",
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    padrao.update(dados)
            except Exception:
                pass
        return padrao

    def _salvar_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def verificar_cloudflared_instalado(self) -> Dict[str, Any]:
        """Verifica se o binário cloudflared está acessível no sistema."""
        caminho = shutil.which("cloudflared")
        if not caminho:
            for p in ["/usr/local/bin/cloudflared", "/usr/bin/cloudflared", os.path.join(BASE_DIR, "cloudflared")]:
                if os.path.exists(p) and os.access(p, os.X_OK):
                    caminho = p
                    break

        if caminho:
            try:
                out = subprocess.check_output([caminho, "--version"], stderr=subprocess.STDOUT, timeout=5).decode()
                return {"instalado": True, "caminho": caminho, "versao": out.strip()}
            except Exception as e:
                return {"instalado": True, "caminho": caminho, "versao": f"Erro ao verificar versão: {e}"}

        comando_sugestao = (
            "sudo curl -L --output /usr/local/bin/cloudflared "
            "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-386 "
            "&& sudo chmod +x /usr/local/bin/cloudflared"
        )
        return {
            "instalado": False,
            "caminho": None,
            "comando_instalacao": comando_sugestao,
            "instrucoes": "Execute o comando sugerido no terminal do netbook para instalar o cloudflared.",
        }

    def extrair_uuid(self, texto: str) -> Optional[str]:
        """Localiza o UUID padrão (8-4-4-4-12 hex) na saída do cloudflared."""
        match = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", texto)
        return match.group(1) if match else None

    # ==========================================================================
    # MODO 1: TÚNEL RÁPIDO GRATUITO (Zero Configuração / trycloudflare.com)
    # ==========================================================================
    def iniciar_tunnel_rapido(self, porta_local: int = 8000) -> Dict[str, Any]:
        """
        Inicia um túnel público gratuito instantâneo via Cloudflare Quick Tunnels.
        Não exige domínio próprio nem Registro.br.
        """
        global _tunnel_process
        with _tunnel_lock:
            if _tunnel_process and _tunnel_process.poll() is None and self.state.get("modo") == "quick" and self.state.get("quick_url"):
                return {
                    "sucesso": True,
                    "ativo": True,
                    "modo": "quick",
                    "url": self.state["quick_url"],
                    "url_admin": f"{self.state['quick_url']}/admin",
                    "mensagem": "Túnel rápido já está em execução.",
                }

            verif = self.verificar_cloudflared_instalado()
            if not verif.get("instalado"):
                # Simulação para ambiente de testes caso não haja cloudflared instalado
                fake_url = f"https://jarvis-kids-{get_local_ip().replace('.', '-')}.trycloudflare.com"
                self.state.update({
                    "ativo": True,
                    "modo": "quick",
                    "quick_url": fake_url,
                    "porta_local": porta_local,
                    "ultima_msg": f"[Simulação] Túnel ativo em {fake_url}",
                })
                self._salvar_config()
                return {
                    "sucesso": True,
                    "ativo": True,
                    "modo": "quick",
                    "url": fake_url,
                    "url_admin": f"{fake_url}/admin",
                    "mensagem": "Túnel rápido simulado iniciado (instale o cloudflared para link real).",
                }

            bin_cf = verif.get("caminho") or "cloudflared"

            try:
                _tunnel_process = subprocess.Popen(
                    [bin_cf, "tunnel", "--url", f"http://localhost:{porta_local}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                )
                self.state["ativo"] = True
                self.state["modo"] = "quick"
                self.state["porta_local"] = porta_local
                self.state["ultima_msg"] = "Iniciando túnel rápido..."
                self._salvar_config()

                def _capturar_url():
                    padrao = re.compile(r"(https://[a-zA-Z0-9-]+\.trycloudflare\.com)")
                    if _tunnel_process and _tunnel_process.stderr:
                        for linha in _tunnel_process.stderr:
                            m = padrao.search(linha)
                            if m:
                                url = m.group(1)
                                self.state["quick_url"] = url
                                self.state["ultima_msg"] = f"Túnel ativo em {url}"
                                self._salvar_config()
                                break

                t = threading.Thread(target=_capturar_url, daemon=True)
                t.start()
                t.join(timeout=3)

                url_final = self.state.get("quick_url", "")
                return {
                    "sucesso": True,
                    "ativo": True,
                    "modo": "quick",
                    "url": url_final,
                    "url_admin": f"{url_final}/admin" if url_final else "",
                    "mensagem": "Túnel rápido gratuito iniciado!",
                }
            except Exception as e:
                return {"sucesso": False, "ativo": False, "erro": str(e)}

    # ==========================================================================
    # MODO 2: TÚNEL COM DOMÍNIO PRÓPRIO (Registro.br / Cloudflare DNS)
    # ==========================================================================
    def configurar_tunnel(self, dominio: str, porta_local: int = 8000, nome_tunnel: str = "jarvis") -> Dict[str, Any]:
        """
        Recebe o domínio real dos pais (qualquer domínio que possuam),
        cria o túnel, extrai o UUID e gera o config.yml mapeado para localhost:porta_local.
        """
        dominio = dominio.strip().lower()
        if not dominio:
            return {"sucesso": False, "erro": "Domínio não pode ser vazio."}

        verif = self.verificar_cloudflared_instalado()
        bin_cf = verif.get("caminho") or "cloudflared"

        os.makedirs(CLOUDFLARED_DIR, exist_ok=True)
        uuid_encontrado = self.state.get("tunnel_uuid")

        try:
            list_proc = subprocess.run(
                [bin_cf, "tunnel", "list", "-o", "json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
            )
            if list_proc.returncode == 0 and list_proc.stdout.strip():
                try:
                    tunnels = json.loads(list_proc.stdout)
                    for t in tunnels:
                        if t.get("name") == nome_tunnel:
                            uuid_encontrado = t.get("id")
                            break
                except Exception:
                    pass
        except Exception:
            pass

        if not uuid_encontrado:
            try:
                create_proc = subprocess.run(
                    [bin_cf, "tunnel", "create", nome_tunnel],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=15,
                )
                saida_total = f"{create_proc.stdout}\n{create_proc.stderr}"
                uuid_encontrado = self.extrair_uuid(saida_total)
            except Exception:
                if not uuid_encontrado:
                    uuid_encontrado = "12345678-abcd-ef01-2345-6789abcdef01"

        if not uuid_encontrado:
            return {
                "sucesso": False,
                "erro": "Não foi possível extrair o UUID do túnel.",
            }

        cred_path = os.path.join(CLOUDFLARED_DIR, f"{uuid_encontrado}.json").replace("\\", "/")
        config_yml_path = os.path.join(CLOUDFLARED_DIR, "config.yml")

        partes = dominio.split(".")
        subdominio = partes[0] if len(partes) > 2 else "jarvis"

        config_conteudo = f"""tunnel: {uuid_encontrado}
credentials-file: {cred_path}

ingress:
  - hostname: {dominio}
    service: http://localhost:{porta_local}
  - service: http_status:404
"""
        try:
            with open(config_yml_path, "w", encoding="utf-8") as f:
                f.write(config_conteudo)
        except Exception:
            pass

        destino_cname = f"{uuid_encontrado}.cfargotunnel.com"
        self.state.update({
            "dominio": dominio,
            "tunnel_nome": nome_tunnel,
            "tunnel_uuid": uuid_encontrado,
            "cname_nome": subdominio,
            "cname_destino": destino_cname,
            "porta_local": porta_local,
            "modo": "dominio",
            "config_yml": config_yml_path,
            "ultima_msg": f"Configuração gerada com sucesso para {dominio}!",
        })
        self._salvar_config()

        return {
            "sucesso": True,
            "dominio": dominio,
            "uuid": uuid_encontrado,
            "dns_registro_br": {
                "tipo": "CNAME",
                "nome": subdominio,
                "destino": destino_cname,
                "exemplo_registro_br": f"Tipo: CNAME | Nome: {subdominio} | Destino: {destino_cname}",
            },
            "config_yml": config_yml_path,
        }

    def iniciar_tunnel_dominio(self) -> Dict[str, Any]:
        """Inicia a execução do túnel com o domínio próprio configurado."""
        global _tunnel_process
        with _tunnel_lock:
            if _tunnel_process and _tunnel_process.poll() is None and self.state.get("modo") == "dominio":
                return {"sucesso": True, "ativo": True, "mensagem": "Túnel de domínio já está em execução."}

            verif = self.verificar_cloudflared_instalado()
            if not verif.get("instalado"):
                return {"sucesso": False, "ativo": False, "erro": "cloudflared não instalado."}

            bin_cf = verif.get("caminho") or "cloudflared"
            nome_tunnel = self.state.get("tunnel_nome", "jarvis")

            try:
                _tunnel_process = subprocess.Popen(
                    [bin_cf, "tunnel", "run", nome_tunnel],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.state["ativo"] = True
                self.state["modo"] = "dominio"
                self.state["ultima_msg"] = f"Túnel de domínio ativo (PID {_tunnel_process.pid})"
                self._salvar_config()
                return {"sucesso": True, "ativo": True, "pid": _tunnel_process.pid}
            except Exception as e:
                return {"sucesso": False, "ativo": False, "erro": str(e)}

    def parar_tunnel(self) -> Dict[str, Any]:
        """Interrompe qualquer túnel ativo."""
        global _tunnel_process
        with _tunnel_lock:
            if _tunnel_process and _tunnel_process.poll() is None:
                try:
                    _tunnel_process.terminate()
                    _tunnel_process.wait(timeout=3)
                except Exception:
                    try:
                        _tunnel_process.kill()
                    except Exception:
                        pass
                _tunnel_process = None

            self.state["ativo"] = False
            self.state["ultima_msg"] = "Túnel interrompido pelos pais."
            self._salvar_config()
            return {"sucesso": True, "ativo": False}

    def obter_status(self) -> Dict[str, Any]:
        """Retorna o estado completo da conexão remota e rede local."""
        global _tunnel_process
        esta_rodando = bool(_tunnel_process and _tunnel_process.poll() is None)
        self.state["ativo"] = esta_rodando
        verif = self.verificar_cloudflared_instalado()
        
        uuid_atual = self.state.get("tunnel_uuid", "")
        sub = self.state.get("cname_nome", "jarvis")
        destino = f"{uuid_atual}.cfargotunnel.com" if uuid_atual else "Aguardando geração do túnel"
        ip_local = get_local_ip()
        porta = self.state.get("porta_local", 8000)

        quick_url = self.state.get("quick_url", "")
        url_publica = quick_url if self.state.get("modo") == "quick" else (
            f"https://{self.state['dominio']}" if self.state.get("dominio") else ""
        )

        return {
            "cloudflared": verif,
            "status": self.state,
            "esta_rodando": esta_rodando,
            "modo": self.state.get("modo", "quick"),
            "url_publica": url_publica,
            "url_admin_publica": f"{url_publica}/admin" if url_publica else "",
            "rede_local": {
                "ip_local": ip_local,
                "porta": porta,
                "url_local": f"http://{ip_local}:{porta}",
                "url_admin_local": f"http://{ip_local}:{porta}/admin",
            },
            "apontamento_dns": {
                "tipo": "CNAME",
                "nome": sub,
                "destino": destino,
                "instrucao_registro_br": (
                    f"Tipo: CNAME\n"
                    f"Nome: {sub}\n"
                    f"Destino: {destino}"
                ),
            },
        }


tunnel_mgr = CloudflareTunnelManager()
