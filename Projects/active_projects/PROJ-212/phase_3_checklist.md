# Phase 3: DI & Service-Locator Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-212 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace service-locator anti-patterns with constructor dependency injection; audit remaining deferred registry imports
**Priority:** Medium
**Effort:** Medium

---

## Tasks

### Task 3.1: RS-007 — Replace service-locator in fleet_capability_calculator.py [Medium]
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Finding:** Uses module-level `_get_default_component_registry()` helper that calls `get_default_registry_provider().get_components()`. This is a service-locator anti-pattern — the calculator should receive the registry via constructor injection.
**Tests:** `pytest tests/unit/strategy/data/ -x`

- [x] Read file, understand current service-locator usage
- [x] Add `component_registry` parameter to constructor (with default=None for DI fallback)
- [x] Update all callers to pass the registry if available
- [x] Remove the `_get_default_component_registry()` helper function (RETAINED for backward compat - see Notes)
- [x] Run tests, verify no regressions

**Notes:**
- Added `component_registry: Optional[Dict[str, Any]] = None` to constructor
- Added `_get_registry()` instance method that uses injected registry or falls back to global
- Updated static methods `ship_has_spaceyard()` and `ship_has_ability()` with optional `component_registry` param
- Retained `_get_default_component_registry()` helper for backward compatibility during DI migration (PROJ-211 will complete)
- All 127 FleetCapabilityCalculator, fleet_report_filters, and fleet_data_source tests passing

### Task 3.2: IIA-005 — Audit deferred registry imports [Medium]
**Finding:** `game.core.registry` (specifically `get_default_registry_provider` and `GameRegistries`) is deferred in ~12 files across all layers. Many of these may be unnecessary after the OrderType extraction (Phase 2) reduced transitive import chains.
**Tests:** `pytest tests/ -n 12`

- [x] Grep for all deferred imports of `game.core.registry` across the codebase
- [x] For each occurrence, determine if the deferral is still necessary:
  - Is there an actual circular dependency?
  - Is this a DI fallback pattern (intentional)?
  - Could it safely be promoted to top-level?
- [x] Promote to top-level where safe
- [x] Document any that must remain deferred (with inline comment explaining why)
- [x] Run full test suite, verify no regressions

**Notes:** Audit complete. Findings:
- **TYPE_CHECKING imports** (~20 files): Correct pattern, no changes needed
- **DI fallback patterns** (~8 files): Intentional, documented with "INTENTIONAL LATE IMPORT" comments, scope of PROJ-211
  - `ship_instance.py:257` - DI-S-001 Critical (PROJ-211)
  - `strategy_session_facade.py:493` - DI-S-004 Major (PROJ-211)
  - `empire_economy_calculator.py:60` - DI fallback (PROJ-211)
  - `fleet_capability_calculator.py:25` - Now has constructor DI (Task 3.1)
- **Docstring examples** (`ship_stats.py:47`): INFO level, teaching pattern, not runtime
- **Init functions** (`component.py:500,566`, `ship_loader.py:38`): One-time startup, acceptable

**Conclusion:** No unnecessary deferred imports found. Phase 2's OrderType extraction reduced the main deferred import issues. Remaining deferred imports are intentional DI fallback patterns in scope for PROJ-211.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite passes: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "All phases complete"
