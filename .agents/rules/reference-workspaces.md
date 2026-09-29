---
description: Sibling repos referenced by surgical-ed-vr for reusable patterns. Read-only; never edit these from within surgical-ed-vr.
alwaysApply: true
---

# Reference workspaces

These sibling folders sit next to `C:\Projects\surgical-ed-vr` and are
attached to the multi-root workspace via `surgical-ed-vr.code-workspace`.
Consult them for established patterns; never modify them from within a
surgical-ed-vr task.

## `C:\Projects\project_utility_scripts` (workspace + Cursor conventions)

- Cross-project cursor rule seed templates (see `cursor_setup.py`, which
  bootstraps `.cursor/rules/{ec2,notebooks,corpus,indexing}.mdc`).
- Workspace-wide dev conventions: `01-workspace-patterns.md`,
  `DEV_RULES.md`, `WORKSPACE_PORTFOLIO.md`, `README_cline_setup.md`.
- **Does NOT contain SSH setup** — its EC2 section only cites Cursor
  Remote-SSH usage, not any config file.

## `C:\Projects\aws-setup` (EC2, IAM, env-var, AWS service runbooks)

- Rich EC2 workflow: `ec2/README_ec2_notebook.md`, `ec2/README.md`,
  bootstrap scripts under `ec2/scripts/bash/`
  (`clone_and_setup.sh`, `setup_git_credentials_auto.sh`,
  `activate_venv.sh`, `setup_docker_ec2.sh`,
  `setup_duckdb_ec2.sh`, `setup_parallel_env.sh`,
  `setup_mnt_drive.sh`) and instance user-data under `ec2/bootstrap/`.
- Multi-language `.env` loader: `env/{load_env.sh, load_env.py,
  load_env.R, .env.example, replace_account_ids.py}`.
- IAM patterns: `iam/create_iam_user.py`, `iam/iam_new_user.qmd`.
- Uses the basic `ssh -i key.pem -L 8888:localhost:8888 ec2-user@ip`
  tunnel pattern only. The persistent `Host` alias + Remote-SSH wiring
  used in surgical-ed-vr lives in `dev_setup/ssh/` here, not in aws-setup.
- **`ec2_analysis/` in aws-setup is an empty placeholder.**

## `C:\Projects\notebookLM-edit-content` (Google Drive / Docs reference)

- Source of the Google Drive OAuth + Drive helper pattern re-used in
  `migrations/google_api_integration/`:
  - `src/ai_content_correction/gdrive.py` (auth flow, download, upload,
    export mappings)
  - `config/gdrive_accounts.yaml` (already includes a
    `jerome_dixon90` profile)
  - `docs/google-drive.md` (setup + first-time auth walkthrough)
- Uses `secrets/gdrive_<account>_client_secret.json` +
  `tokens/gdrive_<account>_token.json` on disk. Both directories are
  gitignored.
- The client secret for `jerome.dixon90@gmail.com` can be copied from
  `notebookLM-edit-content/secrets/` into
  `surgical-ed-vr/migrations/google_api_integration/secrets/` without regenerating
  it in Google Cloud Console.

## Rules of engagement

- Reference these paths in analysis, but do **not** commit changes to
  them from a surgical-ed-vr task. They are separate git repos.
- Prefer *copying + adapting* an idiom over cross-repo imports. Each
  surgical-ed-vr subsystem should remain runnable without these
  references present on disk.
- If a pattern is worth re-using long-term, promote it into
  `surgical-ed-vr/dev_setup/` or the relevant subpackage
  (e.g. `migrations/google_api_integration/`, `migrations/aws_account_migration/`) with the
  origin cited in a nearby README.
