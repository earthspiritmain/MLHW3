# dev/active/ — In-Progress Task Documentation

Use this folder for any implementation task that spans more than one session or involves a non-trivial design decision.

## When to create a task folder

- Designing a new model architecture (e.g. `cnn-baseline`, `unet-design`, `symmetry-module`)
- Planning a report section (e.g. `report-section-a`, `report-part2`)
- Planning the full training comparison (e.g. `symmetry-comparison`)

## Required files per task

```
dev/active/<task-name>/
├── <task>-plan.md         ← what will be done and why (accepted plan)
├── <task>-context.md      ← key files, rubric points addressed, constraints, Last Updated line
├── <task>-tasks.md        ← checklist; check off immediately when done
└── plan-audits/           ← written by /mlhw3-plan-audit
    ├── active-bundle.json ← pointer to latest plan audit
    └── <run_id>/
        ├── manifest.json
        └── findings.md
```

## Workflow

1. Create the three required files
2. Run `/mlhw3-plan-audit <task>` — stress-test the plan
3. Run `/mlhw3-plan-remediation task=<task>` — fix plan doc gaps
4. Implement step by step following `<task>-tasks.md`
5. After each component: run `/mlhw3-code-diff-audit-ensemble` → `/mlhw3-code-remediation`
6. After completion: move folder to `dev/archive/`

## Context file template

```markdown
# <task> — Context

**Last Updated:** YYYY-MM-DD

## Rubric points addressed
- [ ] A.x — ...
- [ ] B.x — ...

## Key files
- `assignment3.ipynb` — main notebook
- `reusable code/lab7-...ipynb` — source for create_model(), flip(), rot()

## Non-negotiables
- Teaching mode: explain every cell before implementing
- Equivariant augmentation: apply transforms to input AND label
- Experiment tracking: save to experiments/logs/, plots/, checkpoints/

## Constraints
- ≤120,000 parameters for bonus
- 6-page report limit
```

## Tasks file template

```markdown
# <task> — Tasks

**Last Updated:** YYYY-MM-DD

- [ ] Explain what the component does (student approves)
- [ ] Adapt function from lab (cite source)
- [ ] Implement cell
- [ ] Test: verify output shape / loss decreases / etc.
- [ ] Save experiment artifacts
- [ ] Update report section if needed
```
