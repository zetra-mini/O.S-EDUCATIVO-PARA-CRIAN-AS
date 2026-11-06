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
    ("ALFABETO", "Qual a primeira letra da palavra BOLA?", "B", ["B", "L", "A", "O"]),
    ("ALFABETO", "Qual a primeira letra da palavra CASA?", "C", ["C", "S", "M", "A"]),
    ("ALFABETO", "Qual a letrinha que faz o som /a/ de AVIÃO?", "A", ["A", "E", "I", "U"]),
    ("ALFABETO", "Qual a letra do herói DINOSSAURO?", "D", ["D", "P", "T", "B"]),
    ("NUMEROS", "Quantas mãos você tem para abraçar a família?", "2", ["1", "2", "3", "5"]),
    ("NUMEROS", "Quantas patinhas tem o gatinho ou o cachorrinho?", "4", ["2", "3", "4", "6"]),
    ("NUMEROS", "Quantos dedos você tem em uma mãozinha?", "5", ["3", "4", "5", "10"]),
    ("ANIMAIS", "Quem é o gigante pescoçudo que come as folhinhas do topo das árvores?", "Girafa", ["Girafa", "Leão", "Pinguim", "Sapo"]),
    ("ANIMAIS", "Quem gosta de rugir bem alto e é o rei da selva?", "Leão", ["Leão", "Coelho", "Tartaruga", "Formiga"]),
    ("CURIOSIDADES", "O que o Sol faz no céu durante o dia?", "Ilumina e aquece a Terra", ["Ilumina e aquece a Terra", "Faz chover gelo", "Fica invisível", "Dorme o dia todo"]),
]


class CognitionGamesManager:
    """Gerencia jogos de cognição, controle inibitório e repetição espaçada."""

    def __init__(self, database=db):
        self.db = database
        self._popular_cards_se_vazio()

    def _popular_cards_se_vazio(self):
        row = self.db.consultar_um("SELECT COUNT(*) AS total FROM cognicao_leitner;")
        if not row or row["total"] == 0:
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
            token_mgr.creditar_fichas(3, "Controle Inibitório (Desafio do Semáforo)", "JOGO")
            pet_mgr.brincar(10, "Semáforo Stark")
            return {
                "sucesso": True,
                "mensagem": "⚡ Excelente reflexo e paciência, Kaleu! Você sabe a hora certa de agir!",
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
            token_mgr.creditar_fichas(5, f"Acerto no Baú do Conhecimento (Caixa {nova_caixa})", "JOGO")
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


# Instância global
cognition_mgr = CognitionGamesManager()
