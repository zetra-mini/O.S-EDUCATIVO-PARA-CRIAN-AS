import tkinter as tk


BOOKS = [
    {
        "id": "tres_porquinhos",
        "title": "Os Três Porquinhos e a Casa Forte",
        "theme_color": "#d97706",
        "cover_emoji": "🐷",
        "pages": [
            {
                "scene": "pig_straw",
                "word": "PALHA",
                "tap_hint": "Toque no porquinho para ouvir o focinho!",
                "tap_sound": "oink",
                "text": "O primeiro porquinho fez uma casinha de PALHA fofa. Ele cantava alegre: 'Minha casa ficou pronta rapidinho!'",
            },
            {
                "scene": "pig_wood",
                "word": "MADEIRA",
                "tap_hint": "Toque na casinha para bater na madeira!",
                "tap_sound": "knock",
                "text": "O segundo porquinho juntou galhos e fez uma casa de MADEIRA. 'Aqui eu fico seguro para brincar!'",
            },
            {
                "scene": "pig_brick",
                "word": "TIJOLO",
                "tap_hint": "Toque na parede forte de ferro e tijolo!",
                "tap_sound": "clang",
                "text": "O terceiro porquinho trabalhou bastante e construiu uma casa forte de TIJOLO e ferro Stark!",
            },
            {
                "scene": "wolf_blow",
                "word": "SOPRAR",
                "tap_hint": "Toque no lobinho para respirar fundo com ele!",
                "tap_sound": "blow",
                "text": "O lobo assoprou forte, mas a casa de tijolos nem se mexeu! Os porquinhos convidaram o lobo para um lanche e viraram amigos!",
            },
        ],
    },
    {
        "id": "chapeuzinho_floresta",
        "title": "Chapeuzinho e a Floresta dos Amigos",
        "theme_color": "#dc2626",
        "cover_emoji": "👧",
        "pages": [
            {
                "scene": "basket_flowers",
                "word": "CESTA",
                "tap_hint": "Toque na cestinha para ver as frutinhas!",
                "tap_sound": "twinkle",
                "text": "Chapeuzinho Vermelho colocou maçãs doces e frutinhas na sua CESTA para levar para a vovó querida.",
            },
            {
                "scene": "tree_birds",
                "word": "FLORESTA",
                "tap_hint": "Toque nos passarinhos para ouvi-los cantar!",
                "tap_sound": "chirp",
                "text": "Pelo caminho na FLORESTA colorida, os passarinhos cantavam e as borboletas dançavam em volta do capuz vermelho.",
            },
            {
                "scene": "wolf_friendly",
                "word": "LOBO",
                "tap_hint": "Toque no lobinho amigo!",
                "tap_sound": "howl_soft",
                "text": "Ela encontrou um LOBO amigável que adorava flores. Ele ajudou a colher margaridas amarelas para a vovó!",
            },
            {
                "scene": "grandma_tea",
                "word": "ABRAÇO",
                "tap_hint": "Toque no coração do abraço!",
                "tap_sound": "heartbeat",
                "text": "Na casa da vovó, todos tomaram chá quentinho e deram um grande ABRAÇO apertado e carinhoso!",
            },
        ],
    },
    {
        "id": "leao_ratinho",
        "title": "O Leão e o Ratinho Valente",
        "theme_color": "#16a34a",
        "cover_emoji": "🦁",
        "pages": [
            {
                "scene": "lion_sleep",
                "word": "LEÃO",
                "tap_hint": "Toque no leão para ouvir o soninho dele!",
                "tap_sound": "snore",
                "text": "O grande LEÃO tirava uma soneca debaixo da árvore. Um ratinho curioso passou correndo perto da sua juba.",
            },
            {
                "scene": "mouse_small",
                "word": "RATINHO",
                "tap_hint": "Toque no ratinho para ouvir: 'Queek queek'!",
                "tap_sound": "squeak",
                "text": "O leão acordou, mas o pequeno RATINHO pediu com jeitinho: 'Por favor, amigo, um dia eu posso ajudar você!'",
            },
            {
                "scene": "lion_net",
                "word": "AJUDA",
                "tap_hint": "Toque nos dentinhos do ratinho roendo!",
                "tap_sound": "nibble",
                "text": "Dias depois, o leão ficou preso numa corda. O ratinho ouviu e correu para dar AJUDA, roendo os nós bem rapidinho!",
            },
            {
                "scene": "friends_smile",
                "word": "AMIGOS",
                "tap_hint": "Toque nas estrelas da amizade!",
                "tap_sound": "cheer",
                "text": "O leão agradeceu de coração: 'Mesmo pequenininho, você é um herói!' E os dois se tornaram grandes AMIGOS!",
            },
        ],
    },
    {
        "id": "dino_tito",
        "title": "O Dinossauro Tito que Adorava Abraços",
        "theme_color": "#0284c7",
        "cover_emoji": "🦖",
        "pages": [
            {
                "scene": "tito_dino",
                "word": "DINO",
                "tap_hint": "Toque no Tito para ouvir um rugidinho amigável!",
                "tap_sound": "roar_cute",
                "text": "Tito era um DINO verde muito forte, mas o que ele mais gostava no mundo inteiro não era rugir: era dar abraços!",
            },
            {
                "scene": "tall_neck",
                "word": "GIGANTE",
                "tap_hint": "Toque no pescoço do Braquiossauro!",
                "tap_sound": "bell",
                "text": "Quando o Braquiossauro GIGANTE ficava cansado de comer folhinhas no alto, Tito dava um abraço no pé dele para alegrar!",
            },
            {
                "scene": "pterodactyl",
                "word": "VOAR",
                "tap_hint": "Toque nas asinhas do pterodáctilo!",
                "tap_sound": "swoosh",
                "text": "Até o passarinho pré-histórico que adorava VOAR lá no céu descia na grama para receber o carinho de Tito.",
            },
            {
                "scene": "dino_party",
                "word": "ALEGRIA",
                "tap_hint": "Toque na festa para comemorar!",
                "tap_sound": "party",
                "text": "Na floresta dos dinossauros, o abraço quentinho de Tito espalhava paz, amor e muita ALEGRIA para todos!",
            },
        ],
    },
    {
        "id": "pequeno_astronauta",
        "title": "O Pequeno Astronauta e a Estrela Dourada",
        "theme_color": "#7c3aed",
        "cover_emoji": "🚀",
        "pages": [
            {
                "scene": "rocket_launch",
                "word": "FOGUETE",
                "tap_hint": "Toque no foguete para a contagem: 3, 2, 1, Decolar!",
                "tap_sound": "rocket_boost",
                "text": "Três, dois, um... FOGUETE ligado! O pequeno astronauta Stark decolou rumbando ao céu azul cheio de estrelas!",
            },
            {
                "scene": "moon_cheese",
                "word": "LUA",
                "tap_hint": "Toque na Lua brilhante!",
                "tap_sound": "moon_glow",
                "text": "Ele deu uma volta inteira na LUA brilhante e viu que a Terra lá embaixo parece uma bola de gude azul e verde.",
            },
            {
                "scene": "star_friend",
                "word": "ESTRELA",
                "tap_hint": "Toque na estrelinha piscando!",
                "tap_sound": "twinkle_bell",
                "text": "Uma ESTRELA dourada e sorridente piscou para ele: 'Obrigada pela visita, astronauta! Continue sonhando alto!'",
            },
            {
                "scene": "earth_bed",
                "word": "DORMIR",
                "tap_hint": "Toque na caminha quentinha!",
                "tap_sound": "lullaby",
                "text": "De volta para casa, era hora de guardar o capacete, abraçar o ursinho e DORMIR para ter sonhos mágicos!",
            },
        ],
    },
    {
        "id": "dragao_calma",
        "title": "Faisquinha: O Dragãozinho que Aprendeu a Soprar",
        "theme_color": "#059669",
        "cover_emoji": "🐲",
        "pages": [
            {
                "scene": "fire_tower",
                "word": "BRAVO",
                "tap_hint": "Toque nos bloquinhos que caíram!",
                "tap_sound": "tumble",
                "text": "Faisquinha estava montando uma torre linda, mas quando um bloquinho escorregou, ele ficou muito BRAVO!",
            },
            {
                "scene": "mom_dragon",
                "word": "SENTIR",
                "tap_hint": "Toque no coração da mamãe dragoa!",
                "tap_sound": "heartbeat",
                "text": "A mamãe ensinou: 'Todo mundo pode SENTIR raiva, mas podemos respirar como heróis para o fogo não queimar!'",
            },
            {
                "scene": "flower_candle",
                "word": "RESPIRAR",
                "tap_hint": "Toque na flor para cheirar e na vela para soprar!",
                "tap_sound": "breath_soft",
                "text": "Puxe o ar pelo nariz cheirando a florzinha, e solte devagar pela boca soprando a vela para RESPIRAR!",
            },
            {
                "scene": "peace_dragon",
                "word": "CALMA",
                "tap_hint": "Toque na estrela da calma!",
                "tap_sound": "zen_chime",
                "text": "Com a CALMA de volta no peito, Faisquinha deu uma gargalhada gostosa e construiu um castelo ainda mais alto!",
            },
        ],
    },
    {
        "id": "aventura_stark_decide",
        "title": "A Grande Aventura Espacial de Kaleo (Você Decide!)",
        "theme_color": "#e11d48",
        "cover_emoji": "⚡",
        "is_interactive": True,
        "pages": [
            {
                "scene": "stark_hangar",
                "word": "FOGUETE",
                "tap_hint": "Toque no Reator Arc para ligar os motores!",
                "tap_sound": "rocket_boost",
                "text": "O alarme Stark tocou! Járvis disse: 'Kaleo, os propulsores estão prontos para a nossa missão! Para onde vamos viajar?'",
                "decision": {
                    "question": "Para onde você quer viajar agora?",
                    "options": [
                        {
                            "label": "🦖 Planeta dos Dinos",
                            "icon": "🦖",
                            "sound": "roar_cute",
                            "next_text": "Você acelerou o foguete em direção ao Planeta dos Dinossauros! O T-Rex Tito acenou com alegria e dividiu frutinhas mágicas com você!",
                            "next_word": "AMIGOS"
                        },
                        {
                            "label": "🌟 Planeta dos Robôs",
                            "icon": "🤖",
                            "sound": "zen_chime",
                            "next_text": "Você ligou os propulsores velozes rumo ao Planeta dos Robôs! Robôs dançarinos tocaram uma música divertida e deram uma capa dourada para você!",
                            "next_word": "MÚSICA"
                        }
                    ]
                }
            },
            {
                "scene": "friends_smile",
                "word": "VITÓRIA",
                "tap_hint": "Toque na armadura para celebrar a vitória!",
                "tap_sound": "cheer",
                "text": "Com a missão cumprida, Kaleo voltou para casa aterrissando suavemente. Járvis exclamou: 'Você é o maior super-herói do universo!'",
            },
        ],
    },
]


def draw_book_illustration(canvas: tk.Canvas, scene: str):
    """Desenha ilustrações vetoriais vibrantes para cada página no Tkinter (Acer Aspire One)."""
    canvas.delete("all")
    w = int(canvas["width"])
    h = int(canvas["height"])
    cx, cy = w // 2, h // 2

    # Fundo estrelado
    for sx, sy in [(30, 25), (w - 40, 30), (50, h - 30), (w - 50, h - 35), (cx - 70, 20), (cx + 80, 25)]:
        canvas.create_oval(sx - 3, sy - 3, sx + 3, sy + 3, fill="#fef08a", outline="")

    if "pig" in scene or scene == "wolf_blow":
        canvas.create_oval(cx - 50, cy - 40, cx + 50, cy + 50, fill="#f472b6", outline="#ffffff", width=3)
        canvas.create_oval(cx - 24, cy - 6, cx + 24, cy + 24, fill="#ec4899", outline="#ffffff", width=2)
        canvas.create_oval(cx - 12, cy + 4, cx - 4, cy + 14, fill="#040914")
        canvas.create_oval(cx + 4, cy + 4, cx + 12, cy + 14, fill="#040914")
        canvas.create_oval(cx - 22, cy - 24, cx - 12, cy - 14, fill="#040914")
        canvas.create_oval(cx + 12, cy - 24, cx + 22, cy - 14, fill="#040914")
    elif "lion" in scene:
        canvas.create_oval(cx - 65, cy - 65, cx + 65, cy + 65, fill="#d97706", outline="#fbbf24", width=4)
        canvas.create_oval(cx - 42, cy - 42, cx + 42, cy + 42, fill="#facc15", outline="#ffffff", width=2)
        canvas.create_polygon(cx - 8, cy + 6, cx + 8, cy + 6, cx, cy + 16, fill="#78350f")
    elif "dino" in scene or scene == "tito_dino":
        canvas.create_oval(cx - 52, cy - 50, cx + 52, cy + 52, fill="#22c55e", outline="#ffffff", width=4)
        canvas.create_oval(cx - 22, cy - 20, cx - 10, cy - 8, fill="#040914")
        canvas.create_oval(cx + 10, cy - 20, cx + 22, cy - 8, fill="#040914")
        canvas.create_arc(cx - 25, cy - 6, cx + 25, cy + 34, start=200, extent=140, style="arc", outline="#040914", width=4)
    elif "rocket" in scene or "moon" in scene or "star" in scene:
        canvas.create_polygon(cx, cy - 58, cx - 28, cy + 24, cx + 28, cy + 24, fill="#ef4444", outline="#ffffff", width=3)
        canvas.create_oval(cx - 14, cy - 18, cx + 14, cy + 10, fill="#38bdf8", outline="#ffffff", width=2)
        canvas.create_polygon(cx - 16, cy + 26, cx, cy + 64, cx + 16, cy + 26, fill="#facc15", outline="")
    else:
        canvas.create_oval(cx - 50, cy - 50, cx + 50, cy + 50, fill="#ec4899", outline="#ffffff", width=3)
        canvas.create_oval(cx - 20, cy - 18, cx - 8, cy - 6, fill="#040914")
        canvas.create_oval(cx + 8, cy - 18, cx + 20, cy - 6, fill="#040914")
        canvas.create_arc(cx - 24, cy - 6, cx + 24, cy + 28, start=200, extent=140, style="arc", outline="#040914", width=4)


class BookLibraryModal:
    """Modal da Biblioteca Stark com histórias clássicas enriquecidas e efeitos sonoros."""

    def __init__(self, os_app):
        self.os_app = os_app
        self.win = os_app._create_activity_window("📚 BIBLIOTECA HOLOGRÁFICA STARK (HISTÓRIAS INFANTIS)")
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

        banner = tk.Frame(self.body, bg="#0c1e35", highlightthickness=2, highlightbackground="#38bdf8", pady=8, padx=14)
        banner.pack(fill="x", pady=(0, 10))

        tk.Label(
            banner,
            text=f"📖 Livros lidos hoje: {read_today}   |   Toque em uma capa colorida para ouvir e fuçar a história!",
            fg="#f0f9ff",
            bg="#0c1e35",
            font=("Arial", 12, "bold"),
        ).pack()

        shelf = tk.Frame(self.body, bg=self.os_app.BG_DARK)
        shelf.pack(fill="both", expand=True)

        for idx, book in enumerate(BOOKS):
            r, c = divmod(idx, 3)
            shelf.columnconfigure(c, weight=1)
            shelf.rowconfigure(r, weight=1)

            card = tk.Frame(
                shelf,
                bg=book.get("theme_color", "#0284c7"),
                highlightthickness=3,
                highlightbackground="#e0f2fe",
                padx=12,
                pady=12,
                cursor="hand2",
            )
            card.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)

            ico = tk.Label(
                card,
                text=book.get("cover_emoji", "📘"),
                fg="#ffffff",
                bg=book.get("theme_color", "#0284c7"),
                font=("Arial", 36),
            )
            ico.pack()

            lbl = tk.Label(
                card,
                text=book["title"],
                fg="#ffffff",
                bg=book.get("theme_color", "#0284c7"),
                font=("Arial", 13, "bold"),
                wraplength=260,
                justify="center",
            )
            lbl.pack(expand=True)

            sub = tk.Label(
                card,
                text=f"{len(book['pages'])} páginas • Toque para ler!",
                fg="#f0f9ff",
                bg=book.get("theme_color", "#0284c7"),
                font=("Arial", 10),
            )
            sub.pack()

            for w in (card, ico, lbl, sub):
                w.bind("<Button-1>", lambda _e, b=book: self._open_book(b))

        self.os_app.say(
            f"Biblioteca de Histórias, {self.os_app.brain.name}! Toque em qualquer livrinho colorido para ouvir!"
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

        book_frame = tk.Frame(
            self.body, bg="#0b192c", highlightthickness=3, highlightbackground=book.get("theme_color", "#0284c7")
        )
        book_frame.pack(fill="both", expand=True, pady=6)

        left_art = tk.Frame(book_frame, bg="#081221", width=330)
        left_art.pack(side="left", fill="y", padx=12, pady=12)

        art_canvas = tk.Canvas(left_art, width=300, height=220, bg="#081221", highlightthickness=0, cursor="hand2")
        art_canvas.pack(pady=6)
        draw_book_illustration(art_canvas, page.get("scene", "star"))

        art_canvas.bind("<Button-1>", lambda _e: self._trigger_tap_spot(page))

        # Palavra-chave gigante para tocar e soletrar
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
        word_btn.pack(pady=4)

        tk.Label(
            left_art,
            text=page.get("tap_hint", "Toque no desenho para fuçar!"),
            fg="#38bdf8",
            bg="#081221",
            font=("Arial", 10, "bold"),
            wraplength=280,
            justify="center",
        ).pack(pady=2)

        right_txt = tk.Frame(book_frame, bg="#0b192c")
        right_txt.pack(side="left", fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            right_txt,
            text=page["text"],
            fg="#ffffff",
            bg="#0b192c",
            font=("Arial", 21, "bold"),
            wraplength=540,
            justify="left",
        ).pack(expand=True, fill="both")

        nav = tk.Frame(self.body, bg=self.os_app.BG_DARK)
        nav.pack(fill="x", pady=(8, 0))

        if self.page_idx > 0:
            tk.Button(
                nav,
                text="⬅ Anterior",
                bg="#334155",
                fg="#ffffff",
                font=("Arial", 13, "bold"),
                padx=16,
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
        ).pack(side="left", padx=10)

        if self.page_idx < len(pages) - 1:
            tk.Button(
                nav,
                text="Próxima Página ➡",
                bg="#10b981",
                fg="#ffffff",
                font=("Arial", 14, "bold"),
                padx=22,
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
                padx=20,
                pady=10,
                command=self._finish_book,
            ).pack(side="right")

        self.os_app.voice.play_tone(587, 110)
        self.os_app.say(page["text"])

    def _trigger_tap_spot(self, page: dict):
        self.os_app.voice.play_tone(784, 140)
        sound = page.get("tap_sound", "")
        if sound == "oink":
            self.os_app.say("Oinc oinc! O porquinho está alegre e seguro!")
        elif sound == "roar_cute":
            self.os_app.say("Ruaaaar! Eu sou o Tito, o dinossauro dos abraços!")
        elif sound == "rocket_boost":
            self.os_app.say("Propulsores ligados! Zuuuuuuum!")
        elif sound == "blow":
            self.os_app.say("Fuuuuuu! O vento soprou bem forte!")
        elif sound == "squeak":
            self.os_app.say("Queek queek! O ratinho valente correu para ajudar!")
        else:
            self.os_app.say(page.get("tap_hint", "Você tocou no desenho mágico!"))

    def _spell_word(self, word: str):
        letters = " ... ".join(list(word.replace(" ", "")))
        self.os_app.voice.play_tone(659, 100)
        self.os_app.say(f"A palavra é {word}! Letrinhas: {letters}. {word}!")

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
