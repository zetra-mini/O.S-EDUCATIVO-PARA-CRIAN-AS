#!/usr/bin/env python3
import platform
import random
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

from academia_emocoes_tech import EmotionsCenterModal, TechAcademyModal
from biblioteca_livros import BookLibraryModal
from gestao_tempo_midia import CinemaStarkModal, MediaTimeManager
from jarvis_brain import JarvisBrain
from voz_jarvis import JarvisVoice


class JarvisKidsOS:
    """
    JARVIS Kids OS v2.0 — Central Educativa Estilo Homem de Ferro para Crianças de ~4 Anos.
    Pilares:
      1. Hábito de Ler Livros (Base Principal — Biblioteca Ilustrada e Narrada)
      2. Gestão das Emoções (Roda de Sentimentos e Reator da Calma)
      3. Tecnologia (Domínio do Mouse + Digitação Correta com as Duas Mãozinhas)
      4. Educação do Tempo (Netflix & YouTube Kids com Horário Fixo, Cronômetro e Redirecionamento)
    Projetado sob medida para Acer Aspire One 532h (1024x600, Atom N450, GMA 3150, < 30 MB RAM).
    """

    BG_DARK = "#040914"
    PANEL_BG = "#0a1628"
    CYAN = "#00f0ff"
    CYAN_DIM = "#0c4a6e"
    GOLD = "#fbbf24"
    RED_STARK = "#ef4444"
    GREEN_OK = "#10b981"
    PURPLE = "#a855f7"
    ORANGE = "#f97316"
    PINK = "#ec4899"

    def __init__(self, kiosk: bool = False):
        self.kiosk = kiosk
        self.brain = JarvisBrain()
        self.media_mgr = MediaTimeManager(self.brain)
        self.is_speaking = False
        self.voice = JarvisVoice(on_speaking_change=self._on_speaking_state)
        self.voice.muted = not self.brain.config.get("voice_enabled", True)

        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S. Kids OS v2.0 — Stark Educational System")
        self.root.configure(bg=self.BG_DARK)
        self.root.geometry("1024x600")
        self.root.minsize(860, 540)

        if self.kiosk:
            self.root.attributes("-fullscreen", True)
            self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        self.angle = 0
        self.pulse = 0
        self.stars_earned = 0
        self.subtitle_var = tk.StringVar(value="Inicializando sistemas educativos Stark...")
        self.mode_badge_var = tk.StringVar()
        self._update_mode_badge()

        self._build_main_hud()
        self._animate_arc_reactor()

        self.root.after(700, self._welcome)

    def _on_speaking_state(self, speaking: bool):
        self.is_speaking = speaking

    def _update_mode_badge(self):
        m = self.brain.config.get("mode", "offline")
        sched = f"{self.brain.config.get('media_start_time', '16:00')}-{self.brain.config.get('media_end_time', '17:00')}"
        labels = {
            "offline": f"OFFLINE • CINEMA: {sched}",
            "ollama": f"OLLAMA REDE • CINEMA: {sched}",
            "cloud": f"NUVEM ({self.brain.config.get('cloud_provider', 'API').upper()}) • CINEMA: {sched}",
        }
        self.mode_badge_var.set(labels.get(m, "MODO: 100% OFFLINE"))

    def update_books_badge(self):
        n = self.media_mgr.get_books_read_today()
        self.books_label.configure(text=f"📖 Livros hoje: {n}")

    def say(self, text: str):
        self.subtitle_var.set(text)
        self.voice.speak(text)

    def _welcome(self):
        self.voice.play_tone(523, 110)
        self.root.after(130, lambda: self.voice.play_tone(659, 110))
        self.root.after(260, lambda: self.voice.play_tone(784, 170))
        books_today = self.media_mgr.get_books_read_today()
        if books_today == 0:
            msg = (
                f"Olá, {self.brain.name}! Eu sou o Járvis! "
                f"Que tal começarmos o dia abrindo um livro mágico na Biblioteca Stark?"
            )
        else:
            msg = self.brain.get_greeting()
        self.root.after(440, lambda: self.say(msg))

    # ==========================================================================
    # HUD PRINCIPAL (1024 x 600) — 8 GRANDES MÓDULOS + REATOR ARC
    # ==========================================================================
    def _build_main_hud(self):
        top_bar = tk.Frame(self.root, bg="#071120", height=46, highlightthickness=1, highlightbackground=self.CYAN_DIM)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        tk.Label(
            top_bar,
            text="◈ J.A.R.V.I.S. KIDS OS",
            fg=self.CYAN,
            bg="#071120",
            font=("Consolas", 13, "bold"),
        ).pack(side="left", padx=14)

        self.stars_label = tk.Label(
            top_bar,
            text="★ 0 Estrelas",
            fg=self.GOLD,
            bg="#071120",
            font=("Arial", 12, "bold"),
        )
        self.stars_label.pack(side="left", padx=10)

        self.books_label = tk.Label(
            top_bar,
            text=f"📖 Livros hoje: {self.media_mgr.get_books_read_today()}",
            fg="#4ade80",
            bg="#071120",
            font=("Arial", 12, "bold"),
        )
        self.books_label.pack(side="left", padx=12)

        tk.Button(
            top_bar,
            text="⚙ PAIS",
            fg="#94a3b8",
            bg="#0f172a",
            activebackground="#1e293b",
            activeforeground=self.CYAN,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._open_parent_gate,
        ).pack(side="right", padx=12, pady=7)

        tk.Label(
            top_bar,
            textvariable=self.mode_badge_var,
            fg="#38bdf8",
            bg="#071120",
            font=("Consolas", 9),
        ).pack(side="right", padx=8)

        # Área Central: 3 Colunas
        center = tk.Frame(self.root, bg=self.BG_DARK)
        center.pack(fill="both", expand=True, padx=14, pady=6)
        center.columnconfigure(0, weight=1)
        center.columnconfigure(1, weight=0)
        center.columnconfigure(2, weight=1)
        center.rowconfigure(0, weight=1)

        left_col = tk.Frame(center, bg=self.BG_DARK)
        left_col.grid(row=0, column=0, sticky="nsew", padx=6)

        mid_col = tk.Frame(center, bg=self.BG_DARK, width=280)
        mid_col.grid(row=0, column=1, sticky="nsew", padx=4)

        right_col = tk.Frame(center, bg=self.BG_DARK)
        right_col.grid(row=0, column=2, sticky="nsew", padx=6)

        # COLUNA ESQUERDA: Os 4 Pilares Principais (Livros, Mouse/Teclado, Emoções, Cinema com Tempo)
        self._make_big_module_btn(
            left_col,
            icon="📚",
            title="LER LIVROS (BASE)",
            subtitle="Histórias Narradas & Palavras",
            color=self.GOLD,
            voice_hint="Biblioteca de Livros! Nossa base principal de aventuras e sabedoria!",
            command=self._open_book_library,
        )
        self._make_big_module_btn(
            left_col,
            icon="⌨",
            title="MOUSE & DIGITAÇÃO",
            subtitle="Usar Mouse e as 2 Mãozinhas",
            color=self.CYAN,
            voice_hint="Academia de Tecnologia! Aprenda a usar o mouse e digitar com as duas mãozinhas!",
            command=self._open_tech_academy,
        )
        self._make_big_module_btn(
            left_col,
            icon="💚",
            title="EMOÇÕES & CALMA",
            subtitle="Sentimentos e Respiração",
            color=self.GREEN_OK,
            voice_hint="Centro das Emoções e Reator da Calma!",
            command=self._open_emotions_center,
        )
        self._make_big_module_btn(
            left_col,
            icon="🎬",
            title="CINEMA NO HORÁRIO",
            subtitle="YouTube Kids & Netflix",
            color=self.RED_STARK,
            voice_hint="Cinema Stark! Lembre-se: tudo tem o seu tempo combinado!",
            command=self._open_cinema_stark,
        )

        # CENTRO: Reator Arc Interativo
        self.arc_canvas = tk.Canvas(
            mid_col, width=270, height=290, bg=self.BG_DARK, highlightthickness=0, cursor="hand2"
        )
        self.arc_canvas.pack(expand=True)
        self.arc_canvas.bind("<Button-1>", lambda _e: self._on_arc_clicked())

        tk.Label(
            mid_col,
            text="Toque no Reator para falar comigo!",
            fg=self.CYAN,
            bg=self.BG_DARK,
            font=("Arial", 9, "bold"),
        ).pack(pady=(0, 4))

        # COLUNA DIREITA: Jogos GCompris, Pintura Tux Paint, Música e Conversa JARVIS
        self._make_big_module_btn(
            right_col,
            icon="★",
            title="JOGOS EDUCATIVOS",
            subtitle="GCompris / Desafio Cores",
            color="#22c55e",
            voice_hint="Jogos educativos e desafio das cores!",
            command=self._launch_gcompris_or_shapes,
        )
        self._make_big_module_btn(
            right_col,
            icon="✎",
            title="PINTURA MÁGICA",
            subtitle="Tux Paint / Lousa Neon",
            color=self.ORANGE,
            voice_hint="Laboratório de pintura mágica!",
            command=self._launch_tuxpaint_or_draw,
        )
        self._make_big_module_btn(
            right_col,
            icon="♪",
            title="PIANO & MÚSICA",
            subtitle="Gamine / Notas Coloridas",
            color=self.PURPLE,
            voice_hint="Piano musical e chuva de estrelas!",
            command=self._open_music_synth,
        )
        self._make_big_module_btn(
            right_col,
            icon="🚀",
            title="CONVERSAR & CONTAR",
            subtitle="Dinos, Espaço e Foguetes",
            color=self.PINK,
            voice_hint="Conversar com o Járvis sobre espaço, dinossauros e foguetes!",
            command=self._open_talk_hub,
        )

        # Barra Inferior de Voz / Legenda
        bottom_bar = tk.Frame(
            self.root, bg="#071324", height=66, highlightthickness=2, highlightbackground=self.CYAN
        )
        bottom_bar.pack(fill="x", side="bottom", padx=14, pady=(0, 10))
        bottom_bar.pack_propagate(False)

        tk.Label(
            bottom_bar,
            textvariable=self.subtitle_var,
            fg="#f0f9ff",
            bg="#071324",
            font=("Arial", 12, "bold"),
            wraplength=960,
            justify="center",
        ).pack(expand=True, fill="both", padx=12, pady=6)

    def _make_big_module_btn(self, parent, icon, title, subtitle, color, voice_hint, command):
        card = tk.Frame(
            parent,
            bg=self.PANEL_BG,
            highlightthickness=2,
            highlightbackground=color,
            cursor="hand2",
            pady=6,
            padx=10,
        )
        card.pack(fill="both", expand=True, pady=5)

        row = tk.Frame(card, bg=self.PANEL_BG)
        row.pack(expand=True, fill="both")

        lbl_icon = tk.Label(
            row, text=icon, fg=color, bg=self.PANEL_BG, font=("Arial", 22, "bold"), width=3
        )
        lbl_icon.pack(side="left", padx=(2, 8))

        txt_frame = tk.Frame(row, bg=self.PANEL_BG)
        txt_frame.pack(side="left", fill="both", expand=True)

        lbl_title = tk.Label(
            txt_frame, text=title, fg="#ffffff", bg=self.PANEL_BG, font=("Arial", 12, "bold"), anchor="w"
        )
        lbl_title.pack(fill="x", pady=(2, 0))

        lbl_sub = tk.Label(
            txt_frame, text=subtitle, fg="#94a3b8", bg=self.PANEL_BG, font=("Arial", 9), anchor="w"
        )
        lbl_sub.pack(fill="x")

        def on_click(_e=None):
            self.voice.play_tone(659, 90)
            command()

        def on_enter(_e=None):
            for w in (card, row, lbl_icon, txt_frame, lbl_title, lbl_sub):
                w.configure(bg="#132642")
            self.subtitle_var.set(voice_hint)

        def on_leave(_e=None):
            for w in (card, row, lbl_icon, txt_frame, lbl_title, lbl_sub):
                w.configure(bg=self.PANEL_BG)

        for w in (card, row, lbl_icon, txt_frame, lbl_title, lbl_sub):
            w.bind("<Button-1>", on_click)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    # ==========================================================================
    # ANIMAÇÃO DO REATOR ARC
    # ==========================================================================
    def _animate_arc_reactor(self):
        c = self.arc_canvas
        c.delete("all")
        cx, cy = 135, 145
        self.angle = (self.angle + 6) % 360
        self.pulse = (self.pulse + 1) % 20

        glow_extra = 9 if self.is_speaking and (self.pulse % 4 < 2) else 0
        core_color = self.GOLD if self.is_speaking else self.CYAN

        c.create_oval(cx - 114, cy - 114, cx + 114, cy + 114, outline=self.CYAN_DIM, width=3)
        c.create_oval(cx - 100, cy - 100, cx + 100, cy + 100, outline=self.CYAN, width=2)

        for i in range(6):
            start_ang = (self.angle + i * 60) % 360
            c.create_arc(
                cx - 86, cy - 86, cx + 86, cy + 86, start=start_ang, extent=32, style="arc", outline=core_color, width=6
            )

        for i in range(4):
            start_ang = (-self.angle * 1.5 + i * 90) % 360
            c.create_arc(
                cx - 60, cy - 60, cx + 60, cy + 60, start=start_ang, extent=45, style="arc", outline="#38bdf8", width=4
            )

        r_core = 38 + glow_extra
        c.create_oval(
            cx - r_core,
            cy - r_core,
            cx + r_core,
            cy + r_core,
            fill="#0284c7" if not self.is_speaking else "#d97706",
            outline="#e0f2fe",
            width=3,
        )
        c.create_oval(cx - 19, cy - 19, cx + 19, cy + 19, fill="#e0f2fe", outline="")
        c.create_text(cx, cy + 130, text="STARK EDU CORE v2.0", fill="#38bdf8", font=("Consolas", 9, "bold"))

        self.root.after(70, self._animate_arc_reactor)

    def _on_arc_clicked(self):
        self.voice.play_tone(784, 130)
        msg = self.brain.ask_topic(random.choice(["heroi", "elogio", "espaco", "animais"]))
        self.say(msg)

    def _add_star(self):
        self.stars_earned += 1
        self.stars_label.configure(text=f"★ {self.stars_earned} Estrelas")
        self.voice.play_tone(523, 90)
        self.root.after(100, lambda: self.voice.play_tone(659, 90))
        self.root.after(200, lambda: self.voice.play_tone(784, 150))

    # ==========================================================================
    # ABERTURA DOS NOVOS PILARES EDUCATIVOS
    # ==========================================================================
    def _open_book_library(self):
        BookLibraryModal(self)

    def _open_tech_academy(self):
        TechAcademyModal(self)

    def _open_emotions_center(self):
        EmotionsCenterModal(self)

    def _open_cinema_stark(self):
        CinemaStarkModal(self)

    # ==========================================================================
    # LANÇADORES EXTERNOS (LINUX) COM FALLBACK INTEGRADO
    # ==========================================================================
    def _launch_external_app(self, candidates: list, label: str) -> bool:
        for cmd_list in candidates:
            exe = cmd_list[0]
            if shutil.which(exe):
                self.say(f"Abrindo {label}! Divirta-se, {self.brain.name}!")
                try:
                    subprocess.Popen(cmd_list)
                    return True
                except Exception:
                    pass
        return False

    def _launch_gcompris_or_shapes(self):
        launched = self._launch_external_app(
            [["gcompris-qt", "--software-renderer", "-f"], ["gcompris"]],
            "o GCompris Jogos Educativos",
        )
        if not launched:
            self._open_colors_mission()

    def _launch_tuxpaint_or_draw(self):
        launched = self._launch_external_app(
            [["tuxpaint", "--fullscreen", "--1024x600", "--nolockfile"], ["tuxpaint"]],
            "o Laboratório Tux Paint",
        )
        if not launched:
            self._open_stark_paint()

    def _create_activity_window(self, title: str):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=self.BG_DARK)
        win.geometry("1024x600")
        if self.kiosk:
            win.attributes("-fullscreen", True)
        win.transient(self.root)
        win.grab_set()

        header = tk.Frame(win, bg="#071120", height=52, highlightthickness=1, highlightbackground=self.CYAN)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Button(
            header,
            text="⬅ VOLTAR AO JARVIS",
            fg="#ffffff",
            bg=self.RED_STARK,
            activebackground="#dc2626",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=14,
            pady=5,
            cursor="hand2",
            command=win.destroy,
        ).pack(side="left", padx=12, pady=7)

        tk.Label(
            header, text=title, fg=self.CYAN, bg="#071120", font=("Arial", 13, "bold")
        ).pack(side="left", padx=14)

        return win

    # ==========================================================================
    # MÓDULOS CLÁSSICOS: PINTURA, PIANO, CORES E CONVERSA/FOGUETES
    # ==========================================================================
    def _open_stark_paint(self):
        win = self._create_activity_window("✎ LOUSA HOLOGRÁFICA STARK")
        self.say(f"Lousa mágica ligada, {self.brain.name}! Escolha uma cor e desenhe com o mouse!")

        toolbar = tk.Frame(win, bg=self.PANEL_BG, pady=8)
        toolbar.pack(fill="x")

        current_color = tk.StringVar(value="#00f0ff")
        colors = [
            ("Azul Stark", "#00f0ff"),
            ("Vermelho", "#ef4444"),
            ("Amarelo Sol", "#facc15"),
            ("Verde", "#22c55e"),
            ("Laranja", "#fb923c"),
            ("Rosa", "#f472b6"),
            ("Branco", "#ffffff"),
        ]

        for cname, hex_c in colors:
            tk.Button(
                toolbar,
                text="   ",
                bg=hex_c,
                activebackground=hex_c,
                width=4,
                height=2,
                relief="raised",
                bd=3,
                cursor="hand2",
                command=lambda c=hex_c, n=cname: (current_color.set(c), self.say(f"Cor {n}!")),
            ).pack(side="left", padx=8)

        canvas = tk.Canvas(win, bg="#030712", highlightthickness=2, highlightbackground=self.CYAN_DIM, cursor="pencil")
        canvas.pack(fill="both", expand=True, padx=14, pady=10)

        tk.Button(
            toolbar,
            text="✨ LIMPAR TELA",
            bg=self.PURPLE,
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
            command=lambda: (canvas.delete("all"), self.say("Tela limpinha para um novo desenho!")),
        ).pack(side="right", padx=14)

        last_pos = {"x": None, "y": None}

        def start_draw(e):
            last_pos["x"], last_pos["y"] = e.x, e.y

        def draw(e):
            if last_pos["x"] is not None:
                canvas.create_line(
                    last_pos["x"], last_pos["y"], e.x, e.y, fill=current_color.get(), width=10, capstyle="round", smooth=True
                )
            last_pos["x"], last_pos["y"] = e.x, e.y

        canvas.bind("<ButtonPress-1>", start_draw)
        canvas.bind("<B1-Motion>", draw)
        canvas.bind("<ButtonRelease-1>", lambda _e: last_pos.update({"x": None, "y": None}))

    def _open_music_synth(self):
        win = self._create_activity_window("♪ SINTETIZADOR MUSICAL STARK")
        self.say("Toque nas teclas coloridas ou aperte o teclado para fazer música e estrelas!")

        sky = tk.Canvas(win, bg="#050b18", height=250, highlightthickness=0)
        sky.pack(fill="both", expand=True, padx=16, pady=(10, 6))

        keys_frame = tk.Frame(win, bg=self.BG_DARK, height=220)
        keys_frame.pack(fill="x", padx=16, pady=(4, 16))

        notes = [
            ("DÓ", 262, "#ef4444"),
            ("RÉ", 294, "#f97316"),
            ("MI", 330, "#facc15"),
            ("FÁ", 349, "#22c55e"),
            ("SOL", 392, "#06b6d4"),
            ("LÁ", 440, "#3b82f6"),
            ("SI", 494, "#a855f7"),
            ("DÓ+", 523, "#ec4899"),
        ]

        def spawn_star(color, label_txt=""):
            x, y, r = random.randint(60, 920), random.randint(40, 210), random.randint(22, 42)
            sky.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="#ffffff", width=2)
            if label_txt:
                sky.create_text(x, y, text=label_txt, fill="#ffffff", font=("Arial", 14, "bold"))
            if len(sky.find_all()) > 50:
                for item in sky.find_all()[:6]:
                    sky.delete(item)

        for n_name, freq, col in notes:
            tk.Button(
                keys_frame,
                text=n_name,
                bg=col,
                fg="#ffffff",
                font=("Arial", 18, "bold"),
                height=5,
                relief="raised",
                bd=4,
                cursor="hand2",
                command=lambda n=n_name, f=freq, c=col: (self.voice.play_tone(f, 240), spawn_star(c, n)),
            ).pack(side="left", fill="both", expand=True, padx=5)

        win.bind(
            "<Key>",
            lambda e: (
                self.voice.play_tone(random.choice(notes)[1], 200),
                spawn_star(random.choice(notes)[2], e.char.upper() if e.char and e.char.isalnum() else "★"),
            ),
        )

    def _open_colors_mission(self):
        win = self._create_activity_window("❖ MISSÃO STARK: CORES E FORMAS")
        prompt_lbl = tk.Label(win, text="", fg="#ffffff", bg=self.BG_DARK, font=("Arial", 20, "bold"), pady=14)
        prompt_lbl.pack()

        board = tk.Frame(win, bg=self.BG_DARK)
        board.pack(expand=True, fill="both", padx=30, pady=10)

        items = [
            ("VERMELHO", "#ef4444", "● CÍRCULO"),
            ("AZUL", "#3b82f6", "■ QUADRADO"),
            ("AMARELO", "#eab308", "▲ TRIÂNGULO"),
            ("VERDE", "#10b981", "★ ESTRELA"),
        ]
        target = {"name": "AZUL"}

        def next_round():
            for w in board.winfo_children():
                w.destroy()
            shuffled = list(items)
            random.shuffle(shuffled)
            chosen = random.choice(shuffled)
            target["name"] = chosen[0]
            instruction = f"{self.brain.name}, toque no botão {chosen[0]}!"
            prompt_lbl.configure(text=instruction)
            self.say(instruction)

            for cname, hex_c, shape_txt in shuffled:
                tk.Button(
                    board,
                    text=f"{shape_txt}\n\n{cname}",
                    bg=hex_c,
                    fg="#ffffff",
                    font=("Arial", 20, "bold"),
                    relief="raised",
                    bd=6,
                    cursor="hand2",
                    command=lambda c=cname: check_choice(c),
                ).pack(side="left", expand=True, fill="both", padx=12, pady=20)

        def check_choice(picked: str):
            if picked == target["name"]:
                self._add_star()
                self.say(f"Isso mesmo! Você achou o {picked}! Ganhou uma estrela Stark!")
                win.after(2200, next_round)
            else:
                self.voice.play_tone(220, 200)
                self.say(f"Esse é o {picked}! Tente encontrar o {target['name']}!")

        next_round()

    def _open_talk_hub(self):
        win = self._create_activity_window("🚀 CONVERSAR COM O JARVIS & CONTAR FOGUETES")

        ans_box = tk.Label(
            win,
            text=f"Sobre o que vamos conversar agora, {self.brain.name}?",
            fg="#f8fafc",
            bg="#0a192f",
            font=("Arial", 15, "bold"),
            wraplength=920,
            height=4,
            padx=18,
            pady=10,
            highlightthickness=2,
            highlightbackground=self.CYAN,
        )
        ans_box.pack(fill="x", padx=24, pady=12)

        grid = tk.Frame(win, bg=self.BG_DARK)
        grid.pack(expand=True, fill="both", padx=24, pady=4)

        topics = [
            ("🚀 ESPAÇO E PLANETAS", "espaco", "#0284c7"),
            ("🦖 DINOSSAUROS", "dinossauros", "#16a34a"),
            ("🦁 ANIMAIS DA SELVA", "animais", "#ea580c"),
            ("🦸 SUPER-HERÓI STARK", "heroi", "#dc2626"),
            ("🔢 CONTAR ATÉ DEZ", "numeros", "#9333ea"),
            ("⭐ ELOGIO DO JARVIS", "elogio", "#ca8a04"),
        ]

        def trigger_topic(t_key):
            self.voice.play_tone(659, 100)
            reply = self.brain.ask_topic(t_key)
            ans_box.configure(text=reply)
            self.say(reply)

        for idx, (label, key, col) in enumerate(topics):
            r, c = divmod(idx, 3)
            grid.columnconfigure(c, weight=1)
            grid.rowconfigure(r, weight=1)
            tk.Button(
                grid,
                text=label,
                bg=col,
                fg="#ffffff",
                font=("Arial", 14, "bold"),
                relief="raised",
                bd=4,
                cursor="hand2",
                command=lambda k=key: trigger_topic(k),
            ).grid(row=r, column=c, sticky="nsew", padx=8, pady=8)

        ask_bar = tk.Frame(win, bg=self.BG_DARK)
        ask_bar.pack(fill="x", padx=24, pady=(4, 14))

        q_entry = tk.Entry(ask_bar, font=("Arial", 13), bg="#1e293b", fg="#ffffff", insertbackground="#ffffff")
        q_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))

        def send_custom(_e=None):
            q = q_entry.get().strip()
            if not q:
                return
            q_entry.delete(0, "end")
            reply = self.brain.ask_custom(q)
            ans_box.configure(text=reply)
            self.say(reply)

        q_entry.bind("<Return>", send_custom)
        tk.Button(
            ask_bar,
            text="Perguntar ao JARVIS",
            bg=self.CYAN,
            fg="#040914",
            font=("Arial", 12, "bold"),
            padx=16,
            pady=6,
            command=send_custom,
        ).pack(side="right")

    # ==========================================================================
    # PAINEL DOS PAIS (HORÁRIO DE CINEMA, REGRA DE LIVRO, SELETOR DE IA)
    # ==========================================================================
    def _open_parent_gate(self):
        gate = tk.Toplevel(self.root)
        gate.title("Acesso dos Pais")
        gate.configure(bg=self.PANEL_BG)
        gate.geometry("420x230")
        gate.transient(self.root)
        gate.grab_set()

        a, b = random.randint(6, 12), random.randint(4, 9)
        tk.Label(
            gate,
            text=f"🔒 Área dos Pais — Quanto é {a} + {b}?",
            fg="#ffffff",
            bg=self.PANEL_BG,
            font=("Arial", 13, "bold"),
        ).pack(pady=(24, 12))

        ans_entry = tk.Entry(gate, font=("Arial", 16), justify="center", width=10)
        ans_entry.pack(pady=8)
        ans_entry.focus_set()

        def verify(_e=None):
            if ans_entry.get().strip() == str(a + b):
                gate.destroy()
                self._open_parent_settings()
            else:
                messagebox.showwarning("Acesso Restrito", "Resposta incorreta.", parent=gate)

        ans_entry.bind("<Return>", verify)
        tk.Button(
            gate, text="Confirmar", bg=self.CYAN, fg="#000000", font=("Arial", 11, "bold"), padx=18, pady=6, command=verify
        ).pack(pady=12)

    def _open_parent_settings(self):
        cfg_win = tk.Toplevel(self.root)
        cfg_win.title("Configurações dos Pais — Educação do Tempo, Leitura & IA")
        cfg_win.configure(bg=self.PANEL_BG)
        cfg_win.geometry("760x570")
        cfg_win.transient(self.root)
        cfg_win.grab_set()

        tk.Label(
            cfg_win,
            text="⚙ Painel dos Pais — Rotina de Vídeo, Leitura & Motor IA",
            fg=self.CYAN,
            bg=self.PANEL_BG,
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        form = tk.Frame(cfg_win, bg=self.PANEL_BG)
        form.pack(fill="both", expand=True, padx=24)

        tk.Label(form, text="Nome da Criança:", fg="#cbd5e1", bg=self.PANEL_BG).grid(row=0, column=0, sticky="w", pady=5)
        name_var = tk.StringVar(value=self.brain.config.get("child_name", "Pequeno Inventor"))
        tk.Entry(form, textvariable=name_var, width=32, font=("Arial", 11)).grid(row=0, column=1, sticky="w", pady=5)

        tk.Label(form, text="Horário Permitido Netflix/YouTube (HH:MM):", fg="#fde047", bg=self.PANEL_BG, font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        sched_frame = tk.Frame(form, bg=self.PANEL_BG)
        sched_frame.grid(row=1, column=1, sticky="w", pady=5)
        start_var = tk.StringVar(value=self.brain.config.get("media_start_time", "16:00"))
        end_var = tk.StringVar(value=self.brain.config.get("media_end_time", "17:00"))
        tk.Entry(sched_frame, textvariable=start_var, width=8, font=("Arial", 11)).pack(side="left")
        tk.Label(sched_frame, text=" até ", fg="#cbd5e1", bg=self.PANEL_BG).pack(side="left")
        tk.Entry(sched_frame, textvariable=end_var, width=8, font=("Arial", 11)).pack(side="left")

        tk.Label(form, text="Tempo Máximo de Vídeo por Dia (minutos):", fg="#fde047", bg=self.PANEL_BG, font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        limit_var = tk.StringVar(value=str(self.brain.config.get("media_daily_minutes", 25)))
        tk.Entry(form, textvariable=limit_var, width=10, font=("Arial", 11)).grid(row=2, column=1, sticky="w", pady=5)

        req_book_var = tk.BooleanVar(value=self.brain.config.get("require_book_before_media", True))
        tk.Checkbutton(
            form,
            text="📚 Exigir leitura de pelo menos 1 Livro no dia antes de liberar Netflix / YouTube Kids",
            variable=req_book_var,
            bg=self.PANEL_BG,
            fg="#4ade80",
            selectcolor="#0f172a",
            font=("Arial", 10, "bold"),
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=6)

        tk.Label(form, text="Motor de IA (offline / ollama / cloud):", fg="#cbd5e1", bg=self.PANEL_BG).grid(row=4, column=0, sticky="w", pady=5)
        mode_var = tk.StringVar(value=self.brain.config.get("mode", "offline"))
        tk.OptionMenu(form, mode_var, "offline", "ollama", "cloud").grid(row=4, column=1, sticky="w", pady=5)

        tk.Label(form, text="URL Ollama na Rede (se 'ollama'):", fg="#cbd5e1", bg=self.PANEL_BG).grid(row=5, column=0, sticky="w", pady=5)
        ollama_url_var = tk.StringVar(value=self.brain.config.get("ollama_url", "http://127.0.0.1:11434"))
        tk.Entry(form, textvariable=ollama_url_var, width=32, font=("Arial", 10)).grid(row=5, column=1, sticky="w", pady=5)

        tk.Label(form, text="Provedor Cloud & API Key (opcional):", fg="#cbd5e1", bg=self.PANEL_BG).grid(row=6, column=0, sticky="w", pady=5)
        cloud_row = tk.Frame(form, bg=self.PANEL_BG)
        cloud_row.grid(row=6, column=1, sticky="w", pady=5)
        cloud_prov_var = tk.StringVar(value=self.brain.config.get("cloud_provider", "groq"))
        tk.OptionMenu(cloud_row, cloud_prov_var, "groq", "gemini", "openai").pack(side="left", padx=(0, 6))
        api_key_var = tk.StringVar(value=self.brain.config.get("cloud_api_key", ""))
        tk.Entry(cloud_row, textvariable=api_key_var, show="*", width=20, font=("Arial", 10)).pack(side="left")

        voice_var = tk.BooleanVar(value=self.brain.config.get("voice_enabled", True))
        tk.Checkbutton(
            form,
            text="Ativar Voz Falada do JARVIS e Efeitos Sonoros",
            variable=voice_var,
            bg=self.PANEL_BG,
            fg="#ffffff",
            selectcolor="#0f172a",
        ).grid(row=7, column=0, columnspan=2, sticky="w", pady=6)

        def grant_now():
            self.media_mgr.grant_bonus_minutes(15)
            messagebox.showinfo(
                "Sessão Liberada",
                "Foram liberados +15 minutos imediatos de Cinema Stark para hoje (mesmo fora do horário padrão)!",
                parent=cfg_win,
            )

        tk.Button(
            form,
            text="🎁 Liberar +15 Minutos de Cinema Agora (Exceção dos Pais)",
            bg="#0284c7",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=6,
            command=grant_now,
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=8)

        def save_all():
            self.brain.config["child_name"] = name_var.get().strip() or "Pequeno Inventor"
            self.brain.config["media_start_time"] = start_var.get().strip() or "16:00"
            self.brain.config["media_end_time"] = end_var.get().strip() or "17:00"
            try:
                self.brain.config["media_daily_minutes"] = max(1, int(limit_var.get().strip()))
            except ValueError:
                self.brain.config["media_daily_minutes"] = 25
            self.brain.config["require_book_before_media"] = req_book_var.get()
            self.brain.config["mode"] = mode_var.get()
            self.brain.config["ollama_url"] = ollama_url_var.get().strip()
            self.brain.config["cloud_provider"] = cloud_prov_var.get()
            self.brain.config["cloud_api_key"] = api_key_var.get().strip()
            self.brain.config["voice_enabled"] = voice_var.get()
            self.brain.save_config()
            self.voice.muted = not voice_var.get()
            self._update_mode_badge()
            cfg_win.destroy()
            self.say(f"Configurações salvas! Tudo pronto para aprender e brincar, {self.brain.name}!")

        btn_bar = tk.Frame(cfg_win, bg=self.PANEL_BG)
        btn_bar.pack(fill="x", padx=24, pady=12)

        tk.Button(
            btn_bar, text="💾 Salvar Configurações", bg=self.GREEN_OK, fg="#ffffff", font=("Arial", 11, "bold"), padx=14, pady=8, command=save_all
        ).pack(side="left")

        tk.Button(
            btn_bar,
            text="🚪 Fechar JARVIS (Sair p/ Desktop)",
            bg=self.ORANGE,
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=8,
            command=self.root.destroy,
        ).pack(side="right", padx=6)

        if platform.system().lower() == "linux":
            tk.Button(
                btn_bar,
                text="⏻ Desligar Netbook",
                bg=self.RED_STARK,
                fg="#ffffff",
                font=("Arial", 10, "bold"),
                padx=12,
                pady=8,
                command=lambda: subprocess.Popen(["systemctl", "poweroff"]),
            ).pack(side="right", padx=6)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    kiosk_flag = "--kiosk" in sys.argv
    app = JarvisKidsOS(kiosk=kiosk_flag)
    app.run()
