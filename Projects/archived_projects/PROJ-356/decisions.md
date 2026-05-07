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

## Audit Remediation (OpenCode review of PROJ-356)

Review report: `Reviews/results/2026-05-05_055830_code_proj-356-review-ai-pdc-capability-cache-fix_req-req_20260505_055830_432529/`.

| Finding | Severity | Verdict | Rationale |
|---------|----------|---------|-----------|
| DC-001 | CRIT | Rejected | Already disclosed in the original PROJ-356 commit + decisions.md (consumer audit row): the `has_pdc`/`pdc_components` keys are intentionally populated for a future PDC-arc cache consumer; today no observable behavior change. The CRIT severity is overstated — the keys cost an O(n) PDC tag scan per enemy at most, and the regression suite locks in tag-based detection. PERF comment updated to mark the keys as future-consumer. |
| DC-002 | CRIT | Fixed | Removed `is_in_pdc_arc` from `controller.py` import tuple. Confirmed zero references in the controller; `target_evaluator.py` retains its own correct import. |
| DC-003 | MAJ | Deferred | A correct fix needs per-firing-ship PDC component caching (the firing ship is the one whose arcs/positions matter, but the current cache is keyed by candidate id). That is a structural change beyond audit-remediation scope; opening as a separate ticket avoids quietly enlarging PROJ-356. The deferral is now explicit in the PERF comment in `_score_and_sort_enemies`. |
| DC-004 | MAJ | Fixed | PERF comment in `_score_and_sort_enemies` rewritten to reflect that only `has_weapons` rules consume the cache today; `pdc_arc` rules still call `is_in_pdc_arc` directly. Cross-refs DC-003 deferral. |
| DC-005 | MAJ | Fixed | Removed the stale "Previously crashed in the cache-miss fallback; outer try/except silently dropped the missile from scoring" sentence from `_eval_has_weapons_rule` docstring. Replaced with an accurate description of the `is_combat_ship` TypeGuard route. |

