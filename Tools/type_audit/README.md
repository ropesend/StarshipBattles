# type_audit

Type safety & annotation quality audit. Two passes: mypy strict-mode analysis + AST-based annotation scanner for `-> Any` density, missing return types, `# type: ignore` usage, and `cast()` proliferation.

## Usage

```powershell
python Tools/type_audit/type_audit.py            # full scan
python Tools/type_audit/type_audit.py --skip-mypy  # AST scan only
```

Outputs to `Reviews/results/YYYY-MM-DD_HHMMSS_type-audit/raw/`:
- `mypy_report.json` — mypy strict-mode results
- `any_heatmap.json` — `-> Any` and `: Any` density by architectural layer
- `missing_returns.json` — public functions without return type annotation
- `type_ignore_sites.json` — every `# type: ignore` with context
- `cast_usage.json` — `cast()` call sites
- `manifest.json` — 4-shard file assignments

## Why a subdirectory

`Tools/README.md` requires every tool to have its own subdirectory and README.
