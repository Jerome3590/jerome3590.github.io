---
description: Where Cursor IDE baselines live; known-bad extensions
alwaysApply: false
---
# Cursor IDE baseline (settings + extensions)

After fixing notebook/Python hangs or extension activation toasts, compare
against the dated snapshot — do **not** invent a new settings dump from scratch.

## Location (git, not S3)

`dev_setup/cursor/baselines/<YYYY-MM-DD>/`  
Pointer: `dev_setup/cursor/baselines/LATEST`

Refresh:

```bash
python dev_setup/scripts/snapshot_cursor_baseline.py
```

**Why git:** PR-diffable, works offline, survives laptop changes.  
**Why not S3:** S3 is for analysis data / HTML reports, not IDE tooling history.  
**Why not full dump in this rule:** rules stay short; the baseline folder holds
the files.

## Known-bad (do not reinstall for this project)

- `luma.jupyter` — crashes; conflicts with `ms-toolsai.jupyter`
- `VisualStudioExptTeam.vscodeintellicode` (+ api-usage-examples) — fails on Cursor; wakes on Python cells
- `paiqo.databricks-vscode` — activates on every notebook open without a Databricks connection

Canonical blocklist also lives in `.vscode/extensions.json` → `unwantedRecommendations`
and in the latest baseline’s `known-bad-extensions.md`.

## Keep

- `ms-toolsai.jupyter` (+ keymap, renderers)
- Workspace interpreter → `.venv_surgical_ed_vr`
- Hang mitigations already in `.vscode/settings.json` (see baseline `workspace.settings.json`)

## Venv / kernel hang (root cause + fix)

Full write-up: [`dev_setup/cursor/VENV_AND_KERNEL_TROUBLESHOOTING.md`](../../dev_setup/cursor/VENV_AND_KERNEL_TROUBLESHOOTING.md)

Short version: `.venv_surgical_ed_vr` is non-standard for Microsoft’s
locator; always pin `python.defaultInterpreterPath`, put the name in
`python.venvFolders`, and set `python-envs.defaultEnvManager` to
`ms-python.python:venv`. Prove the kernel with `jupyter kernelspec list`
**outside** Cursor before debugging the Jupyter UI.
