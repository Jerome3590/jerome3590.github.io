---
description: Use ASCII arrows (-->) everywhere; never Unicode →
alwaysApply: true
---

# ASCII arrows (`-->`) — project-wide

Use **`-->`** everywhere in this repo. Do **not** use **`→`** (U+2192).

Applies to: Python, PowerShell, JavaScript, docs, templates, customer guides, comments, log messages, and dashboard copy.

## Why

Windows `charmap` / PowerShell cannot reliably encode `→`. That breaks `aws logs tail`, deploy scripts, and local tooling:

`UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'`

## Standard

```python
print(f'[route]   {from_name} --> {to_name}: {leg["distance_km"]} km')
```

```markdown
| Date | Phase | From --> To | Activity |
```

```powershell
Write-Host "S3 --> Lambda trigger confirmed"
```

## Parsing legacy uploads

When reading **old** customer files that may still contain `→`, accept both separators in parsers only:

```python
if '-->' in route or '\u2192' in route or '->' in route:
    ...
```

New templates and examples use **`-->`** only.

## When editing

Never introduce `→`. If you see it, replace with `-->` in the same change.
