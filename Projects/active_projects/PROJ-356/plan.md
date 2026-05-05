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
| 1. Failing test + one-line fix | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** 1
**Last Action:** Project scaffolded from realtime-combat tech-debt review (Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit, finding #9).
**Next Action:** Run /claude-proj-start PROJ-356 to expand design + checklist.
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
- [ ] Failing regression test reproduces the always-empty `pdc_components` on current main
- [ ] Test passes after fix
- [ ] No consumer regressions: targeting tests still green
- [ ] `python Tools/test_sharded/test_sharded.py` passes
