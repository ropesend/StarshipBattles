# PROJ-356: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project ID = PROJ-356 | User-directed: PROJ-355 and below are taken; start sequence at 356. |
| 2026-05-04 | Project created from realtime-combat tech-debt review | Review finding #9 (P1 correctness): AI capability cache calls `has_ability('PDCAbility')` against a non-existent class; PDC is tag-based via `has_pdc_ability()`. |
| 2026-05-04 | Manual scaffolding (not via `create_project.py`) | Folder pre-existed with `plan.md` from initial scaffold. Followed canonical templates (design/decisions/manifest/phase-checklist) verbatim from `Projects/scripts/create_project.py` and `Reviews/scripts/review_to_project.py`. |
| 2026-05-04 | Opted into 03c phase-aware execution | Per `.claude/skills/claude-proj-start/SKILL.md` Phase D, default for new projects. |
| 2026-05-04 | Single-phase project | Bug surface is one line plus one test plus one consumer audit; further phasing is overhead. |
