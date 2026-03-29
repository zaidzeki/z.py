"""Core functionality for the ``z`` package."""


def greet(name: str = "world") -> str:
    """Return a friendly greeting.

    Args:
        name: Name to greet.

    Returns:
        A greeting string.
    """
    normalized = name.strip() or "world"
    return f"Hello, {normalized}!"
