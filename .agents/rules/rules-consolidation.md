---
description: Where Cursor rule files live, why they are not tracked per-project, and the canonical mirror location
alwaysApply: true
---

# Rule-file storage policy

## Per-project rule files are NOT committed

Every workspace keeps its rules in `.cursor/rules/*.mdc`, but in this
organisation **that folder is intentionally `.gitignore`d on every project repo**.
Project repos therefore never carry rule files in their commit history — do not
attempt to `git add -f .cursor/` to work around this.

## Canonical mirror: `C:\Projects\project_utility_scripts`

All rule files are consolidated and version-controlled in one repo:

```text
C:\Projects\project_utility_scripts\.cursor\rules\*.mdc
C:\Projects\project_utility_scripts\CURSOR_DEV_RULES.md
C:\Projects\project_utility_scripts\DEV_RULES.md
C:\Projects\project_utility_scripts\docs\lessons_learned\
```

Treat those paths as the authoritative store. `.mdc` rules already consolidated
include dashboard JSON/S3 rules, `duckdb-r-connection.mdc`, notebook/EC2 variants
(project-prefixed when names collide), plus whatever has been added since.

Shared Markdown guidance lives at the root of this repo (`CURSOR_DEV_RULES.md`,
`DEV_RULES.md`) and under `docs\lessons_learned\`.

## Workflow when you create or edit a rule

1. Write / edit the rule in the project's local `.cursor/rules/<name>.mdc` so it
   takes effect immediately in the current Cursor workspace.
2. **Copy** (not move) the same file to `C:\Projects\project_utility_scripts\.cursor\rules\<name>.mdc`.
3. If the rule is project-specific, keep the filename unique (e.g.
   `querying-telemetry.mdc` is RL-project-specific but useful to archive alongside
   other projects' rules).
4. Commit the change **in `project_utility_scripts`**, not in the product repo.
   Product repos have nothing to stage because `.cursor/` is ignored there.
5. If `.cursor/` is gitignored here too, sync commits must use
   `git add -f .cursor/rules/<name>.mdc` to override the ignore. That is the one
   place `-f` is correct.

## Why this policy exists

- Rule files are personal + cross-project guidance, not project source code.
- Consolidating them in `project_utility_scripts` makes it easy to audit, grep,
  and port rules across projects without fragmenting them into N project histories.
- Keeping project repos free of rule files keeps diffs focused on product work.

## PowerShell one-liner to sync after editing

```powershell
Copy-Item -Force `
  "<project-root>\.cursor\rules\*.mdc" `
  "C:\Projects\project_utility_scripts\.cursor\rules\"
```

