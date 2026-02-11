# Phase 6: Minor Cleanup Batch

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-107 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Batch cleanup of MINOR findings and lower-priority MAJOR items that are documentation-only or low-risk.

**Findings:** CON-FND-006, CON-FND-012 through CON-FND-019, CON-SIM-007 through CON-SIM-016, CON-STR-004 through CON-STR-006, CON-STR-008, CON-STR-009, CON-STR-012 through CON-STR-020, CON-UI1-002 through CON-UI1-009, CON-UI2-006 through CON-UI2-013

---

## Tasks

### Task 6.1: Document StrategyManager Thread Safety Convention [Simple]
**File:** `game/ai/strategy_manager.py`
**Tests:** No code changes

- [ ] Add to class docstring: "Thread Safety: Instance creation is thread-safe. Data loading (load_data/ensure_loaded) must occur before multi-threaded access begins. Once loaded, all reads are safe without synchronization."
- [ ] Verify: Docstring accurately describes actual behavior

**Notes:** CON-FND-006. The code is correct; documentation needs to be explicit about the contract.

---

### Task 6.2: Add Missing Return Type Hints to Strategy Public Methods [Medium]
**File:** `game/strategy/data/galaxy.py`, `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] `galaxy.py` - Add return type hints to all public methods missing them (lines 127-195)
- [ ] `game_session.py` - Add return type hints to public methods (lines 161-194)
- [ ] Verify: `pytest tests/unit/strategy/ -n 12` passes

**Notes:** CON-STR-004. Examine actual return values before adding hints.

---

### Task 6.3: Document Deferred/Out-of-Scope Items [Simple]
**File:** This checklist (documentation only)

The following findings are documented as out-of-scope for PROJ-107 and deferred:

- [ ] Document: **CON-UI1-001** (handle_event vs process_event) - 50 files affected, 33 use handle_event, 17 use process_event. Deferred to dedicated PROJ because renaming ~50 methods across the UI layer is a high-risk change that warrants its own project. Recommendation: standardize on `handle_event`.
- [ ] Document: **CON-SIM-006** (Ability lifecycle methods recalculate vs sync_data) - Complex refactor touching ability base class and all subclasses. Deferred to PROJ-88 (Simulation Core Tier) which already plans ability system improvements.
- [ ] Document: **CON-SIM-009** (Lazy initialization patterns) - Multiple patterns across codebase. Standardizing requires touching ship.py, component.py, ship_stat_querier.py, battle_controller.py. Deferred to God Class Decomposition projects (PROJ-86/87/88/89).
- [ ] Document: **CON-SIM-010** (Ship facade pattern inconsistency) - Already being addressed by PROJ-88 (Simulation Core Tier).
- [ ] Document: **CON-SIM-011** (Inconsistent serialization) - Large scope. Some classes intentionally don't serialize. Deferred.
- [ ] Document: **CON-STR-007** (fleet vs fleet_id parameter naming) - Requires careful API design review. Deferred to PROJ-87 (Strategy Data Tier).
- [ ] Document: **CON-STR-010** (Error handling return values) - ValidationResult vs custom dataclasses. Requires design decision. Deferred.
- [ ] Document: **CON-STR-011** (from_dict signature inconsistency) - Complex, each class has unique deserialization needs. Deferred.
- [ ] Document: **CON-UI2-006** (ShipThemeManager singleton) - Requires DI refactor. Deferred to PROJ-86 (Critical UI Tier).
- [ ] Document: **CON-UI2-008** (Camera API) - Requires DI refactor. Deferred to PROJ-89 (Remaining UI Tier).
- [ ] Document: **CON-UI2-009** (BattleUIService conversion error handling) - Needs error handling design. Deferred.
- [ ] Document: **CON-UI1-004** (Return type inconsistency in click handlers) - 25+ files. Deferred to dedicated PROJ.
- [ ] Document: **CON-UI1-005** (Click handler parameter inconsistency) - Needs protocol definition. Deferred to UI standardization project.

**Notes:** These items are out of scope because they are either: (a) already covered by active God Class Decomposition projects, (b) too large for a consistency cleanup project, or (c) require design decisions beyond this project's scope.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
