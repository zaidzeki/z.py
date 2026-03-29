"""Tests for ``z.ftp``."""

from pathlib import Path

import z.ftp as ftp_mod


class FakeClient:
    def __init__(self, host: str | None = None, timeout: int | None = None) -> None:
        self.host = host
        self.timeout = timeout
        self.calls: list[tuple] = []
        self.files: dict[str, bytes] = {}
        self.cwd_path = "/"

    def connect(self, host: str, port: int, timeout: int | None = None) -> None:
        self.calls.append(("connect", host, port, timeout))

    def login(self, user: str, password: str) -> None:
        self.calls.append(("login", user, password))

    def auth(self) -> None:
        self.calls.append(("auth",))

    def prot_p(self) -> None:
        self.calls.append(("prot_p",))

    def cwd(self, path: str) -> None:
        self.cwd_path = path
        self.calls.append(("cwd", path))

    def nlst(self) -> list[str]:
        return sorted(self.files)

    def storbinary(self, command: str, handle) -> None:
        name = command.split(" ", 1)[1]
        self.files[name] = handle.read()
        self.calls.append(("storbinary", name))

    def retrbinary(self, command: str, callback) -> None:
        name = command.split(" ", 1)[1]
        callback(self.files[name])
        self.calls.append(("retrbinary", name))

    def delete(self, path: str) -> None:
        self.files.pop(path, None)
        self.calls.append(("delete", path))

    def rename(self, src: str, dst: str) -> None:
        self.files[dst] = self.files.pop(src)
        self.calls.append(("rename", src, dst))

    def quit(self) -> None:
        self.calls.append(("quit",))

    def close(self) -> None:
        self.calls.append(("close",))


class FakeTLS(FakeClient):
    ssl_version = None


def test_open_with_tls_and_basic_operations(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(ftp_mod, "_StdFTPTLS", FakeTLS)

    ftp = ftp_mod.FTP(
        user="u", password="p", host="example.org", port=2121, cwd="/incoming", use_tls=True
    )
    session = ftp.open()

    assert isinstance(session, ftp_mod.FTPInstance)
    assert session.ls() == []

    source = tmp_path / "a.txt"
    source.write_bytes(b"hello")
    session.upload(source)
    assert session.ls() == ["a.txt"]

    out = session.download("a.txt", tmp_path / "out" / "a.txt")
    assert out.read_bytes() == b"hello"

    session.mv("a.txt", "b.txt")
    assert session.ls() == ["b.txt"]

    session.rm("b.txt")
    assert session.ls() == []

    session.close()


def test_open_without_tls(monkeypatch) -> None:
    monkeypatch.setattr(ftp_mod, "_StdFTP", FakeClient)

    ftp = ftp_mod.FTP(user="u", password="p", host="example.org", port=21, cwd="/", use_tls=False)
    session = ftp.open()

    session.cd("/tmp")
    assert session._client.cwd_path == "/tmp"
