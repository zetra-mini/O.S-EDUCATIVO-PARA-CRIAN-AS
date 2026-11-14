## 📝 Descrição das Alterações
<!-- Descreva de forma clara e objetiva o que este PR faz (correção de bug, nova funcionalidade, melhoria de performance, etc.) -->

## 🎯 Tipo de Mudança
- [ ] 🐛 Correção de Bug (*fix*)
- [ ] ✨ Nova Funcionalidade / Novo Jogo (*feat*)
- [ ] ⚡ Otimização de Performance (*perf*)
- [ ] 📚 Documentação (*docs*)
- [ ] 🎨 Ajuste Visual ou Estilização (*style*)
- [ ] ♻️ Refatoração de Código (*refactor*)

## ✅ Checklist de Conformidade Arquitetural (Obrigatório)
Por favor, verifique todos os itens antes de submeter o PR:
- [ ] **Zero Dados Pessoais / Chaves de API:** Verifiquei e confirmo que NENHUM nome de criança, foto real, dado pessoal, ou chave de API/segredo foi adicionado.
- [ ] **Compatibilidade 1024x600:** Testei a interface na resolução de 1024x600 pixels (telas de netbook/quiósque) e garanti que não há elementos cortados ou dependentes de scrollbar invisível.
- [ ] **Performance no Intel Atom (1GB RAM):** O código é ultraleve, sem dependências externas pesadas ou loops infinitos de renderização/Canvas.
- [ ] **Controle de Áudio & Limpeza:** Se o PR envolve sons ou minigames, garanti que áudios anteriores são cancelados e que todos os sons/loops/webcam são interrompidos imediatamente ao fechar o modal ou jogo.
- [ ] **Idioma Português (pt-BR):** Textos, mensagens faladas pelo Jarvis e instruções estão em Português do Brasil com tom encorajador e carinhoso para a criança.
- [ ] **Modo Fácil por Padrão:** Novos jogos iniciam obrigatoriamente no modo fácil (🟢 Fácil).
- [ ] **Compilação Sem Erros:** Executei `python -m compileall .` e confirmo que não há erros de sintaxe Python.

## 🧪 Como Testar as Mudanças?
<!-- Descreva o passo a passo para reproduzir e testar o que foi implementado -->
1. Executar `python run_server.py 8000`.
2. Acessar a tela em `http://localhost:8000/...`.
3. Observar o comportamento...
