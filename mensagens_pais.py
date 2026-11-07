"""
Módulo de Presença Paterna e Mensagens Remotas da Família.
Transforma o computador em uma ponte afetiva segura entre o pai/mãe e o Kaleu:
1. Tabela mensagens_familia no SQLite WAL.
2. Ciclo de status em tempo real: ENVIADA -> RECEBIDA -> ABERTA.
3. Rastreamento com hora exata para visualização no celular dos pais.
4. Notificação com envelope brilhante e modo foco na reprodução.
"""

import os
import base64
import time
import uuid
from typing import Any, Dict, List, Optional
from banco_dados import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads_recados")
os.makedirs(UPLOADS_DIR, exist_ok=True)


class FamilyMessagesManager:
    """Gerencia o envio, entrega e confirmação de leitura das mensagens da família."""

    def __init__(self, database=db):
        self.db = database

    def salvar_midia_base64(self, midia_base64: str, tipo_padrao: str = "audio") -> tuple:
        """
        Decodifica string DataURL base64 e salva no disco.
        Retorna (tipo_detectado, url_relativa_arquivo).
        """
        if not midia_base64 or not isinstance(midia_base64, str):
            return (tipo_padrao, "")

        header = ""
        b64_data = midia_base64
        ext = "webm"
        tipo = tipo_padrao

        if "," in midia_base64:
            header, b64_data = midia_base64.split(",", 1)
            header_lower = header.lower()
            if "video" in header_lower:
                tipo = "video"
                if "mp4" in header_lower:
                    ext = "mp4"
                elif "webm" in header_lower:
                    ext = "webm"
                elif "quicktime" in header_lower or "mov" in header_lower:
                    ext = "mov"
                else:
                    ext = "webm"
            elif "audio" in header_lower:
                tipo = "audio"
                if "mp3" in header_lower or "mpeg" in header_lower:
                    ext = "mp3"
                elif "wav" in header_lower:
                    ext = "wav"
                elif "ogg" in header_lower:
                    ext = "ogg"
                elif "m4a" in header_lower or "mp4" in header_lower:
                    ext = "m4a"
                else:
                    ext = "webm"

        filename = f"recado_{int(time.time())}_{uuid.uuid4().hex[:6]}.{ext}"
        filepath = os.path.join(UPLOADS_DIR, filename)

        try:
            file_bytes = base64.b64decode(b64_data)
            with open(filepath, "wb") as f:
                f.write(file_bytes)
            url_relativa = f"/static/uploads_recados/{filename}"
            return (tipo, url_relativa)
        except Exception as e:
            print(f"Erro ao salvar midia de recado: {e}")
            return (tipo, "")

    def enviar_mensagem(
        self,
        remetente: str = "Papai",
        tipo: str = "texto",
        texto: str = "",
        caminho_midia: str = "",
        midia_base64: str = "",
    ) -> Dict[str, Any]:
        """Salva nova mensagem no SQLite via fila Single-Writer com status ENVIADA."""
        if midia_base64:
            tipo_detectado, midia_url = self.salvar_midia_base64(midia_base64, tipo_padrao=tipo)
            if midia_url:
                caminho_midia = midia_url
                tipo = tipo_detectado

        msg_id = self.db.executar_escrita(
            """
            INSERT INTO mensagens_familia (remetente, tipo, conteudo_texto, caminho_midia, status, data_envio)
            VALUES (?, ?, ?, ?, 'ENVIADA', CURRENT_TIMESTAMP);
            """,
            (remetente, tipo, (texto or "").strip(), caminho_midia or ""),
        )
        return {
            "sucesso": True,
            "id": msg_id,
            "tipo": tipo,
            "caminho_midia": caminho_midia,
            "mensagem": f"Recado de {tipo} enviado com carinho para o netbook do Kaleo!",
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
            SELECT id, remetente, tipo, conteudo_texto, caminho_midia, status, data_envio, data_abertura
            FROM mensagens_familia
            ORDER BY id DESC LIMIT {limite};
            """
        )


# Instância global
messages_mgr = FamilyMessagesManager()
