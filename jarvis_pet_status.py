"""
Módulo do Mascote Virtual (Pou / B-bot Jarvis) para o Kaleu.
Porta a lógica matemática de necessidades do repositório POUPY para a API assíncrona Web:
- 4 Barras de estado (0 a 100%): Higiene, Alimentação, Diversão e Energia.
- Decaimento suave com o tempo.
- Expressões visuais baseadas no estado das barras.
- Mecânica do Abajur (Hora de Dormir) para controle carinhoso de sono e transição sem atrito.
- Carinho ao clicar/segurar.
- Persistência no SQLite em modo WAL.
"""

import time
from typing import Any, Dict
from banco_dados import db
from economia_fichas import token_mgr


class JarvisPetManager:
    """Gerenciador do estado do bichinho virtual do Jarvis."""

    # Taxa de decaimento por minuto para cada necessidade
    DECAY_RATE_PER_MINUTE = 0.45  # ~5 pontos a cada ~11 minutos

    def __init__(self, database=db):
        self.db = database

    def obter_status(self) -> Dict[str, Any]:
        """Calcula decaimento de necessidades pelo tempo decorrido e retorna o estado atual."""
        row = self.db.consultar_um(
            "SELECT higiene, alimentacao, diversao, energia, felicidade, estado_animacao, acessorio_atual, modo_dormir, ultimo_decaimento FROM bixinho_status WHERE id = 1;"
        )
        if not row:
            return {
                "higiene": 100.0,
                "alimentacao": 100.0,
                "diversao": 100.0,
                "energia": 100.0,
                "felicidade": 100.0,
                "humor": "FELIZ",
                "modo_dormir": False,
                "acessorio": None,
            }

        now = time.time()
        ultimo = float(row["ultimo_decaimento"] or 0)
        higiene = float(row["higiene"])
        alimentacao = float(row["alimentacao"])
        diversao = float(row["diversao"])
        energia = float(row["energia"])
        modo_dormir = bool(row["modo_dormir"])

        # Se passou tempo significativo desde o último decaimento (mínimo 10 segundos)
        if ultimo > 0 and (now - ultimo) >= 10:
            minutos = (now - ultimo) / 60.0
            decaimento = minutos * self.DECAY_RATE_PER_MINUTE

            # Se não estiver dormindo, decai normalmente
            if not modo_dormir:
                higiene = max(10.0, higiene - decaimento)
                alimentacao = max(10.0, alimentacao - decaimento)
                diversao = max(10.0, diversao - decaimento)
                energia = max(10.0, energia - (decaimento * 0.8))
            else:
                # Quando dorme, regenera energia e decaimento de fome é bem menor
                energia = min(100.0, energia + (minutos * 2.0))
                alimentacao = max(10.0, alimentacao - (decaimento * 0.2))

            felicidade = (higiene + alimentacao + diversao + energia) / 4.0

            # Salva atualização suave no SQLite Single-Writer
            self.db.executar_escrita(
                """
                UPDATE bixinho_status
                SET higiene = ?, alimentacao = ?, diversao = ?, energia = ?, felicidade = ?, ultimo_decaimento = ?, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = 1;
                """,
                (round(higiene, 1), round(alimentacao, 1), round(diversao, 1), round(energia, 1), round(felicidade, 1), now),
            )
        elif ultimo == 0:
            # Inicializa timestamp de decaimento
            self.db.executar_escrita(
                "UPDATE bixinho_status SET ultimo_decaimento = ? WHERE id = 1;",
                (now,),
            )

        felicidade = (higiene + alimentacao + diversao + energia) / 4.0

        # Determina o humor e carência do mascote
        humor = "FELIZ"
        if modo_dormir or energia < 30.0:
            humor = "SONOLENTO"
        elif higiene < 35.0:
            humor = "SUJINHO"
        elif alimentacao < 35.0:
            humor = "COM_FOME"
        elif diversao < 35.0:
            humor = "ENTEDIADO"
        elif felicidade < 60.0:
            humor = "CARENTE"

        return {
            "higiene": round(higiene, 1),
            "alimentacao": round(alimentacao, 1),
            "diversao": round(diversao, 1),
            "energia": round(energia, 1),
            "felicidade": round(felicidade, 1),
            "humor": humor,
            "modo_dormir": modo_dormir,
            "acessorio": row["acessorio_atual"],
        }

    def dar_banho(self) -> Dict[str, Any]:
        """Restaura higiene para 100%, dá moedas para o pote e comemora."""
        self.db.executar_escrita(
            """
            UPDATE bixinho_status
            SET higiene = 100.0, ultimo_decaimento = ?
            WHERE id = 1;
            """,
            (time.time(),),
        )
        token_mgr.creditar_fichas(5, "Banho Limpinho no Jarvis", "ROTINA")
        return {
            "sucesso": True,
            "mensagem": "🧼 Circuito limpo e reluzente! A armadura do Jarvis está brilhando como nova!",
            "status": self.obter_status(),
        }

    def alimentar(self, pontos: int = 25, nome_alimento: str = "Fruta Saudável", moedas: int = 5) -> Dict[str, Any]:
        """Alimenta o pet, restaurando alimentação e concedendo recompensas."""
        current = self.obter_status()
        nova_alim = min(100.0, current["alimentacao"] + pontos)

        self.db.executar_escrita(
            """
            UPDATE bixinho_status
            SET alimentacao = ?, ultimo_decaimento = ?
            WHERE id = 1;
            """,
            (nova_alim, time.time()),
        )
        if moedas > 0:
            token_mgr.creditar_fichas(moedas, f"Alimentou o Jarvis com {nome_alimento}", "ALIMENTO")

        return {
            "sucesso": True,
            "mensagem": f"🍎 Nhac! Uma delícia de {nome_alimento}! Bateria recarregada e reator brilhando!",
            "status": self.obter_status(),
        }

    def brincar(self, pontos: int = 20, jogo_nome: str = "Desafio Educativo") -> Dict[str, Any]:
        """Aumenta diversão ao concluir jogos educativos."""
        current = self.obter_status()
        nova_div = min(100.0, current["diversao"] + pontos)

        self.db.executar_escrita(
            """
            UPDATE bixinho_status
            SET diversao = ?, ultimo_decaimento = ?
            WHERE id = 1;
            """,
            (nova_div, time.time()),
        )
        token_mgr.creditar_fichas(5, f"Brincou no jogo: {jogo_nome}", "JOGO")
        return {
            "sucesso": True,
            "mensagem": f"🎮 Bip-bip! Que divertido brincar de {jogo_nome} com você, Kaleu!",
            "status": self.obter_status(),
        }

    def fazer_carinho(self) -> Dict[str, Any]:
        """Dispara reação de afeto e coração no mascote."""
        current = self.obter_status()
        nova_div = min(100.0, current["diversao"] + 6.0)
        self.db.executar_escrita(
            "UPDATE bixinho_status SET diversao = ? WHERE id = 1;",
            (nova_div,),
        )
        return {
            "sucesso": True,
            "mensagem": "💙 O Jarvis adora o seu carinho, Kaleu! Reator Arc brilhando forte e feliz!",
            "status": self.obter_status(),
        }

    def alternar_abajur(self) -> Dict[str, Any]:
        """Mecânica do Abajur do Sono (Hora de Dormir)."""
        current = self.obter_status()
        novo_dormir = not current["modo_dormir"]

        self.db.executar_escrita(
            """
            UPDATE bixinho_status
            SET modo_dormir = ?, ultimo_decaimento = ?
            WHERE id = 1;
            """,
            (1 if novo_dormir else 0, time.time()),
        )

        msg = (
            "🌙 *Click!* Luzes apagadas. O Jarvis entrou em modo de recarga e descanso... Bons sonhos, Kaleu!"
            if novo_dormir
            else "☀️ *Click!* Sistemas online! Bom dia, Kaleu! O Jarvis acordou pronto para aprender e brincar!"
        )
        return {
            "sucesso": True,
            "modo_dormir": novo_dormir,
            "mensagem": msg,
            "status": self.obter_status(),
        }


# Instância global do Mascote
pet_mgr = JarvisPetManager()
