## EC2 workflow

Primary path: **SSH into the shared Spot instance, git clone into the projects dir, run delivery with NVMe I/O.**

1. `ec2/spot_manager.ipynb` — start Spot + SES login email + SSH
2. `ec2/e616_ec2_delivery.ipynb` — clone → bootstrap → `--workers` delivery → pull
3. Stop from `spot_manager.ipynb` when idle

- Helpers: `ec2/scripts/ec2_session.py`
- Config: `ec2/config.yaml` (`project_slug: notebooklm-automation`)
- Code: `/home/pgx-3874/<clone_repo>/` (git clone; basename of `git_repo_url`)
- Video I/O: `/mnt/data/<project_slug>/` (NVMe)
- Local Jupyter only (no Remote-SSH notebook IDE)

## Spot capacity / AZ failover

- Default compute is **Spot**. Keep **at least two Spot analysis instances
  in different AZs**. If an AZ is lost or a box is retired, stand up a
  replacement Spot box in another AZ before relying on on-demand.
- On `InsufficientInstanceCapacity` or a Spot capacity fail for the
  primary: try the other-AZ Spot box(es) next. On-demand is last resort
  only. Path: primary Spot --> other-AZ Spot --> on-demand last resort.
- Document this project's instance IDs and failover order in this rule
  when they exist. Do not treat surgical-ed-vr instance IDs as this
  project's primary boxes.
- Never terminate Mushin `i-0c968462d413a1028`.
- ASCII arrows only: `-->`.
