"""Tests for z.filetree – directory-tree generator."""

from __future__ import annotations

import pathlib

import pytest

from z.filetree import FileStructureGenerator, generate_tree


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def simple_tree(tmp_path: pathlib.Path) -> pathlib.Path:
    """
    tmp_path/
    ├── subdir/
    │   └── child.txt
    ├── alpha.txt
    └── beta.txt
    """
    (tmp_path / "alpha.txt").touch()
    (tmp_path / "beta.txt").touch()
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "child.txt").touch()
    return tmp_path


@pytest.fixture()
def hidden_tree(tmp_path: pathlib.Path) -> pathlib.Path:
    """tmp_path with a visible file and a hidden file."""
    (tmp_path / "visible.txt").touch()
    (tmp_path / ".hidden").touch()
    return tmp_path


@pytest.fixture()
def deep_tree(tmp_path: pathlib.Path) -> pathlib.Path:
    """Three levels deep: level0/level1/level2/file.txt"""
    deep = tmp_path / "level0" / "level1" / "level2"
    deep.mkdir(parents=True)
    (deep / "file.txt").touch()
    return tmp_path


# ---------------------------------------------------------------------------
# Root line
# ---------------------------------------------------------------------------


class TestRootLine:
    def test_root_line_includes_trailing_slash(self, simple_tree):
        tree = generate_tree(simple_tree)
        first_line = tree.splitlines()[0]
        assert first_line.endswith("/")

    def test_root_line_is_directory_name(self, simple_tree):
        tree = generate_tree(simple_tree)
        assert tree.splitlines()[0] == simple_tree.name + "/"


# ---------------------------------------------------------------------------
# Entry listing
# ---------------------------------------------------------------------------


class TestEntryListing:
    def test_files_appear_in_tree(self, simple_tree):
        tree = generate_tree(simple_tree)
        assert "alpha.txt" in tree
        assert "beta.txt" in tree

    def test_subdirectory_has_trailing_slash(self, simple_tree):
        tree = generate_tree(simple_tree)
        assert "subdir/" in tree

    def test_nested_file_appears(self, simple_tree):
        tree = generate_tree(simple_tree)
        assert "child.txt" in tree

    def test_directories_listed_before_files(self, simple_tree):
        lines = generate_tree(simple_tree).splitlines()
        dir_idx = next(i for i, ln in enumerate(lines) if "subdir/" in ln)
        file_idx = next(i for i, ln in enumerate(lines) if "alpha.txt" in ln)
        assert dir_idx < file_idx


# ---------------------------------------------------------------------------
# Connectors
# ---------------------------------------------------------------------------


class TestConnectors:
    def test_last_entry_uses_elbow(self, simple_tree):
        tree = generate_tree(simple_tree)
        lines = tree.splitlines()[1:]  # skip root
        assert lines[-1].lstrip().startswith("└──")

    def test_non_last_entry_uses_tee(self, simple_tree):
        tree = generate_tree(simple_tree)
        # subdir/ is the first entry (dirs before files) and NOT last
        tee_line = next(ln for ln in tree.splitlines() if "subdir/" in ln)
        assert "├──" in tee_line


# ---------------------------------------------------------------------------
# max_depth
# ---------------------------------------------------------------------------


class TestMaxDepth:
    def test_depth_zero_shows_only_root(self, simple_tree):
        tree = generate_tree(simple_tree, max_depth=0)
        assert tree.strip() == simple_tree.name + "/"

    def test_depth_one_excludes_nested_files(self, simple_tree):
        tree = generate_tree(simple_tree, max_depth=1)
        assert "child.txt" not in tree
        assert "subdir/" in tree

    def test_depth_two_includes_nested_files(self, deep_tree):
        tree = generate_tree(deep_tree, max_depth=4)
        assert "file.txt" in tree

    def test_depth_none_is_unlimited(self, deep_tree):
        tree = generate_tree(deep_tree, max_depth=None)
        assert "file.txt" in tree


# ---------------------------------------------------------------------------
# Hidden files
# ---------------------------------------------------------------------------


class TestHiddenFiles:
    def test_hidden_excluded_by_default(self, hidden_tree):
        tree = generate_tree(hidden_tree)
        assert ".hidden" not in tree

    def test_hidden_included_when_flag_set(self, hidden_tree):
        tree = generate_tree(hidden_tree, include_hidden=True)
        assert ".hidden" in tree

    def test_visible_always_included(self, hidden_tree):
        tree = generate_tree(hidden_tree)
        assert "visible.txt" in tree


# ---------------------------------------------------------------------------
# ignore_list
# ---------------------------------------------------------------------------


class TestIgnoreList:
    def test_default_ignore_suppresses_pycache(self, tmp_path):
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "keep.txt").touch()
        tree = generate_tree(tmp_path)
        assert "__pycache__" not in tree
        assert "keep.txt" in tree

    def test_custom_ignore_list(self, tmp_path):
        (tmp_path / "skip_me").mkdir()
        (tmp_path / "keep.txt").touch()
        tree = generate_tree(tmp_path, ignore_list=["skip_me"])
        assert "skip_me" not in tree
        assert "keep.txt" in tree

    def test_empty_ignore_list_shows_all(self, tmp_path):
        (tmp_path / "__pycache__").mkdir()
        tree = generate_tree(tmp_path, ignore_list=[])
        assert "__pycache__" in tree


# ---------------------------------------------------------------------------
# Permission denied
# ---------------------------------------------------------------------------


class TestPermissionDenied:
    def test_permission_denied_shows_message(self, tmp_path, monkeypatch):
        sub = tmp_path / "locked"
        sub.mkdir()
        (tmp_path / "other.txt").touch()

        original_iterdir = pathlib.Path.iterdir

        def mock_iterdir(self):
            if self == sub:
                raise PermissionError("locked")
            return original_iterdir(self)

        monkeypatch.setattr(pathlib.Path, "iterdir", mock_iterdir)
        tree = generate_tree(tmp_path)
        assert "Permission Denied" in tree


# ---------------------------------------------------------------------------
# generate_tree convenience wrapper
# ---------------------------------------------------------------------------


class TestGenerateTree:
    def test_returns_string(self, simple_tree):
        result = generate_tree(simple_tree)
        assert isinstance(result, str)

    def test_accepts_string_path(self, simple_tree):
        result = generate_tree(str(simple_tree))
        assert simple_tree.name in result

    def test_accepts_pathlib_path(self, simple_tree):
        result = generate_tree(simple_tree)
        assert simple_tree.name in result


# ---------------------------------------------------------------------------
# FileStructureGenerator class API
# ---------------------------------------------------------------------------


class TestClassAPI:
    def test_generate_called_twice_is_idempotent(self, simple_tree):
        gen = FileStructureGenerator(simple_tree)
        first = gen.generate()
        second = gen.generate()
        assert first == second

    def test_default_ignore_list_not_mutated(self, tmp_path):
        gen = FileStructureGenerator(tmp_path, ignore_list=["custom"])
        assert gen.ignore_list == ["custom"]
        assert FileStructureGenerator._DEFAULT_IGNORE == [
            ".git",
            "__pycache__",
            ".DS_Store",
            "node_modules",
        ]
