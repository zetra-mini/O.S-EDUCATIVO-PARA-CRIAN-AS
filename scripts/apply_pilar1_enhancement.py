import re

# 1. Atualizar run_server.py para incluir "missoes" no /api/state
server_path = r'C:\Users\User\.gemini\antigravity\scratch\jarvis-kids-os\run_server.py'
with open(server_path, 'r', encoding='utf-8') as f:
    server_code = f.read()

target_state_end = """"ultimo_recado_visto": REMOTE_STATE.get("ultimo_recado_visto"),
            "bateria": bat,
        }"""

replacement_state_end = """"ultimo_recado_visto": REMOTE_STATE.get("ultimo_recado_visto"),
            "bateria": bat,
            "missoes": listar_missoes_rotina(),
        }"""

if target_state_end in server_code:
    server_code = server_code.replace(target_state_end, replacement_state_end, 1)
    with open(server_path, 'w', encoding='utf-8') as f:
        f.write(server_code)
    print("1. run_server.py atualizado com 'missoes' no /api/state!")
else:
    print("1. run_server.py já contém 'missoes'.")


# 2. Atualizar templates/hud_jarvis.html
hud_path = r'C:\Users\User\.gemini\antigravity\scratch\jarvis-kids-os\templates\hud_jarvis.html'
with open(hud_path, 'r', encoding='utf-8') as f:
    hud_code = f.read()

# 2.1 Adicionar ID no top-missions-val se não tiver
if 'id="top-missions-val"' not in hud_code:
    old_badge_span = '<span style="color:#fef08a; font-size:0.88rem; font-weight:900;">Missões</span>'
    new_badge_span = '<span id="top-missions-val" style="color:#fef08a; font-size:0.88rem; font-weight:900;">Missões</span>'
    assert old_badge_span in hud_code, "old_badge_span não encontrado!"
    hud_code = hud_code.replace(old_badge_span, new_badge_span, 1)
    print("2.1 ID top-missions-val inserido com sucesso!")

# 2.2 Adicionar Card das Missões do Herói na Gaveta de Atividades se não tiver
if 'Quartel-General de Missões' not in hud_code:
    old_drawer_top = '<div class="drawer-content" id="drawer-content">\n      <!-- PÁGINA 1: LEITURA, LETRAS, NÚMEROS E IDIOMAS -->\n      <div class="drawer-card-item drawer-card-p1" onclick="abrirAtividadeDrawer(openBooksLibrary)">'
    new_drawer_top = """<div class="drawer-content" id="drawer-content">
      <!-- PÁGINA 1: LEITURA, LETRAS, NÚMEROS E IDIOMAS -->
      <div class="drawer-card-item drawer-card-p1" style="background:linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(15, 23, 42, 0.8)); border:2px solid #eab308;" onclick="abrirAtividadeDrawer(abrirModalMissoesHeroi)">
        <div class="drawer-card-icon" style="filter:drop-shadow(0 0 8px rgba(234, 179, 8, 0.6));">📋</div>
        <div>
          <div class="drawer-card-name" style="color:#fef08a; font-weight:900;">Quartel-General de Missões</div>
          <div class="drawer-card-desc">Rotina diária, hábitos e recompensas em ouro</div>
        </div>
      </div>

      <div class="drawer-card-item drawer-card-p1" onclick="abrirAtividadeDrawer(openBooksLibrary)">"""
    assert old_drawer_top in hud_code, "old_drawer_top não encontrado!"
    hud_code = hud_code.replace(old_drawer_top, new_drawer_top, 1)
    print("2.2 Card de missões inserido na gaveta de atividades!")

# 2.3 Atualizar loadState para alimentar missoesHeroiCache e badge se não tiver
if 'missoesHeroiCache = data.missoes;' not in hud_code:
    target_loadstate = """      if (data.bateria) {
        atualizarMonitorBateria(data.bateria);
      }"""
    replacement_loadstate = """      if (data.bateria) {
        atualizarMonitorBateria(data.bateria);
      }
      if (data.missoes && Array.isArray(data.missoes)) {
        missoesHeroiCache = data.missoes;
        const total = missoesHeroiCache.length;
        const pendentes = missoesHeroiCache.filter(m => !m.cumprida).length;
        if (typeof atualizarBadgeMissoesTop === 'function') {
          atualizarBadgeMissoesTop(pendentes, total);
        }
      }"""
    assert target_loadstate in hud_code, "target_loadstate não encontrado!"
    hud_code = hud_code.replace(target_loadstate, replacement_loadstate, 1)
    print("2.3 loadState atualizado para receber missões!")

# 2.4 Substituir o bloco completo do Pilar 1
start_marker = '    // PILAR 1: MISS'
end_marker = '    // PILAR 3: KIOSK BYPASS'

p1 = hud_code.find(start_marker)
p2 = hud_code.find(end_marker)
assert p1 != -1 and p2 != -1, f"Marcadores p1 ({p1}) ou p2 ({p2}) não encontrados!"

sep1 = hud_code.rfind('    // ====', 0, p1)
sep2 = hud_code.rfind('    // ====', 0, p2)
assert sep1 != -1 and sep2 != -1, f"Separadores sep1 ({sep1}) ou sep2 ({sep2}) não encontrados!"

new_pilar1_code = """    // =========================================================================
    // PILAR 1: MISSÕES DO HERÓI (ROTINA DIÁRIA) - QUARTEL-GENERAL GAMIFICADO
    // =========================================================================
    let filtroMissoesHeroi = 'todas';
    let missoesHeroiCache = [];

    function atualizarBadgeMissoesTop(pendentes, total) {
      const el = document.getElementById('top-missions-badge');
      const valEl = document.getElementById('top-missions-val');
      if (!el) return;
      if (pendentes > 0) {
        if (valEl) valEl.textContent = `Missões (${pendentes})`;
        el.style.borderColor = '#eab308';
        el.style.background = 'rgba(234,179,8,0.22)';
        el.title = `${pendentes} de ${total} missões pendentes hoje (+Moedas)`;
      } else if (total > 0) {
        if (valEl) valEl.textContent = `Missões (✓)`;
        el.style.borderColor = '#22c55e';
        el.style.background = 'rgba(34,197,94,0.22)';
        el.title = `Todas as ${total} missões de hoje foram cumpridas! Parabéns!`;
      }
    }

    function abrirModalMissoesHeroi() {
      pushModalScreen('📋 QUARTEL-GENERAL DAS MISSÕES DO HERÓI', (body) => {
        carregarERenderizarMissoesHeroi(body);
      }, false);
    }

    async function carregarERenderizarMissoesHeroi(body) {
      playTone(587, 90);
      body.innerHTML = `
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:240px; gap:14px; text-align:center;">
          <div style="font-size:3.5rem; animation:pulse 1.2s infinite;">📋</div>
          <div style="font-size:1.3rem; font-weight:900; color:#38bdf8;">Abrindo o Quartel-General de Missões...</div>
          <div style="font-size:0.95rem; color:#94a3b8;">Carregando suas tarefas e recompensas de ouro...</div>
        </div>
      `;

      try {
        const res = await fetch('/api/missoes');
        const data = await res.json();
        missoesHeroiCache = data.missoes || [];
        renderMissoesHeroiView(body, true);
      } catch (err) {
        body.innerHTML = `
          <div style="text-align:center; padding:30px;">
            <div style="font-size:3.5rem;">⚠️</div>
            <div style="font-size:1.3rem; font-weight:900; color:#f87171; margin-top:8px;">Ops! Não conseguimos carregar as missões agora.</div>
            <button type="button" class="big-btn" style="background:#0284c7; margin-top:16px; padding:8px 20px;" onclick="carregarERenderizarMissoesHeroi(document.getElementById('modal-body'))">
              🔄 Tentar Novamente
            </button>
          </div>
        `;
      }
    }

    function alternarFiltroMissoesHeroi(filtro) {
      filtroMissoesHeroi = filtro;
      playTone(660, 60);
      const b = document.getElementById('modal-body');
      if (b) renderMissoesHeroiView(b, false);
    }

    function obterEstiloCategoriaMissao(cat) {
      const c = (cat || 'Geral').toLowerCase();
      if (c.includes('higiene')) return { badgeBg: '#0891b2', border: '#06b6d4', glow: 'rgba(6,182,212,0.25)', corTexto: '#cffafe', icone: '🧼' };
      if (c.includes('saúde') || c.includes('saude') || c.includes('alimento') || c.includes('nutri')) return { badgeBg: '#16a34a', border: '#22c55e', glow: 'rgba(34,197,94,0.25)', corTexto: '#dcfce7', icone: '🍎' };
      if (c.includes('organiza') || c.includes('quarto') || c.includes('casa')) return { badgeBg: '#d97706', border: '#f59e0b', glow: 'rgba(245,158,11,0.25)', corTexto: '#fef3c7', icone: '🧸' };
      if (c.includes('estudo') || c.includes('leitura') || c.includes('escola')) return { badgeBg: '#9333ea', border: '#a855f7', glow: 'rgba(168,85,247,0.25)', corTexto: '#f3e8ff', icone: '📚' };
      return { badgeBg: '#0284c7', border: '#38bdf8', glow: 'rgba(56,189,248,0.25)', corTexto: '#e0f2fe', icone: '⭐' };
    }

    function obterAtalhoMissao(m) {
      const tit = (m.titulo || '').toLowerCase();
      if (tit.includes('dente') || tit.includes('escovar')) {
        return { rotulo: '🪥 Ir para Escovação (2 Min)', fn: 'iniciarMissaoDente()', cor: '#0284c7', border: '#38bdf8' };
      }
      if (tit.includes('livro') || tit.includes('ler') || tit.includes('leitura')) {
        return { rotulo: '📚 Abrir Livros Mágicos', fn: 'openBooksLibrary()', cor: '#7c3aed', border: '#c084fc' };
      }
      if (tit.includes('fruta') || tit.includes('salada') || tit.includes('comer') || tit.includes('comida') || tit.includes('alimento')) {
        return { rotulo: '🍎 Montar Prato Saudável', fn: 'openHealthyFoodGame()', cor: '#16a34a', border: '#86efac' };
      }
      if (tit.includes('brinquedo') || tit.includes('guardar') || tit.includes('arrumar') || tit.includes('quarto')) {
        return { rotulo: '🧸 Desafio de Organização', fn: 'iniciarMissaoQuarto()', cor: '#ea580c', border: '#fdba74' };
      }
      return null;
    }

    function renderMissoesHeroiView(body, falarSaudacao = false) {
      const missoes = missoesHeroiCache || [];
      const total = missoes.length;
      const cumpridas = missoes.filter(m => Boolean(m.cumprida)).length;
      const pendentes = total - cumpridas;
      const pct = total > 0 ? Math.round((cumpridas / total) * 100) : 0;
      const moedasGanhasHoje = missoes.filter(m => Boolean(m.cumprida)).reduce((acc, m) => acc + (m.recompensa_moedas || 0), 0);
      const childName = (appState.config && appState.config.child_name) || 'Campeão';

      // Atualiza badge de missões no topo do HUD
      if (typeof atualizarBadgeMissoesTop === 'function') {
        atualizarBadgeMissoesTop(pendentes, total);
      }

      if (falarSaudacao) {
        if (total === 0) {
          speak(`Olá, super-herói ${childName}! Nenhuma missão cadastrada no momento. Chame o papai ou a mamãe se quiserem novas tarefas!`);
        } else if (pendentes === 0) {
          speak(`Incrível, super campeão ${childName}! Você já completou todas as missões de rotina de hoje! Todas as moedas são suas!`);
        } else {
          speak(`Quartel-general de missões do herói ${childName}! Você já completou ${cumpridas} de ${total} missões hoje! Vamos cumprir as tarefas e ganhar mais moedas de ouro!`);
        }
      }

      let missoesFiltradas = missoes;
      if (filtroMissoesHeroi === 'pendentes') missoesFiltradas = missoes.filter(m => !m.cumprida);
      else if (filtroMissoesHeroi === 'concluidas') missoesFiltradas = missoes.filter(m => Boolean(m.cumprida));

      body.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:14px; padding:2px 4px; max-width:980px; margin:0 auto; box-sizing:border-box;">
          
          <!-- BANNER HERO HQ: STATUS DO DIA, PROGRESSO & RECOMPENSAS -->
          <div style="background:linear-gradient(135deg, rgba(30, 58, 138, 0.45) 0%, rgba(15, 23, 42, 0.9) 100%); border:2px solid #38bdf8; border-radius:20px; padding:14px 18px; box-shadow:0 6px 24px rgba(56, 189, 248, 0.2); display:flex; flex-direction:column; gap:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
              <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:52px; height:52px; border-radius:16px; background:linear-gradient(135deg, #eab308, #ca8a04); border:2px solid #fef08a; display:flex; align-items:center; justify-content:center; font-size:2rem; box-shadow:0 0 16px rgba(234, 179, 8, 0.45);">
                  🎖️
                </div>
                <div>
                  <div style="font-size:1.35rem; font-weight:900; color:#fff; letter-spacing:0.3px; display:flex; align-items:center; gap:8px;">
                    Missões Diárias de ${childName}
                    <span style="background:#eab308; color:#000; font-size:0.75rem; font-weight:900; padding:2px 8px; border-radius:999px;">NÍVEL HERÓI</span>
                  </div>
                  <div style="font-size:0.88rem; color:#bae6fd; margin-top:2px;">
                    Complete tarefas com o papai e a mamãe para conquistar moedas de ouro no cofrinho!
                  </div>
                </div>
              </div>

              <!-- CHIPS DE ESTATÍSTICA -->
              <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <div style="background:rgba(234,179,8,0.18); border:1px solid #eab308; padding:5px 12px; border-radius:12px; display:flex; align-items:center; gap:6px;">
                  <span style="font-size:1.2rem;">🪙</span>
                  <div>
                    <div style="font-size:0.65rem; color:#fde047; font-weight:800;">GANHAS HOJE</div>
                    <div style="font-size:0.95rem; font-weight:900; color:#fff;">+${moedasGanhasHoje} Moedas</div>
                  </div>
                </div>
                <div style="background:rgba(56,189,248,0.18); border:1px solid #38bdf8; padding:5px 12px; border-radius:12px; display:flex; align-items:center; gap:6px;">
                  <span style="font-size:1.2rem;">🎯</span>
                  <div>
                    <div style="font-size:0.65rem; color:#7dd3fc; font-weight:800;">STATUS</div>
                    <div style="font-size:0.95rem; font-weight:900; color:#fff;">${cumpridas} / ${total} Missões</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- BARRA DE PROGRESSO DO HERÓI -->
            <div>
              <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.82rem; font-weight:800; color:#cbd5e1; margin-bottom:4px;">
                <span>⚡ Barra de Conquista Diária</span>
                <span style="color:#facc15;">${pct}% Concluído (${cumpridas} de ${total})</span>
              </div>
              <div style="width:100%; height:14px; background:#0f172a; border:1px solid #334155; border-radius:999px; overflow:hidden; padding:2px; box-sizing:border-box;">
                <div style="width:${pct}%; height:100%; background:linear-gradient(90deg, #f59e0b, #10b981); border-radius:999px; transition:width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1); box-shadow:0 0 10px rgba(16,185,129,0.5);"></div>
              </div>
              ${pct >= 100 && total > 0 ? `
                <div style="margin-top:6px; background:linear-gradient(90deg, rgba(21,128,61,0.5), rgba(234,179,8,0.5)); border:1px solid #86efac; border-radius:10px; padding:4px 10px; text-align:center; font-size:0.85rem; font-weight:900; color:#fff; animation:pulse 2s infinite;">
                  🌟 PARABÉNS! VOCÊ COMPLETOU 100% DAS SUAS MISSÕES HOJE! VOCÊ É UM SUPER CAMPEÃO! 🏆
                </div>
              ` : ''}
            </div>
          </div>

          <!-- FILTROS DE ABAS (TODAS / PENDENTES / CONCLUÍDAS) -->
          <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap;">
            <div style="display:flex; gap:6px;">
              <button type="button" class="big-btn" style="padding:6px 14px; font-size:0.88rem; font-weight:900; border-radius:10px; ${filtroMissoesHeroi === 'todas' ? 'background:#0284c7; border:2px solid #38bdf8; color:#fff;' : 'background:#1e293b; border:1px solid #334155; color:#94a3b8;'}" onclick="alternarFiltroMissoesHeroi('todas')">
                🎯 Todas (${total})
              </button>
              <button type="button" class="big-btn" style="padding:6px 14px; font-size:0.88rem; font-weight:900; border-radius:10px; ${filtroMissoesHeroi === 'pendentes' ? 'background:#d97706; border:2px solid #fde047; color:#fff;' : 'background:#1e293b; border:1px solid #334155; color:#94a3b8;'}" onclick="alternarFiltroMissoesHeroi('pendentes')">
                ⏳ Para Fazer (${pendentes})
              </button>
              <button type="button" class="big-btn" style="padding:6px 14px; font-size:0.88rem; font-weight:900; border-radius:10px; ${filtroMissoesHeroi === 'concluidas' ? 'background:#15803d; border:2px solid #86efac; color:#fff;' : 'background:#1e293b; border:1px solid #334155; color:#94a3b8;'}" onclick="alternarFiltroMissoesHeroi('concluidas')">
                ✅ Concluídas (${cumpridas})
              </button>
            </div>

            <button type="button" class="big-btn" style="background:#0f172a; border:1px solid #334155; color:#94a3b8; padding:5px 12px; font-size:0.82rem; font-weight:800; border-radius:8px;" onclick="carregarERenderizarMissoesHeroi(document.getElementById('modal-body'))" title="Atualizar lista">
              🔄 Atualizar
            </button>
          </div>

          <!-- LISTA / GRID DE CARDS DAS MISSÕES -->
          ${missoesFiltradas.length === 0 ? `
            <div style="background:#0b172a; border:2px dashed #334155; border-radius:18px; padding:32px 18px; text-align:center;">
              <div style="font-size:3.5rem; margin-bottom:8px;">${filtroMissoesHeroi === 'pendentes' ? '🎉' : '🌟'}</div>
              <div style="font-size:1.3rem; font-weight:900; color:#fff;">
                ${filtroMissoesHeroi === 'pendentes' ? 'Nenhuma missão pendente!' : (filtroMissoesHeroi === 'concluidas' ? 'Nenhuma missão concluída ainda hoje.' : 'Nenhuma missão cadastrada!')}
              </div>
              <div style="font-size:0.95rem; color:#94a3b8; max-width:480px; margin:6px auto 0;">
                ${filtroMissoesHeroi === 'pendentes' ? 'Você já fez todas as tarefas de hoje! Aproveite para brincar na sala de jogos!' : 'Realize as tarefas com o papai e a mamãe para registrar suas vitórias!'}
              </div>
            </div>
          ` : `
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:12px;">
              ${missoesFiltradas.map(m => {
                const isCumprida = Boolean(m.cumprida);
                const estiloCat = obterEstiloCategoriaMissao(m.categoria);
                const atalho = !isCumprida ? obterAtalhoMissao(m) : null;
                return `
                  <div id="card-missao-${m.id}" style="${isCumprida ? `
                    background:linear-gradient(145deg, rgba(16, 185, 129, 0.16) 0%, rgba(6, 78, 59, 0.28) 100%);
                    border:2px solid #22c55e;
                    box-shadow:0 4px 18px rgba(34, 197, 94, 0.18);
                  ` : `
                    background:linear-gradient(145deg, #0b172a 0%, #030816 100%);
                    border:2px solid ${estiloCat.border};
                    box-shadow:0 4px 18px ${estiloCat.glow};
                  `} border-radius:18px; padding:14px; display:flex; flex-direction:column; justify-content:space-between; gap:12px; transition:all 0.3s ease;">
                    
                    <!-- TOPO DO CARD: CATEGORIA & RECOMPENSA -->
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
                      <span style="background:${estiloCat.badgeBg}; color:${estiloCat.corTexto}; padding:3px 10px; border-radius:999px; font-size:0.75rem; font-weight:900; letter-spacing:0.4px;">
                        ${m.categoria ? m.categoria.toUpperCase() : 'ROTINA'}
                      </span>
                      <span style="background:linear-gradient(135deg, #eab308, #ca8a04); color:#000; padding:3px 10px; border-radius:999px; font-size:0.8rem; font-weight:900; box-shadow:0 0 10px rgba(234, 179, 8, 0.35);">
                        +${m.recompensa_moedas} 🪙 Moedas
                      </span>
                    </div>

                    <!-- MEIO: ÍCONE + TÍTULO + DESCRIÇÃO -->
                    <div style="display:flex; gap:12px; align-items:flex-start;">
                      <div style="width:54px; height:54px; border-radius:14px; ${isCumprida ? 'background:rgba(34,197,94,0.2); border:2px solid #22c55e;' : `background:${estiloCat.glow}; border:2px solid ${estiloCat.border};`} display:flex; align-items:center; justify-content:center; font-size:2.2rem; flex-shrink:0; position:relative;">
                        ${m.icone || estiloCat.icone}
                        ${isCumprida ? `<span style="position:absolute; bottom:-4px; right:-4px; background:#22c55e; color:#fff; border-radius:50%; width:20px; height:20px; font-size:0.8rem; display:flex; align-items:center; justify-content:center; font-weight:900;">✓</span>` : ''}
                      </div>
                      <div style="flex:1;">
                        <div style="font-size:1.15rem; font-weight:900; color:#fff; line-height:1.25;">
                          ${m.titulo}
                        </div>
                        <div style="font-size:0.88rem; color:#94a3b8; margin-top:4px; line-height:1.35;">
                          ${m.descricao || 'Missão especial de rotina diária.'}
                        </div>
                      </div>
                    </div>

                    <!-- RODAPÉ: BOTÃO CUMPRIR / STATUS / ATALHOS -->
                    <div style="display:flex; flex-direction:column; gap:6px; margin-top:4px;">
                      ${isCumprida ? `
                        <button type="button" class="big-btn" style="background:rgba(34, 197, 94, 0.2); border:1px solid #22c55e; color:#86efac; font-size:0.92rem; font-weight:900; padding:10px 16px; border-radius:12px; cursor:default; width:100%; text-align:center;" disabled>
                          🏆 Concluída hoje ${m.hora_cumprida ? 'às ' + m.hora_cumprida : ''}! (+${m.recompensa_moedas} 🪙)
                        </button>
                      ` : `
                        <button type="button" class="big-btn" style="background:linear-gradient(135deg, #0284c7, #0369a1); border:2px solid #38bdf8; color:#fff; font-size:1.02rem; font-weight:900; padding:10px 16px; border-radius:12px; cursor:pointer; width:100%; display:flex; align-items:center; justify-content:center; gap:8px; box-shadow:0 4px 14px rgba(2, 132, 199, 0.4);" onclick="cumprirMissaoKiosk(${m.id})">
                          ⭐ Cumprir Missão (+${m.recompensa_moedas} 🪙)
                        </button>
                        ${atalho ? `
                          <button type="button" class="big-btn" style="background:${atalho.cor}; border:1px solid ${atalho.border}; color:#fff; font-size:0.82rem; font-weight:800; padding:6px 12px; border-radius:10px; cursor:pointer;" onclick="${atalho.fn}">
                            ${atalho.rotulo}
                          </button>
                        ` : ''}
                      `}
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          `}
        </div>
      `;
    }

    function cumprirMissaoKiosk(id) {
      const m = (missoesHeroiCache || []).find(x => x.id === id);
      if (!m || m.cumprida) return;

      const childName = (appState.config && appState.config.child_name) || 'Campeão';
      const moedas = m.recompensa_moedas || 5;

      // 1. Efeitos imediatos em 0ms (Web Audio API + Dopamina de Confetes)
      playCelebrationFanfare();
      playSfxCoin();
      dispararConfetesDopamina(90);
      dispararChuvaCoracoes(70);

      // 2. Atualização imediata do cache local
      const agora = new Date();
      const horaStr = `${String(agora.getHours()).padStart(2, '0')}:${String(agora.getMinutes()).padStart(2, '0')}`;
      m.cumprida = 1;
      m.hora_cumprida = horaStr;

      // 3. Atualização imediata do pote no DOM
      const pEl = document.getElementById('pote-fichas-val');
      if (pEl) pEl.textContent = parseInt(pEl.textContent || '0') + moedas;
      showToast(`🎉 Missão Concluída! +${moedas} Moedas de Ouro no Pote!`);

      // 4. Re-renderização imediata da tela
      const b = document.getElementById('modal-body');
      if (b) renderMissoesHeroiView(b, false);

      // 5. Narrar mensagem vibrante do Jarvis
      const pendentesApos = (missoesHeroiCache || []).filter(x => !x.cumprida).length;
      if (pendentesApos === 0) {
        speak(`Incrível, super campeão ${childName}! Você cumpriu a missão ${m.titulo} e ganhou ${moedas} moedas! E você completou todas as missões de rotina de hoje! Parabéns!`);
      } else {
        speak(`Parabéns, ${childName}! Você cumpriu a missão ${m.titulo} e ganhou ${moedas} moedas de ouro para o seu cofrinho! Restam apenas ${pendentesApos} missões!`);
      }

      // 6. Sincronização assíncrona com o backend
      fetch('/api/missoes/cumprir', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ missao_id: id })
      }).then(res => res.json()).then(d => {
        if (d && d.novo_saldo !== undefined && pEl) {
          pEl.textContent = d.novo_saldo;
        }
      }).catch(err => console.warn('Erro ao sincronizar missão cumprida:', err));
    }
"""

hud_code = hud_code[:sep1] + new_pilar1_code + '\n' + hud_code[sep2:]
print("2.4 Código de missões do Pilar 1 substituído com sucesso!")

with open(hud_path, 'w', encoding='utf-8') as f:
    f.write(hud_code)

print("Todas as alterações em templates/hud_jarvis.html foram gravadas com sucesso!")
