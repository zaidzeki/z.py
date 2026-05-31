"""Tests for ZFTP client using a mock/dummy FTPS server."""

from unittest.mock import MagicMock, patch
from z.ftp import ZFTP


class DummyFTPServer:
    """A dummy FTP/FTPS server representation for mock verification."""

    def __init__(self):
        self.mock_ftp = MagicMock()
        self.mock_ftp.nlst.return_value = ["file1.txt", "file2.txt"]


def test_z_ftp_lifecycle():
    """Test the FTPS context manager setup, login, cwd, and shutdown."""
    dummy_server = DummyFTPServer()
    with patch("z.ftp.FTP_TLS", return_value=dummy_server.mock_ftp) as mock_ftp_class:
        with ZFTP(user="dummy_user", passwd="dummy_password") as client:
            mock_ftp_class.assert_called_once_with("ftp-slim-shady.alwaysdata.net", timeout=60.0)
            dummy_server.mock_ftp.auth.assert_called_once()
            dummy_server.mock_ftp.prot_p.assert_called_once()
            dummy_server.mock_ftp.login.assert_called_once_with("dummy_user", "dummy_password")
            dummy_server.mock_ftp.cwd.assert_called_once_with("www")
            assert client.host == "ftp-slim-shady.alwaysdata.net"

        dummy_server.mock_ftp.quit.assert_called_once()


def test_z_ftp_operations(tmp_path):
    """Test the client API methods: upload, download, list_files, delete, etc."""
    dummy_server = DummyFTPServer()
    with patch("z.ftp.FTP_TLS", return_value=dummy_server.mock_ftp):
        # Create a dummy local file for upload test
        local_file = tmp_path / "test_upload.txt"
        local_file.write_bytes(b"content to upload")

        with ZFTP(user="dummy_user", passwd="dummy_password") as client:
            # Test upload
            client.upload(str(local_file))

            # Test list_files
            files = client.list_files()
            assert files == ["file1.txt", "file2.txt"]

            # Test download
            download_dest = tmp_path / "downloaded.txt"
            client.download("file1.txt", str(download_dest))

            # Test delete
            client.delete("file2.txt")

            # Test mkdir
            client.mkdir("new_dir")

            # Test rmdir
            client.rmdir("old_dir")

            # Test rename
            client.rename("a.txt", "b.txt")

        # Verify calls on the dummy FTP server
        dummy_server.mock_ftp.storbinary.assert_called_once()
        dummy_server.mock_ftp.retrbinary.assert_called_once()
        dummy_server.mock_ftp.delete.assert_called_once_with("file2.txt")
        dummy_server.mock_ftp.mkd.assert_called_once_with("new_dir")
        dummy_server.mock_ftp.rmd.assert_called_once_with("old_dir")
        dummy_server.mock_ftp.rename.assert_called_once_with("a.txt", "b.txt")
