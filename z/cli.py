"""Command line interface for z (alias: zi)."""

from __future__ import annotations

import argparse
import bz2
import gzip
from hashlib import sha256
from pathlib import Path
import sqlite3
import tarfile
from time import time
from typing import Sequence
import lzma
import zipfile

from .crypto import encrypt_full

try:
    import getpass
except Exception:  # pragma: no cover
    getpass = None

CIPHER_ROOT = Path.home() / ".zekiprod" / "cipher"
KEYS_DIR = CIPHER_ROOT / "keys"
DB_PATH = CIPHER_ROOT / "main.db"


def _ensure_cipher_store() -> None:
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ciphers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                aliases TEXT,
                strength TEXT,
                created_at INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cipher_name TEXT NOT NULL,
                rsa_bits INTEGER NOT NULL,
                public_key_path TEXT NOT NULL,
                private_key_path TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
            """
        )


def _prompt_or_value(value: str | None, prompt: str) -> str:
    if value:
        return value
    return input(f"{prompt}: ").strip()


def _password_or_prompt(value: str | None) -> str:
    if value:
        return value
    if getpass is None:
        return input("encrypting password: ").strip()
    return getpass.getpass("encrypting password: ").strip()


def _derive_key(password: str) -> bytes:
    return sha256(password.encode("utf-8")).digest()


def recover(path: Path, output: Path | None = None) -> Path:
    """Recover a compressed or archived file."""
    suffixes = path.suffixes
    if not suffixes:
        raise ValueError("file has no extension")

    if path.suffix == ".gz":
        out = output or path.with_suffix("")
        out.write_bytes(gzip.decompress(path.read_bytes()))
        return out
    if path.suffix == ".xz":
        out = output or path.with_suffix("")
        out.write_bytes(lzma.decompress(path.read_bytes()))
        return out
    if path.suffix == ".bz2":
        out = output or path.with_suffix("")
        out.write_bytes(bz2.decompress(path.read_bytes()))
        return out
    if path.suffix == ".br":
        try:
            import brotli
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError("brotli is required to recover .br files") from exc
        out = output or path.with_suffix("")
        out.write_bytes(brotli.decompress(path.read_bytes()))
        return out
    if path.suffix == ".tar":
        out_dir = output or path.with_suffix("")
        out_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(path, "r") as archive:
            archive.extractall(out_dir)
        return out_dir
    if path.suffix == ".zip":
        out_dir = output or path.with_suffix("")
        out_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "r") as archive:
            archive.extractall(out_dir)
        return out_dir

    raise ValueError(f"unsupported recover format: {path.suffix}")


def cipher_generate(name: str, aliases: str, strength: str, password: str) -> None:
    """Register a cipher profile in the local DB."""
    _ensure_cipher_store()
    alias_csv = ",".join([a.strip() for a in aliases.split(",") if a.strip()])

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO ciphers(name, aliases, strength, created_at) VALUES (?, ?, ?, ?)",
            (name, alias_csv, strength, int(time())),
        )

    marker = KEYS_DIR / f"{name}.profile"
    marker.write_text(
        f"strength={strength}\naliases={alias_csv}\npassword_hint=sha256:{sha256(password.encode()).hexdigest()[:8]}\n"
    )


def _resolve_cipher_name(name_or_alias: str) -> str:
    _ensure_cipher_store()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT name, aliases FROM ciphers").fetchall()
    for name, aliases in rows:
        if name_or_alias == name:
            return name
        alias_set = {a.strip() for a in (aliases or "").split(",") if a.strip()}
        if name_or_alias in alias_set:
            return name
    raise ValueError(f"cipher not found: {name_or_alias}")


def cipher_encrypt(name_or_alias: str, rsa_bits: int, password: str) -> tuple[Path, Path]:
    """Generate RSA keys for a cipher profile and encrypt the private key with password."""
    _ensure_cipher_store()
    cipher_name = _resolve_cipher_name(name_or_alias)

    try:
        from Crypto.PublicKey import RSA
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ModuleNotFoundError("PyCryptodome is required for RSA generation") from exc

    key = RSA.generate(rsa_bits)
    public_pem = key.publickey().export_key()
    private_pem = key.export_key()

    ts = int(time())
    public_path = KEYS_DIR / f"{cipher_name}.{ts}.{rsa_bits}.pub.pem"
    private_path = KEYS_DIR / f"{cipher_name}.{ts}.{rsa_bits}.priv.enc"

    public_path.write_bytes(public_pem)
    private_path.write_bytes(encrypt_full(private_pem, _derive_key(password)))

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO keys(cipher_name, rsa_bits, public_key_path, private_key_path, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (cipher_name, rsa_bits, str(public_path), str(private_path), ts),
        )

    return public_path, private_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zi", description="z command line utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    recover_parser = sub.add_parser("recover", help="decompress or extract files")
    recover_parser.add_argument("path")
    recover_parser.add_argument("--output", "-o", default=None)

    cipher_parser = sub.add_parser("cipher", help="cipher profile and key operations")
    cipher_sub = cipher_parser.add_subparsers(dest="cipher_action", required=True)

    gen = cipher_sub.add_parser("generate", help="create/update cipher profile")
    gen.add_argument("--name", default=None)
    gen.add_argument("--aliases", default=None)
    gen.add_argument("--strength", default=None)
    gen.add_argument("--password", default=None)

    enc = cipher_sub.add_parser("encrypt", help="generate and encrypt an RSA private key")
    enc.add_argument("--name", default=None)
    enc.add_argument("--rsa-bits", type=int, default=None)
    enc.add_argument("--password", default=None)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "recover":
        output = recover(Path(args.path), Path(args.output) if args.output else None)
        print(output)
        return 0

    if args.command == "cipher" and args.cipher_action == "generate":
        name = _prompt_or_value(args.name, "name")
        aliases = _prompt_or_value(args.aliases, "aliases (comma-separated)")
        strength = _prompt_or_value(args.strength, "strength")
        password = _password_or_prompt(args.password)
        cipher_generate(name=name, aliases=aliases, strength=strength, password=password)
        print(f"cipher profile saved: {name}")
        return 0

    if args.command == "cipher" and args.cipher_action == "encrypt":
        name = _prompt_or_value(args.name, "name / alias")
        bits = args.rsa_bits or int(_prompt_or_value(None, "length of RSA key"))
        password = _password_or_prompt(args.password)
        public_path, private_path = cipher_encrypt(
            name_or_alias=name, rsa_bits=bits, password=password
        )
        print(public_path)
        print(private_path)
        return 0

    parser.error("unsupported command")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
