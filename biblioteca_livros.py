import tkinter as tk


BOOKS = [
    {
        "id": "segredo_livros",
        "title": "O Segredo dos Livros Mágicos",
        "theme_color": "#0284c7",
        "pages": [
            {
                "scene": "book_glow",
                "word": "LIVRO",
                "text": "Era uma vez um pequeno inventor que descobriu um objeto mágico na estante: um LIVRO brilhante!",
            },
            {
                "scene": "rocket",
                "word": "VIAGEM",
                "text": "Sem sair da cadeira, cada página aberta levava ele para uma VIAGEM até as estrelas e planetas distantes!",
            },
            {
                "scene": "castle",
                "word": "IMAGINAR",
                "text": "Nos livros moram dragões amigos, florestas encantadas e robôs falantes. Ler faz a nossa mente IMAGINAR!",
            },
            {
                "scene": "heart",
                "word": "SABER",
                "text": "Quem lê um pouquinho todos os dias ganha o maior superpoder do universo: o poder de SABER e sonhar!",
            },
        ],
    },
    {
        "id": "tudo_tem_hora",
        "title": "Tudo Tem o Seu Tempo",
        "theme_color": "#d97706",
        "pages": [
            {
                "scene": "sun",
                "word": "TEMPO",
                "text": "O Sol nasce de manhãzinha e a Lua aparece de noite. Na natureza, tudo respeita o seu TEMPO!",
            },
            {
                "scene": "book_glow",
                "word": "LER",
                "text": "Existe a hora gostosa de LER histórias, desenhar, correr pela casa e montar brinquedos!",
            },
            {
                "scene": "clock",
                "word": "COMBINADO",
                "text": "Também existe um horarinho curto para assistir desenhos. E quando o relógio avisa, cumprimos o COMBINADO!",
            },
            {
                "scene": "star",
                "word": "HERÓI",
                "text": "Desligar a telinha na hora certa com alegria mostra que você já é um verdadeiro HERÓI crescido!",
            },
        ],
    },
    {
        "id": "dragao_calma",
        "title": "O Dragãozinho que Aprendeu a Respirar",
        "theme_color": "#16a34a",
        "pages": [
            {
                "scene": "fire",
                "word": "BRAVO",
                "text": "Faisquinha era um dragãozinho legal, mas quando sua torre de blocos caía, ele ficava muito BRAVO!",
            },
            {
                "scene": "cloud",
                "word": "SENTIR",
                "text": "A mamãe dragoa explicou: Todo mundo pode SENTIR raiva ou frustração, mas não precisamos soltar fogo!",
            },
            {
                "scene": "flower",
                "word": "RESPIRAR",
                "text": "Ela ensinou um truque mágico: cheirar uma florzinha bem fundo e soprar uma velinha devagar para RESPIRAR!",
            },
            {
                "scene": "smile",
                "word": "CALMA",
                "text": "Depois de três respirações, a CALMA voltou ao coração de Faisquinha, e ele montou uma torre ainda maior!",
            },
        ],
    },
    {
        "id": "amigos_gentis",
        "title": "As Palavras Mágicas da Floresta",
        "theme_color": "#9333ea",
        "pages": [
            {
                "scene": "tree",
                "word": "AMIGOS",
                "text": "Na floresta iluminada, o coelhinho, a coruja e o ursinho adoravam brincar juntos como grandes AMIGOS.",
            },
            {
                "scene": "gift",
                "word": "POR FAVOR",
                "text": "Quando alguém queria um brinquedo emprestado, usava a chave dourada: você me empresta, POR FAVOR?",
            },
            {
                "scene": "heart",
                "word": "OBRIGADO",
                "text": "E ao receber ajuda ou carinho, todos sorriam dizendo uma palavra que aquece o peito: muito OBRIGADO!",
            },
            {
                "scene": "star",
                "word": "AMOR",
                "text": "Com gentileza, respeito e AMOR, qualquer dia comum vira uma grande aventura feliz!",
            },
        ],
    },
]


def draw_book_illustration(canvas: tk.Canvas, scene: str):
    """Desenha ilustrações vetoriais leves (< 1ms CPU no Atom N450) para cada página do livro."""
    canvas.delete("all")
    w = int(canvas["width"])
    h = int(canvas["height"])
    cx, cy = w // 2, h // 2

    # Fundo estrelado suave
    for sx, sy in [(40, 35), (w - 50, 45), (75, h - 40), (w - 70, h - 35), (140, 28), (w - 140, 32)]:
        canvas.create_oval(sx - 2, sy - 2, sx + 2, sy + 2, fill="#bae6fd", outline="")

    if scene == "book_glow":
        canvas.create_oval(cx - 75, cy - 75, cx + 75, cy + 75, fill="#0c4a6e", outline="#38bdf8", width=2)
        canvas.create_rectangle(cx - 55, cy - 35, cx - 3, cy + 40, fill="#f8fafc", outline="#0284c7", width=3)
        canvas.create_rectangle(cx + 3, cy - 35, cx + 55, cy + 40, fill="#f1f5f9", outline="#0284c7", width=3)
        for dy in (-18, -4, 10, 24):
            canvas.create_line(cx - 45, cy + dy, cx - 12, cy + dy, fill="#64748b", width=3)
            canvas.create_line(cx + 12, cy + dy, cx + 45, cy + dy, fill="#64748b", width=3)
    elif scene == "rocket":
        canvas.create_oval(cx - 60, cy - 60, cx + 60, cy + 60, fill="#1e1b4b", outline="#818cf8", width=2)
        canvas.create_polygon(cx, cy - 55, cx - 26, cy + 20, cx + 26, cy + 20, fill="#ef4444", outline="#ffffff", width=2)
        canvas.create_oval(cx - 12, cy - 22, cx + 12, cy + 2, fill="#38bdf8", outline="#ffffff", width=2)
        canvas.create_polygon(cx - 16, cy + 22, cx, cy + 58, cx + 16, cy + 22, fill="#facc15", outline="")
    elif scene == "sun":
        for ang in range(0, 360, 30):
            import math
            r1, r2 = 52, 74
            x1, y1 = cx + r1 * math.cos(math.radians(ang)), cy + r1 * math.sin(math.radians(ang))
            x2, y2 = cx + r2 * math.cos(math.radians(ang)), cy + r2 * math.sin(math.radians(ang))
            canvas.create_line(x1, y1, x2, y2, fill="#fde047", width=5)
        canvas.create_oval(cx - 45, cy - 45, cx + 45, cy + 45, fill="#facc15", outline="#fef08a", width=3)
    elif scene == "clock":
        canvas.create_oval(cx - 58, cy - 58, cx + 58, cy + 58, fill="#fef3c7", outline="#f59e0b", width=6)
        canvas.create_line(cx, cy, cx, cy - 36, fill="#1e293b", width=5)
        canvas.create_line(cx, cy, cx + 28, cy + 10, fill="#dc2626", width=4)
        canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#1e293b")
    elif scene == "flower":
        canvas.create_line(cx, cy + 10, cx, cy + 68, fill="#22c55e", width=7)
        for dx, dy in [(-26, -15), (26, -15), (0, -36), (-22, 16), (22, 16)]:
            canvas.create_oval(cx + dx - 20, cy + dy - 20, cx + dx + 20, cy + dy + 20, fill="#f472b6", outline="#fbcfe8", width=2)
        canvas.create_oval(cx - 18, cy - 18, cx + 18, cy + 18, fill="#facc15", outline="#fef08a", width=2)
    elif scene in ("heart", "gift"):
        canvas.create_oval(cx - 48, cy - 42, cx + 2, cy + 8, fill="#ec4899", outline="")
        canvas.create_oval(cx - 2, cy - 42, cx + 48, cy + 8, fill="#ec4899", outline="")
        canvas.create_polygon(cx - 48, cy - 10, cx + 48, cy - 10, cx, cy + 52, fill="#ec4899", outline="")
    elif scene in ("fire", "cloud"):
        color = "#f97316" if scene == "fire" else "#60a5fa"
        canvas.create_oval(cx - 50, cy - 35, cx + 50, cy + 45, fill=color, outline="#ffffff", width=2)
        canvas.create_oval(cx - 25, cy - 52, cx + 25, cy + 10, fill="#fbbf24" if scene == "fire" else "#93c5fd", outline="")
    elif scene in ("smile", "star", "castle", "tree"):
        canvas.create_oval(cx - 54, cy - 54, cx + 54, cy + 54, fill="#22c55e" if scene == "tree" else "#eab308", outline="#fef08a", width=4)
        canvas.create_oval(cx - 22, cy - 20, cx - 10, cy - 8, fill="#0f172a")
        canvas.create_oval(cx + 10, cy - 20, cx + 22, cy - 8, fill="#0f172a")
        canvas.create_arc(cx - 28, cy - 10, cx + 28, cy + 32, start=200, extent=140, style="arc", outline="#0f172a", width=5)


class BookLibraryModal:
    """Modal interativo da Biblioteca Stark — Base Principal de Leitura Diária."""

    def __init__(self, os_app):
        self.os_app = os_app
        self.win = os_app._create_activity_window("📚 BIBLIOTECA HOLOGRÁFICA STARK (HÁBITO DE LER)")
        self.current_book = None
        self.page_idx = 0

        self.body = tk.Frame(self.win, bg=os_app.BG_DARK)
        self.body.pack(fill="both", expand=True, padx=20, pady=12)

        self._render_shelf()

    def _clear_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    def _render_shelf(self):
        self._clear_body()
        read_today = self.os_app.media_mgr.get_books_read_today()

        banner = tk.Frame(self.body, bg="#0c1e35", highlightthickness=2, highlightbackground="#38bdf8", pady=10, padx=16)
        banner.pack(fill="x", pady=(0, 14))

        tk.Label(
            banner,
            text=f"📖 Livros lidos hoje: {read_today}   |   Escolha uma história para ouvir, ver as palavras e ganhar Medalhas de Leitor!",
            fg="#f0f9ff",
            bg="#0c1e35",
            font=("Arial", 13, "bold"),
        ).pack()

        shelf = tk.Frame(self.body, bg=self.os_app.BG_DARK)
        shelf.pack(fill="both", expand=True)

        all_books = list(BOOKS) + self.os_app.brain.config.get("custom_books", [])

        for idx, book in enumerate(all_books):
            r, c = divmod(idx, 2)
            shelf.columnconfigure(c, weight=1)
            shelf.rowconfigure(r, weight=1)

            card = tk.Frame(
                shelf,
                bg=book.get("theme_color", "#0284c7"),
                highlightthickness=3,
                highlightbackground="#e0f2fe",
                padx=18,
                pady=16,
                cursor="hand2",
            )
            card.grid(row=r, column=c, sticky="nsew", padx=10, pady=10)

            lbl = tk.Label(
                card,
                text=f"📘 {book['title']}",
                fg="#ffffff",
                bg=book.get("theme_color", "#0284c7"),
                font=("Arial", 17, "bold"),
                wraplength=400,
                justify="center",
            )
            lbl.pack(expand=True)

            sub = tk.Label(
                card,
                text=f"{len(book['pages'])} páginas ilustradas • Toque para abrir!",
                fg="#f0f9ff",
                bg=book.get("theme_color", "#0284c7"),
                font=("Arial", 11),
            )
            sub.pack()

            for w in (card, lbl, sub):
                w.bind("<Button-1>", lambda _e, b=book: self._open_book(b))

        self.os_app.say(
            f"Bem-vindo à Biblioteca Stark, {self.os_app.brain.name}! Escolha um livro colorido para lermos juntos!"
        )

    def _open_book(self, book: dict):
        self.current_book = book
        self.page_idx = 0
        self._render_page()

    def _render_page(self):
        self._clear_body()
        book = self.current_book
        pages = book["pages"]
        page = pages[self.page_idx]

        top_info = tk.Frame(self.body, bg=self.os_app.BG_DARK)
        top_info.pack(fill="x", pady=(0, 6))

        tk.Button(
            top_info,
            text="📚 Outros Livros",
            bg="#1e293b",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=12,
            pady=4,
            command=self._render_shelf,
        ).pack(side="left")

        tk.Label(
            top_info,
            text=f"{book['title']}  —  Página {self.page_idx + 1} de {len(pages)}",
            fg="#38bdf8",
            bg=self.os_app.BG_DARK,
            font=("Arial", 13, "bold"),
        ).pack(side="right")

        # Área principal do livro aberto
        book_frame = tk.Frame(
            self.body, bg="#0b192c", highlightthickness=3, highlightbackground=book.get("theme_color", "#0284c7")
        )
        book_frame.pack(fill="both", expand=True, pady=6)

        left_art = tk.Frame(book_frame, bg="#081221", width=330)
        left_art.pack(side="left", fill="y", padx=12, pady=12)

        art_canvas = tk.Canvas(left_art, width=300, height=220, bg="#081221", highlightthickness=0)
        art_canvas.pack(pady=10)
        draw_book_illustration(art_canvas, page.get("scene", "star"))

        # Palavra-chave gigante para pré-alfabetização!
        word_btn = tk.Button(
            left_art,
            text=f"🔤 {page['word']}",
            bg="#facc15",
            fg="#0f172a",
            font=("Arial", 22, "bold"),
            relief="raised",
            bd=4,
            padx=16,
            pady=6,
            cursor="hand2",
            command=lambda w=page["word"]: self._spell_word(w),
        )
        word_btn.pack(pady=6)

        tk.Label(
            left_art,
            text="Toque na palavra amarela para soletrar!",
            fg="#94a3b8",
            bg="#081221",
            font=("Arial", 9),
        ).pack()

        # Texto da história em letras grandes e confortáveis
        right_txt = tk.Frame(book_frame, bg="#0b192c")
        right_txt.pack(side="left", fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            right_txt,
            text=page["text"],
            fg="#ffffff",
            bg="#0b192c",
            font=("Arial", 20, "bold"),
            wraplength=540,
            justify="left",
        ).pack(expand=True, fill="both")

        # Controles de navegação da história
        nav = tk.Frame(self.body, bg=self.os_app.BG_DARK)
        nav.pack(fill="x", pady=(8, 0))

        if self.page_idx > 0:
            tk.Button(
                nav,
                text="⬅ Página Anterior",
                bg="#334155",
                fg="#ffffff",
                font=("Arial", 13, "bold"),
                padx=18,
                pady=10,
                command=self._prev_page,
            ).pack(side="left")

        tk.Button(
            nav,
            text="🔊 Ouvir de Novo",
            bg="#0284c7",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
            padx=18,
            pady=10,
            command=lambda: self.os_app.say(page["text"]),
        ).pack(side="left", padx=12)

        if self.page_idx < len(pages) - 1:
            tk.Button(
                nav,
                text="Próxima Página ➡",
                bg="#10b981",
                fg="#ffffff",
                font=("Arial", 14, "bold"),
                padx=24,
                pady=10,
                command=self._next_page,
            ).pack(side="right")
        else:
            tk.Button(
                nav,
                text="🏆 Concluir Livro e Ganhar Medalha!",
                bg="#eab308",
                fg="#0f172a",
                font=("Arial", 14, "bold"),
                padx=22,
                pady=10,
                command=self._finish_book,
            ).pack(side="right")

        self.os_app.voice.play_tone(587, 110)
        self.os_app.say(page["text"])

    def _spell_word(self, word: str):
        letters = " ... ".join(list(word.replace(" ", "")))
        self.os_app.voice.play_tone(659, 100)
        self.os_app.say(f"A palavra é {word}! Vamos ouvir as letrinhas: {letters}. {word}!")

    def _prev_page(self):
        if self.page_idx > 0:
            self.page_idx -= 1
            self._render_page()

    def _next_page(self):
        if self.page_idx < len(self.current_book["pages"]) - 1:
            self.page_idx += 1
            self._render_page()

    def _finish_book(self):
        total_today = self.os_app.media_mgr.record_book_read(self.current_book["id"])
        self.os_app._add_star()
        self.os_app._add_star()
        self.os_app.update_books_badge()
        self.os_app.say(
            f"Parabéns, {self.os_app.brain.name}! Você terminou o livro {self.current_book['title']} e ganhou duas estrelas de super leitor! Você já leu {total_today} livro hoje!"
        )
        self._render_shelf()
