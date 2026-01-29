# Phase 4: Clean Up Serialization & Format Support

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-42 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove dead format support code, standardize serialization
**Complexity:** Medium

---

## Pre-Phase Checklist
- [ ] Phase 3 complete
- [ ] Read [design.md](design.md) - review "Serialization Legacy Formats" section
- [ ] Verify: `pytest tests/` passes

---

## Task 4.1: Remove Ship String Format Parser [Simple]
**Issue:** BCD-010 (partial)
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py`

### Subtasks
- [ ] Locate the string format handling code (lines 168-172):
  ```python
  if isinstance(c_entry, str):
      # Old format: just component ID
      comp_id = c_entry
  ```
- [ ] Replace with explicit dict requirement:
  ```python
  if not isinstance(c_entry, dict):
      raise ValueError(f"Component entry must be dict, got {type(c_entry)}")
  comp_id = c_entry.get("id", "")
  modifiers_data = c_entry.get("modifiers", [])
  ```
- [ ] Verify no saves use string format (search test data if available)
- [ ] Run tests: `pytest tests/unit/entities/test_ship_serialization.py`

**Notes:**

---

## Task 4.2: Standardize Component Serialization to Dict-Only [Simple]
**Issue:** BCD-010
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py`

### Subtasks
- [ ] Review `to_dict()` method - verify it outputs dict format
- [ ] Review `from_dict()` method - verify it only accepts dict format (after Task 4.1)
- [ ] Add format version field to serialization output:
  ```python
  def to_dict(self, ship):
      return {
          "_format_version": "2.0",  # Add this
          "name": ship.name,
          # ... rest of fields
      }
  ```
- [ ] Add version check in `from_dict()`:
  ```python
  version = data.get("_format_version", "1.0")
  if version < "2.0":
      raise ValueError(f"Unsupported ship format version: {version}")
  ```
- [ ] Run tests: `pytest tests/unit/entities/test_ship_serialization.py`

**Notes:**

---

## Task 4.3: Clean Up Formation Editor Dual Format Support [Medium]
**Issue:** LPH-007
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/` (or manual test formation editor)

### Subtasks
- [ ] Locate dual format handling (lines 204-209):
  ```python
  if isinstance(item, list):  # Legacy
      self.arrows.append(item)
  elif isinstance(item, dict):
      self.arrows.append(item.get('pos', [0,0]))
  ```
- [ ] Replace with dict-only loading:
  ```python
  if not isinstance(item, dict):
      raise ValueError(f"Arrow must be dict format, got {type(item)}")
  self.arrows.append(item.get('pos', [0,0]))
  self.arrow_attrs.append({'rotation_mode': item.get('rotation_mode', 'relative')})
  ```
- [ ] Add format version to formation files on save
- [ ] Run tests or manual test formation editor

**Notes:**

---

## Task 4.4: Remove Stats Mismatch Warning Fallback [Simple]
**Issue:** BCD-006
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py`

### Subtasks
- [ ] Locate stats mismatch handling (lines 208-246):
  ```python
  if mismatches:
      log_warning(f"Ship '{s.name}' stats mismatch after loading!")
  ```
- [ ] Decide on approach:
  - Option A: Convert warning to error (strict)
  - Option B: Keep warning but document it's expected during migration
  - Option C: Remove the verification entirely (trust recalculated stats)
- [ ] Implement chosen approach
- [ ] Run tests: `pytest tests/unit/entities/test_ship_serialization.py`

**Notes:**

---

## Task 4.5: Clean Up getattr Defaults for Ship Attributes [Simple]
**Issue:** BCD-009
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py`

### Subtasks
- [ ] Locate getattr with defaults (lines 41-66):
  ```python
  "vehicle_type": getattr(ship, 'vehicle_type', 'Ship'),
  "strategic_movement": getattr(ship, 'total_strategic_movement', 0),
  "warp_max_tonnage": getattr(ship, 'warp_max_tonnage', 0),
  ```
- [ ] Verify these attributes are mandatory on Ship class
- [ ] If mandatory, replace with direct access (no getattr default):
  ```python
  "vehicle_type": ship.vehicle_type,
  "strategic_movement": ship.total_strategic_movement,
  ```
- [ ] If some are optional, document why and keep getattr
- [ ] Run tests: `pytest tests/unit/entities/test_ship_serialization.py`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/` - all tests pass
- [ ] Verify no isinstance checks for legacy formats remain in serialization
- [ ] Verify format version field added to serialization
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
- [ ] Commit: "PROJ-42 Phase 4: Standardize serialization formats"
