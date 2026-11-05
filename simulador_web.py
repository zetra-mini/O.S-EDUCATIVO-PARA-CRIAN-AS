import os
from flask import Flask, Response, jsonify, render_template, request

from biblioteca_livros import BOOKS
from gestao_tempo_midia import MediaTimeManager
from jarvis_brain import JarvisBrain
from voz_jarvis import VOICE_PROFILES, neural_tts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

brain = JarvisBrain()
media_mgr = MediaTimeManager(brain)


@app.route("/")
def index():
    return render_template("hud_jarvis.html")


@app.route("/api/state", methods=["GET"])
def api_state():
    brain.load_config()
    perm = media_mgr.check_permission()
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
            "books": BOOKS,
            "media_permission": perm,
            "greeting": brain.get_greeting(),
        }
    )


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


@app.route("/api/tts", methods=["POST"])
def api_tts():
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
        headers={"Cache-Control": "no-store"},
    )


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
        if p == "gemini" and key:
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


@app.route("/api/config", methods=["POST"])
def api_save_config():
    data = request.get_json(silent=True) or {}
    for key in (
        "child_name",
        "active_provider",
        "mode",
        "voice_profile",
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
    print("Simulador Web J.A.R.V.I.S. Kids OS v2.2 ativo em http://127.0.0.1:5090")
    app.run(host="127.0.0.1", port=5090, debug=False)
