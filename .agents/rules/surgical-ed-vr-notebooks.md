---
description: Single-canonical notebook workflow for surgical-ed-vr
alwaysApply: true
---

# Notebook workflow — single canonical file per topic

There is **one notebook per topic**, at `papers/NEW_PAPER/<stem>.ipynb`.
No dev/production split, no output stripping, no S3 output cache, no
mirrored dev/ copies. History lives in git; rendered HTML for browser
review lives on S3.

The historical dual workflow was working around what turned out to be
notebook corruption caused by `EditNotebook` — see
[`notebook-edit-safety.mdc`](notebook-edit-safety.mdc). Now that we have
`dev_setup/scripts/validate_notebooks.py`,
`dev_setup/scripts/notebook_insert_cell.py`, and the pre-commit
validator hook, output-rich notebooks are safe to edit and open in
Cursor without any dev/ mirror.

## Canonical layout

| Role                     | Path                                            | Git                    |
|--------------------------|-------------------------------------------------|------------------------|
| Notebook (source + outputs) | `papers/NEW_PAPER/<stem>.ipynb`             | Yes, with outputs      |
| Supporting Python code    | `papers/NEW_PAPER/*.py`, `papers/NEW_PAPER/scripts/` | Yes               |
| Run metadata sidecar      | `papers/NEW_PAPER/<stem>.meta.json`           | Yes                    |
| HTML report (local)       | `papers/NEW_PAPER/reports/<stem>.html`        | No (gitignored)        |
| HTML report (rendered)    | `s3://surgical-ed-vr-analysis-visuals/reports/surgical-ed-vr/<stem>.html` | N/A |

Rendered browser URL:
`http://surgical-ed-vr-analysis-visuals.s3-website-us-east-1.amazonaws.com/reports/surgical-ed-vr/<stem>.html`

## Editing rules

1. **Never use `EditNotebook`** on any notebook with outputs — it silently
   drops `"name": "stdout"` from stream outputs and crashes Cursor's
   Jupyter renderer. Use `dev_setup/scripts/notebook_insert_cell.py`
   (safe `nbformat.write` path) or `nbstripout` first if you must.
2. **Validate after any structural change**:
   `python dev_setup/scripts/validate_notebooks.py --all` (or `--staged`).
3. **The pre-commit hook enforces schema validity** on every staged
   `.ipynb` — install with `make install-pre-commit-hook`.

## Commands

```bash
make publish     NB=validation_analysis     # local: execute + HTML report (+ S3 push)
make publish-ec2 NB=validation_analysis     # EC2: execute + HTML report + S3 push + git commit + push
make notebooks-validate                     # validate all .ipynb against nbformat schema
make status                                 # verify env + tooling
```

Execute-in-place means the same file becomes both source and outputs.
S3 report push happens automatically in `publish` / `publish-ec2` —
override with `PUSH_REPORT_TO_S3=0` for HTML-only local runs.

## Cursor stability

- Full DTW / production-cache runs still happen on EC2 (`papers/NEW_PAPER/WORKFLOW.md`).
- Save plots to `papers/NEW_PAPER/output/figures/` (committed via the
  team-facing allow-rule in `.gitignore`).
- `.ipynb` files are excluded from Cursor's automatic AI context;
  `@`-mention specific cells when you need to.
