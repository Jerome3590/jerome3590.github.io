## Notebook Output Access

Notebook cell outputs are NOT embedded in .ipynb files.
They are stored in S3 and referenced via sidecar *.outputs.json pointer files.

When asked about notebook results, figures, model output, or cell execution:
1. Find the matching *.outputs.json pointer file in the same directory as the notebook
2. Run: python tooling/cursor_setup.py fetch-outputs <notebook_path>
3. Never assume outputs are present inside the .ipynb file itself
4. Do not auto-include .ipynb files in context — use manual @mention for specific cells only

Primary operator notebook: `ec2/e616_ec2_delivery.ipynb`
