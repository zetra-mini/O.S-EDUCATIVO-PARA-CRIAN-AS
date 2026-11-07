# 🚀 J.A.R.V.I.S. Kids OS v3.2 — Stark Educational System (Para Kaleo Noah)

Sistema operacional educativo, companheiro emocional e assistente gamificado estilo **JARVIS do Homem de Ferro**, projetado sob medida com princípios de engenharia de software de alta eficiência para netbooks modestos e computadores com recursos restritos (modelo original **Acer Aspire One / Asus Eee PC** com `Intel Atom 1.6 GHz`, `1 GB a 2 GB RAM`, tela `1024x600`), expandido para arquitetura **multiplataforma universal** compatível com **Linux Kiosk**, **Windows Desktop**, **macOS (.app)** e **Android (.apk)**!

---

## 🌟 Novidades da Versão 3.2

### 🗣️ 1. Fonoaudiologia & Dicção do Super-Herói (17º Jogo Oficial)
- **66 Desafios Fonoaudiológicos Completos:**
  - **24 Desafios de Sílabas & Sons Desafiadores:** Trabalho minucioso de articulação infantil cobrindo fonemas R brando na ponta da língua (*Arara*, *Jacaré*, *Coração*, *Careta*, *Pirata*), R forte na garganta (*Rato*, *Robô*, *Rei*, *Rua*, *Rádio*), encontros consonantais com R (*Prato*, *Trator*, *Brasil*, *Dragão*, *Cravo*, *Fruta*, *Grade*), encontros consonantais com L (*Planeta*, *Flauta*, *Globo*, *Clube*, *Blusa*), sons de sibilantes e chiados (*Sapo*, *Sorvete*, *Zebra*, *Chocolate*, *Janela*, *Xícara*) e dígrafos nasais/palatais (*Coelho*, *Golfinho*).
  - **30 Palavras Poderosas & Desafios Gigantes:** Palavras polissílabas infantis de 3 a 7 sílabas, incluindo o lendário campeão **Paralelepípedo** (7 sílabas!), *Astronauta*, *Borboleta*, *Dinossauro*, *Helicóptero*, *Hipopótamo*, *Rinoceronte*, *Escavadeira*, *Submarino*, *Tartaruga*, *Camaleão*, *Espetacular*, *Super-Herói*, *Constelação*, *Transformação*, *Bicicleta*, *Elefante*, *Arco-Íris*, *Computador*, *Telefone*, *Microscópio*, *Relâmpago*, *Joaninha*, *Melancia*, *Paraquedas*, *Tesouro*, *Foguete*, *Castelo*, *Espada* e *Aventura*.
  - **12 Trava-Línguas Divertidos:** Treino de agilidade e ritmo articulatório (*O rato roeu*, *Três pratos de trigo*, *Sapo no saco*, *Doce mais doce*, *Aranha e a rã*, *Sabiá assobiador*, *Pinga a pia*, *O tempo*, *Mafagafos*, *Farofa fofa*, *Bote a bota*, *Peito de Pedro*).
- **✨ Botão: "Nova Palavra Surpresa do Jarvis! 🤖":**
  - O mascote Jarvis escolhe aleatoriamente uma palavra nova da cartola sob demanda, disparando arpeggio musical, chuva de corações/estrelas e expressão feliz nos olhinhos do robô.
  - O robô fala com empolgação: *"Bip bip, super-herói Kaleo! O Jarvis preparou uma palavra mágica nova para você treinar a dicção: [SÍLABAS]! [DICA DA BOQUINHA] Vamos falar juntos?"*.
- **🔉 Botão: "Sílaba por Sílaba":** Pronúncia pausada com cadência fonoaudiológica para a criança imitar cada pedacinho com calma.
- **🎙️ Treino Interativo com Moedas Reais:** A criança treina a fala e recebe elogio do robô com **+5 moedas reais** creditadas no Pote do Tesouro.
- **Comando de Voz Integrado:** Diga *"Jarvis me mostra uma palavra nova"*, *"Jarvis palavra mágica"* ou *"Jarvis treinar dicção"* e o jogo abre sorteando a palavra na hora!

### 🎬 2. Gestão de Tempo de Cinema & Orientação Segura
- **🚫 Botão de Travar / Zerar Cinema nas Ações Rápidas:** Os pais podem interromper ou revogar instantaneamente qualquer tempo residual de vídeo diretamente pelo painel `/pais` via `/api/admin/media/zerar`.
- **Teto Máximo para Bônus de Mídia:** O bônus concedido pelos pais possui teto protetivo (máximo de 45 minutos), evitando acúmulos infinitos de tela.
- **Diálogo Interativo por Voz:** Quando o cinema é liberado por horário ou bônus, o Jarvis anuncia por voz e pergunta gentilmente se a criança deseja assistir agora ou continuar brincando.

### 🛡️ 3. Filtros Rígidos de Segurança Infantil (Child-Safe Guardrails)
- **Sanitização de Respostas:** O módulo `jarvis_brain.py` aplica filtros estritos de segurança infantil que barram termos violentos, inapropriados ou assustadores, além de suprimir alucinações de blocos de código e markdown técnico.
- **Proteção Canônica de Path Traversal:** Bloqueio `403 Forbidden` na rota de estáticos para tentativas de fuga de diretório (`/static/../../`).
- **Rate Limit & Limite de Upload:** Uploads de vídeo e áudio dos pais limitados a 20MB para preservar a memória RAM do netbook contra travamentos (OOM).

### 📦 4. Multiplataforma Universal & GitHub Actions CI/CD (.apk e .app)
- **CI/CD Automatizado:** Compilação em nuvem de todos os pacotes oficiais a cada push ou tag de versão no GitHub Actions:
  - 📱 **Android (.apk):** Aplicativo nativo em modo Fullscreen Landscape para tablets e celulares infantis (`deploy/android_app/`).
  - 🍏 **macOS (.app e .app.zip):** Application Bundle executável para Mac com inicializador Python embutido (`deploy/macos_app/`).
  - 🐧 **Debian Kiosk (.deb):** Pacote instalável com 1 clique para antiX Linux, Raspberry Pi OS e Ubuntu.
  - 🐧 **Linux Standalone (.tar.gz):** Pacote portátil de quiosque para netbooks modestos.
  - 🪟 **Windows Desktop (.zip):** Versão portátil completa com inicializador `.bat` para qualquer PC Windows.
  - 📱 **PWA Móvel dos Pais:** Progressive Web App instalável no smartphone com Service Worker offline e push notifications.

---

## 📸 Capturas de Tela do Sistema em Execução

| 🤖 Tela Principal — Sala de Brincar do Robô Jarvis | 🎮 Central de Jogos & Estudos Paginada |
| :---: | :---: |
| ![HUD Jarvis](docs/screenshots/jarvis_sala_brincar.jpg) | ![Menu de Jogos e Estudos](docs/screenshots/menu_jogos_estudos.jpg) |
| *Mascote Jarvis interativo com clima, economia de moedas, cômodos e status de bateria do notebook* | *17 Jogos infantis paginados em Grid 2x2 com botões táteis grandes e ZERO barras de rolagem* |

| 🗣️ Fonoaudiologia & Dicção do Super-Herói | 📚 Biblioteca Mágica de Virtudes & Histórias |
| :---: | :---: |
| ![Fonoaudiologia](docs/screenshots/menu_jogos_estudos.jpg) | ![Biblioteca Mágica](docs/screenshots/biblioteca_magica.jpg) |
| *66 desafios fonoaudiológicos com sílabas neon gigantes, botão de palavra surpresa do Jarvis e fala sílaba por sílaba* | *Livros infantis com virtudes, moral da história e gerador de histórias com IA* |

---

## 🖥️ Especificações de Hardware & Requisitos do Sistema

O **J.A.R.V.I.S. Kids OS** nasceu com uma premissa de engenharia intransigente: **dar vida útil e propósito nobre a computadores antigos e modestos**, transformando um netbook esquecido em um superassistente educativo com inteligência artificial para o aprendizado e desenvolvimento de uma criança.

### 🎯 Hardware Alvo Original de Desenvolvimento
O sistema foi concebido, calibrado e testado originalmente para a linha de netbooks ultra-compactos:
- **Modelo de Referência Principal:** Netbook **Acer Aspire One (532h / D250 / D255)** e **Asus Eee PC (1005 / 1015)**.
- **Processador (CPU):** Intel Atom N450 / N270 / D2500 (1.60 GHz a 1.66 GHz, 1 Núcleo / 2 Threads, x86/x64).
- **Memória RAM:** 1 GB a 2 GB DDR2 / DDR3.
- **Gráficos (GPU):** Intel GMA 3150 / Intel 945GSE integrada (aceleração gráfica 2D básica).
- **Armazenamento:** HDD ou SSD SATA de 160 GB, ou cartão de memória SD.
- **Tela e Resolução:** 10.1 polegadas WSVGA (1024 x 600 pixels) com preenchimento total e modo quiosque tela cheia.
- **Sistema Operacional Recomendado:** **antiX Linux 23/24 (32 bits ou 64 bits)** ou **Windows 7/10 Home**.

---

### 📊 Tabela de Requisitos de Sistema (Mínimos vs. Recomendados)

| Componente | Requisitos Mínimos (Netbook Acer / Asus / PCs Antigos) | Requisitos Recomendados (PCs / Notebooks Modernos) |
| :--- | :--- | :--- |
| **Processador (CPU)** | Intel Atom 1.6 GHz, Intel Celeron antigo, AMD E-Series ou qualquer processador x86/x64 de 1 núcleo | Intel Core i3 / i5, AMD Ryzen 3 / 5 ou Celeron moderno quad-core |
| **Memória RAM** | **1 GB de RAM** *(o backend Microdot consome apenas ~12 a 25 MB de RAM)* | **4 GB a 8 GB de RAM** *(necessário para rodar IA local com Ollama)* |
| **Armazenamento** | **500 MB livres** em disco ou cartão SD | **4 GB a 10 GB livres** *(para pesos dos modelos locais de IA)* |
| **Resolução de Tela** | **1024 x 600 pixels** (10.1") com preenchimento total responsivo sem scrollbars | **1366 x 768**, **1920 x 1080 (Full HD)** ou superior |
| **Áudio & Microfone** | Microfone integrado e alto-falantes estéreo / saída P2 | Microfone USB com cancelamento de ruído e caixas de som |
| **Conexão de Rede** | Wi-Fi 802.11 b/g/n (para síntese de voz neural e APIs na nuvem) | Conexão Wi-Fi ou Ethernet estável |
| **Sistemas Operacionais** | **antiX Linux** (32/64 bits), **Debian minimal**, **Raspberry Pi OS**, **Windows 7/10/11**, **Android**, **macOS** | Windows 10/11, Ubuntu/Debian, Fedora, macOS Sonoma/Sequoia, Android 10+ |

---

## 📦 Matriz de Pacotes & Downloads Oficiais (GitHub Releases)

Os arquivos compilados são gerados automaticamente pelo [GitHub Actions CI/CD](https://github.com/zetra-mini/O.S-EDUCATIVO-PARA-CRIAN-AS/actions) e disponibilizados na aba de **Releases**:

| Formato | Plataforma Alvo | Arquivo de Download | Como Instalar / Executar |
| :--- | :--- | :--- | :--- |
| 🐧 **.deb** | Debian / antiX / Ubuntu / Raspberry Pi OS | `jarvis-kids-os_2.6.0.deb` | `sudo dpkg -i jarvis-kids-os_2.6.0.deb` |
| 📦 **.tar.gz** | Linux Kiosk Standalone (Netbook Atom) | `jarvis-kids-os-2.6.0-linux-desktop.tar.gz` | `tar -xzf jarvis-kids-os-*.tar.gz && ./iniciar_jarvis_linux.sh` |
| 🪟 **.zip** | Windows 7 / 10 / 11 (Desktop) | `jarvis-kids-os-2.6.0-windows-desktop.zip` | Extrair e clicar em `iniciar_jarvis_windows.bat` |
| 📱 **.apk** | Android Celulares & Tablets Infantis | `jarvis-kids-os-2.6.0-android.apk` | Instalar no Android e permitir microfone |
| 🍏 **.app** | macOS (Intel & Apple Silicon M1/M2/M3) | `jarvis-kids-os-2.6.0-macos.app.zip` | Extrair e abrir `JARVIS-Kids-OS.app` |
| 📱 **PWA** | Smartphone dos Pais (iOS / Android) | Acesso direto via navegador | Acessar `/pais` e clicar em *Adicionar à Tela Inicial* |

---

## ⚡ Engenharia de Performance & Hardware Restrito

### 1. Servidor Web Ultraleve com Microdot (< 15 MB de RAM)
- O backend opera sobre o **Microdot**, micro-framework assíncrono de pegada de memória mínima.
- **Consumo real medido:** Apenas **9 a 14 MB de RAM**, operando com folga muito abaixo do teto de 30 MB.
- Servido nativamente na porta `http://127.0.0.1:8000`.

### 2. SQLite em Modo WAL & Arquitetura de Acesso Seguro
- Para evitar a falha `SQLITE_BUSY` e o congelamento do disco/SSD por acessos simultâneos, todas as conexões SQLite injetam no momento da abertura:
  ```sql
  PRAGMA journal_mode = WAL;     -- Write-Ahead Logging: leituras e escritas não bloqueiam umas às outras
  PRAGMA synchronous = NORMAL;   -- Reduz chamadas excessivas de fsync ao disco
  PRAGMA temp_store = MEMORY;    -- Força tabelas temporárias e ordenações na memória RAM
  PRAGMA busy_timeout = 5000;    -- Espera até 5 segundos em caso de concorrência antes de falhar
  ```

### 3. Eliminação Absoluta de Áudio sobre Áudio
- Toda emissão de voz neural (`speak()`), chime sonoro ou música aciona previamente `pararTodosAudiosESpeech()`, cancelando requisições TTS em andamento e silenciando sintetizadores do navegador para garantir que nunca ocorra sobreposição de falas.

### 4. Zero Scrollbars & Paginação Tátil
- Todas as interfaces (HUD, Loja, Biblioteca, Prato dos Campeões, Central de 17 Jogos e Academia de Dicção) utilizam containers flexbox com `overflow: hidden; max-height: calc(100vh - 72px)` e navegação anterior/próxima em botões de alta visibilidade, eliminando completamente barras de rolagem.

---

## 🎮 Catálogo dos 17 Jogos & Atividades Educativas

1. **🎨 Laboratório de Pintura Neon:** Lousa artística com pincéis coloridos e salvamento de desenhos.
2. **🎵 Laboratório Musical Stark:** Teclado Dó-Ré-Mi, bateria de ritmo e músicas infantis guiadas.
3. **🔢 Desafio dos Dedinhos:** Matemática visual e contagem de 1 a 10 com mãozinhas animadas.
4. **🔤 Ler & Escrever (Método Fônico):** Sons de cada letra do alfabeto e escrita na lousa neon.
5. **🌍 Idiomas Mágicos:** Cartões falantes em Português, Inglês e Espanhol.
6. **🚦 Semáforo & Atenção:** Treino de autorregulação e reflexos estilo "luz verde, luz vermelha".
7. **🌸 Centro das Emoções & Flor da Calma:** Identificação de sentimentos e respiração guiada.
8. **🍎 Prato dos Super Campeões:** Educação alimentar com divisão dos 4 grupos de nutrientes.
9. **🧼 Academia de Higiene Pessoal:** 4 missões práticas de autocuidado (mãos, dentes, banho e unhas).
10. **💻 Academia Tech & Treino do Mouse:** Foguete (scroll up), Submarino (scroll down), mira e clique.
11. **🇧🇷 Festas & Datas Comemorativas do Brasil:** Celebrações culturais brasileiras no calendário.
12. **🪢 Labirinto Espacial:** Coordenação motora fina e raciocínio lógico em labirintos estelares.
13. **🧩 Jogo da Memória dos Heróis:** Cartas mágicas com pares de personagens e virtudes.
14. **🪐 Cores e Formas Espaciais:** Geometria lúdica com círculos, quadrados, triângulos e estrelas.
15. **🧮 Quebra-Cabeça Numérico:** Ordenação de peças numeradas com estímulo cognitivo.
16. **🗃️ Baú Leitner de Repetição Espaçada:** Memorização inteligente de fatos e conceitos.
17. **🗣️ Fonoaudiologia & Dicção do Super-Herói:** 66 desafios de fala com sílabas neon, dica da boquinha, fala pausada e sorteio de palavras mágicas pelo robô Jarvis!

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.10 ou superior
- Navegador moderno (Chromium, Chrome, Edge ou Firefox)

### Instalação Rápida
```bash
git clone https://github.com/zetra-mini/O.S-EDUCATIVO-PARA-CRIAN-AS.git
cd O.S-EDUCATIVO-PARA-CRIAN-AS
pip install -r requirements.txt
```

### Inicialização
```bash
# Inicia o servidor local
python run_server.py 8000
```
- Acesse a interface da criança: `http://localhost:8000`
- Acesse o painel dos pais: `http://localhost:8000/pais`

---

## 📱 Painel dos Pais (`/pais`)

Acessível por qualquer smartphone, tablet ou computador na mesma rede Wi-Fi (`http://[IP-DO-NETBOOK]:8000/pais`):
- **Ações Rápidas com 1 Toque:** Liberar ou travar cinema, pausar para refeição, acionar alarme de escovar dentes ou guardar brinquedos.
- **Pote do Tesouro:** Gerenciamento do saldo de moedas e aprovação de resgates da vida real.
- **Mensagens & Recados com Áudio/Vídeo:** Envio de bilhetes carinhosos com confirmação de leitura pela criança.
- **Configurações de Voz Neural:** Seleção entre 11 vozes neurais brasileiras com prioridade total no sistema.
- **Geografia Ensinável:** Configuração de cidade, estado e país para ensinar à criança sua localização no planeta Terra.
- **Logs & Diagnóstico em Tempo Real:** Monitoramento de eventos, bateria do notebook e integridade do banco SQLite.

---

## 🛡️ Licença e Dedicação

Desenvolvido com amor, carinho e dedicação paterna para **Kaleo Noah**, unindo a mais avançada psicologia do desenvolvimento infantil à engenharia de software de alta eficiência.
