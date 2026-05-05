# PROJ-358: Battle Runner — Validate Spec Components, No Silent Drift

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-358` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-358 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Failing tests + validation error | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** 1
**Last Action:** Project scaffolded from realtime-combat tech-debt review finding #7.
**Next Action:** Run /claude-proj-start PROJ-358 to expand design + checklist.
**Blockers:** None

## Overview

`_apply_spec_components_to_ship` (`game/simulation/battle_runner.py:580-619`)
silently ignores `ShipSpec.components` entries that do not map to a
materialized Ship component. The docstring labels this "design drift" and
treats it as acceptable, masking invalid specs, stale designs, and
materialization bugs at the strategy↔combat boundary.

Per AGENTS.md "Root Cause Fixes": delete the silent path and surface a
domain validation error with `ship_id`, `component_id`, and `design_id`
context so failures are loud and actionable.

Source: realtime combat tech-debt review finding #7 (P2, hidden failure mode).

## Goals
- Spec component entries that do not map to the materialized ship raise a typed validation error before battle start
- Error message includes ship id, component id, instance index, and design id
- All currently-valid production specs remain accepted with bit-identical materialization
- Remove the "design drift" docstring justification and any tolerant code paths

## Scope
**In:**
- `game/simulation/battle_runner.py` — `_apply_spec_components_to_ship`, callers
- Domain validation error type (reuse existing `ValidationException` if appropriate)
- Tests under `tests/unit/simulation/battle_runner/`

**Out:**
- Broader spec typing rework (#10 / `BattleSpec` `object` fields — separate)
- Strategy spec compiler changes unless a real production drift surfaces
- Save-file migration paths (per AGENTS.md, old saves are disposable)

## Key Files
| Component | File Path |
|-----------|-----------|
| Drift site (root cause) | `game/simulation/battle_runner.py:580` |
| Spec types | `game/simulation/battle_spec.py` |
| Strategy compiler (caller) | `game/strategy/combat/spec_compiler.py` |
| Battle Setup compiler (caller) | `game/ui/screens/battle_setup/spec_compiler.py` |
| Tests (new) | `tests/unit/simulation/battle_runner/test_spec_component_validation.py` |

## Related Documents
- Review report finding #7: `Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/report.md`
- AGENTS.md § Root Cause Fixes

## Verification
- [ ] Failing test: spec with an unmapped component raises with ship/component/design context
- [ ] Failing test: HP from spec lands on the intended materialized component
- [ ] All existing valid specs still produce identical Ship state (golden compare)
- [ ] No silent-ignore branch remains in `_apply_spec_components_to_ship`
- [ ] `python Tools/test_sharded/test_sharded.py` passes
