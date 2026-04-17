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
| 1. Design interface + failing tests | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Implement InstanceBackedMaterializer | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Implement DesignOnlyMaterializer | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Wire into ApplicationContext | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Make `ship_builder` kwarg optional | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Migrate three production call sites | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Docs update | Complete | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-04-16
**Active Phase:** COMPLETE — awaiting user verification
**Last Action:** Phase 7 complete. All 7 phases delivered.
- **Docs updated:** New "ShipMaterializer (PROJ-274)" section at top of `docs/04_SERVICES.md` covering protocol, 2 implementations, module accessors, `run_battle` integration, `ShipSpec.instance_ref`, and caller table. `docs/01_ARCHITECTURE.md` ApplicationContext description updated. `docs/systems/combat_simulation.md` canonical `run_battle` example trimmed (no more `ship_builder=my_ship_builder`).
- **Memory updated:** `MEMORY.md` In-Progress Projects section now covers both PROJ-273 + PROJ-274.
- **Bonus Phase 6 cleanup:** Eliminated the 30-line `_make_ship_builder` method in `game/strategy/adapters/simulation_adapter.py` that was doing redundant `instance_id → ShipInstance` lookup. With `instance_ref` set by the strategy compiler, the context materializer reads it directly.

**Regression:** Final full-suite run: **14800 passed, 1 failed (quickstart — pre-existing), 2 skipped, 3 errors (ai x2 + strategy/engine x1 — all pre-existing)** in 221.87s. Exactly matches pre-PROJ-274 baseline. Combat Lab 162/162.
**Next Action:** User verification steps:
1. Manual smoke: launch strategy battle (verify InstanceBackedMaterializer used) + launch Combat Lab test (verify DesignOnlyMaterializer used). Both should work with no error messages about missing ship_builder or instance_ref.
2. Audit per `Projects/protocols/04_audit_project.md`, then archive.
**Blockers:** None
**Context for Next Agent:** PROJECT COMPLETE. All acceptance criteria met:
- New module at `game/simulation/combat/services/ship_materializer.py` (typo — actually `game/simulation/services/ship_materializer.py`) with `IShipMaterializer` protocol, `InstanceBackedMaterializer`, `DesignOnlyMaterializer`, `get_default_ship_materializer()` / `set_default_ship_materializer()` accessors.
- `ShipSpec.instance_ref: Optional[Any] = None` added to `game/simulation/battle_spec.py`.
- Strategy + battle_setup compilers pass `instance_ref=ship` when building ShipSpecs.
- `run_battle(spec, *, ai_factory, ship_builder=None, ...)` — ship_builder optional; None → context materializer via `_default_ship_builder_from_context()`.
- `BattleController.start_from_spec(spec, *, ai_factory, ship_builder=None, config=None)` — same.
- 5 production `_ship_builder` closures eliminated (`game/app.py`, `game/strategy/adapters/simulation_adapter.py::_make_ship_builder`, `game/ui/screens/test_lab/screen.py` x2, `combat_lab/services/test_execution_service.py` x2).
- Combat Lab `TestRunner.__init__` installs DesignOnlyMaterializer via new `combat_lab/design_loader.py::load_combat_lab_design`.
- ComparisonScenario + scenario_run_helper keep role-tagging closures but delegate to context builder.
- 4 test-only `ship_builder=` overrides preserved (`test_three_team_battle.py`, `test_boundary_retreat.py`, `test_telemetry_overhead.py`, + 3 strategy/combat tests).
- 24+ new tests added (`test_ship_materializer.py` — 17 tests; `test_battle_runner.py::TestShipBuilderDefaultsFromContext` — 2 tests; plus Phase 1-4 test subsets).
- Unblocks **PROJ-275** (N-Team Combat Support).

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
