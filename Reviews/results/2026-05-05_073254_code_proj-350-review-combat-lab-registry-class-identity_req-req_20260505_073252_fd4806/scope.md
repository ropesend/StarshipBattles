# Review Scope: PROJ-350 Combat Lab Registry Class Identity Fix
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_073252_fd4806
**Scope:**
- `combat_lab/registry.py` (changed to use `importlib.import_module`)
- `combat_lab/spec_compiler.py` (crash-site reference only)
- `combat_lab/scenarios/templates.py` (the previously-duplicated module)
- `tests/unit/combat_lab/` (new regression test for class-identity invariance)
- `Projects/active_projects/PROJ-350/decisions.md`
- Commit: `d555e8bd1`
**Instructions:**
- Verify the regression test would have failed on the previous code (uses bespoke loader)
- Confirm there are no remaining `spec_from_file_location` / `module_from_spec` calls in the registry path
- Note: `combat_lab/runner.py:271-292` is a separate explicit-path CLI loader (out of scope) — but verify it does not exhibit the same class-identity problem
- Audit other places in the codebase using `spec_from_file_location` (mods, plugins, scenario discovery)
- Check the regression test really pins class identity (asserts `isinstance` survives registry discovery)
**Context:**
Already-implemented project (committed 2026-05-04 at `d555e8bd1`). Plan status was 'Complete (awaiting user verification)'. Audit only.
**Review mode:** standard
**Limitations:** Runner CLI loader (`combat_lab/runner.py:271-292`) was explicitly scoped out per decisions.md. Codebase-wide audit covers all other `spec_from_file_location` usages.
