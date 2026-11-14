import re

path = r'C:\Users\User\.gemini\antigravity\scratch\jarvis-kids-os\templates\hud_jarvis.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Original length:", len(content))

# 1. Correção da tag de canvas-confetti e funções de confete globais
target_confetti = """    <!-- BIBLIOTECAS OPEN-SOURCE LEVES PARA O INTEL ATOM (0% CPU) -->
  <script src="/static/libs/canvas-confetti.min.js">
    // =========================================================================
    // KIOSK HARDENING & BLOQUEIO DE SELEÇÃO / CLIQUE DIREITO
    // =========================================================================
    window.addEventListener('contextmenu', e => e.preventDefault());
    window.addEventListener('dragstart', e => e.preventDefault());

    window.dispararConfetesDopamina = function(count = 50) {
      if (typeof window.confetti === 'function') {
        window.confetti({ particleCount: count });
      }
    };
  </script>
  <script src="/static/libs/sweetalert2.all.min.js"></script>
  <script src="/static/libs/sortable.min.js"></script>"""

replacement_confetti = """    <!-- BIBLIOTECAS OPEN-SOURCE LEVES PARA O INTEL ATOM (0% CPU) -->
  <script src="/static/libs/canvas-confetti.min.js"></script>
  <script src="/static/libs/sweetalert2.all.min.js"></script>
  <script src="/static/libs/sortable.min.js"></script>
  <script>
    // =========================================================================
    // KIOSK HARDENING & BLOQUEIO DE SELEÇÃO / CLIQUE DIREITO
    // =========================================================================
    window.addEventListener('contextmenu', e => e.preventDefault());
    window.addEventListener('dragstart', e => e.preventDefault());

    window.dispararConfetesDopamina = function(count = 50) {
      try {
        if (typeof window.confetti === 'function') {
          window.confetti({ particleCount: count, origin: { y: 0.6 } });
        }
      } catch (e) {}
    };

    window.dispararChuvaCoracoes = function(count = 50) {
      try {
        if (typeof window.confetti === 'function') {
          window.confetti({
            particleCount: count,
            spread: 70,
            origin: { y: 0.6 }
          });
        }
      } catch (e) {}
    };
  </script>"""

assert target_confetti in content, "target_confetti não encontrado!"
content = content.replace(target_confetti, replacement_confetti, 1)
print("1. Tag de script de confetti corrigida!")

# 2. Definições globais de áudio de fanfarra, chuva de corações e showHudToast
target_audio = """    function playSfxError() {
      try {
        destravarAudioNavegador();
        if (!audioCtx) return;
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(260, now);
        osc.frequency.exponentialRampToValueAtTime(170, now + 0.2);
        gain.gain.setValueAtTime(0.14, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.2);
        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch (err) {}
        };
      } catch (e) {}
    }"""

replacement_audio = """    function playSfxError() {
      try {
        destravarAudioNavegador();
        if (!audioCtx) return;
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(260, now);
        osc.frequency.exponentialRampToValueAtTime(170, now + 0.2);
        gain.gain.setValueAtTime(0.14, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.2);
        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch (err) {}
        };
      } catch (e) {}
    }

    // FANFARRA TRIUNFAL DE VITÓRIA (WEB AUDIO API - 0ms LATÊNCIA, 0 REDE, 0 ENGASGO)
    function playCelebrationFanfare() {
      try {
        destravarAudioNavegador();
        if (!audioCtx) return;
        const notes = [523.25, 659.25, 783.99, 1046.50, 1318.51];
        notes.forEach((freq, idx) => {
          setTimeout(() => playTone(freq, 150, 'triangle', 0.22), idx * 80);
        });
      } catch (e) {}
    }
    window.playCelebrationFanfare = playCelebrationFanfare;

    function dispararChuvaCoracoes(count = 50) {
      try {
        if (typeof window.confetti === 'function') {
          window.confetti({ particleCount: count, spread: 70, origin: { y: 0.6 } });
        }
      } catch (e) {}
    }
    window.dispararChuvaCoracoes = dispararChuvaCoracoes;

    window.showHudToast = function(msg, isError = false) {
      if (typeof showToast === 'function') showToast(msg, isError);
    };

    // Fallbacks seguros de higiene para prevenir referências nulas
    window.eliminarGerme = window.eliminarGerme || function() {};
    window.escovarParteDente = window.escovarParteDente || function() {};
    window.concluirEtapaBanho = window.concluirEtapaBanho || function() {};
    window.concluirUnhasCabelo = window.concluirUnhasCabelo || function() {};"""

assert target_audio in content, "target_audio não encontrado!"
content = content.replace(target_audio, replacement_audio, 1)
print("2. playCelebrationFanfare e helpers de áudio adicionados!")

# 3. Lógica do botão Concluir Livro (livros_hoje e resposta instantânea 0ms)
target_book = """        document.getElementById('btn-finish').onclick = async () => {
          const res = await fetch('/api/book-finished', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ book_id: book.id })
          });
          const d = await res.json();
          appState.books_read_today = d.books_read_today;
          document.getElementById('books-badge').textContent = `📖 Livros hoje: ${d.books_read_today}`;
          addStar(2);
          const moralTexto = book.moral ? ` E a grande lição de hoje é: ${book.moral}` : '';
          speak(`Parabéns, ${appState.config.child_name || 'Campeão'}! Você leu o livro ${book.title} e ganhou duas estrelas de Super Leitor!${moralTexto}`);
          voltarTelaModal();
        };"""

replacement_book = """        document.getElementById('btn-finish').onclick = () => {
          // Resposta imediata em 0ms: fanfarra, confetes, estrelas e fala
          playCelebrationFanfare();
          dispararChuvaCoracoes(60);
          addStar(2);
          const moralTexto = book.moral ? ` E a grande lição de hoje é: ${book.moral}` : '';
          speak(`Parabéns, ${appState.config.child_name || 'Campeão'}! Você leu o livro ${book.title} e ganhou duas estrelas de Super Leitor!${moralTexto}`);
          voltarTelaModal();

          // Sincronização em segundo plano não-bloqueante
          fetch('/api/book-finished', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ book_id: book.id })
          }).then(res => res.json()).then(d => {
            if (d && d.books_read_today !== undefined) {
              appState.books_read_today = d.books_read_today;
              const bBadge = document.getElementById('books-badge');
              if (bBadge) bBadge.textContent = `📖 Livros hoje: ${d.books_read_today}`;
            }
          }).catch(err => console.warn('Erro ao sincronizar livro lido:', err));
        };"""

assert target_book in content, "target_book não encontrado!"
content = content.replace(target_book, replacement_book, 1)
print("3. Conclusão de livros otimizada para 0ms e segura!")

# 4. Detetive Stark (Jogo dos 7 Erros) - Vitória imediata, banner épico e botões de ação
target_detetive = """    async function clicarErroDetetive(id) {
      if (errosDetetiveEncontrados.includes(id)) return;
      errosDetetiveEncontrados.push(id);
      playTone(784, 120);
      showToast(`🎯 Erro ${errosDetetiveEncontrados.length} de 7 Encontrado!`);

      if (errosDetetiveEncontrados.length >= 7) {
        playCelebrationFanfare();
        if (typeof window.confetti === 'function') window.confetti({ particleCount: 50 });
        dispararChuvaCoracoes();
        speak(`Incrível, super detetive! Você usou seus olhos de águia e encontrou todos os 7 erros! Ganhou 10 moedas de ouro!`);
        await fetch('/api/fichas/bonificar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantidade: 10, motivo: 'jogo_7_erros_detetive' })
        }).catch(() => null);
        const pEl = document.getElementById('pote-fichas-val');
        if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 10;
      } else {
        speak(`Muito bem! Você encontrou o erro número ${errosDetetiveEncontrados.length}! Continue procurando!`);
      }

      const b = document.querySelector('.modal-body');
      if (b) renderDetectiveErrorsBody(b);
    }"""

replacement_detetive = """    function clicarErroDetetive(id) {
      if (errosDetetiveEncontrados.includes(id)) return;
      errosDetetiveEncontrados.push(id);
      playTone(784, 120);
      showToast(`🎯 Erro ${errosDetetiveEncontrados.length} de 7 Encontrado!`);

      if (errosDetetiveEncontrados.length >= 7) {
        playCelebrationFanfare();
        dispararChuvaCoracoes(70);
        speak(`Incrível, super detetive ${appState.config.child_name || 'Campeão'}! Você usou seus olhos de águia e encontrou todos os 7 erros! Ganhou 10 moedas de ouro!`);
        showToast('🏆 Missão Cumprida! +10 Moedas de Ouro!');
        
        // Bonificação imediata no pote visual (0ms)
        const pEl = document.getElementById('pote-fichas-val');
        if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 10;

        // Requisição não-bloqueante em segundo plano
        fetch('/api/fichas/bonificar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantidade: 10, motivo: 'jogo_7_erros_detetive' })
        }).catch(() => null);
      } else {
        speak(`Muito bem! Você encontrou o erro número ${errosDetetiveEncontrados.length}! Continue procurando!`);
      }

      const b = document.querySelector('.modal-body');
      if (b) renderDetectiveErrorsBody(b);
    }

    function reiniciarJogoDetetive() {
      errosDetetiveEncontrados = [];
      playTone(523, 80);
      const b = document.querySelector('.modal-body');
      if (b) renderDetectiveErrorsBody(b);
      speak('Cena reiniciada! Abra bem os olhinhos e encontre os 7 erros!');
    }"""

assert target_detetive in content, "target_detetive não encontrado!"
content = content.replace(target_detetive, replacement_detetive, 1)
print("4. clicarErroDetetive refatorado com sucesso!")

# 4.1 Adicionar Banner de Vitória no renderDetectiveErrorsBody
target_detetive_body = """          <div style="display:flex; justify-content:space-between; align-items:center; background:#0f172a; padding:6px 14px; border-radius:12px; border:1px solid #334155;">
            <div style="font-size:0.95rem; font-weight:900; color:#38bdf8;">
              🔍 Erros Encontrados: <span style="color:#22c55e;">${errosDetetiveEncontrados.length}</span> / 7
            </div>
            <button type="button" class="big-btn" style="background:#0284c7; border:1px solid #38bdf8; color:#fff; padding:4px 12px; border-radius:8px; font-size:0.85rem; font-weight:800;" onclick="darDicaDetetive()">
              💡 Pedir Dica ao Jarvis
            </button>
          </div>"""

replacement_detetive_body = """          ${errosDetetiveEncontrados.length >= 7 ? `
            <div style="background:linear-gradient(135deg, #15803d, #166534); border:2px solid #86efac; border-radius:14px; padding:10px 16px; display:flex; align-items:center; justify-content:space-between; box-shadow:0 0 25px rgba(34,197,94,0.4); animation:pulse 2s infinite;">
              <div>
                <div style="font-size:1.15rem; font-weight:900; color:#fff;">🏆 MISSÃO DE DETETIVE CUMPRIDA! (7 / 7)</div>
                <div style="font-size:0.85rem; color:#bbf7d0;">Olhos de águia imbatíveis! Você ganhou +10 Moedas de Ouro 🪙!</div>
              </div>
              <div style="display:flex; gap:8px;">
                <button type="button" class="big-btn" style="background:#f59e0b; border:2px solid #fde047; color:#000; font-weight:900; padding:6px 14px; border-radius:10px; font-size:0.88rem;" onclick="reiniciarJogoDetetive()">
                  🔄 Jogar de Novo
                </button>
                <button type="button" class="big-btn" style="background:#0284c7; border:2px solid #38bdf8; color:#fff; font-weight:900; padding:6px 14px; border-radius:10px; font-size:0.88rem;" onclick="voltarTelaModal()">
                  🏠 Outro Jogo
                </button>
              </div>
            </div>
          ` : `
            <div style="display:flex; justify-content:space-between; align-items:center; background:#0f172a; padding:6px 14px; border-radius:12px; border:1px solid #334155;">
              <div style="font-size:0.95rem; font-weight:900; color:#38bdf8;">
                🔍 Erros Encontrados: <span style="color:#22c55e;">${errosDetetiveEncontrados.length}</span> / 7
              </div>
              <button type="button" class="big-btn" style="background:#0284c7; border:1px solid #38bdf8; color:#fff; padding:4px 12px; border-radius:8px; font-size:0.85rem; font-weight:800;" onclick="darDicaDetetive()">
                💡 Pedir Dica ao Jarvis
              </button>
            </div>
          `}"""

assert target_detetive_body in content, "target_detetive_body não encontrado!"
content = content.replace(target_detetive_body, replacement_detetive_body, 1)
print("4.1 Banner de vitória no Jogo dos 7 Erros integrado!")

# 5. Escavação de Dinossauros: Vitória automática no 6º bloco, próximo dinossauro e comemoração instantânea
target_dino_escavar = """    function escavarBlocoDino(idx) {
      if (blocosDinoEscavadosSet.has(idx)) return;
      blocosDinoEscavadosSet.add(idx);
      
      const parte = PARTES_FOSSIL_DINO[idx];
      if (ferramentaDinoAtiva === 'martelo') playTone(220 + blocosDinoEscavadosSet.size * 50, 90, 'square');
      else if (ferramentaDinoAtiva === 'pincel') playTone(540 + blocosDinoEscavadosSet.size * 50, 90, 'sine');
      else playTone(740 + blocosDinoEscavadosSet.size * 50, 90, 'triangle');

      showToast(`⛏️ ${parte.nome} limpo com sucesso! (${blocosDinoEscavadosSet.size}/6)`);

      if (blocosDinoEscavadosSet.size >= 6) {
        tocarRugidoDinoStark();
        playCelebrationFanfare();
        if (typeof window.confetti === 'function') window.confetti({ particleCount: 50 });
        dispararChuvaCoracoes();
        const d = BANCO_DINOSSAUROS[dinoIdx];
        speak(`Incrível, paleontólogo! Você restaurou o esqueleto fóssil do ${d.nome}! Ele agora está vivo na galeria do museu!`);
      }

      const b = document.querySelector('.modal-body');
      if (b) renderDinosaurFossilsBody(b);
    }"""

replacement_dino_escavar = """    function escavarBlocoDino(idx) {
      if (blocosDinoEscavadosSet.has(idx)) return;
      blocosDinoEscavadosSet.add(idx);
      
      const parte = PARTES_FOSSIL_DINO[idx];
      if (ferramentaDinoAtiva === 'martelo') playTone(220 + blocosDinoEscavadosSet.size * 50, 90, 'square');
      else if (ferramentaDinoAtiva === 'pincel') playTone(540 + blocosDinoEscavadosSet.size * 50, 90, 'sine');
      else playTone(740 + blocosDinoEscavadosSet.size * 50, 90, 'triangle');

      showToast(`⛏️ ${parte.nome} limpo com sucesso! (${blocosDinoEscavadosSet.size}/6)`);

      if (blocosDinoEscavadosSet.size >= 6) {
        // Conclusão 100% imediata e automática no 6º bloco!
        tocarRugidoDinoStark();
        playCelebrationFanfare();
        dispararChuvaCoracoes(60);
        const d = BANCO_DINOSSAUROS[dinoIdx];
        speak(`Incrível, super paleontólogo ${appState.config.child_name || 'Campeão'}! Você restaurou o esqueleto fóssil do ${d.nome}! Ele agora está vivo na galeria do museu! Ganhou 10 moedas de ouro!`);
        showToast('🦖 Fóssil 100% Restaurado! +10 Moedas!');

        // Bonificação imediata no pote (0ms)
        const pEl = document.getElementById('pote-fichas-val');
        if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 10;

        // Envio assíncrono em segundo plano
        fetch('/api/fichas/bonificar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantidade: 10, motivo: 'paleontologia_dino' })
        }).catch(() => null);
      }

      const b = document.querySelector('.modal-body');
      if (b) renderDinosaurFossilsBody(b);
    }

    function proximoDinoEscavacao() {
      dinoIdx = (dinoIdx + 1) % BANCO_DINOSSAUROS.length;
      blocosDinoEscavadosSet.clear();
      playTone(523, 80);
      const b = document.querySelector('.modal-body');
      if (b) renderDinosaurFossilsBody(b);
      const d = BANCO_DINOSSAUROS[dinoIdx];
      speak(`Novo sítio de escavação: ${d.nome}! Limpe os 6 blocos de terra!`);
    }"""

assert target_dino_escavar in content, "target_dino_escavar não encontrado!"
content = content.replace(target_dino_escavar, replacement_dino_escavar, 1)
print("5. escavarBlocoDino e proximoDinoEscavacao configurados!")

# 5.1 Otimizar botões de vitória no renderDinosaurFossilsBody
target_dino_botoes = """              ${completo ? `
                <button type="button" class="big-btn" style="background:#22c55e; border:2px solid #86efac; color:#fff; padding:6px 18px; border-radius:10px; font-weight:900; font-size:0.95rem; margin-top:2px;" onclick="comemorarDinoCompleto()">
                  🎉 Fóssil 100% Restaurado! (+10 🪙)
                </button>
              ` : ''}"""

replacement_dino_botoes = """              ${completo ? `
                <div style="display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin-top:2px; animation:bounceIn 0.5s ease;">
                  <button type="button" class="big-btn" style="background:#15803d; border:2px solid #86efac; color:#fff; padding:6px 16px; border-radius:10px; font-weight:900; font-size:0.92rem;" onclick="proximoDinoEscavacao()">
                    🦖 Próximo Dinossauro! ➔
                  </button>
                  <button type="button" class="big-btn" style="background:#d97706; border:2px solid #fde047; color:#fff; padding:6px 16px; border-radius:10px; font-weight:900; font-size:0.92rem;" onclick="alternarModoDino('museu')">
                    🏛️ Ver na Galeria do Museu
                  </button>
                  <button type="button" class="big-btn" style="background:#334155; border:1px solid #64748b; color:#e2e8f0; padding:6px 12px; border-radius:10px; font-weight:800; font-size:0.85rem;" onclick="blocosDinoEscavadosSet.clear(); const b = document.querySelector('.modal-body'); if (b) renderDinosaurFossilsBody(b);">
                    🔄 Escavar de Novo
                  </button>
                </div>
              ` : ''}"""

assert target_dino_botoes in content, "target_dino_botoes não encontrado!"
content = content.replace(target_dino_botoes, replacement_dino_botoes, 1)
print("5.1 Botões de vitória dos dinossauros otimizados!")

# 6. Tornar assíncronas e imediatas as bonificações nos outros jogos

# 6.1 Quiz Astronauta
target_quiz_astro = """    async function responderQuizAstronauta(escolha, correta) {
      if (escolha === correta) {
        playCelebrationFanfare();
        if (typeof window.confetti === 'function') window.confetti({ particleCount: 50 });
        dispararChuvaCoracoes();
        speak(`Excelente resposta, astronauta! Você acertou na mosca! É ${correta}! Ganhou 5 moedas espaciais!`);
        showToast('🌟 Resposta Correta! +5 Moedas do Tesouro!');
        await fetch('/api/fichas/bonificar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantidade: 5, motivo: 'quiz_sistema_solar' })
        }).catch(() => null);
        const pEl = document.getElementById('pote-fichas-val');
        if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;
        const box = document.getElementById('quiz-astronauta-box');
        if (box) box.style.display = 'none';
      } else {"""

replacement_quiz_astro = """    function responderQuizAstronauta(escolha, correta) {
      if (escolha === correta) {
        playCelebrationFanfare();
        dispararChuvaCoracoes(50);
        speak(`Excelente resposta, astronauta ${appState.config.child_name || 'Campeão'}! Você acertou na mosca! É ${correta}! Ganhou 5 moedas espaciais!`);
        showToast('🌟 Resposta Correta! +5 Moedas do Tesouro!');
        
        const pEl = document.getElementById('pote-fichas-val');
        if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;
        const box = document.getElementById('quiz-astronauta-box');
        if (box) box.style.display = 'none';

        fetch('/api/fichas/bonificar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantidade: 5, motivo: 'quiz_sistema_solar' })
        }).catch(() => null);
      } else {"""

assert target_quiz_astro in content, "target_quiz_astro não encontrado!"
content = content.replace(target_quiz_astro, replacement_quiz_astro, 1)
print("6.1 Quiz Astronauta atualizado!")

# 6.2 Desafio dos Bichos
target_desafio_bicho = """    async function responderDesafioBicho(escolha, corretaId) {
      if (escolha === corretaId) {
        const bicho = BANCO_ANIMAIS_STARK.find(x => x.id === corretaId);
        playCelebrationFanfare();
        if (typeof window.confetti === 'function') window.confetti({ particleCount: 50 });
        dispararChuvaCoracoes();
        speak(`Sensacional, herói! Você reconheceu perfeitamente o som do ${bicho ? bicho.nome : 'animal'}! Ganhou 5 moedas!`);
        showToast('🎉 Acertou o Animal! +5 Moedas!');
        await fetch('/api/fichas/bonificar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantidade: 5, motivo: 'desafio_animais' })
        }).catch(() => null);
        const pEl = document.getElementById('pote-fichas-val');
        if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;
        const box = document.getElementById('desafio-bicho-box');
        if (box) box.style.display = 'none';
      } else {"""

replacement_desafio_bicho = """    function responderDesafioBicho(escolha, corretaId) {
      if (escolha === corretaId) {
        const bicho = BANCO_ANIMAIS_STARK.find(x => x.id === corretaId);
        playCelebrationFanfare();
        dispararChuvaCoracoes(50);
        speak(`Sensacional, herói! Você reconheceu perfeitamente o som do ${bicho ? bicho.nome : 'animal'}! Ganhou 5 moedas!`);
        showToast('🎉 Acertou o Animal! +5 Moedas!');
        
        const pEl = document.getElementById('pote-fichas-val');
        if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;
        const box = document.getElementById('desafio-bicho-box');
        if (box) box.style.display = 'none';

        fetch('/api/fichas/bonificar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantidade: 5, motivo: 'desafio_animais' })
        }).catch(() => null);
      } else {"""

assert target_desafio_bicho in content, "target_desafio_bicho não encontrado!"
content = content.replace(target_desafio_bicho, replacement_desafio_bicho, 1)
print("6.2 Desafio dos Bichos atualizado!")

# 6.3 Desafio dos 30s Relógio
target_desafio_30s = """          if (typeof window.confetti === 'function') window.confetti({ particleCount: 60 });
          playCelebrationFanfare();
          dispararChuvaCoracoes();
          speak(`Tempo esgotado! Missão superada com sucesso! Você é super veloz, super-herói! Ganhou 5 moedas!`);
          showToast('⚡ Desafio dos 30s Concluído! +5 Moedas!');
          await fetch('/api/fichas/bonificar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantidade: 5, motivo: 'desafio_30s_relogio' })
          }).catch(() => null);
          const pEl = document.getElementById('pote-fichas-val');
          if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;"""

replacement_desafio_30s = """          playCelebrationFanfare();
          dispararChuvaCoracoes(60);
          speak(`Tempo esgotado! Missão superada com sucesso! Você é super veloz, super-herói! Ganhou 5 moedas!`);
          showToast('⚡ Desafio dos 30s Concluído! +5 Moedas!');
          const pEl = document.getElementById('pote-fichas-val');
          if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;
          fetch('/api/fichas/bonificar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantidade: 5, motivo: 'desafio_30s_relogio' })
          }).catch(() => null);"""

assert target_desafio_30s in content, "target_desafio_30s não encontrado!"
content = content.replace(target_desafio_30s, replacement_desafio_30s, 1)
print("6.3 Desafio dos 30s Relógio atualizado!")

# 6.4 Validar Missão Relógio
target_validar_relogio = """    async function validarMissaoRelogio() {
      if (!missaoRelogioCorrente) return;
      if (horaRelogioAtual === missaoRelogioCorrente.hora && minutoRelogioAtual === missaoRelogioCorrente.min) {
        playCelebrationFanfare();
        if (typeof window.confetti === 'function') window.confetti({ particleCount: 50 });
        dispararChuvaCoracoes();
        speak(`Incrível, herói! Você acertou exatamente o horário de ${missaoRelogioCorrente.titulo}! Ganhou 5 moedas do tempo!`);
        showToast('⏰ Missão Cumprida! +5 Moedas do Tesouro!');
        await fetch('/api/fichas/bonificar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantidade: 5, motivo: 'missao_relogio_tempo' })
        }).catch(() => null);
        const pEl = document.getElementById('pote-fichas-val');
        if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;
        const box = document.getElementById('missao-relogio-box');
        if (box) box.style.display = 'none';
      } else {"""

replacement_validar_relogio = """    function validarMissaoRelogio() {
      if (!missaoRelogioCorrente) return;
      if (horaRelogioAtual === missaoRelogioCorrente.hora && minutoRelogioAtual === missaoRelogioCorrente.min) {
        playCelebrationFanfare();
        dispararChuvaCoracoes(50);
        speak(`Incrível, herói! Você acertou exatamente o horário de ${missaoRelogioCorrente.titulo}! Ganhou 5 moedas do tempo!`);
        showToast('⏰ Missão Cumprida! +5 Moedas do Tesouro!');
        const pEl = document.getElementById('pote-fichas-val');
        if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;
        const box = document.getElementById('missao-relogio-box');
        if (box) box.style.display = 'none';
        fetch('/api/fichas/bonificar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantidade: 5, motivo: 'missao_relogio_tempo' })
        }).catch(() => null);
      } else {"""

assert target_validar_relogio in content, "target_validar_relogio não encontrado!"
content = content.replace(target_validar_relogio, replacement_validar_relogio, 1)
print("6.4 Missão do Relógio atualizada!")

# 6.5 Experimento Vulcão
target_vulcao = """      playCelebrationFanfare();
      dispararChuvaCoracoes();
      speak(`CABUUUM! O vulcão entrou em erupção total! As bolhas de gás do bicarbonato com vinagre fizeram a lava subir e escorrer pela montanha! Experimento fantástico!`);
      showToast('🌋 Erupção Espetacular! +5 Moedas!');
      
      await fetch('/api/fichas/bonificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantidade: 5, motivo: 'experimento_vulcao' })
      }).catch(() => null);
      const pEl = document.getElementById('pote-fichas-val');
      if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;

      const b = document.querySelector('.modal-body');
      if (b) renderScienceLabBody(b);"""

replacement_vulcao = """      playCelebrationFanfare();
      dispararChuvaCoracoes(50);
      speak(`CABUUUM! O vulcão entrou em erupção total! As bolhas de gás do bicarbonato com vinagre fizeram a lava subir e escorrer pela montanha! Experimento fantástico!`);
      showToast('🌋 Erupção Espetacular! +5 Moedas!');
      
      const pEl = document.getElementById('pote-fichas-val');
      if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;

      fetch('/api/fichas/bonificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantidade: 5, motivo: 'experimento_vulcao' })
      }).catch(() => null);

      const b = document.querySelector('.modal-body');
      if (b) renderScienceLabBody(b);"""

assert target_vulcao in content, "target_vulcao não encontrado!"
content = content.replace(target_vulcao, replacement_vulcao, 1)
print("6.5 Vulcão de Ciências atualizado!")

# 6.6 Academia de Xadrez
target_xadrez = """    async function concluirDesafioXadrez() {
      playCelebrationFanfare();
      dispararChuvaCoracoes();
      speak(`Xeque-mate no tédio, mestre do xadrez! Você aprendeu as jogadas certas e ganhou 5 moedas reais!`);
      showToast('♟️ Mestre do Xadrez! +5 Moedas!');
      await fetch('/api/fichas/bonificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantidade: 5, motivo: 'academia_xadrez' })
      }).catch(() => null);
      const pEl = document.getElementById('pote-fichas-val');
      if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;
    }"""

replacement_xadrez = """    function concluirDesafioXadrez() {
      playCelebrationFanfare();
      dispararChuvaCoracoes(50);
      speak(`Xeque-mate no tédio, mestre do xadrez ${appState.config.child_name || 'Campeão'}! Você aprendeu as jogadas certas e ganhou 5 moedas reais!`);
      showToast('♟️ Mestre do Xadrez! +5 Moedas!');
      const pEl = document.getElementById('pote-fichas-val');
      if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + 5;
      fetch('/api/fichas/bonificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantidade: 5, motivo: 'academia_xadrez' })
      }).catch(() => null);
    }"""

assert target_xadrez in content, "target_xadrez não encontrado!"
content = content.replace(target_xadrez, replacement_xadrez, 1)
print("6.6 Academia de Xadrez atualizada!")

# 7. Salvar arquivo
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Todas as correções foram gravadas com sucesso no arquivo templates/hud_jarvis.html!")
