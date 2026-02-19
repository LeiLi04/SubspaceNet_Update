# R32 (ICICSP 2025) Fig.3 RMSE vs Time (digitized, approximate)

Source: `docs/literature/fulltext/subscription/10.1109_icicsp66564.2025.11338321.pdf` (page 5, Fig.3)
Plot crop: `docs/literature/plan_strong_evidence_gapfix_2026-02-19/R32_fig3_graph_only.png`
Mask overlay: `docs/literature/plan_strong_evidence_gapfix_2026-02-19/R32_fig3_curve_masks_v2.png`

Caveats: values are approximate (figure digitization); use as supporting evidence, not exact claims.

| Method | Noise window 3600-4000s median RMSE (deg) | Noise window 3600-4000s p95 RMSE (deg) | RMSE at t=3900s (deg) |
|---|---:|---:|---:|
| EKF | 3.309 | 4.443 | 3.730 |
| SH-EKF | 1.965 | 3.078 | 0.767 |
| VB-EKF | 1.809 | 2.974 | 0.664 |
| FD-EKF | 1.026 | 1.365 | 0.905 |

Additional sampled time-slices (median within +/-30s):

| Method | t=1000s | t=2000s | t=3500s | t=3800s | t=3900s | t=4000s | t=4500s |
|---|---:|---:|---:|---:|---:|---:|---:|
| EKF | 0.664 | 0.741 | 0.578 | 1.678 | 3.730 | 4.557 | 2.556 |
| SH-EKF | 0.319 | 0.466 | 2.353 | 2.181 | 0.767 | 1.804 | 1.026 |
| VB-EKF | 0.293 | 0.552 | 0.931 | 2.379 | 0.664 | 1.596 | 1.452 |
| FD-EKF | 0.069 | 0.060 | 0.448 | 1.313 | 0.905 | 0.509 | 0.052 |
