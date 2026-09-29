---
description: Python, R, Windows/WSL, and terminal execution rules for this repo
alwaysApply: true
---

# Dev Environment

- Work from the repository root: `C:\Projects\notebookLM_edits` on Windows or `/mnt/c/Projects/notebookLM_edits` from WSL-style shells.
- The active terminal is Git Bash on Windows. Use bash-compatible commands by default; use `powershell.exe -NoProfile -Command '...'` only when Windows environment APIs or native Windows paths are required.
- Python on `PATH` is Python 3.12.3 at `C:\Program Files\Python312\python.exe`. The Windows launcher also has Python 3.13, 3.12, 3.9, and uv-managed 3.11 available; do not switch versions unless the project config requires it.
- Prefer `uv` for Python dependency and task execution when project metadata exists. Until then, create/use a project-local `.venv` and avoid global `pip install`.
- R 4.6.0 is installed at `C:\Program Files\R\R-4.6.0`. Git Bash user startup prepends `/c/Program Files/R/R-4.6.0/bin`, so `Rscript` should resolve to R 4.6.0 in this repo. Set `R_HOME=C:/Program Files/R/R-4.6.0` and `R_LIBS_USER=C:/R/libs-4.6` for R commands so packages are not loaded from older R library trees. Use `renv` if R package state becomes part of the project.
- The shared user `.Renviron` path is `C:\Users\jerom\OneDrive\Documents\.Renviron`; treat it as machine-local configuration and never commit its contents.
- When R is upgraded, update all environment surfaces together: Windows User PATH, Windows Machine PATH when admin is available, `R_HOME`, `R_LIBS_USER`, Git Bash startup (`C:\Users\jerom\.bash_profile`), Cursor user settings (`%APPDATA%\Cursor\User\settings.json`), VS Code user settings (`%APPDATA%\Code\User\settings.json`), and `docs/r-environment.md`.
- After any R environment update, verify with `Rscript --version`, `which Rscript`, a fresh `bash --login -c 'Rscript --version && which Rscript'`, and JSON validation for edited IDE settings. Search settings/docs for stale `R-4.x` and old library paths before finishing.
- Keep machine-specific paths, secrets, and credentials out of Git. Use untracked files such as `.env`, `.Renviron`, or `env/vars.sh` if local configuration is needed.
- Do not hard-code OS-specific data paths in Python or R. Read paths from environment variables and build paths with `pathlib.Path` in Python or `file.path()` in R.
- Keep Python and R console output ASCII-safe for Windows terminals; use `->` instead of Unicode arrows or other characters that can fail under Windows code pages.
- Scope validation commands to the changed component. Avoid broad, long-running, networked, or destructive commands unless the task explicitly requires them.
