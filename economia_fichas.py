"""
Módulo de Economia de Fichas (Token Economy) & Pote do Tesouro Real para o Kaleu.
Gerencia moedas, estrelas, histórico paginado (com gerador yield) e resgate de privilégios reais.
"""

from typing import Any, Dict, Generator, List, Optional
from banco_dados import db


class TokenEconomyManager:
    """Gerencia a economia de fichas e recompensas do mundo real e virtual."""

    def __init__(self, database=db):
        self.db = database

    def obter_status_pote(self) -> Dict[str, Any]:
        """Retorna saldo de fichas, total acumulado e estrelas."""
        res = self.db.consultar_um("SELECT saldo, total_acumulado, estrelas FROM pote_fichas WHERE id = 1;")
        if res:
            return {
                "saldo": int(res["saldo"]),
                "total_acumulado": int(res["total_acumulado"]),
                "estrelas": int(res["estrelas"]),
            }
        return {"saldo": 0, "total_acumulado": 0, "estrelas": 0}

    def pode_creditar_categoria(self, categoria: str, limite_diario: int = 4) -> bool:
        """Verifica se a categoria atingiu o limite diário de recompensas para valorizar as conquistas."""
        cat_norm = categoria.upper()
        if cat_norm in ("MISSAO", "LEITURA", "LOJA", "CONQUISTA"):
            return True
        try:
            sql = """
                SELECT COUNT(*) as total FROM transacoes_fichas
                WHERE tipo = 'GANHO' AND categoria = ? AND date(data_hora) = date('now', 'localtime');
            """
            row = self.db.consultar_um(sql, (cat_norm,))
            if row and int(row.get("total", 0)) >= limite_diario:
                return False
        except Exception:
            pass
        return True

    def creditar_fichas(self, quantidade: int, motivo: str, categoria: str = "ROTINA") -> Dict[str, Any]:
        """Credita fichas na conta do Kaleu com limite pedagógico para controle de dopamina."""
        if quantidade <= 0:
            return self.obter_status_pote()

        cat = categoria.upper()
        # Limites diários pedagógicos: previne spam de cliques e estimula esforço real
        limites = {
            "ALIMENTO": 3,
            "ROTINA": 4,
            "PET": 3,
            "JOGO": 8,
        }
        if cat in limites and not self.pode_creditar_categoria(cat, limites[cat]):
            return self.obter_status_pote()

        # Atualiza saldo e total acumulado
        self.db.executar_escrita(
            """
            UPDATE pote_fichas
            SET saldo = saldo + ?, total_acumulado = total_acumulado + ?, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = 1;
            """,
            (quantidade, quantidade),
        )

        # Registra transação no histórico
        self.db.executar_escrita(
            """
            INSERT INTO transacoes_fichas (quantidade, tipo, categoria, descricao)
            VALUES (?, 'GANHO', ?, ?);
            """,
            (quantidade, cat, motivo),
        )

        return self.obter_status_pote()

    def creditar_estrela(self, quantidade: int = 1) -> int:
        """Adiciona estrelas Stark por conquistas cognitivas/leitura."""
        self.db.executar_escrita(
            "UPDATE pote_fichas SET estrelas = estrelas + ? WHERE id = 1;",
            (quantidade,),
        )
        status = self.obter_status_pote()
        return status["estrelas"]

    def debitar_fichas(self, quantidade: int, motivo: str) -> bool:
        """Debita fichas caso o saldo seja suficiente."""
        status = self.obter_status_pote()
        if status["saldo"] < quantidade:
            return False

        self.db.executar_escrita(
            """
            UPDATE pote_fichas
            SET saldo = saldo - ?, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = 1;
            """,
            (quantidade,),
        )

        self.db.executar_escrita(
            """
            INSERT INTO transacoes_fichas (quantidade, tipo, categoria, descricao)
            VALUES (?, 'RESGATE', 'LOJA', ?);
            """,
            (quantidade, motivo),
        )
        return True

    def listar_recompensas_loja(self) -> List[Dict[str, Any]]:
        """Retorna todos os itens disponíveis na Loja do Tesouro Real."""
        return self.db.consultar_todos(
            "SELECT id, titulo, descricao, custo_fichas, tipo, icone, vezes_resgatado FROM recompensas_loja WHERE disponivel = 1 ORDER BY custo_fichas ASC;"
        )

    def resgatar_recompensa(self, item_id: str) -> Dict[str, Any]:
        """Resgata uma recompensa real ou virtual gastando fichas do pote."""
        item = self.db.consultar_um(
            "SELECT id, titulo, custo_fichas, tipo, icone FROM recompensas_loja WHERE id = ? AND disponivel = 1;",
            (item_id,),
        )
        if not item:
            return {"sucesso": False, "mensagem": "Item de recompensa não encontrado."}

        custo = int(item["custo_fichas"])
        if not self.debitar_fichas(custo, f"Resgate: {item['titulo']}"):
            return {
                "sucesso": False,
                "mensagem": f"Fichas insuficientes! Você precisa de {custo} moedas no Pote do Tesouro.",
            }

        self.db.executar_escrita(
            "UPDATE recompensas_loja SET vezes_resgatado = vezes_resgatado + 1 WHERE id = ?;",
            (item_id,),
        )

        novo_status = self.obter_status_pote()
        return {
            "sucesso": True,
            "mensagem": f"Parabéns, Kaleu! Você resgatou '{item['titulo']}'!",
            "item": dict(item),
            "saldo_restante": novo_status["saldo"],
        }

    def listar_historico_paginado(self, limite: int = 10, pagina: int = 0) -> List[Dict[str, Any]]:
        """
        Retorna transações com paginação estrita.
        Consome via gerador para evitar qualquer acúmulo desnecessário de objetos na memória RAM.
        """
        offset = pagina * limite
        sql = "SELECT id, quantidade, tipo, categoria, descricao, data_hora FROM transacoes_fichas ORDER BY id DESC"
        gerador = self.db.consultar_gerador(sql, limit=limite, offset=offset)
        return list(gerador)


# Instância singleton da Economia de Fichas
token_mgr = TokenEconomyManager()
