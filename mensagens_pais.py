"""
Módulo de Presença Paterna e Mensagens Remotas da Família.
Transforma o computador em uma ponte afetiva segura entre o pai/mãe e o Kaleu:
1. Tabela mensagens_familia no SQLite WAL.
2. Ciclo de status em tempo real: ENVIADA -> RECEBIDA -> ABERTA.
3. Rastreamento com hora exata para visualização no celular dos pais.
4. Notificação com envelope brilhante e modo foco na reprodução.
"""

import os
from typing import Any, Dict, List, Optional
from banco_dados import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads_recados")
os.makedirs(UPLOADS_DIR, exist_ok=True)


class FamilyMessagesManager:
    """Gerencia o envio, entrega e confirmação de leitura das mensagens da família."""

    def __init__(self, database=db):
        self.db = database

    def enviar_mensagem(
        self,
        remetente: str = "Papai",
        tipo: str = "texto",
        texto: str = "",
        caminho_midia: str = "",
    ) -> Dict[str, Any]:
        """Salva nova mensagem no SQLite via fila Single-Writer com status ENVIADA."""
        msg_id = self.db.executar_escrita(
            """
            INSERT INTO mensagens_familia (remetente, tipo, conteudo_texto, caminho_midia, status, data_envio)
            VALUES (?, ?, ?, ?, 'ENVIADA', CURRENT_TIMESTAMP);
            """,
            (remetente, tipo, texto.strip(), caminho_midia),
        )
        return {
            "sucesso": True,
            "id": msg_id,
            "mensagem": "Recado enviado com carinho para o netbook do Kaleu!",
        }

    def verificar_novas_para_crianca(self) -> Optional[Dict[str, Any]]:
        """
        Retorna a mensagem mais recente pendente para a criança.
        Transiciona automaticamente de 'ENVIADA' para 'RECEBIDA'.
        """
        msg = self.db.consultar_um(
            """
            SELECT id, remetente, tipo, conteudo_texto, caminho_midia, status, data_envio
            FROM mensagens_familia
            WHERE status IN ('ENVIADA', 'RECEBIDA')
            ORDER BY id ASC LIMIT 1;
            """
        )
        if msg:
            msg_dict = dict(msg)
            if msg_dict["status"] == "ENVIADA":
                self.db.executar_escrita(
                    "UPDATE mensagens_familia SET status = 'RECEBIDA' WHERE id = ?;",
                    (msg_dict["id"],),
                )
                msg_dict["status"] = "RECEBIDA"
            return msg_dict
        return None

    def marcar_como_aberta(self, msg_id: int) -> Dict[str, Any]:
        """Marca mensagem como ABERTA com timestamp no exato momento da reprodução."""
        self.db.executar_escrita(
            """
            UPDATE mensagens_familia
            SET status = 'ABERTA', data_abertura = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (msg_id,),
        )
        return {"sucesso": True, "status": "ABERTA"}

    def listar_status_pais(self, limite: int = 15) -> List[Dict[str, Any]]:
        """Retorna histórico de recados para visualização dos pais no smartphone."""
        return self.db.consultar_todos(
            f"""
            SELECT id, remetente, tipo, conteudo_texto, status, data_envio, data_abertura
            FROM mensagens_familia
            ORDER BY id DESC LIMIT {limite};
            """
        )


# Instância global
messages_mgr = FamilyMessagesManager()
