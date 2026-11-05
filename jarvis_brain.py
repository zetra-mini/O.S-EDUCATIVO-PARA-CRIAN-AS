import json
import os
import random
import re
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "child_name": "Pequeno Inventor",
    "mode": "gemini",  # 'gemini' (Google Gemini 3.8), 'ollama' (IA Local), 'offline' (100% sem Wi-Fi), 'cloud'
    "gemini_api_key": "",
    "gemini_model": "gemini-3.8-flash",
    "voice_profile": "jarvis_antonio",  # 'jarvis_antonio', 'amiga_thalita', 'amiga_francisca', 'gemini_puck', 'gemini_sulafat'
    "prefer_neural_voice": True,
    "ollama_url": "http://127.0.0.1:11434",
    "ollama_model": "qwen2.5:0.5b",
    "cloud_provider": "groq",  # 'groq', 'openai'
    "cloud_api_key": "",
    "cloud_model": "llama-3.3-70b-versatile",
    "voice_enabled": True,
    "media_start_time": "16:00",
    "media_end_time": "17:00",
    "media_daily_minutes": 25,
    "require_book_before_media": True,
    "custom_books": [],
}


class JarvisBrain:
    """
    Cérebro híbrido do JARVIS Kids OS v2.1:
    1. Modo Google Gemini (gemini-3.8-flash): Conversa natural multi-turno segura para crianças de 4 anos via google-genai Interactions API.
    2. Modo IA Local (Ollama / OpenCode): Conecta a http://127.0.0.1:11434 sem custo e 100% local.
    3. Modo Offline (Acer Aspire One 532 sem Wi-Fi): Zero latência e < 5 MB RAM.
    4. Modo Cloud Adicional: Conecta a Groq / OpenAI.
    Todos os modos possuem fallback automático em cascata para nunca deixar a criança sem resposta!
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
        self.local_history = []

    @property
    def name(self) -> str:
        return self.config.get("child_name", "Pequeno Inventor").strip() or "Pequeno Inventor"

    def get_effective_gemini_key(self) -> str:
        k = (
            self.config.get("gemini_api_key", "").strip()
            or os.environ.get("GEMINI_API_KEY", "").strip()
            or os.environ.get("GOOGLE_API_KEY", "").strip()
        )
        if not k and self.config.get("cloud_provider") == "gemini":
            k = self.config.get("cloud_api_key", "").strip()
        return k

    def _child_system_instruction(self) -> str:
        return (
            f"Você é o Járvis junto com o Amigo Google Gemini, o melhor amigo robô carinhoso, alegre e curioso "
            f"de uma criança brasileira de 4 anos chamada {self.name}. "
            f"REGRAS OBRIGATÓRIAS PARA VOZ INFANTIL:\n"
            f"1. Fale sempre em Português do Brasil bem natural, afetuoso, lúdico e fácil para 4 anos.\n"
            f"2. Responda em NO MÁXIMO 2 ou 3 frases curtas, pois sua resposta será lida em voz alta.\n"
            f"3. NUNCA use asteriscos (*), hashtags (#), listas ou formatação markdown — escreva texto puro pronto para fala.\n"
            f"4. Incentive sempre a curiosidade, a gentileza, acalmar as emoções respirando fundo e o amor por ler livros.\n"
            f"5. Sempre que fizer sentido, termine com uma perguntinha divertida e simples para continuar a conversa com {self.name}!"
        )

    def _clean_llm_reply(self, text: str) -> str:
        if not text:
            return ""
        cleaned = re.sub(r"[*_#`~>]", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
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
                "Vamos contar juntos nos propulsores! Um, dois, três, quatro, cinco, seis, sete, oito, nove, dez! Decolar!",
                "Você tem cinco dedinhos em uma mão e cinco na outra! Juntando as duas mãos, temos dez dedinhos super espertos!",
                "Um olhinho, dois olhinhos! Uma orelhinha, duas orelhinhas! Você conta super bem!",
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
            f"Olá, {self.name}! Eu sou o Járvis com sua nova voz! Todos os sistemas e o modo conversa estão prontos!",
            f"Bem-vindo de volta, {self.name}! Reator Arc ligado. Quer ler um livro mágico ou conversar comigo pelo microfone?",
            f"Sistemas prontos, {self.name}! Escolha uma missão na tela ou aperte o microfone para batermos um papo!",
        ]
        return random.choice(greetings)

    def ask_topic(self, topic: str) -> str:
        res = self.ask_topic_detailed(topic)
        return res["reply"]

    def ask_topic_detailed(self, topic: str) -> dict:
        prompts_map = {
            "espaco": f"Conte uma curiosidade mágica e alegre sobre planetas, foguetes ou estrelas para {self.name} (4 anos) e faça uma perguntinha divertida.",
            "dinossauros": f"Conte uma curiosidade divertida e amigável sobre dinossauros para {self.name} (4 anos) e pergunte qual dinossauro ele gosta.",
            "numeros": f"Faça uma brincadeira curta e animada contando números com {self.name} (4 anos).",
            "animais": f"Conte uma curiosidade fofa sobre um animal da natureza para {self.name} (4 anos) e convide para imitar o som do bichinho.",
            "heroi": f"Dê uma mensagem carinhosa estilo JARVIS e Google Gemini para o pequeno herói {self.name} (4 anos), elogiando a bondade e a leitura de livros.",
            "elogio": f"Faça um elogio super carinhoso e animado para {self.name} (4 anos).",
            "adivinha": f"Faça uma brincadeira fácil e divertida de 'O que é, o que é?' sobre animais ou natureza para {self.name} (4 anos) adivinhar!",
        }

        if topic in prompts_map and self.config.get("mode", "gemini") != "offline":
            ans, engine = self._try_smart_conversation(prompts_map[topic])
            if ans:
                return {
                    "reply": ans,
                    "engine_used": engine,
                    "has_gemini_key": bool(self.get_effective_gemini_key()),
                }

        options = self.topics.get(topic, self.topics["elogio"])
        chosen = random.choice(options)
        return {
            "reply": f"{self.name}, {chosen[0].lower()}{chosen[1:]}",
            "engine_used": "offline",
            "has_gemini_key": bool(self.get_effective_gemini_key()),
        }

    def ask_custom(self, question: str) -> str:
        return self.ask_custom_detailed(question)["reply"]

    def ask_custom_detailed(self, question: str) -> dict:
        if self.config.get("mode", "gemini") != "offline":
            ans, engine = self._try_smart_conversation(question)
            if ans:
                return {
                    "reply": ans,
                    "engine_used": engine,
                    "has_gemini_key": bool(self.get_effective_gemini_key()),
                }

        return {
            "reply": self._offline_conversational_fallback(question),
            "engine_used": "offline",
            "has_gemini_key": bool(self.get_effective_gemini_key()),
        }

    def _offline_conversational_fallback(self, question: str) -> str:
        q_low = question.lower()
        if any(w in q_low for w in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "tudo bem"]):
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
            return f"Eu adoro histórias, {self.name}! Era uma vez um pequeno inventor muito corajoso que tinha um amigo robô brilhante. Vamos abrir nossa Biblioteca de Livros para ver as figuras?"
        if any(w in q_low for w in ["adivinha", "brincar", "jogo", "charada"]):
            return self.ask_topic("adivinha")
        return f"Que legal o que você falou, {self.name}! Me conta mais um pouquinho sobre isso ou escolha um tema divertido para explorarmos juntos!"

    def _try_smart_conversation(self, user_input: str) -> tuple[str, str]:
        mode = self.config.get("mode", "gemini")

        # 1. Google Gemini 3.8 Flash (Prioridade quando selecionado ou como provedor cloud)
        if mode == "gemini" or (mode == "cloud" and self.config.get("cloud_provider") == "gemini"):
            ans = self._call_gemini_interactions(user_input)
            if ans:
                return ans, "gemini"
            # Se ainda não há chave Gemini configurada, tenta IA Local (Ollama) automaticamente!
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return ans_local, "ollama"
            return "", ""

        # 2. IA Local (Ollama / OpenCode Localhost)
        if mode == "ollama":
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return ans_local, "ollama"
            if self.get_effective_gemini_key():
                ans = self._call_gemini_interactions(user_input)
                if ans:
                    return ans, "gemini"
            return "", ""

        # 3. Outras Nuvens (Groq / OpenAI)
        if mode == "cloud":
            ans_cloud = self._call_openai_compatible(user_input)
            if ans_cloud:
                return ans_cloud, "cloud"
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return ans_local, "ollama"

        return "", ""

    def _call_gemini_interactions(self, user_input: str, override_key: str = "") -> str:
        api_key = override_key.strip() or self.get_effective_gemini_key()
        if not api_key:
            return ""
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            model_name = self.config.get("gemini_model", "gemini-3.8-flash") or "gemini-3.8-flash"
            # Garante uso de modelos Gemini atuais (nunca legados 1.5/2.0/2.5)
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
                # Se o previous_interaction_id expirou, inicia nova sessão limpa
                kwargs.pop("previous_interaction_id", None)
                interaction = client.interactions.create(**kwargs)

            if not override_key and getattr(interaction, "id", None):
                self.last_gemini_interaction_id = interaction.id

            reply = self._clean_llm_reply(getattr(interaction, "output_text", "") or "")
            return reply
        except Exception:
            return ""

    def test_gemini_connection(self, candidate_key: str = "") -> tuple[bool, str]:
        """Valida a chave do Google Gemini ao vivo para o Painel dos Pais."""
        key = candidate_key.strip() or self.get_effective_gemini_key()
        if not key:
            return (
                False,
                "Cole sua chave gratuita do Google AI Studio (GEMINI_API_KEY) no campo acima para ativar o Google Gemini oficial!",
            )
        try:
            from google import genai

            client = genai.Client(api_key=key)
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                system_instruction=self._child_system_instruction(),
                input=f"Dê um oi bem alegre e curtinho dizendo que o Google Gemini agora está conectado no JARVIS para conversar com {self.name}!",
                generation_config={"max_output_tokens": 120},
            )
            txt = self._clean_llm_reply(getattr(interaction, "output_text", "") or "")
            if txt:
                return True, txt
            return False, "Conectou ao Gemini, mas a resposta veio vazia. Tente novamente."
        except Exception as exc:
            return False, f"Não foi possível autenticar a chave no Google Gemini: {str(exc)[:140]}"

    def _call_ollama(self, user_input: str) -> str:
        try:
            url = self.config.get("ollama_url", "http://127.0.0.1:11434").rstrip("/") + "/api/chat"
            messages = [{"role": "system", "content": self._child_system_instruction()}]
            messages.extend(self.local_history[-6:])
            messages.append({"role": "user", "content": user_input})

            payload = json.dumps(
                {
                    "model": self.config.get("ollama_model", "qwen2.5:0.5b"),
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.55, "num_predict": 110},
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                url, data=payload, headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=12) as res:
                data = json.loads(res.read().decode("utf-8"))
                ans = self._clean_llm_reply(
                    (data.get("message") or {}).get("content", "")
                )
                if ans:
                    self.local_history.append({"role": "user", "content": user_input})
                    self.local_history.append({"role": "assistant", "content": ans})
                    return ans
        except Exception:
            pass
        return ""

    def _call_openai_compatible(self, user_input: str) -> str:
        try:
            provider = self.config.get("cloud_provider", "groq")
            key = self.config.get("cloud_api_key", "").strip()
            model = self.config.get("cloud_model", "llama-3.3-70b-versatile")
            if not key:
                return ""
            base = (
                "https://api.groq.com/openai/v1"
                if provider == "groq"
                else "https://api.openai.com/v1"
            )
            payload = json.dumps(
                {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": self._child_system_instruction()},
                        {"role": "user", "content": user_input},
                    ],
                    "max_tokens": 140,
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                f"{base}/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode("utf-8"))
                return self._clean_llm_reply(
                    data["choices"][0]["message"]["content"]
                )
        except Exception:
            return ""
