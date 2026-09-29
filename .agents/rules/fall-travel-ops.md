---
description: Fall travel booking, Gmail sync, dashboard deploy, and budget tracking process
alwaysApply: true
---

# Fall travel ops process

## Goal
Keep at least the next **4 weeks** of travel tasks confirmed. Open `todo` items whose phase overlaps that window show **TO DO** in bold red on the dashboard.

## Source of truth
1. Edit `data/trip-data.json` (phases, checklist, bookNext, hubs).
2. Mirror human checklists in root `README.md`.
3. Run `node build-app.js` to inject data into `website/app.js`.

## Gmail receipts + Gemini diff (no Enterprise Notebook)
- Shared auth: `scripts/gmail_auth.py` (notebookLM client secrets + repo `secrets/gmail_*_token.json`).
- Label scan: `scripts/fetch_gmail_receipts.py` — labels `Travel`, `Finance`, `Finance/Receipts`.
- Automation report: `scripts/gmail_gemini_trip_diff.py` — Gmail → Gemini API → advisory diff vs `data/trip-data.json` (does **not** auto-edit bookings).
  - Key: env `GEMINI_API_KEY` or `secrets/gemini_api_key.txt` from https://aistudio.google.com/apikey
  - Outputs (gitignored): `secrets/trip_diff_report.md` + `.json`
- On confirmed findings: update checklist statuses, conf #s, dates; mark rentals `n/a` when rideshare is the plan.
- Never commit `secrets/`, tokens, email dumps, or API keys (see `.gitignore`).
- Skip Gemini Notebook Enterprise for solo use; consumer Notebook is optional/manual.

## Dashboard refresh (when user asks to refresh / deploy)
```powershell
node build-app.js
aws s3 cp website/index.html s3://jerome-dixon.io/fall_travel/index.html --cache-control "public,max-age=300" --content-type "text/html"
aws s3 cp website/base.css   s3://jerome-dixon.io/fall_travel/base.css   --cache-control "public,max-age=300" --content-type "text/css"
aws s3 cp website/style.css  s3://jerome-dixon.io/fall_travel/style.css  --cache-control "public,max-age=300" --content-type "text/css"
aws s3 cp website/app.js     s3://jerome-dixon.io/fall_travel/app.js     --cache-control "public,max-age=60"  --content-type "application/javascript"
aws s3 cp data/trip-data.json s3://jerome-dixon.io/fall_travel/trip-data.json --cache-control "public,max-age=60" --content-type "application/json"
aws cloudfront create-invalidation --distribution-id E3MZK5HYTJ14P3 --paths "/fall_travel/*"
```
Live: https://jerome-dixon.io/fall_travel/

## Lodging / cost posture
- Principles: MWR primary · Hilton/Graduate backup · prefer **Airbnb** when hotel rates threaten the debt snowball.
- Cap guidance lives in `budget/travel-budget-impact.qmd` (+ `.canvas.tsx` copy). Update both when balances or bookings change; keep ledger file in sync.

## Git
- Commit/push only when asked. Prefer `gh auth setup-git` if HTTPS push hangs.
- Do not commit receipts that are email dumps; intentional PDFs in `receipts/` are OK.
