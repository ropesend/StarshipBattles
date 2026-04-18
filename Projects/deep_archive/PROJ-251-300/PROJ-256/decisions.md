# PROJ-256 Decision Log

## DEC-001: Move ships/ under output/
**Date:** 2026-04-07
**Decision:** Ship design JSON files move from `ships/` (project root) to `output/ships/`.
**Rationale:** All other user-generated runtime data (saves, screenshots, logs, settings, races) already lives under `output/`. The `output/` directory is gitignored, which is correct for user data — ship designs like "crap custom.json" should not be in version control. This makes `ships/` consistent with every other user-data directory.
**Impact:** Users' existing ship files need to be moved once. ShipIO file dialog will default to the new location.

## DEC-002: Default parameter pattern for file paths
**Date:** 2026-04-07
**Decision:** Replace `def foo(path="data/x.json")` with `def foo(path=None)` + `path = path or Paths.X` inside the body.
**Rationale:** Python evaluates default parameter values at import time. If `Paths` hasn't been imported yet, or if the constant is computed dynamically, a class-attribute default can fail. Using `None` + body assignment is the standard Python pattern for mutable/computed defaults and avoids import ordering surprises.
**Impact:** Callers passing explicit paths are unaffected. Callers relying on the default get identical behavior.

## DEC-003: Test files out of scope
**Date:** 2026-04-07
**Decision:** Test files (`tests/`, `test_framework/`, `simulation_tests/`) are excluded from this refactoring.
**Rationale:** Tests legitimately use paths relative to their own data directories (`tests/data/ships/`, `simulation_tests/data/`). These are not the same as `Paths.SHIPS_DIR` — they point to test-specific fixture data. Forcing them through `Paths` would create unnecessary coupling and make test data harder to relocate.
**Impact:** None — test paths remain as-is.

## DEC-004: Scripts with CLI args out of scope
**Date:** 2026-04-07
**Decision:** Scripts that accept `--output` CLI arguments (e.g., `inspect_galaxy.py`, `galaxy_screenshot.py`) are excluded.
**Rationale:** These scripts write to user-specified directories via CLI args. Their defaults are reasonable (`./output/galaxy_inspect`) and are not the same as the game's runtime `Paths.OUTPUT_DIR`. Centralizing them would over-constrain the scripts.
**Impact:** None.
