"""Validate c_i = y^T S^-1 y against the chi-square null distribution.

Usage:
    python scripts/validate_null_distribution.py --input outputs/null_validation.npz
    python scripts/validate_null_distribution.py --input outputs/null_validation.npz --decimate 5
    python scripts/validate_null_distribution.py --input outputs/null_validation.npz --per-source
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
    with np.load(path) as data:
        for key in ("c", "c_values", "c_per_step"):
            if key in data:
                return np.asarray(data[key], dtype=np.float64)
    raise ValueError(f"{path} must contain one of: c, c_values, c_per_step")


def _load_per_source_values(path: Path) -> np.ndarray:
    with np.load(path) as data:
        for key in ("c_per_step_per_source", "c_per_source", "per_source"):
            if key in data:
                values = np.asarray(data[key], dtype=np.float64)
                if values.ndim != 2:
                    raise ValueError(f"{key} in {path} must be a 2D array [steps, sources]")
                return values
    raise ValueError(
        f"{path} must contain c_per_step_per_source for --per-source validation. "
        "Regenerate the dump with the updated pipeline hook."
    )


def _decimate(values: np.ndarray, stride: int) -> np.ndarray:
    if stride < 1:
        raise ValueError("--decimate must be >= 1")
    if stride == 1:
        return values
    return values[::stride]


def _validate_1d(values: np.ndarray, dof: int, alpha: float, label: str) -> bool:
    if values.size == 0:
        raise ValueError(f"No c-values available for {label}")
    ks_stat, p_value = stats.kstest(values, "chi2", args=(dof,))
    logger.info(
        "%s: N=%s samples, mean=%.3f (theoretical %s)",
        label,
        len(values),
        values.mean(),
        dof,
    )
    logger.info("%s: KS test vs chi2(%s): stat=%.4f, p=%.4g", label, dof, ks_stat, p_value)
    if p_value > alpha:
        logger.info("%s: PASS: cannot reject H0 at alpha=%s", label, alpha)
        return True
    logger.warning("%s: FAIL: p=%.4g <= alpha=%s; null distribution deviates", label, p_value, alpha)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None, help="Pipeline-generated npz file with real c values.")
    parser.add_argument("--dof", type=int, default=3)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--samples", type=int, default=300)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--synthetic-null", action="store_true", help="Generate synthetic chi-square samples for script smoke only.")
    parser.add_argument("--per-source", action="store_true", help="Validate per-source c values against chi2(1).")
    parser.add_argument("--decimate", type=int, default=1, help="Keep every Nth sample before KS testing; use for overlapping-window dumps.")
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
        if args.per_source:
            c_values = rng.chisquare(df=1, size=(args.samples, args.dof)).astype(np.float64)
            logger.info("Generated synthetic per-source chi-square null samples for script smoke only.")
        else:
            c_values = rng.chisquare(df=args.dof, size=args.samples).astype(np.float64)
            logger.info("Generated synthetic chi-square null samples for script smoke only.")
    else:
        if args.per_source:
            c_values = _load_per_source_values(args.input)
            logger.info("Loaded per-source c-values with shape %s from %s", c_values.shape, args.input)
        else:
            c_values = _load_values(args.input)
            logger.info("Loaded %s c-values from %s", len(c_values), args.input)

    c_values = _decimate(c_values, args.decimate)
    if args.decimate > 1:
        logger.info("Applied decimation: kept every %sth sample; new shape=%s", args.decimate, c_values.shape)

    if c_values.size == 0:
        raise ValueError("No c-values available for validation")

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        if args.per_source:
            np.savez(args.out, c_per_step_per_source=c_values, dof=1)
        else:
            np.savez(args.out, c=c_values, dof=args.dof)

    if args.per_source:
        passed = True
        for source_idx in range(c_values.shape[1]):
            passed &= _validate_1d(
                c_values[:, source_idx],
                dof=1,
                alpha=args.alpha,
                label=f"source[{source_idx}]",
            )
        return 0 if passed else 1

    return 0 if _validate_1d(c_values, dof=args.dof, alpha=args.alpha, label="total") else 1


if __name__ == "__main__":
    sys.exit(main())
