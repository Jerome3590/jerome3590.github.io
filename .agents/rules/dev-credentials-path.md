---
description: Local development AWS credentials path
alwaysApply: true
---

# Local AWS Credentials Path

- Local development AWS credential material is stored under `C:\Projects\credentials`.
- Do not read, print, summarize, copy, commit, or expose files from this directory unless the user explicitly asks for a specific credential-management action.
- Prefer passing this path to tooling as configuration rather than inspecting credential contents.
- For E616 GovCloud work, use AWS profile `421067336112_ProductTeamMemberAccess`.
- Set `AWS_SHARED_CREDENTIALS_FILE=/c/Projects/credentials` in Git Bash, or `AWS_SHARED_CREDENTIALS_FILE=C:\Projects\credentials` in Windows shells.
- Set both `AWS_REGION` and `AWS_DEFAULT_REGION` to `us-gov-west-1`; using commercial `us-east-1` can cause `InvalidClientTokenId` for this profile.
