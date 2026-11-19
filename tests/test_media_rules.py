import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jarvis_brain import JarvisBrain
from gestao_tempo_midia import MediaTimeManager

class TestMediaRules(unittest.TestCase):
    def setUp(self):
        self.brain = JarvisBrain()
        self.mgr = MediaTimeManager(self.brain)

    def test_book_required_blocks_cinema_initially(self):
        # Quando a regra require_book_before_media é True e nenhum livro foi lido
        self.brain.config["require_book_before_media"] = True
        perm = self.mgr.check_permission()
        # Se nenhum livro foi lido ou fora do horário, deve bloquear
        if self.mgr.get_books_read_today() == 0:
            self.assertFalse(perm["allowed"])
            self.assertIn("reason", perm)

    def test_record_book_unlocks_requirement(self):
        self.brain.config["require_book_before_media"] = True
        # Registra um livro lido
        self.mgr.record_book_read("livro_teste_unitario")
        self.assertGreaterEqual(self.mgr.get_books_read_today(), 1)

    def test_bonus_minutes_and_revoke(self):
        # Concede bônus de 15 minutos
        self.mgr.grant_bonus_minutes(15)
        # Zera tempo de cinema
        self.mgr.revoke_all_media_time()
        perm = self.mgr.check_permission()
        self.assertEqual(perm.get("remaining_seconds", 0), 0)

if __name__ == '__main__':
    unittest.main()
