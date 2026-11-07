import os
import socket
from flask import Flask, Response, jsonify, render_template, request, send_file

from biblioteca_livros import BOOKS, library_mgr
from clima_estacoes import weather_mgr
from gestao_tempo_midia import MediaTimeManager
from jarvis_brain import JarvisBrain
from voz_jarvis import VOICE_PROFILES, neural_tts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

brain = JarvisBrain()
media_mgr = MediaTimeManager(brain)

def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

REMOTE_STATE = {
    "paused": False,
    "pause_message": "Hora de recarregar as energias! Vamos fazer uma pausa para comer comidinha gostosa!",
    "night_mode": False
}


@app.route("/")
def index():
    return render_template("hud_jarvis.html")


@app.route("/pais")
def painel_pais():
    return render_template("painel_pais.html")


@app.route("/favicon.ico")
def favicon():
    return Response(status=204)


@app.route("/manifest.json")
def manifest():
    return send_file(os.path.join(BASE_DIR, "static", "manifest.json"), mimetype="application/manifest+json")


@app.route("/sw.js")
def service_worker():
    return send_file(os.path.join(BASE_DIR, "static", "sw.js"), mimetype="application/javascript")


@app.route("/api/clima/atual", methods=["GET"])
def api_clima_atual():
    return jsonify(weather_mgr.obter_clima_atual())


@app.route("/api/clima/estacoes", methods=["GET"])
def api_clima_estacoes():
    return jsonify(weather_mgr.obter_dados_estacoes())


@app.route("/api/state", methods=["GET"])
def api_state():
    brain.load_config()
    perm = media_mgr.check_permission()
    local_ip = get_local_ip()
    return jsonify(
        {
            "config": {
                "child_name": brain.config.get("child_name", "Pequeno Inventor"),
                "active_provider": brain.provider,
                "mode": brain.provider,
                "voice_profile": brain.config.get("voice_profile", "jarvis_antonio"),
                "has_gemini_key": bool(brain.get_effective_gemini_key()),
                "has_openai_key": bool(brain.get_effective_openai_key()),
                "has_groq_key": bool(brain.get_effective_groq_key()),
                "gemini_model": brain.config.get("gemini_model", "gemini-3.8-flash"),
                "openai_model": brain.config.get("openai_model", "gpt-4o-mini"),
                "groq_model": brain.config.get("groq_model", "llama-3.3-70b-versatile"),
                "ollama_url": brain.config.get("ollama_url", "http://127.0.0.1:11434"),
                "ollama_model": brain.config.get("ollama_model", "qwen2.5:0.5b"),
                "voice_enabled": brain.config.get("voice_enabled", True),
                "media_start_time": brain.config.get("media_start_time", "16:00"),
                "media_end_time": brain.config.get("media_end_time", "17:00"),
                "media_daily_minutes": brain.config.get("media_daily_minutes", 25),
                "require_book_before_media": brain.config.get(
                    "require_book_before_media", True
                ),
                "netflix_url": brain.config.get("netflix_url", "https://www.netflix.com/Kids"),
                "youtube_url": brain.config.get("youtube_url", "https://www.youtubekids.com"),
            },
            "voice_profiles": {
                k: v["label"] for k, v in VOICE_PROFILES.items()
            },
            "books_read_today": media_mgr.get_books_read_today(),
            "books": library_mgr.obter_todos_os_livros(),
            "media_permission": perm,
            "greeting": brain.get_greeting(),
            "local_ip": local_ip,
            "remote_url": f"http://{local_ip}:5090/pais",
            "remote_paused": REMOTE_STATE["paused"],
            "pause_message": REMOTE_STATE["pause_message"],
            "night_mode": REMOTE_STATE["night_mode"],
            "clima": weather_mgr.obter_clima_atual(),
        }
    )


@app.route("/api/remote/pause", methods=["POST"])
def api_remote_pause():
    data = request.get_json(silent=True) or {}
    msg = data.get("message", "Hora de recarregar as energias! Vamos fazer uma pausa para comer comidinha gostosa!")
    REMOTE_STATE["paused"] = True
    REMOTE_STATE["pause_message"] = msg
    return jsonify({"ok": True, "paused": True, "message": msg})


@app.route("/api/remote/resume", methods=["POST"])
def api_remote_resume():
    REMOTE_STATE["paused"] = False
    return jsonify({"ok": True, "paused": False})


@app.route("/api/remote/night", methods=["POST"])
def api_remote_night():
    data = request.get_json(silent=True) or {}
    enable = data.get("enable")
    if enable is None:
        REMOTE_STATE["night_mode"] = not REMOTE_STATE["night_mode"]
    else:
        REMOTE_STATE["night_mode"] = bool(enable)
    return jsonify({"ok": True, "night_mode": REMOTE_STATE["night_mode"]})


@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json(silent=True) or {}
    topic = data.get("topic")
    question = data.get("question")
    if topic:
        res = brain.ask_topic_detailed(topic)
    elif question:
        res = brain.ask_custom_detailed(question)
    else:
        res = {
            "reply": brain.get_greeting(),
            "engine_used": brain.provider,
        }
    return jsonify(res)


def transcribe_audio_bytes(audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
    """Converte áudio gravado do microfone em texto em Português do Brasil."""
    if not audio_bytes or len(audio_bytes) < 400:
        return ""

    # Camada 1: Se chave do Gemini estiver configurada, usa transcrição do Gemini
    gemini_key = brain.get_effective_gemini_key()
    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type or "audio/webm"),
                    "Transcreva com exatidão o que foi falado em português do Brasil neste áudio. Retorne apenas as palavras ouvidas sem introdução."
                ]
            )
            txt = (res.text or "").strip()
            if txt:
                return txt
        except Exception as e:
            print(f"Gemini STT notice: {e}")

    # Camada 2: SpeechRecognition com Google STT nativo em pt-BR (gratuito)
    try:
        import io
        from pydub import AudioSegment
        import speech_recognition as sr

        seg = AudioSegment.from_file(io.BytesIO(audio_bytes))
        seg = seg.set_channels(1).set_frame_rate(16000)
        wav_buf = io.BytesIO()
        seg.export(wav_buf, format="wav")
        wav_buf.seek(0)

        r = sr.Recognizer()
        with sr.AudioFile(wav_buf) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="pt-BR")
            return text.strip()
    except Exception as e:
        print(f"SpeechRecognition STT notice: {e}")

    return ""


@app.route("/api/stt", methods=["POST"])
def api_stt():
    audio_bytes = request.get_data()
    mime = request.content_type or "audio/webm"
    text = transcribe_audio_bytes(audio_bytes, mime)
    if text:
        return jsonify({"ok": True, "text": text})
    return jsonify({"ok": False, "error": "Não foi possível transcrever o áudio", "text": ""})


@app.route("/api/tts", methods=["POST"])
def api_tts():
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        if not text:
            return Response(status=204)

        profile_key = data.get("voice_profile") or brain.config.get(
            "voice_profile", "jarvis_antonio"
        )
        override_key = (data.get("gemini_api_key") or "").strip()
        effective_key = override_key or brain.get_effective_gemini_key()

        audio_bytes, mime_type = neural_tts.synthesize(text, profile_key, effective_key)
        if not audio_bytes:
            return Response(status=204)

        return Response(
            audio_bytes,
            mimetype=mime_type,
            headers={
                "Cache-Control": "public, max-age=604800, immutable",
                "X-Audio-Cache": "hit" if profile_key in str(neural_tts._cache) else "miss"
            },
        )
    except Exception as e:
        print(f"Aviso TTS: {e}")
        return Response(status=204)


@app.route("/api/provider/test", methods=["POST"])
def api_provider_test():
    data = request.get_json(silent=True) or {}
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
        elif p == "ollama" and url:
            brain.config["ollama_url"] = url
        brain.config["active_provider"] = p
        brain.config["mode"] = p
        brain.save_config()

    return jsonify({"ok": ok, "message": msg, "provider": provider})


@app.route("/api/gemini/test", methods=["POST"])
def api_gemini_test():
    data = request.get_json(silent=True) or {}
    candidate_key = (data.get("gemini_api_key") or "").strip()
    ok, msg = brain.test_provider("gemini", candidate_key)
    if ok and candidate_key:
        brain.config["gemini_api_key"] = candidate_key
        brain.config["active_provider"] = "gemini"
        brain.config["mode"] = "gemini"
        brain.save_config()
    return jsonify({"ok": ok, "message": msg, "has_gemini_key": bool(brain.get_effective_gemini_key())})


@app.route("/api/gemini/reset", methods=["POST"])
def api_gemini_reset():
    brain.reset_conversation()
    return jsonify({"ok": True})


@app.route("/api/book-finished", methods=["POST"])
def api_book_finished():
    data = request.get_json(silent=True) or {}
    book_id = data.get("book_id", "livro")
    total = media_mgr.record_book_read(book_id)
    return jsonify({"ok": True, "books_read_today": total})


@app.route("/api/livros", methods=["GET"])
def api_livros_listar():
    return jsonify({"ok": True, "livros": library_mgr.obter_todos_os_livros()})


@app.route("/api/livros/gerar", methods=["POST"])
def api_livros_gerar():
    data = request.get_json(silent=True) or {}
    tema = data.get("tema", "Resiliência")
    child_name = data.get("child_name") or brain.config.get("child_name", "Kaleo")
    novo = library_mgr.gerar_historia_ia(tema=tema, child_name=child_name)
    return jsonify({"ok": True, "livro": novo})


@app.route("/api/livros/criar", methods=["POST"])
def api_livros_criar():
    data = request.get_json(silent=True) or {}
    sucesso = library_mgr.salvar_novo_livro(data)
    return jsonify({"ok": sucesso})


@app.route("/api/livros/excluir", methods=["POST"])
def api_livros_excluir():
    data = request.get_json(silent=True) or {}
    book_id = data.get("id", "")
    sucesso = library_mgr.excluir_livro_dinamico(book_id)
    return jsonify({"ok": sucesso})


@app.route("/api/media/tick", methods=["POST"])
def api_media_tick():
    data = request.get_json(silent=True) or {}
    secs = int(data.get("seconds", 5))
    remaining = media_mgr.add_watched_seconds(secs)
    return jsonify({"remaining_sec": remaining})


@app.route("/api/media/bonus", methods=["POST"])
def api_media_bonus():
    data = request.get_json(silent=True) or {}
    mins = int(data.get("minutes", 15))
    media_mgr.grant_bonus_minutes(mins)
    return jsonify({"ok": True, "permission": media_mgr.check_permission()})


@app.route("/api/media/close", methods=["POST"])
def api_media_close():
    media_mgr.close_streaming()
    return jsonify({"ok": True, "status": "closed"})


@app.route("/api/config", methods=["POST"])
def api_save_config():
    data = request.get_json(silent=True) or {}
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
    ):
        if key in data:
            brain.config[key] = data[key]

    if "gemini_api_key" in data and data["gemini_api_key"].strip():
        brain.config["gemini_api_key"] = data["gemini_api_key"].strip()
    if "openai_api_key" in data and data["openai_api_key"].strip():
        brain.config["openai_api_key"] = data["openai_api_key"].strip()
    if "groq_api_key" in data and data["groq_api_key"].strip():
        brain.config["groq_api_key"] = data["groq_api_key"].strip()

    if data.get("active_provider"):
        brain.config["mode"] = data["active_provider"]

    brain.reset_conversation()
    brain.save_config()
    return jsonify(
        {
            "ok": True,
            "permission": media_mgr.check_permission(),
            "active_provider": brain.provider,
        }
    )


if __name__ == "__main__":
    import time
    print(f"Simulador Web J.A.R.V.I.S. Kids OS v2.2 ativo em http://127.0.0.1:5090 e na rede http://{get_local_ip()}:5090/pais")
    while True:
        try:
            app.run(host="0.0.0.0", port=5090, debug=False, threaded=True)
        except KeyboardInterrupt:
            break
        except (Exception, BaseException) as e:
            print(f"Servidor reiniciando após sinal/erro: {e}")
        time.sleep(1)
