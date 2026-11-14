"""
Módulo de Funções Executivas, Memória e Repetição Espaçada de Leitner.
1. Desafio do Semáforo (Controle Inibitório / Parar e Pensar):
   - Estímulo visual verde (agir) vs vermelho (inibir ação).
   - Treino de paciência e controle de impulsos.
2. Baú do Conhecimento (Repetição Espaçada de Leitner):
   - 3 caixas de memorização progressivas.
   - Acertos avançam de caixa; erros retornam à caixa 1 sem mensagens punitivas.
   - Teoria da Autodeterminação (SDT) e proteção da motivação intrínseca.
"""

import json
import random
from typing import Any, Dict, List, Optional
from banco_dados import db
from economia_fichas import token_mgr
from jarvis_pet_status import pet_mgr


CARDS_INICIAIS = [
    ("ANIMAIS", "Quem é o rei da selva e dá um rugido bem forte?", "🦁 Leão", ["🦁 Leão", "🐶 Cachorrinho", "🐱 Gatinho", "🦆 Patinho"]),
    ("ANIMAIS", "Quem gosta de abanar o rabinho e faz Au-Au?", "🐶 Cachorrinho", ["🐶 Cachorrinho", "🐸 Sapinho", "🐮 Vaquinha", "🐷 Porquinho"]),
    ("ANIMAIS", "Quem dá o leitinho gostoso para o nosso lanche?", "🐮 Vaquinha", ["🐮 Vaquinha", "🦁 Leão", "🐵 Macaquinho", "🐰 Coelhinho"]),
    ("ANIMAIS", "Quem diz Quac-Quac e adora nadar na lagoa?", "🦆 Patinho", ["🦆 Patinho", "🐱 Gatinho", "🐻 Ursinho", "🐴 Cavalinho"]),
    ("ANIMAIS", "Quem diz Miau e adora brincar com novelo de lã?", "🐱 Gatinho", ["🐱 Gatinho", "🐶 Cachorrinho", "🐸 Sapinho", "🦁 Leão"]),
    ("FRUTAS", "Qual é a frutinha vermelha bem crocante e docinha?", "🍎 Maçã", ["🍎 Maçã", "🍌 Banana", "🍇 Uva", "🍊 Laranja"]),
    ("FRUTAS", "Qual fruta amarela o macaquinho mais adora comer?", "🍌 Banana", ["🍌 Banana", "🍎 Maçã", "🍓 Morango", "🍉 Melancia"]),
    ("FRUTAS", "Qual é a fruta vermelhinha com pintinhas que é uma delícia?", "🍓 Morango", ["🍓 Morango", "🍇 Uva", "🍍 Abacaxi", "🍋 Limão"]),
    ("TRANSPORTE", "Qual meio de transporte voa lá no alto entre as nuvens?", "✈️ Avião", ["✈️ Avião", "🚗 Carro", "⛵ Barco", "🚲 Bicicleta"]),
    ("TRANSPORTE", "Qual transporte anda sobre os trilhos fazendo Piwi-Tchutchu?", "🚂 Trem", ["🚂 Trem", "🚀 Foguete", "🚗 Carro", "⛵ Barco"]),
    ("TRANSPORTE", "Qual vai lá no espaço sideral até a Lua?", "🚀 Foguete", ["🚀 Foguete", "🚲 Bicicleta", "🚌 Ônibus", "🚗 Carro"]),
    ("NATUREZA", "Quem brilha lá no céu de dia para esquentar o nosso dia?", "☀️ Sol", ["☀️ Sol", "🌙 Lua", "⭐ Estrela", "🌧️ Chuva"]),
    ("NATUREZA", "Quem aparece no céu de noite para iluminar nossos sonhos?", "🌙 Lua", ["🌙 Lua", "☀️ Sol", "🌈 Arco-íris", "⚡ Raio"]),
    ("NUMEROS", "Quantas mãos você tem para abraçar a família?", "2️⃣ Duas Mãos", ["2️⃣ Duas Mãos", "1️⃣ Uma Mão", "4️⃣ Quatro Mãos", "5️⃣ Cinco Mãos"]),
    ("NUMEROS", "Quantas patinhas tem o cachorrinho ou o gatinho?", "4️⃣ Quatro Patas", ["4️⃣ Quatro Patas", "2️⃣ Duas Patas", "3️⃣ Três Patas", "6️⃣ Seis Patas"]),
    ("NUMEROS", "Quantos dedinhos você tem em uma mãozinha?", "5️⃣ Cinco Dedos", ["5️⃣ Cinco Dedos", "3️⃣ Três Dedos", "2️⃣ Dois Dedos", "🔟 Dez Dedos"]),
    ("LETRAS", "Qual a primeira letra da palavra BOLA?", "⚽ Letra B", ["⚽ Letra B", "🚗 Letra C", "🍎 Letra A", "🌙 Letra M"]),
    ("LETRAS", "Qual a letrinha que começa o nome do assistente JARVIS?", "🤖 Letra J", ["🤖 Letra J", "⚽ Letra B", "☀️ Letra S", "🚀 Letra R"]),
    ("LETRAS", "Qual a letrinha mágica de AVIÃO e AMIGO?", "✈️ Letra A", ["✈️ Letra A", "🦆 Letra P", "🐱 Letra G", "⭐ Letra E"]),
]


class CognitionGamesManager:
    """Gerencia jogos de cognição, controle inibitório e repetição espaçada."""

    def __init__(self, database=db):
        self.db = database
        self._popular_cards_se_vazio()

    def _popular_cards_se_vazio(self):
        row = self.db.consultar_um("SELECT COUNT(*) AS total FROM cognicao_leitner;")
        # Se vazio ou se tem cards antigos sem emojis, limpa e popula com os novos cards ilustrados
        precisa_recriar = False
        if not row or row["total"] == 0:
            precisa_recriar = True
        else:
            amostra = self.db.consultar_um("SELECT resposta_correta FROM cognicao_leitner LIMIT 1;")
            if amostra and "🦁" not in amostra["resposta_correta"] and "🍎" not in amostra["resposta_correta"] and "2️⃣" not in amostra["resposta_correta"]:
                precisa_recriar = True

        if precisa_recriar:
            self.db.executar_escrita("DELETE FROM cognicao_leitner;")
            for cat, perg, resp, opc in CARDS_INICIAIS:
                self.db.executar_escrita(
                    """
                    INSERT INTO cognicao_leitner (categoria, pergunta, resposta_correta, opcoes_json, caixa, acertos, erros)
                    VALUES (?, ?, ?, ?, 1, 0, 0);
                    """,
                    (cat, perg, resp, json.dumps(opc, ensure_ascii=False)),
                )

    def obter_desafio_semaforo(self) -> Dict[str, Any]:
        """Gera rodada do jogo do semáforo com controle inibitório."""
        eh_verde = random.random() < 0.65  # 65% verde, 35% vermelho
        return {
            "sinal": "VERDE" if eh_verde else "VERMELHO",
            "cor_hex": "#10b981" if eh_verde else "#ef4444",
            "instrucao": "🟢 TOQUE RÁPIDO NO VERDE!" if eh_verde else "🔴 PAROU! NÃO TOQUE NO VERMELHO!",
            "acao_esperada": "CLICAR" if eh_verde else "ESPERAR",
            "tempo_limite_ms": 1600,
        }

    def registrar_resultado_semaforo(self, acertou: bool) -> Dict[str, Any]:
        """Registra pontuação do semáforo de forma construtiva."""
        if acertou:
            token_mgr.creditar_fichas(1, "Controle Inibitório (Desafio do Semáforo)", "JOGO")
            pet_mgr.brincar(10, "Semáforo Stark")
            return {
                "sucesso": True,
                "mensagem": "⚡ Excelente reflexo e paciência, Campeão! Você sabe a hora certa de agir!",
                "fichas_ganhas": 3,
                "saldo": token_mgr.obter_status_pote()["saldo"],
            }
        else:
            return {
                "sucesso": False,
                "mensagem": "Quase lá! Treinar a paciência é como respirar fundo antes de pular. Vamos mais uma?",
                "fichas_ganhas": 0,
            }

    def sortear_card_leitner(self) -> Optional[Dict[str, Any]]:
        """Sorteia um flashcard do Baú do Conhecimento priorizando caixas iniciais."""
        # 60% chance de vir da caixa 1, 30% caixa 2, 10% caixa 3
        rand = random.random()
        caixa_alvo = 1 if rand < 0.60 else (2 if rand < 0.90 else 3)

        card = self.db.consultar_um(
            """
            SELECT id, categoria, pergunta, resposta_correta, opcoes_json, caixa, acertos, erros
            FROM cognicao_leitner
            WHERE caixa = ?
            ORDER BY RANDOM() LIMIT 1;
            """,
            (caixa_alvo,),
        )
        if not card:
            # Fallback para qualquer caixa
            card = self.db.consultar_um("SELECT id, categoria, pergunta, resposta_correta, opcoes_json, caixa FROM cognicao_leitner ORDER BY RANDOM() LIMIT 1;")

        if card:
            card_dict = dict(card)
            try:
                card_dict["opcoes"] = json.loads(card_dict["opcoes_json"])
            except Exception:
                card_dict["opcoes"] = []
            return card_dict
        return None

    def responder_card_leitner(self, card_id: int, resposta_usuario: str) -> Dict[str, Any]:
        """Avança o card de caixa se correto; se errado, retorna suavemente à caixa 1."""
        card = self.db.consultar_um(
            "SELECT id, resposta_correta, caixa FROM cognicao_leitner WHERE id = ?;",
            (card_id,),
        )
        if not card:
            return {"sucesso": False, "mensagem": "Cartão não encontrado."}

        correta = card["resposta_correta"].strip().lower()
        acertou = (resposta_usuario or "").strip().lower() == correta
        caixa_atual = int(card["caixa"])

        if acertou:
            nova_caixa = min(3, caixa_atual + 1)
            self.db.executar_escrita(
                """
                UPDATE cognicao_leitner
                SET caixa = ?, acertos = acertos + 1, ultima_revisao = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (nova_caixa, card_id),
            )
            token_mgr.creditar_fichas(2, f"Acerto no Baú do Conhecimento (Caixa {nova_caixa})", "JOGO")
            token_mgr.creditar_estrela(1)
            pet_mgr.brincar(12, "Baú de Conhecimento")
            return {
                "acertou": True,
                "mensagem": f"⭐ Resposta perfeita! O conhecimento avançou para a Caixa {nova_caixa}! (+5 Moedas e +1 Estrela)",
                "nova_caixa": nova_caixa,
                "saldo": token_mgr.obter_status_pote()["saldo"],
            }
        else:
            # Sem mensagens punitivas, apenas encorajamento
            self.db.executar_escrita(
                """
                UPDATE cognicao_leitner
                SET caixa = 1, erros = erros + 1, ultima_revisao = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (card_id,),
            )
            return {
                "acertou": False,
                "mensagem": f"Opa! A resposta certa era '{card['resposta_correta']}'. Logo vamos rever juntos para memorizar de vez!",
                "nova_caixa": 1,
            }

    # ==========================================================================
    # DESCOBRE O SOM (Gamificação & Sonoplastia)
    # ==========================================================================
    def obter_desafio_descobre_som(self) -> Dict[str, Any]:
        """
        Gera um desafio de 'Descobre o Som':
        1. Sorteia um animal com áudio gravado em sounds/animais/.
        2. Sorteia 2 opções distratoras de animais ou dinossauros.
        3. Retorna o áudio a tocar e 3 opções embaralhadas.
        """
        banco_sons = [
            {"id": "leao", "nome": "Leão", "emoji": "🦁", "som": "/static/sounds/animais/leao.mp3"},
            {"id": "elefante", "nome": "Elefante", "emoji": "🐘", "som": "/static/sounds/animais/elefante.mp3"},
            {"id": "sapo", "nome": "Sapo Cururu", "emoji": "🐸", "som": "/static/sounds/animais/sapo.mp3"},
            {"id": "cavalo", "nome": "Cavalo", "emoji": "🐴", "som": "/static/sounds/animais/cavalo.mp3"},
            {"id": "passaro", "nome": "Pássaro Cantador", "emoji": "🐦", "som": "/static/sounds/animais/passaro.mp3"},
            {"id": "arara", "nome": "Arara Azul", "emoji": "🦜", "som": "/static/sounds/animais/arara.mp3"},
            {"id": "mico", "nome": "Mico Leão", "emoji": "🐒", "som": "/static/sounds/animais/mico.mp3"},
            {"id": "onca", "nome": "Onça Pintada", "emoji": "🐆", "som": "/static/sounds/animais/onca.mp3"},
            {"id": "coruja", "nome": "Coruja Sábia", "emoji": "🦉", "som": "/static/sounds/animais/coruja.mp3"},
            {"id": "golfinho", "nome": "Golfinho", "emoji": "🐬", "som": "/static/sounds/animais/golfinho.mp3"},
            {"id": "jacare", "nome": "Jacaré", "emoji": "🐊", "som": "/static/sounds/animais/jacare.mp3"},
            {"id": "baleia", "nome": "Baleia Jubarte", "emoji": "🐋", "som": "/static/sounds/animais/baleia.mp3"},
            {"id": "cachorro", "nome": "Cachorrinho", "emoji": "🐶", "som": "/static/sounds/animais/cachorro.mp3"},
            {"id": "gato", "nome": "Gatinho", "emoji": "🐱", "som": "/static/sounds/animais/gato.mp3"},
            {"id": "vaca", "nome": "Vaquinha", "emoji": "🐮", "som": "/static/sounds/animais/vaca.mp3"},
            {"id": "pato", "nome": "Patinho", "emoji": "🦆", "som": "/static/sounds/animais/pato.mp3"},
            {"id": "urso", "nome": "Urso Pardo", "emoji": "🐻", "som": "/static/sounds/animais/urso.mp3"},
            {"id": "pinguim", "nome": "Pinguim", "emoji": "🐧", "som": "/static/sounds/animais/pinguim.mp3"},
        ]

        distratores_extras = [
            {"id": "dino_trex", "nome": "T-Rex Fóssil", "emoji": "🦖", "imagem": "/static/images/dinossauros/trex.webp"},
            {"id": "dino_triceratops", "nome": "Tricerátops", "emoji": "🦕", "imagem": "/static/images/dinossauros/triceratops.webp"},
            {"id": "dino_spinosaurus", "nome": "Espinossauro", "emoji": "🐊", "imagem": "/static/images/dinossauros/spinosaurus.webp"},
            {"id": "dino_stegosaurus", "nome": "Estegossauro", "emoji": "🛡️", "imagem": "/static/images/dinossauros/stegosaurus.webp"},
        ]

        alvo = random.choice(banco_sons)
        # Sorteia 2 distratores diferentes do alvo
        outros_animais = [a for a in banco_sons if a["id"] != alvo["id"]]
        piscina = outros_animais + distratores_extras
        distratores = random.sample(piscina, 2)

        opcoes = [
            {"id": alvo["id"], "nome": alvo["nome"], "emoji": alvo["emoji"], "imagem": alvo.get("imagem", "")},
            {"id": distratores[0]["id"], "nome": distratores[0]["nome"], "emoji": distratores[0]["emoji"], "imagem": distratores[0].get("imagem", "")},
            {"id": distratores[1]["id"], "nome": distratores[1]["nome"], "emoji": distratores[1]["emoji"], "imagem": distratores[1].get("imagem", "")},
        ]
        random.shuffle(opcoes)

        return {
            "alvo_id": alvo["id"],
            "alvo_nome": alvo["nome"],
            "audio_url": alvo["som"],
            "pergunta": "Quem faz esse som incrível da natureza? Ouça com atenção!",
            "opcoes": opcoes,
        }

    def validar_descobre_som(self, alvo_id: str, resposta_id: str) -> Dict[str, Any]:
        """
        Valida o palpite do minijogo. Acertos geram confetes na tela e moedas no SQLite (WAL).
        """
        alvo = str(alvo_id or "").strip().lower()
        resp = str(resposta_id or "").strip().lower()
        acertou = (alvo == resp) and bool(alvo)

        if acertou:
            token_mgr.creditar_fichas(2, "Acerto no Descobre o Som", "JOGO")
            token_mgr.creditar_estrela(1)
            pet_mgr.brincar(12, "Descobre o Som")
            return {
                "acertou": True,
                "confetes": True,
                "fichas_ganhas": 5,
                "saldo": token_mgr.obter_status_pote()["saldo"],
                "mensagem": "🎉 Maravilha, Campeão! Você tem um super ouvido de biólogo! Ganhou +5 Moedas e +1 Estrela!",
            }
        else:
            return {
                "acertou": False,
                "confetes": False,
                "fichas_ganhas": 0,
                "mensagem": "Quase lá, super-herói! Aperte para ouvir de novo e tente mais uma vez!",
            }



# Instância global
cognition_mgr = CognitionGamesManager()
