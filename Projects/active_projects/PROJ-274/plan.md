# PROJ-274: Unified ShipMaterializer Service

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-274` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-274 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Design interface + failing tests | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Implement InstanceBackedMaterializer | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Implement DesignOnlyMaterializer | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Wire into ApplicationContext | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Make `ship_builder` kwarg optional | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Migrate three production call sites | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Docs update | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-04-16
**Active Phase:** Planning (ready to start Phase 1)
**Last Action:** Project created with full plan
**Next Action:** Begin Phase 1 — design `IShipMaterializer` protocol and write failing tests
**Blockers:** None
**Context for Next Agent:** This project unblocks PROJ-275 (N-team combat). Can be executed in parallel with PROJ-273. The `ship_builder` kwarg in `game/simulation/battle_runner.py` is a Phase-1 transitional placeholder (acknowledged in the docstring at L105-110) that every caller has to handle independently. Six forks exist: `game/app.py::_ship_builder`, `combat_lab/services/test_execution_service.py:83,95`, `combat_lab/services/scenario_run_helper.py:67`, `combat_lab/scenarios/templates.py:844` (ComparisonScenario), plus three test-only variants in `tests/integration/simulation/test_three_team_battle.py`, `test_boundary_retreat.py`, `tests/performance/test_telemetry_overhead.py`. This project replaces the production forks with a single context-registered service, keeping the kwarg as a test-override path.

## Overview

Replace the six-way `ship_builder` closure proliferation with a single `IShipMaterializer` service registered on `ApplicationContext`. `run_battle` will pull its materializer from context by default, freeing callers from rolling their own closures. `BattleSpec` becomes self-sufficient: give it to `run_battle`, get an outcome.

## Goals

- One interface (`IShipMaterializer`), two production implementations (`InstanceBackedMaterializer`, `DesignOnlyMaterializer`).
- `run_battle(spec)` requires no `ship_builder` kwarg for normal production calls.
- `BattleSpec` carries enough data for any materializer (adding `instance_ref: Optional[Any]` to `ShipSpec`).
- The three production `ship_builder` closures collapse to single-line calls.
- Test-only closures remain supported via explicit override kwarg (not removed — tests need isolation).

## Scope

**In:**
- New module: `game/simulation/services/ship_materializer.py` — `IShipMaterializer` protocol + two impls.
- Wire into `ApplicationContext` (`game/context.py`) with `get_default_ship_materializer()` / `set_default_ship_materializer()`.
- Add `ShipSpec.instance_ref: Optional[Any]` field (loose typing to avoid layer violation).
- Refactor `run_battle(spec)`: `ship_builder` optional override; default from context.
- Migrate three production call sites.
- Update `materialize_spec_ships` helper.

**Out:**
- Deleting test-only `ship_builder` closures (they remain as explicit overrides).
- Changes to `ShipInstance.to_ship()` signature.
- Changes to ship construction semantics (just redirecting who calls which existing constructor).

## Key Files

| Component | File Path |
|-----------|-----------|
| New interface + impls | `game/simulation/services/ship_materializer.py` |
| ApplicationContext | `game/context.py` |
| ShipSpec DTO | `game/simulation/battle_spec.py` |
| Battle runner | `game/simulation/battle_runner.py` |
| Battle controller | `game/simulation/battle_controller.py` |
| App entry | `game/app.py` |
| Test lab entry | `game/ui/screens/test_lab/screen.py` |
| Combat Lab execution | `combat_lab/services/test_execution_service.py` |
| Combat Lab spec compiler | `combat_lab/spec_compiler.py` |
| Integration test | `tests/integration/test_app_integration.py` |
| Docs | `docs/04_SERVICES.md`, `docs/01_ARCHITECTURE.md`, `docs/systems/combat_simulation.md` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest

## Verification
- [ ] All phase checklists complete
- [ ] `pytest tests/unit/simulation/services/test_ship_materializer.py` passes
- [ ] Integration test at `tests/integration/test_app_integration.py:160-190` migrated and passing
- [ ] Test-override closures still work
- [ ] Full suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Manual: launch strategy battle (InstanceBackedMaterializer active); launch Combat Lab test (DesignOnlyMaterializer active)
- [ ] Audit passed
- [ ] User verified
