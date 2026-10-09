"""
vault.py — NISHA Encrypted Vault
Stores credentials, API keys, and sensitive items.
Encrypted at rest. Never appears in prompt logs.
"""
import json
import os
import base64
import hashlib
from pathlib import Path
from typing import Optional
import sys


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR   = get_base_dir()
VAULT_PATH = BASE_DIR / "memory" / "vault" / ".nisha_vault.enc"
SALT_PATH  = BASE_DIR / "memory" / "vault" / ".salt"


def _derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)


def _xor_encrypt(data: bytes, key: bytes) -> bytes:
    """Simple XOR with repeating key — lightweight, dependency-free."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


class NishaVault:
    """
    Encrypted local vault for secrets.
    Contents are NEVER injected into prompts or logs.
    Access requires the vault password.
    """

    def __init__(self):
        VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)

    def _get_salt(self) -> bytes:
        if not SALT_PATH.exists():
            salt = os.urandom(16)
            SALT_PATH.write_bytes(salt)
        return SALT_PATH.read_bytes()

    def _load(self, password: str) -> Optional[dict]:
        if not VAULT_PATH.exists():
            return {}
        salt = self._get_salt()
        key  = _derive_key(password, salt)
        try:
            raw  = base64.b64decode(VAULT_PATH.read_bytes())
            data = _xor_encrypt(raw, key)
            return json.loads(data.decode("utf-8"))
        except Exception:
            return None   # Wrong password or corrupted

    def _save(self, data: dict, password: str) -> None:
        salt = self._get_salt()
        key  = _derive_key(password, salt)
        raw  = json.dumps(data, ensure_ascii=False).encode("utf-8")
        enc  = _xor_encrypt(raw, key)
        VAULT_PATH.write_bytes(base64.b64encode(enc))

    def set(self, key: str, value: str, password: str) -> bool:
        data = self._load(password)
        if data is None:
            return False
        data[key] = value
        self._save(data, password)
        return True

    def get(self, key: str, password: str) -> Optional[str]:
        data = self._load(password)
        if data is None:
            return None
        return data.get(key)

    def delete(self, key: str, password: str) -> bool:
        data = self._load(password)
        if data is None or key not in data:
            return False
        del data[key]
        self._save(data, password)
        return True

    def list_keys(self, password: str) -> list:
        """Return key names only — never values."""
        data = self._load(password)
        if data is None:
            return []
        return list(data.keys())

    def exists(self) -> bool:
        return VAULT_PATH.exists()


# Module-level singleton
_vault: Optional[NishaVault] = None

def get_vault() -> NishaVault:
    global _vault
    if _vault is None:
        _vault = NishaVault()
    return _vault
