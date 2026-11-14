import re, os

# 1. Atualizar run_server.py
server_path = r'C:\Users\User\.gemini\antigravity\scratch\jarvis-kids-os\run_server.py'
with open(server_path, 'r', encoding='utf-8') as f:
    server_code = f.read()

# 1.1 Inserir mtime cache no obter_template_cache
old_template_cache = """def obter_template_cache(nome_arquivo: str) -> bytes:
    \"\"\"Carrega o template HTML em cache de memória RAM para 0ms de I/O em disco no Netbook.\"\"\"
    if nome_arquivo not in _TEMPLATE_RAM_CACHE:
        caminho = os.path.join(TEMPLATES_DIR, nome_arquivo)
        with open(caminho, "rb") as f:
            _TEMPLATE_RAM_CACHE[nome_arquivo] = f.read()
    return _TEMPLATE_RAM_CACHE[nome_arquivo]"""

new_template_cache = """_TEMPLATE_MTIME_CACHE = {}

def obter_template_cache(nome_arquivo: str) -> bytes:
    \"\"\"Carrega o template HTML em RAM com recarga automática imediata ao modificar o arquivo.\"\"\"
    caminho = os.path.join(TEMPLATES_DIR, nome_arquivo)
    try:
        mtime = os.path.getmtime(caminho)
    except Exception:
        mtime = 0
    if nome_arquivo not in _TEMPLATE_RAM_CACHE or _TEMPLATE_MTIME_CACHE.get(nome_arquivo) != mtime:
        with open(caminho, "rb") as f:
            _TEMPLATE_RAM_CACHE[nome_arquivo] = f.read()
            _TEMPLATE_MTIME_CACHE[nome_arquivo] = mtime
    return _TEMPLATE_RAM_CACHE[nome_arquivo]"""

if old_template_cache in server_code:
    server_code = server_code.replace(old_template_cache, new_template_cache, 1)
    print("1.1 obter_template_cache atualizado com auto-reload por mtime!")

# 1.2 Inserir headers de no-cache no / e /admin
old_index_headers = """    headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Permissions-Policy": "microphone=(self), camera=(self)",
        "Access-Control-Allow-Origin": "*",
    }
    return Response(body=conteudo, status_code=200, headers=headers)


@app.route("/admin")
def painel_admin(request: Request):
    \"\"\"Serve o painel dos pais com autenticação e entrega instantânea em RAM.\"\"\"
    conteudo = obter_template_cache("painel_pais.html")
    headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Permissions-Policy": "microphone=(self), camera=(self)",
        "Access-Control-Allow-Origin": "*",
    }"""

new_index_headers = """    headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Permissions-Policy": "microphone=(self), camera=(self)",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return Response(body=conteudo, status_code=200, headers=headers)


@app.route("/admin")
def painel_admin(request: Request):
    \"\"\"Serve o painel dos pais com autenticação e entrega instantânea em RAM.\"\"\"
    conteudo = obter_template_cache("painel_pais.html")
    headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Permissions-Policy": "microphone=(self), camera=(self)",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }"""

if old_index_headers in server_code:
    server_code = server_code.replace(old_index_headers, new_index_headers, 1)
    print("1.2 Headers Cache-Control no-cache inseridos nas rotas / e /admin!")

with open(server_path, 'w', encoding='utf-8') as f:
    f.write(server_code)


# 2. Atualizar templates/hud_jarvis.html
hud_path = r'C:\Users\User\.gemini\antigravity\scratch\jarvis-kids-os\templates\hud_jarvis.html'
with open(hud_path, 'r', encoding='utf-8') as f:
    hud_code = f.read()

# 2.1 Botão de Concluir Livro na última página: visual dourado pulsante de conquista
old_btn_finish_html = """${pageIdx < book.pages.length - 1
              ? '<button type="button" class="big-btn" style="background:#10b981; font-size:1.2rem; padding:14px 26px;" id="btn-next">Próxima Página ➡</button>'
              : '<button type="button" class="big-btn" style="background:#eab308; color:#0f172a; font-size:1.2rem; padding:14px 26px;" id="btn-finish">🏆 Concluir Livro e Ganhar Medalha!</button>'}"""

new_btn_finish_html = """${pageIdx < book.pages.length - 1
              ? '<button type="button" class="big-btn" style="background:#10b981; font-size:1.2rem; padding:14px 26px;" id="btn-next">Próxima Página ➡</button>'
              : '<button type="button" class="big-btn" style="background:linear-gradient(135deg, #f59e0b, #d97706); border:3px solid #fef08a; color:#0f172a; font-size:1.3rem; font-weight:900; padding:14px 28px; border-radius:18px; box-shadow:0 0 22px rgba(245,158,11,0.55); animation:pulse 1.4s infinite; cursor:pointer;" id="btn-finish">🌟 CONCLUIR HISTÓRIA! (+2 ⭐)</button>'}"""

assert old_btn_finish_html in hud_code, "old_btn_finish_html não encontrado!"
hud_code = hud_code.replace(old_btn_finish_html, new_btn_finish_html, 1)
print("2.1 Botão Concluir História estilizado com visual de conquista!")

# 2.2 Substituir a ação de clique do btn-finish para chamar concluirLivroComCelebracao
old_finish_action = """      if (pageIdx > 0) document.getElementById('btn-prev').onclick = () => openBookPage(body, bookIdx, pageIdx - 1);
      if (pageIdx < book.pages.length - 1) {
        document.getElementById('btn-next').onclick = () => openBookPage(body, bookIdx, pageIdx + 1);
      } else {
        document.getElementById('btn-finish').onclick = () => {
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
        };
      }"""

new_finish_action = """      if (pageIdx > 0) document.getElementById('btn-prev').onclick = () => openBookPage(body, bookIdx, pageIdx - 1);
      if (pageIdx < book.pages.length - 1) {
        document.getElementById('btn-next').onclick = () => openBookPage(body, bookIdx, pageIdx + 1);
      } else {
        const btnFinish = document.getElementById('btn-finish');
        if (btnFinish) {
          btnFinish.onclick = () => {
            concluirLivroComCelebracao(body, bookIdx);
          };
        }
      }"""

assert old_finish_action in hud_code, "old_finish_action não encontrado!"
hud_code = hud_code.replace(old_finish_action, new_finish_action, 1)
print("2.2 Ação de clique do btn-finish conectada a concluirLivroComCelebracao!")

# 2.3 Implementar a função concluirLivroComCelebracao logo após openBookPage
old_book_end = """      if (pageIdx > 0) document.getElementById('btn-prev').onclick = () => openBookPage(body, bookIdx, pageIdx - 1);
      if (pageIdx < book.pages.length - 1) {
        document.getElementById('btn-next').onclick = () => openBookPage(body, bookIdx, pageIdx + 1);
      } else {
        const btnFinish = document.getElementById('btn-finish');
        if (btnFinish) {
          btnFinish.onclick = () => {
            concluirLivroComCelebracao(body, bookIdx);
          };
        }
      }
    }"""

new_book_end = """      if (pageIdx > 0) document.getElementById('btn-prev').onclick = () => openBookPage(body, bookIdx, pageIdx - 1);
      if (pageIdx < book.pages.length - 1) {
        document.getElementById('btn-next').onclick = () => openBookPage(body, bookIdx, pageIdx + 1);
      } else {
        const btnFinish = document.getElementById('btn-finish');
        if (btnFinish) {
          btnFinish.onclick = () => {
            concluirLivroComCelebracao(body, bookIdx);
          };
        }
      }
    }

    // TELA DE VITÓRIA & CELEBRAÇÃO DA HISTÓRIA (100% PENSADA PARA CRIANÇAS DE 4 ANOS)
    function concluirLivroComCelebracao(body, bookIdx) {
      const book = appState.books[bookIdx];
      const childName = (appState.config && appState.config.child_name) || 'Campeão';

      // 1. Resposta imediata em 0ms: efeitos sonoros, confetes e estrelas
      playCelebrationFanfare();
      playSfxCoin();
      dispararConfetesDopamina(90);
      dispararChuvaCoracoes(70);

      // 2. Incrementar estrelas e livros lidos imediatamente no estado e DOM
      addStar(2);
      appState.books_read_today = (appState.books_read_today || 0) + 1;
      const bBadge = document.getElementById('books-badge');
      if (bBadge) bBadge.textContent = `📖 ${appState.books_read_today}`;

      // 3. Renderizar a Tela Épica de Conquista da História (sem fechar o modal no susto!)
      const lastPage = book.pages && book.pages.length ? book.pages[book.pages.length - 1] : {};
      const iconeCena = SCENE_ICONS[lastPage.scene] || '🌟🏆';

      body.innerHTML = `
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:12px; height:100%; min-height:420px; gap:14px; animation:bounceIn 0.5s ease; box-sizing:border-box;">
          
          <!-- PERSONAGEM / CENA EM TAMANHO GIGANTE ILUMINADO -->
          <div style="font-size:5.8rem; line-height:1; animation:pulse 1.4s infinite; filter:drop-shadow(0 0 26px rgba(250,204,21,0.65)); cursor:pointer;" onclick="playSfxCoin(); dispararConfetesDopamina(50);" title="Toque para comemorar!">
            ${iconeCena}
          </div>

          <!-- TÍTULO DE CONQUISTA VIBRANTE -->
          <div>
            <div style="font-size:2rem; font-weight:900; color:#facc15; text-shadow:0 0 16px rgba(250,204,21,0.6); letter-spacing:0.5px;">
              🎉 PARABÉNS, ${childName.toUpperCase()}!
            </div>
            <div style="font-size:1.25rem; font-weight:800; color:#ffffff; margin-top:4px;">
              Você leu toda a história de <span style="color:#38bdf8;">${book.title}</span>!
            </div>
          </div>

          <!-- MEDALHA DE DUAS ESTRELAS DE LEITOR -->
          <div style="display:flex; gap:14px; align-items:center; justify-content:center; background:linear-gradient(135deg, rgba(234,179,8,0.22), rgba(15,23,42,0.8)); border:2px solid #eab308; border-radius:24px; padding:10px 24px; box-shadow:0 4px 20px rgba(234,179,8,0.3);">
            <span style="font-size:2.8rem; animation:pulse 1s infinite;">⭐</span>
            <div style="text-align:left;">
              <div style="font-size:1.15rem; font-weight:900; color:#fef08a;">+2 ESTRELAS DE SUPER LEITOR!</div>
              <div style="font-size:0.88rem; color:#bae6fd;">Total de histórias lidas hoje: <b style="color:#fff;">${appState.books_read_today}</b></div>
            </div>
            <span style="font-size:2.8rem; animation:pulse 1s infinite;">⭐</span>
          </div>

          <!-- MORAL DA HISTÓRIA NARRADA -->
          ${book.moral ? `
            <div style="background:#09192f; border:2px solid #38bdf8; border-radius:18px; padding:12px 20px; max-width:640px; box-shadow:0 4px 16px rgba(56,189,248,0.2);">
              <div style="font-size:0.85rem; font-weight:900; color:#38bdf8; letter-spacing:0.5px; margin-bottom:4px;">💡 LIÇÃO DE HOJE DO JARVIS:</div>
              <div style="font-size:1.12rem; font-weight:800; color:#ffffff; line-height:1.4;">
                ${book.moral}
              </div>
            </div>
          ` : ''}

          <!-- BOTÕES GIGANTES TÁTEIS ADAPTADOS PARA UMA CRIANÇA DE 4 ANOS -->
          <div style="display:flex; gap:12px; flex-wrap:wrap; justify-content:center; margin-top:4px;">
            <button type="button" class="big-btn" style="background:#0284c7; border:3px solid #38bdf8; color:#fff; font-size:1.18rem; font-weight:900; padding:12px 24px; border-radius:16px; display:flex; align-items:center; gap:8px; box-shadow:0 4px 14px rgba(2,132,199,0.4);" onclick="voltarTelaModal()">
              <span style="font-size:1.6rem;">📚</span> Outras Histórias
            </button>
            <button type="button" class="big-btn" style="background:#15803d; border:3px solid #86efac; color:#fff; font-size:1.18rem; font-weight:900; padding:12px 24px; border-radius:16px; display:flex; align-items:center; gap:8px; box-shadow:0 4px 14px rgba(21,128,61,0.4);" onclick="openBookPage(document.getElementById('modal-body'), ${bookIdx}, 0)">
              <span style="font-size:1.6rem;">🔄</span> Ouvir de Novo
            </button>
            <button type="button" class="big-btn" style="background:#d97706; border:3px solid #fde047; color:#fff; font-size:1.18rem; font-weight:900; padding:12px 24px; border-radius:16px; display:flex; align-items:center; gap:8px; box-shadow:0 4px 14px rgba(217,119,6,0.4);" onclick="closeModal()">
              <span style="font-size:1.6rem;">🏠</span> Voltar pro Jarvis
            </button>
          </div>
        </div>
      `;

      // 4. Voz amigável do Jarvis falando com entusiasmo para a criança
      const moralTexto = book.moral ? ` E a grande lição de hoje é: ${book.moral}` : '';
      speak(`Parabéns, ${childName}! Você leu a história ${book.title} e ganhou duas estrelas de Super Leitor!${moralTexto}`);

      // 5. Sincronização em segundo plano não-bloqueante com a API
      fetch('/api/book-finished', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ book_id: book.id })
      }).then(res => res.json()).then(d => {
        if (d && d.books_read_today !== undefined) {
          appState.books_read_today = d.books_read_today;
          const bb = document.getElementById('books-badge');
          if (bb) bb.textContent = `📖 ${d.books_read_today}`;
        }
      }).catch(err => console.warn('Erro ao sincronizar livro lido:', err));
    }"""

assert old_book_end in hud_code, "old_book_end não encontrado!"
hud_code = hud_code.replace(old_book_end, new_book_end, 1)
print("2.3 Função concluirLivroComCelebracao inserida com sucesso!")

with open(hud_path, 'w', encoding='utf-8') as f:
    f.write(hud_code)

print("Todas as melhorias foram aplicadas com sucesso!")
