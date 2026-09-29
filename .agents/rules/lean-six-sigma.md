---
description: Lean Six Sigma — DMAIC, CTQs, and waste reduction for all dev and ops work
alwaysApply: true
---

# Lean Six Sigma (project standard)

Canonical ops doc: `docs/LSS_CONTROL_PLAN.md` · Metrics: `data_pipeline/src/lss_metrics.py` · `GET /metrics`

Apply DMAIC to **every** feature, fix, doc, and deploy — not only intake/Lambda work.

## Define (before building)

- Name the **customer** (buyer vs seller) and the **CTQ** (Critical to Quality) one sentence.
- Map the step in [CUSTOMER_WORKFLOW.md](docs/CUSTOMER_WORKFLOW.md): pay --> notify --> upload --> pipeline --> delivery.
- Prefer **one automated path**; manual seller steps are **exceptions** with SNS/alert when they fire.
- Reject scope that adds duplicate buyer touchpoints (email + Etsy + SES for the same event).

## Measure (make it observable)

- Every workflow change must be **measurable**: DynamoDB field, S3 artifact, structured log prefix, or LSS KPI.
- Use existing CTQs where they apply:
  - `auto_ses_rate` · `manual_action_pct` · `sale_to_upload_median_days` · `stale_awaiting_upload`
- Log for CloudWatch Insights: `[module] action key=value` (see `customer_email`, `intake_report`).
- Persist audit data (`intake-report.json`, `notify_status`, `delivery_email_sent_at`) — not only logs.

## Analyze (root cause, not symptoms)

- Classify failures: `no_email`, `failed`, `manual_required`, pipeline `error`, payment gate.
- Fix **upstream** (register, parse, idempotency) before adding seller workarounds.
- One email per intent (upload instructions vs delivery with URL + results) — no notification waste.

## Improve (reduce waste)

**Eliminate muda:**

| Waste | Avoid |
|-------|--------|
| Over-processing | Duplicate SNS, BCC, second SES, Etsy paste when auto succeeded |
| Waiting | Black-box upload with no report; seller guessing from zip |
| Defects | Silent drops (non-GPS photos) without `intake-report` + delivery summary |
| Motion | Manual copy-paste unless `notify_status` requires it |

- **Idempotent** automations (`buyer_email_sent_at`, `delivery_email_sent_at`).
- **Template fallback** when LLM/heavy deps fail — pipeline must still complete.
- Smallest diff that moves a CTQ; no unrelated refactors.

## Control (sustain)

- Thresholds: `lss_metrics.DEFAULT_THRESHOLDS` / env `LSS_STALE_AWAITING_DAYS`.
- After deploy: `production-smoke.ps1` · weekly `lss-metrics.ps1` · admin LSS banner.
- New env flags default **safe** (`SEND_DELIVERY_EMAIL` on; strict geotag off until tested).
- Docs: update `LSS_CONTROL_PLAN.md` or `CUSTOMER_EMAIL_DATA_PLAN.md` when CTQs or standard work change.

## Code review checklist (agent self-check)

1. Which CTQ does this improve?
2. What metric proves it worked?
3. Did we add or remove manual seller steps?
4. Is there exactly one buyer path for this event?
5. Failure mode: what does seller/customer see?

## Examples

```python
# BAD — unmeasured manual exception
send_email_to_jerome("something broke")

# GOOD — classified, idempotent, in KPIs
record_notify_result(order_id, {'sent': False, 'reason': 'no_email'})
```

```python
# BAD — second buyer email for same milestone
maybe_send_processing_summary(...)  # then delivery email

# GOOD — one delivery email with URL + intake report (CUSTOMER_EMAIL_DATA_PLAN.md)
maybe_send_delivery_email(cfg, dashboard_url, intake_report)
```
