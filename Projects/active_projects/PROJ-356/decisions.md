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
| 2026-05-04 | Consumer audit: cache `pdc_components` / `'has_pdc'` are unused at read time | Grep across `game/` shows the only writer is `controller._build_capabilities_cache`. `target_evaluator._eval_capability_rule` and `_eval_pdc_arc_rule` (the only readers of `ship_capabilities_cache`) consult `is_in_pdc_arc(ship, candidate)` directly, never the `has_pdc`/`pdc_components` keys. Conclusion: fixing the always-empty list is purely correctness for future consumers; **no observable AI behavior changes today**. The docstring at `target_evaluator.py:287` documents the cache shape but nothing reads those two keys. |
| 2026-05-04 | Existing fixture in `test_ai_capabilities_cache.py:65` was locking in the bug | The shared `create_mock_enemy` helper set `weapon.has_ability = MagicMock(return_value=has_pdc)`, which made the `has_ability('PDCAbility')` call return True for the test mock and silently pass even though no real component would. Updated the helper to mock `weapon.has_pdc_ability` instead. This both unblocks the existing tests and prevents a future regression that re-introduces the dead string check from passing. |
| 2026-05-04 | `test_controllable_adapter_edge_cases.py:231` left as-is | That test verifies the adapter delegates `get_components_by_ability(name, op_only)` to the underlying ship verbatim — the string `'PDCAbility'` is just a passthrough probe value, not a contract about controller PDC discovery. Renaming would obscure intent without improving coverage. |
