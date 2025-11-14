import os
import json
import base64
import secrets
from typing import Optional, Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


VERSION = 1


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode('utf-8')


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode('utf-8'))


def generate_aes_key() -> bytes:
    return secrets.token_bytes(32)  # AES-256


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    return kdf.derive(password.encode('utf-8'))


def encrypt_key_with_password(key: bytes, password: str) -> dict:
    salt = secrets.token_bytes(16)
    pw_key = derive_key_from_password(password, salt)
    nonce = secrets.token_bytes(12)
    aead = AESGCM(pw_key)
    enc = aead.encrypt(nonce, key, None)
    return {
        'version': VERSION,
        'salt': _b64e(salt),
        'nonce': _b64e(nonce),
        'enc': _b64e(enc),
        'type': 'encrypted_key'
    }


def decrypt_key_with_password(data: dict, password: str) -> bytes:
    salt = _b64d(data['salt'])
    nonce = _b64d(data['nonce'])
    enc = _b64d(data['enc'])
    pw_key = derive_key_from_password(password, salt)
    aead = AESGCM(pw_key)
    return aead.decrypt(nonce, enc, None)


def save_key_file(path: str, key: bytes, password: Optional[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if password:
        payload = encrypt_key_with_password(key, password)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f)
    else:
        # Store plaintext (base64) with a simple header
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'version': VERSION, 'type': 'plaintext_key', 'key': _b64e(key)}, f)


def load_key_file(path: str, password: Optional[str]) -> Tuple[bytes, bool]:
    """Return (key, encrypted_flag). encrypted_flag indicates the key file is password-protected."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if data.get('type') == 'encrypted_key':
        if not password:
            raise ValueError('需要密码解锁密钥文件')
        key = decrypt_key_with_password(data, password)
        return key, True
    elif data.get('type') == 'plaintext_key':
        return _b64d(data['key']), False
    else:
        raise ValueError('未知的secret.key格式')


def encrypt_payload(key: bytes, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    nonce = secrets.token_bytes(12)
    aead = AESGCM(key)
    ct = aead.encrypt(nonce, data, None)
    return {'version': VERSION, 'nonce': _b64e(nonce), 'ct': _b64e(ct)}


def decrypt_payload(key: bytes, blob: dict) -> dict:
    nonce = _b64d(blob['nonce'])
    ct = _b64d(blob['ct'])
    aead = AESGCM(key)
    data = aead.decrypt(nonce, ct, None)
    return json.loads(data.decode('utf-8'))