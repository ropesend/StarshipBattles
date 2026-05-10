# Phase 4: Formation Delegation Removal [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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
- [x] Line 423: `self._ship.formation_members` → `self._ship.formation.members`
- [x] Line 427: `self._ship.formation_master` → `self._ship.formation.master`
- [x] Line 431: `self._ship.in_formation` → `self._ship.formation.active`
- [x] Line 435: `self._ship.formation_offset` → `self._ship.formation.offset`
- [x] Line 439: `self._ship.in_formation = value` → `self._ship.formation.active = value`
- [x] Line 443: `self._ship.formation_master = master` → `self._ship.formation.master = master`
- [x] Added `get_formation_rotation_mode()` to IControllable interface and adapter
- [x] Run tests: `pytest tests/unit/ai/ -x`

### Task 4.2: Update Production Callers [Simple]
**Files:** `game/ai/controller.py`, `game/ui/services/ship_factory.py`, `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/ tests/unit/ui/services/ -x`

**controller.py:**
- [x] `member.formation_offset` → `member.formation.offset` (2 occurrences)
- [x] `member.in_formation` → `member.formation.active`
- [x] `own_ship.formation_master.formation_members.remove(own_ship)` → `own_ship.formation.master.formation.members.remove(own_ship)`

**ship_factory.py:**
- [x] All 5 formation property accesses migrated

**behaviors.py:** (not in original plan, discovered during implementation)
- [x] 3 `getattr(raw_ship, 'formation_rotation_mode', ...)` → `ship.get_formation_rotation_mode()`
- [x] Removed `raw_ship` unwrapping hack — now uses proper interface method
- [x] Run tests: `pytest tests/unit/ai/ tests/unit/ui/services/ -x`

### Task 4.3: Update Test Callers [Medium]
**Files:** 20+ test files (155+ occurrences)
**Tests:** `pytest tests/ -x`

- [x] All integration test files migrated
- [x] All AI unit test files migrated
- [x] All builder/UI service test files migrated
- [x] Entity formation tests updated to test `ship.formation.*` directly
- [x] Added `get_formation_rotation_mode` mock setup to test fixtures
- [x] Run tests: `pytest tests/ -x` — 6248 passed

### Task 4.4: Remove Formation Delegation Properties from Ship [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ -x`
- [x] Removed all 5 delegation properties and their setters (formation_master, formation_offset, formation_rotation_mode, formation_members, in_formation)
- [x] Removed section comment
- [x] Run full test suite: `pytest tests/ -x` — 6248 passed

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
