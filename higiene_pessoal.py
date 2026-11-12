"""
Módulo de Higiene Pessoal & Autocuidado dos Pequenos Campeões.
Ensina hábitos essenciais de saúde, autonomia e virtude:
1. Lavar as Mãos (Xô Bactérias e Germes!).
2. Escovação Mágica dos Dentinhos (Sorriso Brilhante e Xô Cáries!).
3. Banho dos Campeões (Corpinho Cheiroso e Relaxante).
4. Unhas Limpinhas & Cabelo de Super-Herói.
"""

from typing import Any, Dict, List
from banco_dados import db
from economia_fichas import token_mgr
from jarvis_pet_status import pet_mgr


class PersonalHygieneManager:
    """Gerencia missões, ensinamentos e recompensas de higiene pessoal infantil."""

    def __init__(self, database=db):
        self.db = database

    def obter_missoes(self) -> List[Dict[str, Any]]:
        """Retorna as missões de higiene pessoal com explicações lúdicas e científicas para crianças."""
        return [
            {
                "id": "lavar_maos",
                "titulo": "Lavar as Mãos (Xô Bactérias!)",
                "icone": "🧼",
                "cor": "#06b6d4",
                "moedas": 2,
                "quando": "Antes de comer, depois de ir ao banheiro e ao chegar da rua",
                "instrucao": "Passe o sabãozinho, esfregue a palma, o dorso e entre cada dedinho enquanto canta!",
                "fala_jarvis": "Lavar as mãos com água e sabão cria um escudo invisível contra bactérias e vírus! Seus dedinhos ficam limpinhos e protegidos!",
            },
            {
                "id": "escovar_dentes",
                "titulo": "Escovação Mágica dos Dentinhos",
                "icone": "🪥",
                "cor": "#3b82f6",
                "moedas": 2,
                "quando": "Após as refeições e antes de ir dormir",
                "instrucao": "Movimento de trenzinho nos dentes do fundo e vassourinha de cima para baixo!",
                "fala_jarvis": "Escovar os dentes protege seu sorriso dos monstrinhos da cárie! Escove com carinho na frente e atrás para um sorriso brilhante!",
            },
            {
                "id": "banho_campeao",
                "titulo": "Super Banho dos Campeões",
                "icone": "🚿",
                "cor": "#10b981",
                "moedas": 3,
                "quando": "Todos os dias para relaxar e ficar cheiroso",
                "instrucao": "Shampoo no cabelinho, sabonete no corpinho e secar bem entre os dedinhos dos pés!",
                "fala_jarvis": "O banho relaxa os músculos após um dia cheio de aventuras e limpa toda a poeirinha! Seque bem os pezinhos depois!",
            },
            {
                "id": "cabelo_unhas",
                "titulo": "Unhas Limpas & Penteado Stark",
                "icone": "✂️",
                "cor": "#a855f7",
                "moedas": 2,
                "quando": "Manter unhas cortadinhas e cabelos penteados",
                "instrucao": "Peça ajuda ao papai ou mamãe para cortar as unhas e use a escovinha no cabelo!",
                "fala_jarvis": "Unhas curtinhas e limpas evitam sujeiras escondidas! E cabelo penteado deixa você pronto para salvar o dia!",
            },
        ]

    def concluir_missao(self, missao_id: str) -> Dict[str, Any]:
        """Registra a conclusão de uma missão de higiene, credita moedas e limpa o robô."""
        missoes = {m["id"]: m for m in self.obter_missoes()}
        if missao_id not in missoes:
            return {"sucesso": False, "mensagem": "Missão de higiene não encontrada."}

        missao = missoes[missao_id]
        fichas = missao["moedas"]

        # Credita fichas na economia real
        token_mgr.creditar_fichas(fichas, f"Higiene: {missao['titulo']}", "ROTINA")
        token_mgr.creditar_estrela(1)

        # Atualiza a higiene do pet/robô Jarvis
        pet_mgr.limpar(35)

        mensagem_voz = f"Parabéns! {missao['fala_jarvis']} Você ganhou {fichas} moedas de ouro!"

        return {
            "sucesso": True,
            "missao_id": missao_id,
            "titulo": missao["titulo"],
            "mensagem": f"✨ Que orgulho! {missao['titulo']} concluído com sucesso! (+{fichas} Moedas e +1 Estrela!)",
            "fala_jarvis": mensagem_voz,
            "fichas_ganhas": fichas,
            "status_pote": token_mgr.obter_status_pote(),
            "status_pet": pet_mgr.obter_status(),
        }


# Instância global
hygiene_mgr = PersonalHygieneManager()
