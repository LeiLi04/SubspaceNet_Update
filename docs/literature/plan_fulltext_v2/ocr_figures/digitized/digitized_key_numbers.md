# Digitized Key Numbers (Approx)

## R45 (TWC 2021) Fig.7 RMSE vs SNR (digitized, approximate)
Source image: `/Users/lilei/PycharmProjects/SubspaceNet_Update/docs/literature/plan_fulltext_v2/ocr_figures/crops/R45_fig7_only.png`
Debug crop: `/Users/lilei/PycharmProjects/SubspaceNet_Update/docs/literature/plan_fulltext_v2/ocr_figures/digitized/R45_fig7_only_plot_bbox.png`

| SNR (dB) | RMSE best (deg) | RMSE worst (deg) | n curve pixels |
|---:|---:|---:|---:|
| -10 | 0.346 | 0.780 | 589 |
| 0 | 0.203 | 0.664 | 940 |
| 10 | 0.070 | 0.517 | 500 |

Notes: best/worst are taken as 90th/10th percentile y among colored (high-saturation) curve pixels at that SNR slice; intended to capture the spread across the 3 manifold cases and EKF/UKF lines. Use as approximate evidence only.
