# PROJ-356: AI PDC Capability Cache — Replace Non-Existent Class Check

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-356` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-356 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Failing test + one-line fix | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** 1 (complete)
**Last Action:** Implemented one-line fix in `game/ai/controller.py:229` (tag-based `has_pdc_ability()`); added regression test `tests/unit/ai/test_capability_cache_pdc.py` (4 tests, RED on main → GREEN after fix); updated `test_ai_capabilities_cache.py` fixture that was silently locking in the dead path. Cache consumer audit: `pdc_components`/`'has_pdc'` are dead at read time today — `target_evaluator` consults `is_in_pdc_arc(ship, candidate)` directly, so no observable AI behavior changes (correctness fix for future consumers). AI tests: 386 passed. AI + combat tests: 736 passed. Sharded suite has 7–33 pre-existing failures in fleet aura / battle outcome layers unrelated to PROJ-356 (in-flight AuraProvider signature work visible in `git status`).
**Next Action:** Complete (awaiting user verification).
**Blockers:** None

## Overview

Fix a silent correctness bug in `game/ai/controller.py:229`. The PDC capability
cache filters weapons via `w.has_ability('PDCAbility')`, but no `PDCAbility`
class exists anywhere in the codebase — PDC is tag-based and exposed via
`Component.has_pdc_ability()` (PROJ-241). The cache's `pdc_components` list is
therefore always empty. Any future targeting rule that consumes
`ship_capabilities_cache['pdc_components']` will see no PDC weapons.

Source: realtime combat tech-debt review finding #9 (P1).

## Goals
- Replace the dead string check with `comp.has_pdc_ability()` on the component path used by the cache
- Add a regression test that locks in tag-based PDC detection
- Confirm no consumer of the cache silently relied on the always-empty list

## Scope
**In:**
- `game/ai/controller.py` — capability cache PDC filter
- New regression test under `tests/unit/ai/`
- Audit consumers of `ship_capabilities_cache['pdc_components']` / `'has_pdc'`

**Out:**
- Broader AI controller refactor or behavior/policy registry injection (mentioned in the review's recommendation but separate scope)
- Targeting policy rewrites

## Key Files
| Component | File Path |
|-----------|-----------|
| Capability cache (bug site) | `game/ai/controller.py:229` |
| Tag-based PDC detection | `game/simulation/components/component.py:191` |
| Cache consumer (verify) | `game/simulation/combat/targeting_system.py` |
| Regression test (new) | `tests/unit/ai/test_capability_cache_pdc.py` |

## Related Documents
- Review report: `Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/report.md` (finding #9)

## Verification
- [x] Failing regression test reproduces the always-empty `pdc_components` on current main
- [x] Test passes after fix
- [x] No consumer regressions: targeting tests still green (tests/unit/ai + tests/unit/simulation/combat: 736 passed)
- [x] `python Tools/test_sharded/test_sharded.py` passes for AI/combat scope; pre-existing fleet-aura / battle-outcome failures are unrelated (see Phase 1 Task 1.5 notes and decisions.md)
