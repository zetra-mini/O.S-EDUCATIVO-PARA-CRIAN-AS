# ◈ J.A.R.V.I.S. Kids OS v2.6 — Stark Educational System (Para Kaleo Noah)

Sistema educativo completo estilo **JARVIS do Homem de Ferro** projetado sob medida para o netbook **Acer Aspire One 532h / Asus EeePC** (`Intel Atom N450`, `2 GB RAM`, SSD, vídeo `Intel GMA 3150`, tela `1024x600`).

Consome **menos de 28 MB de memória RAM no modo nativo (ou ~180 MB no modo Web Arcade Kiosk)**, funciona **100% offline** nas atividades educativas com respostas instantâneas (< 1 ms), integra controle de tempo pedagógico inteligente para o cinema e agora suporta **OpenCode CLI / LAN Híbrido** e **Jogo das Emoções Interativo**.

---

## 🚀 Novidades da Versão 2.6

1. **⚡ Suporte Prioritário ao OpenCode CLI & Modo Híbrido LAN:**
   - Adicionada opção do **OpenCode CLI (`opencode-ai`)** como motor prioritário de IA e orquestração.
   - Pode rodar diretamente no netbook ou conectar-se via Wi-Fi a um servidor OpenCode no PC principal da casa (`iniciar_opencode_lan.sh` / `.bat`), garantindo IA inteligente sem esquentar o processador Atom nem travar os 2 GB de RAM.
   - Suporte a modelos como `google/gemini-2.0-flash`, `opencode/mimo-v2.6-flash-free` e `groq/llama-3.3-70b`.

2. **💚 Novo Jogo das Emoções Reformulado (Histórias Lúdicas com Estrelas):**
   - **🎮 1. Jogo: Como o Amigo se Sente?:** Mini-histórias ilustradas com situações infantis reais (o dinossauro ganhando brinquedo, torre de blocos caindo, barulho de trovão, amiguinho pegando giz sem pedir, cobertor macio na hora de dormir).
   - A criança identifica a emoção certa nos botões coloridos, ouve o elogio em voz alta e ganha estrelas Stark com avanço automático!
   - **🎭 2. Meu Coração & Sentimentos:** Cartões táteis de autorregulação emocional.
   - **🌸 3. Florzinha da Calma:** Respiração guiada para acalmar a criança: "Cheirar a florzinha pelo nariz" (4s) e "Soprar a velinha pela boca" (4s) com animação suave e som harmônico.

3. **📏 Respostas do Járvis 100% Proporcionais (Resolução 1024x600):**
   - O cérebro (`jarvis_brain.py`) agora ajusta e trunca automaticamente respostas longas em 2 ou 3 sentenças completas e carinhosas, evitando parágrafos cansativos para crianças de 4 anos.
   - O rodapé de legendas e o balão de conversa receberam tipografia fluida com `clamp()` e barra de rolagem suave com `overflow-y: auto`, nunca quebrando nem escondendo botões.

4. **🔇 Silenciamento do Talkback ao Passar o Mouse:**
   - Removido o áudio automático ao passar o cursor sobre os cards da tela inicial. O Járvis agora só fala quando a criança clica no card ou pressiona o microfone para conversar.

---

## 🌟 Recursos Anteriores (v2.5)

1. **⚡ Armadura Stark por Conquistas:**
   - Conforme a criança estuda e lê, desbloqueia em tempo real as 4 peças da Armadura Stark (Capacete, Luvas com Repulsores, Botas a Jato e Reator Arc).
2. **🔤 Método Fônico & Lousa de Traçado Neon:**
   - Fonemas estendidos (*"/b/ /b/ de Bola!"*) e traçado interativo em neon ciano com faíscas elétricas.
3. **📖 Histórias Interativas ("Você Decide!"):**
   - Livros com decisões ilustradas de 1 toque (ex: *"A Grande Aventura Espacial de Kaleo"*).
4. **📱 Painel dos Pais no Celular (`/pais`):**
   - Controle remoto de bônus de cinema (+15 min), pausa para almoço/jantar e modo noturno.
5. **🔒 Blindagem de Quiosque no antiX Linux / IceWM:**
   - Bloqueio de atalhos acidentais e trava de volume seguro a 75%.

---

## 🛠️ Como Iniciar o Sistema

### No Windows
- **Modo Web Arcade Completo:** Clique duas vezes em `iniciar_web_windows.bat` (abre em `http://127.0.0.1:5090`)
- **Modo Nativo Desktop:** Clique duas vezes em `testar_no_windows.bat`
- **Servidor OpenCode LAN:** Clique duas vezes em `iniciar_opencode_lan.bat`

### No Netbook Acer / Asus One (antiX Linux)
1. Instale o **antiX Linux** com **Auto-Login** ativado.
2. No terminal:
   ```bash
   git clone https://github.com/zetra-mini/O.S-EDUCATIVO-PARA-CRIAN-AS.git jarvis-kids-os
   cd jarvis-kids-os
   chmod +x instalar_antix_kiosk.sh iniciar_opencode_lan.sh
   bash instalar_antix_kiosk.sh
   ```
3. O netbook iniciará automaticamente em modo quiosque Stark em tela cheia!
