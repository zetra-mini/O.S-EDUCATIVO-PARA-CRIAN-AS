# 🤝 Guia de Contribuição — J.A.R.V.I.S. Kids OS

Seja muito bem-vindo(a) ao projeto de código aberto **J.A.R.V.I.S. Kids OS**! 🎉

Este projeto nasceu como um sistema operacional educativo, companheiro emocional e assistente gamificado infantil, desenvolvido com carinho para revitalizar computadores modestos e netbooks antigos (como **Acer Aspire One** e **Asus Eee PC** com processador *Intel Atom* e *1 GB de RAM*), além de rodar em **Linux Kiosk**, **Windows**, **macOS** e **Android**.

O sistema está em **desenvolvimento ativo e agora é aberto para a comunidade**! Qualquer pessoa interessada em educação infantil, inteligência artificial de borda, otimização de baixo consumo, jogos lúdicos ou interfaces acessíveis pode colaborar.

---

## 🏛️ Pilares Arquiteturais Inegociáveis

Para manter a integridade, a segurança das crianças e a fluidez do sistema em computadores modestos, todas as contribuições devem respeitar rigorosamente os seguintes pilares:

### 1. 🛡️ Privacidade e Proteção Infantil Absoluta (COPPA & LGPD)
- **Zero Informações Pessoais:** Jamais submeta commits contendo nomes reais de crianças, fotos de pessoas reais, contatos telefônicos, e-mails privados ou localizações precisas. Use sempre termos neutros e carinhosos como `"Campeão"`, `"Super Herói"` ou `"Pequeno Cientista"`.
- **Zero Segredos e Chaves de API no Código:** Nenhuma chave de API (Google Gemini, OpenAI, Groq, etc.) deve ser commitada. O arquivo `config_jarvis.json` deve manter chaves vazias `""`. Chaves reais pertencem a arquivos `.env` ou ao arquivo de configuração local do usuário (que são ignorados pelo `.gitignore`).
- **Sem Rastreamento Invasivo:** Não são permitidos scripts de telemetria externa, rastreadores de publicidade ou ferramentas de terceiros que monitorem as ações da criança.

### 2. ⚡ Desempenho Extremo em Hardware Modesto (Intel Atom N450 / 1GB RAM)
- **Backend Ultraleve:** Mantemos o servidor em Python com o micro-framework **Microdot**, com consumo de memória estritamente inferior a **15 MB de RAM**. Evite incluir dependências pesadas de bibliotecas ou frameworks robustos desnecessários em tempo de execução.
- **Frontend Puro (Vanilla Web):** A interface utiliza HTML5, CSS3 e JavaScript Vanilla moderno sem sobrecarga de frameworks como React, Angular ou Vue no cliente.
- **Gráficos 2D Canvas Otimizados:** Ao criar animações em Canvas, evite filtros de sombra pesados (`ctx.shadowBlur` com valores altos) e quantidades excessivas de partículas que sobrecarreguem GPUs legadas como a *Intel GMA 3150*.
- **Descarte de Frames em Visão Computacional:** Qualquer processamento de câmera ou imagem deve conter proteção de sobrecarga (`isProcessing` guards) e amostragem controlada para não engasgar a CPU.

### 3. 📐 Resolução Nativa Obrigatória de 1024x600 (Touch & Trackpad Friendly)
- Toda nova tela, jogo, painel ou modal deve ser projetado e calibrado para caber perfeitamente na resolução nativa **1024 x 600 pixels**.
- **Proibição de Scrollbars Ocultas:** Nenhum botão essencial, controle de navegação ou informação principal deve ficar escondido fora do campo de visão exigindo rolagem invisível. Utilize **paginação explícita** (ex: *Página 1 de 8*) com botões táteis generosos de navegação (*⬅ Anterior* e *Próxima ➡*).

### 4. 🔇 Sonoplastia & Síntese Vocal Limpa (Zero Audio Overlap)
- **Sem Sons Sobrepostos:** Todo som gerado (seja efeito Web Audio API, arquivo de áudio real de animal `.mp3` ou fala sintetizada do Jarvis) deve obrigatoriamente pausar e cancelar sons anteriores antes de iniciar uma nova reprodução.
- **Encerramento Imediato ao Sair:** Ao fechar qualquer modal, minigame ou voltar para a Sala do Jarvis, é **obrigatório** limpar todos os loops de animação (`cancelAnimationFrame`), parar temporizadores (`clearInterval`/`clearTimeout`), silenciar áudios em execução (`audio.pause(); audio.currentTime = 0;`) e cancelar a síntese vocal (`speechSynthesis.cancel()`).

### 5. 🇧🇷 Idioma Padrão e Pedagogia Afetuosa
- **Português do Brasil (pt-BR):** Todos os textos pedagógicos, interfaces, histórias e vozes devem ser elaborados em Português do Brasil com excelente correção ortográfica e clareza.
- **Tom Positivo e Não-Punitivo:** A comunicação do Jarvis com a criança é sempre acolhedora, encorajadora e paciente. Erros em minigames são tratados como oportunidades de aprendizado (*"Quase lá! Vamos tentar juntos novamente!"*).
- **Modo Fácil por Padrão:** Todo novo jogo deve obrigatoriamente iniciar com a dificuldade mais fácil e acessível (🟢 Fácil), permitindo que a criança progrida com confiança.

### 6. 🤖 Arquitetura de IA Híbrida & Offline-First
- O sistema deve permanecer 100% funcional mesmo sem qualquer conexão com a internet (histórias locais, jogos lúdicos, rotinas, reconhecimento procedural e sintetizador de voz local).
- Em módulos com suporte a inteligência artificial generativa, priorize o suporte a ferramentas locais e CLI como **OpenCode CLI** e **Ollama** (`http://127.0.0.1:11434`), mantendo provedores de nuvem (Gemini, OpenAI, Groq) como opções externas configuráveis.

---

## 🛠️ Como Contribuir Passo a Passo

### 1. Criando seu Fork e Branch
1. Faça o fork do repositório no GitHub.
2. Clone o seu fork na sua máquina de desenvolvimento:
   ```bash
   git clone https://github.com/SEU_USUARIO/O.S-EDUCATIVO-PARA-CRIAN-AS.git
   cd O.S-EDUCATIVO-PARA-CRIAN-AS
   ```
3. Crie uma branch específica para sua funcionalidade ou correção:
   ```bash
   git checkout -b feat/novo-jogo-matematica
   # ou
   git checkout -b fix/interrupcao-audio-arcade
   ```

### 2. Padrão de Commits Semânticos
Utilize mensagens de commit semânticas e claras baseadas na convenção *Conventional Commits*:
- `feat:` Inclusão de uma nova funcionalidade, jogo, história ou módulo.
- `fix:` Correção de um bug ou falha de comportamento.
- `perf:` Melhoria comprovada de desempenho ou redução de consumo de CPU/RAM.
- `docs:` Atualizações ou correções na documentação (README, guias).
- `refactor:` Refatoração de código sem alterar o comportamento externo.
- `style:` Ajustes estéticos, formatação ou alinhamento visual.

Exemplo:
```bash
git commit -m "feat(arcade): adicionar novo jogo de corrida com nivel facil inicial"
```

### 3. Validação Local Antes de Enviar o Pull Request
Antes de realizar o push da sua branch, realize sempre a validação local:
1. **Verificação de Compilação Python:**
   ```bash
   python -m compileall .
   ```
   Certifique-se de que nenhum arquivo apresente erros de sintaxe.
2. **Teste de Execução do Servidor:**
   ```bash
   python run_server.py 8000
   ```
   Abra `http://localhost:8000` e teste o fluxo completo das telas afetadas.
3. **Auditoria de Segredos e Informações Privadas:**
   Certifique-se de que nenhum arquivo modificado contenha tokens de API, senhas ou dados privados.
4. **Verificação de Responsividade:**
   No navegador, abra as Ferramentas do Desenvolvedor (F12) e emule a resolução de tela **1024 x 600**. Verifique se todos os botões e informações estão acessíveis sem cortes indesejados.

### 4. Abrindo o Pull Request
- Submeta seu Pull Request para a branch `main` do repositório oficial.
- Descreva detalhadamente o que foi implementado, os arquivos modificados e como o teste foi realizado.
- Preencha todos os itens do checklist do nosso template de Pull Request.

---

## 💡 Ideias Abertas para a Comunidade

Procurando por onde começar? Aqui estão algumas áreas que adoraríamos receber contribuições:
- 🎨 **Novos Jogos Educativos 2D:** Jogos de lógica, memória, musicalização ou coordenação motora leves em HTML5 Canvas.
- 📖 **Novas Histórias e Livros Infantis:** Livros ilustrados interativos com valores éticos, amizade, ciência e imaginação.
- 🌍 **Expansão de Módulos de Idiomas:** Novos cartões de vocabulário com pronúncia e saudações de países ao redor do mundo.
- 🐧 **Suporte a Novas Distribuições Linux Leves:** Melhorias no script `./pkg` para suportar novas distribuições focadas em computadores antigos (Puppy Linux, Bodhi Linux, Alpine Kiosk).
- ♿ **Acessibilidade e Usabilidade:** Modos de alto contraste e adaptações para crianças com necessidades especiais.

Muito obrigado por fazer parte da construção de um sistema operacional carinhoso, inteligente e acessível para crianças! 🚀
