---
description: Shared machine-local credentials path for all projects
alwaysApply: true
---

# Shared Credentials

- AWS shared credentials file: `C:\Projects\credentials` (env: `AWS_SHARED_CREDENTIALS_FILE`)
- SSH / PEM keys: `C:\Projects\*.pem` (e.g. `mushin_pgx.pem`)
- Never commit secrets, print credential file contents, or invent per-repo `.aws/` key stores
- Prefer `AWS_PROFILE` / `EC2_KEY_PATH` / `GITHUB_PAT` env overrides when needed

Canonical docs: `C:\Projects\project_utility_scripts\CURSOR_DEV_RULES.md`
