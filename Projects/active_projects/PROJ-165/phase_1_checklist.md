# Phase 1: Add Helper Function + Unit Tests

## Task 1.1: Add `create_section_header()` to `game/ui/utils.py`
**File:** `game/ui/utils.py`
**Tests:** `pytest tests/unit/ui/ -v`

- [ ] Add `create_section_header()` function at end of file
- [ ] Use lazy import of `pygame_gui` inside function body
- [ ] Signature: `create_section_header(text, y, width, manager, container, x=10, height=25) -> UILabel`
- [ ] Verify existing tests still pass

**Notes:**

## Task 1.2: Write unit tests for `create_section_header()`
**File:** `tests/unit/ui/test_ui_utils.py` (create or extend existing)
**Tests:** `pytest tests/unit/ui/test_ui_utils.py -v`

- [ ] Check if `test_ui_utils.py` exists; create or extend
- [ ] Add `TestCreateSectionHeader` class with these test cases:
  - [ ] `test_returns_uilabel` — returns a `pygame_gui.elements.UILabel` instance
  - [ ] `test_default_x_position` — rect.x == 10
  - [ ] `test_default_height` — rect.height == 25
  - [ ] `test_custom_x` — passing `x=20` results in rect.x == 20
  - [ ] `test_custom_height` — passing `height=30` results in rect.height == 30
  - [ ] `test_object_id` — object_id includes `"#section_header"`
  - [ ] `test_text_set` — label text matches input string
  - [ ] `test_width_matches` — rect.width matches passed width argument
- [ ] Run tests, verify all pass

**Notes:** Check existing UI test fixtures for pygame display initialization patterns.

## Phase 1 Completion
- [ ] All tests pass: `pytest tests/unit/ui/ -v`
- [ ] `create_section_header` is importable from `game.ui.utils`
- [ ] Function handles default and custom x/height parameters
