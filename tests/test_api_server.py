import os
import sys
import json
import asyncio
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from run_server import app, brain
from microdot.test_client import TestClient

class TestApiServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_api_state_returns_config(self):
        async def run():
            res = await self.client.get('/api/state')
            self.assertEqual(res.status_code, 200)
            data = res.json
            self.assertIn('config', data)
            self.assertIn('active_provider', data['config'])
            self.assertIn('child_name', data['config'])
        asyncio.run(run())

    def test_api_config_persists_provider(self):
        async def run():
            # Salva provedor opencode
            payload = json.dumps({"active_provider": "opencode", "mode": "opencode"})
            res = await self.client.post('/api/config', body=payload, headers={'Content-Type': 'application/json'})
            self.assertEqual(res.status_code, 200)
            data = res.json
            self.assertTrue(data.get("ok"))
            self.assertEqual(data.get("config", {}).get("active_provider"), "opencode")

            # Verifica se /api/state reflete o novo provedor
            res_state = await self.client.get('/api/state')
            self.assertEqual(res_state.json.get("config", {}).get("active_provider"), "opencode")

            # Restaura para o padrão
            await self.client.post('/api/config', body=json.dumps({"active_provider": "ollama", "mode": "ollama"}), headers={'Content-Type': 'application/json'})
        asyncio.run(run())

    def test_parental_pin_verification(self):
        async def run():
            # Teste de verificação com PIN de contingência padrão "1234" ou "56"
            res = await self.client.post('/api/parental/verify-pin', body=json.dumps({"pin": "1234"}), headers={'Content-Type': 'application/json'})
            self.assertEqual(res.status_code, 200)
            self.assertTrue(res.json.get("ok"))

            res_math = await self.client.post('/api/parental/verify-pin', body=json.dumps({"pin": "56"}), headers={'Content-Type': 'application/json'})
            self.assertEqual(res_math.status_code, 200)
            self.assertTrue(res_math.json.get("ok"))

            # Teste com PIN inválido
            res_err = await self.client.post('/api/parental/verify-pin', body=json.dumps({"pin": "999999"}), headers={'Content-Type': 'application/json'})
            self.assertEqual(res_err.status_code, 401)
            self.assertFalse(res_err.json.get("ok"))
        asyncio.run(run())

    def test_parental_pin_change(self):
        async def run():
            # Define novo PIN válido (4 dígitos)
            res = await self.client.post('/api/parental/change-pin', body=json.dumps({"pin": "4321"}), headers={'Content-Type': 'application/json'})
            self.assertEqual(res.status_code, 200)
            self.assertTrue(res.json.get("ok"))

            # Testa novo PIN
            res_val = await self.client.post('/api/parental/verify-pin', body=json.dumps({"pin": "4321"}), headers={'Content-Type': 'application/json'})
            self.assertEqual(res_val.status_code, 200)
            self.assertTrue(res_val.json.get("ok"))

            # Restaura PIN original
            await self.client.post('/api/parental/change-pin', body=json.dumps({"pin": "1234"}), headers={'Content-Type': 'application/json'})
        asyncio.run(run())

    def test_api_livros(self):
        async def run():
            res = await self.client.get('/api/livros')
            self.assertEqual(res.status_code, 200)
            data = res.json
            books = data.get("livros", data.get("books", data)) if isinstance(data, dict) else data
            self.assertIsInstance(books, list)
            self.assertGreater(len(books), 0)
        asyncio.run(run())

if __name__ == '__main__':
    unittest.main()
