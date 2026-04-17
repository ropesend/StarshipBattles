# Phase 2: Delete Dead Strategy `ShipStatsCalculator` Module

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 2`

**Status:** Complete
**Objective:** Eradicate the dead `game/strategy/services/ship_stats_calculator.py` module. The Phase 1 audit confirmed zero production importers; four parallel subagents independently verified. Clean-Sheet Rule + System Migration Policy mandate deletion, not migration.

**Scope change from original plan:** The original Phase 2 was "migrate 20 sites". The audit revealed those 20 sites live in dead code. Migration would be churn; deletion is correct. See `findings/component_damage_callsite_audit.md` ("Dead Module Finding") and `.agent_reports/proj276-dead-module-verification/SYNTHESIS.md` for the full rationale.

The production stat-calc hot path is `game/simulation/entities/ship_design_stats.py::calculate_design_stats` (4 `component_damage` sites). That migration is now **Phase 2b** below — a small follow-up.

---

## Tasks

### Task 2.1: Verify no production importers [Simple]
**File:** N/A — grep-only verification
**Tests:** N/A

- [x] `grep "from game.strategy.services.ship_stats_calculator" game/` — returns zero hits
- [x] `grep "ship_stats_calculator" game/` — returns zero hits outside the file itself
- [x] Confirmed by Agent A (see `SYNTHESIS.md`)
- [x] Confirmed ApplicationContext and core/registry.py do NOT register it
- [x] Confirmed `game/strategy/services/__init__.py` does NOT re-export it

**Notes:** Four subagents ran the exhaustive check. A and D verified safe to delete; B and C flagged concerns that turned out to be about dead-code tests, not live production behavior.

### Task 2.2: Delete the dead module [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** Full suite after deletion

- [x] `rm game/strategy/services/ship_stats_calculator.py` (751 LOC removed)

**Notes:** No `__init__.py` re-export to clean up. No DI registration. No dynamic import. Clean removal.

### Task 2.3: Delete dedicated test directory [Simple]
**File:** `tests/unit/strategy/ship_stats/`
**Tests:** N/A

- [x] `rm -r tests/unit/strategy/ship_stats/` (6 files: `__init__.py`, `conftest.py`, `test_basics.py`, `test_edge_cases.py`, `test_modifiers.py`, `test_resources.py`, `test_toggles.py`, `test_warp.py`)

**Notes:** These tests exercised the dead module's behaviors. None encoded production invariants that production actually implements.

### Task 2.4: Delete or migrate orphan test files [Medium]
**Files:** Multiple
**Tests:** Affected files after change

- [x] `tests/unit/strategy/services/test_ship_stats_pod_storage.py` — DELETED (pod_storage coverage exists in `tests/unit/simulation/systems/test_ship_stats_strategy_attributes.py`)
- [x] `tests/unit/strategy/services/test_ship_stats_cargo_storage.py` — MIGRATED to `calculate_design_stats`
- [x] `tests/integration/resource_system/test_custom_resource_lifecycle.py::test_custom_resource_storage_in_stats` — MIGRATED (now builds real `Component` object)
- [x] `tests/integration/strategy/turn_engine/test_components.py::test_disabled_component_not_consumed_per_turn` — MIGRATED; uses real `standard_engine` with `strategic_per_hex` trigger. Renamed to `test_disabled_component_not_counted_in_stats`.
- [x] `tests/unit/core/test_service_injection.py::TestShipStatsCalculatorInjection` — DELETED class (4 tests); DI behavior on a class that no longer exists is untestable.
- [x] `tests/unit/strategy/conftest.py::mock_component_registry` fixture — DELETED orphan fixture that patched the deleted module. All callers defined their own local fixture with the same name.

**Notes:** Migrations preserve real production-coverage where possible; the DI-injection tests were deleted because they tested the constructor of a class that no longer exists.

### Task 2.5: Update documentation [Simple]
**Files:** `docs/04_SERVICES.md`, `game/ui/panels/build_queue_controller.py`
**Tests:** N/A

- [x] `docs/04_SERVICES.md:542` — updated "deprecated" note to reflect actual deletion under PROJ-276
- [x] `game/ui/panels/build_queue_controller.py:247` — fixed outdated docstring that referenced `ShipStatsCalculator.recalculate_stats()` (not a real method name)
- [x] Verified `docs/02_PATTERNS.md:256` reference is to the simulation-layer `ShipStatsCalculator` (legitimate; not updated)
- [x] Verified `docs/systems/combat_simulation.md` references are all to the simulation-layer `ShipStatsCalculator`

**Notes:** `ShipStatsCalculator` is still a valid class name — the simulation-layer one at `game/simulation/entities/ship_stats.py:81` remains. Only the strategy-layer duplicate was deleted.

### Task 2.6: Verify test suite still passes [Medium]
**Files:** N/A
**Tests:** `pytest tests/ --testmon`

- [x] 14,621 passed (above CLAUDE.md baseline of 14,420)
- [x] 2 pre-existing failures + 3 pre-existing import errors are unrelated to PROJ-276 (verified — no failing file references the deleted module)
- [x] All four directly-affected test files pass individually

**Notes:** Pre-existing issues: theme_id (Federation vs Klingons), colony owner_id mismatch, 3 ImportErrors in unrelated modules (`IFormationMaster`, `FormationBehavior`, `create_auto_load_population_order`).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-276 2`
