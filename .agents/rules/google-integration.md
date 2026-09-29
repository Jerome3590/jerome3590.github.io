# Google Integration Guidelines

## 1. Secrets & Drive
- Google Drive OAuth client secret is stored at `C:\Projects\notebookLM_edits\secrets\gdrive_jerome_dixon90_client_secret.json` (or `C:\Projects\notebookLM-edit-content\secrets\...`).
- Never expose, print, or commit this file.

## 2. NotebookLM
- Automation repo: `C:\Projects\notebookLM-automation`
- Content repo: `C:\Projects\notebookLM_edits` (alias `notebookLM-edit-content`)
- Use local corpus-first approach prior to external API escalation.

## 3. Google Cloud / DataCloud
- Datacloud MCP servers (`notebooks`, `visualization`) are configured in global `mcp_config.json`.
- BigQuery, Cloud Storage, and GCP data tools are accessed via specialized GCP skills.
