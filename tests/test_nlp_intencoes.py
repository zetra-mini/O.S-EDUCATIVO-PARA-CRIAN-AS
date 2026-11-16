import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jarvis_brain import JarvisBrain

brain = JarvisBrain()
# Mock ask so it doesn't need external LLM network connection during test
brain.ask = lambda text: (f"Resposta IA para: {text}", "mock_llm")

test_cases = [
    ("Quem é o Homem-Aranha dos filmes?", "conversa_ia", "nenhuma"),
    ("Jarvis, quem é o Homem-Aranha dos filmes", "conversa_ia", "nenhuma"),
    ("Jarvis, jogo do xadrez", "xadrez_mestre", "abrir_xadrez_mestre"),
    ("Jarvis, jogo do livro", "abrir_biblioteca", "abrir_biblioteca"),
    ("Jarvis, abrir jogo do relógio", "relogio_tempo", "abrir_relogio_tempo"),
    ("como funciona o cinema?", "conversa_ia", "nenhuma"),
    ("qual é o seu livro preferido?", "conversa_ia", "nenhuma"),
    ("o que é xadrez", "conversa_ia", "nenhuma"),
    ("me fala sobre os dinossauros", "conversa_ia", "nenhuma"),
    ("vamos jogar o jogo da cobrinha", "circuito_neon", "abrir_circuito_neon"),
    ("que horas são?", "relogio_tempo", "nenhuma"),
    ("Jarvis, abrir jogos", "jogos", "abrir_jogos"),
    ("Jarvis, abrir cinema", ["abrir_cinema", "cinema_bloqueado"], ["abrir_cinema", "cinema_bloqueado"]),
    ("assistir filme", ["abrir_cinema", "cinema_bloqueado"], ["abrir_cinema", "cinema_bloqueado"]),
    ("assistir desenho", ["abrir_cinema", "cinema_bloqueado"], ["abrir_cinema", "cinema_bloqueado"]),
]

all_passed = True
for query, expected_intencao, expected_acao in test_cases:
    res = brain.interpret_command(query)
    intencao = res.get("intencao")
    acao = res.get("acao_frontend")
    exp_int = [expected_intencao] if isinstance(expected_intencao, str) else expected_intencao
    exp_ac = [expected_acao] if isinstance(expected_acao, str) else expected_acao
    ok = (intencao in exp_int and acao in exp_ac)
    status = "PASS" if ok else "FAIL"
    if not ok:
        all_passed = False
    print(f"[{status}] \"{query}\" -> intencao={intencao} (esperado {expected_intencao}), acao={acao} (esperado {expected_acao})")

if all_passed:
    print("\n>>> ALL NLP TESTS PASSED PERFECTLY! <<<")
    exit(0)
else:
    print("\n>>> SOME TESTS FAILED! <<<")
    exit(1)
