"""
Módulo de Presença Paterna e Mensagens Remotas da Família.
Transforma o computador em uma ponte afetiva segura entre o pai/mãe e o Campeão:
1. Tabela mensagens_familia no SQLite WAL.
2. Ciclo de status em tempo real: ENVIADA -> RECEBIDA -> ABERTA.
3. Rastreamento com hora exata para visualização no celular dos pais.
4. Notificação com envelope brilhante e modo foco na reprodução.
"""

import os
import base64
import time
import uuid
import shutil
import subprocess
from typing import Any, Dict, List, Optional
from banco_dados import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads_recados")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def otimizar_video_480p(filepath: str) -> str:
    """
    Otimiza e redimensiona vídeos para no máximo 480px de largura/altura,
    com taxa de quadros (24 fps) e bitrate leve (~500k) para não sobrecarregar
    o hardware modesto do Netbook (Intel Atom N450 / GMA 3150 / 1GB RAM / tela 1024x600).
    Converte para MP4 H.264 Baseline com moov atom faststart.
    Se o ffmpeg falhar, não estiver presente ou der timeout, retorna o arquivo original com segurança.
    """
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin or not os.path.exists(filepath):
        return filepath

    dir_name, base_name = os.path.split(filepath)
    name, _ = os.path.splitext(base_name)
    output_path = os.path.join(dir_name, f"{name}_480p.mp4")

    # Comando ultra leve e tolerante a streams sem áudio (-map 0:a?)
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", filepath,
        "-vf", "scale=min(480\\,iw):-2",
        "-r", "24",
        "-c:v", "libx264",
        "-profile:v", "baseline",
        "-level", "3.0",
        "-pix_fmt", "yuv420p",
        "-b:v", "450k",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-b:a", "64k",
        "-movflags", "+faststart",
        output_path,
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            try:
                os.remove(filepath)
            except Exception:
                pass
            return output_path
    except Exception as e:
        print(f"Aviso: Otimização FFmpeg não aplicada (usando arquivo original): {e}")

    return filepath


class FamilyMessagesManager:
    """Gerencia o envio, entrega e confirmação de leitura das mensagens da família."""

    def __init__(self, database=db):
        self.db = database

    def salvar_midia_base64(self, midia_base64: str, tipo_padrao: str = "audio") -> tuple:
        """
        Decodifica string DataURL base64 e salva no disco com garantia de integridade.
        Retorna (tipo_detectado, url_relativa_arquivo).
        """
        if not midia_base64 or not isinstance(midia_base64, str):
            return (tipo_padrao, "")

        header = ""
        b64_data = midia_base64
        ext = "webm"
        tipo = tipo_padrao

        if ";base64," in midia_base64:
            header, b64_data = midia_base64.split(";base64,", 1)
        elif "," in midia_base64:
            header, b64_data = midia_base64.rsplit(",", 1)

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

        # Limpeza de possíveis quebras de linha ou espaços
        b64_data = b64_data.strip().replace("\r", "").replace("\n", "").replace(" ", "+")
        # Garante padding correto para múltiplos de 4
        missing_padding = len(b64_data) % 4
        if missing_padding:
            b64_data += "=" * (4 - missing_padding)

        filename = f"recado_{int(time.time())}_{uuid.uuid4().hex[:6]}.{ext}"
        filepath = os.path.join(UPLOADS_DIR, filename)

        try:
            file_bytes = base64.b64decode(b64_data)
            if not file_bytes or len(file_bytes) < 100:
                print("Aviso: Dados de mídia Base64 vazios ou menores que 100 bytes.")
                return (tipo, "")

            with open(filepath, "wb") as f:
                f.write(file_bytes)

            filename_final = filename
            # Se for vídeo, tenta otimizar para MP4 480p Baseline, mas se falhar preserva original
            if tipo == "video":
                try:
                    caminho_otimizado = otimizar_video_480p(filepath)
                    filename_final = os.path.basename(caminho_otimizado)
                except Exception as e_opt:
                    print(f"Aviso ao otimizar vídeo ({e_opt}), mantendo original {filename}")
                    filename_final = filename

            url_relativa = f"/static/uploads_recados/{filename_final}"
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
        # Se for áudio ou vídeo, garante que a mídia é válida
        if tipo in ("audio", "video") or midia_base64:
            if midia_base64:
                tipo_detectado, midia_url = self.salvar_midia_base64(midia_base64, tipo_padrao=tipo)
                if midia_url:
                    caminho_midia = midia_url
                    tipo = tipo_detectado
                else:
                    return {
                        "sucesso": False,
                        "erro": f"Não foi possível processar o arquivo de {tipo}. Grave novamente ou tente anexar um arquivo menor.",
                    }
            elif not caminho_midia:
                return {
                    "sucesso": False,
                    "erro": f"Nenhum arquivo de {tipo} foi anexado ou gravado. Por favor, grave ou anexe a mídia primeiro.",
                }

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
            "mensagem": f"Recado de {tipo} enviado com carinho para o netbook do Campeão!",
        }

    def verificar_novas_para_crianca(self) -> Optional[Dict[str, Any]]:
        """
        Retorna a mensagem pendente mais recente para a criança.
        Transiciona automaticamente de 'ENVIADA' para 'RECEBIDA'.
        """
        msg = self.db.consultar_um(
            """
            SELECT id, remetente, tipo, conteudo_texto, caminho_midia, status, data_envio
            FROM mensagens_familia
            WHERE status IN ('ENVIADA', 'RECEBIDA')
            ORDER BY id DESC LIMIT 1;
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
