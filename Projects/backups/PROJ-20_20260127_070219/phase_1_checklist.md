# Phase 1: Production Queue Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-20 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove legacy `["name", turns]` list format support, standardize on dict format `{"design_id": ..., "type": ..., "turns_remaining": N}`

**Risk:** Low - production code already creates dict format

---

## Tasks

### Task 1.1: Update production_engine.py [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/test_production_engine.py -v`

**Current State (Lines 57-79):**
```python
if isinstance(item, list):
    vehicle_type = "ship"
    design_id = item[0]
else:
    vehicle_type = item.get("type", "ship")
    design_id = item["design_id"]
```

- [x] Remove `isinstance(item, list)` check on line 58
- [x] Remove list format handling (lines 59-61, 74-76)
- [x] Keep only dict format handling
- [x] Add type hint `item: Dict[str, Any]`
- [x] Update method docstring to reflect dict-only format
- [x] Verify: `grep -n "isinstance.*list" game/strategy/engine/production_engine.py` returns nothing

**Notes:** Updated module docstring, class docstring, and process_production method. Removed all isinstance(item, list) checks. Added Dict[str, Any] type hint to item variable.

---

### Task 1.2: Update planet.py add_production() [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/strategy/test_production.py -v`

**Current State (Lines 132-149):**
- Accepts both list and dict formats
- Converts list to dict internally

- [x] Simplify `add_production()` to accept dict format only
- [x] Update method signature: `def add_production(self, design_id: str, turns: int, vehicle_type: str = "ship"):`
- [x] Remove list-to-dict conversion logic
- [x] Update docstring to describe dict format
- [x] Verify: Method only appends item directly to queue

**Notes:** Changed signature to accept individual parameters (design_id, turns, vehicle_type) and internally create the dict. This provides a cleaner API while ensuring consistent dict format.

---

### Task 1.3: Update build_queue_screen.py [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/ui/test_build_queue_screen.py -v`

**Locations to fix:**
| Line(s) | Pattern |
|---------|---------|
| 477 | `isinstance(item, dict)` check |
| 482-485 | Legacy list format extraction |
| 702 | `isinstance(removed_item, dict)` check |
| 760-761 | Format checks in drag handling |
| 770 | Format check for turns |

- [x] Line 477: Remove isinstance check, assume dict
- [x] Lines 482-485: Remove else branch (list format handling)
- [x] Line 696: Remove isinstance check (was on line 702 in original)
- [x] Lines 754-755: Remove format checks (was 760-761 in original)
- [x] Line 764: Remove format check (was line 770 in original)
- [x] Verify: `grep -n "isinstance.*list\|isinstance.*dict" game/ui/screens/build_queue_screen.py` returns nothing for production items

**Notes:** Removed all isinstance checks for production queue items. Remaining isinstance checks (lines 594-595) are for layer_data/design components, not production queue items.

---

### Task 1.4: Remove backward compatibility tests [Simple]
**Files:** Multiple test files
**Tests:** Run full test suite after removal

- [x] `tests/unit/strategy/test_turn_engine.py`: Remove `test_legacy_list_format_supported()` (around line 481)
- [x] `tests/unit/strategy/test_production_engine.py`: Remove legacy list format tests if any exist
- [x] `tests/strategy/test_production.py`: Remove `test_backwards_compat_list_format()` (around line 172)
- [x] Verify: No test failures related to production queue

**Notes:** Removed test_legacy_list_format_supported from test_turn_engine.py, test_backwards_compat_list_format from test_production.py, and legacy tests from test_production_engine.py. Updated test_add_to_queue to use dict format assertions.

---

### Task 1.5: Update remaining test fixtures [Simple]
**Tests:** `pytest tests/unit/strategy/ tests/strategy/ -v`

- [x] Search for list format in test fixtures: `grep -rn '\[".*", [0-9]' tests/`
- [x] Convert any remaining `["name", N]` to `{"design_id": "name", "type": "ship", "turns_remaining": N}`
- [x] Verify: All production tests pass

**Notes:** No additional list format fixtures needed conversion. The add_production() API handles conversion internally.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/test_production_engine.py tests/unit/strategy/test_turn_engine.py tests/strategy/test_production.py -v` passes
- [x] `grep -rn "isinstance.*list" game/strategy/engine/production_engine.py` returns nothing
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
