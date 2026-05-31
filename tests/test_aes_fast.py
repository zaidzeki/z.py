from __future__ import annotations

import io
import os
import tempfile
import unittest
from unittest.mock import patch

from z import decrypt_stream, encrypt_stream
from z.aes_fast import CHUNK_SIZE, MAGIC
from z.cli import main


class TestAesFast(unittest.TestCase):
    """Unit tests for streaming cryptographic methods."""

    def _roundtrip_bytes(self, data: bytes, password: str) -> bytes:
        """Helper to test streaming using in-memory BytesIO objects.

        Parameters
        ----------
        data : bytes
            Plaintext bytes to encrypt and decrypt.
        password : str
            Passphrase for the stream cipher.

        Returns
        -------
        bytes
            The decrypted output bytes.
        """
        fin = io.BytesIO(data)
        fenc = io.BytesIO()
        encrypt_stream(fin, fenc, password)

        fenc.seek(0)
        fout = io.BytesIO()
        decrypt_stream(fenc, fout, password)
        return fout.getvalue()

    def test_roundtrip_text(self):
        """Verify successful roundtrip encryption and decryption of standard text."""
        msg = b"The quick brown fox jumps over the lazy dog."
        self.assertEqual(self._roundtrip_bytes(msg, "pw"), msg)

    def test_roundtrip_empty(self):
        """Verify roundtrip with empty byte string input works correctly."""
        self.assertEqual(self._roundtrip_bytes(b"", "pw"), b"")

    def test_roundtrip_chunk_boundary(self):
        """Verify behavior around boundary sizes of chunk-based streaming buffer."""
        for size in [CHUNK_SIZE - 1, CHUNK_SIZE, CHUNK_SIZE + 1, CHUNK_SIZE * 2 + 50]:
            msg = os.urandom(size)
            self.assertEqual(self._roundtrip_bytes(msg, "pw"), msg, f"Failed at size {size}")

    def test_streaming_memory_footprint(self):
        """Confirm streaming logic handles data sizes larger than typical chunks."""
        msg = os.urandom(2 * 1024 * 1024)
        self.assertEqual(self._roundtrip_bytes(msg, "pw"), msg)

    def test_bad_magic(self):
        """Verify decryption fails when input lacks the required header magic."""
        fin = io.BytesIO(b"NOPE" + b"\x00" * 100)
        fout = io.BytesIO()
        with self.assertRaises(ValueError) as context:
            decrypt_stream(fin, fout, "pw")
        self.assertIn("bad magic", str(context.exception))

    def test_truncated_header(self):
        """Verify decryption fails with ValueError on incomplete header data."""
        fin = io.BytesIO(MAGIC + b"\x00" * 4)  # Only 4 bytes of nonce instead of 8
        fout = io.BytesIO()
        with self.assertRaises(ValueError) as context:
            decrypt_stream(fin, fout, "pw")
        self.assertIn("Truncated header", str(context.exception))

    def test_different_nonces(self):
        """Ensure nonces are randomly generated to produce different ciphertexts."""
        msg = b"same"
        enc1 = io.BytesIO()
        enc2 = io.BytesIO()
        encrypt_stream(io.BytesIO(msg), enc1, "pw")
        encrypt_stream(io.BytesIO(msg), enc2, "pw")
        self.assertNotEqual(enc1.getvalue(), enc2.getvalue())


class TestCliAesFast(unittest.TestCase):
    """Unit tests covering the command-line interface execution."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.input_file = os.path.join(self.temp_dir.name, "input.txt")
        self.output_file = os.path.join(self.temp_dir.name, "output.enc")
        self.decrypted_file = os.path.join(self.temp_dir.name, "decrypted.txt")

        with open(self.input_file, "wb") as f:
            f.write(b"Hello world, testing CLI functionality.")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cli_encrypt_decrypt_success(self):
        # Run encrypt pathway
        ret_enc = main(
            [
                "encrypt-fast",
                "-i",
                self.input_file,
                "-o",
                self.output_file,
                "-p",
                "supersecret",
            ]
        )
        self.assertEqual(ret_enc, 0)

        # Run decrypt pathway
        ret_dec = main(
            [
                "decrypt-fast",
                "-i",
                self.output_file,
                "-o",
                self.decrypted_file,
                "-p",
                "supersecret",
            ]
        )
        self.assertEqual(ret_dec, 0)

        # Verify plaintext output identity
        with open(self.decrypted_file, "rb") as f:
            self.assertEqual(f.read(), b"Hello world, testing CLI functionality.")

    def test_cli_same_file_error(self):
        # Verify attempt to encrypt in-place yields failure code to prevent data loss
        ret = main(["encrypt-fast", "-i", self.input_file, "-o", self.input_file, "-p", "pw"])
        self.assertEqual(ret, 1)

    @patch("getpass.getpass")
    def test_cli_mismatched_password_prompt(self, mock_getpass):
        # Verify mismatched verification password triggers exit code 1
        mock_getpass.side_effect = ["one", "two"]
        ret = main(["encrypt-fast", "-i", self.input_file, "-o", self.output_file])
        self.assertEqual(ret, 1)

    @patch("getpass.getpass")
    def test_cli_empty_password_prompt(self, mock_getpass):
        # Verify empty password prompt entry triggers exit code 1
        mock_getpass.return_value = ""
        ret = main(["encrypt-fast", "-i", self.input_file, "-o", self.output_file])
        self.assertEqual(ret, 1)

    def test_cli_non_existent_input(self):
        # Verify non-existent file yields exit code 2 (I/O error)
        ret = main(
            [
                "encrypt-fast",
                "-i",
                "nonexistent_file_path.xyz",
                "-o",
                self.output_file,
                "-p",
                "pw",
            ]
        )
        self.assertEqual(ret, 2)
