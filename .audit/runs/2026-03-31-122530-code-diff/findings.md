# Ensemble Code Audit — Steps 7–10
**Run ID:** 2026-03-31-122530-code-diff
**Passes:** 5 (physics correctness, rubric C/D compliance, ML hygiene, teaching mode, experiment tracking)
**Scope:** steps 7–10

---

## Executive Summary

**Top risks:**
- **CRITICAL:** The notebook was never executed end-to-end. Cells 27, 36–42 (num_params, step 9 training, all of step 10) have empty outputs. No GroupAvgModel checkpoint, log, or comparison plot exists on disk.
- **HIGH:** Step 10 symmetry comparison uses Kaggle MARE (E) as the only metric — rubric C.4 requires "the metrics to evaluate the respect of symmetries proposed previously" (equivariance-error, not MARE).
- **HIGH:** Stale hyperparameter values in markdown cells: Step 7 states lr=1e-4/epochs=50/patience=10 but code uses lr=1e-3/epochs=150/patience=20; Step 9.3 markdown states patience=10/epochs=50 but code uses patience=20/epochs=150. Cell 36 hardcodes "max configured: 50" but baseline used epochs=30.
- **HIGH:** Step 10 markdown claims "→ Satisfies rubric B.3" — the correct criterion is C.4. Graders scanning for C.4 will not find it annotated.
- **MEDIUM:** No `torch.manual_seed(SEED)` before `model_cnn` construction (step 7); steps 9 and 10 correctly re-seed but baseline does not.
- **MEDIUM:** Comparison plots (step 9.3, step 10) use hardcoded filenames deviating from the `{model_name}_{YYYYMMDD_HHMMSS}` run_id convention.
- **MEDIUM:** GroupAvgModel vs plain-CNN comparison is not a clean ablation — the baseline is `MaskedCNNSoftplus` (with Softplus + L2), so two variables differ simultaneously.

**Consistently found (≥3/5 passes):** C1 (unexecuted cells), C2 (wrong metric for C.4), C3 (stale markdown hyperparameters), C4 (wrong rubric reference), C6 (hardcoded plot filenames).

**Singleton / needs confirmation:** C12 (stale `cnn_baseline_params.json` file).

**Parameter count status:** `num_params(model_cnn)` is coded in cell 27 but was never executed — no evidence of ≤120,000 in the current notebook state.

---

## Merged Findings Table

| ID | Severity | Category | Finding | Consensus |
|----|----------|----------|---------|-----------|
| C1 | CRITICAL | Notebook execution | Cells 27, 36–42 (num_params, step 9 training, step 10 GroupAvgModel) all have empty outputs — notebook was never executed end-to-end. No GroupAvgModel checkpoint, log, or comparison plot exists. `ld_sym`/`run_id_sym` are undefined. Step 9/10 comparisons exist only from prior kernel sessions. | 5/5 |
| C2 | HIGH | Rubric C.4 metric | Step 10 symmetry comparison uses Kaggle MARE (E) as the only metric. Rubric C.4 requires using "the metrics to evaluate the respect of symmetries that you proposed previously" — a symmetry-violation metric such as ‖q(Tx) − T(q(x))‖. No equivariance-error computation is present. | 4/5 |
| C3 | HIGH | Documentation mismatch | Stale hyperparameter values in markdown: (1) Step 7 markdown states lr=1e-4 / epochs=50 / patience=10 but code uses lr=1e-3 / epochs=150 / patience=20. (2) Step 9.3 markdown states patience=10 / epochs=50 but code uses patience=20 / epochs=150. (3) Cell 36 hardcodes `"max configured: 50"` but baseline trained with epochs=30. | 4/5 |
| C4 | HIGH | Rubric annotation | Step 10 markdown claims "→ Satisfies rubric B.3". The graded criterion for symmetry comparison is C.4. Graders scanning for C.4 will not find it explicitly claimed. | 3/5 |
| C5 | MEDIUM | ML hygiene — seeds | `torch.manual_seed(SEED)` is not called before `model_cnn` construction in cell 25. Steps 9 and 10 correctly re-seed before model instantiation; the step 7 baseline does not, making its weight initialization non-reproducible given all intervening random ops. | 2/5 |
| C6 | MEDIUM | Experiment tracking | Step 9 comparison plot saved as hardcoded `"step9_reg_comparison.png"`; step 10 comparison as `"step10_symmetry_comparison.png"` — both deviate from the `{model_name}_{YYYYMMDD_HHMMSS}` run_id convention. Plots cannot be matched to log/checkpoint by filename. | 3/5 |
| C7 | MEDIUM | Teaching mode | No markdown cell before cell 42 (GroupAvgModel training + comparison code). No expected-outcome statement for the step 10 comparison (what direction of improvement is expected, and what it would mean if GroupAvgModel performs worse). | 2/5 |
| C8 | MEDIUM | Ablation validity | GroupAvgModel comparison uses `model_reg` (MaskedCNNSoftplus + L2) as the "plain CNN" baseline. The two models differ on both symmetry enforcement AND Softplus activation. This is not a clean with/without-symmetry ablation. | 2/5 |
| C9 | LOW | Source attribution | `hflip()` and `vflip()` in cell 41 are missing `# adapted from lab7: flip()` comments. `rot180()` (new composition not directly in lab7) should note it is derived from composing two lab7 `rot()` calls. `GroupAvgModel` class has attribution but helpers do not. | 2/5 |
| C10 | LOW | Source attribution | The inverse-transform step in `GroupAvgModel.forward()` is a new addition absent from lab7 (which outputs a scalar, not a field). The comment block lists structural changes but does not flag this addition explicitly. | 2/5 |
| C11 | LOW | Non-physical outputs | Baseline `model_cnn` (trained in step 7) has no Softplus — negative predictions at open pixels are possible during training. Softplus only appears in step 9. If the Kaggle submission uses `model_cnn`, predictions may be non-physical. | 2/5 |
| C12 | LOW | Experiment hygiene | `experiments/logs/cnn_baseline_params.json` uses a non-standard name (no run_id timestamp) and has no corresponding code visible in the notebook. | 1/5 |

---

## Rubric Coverage (Merged, Steps 7–10)

| Section | Sub-point | Status |
|---------|-----------|--------|
| C.1 | Working CNN trained, valid predictions | PASS |
| C.2 | Key code snippets in report (`\lstlisting`) | OUT OF SCOPE (report) |
| C.3 | Train + val loss curves with axis labels | PASS (train_model() saves correctly) |
| C.3 | Overfitting commentary | PASS (cells 33–34) |
| C.3 | At least one anti-overfitting strategy shown working | CODED — NOT EXECUTED (cells 36–39 empty) |
| C.4 | Code running with and without hardwired symmetry | CODED — NOT EXECUTED (cells 41–42 empty) |
| C.4 | Quantitative metric comparing with/without symmetry | PARTIAL — metric is MARE, not symmetry-violation metric from A |
| C.4 | Rubric C.4 explicitly annotated | FAIL — annotated as B.3 |
| D | `num_params()` called, output shown | CODED — NOT EXECUTED (cell 27 empty) |
| D | ≤120,000 parameter bonus evidenced | NOT EVIDENCED |
| E | Seeds (torch + numpy) set | PARTIAL — missing before model_cnn in cell 25 |
| E | model.train() / model.eval() | PASS |
| E | torch.no_grad() during validation | PASS |
| E | Augmentation only on training set | PASS |
| E | Device handling consistent | PASS |
| Exp. tracking | run_id naming convention | PARTIAL — comparison plots violate convention |
| Exp. tracking | JSON log + checkpoint + plot saved per run | PASS for executed runs; missing for step 9/10 |

---

## Recommended Next Steps

### Must-fix (grade impact)
1. **Run all cells 25–42 end-to-end** — Steps 9 and 10 have no executed outputs. Without this, rubric C.3 (overfitting prevention) and C.4 (symmetry comparison) cannot be demonstrated.
2. **Add symmetry-violation metric for C.4** — Compute equivariance error `‖q(Tx) − T(q(x))‖` on the validation set for both models. This is what rubric C.4 requires by "the metrics proposed in A."
3. **Fix rubric annotation in step 10** — Change "→ Satisfies rubric B.3" to "→ Satisfies rubric C.4" in the step 10 markdown.
4. **Fix stale hyperparameter values in markdown** — Update step 7 markdown (lr, epochs, patience) and step 9.3 markdown + code comments to match the actual code. Fix cell 36's hardcoded "50".

### Should-fix (quality / reproducibility)
5. **Add `torch.manual_seed(SEED)` before `model_cnn` in cell 25** — For reproducibility parity with steps 9 and 10.
6. **Clean GroupAvgModel ablation** — Either (a) use a plain `MaskedCNN` (no Softplus) as the "no symmetry" baseline in step 10, or (b) document explicitly that the baseline for step 10 is `MaskedCNNSoftplus` and explain why this is still a valid comparison.
7. **Add run_id to comparison plot filenames** — Step 9.3 and step 10 comparison plots should use the `{model_name}_{YYYYMMDD_HHMMSS}` convention.
8. **Add markdown before cell 42** — Explain what cell 42 does, the expected outcome, and why group averaging should improve (or at minimum not hurt) validation loss.
9. **Add attribution comments to `hflip`, `vflip`** — `# adapted from lab7: flip()`. Note that `rot180` is a new composition.

---

## Rating

**Score: 3/5**
**Stars:** ⭐⭐⭐

| Score | Meaning |
|-------|---------|
| 5/5 | Production-ready, all rubric criteria met, no issues |
| 4/5 | Minor issues only, all major criteria satisfied |
| 3/5 | Correct design, significant gaps in execution or rubric coverage |
| 2/5 | Core functionality present but major rubric or correctness failures |
| 1/5 | Incomplete or fundamentally broken |

**Justification:** All 5 passes converged on the same root cause: the notebook was submitted with the majority of steps 9 and 10 unexecuted (empty output cells), making it impossible to demonstrate overfitting prevention working or the symmetry comparison. The code design is sound — `train_model()`, `GroupAvgModel`, and the regularisation comparison are all correctly implemented — but unexecuted code satisfies no rubric criteria. Secondary issues (wrong metric for C.4, stale markdown values, wrong rubric annotation) compound the gap and would each cost marks independently even after the execution issue is resolved.

---

## Commit Message

`fix(notebook): execute steps 7–10, add symmetry-violation metric for C.4, fix stale markdown hyperparameters, correct B.3→C.4 rubric annotation`
