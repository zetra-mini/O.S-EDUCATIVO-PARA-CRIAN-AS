import gc
import json
import os
import random
import re
import subprocess
import sys
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "child_name": "Kaleu",
    "active_provider": "ollama",  # 'ollama', 'opencode', 'gemini', 'openai', 'groq', 'offline'
    "mode": "ollama",  # Mantido para retrocompatibilidade
    "opencode_model": "google/gemini-2.0-flash",
    "opencode_server": "",
    "opencode_cli_path": "opencode",
    "gemini_api_key": "",
    "gemini_model": "gemini-3.8-flash",
    "openai_api_key": "",
    "openai_model": "gpt-4o-mini",
    "groq_api_key": "",
    "groq_model": "llama-3.3-70b-versatile",
    "voice_profile": "jarvis_antonio",  # 'jarvis_antonio', 'amiga_thalita', 'amiga_francisca', 'gemini_puck', 'gemini_sulafat'
    "prefer_neural_voice": True,
    "ollama_url": "http://127.0.0.1:11434",
    "ollama_model": "llama3.2:1b",
    "voice_enabled": True,
    "media_start_time": "16:00",
    "media_end_time": "17:00",
    "media_daily_minutes": 25,
    "require_book_before_media": True,
    "netflix_url": "https://www.netflix.com/Kids",
    "youtube_url": "https://www.youtubekids.com",
    "custom_books": [],
    "picovoice_access_key": "",
}


class JarvisBrain:
    """
    Cérebro híbrido do JARVIS Kids OS v2.2:
    Suporta seleção dinâmica de provedores no Painel dos Pais:
    1. Google Gemini (gemini-3.8-flash) via google-genai Interactions API oficial.
    2. OpenAI ChatGPT (gpt-4o-mini / gpt-4o).
    3. Groq Cloud (llama-3.3-70b-versatile ultrarrápido).
    4. IA Local / Ollama (100% Localhost sem internet).
    5. Modo 100% Offline (sem Wi-Fi e < 5 MB RAM para Acer Aspire One 532).
    """

    def __init__(self):
        self.config = dict(DEFAULT_CONFIG)
        self.last_gemini_interaction_id = None
        self.local_history = []
        self.load_config()
        self._build_offline_knowledge()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.config.update(saved)
            except Exception:
                pass
        else:
            self.save_config()

    def save_config(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def reset_conversation(self):
        self.last_gemini_interaction_id = None
        self.local_history.clear()
        gc.collect()

    @property
    def name(self) -> str:
        return self.config.get("child_name", "Pequeno Inventor").strip() or "Pequeno Inventor"

    @property
    def provider(self) -> str:
        p = self.config.get("active_provider") or self.config.get("mode") or "gemini"
        return p.lower()

    def get_effective_gemini_key(self) -> str:
        return (
            self.config.get("gemini_api_key", "").strip()
            or os.environ.get("GEMINI_API_KEY", "").strip()
            or os.environ.get("GOOGLE_API_KEY", "").strip()
        )

    def get_effective_openai_key(self) -> str:
        return (
            self.config.get("openai_api_key", "").strip()
            or os.environ.get("OPENAI_API_KEY", "").strip()
        )

    def get_effective_groq_key(self) -> str:
        return (
            self.config.get("groq_api_key", "").strip()
            or os.environ.get("GROQ_API_KEY", "").strip()
        )

    def _child_system_instruction(self) -> str:
        return (
            f"Você é o J.A.R.V.I.S., o robozinho super fofo, companheiro, animado e protetor da criança {self.name} (idade de 4 a 10 anos).\n"
            f"Você tem olhinhos azuis de neon brilhantes, um reator no peito e muito carinho por {self.name}!\n"
            f"CONHECIMENTO GERAL E SUPER-HERÓIS:\n"
            f"Você conhece perfeitamente todos os super-heróis dos quadrinhos e desenhos infantis:\n"
            f"- Homem-Aranha é o Peter Parker, que escala paredes, solta teias e protege a cidade com bom humor;\n"
            f"- Homem de Ferro é o Tony Stark, um inventor genial que criou sua armadura tecnológica com reator Arc no peito;\n"
            f"- Batman é o Bruce Wayne, o Cavaleiro das Trevas que protege Gotham City com o Batmóvel;\n"
            f"- Hulk é o cientista Bruce Banner que fica gigante, verde e super forte para proteger os amigos;\n"
            f"- Capitão América é o Steve Rogers com seu escudo indestrutível com estrela;\n"
            f"- Flash é o Barry Allen, o herói mais veloz do mundo que corre como um raio;\n"
            f"- Super-Homem é o Clark Kent do planeta Krypton que voa e salva as pessoas.\n"
            f"Além disso, você adora dinossauros, animais, astronomia, planetas, ciências, livros e matemática divertida!\n"
            f"DIRETRIZES DE RESPOSTA:\n"
            f"1. Fale sempre em Português do Brasil com ternura, entusiasmo e alegria (bip bip!).\n"
            f"2. Responda com exatidão, clareza e doçura em 2 ou 3 frases curtas, ideais para ouvir em voz alta.\n"
            f"3. NUNCA gere formatações markdown, asteriscos, códigos, links ou listas.\n"
            f"4. NUNCA mencione violência, armas, sangue, morte ou temas adultos.\n"
            f"5. Se a criança perguntar sobre qualquer herói ou personagem, responda quem ele é de verdade com empolgação infantil!"
        )

    def sanitizar_resposta_infantil(self, raw_text: str) -> str:
        """
        Filtro de Segurança e Heurística de Conteúdo Infantil (Child-Safe Guardrails):
        1. Remove qualquer marcação técnica (Markdown, HTML, JSON, código, chaves, asteriscos).
        2. Detecta termos impróprios, violentos, pesados, adultos ou assustadores.
        3. Se detectar conteúdo inadequado ou sem sentido, intercepta e substitui por resposta segura e carinhosa.
        4. Garante frases curtas, afetuosas e fáceis de ouvir para uma criança de 4 a 10 anos.
        """
        if not raw_text or not isinstance(raw_text, str):
            return f"Eu estou aqui com você, {self.name}! Sobre o que você quer conversar agora?"

        text = raw_text.strip()

        # Remove blocos de código e tags HTML
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        # Remove asteriscos de negrito/itálico e hashtags
        text = re.sub(r'[*#_`~]', '', text)

        # Detecta alucinações de programação ou erros de sistema
        padroes_tecnicos = [
            r'def\s+\w+\(', r'function\s*\(', r'import\s+\w+', r'undefined', r'null', r'NaN',
            r'traceback', r'exception', r'http[s]?://', r'\{[\s\S]*?\}', r'\[[\s\S]*?\]'
        ]
        for p in padroes_tecnicos:
            if re.search(p, text, re.IGNORECASE):
                return f"Que pergunta legal, {self.name}! O Jarvis adora conversar com você! Vamos brincar de adivinhar animais agora?"

        # Lista de Termos Sensíveis/Inadequados para Crianças (Blacklist de Segurança Infantil)
        termos_inapropriados = [
            'morte', 'morrer', 'matar', 'assassino', 'arma', 'tiro', 'revólver', 'faca', 'sangue',
            'violência', 'violento', 'briga', 'bater', 'machucar', 'espancar', 'terror', 'monstro do mal',
            'pesadelo', 'assombração', 'fantasma mau', 'inferno', 'demônio', 'droga', 'remédio escondido',
            'veneno', 'álcool', 'cerveja', 'cigarro', 'fumar', 'crime', 'ladrão', 'presídio', 'cadeia',
            'sexo', 'nudez', 'pornografia', 'palavrão', 'merda', 'bosta', 'porra', 'caralho', 'desgraça',
            'maldito', 'política', 'partido', 'eleição', 'guerra', 'bomba', 'explosão fatal'
        ]
        text_lower = text.lower()
        for termo in termos_inapropriados:
            if re.search(r'\b' + re.escape(termo) + r'\b', text_lower):
                return (
                    f"Essa é uma curiosidade para quando você crescer mais um pouquinho, super-herói {self.name}! "
                    f"Que tal a gente inventar uma historinha bem divertida de animais ou naves espaciais agora?"
                )

        # Limpeza de espaçamentos múltiplos
        text = re.sub(r'\s+', ' ', text).strip()

        # Se ficou muito curto ou vazio
        if len(text) < 4:
            return f"Bip bip! Eu te ouvi, {self.name}! Vamos brincar juntos?"

        # Limita a 2 a 3 frases no máximo para não sobrecarregar a fala
        frases = re.split(r'([.!?]+)', text)
        if len(frases) > 6:
            text = "".join(frases[:6]).strip()

        return text

    def _ensure_ollama_running(self) -> bool:
        """Verifica se o Ollama está respondendo; se não estiver, inicia-o automaticamente em background."""
        url = self.config.get("ollama_url", "http://127.0.0.1:11434").rstrip("/")
        try:
            req = urllib.request.Request(f"{url}/api/tags")
            with urllib.request.urlopen(req, timeout=1.5) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass

        try:
            if sys.platform == "win32":
                caminhos = [
                    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Ollama.Ollama.Portable_Microsoft.Winget.Source_8wekyb3d8bbwe\ollama.exe"),
                    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
                    "ollama.exe",
                    "ollama"
                ]
                for c in caminhos:
                    if os.path.exists(c) or c.startswith("ollama"):
                        try:
                            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
                            subprocess.Popen([c, "serve"], creationflags=flags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            import time
                            for _ in range(5):
                                time.sleep(0.8)
                                try:
                                    with urllib.request.urlopen(f"{url}/api/tags", timeout=1.5) as r2:
                                        if r2.status == 200:
                                            return True
                                except Exception:
                                    pass
                            break
                        except Exception:
                            continue
            else:
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import time
                time.sleep(1.5)
                with urllib.request.urlopen(f"{url}/api/tags", timeout=1.5) as r2:
                    if r2.status == 200:
                        return True
        except Exception:
            pass
        return False

    def is_cognitive_question(self, text: str) -> bool:
        """
        Identifica se a frase é uma pergunta ou dúvida conceitual/curiosidade
        que deve ser respondida pelo motor de IA (Llama/Gemini) e NUNCA abrir
        modais de jogos ou rotinas do sistema.
        """
        t = (text or "").lower().strip()
        if not t:
            return False

        # Termina com ponto de interrogação
        if t.endswith("?"):
            if not any(u in t for u in ["que horas", "horas sao", "temperatura hoje", "previsao do tempo", "quantas moedas"]):
                return True

        # Padrões interrogativos explícitos
        padroes_pergunta = [
            r"^(por\s*que|porque|pq|o\s*que|oq|qual|quais|como|quem|onde|aonde|quando|quanto|quantos|quantas)\b",
            r"^(me\s+explica|me\s+conta|conta\s+sobre|fale\s+sobre|voc[eê]\s+sabe|voc[eê]\s+conhece|voc[eê]\s+gosta|o\s+que\s+acha|me\s+diz|me\s+ajuda\s+a\s+entender)\b",
            r"^(quanto\s+[eé]|quantos\s+[eé]|como\s+[eé]|por\s*que\s+[eé]|o\s+que\s+[eé])\b",
            r"^(ser[aá]\s+que|voc[eê]\s+pode\s+me\s+explicar|me\s+ajuda\s+a\s+entender)\b",
            r"\b(por\s*que|porque)\b",
        ]
        for p in padroes_pergunta:
            if re.search(p, t):
                if any(u in t for u in ["que horas", "horas sao", "temperatura hoje", "previsao do tempo", "quantas moedas"]):
                    return False
                return True

        return False

    def interpret_command(self, user_text: str) -> dict:
        """
        Interpreta a intenção do comando de voz do Kaleu:
        1. Comandos de Utilidade Imediata (horas, saldo, clima) -> 0ms
        2. Perguntas Cognitivas/Curiosidades/Dúvidas -> IA API (Llama Local / Provedor configurado)
        3. Comandos de Abrir Jogos/Atividades -> Execução Direta do Jogo
        """
        text_lower = (user_text or "").lower().strip()

        # 0. COMANDOS DE UTILIDADE IMEDIATA DO SISTEMA (Relógio, Clima Exato, Moedas)
        if any(w in text_lower for w in ["que horas", "que horas sao", "horas agora", "horario agora"]):
            import datetime
            agora = datetime.datetime.now()
            reply = f"Bip bip, herói {self.name}! Agora no relógio são exatamente {agora.hour} horas e {agora.minute} minutos!"
            return {
                "ok": True,
                "intencao": "relogio_tempo",
                "resposta_voz": reply,
                "acao_frontend": "nenhuma",
                "dados": {"hora": agora.strftime("%H:%M")},
            }

        if any(w in text_lower for w in ["quantas moedas", "saldo de moedas", "meu tesouro", "pote de moedas", "saldo atual"]):
            try:
                from economia_fichas import token_mgr
                status = token_mgr.obter_status_pote()
                saldo = status.get("saldo", 0)
                reply = f"Bip bip! {self.name}, você tem {saldo} moedas brilhantes guardadas no seu Pote do Tesouro!"
                return {
                    "ok": True,
                    "intencao": "tesouro",
                    "resposta_voz": reply,
                    "acao_frontend": "abrir_loja",
                    "dados": status,
                }
            except Exception:
                pass

        if any(w in text_lower for w in ["previsão do tempo", "previsao do tempo", "temperatura hoje", "vai chover hoje", "clima hoje"]):
            try:
                from clima_estacoes import weather_mgr
                cidade_cfg = self.config.get("geo_cidade", "Campo Largo")
                estado_cfg = self.config.get("geo_estado", "Paraná")
                weather_mgr.definir_localizacao(cidade_cfg, estado_cfg)
                clima = weather_mgr.obter_clima_atual(forcar=True)
                temp = clima.get("temperatura", 20)
                desc = clima.get("descricao", "agradável")
                cidade = clima.get("cidade", cidade_cfg)
                conselho = clima.get("conselho_infantil", "Um ótimo dia para se divertir!")
                reply = f"Em {cidade}, agora está fazendo {temp} graus com {desc}. {conselho}"
                return {
                    "ok": True,
                    "intencao": "clima",
                    "resposta_voz": reply,
                    "acao_frontend": "nenhuma",
                    "dados": clima,
                }
            except Exception:
                pass

        # 1. SE FOR UMA PERGUNTA COGNITIVA (DÚVIDA, CURIOSIDADE, CIÊNCIA, AMIZADE):
        # NUNCA abre jogos nem rotinas! Vai DIRETO para o cérebro da IA (Llama local / Provedor ativo)!
        if self.is_cognitive_question(user_text):
            reply, engine = self.ask(user_text)
            return {
                "ok": True,
                "intencao": "conversa_ia",
                "resposta_voz": reply,
                "acao_frontend": "nenhuma",
                "dados": {"engine": engine, "pergunta": user_text},
            }

        # 0. Cinema Stark / YouTube / Netflix (com verificação estrita de bloqueio e orientação)
        if any(w in text_lower for w in ["cinema", "youtube", "netflix", "desenho", "desenhos", "assistir", "filme"]):
            try:
                from gestao_tempo_midia import MediaTimeManager
                from banco_dados import db
                mm = MediaTimeManager(self, database=db)
                perm = mm.check_permission()
                bloqueado = not perm.get("allowed", False)
                motivo = perm.get("reason", "")
                msg_bloqueio = perm.get("message", "")

                if bloqueado:
                    if motivo == "need_book" or "livro" in motivo.lower() or "leitura" in motivo.lower():
                        reply = f"Atenção, super-herói {self.name}! O Cinema Stark está protegido pelas regrinhas da família! Para liberar o YouTube e Netflix, primeiro você precisa ler um livrinho mágico na nossa biblioteca! Quer que eu abra as histórias agora?"
                        return {
                            "ok": True,
                            "intencao": "cinema_bloqueado",
                            "resposta_voz": reply,
                            "acao_frontend": "cinema_bloqueado",
                            "dados": {"motivo": "leitura_pendente", "status": perm},
                        }
                    elif motivo == "daily_limit" or "tempo" in motivo.lower() or "limite" in motivo.lower():
                        reply = f"{self.name}, o tempo de vídeo de hoje já chegou ao fim! Seus olhinhos precisam descansar um pouco. Que tal tocar uma canção no piano ou desenhar na lousa mágica?"
                        return {
                            "ok": True,
                            "intencao": "cinema_bloqueado",
                            "resposta_voz": reply,
                            "acao_frontend": "cinema_bloqueado",
                            "dados": {"motivo": "limite_atingido", "status": perm},
                        }
                    else:
                        reply = f"O Cinema Stark só abre no horário combinado com a família! {msg_bloqueio} Enquanto isso, vamos jogar um joguinho bem legal na nossa sala?"
                        return {
                            "ok": True,
                            "intencao": "cinema_bloqueado",
                            "resposta_voz": reply,
                            "acao_frontend": "cinema_bloqueado",
                            "dados": {"motivo": "horario_restrito", "status": perm},
                        }
                else:
                    reply = f"Cinema Stark liberado com sucesso, {self.name}! Prepare-se para ver seus desenhos favoritos aprovados pela família!"
                    return {
                        "ok": True,
                        "intencao": "abrir_cinema",
                        "resposta_voz": reply,
                        "acao_frontend": "abrir_cinema",
                        "dados": perm,
                    }
            except Exception:
                pass

        # 1. Histórias Mágicas / Livros de Virtudes
        if any(w in text_lower for w in ["história", "historia", "histórias", "historias", "historinha", "livro", "livros", "ler", "leitura", "biblioteca"]):
            reply = "Abrindo a nossa Biblioteca Mágica de Histórias de Herói! Escolha uma linda virtude para aprender hoje!"
            return {
                "ok": True,
                "intencao": "abrir_biblioteca",
                "resposta_voz": reply,
                "acao_frontend": "abrir_biblioteca",
                "dados": {},
            }

        # 2. Laboratório Musical / Piano / Bateria
        if any(w in text_lower for w in ["música", "musica", "piano", "tocar", "canção", "cancao", "bateria", "cantar"]):
            reply = "Abrindo o Laboratório Musical do Jarvis! Vamos tocar o piano mágico e soltar o som dos tambores!"
            return {
                "ok": True,
                "intencao": "abrir_musica",
                "resposta_voz": reply,
                "acao_frontend": "abrir_musica",
                "dados": {},
            }

        # 3. Pintura & Lousa Mágica Neon
        if any(w in text_lower for w in ["pintar", "pintura", "desenhar", "lousa", "colorir", "arte"]):
            reply = "Abrindo a Lousa Neon e Pintura Mágica! Solte a sua imaginação e crie uma obra de arte com cores brilhantes!"
            return {
                "ok": True,
                "intencao": "abrir_pintura",
                "resposta_voz": reply,
                "acao_frontend": "abrir_pintura",
                "dados": {},
            }

        # 4. Academia Tech: Teclado, Mouse & Rodinha Scroll
        if any(w in text_lower for w in ["teclado", "mouse", "rodinha", "scroll", "digitar", "clique", "setinha"]):
            reply = "Abrindo a Academia Tech! Vamos treinar os dedinhos no teclado, o clique do mouse e o movimento da rodinha mágica!"
            return {
                "ok": True,
                "intencao": "abrir_tech",
                "resposta_voz": reply,
                "acao_frontend": "abrir_tech",
                "dados": {},
            }

        # 5. Festas & Datas Comemorativas do Brasil
        if any(w in text_lower for w in ["data", "datas", "comemorativa", "comemorativas", "festa", "festas", "carnaval", "páscoa", "pascoa", "natal", "dia das mães", "dia dos pais", "7 de setembro"]):
            reply = "Abrindo o Calendário de Festas e Datas Comemorativas do Brasil! Vamos descobrir o que celebramos com alegria!"
            return {
                "ok": True,
                "intencao": "abrir_datas",
                "resposta_voz": reply,
                "acao_frontend": "abrir_datas",
                "dados": {},
            }

        # 6. Alimentação Saudável / Prato dos Campeões
        if any(w in text_lower for w in ["prato", "comida saudável", "comida saudavel", "alimentação", "alimentacao", "nutrição", "nutricao", "comidinha"]):
            reply = "Abrindo o Prato dos Super Campeões! Vamos escolher comidinhas saudáveis e coloridas para ficar bem forte!"
            return {
                "ok": True,
                "intencao": "abrir_comida",
                "resposta_voz": reply,
                "acao_frontend": "abrir_comida",
                "dados": {},
            }

        # 7. Higiene dos Heróis / Banho, Mãos e Dentes
        if any(w in text_lower for w in ["higiene", "banho", "limpinho", "sabão", "sabao", "lavar mão", "lavar as mãos"]):
            reply = "Missão Super Herói Limpinho ativada! Vamos cuidar do nosso corpinho, tomar um banho gostoso e lavar as mãozinhas!"
            return {
                "ok": True,
                "intencao": "abrir_higiene",
                "resposta_voz": reply,
                "acao_frontend": "abrir_higiene",
                "dados": {},
            }

        # 8. Mãos & Contar de 1 a 10
        if any(w in text_lower for w in ["contar", "dedinhos", "mãozinha", "maozinha", "1 a 10", "número", "numeros"]):
            reply = "Abrindo o jogo de contar com as mãozinhas! Vamos levantar os dedinhos e aprender a contar de 1 a 10!"
            return {
                "ok": True,
                "intencao": "abrir_dedinhos",
                "resposta_voz": reply,
                "acao_frontend": "abrir_dedinhos",
                "dados": {},
            }

        # 9. Ler & Escrever (Método Fônico)
        if any(w in text_lower for w in ["alfabeto", "letrinha", "letrinhas", "escrever", "fônico", "fonico", "ler"]):
            reply = "Abrindo o treino fônico das letrinhas! Vamos ouvir o som que cada letrinha faz e praticar na lousa neon!"
            return {
                "ok": True,
                "intencao": "abrir_letras",
                "resposta_voz": reply,
                "acao_frontend": "abrir_letras",
                "dados": {},
            }

        # 10. Idiomas Mágicos (English & Español)
        if any(w in text_lower for w in ["inglês", "ingles", "espanhol", "idioma", "idiomas", "english"]):
            reply = "Welcome! Abrindo os Idiomas Mágicos! Vamos aprender palavras em inglês e espanhol com cartões falantes!"
            return {
                "ok": True,
                "intencao": "abrir_idiomas",
                "resposta_voz": reply,
                "acao_frontend": "abrir_idiomas",
                "dados": {},
            }

        # 11. Semáforo & Atenção
        if any(w in text_lower for w in ["semáforo", "semaforo", "sinal", "atenção", "atencao"]):
            reply = "Abrindo o Desafio do Semáforo Stark! Foco total: quando ficar verde a gente clica, quando ficar vermelho a gente espera!"
            return {
                "ok": True,
                "intencao": "abrir_semaforo",
                "resposta_voz": reply,
                "acao_frontend": "abrir_semaforo",
                "dados": {},
            }

        # 12. Emoções & Flor da Calma
        if any(w in text_lower for w in ["emoção", "emocao", "emoções", "emocoes", "calma", "respirar", "raiva", "triste", "medo"]):
            reply = "Abrindo o Centro das Emoções e a Flor da Calma! Vamos respirar fundo, soltar o ar e acalmar o coraçãozinho!"
            return {
                "ok": True,
                "intencao": "abrir_emocoes",
                "resposta_voz": reply,
                "acao_frontend": "abrir_emocoes",
                "dados": {},
            }

        # 12.1 Fonoaudiologia & Dicção / Palavra Nova do Jarvis
        if any(w in text_lower for w in ["palavra nova", "palavra mágica", "palavra magica", "nova palavra", "mostrar palavra", "sortear palavra"]):
            reply = f"Bip bip, super-herói {self.name}! O Jarvis vai sortear agora mesmo uma palavra mágica novinha para você treinar a dicção!"
            return {
                "ok": True,
                "intencao": "sortear_palavra_diccao",
                "resposta_voz": reply,
                "acao_frontend": "sortear_palavra_diccao",
                "dados": {},
            }

        if any(w in text_lower for w in ["fono", "fonoaudiologia", "dicção", "diccao", "trava-língua", "trava lingua", "travalingua", "treinar fala", "aprender a falar"]):
            reply = f"Abrindo a Academia de Dicção e Fonoaudiologia do Herói, {self.name}! Vamos treinar a boquinha com o Jarvis!"
            return {
                "ok": True,
                "intencao": "abrir_diccao",
                "resposta_voz": reply,
                "acao_frontend": "abrir_diccao",
                "dados": {},
            }

        # 13. Clima / Tempo / Estações (não conflita com Sistema Solar)
        if ("solar" not in text_lower) and (any(w in text_lower for w in ["tempo", "clima", "chover", "chuva", "calor", "frio", "previsão", "previsao", "estação", "estacoes", "geografia"]) or re.search(r'\b(sol|ensolarado)\b', text_lower)):
            try:
                from clima_estacoes import weather_mgr
                cidade_cfg = self.config.get("geo_cidade", "Campo Largo")
                estado_cfg = self.config.get("geo_estado", "Paraná")
                weather_mgr.definir_localizacao(cidade_cfg, estado_cfg)
                crianca = self.name

                # 13.1 Previsão para AMANHÃ
                is_amanha = any(w in text_lower for w in ["amanhã", "amanha", "dia seguinte", "próximo dia", "proximo dia"])
                if is_amanha:
                    prev = weather_mgr.obter_previsao_amanha()
                    t_max = prev.get("temp_max", 20)
                    t_min = prev.get("temp_min", 14)
                    desc = prev.get("descricao", "agradável")
                    cidade = prev.get("cidade", cidade_cfg)
                    conselho = prev.get("conselho_infantil", "Um ótimo dia pela frente!")
                    reply = f"Previsão do tempo para amanhã em {cidade}, {crianca}: teremos máxima de {t_max} graus e mínima de {t_min} graus, com {desc}. {conselho}"
                    return {
                        "ok": True,
                        "intencao": "previsao_amanha",
                        "resposta_voz": reply,
                        "acao_frontend": "nenhuma",  # Não abre modal, apenas responde por voz e texto
                        "dados": prev,
                    }

                # 13.2 Clima ATUAL (Hoje)
                clima = weather_mgr.obter_clima_atual(forcar=True)
                temp = clima.get("temperatura", 20)
                desc = clima.get("descricao", "agradável")
                cidade = clima.get("cidade", cidade_cfg)
                conselho = clima.get("conselho_infantil", "Um lindo dia para se divertir!")
                reply = f"Sistemas meteorológicos ativos, {crianca}! Em {cidade}, agora está fazendo {temp} graus com {desc}. {conselho}"
                return {
                    "ok": True,
                    "intencao": "clima",
                    "resposta_voz": reply,
                    "acao_frontend": "nenhuma",  # Não abre modal, apenas responde por voz e texto
                    "dados": clima,
                }
            except Exception:
                pass

        # 14. Moedas / Tesouro Real
        if any(w in text_lower for w in ["moeda", "moedas", "tesouro", "saldo", "pote", "fichas", "dinheiro"]):
            try:
                from economia_fichas import token_mgr
                status = token_mgr.obter_status_pote()
                saldo = status.get("saldo", 0)
                reply = f"Bip bip! Kaleo, você tem {saldo} moedas brilhantes guardadas no seu Pote do Tesouro! Vamos ver as recompensas na loja?"
                return {
                    "ok": True,
                    "intencao": "tesouro",
                    "resposta_voz": reply,
                    "acao_frontend": "abrir_loja",
                    "dados": status,
                }
            except Exception:
                pass

        # 15. Escovar os dentes
        if any(w in text_lower for w in ["dente", "dentes", "escova", "escovar"]):
            reply = "Missão Dente Brilhante ativada, Kaleo! Pegue a sua escovinha que o cronômetro de 2 minutos vai começar agora! Vamos deixar o sorriso brilhando!"
            return {
                "ok": True,
                "intencao": "dente",
                "resposta_voz": reply,
                "acao_frontend": "missao_dente",
                "dados": {"duracao_segundos": 120},
            }

        # 16. Guardar brinquedos / Quarto limpo
        if any(w in text_lower for w in ["quarto", "brinquedo", "brinquedos", "guardar", "bagunça", "arrumar"]):
            reply = "Operação Quarto Limpo ativada! Vamos guardar todos os brinquedos no baú antes do tempo acabar! Você é um super-herói veloz!"
            return {
                "ok": True,
                "intencao": "quarto",
                "resposta_voz": reply,
                "acao_frontend": "missao_quarto",
                "dados": {"duracao_segundos": 180},
            }

        # 17. Novos Jogos Educativos (Sistema Solar, Animais, Relógio, Detetive, Ciências, Xadrez, Dinos)
        if any(w in text_lower for w in ["sistema solar", "planetas", "planeta", "astronomia", "galáxia", "saturno", "marte", "júpiter"]):
            reply = f"Nave espacial Stark pronta para decolar, astronauta {self.name}! Abrindo o mapa do Sistema Solar e dos planetas!"
            return {
                "ok": True,
                "intencao": "sistema_solar",
                "resposta_voz": reply,
                "acao_frontend": "abrir_sistema_solar",
                "dados": {},
            }

        if any(w in text_lower for w in ["animais", "animal", "sons dos animais", "som dos animais", "bicho", "bichos", "natureza"]):
            reply = f"Expedição dos Bichos ativada, {self.name}! Vamos ouvir os sons dos animais e aprender sobre a natureza com o Jarvis!"
            return {
                "ok": True,
                "intencao": "reino_animal",
                "resposta_voz": reply,
                "acao_frontend": "abrir_reino_animal",
                "dados": {},
            }

        if any(w in text_lower for w in ["relógio", "relogio", "que horas são", "horas", "minutos"]):
            reply = f"Abrindo o Relógio Mágico do Tempo, herói {self.name}! Vamos aprender as horas e a rotina do dia juntos!"
            return {
                "ok": True,
                "intencao": "relogio_tempo",
                "resposta_voz": reply,
                "acao_frontend": "abrir_relogio_tempo",
                "dados": {},
            }

        if any(w in text_lower for w in ["detetive", "sete erros", "7 erros", "jogo dos erros", "olhos de águia"]):
            reply = f"Ativando olhos de águia, super detetive {self.name}! Vamos encontrar todos os 7 detalhes escondidos na cena!"
            return {
                "ok": True,
                "intencao": "detetive_erros",
                "resposta_voz": reply,
                "acao_frontend": "abrir_detetive_erros",
                "dados": {},
            }

        if any(w in text_lower for w in ["ciência", "ciencias", "experiência", "experiencia", "laboratório", "mistura", "misturas"]):
            reply = f"Laboratório Científico Stark ativo, cientista {self.name}! Vamos misturar poções mágicas e brincar com ímãs!"
            return {
                "ok": True,
                "intencao": "ciencias_misturas",
                "resposta_voz": reply,
                "acao_frontend": "abrir_ciencias_misturas",
                "dados": {},
            }

        if any(w in text_lower for w in ["xadrez", "jogar xadrez", "aprender xadrez", "peça de xadrez", "cavalo em l", "torre"]):
            reply = f"Bem-vindo ao Reino do Xadrez, pequeno grande mestre {self.name}! Vamos aprender a movimentar o Cavalo, a Torre e o Peão!"
            return {
                "ok": True,
                "intencao": "xadrez_mestre",
                "resposta_voz": reply,
                "acao_frontend": "abrir_xadrez_mestre",
                "dados": {},
            }

        if any(w in text_lower for w in ["dinossauro", "dinossauros", "fóssil", "fósseis", "fossil", "fosseis", "t-rex", "t rex", "paleontologia"]):
            reply = f"Pás e pincéis a postos, paleontólogo {self.name}! Vamos escavar a rocha e desenterrar o esqueleto do T-Rex!"
            return {
                "ok": True,
                "intencao": "dinossauros_fosseis",
                "resposta_voz": reply,
                "acao_frontend": "abrir_dinossauros_fosseis",
                "dados": {},
            }

        if any(w in text_lower for w in ["engenharia", "blockly", "programação", "programacao", "robótica", "robotica", "código", "codigo"]):
            reply = f"Abrindo a Bancada de Programação e Engenharia Stark, pequeno engenheiro {self.name}!"
            return {
                "ok": True,
                "intencao": "engenharia_blockly",
                "resposta_voz": reply,
                "acao_frontend": "abrir_engenharia",
                "dados": {},
            }

        if any(w in text_lower for w in ["matemática", "matematica", "somar", "diminuir", "multiplicar", "dividir", "continha", "continhas", "fazer conta", "tabuada", "adição", "adicao", "subtração", "subtracao"]):
            reply = f"Laboratório de Matemática Stark ativo, super campeão {self.name}! Vamos somar, diminuir, multiplicar e dividir com frutas e heróis!"
            return {
                "ok": True,
                "intencao": "matematica_stark",
                "resposta_voz": reply,
                "acao_frontend": "abrir_matematica",
                "dados": {},
            }

        if any(w in text_lower for w in ["reciclagem", "reciclar", "lixo", "lixeira", "guardiões da terra", "guardioes da terra", "meio ambiente", "salvar o planeta"]):
            reply = f"Missão Guardiões da Terra iniciada, herói {self.name}! Vamos separar o lixo nas lixeiras coloridas e cuidar do nosso planeta!"
            return {
                "ok": True,
                "intencao": "reciclagem_planeta",
                "resposta_voz": reply,
                "acao_frontend": "abrir_reciclagem",
                "dados": {},
            }

        if any(w in text_lower for w in ["corrida", "carro", "pilotar", "pista", "turbo", "super carro", "automóvel", "automovel", "corrida turbo"]):
            reply = f"Motores roncando e turbo calibrado, piloto {self.name}! Abrindo a Corrida Turbo Stark! Aperte o cinto e acelere!"
            return {
                "ok": True,
                "intencao": "corrida_turbo",
                "resposta_voz": reply,
                "acao_frontend": "abrir_corrida_turbo",
                "dados": {},
            }

        if any(w in text_lower for w in ["defensor galáctico", "defensor galactico", "tiro espacial", "batalha espacial", "invasores", "jogo de nave", "voo espacial", "homem de ferro"]):
            reply = f"Sistemas de tiro de plasma armados, piloto {self.name}! Abrindo o Defensor Galáctico Stark! Defenda a galáxia com tiros turbo!"
            return {
                "ok": True,
                "intencao": "defensor_galactico",
                "resposta_voz": reply,
                "acao_frontend": "abrir_defensor_galactico",
                "dados": {},
            }

        if any(w in text_lower for w in ["arkanoid", "quebra blocos", "quebra-blocos", "destruir blocos", "bola turbo", "reator arkanoid", "submarino"]):
            reply = f"Base magnética energizada, mestre {self.name}! Abrindo o Reator Arkanoid Stark! Rebata a esfera quântica e quebre todos os blocos!"
            return {
                "ok": True,
                "intencao": "reator_arkanoid",
                "resposta_voz": reply,
                "acao_frontend": "abrir_reator_arkanoid",
                "dados": {},
            }

        if any(w in text_lower for w in ["jetpack", "propulsor", "voar com homem de ferro", "flappy", "gravidade", "voo gravitacional", "hoverboard"]):
            reply = f"Propulsores repulsores acionados, herói {self.name}! Abrindo o Jetpack Repulsor Stark! Voe contra a gravidade e passe pelos portais!"
            return {
                "ok": True,
                "intencao": "jetpack_repulsor",
                "resposta_voz": reply,
                "acao_frontend": "abrir_jetpack_repulsor",
                "dados": {},
            }

        if any(w in text_lower for w in ["cobrinha", "snake", "circuito neon", "jogo da cobrinha", "tron", "helicóptero", "helicoptero"]):
            reply = f"Circuito de alta velocidade conectado, campeão {self.name}! Abrindo o Circuito Neon Stark! Colete os núcleos e acelere no turbo!"
            return {
                "ok": True,
                "intencao": "circuito_neon",
                "resposta_voz": reply,
                "acao_frontend": "abrir_circuito_neon",
                "dados": {},
            }

        # 18. Jogar / Brincar geral (Apenas se nenhum jogo específico acima foi detectado)
        termos_gerais = ["jogar", "jogo", "brincar", "brincadeira", "jogos", "todos os jogos", "menu de jogos", "lista de jogos"]
        if any(w in text_lower for w in termos_gerais):
            reply = "Eba! Adoro brincar com você, Kaleo! Abrindo a lista de todos os jogos incríveis!"
            return {
                "ok": True,
                "intencao": "jogos",
                "resposta_voz": reply,
                "acao_frontend": "abrir_jogos",
                "dados": {},
            }

        # 7. Conversa / Pergunta Geral (IA Local Llama ou Provedor Ativo)
        reply, engine = self.ask(user_text)
        return {
            "ok": True,
            "intencao": "conversa",
            "resposta_voz": reply,
            "acao_frontend": "nenhuma",
            "dados": {"engine": engine},
        }

    def _clean_llm_reply(self, text: str) -> str:
        if not text:
            return ""
        cleaned = re.sub(r"[*_#`~>]", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        # Garante que respostas para criança de 4 anos sejam sempre curtas e nunca desproporcionais
        if len(cleaned) > 200:
            sentences = re.split(r"([.!?]+)", cleaned)
            rebuilt = ""
            for i in range(0, len(sentences) - 1, 2):
                piece = sentences[i] + sentences[i + 1]
                if len(rebuilt + piece) <= 220 or not rebuilt:
                    rebuilt += piece
                else:
                    break
            if rebuilt.strip():
                cleaned = rebuilt.strip()
        return cleaned

    def _build_offline_knowledge(self):
        self.topics = {
            "espaco": [
                "Olhando pelo telescópio Stark! Sabia que o Sol é uma estrela gigante bem quentinha que ilumina o nosso dia? Qual planeta você quer visitar no nosso foguete?",
                "Foguetes preparados! A Lua gira em volta da Terra e brilha lá no céu de noite! Você já viu a Lua pela janela hoje?",
                "Sabia que Marte é chamado de Planeta Vermelho? Um dia os robôs amigáveis vão construir casinhas lá! Vamos viajar juntos na imaginação?",
                "As estrelas lá no céu parecem pequenininhas porque estão muito longe, mas elas são enormes e brilhantes!",
            ],
            "dinossauros": [
                "Radar pré-histórico ligado! O Tiranossauro Rex tinha dentes grandões, mas bracinhos bem curtinhos! Você consegue imitar o rugido de um dinossauro?",
                "O Braquiossauro tinha um pescoço compridão igual a uma girafa gigante para comer folhinhas no alto das árvores!",
                "O Tricerátops tinha três chifres na cabeça e um escudo forte para proteger seus amigos! Qual é o seu dinossauro favorito?",
                "Sabia que muitos passarinhos que cantam hoje na janela são primos distantes dos dinossauros?",
            ],
            "numeros": [
                "Vamos contar nas mãozinhas! Levante um dedinho: um! Mais um: dois! Mais um: três! Mais um: quatro! E a mãozinha cheia dando tchauzinho: cinco! Você é nota dez!",
                "Você tem cinco dedinhos em uma mão e cinco na outra! Juntando as duas mãos abertas, temos dez dedinhos de herói Stark!",
                "Olhe para sua mãozinha! Cada dedinho tem um superpoder: polegar, indicador, médio, anelar e mindinho! Conte com o Járvis de um até dez!",
                "Cinco dedinhos na mão esquerda mais cinco na mão direita! Cinco mais cinco é igual a dez! Parabéns, pequeno gênio!",
                "Um foguete voando, dois coelhinhos pulando, três porquinhos cantando! Contar com os dedinhos é pura diversão!",
            ],
            "animais": [
                "O leão é o rei da selva e faz um rugido bem forte: Uááár! Qual bichinho você mais gosta?",
                "As abelhinhas trabalham juntas visitando as flores coloridas para fazer um mel bem docinho!",
                "O golfinho mora no mar, nada super rápido e adora dar pulos fora da água!",
                "O elefante tem uma tromba comprida que serve para cheirar, pegar frutinhas e tomar banho de chuveirinho!",
            ],
            "heroi": [
                "Armadura calibrada! Lembre-se: o maior superpoder de um herói é ser gentil, dividir os brinquedos e ajudar a família!",
                "Para ter bastante energia no seu Reator Arc, todo super-herói precisa comer comidinha saudável, beber água, ler livrinhos e dormir bem!",
                "Sistemas em cem por cento! Sua imaginação é mais forte que qualquer armadura de ferro! Qual aventura vamos inventar agora?",
            ],
            "elogio": [
                "Sensores indicam que você está aprendendo super rápido hoje! Estou muito orgulhoso de você!",
                "Muito bem! Eu adoro conversar, ouvir sua voz e descobrir coisas novas com você!",
                "Nota dez nos circuitos da inteligência! Continue curioso e alegre assim!",
            ],
            "adivinha": [
                "Vamos brincar de adivinhar! Eu sou amarelo, moro lá no alto do céu e deixo o dia bem quentinho. Quem sou eu?",
                "Adivinha só quem eu sou! Tenho orelhas compridas, adoro pular e comer cenoura crocante! Você sabe qual bichinho é?",
                "Desafio do Járvis! Eu tenho muitas páginas coloridas e guardo histórias mágicas dentro de mim. Quem sou eu? Isso mesmo, o livro!",
            ],
        }

    def get_greeting(self) -> str:
        greetings = [
            f"Olá, {self.name}! Eu sou o Járvis! Todos os sistemas educativos estão prontos para brincar!",
            f"Reator Arc ligado, {self.name}! Quer abrir um livro mágico ou segurar o botão para conversar comigo?",
            f"Sistemas prontos, {self.name}! Escolha um botão colorido na tela para começarmos a aventura!",
        ]
        return random.choice(greetings)

    def ask_topic(self, topic: str) -> str:
        return self.ask_topic_detailed(topic)["reply"]

    def ask_topic_detailed(self, topic: str) -> dict:
        prompts_map = {
            "espaco": f"Conte uma curiosidade mágica e alegre sobre planetas, foguetes ou estrelas para {self.name} (4 anos) e faça uma perguntinha divertida.",
            "dinossauros": f"Conte uma curiosidade divertida e amigável sobre dinossauros para {self.name} (4 anos) e pergunte qual dinossauro ele gosta.",
            "numeros": f"Faça uma brincadeira curta e animada contando números com {self.name} (4 anos).",
            "animais": f"Conte uma curiosidade fofa sobre um animal da natureza para {self.name} (4 anos) e convide para imitar o som do bichinho.",
            "heroi": f"Dê uma mensagem carinhosa estilo JARVIS para o pequeno herói {self.name} (4 anos), elogiando a bondade e a leitura de livros.",
            "elogio": f"Faça um elogio super carinhoso e animado para {self.name} (4 anos).",
            "adivinha": f"Faça uma brincadeira fácil e divertida de 'O que é, o que é?' sobre animais ou natureza para {self.name} (4 anos) adivinhar!",
        }

        if topic in prompts_map and self.provider != "offline":
            ans, engine = self._try_smart_conversation(prompts_map[topic])
            if ans:
                return {"reply": ans, "engine_used": engine}

        options = self.topics.get(topic, self.topics["elogio"])
        chosen = random.choice(options)
        return {
            "reply": f"{self.name}, {chosen[0].lower()}{chosen[1:]}",
            "engine_used": "offline",
        }

    def ask_custom(self, question: str) -> str:
        return self.ask_custom_detailed(question)["reply"]

    def ask_custom_detailed(self, question: str) -> dict:
        if self.provider != "offline":
            ans, engine = self._try_smart_conversation(question)
            if ans:
                return {"reply": ans, "engine_used": engine}

        return {
            "reply": self._offline_conversational_fallback(question),
            "engine_used": "offline",
        }

    def ask(self, question: str) -> tuple[str, str]:
        """Método unificado de consulta ao cérebro do Jarvis (retorna reply, engine_used)."""
        res = self.ask_custom_detailed(question)
        return res.get("reply", ""), res.get("engine_used", "offline")

    def _offline_conversational_fallback(self, question: str) -> str:
        q_low = question.lower()
        if re.search(r"\b(oi|ol[áa]|bom dia|boa tarde|boa noite|tudo bem)\b", q_low):
            return f"Oi, {self.name}! Eu estou super feliz em conversar com você! Sobre o que você quer brincar agora: dinossauros, foguetes ou histórias?"
        if any(w in q_low for w in ["sol", "lua", "estrela", "planeta", "espaço", "espaco", "foguete"]):
            return self.ask_topic("espaco")
        if any(w in q_low for w in ["dino", "rex", "tiranossauro"]):
            return self.ask_topic("dinossauros")
        if any(w in q_low for w in ["conta", "número", "numero", "quantos", "um", "dois"]):
            return self.ask_topic("numeros")
        if any(w in q_low for w in ["bicho", "animal", "leão", "leao", "cachorro", "gato", "elefante", "macaco"]):
            return self.ask_topic("animais")
        if any(w in q_low for w in ["história", "historia", "livro", "era uma vez"]):
            return f"Eu adoro histórias, {self.name}! Que tal abrirmos a Biblioteca de Histórias para ver os Três Porquinhos ou o Tito Dinossauro?"
        if any(w in q_low for w in ["adivinha", "brincar", "jogo", "charada"]):
            return self.ask_topic("adivinha")
        if any(w in q_low for w in ["cor", "cores", "azul", "vermelho", "amarelo", "verde", "rosa", "roxo"]):
            return f"As cores são mágicas, {self.name}! O azul é da cor do céu, o amarelo é do Sol quentinho e o vermelho é do Reator Stark! Qual é a sua cor preferida?"
        if any(w in q_low for w in ["carro", "avião", "aviao", "trem", "barco", "foguete", "caminhão", "caminhao"]):
            return f"Motores roncando! Vrum, vrum! Eu adoro máquinas velozes! Você quer pilotar um carro de corrida ou um foguete espacial comigo?"
        if any(w in q_low for w in ["comida", "fruta", "banana", "maçã", "maca", "laranja", "fome", "comer"]):
            return f"Hummm, comer frutinhas bem doces e comidinha saudável dá muita energia para o reator de todo super-herói! Qual fruta você mais gosta de morder?"
        if any(w in q_low for w in ["música", "musica", "cantar", "piano", "bateria", "canção", "cancao"]):
            return f"A música deixa o coração alegre, {self.name}! Que tal abrirmos o Laboratório Musical para tocar piano ou fazer barulho na Bateria Stark?"
        if any(w in q_low for w in ["papai", "pai", "mamãe", "mamae", "mãe", "mae", "família", "familia"]):
            return f"A sua família tem o maior superpoder do mundo: o amor e o carinho por você! Já deu um abraço bem apertado neles hoje?"
        if any(w in q_low for w in ["bravo", "raiva", "triste", "medo", "chorar"]):
            return f"Quando bater uma sensação difícil, {self.name}, lembre-se: respire bem fundo três vezes, cheirando a florzinha e assoprando a velinha! Eu estou aqui com você!"
        # Super-heróis e personagens infantis famosos
        if any(w in q_low for w in ["aranha", "spider", "peter parker"]):
            return "O Homem-Aranha é o Peter Parker! Ele ganhou superpoderes de aranha, escala paredes, solta teias e protege a cidade com muita coragem e alegria!"
        if any(w in q_low for w in ["homem de ferro", "iron man", "tony stark"]):
            return "O Homem de Ferro é o Tony Stark! Ele é um inventor genial que criou uma super armadura cheia de tecnologia e um Reator Arc brilhante no peito!"
        if any(w in q_low for w in ["batman", "homem morcego", "bruce wayne"]):
            return "O Batman é o Bruce Wayne! Ele é um herói super esperto que usa o Batmóvel, bat-bumerangues e sua capa para proteger a cidade!"
        if any(w in q_low for w in ["hulk", "gigante verde", "bruce banner"]):
            return "O Hulk é o cientista Bruce Banner! Quando ele fica bravo, ele vira um gigante verde super forte, mas ele tem um bom coração e protege os amigos!"
        if any(w in q_low for w in ["capitão américa", "capitao america", "steve rogers"]):
            return "O Capitão América é o Steve Rogers! Ele usa um escudo de vibranium indestrutível e lidera os heróis com muita coragem e lealdade!"
        if any(w in q_low for w in ["flash", "barry allen"]):
            return "O Flash é o herói mais veloz do mundo! Ele corre tão rápido quanto um raio e sempre chega a tempo de salvar todo mundo!"
        if any(w in q_low for w in ["superman", "super-homem", "super homem", "clark kent"]):
            return "O Super-Homem veio do planeta Krypton! Ele voa lá no alto das nuvens, tem super força e uma capa vermelha linda!"
        if any(w in q_low for w in ["vingadores", "liga da justiça", "liga da justica", "super heroi", "super-heroi"]):
            return "Os super-heróis trabalham sempre em equipe com muito amor e coragem! Qual é o seu herói favorito?"
        if any(w in q_low for w in ["stark", "ferro", "armadura", "jarvis", "robô", "robo"]):
            return self.ask_topic("heroi")
        return f"Que legal o que você falou, {self.name}! Segure o botão para me contar mais ou toque num desenho colorido para brincarmos juntos!"

    def _try_smart_conversation(self, user_input: str) -> tuple[str, str]:
        prov = self.provider

        if prov == "opencode":
            ans = self._call_opencode(user_input)
            if ans:
                return self.sanitizar_resposta_infantil(ans), "opencode"
            # Fallback para Ollama se disponível localmente
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return self.sanitizar_resposta_infantil(ans_local), "ollama"

        elif prov == "gemini":
            ans = self._call_gemini_interactions(user_input)
            if ans:
                return self.sanitizar_resposta_infantil(ans), "gemini"
            # Fallback para Ollama se disponível localmente
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return self.sanitizar_resposta_infantil(ans_local), "ollama"

        elif prov == "openai":
            ans = self._call_openai(user_input)
            if ans:
                return self.sanitizar_resposta_infantil(ans), "openai"
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return self.sanitizar_resposta_infantil(ans_local), "ollama"

        elif prov == "groq":
            ans = self._call_groq(user_input)
            if ans:
                return self.sanitizar_resposta_infantil(ans), "groq"
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return self.sanitizar_resposta_infantil(ans_local), "ollama"

        elif prov == "ollama":
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return self.sanitizar_resposta_infantil(ans_local), "ollama"
            if self.get_effective_gemini_key():
                ans_gem = self._call_gemini_interactions(user_input)
                if ans_gem:
                    return self.sanitizar_resposta_infantil(ans_gem), "gemini"

        return "", ""

    def _call_opencode(self, user_input: str) -> str:
        """Executa o OpenCode CLI ou orquestra via servidor OpenCode LAN."""
        try:
            cli = self.config.get("opencode_cli_path", "opencode")
            model = self.config.get("opencode_model", "google/gemini-2.0-flash")
            server = self.config.get("opencode_server", "").strip()

            prompt = (
                f"{self._child_system_instruction()}\n\n"
                f"Mensagem da criança {self.name}: {user_input}\n"
                f"Responda diretamente em no máximo 1 ou 2 frases carinhosas e alegres."
            )

            cmd = [cli, "run", prompt, "--format", "default"]
            if model:
                cmd.extend(["--model", model])
            if server:
                cmd.extend(["--server", server])

            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=18,
                shell=(sys.platform == "win32"),
            )
            out = (res.stdout or "").strip()
            if out:
                ans = self._clean_llm_reply(out)
                if ans:
                    self.local_history.append({"role": "user", "content": user_input})
                    self.local_history.append({"role": "assistant", "content": ans})
                    return ans
        except Exception:
            pass
        return ""

    def _call_gemini_interactions(self, user_input: str, override_key: str = "") -> str:
        api_key = override_key.strip() or self.get_effective_gemini_key()
        if not api_key:
            return ""
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            model_name = self.config.get("gemini_model", "gemini-3.8-flash") or "gemini-3.8-flash"
            if any(old in model_name for old in ("1.5", "2.0", "2.5")):
                model_name = "gemini-3.8-flash"

            kwargs = {
                "model": model_name,
                "system_instruction": self._child_system_instruction(),
                "input": user_input,
                "generation_config": {"max_output_tokens": 220},
            }
            if self.last_gemini_interaction_id and not override_key:
                kwargs["previous_interaction_id"] = self.last_gemini_interaction_id

            try:
                interaction = client.interactions.create(**kwargs)
            except Exception:
                kwargs.pop("previous_interaction_id", None)
                interaction = client.interactions.create(**kwargs)

            if not override_key and getattr(interaction, "id", None):
                self.last_gemini_interaction_id = interaction.id

            reply = self._clean_llm_reply(getattr(interaction, "output_text", "") or "")
            return reply
        except Exception:
            return ""

    def _call_openai(self, user_input: str, override_key: str = "") -> str:
        key = override_key.strip() or self.get_effective_openai_key()
        if not key:
            return ""
        try:
            model = self.config.get("openai_model", "gpt-4o-mini")
            messages = [{"role": "system", "content": self._child_system_instruction()}]
            messages.extend(self.local_history[-6:])
            messages.append({"role": "user", "content": user_input})

            payload = json.dumps({
                "model": model,
                "messages": messages,
                "max_tokens": 140,
                "temperature": 0.6,
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode("utf-8"))
                reply = self._clean_llm_reply(data["choices"][0]["message"]["content"])
                if reply:
                    self.local_history.append({"role": "user", "content": user_input})
                    self.local_history.append({"role": "assistant", "content": reply})
                return reply
        except Exception:
            return ""

    def _call_groq(self, user_input: str, override_key: str = "") -> str:
        key = override_key.strip() or self.get_effective_groq_key()
        if not key:
            return ""
        try:
            model = self.config.get("groq_model", "llama-3.3-70b-versatile")
            messages = [{"role": "system", "content": self._child_system_instruction()}]
            messages.extend(self.local_history[-6:])
            messages.append({"role": "user", "content": user_input})

            payload = json.dumps({
                "model": model,
                "messages": messages,
                "max_tokens": 140,
                "temperature": 0.6,
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            )
            with urllib.request.urlopen(req, timeout=8) as res:
                data = json.loads(res.read().decode("utf-8"))
                reply = self._clean_llm_reply(data["choices"][0]["message"]["content"])
                if reply:
                    self.local_history.append({"role": "user", "content": user_input})
                    self.local_history.append({"role": "assistant", "content": reply})
                return reply
        except Exception:
            return ""

    def _call_ollama(self, user_input: str) -> str:
        try:
            self._ensure_ollama_running()
            base_url = self.config.get("ollama_url", "http://127.0.0.1:11434").rstrip("/")
            url = f"{base_url}/api/chat"
            preferred_model = self.config.get("ollama_model", "llama3.2:1b")

            # Descobre modelos disponíveis no Ollama para evitar 404
            available = []
            try:
                with urllib.request.urlopen(f"{base_url}/api/tags", timeout=1.5) as r:
                    tags = json.loads(r.read().decode("utf-8"))
                    available = [item.get("name") for item in tags.get("models", [])]
            except Exception:
                pass

            models_to_try = []
            if preferred_model in available:
                models_to_try.append(preferred_model)
            elif available:
                models_to_try.append(available[0])
            else:
                models_to_try.extend([preferred_model, "llama3.2:1b", "qwen2.5:0.5b"])

            messages = [{"role": "system", "content": self._child_system_instruction()}]
            messages.extend(self.local_history[-6:])
            messages.append({"role": "user", "content": user_input})

            for m in models_to_try:
                try:
                    payload = json.dumps({
                        "model": m,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": 0.45, "num_predict": 110},
                    }).encode("utf-8")
                    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=22) as res:
                        data = json.loads(res.read().decode("utf-8"))
                        ans = self._clean_llm_reply((data.get("message") or {}).get("content", ""))
                        if ans:
                            self.local_history.append({"role": "user", "content": user_input})
                            self.local_history.append({"role": "assistant", "content": ans})
                            return ans
                except Exception:
                    continue
        except Exception:
            pass
        return ""

    def test_provider(self, provider: str, candidate_key: str = "", model: str = "", ollama_url: str = "") -> tuple[bool, str]:
        """Testa e valida ao vivo qualquer um dos provedores no Painel dos Pais."""
        p = provider.lower()
        test_prompt = f"Dê um oi bem alegre de 1 frase dizendo que você está pronto para ser o melhor amigo robô de {self.name}!"

        if p == "opencode":
            cli = self.config.get("opencode_cli_path", "opencode")
            try:
                res = subprocess.run(
                    [cli, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=(sys.platform == "win32"),
                )
                ver = (res.stdout or "").strip()
                if "opencode" in ver.lower():
                    m = model.strip() or self.config.get("opencode_model", "google/gemini-2.0-flash")
                    return True, f"OpenCode CLI detectado com sucesso ({ver})! Pronto para orquestrar com o modelo: {m}."
                return False, f"OpenCode executou, mas resposta foi: {ver[:90]}"
            except Exception as exc:
                return False, f"OpenCode CLI não encontrado no PATH: {str(exc)[:120]}"

        elif p == "gemini":
            key = candidate_key.strip() or self.get_effective_gemini_key()
            if not key:
                return False, "Cole a chave do Google Gemini (obtida em aistudio.google.com/apikey) para testar."
            try:
                from google import genai

                client = genai.Client(api_key=key)
                m = model.strip() or self.config.get("gemini_model", "gemini-3.8-flash")
                interaction = client.interactions.create(
                    model=m,
                    system_instruction=self._child_system_instruction(),
                    input=test_prompt,
                    generation_config={"max_output_tokens": 90},
                )
                txt = self._clean_llm_reply(getattr(interaction, "output_text", "") or "")
                if txt:
                    return True, txt
                return False, "Conectou ao Gemini, mas não houve texto retornado."
            except Exception as exc:
                return False, f"Erro Gemini: {str(exc)[:130]}"

        elif p == "openai":
            key = candidate_key.strip() or self.get_effective_openai_key()
            if not key:
                return False, "Cole sua chave da OpenAI (sk-...) para testar o ChatGPT."
            try:
                m = model.strip() or self.config.get("openai_model", "gpt-4o-mini")
                payload = json.dumps({
                    "model": m,
                    "messages": [
                        {"role": "system", "content": self._child_system_instruction()},
                        {"role": "user", "content": test_prompt},
                    ],
                    "max_tokens": 90,
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    data=payload,
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
                )
                with urllib.request.urlopen(req, timeout=10) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    txt = self._clean_llm_reply(data["choices"][0]["message"]["content"])
                    return True, txt
            except Exception as exc:
                return False, f"Erro OpenAI: {str(exc)[:130]}"

        elif p == "groq":
            key = candidate_key.strip() or self.get_effective_groq_key()
            if not key:
                return False, "Cole sua chave Groq (gsk_...) para testar."
            try:
                m = model.strip() or self.config.get("groq_model", "llama-3.3-70b-versatile")
                payload = json.dumps({
                    "model": m,
                    "messages": [
                        {"role": "system", "content": self._child_system_instruction()},
                        {"role": "user", "content": test_prompt},
                    ],
                    "max_tokens": 90,
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=payload,
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
                )
                with urllib.request.urlopen(req, timeout=10) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    txt = self._clean_llm_reply(data["choices"][0]["message"]["content"])
                    return True, txt
            except Exception as exc:
                return False, f"Erro Groq: {str(exc)[:130]}"

        elif p == "ollama":
            url = (ollama_url.strip() or self.config.get("ollama_url", "http://127.0.0.1:11434")).rstrip("/")
            try:
                with urllib.request.urlopen(f"{url}/api/tags", timeout=5) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    models = [m.get("name", "") for m in data.get("models", [])]

                target_model = model.strip() or self.config.get("ollama_model", "llama3.2:1b")
                if models and target_model not in models:
                    target_model = models[0]

                chat_payload = json.dumps({
                    "model": target_model,
                    "messages": [
                        {"role": "system", "content": f"Você é o robô JARVIS, melhor amigo de {self.name}. Dê um oi alegre em uma frase curta."},
                        {"role": "user", "content": "Oi Jarvis!"}
                    ],
                    "stream": False,
                    "options": {"num_predict": 45}
                }).encode("utf-8")
                chat_req = urllib.request.Request(f"{url}/api/chat", data=chat_payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(chat_req, timeout=12) as c_res:
                    c_data = json.loads(c_res.read().decode("utf-8"))
                    reply = self._clean_llm_reply((c_data.get("message") or {}).get("content", ""))
                    return True, f"Ollama Local ({target_model}) respondeu perfeitamente: \"{reply}\""
            except Exception as exc:
                return False, f"Ollama em {url}: {str(exc)[:120]}"

        return False, "Provedor desconhecido."
