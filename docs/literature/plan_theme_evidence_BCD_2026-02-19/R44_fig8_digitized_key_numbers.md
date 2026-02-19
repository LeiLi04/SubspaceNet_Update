## R44 (ICC 2020) Fig.8 RMSE vs SNR (digitized, approximate)
Source: `docs/literature/plan_fulltext_v2/ocr_figures/R44_fig8_rmse.png`
Digitization workspace: `docs/literature/plan_theme_evidence_BCD_2026-02-19/`

Method:
- Cropped plot region -> color-threshold curve pixels (red/green/blue).
- Linear x mapping: assume plot x-range covers SNR -10..20 dB.
- Linear y mapping: detect a prominent horizontal gridline near y=3 (top) and use bottom axis as y=0.

Caveats:
- Values are approximate (figure digitization). Use only as supporting evidence, not as primary claims.

Approx RMSE (deg):

| SNR (dB) | Case-1 (blue) | Case-2 (green) | Case-3 (red) |
|---:|---:|---:|---:|
| -10 | 0.453 | 0.750 | 2.844 |
| -5 | 0.368 | 0.623 | 1.910 |
| 0 | 0.297 | 0.509 | 1.245 |
| 5 | 0.226 | 0.396 | 0.821 |
| 10 | 0.184 | 0.325 | 0.665 |
| 15 | 0.142 | 0.255 | 0.538 |
| 20 | 0.042 | 0.042 | 0.453 |

Debug artifacts:
- Plot-only crop: `docs/literature/plan_theme_evidence_BCD_2026-02-19/R44_fig8_plot_only.png`
- Auto bbox: `docs/literature/plan_theme_evidence_BCD_2026-02-19/R44_fig8_plot_bbox_auto.png`
- Inner plot: `docs/literature/plan_theme_evidence_BCD_2026-02-19/R44_fig8_plot_inner.png`
- Curve masks overlay: `docs/literature/plan_theme_evidence_BCD_2026-02-19/R44_fig8_inner_curve_masks.png`
