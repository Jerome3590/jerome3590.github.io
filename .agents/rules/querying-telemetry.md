---
description: How to query AWS telemetry (DynamoDB + bakkesmod.log) from PowerShell without encoding, quoting, or schema-assumption traps
alwaysApply: true
---

# Querying telemetry from PowerShell (AWS CLI + bakkesmod.log)

Hard-won lessons from the v4.1 flip-reset investigation. Follow these every time
you diagnose a discrepancy between the BakkesMod plugin and `events_rocket_league`.

## 1. Describe the table before filtering

Never assume attribute names from memory or docs — DDB will happily return
`Count=0, ScannedCount=17469` when you filter on a name that doesn't exist.

```powershell
aws dynamodb describe-table --table-name events_rocket_league `
  --profile mushin --region us-east-1 `
  --query "Table.[KeySchema,AttributeDefinitions,ItemCount]"
```

Real keys today: `Game_ID` (HASH, S) + `Time_Stamp` (RANGE, N, **microseconds**
as of v4.1 — was milliseconds before). Per-player fields are
`teamN_PlayerM_<Field>`, not `Event_*`.

## 2. Interpret scan results correctly

- `Count=0, ScannedCount=0` → no base data in the window.
- `Count=0, ScannedCount>0` → filter didn't match anything. Fix the attribute
  name, value type (`S` vs `N`), or unit (ms vs µs) before re-running.
- `Count=N` without paging → trust it. `describe-table`'s `ItemCount` lags 6h+.

## 3. Quote filter values via `file://`, never inline

PowerShell mangles `--expression-attribute-values '{":x":{"S":"Yes"}}'`. Write
an ASCII temp file and reference it:

```powershell
'{":yes":{"S":"Yes"}}' | Out-File -Encoding ascii -NoNewline -FilePath ./tmp_eav.json
aws dynamodb scan --table-name events_rocket_league --profile mushin --region us-east-1 `
  --filter-expression "team0_Player1_Flip_Reset_Event = :yes" `
  --expression-attribute-values file://tmp_eav.json --output json > tmp_scan.json
```

## 4. Force UTF-8 for AWS CLI output

Python's CLI stack defaults to `charmap` on Windows, which crashes the moment a
player name contains non-ASCII (e.g. Turkish `ı`, U+0131). Set both env vars
**before** invoking `aws`, and read the resulting file with
`[System.IO.File]::ReadAllText`, not `Get-Content -Raw`:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8       = '1'
aws dynamodb scan ... > tmp_scan.json
$r = [System.IO.File]::ReadAllText((Resolve-Path ./tmp_scan.json)) | ConvertFrom-Json
```

## 5. Check `bakkesmod.log` before blaming detection

The plugin emits its own diagnostic channel (`%APPDATA%\bakkesmod\bakkesmod\bakkesmod.log`).
When DDB rows are missing, grep the log **first** — writer failures surface
there minutes before they'd ever show up as a downstream gap.

```powershell
Select-String -Path "$env:APPDATA\bakkesmod\bakkesmod\bakkesmod.log" `
  -Pattern '\[batch\] FAIL|\[batch\] DROPPED|ValidationException'
```

Canonical failure modes seen in this repo:

- `ValidationException - Provided list of item keys contains duplicates` →
  two poll ticks collided on `(Game_ID, Time_Stamp)`. Fixed in v4.1 by moving
  `Time_Stamp` to microseconds.
- `[batch] DROPPED N items after 5 retries` → retriable error hit the cap;
  check AWS status and throttling.

## 6. Cross-check log EMIT count vs DDB Yes count

For every flip-reset session, the two numbers should match within ±1:

- Log EMITs: `Select-String ... '\[flip-reset\] \S+ EMIT #\d+' | Measure-Object`
- DDB Yes rows: scan with filter `teamN_PlayerM_Flip_Reset_Event = :yes` and
  `Time_Stamp > :cutoff` where `:cutoff` is in **µs since epoch** (v4.1+).

A gap larger than 1 means either the writer is dropping batches (lesson 5) or
the detector is misattributing names across match boundaries (rare; check
`[flip-reset] match boundary` lines).
