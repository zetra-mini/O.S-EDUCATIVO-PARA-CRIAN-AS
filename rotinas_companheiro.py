"""
Módulo Companheiro B-bot & Rotinas Diárias Gamificadas com Protocolo Anti-Conflito.
Projetado para desarmar conflitos e disputas de poder através da psicologia infantil:
1. Missões cooperativas (Dente Brilhante 2 min, Operação Quarto Limpo 3-5 min).
2. Escolhas dirigidas (autonomia com limites).
3. Aviso prévio de transição (Regra dos 5 minutos).
4. Validação emocional da frustração infantil.
5. Crédito instantâneo de fichas no Pote do Tesouro.
"""

import datetime
from typing import Any, Dict, List, Optional
from banco_dados import db
from economia_fichas import token_mgr
from jarvis_pet_status import pet_mgr


class CompanionRoutinesManager:
    """Gerencia missões diárias, agenda e protocolo anti-conflito."""

    def __init__(self, database=db):
        self.db = database

    def listar_rotinas(self) -> List[Dict[str, Any]]:
        """Lista todas as rotinas ativas cadastradas."""
        hoje = datetime.date.today().isoformat()
        return self.db.consultar_todos(
            """
            SELECT id, titulo, horario, aviso_previo_minutos, tipo_acao, icone,
                   pergunta_escolha, recompensa_fichas, ativo,
                   CASE WHEN data_conclusao = ? THEN 1 ELSE 0 END AS concluida_hoje
            FROM agenda_rotina_diaria
            WHERE ativo = 1
            ORDER BY horario ASC;
            """,
            (hoje,),
        )

    def concluir_rotina(self, rotina_id: str) -> Dict[str, Any]:
        """Valida e conclui uma missão da rotina, creditando moedas e subindo barras do mascote."""
        hoje = datetime.date.today().isoformat()
        rotina = self.db.consultar_um(
            "SELECT id, titulo, recompensa_fichas, icone FROM agenda_rotina_diaria WHERE id = ?;",
            (rotina_id,),
        )
        if not rotina:
            return {"sucesso": False, "mensagem": "Missão não encontrada."}

        fichas = int(rotina["recompensa_fichas"])

        # Marca como concluída hoje
        self.db.executar_escrita(
            "UPDATE agenda_rotina_diaria SET concluida_hoje = 1, data_conclusao = ? WHERE id = ?;",
            (hoje, rotina_id),
        )

        # Credita fichas no Pote do Tesouro
        token_mgr.creditar_fichas(fichas, f"Missão Cumprida: {rotina['titulo']}", "ROTINA")

        # Se for missão de escovar dente ou banho, melhora higiene do mascote
        if "dente" in rotina_id.lower() or "banho" in rotina_id.lower():
            pet_mgr.dar_banho()
        elif "almoço" in rotina_id.lower():
            pet_mgr.alimentar(30, "Almoço do Herói", 0)

        return {
            "sucesso": True,
            "mensagem": f"🌟 Parabéns, Campeão! Missão '{rotina['titulo']}' cumprida com sucesso! (+{fichas} Moedas no Pote!)",
            "fichas_ganhas": fichas,
            "status_pote": token_mgr.obter_status_pote(),
            "status_pet": pet_mgr.obter_status(),
        }

    def gerar_desafio_anti_conflito(self, motivo: str = "guardar_brinquedos") -> Dict[str, Any]:
        """
        Retorna diálogo estruturado em 3 fases para desarmar conflito infantil:
        1. Validação empática.
        2. Escolha dirigida (duas opções viáveis).
        3. Gamificação com cronômetro cooperativo.
        """
        if motivo == "guardar_brinquedos":
            return {
                "titulo": "Operação Quarto Limpo & Resgate de Herói",
                "validacao_emocional": "Eu sei, Campeão, parar de brincar quando a diversão tá boa é chato mesmo! Mas sabe de uma coisa? Os heróis guardam suas ferramentas para achá-las no próximo treino!",
                "escolha_dirigida": {
                    "pergunta": "Como vamos começar nossa operação?",
                    "opcoes": [
                        {"id": "carrinhos", "label": "🏎️ Guardar os carrinhos voando como um avião!"},
                        {"id": "blocos", "label": "🧱 Guardar os blocos usando a garra de um guindaste gigante!"},
                    ],
                },
                "tempo_segundos": 180,  # 3 minutos
                "recompensa": 10,
            }
        elif motivo == "escovar_dentes":
            return {
                "titulo": "Missão Dente Brilhante Stark",
                "validacao_emocional": "Seus dentes trabalharam bastante hoje mastigando tantas comidinhas gostosas! Hora de dar um banho de espuma neles!",
                "escolha_dirigida": {
                    "pergunta": "Por onde a escova supersônica vai começar?",
                    "opcoes": [
                        {"id": "dentes_cima", "label": "🦷 Começar nos dentes lá de cima em círculos!"},
                        {"id": "dentes_baixo", "label": "✨ Começar nos dentes lá de baixo como um trenzinho!"},
                    ],
                },
                "tempo_segundos": 120,  # 2 minutos
                "recompensa": 5,
            }
        else:
            return {
                "titulo": "Respiração da Florzinha & Reator da Calma",
                "validacao_emocional": "Todo herói sente o coração acelerar ou fica bravo às vezes. Vamos acalmar o corpo juntos?",
                "escolha_dirigida": {
                    "pergunta": "O que você quer fazer agora?",
                    "opcoes": [
                        {"id": "florzinha", "label": "🌸 Cheirar a florzinha e soprar a velinha devagar"},
                        {"id": "abraco", "label": "🫂 Pedir um abraço bem quentinho do papai"},
                    ],
                },
                "tempo_segundos": 60,
                "recompensa": 5,
            }

    def cadastrar_rotina(
        self,
        id_rotina: str,
        titulo: str,
        horario: str,
        aviso_minutos: int = 5,
        tipo_acao: str = "escolha_dirigida",
        icone: str = "⭐",
        pergunta: str = "",
        recompensa: int = 5,
    ) -> bool:
        """Permite que os pais adicionem ou alterem rotinas facilmente pelo painel."""
        self.db.executar_escrita(
            """
            INSERT OR REPLACE INTO agenda_rotina_diaria
            (id, titulo, horario, aviso_previo_minutos, tipo_acao, icone, pergunta_escolha, recompensa_fichas, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1);
            """,
            (id_rotina, titulo, horario, aviso_minutos, tipo_acao, icone, pergunta, recompensa),
        )
        return True


# Instância global de rotinas
routines_mgr = CompanionRoutinesManager()
