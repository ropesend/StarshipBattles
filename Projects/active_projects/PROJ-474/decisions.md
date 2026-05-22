# PROJ-474: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-21 | Project initialized | Starting point for Facade read-path: value/config UI-safe read-surface allowlist consolidation (follow-on from PROJ-472) |
| 2026-05-21 | Created + scoped as the **value/config allowlist** deferred tail of PROJ-472. **GATED on PROJ-472's import-guard landing.** | PROJ-472 caps scope at policy + guards + build-queue cluster + session consumers; the value/config allowlist consolidation is mostly doc + allowlist work and belongs in its own pass per consult §4. Do not start until `tests/static_guards/test_facade_read_path_imports_guard.py` and its UI-safe allowlist exist. |
