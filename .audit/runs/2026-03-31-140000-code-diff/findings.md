# Ensemble Code Audit — Steps 6–9
**Run ID:** 2026-03-31-140000-code-diff
**Scope:** Steps 6–9 (loss function, training loop, evaluation/plotting, overfitting prevention)
**Passes:** 5 (Physics, Rubric C/D, ML Hygiene, Teaching Mode, Experiment Tracking)

---

## Executive Summary

**Top risks:**
- **Step 9 is entirely absent** — no markdown explanation cell, no code cell, only forward references from earlier steps. This is the single most impactful gap, found by all 5 passes at CRITICAL/HIGH severity. Rubric C.3 ("showcase effectiveness of at least one measure") cannot be satisfied.
- **No anti-overfitting effectiveness plot** — `weight_decay=1e-4` and early stopping (`patience=10`) are silently embedded inside `train_model()` but are never demonstrated comparatively (with vs without). A rubric-required comparison plot is missing.
- **Softplus non-negativity enforcement promised but absent** — Cell 21 explicitly promises "A Softplus output activation to hard-enforce non-negativity is added in Step 9." This is unfulfilled, leaving negative flow predictions possible at open pixels.
- **Magic numbers unexplained** — `weight_decay=1e-4`, `patience=10`, and an `lr` discrepancy (markdown says 1e-3, code uses 1e-4) have no prose motivation in any teaching cell.
- **Orphaned prediction plot** — `cnn_baseline_20260331_122852_predictions.png` has a timestamp that matches no log or checkpoint file (latest run is `122819`), indicating it was generated in a separate kernel session.
- **`or True` dead code** — early-stopping print condition is always true, a leftover debug artifact.
- **ε justification conflates SI and normalised label scales** — minor documentation inconsistency.

**Consistently found (strong consensus ≥ 4/5):** C1 (Step 9 absent), C2 (no effectiveness plot), C4 (magic numbers).
**Majority findings (3/5):** C3 (Softplus absent), C5 (or True dead code).
**Singleton findings (1–2/5):** C6 (lr discrepancy), C7 (orphaned plot), C8 (ε scale conflation).

**Parameter count:** MaskedCNN confirmed at **18,593 parameters** — well within 120,000 bonus threshold. Bonus is achievable.

---

## Merged Findings Table

| ID | Severity | Consensus | Category | Finding |
|----|----------|-----------|----------|---------|
| C1 | CRITICAL | 5/5 | Step 9 absent | Step 9 (overfitting prevention) does not exist in the notebook. The notebook ends at cell 34 (step 8.3) with a forward reference: "Step 9 will address this." No Step 9 markdown cell and no Step 9 code cell exist. Rubric C.3 requires implementing and demonstrating effectiveness of at least one anti-overfitting strategy. |
| C2 | HIGH | 4/5 | No effectiveness demonstration | Even though `weight_decay=1e-4` and `patience=10` are present inside `train_model()`, there is no comparison plot showing training dynamics with vs without these strategies. Rubric C.3 explicitly requires "showcase effectiveness." A single loss curve with no comparative baseline does not satisfy this. |
| C3 | HIGH | 3/5 | Non-physical outputs | `MaskedCNN` correctly zeroes closed pixels (confirmed). However at open pixels the backbone uses no activation preventing **negative** predictions. Cell 21 promises "A Softplus output activation to hard-enforce non-negativity is added in Step 9." Step 9 does not exist, so negative flow values remain possible post-training. |
| C4 | MEDIUM | 4/5 | Magic numbers unexplained | Three values have no prose explanation in any teaching cell: (a) `weight_decay=1e-4` — what L2 regularisation does and why this value; (b) `patience=10` — what early stopping is and why 10 epochs; (c) `lr=1e-4` in the actual call vs `lr=1e-3` stated in the Step 7 markdown — a factual discrepancy that misleads readers. |
| C5 | LOW | 3/5 | Dead code | `if (epoch + 1) % max(1, epochs // 10) == 0 or True:` inside the early-stopping branch — the `or True` makes the condition always true. Every early-stop epoch is printed regardless of the frequency gate. This is leftover debug code. |
| C6 | MEDIUM | 1/5 (singleton) | lr discrepancy | The Step 7 markdown (cell 24) states "We use `lr=1e-3` as the starting learning rate." The actual `train_model()` call uses `lr=1e-4`. This is a specific factual error in the teaching cell, not merely an omission. Needs confirmation but high teaching-mode impact. |
| C7 | MEDIUM | 1/5 (singleton) | Orphaned experiment artifact | `cnn_baseline_20260331_122852_predictions.png` has a timestamp that does not match any JSON log or checkpoint (latest training run is `122819`). The plot was generated in a separate kernel session, breaking the experiment tracking linkage. |
| C8 | LOW | 1/5 (singleton) | ε documentation | The comment justifying `EPSILON = 1e-6` references SI-unit q values ("SI min ~1e-4 >> 1e-6") but the model is trained on normalised `q/v0` labels (O(1)). The reasoning is internally inconsistent — the correct comparison should be against `min(q/v0)`, not SI q. Functionally harmless but misleading. |
| C9 | INFO | 2/5 | Loss formula correct | `kaggle_loss()` implements `mean(|pred-truth| / (truth + eps))` — exactly matching the assignment formula with ε in the ground truth denominator. Three sanity checks confirm correctness. No defect. |
| C10 | INFO | 5/5 | ML hygiene confirmed | Seeds (`torch.manual_seed`, `np.random.seed`, CUDA seeds), device handling, `model.train()`/`model.eval()`, `optimizer.zero_grad()`, `torch.no_grad()` in validation, best-checkpoint saving and reload — all correct and fully compliant. |
| C11 | INFO | 5/5 | Experiment tracking confirmed | All three artifact types (JSON log, loss plot, checkpoint) saved with `{model_name}_{YYYYMMDD_HHMMSS}` naming. Three complete run triplets confirmed on disk. `os.makedirs(..., exist_ok=True)` guards present. |
| C12 | INFO | 5/5 | Parameter count | MaskedCNN: 18,593 total parameters. Well within 120,000 bonus threshold. `num_params()` correctly adapted from helper with `return total` added. |

---

## Rubric Coverage (Steps 6–9)

| Section | Sub-point | Status |
|---------|-----------|--------|
| Step 6 | Kaggle loss E implemented with ε | PASS |
| Step 6 | ε prevents division by zero | PASS |
| Step 6 | Source attribution from lab7 rmsre() | PASS |
| Step 7 | Training loop has model.train() / model.eval() | PASS |
| Step 7 | Both train AND validation loss tracked per epoch | PASS |
| Step 7 | optimizer.zero_grad() before backward() | PASS |
| Step 7 | Checkpoint saved to experiments/checkpoints/ (best val) | PASS |
| Step 7 | JSON log saved to experiments/logs/ | PASS |
| Step 7 | Loss plot saved to experiments/plots/ | PASS |
| Step 7 | Run naming convention {model_name}_{YYYYMMDD_HHMMSS} | PASS |
| Step 7 | Source attribution from lab6 train_model() | PASS |
| Step 7 | weight_decay explained in teaching cell | FAIL |
| Step 7 | patience / early stopping explained in teaching cell | FAIL |
| Step 7 | lr value consistent between markdown and code | FAIL |
| Step 8 | Loss curves with axis labels saved to experiments/plots/ | PASS |
| Step 8 | Prediction visualisations with eval+no_grad | PASS |
| Step 8 | Non-physical output check (check_nonphysical) | PASS |
| Step 8 | Prediction plot run_id matches training run | FAIL (orphaned) |
| Step 9 | Dedicated section with markdown explanation | FAIL |
| Step 9 | At least one anti-overfitting strategy implemented | PARTIAL (in train_model(), not labelled) |
| Step 9 | Effectiveness demonstrated with comparison plot | FAIL |
| Rubric C.3 | "Showcase effectiveness of at least one measure" | FAIL |

---

## Recommended Next Steps

### Must-fix (grade impact — rubric C.3 is required for Good/Excellent band)

1. **Implement Step 9** — Add a dedicated Step 9 section with:
   - A markdown cell explaining the anti-overfitting strategy (weight decay, early stopping, or dropout) in plain language with rubric C.3 reference
   - A comparative experiment: train once without the strategy, once with it, plot both loss curves together
   - Add Softplus output activation to enforce non-negativity at open pixels (promised in cell 21)

2. **Fix lr discrepancy** — Update the Step 7 markdown to state `lr=1e-4` (matching the actual call), or change the call to `lr=1e-3` and document the choice.

3. **Explain magic numbers** — Add 1-2 sentences each in Step 7 markdown explaining `weight_decay=1e-4` (L2 regularisation, prevents large weights), `patience=10` (early stopping, avoids overfit after plateau).

### Should-fix (quality/reproducibility)

4. **Remove `or True`** — Delete the dead `or True` from the early-stopping print condition.

5. **Fix orphaned prediction plot** — Regenerate the prediction plot in the same kernel session as training (pass `run_id_cnn` correctly), or rename the file to match the training run timestamp.

6. **Add `run_id` to `cnn_baseline_params.json`** — Include `"run_id": run_id_cnn` so the parameter log is traceable to its checkpoint.

7. **Fix ε justification comment** — Reference `min(q/v0)` (normalised scale) instead of SI `q` min.

---

## Rating

- **Score: 3/5**
- **Stars:** ⭐⭐⭐

**Rating scale:**
| Score | Meaning |
|-------|---------|
| 5/5 | All steps complete, no significant gaps |
| 4/5 | All steps present, minor issues only |
| 3/5 | Core steps solid but one required step missing/incomplete |
| 2/5 | Multiple required steps missing or critically flawed |
| 1/5 | Notebook largely incomplete |

**Justification:** All 5 passes confirmed that Steps 6, 7, and 8 are correctly implemented with strong ML hygiene (seeds, device, train/eval modes, gradient zeroing, best-checkpoint saving), correct Kaggle loss formula, proper experiment tracking, and all artifacts saved with the correct naming convention. The score is held at 3/5 — not higher — because Step 9 is entirely absent across all 5 audit passes (unanimous CRITICAL/HIGH finding). Rubric C.3 ("showcase effectiveness of at least one measure") is a required sub-point for the Good grade band and cannot be satisfied by the current notebook. Passes 2 and 4 scored 2/5; passes 1, 3, and 5 scored 3/5 — majority 3/5 adopted, tempered by the unanimous CRITICAL gap.

---

## Commit Message

`feat(notebook): add step 9 — anti-overfitting strategy with comparative plot; fix lr discrepancy, explain weight_decay/patience, add Softplus output activation`
