---
description: Use SSM parameters for API keys and secret environment values
alwaysApply: true
---

# AWS SSM Secret Environment Values

- For Lambda/API-key work, store API keys, tokens, passwords, OAuth credentials, and other secret environment values in GovCloud AWS SSM Parameter Store as `SecureString` parameters.
- Do not put plaintext secrets directly into Lambda environment variables, Dockerfiles, runbooks, committed config, shell history, or chat-visible command output.
- Lambda environment variables may contain non-secret parameter names, for example `DRS_API_KEY_SSM_PARAM=/e616/dev/faa/drs-api-key`.
- Runtime code should resolve the parameter with `ssm:GetParameter` and `WithDecryption=True`, then pass the value only inside the running process.
- IAM permissions must be scoped to the exact parameter ARN when possible.
- Do not call APIs or commands that print secret values. Metadata checks such as `describe-parameters` are OK; value reads require an explicit user-approved secret-management action and must avoid exposing the value.

## FAA DRS and Gmail OAuth

- FAA DRS uses `/e616/dev/faa/drs-api-key` via `DRS_API_KEY_SSM_PARAM` and scoped `ssm:GetParameter`.
- Gmail OAuth follows the same SSM pattern. Store token/client JSON as SecureStrings under `/e616/dev/gmail/good/...` and `/e616/dev/gmail/bad/...`.
- Gmail lane mapping:
  - `vendorintellisense2@gmail.com`, `vendor`, and `good` select the `good` lane for vendor-specific alerts.
  - `vendorintellisense@gmail.com`, `supply_chain`, `supply-chain`, and `bad` select the `bad` lane for supply-chain alerts.
  - Gmail Lambda event selectors may use `email`, `gmail_account`, `lane`, or `source_type`; absence defaults to `good` / vendor-specific for backward compatibility.
- Local Gmail credential files under `C:/Projects/osi_supply_chain_risk/google_services/credentials` are approved only for explicit credential-management actions. Do not read, print, summarize, copy, commit, or expose them otherwise.
- Lambda images must remain non-secret. Runtime loaders should materialize only the selected Gmail lane credentials to lane-specific `/tmp` paths or pass values internally after SSM resolution.
- Refresh Gmail OAuth tokens with the repo-local helper, not global Python: `uv run --with google-auth-oauthlib python packages/e616-ops/scripts/refresh_gmail_oauth_token.py <good|bad> --no-browser`.
- For Gmail OAuth account switching, prefer the PowerShell incognito Chrome workaround: `Start-Process chrome -ArgumentList @('--incognito', '<full-url>')`. Preserve the full one-line URL and query string, including `prompt=select_account consent`, `login_hint`, and the localhost callback. If the incognito window does not surface, paste the complete generated URL manually into an existing browser/incognito window on the same machine; after approval, resume token save and SSM upload.
- Upload refreshed Gmail tokens to SSM with `uv run python packages/e616-ops/scripts/upload_gmail_token_ssm.py both` under the target GovCloud AWS environment.
- Never print token JSON, client secret JSON, email bodies, or message contents in logs, docs, or final responses. Validate Gmail by Lambda status/logs and S3 metadata/counts only.
