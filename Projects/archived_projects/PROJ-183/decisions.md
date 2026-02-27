# PROJ-183: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Independent audit of PROJ-175 found remaining cleanup items |
| 2026-02-24 | Exclude game/app.py from traceback cleanup | Top-level crash handler at line 714-715 needs `traceback.format_exc()` for display in the error dialog, not just logging |
| 2026-02-24 | Exclude test files from json.load/dump scope | PROJ-175 explicitly scoped test fixtures out: "Out: tests/ and simulation_tests/ logging patterns" |
| 2026-02-24 | Exclude archived docs from cleanup | Files in `docs/refactoring/completed/` are historical artifacts not used as active templates |
| 2026-02-24 | Exclude warnings.warn() in registry.py | `warnings.warn()` with `DeprecationWarning` is the correct Python pattern for API deprecations - not a logging concern |
| 2026-02-24 | Use logger.warning() for error-at-INFO fixes | Validation errors and blueprint load failures are recoverable, so WARNING is appropriate (not ERROR) |
| 2026-02-24 | Use logger.exception() not logger.error(exc_info=True) | `logger.exception()` is more concise and is the standard idiom; functionally equivalent to `logger.error(msg, exc_info=True)` |
