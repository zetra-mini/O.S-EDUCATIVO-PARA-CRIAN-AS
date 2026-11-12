# 🚀 J.A.R.V.I.S. Kids OS v3.7.0 — Edição Stark Edge AI (TensorFlow Lite & Alta Fluidez)

Sistema operacional educativo, companheiro emocional e assistente gamificado estilo **JARVIS do Homem de Ferro**, projetado sob medida com princípios de engenharia de software de alta eficiência para netbooks modestos e computadores com recursos restritos (modelo original **Acer Aspire One / Asus Eee PC** com `Intel Atom 1.6 GHz`, `1 GB a 2 GB RAM`, tela `1024x600`), expandido para arquitetura **multiplataforma universal** compatível com **Linux Kiosk**, **Windows Desktop**, **macOS (.app)** e **Android (.apk autônomo offline)**!

---

## 📸 Galeria Visual do Sistema em Execução (Screenshots Oficiais 1024x600)

Telas reais capturadas diretamente do sistema em execução na resolução nativa do netbook (1024x600):

| 🤖 1. HUD Principal — Sala de Comando do Robô Jarvis | 🦸‍♂️ 2. Quartel-General das Missões do Herói |
| :---: | :---: |
| ![HUD Jarvis](docs/screenshots/01_hud_jarvis_sala_brincar.png) | ![Missões do Herói](docs/screenshots/02_missoes_do_heroi.png) |
| *Mascote Jarvis interativo em tela desobstruída e limpa (sem modais superiores intrusivos), clima em tempo real, moedas do Pote do Tesouro, bateria e barra inferior com Jogos, Histórias e Loja.* | *Quartel-General de Missões reformulado com barra de conquista diária de super-herói, abas de filtro (Todas, Para Fazer, Concluídas) e atalhos rápidos.* |

| 📚 3. Biblioteca Mágica de Histórias (Estante) | 🌟 4. Tela de Conquista & Celebração do Livro |
| :---: | :---: |
| ![Biblioteca Mágica](docs/screenshots/03_biblioteca_historias.png) | ![Celebração do Livro](docs/screenshots/04_leitor_livro_celebracao.png) |
| *Estante de livros ilustrados infantis organizados com capas táteis, temas pedagógicos de virtudes, valores e gerador de histórias com IA.* | *Tela de Conquista com chuva de confetes 2D, moral da história destacada, voz amigável de parabéns do Jarvis e 3 botões gigantes de alta visibilidade.* |

| 🦖 5. Parque dos Dinossauros & Sítio Paleontológico | 🕵️ 6. Detetive Stark (Jogo dos 7 Erros) |
| :---: | :---: |
| ![Parque dos Dinossauros](docs/screenshots/05_parque_dinossauros.png) | ![Detetive Stark](docs/screenshots/06_detetive_7_erros.png) |
| *Escavação fóssil interativa com martelinho, pincel e super lupa, além de rugidos pré-históricos e fatos científicos adaptados para crianças.* | *Desafio visual de atenção e foco com contador tátil progressivo, efeitos sonoros imersivos e incentivos falados pelo robô Jarvis.* |

| 🎨 7. Lousa Mágica Neon & Carimbos Colecionáveis | 📱 8. Painel Administrativo dos Pais (`/admin`) |
| :---: | :---: |
| ![Lousa Mágica Neon](docs/screenshots/07_lousa_magica_neon.png) | ![Painel dos Pais](docs/screenshots/08_painel_pais_admin.png) |
| *Quadro de desenho digital com pincéis neon vibrantes, borracha tátil e carimbos colecionáveis (⭐, 🤖, 🚀, 🦖, ❤️, 👑, ⚡).* | *Painel dos pais com indicador de Wi-Fi em tempo real (nmcli), túnel Cloudflare, limite de tempo de tela, controle de volume e mensagens carinhosas.* |

| 🧩 9. Quarto de Engenharia (Programação Visual por Blocos) |
| :---: |
| ![Quarto de Engenharia](docs/screenshots/09_quarto_engenharia.png) |
| *Bancada de lógica computacional e robótica infantil estilo Google Blockly: a criança programa sequências de passos e ações para o robô Jarvis executar!* |

---

## 🌟 Novidades da Versão 3.7.0 (Stark Edge AI & Aceleração TensorFlow Lite)

Inspirado na arquitetura do **TensorFlow Lite**, **XNNPACK** e **QuickDraw**, o sistema agora conta com visão computacional de borda e reconhecimento de voz instantâneo projetados sob medida para não consumir CPU nem RAM no **Intel Atom N450**:

### 🔮 1. Lousa Mágica Inteligente com Visão de Desenhos (QuickDraw Edge)
- **Botão `🔮 O que o Jarvis vê?`:** A criança desenha livremente na Lousa Neon e clica no botão mágico. A IA de borda analisa a imagem instantaneamente e o Jarvis reconhece o que foi desenhado (*Sol, Estrela, Coração, Foguete, Casinha, Dinossauro, Peixinho, Florzinha*).
- **Elogio Falado & Recompensa Gamificada:** O Jarvis fala em voz alta elogiando a imaginação do pequeno herói (*"Bip bip, super Kaleo! O Jarvis viu que você desenhou um lindo Sol radiante e quentinho!"*), dispara confetes 2D e adiciona +2 moedas de ouro no Pote do Tesouro.
- **Suporte Total a Touch:** Adicionado suporte nativo a toques de dedos na tela (`touchstart`, `touchmove`, `touchend`), permitindo desenhar com os dedinhos em netbooks touch, tablets e smartphones.

### 📸 2. Desafio dos Dedinhos com Câmera Mágica (Hand Vision)
- **Nova Aba `📸 Mãozinha na Câmera (IA)`:** A criança coloca a mãozinha na frente da webcam do netbook e o Jarvis detecta e conta os dedinhos levantados (de 1 a 5).
- **Amostragem Ultraleve (380ms):** A visão computacional processa em miniatura (80x60) com espaçamento temporal seguro, garantindo **0% de travamento na CPU** do Atom e mantendo os 60 FPS da interface do quiosque.
- **Feedback por Voz em Tempo Real:** Conforme a criança mexe os dedinhos, o mostrador numérico se atualiza e o Jarvis comemora por voz!

### ⚡ 3. Ativação de Voz Instantânea Offline (Fast Keyword Spotter em 10ms)
- **Resposta em 10 milissegundos:** Comandos diretos da criança (*"jogos"*, *"livro"*, *"desenhar"*, *"dedinhos"*, *"loja"*, *"dinossauro"*, *"música"*, *"escovar dente"*, *"bom dia"*, *"boa noite"*) são reconhecidos localmente de imediato.
- **100% Funcional sem Internet:** Se a rede Wi-Fi cair, a criança continua conversando e abrindo todas as atividades por voz sem travar na tela de escuta.

### 🧠 4. Motor Backend `ai_edge_engine.py` & Suporte a `tflite-runtime`
- **Novo Módulo de IA de Borda:** Implementado em `ai_edge_engine.py` e integrado ao `run_server.py` nas rotas `/api/ia/classificar_desenho` e `/api/ia/status`.
- **Substituição do Monólito:** Em vez do pacote pesado do TensorFlow (850 MB), o sistema adota oficialmente o `tflite-runtime` (apenas 3.8 MB), acelerado por instruções SSE2/SSSE3 nativas do Atom N450.
- **Novo `requirements.txt` Oficial:** Dependências mapeadas com precisão na raiz do repositório.

---

## 🌟 Novidades da Versão 3.6.6 (HUD Clean & Acesso Direto a Histórias)

### 🚀 1. Interface Desobstruída & Limpa (Sem Modal Superior)
- **Visão 100% Limpa e Espaçosa:** Remoção do modal flutuante superior ("Sala de Brincar") e do seletor de cômodos, eliminando distrações visuais e desobstruindo a área central para o robô Jarvis e para a criança.
- **🛡️ Proteção Anti-Deslize:** Desativação de gestos de swipe acidentais na tela principal que causavam trocas involuntárias de cenário ou escurecimento de tela.

### 📚 2. Acesso Direto à Biblioteca Mágica na Barra Inferior
- **Tríade de Ouro de Alta Usabilidade:** A barra inferior agora exibe 3 pilares imediatos de 1 toque:
  1. `[🎮 Jogos]` — Central de 24 jogos educativos paginados.
  2. `[📚 Histórias]` — Acesso direto e instantâneo à Biblioteca Mágica de Histórias com virtudes e valores (sem precisar caçar no catálogo).
  3. `[🏪 Loja / Armário]` — Personalização de roupinhas/acessórios e Pote do Tesouro.

---

## 🌟 Novidades da Versão 3.6.5 (Edição Definitiva de Estabilidade e UX Infantil)

### 🌟 1. Tela de Conquista & Celebração do Livro Definitiva (`v3.6.4`)
- **Fim do Fechamento Abrupto e Travamento:** O botão de concluir livro agora é uma chamada dourada pulsante `🌟 CONCLUIR HISTÓRIA! (+2 ⭐)` de 68px de altura com feedback tátil instantâneo.
- **Tela de Conquista Festiva:** Ao terminar uma história, abre-se uma tela comemorativa com o mascote Jarvis feliz, chuva de confetes 2D (`canvas-confetti`), a moral da história destacada em caixa dourada e 3 botões gigantes: `⭐ Pegar Minhas Estrelas!`, `🔄 Ler Novamente` e `📚 Escolher Outro Livro`.
- **Elogio e Síntese de Voz Sem Conflito:** O Jarvis elogia a criança por voz com tom afetuoso sem silenciar a música de fundo nem congelar a interface.

### 🦸‍♂️ 2. Quartel-General de Missões do Herói Reformulado (`v3.6.3`)
- **Linha do Tempo Visual de Conquistas:** Barra de progresso vibrante exibindo quantas missões foram concluídas no dia.
- **Abas de Filtro Ergonômicas:** Filtros rápidos `Todas`, `Para Fazer` e `Concluídas` com tamanho adaptado para dedinhos de crianças pequenas.
- **Atalhos Contextuais:** Cada missão possui botão com atalho direto para a atividade correspondente (escovação de dentes, dinossauros, livros, etc.).

### 📶 3. Gestão de Wi-Fi em Tempo Real no Painel dos Pais (`/admin`)
- **Detecção Precisa do SSID Ativo via `nmcli`:** O painel administrativo dos pais detecta e exibe a rede conectada instantaneamente (ex.: `ANJOS_COLCHOES`), com indicador visual de sinal e IP atribuído.
- **Varredura Segura em Segundo Plano:** Escaneamento de redes disponíveis sem congelamento da interface e conexão guiada com senha protegida.

### ⚡ 4. Servidor Inteligente com Recarregamento Automático e Headers Anti-Cache
- **Monitoramento de Modificação (`mtime`):** O `run_server.py` detecta alterações nos arquivos de template HTML e recarrega o cache de RAM automaticamente sem necessidade de reiniciar o processo.
- **Headers HTTP Anti-Cache:** Injeção estrita de `Cache-Control: no-cache, no-store, must-revalidate` e `Pragma: no-cache`, garantindo que o navegador nunca sirva versões antigas de scripts ou estilos.

### 🧩 5. Quarto de Engenharia com Programação Visual (`/engenharia`)
- **Bancada de Automação Infantil:** Ambiente interativo baseado em blocos visuais onde a criança conecta peças de código (andar, falar, girar, acender luzes) e assiste ao robô Jarvis executar as instruções na tela.

---

## 🌟 Novidades da Versão 3.5.0

### 🌐 1. Gestão Automatizada de Domínio & Cloudflare Tunnel (`config_nuvem.py`)
- **Acesso Parental de Qualquer Lugar:** Painel dos Pais acessível remotamente em HTTPS sem necessidade de IP fixo, DDNS ou abertura de portas no roteador.
- **Integração com `cloudflared` CLI:** Criação automatizada do túnel `jarvis` via subprocess, extração de UUID e geração de `config.yml` mapeando para a porta local do Jarvis.
- **Apontamento DNS CNAME para Registro.br:** Exibição clara na interface com 1 clique para copiar o registro DNS (`Tipo: CNAME | Nome: jarvis | Destino: [UUID].cfargotunnel.com`).

### 🛡️ 2. Roteamento Estrito & Proteção Parental (`run_server.py`)
- **Modo Quiosque Puro na Raiz (`/`):** A raiz do sistema renderiza EXCLUSIVAMENTE o `hud_jarvis.html` em modo quiosque sem acesso a configurações administrativas.
- **Painel Administrativo Protegido (`/admin`):** O painel dos pais requer autenticação ou PIN de segurança quando acessado remotamente, mantendo o controle total nas mãos dos pais.
- **Redirecionamento Inteligente:** Rota `/pais` redireciona via HTTP 302 para `/admin`.

### 💻 3. Módulo de Controle de Hardware & Energia (`config_hardware.py`)
- **Gestão de Wi-Fi:** Escaneamento e conexão a redes Wi-Fi em background via `nmcli`.
- **Áudio & Mute:** Controle fino de volume ALSA e botão Mute instantâneo via `amixer`.
- **Brilho & Filtro Noturno Circadiano:** Controle de iluminação da tela via `xrandr` e ativação agendada de `redshift -O 3500` às 19h00 (restaurando 6500K às 07h00) para proteção ocular infantil.
- **Kiosk Bypass (`/manutencao`):** Encerra navegadores quiosque via `pkill` para liberar a área de trabalho do Linux aos pais para manutenções do sistema.
- **Gestão de Energia:** Comandos seguros de reinicialização (`sudo reboot`) e desligamento (`sudo shutdown`).

### ⚡ 4. Otimização Profunda do Sistema Operacional (antiX Linux / Atom N450)
- **ZRAM Ativo:** Compressão de memória RAM (`zram-tools` com `zstd`/`lz4` a 50% de RAM), fazendo os 2 GB físicos renderem com a folga de 3 GB.
- **VRAM & Aceleração GPU Intel GMA 3150:** Configuração de `/etc/X11/xorg.conf.d/20-intel.conf` com `Option "AccelMethod" "sna"` e `Option "TearFree" "true"`, transferindo a carga gráfica das animações CSS para a GPU e liberando a CPU.
- **Firewall UFW:** Bloqueio de tráfego de entrada não essencial, mantendo apenas portas locais e túnel Cloudflare ativos.
- **Eliminação Absoluta de Bluetooth:** Remoção e bloqueio de serviços Bluetooth via `rfkill block bluetooth` para poupar bateria e ciclos de processamento.

### 🎨 5. Bibliotecas Leves & Quarto de Engenharia (Blockly)
- **Animate.css & SweetAlert2:** Transições fluidas e alertas visuais adaptados ao tema Stark.
- **Canvas-Confetti (Dopamina 2D):** Disparo de partículas festivas ao concluir missões com 0% de sobrecarga na CPU.
- **SortableJS:** Drag-and-drop leve integrado.
- **KenneyNL UI Kit:** Assets vetoriais organizados em `/static/ui/`.

### 🎵 6. Gamificação, Sonoplastia & Trilha em Loop
- **Minijogo "Descobre o Som":** O Jarvis reproduz áudios reais de animais gravados da natureza e a criança escolhe entre 3 opções de bichos ou dinossauros, recebendo confetes e moedas SQLite WAL.
- **Trilha Sonora em Loop:** Música temática *BoxCat Games - Young Love.mp3* reproduzida em loop via tag HTML `<audio>` durante desafios com timer e escovação de dentes.

### 📱 7. App Android Remoto Otimizado (< 3 MB)
- **WebView Nativo:** Aponta nativamente para a URL segura do painel remoto em tela cheia imersiva (sem barra de endereços).
- **Sem Assets Pesados:** Imagens e áudios pesados do netbook foram desvinculados do pacote Android, gerando um APK extremamente leve e rápido.

---

## 🌟 Novidades da Versão 3.4.6

### 🎮 1. Catálogo Expandido para 24 Jogos Educativos (6 Páginas 2x2)
- **Zero Scrollbar no Netbook 1024x600:** Cada página acomoda exatamente 4 jogos em grade 2x2, sem estourar a altura útil da tela.
- **Novos Jogos Didáticos & Científicos:**
  - **🪐 Sistema Solar & Simulador de Gravidade:** Pilote naves espaciais, observe planetas e experimente o simulador de gravidade na Terra ($1.0\times$), Lua ($0.16\times$) e Júpiter ($2.5\times$).
  - **🦁 Reino Animal com Sons Reais (18 Animais):** Áudios reais gravados de leão, elefante, sapo, cavalo, pássaro, arara, mico, onça, coruja, golfinho, jacaré, baleia, cachorro, gato, vaca, pato, urso e pinguim.
  - **⏰ Relógio Mágico & Cronômetro de 30s:** Ensino de horas com mostrador analógico/digital e cronômetro gamificado com contagem regressiva sonora para lavar as mãos e escovar os dentes.
  - **🕵️ Detetive Stark (Jogo dos 7 Erros):** Desafios visuais com efeitos sonoros e pistas do robô Jarvis.
  - **🔬 Laboratório de Ciências & Vulcão Químico:** Estados da água (Gelo, Líquido, Vapor), misturador de cores primárias e o experimento do Vulcão Químico (Bicarbonato + Vinagre) com erupção borbulhante e fumaça neon.
  - **♟️ Academia de Xadrez do Pequeno Mestre:** Mini-tabuleiro interativo ensinando o movimento do Peão, Torre e o famoso salto em "L" do Cavalo.
  - **🦖 Parque dos Dinossauros & Fósseis Stark:** Sítio paleontológico com escavação de ossos do Tiranossauro Rex, Braquiossauro e Tricerátops, com rugidos pré-históricos e fatos científicos.
  - **🎨 Lousa Mágica Neon Atualizada:** Novos carimbos colecionáveis (⭐, 🤖, 🚀, 🦖, ❤️, 👑, ⚡).

### 🌤️ 2. Clima e Previsão com Geocodificação Dinâmica em Tempo Real
- **Sincronização com Open-Meteo:** Dados meteorológicos reais para Campo Largo / PR e qualquer município configurado.
- **Previsão de Amanhã Inteligente:** Jarvis agora diferencia com precisão perguntas sobre o clima de hoje vs. previsão do tempo de amanhã (temperatura máxima, mínima e probabilidade de chuva).
- **Resposta por Voz Limpa:** O Jarvis responde a previsão falando naturalmente por voz sem forçar a abertura de janelas ou modais que interrompam a atividade da criança.

### 📱 3. Aplicativo Android 100% Autônomo & Offline (Sem Erro de Porta 8000)
- **Execução Nativa Direta:** O APK Android agora embute todos os templates, jogos, mascote e folhas de estilo dentro do próprio pacote (`assets/` nativo em `file:///android_asset/hud_jarvis.html`), funcionando de forma **100% autônoma e offline** diretamente no celular da criança, sem precisar de servidor rodando ou de IP na porta 8000.
- **Persistência Local (localStorage Fallback):** Fichas, moedas, itens da lojinha e histórico de dicção são mantidos localmente no próprio aparelho da criança.
- **Modo Wi-Fi Opcional com 1 Toque:** Se os pais quiserem conectar o celular ao robô que está rodando no netbook ou PC da casa, basta dar um **toque longo na tela** para abrir o menu de conexão, digitar o IP e alternar na hora.

---

## 🌟 Recursos Consolidados da Versão 3.2

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
- **🚫 Botão de Travar / Zerar Cinema nas Ações Rápidas:** Os pais podem interromper ou revogar instantaneamente qualquer tempo residual de vídeo diretamente pelo painel `/admin` via `/api/admin/media/zerar`.
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
| 🐧 **.deb** | Debian / antiX / Ubuntu / Raspberry Pi OS | `jarvis-kids-os_3.7.0.deb` | `sudo dpkg -i jarvis-kids-os_3.7.0.deb` |
| 📦 **.tar.gz** | Linux Kiosk Standalone (Netbook Atom) | `jarvis-kids-os-3.7.0-linux-desktop.tar.gz` | `tar -xzf jarvis-kids-os-*.tar.gz && ./iniciar_jarvis_linux.sh` |
| 🪟 **.zip** | Windows 7 / 10 / 11 (Desktop) | `jarvis-kids-os-3.7.0-windows-desktop.zip` | Extrair e clicar em `iniciar_jarvis_windows.bat` |
| 📱 **.apk** | Android Celulares & Tablets Infantis | `jarvis-kids-os-3.7.0-android.apk` | Instalar no Android e permitir microfone (Modo Autônomo Offline Nativo) |
| 🍏 **.app** | macOS (Intel & Apple Silicon M1/M2/M3) | `jarvis-kids-os-3.7.0-macos.app.zip` | Extrair e abrir `JARVIS-Kids-OS.app` |
| 📱 **PWA** | Smartphone dos Pais (iOS / Android) | Acesso direto via navegador | Acessar `/admin` e clicar em *Adicionar à Tela Inicial* |

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
- Todas as interfaces (HUD, Loja, Biblioteca, Prato dos Campeões, Central de Jogos e Academia de Dicção) utilizam containers flexbox com `overflow: hidden; max-height: calc(100vh - 72px)` e navegação anterior/próxima em botões de alta visibilidade, eliminando completamente barras de rolagem.

---

## 🐧 Inicialização Automática no Boot (antiX Linux & Netbooks Dedicados)

Uma das maiores vantagens do JARVIS Kids OS quando instalado no **antiX Linux** (especialmente no Acer Aspire One, Asus Eee PC ou PCs antigos) é a experiência de **Console Educativo Dedicado** (estilo videogame ou eletrodoméstico):

### 🚀 Instalação com 1 Comando no antiX Linux (100% Automático):
Basta baixar o arquivo `.deb` da versão mais recente nas Releases (ou passar pelo pendrive) e executar no terminal do antiX:

```bash
sudo dpkg -i jarvis-kids-os_3.7.0.deb || sudo apt-get install -f -y
```

Ou usando o comando moderno do `apt` (que resolve e baixa todas as dependências do sistema de uma só vez):
```bash
sudo apt install ./jarvis-kids-os_3.7.0.deb
```

> 🛠️ **Como compilar o `.deb` localmente a qualquer momento:**
> Se você clonou ou extraiu o repositório no Linux, pode gerar o pacote oficial executando:
> ```bash
> bash gerar_deb.sh
> ```

**Pronto! A partir desse momento, tudo é 100% automático:**
- **Zero configuração manual:** Você **não precisa** ativar o servidor pelo terminal nem digitar comandos toda vez que ligar o netbook.
- **Início Automático no Boot:** O instalador `.deb` configura o serviço de background e a sessão do antiX. Sempre que você ligar ou reiniciar o computador, o Jarvis Kids OS sobe sozinho em tela cheia (modo quiosque 1024x600).
- **Sem senhas ou distrações:** A criança vê apenas o robô Jarvis e seus jogos educativos, sem acesso a menus do sistema, barra de tarefas ou terminal.

---

### 🔄 Como Funciona Toda Vez que Ligar ou Reiniciar:
1. **Zero Senhas (Auto-Login Instantâneo):** O sistema faz o login automático direto no usuário da criança pelo gerenciador **SLiM** (`/etc/slim.conf`) ou **LightDM**, sem travar em telas de senha.
2. **Zero Telas do Linux ou Menus Confusos:** O netbook não abre terminal, painéis ou área de trabalho com ícones soltos.
3. **Direto no Robô Jarvis (Tela Cheia 1024x600):** O arquivo de inicialização de sessão do antiX (`~/.desktop-session/startup`) sobe o backend Python ultraleve e aciona o navegador em modo quiosque (`--kiosk http://127.0.0.1:8000`) em poucos segundos!
4. **Volume Destravado Automaticamente:** O áudio dos alto-falantes e o microfone interno são regulados automaticamente em 85% pelo ALSA no boot, garantindo que o Jarvis fale e ouça a criança imediatamente.

### 🛡️ Blindagem Infantil Anti-Fechamento:
* **Teclas Desativadas:** Teclas e atalhos de sistema que crianças pequenas costumam apertar sem querer (`Alt + F4`, `Alt + Tab`, teclas Windows/Super) são desativados no `~/.icewm/prefoverride` e no Openbox (`rc.xml`).
* **Watchdog de Persistência:** Caso o navegador seja fechado acidentalmente, um laço de monitoramento reabre o Jarvis automaticamente em 2 segundos.
* **Protetor de Tela Desativado:** Comandos `xset s off -dpms` impedem que a tela apague no meio de uma historinha ou jogo.

---

### ⚡ Script de Instalação e Otimização Direta (`instalar_otimizado.sh`)
Para quem já clonou ou extraiu o repositório diretamente no netbook (Intel Atom N450 com 1 GB a 2 GB de RAM), o script all-in-one aplica todos os ajustes finos de baixo nível no sistema operacional com apenas 1 comando como root:

```bash
sudo bash instalar_otimizado.sh
```

**O que o `instalar_otimizado.sh` faz automaticamente:**
1. **Otimização de Kernel (ZRAM & Swappiness):** Aplica `vm.swappiness=80` e `vm.vfs_cache_pressure=50` em `/etc/sysctl.d/99-jarvis-otimizado.conf` para evitar thrashing de RAM.
2. **Compressão ZRAM (lz4):** Instala `zram-tools` e aloca 50% da memória com compressão ultrarrápida lz4, além de instalar `unclutter` para ocultar o cursor do mouse após inatividade.
3. **Aceleração de Disco (noatime, nodiratime):** Modifica `/etc/fstab` para eliminar o overhead de registro de acesso a cada arquivo ou asset lido no HDD/SSD lento do netbook.
4. **Renderização Web Otimizada:** Injeta flags de baixo consumo no `iniciar_web_kiosk.sh` (`--kiosk --disable-gpu --disable-dev-shm-usage --disable-background-networking --disable-extensions --js-flags="--max_old_space_size=256"`).
5. **Daemon do Sistema:** Copia e ativa o serviço `/etc/systemd/system/jarvis-kids.service` (ou modo de segundo plano no antiX SysVinit).
6. **Manutenção Noturna Automática:** Agenda na crontab das 3h da manhã um reinício preventivo do serviço e limpeza dos caches de RAM (`drop_caches`), garantindo que o netbook acorde 100% responsivo para o uso da criança no dia seguinte.

---

## 🎮 Catálogo dos 24 Jogos & Atividades Educativas (6 Páginas 2x2)

### 📄 Página 1: Alfabetização, Matemática e Linguagens
1. **📚 Biblioteca Mágica de Histórias:** Livros ilustrados interativos e histórias com decisões morais.
2. **🔤 Ler & Escrever (Método Fônico):** Sons de cada letra do alfabeto e escrita na lousa neon.
3. **🖐️ Desafio dos Dedinhos:** Matemática visual e contagem de 1 a 10 com mãozinhas animadas.
4. **🌍 Idiomas Mágicos (English & Español):** Cartões falantes em 3 idiomas e miniquiz com moedas reais.

### 📄 Página 2: Nutrição, Higiene, Arte e Música
5. **🍎 Prato dos Super Campeões:** Educação alimentar lúdica com os 4 grupos de nutrientes essenciais.
6. **🧼 Super Herói Limpinho (Higiene):** 4 missões práticas de autocuidado (dentes, banho, mãos e unhas).
7. **🎨 Pintura & Lousa Mágica Neon:** Lousa artística com pincéis coloridos e salvamento de desenhos.
8. **🎵 Laboratório Musical Stark:** Teclado Dó-Ré-Mi, bateria de ritmo e músicas infantis guiadas.

### 📄 Página 3: Tecnologia, Cultura e Informação
9. **💻 Academia Tech: Mouse, Teclado & Scroll:** Foguete (scroll up), Submarino (scroll down), mira e clique.
10. **🇧🇷 Festas & Datas Comemorativas do Brasil:** Celebrações culturais brasileiras no calendário interativo.
11. **🎬 Cinema & Desenhos Stark:** Gestão segura de tempo de vídeo no YouTube Kids e Netflix.
12. **🌤️ Clima, Geografia & Meu Lugar no Mundo:** Sua cidade, estado, Brasil, mapa e as 4 estações do ano.

### 📄 Página 4: Mente, Emoções e Cognição
13. **🚦 Desafio do Semáforo Stark:** Treino de atenção rápida, reflexos e controle inibitório.
14. **💚 Flor da Calma & Emoções:** Respiração guiada, identificação de sentimentos e regulação emocional.
15. **📦 Baú Leitner da Memória:** Repetição espaçada e memorização inteligente de fatos e conceitos.
16. **🔷 Cores, Formas & Lógica Espacial:** Geometria lúdica com círculos, quadrados, triângulos e estrelas.

### 📄 Página 5: Dicção, Espaço, Natureza e Tempo
17. **🗣️ Fonoaudiologia & Dicção do Super-Herói:** 66 desafios de fala com sílabas neon, dica da boquinha, fala pausada e sorteio de palavras mágicas pelo robô Jarvis!
18. **🪐 Sistema Solar & Planetas do Universo:** Pilote a nave espacial, visite planetas (Marte, Júpiter, Saturno), aprenda curiosidades espaciais e dispute o Quiz Astronauta.
19. **🦁 Reino Animal & Sons da Natureza (Biólogo Stark):** Conheça os animais, ouça sons característicos sintetizados e adivinhe o bicho pelo som no Desafio do Ouvido!
20. **⏰ O Relógio Mágico do Tempo & Horas:** Mostrador analógico e digital interativo, ciclo visual dia/noite e missões de rotina (hora de acordar, almoçar e dormir).

### 📄 Página 6: Raciocínio, Ciências, Estratégia e Aventura Pré-Histórica
21. **🕵️ Detetive Stark: Jogo dos 7 Erros:** Olhos de águia para encontrar detalhes secretos em cenas de alta visibilidade com incentivos do Jarvis.
22. **🔬 Laboratório de Misturas & Ciências:** Misturador de cores primárias (vermelho, azul, amarelo), termômetro dos 3 estados da água (gelo, líquido, vapor) e o super ímã magnético.
23. **♟️ Academia de Xadrez do Pequeno Mestre:** Aprenda o movimento do Peão, Cavalo em L, Torre e grandes jogadas com mini-tabuleiro interativo e dicas do Jarvis.
24. **🦖 Parque dos Dinossauros & Fósseis Stark:** Sítio paleontológico com pincel e martelo para desenterrar fósseis de T-Rex, Braquiossauro e Tricerátops, com rugidos épicos e curiosidades.

---

## 🚀 Como Executar Localmente (Desenvolvimento & Testes)

> 💡 **Para quem usa o Netbook com antiX Linux:** Você **NÃO** precisa clonar o repositório nem rodar comandos no terminal para iniciar o servidor! Basta instalar o pacote `.deb` oficial (`sudo dpkg -i jarvis-kids-os_3.7.0.deb || sudo apt-get install -f -y`). O sistema inicia 100% automático no boot.
>
> O passo a passo abaixo é voltado exclusivamente para desenvolvedores ou para quem deseja testar o código manualmente em outros computadores:

### Pré-requisitos (Modo Dev)
- Python 3.10 ou superior
- Navegador moderno (Chromium, Chrome, Edge ou Firefox)

### Instalação em Modo de Desenvolvimento
```bash
git clone https://github.com/zetra-mini/O.S-EDUCATIVO-PARA-CRIAN-AS.git
cd O.S-EDUCATIVO-PARA-CRIAN-AS
pip install -r requirements.txt
```

### Inicialização Manual do Servidor
```bash
python run_server.py 8000
```
- Interface da criança (Modo Kiosk): `http://localhost:8000`
- Painel Administrativo dos Pais: `http://localhost:8000/admin` (ou `/pais`)
- Quarto de Engenharia (Blockly): `http://localhost:8000/engenharia`

---

## 📱 Painel dos Pais (`/admin` ou `/pais`)

Acessível por qualquer smartphone, tablet ou computador na mesma rede Wi-Fi (`http://[IP-DO-NETBOOK]:8000/admin`):
- **📶 Status Wi-Fi em Tempo Real:** Visualização do SSID conectado (`nmcli`) e sinal da rede.
- **Ações Rápidas com 1 Toque:** Liberar ou travar cinema, pausar para refeição, acionar alarme de escovar dentes ou guardar brinquedos.
- **Pote do Tesouro:** Gerenciamento do saldo de moedas e aprovação de resgates da vida real.
- **Mensagens & Recados com Áudio/Vídeo:** Envio de bilhetes carinhosos com confirmação de leitura pela criança.
- **Configurações de Voz Neural:** Seleção entre 11 vozes neurais brasileiras com prioridade total no sistema.
- **Geografia Ensinável:** Configuração de cidade, estado e país para ensinar à criança sua localização no planeta Terra.
- **Logs & Diagnóstico em Tempo Real:** Monitoramento de eventos, bateria do notebook e integridade do banco SQLite.

---

## 🛡️ Licença e Dedicação

Desenvolvido com amor, carinho e dedicação paterna para **Kaleo Noah**, unindo a mais avançada psicologia do desenvolvimento infantil à engenharia de software de alta eficiência.
