# Findings: Repo Positioning Notes (SubspaceNet_Update)

## Metadata
- Created At: `2026-02-19 16:37:00 UTC`
- Last Updated At: `2026-02-19 16:37:00 UTC`

## Repo-Specific Signals (for Discussion)
- The codebase implements trajectory-level evaluation with **DNN predictions + (Batch) Kalman filter / EKF** post-processing (`src/eval/evaluation.py`).
- Online adaptation exists as a **windowed online learning** loop with configurable triggers and loss types (`src/train/online_learning.py`, `config/schema.py`).
- Unsupervised objectives include variants of **innovation-consistency** style losses (e.g., `kalman_innovation`, `y_s_inv_y`, and a “multimoment” blend of RMSPE+RMAPE) configured under `OnlineLearningLossConfig` (`config/schema.py`, `src/eval/metrics/multimoment_innovation_consistency_loss.py`).
- The simulation pipeline supports a drift/control parameter `eta` that affects array/signal generation and can be updated over windows (`src/data/trajectory.py`).

