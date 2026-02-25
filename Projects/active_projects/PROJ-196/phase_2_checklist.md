# Phase 2: Cached Font Migration + Remove Private Caches

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-196 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate all `__init__`-cached fonts to `get_font()`, remove private font caches from research_renderer and strategy_renderer, move `FONT_MAIN` from colors.py to fonts.py.

---

## Tasks

### Task 2.1: Remove FONT_MAIN from colors.py [Simple]
**File:** `game/ui/colors.py`
**Tests:** `pytest tests/unit/ui/test_colors.py -v`

- [ ] Remove line 11: `FONT_MAIN = "Arial"`
- [ ] Update docstring if it references FONT_MAIN
- [ ] Verify `from game.ui.colors import COLORS` still works

**Notes:**

---

### Task 2.2: Migrate test_lab files from FONT_MAIN to get_font [Medium]
**Files:** 8 test_lab files
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -v`

For each file: change `from game.ui.colors import FONT_MAIN` to `from game.ui.fonts import get_font`, replace `pygame.font.SysFont(FONT_MAIN, N)` with `get_font(N)`:

- [ ] `game/ui/screens/test_lab/renderer.py` (line 13 import; lines 42-45: 4 fonts)
- [ ] `game/ui/screens/test_lab/dialogs.py` (line 11 import; lines 41-42, 150-152: 5 fonts; line 42 `'Courier New'` → `get_font(14, "Courier New")`)
- [ ] `game/ui/screens/test_lab/json_viewer.py` (line 9 import; lines 44-45: 2 fonts)
- [ ] `game/ui/screens/test_lab/component_dropdown.py` (line 8 import; line 35: 1 font)
- [ ] `game/ui/screens/test_lab/results_panel.py` (line 8 import; lines 38-40: 3 fonts)
- [ ] `game/ui/screens/test_lab/ship_panels.py` (line 8 import; lines 74-75: 2 fonts)
- [ ] `game/ui/screens/test_lab/test_run_card.py` (line 8 import; lines 50-52: 3 fonts)
- [ ] `game/ui/screens/test_lab/test_run_details.py` (line 8 import; lines 33-36: 4 fonts)

**Notes:** Keep `TEST_PASS, TEST_FAIL` imports from `game.ui.colors` where used.

---

### Task 2.3: Migrate battle_state_viewer.py [Simple]
**File:** `game/ui/screens/battle_state_viewer.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Remove local `FONT_MAIN = 'Consolas'` (line 22)
- [ ] Add `from game.ui.fonts import get_font, FONT_MONO`
- [ ] Line 80: `pygame.font.SysFont(FONT_MAIN, 24)` → `get_font(24, FONT_MONO)`
- [ ] Line 81: `pygame.font.SysFont(FONT_MAIN, 16)` → `get_font(16, FONT_MONO)`
- [ ] Line 82: `pygame.font.SysFont(FONT_MAIN, 14)` → `get_font(14, FONT_MONO)`

**Notes:**

---

### Task 2.4: Migrate scrollable_json_panel.py [Simple]
**File:** `game/ui/widgets/scrollable_json_panel.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Remove local `FONT_MAIN = 'Consolas'` and `FONT_MONO = 'Consolas'` (lines 19-21)
- [ ] Add `from game.ui.fonts import get_font, FONT_MONO`
- [ ] Line 67: `pygame.font.SysFont(FONT_MAIN, 18)` → `get_font(18, FONT_MONO)`
- [ ] Line 68: `pygame.font.SysFont(FONT_MONO, 13)` → `get_font(13, FONT_MONO)`

**Notes:**

---

### Task 2.5: Migrate modifier_impact_grid.py [Simple]
**File:** `game/ui/panels/modifier_impact_grid.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 83: `pygame.font.SysFont("Arial", 15)` → `get_font(15)`
- [ ] Line 84: `pygame.font.SysFont("Arial", 14)` → `get_font(14)`
- [ ] Line 85: `pygame.font.SysFont("Arial", 15, bold=True)` → `get_font(15, bold=True)`

**Notes:**

---

### Task 2.6: Migrate app.py [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 76: `pygame.font.SysFont("arial", 12)` → `get_font(12)`
- [ ] Line 77: `pygame.font.SysFont("arial", 20)` → `get_font(20)`
- [ ] Line 78: `pygame.font.SysFont("arial", 32)` → `get_font(32)`

**Notes:**

---

### Task 2.7: Migrate weapons_renderer.py [Simple]
**File:** `game/ui/screens/builder/weapons_renderer.py`
**Tests:** `pytest tests/unit/builder/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Remove class constant `FONT_NAME = "Arial"` (line 92) — redundant with `FONT_MAIN`
- [ ] Line 106: `pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE_NORMAL)` → `get_font(self.FONT_SIZE_NORMAL)`
- [ ] Line 107: `pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE_SMALL)` → `get_font(self.FONT_SIZE_SMALL)`
- [ ] Line 108: `pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE_NORMAL)` → `get_font(self.FONT_SIZE_NORMAL)`

**Notes:**

---

### Task 2.8: Migrate battle_screen.py lazy font [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Lines 591-594: Replace lazy `_hud_font` init with direct `font = get_font(20)` call (cache makes guard unnecessary)
- [ ] Remove `self._hud_font = None` init if present in `__init__`

**Notes:** The lazy-init was already safe (creates once), but `get_font` makes it simpler.

---

### Task 2.9: Replace research_renderer private cache [Medium]
**File:** `game/ui/research/research_renderer.py`
**Tests:** `pytest tests/unit/research/test_research_renderer.py -v`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Lines 75-85: Replace `_get_font` body:
  ```python
  def _get_font(self, size: int) -> pygame.font.Font:
      quantized_size = max(8, (size // 2) * 2)
      return get_font(quantized_size)
  ```
- [ ] Remove `self._font_cache = {}` from `__init__` (line 73)
- [ ] Update tests that reference `_font_cache` attribute

**Notes:** Quantization wrapper stays — unbounded zoom could create too many cache entries. Central cache handles actual caching.

---

### Task 2.10: Replace strategy_renderer private cache [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -v`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Lines 58-63: Replace `_get_font` body:
  ```python
  def _get_font(self, size, bold=False):
      return get_font(size, bold=bold)
  ```
- [ ] Remove `self._font_cache = {}` from `__init__` (line 45)
- [ ] Update tests: remove `test_init_creates_font_cache`, keep functional cache tests

**Notes:**

---

### Task 2.11: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 12,718 tests pass
- [ ] Verify: no `FONT_MAIN` in `game/ui/colors.py`
- [ ] Verify: no `from game.ui.colors import.*FONT_MAIN` remaining in `game/`
- [ ] Verify: no local `FONT_MAIN` definitions remain except in `game/ui/fonts.py`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
