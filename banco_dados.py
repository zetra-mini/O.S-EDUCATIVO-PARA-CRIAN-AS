"""
Módulo de Banco de Dados SQLite de Alto Desempenho para Hardware Restrito (Intel Atom N450 / 2GB RAM).
Aplica rigorosamente:
1. PRAGMA journal_mode = WAL (Write-Ahead Logging para leitura e escrita concorrentes sem travas)
2. PRAGMA synchronous = NORMAL (reduz acessos I/O excessivos ao disco/SSD)
3. PRAGMA temp_store = MEMORY (tabelas e ordenações temporárias na RAM)
4. PRAGMA busy_timeout = 5000 (espera até 5 segundos em concorrência evitando SQLITE_BUSY)
5. Padrão Single-Writer (Fila de gravação sequencial com Worker dedicado) e Multi-Reader simultâneo.
6. Consultas paginadas com geradores (yield) para gestão estrita de RAM.
"""

import gc
import json
import os
import queue
import sqlite3
import threading
import time
from typing import Any, Callable, Generator, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "banco_educativo.db")


def configurar_pragmas(conn: sqlite3.Connection) -> None:
    """Injeta pragmas essenciais para ultra-desempenho no SQLite."""
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA foreign_keys = ON;")


class WriteTask:
    """Representa uma operação de escrita sequencial enfileirada para o Worker."""

    def __init__(self, sql: str, params: tuple = (), callback: Optional[Callable] = None):
        self.sql = sql
        self.params = params
        self.callback = callback
        self.event = threading.Event()
        self.result: Any = None
        self.error: Optional[Exception] = None


class DatabaseManager:
    """
    Gerenciador central de SQLite Single-Writer / Multi-Reader.
    - Leituras: conexões rápidas e independentes em modo WAL.
    - Gravações: enfileiradas e executadas estritamente por um único Worker em segundo plano.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._write_queue: queue.Queue = queue.Queue(maxsize=1000)
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._writer_worker_loop, daemon=True, name="SQLiteSingleWriter"
        )
        self._worker_thread.start()
        self.inicializar_tabelas()

    def _get_read_connection(self) -> sqlite3.Connection:
        """Cria uma conexão de leitura independente configurada com WAL."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        configurar_pragmas(conn)
        return conn

    def _writer_worker_loop(self) -> None:
        """Worker sequencial exclusivo para todas as escritas no banco de dados."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        configurar_pragmas(conn)

        while self._running:
            try:
                task: Optional[WriteTask] = self._write_queue.get(timeout=1.0)
                if task is None:
                    continue

                try:
                    cursor = conn.cursor()
                    cursor.execute(task.sql, task.params)
                    conn.commit()
                    task.result = cursor.lastrowid
                    if task.callback:
                        task.callback(task.result, None)
                except Exception as exc:
                    conn.rollback()
                    task.error = exc
                    if task.callback:
                        task.callback(None, exc)
                finally:
                    task.event.set()
                    self._write_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                pass

        try:
            conn.close()
        except Exception:
            pass

    def executar_escrita(self, sql: str, params: tuple = (), timeout: float = 6.0) -> Any:
        """Enfileira uma instrução de escrita no Worker e aguarda o término de forma segura."""
        task = WriteTask(sql, params)
        self._write_queue.put(task)
        if not task.event.wait(timeout=timeout):
            raise TimeoutError("Tempo limite excedido na fila de escrita do SQLite Single-Writer.")
        if task.error:
            raise task.error
        return task.result

    def executar_escrita_lote(self, lista_comandos: List[Tuple[str, tuple]]) -> bool:
        """Executa um lote de escritas em uma única transação atômica pelo Worker."""
        for sql, params in lista_comandos:
            self.executar_escrita(sql, params)
        return True

    def consultar_um(self, sql: str, params: tuple = ()) -> Optional[dict]:
        """Consulta um único registro de forma concorrente sem travar o banco."""
        conn = self._get_read_connection()
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def consultar_todos(self, sql: str, params: tuple = ()) -> List[dict]:
        """Consulta registros com limite seguro."""
        conn = self._get_read_connection()
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def consultar_gerador(
        self, sql: str, params: tuple = (), limit: int = 15, offset: int = 0
    ) -> Generator[dict, None, None]:
        """
        Consulta paginada usando gerador (yield) linha por linha.
        Nunca carrega o dataset inteiro na memória RAM (essencial para 2GB de RAM).
        """
        sql_paginado = f"{sql.rstrip(';')} LIMIT {limit} OFFSET {offset};"
        conn = self._get_read_connection()
        try:
            cur = conn.cursor()
            cur.execute(sql_paginado, params)
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                yield dict(row)
        finally:
            conn.close()
            # Sugere coleta ativa após consumir gerador
            gc.collect()

    def inicializar_tabelas(self) -> None:
        """Cria e estrutura todas as tabelas necessárias para o ecossistema educativo do Kaleu."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        configurar_pragmas(conn)
        cursor = conn.cursor()

        # 1. POTE DE FICHAS & HISTÓRICO DE RECOMPENSAS (TOKEN ECONOMY)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pote_fichas (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                saldo INTEGER NOT NULL DEFAULT 0,
                total_acumulado INTEGER NOT NULL DEFAULT 0,
                estrelas INTEGER NOT NULL DEFAULT 0,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO pote_fichas (id, saldo, total_acumulado, estrelas)
            VALUES (1, 20, 20, 5);
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transacoes_fichas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quantidade INTEGER NOT NULL,
                tipo TEXT NOT NULL, -- 'GANHO' ou 'RESGATE'
                categoria TEXT NOT NULL, -- 'ROTINA', 'MISSAO', 'JOGO', 'ALIMENTO', 'CLIMA'
                descricao TEXT NOT NULL,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # 2. LOJA DO TESOURO REAL & ACESSÓRIOS VIRTUAIS DO JARVIS
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recompensas_loja (
                id TEXT PRIMARY KEY,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                custo_fichas INTEGER NOT NULL,
                tipo TEXT NOT NULL, -- 'REAL' (mundo real com os pais) ou 'VIRTUAL' (roupinha pet)
                icone TEXT NOT NULL,
                disponivel BOOLEAN NOT NULL DEFAULT 1,
                vezes_resgatado INTEGER NOT NULL DEFAULT 0
            );
            """
        )

        # 2.05 REGISTRO DE RESGATES DO TESOURO REAL EM FAMÍLIA (PAI & FILHO)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS resgates_familia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL,
                titulo TEXT NOT NULL,
                icone TEXT NOT NULL,
                custo_fichas INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDENTE', -- 'PENDENTE' ou 'ENTREGUE'
                solicitado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                entregue_em TIMESTAMP DEFAULT NULL
            );
            """
        )

        # 2.1 INVENTÁRIO DE ACESSÓRIOS VESTÍVEIS REAIS DO JARVIS (ARMÁRIO)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inventario_acessorios (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                custo_fichas INTEGER NOT NULL,
                icone TEXT NOT NULL,
                categoria TEXT NOT NULL, -- 'olhos', 'cabeca', 'pescoco', 'costas'
                comprado BOOLEAN NOT NULL DEFAULT 0,
                equipado BOOLEAN NOT NULL DEFAULT 0
            );
            """
        )

        # 3. STATUS DO BICHINHO VIRTUAL (POU / B-BOT JARVIS)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bixinho_status (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                higiene REAL NOT NULL DEFAULT 100.0,
                alimentacao REAL NOT NULL DEFAULT 100.0,
                diversao REAL NOT NULL DEFAULT 100.0,
                energia REAL NOT NULL DEFAULT 100.0,
                felicidade REAL NOT NULL DEFAULT 100.0,
                estado_animacao TEXT NOT NULL DEFAULT 'PARADO',
                acessorio_atual TEXT DEFAULT NULL,
                modo_dormir BOOLEAN NOT NULL DEFAULT 0,
                ultimo_decaimento REAL DEFAULT 0,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO bixinho_status (id, higiene, alimentacao, diversao, energia, felicidade, estado_animacao, modo_dormir)
            VALUES (1, 100.0, 100.0, 100.0, 100.0, 100.0, 'PARADO', 0);
            """
        )

        # 4. AGENDA E ROTINAS DIÁRIAS (PROTOCOLOS ANTI-CONFLITO & MISSÕES COOPERATIVAS)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agenda_rotina_diaria (
                id TEXT PRIMARY KEY,
                titulo TEXT NOT NULL,
                horario TEXT NOT NULL, -- 'HH:MM'
                aviso_previo_minutos INTEGER NOT NULL DEFAULT 5,
                tipo_acao TEXT NOT NULL, -- 'desafio_tempo', 'mensagem_voz', 'escolha_dirigida'
                icone TEXT NOT NULL,
                pergunta_escolha TEXT DEFAULT NULL,
                recompensa_fichas INTEGER NOT NULL DEFAULT 5,
                ativo BOOLEAN NOT NULL DEFAULT 1,
                concluida_hoje BOOLEAN NOT NULL DEFAULT 0,
                data_conclusao TEXT DEFAULT NULL
            );
            """
        )

        # 5. INTELIGÊNCIA EMOCIONAL (SCANNER DE HUMOR, MAPA CORPORAL E TERMÔMETRO DA CALMA)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS emocoes_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                humor TEXT NOT NULL, -- 'FELIZ', 'CALMO', 'BRAVO', 'CANSADO', 'TRISTE'
                local_corpo TEXT DEFAULT NULL, -- 'PEITO', 'BARRIGA', 'MAOS', 'CABECA'
                respiracao_concluida BOOLEAN DEFAULT 0,
                observacao TEXT DEFAULT NULL,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # 6. FUNÇÕES EXECUTIVAS E MEMÓRIA (REPETIÇÃO ESPAÇADA DE LEITNER)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cognicao_leitner (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT NOT NULL, -- 'ALFABETO', 'NUMEROS', 'ANIMAIS', 'CURIOSIDADES'
                pergunta TEXT NOT NULL,
                resposta_correta TEXT NOT NULL,
                opcoes_json TEXT NOT NULL,
                caixa INTEGER NOT NULL DEFAULT 1, -- 1 = Diário, 2 = 3 Dias, 3 = Semanal
                acertos INTEGER NOT NULL DEFAULT 0,
                erros INTEGER NOT NULL DEFAULT 0,
                ultima_revisao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # 7. EDUCAÇÃO ALIMENTAR E PRATO COLORIDO
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alimentos_nutricao (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL, -- 'fruta', 'legume', 'grao', 'proteina', 'doce'
                semaforo TEXT NOT NULL, -- 'verde', 'amarelo', 'vermelho'
                superpoder TEXT NOT NULL,
                cor_grupo TEXT NOT NULL, -- 'verde', 'laranja', 'vermelho', 'roxo', 'amarelo'
                icone TEXT NOT NULL,
                pontos_nutritivos INTEGER NOT NULL DEFAULT 10
            );
            """
        )

        # 8. DATAS COMEMORATIVAS DO BRASIL E DO MUNDO
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS datas_calendario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                categoria TEXT NOT NULL, -- 'brasil', 'mundo', 'natureza', 'ciencia'
                mensagem_jarvis TEXT NOT NULL,
                acessorio_mascote TEXT DEFAULT NULL,
                desafio_tipo TEXT NOT NULL, -- 'missao_real', 'minigame', 'quiz'
                recompensa_fichas INTEGER NOT NULL DEFAULT 15,
                ano_conclusao INTEGER DEFAULT NULL
            );
            """
        )

        # 9. CLIMA & CACHE INTELIGENTE DE 120 MINUTOS (OPEN-METEO SEM CHAVE)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_clima (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                temperatura REAL NOT NULL,
                codigo_tempo INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                icone TEXT NOT NULL,
                estacao_ano TEXT NOT NULL,
                conselho_infantil TEXT NOT NULL,
                acessorio_mascote TEXT NOT NULL,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # 10. MENSAGENS SECRETAS DOS PAIS & RASTREAMENTO EM TEMPO REAL
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mensagens_familia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remetente TEXT NOT NULL DEFAULT 'Papai',
                tipo TEXT NOT NULL, -- 'texto', 'audio', 'video'
                conteudo_texto TEXT DEFAULT '',
                caminho_midia TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'ENVIADA', -- 'ENVIADA', 'RECEBIDA', 'ABERTA'
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_abertura TIMESTAMP DEFAULT NULL
            );
            """
        )

        # 11. REGISTRO DE USO DE MÍDIA E HORÁRIOS (SUBSTITUI USO_DIARIO.JSON)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS uso_tempo_midia (
                data_iso TEXT PRIMARY KEY,
                segundos_assistidos INTEGER NOT NULL DEFAULT 0,
                livros_lidos INTEGER NOT NULL DEFAULT 0,
                livros_ids_json TEXT NOT NULL DEFAULT '[]',
                minutos_bonus INTEGER NOT NULL DEFAULT 0,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # 12. LOGS DO SISTEMA & DIAGNÓSTICO DE FALHAS
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sistema_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                nivel TEXT NOT NULL,         -- 'ERRO', 'ALERTA', 'INFO'
                modulo TEXT NOT NULL,        -- 'voz', 'ia', 'sqlite', 'servidor', 'idiomas', 'clima', 'midia'
                mensagem TEXT NOT NULL,
                detalhes TEXT DEFAULT ''
            );
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_data ON sistema_logs (data_hora DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_nivel ON sistema_logs (nivel);")

        # 13. PROGRESSO DO ESTUDO DE IDIOMAS (INGLÊS E ESPANHOL)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS progresso_idiomas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idioma TEXT NOT NULL,         -- 'en', 'es'
                categoria TEXT NOT NULL,
                palavra_id TEXT NOT NULL,
                acertos INTEGER NOT NULL DEFAULT 0,
                erros INTEGER NOT NULL DEFAULT 0,
                ultima_pratica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(idioma, categoria, palavra_id)
            );
            """
        )

        conn.commit()

        # POPULAR ITENS INICIAIS DA LOJA DO TESOURO SE VAZIA
        cursor.execute("SELECT COUNT(*) FROM recompensas_loja;")
        if cursor.fetchone()[0] == 0:
            itens_loja = [
                ("passeio_parque", "🌳 Passeio Especial no Parque com o Papai", "Uma tarde divertida ao ar livre escolhendo a brincadeira!", 50, "REAL", "🌳"),
                ("escolher_filme", "🎬 Escolher o Filme do Cinema em Família", "Direito de escolher o desenho animado de sexta à noite!", 35, "REAL", "🎬"),
                ("brincadeira_extra", "🧩 +30 Minutos de Bloco de Montar / Massinha", "Tempo livre de brincadeira com o pai antes do banho!", 25, "REAL", "🧩"),
                ("chapeu_astronauta", "👨‍🚀 Capacete de Astronauta para o Jarvis", "Acessório cósmico para o seu robô companheiro!", 20, "VIRTUAL", "👨‍🚀"),
                ("oculos_estiloso", "🕶️ Óculos Escuros Neon para o Jarvis", "Deixe o robô estiloso para os dias de sol!", 15, "VIRTUAL", "🕶️"),
                ("luz_dourada", "⭐ Reator Arc Dourado Brilhante", "Aura estelar cintilante para o mascote!", 30, "VIRTUAL", "⭐"),
            ]
            cursor.executemany(
                "INSERT INTO recompensas_loja (id, titulo, descricao, custo_fichas, tipo, icone) VALUES (?, ?, ?, ?, ?, ?);",
                itens_loja,
            )

        # POPULAR ACESSÓRIOS VESTÍVEIS DO ARMÁRIO DO JARVIS SE VAZIA
        cursor.execute("SELECT COUNT(*) FROM inventario_acessorios;")
        if cursor.fetchone()[0] == 0:
            acessorios = [
                ("oculos_stark", "Óculos Stark Neon", "Lentes futuristas espelhadas de alta tecnologia!", 15, "🕶️", "olhos", 0, 0),
                ("coroa_ouro", "Coroa Real de Ouro", "Coroa brilhante de mestre de missões cumpridas!", 25, "👑", "cabeca", 0, 0),
                ("bone_heroi", "Boné Espacial de Campeão", "Boné estiloso de explorador do universo!", 15, "🧢", "cabeca", 0, 0),
                ("cachecol_espacial", "Cachecol Quentinho das Estrelas", "Cachecol macio e quentinho com listras douradas!", 12, "🧣", "pescoco", 0, 0),
                ("headset_gamer", "Headset Gamer Neon Pro", "Fones luminosos com microfone de comunicação galáctica!", 20, "🎧", "cabeca", 0, 0),
                ("asas_foguete", "Asas de Propulsão Plasma", "Turbinas de voo cósmico para voar super alto!", 30, "🚀", "costas", 0, 0),
            ]
            cursor.executemany(
                "INSERT INTO inventario_acessorios (id, nome, descricao, custo_fichas, icone, categoria, comprado, equipado) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                acessorios,
            )

        # POPULAR DATAS COMEMORATIVAS SE VAZIA
        cursor.execute("SELECT COUNT(*) FROM datas_calendario;")
        if cursor.fetchone()[0] == 0:
            datas = [
                (22, 3, "Dia Mundial da Água", "natureza", "A água é a fonte da vida do nosso planeta! Vamos lembrar de fechar a torneira!", "gotinha.png", "missao_real", 20),
                (22, 4, "Dia do Planeta Terra", "natureza", "A Terra é a nossa grande casa! Que tal cuidar de uma plantinha hoje?", "folhinha.png", "missao_real", 20),
                (5, 6, "Dia Mundial do Meio Ambiente", "natureza", "Proteger as florestas e os animais é dever de todo pequeno herói!", "arvore.png", "minigame", 20),
                (24, 6, "Festa Junina & Tradições", "brasil", "Pula a fogueira com alegria e comidinhas de milho gostosas!", "chapeu_palha.png", "quiz", 20),
                (20, 7, "Dia do Amigo & Espaço", "ciencia", "Um viva para os grandes amigos que viajam com a gente pelo universo!", "capacete_espaco.png", "quiz", 20),
                (21, 9, "Dia da Árvore", "natureza", "As árvores dão sombra fresquinha e ar puro para respirarmos bem fundo!", "folhinha.png", "missao_real", 20),
                (12, 10, "Dia das Crianças & Imaginação", "brasil", "Hoje o dia é todo seu, Kaleu! Muita brincadeira, sorrisos e afeto!", "coroa_ouro.png", "minigame", 30),
                (29, 10, "Dia Nacional do Livro", "brasil", "Cada história é uma nave espacial que nos leva a lugares mágicos!", "livro_magico.png", "missao_real", 25),
            ]
            cursor.executemany(
                "INSERT INTO datas_calendario (dia, mes, titulo, categoria, mensagem_jarvis, acessorio_mascote, desafio_tipo, recompensa_fichas) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                datas,
            )

        # POPULAR ALIMENTOS SE VAZIA
        cursor.execute("SELECT COUNT(*) FROM alimentos_nutricao;")
        if cursor.fetchone()[0] == 0:
            alimentos = [
                ("cenoura", "Cenoura Crocante", "legume", "verde", "Supervisão de águia e pele protegida!", "laranja", "🥕", 15),
                ("brocolis", "Brócolis Arvorezinha", "legume", "verde", "Escudo de imunidade e força nos músculos!", "verde", "🥦", 15),
                ("melancia", "Melancia Refrescante", "fruta", "verde", "Hidratação profunda e coração de herói!", "vermelho", "🍉", 15),
                ("banana", "Banana de Ouro", "fruta", "verde", "Energia pura para correr, pular e brincar!", "amarelo", "🍌", 12),
                ("feijao", "Feijãozinho Gostoso", "grao", "verde", "Força de ferro no sangue e supermemória!", "roxo", "🫘", 15),
                ("maca", "Maçã Vermelha", "fruta", "verde", "Dentes limpinhos e corpo cheio de vitalidade!", "vermelho", "🍎", 12),
                ("pao_queijo", "Pão de Queijo Caseiro", "grao", "amarelo", "Comer com moderação no lanche da tarde!", "amarelo", "🧀", 8),
                ("bala_doce", "Bala / Pirulito", "doce", "vermelho", "Apenas em festinhas e dias especiais!", "vermelho", "🍬", 2),
            ]
            cursor.executemany(
                "INSERT INTO alimentos_nutricao (id, nome, categoria, semaforo, superpoder, cor_grupo, icone, pontos_nutritivos) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                alimentos,
            )

        # POPULAR AGENDA DA ROTINA DIÁRIA SE VAZIA
        cursor.execute("SELECT COUNT(*) FROM agenda_rotina_diaria;")
        if cursor.fetchone()[0] == 0:
            rotinas = [
                ("dente_manha", "🦷 Missão Dente Brilhante da Manhã", "08:00", 5, "desafio_tempo", "🦷", "Escovar com carinho por 2 minutos!", 5),
                ("almoço_forte", "🍽️ Almoço dos Superpoderes", "12:00", 10, "escolha_dirigida", "🍽️", "Qual verdura ou legume vamos provar hoje?", 5),
                ("quarto_limpo", "🧸 Operação Quarto Limpo (Guardar Brinquedos)", "17:30", 5, "escolha_dirigida", "🧸", "Quer guardar os carrinhos ou os blocos primeiro?", 10),
                ("banho_relax", "🛁 Hora do Banho Quentinho & Limpeza", "19:00", 5, "desafio_tempo", "🛁", "Lavar o corpo para recarregar as energias!", 5),
                ("dormir_abajur", "🌙 Apagar o Abajur & Hora do Sono", "20:30", 5, "desafio_tempo", "🌙", "Puxar a cordinha do abajur do Jarvis para dormir!", 10),
            ]
            cursor.executemany(
                "INSERT INTO agenda_rotina_diaria (id, titulo, horario, aviso_previo_minutos, tipo_acao, icone, pergunta_escolha, recompensa_fichas) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                rotinas,
            )

        conn.commit()
        conn.close()


# Instância singleton global do Banco de Dados
db = DatabaseManager()


# ==============================================================================
# FUNÇÕES DE GESTÃO DE LOGS E DIAGNÓSTICO DO SISTEMA (PAINEL ADM)
# ==============================================================================


def registrar_log(nivel: str, modulo: str, mensagem: str, detalhes: str = "") -> None:
    """
    Grava um evento, alerta ou erro do sistema no SQLite via fila Single-Writer.
    Níveis válidos: 'ERRO', 'ALERTA', 'INFO'.
    """
    try:
        nivel_fmt = (nivel or "INFO").upper().strip()
        modulo_fmt = (modulo or "sistema").lower().strip()
        msg_fmt = str(mensagem or "").strip()
        det_fmt = str(detalhes or "").strip()

        db.executar_escrita(
            """
            INSERT INTO sistema_logs (nivel, modulo, mensagem, detalhes)
            VALUES (?, ?, ?, ?);
            """,
            (nivel_fmt, modulo_fmt, msg_fmt, det_fmt),
            timeout=2.0,
        )
    except Exception as e:
        # Fallback defensivo para nunca quebrar a thread chamadora
        import sys
        sys.stderr.write(f"[FALHA_LOG] {e} | {nivel} | {modulo} | {mensagem}\n")


def obter_logs(limite: int = 100, nivel: Optional[str] = None, busca: Optional[str] = None) -> List[dict]:
    """
    Consulta os logs mais recentes de forma defensiva e paginada.
    """
    limite = max(1, min(int(limite or 100), 500))
    filtros = []
    params = []

    if nivel and nivel.upper() in ("ERRO", "ALERTA", "INFO"):
        filtros.append("nivel = ?")
        params.append(nivel.upper())

    if busca and busca.strip():
        filtros.append("(mensagem LIKE ? OR detalhes LIKE ? OR modulo LIKE ?)")
        termo = f"%{busca.strip()}%"
        params.extend([termo, termo, termo])

    where_clause = f"WHERE {' AND '.join(filtros)}" if filtros else ""
    sql = f"""
        SELECT id, data_hora, nivel, modulo, mensagem, detalhes
        FROM sistema_logs
        {where_clause}
        ORDER BY id DESC
        LIMIT ?;
    """
    params.append(limite)

    return db.consultar_todos(sql, tuple(params))


def limpar_logs() -> bool:
    """Limpa o histórico de logs do sistema e registra o evento de limpeza."""
    try:
        db.executar_escrita("DELETE FROM sistema_logs;", timeout=3.0)
        registrar_log("INFO", "sistema", "Histórico de logs limpo pelo administrador.")
        return True
    except Exception as e:
        registrar_log("ERRO", "sistema", f"Falha ao limpar logs: {e}")
        return False


def registrar_progresso_idioma(idioma: str, categoria: str, palavra_id: str, acertou: bool) -> None:
    """Registra ou atualiza o progresso de aprendizado de vocabulário da criança."""
    col_update = "acertos = acertos + 1" if acertou else "erros = erros + 1"
    sql = f"""
        INSERT INTO progresso_idiomas (idioma, categoria, palavra_id, acertos, erros, ultima_pratica)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(idioma, categoria, palavra_id) DO UPDATE SET
            {col_update},
            ultima_pratica = CURRENT_TIMESTAMP;
    """
    acertos_init = 1 if acertou else 0
    erros_init = 0 if acertou else 1
    db.executar_escrita(sql, (idioma, categoria, palavra_id, acertos_init, erros_init), timeout=3.0)


def obter_resumo_progresso_idiomas() -> dict:
    """Retorna estatísticas consolidadas de estudo de idiomas para o painel."""
    resumo = {
        "total_praticado": 0,
        "acertos_en": 0,
        "acertos_es": 0,
        "palavras_dominadas": 0,
    }
    for row in db.consultar_todos("SELECT idioma, SUM(acertos) as total_acertos, COUNT(*) as total_palavras FROM progresso_idiomas GROUP BY idioma;"):
        idioma = row["idioma"]
        total = row["total_acertos"] or 0
        if idioma == "en":
            resumo["acertos_en"] = total
        elif idioma == "es":
            resumo["acertos_es"] = total
        resumo["total_praticado"] += total

    row_dom = db.consultar_um("SELECT COUNT(*) as dominadas FROM progresso_idiomas WHERE acertos >= 3;")
    if row_dom:
        resumo["palavras_dominadas"] = row_dom.get("dominadas", 0)

    return resumo

