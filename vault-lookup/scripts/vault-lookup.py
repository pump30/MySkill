#!/usr/bin/env python3
"""
Vaultwarden vault lookup script.
Authenticates via Bitwarden API, decrypts vault entries client-side,
and searches by name/URI/username.

Usage:
  python3 vault-lookup.py [search_term]

Without search_term: lists all entries.
With search_term: filters entries matching the term (case-insensitive).

Output: JSON array of matching entries.
"""

import hashlib
import base64
import json
import sys
import os
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
    from cryptography.hazmat.backends import default_backend
    import requests
except ImportError:
    print(json.dumps({"error": "Missing dependencies. Run: pip3 install cryptography requests --break-system-packages"}))
    sys.exit(1)


def load_config():
    config_path = Path.home() / ".config" / "vault-lookup" / "config.json"
    if not config_path.exists():
        print(json.dumps({"error": f"Config not found at {config_path}"}))
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def decrypt_aes(enc_string, key):
    """Decrypt a Bitwarden encrypted string (type 2: AES-CBC-256)."""
    if not enc_string:
        return None
    parts = enc_string.split(".")
    pieces = parts[1].split("|")
    iv = base64.b64decode(pieces[0])
    ct = base64.b64decode(pieces[1])

    enc_key_part = key[:32]
    cipher = Cipher(algorithms.AES(enc_key_part), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()

    pad_len = padded[-1]
    if 1 <= pad_len <= 16:
        return padded[:-pad_len].decode("utf-8", errors="replace")
    return padded.decode("utf-8", errors="replace")


def main():
    config = load_config()
    base_url = config["base_url"].rstrip("/")
    email = config["email"]
    password = config["master_password"]

    search_term = sys.argv[1].lower() if len(sys.argv) > 1 else None

    # 1. Get KDF params
    resp = requests.post(f"{base_url}/identity/accounts/prelogin",
                         json={"email": email})
    prelogin = resp.json()
    iterations = prelogin["kdfIterations"]

    # 2. Derive master key + hashed password
    master_key = hashlib.pbkdf2_hmac("sha256", password.encode(), email.lower().encode(), iterations)
    hashed_password = base64.b64encode(
        hashlib.pbkdf2_hmac("sha256", master_key, password.encode(), 1)
    ).decode()

    # 3. Login
    resp = requests.post(f"{base_url}/identity/connect/token", data={
        "grant_type": "password",
        "username": email,
        "password": hashed_password,
        "scope": "api offline_access",
        "client_id": "cli",
        "deviceType": "14",
        "deviceIdentifier": "claude-code-vault-lookup",
        "deviceName": "claude-code",
    })
    if resp.status_code != 200:
        print(json.dumps({"error": f"Login failed: {resp.json().get('message', resp.status_code)}"}))
        sys.exit(1)

    token_data = resp.json()
    access_token = token_data["access_token"]
    enc_key_b64 = token_data["Key"]

    # 4. Derive stretched key
    stretched_enc = HKDFExpand(algorithm=hashes.SHA256(), length=32, info=b"enc",
                              backend=default_backend()).derive(master_key)
    stretched_mac = HKDFExpand(algorithm=hashes.SHA256(), length=32, info=b"mac",
                              backend=default_backend()).derive(master_key)
    stretched_key = stretched_enc + stretched_mac

    # 5. Decrypt user encryption key (raw bytes, not decoded to str)
    parts = enc_key_b64.split(".")
    pieces = parts[1].split("|")
    iv = base64.b64decode(pieces[0])
    ct = base64.b64decode(pieces[1])
    enc_key_part = stretched_key[:32]
    cipher = Cipher(algorithms.AES(enc_key_part), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()
    pad_len = padded[-1]
    user_key = padded[:-pad_len] if 1 <= pad_len <= 16 else padded

    # 6. Fetch ciphers
    resp = requests.get(f"{base_url}/api/ciphers",
                        headers={"Authorization": f"Bearer {access_token}"})
    ciphers = resp.json()["data"]

    # 7. Decrypt and filter
    results = []
    for c in ciphers:
        try:
            name = decrypt_aes(c["name"], user_key) or ""
            entry = {"name": name, "type": c["type"]}

            if c["type"] == 1 and c.get("login"):
                login = c["login"]
                entry["username"] = decrypt_aes(login.get("username"), user_key) if login.get("username") else None
                entry["password"] = decrypt_aes(login.get("password"), user_key) if login.get("password") else None
                entry["uris"] = []
                if login.get("uris"):
                    for u in login["uris"]:
                        uri = decrypt_aes(u.get("uri"), user_key)
                        if uri:
                            entry["uris"].append(uri)

            if c.get("notes"):
                entry["notes"] = decrypt_aes(c["notes"], user_key)

            # Filter
            if search_term:
                searchable = " ".join(filter(None, [
                    name,
                    entry.get("username", ""),
                    " ".join(entry.get("uris", [])),
                    entry.get("notes", ""),
                ])).lower()
                if search_term not in searchable:
                    continue

            results.append(entry)
        except Exception as e:
            continue

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
