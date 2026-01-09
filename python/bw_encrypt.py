#!/usr/bin/env python3
"""
Bitwarden JSON export encryptor

- Loads a Bitwarden .json export
- Encrypts:
  - item.login.password for items where item.type == 1 (login items)
  - custom field values where field.type == 1 (hidden fields)
- Writes:
  - <input>_<tag>_encrypted.json
  - <input>_<tag>_decryption_key.txt

NOTE:
This is for safely storing/exporting data. Bitwarden will NOT import this encrypted JSON as a normal export.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    raise SystemExit(
        "Missing dependency: cryptography\n\n"
        "Install it with:\n"
        "  python3 -m pip install --upgrade cryptography\n"
    )

ENC_PREFIX = "fernet:"


def encrypt_str(f: Fernet, s: str) -> str:
    return ENC_PREFIX + f.encrypt(s.encode("utf-8")).decode("ascii")


def decrypt_str(f: Fernet, s: str) -> str:
    if not isinstance(s, str) or not s.startswith(ENC_PREFIX):
        return s
    token = s[len(ENC_PREFIX):].encode("ascii")
    return f.decrypt(token).decode("utf-8")


def chmod_600(path: Path) -> None:
    try:
        os.chmod(path, 0o600)
    except Exception:
        # Best effort (Windows/odd FS may not support)
        pass


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "items" not in data or not isinstance(data["items"], list):
        raise ValueError("Input file does not look like a Bitwarden JSON export (missing top-level 'items' list).")
    return data


def save_json(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def encrypt_bitwarden(data: Dict[str, Any], f: Fernet) -> Tuple[Dict[str, Any], int]:
    changed = 0
    items: List[Dict[str, Any]] = data.get("items", [])

    for item in items:
        if not isinstance(item, dict):
            continue

        # Encrypt passwords for login items (type == 1)
        if item.get("type") == 1:
            login = item.get("login")
            if isinstance(login, dict):
                pw = login.get("password")
                if isinstance(pw, str) and pw and not pw.startswith(ENC_PREFIX):
                    login["password"] = encrypt_str(f, pw)
                    changed += 1

        # Encrypt hidden custom fields (field.type == 1)
        fields = item.get("fields")
        if isinstance(fields, list):
            for field in fields:
                if not isinstance(field, dict):
                    continue
                if field.get("type") == 1:
                    val = field.get("value")
                    if isinstance(val, str) and val and not val.startswith(ENC_PREFIX):
                        field["value"] = encrypt_str(f, val)
                        changed += 1

    # Mark as encrypted (informational)
    data["encrypted"] = True
    data.setdefault("encryption", {})
    if isinstance(data["encryption"], dict):
        data["encryption"].update(
            {
                "scheme": "fernet",
                "prefix": ENC_PREFIX,
                "scope": [
                    "items[].login.password where items[].type==1",
                    "items[].fields[].value where fields[].type==1",
                ],
            }
        )

    return data, changed


def decrypt_bitwarden(data: Dict[str, Any], f: Fernet) -> Tuple[Dict[str, Any], int]:
    changed = 0
    items: List[Dict[str, Any]] = data.get("items", [])

    for item in items:
        if not isinstance(item, dict):
            continue

        if item.get("type") == 1:
            login = item.get("login")
            if isinstance(login, dict):
                pw = login.get("password")
                if isinstance(pw, str) and pw.startswith(ENC_PREFIX):
                    login["password"] = decrypt_str(f, pw)
                    changed += 1

        fields = item.get("fields")
        if isinstance(fields, list):
            for field in fields:
                if not isinstance(field, dict):
                    continue
                val = field.get("value")
                if isinstance(val, str) and val.startswith(ENC_PREFIX):
                    field["value"] = decrypt_str(f, val)
                    changed += 1

    data["encrypted"] = False
    return data, changed


def main() -> int:
    p = argparse.ArgumentParser(description="Encrypt/decrypt Bitwarden JSON export passwords + hidden fields.")
    p.add_argument("input", type=Path, help="Path to Bitwarden JSON export (e.g. bitwarden_export_*.json)")
    p.add_argument("--tag", default="reipur", help="Tag used in output filenames (default: reipur)")
    p.add_argument("--force", action="store_true", help="Overwrite output files if they exist")

    mode = p.add_mutually_exclusive_group(required=False)
    mode.add_argument("--decrypt", action="store_true", help="Decrypt an encrypted JSON (requires --keyfile)")
    mode.add_argument("--encrypt", action="store_true", help="Encrypt (default)")

    p.add_argument("--keyfile", type=Path, default=None, help="Key file to use (required for --decrypt; optional for encrypt)")
    args = p.parse_args()

    in_path: Path = args.input
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    data = load_json(in_path)

    # Build output filenames
    stem = in_path.stem
    out_dir = in_path.parent
    if args.decrypt:
        out_json = out_dir / f"{stem}_{args.tag}_decrypted.json"
        key_path = args.keyfile
        if key_path is None:
            raise SystemExit("--decrypt requires --keyfile <path-to-decryption-key.txt>")
    else:
        out_json = out_dir / f"{stem}_{args.tag}_encrypted.json"
        key_path = args.keyfile or (out_dir / f"{stem}_{args.tag}_decryption_key.txt")

    if out_json.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing file: {out_json} (use --force)")

    if args.decrypt:
        key_bytes = key_path.read_bytes().strip()
        f = Fernet(key_bytes)
        try:
            data2, changed = decrypt_bitwarden(data, f)
        except InvalidToken:
            raise SystemExit("Decryption failed: wrong key file or file content is corrupted.")
        save_json(out_json, data2)
        print(f"Wrote: {out_json} (decrypted values: {changed})")
        return 0

    # Encrypt (default)
    if key_path.exists():
        # If a key file exists, reuse it to make encryption repeatable.
        key = key_path.read_bytes().strip()
    else:
        key = Fernet.generate_key()
        if key_path.exists() and not args.force:
            raise SystemExit(f"Refusing to overwrite existing key file: {key_path} (use --force)")
        key_path.write_bytes(
            key
            + b"\n"
            + b"# Keep this file secret. It is required to decrypt the encrypted Bitwarden export.\n"
            + b"# Encryption scheme: Fernet (cryptography)\n"
            + b"# Encrypted values are prefixed with: fernet:\n"
        )
        chmod_600(key_path)

    f = Fernet(key)
    data2, changed = encrypt_bitwarden(data, f)
    save_json(out_json, data2)
    print(f"Wrote: {out_json} (encrypted values: {changed})")
    print(f"Wrote: {key_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
