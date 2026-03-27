# Rubric — Full Requirements (from assignment3.tex)

Read `assignment3.tex` directly for the authoritative text. This file is a structured checklist for quick reference during audits.

---

## A. Physics of the problem — 2/10

Required for 10/10 (all sub-points):

1. **Dimensional analysis** — State SI units for all variables (ΔP [Pa], L [m], μ [Pa·s], ΔA [m²], q [m/s]). Write the learning problem in **dimensionless form** AND in **degree-1 homogeneous (scaling) form**.
2. **Symmetries** — Identify ALL invariances and equivariances of q(x,y). Distinguish invariance (scalar output unchanged) from equivariance (field output transforms with the input). Reflections (left-right, up-down) and rotations.
3. **Dataset characterization** — Statistical description of training data: parameter distributions, flow field distributions, example plots with axis labels and captions.
4. **≥3 loss functions** — Each written as an explicit formula. Each criticized in physical terms (dimensional homogeneity? penalizes non-physical outputs?). Kaggle loss E counts as one.
5. **Symmetry-penalizing loss** — At least one explicitly formulated loss-like function that penalizes outputs violating the identified symmetries.

Excellent (10): All points at highest scientific quality. All symmetries identified. Extensive dataset discussion. Physical reasoning for all loss functions.
Good (8–9): Correct dimensional analysis, ≥1 dimensionless + ≥1 homogeneous form. Basic dataset properties. Attempt at symmetries. ≥1 meaningful loss + attempt at symmetry loss.

---

## B. Network design — 2.5/10

Required for 10/10 (all sub-points):

1. **Data augmentation** — Strategy using identified symmetries. Disambiguation: how to break symmetry ties in labels during training.
2. **CNN/VGG design** — Specific architecture proposed. Receptive field computed per layer (numbers, not qualitative). Limitations identified.
3. **Fully convolutional NN** — Explicitly considered and criticized.
4. **U-Net** — Explicitly considered and criticized. Skip connections explained.
5. **Architecture diagrams** — At least one diagram per architecture discussed.
6. **Hardwiring symmetries** — Mathematical formalism for finite symmetry groups in a network. Applied to CNN, fully conv NN, and U-Net.
7. **Non-physical outputs** — Identified (e.g. positive flow at closed pixel=0). Prevention strategies proposed (masking, activation).

Excellent (10): Full mathematical formalism for symmetry hardwiring shown for all three architecture types.
Good (8–9): Correct theoretical discussion. Network designs with sketches. Qualitative performance expectations.

---

## C. Implementation and performance — 2.5/10

Required for 10/10 (all sub-points):

1. **Working CNN** — Trained, produces valid predictions.
2. **Code snippets** — Key architectural elements in `\lstlisting` in the report.
3. **Training visualization** — Train + validation loss curves with axis labels. Comment on overfitting. At least one anti-overfitting strategy shown working.
4. **Symmetry comparison** — Quantitative: with vs without hardwired symmetries, using the symmetry metric from A.
5. **Parameter efficiency** — CNN vs U-Net: parameter count vs performance comparison. Case made that U-Net is more efficient.

Excellent (10): Multiple models with/without symmetries. Working U-Net. Hardwired symmetries working. Quantitative comparison. Overfitting prevention evidenced.
Good (8–9): Working VGG-like CNN. Successful training shown. Concrete attempt at symmetry hardwiring. U-Net attempt.

---

## D. Kaggle competition — 2/10

Score thresholds (Kaggle loss E):
- 10/10: E < 0.10 × 10⁻²
- 9/10:  E < 0.12 × 10⁻²
- 8/10:  E < 0.16 × 10⁻²
- 7/10:  E < 0.22 × 10⁻²
- 6/10:  E < 0.40 × 10⁻²

**Low complexity bonus (0.5/10):** ≤ 120,000 trainable parameters. Must be evidenced with `num_params()` output in the report showing the per-layer count.

---

## E. Report quality — 1/10

- Clear layout, consistent structure, within **6 pages**
- Proper scientific language and grammar
- Every figure has **axis labels AND caption**
- Introduction present (problem overview + performance summary)
- Conclusion present (sums up results)
- A peer who has NOT read the assignment can reproduce all results from the report alone
- Bibliography present

---

## Kaggle loss formula (from assignment3.tex)

$$E = \frac{1}{|\text{dataset}|} \sum_{i} \frac{1}{N_X N_Y} \sum_{xy} \left| \frac{q_i^T(x,y) - q_i(x,y)}{q_i^T(x,y) + \varepsilon} \right|$$

Where q_i is predicted, q_i^T is ground truth, ε prevents division by zero.
