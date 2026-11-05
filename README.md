# ◈ J.A.R.V.I.S. Kids OS v2.5 — Stark Educational System (Para Kaleo Noah)

Sistema educativo completo estilo **JARVIS do Homem de Ferro** projetado sob medida para o netbook **Acer Aspire One 532h** (`Intel Atom N450`, `2 GB RAM`, SSD, vídeo `Intel GMA 3150`, tela `1024x600`).

Consome **menos de 28 MB de memória RAM no modo nativo (ou ~180 MB no modo Web Arcade Kiosk)**, funciona **100% offline** nas atividades educativas com respostas instantâneas (< 1 ms) e integra controle de tempo pedagógico inteligente para o horário do cinema.

---

## Novidades da Versão 2.5

1. **⚡ Armadura Stark por Conquistas (Gamificação Lúdica):**
   - Conforme a criança lê livros, treina dedinhos ou acerta letrinhas, desbloqueia em tempo real as 4 peças da Armadura Stark no centro da tela:
     - ⛑️ Capacete Stark
     - 🧤 Luvas com Repulsores
     - 🥾 Botas a Jato
     - ⚡ Reator Arc Dourado Completo
   - Ao completar as 4 partes, o JARVIS celebra com fanfarra musical e parabéns por voz!

2. **🔤 Método Fônico & Lousa de Traçado Neon:**
   - **Método Fônico:** Ao tocar nas letras, a criança ouve o nome da letra e o fonema estendido (*"/b/ /b/ de Bola!"*, *"/k/ /k/ de Casa!"*).
   - **Aba "✍️ Traçar Letras":** Canvas interativo com guia pontilhada onde o traço acende em neon ciano e amarelo com faíscas elétricas e sons estelares.

3. **📖 Histórias Interativas ("Você Decide!"):**
   - Livros com pontos de decisão (ex: *"A Grande Aventura Espacial de Kaleo"*). A criança escolhe entre viajar para o Planeta dos Dinossauros ou Planeta dos Robôs com cards ilustrados de 1 toque!

4. **📱 Painel dos Pais no Celular (Mesmo Wi-Fi — `/pais`):**
   - Acesse `http://<IP-DO-NETBOOK>:5090/pais` em qualquer smartphone conectado na mesma rede:
     - Ver tempo restante de vídeo e livros lidos hoje;
     - Botão de 1 toque para conceder **+15 min de bônus** de cinema;
     - Botão **"Pausar Tela (Almoço / Jantar)"** que aciona aviso carinhoso em tela cheia no netbook;
     - Alternador do Modo Noturno.

5. **🌙 Modo Noturno Automático (Proteção Visual & Sono):**
   - Redução automática de luz azul após as 19h30 com paleta de repouso ambarina e fala acolhedora.

6. **🔒 Blindagem de Quiosque no antiX Linux / IceWM:**
   - Bloqueio de teclas acidentais (`Alt+Tab`, `Alt+F4`, `Ctrl+Alt+T`);
   - Trava de volume ALSA seguro a 75%;
   - Otimizações para GPU Intel GMA 3150 (remoção de blur por software e aceleração de composição `translateZ(0)`).

---

## Como Rodar no Windows

- **Modo Nativo Desktop:** Clique duas vezes em `testar_no_windows.bat`
- **Modo Web Arcade:** Clique duas vezes em `iniciar_web_windows.bat` (abre em `http://127.0.0.1:5090`)

---

## Instalação no Acer Aspire One 532 (antiX Linux)

1. Instale o **antiX Linux** (64-bit para 2 GB RAM ou 32-bit `i386`) com **Auto-Login** ativado.
2. Abra o terminal e execute:
   ```bash
   git clone https://github.com/zetra-mini/O.S-EDUCATIVO-PARA-CRIAN-AS.git jarvis-kids-os
   cd jarvis-kids-os
   chmod +x instalar_antix_kiosk.sh
   bash instalar_antix_kiosk.sh
   ```
3. O netbook reiniciará já configurado em modo quiosque automático com ZRAM lz4 ativado!
