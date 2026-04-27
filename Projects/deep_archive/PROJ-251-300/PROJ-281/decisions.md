# PROJ-281: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Project initialized | Starting point for BattleScreen Legacy Fallback Removal |
| 2026-04-17 | Approach: migrate tests, then delete shim + fallback (Option A) | User chose "Migrate then delete (Recommended)". Single PR, no transition state. Follows codebase's eradicate-old-systems policy. Rejected: delete-first-fix-reactively (messier); keep-shim-replace-fallback-only (kept dual paths against policy) |
| 2026-04-17 | One PR (no incremental delivery) | Migration + deletion together means no orphaned partial state in `main`. Test churn happens once |
| 2026-04-17 | New helper location: `tests/helpers/battle_spec_helpers.py` | Co-locates with other test infrastructure. Phase 1 confirms whether this directory exists or whether helpers live elsewhere |
| 2026-04-17 | Sequencing: AFTER PROJ-280 | Combat Lab cluster (PROJ-278/279/280) closes first. UI cleanup cluster opens with this project, closes with PROJ-282. Cleaner cognitive grouping than interleaving |
| 2026-04-17 | Helper offers a `make_minimal_spec` builder; defer optional `make_minimal_spec_and_run` headless variant | Start with the minimum API. Add the headless variant only if migration shows tests want to skip controller setup |
