# Ensemble Code Audit — Steps 1–5
**Run:** 2026-03-31-170000-code-diff | **Tool:** mlhw3-code-diff-audit-ensemble | **N=5 passes**
**Scope:** steps-1-5

---

## Executive Summary

**Top risks (grade impact order):**

1. **C1 — Homogeneity degree wrong (HIGH):** Step 3 markdown labels v₀ = ΔP·ΔA/(μ·L) as "degree-1 homogeneous." It is degree-0 (scale-invariant). Rubric A.1 explicitly requires the degree-1 form — this will cost marks.
2. **C2 — No output activation (HIGH):** The CNN final layer is unconstrained. q ≥ 0 physically, but the network can produce negative predictions. No ReLU/Softplus at output. Rubric B.7 requires prevention strategies.
3. **C3 — No closed-pixel masking (MEDIUM):** Pixels where the cross-section = 0 must have q = 0. The architecture does not multiply output by the input binary mask. Step 1 summary table promised this for Step 5; it was not implemented.
4. **C4 — CUDA seed missing (HIGH):** `torch.cuda.manual_seed_all(SEED)` absent from setup cell. GPU runs will be non-reproducible (different weight inits than CPU). Rubric E requires full reproducibility.
5. **C8 — `num_params()` not called (MEDIUM):** The per-layer parameter breakdown required for the D-section bonus proof is absent. Only a total count is printed inline.
6. **C12 — `flip_h` attribution inconsistency (LOW):** `flip_h` has no `# adapted from lab7` comment inside its function body — the other two flip functions do.
7. **C14 — Receptive field not computed (LOW):** Rubric B.2 requires numerical receptive field computation per layer. Not present in Steps 1–5.

**Consistently found (≥3/5 passes):**
- C2 (output activation): passes 1, 2, 4 → Majority
- C12 (flip_h attribution): passes 2, 4, 5 → Majority

**Singleton findings (1/5 pass — needs confirmation before fixing):**
- C1 (degree-0 label), C4 (CUDA seed), C5 (cudnn flags), C6 (model.to(device)), C7 (model.eval), C10 (Buckingham definition), C11 (equivariance plain language), C13 (Flatten vs squeeze diagram)

**Parameter count status:** 18,592 params at C=16 — **well within 120,000 bonus cap.** But per-layer `num_params()` proof is missing.

---

## Merged Findings Table

| ID | Severity | Category | Finding | Consensus |
|----|----------|----------|---------|-----------|
| C1 | HIGH | Physics | Step 3 labels v₀ = ΔP·ΔA/(μ·L) as "degree-1 homogeneous." Scaling all 4 inputs by λ gives λ²/λ² · v₀ = v₀ — degree-0 (invariant), not degree-1. Rubric A.1 requires the degree-1 form. | Singleton (Pass 1) |
| C2 | HIGH | Physics / Architecture | CNN output layer has no activation. q ≥ 0 physically; network can output negative values. No ReLU, Softplus, or clamp after `Conv2d(C→1)`. Rubric B.7 requires prevention strategies implemented. | Majority (Passes 1, 2, 4) |
| C3 | MEDIUM | Physics / Architecture | No closed-pixel masking. At pixels where cross-section = 0, q must be exactly 0. Output is not multiplied by the input binary mask. Step 1 summary (cell 13) promised this for Step 5. | 2/5 (Passes 1, 2) |
| C4 | HIGH | Seeds / Reproducibility | `torch.cuda.manual_seed_all(SEED)` is absent from the setup cell. GPU runs produce different convolutional weight initializations than CPU runs. Rubric E requires a peer to reproduce all results. | Singleton (Pass 3) |
| C5 | MEDIUM | Seeds / Reproducibility | `torch.backends.cudnn.deterministic = True` and `torch.backends.cudnn.benchmark = False` not set. Non-deterministic cuDNN algorithm selection means two GPU runs of identical code can differ. | Singleton (Pass 3) |
| C6 | MEDIUM | Device | Smoke test in Step 5 creates `dummy_input` and `model` without `.to(device)`. Works by accident on CPU but breaks the device-consistency pattern needed for all later training cells. | Singleton (Pass 3) |
| C7 | MEDIUM | ML hygiene | `model.eval()` not called before the `torch.no_grad()` smoke test. Harmless now (no BN/Dropout), but establishes a bad pattern that will cause silent bugs when regularisation layers are added. | Singleton (Pass 3) |
| C8 | MEDIUM | Rubric D | `num_params()` from the helper notebook is never imported or called. Only `sum(p.numel() for p in model.parameters())` is used. Per-layer breakdown required for rubric D bonus proof is absent. | 2/5 (Passes 2, 5) |
| C9 | LOW | Teaching | Split ratio `0.8` is a bare literal in cell 15; no `TRAIN_SPLIT = 0.8` constant. `BATCH_SIZE = 32` defined inside Step 2 code cell rather than in the top-level setup block. | Singleton (Pass 4) |
| C10 | LOW | Teaching | Buckingham π theorem applied in Step 3 without first stating it in one plain-language sentence ("n variables, m base units → n−m dimensionless groups"). Readers unfamiliar with the theorem have no entry point. | Singleton (Pass 4) |
| C11 | LOW | Teaching | Equivariance is defined only via the formula `T(q(x,y)) = q(T(x,y))` in Step 4; no preceding plain-language sentence ("flipping the input produces a correspondingly flipped output"). | Singleton (Pass 4) |
| C12 | LOW | Attribution | `flip_h` has no `# adapted from lab7` comment inside its function body. `flip_v` and `flip_hv` both have the comment. Inconsistency visible to any reader scanning individual functions. | Majority (Passes 2, 4, 5) |
| C13 | LOW | Documentation | Step 5 architecture diagram (markdown) shows `squeeze(1)` while the code uses `nn.Flatten(start_dim=1, end_dim=2)`. Both produce `(B,32,64)` from `(B,1,32,64)` — correct — but diagram ≠ code. | Singleton (Pass 2) |
| C14 | LOW | Rubric B.2 | Receptive field per layer not computed anywhere in Steps 1–5. Rubric B.2 requires "scaling of receptive fields computed per layer (numbers, not qualitative)." | Singleton (Pass 2) |
| C15 | LOW | Rubric B.2 | Step 5 markdown never uses the term "VGG-like." Rubric C.1 and B.2 both reference CNN/VGG design; the architecture should be explicitly identified as VGG-like. | Singleton (Pass 2) |
| C16 | LOW | Teaching | Step 5 markdown references "rubric C.1" but not "rubric C.2" (code snippets of key architectural elements in report). The architecture in cell 21 is exactly the C.2 evidence. | Singleton (Pass 4) |
| C17 | LOW | Teaching | No explanation of why the output layer has no activation (linear output for regression vs. classification distinction). Especially relevant given C2 is a known physics gap. | 2/5 (Passes 1, 4) |
| C18 | LOW | Experiment tracking | Step 5 produces no disk artifact (no architecture log, no `num_params()` output file). Coding-workflow.md intent is that every materialised model leaves a trace. | Singleton (Pass 5) |

---

## Rubric Coverage (Steps 1–5)

| Section | Sub-point | Status |
|---------|-----------|--------|
| A.1 | SI units for all 5 variables | PASS |
| A.1 | Buckingham π: 4 vars, 3 units → 2 groups | PASS |
| A.1 | Dimensionless form written explicitly | PASS |
| A.1 | Degree-1 homogeneous form correct | **FAIL** — labeled degree-1, is degree-0 (C1) |
| A.3 | Dataset characterisation with labelled plots | PASS — 4 plots with axes/colorbars |
| B.1 | Augmentation using correct symmetry group | PASS — V₄ ≅ Z₂×Z₂ |
| B.1 | Same transform on input AND label | PASS |
| B.1 | Disambiguation explained | PASS |
| B.2 | Receptive field computed per layer | **MISSING** (C14) |
| B.2 | Architecture identified as VGG-like | **MISSING** (C15) |
| B.7 | Non-physical outputs identified + prevention | **MISSING** (C2, C3) |
| C.1 | Working CNN, correct I/O shapes | PASS (architecture only; training is Step 7) |
| C.2 | Code snippets for report | PARTIAL — code present, rubric ref missing (C16) |
| D | ≤120,000 params confirmed | PARTIAL — total count only; per-layer via `num_params()` missing (C8) |
| E | torch/numpy seeds set | PARTIAL — CPU seeds set; CUDA seed missing (C4) |
| E | cudnn determinism | **MISSING** (C5) |

---

## Recommended Next Steps

### Must-fix (grade impact)
1. **C1** — Correct degree-0 label in Step 3 markdown. v₀ is scale-invariant (degree-0). The degree-1 form is `q = v₀ · f(cross-section)` where f is the dimensionless function the network learns — state this explicitly.
2. **C2** — Add output activation (or masking) to `create_model()`. Minimum: apply input mask `output * x.squeeze(1)` to enforce q=0 at closed pixels (also fixes C3). Optionally add `nn.ReLU()` or `nn.Softplus()` before the mask.
3. **C4** — Add `torch.cuda.manual_seed_all(SEED)` to the setup cell immediately after `torch.manual_seed(SEED)`.

### Should-fix (rubric coverage or hygiene debt)
4. **C3** — Closed-pixel masking (if not already handled by C2 fix).
5. **C5** — Add `torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False` to setup cell.
6. **C6 + C7** — Add `model.to(DEVICE)`, `dummy_input.to(DEVICE)`, and `model.eval()` to Step 5 smoke test.
7. **C8** — Import and call `num_params(model)` at end of Step 5 smoke test.
8. **C14** — Compute receptive field per layer (can be in a markdown cell with a table).

### Low priority (polish)
9. **C12** — Add `# adapted from lab7: flip(x) = torch.flip(x, [-1])` inside `flip_h` body.
10. **C13** — Update architecture diagram in Step 5 markdown: replace `squeeze(1)` with `Flatten(start_dim=1, end_dim=2)`.
11. **C9** — Move `BATCH_SIZE` to setup cell; define `TRAIN_SPLIT = 0.8`.
12. **C10/C11** — Add one-sentence plain-language statements for Buckingham theorem and equivariance.
13. **C17** — Explain in Step 5 markdown why no output activation is used (or explain the C2 fix).

---

## Rating

**Score: 3/5**
**Stars:** ⭐⭐⭐

| Score | Meaning |
|-------|---------|
| 5 | No issues or trivial polish only |
| 4 | Minor gaps, no physics errors |
| 3 | Moderate issues: 1–2 HIGH findings, some rubric gaps |
| 2 | Major issues: physics wrong or training broken |
| 1 | Critical blockers: non-functional |

**Justification:** Individual pass scores were 3, 3, 4, 4, 3.5 → averaged 3.5/5. Rounded down to 3 due to two HIGH-severity physics findings (C1: wrong homogeneity degree — directly costs A.1 marks; C2: unconstrained output — directly costs B.7 marks) plus a HIGH reproducibility gap (C4). The foundations are solid: equivariant augmentation is correctly implemented, the Buckingham π analysis is structurally complete, all 5 plots have axis labels, the CNN produces the correct I/O shape, and 18,592 parameters are well under the bonus cap. With C1–C4 fixed this audit would score 4/5.

---

## Commit Message

`fix(notebook): correct degree-0 homogeneity, add output masking + CUDA seed to steps 1-5`
