"""
Módulo Meteorológico e das 4 Estações do Ano.
1. Consulta Open-Meteo API (100% gratuita, sem API key).
2. Cache no SQLite de 120 minutos (poupa CPU e evita tráfego de rede).
3. Recomendações infantis de autocuidado prático (agasalho no frio, água no calor, guarda-chuva).
4. Acessório automático no mascote (óculos escuros, capa de chuva, cachecol).
5. Minigame educativo das 4 estações.
"""

import datetime
import json
import time
import urllib.request
from typing import Any, Dict
from banco_dados import db


# Coordenadas padrão (São Paulo / Brasil - ajustável dinamicamente)
DEFAULT_LAT = -23.5505
DEFAULT_LON = -46.6333


def obter_estacao_do_ano(mes: int) -> str:
    """Determina a estação do ano aproximada no Hemisfério Sul."""
    if mes in (12, 1, 2):
        return "Verão"
    elif mes in (3, 4, 5):
        return "Outono"
    elif mes in (6, 7, 8):
        return "Inverno"
    else:
        return "Primavera"


class WeatherSeasonManager:
    """Gerencia clima, cache e aprendizado das 4 estações."""

    CACHE_TTL_SECONDS = 7200  # 120 minutos de cache

    def __init__(self, database=db, lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON):
        self.db = database
        self.lat = lat
        self.lon = lon

    def obter_clima_atual(self) -> Dict[str, Any]:
        """Retorna clima atual usando cache de 120 minutos do SQLite ou consulta Open-Meteo."""
        cached = self.db.consultar_um("SELECT temperatura, codigo_tempo, descricao, icone, estacao_ano, conselho_infantil, acessorio_mascote, atualizado_em FROM cache_clima WHERE id = 1;")
        hoje = datetime.date.today()
        estacao = obter_estacao_do_ano(hoje.month)

        deve_atualizar = True
        if cached and cached.get("atualizado_em"):
            try:
                # Compara timestamp SQLite
                tempo_str = str(cached["atualizado_em"])
                formato = "%Y-%m-%d %H:%M:%S"
                t_struct = time.strptime(tempo_str.split(".")[0], formato)
                diff = time.time() - time.mktime(t_struct)
                if diff < self.CACHE_TTL_SECONDS:
                    deve_atualizar = False
            except Exception:
                pass

        if not deve_atualizar and cached:
            return dict(cached)

        # Tenta consultar Open-Meteo API
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current=temperature_2m,weather_code&timezone=auto"
            req = urllib.request.Request(url, headers={"User-Agent": "JarvisKidsOS/2.6"})
            with urllib.request.urlopen(req, timeout=4.0) as res:
                data = json.loads(res.read().decode("utf-8"))
                current = data.get("current", {})
                temp = float(current.get("temperature_2m", 22.0))
                code = int(current.get("weather_code", 0))

                # Mapeia código para descrição e conselho
                desc, icone, acessorio = self._traduzir_codigo_clima(code, temp)
                conselho = self._gerar_conselho_infantil(temp, code)

                # Salva no cache WAL do SQLite
                self.db.executar_escrita(
                    """
                    INSERT OR REPLACE INTO cache_clima
                    (id, temperatura, codigo_tempo, descricao, icone, estacao_ano, conselho_infantil, acessorio_mascote, atualizado_em)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
                    """,
                    (round(temp, 1), code, desc, icone, estacao, conselho, acessorio),
                )

                return {
                    "temperatura": round(temp, 1),
                    "codigo_tempo": code,
                    "descricao": desc,
                    "icone": icone,
                    "estacao_ano": estacao,
                    "conselho_infantil": conselho,
                    "acessorio_mascote": acessorio,
                }
        except Exception:
            # Fallback seguro para modo offline
            if cached:
                return dict(cached)
            return {
                "temperatura": 24.0,
                "codigo_tempo": 0,
                "descricao": "Dia Ensolarado e Tranquilo",
                "icone": "☀️",
                "estacao_ano": estacao,
                "conselho_infantil": "O dia está ótimo para brincar e aprender! Lembre-se de tomar um copo d'água!",
                "acessorio_mascote": "oculos_sol.png",
            }

    def _traduzir_codigo_clima(self, code: int, temp: float) -> tuple[str, str, str]:
        if code in (51, 53, 55, 61, 63, 65, 80, 81, 82, 95):
            return "Chuva Fresquinha", "🌧️", "guarda_chuva.png"
        elif code in (1, 2, 3):
            return "Céu com Nuvens Suaves", "⛅", "bone.png"
        elif temp < 18.0:
            return "Tempo Frio", "❄️", "cachecol.png"
        else:
            return "Sol Brilhante", "☀️", "oculos_sol.png"

    def _gerar_conselho_infantil(self, temp: float, code: int) -> str:
        if code in (51, 53, 55, 61, 63, 65, 80, 81, 82, 95):
            return "🌧️ A chuva está molhando as plantinhas! Se for passear lá fora, não esqueça a capa ou o guarda-chuva!"
        elif temp < 18.0:
            return "❄️ Brrr! Está friozinho hoje! Missão do Kaleu: colocar um casaco quentinho e uma meia no pé!"
        elif temp > 26.0:
            return "☀️ O sol está quentinho e brilhante! Beba bastante água para manter seu corpo super hidratado!"
        else:
            return "🌤️ O clima está super gostoso hoje! Perfeito para aprender coisas novas com o Jarvis!"

    def obter_dados_estacoes(self) -> Dict[str, Any]:
        """Retorna informações pedagógicas sobre as 4 estações."""
        hoje = datetime.date.today()
        atual = obter_estacao_do_ano(hoje.month)
        return {
            "estacao_atual": atual,
            "estacoes": [
                {
                    "nome": "Primavera",
                    "descricao": "A estação das flores coloridas, dos passarinhos cantando e das borboletas!",
                    "icone": "🌸",
                    "roupa_certa": "Roupa leve e alegre para passear no jardim",
                },
                {
                    "nome": "Verão",
                    "descricao": "Dias longos de muito sol, piscina, praia e picolé gostoso!",
                    "icone": "☀️",
                    "roupa_certa": "Camiseta regata, shorts e protetor solar",
                },
                {
                    "nome": "Outono",
                    "descricao": "As folhas mudam de cor, caem ao chão e o ventinho fica fresco!",
                    "icone": "🍂",
                    "roupa_certa": "Calça confortável e um casaquinho leve",
                },
                {
                    "nome": "Inverno",
                    "descricao": "A época do cobertor quentinho, noites calmas e leite quentinho com sopa!",
                    "icone": "❄️",
                    "roupa_certa": "Casaco grosso, cachecol e meias quentinhas",
                },
            ],
        }


# Instância global
weather_mgr = WeatherSeasonManager()
