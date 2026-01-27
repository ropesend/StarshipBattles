# Phase 1: Production Queue Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-20 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Remove `isinstance(item, list)` check on line 58
- [ ] Remove list format handling (lines 59-61, 74-76)
- [ ] Keep only dict format handling
- [ ] Add type hint `item: Dict[str, Any]`
- [ ] Update method docstring to reflect dict-only format
- [ ] Verify: `grep -n "isinstance.*list" game/strategy/engine/production_engine.py` returns nothing

**Notes:**

---

### Task 1.2: Update planet.py add_production() [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/strategy/test_production.py -v`

**Current State (Lines 132-149):**
- Accepts both list and dict formats
- Converts list to dict internally

- [ ] Simplify `add_production()` to accept dict format only
- [ ] Update method signature: `def add_production(self, item: Dict[str, Any]):`
- [ ] Remove list-to-dict conversion logic
- [ ] Update docstring to describe dict format
- [ ] Verify: Method only appends item directly to queue

**Notes:**

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

- [ ] Line 477: Remove isinstance check, assume dict
- [ ] Lines 482-485: Remove else branch (list format handling)
- [ ] Line 702: Remove isinstance check
- [ ] Lines 760-761: Remove format checks
- [ ] Line 770: Remove format check
- [ ] Verify: `grep -n "isinstance.*list\|isinstance.*dict" game/ui/screens/build_queue_screen.py` returns nothing for production items

**Notes:**

---

### Task 1.4: Remove backward compatibility tests [Simple]
**Files:** Multiple test files
**Tests:** Run full test suite after removal

- [ ] `tests/unit/strategy/test_turn_engine.py`: Remove `test_legacy_list_format_supported()` (around line 481)
- [ ] `tests/unit/strategy/test_production_engine.py`: Remove legacy list format tests if any exist
- [ ] `tests/strategy/test_production.py`: Remove `test_backwards_compat_list_format()` (around line 172)
- [ ] Verify: No test failures related to production queue

**Notes:**

---

### Task 1.5: Update remaining test fixtures [Simple]
**Tests:** `pytest tests/unit/strategy/ tests/strategy/ -v`

- [ ] Search for list format in test fixtures: `grep -rn '\[".*", [0-9]' tests/`
- [ ] Convert any remaining `["name", N]` to `{"design_id": "name", "type": "ship", "turns_remaining": N}`
- [ ] Verify: All production tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/test_production_engine.py tests/unit/strategy/test_turn_engine.py tests/strategy/test_production.py -v` passes
- [ ] `grep -rn "isinstance.*list" game/strategy/engine/production_engine.py` returns nothing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
