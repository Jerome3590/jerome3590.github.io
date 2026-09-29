---
description: Use [1] for success and [X] for failure in logs and scripts
alwaysApply: true
---

# Status markers — `[1]` / `[X]`

Use ASCII status prefixes in **logs, deploy scripts, smoke tests, and handler output**. Do not use Unicode checkmarks (`✓`, `✗`, `⚠`) or bare `PASS`/`FAIL` in new code.

| Outcome | Marker | Example |
|---------|--------|---------|
| Success | `[1]` | `[handler] [1] Review pending -- {url}` |
| Failure | `[X]` | `[handler] [X] Error: {msg}` |

## Python

```python
print(f'[trip_intake] [1] Wrote trip-plan.md from form')
print(f'[handler] [X] Error: {error_msg}')
```

## PowerShell

```powershell
function Write-Ok($msg)   { Write-Host "  [1] $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "  [X] $msg" -ForegroundColor Red }

if ($cond) { Write-Host "  [1] $label" -ForegroundColor Green }
else       { Write-Host "  [X] $label" -ForegroundColor Red }
```

## Node / smoke tests

```javascript
console.log('[1] api-cors');
console.error('[X] api-cors:', err.message);
process.exit(1);
```

## Warnings

Use plain `WARN:` or `[!]` for non-fatal warnings — not `[X]` (reserved for failure).

## When editing

Replace `✓`, `✗`, `PASS`, and `FAIL` with `[1]` / `[X]` in the same change. Keep `[1]`/`[X]` at the **start** of the status token (after optional `[module]` prefix).
