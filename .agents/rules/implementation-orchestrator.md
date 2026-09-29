---
description: Sequential implementation-plan orchestration rules
alwaysApply: true
---

# Implementation Orchestrator

- Treat `IMPLEMENTATION_TODO.md` as the source of truth for remaining build work.
- When acting as the orchestrator, work one unchecked item at a time in document order unless the user explicitly reprioritizes.
- Do not run implementation TODO items in parallel. Finish the active item, validate it, record/fix errors, then move to the next item.
- For each item, define a clear artifact, acceptance check, and validation command before editing.
- If validation fails, stop forward progress, capture the error, create fix tasks, complete those fixes, rerun validation, and only then mark the original item complete.
- Keep generated data and local outputs out of Git unless the implementation plan explicitly says the artifact should be committed.
- Prefer small, reviewable changes and focused tests. Broaden validation when the change touches shared pipeline behavior or deployment artifacts.
- Update `IMPLEMENTATION_TODO.md` only after the artifact is built and validation passes.
