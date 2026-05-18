# PROJ-402: Tier 1 B-03 — `SimulationBattleResolver` catch `ValidationException`

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Widen catch tuple + restore originally-required test | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09
**Active Phase:** Closeout
**Last Action:** Phase 1 complete — catch tuple widened to `(SimulationException, ValidationException)`; canonical regression test restored (`test_validation_exception_wrapped_with_battle_context`); existing `SimulationException` coverage retained.
**Next Action:** Awaiting user verification.
**Blockers:** None

## Overview
PROJ-381 Phase 3 Task 3.10 was supposed to ensure `SimulationBattleResolver` preserves battle context when `run_battle` raises `ValidationException`. The implementation only catches `SimulationException`; the regression test was substituted to use a custom `SimulationException` instead of the originally-required `ValidationException`. `run_battle` (`battle_runner.py:640-652`) does raise `ValidationException` for invalid `ShipSpec.components`, so a real failure-path bypasses the wrapper and propagates with empty context, defeating the goal of B-6 in PROJ-381.

## Goals
- Widen the `simulation_adapter.SimulationBattleResolver` catch tuple to `(SimulationException, ValidationException)`.
- Replace the substituted regression test with one that injects `ValidationException` (the originally-required case) and asserts the wrapped `BattleResolutionError` carries `fleet_ids`, `empire_ids`, `hex_coord`.

## Scope
**In:**
- `game/strategy/adapters/simulation_adapter.py` — widen catch tuple.
- `tests/unit/strategy/adapters/test_simulation_adapter.py` — replace the substituted test with the canonical one.

**Out:**
- The C-02 facade unit test (separate Tier 4 work).
- The C-03 raw `EnginePhaseError` defensive catch in the UI (deferred MAJ-014 — see Tier 5 PROJ-409).

## Key Files
| Component | File Path |
|-----------|-----------|
| Wrapper | `game/strategy/adapters/simulation_adapter.py` |
| Source of `ValidationException` | `game/simulation/battle_runner.py` (read-only) |
| Test | `tests/unit/strategy/adapters/test_simulation_adapter.py` |

## Source Evidence (REMEDIATION_PLAN B-03)
- `game/strategy/adapters/simulation_adapter.py:292-300` — only catches `SimulationException`.
- `game/simulation/battle_runner.py:640-652` — `run_battle` raises `ValidationException` for invalid `ShipSpec.components`.
- `tests/unit/strategy/adapters/test_simulation_adapter.py:391-404` — current test injects custom `SimulationException`, not the originally-required `ValidationException`.
- PROJ-381 review (`Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-381_report.md`)

## Verification
- [x] Phase 1 checklist complete
- [x] New `ValidationException`-injection regression test passes
- [x] Existing `SimulationException`-injection test still passes (both cases must be covered)
- [x] `pytest tests/unit/strategy/adapters/test_simulation_adapter.py -v` clean (19 passed)
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-402` passes
- [ ] User verified
