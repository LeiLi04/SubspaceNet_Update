"""Validate c_i = y^T S^-1 y against the chi-square null distribution.

Usage:
    python scripts/validate_null_distribution.py --input outputs/null_validation.npz
    python scripts/validate_null_distribution.py --synthetic-null  # smoke only

Generate a real input file by running online learning with:
    online_learning.dump_c_per_step_path=outputs/null_validation_real.npz
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
from scipy import stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _load_values(path: Path) -> np.ndarray:
    data = np.load(path)
    for key in ("c", "c_values", "c_per_step"):
        if key in data:
            return np.asarray(data[key], dtype=np.float64)
    raise ValueError(f"{path} must contain one of: c, c_values, c_per_step")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None, help="Pipeline-generated npz file with real c values.")
    parser.add_argument("--dof", type=int, default=3)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--samples", type=int, default=300)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--synthetic-null", action="store_true", help="Generate synthetic chi-square samples for script smoke only.")
    parser.add_argument("--out", type=Path, default=None, help="Optional path to copy the tested c values.")
    args = parser.parse_args()

    if args.input is None and not args.synthetic_null:
        parser.error(
            "--input is required for real validation. "
            "Set online_learning.dump_c_per_step_path in a no-drift run to generate it, "
            "or pass --synthetic-null for script smoke only."
        )

    if args.synthetic_null:
        rng = np.random.default_rng(args.seed)
        c_values = rng.chisquare(df=args.dof, size=args.samples).astype(np.float64)
        logger.info("Generated synthetic chi-square null samples for script smoke only.")
    else:
        c_values = _load_values(args.input)
        logger.info("Loaded %s c-values from %s", len(c_values), args.input)

    if c_values.size == 0:
        raise ValueError("No c-values available for validation")

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        np.savez(args.out, c=c_values, dof=args.dof)

    ks_stat, p_value = stats.kstest(c_values, "chi2", args=(args.dof,))
    logger.info("N=%s samples, mean=%.3f (theoretical %s)", len(c_values), c_values.mean(), args.dof)
    logger.info("KS test vs chi2(%s): stat=%.4f, p=%.4g", args.dof, ks_stat, p_value)

    if p_value > args.alpha:
        logger.info("PASS: cannot reject H0 at alpha=%s", args.alpha)
        return 0
    logger.warning("FAIL: p=%.4g <= alpha=%s; null distribution deviates", p_value, args.alpha)
    return 1


if __name__ == "__main__":
    sys.exit(main())
