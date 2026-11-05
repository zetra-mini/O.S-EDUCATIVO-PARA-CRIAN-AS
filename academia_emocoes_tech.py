import random
import tkinter as tk


LEFT_HAND_KEYS = set("QWERTASDFGZXCVB")
RIGHT_HAND_KEYS = set("YUIOPHJKLNM")


class EmotionsCenterModal:
    """Centro Stark de Gestão das Emoções e Reator da Calma (Respiração Guiada)."""

    def __init__(self, os_app):
        self.os_app = os_app
        self.win = os_app._create_activity_window("💚 GESTÃO DAS EMOÇÕES & REATOR DA CALMA")
        self.breath_job = None
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

        self.body = tk.Frame(self.win, bg=os_app.BG_DARK)
        self.body.pack(fill="both", expand=True, padx=20, pady=12)

        self._render_emotions_wheel()

    def _on_close(self):
        if self.breath_job:
            self.win.after_cancel(self.breath_job)
        self.win.destroy()

    def _clear(self):
        if self.breath_job:
            self.win.after_cancel(self.breath_job)
            self.breath_job = None
        for w in self.body.winfo_children():
            w.destroy()

    def _render_emotions_wheel(self):
        self._clear()
        name = self.os_app.brain.name

        tk.Label(
            self.body,
            text=f"Como o seu coração está se sentindo agora, {name}?",
            fg="#ffffff",
            bg=self.os_app.BG_DARK,
            font=("Arial", 19, "bold"),
        ).pack(pady=(4, 12))

        cards_frame = tk.Frame(self.body, bg=self.os_app.BG_DARK)
        cards_frame.pack(fill="x", pady=6)

        emotions = [
            (
                "😊",
                "FELIZ",
                "#16a34a",
                f"Que alegria saber que você está feliz, {name}! Quando estamos felizes, podemos compartilhar nosso sorriso e agradecer pelas coisas boas!",
                False,
            ),
            (
                "😠",
                "BRAVO",
                "#dc2626",
                f"Tudo bem sentir raiva quando algo não sai como queremos, {name}. Todo herói sente isso! Vamos ligar o Reator da Calma para esfriar esse vulcão?",
                True,
            ),
            (
                "😢",
                "TRISTE",
                "#2563eb",
                f"Sentir tristeza faz parte da vida, {name}. Você nunca está sozinho: pode pedir um abraço bem apertado para sua família e respirar comigo!",
                True,
            ),
            (
                "😨",
                "COM MEDO",
                "#7c3aed",
                f"Coragem não é nunca ter medo, {name}, é saber que você está protegido e seguro! Vamos respirar devagar juntos?",
                True,
            ),
            (
                "⚡",
                "AGITADO",
                "#d97706",
                f"Seus propulsores estão a mil por hora, {name}! Vamos pousar a armadura suavemente fazendo a respiração do herói?",
                True,
            ),
        ]

        for idx, (emoji, title, color, speech, suggest_breath) in enumerate(emotions):
            cards_frame.columnconfigure(idx, weight=1)
            btn = tk.Button(
                cards_frame,
                text=f"{emoji}\n{title}",
                bg=color,
                fg="#ffffff",
                font=("Arial", 16, "bold"),
                pady=18,
                relief="raised",
                bd=5,
                cursor="hand2",
                command=lambda s=speech, sb=suggest_breath: self._select_emotion(s, sb),
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=6)

        self.msg_box = tk.Label(
            self.body,
            text="Toque em um rostinho colorido acima para contar ao Járvis como você está!",
            fg="#e0f2fe",
            bg="#0b192c",
            font=("Arial", 15, "bold"),
            wraplength=880,
            height=4,
            padx=18,
            pady=12,
            highlightthickness=2,
            highlightbackground="#38bdf8",
        )
        self.msg_box.pack(fill="x", pady=16)

        tk.Button(
            self.body,
            text="🌬️ INICIAR EXERCÍCIO DO REATOR DA CALMA (RESPIRAÇÃO GUIADA)",
            bg="#0284c7",
            fg="#ffffff",
            font=("Arial", 15, "bold"),
            padx=24,
            pady=14,
            cursor="hand2",
            command=self._start_breathing_exercise,
        ).pack(pady=6)

        self.os_app.say(f"Como o seu coração está se sentindo agora, {name}? Toque em um dos rostinhos!")

    def _select_emotion(self, speech: str, suggest_breath: bool):
        self.os_app.voice.play_tone(523, 120)
        self.msg_box.configure(text=speech)
        self.os_app.say(speech)
        if suggest_breath:
            self.breath_job = self.win.after(6800, self._start_breathing_exercise)

    def _start_breathing_exercise(self):
        self._clear()
        tk.Button(
            self.body,
            text="⬅ Voltar aos Sentimentos",
            bg="#334155",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=5,
            command=self._render_emotions_wheel,
        ).pack(anchor="w")

        self.phase_lbl = tk.Label(
            self.body,
            text="Prepare-se para respirar com o Reator da Calma...",
            fg="#38bdf8",
            bg=self.os_app.BG_DARK,
            font=("Arial", 20, "bold"),
        )
        self.phase_lbl.pack(pady=8)

        self.b_canvas = tk.Canvas(self.body, width=420, height=320, bg=self.os_app.BG_DARK, highlightthickness=0)
        self.b_canvas.pack(expand=True)

        self.step = 0
        self.cycles = 0
        self._animate_breath()

    def _animate_breath(self):
        # Cada ciclo tem 80 passos de 100ms (4s inspirar + 4s expirar)
        pos = self.step % 80
        if pos == 0:
            if self.cycles >= 3:
                self.os_app._add_star()
                self.phase_lbl.configure(text="🌟 Muito bem! Coração calmo e mente brilhante! (+1 Estrela)")
                self.os_app.say(
                    f"Parabéns, {self.os_app.brain.name}! Três respirações completas! Seu Reator da Calma está brilhando!"
                )
                return
            self.phase_lbl.configure(text="🌸 PUXE O AR PELO NARIZ (Cheire a florzinha...)", fg="#34d399")
            self.os_app.voice.play_tone(440, 180)
            self.os_app.say("Puxe o ar cheirando a florzinha...")
        elif pos == 40:
            self.phase_lbl.configure(text="🕯️ SOLTE O AR PELA BOCA (Sopre a velinha devagar...)", fg="#fbbf24")
            self.os_app.voice.play_tone(330, 180)
            self.os_app.say("Agora sopre a velinha bem devagar...")
            self.cycles += 1

        # Raio varia suavemente entre 45 e 135
        radius = 45 + int(90 * (pos / 40.0)) if pos < 40 else 135 - int(90 * ((pos - 40) / 40.0))
        color = "#10b981" if pos < 40 else "#38bdf8"

        self.b_canvas.delete("all")
        cx, cy = 210, 160
        self.b_canvas.create_oval(
            cx - radius - 14, cy - radius - 14, cx + radius + 14, cy + radius + 14, outline=color, width=3
        )
        self.b_canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=color, outline="#ffffff", width=3)
        self.b_canvas.create_text(
            cx, cy, text="CALMA" if pos >= 40 else "AR", fill="#040914", font=("Arial", 18, "bold")
        )

        self.step += 1
        self.breath_job = self.win.after(100, self._animate_breath)


class TechAcademyModal:
    """Academia Stark de Tecnologia: Domínio do Mouse (Mover, Clicar, Arrastar) e Digitação com as 2 Mãos."""

    KEYBOARD_ROWS = [
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["Z", "X", "C", "V", "B", "N", "M"],
    ]

    WORDS = ["LIVRO", "SOL", "LUA", "AMOR", "CASA", "CALMA", " BOLA".strip(), "GATO", "VIDA"]

    def __init__(self, os_app):
        self.os_app = os_app
        self.win = os_app._create_activity_window("⌨️ ACADEMIA DE MOUSE & DIGITAÇÃO CORRETA")

        tabs = tk.Frame(self.win, bg="#0b1526", pady=8)
        tabs.pack(fill="x")

        tk.Button(
            tabs,
            text="🖱️ 1. TREINO DE MOUSE (MOVER, CLICAR E ARRASTAR)",
            bg="#0284c7",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._render_mouse_trainer,
        ).pack(side="left", padx=16)

        tk.Button(
            tabs,
            text="⌨️ 2. DIGITAÇÃO CORRETA (AS DUAS MÃOZINHAS)",
            bg="#eab308",
            fg="#0f172a",
            font=("Arial", 12, "bold"),
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._render_typing_trainer,
        ).pack(side="left", padx=8)

        self.stage = tk.Frame(self.win, bg=os_app.BG_DARK)
        self.stage.pack(fill="both", expand=True, padx=18, pady=10)

        self._render_typing_trainer()

    def _clear_stage(self):
        self.win.unbind("<Key>")
        for w in self.stage.winfo_children():
            w.destroy()

    # ==========================================================================
    # ABA 1: TREINO DE MOUSE EM 3 FASES (MOVER -> CLICAR -> ARRASTAR)
    # ==========================================================================
    def _render_mouse_trainer(self):
        self._clear_stage()
        self.mouse_level = 1
        self.mouse_hits = 0

        self.m_info = tk.Label(
            self.stage,
            text="Fase 1: Passeie com o mouse e encoste a setinha na Estrela Azul!",
            fg="#38bdf8",
            bg=self.os_app.BG_DARK,
            font=("Arial", 16, "bold"),
        )
        self.m_info.pack(pady=(0, 8))

        self.m_canvas = tk.Canvas(
            self.stage, bg="#06101f", highlightthickness=2, highlightbackground="#0284c7", cursor="hand2"
        )
        self.m_canvas.pack(fill="both", expand=True)

        self.os_app.say(
            "Treino de Mouse! Fase um: mexa o mouse devagarinho até encostar a setinha na bola azul brilhante!"
        )
        self.win.after(150, self._spawn_mouse_challenge)

    def _spawn_mouse_challenge(self):
        c = self.m_canvas
        c.delete("all")
        w = max(600, c.winfo_width())
        h = max(320, c.winfo_height())

        tx = random.randint(90, w - 110)
        ty = random.randint(70, h - 90)

        if self.mouse_level == 1:
            # Fase 1: Apenas encostar o cursor (coordenação motora fina)
            target = c.create_oval(tx - 42, ty - 42, tx + 42, ty + 42, fill="#00f0ff", outline="#ffffff", width=4)
            txt = c.create_text(tx, ty, text="ENCOSTE", fill="#040914", font=("Arial", 11, "bold"))

            def on_hover(_e):
                self._advance_mouse_progress()

            c.tag_bind(target, "<Enter>", on_hover)
            c.tag_bind(txt, "<Enter>", on_hover)

        elif self.mouse_level == 2:
            # Fase 2: Clique Esquerdo com o dedo indicador
            target = c.create_oval(tx - 44, ty - 44, tx + 44, ty + 44, fill="#22c55e", outline="#ffffff", width=4)
            txt = c.create_text(tx, ty, text="CLIQUE!", fill="#ffffff", font=("Arial", 13, "bold"))

            def on_click(_e):
                self._advance_mouse_progress()

            c.tag_bind(target, "<Button-1>", on_click)
            c.tag_bind(txt, "<Button-1>", on_click)

        else:
            # Fase 3: Segurar o botão e Arrastar (Drag & Drop) até o Reator!
            rx, ry = w - 130, h // 2
            c.create_oval(rx - 62, ry - 62, rx + 62, ry + 62, fill="#0c4a6e", outline="#00f0ff", width=4)
            c.create_text(rx, ry, text="REATOR\n(SOLTE AQUI)", fill="#e0f2fe", font=("Arial", 10, "bold"), justify="center")

            bx, by = 130, h // 2
            orb = c.create_oval(bx - 36, by - 36, bx + 36, by + 36, fill="#facc15", outline="#ffffff", width=4)
            orb_txt = c.create_text(bx, by, text="ENERGIA", fill="#0f172a", font=("Arial", 10, "bold"))

            drag_data = {"dragging": False}

            def start_drag(_e):
                drag_data["dragging"] = True

            def move_drag(e):
                if drag_data["dragging"]:
                    c.coords(orb, e.x - 36, e.y - 36, e.x + 36, e.y + 36)
                    c.coords(orb_txt, e.x, e.y)

            def end_drag(e):
                if not drag_data["dragging"]:
                    return
                drag_data["dragging"] = False
                if abs(e.x - rx) < 68 and abs(e.y - ry) < 68:
                    self._advance_mouse_progress()

            for item in (orb, orb_txt):
                c.tag_bind(item, "<ButtonPress-1>", start_drag)
                c.tag_bind(item, "<B1-Motion>", move_drag)
                c.tag_bind(item, "<ButtonRelease-1>", end_drag)

    def _advance_mouse_progress(self):
        self.os_app.voice.play_tone(659, 110)
        self.mouse_hits += 1

        if self.mouse_hits >= 3 and self.mouse_level == 1:
            self.mouse_level = 2
            self.mouse_hits = 0
            self.m_info.configure(text="Fase 2: Agora aperte o botão ESQUERDO do mouse com o dedinho indicador!", fg="#4ade80")
            self.os_app.say("Muito bem! Fase dois: agora clique com o dedinho indicador no círculo verde!")
        elif self.mouse_hits >= 3 and self.mouse_level == 2:
            self.mouse_level = 3
            self.mouse_hits = 0
            self.m_info.configure(text="Fase 3: Segure o botão na ENERGIA amarela e arraste até o REATOR!", fg="#facc15")
            self.os_app.say("Excelente! Fase três: segure a energia amarela com o mouse e arraste até dentro do Reator!")
        elif self.mouse_hits >= 2 and self.mouse_level == 3:
            self.os_app._add_star()
            self.mouse_level = 1
            self.mouse_hits = 0
            self.m_info.configure(text="🏆 Mestre do Mouse! Você ganhou uma Estrela Stark! Vamos mais uma rodada!", fg="#38bdf8")
            self.os_app.say(f"Parabéns, {self.os_app.brain.name}! Você já sabe mover, clicar e arrastar o mouse!")

        self._spawn_mouse_challenge()

    # ==========================================================================
    # ABA 2: DIGITAÇÃO CORRETA COM MAPA VISUAL DAS DUAS MÃOZINHAS
    # ==========================================================================
    def _render_typing_trainer(self):
        self._clear_stage()

        # Legenda Educativa das Duas Mãos
        legend = tk.Frame(self.stage, bg="#0b192c", pady=6, padx=12, highlightthickness=1, highlightbackground="#38bdf8")
        legend.pack(fill="x", pady=(0, 8))

        tk.Label(
            legend,
            text="🖐 MÃO ESQUERDA = Teclas Azuis (Indicador na tecla F•)",
            fg="#38bdf8",
            bg="#0b192c",
            font=("Arial", 12, "bold"),
        ).pack(side="left", padx=12)

        tk.Label(
            legend,
            text="🤚 MÃO DIREITA = Teclas Amarelas (Indicador na tecla J•)",
            fg="#facc15",
            bg="#0b192c",
            font=("Arial", 12, "bold"),
        ).pack(side="right", padx=12)

        # Palavra atual e letra alvo
        self.word_lbl = tk.Label(self.stage, text="", fg="#ffffff", bg=self.os_app.BG_DARK, font=("Consolas", 28, "bold"))
        self.word_lbl.pack(pady=4)

        self.hand_hint_lbl = tk.Label(self.stage, text="", fg="#4ade80", bg=self.os_app.BG_DARK, font=("Arial", 15, "bold"))
        self.hand_hint_lbl.pack(pady=(0, 10))

        # Mapa Visual do Teclado na Tela
        kb_frame = tk.Frame(self.stage, bg=self.os_app.BG_DARK)
        kb_frame.pack(expand=True)

        self.key_widgets = {}
        for r_idx, row in enumerate(self.KEYBOARD_ROWS):
            row_frame = tk.Frame(kb_frame, bg=self.os_app.BG_DARK)
            row_frame.pack(pady=4)
            for key_char in row:
                base_bg = "#0369a1" if key_char in LEFT_HAND_KEYS else "#a16207"
                label_txt = f"{key_char}•" if key_char in ("F", "J") else key_char
                lbl = tk.Label(
                    row_frame,
                    text=label_txt,
                    width=4,
                    height=2,
                    bg=base_bg,
                    fg="#ffffff",
                    font=("Arial", 16, "bold"),
                    relief="raised",
                    bd=3,
                )
                lbl.pack(side="left", padx=4)
                lbl.bind("<Button-1>", lambda _e, k=key_char: self._process_typed_char(k))
                self.key_widgets[key_char] = (lbl, base_bg)

        # Barra de Espaço (Dedões)
        space_lbl = tk.Label(
            kb_frame,
            text="👍 BARRA DE ESPAÇO (DEDÕES)",
            width=32,
            height=1,
            bg="#15803d",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            relief="raised",
            bd=3,
            pady=6,
        )
        space_lbl.pack(pady=6)

        # Incluir o próprio nome da criança (apenas letras sem acento simples) na lista!
        clean_child = "".join(ch for ch in self.os_app.brain.name.upper() if ch in LEFT_HAND_KEYS or ch in RIGHT_HAND_KEYS)
        self.word_pool = list(self.WORDS)
        if 2 <= len(clean_child) <= 10:
            self.word_pool.insert(0, clean_child)

        self.current_word = ""
        self.char_idx = 0
        self.win.bind("<Key>", lambda e: self._process_typed_char(e.char.upper()))
        self._next_typing_word()

    def _next_typing_word(self):
        self.current_word = random.choice(self.word_pool)
        self.char_idx = 0
        self._refresh_typing_ui(announce_word=True)

    def _refresh_typing_ui(self, announce_word: bool = False):
        # Restaura cores padrão das teclas
        for k, (widget, base_bg) in self.key_widgets.items():
            widget.configure(bg=base_bg, fg="#ffffff")

        target_char = self.current_word[self.char_idx]
        typed_part = self.current_word[: self.char_idx]
        rem_part = self.current_word[self.char_idx + 1 :]
        self.word_lbl.configure(text=f"{typed_part} [ {target_char} ] {rem_part}")

        hand_txt = "🖐 MÃOZINHA ESQUERDA (Lado Azul)" if target_char in LEFT_HAND_KEYS else "🤚 MÃOZINHA DIREITA (Lado Amarelo)"
        hand_speech = "mãozinha esquerda" if target_char in LEFT_HAND_KEYS else "mãozinha direita"
        self.hand_hint_lbl.configure(text=f"Aperte a letra '{target_char}' usando a {hand_txt}!")

        if target_char in self.key_widgets:
            w, _ = self.key_widgets[target_char]
            w.configure(bg="#22c55e", fg="#040914")  # Destaca tecla alvo em verde neon!

        if announce_word:
            self.os_app.say(
                f"Vamos escrever a palavra {self.current_word}! Comece apertando a letra {target_char} com a {hand_speech}!"
            )
        else:
            self.os_app.say(f"Letra {target_char}, com a {hand_speech}!")

    def _process_typed_char(self, ch: str):
        if not ch or not self.current_word:
            return
        target_char = self.current_word[self.char_idx]
        if ch == target_char:
            self.os_app.voice.play_tone(659, 100)
            self.char_idx += 1
            if self.char_idx >= len(self.current_word):
                self.os_app._add_star()
                done_word = self.current_word
                self.word_lbl.configure(text=f"🌟 {done_word} 🌟")
                self.os_app.say(f"Sensacional! Você digitou {done_word} usando as duas mãozinhas!")
                self.win.after(2400, self._next_typing_word)
            else:
                self._refresh_typing_ui(announce_word=False)
        elif ch in self.key_widgets:
            self.os_app.voice.play_tone(240, 140)
            hand_speech = "mãozinha esquerda, no lado azul" if target_char in LEFT_HAND_KEYS else "mãozinha direita, no lado amarelo"
            self.os_app.say(f"Quase! Procure a tecla verde com a letra {target_char}, usando a {hand_speech}!")
