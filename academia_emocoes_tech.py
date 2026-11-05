import random
import tkinter as tk


LEFT_HAND_KEYS = set("QWERTASDFGZXCVB")
RIGHT_HAND_KEYS = set("YUIOPHJKLNM")

EMOTION_SITUATIONS = [
    {
        "story": "🦖 O amiguinho Dino ganhou uma caixa cheia de brinquedos novos e coloridos!",
        "options": [("😊", "FELIZ", True), ("😠", "BRAVO", False), ("😢", "TRISTE", False)],
        "praise": "Muito bem! Ele ficou radiante e com um sorrisão super feliz!",
    },
    {
        "story": "🧱 A torre de blocos gigantes caiu no chão quando o amiguinho ia terminar...",
        "options": [("😢", "TRISTE", True), ("😊", "FELIZ", False), ("😨", "COM MEDO", False)],
        "praise": "Isso mesmo! Dá uma tristeza quando cai, mas logo podemos reconstruir juntos com calma!",
    },
    {
        "story": "⚡ O céu escureceu, fez um barulhão de trovão e começou uma chuva forte lá fora!",
        "options": [("😨", "COM MEDO", True), ("😊", "FELIZ", False), ("😠", "BRAVO", False)],
        "praise": "Perfeito! O trovão assusta e dá medo, mas em casa com a família estamos seguros!",
    },
    {
        "story": "🖍️ Um amiguinho puxou o giz de cera da mão sem pedir licença...",
        "options": [("😠", "BRAVO", True), ("😊", "FELIZ", False), ("😨", "COM MEDO", False)],
        "praise": "Exato! Ficamos bravos, mas conversar com carinho e pedir ajuda resolve tudo!",
    },
    {
        "story": "🥛 Hora de tomar leite quentinho, cheirar o travesseiro e deitar no cobertor macio...",
        "options": [("🌸", "CALMO", True), ("😠", "BRAVO", False), ("😨", "COM MEDO", False)],
        "praise": "Que delícia! Uma paz suave e calma no coração para descansar!",
    },
]

FINGER_ASSIGNMENTS = {
    "Q": "Dedinho Mindinho da Mão Esquerda",
    "A": "Dedinho Mindinho da Mão Esquerda",
    "Z": "Dedinho Mindinho da Mão Esquerda",
    "W": "Dedo Anelar da Mão Esquerda",
    "S": "Dedo Anelar da Mão Esquerda",
    "X": "Dedo Anelar da Mão Esquerda",
    "E": "Dedo Médio da Mão Esquerda",
    "D": "Dedo Médio da Mão Esquerda",
    "C": "Dedo Médio da Mão Esquerda",
    "R": "Dedinho Indicador da Mão Esquerda",
    "T": "Dedinho Indicador da Mão Esquerda",
    "F": "Dedinho Indicador da Mão Esquerda (F•)",
    "G": "Dedinho Indicador da Mão Esquerda",
    "V": "Dedinho Indicador da Mão Esquerda",
    "B": "Dedinho Indicador da Mão Esquerda",
    "Y": "Dedinho Indicador da Mão Direita",
    "U": "Dedinho Indicador da Mão Direita",
    "H": "Dedinho Indicador da Mão Direita",
    "J": "Dedinho Indicador da Mão Direita (J•)",
    "N": "Dedinho Indicador da Mão Direita",
    "M": "Dedinho Indicador da Mão Direita",
    "I": "Dedo Médio da Mão Direita",
    "K": "Dedo Médio da Mão Direita",
    "O": "Dedo Anelar da Mão Direita",
    "L": "Dedo Anelar da Mão Direita",
    "P": "Dedinho Mindinho da Mão Direita",
}


class EmotionsCenterModal:
    """Centro Stark de Gestão das Emoções e Reator da Calma (Respiração Guiada)."""

    def __init__(self, os_app):
        self.os_app = os_app
        self.win = os_app._create_activity_window("💚 GESTÃO DAS EMOÇÕES & REATOR DA CALMA")
        self.breath_job = None
        self.quiz_idx = 0
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

        # Barra de Navegação por Abas
        nav_bar = tk.Frame(self.win, bg="#081528", pady=6)
        nav_bar.pack(fill="x")

        self.btn_tab_quiz = tk.Button(
            nav_bar,
            text="🎮 1. JOGO: COMO O AMIGO SE SENTE?",
            bg="#0284c7",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self._render_quiz,
        )
        self.btn_tab_quiz.pack(side="left", padx=8)

        self.btn_tab_wheel = tk.Button(
            nav_bar,
            text="🎭 2. MEU CORAÇÃO & SENTIMENTOS",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self._render_emotions_wheel,
        )
        self.btn_tab_wheel.pack(side="left", padx=8)

        self.btn_tab_breath = tk.Button(
            nav_bar,
            text="🌸 3. REATOR DA CALMA (RESPIRAÇÃO)",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self._start_breathing_exercise,
        )
        self.btn_tab_breath.pack(side="left", padx=8)

        self.body = tk.Frame(self.win, bg=os_app.BG_DARK)
        self.body.pack(fill="both", expand=True, padx=20, pady=10)

        # Inicia direto no jogo interativo de situações
        self._render_quiz()

    def _set_active_tab(self, active_tab: str):
        tabs = {
            "quiz": self.btn_tab_quiz,
            "wheel": self.btn_tab_wheel,
            "breath": self.btn_tab_breath,
        }
        for key, btn in tabs.items():
            if key == active_tab:
                btn.configure(bg="#0284c7", fg="#ffffff")
            else:
                btn.configure(bg="#1e293b", fg="#cbd5e1")

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

    def _render_quiz(self):
        self._clear()
        self._set_active_tab("quiz")
        name = self.os_app.brain.name
        sit = EMOTION_SITUATIONS[self.quiz_idx % len(EMOTION_SITUATIONS)]

        tk.Label(
            self.body,
            text=f"🎮 Jogo das Emoções: Como o amigo está se sentindo, {name}?",
            fg="#38bdf8",
            bg=self.os_app.BG_DARK,
            font=("Arial", 18, "bold"),
        ).pack(pady=(4, 8))

        # História em destaque
        story_box = tk.Label(
            self.body,
            text=sit["story"],
            fg="#f8fafc",
            bg="#0f172a",
            font=("Arial", 16, "bold"),
            wraplength=880,
            padx=20,
            pady=16,
            relief="groove",
            bd=3,
        )
        story_box.pack(fill="x", pady=8)

        # Botões de escolha
        opts_frame = tk.Frame(self.body, bg=self.os_app.BG_DARK)
        opts_frame.pack(fill="x", pady=10)

        colors = ["#16a34a", "#dc2626", "#2563eb", "#7c3aed"]
        for idx, (emoji, title, is_correct) in enumerate(sit["options"]):
            opts_frame.columnconfigure(idx, weight=1)
            btn = tk.Button(
                opts_frame,
                text=f"{emoji}\n{title}",
                bg=colors[idx % len(colors)],
                fg="#ffffff",
                font=("Arial", 17, "bold"),
                pady=16,
                relief="raised",
                bd=5,
                cursor="hand2",
                command=lambda ic=is_correct, pr=sit["praise"]: self._answer_quiz(ic, pr),
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=10)

        self.quiz_feedback = tk.Label(
            self.body,
            text="Ouça a historinha e toque no rostinho certo para ganhar estrelas!",
            fg="#e0f2fe",
            bg="#0b192c",
            font=("Arial", 14, "bold"),
            wraplength=880,
            height=3,
            padx=16,
            pady=8,
            highlightthickness=2,
            highlightbackground="#38bdf8",
        )
        self.quiz_feedback.pack(fill="x", pady=10)

        # Narração da situação
        clean_story = sit["story"].replace("🦖", "").replace("🧱", "").replace("⚡", "").replace("🖍️", "").replace("🥛", "")
        self.os_app.say(f"{name}, como o amigo se sente? {clean_story}")

    def _answer_quiz(self, is_correct: bool, praise: str):
        if is_correct:
            self.os_app._add_star()
            self.os_app.voice.play_tone(587, 120)
            self.os_app.voice.play_tone(880, 180)
            self.quiz_feedback.configure(
                text=f"⭐ PARABÉNS! {praise} (+1 Estrela Stark!)",
                fg="#34d399",
                highlightbackground="#10b981",
            )
            self.os_app.say(praise)
            # Próxima situação após 3 segundos
            self.win.after(3200, self._next_situation)
        else:
            self.os_app.voice.play_tone(330, 140)
            self.quiz_feedback.configure(
                text="Quase lá! Olhe bem para o rostinho e tente de novo!",
                fg="#f59e0b",
                highlightbackground="#f59e0b",
            )
            self.os_app.say("Quase lá! Vamos pensar juntos: como ele deve estar se sentindo?")

    def _next_situation(self):
        self.quiz_idx = (self.quiz_idx + 1) % len(EMOTION_SITUATIONS)
        self._render_quiz()

    def _render_emotions_wheel(self):
        self._clear()
        self._set_active_tab("wheel")
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
        self._set_active_tab("breath")
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

        finger_txt = FINGER_ASSIGNMENTS.get(target_char, "dedinho indicado")
        self.hand_hint_lbl.configure(text=f"👉 Use o {finger_txt} para apertar a tecla '{target_char}'!")

        if target_char in self.key_widgets:
            w, _ = self.key_widgets[target_char]
            w.configure(bg="#22c55e", fg="#040914")  # Destaca tecla alvo em verde neon!

        if announce_word:
            self.os_app.say(
                f"Vamos escrever a palavra {self.current_word}! Use o {finger_txt} na tecla {target_char}!"
            )
        else:
            self.os_app.say(f"Use o {finger_txt} na tecla {target_char}!")

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


class FingerCountingModal:
    """Atividade Pedagógica de Contagem com as Mãos (1 a 10) para Crianças de 4 Anos."""

    FINGER_DATA = {
        0: ("ZERO", "Mãozinhas fechadas! Zero dedinhos!", "✊ Mãozinhas Fechadas"),
        1: ("UM", "Número 1! Um dedinho apontando pro céu! Mostre o número um com sua mãozinha!", "🚀 1 Foguete voando!"),
        2: ("DOIS", "Número 2! Dois dedinhos levantados! Sinal da vitória do herói!", "🚀 🚀 2 Foguetes velozes!"),
        3: ("TRÊS", "Número 3! Três dedinhos! Um, dois, três porquinhos da história!", "🚀 🚀 🚀 3 Foguetes mágicos!"),
        4: ("QUATRO", "Número 4! Quatro dedinhos levantados! Quatro patinhas de leãozinho!", "🐾 🐾 🐾 🐾 4 Patinhas!"),
        5: ("CINCO", "Número 5! Uma mãozinha inteira aberta, dando tchauzinho com todos os cinco dedos!", "⭐ ⭐ ⭐ ⭐ ⭐ 5 Estrelas!"),
        6: ("SEIS", "Número 6! Uma mão cheia mais um dedinho da outra mão! Cinco mais um dá seis!", "🍎 🍎 🍎 🍎 🍎 🍎 6 Maçãs!"),
        7: ("SETE", "Número 7! Cinco dedinhos em uma mão e dois na outra! Sete cores do arco-íris!", "🌈 🌈 🌈 🌈 🌈 🌈 🌈 7 Cores!"),
        8: ("OITO", "Número 8! Cinco mais três! Oito patinhas do polvo marinheiro!", "🐙 🐙 🐙 🐙 🐙 🐙 🐙 🐙 8 Patinhas!"),
        9: ("NOVE", "Número 9! Quase duas mãos cheias! Falta só um dedinho para dez!", "🎈 🎈 🎈 🎈 🎈 🎈 🎈 🎈 🎈 9 Balões!"),
        10: ("DEZ", "DEZ! Duas mãozinhas cheias abertas! Todos os dez dedinhos! Parabéns herói!", "🌟 🌟 🌟 🌟 🌟 🌟 🌟 🌟 🌟 🌟 10 Estrelas!"),
    }

    TONES = [262, 294, 330, 349, 392, 440, 494, 523, 587, 659]

    def __init__(self, os_app):
        self.os_app = os_app
        self.win = os_app._create_activity_window("🖐️ CONTAR DE 1 A 10 COM AS MÃOZINHAS")
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)
        self.fingers = [False] * 10
        self.song_job = None
        self.quiz_target = None

        # Topo: Número Gigante e Itens
        top_frame = tk.Frame(self.win, bg="#0a192f", padx=16, pady=8, highlightthickness=2, highlightbackground="#38bdf8")
        top_frame.pack(fill="x", padx=16, pady=(10, 6))

        self.num_lbl = tk.Label(top_frame, text="3", font=("Arial", 38, "bold"), fg="#facc15", bg="#0a192f", width=3)
        self.num_lbl.pack(side="left", padx=8)

        text_sub = tk.Frame(top_frame, bg="#0a192f")
        text_sub.pack(side="left", fill="both", expand=True)

        self.title_lbl = tk.Label(text_sub, text="TRÊS", font=("Arial", 18, "bold"), fg="#ffffff", bg="#0a192f", anchor="w")
        self.title_lbl.pack(fill="x")

        self.items_lbl = tk.Label(text_sub, text="🚀 🚀 🚀 3 Foguetes mágicos!", font=("Arial", 13, "bold"), fg="#38bdf8", bg="#0a192f", anchor="w")
        self.items_lbl.pack(fill="x")

        tk.Button(
            top_frame,
            text="🔊 Ouvir Járvis",
            bg="#059669",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            padx=12,
            pady=6,
            command=self._speak_current,
        ).pack(side="right", padx=8)

        # Centro: Canvas Gráfico das Mãozinhas
        self.canvas = tk.Canvas(self.win, bg="#071224", height=230, highlightthickness=1, highlightbackground="#1e293b")
        self.canvas.pack(fill="both", expand=True, padx=16, pady=4)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # Barra de feedback
        self.feedback_lbl = tk.Label(
            self.win,
            text="Toque nos dedinhos para levantar ou escolha um número na régua abaixo!",
            font=("Arial", 12, "bold"),
            fg="#fef08a",
            bg=os_app.BG_DARK,
        )
        self.feedback_lbl.pack(pady=2)

        # Barra de Botões 0 a 10
        btn_bar = tk.Frame(self.win, bg=os_app.BG_DARK)
        btn_bar.pack(fill="x", padx=16, pady=(4, 6))

        colors = ["#64748b", "#ef4444", "#f97316", "#f59e0b", "#10b981", "#06b6d4", "#3b82f6", "#6366f1", "#8b5cf6", "#ec4899", "#e11d48"]
        self.pill_btns = []
        for i in range(11):
            b = tk.Button(
                btn_bar,
                text=str(i),
                bg=colors[i],
                fg="#ffffff",
                font=("Arial", 14, "bold"),
                relief="raised",
                bd=3,
                cursor="hand2",
                command=lambda val=i: self.set_number(val, speak=True),
            )
            b.pack(side="left", fill="both", expand=True, padx=2)
            self.pill_btns.append(b)

        # Botões de Ação Extras (Quiz e Canção)
        action_bar = tk.Frame(self.win, bg=os_app.BG_DARK)
        action_bar.pack(fill="x", padx=16, pady=(2, 10))

        tk.Button(
            action_bar,
            text="🎮 Jogo: Quantos Dedinhos?",
            bg="#2563eb",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            padx=14,
            pady=6,
            command=self._start_quiz,
        ).pack(side="left", padx=4)

        tk.Button(
            action_bar,
            text="▶️ Canção de Contar (1 ao 10)",
            bg="#7c3aed",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            padx=14,
            pady=6,
            command=self._play_song,
        ).pack(side="left", padx=4)

        self.quiz_frame = tk.Frame(action_bar, bg=os_app.BG_DARK)
        self.quiz_frame.pack(side="right", padx=4)

        self.finger_boxes = []
        self._init_hands_geometry()
        self.set_number(3, speak=False)
        self.os_app.say(f"Vamos contar com as mãozinhas de um até dez, {self.os_app.brain.name}!")

    def _init_hands_geometry(self):
        # 10 dedos: 5 na esquerda e 5 na direita
        # [x, y, w, h, cor, nome, id]
        self.finger_specs = [
            (50, 70, 24, 70, "#a855f7", "Mindinho E", 0),
            (82, 40, 24, 100, "#f97316", "Anelar E", 1),
            (114, 20, 26, 120, "#22c55e", "Médio E", 2),
            (148, 35, 26, 105, "#0284c7", "Indicador E", 3),
            (182, 90, 28, 65, "#eab308", "Polegar E", 4),
            (320, 90, 28, 65, "#eab308", "Polegar D", 5),
            (354, 35, 26, 105, "#0284c7", "Indicador D", 6),
            (388, 20, 26, 120, "#22c55e", "Médio D", 7),
            (420, 40, 24, 100, "#f97316", "Anelar D", 8),
            (452, 70, 24, 70, "#a855f7", "Mindinho D", 9),
        ]

    def _draw_hands(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 540
        h = self.canvas.winfo_height() or 230

        # Offset para centralizar no canvas
        offset_x = max(10, (w - 530) // 2)

        # Palmas das Mãos
        # Mão Esquerda
        self.canvas.create_oval(offset_x + 50, 130, offset_x + 200, 220, fill="#1e293b", outline="#38bdf8", width=3)
        self.canvas.create_text(offset_x + 125, 175, text="MÃO ESQUERDA", fill="#94a3b8", font=("Arial", 9, "bold"))

        # Mão Direita
        self.canvas.create_oval(offset_x + 320, 130, offset_x + 470, 220, fill="#1e293b", outline="#38bdf8", width=3)
        self.canvas.create_text(offset_x + 395, 175, text="MÃO DIREITA", fill="#94a3b8", font=("Arial", 9, "bold"))

        # Desenhar Dedos
        self.finger_boxes = []
        for x, y, fw, fh, col, name, idx in self.finger_specs:
            bx = offset_x + x
            is_up = self.fingers[idx]
            if is_up:
                dy = y
                dh = fh
                f_fill = col
                f_out = "#ffffff"
                f_w = 3
            else:
                dy = y + fh - 24
                dh = 24
                f_fill = "#1e293b"
                f_out = "#334155"
                f_w = 2

            tag_id = self.canvas.create_rectangle(bx, dy, bx + fw, dy + dh, fill=f_fill, outline=f_out, width=f_w)
            
            # Círculo com o número do dedo no topo
            cx = bx + fw // 2
            cy = dy - 12 if is_up else dy - 8
            self.canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill=col if is_up else "#0f172a", outline="#ffffff" if is_up else "#334155", width=2)
            self.canvas.create_text(cx, cy, text=str(idx + 1), fill="#ffffff" if is_up else "#64748b", font=("Arial", 9, "bold"))

            self.finger_boxes.append((bx, dy, bx + fw, dy + dh, idx))

    def _on_canvas_click(self, e):
        self._stop_song()
        for x1, y1, x2, y2, idx in self.finger_boxes:
            if x1 - 8 <= e.x <= x2 + 8 and y1 - 25 <= e.y <= y2 + 10:
                self.fingers[idx] = not self.fingers[idx]
                tone = self.TONES[idx]
                self.os_app.voice.play_tone(tone, 180)
                count = sum(self.fingers)
                self.set_number(count, speak=False)
                self.feedback_lbl.configure(text=f"{count} dedinho{'s' if count != 1 else ''} levantado{'s' if count != 1 else ''}!")
                return

    def set_number(self, num: int, speak: bool = True):
        self._stop_song()
        num = max(0, min(10, num))
        for i in range(10):
            self.fingers[i] = i < num

        self.num_lbl.configure(text=str(num))
        title, hint, items = self.FINGER_DATA.get(num, self.FINGER_DATA[0])
        self.title_lbl.configure(text=title)
        self.items_lbl.configure(text=items)
        self.feedback_lbl.configure(text=hint)

        self._draw_hands()

        # Destaque no botão
        for idx, btn in enumerate(self.pill_btns):
            if idx == num:
                btn.configure(relief="sunken", bd=5)
            else:
                btn.configure(relief="raised", bd=3)

        if num == 10:
            self.os_app._add_star()
            self.os_app.voice.play_tone(659, 120)
            self.win.after(120, lambda: self.os_app.voice.play_tone(880, 240))

        if speak:
            self.os_app.say(hint)

    def _speak_current(self):
        count = sum(self.fingers)
        _, hint, _ = self.FINGER_DATA.get(count, self.FINGER_DATA[0])
        self.os_app.say(hint)

    def _start_quiz(self):
        self._stop_song()
        for w in self.quiz_frame.winfo_children():
            w.destroy()

        self.quiz_target = random.randint(1, 10)
        for i in range(10):
            self.fingers[i] = i < self.quiz_target

        self.num_lbl.configure(text="?")
        self.title_lbl.configure(text="QUANTOS DEDINHOS?")
        self.items_lbl.configure(text="Conte os dedinhos levantados na tela!")
        msg = f"Quantos dedinhos o Járvis está levantando, {self.os_app.brain.name}?"
        self.feedback_lbl.configure(text=msg)
        self.os_app.say(f"Quantos dedinhos o Járvis está mostrando? Conte com a sua mãozinha e toque no número certo!")
        self._draw_hands()

        opts = {self.quiz_target}
        while len(opts) < 3:
            opts.add(random.randint(1, 10))
        shuffled = sorted(list(opts))

        for opt in shuffled:
            tk.Button(
                self.quiz_frame,
                text=str(opt),
                bg="#2563eb",
                fg="#ffffff",
                font=("Arial", 16, "bold"),
                width=3,
                command=lambda val=opt: self._check_quiz(val),
            ).pack(side="left", padx=4)

    def _check_quiz(self, picked: int):
        if picked == self.quiz_target:
            self.os_app._add_star()
            self.os_app.voice.play_tone(659, 120)
            self.win.after(120, lambda: self.os_app.voice.play_tone(880, 220))
            self.set_number(self.quiz_target, speak=False)
            self.feedback_lbl.configure(text=f"🎉 PARABÉNS! Você acertou: são {self.quiz_target} dedinhos! Ganhou uma estrela!")
            self.os_app.say(f"Parabéns, {self.os_app.brain.name}! São exatamente {self.quiz_target} dedinhos! Você é nota dez!")
            for w in self.quiz_frame.winfo_children():
                w.destroy()
        else:
            self.os_app.voice.play_tone(220, 180)
            self.feedback_lbl.configure(text=f"Quase! Vamos contar juntos: são {self.quiz_target} dedinhos!")
            self.os_app.say(f"Quase! Vamos contar juntos os dedinhos levantados! Tente tocar no número certo!")

    def _play_song(self):
        self._stop_song()
        self.os_app.say(f"Vamos cantar e contar de um até dez levantando os dedinhos, {self.os_app.brain.name}!")
        step = 1

        def next_num():
            nonlocal step
            if step > 10:
                self._stop_song()
                return
            self.set_number(step, speak=True)
            step += 1
            self.song_job = self.win.after(3500, next_num)

        self.song_job = self.win.after(2200, next_num)

    def _stop_song(self):
        if self.song_job:
            self.win.after_cancel(self.song_job)
            self.song_job = None

    def _on_close(self):
        self._stop_song()
        self.win.destroy()
