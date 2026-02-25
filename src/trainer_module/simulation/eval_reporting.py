"""Evaluation reporting helpers for trajectory metrics and comparisons."""

from __future__ import annotations

from typing import Any, Dict, List
import logging

import numpy as np

logger = logging.getLogger(__name__)


def log_evaluation_results(
    simulation: Any,
    dnn_total_loss: float,
    ekf_total_loss: float,
    dnn_total_samples: int,
    classic_methods_losses: Dict[str, Dict[str, float]],
    dnn_trajectory_results: List[Dict[str, Any]],
    classic_trajectory_results: List[Dict[str, Any]] | None,
) -> None:
    """Aggregate, persist, and print evaluation metrics."""
    dnn_avg_loss = dnn_total_loss / max(dnn_total_samples, 1)
    ekf_avg_loss = ekf_total_loss / max(dnn_total_samples, 1)
    dnn_avg_loss_in_degrees = dnn_avg_loss * 180 / np.pi
    ekf_avg_loss_in_degrees = ekf_avg_loss * 180 / np.pi

    logger.info(
        "DNN Model - Average loss: %.6f in degrees: %.6f",
        dnn_avg_loss,
        dnn_avg_loss_in_degrees,
    )
    logger.info(
        "EKF Model - Average loss: %.6f in degrees: %.6f",
        ekf_avg_loss,
        ekf_avg_loss_in_degrees,
    )

    classic_methods_avg_losses: Dict[str, float] = {}
    classic_methods_avg_losses_in_degrees: Dict[str, float] = {}
    for method, loss_data in classic_methods_losses.items():
        if loss_data["total_samples"] > 0:
            avg_loss = loss_data["total_loss"] / loss_data["total_samples"]
            classic_methods_avg_losses[method] = avg_loss
            classic_methods_avg_losses_in_degrees[method] = avg_loss * 180 / np.pi
            logger.info(
                "Classic Method %s - Average loss: %.6f in degrees: %.6f",
                method,
                avg_loss,
                classic_methods_avg_losses_in_degrees[method],
            )

    simulation.results["dnn_test_loss"] = dnn_avg_loss
    simulation.results["ekf_test_loss"] = ekf_avg_loss
    simulation.results["classic_methods_test_losses"] = classic_methods_avg_losses

    dnn_ekf_diff = dnn_avg_loss - ekf_avg_loss
    dnn_ekf_relative_diff = dnn_ekf_diff / ekf_avg_loss * 100 if ekf_avg_loss != 0 else float("inf")

    logger.info("DNN vs EKF Comparison:")
    if dnn_ekf_diff < 0:
        logger.info(
            "DNN outperforms EKF by %.6f (%.2f%%) in degrees: %.6f",
            abs(dnn_ekf_diff),
            abs(dnn_ekf_relative_diff),
            abs(dnn_ekf_diff * 180 / np.pi),
        )
    else:
        logger.info(
            "EKF outperforms DNN by %.6f (%.2f%%) in degrees: %.6f",
            dnn_ekf_diff,
            dnn_ekf_relative_diff,
            dnn_ekf_diff * 180 / np.pi,
        )

    if classic_methods_avg_losses:
        logger.info("DNN vs Classic Methods Comparison:")
        for method, avg_loss in classic_methods_avg_losses.items():
            diff = dnn_avg_loss - avg_loss
            relative_diff = diff / avg_loss * 100 if avg_loss != 0 else float("inf")
            if diff < 0:
                logger.info(
                    "DNN outperforms %s by %.6f (%.2f%%) in degrees: %.6f",
                    method,
                    abs(diff),
                    abs(relative_diff),
                    abs(diff * 180 / np.pi),
                )
            else:
                logger.info(
                    "%s outperforms DNN by %.6f (%.2f%%) in degrees: %.6f",
                    method,
                    diff,
                    relative_diff,
                    diff * 180 / np.pi,
                )

        logger.info("EKF vs Classic Methods Comparison:")
        for method, avg_loss in classic_methods_avg_losses.items():
            diff = ekf_avg_loss - avg_loss
            relative_diff = diff / avg_loss * 100 if avg_loss != 0 else float("inf")
            if diff < 0:
                logger.info(
                    "EKF outperforms %s by %.6f (%.2f%%) in degrees: %.6f",
                    method,
                    abs(diff),
                    abs(relative_diff),
                    abs(diff * 180 / np.pi),
                )
            else:
                logger.info(
                    "%s outperforms EKF by %.6f (%.2f%%) in degrees: %.6f",
                    method,
                    diff,
                    relative_diff,
                    diff * 180 / np.pi,
                )

    logger.info("Evaluated %d trajectories with DNN model", len(dnn_trajectory_results))
    if classic_trajectory_results:
        logger.info(
            "Evaluated %d trajectories with classic methods",
            len(classic_trajectory_results),
        )

    print("\n" + "=" * 80)
    print(f"{'EVALUATION RESULTS':^80}")
    print("=" * 80)

    print(f"\n{'DNN AND EKF MODELS WITH KALMAN FILTER':^100}")
    print("-" * 100)
    print(f"{'Method':<20} {'Average Loss':<20} {'Average Loss (degrees)':<25} {'Additional Info':<30}")
    print("-" * 100)
    dnn_avg_loss_degrees = dnn_avg_loss * 180 / np.pi
    ekf_avg_loss_degrees = ekf_avg_loss * 180 / np.pi
    additional_info = f"Samples: {dnn_total_samples}, Traj: {len(dnn_trajectory_results)}"
    print(f"{'DNN+Kalman':<20} {dnn_avg_loss:<20.6f} {dnn_avg_loss_degrees:<25.6f} {additional_info:<30}")
    print(f"{'EKF':<20} {ekf_avg_loss:<20.6f} {ekf_avg_loss_degrees:<25.6f} {additional_info:<30}")

    dnn_ekf_diff_degrees = dnn_ekf_diff * 180 / np.pi
    if dnn_ekf_diff < 0:
        comparison_text = f"DNN better by {abs(dnn_ekf_diff_degrees):.6f} deg ({abs(dnn_ekf_relative_diff):.2f}%)"
    else:
        comparison_text = f"EKF better by {dnn_ekf_diff_degrees:.6f} deg ({dnn_ekf_relative_diff:.2f}%)"
    print(f"{'DNN vs EKF':<20} {'Comparison':<20} {comparison_text:<25} {'Performance Gap':<30}")

    if classic_methods_avg_losses:
        print(f"\n{'CLASSIC SUBSPACE METHODS':^100}")
        print("-" * 100)
        print(f"{'Method':<20} {'Average Loss':<20} {'Average Loss (degrees)':<25} {'Comparison with DNN':<30}")
        print("-" * 100)

        for method, avg_loss in classic_methods_avg_losses.items():
            diff = dnn_avg_loss - avg_loss
            relative_diff = diff / avg_loss * 100 if avg_loss != 0 else float("inf")
            avg_loss_degrees = avg_loss * (180.0 / np.pi)

            if diff < 0:
                comparison = f"DNN better by {abs(diff):.6f} ({abs(relative_diff):.2f}%)"
            elif diff > 0:
                comparison = f"DNN worse by {diff:.6f} ({relative_diff:.2f}%)"
            else:
                comparison = "Equal performance"

            print(f"{method:<20} {avg_loss:<20.6f} {avg_loss_degrees:<25.6f} {comparison:<30}")

    print("\n" + "=" * 80)
