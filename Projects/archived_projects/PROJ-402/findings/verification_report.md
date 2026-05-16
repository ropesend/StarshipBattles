# PROJ-402 Verification Report

**Date:** 2026-05-09
**Branch:** `feat/03c-phase-aware-execution`
**Phases:** 1 (single phase)
**Status:** Complete — awaiting user verification.

## Summary

Tier 1 B-03 from the PROJ-380–399 implementation review is fixed.
`SimulationBattleResolver` now catches both `SimulationException` and
`ValidationException` so battle context (`fleet_ids`, `empire_ids`,
`hex_coord`) survives into crash dumps for both failure modes
`run_battle` can raise.

## Production change

`game/strategy/adapters/simulation_adapter.py:288-300`
- Lazy-import block now also imports `ValidationException` from
  `game.core.exceptions`.
- The `except SimulationException` clause is widened to
  `except (SimulationException, ValidationException) as e:`.
- Comment block updated to reference PROJ-402 and the
  `battle_runner.py:640-652` source of `ValidationException`.

No behavioral change for callers that already received
`BattleResolutionError`; the previously-uncaught path now also produces
the wrapped exception with the same `context={"fleet_ids", "empire_ids",
"hex_coord", "original_type"}` shape.

## Test change

`tests/unit/strategy/adapters/test_simulation_adapter.py` —
`TestSimulationAdapterBattleContextPreservation`:
- Replaced the substituted `_BoomSim`-only test with the canonical
  `test_validation_exception_wrapped_with_battle_context` that injects a
  real `ValidationException("invalid component")`.
- Asserts `BattleResolutionError` is raised, `context` carries
  `fleet_ids=[1,2]`, `empire_ids=[7,9]`, `hex_coord=(3,4)`,
  `original_type="ValidationException"`, and `__cause__` is the
  injected `ValidationException`.
- Retained the `SimulationException` regression as
  `test_simulation_exception_wrapped_with_battle_context` so existing
  branch coverage is preserved.
- TDD discipline: confirmed RED before fix (raw `ValidationException`
  propagated); confirmed GREEN after.

## Cross-check

`rg -n "except SimulationException" game/strategy/adapters/` returns
zero matches. `simulation_adapter.py` was the only adapter wrapping
`run_battle`, so no follow-up scope is flagged.

## Validators

- `pytest tests/unit/strategy/adapters/test_simulation_adapter.py -v`:
  19 passed.
- `python Projects/scripts/validate_phase.py PROJ-402 1`: PASSED.
- `python Projects/scripts/validate_audit_ready.py PROJ-402`: PASSED.
