# docs_audit

Documentation freshness & accuracy audit. Cross-references all `docs/` file references against the live filesystem and project index. Finds dead references, stale PROJ mentions, undocumented modules, and stale "Last verified" timestamps.

## Usage

```powershell
python Tools/docs_audit/docs_audit.py
```

Outputs to `Reviews/results/YYYY-MM-DD_HHMMSS_docs-audit/raw/`:
- `doc_file_refs.json` — every `game/*` path in docs validated against filesystem
- `stale_proj_refs.json` — PROJ references cross-referenced against projects_index.md
- `doc_staleness.json` — "Last verified" timestamps with staleness scores
- `undocumented_modules.json` — production modules > 50 LOC with no doc mention
- `doc_inventory.json` — full doc file listing with headings for agent sharding

## Why a subdirectory

`Tools/README.md` requires every tool to have its own subdirectory and README.
