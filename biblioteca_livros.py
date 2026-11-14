"""
Módulo de Biblioteca Dinâmica de Livros & Histórias de Desenvolvimento Pessoal Infantil.
- Catálogo nativo focado em virtudes formativas (Resiliência, Coragem, Paciência, Gratidão, Trabalho em Equipe, Disciplina).
- Suporte a livros dinâmicos gerados por IA ou criados pelos pais no banco SQLite.
- Páginas com método fônico interativo (palavra em destaque, dica de toque e sons).
"""

import json
import uuid
import re
from typing import List, Dict, Any, Optional
from banco_dados import db


# ==============================================================================
# CATÁLOGO NATIVO DE HISTÓRIAS DE DESENVOLVIMENTO PESSOAL INFANTIL
# ==============================================================================

DEFAULT_DEVELOPMENT_BOOKS = [
    {
        "id": "estrelinha_resiliente",
        "title": "A Estrelinha que Nunca Desistia",
        "theme_color": "#f59e0b",
        "cover_emoji": "⭐",
        "category": "Resiliência & Persistência",
        "moral": "Errar faz parte do aprendizado! Tentar de novo com paciência nos faz brilhar ainda mais forte!",
        "pages": [
            {
                "scene": "little_star",
                "word": "BRILHAR",
                "tap_hint": "Toque na estrelinha para fazê-la piscar!",
                "tap_sound": "twinkle",
                "text": "No alto do céu escuro, a pequena Estrelinha Tetê tentava BRILHAR com toda a força, mas seu brilho ainda era fraquinho como uma vela."
            },
            {
                "scene": "star_fall",
                "word": "TENTAR",
                "tap_hint": "Toque no vento amigo que sopra coragem!",
                "tap_sound": "swoosh",
                "text": "Ela tentou uma vez, duas vezes e até tropeçou numa nuvem! Mas a Lua sussurrou: 'Não desista! TENTAR de novo é o segredo dos fortes!'"
            },
            {
                "scene": "star_breath",
                "word": "FORÇA",
                "tap_hint": "Toque no coração da estrelinha respirando fundo!",
                "tap_sound": "heartbeat",
                "text": "Tetê respirou fundo, concentrou toda a sua FORÇA de vontade e acreditou no seu potencial. Ela sorriu e deu um pulinho no céu!"
            },
            {
                "scene": "star_super_glow",
                "word": "CAMPEÃ",
                "tap_hint": "Toque na luz dourada da vitória!",
                "tap_sound": "cheer",
                "text": "Zuuuum! Uma luz dourada iluminou toda a galáxia! A estrelinha virou uma CAMPEÃ que nunca desiste de brilhar!"
            }
        ]
    },
    {
        "id": "leaozinho_corajoso",
        "title": "O Leãozinho Leo e a Coragem no Coração",
        "theme_color": "#ea580c",
        "cover_emoji": "🦁",
        "category": "Coragem & Autoconfiança",
        "moral": "Coragem não é a ausência de medo: é dar o primeiro passo mesmo com o coração batendo forte!",
        "pages": [
            {
                "scene": "lion_cave",
                "word": "MEDO",
                "tap_hint": "Toque na patinha do leãozinho para dar apoio!",
                "tap_sound": "roar_cute",
                "text": "O leãozinho Leo tinha um coração enorme, mas sentia MEDO de atravessar a ponte de madeira alta sobre o riozinho azul."
            },
            {
                "scene": "bird_friend",
                "word": "AMIGO",
                "tap_hint": "Toque no passarinho cantador!",
                "tap_sound": "chirp",
                "text": "Um passarinho AMIGO pousou na sua juba e disse: 'Olhe para a frente, Leo! Um passinho de cada vez e você consegue!'"
            },
            {
                "scene": "lion_step",
                "word": "CORAGEM",
                "tap_hint": "Toque na ponte firme de madeira!",
                "tap_sound": "knock",
                "text": "Leo colocou a primeira pata... depois a segunda... A CORAGEM cresceu dentro do peito como um sol quentinho!"
            },
            {
                "scene": "lion_proud",
                "word": "VITÓRIA",
                "tap_hint": "Toque no rugido alegre de herói!",
                "tap_sound": "cheer",
                "text": "Ele chegou ao outro lado! Sentiu a doce VITÓRIA de ter superado seu próprio medo e abraçou todos os amiguinhos!"
            }
        ]
    },
    {
        "id": "tartaruga_calma",
        "title": "A Tartaruga Sábia e o Segredo da Calma",
        "theme_color": "#10b981",
        "cover_emoji": "🐢",
        "category": "Paciência & Controle Emocional",
        "moral": "Quem tem paciência e sabe respirar quando está bravo encontra as melhores soluções do mundo!",
        "pages": [
            {
                "scene": "turtle_hurry",
                "word": "PRESSA",
                "tap_hint": "Toque no coelhinho correndo sem parar!",
                "tap_sound": "bell",
                "text": "Na floresta, o coelho vivia em extrema PRESSA, correndo de um lado para o outro sem prestar atenção nas flores do caminho."
            },
            {
                "scene": "turtle_breath",
                "word": "CALMA",
                "tap_hint": "Toque na tartaruga respirando bem devagar!",
                "tap_sound": "blow",
                "text": "A sábia tartaruga Tulipa ensinou: 'Quando a raiva ou a agonia baterem, respire com CALMA... Puxe o ar cheirando uma flor!'"
            },
            {
                "scene": "turtle_step",
                "word": "PACIÊNCIA",
                "tap_hint": "Toque nas pegadinhas firmes na terra!",
                "tap_sound": "knock",
                "text": "Passo a passo, com muita PACIÊNCIA, Tulipa chegou ao topo da montanha e viu o mais belo pôr do sol dourado."
            },
            {
                "scene": "peace_forest",
                "word": "PAZ",
                "tap_hint": "Toque no coração tranquilo!",
                "tap_sound": "heartbeat",
                "text": "O coelho aprendeu a lição. Descobriu que um coração sereno e em PAZ é o maior superpoder que alguém pode ter!"
            }
        ]
    },
    {
        "id": "bau_gratidao",
        "title": "O Baú Mágico da Gratidão",
        "theme_color": "#8b5cf6",
        "cover_emoji": "🎁",
        "category": "Gratidão & Família",
        "moral": "Agradecer pela comida, pela saúde, pelo brinquedo e pelo abraço da família enche o nosso coração de alegria verdadeira!",
        "pages": [
            {
                "scene": "chest_closed",
                "word": "BAÚ",
                "tap_hint": "Toque na fechadura dourada do baú!",
                "tap_sound": "twinkle",
                "text": "Campeão encontrou um BAÚ de madeira mágica no seu quarto. A fechadura só abria quando alguém dizia três coisas boas do dia!"
            },
            {
                "scene": "chest_food",
                "word": "OBRIGADO",
                "tap_hint": "Toque no prato de comidinha gostosa!",
                "tap_sound": "bell",
                "text": "Campeão sorriu: 'OBRIGADO pelo prato gostoso que o papai e a mamãe prepararam para me deixar forte e saudável!'"
            },
            {
                "scene": "chest_hug",
                "word": "CARINHO",
                "tap_hint": "Toque no abraço da família!",
                "tap_sound": "heartbeat",
                "text": "'Obrigado pela caminha macia e por todo o CARINHO que eu recebo todos os dias!' Uma luz dourada começou a brilhar no baú!"
            },
            {
                "scene": "chest_open",
                "word": "ALEGRIA",
                "tap_hint": "Toque nas moedinhas de luz que saem do baú!",
                "tap_sound": "party",
                "text": "O baú se abriu! Dentro dele não havia ouro, mas uma doce onda de ALEGRIA que abraçou a casa inteira!"
            }
        ]
    },
    {
        "id": "ponte_amizade",
        "title": "A Ponte dos Bichinhos Construtores",
        "theme_color": "#0284c7",
        "cover_emoji": "🌉",
        "category": "Trabalho em Equipe & Empatia",
        "moral": "Juntos nós somos muito mais fortes! Dividir as tarefas e ajudar o amigo constrói coisas incríveis!",
        "pages": [
            {
                "scene": "river_gap",
                "word": "RIO",
                "tap_hint": "Toque na água do rio correndo!",
                "tap_sound": "swoosh",
                "text": "Um grande RIO separava os esquilinhos dos castores. Ninguém conseguia pular tão longe sozinho para brincar junto."
            },
            {
                "scene": "team_idea",
                "word": "JUNTOS",
                "tap_hint": "Toque nos animaizinhos dando as mãos!",
                "tap_sound": "cheer",
                "text": "O castor sugeriu: 'E se trabalharmos JUNTOS? Eu corto a madeira firme e vocês carregam as folhas para amarrar!'"
            },
            {
                "scene": "bridge_build",
                "word": "AJUDAR",
                "tap_hint": "Toque nas madeirinhas sendo encaixadas!",
                "tap_sound": "clang",
                "text": "Cada bichinho fez a sua parte. AJUDAR com alegria fez o trabalho render rápido e sem ninguém se cansar demais."
            },
            {
                "scene": "bridge_finish",
                "word": "AMIZADE",
                "tap_hint": "Toque na ponte concluída com bandeirinhas!",
                "tap_sound": "party",
                "text": "A ponte ficou pronta! E eles a batizaram de Ponte da AMIZADE, onde todos celebram o valor da união!"
            }
        ]
    },
    {
        "id": "pequeno_samurai",
        "title": "O Pequeno Samurai dos Hábitos Fortes",
        "theme_color": "#dc2626",
        "cover_emoji": "🥋",
        "category": "Disciplina & Hábitos Fortes",
        "moral": "Arrumar a cama, guardar os brinquedos e praticar um pouquinho todo dia é o segredo de quem se torna um mestre!",
        "pages": [
            {
                "scene": "samurai_room",
                "word": "ORDEM",
                "tap_hint": "Toque na caminha sendo arrumada!",
                "tap_sound": "bell",
                "text": "O pequeno samurai acordava com o nascer do sol e começava sua primeira missão: colocar ORDEM e beleza no seu quarto."
            },
            {
                "scene": "samurai_train",
                "word": "TREINAR",
                "tap_hint": "Toque na espada de treino de bambu!",
                "tap_sound": "clang",
                "text": "Todo dia ele dedicava 15 minutinhos para TREINAR o equilíbrio e a leitura. Nem um dia a mais, nem um dia a menos!"
            },
            {
                "scene": "samurai_focus",
                "word": "FOCO",
                "tap_hint": "Toque no olhar atento do guerreiro!",
                "tap_sound": "heartbeat",
                "text": "Com FOCO no que estava fazendo, ele guardava cada brinquedo no seu lugar e cuidava com respeito de tudo o que tinha."
            },
            {
                "scene": "samurai_master",
                "word": "MESTRE",
                "tap_hint": "Toque na faixa dourada de honra!",
                "tap_sound": "cheer",
                "text": "O grande mestre sorriu e disse: 'Você se tornou um verdadeiro MESTRE! Pois quem domina seus hábitos domina seu destino!'"
            }
        ]
    },
    {
        "id": "cientista_ideias",
        "title": "O Pequeno Cientista Stark e a Lâmpada das Ideias",
        "theme_color": "#06b6d4",
        "cover_emoji": "💡",
        "category": "Foco & Curiosidade",
        "moral": "Ter curiosidade, fazer perguntas inteligentes e inventar coisas boas torna o mundo um lugar incrível!",
        "pages": [
            {
                "scene": "stark_lab",
                "word": "INVENTAR",
                "tap_hint": "Toque nos circuitos brilhantes da bancada!",
                "tap_sound": "twinkle",
                "text": "No laboratório do robô Jarvis, o pequeno cientista adorava INVENTAR máquinas para ajudar as pessoas e cuidar dos animais."
            },
            {
                "scene": "question_mark",
                "word": "PORQUÊ",
                "tap_hint": "Toque no ponto de interrogação flutuante!",
                "tap_sound": "bell",
                "text": "Ele nunca tinha vergonha de perguntar: 'Por que o céu é azul? Por que as folhas respiram?' A pergunta PORQUÊ é a chave da ciência!"
            },
            {
                "scene": "light_bulb",
                "word": "IDEIA",
                "tap_hint": "Toque na lâmpada mágica acendendo!",
                "tap_sound": "cheer",
                "text": "Plim! Uma grande IDEIA acendeu na sua cabeça: um regador automático de plantinhas movido a luz do Sol!"
            },
            {
                "scene": "robot_applause",
                "word": "GENIAL",
                "tap_hint": "Toque no robô Jarvis aplaudindo!",
                "tap_sound": "party",
                "text": "O Jarvis comemorou com luzes neon: 'Você é um herói GENIAL, Campeão! A sua curiosidade vai transformar o mundo!'"
            }
        ]
    },
    {
        "id": "escudo_gentileza",
        "title": "O Escudo Mágico das Palavras Gentis",
        "theme_color": "#ec4899",
        "cover_emoji": "🛡️",
        "category": "Gentileza & Empatia",
        "moral": "Dizer 'por favor', 'com licença' e 'você consegue' acalma qualquer briga e cura corações tristes!",
        "pages": [
            {
                "scene": "sad_friend",
                "word": "TRISTE",
                "tap_hint": "Toque na nuvenzinha cinza que vai embora!",
                "tap_sound": "howl_soft",
                "text": "No parquinho, o ursinho Bidu estava TRISTE porque seu castelinho de areia havia caído no chão."
            },
            {
                "scene": "kind_word",
                "word": "BONDADE",
                "tap_hint": "Toque no coração que se aproxima!",
                "tap_sound": "heartbeat",
                "text": "Campeão se aproximou com BONDADE e disse: 'Não fique triste, Bidu! Nós podemos construir outro castelo ainda mais bonito juntos!'"
            },
            {
                "scene": "smile_magic",
                "word": "SORRISO",
                "tap_hint": "Toque no solzinho voltando a brilhar!",
                "tap_sound": "twinkle",
                "text": "Uma palavra gentil foi como mágica! O ursinho abriu um largo SORRISO e os dois começaram a moldar torres de areia!"
            },
            {
                "scene": "magic_shield",
                "word": "SUPERPODER",
                "tap_hint": "Toque no escudo brilhante de flores!",
                "tap_sound": "cheer",
                "text": "Campeão descobriu seu maior escudo: a gentileza é um SUPERPODER que cura corações e espalha luz por onde passa!"
            }
        ]
    }
]


# ==============================================================================
# CLASSE GERENCIADORA DA BIBLIOTECA DINÂMICA
# ==============================================================================

class DynamicLibraryManager:
    """Gerencia livros nativos e livros dinâmicos criados por IA ou pelos pais no SQLite."""

    def __init__(self, database=db):
        self.db = database
        self._inicializar_tabela()

    def _inicializar_tabela(self):
        """Garante a existência da tabela livros_dinamicos no SQLite."""
        self.db.executar_escrita("""
            CREATE TABLE IF NOT EXISTS livros_dinamicos (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                theme_color TEXT NOT NULL,
                cover_emoji TEXT NOT NULL,
                category TEXT NOT NULL,
                moral TEXT NOT NULL,
                pages_json TEXT NOT NULL,
                origem TEXT DEFAULT 'ia',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    def obter_todos_os_livros(self) -> List[Dict[str, Any]]:
        """Retorna todos os livros: catálogo fixo de desenvolvimento pessoal + dinâmicos do SQLite."""
        todos = list(DEFAULT_DEVELOPMENT_BOOKS)

        # Busca livros do banco
        rows = self.db.consultar_todos(
            "SELECT id, title, theme_color, cover_emoji, category, moral, pages_json, origem FROM livros_dinamicos ORDER BY criado_em DESC;"
        )

        for r in rows:
            try:
                pages = json.loads(r["pages_json"])
                todos.append({
                    "id": r["id"],
                    "title": r["title"],
                    "theme_color": r["theme_color"],
                    "cover_emoji": r["cover_emoji"],
                    "category": r["category"],
                    "moral": r["moral"],
                    "pages": pages,
                    "origem": r.get("origem", "dinamico")
                })
            except Exception:
                pass

        return todos

    def obter_livro_por_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Busca um livro específico por ID."""
        for b in self.obter_todos_os_livros():
            if b["id"] == book_id:
                return b
        return None

    def salvar_novo_livro(self, livro: Dict[str, Any]) -> bool:
        """Salva um livro criado pelos pais ou gerado pela IA no SQLite."""
        if not livro.get("id"):
            livro["id"] = f"livro_{uuid.uuid4().hex[:8]}"

        pages_json = json.dumps(livro.get("pages", []), ensure_ascii=False)

        res = self.db.executar_escrita("""
            INSERT OR REPLACE INTO livros_dinamicos 
            (id, title, theme_color, cover_emoji, category, moral, pages_json, origem, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
        """, (
            livro["id"],
            livro.get("title", "História Especial"),
            livro.get("theme_color", "#0284c7"),
            livro.get("cover_emoji", "📖"),
            livro.get("category", "Desenvolvimento Pessoal"),
            livro.get("moral", "Uma lição de sabedoria e amor."),
            pages_json,
            livro.get("origem", "ia")
        ))
        return res is not None

    def excluir_livro_dinamico(self, book_id: str) -> bool:
        """Exclui um livro customizado do banco."""
        res = self.db.executar_escrita("DELETE FROM livros_dinamicos WHERE id = ?;", (book_id,))
        return res is not None

    def gerar_historia_ia(self, tema: str = "Resiliência", child_name: str = "Campeão") -> Dict[str, Any]:
        """
        Gera uma nova história dinâmica focada em desenvolvimento pessoal.
        Garante estrutura de 4 páginas com palavras de apoio e moral prática.
        """
        temas_map = {
            "resiliencia": {
                "title": f"A Grande Aventura de Superação de {child_name}",
                "emoji": "🌟",
                "color": "#f59e0b",
                "category": "Resiliência & Persistência",
                "moral": f"Mesmo quando algo dá errado, {child_name} respira fundo e tenta com amor até conseguir!",
                "p1": ("DESAFIO", f"{child_name} encontrou um grande DESAFIO no castelo de blocos que caiu no chão.", "puzzle"),
                "p2": ("RESPIRAR", f"Ele parou para RESPIRAR fundo três vezes e acalmar o coraçãozinho.", "blow"),
                "p3": ("TENTAR", f"Com muita paciência, começou a TENTAR de novo colocando peça por peça firme.", "knock"),
                "p4": ("SUCESSO", f"Que maravilha! O castelo ficou mais alto e forte! Um grande SUCESSO!", "cheer"),
            },
            "coragem": {
                "title": f"{child_name} e a Capa da Coragem",
                "emoji": "🦸",
                "color": "#ea580c",
                "category": "Coragem & Autoconfiança",
                "moral": f"A verdadeira força está dentro do coração de {child_name}!",
                "p1": ("ESCURO", f"A noite chegou e a sombra na parede parecia assustadora no ESCURO do quarto.", "howl_soft"),
                "p2": ("LANTERNA", f"{child_name} pegou sua LANTERNA mágica e acendeu uma luz corajosa.", "twinkle"),
                "p3": ("VERDADE", f"Ele viu a VERDADE: a sombra era só o seu ursinho de pelúcia na estante!", "cheer"),
                "p4": ("CORAGEM", f"Ele sorriu no travesseiro, sabendo que a CORAGEM protege todos os seus sonhos!", "heartbeat"),
            },
            "gratidao": {
                "title": f"O Dia Dourado de Gratidão de {child_name}",
                "emoji": "☀️",
                "color": "#8b5cf6",
                "category": "Gratidão & Família",
                "moral": "Agradecer pelas pessoas que nos amam e pelas coisas boas faz a vida brilhar!",
                "p1": ("MANHÃ", f"{child_name} acordou com o raio de sol entrando na janela logo pela MANHÃ.", "twinkle"),
                "p2": ("AGRADECER", f"Ele resolveu AGRADECER pelo abraço carinhoso da família antes do café.", "heartbeat"),
                "p3": ("COMPARTILHAR", f"No parquinho, decidiu COMPARTILHAR seu brinquedo favorito com um amigo novo.", "bell"),
                "p4": ("FELICIDADE", f"O coração ficou leve e saltitante! É a magia da pura FELICIDADE!", "party"),
            },
            "paciencia": {
                "title": f"{child_name} e a Sementinha Mágica",
                "emoji": "🌱",
                "color": "#10b981",
                "category": "Paciência & Calma",
                "moral": "Tudo tem seu tempo para crescer! Saber esperar com carinho faz as flores mais lindas brotarem!",
                "p1": ("SEMENTE", f"{child_name} colocou uma pequena SEMENTE na terra fofa do vasinho.", "bell"),
                "p2": ("REGAR", f"Todo dia ele ia REGAR com gotinhas d'água fresca e muito cuidado.", "swoosh"),
                "p3": ("ESPERAR", f"Ele aprendeu a ESPERAR pacientemente sem puxar a plantinha antes da hora.", "blow"),
                "p4": ("FLOR", f"Plim! Brotou uma FLOR linda e perfumada, coroando a paciência de herói!", "cheer"),
            },
            "disciplina": {
                "title": f"{child_name} e a Rotina do Campeão",
                "emoji": "🏆",
                "color": "#dc2626",
                "category": "Disciplina & Hábitos",
                "moral": "Pequenas vitórias todo dia constroem os maiores campeões do mundo!",
                "p1": ("ARRUMAR", f"A primeira vitória do dia foi ARRUMAR a caminha com capricho de herói.", "knock"),
                "p2": ("ALIMENTAR", f"Na mesa, soube se ALIMENTAR com comidinha saudável para crescer forte.", "bell"),
                "p3": ("ESTUDAR", f"Depois dedicou um tempinho para ESTUDAR as letrinhas e os números.", "twinkle"),
                "p4": ("VITÓRIA", f"O Jarvis tocou uma fanfarra: é a grande VITÓRIA da dedicação e foco!", "party"),
            }
        }

        chave_busca = "resiliencia"
        tema_low = tema.lower()
        for k in temas_map:
            if k in tema_low:
                chave_busca = k
                break

        dados = temas_map[chave_busca]
        novo_id = f"historia_{chave_busca}_{uuid.uuid4().hex[:6]}"

        novo_livro = {
            "id": novo_id,
            "title": dados["title"],
            "theme_color": dados["color"],
            "cover_emoji": dados["emoji"],
            "category": dados["category"],
            "moral": dados["moral"],
            "origem": "ia_dinamica",
            "pages": [
                {
                    "scene": f"p1_{chave_busca}",
                    "word": dados["p1"][0],
                    "tap_hint": f"Toque para explorar a cena de {dados['p1'][0].lower()}!",
                    "tap_sound": dados["p1"][2],
                    "text": dados["p1"][1]
                },
                {
                    "scene": f"p2_{chave_busca}",
                    "word": dados["p2"][0],
                    "tap_hint": f"Toque para descobrir o segredo de {dados['p2'][0].lower()}!",
                    "tap_sound": dados["p2"][2],
                    "text": dados["p2"][1]
                },
                {
                    "scene": f"p3_{chave_busca}",
                    "word": dados["p3"][0],
                    "tap_hint": f"Toque e sinta a força da palavra {dados['p3'][0].lower()}!",
                    "tap_sound": dados["p3"][2],
                    "text": dados["p3"][1]
                },
                {
                    "scene": f"p4_{chave_busca}",
                    "word": dados["p4"][0],
                    "tap_hint": f"Toque na grande comemoração final de {dados['p4'][0].lower()}!",
                    "tap_sound": dados["p4"][2],
                    "text": dados["p4"][1]
                }
            ]
        }

        # Salva no banco de dados para persistência infinita
        self.salvar_novo_livro(novo_livro)
        return novo_livro


# Instância global
library_mgr = DynamicLibraryManager()

# Exportação direta para retrocompatibilidade
BOOKS = library_mgr.obter_todos_os_livros()
