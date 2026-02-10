"""Model layer for the refactored project structure."""

try:
    # Keep compatibility for DCD_MUSIC imports like `from src.models import SubspaceNet`.
    from DCD_MUSIC.src.models import *  # type: ignore # noqa: F401,F403
except ModuleNotFoundError:
    pass
