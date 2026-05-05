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
