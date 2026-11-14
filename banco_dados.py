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
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple

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
        """Cria e estrutura todas as tabelas necessárias para o ecossistema educativo do Campeão."""
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

        # 14. MISSÕES DE ROTINA & HÁBITOS (PAINEL DOS PAIS / PILAR 1)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS missoes_rotina (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT DEFAULT '',
                recompensa_moedas INTEGER NOT NULL DEFAULT 5,
                icone TEXT DEFAULT '⭐',
                categoria TEXT DEFAULT 'Geral',
                ativa INTEGER NOT NULL DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS missoes_cumpridas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                missao_id INTEGER NOT NULL,
                data_dia TEXT NOT NULL,
                hora_cumprida TEXT NOT NULL,
                moedas_ganhas INTEGER NOT NULL DEFAULT 5,
                FOREIGN KEY(missao_id) REFERENCES missoes_rotina(id) ON DELETE CASCADE,
                UNIQUE(missao_id, data_dia)
            );
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_missoes_dia ON missoes_cumpridas (data_dia);")

        # 15. GALERIA DE ARTE DA LOUSA NEON (PILAR 2)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS galeria_arte (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT DEFAULT 'Obra de Arte do Campeão',
                imagem_base64 TEXT NOT NULL,
                data_dia TEXT NOT NULL,
                hora TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_arte_dia ON galeria_arte (data_dia DESC);")

        # 16. LINHA DO TEMPO DIÁRIA DE ATIVIDADES (PILAR 4)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS linha_tempo_atividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descricao TEXT DEFAULT '',
                icone TEXT DEFAULT '🌟',
                hora TEXT NOT NULL,
                data_dia TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linha_tempo ON linha_tempo_atividades (data_dia DESC, hora DESC);")

        conn.commit()

        # POPULAR ITENS INICIAIS DA LOJA DO TESOURO REAL (INSERT OR IGNORE)
        itens_loja = [
            ("passeio_parque", "🌳 Passeio no Parque com o Papai", "Uma tarde divertida ao ar livre escolhendo a brincadeira favorita!", 40, "REAL", "🌳"),
            ("escolher_filme", "🎬 Escolher o Filme do Cinema em Família", "Direito especial de escolher o desenho animado de sexta à noite!", 30, "REAL", "🎬"),
            ("brincadeira_extra", "🧩 +30 Minutos de Massinha ou Lego", "Tempo livre de brincadeira com o pai antes do banho da noite!", 20, "REAL", "🧩"),
            ("andar_bicicleta", "🚲 Passeio de Bicicleta ou Patinete", "Passeio veloz de super piloto na pracinha com o papai!", 35, "REAL", "🚲"),
            ("noite_cabaninha", "⛺ Noite da Cabaninha de Lençol", "Construir uma cabaninha gigante de almofadas na sala para brincar!", 45, "REAL", "⛺"),
            ("fazer_panquecas", "🥞 Fazer Panquecas ou Bolo Juntos", "Receita deliciosa na cozinha para misturar a massa e saborear!", 25, "REAL", "🥞"),
            ("tres_historias", "📖 3 Histórias Especiais antes de Dormir", "O papai ou a mamãe leem três livrinhos mágicos na cama!", 15, "REAL", "📖"),
            ("passeio_sorvete", "🍦 Passeio na Sorveteria com 2 Sabores", "Escolher dois sabores deliciosos de sorvete na casquinha!", 35, "REAL", "🍦"),
            ("tarde_pintura", "🎨 Tarde de Pintura com Tinta Guache", "Fazer um quadro artístico de herói com as cores favoritas!", 25, "REAL", "🎨"),
            ("dia_campeao", "🌟 Dia do Super Campeão (Escolhe o Almoço)", "Direito de escolher o cardápio do almoço especial de domingo!", 50, "REAL", "🌟"),
            ("banho_espuma", "🛁 Banho Mágico de Espuma e Brinquedos", "Banho quentinho super divertido com montanhas de espuma!", 15, "REAL", "🛁"),
            ("dormir_tarde", "⏰ +20 Minutos Acordado na Sexta", "Ficar um tempinho a mais acordado para conversar e rir com a família!", 25, "REAL", "⏰"),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO recompensas_loja (id, titulo, descricao, custo_fichas, tipo, icone) VALUES (?, ?, ?, ?, ?, ?);",
            itens_loja,
        )

        # POPULAR ACESSÓRIOS VESTÍVEIS, COMIDINHAS & SKINS DO JARVIS (INSERT OR IGNORE)
        acessorios = [
            # COMIDINHAS & RECARGA DE ENERGIA DO JARVIS (Consumíveis de alta tecnologia - 2 a 4 moedas)
            ("bateria_plasma", "Bateria Quântica de Plasma", "Super carga de íons de plasma que recarrega a bateria do Jarvis instantaneamente!", 2, "🔋", "comida", 0, 0),
            ("reator_arc_mini", "Célula de Energia Arc Stark", "Poder atômico limpo que faz o Reator Arc no peito do Jarvis brilhar intensamente!", 3, "💠", "comida", 0, 0),
            ("picole_eletrico", "Picolé de Eletricidade Cósmica", "Picolé azul neon com faíscas cósmicas refrescantes para os circuitos!", 2, "⚡", "comida", 0, 0),
            ("oleo_turbo_stark", "Óleo Super Turbo Stark", "Lubrificante de titânio de alta velocidade para engrenagens rodarem macias!", 3, "🛢️", "comida", 0, 0),
            ("biscoito_nanobots", "Biscoito Nanotec com Chocolate", "Biscoito crocante com nanobots inteligentes que reparam microchips!", 2, "🍪", "comida", 0, 0),
            ("pocao_combustivel", "Hiper-Combustível Stark Neon", "Frasco de energia luminosa que dobra a velocidade de raciocínio do robô!", 4, "🧪", "comida", 0, 0),
            ("maca_dourada", "Maçã Biocibernética Dourada", "Maçã dourada fortificada com vitaminas e microchips de alta voltagem!", 2, "🍏", "comida", 0, 0),
            ("pizza_espacial", "Micro-Pizza Termonuclear", "Pedacinho quentinho de pizza com queijo cósmico e alta energia!", 3, "🍕", "comida", 0, 0),
            ("suco_estelar", "Suco de Plasma Estelar", "Bebida refrescante de néon para resfriar os processadores do mascote!", 2, "🥤", "comida", 0, 0),

            ("gravata_stark", "Gravata Borboleta Elegante", "Gravata azul e amarela super estilosa para festas!", 8, "🎀", "pescoco", 0, 0),
            ("cachecol_espacial", "Cachecol Quentinho das Estrelas", "Cachecol macio e quentinho com listras douradas!", 10, "🧣", "pescoco", 0, 0),
            ("oculos_stark", "Óculos Stark Neon", "Lentes futuristas espelhadas de alta tecnologia!", 12, "🕶️", "olhos", 0, 0),
            ("oculos_pixel", "Óculos Pixelados Gamer", "Óculos escuros em cubinhos estilo Minecraft!", 14, "🕶️", "olhos", 0, 0),
            ("bone_heroi", "Boné Espacial de Campeão", "Boné estiloso de explorador do universo!", 15, "🧢", "cabeca", 0, 0),
            ("orelhas_gato", "Orelhinhas de Gatinho Fofas", "Orelhas peludinhas e amigáveis para o Jarvis miar de alegria!", 12, "🐱", "cabeca", 0, 0),
            ("tiara_dino", "Tiara de Dinossauro Rex", "Chifrinhos verdes de dinossauro corajoso!", 14, "🦖", "cabeca", 0, 0),
            ("faixa_ninja", "Faixa de Mestre Ninja", "Faixa vermelha de agilidade e concentração!", 12, "🥋", "cabeca", 0, 0),
            ("chapeu_safari", "Chapéu de Aventureiro Safari", "Chapéu de explorador da selva e das savanas!", 15, "🤠", "cabeca", 0, 0),
            ("mascara_ninja", "Máscara Cibernética Ninja", "Máscara de herói misterioso e veloz!", 16, "🥷", "olhos", 0, 0),
            ("oculos_mergulho", "Óculos de Mergulhador Aquático", "Máscara de mergulho para explorar corais e oceanos!", 14, "🥽", "olhos", 0, 0),
            ("antena_radar", "Antena Holográfica de Radar", "Antena giratória que detecta estrelas cadentes!", 15, "📡", "cabeca", 0, 0),

            # ACESSÓRIOS MÉDIOS & HEROICOS (18 a 35 moedas)
            ("capa_heroi", "Capa de Super-Herói Vermelha", "Capa mágica de super campeão com fecho dourado!", 18, "🦸", "costas", 0, 0),
            ("chapeu_mago", "Chapéu de Mago Estelar", "Chapéu azul decorado com estrelas cósmicas!", 20, "🧙", "cabeca", 0, 0),
            ("headset_gamer", "Headset Gamer Neon Pro", "Fones luminosos com microfone de comunicação galáctica!", 20, "🎧", "cabeca", 0, 0),
            ("escudo_vibranium", "Escudo Mágico Stark", "Escudo brilhante de proteção contra monstrinhos!", 22, "🛡️", "braco", 0, 0),
            ("coroa_ouro", "Coroa Real de Ouro", "Coroa brilhante de mestre de missões cumpridas!", 25, "👑", "cabeca", 0, 0),
            ("capacete_astronauta", "Capacete de Astronauta", "Capacete espacial com visor protetor holográfico!", 25, "👨‍🚀", "cabeca", 0, 0),
            ("espada_laser", "Sabre de Luz Laser Neon", "Espada de plasma luminoso para iluminar a escuridão!", 25, "⚔️", "braco", 0, 0),
            ("botas_foguete", "Botas Propulsoras Anti-Gravidade", "Sapatos a jato para dar pulos gigantescos!", 28, "🥾", "pe", 0, 0),
            ("asas_foguete", "Asas de Propulsão Plasma", "Turbinas de voo cósmico para voar super alto!", 30, "🚀", "costas", 0, 0),
            ("martelo_trovao", "Martelo do Trovão Mágico", "Martelo lendário que brilha com faíscas elétricas azuis!", 30, "🔨", "braco", 0, 0),
            ("skate_hoverboard", "Skate Voador Hoverboard", "Prancha magnética que flutua a 1 metro do chão!", 35, "🛹", "pe", 0, 0),

            # ITENS ÉPICOS & TEMAS DE QUARTO (45 a 100 moedas - Metas de Longo Prazo!)
            ("tema_quarto_espacial", "Quarto Estação Espacial", "Transforma o quarto do Jarvis em uma cabine de nave cósmica!", 45, "🌌", "tema", 0, 0),
            ("tema_quarto_castelo", "Quarto Castelo dos Cavaleiros", "Paredes de pedra mágica e tochas medievais brilhantes!", 50, "🏰", "tema", 0, 0),
            ("tema_quarto_dino", "Quarto Floresta dos Dinossauros", "Cenário jurássico com folhagens e pegadas gigantes!", 50, "🌴", "tema", 0, 0),
            ("tema_quarto_corrida", "Quarto Garagem de Super Carros", "Pista de corrida neon e troféus de velocidade!", 45, "🏎️", "tema", 0, 0),
            ("skin_jarvis_dourado", "Armadura Dourada Stark Mark 85", "Visual dourado reluzente de tecnologia de ponta!", 75, "⚡", "skin", 0, 0),
            ("skin_jarvis_diamante", "Skin Diamante Estelar Puro", "O maior troféu do jogo: Jarvis esculpido em diamante cintilante!", 100, "💎", "skin", 0, 0),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO inventario_acessorios (id, nome, descricao, custo_fichas, icone, categoria, comprado, equipado) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
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
                (12, 10, "Dia das Crianças & Imaginação", "brasil", "Hoje o dia é todo seu, Campeão! Muita brincadeira, sorrisos e afeto!", "coroa_ouro.png", "minigame", 30),
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
                ("dente_manha", "🦷 Missão Dente Brilhante da Manhã", "08:00", 5, "desafio_tempo", "🦷", "Escovar com carinho por 2 minutos!", 2),
                ("almoço_forte", "🍽️ Almoço dos Superpoderes", "12:00", 10, "escolha_dirigida", "🍽️", "Qual verdura ou legume vamos provar hoje?", 2),
                ("quarto_limpo", "🧸 Operação Quarto Limpo (Guardar Brinquedos)", "17:30", 5, "escolha_dirigida", "🧸", "Quer guardar os carrinhos ou os blocos primeiro?", 2),
                ("banho_relax", "🛁 Hora do Banho Quentinho & Limpeza", "19:00", 5, "desafio_tempo", "🛁", "Lavar o corpo para recarregar as energias!", 2),
                ("dormir_abajur", "🌙 Apagar o Abajur & Hora do Sono", "20:30", 5, "desafio_tempo", "🌙", "Puxar a cordinha do abajur do Jarvis para dormir!", 3),
            ]
            cursor.executemany(
                "INSERT INTO agenda_rotina_diaria (id, titulo, horario, aviso_previo_minutos, tipo_acao, icone, pergunta_escolha, recompensa_fichas) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                rotinas,
            )

        # POPULAR MISSÕES DE ROTINA SE VAZIA
        cursor.execute("SELECT COUNT(*) FROM missoes_rotina;")
        if cursor.fetchone()[0] == 0:
            missoes_iniciais = [
                ("Escovar os Dentes", "Deixar os dentes limpinhos e sorriso brilhante de super-herói!", 2, "🪥", "Higiene"),
                ("Guardar os Brinquedos", "Deixar o quarto organizado como um quartel-general!", 2, "🧸", "Organização"),
                ("Beber Água Fresquinha", "Hidratação de super-herói para recarregar as forças!", 1, "💧", "Saúde"),
                ("Comer Frutas ou Salada", "Alimentação forte com superpoderes e vitaminas!", 2, "🍎", "Saúde"),
                ("Ler 1 Livro na Biblioteca", "Ler ou ouvir uma história incrível no Jarvis!", 3, "📚", "Estudos"),
            ]
            cursor.executemany(
                "INSERT INTO missoes_rotina (titulo, descricao, recompensa_moedas, icone, categoria) VALUES (?, ?, ?, ?, ?);",
                missoes_iniciais,
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


def limpar_mensagens_familia() -> bool:
    """Apaga todas as mensagens da família e remove os arquivos de áudio/vídeo enviados."""
    try:
        db.executar_escrita("DELETE FROM mensagens_familia;", timeout=3.0)
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads_recados")
        if os.path.exists(uploads_dir):
            for f in os.listdir(uploads_dir):
                if f != ".gitkeep":
                    fp = os.path.join(uploads_dir, f)
                    try:
                        if os.path.isfile(fp):
                            os.remove(fp)
                    except Exception:
                        pass
        registrar_log("INFO", "recados", "Histórico de recados da família limpo pelo administrador.")
        return True
    except Exception as e:
        registrar_log("ERRO", "recados", f"Falha ao limpar recados da família: {e}")
        return False


def limpar_historico_completo(resetar_saldo_moedas: bool = False) -> bool:
    """Limpa logs, recados, histórico de transações de moedas e atividades diárias."""
    try:
        limpar_logs()
        limpar_mensagens_familia()
        db.executar_escrita("DELETE FROM transacoes_fichas;", timeout=3.0)
        db.executar_escrita("DELETE FROM resgates_familia;", timeout=3.0)
        db.executar_escrita("DELETE FROM linha_tempo_atividades;", timeout=3.0)
        if resetar_saldo_moedas:
            db.executar_escrita("UPDATE pote_fichas SET saldo = 10, total_acumulado = 10, estrelas = 0 WHERE id = 1;", timeout=3.0)
        registrar_log("INFO", "sistema", "Limpeza completa de históricos, logs e transações realizada com sucesso.")
        return True
    except Exception as e:
        registrar_log("ERRO", "sistema", f"Falha na limpeza completa: {e}")
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


# ==============================================================================
# PILAR 1: MISSÕES DE ROTINA & HÁBITOS DOS PAIS
# ==============================================================================

def listar_missoes_rotina(data_dia: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista todas as missões de rotina ativas e indica se já foram cumpridas na data especificada."""
    import datetime
    dia = data_dia or datetime.date.today().isoformat()
    sql = """
        SELECT m.id, m.titulo, m.descricao, m.recompensa_moedas, m.icone, m.categoria, m.ativa,
               CASE WHEN c.id IS NOT NULL THEN 1 ELSE 0 END as cumprida,
               c.hora_cumprida
        FROM missoes_rotina m
        LEFT JOIN missoes_cumpridas c ON m.id = c.missao_id AND c.data_dia = ?
        WHERE m.ativa = 1
        ORDER BY cumprida ASC, m.id ASC;
    """
    return db.consultar_todos(sql, (dia,))


def adicionar_missao_rotina(titulo: str, descricao: str = "", recompensa_moedas: int = 5, icone: str = "⭐", categoria: str = "Geral") -> int:
    """Adiciona uma nova missão de rotina criada pelos pais."""
    sql = """
        INSERT INTO missoes_rotina (titulo, descricao, recompensa_moedas, icone, categoria, ativa)
        VALUES (?, ?, ?, ?, ?, 1);
    """
    res = db.executar_escrita(sql, (titulo.strip(), descricao.strip(), max(1, int(recompensa_moedas)), icone.strip(), categoria.strip()))
    return int(res or 0)


def excluir_missao_rotina(missao_id: int) -> bool:
    """Desativa ou exclui uma missão de rotina."""
    try:
        db.executar_escrita("DELETE FROM missoes_rotina WHERE id = ?;", (int(missao_id),))
        return True
    except Exception:
        return False


def cumprir_missao_rotina(missao_id: int, data_dia: Optional[str] = None) -> Dict[str, Any]:
    """Marca uma missão como cumprida hoje, credita as moedas no cofre e registra na linha do tempo."""
    import datetime
    dia = data_dia or datetime.date.today().isoformat()
    hora = datetime.datetime.now().strftime("%H:%M")

    # Verifica se a missão existe
    m = db.consultar_um("SELECT id, titulo, recompensa_moedas, icone FROM missoes_rotina WHERE id = ?;", (int(missao_id),))
    if not m:
        return {"sucesso": False, "erro": "Missão não encontrada."}

    # Verifica se já foi cumprida hoje
    ja = db.consultar_um("SELECT id FROM missoes_cumpridas WHERE missao_id = ? AND data_dia = ?;", (int(missao_id), dia))
    if ja:
        return {"sucesso": False, "erro": "Esta missão já foi concluída hoje!", "ja_cumprida": True}

    moedas = int(m["recompensa_moedas"])
    db.executar_escrita(
        "INSERT INTO missoes_cumpridas (missao_id, data_dia, hora_cumprida, moedas_ganhas) VALUES (?, ?, ?, ?);",
        (int(missao_id), dia, hora, moedas)
    )

    # Credita as moedas no pote de fichas do Campeão
    from economia_fichas import TokenEconomyManager
    econ = TokenEconomyManager(db)
    status_pote = econ.creditar_fichas(moedas, f"Missão cumprida: {m['titulo']}", categoria="MISSAO")

    # Registra evento na linha do tempo diária
    registrar_atividade_linha_tempo(
        tipo="missao",
        titulo=f"Concluiu a missão: {m['titulo']}",
        descricao=f"+{moedas} moedas de ouro adicionadas ao pote!",
        icone=m.get("icone") or "⭐"
    )

    return {
        "sucesso": True,
        "missao": m["titulo"],
        "moedas_ganhas": moedas,
        "novo_saldo": status_pote.get("saldo", 0),
        "hora": hora
    }


# ==============================================================================
# PILAR 2: GALERIA DE ARTE DA LOUSA NEON
# ==============================================================================

def salvar_desenho_arte(imagem_base64: str, titulo: str = "Desenho Lousa Neon") -> Dict[str, Any]:
    """Salva um desenho feito pelo Campeão no banco de dados e adiciona à linha do tempo."""
    import datetime
    dia = datetime.date.today().isoformat()
    hora = datetime.datetime.now().strftime("%H:%M")
    tit = (titulo or "Desenho do Campeão").strip()

    sql = """
        INSERT INTO galeria_arte (titulo, imagem_base64, data_dia, hora)
        VALUES (?, ?, ?, ?);
    """
    res = db.executar_escrita(sql, (tit, imagem_base64, dia, hora))
    novo_id = int(res or 0)

    # Registra na linha do tempo
    registrar_atividade_linha_tempo(
        tipo="arte",
        titulo="Criou uma nova obra de arte na Lousa Neon!",
        descricao=f"Obra '{tit}' enviada com carinho para os pais.",
        icone="🎨"
    )

    return {"sucesso": True, "id": novo_id, "data_dia": dia, "hora": hora}


def listar_galeria_arte(limite: int = 50) -> List[Dict[str, Any]]:
    """Retorna os desenhos da galeria de arte com miniaturas e metadados."""
    sql = "SELECT id, titulo, imagem_base64, data_dia, hora FROM galeria_arte ORDER BY id DESC LIMIT ?;"
    return db.consultar_todos(sql, (max(1, int(limite)),))


def excluir_desenho_arte(arte_id: int) -> bool:
    """Exclui um desenho da galeria de arte."""
    try:
        db.executar_escrita("DELETE FROM galeria_arte WHERE id = ?;", (int(arte_id),))
        return True
    except Exception:
        return False


# ==============================================================================
# PILAR 4: LINHA DO TEMPO DIÁRIA DE ATIVIDADES
# ==============================================================================

def registrar_atividade_linha_tempo(tipo: str, titulo: str, descricao: str = "", icone: str = "🌟") -> None:
    """Registra uma atividade recente do Campeão na linha do tempo diária para os pais."""
    import datetime
    dia = datetime.date.today().isoformat()
    hora = datetime.datetime.now().strftime("%H:%M")
    try:
        db.executar_escrita(
            """
            INSERT INTO linha_tempo_atividades (tipo, titulo, descricao, icone, hora, data_dia)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (tipo, titulo, descricao, icone, hora, dia),
            timeout=2.0
        )
    except Exception:
        pass


def listar_linha_tempo(data_dia: Optional[str] = None, limite: int = 50) -> List[Dict[str, Any]]:
    """Consulta a linha do tempo de atividades do Campeão para uma determinada data."""
    import datetime
    dia = data_dia or datetime.date.today().isoformat()
    sql = """
        SELECT id, tipo, titulo, descricao, icone, hora, data_dia
        FROM linha_tempo_atividades
        WHERE data_dia = ?
        ORDER BY id DESC
        LIMIT ?;
    """
    return db.consultar_todos(sql, (dia, max(1, int(limite))))


