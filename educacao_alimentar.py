"""
Módulo de Educação Alimentar e Nutricional (EAN) Gamificada.
Ensina conceitos de nutrição saudável sem imposições rígidas:
1. Prato Colorido dos Superpoderes (Cenoura, Brócolis, Melancia, Feijão).
2. Semáforo dos Alimentos (Verde = Sempre, Amarelo = Moderação, Vermelho = Dias Especiais).
3. Conexão real com a alimentação do Campeão através do Painel dos Pais.
"""

from typing import Any, Dict, List
from banco_dados import db
from economia_fichas import token_mgr
from jarvis_pet_status import pet_mgr


class FoodEducationManager:
    """Gerencia catálogo de alimentos, pratos coloridos e hábitos alimentares."""

    def __init__(self, database=db):
        self.db = database

    def listar_alimentos(self) -> List[Dict[str, Any]]:
        """Retorna todos os alimentos cadastrados."""
        return self.db.consultar_todos(
            "SELECT id, nome, categoria, semaforo, superpoder, cor_grupo, icone, pontos_nutritivos FROM alimentos_nutricao ORDER BY semaforo ASC, nome ASC;"
        )

    def avaliar_prato(self, alimentos_ids: List[str]) -> Dict[str, Any]:
        """
        Avalia o prato montado pela criança:
        - Deve conter variedade de cores e priorizar alimentos do semáforo verde.
        - Se tiver 3 ou mais cores diferentes, ganha bônus de superpoderes!
        """
        if not alimentos_ids:
            return {"sucesso": False, "mensagem": "Escolha alimentos coloridos para montar o seu prato!"}

        placeholders = ",".join("?" for _ in alimentos_ids)
        itens = self.db.consultar_todos(
            f"SELECT id, nome, semaforo, superpoder, cor_grupo, icone, pontos_nutritivos FROM alimentos_nutricao WHERE id IN ({placeholders});",
            tuple(alimentos_ids),
        )

        cores = set(item["cor_grupo"] for item in itens)
        tem_vermelho_doce = any(item["semaforo"] == "vermelho" for item in itens)
        apenas_verdes = all(item["semaforo"] == "verde" for item in itens)

        # Atualiza a alimentação do bichinho
        pontos_totais = sum(item["pontos_nutritivos"] for item in itens)
        pet_mgr.alimentar(pontos_totais, "Prato Colorido", 0)

        # Regras de recompensa
        if len(cores) >= 3 and apenas_verdes:
            fichas = 1
            token_mgr.creditar_fichas(fichas, "Prato Colorido com 3+ Superpoderes", "ALIMENTO")
            token_mgr.creditar_estrela(1)
            msg = f"🌈 UAU, CAMPEÃO! Seu prato tem {len(cores)} cores diferentes e superpoderes puros! Seus músculos e coração estão blindados! (+3 Moedas e +1 Estrela!)"
            animacao = "fogos_2d"
        elif tem_vermelho_doce:
            fichas = 1
            token_mgr.creditar_fichas(fichas, "Refeição com doce (moderação)", "ALIMENTO")
            msg = "Doces são gostosos em dias especiais, mas comer muitas frutinhas e legumes deixa o corpo mais forte para correr!"
            animacao = "aviso_suave"
        else:
            fichas = 2
            token_mgr.creditar_fichas(fichas, "Prato Nutritivo", "ALIMENTO")
            msg = "Muito bem! Seu prato está bem gostoso e nutritivo! Que tal adicionar mais uma cor na próxima vez?"
            animacao = "estrelas"

        return {
            "sucesso": True,
            "mensagem": msg,
            "cores_distintas": list(cores),
            "animacao": animacao,
            "fichas_ganhas": fichas,
            "status_pet": pet_mgr.obter_status(),
            "status_pote": token_mgr.obter_status_pote(),
        }

    def validar_refeicao_real(self, tipo_refeicao: str) -> Dict[str, Any]:
        """Acionado pelos pais no celular quando a criança come no mundo real."""
        recompensas = {
            "almoco_completo": ("Almoço Completo e Saudável", 15, "🍽️"),
            "comeu_fruta": ("Comeu Fruta Fresquinha", 10, "🍎"),
            "provou_novo": ("Desafio do Chef: Provou Alimento Novo", 20, "🥦"),
            "bebeu_agua": ("Missão Hidratação (Copo d'Água)", 5, "💧"),
        }

        nome, fichas, icone = recompensas.get(tipo_refeicao, ("Refeição Saudável", 10, "🍽️"))
        token_mgr.creditar_fichas(fichas, f"Vida Real: {nome}", "ALIMENTO")
        pet_mgr.alimentar(30, nome, 0)

        return {
            "sucesso": True,
            "mensagem": f"{icone} Que orgulho! {nome} confirmado com sucesso! (+{fichas} Moedas no Pote!)",
            "fichas_ganhas": fichas,
            "status_pote": token_mgr.obter_status_pote(),
            "status_pet": pet_mgr.obter_status(),
        }


# Instância global
food_mgr = FoodEducationManager()
