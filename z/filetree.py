"""Visual directory-tree generator for ``z``.

Provides :class:`FileStructureGenerator` for rendering a filesystem path as a
Unicode tree, and :func:`generate_tree` as a convenience wrapper.

Examples
--------
>>> from z.filetree import generate_tree
>>> print(generate_tree(".", max_depth=2))
./
├── README.md
└── z/
    ├── __init__.py
    └── filetree.py
"""

from __future__ import annotations

import pathlib


class FileStructureGenerator:
    """Generates a visual tree structure for a given directory.

    Parameters
    ----------
    root_dir:
        Root directory to visualise.
    max_depth:
        Maximum recursion depth.  ``None`` means unlimited.
    include_hidden:
        When ``True``, entries whose names begin with ``.`` are shown.
    ignore_list:
        Exact entry names to suppress regardless of ``include_hidden``.
        Defaults to ``[".git", "__pycache__", ".DS_Store", "node_modules"]``.
    """

    # Tree drawing characters
    PIPE = "│"
    ELBOW = "└──"
    TEE = "├──"
    PIPE_PREFIX = "│   "
    SPACE_PREFIX = "    "

    _DEFAULT_IGNORE: list[str] = [".git", "__pycache__", ".DS_Store", "node_modules"]

    def __init__(
        self,
        root_dir: str | pathlib.Path,
        max_depth: int | None = None,
        include_hidden: bool = False,
        ignore_list: list[str] | None = None,
    ) -> None:
        self.root_path = pathlib.Path(root_dir)
        self.max_depth = max_depth
        self.include_hidden = include_hidden
        self.ignore_list: list[str] = (
            list(ignore_list) if ignore_list is not None else list(self._DEFAULT_IGNORE)
        )
        self._tree_lines: list[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self) -> str:
        """Return the full tree as a single newline-delimited string."""
        self._tree_lines = [self.root_path.name + "/"]
        self._build_tree(self.root_path, prefix="", depth=0)
        return "\n".join(self._tree_lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _should_ignore(self, path: pathlib.Path) -> bool:
        """Return ``True`` if *path* should be excluded from the tree."""
        if not self.include_hidden and path.name.startswith("."):
            return True
        return path.name in self.ignore_list

    def _build_tree(self, directory: pathlib.Path, prefix: str, depth: int) -> None:
        """Recursively append lines for *directory* to ``_tree_lines``."""
        if self.max_depth is not None and depth >= self.max_depth:
            return

        try:
            entries = sorted(
                (p for p in directory.iterdir() if not self._should_ignore(p)),
                # Directories first, then files; within each group sort by name
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except PermissionError:
            self._tree_lines.append(f"{prefix}{self.ELBOW} [Permission Denied]")
            return

        count = len(entries)
        for index, path in enumerate(entries):
            is_last = index == count - 1
            connector = self.ELBOW if is_last else self.TEE
            display_name = path.name + ("/" if path.is_dir() else "")
            self._tree_lines.append(f"{prefix}{connector} {display_name}")

            if path.is_dir():
                extension = self.SPACE_PREFIX if is_last else self.PIPE_PREFIX
                self._build_tree(path, prefix + extension, depth + 1)


def generate_tree(
    path: str | pathlib.Path = ".",
    max_depth: int | None = None,
    include_hidden: bool = False,
    ignore_list: list[str] | None = None,
) -> str:
    """Return a Unicode directory tree string for *path*.

    Parameters
    ----------
    path:
        Root directory to visualise (default: current working directory).
    max_depth:
        Maximum recursion depth.  ``None`` means unlimited.
    include_hidden:
        Show dotfiles and hidden directories when ``True``.
    ignore_list:
        Entry names to suppress.  Defaults to the
        :attr:`FileStructureGenerator._DEFAULT_IGNORE` list.

    Returns
    -------
    str
        Multi-line tree string.
    """
    return FileStructureGenerator(path, max_depth, include_hidden, ignore_list).generate()
