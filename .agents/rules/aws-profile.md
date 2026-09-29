---
description: Always use AWS profile `mushin` and region `us-east-1` for this project
alwaysApply: true
---

# AWS profile & region (project-wide)

This project uses exactly one AWS profile: **`mushin`** in **`us-east-1`**.

- CLI: always pass `--profile mushin`. Never omit it in committed scripts or docs.
- boto3: `boto3.Session(profile_name="mushin", region_name="us-east-1")` in deploy/admin scripts.
- C++ plugin: do NOT hardcode `"mushin"` — use the default credential provider chain. During dev the profile is picked up from `AWS_PROFILE=mushin` in the launcher environment.
- Verification: `aws sts get-caller-identity --profile mushin` before any infra-touching work.
- Never commit credentials, access keys, or session tokens.

Full rationale and patterns: [`.windsurf/rules/aws-profile-rules.md`](../../.windsurf/rules/aws-profile-rules.md).
