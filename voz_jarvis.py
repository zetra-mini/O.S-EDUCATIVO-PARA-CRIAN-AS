import io
import math
import os
import platform
import shutil
import struct
import subprocess
import tempfile
import threading
import wave


class JarvisVoice:
    """
    Sintetizador de voz e efeitos sonoros 100% offline e ultraleve (< 5 MB RAM).
    - No Linux (Acer Aspire One 532 / antiX): usa espeak-ng em pt-br e aplay.
    - No Windows (ambiente de teste): usa System.Speech nativo e winsound.
    """

    def __init__(self, on_speaking_change=None):
        self.system = platform.system().lower()
        self.on_speaking_change = on_speaking_change
        self._lock = threading.Lock()
        self._current_proc = None
        self.muted = False

        self.has_espeak_ng = shutil.which("espeak-ng") is not None
        self.has_espeak = shutil.which("espeak") is not None
        self.has_aplay = shutil.which("aplay") is not None

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
        clean_text = text.replace('"', "").replace("'", "").replace("\n", " ").strip()
        if not clean_text:
            return

        threading.Thread(target=self._speak_worker, args=(clean_text,), daemon=True).start()

    def _notify(self, speaking: bool):
        if callable(self.on_speaking_change):
            try:
                self.on_speaking_change(speaking)
            except Exception:
                pass

    def _speak_worker(self, text: str):
        self.stop()
        self._notify(True)
        try:
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
                    # Envelope suave para som agradável infantil
                    fade = min(1.0, (n_samples - i) / max(1, n_samples * 0.25))
                    val = int(16000 * fade * math.sin(2.0 * math.pi * freq_hz * i / sample_rate))
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
