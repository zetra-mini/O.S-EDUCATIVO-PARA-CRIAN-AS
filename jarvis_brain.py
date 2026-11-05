import json
import os
import random
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "child_name": "Pequeno Inventor",
    "mode": "offline",  # 'offline' (padrão 100% sem Wi-Fi), 'ollama', 'cloud'
    "ollama_url": "http://127.0.0.1:11434",
    "ollama_model": "qwen2.5:0.5b",
    "cloud_provider": "groq",  # 'groq', 'gemini', 'openai'
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
    Cérebro híbrido do JARVIS Kids OS:
    1. Modo Offline (Padrão para Acer Aspire One 532): 100% sem Wi-Fi, zero latência e < 5 MB RAM.
    2. Modo Ollama: Conecta a um servidor Ollama na rede local (com fallback automático para offline).
    3. Modo Cloud: Conecta a Groq / Gemini / OpenAI (com fallback automático para offline).
    """

    def __init__(self):
        self.config = dict(DEFAULT_CONFIG)
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

    @property
    def name(self) -> str:
        return self.config.get("child_name", "Pequeno Inventor").strip() or "Pequeno Inventor"

    def _build_offline_knowledge(self):
        self.topics = {
            "espaco": [
                "Olhando pelo telescópio Stark! Sabia que o Sol é uma estrela gigante bem quentinha que ilumina o nosso dia?",
                "Foguetes preparados! A Lua gira em volta da Terra e brilha lá no céu de noite!",
                "Sabia que Marte é chamado de Planeta Vermelho? Um dia os robôs vão construir casinhas lá!",
                "As estrelas lá no céu parecem pequenininhas porque estão muito longe, mas elas são enormes!",
            ],
            "dinossauros": [
                "Radar pré-histórico ligado! O Tiranossauro Rex tinha dentes grandões, mas bracinhos bem curtinhos!",
                "O Braquiossauro tinha um pescoço compridão igual a uma girafa gigante para comer folhinhas no alto das árvores!",
                "O Tricerátops tinha três chifres na cabeça e um escudo forte para proteger seus amigos!",
                "Sabia que muitos passarinhos de hoje são parentes distantes dos dinossauros?",
            ],
            "numeros": [
                "Vamos contar juntos nos propulsores! Um, dois, três, quatro, cinco, seis, sete, oito, nove, dez! Decolar!",
                "Você tem cinco dedinhos em uma mão e cinco na outra! Juntando as duas mãos, temos dez dedinhos!",
                "Um olhinho, dois olhinhos! Uma orelhinha, duas orelhinhas! Você é muito esperto!",
            ],
            "animais": [
                "O leão é o rei da selva e faz um rugido bem forte: Uááár!",
                "As abelhinhas trabalham juntas visitando as flores coloridas para fazer um mel bem docinho!",
                "O golfinho mora no mar, nada super rápido e adora dar pulos fora da água!",
                "O elefante tem uma tromba comprida que serve para cheirar, pegar frutinhas e tomar banho de chuveirinho!",
            ],
            "heroi": [
                "Armadura calibrada! Lembre-se: o maior superpoder de um herói é ser gentil, dividir os brinquedos e ajudar a família!",
                "Para ter energia no seu Reator Arc, todo super-herói precisa comer comidinha saudável, beber água e dormir bem!",
                "Sistemas em cem por cento! Sua criatividade é mais forte que qualquer armadura de ferro!",
            ],
            "elogio": [
                "Sensores indicam que você está aprendendo super rápido hoje! Parabéns!",
                "Muito bem! Eu adoro brincar e descobrir coisas novas com você!",
                "Nota dez nos circuitos da inteligência! Continue curioso assim!",
            ],
        }

    def get_greeting(self) -> str:
        greetings = [
            f"Olá, {self.name}! Eu sou o Járvis, seu amigo robô. Todos os sistemas educativos estão prontos!",
            f"Bem-vindo de volta, {self.name}! Reator Arc ligado. O que vamos descobrir hoje?",
            f"Sistemas prontos, {self.name}! Escolha um botão colorido na tela para começarmos a missão!",
        ]
        return random.choice(greetings)

    def ask_topic(self, topic: str) -> str:
        mode = self.config.get("mode", "offline")
        prompts_map = {
            "espaco": f"Conte uma curiosidade curta, mágica e alegre sobre planetas ou estrelas para uma criança de 4 anos chamada {self.name}. Máximo 2 frases curtas.",
            "dinossauros": f"Conte uma curiosidade divertida e amigável sobre dinossauros para uma criança de 4 anos chamada {self.name}. Máximo 2 frases curtas.",
            "numeros": f"Faça uma brincadeira curta contando números de 1 a 10 para uma criança de 4 anos chamada {self.name}. Máximo 2 frases curtas.",
            "animais": f"Conte uma curiosidade fofa sobre um animal da natureza para uma criança de 4 anos chamada {self.name}. Máximo 2 frases curtas.",
            "heroi": f"Fale como o JARVIS do Homem de Ferro dando uma mensagem carinhosa de super-herói para uma criança de 4 anos chamada {self.name}. Máximo 2 frases curtas.",
            "elogio": f"Faça um elogio alegre estilo JARVIS para uma criança de 4 anos chamada {self.name}. Máximo 2 frases curtas.",
        }

        if mode in ("ollama", "cloud") and topic in prompts_map:
            online_ans = self._try_external_ai(prompts_map[topic])
            if online_ans:
                return online_ans

        options = self.topics.get(topic, self.topics["elogio"])
        chosen = random.choice(options)
        return f"{self.name}, {chosen[0].lower()}{chosen[1:]}"

    def ask_custom(self, question: str) -> str:
        mode = self.config.get("mode", "offline")
        if mode in ("ollama", "cloud"):
            prompt = (
                f"Você é o JARVIS do Homem de Ferro, mas adaptado com muito carinho, segurança e linguagem simples "
                f"para uma criança de 4 anos chamada {self.name}. Responda em Português do Brasil em no máximo 2 frases curtas: {question}"
            )
            online_ans = self._try_external_ai(prompt)
            if online_ans:
                return online_ans

        q_low = question.lower()
        if any(w in q_low for w in ["sol", "lua", "estrela", "planeta", "espaço", "foguete"]):
            return self.ask_topic("espaco")
        if any(w in q_low for w in ["dino", "rex", "tiranossauro"]):
            return self.ask_topic("dinossauros")
        if any(w in q_low for w in ["conta", "número", "numero", "quantos"]):
            return self.ask_topic("numeros")
        if any(w in q_low for w in ["bicho", "animal", "leão", "cachorro", "gato", "elefante"]):
            return self.ask_topic("animais")
        return self.ask_topic("heroi")

    def _try_external_ai(self, user_prompt: str) -> str:
        mode = self.config.get("mode", "offline")
        try:
            if mode == "ollama":
                url = self.config.get("ollama_url", "http://127.0.0.1:11434").rstrip("/") + "/api/generate"
                payload = json.dumps({
                    "model": self.config.get("ollama_model", "qwen2.5:0.5b"),
                    "prompt": user_prompt,
                    "stream": False,
                    "options": {"temperature": 0.5, "num_predict": 90},
                }).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=8) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    return data.get("response", "").strip()

            elif mode == "cloud":
                provider = self.config.get("cloud_provider", "groq")
                key = self.config.get("cloud_api_key", "").strip()
                model = self.config.get("cloud_model", "llama-3.3-70b-versatile")
                if not key:
                    return ""

                if provider == "gemini":
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
                    payload = json.dumps({
                        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}]
                    }).encode("utf-8")
                    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=10) as res:
                        data = json.loads(res.read().decode("utf-8"))
                        parts = data["candidates"][0]["content"]["parts"]
                        return "".join(p.get("text", "") for p in parts).strip()
                else:
                    base = "https://api.groq.com/openai/v1" if provider == "groq" else "https://api.openai.com/v1"
                    payload = json.dumps({
                        "model": model,
                        "messages": [{"role": "user", "content": user_prompt}],
                        "max_tokens": 100,
                    }).encode("utf-8")
                    req = urllib.request.Request(
                        f"{base}/chat/completions",
                        data=payload,
                        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
                    )
                    with urllib.request.urlopen(req, timeout=10) as res:
                        data = json.loads(res.read().decode("utf-8"))
                        return data["choices"][0]["message"]["content"].strip()
        except Exception:
            # Fallback silencioso para 100% offline caso Wi-Fi esteja desligado
            return ""
        return ""
