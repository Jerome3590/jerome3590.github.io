---
description: How to safely edit .ipynb files — the EditNotebook tool corrupts notebooks with existing outputs; use nbformat.write instead. Validate before AND after any notebook edit.
alwaysApply: true
---

# Notebook edit safety

## The trap

The Cursor agent's `EditNotebook` tool re-serializes the entire `.ipynb`
file on every call. That re-serializer **silently drops required schema
fields from existing outputs** — most commonly `"name": "stdout"` on
every stream output, occasionally other required properties. The
notebook still parses as JSON, but fails `nbformat.validate` and
**crashes Cursor's Jupyter renderer** with generic "cannot open
notebook" errors.

Historical hits in this repo: `papers/NEW_PAPER/validation_analysis.ipynb` has
41 stream outputs across 29 code cells; a single `EditNotebook` insert
of one markdown cell dropped `name` from all 41. The user experience is
"the notebook is crashing" with no obvious cause in the diff.

## Rule: never use `EditNotebook` on a notebook with outputs

Prefer these safe alternatives:

1. **Strip outputs first**, then edit:

   ```bash
   nbstripout papers/NEW_PAPER/validation_analysis.ipynb
   # then EditNotebook is safe
   ```

2. **Insert via `nbformat.write`** (preserves every field intact):

   ```python
   import nbformat
   from nbformat.v4 import new_markdown_cell  # or new_code_cell

   nb = nbformat.read(path, as_version=4)
   cell = new_markdown_cell("...")
   # nbformat_minor <= 4 forbids cell ids; new_*_cell always adds one
   if nb.nbformat_minor < 5:
       cell.pop("id", None)
   nb.cells.insert(idx, cell)
   nbformat.validate(nb)
   nbformat.write(nb, path)
   ```

## Rule: validate before AND after any notebook change

```bash
python -c "import nbformat; nb = nbformat.read('nb.ipynb', as_version=4); nbformat.validate(nb); print('OK cells=', len(nb.cells))"
```

For the specific `name`-on-stream corruption pattern:

```bash
python -c "import json; nb = json.load(open('nb.ipynb', encoding='utf-8')); n = sum(1 for c in nb['cells'] if c['cell_type']=='code' for o in c.get('outputs',[]) if o.get('output_type')=='stream' and 'name' not in o); print('broken_streams:', n)"
```

`broken_streams` must be `0`. Any positive count = the notebook was
silently corrupted by a re-serializer.

## Recovery when a notebook is already broken

The fingerprint in `git diff --stat`: **thousands of deletions and a
similar count of insertions** for what should have been a small logical
change (e.g. inserting one markdown cell). Example from this repo:

```text
papers/NEW_PAPER/validation_analysis.ipynb | 5523 +++++++++++++++++--------
1 file changed, 2760 insertions(+), 2763 deletions(-)
```

That is not "inserted one markdown cell." That is the whole notebook
re-serialized with fields dropped.

Recovery:

```bash
git checkout -- <nb.ipynb>           # revert
# Re-apply the intended change via the nbformat.write script pattern above.
# Verify: no stream outputs missing name, nbformat.validate passes.
```

## Version gotchas

- `nbformat_minor >= 5` **requires** each cell to have a unique `id`.
- `nbformat_minor <= 4` **forbids** the `id` field on cells.
- `nbformat.v4.new_markdown_cell` / `new_code_cell` always assign an
  `id`. Pop it (`cell.pop("id", None)`) before inserting into an older
  notebook, OR bump the notebook to `nbformat_minor = 5` and run
  `nbformat.validator.normalize(nb)` to assign ids to every pre-existing
  cell.

## Canonical source

Full guidance including the Chat-vs-Composer routing table and the
notebook-hang settings.json rules lives in
[`C:\Projects\project_utility_scripts\CURSOR_DEV_RULES.md`](../../../project_utility_scripts/CURSOR_DEV_RULES.md)
under **§ Notebook Optimization → Notebook edit safety**.
