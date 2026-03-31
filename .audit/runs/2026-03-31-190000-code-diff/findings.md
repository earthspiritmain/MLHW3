# Ensemble Code Audit — Steps 5–6 — 2026-03-31

**Scope:** Steps 5 (Baseline CNN) and 6 (Loss function) only.
**Passes:** 5 parallel passes with rotated lenses (physics, rubric C/D, ML hygiene, teaching mode, experiment tracking).
**Notebook:** `assignment3.ipynb`

---

## Executive Summary

- **Top risk:** `kaggle_loss` has a latent explosion risk at closed pixels (~|pred|×10⁶) when called without the `MaskedCNN` wrapper — this will silently corrupt ablation/symmetry experiments in later steps (confirmed by 5/5 passes).
- **Architecture concern:** `nn.Flatten(start_dim=1, end_dim=2)` is a fragile non-standard idiom that only works because the final Conv2d outputs exactly 1 channel; no assertion guards it (4/5 passes).
- **Physics gap:** `v0` velocity scale is not injected into the CNN at inference — predictions are dimensionless but no mechanism reconstructs physical units at test time (3/5 passes).
- **Teaching gap:** ε = 1e-6 is used without justification relative to the normalised label scale; `num_channels=16` capacity tradeoff is not explained.
- **Experiment tracking gap:** `num_params()` output is printed to stdout only; per workflow convention it should be persisted to `experiments/logs/`.
- **All passes confirmed:** Seeds correct, device handling correct, loss formula mathematically correct, `create_model()` and `rmsre()` adaptations correct with proper attribution, augmentation equivariance correct, dimensional preprocessing clean.
- **Notebook unexecuted:** All cells have `execution_count=None`; smoke test outputs not visible.
- **Parameter count:** ~18,592 << 120,000 — bonus cap comfortably met.

---

## Merged Findings Table

| ID | Severity | Category | Finding | Consensus |
|----|----------|----------|---------|-----------|
| C1 | HIGH | Loss — closed pixel latent risk | `kaggle_loss` divides by `truth + eps` (ε=1e-6). At closed pixels ground truth=0, so denominator=1e-6. If called with unmasked predictions (e.g. ablation, symmetry comparison without `MaskedCNN`), closed-pixel outputs contribute ~\|pred\|×10⁶ to the loss, silently exploding training. The function carries no docstring or comment warning about this dependency on masked inputs. | 5/5 strong consensus |
| C2 | MEDIUM | Architecture — Flatten fragile | `nn.Flatten(start_dim=1, end_dim=2)` merges the singleton channel dim with H=32. Works only because the final `Conv2d` outputs exactly 1 channel. Any future change to output channels would silently produce wrong shapes. `squeeze(1)` or an assertion `assert out.shape[1] == 1` would be semantically clearer and safer. | 4/5 strong consensus |
| C3 | MEDIUM | Physics — v0 not recoverable at inference | CNN receives only the binary cross-section `(B,1,32,64)`; the velocity scale `v0 = ΔP·ΔA/(μ·L)` (per-sample, from Step 3) is absorbed into label normalisation at training time but there is no mechanism to re-apply it when converting dimensionless predictions back to physical units [m/s] at inference (Step 7/13). Must be resolved before Step 7. | 3/5 majority |
| C4 | MEDIUM | Physics — non-negativity not asserted in smoke test | No output activation constrains predictions to non-negative values. Deliberately deferred to Step 9, but the Step 5 smoke test does not assert that output values are ≥ 0, so a randomly-initialised model silently produces negative flow rates with no flag. At minimum, a note or `print(f"output min: {out.min():.4f}")` would surface this. | 3/5 majority |
| C5 | MEDIUM | Experiment tracking — num_params() not persisted | `num_params(model)` result is printed to stdout only. Per `docs/coding-workflow.md`, experiment metadata should be saved to `experiments/logs/` (e.g. as part of the `run_id` JSON). Also, the attribution comment says "Direct reuse" but a `return total` statement was added — minor inaccuracy. | 3/5 majority |
| C6 | LOW | Loss — ε value undocumented vs dataset scale | `EPSILON = 1e-6` is chosen without any reference to the normalised label range (~O(0.1–1) from Step 3 statistics). A comment anchoring the choice ("ε ≪ minimum non-zero q/v0 ≈ 0.001 in the training set") would prevent misuse when labels are in different units. | 3/5 majority |
| C7 | LOW | Architecture — adaptation comment slightly misleading | Inline comment says "same three-block VGG-like structure" but the third `MaxPool2d` from lab7 is removed (only 2 pooling stages used here). The markdown explanation cell correctly documents this choice; the inline comment should be updated to match. | 2/5 majority |
| C8 | LOW | Teaching — num_channels=16 design rationale missing | Markdown gives the resulting parameter count (~18,600) but does not explain why 16 channels were chosen over 8 or 32 in terms of capacity-vs-budget tradeoff. One sentence would satisfy this. | 2/5 majority |
| C9 | LOW | ML hygiene — bias=False on final conv | Output `Conv2d(C, 1, kernel_size=1, bias=False)` disables the output-layer bias. A bias allows the network to learn a non-zero output mean; without it the model must learn this offset entirely through the weights, potentially slowing convergence on fields with non-zero mean flow. Minor efficiency concern. | 1/5 singleton |

---

## Rubric Coverage (Steps 5–6)

| Section | Sub-point | Status |
|---------|-----------|--------|
| C.1 | Working CNN implemented | PRESENT — `MaskedCNN(create_model())` defined; smoke test code in cell 21 |
| C.1 | CNN produces valid predictions | NOT YET — notebook unexecuted; will be confirmed after Step 7 training |
| C.2 | Key architectural code snippets | PRESENT — full `create_model()` + `MaskedCNN` in cell 21 with shape-annotated diagram in cell 20 |
| C (physics) | Closed-pixel masking (q=0) | PRESENT — `MaskedCNN` wrapper adds zero parameters |
| C (physics) | Non-negative output constraint | DEFERRED — explicitly deferred to Step 9; no assertion in smoke test |
| D (bonus) | num_params() ≤ 120,000 evidenced | PRESENT in code (unexecuted); estimated ~18,592 |
| A.4 | Loss formula written explicitly before code | PRESENT — LaTeX formula in cell 22 |
| Step 5 | `create_model()` adapted from lab7 with attribution | PRESENT — comment + markdown document all changes |
| Step 5 | Output shape 32×64 correct | PRESENT — assertion `dummy_output.shape == (4, 32, 64)` in cell 21 |
| Step 6 | `kaggle_loss` adapted from lab7 `rmsre()` with attribution | PRESENT — both formula changes documented |
| Step 6 | ε guard present | PRESENT — `EPSILON = 1e-6`, denominator `truth + eps` |
| Step 6 | Sanity checks | PRESENT — three checks (perfect, all-zero, 2× over-prediction) |
| Experiment tracking | experiments/ directories created | PRESENT — cell 2 |
| Experiment tracking | run_id setup | Correctly deferred to Step 7 |
| Experiment tracking | num_params persisted to log | MISSING |
| Rubric E | Seeds set at top | PRESENT — both `torch.manual_seed(SEED)` and `np.random.seed(SEED)` in cell 2 |

---

## Recommended Next Steps

### Must-fix (before Step 7 training)

1. **C1 — Document the mask dependency in `kaggle_loss`**: Add a docstring or comment: "WARNING: `truth` must be masked-CNN output or a physics-masked tensor. At closed pixels truth=0 and eps=1e-6; calling with unmasked predictions will produce loss ~|pred|×10⁶." This prevents silent corruption in Step 10 symmetry-comparison ablations.
2. **C3 — v0 at inference**: Decide and document how per-sample `v0` is applied to convert dimensionless CNN output back to physical units [m/s] at inference time. Options: (a) keep labels normalised, return dimensionless predictions, multiply by v0 in post-processing; (b) inject v0 as a second input channel. The chosen strategy must be implemented before Step 7.

### Should-fix (before report submission)

3. **C2 — Replace fragile Flatten**: Change `nn.Flatten(start_dim=1, end_dim=2)` to `nn.Sequential(..., nn.Conv2d(C, 1, 1), Squeeze(dim=1))` or add `assert out_channels == 1` before the Flatten.
4. **C4 — Add non-negativity note in smoke test**: Print `f"output min: {out.min():.4f}"` after the smoke test to surface physically-invalid negatives at Step 5.
5. **C5 — Persist num_params() to log**: Save the parameter count dictionary to `experiments/logs/cnn_baseline_params.json` alongside the training run.
6. **C6 — Anchor ε to dataset**: Add one comment line justifying `EPSILON = 1e-6` relative to minimum non-zero normalised flow rate.

### Nice-to-have

7. **C7 — Fix inline comment**: Update "same three-block VGG-like structure" to "three-block encoder, third block without MaxPool".
8. **C8 — Explain num_channels=16 choice**: Add one sentence on capacity-vs-budget rationale.
9. **C9 — Consider output bias**: Change final conv to `bias=True` (default) to allow learning of non-zero output mean.

---

## Rating

- **Score: 4/5**
- **Stars:** ⭐⭐⭐⭐
- **Rating scale:**
  | Score | Meaning |
  |-------|---------|
  | 5/5 | Production-ready, all checks pass |
  | 4/5 | Solid implementation, minor issues |
  | 3/5 | Works but has notable gaps |
  | 2/5 | Partial implementation, blocking issues |
  | 1/5 | Major correctness failures |
- **Justification:** All 5 passes independently gave 4/5. Steps 5 and 6 are structurally sound: the CNN correctly handles the 32×64 grid, the physics mask is a genuine improvement over the lab7 baseline, the loss formula faithfully implements the Kaggle spec, attribution is complete on all three adapted functions, seeds and device handling are correct, and the teaching-mode explanation cells are thorough. The score is held at 4/5 (not 5/5) by: the HIGH-severity latent loss explosion risk at closed pixels (C1, confirmed by 5/5 passes), the unresolved v0 inference path (C3), and the fragile Flatten idiom (C2). None of these block the current step in isolation, but C1 and C3 will cause problems in Steps 7 and 10 if left unresolved.

---

## Commit Message

`feat(notebook): add baseline MaskedCNN (step 5) and kaggle_loss with ε guard (step 6) — lab7 attribution, ~18.6k params`
