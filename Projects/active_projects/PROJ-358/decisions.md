# PROJ-358: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project ID = PROJ-358 | User-directed sequence start at 356; this is #3 of 5. |
| 2026-05-04 | Project created from realtime-combat tech-debt review | Review finding #7 (P2 hidden-failure): `_apply_spec_components_to_ship` silently drops unmapped components. |
| 2026-05-04 | Manual scaffolding (not via `create_project.py`) | Folder pre-existed with `plan.md`. Mirrored canonical templates from `Projects/scripts/create_project.py` and `Reviews/scripts/review_to_project.py`. |
| 2026-05-04 | Opted into 03c phase-aware execution | Per `.claude/skills/claude-proj-start/SKILL.md` Phase D. |
| 2026-05-04 | Single-phase project | One narrow surface (one function); the validation, error-type choice, and caller contract live together. |
| 2026-05-04 | Reuse `ValidationException` | Per AGENTS.md, prefer existing registries/services/protocols/helpers. Adding a new exception type is unwarranted. |
| 2026-05-04 | Error code `V002 SCHEMA_VALIDATION_ERROR` | Drift is structural (the spec describes a layout the design doesn't have); fits "structural validation error (missing fields, invalid data structure)" closer than V001 generic or V003 missing-entity. |
| 2026-05-04 | Report only the first unmapped key | Keeps the error message focused. The first drift typically points at the root cause (stale design, wrong design_id, compiler bug); subsequent drifts are usually downstream symptoms. |
| 2026-05-04 | Two-pass design (apply, then validate) | Lets the valid-case materialization remain bit-identical (single forward walk through layers). Validation is a `set` diff afterwards — O(n) extra work, no behavioral change for valid specs. |
| 2026-05-04 | Audit found NO existing test fixture relying on silent absorb | All 8 `ComponentStateSpec(...)` usages in tests/ construct entries that map cleanly to their fixture designs. None encoded the bug. |
