"""Sandbox helpers for changepoint detection experiments."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def glrt_changepoint_detection(losses, min_segment_size=5):
    """Detect a changepoint with a Gaussian GLRT objective."""
    losses = np.array(losses)
    n = len(losses)

    mu_0 = np.mean(losses)
    sigma_0 = np.std(losses, ddof=1)

    log_L0 = -n / 2 * np.log(2 * np.pi) - n / 2 * np.log(sigma_0**2) - np.sum((losses - mu_0) ** 2) / (2 * sigma_0**2)

    all_log_glr = np.zeros(n - 2 * min_segment_size)
    candidate_points = range(min_segment_size, n - min_segment_size)

    for i, tau in enumerate(candidate_points):
        segment1 = losses[:tau]
        segment2 = losses[tau:]

        n1, n2 = len(segment1), len(segment2)
        mu1, mu2 = np.mean(segment1), np.mean(segment2)
        sigma1 = max(np.std(segment1, ddof=1), 1e-10)
        sigma2 = max(np.std(segment2, ddof=1), 1e-10)

        log_L1_seg1 = -n1 / 2 * np.log(2 * np.pi) - n1 / 2 * np.log(sigma1**2) - np.sum((segment1 - mu1) ** 2) / (2 * sigma1**2)
        log_L1_seg2 = -n2 / 2 * np.log(2 * np.pi) - n2 / 2 * np.log(sigma2**2) - np.sum((segment2 - mu2) ** 2) / (2 * sigma2**2)
        log_L1 = log_L1_seg1 + log_L1_seg2

        all_log_glr[i] = log_L1 - log_L0

    max_idx = np.argmax(all_log_glr)
    changepoint = candidate_points[max_idx]
    max_log_glr = all_log_glr[max_idx]

    return changepoint, max_log_glr, all_log_glr, candidate_points


def plot_results(losses, changepoint, all_log_glr, candidate_points):
    """Visualize losses and GLRT statistics."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    ax1.plot(losses, "b-", linewidth=1.5, label="RMSPE Loss")
    ax1.axvline(x=changepoint, color="r", linestyle="--", linewidth=2, label=f"Detected Change Point (t={changepoint})")
    ax1.set_xlabel("Time Window", fontsize=12)
    ax1.set_ylabel("RMSPE Loss", fontsize=12)
    ax1.set_title("Model Loss Over Time with Detected Change Point", fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(candidate_points, all_log_glr, "g-", linewidth=1.5)
    ax2.axvline(x=changepoint, color="r", linestyle="--", linewidth=2, label=f"Maximum log-GLR (t={changepoint})")
    ax2.set_xlabel("Candidate Change Point", fontsize=12)
    ax2.set_ylabel("Log Generalized Likelihood Ratio", fontsize=12)
    ax2.set_title("GLRT Statistics Across All Candidate Change Points", fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def _demo() -> None:
    losses = [
        np.float64(0.004931669023353607),
        np.float64(0.007578440988436341),
        np.float64(0.012997683663852512),
        np.float64(0.00808196676429361),
        np.float64(0.0037428371026180683),
        np.float64(0.0036191873881034555),
        np.float64(0.0068395142117515205),
        np.float64(0.005118306514341384),
        np.float64(0.004571315133944154),
        np.float64(0.008349625742994249),
        np.float64(0.005849287793971598),
        np.float64(0.003415681341430172),
        np.float64(0.0038480300654191524),
        np.float64(0.0037694890226703135),
        np.float64(0.005921079907566309),
        np.float64(0.008513692754786462),
        np.float64(0.006546487710438669),
        np.float64(0.004433163041248918),
        np.float64(0.0064321842044591905),
        np.float64(0.0048534156614914534),
        np.float64(0.00431691390927881),
        np.float64(0.1368792290240526),
        np.float64(0.20899184323847295),
        np.float64(0.21095313012599945),
        np.float64(0.21011458970606328),
        np.float64(0.21278823256492616),
        np.float64(0.2093567244708538),
        np.float64(0.2244790482521057),
        np.float64(0.17682151876389982),
        np.float64(0.1454287474602461),
        np.float64(0.2027802936732769),
        np.float64(0.2186738930642605),
        np.float64(0.21005682542920112),
        np.float64(0.18476634681224824),
        np.float64(0.21587180890142918),
        np.float64(0.22898483499884606),
        np.float64(0.18468307211995125),
        np.float64(0.18271939642727375),
        np.float64(0.1825578884780407),
        np.float64(0.2150580244511366),
        np.float64(0.23237869411706924),
        np.float64(0.17873112492263318),
        np.float64(0.18701113909482955),
        np.float64(0.216712242141366),
        np.float64(0.2319300489127636),
        np.float64(0.1864546513557434),
        np.float64(0.15158024199306966),
        np.float64(0.22755918517708779),
        np.float64(0.212598287910223),
        np.float64(0.18568192034959793),
        np.float64(0.19146738044917583),
        np.float64(0.2041339661180973),
        np.float64(0.22155723571777344),
        np.float64(0.2082066160440445),
        np.float64(0.15259424425661564),
        np.float64(0.19504203505814074),
        np.float64(0.21823965817689894),
        np.float64(0.2262695948779583),
        np.float64(0.17920041956007482),
    ]

    changepoint, max_log_glr, all_log_glr, candidate_points = glrt_changepoint_detection(losses, min_segment_size=5)

    print(f"Detected Change Point: Window {changepoint}")
    print(f"Maximum Log-GLR: {max_log_glr:.4f}")

    fig = plot_results(losses, changepoint, all_log_glr, candidate_points)
    out_dir = Path("outputs/figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "glrt_demo.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved visualization to {out_path}")


if __name__ == "__main__":
    _demo()
