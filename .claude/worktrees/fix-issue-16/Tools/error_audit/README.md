# error_audit

Error handling & robustness audit. Scans every .py file under `game/` for exception handling quality, resource cleanup, and error propagation patterns.

## Usage

```powershell
python Tools/error_audit/error_audit.py
```

Outputs to `Reviews/results/YYYY-MM-DD_HHMMSS_error-audit/raw/`:
- `broad_except_sites.json` — `except Exception` without `# Intentional` comment
- `bare_except_sites.json` — bare `except:` clauses
- `json_bypass_sites.json` — `json.load`/`dump` not routed through `json_utils`
- `raise_generic_sites.json` — `raise Exception(...)` instead of domain-specific
- `print_debug_sites.json` — `traceback.print_exc()` / `print()` diagnostics
- `manifest.json` — 4-shard file assignments for Phase 2 agent review

## Why a subdirectory

`Tools/README.md` requires every tool to have its own subdirectory and README.
