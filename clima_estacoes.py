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
import urllib.parse
import urllib.request
from typing import Any, Dict
from banco_dados import db


# Coordenadas conhecidas das principais capitais e cidades brasileiras (fallback ultra-rápido offline)
CIDADES_BRASIL = {
    "campo largo": (-25.4595, -49.5301, "Campo Largo", "PR"),
    "curitiba": (-25.4284, -49.2733, "Curitiba", "PR"),
    "londrina": (-23.3045, -51.1696, "Londrina", "PR"),
    "maringa": (-23.4205, -51.9331, "Maringá", "PR"),
    "ponta grossa": (-25.0950, -50.1619, "Ponta Grossa", "PR"),
    "cascavel": (-24.9578, -53.4595, "Cascavel", "PR"),
    "foz do iguacu": (-25.5163, -54.5854, "Foz do Iguaçu", "PR"),
    "sao paulo": (-23.5505, -46.6333, "São Paulo", "SP"),
    "campinas": (-22.9056, -47.0608, "Campinas", "SP"),
    "santos": (-23.9608, -46.3331, "Santos", "SP"),
    "sao jose dos campos": (-23.1896, -45.8841, "São José dos Campos", "SP"),
    "ribeirao preto": (-21.1775, -47.8103, "Ribeirão Preto", "SP"),
    "sorocaba": (-23.5015, -47.4526, "Sorocaba", "SP"),
    "guarulhos": (-23.4542, -46.5333, "Guarulhos", "SP"),
    "osasco": (-23.5325, -46.7917, "Osasco", "SP"),
    "rio de janeiro": (-22.9068, -43.1729, "Rio de Janeiro", "RJ"),
    "niteroi": (-22.8832, -43.1034, "Niterói", "RJ"),
    "brasilia": (-15.7975, -47.8919, "Brasília", "DF"),
    "belo horizonte": (-19.9208, -43.9378, "Belo Horizonte", "MG"),
    "uberlandia": (-18.9186, -48.2772, "Uberlândia", "MG"),
    "juiz de fora": (-21.7587, -43.3496, "Juiz de Fora", "MG"),
    "porto alegre": (-30.0346, -51.2177, "Porto Alegre", "RS"),
    "caxias do sul": (-29.1678, -51.1794, "Caxias do Sul", "RS"),
    "canoas": (-29.9177, -51.1836, "Canoas", "RS"),
    "florianopolis": (-27.5954, -48.5480, "Florianópolis", "SC"),
    "joinville": (-26.3045, -48.8487, "Joinville", "SC"),
    "blumenau": (-26.9196, -49.0658, "Blumenau", "SC"),
    "salvador": (-12.9714, -38.5014, "Salvador", "BA"),
    "recife": (-8.0476, -34.8770, "Recife", "PE"),
    "fortaleza": (-3.7172, -38.5433, "Fortaleza", "CE"),
    "goiania": (-16.6869, -49.2648, "Goiânia", "GO"),
    "manaus": (-3.1190, -60.0217, "Manaus", "AM"),
    "belem": (-1.4558, -48.5039, "Belém", "PA"),
    "vitoria": (-20.3155, -40.3128, "Vitória", "ES"),
}

DEFAULT_LAT = -25.4595  # Campo Largo / Curitiba (PR) como padrão local da família
DEFAULT_LON = -49.5301


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

    CACHE_TTL_SECONDS = 900  # 15 minutos de cache em tempo real

    def __init__(self, database=db, lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON):
        self.db = database
        self.lat = lat
        self.lon = lon
        self.cidade = "Campo Largo"
        self.estado = "Paraná"
        self.pais = "Brasil"
        self.continente = "América do Sul"
        self.planeta = "Planeta Terra"

    def definir_localizacao(self, cidade: str, estado: str = "", pais: str = "Brasil"):
        """Atualiza a localização geográfica e busca coordenadas com geocoding dinâmico."""
        antiga_cid = self.cidade
        antiga_lat = self.lat
        antiga_lon = self.lon

        if cidade:
            self.cidade = cidade.strip()
        if estado:
            self.estado = estado.strip()
        if pais:
            self.pais = pais.strip()

        # 1. Busca em tabela estática de alta velocidade
        cid_norm = self.cidade.lower().replace("ã", "a").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("-", " ")
        encontrado = False
        for k, v in CIDADES_BRASIL.items():
            if k == cid_norm or k in cid_norm or cid_norm in k:
                self.lat, self.lon, self.cidade, self.estado = v[0], v[1], v[2], v[3]
                encontrado = True
                break

        # 2. Geocoding dinâmico via Open-Meteo se a cidade não estiver na lista estática
        if not encontrado and self.cidade:
            try:
                q = urllib.parse.quote(self.cidade)
                url = f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=pt&format=json"
                req = urllib.request.Request(url, headers={"User-Agent": "JarvisKidsOS/3.3"})
                with urllib.request.urlopen(req, timeout=3.0) as res_geo:
                    dados_geo = json.loads(res_geo.read().decode("utf-8"))
                    if dados_geo.get("results"):
                        item = dados_geo["results"][0]
                        self.lat = float(item["latitude"])
                        self.lon = float(item["longitude"])
                        if item.get("name"):
                            self.cidade = item["name"]
                        if item.get("admin1"):
                            self.estado = item["admin1"]
                        if item.get("country"):
                            self.pais = item["country"]
                        encontrado = True
            except Exception:
                pass

        # 3. Se a localização mudou, invalida o cache para atualizar o clima imediatamente
        if antiga_cid != self.cidade or antiga_lat != self.lat or antiga_lon != self.lon:
            try:
                self.db.executar_escrita("DELETE FROM cache_clima WHERE id = 1;")
            except Exception:
                pass

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

    def obter_clima_atual(self, forcar: bool = False) -> Dict[str, Any]:
        """Retorna clima atual com geografia, usando cache de 15 minutos ou Open-Meteo em tempo real."""
        cached = self.db.consultar_um(
            "SELECT temperatura, codigo_tempo, descricao, icone, estacao_ano, conselho_infantil, acessorio_mascote, atualizado_em FROM cache_clima WHERE id = 1;"
        )
        hoje = datetime.date.today()
        estacao = obter_estacao_do_ano(hoje.month)

        deve_atualizar = forcar or (cached is None)
        if not deve_atualizar and cached and cached.get("atualizado_em"):
            try:
                tempo_str = str(cached["atualizado_em"]).split(".")[0]
                formato = "%Y-%m-%d %H:%M:%S"
                t_struct = time.strptime(tempo_str, formato)
                diff = time.time() - time.mktime(t_struct)
                # Se diff estiver fora da janela válida ou for negativo (fuso horário), atualiza
                if diff < 0 or diff >= self.CACHE_TTL_SECONDS:
                    deve_atualizar = True
            except Exception:
                deve_atualizar = True

        geo = self.obter_geografia_infantil()

        if not deve_atualizar and cached:
            res = dict(cached)
            res.update(geo)
            return res

        # Consulta Open-Meteo API com coordenadas reais da cidade
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current=temperature_2m,weather_code&timezone=auto"
            req = urllib.request.Request(url, headers={"User-Agent": "JarvisKidsOS/3.3"})
            with urllib.request.urlopen(req, timeout=4.0) as res_req:
                data = json.loads(res_req.read().decode("utf-8"))
                current = data.get("current", {})
                temp = float(current.get("temperature_2m", 20.0))
                code = int(current.get("weather_code", 0))

                desc, icone, acessorio = self._traduzir_codigo_clima(code, temp)
                conselho = self._gerar_conselho_infantil(temp, code)
                agora_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.db.executar_escrita(
                    """
                    INSERT OR REPLACE INTO cache_clima
                    (id, temperatura, codigo_tempo, descricao, icone, estacao_ano, conselho_infantil, acessorio_mascote, atualizado_em)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (round(temp, 1), code, desc, icone, estacao, conselho, acessorio, agora_str),
                )

                clima_res = {
                    "temperatura": round(temp, 1),
                    "codigo_tempo": code,
                    "descricao": desc,
                    "icone": icone,
                    "estacao_ano": estacao,
                    "conselho_infantil": conselho,
                    "acessorio_mascote": acessorio,
                    "atualizado_em": agora_str,
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
            "temperatura": 20.0,
            "codigo_tempo": 0,
            "descricao": "Tempo Tranquilo e Agradável",
            "icone": "⛅",
            "estacao_ano": estacao,
            "conselho_infantil": "O dia está ótimo para brincar e aprender! Lembre-se de tomar um copo d'água!",
            "acessorio_mascote": "oculos_sol.png",
        }
        clima_res.update(geo)
        return clima_res

    def obter_previsao_amanha(self) -> Dict[str, Any]:
        """Consulta previsão meteorológica detalhada para o dia seguinte (amanhã)."""
        geo = self.obter_geografia_infantil()
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
            req = urllib.request.Request(url, headers={"User-Agent": "JarvisKidsOS/3.4"})
            with urllib.request.urlopen(req, timeout=4.0) as res_req:
                data = json.loads(res_req.read().decode("utf-8"))
                daily = data.get("daily", {})
                times = daily.get("time", [])
                if len(times) > 1:
                    max_temp = float(daily.get("temperature_2m_max", [22.0, 20.0])[1])
                    min_temp = float(daily.get("temperature_2m_min", [15.0, 14.0])[1])
                    code = int(daily.get("weather_code", [0, 0])[1])
                    prob_chuva = int(daily.get("precipitation_probability_max", [0, 0])[1])

                    desc, icone, acessorio = self._traduzir_codigo_clima(code, max_temp)

                    if prob_chuva >= 50 or code in (51, 53, 55, 61, 63, 65, 80, 81, 82, 95):
                        conselho = f"🌧️ A previsão indica {prob_chuva}% de chance de chuva amanhã! Se for sair de casa, separe a capa ou o guarda-chuva!"
                    elif max_temp < 18.0:
                        conselho = f"❄️ Amanhã vai fazer friozinho com mínima de {round(min_temp)} graus! Separe um casaco bem quentinho!"
                    elif max_temp > 27.0:
                        conselho = f"☀️ Amanhã o dia promete calor com máxima de {round(max_temp)} graus! Lembre-se de beber bastante água!"
                    else:
                        conselho = "🌤️ Amanhã o clima estará super agradável para brincar e aprender com o Jarvis!"

                    res = {
                        "ok": True,
                        "data_amanha": times[1],
                        "temp_max": round(max_temp, 1),
                        "temp_min": round(min_temp, 1),
                        "codigo_tempo": code,
                        "prob_chuva": prob_chuva,
                        "descricao": desc,
                        "icone": icone,
                        "conselho_infantil": conselho,
                        "acessorio_mascote": acessorio,
                    }
                    res.update(geo)
                    return res
        except Exception:
            pass

        # Fallback seguro para modo offline
        res = {
            "ok": True,
            "temp_max": 20.0,
            "temp_min": 14.0,
            "codigo_tempo": 0,
            "prob_chuva": 20,
            "descricao": "Tempo Aconchegante e Agradável",
            "icone": "⛅",
            "conselho_infantil": "Amanhã o dia será ótimo para se divertir e aprender coisas novas com o Jarvis!",
            "acessorio_mascote": "bone.png",
        }
        res.update(geo)
        return res

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
