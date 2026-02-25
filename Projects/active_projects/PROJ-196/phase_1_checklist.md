# Phase 1: Font Module + Per-Frame Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-196 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create `game/ui/fonts.py` with cached font management, then fix all per-frame font creation bugs across 16 files.

---

## Tasks

### Task 1.1: Create `game/ui/fonts.py` [Simple]
**File:** `game/ui/fonts.py` (new)
**Tests:** `python -c "from game.ui.fonts import get_font, get_default_font, FONT_MAIN, FONT_MONO"`

- [ ] Create module with docstring referencing PROJ-196
- [ ] Define `FONT_MAIN = "Arial"` constant
- [ ] Define `FONT_MONO = "Consolas"` constant
- [ ] Define `_font_cache: dict = {}` module-level cache
- [ ] Implement `get_font(size: int, name: str = FONT_MAIN, bold: bool = False) -> pygame.font.Font` — cache key `(name, size, bold)`, create via `pygame.font.SysFont`
- [ ] Implement `get_default_font(size: int) -> pygame.font.Font` — cache key `(None, size)`, create via `pygame.font.Font(None, size)`
- [ ] Implement `clear_cache() -> None`
- [ ] Verify import succeeds

**Notes:**

---

### Task 1.2: Write unit tests for fonts.py [Simple]
**File:** `tests/unit/ui/test_fonts.py` (new)
**Tests:** `pytest tests/unit/ui/test_fonts.py -v`

- [ ] Test `get_font` returns same object for same args (cache hit)
- [ ] Test `get_font` returns different objects for different sizes
- [ ] Test `get_font` bold vs non-bold returns different objects
- [ ] Test `get_font` with custom name ("Consolas")
- [ ] Test `get_default_font` returns same object for same size
- [ ] Test `get_default_font` returns different objects for different sizes
- [ ] Test `clear_cache` empties cache
- [ ] Test `FONT_MAIN == "Arial"` and `FONT_MONO == "Consolas"`

**Notes:** Need `pygame.font.init()` fixture.

---

### Task 1.3: Fix per-frame fonts in `battle_panels.py` [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/ tests/integration/ --testmon`

- [ ] Add `from game.ui.fonts import get_default_font`
- [ ] Line 103: `pygame.font.Font(None, UIConfig.FONT_TITLE)` → `get_default_font(UIConfig.FONT_TITLE)`
- [ ] Line 104: `pygame.font.Font(None, UIConfig.FONT_NAME)` → `get_default_font(UIConfig.FONT_NAME)`
- [ ] Line 105: `pygame.font.Font(None, UIConfig.FONT_STAT)` → `get_default_font(UIConfig.FONT_STAT)`
- [ ] Line 311: `pygame.font.Font(None, 28)` → `get_default_font(28)`
- [ ] Line 312: `pygame.font.Font(None, 22)` → `get_default_font(22)`
- [ ] Line 313: `pygame.font.Font(None, 18)` → `get_default_font(18)`
- [ ] Line 518: `pygame.font.Font(None, 72)` → `get_default_font(72)`
- [ ] Line 523: `pygame.font.Font(None, 36)` → `get_default_font(36)`
- [ ] Line 541: `pygame.font.Font(None, 24)` → `get_default_font(24)`

**Notes:** Highest-impact perf fix — 3 draw methods creating 9 fonts per frame.

---

### Task 1.4: Fix per-frame fonts in `strategy_widgets.py` [Simple]
**File:** `game/ui/panels/strategy_widgets.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 56: `pygame.font.SysFont("arial", 8)` → `get_font(8)`
- [ ] Line 115: `pygame.font.SysFont("arial", 12)` → `get_font(12)`
- [ ] Line 138: `pygame.font.SysFont("arial", 8)` → `get_font(8)`

**Notes:**

---

### Task 1.5: Fix per-frame fonts in `battle_ui.py` [Simple]
**File:** `game/ui/screens/battle_ui.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 247: `pygame.font.SysFont("Arial", 28, bold=True)` → `get_font(28, bold=True)`
- [ ] Line 253: `pygame.font.SysFont("Arial", 56, bold=True)` → `get_font(56, bold=True)`
- [ ] Line 290: `pygame.font.SysFont("Arial", 48, bold=True)` → `get_font(48, bold=True)`

**Notes:**

---

### Task 1.6: Fix per-frame fonts in `setup_screen.py` [Simple]
**File:** `game/ui/screens/setup_screen.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_default_font`
- [ ] Line 371: `pygame.font.Font(None, 36)` → `get_default_font(36)`
- [ ] Line 372: `pygame.font.Font(None, 28)` → `get_default_font(28)`

**Notes:**

---

### Task 1.7: Fix per-frame font in `setup_renderer.py` [Simple]
**File:** `game/ui/screens/setup_renderer.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_default_font`
- [ ] Line 15: `pygame.font.Font(None, 64)` → `get_default_font(64)`

**Notes:**

---

### Task 1.8: Fix per-frame fonts in `strategy_ui.py` [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 316: `pygame.font.SysFont("arial", 20)` → `get_font(20)`

**Notes:**

---

### Task 1.9: Fix per-frame font in `workshop_screen.py` [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 511: `pygame.font.SysFont("Arial", 18)` → `get_font(18)`

**Notes:**

---

### Task 1.10: Fix per-frame font in `keybindings_scene.py` [Simple]
**File:** `game/ui/screens/keybindings_scene.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 410: `pygame.font.SysFont("arial", 28)` → `get_font(28)`

**Notes:**

---

### Task 1.11: Fix per-frame fonts in `test_lab/screen.py` [Simple]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ --testmon`

- [ ] Add `from game.ui.fonts import get_font, FONT_MONO`
- [ ] Line 380: `pygame.font.SysFont("consolas", 24)` → `get_font(24, FONT_MONO)`
- [ ] Line 381: `pygame.font.SysFont("consolas", 18)` → `get_font(18, FONT_MONO)`
- [ ] Line 382: `pygame.font.SysFont("consolas", 14)` → `get_font(14, FONT_MONO)`

**Notes:**

---

### Task 1.12: Fix per-frame fonts in `schematic_view.py` [Simple]
**File:** `game/ui/screens/builder/schematic_view.py`
**Tests:** `pytest tests/unit/builder/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 99: `pygame.font.SysFont("Arial", 10)` → `get_font(10)`
- [ ] Line 175: `pygame.font.SysFont("Arial", 10)` → `get_font(10)`

**Notes:**

---

### Task 1.13: Fix per-frame font in `detail_panel.py` [Simple]
**File:** `game/ui/screens/builder/detail_panel.py`
**Tests:** `pytest tests/unit/builder/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 262: `pygame.font.SysFont("Arial", 14)` → `get_font(14)`

**Notes:**

---

### Task 1.14: Fix per-frame font in `formation/renderer.py` [Simple]
**File:** `game/ui/screens/formation/renderer.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 260: `pygame.font.SysFont("Arial", 14, bold=True)` → `get_font(14, bold=True)`

**Notes:**

---

### Task 1.15: Fix per-frame fonts in `galaxy_test/system_mode.py` [Simple]
**File:** `game/ui/screens/galaxy_test/system_mode.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 530: `pygame.font.SysFont("arial", 12)` → `get_font(12)`
- [ ] Line 561: `pygame.font.SysFont("arial", 10)` → `get_font(10)`

**Notes:**

---

### Task 1.16: Fix per-frame fonts in `design_report_panel.py` [Simple]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 249: `pygame.font.SysFont("arial", int(18 * font_scale), bold=True)` → `get_font(int(18 * font_scale), bold=True)`
- [ ] Line 250: `pygame.font.SysFont("arial", int(14 * font_scale))` → `get_font(int(14 * font_scale))`

**Notes:** Dynamic font sizes are fine — `get_font` caches any size.

---

### Task 1.17: Fix per-frame font in `planet_report_panel.py` [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 225: `pygame.font.SysFont("arial", 16, bold=True)` → `get_font(16, bold=True)`

**Notes:**

---

### Task 1.18: Fix per-frame font in `design_image_helper.py` [Simple]
**File:** `game/ui/screens/design_image_helper.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.fonts import get_font`
- [ ] Line 98: `pygame.font.SysFont("arial", int(size * 0.5), bold=True)` → `get_font(int(size * 0.5), bold=True)`

**Notes:**

---

### Task 1.19: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 12,718 tests pass
- [ ] No new warnings introduced

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes (12,718+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
