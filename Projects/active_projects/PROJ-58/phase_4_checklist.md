# Phase 4: Formation Delegation Removal [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all callers of formation delegation properties (10 prod + 6 adapter + 155 test), then remove 5 properties from Ship.

---

## Property Mapping
| Backward Compat Property | Direct Replacement |
|--------------------------|-------------------|
| `ship.formation_master` | `ship.formation.master` |
| `ship.formation_offset` | `ship.formation.offset` |
| `ship.formation_rotation_mode` | `ship.formation.rotation_mode` |
| `ship.formation_members` | `ship.formation.members` |
| `ship.in_formation` | `ship.formation.active` |

## Tasks

### Task 4.1: Update ShipControllableAdapter [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/ -x`
- [ ] Line 423: `self._ship.formation_members` → `self._ship.formation.members`
- [ ] Line 427: `self._ship.formation_master` → `self._ship.formation.master`
- [ ] Line 431: `self._ship.in_formation` → `self._ship.formation.active`
- [ ] Line 435: `self._ship.formation_offset` → `self._ship.formation.offset`
- [ ] Line 439: `self._ship.in_formation = value` → `self._ship.formation.active = value`
- [ ] Line 443: `self._ship.formation_master = master` → `self._ship.formation.master = master`
- [ ] Run tests: `pytest tests/unit/ai/ -x`

### Task 4.2: Update Production Callers [Simple]
**Files:** `game/ai/controller.py`, `game/ui/services/ship_factory.py`
**Tests:** `pytest tests/unit/ai/ tests/unit/ui/services/ -x`

**controller.py:**
- [ ] Line 369: `member.formation_offset` → `member.formation.offset`
- [ ] Line 370: `member.formation_offset.length()` → `member.formation.offset.length()`
- [ ] Line 387: `member.in_formation` → `member.formation.active`
- [ ] Line 389: `member.formation_offset.rotate(...)` → `member.formation.offset.rotate(...)`
- [ ] Line 419: `own_ship.formation_master.formation_members.remove(own_ship)` → `own_ship.formation.master.formation.members.remove(own_ship)`

**ship_factory.py:**
- [ ] Line 169: `ship.formation_master = master` → `ship.formation.master = master`
- [ ] Line 170: `master.formation_members.append(ship)` → `master.formation.members.append(ship)`
- [ ] Line 174: `ship.formation_rotation_mode = rotation_mode` → `ship.formation.rotation_mode = rotation_mode`
- [ ] Line 177: `ship.formation_offset = diff` → `ship.formation.offset = diff`
- [ ] Line 180: `ship.formation_offset = diff.rotate(...)` → `ship.formation.offset = diff.rotate(...)`
- [ ] Run tests: `pytest tests/unit/ai/ tests/unit/ui/services/ -x`

### Task 4.3: Update Test Callers [Medium]
**Files:** 20+ test files (155+ occurrences)
**Tests:** `pytest tests/ --testmon`

Apply the property mapping table above to all test files. Key files with heaviest usage:

**Integration tests:**
- [ ] `tests/integration/test_formation_flight.py` (~8 occurrences)
- [ ] `tests/integration/test_formation_attack.py` (~7 occurrences)
- [ ] `tests/integration/ai_strategy/test_response.py` (~6 occurrences)
- [ ] `tests/integration/ai_strategy/test_evaluation.py` (~1 occurrence)

**AI unit tests:**
- [ ] `tests/unit/ai/test_ai_controller_interface.py` (~16 occurrences)
- [ ] `tests/unit/ai/test_advanced_behaviors.py` (~5 occurrences)
- [ ] `tests/unit/ai/test_ai_behaviors.py` (~8 occurrences)
- [ ] `tests/unit/ai/formation_prediction/test_formation_behavior.py` (~30 occurrences)
- [ ] `tests/unit/ai/formation_prediction/conftest.py` (~6 occurrences)
- [ ] `tests/unit/ai/controllable_interface/test_adapter_methods.py` (~3 occurrences)
- [ ] `tests/unit/ai/controllable_interface/test_adapter_basics.py` (~3 occurrences)
- [ ] `tests/unit/ai/controllable_interface/conftest.py` (~4 occurrences)

**Other unit tests:**
- [ ] `tests/unit/builder/test_fleet_composition.py` (~4 occurrences)
- [ ] `tests/unit/ui/services/test_ship_factory.py` (~5 occurrences)

**Entity tests (backward compat tests to REWRITE/REMOVE):**
- [ ] `tests/unit/entities/test_ship_formation.py` (~lines 152-208) - These tests explicitly test the backward compat delegation. Update to test `ship.formation.*` directly instead.

- [ ] Run tests: `pytest tests/ --testmon`
**Notes:** This is the highest-volume task. Use search-and-replace carefully. The `in_formation` → `formation.active` mapping is the trickiest since it changes semantics.

### Task 4.4: Remove Formation Delegation Properties from Ship [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ -x`
- [ ] Remove `formation_master` property and setter (~lines 219-226)
- [ ] Remove `formation_offset` property and setter (~lines 228-235)
- [ ] Remove `formation_rotation_mode` property and setter (~lines 237-244)
- [ ] Remove `formation_members` property and setter (~lines 246-253)
- [ ] Remove `in_formation` property and setter (~lines 255-262)
- [ ] Remove section comment (~line 216)
- [ ] Run full test suite: `pytest tests/ -x`
**Notes:** Only do this AFTER Tasks 4.1-4.3 are complete.

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
