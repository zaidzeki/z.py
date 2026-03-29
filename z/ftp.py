"""FTP helpers for the ``z.ftp`` module."""

from __future__ import annotations

from dataclasses import dataclass
from ftplib import FTP as _StdFTP
from ftplib import FTP_TLS as _StdFTPTLS
from pathlib import Path
import ssl


@dataclass(frozen=True)
class FTPConfig:
    """Configuration for FTP connections."""

    user: str
    password: str
    host: str
    port: int = 21
    cwd: str = "/"
    use_tls: bool = True
    timeout: int = 60


class FTP:
    """Factory wrapper for creating isolated FTP sessions."""

    def __init__(
        self,
        *,
        user: str,
        password: str,
        host: str,
        port: int = 21,
        cwd: str = "/",
        use_tls: bool = True,
        timeout: int = 60,
    ) -> None:
        self.config = FTPConfig(
            user=user,
            password=password,
            host=host,
            port=port,
            cwd=cwd,
            use_tls=use_tls,
            timeout=timeout,
        )

    def open(self) -> "FTPInstance":
        """Create and return a new FTP session instance."""
        return FTPInstance(self.config)


class FTPInstance:
    """Single FTP connection instance."""

    def __init__(self, config: FTPConfig) -> None:
        self._config = config
        self._client = self._connect()

    def _connect(self) -> _StdFTP | _StdFTPTLS:
        if self._config.use_tls:
            client = _StdFTPTLS(self._config.host, timeout=self._config.timeout)
            client.ssl_version = ssl.PROTOCOL_TLSv1_2
            client.connect(self._config.host, self._config.port)
            client.login(self._config.user, self._config.password)
            client.auth()
            client.prot_p()
        else:
            client = _StdFTP()
            client.connect(self._config.host, self._config.port, timeout=self._config.timeout)
            client.login(self._config.user, self._config.password)

        if self._config.cwd:
            client.cwd(self._config.cwd)
        return client

    def cd(self, path: str) -> None:
        self._client.cwd(path)

    def ls(self) -> list[str]:
        return self._client.nlst()

    def upload(self, local_path: str | Path, remote_name: str | None = None) -> str:
        path = Path(local_path)
        name = remote_name or path.name
        with path.open("rb") as handle:
            self._client.storbinary(f"STOR {name}", handle)
        return name

    def rm(self, remote_path: str) -> None:
        self._client.delete(remote_path)

    def download(self, remote_path: str, local_path: str | Path) -> Path:
        destination = Path(local_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as handle:
            self._client.retrbinary(f"RETR {remote_path}", handle.write)
        return destination

    def mv(self, source_path: str, destination_path: str) -> None:
        self._client.rename(source_path, destination_path)

    def close(self) -> None:
        try:
            self._client.quit()
        except Exception:
            self._client.close()

    def __enter__(self) -> "FTPInstance":
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: object
    ) -> None:
        self.close()
