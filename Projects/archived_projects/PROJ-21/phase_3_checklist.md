# Phase 3: Property Naming Standardization

**Objective:** Rename ALL_CAPS instance properties to lowercase
**Status:** Complete
**Complexity:** Medium

## Tasks

### Task 3.1: Rename HEX_SIZE and DETAIL_ZOOM_LEVEL in StrategyScene [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/ui/ -v`

- [x] Line 68: Rename `self.HEX_SIZE = 10` to `self.hex_size = 10`
- [x] Line 69: Rename `self.DETAIL_ZOOM_LEVEL = 3.0` to `self.detail_zoom_level = 3.0`

**Notes:** Base properties renamed.

---

### Task 3.2: Update strategy_renderer.py property [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/ui/ -v`

- [x] Rename `@property def HEX_SIZE(self):` to `@property def hex_size(self):`
- [x] Update return statement: `return self.scene.hex_size`
- [x] Update all internal usages (20+ occurrences)

**Notes:** All usages updated via replace_all.

---

### Task 3.3: Update strategy_camera_nav.py property [Simple]
**File:** `game/ui/screens/strategy_camera_nav.py`
**Tests:** `pytest tests/ui/ -v`

- [x] Rename property `def HEX_SIZE` → `def hex_size`
- [x] Update return: `return self.scene.hex_size`
- [x] Update usages at lines 47, 89, 147

**Notes:** All usages updated via replace_all.

---

### Task 3.4: Update strategy_colonization.py property [Simple]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/ui/ -v`

- [x] Rename property and update reference
- [x] Update usage at line 142

**Notes:** All usages updated via replace_all.

---

### Task 3.5: Update strategy_fleet_ops.py property [Simple]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Tests:** `pytest tests/ui/ -v`

- [x] Rename property `def HEX_SIZE` → `def hex_size`
- [x] Update return: `return self.scene.hex_size`
- [x] Update usages at lines 76, 156

**Notes:** All usages updated via replace_all.

---

### Task 3.6: Update strategy_input_handler.py usages [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/ui/ -v`

- [x] Update `self.scene.HEX_SIZE` → `self.scene.hex_size` (3 occurrences)

**Notes:** All usages updated via replace_all.

---

## Phase 3 Verification
- [x] No `HEX_SIZE` or `DETAIL_ZOOM_LEVEL` in ALL_CAPS remain
- [x] `grep -r "self.HEX_SIZE" game/` returns no matches
- [x] `grep -r "self.DETAIL_ZOOM_LEVEL" game/` returns no matches
- [x] `pytest tests/ui/ -v` passes (87 tests)
