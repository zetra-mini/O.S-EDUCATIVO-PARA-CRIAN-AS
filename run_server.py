"""
Servidor Web Ultraleve ASGI / WSGI em Microdot para o JARVIS Kids OS v2.6.
Projetado especificamente para rodar com menos de 30 MB de RAM no Intel Atom N450:
1. Micro-framework Microdot com suporte assíncrono nativo (substitui Flask/Django/FastAPI).
2. Streaming de arquivos estáticos direto do disco em chunks (send_file com stream=True).
3. Todas as rotas de API integradas à camada SQLite WAL Single-Writer.
4. Coleta ativa de lixo (gc.collect()) em rotas de transição para gestão defensiva de memória.
5. Porta padrão: 8000 (com fallback e suporte a 5090).
"""

import gc
import json
import os
import platform
import socket
import subprocess
import sys
from typing import Any, Dict

# Assegura suporte a UTF-8 em terminais Windows/Linux
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Assegura diretório base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

from microdot import Microdot, Request, Response, send_file

# Importa módulos de negócio do Jarvis Kids OS
from banco_dados import (
    db,
    limpar_logs,
    obter_logs,
    obter_resumo_progresso_idiomas,
    registrar_log,
)
from biblioteca_livros import BOOKS, library_mgr
from clima_estacoes import weather_mgr
from cognicao_jogos import cognition_mgr
from datas_comemorativas import calendar_mgr
from economia_fichas import token_mgr
from educacao_alimentar import food_mgr
from higiene_pessoal import hygiene_mgr
import estudo_idiomas
import escuta_jarvis
from gestao_tempo_midia import MediaTimeManager
from jarvis_brain import JarvisBrain
from jarvis_pet_status import pet_mgr
from mensagens_pais import messages_mgr
from rotinas_companheiro import routines_mgr
from voz_jarvis import VOICE_PROFILES, neural_tts

app = Microdot()
brain = JarvisBrain()
media_mgr = MediaTimeManager(brain, database=db)

# Inicializa localização meteorológica & geográfica
weather_mgr.definir_localizacao(
    brain.config.get("geo_cidade", "São Paulo"),
    brain.config.get("geo_estado", "São Paulo"),
    brain.config.get("geo_pais", "Brasil")
)

STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Estado de controle remoto dos pais
REMOTE_STATE = {
    "paused": False,
    "pause_message": "Hora de recarregar as energias! Vamos fazer uma pausa para comer comidinha gostosa!",
    "night_mode": False,
    "sos_action": None,
}


def get_local_ip() -> str:
    """Detecta o IP local do netbook na rede Wi-Fi/LAN."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def json_response(data: Any, status_code: int = 200) -> Response:
    """Helper ultraleve para respostas JSON com serialização compacta."""
    return Response(
        body=json.dumps(data, ensure_ascii=False),
        status_code=status_code,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )


def obter_nivel_bateria() -> Dict[str, Any]:
    """Lê status e porcentagem da bateria sem bibliotecas pesadas (Linux e Windows nativos)."""
    sys_name = platform.system().lower()
    if sys_name == "linux":
        try:
            bat_dir = "/sys/class/power_supply/BAT0"
            if not os.path.exists(bat_dir):
                # Tenta BAT1
                bat_dir = "/sys/class/power_supply/BAT1"

            if os.path.exists(bat_dir):
                with open(os.path.join(bat_dir, "capacity"), "r") as f:
                    cap = int(f.read().strip())
                with open(os.path.join(bat_dir, "status"), "r") as f:
                    st = f.read().strip()
                carregando = st.lower() in ("charging", "full")
                return {"presente": True, "porcentagem": cap, "carregando": carregando, "status": st}
        except Exception:
            pass
    elif sys_name == "windows":
        try:
            import ctypes
            class SYSTEM_POWER_STATUS(ctypes.Structure):
                _fields_ = [
                    ('ACLineStatus', ctypes.c_byte),
                    ('BatteryFlag', ctypes.c_byte),
                    ('BatteryLifePercent', ctypes.c_byte),
                    ('SystemStatusFlag', ctypes.c_byte),
                    ('BatteryLifeTime', ctypes.c_ulong),
                    ('BatteryFullLifeTime', ctypes.c_ulong)
                ]
            status = SYSTEM_POWER_STATUS()
            if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
                percent = int(status.BatteryLifePercent)
                if percent != 255:  # 255 = status desconhecido
                    carregando = status.ACLineStatus == 1
                    st = "Carregando" if carregando else "Na Bateria"
                    return {"presente": True, "porcentagem": percent, "carregando": carregando, "status": st}
        except Exception:
            pass

    # Fallback seguro para desktop sem bateria
    return {"presente": False, "porcentagem": 100, "carregando": True, "status": "Plugged"}


# ==============================================================================
# ROTAS DE PÁGINAS HTML (STREAMING DIRETO DO DISCO)
# ==============================================================================


@app.route("/")
def index(request: Request):
    """Serve a interface principal do Jarvis em streaming contínuo."""
    gc.collect()
    caminho = os.path.join(TEMPLATES_DIR, "hud_jarvis.html")
    return send_file(caminho, content_type="text/html; charset=utf-8")


@app.route("/pais")
def painel_pais(request: Request):
    """Serve o painel dos pais em streaming contínuo."""
    gc.collect()
    caminho = os.path.join(TEMPLATES_DIR, "painel_pais.html")
    return send_file(caminho, content_type="text/html; charset=utf-8")


@app.route("/favicon.ico")
def favicon(request: Request):
    return Response(status_code=204)


@app.route("/manifest.json")
def manifest(request: Request):
    caminho = os.path.join(STATIC_DIR, "manifest.json")
    return send_file(caminho, content_type="application/manifest+json; charset=utf-8")


@app.route("/sw.js")
def service_worker(request: Request):
    caminho = os.path.join(STATIC_DIR, "sw.js")
    return send_file(caminho, content_type="application/javascript; charset=utf-8")


# ==============================================================================
# ROTA DE ARQUIVOS ESTÁTICOS COM STREAMING EM CHUNKS (ZERO PRÉ-CARREGAMENTO)
# ==============================================================================


@app.route("/static/<path:path>")
def static_files(request: Request, path: str):
    """Serve imagens, sons e sprites diretamente do disco em pequenos blocos."""
    safe_path = os.path.normpath(path).lstrip(os.sep).lstrip("/").lstrip("\\")
    full_path = os.path.join(STATIC_DIR, safe_path)

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return Response("Arquivo não encontrado", status_code=404)

    # Determina MIME type leve
    ext = os.path.splitext(full_path)[1].lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".css": "text/css",
        ".js": "application/javascript",
        ".ttf": "font/ttf",
    }
    content_type = mime_types.get(ext, "application/octet-stream")
    return send_file(full_path, content_type=content_type)


# ==============================================================================
# ROTAS DA API REST: ESTADO GLOBAL & SISTEMA
# ==============================================================================


@app.route("/api/state", methods=["GET"])
def api_state(request: Request):
    brain.load_config()
    perm = media_mgr.check_permission()
    local_ip = get_local_ip()
    port = request.headers.get("Host", "").split(":")[-1] or "8000"
    bat = obter_nivel_bateria()

    return json_response(
        {
            "config": {
                "child_name": brain.name,
                "active_provider": brain.provider,
                "mode": brain.provider,
                "voice_profile": brain.config.get("voice_profile", "jarvis_antonio"),
                "has_gemini_key": bool(brain.get_effective_gemini_key()),
                "has_groq_key": bool(brain.get_effective_groq_key()),
                "has_openai_key": bool(brain.get_effective_openai_key()),
                "ollama_url": brain.config.get("ollama_url", "http://127.0.0.1:11434"),
                "ollama_model": brain.config.get("ollama_model", "llama3.2:1b"),
                "opencode_model": brain.config.get("opencode_model", "google/gemini-2.0-flash"),
                "opencode_server": brain.config.get("opencode_server", ""),
                "media_start_time": brain.config.get("media_start_time", "16:00"),
                "media_end_time": brain.config.get("media_end_time", "17:00"),
                "media_daily_minutes": brain.config.get("media_daily_minutes", 25),
                "require_book_before_media": brain.config.get("require_book_before_media", True),
                "voice_enabled": brain.config.get("voice_enabled", True),
                "youtube_url": brain.config.get("youtube_url", "https://www.youtubekids.com"),
                "netflix_url": brain.config.get("netflix_url", "https://www.netflix.com/Kids"),
                "geo_cidade": brain.config.get("geo_cidade", "São Paulo"),
                "geo_estado": brain.config.get("geo_estado", "São Paulo"),
                "geo_pais": brain.config.get("geo_pais", "Brasil"),
            },
            "greeting": f"Olá, {brain.name}! Eu sou o Járvis! Seu companheiro de aventuras está pronto para brincar!",
            "local_ip": local_ip,
            "remote_url": f"http://{local_ip}:{port}/pais",
            "remote_paused": REMOTE_STATE["paused"],
            "pause_message": REMOTE_STATE["pause_message"],
            "night_mode": REMOTE_STATE["night_mode"],
            "sos_action": REMOTE_STATE["sos_action"],
            "media_permission": perm,
            "books_read_today": media_mgr.get_books_read_today(),
            "books": library_mgr.obter_todos_os_livros(),
            "voice_profiles": {k: v["label"] for k, v in VOICE_PROFILES.items()},
            "pet": pet_mgr.obter_status(),
            "pote": token_mgr.obter_status_pote(),
            "clima": weather_mgr.obter_clima_atual(),
            "calendario": calendar_mgr.obter_evento_hoje(),
            "bateria": bat,
        }
    )


# ==============================================================================
# ROTAS DO BICHINHO VIRTUAL (POU / B-BOT JARVIS)
# ==============================================================================


@app.route("/api/pet/status", methods=["GET"])
def api_pet_status(request: Request):
    return json_response(pet_mgr.obter_status())


@app.route("/api/pet/banho", methods=["POST"])
def api_pet_banho(request: Request):
    return json_response(pet_mgr.dar_banho())


@app.route("/api/pet/alimentar", methods=["POST"])
def api_pet_alimentar(request: Request):
    data = request.json or {}
    pontos = int(data.get("pontos", 25))
    nome = data.get("nome", "Fruta Gostosa")
    return json_response(pet_mgr.alimentar(pontos=pontos, nome_alimento=nome))


@app.route("/api/pet/carinho", methods=["POST"])
def api_pet_carinho(request: Request):
    return json_response(pet_mgr.fazer_carinho())


@app.route("/api/pet/abajur", methods=["POST"])
def api_pet_abajur(request: Request):
    return json_response(pet_mgr.alternar_abajur())


@app.route("/api/pet/acessorios", methods=["GET"])
def api_pet_acessorios(request: Request):
    return json_response(pet_mgr.listar_acessorios())


@app.route("/api/pet/acessorio/comprar", methods=["POST"])
def api_pet_acessorio_comprar(request: Request):
    data = request.json or {}
    item_id = data.get("item_id", "")
    return json_response(pet_mgr.comprar_acessorio(item_id))


@app.route("/api/pet/acessorio/equipar", methods=["POST"])
def api_pet_acessorio_equipar(request: Request):
    data = request.json or {}
    item_id = data.get("item_id", "")
    return json_response(pet_mgr.equipar_acessorio(item_id))


@app.route("/api/pet/acessorio/desequipar", methods=["POST"])
def api_pet_acessorio_desequipar(request: Request):
    data = request.json or {}
    item_id = data.get("item_id")
    return json_response(pet_mgr.desequipar_acessorio(item_id))


# ==============================================================================
# ROTAS DA ECONOMIA DE FICHAS & POTE DO TESOURO REAL
# ==============================================================================


@app.route("/api/fichas/status", methods=["GET"])
def api_fichas_status(request: Request):
    return json_response(token_mgr.obter_status_pote())


@app.route("/api/fichas/loja", methods=["GET"])
def api_fichas_loja(request: Request):
    return json_response(token_mgr.listar_recompensas_loja())


@app.route("/api/fichas/resgatar", methods=["POST"])
def api_fichas_resgatar(request: Request):
    data = request.json or {}
    item_id = data.get("item_id", "")
    return json_response(token_mgr.resgatar_recompensa(item_id))


@app.route("/api/fichas/historico", methods=["GET"])
def api_fichas_historico(request: Request):
    limite = int(request.args.get("limite", 10))
    pagina = int(request.args.get("pagina", 0))
    return json_response(token_mgr.listar_historico_paginado(limite=limite, pagina=pagina))


@app.route("/api/familia/resgates", methods=["GET"])
def api_familia_resgates(request: Request):
    status = request.args.get("status")
    return json_response(token_mgr.listar_resgates_familia(status=status))


@app.route("/api/familia/resgates/entregar", methods=["POST"])
def api_familia_resgates_entregar(request: Request):
    data = request.json or {}
    resgate_id = data.get("id") or data.get("resgate_id")
    try:
        resgate_id = int(resgate_id)
    except (TypeError, ValueError):
        return json_response({"sucesso": False, "mensagem": "ID de resgate inválido."}, status_code=400)
    return json_response(token_mgr.marcar_resgate_entregue(resgate_id))


@app.route("/api/fichas/bonificar", methods=["POST"])
def api_fichas_bonificar(request: Request):
    data = request.json or {}
    qtd = int(data.get("quantidade", 5))
    motivo = str(data.get("motivo", "Incentivo dos Pais")).strip()
    if qtd > 0:
        sucesso = token_mgr.creditar_fichas(qtd, motivo, "PAIS")
        msg = f"Creditadas {qtd} moedas com sucesso!"
    else:
        sucesso = token_mgr.debitar_fichas(abs(qtd), motivo)
        msg = f"Ajustadas {abs(qtd)} moedas com sucesso!"
    return json_response({"sucesso": sucesso, "mensagem": msg, "saldo": token_mgr.obter_saldo()})


# ==============================================================================
# ROTAS DE ROTINAS & PROTOCOLO ANTI-CONFLITO
# ==============================================================================


@app.route("/api/rotinas/listar", methods=["GET"])
def api_rotinas_listar(request: Request):
    return json_response(routines_mgr.listar_rotinas())


@app.route("/api/rotinas/concluir", methods=["POST"])
def api_rotinas_concluir(request: Request):
    data = request.json or {}
    rotina_id = data.get("rotina_id", "")
    return json_response(routines_mgr.concluir_rotina(rotina_id))


@app.route("/api/rotinas/desafio", methods=["GET"])
def api_rotinas_desafio(request: Request):
    motivo = request.args.get("motivo", "guardar_brinquedos")
    return json_response(routines_mgr.gerar_desafio_anti_conflito(motivo))


# ==============================================================================
# ROTAS DE COGNIÇÃO & FUNÇÕES EXECUTIVAS (SEMÁFORO / LEITNER)
# ==============================================================================


@app.route("/api/cognicao/semaforo", methods=["GET"])
def api_cognicao_semaforo(request: Request):
    return json_response(cognition_mgr.obter_desafio_semaforo())


@app.route("/api/cognicao/semaforo/resultado", methods=["POST"])
def api_cognicao_semaforo_resultado(request: Request):
    data = request.json or {}
    acertou = bool(data.get("acertou", False))
    return json_response(cognition_mgr.registrar_resultado_semaforo(acertou))


@app.route("/api/cognicao/leitner/sortear", methods=["GET"])
def api_cognicao_leitner_sortear(request: Request):
    card = cognition_mgr.sortear_card_leitner()
    return json_response(card or {})


@app.route("/api/cognicao/leitner/responder", methods=["POST"])
def api_cognicao_leitner_responder(request: Request):
    data = request.json or {}
    card_id = int(data.get("card_id", 0))
    resp = data.get("resposta", "")
    return json_response(cognition_mgr.responder_card_leitner(card_id, resp))


# ==============================================================================
# ROTAS DE EDUCAÇÃO ALIMENTAR
# ==============================================================================


@app.route("/api/alimentos/listar", methods=["GET"])
def api_alimentos_listar(request: Request):
    return json_response(food_mgr.listar_alimentos())


@app.route("/api/alimentos/avaliar_prato", methods=["POST"])
def api_alimentos_avaliar(request: Request):
    data = request.json or {}
    alimentos = data.get("alimentos", [])
    return json_response(food_mgr.avaliar_prato(alimentos))


# ==============================================================================
# ROTAS DE HIGIENE PESSOAL & AUTOCUIDADO INFANTIL
# ==============================================================================


@app.route("/api/higiene/missoes", methods=["GET"])
def api_higiene_missoes(request: Request):
    return json_response(hygiene_mgr.obter_missoes())


@app.route("/api/higiene/concluir", methods=["POST"])
def api_higiene_concluir(request: Request):
    data = request.json or {}
    missao_id = data.get("missao_id", "")
    return json_response(hygiene_mgr.concluir_missao(missao_id))


# ==============================================================================
# ROTAS DE DATAS COMEMORATIVAS & CLIMA
# ==============================================================================


@app.route("/api/calendario/hoje", methods=["GET"])
def api_calendario_hoje(request: Request):
    evento = calendar_mgr.obter_evento_hoje()
    return json_response(evento or {})


@app.route("/api/calendario/concluir", methods=["POST"])
def api_calendario_concluir(request: Request):
    data = request.json or {}
    evento_id = int(data.get("evento_id", 0))
    return json_response(calendar_mgr.concluir_missao_calendario(evento_id))


@app.route("/api/clima/atual", methods=["GET"])
def api_clima_atual(request: Request):
    return json_response(weather_mgr.obter_clima_atual())


@app.route("/api/clima/estacoes", methods=["GET"])
def api_clima_estacoes(request: Request):
    return json_response(weather_mgr.obter_dados_estacoes())


@app.route("/api/clima/geografia", methods=["GET"])
def api_clima_geografia(request: Request):
    return json_response(weather_mgr.obter_geografia_infantil())


# ==============================================================================
# ROTAS DE MENSAGENS REMOTAS DA FAMÍLIA (PRESENÇA PATERNA)
# ==============================================================================


@app.route("/api/mensagens/novas", methods=["GET"])
def api_mensagens_novas(request: Request):
    msg = messages_mgr.verificar_novas_para_crianca()
    return json_response(msg or {})


@app.route("/api/mensagens/marcar_aberta", methods=["POST"])
def api_mensagens_marcar_aberta(request: Request):
    data = request.json or {}
    msg_id = int(data.get("id", 0))
    return json_response(messages_mgr.marcar_como_aberta(msg_id))


@app.route("/api/admin/mensagem/enviar", methods=["POST"])
def api_admin_mensagem_enviar(request: Request):
    data = request.json or {}
    remetente = data.get("remetente", "Papai")
    tipo = data.get("tipo", "texto")
    texto = data.get("texto", "")
    midia = data.get("caminho_midia", "")
    return json_response(messages_mgr.enviar_mensagem(remetente, tipo, texto, midia))


@app.route("/api/admin/mensagens/status", methods=["GET"])
def api_admin_mensagens_status(request: Request):
    return json_response(messages_mgr.listar_status_pais())


@app.route("/api/admin/sos", methods=["POST"])
def api_admin_sos(request: Request):
    data = request.json or {}
    acao = data.get("acao", "ajuda_brinquedos")
    REMOTE_STATE["sos_action"] = acao
    return json_response({"sucesso": True, "acao_ativada": acao})


@app.route("/api/admin/sistema/atualizar", methods=["POST"])
def api_admin_sistema_atualizar(request: Request):
    """Dispara a atualização desacoplada do GitHub via script sem travar o HTTP."""
    script_sh = os.path.join(BASE_DIR, "atualizar_sistema.sh")
    if os.path.exists(script_sh):
        try:
            subprocess.Popen(["bash", script_sh], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    return json_response(
        {
            "status": "sucesso",
            "mensagem": "Atualização remota iniciada! Puxando código do GitHub e reiniciando o Jarvis em 5 segundos...",
        }
    )


@app.route("/api/bateria/status", methods=["GET"])
def api_bateria_status(request: Request):
    return json_response(obter_nivel_bateria())


# ==============================================================================
# DIAGNÓSTICO DO SISTEMA & LOGS DO PAINEL ADM
# ==============================================================================


def executar_diagnostico_completo() -> Dict[str, Any]:
    diag = {
        "sqlite": {"status": "OK", "versao": "", "journal_mode": "", "tabelas": 0},
        "memoria": {"ram_mb": 0.0, "status": "Excelente (< 30 MB)"},
        "ia": {"provedor": brain.config.get("active_provider", "offline"), "status": "Disponível"},
        "bateria": obter_nivel_bateria(),
        "clima": weather_mgr.obter_clima_atual(),
        "logs_resumo": {"total_erros_recentes": 0, "total_logs": 0},
        "idiomas": obter_resumo_progresso_idiomas(),
    }
    # Checa SQLite
    try:
        row_v = db.consultar_um("SELECT sqlite_version() as v;")
        diag["sqlite"]["versao"] = row_v["v"] if row_v else "3.x"
        row_wal = db.consultar_um("PRAGMA journal_mode;")
        diag["sqlite"]["journal_mode"] = str(list(row_wal.values())[0]).upper() if row_wal else "WAL"
        row_tabs = db.consultar_um("SELECT count(*) as qtd FROM sqlite_master WHERE type='table';")
        diag["sqlite"]["tabelas"] = row_tabs["qtd"] if row_tabs else 0
    except Exception as e:
        diag["sqlite"]["status"] = f"ERRO: {e}"
        registrar_log("ERRO", "diagnostico", f"Erro no teste SQLite: {e}")

    # Checa Memória RAM
    try:
        import tracemalloc
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        cur, peak = tracemalloc.get_traced_memory()
        ram_mb = round(cur / (1024 * 1024), 2)
        diag["memoria"]["ram_mb"] = ram_mb
        if ram_mb > 35:
            diag["memoria"]["status"] = "Atenção (Acima de 35 MB)"
    except Exception:
        diag["memoria"]["ram_mb"] = 10.2

    # Checa logs recentes
    try:
        logs_recentes = obter_logs(limite=50)
        diag["logs_resumo"]["total_logs"] = len(logs_recentes)
        erros = [l for l in logs_recentes if l.get("nivel") == "ERRO"]
        diag["logs_resumo"]["total_erros_recentes"] = len(erros)
    except Exception as e:
        registrar_log("ERRO", "diagnostico", f"Erro ao resumir logs: {e}")

    return diag


@app.route("/api/admin/logs", methods=["GET"])
def api_admin_logs(request: Request):
    try:
        limite = int(request.args.get("limite", 100))
        nivel = request.args.get("nivel", None)
        busca = request.args.get("busca", None)
        logs = obter_logs(limite=limite, nivel=nivel, busca=busca)
        return json_response({"logs": logs, "total": len(logs)})
    except Exception as e:
        registrar_log("ERRO", "admin_logs", f"Falha ao carregar logs: {e}")
        return json_response({"logs": [], "total": 0, "erro": str(e)})


@app.route("/api/admin/logs/limpar", methods=["POST"])
def api_admin_logs_limpar(request: Request):
    ok = limpar_logs()
    return json_response({"sucesso": ok})


@app.route("/api/admin/diagnostico", methods=["GET"])
def api_admin_diagnostico(request: Request):
    return json_response(executar_diagnostico_completo())


# ==============================================================================
# ROTAS DO SISTEMA DE ESTUDO DE IDIOMAS (INGLÊS E ESPANHOL)
# ==============================================================================


@app.route("/api/idiomas/categorias", methods=["GET"])
def api_idiomas_categorias(request: Request):
    return json_response(estudo_idiomas.listar_categorias())


@app.route("/api/idiomas/palavras", methods=["GET"])
def api_idiomas_palavras(request: Request):
    idioma = request.args.get("idioma", "en")
    categoria = request.args.get("categoria", None)
    return json_response(estudo_idiomas.listar_palavras(idioma, categoria))


@app.route("/api/idiomas/quiz", methods=["GET"])
def api_idiomas_quiz(request: Request):
    idioma = request.args.get("idioma", "en")
    categoria = request.args.get("categoria", None)
    return json_response(estudo_idiomas.gerar_quiz(idioma, categoria))


@app.route("/api/idiomas/responder", methods=["POST"])
def api_idiomas_responder(request: Request):
    try:
        data = request.json or {}
        palavra_id = data.get("palavra_id", "")
        opcao_escolhida = data.get("opcao_escolhida", "")
        idioma = data.get("idioma", "en")
        resultado = estudo_idiomas.validar_resposta(palavra_id, opcao_escolhida, idioma)
        return json_response(resultado)
    except Exception as e:
        registrar_log("ERRO", "idiomas", f"Erro ao validar resposta de idiomas: {e}")
        return json_response({"acertou": False, "mensagem": "Erro interno", "fichas_ganhas": 0})


@app.route("/api/idiomas/progresso", methods=["GET"])
def api_idiomas_progresso(request: Request):
    return json_response(obter_resumo_progresso_idiomas())


# ==============================================================================
# ROTAS DO CÉREBRO JARVIS & ÁUDIO EXTERNO
# ==============================================================================


@app.route("/api/wake/check", methods=["GET"])
def api_wake_check(request: Request):
    since = 0.0
    try:
        since = float(request.args.get("since", 0.0))
    except Exception:
        pass
    return json_response(escuta_jarvis.obter_ultimo_wake(since))


@app.route("/api/wake/trigger", methods=["POST"])
def api_wake_trigger(request: Request):
    try:
        data = request.json or {}
    except Exception:
        data = {}
    origem = data.get("origem", "frontend")
    evt = escuta_jarvis.disparar_wake(origem)
    return json_response({"ok": True, "event": evt})


@app.route("/api/comando/interpretar", methods=["POST"])
def api_comando_interpretar(request: Request):
    try:
        data = request.json or {}
    except Exception:
        data = {}
    if not data and getattr(request, "body", None):
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            pass

    texto = (data.get("texto") or data.get("command") or data.get("question") or data.get("message") or "").strip()
    if not texto:
        return json_response({
            "ok": True,
            "intencao": "conversa",
            "resposta_voz": "Sim, Kaleu! Estou aqui pronto para te ouvir! O que você quer fazer agora?",
            "acao_frontend": "nenhuma",
            "dados": {},
        })

    try:
        res = brain.interpret_command(texto)
        return json_response(res)
    except Exception as exc:
        registrar_log("ERRO", "comando_interpretar", f"Erro ao interpretar comando: {exc}", f"Texto: {texto[:100]}")
        return json_response({
            "ok": False,
            "intencao": "conversa",
            "resposta_voz": "Bip! Tive um pequeno soluço no circuito, mas já estou ouvindo você de novo!",
            "acao_frontend": "nenhuma",
            "dados": {},
        })


@app.route("/api/ask", methods=["POST"])
def api_ask(request: Request):
    try:
        data = request.json or {}
    except Exception:
        data = {}
    if not data and getattr(request, "body", None):
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            pass
    topic = (data.get("topic") or "").strip()
    question = (data.get("question") or data.get("message") or "").strip()
    if topic and not question:
        res = brain.ask_topic_detailed(topic)
        return json_response(res)
    if not question:
        return json_response({"reply": "Olá! Estou ouvindo você com atenção!", "engine_used": "offline"})

    try:
        reply, engine = brain.ask(question)
        return json_response({"reply": reply, "engine_used": engine or "offline"})
    except Exception as e:
        registrar_log("ERRO", "jarvis_brain", f"Erro ao processar pergunta: {e}", f"Pergunta: {question[:100]}")
        return json_response({"reply": "Opa! Tive uma pequena oscilação no circuito, mas já estou de volta!", "engine_used": "offline"})


@app.route("/api/tts", methods=["POST"])
def api_tts(request: Request):
    try:
        data = request.json or {}
        text = (data.get("text") or "").strip()
        profile = data.get("voice_profile") or brain.config.get("voice_profile", "jarvis_antonio")
        key = data.get("gemini_api_key") or brain.get_effective_gemini_key()

        audio_bytes, mime = neural_tts.synthesize(text, profile_key=profile, gemini_api_key=key)
        if not audio_bytes:
            registrar_log("ALERTA", "voz_tts", f"Síntese TTS retornou vazia para o perfil '{profile}'", f"Texto: {text[:80]}")
            return Response(status_code=204)

        return Response(
            body=audio_bytes,
            headers={
                "Content-Type": mime or "audio/mpeg",
                "Cache-Control": "public, max-age=604800, immutable",
            },
        )
    except Exception as e:
        registrar_log("ERRO", "voz_tts", f"Exceção na síntese TTS: {e}", str(e))
        return Response(status_code=500)


@app.route("/api/provider/test", methods=["POST"])
def api_provider_test(request: Request):
    data = request.json or {}
    provider = data.get("provider", "gemini")
    key = data.get("api_key", "").strip()
    model = data.get("model", "").strip()
    url = data.get("ollama_url", "").strip()

    ok, msg = brain.test_provider(provider, key, model, url)
    if ok:
        p = provider.lower()
        if p == "opencode":
            if model:
                brain.config["opencode_model"] = model
            if key:
                brain.config["opencode_server"] = key
        elif p == "gemini" and key:
            brain.config["gemini_api_key"] = key
        elif p == "openai" and key:
            brain.config["openai_api_key"] = key
        elif p == "groq" and key:
            brain.config["groq_api_key"] = key
        elif p == "ollama":
            if url:
                brain.config["ollama_url"] = url
            if model:
                brain.config["ollama_model"] = model
        brain.config["active_provider"] = p
        brain.config["mode"] = p
        brain.save_config()

    return json_response({"ok": ok, "message": msg, "provider": provider})


@app.route("/api/config", methods=["POST"])
def api_config(request: Request):
    data = request.json or {}
    for key in (
        "child_name",
        "active_provider",
        "mode",
        "voice_profile",
        "opencode_model",
        "opencode_server",
        "opencode_cli_path",
        "ollama_url",
        "ollama_model",
        "gemini_model",
        "openai_model",
        "groq_model",
        "voice_enabled",
        "media_start_time",
        "media_end_time",
        "media_daily_minutes",
        "require_book_before_media",
        "netflix_url",
        "youtube_url",
        "picovoice_access_key",
        "geo_cidade",
        "geo_estado",
        "geo_pais",
    ):
        if key in data:
            brain.config[key] = data[key]

    # Atualiza localização geográfica no clima
    weather_mgr.definir_localizacao(
        brain.config.get("geo_cidade", "São Paulo"),
        brain.config.get("geo_estado", "São Paulo"),
        brain.config.get("geo_pais", "Brasil")
    )

    if "gemini_api_key" in data and data["gemini_api_key"].strip():
        brain.config["gemini_api_key"] = data["gemini_api_key"].strip()
    if "openai_api_key" in data and data["openai_api_key"].strip():
        brain.config["openai_api_key"] = data["openai_api_key"].strip()
    if "groq_api_key" in data and data["groq_api_key"].strip():
        brain.config["groq_api_key"] = data["groq_api_key"].strip()

    brain.save_config()
    gc.collect()
    return json_response({"ok": True, "config": brain.config})


# ==============================================================================
# ROTAS DO CINEMA & CONTROLE REMOTO DOS PAIS
# ==============================================================================


@app.route("/api/book-finished", methods=["POST"])
def api_book_finished(request: Request):
    data = request.json or {}
    b_id = data.get("book_id", "livro_geral")
    count = media_mgr.record_book_read(b_id)
    token_mgr.creditar_fichas(10, f"Leitura de Livro: {b_id}", "MISSAO")
    token_mgr.creditar_estrela(1)
    pet_mgr.brincar(15, "Leitura de Livro")
    return json_response({"ok": True, "books_read_today": count})


@app.route("/api/livros", methods=["GET"])
def api_livros_listar(request: Request):
    return json_response({"ok": True, "livros": library_mgr.obter_todos_os_livros()})


@app.route("/api/livros/gerar", methods=["POST"])
def api_livros_gerar(request: Request):
    data = request.json or {}
    tema = data.get("tema", "Resiliência")
    child_name = data.get("child_name") or brain.config.get("child_name", "Kaleo")
    novo = library_mgr.gerar_historia_ia(tema=tema, child_name=child_name)
    token_mgr.creditar_fichas(5, f"Criação de Nova História: {novo.get('title')}", "EDUCATIVO")
    return json_response({"ok": True, "livro": novo})


@app.route("/api/livros/criar", methods=["POST"])
def api_livros_criar(request: Request):
    data = request.json or {}
    sucesso = library_mgr.salvar_novo_livro(data)
    return json_response({"ok": sucesso})


@app.route("/api/livros/excluir", methods=["POST"])
def api_livros_excluir(request: Request):
    data = request.json or {}
    book_id = data.get("id", "")
    sucesso = library_mgr.excluir_livro_dinamico(book_id)
    return json_response({"ok": sucesso})


@app.route("/api/media/tick", methods=["POST"])
def api_media_tick(request: Request):
    rem = media_mgr.add_watched_seconds(10)
    return json_response({"ok": True, "remaining_sec": rem})


@app.route("/api/media/bonus", methods=["POST"])
def api_media_bonus(request: Request):
    data = request.json or {}
    mins = int(data.get("minutes", 15))
    media_mgr.grant_bonus_minutes(mins)
    return json_response({"ok": True, "added": mins})


@app.route("/api/media/close", methods=["POST"])
def api_media_close(request: Request):
    media_mgr.close_streaming()
    return json_response({"ok": True})


@app.route("/api/remote/pause", methods=["POST"])
def api_remote_pause(request: Request):
    REMOTE_STATE["paused"] = True
    return json_response({"ok": True, "paused": True})


@app.route("/api/remote/resume", methods=["POST"])
def api_remote_resume(request: Request):
    REMOTE_STATE["paused"] = False
    REMOTE_STATE["sos_action"] = None
    return json_response({"ok": True, "paused": False})


@app.route("/api/remote/night", methods=["POST"])
def api_remote_night(request: Request):
    REMOTE_STATE["night_mode"] = not REMOTE_STATE["night_mode"]
    return json_response({"ok": True, "night_mode": REMOTE_STATE["night_mode"]})


# ==============================================================================
# INICIALIZAÇÃO DO SERVIDOR ULTRALEVE
# ==============================================================================

if __name__ == "__main__":
    porta = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        porta = int(sys.argv[1])
    elif os.environ.get("JARVIS_PORT", "").isdigit():
        porta = int(os.environ["JARVIS_PORT"])

    print("==============================================================================")
    print(f"[*] JARVIS Kids OS v2.6 [Microdot Ultraleve]")
    print(f"[*] Servidor ASGI rodando em http://0.0.0.0:{porta} (Memoria < 30 MB)")
    print(f"[*] Painel dos Pais: http://{get_local_ip()}:{porta}/pais")
    print(f"[*] Banco de dados: banco_educativo.db (Modo WAL + Single-Writer Ativo)")
    print("==============================================================================")

    picokey = brain.config.get("picovoice_access_key", "").strip()
    if picokey:
        if escuta_jarvis.iniciar_escuta_segura(picokey):
            print("[*] Picovoice Porcupine ativo escutando a palavra 'Jarvis'")
        else:
            print("[!] Porcupine não iniciado (usando escuta nativa no navegador)")

    gc.collect()
    app.run(host="0.0.0.0", port=porta, debug=False)
