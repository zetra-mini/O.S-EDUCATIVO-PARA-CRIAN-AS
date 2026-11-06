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
            f"Você é o JÁRVIS, o amigo robô amável, protetor e animado do pequeno {self.name} (criança de 4 anos). "
            f"REGRAS INFANTIS INDISPENSÁVEIS:\n"
            f"1. Fale sempre em Português do Brasil com carinho, alegria e vocabulário simples e lúdico.\n"
            f"2. A criança NÃO SABE LER NEM ESCREVER! Sua resposta será lida em voz alta. Responda em no máximo 2 ou 3 frases curtas!\n"
            f"3. NUNCA use formatação markdown como asteriscos (*), hashtags (#), hifens (-) ou tópicos.\n"
            f"4. Incentive o hábito de ler livrinhos, respirar fundo quando ficar agitado e a imaginação.\n"
            f"5. Termine com uma perguntinha divertida e simples para ele responder pelo microfone!"
        )

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
        if any(w in q_low for w in ["stark", "ferro", "armadura", "jarvis", "robô", "robo"]):
            return self.ask_topic("heroi")
        return f"Que legal o que você falou, {self.name}! Segure o botão para me contar mais ou toque num desenho colorido para brincarmos juntos!"

    def _try_smart_conversation(self, user_input: str) -> tuple[str, str]:
        prov = self.provider

        if prov == "opencode":
            ans = self._call_opencode(user_input)
            if ans:
                return ans, "opencode"
            # Fallback para Ollama se disponível localmente
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return ans_local, "ollama"

        elif prov == "gemini":
            ans = self._call_gemini_interactions(user_input)
            if ans:
                return ans, "gemini"
            # Fallback para Ollama se disponível localmente
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return ans_local, "ollama"

        elif prov == "openai":
            ans = self._call_openai(user_input)
            if ans:
                return ans, "openai"
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return ans_local, "ollama"

        elif prov == "groq":
            ans = self._call_groq(user_input)
            if ans:
                return ans, "groq"
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return ans_local, "ollama"

        elif prov == "ollama":
            ans_local = self._call_ollama(user_input)
            if ans_local:
                return ans_local, "ollama"
            if self.get_effective_gemini_key():
                ans_gem = self._call_gemini_interactions(user_input)
                if ans_gem:
                    return ans_gem, "gemini"

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
            base_url = self.config.get("ollama_url", "http://127.0.0.1:11434").rstrip("/")
            url = f"{base_url}/api/chat"
            preferred_model = self.config.get("ollama_model", "llama3.2:1b")

            models_to_try = [preferred_model]
            if preferred_model != "llama3.2:1b":
                models_to_try.append("llama3.2:1b")
            if "qwen2.5:0.5b" not in models_to_try:
                models_to_try.append("qwen2.5:0.5b")

            messages = [{"role": "system", "content": self._child_system_instruction()}]
            messages.extend(self.local_history[-6:])
            messages.append({"role": "user", "content": user_input})

            for m in models_to_try:
                try:
                    payload = json.dumps({
                        "model": m,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": 0.55, "num_predict": 110},
                    }).encode("utf-8")
                    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=14) as res:
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
