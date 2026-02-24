"""Warmstart helpers for the legacy training stack."""

from pathlib import Path


def warmstart_from_checkpoint(config_overrides: list[str], checkpoint_path: str) -> list[str]:
    """Inject standard warmstart overrides into an existing override list."""
    overrides = list(config_overrides)
    ckpt = Path(checkpoint_path)
    overrides.extend([
        "simulation.load_model=true",
        f"simulation.model_path={ckpt}",
    ])
    return overrides
