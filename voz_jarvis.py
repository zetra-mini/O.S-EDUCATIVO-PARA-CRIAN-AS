import asyncio
import base64
from collections import OrderedDict
import io
import math
import os
import platform
import re
import shutil
import struct
import subprocess
import tempfile
import threading
import wave

# Perfis de voz neural disponíveis para o JARVIS Kids OS
VOICE_PROFILES = {
    "jarvis_antonio": {
        "label": "J.A.R.V.I.S. Neural (Antonio PT-BR — Masculino Amigável)",
        "engine": "edge",
        "voice": "pt-BR-AntonioNeural",
        "rate": "+4%",
        "pitch": "+2Hz",
    },
    "amiga_thalita": {
        "label": "Amiga Gemini Neural (Thalita PT-BR — Expressiva e Calorosa)",
        "engine": "edge",
        "voice": "pt-BR-ThalitaMultilingualNeural",
        "rate": "+2%",
        "pitch": "+0Hz",
    },
    "amiga_francisca": {
        "label": "Contadora de Histórias (Francisca PT-BR — Voz Doce e Calma)",
        "engine": "edge",
        "voice": "pt-BR-FranciscaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
    },
    "gemini_puck": {
        "label": "Google Gemini 3.8 Studio TTS — Puck (Alegre / Requer Chave Gemini)",
        "engine": "gemini",
        "voice": "Puck",
        "fallback_edge": "pt-BR-AntonioNeural",
    },
    "gemini_sulafat": {
        "label": "Google Gemini 3.8 Studio TTS — Sulafat (Acolhedora / Requer Chave Gemini)",
        "engine": "gemini",
        "voice": "Sulafat",
        "fallback_edge": "pt-BR-ThalitaMultilingualNeural",
    },
}


def clean_text_for_speech(text: str) -> str:
    """Remove emojis, símbolos markdown e excesso de espaços para leitura limpa e natural."""
    if not text:
        return ""
    # Remove blocos markdown simples (*, _, #, `, ~)
    cleaned = re.sub(r"[*_#`~>|]", " ", text)
    # Remove emojis e pictogramas mantendo acentuação completa do Português
    cleaned = re.sub(
        r"[\U00010000-\U0010ffff\u2600-\u27bf\u2300-\u23ff\u2b50\u25a0-\u25ff]",
        " ",
        cleaned,
    )
    cleaned = cleaned.replace("J.A.R.V.I.S.", "Járvis").replace("JARVIS", "Járvis")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


class NeuralTTSService:
    """
    Serviço híbrido de Voz Neural em Português do Brasil com cache em memória:
    1. Google Gemini 3.8 TTS (gemini-3.8-flash-lite-tts) via SDK oficial google-genai.
    2. Voz Neural PT-BR gratuita (edge-tts: AntonioNeural / ThalitaMultilingualNeural / FranciscaNeural).
    """

    def __init__(self, max_cache: int = 48):
        self._cache = OrderedDict()
        self._max_cache = max_cache
        self._lock = threading.Lock()

    def synthesize(
        self, text: str, profile_key: str = "jarvis_antonio", gemini_api_key: str = ""
    ) -> tuple[bytes, str]:
        """Retorna (audio_bytes, mime_type) ou (b'', '') se sem internet."""
        clean = clean_text_for_speech(text)
        if not clean:
            return b"", ""

        profile = VOICE_PROFILES.get(profile_key, VOICE_PROFILES["jarvis_antonio"])
        engine = profile["engine"]
        effective_key = (
            gemini_api_key.strip()
            or os.environ.get("GEMINI_API_KEY", "").strip()
            or os.environ.get("GOOGLE_API_KEY", "").strip()
        )

        cache_id = f"{profile_key}:{bool(effective_key)}:{clean}"
        with self._lock:
            if cache_id in self._cache:
                self._cache.move_to_end(cache_id)
                return self._cache[cache_id]

        audio_bytes = b""
        mime_type = ""

        # Camada 1: Google Gemini 3.8 Studio TTS quando selecionado e com chave ativa
        if engine == "gemini" and effective_key:
            audio_bytes, mime_type = self._synthesize_gemini_tts(
                clean, profile["voice"], effective_key
            )

        # Camada 2: Voz Neural PT-BR gratuita (edge-tts) — funciona sem chave de API!
        if not audio_bytes:
            edge_voice = profile.get("fallback_edge") or profile.get(
                "voice", "pt-BR-AntonioNeural"
            )
            rate = profile.get("rate", "+2%")
            pitch = profile.get("pitch", "+0Hz")
            audio_bytes, mime_type = self._synthesize_edge_tts(
                clean, edge_voice, rate, pitch
            )

        if audio_bytes:
            with self._lock:
                self._cache[cache_id] = (audio_bytes, mime_type)
                if len(self._cache) > self._max_cache:
                    self._cache.popitem(last=False)

        return audio_bytes, mime_type

    def _synthesize_gemini_tts(
        self, text: str, voice_name: str, api_key: str
    ) -> tuple[bytes, str]:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            interaction = client.interactions.create(
                model="gemini-3.8-flash-lite-tts",
                input=[
                    {
                        "type": "user_input",
                        "content": [
                            {
                                "type": "text",
                                "text": text,
                                "annotations": [
                                    {
                                        "type": "speech_metadata",
                                        "style": "warm, cheerful, caring Brazilian Portuguese friend talking to a 4-year-old child",
                                    }
                                ],
                            }
                        ],
                    }
                ],
                response_format={"type": "audio"},
                generation_config={"speech_config": [{"voice": voice_name}]},
            )
            if getattr(interaction, "output_audio", None) and interaction.output_audio.data:
                raw_wav = base64.b64decode(interaction.output_audio.data)
                return raw_wav, "audio/wav"
        except Exception:
            pass
        return b"", ""

    def _synthesize_edge_tts(
        self, text: str, voice_name: str, rate: str, pitch: str
    ) -> tuple[bytes, str]:
        try:
            import edge_tts

            async def _run():
                comm = edge_tts.Communicate(text, voice_name, rate=rate, pitch=pitch)
                buf = bytearray()
                async for chunk in comm.stream():
                    if chunk.get("type") == "audio":
                        buf.extend(chunk["data"])
                return bytes(buf)

            mp3_bytes = asyncio.run(_run())
            if mp3_bytes:
                return mp3_bytes, "audio/mpeg"
        except Exception:
            pass
        return b"", ""


neural_tts = NeuralTTSService()


class JarvisVoice:
    """
    Sintetizador de voz e efeitos sonoros para o Desktop (Tkinter):
    - Quando conectado e player leve disponível (ffplay / mpg123), usa Voz Neural PT-BR!
    - Fallback instantâneo 100% offline (< 5 MB RAM):
      * No Linux (Acer Aspire One 532 / antiX): usa espeak-ng em pt-br e aplay.
      * No Windows: usa System.Speech nativo e winsound.
    """

    def __init__(self, on_speaking_change=None, config_getter=None):
        self.system = platform.system().lower()
        self.on_speaking_change = on_speaking_change
        self.config_getter = config_getter
        self._lock = threading.Lock()
        self._current_proc = None
        self.muted = False

        self.has_espeak_ng = shutil.which("espeak-ng") is not None
        self.has_espeak = shutil.which("espeak") is not None
        self.has_aplay = shutil.which("aplay") is not None
        self.has_mpg123 = shutil.which("mpg123") is not None
        self.has_ffplay = shutil.which("ffplay") is not None

    def stop(self):
        with self._lock:
            if self._current_proc and self._current_proc.poll() is None:
                try:
                    self._current_proc.terminate()
                except Exception:
                    pass
            self._current_proc = None

    def speak(self, text: str):
        if self.muted or not text:
            return
        clean_text = clean_text_for_speech(text).replace("'", "").replace('"', "")
        if not clean_text:
            return

        threading.Thread(
            target=self._speak_worker, args=(clean_text,), daemon=True
        ).start()

    def _notify(self, speaking: bool):
        if callable(self.on_speaking_change):
            try:
                self.on_speaking_change(speaking)
            except Exception:
                pass

    def _try_play_neural_desktop(self, text: str) -> bool:
        cfg = self.config_getter() if callable(self.config_getter) else {}
        if cfg.get("mode") == "offline" and not cfg.get("prefer_neural_voice", True):
            return False

        profile_key = cfg.get("voice_profile", "jarvis_antonio")
        gemini_key = cfg.get("gemini_api_key", "") or cfg.get("cloud_api_key", "")
        audio_bytes, mime = neural_tts.synthesize(text, profile_key, gemini_key)
        if not audio_bytes:
            return False

        if mime == "audio/wav":
            if self.system == "windows":
                import winsound

                winsound.PlaySound(audio_bytes, winsound.SND_MEMORY)
                return True
            elif self.system == "linux" and self.has_aplay:
                return self._play_temp_file(audio_bytes, ".wav", ["aplay", "-q"])

        if mime == "audio/mpeg":
            if self.has_mpg123:
                return self._play_temp_file(audio_bytes, ".mp3", ["mpg123", "-q"])
            if self.has_ffplay:
                return self._play_temp_file(
                    audio_bytes,
                    ".mp3",
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
                )
        return False

    def _play_temp_file(self, data: bytes, suffix: str, base_cmd: list[str]) -> bool:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(data)
                tmp_path = tmp.name
            with self._lock:
                self._current_proc = subprocess.Popen(
                    [*base_cmd, tmp_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            self._current_proc.wait()
            return True
        except Exception:
            return False
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def _speak_worker(self, text: str):
        self.stop()
        self._notify(True)
        try:
            if self._try_play_neural_desktop(text):
                return

            if self.system == "linux":
                cmd = None
                if self.has_espeak_ng:
                    cmd = ["espeak-ng", "-v", "pt-br", "-s", "148", "-p", "48", text]
                elif self.has_espeak:
                    cmd = ["espeak", "-v", "pt", "-s", "145", "-p", "48", text]

                if cmd:
                    with self._lock:
                        self._current_proc = subprocess.Popen(
                            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                    self._current_proc.wait()
            elif self.system == "windows":
                ps_script = (
                    "Add-Type -AssemblyName System.Speech; "
                    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    "$s.Rate = 0; "
                    f"$s.Speak('{text}');"
                )
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                with self._lock:
                    self._current_proc = subprocess.Popen(
                        ["powershell", "-NoProfile", "-Command", ps_script],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        startupinfo=startupinfo,
                    )
                self._current_proc.wait()
        except Exception:
            pass
        finally:
            self._notify(False)

    def play_tone(self, freq_hz: int = 523, duration_ms: int = 180):
        """Toca notas musicais sintetizadas em memória (zero arquivos externos)."""
        if self.muted:
            return
        threading.Thread(
            target=self._tone_worker, args=(freq_hz, duration_ms), daemon=True
        ).start()

    def _tone_worker(self, freq_hz: int, duration_ms: int):
        try:
            sample_rate = 22050
            n_samples = int(sample_rate * (duration_ms / 1000.0))
            buf = io.BytesIO()
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                frames = bytearray()
                for i in range(n_samples):
                    fade = min(1.0, (n_samples - i) / max(1, n_samples * 0.25))
                    val = int(
                        16000 * fade * math.sin(2.0 * math.pi * freq_hz * i / sample_rate)
                    )
                    frames.extend(struct.pack("<h", val))
                wf.writeframes(bytes(frames))

            wav_bytes = buf.getvalue()

            if self.system == "windows":
                import winsound

                winsound.PlaySound(wav_bytes, winsound.SND_MEMORY)
            elif self.system == "linux" and self.has_aplay:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(wav_bytes)
                    tmp_path = tmp.name
                try:
                    subprocess.run(
                        ["aplay", "-q", tmp_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=3,
                    )
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
        except Exception:
            pass
