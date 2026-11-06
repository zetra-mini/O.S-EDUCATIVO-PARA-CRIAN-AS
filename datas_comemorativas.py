"""
Módulo de Datas Comemorativas Dinâmicas do Brasil e do Mundo.
Apresenta o calendário como uma jornada de descobertas e novidades:
- Compara a data do sistema com a tabela local do SQLite.
- Customiza o mascote com acessórios temáticos (chapéu junino, gotinha, capacete espacial).
- Dispara missões comemorativas especiais com moedas bônus no Pote do Tesouro.
"""

import datetime
from typing import Any, Dict, Optional
from banco_dados import db
from economia_fichas import token_mgr


class CalendarEventsManager:
    """Gerencia eventos comemorativos e temas sazonais."""

    def __init__(self, database=db):
        self.db = database

    def obter_evento_hoje(self) -> Optional[Dict[str, Any]]:
        """Verifica se a data atual possui evento comemorativo cadastrado."""
        hoje = datetime.date.today()
        dia, mes, ano = hoje.day, hoje.month, hoje.year

        evento = self.db.consultar_um(
            """
            SELECT id, dia, mes, titulo, categoria, mensagem_jarvis, acessorio_mascote, desafio_tipo, recompensa_fichas, ano_conclusao
            FROM datas_calendario
            WHERE dia = ? AND mes = ?;
            """,
            (dia, mes),
        )

        if evento:
            evento_dict = dict(evento)
            evento_dict["concluido_ano"] = (evento["ano_conclusao"] == ano)
            return evento_dict
        return None

    def concluir_missao_calendario(self, evento_id: int) -> Dict[str, Any]:
        """Conclui a missão festiva do dia e credita moedas bônus."""
        ano = datetime.date.today().year
        evento = self.db.consultar_um(
            "SELECT id, titulo, recompensa_fichas FROM datas_calendario WHERE id = ?;",
            (evento_id,),
        )
        if not evento:
            return {"sucesso": False, "mensagem": "Evento não encontrado."}

        fichas = int(evento["recompensa_fichas"])

        self.db.executar_escrita(
            "UPDATE datas_calendario SET ano_conclusao = ? WHERE id = ?;",
            (ano, evento_id),
        )

        token_mgr.creditar_fichas(fichas, f"Data Comemorativa: {evento['titulo']}", "MISSAO")
        token_mgr.creditar_estrela(1)

        return {
            "sucesso": True,
            "mensagem": f"🎉 Sensacional, Kaleu! Você celebrou '{evento['titulo']}' com maestria! (+{fichas} Moedas e +1 Estrela)",
            "fichas_ganhas": fichas,
            "saldo": token_mgr.obter_status_pote()["saldo"],
        }


# Instância global
calendar_mgr = CalendarEventsManager()
