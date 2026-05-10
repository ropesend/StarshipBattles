# pattern_audit

Pattern conformance & architecture drift audit. Validates the 8-layer dependency table against all imports, scans for protocol class usage, checks LOC ceiling, and provides the foundation for pattern adherence agent review.

## Usage

```powershell
python Tools/pattern_audit/pattern_audit.py        # full orchestrated scan
python Tools/pattern_audit/layer_validator.py --output PATH/TO/raw/  # layer check only
```

Outputs to `Reviews/results/YYYY-MM-DD_HHMMSS_pattern-audit/raw/`:
- `layer_violations.json` — every cross-layer forbidden import
- `loc_baseline.json` — LOC by section
- `file_size_violations.txt` — files over 500 LOC
- `protocol_registry.json` — Protocol classes found in codebase
- `manifest.json` — 4-shard file assignments

## Why a subdirectory

`Tools/README.md` requires every tool to have its own subdirectory and README.
