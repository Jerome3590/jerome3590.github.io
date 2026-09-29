---
description: Deploy all AWS Lambdas as ECR container images (never zip)
globs: data_pipeline/**/*
alwaysApply: true
---

# Lambda deploy — ECR only

This project **always** ships Lambdas as **Docker container images** pushed to **ECR**. Do not add or restore zip-based `aws lambda update-function-code` with `.zip` artifacts.

## Standard workflow

1. **Dockerfile** per function under `data_pipeline/lambdas/<name>/` (copies from `data_pipeline/src/`).
2. **ECR repo** — `data_pipeline/infra/setup-lambda-ecr.ps1` (idempotent).
3. **Deploy** — `data_pipeline/infra/deploy-lambda-ecr.ps1` via the service script:
   - `deploy.ps1` — `mushin-pipeline`
   - `deploy-email-intake.ps1` — `mushin-email-intake` (+ SES invoke permission)
   - `deploy-upload-api.ps1` — `mushin-upload-api`
   - `deploy-all-lambdas.ps1` — all of the above

Build uses `Push-Location` + `docker build -f <Dockerfile> .` from `data_pipeline/` (Windows-safe).

## If a function is still `PackageType: Zip`

Run the matching `deploy-*.ps1` script — it **migrates** Zip --> Image (brief downtime). Do not hand-upload zip bundles.

## After code changes

Rebuild and push the image, then update Lambda (`deploy-*` without `-SkipBuild` unless the image was just built locally and you only need push/update).
