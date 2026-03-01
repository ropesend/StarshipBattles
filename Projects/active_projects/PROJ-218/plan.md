# PROJ-218: Fix Production Queue Cost and Build Time Defaults

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-218` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-218 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix DesignCostCalculator to Use Registry | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Fix Command Handler and All Callers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Cleanup and Validation Hardening | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-28 16:30
**Active Phase:** Planning
**Last Action:** Plan written, awaiting user approval
**Next Action:** User reviews plan, then implementation begins
**Blockers:** None

## Overview
Production queues display "1.0 turns, 0 cost" for all items instead of actual resource costs and build times. The root cause is `DesignCostCalculator.calculate_total_cost()` which looks for inline `resource_cost` on component entries in design JSON, but design files only contain component **references** (e.g., `{"id": "bridge"}`). The actual `resource_cost` data lives in the component registry (`data/components.json`), and costs can include formula-based values and modifier multipliers.

**The fix:** Replace the broken cost calculator to load a Ship object (which resolves components from the registry, evaluates formulas, and applies modifiers), then extract `ship.construction_cost`. This is the same proven approach used by `BuildQueueController._get_design_cost()` and the design report panel.

## Goals
- Queue items display correct per-resource costs derived from actual component definitions and modifiers
- Build time estimates reflect true costs relative to production rates
- All callers of the broken cost calculator are updated
- Legacy `Planet.add_production()` method is removed (per CLAUDE.md eradication policy)

## Scope
**In:**
- Fix `DesignCostCalculator.calculate_total_cost()` to resolve costs from registry via Ship loading
- Fix `AddToConstructionQueueCommandHandler._load_design_cost()` to use corrected calculator
- Fix `DesignMetadata._calculate_resource_cost()` (same bug, plus wrong field name)
- Fix `ProductionEngine._validate_queue_item()` to reject empty `total_cost`
- Update all affected tests
- Delete legacy `Planet.add_production()` method

**Out:**
- Save file migration (per CLAUDE.md: saves are disposable)
- Changes to the build time display calculation in ProductionEngine (dynamic recalculation already works correctly once costs are populated)
- Changes to the design report panel (already works correctly via Ship loading)

## Key Files
| Component | File Path |
|-----------|-----------|
| Cost Calculator | `game/strategy/services/design_cost_calculator.py` |
| Command Handler | `game/strategy/engine/command_handlers.py` (lines 767-841) |
| Production Engine Validation | `game/strategy/engine/production_engine.py` (line 336-344) |
| Design Metadata | `game/strategy/data/design_metadata.py` (lines 216-230) |
| Legacy Method | `game/strategy/data/planet.py` (lines 190-203) |
| Queue Renderer | `game/ui/screens/build_queue_renderer.py` (line 216) |
| Maintenance Engine | `game/strategy/engine/maintenance_engine.py` |
| Empire Economy Calculator | `game/strategy/engine/empire_economy_calculator.py` |
| Design Loader | `game/simulation/services/design_loader.py` |
| Ship Stats Calculator | `game/simulation/entities/ship_stats.py` (lines 104-114) |
| Cost Calculator Tests | `tests/unit/strategy/services/test_design_cost_calculator.py` |
| Command Handler Tests | `tests/unit/strategy/test_command_handlers.py` (lines 1037-1264) |
| Production Repro Tests | `tests/unit/strategy/engine/test_production_repro.py` |
| Triage Findings | `findings/production_queues_cost.md` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Use Ship-loading approach (not simple registry lookup) | Component costs include formula-based values (e.g., `=50 * sqrt(ship_class_mass / 1000)`) and modifier multipliers (`cost_mult`). Only a loaded Ship object accurately calculates these. |
| 2026-02-28 | Replace broken `calculate_total_cost()` entirely | Per CLAUDE.md: "When new system replaces old, ERADICATE the old completely." The old method has never worked for real design files. |
| 2026-02-28 | Delete `Planet.add_production()` | Only called by 2 integration tests. Creates incomplete queue items without cost tracking. Per eradication policy. |
| 2026-02-28 | No save migration | Per CLAUDE.md: "Save files are disposable." Old saves with empty `total_cost` will have items skipped by validation. |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Fix DesignCostCalculator to Use Registry [Medium]
**Objective:** Replace the broken `calculate_total_cost()` with a method that loads a Ship object and extracts `construction_cost`, giving accurate costs including formulas and modifiers.
**Status:** Not Started

#### Task 1.1: Rewrite `DesignCostCalculator.calculate_total_cost()` [Medium]
**File:** `game/strategy/services/design_cost_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/test_design_cost_calculator.py -v`
- [ ] Replace `calculate_total_cost()` signature to accept `registries: GameRegistries` parameter
- [ ] Implementation: use `SimulationDesignLoader(registries=registries).load_ship_from_design_data(design_data, 0, 0)` to create Ship
- [ ] Extract and return `dict(ship.construction_cost)` with zero-values stripped
- [ ] Handle None ship (design load failure) by returning `{}`
- [ ] Add import for `SimulationDesignLoader` and `GameRegistries` (TYPE_CHECKING)
- [ ] Update `calculate_maintenance_cost()` to accept and pass `registries` parameter
**Notes:**

#### Task 1.2: Update DesignCostCalculator Tests [Medium]
**File:** `tests/unit/strategy/services/test_design_cost_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/test_design_cost_calculator.py -v`
- [ ] Update all test methods to pass a `registries` parameter (can use `TestRegistryProvider` or real registries)
- [ ] Add test with component references (not inline `resource_cost`) to verify registry resolution works
- [ ] Add test with modifier-affected costs to verify multipliers are applied
- [ ] Verify maintenance cost tests still pass with updated signature
**Notes:**

#### Task 1.3: Fix `DesignMetadata._calculate_resource_cost()` [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/data/test_design_metadata.py -v`
- [ ] Fix `_calculate_resource_cost()` (line 217-230): this method is used by `from_design_file()` for creating metadata from raw design JSON on disk
- [ ] Since this is called without a Ship object (just raw JSON + registry), it needs registry access to resolve component IDs
- [ ] Option: accept `components_registry` parameter and look up `resource_cost` per component ID from registry. Formulas/modifiers are secondary here (metadata is approximate)
- [ ] Fix field name: currently uses `"cost"` (line 226), should use `"resource_cost"` for consistency
- [ ] Update callers of `_calculate_resource_cost()` to pass registry if available, or leave as-is if metadata accuracy is secondary
**Notes:** `_calculate_resource_cost_from_ship()` (line 232) already works correctly — it uses loaded Ship objects. Focus on the `from_design_file()` path.

---

### Phase 2: Fix Command Handler and All Callers [Medium]
**Objective:** Update all callers of `DesignCostCalculator` to pass registries, ensuring every code path produces correct costs.
**Status:** Not Started

#### Task 2.1: Fix `AddToConstructionQueueCommandHandler._load_design_cost()` [Simple]
**File:** `game/strategy/engine/command_handlers.py` (lines 817-841)
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py::TestAddToConstructionQueueCommandHandler -v`
- [ ] Update `_load_design_cost()` to pass `session.registries` to `DesignCostCalculator.calculate_total_cost()`
- [ ] Verify the handler test `test_queue_item_has_required_fields()` now gets populated costs
- [ ] Add test assertion that `total_cost` is non-empty when design exists
**Notes:**

#### Task 2.2: Fix `ProductionEngine._calculate_design_cost()` [Simple]
**File:** `game/strategy/engine/production_engine.py` (lines 89-107)
**Tests:** `pytest tests/unit/strategy/production_engine/ -v`
- [ ] Update to pass `self._registries` to `DesignCostCalculator.calculate_total_cost()`
- [ ] Verify existing production engine tests pass
**Notes:** This method is only called during tick processing for items that already have `total_cost`. It's a fallback path but should be correct.

#### Task 2.3: Fix Maintenance Engine Callers [Simple]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py -v`
- [ ] Find all calls to `DesignCostCalculator.calculate_total_cost()` or `calculate_maintenance_cost()`
- [ ] Update to pass registries
- [ ] Verify maintenance engine tests pass
**Notes:**

#### Task 2.4: Fix Empire Economy Calculator [Simple]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy.py -v`
- [ ] Find all calls to cost calculator
- [ ] Update to pass registries
- [ ] Verify economy tests pass
**Notes:**

#### Task 2.5: Update Command Handler Tests [Medium]
**File:** `tests/unit/strategy/test_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py::TestAddToConstructionQueueCommandHandler -v`
- [ ] Update test fixtures to provide registries with component definitions that have `resource_cost`
- [ ] Add test: add design to queue → verify `total_cost` matches expected component costs
- [ ] Add test: add design with modifiers → verify cost reflects modifier multipliers
- [ ] Verify all existing handler tests still pass
**Notes:**

#### Task 2.6: Update Production Repro Tests [Simple]
**File:** `tests/unit/strategy/engine/test_production_repro.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_repro.py -v`
- [ ] Update `_make_add_callback()` to pass registries to cost calculator
- [ ] Verify `test_queue_item_has_populated_cost()` passes with the fix
**Notes:** This test was written for PROJ-213 to verify costs are populated — should pass after fix.

---

### Phase 3: Cleanup and Validation Hardening [Simple]
**Objective:** Remove legacy code paths and harden validation to prevent this class of bug.
**Status:** Not Started

#### Task 3.1: Delete `Planet.add_production()` [Simple]
**File:** `game/strategy/data/planet.py` (lines 190-203)
**Tests:** `pytest tests/integration/strategy/production/ -v`
- [ ] Delete the `add_production()` method from Planet class
- [ ] Find callers: `tests/integration/strategy/production/test_queue.py` lines 54, 64
- [ ] Update those tests to use `AddToConstructionQueueCommand` through the command handler instead
- [ ] Verify all integration tests pass
**Notes:**

#### Task 3.2: Harden `ProductionEngine._validate_queue_item()` [Simple]
**File:** `game/strategy/engine/production_engine.py` (lines 336-344)
**Tests:** `pytest tests/unit/strategy/production_engine/ -v`
- [ ] Update validation to also reject empty `total_cost` (currently only checks for missing key):
  ```python
  if 'total_cost' not in item or not item['total_cost']:
      logger.warning(f"Queue item {design_id} has empty/missing 'total_cost' - skipping")
      return "skip"
  ```
- [ ] Add test for empty `total_cost` validation
**Notes:**

#### Task 3.3: Remove Legacy Fallback in `EmpireBuildQueueWindow` [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py` (line 413-415)
**Tests:** `pytest tests/integration/ui/ -v`
- [ ] Evaluate the legacy fallback on line 413-415: `source.construction_queue.append(dict(item))`
- [ ] If all tests have session/facade injection, remove the fallback entirely
- [ ] If some tests depend on it, update those tests to provide session/facade
**Notes:**

#### Task 3.4: Full Test Suite Verification [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite with `-n 12` parallelism
- [ ] All 13,040+ tests must pass
- [ ] No new warnings introduced
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` - all tests pass (13,040 passed, 1 skipped)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Verify queue items show correct costs in UI (manual test)
- [ ] Verify build time estimates are reasonable given production rates

### Final Verification
- [ ] Start new game → add ship to build queue → verify cost matches design report panel
- [ ] Start new game → add complex to build queue → verify cost matches design report panel
- [ ] Process a turn → verify production engine consumes correct resources
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
