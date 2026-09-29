---
description: Indexing and context budget rules for surgical-ed-vr
alwaysApply: true
---

# Indexing and Context Budget

- Open `surgical-ed-vr` directly rather than the `c:\Projects` monorepo root for focused work.
- Keep generated data, output folders, model artifacts, notebook checkpoints, and build artifacts out of context.
- Preserve source JSON/schema/config files in context; many Unity, QuickSight, and AWS definitions are meaningful source artifacts.
- Start a fresh chat when switching between paper analytics, QuickSight/AWS migration, and portal testing work.
