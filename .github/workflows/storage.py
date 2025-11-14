import os
import json
import time
import csv
from typing import List, Dict, Optional

from encryption import encrypt_payload, decrypt_payload, generate_aes_key, save_key_file, load_key_file


APP_NAME = '账号密码管理器'
DATA_FILE = 'saved_accounts.json'
KEY_FILE = 'secret.key'


def app_root() -> str:
    # Ensure data files live beside the executable/script
    # In PyInstaller onefile mode, use the directory containing the executable
    import sys
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def data_path() -> str:
    return os.path.join(app_root(), DATA_FILE)


def key_path() -> str:
    return os.path.join(app_root(), KEY_FILE)


class KeyManager:
    def __init__(self):
        self._key: Optional[bytes] = None
        self._encrypted: bool = False

    def ensure_key_exists(self):
        kp = key_path()
        if not os.path.exists(kp):
            key = generate_aes_key()
            save_key_file(kp, key, password=None)

    def load(self, password: Optional[str]) -> None:
        self.ensure_key_exists()
        key, enc_flag = load_key_file(key_path(), password)
        self._key = key
        self._encrypted = enc_flag

    def set_password(self, new_password: Optional[str]):
        # Re-write secret.key with or without password protection
        if self._key is None:
            self.ensure_key_exists()
            key, _ = load_key_file(key_path(), None)
            self._key = key
        save_key_file(key_path(), self._key, new_password)
        self._encrypted = bool(new_password)

    @property
    def key(self) -> bytes:
        assert self._key is not None, 'Key not loaded'
        return self._key

    @property
    def encrypted(self) -> bool:
        return self._encrypted


class SecureStorage:
    def __init__(self, key_mgr: KeyManager):
        self.key_mgr = key_mgr
        self.accounts: List[Dict] = []

    def load(self):
        p = data_path()
        if not os.path.exists(p):
            self.accounts = []
            return
        with open(p, 'r', encoding='utf-8') as f:
            blob = json.load(f)
        payload = decrypt_payload(self.key_mgr.key, blob)
        self.accounts = payload.get('accounts', [])

    def save(self):
        payload = {'accounts': self.accounts, 'ts': int(time.time())}
        blob = encrypt_payload(self.key_mgr.key, payload)
        with open(data_path(), 'w', encoding='utf-8') as f:
            json.dump(blob, f, ensure_ascii=False)

    def add(self, record: Dict):
        self.accounts.append(record)
        self.save()

    def delete_by_index(self, idx: int):
        if 0 <= idx < len(self.accounts):
            del self.accounts[idx]
            self.save()

    def search(self, q: str) -> List[Dict]:
        q = q.strip()
        if not q:
            return list(self.accounts)
        key_fields = ['website', 'account', 'email', 'phone', 'note']
        res = []
        for r in self.accounts:
            for f in key_fields:
                val = str(r.get(f, ''))
                if q.lower() in val.lower():
                    res.append(r)
                    break
        return res

    def export_csv(self, path: str):
        fields = ['website', 'account', 'password', 'phone', 'email', 'note', 'created_at']
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in self.accounts:
                w.writerow({k: r.get(k, '') for k in fields})

    def import_csv(self, path: str) -> int:
        count = 0
        with open(path, 'r', newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            required = {'account', 'password'}
            # 允许自定义字段名，但最少要包含账号和密码
            headers = set([h.strip().lower() for h in r.fieldnames or []])
            if not required.issubset(headers):
                raise ValueError('CSV需包含“账号(account)”与“密码(password)”字段')
            for row in r:
                rec = {
                    'website': row.get('website', ''),
                    'account': row.get('account', ''),
                    'password': row.get('password', ''),
                    'phone': row.get('phone', ''),
                    'email': row.get('email', ''),
                    'note': row.get('note', ''),
                    'created_at': int(time.time())
                }
                if rec['account'] and rec['password']:
                    self.accounts.append(rec)
                    count += 1
        self.save()
        return count