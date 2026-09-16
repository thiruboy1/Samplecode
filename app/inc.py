"""Password-based authenticated encryption for image files."""

from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


MAGIC = b"IMGCRYPT1"
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from a password using scrypt."""
    kdf = Scrypt(salt=salt, length=KEY_SIZE, n=2**14, r=8, p=1)
    return kdf.derive(password.encode("utf-8"))


def write_new_file(path: Path, data: bytes) -> None:
    """Write data without accidentally replacing an existing file."""
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

    plaintext = source.read_bytes()
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, MAGIC)
    write_new_file(destination, MAGIC + salt + nonce + ciphertext)


def decrypt_file(source: Path, destination: Path, password: str) -> None:
    payload = source.read_bytes()
    header_size = len(MAGIC) + SALT_SIZE + NONCE_SIZE

    if len(payload) <= header_size or not payload.startswith(MAGIC):
        raise ValueError("This is not a valid encrypted image file.")

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


def find_one(folder: Path, encrypted: bool) -> Path:
    if not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    candidates = sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and (path.suffix.lower() == ".enc") == encrypted
    )
    if not candidates:
        kind = "encrypted file" if encrypted else "image"
        raise FileNotFoundError(f"No {kind} found in {folder}")
    if len(candidates) > 1:
        names = ", ".join(path.name for path in candidates)
        raise ValueError(f"More than one file found ({names}). Pass the file path explicitly.")
    return candidates[0]


def ask_password(confirm: bool) -> str:
    password = getpass.getpass("Password: ")
    if not password:
        raise ValueError("Password cannot be empty.")
    if confirm and password != getpass.getpass("Confirm password: "):
        raise ValueError("Passwords do not match.")
    return password


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt an image using a password."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt an image")
    encrypt_parser.add_argument(
        "file", nargs="?", type=Path, help="Image path (default: the file in input/)"
    )
    encrypt_parser.add_argument("-o", "--output", type=Path, help="Encrypted output path")

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt an image")
    decrypt_parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Encrypted path (default: the .enc file in encrypted/)",
    )
    decrypt_parser.add_argument("-o", "--output", type=Path, help="Decrypted output path")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    project_dir = Path(__file__).resolve().parent

    try:
        if args.command == "encrypt":
            source = args.file or find_one(project_dir / "input", encrypted=False)
            source = source.resolve()
            if not source.is_file():
                raise FileNotFoundError(f"File not found: {source}")
            destination = args.output or project_dir / "encrypted" / f"{source.name}.enc"
            encrypt_file(source, destination.resolve(), ask_password(confirm=True))
            print(f"Encrypted successfully: {destination.resolve()}")
        else:
            source = args.file or find_one(project_dir / "encrypted", encrypted=True)
            source = source.resolve()
            if not source.is_file():
                raise FileNotFoundError(f"File not found: {source}")
            default_name = source.name[:-4] if source.name.lower().endswith(".enc") else source.stem
            destination = args.output or project_dir / "decrypted" / default_name
            decrypt_file(source, destination.resolve(), ask_password(confirm=False))
            print(f"Decrypted successfully: {destination.resolve()}")
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
