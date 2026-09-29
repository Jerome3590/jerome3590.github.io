---
description: EC2 workflow, Spot AZ failover, and local/remote compute guidance for surgical-ed-vr
alwaysApply: false
---

# EC2 Remote Workflow

- **Platform boundary:** local development is Windows using PowerShell, WSL, or
  Git Bash; production analysis runs on Amazon Linux EC2. Paths, key permissions,
  Python activation, and AWS credential sources are environment-specific.
- Source `dev_setup/scripts/detect_runtime_env.sh` in cross-platform Bash scripts.
  It detects `windows-wsl`, `windows-git-bash`, `amazon-linux-ec2`, or generic
  `linux` and exports `SEDVR_*` defaults. Explicit caller overrides win. Inspect
  with `bash dev_setup/scripts/detect_runtime_env.sh --check`.
- Local Cursor terminals use AWS profile `mushin` from `.vscode/settings.json`; EC2 should normally use its IAM instance profile.
- Long notebook, visualization, or data preparation runs should execute on EC2 or the configured compute environment, not in the local editor.
- Use documented S3 buckets and existing helper scripts instead of hard-coded local paths.
- Before enabling the Jupyter post-save hook, verify `python dev_setup/cursor_setup.py status` works in the EC2 checkout.

## Instances

Profile `surgical_ed_vr`, region `us-east-1`. Default compute is **Spot**.
**Launch from-scratch each session** (stock Amazon Linux 2 + bootstrap), same
pattern as pgx `launch_pgx_session.sh`. Do not keep a session AMI or extra
197 GB roots. `DeleteOnTermination=true`. After the run, cancel the Spot
request and terminate (`cancel_analysis_session.sh`). A leftover persistent
request will revive the box on the next capacity wobble.

```bash
AWS_PROFILE=surgical_ed_vr bash migrations/aws_account_migration/ec2/launch_analysis_session.sh
bash migrations/aws_account_migration/ec2/clone_and_setup_sedvr.sh
INSTANCE_ID=i-xxxxxxxx bash migrations/aws_account_migration/ec2/cancel_analysis_session.sh
```

Failover (other AZ before on-demand):

1. Default: us-east-1d `subnet-03402b19ac5249894`
2. Other-AZ Spot: `AVAILABILITY_ZONE=us-east-1a SUBNET_ID=subnet-07630cd444b5994e8`
3. Last resort: on-demand. Do not keep warm failover roots.

Stopped AMI box `i-07dbb05da43df1cad` is leftover from the old path; do not
start it for new work. Never terminate Mushin `i-0c968462d413a1028`.

- Public IP changes on stop/start -- refresh with `bash
  dev_setup/scripts/refresh_ec2_ssh_host.sh` (or `TARGET_INSTANCE_ID=... ` for a
  specific box). Override the launcher with `EC2_INSTANCE_ID=<id>` on
  `papers/NEW_PAPER/scripts/run_full_analysis_and_publish.sh`.

## Idle shutdown (45 minutes)

CloudWatch alarm `sedvr-idle-stop-<instance-id>`: **CPU < 5% for 45 minutes**
then `arn:aws:automate:us-east-1:ec2:stop`. No Lambda. EventBridge (old
CloudWatch Events) still needs a target to stop EC2; the native stop action
is on CloudWatch **Alarms**.

- Deploy: `AWS_PROFILE=surgical_ed_vr bash dev_setup/scripts/install_ec2_idle_shutdown.sh`
- Hold: `aws cloudwatch disable-alarm-actions --alarm-names sedvr-idle-stop-<id>`
- Never alarm Mushin `i-0c968462d413a1028`
- Do not leave analysis instances running after work is done.

## Spot capacity / AZ failover

- Default compute is Spot. Do not keep warm roots in extra AZs. If the
  session AZ has no capacity, launch a new from-scratch session in another AZ,
  then on-demand.
- On `InsufficientInstanceCapacity` for us-east-1d: launch other-AZ Spot,
  then on-demand last resort. Path: stock AL2 in 1d --> stock AL2 in 1a
  --> on-demand last resort.
- Never terminate Mushin `i-0c968462d413a1028`.
- Launcher override: `EC2_INSTANCE_ID=<id>` on
  `papers/NEW_PAPER/scripts/run_full_analysis_and_publish.sh`.

## SSH from Windows (WSL vs git-bash) — key path and permissions

The PEM lives on the Windows `C:` drive. The mount point **differs by shell**:

- **git-bash:** `/c/Projects/mushin_pgx.pem`
- **WSL:** `/mnt/c/Projects/mushin_pgx.pem` (there is no `/c` under WSL)

Rules for any script/command that SSHes to EC2 with this key:

1. **Auto-detect the mount.** Probe `/c/...`, then `/mnt/c/...`, then
   `$HOME/.ssh/...`; use the first that exists. Never hard-code one mount.
2. **Force `0600` on the key.** OpenSSH refuses group/world-readable private keys.
   WSL's DrvFs reports `/mnt/c` files as mode `0444` (`Permissions 0444 ... are too
   open ... This private key will be ignored` --> `Permission denied (publickey)`), and
   `chmod` on `/mnt/c` usually does not stick. Copy to a Linux-fs temp and tighten:
   ```bash
   K="$(mktemp)"; cp "$SRC_KEY" "$K"; chmod 600 "$K"; trap 'rm -f "$K"' EXIT
   ssh -i "$K" -o StrictHostKeyChecking=accept-new pgx3874@<ip> '...'
   ```
3. **Diagnosis:** if `Test-NetConnection <ip> -Port 22` succeeds but ssh still says
   `Permission denied (publickey)`, the SG is fine (it is `0.0.0.0/0` on 22) — suspect
   the key **path** or **perms**, not networking.

Both fixes are implemented through `detect_runtime_env.sh` and
`run_full_analysis_and_publish.sh` (`SEDVR_SSH_KEY_SOURCE` + `SECURE_KEY` 0600
temp copy). See
[`project_management/LESSONS_LEARNED.md`](../../project_management/LESSONS_LEARNED.md).

## EC2 Python path — activate `~/jupyter-env` for non-interactive SSH

- The analysis interpreter is the venv **`~/jupyter-env/bin/python`** (Python 3.11.9;
  has boto3, dtaidistance, sklearn, scipy, pandas, nbformat).
- It is **not** on PATH for a non-interactive `ssh host "..."` command (nor a login
  `-l` shell) — `.bashrc` does not activate it there. Repo scripts
  (`run_ec2_workflow.sh`, `publish_notebook_ec2.sh`, `bootstrap.sh`) call bare
  `python`, so a remote command that does not activate the venv fails with
  `python: command not found`.
- **Rule:** any remote command that runs `python` must first
  `source ~/jupyter-env/bin/activate` (or call `~/jupyter-env/bin/python`
  explicitly). Interactive Remote-SSH terminals activate it automatically, which is
  why the bug only appears in scripted ssh. The environment helper exports
  `SEDVR_REMOTE_PYENV_ACTIVATE`. See
  [`project_management/LESSONS_LEARNED.md`](../../project_management/LESSONS_LEARNED.md).

## Shell script line endings

- Keep `*.sh` as **LF**. CRLF makes bash read a trailing `\r` and fail with
  `set: pipefail: invalid option name` / `$'\r': command not found`. Cursor's `Write`
  tool can emit CRLF on Windows — normalize with `sed -i 's/\r$//' file.sh` (repo) or
  run read-only via `tr -d '\015' < file.sh | bash`. This is unrelated to the
  intermittent Cursor "no exit status" terminal glitch. See
  [`project_management/LESSONS_LEARNED.md`](../../project_management/LESSONS_LEARNED.md).
- Cursor workspace settings enforce `"files.eol": "\n"` for both Windows and
  Remote-SSH. Do not switch repository files to CRLF on Windows.
- Terminal Enter is a separate PTY concern: terminals normally send CR and the
  Linux terminal driver maps it appropriately. Do not add `stty` or keybinding
  workarounds to “fix CRLF” unless a raw-mode application is demonstrably broken.

## Platform-specific Cursor terminal profiles

Workspace `.vscode/settings.json` deliberately overrides terminal profiles by
platform:

- Windows client: `terminal.integrated.defaultProfile.windows = WSL`
- Remote Amazon Linux: `terminal.integrated.defaultProfile.linux = bash`
- Automation: `wsl.exe /bin/bash` on Windows; `/bin/bash -l` on Linux

This override is required because a user-level
`terminal.integrated.defaultProfile.linux = WSL` is valid-looking on the Windows
client but invalid in a Remote-SSH EC2 window, where no `WSL` profile exists.
