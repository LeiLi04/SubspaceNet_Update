"""Shared utility layer for refactored source tree."""

from src.utils.logging_utils import setup_logging_from_config
from src.utils.plotting import plot_scenario_results
from src.utils.utils import save_model_state
try:
    # Keep compatibility for DCD_MUSIC imports like `from src.utils import *`.
    from DCD_MUSIC.src.utils import *  # type: ignore # noqa: F401,F403
except ModuleNotFoundError:
    pass
