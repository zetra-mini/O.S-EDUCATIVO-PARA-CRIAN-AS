"""
Módulo de Detecção da Palavra-Chave 'Jarvis' (Wake Word) e Vigilância de Áudio Leve.
Projetado para rodar em thread separada sem consumir CPU excessiva do Intel Atom:
1. Suporte a Picovoice Porcupine (se chave configurada).
2. Fallback desacoplado para escuta Web (Web Speech API no navegador) e eventos leves.
3. Notificação instantânea para o frontend ao detectar o chamado do Kaleu.
"""

import threading
import time
import uuid
from typing import Callable, Optional

# Estado global de eventos de Wake
_on_wake_callback: Optional[Callable] = None
_listening_thread: Optional[threading.Thread] = None
_is_running = False

_last_wake_event = {
    "id": "",
    "timestamp": 0.0,
    "origem": "none",
}
_wake_lock = threading.Lock()


def configurar_callback_wake(callback: Callable):
    global _on_wake_callback
    _on_wake_callback = callback


def disparar_wake(origem: str = "manual") -> dict:
    """Dispara um evento de ativação 'Jarvis!' e notifica os ouvintes."""
    global _last_wake_event
    with _wake_lock:
        evt = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "origem": origem,
        }
        _last_wake_event = evt

    if _on_wake_callback:
        try:
            _on_wake_callback(evt)
        except Exception:
            pass
    return evt


def obter_ultimo_wake(since_timestamp: float = 0.0) -> dict:
    """Retorna o último evento de wake se ocorreu após since_timestamp."""
    with _wake_lock:
        if _last_wake_event["timestamp"] > since_timestamp:
            return {"wake": True, "event": dict(_last_wake_event)}
        return {"wake": False, "timestamp": _last_wake_event["timestamp"]}


def iniciar_escuta_segura(access_key: str = "") -> bool:
    """Inicia thread de escuta sem travar o processador Atom N450."""
    global _is_running, _listening_thread
    if _is_running:
        return True

    if not access_key:
        # Sem chave Porcupine, o sistema delega para o Web Speech API nativo no navegador (zero CPU em Python)
        return False

    try:
        import pvporcupine
        import pyaudio

        porcupine = pvporcupine.create(access_key=access_key, keywords=["jarvis"])
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )

        def _loop():
            global _is_running
            _is_running = True
            try:
                while _is_running:
                    pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                    import struct
                    pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)
                    idx = porcupine.process(pcm_unpacked)
                    if idx >= 0:
                        disparar_wake(origem="porcupine")
            except Exception:
                pass
            finally:
                audio_stream.close()
                pa.terminate()
                porcupine.delete()
                _is_running = False

        _listening_thread = threading.Thread(target=_loop, daemon=True, name="WakeWordThread")
        _listening_thread.start()
        return True
    except Exception:
        # Se pyaudio ou porcupine não estiverem instalados, fallback transparente para o navegador
        return False


def parar_escuta():
    global _is_running
    _is_running = False
