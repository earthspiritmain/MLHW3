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

## Hard Constraints

1. No numerical PDE solvers, FEM, or analytical solutions as models — feedforward NNs only.
2. Report ≤ 6 pages. Overflow to appendix (notebook).
3. Every figure needs axis labels + caption.
4. Set `torch.manual_seed()` and `np.random.seed()` at notebook top (reproducibility, rubric E).
5. Submission CSV: id column must be integer (not 1.0), 2048 prediction columns, 500 rows.
