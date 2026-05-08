# legacy_audit

Legacy code, alias, shim, deprecation marker, and migration code audit. Scans every `.py` file under `game/` for residue of old systems that should have been removed: module aliases, re-export shims, deprecation markers, wrapper delegates, name-pair drift, save migration code, superseded patterns, `TYPE_CHECKING`-only re-exports, and partial Protocol implementations.

## Usage

```powershell
python Tools/legacy_audit/legacy_audit.py
```

Outputs to `Reviews/results/YYYY-MM-DD_HHMMSS_legacy-audit/raw/`:

- `module_aliases.json` — top-level `OldName = NewName` aliases
- `init_reexports.json` — `__init__.py` star-imports / `as`-aliasing imports
- `deprecation_markers.json` — `# DEPRECATED`, `# LEGACY`, `# TODO remove`, `@deprecated`, `DeprecationWarning(...)`, etc.
- `wrapper_delegates.json` — single-statement `return other(...)` functions
- `name_pair_drift.json` — `LegacyX`/`OldX`/`XV1`/`XV2`/`XOld`/`XLegacy`/`_X` co-existing with `X`, plus `XManager`/`XService` overlap pairs
- `save_migration_code.json` — `migrate_*`, `convert_legacy_*`, `from_vN_to_vM`, `*_migration.py`, `*_compat.py`
- `superseded_pattern_uses.json` — `superseded_by` patterns (from latest pattern-audit `patterns_toc.json` if present, else parsed from `docs/02_PATTERNS.md`)
- `type_checking_only_reexports.json` — names imported under `if TYPE_CHECKING:` AND re-exported via `__all__` or top-level alias
- `optional_protocol_methods.json` — classes that partially match a `Protocol` method set (legacy implementations missing newer methods)
- `manifest.json` — 4-shard file assignments (mirrors `Tools/audit_shrink/manifest.py`)

For each detector, a global JSON plus per-shard filtered copies (`<name>_{01..04}.json`) are written so shard agents only consume their own findings.

After the run, an entry under `audit_name="legacy"` is appended to `Reviews/results/legacy_history.json` via `Tools/_audit_common/run_tracker.py`.

## Why a subdirectory

`Tools/README.md` requires every tool to have its own subdirectory and README.
