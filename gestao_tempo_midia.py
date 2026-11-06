import datetime
import json
import os
import platform
import shutil
import subprocess
import tkinter as tk
import webbrowser

from banco_dados import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USAGE_PATH = os.path.join(BASE_DIR, "uso_diario.json")


class MediaTimeManager:
    """
    Controlador pedagógico de tempo para Netflix & YouTube Kids ('Tudo tem o seu tempo'):
    - Persiste dados no SQLite WAL com Single-Writer para zero conflito em disco.
    - Só libera dentro da janela de horário definida pelos pais (ex: 16:00 às 17:00) ou se houver bônus ativo.
    - Pode exigir 1 livro lido no dia antes de liberar o vídeo (hábito de leitura em 1º lugar!).
    - Monitora os minutos restantes, faz aviso gentil faltando 2 minutos e, ao terminar,
      fecha o vídeo e direciona a criança para uma nova atividade educativa!
    """

    def __init__(self, brain, database=db):
        self.brain = brain
        self.db = database
        self.browser_proc = None
        self.session_active = False
        self.warned_two_min = False

    def _today_key(self) -> str:
        return datetime.date.today().isoformat()

    def _load_usage(self) -> dict:
        today = self._today_key()
        row = self.db.consultar_um(
            "SELECT data_iso, segundos_assistidos, livros_lidos, livros_ids_json, minutos_bonus FROM uso_tempo_midia WHERE data_iso = ?;",
            (today,),
        )
        if row:
            try:
                b_ids = json.loads(row["livros_ids_json"])
            except Exception:
                b_ids = []
            return {
                "date": today,
                "seconds_watched": int(row["segundos_assistidos"]),
                "books_read": int(row["livros_lidos"]),
                "book_ids": b_ids,
                "bonus_minutes": int(row["minutos_bonus"]),
            }

        # Inicializa o dia no SQLite
        self.db.executar_escrita(
            """
            INSERT OR IGNORE INTO uso_tempo_midia (data_iso, segundos_assistidos, livros_lidos, livros_ids_json, minutos_bonus)
            VALUES (?, 0, 0, '[]', 0);
            """,
            (today,),
        )
        return {"date": today, "seconds_watched": 0, "books_read": 0, "book_ids": [], "bonus_minutes": 0}

    def _save_usage(self, data: dict):
        today = self._today_key()
        try:
            b_json = json.dumps(data.get("book_ids", []), ensure_ascii=False)
            self.db.executar_escrita(
                """
                INSERT INTO uso_tempo_midia (data_iso, segundos_assistidos, livros_lidos, livros_ids_json, minutos_bonus, atualizado_em)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(data_iso) DO UPDATE SET
                    segundos_assistidos = excluded.segundos_assistidos,
                    livros_lidos = excluded.livros_lidos,
                    livros_ids_json = excluded.livros_ids_json,
                    minutos_bonus = excluded.minutos_bonus,
                    atualizado_em = CURRENT_TIMESTAMP;
                """,
                (
                    today,
                    int(data.get("seconds_watched", 0)),
                    int(data.get("books_read", 0)),
                    b_json,
                    int(data.get("bonus_minutes", 0)),
                ),
            )
        except Exception:
            pass

    def record_book_read(self, book_id: str) -> int:
        data = self._load_usage()
        data["books_read"] = int(data.get("books_read", 0)) + 1
        if book_id not in data.get("book_ids", []):
            data.setdefault("book_ids", []).append(book_id)
        self._save_usage(data)
        return data["books_read"]

    def get_books_read_today(self) -> int:
        return int(self._load_usage().get("books_read", 0))

    def grant_bonus_minutes(self, minutes: int = 15):
        data = self._load_usage()
        data["bonus_minutes"] = int(data.get("bonus_minutes", 0)) + minutes
        self._save_usage(data)

    def check_permission(self) -> dict:
        """Retorna se o Cinema está liberado agora, quantos segundos restam ou o motivo pedagógico."""
        cfg = self.brain.config
        start_str = cfg.get("media_start_time", "16:00")
        end_str = cfg.get("media_end_time", "17:00")
        daily_limit_min = int(cfg.get("media_daily_minutes", 25))
        require_book = bool(cfg.get("require_book_before_media", True))

        usage = self._load_usage()
        bonus_min = int(usage.get("bonus_minutes", 0))
        books_read = int(usage.get("books_read", 0))
        watched_sec = int(usage.get("seconds_watched", 0))

        # 1. Regra de Hábito de Leitura Principal
        if require_book and books_read < 1 and bonus_min == 0:
            return {
                "allowed": False,
                "reason": "need_book",
                "message": (
                    f"{self.brain.name}, antes do Cinema Stark temos nossa missão principal de herói: "
                    f"ler pelo menos um livrinho hoje na Biblioteca! Vamos escolher uma história juntos?"
                ),
            }

        # 2. Verificar saldo de minutos do dia
        total_allowed_sec = (daily_limit_min + bonus_min) * 60
        remaining_sec = total_allowed_sec - watched_sec
        if remaining_sec <= 0:
            return {
                "allowed": False,
                "reason": "time_up",
                "message": (
                    f"{self.brain.name}, o nosso tempo de vídeos de hoje já terminou! "
                    f"Tudo tem a sua hora. Agora é hora de criar um desenho, fazer música ou ler um livro!"
                ),
            }

        # 3. Verificar janela de relógio (a menos que os pais tenham liberado bônus imediato)
        now = datetime.datetime.now().time()
        try:
            sh, sm = [int(x) for x in start_str.split(":")]
            eh, em = [int(x) for x in end_str.split(":")]
            t_start = datetime.time(sh, sm)
            t_end = datetime.time(eh, em)
            in_window = (t_start <= now <= t_end) if t_start <= t_end else (now >= t_start or now <= t_end)
        except Exception:
            in_window = True

        if not in_window and bonus_min == 0:
            return {
                "allowed": False,
                "reason": "outside_schedule",
                "schedule": f"{start_str} às {end_str}",
                "message": (
                    f"{self.brain.name}, cada coisa tem o seu tempo especial! "
                    f"O horário do Cinema Stark é das {start_str} até as {end_str}. "
                    f"Enquanto não chega a hora, vamos brincar na Biblioteca de Livros ou na Academia Stark!"
                ),
            }

        return {
            "allowed": True,
            "remaining_sec": remaining_sec,
            "schedule": f"{start_str} às {end_str}",
        }

    def add_watched_seconds(self, seconds: int) -> int:
        usage = self._load_usage()
        usage["seconds_watched"] = int(usage.get("seconds_watched", 0)) + seconds
        self._save_usage(usage)
        cfg = self.brain.config
        total_allowed = (int(cfg.get("media_daily_minutes", 25)) + int(usage.get("bonus_minutes", 0))) * 60
        return max(0, total_allowed - usage["seconds_watched"])

    def launch_streaming(self, url: str):
        """Abre Netflix Kids ou YouTube Kids em janela controlada e leve para RAM."""
        self.close_streaming()
        sys_name = platform.system().lower()

        if sys_name == "linux":
            browsers = [
                ["chromium", f"--app={url}", "--start-fullscreen", "--process-per-site"],
                ["chromium-browser", f"--app={url}", "--start-fullscreen", "--process-per-site"],
                ["firefox-esr", "--kiosk", url],
                ["firefox", "--kiosk", url],
                ["falkon", "-f", url],
            ]
            for cmd in browsers:
                if shutil.which(cmd[0]):
                    self.browser_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.session_active = True
                    return
        elif sys_name == "windows":
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ]
            for ep in edge_paths:
                if os.path.exists(ep):
                    self.browser_proc = subprocess.Popen([ep, f"--app={url}"])
                    self.session_active = True
                    return

        webbrowser.open(url)
        self.session_active = True

    def close_streaming(self):
        self.session_active = False
        if self.browser_proc and self.browser_proc.poll() is None:
            try:
                self.browser_proc.terminate()
                self.browser_proc.wait(timeout=2)
            except Exception:
                try:
                    self.browser_proc.kill()
                except Exception:
                    pass
        self.browser_proc = None
        if platform.system().lower() == "linux":
            try:
                subprocess.run(
                    ["pkill", "-f", "firefox|chromium|falkon"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass


class CinemaStarkModal:
    """Tela pedagógica do Cinema Stark (YouTube Kids & Netflix Kids com Relógio Educativo)."""

    def __init__(self, os_app):
        self.os_app = os_app
        self.mgr = os_app.media_mgr
        self.win = os_app._create_activity_window("🎬 CINEMA STARK — TUDO TEM O SEU TEMPO")
        self.timer_job = None

        self.win.protocol("WM_DELETE_WINDOW", self._on_close)
        self.body = tk.Frame(self.win, bg=os_app.BG_DARK)
        self.body.pack(fill="both", expand=True, padx=24, pady=16)

        self._render_state()

    def _on_close(self):
        if self.timer_job:
            self.win.after_cancel(self.timer_job)
        self.mgr.close_streaming()
        self.win.destroy()

    def _render_state(self):
        for w in self.body.winfo_children():
            w.destroy()

        perm = self.mgr.check_permission()

        if not perm["allowed"]:
            # Mostra tela pedagógica gentil e botão grande para a atividade sugerida!
            box = tk.Frame(
                self.body, bg="#0f172a", highlightthickness=3, highlightbackground="#f59e0b", padx=28, pady=28
            )
            box.pack(expand=True, fill="both", pady=12)

            icon = "📚" if perm["reason"] == "need_book" else "⏰"
            tk.Label(box, text=icon, font=("Arial", 54), bg="#0f172a", fg="#facc15").pack(pady=6)

            tk.Label(
                box,
                text=perm["message"],
                fg="#ffffff",
                bg="#0f172a",
                font=("Arial", 18, "bold"),
                wraplength=820,
                justify="center",
            ).pack(pady=14)

            btn_row = tk.Frame(box, bg="#0f172a")
            btn_row.pack(pady=14)

            tk.Button(
                btn_row,
                text="📚 IR PARA A BIBLIOTECA DE LIVROS!",
                bg="#10b981",
                fg="#ffffff",
                font=("Arial", 16, "bold"),
                padx=22,
                pady=12,
                cursor="hand2",
                command=lambda: (self._on_close(), self.os_app._open_book_library()),
            ).pack(side="left", padx=10)

            tk.Button(
                btn_row,
                text="🎨 IR PARA PINTURA MÁGICA",
                bg="#f97316",
                fg="#ffffff",
                font=("Arial", 15, "bold"),
                padx=20,
                pady=12,
                cursor="hand2",
                command=lambda: (self._on_close(), self.os_app._launch_tuxpaint_or_draw()),
            ).pack(side="left", padx=10)

            self.os_app.say(perm["message"])
            return

        # Horário liberado! Mostra contador e botões do YouTube Kids e Netflix Kids
        rem_min = max(1, perm["remaining_sec"] // 60)
        msg = (
            f"Horário do Cinema liberado, {self.os_app.brain.name}! "
            f"Você tem {rem_min} minutos hoje. Quando o relógio terminar, faremos outra atividade divertida!"
        )
        self.os_app.say(msg)

        self.timer_lbl = tk.Label(
            self.body,
            text=f"⏱ Tempo disponível hoje: {perm['remaining_sec'] // 60:02d}:{perm['remaining_sec'] % 60:02d}",
            fg="#34d399",
            bg=self.os_app.BG_DARK,
            font=("Arial", 24, "bold"),
        )
        self.timer_lbl.pack(pady=(8, 16))

        cards = tk.Frame(self.body, bg=self.os_app.BG_DARK)
        cards.pack(expand=True, fill="both", pady=10)
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)
        cards.rowconfigure(0, weight=1)

        yt_btn = tk.Button(
            cards,
            text="▶ YOUTUBE KIDS\n\n(Desenhos Educativos)",
            bg="#dc2626",
            fg="#ffffff",
            font=("Arial", 22, "bold"),
            relief="raised",
            bd=6,
            cursor="hand2",
            command=lambda: self._start_watching("https://www.youtubekids.com", "YouTube Kids"),
        )
        yt_btn.grid(row=0, column=0, sticky="nsew", padx=14, pady=12)

        nf_btn = tk.Button(
            cards,
            text="🎬 NETFLIX KIDS\n\n(Filmes e Séries Infantis)",
            bg="#991b1b",
            fg="#ffffff",
            font=("Arial", 22, "bold"),
            relief="raised",
            bd=6,
            cursor="hand2",
            command=lambda: self._start_watching("https://www.netflix.com/Kids", "Netflix Infantil"),
        )
        nf_btn.grid(row=0, column=1, sticky="nsew", padx=14, pady=12)

        tk.Button(
            self.body,
            text="⏹ Parar Vídeo e Guardar Meu Tempo para Depois",
            bg="#334155",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
            padx=18,
            pady=10,
            command=self._stop_watching_voluntarily,
        ).pack(pady=8)

    def _start_watching(self, url: str, service_name: str):
        self.mgr.warned_two_min = False
        self.os_app.say(f"Abrindo {service_name}! Eu aviso você dois minutinhos antes de acabar o tempo!")
        self.mgr.launch_streaming(url)
        if self.timer_job:
            self.win.after_cancel(self.timer_job)
        self._tick_timer()

    def _tick_timer(self):
        if not self.mgr.session_active:
            return

        remaining = self.mgr.add_watched_seconds(5)
        mins, secs = divmod(remaining, 60)
        if self.timer_lbl.winfo_exists():
            self.timer_lbl.configure(text=f"⏱ Tempo restante hoje: {mins:02d}:{secs:02d}")

        # Aviso amigo faltando 2 minutos (120s) para preparar emocionalmente a criança!
        if 115 <= remaining <= 120 and not self.mgr.warned_two_min:
            self.mgr.warned_two_min = True
            self.os_app.say(
                f"Atenção, {self.os_app.brain.name}! Faltam dois minutinhos para terminar o vídeo. Já vamos nos despedir do desenho!"
            )

        if remaining <= 0:
            self._finish_time_and_redirect()
            return

        self.timer_job = self.win.after(5000, self._tick_timer)

    def _stop_watching_voluntarily(self):
        if self.mgr.session_active:
            self.mgr.close_streaming()
            self.os_app._add_star()
            self.os_app.say(
                f"Uau, {self.os_app.brain.name}! Você guardou seu tempo antes mesmo do relógio apitar! Ganhou uma estrela de autocontrole!"
            )

    def _finish_time_and_redirect(self):
        self.mgr.close_streaming()
        if self.win.winfo_exists():
            self.win.destroy()
        self.os_app.root.lift()
        self.os_app._add_star()
        self.os_app.say(
            f"O tempo de vídeo terminou, {self.os_app.brain.name}! Parabéns por respeitar o combinado! "
            f"Agora o Járvis preparou uma nova missão especial para você na Biblioteca de Livros!"
        )
        self.os_app.root.after(2500, self.os_app._open_book_library)
