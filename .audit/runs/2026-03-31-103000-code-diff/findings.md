# Ensemble Code Audit — Steps 6–8 — 2026-03-31

**Scope:** Steps 6 (loss function), 7 (training loop), 8 (evaluation + plotting).
**Passes:** 5 parallel passes — physics, rubric C/D, ML hygiene, teaching mode, experiment tracking.
**Notebook:** `assignment3.ipynb`

---

## Executive Summary

- **Top risk (C1, 5/5):** Y-axis label on every saved loss-curve plot reads "Kaggle loss (RMSRE)". The loss is MARE (Mean Absolute Relative Error). Label will propagate into report figures causing a terminology contradiction with the formula derived in the same cell.
- **Top risk (C2, 4/5):** `x_batch` / `y_batch` / `x_val` / `y_val` are never moved to `device` inside `train_model()`. On any GPU machine the first `model(x_batch)` call will crash with a device-mismatch error.
- **Physics gap (C3, 2/5):** Training call passes `train_loader` (1200 samples, no augmentation) instead of `train_loader_aug` (4800 samples). The entire augmentation infrastructure from Step 4 is discarded.
- **Experiment tracking (C4, 3/5):** `plot_predictions()` generates its own timestamp internally, disconnecting the prediction plot filename from the `run_id` used for the checkpoint and loss JSON.
- **Rubric D gap (C5, 2/5):** `num_params()` is defined in Step 5 but never called on the trained model. The low-complexity bonus (≤120,000 params) cannot be substantiated in the report.
- **ML hygiene (C6, 2/5):** `check_nonphysical()` builds the computation graph on every batch — missing `torch.no_grad()`.
- **PyTorch compatibility (C7, 2/5):** `torch.load` missing `weights_only=True` — emits FutureWarning, breaks on PyTorch ≥ 2.6.

---

## Merged Findings Table

| ID | Severity | Category | Finding | Consensus |
|----|----------|----------|---------|-----------|
| C1 | HIGH | Plot label | Y-axis label "Kaggle loss (RMSRE)" — loss is MARE not RMSRE; propagates to saved plots and report | 5/5 |
| C2 | HIGH | Device handling | `x_batch`, `y_batch`, `x_val`, `y_val` never moved to `device` inside `train_model()` — crashes on GPU | 4/5 |
| C3 | HIGH | Physics | Training call uses `train_loader` not `train_loader_aug` — discards all augmentation from Step 4 | 2/5 |
| C4 | MEDIUM | Experiment tracking | `plot_predictions()` uses own timestamp; disconnected from `run_id` of checkpoint/log | 3/5 |
| C5 | MEDIUM | Rubric D | `num_params()` never called on `model_cnn` — rubric D bonus unsubstantiated | 2/5 |
| C6 | LOW | ML hygiene | `check_nonphysical()` missing `torch.no_grad()` — builds computation graph on every batch | 2/5 |
| C7 | LOW | Compatibility | `torch.load` missing `weights_only=True` — FutureWarning / breaks on PyTorch ≥ 2.6 | 2/5 |

---

## Rubric Coverage

| Section | Sub-point | Status |
|---------|-----------|--------|
| C.1 | Working CNN | PRESENT |
| C.3 | Train + val loss curves with axis labels | PRESENT but mislabelled (C1) |
| C.3 | Overfitting commentary | PRESENT (deferred to step 9) |
| C.3 | Anti-overfitting strategy shown working | DEFERRED to step 9 |
| C.4 | Symmetry comparison | DEFERRED to step 10 |
| C.5 | Parameter efficiency + U-Net | DEFERRED to step 11 |
| D | num_params() evidenced | MISSING (C5) |
| D | Kaggle submission | DEFERRED to step 13 |
| B.7 | Non-physical outputs identified | PRESENT — check_nonphysical() |

---

## Recommended Next Steps

### Must-fix
1. **C1** — Fix y-axis label: `"Kaggle loss (RMSRE)"` → `"Kaggle loss E (MARE)"`
2. **C2** — Add `.to(device)` on `x_batch`, `y_batch` in train loop; `x_val`, `y_val` in val loop
3. **C3** — Switch training call from `train_loader` → `train_loader_aug`

### Should-fix
4. **C4** — Add `run_id` parameter to `plot_predictions()`; pass `run_id_cnn` at call site
5. **C5** — Call `num_params(model_cnn)` after training, save to log
6. **C6** — Wrap `model(x_batch)` in `check_nonphysical()` with `torch.no_grad()`
7. **C7** — Add `weights_only=True` to `torch.load()`
