---
description: SSM Parameter Store is the canonical home for credentials, ARNs, and cross-service config in the surgical-ed-vr AWS account. Read from SSM at consumption time; never bake secrets into env vars, files, or command args.
alwaysApply: true
---

# SSM credential / config handoff pattern

Established in commits `c6e2fd2` (OIDC role → SSM + gh) and `5e7ab5f`
(direct-body fix) on 2026-07-13. See
[`migrations/aws_account_migration/gha_oidc/create_gha_oidc_s3_reader.sh`](../../migrations/aws_account_migration/gha_oidc/create_gha_oidc_s3_reader.sh)
for the reference implementation.

## When this applies

Follow this rule whenever a script, workflow, or agent action needs to:

- Distribute an **IAM role ARN, bucket name, or connection endpoint** to
  a consumer that lives outside AWS (GitHub Actions, local dev,
  cross-account pipeline).
- Retrieve a **GitHub PAT, API token, or OAuth client secret** for
  short-lived use inside a script.
- Bootstrap a new automation that will run in more than one place (local
  + EC2 + CI).

Do **not** follow this rule for values that are (a) already public
(the account ID, region, non-secret bucket names in READMEs are fine),
or (b) genuinely single-use and never re-run (e.g. a one-off migration
verification token you delete same-day).

## The pattern (one-line summary)

> **SSM Parameter Store is the source of truth. All other stores
> (GitHub Actions secrets, `.env` files, EC2 instance profile env vars,
> `gh auth` keyring) are mirrors written *from* SSM by an idempotent
> bootstrap script — never authored directly.**

Consequences:

1. Rotating a value = update in SSM, re-run bootstrap. Bootstrap
   re-mirrors to all downstream consumers.
2. Discovery = `aws ssm describe-parameters ... BeginsWith /<project>/`.
3. Audit trail = SSM parameter-history + CloudTrail
   `GetParameter` events.
4. Reproducibility = new laptop / new CI runner needs only AWS creds;
   everything else derives.

## Naming convention

Path structure: `/<project>/<component-or-workflow>/<resource>`.

Live examples in this account:

| Path | Type | Purpose |
|---|---|---|
| `/surgical-ed-vr/github-actions/s3-structure-refresh/role-arn` | `String` | OIDC assume-role ARN consumed by [`.github/workflows/s3-structure-refresh.yml`](../../.github/workflows/s3-structure-refresh.yml) |
| `/surgicaledvr/ec2/GITHUB_PAT` | `SecureString` | GitHub PAT used by EC2 clones + local `gh auth login --with-token` |

Rules:

- **Leading `/`** always. SSM requires fully-qualified names.
- **Project segment** matches the git repo name; use hyphens.
  (The prior `surgicaledvr` variant predates this convention — new
  params should use `/surgical-ed-vr/...`.)
- **Component segment** identifies the consumer subsystem
  (`github-actions`, `ec2`, `portal`, `analytics`).
- **Resource segment** is descriptive kebab-case
  (`role-arn`, `client-secret`, `bucket-name`).
- Tags on first-create: always attach
  `Project=surgical-ed-vr`, `Purpose=<what>`, plus one more scoping tag
  (`Workflow=<name>`, `Component=<name>`).

## Type discipline

- `String` — non-sensitive routing info (ARNs, bucket names, URLs,
  role names, region-scoped endpoints). Cheap; version-history visible
  in the console.
- `SecureString` — everything treated as a secret (tokens, private
  keys, passwords, DB connection strings with embedded creds). Always
  requires `--with-decryption` on read.
- `StringList` — reserved for genuine lists (e.g. allowlist of email
  addresses). Rare; prefer separate params.

If you're unsure: default to `SecureString`. Downgrade only after
confirming the value is safe to appear in plaintext in CloudTrail /
Parameter-Store UI.

## Bootstrap-script idempotency

Bootstrap scripts (see `create_gha_oidc_s3_reader.sh`) must:

1. **Create OR update** all resources they touch — never fail if the
   value already exists.
2. **Handle the SSM API quirk**: `--tags` and `--overwrite` cannot
   coexist in one `put-parameter` call. Use:
   ```bash
   if aws ssm get-parameter --name "$NAME" >/dev/null 2>&1; then
     aws ssm put-parameter --name "$NAME" --value "$VALUE" \
       --type String --overwrite --description "..."
   else
     aws ssm put-parameter --name "$NAME" --value "$VALUE" \
       --type String --description "..." \
       --tags "Key=Project,Value=surgical-ed-vr" \
              "Key=Purpose,Value=..." \
              "Key=Component,Value=..."
   fi
   ```
3. **Report status of every mirror** in the final banner so the runner
   knows what fired and what didn't. Example:
   ```
   Role ARN:            arn:aws:iam::.../SurgicalEdVr...
   SSM parameter:       /surgical-ed-vr/.../role-arn
   GitHub repo secret:  set via gh    |  not authed — set manually
   ```

## In-memory handoff (never persist secrets on disk)

When reading a `SecureString` to hand off to another tool:

```bash
# GOOD — token stays in the pipe, never appears in ps / env / disk
aws ssm get-parameter \
    --profile surgical_ed_vr \
    --name /surgicaledvr/ec2/GITHUB_PAT \
    --with-decryption \
    --query 'Parameter.Value' --output text \
  | gh auth login --with-token --hostname github.com
```

```bash
# BAD — token now visible via `ps auxe`, present in shell history,
# and captured by any error handler that echoes $env
export GITHUB_TOKEN=$(aws ssm get-parameter ... --output text)
```

```bash
# ALSO BAD — token lands in a file that survives the process
aws ssm get-parameter ... --output text > /tmp/pat.txt
gh auth login --with-token < /tmp/pat.txt
```

Same rule for other credential formats: pipe SSM → consumer, no
intermediate variable, no intermediate file.

## Cross-boundary mirroring (SSM → foreign secret store)

Some consumers can't read AWS SSM directly (GitHub Actions is the
canonical example — the workflow itself needs an ARN to *assume the
role* that would let it read SSM). For those, mirror the SSM value
into the consumer's native store from the same bootstrap script:

```bash
# Preferred pattern — direct --body <value>, no stdin pipe.
gh secret set "$SECRET_NAME" \
    --repo "$REPO_SLUG" \
    --body "$VALUE_FROM_SSM"
```

Rules for the mirror step:

1. **SSM remains canonical.** Never author values directly in the
   foreign store — always source them from SSM in-script.
2. **Bootstrap detects and reports the mirror path**: gh installed +
   authed → set via gh; gh installed not authed → print manual
   instructions; gh missing → print manual instructions. All three
   states are recoverable without editing the script.
3. **Consumer references the mirror by name**, not the SSM path:
   ```yaml
   # .github/workflows/s3-structure-refresh.yml
   - uses: aws-actions/configure-aws-credentials@v4
     with:
       role-to-assume: ${{ secrets.AWS_S3_STRUCTURE_READER_ROLE_ARN }}
   ```
   Repo secret name lives in the workflow; SSM path lives in the
   bootstrap script + this rule.

## Argument-passing safety — direct `--body <value>`, not stdin pipe

**Incident, 2026-07-13** ([run 29249157518](https://github.com/Jerome3590/surgical-ed-vr/actions/runs/29249157518)):

- Bootstrap used `printf '%s' "$ROLE_ARN" | gh secret set ... --body -`.
- On Windows git-bash, MSYS pipe translation appended a stray character
  (likely CR) to the piped bytes.
- `gh` accepted the value; `gh secret list` showed the secret as set;
  workflow retrieved it via `${{ secrets.... }}`.
- `aws-actions/configure-aws-credentials@v4` failed the ARN-format
  regex due to the trailing byte and reported the misleading
  `"Source Account ID is needed if the Role Name is provided and not
  the Role Arn."`
- Root cause was invisible without hex-dumping the secret from the
  workflow itself.

**Rule**: for any secret write via the `gh` / `aws` / `az` CLI, prefer
the direct-value form:

```bash
gh secret set NAME --repo owner/repo --body "$VALUE"
aws ssm put-parameter --name /path --value "$VALUE" --type SecureString
```

Reserve stdin pipes for values that legitimately can't fit on the
command line (multi-line PEM keys, gigantic blobs). If you must pipe,
use `printf '%s'` (no trailing newline), do the write, and then
**round-trip the value out via the consumer to verify byte-equality**
before considering the write successful.

The bootstrap script now enforces this — see the inline warning
comment above the `gh secret set` call.

## Discovery commands

```bash
# All surgical-ed-vr scoped params
aws ssm describe-parameters --profile surgical_ed_vr \
    --parameter-filters "Key=Name,Option=BeginsWith,Values=/surgical-ed-vr/"

# Any param whose name contains a substring
aws ssm describe-parameters --profile surgical_ed_vr \
    --parameter-filters "Key=Name,Option=Contains,Values=GITHUB"

# Read a single value (add --with-decryption for SecureString)
aws ssm get-parameter --profile surgical_ed_vr \
    --name /surgical-ed-vr/github-actions/s3-structure-refresh/role-arn \
    --query 'Parameter.Value' --output text

# Full version history for one param
aws ssm get-parameter-history --profile surgical_ed_vr \
    --name /surgical-ed-vr/github-actions/s3-structure-refresh/role-arn \
    --query 'Parameters[*].{Version:Version,Modified:LastModifiedDate,ModifiedBy:LastModifiedUser}'

# Who accessed a param recently (CloudTrail)
aws cloudtrail lookup-events --profile surgical_ed_vr \
    --lookup-attributes AttributeKey=EventName,AttributeValue=GetParameter \
    --max-results 20
```

## Reference implementations in this repo

- **Bootstrap that creates + mirrors an ARN**:
  [`migrations/aws_account_migration/gha_oidc/create_gha_oidc_s3_reader.sh`](../../migrations/aws_account_migration/gha_oidc/create_gha_oidc_s3_reader.sh)
- **Consumer via GitHub OIDC + repo secret**:
  [`.github/workflows/s3-structure-refresh.yml`](../../.github/workflows/s3-structure-refresh.yml)
  (`role-to-assume: ${{ secrets.AWS_S3_STRUCTURE_READER_ROLE_ARN }}`)
- **Consumer via in-memory pipe** (see prior turn's commit history):
  ```bash
  aws ssm get-parameter --with-decryption --name /surgicaledvr/ec2/GITHUB_PAT \
      --query 'Parameter.Value' --output text \
    | gh auth login --with-token
  ```
- **EC2-side SSM read policy**:
  [`migrations/aws_account_migration/ec2/config/ec2_analysis_ssm_github_policy.json`](../../migrations/aws_account_migration/ec2/config/ec2_analysis_ssm_github_policy.json)

## Related dev-rules

- [`ec2.mdc`](ec2.mdc) — EC2 instance-profile pattern (SSM read from
  the instance itself; no local creds needed).
- Lesson `§9.4-bis` in [`project_management/to_do.md`](../../project_management/to_do.md#9.4)
  — MSYS path-conversion hazard when reading POSIX-style SSM param
  names from Windows git-bash. `export MSYS_NO_PATHCONV=1` at script
  top handles it.
