"""
Módulo Meteorológico e das 4 Estações do Ano com Geografia Educativa.
1. Consulta Open-Meteo API (100% gratuita, sem API key).
2. Cache no SQLite de 120 minutos (poupa CPU e evita tráfego de rede).
3. Recomendações infantis de autocuidado prático (agasalho no frio, água no calor, guarda-chuva).
4. Geografia ensinável para a criança se localizar no mundo:
   Planeta Terra 🌍 -> América do Sul -> Brasil 🇧🇷 -> Estado -> Cidade!
5. Minigame educativo das 4 estações e conselhos meteorológicos.
"""

import datetime
import json
import time
import urllib.request
from typing import Any, Dict
from banco_dados import db


# Coordenadas conhecidas das principais capitais e cidades brasileiras
CIDADES_BRASIL = {
    "sao paulo": (-23.5505, -46.6333, "São Paulo", "SP"),
    "rio de janeiro": (-22.9068, -43.1729, "Rio de Janeiro", "RJ"),
    "brasilia": (-15.7975, -47.8919, "Brasília", "DF"),
    "belo horizonte": (-19.9208, -43.9378, "Belo Horizonte", "MG"),
    "curitiba": (-25.4284, -49.2733, "Curitiba", "PR"),
    "porto alegre": (-30.0346, -51.2177, "Porto Alegre", "RS"),
    "salvador": (-12.9714, -38.5014, "Salvador", "BA"),
    "recife": (-8.0476, -34.8770, "Recife", "PE"),
    "fortaleza": (-3.7172, -38.5433, "Fortaleza", "CE"),
    "goiania": (-16.6869, -49.2648, "Goiânia", "GO"),
    "manaus": (-3.1190, -60.0217, "Manaus", "AM"),
    "belem": (-1.4558, -48.5039, "Belém", "PA"),
    "florianopolis": (-27.5954, -48.5480, "Florianópolis", "SC"),
    "vitoria": (-20.3155, -40.3128, "Vitória", "ES"),
    "campinas": (-22.9056, -47.0608, "Campinas", "SP"),
    "santos": (-23.9608, -46.3331, "Santos", "SP"),
}

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
    """Gerencia clima, cache, geografia ensinável e aprendizado das 4 estações."""

    CACHE_TTL_SECONDS = 7200  # 120 minutos de cache

    def __init__(self, database=db, lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON):
        self.db = database
        self.lat = lat
        self.lon = lon
        self.cidade = "São Paulo"
        self.estado = "São Paulo"
        self.pais = "Brasil"
        self.continente = "América do Sul"
        self.planeta = "Planeta Terra"

    def definir_localizacao(self, cidade: str, estado: str = "", pais: str = "Brasil"):
        """Atualiza a localização geográfica e busca coordenadas aproximadas."""
        if cidade:
            self.cidade = cidade.strip()
        if estado:
            self.estado = estado.strip()
        if pais:
            self.pais = pais.strip()

        # Busca coordenadas aproximadas
        cid_norm = self.cidade.lower().replace("ã", "a").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        for k, v in CIDADES_BRASIL.items():
            if k in cid_norm or cid_norm in k:
                self.lat, self.lon, self.cidade, self.estado = v[0], v[1], v[2], v[3]
                break

    def obter_geografia_infantil(self) -> Dict[str, Any]:
        """Gera informações geográficas ensináveis para a criança entender seu lugar no mundo."""
        return {
            "planeta": self.planeta,
            "icone_planeta": "🌍",
            "continente": self.continente,
            "icone_continente": "🌎",
            "pais": self.pais,
            "icone_pais": "🇧🇷",
            "estado": self.estado,
            "cidade": self.cidade,
            "icone_cidade": "🏙️",
            "texto_ensinavel": (
                f"Você sabia onde está agora? Você está na cidade de {self.cidade}, "
                f"no estado de {self.estado}, no nosso amado país {self.pais} 🇧🇷, "
                f"na {self.continente}, no lindo {self.planeta} 🌍!"
            ),
        }

    def obter_clima_atual(self) -> Dict[str, Any]:
        """Retorna clima atual com geografia, usando cache de 120 minutos do SQLite ou Open-Meteo."""
        cached = self.db.consultar_um(
            "SELECT temperatura, codigo_tempo, descricao, icone, estacao_ano, conselho_infantil, acessorio_mascote, atualizado_em FROM cache_clima WHERE id = 1;"
        )
        hoje = datetime.date.today()
        estacao = obter_estacao_do_ano(hoje.month)

        deve_atualizar = True
        if cached and cached.get("atualizado_em"):
            try:
                tempo_str = str(cached["atualizado_em"])
                formato = "%Y-%m-%d %H:%M:%S"
                t_struct = time.strptime(tempo_str.split(".")[0], formato)
                diff = time.time() - time.mktime(t_struct)
                if diff < self.CACHE_TTL_SECONDS:
                    deve_atualizar = False
            except Exception:
                pass

        geo = self.obter_geografia_infantil()

        if not deve_atualizar and cached:
            res = dict(cached)
            res.update(geo)
            return res

        # Tenta consultar Open-Meteo API
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current=temperature_2m,weather_code&timezone=auto"
            req = urllib.request.Request(url, headers={"User-Agent": "JarvisKidsOS/2.7"})
            with urllib.request.urlopen(req, timeout=4.0) as res_req:
                data = json.loads(res_req.read().decode("utf-8"))
                current = data.get("current", {})
                temp = float(current.get("temperature_2m", 22.0))
                code = int(current.get("weather_code", 0))

                desc, icone, acessorio = self._traduzir_codigo_clima(code, temp)
                conselho = self._gerar_conselho_infantil(temp, code)

                self.db.executar_escrita(
                    """
                    INSERT OR REPLACE INTO cache_clima
                    (id, temperatura, codigo_tempo, descricao, icone, estacao_ano, conselho_infantil, acessorio_mascote, atualizado_em)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
                    """,
                    (round(temp, 1), code, desc, icone, estacao, conselho, acessorio),
                )

                clima_res = {
                    "temperatura": round(temp, 1),
                    "codigo_tempo": code,
                    "descricao": desc,
                    "icone": icone,
                    "estacao_ano": estacao,
                    "conselho_infantil": conselho,
                    "acessorio_mascote": acessorio,
                }
                clima_res.update(geo)
                return clima_res
        except Exception:
            pass

        # Fallback seguro para modo offline
        if cached:
            res = dict(cached)
            res.update(geo)
            return res

        clima_res = {
            "temperatura": 24.0,
            "codigo_tempo": 0,
            "descricao": "Dia Ensolarado e Tranquilo",
            "icone": "☀️",
            "estacao_ano": estacao,
            "conselho_infantil": "O dia está ótimo para brincar e aprender! Lembre-se de tomar um copo d'água!",
            "acessorio_mascote": "oculos_sol.png",
        }
        clima_res.update(geo)
        return clima_res

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
            return "❄️ Brrr! Está friozinho hoje! Missão do Herói: colocar um casaco quentinho e uma meia no pé!"
        elif temp > 26.0:
            return "☀️ O sol está quentinho e brilhante! Beba bastante água para manter seu corpo super hidratado!"
        else:
            return "🌤️ O clima está super gostoso hoje! Perfeito para aprender coisas novas com o Jarvis!"

    def obter_dados_estacoes(self) -> Dict[str, Any]:
        """Retorna informações pedagógicas sobre as 4 estações e geografia."""
        hoje = datetime.date.today()
        atual = obter_estacao_do_ano(hoje.month)
        return {
            "estacao_atual": atual,
            "geografia": self.obter_geografia_infantil(),
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
