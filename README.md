# ◈ J.A.R.V.I.S. Kids OS — Stark Educational System (4 Anos)

Sistema educativo estilo **JARVIS do Homem de Ferro** projetado sob medida para o netbook **Acer Aspire One 532h** (`Intel Atom N450`, `1 GB–2 GB RAM`, vídeo `Intel GMA 3150`, tela `1024x600`).

Consome **menos de 28 MB de memória RAM**, funciona **100% offline sem Wi-Fi** (por padrão) e traz um **Seletor Híbrido** protegido no Painel dos Pais para conectar opcionalmente ao **Ollama na rede local** ou **APIs em Nuvem (Groq / Gemini / OpenAI)**.

---

## O que vem integrado no JARVIS Kids OS:

1. **Reator Arc Animado Central (`1024x600`):** Pulsa e muda de cor quando o JARVIS fala em Português com a criança pelo nome!
2. **Lançadores Automáticos + Jogos Integrados:**
   - **★ Jogos Educativos:** Abre o **GCompris** (pré-configurado em renderização por software para a placa Intel GMA 3150 + filtro para 4 anos em PT-BR) ou o **Desafio de Cores e Formas** integrado.
   - **✎ Pintura Mágica:** Abre o **Tux Paint** em tela cheia ou a **Lousa Holográfica Neon Stark** integrada.
   - **♪ Piano & Sons:** Sintetizador musical colorido (DÓ a DÓ+) com geração sonora em memória e chuva de estrelas estilo **Gamine**.
   - **123 Contar Foguetes:** Contagem interativa falada de 1 até 10 com conquista de Estrelas Stark.
   - **◈ Conversar com o JARVIS:** 6 botões visuais grandes (Espaço, Dinossauros, Animais, Super-Herói, Números e Elogios) + caixa de perguntas conectada ao cérebro híbrido.
3. **🔒 Painel dos Pais (com Trava Matemática Anti-Criança):**
   - Personalizar o **Nome da Criança** falado pelo JARVIS;
   - Alternar o **Motor de IA** entre `offline` (padrão 100% sem Wi-Fi), `ollama` (rede local) ou `cloud` (Groq/Gemini/OpenAI);
   - Sair do Modo Quiosque ou desligar o netbook com segurança.

---

## Passo a Passo para Instalar no Acer Aspire One 532

1. **Instale o antiX Linux no netbook:**
   - Baixe o **antiX Linux Full (32-bit `i386` se tiver 1 GB de RAM, ou 64-bit se tiver 2 GB)** em https://antixlinux.com e instale marcando **Auto-Login**.
2. **Baixe diretamente do GitHub no netbook (ou leve via pendrive):**
   ```bash
   git clone https://github.com/zetra-mini/O.S-EDUCATIVO-PARA-CRIAN-AS.git jarvis-kids-os
   cd jarvis-kids-os
   chmod +x instalar_antix_kiosk.sh
   bash instalar_antix_kiosk.sh
   ```
4. **Pronto!** Pode desligar o Wi-Fi do netbook: toda vez que apertar o botão Power do Acer Aspire One 532, ele ligará direto no **JARVIS Kids OS** falando em Português!
