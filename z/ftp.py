"""FTP/FTPS client module for ``z``."""

from ftplib import FTP_TLS
import ssl

# Configuration Constants
FTP_HOST = "ftp-slim-shady.alwaysdata.net"
REMOTE_DIR = "www"


class ZFTP:
    """A context manager to handle FTPS connections to the configured server."""

    def __init__(
        self,
        host: str = FTP_HOST,
        user: str | None = None,
        passwd: str | None = None,
        remote_dir: str = REMOTE_DIR,
        timeout: float = 60.0,
        ssl_version=ssl.PROTOCOL_TLSv1_2,
    ):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.remote_dir = remote_dir
        self.timeout = timeout
        self.ssl_version = ssl_version

        self.ftp = FTP_TLS(self.host, timeout=self.timeout)
        self.ftp.ssl_version = self.ssl_version

    def __enter__(self):
        """Establishes the connection when entering the 'with' block."""
        self.ftp.auth()
        self.ftp.prot_p()
        print("FTPS connection initiated using TLS.")

        self.ftp.login(self.user, self.passwd)
        print("Logged in to FTPS server.")

        if self.remote_dir:
            self.ftp.cwd(self.remote_dir)
            print(f"Changed working directory to '{self.remote_dir}'.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures the connection is closed when exiting the 'with' block."""
        try:
            self.ftp.quit()
            print("FTPS connection closed.")
        except Exception:
            self.ftp.close()

    def upload(self, filename: str):
        """Upload a local file to the FTP server."""
        with open(filename, "rb") as fp:
            self.ftp.storbinary(f"STOR {filename}", fp)
        print(f"File '{filename}' uploaded successfully.")

    def download(self, filename: str, local_path: str | None = None):
        """Download a remote file from the FTP server."""
        out_path = local_path or filename
        with open(out_path, "wb") as fp:
            self.ftp.retrbinary(f"RETR {filename}", fp.write)
        print(f"File '{filename}' downloaded successfully to '{out_path}'.")

    def list_files(self) -> list[str]:
        """List file names in the current working directory."""
        files = self.ftp.nlst()
        print(f"Found {len(files)} items in '{self.remote_dir}':")
        for file in files:
            print(f" - {file}")
        return files

    def delete(self, filename: str):
        """Delete a file from the FTP server."""
        self.ftp.delete(filename)
        print(f"File '{filename}' deleted successfully.")

    def mkdir(self, dirname: str):
        """Create a remote directory on the FTP server."""
        self.ftp.mkd(dirname)
        print(f"Directory '{dirname}' created successfully.")

    def rmdir(self, dirname: str):
        """Remove a remote directory from the FTP server."""
        self.ftp.rmd(dirname)
        print(f"Directory '{dirname}' removed successfully.")

    def rename(self, fromname: str, toname: str):
        """Rename a file or directory on the FTP server."""
        self.ftp.rename(fromname, toname)
        print(f"Renamed '{fromname}' to '{toname}' successfully.")
