# Findings: Theme B/C/D Evidence Upgrade

## Metadata
- Created At: `2026-02-19 16:23:00 UTC`
- Last Updated At: `2026-02-19 16:36:00 UTC`

## Numeric Evidence (Verified)

### R42 (ICSIP 2024) Table I: averaged running time (ms)
Source PDF: `docs/literature/fulltext/subscription/10.1109_icsip61881.2024.10671444.pdf` (page 4)
- 500 samples: WGMM 12.85 vs Hist-WGMM 2.01
- 1000: 24.48 vs 2.12
- 5000: 146.30 vs 5.76
- 10000: 277.10 vs 7.47
- 50000: 1245.10 vs 26.10
Notes: Hist-WGMM resolution 1 degree, max iterations 200. (use as real-time feasibility evidence) [@R42]

### R43 (EURASIP 2018) Table 2: time cost (s)
Source PDF: `docs/literature/fulltext/oa/10.1186_s13634-018-0541-0.pdf` (page 13, PyMuPDF block extraction)
- VSBL: 4.51
- VSBLKF (real): 21.23
- OGVSBLKF (real): 28.51
- VSBLKF (complex): 44.31
- OGVSBLKF (complex): 55.36 [@R43]

### R45 (TWC 2021) Fig.7 RMSE vs SNR (digitized, approximate)
Source crop: `docs/literature/plan_fulltext_v2/ocr_figures/crops/R45_fig7_only.png`
Debug: `docs/literature/plan_fulltext_v2/ocr_figures/digitized/R45_fig7_only_plot_bbox.png`
- SNR=-10 dB: RMSE best ~0.346 deg, worst ~0.780 deg
- SNR=0 dB: RMSE best ~0.203 deg, worst ~0.664 deg
- SNR=10 dB: RMSE best ~0.070 deg, worst ~0.517 deg
Notes: best/worst are percentile spread of curve pixels at each SNR slice; use as approximate evidence only. [@R45]

### R44 (ICC 2020) Fig.8 RMSE vs SNR (digitized, approximate)
Digitization note: `docs/literature/plan_theme_evidence_BCD_2026-02-19/R44_fig8_digitized_key_numbers.md`
Key points (approx RMSE, deg):
- SNR=0 dB: Case-1 ~0.297, Case-2 ~0.509, Case-3 ~1.245
- SNR=-10 dB: Case-1 ~0.453, Case-2 ~0.750, Case-3 ~2.844
- SNR=10 dB: Case-1 ~0.184, Case-2 ~0.325, Case-3 ~0.665
Use: supports “manifold extender” / observation-space augmentation improves robustness, but label as digitized approximate. [@R44]

## Numeric Evidence (Theme B/C)

### R03 (SDOA-Net) key statement (imperfect array)
From extracted text `docs/literature/plan_theme_evidence_BCD_2026-02-19/arxiv_text/arxiv_2203.10231.txt`:
- At SNR=10 dB: SDOA-Net RMSE ~0.70 deg vs ANM ~1.15 deg (about 39.13% RMSE improvement).
- SNR “gain” claim: SDOA-Net at 7.5 dB matches ANM at 15 dB (about 7.5 dB improvement). [@R03]

### R08 (SubspaceNet) Table I: coherent sources RMSPE (deg)
From extracted text `docs/literature/plan_theme_evidence_BCD_2026-02-19/arxiv_text/arxiv_2306.02271.txt` (Table I):
- M=2 coherent sources: Root-MUSIC 12.4790 vs SubspaceNet+Root-MUSIC 0.2005
- M=3: Root-MUSIC 20.3972 vs SubspaceNet+Root-MUSIC 0.7219
- M=4: Root-MUSIC 23.2047 vs SubspaceNet+Root-MUSIC 3.8846 [@R08]
