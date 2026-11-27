import asyncio
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jarvis_brain as jb
import mensagens_pais as mp
import run_server as rs
import seguranca_aes as sa
from microdot.test_client import TestClient


class TestAES256Security(unittest.TestCase):
    def test_pure_python_and_cryptography_interop(self):
        key = os.urandom(32)
        nonce = os.urandom(12)
        aad = b"jarvis-aad-check"
        plaintext = "Chave Gemini AIzaSy_Teste_Segredo_256bits! 🚀".encode("utf-8")

        pure = sa.PurePythonAES256GCM(key)
        ct_pure = pure.encrypt(nonce, plaintext, aad)
        self.assertEqual(pure.decrypt(nonce, ct_pure, aad), plaintext)

        if sa.HAS_CRYPTOGRAPHY and sa._CryptoAESGCM is not None:
            native = sa._CryptoAESGCM(key)
            ct_native = native.encrypt(nonce, plaintext, aad)
            self.assertEqual(ct_pure, ct_native)
            self.assertEqual(native.decrypt(nonce, ct_pure, aad), plaintext)
            self.assertEqual(pure.decrypt(nonce, ct_native, aad), plaintext)

        # Adulteração de 1 bit ou AAD divergente deve falhar na verificação GCM
        tampered = bytearray(ct_pure)
        tampered[0] ^= 0x01
        with self.assertRaises(ValueError):
            pure.decrypt(nonce, bytes(tampered), aad)
        with self.assertRaises(ValueError):
            pure.decrypt(nonce, ct_pure, b"wrong-aad")

    def test_config_secrets_encrypted_at_rest_with_aes256(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_cfg_path = jb.CONFIG_PATH
            orig_master = sa.MASTER_KEY_PATH
            orig_cfg = dict(rs.brain.config)
            try:
                jb.CONFIG_PATH = os.path.join(tmpdir, "config.json")
                sa.MASTER_KEY_PATH = os.path.join(tmpdir, ".jarvis_master.key")

                rs.brain.config["gemini_api_key"] = "AIzaSySecretoAES256_RealKey"
                rs.brain.config["parental_pin"] = "7890"
                rs.brain.save_config()

                # Verifica no disco que NÃO existe texto claro no config.json
                raw_disk = open(jb.CONFIG_PATH, "r", encoding="utf-8").read()
                self.assertNotIn("AIzaSySecretoAES256_RealKey", raw_disk)
                self.assertNotIn("7890", raw_disk)
                disk_json = json.loads(raw_disk)
                self.assertTrue(sa.esta_criptografado_aes256(disk_json["gemini_api_key"]))
                self.assertTrue(sa.esta_criptografado_aes256(disk_json["parental_pin"]))

                # Recarrega em uma nova instância e confirma descriptografia transparente
                rs.brain.config["gemini_api_key"] = ""
                rs.brain.config["parental_pin"] = ""
                rs.brain.load_config()
                self.assertEqual(rs.brain.config["gemini_api_key"], "AIzaSySecretoAES256_RealKey")
                self.assertEqual(rs.brain.config["parental_pin"], "7890")
            finally:
                jb.CONFIG_PATH = orig_cfg_path
                sa.MASTER_KEY_PATH = orig_master
                rs.brain.config.clear()
                rs.brain.config.update(orig_cfg)

    def test_family_message_encrypted_in_sqlite_and_decrypted_on_read(self):
        mgr = mp.FamilyMessagesManager()
        texto_secreto = "Recado confidencial do papai com AES-256!"
        res = mgr.enviar_mensagem(remetente="Papai", tipo="texto", texto=texto_secreto)
        self.assertTrue(res.get("sucesso"))
        msg_id = res["id"]

        row = mgr.db.consultar_um("SELECT conteudo_texto FROM mensagens_familia WHERE id = ?;", (msg_id,))
        self.assertIsNotNone(row)
        self.assertTrue(sa.esta_criptografado_aes256(row["conteudo_texto"]))
        self.assertNotIn(texto_secreto, row["conteudo_texto"])

        lidas = mgr.listar_status_pais(limite=5)
        match = [m for m in lidas if m["id"] == msg_id]
        self.assertTrue(match)
        self.assertEqual(match[0]["conteudo_texto"], texto_secreto)

        # Limpeza do registro de teste
        mgr.db.executar_escrita("DELETE FROM mensagens_familia WHERE id = ?;", (msg_id,))

    def test_aes256_session_cookie_and_diagnostics(self):
        client = TestClient(rs.app)
        remote_headers = {"CF-Connecting-IP": "198.51.100.88"}

        async def run():
            res_login = await client.post(
                "/api/admin/login",
                body=json.dumps({"pin": "1234"}),
                headers={**remote_headers, "Content-Type": "application/json"},
            )
            self.assertEqual(res_login.status_code, 200)
            raw_sc = res_login.headers.get("Set-Cookie", [])
            cookie_header = (raw_sc[0] if isinstance(raw_sc, list) and raw_sc else str(raw_sc)).split(";", 1)[0]
            self.assertIn(sa.ENC_PREFIX, cookie_header)

            res_diag = await client.get(
                "/api/admin/diagnostico",
                headers={**remote_headers, "Cookie": cookie_header},
            )
            self.assertEqual(res_diag.status_code, 200)
            cripto = res_diag.json.get("criptografia", {})
            self.assertEqual(cripto.get("algoritmo"), "AES-256-GCM")
            self.assertEqual(cripto.get("bits_chave"), 256)
            self.assertTrue(cripto.get("chave_configurada"))

        asyncio.run(run())
