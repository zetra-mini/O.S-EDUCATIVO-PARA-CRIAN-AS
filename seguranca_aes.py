"""
Módulo de Criptografia Autenticada AES-256-GCM (seguranca_aes.py) — JARVIS Kids OS
=================================================================================
Protege segredos locais (chaves de API Gemini/OpenAI/Groq/Picovoice, PIN parental),
sessões administrativas e recados privados da família com criptografia autenticada
AES-256-GCM (chave de 256 bits, nonce aleatório CSPRNG de 96 bits e tag de 128 bits).

Arquitetura Zero-Failure para Acer Aspire One 532 (1 GB RAM / antiX Linux / Windows):
1. Usa aceleração nativa (`cryptography.hazmat.primitives.ciphers.aead.AESGCM`) quando disponível.
2. Possui implementação pura 100% interoperável AES-256-GCM (FIPS 197 + NIST SP 800-38D)
   caso o sistema enxuto de 32-bit não possua `cryptography` instalado.
3. Chave mestra de 256 bits por instalação armazenada em `JARVIS_AES_KEY` ou em
   `.jarvis_master.key` (permissão `0600` em sistemas POSIX, ignorado no Git e no `.deb`).
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import sys
import threading
from typing import Any, Dict, Optional

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM as _CryptoAESGCM
    HAS_CRYPTOGRAPHY = True
except Exception:
    _CryptoAESGCM = None
    HAS_CRYPTOGRAPHY = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MASTER_KEY_PATH = os.path.join(BASE_DIR, ".jarvis_master.key")
ENC_PREFIX = "enc:aes256gcm:v1:"

_KEY_LOCK = threading.Lock()
_EPHEMERAL_FALLBACK_KEY: Optional[bytes] = None

# ==============================================================================
# Implementação Pura Interoperável AES-256-GCM (FIPS 197 + NIST SP 800-38D)
# ==============================================================================

_SBOX = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)
_RCON = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)


def _xtime(a: int) -> int:
    return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else ((a << 1) & 0xFF)


def _aes256_expand_key(key: bytes) -> list:
    if len(key) != 32:
        raise ValueError("A chave AES-256 deve ter exatamente 32 bytes (256 bits).")
    rk = list(key)
    for i in range(8, 60):
        t0, t1, t2, t3 = rk[-4], rk[-3], rk[-2], rk[-1]
        if i % 8 == 0:
            t0, t1, t2, t3 = _SBOX[t1] ^ _RCON[i // 8 - 1], _SBOX[t2], _SBOX[t3], _SBOX[t0]
        elif i % 8 == 4:
            t0, t1, t2, t3 = _SBOX[t0], _SBOX[t1], _SBOX[t2], _SBOX[t3]
        p = (i - 8) * 4
        rk.extend((rk[p] ^ t0, rk[p + 1] ^ t1, rk[p + 2] ^ t2, rk[p + 3] ^ t3))
    return [rk[j : j + 16] for j in range(0, 240, 16)]


def _aes256_encrypt_block(round_keys: list, block: bytes) -> bytes:
    s = list(block)
    k0 = round_keys[0]
    for i in range(16):
        s[i] ^= k0[i]

    for rnd in range(1, 15):
        # SubBytes + ShiftRows
        t = [
            _SBOX[s[0]], _SBOX[s[5]], _SBOX[s[10]], _SBOX[s[15]],
            _SBOX[s[4]], _SBOX[s[9]], _SBOX[s[14]], _SBOX[s[3]],
            _SBOX[s[8]], _SBOX[s[13]], _SBOX[s[2]], _SBOX[s[7]],
            _SBOX[s[12]], _SBOX[s[1]], _SBOX[s[6]], _SBOX[s[11]],
        ]
        kr = round_keys[rnd]
        if rnd < 14:
            # MixColumns + AddRoundKey
            for c in range(0, 16, 4):
                a0, a1, a2, a3 = t[c], t[c + 1], t[c + 2], t[c + 3]
                x = a0 ^ a1 ^ a2 ^ a3
                s[c] = a0 ^ x ^ _xtime(a0 ^ a1) ^ kr[c]
                s[c + 1] = a1 ^ x ^ _xtime(a1 ^ a2) ^ kr[c + 1]
                s[c + 2] = a2 ^ x ^ _xtime(a2 ^ a3) ^ kr[c + 2]
                s[c + 3] = a3 ^ x ^ _xtime(a3 ^ a0) ^ kr[c + 3]
        else:
            for i in range(16):
                s[i] = t[i] ^ kr[i]
    return bytes(s)


def _gf_mul_128(x: int, y: int) -> int:
    z = 0
    v = y
    r_poly = 0xE1000000000000000000000000000000
    for i in range(127, -1, -1):
        if (x >> i) & 1:
            z ^= v
        if v & 1:
            v = (v >> 1) ^ r_poly
        else:
            v >>= 1
    return z


def _ghash(h_int: int, aad: bytes, ct: bytes) -> bytes:
    y = 0
    for block_src in (aad, ct):
        for i in range(0, len(block_src), 16):
            chunk = block_src[i : i + 16]
            if len(chunk) < 16:
                chunk = chunk + b"\x00" * (16 - len(chunk))
            y = _gf_mul_128(y ^ int.from_bytes(chunk, "big"), h_int)
    len_block = ((len(aad) * 8) << 64) | (len(ct) * 8)
    y = _gf_mul_128(y ^ len_block, h_int)
    return y.to_bytes(16, "big")


class PurePythonAES256GCM:
    """AES-256-GCM compatível bit a bit com `cryptography.hazmat.primitives.ciphers.aead.AESGCM`."""

    def __init__(self, key: bytes):
        self._rk = _aes256_expand_key(key)
        self._h_int = int.from_bytes(_aes256_encrypt_block(self._rk, b"\x00" * 16), "big")

    def _gctr(self, icb: bytes, data: bytes) -> bytes:
        if not data:
            return b""
        prefix = icb[:12]
        ctr = int.from_bytes(icb[12:16], "big")
        out = bytearray()
        for i in range(0, len(data), 16):
            cb = prefix + (ctr & 0xFFFFFFFF).to_bytes(4, "big")
            ks = _aes256_encrypt_block(self._rk, cb)
            chunk = data[i : i + 16]
            out.extend(a ^ b for a, b in zip(chunk, ks))
            ctr += 1
        return bytes(out)

    def encrypt(self, nonce: bytes, data: bytes, associated_data: Optional[bytes] = None) -> bytes:
        if len(nonce) != 12:
            raise ValueError("Nonce AES-256-GCM deve ter 12 bytes.")
        aad = associated_data or b""
        j0 = nonce + b"\x00\x00\x00\x01"
        icb = nonce + b"\x00\x00\x00\x02"
        ct = self._gctr(icb, data)
        tag_mask = _aes256_encrypt_block(self._rk, j0)
        gh = _ghash(self._h_int, aad, ct)
        tag = bytes(a ^ b for a, b in zip(gh, tag_mask))
        return ct + tag

    def decrypt(self, nonce: bytes, data: bytes, associated_data: Optional[bytes] = None) -> bytes:
        if len(nonce) != 12 or len(data) < 16:
            raise ValueError("Ciphertext AES-256-GCM inválido.")
        aad = associated_data or b""
        ct, tag = data[:-16], data[-16:]
        j0 = nonce + b"\x00\x00\x00\x01"
        icb = nonce + b"\x00\x00\x00\x02"
        tag_mask = _aes256_encrypt_block(self._rk, j0)
        gh = _ghash(self._h_int, aad, ct)
        expected_tag = bytes(a ^ b for a, b in zip(gh, tag_mask))
        if not hmac.compare_digest(tag, expected_tag):
            raise ValueError("Falha de autenticidade AES-256-GCM (tag inválida).")
        return self._gctr(icb, ct)


# ==============================================================================
# Gestão da Chave Mestra (256 bits) e API de Criptografia do Sistema
# ==============================================================================

def _parse_key_material(raw: str) -> Optional[bytes]:
    txt = (raw or "").strip()
    if not txt:
        return None
    if len(txt) == 64:
        try:
            decoded = bytes.fromhex(txt)
            if len(decoded) == 32:
                return decoded
        except ValueError:
            pass
    try:
        padded = txt + ("=" * ((4 - len(txt) % 4) % 4))
        b = base64.urlsafe_b64decode(padded.encode("ascii"))
        if len(b) == 32:
            return b
    except Exception:
        pass
    return hashlib.pbkdf2_hmac("sha256", txt.encode("utf-8"), b"jarvis-kids-aes256-v1", 100_000, dklen=32)


def obter_chave_mestra_aes256() -> bytes:
    """Retorna a chave AES de 256 bits (32 bytes), priorizando variável de ambiente ou `.jarvis_master.key`."""
    global _EPHEMERAL_FALLBACK_KEY
    env_key = os.environ.get("JARVIS_AES_KEY", "").strip()
    if env_key:
        parsed = _parse_key_material(env_key)
        if parsed and len(parsed) == 32:
            return parsed

    with _KEY_LOCK:
        if os.path.exists(MASTER_KEY_PATH):
            try:
                with open(MASTER_KEY_PATH, "r", encoding="utf-8") as f:
                    parsed = _parse_key_material(f.read())
                    if parsed and len(parsed) == 32:
                        return parsed
            except Exception:
                pass

        nova_chave = secrets.token_bytes(32)
        b64_chave = base64.urlsafe_b64encode(nova_chave).decode("ascii")
        tmp_path = f"{MASTER_KEY_PATH}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(b64_chave)
            os.replace(tmp_path, MASTER_KEY_PATH)
            if sys.platform != "win32":
                os.chmod(MASTER_KEY_PATH, 0o600)
            return nova_chave
        except Exception:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            if _EPHEMERAL_FALLBACK_KEY is None:
                _EPHEMERAL_FALLBACK_KEY = secrets.token_bytes(32)
            return _EPHEMERAL_FALLBACK_KEY


def _criar_cifrador(key: Optional[bytes] = None):
    chave = key or obter_chave_mestra_aes256()
    if HAS_CRYPTOGRAPHY and _CryptoAESGCM is not None:
        return _CryptoAESGCM(chave)
    return PurePythonAES256GCM(chave)


def esta_criptografado_aes256(valor: Any) -> bool:
    return isinstance(valor, str) and valor.startswith(ENC_PREFIX)


def criptografar_texto_aes256(texto: str, aad: str = "", key: Optional[bytes] = None) -> str:
    """Criptografa uma string em UTF-8 usando AES-256-GCM e retorna token formatado."""
    if texto is None or texto == "":
        return ""
    if esta_criptografado_aes256(texto):
        return texto
    nonce = os.urandom(12)
    cifrador = _criar_cifrador(key)
    ct_tag = cifrador.encrypt(nonce, str(texto).encode("utf-8"), aad.encode("utf-8") if aad else None)
    n_b64 = base64.urlsafe_b64encode(nonce).decode("ascii").rstrip("=")
    c_b64 = base64.urlsafe_b64encode(ct_tag).decode("ascii").rstrip("=")
    return f"{ENC_PREFIX}{n_b64}:{c_b64}"


def descriptografar_texto_aes256(valor: str, aad: str = "", key: Optional[bytes] = None) -> str:
    """Descriptografa um token `enc:aes256gcm:v1:...`; se for texto legado sem prefixo, devolve intacto."""
    if not valor or not isinstance(valor, str):
        return ""
    if not valor.startswith(ENC_PREFIX):
        return valor
    try:
        resto = valor[len(ENC_PREFIX) :]
        n_b64, c_b64 = resto.split(":", 1)
        nonce = base64.urlsafe_b64decode(n_b64 + ("=" * ((4 - len(n_b64) % 4) % 4)))
        ct_tag = base64.urlsafe_b64decode(c_b64 + ("=" * ((4 - len(c_b64) % 4) % 4)))
        cifrador = _criar_cifrador(key)
        pt = cifrador.decrypt(nonce, ct_tag, aad.encode("utf-8") if aad else None)
        return pt.decode("utf-8")
    except Exception:
        return ""


def criptografar_json_aes256(dados: Dict[str, Any], aad: str = "json", key: Optional[bytes] = None) -> str:
    bruto = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
    return criptografar_texto_aes256(bruto, aad=aad, key=key)


def descriptografar_json_aes256(token: str, aad: str = "json", key: Optional[bytes] = None) -> Optional[Dict[str, Any]]:
    if not token or not esta_criptografado_aes256(token):
        return None
    dec = descriptografar_texto_aes256(token, aad=aad, key=key)
    if not dec:
        return None
    try:
        obj = json.loads(dec)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def status_criptografia_aes256() -> Dict[str, Any]:
    chave = obter_chave_mestra_aes256()
    return {
        "algoritmo": "AES-256-GCM",
        "bits_chave": len(chave) * 8,
        "backend": "cryptography-native" if HAS_CRYPTOGRAPHY else "pure-python-fips197",
        "chave_configurada": len(chave) == 32,
        "origem_chave": "env:JARVIS_AES_KEY" if os.environ.get("JARVIS_AES_KEY") else "arquivo:.jarvis_master.key",
    }
