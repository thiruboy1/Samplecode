"""Encrypt and decrypt text files using a password."""

from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


MAGIC = b"TXTCRYPT1"
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(salt=salt, length=KEY_SIZE, n=2**14, r=8, p=1)
    return kdf.derive(password.encode("utf-8"))


def write_new_file(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as output_file:
            output_file.write(data)
    except FileExistsError as exc:
        raise FileExistsError(f"Output already exists: {path}") from exc


def encrypt_file(source: Path, destination: Path, password: str) -> None:
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)
    ciphertext = AESGCM(key).encrypt(nonce, source.read_bytes(), MAGIC)
    write_new_file(destination, MAGIC + salt + nonce + ciphertext)


def decrypt_file(source: Path, destination: Path, password: str) -> None:
    payload = source.read_bytes()
    minimum_size = len(MAGIC) + SALT_SIZE + NONCE_SIZE
    if len(payload) <= minimum_size or not payload.startswith(MAGIC):
        raise ValueError("This is not a valid encrypted text file.")

    offset = len(MAGIC)
    salt = payload[offset : offset + SALT_SIZE]
    offset += SALT_SIZE
    nonce = payload[offset : offset + NONCE_SIZE]
    ciphertext = payload[offset + NONCE_SIZE :]
    key = derive_key(password, salt)

    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, MAGIC)
    except InvalidTag as exc:
        raise ValueError("Wrong password, or the encrypted file is damaged.") from exc

    write_new_file(destination, plaintext)


def safe_filename(value: str) -> str:
    """Accept a filename only, preventing access outside the expected folder."""
    if not value or Path(value).name != value or value in {".", ".."}:
        raise argparse.ArgumentTypeError("Pass only a filename, not a folder path.")
    return value


def ask_password(confirm: bool) -> str:
    password = getpass.getpass("Password: ")
    if not password:
        raise ValueError("Password cannot be empty.")
    if confirm and password != getpass.getpass("Confirm password: "):
        raise ValueError("Passwords do not match.")
    return password


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt a text file using a password."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt input/<filename>")
    encrypt_parser.add_argument("filename", type=safe_filename)

    decrypt_parser = subparsers.add_parser(
        "decrypt", help="Decrypt encrypted/<filename>.enc"
    )
    decrypt_parser.add_argument("filename", type=safe_filename)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    project_dir = Path(__file__).resolve().parent

    try:
        if args.command == "encrypt":
            source = project_dir / "input" / args.filename
            destination = project_dir / "encrypted" / f"{args.filename}.enc"
            if not source.is_file():
                raise FileNotFoundError(f"Input file not found: {source}")
            encrypt_file(source, destination, ask_password(confirm=True))
            print(f"Encrypted successfully: {destination}")
        else:
            source = project_dir / "encrypted" / args.filename
            output_name = (
                args.filename[:-4]
                if args.filename.lower().endswith(".enc")
                else f"{args.filename}.decrypted"
            )
            destination = project_dir / "decrypted" / output_name
            if not source.is_file():
                raise FileNotFoundError(f"Encrypted file not found: {source}")
            decrypt_file(source, destination, ask_password(confirm=False))
            print(f"Decrypted successfully: {destination}")
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
