# CLAUDE.md — 34MLS Assignment 3: Flow Field Through Porous Media

**Deadline: 11-04-2026 23:59** | Course: 34MLS TU/e | Individual assignment

Deliverables: `assignment3.tex` (PDF report, ≤6 pages, IEEE template) + `assignment3.ipynb` (notebook as .ipynb and .pdf) + ≥1 Kaggle submission.

---

## Non-negotiables

1. **Read `assignment3.tex` fully before every task.** Every sentence is the authority on what is required. Nothing may be missed.
2. **Teach before implementing.** Explain every component in plain language → student approves → implement exactly that one component. Never batch.
3. **Step-by-step coding order** — see `docs/coding-workflow.md`.
4. **No code before planning** for non-trivial components. Create `dev/active/<task>/` first, audit with `/mlhw3-plan-audit`, then implement.
5. **Parameter count ≤ 120,000** for the 0.5/10 bonus. Flag if exceeded; do not actively loop-check.
6. **Part D has no written report section.** Kaggle score is auto-graded. The only written evidence needed is the `num_params()` per-layer output (for the bonus) — fold it into Section C's parameter efficiency discussion, not a separate section.

---

## File Map

```
MLHW3/
├── assignment3.tex              ← PRIMARY SOURCE — rubric + problem (read every task)
├── assignment3.ipynb            ← main notebook (build step by step)
├── template.tex                 ← IEEE visual template
├── lecture notes.latex          ← notation + concepts reference
├── Assignement_3_helper_functions.ipynb  ← save_predictions_to_csv(), num_params()
├── reusable code/               ← lab4/5/6/7 + assignment2 notebooks
├── flow-field-through-a-porous-media-25-26/  ← Kaggle data
├── fig/                         ← figures for report (\includegraphics)
├── experiments/logs/            ← training loss dicts (.json)
├── experiments/plots/           ← all matplotlib figures (auto-save here)
├── experiments/checkpoints/     ← model .pt files
├── submissions/                 ← Kaggle CSV files
├── docs/                        ← reference files (read on demand)
│   ├── rubric.md                ← full rubric A–E with all sub-points
│   ├── reusable-functions.md    ← catalog of lab functions to adapt
│   └── coding-workflow.md       ← step-by-step coding order + experiment tracking
├── .audit/                      ← ensemble audit bundles
└── dev/active/                  ← in-progress task docs
```

---

## Skills

| Command | What it does |
|---------|-------------|
| `/mlhw3-plan-audit <task>` | N parallel passes over plan docs → P# findings + bundle |
| `/mlhw3-plan-remediation` | Fix plan docs → verify → closure |
| `/mlhw3-report-diff-audit` | Single-pass report audit (rubric + notation) |
| `/mlhw3-report-diff-audit-ensemble` | 5-lens report audit → merged bundle |
| `/mlhw3-code-diff-audit` | Single-pass notebook audit |
| `/mlhw3-code-diff-audit-ensemble` | 5-lens notebook audit → merged bundle |
| `/mlhw3-report-remediation` | Fix report → verify → grade estimate |
| `/mlhw3-code-remediation` | Fix notebook → verify → submission readiness |
| `/mlhw3-kaggle-submit` | Generate + validate submission CSV |

---

## Report Writing Style

- Write in long, dense paragraphs. Do not start a new paragraph or add a `\subsubsection` unless it directly answers a distinct rubric criterion.
- No italics anywhere (`\textit{}` and `\emph{}` are banned).
- No bold on words inside paragraphs (`\textbf{}` inside running prose is banned; bold is only permitted for list item labels, e.g. `\item \textbf{...}`).
- Merge related points into continuous prose rather than bullet lists or short fragments.

---

## Plot / Figure Rules

**One plot = one rubric point. No decorative plots.**

Before adding any new plot, ask: which specific rubric sub-point does this satisfy that no existing plot already covers? If the answer is none, do not add it.

**Consolidation rules (apply at all times):**
- Multiple related series → same axes with a legend, not side-by-side subplots. E.g. plain CNN val vs GroupAvg val on one axes, not two subplots.
- Multiple related histograms or scatter plots for the same step → one multi-panel figure (max 3 panels wide), not separate figures.
- Never generate an individual training loss curve for a model if a comparison plot already shows that model's curve. Use `save_plot=False` in `train_model()` for non-baseline runs.
- Never re-plot data that was already plotted in an earlier cell just to add annotations — modify the original cell instead.
- Cross-section + flow field examples: max 3 sample rows (not 6).

**Current approved figures (do not add more without justification):**
1. Cross-sections + flow fields — 3×2 grid (rubric A.3)
2. Physical parameter distributions — 2×2 histograms (rubric A.3)
3. Flow stats + porosity — 1×3 (nonzero q / porosity hist / porosity vs Q) (rubric A.3)
4. Dimensional analysis — 1×2 (π₂ CV / q/v₀ histogram) (rubric A.1)
5. Augmentation verification — 2×4 (rubric B.1)
6. Baseline training curve — 1 auto-plot from `train_model()` (rubric C.2)
7. Prediction visualisation — n×4 panels (rubric C.1)
8. Combined C.3+C.4 figure — 1×3 (L2 comparison / sym val comparison / SV bars) (rubric C.3+C.4)
9. Step 11 param efficiency — 1×2 (val loss curves all 3 models / param count scatter) saved as `step11_reg_comparison.png` (rubric C.5)

---

## Hard Constraints

1. No numerical PDE solvers, FEM, or analytical solutions as models — feedforward NNs only.
2. Report ≤ 6 pages. Overflow to appendix (notebook).
3. Every figure needs axis labels + caption.
4. Set `torch.manual_seed()` and `np.random.seed()` at notebook top (reproducibility, rubric E).
5. Submission CSV: id column must be integer (not 1.0), 2048 prediction columns, 500 rows.
