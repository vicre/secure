#!/usr/bin/env python3
"""
bw_decrypt.py

Decrypts files produced by bw_encrypt.py:
- Decrypts item.login.password where item.type == 1
- Decrypts custom field values where field.type == 1
Only decrypts strings prefixed with "fernet:".

Example:
  python ./bw_decrypt.py \
    bitwarden_export_20260109134347_reipur_encrypted.json \
    --keyfile bitwarden_export_20260109134347_reipur_decryption_key.txt
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from cryptography.fernet import Fernet, InvalidToken

ENC_PREFIX = "fernet:"


def decrypt_str(f: Fernet, s: str) -> str:
    if not isinstance(s, str) or not s.startswith(ENC_PREFIX):
        return s
    token = s[len(ENC_PREFIX):].encode("ascii")
    return f.decrypt(token).decode("utf-8")


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, dict) or "items" not in data or not isinstance(data["items"], list):
        raise ValueError("Input file does not look like a Bitwarden JSON export (missing top-level 'items' list).")
    return data


def save_json(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
        fp.write("\n")


def chmod_600(path: Path) -> None:
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def decrypt_bitwarden(data: Dict[str, Any], f: Fernet) -> Tuple[Dict[str, Any], int]:
    changed = 0
    items: List[Dict[str, Any]] = data.get("items", [])

    for item in items:
        if not isinstance(item, dict):
            continue

        # Decrypt passwords for login items (type == 1)
        if item.get("type") == 1:
            login = item.get("login")
            if isinstance(login, dict):
                pw = login.get("password")
                if isinstance(pw, str) and pw.startswith(ENC_PREFIX):
                    login["password"] = decrypt_str(f, pw)
                    changed += 1

        # Decrypt hidden custom fields (field.type == 1) and any other field values with prefix
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


def default_output_name(input_path: Path) -> Path:
    """
    If input is: something_reipur_encrypted.json
    output becomes: something_reipur_decrypted.json

    Otherwise:
    input.json -> input_decrypted.json
    """
    stem = input_path.stem
    if stem.endswith("_encrypted"):
        stem = stem[: -len("_encrypted")] + "_decrypted"
    else:
        stem = stem + "_decrypted"
    return input_path.with_name(stem + input_path.suffix)


def read_key_file(key_path: Path) -> bytes:
    """
    Reads the Fernet key from the key file written by bw_encrypt.py.
    That file may contain comment lines starting with '#'.
    """
    raw = key_path.read_text(encoding="utf-8", errors="strict").splitlines()
    for line in raw:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # First non-comment, non-empty line should be the key
        return line.encode("ascii")
    raise ValueError("No key found in key file (expected a base64 Fernet key on the first non-comment line).")


def main() -> int:
    p = argparse.ArgumentParser(description="Decrypt a Bitwarden JSON file produced by bw_encrypt.py")
    p.add_argument("input", type=Path, help="Encrypted JSON file (e.g. *_encrypted.json)")
    p.add_argument("--keyfile", type=Path, required=True, help="Decryption key txt file produced by bw_encrypt.py")
    p.add_argument("-o", "--output", type=Path, default=None, help="Output JSON path (default: auto)")
    p.add_argument("--force", action="store_true", help="Overwrite output if it exists")
    args = p.parse_args()

    in_path: Path = args.input
    key_path: Path = args.keyfile

    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")
    if not key_path.exists():
        raise SystemExit(f"Key file not found: {key_path}")

    out_path = args.output or default_output_name(in_path)
    if out_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing file: {out_path} (use --force)")

    key = read_key_file(key_path)
    f = Fernet(key)

    data = load_json(in_path)
    try:
        data2, changed = decrypt_bitwarden(data, f)
    except InvalidToken:
        raise SystemExit("Decryption failed: wrong key file or file content is corrupted.")

    save_json(out_path, data2)
    chmod_600(out_path)  # best-effort; keeps decrypted file private if supported
    print(f"Wrote: {out_path} (decrypted values: {changed})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
