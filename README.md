# 🚀 J.A.R.V.I.S. Kids OS v3.0 — Stark Educational System (Para Kaleo Noah)

Sistema operacional educativo, companheiro emocional e assistente gamificado estilo **JARVIS do Homem de Ferro**, projetado sob medida para o netbook **Acer Aspire One 532h / Asus EeePC** (`Intel Atom N450 1.66 GHz`, `2 GB RAM`, `SSD`, GPU `Intel GMA 3150`, tela `1024x600`), rodando sobre **antiX Linux** ou **Windows**.

Projetado sob princípios rigorosos de **engenharia de software para hardware ultra-restrito**, consumindo **menos de 15 MB de RAM no backend** e garantindo que o processador Atom de núcleo único nunca trave em 100%.

---

## ⚡ Parte 1: Engenharia de Performance & Hardware Restrito

### 1. Servidor Web Ultraleve com Microdot (< 15 MB de RAM)
- O backend foi migrado de frameworks pesados para o **Microdot**, um micro-framework assíncrono de pegada de memória mínima.
- **Consumo real medido com `tracemalloc`:** Apenas **8.86 MB de RAM** (pico de **10.45 MB**), rodando com folga muito abaixo do teto de 30 MB.
- Servido nativamente na porta `http://127.0.0.1:8000`.

### 2. SQLite em Modo WAL & Arquitetura Single-Writer / Multi-Reader
- Para evitar a temida falha `SQLITE_BUSY` e o congelamento do disco/SSD por acessos simultâneos, todas as conexões SQLite injetam no momento da abertura:
  ```sql
  PRAGMA journal_mode = WAL;     -- Write-Ahead Logging: leituras e escritas não bloqueiam umas às outras
  PRAGMA synchronous = NORMAL;   -- Reduz chamadas excessivas de fsync ao disco
  PRAGMA temp_store = MEMORY;    -- Força tabelas temporárias e ordenações na memória RAM
  PRAGMA busy_timeout = 5000;    -- Espera até 5 segundos em caso de concorrência antes de falhar
  ```
- **Fila Sequencial Assíncrona (`banco_dados.py`):** As rotas de escrita enfileiram tarefas em uma `queue.Queue`. Um único Worker em segundo plano (`SQLiteSingleWriter`) consome os dados e grava de forma estritamente sequencial. Múltiplas rotas podem ler concorrentemente com conexões independentes.

### 3. Gestão Defensiva de Memória RAM (Teto de 2 GB)
- **Paginação com Geradores (`yield`):** Consultas de histórico (logs, fichas, mensagens) usam `LIMIT` e `OFFSET`, transmitindo registros através de geradores linha por linha sem criar arrays gigantes na RAM.
- **Coleta Ativa (`gc.collect()`):** Liberação ativa de memória e variáveis de sessão na transição entre jogos e módulos.
- **Mídia sob Demanda:** Imagens, sons e áudios são transmitidos via fluxo contínuo do disco (`send_file(..., stream=True)`), nunca pré-carregados na memória.

### 4. Inteligência Artificial e Voz Terceirizadas
- **Zero modelos neurais pesados locais:** Nenhum modelo Whisper, PyTorch ou LLM local roda no Atom.
- O reconhecimento e síntese de voz (STT/TTS) são terceirizados para APIs em nuvem (**Google AI Studio / Gemini**, **Edge-TTS**, **OpenCode LAN** ou a **Web Speech API** nativa do navegador), garantindo CPU a 0% em repouso.

---

## 🧸 Parte 2: Psicologia Infantil, Rotinas e Conexão Paterna

### 1. Bichinho Virtual Estilo Pou (`jarvis_pet_status.py` / POUPY)
- **4 Barras Vitais:** Higiene, Alimentação, Diversão e Energia com decaimento suave ao longo do tempo.
- **Interação Tátil:** Carinho ao clicar/segurar no mascote, sabonete/chuveiro para higiene, frutinhas saudáveis e abajur interativo para o sono reparador.
- **Humores Dinâmicos:** `FELIZ`, `COM_FOME`, `SUJO`, `CANSADO`, `TRISTE` refletidos nas expressões visuais 2D do mascote.

### 2. Rotinas Diárias B-bot & Protocolo Anti-Conflito (`rotinas_companheiro.py`)
- Em vez de ordens, missões cooperativas gamificadas:
  - **Missão Dente Brilhante:** Cronômetro interativo de 2 minutos com barra visual de escovação.
  - **Operação Quarto Limpo:** Desafio de contagem regressiva (3 a 5 minutos) para guardar brinquedos.
  - **Aviso Preventivo de 5 Minutos:** Notificação afetuosa antes do fim do tempo de brincar ou do cinema.
  - **Escolhas Dirigidas:** "Você quer calçar o sapato azul ou o vermelho agora?" promovendo autonomia sem atrito.

### 3. Economia de Fichas & O "Pote do Tesouro" (`economia_fichas.py`)
- Cada rotina concluída rende moedas/estrelas creditadas instantaneamente.
- **Pote Virtual:** Animação imediata com o pote enchendo na tela.
- **Loja de Privilégios Reais:** Troca de moedas por momentos especiais com os pais (passeio no parque, piquenique, sessão de cinema em família) e acessórios virtuais.

### 4. Inteligência Emocional SEL & Autorregulação (`academia_emocoes_tech.py`)
- **Mini-Histórias:** Situações infantis reais onde a criança identifica o sentimento do amigo.
- **Florzinha da Calma:** Exercício de respiração vagal guiada: "Cheirar a florzinha pelo nariz" (4s) e "Soprar a velinha pela boca" (4s) para momentos de agitação ou frustração.

### 5. Funções Executivas & Cognição (`cognicao_jogos.py`)
- **Desafio do Semáforo (Controle Inibitório):** Toque rápido quando o sinal está verde; pare imediato quando o sinal fica vermelho.
- **Baú do Conhecimento (Repetição Espaçada de Leitner):** Flashcards educativos em 3 caixas progressivas (diária, a cada 2 dias, semanal), consolidando letras, números, cores e animais.

### 6. Educação Alimentar & Semáforo Nutricional (`educacao_alimentar.py`)
- **Prato Colorido dos Superpoderes:** Estimula comer alimentos de cores variadas (verde para força, vermelho para coração forte, laranja para visão de herói).
- **Semáforo dos Alimentos:** Alimentos livres (verde), moderados (amarelo) e doces ocasionais (vermelho), com validação remota de refeição pelos pais.

### 7. Clima, Estações & Cuidados Pessoais (`clima_estacoes.py`)
- Consulta automática da API gratuita **Open-Meteo** (sem necessidade de chaves).
- **Cache de 120 minutos no SQLite:** Poupando conexão e processamento.
- Dicas práticas e carinhosas para a criança (levar guarda-chuva na chuva, beber água no calor, vestir casaco no frio).

### 8. Presença Paterna & Mensagens Remotas (`mensagens_pais.py`)
- Mensagens secretas enviadas pelos pais via celular que surgem com destaque afetuoso na tela do Kaleo.
- **Rastreamento em Tempo Real:** O painel dos pais exibe o status exato: `ENVIADA` ➔ `RECEBIDA` ➔ `ABERTA (às HH:MM:SS)`.
- **SOS Intervenção:** O pai pode disparar do celular uma pausa com tela de abraço, música de calma ou chamada para refeição.

### 10. Estudo Lúdico de Idiomas (Inglês 🇺🇸 e Espanhol 🇪🇸 — `estudo_idiomas.py`)
- **Cards Falantes Interativos:** A criança vê a ilustração colorida, o nome em português, a palavra em destaque com guia fonético (ex: *"Dóg"*, *"Pê-rro"*, *"Uan"*) e ouve a pronúncia nativa com a Web Speech API (`en-US` e `es-ES`).
- **Mãozinhas & Dedos (Números de 1 a 10):** Ensinamento concreto mostrando os dedinhos das mãos levantados (ex: 1 dedinho = *One / Uno*, 5 dedinhos = *Five / Cinco*, duas mãos abertas = *Ten / Diez*).
- **Categorias Cotidianas:** Animais, Cores, Mãozinhas & Números, Frutinhas & Comidas, Saudações de Afeto e Família Querida.
- **Mini-Quiz do Jarvis ("Adivinhe a Palavra"):** O Jarvis pergunta com áudio (*"Where is the Cat?"* ou *"¿Dónde está el Perro?"*) e a criança toca na carta correta entre 3 opções coloridas.
- **Reforço Imediato:** Cada acerto credita **+5 moedas para o Pote do Tesouro** com festa visual de confetes e estrelas!

### 11. Atualização em 1 Clique & Persistência do Sistema
- **Script `atualizar_sistema.sh`:** Atualiza o repositório do GitHub (`git pull`) e reinicia os serviços sem complicações.
- **Watchdog `iniciar_servicos.sh`:** Monitora o processo e reinicia automaticamente em caso de encerramento, garantindo disponibilidade contínua.
- **Monitor de Bateria:** Alerta amigável no netbook quando a bateria estiver baixa (< 20%) ou 100% cheia para desconectar da tomada e proteger as células.

---

## 🕹️ Como Iniciar o Sistema

### No Windows
1. Dê um duplo-clique em:
   ```cmd
   iniciar_web_windows.bat
   ```
2. O servidor Microdot ultraleve iniciará na porta `8000` e o navegador abrirá automaticamente em `http://127.0.0.1:8000`.
3. O painel dos pais estará disponível em `http://127.0.0.1:8000/pais`.

### No Netbook Acer / Asus One (antiX Linux)
1. Instale as dependências com o script otimizado:
   ```bash
   bash instalar_antix_kiosk.sh
   ```
2. Inicie o modo quiosque de tela cheia:
   ```bash
   bash iniciar_web_kiosk.sh
   ```
3. Para ativar a inicialização automática no boot com proteção de tela e atalhos bloqueados:
   ```bash
   bash configurar_boot_automatico.sh
   ```

---

## 📱 Painel dos Pais (`/pais`)

Acessível por qualquer smartphone, tablet ou computador na mesma rede Wi-Fi (`http://[IP-DO-NETBOOK]:8000/pais`):
- **Envio de Mensagens com Leitura Confirmada:** Acompanhe quando seu filho abriu o bilhete.
- **Pote do Tesouro:** Gerenciamento de fichas conquistadas e aprovação de resgates da vida real.
- **Controle de Cinema & Mídia:** Adicione minutos de bônus ou pause a tela para o almoço.
- **SOS Intervenção Imediata:** Acione respiração guiada, pausa de descanso ou hora da comidinha com um toque.
- **Diagnóstico em Tempo Real & Logs de Falhas:** Visualizador de eventos, erros e alertas do sistema (banco SQLite, IA, voz TTS, bateria e memória) com filtros dinâmicos, busca por palavra e limpeza com 1 clique.
- **Atualização do Sistema:** Botão remoto para baixar atualizações do GitHub e reiniciar o Jarvis.

---

## 🛡️ Licença e Dedicação

Desenvolvido com amor, carinho e dedicação paterna para **Kaleo Noah**, unindo a mais avançada psicologia do desenvolvimento infantil à engenharia de software de alta eficiência.
