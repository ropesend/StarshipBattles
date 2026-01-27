# Phase 3: Property Naming Standardization

**Objective:** Rename ALL_CAPS instance properties to lowercase
**Status:** Not Started
**Complexity:** Medium

## Tasks

### Task 3.1: Rename HEX_SIZE and DETAIL_ZOOM_LEVEL in StrategyScene [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/ui/ -v`

- [ ] Line 67: Rename `self.HEX_SIZE = 10` to `self.hex_size = 10`
- [ ] Line 68: Rename `self.DETAIL_ZOOM_LEVEL = 3.0` to `self.detail_zoom_level = 3.0`
- [ ] Search for all usages of `HEX_SIZE` and `DETAIL_ZOOM_LEVEL` in this file and update
- [ ] Use find-and-replace: `self.HEX_SIZE` → `self.hex_size`, `self.DETAIL_ZOOM_LEVEL` → `self.detail_zoom_level`

**Notes:**

---

### Task 3.2: Update strategy_renderer.py property [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/ui/ -v`

- [ ] Lines 46-47: Rename `@property def HEX_SIZE(self):` to `@property def hex_size(self):`
- [ ] Update return statement: `return self.scene.HEX_SIZE` → `return self.scene.hex_size`
- [ ] Update all internal usages (search for `self.HEX_SIZE` in file)

**Notes:**

---

### Task 3.3: Update strategy_camera_nav.py property [Simple]
**File:** `game/ui/screens/strategy_camera_nav.py`
**Tests:** `pytest tests/ui/ -v`

- [ ] Lines 67-68: Rename property `def HEX_SIZE` → `def hex_size`
- [ ] Update return: `return self.scene.HEX_SIZE` → `return self.scene.hex_size`
- [ ] Update usages at lines 79, 84

**Notes:**

---

### Task 3.4: Update strategy_colonization.py property [Simple]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/ui/ -v`

- [ ] Lines 51-52: Rename property and update reference
- [ ] Update usage at line 68

**Notes:**

---

### Task 3.5: Update strategy_fleet_ops.py property [Simple]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Tests:** `pytest tests/ui/ -v`

- [ ] Lines 34-35: Rename property `def HEX_SIZE` → `def hex_size`
- [ ] Update return: `return self.scene.HEX_SIZE` → `return self.scene.hex_size`
- [ ] Update usages at lines 62, 68

**Notes:**

---

### Task 3.6: Update strategy_input_handler.py usages [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/ui/ -v`

- [ ] Line 49: Update `hex_size = self.scene.HEX_SIZE` → `hex_size = self.scene.hex_size`
- [ ] Line 50: Update `pixel_to_hex(..., self.scene.HEX_SIZE)` → `pixel_to_hex(..., self.scene.hex_size)`
- [ ] Line 64: Update any other HEX_SIZE references

**Notes:**

---

## Phase 3 Verification
- [ ] No `HEX_SIZE` or `DETAIL_ZOOM_LEVEL` in ALL_CAPS remain (except constants in scripts/)
- [ ] `grep -r "self.HEX_SIZE" game/` returns no matches
- [ ] `grep -r "self.DETAIL_ZOOM_LEVEL" game/` returns no matches
- [ ] `pytest tests/ui/ -v` passes
- [ ] Application launches without errors: `python -m game.app`
